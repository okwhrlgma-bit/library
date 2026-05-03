"""오프라인 데모 mock LLM·API 서버 — v0.6.0 (Part 92 §A.1).

PO 명령 (Part 92): "30초·API 키 X 데모 = 표준"

작동:
1. `kormarc-auto demo` subcommand 실행
2. 본 모듈 = in-process mock·5~10 sample books 사전 답변
3. 외부 API (NL·data4library·알라딘·Anthropic) 모두 mock
4. 사용자는 .env·키 발급 X·30초 안에 첫 .mrc 출력 확인

근거:
- fakellm·mockllm (2025 PyPI)
- Anthropic Prism harness (localhost:4010)
- Stripe sentinel test cards (4242 패턴)
"""

from __future__ import annotations

from dataclasses import dataclass

# Sentinel ISBN (Stripe-style) = 데모·테스트 시 always-success/fail
SENTINEL_ISBNS = {
    "9788900000000": "always_success",  # 정상 fetch (어린왕자 mock)
    "9788900000001": "no_match",  # SEOJI 미등록 (Vision 폴백 trigger)
    "9788900000002": "ai_low_confidence",  # AI 신뢰도 낮음 (사서 검토 trigger)
    "9788900000003": "rate_limit",  # 외부 API 429 시뮬
    "9788900000004": "network_error",  # 네트워크 장애 시뮬
}

# 5~10 sample books = 데모 시 즉시 사용 가능 (committed fixture)
SAMPLE_BOOKS: dict[str, dict] = {
    "9788937437076": {
        "isbn": "9788937437076",
        "title": "어린 왕자",
        "author": "생텍쥐페리",
        "publisher": "민음사",
        "publication_year": "2007",
        "kdc": "863.2",
        "additional_code": "73810",
        "pages": "150",
        "book_size": "20",
        "summary": "프랑스 작가 생텍쥐페리의 동화·여러 별을 여행하는 어린 왕자",
    },
    "9788932473901": {
        "isbn": "9788932473901",
        "title": "82년생 김지영",
        "author": "조남주",
        "publisher": "민음사",
        "publication_year": "2016",
        "kdc": "813.7",
        "additional_code": "03810",
        "pages": "192",
        "book_size": "20",
    },
    "9788936434120": {
        "isbn": "9788936434120",
        "title": "작별하지 않는다",
        "author": "한강",
        "publisher": "문학동네",
        "publication_year": "2021",
        "kdc": "813.7",
        "additional_code": "03810",
    },
    "9788960517257": {
        "isbn": "9788960517257",
        "title": "코스모스",
        "author": "칼 세이건",
        "publisher": "사이언스북스",
        "publication_year": "2010",
        "kdc": "443",
        "additional_code": "03440",
    },
    "9788937462788": {
        "isbn": "9788937462788",
        "title": "사피엔스",
        "author": "유발 하라리",
        "publisher": "김영사",
        "publication_year": "2015",
        "kdc": "909.1",
        "additional_code": "03900",
    },
    # 의학 (페르소나 04)
    "9788991915082": {
        "isbn": "9788991915082",
        "title": "당뇨병 임상 가이드라인",
        "author": "대한당뇨병학회",
        "publisher": "대한당뇨병학회",
        "publication_year": "2024",
        "kdc": "513.6",
        "summary": "당뇨병 진단·치료·관리 임상 권고",
    },
    # 학교 (페르소나 01·DLS)
    "9788961723459": {
        "isbn": "9788961723459",
        "title": "중학교 수학 1학년 워크북",
        "author": "교육청",
        "publisher": "한국교육과정평가원",
        "publication_year": "2024",
        "kdc": "510",
        "additional_code": "53400",  # 학습참고서
    },
}


@dataclass(frozen=True)
class MockResponse:
    """mock 응답 1건."""

    status_code: int
    json_body: dict
    delay_ms: int = 50  # 실제 호출 시뮬


def mock_seoji(isbn: str) -> MockResponse:
    """SEOJI mock 응답."""
    if isbn in SENTINEL_ISBNS:
        kind = SENTINEL_ISBNS[isbn]
        if kind == "no_match":
            return MockResponse(200, {"docs": []})
        if kind == "rate_limit":
            return MockResponse(429, {"error": "rate_limit"})
        if kind == "network_error":
            return MockResponse(500, {"error": "network"})
        # always_success → mock 1건
        return MockResponse(200, {"docs": [SAMPLE_BOOKS["9788937437076"]]})

    book = SAMPLE_BOOKS.get(isbn)
    if not book:
        return MockResponse(200, {"docs": []})
    return MockResponse(200, {"docs": [book]})


def mock_data4library(isbn: str) -> MockResponse:
    """data4library mock (KDC + 키워드)."""
    book = SAMPLE_BOOKS.get(isbn)
    if not book:
        return MockResponse(200, {"response": {"docs": []}})
    return MockResponse(
        200,
        {
            "response": {
                "docs": [
                    {
                        "doc": {
                            "isbn13": isbn,
                            "kdc": book.get("kdc", ""),
                            "keywords": ["문학", "소설", "한국문학"],
                        }
                    }
                ]
            }
        },
    )


def mock_aladin(isbn: str) -> MockResponse:
    """알라딘 mock (505 목차·520 요약)."""
    book = SAMPLE_BOOKS.get(isbn)
    if not book:
        return MockResponse(200, {"item": []})
    return MockResponse(
        200,
        {
            "item": [
                {
                    "isbn13": isbn,
                    "title": book.get("title", ""),
                    "author": book.get("author", ""),
                    "description": book.get("summary", ""),
                    "toc": "1장. 시작\n2장. 본문\n3장. 결론",
                    "cover": "https://image.aladin.co.kr/mock.jpg",
                }
            ]
        },
    )


def mock_anthropic_kdc_recommendation(text: str) -> MockResponse:
    """Anthropic KDC 추천 mock (top-3·결정성)."""
    # 시드 = text hash → 결정성
    seed = sum(ord(c) for c in text[:50]) if text else 0
    if seed % 5 == 0:
        kdcs = ["813.7", "813.6", "810"]  # 한국문학
    elif seed % 5 == 1:
        kdcs = ["863.2", "863", "860"]  # 외국문학
    elif seed % 5 == 2:
        kdcs = ["443", "440", "400"]  # 자연과학
    elif seed % 5 == 3:
        kdcs = ["513.6", "513", "510"]  # 의학
    else:
        kdcs = ["909.1", "900", "910"]  # 역사

    return MockResponse(
        200,
        {
            "content": [
                {
                    "type": "text",
                    "text": f'{{"top3": {kdcs}, "confidence": 0.85, "reasoning": "mock·결정성 보장"}}',
                }
            ],
            "usage": {"input_tokens": 200, "output_tokens": 30},
        },
    )


def list_demo_isbns() -> list[str]:
    """데모 시 사용 가능한 ISBN 리스트 (사용자 안내·README)."""
    real = list(SAMPLE_BOOKS.keys())
    sentinel = list(SENTINEL_ISBNS.keys())
    return real + sentinel


def is_demo_mode() -> bool:
    """환경변수 KORMARC_DEMO_MODE=1 이면 mock 활성."""
    import os

    return os.getenv("KORMARC_DEMO_MODE") == "1"


__all__ = [
    "SAMPLE_BOOKS",
    "SENTINEL_ISBNS",
    "MockResponse",
    "is_demo_mode",
    "list_demo_isbns",
    "mock_aladin",
    "mock_anthropic_kdc_recommendation",
    "mock_data4library",
    "mock_seoji",
]
