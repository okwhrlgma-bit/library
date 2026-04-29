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
    """페이지 설정 + 사서 친화적 UI 테마 (큰 글씨·차분한 색·터치 영역).

    UX 원칙:
    - 50대 사서가 폰·PC 양쪽 사용 가정
    - 본문 16px (작은 글씨 거부감)
    - 도서관 톤 (네이비·살구·아이보리)
    - 버튼 높이 48px+ (모바일 터치 안전)
    - 카드 둥근 모서리 12px, 약한 그림자
    - 한글 폰트 우선 (Pretendard fallback Noto Sans KR)
    """
    st.set_page_config(
        page_title="kormarc-auto · 사서 KORMARC 자동 생성",
        page_icon="📚",
        layout="centered",
        initial_sidebar_state="collapsed",
        menu_items={
            "Get Help": "mailto:okwhrlgma@gmail.com",
            "Report a bug": "mailto:okwhrlgma@gmail.com",
            "About": "kormarc-auto · 한국 도서관 KORMARC 자동 생성 SaaS",
        },
    )
    st.markdown(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

        :root {
          --primary: #2C5282;          /* 차분한 네이비 (도서관 톤) */
          --primary-soft: #EBF4FF;
          --accent: #ED8936;           /* 살구색 (CTA·강조) */
          --bg: #FAFAF7;               /* 아이보리 배경 */
          --text: #1A202C;
          --muted: #718096;
          --success: #38A169;
          --warning: #D69E2E;
          --error: #C53030;
        }

        html, body, [class*="css"] {
          font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif !important;
          font-size: 16px !important;
          line-height: 1.6 !important;
          color: var(--text) !important;
        }

        .block-container {
          max-width: 760px;
          padding-top: 1.5rem;
          padding-bottom: 5rem;
        }

        h1, h2, h3 {
          letter-spacing: -0.02em;
          color: var(--primary) !important;
        }
        h1 { font-size: 28px !important; }
        h2 { font-size: 22px !important; }
        h3 { font-size: 18px !important; }

        /* 버튼 — 큰 터치 영역, 차분한 톤 */
        .stButton button {
          width: 100%;
          min-height: 48px;
          font-size: 16px !important;
          font-weight: 600;
          border-radius: 10px !important;
          background: var(--primary) !important;
          color: white !important;
          border: none !important;
          transition: all 0.2s;
        }
        .stButton button:hover {
          background: #1A365D !important;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(44, 82, 130, 0.2);
        }

        /* 다운로드 버튼은 살구색 (강조) */
        .stDownloadButton button {
          background: var(--accent) !important;
          min-height: 48px;
          font-size: 16px !important;
          border-radius: 10px !important;
        }

        /* 입력 — 큰 글씨, 명확한 테두리 */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
          font-size: 16px !important;
          padding: 12px !important;
          border-radius: 8px !important;
          border: 1.5px solid #CBD5E0 !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
          border-color: var(--primary) !important;
          box-shadow: 0 0 0 3px var(--primary-soft) !important;
        }

        /* 카드 */
        .candidate-card {
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          padding: 16px;
          margin: 10px 0;
          background: white;
          box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .candidate-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
          border-color: var(--primary);
        }

        /* 메시지 박스 */
        .stAlert {
          border-radius: 10px !important;
          font-size: 15px !important;
        }

        /* 작은 안내 글 */
        .small-muted {
          color: var(--muted);
          font-size: 14px;
        }

        /* 메트릭 카드 */
        [data-testid="metric-container"] {
          background: white;
          padding: 16px;
          border-radius: 10px;
          border: 1px solid #E2E8F0;
        }

        /* 탭 */
        button[data-baseweb="tab"] {
          font-size: 16px !important;
          font-weight: 600;
        }

        /* 모바일 ≤ 480px */
        @media (max-width: 480px) {
          .block-container { padding: 1rem; }
          h1 { font-size: 24px !important; }
          .stButton button { min-height: 52px; }
        }
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

    with st.spinner(f"외부 API 조회 중 (약 3초)... {isbn}"):
        try:
            book_data = aggregate_by_isbn(isbn)
        except Exception as e:
            st.error(f"외부 API 호출 실패: {e}")
            st.info(
                "💡 **해결 방법:**\n"
                "1. 인터넷 연결을 확인하세요\n"
                "2. 잠시 후 다시 시도하세요 (외부 API 일시 장애일 수 있음)\n"
                "3. 계속 실패하면 [사진] 탭으로 표지 업로드"
            )
            return None

    if not book_data.get("sources"):
        st.error(f"ISBN {isbn}: 등록 정보를 찾을 수 없습니다.")
        st.info(
            "💡 **해결 방법:**\n"
            "1. ISBN 13자리가 맞는지 확인 (978로 시작)\n"
            "2. [검색] 탭에서 표제·저자로 시도\n"
            "3. 옛 책·자가출판이면 [사진] 탭으로 표지 업로드"
        )
        return None

    user_key = st.session_state.get("user_anthropic_key") or None
    use_ai = bool(st.session_state.get("ai_enabled")) and user_key
    if use_ai:
        import os

        os.environ.pop("KORMARC_DISABLE_AI", None)

    with st.spinner("KDC 분류 추천 중 (약 2초)..."):
        kdc_candidates = recommend_kdc(book_data, user_api_key=user_key if use_ai else None)
    if kdc_candidates and not book_data.get("kdc"):
        book_data["kdc"] = kdc_candidates[0]["code"]

    with st.spinner("주제명 추천 중 (약 2초)..."):
        subject_candidates = recommend_subjects(
            book_data, user_api_key=user_key if use_ai else None
        )

    with st.spinner("KORMARC 빌드 중..."):
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
            st.warning("검색 결과가 없습니다.")
            st.info(
                "💡 **다음을 시도해 보세요:**\n"
                "- 띄어쓰기/오타 확인 (예: '한강 작별' vs '한강작별')\n"
                "- 표제 일부만 (예: '작별')\n"
                "- 저자명 단독\n"
                "- ISBN을 알면 [ISBN 단건] 탭이 더 정확합니다"
            )
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
    st.caption(
        "표지·판권지·뒷표지 사진 1~3장 업로드. 폰에서 사용 시 [사진 촬영]을 누르세요. "
        "ISBN이 있는 판권지(책 뒷쪽 4페이지)가 가장 정확합니다."
    )
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
            st.info(
                "💡 **해결 방법:**\n"
                "1. **판권지(책 뒷쪽)** 사진을 찍으세요 — ISBN 13자리가 인쇄된 페이지\n"
                "2. 흔들림 없이 평면으로 촬영 (모서리 4개가 모두 보이게)\n"
                "3. 형광등이 직접 비치지 않도록 (글자 가림 방지)\n"
                "4. ISBN이 정 안 보이면 [검색] 탭에서 표제로 찾으세요"
            )
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
        [
            "로마자",
            "라벨 PDF",
            "자관 검색",
            "KDC 트리",
            "식별기호 ▾",
            "장서점검",
            "보고서",
            "알림",
            "납본",
            "등록번호",
            "상호대차",
            "수서 분석",
            "제적·폐기",
            "연간 통계",
        ]
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

    with sub_tabs[7]:
        st.markdown("**이용자 알림 메시지** — 연체·반납·예약·휴관 SMS/LMS/email 본문 생성")
        from kormarc_auto.librarian_helpers import notifications

        kind = st.selectbox(
            "유형",
            ["연체 (overdue)", "반납 안내 (return)", "예약 도착 (reservation)", "휴관 (closure)"],
            key="not_kind",
        )
        lib = st.text_input("도서관명", "○○도서관", key="not_lib")
        if "휴관" in kind:
            dates = st.text_input(
                "휴관일 (콤마 구분, YYYY-MM-DD)",
                "2026-05-05",
                key="not_dates",
            )
            reason = st.text_input("사유", "정기 휴관", key="not_reason")
            if st.button("메시지 생성", key="not_btn_clo"):
                msg = notifications.closure_notice(
                    library_name=lib,
                    closure_dates=[d.strip() for d in dates.split(",") if d.strip()],
                    reason=reason,
                )
                st.code(msg["sms"], language=None)
                st.text_area("LMS", msg["lms"], height=200)
                st.text_input("email subject", msg["email_subject"])
        else:
            user = st.text_input("이용자명", "", key="not_user")
            book = st.text_input("도서명", "", key="not_book")
            due = st.text_input("만기/수령기한 (YYYY-MM-DD)", "", key="not_due")
            days = st.number_input("연체일/사전알림일", 0, 365, 0, key="not_days")
            fine = st.number_input("일 연체료(원)", 0, 10000, 0, key="not_fine")
            if st.button("메시지 생성", key="not_btn") and user and book and due:
                if "연체" in kind:
                    od = days or notifications.calculate_overdue_days(due)
                    msg = notifications.overdue_notice(
                        user_name=user,
                        book_title=book,
                        due_date=due,
                        overdue_days=od,
                        library_name=lib,
                        fine_per_day=fine,
                    )
                elif "반납 안내" in kind:
                    msg = notifications.return_reminder(
                        user_name=user,
                        book_title=book,
                        due_date=due,
                        library_name=lib,
                        days_before=days or 3,
                    )
                else:  # 예약
                    msg = notifications.reservation_ready(
                        user_name=user,
                        book_title=book,
                        pickup_deadline=due,
                        library_name=lib,
                    )
                st.code(msg["sms"], language=None)
                st.text_area("LMS", msg["lms"], height=200)
                st.text_input("email subject", msg["email_subject"])

    with sub_tabs[8]:
        st.markdown("**납본 추적** — 도서관법 제20조 (발행 후 30일 내 국립중앙도서관)")
        from kormarc_auto.librarian_helpers import deposit

        action = st.radio("작업", ["기록 추가", "이력 조회", "마감일 계산"], key="dep_act")

        if action == "기록 추가":
            d_title = st.text_input("자료 표제", key="dep_title")
            d_isbn = st.text_input("ISBN/ISSN (선택)", key="dep_isbn")
            d_pub = st.text_input("발행일 (YYYY-MM-DD)", key="dep_pub")
            d_dep = st.text_input("납본일 (비우면 오늘)", key="dep_dep")
            d_copies = st.number_input("부수", 1, 10, 2, key="dep_copies")
            d_note = st.text_input("메모", key="dep_note")
            if st.button("기록", key="dep_btn") and d_title and d_pub:
                e = deposit.record_deposit(
                    title=d_title,
                    isbn=d_isbn or None,
                    publication_date=d_pub,
                    deposit_date=d_dep or None,
                    copies=int(d_copies),
                    note=d_note,
                )
                st.success(f"✓ 기록됨: {e['id']}")

        elif action == "이력 조회":
            items = deposit.list_deposits(limit=200)
            st.write(f"전체 {len(items)}건")
            for e in items[:50]:
                st.markdown(
                    f"- {e['deposit_date']} · **{e.get('title', '?')}** · "
                    f"ISBN `{e.get('isbn', '-')}` · {e['recipient']} {e['copies']}부"
                )

        else:  # 마감일 계산
            pub = st.text_input("발행일 (YYYY-MM-DD)", key="dep_calc_pub")
            if pub:
                try:
                    d = deposit.deposit_deadline(pub)
                    st.info(f"발행일 {pub} → 납본 마감일: **{d.isoformat()}** (발행 후 30일)")
                except Exception as ex:
                    st.error(f"날짜 형식 오류: {ex}")

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

    # ── 9. 등록번호 자동 부여 ────────────────────────────
    with sub_tabs[9]:
        st.markdown("**등록번호 자동 부여** — 알파스/KOLAS 워크플로우")
        from datetime import date as _date

        from kormarc_auto.librarian_helpers.registration import (
            assign_for_multivolume,
            find_missing_numbers,
            load_existing_from_index,
            next_registration_number,
        )

        reg_action = st.radio(
            "작업",
            ["다음 번호", "누락번호 점검", "다권본 일괄"],
            key="reg_action",
        )
        col_k, col_t, col_y = st.columns(3)
        with col_k:
            reg_kind = st.text_input("등록구분", "EM", key="reg_kind")
        with col_t:
            reg_turn = st.number_input("차수", 1, 99, 1, key="reg_turn")
        with col_y:
            reg_year = st.number_input(
                "연도(2자리)", 0, 99, _date.today().year % 100, key="reg_year"
            )

        existing = load_existing_from_index()
        st.caption(f"자관 인덱스 등록번호 {len(existing)}건 로드됨")

        if reg_action == "다음 번호":
            fill = st.checkbox("누락번호 우선 채움", value=True, key="reg_fill")
            if st.button("다음 번호", key="reg_next_btn"):
                n = next_registration_number(
                    existing,
                    kind=reg_kind,
                    turn=int(reg_turn),
                    year=int(reg_year),
                    fill_gap=fill,
                )
                st.success(f"다음 등록번호: **{n}**")
        elif reg_action == "누락번호 점검":
            if st.button("점검", key="reg_miss_btn"):
                gaps = find_missing_numbers(
                    existing,
                    kind=reg_kind,
                    turn=int(reg_turn),
                    year=int(reg_year),
                )
                if gaps:
                    st.warning(f"누락번호 {len(gaps)}개 발견")
                    st.code(
                        "\n".join(
                            f"{reg_kind}{int(reg_turn):02d}{int(reg_year):02d}{g:05d}"
                            for g in gaps
                        )
                    )
                else:
                    st.success("누락번호 없음 — 깔끔합니다")
        else:  # 다권본
            mv_volumes = st.number_input("권수", 2, 50, 5, key="reg_vols")
            mv_title = st.text_input("표제", "", key="reg_title")
            if st.button("다권본 등록번호 부여", key="reg_mv_btn"):
                results = assign_for_multivolume(
                    {"title": mv_title or "(미입력)"},
                    volumes=int(mv_volumes),
                    kind=reg_kind,
                    turn=int(reg_turn),
                    year=int(reg_year),
                    existing=existing,
                )
                for r in results:
                    st.markdown(
                        f"- `{r['registration_number']}` · {r['volume_label']} · "
                        f"245 ▾n {r['marc_245_n']}"
                    )

    # ── 10. 상호대차 양식 어댑터 ─────────────────────────
    with sub_tabs[10]:
        st.markdown("**상호대차 양식** — 책나래·책바다·RISS 사서대리신청 일괄업로드")
        from kormarc_auto.interlibrary.exporters import from_inventory, write_xlsx

        il_system = st.selectbox(
            "시스템",
            ["chaeknarae", "chaekbada", "riss"],
            format_func=lambda s: {
                "chaeknarae": "책나래 (장애인 자료배달)",
                "chaekbada": "책바다 (전국 상호대차)",
                "riss": "RISS (KERIS 학술)",
            }.get(s, s),
            key="il_sys",
        )
        il_isbns = st.text_area(
            "ISBN 목록 (한 줄당 1개)",
            placeholder="9788912345678\n9788998765432",
            height=140,
            key="il_isbns",
        )
        if st.button("양식 XLSX 생성", key="il_btn"):
            isbns = [x.strip() for x in il_isbns.splitlines() if x.strip()]
            if not isbns:
                st.warning("ISBN 1개 이상 입력")
            else:
                books = from_inventory(isbns)
                out_path = Path(".cache/kormarc-auto/ui-interlibrary/req.xlsx")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    p = write_xlsx(books, out_path, system=il_system)
                    st.download_button(
                        "📥 양식 XLSX 다운로드",
                        data=p.read_bytes(),
                        file_name=f"{il_system}_request.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    held = sum(1 for b in books if b.get("holding_status") == "보유")
                    st.success(f"✓ {len(books)}건 ({held}건 자관 보유 / {len(books)-held}건 미보유)")
                except Exception as e:
                    st.error(f"생성 실패: {e}")

    # ── 11. 비치희망도서 수서 분석 ───────────────────────
    with sub_tabs[11]:
        st.markdown("**비치희망도서 수서 분석** — 자관 중복 + KDC 균형 + 예상 비용")
        from kormarc_auto.acquisition.wishlist import analyze_wishlist, summarize

        ws_isbns = st.text_area(
            "희망도서 ISBN 목록 (한 줄당 1개)",
            placeholder="9788912345678\n9788998765432",
            height=140,
            key="ws_isbns",
        )
        ws_offline = st.checkbox(
            "오프라인 (자관 인덱스만)", value=False, key="ws_offline"
        )
        if st.button("분석", key="ws_btn"):
            isbns = [x.strip() for x in ws_isbns.splitlines() if x.strip()]
            if not isbns:
                st.warning("ISBN 1개 이상")
            else:
                with st.spinner(f"수서 분석 중 (약 {len(isbns)*2}초)..."):
                    items = analyze_wishlist(isbns, use_external=not ws_offline)
                summary = summarize(items)
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("총", summary["total"])
                col_b.metric("자관 보유", summary["in_holdings"])
                col_c.metric("신규 구입 후보", summary["new_purchase"])
                if summary["estimated_cost_krw"]:
                    st.metric("예상 비용", f"{summary['estimated_cost_krw']:,}원")
                if summary["balance_warnings"]:
                    st.warning("\n".join(summary["balance_warnings"]))
                with st.expander(f"개별 결과 ({len(items)}건)"):
                    for it in items:
                        flag = "✓ 보유" if it.in_holdings else "○ 신규"
                        st.markdown(
                            f"- `{it.isbn}` {flag} · **{it.title or '?'}** · "
                            f"KDC {it.kdc or '?'} · "
                            f"{f'{it.price_krw:,}원' if it.price_krw else '가격 미상'}"
                        )

    # ── 12. 제적·폐기 결재서식 ──────────────────────────
    with sub_tabs[12]:
        st.markdown("**제적·폐기 결재서식** — 도서관법 §22 + 장서개발지침 §3.2")
        from kormarc_auto.output.disposal_form import (
            DISPOSAL_REASONS,
            DisposalEntry,
            render_disposal_form_pdf,
            write_disposal_xlsx,
        )

        dis_lib = st.text_input("도서관명", "○○도서관", key="dis_lib")
        dis_period = st.text_input("심의 기간", "2026 1분기", key="dis_period")
        dis_director = st.text_input("결재자(관장)", "", key="dis_dir")
        dis_csv = st.text_area(
            "제적 자료 (한 줄: 등록번호,표제,사유코드,점검자)",
            placeholder=(
                "EM012600101,노후도서1,WORN,○○사서\n"
                "EM012600102,복본도서,DUPL,○○사서"
            ),
            height=140,
            key="dis_csv",
        )
        st.caption(
            "사유코드: " + " / ".join(f"{k}={v}" for k, v in DISPOSAL_REASONS.items())
        )

        if st.button("결재서식 PDF + 폐기목록 XLSX 생성", key="dis_btn"):
            entries: list[DisposalEntry] = []
            for line in dis_csv.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    entries.append(
                        DisposalEntry(
                            registration_number=parts[0],
                            title=parts[1],
                            reason_code=parts[2],
                            inspector=parts[3] if len(parts) > 3 else "",
                        )
                    )
            if not entries:
                st.warning("최소 1줄 (등록번호,표제,사유코드)")
            else:
                out_dir = Path(".cache/kormarc-auto/ui-disposal")
                out_dir.mkdir(parents=True, exist_ok=True)
                try:
                    pdf = render_disposal_form_pdf(
                        entries,
                        library_name=dis_lib,
                        fiscal_period=dis_period,
                        director=dis_director,
                        output_path=out_dir / "disposal.pdf",
                    )
                    xlsx = write_disposal_xlsx(entries, out_dir / "disposal.xlsx")
                    st.download_button(
                        "📥 결재서식 PDF",
                        data=pdf.read_bytes(),
                        file_name="disposal_form.pdf",
                        mime="application/pdf",
                    )
                    st.download_button(
                        "📥 폐기목록 XLSX",
                        data=xlsx.read_bytes(),
                        file_name="disposal_list.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    st.success(f"{len(entries)}건 결재서식 생성")
                except Exception as e:
                    st.error(f"생성 실패: {e}")

    # ── 13. 연간 KOLIS-NET 통계 ─────────────────────────
    with sub_tabs[13]:
        st.markdown(
            "**연간 통계** — KOLIS-NET 제출 + RISS 학교도서관 양식 (자관 인덱스 자동 집계)"
        )
        from datetime import datetime as _dt

        from kormarc_auto.output.annual_statistics import (
            build_annual_stats,
            export_to_riss_for_school,
            write_kolisnet_xlsx,
        )

        stats_lib = st.text_input("도서관명", "○○도서관", key="stats_lib")
        stats_code = st.text_input(
            "KOLIS-NET 도서관 코드 (옵션)", "", key="stats_code"
        )
        col_y, col_t = st.columns(2)
        with col_y:
            stats_year = st.number_input(
                "통계연도", 2020, 2100, _dt.now().year, key="stats_year"
            )
        with col_t:
            stats_target = st.selectbox(
                "양식", ["KOLIS-NET (공공)", "RISS (학교도서관)"], key="stats_target"
            )

        st.markdown("**사서 보정값 (선택 입력)**")
        col_l, col_v, col_m = st.columns(3)
        with col_l:
            stats_loans = st.number_input("연간 대출", 0, 10000000, 0, key="stats_loans")
        with col_v:
            stats_visits = st.number_input("이용자 방문", 0, 10000000, 0, key="stats_visits")
        with col_m:
            stats_members = st.number_input("회원 수", 0, 10000000, 0, key="stats_members")

        if st.button("연간 통계 XLSX 생성", key="stats_btn"):
            s = build_annual_stats(
                year=int(stats_year),
                library_name=stats_lib,
                library_code=stats_code,
                overrides={
                    "loans_total": int(stats_loans),
                    "visits_total": int(stats_visits),
                    "members_total": int(stats_members),
                },
            )
            out_dir = Path(".cache/kormarc-auto/ui-stats")
            out_dir.mkdir(parents=True, exist_ok=True)
            try:
                if stats_target.startswith("KOLIS"):
                    xlsx = write_kolisnet_xlsx(
                        s, out_dir / f"kolisnet_{int(stats_year)}.xlsx"
                    )
                    fname = f"kolisnet_{int(stats_year)}.xlsx"
                else:
                    xlsx = export_to_riss_for_school(
                        s, out_dir / f"riss_{int(stats_year)}.xlsx"
                    )
                    fname = f"riss_{int(stats_year)}.xlsx"
                st.download_button(
                    "📥 통계 XLSX 다운로드",
                    data=xlsx.read_bytes(),
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                st.success(
                    f"총 장서 {s.holdings_total}권 · KDC 분포 {s.holdings_by_kdc}"
                )
            except Exception as e:
                st.error(f"생성 실패: {e}")


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

    # Part G Step 2·8 (DECISIONS 6dim+7) — 인증 가드 (st.set_page_config 직후, 본 콘텐츠 직전)
    from kormarc_auto.ui.auth import require_login

    require_login()

    st.title("📚 kormarc-auto")
    st.caption(f"한국 도서관용 KORMARC 자동 생성 · v{__version__}")

    st.info(
        "✨ **처음이신가요?** 신규 가입자는 **50건 무료**입니다. "
        "아래 [ISBN] 탭에 ISBN 13자리만 넣으면 5초 안에 KORMARC가 생성됩니다.",
        icon="👋",
    )
    st.caption(
        "**자관 .mrc 99.82% 정합 검증 완료** ★ "
        "다른 자관 049 prefix 자동 발견 → `streamlit run src/kormarc_auto/ui/prefix_discover_app.py`"
    )
    with st.expander("📖 5분 가이드 (처음 사용 시 권장)"):
        st.markdown(
            "**1. ISBN 단건** — 13자리 ISBN 입력 → KORMARC 생성  \n"
            "**2. 검색** — 표제/저자로 후보 보고 선택  \n"
            "**3. 사진** — 표지·판권지 1~3장 (폰 카메라 OK)  \n"
            "**4. 일괄** — ISBN 여러 개를 한 번에  \n\n"
            "결과 카드의 KDC·주제명은 **AI 추천** 후보입니다. "
            "사서가 검토 후 사용하세요. KOLAS 반입 폴더에 .mrc 파일을 넣으면 자동 인식."
        )

    with st.sidebar:
        st.markdown("### 설정")
        agency = st.text_input(
            "우리 도서관 부호",
            "OURLIB",
            key="agency_input",
            help="KOLAS 관리자 화면의 도서관 식별부호 (KORMARC 040 ▾a). 모르시면 OURLIB 그대로 두세요.",
        )
        st.markdown("---")
        st.markdown("### AI 추천 보조 (선택)")
        st.caption("⚙ KDC·주제명 AI 자동 추천을 쓰려면 입력. 안 입력해도 ISBN 기능은 100% 작동합니다.")
        ai_key = st.text_input(
            "AI 추천 보조 키 (선택)",
            type="password",
            placeholder="sk-ant-api03-...",
            key="user_anthropic_key",
            help="https://console.anthropic.com/settings/keys 에서 발급. 비용 본인 부담 (권당 약 0.5원).",
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
        st.markdown("### 내 사용량")
        usage_key = st.text_input(
            "내 API 키 (kma_...) — 가입 후 받은 키 입력",
            type="password",
            key="usage_api_key",
            help="가입 시 발급된 kma_로 시작하는 키. 이 키 없이도 PC에서는 모든 도구가 작동하지만, 무료 잔여·결제 안내는 키가 있어야 표시됩니다.",
        )
        if usage_key and len(usage_key) >= 12:
            try:
                from kormarc_auto.server.usage import can_consume

                _, status = can_consume(usage_key)
                remaining = status.get("remaining", 0)
                used = status.get("used", 0)
                quota = status.get("free_quota", 50)
                col_u, col_r = st.columns(2)
                col_u.metric("사용", used)
                col_r.metric("잔여 무료", remaining)
                progress = min(used / quota, 1.0) if quota else 0
                st.progress(progress)
                if remaining <= 0:
                    st.error(
                        f"무료 한도 {quota}건 초과 — 결제 안내를 확인해 주세요. "
                        f"권당 {PRICE_PER_RECORD_KRW:,}원 또는 월 정액."
                    )
                    st.markdown(f"[💳 결제 안내]({PAYMENT_INFO_URL})")
                elif remaining <= 5:
                    st.warning(
                        f"⏳ 무료 잔여 **{remaining}건**. 곧 결제 전환이 필요합니다. "
                        f"[가격 안내]({PAYMENT_INFO_URL})"
                    )
                elif remaining <= 10:
                    st.info(f"📊 무료 잔여 {remaining}건. 미리 결제 옵션을 살펴보세요.")
            except Exception:
                st.caption("⚠ 사용량 조회 실패 (서버 비활성 또는 키 미등록).")
        st.markdown("---")
        st.markdown("### 가격 안내")
        st.markdown(f"- 권당 **{PRICE_PER_RECORD_KRW:,}원**")
        st.markdown("- 신규 50건 무료 체험")
        st.markdown(f"- [가격 페이지]({PAYMENT_INFO_URL})")
        st.markdown("---")
        st.markdown("### 약관·개인정보")
        _docs_base = (
            "https://github.com/okwhr/kormarc-auto/blob/main/docs"
        )
        st.markdown(f"- [이용약관]({_docs_base}/terms-of-service.md)")
        st.markdown(f"- [개인정보 처리방침]({_docs_base}/privacy-policy.md)")
        st.caption("개인정보보호법 §35-3·§36에 따라 본인 데이터 다운로드/삭제 권리가 있습니다.")
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
