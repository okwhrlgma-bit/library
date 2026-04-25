"""월별 청구·영수증 생성 — 캐시카우 자동화의 핵심.

PO 손 안 타고 매출 발생 가능하게:
1. 월말 자동으로 키별 사용량 집계 → 청구서 JSON 생성
2. 한국 도서관 예산 처리용 영수증 PDF (사업자번호·계좌번호·금액)
3. 결제 임박 알림 (잔여 5건 이하 시 응답에 자동 첨부)

PO가 매월 invoice JSON을 보고 카카오뱅크/통장 입금 확인 후 reset_usage 호출.
나중에 Stripe/포트원 정식 결제 연동 시 이 모듈만 교체.
"""

from __future__ import annotations

import calendar
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from kormarc_auto.constants import (
    PRICE_PER_RECORD_KRW,
    USAGE_LOG_PATH,
)

logger = logging.getLogger(__name__)


# 월정액 플랜 자동 추천 임계값 (CLAUDE.md §12 가격표 기반)
PLAN_TIERS = [
    (500, 30000, "월정액 (작은도서관)"),
    (1000, 50000, "월정액 (소)"),
    (5000, 150000, "월정액 (중)"),
    (float("inf"), 300000, "월정액 (대) — 무제한"),
]


def _log_path() -> Path:
    return Path(os.getenv("KORMARC_USAGE_LOG", USAGE_LOG_PATH))


def aggregate_monthly(year: int, month: int) -> dict[str, Any]:
    """해당 연·월의 키별 사용량 집계.

    Returns:
        {
            "year": 2026,
            "month": 4,
            "total_records": 1234,
            "total_revenue_krw": 123400,
            "by_key": {
                "key_hash_xx": {
                    "records": 50,
                    "revenue_krw": 5000,
                    "by_kind": {"isbn": 30, "photo": 5, "search": 15},
                    "recommended_plan": ("월정액 (작은도서관)", 30000),
                },
                ...
            }
        }
    """
    log = _log_path()
    if not log.exists():
        return _empty_summary(year, month)

    start_ts = int(datetime(year, month, 1).timestamp())
    last_day = calendar.monthrange(year, month)[1]
    end_ts = int(datetime(year, month, last_day, 23, 59, 59).timestamp())

    by_key: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"records": 0, "revenue_krw": 0, "by_kind": defaultdict(int)}
    )
    total_records = 0

    with log.open(encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = e.get("ts", 0)
            if ts < start_ts or ts > end_ts:
                continue
            if not e.get("ok"):
                continue
            kh = e.get("key_hash") or "unknown"
            by_key[kh]["records"] += 1
            by_key[kh]["by_kind"][e.get("kind", "unknown")] += 1
            by_key[kh]["revenue_krw"] += e.get("cost_estimate_krw", PRICE_PER_RECORD_KRW)
            total_records += 1

    # plan 추천 + dict 직렬화
    for info in by_key.values():
        info["by_kind"] = dict(info["by_kind"])
        info["recommended_plan"] = recommend_plan(info["records"])

    return {
        "year": year,
        "month": month,
        "total_records": total_records,
        "total_revenue_krw": total_records * PRICE_PER_RECORD_KRW,
        "by_key": dict(by_key),
        "generated_at": datetime.now().isoformat(),
    }


def recommend_plan(monthly_records: int) -> tuple[str, int]:
    """월간 사용량 → 권장 플랜 (이름, 가격)."""
    pay_per_use = monthly_records * PRICE_PER_RECORD_KRW
    for limit, price, name in PLAN_TIERS:
        if monthly_records <= limit and price < pay_per_use * 1.2:
            return (name, price)
    return ("권당 과금", pay_per_use)


def _empty_summary(year: int, month: int) -> dict[str, Any]:
    return {
        "year": year,
        "month": month,
        "total_records": 0,
        "total_revenue_krw": 0,
        "by_key": {},
        "generated_at": datetime.now().isoformat(),
    }


def write_monthly_invoice_json(
    year: int,
    month: int,
    *,
    output_path: str | Path | None = None,
) -> Path:
    """월간 청구서 JSON 저장 (PO가 카카오뱅크 입금 확인용)."""
    summary = aggregate_monthly(year, month)
    out = Path(
        output_path or f"logs/invoices/invoice_{year}_{month:02d}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "월간 청구서 저장: %s (총 %d건 / %s원)",
        out, summary["total_records"], f"{summary['total_revenue_krw']:,}",
    )
    return out


def render_invoice_pdf(
    year: int,
    month: int,
    *,
    library_name: str = "도서관",
    api_key_hash: str,
    output_path: str | Path | None = None,
    business_info: dict[str, str] | None = None,
) -> Path:
    """한국 도서관 예산 처리용 영수증 PDF (한 키 한 영수증).

    business_info: PO 사업자 정보
        {"name": "kormarc-auto", "biz_no": "000-00-00000",
         "address": "...", "bank": "카카오뱅크 3333-00-0000000"}
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
    except ImportError as e:
        raise RuntimeError("reportlab 미설치 — `pip install reportlab`") from e

    from kormarc_auto.output.reports import _korean_font

    summary = aggregate_monthly(year, month)
    key_summary = summary["by_key"].get(api_key_hash, {
        "records": 0, "revenue_krw": 0, "by_kind": {}, "recommended_plan": ("", 0),
    })

    biz = business_info or {
        "name": "kormarc-auto",
        "biz_no": os.getenv("KORMARC_BIZ_NO", "(사업자번호 미등록)"),
        "address": os.getenv("KORMARC_BIZ_ADDR", "(주소 미등록)"),
        "bank": os.getenv("KORMARC_BANK_INFO", "(계좌 미등록)"),
    }

    out = Path(
        output_path or f"logs/invoices/invoice_{year}_{month:02d}_{api_key_hash}.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    font = _korean_font(c)
    _w, page_h = A4
    margin = 20 * mm
    y = page_h - margin

    c.setFont(font, 18)
    c.drawString(margin, y, f"영수증 — {year}년 {month}월")
    y -= 12 * mm

    c.setFont(font, 11)
    c.drawString(margin, y, f"공급받는 자: {library_name}")
    y -= 6 * mm
    c.drawString(margin, y, f"키 식별자: {api_key_hash}")
    y -= 6 * mm
    c.drawString(margin, y, f"청구 기간: {year}-{month:02d}-01 ~ {year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}")
    y -= 10 * mm

    c.setFont(font, 14)
    c.drawString(margin, y, "사용 내역")
    y -= 8 * mm
    c.setFont(font, 11)
    for kind, count in key_summary.get("by_kind", {}).items():
        c.drawString(margin + 5 * mm, y, f"• {kind}: {count}건")
        y -= 6 * mm

    y -= 4 * mm
    c.setFont(font, 13)
    total = key_summary.get("revenue_krw", 0)
    c.drawString(margin, y, f"합계: {total:,}원 (권당 {PRICE_PER_RECORD_KRW}원 x {key_summary['records']}건)")
    y -= 10 * mm

    plan_name, plan_price = key_summary.get("recommended_plan", ("", 0))
    if plan_name and "권당" not in plan_name:
        c.setFont(font, 10)
        c.drawString(
            margin,
            y,
            f"💡 권장 플랜: {plan_name} ({plan_price:,}원/월) — 다음 달부터 절감 가능",
        )
        y -= 10 * mm

    c.setFont(font, 10)
    c.drawString(margin, y, "공급자")
    y -= 5 * mm
    c.drawString(margin, y, f"  · 상호: {biz['name']}")
    y -= 5 * mm
    c.drawString(margin, y, f"  · 사업자: {biz['biz_no']}")
    y -= 5 * mm
    c.drawString(margin, y, f"  · 주소: {biz['address']}")
    y -= 5 * mm
    c.drawString(margin, y, f"  · 입금 계좌: {biz['bank']}")
    y -= 10 * mm

    c.setFont(font, 8)
    c.drawString(margin, margin, f"발행: {datetime.now().strftime('%Y-%m-%d %H:%M')} · kormarc-auto")
    c.save()
    logger.info("영수증 PDF: %s", out)
    return out


__all__ = [
    "PLAN_TIERS",
    "aggregate_monthly",
    "recommend_plan",
    "render_invoice_pdf",
    "write_monthly_invoice_json",
]
