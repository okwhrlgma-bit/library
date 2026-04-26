# Architecture Decision Records (ADR)

> kormarc-auto의 큰 결정 이력. 6개월 후 "왜 이렇게 했지?" 답변용.
> 패턴: PO 자율성 가이드 §8 (Spec-Driven Development) — 명세를 진실 원천으로.

## 작성 규칙

- 매 큰 결정 1건 = 1 파일 (`NNN-제목.md`)
- 형식: 컨텍스트 → 결정 → 결과 → 트레이드오프
- 번호는 0001부터, 제목은 영문 kebab-case
- 결정 변경 시 새 ADR로 supersedes 명시 (기존 파일 그대로 보존)

## 상태 코드

- `proposed` — 검토 중
- `accepted` — 적용 중
- `superseded by NNN` — 후속 ADR로 대체됨
- `deprecated` — 미적용 (이유 명시)

## 인덱스

| 번호 | 제목 | 상태 |
|---|---|---|
| 0001 | byok-anthropic-api-key | accepted |
| 0002 | cloudflare-tunnel-mobile | accepted |
| 0003 | per-record-pricing-100krw | accepted |
| 0004 | byok-vs-managed-keys | accepted |
| 0005 | sqlite-deferred-mvp2 | accepted |
| 0006 | claude-code-permissions-policy | accepted |
