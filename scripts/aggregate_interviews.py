"""베타 사서 인터뷰 누적 분석 — `docs/beta-interview-template.md` 응답 자동 집계.

PILOT 사서 인터뷰가 `logs/interviews/<YYYY-MM-DD>_<도서관>_<사서>.json` 또는
`.md` 형식으로 누적됨. 본 스크립트는 JSON 응답을 읽어:

1. NPS (Net Promoter Score) 평균
2. 페인포인트 Top 5 빈도
3. 지불 의향 분포
4. 결제 결정자 분포
5. 도서관 종류별 클러스터링

매월 1회 PO에게 보고서 자동 생성. 다음 자율 디벨롭 우선순위 입력.

JSON 응답 양식 (사서 인터뷰 후 PO가 수기 입력):
```json
{
  "date": "2026-04-26",
  "library_name": "○○도서관",
  "library_type": "small",  // public|school|small|university|special
  "librarian_name": "○○",
  "librarian_age_band": "50s",
  "it_familiarity": 2,
  "current_systems": ["KOLAS"],
  "daily_marc_minutes": 60,
  "biggest_painpoints": ["KDC 분류 결정", "880 한자"],
  "demo_impressive": ["ISBN 단건", "사진 입력"],
  "nps": 9,
  "willingness_to_pay_monthly_krw_band": "30000-50000",
  "payment_decision_maker": "self",
  "consortium_eligible": true,
  "feature_requests": ["고서 처리 강화"]
}
```
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
INTERVIEWS_DIR = ROOT / "logs" / "interviews"


def load_interviews() -> list[dict[str, Any]]:
    if not INTERVIEWS_DIR.exists():
        return []
    out: list[dict[str, Any]] = []
    for p in INTERVIEWS_DIR.glob("*.json"):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def nps_score(interviews: list[dict[str, Any]]) -> dict[str, Any]:
    """NPS 표준 산식: %Promoters(9~10) - %Detractors(0~6)."""
    if not interviews:
        return {"score": None, "n": 0, "promoters": 0, "passives": 0, "detractors": 0}
    n = len(interviews)
    promoters = sum(1 for i in interviews if (i.get("nps") or 0) >= 9)
    detractors = sum(1 for i in interviews if (i.get("nps") or 0) <= 6)
    passives = n - promoters - detractors
    score = (promoters / n - detractors / n) * 100
    return {
        "score": round(score, 1),
        "n": n,
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "promoter_rate": round(promoters / n, 2),
        "detractor_rate": round(detractors / n, 2),
    }


def painpoint_top(interviews: list[dict[str, Any]], top: int = 5) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for i in interviews:
        for p in i.get("biggest_painpoints", []) or []:
            c[str(p).strip()] += 1
    return c.most_common(top)


def willingness_distribution(interviews: list[dict[str, Any]]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for i in interviews:
        c[str(i.get("willingness_to_pay_monthly_krw_band") or "unknown")] += 1
    return dict(c)


def decision_maker_distribution(interviews: list[dict[str, Any]]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for i in interviews:
        c[str(i.get("payment_decision_maker") or "unknown")] += 1
    return dict(c)


def by_library_type(interviews: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for i in interviews:
        t = str(i.get("library_type") or "unknown")
        by_type.setdefault(t, []).append(i)
    return {
        t: {
            "count": len(v),
            "nps": nps_score(v),
            "willingness": willingness_distribution(v),
        }
        for t, v in by_type.items()
    }


def by_persona(interviews: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """4 페르소나별 NPS·Q1·시간 절감·결제 의향 분석 (KLA 슬라이드 직접 데이터 ★).

    pilot_collect.py가 저장한 'persona' 키 (macro·acquisition·general·video)
    별로 그룹화 → 페르소나별 정량 비교.
    """
    by_p: dict[str, list[dict[str, Any]]] = {}
    for i in interviews:
        p = str(i.get("persona") or "unknown")
        by_p.setdefault(p, []).append(i)

    result: dict[str, dict[str, Any]] = {}
    for p, group in by_p.items():
        time_saved = [
            float(g["time_saved_pct"])
            for g in group
            if isinstance(g.get("time_saved_pct"), (int, float))
        ]
        q1_counter: Counter[str] = Counter()
        for g in group:
            q1_counter[str(g.get("q1_payment_band") or "unknown")] += 1

        kla_quotable = sum(1 for g in group if g.get("consent_kla_quote"))

        result[p] = {
            "count": len(group),
            "label": (group[0].get("persona_label") or "?") if group else "?",
            "nps": nps_score(group),
            "willingness": willingness_distribution(group),
            "q1_distribution": dict(q1_counter),
            "avg_time_saved_pct": round(sum(time_saved) / len(time_saved), 1)
            if time_saved
            else 0.0,
            "kla_quotable_count": kla_quotable,
            "decision_makers": decision_maker_distribution(group),
        }
    return result


def feature_request_top(interviews: list[dict[str, Any]], top: int = 5) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for i in interviews:
        for f in i.get("feature_requests", []) or []:
            c[str(f).strip()] += 1
    return c.most_common(top)


def render_summary(interviews: list[dict[str, Any]]) -> str:
    if not interviews:
        return "인터뷰 0건 — `logs/interviews/*.json` 디렉토리에 응답 추가 후 재실행."

    n = len(interviews)
    nps = nps_score(interviews)
    pains = painpoint_top(interviews)
    will = willingness_distribution(interviews)
    dm = decision_maker_distribution(interviews)
    by_t = by_library_type(interviews)
    feats = feature_request_top(interviews)

    lines: list[str] = []
    lines.append(f"# 베타 사서 인터뷰 누적 분석 (n={n})")
    lines.append("")
    lines.append("## NPS")
    lines.append(
        f"- **{nps['score']}** (Promoter {nps['promoters']} / Passive {nps['passives']} / Detractor {nps['detractors']})"
    )
    lines.append(f"- Promoter rate: {nps['promoter_rate']:.0%} → 컨소시엄 영업 채널 가능 사서 수")
    lines.append("")
    lines.append("## 페인포인트 Top 5")
    for p, cnt in pains:
        lines.append(f"- {p}: {cnt}건")
    lines.append("")
    lines.append("## 지불 의향 분포")
    for k, v in sorted(will.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}건")
    lines.append("")
    lines.append("## 결제 결정자 분포")
    for k, v in sorted(dm.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}건")
    lines.append("")
    lines.append("## 도서관 종류별")
    for t, info in by_t.items():
        s = info["nps"]["score"]
        lines.append(f"- {t}: n={info['count']}, NPS={s}")
    lines.append("")

    lines.append("## 4 페르소나별 (KLA 슬라이드 직접 데이터 ★)")
    by_p = by_persona(interviews)
    for p, info in by_p.items():
        s = info["nps"]["score"]
        lines.append(
            f"- **{p}** ({info['label']}): n={info['count']}, NPS={s}, "
            f"평균 시간 절감={info['avg_time_saved_pct']}%, "
            f"KLA 인용 가능={info['kla_quotable_count']}건"
        )
        if info["q1_distribution"]:
            q1_str = " · ".join(f"{k}={v}" for k, v in info["q1_distribution"].items())
            lines.append(f"  · Q1 결제 의향: {q1_str}")
    lines.append("")
    lines.append("## 기능 요청 Top 5 (다음 자율 디벨롭 우선순위)")
    for f, cnt in feats:
        lines.append(f"- {f}: {cnt}건")
    lines.append("")
    lines.append("## 자율 디벨롭 행동 권고")
    if nps["score"] is not None and nps["score"] >= 30:
        lines.append("- ✓ NPS 30+ → 컨소시엄 영업 본격 진입 가능 (`docs/consortium-pitch.md`)")
    elif nps["score"] is not None and nps["score"] < 0:
        lines.append("- ❌ NPS 음수 → 페인포인트 Top 1 즉시 코드 수정 우선")
    if pains:
        top_pain = pains[0][0]
        lines.append(f"- 페인포인트 1위 '{top_pain}' → 다음 commit 단위로 모듈 추가/강화")
    if feats:
        top_feat = feats[0][0]
        lines.append(f"- 기능 요청 1위 '{top_feat}' → 자율 우선순위 #1")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    parser.add_argument("--output", default=None, help="결과 저장 경로 (.md)")
    args = parser.parse_args()

    interviews = load_interviews()

    if args.json:
        print(
            json.dumps(
                {
                    "n": len(interviews),
                    "nps": nps_score(interviews),
                    "painpoints_top": painpoint_top(interviews),
                    "willingness": willingness_distribution(interviews),
                    "decision_maker": decision_maker_distribution(interviews),
                    "by_library_type": by_library_type(interviews),
                    "feature_requests_top": feature_request_top(interviews),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        text = render_summary(interviews)
        print(text)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
            print(f"\n✓ 보고서 저장: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
