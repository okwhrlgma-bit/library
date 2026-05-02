"""사서 페인 지속 발견 시스템 — Part 75 정합.

PO 비전: "사서 페인 = 매출 = 페인 발견 = 매출 발견"

12 채널 monitoring + ICE Score + 솔루션 매핑 + Mem0 학습.
Phase 1 = 수집·점수·매핑 (외부 API 통합 X·Phase 2).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

PainCategory = Literal[
    "acquisition",  # 수서
    "cataloging",  # 정리
    "processing",  # 장비·배가
    "circulation",  # 대출·반납
    "reference",  # 참고봉사
    "preservation",  # 보존·관리
    "programs",  # 행사
    "administration",  # 행정
    "system_it",  # 시스템·IT
    "facility",  # 시설
    "emotional_labor",  # 감정노동 (Part 77)
    "career",  # 경력·번아웃 (Part 76·78)
    "other",
]

PainChannel = Literal[
    "interview",  # T5 인터뷰
    "social",  # G5 소셜 (네이버 카페·디스코드)
    "academic",  # E7 학술
    "policy",  # D3·D4 정책 보고서
    "data",  # DT1 사용자 데이터
    "competitor",  # AD1 경쟁사
    "national",  # 국회·국제
    "media",  # M1 미디어
]


@dataclass(frozen=True)
class Pain:
    """발견된 사서 페인 1건."""

    description: str
    category: PainCategory
    channel: PainChannel
    source_url: str = ""
    librarian_segment: str = ""  # P1·P2 등 페르소나
    impact_minutes_per_week: int = 0  # 주당 영향 시간
    librarian_count_estimated: int = 0  # 영향 사서 수
    confidence_count: int = 1  # 검증 건수 (3+ = 진짜 페인)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(frozen=True)
class ICEScore:
    """페인 우선순위 ICE."""

    impact: int  # 1~10 (시간×사서 수)
    confidence: int  # 1~5 (검증 건수)
    ease: int  # 1~5 (구현 쉬움 L1~L4)

    @property
    def total(self) -> int:
        return self.impact * self.confidence * self.ease


def calculate_ice(pain: Pain, *, ease: int = 3) -> ICEScore:
    """페인 → ICE Score.

    Impact (1~10):
        - 시간 (1h/주=1·10h/주=10)
        - 사서 수 (1관=1·1만관=10)
    Confidence (1~5):
        - 검증 건수 (1=1건·5=5건+)
    Ease (1~5):
        - 구현 쉬움 (L1=5·L4=1)
    """
    # Impact 계산
    time_score = min(pain.impact_minutes_per_week / 60, 10)  # 시간 기준
    librarian_score = min(pain.librarian_count_estimated / 1000, 10)  # 1,000 기준
    impact = int((time_score + librarian_score) / 2)

    # Confidence
    confidence = min(pain.confidence_count, 5)

    return ICEScore(impact=max(impact, 1), confidence=confidence, ease=ease)


def prioritize(pains: list[Pain]) -> list[tuple[Pain, ICEScore]]:
    """페인 우선순위 정렬 (ICE 내림차순)."""
    scored = [(p, calculate_ice(p)) for p in pains]
    scored.sort(key=lambda x: x[1].total, reverse=True)
    return scored


class PainDiscoverySystem:
    """페인 발견·검증·매핑 자동.

    사용:
        system = PainDiscoverySystem(Path('.cache/pains'))
        system.add_pain(Pain(description='KORMARC 입력 부담', ...))
        priorities = system.report_top(n=10)
    """

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file = self.storage_dir / "pains.jsonl"

    def add_pain(self, pain: Pain) -> None:
        """페인 추가 (jsonl append)."""
        with self.file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(pain), ensure_ascii=False) + "\n")

    def all_pains(self) -> list[Pain]:
        """누적 페인 모두."""
        if not self.file.exists():
            return []
        pains = []
        with self.file.open(encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    pains.append(Pain(**data))
                except (json.JSONDecodeError, TypeError):
                    continue
        return pains

    def report_top(self, *, n: int = 10) -> list[tuple[Pain, ICEScore]]:
        """ICE Top N 페인 보고."""
        return prioritize(self.all_pains())[:n]

    def report_by_category(self, category: PainCategory) -> list[Pain]:
        """카테고리별 페인."""
        return [p for p in self.all_pains() if p.category == category]


__all__ = [
    "ICEScore",
    "Pain",
    "PainCategory",
    "PainChannel",
    "PainDiscoverySystem",
    "calculate_ice",
    "prioritize",
]
