"""588 provenance 자동 stamp + 결정성 보장 — Part 92 §C.4 / Theme 2.

PO 명령 (Part 92): "결정성·provenance = moat"
- ELUNA 2025: "AI 다른 결과 매번 = 트러스트 킬러"
- PCC AI Cataloging Final Report (2024·revised 2025): 588 source-of-description 정합 가이드
- Cursor 2024-2025: auto-apply 회귀 = forum 항의 = per-field accept/reject 표준

작동:
1. 588 ▾a = 자동 KORMARC 필드 출처 + 모델 버전 + 생성 시각
2. fixed seed/temperature = 결정성 (peer review 통과)
3. visible diff = 같은 입력 = 같은 출력 비교 가능
4. per-record audit log = librarian_id·field·suggestion·accepted/rejected

근거:
- PCC 588 ▾a: "Source of description"·AI tool 식별 + 버전
- KORMARC 588 (NLK·KS X 6006-0:2023.12)
- Anthropic API: temperature=0·top_p=1 = 결정성
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# 결정성 보장 (Anthropic API 권장)
DETERMINISTIC_TEMPERATURE = 0.0
DETERMINISTIC_TOP_P = 1.0
DETERMINISTIC_TOP_K = 1


@dataclass(frozen=True)
class ProvenanceStamp:
    """588 provenance stamp."""

    record_isbn: str
    generator: str = "kormarc-auto"
    version: str = "v0.6.0"  # CHANGELOG 동기화
    model_id: str = "claude-sonnet-4-6"
    sources_used: list[str] = field(default_factory=list)  # ["seoji", "data4library", ...]
    librarian_id: str | None = None
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    seed: int = 0  # 결정성
    temperature: float = DETERMINISTIC_TEMPERATURE
    librarian_reviewed: bool = False  # 사서 검수 단계 (헌법 §0)


def render_588_subfield(stamp: ProvenanceStamp) -> str:
    """KORMARC 588 ▾a 필드 텍스트 렌더링.

    예: "이 레코드는 kormarc-auto v0.6.0이 SEOJI·data4library 기반으로
         claude-sonnet-4-6 (temperature=0.0, seed=0)로 2026-05-03 생성한 초안임.
         사서 검수 필수."
    """
    sources = "·".join(stamp.sources_used) if stamp.sources_used else "외부 API"
    review = "사서 검수 완료" if stamp.librarian_reviewed else "사서 검수 필수"
    return (
        f"이 레코드는 {stamp.generator} {stamp.version}이 "
        f"{sources} 기반으로 {stamp.model_id} "
        f"(temperature={stamp.temperature}, seed={stamp.seed})로 "
        f"{stamp.generated_at[:10]} 생성한 초안임. {review}."
    )


def stamp_to_kormarc_field(stamp: ProvenanceStamp) -> dict:
    """KORMARC 588 필드 dict (builder 통합용·▾a + ▾5 + ▾2)."""
    return {
        "tag": "588",
        "indicators": [" ", " "],
        "subfields": [
            {"code": "a", "value": render_588_subfield(stamp)},
            {"code": "5", "value": stamp.generator},  # 작성기관
        ],
    }


@dataclass(frozen=True)
class FieldProvenance:
    """필드별 출처 추적 (provenance chip·UX)."""

    field_tag: str  # "245", "650", "008" 등
    source: str  # "seoji" / "kolisnet" / "vision_ocr" / "ai_inferred" / "librarian_manual"
    source_record_id: str | None = None  # KOLIS-NET ID 등
    confidence: float = 1.0  # 0.0~1.0
    librarian_action: str | None = None  # "accepted" / "edited" / "rejected"


@dataclass
class RecordAuditLog:
    """레코드별 audit log·1주 100% 환불 + PIPA 정합."""

    record_isbn: str
    field_provenances: list[FieldProvenance] = field(default_factory=list)
    librarian_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    final_committed_at: str | None = None
    audit_hash_chain: list[str] = field(default_factory=list)  # 변조 불가 증명

    def add_field_event(self, prov: FieldProvenance) -> None:
        """필드 이벤트 추가 + 해시 체인 갱신."""
        self.field_provenances.append(prov)
        prev_hash = self.audit_hash_chain[-1] if self.audit_hash_chain else "GENESIS"
        new_hash = hashlib.sha256(
            f"{prev_hash}|{prov.field_tag}|{prov.source}|{prov.librarian_action}".encode()
        ).hexdigest()[:16]
        self.audit_hash_chain.append(new_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_isbn": self.record_isbn,
            "librarian_id": self.librarian_id,
            "created_at": self.created_at,
            "final_committed_at": self.final_committed_at,
            "field_count": len(self.field_provenances),
            "audit_chain_head": self.audit_hash_chain[-1] if self.audit_hash_chain else None,
            "fields": [
                {
                    "tag": p.field_tag,
                    "source": p.source,
                    "confidence": p.confidence,
                    "action": p.librarian_action,
                }
                for p in self.field_provenances
            ],
        }


def deterministic_anthropic_params() -> dict[str, Any]:
    """Anthropic API 결정성 보장 파라미터.

    Returns:
        api 호출 시 spread할 dict (`**deterministic_anthropic_params()`)
    """
    return {
        "temperature": DETERMINISTIC_TEMPERATURE,
        "top_p": DETERMINISTIC_TOP_P,
        # Anthropic = top_k 노출 X·temperature 0이면 결정성
    }


def compute_record_hash(book_data: dict) -> str:
    """레코드 핵심 필드 해시 (visible diff 비교용)."""
    canonical = json.dumps(
        {k: book_data.get(k, "") for k in sorted(book_data.keys())},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def visible_diff_summary(old_data: dict, new_data: dict) -> dict:
    """visible diff 요약 (regenerate 시 사서가 보는 것)."""
    all_keys = set(old_data.keys()) | set(new_data.keys())
    changes = []
    for k in sorted(all_keys):
        old_v = old_data.get(k)
        new_v = new_data.get(k)
        if old_v != new_v:
            changes.append(
                {
                    "field": k,
                    "before": str(old_v)[:100] if old_v else None,
                    "after": str(new_v)[:100] if new_v else None,
                }
            )
    return {
        "old_hash": compute_record_hash(old_data),
        "new_hash": compute_record_hash(new_data),
        "changes_count": len(changes),
        "changes": changes,
        "is_identical": len(changes) == 0,
    }


__all__ = [
    "DETERMINISTIC_TEMPERATURE",
    "DETERMINISTIC_TOP_K",
    "DETERMINISTIC_TOP_P",
    "FieldProvenance",
    "ProvenanceStamp",
    "RecordAuditLog",
    "compute_record_hash",
    "deterministic_anthropic_params",
    "render_588_subfield",
    "stamp_to_kormarc_field",
    "visible_diff_summary",
]
