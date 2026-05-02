"""장서 분야별 균형 분석 — Part 82+ 페인 #39 정합.

사서 페인:
- 주제·시기 불균형 → 이용자 불만
- 사서 응용 부담 + 편견 배제

해결: KDC 대분류 10 자동 분포 분석·균형 추천.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

KDC_MAJOR_CLASSES = {
    "000": "총류",
    "100": "철학",
    "200": "종교",
    "300": "사회과학",
    "400": "자연과학",
    "500": "기술과학",
    "600": "예술",
    "700": "언어",
    "800": "문학",
    "900": "역사",
}


@dataclass(frozen=True)
class BalanceReport:
    """장서 균형 보고서."""

    total_books: int
    distribution: dict[str, int]  # KDC 대분류별 권수
    distribution_pct: dict[str, float]  # 퍼센트
    underrepresented: list[str]  # 부족 분야 (5% 미만)
    overrepresented: list[str]  # 과다 분야 (25% 이상)
    recommended_purchases: dict[str, int]  # 권장 구매 권수


def analyze_collection(books: list[dict]) -> BalanceReport:
    """장서 분야별 분포 분석.

    Args:
        books: list[dict(kdc=...)] (자관 장서)

    Returns:
        BalanceReport (균형 분석 + 권장)
    """
    distribution = Counter()
    for book in books:
        kdc = str(book.get("kdc", ""))
        if kdc:
            major = kdc[0] + "00" if kdc[0].isdigit() else "000"
            distribution[major] += 1

    total = len(books)
    pct = {k: round(v / max(total, 1) * 100, 1) for k, v in distribution.items()}

    # 균형 권장: KDC 대분류 = 각 10% (이상)
    target_pct = 10.0
    underrepresented = [k for k in KDC_MAJOR_CLASSES if pct.get(k, 0) < 5.0]
    overrepresented = [k for k in KDC_MAJOR_CLASSES if pct.get(k, 0) >= 25.0]

    # 권장 구매 (균형 회복)
    recommended = {}
    for k in underrepresented:
        current = distribution.get(k, 0)
        target = int(total * target_pct / 100)
        if target > current:
            recommended[k] = target - current

    return BalanceReport(
        total_books=total,
        distribution=dict(distribution),
        distribution_pct=pct,
        underrepresented=underrepresented,
        overrepresented=overrepresented,
        recommended_purchases=recommended,
    )


def generate_balance_summary(report: BalanceReport) -> str:
    """장서 균형 보고서 markdown."""
    lines = [
        "# 자관 장서 분야별 균형 분석",
        "",
        f"> 총 {report.total_books:,}권 분석",
        "",
        "## KDC 대분류 분포",
        "",
        "| 분류 | 명칭 | 권수 | 비율 |",
        "|---|---|---:|---:|",
    ]
    for code, name in KDC_MAJOR_CLASSES.items():
        cnt = report.distribution.get(code, 0)
        p = report.distribution_pct.get(code, 0)
        flag = ""
        if code in report.underrepresented:
            flag = " 🔴 부족"
        elif code in report.overrepresented:
            flag = " ⚠ 과다"
        lines.append(f"| {code} | {name} | {cnt:,} | {p}%{flag} |")

    if report.underrepresented:
        lines.extend(["", "## 부족 분야 권장 구매", ""])
        for code in report.underrepresented:
            cnt = report.recommended_purchases.get(code, 0)
            lines.append(f"- {code} {KDC_MAJOR_CLASSES[code]} = +{cnt}권 권장")

    if report.overrepresented:
        lines.extend(["", "## 과다 분야 (수서 자제 권장)", ""])
        for code in report.overrepresented:
            lines.append(f"- {code} {KDC_MAJOR_CLASSES[code]} = 신간 검토 필요")

    return "\n".join(lines)


__all__ = [
    "KDC_MAJOR_CLASSES",
    "BalanceReport",
    "analyze_collection",
    "generate_balance_summary",
]
