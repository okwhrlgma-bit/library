---
description: 책장 사진 OCR로 장서 점검 (오배가·미등록 자동 검출)
---

## 사용법

```powershell
kormarc-auto inspect "$ARGUMENTS"
```

예:
- `/inspect shelf1.jpg shelf2.jpg`
- `/inspect shelf1.jpg --kdc-range 810-820`

## 동작

1. EasyOCR로 책등 청구기호 추출 (한글·숫자 패턴)
2. 자관 DB(library_db.jsonl)와 대조
3. 결과 분류:
   - **matched**: 자관 일치 (정상)
   - **missorted**: 자관에 있으나 KDC 범위 밖 (오배가)
   - **missing_in_db**: OCR에서 보이나 자관 미등록

## 사전 요건

- `pip install -e .[ocr]` (easyocr) — 첫 실행 시 모델 자동 다운로드
- 자관에 .mrc 누적 필요 (`kormarc-auto isbn ...`로 쌓이는 인덱스)

## 사서 활용

연 1~2회 전수 점검을 며칠 → 몇 시간으로 단축. 결과는 사서가 검토 후 KOLAS 수기 정정.
