"""주제명 (650 필드) 자동 추천 — 도정나 키워드 + Claude AI.

전략:
1. 도정나 keywords (대출 통계 기반) — 신뢰도 0.6
2. Claude AI 추천 5개 (NLSH 어휘 스타일 권장) — 신뢰도 0.75
3. 합쳐서 dedup + 신뢰도 정렬, 최대 8개 반환

650 필드 형식:
    지시기호1 = ' ' (소스)
    지시기호2 = '8' (NLSH/표준화 안 된 보조 어휘)
    ▾a = 주제명
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from kormarc_auto._anthropic_client import (
    AnthropicClientError,
    cached_messages,
    make_text_cache_key,
)
from kormarc_auto.constants import DEFAULT_TEXT_MODEL, SUBJECT_PROMPT_VERSION

logger = logging.getLogger(__name__)


_SUBJECT_TOOL = {
    "name": "recommend_subjects",
    "description": "한국 도서관 주제명(NLSH 스타일) 후보를 보고한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "subjects": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "주제명 (한국어, NLSH 어휘 스타일 권장)",
                        },
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "rationale": {"type": "string"},
                    },
                    "required": ["term", "confidence"],
                },
            }
        },
        "required": ["subjects"],
    },
}


_SUBJECT_SYSTEM_PROMPT = """\
당신은 한국 공공도서관 사서로 NLSH(국립중앙도서관 주제명표목표) 어휘에 익숙하다.
주어진 도서 메타데이터를 보고 KORMARC 650 필드용 주제명 후보를 1~5개 추천한다.

규칙:
- 한국어 통제어휘 우선 (NLSH 스타일)
- 너무 일반적인 용어(예: '책', '문학') 금지
- 너무 구체적/지엽적 용어보다 검색용으로 의미 있는 수준
- 동의어·이형 분리 금지 — 가장 일반적 형태 1개
- 5개를 반드시 채울 필요는 없다 (모르는 건 빼라)
- 신뢰도는 합쳐서 약 1.0~3.0

반드시 recommend_subjects 도구를 호출해 결과를 보고한다.
"""


def recommend_subjects(
    book_data: dict[str, Any],
    *,
    user_api_key: str | None = None,
) -> list[dict[str, Any]]:
    """주제명 후보 추천 (최대 8개).

    Args:
        book_data: BookData dict

    Returns:
        후보 리스트 (신뢰도 내림차순). 각 항목:
        - `term`: 주제명
        - `confidence`: 0.0~1.0
        - `source`: "data4library" / "ai"
        - `rationale`: 추천 이유 (있을 때)
    """
    candidates: list[dict[str, Any]] = []

    # 1) 도정나 키워드
    for kw in (book_data.get("keywords") or [])[:10]:
        kw = str(kw).strip()
        if kw:
            candidates.append(
                {
                    "term": kw,
                    "confidence": 0.6,
                    "source": "data4library",
                    "rationale": "도서관 정보나루 대출 데이터 키워드",
                }
            )

    # 2) AI 추천
    if _has_ai_signal(book_data):
        try:
            ai_results = _ai_subject_recommend(book_data, user_api_key=user_api_key)
            candidates.extend(ai_results)
        except AnthropicClientError as e:
            logger.warning("주제명 AI 추천 실패: %s", e)

    # 3) dedup + 정렬
    seen: dict[str, dict[str, Any]] = {}
    for c in candidates:
        term = c["term"].strip()
        if not term:
            continue
        existing = seen.get(term)
        if existing is None or c["confidence"] > existing["confidence"]:
            seen[term] = c

    out = sorted(seen.values(), key=lambda c: c["confidence"], reverse=True)
    return out[:8]


def _has_ai_signal(book_data: dict[str, Any]) -> bool:
    return bool(
        book_data.get("title")
        or book_data.get("summary")
        or book_data.get("category")
    )


def _ai_subject_recommend(
    book_data: dict[str, Any],
    *,
    user_api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Claude로 주제명 후보 1~5개 반환."""
    use_model = os.getenv("CLAUDE_TEXT_MODEL") or DEFAULT_TEXT_MODEL

    payload = {
        "title": book_data.get("title"),
        "subtitle": book_data.get("subtitle"),
        "author": book_data.get("author"),
        "category": book_data.get("category"),
        "summary": (book_data.get("summary") or "")[:600],
        "kdc": book_data.get("kdc"),
        "existing_keywords": (book_data.get("keywords") or [])[:5],
    }
    payload_str = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    cache_key = make_text_cache_key(
        prompt_kind="subject",
        model=use_model,
        prompt_version=SUBJECT_PROMPT_VERSION,
        payload=payload_str,
    )

    user_text = (
        "다음 도서의 NLSH 스타일 주제명 후보를 1~5개 추천하세요.\n\n"
        f"```json\n{payload_str}\n```"
    )

    result = cached_messages(
        cache_key=cache_key,
        model=use_model,
        system=_SUBJECT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
        tools=[_SUBJECT_TOOL],
        tool_name="recommend_subjects",
        max_tokens=400,
        user_api_key=user_api_key,
    )

    tool_input = result.get("tool_input") or {}
    subjects_raw = tool_input.get("subjects", []) or []
    out: list[dict[str, Any]] = []
    for s in subjects_raw[:5]:
        term = str(s.get("term", "")).strip()
        if not term:
            continue
        try:
            conf = float(s.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        out.append(
            {
                "term": term,
                "confidence": max(0.0, min(conf, 0.85)),
                "source": "ai",
                "rationale": str(s.get("rationale", "")).strip() or "AI 추천",
            }
        )
    return out
