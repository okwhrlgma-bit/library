"""정확도 disaggregation — Part 92 (PO dossier 핵심).

PO 명령 (Part 92): "99.82% 단일 number = 불가검증·peer review 미통과"
근거:
- SemEval-2025 Task 5 LLMs4Subjects (arXiv 2504.07199): F1@5 < 0.35 (subject)
- Korean BERT-NLSH 2023 (KCI ART002961357): micro-F1 0.6059
- Yang & Zhang 2025 (PeerJ): F1 0.7920 (cover-driven classification)

→ MARC block별 분리 측정·각 ranges 명시.

블록:
- descriptive (0XX-3XX): ISBN-grounded·SEOJI 매칭·90~99%+ 가능
- subject (6XX): KDC·NLSH·LCSH·MeSH·F1 0.35~0.79
- added entries (7XX): 부출표목·중간
- full-record: 모든 필드 100% 일치 = 사실상 X
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MarcBlock = Literal[
    "descriptive",  # 0XX-3XX (008·020·245·250·260/264·300)
    "subject",  # 6XX (650·600·651·655)
    "added_entries",  # 7XX (700·710·730)
    "local",  # 8XX·9XX (자관 prefix·청구기호)
    "full_record",  # 모든 필드 일치 (가장 어려움)
]


# 블록별 현실적 범위 (peer-reviewed 학술 결과 기반)
REALISTIC_RANGES: dict[MarcBlock, dict] = {
    "descriptive": {
        "min_pct": 90.0,
        "max_pct": 99.5,
        "typical_pct": 97.0,
        "evidence": "SEOJI/KOLIS-NET 매칭·ISBN 정확도·EAN-13 체크",
        "anchor_papers": ["Aycock 2025", "Hartshorne 2025"],
    },
    "subject": {
        "min_pct": 35.0,
        "max_pct": 79.0,
        "typical_pct": 60.0,
        "evidence": "F1·LLMs4Subjects 0.35·BERT-NLSH 0.61·Yang&Zhang 0.79",
        "anchor_papers": [
            "SemEval-2025 LLMs4Subjects (arXiv 2504.07199)",
            "BERT-NLSH 2023 (KCI ART002961357)",
            "Yang & Zhang 2025 (PeerJ)",
        ],
    },
    "added_entries": {
        "min_pct": 60.0,
        "max_pct": 92.0,
        "typical_pct": 80.0,
        "evidence": "전거 통제·동명이인·100/700 매칭",
        "anchor_papers": ["MDPI Publications 14:1:19"],
    },
    "local": {
        "min_pct": 40.0,
        "max_pct": 99.5,
        "typical_pct": 70.0,
        "evidence": "자관 정책 의존·prefix-discover 적용 후 ↑",
        "anchor_papers": ["Part 87 §2.1"],
    },
    "full_record": {
        "min_pct": 30.0,
        "max_pct": 70.0,
        "typical_pct": 50.0,
        "evidence": "모든 필드 100% 일치·사서 검수 단계 보존 권장",
        "anchor_papers": ["PCC AI Cataloging Final Report 2025"],
    },
}


@dataclass(frozen=True)
class BlockAccuracy:
    """1 블록 정확도 측정."""

    block: MarcBlock
    samples_total: int
    samples_matched: int
    accuracy_pct: float
    field_breakdown: dict[str, float] = field(default_factory=dict)  # tag → pct
    notes: str = ""


@dataclass(frozen=True)
class DisaggregatedReport:
    """전체 disaggregated 정확도 보고서."""

    eval_corpus_id: str
    sample_size: int
    library_count: int
    by_block: dict[MarcBlock, BlockAccuracy]
    headline_warning: str
    timestamp: str = ""


def calculate_block_accuracy(
    block: MarcBlock,
    samples_total: int,
    samples_matched: int,
    field_breakdown: dict[str, float] | None = None,
) -> BlockAccuracy:
    """블록 정확도 계산."""
    pct = (samples_matched / samples_total * 100) if samples_total > 0 else 0.0
    return BlockAccuracy(
        block=block,
        samples_total=samples_total,
        samples_matched=samples_matched,
        accuracy_pct=round(pct, 2),
        field_breakdown=field_breakdown or {},
        notes=REALISTIC_RANGES[block]["evidence"],
    )


def is_in_realistic_range(block: BlockAccuracy) -> bool:
    """측정값이 학술 ranges 내인지 (peer review 통과 가능 여부)."""
    rng = REALISTIC_RANGES[block.block]
    return rng["min_pct"] <= block.accuracy_pct <= rng["max_pct"]


def build_disaggregated_report(
    eval_corpus_id: str,
    by_block: dict[MarcBlock, BlockAccuracy],
    library_count: int = 1,
) -> DisaggregatedReport:
    """전체 보고서 빌드."""
    from datetime import UTC, datetime

    sample_size = sum(b.samples_total for b in by_block.values())

    # Headline warning: 99%+ single number 불가
    if any(b.accuracy_pct >= 99.0 for b in by_block.values() if b.block == "full_record"):
        warning = "⚠ full_record 99%+ = 학술 ranges 초과·peer review 미통과 위험"
    elif library_count == 1:
        warning = "⚠ PILOT 자관 1관 한정·cross-library 검증 필요"
    else:
        warning = ""

    return DisaggregatedReport(
        eval_corpus_id=eval_corpus_id,
        sample_size=sample_size,
        library_count=library_count,
        by_block=by_block,
        headline_warning=warning,
        timestamp=datetime.now(UTC).isoformat(),
    )


def render_marketing_safe_summary(report: DisaggregatedReport) -> str:
    """영업 자료용 안전 표현 (단일 % 단정 X)."""
    lines = [f"# 정확도 보고서 ({report.eval_corpus_id})"]
    lines.append(f"표본: {report.sample_size:,}건 / 자관 {report.library_count}곳")
    if report.headline_warning:
        lines.append(f"\n{report.headline_warning}\n")

    lines.append("\n## MARC block별 정확도\n")
    for blk, acc in report.by_block.items():
        rng = REALISTIC_RANGES[blk]
        in_range = is_in_realistic_range(acc)
        marker = "✅" if in_range else "⚠"
        lines.append(
            f"- **{blk}** {marker}: {acc.accuracy_pct}% "
            f"(학술 범위 {rng['min_pct']}~{rng['max_pct']}%·근거: {rng['evidence']})"
        )

    lines.append("\n## 인용 가능 학술 출처\n")
    cited = set()
    for blk in report.by_block:
        for paper in REALISTIC_RANGES[blk]["anchor_papers"]:
            cited.add(paper)
    for paper in sorted(cited):
        lines.append(f"- {paper}")

    return "\n".join(lines)


__all__ = [
    "REALISTIC_RANGES",
    "BlockAccuracy",
    "DisaggregatedReport",
    "MarcBlock",
    "build_disaggregated_report",
    "calculate_block_accuracy",
    "is_in_realistic_range",
    "render_marketing_safe_summary",
]
