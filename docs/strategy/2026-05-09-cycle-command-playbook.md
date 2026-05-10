# Cycle 별 즉시 실행 명령서 (Cycle 735·PO #84 산출물 #4)

> **목적**: 매 cycle 자율 운영 시 Claude가 바로 실행할 수 있는 명령 모음.

---

## 매 Cycle 표준 흐름 (10분)

### 1. 자동 health check (의무·30초)
```python
from observability.deployment import check_url_health
for u in [10 SaaS URL]:
    print(check_url_health(u).label_kr)
```

### 2. cycle 작업 (8분·우선순위 트리)
```
A. 5-cycle 의무 (자기 진단·박제) → cycle % 5 == 4면 우선
B. PO 명령 응답 → 도착 시 즉시
C. 비매출 코드 시드 (priority_3·신규 SaaS) → 매출 데이터 30일 후
D. 매출 가속 시드 (Bundle·cross-saas·SEO·monitoring) → 우선
E. 박제 (사용자_TODO·_meta·메모리) → 매 5 cycle
```

### 3. ScheduleWakeup (10분 후·1분)
```python
ScheduleWakeup(delaySeconds=600, ..., prompt="야간 자율 진행")
```

---

## 작업 카테고리별 cycle별 명령

### 카테고리 A: 매출 활성 (priority 1·매 cycle)

```
- Polar 영구 buy URL 추가 시드 (PO 키 변경 시)
- landing CTA 강화 (FOMO·socialproof·testimonial)
- Bundle CTA cross-link 검증
- Dashboard 갱신 (revenues·traffics 실 데이터 후)
- 자동 monitoring (매 cycle health check + 이상 시 즉시 fix)
```

### 카테고리 B: 자동화 (priority 2·매 cycle)

```
- _shared 모듈 보강 (DRY·cross-saas)
- 자동 패치 trigger (cs_helper·complaint·auto_repair)
- webhook secret 등록 자동 (PO secret 공유 시)
- Vercel env vars 자동 등록
```

### 카테고리 C: 신규 시장 (priority 3·30일 후 보류)

```
- 30일 매출 데이터 수집 우선
- Top 3 결정 후 winner 깊이 강화
- Kill list 결정 후 sunset 처리
- 새 priority_3 시드 = 매출 데이터 30일 후
```

### 카테고리 D: 박제 (의무·매 cycle 끝)

```
- 매 5 cycle = 자기 진단 박제 (118·123·128번째)
- 매 cycle 끝 = 사용자_TODO 점검 (변동 없으면 skip)
- 매 5 cycle = _meta/00 갱신 (변동 ≥ 5 시)
- PO 영구 명령 = 메모리 박제 즉시 (#74·#76·#79·#80 정합)
```

---

## 즉시 실행 가능 명령 (PO 외부 작업 후)

### PO Polar publish 후 (15분 후)
```
1. 9 SaaS Polar product list 검증
2. 영구 buy URL HTTP 200 확인
3. checkout flow 실 결제 시뮬 (자관 1건)
4. Polar webhook secret 등록 → Vercel env vars 자동 추가
```

### PO Streamlit Cloud Deploy 후
```
1. https://kormarc-auto.streamlit.app HTTP 200 확인
2. license gate 검증 (LS·Polar 키 기반)
3. 본 앱 4 탭 UI (ISBN·검색·사진·일괄) 실 호출
4. dogfooding 1건 KORMARC 처리·시간 측정
```

### PO 자관 dogfooding 결제 후
```
1. Polar webhook 수신 → MongoDB 로그
2. revenues dict 갱신 (kormarc-auto = 매출 ₩7,000+)
3. dashboard 자동 재생성 (Top 3·Kill list)
4. critical_lockup 해소 시그널 박제
```

---

## 5 cycle 사이클 (Cycle 729~734 → Cycle 735~739)

| Cycle | 작업 |
|---|---|
| 735 (지금) | 산출물 #4·#10 박제 (전략 가이드 4건) |
| 736 | 산출물 #8·#9 박제 (Kill 사후·Cross-SaaS 시너지) |
| 737 | _meta/00 갱신 (Cycle 713 → 737·24 cycle 진척) |
| 738 | priority_3 #100 또는 기존 SaaS 강화 (FAQ·terms·webhook) |
| 739 | 119번째 자기 진단 (5-cycle 의무) |

---

## 자율 운영 안전 가드 (영구)

```
1. 비가역 액션 차단 (rm -rf·git push --force·DROP TABLE)
2. PO 결제·인증 키 변경 X
3. 자관 데이터 git commit X (헌법 §14)
4. 외부 발사 (ProductHunt·HN·X) = PO 명시 후만 (ADR 0052)
5. CircuitBreaker (3회·$10·1시간 한계)
6. 차단 paths: 결제·인증·.env·CI yaml
7. 매 cycle 끝 ScheduleWakeup (PO STOP 시 정지)
```

---

## 결론

이 playbook = 매 cycle Claude 자율 실행 표준.
PO 명령 도착 시 = 즉시 응답·기존 작업 일시 중단.
의문 시 = 사용자_TODO 갱신·메모리 박제·다음 cycle 자동.
