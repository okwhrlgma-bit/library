"""프로젝트 전역 상수.

URL·타임아웃·신뢰도·기본값을 한 곳에서 관리. 매직 넘버 금지.
"""

from __future__ import annotations

from typing import Final

# ─── 외부 API 엔드포인트 ───────────────────────────────────────
NL_KOREA_ISBN_URL: Final = "https://www.nl.go.kr/seoji/SearchApi.do"
NL_KOREA_KOLISNET_URL: Final = "https://www.nl.go.kr/NL/search/openApi/searchKolisNet.do"
NL_KOREA_NL_SEARCH_URL: Final = "https://www.nl.go.kr/NL/search/openApi/search.do"
ALADIN_LOOKUP_URL: Final = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
ALADIN_SEARCH_URL: Final = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
KAKAO_BOOK_URL: Final = "https://dapi.kakao.com/v3/search/book"
DATA4LIBRARY_KEYWORDS_URL: Final = "http://data4library.kr/api/keywordList"
ANTHROPIC_API_BASE: Final = "https://api.anthropic.com/v1"

# ─── 타임아웃·재시도 ────────────────────────────────────────────
HTTP_TIMEOUT: Final = 10  # 초
HTTP_MAX_RETRIES: Final = 3
HTTP_BACKOFF_FACTOR: Final = 0.5  # 0.5s, 1s, 2s 지수 백오프

# ─── 신뢰도 (가중치) ────────────────────────────────────────────
CONFIDENCE_NL_KOREA: Final = 0.95
CONFIDENCE_KOLISNET: Final = 0.92
CONFIDENCE_ALADIN: Final = 0.80
CONFIDENCE_KAKAO: Final = 0.75
CONFIDENCE_VISION_WITH_API: Final = 0.85
CONFIDENCE_VISION_ONLY: Final = 0.65
CONFIDENCE_BARCODE: Final = 0.95
CONFIDENCE_FALLBACK: Final = 0.10

# 자동 승인 임계 (이 이상이면 사서 검토 없이 일괄 승인 가능)
AUTO_APPROVAL_THRESHOLD: Final = 0.95

# ─── 출처 표시 의무 ─────────────────────────────────────────────
ALADIN_ATTRIBUTION: Final = "도서 DB 제공 : 알라딘 인터넷서점(www.aladin.co.kr)"
NL_KOREA_ATTRIBUTION: Final = "출처: 국립중앙도서관(www.nl.go.kr)"

# ─── KORMARC 기본값 ─────────────────────────────────────────────
DEFAULT_LANGUAGE: Final = "kor"
DEFAULT_CATALOGING_AGENCY: Final = "OURLIB"
DEFAULT_LEADER: Final = "00000nam a2200000   4500"

# ─── 출력 ──────────────────────────────────────────────────────
DEFAULT_OUTPUT_DIR: Final = "./output"
KORMARC_FILE_EXT: Final = ".mrc"
MARCXML_FILE_EXT: Final = ".xml"

# ─── AI 모델 ───────────────────────────────────────────────────
DEFAULT_VISION_MODEL: Final = "claude-sonnet-4-6"
DEFAULT_TEXT_MODEL: Final = "claude-sonnet-4-6"
DEFAULT_LIGHT_MODEL: Final = "claude-haiku-4-5-20251001"

# AI 호출 타임아웃·토큰
ANTHROPIC_TIMEOUT_SECONDS: Final = 60  # 모델 추론 대기. HTTP API의 10초와 다름
ANTHROPIC_MAX_RETRIES: Final = 3
ANTHROPIC_DEFAULT_MAX_TOKENS: Final = 1024

# 프롬프트 버전 (캐시 무효화용 — 프롬프트 변경 시 +1)
VISION_PROMPT_VERSION: Final = "v1"
KDC_PROMPT_VERSION: Final = "v1"
SUBJECT_PROMPT_VERSION: Final = "v1"

# 이미지 리사이즈 (Anthropic 권장 longest_side ≤ 1568px)
VISION_IMAGE_MAX_LONGEST_SIDE: Final = 1568

# ─── 캐시 ──────────────────────────────────────────────────────
CACHE_DIR: Final = ".cache/kormarc-auto"
ANTHROPIC_CACHE_SUBDIR: Final = "anthropic"
CACHE_TTL_SECONDS: Final = 60 * 60 * 24 * 30  # 30일 (서지 데이터는 거의 안 변함)

# ─── 수익화 (MVP) ──────────────────────────────────────────────
FREE_QUOTA_DEFAULT: Final = 50  # 신규 키 1개당 무료 생성 건수
PRICE_PER_RECORD_KRW: Final = 100  # 권당 안내 가격 (정식 결제는 MVP-2)
PAYMENT_INFO_URL: Final = "https://example.com/kormarc-auto/pricing"  # PO 가격 페이지 (추후 실 URL 교체)
USAGE_LOG_PATH: Final = "logs/usage.jsonl"
USAGE_DB_PATH: Final = "logs/usage.json"

# ─── 서버 ──────────────────────────────────────────────────────
DEFAULT_SERVER_HOST: Final = "127.0.0.1"  # 외부 노출은 cloudflared 통해서만
DEFAULT_SERVER_PORT: Final = 8000
DEFAULT_UI_PORT: Final = 8501

# ─── 한자 감지 정규식 (CJK Unified Ideographs) ─────────────────
HANJA_PATTERN: Final = r"[一-鿿]"

# ─── 880 페어 대상 필드 ─────────────────────────────────────────
FIELDS_880_PAIRABLE: Final = frozenset({"100", "245", "490", "505", "700"})
