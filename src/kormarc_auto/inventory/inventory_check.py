"""장서점검 (Inventory Check) — Part 80 정합.

사서 페인 (Part 80·페인 20):
- 장서점검 = 몇 주 엄청난 노동력
- RFID = 비싼 (대규모만)
- 작은·중규모 = 수동만

해결: 바코드·ISBN·자관 등록번호 일괄 자동 검증.
모바일 카메라 스캔 통합 (T1 Phase 2).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class InventoryItem:
    """장서점검 1건."""

    isbn: str
    registration_no: str
    expected_location: str = ""  # 자관 청구기호 위치
    found: bool = False
    actual_location: str = ""
    notes: str = ""


@dataclass
class InventorySession:
    """장서점검 세션 (자관·기간)."""

    sasagwan: str
    started_at: datetime = field(default_factory=datetime.now)
    items: list[InventoryItem] = field(default_factory=list)

    def mark_found(self, isbn: str, actual_location: str = "") -> bool:
        """발견 표시."""
        for i, item in enumerate(self.items):
            if item.isbn == isbn:
                self.items[i] = InventoryItem(
                    isbn=item.isbn,
                    registration_no=item.registration_no,
                    expected_location=item.expected_location,
                    found=True,
                    actual_location=actual_location or item.expected_location,
                    notes=item.notes,
                )
                return True
        return False

    def missing_items(self) -> list[InventoryItem]:
        """미발견 (분실·도난·오배가 후보)."""
        return [i for i in self.items if not i.found]

    def misplaced_items(self) -> list[InventoryItem]:
        """오배가 (위치 불일치)."""
        return [
            i for i in self.items
            if i.found and i.expected_location and i.actual_location != i.expected_location
        ]

    def summary(self) -> dict[str, int]:
        """요약 통계."""
        total = len(self.items)
        found = sum(1 for i in self.items if i.found)
        return {
            "total": total,
            "found": found,
            "missing": total - found,
            "misplaced": len(self.misplaced_items()),
            "completion_rate": int(found / total * 100) if total else 0,
        }


def load_inventory_from_csv(csv_path: Path) -> list[InventoryItem]:
    """자관 등록부 CSV → 장서점검 항목.

    CSV 헤더: ISBN,자관등록번호,청구기호
    """
    items = []
    with csv_path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(
                InventoryItem(
                    isbn=row.get("ISBN", "").replace("-", "").strip(),
                    registration_no=row.get("자관등록번호", "").strip(),
                    expected_location=row.get("청구기호", "").strip(),
                )
            )
    return items


def export_session_report(session: InventorySession, output_path: Path) -> Path:
    """장서점검 보고서 markdown 자동 생성."""
    summary = session.summary()
    lines = [
        f"# {session.sasagwan} 장서점검 보고서",
        "",
        f"> 시작: {session.started_at.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 요약",
        f"- 총 등록: {summary['total']}권",
        f"- 발견: {summary['found']}권 ({summary['completion_rate']}%)",
        f"- 미발견: {summary['missing']}권",
        f"- 오배가: {summary['misplaced']}권",
        "",
        "## 미발견 도서 (확인 필요)",
    ]
    for item in session.missing_items()[:50]:  # 상위 50건
        lines.append(f"- ISBN {item.isbn} / 등록 {item.registration_no} / 위치 {item.expected_location}")

    lines.append("")
    lines.append("## 오배가 도서")
    for item in session.misplaced_items()[:50]:
        lines.append(
            f"- ISBN {item.isbn} / 예상 {item.expected_location} → 실제 {item.actual_location}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


__all__ = [
    "InventoryItem",
    "InventorySession",
    "export_session_report",
    "load_inventory_from_csv",
]
