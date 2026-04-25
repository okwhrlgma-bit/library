"""공유 Anthropic 클라이언트 — 캐시·재시도·prompt caching.

Vision/KDC/Subject 등 모든 모듈이 이 모듈의 `cached_messages()`만 호출.
- diskcache 30일 (응답만, 이미지 base64는 캐시 키 SHA256만 사용)
- tenacity 재시도 (429, 5xx 지수 백오프)
- system 프롬프트에 cache_control: ephemeral 자동 부여 (Anthropic Prompt Caching)
- tool_use 응답 자동 파싱 → input dict 반환
"""

from __future__ import annotations

import hashlib
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from kormarc_auto.constants import (
    ANTHROPIC_CACHE_SUBDIR,
    ANTHROPIC_DEFAULT_MAX_TOKENS,
    ANTHROPIC_MAX_RETRIES,
    ANTHROPIC_TIMEOUT_SECONDS,
    CACHE_DIR,
    CACHE_TTL_SECONDS,
)

logger = logging.getLogger(__name__)


class AnthropicClientError(Exception):
    """Anthropic 호출 실패 (네트워크·인증·파싱)."""


@lru_cache(maxsize=1)
def get_anthropic_client() -> Any:
    """전역 Anthropic 클라이언트 — 환경변수 키 사용 (PO/관리자용)."""
    return _build_client(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _build_client(api_key: str | None) -> Any:
    """주어진 키로 Anthropic 클라이언트 생성. BYOK 호출자에서 사용."""
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise AnthropicClientError(
            "anthropic SDK 미설치 — `pip install anthropic`로 설치하세요."
        ) from e

    if not api_key:
        raise AnthropicClientError(
            "ANTHROPIC_API_KEY 미설정. 사서 본인 키를 UI에 입력하거나 .env에 ANTHROPIC_API_KEY 추가."
        )
    return Anthropic(api_key=api_key, timeout=ANTHROPIC_TIMEOUT_SECONDS)


@lru_cache(maxsize=1)
def get_anthropic_cache() -> Any:
    """Anthropic 응답용 diskcache (lazy import, 미설치 시 None)."""
    try:
        from diskcache import Cache
    except ImportError:
        logger.debug("diskcache 미설치 — Anthropic 캐싱 비활성")
        return None

    base = Path(os.getenv("KORMARC_CACHE_DIR", CACHE_DIR))
    path = base / ANTHROPIC_CACHE_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return Cache(str(path))


def make_image_cache_key(image_bytes_list: list[bytes], prompt_version: str, model: str) -> str:
    """이미지 묶음 + 프롬프트 버전 + 모델 → 짧은 캐시 키."""
    h = hashlib.sha256()
    for b in image_bytes_list:
        h.update(b)
    return f"vision:{model}:{prompt_version}:{h.hexdigest()[:32]}"


def make_text_cache_key(*, prompt_kind: str, model: str, prompt_version: str, payload: str) -> str:
    """텍스트 호출용 캐시 키 (KDC·Subject 등)."""
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"{prompt_kind}:{model}:{prompt_version}:{digest}"


def _ensure_cache_control_on_system(system: str | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """system 프롬프트에 cache_control: ephemeral 자동 부여."""
    if isinstance(system, str):
        return [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]

    out: list[dict[str, Any]] = []
    for block in system:
        block = dict(block)
        block.setdefault("cache_control", {"type": "ephemeral"})
        out.append(block)
    return out


def _extract_tool_input(response: Any, tool_name: str) -> dict[str, Any] | None:
    """anthropic Message 응답에서 tool_use 블록의 input dict 추출."""
    content = getattr(response, "content", []) or []
    for block in content:
        block_type = getattr(block, "type", None)
        if block_type == "tool_use" and getattr(block, "name", None) == tool_name:
            input_val = getattr(block, "input", None)
            if isinstance(input_val, dict):
                return input_val
    return None


def cached_messages(
    *,
    cache_key: str,
    model: str,
    system: str | list[dict[str, Any]],
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    tool_name: str | None = None,
    max_tokens: int = ANTHROPIC_DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    use_cache: bool = True,
    user_api_key: str | None = None,
) -> dict[str, Any]:
    """anthropic.messages.create() 래퍼.

    Args:
        cache_key: make_image_cache_key/make_text_cache_key 결과
        model: claude-sonnet-4-6 / claude-haiku-4-5-20251001 등
        system: 시스템 프롬프트 (cache_control 자동 추가)
        messages: anthropic 메시지 리스트
        tools: 도구 정의 리스트 (있으면 tool_choice로 강제)
        tool_name: tools 강제 시 도구 이름 (자동 input dict 추출)
        max_tokens: 최대 출력 토큰
        temperature: 0.0 (결정적 출력 권장)
        use_cache: False면 디스크 캐시 우회

    Returns:
        {
            "tool_input": dict | None,    # tool_use 응답이면 input dict
            "text": str | None,           # text 응답이면 합쳐진 문자열
            "raw": Any,                   # 원본 Message 객체
            "cached": bool,               # 캐시 히트 여부
        }

    Raises:
        AnthropicClientError: 호출·파싱 실패
    """
    # AI 비활성 모드 — 크레딧 절감용 (KDC 1·2순위 + 외부 API만으로 동작)
    if os.getenv("KORMARC_DISABLE_AI", "").lower() in ("1", "true", "yes"):
        logger.info("KORMARC_DISABLE_AI 설정됨 — Anthropic 호출 건너뜀: %s", cache_key)
        return {"tool_input": None, "text": None, "raw": None, "cached": False, "disabled": True}

    cache = get_anthropic_cache() if use_cache else None
    if cache is not None:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Anthropic 캐시 히트: %s", cache_key)
            return {**cached, "cached": True}

    # BYOK: 호출자가 user_api_key 명시 시 그 키 사용 (사서 본인 비용)
    # 없으면 환경변수 기본 키 (PO/관리자용)
    client = _build_client(user_api_key) if user_api_key else get_anthropic_client()

    create_kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": _ensure_cache_control_on_system(system),
        "messages": messages,
    }
    if tools:
        create_kwargs["tools"] = tools
        if tool_name:
            create_kwargs["tool_choice"] = {"type": "tool", "name": tool_name}

    try:
        response = _call_with_retry(client, create_kwargs)
    except Exception as e:
        raise AnthropicClientError(f"Anthropic 호출 실패: {e}") from e

    tool_input = _extract_tool_input(response, tool_name) if tool_name else None
    text_blocks = [
        getattr(b, "text", "") for b in getattr(response, "content", []) if getattr(b, "type", None) == "text"
    ]
    text = "".join(text_blocks) if text_blocks else None

    result = {
        "tool_input": tool_input,
        "text": text,
        "raw": None,
        "cached": False,
    }

    if cache is not None:
        cache.set(cache_key, {k: v for k, v in result.items() if k != "raw"}, expire=CACHE_TTL_SECONDS)

    return result


def _call_with_retry(client: Any, create_kwargs: dict[str, Any]) -> Any:
    """tenacity 기반 재시도 (429·5xx 지수 백오프)."""
    try:
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )
    except ImportError:
        return client.messages.create(**create_kwargs)

    try:
        from anthropic import APIError, APITimeoutError, RateLimitError
    except ImportError:
        APIError = APITimeoutError = RateLimitError = Exception  # type: ignore[assignment,misc]

    @retry(
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError, ConnectionError)),
        stop=stop_after_attempt(ANTHROPIC_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _do_call() -> Any:
        return client.messages.create(**create_kwargs)

    return _do_call()
