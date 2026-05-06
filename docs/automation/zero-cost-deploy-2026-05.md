# 신경 0 배포 stack — ₩0/월·자동·도메인 없이 (Cycle 63)

> PO 명령 (2026-05-06): "도메인 필수? 앱 배포 안돼? 돈 안 들이고 올려놓고 신경끄는 구조".
> 답: 도메인 필수 X·앱 배포 = 무료·git push = 자동 deploy.

## 추천 stack (₩0/월·maintenance ₩0)

```
GitHub repo (public)
  ├─ main push ──→ GitHub Pages       (정적 사이트·도메인 X·자동)
  ├─ main push ──→ Streamlit Cloud    (실제 앱·도메인 X·자동)
  ├─ tag push  ──→ GitHub Releases    (.mrc·PDF·자동)
  ├─ cron      ──→ GitHub Actions     (KOLAS3·blocker·자동)
  └─ webhook   ──→ 이메일/슬랙        (사고 알림만·자동)
```

## 1. GitHub Pages (정적 사이트)

### 활성 (5분·1회)
1. GitHub repo `Settings → Pages`
2. Source = "GitHub Actions" 선택
3. `.github/workflows/github-pages.yml` 자동 작동 (이미 박제·Cycle 63)
4. `git push origin main` = 자동 deploy
5. URL = `https://okwhrlgma-bit.github.io/library/`

### 효과
- ✅ 정적 사이트 호스팅 무료
- ✅ HTTPS 자동
- ✅ 구글·네이버 인덱싱 정상
- ✅ JSON-LD·OG·sitemap 100% 작동
- ✅ Lead magnet PDF 호스팅 가능

## 2. Streamlit Community Cloud (실제 앱)

### 활성 (5분·1회)
1. https://share.streamlit.io 가입 (GitHub 계정 연동·₩0)
2. "New app" → GitHub repo 선택
3. Main file = `src/kormarc_auto/ui/streamlit_app.py`
4. Branch = `main`
5. Secrets = `.streamlit/secrets.toml.example` 내용 → 값 채워서 붙여넣기
6. Deploy = 자동
7. URL = `https://kormarc-auto.streamlit.app` (커스텀 가능)

### 효과
- ✅ 실제 앱 작동 (Streamlit UI 그대로)
- ✅ git push = 자동 재배포
- ✅ 무료 sleep 후 재시작 (cold start 30초)
- ✅ 도서관 사서 = 링크만 받으면 즉시 사용

### 한도 (무료 tier)
- CPU 1·메모리 1GB
- 무료 1 앱 (1 사용자)·다중 사용자 동시 = 부하 분산 X
- 일일 사용자 한도 X (개인 SaaS = 충분)
- 7일 미사용 = 자동 sleep·접속 시 재시작

→ **사서 5명 인터뷰·PILOT 5관 = 충분**.

## 3. Hugging Face Spaces (백업 옵션)

### 활성 (5분·1회)
1. https://huggingface.co 가입 (₩0)
2. "New Space" → SDK = Streamlit
3. GitHub repo sync (자동)
4. URL = `https://huggingface.co/spaces/okwhrlgma-bit/kormarc-auto`

### 차이점 (vs Streamlit Cloud)
- ✅ AI/ML 커뮤니티 노출 ↑
- ✅ Streamlit Cloud sleep 시 backup
- ⚠ 한국 사서 = HF 익숙 X

→ **Phase 2 옵션·Streamlit Cloud 1차 권장**.

## 4. GitHub Releases (파일 배포)

### 자동 활성
- `git tag v0.7.2 && git push --tags` = Release 자동 생성
- `.mrc`·PDF lead magnet·로고·스크린샷 첨부 가능
- 영구 호스팅·CDN·HTTPS

### 활용
- KOLAS III 마이그 가이드 PDF
- 자관 PILOT case study PDF
- 학교운영위 결재 자료 PDF
- 보도자료 자료실

## 5. GitHub Actions (cron 자동화)

### 이미 박제 (Cycle 22·52·61)
- `weekly-report.yml` = 매주 월 리포트
- `daily-blocker.yml` = 매일 차단점
- `regression-check.yml` = main push 회귀
- `a11y-ci.yml` = PR a11y 회귀
- `github-pages.yml` = 자동 deploy
- `test-hooks.yml` = hook 회귀

### 비용
- public repo = 무료 (무제한 분)
- private repo = 월 2,000분 무료

## 6. 신경 0 운영 매뉴얼

### 매일 (PO 5분)
```bash
# 핸드폰에서도 가능
git pull
make blocker  # 또는 GitHub Actions artifact 확인
```

### 매주 (PO 10분)
```bash
# Streamlit Cloud sleep 깨우기 (URL 1회 클릭)
# GitHub Pages 인덱싱 확인
# weekly report PR review (자동 생성)
```

### 매월 (PO 30분)
```bash
# learnings.md 신규 사실 검토
# decisions.md 누적 검토
# 사용자 피드백 GitHub Discussions 응대
```

### 사고 시 (긴급)
```bash
make stop  # emergency-stop.sh
make rollback  # 마지막 commit revert
git revert HEAD  # GitHub Pages 자동 재배포
```

## 7. 도메인 추가 시점 (선택·미래)

- **첫 매출 ₩100K 후** = `kormarc-auto.kr` (가비아 ₩30K/년)
- **이메일 인증 필요 시** = 구글 워크스페이스 (₩9K/월)
- **자치구 진입 시** = 도메인 + ISMS-P 자체점검

→ 도메인 = **매출 시작 후 추가**·**선요건 X**.

## 8. 비용 비교

| stack | 월 비용 | 신경도 | 한국 사서 친화 |
|---|---:|---:|---:|
| **이 stack (GitHub + Streamlit)** | **₩0** | 🟢 매우 낮음 | 🟢 |
| AWS Lightsail (Cycle 26·외부 858) | ₩7K | 🟡 중간 | 🟢 |
| 자체 도메인 + 워크스페이스 | ₩39K/월 | 🟠 높음 | 🟢 |
| NCP/NHN CSAP | ₩50K+/월 | 🔴 높음 | 🟢 |

→ **PO Phase 1 (사용자 0명·검증) = 이 stack 1순위**.

## 9. 한계 (정직 헤더)

- Streamlit Cloud = 1 앱·동시 사용자 부하 분산 X (5명+ 동시 = 느림)
- GitHub Pages = 정적 (JS·DB X)
- 매출 ₩100K+ = AWS Lightsail 권장 (사이클 26 박제)
- CSAP·자치구 일괄 = NCP/NHN 필수 (외부 858 정합)
- **이 stack = MVP·Phase 1 검증·5명 인터뷰까지 충분**

## 10. 즉시 활성 (PO 외부 작업·15분)

1. **GitHub repo public 전환** (필요 시): Settings → Visibility → Public
2. **GitHub Pages 활성**: Settings → Pages → Source: GitHub Actions
3. **Streamlit Community Cloud 가입**: share.streamlit.io (GitHub 연동)
4. **앱 deploy**: Streamlit Cloud → New app → repo 선택 → Deploy
5. **secrets 입력**: KORMARC_DEMO_MODE=1 (키 0개로 작동)
6. **git push**: 자동 deploy 시작·5분 후 URL 활성

→ **15분 작업으로 = 무료 호스팅 완료·도메인 X·신경 X**.

## 11. 발행 후 자동 SEO 활성

GitHub Pages URL이 활성되면:
- ✅ 구글·네이버 자동 인덱싱 (sitemap.xml 정합)
- ✅ JSON-LD 100% 작동
- ✅ LLM (ChatGPT·Claude) 인용 가능 (llms.txt 정합)
- ✅ 콜드 메일 = `https://okwhrlgma-bit.github.io/library/` link 사용 가능

→ **도메인 0원·즉시 검색·LLM 노출 활성**.
