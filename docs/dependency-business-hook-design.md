# dependency-business hook 설계 (ADR 0085 후보)

> **목적**: 새 의존성 추가 시 사업가치 임계 미달 자동 차단. PO 사업 마스터 §1.7 정합.
> **현재 상태**: docs only 설계.
> **헌법 정합**: `autonomy-gates.md` "5대 멈춤 패턴 사전 차단 §의존성 네트워크 실패 → 새 의존성 금지" + 사업 5질문 Q2 (비용) + Q3 (자산).

---

## 0. 정합 배경

| 영역 | 현황 |
|---|---|
| 효율 가드 §5 의존성 빈도 위반 회피 | 현재: autonomy-gates 수동 감시 |
| PO 사업 마스터 §1.7 | "새 의존성당 인지 부하 증가 = 비용" |
| 카카오 학습 | 부분 적용 의존성 → 마이그레이션 비용 폭증 |

→ 의존성 추가 시 자동 검증 = 사업·기술 6차원·유지보수 부담 통합 게이트.

---

## 1. Hook 명세

### 1.1 위치

```
.claude/hooks/dependency-business.py
```

### 1.2 트리거

PreToolUse hook — `Edit·Write` 시 `pyproject.toml`·`requirements.txt` 변경 감지.

### 1.3 검증 단계 (4 게이트)

```
Gate 1: 의존성 추가 감지
  - pyproject.toml `[project.dependencies]` 섹션 변경
  - requirements.txt 새 줄 추가
  - +pkg==version 패턴

Gate 2: 사업가치 검증 (Q1·Q2·Q3·Q4)
  - 의존성당 commit message 또는 ADR 사업 점수 명시
  - 종합 ≥ 75 (Beta 단계)

Gate 3: 6차원 검증
  - OS 호환성 (Windows·macOS·Linux 모두 동작)
  - 의존성 자체 (활발 유지보수·메이저 버전 안정)
  - 보안 (CVE 이력·known issues)
  - 라이선스 (MIT/Apache/BSD OK·GPL/AGPL 검토)

Gate 4: 메타 검증
  - 패키지 다운로드 수 (PyPI/npm)
  - 마지막 업데이트 일자 (1년 이내)
  - GitHub Stars (≥100 권장)
```

### 1.4 강제 형식 (의존성 추가 시 ADR 또는 commit)

```markdown
## 의존성 추가 평가

### 패키지: <name>==<version>
- 출처: PyPI / npm
- 라이선스: MIT|Apache 2.0|BSD-3
- 다운로드: <number>/월
- 마지막 업데이트: <YYYY-MM-DD>
- GitHub stars: <number>
- CVE 이력: 없음 / <CVE-ID>

### 사업 5질문
- Q1 결제 의향: <0~100> (사용자 가치)
- Q2 비용: <0~100> (의존성 자체 비용 + 유지보수 부담)
- Q3 자산: <0~100> (재사용성·차별화)
- Q4 락인: <0~100>
- Q5 컴플: PASS|FAIL

### 6차원
- OS 호환성: <-1~+1>
- 의존성 자체: <-1~+1>
- 보안: <-1~+2>
- 라이선스: <PASS|FAIL>
- 롤백: <-1~+2>
- 관측: <-1~+2>

### 종합: <0~100>
- ≥75: ACCEPT (자율 commit)
- 60~74: PO 결정
- <60: 폐기

### 대안 검토
- 대안 1: <alternative_pkg> — <차이점·왜 X>
- 대안 2: <inline 구현 가능 여부>
- 대안 3: <표준 라이브러리>
```

---

## 2. 차단 케이스

| 케이스 | 결과 |
|---|---|
| 사업 5질문 점수 누락 | 🔴 deny |
| Q5 = FAIL (라이선스 GPL/AGPL 등 컴플 위반) | 🔴 즉시 deny |
| 종합 < 60 | 🔴 deny |
| 60 ≤ 종합 < 75 | 🟡 warn (PO 결정) |
| 마지막 업데이트 > 1년 | 🟡 warn (deprecated 위험) |
| GitHub stars < 50 | 🟡 warn (검증 부족) |
| CVE 이력 있음 | 🟡 warn (PO 결정) |
| 종합 ≥ 75 + 모든 메타 통과 | 🟢 allow |

---

## 3. 84 ADR 적용 예시

### 후보 의존성 (이번 야간 자율 ADR 누적)

| 의존성 | ADR | 종합 | 결과 |
|---|---|---:|---|
| `python-hwpx>=0.5` | 0021 (상호대차 띠지) | 89 | 🟢 allow |
| `watchdog>=4.0` | 0016 (Folder Watcher) | 86 | 🟢 |
| `pystray>=0.19` + `pillow>=10.0` | 0017 (System Tray) | 84 | 🟢 |
| `python-hanja` | 0048 (로마자 표기) | 75 | 🟢 |
| `olefile>=0.46` | (HWP 5.0 OLE2 처리) | 65 | 🟡 warn (PO 결정) |
| `openpyxl>=3.1` (이미 사용) | 일반 | 90 | 🟢 (skip — 기존) |

### 차단 케이스 (예시)

| 가상 의존성 | 결과 |
|---|---|
| `random_streamlit_addon` (stars 5·1년+ 미업데이트) | 🟡 warn |
| `sqlalchemy_with_GPL_license` | 🔴 Q5 FAIL (라이선스) |
| `unmaintained_marc_lib` (마지막 2019) | 🔴 deny |

---

## 4. 자동 메타 조회 (PyPI API)

```python
def fetch_pypi_meta(pkg: str) -> dict:
    """PyPI JSON API로 메타 자동 조회.
    
    - https://pypi.org/pypi/{pkg}/json
    - timeout=10
    - cache 30일 (이미 사용 의존성 활용)
    """
    return {
        "downloads_per_month": int,
        "last_release_date": str,
        "license": str,
        "github_stars": int,  # 별도 GitHub API
        "cve_count": int,     # NVD API
    }
```

---

## 5. 출력 형식 (Claude Code v2.1.x PreToolUse 표준)

### 5.1 deny

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "의존성 'random_pkg==1.0' 종합 점수 45 (임계값 60 미달). 대안: 표준 라이브러리·인라인 구현 검토. 참조: docs/dependency-business-hook-design.md"
  }
}
```

### 5.2 warn (60 ≤ 종합 < 75 OR 메타 경고)

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "ask",
    "permissionDecisionReason": "의존성 'olefile>=0.46' 마지막 업데이트 2024-01 (1년 초과). PO 결정 필요."
  }
}
```

---

## 6. ADR 0085 (신규 후보) PO 승인 트리거

PO 승인 후:
1. `dependency-business.py` 구현 (이 docs 기반, 약 250줄)
2. settings.json 등록 (Edit·Write matcher with file_path 매처)
3. 통합 테스트 6+ 케이스
4. CLAUDE.md §4 추가: "새 의존성 추가 시 사업·6차원·메타 평가 강제"
5. learnings.md `dependency-business active` 갱신

---

## 7. 효율 가드 §5 의존성 빈도 자동화

현재 (수동):
> "새 의존성 금지 + 오프라인 모드 우선" (autonomy-gates.md §5대 멈춤)

업그레이드 후 (자동):
- Hook이 사업가치·6차원·메타 자동 검증
- 임계값 미달 차단 → "정말 필요한 의존성만 추가" 정합

---

## 8. 종합 평가 (ADR 0085 자체)

| 항목 | 점수 |
|---|---:|
| Q1 결제 | 40 (간접 — 영업 신뢰성·"우리 SaaS는 의존성 신중") |
| Q2 비용 | 100 (hook 자체 비용 0) |
| Q3 자산 | 95 (재사용성 ↑·차별화 ↑·5대 멈춤 자동 차단) |
| Q4 락인 | 60 (의존성 평가 史료 누적) |
| Q5 컴플 | PASS (라이선스 자동 검증) |
| 6dim | +6 |
| **사업 5질문** | (40·40 + 25·100 + 15·95 + 10·60 + 10·100)/100 = 70 |
| 6dim 정규화 | 83 |
| **종합** | 70×0.6 + 83×0.4 = 75.2 | 🟢 ACCEPT |

---

## 9. 영업 메시지

> "우리 SaaS는 모든 새 의존성 추가에서 사업가치 + 라이선스 + 메타 (다운로드·마지막 업데이트·CVE) 자동 검증 hook을 운영합니다.
>
> 종합 점수 75 미달 또는 라이선스 컴플 위반 의존성은 자동 차단 — 5대 멈춤 패턴 §5 (의존성 네트워크 실패) 사전 차단."

---

## 10. Sources

- PO 사업 마스터 §1.7 (의존성 비용 = 인지 부하 + 유지보수 부담)
- `docs/business-evaluation-criteria-2026-04-28.md`
- `.claude/rules/autonomy-gates.md` 5대 멈춤 §5 의존성 네트워크
- `docs/pii-guard-hook-design.md` (Q5 자동 검증 연동)
- `docs/business-impact-check-hook-design.md` (사업 점수 검증 연동)
- ADR 0085 (신규 후보 — under_review)
- PyPI JSON API + NVD API + GitHub API (메타 조회)
- Claude Code v2.1.119 PreToolUse hook spec
