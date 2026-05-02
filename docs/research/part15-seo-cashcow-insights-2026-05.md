# Part 15 — SEO·캐시카우 직결 인사이트 (2026-05)

> 출처: 2026 AI 앱 엔지니어링 통합 리포트 (사용자 제공) §5·§6 발췌 + kormarc-auto 적용 분석
> 작성: 2026-05-02
> **연계**: ADR-0007 (포트원), v0.4.35 (PG 어댑터), 영업 자료 11건

---

## 1. Streamlit SPA의 SEO 한계 — 사서 자연 유입 차단

kormarc-auto는 Streamlit 기반이라 **JavaScript 렌더링 후 DOM 생성** 구조다. 일반 검색 엔진 크롤러는 페이지 내용을 완전히 파악하지 못한다. 결과: "KORMARC 자동 생성", "KORMARC 변환 도구" 같은 핵심 검색어로 **자연 유입 0**.

### 즉시 적용 가능한 3축

#### 1-1. 동적 메타 태그 강제 주입 (streamlit_app.py)

```python
# streamlit_app.py 최상단
import streamlit as st

st.set_page_config(
    page_title="KORMARC 자동 생성 SaaS — 사서 시간 95% 절감",
    page_icon="📚",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "ISBN 입력만으로 KORMARC 통합서지 자동 생성. 9개 자료유형 지원."
    }
)

# 페이지별 description 동적 주입 (st.markdown으로 <meta> 직접 삽입)
st.markdown("""
<meta name="description" content="KORMARC 자동 생성 SaaS. ISBN 입력만으로 KOLAS·DLS 호환 .mrc 파일 즉시 생성. 자관 99.82% 정합 검증.">
<meta name="keywords" content="KORMARC, 자동 생성, KOLAS, 도서관 자동화, 사서 SaaS, BIBFRAME, 통합서지">
<meta property="og:title" content="KORMARC 자동 생성 SaaS">
<meta property="og:description" content="ISBN → KORMARC 즉시 변환. 사서 시간 95% 절감.">
<meta property="og:type" content="website">
""", unsafe_allow_html=True)
```

#### 1-2. 하이브리드 마케팅 페이지 — 정적 HTML 랜딩

이미 `landing/` 폴더 있음 (kormarc-auto/landing/). 이를 활용:
- **landing/index.html** — 정적 HTML, SEO 완벽 색인
- **타겟 키워드**: "KORMARC 자동 생성", "도서관 SaaS", "KOLAS 변환", "사서 매크로 대안"
- **CTA**: "지금 무료로 시작" → Streamlit 앱 URL로 redirect
- **백링크 확보**: 한국도서관협회·KLA·도서관 정보나루 게시판에 무료 가이드 글 + landing 링크

#### 1-3. 고유 서브도메인 안정화

배포 직후 임의 해시 URL을 그대로 두면 인덱싱 후 URL 변경 시 404 트래픽 유실. 권장:
- `kormarc.app` 또는 `kormarc.kr` 도메인 선점
- Streamlit Community Cloud → 커스텀 도메인 연결

---

## 2. 사서 대상 키워드 전략 (롱테일 우선)

구글·네이버 키워드 플래너 교차 분석 후 추출할 후보:

### 검색 의도별 키워드 매트릭스

| 의도 | 키워드 예시 | 경쟁도 | 적용 위치 |
|------|------------|--------|-----------|
| **문제 인지** | "KORMARC 008 필드 자동", "KOLAS 일괄 등록", "ISBN으로 서지 만들기" | 낮음 | 블로그·튜토리얼 |
| **솔루션 비교** | "KORMARC 자동 생성 도구", "도서관 자동화 SaaS 비교" | 중 | 비교 랜딩 페이지 |
| **구매 직전** | "KORMARC SaaS 가격", "KOLAS 변환 무료" | 낮음 | 가격 페이지 + Free Trial |
| **사용자 군별** | "사서교사 KORMARC", "공공도서관 자동화" | 매우 낮음 | 페르소나별 랜딩 |

### 자동화 가능 부분

이미 kormarc-auto가 가진 자산을 SEO로 변환:
- **자관 99.82% 검증 결과** → "KORMARC 정합 99.82% 달성 사례" 블로그
- **9개 자료유형 builder** → "도서·연속간행물·전자자료 자동 KORMARC" 각각 별도 페이지
- **PILOT 4주차 매뉴얼** → "도서관 SaaS 도입 4주 가이드" SEO 콘텐츠

---

## 3. 캐시카우 결제 흐름 — Stripe vs 포트원

ADR-0007에서 포트원 채택 결정. 받은 리서치는 Stripe 위주지만 핵심 패턴은 동일:

### Webhook 수신 → DB 플래그 업데이트 패턴

```python
# 이미 v0.4.35에서 구현됨 (CHANGELOG_NIGHT.md 확인)
# /webhook/portone POST endpoint ✅ b06f60e

# 추가 권장: Webhook 검증 강화
@app.post("/webhook/portone")
async def portone_webhook(request: Request):
    # 1. 서명 검증 (포트원 docs)
    signature = request.headers.get("x-portone-signature")
    if not verify_portone_signature(await request.body(), signature):
        raise HTTPException(403, "Invalid signature")

    # 2. 이벤트 처리 + idempotency
    event = await request.json()
    event_id = event.get("id")
    if await already_processed(event_id):
        return {"status": "duplicate"}

    # 3. 구독 상태 업데이트 → DB
    await update_subscription_status(event)
    await mark_processed(event_id)

    return {"status": "ok"}
```

### Streamlit st-paywall 대신 자체 인가 패턴

받은 리서치는 `st-paywall` 패키지를 권장하나, 이미 kormarc-auto는 자체 billing 모듈 보유. 패키지 대체보다 **기존 billing.py + payment_adapter.py 활용**이 낫다:

```python
# Streamlit 페이지에서 사용
def require_premium():
    user_id = st.session_state.get("user_id")
    status = check_subscription_status(user_id)  # billing.py 활용
    if status != "active":
        st.error("프리미엄 기능입니다. 결제 후 이용 가능합니다.")
        st.markdown(f"[결제하기]({get_payment_url(user_id)})")
        st.stop()
    # 프리미엄 기능 코드 ...
```

---

## 4. 영업 자료 → SEO 자산 전환

이미 만든 영업 자료 11건을 SEO 콘텐츠로 재활용:

| 기존 자료 | SEO 콘텐츠로 변환 |
|-----------|-------------------|
| `outreach-kolis-net-migration-2026-05.md` | 블로그: "KOLIS-NET에서 모던 도서관 SaaS로 마이그레이션 5단계" |
| `outreach-bibframe-lod-2026-05.md` | 블로그: "BIBFRAME 2.0 LOD 전환 가이드 — 한국 도서관 사례" |
| `data4library-guide-2026-05.md` | 블로그: "도서관 정보나루 API 활용 자동화 가이드" |
| PILOT 매뉴얼 4주차 | 가이드: "사서를 위한 SaaS 도입 4주 체크리스트" |

각 페이지에:
- 정적 HTML로 변환 (Streamlit 외부)
- 타겟 키워드 1~2개 집중
- kormarc-auto 메인 앱 링크 (CTA)
- 댓글·문의 폼 (lead capture)

---

## 5. 다음 액션 (우선순위)

| 우선순위 | 작업 | 예상 시간 | 평가축 |
|----------|------|-----------|--------|
| 1 | streamlit_app.py에 메타 태그 강제 주입 | 30분 | Q1 매출 의향 +1 (자연 유입 시작) |
| 2 | landing/index.html 핵심 키워드 4종 강화 | 1시간 | Q1 +2 |
| 3 | 영업 자료 4건 → 정적 HTML 블로그 변환 | 2시간 | Q1 +2, Q4 락인 +1 |
| 4 | 도메인 선점 (kormarc.app or kormarc.kr) | PO 작업 | Q1 +1 |
| 5 | Webhook 서명 검증 강화 | 1시간 | Q5 컴플라이언스 +1 |

> **합계 시간**: 약 4.5시간 (도메인 제외)
> **예상 효과**: 자연 유입 0 → 월 50~200 사서 검색 트래픽 (롱테일 키워드 기준)

---

## 참고

- 원본 리서치: `바이브코딩 지식/참고자료/리서치_원본_2026/2026_ai_app_engineering_integrated.md`
- 관련 ADR: 0007 (포트원), 0011 (managed stack)
- 관련 영업 자료: `kormarc-auto/docs/sales/` 11건
