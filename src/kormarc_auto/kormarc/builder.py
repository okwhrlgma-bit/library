"""BookData (통합 dict) → pymarc.Record 변환."""

from __future__ import annotations

import logging
from typing import Any

from pymarc import Field, Indicators, Record, Subfield

from kormarc_auto.kormarc.mapping import build_008, normalize_isbn, parse_publication_place

logger = logging.getLogger(__name__)


def build_kormarc_record(
    book_data: dict[str, Any],
    *,
    cataloging_agency: str = "OURLIB",
    cataloging_lang: str = "kor",
    auto_validate: bool = True,
) -> Record:
    """BookData dict를 pymarc Record로 변환.

    Args:
        book_data: aggregator.aggregate_by_isbn() 결과
        cataloging_agency: 040 ▾a 우리 도서관 부호 (기관 설정)
        cataloging_lang: 040 ▾b 사용 언어
        auto_validate: True면 빌드 직후 validate_record_full 호출 + logger.warning
                       (default True). False면 검증 생략 (테스트·골든 데이터셋 빌드 시).

    Returns:
        pymarc.Record (UTF-8, KORMARC 통합서지용 호환)
    """
    record = Record(force_utf8=True, leader="00000nam a2200000   4500")

    # 008 — 부호화 정보 (40자리)
    place = parse_publication_place(book_data.get("publisher")) or book_data.get(
        "publication_place"
    )
    field_008 = build_008(
        publication_year=book_data.get("publication_year"),
        language=cataloging_lang,
        publication_place=place,
    )
    record.add_field(Field(tag="008", data=field_008))

    # 020 — ISBN
    isbn = normalize_isbn(book_data.get("isbn"))
    if isbn:
        subfields = [Subfield(code="a", value=isbn)]
        if book_data.get("additional_code"):
            subfields.append(Subfield(code="g", value=str(book_data["additional_code"])))
        if book_data.get("price"):
            subfields.append(Subfield(code="c", value=f"₩{book_data['price']}"))
        record.add_field(Field(tag="020", indicators=Indicators(" ", " "), subfields=subfields))

    # 040 — 목록작성기관
    record.add_field(
        Field(
            tag="040",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value=cataloging_agency),
                Subfield(code="b", value=cataloging_lang),
                Subfield(code="c", value=cataloging_agency),
            ],
        )
    )

    # 056 — KDC
    if book_data.get("kdc"):
        record.add_field(
            Field(
                tag="056",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="a", value=str(book_data["kdc"])),
                    Subfield(code="2", value="6"),  # 6판
                ],
            )
        )

    # 082 — DDC (있으면)
    if book_data.get("ddc"):
        record.add_field(
            Field(
                tag="082",
                indicators=Indicators("0", " "),
                subfields=[Subfield(code="a", value=str(book_data["ddc"]))],
            )
        )

    # 100 — 주표목 (개인저자)
    author = book_data.get("author")
    primary_author = _split_first_author(author) if author else ""
    if primary_author:
        record.add_field(
            Field(
                tag="100",
                indicators=Indicators("1", " "),
                subfields=[Subfield(code="a", value=primary_author)],
            )
        )

    # 245 — 표제와 책임표시사항 (필수)
    # 관제(冠題, 본표제 앞 수식어) 한국 특수 처리:
    #   "(개정증보판) 작별하지 않는다" 같은 원괄호 표기
    #   2지시기호 = 관제 길이 + 1 (정렬 무시 글자수)
    title = book_data.get("title") or "표제 미상"
    crown = book_data.get("crown_title") or ""  # 관제 (없으면 빈)
    if crown:
        full_title = f"({crown}) {title}"
        ind2 = str(min(9, len(crown) + 3))  # "(관제) " 길이 = len + 3
    else:
        full_title = title
        ind2 = "0"
    title_subfields = [Subfield(code="a", value=full_title)]
    if book_data.get("subtitle"):
        title_subfields.append(Subfield(code="b", value=f": {book_data['subtitle']}"))
    if author:
        title_subfields.append(Subfield(code="c", value=f"/ {author}"))
    # 1지시기호: 1=주표목 있음(100), 0=없음
    ind1 = "1" if primary_author else "0"
    record.add_field(
        Field(tag="245", indicators=Indicators(ind1, ind2), subfields=title_subfields)
    )

    # 090 청구기호 (대학도서관용, 옵션)
    if book_data.get("call_number_090"):
        cn = book_data["call_number_090"]
        sf_090: list[Subfield] = []
        if isinstance(cn, dict):
            if cn.get("classification"):
                sf_090.append(Subfield(code="a", value=str(cn["classification"])))
            if cn.get("book_mark"):
                sf_090.append(Subfield(code="b", value=str(cn["book_mark"])))
        else:
            sf_090.append(Subfield(code="a", value=str(cn)))
        if sf_090:
            record.add_field(Field(tag="090", indicators=Indicators(" ", " "), subfields=sf_090))

    # 264 — 발행/제작 (RDA)
    pub_subfields = []
    if place:
        pub_subfields.append(Subfield(code="a", value=f"{place} :"))
    if book_data.get("publisher"):
        pub_subfields.append(Subfield(code="b", value=f"{book_data['publisher']},"))
    if book_data.get("publication_year"):
        pub_subfields.append(Subfield(code="c", value=str(book_data["publication_year"])))
    if pub_subfields:
        record.add_field(
            Field(tag="264", indicators=Indicators(" ", "1"), subfields=pub_subfields)
        )

    # 300 — 형태사항
    extent_subfields = []
    if book_data.get("pages"):
        pages = str(book_data["pages"]).strip()
        if not pages.endswith("p.") and pages.replace(" ", "").isdigit():
            pages = f"{pages} p."
        extent_subfields.append(Subfield(code="a", value=pages))
    if book_data.get("book_size"):
        size = str(book_data["book_size"]).strip()
        if not size.endswith("cm"):
            size = f"{size} cm" if size.replace(" ", "").isdigit() else size
        extent_subfields.append(Subfield(code="c", value=size))
    if extent_subfields:
        record.add_field(
            Field(tag="300", indicators=Indicators(" ", " "), subfields=extent_subfields)
        )

    # 336/337/338 — RDA 콘텐츠/매체/캐리어 유형 (도서 기본)
    record.add_field(
        Field(
            tag="336",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="text"), Subfield(code="2", value="rdacontent")],
        )
    )
    record.add_field(
        Field(
            tag="337",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="unmediated"), Subfield(code="2", value="rdamedia")],
        )
    )
    record.add_field(
        Field(
            tag="338",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="volume"), Subfield(code="2", value="rdacarrier")],
        )
    )

    # 490 — 총서사항
    if book_data.get("series_title"):
        series_subfields = [Subfield(code="a", value=str(book_data["series_title"]))]
        if book_data.get("series_no"):
            series_subfields.append(Subfield(code="v", value=str(book_data["series_no"])))
        record.add_field(
            Field(tag="490", indicators=Indicators("1", " "), subfields=series_subfields)
        )

    # 505 — 내용주기 (목차)
    if book_data.get("toc"):
        toc_clean = str(book_data["toc"]).replace("\n", " -- ")[:2000]
        record.add_field(
            Field(
                tag="505",
                indicators=Indicators("0", " "),
                subfields=[Subfield(code="a", value=toc_clean)],
            )
        )

    # 520 — 요약/초록
    if book_data.get("summary"):
        summary_clean = str(book_data["summary"])[:2000]
        record.add_field(
            Field(
                tag="520",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=summary_clean)],
            )
        )

    # 041 — 본문 언어 (다국어 도서)
    languages = book_data.get("languages")
    if languages and isinstance(languages, list) and len(languages) > 1:
        lang_subfields = [Subfield(code="a", value=lang) for lang in languages[:5]]
        record.add_field(
            Field(tag="041", indicators=Indicators("0", " "), subfields=lang_subfields)
        )

    # 246 — 변형표제 (표지·이전 제목·로마자)
    if book_data.get("alternative_title"):
        record.add_field(
            Field(
                tag="246",
                indicators=Indicators("3", " "),
                subfields=[Subfield(code="a", value=str(book_data["alternative_title"]))],
            )
        )

    # 250 — 판차
    if book_data.get("edition"):
        record.add_field(
            Field(
                tag="250",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=str(book_data["edition"]))],
            )
        )

    # 500 — 일반주기
    if book_data.get("general_note"):
        record.add_field(
            Field(
                tag="500",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=str(book_data["general_note"])[:1000])],
            )
        )

    # 504 — 서지·색인 주기
    if book_data.get("bibliography_note"):
        record.add_field(
            Field(
                tag="504",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=str(book_data["bibliography_note"])[:500])],
            )
        )

    # 856 — 전자자료 URL
    if book_data.get("url"):
        record.add_field(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),
                subfields=[
                    Subfield(code="u", value=str(book_data["url"])),
                    Subfield(code="y", value=str(book_data.get("url_label") or "전자자료")),
                ],
            )
        )

    # 653 — 비통제 색인어 (도정나 키워드)
    keywords = book_data.get("keywords", [])
    if keywords:
        kw_subfields = [Subfield(code="a", value=k) for k in keywords[:10]]
        record.add_field(
            Field(tag="653", indicators=Indicators(" ", " "), subfields=kw_subfields)
        )

    # 700 — 부출표목 (역자, 공동저자) — author 문자열에 ';' 또는 ',' 다수면 분리
    additional_authors = _split_additional_authors(author or "")
    for add_author in additional_authors:
        record.add_field(
            Field(
                tag="700",
                indicators=Indicators("1", " "),
                subfields=[Subfield(code="a", value=add_author)],
            )
        )

    # 950 — 가격 (한국 특수 필드)
    if book_data.get("price"):
        record.add_field(
            Field(
                tag="950",
                indicators=Indicators("0", " "),
                subfields=[Subfield(code="b", value=f"₩{book_data['price']}")],
            )
        )

    # ── Phase 1.5 자료유형 분기: ebook·ejournal·audiobook·multimedia·thesis
    # detect_material_type() + book_data에 자료유형 특유 키가 있을 때만 분기.
    # 단행본 기본 케이스는 영향 X (모든 추가 필드는 옵션).
    _apply_phase15_fields(record, book_data)

    # 빌드 직후 KORMARC 2023.12 + M/A/O 자동 검증 (logger.warning, raise X)
    if auto_validate:
        # 순환 import 회피 — 함수 내부 import
        from kormarc_auto.kormarc.validator import validate_record_full

        issues = validate_record_full(record, book_data)
        if issues:
            logger.warning(
                "KORMARC 빌드 검증 위반 %d건 (ISBN=%s): %s%s",
                len(issues),
                book_data.get("isbn", "?"),
                issues[:3],
                "..." if len(issues) > 3 else "",
            )

    return record


def _apply_phase15_fields(record: Record, book_data: dict[str, Any]) -> None:
    """Phase 1.5 자료유형 모듈 자동 통합 (ebook·ejournal·audiobook·multimedia·thesis).

    detect_material_type()로 감지 + book_data에 자료유형 특유 키 (url·issn·narrator·
    runtime·degree)가 있으면 해당 모듈의 build_*_fields() 결과를 record에 append.

    중복 회피: builder가 이미 추가한 필드 태그(856 등)는 자료유형 모듈이 책임.
    단순화 위해 Phase 1.5 분기에 진입하면 사전에 추가된 동일 태그 제거.
    """
    from kormarc_auto.kormarc.material_type import detect_material_type

    material_type = book_data.get("material_type") or detect_material_type(book_data)
    extra_fields: list[Field] = []

    if material_type == "ebook" or book_data.get("format") in ("PDF", "EPUB", "HWP"):
        from kormarc_auto.kormarc.ebook import build_ebook_fields

        extra_fields.extend(build_ebook_fields(book_data))
    elif material_type == "audiobook" or book_data.get("narrator"):
        from kormarc_auto.kormarc.audiobook import build_audiobook_fields

        extra_fields.extend(build_audiobook_fields(book_data))
    elif material_type in ("dvd", "multimedia") or book_data.get("runtime"):
        from kormarc_auto.kormarc.multimedia import build_multimedia_fields

        extra_fields.extend(build_multimedia_fields(book_data))
    elif material_type in ("serial_current", "serial_ceased", "ejournal") or book_data.get("issn"):
        from kormarc_auto.kormarc.ejournal import build_ejournal_fields

        extra_fields.extend(build_ejournal_fields(book_data))
    elif material_type == "thesis" or book_data.get("degree"):
        from kormarc_auto.kormarc.thesis import build_thesis_fields

        extra_fields.extend(build_thesis_fields(book_data))

    if not extra_fields:
        return

    # 중복 태그 정리: 자료유형 모듈이 채우는 태그는 사전 856·538·022·300 등.
    # 핵심 식별 (008·020·245·100·700·056·082·040·950)은 보존, 자료유형 책임 태그만 제거.
    type_owned_tags = {f.tag for f in extra_fields}
    keep_tags_priority = {"008", "020", "040", "056", "082", "100", "245", "264", "490", "700", "950"}
    drop_targets = type_owned_tags - keep_tags_priority

    if drop_targets:
        for tag in drop_targets:
            for existing in list(record.get_fields(tag)):
                record.remove_field(existing)

    for f in extra_fields:
        record.add_field(f)


def _split_first_author(author_field: str) -> str:
    """저자 문자열에서 대표(첫) 저자만 추출."""
    for sep in [";", ",", " 외", " 외 "]:
        if sep in author_field:
            return author_field.split(sep)[0].strip()
    return author_field.strip()


def _split_additional_authors(author_field: str) -> list[str]:
    """대표 저자 외 부출 후보 추출. 최대 3명."""
    parts = [p.strip() for p in author_field.replace(",", ";").split(";")]
    return [p for p in parts[1:4] if p]
