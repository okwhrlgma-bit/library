# PO 직접 실행용·git push helper·1줄 명령
# 사용: PowerShell에서 .\push_kormarc_landing.ps1
# 결과: kormarc-auto landing 변경 7건 = git push → Vercel 자동 재배포 → LIVE

$repo = "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"
Set-Location $repo

Write-Host "=== Cycle 1021 push helper ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "변경 파일 점검:" -ForegroundColor Yellow
git status --short landing/

Write-Host ""
Write-Host "Stage·commit·push 진행 (3 명령):" -ForegroundColor Yellow

git add landing/ -A
$msg = @"
feat(landing): SEO 일괄 강화 (PO #90 정합·Cycle 1014~1017)

- Google site verification meta (G-TQG3YRP3CP·search.google.com)
- canonical link + og:url 정정 (kormarc-auto.com → kormarc-auto-landing.vercel.app)
- sitemap.xml 도메인 정정 + privacy·terms URLs
- robots.txt Sitemap 라인 정정
- Google Analytics 4 추적 (G-TQG3YRP3CP)
- inline SVG favicon (data URI·외부 CDN X)
- privacy.html + terms.html 정적 페이지 (Polar 결제 요건·PIPA·전자상거래법 정합)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
"@
git commit -m $msg

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "commit OK·push 시작..." -ForegroundColor Green
    git push origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ push 완료·Vercel 자동 재배포 시작·1~3분 후 LIVE" -ForegroundColor Green
        Write-Host ""
        Write-Host "검증: 1~3분 후 다음 명령 실행:" -ForegroundColor Cyan
        Write-Host '  cd "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\30-apps\_shared"'
        Write-Host "  python -m search_console_registry verify"
        Write-Host ""
        Write-Host "또는 브라우저에서:" -ForegroundColor Cyan
        Write-Host "  https://search.google.com/search-console → 확인 클릭"
        Write-Host "  https://searchadvisor.naver.com → 사이트맵 제출"
    } else {
        Write-Host "❌ push 실패·credential·remote 점검 필요" -ForegroundColor Red
    }
} else {
    Write-Host "❌ commit 실패·status 재확인" -ForegroundColor Red
}
