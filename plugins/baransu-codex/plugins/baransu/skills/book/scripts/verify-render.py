#!/usr/bin/env python3
"""
Render a local HTML file in headless Chromium, save a full-page screenshot,
and print a one-line JSON probe of key structural elements.

Usage:
    python3 verify-render.py <html-path> <png-out-path>

Exit codes:
    0 — rendered and screenshot saved (probe printed to stdout)
    1 — Playwright launch / navigation failed (error printed to stderr)
    2 — usage error

Why Playwright (not browser-use):
    browser-use's headless Chromium silently fails to load file:// URLs
    (readyState=complete but DOM stays empty). Playwright handles file://
    natively and is the documented project-standard E2E browser driver.
"""
import json
import os
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify-render.py <html-path> <png-out-path>", file=sys.stderr)
        return 2

    html_path = os.path.abspath(sys.argv[1])
    out_png = sys.argv[2]

    if not os.path.isfile(html_path):
        print(f"error: html not found: {html_path}", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("error: playwright not installed (pip install playwright && playwright install chromium)", file=sys.stderr)
        return 1

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                device_scale_factor=2,
            )
            page = ctx.new_page()
            page.goto(f"file://{html_path}", wait_until="networkidle")
            probe = page.evaluate(
                """() => ({
                    overflow: document.documentElement.scrollWidth > window.innerWidth,
                    has_paper: !!document.querySelector('.paper'),
                    has_h1: !!document.querySelector('h1'),
                    has_h2: !!document.querySelector('h2'),
                    svg_count: document.querySelectorAll('svg').length,
                    title: document.title || ""
                })"""
            )
            page.screenshot(path=out_png, full_page=True)
            browser.close()
    except Exception as e:
        print(f"error: render failed: {e}", file=sys.stderr)
        return 1

    print(json.dumps(probe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
