"""자관 .mrc 174 전수 검증 — KORMARC 2023.12 + M/A/O + 자관 정책.

실행:
    python scripts/validate_real_mrc.py
    python scripts/validate_real_mrc.py --dir "D:/○○도서관/수서"
    python scripts/validate_real_mrc.py --json reports/real_mrc_2026-04-29.json

영업 가치: 자관 PILOT 인용 자료 ★ — "우리 검증 모듈이 자관 .mrc 174건
전부 ≥99% 정합" 정량 근거. KLA 5.31 발표·사서교육원 강의 즉시 활용.

Read-only: D 드라이브에 어떠한 변경도 가하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.kormarc.application_level import (  # noqa: E402
    validate_application_level,
)
from kormarc_auto.logging_config import setup_logging  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_DIR = Path("D:/○○도서관/수서")
# 자관 등록번호 prefix (실측 D 드라이브 .mrc 174 파일·3,383 레코드 분포):
# EQ 2,553건 (일반)·CQ 773건 (아동)·WQ 57건 (윤동주·시문학 별치)
# EM/CM은 향후 영업 정책 (예약). config.yaml.kolas_register.registration_prefix
# 자관별 변형 정합 (CLAUDE.md §정책 ③).
SELF_LIBRARY_PREFIXES = ("EQ", "CQ", "EM", "CM", "WQ")


def _find_mrc_files(root: Path) -> list[Path]:
    """디렉토리 재귀 검색 → .mrc 파일 목록."""
    if not root.exists():
        logger.error(".mrc 디렉토리 없음: %s", root)
        return []
    return sorted(root.rglob("*.mrc"))


def _parse_mrc_any_encoding(path: Path, reader_cls: Any) -> list[Any]:
    """KOLAS는 EUC-KR/CP949·UTF-8 혼재 — 인코딩 자동 감지 후 파싱.

    leader[9]가 'a'면 UTF-8, ' '이면 MARC-8/EUC-KR. 실제로는 leader가
    잘못된 경우가 많아 둘 다 시도.
    """
    for encoding in ("cp949", "utf-8", "euc-kr"):
        try:
            with path.open("rb") as f:
                records = [r for r in reader_cls(
                    f, force_utf8=False, to_unicode=True, file_encoding=encoding,
                ) if r]
            if records:
                return records
        except (UnicodeDecodeError, ValueError, OSError):
            continue
    return []


def _check_record(record: Any) -> dict[str, Any]:
    """단일 pymarc.Record 검증 → 위반 dict."""
    present_tags = {f.tag for f in record.get_fields()}

    issues: list[str] = []

    # 008 길이 정합 (40자리)
    field_008 = record.get("008")
    if field_008:
        value = field_008.value() if hasattr(field_008, "value") else str(field_008.data)
        if len(value) != 40:
            issues.append(f"008 길이 {len(value)} (40 필요)")

    # 자관 049 prefix 정합
    field_049 = record.get("049")
    register_prefix = None
    if field_049:
        for sf in field_049.subfields:
            if sf.code == "l":
                register_prefix = (sf.value or "").strip()[:2]
                break
        if register_prefix and register_prefix not in SELF_LIBRARY_PREFIXES:
            issues.append(f"049 prefix 비정합: {register_prefix}")

    # M/A/O validate (book_single 가정 — 자관은 단행본 위주)
    book_data: dict[str, Any] = {}
    title_field = record.get("245")
    if title_field:
        for sf in title_field.subfields:
            if sf.code == "a":
                book_data["title"] = sf.value
    series_field = record.get("440") or record.get("490")
    if series_field:
        for sf in series_field.subfields:
            if sf.code == "a":
                book_data["series_title"] = sf.value
    ao_issues = validate_application_level(present_tags, book_data, "book_single")

    return {
        "issues": issues,
        "ao_issues": [{"tag": t, "level": lvl, "reason": r} for t, lvl, r in ao_issues],
        "present_tags": sorted(present_tags),
        "register_prefix": register_prefix,
    }


def main(directory: Path, json_path: Path | None) -> int:
    setup_logging()

    try:
        from pymarc import MARCReader
    except ImportError:
        logger.error("pymarc 미설치 — `pip install pymarc`")
        return 1

    files = _find_mrc_files(directory)
    if not files:
        return 1
    print(f".mrc 파일 발견: {len(files)}건")

    total_records = 0
    fail_records = 0
    issue_counter: Counter[str] = Counter()
    file_summary: list[dict[str, Any]] = []

    for path in files:
        records_in_file = 0
        fails_in_file = 0
        records = _parse_mrc_any_encoding(path, MARCReader)
        if not records:
            issue_counter["파싱 실패"] += 1
            continue
        for record in records:
            records_in_file += 1
            total_records += 1
            result = _check_record(record)
            if result["issues"] or result["ao_issues"]:
                fails_in_file += 1
                fail_records += 1
                for issue in result["issues"]:
                    issue_counter[issue.split(":")[0]] += 1
                for ao in result["ao_issues"]:
                    issue_counter[f"A 누락 {ao['tag']}"] += 1

        file_summary.append({
            "file": str(path.relative_to(directory)),
            "records": records_in_file,
            "fails": fails_in_file,
        })

    pass_records = total_records - fail_records
    pass_rate = (pass_records / total_records * 100) if total_records else 0.0

    print("\n=== 자관 .mrc 검증 결과 ===")
    print(f"파일: {len(files)}건")
    print(f"레코드 합계: {total_records}건")
    print(f"정합: {pass_records}건 ({pass_rate:.2f}%)")
    print(f"위반: {fail_records}건")
    print("\n위반 유형 Top 10:")
    for issue, count in issue_counter.most_common(10):
        print(f"  - {issue}: {count}건")

    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "files_count": len(files),
                    "records_total": total_records,
                    "records_pass": pass_records,
                    "records_fail": fail_records,
                    "pass_rate_pct": round(pass_rate, 2),
                    "issue_counter": dict(issue_counter),
                    "files": file_summary,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nJSON 보고서: {json_path}")

    return 0 if pass_rate >= 99.0 else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    sys.exit(main(args.dir, args.json))
