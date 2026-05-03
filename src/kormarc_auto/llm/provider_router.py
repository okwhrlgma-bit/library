"""LLM Provider 추상화·라우팅 — M8 (Part 92 §1.4 critical-path).

PO 명령 (Part 92): "Anthropic-only = 공공 deathline"
- DPG 가이드라인 2.0 (2025-04-16): CSAP 인증·G-Cloud 권장
- PIPC 생성형 AI 안내서 (2025-08-06): 폐쇄형 LLM 권장·CPO 거버넌스
- 결과: api.anthropic.com 행정망 차단 = 공공 영업 deathline

해결: 5 provider 추상화·portable prompts·자동 폴백.

Provider:
- anthropic_direct: api.anthropic.com (개발·체험판·민간만)
- bedrock_seoul: AWS Bedrock ap-northeast-2 (CSAP·Claude 사용 가능·공공)
- naver_hcx: HyperCLOVA X (도메스틱·공공 선호)
- kt_midm: KT 믿:음 (도메스틱)
- lg_exaone: LG EXAONE (도메스틱·OSS)
- azure_openai_korea: Azure Korea Central (GPT)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol

ProviderId = Literal[
    "anthropic_direct",
    "bedrock_seoul",
    "naver_hcx",
    "kt_midm",
    "lg_exaone",
    "azure_openai_korea",
]

DeploymentSegment = Literal["public_govt", "academic", "private", "personal"]


# Provider 메타 (CSAP 정합·세그먼트별 사용 가능)
PROVIDER_META: dict[ProviderId, dict] = {
    "anthropic_direct": {
        "name": "Anthropic Direct (api.anthropic.com)",
        "csap_certified": False,
        "korean_data_residency": False,
        "model_family": "Claude (Sonnet 4.6·Haiku 4.5·Opus 4.7)",
        "allowed_segments": ["private", "personal"],
        "blocked_segments": ["public_govt"],  # 행정망 차단
        "cost_tier": "competitive",
        "notes": "민간·개인 SaaS만·공공 영업 X·prompt cache + Batch 95% off",
    },
    "bedrock_seoul": {
        "name": "AWS Bedrock Seoul (ap-northeast-2)",
        "csap_certified": True,  # AWS Korea CSAP 안전등급
        "korean_data_residency": True,
        "model_family": "Claude (Anthropic via Bedrock)",
        "allowed_segments": ["public_govt", "academic", "private", "personal"],
        "blocked_segments": [],
        "cost_tier": "20~30% 프리미엄 (Anthropic 직접 대비)",
        "notes": "공공 영업 unblock·Anthropic 모델 = 동일 prompt portable",
    },
    "naver_hcx": {
        "name": "Naver HyperCLOVA X (HCX-005·HCX-DASH)",
        "csap_certified": True,  # NCP CSAP
        "korean_data_residency": True,
        "model_family": "HyperCLOVA X",
        "allowed_segments": ["public_govt", "academic", "private"],
        "blocked_segments": [],
        "cost_tier": "domestic 가격 (한국 시장 정합)",
        "notes": "도메스틱 LLM 1순위·NIA/MOIS 선호·CLOVA X source-citing 기본",
    },
    "kt_midm": {
        "name": "KT 믿:음",
        "csap_certified": True,
        "korean_data_residency": True,
        "model_family": "KT MIDM",
        "allowed_segments": ["public_govt", "academic", "private"],
        "blocked_segments": [],
        "cost_tier": "domestic 가격",
        "notes": "KT Cloud 통합·경기도 생성형 AI 사례",
    },
    "lg_exaone": {
        "name": "LG EXAONE 3.5 (vLLM 자체호스팅 옵션)",
        "csap_certified": True,
        "korean_data_residency": True,
        "model_family": "EXAONE 3.5 7.8B / 32B",
        "allowed_segments": ["public_govt", "academic", "private", "personal"],
        "blocked_segments": [],
        "cost_tier": "self-host = ₩0 추론·인프라만 필요",
        "notes": "자체호스팅 가능·OSS·디딤돌 R&D·완전 주권",
    },
    "azure_openai_korea": {
        "name": "Azure OpenAI Korea Central",
        "csap_certified": True,  # Azure Korea CSAP
        "korean_data_residency": True,
        "model_family": "GPT-5.4 / GPT-4.1",
        "allowed_segments": ["public_govt", "academic", "private", "personal"],
        "blocked_segments": [],
        "cost_tier": "Microsoft 라이선스 정합",
        "notes": "MS 영업·MS Korea 협업 가능",
    },
}


@dataclass(frozen=True)
class LLMRequest:
    """추상 LLM 요청."""

    system_prompt: str
    user_message: str
    max_tokens: int = 1024
    temperature: float = 0.0  # 결정성 = peer review 통과
    json_schema: dict | None = None  # Structured Outputs


@dataclass(frozen=True)
class LLMResponse:
    """추상 LLM 응답."""

    text: str
    provider_used: ProviderId
    input_tokens: int = 0
    output_tokens: int = 0
    cost_won: float = 0.0
    cached: bool = False
    metadata: dict = field(default_factory=dict)


class LLMProvider(Protocol):
    """프로바이더 인터페이스 (구현체별 분리)."""

    def generate(self, request: LLMRequest) -> LLMResponse: ...


def select_provider(
    segment: DeploymentSegment,
    require_csap: bool = False,
    prefer_domestic: bool = False,
) -> list[ProviderId]:
    """세그먼트별 사용 가능 provider 우선순위 리스트.

    Args:
        segment: 배포 환경
        require_csap: True면 CSAP 인증 필수
        prefer_domestic: True면 도메스틱 LLM 우선

    Returns:
        우선순위 리스트 (1차·2차·3차 폴백)
    """
    candidates = []
    for pid, meta in PROVIDER_META.items():
        if segment in meta["blocked_segments"]:
            continue
        if segment not in meta["allowed_segments"]:
            continue
        if require_csap and not meta["csap_certified"]:
            continue
        candidates.append(pid)

    # 우선순위 정렬
    if segment == "public_govt":
        # 공공 = 도메스틱 우선
        priority = ["naver_hcx", "kt_midm", "bedrock_seoul", "azure_openai_korea", "lg_exaone"]
    elif prefer_domestic:
        priority = ["naver_hcx", "kt_midm", "lg_exaone", "bedrock_seoul", "azure_openai_korea"]
    else:
        # 민간·개인 = Anthropic 직접 (가장 저렴)
        priority = [
            "anthropic_direct",
            "bedrock_seoul",
            "azure_openai_korea",
            "naver_hcx",
            "lg_exaone",
        ]

    return [p for p in priority if p in candidates]


def can_deploy_to(segment: DeploymentSegment) -> dict:
    """배포 가능 여부 + 권장 provider."""
    public_provs = select_provider(segment, require_csap=True)
    return {
        "segment": segment,
        "csap_required": segment == "public_govt",
        "providers_available": public_provs,
        "primary_recommendation": public_provs[0] if public_provs else None,
        "fallback_chain": public_provs[1:],
        "ready": len(public_provs) > 0,
    }


def estimate_segment_cost_won(
    segment: DeploymentSegment,
    requests_per_month: int,
    avg_tokens_per_req: int = 700,
) -> dict:
    """세그먼트별 월간 비용 추정 (영업 자료)."""
    # 권당 평균 토큰 (input 500 + output 200) × ₩0.7/1K (Haiku 정도)
    base_cost = requests_per_month * avg_tokens_per_req * 0.7 / 1000
    providers = select_provider(segment, require_csap=(segment == "public_govt"))

    cost_estimates = {}
    for pid in providers:
        meta = PROVIDER_META[pid]
        if pid == "anthropic_direct":
            cost_estimates[pid] = int(base_cost)  # baseline
        elif pid == "bedrock_seoul":
            cost_estimates[pid] = int(base_cost * 1.25)  # 20~30% premium
        elif pid in ("naver_hcx", "kt_midm"):
            cost_estimates[pid] = int(base_cost * 1.1)  # domestic 정합
        elif pid == "lg_exaone":
            cost_estimates[pid] = 0  # self-host
        else:
            cost_estimates[pid] = int(base_cost * 1.15)
        cost_estimates[pid] = {
            "monthly_won": cost_estimates[pid],
            "csap": meta["csap_certified"],
            "domestic": meta["korean_data_residency"],
        }

    return {
        "segment": segment,
        "requests_per_month": requests_per_month,
        "by_provider": cost_estimates,
    }


__all__ = [
    "PROVIDER_META",
    "DeploymentSegment",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "ProviderId",
    "can_deploy_to",
    "estimate_segment_cost_won",
    "select_provider",
]
