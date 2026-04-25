"""kormarc-auto Streamlit UI — 모바일 반응형.

탭:
1. ISBN 단건 — ISBN 입력 → 결과 카드 → .mrc 다운로드 + 즉석 편집
2. 검색 — 키워드 → 후보 리스트 → 선택 → 단건 흐름
3. 사진 — 1~3장 업로드 (모바일 카메라) → 결과
4. 일괄 — ISBN 목록 텍스트 → CSV·ZIP 다운로드

실행: `streamlit run src/kormarc_auto/ui/streamlit_app.py` 또는 `kormarc-ui`
"""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import streamlit as st

from kormarc_auto import __version__
from kormarc_auto.api.aggregator import aggregate_by_isbn
from kormarc_auto.api.search import search_by_query
from kormarc_auto.classification.kdc_classifier import recommend_kdc
from kormarc_auto.classification.subject_recommender import recommend_subjects
from kormarc_auto.constants import (
    PAYMENT_INFO_URL,
    PRICE_PER_RECORD_KRW,
)
from kormarc_auto.kormarc.builder import build_kormarc_record
from kormarc_auto.kormarc.validator import validate_record
from kormarc_auto.logging_config import setup_logging
from kormarc_auto.output.kolas_writer import write_kolas_mrc
from kormarc_auto.vernacular.field_880 import add_880_pairs

logger = logging.getLogger(__name__)


def _record_to_mrk(record) -> str:  # type: ignore[no-untyped-def]
    """pymarc.Record → 사람이 읽는 mrk 형식 (사서 검토용)."""
    lines = [f"=LDR  {record.leader}"]
    for field in record.fields:
        if field.is_control_field():
            lines.append(f"={field.tag}  {field.data}")
        else:
            ind1, ind2 = field.indicators[0], field.indicators[1]
            ind1 = "\\" if ind1 == " " else ind1
            ind2 = "\\" if ind2 == " " else ind2
            subs = "".join("$" + s.code + s.value for s in field.subfields)
            lines.append(f"={field.tag}  {ind1}{ind2}{subs}")
    return "\n".join(lines)


def _send_feedback(api_key: str, rating: int, comment: str, category: str) -> None:
    """Streamlit 사이드바에서 피드백을 백엔드로 전송 (서버 도움 없이도 동작 — 로컬 저장)."""
    if not comment and rating == 0:
        st.warning("평점 또는 의견 중 하나는 입력하세요.")
        return
    try:
        from kormarc_auto.server.feedback import save_feedback

        save_feedback(
            api_key=api_key or "anonymous",
            rating=rating,
            comment=comment,
            category=category,
        )
        st.success("✓ 피드백 저장 완료. 감사합니다!")
    except Exception as e:
        st.error(f"저장 실패: {e}")


def _setup_page() -> None:
    st.set_page_config(
        page_title="kormarc-auto",
        page_icon="📚",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        .block-container {max-width: 720px; padding-top: 1.2rem; padding-bottom: 4rem;}
        .stButton button {width: 100%;}
        .candidate-card {border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0;}
        .small-muted {color: #888; font-size: 0.85em;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _process_isbn(isbn: str, agency: str) -> dict | None:
    """ISBN → 통합 BookData + KDC + Subject + .mrc bytes."""
    isbn = isbn.replace("-", "").strip()
    if not isbn:
        st.error("ISBN을 입력하세요.")
        return None

    with st.spinner(f"외부 API 조회 중... ({isbn})"):
        try:
            book_data = aggregate_by_isbn(isbn)
        except Exception as e:
            st.error(f"외부 API 호출 실패: {e}")
            return None

    if not book_data.get("sources"):
        st.error(f"ISBN {isbn}: 모든 소스에서 미조회")
        return None

    user_key = st.session_state.get("user_anthropic_key") or None
    use_ai = bool(st.session_state.get("ai_enabled")) and user_key
    if use_ai:
        import os

        os.environ.pop("KORMARC_DISABLE_AI", None)

    with st.spinner("KDC 분류 추천..."):
        kdc_candidates = recommend_kdc(book_data, user_api_key=user_key if use_ai else None)
    if kdc_candidates and not book_data.get("kdc"):
        book_data["kdc"] = kdc_candidates[0]["code"]

    with st.spinner("주제명 추천..."):
        subject_candidates = recommend_subjects(
            book_data, user_api_key=user_key if use_ai else None
        )

    with st.spinner("KORMARC 빌드..."):
        record = build_kormarc_record(book_data, cataloging_agency=agency)
        add_880_pairs(record)
        errors = validate_record(record)

    out_dir = Path(".cache/kormarc-auto/ui-output")
    out_path = write_kolas_mrc(record, isbn, output_dir=str(out_dir))
    mrc_bytes = out_path.read_bytes()

    # 자관 인덱스 자동 누적 (검색 가능)
    try:
        from kormarc_auto.inventory.library_db import add_record

        add_record({**book_data, "isbn": isbn}, mrc_path=str(out_path))
    except Exception:
        pass

    return {
        "isbn": isbn,
        "book_data": book_data,
        "kdc_candidates": kdc_candidates,
        "subject_candidates": subject_candidates,
        "record": record,
        "errors": errors,
        "mrc_bytes": mrc_bytes,
        "field_count": len(record.fields),
    }


def _render_result(result: dict) -> None:
    """단건 결과 카드 렌더."""
    bd = result["book_data"]
    st.success(f"✓ {bd.get('title') or '표제 미상'}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("신뢰도", f"{bd.get('confidence', 0):.2f}")
    with col2:
        st.metric("KORMARC 필드 수", result["field_count"])

    st.markdown(f"**저자**: {bd.get('author', '?')}")
    st.markdown(f"**출판**: {bd.get('publisher', '?')} ({bd.get('publication_year', '?')})")
    st.markdown(f"**소스**: {', '.join(bd.get('sources', []))}")

    if bd.get("attributions"):
        st.caption(" / ".join(bd["attributions"]))

    if result["kdc_candidates"]:
        with st.expander(f"KDC 후보 ({len(result['kdc_candidates'])}개)"):
            for c in result["kdc_candidates"]:
                st.markdown(
                    f"- **{c['code']}** (conf {c['confidence']:.2f}, {c['source']}) "
                    f"<span class='small-muted'>{c.get('rationale', '')}</span>",
                    unsafe_allow_html=True,
                )

    if result["subject_candidates"]:
        with st.expander(f"주제명 후보 ({len(result['subject_candidates'])}개)"):
            for c in result["subject_candidates"]:
                st.markdown(f"- **{c['term']}** (conf {c['confidence']:.2f}, {c['source']})")

    if result["errors"]:
        with st.expander(f"⚠ 검증 경고 ({len(result['errors'])}개)"):
            for e in result["errors"]:
                st.warning(e)
    else:
        st.success("✓ 검증 통과")

    with st.expander("📄 KORMARC 미리보기 (mrk 텍스트)"):
        st.code(_record_to_mrk(result["record"]), language="text")

    st.download_button(
        label="📥 .mrc 다운로드 (KOLAS 자동 반입)",
        data=result["mrc_bytes"],
        file_name=f"{result['isbn']}.mrc",
        mime="application/marc",
    )


def _tab_isbn(agency: str) -> None:
    st.subheader("ISBN 단건")
    isbn = st.text_input("ISBN-13", placeholder="9788936434120", key="isbn_input")
    if st.button("KORMARC 생성", key="isbn_btn"):
        result = _process_isbn(isbn, agency)
        if result:
            _render_result(result)


def _tab_search(agency: str) -> None:
    st.subheader("키워드 검색")
    query = st.text_input("검색어", placeholder="한강 작별하지 않는다", key="search_input")
    limit = st.slider("최대 결과 수", 5, 30, 10, key="search_limit")

    if st.button("검색", key="search_btn"):
        with st.spinner("검색 중..."):
            try:
                candidates = search_by_query(query, limit=limit)
            except Exception as e:
                st.error(f"검색 실패: {e}")
                return
        if not candidates:
            st.warning("검색 결과 없음")
            return
        st.session_state["search_candidates"] = candidates

    cands = st.session_state.get("search_candidates", [])
    for i, c in enumerate(cands):
        with st.container():
            st.markdown(
                f"<div class='candidate-card'><strong>{c.get('title', '?')}</strong><br>"
                f"<span class='small-muted'>{c.get('author', '?')} · {c.get('publisher', '?')} "
                f"({c.get('publication_year', '?')}) · ISBN {c.get('isbn', '?')} · "
                f"conf {c.get('confidence', 0):.2f}</span></div>",
                unsafe_allow_html=True,
            )
            if c.get("isbn") and st.button("이 ISBN으로 KORMARC 생성", key=f"cand_{i}"):
                result = _process_isbn(c["isbn"], agency)
                if result:
                    _render_result(result)


def _tab_photo(agency: str) -> None:
    st.subheader("사진 → KORMARC")
    st.caption("표지·판권지·뒷표지 사진 1~3장 업로드. 모바일에서는 카메라 직접 촬영 가능.")
    uploads = st.file_uploader(
        "이미지 선택",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="photo_upload",
    )
    if not uploads:
        return
    if len(uploads) > 3:
        st.warning("최대 3장까지 사용. 처음 3장만 분석합니다.")
        uploads = uploads[:3]

    for up in uploads:
        st.image(up, width=180)

    if st.button("Vision 분석 + KORMARC 생성", key="photo_btn"):
        from kormarc_auto.vision.photo_pipeline import photo_to_book_data

        tmp_dir = Path(".cache/kormarc-auto/ui-uploads")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str | Path] = []
        for up in uploads:
            p = tmp_dir / up.name
            p.write_bytes(up.getvalue())
            paths.append(p)

        with st.spinner("이미지 분석 (바코드 → Vision)"):
            try:
                book_data = photo_to_book_data(paths)
            except Exception as e:
                st.error(f"Vision 실패: {e}")
                return

        if book_data.get("vision_only") and not book_data.get("isbn"):
            st.error("ISBN 추출 실패 — 사진 품질을 확인하세요.")
            if book_data.get("warnings"):
                for w in book_data["warnings"]:
                    st.warning(w)
            return

        # ISBN이 잡혔으면 단건 흐름 재사용
        if book_data.get("isbn"):
            result = _process_isbn(str(book_data["isbn"]), agency)
            if result:
                _render_result(result)
        else:
            st.info("Vision만으로 메타데이터 추출 — 사서 검토 필수")
            st.json(book_data)


def _tab_batch(agency: str) -> None:
    st.subheader("일괄 처리")
    st.caption("ISBN을 한 줄에 하나씩 입력. CSV 요약 + 모든 .mrc를 ZIP으로 다운로드.")
    text = st.text_area("ISBN 목록", height=180, key="batch_input")
    if not st.button("일괄 처리", key="batch_btn"):
        return

    isbns = [
        line.strip().replace("-", "")
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not isbns:
        st.warning("ISBN이 없습니다.")
        return

    progress = st.progress(0.0)
    rows: list[dict] = []
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, isbn in enumerate(isbns, 1):
            progress.progress(i / len(isbns), text=f"{i}/{len(isbns)} {isbn}")
            try:
                result = _process_isbn(isbn, agency)
                if result:
                    bd = result["book_data"]
                    rows.append(
                        {
                            "isbn": isbn,
                            "title": bd.get("title", ""),
                            "author": bd.get("author", ""),
                            "publisher": bd.get("publisher", ""),
                            "year": bd.get("publication_year", ""),
                            "confidence": f"{bd.get('confidence', 0):.2f}",
                            "fields": result["field_count"],
                            "errors": len(result["errors"]),
                            "ok": "Y",
                        }
                    )
                    zf.writestr(f"{isbn}.mrc", result["mrc_bytes"])
                else:
                    rows.append({"isbn": isbn, "ok": "N", "title": "", "author": "", "publisher": "", "year": "", "confidence": "", "fields": "", "errors": ""})
            except Exception as e:
                rows.append({"isbn": isbn, "ok": "N", "title": str(e)[:40], "author": "", "publisher": "", "year": "", "confidence": "", "fields": "", "errors": ""})

    progress.empty()
    st.dataframe(rows, use_container_width=True)

    csv_bytes = _rows_to_csv(rows)
    st.download_button(
        "📊 CSV 요약 다운로드",
        data=csv_bytes,
        file_name="batch_summary.csv",
        mime="text/csv",
    )
    st.download_button(
        "📦 모든 .mrc ZIP 다운로드",
        data=zip_buf.getvalue(),
        file_name="kormarc_batch.zip",
        mime="application/zip",
    )


def _tab_tools() -> None:
    """사서 도구 모음 탭 — 로마자·라벨·자관 검색·KDC 트리·식별기호 도움말."""
    st.subheader("🛠 사서 도구")
    sub_tabs = st.tabs(
        ["로마자", "라벨 PDF", "자관 검색", "KDC 트리", "식별기호 ▾", "장서점검", "보고서"]
    )

    with sub_tabs[0]:
        st.markdown("**한글 → 로마자 (RR + ALA-LC)**")
        text = st.text_input("한글 입력", key="rom_input", placeholder="한강 작별하지 않는다")
        if text:
            from kormarc_auto.librarian_helpers.romanization import (
                hangul_to_alalc,
                hangul_to_rr,
            )

            st.code(f"RR (정부 표준):  {hangul_to_rr(text)}\nALA-LC (학술): {hangul_to_alalc(text)}")

    with sub_tabs[1]:
        st.markdown("**A4 라벨 PDF 생성** (Avery L7160 21장 / L7159 24장)")
        layout = st.selectbox("레이아웃", ["L7160", "L7159", "A4_one"], key="lbl_layout")
        csv_text = st.text_area(
            "라벨 데이터 (한 줄: 청구기호,등록번호,표제)",
            placeholder="813.7 한31ㅈ,K000123,작별하지 않는다",
            height=140,
            key="lbl_csv",
        )
        if st.button("PDF 생성", key="lbl_btn"):
            items = []
            for line in csv_text.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    items.append(
                        {
                            "call_number": parts[0],
                            "registration_no": parts[1],
                            "title": parts[2],
                            "barcode_value": parts[1],
                        }
                    )
            if not items:
                st.warning("최소 1줄 (청구기호,등록번호,표제) 입력 필요")
            else:
                try:
                    from kormarc_auto.output.labels import make_label_pdf

                    out_path = Path(".cache/kormarc-auto/ui-labels/labels.pdf")
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    pdf = make_label_pdf(items, output_path=str(out_path), layout=layout)
                    st.download_button(
                        "📥 라벨 PDF 다운로드",
                        data=pdf.read_bytes(),
                        file_name=f"labels_{layout}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"실패: {e}\n\n`pip install -e .[labels]` 필요할 수 있음")

    with sub_tabs[2]:
        st.markdown("**자관 장서 검색** (생성한 .mrc 누적 인덱스)")
        from kormarc_auto.inventory.library_db import search_local, stats

        col1, col2 = st.columns([2, 1])
        with col1:
            q = st.text_input("검색어", key="inv_q", placeholder="ISBN·표제·저자·등록번호")
        with col2:
            kdc_pf = st.text_input("KDC 시작", key="inv_kdc", placeholder="813")
        if st.button("검색", key="inv_btn") or q:
            results = search_local(q, kdc_prefix=kdc_pf or None, limit=50)
            st.write(f"{len(results)}건")
            for r in results[:20]:
                st.markdown(
                    f"- **{r.get('title', '?')}** · {r.get('author', '?')} "
                    f"· KDC `{r.get('kdc', '-')}` · ISBN `{r.get('isbn', '?')}`"
                )

        st.markdown("---")
        st.markdown("**자관 통계**")
        s = stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 레코드", s["total"])
        with col2:
            top_kdc = max(s["by_kdc_main"].items(), key=lambda x: x[1], default=("-", 0))
            st.metric("최다 KDC", f"{top_kdc[0]} ({top_kdc[1]})")
        if s["by_kdc_main"]:
            st.bar_chart(s["by_kdc_main"])

    with sub_tabs[3]:
        st.markdown("**KDC 6판 트리 탐색**")
        from kormarc_auto.librarian_helpers.kdc_tree import (
            get_main_classes,
            get_subtree,
            search_kdc,
        )

        kw = st.text_input("키워드 검색", key="kdc_search", placeholder="소설·역사·종교")
        if kw:
            results = search_kdc(kw, limit=20)
            for code, name in results:
                st.markdown(f"- **{code}** {name}")
        st.markdown("---")
        main_choice = st.selectbox(
            "주류 선택", [f"{c} {n}" for c, n in get_main_classes()], key="kdc_main"
        )
        if main_choice:
            main_code = main_choice.split()[0]
            sub = get_subtree(main_code)
            for code, name in sub.items():
                st.markdown(f"- **{code}** {name}")

    with sub_tabs[5]:
        st.markdown("**장서 점검** — 책장 사진 OCR → 자관 DB 대조")
        st.caption("연 1~2회 사서가 며칠 걸리는 전수 점검을 자동화합니다.")
        uploads = st.file_uploader(
            "책장(책등) 사진 업로드",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="insp_imgs",
        )
        col1, col2 = st.columns(2)
        with col1:
            kdc_start = st.text_input(
                "예상 KDC 시작",
                key="insp_start",
                placeholder="810",
                help="이 책장에 있어야 할 KDC 범위 시작",
            )
        with col2:
            kdc_end = st.text_input(
                "예상 KDC 끝",
                key="insp_end",
                placeholder="820",
                help="범위 끝. 비우면 오배가 판별 생략.",
            )
        if uploads and st.button("점검 시작", key="insp_btn"):
            from kormarc_auto.inventory.inspection import inspect_shelf_images

            tmp_dir = Path(".cache/kormarc-auto/inspection")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            paths: list[Path] = []
            for u in uploads:
                p = tmp_dir / (u.name or "shelf.jpg")
                p.write_bytes(u.read())
                paths.append(p)
            kdc_pair = (
                (kdc_start.strip(), kdc_end.strip()) if kdc_start and kdc_end else None
            )
            with st.spinner("OCR + 대조 진행 중..."):
                try:
                    result = inspect_shelf_images(paths, expected_kdc_range=kdc_pair)
                except Exception as e:
                    st.error(f"점검 실패: {e}\n\n`pip install -e .[ocr]` 필요할 수 있음")
                    result = None
            if result:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("검출", result["detected_count"])
                c2.metric("일치", len(result["matched"]))
                c3.metric("오배가", len(result["missorted"]))
                c4.metric("미등록", len(result["missing_in_db"]))
                if result["missorted"]:
                    st.markdown("**오배가 후보**")
                    for cn in result["missorted"][:20]:
                        st.markdown(f"- `{cn}`")
                if result["missing_in_db"]:
                    st.markdown("**미등록 후보 (자관 DB에 없음)**")
                    for cn in result["missing_in_db"][:20]:
                        st.markdown(f"- `{cn}`")
                if result["warnings"]:
                    with st.expander("경고 메시지"):
                        for w in result["warnings"]:
                            st.caption(f"- {w}")

                from kormarc_auto.inventory.inspection import (
                    inspection_result_to_csv_bytes,
                )

                st.download_button(
                    "📥 점검 결과 CSV 다운로드",
                    data=inspection_result_to_csv_bytes(result),
                    file_name="inspection_result.csv",
                    mime="text/csv",
                )

    with sub_tabs[6]:
        st.markdown("**보고서 PDF** — 신착 안내·월간 보고·일괄 검증")
        report_kind = st.radio(
            "유형",
            ["신착 안내문 (이용자용)", "월간 운영 보고서 (상부기관)", "일괄 검증 리포트"],
            key="rep_kind",
        )
        library = st.text_input("도서관명", "○○도서관", key="rep_lib")

        if report_kind.startswith("신착"):
            n = st.number_input("게재 권수", 5, 200, 30, key="rep_ann_n")
            title = st.text_input("안내문 제목", "신착도서 안내", key="rep_ann_title")
            if st.button("PDF 생성", key="rep_ann_btn"):
                from kormarc_auto.inventory.library_db import search_local
                from kormarc_auto.output.reports import make_acquisition_announcement

                items = search_local(query="", limit=int(n))
                if not items:
                    st.warning("자관 인덱스가 비었습니다 — 먼저 ISBN/사진 탭에서 .mrc를 생성하세요.")
                else:
                    out_path = Path(".cache/kormarc-auto/reports/announcement.pdf")
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        pdf = make_acquisition_announcement(
                            items,
                            title=title,
                            library_name=library,
                            output_path=str(out_path),
                        )
                        st.download_button(
                            "📥 안내문 PDF 다운로드",
                            data=pdf.read_bytes(),
                            file_name="acquisition_announcement.pdf",
                            mime="application/pdf",
                        )
                        st.success(f"{len(items)}권 게재")
                    except Exception as e:
                        st.error(f"PDF 생성 실패: {e}")

        elif report_kind.startswith("월간"):
            from datetime import datetime as _dt

            now = _dt.now()
            col_y, col_m = st.columns(2)
            with col_y:
                year = st.number_input("연도", 2020, 2100, now.year, key="rep_year")
            with col_m:
                month = st.number_input("월", 1, 12, now.month, key="rep_month")
            if st.button("PDF 생성", key="rep_mon_btn"):
                from kormarc_auto.output.reports import make_monthly_report

                out_path = Path(
                    f".cache/kormarc-auto/reports/monthly_{int(year)}_{int(month):02d}.pdf"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    pdf = make_monthly_report(
                        library_name=library,
                        year=int(year),
                        month=int(month),
                        output_path=str(out_path),
                    )
                    st.download_button(
                        "📥 월간 보고서 다운로드",
                        data=pdf.read_bytes(),
                        file_name=f"monthly_{int(year)}_{int(month):02d}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF 생성 실패: {e}")

        else:  # 일괄 검증
            mrcs = st.file_uploader(
                ".mrc 파일 업로드 (다중 가능)",
                type=["mrc"],
                accept_multiple_files=True,
                key="rep_val_files",
            )
            if mrcs and st.button("PDF 생성", key="rep_val_btn"):
                from kormarc_auto.output.reports import make_validation_report

                tmp_dir = Path(".cache/kormarc-auto/reports/validate")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                paths: list[Path] = []
                for u in mrcs:
                    p = tmp_dir / (u.name or "data.mrc")
                    p.write_bytes(u.read())
                    paths.append(p)
                try:
                    pdf = make_validation_report(
                        paths,
                        output_path=str(tmp_dir / "validation_report.pdf"),
                    )
                    st.download_button(
                        "📥 검증 리포트 다운로드",
                        data=pdf.read_bytes(),
                        file_name="validation_report.pdf",
                        mime="application/pdf",
                    )
                    st.success(f"{len(paths)}개 파일 검증 완료")
                except Exception as e:
                    st.error(f"PDF 생성 실패: {e}")

    with sub_tabs[4]:
        st.markdown("**식별기호 ▾ 변환·도움말**")
        from kormarc_auto.librarian_helpers.subfield_input import (
            common_subfield_hint,
            expand_subfield_codes,
        )

        text = st.text_input(
            "입력 ($a·//a → ▾a 변환)",
            key="sf_input",
            placeholder="245 10 $a작별하지 않는다 $c/ 한강",
        )
        if text:
            st.code(expand_subfield_codes(text))
        tag = st.text_input("필드 태그 (도움말)", key="sf_tag", placeholder="245")
        if tag:
            st.info(common_subfield_hint(tag))


def _rows_to_csv(rows: list[dict]) -> bytes:
    import csv

    buf = io.StringIO()
    if not rows:
        return b""
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8-sig")


def main() -> None:
    from dotenv import load_dotenv

    # .env를 작업 폴더에서 우선, 없으면 부모로 거슬러 올라가며 자동 탐색
    load_dotenv()
    setup_logging()
    _setup_page()

    st.title("📚 kormarc-auto")
    st.caption(f"한국 도서관용 KORMARC 자동 생성 · v{__version__}")

    with st.sidebar:
        st.markdown("### 설정")
        agency = st.text_input("우리 도서관 부호 (040 ▾a)", "OURLIB", key="agency_input")
        st.markdown("---")
        st.markdown("### AI 보조 (선택)")
        st.markdown("KDC·주제명 AI 추천을 쓰려면 본인 Anthropic 키 입력. 비용은 본인 부담 (권당 약 0.5원).")
        ai_key = st.text_input(
            "Anthropic API 키",
            type="password",
            placeholder="sk-ant-api03-...",
            key="user_anthropic_key",
            help="https://console.anthropic.com/settings/keys 에서 발급",
        )
        st.checkbox(
            "AI 보조 사용",
            value=bool(ai_key),
            key="ai_enabled",
            disabled=not bool(ai_key),
            help="키 입력 시에만 활성. AI 미사용 시 ISBN 부가기호·KDC 트리만 사용.",
        )
        if ai_key:
            st.caption("✓ AI 사용 가능 — 본인 비용으로 호출됨")
        st.markdown("---")
        st.markdown("### 가격 안내")
        st.markdown(f"- 권당 **{PRICE_PER_RECORD_KRW:,}원**")
        st.markdown("- 신규 50건 무료 체험")
        st.markdown(f"- [가격 페이지]({PAYMENT_INFO_URL})")
        st.markdown("---")
        with st.expander("📖 처음이신가요? (5분 가이드)"):
            st.markdown(
                "**1. ISBN 단건** — 13자리 ISBN 입력 → KORMARC 생성  \n"
                "**2. 검색** — 표제/저자로 후보 보고 선택  \n"
                "**3. 사진** — 표지·판권지 1~3장 (폰 카메라 OK)  \n"
                "**4. 일괄** — ISBN 여러 개를 한 번에  \n\n"
                "결과 카드의 KDC·주제명은 **AI 추천** 후보입니다. "
                "사서가 검토 후 사용하세요. KOLAS 반입 폴더에 .mrc 파일을 넣으면 자동 인식."
            )
        with st.expander("💬 피드백 보내기"):
            fb_rating = st.slider("평점 (선택)", 0, 5, 0, key="fb_rating")
            fb_category = st.selectbox(
                "분류",
                ["bug", "feature", "ux", "정확도", "기타"],
                key="fb_cat",
            )
            fb_comment = st.text_area("사용 소감·요청", height=100, key="fb_comment")
            fb_key = st.text_input("API 키 (있으면)", type="password", key="fb_key")
            if st.button("피드백 전송", key="fb_send"):
                _send_feedback(fb_key, fb_rating, fb_comment, fb_category)
        st.markdown("---")
        st.caption("MVP 베타 — 사서 피드백 환영")

    tabs = st.tabs(["ISBN", "검색", "사진", "일괄", "🛠 도구"])
    with tabs[0]:
        _tab_isbn(agency)
    with tabs[1]:
        _tab_search(agency)
    with tabs[2]:
        _tab_photo(agency)
    with tabs[3]:
        _tab_batch(agency)
    with tabs[4]:
        _tab_tools()


def run() -> None:
    """`kormarc-ui` 엔트리포인트 — streamlit run을 wrapping."""
    import os
    import subprocess
    import sys

    script = Path(__file__).resolve()
    port = os.getenv("KORMARC_UI_PORT", "8501")
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(script),
        "--server.port",
        port,
        "--server.address",
        "127.0.0.1",
        "--browser.gatherUsageStats",
        "false",
    ]
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
