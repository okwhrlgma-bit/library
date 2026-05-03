# BIBFRAME 2.0 / LOD 영업 메일 — 대학·디지털 컬렉션

> **대상**: KSLA 사립대학·국공립대학·NLK 디지털 컬렉션·도서관학 학계
> **단가**: 일반 공공 = 월 15만원 / 대규모 = 월 30만원 (법인·시도교육청 카드)
> **단일 진실**: KORMARC ↔ BIBFRAME 2.0 ↔ MODS XML 양방향 변환 정합

---

## 1. BIBFRAME 2.0 한눈

- LC (Library of Congress) 차세대 표준 (2016 GA·2024 v2.5)
- Work·Instance·Item 3 추상 모델
- LOD (Linked Open Data) RDF 기반
- 한국 NLK·KSLA 일부 도입 검토 중 (2026)

우리 정합:
- `src/kormarc_auto/conversion/marc21.py` — MARC21 호환 (BIBFRAME 변환 기반)
- `src/kormarc_auto/kormarc/authority_data.py` — 100/110/111 전거 (Work 매핑)
- `docs/research/part2-kormarc-implementation.md` §2 — BIBFRAME 2.0 변환 의사코드

---

## 2. 영업 메일 — KSLA 사립대학·국공립대학

**제목**: "사립대학 도서관 — KORMARC ↔ BIBFRAME 2.0 LOD 자동 변환 (월 15~30만원)"

```
안녕하세요. 사서 출신 1인 개발자 [PO 이름]입니다.

KSLA 사립대학·국공립대학 도서관에 BIBFRAME 2.0 LOD 변환 자동화 SaaS
제안드립니다. KORMARC ↔ MARC21 ↔ BIBFRAME ↔ MODS XML 양방향 정합.

[정량]
- 자관 .mrc 174 파일·3,383 레코드 → 99.82% 정합 (한국 KOLAS 실무)
- 학위논문 502·전자책 856·연속간행물 022 ISSN 모두 자동
- BIBFRAME 2.0 (Work·Instance·Item) 변환 + RDF/Turtle 출력
- MODS XML 5 자료유형 (NLK 온라인자료과 표준)

[제안]
- 월 15만원 / 5,000건 (일반 공공) 또는 월 30만원 / 무제한 (대규모·로펌·대학병원)
- 첫 50건 무료
- 시도교육청 또는 법인 카드 결제
- KSLA 학술대회 발표·기고 가능

[대학·학술 차별화]
- 학위논문 502 자동 (석·박사·학과·지도교수)
- 전자책 856 + 538 매체 자동
- 연속간행물 022 ISSN + 310 발행빈도 + 362 권차
- 고서·한자 880 페어 (NLK 「로마자 표기 지침(2021)」 정합)
- BIBFRAME LOD 변환 (Linked Open Data·시맨틱 웹)

[5월 KLA 5.31 발표 후속]
- 6월 KSLA 학술대회 강의·기고 제안
- 7월 사서교육원 강의 (60분 또는 30분)

contact@kormarc-auto.example
```

---

## 3. NLK 디지털 컬렉션 위탁 운영 도서관

**제목**: "NLK 디지털 컬렉션 — MODS XML 5 자료유형 자동 변환"

```
안녕하세요. [PO 이름]입니다.

NLK 온라인자료과 MODS XML 5 자료유형 (멀티미디어·오디오북·전자저널·
전자책·학위논문) 표준 정합 SaaS 제안드립니다.

[정량]
- KORMARC ↔ MODS XML 양방향 자동
- BIBFRAME 2.0 (Work·Instance·Item·LOD)
- 자관 .mrc 99.82% 정합

[제안]
- 월 30만원 / 무제한 (대규모 디지털 컬렉션)
- 첫 50건 무료

contact@kormarc-auto.example
```

---

## 4. 학회 기고·강의 제안 (KSLA·OAK Korea)

- KSLA 2026 학술대회 (10~11월·연 1회)
- OAK Korea 학술지 (분기·도서관학 연구)
- 도서관학 교수·학회 회원 직접 인용 → 학술 신뢰 ↑

---

## 5. 답장률 목표

| 채널 | 발송 | 회신 목표 | PILOT |
|---|---:|---:|---:|
| 사립대학 (KSLA) | 30통 | 4건 (13%) | 1관 |
| 국공립대학 | 20통 | 2건 (10%) | 0~1관 |
| NLK 디지털 | 5통 | 1건 (20%) | 0~1관 |
| **합계** | **55통** | **7건** | **1~3관** |

---

## Sources

- LC BIBFRAME 2.0 (loc.gov/bibframe)
- KSLA (kacls.or.kr)
- NLK 온라인자료과 MODS XML 표준
- `src/kormarc_auto/conversion/marc21.py`
- `docs/research/part2-kormarc-implementation.md` §2
