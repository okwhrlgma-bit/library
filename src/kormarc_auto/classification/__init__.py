"""KDC 자동 분류 + 주제명 추천 (Phase 3).

다단계 폴백:
1. 국립중앙도서관 KDC (book_data['kdc']에 이미 있으면 그대로)
2. ISBN 부가기호 매핑 (보조)
3. AI(Claude) 후보 3개 + 신뢰도

상세 알고리즘은 docs/spec.md §KDC 자동 분류 참조.
"""
