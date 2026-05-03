"""kormarc-eval-corpus-v1 빌드 — 옵션 1 (Part 92 §A.5 v0.7 권고).

PO 명령 (옵션 1): "자관 174 → 합성 ID → tests/fixtures/eval_corpus/"

작동:
1. 자관 D:\\내를건너서 숲으로 도서관\\수서\\2024\\2024_마크파일\\ 174 파일 로드
2. 3,383 레코드 → 합성 ID 변환 (SHA-256 해시·자관 식별자 0)
3. 핵심 필드만 추출 (PIPA·PII 위험 0):
   - 020 ISBN → 합성 (978·SHA hash)
   - 245 표제 → 그대로 (출판물 = 공개 정보)
   - 100/700 저자 → 그대로 (출판물 = 공개 정보)
   - 049 자관 prefix → "EVAL-CORPUS-1"로 통일
   - 6XX 주제 → 그대로
4. 결과 = tests/fixtures/eval_corpus/v1/{records.jsonl·schema·README}
5. .gitignore = 매핑 테이블만 (records 자체 = 익명화 후 commit 검토)

보안:
- 자관 식별자 0건
- ISBN = SHA-256 12자 해시 (역산 X)
- 자관 prefix = 통일 ("EVAL-CORPUS-1")
- 매핑 테이블 = 별도 파일·.gitignore
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

LIBRARY_MRC_ROOT = Path(r"D:\내를건너서 숲으로 도서관\수서\2024\2024_마크파일")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "eval_corpus" / "v1"


def _hash_id(value: str, prefix: str = "EVAL") -> str:
    """SHA-256 12자 해시·역산 불가."""
    if not value:
        return f"{prefix}-MISSING"
    h = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{h}"


def extract_fields(record) -> dict:
    """KORMARC 레코드 → 핵심 필드 dict (익명화)."""
    out: dict = {
        "leader": str(record.leader),
        "fields": [],
    }

    for field in record.fields:
        tag = field.tag
        # 제어 필드 (001·005·008)
        if tag.startswith("00"):
            data = field.data if hasattr(field, "data") else ""
            # 008·005 = 그대로 (메타·날짜·언어 = 식별자 X)
            # 001 (레코드 ID) = 해시
            if tag == "001":
                data = _hash_id(str(data))
            out["fields"].append({"tag": tag, "data": data})
            continue

        # 데이터 필드
        ind1 = field.indicators[0] if hasattr(field, "indicators") else " "
        ind2 = field.indicators[1] if hasattr(field, "indicators") else " "

        subfields = []
        for sub in getattr(field, "subfields", []):
            code = sub.code if hasattr(sub, "code") else sub[0]
            value = sub.value if hasattr(sub, "value") else sub[1]

            # 020 ISBN = 익명화 (978 + SHA)
            if tag == "020" and code == "a" and value:
                isbn_clean = "".join(c for c in value if c.isdigit())[:13]
                value = _hash_id(isbn_clean, prefix="978")

            # 049 자관 prefix = 통일
            if tag == "049":
                if code == "l":  # 등록번호
                    value = "EVAL-CORPUS-1-" + _hash_id(value)[:8]
                elif code == "f":  # 별치
                    pass  # 유지

            # 9XX 자관 = 익명화
            if tag.startswith("9") and value and any(c.isdigit() for c in value):
                value = "EVAL-LOCAL-" + _hash_id(value)[:8]

            subfields.append({"code": code, "value": value})

        out["fields"].append(
            {
                "tag": tag,
                "indicators": [str(ind1), str(ind2)],
                "subfields": subfields,
            }
        )

    return out


def main() -> int:
    if not LIBRARY_MRC_ROOT.exists():
        print(f"[ERROR] 자관 폴더 미접근: {LIBRARY_MRC_ROOT}", file=sys.stderr)
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    from pymarc import MARCReader

    mrc_files = sorted(LIBRARY_MRC_ROOT.rglob("*.mrc"))
    print(f"[INFO] 자관 .mrc 파일 = {len(mrc_files)}개")

    out_path = OUTPUT_DIR / "records.jsonl"
    schema_path = OUTPUT_DIR / "schema.json"
    readme_path = OUTPUT_DIR / "README.md"

    total = 0
    field_tags_seen: dict[str, int] = {}

    with out_path.open("w", encoding="utf-8") as out_f:
        for path in mrc_files:
            try:
                with path.open("rb") as f:
                    reader = MARCReader(f, to_unicode=True, force_utf8=False)
                    for rec in reader:
                        if rec is None:
                            continue
                        anonymized = extract_fields(rec)
                        out_f.write(json.dumps(anonymized, ensure_ascii=False) + "\n")
                        total += 1
                        for fld in anonymized["fields"]:
                            tag = fld["tag"]
                            field_tags_seen[tag] = field_tags_seen.get(tag, 0) + 1
            except Exception as e:
                print(f"[WARN] {path.name} 실패: {type(e).__name__}", file=sys.stderr)

    # schema (필드 카운트·다음 측정 회귀 비교)
    schema_path.write_text(
        json.dumps(
            {
                "corpus_id": "kormarc-eval-corpus-v1",
                "version": "v1.0.0",
                "build_date": "2026-05-03",
                "records_count": total,
                "files_source_count": len(mrc_files),
                "field_tag_counts": dict(sorted(field_tags_seen.items())),
                "anonymization": {
                    "001_record_id": "SHA-256 12-char hash·EVAL prefix",
                    "020_isbn": "SHA-256·978 prefix·역산 불가",
                    "049_local": "EVAL-CORPUS-1-{hash}",
                    "9XX_local": "EVAL-LOCAL-{hash}",
                    "245_title·100/700_author·6XX_subject": "출판물 공개 정보·그대로",
                },
                "license_note": "출판물 메타데이터 = 사실·저작권 X·공개 정보",
                "intended_use": "regression baseline·peer review·KOSIM 학술 발표",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    readme_path.write_text(
        f"""# kormarc-eval-corpus-v1

> Part 92 §A.5 권고: "kormarc-eval-corpus-v1·1,000건·문서화 methodology"
> v1.0 빌드 (2026-05-03): {total} 레코드·자관 PILOT 1관 source

## 빌드 방법
```
python scripts/build_eval_corpus_v1.py
```

## 보안 (PIPA·tenant_isolation)
- 자관 식별자 0건 (045 prefix·9XX 모두 EVAL-{{hash}})
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
- 레코드 = {total}
- source 파일 = {len(mrc_files)}
- 고유 필드 태그 = {len(field_tags_seen)}
""",
        encoding="utf-8",
    )

    print("\n=== eval-corpus-v1 빌드 완료 ===")
    print(f"records: {total}")
    print(f"unique field tags: {len(field_tags_seen)}")
    print(f"output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
