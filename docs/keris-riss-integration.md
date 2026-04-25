# KERIS / RISS 연동 가능성 조사 보고서

> 작성일: 2026-04-26 · 대상: kormarc-auto 대학도서관 시장 진출 검토

## 핵심 결론 (3줄 요약)

1. **RISS Open API는 무료로 제공되며 학위논문/학술지/단행본/연구보고서 등 7개 자료 유형의 서지 검색이 가능**하므로, kormarc-auto의 "원문 메타데이터 조회 → KORMARC 자동 생성" 파이프라인의 보조 데이터 소스로 즉시 활용 가능하다.
2. **대학도서관 ILS(TULIP, SOLARS 등)는 모두 KORMARC-통합서지용을 표준으로 사용**하므로, 우리가 출력하는 `.mrc` 파일은 별도 변환 없이 대학도서관 시스템에 그대로 import 가능하다 (단, KERIS 종합목록 입력지침의 필수 필드 검증 로직 추가 필요).
3. **단, 대학도서관은 이미 TULIP/SOLARS가 600+150개 기관에 deep-locked된 시장**이며 자동 목록은 벤더 솔루션에 통합되어 있으므로, B2B 직판보다는 **"개별 사서의 작업 효율화 도구"** 또는 **"중소형 전문/연구기관 도서관 타겟"** 진입이 현실적이다.

---

## 1. KERIS (한국교육학술정보원) 개요

- 교육부 산하 정부출연기관, 1999년 설립. RISS·Rinfo·KOCW·KERIS 종합목록 등 운영.
- 사서 입장의 핵심 서비스: **KERIS 종합목록(UNICAT)** — 전국 대학도서관 소장 자료의 통합 서지 DB. 각 대학이 자관 서지를 업로드하면 RISS 검색·상호대차(ILL)·E-DDS에 노출됨.
- 매년 「대학도서관 통계조사」 및 「KERIS 종합목록 입력지침 교육」을 시행. 입력지침이 곧 사실상의 대학도서관 KORMARC 표준.
- 출처: <https://www.keris.or.kr/>, <http://unicat.riss.kr/>

## 2. RISS Open API

- **API 센터**(<https://www.riss.kr/apicenter/apiMain.do>)에서 6종 API 공개:
  RISS Search · KOCW · WILL(상호대차) · Rinfo(통계) · FRIC(외국학술지) · SAM(학술관계분석).
- **무료** ("애플리케이션 개발자에게 RISS의 콘텐츠를 무료로 제공"). 인증키는 RISS API 센터 또는 공공데이터포털(<https://www.data.go.kr/data/3046254/openapi.do>)에서 신청.
- 자료 유형 커버리지: 학위논문, 국내·해외 학술논문, 단행본, 연구보고서, 학술지, 공개강의 — kormarc-auto가 다루는 모든 단행본/연속간행물 케이스를 포괄.
- ISBN/표제 검색은 RISS Search API의 검색 파라미터에 포함되나, 정확한 필드명·rate limit은 인증키 발급 후 Swagger 명세를 봐야 확인 가능.

## 3. 대학도서관 표준 시스템

- 한국 대학도서관 ILS는 **KERIS 자체 LAS가 아니라 민간 벤더 제품**이 사실상 표준:
  - **TULIP / TULIP+ (퓨처누리)** — 600여 기관 도입, 국내 1위. KERIS 연동 내장.
  - **SOLARS (아이네크/INEK)** — 150여 기관, 강원대·경북대·숭실대·한양대 등.
- 두 시스템 모두 **KORMARC-통합서지용(KS X 6006-0)** 표준 채택. 즉 우리 `.mrc` 출력은 import 호환.
- 출처: <https://home.futurenuri.com/>, <https://www.inek.kr/about/intro/>, <https://librarian.nl.go.kr/LI/contents/L10102000000.do>

## 4. 연동 시나리오

| 시나리오 | 실현성 | 필요 작업 |
| --- | --- | --- |
| RISS Search API로 ISBN 조회 → KORMARC 자동 생성 | 매우 높음 | API 키 발급, XML/JSON 파서, 245/260/300 매핑 |
| `.mrc` 파일을 TULIP/SOLARS에 일괄 import | 높음 | KERIS 종합목록 입력지침의 필수태그(008/040/245/260/300/490/500/653) 검증기 추가 |
| KERIS 종합목록(UNICAT)에 직접 업로드 | 중간 | 기관 가입·인증 필요. 개별 사서 단독으로는 불가, 대학 단위 계정 필요 |

## 5. 시장 규모

- 4년제 대학 RISS 참여율 **100%**, 학위논문 제공 대학 **229곳**, 단행본 제공 고등교육·전문도서관 **797곳 이상**.
- 한국 대학도서관 연간 자료구입비 합계는 약 3,000억 원대 (KERIS 「대학도서관 통계조사」 기준), 1관당 평균 도서구입비 수억 원.
- 출처: <https://www.rinfo.kr/>, <https://www.keris.or.kr/main/na/ntt/selectNttInfo.do?mi=1088&nttSn=38433>, <https://library.korea.ac.kr/about/notice/?lang=en&mod=document&uid=30844>

## 6. 경쟁 솔루션

- 글로벌: **Ex Libris Alma**(서울대·연세대 등 일부 도입), **OCLC WorldShare**. Alma는 2025-2026 로드맵에 한국어 지원 강화 포함.
- 국내: TULIP/SOLARS가 자동 목록 모듈을 자사 ILS 안에 묶어 판매. 별도 SaaS 형태의 자동 목록 도구는 사실상 부재 — kormarc-auto가 진입할 **틈새 존재**.
- 다만 대학도서관 사서들은 이미 ILS 내 카탈로깅 모듈에 익숙하므로, "ILS 외부의 별도 SaaS"가 채택되려면 **속도·정확도·LLM 기반 부가가치(예: 분류기호 추천, 주제어 자동 부여)**로 차별화 필요.
- 출처: <https://librarytechnology.org/pr/31108>, <https://developers.exlibrisgroup.com/alma/integrations/publishing/publishing-to-oclc/>

---

## 권고 (Revenue-first 관점)

- **Phase A (1~2주)**: RISS Open API 키 발급 → kormarc-auto에 "RISS lookup" 버튼 추가. 마케팅 카피: "국립중앙도서관에 없는 학술서·학위논문도 잡아냅니다".
- **Phase B (1개월)**: KERIS 종합목록 입력지침 검증기 추가, 출력 `.mrc`에 "TULIP import 호환" 라벨링.
- **Phase C (조건부)**: 직접 대학 B2B는 TULIP/SOLARS 락인이 강해 비추. 대신 **연구소 도서관·대학원 전공도서실·소규모 사립대** 같은 sub-million 예산 기관을 1차 타겟으로.

## 인용 URL 모음

- <https://www.keris.or.kr/>
- <https://www.riss.kr/>
- <https://www.riss.kr/apicenter/apiMain.do>
- <http://unicat.riss.kr/>
- <https://www.data.go.kr/data/3046254/openapi.do>
- <https://www.keris.or.kr/main/ad/pblcte/selectPblcteETCInfo.do?mi=1142&pblcteSeq=13233>
- <https://librarian.nl.go.kr/LI/contents/L10102000000.do>
- <https://www.rinfo.kr/>
- <https://home.futurenuri.com/homepage4/product/tulip_plus_lms.do>
- <https://www.inek.kr/about/intro/>
- <https://library.korea.ac.kr/about/notice/?lang=en&mod=document&uid=30844>
- <https://librarytechnology.org/pr/31108>
- <https://ko.wikipedia.org/wiki/%ED%95%99%EC%88%A0%EC%97%B0%EA%B5%AC%EC%A0%95%EB%B3%B4%EC%84%9C%EB%B9%84%EC%8A%A4>
