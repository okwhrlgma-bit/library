"""갈래 A Cycle 10 (P14·T4-3) — 필드별 status·confidence·provenance.

목표:
- AI 생성 필드 = ghost text 표시 (Streamlit·UI 미들웨어)
- 사서 명시적 accept/reject/edit 필요
- per-field status 전이 = ai_generated → accepted / rejected / edited
- API 응답 = field-level status + confidence + provenance
- PATCH /marc-record/{id}/field/{tag} = 멱등성 보장

헌법 §4 정합 ("100% 자동" 카피 금지·사서 검토 단계 보존).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

FieldStatus = Literal["ai_generated", "accepted", "rejected", "edited", "pending"]
ConfidenceLevel = Literal["확실", "검토 필요", "불확실"]


VALID_TRANSITIONS: dict[FieldStatus, set[FieldStatus]] = {
    "pending": {"ai_generated", "accepted", "rejected", "edited"},
    "ai_generated": {"accepted", "rejected", "edited"},
    "accepted": {"edited", "rejected"},  # 사서가 마음 바꿔도 OK
    "rejected": {"edited", "ai_generated"},  # 재생성 시 ai_generated로 복귀
    "edited": {"accepted", "rejected"},  # edit 후 다시 accept/reject
}


def can_transition(current: FieldStatus, target: FieldStatus) -> bool:
    """status 전이 가능 여부 (멱등성 보장)."""
    if current == target:
        return True  # idempotent
    return target in VALID_TRANSITIONS.get(current, set())


@dataclass
class FieldState:
    """필드별 상태 + 신뢰도 + 출처."""

    tag: str  # "245", "650", "008" 등
    value: str
    status: FieldStatus = "ai_generated"
    confidence: ConfidenceLevel = "검토 필요"
    provenance: dict[str, Any] = field(default_factory=dict)
    last_updated: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def transition(self, new_status: FieldStatus, *, new_value: str | None = None) -> bool:
        """status 전이·전이 불가 시 False·성공 시 True."""
        if not can_transition(self.status, new_status):
            return False
        self.status = new_status
        if new_value is not None:
            self.value = new_value
        self.last_updated = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return True

    def to_api_dict(self) -> dict[str, Any]:
        """API 응답 형식 (UI ghost text 분기용)."""
        return {
            "tag": self.tag,
            "value": self.value,
            "status": self.status,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "last_updated": self.last_updated,
            "ui_hint": _ui_hint_for(self.status, self.confidence),
        }


def _ui_hint_for(status: FieldStatus, confidence: ConfidenceLevel) -> dict[str, str]:
    """UI 렌더링 힌트 (Streamlit·Web)."""
    if status == "ai_generated":
        # ghost text 표시·italic·회색
        color = {"확실": "gray-500", "검토 필요": "amber-600", "불확실": "red-600"}.get(
            confidence, "amber-600"
        )
        return {"style": "italic gray", "color": color, "icon": "ⓘ"}
    if status == "accepted":
        return {"style": "normal black", "color": "green-700", "icon": "✓"}
    if status == "rejected":
        return {"style": "strikethrough gray", "color": "gray-400", "icon": "✗"}
    if status == "edited":
        return {"style": "normal black underline", "color": "blue-700", "icon": "✎"}
    return {"style": "italic gray", "color": "gray-500", "icon": "?"}


@dataclass
class RecordReviewState:
    """레코드 단위 검토 진행률 + 필드별 상태."""

    record_id: str
    fields: list[FieldState] = field(default_factory=list)

    def add_field(self, fs: FieldState) -> None:
        self.fields.append(fs)

    def progress(self) -> dict[str, int]:
        """검토 진행률 카운트."""
        counts = {
            "total": len(self.fields),
            "ai_generated": 0,
            "accepted": 0,
            "rejected": 0,
            "edited": 0,
            "pending": 0,
        }
        for fs in self.fields:
            counts[fs.status] = counts.get(fs.status, 0) + 1
        counts["reviewed"] = counts["accepted"] + counts["rejected"] + counts["edited"]
        return counts

    def is_fully_reviewed(self) -> bool:
        return all(fs.status in ("accepted", "rejected", "edited") for fs in self.fields)

    def reject_all(self) -> int:
        """전체 거부 (escape hatch). 변경된 필드 수 반환."""
        changed = 0
        for fs in self.fields:
            if fs.transition("rejected"):
                changed += 1
        return changed

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "fields": [fs.to_api_dict() for fs in self.fields],
            "progress": self.progress(),
            "fully_reviewed": self.is_fully_reviewed(),
        }


__all__ = [
    "VALID_TRANSITIONS",
    "ConfidenceLevel",
    "FieldState",
    "FieldStatus",
    "RecordReviewState",
    "can_transition",
]
