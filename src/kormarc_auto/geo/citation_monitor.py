"""갈래 B Cycle 18B P40 — LLM AI 인용 모니터링.

원칙:
- 표준 쿼리 10개 = 베이스라인 측정 (주 1회 cron 권장)
- 응답 텍스트 → 우리 SaaS·경쟁사 인용 여부 추출
- 비용 캡 (월 $50 초과 = 일시 중단·V2 비용 폭주 방지)

V2 안전장치 정합:
- 외부 API 호출 자동 = monitoring/scripts/llm_citation_monitor.py (별도 cron·헌법 §3)
- 본 모듈 = 응답 파싱·결과 측정만 (LLM 호출은 외부 트리거)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

# 표준 쿼리 10개 (외부 매출 보고서 P40 정합)
STANDARD_QUERIES: list[str] = [
    "한국 도서관 KORMARC 자동 생성 SaaS 추천",
    "도서관 마크 자동화 도구",
    "KOLAS III 마이그레이션 솔루션",
    "KORMARC 880 한자 병기 자동",
    "사서 마크 작성 프로그램",
    "독서로 DLS MARC 일괄 등록",
    "ISBN MARC 변환",
    "KOLAS III 종료 대안",
    "한국 도서관 SaaS 가격",
    "도서관 정보누리 KNU 대안",
]

# 우리 SaaS 식별 패턴
OUR_BRAND_PATTERNS = [
    r"kormarc[_\-\s]*auto",
    r"코마크[\-\s]*오토",
    r"한국\s*도서관\s*KORMARC\s*자동",
]

# 경쟁사 인용 비교 (공정한 측정·비방 X)
COMPETITOR_PATTERNS = {
    "alpas": [r"알파스", r"ALPAS", r"이씨오"],
    "k_las_3": [r"K-LAS\s*3", r"K LAS 3"],
    "kolas_extension": [r"코라스\s*Ⅲ\s*확장", r"KOLAS\s*III\s*확장"],
    "kolas_web": [r"KOLAS-WEB", r"KOLAS\s*WEB"],
    "marcedit": [r"MarcEdit", r"마크에딧"],
}

CitationKind = Literal["our_brand", "competitor", "none"]


@dataclass(frozen=True)
class CitationCheckResult:
    """1 쿼리 결과 = 인용 여부 + 경쟁사 비교."""

    query: str
    response_text: str
    our_brand_cited: bool
    competitor_citations: dict[str, bool]
    response_word_count: int
    note: str

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "our_brand_cited": self.our_brand_cited,
            "competitor_citations": self.competitor_citations,
            "response_word_count": self.response_word_count,
            "note": self.note,
        }


def parse_citation_response(query: str, response_text: str) -> CitationCheckResult:
    """LLM 응답 → 인용 여부 추출."""
    our_cited = any(re.search(p, response_text, re.IGNORECASE) for p in OUR_BRAND_PATTERNS)

    comp_cited: dict[str, bool] = {}
    for name, patterns in COMPETITOR_PATTERNS.items():
        comp_cited[name] = any(re.search(p, response_text, re.IGNORECASE) for p in patterns)

    wc = len([t for t in response_text.split() if t])

    if our_cited and not any(comp_cited.values()):
        note = "🟢 우리만 인용·우월"
    elif our_cited:
        cited_competitors = [k for k, v in comp_cited.items() if v]
        note = f"🟡 우리 + 경쟁 {len(cited_competitors)}개 ({','.join(cited_competitors)})"
    elif any(comp_cited.values()):
        cited_competitors = [k for k, v in comp_cited.items() if v]
        note = f"🔴 우리 미인용·경쟁 {','.join(cited_competitors)}만 인용"
    else:
        note = "⚪ 인용 없음·SEO 부재 또는 신규 카테고리"

    return CitationCheckResult(
        query=query,
        response_text=response_text,
        our_brand_cited=our_cited,
        competitor_citations=comp_cited,
        response_word_count=wc,
        note=note,
    )


def build_baseline_query_set() -> list[dict]:
    """표준 쿼리 10개 베이스라인 측정 set."""
    return [
        {
            "id": f"q-{i + 1:02d}",
            "query": q,
            "expected_our_citation": True,  # 목표
            "competitor_check": True,
        }
        for i, q in enumerate(STANDARD_QUERIES)
    ]


def aggregate_results(results: list[CitationCheckResult]) -> dict:
    """전체 베이스라인 집계."""
    total = len(results)
    if total == 0:
        return {"total": 0, "our_citation_rate_pct": 0.0, "note": "데이터 없음"}

    our_count = sum(1 for r in results if r.our_brand_cited)
    competitor_only = sum(
        1 for r in results if not r.our_brand_cited and any(r.competitor_citations.values())
    )

    return {
        "total": total,
        "our_citation_count": our_count,
        "our_citation_rate_pct": round(our_count / total * 100, 1),
        "competitor_only_count": competitor_only,
        "competitor_only_rate_pct": round(competitor_only / total * 100, 1),
        "no_citation_count": total - our_count - competitor_only,
        "note": (
            f"베이스라인 {our_count}/{total} ({our_count / total * 100:.0f}%) 우리 인용·"
            f"경쟁만 {competitor_only}건"
        ),
    }
