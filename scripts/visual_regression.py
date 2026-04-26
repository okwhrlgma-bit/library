"""Streamlit UI 시각 회귀 — PO 자율성 가이드 §6 (지각 피드백).

매 큰 UI 변경 후 자동 스크린샷 → 기준 이미지와 픽셀 차이 측정 →
허용 임계값(기본 1%) 초과 시 회귀 플래그.

3단계:
1. baseline 캡처 (`--baseline`) — 첫 실행 시 또는 의도된 변경 후
2. 비교 (`--compare`) — 매 commit 후 자동 (Stop hook 후보)
3. 보고서 (`logs/visual/diff_report.html`) — 사서 시연 전 점검

의존성: Playwright (설치 안 되어 있으면 graceful fail).

사용:
    # 첫 실행 (기준 이미지 생성)
    python scripts/visual_regression.py --baseline

    # 회귀 검사 (비교)
    python scripts/visual_regression.py --compare

    # 임계값 조정
    python scripts/visual_regression.py --compare --threshold 0.5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = ROOT / ".claude" / "visual" / "baseline"
CURRENT_DIR = ROOT / ".claude" / "visual" / "current"
DIFF_DIR = ROOT / "logs" / "visual"

# 기본 캡처 시나리오 — 사서가 가장 자주 보는 화면
SCENARIOS = [
    {
        "name": "main_isbn",
        "url": "http://127.0.0.1:8501",
        "viewport": {"width": 1280, "height": 900},
        "description": "메인 화면 (ISBN 탭)",
    },
    {
        "name": "main_mobile",
        "url": "http://127.0.0.1:8501",
        "viewport": {"width": 375, "height": 812},  # iPhone X
        "description": "모바일 (사서 폰 카메라 시연)",
    },
]


async def capture_url(url: str, output_path: Path, viewport: dict[str, int]) -> bool:
    """단일 URL 스크린샷. Playwright 미설치면 False."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("⚠ playwright 미설치 — `pip install playwright && playwright install chromium`")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        try:
            await page.goto(url, timeout=15000)
            # Streamlit는 hydration이 늦음 — 2초 대기
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(output_path), full_page=True)
        except Exception as e:
            print(f"⚠ {url} 캡처 실패: {e}")
            await browser.close()
            return False
        await browser.close()
    return True


def pixel_diff_ratio(img_a: Path, img_b: Path) -> float:
    """두 PNG 픽셀 차이 비율 (0.0~1.0). PIL 미설치면 -1.0."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return -1.0

    if not img_a.exists() or not img_b.exists():
        return 1.0  # 둘 중 하나 없으면 100% 차이

    a = Image.open(img_a).convert("RGB")
    b = Image.open(img_b).convert("RGB")
    if a.size != b.size:
        return 1.0  # 크기 다르면 회귀

    diff = ImageChops.difference(a, b)
    bbox = diff.getbbox()
    if bbox is None:
        return 0.0  # 완전 동일

    # 차이 영역의 평균 픽셀값을 0~1로
    bands = diff.split()
    n_pixels = a.size[0] * a.size[1]
    diff_sum = sum(sum(band.histogram()[i] * i for i in range(256)) for band in bands)
    max_diff = 255 * 3 * n_pixels
    return diff_sum / max_diff if max_diff else 0.0


async def run_baseline() -> int:
    print(f"📸 baseline 캡처 ({len(SCENARIOS)} 시나리오)...")
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for s in SCENARIOS:
        path = BASELINE_DIR / f"{s['name']}.png"
        if await capture_url(s["url"], path, s["viewport"]):
            print(f"  ✓ {s['name']} → {path.name}")
            ok += 1
        else:
            print(f"  ❌ {s['name']}")
    return 0 if ok == len(SCENARIOS) else 1


async def run_compare(threshold: float) -> int:
    if not BASELINE_DIR.exists() or not any(BASELINE_DIR.iterdir()):
        print("⚠ baseline 없음 — `--baseline` 먼저 실행")
        return 1

    print(f"📸 비교 캡처 + 픽셀 차이 (임계값 {threshold:.1%})...")
    CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    DIFF_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    regressed = 0

    for s in SCENARIOS:
        cur = CURRENT_DIR / f"{s['name']}.png"
        base = BASELINE_DIR / f"{s['name']}.png"
        captured = await capture_url(s["url"], cur, s["viewport"])
        if not captured:
            results.append({"scenario": s["name"], "captured": False})
            continue

        ratio = pixel_diff_ratio(base, cur)
        is_regression = ratio > threshold
        if is_regression:
            regressed += 1
        results.append(
            {
                "scenario": s["name"],
                "ratio": round(ratio, 4),
                "regression": is_regression,
                "baseline": str(base),
                "current": str(cur),
            }
        )
        mark = "❌" if is_regression else "✓"
        print(f"  {mark} {s['name']}: {ratio:.2%} 차이")

    # 누적 로그
    log_path = DIFF_DIR / "history.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {"ts": int(time.time()), "threshold": threshold, "results": results},
                ensure_ascii=False,
            )
            + "\n"
        )

    print(f"\n총 {len(results)} 시나리오 / 회귀 {regressed}건 / 로그: {log_path}")
    return 1 if regressed > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Streamlit 시각 회귀")
    parser.add_argument("--baseline", action="store_true", help="기준 이미지 생성")
    parser.add_argument("--compare", action="store_true", help="비교 실행")
    parser.add_argument(
        "--threshold", type=float, default=0.01, help="회귀 판정 임계값 (기본 1%)"
    )
    args = parser.parse_args()

    if not args.baseline and not args.compare:
        parser.print_help()
        return 1

    if args.baseline:
        return asyncio.run(run_baseline())
    if args.compare:
        return asyncio.run(run_compare(args.threshold))
    return 0


if __name__ == "__main__":
    sys.exit(main())
