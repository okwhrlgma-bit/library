# B2B 도서납품업체 사용 가이드

> **대상**: 학교도서관·공공도서관에 도서를 납품하면서 KORMARC `.mrc` 파일까지 함께 납품하는 도서납품업체.
> **시장 근거**: 학교도서관 95%가 마크 작업을 외주(도서납품업체)에 의존 (2023 뉴시스). 도서납품업체는 권당 800~1,500원의 마크 비용을 청구. kormarc-auto B2B 도입 시 권당 100원 → **마진 700~1,400원/권**.

---

## 1. 5분 도입 가이드

### 1.1 가입 (이메일 1개)

```bash
curl -X POST https://api.kormarc.kr/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "vendor@example.com", "library_name": "○○도서납품"}'
```

응답:

```json
{
  "ok": true,
  "api_key": "kma_xxxxxxxxxxxxxxxxxxxxxx",
  "free_quota": 50,
  "ui_url": "https://app.kormarc.kr",
  "api_url": "https://api.kormarc.kr"
}
```

→ 받은 `api_key`로 즉시 50건 무료 테스트 가능.

### 1.2 ISBN 1,000건 한 번에 처리

```bash
curl -X POST https://api.kormarc.kr/batch-vendor \
  -H "X-API-Key: kma_xxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "isbns": ["9788936434120", "9788932473901", "9788983927774"],
    "agency": "VENDOR1"
  }'
```

응답 (각 ISBN별):

```json
{
  "ok": true,
  "total": 3,
  "success": 3,
  "failed": 0,
  "results": [
    {
      "isbn": "9788936434120",
      "ok": true,
      "title": "작별하지 않는다",
      "author": "한강",
      "kdc": "813.7",
      "confidence": 0.95,
      "errors": [],
      "mrc_base64": "MDA1MTRu..."
    }
    ...
  ]
}
```

`mrc_base64` 디코딩 → `.mrc` 파일 → KOLAS·DLS·SOLARS 즉시 반입.

### 1.3 Python 스크립트 예시 (1,000건/회 처리)

```python
import base64, requests, csv

API_KEY = "kma_..."
ENDPOINT = "https://api.kormarc.kr/batch-vendor"

# 1) 납품 ISBN 리스트 로드 (CSV)
with open("acquisitions.csv", encoding="utf-8") as f:
    isbns = [row["ISBN"].replace("-", "") for row in csv.DictReader(f)]

# 2) 1,000개씩 청크
def chunks(lst, n=1000):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# 3) 일괄 호출
for batch in chunks(isbns):
    r = requests.post(
        ENDPOINT,
        headers={"X-API-Key": API_KEY},
        json={"isbns": batch, "agency": "VENDOR1"},
        timeout=120,
    )
    r.raise_for_status()
    for result in r.json()["results"]:
        if result["ok"]:
            mrc = base64.b64decode(result["mrc_base64"])
            with open(f"output/{result['isbn']}.mrc", "wb") as out:
                out.write(mrc)
        else:
            print(f"실패: {result['isbn']} ({result.get('reason')})")
```

---

## 2. 가격·정산

| 항목 | 가격 |
|---|---|
| 무료 체험 | 신규 50건 |
| 권당 과금 | **100원/건** (성공 처리만 차감) |
| 월 정액 (대) | **30만원/월 무제한** — 500권/월 이상이면 권장 |

- **마진 계산** (학교도서관 외주 단가 800원 기준):
  - 1,000권/월 도입 시: 매출 80만원 - kormarc 100원×1,000 = **순이익 70만원**
  - 5,000권/월 도입 시: 매출 400만원 - kormarc 30만원(월정액) = **순이익 370만원**

- **세금계산서**: 사업자등록 후 자동 발행. 도서관 예산 분기제(4월·10월) 결제 환영.
- **결제 수단**: 카카오페이·계좌이체 (PG 도입 후 신용카드 추가 예정).

---

## 3. 정확도·품질 보증

- **3중 폴백**: NL Korea(공식) → KOLIS-NET → 알라딘 → 카카오. 1순위 미조회 시 자동 다음 소스.
- **신뢰도 점수**: 각 결과에 `confidence` 0.0~1.0. 0.85 미만은 사서 검토 권장.
- **검증 경고**: `errors` 배열에 008/020/245 등 KORMARC 표준 위반 자동 검출.
- **880 자동**: 한자 병기 표제 자동 페어 생성.
- **출처 표시**: 알라딘 데이터 사용 시 `attributions`에 의무 표시 자동 포함.

품질 한도 (PO 책임):
- KDC 분류·주제명은 **AI 추천 후보**. 최종 결정은 사서.
- 옛 책·자가출판 ISBN-10·자료유형 비도서는 사진 입력 권장 (`/photo`).

---

## 4. KOLAS III 종료(2026-12-31) 마이그레이션 영업

학교·공공도서관 거래처에 **마이그레이션 안내** 메일 템플릿:

> ○○도서관 사서 선생님께,
>
> 국립중앙도서관이 발표한 바와 같이 **KOLAS III 표준형 기술지원이 2026년 12월 31일에 종료**됩니다 (NL 공지).
>
> 후속 시스템(예: KOLAS IV·KOLASYS-NET)으로 데이터를 이전하실 때, 저희가 그동안 납품한 도서의 KORMARC `.mrc` 파일은 **표준 형식이라 어떤 후속 시스템에도 그대로 import 가능**합니다.
>
> 신규 발주 도서의 경우, 저희가 도입한 kormarc-auto SaaS로 5초 안에 KORMARC를 생성합니다 — KOLAS·DLS·SOLARS·Koha 모두 호환.
>
> 마이그레이션 일정·지원이 필요하시면 답장 부탁드립니다.

`/migrate-from-kolas` 엔드포인트(GET, 인증 불필요)로 자동 안내 페이지를 도서관에 그대로 공유 가능.

---

## 5. 다음 단계

1. `/signup`으로 키 발급 (50건 무료)
2. 거래처 도서관 1곳 PILOT — 한 달 분 ISBN 100~200건 일괄 처리
3. 정확도·시간 절감 측정 (사서 면담)
4. 월 정액 전환 시 PO에 직접 상담 — `contact@kormarc-auto.example`

---

## 부록: 응답 필드 사양

| 필드 | 설명 |
|---|---|
| `ok` | 단건 성공 여부 |
| `isbn` | 입력 ISBN (정규화 후) |
| `title` | 본표제 (245 ▾a) |
| `author` | 책임표시 (245 ▾c) |
| `kdc` | KDC 분류 (056 ▾a) |
| `confidence` | 통합 신뢰도 |
| `errors` | KORMARC 검증 경고 |
| `mrc_base64` | ISO 2709 MARC `.mrc` 바이너리 base64 |
| `reason` | 실패 시 사유 (`no_data` / 예외 메시지) |

---

**문의**: PO `contact@kormarc-auto.example` · 응답 24시간 이내 (영업일).
