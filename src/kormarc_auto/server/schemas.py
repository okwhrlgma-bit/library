"""FastAPI 요청·응답 Pydantic 모델."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IsbnRequest(BaseModel):
    isbn: str = Field(..., description="13자리 ISBN", min_length=10, max_length=20)
    agency: str = Field("OURLIB", description="040 ▾a 우리 도서관 부호")


class SearchRequest(BaseModel):
    query: str = Field(..., description="검색어 (표제·저자·키워드)", min_length=1)
    limit: int = Field(10, ge=1, le=30, description="최대 결과 수")


class ValidateRequest(BaseModel):
    mrc_base64: str = Field(..., description=".mrc 파일을 base64 인코딩한 문자열")


class KormarcResponse(BaseModel):
    ok: bool
    isbn: str | None = None
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    publication_year: str | None = None
    confidence: float = 0.0
    sources: list[str] = []
    source_map: dict[str, str] = {}
    attributions: list[str] = []
    kdc_candidates: list[dict[str, Any]] = []
    subject_candidates: list[dict[str, Any]] = []
    field_count: int = 0
    validation_errors: list[str] = []
    mrc_base64: str | None = None
    marcxml: str | None = None
    usage: dict[str, Any] | None = None
    warnings: list[str] = []


class SearchResponse(BaseModel):
    ok: bool
    query: str
    candidates: list[dict[str, Any]]
    usage: dict[str, Any] | None = None


class ValidationResponse(BaseModel):
    ok: bool
    record_count: int
    errors_per_record: list[list[str]]


class HealthResponse(BaseModel):
    ok: bool
    version: str
    service: str = "kormarc-auto"


class UsageResponse(BaseModel):
    key_hash: str
    free_quota: int
    used: int
    remaining: int
    price_per_record_krw: int
    payment_url: str | None = None


class SignupRequest(BaseModel):
    email: str = Field(..., description="사서 이메일", min_length=5, max_length=200)
    library_name: str | None = Field(None, description="도서관명 (옵션)", max_length=200)


class SignupResponse(BaseModel):
    api_key: str
    free_quota: int
    library_name: str | None = None
    ui_url: str
    api_url: str
    payment_url: str
    terms_url: str | None = None
    privacy_url: str | None = None
    kakao_channel_url: str | None = None
    welcome_message: str | None = None
    expires_at: int | None = None
    next_steps: list[str] = []
