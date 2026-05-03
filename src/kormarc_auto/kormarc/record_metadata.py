"""갈래 A Cycle 8 (P12) — KORMARC 레코드 메타 부착.

목적:
- 레코드 생성 시 model_string·timestamp·input_hash·deterministic_seed 자동 부착
- 결정론 검증·재생성 비교·향후 진단 가능
- provenance.py (588 stamp) 와 분리: 본 모듈 = record-level metadata dict

헌법 §9: 동일 입력 = 동일 출력 보장.
"""

from __future__ import annotations

from typing import Any

from kormarc_auto.llm.deterministic import (
    DeterministicCallParams,
    compute_input_hash,
    get_pinned_model,
    utc_timestamp,
)


def build_record_metadata(
    *,
    input_payload: Any,
    tier: str = "sonnet",
    deterministic_seed: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """KORMARC 레코드 생성 시 부착할 metadata dict.

    Args:
        input_payload: ISBN·book_data dict 등 입력 (hash 계산 대상)
        tier: haiku/sonnet/opus
        deterministic_seed: 향후 Anthropic seed 지원 시 사용
        extra: 추가 메타 (e.g. operator·session_id)

    Returns:
        record metadata dict (KORMARC 588 + audit log + diff 비교용)
    """
    meta: dict[str, Any] = {
        "model_string": get_pinned_model(tier),
        "generation_timestamp": utc_timestamp(),
        "input_hash": compute_input_hash(input_payload),
        "deterministic": True,
    }
    if deterministic_seed is not None:
        meta["deterministic_seed"] = deterministic_seed
    if extra:
        meta.update(extra)
    return meta


def attach_metadata_to_record_dict(
    record_dict: dict[str, Any],
    *,
    input_payload: Any,
    call_params: DeterministicCallParams | None = None,
    tier: str = "sonnet",
) -> dict[str, Any]:
    """레코드 dict에 _meta 키로 메타 부착 (in-place·반환).

    KORMARC pymarc.Record 변환 전 dict 단계에서 호출.
    """
    if call_params is not None:
        meta = call_params.attach_record_metadata(input_payload)
    else:
        meta = build_record_metadata(input_payload=input_payload, tier=tier)
    record_dict["_meta"] = meta
    return record_dict


def verify_deterministic_consistency(
    meta_a: dict[str, Any], meta_b: dict[str, Any]
) -> tuple[bool, str | None]:
    """두 메타 비교 = 동일 입력·동일 모델 시 동일성 검증.

    Returns:
        (consistent, reason) — consistent=False 시 reason
    """
    for key in ("model_string", "input_hash", "deterministic"):
        if meta_a.get(key) != meta_b.get(key):
            return False, f"{key} mismatch: {meta_a.get(key)} != {meta_b.get(key)}"
    return True, None


__all__ = [
    "attach_metadata_to_record_dict",
    "build_record_metadata",
    "verify_deterministic_consistency",
]
