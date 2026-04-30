"""자관 .mrc 디렉토리 한 번에 진단 — PILOT 1주차 사서가 첫 30분 내 활용.

prefix 발견 + KORMARC 정합 검증 통합 → 한 번의 CLI로 자관 데이터 건강 진단.

영업 가치 (★ PILOT 1주차 핵심 도구):
- 사서 첫 만남에서 즉시 "귀관 .mrc 정합 N% / prefix 발견 N개" 보고
- 자관 「내를건너서 숲으로 도서관」 4-29 실측 = 99.82% 정합
- 다른 자관 PILOT 시 PrefixDiscoverer + .mrc 검증 1번에 결과
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kormarc_auto.librarian_helpers.prefix_discovery import (
    PrefixDiscoverer,
    PrefixSummary,
)


@dataclass(frozen=True)
class SanityReport:
    """자관 .mrc 디렉토리 진단 보고서."""

    directory: str
    file_count: int
    record_count: int
    valid_count: int
    issue_count: int
    integrity_pct: float
    prefix_summary: PrefixSummary
    issues_by_type: dict[str, int] = field(default_factory=dict)
    sample_issues: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        """사서 친화 텍스트 보고서 (콘솔 출력용)."""
        lines = [
            "=" * 50,
            "자관 .mrc 진단 보고서",
            "=" * 50,
            f"디렉토리   : {self.directory}",
            f"파일 수    : {self.file_count:,}건",
            f"레코드 수  : {self.record_count:,}건",
            f"정합 레코드: {self.valid_count:,}건",
            f"위반 레코드: {self.issue_count:,}건",
            f"정합률     : {self.integrity_pct:.2f}%",
            "-" * 50,
            "049 prefix 분포 (상위 5):",
        ]
        rows = sorted(
            self.prefix_summary.prefix_counts.items(), key=lambda x: -x[1]
        )[:5]
        for prefix, count in rows:
            pct = (
                count / self.prefix_summary.total_records * 100
                if self.prefix_summary.total_records else 0.0
            )
            mark = " [권장]" if prefix in self.prefix_summary.recommended_prefixes else ""
            lines.append(f"  {prefix}: {count:>5}건 ({pct:5.1f}%){mark}")

        if self.issues_by_type:
            lines.append("-" * 50)
            lines.append("위반 유형 (Top 5):")
            for kind, n in sorted(self.issues_by_type.items(), key=lambda x: -x[1])[:5]:
                lines.append(f"  - {kind}: {n}건")
        lines.append("=" * 50)
        return "\n".join(lines)


def run_sanity_check(directory: Path, *, prefix_threshold: float = 1.0) -> SanityReport:
    """자관 디렉토리 진단.

    Args:
        directory: 자관 .mrc 디렉토리 (재귀).
        prefix_threshold: prefix 권장 임계값 % (default 1.0).

    Returns:
        SanityReport.
    """
    if not directory.exists():
        empty_summary = PrefixDiscoverer(threshold_pct=prefix_threshold).scan(directory)
        return SanityReport(
            directory=str(directory),
            file_count=0,
            record_count=0,
            valid_count=0,
            issue_count=0,
            integrity_pct=0.0,
            prefix_summary=empty_summary,
        )

    discoverer = PrefixDiscoverer(threshold_pct=prefix_threshold)
    prefix_summary = discoverer.scan(directory)

    files = sorted(directory.rglob("*.mrc"))
    record_count = 0
    valid_count = 0
    issue_count = 0
    issues_by_type: dict[str, int] = {}
    samples: list[str] = []

    try:
        from pymarc import MARCReader

        from kormarc_auto.kormarc.application_level import validate_application_level
    except ImportError:
        # pymarc 미설치 — prefix 보고서만으로 반환
        return SanityReport(
            directory=str(directory),
            file_count=len(files),
            record_count=prefix_summary.total_records,
            valid_count=0,
            issue_count=0,
            integrity_pct=0.0,
            prefix_summary=prefix_summary,
        )

    for path in files:
        for record in PrefixDiscoverer._parse_any_encoding(path, MARCReader):
            record_count += 1
            present_tags = {f.tag for f in record.get_fields()}
            book_data: dict[str, Any] = {}
            issues = validate_application_level(present_tags, book_data, "book_single")
            if issues:
                issue_count += 1
                for tag, level, reason in issues:
                    kind = _categorize_issue(f"{tag} {reason}")
                    issues_by_type[kind] = issues_by_type.get(kind, 0) + 1
                    if len(samples) < 5:
                        samples.append(f"{path.name}: {tag}({level}) {reason}")
            else:
                valid_count += 1

    integrity_pct = (valid_count / record_count * 100) if record_count else 0.0

    return SanityReport(
        directory=str(directory),
        file_count=len(files),
        record_count=record_count,
        valid_count=valid_count,
        issue_count=issue_count,
        integrity_pct=integrity_pct,
        prefix_summary=prefix_summary,
        issues_by_type=issues_by_type,
        sample_issues=samples,
    )


def _categorize_issue(issue: str) -> str:
    """위반 메시지 → 분류 키 (사서 친화)."""
    text = issue.lower()
    if "880" in text:
        return "한자 880 페어 누락"
    if "008" in text:
        return "008 부호화 위반"
    if "020" in text or "isbn" in text:
        return "ISBN 형식"
    if "245" in text:
        return "245 표제 형식"
    if "049" in text:
        return "049 등록번호 형식"
    if "260" in text or "264" in text:
        return "260/264 발행사항"
    return "기타"


__all__ = [
    "SanityReport",
    "run_sanity_check",
]
