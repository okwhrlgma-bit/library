"""영업 funnel 추적 — 신규 가입 → 무료 50건 사용 → 결제 전환 단계별 측정.

PO 매월 1회 실행 → 어느 단계에서 사서 이탈하는지 즉시 파악 → 영업 메시지·
UI·가격 조정 의사결정.

데이터 소스:
- `logs/signups.jsonl` — signup 이벤트 (api_key·library_name·timestamp)
- `logs/usage.jsonl` — 변환 이벤트 (api_key·records·timestamp)
- `logs/feedback.jsonl` — 피드백 이벤트 (api_key·rating·comment)

사용:
    python scripts/sales_funnel.py
    python scripts/sales_funnel.py --json reports/funnel_2026-05.json
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"


@dataclass(frozen=True)
class FunnelMetrics:
    """단계별 funnel 정량."""

    signups: int
    activated: int  # 1건 이상 변환
    free_quota_used: int  # 무료 50건 모두 소진
    paid: int  # 결제 시작
    activation_rate_pct: float  # signups → activated
    quota_exhaust_rate_pct: float  # activated → free_quota_used
    paid_conversion_rate_pct: float  # free_quota_used → paid
    end_to_end_pct: float  # signups → paid

    def to_dict(self) -> dict[str, Any]:
        return {
            "signups": self.signups,
            "activated": self.activated,
            "free_quota_used": self.free_quota_used,
            "paid": self.paid,
            "activation_rate_pct": self.activation_rate_pct,
            "quota_exhaust_rate_pct": self.quota_exhaust_rate_pct,
            "paid_conversion_rate_pct": self.paid_conversion_rate_pct,
            "end_to_end_pct": self.end_to_end_pct,
        }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """JSONL 파일 → list of dicts (없으면 빈 list)."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            with contextlib.suppress(json.JSONDecodeError):
                records.append(json.loads(line))
    return records


def compute_funnel(
    signups: list[dict[str, Any]],
    usage: list[dict[str, Any]],
    *,
    free_quota: int = 50,
) -> FunnelMetrics:
    """signups·usage → funnel 단계별 정량.

    paid = is_paid:true 표시된 키 (포트원 webhook handle_event가 갱신 예정).
    free_quota_used = 무료 한도 100% 도달 (records >= free_quota).
    """
    signup_keys = {s.get("api_key") for s in signups if s.get("api_key")}
    n_signups = len(signup_keys)

    # 키별 누적 사용량
    usage_by_key: Counter[str] = Counter()
    for u in usage:
        key = u.get("api_key")
        if key:
            usage_by_key[key] += int(u.get("records", 1))

    activated_keys = {k for k, n in usage_by_key.items() if n > 0 and k in signup_keys}
    quota_used_keys = {k for k, n in usage_by_key.items() if n >= free_quota and k in signup_keys}

    # 결제 키 = signup 또는 usage 기록의 is_paid 플래그
    paid_keys: set[str] = set()
    for s in signups:
        if s.get("is_paid"):
            paid_keys.add(s.get("api_key"))
    for u in usage:
        if u.get("is_paid"):
            paid_keys.add(u.get("api_key"))
    paid_keys &= signup_keys

    n_activated = len(activated_keys)
    n_quota = len(quota_used_keys)
    n_paid = len(paid_keys)

    def _pct(num: int, denom: int) -> float:
        return round(num / denom * 100, 1) if denom else 0.0

    return FunnelMetrics(
        signups=n_signups,
        activated=n_activated,
        free_quota_used=n_quota,
        paid=n_paid,
        activation_rate_pct=_pct(n_activated, n_signups),
        quota_exhaust_rate_pct=_pct(n_quota, n_activated),
        paid_conversion_rate_pct=_pct(n_paid, n_quota),
        end_to_end_pct=_pct(n_paid, n_signups),
    )


def funnel_by_persona(
    signups: list[dict[str, Any]],
    usage: list[dict[str, Any]],
    interviews: list[dict[str, Any]],
    *,
    free_quota: int = 50,
) -> dict[str, FunnelMetrics]:
    """4 페르소나별 funnel 분리 — KLA 슬라이드 직접 데이터 ★.

    interviews는 `aggregate_interviews.load_interviews()` 결과 또는 동등.
    각 인터뷰의 `persona` + `library_name` (또는 `api_key`)를 통해 signup·usage 매칭.
    """
    persona_keys: dict[str, set[str]] = {}
    for i in interviews:
        p = str(i.get("persona") or "unknown")
        key = i.get("api_key") or i.get("library_name") or i.get("librarian_name")
        if key:
            persona_keys.setdefault(p, set()).add(str(key))

    result: dict[str, FunnelMetrics] = {}
    for persona, keys in persona_keys.items():
        s_filtered = [
            s for s in signups
            if s.get("api_key") in keys or s.get("library_name") in keys
        ]
        u_filtered = [
            u for u in usage
            if u.get("api_key") in keys or u.get("library_name") in keys
        ]
        result[persona] = compute_funnel(s_filtered, u_filtered, free_quota=free_quota)

    return result


def render_summary(metrics: FunnelMetrics) -> str:
    lines: list[str] = []
    lines.append("=== 영업 funnel ===")
    lines.append(f"가입 (signup):       {metrics.signups}")
    lines.append(f"활성 (1건+ 변환):    {metrics.activated} ({metrics.activation_rate_pct}%)")
    lines.append(f"무료 한도 도달:      {metrics.free_quota_used} ({metrics.quota_exhaust_rate_pct}% of 활성)")
    lines.append(f"결제:                {metrics.paid} ({metrics.paid_conversion_rate_pct}% of 한도 도달)")
    lines.append(f"end-to-end (가입→결제): {metrics.end_to_end_pct}%")
    lines.append("")
    lines.append("=== 영업 의사결정 ===")
    if metrics.activation_rate_pct < 50 and metrics.signups >= 5:
        lines.append("- 활성률 < 50% → onboarding 메시지 강화 (welcome·첫 1건 가이드)")
    if metrics.quota_exhaust_rate_pct < 30 and metrics.activated >= 5:
        lines.append("- 한도 도달률 < 30% → UX 개선 (5분 시연·도구 탭 단순화)")
    if metrics.paid_conversion_rate_pct < 10 and metrics.free_quota_used >= 5:
        lines.append("- 결제 전환률 < 10% → 가격 조정·결제 결정자 영업 (학교 카드·자치구 예산)")
    if metrics.end_to_end_pct >= 5:
        lines.append("- end-to-end >= 5% → 채널 확장 (사서교육원·블로그 SEO·KLA)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=None, help="JSON 보고서 경로")
    parser.add_argument("--free-quota", type=int, default=50)
    args = parser.parse_args()

    signups = _load_jsonl(LOGS_DIR / "signups.jsonl")
    usage = _load_jsonl(LOGS_DIR / "usage.jsonl")

    metrics = compute_funnel(signups, usage, free_quota=args.free_quota)
    print(render_summary(metrics))

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(metrics.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nJSON 보고서: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
