# kormarc-auto UX 감사 보고서

> 사서(50대 여성·IT 비전공) 관점에서 Streamlit UI(`streamlit_app.py`)와 랜딩(`landing/*.html`)을 8개 항목으로 감사. 코드 직접 수정은 메인 에이전트가 수행. 라인 인용은 모두 정확히 표기.

작성일: 2026-04-26 · v0.4.1 기준

---

## 1. 종합 점수 (각 항목 5점 만점, 합계 40점)

| 항목 | 점수 | 핵심 진단 |
|---|---|---|
| A. 첫인상 | 4 / 5 | 헤드라인 "권당 8분 → 2분"은 강력. 다만 CTA 버튼 색·크기 단조롭고 무료 조건이 헤드라인 옆에 없음 |
| B. 정보 위계 | 3 / 5 | Streamlit 메인 5탭 순서는 적절. 단, 사이드바에 핵심 설정(040 부호)이 모바일에서 collapsed → 발견성 낮음 |
| C. 색상·타이포·간격 | 2 / 5 | 본문 13~14px이 다수, 50대 사서에 작음. 색 대비 OK이지만 회색 `#9ca3af` 캡션은 WCAG AA 미달 가능 |
| D. 빈/로딩/에러 | 3 / 5 | spinner 메시지는 구체적이나, "검색 결과 없음" `st.warning`(L229)은 다음 단계 미제시 |
| E. 모바일 | 3 / 5 | viewport·반응형 그리드 OK. 하지만 file_uploader에 `capture="environment"` 미설정 → 카메라 직접 호출 안 됨 |
| F. 사서 멘탈 모델 | 4 / 5 | 도서관 용어 정확("표제", "발행자", "관제", "▾a"). 사이드바 헬프 친절. "040 ▾a"는 IT 비전공자에 난해 |
| G. 온보딩 | 3 / 5 | 가이드는 expander 안에 숨겨져(L836) 첫 화면에서 안 보임. 무료 50건이 사이드바에만 |
| H. 결제 전환 | 4 / 5 | 가격 페이지 명확·세금계산서/분기제 호환 안내 우수. 단 한도 임박 경고가 UI에 없음 |

**총점: 26 / 40 (65%)** — "기능 완성도는 충분하나, 50대 비IT 사서가 한 번에 이해·완수하기엔 시각적 무게·온보딩이 부족."

---

## 2. 즉시 수정 권고 Top 10

### #1. 본문 폰트 15~16px로 상향 (전 화면)
- **근거**: 50대 여성 비율 높음. 현재 `landing/index.html` L29 카드 본문 `font-size:14px`, L37 input `15px`, L39 result `13px`, `pricing.html` L20 table `14px`, `demo.html` L17 meta `13px`.
- **개선**: `:root` 차원에서 `--font-body:16px; --font-sm:14px;` 정의. 본문 16px, 보조 14px만 허용. `streamlit_app.py` L82 `<style>` 블록에 `html, body, .stMarkdown {font-size:16px;}` 주입.

### #2. Streamlit 메인 화면 첫 줄에 "무료 50건"·"5분 가이드" 카드 노출
- **근거**: 현재 L836 `with st.expander("📖 처음이신가요? (5분 가이드)")` — 사이드바 안 + 접힌 상태 → 모바일에서 사이드바 collapsed라 발견 0%.
- **개선**: L805 `st.title` 직후 `st.info("✨ 처음이신가요? 신규 50건 무료. 아래 [ISBN] 탭에 ISBN 13자리만 넣어 보세요.")` 추가 후, 가이드 expander를 사이드바와 메인 양쪽에 두기.

### #3. 사이드바 "040 ▾a"·"Anthropic API 키" 용어 변경
- **근거**: L810 `agency = st.text_input("우리 도서관 부호 (040 ▾a)", "OURLIB")` — "040 ▾a"는 사서가 KORMARC 익숙해도 낯섦. L815 `Anthropic API 키`는 도서관 용어 아님.
- **개선**:
  - L810 라벨 → `"우리 도서관 부호"` + `help="KOLAS 관리자 화면의 도서관 식별부호. 모르시면 OURLIB 그대로 두세요."`
  - L814 라벨 → `"AI 추천 보조 키 (선택)"` + 아래에 `st.caption("⚙ KDC·주제명 AI 자동 추천을 쓰려면 입력. 안 입력해도 ISBN 기능은 100% 작동.")`

### #4. 검색 결과 0건에 "다음 단계" 제시
- **근거**: L229 `st.warning("검색 결과 없음")` — 막다른 길.
- **개선**:
  ```python
  st.warning("검색 결과가 없습니다.")
  st.info(
      "다음을 시도해 보세요:\n"
      "- 띄어쓰기/오타 확인 (예: '한강 작별' vs '한강작별')\n"
      "- 표제 일부만 (예: '작별')\n"
      "- ISBN을 알면 [ISBN 단건] 탭이 더 정확합니다"
  )
  ```

### #5. 파일 업로더에 `accept="image/*" capture="environment"` 폴리필
- **근거**: L252 `st.file_uploader(...)` — Streamlit 기본은 갤러리 선택. 모바일 카메라 직접 호출 시 한 번 더 탭 필요.
- **개선**: L251 caption 아래에 `st.markdown("<p style='font-size:14px;color:#6b7280;'>📷 폰에서 사용 시 [사진 촬영]을 누르세요.</p>", unsafe_allow_html=True)` 추가 + `streamlit-camera-input-live` 컴포넌트 도입 검토 (중기).

### #6. 랜딩 CTA 버튼 크기·색 강화
- **근거**: `landing/index.html` L21 `.btn { padding:12px 22px; }` — 50대에는 작음. L56 `<a class="btn btn-pri" href="#try">50건 무료 시작</a>`는 헤드라인 강조 약함.
- **개선**: 
  ```css
  .btn-pri { padding:18px 32px; font-size:18px; box-shadow:0 4px 14px rgba(31,111,235,0.25); }
  .btn-pri:hover { background:#1856c4; transform:translateY(-1px); }
  ```
- 헤드라인 L53 `<h2>사서의 마크 작업, 권당 8분 → 2분</h2>` 아래에 "**카드 등록 없음 · 50건 무료**" 한 줄 강조 추가.

### #7. Streamlit 결과 카드에 진행률·예상 시간 라벨
- **근거**: L100 `st.spinner(f"외부 API 조회 중... ({isbn})")` — "얼마나 걸릴지" 불명. 사서는 폰을 들고 기다리는 시간이 곧 가치.
- **개선**: spinner 메시지에 예상 시간 명시.
  - L100 → `"외부 API 조회 중 (약 3초)... {isbn}"`
  - L118 → `"KDC 분류 추천 중 (약 2초)..."`
  - 일괄 처리(L323) → `progress.progress(i / len(isbns), text=f"{i}/{len(isbns)}권 · 약 {(len(isbns)-i)*4}초 남음")`

### #8. 에러 메시지에 "어떻게 해결" 추가
- **근거**: L104 `st.error(f"외부 API 호출 실패: {e}")`, L108 `st.error(f"ISBN {isbn}: 모든 소스에서 미조회")`, L286 `st.error("ISBN 추출 실패 — 사진 품질을 확인하세요.")` — 무엇이 문제인지는 알리나 "다음 단계"가 약하거나 없음.
- **개선**:
  ```python
  st.error(f"ISBN {isbn}: 등록 정보를 찾을 수 없습니다.")
  st.info(
      "💡 해결 방법:\n"
      "1. ISBN 13자리가 맞는지 확인 (978로 시작)\n"
      "2. [검색] 탭에서 표제·저자로 시도\n"
      "3. 옛 책·자가출판이면 [사진] 탭으로 표지 업로드"
  )
  ```

### #9. 가격 페이지 "추천" 플랜 시각 강화 + 분기제 안내 위치 상승
- **근거**: `landing/pricing.html` L58 `<div class="plan recommended">` 작은도서관 3만원 — 메시지는 좋으나 박스가 다른 plan과 거의 같은 크기. L112 "분기제 호환" 안내가 FAQ 위지만 헤드 근처가 아님.
- **개선**: 
  - L15 `.plan.recommended` → `transform:scale(1.05); padding:28px;` 추가.
  - L37 lead 문장 직후에 강조 박스: "📅 도서관 예산 분기제(4월·10월) 결제 환영. 세금계산서 발행."

### #10. Streamlit 사이드바 "가격 안내" 섹션을 메인 결과 카드에도 노출 (한도 근접 시)
- **근거**: 사이드바(L831) 가격 안내는 사용자가 펼치지 않으면 안 보임. 50건 무료 임박/초과 시 자연스러운 결제 유도 부재.
- **개선**: `_render_result` 마지막(L204 이후)에 `usage` 모듈에서 잔여 무료 카운트 가져와 표시:
  ```python
  remaining = get_user_remaining_quota(user_key)  # server.usage
  if remaining is not None and remaining <= 10:
      st.info(f"📊 무료 잔여: {remaining}건. 이후엔 권당 100원 또는 월 3만원~. [가격 안내]({PAYMENT_INFO_URL})")
  ```

---

## 3. 중장기 권고 5종

1. **온보딩 투어 (3단계 카드)**: 첫 로그인 시 `streamlit-extras`의 `mention` 또는 자체 sticky 카드로 "1) ISBN 입력 → 2) 결과 확인 → 3) .mrc 다운로드"를 화면 위에 띄움. 닫기 시 localStorage 저장.
2. **사진 탭 가이드 일러스트**: 표지·판권지·뒷표지의 3가지 좋은 사진 예시 이미지 (1024×768 정도)를 `landing/static/`에 추가하고 사진 탭(L251)에 미니 갤러리로 노출. "흐릿한 사진 vs 또렷한 사진" 비교.
3. **가격 페이지에 "내 도서관 ROI 계산기"**: 월 신착 권수 입력 → 시간 절감(권당 6분) × 사서 시급(공공 19,000원) → 절감액 vs 결제액 비교. 조용한 설득 도구.
4. **음성 안내(접근성)**: 50대 사서·시각 약시 사서 대상 `aria-label`·`role="status"` 보강. 결과 카드 success 메시지에 ARIA live region.
5. **카카오톡 채널 통합**: 랜딩 footer에 "카카오톡으로 1:1 문의" 버튼. 50대 사서에 이메일보다 카톡 문턱이 낮음. PO의 plus_friend 키 발급 후 deep link.

---

## 4. 참고 사례 (한국 사용자 친화 SaaS)

- **토스 (toss.im)**: 한 화면에 한 가지 결정만. 큰 폰트(17~18px), 버튼 풀폭. 색채는 단일 파랑(#3182F6) + 회색 톤. → kormarc-auto도 결과 카드 다운로드 버튼이 화면 바닥에 풀폭 sticky로 있어야 함.
- **카카오뱅크**: 에러 메시지가 "왜 안 됐고, 무엇을 하면 되는지" 두 문장으로. → 권고 #8 직접 영감.
- **노션 (Notion 한국어)**: 첫 가입 시 "샘플 페이지 → 직접 편집"의 3단계 가이드. 닫기 가능. → 권고 중장기 #1.
- **잡코리아·사람인 (50대 이용 비율 높음)**: 폼 입력 칸 높이 48px·라벨 16px 고정. → Streamlit input height CSS 오버라이드.
- **국립중앙도서관 KOLIS-NET**: 사서 친숙. 색채는 차분한 청록·회색. → 본 시스템과 톤 일관 권장 (현재의 #1f6feb 파란은 깔끔하나 약간 차갑다 — #2563eb 또는 따뜻한 #1e6091로 미세 조정 검토).

---

## 5. 색상 팔레트·폰트 권장 (즉시 적용 가능 CSS)

### 팔레트 (사서 친화: 차분 + 가독)

```css
:root {
  /* Primary */
  --color-primary:        #2563eb;  /* 차분한 파랑 — 기존 #1f6feb보다 약간 따뜻 */
  --color-primary-dark:   #1d4ed8;  /* hover */
  --color-primary-soft:   #dbeafe;  /* 알림 배경 */

  /* Neutrals (WCAG AA 통과 검증) */
  --color-text:           #111827;  /* 본문 — #1f2937보다 진하게 */
  --color-text-secondary: #4b5563;  /* 보조 — #6b7280에서 상향, AA 통과 */
  --color-muted:          #6b7280;  /* 캡션 (BG 흰색일 때만) */
  --color-line:           #e5e7eb;
  --color-bg:             #ffffff;
  --color-bg-soft:        #f9fafb;

  /* Semantic */
  --color-success:        #16a34a;
  --color-warning-bg:     #fef3c7;
  --color-warning-line:   #f59e0b;
  --color-error:          #dc2626;

  /* Typography */
  --font-family: "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic",
                 system-ui, -apple-system, sans-serif;
  --font-size-base:  16px;   /* 본문 — 50대 가독 */
  --font-size-lg:    18px;   /* 강조 */
  --font-size-h2:    28px;
  --font-size-h3:    22px;
  --font-size-sm:    14px;   /* 캡션 — 최소 */
  --line-height:     1.7;    /* 한글은 1.6~1.8 권장 */
  --letter-spacing:  -0.01em; /* 한글 자간 약간 좁게 */

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;

  /* Touch */
  --touch-min: 48px;  /* WCAG 2.5.5 + 모바일 권장 */
  --radius:    10px;
  --shadow-card: 0 2px 8px rgba(17, 24, 39, 0.06);
  --shadow-cta:  0 4px 14px rgba(37, 99, 235, 0.25);
}

/* 본문 기본 적용 */
html, body {
  font-family: var(--font-family);
  font-size:   var(--font-size-base);
  line-height: var(--line-height);
  letter-spacing: var(--letter-spacing);
  color:       var(--color-text);
  background:  var(--color-bg);
}

/* 버튼 — 터치 영역 보장 */
button, .btn, .stButton button {
  min-height: var(--touch-min);
  padding: 14px 24px;
  font-size: var(--font-size-base);
  font-weight: 600;
  border-radius: var(--radius);
  border: 0;
  cursor: pointer;
  transition: transform .08s, box-shadow .15s, background .15s;
}
.btn-pri, .stButton button[kind="primary"] {
  background: var(--color-primary);
  color: #fff;
  box-shadow: var(--shadow-cta);
}
.btn-pri:hover, .stButton button[kind="primary"]:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

/* 입력 — 50대 가독 */
input[type=text], input[type=email], input[type=password], textarea {
  min-height: var(--touch-min);
  padding: 12px 14px;
  font-size: var(--font-size-base);
  border: 1.5px solid var(--color-line);
  border-radius: var(--radius);
}
input:focus, textarea:focus {
  border-color: var(--color-primary);
  outline: 3px solid var(--color-primary-soft);
}

/* 카드 */
.card, .candidate-card, .result-card {
  padding: var(--space-5);
  border: 1px solid var(--color-line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  margin: var(--space-4) 0;
}

/* 모바일 — 360px 안전 */
@media (max-width: 480px) {
  :root { --font-size-base: 16px; --font-size-h2: 24px; }
  .btn, button, .stButton button { width: 100%; }   /* 풀폭 */
  .wrap, .block-container { padding: 16px 14px 80px !important; }
}

/* 한글 가독 추가 */
.korean-body { word-break: keep-all; overflow-wrap: break-word; }
```

### 폰트 권장

- **1순위**: Pretendard (한국어 최적, 무료 OFL) — `<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">`
- **2순위 폴백**: Apple SD Gothic Neo (iOS/macOS), Malgun Gothic (Windows), system-ui
- **금지**: Noto Sans KR(load 무거움), Nanum Gothic(자간 약함)

### Streamlit 적용 위치

`streamlit_app.py` L80-90 `_setup_page()` 의 `<style>` 블록을 위 CSS로 교체하고, `<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">`를 `st.markdown(..., unsafe_allow_html=True)` 로 주입.

랜딩 3종(`index.html` L11, `pricing.html` L9, `demo.html` L9)은 head에 동일 link + `:root` 변수 통일.

---

## 부록: 라인 인용 색인 (메인 에이전트 구현 시 참조)

### `streamlit_app.py`
- L80-90: `_setup_page` CSS 블록 → 팔레트 교체 대상
- L100, L118, L123, L128: spinner 메시지 → 예상 시간 명시
- L104, L108, L226, L229, L286: 에러/0건 메시지 → 다음 단계 추가
- L160: success 라벨 "표제 미상" 유지 (정확한 사서 용어)
- L168-170: 결과 메타 표시 → 폰트 16px 유지 권장
- L209: ISBN input placeholder → `9788936434120` 좋음, help 추가 권고
- L251-252: 사진 탭 caption → 카메라 가이드 강화
- L286-289: Vision 실패 시 후속 단계 부재 → 권고 #8
- L805-806: title/caption → 첫 화면 안내 카드 추가 위치
- L810: "040 ▾a" → "우리 도서관 부호" 단순화
- L815-820: API 키 안내 → 용어 부드럽게
- L836-844: 처음이신가요 expander → 메인에도 노출
- L859: tabs 5개 순서는 적절 (변경 불요)

### `landing/index.html`
- L11: `:root` 변수 → 팔레트 교체
- L13: line-height 1.55 → 1.7 권장
- L16: header h1 22px → 24px
- L18: hero h2 32px → 모바일에서 28px (L41 미디어쿼리 보강)
- L21-22: `.btn` padding/배경 → 권고 #6
- L29: card p 14px → 15px
- L37: input padding/font → 권고 #1
- L53-54: 헤드라인 → "카드 등록 없음 · 50건 무료" 보조 줄 추가
- L88-93: pricing 4개 plan → "추천" 강조 (현재 없음, pricing.html과 일관성)

### `landing/pricing.html`
- L9: body line-height 1.6 → 1.7
- L15-16: `.plan.recommended` → scale 1.05·shadow 강화
- L20: table font 14px → 15px
- L37: lead 직후 분기제 안내 강조 박스 권고
- L98-103: 비교 table cell padding 10px → 14px (50대 터치)

### `landing/demo.html`
- L9: line-height 1.6 → 1.7
- L17: meta div font 13px → 15px
- L20: pre font 12px → 13px (KORMARC 코드라 작아도 OK이나 13px 하한)
- L82: notice 박스 → font 15px

---

**총평**: 기능적으로는 사서 도메인을 깊이 이해한 제품. 다만 "보기·사용하기 좋아야 한다"는 PO 기준에서 보면 **타이포그래피 1점, 온보딩 2점**의 개선 여지가 가장 크다. 즉시 수정 Top 10만 적용해도 사서 첫인상 점수가 26 → 33점대로 올라갈 것으로 예측. 이후 중장기 5종이 매출 전환을 가속화한다.
