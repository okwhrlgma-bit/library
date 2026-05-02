"""자관 지식 베이스 (Library Knowledge Base) — Part 73 (P14 야간 사서) 정합.

사서 페인 (Part 73·76·80):
- 야간 사서 = 2년 교체 = 인수인계 자료 X
- 자관 정보 (prefix·청구기호·정책) 추정 작업
- 5년 못 버티는 구조 = 노하우 휘발

해결: 사서 결정·노하우 = 자동 누적 (Mem0 통합 ADR-0071) + 다음 사서 자동 학습.

Phase 1 = JSON 파일 기반 (의존성 X).
Phase 2 = Mem0 통합 (pg_vector·embedding).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class LibraryDecision:
    """사서 결정 1건 (자관 노하우 누적)."""

    sasagwan: str
    decision_type: str  # "prefix·classification·call_number·policy·response"
    context: str  # 결정 배경
    decision: str  # 실제 결정
    reason: str = ""  # 왜
    librarian_name: str = ""  # 누가
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class LibraryKnowledgeBase:
    """자관 지식 베이스 (Mem0 통합 전 단계).

    사용:
        kb = LibraryKnowledgeBase(Path(".cache/kormarc-auto/kb"))
        kb.learn(LibraryDecision(...))
        results = kb.query("EQ vs CQ prefix")
    """

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, sasagwan: str) -> Path:
        safe = sasagwan.replace("/", "_").replace(" ", "_")
        return self.storage_dir / f"{safe}.jsonl"

    def learn(self, decision: LibraryDecision) -> None:
        """사서 결정 누적 (jsonl append)."""
        path = self._file_path(decision.sasagwan)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(decision), ensure_ascii=False) + "\n")

    def query(self, sasagwan: str, keyword: str, *, limit: int = 5) -> list[LibraryDecision]:
        """자관 결정 검색 (단순 키워드 매칭·Phase 1).

        Phase 2 = Mem0 vector embedding (pg_vector).
        """
        path = self._file_path(sasagwan)
        if not path.exists():
            return []

        results = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                # 단순 매칭 (Phase 1)
                searchable = f"{data.get('context','')} {data.get('decision','')} {data.get('reason','')}"
                if keyword.lower() in searchable.lower():
                    results.append(LibraryDecision(**data))

        return results[:limit]

    def export_handover(self, sasagwan: str) -> str:
        """다음 사서 인수인계 markdown 자동 생성 (P14·P15 정합)."""
        path = self._file_path(sasagwan)
        if not path.exists():
            return f"# {sasagwan} 자관 인수인계\n\n(누적 데이터 없음)\n"

        decisions: list[LibraryDecision] = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    decisions.append(LibraryDecision(**json.loads(line.strip())))
                except json.JSONDecodeError:
                    continue

        # 카테고리별 그룹화
        by_type: dict[str, list[LibraryDecision]] = {}
        for d in decisions:
            by_type.setdefault(d.decision_type, []).append(d)

        lines = [
            f"# {sasagwan} 자관 인수인계 매뉴얼",
            "",
            "> kormarc-auto 자동 생성 (이전 사서 결정·노하우 누적)",
            f"> 누적 결정 {len(decisions)}건",
            "",
            "## 다음 선생님께",
            "",
            "이 도서관에서 일하던 선생님들이 만든 결정·노하우를 자동 정리했어요.",
            "선생님께서 새로 결정하실 때 참고하시고, 본인 결정도 자동 누적되어 다음 분께 전달됩니다.",
            "",
        ]

        for dtype, items in by_type.items():
            lines.append(f"## {_type_korean(dtype)} ({len(items)}건)")
            lines.append("")
            for item in items[:20]:  # 카테고리당 상위 20건
                lines.append(f"### {item.context or '(컨텍스트 없음)'}")
                lines.append(f"- **결정**: {item.decision}")
                if item.reason:
                    lines.append(f"- **이유**: {item.reason}")
                if item.librarian_name:
                    lines.append(f"- 결정 사서: {item.librarian_name} 선생님")
                lines.append(f"- 시점: {item.timestamp[:10]}")
                lines.append("")

        return "\n".join(lines)


def _type_korean(decision_type: str) -> str:
    mapping = {
        "prefix": "자관 등록번호 prefix 룰",
        "classification": "분류 (KDC) 결정",
        "call_number": "청구기호 패턴",
        "policy": "자관 운영 정책",
        "response": "이용자 응대 노하우",
    }
    return mapping.get(decision_type, decision_type)


__all__ = ["LibraryDecision", "LibraryKnowledgeBase"]
