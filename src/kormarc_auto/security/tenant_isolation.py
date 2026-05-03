"""멀티테넌시 격리 — M5 (PIPA + 자관 데이터 안전).

PO 명령 (Part 87 §11 위험 #5): "PIPA 2026.09.11 시행 = 매출 10% 과징금"
도서관 A 데이터가 도서관 B로 새지 않도록 격리.

작동 모델:
1. ContextVar = 요청별 tenant_id 자동 전파 (FastAPI dependency)
2. assert_tenant_match = 누락 시 즉시 raise (silent leak 방지)
3. tenant_scoped 데코레이터 = 함수에 tenant 검증 강제
4. audit_log = 모든 tenant 전환 기록

사용:
    set_current_tenant("LIB001")
    # 이후 모든 query 자동 tenant 필터
    @tenant_scoped
    def get_records(): ...

근거:
- PIPA §29-2 안전조치
- 카카오 151억 과징금 학습 (Part 87 §9.9)
- 헌법 §0 (사서 데이터 안전 = 결제 의향 직결)
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any, TypeVar

T = TypeVar("T")

# 요청별 tenant_id 전파 (None = unset = 거부)
_current_tenant: ContextVar[str | None] = ContextVar("current_tenant", default=None)


class TenantIsolationError(Exception):
    """tenant 격리 위반."""


class TenantNotSetError(TenantIsolationError):
    """tenant_id 미설정 + 격리 영역 접근 시도."""


class TenantMismatchError(TenantIsolationError):
    """tenant_id 불일치 (cross-tenant 접근 시도)."""


def set_current_tenant(tenant_id: str | None) -> None:
    """현재 요청의 tenant 설정 (FastAPI dependency·middleware에서 호출)."""
    _current_tenant.set(tenant_id)


def get_current_tenant() -> str | None:
    """현재 요청의 tenant 조회. None = 미설정."""
    return _current_tenant.get()


def require_tenant() -> str:
    """tenant 필수 — 미설정 시 raise."""
    tenant = _current_tenant.get()
    if tenant is None:
        raise TenantNotSetError(
            "tenant_id 미설정·격리 영역 접근 시도. "
            "FastAPI dependency 또는 set_current_tenant() 호출 필요."
        )
    return tenant


def assert_tenant_match(record_tenant_id: str) -> None:
    """레코드의 tenant_id가 현재 요청과 일치 검증. 불일치 = raise."""
    current = require_tenant()
    if record_tenant_id != current:
        raise TenantMismatchError(
            f"cross-tenant 접근 시도: current={current} ≠ record={record_tenant_id}"
        )


def tenant_scoped(func: Callable[..., T]) -> Callable[..., T]:
    """함수에 tenant 검증 강제 (decorator).

    사용:
        @tenant_scoped
        def get_records():
            tenant = require_tenant()  # 자동 가져옴
            return db.query(...).filter(tenant_id=tenant)
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        require_tenant()  # 미설정 시 raise
        return func(*args, **kwargs)

    return wrapper


def filter_by_tenant(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """records 리스트에서 현재 tenant만 필터 (방어적 필터·SQL WHERE 보강)."""
    current = require_tenant()
    return [r for r in records if r.get("tenant_id") == current]


# Tenant 전환 audit log (PIPA 안전조치)
_tenant_audit: list[dict[str, Any]] = []


def log_tenant_switch(from_tenant: str | None, to_tenant: str | None, reason: str = "") -> None:
    """tenant 전환 기록 (audit_log 통합 시 hash chain)."""
    from datetime import UTC, datetime

    _tenant_audit.append(
        {
            "ts": datetime.now(UTC).isoformat(),
            "from": from_tenant,
            "to": to_tenant,
            "reason": reason,
        }
    )


def get_tenant_audit_log(limit: int = 100) -> list[dict[str, Any]]:
    """audit log 조회 (최근 N건)."""
    return _tenant_audit[-limit:]


def clear_tenant() -> None:
    """tenant unset (요청 종료 시·테스트 cleanup)."""
    _current_tenant.set(None)


__all__ = [
    "TenantIsolationError",
    "TenantMismatchError",
    "TenantNotSetError",
    "assert_tenant_match",
    "clear_tenant",
    "filter_by_tenant",
    "get_current_tenant",
    "get_tenant_audit_log",
    "log_tenant_switch",
    "require_tenant",
    "set_current_tenant",
    "tenant_scoped",
]
