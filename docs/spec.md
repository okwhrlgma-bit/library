# 마스터 명세서 — kormarc-auto

> 이 파일은 PO가 정리한 종합 명세서를 담는 자리입니다.
> 별도 대화에서 받은 긴 명세서(시장 분석·API 상세·KORMARC 매핑·KDC 알고리즘·KOLAS 출력 형식 등)를 여기에 붙여넣으세요.

---

## 빠른 참조 (헌법 보완)

### 데이터 흐름 핵심

```
ISBN 입력 (또는 사진 → 바코드 추출)
   ↓
[Stage 1] 국립중앙도서관 ISBN API
   ↓ 부재 시
[Stage 2] KOLIS-NET 통합 목록
   ↓ 부재 시
[Stage 3] 알라딘 ItemLookUp
   ↓ 부재 시
[Stage 4] 카카오 책 검색
   ↓ ISBN조차 없는 경우
[Stage 5] Claude Vision (표지/판권지/목차 분석)
   ↓
[Aggregator] 출처별 신뢰도 가중 통합
   ↓
[Builder] BookData → pymarc.Record
   ↓
[KDC Classifier] AI 추천 3개 (사서 선택)
   ↓
[Vernacular] 한자 감지 → 880 페어 생성
   ↓
[Validator] 008 길이, ISBN 체크섬, 필수 필드
   ↓
[KOLAS Writer] {ISBN}.mrc (UTF-8, ISO 2709)
```

### 데이터 출처 신뢰도 가중

| 소스 | 신뢰도 | 비고 |
|---|---|---|
| 국립중앙도서관 ISBN | 0.95 | 한국 자료 1순위 |
| KOLIS-NET | 0.92 | 다른 도서관 검증 데이터 |
| 알라딘 | 0.80 | 상용 데이터, 출처 표시 의무 |
| 카카오 | 0.75 | 보조 |
| Claude Vision (사진) | 0.65 | 사람 검토 필수 |
| Claude Vision + 외부 API 보강 | 0.85 | 교차 검증 |

### 필드별 자동화 가능성

- **100% 자동**: 005, 008(부분), 020, 040, 264, 300, 336/337/338
- **90%+ (사서 확인)**: 100, 245, 250, 490, 505, 520, 700
- **50~80% (AI 추천 + 사서 결정)**: 056(KDC), 082(DDC), 650(주제명), 049(청구기호)
- **수동 (AI 보조)**: 500(주기), 521(이용대상), 530(부가형식)

---

## 명세서 본문

(여기에 별도 대화에서 받은 종합 명세서를 붙여넣으세요. 권장 섹션:
1. 시장 분석 (KOLAS, 북이즈, 제이넷 비교)
2. 외부 API 상세 (요청/응답 예시)
3. KORMARC 필드 매핑표 전체
4. KDC 자동 분류 알고리즘 (다단계 + AI 프롬프트)
5. 880 한자 병기 자동 생성
6. KOLAS III 자동 반입 형식
7. 독서로DLS 출력 형식
8. UI/UX 와이어프레임
9. 테스트 골든 데이터셋
10. 법적/윤리적 주의사항)

---

## 다음 세션 작업 큐

### 완료 (2026-04-25 v0.3)
- [x] Phase 2: Claude Vision 2단계 (Haiku ISBN → Sonnet 종합)
- [x] Phase 3: KDC AI 분류 (Sonnet + tool_use + prompt caching)
- [x] Phase 3+: Subject(650) NLSH AI 추천
- [x] Phase 4: Streamlit UI (모바일 반응형, 4탭)
- [x] Phase 5: FastAPI REST 서버 + 인증 + 사용량 카운터
- [x] 검색: NL/알라딘/카카오 키워드 통합 검색
- [x] 출력 포맷: DLS·MARCXML·CSV·KOLAS 모두
- [x] 사서 가치: 049 청구기호, KOLAS 사전 검증, KOLIS-NET 비교
- [x] 모바일 인프라: cloudflared/ngrok 자동 설치 + 권한 사전 등록
- [x] 수익화 가설 §12 헌법화 + pricing.md

### 다음 세션
- [ ] **PO 액션**: ANTHROPIC_API_KEY/NL_CERT_KEY 등 .env 채우기
- [ ] **PO 액션**: cloudflared 1회 로그인 (`docs/mobile-tunnel.md`)
- [ ] **PO 액션**: 베타 사서 1~2명 모집
- [ ] 골든 데이터셋 30권 수집 (사서 검증 정답 KORMARC)
- [ ] 정확도 측정 + `docs/test_results.md` 갱신
- [ ] 사서 베타 인터뷰 → 우선순위 재조정
- [ ] 결제 시스템 정식화 (포트원/토스)
- [ ] 008 발행국부호 매핑 전체 보강 (KORMARC 매뉴얼 PDF 입수)
- [ ] librarian_helpers/call_number 도서관별 규칙 JSON 1관 작성
