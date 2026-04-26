# ADR 0004 — SQLite 마이그레이션 MVP-2로 연기

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

현재 사용량 DB·signup 로그·자관 인덱스 모두 JSON/JSONL 파일.
운영 감사(`docs/real-world-operations-audit.md` 단기 #3): "동시 사서 100명 시 `usage.json` 전체 read/write 락 충돌 → SQLite WAL 모드로 무중단 전환".

옵션:
1. 즉시 SQLite 전환 (1일 작업 + 기존 데이터 마이그레이션)
2. MVP-2 (베타 20명+ 도달 시) 전환
3. PostgreSQL 직행 (클라우드 이전과 동시)

## 결정

**MVP-2 (베타 20명+ 또는 동시 사용 10건/초+)로 연기**.

## 결과

- 베타 기간 단순성 유지 (PO가 jsonl 파일 그대로 열람·점검 가능)
- 사용량 DB 락 충돌 위험은 감수 (베타 50명 미만에서는 문제 안 됨)
- `_lock = Lock()` 단일 프로세스 락으로 충돌 거의 0

## 트레이드오프

✅ **장점**
- 코드 단순 (`json.load` / `json.dump`만)
- 디버깅 쉬움 (jsonl 직접 확인)
- 백업 단순 (`scripts/backup_logs.py` zip 1개)
- 의존성 0 (SQLite는 표준 라이브러리지만 schema·마이그레이션 도구 필요)

❌ **단점**
- 동시 100건/초 부하 시 락 대기
- 큰 로그(1년치) 분석 시 jsonl 전체 읽기 O(N)
- 트랜잭션 (signup + initial usage 동시 쓰기) 원자성 약함

## 완화 조치

- `scripts/rotate_logs.py` 90일 자동 회전 → jsonl 크기 통제
- 사용량 DB는 `_lock` + atomic write (tmp → rename)
- 베타 20명 도달 직전 SQLite 전환 PR 준비 (`docs/migration-plan-sqlite.md` 사전 작성)

## 트리거 (전환 시점)

다음 중 하나 충족 시 즉시 SQLite 전환:
- 동시 활성 사서 ≥ 20명 (admin/stats에서 daily active users)
- `logs/usage.jsonl` ≥ 100MB
- `usage.json` 락 대기 시간 측정 ≥ 100ms (관측되면 즉시)
- 결제 분쟁 발생 시 (트랜잭션 무결성 증빙 필요)

## 6개월 후 되돌릴 수 있는가?

**부분** — JSON → SQLite 전환은 1회성 마이그레이션 스크립트로 가능. 반대 방향(SQLite → JSON)은 거의 불필요.

## 관련 자료

- `src/kormarc_auto/server/usage.py` — 현재 JSON 구현
- `docs/real-world-operations-audit.md` 단기 #3
