"""갈래 A Cycle 8 (P12·T4-1) — 결정론적 LLM 호출 미들웨어.

목표:
- 모든 Anthropic API 호출 = temperature=0.0·top_p=1.0 강제
- 모델 string pinning (.env: ANTHROPIC_MODEL_HAIKU·SONNET·OPUS)
- 호출 메타 자동 부착 (model·timestamp·input_hash)
- 모델 변경 시 ADR 필수 (CLAUDE.md 헌법 §9)

헌법 정합:
- §9 동일 입력 = 동일 출력 보장 (모델 pinning + temperature=0)
- §3 외부 API timeout 10s
- ADR 0028 결정론적 재생성

기존 provenance.py와 분리: provenance = 588 stamp + audit·deterministic = call-time 강제.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# 결정성 상수 (변경 = ADR 필수)
DETERMINISTIC_TEMPERATURE: float = 0.0
DETERMINISTIC_TOP_P: float = 1.0

# 기본 모델 pinning (ENV override 가능)
DEFAULT_MODEL_HAIKU = "claude-haiku-4-5-20251001"
DEFAULT_MODEL_SONNET = "claude-sonnet-4-6"
DEFAULT_MODEL_OPUS = "claude-opus-4-7"


def get_pinned_model(tier: str = "sonnet") -> str:
    """ENV에서 pinned 모델 string 반환·없으면 default."""
    env_map = {
        "haiku": ("ANTHROPIC_MODEL_HAIKU", DEFAULT_MODEL_HAIKU),
        "sonnet": ("ANTHROPIC_MODEL_SONNET", DEFAULT_MODEL_SONNET),
        "opus": ("ANTHROPIC_MODEL_OPUS", DEFAULT_MODEL_OPUS),
    }
    env_key, default = env_map.get(tier.lower(), env_map["sonnet"])
    return os.getenv(env_key, default)


def compute_input_hash(payload: Any) -> str:
    """입력 payload SHA-256 hash (결정론 검증용·역산 X)."""
    if isinstance(payload, dict):
        # 키 정렬·일관 직렬화
        import json

        normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    elif isinstance(payload, str):
        normalized = payload
    else:
        normalized = str(payload)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def utc_timestamp() -> str:
    """ISO 8601 UTC (Z suffix)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class DeterministicCallParams:
    """LLM 호출 파라미터 + 메타 (record metadata 부착용)."""

    model: str
    temperature: float = DETERMINISTIC_TEMPERATURE
    top_p: float = DETERMINISTIC_TOP_P
    timeout_seconds: int = 10  # 헌법 §3
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_anthropic_kwargs(self) -> dict[str, Any]:
        """Anthropic SDK messages.create() kwargs."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "timeout": self.timeout_seconds,
        }

    def attach_record_metadata(self, input_payload: Any) -> dict[str, Any]:
        """레코드 생성 시 부착할 메타 dict."""
        return {
            "model_string": self.model,
            "generation_timestamp": utc_timestamp(),
            "input_hash": compute_input_hash(input_payload),
            "deterministic": True,
            "temperature": self.temperature,
            "top_p": self.top_p,
            **self.metadata,
        }


def make_deterministic_call(
    *,
    tier: str = "sonnet",
    extra_metadata: dict[str, Any] | None = None,
) -> DeterministicCallParams:
    """결정론 LLM 호출 파라미터 빌더 (모든 진입점이 사용)."""
    return DeterministicCallParams(
        model=get_pinned_model(tier),
        metadata=extra_metadata or {},
    )


def assert_deterministic_kwargs(kwargs: dict[str, Any]) -> None:
    """LLM 호출 직전 assertion (CI·hook 검증용·temperature·top_p 위반 즉시 차단)."""
    temp = kwargs.get("temperature", DETERMINISTIC_TEMPERATURE)
    top_p = kwargs.get("top_p", DETERMINISTIC_TOP_P)
    if temp != DETERMINISTIC_TEMPERATURE:
        raise ValueError(f"헌법 §9 위반: temperature={temp} (요구={DETERMINISTIC_TEMPERATURE})")
    if top_p != DETERMINISTIC_TOP_P:
        raise ValueError(f"헌법 §9 위반: top_p={top_p} (요구={DETERMINISTIC_TOP_P})")


__all__ = [
    "DEFAULT_MODEL_HAIKU",
    "DEFAULT_MODEL_OPUS",
    "DEFAULT_MODEL_SONNET",
    "DETERMINISTIC_TEMPERATURE",
    "DETERMINISTIC_TOP_P",
    "DeterministicCallParams",
    "assert_deterministic_kwargs",
    "compute_input_hash",
    "get_pinned_model",
    "make_deterministic_call",
    "utc_timestamp",
]
