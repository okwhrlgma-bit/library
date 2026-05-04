# ADR 0029 — Audit log + AI disclaimer + 처리방침 §28의8 6항목 강화

- 상태: Accepted (2026-05-04·갈래 A Cycle 9 + 갈래 B Cycle 10B 통합)
- 일자: 2026-05-04
- 트리거: 갈래 A 헤더 P3 (588 + audit log) + 외부 858 출처 P29 (처리방침)·인공지능 기본법 §31 시행 2026.1.22

## Context

### A. AI 출처 표시 의무 (인공지능 기본법 §31)
- 시행 2026.1.22 = 생성형 AI 결과물 표시 의무
- 미표시 = 사서 신뢰 저하 + 향후 분쟁 시 증거 부재

### B. PIPA §28의8 국외이전 6항목 (외부 858 출처 #1 위험)
- PIPC 결정 2024-010-184 동일 사유 시정 처분 선례
- Anthropic Claude US 호출 = 핵심 기능
- 6항목 누락 = 즉각 적발 위험

### C. PIPA §35 열람권 + §36 파기 요청권
- 정보주체 audit log 조회 + 파기 요청 = endpoint 필수

## Decision

### 1. Audit log persistent store (Cycle 9 P13)
- `src/kormarc_auto/audit/store.py` 신규
- JSONL append-only·월별 파티션 (~/.kormarc-auto/audit/{YYYY-MM}/records.jsonl)
- AuditEvent dataclass = record_id·action·timestamp·user·model·hash·field·note·extra
- 6 actions: create / regenerate / edit / accept / reject / delete_request
- 7년 보관·동시성 안전 (POSIX append guarantee)
- 12 tests passing

### 2. 처리방침 §9 강화 (외부 858 출처 P29)
- 5 수신자 × 6항목 (Anthropic·AWS·PortOne·Google·Cloudflare)
- 이전 항목·국가·일시·받는 자·목적·거부 방법
- §28의8 ①항 3호 동의 갈음 근거 명시

### 3. §9의2 자동화된 결정 (§37의2) 입장
- 사서 검토 전제 = "완전 자동화" X
- 도서 메타데이터 = 일반 개인정보 X
- 설명요구 30일 내 회신 채널
- ⚠ 조문 정정: §35의2 = 전송요구권 / §37의2 = 자동화 결정

### 4. AI disclaimer 4곳 동시 표시
- `docs/legal/ai-disclaimer-2026-05.md` 신규
- UI · 처리방침 · API 응답 메타 · CLI info 4곳
- KORMARC 588 한국어 stamp
- 환각 위험 영역 매트릭스 (6XX 높음·245 낮음)

### 5. Cycle 10A P14 통합
- `kormarc/field_status.py` (FieldState·RecordReviewState·can_transition)
- 18 tests passing
- ghost text UI 분기 (ai_generated → accepted/rejected/edited)
- 화면 상단 "전체 거부" escape hatch
- 헌법 §4 (사서 검토 보존) 정합

## Consequences

### Positive
- PIPC 시정 처분 선례 회피 (§28의8 6항목)
- 사서 신뢰 ↑ (AI 명시·588 stamp·audit log)
- 인공지능 기본법 §31 사전 대응
- per-field accept/reject UI = 헌법 §4 강화
- audit log = 향후 분쟁 시 증거

### Negative / Trade-off
- UI 복잡도 증가 (ghost text + accept/reject)
- 사서 검토 시간 증가 (모든 필드 명시 accept 필요)
- audit log 디스크 증가 (월 100건·1년 ≈ 1MB·무시 가능)

### Risk Mitigation
- audit JSONL 손상 시 = JSON skip + log warning (silent fail X)
- delete_request = soft tombstone (법적 추적 가능)
- env override (`KORMARC_AUDIT_DIR`) = 운영 중 경로 변경 가능

## Alternatives Considered

### Alt 1: SQLite audit
- Reject: append-only JSONL = 단순·diff 가능·복잡한 의존성 X

### Alt 2: 588 영문 stamp
- Reject: 한국어 사서 환경·번역 layer 불필요

### Alt 3: §28의8 항목 4개만 (간소화)
- Reject: PIPC 결정 6항목 모두 요구·간소화 = 시정 처분 위험

### Alt 4: §37의2 적용 인정 (안전·과보호)
- Reject: 도서 메타데이터 = 개인정보 X·사서 검토 전제 = "완전 자동" X·과보호 = UX 손상

## References

- 외부 858 출처 deep research §6.6 (AI 결과물 표시) + §6.1 (§28의8 6항목)
- ADR 0026 한국 SaaS 프로덕션 결정
- ADR 0028 결정론적 재생성
- 갈래 A 헤더 P3 (588 + audit) + P4 (Ghost text)
- 인공지능 기본법 §31 (시행 2026.1.22)
- PIPC 결정 2024-010-184 (시정 처분 선례)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · 갈래 A+B 병행 사이클
