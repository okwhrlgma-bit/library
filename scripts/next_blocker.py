"""Cycle 25 — 다음 매출 차단점 자동 감지.

Plan B P29~P52 + 외부 의존성 매트릭스 → 다음 진행 가능 항목 자동 추천.
PO 외부 작업 진척에 따라 우선순위 동적 변경.

실행:
    python scripts/next_blocker.py        # 현재 차단점 + 권장 액션
    python scripts/next_blocker.py --json # JSON 출력 (cron·hook용)
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


@dataclass
class Blocker:
    id: str
    severity: str  # "critical" / "high" / "medium" / "low"
    description: str
    next_action: str
    estimated_unblock_days: int
    revenue_impact: str  # "🔴 매출 0 → 가능" / "🟡 정확도" / "🟢 장기"


def _has_env_key(key: str) -> bool:
    """env에 key=값 (비어있지 않음) 존재."""
    if key in os.environ and os.environ[key].strip():
        return True
    if not ENV_FILE.exists():
        return False
    try:
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key and v.strip() not in ("", '""', "''"):
                return True
    except Exception:
        pass
    return False


def _interview_count() -> int:
    """사서 인터뷰 진척 = docs/research/librarian-interviews-2026-05/ 파일 수 (Cycle 36)."""
    log_dir = ROOT / "docs" / "research" / "librarian-interviews-2026-05"
    if not log_dir.exists():
        return 0
    return sum(1 for _ in log_dir.glob("*.md"))


def detect_blockers() -> list[Blocker]:
    """현재 환경 → 차단점 리스트 (우선순위 정렬·Cycle 36 동적 강화)."""
    blockers: list[Blocker] = []

    # P30 PortOne = 사업자 등록 차단
    has_anthropic = _has_env_key("ANTHROPIC_API_KEY")
    has_nl_cert = _has_env_key("NL_CERT_KEY")
    has_data4lib = _has_env_key("DATA4LIBRARY_AUTH_KEY")
    interviews_done = _interview_count()

    # 사업자 등록 (가장 큰 매출 차단점)
    if not (ROOT / ".business-registered").exists():
        blockers.append(
            Blocker(
                id="PO-PROD-1",
                severity="critical",
                description="일반과세자 등록 미완료 = P30 PortOne 라이브 활성 X = 매출 0",
                next_action=("홈택스 (hometax.go.kr) 사업자등록 신청·업종 722000·자택 사업장·30분"),
                estimated_unblock_days=3,
                revenue_impact="🔴 매출 0 → 가능 (D+14)",
            )
        )

    # ANTHROPIC_API_KEY = AI Vision·KDC 추천 활성
    if not has_anthropic:
        blockers.append(
            Blocker(
                id="PO-PROD-6",
                severity="high",
                description="ANTHROPIC_API_KEY 미발급 = AI Vision·KDC 추천·prompt cache 실측 X",
                next_action="console.anthropic.com → API Keys → Create·5분·spend limit $50/월",
                estimated_unblock_days=0,
                revenue_impact="🟡 AI 기능·정확도 ↑",
            )
        )

    # NL_CERT_KEY = SEOJI backbone
    if not has_nl_cert:
        blockers.append(
            Blocker(
                id="PO-PROD-5",
                severity="high",
                description="NL_CERT_KEY 미발급 = 12 KORMARC 필드 자동·SEOJI 백본 X",
                next_action="nl.go.kr/seoji 회원가입 → 인증키 신청·1~3 영업일",
                estimated_unblock_days=3,
                revenue_impact="🟡 정확도",
            )
        )

    # 사서 인터뷰 진척 (Cycle 36 동적 = 0~5 단계 표시)
    if interviews_done < 5:
        remaining = 5 - interviews_done
        sev: str = "high" if interviews_done < 2 else "medium"
        blockers.append(
            Blocker(
                id="SALES-1",
                severity=sev,
                description=(
                    f"사서 인터뷰 진척 {interviews_done}/5 완료·"
                    f"잔여 {remaining}건 = wedge 확정·P39 사서어 매핑 데이터"
                ),
                next_action=(
                    "Mom Test rules·docs/research/librarian-interviews-2026-05/{slug}.md 1건씩 기록"
                ),
                estimated_unblock_days=14 if interviews_done == 0 else 7,
                revenue_impact="🔴 wedge = 매출 방향 결정",
            )
        )

    # KLA D-day (2026-05-31 마감)
    from datetime import date

    kla_deadline = date(2026, 5, 31)
    today = date.today()
    days_to_kla = (kla_deadline - today).days
    if days_to_kla > 0:
        blockers.append(
            Blocker(
                id="SALES-2",
                severity="medium" if days_to_kla > 14 else "high",
                description=f"KLA 전국도서관대회 발표 신청 마감 D-{days_to_kla}",
                next_action="kla.kr 발표 신청·docs/sales/31-kla-2026 양식 참조·30분",
                estimated_unblock_days=0,
                revenue_impact="🟡 영업 권위",
            )
        )

    # data4library (이미 발급됨 가정)
    if not has_data4lib:
        blockers.append(
            Blocker(
                id="PO-DATA4LIB",
                severity="low",
                description="DATA4LIBRARY_AUTH_KEY 미설정 (KDC 보강 폴백)",
                next_action="data4library.kr 인증키 신청·자동 적용",
                estimated_unblock_days=2,
                revenue_impact="🟢 정확도 보강",
            )
        )

    # 정신건강 (영구 우선)
    wellbeing = ROOT / ".po-wellbeing-checked"
    if not wellbeing.exists():
        blockers.append(
            Blocker(
                id="PO-WELL-1",
                severity="critical",
                description="청년 마음건강 미신청 (외부 901 보고서 진단·burnout +77%)",
                next_action=(
                    "youth.seoul.go.kr (서울 19~39세·6 free) 또는 bokjiro.go.kr 신청·30분"
                ),
                estimated_unblock_days=0,
                revenue_impact="🔴 PO 지속 가능성",
            )
        )

    # 우선순위 정렬 (severity → impact)
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    blockers.sort(key=lambda b: severity_order.get(b.severity, 9))
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    blockers = detect_blockers()

    if args.json:
        print(
            json.dumps(
                [asdict(b) for b in blockers],
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not blockers:
        print("✓ 차단점 0건·다음 사이클 자동 진행 가능")
        return 0

    print(f"=== 매출 차단점 {len(blockers)}건 (우선순위순) ===\n")
    for i, b in enumerate(blockers, 1):
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(b.severity, "⚪")
        print(f"{i}. {emoji} [{b.severity.upper()}] {b.id}")
        print(f"   설명: {b.description}")
        print(f"   액션: {b.next_action}")
        print(f"   소요: {b.estimated_unblock_days}일·영향: {b.revenue_impact}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
