#!/usr/bin/env python3
"""
capture_gaps.py — Grab all missing screenshots for INK & ARCH audit.

Captures:
  screenshot-gap-2.png            INK & ARCH GMB panel (review count)
  screenshot-gap-3-parlon.png     Parlon Baguio brows search — no INK & ARCH
  screenshot-gap-3-whatclinic.png WhatClinic Baguio — only Derm Avenue listed

Also prints the Google review count to stdout.
"""

import time
import re
from pathlib import Path

OUT = Path(__file__).parent

# Real Chrome UA to avoid bot blocks
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def shot(page, out_path, height=900):
    page.keyboard.press("Escape")
    time.sleep(0.5)
    page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": 1280, "height": height})
    print(f"   saved: {out_path.name} ({out_path.stat().st_size // 1024}KB)")


def get_gmb_review_count(page):
    try:
        # Try span with review count (Google Maps renders "X reviews" in an aria-label on the star button)
        text = page.inner_text("body")
        # Pattern: "5.0 (12)" or "12 reviews" or "(12)"
        m = re.search(r"\((\d[\d,]*)\)", text)
        if m:
            return m.group(1).replace(",", "")
        m = re.search(r"([\d,]+)\s+review", text, re.IGNORECASE)
        if m:
            return m.group(1).replace(",", "")
    except Exception as e:
        print(f"   review parse error: {e}")
    return "unknown"


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        ctx = browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = ctx.new_page()

        # --- Gap 2: INK & ARCH GMB ---
        print("\n=== Gap 2: INK & ARCH Google Maps ===")
        gmb_url = "https://www.google.com/maps/search/INK+%26+ARCH+by+Mary+Jane+Ledda+Baguio"
        page.goto(gmb_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(8)
        # Click the first result to open the panel
        try:
            first = page.query_selector('a[href*="/maps/place/"]')
            if first:
                first.click()
                time.sleep(5)
        except Exception:
            pass
        review_count = get_gmb_review_count(page)
        print(f"   Google review count: {review_count}")
        shot(page, OUT / "screenshot-gap-2.png", height=900)

        # --- Gap 3: Parlon — search Baguio brows ---
        print("\n=== Gap 3: Parlon Baguio brows ===")
        # Use the working search URL for Baguio + brows category
        parlon_url = "https://www.parlon.ph/all-parlon-deals?c=brows&location=Baguio+City"
        page.goto(parlon_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(7)
        # Dismiss any modals
        for sel in ['button[aria-label*="lose"]', 'button:has-text("Close")', 'button:has-text("No")', '[class*="modal-close"]']:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.click()
                    time.sleep(1)
            except Exception:
                pass
        shot(page, OUT / "screenshot-gap-3-parlon.png", height=900)

        # --- Gap 3: WhatClinic Baguio with real UA ---
        print("\n=== Gap 3: WhatClinic Baguio ===")
        wc_url = "https://www.whatclinic.com/cosmetic-plastic-surgery/philippines/baguio-city"
        page.goto(wc_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(6)
        shot(page, OUT / "screenshot-gap-3-whatclinic.png", height=900)

        page.close()
        browser.close()

    print(f"\n=== DONE ===")
    print(f"Google review count for INK & ARCH: {review_count}")
    print("Update audit.md competitor table with this number.")


if __name__ == "__main__":
    main()
