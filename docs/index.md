# 문서 인덱스 — kormarc-auto

> 모든 docs 한 번에 보기. 검색·탐색용.
> 총 30+ 문서, 26 모듈, 25+ 커밋.

---

## 1. 시작·운영

| 문서 | 내용 |
|---|---|
| [README.md](../README.md) | 5분 더블클릭 시작 |
| [CLAUDE.md](../CLAUDE.md) | 프로젝트 헌법 (13장) |
| [quickstart-librarian.md](quickstart-librarian.md) | 사서 5분 가이드 |
| [troubleshooting.md](troubleshooting.md) | 25+ 케이스 트러블슈팅 |
| [api.md](api.md) | REST API 사용법 |
| [mobile-tunnel.md](mobile-tunnel.md) | Cloudflare 모바일 접속 |
| [deploy.md](deploy.md) | Fly/Render/VPS 배포 |

## 2. 사업·전략

| 문서 | 내용 |
|---|---|
| [pricing.md](pricing.md) | 가격 정책 (작은도서관 3만원 등) |
| [sales-roadmap.md](sales-roadmap.md) | 캐시카우 도달 3단계 |
| [business-checklist.md](business-checklist.md) | 사업 운영 8영역 |
| [outreach.md](outreach.md) | 사서 모집 메시지 5종 |
| [terms-beta.md](terms-beta.md) | 베타 약관 |
| [global-strategy.md](global-strategy.md) | 한·일·영어권 4단계 |
| [government-grants.md](government-grants.md) | K-Startup 공모 + 인용 문단 |
| [competitor-analysis.md](competitor-analysis.md) | 경쟁사 14개 비교 |
| [research-roadmap.md](research-roadmap.md) | 1년 조사 청사진 8영역 |
| [regulatory-landscape.md](regulatory-landscape.md) | 12 법령 |
| [technology-trends.md](technology-trends.md) | 기술 트렌드 12분야 |
| [legal-references.md](legal-references.md) | 도서관 법률 7종 |
| [code-review.md](code-review.md) | 자기 비판 검토 |

## 3. 사서·도서관 도메인

| 문서 | 내용 |
|---|---|
| [librarian-domain.md](librarian-domain.md) | 사서 업무 종합 |
| [librarian-comprehensive.md](librarian-comprehensive.md) | KLA 윤리·자격·SNS·시간 분포 |
| [librarian-tools-detail.md](librarian-tools-detail.md) | KOLAS·DLS·KOLASYS·LAS 상세 |
| [librarian-tools-match.md](librarian-tools-match.md) | 사서 도구 21종 매칭 |
| [librarian-jargon.md](librarian-jargon.md) | 사서 실무 용어 9분야 |
| [librarian-interview-questions.md](librarian-interview-questions.md) | 베타 인터뷰 30개 |
| [librarian-deep-research.md](librarian-deep-research.md) | PO 자료 + Aycock 통합 |
| [library-science-references.md](library-science-references.md) | 문헌정보학·서지학·분류학·목록학 |
| [library-statistics.md](library-statistics.md) | 한국 도서관 통계 |
| [library-vendor-ecosystem.md](library-vendor-ecosystem.md) | 솔루션 업체 6분류 |
| [library-services-integration.md](library-services-integration.md) | 책바다·책나래·책이음·알파스 |

## 4. KORMARC·표준

| 문서 | 내용 |
|---|---|
| [marc-fields-guide.md](marc-fields-guide.md) | 17필드 사서 가이드 |
| [kormarc-spec-summary.md](kormarc-spec-summary.md) | NL Korea 매뉴얼 요약 |
| [kormarc-comprehensive-spec.md](kormarc-comprehensive-spec.md) | 자료 30+ 매핑 매트릭스 |
| [kolas-modules-index.md](kolas-modules-index.md) | KOLAS III 1,737 파일 |
| [kolas-integration-guide.md](kolas-integration-guide.md) | KOLAS 실 연동 가이드 |
| [github-libraries.md](github-libraries.md) | GitHub 한국 first-mover |

## 5. 데이터·검증

| 문서 | 내용 |
|---|---|
| [test_results.md](test_results.md) | 테스트·정확도 누적 |
| [research-references.md](research-references.md) | 학술 인용 자료 (국회도서관 보고서·Aycock) |
| [real-library-data-analysis.md](real-library-data-analysis.md) | 실 도서관 1개월 236권 분석 + ROI 19배 |
| [real-library-d-drive-index.md](real-library-d-drive-index.md) | D:\ 도서관 자료 87 항목 |
| [po-real-library-materials.md](po-real-library-materials.md) | 자료 폴더 30+ 종 매칭 |
| [known-issues.md](known-issues.md) | 알려진 이슈 |
| [spec.md](spec.md) | 마스터 명세서 |

---

## 핵심 모듈 인덱스 (`src/kormarc_auto/`)

### KORMARC 빌드
- `kormarc/builder.py` — 통합서지용 (단행본·관제·090·041·246·250·500·504·856)
- `kormarc/validator.py` — 기본 검증
- `kormarc/kolas_validator.py` — KOLAS 반입 사전 엄격 검증
- `kormarc/material_type.py` — LDR 06·08 자료유형 분기
- `kormarc/serial.py` — 연속간행물 (022·310·362·780/785)
- `kormarc/non_book.py` — 비도서·전자자료 (007·502·538·856)
- `kormarc/rare_book.py` — 고서 (한자·간지·葉)
- `kormarc/authority_data.py` — 100/110/111 + 700/710/711 전거
- `kormarc/mapping.py` — 발행국부호 등

### 변환·출력
- `conversion/marc21.py` — KORMARC ↔ MARC21
- `output/kolas_writer.py` — KOLAS .mrc
- `output/dls_writer.py` — 독서로DLS
- `output/marcxml_writer.py` — MARCXML
- `output/csv_writer.py` — CSV (KOLASYS-NET)
- `output/labels.py` — A4 라벨 PDF (Avery)

### AI·외부
- `_anthropic_client.py` — BYOK + 캐시 + 재시도
- `vision/claude_vision.py` — 2단계 (Haiku→Sonnet)
- `vision/photo_pipeline.py` — 바코드→OCR→Vision
- `vision/ocr.py` — EasyOCR (AI 0원)
- `vision/barcode.py` — pyzbar
- `api/aggregator.py` — 다중 소스 폴백
- `api/nl_korea.py` / `aladin.py` / `kakao.py` / `data4library.py`
- `api/kolisnet_compare.py` — 다른 도서관 분류 비교
- `api/search.py` — 키워드 통합 검색

### 분류·주제
- `classification/kdc_classifier.py` — KDC AI 후보
- `classification/subject_recommender.py` — NLSH AI
- `classification/scheme.py` — KDC/DDC/NDC/LCC/UDC 추상
- `classification/nlsh_vocabulary.py` — NLSH 9 카테고리

### 사서 보조
- `librarian_helpers/call_number.py` — 049 청구기호 + 이재철 근사
- `librarian_helpers/normalize.py` — 입력 패턴 자동 변환
- `librarian_helpers/publisher_db.py` — ISBN 출판사 캐시
- `librarian_helpers/kdc_tree.py` — KDC 6판 트리
- `librarian_helpers/subfield_input.py` — $a→▾a 변환
- `librarian_helpers/romanization.py` — 한글→RR/ALA-LC
- `librarian_helpers/loss_damage.py` — 583 처리 (분실·파손 등 7종)

### 자관·검색
- `inventory/library_db.py` — 자관 .mrc 인덱스
- `inventory/importer.py` — 외부 .mrc/MARCXML import

### 서버·UI
- `server/app.py` — FastAPI (8 엔드포인트)
- `server/auth.py` / `usage.py` / `signup.py` / `feedback.py` / `admin.py`
- `server/schemas.py`
- `ui/streamlit_app.py` — 모바일 반응형 4탭

### 한자·기타
- `vernacular/field_880.py` — 880 자동 페어
- `vernacular/hanja_converter.py` — 한자→한글
- `cli.py` — argparse (8 서브명령)
- `constants.py` / `logging_config.py`

---

## 스크립트

- `scripts/build_golden_dataset.py` — NL Korea로 정답 수집
- `scripts/accuracy_compare.py` — 정확도 회귀
- `scripts/accuracy_check.py` — 5건 검증
- `scripts/analyze_real_acquisitions.py` — 신착 .xlsx 분석
- `scripts/backup_logs.py` — 운영 백업

---

## 슬래시 명령 (`.claude/commands/`)

`/test` `/lint-fix` `/add-isbn` `/batch-isbns` `/quality-check` `/daily`
`/serve` `/ui` `/search` `/vision-test` `/kdc-test` `/mobile-status` `/golden`

---

## PO 즉시 액션 우선순위 (TOP 5)

1. **`.env`에 `NL_CERT_KEY`·`ANTHROPIC_API_KEY` 채우기**
2. **`start-all.bat` 더블클릭** → http://localhost:8501
3. **`scripts/build_golden_dataset.py` 실행** (정답 데이터 50건 자동)
4. **사서 5명 베타 카카오톡** (`docs/outreach.md`)
5. **충남 공공데이터·AI 경진대회 신청** (마감 5/26, `docs/government-grants.md`)
