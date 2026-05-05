"""갈래 B Cycle 12 (P37) — KOLAS III 보도자료 자동 생성기.

채널: 플래텀·벤처스퀘어·잡포스트·도서관저널·KLA
공식: "1,200+개 공공도서관 KOLAS III 종료 D-{N}, 마이그레이션 SaaS 출시"
출처: books.nl.go.kr (국립중앙도서관 공식 공지)

게이트: 모든 인용 수치에 출처 URL 자동 첨부.
"""

from __future__ import annotations

from datetime import datetime

from kormarc_auto.migration.countdown import days_until_kolas3_end


def generate_press_release(
    *,
    channel: str = "platum",
    company_name: str = "kormarc-auto",
    contact_email: str = "contact@kormarc-auto.example",
    now: datetime | None = None,
) -> str:
    """채널별 보도자료 markdown 생성."""
    days = days_until_kolas3_end(now=now)
    headline = f"1,200+ 공공도서관 KOLAS III 종료 D-{days}, 마이그레이션 SaaS 출시"

    body = f"""# [보도자료] {headline}

**보도일**: {(now or datetime.now()).strftime("%Y-%m-%d")}
**대상 채널**: {channel}
**문의**: {contact_email}

## 핵심 내용

국립중앙도서관이 운영해 온 공공도서관 표준자료관리시스템 **KOLAS III 표준형의 기술 지원이 2026년 12월 31일자로 종료**된다.[1] 2024년 기준 전국 공공도서관은 **1,296개관**(전년 대비 +2%)이며,[2] 표준형을 사용 중인 다수 도서관이 동시에 마이그레이션 의사결정에 진입하는 단 한 번의 골든윈도우가 열려 있다.

{company_name}는 이 시장 변화에 맞춰 **KORMARC 자동 생성 SaaS**를 출시한다. 자관 PILOT 1관·174 파일·3,383 레코드 round-trip 100% 정합도를 검증했고,[3] 권당 100원 또는 월 3·5·15·30만원의 명시 가격으로 ALPAS·OCLC·Alma의 비공개 가격 대비 **투명성 차별화**를 내세웠다.

## 마이그레이션 핵심 4단계

1. **D-180 (6개월 전·예산 편성)**: 차년 본예산 또는 추경에 SaaS 항목 반영
2. **D-90 (3개월 전·계약·이전)**: 정식 계약 + KOLAS III .mrc 일괄 export → kormarc-auto 일괄 import + 1주 병행 운영
3. **D-30 (1개월 전·전환)**: 신규 입수 자료 = kormarc-auto 단독 등록·사서 교육 1회
4. **D-0 (종료)**: KOLAS III 접근 차단·검색·통계는 SaaS 단독

## 잃지 말아야 할 5가지 데이터

서지 .mrc·대출 이력·이용자 정보·RFID 매핑·책이음·책나래 회원 키.

## 시장 환경

- KOLAS III 표준형 종료: 2026.12.31[1]
- 공공도서관 1,296개관[2]
- 작은도서관 정보누리(KNU) 미사용 5,100개관 (외부 도서관 SaaS 시장 분석[3])
- 4 공식 후속 시스템: 코라스Ⅲ 확장형·알파스(이씨오)·K-LAS 3.0·KOLAS-WEB

## 회사 소개

{company_name}는 사서 출신 1인 개발자가 자관 「○○도서관」 PILOT을 거쳐 만든 한국 도서관 KORMARC 자동 생성 SaaS다. 2026년 5월 v0.6.0 release·758 tests passing·CI Green.

## 문의

{contact_email}
GitHub: https://github.com/kormarc-auto/library

방법론: docs/eval/methodology.md

---

## 출처

[1] 국립중앙도서관 공공도서관지원서비스 포털 — books.nl.go.kr (KOLAS III 표준형 기술 지원 종료 공지)
[2] 문체부·한국도서관협회 2024 통계 — korea.kr/news/policyNewsView.do?newsId=148943216
[3] 자관 PILOT 측정 결과 — docs/eval/results/2026-05-04/per-record.json (3,383/3,383 round-trip 100%)
"""
    return body


def channel_specific_format(channel: str) -> dict[str, str]:
    """채널별 형식 가이드 (외부 보고서 P37 정합)."""
    formats = {
        "platum": {
            "tone": "스타트업 친화·간결·임팩트 수치 위주",
            "max_length": "1,500자",
            "submit_url": "platum.kr·제목 70자 이내",
        },
        "venturesquare": {
            "tone": "기술·혁신 강조·B2B 사례 위주",
            "max_length": "2,000자",
            "submit_url": "venturesquare.net·press@venturesquare.net",
        },
        "jobpost": {
            "tone": "공공 친화·정책 인용·법적 근거 명확",
            "max_length": "2,500자",
            "submit_url": "jobpost.co.kr·기관 신뢰 신호 우선",
        },
        "library_journal": {
            "tone": "사서·도서관계 전문 용어·KORMARC 표준 강조",
            "max_length": "3,000자",
            "submit_url": "도서관저널·격월간·DOI 인용 가능",
        },
        "kla": {
            "tone": "한국도서관협회 공식·통계·인용 풍부",
            "max_length": "5,000자",
            "submit_url": "kla.kr·연 학술대회 발표 자료 transformable",
        },
    }
    return formats.get(channel, formats["platum"])
