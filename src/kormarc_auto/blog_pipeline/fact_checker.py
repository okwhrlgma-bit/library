"""갈래 B Cycle 16A (P36) — 발행 전 사실확인 게이트.

외부 보고서 P36 STOP 조건:
- KOLAS III 종료일 = 2026-12-31 외 다른 날짜 출력 시 STOP
- "확장형도 종료" 등 사실 오류 시 STOP

KOLAS III 핵심 사실 = ADR 0026·외부 매출 보고서 §A 정합.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# 핵심 사실 (1글자 변경 = 회귀 게이트 STOP)
KOLAS3_EXPECTED_FACTS = {
    "end_date": "2026-12-31",
    "scope": "표준형",  # 표준형만 종료·확장형 별도
    "successors_count": 4,  # 코라스Ⅲ 확장형·알파스·K-LAS 3.0·KOLAS-WEB
    "public_libraries_2024": 1296,
}


@dataclass(frozen=True)
class FactCheckResult:
    is_passing: bool
    issues: list[str]
    note: str

    def to_dict(self) -> dict:
        return {
            "is_passing": self.is_passing,
            "issues": self.issues,
            "note": self.note,
        }


def check_post_facts(text: str) -> FactCheckResult:
    """본문 사실 검증·STOP 조건 위반 시 issues 반환."""
    issues: list[str] = []

    # 1. KOLAS III 종료일 = 2026-12-31 (다른 날짜 등장 시 STOP)
    # 허용: 2026-12-31 / 2026.12.31 / 2026년 12월 31일 / D-day 카운트
    suspicious_dates = re.findall(
        r"KOLAS\s*(?:III|3|Ⅲ)[^.]*?(\d{4}[년\-./ ]+\d{1,2}[월\-./ ]+\d{1,2}[일]?)",
        text,
        re.IGNORECASE,
    )
    for d in suspicious_dates:
        # normalize
        d_norm = re.sub(r"[년월일.\s/]", "-", d).strip("-")
        d_parts = [p for p in d_norm.split("-") if p]
        if len(d_parts) == 3:
            year, month, day = d_parts
            if not (year == "2026" and month in ("12", "12") and day in ("31", "31")):
                issues.append(f"⚠ KOLAS III 종료일 의심 표기: '{d}'·기대=2026-12-31")

    # 2. "확장형도 종료" 사실 오류 차단
    if re.search(r"확장형\s*(?:도|또한|역시)\s*(?:종료|중단|만료)", text):
        issues.append("⚠ 사실 오류: 확장형도 종료 표기·표준형만 종료가 사실")

    # 3. 후속 시스템 수 (4개) — 5개 이상 명시 시 의심
    if re.search(r"공식\s*후속\s*\d+\s*종", text):
        m = re.search(r"공식\s*후속\s*(\d+)\s*종", text)
        if m and int(m.group(1)) != 4:
            issues.append(f"⚠ 후속 시스템 수 = {m.group(1)} (기대=4)")

    # 4. 공공도서관 수치 = 1,296 (다른 정량 인용 시 출처 필수)
    if re.search(r"공공도서관\s*\d{1,3}(?:,?\d{3})*\s*개", text):
        m = re.search(r"공공도서관\s*(\d{1,3}(?:,?\d{3})*)\s*개", text)
        if m:
            count_str = m.group(1).replace(",", "")
            if count_str.isdigit() and abs(int(count_str) - 1296) > 100:
                issues.append(f"⚠ 공공도서관 수 '{m.group(1)}' = 1,296 (2024 통계) 대비 큰 차이")

    note = (
        "발행 가능 (외부 보고서 P36 게이트 통과)"
        if not issues
        else f"발행 차단·{len(issues)}건 사실확인 필요"
    )
    return FactCheckResult(is_passing=not issues, issues=issues, note=note)
