"""갈래 B Cycle 16B (P38·외부 매출 보고서) — 자치구·교육청 묶음 견적 자동.

원칙 (외부 매출 보고서 P38·§3 영업 동선 정합):
- 5/10/25/100관 묶음 = 10/15/20/25% (billing.plans 정합)
- VAT 별도·세금계산서 발행 가능 (일반과세자·간이과세 차단)
- 견적 유효기간 30일·직인 placeholder
- 자치구 수의계약 임계 인용 (2,000만원·1인 견적)

STOP 조건:
- 간이과세자 모드 청구서 = STOP (세금계산서 불가 = 학교 거래 차단)
- CSAP 미인증·"공공 SaaS" 표기 = STOP (허위표시)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from kormarc_auto.billing import BillingCycle, calculate_quote, get_plan


@dataclass(frozen=True)
class BundleQuote:
    """자치구·교육청 묶음 견적."""

    customer_name: str  # "○○자치구청·구립도서관 25관"
    branch_count: int
    plan_code: str
    cycle: BillingCycle
    founding_member: bool
    subtotal_krw: int
    vat_krw: int
    grand_total_krw: int
    discount_pct_total: float
    issued_at: str
    valid_until: str
    legal_basis_note: str  # 클라우드컴퓨팅법 §20 등

    def to_quote_dict(self) -> dict:
        return {
            "customer_name": self.customer_name,
            "branch_count": self.branch_count,
            "plan_code": self.plan_code,
            "plan_label": get_plan(self.plan_code).label,
            "cycle": self.cycle,
            "founding_member": self.founding_member,
            "subtotal_krw": self.subtotal_krw,
            "vat_krw": self.vat_krw,
            "grand_total_krw": self.grand_total_krw,
            "discount_pct_total": self.discount_pct_total,
            "issued_at": self.issued_at,
            "valid_until": self.valid_until,
            "legal_basis": self.legal_basis_note,
            "currency": "KRW",
            "vat_note": "VAT 별도·세금계산서 발행 (일반과세자)",
        }


def _legal_basis_for(branch_count: int, plan_code: str) -> str:
    """공공 영업 견적 = 법적 근거 인용 자동 (외부 매출 보고서 §3 정합)."""
    parts = []
    if plan_code in ("public", "enterprise"):
        parts.append("「클라우드컴퓨팅법」 §20 (국가기관 SaaS 우선 도입 의무)")
    if branch_count >= 100:
        parts.append("「지방계약법 시행령」 §25 (영세기업 1인 견적 1억 이내)")
    elif branch_count >= 5:
        parts.append("「지방계약법 시행령」 §30 (수의계약 2,000만원 임계)")
    parts.append("「조세특례제한법」 (일반과세자·세금계산서 발행 가능)")
    return "·".join(parts)


def generate_bundle_quote(
    *,
    customer_name: str,
    branch_count: int,
    plan_code: str = "public",
    cycle: BillingCycle = "annual",
    founding_member: bool = False,
    issued_on: date | None = None,
    valid_days: int = 30,
    is_simplified_tax_payer: bool = False,
) -> BundleQuote:
    """묶음 견적 생성. 일반과세자만 허용·간이과세자 = ValueError."""
    # STOP 조건 1: 간이과세자 차단 (외부 858 출처·세금계산서 불가)
    if is_simplified_tax_payer:
        raise ValueError(
            "간이과세자 모드 = 세금계산서 발급 불가 = 학교·공공 거래 차단·일반과세자 등록 필수"
        )

    quote = calculate_quote(
        plan_code=plan_code,
        branch_count=branch_count,
        cycle=cycle,
        founding_member=founding_member,
    )

    if issued_on is None:
        issued_on = date.today()
    valid_until = issued_on + timedelta(days=valid_days)

    return BundleQuote(
        customer_name=customer_name,
        branch_count=branch_count,
        plan_code=plan_code,
        cycle=cycle,
        founding_member=founding_member,
        subtotal_krw=quote["subtotal_krw"],
        vat_krw=quote["vat_krw"],
        grand_total_krw=quote["grand_total_krw"],
        discount_pct_total=quote["total_discount_pct"],
        issued_at=issued_on.isoformat(),
        valid_until=valid_until.isoformat(),
        legal_basis_note=_legal_basis_for(branch_count, plan_code),
    )


def render_quote_markdown(q: BundleQuote, *, supplier_name: str = "kormarc-auto") -> str:
    """견적서 markdown (PDF 변환 전 단계)."""
    plan = get_plan(q.plan_code)
    return f"""# 견적서 (Quote)

**공급자**: {supplier_name}
**고객**: {q.customer_name}
**발행일**: {q.issued_at}
**유효기간**: {q.valid_until} (30일)

## 견적 내역

| 항목 | 내용 |
|---|---|
| 플랜 | {plan.label} ({q.plan_code}) |
| 분관 수 | {q.branch_count}관 |
| 결제 주기 | {q.cycle} |
| Founding Member | {"Yes (영구 50%)" if q.founding_member else "No"} |
| 종합 할인율 | {q.discount_pct_total * 100:.1f}% |

## 금액

| 항목 | 금액 (KRW) |
|---|---:|
| 공급가 | ₩{q.subtotal_krw:,} |
| VAT (10%) | ₩{q.vat_krw:,} |
| **합계** | **₩{q.grand_total_krw:,}** |

## 법적 근거

{q.legal_basis_note}

## 결제 방식

- 가상계좌 (KG이니시스·B2B 표준)
- 입금 확인 후 팝빌 전자세금계산서 자동 발행
- 일반과세자·세금계산서 발급 가능

## 직인

(발행 시 사업자 직인 첨부·placeholder)
"""


def build_procurement_pack_index() -> dict[str, str]:
    """디지털서비스몰 카탈로그 등록용 ZIP 패키지 인덱스 (외부 매출 보고서 §3.6)."""
    return {
        "사업자등록증": "공급자 일반과세자·정보통신업 722000",
        "통장사본": "사업자 통장 (B2B 가상계좌 입금용)",
        "직접생산증명서": "한국정보통신산업진흥원·SaaS 직접 개발",
        "이용약관": "docs/legal/terms-* + 자동갱신·환불·자동결제 4개 조항",
        "개인정보처리방침": "docs/legal/privacy-policy-2026-05.md (§28의8 6항목 5수신자)",
        "DPA": "docs/legal/dpa-data-processing-agreement-2026-05.md (PIPA §26 8항목)",
        "SLA": "docs/legal/sla-service-level-agreement-2026-05.md (99.5% 환급 5~15%)",
        "환불정책": "docs/legal/refund-policy-2026-05.md (§17·§18 7일·3영업일)",
        "AI 안내": "docs/legal/ai-disclaimer-2026-05.md (인공지능 기본법 §31)",
        "회사소개서": "kormarc-auto v0.7.0·자관 PILOT 1관 round-trip 100%·903 tests",
        "방법론": "docs/eval/methodology.md (재현 가능 명세)",
        "보안 검토 자료": "ISMS-P 간편인증 (자치구 진출 시·매출 발생 후)",
        "CSAP 인증서": "v1.0+ 시점·매출 발생 후 검토 (소중기업 50-70% 환급)",
        "4대보험·국세·지방세 완납증명": "사업자 등록 후 정기 갱신",
        "청렴계약 이행서약서": "공공기관 거래 시 발행자 직인 첨부",
        "납품실적증명서": "PILOT·1차 도서관 도입 후 발급",
    }
