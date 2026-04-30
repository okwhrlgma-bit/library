"""자관 049 ▾l 등록번호 prefix 자동 발견.

PILOT 시작 시 사서가 자관 .mrc 디렉토리만 지정 → prefix 분포 자동 추출 →
config 갱신 권장값 출력.

사용 예 (다른 자관 PILOT 1주차):
    discoverer = PrefixDiscoverer(threshold_pct=1.0)
    summary = discoverer.scan(Path("D:/자관/수서"))
    # summary.recommended_prefixes == ('AB', 'CD', ...)

영업 가치: 다른 자관 PILOT 즉시 99%+ 정합 도달 (자관 「내를건너서 숲으로
도서관」 4-29 실측 = WQ 1.7% 발견 → 99.82% 정합).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PrefixSummary:
    """049 prefix 발견 결과."""

    total_records: int
    prefix_counts: dict[str, int]
    recommended_prefixes: tuple[str, ...]
    threshold_pct: float

    def to_yaml_snippet(self) -> str:
        """config.yaml에 붙여넣기 가능한 snippet."""
        prefixes_list = ", ".join(f'"{p}"' for p in self.recommended_prefixes)
        return (
            "# kormarc-auto가 자관 .mrc 분석으로 자동 발견한 prefix 정책.\n"
            "# 사서 검수 후 본 config 적용.\n"
            "kolas_register:\n"
            f"  registration_prefix: [{prefixes_list}]\n"
        )


class PrefixDiscoverer:
    """자관 .mrc 디렉토리 → 049 prefix 분포 추출."""

    def __init__(self, *, threshold_pct: float = 1.0) -> None:
        """
        Args:
            threshold_pct: 이 비율 이상 등장하는 prefix만 권장 (default 1%).
                           예: 0.5 → 0.5% 이상 prefix 모두 포함.
        """
        if not 0 < threshold_pct < 100:
            raise ValueError("threshold_pct는 0과 100 사이")
        self.threshold_pct = threshold_pct

    def scan(self, root: Path) -> PrefixSummary:
        """디렉토리 재귀 검색 → prefix 분포.

        Args:
            root: .mrc 파일 디렉토리 (재귀).

        Returns:
            PrefixSummary.
        """
        try:
            from pymarc import MARCReader
        except ImportError as e:
            raise RuntimeError("pymarc 미설치 — `pip install pymarc`") from e

        if not root.exists():
            return PrefixSummary(0, {}, (), self.threshold_pct)

        counter: Counter[str] = Counter()
        total = 0

        for path in root.rglob("*.mrc"):
            for record in self._parse_any_encoding(path, MARCReader):
                total += 1
                prefix = self._extract_049_prefix(record)
                if prefix:
                    counter[prefix] += 1

        threshold_count = total * (self.threshold_pct / 100)
        recommended = tuple(sorted(
            prefix for prefix, count in counter.items() if count >= threshold_count
        ))

        return PrefixSummary(
            total_records=total,
            prefix_counts=dict(counter),
            recommended_prefixes=recommended,
            threshold_pct=self.threshold_pct,
        )

    @staticmethod
    def _parse_any_encoding(path: Path, reader_cls: Any) -> list[Any]:
        """KOLAS .mrc 인코딩 fallback (cp949·utf-8·euc-kr)."""
        for encoding in ("cp949", "utf-8", "euc-kr"):
            try:
                with path.open("rb") as f:
                    records = [
                        r for r in reader_cls(
                            f, force_utf8=False, to_unicode=True, file_encoding=encoding,
                        ) if r
                    ]
                if records:
                    return records
            except (UnicodeDecodeError, ValueError, OSError):
                continue
        return []

    @staticmethod
    def _extract_049_prefix(record: Any) -> str | None:
        """049 ▾l 첫 2글자 추출 (대문자 정규화)."""
        field = record.get("049")
        if not field:
            return None
        for sf in field.subfields:
            if sf.code == "l":
                value = (sf.value or "").strip()
                if len(value) >= 2:
                    return value[:2].upper()
        return None
