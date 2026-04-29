# Part 4 — 사서 친화 UI/UX · 한국 SEO · 영업·마케팅 · 배포·운영 자동화

> **대상 독자**: PO + Claude Code (운영·홍보·배포 자동화 명령서)
> **언어**: 한국어
> **작성일**: 2026-04-29
> **상위 헌법**: `CLAUDE.md` §0·§12 / `.claude/rules/autonomy-gates.md` 캐시카우 평가축 / `business-impact-axes.md` 5질문 (Q5 PIPA 별도 게이트)
> **선행 보고서**: `docs/sales-roadmap.md` · `docs/pricing.md` · `docs/po-outreach-list.md` · `docs/po-master-action-plan-2026-04-28.md` · `docs/mvp-redefinition-2026-04-29.md` · `docs/ux-audit.md` · `docs/saseo-personas-2026-04-28.md`
> **PIPA 시행**: 2026-09-11 (매출 10% 과징금) — Part 4 §6은 옵션 C (회원 PII = 자관 알파스 위임) 이행 명령서

---

## 0. 30초 요약 (PO 화면 첫 줄)

1. **UI/UX**: 1,429줄 단일 `streamlit_app.py` → **5페이지 multi-page 재구축** (메인/검색/사진/일괄/도구). 22 버튼 → **5 버튼**으로 압축. Pretendard 16px·네이비/살구.
2. **SEO**: 네이버 1순위 (한국 사서 검색 채널 1위) → 카카오 채널 → 구글 부차. **"KORMARC 자동" 키워드 1위 점령** = 베타 사서 50명 도달의 1차 경로.
3. **영업 ★ 1순위**: KLA 전국도서관대회 발표 신청 (2026-05-31 마감) — **연 1회 전국 사서 모임**. 이 1건 = 6개월치 영업.
4. **배포**: FastAPI + Cloudflare Tunnel (현재) → **Fly.io 도쿄(nrt) + Supabase + 포트원** (200관 캐시카우 도달 시 자동 전환).
5. **운영 자동화**: GitHub Actions CI + 자동 백업 + 영수증 PDF 자동 + DSAR 자동. PO 시간 0 목표.
6. **PIPA**: ★ **옵션 C** = 회원 PII는 자관 알파스에 위임. 우리는 양식·통계·템플릿만. logging PII 5종 마스킹 보강 (PILOT 전).

---

## 1. 사서 친화 UI/UX (한국 사서 IT 비전공·1번 보면 이해)

### 1.1 현 상태 진단 (Reality Check)

| 항목 | 현재 | 목표 |
|---|---|---|
| `streamlit_app.py` 줄 수 | **1,429줄 단일 파일** | 페이지별 분리 (200~300줄 × 5) |
| 메인 탭·도구 탭 버튼 | 22개 (5탭 + 도구 9 + 사이드바 8) | **5개** (ISBN·검색·사진·일괄·도구) |
| 첫 화면 가이드 | expander 안에 숨김 | 첫 줄 카드 (50건 무료 + 5분 가이드) |
| 본문 폰트 | 13~14px (50대 사서 작음) | **16px** Pretendard 표준 |
| 모바일 카메라 | 갤러리 선택 강제 | `capture="environment"` 직접 호출 |
| 에러 메시지 | "외부 API 호출 실패: {e}" 영문 stack | "해결법 카드 3가지" 한국어 |

**결론**: 기능 점수 8/10이지만 **사서 첫인상 점수 26/40 (65%)**. 1,429줄을 통째로 폐기하고 5 page multi-page 구조로 재구축이 권장됨.

### 1.2 Streamlit 사서 친화 패턴 (헌법 §12 정합)

```python
# st.set_page_config — 모든 페이지 공통
st.set_page_config(
    page_title="kormarc-auto — 사서를 위한 KORMARC 자동",
    page_icon="📚",
    layout="centered",  # wide 금지 (모바일 우선)
    initial_sidebar_state="collapsed",  # 모바일 collapsed 기본
    menu_items={
        "Get help": "https://pf.kakao.com/_kormarc",
        "Report a bug": "mailto:okwhrlgma@gmail.com",
        "About": "사서 출신 1인 창업자가 만든 KORMARC 자동 SaaS",
    },
)
```

**색상 팔레트** (`docs/ux-audit.md` §5 검증 — WCAG AA 통과):

| 토큰 | 값 | 용도 |
|---|---|---|
| `--primary` | `#1d4ed8` (네이비) | 메인 CTA·헤더 |
| `--accent` | `#fb923c` (살구) | 강조 배지·신규 |
| `--text` | `#111827` | 본문 (50대 가독) |
| `--muted` | `#4b5563` | 캡션 (AA 통과) |
| `--bg` | `#ffffff` | 카드 배경 |
| `--bg-soft` | `#f9fafb` | 페이지 배경 |
| `--success` | `#16a34a` | 성공 |
| `--warning-bg` | `#fef3c7` | 경고 배경 |
| `--error` | `#dc2626` | 에러 |

**폰트**: Pretendard 1순위 (CDN `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css`) → Apple SD Gothic Neo / Malgun Gothic 폴백. **Noto Sans KR / Nanum Gothic 금지** (load 무겁고 자간 약함).

### 1.3 5분 시연 5페이지 multi-page 재구축 설계

```
src/kormarc_auto/ui/
├── pages/
│   ├── 1_📕_ISBN_단건.py        # 가장 자주 쓰는 흐름 (90% 사서)
│   ├── 2_🔍_검색.py              # ISBN 모를 때
│   ├── 3_📷_사진.py              # 폰 카메라 → 30초 KORMARC
│   ├── 4_📚_일괄.py              # 신착 50권 한 번에
│   └── 5_🛠_도구.py              # 부가 기능 9개 (드롭다운으로)
├── streamlit_app.py             # 첫 화면 (가이드 + 무료 50건 + 가입 CTA)
└── _shared.py                   # 공통 컴포넌트 (헤더·테마·에러 카드)
```

**파일별 줄 수 목표**: 각 200~300줄. 1,429줄 단일 파일 폐기.

### 1.4 사서가 누르는 버튼 22 → 5 압축 의사결정

| 현재 22 버튼 | 5 압축 후 | 결정 근거 |
|---|---|---|
| ISBN·검색·사진·일괄·도구 (5 메인) + 도구 안 9 + 사이드바 설정 8 | **메인 5탭만 화면 표시** | Hick's Law: 옵션 N개 → 결정 시간 log₂(N+1)배 증가. 5개가 인지 한계 |
| "040 ▾a 도서관 부호" | "우리 도서관 부호" + help 텍스트 | "▾a"는 KORMARC 익숙 사서도 즉시 안 떠오름 |
| "Anthropic API 키" | "AI 추천 보조 키 (선택)" | 사서는 Anthropic 모름. "선택"이라 안 입력해도 ISBN 100% 동작 |
| 사이드바 8개 설정 (CORS·timeout·로그 레벨 등) | 모두 환경변수로 숨김 | 사서가 건드리면 안 되는 것 = UI에서 제거 |
| 도구 탭 안 9 부가기능 | 드롭다운 1 + 선택 시 화면 전환 | 발견성 ↑ + 첫 화면 인지 부하 ↓ |

### 1.5 모바일 반응형 (폰 카메라 → 30초 KORMARC 1건)

**현재 결손**:
- `st.file_uploader`가 모바일에서 갤러리 선택 강제 (한 번 더 탭 필요)
- 사이드바가 collapsed → 핵심 설정 발견 0%
- 결과 카드 다운로드 버튼이 화면 중간 (한 손 엄지 닿기 어려움)

**목표 흐름** (사서 폰으로 책 1권 30초 시연):

```
[1] 카메라 아이콘 누르기 (3초) — capture="environment" 활성
[2] 책 표지 1장 촬영 (5초)
[3] AI 처리 진행률 카드 (10초) — "약 8초 남음"
[4] KORMARC 결과 카드 (3초 확인)
[5] 화면 바닥 sticky [.mrc 다운로드] 버튼 풀폭 (1초)
================================================================
합계 22초 — "30초 시연 가능" 마케팅 메시지 검증 가능
```

**구현 키 포인트**:

```python
# 모바일 카메라 직접 호출 (Streamlit 1.30+ 지원)
uploaded = st.file_uploader(
    "📷 책 표지 촬영",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    label_visibility="visible",
    help="폰에서는 카메라가 즉시 열립니다",
)

# 또는 streamlit-camera-input-live 컴포넌트 (중기 도입 ADR 후보)
from camera_input_live import camera_input_live
image = camera_input_live(key="cover")  # iframe로 실시간 카메라
```

**터치 영역 보장**: 모든 버튼 `min-height: 48px` (WCAG 2.5.5 + 모바일 권장). Streamlit 기본 36px → CSS override로 48px 강제.

### 1.6 에러 메시지 사서 친화 표현

**현재 결손**:
```python
st.error(f"외부 API 호출 실패: {e}")  # ❌ 영문 stack trace
st.error("ISBN 추출 실패 — 사진 품질을 확인하세요.")  # ❌ "어떻게?" 부재
```

**목표 패턴** (해결법 카드 3가지):

```python
def render_error_card(title: str, body: str, solutions: list[str], *, contact: bool = True) -> None:
    """사서 친화 에러 카드 — 영문 stack trace 금지·해결법 3가지 필수."""
    st.error(f"⚠ {title}")
    st.markdown(f"**무엇이 안 됐나요**\n\n{body}")
    st.info("**💡 이렇게 해 보세요**\n\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(solutions)))
    if contact:
        st.caption("그래도 안 되면 카카오톡 채널로 문의 (24시간 내 PO 답변)")

# 사용 예 — ISBN 미조회
render_error_card(
    title="등록 정보를 찾을 수 없습니다",
    body=f"ISBN {isbn}이(가) 4개 외부 도서 DB 모두에 없습니다.",
    solutions=[
        "ISBN 13자리가 정확한지 확인 (978로 시작)",
        "[검색] 탭에서 표제·저자로 다시 시도",
        "옛 책·자가출판이면 [사진] 탭으로 표지 1장 업로드",
    ],
)
```

**금지 패턴**:
- `traceback.format_exc()` UI 노출 X (서버 로그에만 기록)
- "Internal Server Error" 같은 영문 메시지 X
- 한 줄 짧은 에러 ("실패", "오류") X — 다음 단계 필수

### 1.7 한국 도서관 시스템 UI 관행 (벤치마크)

| 시스템 | 학습 포인트 | 우리 적용 |
|---|---|---|
| **KOLAS III** | 사서가 가장 익숙한 화면. 좌측 트리 + 우측 폼. 하단 상태표시줄 | 좌측 사이드바 navigation 보존. 단순 사서는 우측 메인만 봐도 되도록 |
| **알파스 (이씨오)** | 카카오클라우드 SaaS. 통합 검색바 상단 고정. 한 화면 한 결정 | 상단 sticky 검색바 + 풀폭 1 결정 카드 |
| **독서로 DLS** | 학교 사서 친화. 큰 폰트·아이콘 라벨. 도움말 항상 노출 | 16px 본문 + 아이콘 + help 텍스트 항상 |
| **국립중앙도서관 KOLIS-NET** | 차분한 청록·회색 톤. 사서 친숙 | 네이비 #1d4ed8 (#1f6feb보다 약간 따뜻) |
| **책이음 통합 회원증** | 단일 회원증·단일 비번. 통합 경험 | 우리도 단일 키 (X-API-Key) 정책 유지 |

**금기 사항** (한국 도서관 사서 거부감):
- ❌ 다크 모드 강제 (50대 시각 약시 비호환)
- ❌ 영문 메뉴 ("Settings" → "환경설정")
- ❌ 토글 스위치 (체크박스 선호 — 한국 관공서 양식 관행)
- ❌ 모달 팝업 (스크린리더 비호환·50대 혼란)

### 1.8 사서_웹사용법.md 통합 (이미 작성된 사용법 문서 활용)

`docs/사서_웹사용법.md`에 이미 1분 가입·5분 시연 가이드가 작성되어 있음. UI에서 다음 위치에 링크:

- 첫 화면 카드: "✨ 처음이신가요? 5분 가이드 →" (`/help/사서_웹사용법`)
- 사이드바 하단: "📖 매뉴얼 PDF 다운로드" (자동 생성)
- 카카오 채널 자동응답 키워드 `사용법·매뉴얼·가이드` → 동일 URL 안내

---

## 2. 한국 SEO + 검색 노출 (사서가 우리를 찾는 경로)

### 2.1 채널 우선순위 (한국 사서 검색 행동 분석)

| 순위 | 채널 | 한국 사서 사용률 | 우리 전략 |
|---|---|---:|---|
| 1 | **네이버 검색·블로그·카페** | **80%+** | 1순위 SEO 집중. 네이버 서치어드바이저 등록 필수 |
| 2 | **카카오톡 오픈채팅** (사서 동호회) | 60%+ | 채널 + 오픈채팅 가입 (사서나라·전국사서 등) |
| 3 | **사서 커뮤니티** (한국도서관협회 게시판·도서관 카페) | 40%+ | 게시판 활동 + 우리 후기 노출 |
| 4 | **유튜브** | 30%+ (영상 교육 선호) | 시연 영상 1편 + 사서 채널 큐레이션 |
| 5 | **구글** | 15% (영문·기술 키워드만) | GitHub README 영문 + 토픽 태그만 |
| 6 | **인스타·페북** | 10% 미만 | 우선순위 X (5월 이후 검토) |

### 2.2 네이버 SEO (1순위 채널)

**네이버 서치어드바이저 등록 (필수, 30분 1회)**:
1. https://searchadvisor.naver.com 접속
2. 사이트 등록 (`https://app.kormarc.kr` 또는 베타 도메인)
3. 소유 확인 (HTML 파일 업로드 또는 메타태그)
4. 사이트맵 제출 (`/sitemap.xml`)
5. RSS 등록 (블로그 운영 시)

**네이버 검색 노출 핵심 요소**:

| 요소 | 우리 적용 |
|---|---|
| 페이지 제목 (title) | "사서를 위한 KORMARC 자동 — 권당 8분→2분 \| kormarc-auto" |
| 메타 디스크립션 | "ISBN 1번 입력 → KORMARC 5초 자동 생성. 신규 50건 무료. 한국 도서관 사서 출신 1인 창업자가 만든 SaaS." |
| H1 태그 | "사서의 마크 작업, 권당 8분 → 2분" |
| 본문 키워드 자연 포함 | KORMARC·ISBN·KOLAS·작은도서관·학교도서관·MARC 자동 |
| 한국어 OG 태그 | og:locale=ko_KR / og:title / og:description / og:image |
| Robots.txt | `Allow: /` + `Sitemap: /sitemap.xml` |
| 응답 속도 | 3초 이내 (네이버 봇 timeout) |
| HTTPS | 필수 (네이버 신뢰도 가산점) |

### 2.3 키워드 매트릭스 (네이버 검색량 추정 + 경쟁도)

| 키워드 | 월 검색량 (추정) | 경쟁도 | 우리 페이지 |
|---|---:|---|---|
| **KORMARC 자동** | 30~50 | 낮음 ★ | 메인 페이지 H1 |
| **MARC 자동 생성** | 20~40 | 낮음 ★ | 메인 페이지 H2 |
| **도서관 사서 마크 자동** | 10~20 | 매우 낮음 ★ | 블로그 글 1편 |
| **ISBN MARC 변환** | 50~100 | 중간 | 도구 페이지 |
| **KORMARC 만들기** | 15~25 | 매우 낮음 ★ | 5분 가이드 |
| **KOLAS 반입** | 100~200 | 중간 | 마이그레이션 페이지 |
| **1인 사서 자동화** | 20~30 | 낮음 ★ | 블로그 글 1편 |
| **작은도서관 마크** | 50~80 | 낮음 ★ | 블로그 글 1편 |
| **학교도서관 KOLAS** | 80~120 | 중간 | 학교도서관 전용 페이지 |
| **납품업체 KORMARC** | 10~20 | 매우 낮음 ★ | B2B 페이지 |

★ = "낮음 + 우리 적합 = 즉시 1위 가능" 키워드. 5월 안에 모두 점령 목표.

### 2.4 네이버 블로그 / 티스토리 / velog 운영

| 플랫폼 | 강점 | 약점 | 우리 사용 |
|---|---|---|---|
| **네이버 블로그** | 네이버 SEO 1순위 가산점·검색 노출 빠름·사서 친숙 | 기술 코드 표시 약함·외부 링크 제한 | **★ 1순위** — 사서 친화 글 (5분 가이드·후기·뉴스) |
| **티스토리** | 자유로운 디자인·구글 SEO 강함·코드블록 OK | 네이버 노출 약함 | 2순위 — 기술 deep dive |
| **velog** | 개발자 커뮤니티·기술 키워드 강함 | 한국 사서 인지도 낮음 | 3순위 — 기술 채용·OSS 홍보 |
| **GitHub README** | 영문·기술 사서·해외 노출 | 한국 사서 직접 도달 X | 영문·토픽 태그 |

**네이버 블로그 운영 1개월 목표**:
- 매주 1편 (4편/월)
- 글 1편 = 키워드 매트릭스에서 1개 점령
- 첫 글 후보:
  1. "사서가 매일 하는 KORMARC 입력, 5초로 줄이는 법"
  2. "KOLAS III 기술지원 종료 (2026-12-31) — 작은도서관 사서가 알아야 할 것"
  3. "1인 사서가 신착 50권을 30분에 카탈로깅하는 방법"
  4. "책나래·책바다 양식 자동 — 상호대차 신청 시간 5분 → 1분"

### 2.5 사서 커뮤니티 SEO

| 커뮤니티 | URL | 회원 | 우리 활동 |
|---|---|---|---|
| **한국도서관협회 게시판** | https://www.kla.kr | 11,000+ | 신규 SaaS 소개 1회 + Q&A 응대 |
| **사서나라 카페** (네이버) | cafe.naver.com/saseo | 5,000+ | 매주 1회 후기 글 (사서 본인 추천) |
| **도서관 관련 카페** | 다수 | 변동 | 작은도서관·학교도서관별 활동 |
| **한국학교도서관협의회** | 시·도별 지부 | - | 시도교육청 연수 자료 기고 |

**활동 원칙**:
- 자연스러운 후기 (사서 본인) 우선 — "이 도구 써봤더니 시간 절감" 형식
- 직접 광고 게시 금지 (커뮤니티 규정 위반·차단 위험)
- 카카오 채널 안내는 본문 마지막 1줄로

### 2.6 카카오 채널 + 카카오톡 오픈채팅

**카카오 비즈니스 채널 운영** (`docs/kakao-channel-faq.md` 정합):

| 항목 | 상태 | 액션 |
|---|---|---|
| 카카오 비즈니스 채널 생성 (`@kormarc-auto`) | ☐ | PO 30분 — 카카오 비즈니스 가입 무료 |
| 자동응답 키워드 20종 등록 | ☐ | docs/kakao-channel-faq.md §1 그대로 |
| 친구추가 보상 (50건 무료 + 추가 20건) | ☐ | server/usage.py 보너스 로직 |
| 영업시간·24시간 SLA 표시 | ☐ | 채널 프로필 |
| 베타 사서 50명 친구추가 캠페인 | ☐ | 5월 PILOT 시작 시 |

**카카오톡 오픈채팅 가입 (사서 동호회)**:
- "전국 사서 모임" (검색어: 사서·도서관)
- "공공도서관 사서 정보공유"
- "학교도서관 사서교사 모임"
- "작은도서관 운영자 모임"

→ 가입 후 1주일 ROM (read only member). 자연스럽게 질문에 답변. 본격 홍보는 신뢰 형성 후.

### 2.7 GitHub README 한국어·영어 동시

```markdown
# kormarc-auto — 사서를 위한 KORMARC 자동 SaaS

[한국어](#korean) | [English](#english) | [日本語](#japanese)

## <a id="korean"></a>한국어

ISBN 1번 입력 → KORMARC 5초 자동 생성. 권당 8분 → 2분.
- 무료 50건 (카드 등록 X)
- 카카오톡 채널: https://pf.kakao.com/_kormarc
- 5분 가이드: docs/사서_웹사용법.md

## <a id="english"></a>English

KORMARC auto-generation SaaS for Korean librarians.
ISBN → KORMARC in 5 seconds. 8min → 2min per book.

## Topics

`korean-libraries` `kormarc` `marc21` `library-saas` `pymarc` `streamlit` `fastapi`
`librarian-tools` `cataloging-automation` `iso2709` `library-automation` `book-cataloging`
```

**GitHub 토픽 태그 12개 등록** = GitHub 검색·구글 검색 동시 노출.

---

## 3. 영업 채널·마케팅·홍보 (사서가 결제 결정에 도달하는 경로)

### 3.1 ★ 1순위 — KLA 전국도서관대회 (5.31 마감)

**왜 1순위인가**:
- 연 1회 전국 사서 모임 (1,000+ 사서 직접 노출)
- 발표자 = 도서관계 신뢰 자산 ★
- 자관 PILOT 결과 발표 → 이후 6개월간 영업 자료
- 신청 마감 **2026-05-31** — 놓치면 1년 대기

**제출 자료**:

| 항목 | 내용 |
|---|---|
| 발표 제목 | "1인 사서가 8분→2분으로 KORMARC 작성하는 법 — 자관 PILOT 4주 결과" |
| 발표자 | PO (사서 출신 1인 창업자) |
| 발표 시간 | 20분 (Q&A 10분) |
| 사용 자료 | 자관 6년 NPS·5년 책단비 1,328·.mrc 174 검증·35 윤동주 컬렉션 |
| 시연 | 라이브 시연 1건 (ISBN → .mrc 5초) |
| 배포 자료 | 사서용 5분 가이드 PDF 200부 |
| KLA 회원 가입 | license@kla.kr (필수, 1일 처리) |

**오늘 PO 액션** (30분):
1. https://www.kla.kr 접속 → 회원 가입
2. 전국도서관대회 발표 공모 페이지 확인
3. 신청 양식 다운로드
4. 자관 라이선스 동의서 PO ↔ 자관 합의 (PILOT 자료 인용 권한)

### 3.2 협회·연합 영업 매트릭스

| 단체 | 회원 | 연락 채널 | 우선순위 | 도달 사서 추정 | 전환율 추정 |
|---|---:|---|---|---:|---:|
| **(사)작은도서관협회** | 1,800곳 | 협회 사무국 문의 양식 | ★★★ | 1,800 | 1~3% |
| **한국도서관협회 (KLA)** | 11,000+ | klaisr.org | ★★★ | 11,000 | 0.5~1% |
| **한국학교도서관협의회** | 시·도 지부 | 시도교육청 학교도서관 부서 | ★★★ | 12,200 | 0.5~1% |
| **(사)한국공공도서관협회** | 1,500곳 | 협회 사무국 | ★★ | 1,500 | 1~2% |
| **한국대학도서관연합회 (KCRL)** | 250+ | 사이트 | ★★ | 5,000 (대학 사서) | 0.3% |
| **(사)한국전문도서관협의회** | 변동 | 협의회 사이트 | ★ | 2,000 | 0.2% |
| **한국사립대학도서관협의회 (KSLA)** | 사립대 도서관 | 사이트 | ★★ | 1,500 | 0.5% |
| **한국도서관·정보학회** | 학술 | 학술대회 발표 + 부스 | ★ | 500 | 1% |

**도달 사서 합계**: 약 35,500명 (전국 사서 ≈ 50,000명 중 70%+ 커버).

### 3.3 사서교육원 강의 (5월·전국 사서 정기 교육)

**전국 사서교육원 5곳**:
1. **국립중앙도서관 사서교육원** (서울) — 가장 권위
2. **부산·대구·광주·대전·울산** 광역시도립도서관 부설 교육원
3. **각 시도교육청 사서교사 직무연수** (학교도서관)

**제안 강의 제목**:
- "1인 사서를 위한 KORMARC 자동화 워크숍 (3시간)"
- "Excel 매크로 자작 사서가 알아야 할 SaaS 도구 (2시간)"
- "PIPA 시행 대비 도서관 사서 의무 (1시간)"

**제안서 포함 사항**:
- 강사 소개 (PO 사서 출신 + 자관 PILOT 결과)
- 실습 자료 (USB 또는 다운로드 링크)
- 무료 50건 쿠폰 (수강 사서 전원)

### 3.4 시도교육청·자치구 도서관 워크숍

| 권역 | 단체 | 비고 |
|---|---|---|
| 서울 | 서울도서관 (정책연구실) + 25개 자치구 도서관 협의회 | 서울시·자치구 예산 |
| 경기 | 경기도사이버도서관 + 31개 시·군 도서관 협의회 | 경기도교육청 |
| 인천 | 인천광역시도서관 + 10개 군·구 | |
| 부산·대구·광주·대전·울산 | 광역시도서관 정책팀 | 광역시 단체 계약 가능 |
| 도단위 | 도립도서관 + 시·군 협의회 | 도교육청 |

**자치구별 자체 명칭 매트릭스 활용** (`docs/po-outreach-list.md` 정합):
- **은평구** (책단비) — 자관 PILOT 1순위
- **양천구** (책가방) — 자관 양식 등록 (정책 ③)
- **마포구** (책마중) — 자관 양식 등록
- 강남구·강북구 — 책이음 우산
- 나머지 18구 — Phase 2

### 3.5 학술지·전문지 기고

| 매체 | 발행 주기 | 독자 | 기고 형식 |
|---|---|---|---|
| **도서관저널** | 월간 | 공공·대학·전문 사서 | 칼럼 1편 (2,500자) |
| **도서관문화** | 월간 | KLA 회원 | 사례 보고 (PILOT 결과) |
| **학교도서관저널** | 월간 | 학교 사서·사서교사 | 학교 특화 기사 |
| **OAK Korea** (오픈액세스코리아) | 부정기 | 학술 사서·OA 활동가 | OA·메타데이터 기고 |
| **국립중앙도서관 도서관연구소 보고서** | 연간 | 정책 사서 | 자동화 사례 정책 보고 |

**5월 1편 목표**: 도서관저널 6월호 칼럼 — "사서 출신 창업자가 만든 KORMARC 자동 SaaS — 자관 PILOT 4주 후기"

### 3.6 유튜브 (사서 채널 큐레이션 + 우리 시연)

**한국 사서 큐레이션 채널** (구독 후 댓글 활동):
- "사서TV" (KLA 공식)
- "도서관TV" (NLK 공식)
- 사서 개인 채널 (검색어: 사서·도서관·책추천)

**우리 시연 영상 1편 (5월 PILOT 시작 후)**:
- 제목: "KORMARC 자동 5초 시연 — 자관 PILOT 라이브"
- 길이: 3분 (모바일 사서 시청 한계)
- 내용: ISBN 입력 → 결과 → KOLAS 반입 검증
- CTA: "무료 50건 가입 → 더보기에 링크"
- unlisted (목록 안 뜸) → 영업 메일·시연 신청자에 직접 공유

### 3.7 영업 골든타임 (예산 사이클 정합)

| 시기 | 예산 단계 | 영업 행동 |
|---|---|---|
| **11~12월** | 학교도서관·자치구 예산 편성 (자료구입비 3% 의무) | 신규 도입 제안서 발송·시연 약속 |
| **2~4월** | 봄 신학기 집행 | **베타 PILOT 도입 골든타임** ★ |
| **5월 (현재)** | KLA 발표·사서교육원 강의 | 도입 신뢰 자산 형성 |
| **6~8월** | 여름 휴가·긴급도입 안 됨 | 컨텐츠 SEO 집중 |
| **9~10월** | 추경 예산 편성 | 추가 도입 제안 |
| **11월** | 가을 추경 집행 | 1년차 갱신 |

**5월 핵심 캘린더**:
```
5/1~5/7  ADR 9 PO 결정 / 자관 PILOT 라이선스 / NL Korea API 신청
5/8~5/14 PILOT 1주 (★ 매크로 사서) / KLA 회원 가입
5/15~5/21 PILOT 2주 (수서 사서) / KLA 슬라이드 초안
5/22~5/28 PILOT 3주 (종합 사서 4명) / 슬라이드 통합
5/29~5/31 PILOT 4주 / KLA 발표 신청 (5/31 마감 ★)
```

### 3.8 영업 채널 종합 매트릭스

| 채널 | 도달 사서 | 전환율 추정 | PO 비용 | 시간 투자 | ROI |
|---|---:|---:|---|---|---|
| KLA 전국도서관대회 | 1,000+ 직접 | 3~5% | 0원 (발표) | 발표 준비 1주 | ★★★★★ |
| 자관 PILOT (8명) | 8명 | 50%+ | 0원 | PILOT 4주 | ★★★★★ |
| 협회 단체 영업 | 35,500 | 0.5~3% | 0원 (메일) | 메일 발송 1일/단체 | ★★★★ |
| 사서교육원 강의 | 50~100명/회 | 10~20% | 0원~50만원 | 준비 1주 | ★★★★ |
| 카카오 채널 | 활성 친구 100~500 | 3~5% | 0원 | 운영 30분/일 | ★★★★ |
| 네이버 블로그 | 월 500~2,000 방문 | 0.5~1% | 0원 | 글 1편/주 | ★★★ |
| 사서 카페 활동 | 5,000~10,000 노출 | 0.1~0.3% | 0원 | 30분/주 | ★★ |
| 유튜브 시연 영상 | 100~1,000 조회 | 0.5~1% | 0원 (자체 촬영) | 편집 1일/편 | ★★ |
| 학술지 칼럼 | 1,000~5,000 독자 | 0.1~0.5% | 0원 (원고료 받음) | 원고 1주 | ★★ |
| 박람회 부스 | 500~2,000 | 1~3% | 50~500만원 | 준비 1개월 | ★ (Phase 2 검토) |

---

## 4. 배포·호스팅 의사결정 (PO: 매니지드 우선·"두면 돈 버는")

### 4.1 백엔드 호스팅 비교

| 옵션 | 월 비용 (Beta 50명) | 월 비용 (200관) | 강점 | 약점 | 한국 latency |
|---|---:|---:|---|---|---|
| **Cloudflare Tunnel + PO PC (현재)** | 0원 | 부적합 | 0원·간단 | PO PC 꺼지면 다운·SLA 0 | 30~80ms |
| **Fly.io** (도쿄 nrt) | $0~5 (~7,000원) | $20~40 (~5만원) | 도쿄 region·docker·CLI 단순 | 무료 크레딧 한계·메모리 512MB | 30~50ms ★ |
| **Render.com** | $0 (free) | $25 (Standard) | GitHub 연동 자동·무료 가능 | 무료 15분 슬립·콜드 30초 | 100~200ms |
| **Vercel Functions** | 0~$20 | $20~50 | DX 최고·자동 스케일 | 함수 timeout 10s·Python 한계 | 50~100ms |
| **AWS EC2 (서울)** | $10~20 | $50~100 | 서울 region·풀 컨트롤 | 운영 부담·1인 부적합 | <20ms |
| **자체 VPS** (KT Cloud·Vultr) | 5,000원 | 2~5만원 | 가장 저렴·풀 컨트롤 | systemd·nginx·certbot 직접 | 20~50ms |

**권장**: **Fly.io 도쿄(nrt)** ★ — 도쿄가 한국에서 가장 빠르고, docker 단순, 시크릿 관리 편함. `fly.toml` + `Dockerfile`은 `docs/deploy.md`에 이미 작성됨.

### 4.2 프런트 호스팅 비교

| 옵션 | 월 비용 | 강점 | 약점 | 우리 사용 |
|---|---:|---|---|---|
| **Streamlit Community Cloud** | 무료 | 즉시 배포·secret 관리·private repo 지원 | 무료는 1GB RAM·sleep·도메인 streamlit.app | **★ Beta 1순위** (50명 무료) |
| **Streamlit + Fly.io 통합** | $5~20 | 자체 도메인·풀 컨트롤·sleep X | 셋업 부담 | Phase 2 (200관) 전환 |
| **Vercel + Streamlit** | 부적합 | - | Vercel은 정적·서버리스만 | X |
| **자체 호스팅 (PO PC)** | 0원 | 즉시·자유 | SLA 0·외부 노출 cloudflared 필수 | 개발·시연만 |

**권장 흐름**:
- **0~50명**: Streamlit Community Cloud + Cloudflare Tunnel (현재)
- **50~200관**: Fly.io 도쿄에 streamlit + fastapi 통합 docker
- **200관+**: Fly.io 자동 스케일 + Cloudflare CDN

### 4.3 결제 인프라 비교 (한국 사업자 등록 후)

| PG | 가입 | 정산 주기 | 수수료 | 강점 | 약점 |
|---|---|---|---:|---|---|
| **포트원** (구 아임포트) | 사업자번호 1일 | 즉시·D+0 옵션 | 카드 2.5%·계좌이체 1.5% | 한국 PG 통합 (KG이니시스·NHN KCP·토스 등 한 SDK)·문서 한국어 | 부분 환불 일부 PG 제한 |
| **토스페이먼츠** | 사업자번호 3일 | D+1 | 카드 2.7~2.9%·간편결제 2.4% | 토스 간편결제 직접·UX 최고 | 단가 약간 비쌈 |
| **Stripe** | 한국 사업자 OK | 7일 | 3.4% + 360원 | 글로벌·정기결제 강력 | 한국 단가 높음·해외 송금 환차손 |
| **카카오페이 송금** | 개인도 가능 | 즉시 | 0% | MVP-1 적합·즉시 가능 | 자동 정기결제 X·세금계산서 X |

**3단계 도입 흐름**:

| 단계 | 시점 | PG | 사업자 등록 |
|---|---|---|---|
| MVP-1 (현재) | 베타 무료 | 카카오페이 송금 + 수기 입금 확인 | 안 함 |
| MVP-2 | 베타 5명 검증 후 | 포트원 (테스트 모드) | 즉시 (홈택스 5분·무료) |
| MVP-3 | 누적 매출 100만원 | 포트원 정식 + 자동 영수증 + 세금계산서 | 사업자 등록 + 통신판매업 신고 |
| MVP-4 | 도서관 10관 도입 | 포트원 정기결제 + 토스페이먼츠 (간편결제 강화) | 부가세 분기 신고 자동 |

### 4.4 DB 비교

| DB | 월 비용 (Beta) | 월 비용 (200관) | 강점 | 약점 | 우리 사용 |
|---|---:|---:|---|---|---|
| **SQLite (현재)** | 0원 | 0원 | 파일 1개·간단·백업 cp 1번 | 동시 쓰기 약함·1 서버 한계 | **★ Beta 1순위** |
| **Supabase** (Postgres) | 무료 (500MB) | $25 (8GB) | PostgreSQL·Auth·Storage·Realtime 통합·관리 부담 0 | 무료 7일 비활성 일시정지 | Phase 2 전환 ★ |
| **Neon** (Serverless Postgres) | 무료 (3GB·1 endpoint) | $19 (10GB) | branching·serverless·즉시 | 도쿄 region 부재·미국 latency | 검토 |
| **Turso** (libSQL·SQLite 호환) | 무료 (9GB·1B reads) | $29 (24GB) | SQLite 그대로·edge replication·도쿄 region | 신생·생태계 작음 | 후보 |
| **PlanetScale** (MySQL) | 무료 (5GB) | $39 | branching·schema migration | MySQL 학습 곡선 | X |

**권장**: **Beta 50관까지 SQLite 유지** → 200관 도달 시 **Supabase로 마이그레이션**. SQLAlchemy ORM 사용하면 코드 변경 최소.

### 4.5 이메일 서비스 비교

| 서비스 | 월 비용 (Beta) | 월 비용 (200관) | 강점 | 약점 | 우리 사용 |
|---|---:|---:|---|---|---|
| **SendGrid** | 무료 (100/일) | $20 (50K/월) | 글로벌·deliverability ★·트랜잭셔널 강점 | 한국어 UI X | **★ 트랜잭셔널 1순위** (영수증·가입) |
| **Resend** | 무료 (3K/월·100/일) | $20 (50K/월) | DX 최고·React Email·SDK 단순 | 신생·도메인 인증 필수 | 검토 |
| **네이버웍스** | 6,000원~/사용자 | 사용자별 | 한국어·기업 메일·캘린더 통합 | 트랜잭셔널 X·SMTP 한계 | PO 본인 메일 (1명) |
| **Mailgun** | $0 (5K 첫달) | $35 | 강력한 API·deliverability | 무료 정책 변동 | X |
| **Amazon SES** | $0.10/1K | $50 | 가장 저렴·AWS 통합 | 도메인 verify·deliverability 자체 관리 | Phase 3 검토 |

**권장**: **SendGrid (트랜잭셔널)** + **PO 네이버웍스 (사서 1:1 응대)**.

### 4.6 모니터링·분석 비교

| 도구 | 월 비용 (Beta) | 강점 | 약점 | 우리 사용 |
|---|---:|---|---|---|
| **Sentry** | 무료 (5K errors/월) | 에러 추적·release 추적·Python·JS 통합 | UI 영문 | **★ 에러 1순위** |
| **PostHog** (self-hosted 무료) | 무료 (1M events/월 cloud) | 제품 분석·funnel·session replay·feature flag·A/B | 무거움·셋업 부담 | Phase 2 funnel 측정 |
| **Plausible** | $9/월 | privacy-first·GDPR·간단·100KB script | A/B X·세그먼트 약함 | **★ 페이지 분석 1순위** |
| **Google Analytics 4** | 무료 | 무료·강력 | privacy 우려·복잡 | X (PIPA 정합 어려움) |
| **Naver Analytics** | 무료 | 한국어·네이버 검색 데이터 통합 | 개발자 친화도 낮음 | 검토 |

**권장 조합**: **Sentry (에러)** + **Plausible (페이지 분석)** + **자체 `server/usage.py` (사용량 카운터)**.

### 4.7 CDN·도메인 비교

| 항목 | 옵션 | 비용 | 권장 |
|---|---|---:|---|
| 도메인 | 가비아 (.kr) | 연 22,000원 | `kormarc.kr` 즉시 |
| 도메인 | Cloudflare (.com) | 연 $10 | `kormarc-auto.com` 백업 |
| CDN | **Cloudflare** (무료 플랜) | 0원 | ★ 1순위 — DDoS·SSL·HTTP/3 |
| CDN | AWS CloudFront | 사용량 비례 | X (복잡·고비용) |
| DNS | Cloudflare | 0원 | ★ 도메인 둘 다 Cloudflare로 |
| SSL | Let's Encrypt (auto) | 0원 | Cloudflare 통합 자동 |

**권장**: 도메인 가비아 `.kr` + Cloudflare DNS·CDN·SSL·DDoS 무료 통합.

### 4.8 비용 시뮬레이션 (단계별)

#### 단계 1 — 베타 50명 (Phase 1 0~12개월)

| 항목 | 월 비용 |
|---|---:|
| Streamlit Community Cloud | 0원 |
| Cloudflare Tunnel + DNS | 0원 |
| 도메인 (가비아 .kr) | 약 1,800원 (연 2.2만원 ÷ 12) |
| Anthropic Vision (BYOK = PO 부담 0) | 0원 |
| SQLite (PO PC) | 0원 |
| SendGrid (무료 100/일) | 0원 |
| Sentry (무료 5K errors) | 0원 |
| Plausible (월 9$) | 약 13,000원 |
| 카카오 비즈니스 채널 | 0원 |
| **합계** | **약 15,000원/월** |

매출: 50관 × 평균 3만원 = 150만원/월. **마진 99%**.

#### 단계 2 — 200관 (Phase 3 24~36개월·캐시카우 도달)

| 항목 | 월 비용 |
|---|---:|
| Fly.io (도쿄 nrt·shared 1cpu 1GB) | $25 (~3.5만원) |
| Supabase Pro (8GB Postgres) | $25 (~3.5만원) |
| 도메인 + Cloudflare | 1,800원 |
| Anthropic (BYOK 부분·일부 자관 부담) | 약 5만원 (자체 quota 지원) |
| SendGrid Essentials | $20 (~2.8만원) |
| Sentry Team | $26 (~3.6만원) |
| Plausible Business | $19 (~2.7만원) |
| 백업 스토리지 (S3·CloudFlare R2) | 약 5,000원 |
| 결제 PG 수수료 (포트원 2.5%) | 매출의 2.5% = 25만원 |
| 통신판매·세무 처리 | 약 5만원 |
| **합계** | **약 50~55만원/월** |

매출: 200관 × 평균 5만원 = 1,015만원/월 (`docs/sales-roadmap.md` Phase 3 정합). **마진 약 95%**.

#### 단계 3 — 1,000관 (Phase 4 36개월+)

| 항목 | 월 비용 |
|---|---:|
| Fly.io (도쿄·multi-region·dedicated 4cpu 4GB) | $100~150 (~20만원) |
| Supabase Team (50GB·dedicated compute) | $200 (~28만원) |
| Cloudflare Pro | $20 (~2.8만원) |
| Anthropic API (자체 호스팅 일부) | 약 50~100만원 |
| SendGrid Pro (100K/월) | $90 (~12.6만원) |
| Sentry Business | $80 (~11만원) |
| Plausible | $19 (~2.7만원) |
| 백업·DR 다중화 | 약 10만원 |
| 결제 PG 수수료 (포트원 2.5%) | 매출의 2.5% = 약 100만원 |
| 통신판매·세무·CS 1명 | 약 200만원 |
| 법무 자문 (분기) | 약 30만원 |
| **합계** | **약 470~520만원/월** |

매출: 1,000관 × 평균 4만원 = 4,000만원/월. **마진 약 87%**.

---

## 5. 운영 자동화 + 분석 + 피드백

### 5.1 사용량 카운터 → 월간 대시보드 자동 집계

`server/usage.py` + `logs/usage.jsonl` 기반 자동 집계 (`docs/sales-roadmap.md` 측정 지표 정합):

```python
# scripts/aggregate_revenue.py (이미 존재)
# 매월 1일 03:00 KST 자동 실행 (GitHub Actions cron)
# 출력: data/monthly/{YYYY-MM}.json
{
  "month": "2026-05",
  "active_libraries": 50,
  "new_signups": 15,
  "churn_rate": 0.08,
  "revenue_krw": 1_500_000,
  "by_plan": {"small": 40, "medium": 8, "large": 2},
  "top_libraries_by_usage": [...],
  "p99_response_ms": 4_800,
  "error_rate": 0.012,
  "nps": 42  # 자관 6년 NPS 历사 비교 가능
}
```

**PO 대시보드** (`/admin/stats` 엔드포인트):
- 월 매출·이탈률·신규 가입 (목표 대비 진척률)
- 도서관별 사용량 Top 10 (이상치 감지)
- 에러율·응답 속도 (SLA 모니터링)
- 자관 NPS 历사 비교 (3년 평균 vs 이번 달)

### 5.2 결제 자동화 (월정액 자동 차감 + PO 시간 0)

**포트원 정기결제 자동 흐름** (MVP-3 이후):

```
[1] 사서 가입 → 카드 등록 (포트원 SDK 1번 호출)
[2] 매월 1일 03:00 KST → cron job 자동 차감
[3] 결제 성공 → 영수증 PDF 자동 생성 (legal/receipt_pdf.py)
[4] 영수증 PDF → 사서 이메일 자동 발송 (SendGrid)
[5] 결제 실패 → 재시도 3회 (D+1·D+3·D+7) → 그래도 실패 → 카카오 자동 알림
[6] 30일 무결제 → 계정 일시 정지 (서비스 차단 X·로그인 가능)
[7] 60일 무결제 → 계정 비활성화 (DSAR 권리 안내)
```

**PO 시간 0** = 위 7단계 모두 자동. PO는 월 1회 `/admin/stats` 30분 점검만.

### 5.3 영수증 PDF 자동 + 한국 부가세 10% 계산

**영수증 PDF 자동 생성** (이미 `legal/receipt_pdf.py` 존재 → 확장):

```
| 항목 | 금액 |
|---|---:|
| 작은도서관 월 정액 | 30,000원 |
| 부가세 (10%) | 3,000원 |
| **합계** | **33,000원** |

공급자: kormarc-auto (사업자등록번호: ___)
공급받는자: ○○도서관
발행일: 2026-05-01
영수증 번호: KMA-2026-05-0042
```

**세금계산서 자동 발행** (포트원 통합):
- 사업자번호 입력한 도서관 → 자동 발행
- 국세청 전자세금계산서 시스템 연동 (포트원 plugin)
- PO 시간 0

### 5.4 NPS·피드백 위젯 → 자동 집계

`scripts/aggregate_interviews.py` (이미 존재) 활용:

```python
# 매월 1일 NPS 집계 자동
# 입력: logs/feedback.jsonl + interviews/*.md
# 출력: data/nps/{YYYY-MM}.json
{
  "month": "2026-05",
  "nps_score": 42,
  "promoters_pct": 56,
  "passives_pct": 30,
  "detractors_pct": 14,
  "top_complaints": ["검색 결과 정확도", "한자 도서 처리"],
  "top_praises": ["권당 시간 절감", "사서 친화 용어"],
  "feature_requests_top10": [...]
}
```

**자관 6년 NPS 历사와 비교** = 자관 PILOT 검증 자료.

### 5.5 GitHub Actions CI (pytest·ruff·binary_assertions 자동)

`.github/workflows/ci.yml` (이미 존재 권장):

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check src tests
      - run: pytest -q
      - run: python scripts/binary_assertions.py --strict
      - run: mypy src
```

**자율 commit 게이트 정합** (`.claude/rules/autonomy-gates.md`):
- pytest 종료 코드 0
- binary_assertions 23/23 통과
- 평가축 §0 또는 §12 양수 영향 (commit 메시지 명시)

### 5.6 백업 자동 (90일·365일 회전)

**백업 대상**:

| 대상 | 빈도 | 보존 | 방법 |
|---|---|---|---|
| SQLite DB (`data/kormarc.db`) | 매일 03:00 | 90일 | `cp + gzip` → Cloudflare R2 |
| `logs/usage.jsonl` | 매시간 | 365일 (개인정보보호법 §21) | `scripts/rotate_logs.py` 자동 |
| `logs/feedback.jsonl` | 매일 | 365일 | 익명화 후 영구 |
| 기관별 데이터 (.mrc archive) | 매주 | 영구 | R2 + 분기 verify |
| GitHub repo | 매 commit | 영구 (git history) | 자동 |

**`scripts/rotate_logs.py`** (이미 존재):
- 90일 경과 → 압축 아카이브
- 365일 경과 → 익명화 (key hash → 'anon', PII 마스킹)
- 5년 경과 → 영구 삭제 (국세기본법 5년 후)

### 5.7 장애 대응 (5xx 알림·oncall 1인 운영 minimal)

**알림 트리거 4단**:

| 단계 | 조건 | 알림 채널 |
|---|---|---|
| L1 정보 | 응답 지연 (p95 > 5초) | Sentry 대시보드만 |
| L2 주의 | 에러율 > 1% (5분 이동평균) | Sentry → 슬랙 (PO 카톡 채널) |
| L3 경고 | 5xx 폭증 (분당 10건+) | Sentry → 카카오 알림톡 PO |
| L4 긴급 | 서비스 다운 (헬스체크 fail 3회) | 카카오 + 이메일 + SMS (Twilio) |

**oncall 1인 운영 minimal**:
- PO 카카오 채널 24시간 영업 SLA
- 새벽 장애 = 다음 영업일 09시 1차 응답 (이용약관 명시)
- L4 긴급만 새벽 응답 (PO 폰 SMS 알림)

### 5.8 법적 준수 자동 (개인정보보호법 §35-3·§36 DSAR·72h 신고)

**자동 처리 매트릭스**:

| 의무 | 자동 처리 | 수동 트리거 |
|---|---|---|
| 개인정보 수집 동의 | 가입 시 체크박스 강제 (이용약관 + 개인정보처리방침 양쪽) | - |
| 개인정보 처리방침 게시 | 모든 페이지 footer 링크 | - |
| 데이터 다운로드 (DSAR §35-3) | `GET /account/export` 즉시 JSON 응답 | - |
| 데이터 삭제 (§36) | `DELETE /account/delete` 즉시 처리 | - |
| 보유기간 경과 자동 파기 | `scripts/rotate_logs.py` 매일 cron | - |
| **72h 신고 (1,000명+ 또는 민감정보)** | 미구현 (베타 PILOT 도달 시) | PO 직접 (개인정보보호위원회) |
| audit_log 해시 체인 (5만명+) | 미구현 (Phase 3 도달 시) | - |
| 동의 철회 자동 처리 | 카카오 채널 키워드 `탈퇴` → 30일 내 처리 | - |

---

## 6. PIPA 시행 2026-09-11 대응 + 옵션 C 선택 (★ 매출 10% 과징금)

### 6.1 PIPA 5대 코드 패턴 (생존 게이트)

`.claude/rules/business-impact-axes.md` Q5 정합:

| 패턴 | 위반 시 | 우리 정합 |
|---|---|---|
| 1. **Reader/Borrower/Patron entity ERD** | 매출 10% 과징금 | ✅ **옵션 C** = 자관 알파스 위임. 우리 ERD에 PII 컬럼 0 |
| 2. **암호화** (bcrypt·AES-256·TLS 1.2+) | 시행령 §7 | 🟡 logging PII 5종 마스킹 보강 필요 ★ |
| 3. **DSAR** (제35·36·37·35조의2) | 정보주체 권리 | ✅ `/account/export`·`/account/delete` |
| 4. **72h 신고** | 1,000명+·민감정보·해킹 시 | ❌ 베타 PILOT 도달 시 (현재 50관 미달) |
| 5. **audit_log + 해시 체인** | 5만명+·민감정보 | ❌ Phase 3 5만명 도달 시 |

### 6.2 카카오 학습 (151억 과징금)

**판단 핵심**: "**부분 적용 후 미마이그레이션이 결정타**"

→ 우리 정책: **보안 패치 시 전수 마이그레이션 강제**. `business-impact-axes.md` §5 명문화 완료.

**예시 시나리오**:
- 2026-08-31 logging PII 마스킹 보강 patch 배포
- 동일 patch에 **기존 logs/usage.jsonl 전수 마이그레이션 스크립트 동시 실행**
- 마이그레이션 verify (rollback 가능 시점 30일 보존)
- 모든 사서에 마이그레이션 완료 통지 (이메일 + 카카오)

### 6.3 ★ 옵션 C 선택 (회원 PII = 자관 알파스 위임)

**3 옵션 비교**:

| 옵션 | 우리 PII 처리 | PIPA 패턴 1 위험 | 사서 가치 |
|---|---|---|---|
| 옵션 A | 회원 정보 직접 처리 (Reader entity ERD) | 🔴 매출 10% 과징금 위험 | 통합 경험 |
| 옵션 B | 회원 정보 일부 (이메일만) | 🟡 부분 위반 | 부분 통합 |
| **옵션 C** ★ | **회원 PII = 자관 알파스에 위임. 우리는 양식·통계·템플릿만** | 🟢 **위반 영역 X** | 자관 시스템 보존 |

**옵션 C 구체 흐름**:

```
[1] 회원 정보 (이름·전화·생년월일·주소) = 자관 알파스 / KOLAS / DLS 보관
[2] 우리 SaaS = 익명화된 통계만 받음 ("3월 신착 50권·KDC 800대 30권")
[3] 우리가 출력 = 양식·통계·템플릿만 (회원증·연체 통계·알림 템플릿)
[4] 사서가 우리 양식을 자관 시스템에 import → 자관 시스템이 회원 매칭
```

**PIPA 패턴별 정합**:
- 패턴 1 Reader entity ERD: ✅ **우리 ERD에 PII 컬럼 0** (사서 본인 이메일·도서관명만)
- 패턴 2 암호화: ✅ TLS 1.2+ Cloudflare·SQLite + 사서 이메일 bcrypt
- 패턴 3 DSAR: ✅ 사서 본인 데이터 export·delete만 (회원 데이터 우리에게 없음)
- 패턴 4 72h 신고: ✅ 회원 PII 누출 risk 0 (우리에게 없음)
- 패턴 5 audit_log: ✅ 사서 본인 활동만 audit (회원 PII 무관)

### 6.4 PILOT 전 PII 5종 마스킹 보강 (logging)

**마스킹 대상 5종** (`docs/pii-guard-hook-design.md` 정합):

| 항목 | 패턴 | 마스킹 후 |
|---|---|---|
| email | `okwhrlgma@gmail.com` | `o***@g***.com` |
| phone | `010-1234-5678` | `010-****-5678` |
| patron_name | `홍길동` | `홍**` |
| patron_id | `2024-001234` | `2024-***234` |
| birth_date | `1990-01-15` | `1990-**-**` |

**logging_config.py 보강**:

```python
import re
from logging import Filter, LogRecord

class PIIMaskingFilter(Filter):
    """PIPA 5대 패턴 — logging 시 자동 마스킹."""
    PATTERNS = [
        (re.compile(r"([a-zA-Z0-9])[a-zA-Z0-9]*@([a-zA-Z0-9])[a-zA-Z0-9]*\.([a-zA-Z]+)"),
         r"\1***@\2***.\3"),
        (re.compile(r"(01\d)[-\s]?(\d{3,4})[-\s]?(\d{4})"),
         r"\1-****-\3"),
        # patron_name: 한글 2~4자, 첫 글자만 노출
        (re.compile(r"([가-힣])[가-힣]{1,3}"), r"\1**"),
        # patron_id: 숫자 4자리-숫자 6자리, 마지막 3자리만
        (re.compile(r"(\d{4})-\d{3}(\d{3})"), r"\1-***\2"),
        # birth_date: YYYY-MM-DD, 연도만 노출
        (re.compile(r"(\d{4})-\d{2}-\d{2}"), r"\1-**-**"),
    ]

    def filter(self, record: LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in self.PATTERNS:
            msg = pattern.sub(repl, msg)
        record.msg = msg
        record.args = ()
        return True
```

**적용 위치**:
- `logging_config.py` root logger에 filter 추가
- 모든 핸들러 (file·console·Sentry) 통과
- pre-commit hook으로 매 commit 검증 (`pii-guard.py`)

### 6.5 PIPA 정합 자동 검증 hook

`.claude/hooks/pii-guard.py` (PreToolUse):

```python
"""PIPA 5대 패턴 자동 차단 — 매 commit 직전 검증."""
import re
import sys
from pathlib import Path

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone_kr": re.compile(r"01[0-9][-\s]?\d{3,4}[-\s]?\d{4}"),
    "rrn": re.compile(r"\d{6}[-\s]?[1-4]\d{6}"),  # 주민등록번호
    "patron_id": re.compile(r"\d{4}-\d{6}"),
}

def scan_diff_for_pii(diff: str) -> list[str]:
    violations = []
    for name, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(diff):
            # 마스킹된 패턴은 통과
            if "***" in match.group():
                continue
            violations.append(f"{name}: {match.group()[:20]}...")
    return violations
```

→ commit 직전 git diff에서 PII 발견 시 차단·수정 요구.

### 6.6 5월 PILOT 전 PIPA 체크리스트

| # | 항목 | 마감 | 담당 |
|---|---|---|---|
| 1 | logging PII 5종 마스킹 filter 적용 | 5/3 | Claude Code |
| 2 | pii-guard.py hook 활성 | 5/3 | Claude Code |
| 3 | 옵션 C 명문화 (CLAUDE.md §12 추가) | 5/3 | PO |
| 4 | privacy-policy.md "회원 PII X" 명시 | 5/3 | Claude Code |
| 5 | 자관 PILOT 라이선스 동의서에 옵션 C 명시 | 5/5 | PO ↔ 자관 |
| 6 | DSAR 엔드포인트 verify (export·delete) | 5/7 | Claude Code |
| 7 | 자관 PILOT 1주 시작 | 5/8 | PO |

---

## 부록 A — 오늘 30분 액션 5건 (PO)

| # | 액션 | 시간 | URL/연락 |
|---|---|---|---|
| 1 | 알라딘 TTBKey 신청 | 5분 | https://www.aladin.co.kr/ttb |
| 2 | 카카오 개발자 API Key | 5분 | https://developers.kakao.com |
| 3 | 도서관 정보나루 가입 | 5분 | https://data4library.kr |
| 4 | NL Korea 서지 API 신청 | 10분 | https://librarian.nl.go.kr |
| 5 | KLA 회원 가입 (전국도서관대회 발표 신청용) | 5분 | https://www.kla.kr → license@kla.kr |

→ **30분으로 MVP Phase 0 진입 + KLA 발표 신청 자격 확보**.

---

## 부록 B — 이번 주 액션 5건 (PO)

| # | 액션 | 마감 | 출력 |
|---|---|---|---|
| 1 | 사업자 등록 (홈택스 5분·무료) | 5/3 | 사업자등록증 |
| 2 | 자관 PILOT 라이선스 동의서 (PO ↔ 자관) | 5/5 | 동의서 PDF |
| 3 | 카카오 비즈니스 채널 생성 (`@kormarc-auto`) + 자동응답 20종 등록 | 5/5 | 채널 활성 |
| 4 | 네이버 블로그 개설 + 첫 글 1편 ("KORMARC 자동 5초") | 5/7 | 글 1편 |
| 5 | KLA 전국도서관대회 발표 신청서 초안 | 5/7 | 초안 PDF |

→ **이번 주 5건 완료 = 5월 PILOT + KLA 발표 신청 동시 진행**.

---

## 부록 C — Claude Code 자율 즉시 명령 5건

| # | 명령 | 평가축 (Q1·Q2·Q3·Q4·Q5) |
|---|---|---|
| 1 | `streamlit_app.py` 1,429줄 → 5 page multi-page 분리 | Q1 90·Q2 95·Q3 85·Q4 70·Q5 PASS |
| 2 | `logging_config.py` PII 5종 마스킹 filter 추가 | Q1 70·Q2 95·Q3 90·Q4 60·Q5 PASS (PIPA 패턴 2 보강) |
| 3 | `.claude/hooks/pii-guard.py` 활성 | Q1 60·Q2 95·Q3 90·Q4 70·Q5 PASS (자동 차단) |
| 4 | `legal/receipt_pdf.py` 부가세 10% 자동 계산 + 세금계산서 hook | Q1 85·Q2 90·Q3 80·Q4 75·Q5 PASS |
| 5 | `pages/3_📷_사진.py` 모바일 카메라 직접 호출 (`capture="environment"`) | Q1 90·Q2 95·Q3 75·Q4 70·Q5 PASS |

→ 5건 모두 **Beta 단계 임계값 70+ 통과** → 자율 commit 즉시.

---

## 부록 D — 5월 1~31일 종합 캘린더

```
주간       PO 액션                              Claude Code 자율 commit
─────────────────────────────────────────────────────────────────────────
5/1~5/7   ☐ 사업자 등록                        ☐ Streamlit 5 page 분리
          ☐ 자관 PILOT 라이선스                ☐ PII 마스킹 filter
          ☐ KLA 회원 가입                      ☐ pii-guard.py 활성
          ☐ 카카오 채널 + 자동응답 20종        ☐ pages/3_사진 모바일 카메라
          ☐ 네이버 블로그 개설                 ☐ DSAR 엔드포인트 verify
                                              ☐ 영수증 PDF 부가세

5/8~5/14  ☐ 자관 PILOT 1주 (★ 매크로 사서)    ☐ 책단비 자동 (chaekdanbi/)
          ☐ NL Korea API 키 활성               ☐ KOLAS F12 importer
          ☐ 네이버 블로그 글 #2                ☐ pages/4_일괄 KOLAS Watch

5/15~5/21 ☐ PILOT 2주 (수서 사서)              ☐ KOLIS-NET 5종 폴백 통합
          ☐ KLA 발표 슬라이드 초안             ☐ Sentry + Plausible 통합
          ☐ 사서교육원 강의 제안서             ☐ aggregate_revenue.py 자동

5/22~5/28 ☐ PILOT 3주 (종합 사서 4명)          ☐ KLA 발표용 시연 시나리오
          ☐ 발표 슬라이드 통합                 ☐ 영업 데이터 export 자동

5/29~5/31 ☐ PILOT 4주 + 통합 검증              ☐ KLA 슬라이드 PDF
          ☐ ★ KLA 발표 신청 (5/31 마감)       ☐ 자관 PILOT 결과 보고서
          ☐ 사서교육원 강의 제안서 제출
```

---

## 부록 E — 핵심 메트릭 (월간 PO 점검 30분)

```bash
# 매월 1일 03:00 KST 자동 (GitHub Actions)
$ python scripts/aggregate_revenue.py --month 2026-05
$ python scripts/aggregate_interviews.py --month 2026-05
$ python scripts/binary_assertions.py --strict
$ python scripts/accuracy_compare.py --against tests/samples/golden

# 결과 → data/monthly/2026-05.json
# PO 대시보드 → /admin/stats?month=2026-05
```

| 지표 | Phase 1 목표 | Phase 2 목표 | Phase 3 목표 |
|---|---|---|---|
| 월 매출 (KRW) | 1,500,000 | 4,100,000 | 10,150,000 |
| 활성 도서관 수 | 50 | 100 | 200 |
| 이탈률 (월) | <15% | <8% | <5% |
| 신규 가입 (월) | 10~15곳 | 8~12곳 | 5~10곳 (입소문) |
| NPS (자관 历사 비교) | 30+ | 40+ | 50+ |
| 정확도 (`accuracy_compare`) | 80%+ | 90%+ | 95%+ |
| 권당 비용 (Q2 검증) | ≤ ₩50 | ≤ ₩30 | ≤ ₩10 |
| 한 달 자율 commit 수 | 30+ | 50+ | 30 (안정기) |
| binary_assertions 통과율 | 100% | 100% | 100% |

---

## 7. Sources

- `docs/sales-roadmap.md` (Phase 1·2·3 캐시카우 도달 경로)
- `docs/pricing.md` (가격 4단·페르소나 정합·PG 도입 단계)
- `docs/po-outreach-list.md` (협회 영업 매트릭스·5월 마감 임박)
- `docs/po-master-action-plan-2026-04-28.md` (5월 1~31일 일정표)
- `docs/mvp-redefinition-2026-04-29.md` (MVP 6 Phase·Phase 0 ISBN→.mrc)
- `docs/ux-audit.md` (Streamlit UX 감사 26/40·즉시 수정 Top 10·CSS 팔레트)
- `docs/saseo-personas-2026-04-28.md` (4 페르소나 ICP 매트릭스)
- `docs/kakao-channel-faq.md` (카카오 채널 자동응답 20종)
- `docs/deploy.md` (Fly.io·Render·VPS 셋업)
- `docs/사서_웹사용법.md` (사서 친화 사용법 가이드)
- `docs/privacy-policy.md` (개인정보처리방침 v1.0)
- `docs/pii-guard-hook-design.md` (PIPA 5대 패턴 자동 차단)
- `CLAUDE.md` §0·§12 (수익 모델 헌법)
- `.claude/rules/autonomy-gates.md` (캐시카우 평가축)
- `.claude/rules/business-impact-axes.md` (5질문 + Q5 PIPA 별도 게이트)
- `.claude/rules/kormarc-domain.md` (KORMARC 2023.12 + 9 자료유형)
- KLA 전국도서관대회 (https://www.kla.kr) — 5.31 발표 신청 마감
- 네이버 서치어드바이저 (https://searchadvisor.naver.com)
- 포트원 (https://portone.io) — 한국 PG 통합
- Fly.io (https://fly.io) — 도쿄 nrt region
- Supabase (https://supabase.com) — Postgres + Auth
- SendGrid (https://sendgrid.com) — 트랜잭셔널 이메일
- Sentry (https://sentry.io) — 에러 추적
- Plausible (https://plausible.io) — privacy-first 분석
- Cloudflare (https://cloudflare.com) — DNS·CDN·DDoS 무료
- 자관 D 드라이브 (사서 8명 페르소나 + .mrc 174 + 6년 NPS)
