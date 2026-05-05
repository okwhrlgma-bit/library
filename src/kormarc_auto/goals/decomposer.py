"""갈래 B Cycle 22 (P52·V2 §5) — Goal Decomposer.

5계층 분해 + 금지 행동 (V2 §5.3 안전장치):
- 가격·도메인·DB schema·결제·이메일·production env 변경 = 자동 X (사람만)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# V2 §5.3 금지 행동 = 일일 자율 루프가 절대 자동 X
FORBIDDEN_ACTIONS = (
    "가격 변경",
    "도메인 변경",
    "DB 스키마 변경",
    "결제 로직 변경",
    "이메일 도메인 변경",
    "production 환경변수 변경",
    "사용자 PII 처리 변경",
)


@dataclass
class Action:
    """일일 단위 실행 항목 (5계층 중 가장 하위)."""

    description: str
    priority: float = 0.5  # 0.0~1.0
    estimated_tokens: int = 5000
    is_forbidden: bool = False


@dataclass
class GoalHierarchy:
    """5계층 = Goal → Strategy → Initiative → Task → Action."""

    goal: str  # 분기 1회·PO
    strategy: str  # 월 1회·PO
    initiative: str  # 주 1회·PO
    tasks: list[str] = field(default_factory=list)  # 일일 자율
    actions: list[Action] = field(default_factory=list)  # 일일 자율


def is_forbidden_action(description: str) -> bool:
    """금지 행동 키워드 매칭 (자동 unsafe 분류)."""
    desc_lower = description.lower()
    forbidden_keywords = (
        "가격",
        "도메인",
        "스키마",
        "결제 로직",
        "이메일 도메인",
        "환경변수",
        "PII",
        "schema",
        "domain",
        "price",
    )
    return any(kw in desc_lower or kw.lower() in desc_lower for kw in forbidden_keywords)


def suggest_daily_actions(
    *,
    initiative: str,
    yesterday_kpis: dict,
    max_actions: int = 3,
) -> list[Action]:
    """전일 KPI + 현재 Initiative → 오늘 Action 1~3개.

    V2 §5.2 정합:
    - 금지 행동 자동 차단
    - 최대 3개 (집중력 분산 차단)
    - 각 Action = 5K 토큰 추정 (예산 정합)
    """
    actions: list[Action] = []

    # KPI 약점 = 우선 액션 (단순 규칙)
    if yesterday_kpis.get("demo_start", 0) == 0:
        actions.append(
            Action(
                description="네이버 검색 키워드 1위 콘텐츠 1건 발행 (P36 블로그 파이프라인)",
                priority=0.9,
                estimated_tokens=8000,
            )
        )

    if yesterday_kpis.get("activation_rate_pct", 100) < 30:
        actions.append(
            Action(
                description="5분 위저드 단계별 drop-off 분석 + UX 개선 (P32)",
                priority=0.8,
                estimated_tokens=6000,
            )
        )

    if (
        yesterday_kpis.get("paid_conversions", 0) == 0
        and yesterday_kpis.get("upgrade_clicked", 0) > 5
    ):
        actions.append(
            Action(
                description="결제 flow 마찰 제거 (P30 PortOne 통합 점검·사업자 등록 후만)",
                priority=0.7,
                estimated_tokens=10000,
            )
        )

    # 일반 Initiative 진행
    if not actions:
        actions.append(
            Action(
                description=f"{initiative} 다음 step (KPI 정상)",
                priority=0.5,
                estimated_tokens=5000,
            )
        )

    # 금지 행동 차단 (V2 §5.3)
    safe_actions = []
    for a in actions[:max_actions]:
        if is_forbidden_action(a.description):
            safe_actions.append(
                Action(
                    description=f"⛔ 금지·사람 큐로: {a.description}",
                    priority=a.priority,
                    estimated_tokens=0,
                    is_forbidden=True,
                )
            )
        else:
            safe_actions.append(a)

    return safe_actions
