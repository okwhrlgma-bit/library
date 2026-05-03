# CLAUDE.md — kormarc-auto (slim·60줄 ceiling)

> Claude Code 매 세션 자동 로드. 절대 우선. 상세 → `agent_docs/`.

## 0. 정체성
한국 도서관 **KORMARC 자동 생성 SaaS**. ISBN/사진 → KOLAS·DLS·알파스 호환 .mrc.
**목표**: 사서 마크 시간 권당 8분 → 1.5분 (descriptive 블록).
**PO**: 사서 출신 1인 비개발자.

## 1. 헌법 (3원칙)
1. **의심하라** — 미션 정합 검증
2. **검증하라** — 추측 X·코드/문서 직접 확인
3. **정제하라** — 자기 비판 후 다듬기

## 2. 평가축 (commit 거부 조건)
모든 변경 = 다음 둘 중 1+ 양수:
- §0 사서 마크 시간 단축
- §12 결제 의향 ↑

음수 = commit X.

## 3. HARD RULES
- ❌ API 키 하드코딩 (`.env` 사용)
- ❌ 알라딘 출처 표시 누락 ("도서 DB 제공 : 알라딘 인터넷서점")
- ❌ "100% 자동" 약속 (사서 검수 단계 보존)
- ❌ 외부 API timeout 미지정 (10초)
- ❌ 한국어 변수명 (식별자 = 영문)
- ✅ try/except + timeout=10 외부 호출
- ✅ confidence 점수 + source_map 추적
- ✅ pymarc UTF-8 명시
- ✅ 한국어 docstring

## 4. 자율성 4단계
- L1 자율: 오타·린트·docstring
- L2 보고: 로드맵·버그
- L3 승인: API·DB 스키마·메이저 버전
- L4 PO만: 운영 키·결제·운영 배포

## 5. 종료 게이트 (이중)
- pytest 통과 + ruff 0 errors
- binary_assertions 38/38 (현재 38/39)
- 평가축 §0/§12 양수 commit message 명시
- `Co-Authored-By: Claude Opus 4.7 (1M context)` 포함

## 6. 5대 멈춤 패턴 회피
- 모호 결정 → 보수적 + DECISIONS.md
- 테스트 3회 실패 → SKIPPED.md + 다음
- 자가 디버그 30 iter 한계
- 컨텍스트 한계 → 본 파일 핵심
- 의존성 실패 → 새 의존성 X·오프라인

## 7. 한국어 정책
- PO 프롬프트·응답 = 한국어
- 영어 = 식별자·git commit·API 경로
- KORMARC·KDC·관제 용어 = 한국어
- 단일 식별자 혼용 금지

## 8. 영구 정책 (PO 명령)
- 명령 없을 시 = 자율 모드 default
- 매 사이클 = 사용자_TODO 자동 정리

## 9. 상세 참조 (agent_docs/)
- KORMARC 도메인 → `agent_docs/CLAUDE-full-2026-05-03.md` (구버전 백업)
- 외부 API → `docs/spec.md`
- 테스트 → `docs/test_results.md`
- 헌법 정밀화 → `.claude/rules/{autonomy-gates,kormarc-domain,business-impact-axes}.md`
- 페르소나 자율 → `.claude/rules/personas-autonomy-policy.md`

## 10. 변경 이력
v0.5.0+ (2026-05-03): Part 87~92·600 tests·Champion 4/4 92.5점·CSAP 추상화·정확도 disaggregation. 상세 → `CHANGELOG_NIGHT.md`.
