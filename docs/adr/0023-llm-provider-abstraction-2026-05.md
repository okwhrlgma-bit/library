# ADR 0023 — LLM Provider 추상화 + EXAONE/Solar Pro 폴백 (2026-05-03)

## Status
Proposed (M8 모듈 구현 시 Accepted)

## Context
현재 Anthropic API 단독 의존:
- 가격 인상 위험 (확률 40% / 6~18개월)
- 차단·단종 위험 (지정학적·정책 변동)
- 한국 정부·공공 = 국내 LLM 선호 가능성 (특히 NLK·KAIT 발주)

Part 87 위험 매트릭스 #4 = 운영 연속성 hedge 필요.

## Decision
**LLM Provider 추상 인터페이스 도입 + 다중 프로바이더 폴백:**

```python
class LLMProvider(Protocol):
    def generate_marc(...) -> MarcDraft: ...
    def classify_kdc(...) -> str: ...
    def extract_subjects(...) -> list[str]: ...
```

**프로바이더 우선순위**:
1. Anthropic Sonnet 4.6 / Haiku 4.5 (현재 1차) — 한국어 우수·prompt cache 90% 할인
2. **Upstage Solar Pro 2** (한국어 폴백·국내 데이터 주권)
3. **OpenAI GPT-5.4 mini** (OpenRouter 경유·다국어)
4. **EXAONE 3.5 7.8B** (자체 호스팅 vLLM·완전 주권 옵션·비용 hedge)

환경변수 `KORMARC_LLM_PRIMARY`로 토글, 5xx 자동 폴백.

## Consequences

### 긍정
- 24h 내 폴백 가능 (운영 연속성)
- 정부 발주 시 "국내 LLM 선택지 보유" = 영업 우위
- EXAONE 자체 호스팅 = 비용 통제 (특히 디딤돌 R&D 후 자금 확보 시)

### 부정
- 멀티 프로바이더 유지보수 부담 ↑
- 프롬프트 호환성 차이 (각 프로바이더별 best practice)
- 황금셋 평가 (`tests/fixtures/golden_marc.jsonl`) 100건 운영 필요

### 후속
- M8 모듈 구현 (90분)
- `tests/fixtures/golden_marc.jsonl` 100건 큐레이션
- Langfuse dataset upload (M5와 통합)
- `docs/llm_strategy.md` 작성

## References
- Part 87 §9 M8 모듈
- Part 87 §11 위험 매트릭스 #4
- Upstage Solar Pro 2 (2025 한국어 LLM 1위)
- EXAONE 3.5 7.8B (LG AI Research)
