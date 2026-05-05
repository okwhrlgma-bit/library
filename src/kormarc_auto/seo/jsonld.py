"""갈래 B Cycle 15B (P35) — JSON-LD 생성기 (SoftwareApplication·FAQPage·Organization).

외부 매출 보고서 §5 + P35:
- SoftwareApplication 5단 Offer KRW 명시 (ALPAS·Alma 비공개 대비 차별화)
- FAQPage 10선 (KOLAS III 종료·독서로 DLS·880 한자 등)
- Organization sameAs (네이버 블로그·LinkedIn·브런치 연결)
- AI Overviews 인용 가능성 ↑ (76.1% = 구글 Top 10 정합)
"""

from __future__ import annotations

from typing import Any

from kormarc_auto.billing import list_plans


def build_softwareapplication_jsonld(
    *,
    company_name: str = "kormarc-auto",
    site_url: str = "https://kormarc-auto.example",
) -> dict[str, Any]:
    """SoftwareApplication JSON-LD (5단 Offer·KRW 명시)."""
    plans = list_plans()
    offers = []
    for p in plans:
        if p.code == "free":
            offers.append(
                {
                    "@type": "Offer",
                    "name": p.label,
                    "price": "0",
                    "priceCurrency": "KRW",
                    "description": p.description,
                }
            )
            continue
        offers.append(
            {
                "@type": "Offer",
                "name": p.label,
                "price": str(p.monthly_krw),
                "priceCurrency": "KRW",
                "billingIncrement": "P1M",
                "description": p.description,
            }
        )

    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": company_name,
        "applicationCategory": "BusinessApplication",
        "applicationSubCategory": "LibraryAutomation",
        "operatingSystem": "Web (Windows·macOS·Linux)",
        "url": site_url,
        "description": (
            "한국 도서관 사서를 위한 KORMARC 자동 생성 SaaS·"
            "ISBN 1번 입력 5초·KOLAS III·DLS·알파스 즉시 반입·"
            "자관 PILOT 1관 round-trip 100% 검증"
        ),
        "inLanguage": "ko",
        "offers": offers,
        "aggregateRating": None,  # 베타 기간·실 사서 후기 누적 후 추가
        "softwareVersion": "0.6.0",
        "datePublished": "2026-05-04",
    }


def librarian_faq_10() -> list[dict[str, str]]:
    """사서 핵심 FAQ 10선 (FAQPage schema + AI 인용 친화)."""
    return [
        {
            "question": "KOLAS III 표준형은 언제 종료되나요?",
            "answer": (
                "2026년 12월 31일 자로 공공도서관 표준자료관리시스템(KOLAS III) 표준형의 "
                "기술 지원이 종료됩니다 (국립중앙도서관 공식 공지·books.nl.go.kr). "
                "확장형은 별도 트랙으로 유지됩니다."
            ),
        },
        {
            "question": "kormarc-auto는 KOLAS III와 호환되나요?",
            "answer": (
                "네. KOLAS III .mrc 일괄 export → kormarc-auto 일괄 import 절차를 지원합니다. "
                "round-trip 100% 정합 (자관 PILOT 1관·174 파일·3,383 레코드 검증)."
            ),
        },
        {
            "question": "독서로 DLS에 자동 반입되나요?",
            "answer": (
                "네. 독서로 DLS·KOLAS·알파스 호환 .mrc를 자동 생성합니다. "
                "ISBN을 파일명으로 한 .mrc 출력 → 반입 폴더 자동 인식 (cp949·utf-8·euc-kr fallback)."
            ),
        },
        {
            "question": "880 한자 병기는 자동인가요?",
            "answer": (
                "네. 한자 감지 시 880 페어 자동 생성. NLK 「서지데이터 로마자 표기 지침(2021)」 정합 "
                "(RR 기본·MR 학술)."
            ),
        },
        {
            "question": "권당 가격은 얼마인가요?",
            "answer": (
                "권당 100원 또는 월 정액 (작은도서관 ₩30,000·학교 ₩50,000·공공 ₩150,000·기관 ₩300,000~). "
                "VAT 별도·연 결제 시 17% 할인 (2개월 무료)·5/10/25/100관 묶음 할인."
            ),
        },
        {
            "question": "사서 검토 단계는 어떻게 작동하나요?",
            "answer": (
                "AI 생성 필드는 ghost text(흐린 회색 italic)로 표시되고 사서가 ✓ 클릭 시 정상 표시. "
                "필드별 accept/reject/edit 가능·전체 거부 escape hatch·KORMARC 588 자동 stamp."
            ),
        },
        {
            "question": "AI 환각이 걱정됩니다. 어떻게 대응하나요?",
            "answer": (
                "결정론 보장 (temperature=0·top_p=1·모델 pinning·ADR 0028)·동일 입력 = 동일 출력. "
                "신뢰도는 카테고리(확실·검토 필요·불확실)로 표시·raw % 노출 X. "
                "6XX 주제명 등 환각 위험 영역은 사서 우선 검토 권장."
            ),
        },
        {
            "question": "개인정보·국외이전 정책은요?",
            "answer": (
                "처리방침 §9 = §28의8 6항목 (Anthropic·AWS·PortOne·Google·Cloudflare 5수신자) 명시. "
                "PIPC 결정 2024-010-184 정합·동의 갈음 근거 명시."
            ),
        },
        {
            "question": "30초 데모가 가능한가요?",
            "answer": (
                "네. API 키 0개로 KORMARC_DEMO_MODE=1 kormarc-auto demo 명령 = "
                "SAMPLE 7건 + SENTINEL 5건·외부 호출 0건·5/5 records·round-trip 100%."
            ),
        },
        {
            "question": "자치구 묶음 도입 할인은?",
            "answer": (
                "5개관 10%·10개관 15%·25개관 20%·100+개관 25% 묶음 할인. "
                "Founding Member (~2026-06-30·100관 한정·연간결제 의무·LTD 금지) 영구 50% 추가 가능."
            ),
        },
    ]


def build_faqpage_jsonld(faqs: list[dict[str, str]] | None = None) -> dict[str, Any]:
    """FAQPage JSON-LD (10선·AI 인용 친화)."""
    if faqs is None:
        faqs = librarian_faq_10()
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q["question"],
                "acceptedAnswer": {"@type": "Answer", "text": q["answer"]},
            }
            for q in faqs
        ],
    }


def build_organization_jsonld(
    *,
    company_name: str = "kormarc-auto",
    site_url: str = "https://kormarc-auto.example",
    same_as: list[str] | None = None,
) -> dict[str, Any]:
    """Organization JSON-LD (sameAs로 네이버 블로그·브런치·LinkedIn 연결)."""
    if same_as is None:
        same_as = [
            "https://blog.naver.com/kormarc-auto",
            "https://brunch.co.kr/@kormarc-auto",
            "https://github.com/kormarc-auto/library",
        ]
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": company_name,
        "url": site_url,
        "logo": f"{site_url}/logo.png",
        "description": "한국 도서관 KORMARC 자동 생성 SaaS·사서 출신 1인 개발자",
        "inLanguage": "ko",
        "sameAs": same_as,
    }
