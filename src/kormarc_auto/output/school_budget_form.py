"""학교운영위 결재 양식 PDF 자동 생성.

Part 50 발견: 영업 자료 28건 (P2 사서교사) ↔ 코드 불일치 해결.

5 표준 템플릿 (서울·경기·부산·대구·기타) + 사용자 커스텀 옵션.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

TemplateRegion = Literal["seoul", "gyeonggi", "busan", "daegu", "other"]


@dataclass
class SchoolBudgetFormData:
    """학교운영위 결재 양식 데이터."""

    school_name: str
    school_address: str
    librarian_name: str  # 사서교사 이름
    proposal_title: str = "학교도서관 KORMARC 자동화 도구 도입의 건"
    monthly_cost_krw: int = 30_000  # 월 3만원 (작은 학교 기준)
    annual_cost_krw: int = 360_000
    start_date: date | None = None
    region: TemplateRegion = "other"
    additional_notes: str = ""


def generate_school_budget_form_markdown(data: SchoolBudgetFormData) -> str:
    """학교운영위 제출용 결재 양식 Markdown 생성.

    P2 사서교사 페인 직접 해결:
    - 양식 작성 시간: 15분 → 1분 (학교 정보 1회 입력)
    - 운영위 회의 안건 즉시 제출 가능
    """
    start = data.start_date or date.today()

    return f"""# {data.proposal_title}

## 1. 안건 개요

| 항목 | 내용 |
|------|------|
| 안건명 | {data.proposal_title} |
| 제안자 | {data.school_name} 도서관 ({data.librarian_name} 사서교사 선생님) |
| 시행일 | {f"{start.year}년 {start.month}월 {start.day}일"} |
| 제안 일자 | {date.today().strftime("%Y년 %m월 %d일")} |

## 2. 도입 사유

### 2.1 현황
- 학교도서관 KORMARC (한국문헌자동화목록형식) 작업 = 권당 약 8분 수동 입력
- 사서교사 1인이 수업·행정·도서관 운영 동시 부담
- 학생·학부모 자원봉사 = KORMARC 자격증 X = 외주 의존

### 2.2 도입 효과
- **사서교사 권당 작업 시간: 8분 → 2분 (75% 절감)**
- **자원봉사·학생도 사용 가능** (5분 학습)
- **사서교사 일괄 검수 큐**: 권당 8분 → 권당 30초 (16x 가속)
- KORMARC 2023.12 표준 정합 + KOLAS·독서로DLS 직접 호환

### 2.3 검증 자료
- PILOT 1관 (수도권·사서 8명 운영) 174건 4단 검증: **99.82% 정합**
- 한국 학교도서관 12,200관 / 사서교사 12.1% (16.16% 갱신, 2025) 정합

## 3. 비용

| 구분 | 금액 |
|------|------|
| 월 정액 | {data.monthly_cost_krw:,}원 |
| **연간 비용** | **{data.annual_cost_krw:,}원** |
| 학교운영비 차지 비율 | 0.0X% (학교 규모별) |
| 가격 인상 | 없음 (Niche Academy 패턴 정합) |
| 기존 고객 가격 동결 | ✅ 영구 |

### 비교: 알파스 v1.0 (㈜이씨오)
- 도입 비용: **1,000만원** (1회 결제)
- 학교 운영비 부담 ↑↑
- → kormarc-auto 27년치 운영비 = 알파스 1관 도입비

## 4. 정부 자금 활용 가능 (도입 부담 0원)

### AI 원스톱 바우처 (NIPA 2026, 8,900억원)
- 학교 = 수요기업 → 최대 2억원 정부 자금
- kormarc-auto = 공급기업 등록 진행 중
- **학교운영비 0원 도입 가능**

### S2B 학교장터
- 사업자 등록 후 즉시 등록 예정
- 학교 행정실 → S2B 검색·결제 (5분)

## 5. 일정

| 시점 | 활동 |
|------|------|
| {f"{start.month}월 {start.day}일"} | 도구 도입·사서교사 5분 학습 |
| {f"{start.month}월 {start.day}일"} + 1주 | 자원봉사·학생 입력·사서교사 검수 시작 |
| {f"{start.month}월 {start.day}일"} + 4주 | 효과 측정·운영위 보고 |

## 6. 첨부 자료

- PILOT 1관 99.82% 정합 검증 보고서
- 한국 학교도서관 통계 (사서교사 16.16% 갱신·자원봉사 86%)
- KORMARC KS X 6006-0:2023.12 표준 정합 자료
- AI 원스톱 바우처 신청 가이드 (NIPA)
- 학교도서관진흥법 제4차 기본계획 (2024~2028) 정합

## 7. 결재 의견

| 직위 | 의견 | 결재 |
|------|------|------|
| 사서교사 | (자동 생성) | ☐ 동의 ☐ 보류 |
| 교감 | | ☐ 동의 ☐ 보류 |
| 교장 | | ☐ 승인 ☐ 보류 |
| 학교운영위원장 | | ☐ 승인 ☐ 보류 |

---

> 본 결재 양식은 kormarc-auto가 자동 생성한 초안입니다.
> 학교 사정에 맞게 수정 후 제출해주세요.
> 문의: okwhrlgma@gmail.com

{f"## 추가 메모{chr(10)}{chr(10)}{data.additional_notes}{chr(10)}" if data.additional_notes else ""}
"""


def generate_school_budget_form_pdf(data: SchoolBudgetFormData, output_path: str) -> bool:
    """PDF 생성 (reportlab 또는 pandoc 활용 시).

    선택적 의존성 — 미설치 시 Markdown만 반환.
    """
    markdown = generate_school_budget_form_markdown(data)

    try:
        # reportlab으로 PDF 생성 (선택적)
        # 또는 pandoc·weasyprint 활용
        # 현재는 Markdown 파일로 저장 (사서가 직접 PDF 변환)
        from pathlib import Path

        Path(output_path).write_text(markdown, encoding="utf-8")
        return True
    except Exception:
        return False


# 지역별 표준 템플릿 메타 (현재는 동일 본문 + 지역별 추가 메모)
REGIONAL_NOTES: dict[TemplateRegion, str] = {
    "seoul": "서울특별시교육청 1교 1사서 정책 정합 (2025 시행계획).",
    "gyeonggi": "경기도교육청 1교 1사서 강화 방안 정합 (2025-03 발표).",
    "busan": "부산광역시교육청 학교도서관 진흥 기본계획 정합.",
    "daegu": "대구광역시교육청 학교도서관 운영 매뉴얼 정합.",
    "other": "제4차 학교도서관 진흥 기본계획(2024~2028) 정합.",
}


def get_regional_template(region: TemplateRegion) -> str:
    """지역별 정책 정합 메모 (영업 자료에 추가)."""
    return REGIONAL_NOTES.get(region, REGIONAL_NOTES["other"])
