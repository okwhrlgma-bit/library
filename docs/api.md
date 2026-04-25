# kormarc-auto REST API

베이스 URL: `http://localhost:8000` (로컬) 또는 `https://*.trycloudflare.com` (모바일 터널)
인증: 모든 엔드포인트(`/healthz`, `/pricing` 제외)에 `X-API-Key` 헤더 필수

---

## 인증·키 발급 (개발 모드)

`.env`에 다음 추가:
```env
KORMARC_USER_KEYS=key_for_libA_xxxx,key_for_libB_yyyy
KORMARC_ADMIN_KEYS=admin_zzzz
```

키가 미등록이면 자동 발급(`KORMARC_USER_KEYS` 미설정 시 모든 8자 이상 키 통과 — 개발용).
운영에서는 화이트리스트 모드로 동작.

---

## 엔드포인트

### `GET /healthz`

응답:
```json
{"ok": true, "version": "0.1.0", "service": "kormarc-auto"}
```

### `GET /pricing`

응답:
```json
{
  "price_per_record_krw": 100,
  "free_quota_default": 50,
  "payment_url": "https://...",
  "currency": "KRW",
  "notes": "권당 과금. 신규 키 50건 무료 체험."
}
```

### `GET /usage`

헤더: `X-API-Key`
응답:
```json
{
  "key_hash": "abcd1234...",
  "free_quota": 50,
  "used": 12,
  "remaining": 38,
  "price_per_record_krw": 100,
  "payment_url": null
}
```

### `POST /isbn`

요청:
```json
{"isbn": "9788936434120", "agency": "OURLIB"}
```

응답: `KormarcResponse` (메타·KDC 후보·주제명·.mrc base64·사용량)

### `POST /search`

요청:
```json
{"query": "한강 작별하지 않는다", "limit": 10}
```

응답: 후보 리스트 (ISBN dedup, 신뢰도 정렬)

### `POST /photo`

multipart 폼:
- `files`: 이미지 1~3장
- `agency`: "OURLIB"

응답: `KormarcResponse`

### `POST /validate`

요청:
```json
{"mrc_base64": "..."}
```

응답: 레코드별 검증 오류 리스트

---

## 에러 코드

| HTTP | 의미 |
|---|---|
| 401 | X-API-Key 누락/짧음 |
| 403 | 키 미등록 (화이트리스트 모드) |
| 402 | 무료 한도 초과 (응답에 `payment_url`) |
| 404 | ISBN 미조회 / Vision 추출 실패 |
| 502 | 외부 API 호출 실패 |

---

## 호출 예시 (curl)

```bash
# 무료 키로 ISBN 변환
curl -X POST http://localhost:8000/isbn \
  -H "X-API-Key: my_key_at_least_8_chars" \
  -H "Content-Type: application/json" \
  -d '{"isbn":"9788936434120"}'

# 검색
curl -X POST http://localhost:8000/search \
  -H "X-API-Key: my_key_at_least_8_chars" \
  -H "Content-Type: application/json" \
  -d '{"query":"한강 작별","limit":5}'

# 사진 (multipart)
curl -X POST http://localhost:8000/photo \
  -H "X-API-Key: my_key_at_least_8_chars" \
  -F "files=@cover.jpg" \
  -F "files=@copyright.jpg" \
  -F "agency=OURLIB"
```

---

## 클라이언트 호환성

- 모든 응답: JSON
- `.mrc`는 base64 인코딩 (디코딩 후 KOLAS 반입 폴더에 저장)
- CORS: 기본 `*` (운영은 도메인 화이트리스트로 좁힐 것 — `KORMARC_CORS_ORIGINS`)
