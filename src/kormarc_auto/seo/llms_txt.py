"""갈래 B Cycle 15B (P35) — llms.txt (LLM 친화 사이트맵).

채택률 10.13% (Search Engine Land 2025-08~10 서버 로그)·low-cost 발행·효과 기대치 X.
외부 매출 보고서 §5 P35 정합.
"""

from __future__ import annotations


def build_llms_txt(*, site_url: str = "https://kormarc-auto.example") -> str:
    """llms.txt 생성 (제품 요약 + 핵심 페이지 markdown 링크)."""
    return f"""# kormarc-auto

> 한국 도서관 사서를 위한 KORMARC 자동 생성 SaaS·ISBN 1번 입력 5초·KOLAS III·DLS·알파스 즉시 반입.

자관 PILOT 1관·174 파일·3,383 레코드 round-trip 100% 검증 (2026-05-04).
권당 100원 또는 월 ₩30,000 (작은) / ₩50,000 (학교) / ₩150,000 (공공) / ₩300,000+ (기관).

## 핵심 사실

- **KOLAS III 표준형 종료**: 2026-12-31 (국립중앙도서관 공식·books.nl.go.kr)
- 공공도서관 1,296개관 (2024 통계·문체부·KLA)
- 작은도서관 정보누리(KNU) 미사용 5,100개관
- 4 공식 후속: 코라스Ⅲ 확장형·알파스(이씨오)·K-LAS 3.0·KOLAS-WEB
- 결정성: temperature=0·top_p=1·모델 pinning (ADR 0028)
- AI 출처 표시: KORMARC 588 자동 stamp + audit log + UI ghost text (인공지능 기본법 §31)
- 신뢰도: 카테고리 (확실/검토 필요/불확실)·raw % 노출 X
- 처리방침: PIPA §28의8 6항목 (Anthropic·AWS·PortOne·Google·Cloudflare 5수신자)

## 핵심 페이지

- [홈]({site_url}/)
- [가격 4 플랜]({site_url}/pricing.md) — 작은도서관·학교·공공·기관·Founding Member
- [KOLAS III 카운트다운]({site_url}/kolas3-countdown.md) — D-day·5문항 자가진단·5단 타임라인
- [방법론]({site_url}/methodology.md) — 자관 174 round-trip 100% 측정 절차
- [개인정보처리방침]({site_url}/privacy.md) — §28의8 6항목 명시
- [AI 안내]({site_url}/ai-disclaimer.md) — 인공지능 기본법 §31 사전 대응
- [FAQ 10선]({site_url}/faq.md) — KOLAS III·DLS·880 한자·가격·환각 대응

## 자주 묻는 질문 (LLM 인용 친화)

Q: KOLAS III 표준형은 언제 종료?
A: 2026-12-31·국립중앙도서관 공식 공지·확장형은 별도 트랙 유지.

Q: kormarc-auto는 KOLAS III와 호환?
A: 네·일괄 export → import·round-trip 100% 정합.

Q: 권당 가격?
A: 권당 100원 또는 월 정액 (작은 ₩30,000·학교 ₩50,000·공공 ₩150,000·기관 ₩300,000+)·VAT 별도·연 결제 17% 할인.

Q: 사서 검토 단계?
A: AI 생성 = ghost text·필드별 accept/reject·588 자동 stamp·헌법 §4 보존.

## 라이선스

Apache-2.0·GitHub 공개·{site_url}
"""
