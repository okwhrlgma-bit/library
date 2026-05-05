---
name: deploy
description: 프로덕션 배포 (사람 승인·일반과세자 등록 후 활성)·테스트→빌드→배포→PROGRESS 기록
disable-model-invocation: true
allowed-tools: Bash(npm:*), Bash(git:*), Bash(uv:*), Bash(pip:*), Bash(python:*), Bash(pytest:*), Read, Write, Edit
---

# /deploy — 프로덕션 배포 슬래시 (P43·V1 §2.5·§3.6 정합)

⚠️ **사업자 등록 후 활성**. 등록 전에는 dry-run만 권장.

## 사전 게이트 (모두 통과 필수)

1. PO 일반과세자 등록 완료 (사용자_TODO PO-PROD-1)
2. PortOne v2 sandbox 통합 완료 (P30·Cycle 14+)
3. 처리방침 §28의8 6항목 (P29 ✅ Cycle 10B)
4. 자관 round-trip ≤ 1pp 회귀 (영구 invariant)
5. binary_assertions 39/39
6. ruff·pytest·887 tests+ 통과

## 절차

### 1. 검증 (결정론·모델 외부)

```bash
ruff check .
ruff format --check .
python -m pytest -q
python scripts/binary_assertions.py --strict
python scripts/eval_per_record_roundtrip.py --sample 50
```

하나라도 실패 = 즉시 중단·배포 금지.

### 2. 빌드

```bash
python -m build  # 또는 uv build
```

### 3. tag·push

```bash
VERSION=$(python -c "from kormarc_auto import __version__; print(__version__)")
git tag -a "v${VERSION}" -m "Release v${VERSION}"
git push origin main --tags
```

### 4. 배포 (운영자 환경)

PO 운영 환경에 따라 분기:
- AWS Lightsail Seoul = `ssh deploy@server "cd /app && git pull && systemctl restart kormarc-auto"`
- NCP/NHN CSAP = 자치구 진출 시 별도 (P51 Progressive Trust 정합)

### 5. PROGRESS.md 자동 (Stop hook 정합·Cycle 17 P41)

```bash
echo "## $(TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M') — Deploy v${VERSION}" >> PROGRESS.md
```

### 6. 사후 검증

- /healthz endpoint 200 OK
- /accuracy endpoint 응답 (분리표 정합)
- /pricing endpoint 4 플랜 응답
- /migration/kolas3 endpoint D-day 정합 (≠ 1초 = STOP)

## STOP 조건

- 사업자 미등록 상태 라이브 모드 시도 = 즉시 STOP
- main 브랜치 직접 푸시 외 절대 금지 (헌법 §0)
- production .env 평문 commit 시도 = scan-secrets hook 차단
- KOLAS III D-day 출력 ≠ 2026-12-31 = STOP

## 알라딘·정부 게이트

- 알라딘 출처 표시 (헌법 §3) ≠ "도서 DB 제공 : 알라딘 인터넷서점" = 차단
- 디지털서비스몰 등재 시 = ISMS-P/CSAP 인증서 첨부 필수

## 정합 ADR

- ADR 0026 한국 SaaS 결정 (일반과세자·PortOne)
- ADR 0028 결정론 (모델 pinning 검증)
- ADR 0030 카테고리형 신뢰 (raw % 노출 0)
- ADR 0032 KWCAG·SEO (사후 검증)
- ADR 0034 hooks (scan-secrets 차단)
- ADR 0036 PAVR (verify 단계 정합)
