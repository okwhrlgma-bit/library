"""장서 점검 (annual inventory) — 책장 사진 OCR + 자관 DB 대조.

연 1~2회 사서가 며칠 걸리는 전수 점검을 자동화.
PO 자료 「내숲 종합 자료관리대장」의 5종 시트(오배가·보수·대출저조·분실·파손) 처리 흐름 매칭.

흐름:
1. 사서가 책장 사진 촬영 (한 번에 10~30권 책등)
2. 본 모듈이 OCR로 청구기호 추출
3. 자관 DB(library_db)와 대조 → 누락·오배가·미등록 자동 판별
4. 결과 리포트 (CSV·PDF)
"""

from __future__ import annotations

import csv
import io
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# 청구기호 패턴 (예: 813.7 한31ㅈ, 911.05 김12ㅎ c.2 v.3)
_CALL_NUMBER_PATTERN = re.compile(
    r"\d{3}(?:\.\d+)?\s*[가-힣]\d{1,2}[가-힣]?(?:\s*c\.\d+)?(?:\s*v\.\d+)?"
)


def extract_call_numbers_from_image(image_path: str | Path) -> list[str]:
    """책장 사진 → 청구기호 후보 리스트 (OCR).

    Args:
        image_path: 책장(책등) 사진 경로

    Returns:
        인식된 청구기호 리스트 (중복 제거)
    """
    try:
        from kormarc_auto.vision.ocr import extract_text_from_image
    except ImportError:
        logger.warning("OCR 미사용 (easyocr 미설치) — `pip install -e .[ocr]`")
        return []

    lines = extract_text_from_image(image_path)
    if not lines:
        return []

    call_numbers: set[str] = set()
    for line in lines:
        for match in _CALL_NUMBER_PATTERN.finditer(line):
            call_numbers.add(match.group(0).strip())
    return sorted(call_numbers)


def compare_with_inventory(
    detected_call_numbers: list[str],
    *,
    expected_kdc_range: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """OCR 결과를 자관 DB와 대조 → 누락·오배가 판별.

    Args:
        detected_call_numbers: 책장 사진에서 추출된 청구기호 리스트
        expected_kdc_range: (시작, 끝) 예: ('810', '820') — 이 범위 자료가 있어야 할 책장

    Returns:
        {
            "detected_count": int,
            "matched": list[str],     # 자관 DB와 일치
            "missorted": list[str],   # 자관에 있으나 KDC 범위 외 (오배가)
            "missing_in_db": list[str],  # OCR에서 보이나 자관 DB에 없음 (등록 누락)
            "warnings": list[str],
        }
    """
    from kormarc_auto.inventory.library_db import search_local

    matched: list[str] = []
    missorted: list[str] = []
    missing_in_db: list[str] = []
    warnings: list[str] = []

    for cn in detected_call_numbers:
        # 청구기호의 KDC 부분 추출 (예: '813.7 한31ㅈ' → '813.7')
        kdc_match = re.match(r"(\d{3}(?:\.\d+)?)", cn)
        kdc = kdc_match.group(1) if kdc_match else ""

        # 자관 DB에서 청구기호 검색
        results = search_local(query=cn, limit=5)
        if not results:
            # 청구기호의 KDC만으로 다시 검색
            if kdc:
                kdc_results = search_local(kdc_prefix=kdc[:3], limit=5)
                if kdc_results:
                    warnings.append(f"{cn}: 자관에 청구기호 정확 일치 없음 (KDC만 일치)")
                    matched.append(cn)
                    continue
            missing_in_db.append(cn)
            continue

        # KDC 범위 체크 (오배가 판별)
        if expected_kdc_range and kdc:
            start, end = expected_kdc_range
            if not (start <= kdc <= end):
                missorted.append(cn)
                continue

        matched.append(cn)

    return {
        "detected_count": len(detected_call_numbers),
        "matched": matched,
        "missorted": missorted,
        "missing_in_db": missing_in_db,
        "warnings": warnings,
        "summary": {
            "matched_pct": (len(matched) / max(len(detected_call_numbers), 1)) * 100,
            "missorted_pct": (len(missorted) / max(len(detected_call_numbers), 1)) * 100,
            "missing_pct": (len(missing_in_db) / max(len(detected_call_numbers), 1)) * 100,
        },
    }


def normalize_call_number(cn: str) -> str:
    """청구기호 정규화 — OCR 오인식 보정용 핵심 키 생성.

    공백·하이픈 제거 + 자주 헷갈리는 글자 통일:
    - 'O'/'o' → '0', 'l'/'I' → '1' (KDC 숫자 영역에서만)
    - 끝의 권차/복본 제거 (c.2, v.3)
    """
    if not cn:
        return ""
    s = cn.strip().lower()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"c\.?\d+$", "", s)
    s = re.sub(r"v\.?\d+$", "", s)
    # KDC 숫자 영역의 OCR 오인식 보정 (앞쪽만)
    head = s[:6]
    head = head.replace("o", "0").replace("l", "1").replace("i", "1")
    return head + s[6:]


def write_inspection_csv(
    inspection_result: dict[str, Any],
    *,
    output_path: str | Path,
) -> Path:
    """점검 결과 → CSV (사서 공유·KOLAS 정정 작업용)."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "call_number", "note"])
        for cn in inspection_result.get("matched", []):
            writer.writerow(["일치", cn, ""])
        for cn in inspection_result.get("missorted", []):
            writer.writerow(["오배가", cn, "KDC 범위 외"])
        for cn in inspection_result.get("missing_in_db", []):
            writer.writerow(["미등록", cn, "자관 DB에 없음"])
        for w in inspection_result.get("warnings", []):
            writer.writerow(["경고", "", w])
    logger.info("점검 결과 CSV 저장: %s", out)
    return out


def inspection_result_to_csv_bytes(inspection_result: dict[str, Any]) -> bytes:
    """CSV 바이트로 직접 반환 (Streamlit/FastAPI 다운로드용)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["category", "call_number", "note"])
    for cn in inspection_result.get("matched", []):
        writer.writerow(["일치", cn, ""])
    for cn in inspection_result.get("missorted", []):
        writer.writerow(["오배가", cn, "KDC 범위 외"])
    for cn in inspection_result.get("missing_in_db", []):
        writer.writerow(["미등록", cn, "자관 DB에 없음"])
    for w in inspection_result.get("warnings", []):
        writer.writerow(["경고", "", w])
    return buf.getvalue().encode("utf-8-sig")


def inspect_shelf_images(
    image_paths: list[str | Path],
    *,
    expected_kdc_range: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """여러 책장 사진을 한 번에 점검.

    Args:
        image_paths: 책장 사진 1~N장
        expected_kdc_range: 이 책장 영역의 KDC 범위 (예: ('810', '820'))

    Returns:
        compare_with_inventory와 동일 구조 + 이미지별 분석
    """
    all_call_numbers: list[str] = []
    per_image: list[dict[str, Any]] = []

    for path in image_paths:
        cns = extract_call_numbers_from_image(path)
        per_image.append({"image": str(path), "detected": cns, "count": len(cns)})
        all_call_numbers.extend(cns)

    # 중복 제거
    all_call_numbers = sorted(set(all_call_numbers))

    result = compare_with_inventory(all_call_numbers, expected_kdc_range=expected_kdc_range)
    result["per_image"] = per_image
    return result
