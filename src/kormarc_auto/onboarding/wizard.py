"""갈래 B Cycle 19B (P32) — 5분 온보딩 위저드.

5단계 (외부 매출 보고서 P32 정합):
1. 자관코드 입력 (도서관부호 또는 사업자등록번호)
2. 분류체계 선택 (KDC 6판 / DDC / 자관 자체)
3. 880 한자 병기 옵션 (자관 한자 자료 보유 여부)
4. DLS / KOLAS / 알파스 출력 형식 선택
5. 첫 ISBN 등록 (체험·offline demo SAMPLE_BOOKS 활용)

5분 안 완료 시 = activation funnel 첫 단계 통과.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

WizardStep = Literal[
    "library_code",
    "classification",
    "hanja_880",
    "output_format",
    "first_isbn",
    "complete",
]

WIZARD_STEPS: list[WizardStep] = [
    "library_code",
    "classification",
    "hanja_880",
    "output_format",
    "first_isbn",
    "complete",
]


_STEP_LABELS = {
    "library_code": "1단계 / 5: 자관코드",
    "classification": "2단계 / 5: 분류체계",
    "hanja_880": "3단계 / 5: 880 한자 병기 옵션",
    "output_format": "4단계 / 5: 출력 형식 (DLS·KOLAS·알파스)",
    "first_isbn": "5단계 / 5: 첫 ISBN 등록 (체험)",
    "complete": "✅ 완료 — 5분 위저드 종료·30일 trial 시작",
}


@dataclass
class OnboardingState:
    """위저드 진행 상태 (사서 본인 데이터·다른 도서관 노출 X)."""

    user_id: str
    current_step: WizardStep = "library_code"
    library_code: str = ""
    classification_system: Literal["KDC6", "DDC", "custom", ""] = ""
    enable_hanja_880: bool = False
    output_formats: list[str] = field(default_factory=list)  # ["DLS", "KOLAS", "ALPAS"]
    first_isbn: str = ""
    started_at: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    completed_at: str | None = None

    def step_label(self) -> str:
        return _STEP_LABELS.get(self.current_step, self.current_step)


def initial_state(user_id: str) -> OnboardingState:
    """신규 사용자 위저드 시작 상태."""
    return OnboardingState(user_id=user_id)


def advance_step(state: OnboardingState, *, step_data: dict) -> OnboardingState:
    """다음 단계 전이·검증 통과 후 갱신.

    Args:
        state: 현재 위저드 상태
        step_data: 현 단계 입력값 (단계별 키 다름)

    Returns:
        갱신된 OnboardingState (in-place·반환)
    """
    cur = state.current_step

    if cur == "library_code":
        code = str(step_data.get("library_code", "")).strip()
        if not code:
            raise ValueError("자관코드 또는 사업자등록번호 필수")
        state.library_code = code
        state.current_step = "classification"

    elif cur == "classification":
        system = step_data.get("classification_system", "")
        if system not in ("KDC6", "DDC", "custom"):
            raise ValueError("분류체계 = KDC6 / DDC / custom 중 1택")
        state.classification_system = system
        state.current_step = "hanja_880"

    elif cur == "hanja_880":
        state.enable_hanja_880 = bool(step_data.get("enable_hanja_880", False))
        state.current_step = "output_format"

    elif cur == "output_format":
        fmts = step_data.get("output_formats", [])
        if not isinstance(fmts, list) or not fmts:
            raise ValueError("출력 형식 1개 이상 선택 (DLS·KOLAS·ALPAS)")
        valid = {"DLS", "KOLAS", "ALPAS"}
        invalid = set(fmts) - valid
        if invalid:
            raise ValueError(f"지원 X 형식: {invalid}·지원 = DLS·KOLAS·ALPAS")
        state.output_formats = fmts
        state.current_step = "first_isbn"

    elif cur == "first_isbn":
        isbn = str(step_data.get("first_isbn", "")).strip().replace("-", "")
        if not isbn or len(isbn) != 13 or not isbn.isdigit():
            raise ValueError("ISBN-13 13자리 숫자 필수 (예: 9788937437076)")
        state.first_isbn = isbn
        state.current_step = "complete"
        state.completed_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    elif cur == "complete":
        # 멱등 (재호출 안전)
        pass

    return state


def is_complete(state: OnboardingState) -> bool:
    return state.current_step == "complete" and state.completed_at is not None


def progress_percentage(state: OnboardingState) -> int:
    """진행률 % (0-100)."""
    idx = WIZARD_STEPS.index(state.current_step)
    return int(idx / (len(WIZARD_STEPS) - 1) * 100)
