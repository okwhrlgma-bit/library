"""갈래 B Cycle 16A (P36·외부 매출 보고서) — 블로그 자동 변환 파이프라인.

원칙 (외부 보고서 P36 정합):
- 자체 블로그 = canonical 원본 (rel=canonical)
- 네이버 = Selenium 임시저장만 (publish 자동 X·약관 위반)
- 브런치 = 클립보드 paste (공식 API 미공개)
- LinkedIn/Medium = 영문 자동 가능
- 첫 단락 30%+ 패러프레이징 (네이버 C-Rank 중복 페널티 회피)
- 사실확인 = KOLAS III 종료일 등 인용 수치 자동 검증
"""

from kormarc_auto.blog_pipeline.canonical import (
    BlogPost,
    add_canonical_footer,
    build_canonical_html,
    extract_frontmatter,
)
from kormarc_auto.blog_pipeline.fact_checker import (
    KOLAS3_EXPECTED_FACTS,
    check_post_facts,
)
from kormarc_auto.blog_pipeline.intro_paraphraser import (
    levenshtein_ratio,
    measure_paraphrase_strength,
)

__all__ = [
    "KOLAS3_EXPECTED_FACTS",
    "BlogPost",
    "add_canonical_footer",
    "build_canonical_html",
    "check_post_facts",
    "extract_frontmatter",
    "levenshtein_ratio",
    "measure_paraphrase_strength",
]
