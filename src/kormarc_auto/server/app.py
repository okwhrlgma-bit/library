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
import json
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

    @app.get("/accuracy", tags=["meta"])
    def accuracy() -> JSONResponse:
        """B안 Cycle 1 — MARC 블록별 분리 정합표 (단일 99.82% 폐기)."""
        import json as _json
        from pathlib import Path as _Path

        eval_dir = _Path(__file__).resolve().parent.parent.parent.parent / "docs" / "eval"
        per_block_path = eval_dir / "results" / "2026-05-03" / "per-block.json"
        per_record_path = eval_dir / "results" / "2026-05-04" / "per-record.json"

        out: dict = {
            "headline": "자관 PILOT 1관·174 파일·3,383 레코드 round-trip 100%",
            "methodology_url": "/static/methodology.md (또는 docs/eval/methodology.md)",
            "single_99_82_deprecated": True,
            "by_block": None,
            "round_trip": None,
            "limitation": "N=1·NL_CERT_KEY 미발급·LLM extraction 정합 별도",
        }
        if per_block_path.exists():
            data = _json.loads(per_block_path.read_text(encoding="utf-8"))
            out["by_block"] = data.get("by_block")
            out["measurement_date_block"] = data.get("measurement_date")
        if per_record_path.exists():
            data = _json.loads(per_record_path.read_text(encoding="utf-8"))
            out["round_trip"] = {
                "metric": data.get("metric"),
                "total_records": data.get("total_records"),
                "pass": data.get("roundtrip_pass"),
                "pass_pct": data.get("roundtrip_pass_pct"),
                "fail_reasons": data.get("fail_reasons"),
            }
            out["measurement_date_roundtrip"] = data.get("measurement_date")
        return JSONResponse(out)

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

    @app.post("/inspect", tags=["tools"])
    async def inspect_endpoint(
        files: list[UploadFile] = File(..., description="책장 사진 1장 이상"),  # noqa: B008
        kdc_range: str = Form("", description="예상 KDC 범위, 예: '810-820'"),
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """책장 사진 OCR → 자관 DB 대조 (장서 점검)."""
        check_quota(api_key)
        from kormarc_auto.inventory.inspection import inspect_shelf_images

        if not files:
            raise HTTPException(status_code=400, detail="이미지 1장 이상 필요")

        kdc_pair: tuple[str, str] | None = None
        if kdc_range:
            parts = [p.strip() for p in kdc_range.split("-", 1)]
            if len(parts) == 2:
                kdc_pair = (parts[0], parts[1])

        tmp_paths: list[str | Path] = []
        try:
            for upload in files:
                suffix = Path(upload.filename or "shelf.jpg").suffix or ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(await upload.read())
                    tmp_paths.append(Path(tmp.name))
            try:
                result = inspect_shelf_images(tmp_paths, expected_kdc_range=kdc_pair)
            except Exception as e:
                consume(api_key, kind="inspect", ok=False, ref=str(len(tmp_paths)))
                raise HTTPException(status_code=502, detail=f"점검 실패: {e}") from e
            consume(api_key, kind="inspect", ok=True, ref=str(len(tmp_paths)))
            return result
        finally:
            for p in tmp_paths:
                with contextlib.suppress(OSError):
                    p.unlink(missing_ok=True)

    @app.post("/report/announcement", tags=["tools"])
    def report_announcement(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """신착도서 안내문 PDF — 자관 인덱스에서 최근 N권."""
        from kormarc_auto.inventory.library_db import search_local
        from kormarc_auto.output.reports import make_acquisition_announcement

        limit = int(body.get("limit", 30))
        items = search_local(query="", limit=limit)
        if not items:
            raise HTTPException(status_code=404, detail="자관 인덱스에 항목이 없습니다")
        out_path = Path(tempfile.gettempdir()) / "kormarc_announcement.pdf"
        make_acquisition_announcement(
            items,
            title=str(body.get("title") or "신착도서 안내"),
            library_name=str(body.get("library_name") or "○○도서관"),
            output_path=str(out_path),
        )
        consume(api_key, kind="report", ok=True, ref="announcement")
        pdf_b64 = base64.b64encode(out_path.read_bytes()).decode("ascii")
        with contextlib.suppress(OSError):
            out_path.unlink(missing_ok=True)
        return {"ok": True, "count": len(items), "pdf_base64": pdf_b64}

    @app.post("/report/monthly", tags=["tools"])
    def report_monthly(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """월간 자관 운영 보고서 PDF (상부기관 제출용)."""
        from datetime import datetime as _dt

        from kormarc_auto.output.reports import make_monthly_report

        now = _dt.now()
        year = int(body.get("year", now.year))
        month = int(body.get("month", now.month))
        out_path = Path(tempfile.gettempdir()) / f"kormarc_monthly_{year}_{month:02d}.pdf"
        make_monthly_report(
            library_name=str(body.get("library_name") or "○○도서관"),
            year=year,
            month=month,
            output_path=str(out_path),
        )
        consume(api_key, kind="report", ok=True, ref=f"monthly_{year}_{month:02d}")
        pdf_b64 = base64.b64encode(out_path.read_bytes()).decode("ascii")
        with contextlib.suppress(OSError):
            out_path.unlink(missing_ok=True)
        return {"ok": True, "year": year, "month": month, "pdf_base64": pdf_b64}

    @app.post("/report/validate", tags=["tools"])
    async def report_validate(
        files: list[UploadFile] = File(..., description=".mrc 파일 1개 이상"),  # noqa: B008
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """일괄 .mrc 검증 리포트 PDF."""
        from kormarc_auto.output.reports import make_validation_report

        if not files:
            raise HTTPException(status_code=400, detail=".mrc 파일 1개 이상 필요")

        tmp_paths: list[str | Path] = []
        try:
            for upload in files:
                suffix = Path(upload.filename or "data.mrc").suffix or ".mrc"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(await upload.read())
                    tmp_paths.append(Path(tmp.name))
            out_path = Path(tempfile.gettempdir()) / "kormarc_validation.pdf"
            make_validation_report(tmp_paths, output_path=str(out_path))
            consume(api_key, kind="report", ok=True, ref="validate")
            pdf_b64 = base64.b64encode(out_path.read_bytes()).decode("ascii")
            with contextlib.suppress(OSError):
                out_path.unlink(missing_ok=True)
            return {"ok": True, "file_count": len(tmp_paths), "pdf_base64": pdf_b64}
        finally:
            for p in tmp_paths:
                with contextlib.suppress(OSError):
                    p.unlink(missing_ok=True)

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

    @app.post("/webhook/portone", tags=["payment"])
    async def portone_webhook(request: Request) -> dict[str, Any]:
        """포트원 v2 webhook 수신 — ADR 0007 트리거 후 결제 자동 처리.

        HMAC-SHA256 서명 검증 → 이벤트 파싱 → 분기 처리.
        현재 stub (handle_event는 logger.info만). ADR 0007 충족 후 실 통합.
        """
        from kormarc_auto.server.portone_webhook import (
            handle_event,
            parse_event,
            verify_signature,
        )

        payload_bytes = await request.body()
        signature = request.headers.get("webhook-signature", "")

        if not verify_signature(payload_bytes, signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        try:
            payload = json.loads(payload_bytes)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}") from e

        event = parse_event(payload)
        return handle_event(event)

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

    @app.post("/batch-vendor", tags=["b2b"])
    def batch_vendor(
        body: dict[str, Any],
        api_key: str = Depends(require_api_key),
    ) -> dict[str, Any]:
        """B2B 도서납품업체 전용 — ISBN 리스트 일괄 처리.

        요청: {"isbns": ["978...", "978...", ...], "agency": "..."}
        응답: 각 ISBN별 KORMARC 결과 + 총 사용량 + .mrc base64 리스트.

        학교도서관 95% 마크 외주 의존 (2023 뉴시스). 납품업체에 라이선스
        판매로 신규 매출 라인 가능.
        """
        check_quota(api_key)
        isbns = [str(x).replace("-", "").strip() for x in body.get("isbns", [])]
        if not isbns:
            raise HTTPException(status_code=400, detail="isbns 리스트 필요")
        if len(isbns) > 1000:
            raise HTTPException(status_code=400, detail="최대 1000건/회")

        agency = str(body.get("agency", "OURLIB"))
        results: list[dict[str, Any]] = []
        ok_count = 0
        for isbn in isbns:
            try:
                book_data = aggregate_by_isbn(isbn)
                if not book_data.get("sources"):
                    results.append({"isbn": isbn, "ok": False, "reason": "no_data"})
                    consume(api_key, kind="batch-vendor", ok=False, ref=isbn)
                    continue
                kdc = recommend_kdc(book_data)
                if kdc and not book_data.get("kdc"):
                    book_data["kdc"] = kdc[0]["code"]
                record = build_kormarc_record(book_data, cataloging_agency=agency)
                add_880_pairs(record)
                errors = validate_record(record)
                out_dir = Path(tempfile.gettempdir()) / "kormarc_b2b"
                out_path = write_kolas_mrc(record, isbn, output_dir=str(out_dir))
                mrc_b64 = base64.b64encode(out_path.read_bytes()).decode("ascii")
                with contextlib.suppress(OSError):
                    out_path.unlink(missing_ok=True)
                results.append(
                    {
                        "isbn": isbn,
                        "ok": True,
                        "title": book_data.get("title"),
                        "author": book_data.get("author"),
                        "kdc": book_data.get("kdc"),
                        "confidence": book_data.get("confidence", 0),
                        "errors": errors,
                        "mrc_base64": mrc_b64,
                    }
                )
                consume(api_key, kind="batch-vendor", ok=True, ref=isbn)
                ok_count += 1
            except Exception as e:
                results.append({"isbn": isbn, "ok": False, "reason": str(e)})
                consume(api_key, kind="batch-vendor", ok=False, ref=isbn)

        return {
            "ok": True,
            "total": len(isbns),
            "success": ok_count,
            "failed": len(isbns) - ok_count,
            "results": results,
        }

    @app.get("/migrate-from-kolas", tags=["meta"])
    def migrate_from_kolas() -> dict[str, Any]:
        """KOLAS III 종료(2026-12-31) 마이그레이션 안내.

        영업 메시지 + 호환 정보 + PO 연락처. 인증 불필요(공개).
        """
        return {
            "ok": True,
            "kolas_eos": "2026-12-31",
            "title": "KOLAS III 표준형 종료 — 데이터 이전을 어떻게 하시나요?",
            "key_points": [
                "KOLAS III 표준형 기술지원이 2026-12-31 종료됩니다.",
                "kormarc-auto는 KORMARC(KS X 6006-0) 표준 .mrc/MARCXML/CSV 출력 → 후속 시스템 어떤 것이든 import 가능",
                "기존 KOLAS .mrc는 그대로 import 후 자관 .mrc 누적 시스템에 통합",
                "신규 마크 작업은 ISBN/사진/검색 어느 입력으로도 5초 이내 완료",
            ],
            "compatible_systems": [
                "후속 KOLAS III/IV (예정)",
                "KOLASYS-NET (작은도서관)",
                "독서로 DLS (학교도서관)",
                "TULIP / SOLARS (대학도서관)",
                "Koha / Alma (글로벌 표준)",
            ],
            "free_trial": "신규 가입 50건 무료 — `/signup` 호출",
            "po_contact": "contact@kormarc-auto.example",
            "pricing_url": get_payment_info_url(),
        }

    @app.get("/billing/monthly/{year}/{month}", tags=["meta"])
    def billing_monthly(
        year: int, month: int, api_key: str = Depends(require_api_key)
    ) -> dict[str, Any]:
        """[관리자] 월간 사용 집계 — 청구서 생성용. admin 키 필수."""
        from kormarc_auto.server.auth import get_admin_keys
        from kormarc_auto.server.billing import aggregate_monthly

        if api_key not in get_admin_keys():
            raise HTTPException(status_code=403, detail="관리자 키만 가능")
        return aggregate_monthly(year, month)

    @app.get("/account/export", tags=["account"])
    def account_export(api_key: str = Depends(require_api_key)) -> dict[str, Any]:
        """개인정보보호법 §35-3 — 본인 데이터 일괄 다운로드.

        키 소유자가 본인의 사용량/로그/가입/피드백을 한 번에 조회.
        ※ 결과 JSON에는 key_hash만 포함 (원본 키 비공개).
        """
        from kormarc_auto.server.usage import export_account_data

        return export_account_data(api_key)

    @app.delete("/account/delete", tags=["account"])
    def account_delete(api_key: str = Depends(require_api_key)) -> dict[str, Any]:
        """개인정보보호법 §36 — 본인 데이터 영구 삭제.

        주의: 되돌릴 수 없음. 삭제 후 동일 키 재사용 불가 (DB에서 사라짐).
        삭제 전 /account/export로 백업 권장.
        """
        from kormarc_auto.server.usage import delete_account_data

        return delete_account_data(api_key)

    @app.post("/legal/deposit-form", tags=["legal"])
    def deposit_form(
        body: dict[str, Any], api_key: str = Depends(require_api_key)
    ) -> dict[str, Any]:
        """도서관법 §21 별지 제3호서식 PDF 자동 생성.

        요청: {
          "book_data": {title, author, publisher, publication_year, isbn, ...},
          "publisher_address": "...", "submitter_name": "...",
          "is_government": false, "consents_preservation": true
        }
        응답: {ok, pdf_base64, deadline, copies}
        """
        check_quota(api_key)
        from kormarc_auto.legal.deposit_form import (
            build_deposit_form,
            deposit_deadline,
            render_deposit_form_pdf,
            required_copies,
        )

        bd = body.get("book_data") or {}
        try:
            form = build_deposit_form(
                bd,
                publisher_address=body.get("publisher_address", ""),
                publisher_contact=body.get("publisher_contact", ""),
                publisher_biz_no=body.get("publisher_biz_no"),
                submitter_name=body.get("submitter_name", ""),
                submitter_role=body.get("submitter_role", "발행인"),
                is_government=bool(body.get("is_government", False)),
                consents_preservation=bool(body.get("consents_preservation", True)),
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        out_dir = Path(tempfile.gettempdir()) / "kormarc_deposit_forms"
        out = render_deposit_form_pdf(
            form,
            output_path=out_dir / f"deposit_{form.title[:20].replace(' ', '_')}.pdf",
        )
        pdf_b64 = base64.b64encode(out.read_bytes()).decode("ascii")
        with contextlib.suppress(OSError):
            out.unlink(missing_ok=True)
        consume(api_key, kind="deposit-form", ok=True, ref=form.title[:50])
        return {
            "ok": True,
            "title": form.title,
            "deadline": deposit_deadline(form.publication_date).isoformat(),
            "copies": required_copies(form),
            "pdf_base64": pdf_b64,
        }

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

        return _build_response(
            book_data, isbn=isbn, agency=body.agency, api_key=api_key, kind="isbn"
        )

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
