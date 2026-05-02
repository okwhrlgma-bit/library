# Part 43 — 사서 친화 UI/UX·워크플로우 종합 설계 (2026-05-02)

> PO 명령: "사용자 입장에 좋은 UI UX 및 디자인 고안 및 적용 + 사용자 입장 워크플로우 구성·편의성 확인"
> 검증: Pencil & Paper Dashboard Patterns + 2026 Enterprise UX Best Practices + streamlit-shadcn-ui

---

## 0. 사서 4 페르소나 + 비전문가 운영자 매핑

| 페르소나 | 비중 | 핵심 워크플로우 | UI 우선 |
|---------|------|----------------|--------|
| 매크로 사서 (★ 1순위 ICP) | 자관 8명 중 1 | ISBN 100건 일괄 → CSV·ZIP | 키보드 우선·일괄 입력 |
| 수서 사서 | 자관 8명 중 2 | 사진 업로드 → 서지 검토·확정 | 모바일 카메라·미리보기 |
| 종합 사서 | 자관 8명 중 3 | 운영 대시보드·통계 | 정보 밀도·5초 발견 |
| 콘텐츠 사서 | 자관 8명 중 2 | 북큐레이션·트렌드 | 시각화·클러스터 |
| **학부모·자원봉사자** ★ 신규 | 학교·작은 86% | ISBN 1건 → 사서 검수 큐 | 5분 학습·1버튼 |
| **사서교사** ★ | 학교 12.1% | 자원봉사 입력 일괄 검수 | 검수 큐·일괄 승인 |

---

## 1. 검증된 UX 원칙 (2026 벤치마크)

### A. 5초 발견 룰 (Pencil & Paper)
"사용자가 필요한 정보를 5초 안에 찾아야 한다"
- kormarc-auto 홈 = 4 메인 액션 카드 (ISBN 단건·검색·사진·일괄)
- 상단 검색바 + 사이드바 페르소나별 진입

### B. Just-in-Time Onboarding (+37% 활성화)
"긴 투어 X, 작업 시점 tooltips ✅"
- ISBN 입력 시점에만 "13자리 입력 또는 카메라 ON" 안내
- 일괄 처리 시점에만 "CSV 양식 다운로드" tooltip
- 사용자 막힘 자동 감지 → 5분 가이드 popup

### C. 정보 밀도 vs 명료성 (46.7% 과부하 회피)
"strict grid + typographical hierarchy"
- 12 column grid (Tailwind 표준)
- H1 24px / H2 18px / Body 14px / Caption 12px
- 색상: Primary 1색 + 상태 (success/warning/error)

### D. AI-Guided Onboarding (+27% 활성화)
"카카오 알림톡 Day 1·3·7·30 자동" (Part 41)

### E. 진보적 공개 (Progressive Disclosure)
- 처음 가입 = ISBN 1건 단순 입력
- 5건 처리 = 일괄·사진 옵션 자동 노출
- 50건 처리 = 사서별 prefix·880·KDC 고급 옵션
- 100건+ = 대시보드·통계 자동 노출

---

## 2. 페르소나별 워크플로우 설계

### 워크플로우 1: 매크로 사서 (1순위 ICP)

```
[홈] → [일괄 처리] (1 클릭)
  ↓
[CSV 업로드 또는 ISBN 텍스트 붙여넣기] (직접 키보드)
  ↓
[자관 prefix 자동 검출] (자동·5초)
  ↓
[KORMARC 일괄 생성] (병렬 처리·진행바)
  ↓
[CSV·ZIP·MRC 다운로드] (3 옵션 동시)
  ↓
[KOLAS·DLS 반입 안내] (1 클릭 가이드)
```

**총 시간**: 100건 처리 5~10분 (기존 800분 → 95% 절감)
**키보드 단축키**: Ctrl+V (붙여넣기) → Enter (실행) → Ctrl+S (저장)

### 워크플로우 2: 수서 사서 (모바일 카메라)

```
[모바일 PWA] (가입 후 홈 화면 추가)
  ↓
[카메라 촬영] (책 표지·바코드)
  ↓
[ISBN 자동 인식] (Claude Vision + Clova OCR)
  ↓
[서지 미리보기 카드] (245·100·260·049 자동)
  ↓
[검토·수정 또는 확정] (필요 필드만 편집)
  ↓
[저장 + 다음 책 카메라]
```

**총 시간**: 1권 1~2분 (기존 8분 → 75% 절감)
**모바일 친화**: 한 손 조작 가능, 카메라 즉시 활성화

### 워크플로우 3: 종합 사서 (대시보드)

```
[대시보드 홈] (5초 발견)
  ┌─ 오늘 처리량 (큰 숫자)
  ├─ 이번 주 처리량 + 사서별 차트
  ├─ KOLAS 반입 대기 (알림 배지)
  └─ 자관 정합률 (99.82% 게이지)

[클릭 → 상세] (Just-in-Time)
  ↓
[필터: 사서·자료유형·기간]
  ↓
[차트 + 표 동시 표시]
  ↓
[CSV 내보내기 또는 PDF 보고서]
```

**정보 밀도**: 12 column grid·H1 핵심 1개·차트 4개 max
**5초 발견**: 가장 중요한 메트릭 = 화면 좌상단 (Z-pattern)

### 워크플로우 4: 콘텐츠 사서 (북큐레이션)

```
[북큐레이션 탭]
  ↓
[주제 클러스터 시각화] (자관 컬렉션 자동 분류)
  ↓
[강점·약점 영역 색상] (red·yellow·green)
  ↓
[신간 추천 (외부 트렌드 + 자관 갭 분석)]
  ↓
[큐레이션 리스트 생성·인쇄]
```

### 워크플로우 5: 학부모·자원봉사자 (★ 5분 학습)

```
[홈] → [신간 등록] (큰 버튼 1개)
  ↓
[ISBN 13자리 입력] (또는 카메라)
  ↓
[자동 변환 진행 안내] (5초 진행바·메시지)
  ↓
[완료 + 사서교사 검수 큐 자동 등록]
  ↓
[다음 책 등록 또는 종료]
```

**비전문가 친화**:
- KORMARC·KOLAS·서지 등 전문 용어 0개 (홈 화면)
- 색상·아이콘 위주 (텍스트 보조)
- 음성 안내 옵션 (한국어 TTS)

### 워크플로우 6: 사서교사 (학교 12.1% — 일괄 검수)

```
[검수 큐] (자원봉사·학생 등록한 신간 N건 대기)
  ↓
[일괄 미리보기] (카드 그리드)
  ↓
[일괄 승인 / 개별 검토 / 반려]
  ↓
[KOLAS·DLS 자동 반입]
```

**사서교사 시간 80% 절감**: 권당 8분 → 일괄 검수 1분

---

## 3. 사용자 편의성 검증 매트릭스

| 항목 | 검증 | kormarc-auto 현재 | 개선 후 (Part 43 적용) |
|------|------|------------------|----------------------|
| 5초 정보 발견 | Pencil & Paper | ⚠️ 6 메인 탭 (과다) | ✅ 4 메인 카드 (페르소나별 사이드바) |
| 5분 학습 | librarian-5min-cheatsheet.md | ✅ 적용됨 | ✅ 유지 + 음성 가이드 |
| Just-in-Time tooltip | +37% 활성화 | ❌ 없음 | ✅ streamlit-shadcn-ui Tooltip |
| 모바일 PWA | 60% B2B 모바일 | ⚠️ Streamlit 기본 반응형 | ✅ PWA 변환 (ADR-0029) |
| WCAG 2.2 AA | KWCAG 인증 | ❌ 미감사 | ✅ ui-ux-pro-max 자동 감사 |
| Progressive Disclosure | +27% 활성화 | ⚠️ 모든 옵션 동시 표시 | ✅ 사용량 기반 단계적 노출 |
| 비전문가 친화 (학부모·자원봉사) | 학교 86% | ❌ 사서 전문 용어 노출 | ✅ 페르소나별 어휘 분기 |
| 음성 안내 | 인클루시브 | ❌ 없음 | ✅ 한국어 TTS 옵션 |
| 키보드 단축키 (매크로 사서) | 매크로 사서 ICP | ❌ 마우스 위주 | ✅ Ctrl+V·Enter·Ctrl+S |
| AI-Guided onboarding | +27% | ⚠️ Day 1 환영만 | ✅ Day 1·3·7·30 (Part 41) |

---

## 4. UI/UX 적용 — 검증된 도구·라이브러리

### A. ui-ux-pro-max 스킬 (이미 cc-automation §3.2)
- 161 컬러 팔레트
- 57 폰트 페어링
- 99 UX 가이드라인
- WCAG 자동 감사

### B. streamlit-shadcn-ui (검증)
- shadcn/ui 모던 컴포넌트 (Modal·Hovercard·Badge)
- Tailwind CSS 커스터마이징
- 컴포넌트 중첩 지원
- iframe 단일 렌더링 (성능 ↑)

### C. streamlit-tailwind
- Tailwind utility class 직접 사용
- 반응형 grid 표준화

### D. dantheand/streamlit-pwa-template (Part 17)
- PWA 변환 (manifest.json + service worker)
- 모바일 홈 화면 추가
- 오프라인 지원

### E. 부산대 로마자 변환기 + Clova OCR (Part 17·19)
- 880 필드 자동 (수서 사서 시간 ↓)
- 책 사진 인식 정확도 +15%

---

## 5. AUTONOMOUS_BACKLOG 추가 (Part 43)

- [ ] **streamlit_app.py UI 재설계 ADR-0059** (4시간·L3) ⭐⭐
  - 4 메인 카드 + 페르소나별 사이드바
  - shadcn-ui + Tailwind 적용
  - Just-in-Time tooltips
  - Progressive Disclosure
  - Q1 +5 (사용자 친화 = 사서 결제 의향)
- [ ] **PWA 변환 ADR-0029 본격 가동** (1.5시간·L2)
  - dantheand template 차용
  - manifest.json + service worker
  - 모바일 홈 화면 추가
- [ ] **WCAG 2.2 AA 자동 감사 (ui-ux-pro-max)** (2시간·L2)
  - 전체 화면 감사 → 위반 항목 자동 수정
  - KWCAG 인증 사전 진단 (사용자_TODO U-41 정합)
- [ ] **음성 안내 한국어 TTS 옵션** (1.5시간·L2)
  - Web Speech API (브라우저 내장)
  - 학부모·자원봉사·시각장애인 친화
- [ ] **페르소나별 어휘 분기 시스템** (2시간·L3 ADR-0060)
  - 사서 모드: KORMARC·MARC·서지·전거 사용
  - 비전문가 모드: "책 정보 자동 등록" 등 일상 어휘
  - 가입 시 페르소나 선택 → 어휘 자동 분기
- [ ] **키보드 단축키 시스템** (1시간·L2)
  - Ctrl+V (ISBN 붙여넣기·일괄)
  - Enter (실행)
  - Ctrl+S (저장)
  - ? (단축키 안내)
- [ ] **사서교사 검수 큐 화면** (2시간·L2)
  - 자원봉사·학생 등록 신간 대기
  - 카드 그리드 일괄 미리보기
  - 일괄 승인 / 개별 / 반려 버튼
- [ ] **콘텐츠 사서 북큐레이션 시각화** (3시간·L2)
  - KDC 클러스터 차트
  - 자관 강점·약점 색상 (heatmap)
  - 신간 트렌드 (외부 + 자관 갭)
- [ ] **종합 사서 대시보드 5초 발견 룰** (2시간·L2)
  - Z-pattern 좌상단 핵심 메트릭
  - 12 column grid
  - H1 24px / H2 18px / Body 14px

---

## 6. UI/UX 설계 원칙 (헌법 §"user friendly mandate" 정합)

```
1. 5초 발견 룰
2. 5분 학습 보장
3. Just-in-Time onboarding
4. Progressive Disclosure
5. 페르소나별 어휘 분기
6. 비전문가 친화 (학부모·자원봉사)
7. WCAG 2.2 AA 이상
8. 모바일 PWA (오프라인)
9. 음성 안내 (인클루시브)
10. 키보드 우선 (매크로 사서 ICP)
```

→ 매 commit 시 이 10원칙 자동 검증 (qa-validator Layer 추가).

---

## 7. 검증된 사례 매핑 (Part 35 정합)

| UI/UX 영역 | 검증 1차 | 검증 2차 (조합) |
|-----------|---------|----------------|
| 5초 발견 | Pencil & Paper | + Z-pattern + Tailwind grid |
| Just-in-Time | +37% 활성화 | + AI-guided +27% (Day 1·3·7·30) |
| 정보 밀도 | 46.7% 과부하 회피 | + Progressive Disclosure |
| PWA 모바일 | dantheand template | + Anvil 비교 + 자체 호스팅 |
| WCAG 2.2 | ui-ux-pro-max 161+57+99 | + KWCAG 90점 인증 (U-41) |
| Streamlit + shadcn | streamlit-shadcn-ui | + Tailwind + 컴포넌트 nest |

---

> **이 파일 위치**: `kormarc-auto/docs/research/part43-ui-ux-workflow-design-2026-05.md`
> **활용**: streamlit_app.py UI 재설계 + qa-validator UI/UX Layer 추가 + KWCAG 인증 사전 진단
