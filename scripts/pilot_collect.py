"""자관 PILOT 시연 결과 1줄 수집 + JSON 자동 저장 + aggregate.

PO 시연 직후 30초 안에 결과 입력 가능. 4 페르소나 templated 인터랙티브:
- 매크로 사서 (사서 E)·수서 사서 (사서 A)·종합 사서 (4명)·영상 사서 (X)

저장: `logs/interviews/<YYYY-MM-DD>_<도서관>_<사서>.json`
이후: `scripts/aggregate_interviews.py`로 자동 집계 → KLA 슬라이드 데이터.

사용:
    python scripts/pilot_collect.py
    python scripts/pilot_collect.py --persona macro --library "○○도서관"
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs" / "interviews"

PERSONAS = {
    "macro": {
        "name": "Excel 매크로 자작 사서",
        "example": "사서 E",
        "default_payment_band": "30000-50000",
        "key_painpoints": ["xlsm 매크로 유지보수", "책단비 hwp 수동", "매크로 학습 곡선"],
    },
    "acquisition": {
        "name": "수서 사서",
        "example": "사서 A",
        "default_payment_band": "30000-150000",
        "key_painpoints": ["정보나루 수동 검색", "자관 중복 확인", "KDC 균형 산정"],
    },
    "general": {
        "name": "종합 사서",
        "example": "사서 B·사서 C·사서 D",
        "default_payment_band": "30000-50000",
        "key_painpoints": ["연체 통계 수동", "월간 보고서 PDF", "장서점검 시간"],
    },
    "video": {
        "name": "영상 편집 사서 (영업 X)",
        "example": "김신학",
        "default_payment_band": "0",
        "key_painpoints": ["우리 영역 X"],
    },
}


def _ask(prompt: str, default: str = "") -> str:
    """interactive 입력 (default 표시)."""
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or default


def _ask_int(prompt: str, default: int, min_v: int = 0, max_v: int = 10) -> int:
    """0~max_v 정수 입력."""
    while True:
        raw = _ask(prompt, str(default))
        try:
            value = int(raw)
            if min_v <= value <= max_v:
                return value
        except ValueError:
            pass
        print(f"  → {min_v}~{max_v} 정수 입력")


def collect(persona_key: str, library: str) -> dict:
    """PILOT 시연 결과 인터랙티브 수집."""
    if persona_key not in PERSONAS:
        raise ValueError(f"persona '{persona_key}' 미지원 (선택: {list(PERSONAS)})")
    persona = PERSONAS[persona_key]

    print(f"\n=== PILOT 시연 결과 수집: {persona['name']} ({persona['example']}) ===\n")

    librarian = _ask("사서 이름", persona["example"])
    week = _ask_int("PILOT 주차 (1~4)", 1, 1, 4)
    today = datetime.now().strftime("%Y-%m-%d")

    nps = _ask_int("NPS (0~10)", 8, 0, 10)
    q1_band = _ask("Q1 결제 의향 (HIGH/MID/LOW/0)", "MID").upper()
    payment_band = _ask("월 지불 의향 KRW band", persona["default_payment_band"])

    decision_maker = _ask(
        "결제 결정자 (self/director/budget_committee/none)", "self",
    )

    pre_min = _ask_int("수동 마크 시간 (권당 분)", 8, 1, 60)
    post_min = _ask_int("우리 시스템 마크 시간 (권당 분)", 2, 0, 60)
    saved_pct = round((pre_min - post_min) / pre_min * 100, 1) if pre_min else 0.0

    impressive = _ask(
        "가장 인상 깊은 기능 (콤마 구분)",
        "ISBN 5초·KOLAS 자동 반입",
    ).split(",")
    pain_remaining = _ask(
        "여전히 페인 (콤마 구분)",
        ",".join(persona["key_painpoints"][:2]),
    ).split(",")

    free_comment = _ask("사서 자유 코멘트 한 줄", "")
    consent_quote = _ask("KLA 발표 인용 동의 (y/n)", "y").lower() == "y"

    record = {
        "date": today,
        "library_name": library,
        "library_type": "public",
        "librarian_name": librarian,
        "persona": persona_key,
        "persona_label": persona["name"],
        "pilot_week": week,
        "pre_marc_minutes": pre_min,
        "post_marc_minutes": post_min,
        "time_saved_pct": saved_pct,
        "biggest_painpoints": [p.strip() for p in pain_remaining if p.strip()],
        "demo_impressive": [i.strip() for i in impressive if i.strip()],
        "nps": nps,
        "q1_payment_band": q1_band,
        "willingness_to_pay_monthly_krw_band": payment_band,
        "payment_decision_maker": decision_maker,
        "free_comment": free_comment,
        "consent_kla_quote": consent_quote,
    }
    return record


def save(record: dict) -> Path:
    """JSON 저장 (logs/interviews/<date>_<library>_<librarian>.json)."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    safe_lib = record["library_name"].replace(" ", "_").replace("/", "_")
    safe_lib_short = safe_lib[:30]
    safe_lib2 = record["librarian_name"].replace(" ", "_").replace("/", "_")
    filename = f"{record['date']}_{safe_lib_short}_{safe_lib2}.json"
    path = LOGS_DIR / filename
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--persona", default="macro", choices=list(PERSONAS.keys()),
        help="PILOT 사서 페르소나",
    )
    parser.add_argument(
        "--library", default="○○도서관",
        help="도서관명",
    )
    args = parser.parse_args()

    record = collect(args.persona, args.library)
    path = save(record)

    print(f"\n[저장 완료] {path}")
    print(f"  NPS: {record['nps']}/10 | Q1: {record['q1_payment_band']} | "
          f"시간 절감: {record['time_saved_pct']}%")
    print("\n[다음 단계]")
    print("  python scripts/aggregate_interviews.py  # 누적 집계 + 보고서 생성")
    print("  KLA 발표 outline S6~S9에 결과 채워넣기 (consent_kla_quote=true 데이터만)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
