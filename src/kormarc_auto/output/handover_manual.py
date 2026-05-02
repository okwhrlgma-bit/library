"""인계 매뉴얼 자동 생성 — 다음 계약직 사서를 위한.

Part 50 발견: 영업 자료 30건 (P4 1년 계약직 사서) ↔ 코드 불일치 해결.

본인 사용 패턴·자관 prefix·즐겨찾기·KOLAS 결제 갱신 일정 자동 export.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class HandoverManualData:
    """인계 매뉴얼 데이터."""

    library_name: str  # 자관 이름 (자관 익명화 정책: PO 동의 후만)
    librarian_name: str
    contract_start: date
    contract_end: date
    next_librarian_start: date | None = None
    self_prefix: list[str] = field(default_factory=list)  # EQ·CQ·WQ 등
    favorite_kdc: list[str] = field(default_factory=list)
    favorite_special_locations: list[str] = field(default_factory=list)  # 별치기호
    monthly_records_avg: int = 0
    total_records: int = 0
    notes: str = ""
    next_renewal_date: date | None = None  # 자치구 결제 갱신 일정
    contact_email: str = ""


def generate_handover_manual_markdown(data: HandoverManualData) -> str:
    """다음 계약직 사서를 위한 인계 매뉴얼 Markdown 생성.

    P4 1년 계약직 사서 페인 직접 해결:
    - 다음 계약직 첫 1주 학습 시간: 1주 → 5분
    - 자관 prefix·KDC·별치 등 노하우 자동 인계
    - 자치구 결제 갱신 일정 누락 방지
    """
    contract_period = (data.contract_end - data.contract_start).days
    next_start_str = (
        f'{data.next_librarian_start.year}년 {data.next_librarian_start.month}월 {data.next_librarian_start.day}일'
        if data.next_librarian_start
        else "(미정)"
    )

    prefix_lines = "\n".join(f"- `{p}`" for p in data.self_prefix) or "- (사용 prefix 없음)"
    kdc_lines = "\n".join(f"- {k}" for k in data.favorite_kdc) or "- (자주 사용한 KDC 없음)"
    special_lines = "\n".join(f"- `{s}`" for s in data.favorite_special_locations) or "- (별치기호 사용 X)"

    return f"""# kormarc-auto 인계 매뉴얼

> {data.library_name} 도서관
> 작성: {data.librarian_name} 선생님 ({date.today().strftime('%Y년 %m월 %d일')})

---

## 0. 다음 선생님께

안녕하세요. 이 도서관에서 kormarc-auto를 사용해온 {data.librarian_name} 선생님입니다.
1년 계약 종료에 따라 다음 사서 선생님께 인계 매뉴얼을 남깁니다.

이 도서관에서 5분 안에 동일한 환경을 이어가실 수 있어요.

---

## 1. 본인 사용 기간 요약

| 항목 | 내용 |
|------|------|
| 사용 기간 | {f'{data.contract_start.year}년 {data.contract_start.month}월 {data.contract_start.day}일'} ~ {f'{data.contract_end.year}년 {data.contract_end.month}월 {data.contract_end.day}일'} ({contract_period}일) |
| 누적 처리 권수 | {data.total_records:,}권 |
| 월 평균 처리 | {data.monthly_records_avg:,}권 |
| 다음 사서 시작일 | {next_start_str} |

---

## 2. 자관 prefix 설정 (049 필드)

본 도서관에서 사용하는 자관 등록번호 prefix:

{prefix_lines}

→ kormarc-auto 설정에서 자동 적용됩니다. 신규 등록 시 자동 prefix.

---

## 3. 자주 사용한 KDC 분류

이 도서관 장서 특성상 자주 등장하는 분류:

{kdc_lines}

→ 신간 등록 시 우선 후보로 자동 표시됩니다.

---

## 4. 별치기호 (049 ▾f)

본 도서관 별치 운영 기호:

{special_lines}

→ 자관 청구기호 자동 생성 시 옵션으로 표시됩니다.

---

## 5. 자치구 결제 갱신 일정 ⭐

| 항목 | 내용 |
|------|------|
| 다음 갱신 예정일 | {f'{data.next_renewal_date.year}년 {data.next_renewal_date.month}월 {data.next_renewal_date.day}일' if data.next_renewal_date else "(자치구 도서관사업소 확인)"} |
| 결제 주체 | 자치구 도서관사업소 |
| 결제 양식 | 자치구 표준 양식 (자동 생성 가능) |

→ **갱신 일자 1개월 전 알림이 자동 발송됩니다.** 다음 사서 선생님께 인계됩니다.

---

## 6. 첫 1주 권장 워크플로

### Day 1
- kormarc-auto 로그인 (인계받은 계정 또는 신규)
- 본인 페르소나 선택 ("1년 계약직 사서")
- 자관 prefix 설정 확인 (위 §2)

### Day 2~3
- 신간 ISBN 입력 1~5건 시범
- 권당 시간 측정 차트 확인 (오늘부터 본인 통계)
- 5분 cheatsheet 다시 읽기

### Day 4~7
- 본인 워크플로 정착 (오전 수서·오후 정리)
- 즐겨찾기·템플릿 본인 화 (위 §3·§4 기반)
- 자치구 결제 갱신 일정 확인 (위 §5)

---

## 7. 막힐 때 — 도움말

| 상황 | 해결 |
|------|------|
| ISBN 인식 안 됨 | 13자리 + 978·979 시작 확인 |
| KORMARC 신뢰도 낮음 | 사서 검토 권장 — 직접 수정 가능 |
| KOLAS 반입 실패 | .mrc 파일 다운로드 후 KOLAS 수동 반입 |
| 자관 prefix 안 보임 | 설정 → 자관 prefix 확인 |
| 결제 만료 임박 | 자치구 도서관사업소 연락 |

---

## 8. 본인 인수 메모

{data.notes if data.notes else "(특이사항 없음)"}

---

## 9. 연락처

| 대상 | 연락처 |
|------|--------|
| 전임 사서 ({data.librarian_name} 선생님) | {data.contact_email or "(개인 연락처는 별도 전달)"} |
| kormarc-auto 운영자 | okwhrlgma@gmail.com |
| 자치구 도서관사업소 | (도서관 비치 연락처 확인) |

---

> 본 인계 매뉴얼은 kormarc-auto가 자동 생성한 표준 양식입니다.
> 추가 메모는 §8에 직접 기록해주세요.

> 다음 사서 선생님이 빠르게 적응하실 수 있도록 작성했습니다.
> 좋은 도서관 운영 응원합니다.

— {data.librarian_name} 선생님
"""


def save_handover_manual(data: HandoverManualData, output_path: str) -> bool:
    """인계 매뉴얼 파일 저장."""
    try:
        markdown = generate_handover_manual_markdown(data)
        Path(output_path).write_text(markdown, encoding="utf-8")
        return True
    except Exception:
        return False
