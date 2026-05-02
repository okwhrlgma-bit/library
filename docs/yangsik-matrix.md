# 양식 매트릭스 — 전국 표준 vs 자치구 한정 vs 자관 자체 + 우리 SaaS 정책

> **PO 명령** (2026-04-28):
> 1. "여러 양식들의 경우 ○○도서관이나 은평구에서만 사용하는 양식일 수 있음 추가 조사 및 확인 필요"
> 2. "추가적인 표준 양식을 찾지 못했을 경우는 제공받은 양식을 적용. 여러 양식이 존재할 경우 기본 양식으로 찾은 양식들 제공 하지만 설정 가능하도록 제공"
> **분석일**: 2026-04-28
> **출처**: WebFetch 6건 + 자료 폴더 표준 매뉴얼 cross-check + D 드라이브 자관 양식

---

## 0. 핵심 결론 — **「책단비」는 은평구 한정 명칭** (이전 audit 정정)

| 시스템·서비스 | 적용 범위 | 표준 운영 |
|---|---|---|
| **책단비** | 🟡 **은평구 11개 공공도서관 + 무인 대출기 (구파발·녹번·DMC·응암역 등)** | 은평구립도서관 자체 (한국 최초 RFID·유비쿼터스 도서관) |
| **책두레** | ✅ **전국 표준** | KOLAS III 자체 상호대차 모듈 (NLK 운영) |
| **책이음** | ✅ **전국 표준** | KOLAS III 기반 통합 회원증 (전국 공공도서관) |
| **책나래** | ✅ **전국 표준** (2024년 1,166개관 참여) | 국립장애인도서관 (NLD) 우편 배송 (장애인·국가유공상이자·장기요양대상자) |
| **책바다** | ✅ **전국 표준** | 국가상호대차 (전국 일반 이용자) |
| **책밴드** | ❌ **알파스 (이씨오) 자체 모듈** (이씨오 SaaS 사용 도서관 한정) | 이씨오 자체 framework |
| **리브로피아** | 🟡 **은평구·일부 자치구 모바일 앱** | 은평구공공도서관 모바일 |

---

## 1. 양식별 적용 범위 매트릭스

| # | 양식 | 적용 범위 | 우리 정책 |
|---|---|---|---|
| 1 | 책단비 4 양식 hwp/hwpx (만료·반납·제공·지하철) | 🟡 **은평구 한정** (자관 작성, `<[내숲]><[은평]>` 토큰) | **자관 양식을 기본 제공 + UI 설정으로 자치구·자관별 토큰 변경 가능** |
| 2 | 책나래 가입신청서 + 우편 발송 양식 | ✅ **전국 표준** (NLD 공식 다운) | **NLD 표준 양식 기본** |
| 3 | 책바다 운영매뉴얼 + 신청서 (52p, 자관 보유) | ✅ **전국 표준** — 국가상호대차서비스, 5,200원/책, 1인 3책, 14일, 8단계 워크플로우 | **국가상호대차 표준 기본** + 자관 통계 4년 데이터 |
| 4 | 책이음 회원가입 절차 매뉴얼 | ✅ **전국 표준** (KOLAS III 기반) | **NLK 표준 기본** |
| 5 | 책두레 F12 엑셀 출력 양식 | ✅ **전국 표준** (KOLAS III 모듈) | **KOLAS 표준 기본** |
| 6 | 알파스 책밴드 양식 | 🔴 **알파스 사용 도서관 한정** (이씨오 SaaS) | **이씨오 매뉴얼 기반 import만** |
| 7 | 종합자료실 오픈 마감메뉴얼 | 🔴 **자관 자체 작성** (15MB hwp) | **참조 자료, 우리 SaaS 양식 X** |
| 8 | 회원증 발급업무 매뉴얼 (은평구·2018·2023 pptx) | 🟡 **은평구 한정** | **각 자치구별 별도 매뉴얼 존재 — 우리 영역 X** |
| 9 | 「내숲 종합 자료관리대장」 28 시트 | 🔴 **자관 자체 작성** | **참조 자료** |
| 10 | KORMARC 통합서지용 표준 (KS X 6006-0:2023) | ✅ **전국·국가 표준** | **KORMARC 표준 100% 정합** |
| 11 | KDC 6판 강목표 (한국도서관협회) | ✅ **전국 표준** | **KDC 6판 기본** |
| 12 | 이재철 5판 도서기호법 | ✅ **전국 표준** | **이재철 5판 기본** |
| 13 | KOLAS III 매뉴얼 + 책두레 가이드 | ✅ **전국 표준** (NLK 공식) | **공식 매뉴얼 기반** |
| 14 | 알파스 공통/단행 매뉴얼 V 1.0 | ✅ **알파스 사용 도서관 표준** | **이씨오 표준 기반** |

---

## 2. 우리 SaaS 정책 — PO 3 명령 통합

### 정책 ① — 표준 양식 미발견 시 자관 양식 적용

```
양식 우선순위:
1. NLK·NLD·문체부·KOLAS·KS X 표준 양식이 존재하면 → 기본 적용
2. 표준 양식이 없으면 → 자관(내숲) 양식을 기본으로 적용
3. 사용자가 별도 양식을 가지면 → 설정에서 추가·교체 가능
```

### 정책 ② — 다중 양식 발견 시 기본=표준 + 자관 양식 설정 가능

### 정책 ③ — **모든 양식은 도서관별 자체 변형 가능 (일반화)** (PO 2026-04-28 추가)

PO 명령: "저런 여러 양식들은 위와 동일하게 타 도서관에서 다른 방식으로 제작 가능"

→ **책단비 (은평구 한정)** 의 자관 한정 정책을 **모든 양식에 일괄 적용**:

| 표준 양식 | 자치구·자관별 변형 가능성 |
|---|---|
| 책나래 (NLD 표준) | 🟡 자관별 띠지·발송 양식 자체 변형 가능 (NLD 양식 위에 자관 토큰 추가) |
| 책바다 (NLK 표준 5,200원) | 🟡 자치구별 결제 정책 (지역별 비용 지원) — 자치구 토큰 변형 |
| 책이음 (KOLAS III 기반) | 🟡 자관별 회원증 발급 양식·교육 자료 자체 작성 (자관 회원증 hwp 발견) |
| 책두레 (KOLAS III 모듈) | 🟡 자관별 F12 엑셀 출력 후 자체 후처리 (책단비 = 은평구 후처리) |
| KOLAS III 자료 등록 | 🟡 자관별 등록번호 prefix 변형 (자관 = `EQ` prefix 발견) |
| KERIS DLS (학교도서관) | 🟡 시·도교육청별 자체 양식·통계 변형 가능 |
| 알파스 (이씨오) | 🟡 자관별 옵션 설정 (책밴드 자동 요청 ON/OFF 등) |

→ 정책 ③: **각 양식마다** PO 정책 ① + ② 적용. 도서관별 자체 양식 등록 가능 + 표준 fallback 보장.

### 정책 ③ 적용 — 일반화된 4단 fallback (전체 양식)

```python
# kormarc-auto/forms/resolver.py — 모든 양식에 일괄 적용
def resolve_form(
    form_type: str,           # "chaeknarae", "chaekbada", "chaekeum", "chaekdure",
                               # "chaekdanbi", "kolas_register", "keris_dls", "alphas",
                               # "kerm_F12", "kolisnet" 등 모든 양식
    user_config: dict,
    library_id: str,           # 자관 식별자 (eunpyeong_naesum 등)
    region_id: str,            # 자치구·시도 식별자
) -> tuple[Path, str]:
    """4단 fallback (모든 양식 일괄):
    1. 사용자 custom 업로드 → 사용
    2. 자관 등록 양식 (data/forms/<library_id>/<form>) → 사용 (자관 PILOT 동의 후)
    3. 자치구·시도 표준 (data/forms/<region_id>/<form>) → 사용 (지역 표준 있으면)
    4. 전국 표준 (data/forms/standard/<form>) → 사용 (NLK·NLD·KS X·KERIS)
    """
```

### config.yaml 정책 ③ 적용 (전체 양식)

```yaml
forms:
  # 기본: 모든 양식 자관 변형 등록 활성
  custom_forms_enabled: true
  
  # 자관 식별
  library_id: "eunpyeong_naesum"
  region_id: "eunpyeong_seoul"
  
  # 양식별 자관 등록 (선택)
  custom_templates:
    chaeknarae:
      template_path: "data/forms/eunpyeong_naesum/chaeknarae_label.hwpx"
      tokens: {library: "[내숲]", region: "[은평]"}
    chaekbada:
      template_path: "data/forms/eunpyeong_naesum/chaekbada_form.xlsx"
    chaekeum:
      template_path: null  # 표준 사용
    chaekdure:
      template_path: "data/forms/eunpyeong_naesum/chaekdure_F12_post.xlsm"
    chaekdanbi:                            # 자관 자체 (은평구 한정)
      template_path: "data/forms/eunpyeong_naesum/chaekdanbi_4set/"
    kolas_register:
      template_path: null  # 표준 사용
      registration_prefix: "EQ"            # 자관 등록번호 prefix
    keris_dls:
      template_path: null  # Phase 2~3
    alphas:
      template_path: null  # 표준 사용
```

```yaml
# config.yaml (사용자별)
forms:
  chaekdanbi:                      # 책단비 (은평구 한정 — 자관 양식 사용)
    enabled: false                 # 기본 비활성 (다른 자치구 사서는 OFF)
    library_name_token: "[내숲]"   # 자관명 토큰 (다른 자관 사용 시 변경)
    region_token: "[은평]"          # 자치구 토큰 (다른 자치구 변경)
    target_libraries:               # 11개 은평구 공공도서관 (기본)
      - "은평구립도서관"
      - "구립증산도서관"
      - "구립응암도서관"
      - "구립은평뉴타운도서관"
      - "구립구산동도서관마을"
      - "구립상림도서관"
      - "PILOT 자관도서관"
      - "구립은뜨락도서관"
      - "신사어린이도서관"
      - "녹번만화도서관"
      - "대조꿈나무어린이도서관"
    target_subway_stations:         # 무인 대출기 위치 (기본)
      - "구파발역"
      - "녹번역"
      - "디지털미디어시티역"
      - "구립상림도서관 버스정류장"
      - "응암역"
    template_paths:                 # 4 양식 hwp/hwpx
      expire: "data/forms/chaekdanbi/만료.hwpx"
      return: "data/forms/chaekdanbi/반납.hwpx"
      provide: "data/forms/chaekdanbi/제공.hwpx"
      subway: "data/forms/chaekdanbi/지하철.hwp"
    rows_per_label:
      library: 20
      station: 30

  chaeknarae:                      # 책나래 (전국 표준 — NLD 공식)
    enabled: true
    standard_form_url: "https://cn.nld.go.kr/chaeknarae/introduce/serviceGuide.do"
    csv_columns:                    # NLD 표준 컬럼 (전국 1,166개관 공통)
      - "이용자ID"
      - "도서명"
      - "ISBN"
      - "발송주소"

  chaekbada:                       # 책바다 (전국 표준 — NLK)
    enabled: true
    standard_manual: "자료/2020+책바다+운영매뉴얼.pdf"

  chaekeum:                        # 책이음 (전국 표준 — KOLAS III)
    enabled: true
    standard_manual: "자료/(재택학습형)KOLASⅢ기반의책이음서비스운영-2기)+과정.pdf"
```

### UI 설계 (Streamlit Sidebar)

```
📚 양식 설정
├─ 🟢 표준 양식 (전국 공통)
│  ├─ ☑ 책나래 (NLD)
│  ├─ ☑ 책바다 (NLK)
│  ├─ ☑ 책이음 (KOLAS III)
│  └─ ☑ 책두레 F12 엑셀 (KOLAS III)
├─ 🟡 지역·자관 양식
│  ├─ ☐ 책단비 (은평구) [자관 양식 사용]
│  │   ├─ 자관명 토큰: [내숲    ]  ← 편집 가능
│  │   ├─ 자치구 토큰: [은평    ]
│  │   └─ 참여 도서관 11개 (편집 가능)
│  └─ ➕ 자관 양식 추가
└─ 📁 양식 라이선스
   └─ 자관 양식은 자관 동의 하에 사용
```

---

## 3. 자관 한정 양식 처리 원칙 (PIPA + IP)

| 양식 | 라이선스 | 우리 SaaS 처리 |
|---|---|---|
| 책단비 4 hwp (자관 작성) | 자관 IP | **자관 PILOT 동의 후 사용** — 다른 자치구는 자체 양식 업로드 |
| 알파스 매뉴얼 (이씨오) | 이씨오 IP | **공개 매뉴얼 기반 import만** (스키마 reverse X) |
| 「내숲 종합 자료관리대장」 28 시트 | 자관 IP | **참조만** — 우리 SaaS 양식 X |
| 「종합자료실 오픈 마감메뉴얼」 | 자관 IP | **참조만** |

### 라이선스 게이트 (자관 PILOT 시 협의)

```
자관 양식 사용 동의서 (PILOT 1관 기본):
1. 우리 SaaS는 자관 양식을 자관 사서만 사용하도록 격리 (다른 도서관 노출 X)
2. 자관 양식 templates는 우리 git repo에 commit X (.gitignore)
3. 자관이 양식 회수 요청 시 즉시 삭제
4. 자관 토큰 ([내숲]·[은평]) 외부 노출 X
```

---

## 4. 양식 우선순위 알고리즘 (구현)

```python
# kormarc-auto/forms/resolver.py
from typing import Literal

def resolve_form(
    form_type: Literal["chaekdanbi", "chaeknarae", "chaekbada", ...],
    user_config: dict,
    library_id: str,
) -> tuple[Path, str]:  # (template_path, source: "standard" | "user_custom" | "library_default")
    """
    양식 우선순위:
    1. 사용자가 custom 양식 업로드 → 그것 사용
    2. 표준 양식 존재 (NLK·NLD·KOLAS·KS) → 표준 사용
    3. 표준 X + 자관 기본 양식 (data/forms/<library_id>/<form>.hwpx) → 자관 양식
    4. 모두 X → 빈 양식 생성 + 사용자 설정 안내
    """
    # 1. 사용자 custom
    custom_path = user_config.get(f"forms.{form_type}.custom_template_path")
    if custom_path and Path(custom_path).exists():
        return Path(custom_path), "user_custom"
    
    # 2. 표준 (전국 공통)
    STANDARD_FORMS = {
        "chaeknarae": "data/forms/standard/chaeknarae_template.csv",
        "chaekbada": "data/forms/standard/chaekbada_template.csv",
        "chaekeum": "data/forms/standard/chaekeum_template.csv",
        "kolas_f12": "data/forms/standard/kolas_f12_xlsx_template.xlsx",
    }
    if form_type in STANDARD_FORMS:
        return Path(STANDARD_FORMS[form_type]), "standard"
    
    # 3. 자관 기본 양식 (지역 한정)
    REGIONAL_FORMS = {
        "chaekdanbi": {
            "eunpyeong": [
                "data/forms/eunpyeong/chaekdanbi/만료.hwpx",
                "data/forms/eunpyeong/chaekdanbi/반납.hwpx",
                "data/forms/eunpyeong/chaekdanbi/제공.hwpx",
                "data/forms/eunpyeong/chaekdanbi/지하철.hwp",
            ],
        }
    }
    region = user_config.get(f"forms.{form_type}.region", "default")
    if form_type in REGIONAL_FORMS and region in REGIONAL_FORMS[form_type]:
        return Path(REGIONAL_FORMS[form_type][region][0]), "library_default"
    
    # 4. 빈 양식 + 사용자 안내
    return Path("data/forms/empty_template.txt"), "user_setup_required"
```

---

## 5. chaekdanbi-workflow-audit.md 정정 사항

이전 audit (2026-04-28 작성)의 **2 정정**:

| 이전 | 정정 |
|---|---|
| "책단비 = 서울특별시 25개 자치구 + 서울교통공사 지하철 도서관 통합 상호대차 서비스" | **"책단비 = 은평구립도서관 11개 공공도서관 + 무인 대출기 5곳 자체 서비스"** |
| "운영 주체: 서울특별시 + 자치구립 도서관 + 서울교통공사" | **"운영 주체: 은평구공공도서관 (한국 최초 RFID·유비쿼터스 도서관)"** |
| "25구 + 지하철 = 책단비 영역 영업 채널 26개" | **"은평구 11개관 + 무인 대출기 5곳 = 자관 PILOT 후 다른 자치구 별도 영업"** |

---

## 6. 영업 메시지 정정 (자관 한정 → 일반화)

### 이전 (오류)

> "○○도서관(은평구)이 5년 동안 매일 작성한 1,328 책단비 대장을 분석했습니다. 책단비 hwp 4 양식이 자동 생성됩니다."

### 정정 (정확)

> "○○도서관(은평구공공도서관)이 5년 동안 매일 작성한 1,328 상호대차 대장을 분석했습니다. KOLAS 책두레 F12 엑셀 1번 다운으로, 자관 상호대차 양식 (만료·반납·제공·지하철)이 자동 생성됩니다.
> - **은평구**는 자관 「책단비」 양식 적용 (한국 최초 RFID·유비쿼터스 도서관 기반)
> - **다른 자치구**는 각 자관 양식 또는 KOLAS 책두레 표준 양식 적용 가능
> - **다른 도서관**은 자관 양식 업로드 또는 표준 양식 자동 사용"

---

## 7. ADR 후보 정정

| ADR | 정정 |
|---|---|
| **ADR 0021** (이전) — 책단비 자동 띠지 생성 | **정정**: 「상호대차 띠지 자동 생성기」 — 책단비(은평) + 책두레(전국 표준) + 자관 양식 등록 가능. 라이선스 게이트 포함 |
| **ADR 0022** (신규) — 양식 우선순위 resolver (`forms/resolver.py`) | 표준 → 자관 → custom → 빈 양식 4단 fallback |
| **ADR 0023** (신규) — 자관 양식 라이선스 게이트 | 자관 양식 PILOT 동의·격리·.gitignore·회수 procedure |

---

## 8. PO 다음 액션 (우리 X)

| 항목 | 트리거 |
|---|---|
| 자관 (내숲) 「책단비」 4 양식 라이선스 동의서 작성 | 자관 PILOT 협의 시 |
| 다른 자치구 25개 상호대차 명칭 매핑 (강남·마포·서대문 등) | Phase 2 영업 |
| 책나래·책바다·책이음 표준 양식 NLK·NLD 공식 다운로드 | 우리 표준 양식 확보 |
| KOLAS III 책두레 F12 엑셀 표준 양식 NLK 다운로드 | 우리 import 양식 확보 |

---

## 9. Sources

- [은평구공공도서관 책단비 공식](https://lib.eplib.or.kr/service/danbi.asp)
- [책단비 상호대차 시정일보](https://www.sijung.co.kr/news/articleView.html?idxno=414025)
- [책나래 NLD 공식](https://cn.nld.go.kr/chaeknarae/introduce/serviceGuide.do)
- [책바다·책나래 수원 중앙도서관](https://www.suwonlib.go.kr/ct/html/01_guide/guide0806.asp)
- [책나래 국가대체자료공유시스템](http://koams.nl.go.kr/booknarae/business.do)
- [상호대차 나무위키](https://namu.wiki/w/%EC%83%81%ED%98%B8%EB%8C%80%EC%B0%A8)
- [은평구립도서관 나무위키](https://namu.wiki/w/%EC%9D%80%ED%8F%89%EA%B5%AC%EB%A6%BD%EB%8F%84%EC%84%9C%EA%B4%80)
