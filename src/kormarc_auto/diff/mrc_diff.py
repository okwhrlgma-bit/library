"""갈래 A Cycle 14A (P16) — KORMARC 레코드 subfield 단위 diff.

원칙:
- subfield 단위 비교 (245$a·650$2 등)
- 추가 (+)·삭제 (-)·변경 (~) 3 타입
- 결정론 (ADR 0028) 정합 = 동일 입력 + 모델 = empty diff (게이트)
- UI modal·CLI --show-diff·API JSON 응답 형식 통일

input = pymarc.Record 또는 dict (tag·indicators·subfields).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

DiffType = Literal["added", "removed", "changed"]


@dataclass(frozen=True)
class DiffEntry:
    """필드별 diff entry (UI 줄 단위)."""

    diff_type: DiffType
    field_tag: str  # "245"
    subfield_code: str | None = None  # "a" / None = 전체 필드 변경
    before: str | None = None
    after: str | None = None

    def to_text(self, *, color: bool = False) -> str:
        """UI 텍스트 한 줄 (red/green/yellow color hint)."""
        prefix = {"added": "+", "removed": "-", "changed": "~"}[self.diff_type]
        sf = f"${self.subfield_code}" if self.subfield_code else ""
        if self.diff_type == "added":
            return f"{prefix} {self.field_tag}{sf} {self.after}"
        if self.diff_type == "removed":
            return f"{prefix} {self.field_tag}{sf} {self.before}"
        return f"{prefix} {self.field_tag}{sf} {self.before} → {self.after}"


@dataclass
class DiffSummary:
    """diff 결과 요약."""

    entries: list[DiffEntry] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return sum(1 for e in self.entries if e.diff_type == "added")

    @property
    def removed_count(self) -> int:
        return sum(1 for e in self.entries if e.diff_type == "removed")

    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.diff_type == "changed")

    @property
    def total_changes(self) -> int:
        return len(self.entries)

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "total_changes": self.total_changes,
            "added": self.added_count,
            "removed": self.removed_count,
            "changed": self.changed_count,
            "is_empty": self.total_changes == 0,
            "entries": [
                {
                    "type": e.diff_type,
                    "field_tag": e.field_tag,
                    "subfield_code": e.subfield_code,
                    "before": e.before,
                    "after": e.after,
                }
                for e in self.entries
            ],
        }


def _record_to_normalized_dict(rec: Any) -> dict[str, list[tuple[str | None, str]]]:
    """pymarc.Record 또는 dict → {tag: [(subfield_code, value), ...]}.

    제어 필드(00X) = subfield_code = None·data 그대로.
    """
    out: dict[str, list[tuple[str | None, str]]] = {}

    # pymarc.Record 추론
    if hasattr(rec, "fields"):
        for f in rec.fields:
            tag = f.tag
            if hasattr(f, "is_control_field") and f.is_control_field():
                out.setdefault(tag, []).append((None, (f.data or "").strip()))
            else:
                items: list[tuple[str | None, str]] = []
                for sf in f.subfields:
                    items.append((sf.code, (sf.value or "").strip()))
                out.setdefault(tag, []).extend(items)
        return out

    # dict 형식
    if isinstance(rec, dict) and "fields" in rec:
        for f in rec["fields"]:
            tag = f.get("tag", "")
            if "data" in f:  # control field
                out.setdefault(tag, []).append((None, (f.get("data") or "").strip()))
            else:
                for sf in f.get("subfields", []):
                    code = sf.get("code")
                    value = (sf.get("value") or "").strip()
                    out.setdefault(tag, []).append((code, value))
        return out

    return out


def diff_records(before: Any, after: Any) -> DiffSummary:
    """두 KORMARC 레코드 비교 → DiffSummary.

    subfield 단위 + tag 단위 정렬 (결정론 정합).
    """
    before_norm = _record_to_normalized_dict(before)
    after_norm = _record_to_normalized_dict(after)

    entries: list[DiffEntry] = []
    all_tags = sorted(set(before_norm.keys()) | set(after_norm.keys()))

    for tag in all_tags:
        before_subs = before_norm.get(tag, [])
        after_subs = after_norm.get(tag, [])

        # 같은 위치별 비교
        max_len = max(len(before_subs), len(after_subs))
        for i in range(max_len):
            b_pair = before_subs[i] if i < len(before_subs) else None
            a_pair = after_subs[i] if i < len(after_subs) else None

            if b_pair is None and a_pair is not None:
                entries.append(
                    DiffEntry(
                        diff_type="added",
                        field_tag=tag,
                        subfield_code=a_pair[0],
                        after=a_pair[1],
                    )
                )
            elif a_pair is None and b_pair is not None:
                entries.append(
                    DiffEntry(
                        diff_type="removed",
                        field_tag=tag,
                        subfield_code=b_pair[0],
                        before=b_pair[1],
                    )
                )
            elif b_pair != a_pair and b_pair is not None and a_pair is not None:
                entries.append(
                    DiffEntry(
                        diff_type="changed",
                        field_tag=tag,
                        subfield_code=a_pair[0],
                        before=b_pair[1],
                        after=a_pair[1],
                    )
                )

    return DiffSummary(entries=entries)


def is_empty_diff(summary: DiffSummary) -> bool:
    """결정론 정합 검증 = 동일 입력 → empty (Cycle 8 ADR 0028 정합)."""
    return summary.total_changes == 0


def format_diff_text(summary: DiffSummary, *, max_lines: int = 50) -> str:
    """CLI/email 출력용 plain text (rich 미설치 환경 호환)."""
    if is_empty_diff(summary):
        return "(변경 사항 없음 = 결정론 정합·동일 입력 동일 출력)"

    header = (
        f"=== KORMARC 변경 사항 ({summary.total_changes}건: "
        f"+{summary.added_count} -{summary.removed_count} ~{summary.changed_count}) ===\n"
    )
    lines = [e.to_text() for e in summary.entries[:max_lines]]
    body = "\n".join(lines)
    if summary.total_changes > max_lines:
        body += f"\n... ({summary.total_changes - max_lines}건 추가 생략)"
    return header + body
