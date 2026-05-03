"""Anthropic prompt caching — T2-4 (Part 92 §A.6).

PO 명령 (Part 92): "8K-token cached prefix·1-hour TTL nightly·5-min interactive"
효과: cache write 1.25× / read 0.10× = 90% off / Batch API 50% off = 95% off 가능

작동:
1. ~8K 토큰 안정 prefix (system + KORMARC field reference + few-shot exemplars)
2. cache_control = {"type": "ephemeral", "ttl": "1h" or "5m"}
3. 모델 namespace 분리 (Haiku ≠ Sonnet ≠ Opus)
4. 결정성 = temperature=0·top_p=1 (provenance.py 통합)

비용 (May 2026 모델):
- Sonnet 4.6: $3 input / $15 output per MTok
- Haiku 4.5: $1 / $5
- Opus 4.7: $5 / $25 (1M context standard pricing)
- Cache write: 1.25×·Cache read: 0.10×

활용:
- nightly batch (1h TTL) = 자관 174 disaggregation 재측정
- interactive Streamlit (5m TTL) = 사서 ISBN 1건 처리
- Haiku 4.5 = 4096 token 최소 cache entry 주의
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

CacheTTL = Literal["5m", "1h"]


# KORMARC 필드 reference (안정 prefix·~3K 토큰)
KORMARC_FIELD_REFERENCE = """
KORMARC KS X 6006-0:2023.12 통합서지용 필드 reference:

00X 제어 필드:
- 001: 레코드 제어번호
- 005: 최종 처리 일시 (YYYYMMDDHHMMSS.0)
- 008: 부호화 정보 (40자리·날짜·언어·국가)

0XX 기술·식별:
- 020 ▾a ISBN-13 (13자리)·▾g 부가기호 (5자리)·▾c 가격
- 040 ▾a 목록작성기관·▾b 사용 언어·▾c 편목기관
- 049 ▾l 등록번호·▾f 별치기호·▾v 권차·▾c 복본
- 056 ▾a KDC 분류·▾2 6 (KDC 6판)
- 082 ▾a DDC 분류
- 090 ▾a 자관 청구기호

1XX 주표목 (개인저자 100·단체 110·회의 111·통일표제 130):
- 100 ▾a 개인 이름·▾d 생몰년·▾e 역할

245 표제 (필수):
- ▾a 본표제·▾b 부표제 ": "·▾c 책임표시 " / "
- 1지시기호 = 책임표시 동일 (1=같음·0=없음)
- 2지시기호 = 관제 길이 + 1 (관제 없으면 0)

250 판차·260/264 발행/제작·300 형태사항·336/337/338 RDA

4XX/8XX 총서:
- 490 총서명·800/810/830 총서 부출표목

5XX 주기:
- 505 ▾a 목차·520 ▾a 요약·588 ▾a 기술 자료원 (PCC AI provenance)

6XX 주제·NLSH:
- 650 ▾a 일반 주제명·▾2 nlsh / mesh / lcsh
- 600 인명·610 단체·611 회의·651 지명

7XX 부출표목 (개인 700·단체 710·통일표제 730)

880 한자·로마자 병기 (대체문자 표제·NLK 「로마자 표기 지침 2021」)

9XX 자관 (자관 정책)

KCR4 규칙 + 자관 49 prefix (EQ·CQ·WQ 등) + 이재철 도서기호.
"""


# Few-shot exemplars (~5K 토큰 추가)
FEW_SHOT_EXEMPLARS = """
예시 1 (단행본·한국문학):
input: ISBN 9788937437076·"어린 왕자"·생텍쥐페리·민음사·2007·KDC 863.2
output:
  245 10 ▾a 어린 왕자 / ▾c 생텍쥐페리
  100 1  ▾a 생텍쥐페리
  260    ▾a 서울 :▾b 민음사,▾c 2007
  056    ▾a 863.2 ▾2 6
  300    ▾a 150 p. ; ▾c 20 cm
  020    ▾a 9788937437076 ▾g 73810

예시 2 (의학·MeSH·Alma):
input: ISBN 9788991915082·"당뇨병 임상 가이드라인"·대한당뇨병학회·2024
output:
  245 10 ▾a 당뇨병 임상 가이드라인 / ▾c 대한당뇨병학회
  650  0 ▾a Diabetes Mellitus ▾2 mesh ▾0 https://id.nlm.nih.gov/mesh/D003920
  056    ▾a 513.6 ▾2 6
  082    ▾a 616.4 (DDC swap·KDC 5 → DDC 6)

예시 3 (학교 DLS 521):
input: ISBN 9788961723459·"중학교 수학 1학년 워크북"·교육청·2024·KDC 510
output:
  245 10 ▾a 중학교 수학 1학년 워크북
  521    ▾a LR (장학자료·DLS 521)
  056    ▾a 510 ▾2 6
"""


@dataclass(frozen=True)
class CachedSystemPrompt:
    """Anthropic 호출용 cached system prompt 구조."""

    text: str
    ttl: CacheTTL = "5m"  # 기본 = interactive
    model_id: str = "claude-sonnet-4-6"

    def to_anthropic_blocks(self) -> list[dict[str, Any]]:
        """Anthropic API 'system' 파라미터 형식 (cache_control 포함)."""
        return [
            {
                "type": "text",
                "text": self.text,
                "cache_control": {"type": "ephemeral", "ttl": self.ttl},
            }
        ]


def build_kormarc_system_prompt(
    *,
    persona: str = "general",
    ttl: CacheTTL = "5m",
    model_id: str = "claude-sonnet-4-6",
) -> CachedSystemPrompt:
    """KORMARC 자동 생성용 cached system prompt.

    Args:
        persona: "general"·"medical"·"school"·"academic"·"small"
        ttl: "5m" (interactive) | "1h" (nightly batch)
        model_id: Anthropic 모델

    Returns:
        ~8K 토큰 안정 prefix·자동 cache_control
    """
    persona_addendum = {
        "general": "",
        "medical": "\n의학 도서관 = MeSH 650 ▾2 mesh 자동·PubMed PMID 035 ▾a 자동.",
        "school": "\n학교도서관 = DLS 521 자료유형 자동 (BK·SR·NB·LR·ET).",
        "academic": "\n대학도서관 = DDC 082 + LCSH 650 ▾2 lcsh + Alma MARCXML.",
        "small": "\n작은도서관 = 자원봉사 onboarding·1인 운영 워크플로우.",
    }.get(persona, "")

    text = (
        "당신은 한국 도서관 사서를 보조하는 KORMARC 카탈로깅 전문가입니다. "
        "KCR4 규칙·KORMARC KS X 6006-0:2023.12·자관 49 prefix 정합 필수.\n\n"
        + KORMARC_FIELD_REFERENCE
        + "\n"
        + FEW_SHOT_EXEMPLARS
        + persona_addendum
        + "\n\n결정성 보장: temperature=0·top_p=1·동일 input = 동일 output."
    )

    return CachedSystemPrompt(text=text, ttl=ttl, model_id=model_id)


def estimate_cache_savings(
    monthly_calls: int,
    *,
    avg_input_tokens: int = 8000,  # cached prefix
    avg_output_tokens: int = 200,
    cache_hit_rate: float = 0.85,  # 85% 재사용 가정
    model_id: str = "claude-sonnet-4-6",
) -> dict:
    """월간 cache 절감 추정 (영업·비용 계획)."""
    pricing = {
        "claude-haiku-4-5-20251001": {"in": 1.0, "out": 5.0},
        "claude-sonnet-4-6": {"in": 3.0, "out": 15.0},
        "claude-opus-4-7": {"in": 5.0, "out": 25.0},
    }
    p = pricing.get(model_id, pricing["claude-sonnet-4-6"])

    # baseline (cache X)
    base_in_usd = monthly_calls * avg_input_tokens / 1_000_000 * p["in"]
    base_out_usd = monthly_calls * avg_output_tokens / 1_000_000 * p["out"]
    baseline_usd = base_in_usd + base_out_usd

    # cached
    write_calls = int(monthly_calls * (1 - cache_hit_rate))
    read_calls = monthly_calls - write_calls
    cached_in_write = write_calls * avg_input_tokens / 1_000_000 * p["in"] * 1.25
    cached_in_read = read_calls * avg_input_tokens / 1_000_000 * p["in"] * 0.10
    cached_out = monthly_calls * avg_output_tokens / 1_000_000 * p["out"]
    cached_usd = cached_in_write + cached_in_read + cached_out

    return {
        "monthly_calls": monthly_calls,
        "model_id": model_id,
        "baseline_usd": round(baseline_usd, 4),
        "cached_usd": round(cached_usd, 4),
        "savings_usd": round(baseline_usd - cached_usd, 4),
        "savings_pct": round((1 - cached_usd / baseline_usd) * 100, 1) if baseline_usd > 0 else 0,
        "savings_won": int((baseline_usd - cached_usd) * 1400),
    }


__all__ = [
    "FEW_SHOT_EXEMPLARS",
    "KORMARC_FIELD_REFERENCE",
    "CacheTTL",
    "CachedSystemPrompt",
    "build_kormarc_system_prompt",
    "estimate_cache_savings",
]
