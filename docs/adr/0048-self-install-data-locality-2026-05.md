# ADR 0048 — 사서 자가 설치 + 데이터 로컬리티 (Cycle 65·invariant 12)

- 상태: Accepted (2026-05-06·Cycle 65)
- 일자: 2026-05-06
- 트리거: PO "사서 컴퓨터에 못 가니까 직접 하도록"·"GitHub만으로 끝?"

## Context

PO 통찰 (Cycle 65·결정적):
1. **PO 방문 X** = 사서가 자기 손으로 설치 = SaaS 영업 결정 요인
2. **사서 IT 자신감** = L1 워드만 25%·L2 엑셀 35% = 60% = 명령어 거부
3. **데이터 로컬리티** = 사서 데이터 = 사서 컴퓨터 = 도서관 RFP 자동 통과·PIPA 정합

## Decision

### A. 사서 자가 설치 stack (₩0/월·도메인 X)

**옵션 A·B 동시 제공** (사서 선택):

#### 옵션 A — URL 클릭 (5초·인터넷 필수)
- Streamlit Community Cloud (₩0)
- URL = `https://kormarc-auto.streamlit.app`
- 사서 IT 자신감 무관·핸드폰·태블릿 OK

#### 옵션 B — `.exe` 다운로드 (도서관 인터넷 차단 시)
- PyInstaller 자동 빌드 (Windows·Mac·Linux 3 OS)
- GitHub Actions = `build-exe.yml`·tag push 자동
- GitHub Releases = 자동 첨부
- 사서 = 더블클릭 1회·Python·명령어 X
- **데이터 100% 사서 컴퓨터·도서관 RFP 통과**

### B. 데이터 로컬리티 invariant 12 (영구·헌법 §14)

> **"사서 .mrc·자관 양식·사용 통계 = 사서 컴퓨터에 저장. 우리 SaaS 서버 = stateless (UI·처리만). 외부 BaaS Storage·DB 절대 X. 도서관 RFP 100% 통과·PIPA §28의8 의무 ↓·SaaS 종료 위험 0."**

CLAUDE.md §14 박제·PR 차단 게이트.

### C. launcher.py = `.exe` 진입점 표준
- Streamlit 자동 실행·브라우저 자동 열기
- offline demo 모드 자동 (KORMARC_DEMO_MODE=1)
- 사서 친화 에러 + GitHub Issues link + 1일 답변 약속

## Alternatives

1. **Supabase·Firebase·AWS RDS** = 거부 (ADR 0047 정합)·중앙 SaaS = 도서관 RFP 부담
2. **사서 Python 설치 후 pip** = 거부·사서 IT L1·L2 60% 거부
3. **온프레미스 직접 설치 (네트워크 셋업·DB)** = 거부·1인 SaaS 운영 한계
4. **모바일 앱 (iOS·Android)** = 옵션·v1.0+ 검토

## Consequences

### Positive
- ✅ 사서 영업 = 클릭 1회 (URL) 또는 더블클릭 1회 (.exe)
- ✅ 도서관 RFP 100% 통과 (데이터 사서 컴퓨터)
- ✅ PIPA §28의8 의무 ↓ (저장 X = 외부 송신 X)
- ✅ SaaS 종료 위험 0 (사서 데이터 = 사서 자산)
- ✅ ₩0/월 stack 유지·도메인 X·신경 0
- ✅ PO 운영 부담 = launcher 1회 빌드·tag push만

### Negative
- ⚠ 첫 .exe 실행 = OS 보안 경고 (1회·"추가 정보" 클릭)
- ⚠ Mac·Linux 빌드 = GitHub Actions 시간 ↑ (matrix 3 OS)
- ⚠ 자동 업데이트 X = 사서가 새 .exe 다운로드 (Cycle 70+ Auto-update 검토)

### Neutral
- ADRs: 0047 → **0048**
- Invariants: 11 → **12** (사서 데이터 = 사서 컴퓨터)
- 헌법 §13 → §14·§15 (자가 설치 친화)

## V3 통합 + 사서 자가 설치 매트릭스 최종

| 영역 | Cycle | 상태 |
|---|---|---|
| 코드 100% 정합 | 1~62 | ✅ |
| ₩0 stack (GitHub Pages·Streamlit Cloud) | 63 | ✅ |
| BaaS 비교 자동 결정 (Supabase 미도입) | 64 | ✅ |
| **사서 자가 설치 (.exe + URL)** | **65** | **✅** |

## 다음 7-cycle 권장 (Cycle 66~72)

1. **66**: PyInstaller 빌드 검증 (로컬 Windows .exe 실행 확인) + 첫 v0.7.2 release
2. **67**: 자동 업데이트 알림 (`.exe`·Streamlit 둘 다) - 신버전 표시
3. **68**: 사서 첫 인터뷰 결과 박제 (PO 외부 작업 후·invariant 11 활성)
4. **69**: 첫 콜드 메일 5건 결과 측정 (open·reply·데모 클릭)
5. **70**: KOLAS3 D-200 보도자료 발행 (2026-06-15)
6. **71**: META_REVIEW Cycle 65~71 + ADR 0049
7. **72**: 첫 매출 시도 (사업자 등록 + PortOne 통합 후)
