# 비코드 자동화 (Non-Code Automation)

캐시카우 SaaS 운영의 절반 이상은 코드가 아닙니다. 이 문서는 코드 외 자동화 4축의 즉시 사용 가능한 시작점을 정리합니다.

## 4개 축

| 축 | 스크립트 | cron 권장 | 자동 발송 가능? |
|---|---|---|---|
| **콘텐츠/SEO** | `automation/content_pipeline.py` | 매일 1회 | 아니오 (PR 머지로) |
| **고객지원** | `automation/support_triage.py` | 새 티켓마다 (webhook) | 부분적 (how-to만) |
| **결제 던닝** | `automation/dunning.py` | 매일 1회 | 아니오 (30일은 검토) |
| **성장 분석** | (다음 분기) | 주간 | n/a |

## 1. 콘텐츠/SEO 파이프라인

### 흐름
```
content/queue.txt (키워드 큐)
       ↓
content_pipeline.py
       ↓
[Sonnet 초안] → [Opus 팩트체크]
       ↓
content/drafts/<date>-<slug>.md  (검증 노트 포함)
       ↓
사람 검토 → PR 머지 → 발행
```

### 셋업
1. `content/queue.txt`에 키워드를 한 줄씩 추가 (월 30개 권장)
2. cron 등록:
   ```cron
   0 9 * * * cd /path/to/project && python automation/content_pipeline.py --auto-pr
   ```
3. PR이 자동 생성됨. `content,needs-review` 라벨 단 PR을 사람이 검토 후 머지.

### 비용 (대략)
- Sonnet 초안: 약 $0.02-0.05 / 글
- Opus 검증: 약 $0.05-0.10 / 글
- **월 30글: $2-5**

### 함정
- **Opus가 PASS해도 사람 검토 필수**: 사실관계 환각은 Opus도 함
- **같은 키워드 중복 방지**: queue에 추가하기 전 `content/drafts/`에 grep
- **클릭베이트 금지**: 프롬프트에 명시했지만 톤이 미묘하게 자랑조 → 검토 시 거르기

---

## 2. 고객지원 자동 분류 + 응답 초안

### 흐름
```
새 티켓 (webhook from Crisp/Intercom/...)
       ↓
support_triage.py
       ↓
[Haiku 분류] → bug | billing | feature-request | how-to | abuse | spam
       ↓
[Sonnet 응답 초안]  (abuse/spam 제외)
       ↓
tickets/<id>/draft.md  (사람 검토 후 발송)
```

### 셋업
1. 티켓 시스템(Crisp/Intercom/Zendesk 등)에서 새 티켓 webhook 설정
2. webhook 받는 엔드포인트:
   ```python
   # FastAPI 예시
   @app.post("/webhook/ticket")
   async def on_ticket(payload: dict):
       json_str = json.dumps({"id": payload["id"], "body": payload["body"]})
       subprocess.run(
           ["python", "automation/support_triage.py"],
           input=json_str, text=True, check=True
       )
   ```
3. `tickets/` 폴더에 초안이 쌓임. 매일 아침 일괄 검토 후 발송.

### 자동 발송 결정 트리
```
처음 30일:           모든 카테고리 사람 검토
30-90일:             how-to만 자동 발송 (오답 추적)
90일 후 신뢰도 기반: how-to 95% 정확률 → 자동 발송 유지
                     billing/bug 항상 사람 검토
```

### 함정
- **abuse 카테고리는 응답하지 마라**: 자극할 뿐. 무시 + 신고.
- **billing 자동 발송 절대 금지**: 환불·청구 오해는 즉시 분쟁이 됨.
- **카테고리 학습**: 매주 `tickets/`를 보고 잘못 분류된 케이스를 `learnings.md`에 기록 → 라우터 프롬프트 개선.

---

## 3. Stripe 던닝 자동화

### 흐름
```
Stripe API에서 실패 invoice 조회 (D+1, D+3, D+7, D+14)
       ↓
dunning.py
       ↓
[Sonnet 단계별 톤 차별 초안]
       ↓
tickets/dunning/<customer>-stage<N>.md
       ↓
사람 검토 후 발송 (또는 90일 후 자동)
```

### 셋업
1. `STRIPE_SECRET_KEY` 환경변수
2. cron:
   ```cron
   0 10 * * * cd /path/to/project && python automation/dunning.py
   ```
3. 매일 오전 10시에 실패 고객별 단계 판정 + 초안 생성.

### 단계별 톤 가이드 (이미 코드에 반영)
| 단계 | 시점 | 톤 | 핵심 |
|---|---|---|---|
| stage1-friendly | D+1 | 친절 | 결제 시도 실패 알림, 카드 갱신 링크 |
| stage2-reminder | D+3 | 차분 | 재시도, 서비스 제한 가능성 |
| stage3-urgent | D+7 | 단호 | 취소 임박, 명확한 마감 |
| stage4-final | D+14 | 사무적 | 자동 취소 안내 |

### 함정
- **자동 발송 절대 신중**: 결제 이슈는 분쟁의 90%. 처음엔 사람이 직접 보내세요.
- **이미 결제 성공한 고객에게 보내지 않기**: invoice 상태가 `paid`로 바뀌었는지 발송 직전 한 번 더 확인.
- **세금/통화 표기 오류**: USD/KRW 혼동, 부가세 포함 여부.

---

## 4. (예고) 성장 분석 자동화

다음 단계로 추가 예정:
- PostHog/GA 데이터 → Sonnet 주간 인사이트 리포트
- A/B 테스트 결과 자동 해석
- 경쟁사 가격·기능 변경 모니터링

지금은 위 3축만 운영해도 1인 SaaS의 운영 부담이 크게 줄어듭니다.

---

## 모든 비코드 자동화에 적용되는 원칙

1. **자동 발송 = 영구 보관**: 한 번 보낸 이메일은 못 되돌림. 자동화 신뢰 기간 충분히 길게.
2. **드라이런 옵션 항상 추가**: `--dry-run` 플래그로 발송 직전까지만 실행하고 멈출 수 있어야 함.
3. **샘플링**: 처음에는 5%만 자동 발송, 점진적 확대.
4. **휴먼 인 더 루프**: 모든 초안에 `status: needs-review` 메타데이터 → 검토 안 된 건 발송 못 함.
5. **로그 보존**: 발송 이력은 최소 1년 — 분쟁·감사 대응용.
