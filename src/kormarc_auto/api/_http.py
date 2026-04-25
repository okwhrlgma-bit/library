"""공유 HTTP 세션 — 재시도·타임아웃·캐싱.

모든 외부 API 클라이언트는 이 모듈의 `get_session()`을 사용.
중복 요청은 자동 캐시(30일 TTL)로 비용 절감.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from kormarc_auto.constants import (
    CACHE_DIR,
    CACHE_TTL_SECONDS,
    HTTP_BACKOFF_FACTOR,
    HTTP_MAX_RETRIES,
    HTTP_TIMEOUT,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_session() -> requests.Session:
    """전역 공유 requests.Session — 재시도 어댑터 장착.

    한 번만 생성되어 모든 호출에서 재사용 (커넥션 풀링).
    """
    session = requests.Session()
    retry = Retry(
        total=HTTP_MAX_RETRIES,
        backoff_factor=HTTP_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "kormarc-auto/0.1"})
    return session


def _cache_dir() -> Path:
    """캐시 디렉토리 (없으면 생성)."""
    path = Path(os.getenv("KORMARC_CACHE_DIR", CACHE_DIR))
    path.mkdir(parents=True, exist_ok=True)
    return path


@lru_cache(maxsize=1)
def get_cache() -> Any:
    """diskcache 인스턴스 (lazy import — 미설치 시 None 폴백).

    Returns:
        diskcache.Cache 또는 None
    """
    try:
        from diskcache import Cache
    except ImportError:
        logger.debug("diskcache 미설치 — 캐싱 비활성화. `pip install diskcache`로 활성화 가능.")
        return None
    return Cache(str(_cache_dir()))


def cached_get(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = HTTP_TIMEOUT,
    cache_key_extra: str = "",
    use_cache: bool = True,
) -> requests.Response:
    """캐싱된 GET 요청. 같은 (url, params) 조합은 30일간 캐시 재사용.

    캐시 키에서 인증키는 자동 제외 (보안 + 키 회전 안전).
    """
    cache = get_cache() if use_cache else None
    cache_key = None

    if cache is not None and params is not None:
        # 인증키 필드는 캐시 키에서 제외
        safe_params = {
            k: v
            for k, v in params.items()
            if k.lower() not in {"cert_key", "ttbkey", "key", "authkey", "auth_key", "api_key"}
        }
        cache_key = f"GET:{url}:{tuple(sorted(safe_params.items()))}:{cache_key_extra}"

        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("캐시 히트: %s", url)
            response = requests.Response()
            response._content = cached["content"]
            response.status_code = cached["status_code"]
            response.headers.update(cached.get("headers", {}))
            response.encoding = cached.get("encoding", "utf-8")
            return response

    session = get_session()
    response = session.get(url, params=params, headers=headers, timeout=timeout)

    if cache is not None and cache_key is not None and response.status_code == 200:
        cache.set(
            cache_key,
            {
                "content": response.content,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "encoding": response.encoding,
            },
            expire=CACHE_TTL_SECONDS,
        )

    return response
