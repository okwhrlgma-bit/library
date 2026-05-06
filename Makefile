# kormarc-auto Makefile (Cycle 26·V2 §10·V3 Block 4·외부 256 출처 통합)
# 단축 명령 = 자율 사이클·검증·운영 entry point.

.PHONY: help test lint format gates regression blocker funnel demo serve audit cost stop rollback pavr weekly kolas3 night-loop a11y ui-test dashboard

# 기본 = help
.DEFAULT_GOAL := help

help: ## 사용 가능 명령 출력
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# === 검증 게이트 (Plan B §0·자동 머지 6 게이트) ===
test: ## pytest 전수
	python -m pytest -q

lint: ## ruff check (자동 fix)
	ruff check . --fix

format: ## ruff format
	ruff format .

gates: lint format test regression ## 4 게이트 통합 (commit 직전)
	python scripts/binary_assertions.py --strict

regression: ## 자관 round-trip baseline 회귀 비교 (≤ 1pp)
	python scripts/regression_check.py --strict

# === 운영 ===
blocker: ## 다음 매출 차단점 자동 감지
	python scripts/next_blocker.py

funnel: ## 주간 funnel 리포트
	bash scripts/automation/weekly-funnel-cron.sh

demo: ## 30초 offline demo (키 0개)
	KORMARC_DEMO_MODE=1 python -m kormarc_auto.cli demo

serve: ## FastAPI 서버 (8000)
	python -m kormarc_auto.cli serve

# === 자동화 인프라 (V2 §10) ===
audit: ## 최근 7일 audit 로그
	bash scripts/automation/audit-query.sh --days 7

cost: ## 최근 7일 비용 리포트
	bash scripts/automation/cost-report.sh

stop: ## 🚨 모든 자율 프로세스 즉시 정지 (V2 §10)
	bash scripts/automation/emergency-stop.sh

rollback: ## 최근 1 commit revert (--commits N 으로 다중)
	bash scripts/automation/rollback.sh --commits 1

# === PAVR + V2 ===
pavr: ## PAVR 슬래시 진입 (Claude Code 세션 권장)
	@echo "Claude Code 세션에서 /pavr <작업> 입력"

# === V3 자동화 (외부 256 출처·Cycle 43~49) ===
weekly: ## V3 Block 4 주간 리포트 (audit.jsonl 7일 후 활성)
	python automation/weekly_report.py

kolas3: ## KOLAS III D-day 자동 갱신 (countdown JSON)
	bash scripts/automation/kolas3-daily-update.sh

night-loop: ## V3 Phase 2 무중단 자율 + cost guard wrapper
	@echo "Phase 2 (Anthropic API 키 발급 후) 활성: ./automation/po_loop_with_cost_guard.sh '<명령>'"

# === UI/UX (Cycle 60·헌법 §12 KWCAG 2.2 + KRDS + Pretendard) ===
a11y: ## UI/UX 회귀 (a11y_inject + librarian_ux 테스트)
	python -m pytest tests/test_a11y_inject.py tests/test_kwcag22.py -v

ui-test: ## 모든 UI 테스트 (a11y + Streamlit components)
	python -m pytest tests/test_a11y_inject.py tests/test_kwcag22.py tests/test_field_status.py -q

dashboard: ## 매출 통합 대시보드 (revenue_dashboard·Cycle 37+51)
	streamlit run src/kormarc_auto/ui/revenue_dashboard.py

# === 회귀 게이트 통합 (CI·로컬 검증) ===
ci: gates ## CI 전수 (gates 동의어)
	@echo "✓ 모든 게이트 통과·commit 안전"
