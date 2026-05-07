"""Cycle 73 — 사서 인터뷰 결과 분석 자동 (PO 1주 작업 후 즉시).

5명 인터뷰 .md 파일 → 평균 점수·결제 권한·페르소나 매핑·결정 트리.
LLM 호출 0·통계 결정적 (V3 §4.10 정합).

실행:
    python scripts/analyze_interviews.py
    python scripts/analyze_interviews.py --json    # JSON 출력
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from pathlib import Path

# Windows cp949 = utf-8 강제
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
INTERVIEWS_DIR = ROOT / "docs" / "research" / "librarian-interviews-2026-05"


def parse_interview_file(path: Path) -> dict:
    """인터뷰 .md 파일 → dict (front matter + score 추출)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    result = {
        "file": path.name,
        "interview_id": None,
        "persona_match": None,
        "score": None,
        "payment_intent_b2c": None,
        "payment_intent_b2b": None,
        "competitor": [],
        "valid": False,
    }

    # front matter (interview_id·persona_match)
    fm = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm:
        for line in fm.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip()
                if k == "interview_id":
                    result["interview_id"] = v
                elif k == "persona_match":
                    result["persona_match"] = v.split("/")[0].strip()  # 첫 매칭

    # 점수 추출 (예: "**점수**: 3 / 5")
    score_match = re.search(r"\*\*점수\*\*\s*[:：]\s*(\d+)\s*/\s*5", text)
    if score_match:
        result["score"] = int(score_match.group(1))
        result["valid"] = True

    # B2C 결제 의향
    if "본인 결제 의향" in text:
        # "B2C ₩9,900 본인 결제 의향: 예 / 아니오 / 모름"
        b2c_match = re.search(r"본인 결제 의향[^\n]*[:：]\s*(예|아니오|모름)", text)
        if b2c_match:
            result["payment_intent_b2c"] = b2c_match.group(1)

    # B2B 결재 가능
    if "결재 가능" in text:
        b2b_match = re.search(r"B2B[^\n]*결재 가능[^\n]*[:：]\s*(예|아니오|모름)", text)
        if b2b_match:
            result["payment_intent_b2b"] = b2b_match.group(1)

    # 경쟁자 (체크박스)
    competitors = ["MarcEdit", "KOLAS III", "ALPAS", "K-LAS", "두드림", "엑셀", "복붙"]
    for comp in competitors:
        if re.search(rf"\[x\]\s*{re.escape(comp)}", text, re.IGNORECASE):
            result["competitor"].append(comp)

    return result


def aggregate_results(interviews: list[dict]) -> dict:
    """5명 결과 → 평균·결정·페르소나 분포.

    임계 (외부 858 보고서 + Cycle 67 playbook 정합):
    - 평균 점수 ≥ 3.5 = 사업성 ✅
    - 2.5~3.5 = 모름·5명 추가
    - < 2.5 = 사업성 ❌·MarcEdit 모델
    """
    valid = [i for i in interviews if i["valid"]]
    if not valid:
        return {
            "n": 0,
            "status": "데이터 부족·인터뷰 .md 파일 박제 후 재실행",
            "next_action": "TEMPLATE.md 복사 → A.md·B.md·... 작성",
        }

    scores = [i["score"] for i in valid]
    avg = sum(scores) / len(scores)

    # 결정 트리
    if avg >= 3.5:
        decision = "✅ 사업성 OK·계속·외부 5관 PILOT 시작"
    elif avg >= 2.5:
        decision = "🟡 모름·5명 추가 인터뷰 (1주)"
    else:
        decision = "❌ 사업성 약함·MarcEdit 모델 + 자동 클리커 검토"

    # 페르소나 분포
    personas = {}
    for i in valid:
        p = i["persona_match"]
        if p:
            personas[p] = personas.get(p, 0) + 1

    # 결제 의향 (B2C·B2B 분리)
    b2c_yes = sum(1 for i in valid if i["payment_intent_b2c"] == "예")
    b2c_no = sum(1 for i in valid if i["payment_intent_b2c"] == "아니오")
    b2b_yes = sum(1 for i in valid if i["payment_intent_b2b"] == "예")

    # 경쟁자 빈도
    competitor_freq = {}
    for i in valid:
        for c in i["competitor"]:
            competitor_freq[c] = competitor_freq.get(c, 0) + 1

    return {
        "n": len(valid),
        "average_score": round(avg, 2),
        "scores": scores,
        "decision": decision,
        "persona_distribution": personas,
        "b2c_payment_yes": b2c_yes,
        "b2c_payment_no": b2c_no,
        "b2c_payment_yes_pct": round(b2c_yes / len(valid) * 100, 1) if valid else 0,
        "b2b_payment_yes": b2b_yes,
        "competitor_frequency": competitor_freq,
        "next_action": _next_action(avg, b2c_yes, valid),
    }


def _next_action(avg: float, b2c_yes: int, valid: list) -> str:
    """결정 트리 → 다음 액션."""
    if not valid:
        return "TEMPLATE.md 복사 → 인터뷰 박제 5건"
    if avg >= 3.5 and b2c_yes >= 3:
        return "B2C 진행·Supabase Auth 통합·PortOne sandbox·PILOT 5관 모집"
    if avg >= 3.5 and b2c_yes < 3:
        return "B2B 우위·도서관장 (P8) 우선·KLMA 채널·세금계산서 통합"
    if avg >= 2.5:
        return "5명 추가 인터뷰·메시지 v2·페르소나 재검토"
    return "도서관 = MarcEdit 모델·자동 클리커 SaaS 시작·60 사이클 학습 자산"


def render_text_report(agg: dict) -> str:
    """CLI 친화 텍스트 리포트."""
    lines = ["=== 사서 인터뷰 결과 분석 (Cycle 73·invariant 11 활성) ==="]
    if agg["n"] == 0:
        lines.append(f"⚠ {agg['status']}")
        lines.append(f"→ {agg['next_action']}")
        return "\n".join(lines)

    lines.append(f"\nN = {agg['n']}명·평균 점수 = {agg['average_score']}/5")
    lines.append(f"개별 점수: {agg['scores']}")
    lines.append(f"\n결정: {agg['decision']}")
    lines.append("\n=== 페르소나 분포 ===")
    for p, n in sorted(agg["persona_distribution"].items()):
        lines.append(f"  {p}: {n}명")

    lines.append("\n=== 결제 의향 ===")
    lines.append(
        f"  B2C ₩9,900 본인 결제: {agg['b2c_payment_yes']}/{agg['n']} "
        f"({agg['b2c_payment_yes_pct']}%)"
    )
    lines.append(f"  B2B ₩30K+/월 결재: {agg['b2b_payment_yes']}/{agg['n']}")

    if agg["competitor_frequency"]:
        lines.append("\n=== 경쟁자 빈도 ===")
        for c, n in sorted(agg["competitor_frequency"].items(), key=lambda x: -x[1]):
            lines.append(f"  {c}: {n}명")

    lines.append("\n=== 다음 액션 ===")
    lines.append(f"→ {agg['next_action']}")
    lines.append("\n⚠ 정직 헤더: 본 분석 = 인터뷰 N건 = 1차 자료 (invariant 11 활성)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="사서 인터뷰 결과 분석")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    if not INTERVIEWS_DIR.exists():
        print(f"⚠ 인터뷰 디렉토리 미발견: {INTERVIEWS_DIR}")
        return 0

    files = [f for f in INTERVIEWS_DIR.glob("*.md") if f.name not in ("TEMPLATE.md", "README.md")]
    interviews = [parse_interview_file(f) for f in files]
    agg = aggregate_results(interviews)

    if args.json:
        print(json.dumps(agg, ensure_ascii=False, indent=2))
    else:
        print(render_text_report(agg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
