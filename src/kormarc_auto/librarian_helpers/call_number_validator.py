"""청구기호 자동 검수·수정 제안 — Part 82 페인 #31 정합.

청구기호 = 4 요소 (별치·분류·도서·부차).
사서 응용 부담 = 자관 정책 + KDC + 저자기호 + 권차.

해결: 자동 검수 + 수정 제안.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ValidationLevel = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class CallNumberIssue:
    """청구기호 검수 1건."""

    component: str  # 별치·분류·도서·부차·전체
    level: ValidationLevel
    message: str
    suggestion: str = ""


KDC_MAIN_CLASSES = ["000", "100", "200", "300", "400", "500", "600", "700", "800", "900"]


def validate_call_number(call_number: str, *, sasagwan_prefix: str = "") -> list[CallNumberIssue]:
    """청구기호 검수.

    표준 형식: {별치}{KDC분류}/{이재철 도서기호}{권차}
    예: "시문학811.7/ㅇ676ㅁ" 또는 "863.2/ㅂ234ㄱ v.3"

    Args:
        call_number: 검수 대상 청구기호
        sasagwan_prefix: 자관 prefix (선택)

    Returns:
        list[CallNumberIssue]
    """
    issues: list[CallNumberIssue] = []

    if not call_number or not call_number.strip():
        issues.append(
            CallNumberIssue(
                component="전체",
                level="error",
                message="청구기호 비어있음",
                suggestion="KDC 분류 + 저자기호 입력 필수",
            )
        )
        return issues

    # 1. KDC 분류 (3자리 숫자) = 청구기호 시작 부분 또는 '/' 앞
    # "/" 앞 또는 시작 부분만 검사 (도서기호의 숫자는 제외)
    pre_slash = call_number.split("/")[0] if "/" in call_number else call_number
    kdc_match = re.search(r"\d{3}(\.\d+)?", pre_slash)
    if not kdc_match:
        issues.append(
            CallNumberIssue(
                component="분류",
                level="error",
                message="KDC 분류기호 (3자리 숫자) 없음",
                suggestion="000~999 KDC 6판 사용",
            )
        )
    else:
        kdc = kdc_match.group()
        # 첫 3자리 = 대분류 검증
        main = kdc[:3]
        major_class = main[0] + "00"
        if major_class not in KDC_MAIN_CLASSES:
            issues.append(
                CallNumberIssue(
                    component="분류",
                    level="warning",
                    message=f"KDC '{main}' = 일반 대분류 외",
                    suggestion="KDC 6판 표준 확인",
                )
            )

    # 2. '/' 구분자 = KDC ↔ 도서기호
    if "/" not in call_number:
        issues.append(
            CallNumberIssue(
                component="도서",
                level="warning",
                message="'/' 구분자 (분류 ↔ 도서기호) 없음",
                suggestion=f"예: {kdc_match.group() if kdc_match else 'KDC'}/ㅇ123ㅁ",
            )
        )

    # 3. 도서기호 (한글 + 숫자) 검증
    book_match = re.search(r"[가-힣]+\d+", call_number)
    if not book_match:
        issues.append(
            CallNumberIssue(
                component="도서",
                level="warning",
                message="도서기호 (한글 + 숫자) 없음",
                suggestion="이재철 저자기호 (예: ㅇ123)",
            )
        )

    # 4. 자관 prefix (있으면) 일관성
    if sasagwan_prefix and not call_number.startswith(sasagwan_prefix):
        issues.append(
            CallNumberIssue(
                component="별치",
                level="info",
                message=f"자관 prefix '{sasagwan_prefix}' 없음",
                suggestion=f"'{sasagwan_prefix}{call_number}'",
            )
        )

    # 5. 권차 (v.3·c.2 등) 형식
    if " " in call_number:
        suffix = call_number.split(" ")[-1]
        if suffix and not re.match(r"^[vc]\.\d+$", suffix):
            issues.append(
                CallNumberIssue(
                    component="부차",
                    level="info",
                    message="권차/복본 = 'v.N' 또는 'c.N' 권장",
                    suggestion="예: v.3 또는 c.2",
                )
            )

    return issues


def suggest_call_number(
    *,
    kdc: str,
    author_korean: str,
    sasagwan_prefix: str = "",
    volume: int | None = None,
    copy: int | None = None,
) -> str:
    """청구기호 자동 생성 (이재철 저자기호 단순화).

    Args:
        kdc: KDC 분류기호
        author_korean: 저자명 (한글)
        sasagwan_prefix: 자관 prefix (선택)
        volume: 권차
        copy: 복본

    Returns:
        청구기호 (예: "시문학811.7/ㅇ123ㅁ v.3")
    """
    # 이재철 저자기호 단순 (첫 자음 + 숫자)
    if author_korean:
        first = author_korean[0]
        # 한글 자음 추출 단순 (Phase 1)
        if "가" <= first <= "힣":
            jamo_idx = (ord(first) - ord("가")) // 588
            chosung_list = [
                "ㄱ",
                "ㄲ",
                "ㄴ",
                "ㄷ",
                "ㄸ",
                "ㄹ",
                "ㅁ",
                "ㅂ",
                "ㅃ",
                "ㅅ",
                "ㅆ",
                "ㅇ",
                "ㅈ",
                "ㅉ",
                "ㅊ",
                "ㅋ",
                "ㅌ",
                "ㅍ",
                "ㅎ",
            ]
            chosung = chosung_list[jamo_idx]
        else:
            chosung = first
        author_code = f"{chosung}{(ord(first) % 1000):03d}"
    else:
        author_code = ""

    parts = []
    if sasagwan_prefix:
        parts.append(sasagwan_prefix)
    parts.append(kdc)
    if author_code:
        parts.append(f"/{author_code}")

    cn = "".join(parts)

    if volume:
        cn += f" v.{volume}"
    if copy:
        cn += f" c.{copy}"

    return cn


__all__ = [
    "CallNumberIssue",
    "ValidationLevel",
    "suggest_call_number",
    "validate_call_number",
]
