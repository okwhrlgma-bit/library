"""kormarc-auto FastAPI 서버.

엔드포인트:
- POST /isbn        ISBN → KORMARC + .mrc base64
- POST /search      키워드 → 후보 리스트
- POST /photo       이미지 1~3장 → KORMARC + .mrc base64
- POST /validate    .mrc base64 → 검증 결과
- GET  /usage       현재 키 사용량 조회
- GET  /healthz     상태 확인
- GET  /pricing     가격 안내

모든 엔드포인트(/healthz, /pricing 제외): X-API-Key 필수.
"""

from __future__ import annotations

import base64
import contextlib
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kormarc_auto import __version__
from kormarc_auto.api.aggregator import aggregate_by_isbn
from kormarc_auto.api.search import search_by_query
from kormarc_auto.classification.kdc_classifier import recommend_kdc
from kormarc_auto.classification.subject_recommender import recommend_subjects
from kormarc_auto.constants import (
    PRICE_PER_RECORD_KRW,
    get_payment_info_url,
)
from kormarc_auto.kormarc.builder import build_kormarc_record
from kormarc_auto.kormarc.validator import validate_record
from kormarc_auto.logging_config import setup_logging
from kormarc_auto.output.kolas_writer import write_kolas_mrc
from kormarc_auto.server.auth import check_quota, get_usage_status, require_api_key
from kormarc_auto.server.schemas import (
    HealthResponse,
    IsbnRequest,
    KormarcResponse,
    SearchRequest,
    SearchResponse,
    SignupRequest,
    SignupResponse,
    UsageResponse,
    ValidateRequest,
    ValidationResponse,
)
from kormarc_auto.server.signup import SignupError, issue_free_trial_key
from kormarc_auto.server.usage import consume
from kormarc_auto.vernacular.field_880 import add_880_pairs

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """FastAPI 앱 팩토리."""
    from dotenv import load_dotenv

    load_dotenv()
    setup_logging()

    app = FastAPI(
        title="kormarc-auto API",
        description="한국 도서관용 KORMARC 자동 생성 REST API",
        version=__version__,
    )

    # CORS — 외부에서 호출 가능. 운영에서는 도메인 화이트리스트 권장.
    allowed_origins = os.getenv("KORMARC_CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.get("/healthz", response_model=HealthResponse, tags=["meta"])
    def healthz() -> HealthResponse:
        return HealthResponse(ok=True, version=__version__)

    @app.get("/pricing", tags=["meta"])
    def pricing() -> JSONResponse:
        return JSONResponse(
            {
                "price_per_record_krw": PRICE_PER_RECORD_KRW,
                "free_quota_default": 50,
                "payment_url": get_payment_info_url(),
                "currency": "KRW",
                "notes": "권당 과금. 신규 키 50건 무료 체험. 정식 결제는 곧 출시 예정.",
            }
        )

    @app.post("/signup", response_model=SignupResponse, tags=["meta"])
    def signup(body: SignupRequest, request: Request) -> SignupResponse:
        """무료 체험 키 자동 발급 (인증 없음).

        보호:
        - 이메일 형식 검증
        - 같은 이메일/IP 분당 5회 한도
        """
        client_ip = request.client.host if request.client else None
        try:
            result = issue_free_trial_key(body.email, body.library_name, client_ip=client_ip)
        except SignupError as e:
            raise HTTPException(status_code=429, detail=str(e)) from e
        return SignupResponse(**result)

    @app.post("/romanize", tags=["tools"])
    def romanize_endpoint(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """한글 → 로마자 (RR + ALA-LC)."""
        from kormarc_auto.librarian_helpers.romanization import (
            hangul_to_alalc,
            hangul_to_rr,
        )

        _ = api_key
        text = str(body.get("text", "")).strip()
        if not text:
            raise HTTPException(status_code=400, detail="text 필드 필요")
        return {"input": text, "rr": hangul_to_rr(text), "alalc": hangul_to_alalc(text)}

    @app.post("/inventory/search", tags=["tools"])
    def inventory_search(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """자관 .mrc 누적 인덱스 검색."""
        from kormarc_auto.inventory.library_db import search_local

        _ = api_key
        results = search_local(
            query=str(body.get("query", "")),
            kdc_prefix=body.get("kdc_prefix"),
            limit=int(body.get("limit", 50)),
        )
        return {"count": len(results), "results": results}

    @app.get("/inventory/stats", tags=["tools"])
    def inventory_stats(api_key: str = Depends(require_api_key)) -> dict[str, Any]:
        """자관 KDC 분포·연도 통계."""
        from kormarc_auto.inventory.library_db import stats

        _ = api_key
        return stats()

    @app.post("/feedback", tags=["meta"])
    def feedback(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """베타 사서 피드백 수집 — 자유 텍스트 + 별점."""
        from kormarc_auto.server.feedback import save_feedback

        rating = int(body.get("rating", 0))
        comment = str(body.get("comment", "")).strip()[:2000]
        category = str(body.get("category", "")).strip()[:50]
        if not comment and rating == 0:
            raise HTTPException(status_code=400, detail="rating 또는 comment 필수")
        return save_feedback(
            api_key=api_key,
            rating=rating,
            comment=comment,
            category=category,
        )

    @app.get("/admin/stats", tags=["meta"])
    def admin_stats(api_key: str = Depends(require_api_key)) -> dict[str, Any]:
        """관리자 대시보드 — 가입자·사용량·피드백 요약. 관리자 키 필수."""
        from kormarc_auto.server.admin import build_stats
        from kormarc_auto.server.auth import get_admin_keys

        if api_key not in get_admin_keys():
            raise HTTPException(status_code=403, detail="관리자 키만 가능")
        return build_stats()

    @app.get("/usage", response_model=UsageResponse, tags=["meta"])
    def usage(api_key: str = Depends(require_api_key)) -> UsageResponse:
        st = get_usage_status(api_key)
        remaining = st["free_quota"] - st["used"]
        return UsageResponse(
            key_hash=st["key_hash"],
            free_quota=st["free_quota"],
            used=st["used"],
            remaining=remaining,
            price_per_record_krw=PRICE_PER_RECORD_KRW,
            payment_url=get_payment_info_url() if remaining <= 5 else None,
        )

    @app.post("/isbn", response_model=KormarcResponse, tags=["kormarc"])
    def isbn_endpoint(
        body: IsbnRequest,
        api_key: str = Depends(require_api_key),
    ) -> KormarcResponse:
        check_quota(api_key)
        isbn = body.isbn.replace("-", "").strip()

        try:
            book_data = aggregate_by_isbn(isbn)
        except Exception as e:
            consume(api_key, kind="isbn", ok=False, ref=isbn)
            raise HTTPException(status_code=502, detail=f"외부 API 호출 실패: {e}") from e

        if not book_data.get("sources"):
            consume(api_key, kind="isbn", ok=False, ref=isbn)
            raise HTTPException(status_code=404, detail=f"ISBN {isbn}: 모든 소스에서 미조회")

        return _build_response(book_data, isbn=isbn, agency=body.agency, api_key=api_key, kind="isbn")

    @app.post("/search", response_model=SearchResponse, tags=["kormarc"])
    def search_endpoint(
        body: SearchRequest,
        api_key: str = Depends(require_api_key),
    ) -> SearchResponse:
        check_quota(api_key)
        try:
            candidates = search_by_query(body.query, limit=body.limit)
        except Exception as e:
            consume(api_key, kind="search", ok=False, ref=body.query[:30])
            raise HTTPException(status_code=502, detail=f"검색 실패: {e}") from e

        usage_status = consume(api_key, kind="search", ok=bool(candidates), ref=body.query[:30])
        return SearchResponse(
            ok=bool(candidates),
            query=body.query,
            candidates=candidates,
            usage=usage_status,
        )

    @app.post("/photo", response_model=KormarcResponse, tags=["kormarc"])
    async def photo_endpoint(
        files: list[UploadFile] = File(..., description="이미지 1~3장 (표지·판권지·목차)"),  # noqa: B008
        agency: str = Form("OURLIB"),
        api_key: str = Depends(require_api_key),
    ) -> KormarcResponse:
        check_quota(api_key)
        if not files:
            raise HTTPException(status_code=400, detail="이미지 최소 1장 필요")
        if len(files) > 3:
            raise HTTPException(status_code=400, detail="이미지 최대 3장")

        from kormarc_auto.vision.photo_pipeline import photo_to_book_data

        tmp_paths: list[str | Path] = []
        try:
            for upload in files:
                suffix = Path(upload.filename or "image.jpg").suffix or ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(await upload.read())
                    tmp_paths.append(Path(tmp.name))

            try:
                book_data = photo_to_book_data(tmp_paths)
            except Exception as e:
                consume(api_key, kind="photo", ok=False, ref=str(len(tmp_paths)))
                raise HTTPException(status_code=502, detail=f"Vision 실패: {e}") from e

            if book_data.get("vision_only") and not book_data.get("isbn"):
                consume(api_key, kind="photo", ok=False, ref=str(len(tmp_paths)))
                raise HTTPException(status_code=404, detail="ISBN 추출 실패 + Vision 보강 부족")

            isbn = book_data.get("isbn") or "unknown"
            return _build_response(
                book_data,
                isbn=str(isbn),
                agency=agency,
                api_key=api_key,
                kind="photo",
            )
        finally:
            for p in tmp_paths:
                with contextlib.suppress(OSError):
                    p.unlink(missing_ok=True)

    @app.post("/validate", response_model=ValidationResponse, tags=["kormarc"])
    def validate_endpoint(
        body: ValidateRequest,
        api_key: str = Depends(require_api_key),
    ) -> ValidationResponse:
        from pymarc import MARCReader

        try:
            mrc_bytes = base64.b64decode(body.mrc_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"base64 디코딩 실패: {e}") from e

        errors_per_record: list[list[str]] = []
        with io.BytesIO(mrc_bytes) as buf:
            reader = MARCReader(buf, force_utf8=True)
            for record in reader:
                if record is None:
                    errors_per_record.append(["레코드 파싱 실패"])
                    continue
                errors_per_record.append(validate_record(record))

        return ValidationResponse(
            ok=all(not e for e in errors_per_record),
            record_count=len(errors_per_record),
            errors_per_record=errors_per_record,
        )

    return app


def _build_response(
    book_data: dict[str, Any],
    *,
    isbn: str,
    agency: str,
    api_key: str,
    kind: str,
) -> KormarcResponse:
    """공통 KORMARC 빌드·검증·응답 조립."""
    kdc_candidates = recommend_kdc(book_data)
    if kdc_candidates and not book_data.get("kdc"):
        book_data["kdc"] = kdc_candidates[0]["code"]

    record = build_kormarc_record(book_data, cataloging_agency=agency)
    add_880_pairs(record)
    errors = validate_record(record)

    # KOLAS 반입 사전 엄격 검증 (errors는 합치고 warnings는 별도)
    from kormarc_auto.kormarc.kolas_validator import kolas_strict_validate

    strict = kolas_strict_validate(record)
    for warn in strict.get("warnings", []):
        errors.append(f"[KOLAS warn] {warn}")

    subject_candidates = recommend_subjects(book_data)

    out_dir = Path(tempfile.gettempdir()) / "kormarc_responses"
    try:
        out_path = write_kolas_mrc(record, isbn, output_dir=str(out_dir))
        mrc_bytes = out_path.read_bytes()
        mrc_b64 = base64.b64encode(mrc_bytes).decode("ascii")
    except Exception as e:
        logger.warning(".mrc 저장 실패: %s", e)
        mrc_b64 = None
    finally:
        try:
            if "out_path" in locals():
                out_path.unlink(missing_ok=True)
        except OSError:
            pass

    usage_status = consume(api_key, kind=kind, ok=True, ref=isbn)

    return KormarcResponse(
        ok=True,
        isbn=str(book_data.get("isbn") or isbn),
        title=book_data.get("title"),
        author=book_data.get("author"),
        publisher=book_data.get("publisher"),
        publication_year=book_data.get("publication_year"),
        confidence=float(book_data.get("confidence", 0.0)),
        sources=list(book_data.get("sources", [])),
        source_map=dict(book_data.get("source_map", {})),
        attributions=list(book_data.get("attributions", [])),
        kdc_candidates=kdc_candidates,
        subject_candidates=subject_candidates,
        field_count=len(record.fields),
        validation_errors=errors,
        mrc_base64=mrc_b64,
        usage=usage_status,
        warnings=list(book_data.get("warnings", [])),
    )


def run() -> None:
    """uvicorn 엔트리포인트 (`kormarc-server`로 실행)."""
    import uvicorn

    from kormarc_auto.constants import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT

    host = os.getenv("KORMARC_HOST", DEFAULT_SERVER_HOST)
    port = int(os.getenv("KORMARC_PORT", str(DEFAULT_SERVER_PORT)))
    uvicorn.run(
        "kormarc_auto.server.app:create_app",
        host=host,
        port=port,
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    run()
