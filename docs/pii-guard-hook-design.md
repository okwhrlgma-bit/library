# pii-guard hook 설계 (ADR 0015·0023·0032·0036·0064·0084 통합)

> **목적**: PIPA 5대 코드 패턴 1 (Reader entity ERD 부재) 자동 보강. PO 결정 후 `.claude/hooks/pii-guard.py` 구현.
> **현재 상태**: docs only 설계 (ADR 0015 under_review).
> **헌법 정합**: `CLAUDE.md §4.1` 절대 X + `.claude/rules/business-impact-axes.md` Q5 별도 게이트.
> **시행 마감**: PIPA 2026-09-11 (매출 10% 과징금) — PO PILOT 도달 전 active 권장.

---

## 0. 정합 배경

| 영역 | 현황 |
|---|---|
| 우리 SaaS 영역 X | 회원·이용자·대출자·학생·장애인 등 PII 직접 처리 |
| 자관 알파스 위임 | 자관(내숲)이 알파스로 회원·대출 PII 처리 = 우리 영역 X |
| PIPA 시행 | 2026-09-11 매출 10% 과징금 |
| 카카오 학습 | 부분 적용 → 기존 데이터 미마이그레이션 = 151억 과징금 |

→ **우리 코드에 Reader/Borrower/Patron 등 회원 entity 절대 X**가 헌법.

---

## 1. 6 ADR 통합 매트릭스

| ADR | 영역 | 통합 hook |
|---|---|---|
| **0015** | reader_*·borrower_*·patron_* grep 자동 차단 | ✅ |
| **0023** | 자관 양식 라이선스 게이트 | ✅ |
| **0032** | 책이음 회원 PII 영역 진입 X | ✅ |
| **0036** | 학교도서관 미성년 PII 영역 진입 X (강화) | ✅ |
| **0064** | 자관 사서 PII 영역 진입 X (사서 개인 폴더 매처 deny) | ✅ |
| **0084** | 자관 PII 영역 진입 X 명문화 (NPKI·재발급·아이핀·전산 비상연락망 7종) | ✅ |

→ 6 ADR 통합 = `pii-guard.py` 단일 hook.

---

## 2. Hook 명세

### 2.1 위치

```
.claude/hooks/pii-guard.py
```

### 2.2 트리거

PreToolUse hook — `Edit`·`Write`·`NotebookEdit` 모두.

### 2.3 차단 조건 (deny 패턴)

#### A. 클래스·함수·테이블 명 (Reader entity 부재)

```python
DENY_NAMES = [
    # PII entity 직접
    r"class\s+(Reader|Borrower|Patron|Member|User|Customer|Student)\b",
    r"class\s+(독자|회원|이용자|대출자|학생|회원증)\b",
    r"def\s+(create|fetch|get|update|delete)_(reader|borrower|patron|member|user|customer|student)",

    # SQL·DB 스키마
    r"CREATE TABLE\s+(reader|borrower|patron|member|user)s?\b",
    r"Table\(['\"](reader|borrower|patron|member|user)s?",
    r"(reader|borrower|patron|member|user)_id\s*=\s*Column",
]
```

#### B. PII 5종 필드 (필드명 매처)

```python
PII_FIELDS = [
    # 식별 PII
    r"(reader|borrower|patron|member|user)_(id|name|number|code)\b",
    r"이용자(ID|이름|번호|코드)",
    r"회원(ID|이름|번호)",

    # 연락 PII
    r"(phone|mobile|email|address|연락처|전화|핸드폰|이메일|주소)",
    r"birth(_date|day|year)?\b",
    r"생년월일|생일",

    # 민감 정보 (강화)
    r"(disability|장애|등록장애인)",
    r"(rrn|jumin|주민번호|주민등록)",
    r"(card|password|아이디비번)",
]
```

#### C. 자관 PII 영역 (D 드라이브 정합)

```python
DENY_PATHS = [
    r"D:[\\/]내를건너서.*(NPKI|재발급|아이핀|비상연락망|회원증발급|개인정보)",
    r"D:[\\/]내를건너서.*[\\/](김기수|박세진|박지수|조기흠|신은미|김신학|황수현)",
    r".*[\\/]신청자명단",
    r".*[\\/]참여자.*명단",
    r".*[\\/]도서대출카드.*재발급",
]
```

### 2.4 허용 조건 (allow override)

```python
ALLOW_OVERRIDE = [
    # 컬럼 매핑 dict (저장 X)
    r"\"이용자ID\":\s*\[",  # interlibrary/exporters.py 책나래 매핑
    r"\"신청자ID\":\s*\[",  # 책바다 매핑
    r"\"patron_id\":\s*\[",  # 그대로 전달

    # 익명 mock·test
    r"# mock|# test|fake_|sample_",

    # PIPA audit·docs
    r"\.md:.*PIPA|\.md:.*개인정보",
    r"docs[\\/].*audit",
    r"docs[\\/].*pii-guard",
]
```

### 2.5 Hook 동작

```python
def main():
    """
    1. PreToolUse 입력 (tool_input·tool_name) 파싱
    2. file_path·content 추출
    3. DENY_PATHS 매처 → deny: PII 영역 차단 메시지 + exit 2
    4. content 안 DENY_NAMES 매처 → deny: Reader entity 차단 + exit 2
    5. content 안 PII_FIELDS 매처 → ALLOW_OVERRIDE 통과 시 OK·아니면 deny
    6. 모두 통과 → exit 0 (allow)
    """
```

### 2.6 출력 형식 (CLAUDE Code v2.1.x PreToolUse 표준)

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "PIPA 패턴 1 위반: Reader entity (`class Patron`) 발견. 우리 SaaS 영역 X (자관 알파스에 위임). 회원 PII 처리 절대 금지 (시행 2026-09-11 매출 10% 과징금)."
  }
}
```

---

## 3. 우회 패턴 (Common False Positive 회피)

| 케이스 | 매처 통과 | 회피 |
|---|---|---|
| `pymarc.MARCReader` | ❌ false positive | `MARCReader`는 클래스 이름이 라이브러리 — `Reader\b` 매처 X (다른 단어 prefix) |
| `easyocr.Reader` | ❌ false positive | OCR 라이브러리 — 동일 회피 |
| `interlibrary/exporters.py` 컬럼 매핑 dict | ✅ allow | ALLOW_OVERRIDE 정합 |
| docs/audit 인용 | ✅ allow | docs path 자체 |
| 자관 PII 영역 read | ❌ deny | DENY_PATHS 직접 차단 |

---

## 4. PO 결정 영역 (자율 X)

ADR 0015 PO 승인 후 active.

### 후속 작업 (PO 승인 후)

```bash
# 1. hook 구현
# .claude/hooks/pii-guard.py (이 docs 기반)

# 2. settings.json 등록
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/pii-guard.py"
          }
        ]
      }
    ]
  }
}

# 3. 테스트
# tests/integration/test_pii_guard.py
def test_reader_entity_blocked(): ...
def test_pii_field_blocked(): ...
def test_d_drive_npki_blocked(): ...
def test_pymarc_marcreader_allowed(): ...  # false positive 회피
def test_interlibrary_dict_allowed(): ...  # 컬럼 매핑 OK
```

---

## 5. 자관 D 드라이브 정합 매트릭스 (PII 영역 X 명시)

| 폴더·파일 | PII 위험 | hook 차단 |
|---|---|---|
| 종합자료실/김기수·박세진·박지수·조기흠·신은미·김신학 | 🔴 사서 PII | ✅ DENY_PATHS |
| 황수현 | 🔴 외부 협력자 | ✅ |
| NPKI/ (CrossCert·KICA·KISA·NCASign·SignKorea·TradeSign·yessign) | 🔴 공인인증서 | ✅ |
| 회원가입/ (은평구 회원증발급) | 🔴 회원 PII | ✅ |
| 도서대출카드 재발급대장.xlsx | 🔴 회원 재발급 | ✅ |
| 공유파일/공공아이핀·민간아이핀 | 🔴 본인인증 | ✅ |
| 공유파일/#전산 비상연락망 | 🔴 IT 비상 | ✅ |
| 24북큐(10) 참여자 명단 | 🔴 이용자 PII | ✅ |
| 디지털자료실 수기이용양식 | 🔴 이용자 PII | ✅ |
| 분실물관리대장 | 🔴 이용자 PII | ✅ |
| **2024_마크파일/.mrc** | 🟢 KORMARC 6 표준 | ✅ allow |
| **2024_도서원부/.xlsx** | 🟢 서지 정보만 | ✅ allow |
| **윤동주 학술·학위논문** | 🟢 서지 정보만 | ✅ allow |
| **연간 이용자 만족도 (집계)** | 🟢 집계 통계 (PII X) | ✅ allow |

---

## 6. Q5 게이트 적용 (사업 5질문)

| 항목 | 결과 |
|---|---|
| Q5 (컴플) | **PASS** (PIPA 패턴 1 자동 보강) |
| Q1 (결제) | 60 (영업 신뢰성 — "우리 SaaS는 PII 영역 X 자동 차단" 영업 메시지) |
| Q2 (비용) | 100 (hook 자체 비용 0) |
| Q3 (자산) | 90 (재사용성 ↑·차별화 ↑) |
| Q4 (락인) | 50 |
| **사업 5질문** | **(40·60 + 25·100 + 15·90 + 10·50 + 10·100)/100 = 78** |
| 6dim | +5 (보안 +2·롤백 +2·데이터 거버넌스 +1) |
| **종합** | **78 × 0.6 + 78 × 0.4 = 78** | 🟢 ACCEPT |

---

## 7. 영업 메시지 (PIPA 패턴 1 자동)

> "우리 SaaS는 PreToolUse hook (`pii-guard.py`)으로 회원 PII (Reader/Borrower/Patron entity) 진입을 코드 레벨에서 자동 차단합니다.
>
> 사서 워크플로우 검증 자료 (자관 .mrc 174 + xlsx 도서원부 + 35 윤동주 컬렉션)는 KORMARC 6 표준 필드만 처리하므로 PIPA 시행 2026-09-11 매출 10% 과징금 위험 0.
>
> 카카오 오픈채팅 151억 과징금 사례 회피 — 우리 SaaS는 처음부터 PII 영역 X로 설계."

---

## 8. ADR 0015 PO 승인 트리거

PO 승인 후:
1. `pii-guard.py` 구현 (이 docs 기반, 약 200~300줄)
2. settings.json 등록 (PreToolUse matcher)
3. 통합 테스트 6+ 케이스
4. learnings.md `pii-guard active` 갱신
5. CLAUDE.md §4.1 절대 X에 "Reader entity ERD 절대 X (pii-guard.py 자동 차단)" 추가

---

## 9. Sources

- PO 사업 마스터 (2026-04-28) — PIPA 5대 코드 패턴
- `자료/business_framework_2026_04_28.md`
- `learnings.md` PIPA audit
- `docs/legal-references.md §8.1` PIPA 2026.9.11
- `docs/d-drive-bookforest-audit.md` 자관 PII 영역
- `docs/d-drive-final-completion-audit.md` NPKI 7 인증기관
- ADR 0015·0023·0032·0036·0064·0084 (6 통합)
- `.claude/rules/business-impact-axes.md` Q5 별도 게이트
- 카카오 오픈채팅 151억 과징금 학습
- Claude Code v2.1.119 PreToolUse hook spec
