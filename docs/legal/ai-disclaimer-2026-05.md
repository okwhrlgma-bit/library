# AI 생성 결과 안내 (인공지능 기본법 §31 사전 대응)

> 시행일: 2026-05-04 (인공지능 기본법 §31 시행 2026.1.22 정합·사전 적용)
> 표시 위치: UI (Streamlit·Web)·약관·처리방침·API 응답 메타·CLI `kormarc-auto info` 4곳 동시
> 외부 858 출처 보고서 §6.6 정합

---

## 1. 핵심 안내문 (모든 surface 동일 문구)

> ⚠ **AI 생성 결과 안내** — 본 KORMARC 레코드는 인공지능(Anthropic Claude API)을 이용해 자동 생성된 **초안**이며, MARC 표준·서지 정확성에 오류(환각·hallucination)가 포함될 수 있습니다. 도서관 정식 등록 전 반드시 **자격 있는 사서가 검토·수정**하시기 바랍니다.

## 2. 표시 위치 4곳

### 2.1 UI (Streamlit·Web)
- 모든 결과 카드 상단 amber 배너 (always-visible)
- AI 생성 필드 = ghost text (italic·gray·ⓘ 아이콘·Cycle 10A P14 정합)
- 사서 ✓ 클릭 시 검정 정상 + ✅
- 화면 상단 "전체 거부" 빨간 escape hatch

### 2.2 처리방침 (privacy-policy-2026-05.md §9의2)
- 자동화된 결정 (§37의2) 입장 명시
- 사서 검토 전제 = "완전 자동화" 아님
- 설명요구 30일 내 회신

### 2.3 API 응답 메타
```json
{
  "fields": [...],
  "_meta": {
    "model_string": "claude-sonnet-4-6",
    "generation_timestamp": "2026-05-04T12:00:00Z",
    "input_hash": "abc123...",
    "deterministic": true,
    "ai_generated": true,
    "human_review_required": true,
    "ai_disclaimer": "본 레코드는 AI 자동 생성 초안·사서 검토 필수"
  }
}
```

### 2.4 CLI `kormarc-auto info`
```
=== AI 생성 안내 ===
본 도구가 생성하는 KORMARC = AI(Anthropic Claude) 자동 초안입니다.
도서관 정식 등록 전 사서 검토 필수.
인공지능 기본법 §31 정합·결정성 보장 (temperature=0·top_p=1·ADR 0028).
```

## 3. KORMARC 588 자동 stamp (Cycle 9 P13)

매 레코드 588 ▾a 한국어 stamp:

> "본 레코드는 kormarc-auto v0.6.0이 [SEOJI·data4library·Aladin] 기반으로 claude-sonnet-4-6 (temperature=0.0·seed=0)로 2026-05-04 생성한 초안임. 사서 검수 필수."

다운로드 옵션:
- **정식 (588 포함)** — 기본·납품 시 권장
- **compact (588 제거)** — 사서 검토 완료 후 정식 등록 시·audit log에 기록

## 4. 환각 (hallucination) 위험 영역

다음 필드는 AI 생성 시 환각 가능성 상대적으로 높음 — 사서 우선 검토:

| 위험도 | 필드 | 사유 |
|---|---|---|
| 🔴 높음 | 6XX 주제명·NLSH | LLM 단독 추론·외부 권위 X 시 |
| 🟡 중간 | 5XX 주기 (520 요약) | LLM 요약 재구성 |
| 🟡 중간 | 명저자 100/700 (생몰년·직위) | 저자 동명이인·옛 책 |
| 🟢 낮음 | 020 ISBN·245 표제 | 외부 API ground-truth |
| 🟢 낮음 | 008 fixed-position | 규칙 기반 |

## 5. 사서 책임 영역 (자동 결정 금지·헌법 §4)

다음은 자동 결정 X·사서 직접 입력:
- KDC 분류 최종 선택 (AI 추천 3개 → 사서 선택)
- 049 자관 등록번호·청구기호
- 880 한자 병기 (AI 자동 후 사서 검토)
- 9XX 자관 정책 필드

## 6. 회수·정정 절차

- **레코드 단위 정정**: UI 마이페이지 → 변경 이력 → "재생성" 또는 "수동 편집"
- **AI 출력 거부**: 화면 상단 "전체 거부" 또는 필드별 ✗
- **audit log 조회**: GET /audit/record/{id} (PIPA §35 본인 열람권·Cycle 9 P13)
- **audit log 파기 요청**: DELETE /audit/record/{id} (PIPA §36·tombstone event 추가·법적 추적 가능)

## 7. 분쟁 시 처리

- 1차: contact@kormarc-auto.example 30일 내 회신
- 2차: 개인정보분쟁조정위원회 (privacy.kisa.or.kr·1833-6972)
- 3차: 개인정보보호위원회 신고 (pipc.go.kr·02-2100-3056)

## 8. 변경 이력

- 2026-05-04 v1.0 (Cycle 10B 신설·외부 858 출처 보고서 정합·인공지능 기본법 §31 사전 대응)
