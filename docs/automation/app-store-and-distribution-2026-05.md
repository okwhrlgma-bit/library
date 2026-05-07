# 앱스토어·배포 채널 매트릭스 (Cycle 69)

> PO 통찰: "구글·애플 스토어에도 올려야 하는거 아님?"
> 답: **상황별 분기·웹 SaaS = 앱스토어 X·모바일 자동 = 회색**

## 1. SaaS 환경 × 배포 채널 매트릭스

### kormarc-auto B2C (사서 SaaS)

| 환경 | 채널 | 비용 | 앱스토어 |
|---|---|---|---|
| **웹 (Streamlit Cloud)** | URL = `kormarc-auto.streamlit.app` | ₩0 | ❌ 불필요 |
| 데스크톱 `.exe` | **GitHub Releases** (Cycle 65) | ₩0 | ❌ Sideload |
| 모바일 (옵션) | **PWA** (Streamlit URL·핸드폰 홈 추가) | ₩0 | ❌ 불필요 |
| 모바일 native | (선택·v1.0+) | $99/년 (iOS)·$25 (Android 1회) | 🟡 가능 (사서 도구 = 안전) |

→ **사서 B2C = 앱스토어 불필요·웹 + `.exe` + PWA = 충분**.

### 자동 클리커 SaaS

| 환경 | 채널 | 비용 | 앱스토어 |
|---|---|---|---|
| 데스크톱 `.exe` | GitHub Releases | ₩0 | ❌ Sideload |
| **모바일 안드로이드** (PO 통찰) | **Google Play** + APK 사이드로드 | $25 (1회) | 🟡 회색 (자동화 일부 거절) |
| 모바일 iOS | App Store | $99/년 | 🔴 거절 거의 확실 |

→ **자동 클리커 = PC GitHub Releases·모바일 = Play Store + APK 사이드로드**.

## 2. 앱스토어 정책 분석 (정직)

### A. Apple App Store (iOS)

#### 거절 정책
- **4.2.2 Background Activity** = 백그라운드 자동화 = 거절
- **2.5.4 Multitasking** = 매크로·자동 클릭 = 거절
- **5.2.1 Trademarks** = 게임 자동 = 약관 위반 거절

#### 통과 가능
- 단순 도구 (계산기·메모) = OK
- 사서 SaaS = 도구 = OK
- 자동 클리커 = **거의 100% 거절**

#### 우회
- TestFlight 베타 (테스터 100명·사이드로드)
- Apple Developer Program = $99/년
- iOS 17 = AltStore·사이드로드 (EU만 합법)

### B. Google Play Store (Android)

#### 통과 가능
- 자동화 앱 카테고리 존재 (Tasker·MacroDroid 통과)
- 사서 SaaS = OK
- 자영업·사무 자동 = OK

#### 거절 영역
- **게임 매크로** = "Cheating" 정책 위반 = 거절
- 광고 자동 클릭 = 거절
- 티켓팅·예약 봇 = 거절

#### 비용
- $25 (1회·평생)·연 갱신 X·간단

### C. PWA (Progressive Web App)

#### 장점
- ✅ 앱스토어 X·즉시 배포
- ✅ 핸드폰 홈 화면 = 앱처럼 작동
- ✅ 오프라인 지원 가능 (Service Worker)
- ✅ iOS + Android 둘 다 지원
- ✅ Streamlit + manifest.json = PWA 변환 가능

#### 단점
- ⚠ iOS = PWA 일부 제한 (Push 알림 = 16.4+)
- ⚠ "앱스토어 익숙 사용자" = 검색 X

#### 사서 B2C 정합
- 사서 = 핸드폰 = 사용 빈도 ↓ (PC 위주)
- but 보조 모바일 = "출퇴근·집 = 잠시 사용" 가능
- PWA = 1주 작업·즉시 활성

### D. GitHub Releases (PC·Sideload)

#### 장점
- ✅ ₩0·앱스토어 검증 X·자유
- ✅ Windows·Mac·Linux 모두 지원
- ✅ tag push 자동 빌드 (Cycle 65)

#### 단점
- ⚠ Windows = "보호된 PC" 경고 (1회)
- ⚠ Mac = "미등록 개발자" 경고 (1회)
- ⚠ 사서 IT L1·L2 = 경고 시 멈출 가능성

## 3. 추천 채널 매트릭스 (kormarc-auto B2C)

### Phase 1 (지금·1개월·₩0)
- ✅ Streamlit Cloud (URL)
- ✅ GitHub Pages (랜딩)
- ✅ GitHub Releases (.exe)

### Phase 2 (사용자 100명+·1~3개월)
- ✅ PWA 활성 (manifest.json·service worker)
- ✅ Supabase Auth (B2C)
- ⏳ Google Play (옵션·자동화 도구 카테고리)

### Phase 3 (사용자 1,000명+·3~6개월)
- ⏳ iOS PWA 우선 (App Store 거절 위험)
- ⏳ Android native (Play Store + APK 사이드로드 동시)

## 4. 자동 클리커 SaaS 채널 (별도)

### Phase 1 (PC 자영업·사무)
- ✅ GitHub Releases (.exe)
- ✅ Streamlit Cloud (UI·명령)

### Phase 2 (모바일 자영업·사무·1순위)
- ✅ **Google Play** (자영업 SNS 자동·법적 안전)
- ✅ APK 사이드로드 (1순위 한국)
- ⚠ iOS = PWA 우선 (App Store 거절)

### Phase 3 (모바일 게임 자동·옵트인·면책)
- ⚠ Google Play = 게임 매크로 거절 = APK 사이드로드만
- ⚠ iOS = TestFlight + Developer 사이드로드
- 면책 조항·옵트인 강조

## 5. PWA 활성 (Streamlit + manifest)

### 1주 작업 (kormarc-auto)

```python
# .streamlit/config.toml = Cycle 60 정합
# + 추가: PWA 매니페스트

# docs/landing/manifest.json
{
  "name": "kormarc-auto · 사서 KORMARC SaaS",
  "short_name": "kormarc-auto",
  "start_url": "https://okwhrlgma-bit.github.io/library/",
  "display": "standalone",
  "background_color": "#FAFAFA",
  "theme_color": "#0F4C9F",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}

# docs/landing/sw.js = Service Worker (오프라인 지원)
```

→ 사서 = 핸드폰 = "kormarc-auto" 홈 추가·앱처럼 사용.

## 6. 결제 채널 (앱스토어 통과 시 30% 수수료)

### 앱스토어 결제 = 30% 수수료
- iOS = 30% Apple Tax
- Android = 30% Play Tax
- 우리 ₩9,900 → ₩6,930 = 마진 ↓

### 우리 결제 (PortOne v2·웹·PWA)
- PG 수수료 약 3% (PortOne·NHN KCP)
- 우리 ₩9,900 → ₩9,603 = 마진 ↑

→ **PWA + 우리 결제 = 앱스토어 30% 회피 = 권장**.

## 7. 정직 헤더

- 본 매트릭스 = 외부 자료 (Apple 정책·Google·PWA)
- 모바일 사서 SaaS = 우선순위 ↓ (사서 = PC 위주)
- 자동 클리커 모바일 = Google Play + APK = 1순위
- iOS 자동 클리커 = 거절 위험·PWA 우선

## 8. 다음 단계 (PO 결정 시)

1. **kormarc-auto PWA 활성** (1주·manifest·sw)
2. **kormarc-auto Streamlit Cloud 배포** (PO 5분 외부 작업)
3. **자동 클리커 모바일 = Phase 2 결정** (사서 인터뷰 후)
4. **앱스토어 등록 = Phase 3** (사용자 1,000명+ 후)
