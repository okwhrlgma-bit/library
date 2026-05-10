---
name: generate-kormarc
description: ISBN → 한국 도서관 KORMARC (KS X 6006-0:2023.12) .mrc 자동 생성·9 자료유형 정합·자관 174 회귀 100%
license: Apache-2.0
version: 0.7.1
language: ko
tags: [korean, library, kormarc, cataloging]
---

# generate-kormarc Skill

> 한국 도서관 KORMARC 마크 자동 생성·사서 시간 권당 8분 → 2분.

## Inputs

- `isbn` (string·필수): ISBN-13
- `source` (enum·옵션): `nl_korea` | `aladin` | `byok` (기본 `nl_korea`)
- `material_type` (enum·옵션): book·serial·non_book·rare·ebook·ejournal·audiobook·multimedia·thesis (자동 감지)

## Outputs

- `mrc_text` (string): KORMARC 형식 (UTF-8·MARC21 호환)
- `confidence` (enum): `확실` | `검토 필요` | `불확실` (헌법 §11·raw % X)
- `source_map` (dict): 필드별 출처 추적
- `audit_log` (list): 헌법 §10 정합·588 provenance stamp

## Constitution

- §3 HARD RULES (timeout 10·UTF-8·"100% 자동" X)
- §11 신뢰도 카테고리만 (raw % UI 금지)
- §14 자관 데이터 = 사용자 컴퓨터 (offline 우선)

## Benchmark

- MarcEdit (26년·무료·미국): KORMARC 미지원
- 채움 K·CLOUD (한국·구축형): 5~15만/월
- 우리 = 즉시 사용·자관 174 회귀 100%·MIT 라이선스

## Anthropic Skills Marketplace

- 호스팅 후보: Agent37·Composio·VoltAgent
- 가격 가설: $0.5/실행 (BYOK 옵션)·Anthropic 사용자 1억+ 잠재
- 한국 사서 niche + 글로벌 한국학 도서관 시장 (북미·일본·유럽)

## 사용 예시

```python
from kormarc_auto import generate_kormarc

result = generate_kormarc(
    isbn="9788937462788",
    source="nl_korea",
)
print(result.mrc_text)  # KORMARC .mrc
print(result.confidence)  # "확실" | "검토 필요" | "불확실"
```

## 정합

- ADR 0053·0058·0059·I-003 (Skills Marketplace GO)
- 30 apps #1·페인 = 한국 사서 KORMARC 작성 시간
- 자관 PILOT 1관 (174 파일·3,383 records) round-trip 100%
