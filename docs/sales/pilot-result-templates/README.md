# PILOT 결과 빈 템플릿 (4 페르소나)

> **사용**: PO 시연 직후 본 폴더의 4 JSON 빈 양식 중 하나를 복사 → `logs/interviews/<날짜>_<도서관>_<사서>.json`로 저장 → 채워넣기 → `python scripts/aggregate_interviews.py` 자동 집계.
> **자동 입력**: `python scripts/pilot_collect.py --persona macro` 인터랙티브 입력으로도 동등한 결과 생성 가능.

---

## 4 페르소나 JSON 양식

| 파일 | 페르소나 | 자관 사서 | 사용 시점 |
|---|---|---|---|
| [macro-template.json](macro-template.json) | ★ Excel 매크로 자작 | 사서 E | PILOT 1주 (5/2주) |
| [acquisition-template.json](acquisition-template.json) | 수서 | 사서 A | PILOT 2주 (5/3주) |
| [general-template.json](general-template.json) | 종합 | 사서 B·사서 C·사서 D | PILOT 3주 (5/4주) |
| [video-template.json](video-template.json) | 영상 편집 (영업 X) | 김신학 | PILOT 4주 통합 시 명시 제외 |

---

## 채워넣기 5 항목 우선순위

1. **NPS** (0~10): "다른 사서에게 추천 의향?" 점수
2. **q1_payment_band** (HIGH/MID/LOW/0): 결제 의향 4단
3. **time_saved_pct**: 수동 분 → 자동 분 백분율
4. **biggest_painpoints**: 여전한 페인 (1~3 항목)
5. **consent_kla_quote**: KLA 5.31 발표 인용 동의 (true/false) — PIPA 정합 ★

→ 나머지는 default 값 그대로 또는 PO 자유 추가.

---

## Sources

- `scripts/pilot_collect.py` (인터랙티브 입력)
- `scripts/aggregate_interviews.py` (집계 + by_persona)
- `docs/sales/pilot-week1-action-manual.md` §1.4~1.5 (Q1·NPS 측정 진행)
- `docs/saseo-personas-2026-04-28.md` (4 페르소나 정밀 정의)
