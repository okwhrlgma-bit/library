"""KORMARC 245 필드 자동 검수 — Part 81 페인 #22 정합.

KCI 학술 논문 검증: "245 필드 = KORMARC 가장 중요·오류 빈발".

검수 항목:
- 원괄호 사용 (관제)
- 식별기호 (▾a·▾b·▾c·▾h)
- 권차 표시 (▾n)
- 책임표시 (▾c · 4인 이상 합저)
- 지시기호 1·2 정합
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ValidationLevel = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class ValidationIssue:
    """검수 결과 1건."""

    field_tag: str
    subfield: str
    level: ValidationLevel
    message: str
    suggestion: str = ""


def validate_245(record_data: dict) -> list[ValidationIssue]:
    """245 필드 검수 (KCR4·KORMARC 정합).

    Args:
        record_data: dict (data_fields 포함)

    Returns:
        list[ValidationIssue] (error·warning·info)
    """
    issues: list[ValidationIssue] = []

    field_245 = None
    for f in record_data.get("data_fields", []):
        if f.get("tag") == "245":
            field_245 = f
            break

    if not field_245:
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="",
                level="error",
                message="245 필드 없음 (필수)",
                suggestion="245 ▾a 본표제 추가 필수",
            )
        )
        return issues

    # 1. ▾a 본표제 검사
    sub_a = _find_subfield(field_245, "a")
    if not sub_a:
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="a",
                level="error",
                message="▾a 본표제 없음",
                suggestion="▾a 본표제 입력 필수",
            )
        )
    else:
        # 본표제 끝 = 별도 부호 X (KCR4)
        if sub_a.endswith("."):
            issues.append(
                ValidationIssue(
                    field_tag="245",
                    subfield="a",
                    level="warning",
                    message="본표제 끝 마침표 = 권장 X",
                    suggestion="마침표 제거 권장",
                )
            )

    # 2. ▾b 부표제 (있으면) 앞에 ': ' 자동
    sub_b = _find_subfield(field_245, "b")
    if sub_b and sub_a and not sub_a.endswith(" :"):
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="a",
                level="info",
                message="▾b 부표제 = ▾a 끝에 ' :' 권장",
                suggestion="▾a 끝에 ' :' 추가",
            )
        )

    # 3. ▾c 책임표시 = 4인 이상 합저 검사 (KCR4 = 첫 1인 + 외)
    sub_c = _find_subfield(field_245, "c")
    if sub_c:
        # 콤마/세미콜론 단위 분리 (4인 이상 = 콤마 3개 이상)
        comma_count = sub_c.count(",") + sub_c.count(";")
        if comma_count >= 3:
            issues.append(
                ValidationIssue(
                    field_tag="245",
                    subfield="c",
                    level="warning",
                    message=f"4인 이상 합저 ({comma_count + 1}인) = KCR4 = 첫 1인 + 외 [기타]",
                    suggestion=f"'{sub_c.split(',')[0].strip()} 외' 권장",
                )
            )

    # 4. ▾h 자료유형 (별도 자료유형) = '[ ]' 안에
    sub_h = _find_subfield(field_245, "h")
    if sub_h and not (sub_h.startswith("[") and sub_h.endswith("]")):
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="h",
                level="error",
                message="▾h 자료유형 = '[ ]'로 묶어야 함",
                suggestion=f"'[{sub_h.strip('[]')}]' 권장",
            )
        )

    # 5. 지시기호 1·2 검사
    ind1 = field_245.get("ind1", " ")
    ind2 = field_245.get("ind2", " ")

    # 지시기호1 = 책임표시 동일여부 (1=같음, 0=없음)
    if ind1 not in ("0", "1"):
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="",
                level="warning",
                message=f"지시기호 1 = '{ind1}' (1=책임표시 같음·0=없음 권장)",
                suggestion="0 또는 1 사용",
            )
        )

    # 지시기호2 = 관제 길이 + 1
    if not ind2.isdigit() and ind2 != " ":
        issues.append(
            ValidationIssue(
                field_tag="245",
                subfield="",
                level="warning",
                message=f"지시기호 2 = '{ind2}' (관제 길이+1 또는 0)",
                suggestion="0~9 사용",
            )
        )

    return issues


def _find_subfield(field: dict, code: str) -> str | None:
    """필드에서 특정 식별기호 값 찾기."""
    for sub in field.get("subfields", []):
        if sub.get("code") == code:
            return sub.get("value")
    return None


def auto_fix_suggestions(issues: list[ValidationIssue]) -> dict[str, str]:
    """검수 결과 → 자동 수정 제안 매핑.

    Returns:
        dict[subfield_code, suggested_value]
    """
    fixes = {}
    for issue in issues:
        if issue.suggestion and issue.subfield:
            fixes[issue.subfield] = issue.suggestion
    return fixes


__all__ = ["ValidationIssue", "ValidationLevel", "auto_fix_suggestions", "validate_245"]
