---
description: ISBN → KORMARC .mrc 생성 (단일)
---

다음 ISBN의 KORMARC를 생성해주세요.

ISBN: $ARGUMENTS

처리 순서:
1. `kormarc_auto.api.aggregator.aggregate_by_isbn()` 호출
2. `kormarc_auto.classification.kdc_classifier.recommend_kdc()`로 KDC 추천
3. `kormarc_auto.kormarc.builder.build_kormarc_record()`로 빌드
4. `kormarc_auto.vernacular.field_880.add_880_pairs()`로 한자 페어
5. `kormarc_auto.kormarc.validator.validate_record()`로 검증
6. `kormarc_auto.output.kolas_writer.write_kolas_mrc()`로 저장

결과를 다음 형식으로 보고:
- 사용된 데이터 소스
- 자동 채워진 필드 수
- 신뢰도
- KDC 후보
- 880 페어 개수
- 검증 결과
- 저장 경로
- (있다면) 출처 표시 의무 문구
