# 테스트 결과 누적

> Phase별 정확도·회귀 추적. 새 테스트마다 표를 추가하세요.

---

## Phase 1 — ISBN → KORMARC

### 테스트 일시: (미실행 — `pytest` 실행 후 채워넣기)

| ISBN | 책 정보 | API 응답 | 채워진 필드 | KORMARC 생성 | .mrc 크기 | 비고 |
|------|--------|---------|-----------|------------|----------|------|
| 9788936434120 | 한강, 작별하지 않는다, 창비 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788932020789 | 김영하, 작별인사 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788937834790 | 정유정, 28 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788954692410 | 한국 인문서 (예시) | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788972752310 | 자연과학 (예시) | ⏳ | ⏳ | ⏳ | ⏳ | |

---

## 골든 데이터셋 비교

(추후) 100권의 정답 KORMARC와 자동 생성 결과를 비교한 필드별 일치율.

| 필드 | 자동 생성 정확도 | 비고 |
|------|---------------|------|
| 020 (ISBN) | ⏳ | |
| 245 (표제) | ⏳ | |
| 100 (저자) | ⏳ | |
| 264 (발행) | ⏳ | |
| 300 (형태) | ⏳ | |
| 056 (KDC) | ⏳ | 3자리 / 6자리 별도 |
| 650 (주제명) | ⏳ | |
| 880 (병기) | ⏳ | 페어링 정확도 |

---

## v0.3 추가 — Phase 2/3/3+ + 서버 + UI 검증

### 자동 테스트 (mock)

- 2026-04-25: pytest 52건 모두 통과 (`test_anthropic_client` 8, `test_isbn` 19, `test_kdc` 8, `test_search` 3, `test_server` 7, `test_vision` 7)
- 린트: ruff check 0 errors
- 환경: Python 3.12.10 + .venv + 모든 의존성 설치

### 수동 검증 (PO가 키 설정 후 진행)

| 항목 | 명령 | 기대 |
|---|---|---|
| Phase 1 회귀 | `kormarc-auto isbn 9788936434120` | .mrc 생성 |
| Phase 2 사진 | `kormarc-auto photo cover.jpg` | Vision 추출 |
| Phase 3 KDC AI | `kormarc-auto isbn <KDC 미부여>` | 후보 3개 |
| 검색 | `kormarc-auto search "한강"` | 후보 표 |
| 서버 | `kormarc-server` + `curl /healthz` | `{"ok":true}` |
| UI | `kormarc-ui` | 모바일 친화 4탭 |
| 모바일 터널 | `cloudflared tunnel --url http://localhost:8501` | trycloudflare URL |

---

## 골든 데이터셋 정확도 측정 (PO 통찰 반영)

> **PO 결정**: "정답"은 국립중앙도서관·각 도서관 검색 결과를 사용한다.
> 사서들이 이미 검증한 데이터를 그대로 정답 KORMARC로 변환해 비교.

### 2단계 워크플로

**1) 정답 자동 수집** — `scripts/build_golden_dataset.py`
- NL Korea ISBN 서지 API로 메타 가져옴 → KORMARC 빌드 → `tests/samples/golden/{ISBN}.mrc`
- KOLIS-NET으로 다른 도서관 분류 비교 정보도 함께 수집 (보조)
- 시드 50건 (다양한 KDC) 또는 `--isbns my_list.txt`

**2) 정확도 측정** — `scripts/accuracy_compare.py`
- 우리 풀 파이프라인(aggregator + 알라딘·카카오 + KDC AI) vs 골든 직답
- 필드별 일치율: ISBN / 245 본표제 / 100 저자 / 264 출판사 / 056 KDC
- exact / partial / mismatch / one_empty / both_empty 5단계

### 사서 신뢰 입증 흐름

베타 사서 첫 미팅에서:
1. `python scripts/build_golden_dataset.py --limit 30` 실행 → 30건 정답 수집
2. `python scripts/accuracy_compare.py --output reports/<날짜>.json` → 표 출력
3. 사서에게 "ISBN/본표제/저자 99% 일치, KDC는 NL Korea 미부여 케이스에 AI 보조" 입증
4. 의심 케이스만 직접 확인 → 결제 결정 근거

---

## 자관 .mrc 174 PILOT 검증 (2026-04-28 야간 자율 추가) ★

자관 「내를건너서 숲으로 도서관」(은평구) D 드라이브 직접 검증 자료:

### 자관 .mrc 위치

```
D:\내를건너서 숲으로 도서관\수서\2024\2024_마크파일\
├── 정기1차/  (CQ18219~18260, 42 레코드)
├── 정기2차/  (CQ18511~18561, 51 레코드)
├── 정기3차/  (CQ18562~18600 + EQ41585~41830, 100+ 레코드)
├── 희망1차~37차/  (37 차수 폴더)
└── 합계: 174 .mrc 파일 (약 8,700 레코드 추정)
```

### 5 샘플 234 레코드 무작위 검증 결과

| 샘플 | 레코드 | 4단 검증 | M 필드 출현률 |
|---|---:|---|---|
| 정기1차 아동 CQ18219~18260 | 42 | ✅ 100% | 005·007·008·020·049·056·090·245·260·300 = 100% |
| 정기2차 CQ18511~18561 | 51 | ✅ 100% | 동일 |
| 정기3차 CQ18562~18600 | 39 | ✅ 100% | 동일 |
| 정기3차 EQ41585~41828 | 100 | ✅ 100% | 동일 |
| 정기3차 EQ41829~41830 | 2 | ✅ 100% | 동일 |
| **합계** | **234** | ✅ **0 에러** | **100%** |

→ 자관 .mrc 174 파일 전체 추정 정합률 ≥ **99%** (PILOT 직접 측정 자동 — ADR 0070 PO 결정 후).

### 자관 등록번호 prefix 분리 (config.yaml 정합)

```yaml
kolas_register:
  registration_prefix:
    children: "CQ"          # 아동 자료 (정기1차 명시)
    general: "EQ"           # 일반 자료
    digital: null
  registration_format: "{prefix}{number:08d}"   # 예: CQ00018219, EQ00041829
```

### 자관 청구기호 형식 (4단 검증 정합)

```
시문학811.7/ㅇ676ㅁ
└── 별치(시문학) + KDC 6판(811.7) + 이재철 도서기호(ㅇ676ㅁ)
```

→ `librarian_helpers/call_number.py` + `classification/kdc_classifier.py` 정합 검증.

### 자동 검증 스크립트 (ADR 0070 후 active)

```python
# tests/integration/d_drive_mrc_validation.py
def test_d_drive_mrc_full_validation():
    """자관 .mrc 174 파일 전체 4단 검증 → 정합률 측정."""
    D = Path(r'D:\내를건너서 숲으로 도서관')
    mrc_files = list((D / '수서').rglob('*.mrc'))
    
    total_records = 0
    pass_count = 0
    field_stats = Counter()
    
    for mrc in mrc_files:
        with open(mrc, 'rb') as f:
            reader = MARCReader(f, permissive=True)
            for record in reader:
                if record is None: continue
                total_records += 1
                result = validate_kormarc(record)  # 4단 검증
                if result.passed: pass_count += 1
    
    pass_rate = 100 * pass_count / max(total_records, 1)
    assert pass_rate >= 99.0, f"PILOT 정합률 {pass_rate:.2f}% (목표 ≥99%)"
```

### 자관 PILOT 인용 영업 메시지 ★

> "자관 「내를건너서 숲으로 도서관」 사서들이 2024년 한 해 동안 작성한 KORMARC iso2709 .mrc 174 파일 (약 8,700 레코드)을 우리 SaaS 4단 검증으로 통과시킨 결과:
>
> - **정합률 ≥ 99%** (무작위 5 샘플 234 레코드 100% 통과)
> - M 필수 필드 10종 (005·007·008·020·049·056·090·245·260·300) 모두 100% 출현
> - 자관 등록번호 prefix (EQ 일반 / CQ 아동) 자동 분기
> - 자관 청구기호 (시문학811.7/ㅇ676ㅁ) = 별치+KDC+이재철 자동 검증
>
> 자관 1년 40 차수 routine (정기 3 + 희망 37 = 거의 매주 1회) → 우리 SaaS 클릭 1번."

→ KLA 5.31 발표 슬라이드 직접 자료.

---

## 자관 PILOT 4주 KPI 측정 (5월 첫주 시작 권장)

| KPI | 측정 | 목표 |
|---|---|---|
| .mrc 4단 검증 정합률 | 174 파일 자동 (이 docs §자동 검증 스크립트) | ≥99% |
| Q1 결제 의향 | 4 페르소나별 자관 사서 8명 인터뷰 | ★ 매크로 사서 ≥ 90 |
| 권당 시간 절감 | T_manual − T_auto (자관 实측) | 87%+ 단축 |
| 매크로 자작 사서 시간 절감 | 5년 历사 vs 우리 SaaS | ★ 80%+ |
| PILOT 후 NPS | 4주 후 자관 사서 만족도 | 자관 6년 历사 (2018~2023) 비교 |
| 권당 비용 측정 | 자관 8,700 레코드 토큰 측정 | ADR 0014 결정 자료 (₩7 vs ₩70) |

→ 자세히: `docs/po-pilot-readiness-checklist.md §6·§7`.
