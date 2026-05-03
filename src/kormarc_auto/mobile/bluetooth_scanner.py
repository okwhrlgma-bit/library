"""블루투스 바코드 스캐너 어댑터 — Phase 2 Flutter 앱 backend.

페르소나 03 (P15 순회사서) deal-breaker:
- 학교 PC가 노후·USB 부족 = HID 유선 X
- 휴대폰 페어링 = 블루투스 HID 키보드 모드
- 가장 흔한 모델: Honeywell Voyager 1602g·Datalogic QuickScan QBT2400

작동 모델:
1. 블루투스 페어링 = OS 기본 (Android·iOS)
2. 스캐너 = HID 키보드 = 입력 필드 자동 입력
3. 본 모듈 = 스캔 이벤트 검증 + ISBN 정규화 + 큐 enqueue

Phase 2 Flutter 앱에서 BLE 직접 통신은 별도 (flutter_blue_plus 라이브러리).
본 모듈은 backend에서 받은 스캔 데이터의 검증·라우팅만.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

ScannerType = Literal["honeywell_1602g", "datalogic_qbt2400", "zebex_z3190bt", "generic_hid"]


@dataclass(frozen=True)
class ScanEvent:
    """블루투스 스캐너 1회 이벤트."""

    raw: str  # 스캐너 원본 입력 (EAN-13 또는 ISBN-10)
    scanned_at: str  # ISO 8601
    scanner_type: ScannerType = "generic_hid"
    device_id: str | None = None  # 블루투스 MAC 또는 페어링 식별
    valid: bool = False
    normalized_isbn: str | None = None
    error: str | None = None


def validate_ean13(code: str) -> bool:
    """EAN-13 체크 디지트 검증 (Modulo 10)."""
    if not code or len(code) != 13 or not code.isdigit():
        return False
    digits = [int(c) for c in code]
    check_sum = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits[:-1]))
    check_digit = (10 - check_sum % 10) % 10
    return check_digit == digits[-1]


def normalize_isbn(raw: str) -> str | None:
    """스캐너 입력 정규화 (공백·하이픈 제거 + 검증)."""
    if not raw:
        return None
    cleaned = raw.strip().replace("-", "").replace(" ", "")
    if len(cleaned) == 13 and validate_ean13(cleaned):
        return cleaned
    if len(cleaned) == 10:  # ISBN-10 → 13 변환은 다른 모듈
        return cleaned
    return None


def process_scan(
    raw: str,
    scanner_type: ScannerType = "generic_hid",
    device_id: str | None = None,
) -> ScanEvent:
    """스캐너 raw 입력 → ScanEvent 생성·검증.

    Args:
        raw: 스캐너 키보드 wedge 입력
        scanner_type: 모델 식별 (디버깅·통계용)
        device_id: 블루투스 MAC

    Returns:
        ScanEvent (valid·normalized_isbn·error)
    """
    now = datetime.now(UTC).isoformat()
    normalized = normalize_isbn(raw)

    if normalized is None:
        return ScanEvent(
            raw=raw,
            scanned_at=now,
            scanner_type=scanner_type,
            device_id=device_id,
            valid=False,
            error="ISBN 형식 불일치 (EAN-13 또는 ISBN-10 필요)",
        )

    return ScanEvent(
        raw=raw,
        scanned_at=now,
        scanner_type=scanner_type,
        device_id=device_id,
        valid=True,
        normalized_isbn=normalized,
    )


# Phase 2 Flutter 앱 권장 모델·예상 가격 (영업 가이드)
RECOMMENDED_SCANNERS: dict[ScannerType, dict] = {
    "honeywell_1602g": {
        "name": "Honeywell Voyager 1602g",
        "price_won": 250_000,
        "battery_hours": 20,
        "pairing": "BT 5.0 HID",
        "notes": "산업용·내구성 우수",
    },
    "datalogic_qbt2400": {
        "name": "Datalogic QuickScan QBT2400",
        "price_won": 180_000,
        "battery_hours": 15,
        "pairing": "BT 4.0 HID",
        "notes": "가성비·교내 환경 적합",
    },
    "zebex_z3190bt": {
        "name": "ZEBEX Z-3190BT",
        "price_won": 140_000,
        "battery_hours": 10,
        "pairing": "BT 3.0 HID",
        "notes": "최저가·기본 기능만",
    },
}


__all__ = [
    "RECOMMENDED_SCANNERS",
    "ScanEvent",
    "ScannerType",
    "normalize_isbn",
    "process_scan",
    "validate_ean13",
]
