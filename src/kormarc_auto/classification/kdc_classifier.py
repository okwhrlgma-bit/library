"""KDC 6판 자동 분류 — 다단계 폴백 + Claude AI.

순서:
1. NL Korea가 KDC 부여 → 신뢰도 0.95
2. ISBN 부가기호 첫 자리 → 주류 매핑 (보조, 신뢰도 0.40)
3. 위 두 가지가 부족하면 Claude AI 후보 3개 + 신뢰도
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
from kormarc_auto.constants import (
    DEFAULT_TEXT_MODEL,
    KDC_PROMPT_VERSION,
)

logger = logging.getLogger(__name__)


# ISBN 부가기호 첫 자리 → KDC 주류 (대략, 보조용)
ADDITIONAL_CODE_TO_KDC_MAIN = {
    "0": "000",
    "1": "030",
    "2": "330",
    "3": "330",
    "4": "300",
    "5": "375",
    "6": "375",
    "7": "813",
    "8": "375",
    "9": "000",
}


_KDC_TOOL = {
    "name": "recommend_kdc_codes",
    "description": "주어진 도서 메타데이터에 가장 적합한 KDC 6판 분류기호 후보 3개를 신뢰도 순으로 추천한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "KDC 6판 분류기호 (예: '813.7', '320.911', '004.7'). 최소 3자리.",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "0.0~1.0",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "1~2문장으로 추천 이유",
                        },
                    },
                    "required": ["code", "confidence", "rationale"],
                },
            }
        },
        "required": ["candidates"],
    },
}


_KDC_SYSTEM_PROMPT = """\
당신은 한국 공공·학교 도서관에서 KDC 6판(한국십진분류법)을 매일 적용하는 전문 사서다.
주어진 도서 메타데이터를 보고 가장 적합한 KDC 분류기호를 정확히 3개 추천한다.

KDC 6판 주류:
000 총류 / 010 도서학·서지학 / 020 문헌정보학 / 030 백과사전 / 040 강연집·수필집·연설문집
050 일반연속간행물 / 060 일반학회·단체·협회 / 070 신문·언론·저널리즘 / 080 일반전집·총서

100 철학 / 110 형이상학 / 120 인식론·인과론·인간학 / 130 철학의체계 / 140 경학
150 동양철학·사상 / 160 서양철학 / 170 논리학 / 180 심리학 / 190 윤리학·도덕철학

200 종교 / 210 비교종교 / 220 불교 / 230 기독교 / 240 도교 / 250 천도교
260 신도 / 270 바라문교·인도교 / 280 이슬람교 / 290 기타종교

300 사회과학 / 310 통계학 / 320 경제학 / 330 사회학·사회문제 / 340 정치학
350 행정학 / 360 법학 / 370 교육학 / 380 풍속·민속학 / 390 국방·군사학

400 자연과학 / 410 수학 / 420 물리학 / 430 화학 / 440 천문학
450 지학 / 460 광물학 / 470 생명과학 / 480 식물학 / 490 동물학

500 기술과학 / 510 의학 / 520 농업·농학 / 530 공학·공업일반·토목공학·환경공학
540 건축공학 / 550 기계공학 / 560 전기공학·전자공학 / 570 화학공학 / 580 제조업
590 가정학·가정관리 및 가족생활

600 예술 / 610 건축술 / 620 조각·조형미술 / 630 공예·장식미술 / 640 서예
650 회화·도화·디자인 / 660 사진예술 / 670 음악 / 680 공연예술·매체예술 / 690 오락·스포츠

700 언어 / 710 한국어 / 720 중국어 / 730 일본어·기타아시아 제어 / 740 영어
750 독일어 / 760 프랑스어 / 770 스페인어·포르투갈어 / 780 이탈리아어 / 790 기타제어

800 문학 / 810 한국문학 / 813 한국소설 / 814 한국수필 / 811 한국시 / 812 한국희곡
815 한국웅변·연설 / 816 한국일기·서간·기행문 / 817 한국풍자·해학 / 818 한국기록
820 중국문학 / 830 일본문학·기타아시아 제문학 / 840 영미문학 / 850 독일문학
860 프랑스문학 / 870 스페인·포르투갈문학 / 880 이탈리아문학 / 890 기타제문학

900 역사 / 910 아시아(한국제외) / 911 한국사 / 912 한국지리·풍속 / 920 유럽
930 아프리카 / 940 북아메리카 / 950 남아메리카 / 960 오세아니아 / 970 양극지방
980 지리·지지 / 990 전기

규칙:
- 강목·세목까지 (예: 한국 현대소설은 813.7 / 한국 단편소설집은 813.6)
- 신뢰도는 합쳐서 약 1.0 (모르는 것까지 억지로 1.0 만들지 말 것)
- 분류 모호할 땐 후보 1~2개만 강한 신뢰도로 보고
- ISBN 부가기호 힌트가 있으면 참고하되 절대 신뢰하지 말 것 (오류 흔함)

반드시 recommend_kdc_codes 도구를 호출해 결과를 보고한다.
"""


def recommend_kdc(
    book_data: dict[str, Any],
    *,
    user_api_key: str | None = None,
) -> list[dict[str, Any]]:
    """KDC 분류 후보 추천 (다단계).

    Args:
        book_data: BookData dict (title, author, summary, toc 등 포함)

    Returns:
        후보 리스트 (신뢰도 내림차순). 각 항목:
        - `code`: KDC 분류기호 (예: "813.7")
        - `confidence`: 0.0~1.0
        - `source`: "nl_korea" / "additional_code" / "ai" / "fallback"
        - `rationale`: 추천 이유
    """
    candidates: list[dict[str, Any]] = []

    # 1순위: NL Korea가 이미 KDC 부여한 경우
    if book_data.get("kdc"):
        candidates.append(
            {
                "code": str(book_data["kdc"]),
                "confidence": 0.95,
                "source": "nl_korea",
                "rationale": "국립중앙도서관 부여 KDC",
            }
        )

    # 2순위: ISBN 부가기호 (보조)
    add_code = book_data.get("additional_code")
    if add_code and len(str(add_code)) >= 1:
        first_digit = str(add_code)[0]
        if first_digit in ADDITIONAL_CODE_TO_KDC_MAIN:
            candidates.append(
                {
                    "code": ADDITIONAL_CODE_TO_KDC_MAIN[first_digit],
                    "confidence": 0.40,
                    "source": "additional_code",
                    "rationale": f"ISBN 부가기호 {add_code} 첫 자리 매핑",
                }
            )

    # 3순위: AI 추천 (1·2순위가 부족할 때만)
    top_conf = max((c["confidence"] for c in candidates), default=0.0)
    if top_conf < 0.80 and _has_ai_signal(book_data):
        try:
            ai_results = _ai_kdc_recommend(book_data, user_api_key=user_api_key)
            candidates.extend(ai_results)
        except AnthropicClientError as e:
            logger.warning("KDC AI 추천 실패: %s", e)

    candidates.sort(key=lambda c: c["confidence"], reverse=True)

    return candidates or [
        {
            "code": "000",
            "confidence": 0.10,
            "source": "fallback",
            "rationale": "후보 없음 — 사서 직접 분류 필요",
        }
    ]


def _has_ai_signal(book_data: dict[str, Any]) -> bool:
    """AI 호출에 의미 있는 입력 데이터가 있는지."""
    return bool(
        book_data.get("title")
        or book_data.get("summary")
        or book_data.get("category")
        or book_data.get("toc")
    )


def _ai_kdc_recommend(
    book_data: dict[str, Any],
    *,
    user_api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Claude로 KDC 후보 3개 + 신뢰도 + 이유 반환."""
    use_model = os.getenv("CLAUDE_TEXT_MODEL") or DEFAULT_TEXT_MODEL

    payload = {
        "title": book_data.get("title"),
        "subtitle": book_data.get("subtitle"),
        "author": book_data.get("author"),
        "publisher": book_data.get("publisher"),
        "category": book_data.get("category"),
        "summary": (book_data.get("summary") or "")[:600],
        "toc": (book_data.get("toc") or "")[:500],
        "additional_code_hint": book_data.get("additional_code"),
    }
    payload_str = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    cache_key = make_text_cache_key(
        prompt_kind="kdc",
        model=use_model,
        prompt_version=KDC_PROMPT_VERSION,
        payload=payload_str,
    )

    user_text = (
        "다음 도서의 KDC 6판 분류기호 후보를 정확히 1~3개 추천하세요.\n\n"
        f"```json\n{payload_str}\n```"
    )

    result = cached_messages(
        cache_key=cache_key,
        model=use_model,
        system=_KDC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_text}],
        tools=[_KDC_TOOL],
        tool_name="recommend_kdc_codes",
        max_tokens=600,
        user_api_key=user_api_key,
    )

    tool_input = result.get("tool_input") or {}
    candidates_raw = tool_input.get("candidates", []) or []
    out: list[dict[str, Any]] = []
    for c in candidates_raw[:3]:
        code = str(c.get("code", "")).strip()
        if not code:
            continue
        try:
            conf = float(c.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        out.append(
            {
                "code": code,
                "confidence": max(0.0, min(conf, 0.85)),  # AI 결과 상한 0.85 (NL Korea보다 낮게)
                "source": "ai",
                "rationale": str(c.get("rationale", "")).strip() or "AI 추천",
            }
        )
    return out


def get_anthropic_client() -> Any:
    """[하위 호환] _anthropic_client.get_anthropic_client로 위임."""
    from kormarc_auto._anthropic_client import get_anthropic_client as _get

    return _get()
