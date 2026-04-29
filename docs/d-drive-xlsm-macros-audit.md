# 자관 xlsm 매크로 천국 audit + 우리 SaaS 흡수 매트릭스

> **출처**: D 드라이브 「내를건너서 숲으로 도서관」 .xlsm **4,233개** + VBA 매크로 모두 포함
> **분석일**: 2026-04-28
> **결론**: 자관 = 매크로 천국 (사서 자작·5년+ 历사). 우리 SaaS 흡수 영역 = 시트 데이터 (KORMARC 6 표준)만. VBA 매크로 binary = 자관·이씨오 IP 위험 → 동등 기능 자체 구현 (Python).

---

## 0. 자관 xlsm 매크로 통계

| 카테고리 | 수 | 비고 |
|---|---:|---|
| 자관 D 드라이브 전체 xlsm | **4,233** | VBA 매크로 모두 포함 (vbaProject.bin) |
| 책단비 5년 历사 (.xlsm) | 1,328 | 매년 ~330건 (이전 발견 정합) |
| 조기흠 사서 자작 매크로 폴더 | 133 | 「조기흠/」 폴더 직접 |
| 신착도서 간지 출력 (★) | 1 | VBA 171KB — 자관 매주 신착 |
| 상호대차 요청도서 쪽지8장 양식 (★) | 2 | VBA 148~200KB — 책두레 자동 |
| 책단비띠지 ver.1·ver.2 | 2 | VBA 34~36KB — 띠지 자동 |

→ 자관 사서 = **5년+ 매크로 자작·운영** = 우리 SaaS 자동화 직접 가치.

---

## 1. 핵심 매크로 5건 (정밀 진단)

### 1.1 신착도서 간지 출력할 때.xlsm (★)

| 항목 | 값 |
|---|---|
| 크기 | 618KB |
| VBA 매크로 (vbaProject.bin) | **171KB** (가장 큼) |
| 시트 | 3건 |
| 의미 | 자관 매주 신착도서 → 간지 (책 사이 끼우는 안내지) 자동 출력 |

**우리 SaaS 정합**: `output/labels.py` + `output/formtec_labels.py` + 신규 `output/insert_paper.py` 후보.

### 1.2 조기흠 「상호대차_요청도서_쪽지8장_양식_18·20.xlsm」 (★ 사서 자작)

| 항목 | 값 |
|---|---|
| 크기 | 396~516KB |
| VBA 매크로 | **148~200KB** (조기흠 자작) |
| 시트 | 3건 |
| 의미 | 자관 매주 책두레 요청도서 쪽지 8장 자동 출력 |

**우리 SaaS 정합**: `chaekdanbi/auto_label_generator.py` 정합 + `interlibrary/request_label_generator.py` 신규 후보.

→ **조기흠 사서 = 5년+ 매크로 자작 핵심 인력** = 우리 SaaS 베타 ICP 페르소나 1순위.

### 1.3 책단비띠지 ver.1·ver.2.xlsm

| 항목 | ver.1 | ver.2 |
|---|---|---|
| 작성일 | 2019.12.10 | 2019.12.10 |
| 띠지 양식 | 도서관 15·역 15 = 30권 | 도서관 20·역 30 = 50권 |
| VBA 매크로 | 34KB | 36KB |
| 시트 | 6건 | 6건 |

→ 자관이 자체 ver.1 → ver.2 진화 시킴 (도구 부족 인지 + 자체 해결).

---

## 2. 우리 SaaS 흡수 영역 매트릭스

### 2.1 진입 영역 (✅ 합법·기술적 가능)

| 영역 | 우리 처리 |
|---|---|
| **xlsm 시트 데이터 import** | `inventory/xlsm_importer.py` 신규 — KORMARC 6 표준 필드만 |
| **자관 컬럼 매핑 자동 추론** | xlsx 도서원부 9 컬럼 매핑 정합 (이전 발견) |
| **결과 xlsx export** (매크로 X) | `output/xlsm_export.py` — VBA 미포함 안전 형식 |
| **사서가 우리 SaaS UI에서 실행** | Streamlit 4탭 + Folder Watcher (#7) |

### 2.2 진입 X 영역 (🔴 IP·라이선스 위험)

| 영역 | 위험 |
|---|---|
| VBA 매크로 (vbaProject.bin) 추출 | 🔴 자관 사서·이씨오 IP |
| VBA 코드 자체 흡수 | 🔴 자관 사서 자작 (조기흠 등) |
| 매크로 기능 자체 reverse engineer | 🔴 IP |

→ 우리 SaaS는 VBA 매크로 X = **동등 기능 자체 구현** (Python·python-hwpx·watchdog).

### 2.3 회피 영역 (정책 ③ 자관 양식 등록)

자관 xlsm 매크로 = 자관 영업 도구. 우리 SaaS = 다른 도서관도 동등 자동화 제공.

```python
# config.yaml (자관별 매크로 회피 + 동등 기능)
forms:
  custom_xlsm_template:
    enabled: false   # 기본 비활성 (자관 IP 보호)
    library_id: "eunpyeong_naesum"
    template_path: null  # 자관 PILOT 동의 후만 활성

  # 우리 SaaS 동등 기능 (VBA 미포함)
  insert_paper_generator:
    enabled: true   # 모든 도서관
    output_format: "xlsx"  # VBA 매크로 미포함

  request_label_generator:
    enabled: true
    output_format: "hwp"  # 책두레 쪽지 8장
```

---

## 3. Excel 통합 방법 4 (신규) — 자관 xlsm 호환 (선택)

`docs/excel-integration.md`의 방법 1·2·3에 추가 후보:

### 방법 4. 자관 xlsm 직접 import (선택)

```bash
kormarc-auto xlsm fill 자관_매크로_xlsm.xlsm --output 우리_검증_결과.xlsx
```

**작동**:
1. xlsm 시트 데이터 read (VBA 매크로 미접근)
2. KORMARC 6 표준 필드 (등록번호·서명·청구기호·저자·출판사·발행년) 자동 매핑
3. 우리 SaaS 4단 검증
4. 결과 xlsx export (매크로 X·매크로 보존 옵션 별도)

**제약**:
- VBA 매크로 보존 X (자관 IP 보호)
- 자관 PILOT 동의 후만 활성

---

## 4. ADR 후보 추가

| ADR | 영역 |
|---|---|
| **ADR 0086 신규** | xlsm 시트 데이터 자동 import (`inventory/xlsm_importer.py`) — VBA 매크로 미접근·KORMARC 6 표준 필드만 |
| **ADR 0087 신규** | 자관 매크로 동등 기능 자체 구현 (Python — VBA 미사용) — `output/insert_paper.py`·`interlibrary/request_label_generator.py` |
| **ADR 0088 신규** | 자관 xlsm IP 보호 정책 (PILOT 동의 + 매크로 보존 X) |

---

## 5. 영업 메시지 (자관 매크로 천국 ICP)

> "내를건너서 숲으로 도서관(은평구·자관)이 5년+ 자작한 xlsm 매크로 4,233개를 분석했습니다.
>
> 우리 SaaS는 매크로 학습 X·VBA 작성 X로 동일 기능을 자동화합니다:
> - 신착도서 간지 자동 출력 (자관 자작 매크로 → 우리 SaaS Python)
> - 상호대차 요청도서 쪽지 8장 양식 자동 (조기흠 사서 자작 매크로 정합)
> - 책단비띠지 ver.1·ver.2 자동 출력 (자관 ver 진화 정합)
>
> 사서가 5년 자작했던 매크로 = 우리 SaaS 도입 후 클릭 1번."

---

## 6. ICP 페르소나 정밀화 — 「매크로 자작 사서」

자관 사서 4 페르소나 (이전 발견) + 매크로 자작 사서 강조:

| 페르소나 | 자관 정합 | 우리 SaaS ICP |
|---|---|---|
| 수서 사서 (박지수 수서) | pdf·hwp 중심 | 표준 사용자 |
| 종합 사서 (김기수·박세진) | jpg·hwp·pdf 균형 | 표준 사용자 |
| **★ Excel 매크로 사서** (조기흠) | xlsm 200건+ 자작 | **1순위 ICP** (사서 시간 영역 매크로 자작) |
| 영상 편집 사서 (김신학) | mp4·prproj 영상 | 우리 영역 X |

**의미**: 자관 = 사서 8명 중 **2명 이상 매크로 자작 사서** = 자관 PILOT 후 자치구·전국 매크로 자작 사서 ICP 영업 채널.

---

## 7. 종합 점수 (방법 4 전체)

| 항목 | 점수 |
|---|---:|
| Q1 결제 의향 | 85 (자관 5년+ 매크로 → 자동화 = 결제 트리거) |
| Q2 비용 | 90 (openpyxl 이미 사용·추가 비용 0) |
| Q3 자산 | 90 (재사용성 ↑·차별화 ↑) |
| Q4 락인 | 80 (자관 매크로 历사 정합) |
| Q5 컴플 | PASS (xlsm 시트만·VBA 미접근) |
| 6dim | +5 |
| **사업 5질문** | (40·85 + 25·90 + 15·90 + 10·80 + 10·100)/100 = 87 |
| 6dim 정규화 | 78 |
| **종합** | 87×0.6 + 78×0.4 = 83.4 | 🟢 ACCEPT |

---

## 8. PO 결정 영역

ADR 0086·0087·0088 PO 승인 후:
1. `inventory/xlsm_importer.py` 구현 (openpyxl 직접 사용)
2. `output/insert_paper.py`·`request_label_generator.py` 자체 구현
3. 자관 PILOT 동의서 후 활성
4. 라이선스 게이트 자동 검증 (ADR 0023 정합)

---

## 9. Sources

- D 드라이브: `D:\내를건너서 숲으로 도서관\` xlsm 4,233개
- 자관 사서: 김기수·박세진·박지수(수서·종합)·**조기흠 (★ 매크로)**·신은미·김신학·황수현
- `docs/excel-integration.md` (방법 1·2·3 정합)
- `docs/d-drive-history-tools-audit.md` (Formtec·다우오피스 정합)
- `docs/chaekdanbi-workflow-audit.md` (책단비 5년 1,328 대장)
- `docs/business-evaluation-criteria-2026-04-28.md` 통합 평가 헌법
- ADR 0023 (자관 양식 라이선스), 0086·0087·0088 (신규 — under_review)
