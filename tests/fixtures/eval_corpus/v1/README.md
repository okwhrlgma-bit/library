# kormarc-eval-corpus-v1

> Part 92 §A.5 권고: "kormarc-eval-corpus-v1·1,000건·문서화 methodology"
> v1.0 빌드 (2026-05-03): 3383 레코드·자관 PILOT 1관 source

## 빌드 방법
```
python scripts/build_eval_corpus_v1.py
```

## 보안 (PIPA·tenant_isolation)
- 자관 식별자 0건 (045 prefix·9XX 모두 EVAL-{hash})
- ISBN = SHA-256 해시 (역산 불가)
- 출판물 메타 (245·100·6XX) = 공개 정보·그대로

## 사용
- regression baseline (다음 측정 회귀 검증)
- peer review·diligence
- KOSIM/CCQ 학술 발표 표본

## v0.7 공개 계획 (Part 92 §A.5)
- 1,000건 stratified sampling (장르·도서관 유형)
- NL Korea + KOLIS-NET·published methodology
- 본 v1.0 = 내부 baseline·v0.7 = 외부 공개

## 통계
- 레코드 = 3383
- source 파일 = 174
- 고유 필드 태그 = 37
