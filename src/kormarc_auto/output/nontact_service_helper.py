"""비대면 도서관 서비스 자동 — Part 82+ 페인 #43 정합.

사서 페인 (코로나 이후·NLK 6대 과제):
- 비대면 부담 38.5% (사서 업무 부담 1순위)
- 비대면 콘텐츠·디지털 격차·온라인 문화행사 부담

해결: 비대면 서비스 6 종 자동 (북드라이브스루·우편·온라인 행사·전자도서관·QR·VR/AR).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

ServiceType = Literal[
    "drive_through",  # 북 드라이브스루
    "postal",  # 우편 대출
    "online_event",  # 온라인 문화행사
    "ebook_loan",  # 전자도서관
    "qr_pickup",  # QR 무인 픽업
    "vr_ar",  # VR·AR 콘텐츠
]


@dataclass(frozen=True)
class NontactRequest:
    """비대면 서비스 요청."""

    service_type: ServiceType
    user_id: str
    book_ids: list[str]
    pickup_time: datetime | None = None
    delivery_address: str = ""
    notes: str = ""


SERVICE_DESCRIPTIONS = {
    "drive_through": {
        "name": "북 드라이브스루",
        "description": "예약한 책을 자동차로 직접 받기",
        "lead_time_days": 1,
    },
    "postal": {
        "name": "우편 대출",
        "description": "예약 책 = 우편 발송",
        "lead_time_days": 3,
    },
    "online_event": {
        "name": "온라인 문화행사",
        "description": "Zoom·유튜브 라이브",
        "lead_time_days": 0,
    },
    "ebook_loan": {
        "name": "전자도서관 대출",
        "description": "도서관 전자도서 즉시 다운로드",
        "lead_time_days": 0,
    },
    "qr_pickup": {
        "name": "QR 무인 픽업",
        "description": "QR 인증·로커 픽업",
        "lead_time_days": 1,
    },
    "vr_ar": {
        "name": "VR/AR 콘텐츠",
        "description": "도서관 가상 투어·체험",
        "lead_time_days": 0,
    },
}


def estimate_service_time(request: NontactRequest) -> dict:
    """서비스별 예상 시간·자동 안내 메시지."""
    info = SERVICE_DESCRIPTIONS.get(request.service_type, {})
    lead = info.get("lead_time_days", 1)

    return {
        "service_name": info.get("name", ""),
        "lead_time_days": lead,
        "expected_ready_date": (date.today().toordinal() + lead),
        "message": (
            f"{info.get('name', '')} 신청 접수 완료. "
            f"준비 = {lead}일 이내. 준비 완료 시 알림드릴게요."
        ),
    }


def generate_user_notification(request: NontactRequest, library_name: str) -> str:
    """이용자 알림 (이메일·카톡 알림톡 호환)."""
    info = SERVICE_DESCRIPTIONS.get(request.service_type, {})
    book_str = ", ".join(request.book_ids[:3])

    return (
        f"[{library_name}] {info.get('name', '')} 신청 안내\n\n"
        f"신청 도서: {book_str}\n"
        f"준비 기간: {info.get('lead_time_days', 1)}일\n\n"
        f"{info.get('description', '')}\n\n"
        f"준비 완료 시 다시 알림드립니다."
    )


__all__ = [
    "SERVICE_DESCRIPTIONS",
    "NontactRequest",
    "ServiceType",
    "estimate_service_time",
    "generate_user_notification",
]
