# ADR 0009 — §33 미국 동아시아 컬렉션 활성화 트리거

**상태**: accepted (트리거 미충족 = inactive 유지)
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

`KORMARC_명세서_§33_미국시장진출.docx` — 하버드-옌칭·UC버클리 등 동아시아 컬렉션 도서관에 KORMARC + 880 + ALA-LC 로마자 변환 SaaS 공급. 권당 0.5 USD ≈ 700원 (한국 가격 7배).

현재 코드: `src/kormarc_auto/conversion/marc21_east_asian.py` 작성 완료, **`ACTIVATED = False`**로 inactive. 호출 시 `RuntimeError`로 실수 차단.

질문: 언제 활성화? 너무 빨리 = 한국 시장 영업 자원 분산. 너무 늦게 = 미국 매출 기회 상실.

## 결정

다음 **3개 모두 충족 시에만** 활성화 (`KORMARC_EAST_ASIAN_ACTIVATED=1` 환경변수 + 코드 `ACTIVATED = True` 변경):

1. **한국 매출 월 200만원 이상** (3개월 연속 — 매출 안정 신호)
2. **베타 사서 50명 이상** (한국 PILOT 검증 완료)
3. **미국 동아시아 컬렉션 도서관 1곳 이상 LOI** (Letter of Intent — "관심 있다" 서면)

## 결과 (활성화 시)

- 영업 자원 한국 70% / 미국 30% 분배
- 가격: 권당 0.5 USD = 약 700원 (한국 100원의 7배)
- 매출 시뮬: 미국 도서관 5곳 × 월 1,000권 × 700원 = **350만원/월** 추가
- 영어 docs·계약서 별도 (한국 docs와 동시 유지)

## 트레이드오프

✅ **장점**
- 한국 시장 BEP 후 매출 자연 확장 (분산 X)
- 우리 880 + 로마자 변환은 글로벌 동아시아 컬렉션 고유 우위
- 환율 헤지 (USD 매출 → 한국 인플레이션 방어)

❌ **단점**
- 영어 OJT·고객 지원 (PO 1인 운영 한계)
- 결제 PG 별도 (Stripe vs 포트원 USD 어그리게이션)
- 시차 (한국 사서 + 미국 사서 동시 응대 불가능)

## 완화 조치 (트리거 충족 후)

- 미국 영업은 **이메일 + Zoom 비동기**만, 24시간 SLA 대신 영업일 48시간
- 미국 결제는 **Stripe USD** 별도 도입 (한국 포트원과 분리)
- 영어 문서는 핵심 5개만 우선 (`README.en.md`·`pricing.en.md`·`api.en.md`·`terms-of-service.en.md`·`privacy-policy.en.md`)
- 미국 PILOT은 **하버드-옌칭 1곳 집중** (UC버클리는 후순위)

## 트리거 미충족 시 정책

- `marc21_east_asian.py` 코드는 **유지** (삭제 X)
- 어셔션 추가 검토: `assert_us_module_inactive` — 트리거 미충족 시 ACTIVATED=False 검증
- `docs/global-strategy.md` (이미 존재)에 트리거 진척 매월 갱신

## 6개월 후 되돌릴 수 있는가?

**Y** — `ACTIVATED = False`로 회귀 가능. 미국 PILOT 실패 시 영어 docs는 보존 (해외 한국학 도서관 무료 마케팅 자산).

## 측정 트리거

`scripts/aggregate_revenue.py` (다음 commit 후보)에서 매월 자동 산출:
- 한국 매출 월 200만원 → 측정 1
- 베타 사서 누적 50명 → `logs/signups.jsonl` 카운트
- LOI 도서관 → PO 수동 기록 (`logs/us_loi.jsonl`)

3개 모두 충족 시 PO에게 알림 → ACTIVATED 변경 PR 작성.

## 관련 자료

- `src/kormarc_auto/conversion/marc21_east_asian.py` — inactive 모듈
- `tests/test_marc21_east_asian.py` — `test_inactive_by_default` (ACTIVATED=False 보호)
- `docs/global-strategy.md` — 한·일·영어권 4단계
- `KORMARC_명세서_§33_미국시장진출.docx` — PO 명세
