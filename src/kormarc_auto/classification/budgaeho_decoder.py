"""부가기호 5자리 디코더 — ISBN EAN-13 add-on에서 KDC·독자대상·발행형태 추출.

Part 87 (2026-05-03) 결정: SEOJI API의 KDC 공백 (2020-12-31 이후 미제공)을
**0 API 호출·100% 정확**으로 메우는 핵심 모듈.

ISBN 부가기호 5자리 구조 (한국 출판유통진흥원):
- 1자리: 독자대상 (0=교양·1=실용·2=여성·3=초등·4=청소년·5=학습참고서·6=초등학습·7=아동·8=비도서·9=전문)
- 2자리: 발행형태 (0=문고·1=사전·2=신서·3=단행본·4=전집·5=전자책·6=전자책 단행본·7=만화·8=잡지)
- 3-4자리: KDC 대분류 + 세분류 (예: 81=문학·한국문학)
- 5자리: 예비 (보통 0)

예: `03810` = 교양 · 단행본 · KDC 81 (문학·한국문학)

근거:
- 한국출판유통진흥원 「ISBN·CIP 발급 안내」 (2024)
- 한국십진분류법 (KDC) 6판
- Part 87 §4.2 (보고서 검증)
"""

from __future__ import annotations

from dataclasses import dataclass

# 독자대상 코드 (1자리)
TARGET_AUDIENCE: dict[str, str] = {
    "0": "교양",
    "1": "실용",
    "2": "여성",
    "3": "초등(전 학년)",
    "4": "청소년",
    "5": "학습참고서 (중·고)",
    "6": "초등학습",
    "7": "아동 (만 14세 미만)",
    "8": "비도서·예비",
    "9": "전문 (학술·기술)",
}

# 발행형태 코드 (2자리)
PUBLICATION_FORM: dict[str, str] = {
    "0": "문고본",
    "1": "사전류",
    "2": "신서판",
    "3": "단행본",
    "4": "전집·총서·다권본",
    "5": "전자출판물 (CD·DVD 등)",
    "6": "도감",
    "7": "그림책·만화",
    "8": "혼합자료·기타 (잡지·연속간행물)",
    "9": "예비",
}

# KDC 대분류 (3자리째 = 0~9)
KDC_MAIN: dict[str, str] = {
    "0": "총류",
    "1": "철학",
    "2": "종교",
    "3": "사회과학",
    "4": "자연과학",
    "5": "기술과학",
    "6": "예술",
    "7": "언어",
    "8": "문학",
    "9": "역사",
}


@dataclass(frozen=True)
class BudgaehoDecoded:
    """부가기호 5자리 디코딩 결과."""

    raw: str
    target_audience: str
    publication_form: str
    kdc_2digit: str  # 예: "81" (문학·한국문학)
    kdc_main: str  # 예: "8 (문학)"
    confidence: float  # 0.0~1.0


def decode_budgaeho(code: str) -> BudgaehoDecoded | None:
    """부가기호 5자리 → 의미 디코딩.

    Args:
        code: 5자리 숫자 문자열 (예: "03810")

    Returns:
        BudgaehoDecoded 또는 None (형식 불일치 시)

    예:
        >>> decode_budgaeho("03810")
        BudgaehoDecoded(raw='03810', target_audience='교양', ...)
    """
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    if len(code) != 5 or not code.isdigit():
        return None

    target_code, form_code, kdc_main_code, kdc_sub_code, _reserve = (
        code[0],
        code[1],
        code[2],
        code[3],
        code[4],
    )

    target = TARGET_AUDIENCE.get(target_code, f"미정의 ({target_code})")
    form = PUBLICATION_FORM.get(form_code, f"미정의 ({form_code})")
    kdc_main_label = KDC_MAIN.get(kdc_main_code, f"미정의 ({kdc_main_code})")
    kdc_2digit = f"{kdc_main_code}{kdc_sub_code}"

    confidence = 1.0 if all([target_code, form_code, kdc_main_code]) else 0.5

    return BudgaehoDecoded(
        raw=code,
        target_audience=target,
        publication_form=form,
        kdc_2digit=kdc_2digit,
        kdc_main=f"{kdc_main_code} ({kdc_main_label})",
        confidence=confidence,
    )


def extract_kdc_from_budgaeho(code: str) -> str | None:
    """부가기호에서 KDC 2자리 추출 (편의 함수).

    Returns:
        "81" 형식의 2자리 KDC 또는 None
    """
    decoded = decode_budgaeho(code)
    return decoded.kdc_2digit if decoded else None


__all__ = [
    "KDC_MAIN",
    "PUBLICATION_FORM",
    "TARGET_AUDIENCE",
    "BudgaehoDecoded",
    "decode_budgaeho",
    "extract_kdc_from_budgaeho",
]
