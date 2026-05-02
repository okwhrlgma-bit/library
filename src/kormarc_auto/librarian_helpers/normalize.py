"""사서 입력 패턴 자동 변환 — 막 쳐도 KORMARC 표준 형식으로 정리.

사서가 평소처럼 빠르게 입력하면 시스템이 자동 정리:
- "2024.5.15" → "20240515" (008 필드 형식)
- "300쪽" → "300 p." (300 ▾a)
- "153x224" → "22 cm" (300 ▾c, 세로 길이)
- "김철수;박영희" → 100 ▾a 김철수 + 700 ▾a 박영희 (주/부 분리)
- "978-89-374-6278-8" → "9788937462788" (ISBN 하이픈 제거)
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


def normalize_date(value: str) -> str | None:
    """다양한 날짜 형식 → YYYYMMDD (008 필드용)."""
    if not value:
        return None
    value = value.strip()
    patterns = [
        ("%Y.%m.%d", r"\d{4}\.\d{1,2}\.\d{1,2}"),
        ("%Y-%m-%d", r"\d{4}-\d{1,2}-\d{1,2}"),
        ("%Y/%m/%d", r"\d{4}/\d{1,2}/\d{1,2}"),
        ("%Y년 %m월 %d일", r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일"),
        ("%Y%m%d", r"\d{8}"),
        ("%Y", r"\d{4}"),
    ]
    for fmt, regex in patterns:
        if re.fullmatch(regex, value):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y%m%d") if fmt != "%Y" else f"{value}0000"
            except ValueError:
                continue
    return None


def normalize_year(value: str) -> str | None:
    """발행연도 → YYYY (4자리)."""
    if not value:
        return None
    m = re.search(r"\d{4}", value)
    return m.group(0) if m else None


def normalize_pages(value: str) -> str | None:
    """페이지 입력 → '300 p.' / '345쪽 p.' 표기 통일."""
    if not value:
        return None
    value = value.strip()
    m = re.search(r"\d+", value)
    if not m:
        return None
    n = m.group(0)
    if "쪽" in value or "p" in value.lower() or "페이지" in value:
        return f"{n} p."
    return f"{n} p."


def normalize_size(value: str) -> str | None:
    """크기 입력 → 'NN cm' (KORMARC는 세로 길이 cm).

    예:
    - "153x224" or "153 x 224" → "22 cm" (세로=224mm=22cm)
    - "22cm" → "22 cm"
    - "22.5" → "23 cm"
    """
    if not value:
        return None
    value = value.strip().lower()

    # WxH 또는 W*H → 세로(=두 번째) 사용
    m = re.search(r"(\d+)[x*×](\d+)", value.replace(" ", ""))
    if m:
        h_mm = int(m.group(2))
        h_cm = round(h_mm / 10) if h_mm > 50 else h_mm  # >50이면 mm로 가정
        return f"{h_cm} cm"

    # 단순 숫자
    m = re.search(r"(\d+(\.\d+)?)", value)
    if m:
        n = float(m.group(1))
        return f"{round(n)} cm"
    return None


def normalize_isbn(value: str) -> str | None:
    """ISBN 입력 → 13자리 하이픈 제거.

    978-89-374-6278-8 → 9788937462788
    """
    if not value:
        return None
    digits = "".join(c for c in value if c.isdigit())
    if len(digits) == 13 and (digits.startswith("978") or digits.startswith("979")):
        return digits
    if len(digits) == 10:  # ISBN-10 → 변환은 별도 로직 필요
        return None
    return None


def split_authors(value: str) -> dict[str, list[str]]:
    """저자 입력 → 주저자 1명 + 부저자 N명 자동 분리.

    "김철수;박영희" → {"primary": "김철수", "additional": ["박영희"]}
    "김철수, 박영희, 이순자" → primary + additional 2명
    "김철수 외" → {"primary": "김철수", "additional": []}
    """
    if not value:
        return {"primary": "", "additional": []}

    # "외" 처리
    s = re.sub(r"\s*외\s*\d*$", "", value.strip())

    # 구분자 통일
    parts = re.split(r"[;,]", s)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return {"primary": "", "additional": []}

    return {
        "primary": parts[0],
        "additional": parts[1:4],  # 부저자 최대 3명
    }


def normalize_price(value: str | int) -> int | None:
    """가격 → 정수 (단위 제거)."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    digits = re.sub(r"[^\d]", "", str(value))
    return int(digits) if digits else None


def normalize_book_data(book_data: dict[str, Any]) -> dict[str, Any]:
    """BookData dict의 모든 필드를 일괄 정규화.

    in-place 수정 안 함 — 새 dict 반환.
    """
    out = dict(book_data)

    if "isbn" in out:
        v = normalize_isbn(out["isbn"])
        if v:
            out["isbn"] = v

    if "publication_year" in out:
        v = normalize_year(out["publication_year"])
        if v:
            out["publication_year"] = v

    if "publication_date" in out:
        v = normalize_date(out["publication_date"])
        if v:
            out["publication_date"] = v

    if "pages" in out:
        v = normalize_pages(out["pages"])
        if v:
            out["pages"] = v

    if "book_size" in out:
        v = normalize_size(out["book_size"])
        if v:
            out["book_size"] = v

    if "price" in out:
        v = normalize_price(out["price"])
        if v is not None:
            out["price"] = v

    if out.get("author"):
        split = split_authors(out["author"])
        if split["primary"]:
            out["primary_author"] = split["primary"]
            out["additional_authors"] = split["additional"]

    return out
