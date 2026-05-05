"""갈래 B Cycle 19A (P49·V2 §10) — 일일 토큰/USD 예산 추적 + 회귀 진단.

원칙 (V2 §8 옵저버빌리티 + §10.3 마스터 코드 정합):
- 일일 USD 예산 = $20 (PO 1인 SaaS 합리적·ENV override)
- 70% 도달 = 알람·90% = 자율 사이클 일시 정지
- 동일 작업 12K → 40K 토큰 = 모델/코드/프롬프트 회귀 진단
- 비용 = 침묵의 살인자 (V2 8 원칙 #7)
"""

from kormarc_auto.budget.regression import (
    RegressionFinding,
    detect_token_regression,
)
from kormarc_auto.budget.tracker import (
    DAILY_USD_BUDGET,
    BudgetState,
    BudgetTracker,
    UsageRecord,
)

__all__ = [
    "DAILY_USD_BUDGET",
    "BudgetState",
    "BudgetTracker",
    "RegressionFinding",
    "UsageRecord",
    "detect_token_regression",
]
