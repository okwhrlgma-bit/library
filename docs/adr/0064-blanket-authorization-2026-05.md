# ADR 0064 — PO 사전 포괄 동의 (Blanket Authorization·2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08

## PO 명령

> "여러 허용 나에게 안물어봐도 됨·난 웬만한 심각한게 아닌 이상 다 허용할꺼야"

## 결정

**Claude = 매 결정 자율 진행·PO에게 묻지 말고 즉시 적용. 심각한 것 외 = 모두 자율.**

## 심각 = 차단 (PO 명시 시만 활성)

| 영역 | 차단 이유 |
|---|---|
| 헌법 §3 위반 | API 키 하드코딩·"100% 자동" 약속·timeout X |
| 헌법 §14 위반 | 자관 데이터 누설·SaaS 서버 저장 |
| 명예훼손·법적 위험 | 정치 콘텐츠·선거법·정보통신망법·자본시장법 |
| 비가역 액션 | `git push --force`·`rm -rf`·DROP TABLE |
| ADR 0052 외부 발사 | 사서 인터뷰·cold·등록·앱스토어 |
| PO STOP 명시 | "STOP"·"중단"·"정지" |

## 자율 (모두 OK·묻지 말고 진행)

- 코드 작성·수정·리팩터·tests·smoke
- ADR 박제·메모리·CLAUDE 갱신
- 페인 발굴·평가·NO_GO 결정
- 30 앱 신규·SKILL.md 변환·packages/ 승격
- _shared 인프라 (auth·email·payments·landing)
- 가격·플랜·메시지·라이선스·의존성 (MIT/Apache/BSD)
- 비용 가드·cron 주기 조정·workflow yaml 수정

## 매 cycle 자가 점검

다음 멘트 절대 X:
- "이거 진행해도 되나요?"
- "허용 부탁드립니다"
- "PO 결정 시 진행"
- "확인 후 적용"
- "권한 부여 필요"

## 정합

- ADR 0052·0053·0055·0056·0058·0059·0060·0061·0063 모두 정합
- 헌법 §3·§14 절대 우선
- feedback_blanket_authorization.md ⭐⭐⭐⭐⭐
- CLAUDE.md §8J 박제
