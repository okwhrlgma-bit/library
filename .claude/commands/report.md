---
description: PDF 보고서 생성 — 신착 안내·월간 운영·일괄 검증
---

## 사용법

```powershell
kormarc-auto report $ARGUMENTS
```

## 3종 보고서

### 1. 신착도서 안내문 (이용자 게시용)

```powershell
kormarc-auto report announcement --library "○○도서관" --title "2026년 4월 신착" --limit 30
```

자관 인덱스 최근 N권 → 표제·저자·청구기호·소개 PDF.

### 2. 월간 자관 운영 보고서 (상부기관 제출)

```powershell
kormarc-auto report monthly --library "○○도서관" --year 2026 --month 4
```

KDC 분포·발행연도 분포·총 자료 수 자동 집계.

### 3. 일괄 검증 리포트 (KOLAS 반입 전 점검)

```powershell
kormarc-auto report validate file1.mrc file2.mrc file3.mrc
```

각 .mrc의 KOLAS 엄격 검증 결과 + 오류·경고 요약 PDF.

## 사전 요건

- `pip install reportlab`
- 한글 폰트 자동 탐지 (Malgun/AppleSDGothic/NanumGothic)
