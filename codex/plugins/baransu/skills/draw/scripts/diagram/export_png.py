#!/usr/bin/env python3
"""Rasterize the first SVG in a diagram HTML file with Playwright."""

from __future__ import annotations

import argparse
import math
import pathlib
import sys
import json, shutil, tempfile, time  # /draw: seeded profile (NOTICE.md safety patch)

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

NETWORK_IDLE_TIMEOUT_MS = 15_000
FALLBACK_SETTLE_MS = 4_000


def exact_size_scale(value: str) -> float:
    try:
        scale = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("scale must be a number") from exc
    if not math.isfinite(scale) or not 1 <= scale <= 4:
        raise argparse.ArgumentTypeError("scale must be between 1 and 4")
    return scale


def rasterize(
    src: pathlib.Path,
    out: pathlib.Path,
    scale: float = 2,
    *,
    network_idle_timeout_ms: int = NETWORK_IDLE_TIMEOUT_MS,
    fallback_settle_ms: int = FALLBACK_SETTLE_MS,
) -> None:
    # /draw: Windows Chromium calls LogonUser(user, ".", "") when a fresh profile opens a tab; ten failed logons lock the account. Record the password check in Local State (µs since 1601, far in the future) before launch.
    profile = tempfile.mkdtemp(prefix="diagram-export-")  # /draw:
    future_us = int((time.time() + 100 * 365 * 86400) * 1_000_000) + 11644473600 * 1_000_000  # /draw:
    pathlib.Path(profile, "Local State").write_text(json.dumps({"password_manager": {"os_password_blank": False, "os_password_last_changed": str(future_us)}}), encoding="utf-8")  # /draw:
    try:  # /draw: remove the seeded profile on every path
        _rasterize(src, out, scale, profile, network_idle_timeout_ms, fallback_settle_ms)
    finally:
        shutil.rmtree(profile, ignore_errors=True)  # /draw:


def _rasterize(src, out, scale, profile, network_idle_timeout_ms, fallback_settle_ms) -> None:  # /draw: the upstream body, launched on the seeded profile
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(profile, device_scale_factor=scale)  # /draw: replaces the fresh-profile launch
        try:
            page = browser.new_page()  # /draw: device_scale_factor moved to the launch above
            page.goto(
                src.resolve().as_uri() + "?motion=static",
                wait_until="domcontentloaded",
            )
            try:
                page.wait_for_load_state("networkidle", timeout=network_idle_timeout_ms)
            except PlaywrightTimeoutError:
                # Proxied networks may stall webfont subrequests past any deadline.
                # Cancel the outstanding load so capture cannot block on it again.
                page.evaluate("window.stop()")
                page.wait_for_timeout(fallback_settle_ms)
                print(
                    "warning: webfont request stalled - captured with fallback "
                    "typography; the PNG may not match the intended fonts",
                    file=sys.stderr,
                )
            page.evaluate("document.fonts.ready")
            if not page.locator("[data-motion-root]").evaluate_all(
                "roots => roots.every(root => root.dataset.frame === 'static')"
            ):
                raise RuntimeError("motion export requires a complete static frame")
            svg = page.locator("svg").first
            # Capture at one CSS pixel per viewBox unit before applying the multiplier.
            svg.evaluate(
                """el => {
                    const box = el.viewBox.baseVal;
                    if (![box.width, box.height].every(n => Number.isFinite(n) && n > 0))
                        throw new Error('PNG export requires a nonzero finite viewBox');
                    for (const [axis, size] of [['width', box.width], ['height', box.height]])
                        for (const prefix of ['', 'min-', 'max-'])
                            el.style.setProperty(prefix + axis, size + 'px', 'important');
                }"""
            )
            # Release every clipping ancestor so a wide SVG is captured whole.
            svg.evaluate(
                "el => { for (let a = el.parentElement; a; a = a.parentElement) "
                "a.style.setProperty('overflow', 'visible', 'important'); }"
            )
            svg.screenshot(path=out, omit_background=True)
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=pathlib.Path, help="diagram HTML input")
    parser.add_argument("out", type=pathlib.Path, help="PNG output")
    parser.add_argument("scale", nargs="?", type=exact_size_scale, default=2)
    args = parser.parse_args()
    rasterize(args.src, args.out, args.scale)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
