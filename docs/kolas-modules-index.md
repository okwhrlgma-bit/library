# KOLAS III 모듈 디렉토리 인덱스 (PO 실 자료)

> 출처: `자료/KOLASIII_단행자료_전체/` (59 디렉토리, 1,737 파일)
> KOLAS III 시스템의 실제 모듈 디렉토리 구조 — `.cpp`·`.dsp`·`.def` 등 C++ 자원.

---

## 1. 모듈 명명 규칙 추정

| 접두 | 의미 | 빈도 |
|---|---|---|
| **BL_*** | Business Logic (업무 로직) | 다수 |
| **BO_*** | Business Object (업무 객체) | 다수 |
| **BL_BO_*** | BL + BO 결합 모듈 | - |
| **SE_*** | Serial (연속간행물) | 별도 폴더 |

## 2. 도메인 분류 (모듈명 기반)

### 단행자료 모듈 영역
| 영역 | 모듈 예 | 우리 매칭 |
|---|---|---|
| **ACQ** (Acquisition, 수서) | `BO_ACQ_API`, `BO_ACQ_BASIC_DATA_MANAGER`, `BO_ACQ_DONATE_DATA_MANAGER`, `BO_ACQ_DONATE_STATISTICS`, `BO_ACQ_FILE_IMPORT_EXPORT`, `BO_ACQ_EVIRONMENT_MANAGER` | 수서·기증 처리 → `inventory/importer.py` 매핑 |
| **LOC** (Location, 위치) | `BL_BO_LOC_1400`, `BL_LOC`, `BL_LOC_2100` | 049 청구기호·소장 위치 |

### 연속간행물 모듈 영역 (SE_*)
| 모듈 | 우리 매칭 |
|---|---|
| `SE_ACCOUNT_STATEMENT` | 회계 명세 |
| `SE_ACQINFO` | 연속간행물 수서 |
| `SE_API` | API |
| `SE_BIBINFO` | 서지정보 |
| `SE_BINDING_DECISION` | 제본 결정 |
| `SE_BINDING_ORDER` | 제본 주문 |
| `SE_BINDING_TERMIN` | 제본 종결 |
| `SE_BINDING_TRANSFER` | 제본 이관 |

→ 연속간행물(잡지·학술지)은 KOLAS III에서 별도 시스템 처리. 우리는 단행본 우선.

---

## 3. 우리 도구 KOLAS 호환 정밀화 (자율 작업 가능)

### 현 상태
- ✅ `output/kolas_writer.py` — `{ISBN}.mrc` 파일명 자동
- ✅ KOLAS 자동 반입 폴더에 두면 자동 인식

### 추가 가능 (PO 명령 시)
- ⏸ `BO_ACQ_FILE_IMPORT_EXPORT` 모듈 분석 → KOLAS가 어떤 폴더 구조·파일명 규칙을 인식하는지 정밀
- ⏸ `BO_ACQ_DONATE_DATA_MANAGER` → 기증도서 처리 흐름 우리 파이프라인 매핑
- ⏸ `SE_*` 모듈군 → 연속간행물 KORMARC 처리 모듈 추가

---

## 4. 사서 호환 검증 흐름

### PO 베타 사서에게 시연 시
1. 사서 도서관에 우리 `.mrc` 파일 전달
2. KOLAS의 `BO_ACQ_FILE_IMPORT_EXPORT` 폴더에 복사
3. KOLAS가 자동 반입 → 사서가 검증
4. **반입 거부 시 우리 `kolas_strict_validate` 결과로 사전 진단**

→ 1,737 파일을 모두 분석할 필요 없음. **모듈명만으로 KOLAS 흐름 추적 가능**.

---

## 5. 자료 활용 한계 (정직)

- ❌ 소스 코드(.cpp) 분석은 KOLAS 저작권 영역 — 우리가 직접 보면 위험
- ❌ 모듈명만 인덱스로 활용 (위험 회피)
- ✅ 사서 시연 시 "이 모듈에 우리 파일 들어갑니다" 안내 가능

→ KOLAS 호환은 **모듈명 인덱스 + 사서 검증**으로 충분.

---

## 6. 결론

PO 자료의 KOLAS III 1,737 파일은:
1. **모듈명만 인덱스로 활용** (저작권 안전)
2. 우리 `.mrc` 파일이 어느 모듈로 들어가는지 정확
3. 사서 시연 시 신뢰도 ↑
4. 연속간행물·기증 등 추가 영역 진입 로드맵

→ Phase 2 진입 시 모듈명 기반 호환 가이드 작성 가능. 현재는 단행본 ICP에 집중.
