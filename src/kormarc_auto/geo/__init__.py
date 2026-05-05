"""갈래 B Cycle 18B (P40·외부 매출 보고서) — LLM GEO + AI 인용 모니터링.

원칙 (외부 매출 보고서 P40 정합):
- 첫 단락 40-60단어 정의문 강제 (AI Overviews 인용 친화)
- 150-200단어마다 통계/숫자/날짜 1개 (76.1% AI 인용 = 구글 Top 10)
- 표준 LLM 쿼리 10개 = 주 1회 베이스라인 측정
- 비용 캡 (월 $50 초과 시 일시 중단·V2 비용 폭주 방지)
"""

from kormarc_auto.geo.answer_first import (
    AnswerFirstReport,
    measure_answer_first,
    measure_fact_density,
)
from kormarc_auto.geo.citation_monitor import (
    STANDARD_QUERIES,
    CitationCheckResult,
    build_baseline_query_set,
    parse_citation_response,
)

__all__ = [
    "STANDARD_QUERIES",
    "AnswerFirstReport",
    "CitationCheckResult",
    "build_baseline_query_set",
    "measure_answer_first",
    "measure_fact_density",
    "parse_citation_response",
]
