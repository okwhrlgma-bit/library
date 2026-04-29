"""Streamlit standalone — 자관 049 prefix 자동 발견 (사서 친화 GUI).

사용:
    streamlit run src/kormarc_auto/ui/prefix_discover_app.py

PILOT 1주차 사서가 GUI 1 클릭으로 본인 도서관 .mrc → 049 prefix 자동 발견 →
config.yaml snippet 즉시 복사. PowerShell·CLI 미숙한 사서도 5분 도입.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from kormarc_auto.librarian_helpers.prefix_discovery import PrefixDiscoverer


def _setup() -> None:
    st.set_page_config(
        page_title="자관 049 prefix 자동 발견",
        page_icon="📚",
        layout="centered",
    )


def main() -> None:
    _setup()
    st.title("자관 049 prefix 자동 발견")
    st.markdown(
        "**자관 .mrc 디렉토리 경로만 입력하세요.** "
        "049 ▾l 등록번호 prefix가 자동 출력됩니다. "
        "[자관 사례](https://github.com/okwhrlgma-bit/library): "
        "EQ(75.5%) · CQ(22.8%) · WQ(1.7%) → 99.82% 정합 도달."
    )

    st.divider()

    directory = st.text_input(
        "자관 .mrc 디렉토리 경로",
        value="D:/내를건너서 숲으로 도서관/수서",
        help="KOLAS·알파스 출력 .mrc 파일이 있는 폴더. 재귀 검색.",
    )

    threshold = st.slider(
        "권장 임계값 (%)",
        min_value=0.5,
        max_value=10.0,
        value=1.0,
        step=0.5,
        help="이 비율 이상 등장하는 prefix만 권장. 자관 사례 1.0% 권장.",
    )

    if st.button("자동 발견 실행", type="primary", use_container_width=True):
        path = Path(directory)
        if not path.exists():
            st.error(f"디렉토리 없음: {directory}")
            return

        with st.spinner("분석 중... (.mrc 파일 인코딩 자동 감지)"):
            discoverer = PrefixDiscoverer(threshold_pct=threshold)
            summary = discoverer.scan(path)

        if summary.total_records == 0:
            st.warning(".mrc 파일 0건 또는 파싱 실패. 디렉토리 다시 확인.")
            return

        st.success(f"분석 완료 — 총 {summary.total_records:,}건 레코드")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("발견된 prefix 수", len(summary.prefix_counts))
        with col2:
            st.metric("권장 prefix 수", len(summary.recommended_prefixes))

        st.subheader("049 prefix 분포")
        for prefix, count in sorted(summary.prefix_counts.items(), key=lambda x: -x[1]):
            pct = count / summary.total_records * 100
            marker = "  ★ 권장" if prefix in summary.recommended_prefixes else ""
            st.write(f"- **{prefix}**: {count:,}건 ({pct:.1f}%){marker}")

        st.divider()
        st.subheader("config.yaml snippet (복사 → 붙여넣기)")
        st.code(summary.to_yaml_snippet(), language="yaml")

        st.info(
            "**다음 단계**: 위 snippet을 `config.yaml`에 붙여넣기 → "
            "`scripts/validate_real_mrc.py --dir <폴더>` 실행 → "
            "99% 정합 확인 → PILOT 1주차 시작."
        )


if __name__ == "__main__":
    main()
