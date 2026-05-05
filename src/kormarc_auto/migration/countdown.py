"""갈래 B Cycle 12 (P37) — KOLAS III D-day 카운트다운 + 자가진단 + 타임라인.

핵심 사실 (KST·books.nl.go.kr 공식 공지·외부 매출 보고서 §A·§E):
- 2026-12-31 23:59:59 KST = KOLAS III 표준형 기술지원 종료
- 표준형만 종료·확장형은 별도 트랙 유지 (오류 시 STOP)
- 1,296 공공도서관 (2024 통계·문체부·KLA) + KNU 미사용 5,100 작은도서관
- 4 공식 후속 = 코라스Ⅲ 확장형·알파스(이씨오)·K-LAS 3.0·KOLAS-WEB

게이트:
- D-day 종료 시점 = 1초라도 다른 값 출력 시 STOP
- "확장형도 종료" 등 사실 오류 = STOP
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

# KST = UTC+9
KST = timezone(timedelta(hours=9))

# 종료 시점 (외부 매출 보고서 P37 게이트·1초 변경 = STOP)
KOLAS3_END_DATE = datetime(2026, 12, 31, 23, 59, 59, tzinfo=KST)

MigrationUrgency = Literal["urgent", "soon", "planned", "early"]


def days_until_kolas3_end(*, now: datetime | None = None) -> int:
    """남은 일수 (KST 기준·음수 가능 = 종료 후)."""
    if now is None:
        now = datetime.now(KST)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=KST)
    delta = KOLAS3_END_DATE - now
    return delta.days


@dataclass(frozen=True)
class DiagnosisAnswer:
    """5문항 자가진단 응답 (Yes/No)."""

    uses_kolas3_standard: bool  # 1. KOLAS III 표준형 사용 중인가?
    has_recent_backup: bool  # 2. 최근 1개월 내 .mrc 백업 있는가?
    has_alternative_plan: bool  # 3. 대체 시스템 검토 시작했는가?
    over_5000_records: bool  # 4. 자관 .mrc 5,000건 이상인가?
    has_dedicated_staff: bool  # 5. IT 담당 사서 있는가?


@dataclass(frozen=True)
class Diagnosis:
    """자가진단 결과."""

    urgency: MigrationUrgency
    score: int  # 0-100·100 = 가장 시급
    days_remaining: int
    recommendation: str
    next_actions: list[str]


def diagnose_migration(answers: DiagnosisAnswer, *, now: datetime | None = None) -> Diagnosis:
    """5문항 → 마이그레이션 시급도 점수 + 권장 액션.

    채점 (외부 보고서 §E·자가진단 5문항 정합):
    - KOLAS III 사용 = +40 (해당 시장)
    - 백업 X = +20 (가장 위험)
    - 대안 검토 X = +15
    - 5,000건 이상 = +15 (마이그레이션 복잡도)
    - IT 담당자 X = +10
    """
    score = 0
    if answers.uses_kolas3_standard:
        score += 40
    if not answers.has_recent_backup:
        score += 20
    if not answers.has_alternative_plan:
        score += 15
    if answers.over_5000_records:
        score += 15
    if not answers.has_dedicated_staff:
        score += 10

    days = days_until_kolas3_end(now=now)

    if score >= 70 or days <= 90:
        urgency: MigrationUrgency = "urgent"
        recommendation = "🚨 즉시 마이그레이션 시작 권장. 30일 내 무료 진단 + 백업 자동화."
        actions = [
            "kormarc-auto 무료 진단 신청 (1관 1주 PoC)",
            "현재 KOLAS III .mrc 일괄 백업 (외부 저장소·암호화)",
            "전임 사서 또는 외부 컨설팅 즉시 확보",
            "이번 주 자치구 IT 담당과 마이그레이션 일정 공유",
        ]
    elif score >= 40 or days <= 180:
        urgency = "soon"
        recommendation = "⚠ 90일 이내 PoC 시작 권장. 백업 + 대안 검토 병행."
        actions = [
            "kormarc-auto 30일 무료 trial 신청",
            "월 백업 cron 설정 + 클라우드 사본",
            "대안 후보 3종 비교 (kormarc-auto·확장형·알파스·K-LAS 3.0)",
            "차년 본예산 또는 추경에 SaaS 항목 반영 (자료구입비 1%)",
        ]
    elif score >= 20:
        urgency = "planned"
        recommendation = "✓ 계획 단계 OK. 다음 분기 PoC 권장."
        actions = [
            "kormarc-auto 데모 (30초·키 0개·KORMARC_DEMO_MODE=1)",
            "자관 049 prefix 확인 (kormarc-auto prefix-discover)",
            "사서 동료 1명과 1시간 데모 공유",
        ]
    else:
        urgency = "early"
        recommendation = "🟢 시급도 낮음. 1년 후 재진단 권장."
        actions = [
            "메일링 가입 (KOLAS III 종료 D-day 알림)",
            "분기 1회 자가진단 재실행",
        ]

    return Diagnosis(
        urgency=urgency,
        score=score,
        days_remaining=days,
        recommendation=recommendation,
        next_actions=actions,
    )


def timeline_actions_for_remaining_days(days: int) -> dict[str, list[str]]:
    """D-240/180/90/30/0 단계별 권장 액션 (외부 보고서 §E)."""
    return {
        "D-240+ (현재·골든윈도우 시작)": [
            "마이그레이션 후보 3종 비교 (kormarc-auto·확장형·알파스·K-LAS 3.0)",
            "kormarc-auto 무료 trial 30일",
            "사서 동료·자치구 IT 담당과 정보 공유",
        ],
        "D-180 (6개월 전·예산 편성)": [
            "차년 본예산 또는 추경 SaaS 항목 반영",
            "kormarc-auto PoC 1관 1주 (자관 049 prefix 검증)",
            "DPA·SLA·세금계산서 발행 가능 확인",
        ],
        "D-90 (3개월 전·계약·이전)": [
            "kormarc-auto 정식 계약 (월·분기·연간 선택)",
            "기존 KOLAS III .mrc 일괄 export → kormarc-auto 일괄 import",
            "1주 병행 운영 (회귀 검증·round-trip 100% 정합 확인)",
        ],
        "D-30 (1개월 전·전환)": [
            "신규 입수 자료 = kormarc-auto 단독 등록 (KOLAS III X)",
            "사서 교육 1회 (5분 cheatsheet)",
            "KOLAS III 백업 보관 (5년·법적 보존)",
        ],
        "D-0 ~ D+30 (종료·이후)": [
            "KOLAS III 접근 차단 후 검색·통계는 kormarc-auto 단독",
            "잔여 데이터 검증 (월 1회 round-trip 회귀)",
            "다음 사서 인수인계 매뉴얼 갱신",
        ],
    }


def lost_data_categories() -> list[dict[str, str]]:
    """KOLAS III 종료 시 잃지 말아야 할 5가지 데이터 (외부 보고서 §E)."""
    return [
        {
            "category": "서지 데이터 (.mrc)",
            "why": "KORMARC 표준 = 도서관 핵심 자산·재구축 시 권당 8분",
            "action": "월 1회 외부 저장소 백업·정식 export 절차 (KOLAS III → .mrc)",
        },
        {
            "category": "대출 이력",
            "why": "이용자 통계·5년 보존 의무 (도서관법 시행령)",
            "action": "이용자 익명화 후 CSV export·SaaS 이전 시 mapping 보존",
        },
        {
            "category": "이용자 정보",
            "why": "회원증·만 14세 미만 학교 위탁 정합·PIPA §28의8 정합",
            "action": "익명 ID + 도서관부호 매핑·DPA 기반 이전",
        },
        {
            "category": "RFID/바코드 매핑",
            "why": "물리 자료 ↔ 디지털 레코드 연결 단절 시 장서점검 불가",
            "action": "049 ▾l 등록번호 ↔ RFID UID CSV 백업",
        },
        {
            "category": "책이음·책나래 회원 키",
            "why": "5종 상호대차 통합·끊기면 이용자 즉시 불편",
            "action": "API 키·federation token 백업·이전 후 재발급 절차 사전 확보",
        },
    ]
