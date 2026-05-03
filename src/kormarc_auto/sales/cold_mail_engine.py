"""콜드메일 자동 생성 엔진 — G1 (Part 88 v2 결제자 깔때기 정합).

PO 명령 (12-섹션 §3.2): "5 페르소나 PILOT 폼·자동 환영 메일"
PO 결제자 깔때기: 사서 → 행정실장·교장·본관·교육청 (2단계)

5 segment:
- 사서교사 (학교) → 행정실장 cc
- 작은도서관 관장 → 본인 (1단계)
- 대학 분관 → 본관 cc
- 공공도서관 평사서 → 관장 cc
- 자치구 담당관 → 직접

작동:
1. 페르소나·세그먼트 분류
2. 핵심 페인 키워드 매칭 (Part 76~82 54건 검증)
3. ROI 데이터 자동 삽입 (decision_maker_pdf 결과)
4. 결제자 깔때기 메시지 자동
5. 회신 추적 ID 자동 (sales_funnel 통합)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

ColdSegment = Literal[
    "school_teacher",  # 사서교사 → 행정실장
    "small_library_director",  # 작은도서관 관장 (본인 결제)
    "university_branch",  # 대학 분관 → 본관
    "public_library",  # 공공도서관 평사서 → 관장
    "jachigu_official",  # 자치구 담당관 직접
]


# Segment별 페인 키워드 (Part 76~82)
SEGMENT_PAINS: dict[ColdSegment, list[str]] = {
    "school_teacher": [
        "사서교사 13.9% 배치·정규 사서교사 미배치 84% (공무직·기간제 포함 시 48~57% 배치)",
        "권당 8분 KORMARC = 사서교사 시간 부족",
        "DLS 521 자료유형 자동 안 됨 = 자원봉사 어려움",
        "행정실 결재 = 사서가 직접 자료 만들기 부담",
    ],
    "small_library_director": [
        "1인 운영 = 모든 일 동시",
        "권당 외주 3,000~5,000원 = 연간 수백만원",
        "책단비·hwp 양식 매번 수기 입력",
        "사서 + 자원봉사 + 행정 모두 본인",
    ],
    "university_branch": [
        "DDC·MeSH·LCSH 3중 분류 수기",
        "Alma 호환 X = 본관 통합 어려움",
        "의학·인문 분야별 다른 분류 체계",
        "PubMed 검색 → KORMARC 변환 수기",
    ],
    "public_library": [
        "KOLAS 2026.12 종료 마이그레이션",
        "880 한자 병기 자동 X",
        "KDC 자동 분류 약함",
        "이용자 OPAC 검색 빈약",
    ],
    "jachigu_official": [
        "자치구 25관 일괄 영업 = 1관씩 협상 비효율",
        "정부 자금 (AI 바우처) 활용 가능",
        "사서 시간 절감 = 예산 절감 직결",
        "PIPA 정합 SaaS 수의계약 가능",
    ],
}


# Segment별 결제자 깔때기 메시지
DECISION_MAKER_FUNNEL: dict[ColdSegment, str] = {
    "school_teacher": "행정실장님께 보여드릴 1페이지 ROI 자료 자동 생성 (decision_maker_pdf)",
    "small_library_director": "관장님 본인 결제 = 결재 단계 0",
    "university_branch": "본관 도서관장님께 보고할 Alma 호환 검증 자료 포함",
    "public_library": "관장님 결재 양식 자동 (자치구 통합 구매 정합)",
    "jachigu_official": "자치구 25관 일괄 도입 = 관당 비용 60% 할인",
}


@dataclass(frozen=True)
class ColdMailRequest:
    """콜드메일 입력."""

    recipient_name: str  # 익명 표기 가능 (사서 A·관장 B)
    segment: ColdSegment
    library_name: str  # ○○도서관 (익명)
    annual_book_count: int = 500  # ROI 계산용
    custom_pain: str | None = None  # 추가 페인


@dataclass(frozen=True)
class ColdMailDraft:
    """생성된 콜드메일."""

    subject: str
    greeting: str
    pain_paragraph: str
    solution_paragraph: str
    roi_paragraph: str
    funnel_paragraph: str
    cta_paragraph: str
    signature: str
    tracking_id: str
    full_body: str = ""

    def render(self) -> str:
        """전체 메일 본문 렌더링."""
        return f"""{self.greeting}

{self.pain_paragraph}

{self.solution_paragraph}

{self.roi_paragraph}

{self.funnel_paragraph}

{self.cta_paragraph}

{self.signature}

[추적 ID: {self.tracking_id}]
"""


_id_counter = 0


def _generate_tracking_id(segment: ColdSegment, recipient: str) -> str:
    """sales_funnel 추적 ID (microsecond + counter = 충돌 0)."""
    global _id_counter
    _id_counter += 1
    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    safe_recipient = "".join(c for c in recipient if c.isalnum())[:5] or "X"
    return f"CM-{segment[:3].upper()}-{ts}-{safe_recipient}-{_id_counter:04d}"


def _calc_roi_summary(annual_book_count: int) -> dict:
    """간단 ROI 계산 (decision_maker_pdf 정합)."""
    minutes_saved = annual_book_count * 6.5  # 8 → 1.5
    hours_saved = round(minutes_saved / 60, 1)
    savings_won = int(hours_saved * 18_000)
    metered_cost = annual_book_count * 200
    return {
        "hours_saved": hours_saved,
        "savings_won": savings_won,
        "metered_cost": metered_cost,
        "net_savings": savings_won - metered_cost,
    }


def generate_cold_mail(request: ColdMailRequest) -> ColdMailDraft:
    """콜드메일 자동 생성."""
    pains = SEGMENT_PAINS[request.segment]
    funnel_msg = DECISION_MAKER_FUNNEL[request.segment]
    roi = _calc_roi_summary(request.annual_book_count)

    subject = f"[{request.library_name}] KORMARC 권당 8분 → 1.5분 자동화 (PILOT 무료 50건)"

    greeting = f"안녕하세요, {request.recipient_name}님."

    pain_paragraph = (
        f"{request.library_name} 같은 도서관이 매일 마주하시는 고민을 정리했습니다:\n"
        + "\n".join(f"  • {p}" for p in pains[:3])
    )
    if request.custom_pain:
        pain_paragraph += f"\n  • {request.custom_pain}"

    solution_paragraph = (
        "kormarc-auto는 ISBN 1번 입력으로 KORMARC 레코드를 5초 내 생성합니다. "
        "KOLAS·DLS·알파스 즉시 반입 가능하고, 사서 검수 단계는 100% 보존됩니다."
    )

    roi_paragraph = (
        f"연간 {request.annual_book_count:,}권 기준 ROI:\n"
        f"  • 사서 시간 절감: {roi['hours_saved']:.1f}시간/년 = 약 {roi['savings_won']:,}원\n"
        f"  • 도입 비용 (권당 200원): {roi['metered_cost']:,}원/년\n"
        f"  • 순 절감: {roi['net_savings']:,}원/년"
    )

    funnel_paragraph = f"💡 {funnel_msg}"

    cta_paragraph = (
        "30일 무료 PILOT (50건 무료) 신청만 부탁드립니다. "
        "5분 안에 첫 .mrc 출력을 보여드리고, 만족하지 않으시면 바로 종료 가능합니다.\n\n"
        "회신 주시면 30분 화상 시연 일정 잡겠습니다."
    )

    signature = (
        "사서 출신 1인 개발자 (PO)\n"
        "kormarc-auto SaaS\n"
        "GitHub: https://github.com/kormarc-auto/library (private)\n"
        "이메일: [PO 이메일]"
    )

    tracking_id = _generate_tracking_id(request.segment, request.recipient_name)

    draft = ColdMailDraft(
        subject=subject,
        greeting=greeting,
        pain_paragraph=pain_paragraph,
        solution_paragraph=solution_paragraph,
        roi_paragraph=roi_paragraph,
        funnel_paragraph=funnel_paragraph,
        cta_paragraph=cta_paragraph,
        signature=signature,
        tracking_id=tracking_id,
    )
    return draft


def batch_generate(
    requests: list[ColdMailRequest],
) -> list[ColdMailDraft]:
    """일괄 생성 (50건 운영)."""
    return [generate_cold_mail(r) for r in requests]


__all__ = [
    "DECISION_MAKER_FUNNEL",
    "SEGMENT_PAINS",
    "ColdMailDraft",
    "ColdMailRequest",
    "ColdSegment",
    "batch_generate",
    "generate_cold_mail",
]
