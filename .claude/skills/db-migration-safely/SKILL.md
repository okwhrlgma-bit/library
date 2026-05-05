---
name: db-migration-safely
description: production DB 스키마를 다운타임·데이터 손실 없이 변경. ADD COLUMN, DROP COLUMN, 인덱스 추가, 컬럼 타입 변경, 테이블 분할 등 모든 마이그레이션에 사용. 자동 실행 금지 — 항상 사람 승인 단계 포함.
---

# Safe DB Migration

production DB 변경은 **결제 다음으로 위험**한 작업입니다. 이 skill은 zero-downtime · 롤백 가능 · 데이터 손실 없음을 보장하는 절차입니다.

## 핵심 원칙

1. **모든 마이그레이션은 두 단계**: expand → contract
2. **롤백 가능 ≠ 데이터 보존**. 롤백해도 잃을 데이터를 미리 식별.
3. **마이그레이션 파일은 한 번 작성, 절대 수정 금지**. 새 마이그레이션으로 덮어쓰기.
4. **production 직전 staging에서 동일 데이터 크기로 리허설**.

## Expand–Contract 패턴

### 컬럼 추가 (안전)
```sql
-- expand: 새 컬럼은 NULL 허용 또는 default 있게
ALTER TABLE users ADD COLUMN tier TEXT DEFAULT 'free';
```
배포 → 코드가 새 컬럼 사용 → 안정화 → 끝.

### 컬럼 제거 (위험 — 4단계)
```
1. expand: 코드에서 컬럼 사용 중단 (읽기·쓰기 모두). 배포.
2. observe: 7일 모니터링. 어디서도 안 쓰이는지 로그·grep 확인.
3. contract: ALTER TABLE ... DROP COLUMN. 배포.
4. cleanup: 마이그레이션 파일 정리.
```

### 컬럼 이름 변경 (위험)
**절대 한 번에 RENAME 하지 말 것.** 다음으로 분해:
```
1. 새 컬럼 추가 (expand)
2. 코드: 양쪽에 쓰고, 새 컬럼에서 읽기 (dual write)
3. 백필: UPDATE ... SET new_col = old_col WHERE new_col IS NULL
4. 검증: 두 컬럼이 일치하는지 SELECT
5. 코드: 옛 컬럼 제거
6. 옛 컬럼 DROP (contract)
```

### 컬럼 타입 변경 (매우 위험)
타입 호환되면(VARCHAR(50)→VARCHAR(100)) 직접. 아니면 expand-contract:
- 새 타입 컬럼 추가 → 백필 → 코드 전환 → 옛 컬럼 제거.

### 인덱스 추가 (postgres)
큰 테이블이면 락이 걸려 다운타임. 항상:
```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```
`CONCURRENTLY`는 트랜잭션 안에서 못 씀 → 마이그레이션 도구가 지원하는지 확인.

### NOT NULL 제약 추가 (위험)
기존 데이터에 NULL 있으면 실패. 절차:
```
1. 기존 NULL 값 백필 (UPDATE)
2. CHECK 제약으로 검증
3. NOT NULL 적용
```

## 실행 전 체크리스트

```
[ ] 마이그레이션 SQL을 staging에서 실행 — 성공
[ ] staging 데이터 크기가 production의 10% 이상
[ ] 락 시간 측정 (EXPLAIN ANALYZE 또는 pg_locks 모니터링)
[ ] 롤백 SQL 작성 + 테스트 실행 가능 검증
[ ] 데이터 손실 가능 여부 명시 (있으면 백업 우선)
[ ] 배포 시간대: 트래픽 최저 시간 + 충분한 대기 캐파
[ ] 알림 채널에 "DB 마이그레이션 시작" 사전 공지
[ ] 사람 승인 (!!! 자동 실행 금지)
```

## 자동화 정책

이 skill에서 Claude는:
- **할 수 있음**: 마이그레이션 SQL 초안 작성, expand-contract 분해, 락 분석
- **할 수 없음**: production DB에 직접 실행, `npm run db:migrate:prod` 류 명령
- **항상**: 위 체크리스트를 PR 본문에 첨부

## 사고 시 (마이그레이션 후 문제)

1. 즉시 코드 롤백 (이전 deploy로 revert)
2. 데이터 손상 여부 확인 (SELECT count 비교)
3. 마이그레이션 자체 롤백은 **신중히** — expand만 했으면 그냥 두고 코드만 돌림
4. `learnings.md`에 사후 기록

## 참고 도구
- migration: drizzle-kit, knex, alembic, prisma
- 락 모니터링: `pg_stat_activity`, `pg_locks`
- 락 없는 인덱스: `CREATE INDEX CONCURRENTLY` (PostgreSQL)
- MySQL: `pt-online-schema-change` 또는 `gh-ost`
