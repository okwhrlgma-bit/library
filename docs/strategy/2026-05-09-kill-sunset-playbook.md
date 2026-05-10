# Kill·Sunset 사후 처리 매뉴얼 (Cycle 736·PO #84 산출물 #8)

> **목적**: 30~60일 매출 데이터 후 SUNSET 결정된 SaaS의 안전한 폐기 절차.
> **헌법**: 비가역 액션 차단·결제·자관 데이터 보호·사용자 알림 의무.

---

## SUNSET 결정 트리거

```
score_saas(name) < KILL_LIST_THRESHOLD (60점)
AND 매출 데이터 ≥ 30일
AND PO 명시 승인 (자율 X·법적 위험·사용자 영향)
```

---

## SUNSET 8 단계 (PO 승인 후)

### Step 1: 사용자 알림 (의무·30일 전)
```
- 결제 사용자 = 이메일 자동 (cs_helper)
- "30일 후 서비스 종료·환불 또는 다른 SaaS 이전 안내"
- 환불 정책: 미사용 부분 = 100% 환불 (전자상거래법 §17 정합)
- 데이터 export = CSV·JSON·30일 다운로드 가능
- Bundle 사용자 = "Bundle 가격 동일·해당 SaaS 제외" 알림
```

### Step 2: Polar 제품 archive (자동 가능)
```python
# Polar API
client.update_product(product_id, {"data": {"attributes": {"status": "archived"}}})
# 신규 결제 차단·기존 구독 = 다음 갱신 시 자동 종료
```

### Step 3: Vercel landing 리다이렉션 (Claude 자동)
```
- /index.html → "서비스 종료·다른 SaaS 안내" 페이지
- 또는 Bundle 또는 winner SaaS 페이지로 redirect
- robots.txt: noindex·검색 색인 제거
- vercel.json rewrites X (정적 redirect)
```

### Step 4: GitHub repo archive (PO 의무·5분)
```
gh repo archive okwhrlgma-bit/<repo-name>
또는 Web UI Settings → Archive this repository
```

### Step 5: 도메인 redirect (선택·5분)
```
Custom Domain 사용 시 = winner SaaS로 redirect
도메인 미사용 시 = 자동 만료·1년 후 폐기
```

### Step 6: 데이터 마이그레이션 (cross-saas 정합)
```
- receipt-ocr SUNSET 시 → simple-budget으로 거래 이전
- simple-todo SUNSET 시 → general-docs 회의록·계획 이전
- 사용자 동의 필수 (PIPA 정합)
```

### Step 7: _shared·30-apps 코드 archive (Claude 자동)
```
30-apps/<번호>_<이름>/_archived/  ← 이름 변경 (rmdir X·archive)
README.md 갱신: "SUNSET·archived YYYY-MM-DD"
git commit: "chore(<n>): sunset archive"
```

### Step 8: 박제 (영구·매월 보고)
```
docs/sunset/<saas-name>-<date>.md
- SUNSET 이유 (overall score·매출·시장·차별화)
- 사용자 마이그레이션 결과 (몇 명·어디로)
- 학습 (다음 SaaS·avoid·apply)
- 메모리 박제: feedback_sunset_<name>.md
```

---

## 차단 액션 (PO 명시 X)

```
🔴 절대 차단:
- git rm -rf <repo> (사용자 데이터·git history 영구 손실)
- Polar 제품 즉시 삭제 (구독자 결제 자동 갱신·환불 X)
- Vercel project 즉시 삭제 (검색 색인·외부 link broken)
- MongoDB collection drop (사용자 거래 기록 손실·법적 위험)

⚠ PO 승인 후만:
- 도메인 폐기·도메인 재할당
- GitHub organization 변경
- 사용자 데이터 재배포·삭제
```

---

## SUNSET 사전 평가 (현재·정적 점수)

```
Top 3 후보 (KEEP):
1. kormarc-auto       44점 ⭐ (PO ★★★·KOLAS)
2. group-member-manage 29점
3. receipt-ocr-auto    29점

SUNSET 우선 후보:
- diet-workout-tracker 21점 (MyFitnessPal 강함·B2C 헬스 niche)
- simple-todo          23점 (Todoist·Notion 강함·생산성 niche)
- medication-reminder  26점 (노년 검색 약함·CS 부담 ↑)
```

→ 30일 매출 데이터 + PO 결정 후만 SUNSET. 현재 = 정적 사전 평가만.

---

## 결론

SUNSET = 8 단계·PO 명시 후만·법적·사용자 보호 우선.
빠른 sunset = 매출 가속 가능 (winner 1~3에 집중).
실패한 SaaS = 학습 자산·메모리 박제·다음 SaaS 시드 시 avoid.
