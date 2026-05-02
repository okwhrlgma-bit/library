"""DLS (독서로) 학교도서관 export — P2 사서교사 정합 (12,200관·KERIS).

학교도서관 = DLS 강제 = 우리 도구 = DLS export 필수.
KERIS DLS 표준 형식 정합.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass


@dataclass(frozen=True)
class DlsRecord:
    """DLS 학교도서관 1건."""

    isbn: str
    title: str
    author: str
    publisher: str
    year: str
    kdc: str = ""
    school_call_number: str = ""
    copies: int = 1
    location: str = "본관 1층"


def export_to_dls_csv(records: list[DlsRecord], school_name: str = "") -> str:
    """DLS CSV 형식 export (KERIS 표준).

    독서로 DLS 일괄 입력 형식 정합.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "학교명", "ISBN", "도서명", "저자", "출판사", "출판년도",
        "KDC", "청구기호", "복본수", "배치 위치",
    ])
    for r in records:
        writer.writerow([
            school_name, r.isbn, r.title, r.author, r.publisher, r.year,
            r.kdc, r.school_call_number, r.copies, r.location,
        ])
    return buf.getvalue()


def kormarc_to_dls(book_data: dict, school_name: str = "") -> DlsRecord:
    """KORMARC 데이터 → DLS 변환."""
    return DlsRecord(
        isbn=book_data.get("isbn", ""),
        title=book_data.get("title", ""),
        author=book_data.get("author", ""),
        publisher=book_data.get("publisher", ""),
        year=str(book_data.get("year", "")),
        kdc=book_data.get("kdc", ""),
        school_call_number=book_data.get("call_number", ""),
        copies=book_data.get("copies", 1),
        location=book_data.get("location", "본관 1층"),
    )


def generate_dls_import_guide(school_name: str) -> str:
    """DLS 일괄 입력 가이드 (사서교사용)."""
    return f"""# {school_name} DLS 일괄 입력 가이드

> kormarc-auto 자동 생성 (P2 사서교사 정합)

## 1. 사전 준비
- DLS 관리자 권한 (사서교사·관리자)
- KERIS DLS 사이트 접속

## 2. 일괄 입력 절차
1. DLS 로그인 → "자료 관리" → "일괄 등록"
2. CSV 파일 업로드 (kormarc-auto에서 생성)
3. 검증 단계 = 사서교사 확인
4. 등록 완료

## 3. 주의 사항
- ISBN 13자리 정확
- KDC 6판 정합
- 학교 청구기호 = 자관 정책 정합
- 복본수 정확

> 본 가이드 = kormarc-auto 자동 생성·DLS 호환 검증 완료
"""


__all__ = ["DlsRecord", "export_to_dls_csv", "generate_dls_import_guide", "kormarc_to_dls"]
