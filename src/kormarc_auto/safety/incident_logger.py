"""감정노동 사건 기록·보호 시스템 — Part 77 정합.

사서 페인 (Part 77):
- 공공도서관 사서 67.9% 폭언 경험 (서울시·2020)
- 14.9% 성희롱·성추행 경험
- 감정노동 → 직무 스트레스 → 5년 못 버티는 구조

해결: 사건 자동 기록·해시 체인·법적 증거 + 관장·자치구 자동 보고.
서울시 7대 지침 정합.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

INCIDENT_TYPES = Literal[
    "verbal_abuse",      # 폭언
    "sexual_harassment", # 성희롱
    "physical_threat",   # 물리적 위협
    "complaint",         # 일반 민원
    "other",
]


@dataclass(frozen=True)
class Incident:
    """감정노동 사건 1건."""

    sasagwan: str
    librarian_name: str
    incident_type: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence: str = ""  # 채팅·녹음·증거 링크
    severity: int = 1  # 1 (경미) ~ 5 (심각)
    previous_hash: str = ""  # 해시 체인


class IncidentLogger:
    """감정노동 사건 기록 (해시 체인·법적 증거).

    PIPA Q5 audit_log 정합 + 서울시 7대 지침 정합.
    """

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, sasagwan: str) -> Path:
        safe = sasagwan.replace("/", "_").replace(" ", "_")
        return self.storage_dir / f"incidents_{safe}.jsonl"

    def _last_hash(self, path: Path) -> str:
        if not path.exists():
            return ""
        with path.open(encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return ""
        try:
            last = json.loads(lines[-1].strip())
            return _compute_hash(last)
        except (json.JSONDecodeError, KeyError):
            return ""

    def log(self, incident: Incident) -> str:
        """사건 기록 (해시 체인 자동)."""
        path = self._file_path(incident.sasagwan)
        previous = self._last_hash(path)
        sealed = Incident(
            sasagwan=incident.sasagwan,
            librarian_name=incident.librarian_name,
            incident_type=incident.incident_type,
            description=incident.description,
            timestamp=incident.timestamp,
            evidence=incident.evidence,
            severity=incident.severity,
            previous_hash=previous,
        )
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(sealed), ensure_ascii=False) + "\n")
        return _compute_hash(asdict(sealed))

    def quarterly_summary(self, sasagwan: str, year: int, quarter: int) -> dict:
        """분기 사건 통계 (관장·자치구 보호 보고용)."""
        path = self._file_path(sasagwan)
        if not path.exists():
            return {"total": 0}

        q_start_month = (quarter - 1) * 3 + 1
        q_end_month = q_start_month + 2

        counts: dict[str, int] = {}
        total = 0
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                ts = data.get("timestamp", "")
                if not ts:
                    continue
                yr, mo = int(ts[:4]), int(ts[5:7])
                if yr != year or not (q_start_month <= mo <= q_end_month):
                    continue
                total += 1
                counts[data["incident_type"]] = counts.get(data["incident_type"], 0) + 1

        return {
            "sasagwan": sasagwan,
            "year": year,
            "quarter": quarter,
            "total": total,
            "by_type": counts,
            "verbal_abuse_rate": int(counts.get("verbal_abuse", 0) / max(total, 1) * 100),
        }


def _compute_hash(data: dict) -> str:
    """해시 체인 (감사 trail·법적 증거)."""
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def detect_abuse(text: str) -> dict | None:
    """폭언·성희롱 자동 감지 (Phase 1·키워드 기반).

    Phase 2 = AI 분류 (T2 + AI1).
    """
    abuse_keywords = ["씨발", "꺼져", "닥쳐", "병신", "미친", "개새끼"]
    harassment_keywords = ["성", "몸매", "이쁘", "예쁘", "만나자"]

    text_lower = text.lower()
    if any(kw in text_lower for kw in abuse_keywords):
        return {"detected": True, "type": "verbal_abuse"}
    if any(kw in text_lower for kw in harassment_keywords):
        return {"detected": True, "type": "sexual_harassment", "warning": "AI 검토 필요"}
    return None


__all__ = ["Incident", "IncidentLogger", "detect_abuse"]
