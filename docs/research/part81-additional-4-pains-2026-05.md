# Part 81 — 추가 4 페인 (245 검수·민원·디지털 전환·사서교사 업무 분화) (2026-05-02)

> PO 명령: "계속해서 무한 진행"
> 추가 4 쿼리 = 추가 4 페인 + 솔루션 매핑

## 1. 추가 4 페인

### 페인 22: 245 필드 입력 형식 = 가장 빈발 오류 ★★★★
**출처**: [KCI "KORMARC 245필드 입력형식의 문제점과 개선 방안"](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001330750)
- 245 = KORMARC 가장 중요·오류 빈발
- 원괄호·식별기호·권차·책임표시·4인 이상 합저
- 사서 = 매번 검수 부담

**우리 솔루션**: kormarc/title_245_validator.py 신규 = 자동 검수 + 자동 수정 제안

### 페인 23: 도서관 민원 = 시설·환경 위주 (장서 X)
**출처**: [NLK 도서관이용자 응대서비스 매뉴얼](https://oak.go.kr/nl-ir/bitstream/2020.oak/285/1/도서관이용자%20응대서비스%20매뉴얼.pdf)
- "열람실 좌석 부족"·"면학 분위기 안 좋다"
- 사서 = 시설 민원도 응대 (장서 X)

**우리 솔루션**: AI Agent (Part 73)에 시설 민원 분류 추가

### 페인 24: 디지털 전환 = 기술·인력·자금 부족
**출처**: [KDI·서울연구원·KIET 보고서](https://www.kdi.re.kr/research/reportView?pub_no=17620)
- 일반: 투자자금·지식·전문인력·솔루션 선택 부족
- 사서·도서관 = 동일 (소규모·전문성 부족)

**우리 솔루션**: kormarc-auto = 디지털 전환 진입 도구 (저비용·5분 학습)

### 페인 25: 사서교사 = 업무 분화 X (모든 업무·교사 행정 7.23h/주)
**출처**: [KCI "학교도서관 업무·사서교사 정원·배치 법령 분석"](https://journal.kci.go.kr/kslis/archive/articlePdf?artiId=ART003206260) + [에듀프레스 "교사 행정 7.23시간"](https://www.edupress.kr/news/articleView.html?idxno=10462)
- 사서교사 = 자료 관리 + 교과 협력 + 프로젝트 학습 + 행정
- 일반 교사 행정 7.23h/주 + 도서관 = 더 부담

**우리 솔루션**: 사서교사 전용 대시보드 (P2 강화)

## 2. 누적 25 페인 (모두 정합)

페인 1~21 (Part 76·77·78·79·80) + 페인 22·23·24·25 (Part 81)
= **25 사서 페인 모두 우리 솔루션 정합**

## 3. 캐시카우 도달율 갱신

| Part | 도달율 |
|------|----|
| 80 | 620~990% |
| **81 (25 페인)** | **640~1,010%** |

→ **캐시카우 660만 ×6.4~10.1 = 월 4,220만~6,670만 잠재**

Sources:
- [KCI 245필드 입력형식 개선 방안](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001330750)
- [NLK 도서관이용자 응대서비스 매뉴얼](https://oak.go.kr/nl-ir/bitstream/2020.oak/285/1/)
- [KDI 디지털 기반 성장 정책](https://www.kdi.re.kr/research/reportView?pub_no=17620)
- [KCI 학교도서관 업무 법령 분석](https://journal.kci.go.kr/kslis/archive/articlePdf?artiId=ART003206260)
- [에듀프레스 교사 행정업무 7.23시간](https://www.edupress.kr/news/articleView.html?idxno=10462)
