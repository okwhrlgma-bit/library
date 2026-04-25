"""KOLIS-NET 다른 도서관 마크 비교 (사서 분류 의사결정 보조).

같은 ISBN을 다른 도서관이 어떻게 분류했는지(KDC, 청구기호, 주제명) 보여주어
사서가 일관성 있는 분류 결정을 내리도록 돕는다.

KOLIS-NET API:
    https://www.nl.go.kr/NL/search/openApi/searchKolisNet.do
    인증키 필요 (NL_CERT_KEY 재사용 — 같은 발급처)
"""

from __future__ import annotations

import logging
import os
from collections import Counter
from typing import Any

import requests

from kormarc_auto.api._http import cached_get
from kormarc_auto.constants import (
    CONFIDENCE_KOLISNET,
    HTTP_TIMEOUT,
    NL_KOREA_KOLISNET_URL,
)

logger = logging.getLogger(__name__)


class KolisNetError(Exception):
    """KOLIS-NET API 호출 실패."""


def fetch_other_libraries(
    isbn: str,
    *,
    cert_key: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """ISBN으로 KOLIS-NET 검색 → 다른 도서관의 분류·청구기호 등 추출.

    Args:
        isbn: 13자리 ISBN
        cert_key: 인증키 (없으면 환경변수)
        limit: 최대 결과 수

    Returns:
        각 도서관별 정보 dict 리스트:
        {
          "library_name": str,
          "kdc": str | None,
          "call_number": str | None,
          "subjects": list[str],
        }
    """
    key = cert_key or os.getenv("NL_CERT_KEY")
    if not key:
        raise KolisNetError("NL_CERT_KEY 환경변수 미설정")

    params = {
        "key": key,
        "kwd": isbn,
        "pageNum": 1,
        "pageSize": max(1, min(limit, 50)),
    }

    try:
        response = cached_get(
            NL_KOREA_KOLISNET_URL, params=params, timeout=HTTP_TIMEOUT
        )
        response.raise_for_status()
    except requests.Timeout as e:
        raise KolisNetError(f"타임아웃 (isbn={isbn})") from e
    except requests.RequestException as e:
        raise KolisNetError(f"요청 실패: {e}") from e

    return _parse(response.text or "", limit=limit)


def summarize_classification(items: list[dict[str, Any]]) -> dict[str, Any]:
    """다른 도서관 분류 결과 요약 — 사서 의사결정 보조.

    Returns:
        {
            "total_libraries": int,
            "kdc_distribution": [(code, count), ...],   # 빈도순
            "most_common_kdc": str | None,
            "subjects_top": [(term, count), ...],
            "call_numbers_sample": list[str],           # 처음 5개
            "confidence": float                          # KOLIS-NET 표본 크기 기반
        }
    """
    kdcs = [it.get("kdc") for it in items if it.get("kdc")]
    kdc_counter = Counter(kdcs)
    subjects = [s for it in items for s in (it.get("subjects") or [])]
    subj_counter = Counter(subjects)
    call_numbers = [it["call_number"] for it in items if it.get("call_number")][:5]

    most_common_kdc = kdc_counter.most_common(1)[0][0] if kdc_counter else None
    sample_size = len(items)
    confidence = min(0.95, CONFIDENCE_KOLISNET * (sample_size / max(sample_size, 5)))

    return {
        "total_libraries": sample_size,
        "kdc_distribution": kdc_counter.most_common(10),
        "most_common_kdc": most_common_kdc,
        "subjects_top": subj_counter.most_common(10),
        "call_numbers_sample": call_numbers,
        "confidence": confidence,
    }


def _parse(xml_or_json_text: str, *, limit: int) -> list[dict[str, Any]]:
    """KOLIS-NET 응답 파싱 (XML 또는 JSON 자동 판별)."""
    text = xml_or_json_text.strip()
    if text.startswith("<"):
        return _parse_xml(text, limit=limit)
    if text.startswith("{") or text.startswith("["):
        return _parse_json(text, limit=limit)
    logger.warning("KOLIS-NET 응답 형식 불명: %s...", text[:60])
    return []


def _parse_xml(text: str, *, limit: int) -> list[dict[str, Any]]:
    """KOLIS-NET XML 파싱 (실응답 스키마 확인 필요 — 보수적)."""
    try:
        from xml.etree import ElementTree as ET

        root = ET.fromstring(text)
    except ET.ParseError as e:
        logger.warning("KOLIS-NET XML 파싱 실패: %s", e)
        return []

    items: list[dict[str, Any]] = []
    for item in root.iter("item"):
        items.append(
            {
                "library_name": _text(item, "libName") or _text(item, "library_name"),
                "kdc": _text(item, "kdc") or _text(item, "callNo")[:5] if _text(item, "callNo") else None,
                "call_number": _text(item, "callNo") or _text(item, "call_number"),
                "subjects": _split(_text(item, "keyword")),
            }
        )
        if len(items) >= limit:
            break
    return items


def _parse_json(text: str, *, limit: int) -> list[dict[str, Any]]:
    import json

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning("KOLIS-NET JSON 파싱 실패: %s", e)
        return []

    docs = data.get("docs") or data.get("items") or []
    out: list[dict[str, Any]] = []
    for d in docs[:limit]:
        out.append(
            {
                "library_name": d.get("LIB_NAME") or d.get("library_name"),
                "kdc": d.get("KDC") or d.get("kdc"),
                "call_number": d.get("CALL_NO") or d.get("call_number"),
                "subjects": _split(d.get("KEYWORD") or d.get("keyword")),
            }
        )
    return out


def _text(elem: Any, tag: str) -> str:
    found = elem.find(tag)
    return (found.text or "").strip() if found is not None and found.text else ""


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in str(value).replace(",", ";").split(";") if v.strip()]
