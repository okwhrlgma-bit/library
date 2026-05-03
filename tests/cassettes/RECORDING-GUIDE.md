# VCR 실 녹화 가이드 (옵션 3·PO .env 작성 후)

> tests/conftest_vcr.py 활성·키 마스킹 완비
> 실 녹화 = PO `.env` 4 키 입력 후 1회 실행

## Step 1: PO .env 작성 (5분)

`C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto\.env`:
```
DATA4LIBRARY_AUTH_KEY=64b83252ee4c195e667c6cca0ba3226f93a10a1c487f254a93134f423ca8cde3
KAKAO_API_KEY=05fdd9c0f5848cffc555f574d9ebfcc7
PUBMED_API_KEY=20b2e7e788bdacc11e35773592bbdb3b8009
```

## Step 2: 실 녹화 (3개 API·3분)

```bash
# data4library cassette
pytest tests/test_data4library.py --vcr-record=once -v

# Kakao cassette
pytest tests/test_kakao.py --vcr-record=once -v

# PubMed cassette
pytest tests/test_pubmed.py --vcr-record=once -v
```

## Step 3: cassette 검증 (키 마스킹 확인)

```bash
grep -r "64b83252\|05fdd9c0\|20b2e7e7" tests/cassettes/  # 0건이어야 함
grep -r "REDACTED" tests/cassettes/                      # 마스킹 정합
```

## Step 4: --block-network 게이트

```bash
pytest --block-network -q  # 모든 외부 호출 차단·cassette만 사용·CI 게이트
```

## Step 5: commit

```bash
git add tests/cassettes/*.yaml
git commit -m "test(cassettes): record data4library + kakao + pubmed (마스킹 정합)"
```

---

## 보류 (NL_CERT_KEY 발급 후)

```bash
pytest tests/test_nl_korea.py --vcr-record=once -v
```

---

## 자동화 (cron·매일)

`.github/workflows/vcr-refresh.yml` (월 1회):
```yaml
- run: pytest --vcr-record=new_episodes
- run: git diff --check tests/cassettes/  # 자동 PR
```
