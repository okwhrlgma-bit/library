---
name: payment-handling
description: 결제·구독·환불 코드 변경 시 항상 호출. webhook 시그니처 검증, idempotency, PCI 노출 차단을 강제.
---

결제 코드를 만지면 다음 체크리스트를 반드시 통과해야 한다.

## 1. Webhook 시그니처 검증

❌ **틀림**:
```ts
const event = req.body  // 검증 없이 신뢰
```

✅ **맞음** (Stripe 예시):
```ts
const sig = req.headers['stripe-signature']
const event = stripe.webhooks.constructEvent(rawBody, sig, webhookSecret)
```

토스페이먼츠도 동일 — `webhookSecret`으로 HMAC 검증.

## 2. Idempotency

같은 이벤트가 두 번 와도 부작용은 한 번만:

```ts
// 이벤트 ID로 중복 차단
const exists = await db.processedEvents.findUnique({ where: { id: event.id } })
if (exists) return res.json({ ok: true, skipped: true })

await db.$transaction([
  // 실제 처리
  db.processedEvents.create({ data: { id: event.id, type: event.type } })
])
```

## 3. 카드 정보 절대 비저장

- ❌ 카드번호·CVC·만료일을 우리 DB에 저장하지 마라
- ❌ 로그에 찍지 마라 (`logger.info(payment)` 같은 거 금지)
- ✅ 결제 게이트웨이의 token만 저장 (Stripe `customer.id`, 토스 `customerKey`)

## 4. 금액은 항상 정수(가장 작은 단위)

- ❌ `amount: 19.99` (float, KRW에서는 무의미)
- ✅ `amount: 1999` (KRW면 그대로 1999원, USD면 cents)
- DB 컬럼은 `INTEGER` 또는 `BIGINT`. NEVER `FLOAT`/`REAL`.

## 5. 통화 명시

```ts
{ amount: 19900, currency: 'KRW' }  // 항상 currency 같이
```

## 6. 환불·취소 권한

- 자율 시스템이 환불을 자동 처리하지 못하게 권한 분리
- `.claude/settings.json`의 `permissions.deny`에 `Bash(stripe:refunds:*)` 같은 패턴 추가
- 환불은 사람이 트리거한 슬래시 커맨드로만

## 7. 테스트 필수

- happy path: 정상 결제→웹훅→DB 갱신
- 위조 시그니처: 거부됨 확인
- 중복 이벤트: 한 번만 처리됨 확인
- 환불 후 다시 환불: 거부됨 확인

## 8. 결제 코드 PR 체크리스트 (PR 본문에 복붙)

```
- [ ] webhook 시그니처 검증
- [ ] idempotency 처리
- [ ] 카드 정보 저장/로그 없음
- [ ] 금액 정수 + currency 명시
- [ ] 회귀 테스트 (위조/중복/이중환불)
- [ ] decisions.md에 결정 추가 (필요 시)
- [ ] 사람 검토 받음 (자동 머지 금지)
```

## 9. 자동 거부

이 skill이 활성화된 동안 다음은 자동 거부:
- 카드번호 정규식(`\d{13,19}`)이 코드에 등장
- `console.log(.*payment.*)` 패턴
- webhook 핸들러에서 `req.body`를 직접 사용 (검증 없이)

위반 시 작업 중단하고 사람 호출.
