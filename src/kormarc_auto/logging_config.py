"""중앙 로깅 설정.

CLI/Streamlit/테스트에서 한 줄로 호출. 시크릿 자동 마스킹.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from typing import Final

SENSITIVE_PATTERNS: Final = [
    re.compile(r"(cert_key|ttbkey|api_key|authorization|x-api-key)=([^&\s]+)", re.IGNORECASE),
    re.compile(r"(sk-ant-[A-Za-z0-9_-]{10,})"),
    re.compile(r"(re_[A-Za-z0-9]{20,})"),
    re.compile(r"(ghp_[A-Za-z0-9]{30,})"),
]


class SecretMaskingFilter(logging.Filter):
    """로그 메시지·인자에서 시크릿 패턴을 마스킹."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in SENSITIVE_PATTERNS:
            msg = pattern.sub(lambda m: f"{m.group(1)[:8]}***" if m.lastindex else "***", msg)
        record.msg = msg
        record.args = ()
        return True


def setup_logging(
    *,
    level: str | int | None = None,
    json_format: bool = False,
) -> None:
    """프로세스 전체 로깅 설정 (1회 호출).

    Args:
        level: 로그 레벨. 미지정 시 LOG_LEVEL 환경변수 또는 INFO.
        json_format: True면 JSON 라인 형식 (운영 환경 권장).
    """
    log_level = level or os.getenv("LOG_LEVEL", "INFO")

    fmt = (
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        if not json_format
        else '{"ts":"%(asctime)s","lvl":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(SecretMaskingFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)

    # 외부 라이브러리 노이즈 줄이기
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """모듈 표준 로거 획득. `__name__` 전달 권장."""
    return logging.getLogger(name)
