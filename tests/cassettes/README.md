# tests/cassettes — VCR.py 녹화 fixtures (Part 92·94 정합)

> Part 92 §A.1: pytest-recording (vcrpy) YAML cassettes = 2024-2026 표준
> 외부 API 호출 (Anthropic·SEOJI·data4library·알라딘·Kakao·PubMed) 모두 녹화·재생

---

## 작동

1. **첫 녹화** = 실 API 키로 1회만:
```bash
pytest tests/test_aggregator_real.py --record-mode=once
```

2. **commit cassettes** = git에 `*.yaml` 포함

3. **재생 (CI·로컬)**:
```bash
pytest --block-network  # 네트워크 차단·cassettes만 사용
```

4. **갱신 시** = `--record-mode=rewrite` 또는 cassette 파일 삭제 후 재녹화

---

## 보안 (PIPA·키 보호)

`tests/conftest.py` vcr_config:
```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-api-key", "REDACTED"), ("authorization", "REDACTED")],
        "filter_query_parameters": [
            ("authKey", "REDACTED"),
            ("api_key", "REDACTED"),
            ("cert_key", "REDACTED"),
            ("ttbkey", "REDACTED"),
        ],
        "decode_compressed_response": True,
        "record_mode": "once",
    }
```

→ 모든 키 자동 마스킹·git push 안전.

---

## 디렉토리 구조 (예정)

```
tests/cassettes/
├── README.md (본 파일)
├── seoji/
│   ├── isbn_9788937437076.yaml      # 어린왕자 SEOJI 응답
│   └── isbn_no_match.yaml
├── data4library/
│   ├── kdc_lookup.yaml
│   └── popular_books.yaml
├── kakao/
│   └── search_korean_title.yaml
├── pubmed/
│   ├── esearch_diabetes.yaml
│   └── efetch_pmid_12345.yaml
└── anthropic/
    ├── kdc_recommendation.yaml
    └── vision_book_cover.yaml
```

---

## 정합

- VCR 8.0 (vcrpy)·pytest-recording (kiwicom)
- Anthropic Python SDK base_url= override (Prism localhost:4010)
- Stripe sentinel ISBN 패턴 (4242 정합·`demo/offline_mock_server.py` SAMPLE_BOOKS)
- CI gate = `--block-network` 통과 = 릴리스 게이트

상세 = `docs/research/part92-integrated-dossier-2026-05.md` §A.1.
