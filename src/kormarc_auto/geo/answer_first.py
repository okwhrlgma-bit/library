"""갈래 B Cycle 18B P40 — Answer-First 검증 + 통계 밀도.

게이트:
- 첫 단락 = 40-60단어 + 정의문 ("X는 ___이다.")
- 150-200단어마다 1개 통계/숫자/날짜
- AI Overviews 인용 가능성 ↑ (76.1% = 구글 Top 10 정합)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_DEFINITION_PATTERNS = [
    r"^[가-힣A-Za-z][^.!?\n]{2,40}(은|는|이란|란|이라|라)\s+[^.!?]{5,60}(이다|입니다|을 말한다|를 의미한다)",
    r"^[가-힣A-Za-z][^.!?\n]{2,40}(은|는)\s+[^.!?]{5,80}(생성하|자동화하|제공하|보조하)",
]


def _word_count(text: str) -> int:
    """한국어·영문 통합 단어 수 (공백 + 한국어 음절)."""
    if not text:
        return 0
    # 공백 단위 + 한국어 음절 길이 가중치
    return len([t for t in re.split(r"\s+", text.strip()) if t])


def _first_paragraph(text: str) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paras[0] if paras else ""


@dataclass(frozen=True)
class AnswerFirstReport:
    """첫 단락 검증 결과."""

    word_count: int
    has_definition_pattern: bool
    is_within_40_60: bool
    is_passing: bool
    note: str

    def to_dict(self) -> dict:
        return {
            "word_count": self.word_count,
            "has_definition_pattern": self.has_definition_pattern,
            "is_within_40_60": self.is_within_40_60,
            "is_passing": self.is_passing,
            "note": self.note,
        }


def measure_answer_first(text: str) -> AnswerFirstReport:
    """첫 단락 검증 (40-60단어 + 정의문)."""
    para = _first_paragraph(text)
    wc = _word_count(para)
    is_within = 40 <= wc <= 60
    has_def = any(re.search(p, para, re.MULTILINE) for p in _DEFINITION_PATTERNS)

    if is_within and has_def:
        note = "✓ AI Overviews 인용 친화 (40-60 단어 + 정의문)"
        passing = True
    elif not is_within:
        note = f"⚠ 첫 단락 {wc}단어 (목표 40-60)·짧으면 확장·길면 두 단락 분리"
        passing = False
    elif not has_def:
        note = "⚠ 정의문 부재·'X는 ___이다.' 형식 권장 (LLM 인용 친화)"
        passing = False
    else:
        note = "⚠ 검토 필요"
        passing = False

    return AnswerFirstReport(
        word_count=wc,
        has_definition_pattern=has_def,
        is_within_40_60=is_within,
        is_passing=passing,
        note=note,
    )


_STAT_PATTERNS = [
    r"\b\d{4}년",  # 연도
    r"\b\d{4}-\d{1,2}-\d{1,2}",  # ISO 날짜
    r"\b\d{1,3}(?:,\d{3})+",  # 1,296 같은 천 단위
    r"\b\d+\s*(?:%|건|관|개|시간|분|초|일|주|월|년|회|배|MB|GB)",
    r"\b₩\d+",
    r"\b\$\d+",
    r"\bD-\d+",  # KOLAS3 D-day
    r"\bv\d+\.\d+",  # 버전
]


def measure_fact_density(text: str) -> dict:
    """150-200단어마다 1개 통계/숫자/날짜 검증."""
    if not text:
        return {"is_passing": False, "note": "본문 없음"}

    wc = _word_count(text)
    facts: list[str] = []
    for pat in _STAT_PATTERNS:
        for m in re.finditer(pat, text):
            facts.append(m.group(0))

    fact_count = len(facts)
    # 200단어당 1개 = 0.5 / 100단어
    expected_min = max(1, wc // 200)
    is_passing = fact_count >= expected_min

    return {
        "word_count": wc,
        "fact_count": fact_count,
        "expected_minimum": expected_min,
        "is_passing": is_passing,
        "facts_sample": facts[:5],
        "note": (
            f"✓ {fact_count}개/{wc}단어 = 통계 밀도 OK"
            if is_passing
            else f"⚠ {fact_count}개/{wc}단어 = 200단어당 1+ 권장 (LLM 인용 친화)"
        ),
    }
