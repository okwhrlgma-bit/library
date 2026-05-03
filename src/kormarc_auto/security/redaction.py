"""PII 마스킹·redaction — 9-1 (로그·에러 응답 PII 누설 0).

PO 명령 (12-섹션 §9.1): "API 키·이메일·전화 로그 누설 차단"
PIPA 2026.09 시행 = 매출 10% 과징금 → redaction middleware 필수.

마스킹 패턴:
- 이메일: user@example.com → u***@e***.com
- 전화: 010-1234-5678 → 010-****-5678
- API 키: sk-ant-api03-XXX → sk-ant-***
- ISBN: 일부 보존 (앞 3 + 끝 3) (디버깅용)
- 카드: 1234-5678-9012-3456 → ****-****-****-3456

사용:
    from kormarc_auto.security.redaction import redact_text
    safe_log = redact_text(raw_log)

또는 logging filter:
    logging.getLogger().addFilter(RedactionFilter())
"""

from __future__ import annotations

import logging
import re

# 정규식 패턴 (성능 = re.compile)
EMAIL_PATTERN = re.compile(
    r"\b([a-zA-Z0-9._%+-])([a-zA-Z0-9._%+-]*)@([a-zA-Z0-9.-])([a-zA-Z0-9.-]*)\.([a-zA-Z]{2,})\b"
)
PHONE_KR_PATTERN = re.compile(r"\b(01[016-9])-?(\d{3,4})-?(\d{4})\b")
ANTHROPIC_KEY_PATTERN = re.compile(r"sk-ant-api03-[A-Za-z0-9_\-]{20,}")
KAKAO_KEY_PATTERN = re.compile(r"\bKakaoAK\s+[A-Za-z0-9]{20,}")
TTBKEY_PATTERN = re.compile(r"\bttb[a-zA-Z0-9]{15,}001\b")
CARD_PATTERN = re.compile(r"\b(\d{4})-?(\d{4})-?(\d{4})-?(\d{4})\b")
KOREAN_RRN_PATTERN = re.compile(r"\b\d{6}-?[1-4]\d{6}\b")  # 주민등록번호


def _redact_email(match: re.Match) -> str:
    user_first, user_rest, dom_first, dom_rest, tld = match.groups()
    masked_user = user_first + "*" * max(1, len(user_rest))
    masked_dom = dom_first + "*" * max(1, len(dom_rest))
    return f"{masked_user}@{masked_dom}.{tld}"


def _redact_phone(match: re.Match) -> str:
    prefix, _middle, last = match.groups()
    return f"{prefix}-****-{last}"


def _redact_card(match: re.Match) -> str:
    return f"****-****-****-{match.group(4)}"


def redact_text(text: str) -> str:
    """입력 문자열에서 PII 마스킹.

    Args:
        text: 원본 (로그·에러 메시지·응답 본문)

    Returns:
        마스킹된 문자열 (PII 0)
    """
    if not text or not isinstance(text, str):
        return text

    # API 키 (보존 우선순위 가장 높음)
    text = ANTHROPIC_KEY_PATTERN.sub("sk-ant-***REDACTED***", text)
    text = KAKAO_KEY_PATTERN.sub("KakaoAK ***REDACTED***", text)
    text = TTBKEY_PATTERN.sub("ttb***REDACTED***", text)

    # 주민등록번호 (가장 민감)
    text = KOREAN_RRN_PATTERN.sub("******-*******", text)

    # 카드 번호
    text = CARD_PATTERN.sub(_redact_card, text)

    # 이메일
    text = EMAIL_PATTERN.sub(_redact_email, text)

    # 전화 (한국)
    text = PHONE_KR_PATTERN.sub(_redact_phone, text)

    return text


class RedactionFilter(logging.Filter):
    """logging filter — 모든 로그 레코드 PII 자동 마스킹.

    사용:
        import logging
        from kormarc_auto.security.redaction import RedactionFilter
        for handler in logging.root.handlers:
            handler.addFilter(RedactionFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)
        if record.args:
            redacted_args = tuple(redact_text(a) if isinstance(a, str) else a for a in record.args)
            record.args = redacted_args
        return True


def install_redaction_globally() -> None:
    """root logger에 redaction filter 설치 (process-wide)."""
    root = logging.getLogger()
    redactor = RedactionFilter()
    for handler in root.handlers:
        handler.addFilter(redactor)
    # 신규 핸들러에도 적용
    root.addFilter(redactor)


def safe_error_response(error: Exception) -> dict[str, str]:
    """에러 응답 일관 포맷 + 자동 마스킹 (FastAPI exception handler).

    Returns:
        {"error": {"code": "...", "message": "..."}} (PII 0)
    """
    raw_message = str(error)
    return {
        "error": {
            "code": type(error).__name__,
            "message": redact_text(raw_message),
        }
    }


__all__ = [
    "ANTHROPIC_KEY_PATTERN",
    "CARD_PATTERN",
    "EMAIL_PATTERN",
    "KAKAO_KEY_PATTERN",
    "KOREAN_RRN_PATTERN",
    "PHONE_KR_PATTERN",
    "TTBKEY_PATTERN",
    "RedactionFilter",
    "install_redaction_globally",
    "redact_text",
    "safe_error_response",
]
