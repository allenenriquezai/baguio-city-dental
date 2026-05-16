#!/usr/bin/env python3
"""
capture_gaps2.py — Fix GMB review count + Parlon Baguio + WhatClinic.

Run from the ink-arch-mary-jane/ folder.
"""

import time
import re
from pathlib import Path

OUT = Path(__file__).parent
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            timezone_id="Asia/Manila",
        )
        # Hide webdriver flag
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        # --- GMB: extract review count ---
        print("\n=== Gap 2: INK & ARCH GMB ===")
        page.goto(
            "https://www.google.com/maps/search/INK+%26+ARCH+by+Mary+Jane+Ledda+Baguio",
            timeout=30000, wait_until="domcontentloaded"
        )
        time.sleep(8)
        # Try to click the first place result
        try:
            result = page.query_selector('[data-result-index="0"] a') or page.query_selector('a[data-item-id]')
            if result:
                result.click()
                time.sleep(5)
        except Exception:
            pass
        # Dump sidebar text to find review count
        sidebar_text = ""
        try:
            sidebar = page.query_selector('[role="main"]') or page.query_selector('[aria-label*="INK"]')
            if sidebar:
                sidebar_text = sidebar.inner_text()
            else:
                sidebar_text = page.inner_text("body")
        except Exception:
            sidebar_text = page.inner_text("body")

        print("--- sidebar text sample ---")
        # Print lines that likely contain the review count
        for line in sidebar_text.split("\n"):
            line = line.strip()
            if line and any(x in line.lower() for x in ["review", "rating", "5.", "4.", "3.", "(", "star"]):
                print(f"  {repr(line)}")

        # Extract count
        review_count = "unknown"
        m = re.search(r"\(([\d,]+)\)", sidebar_text)
        if m:
            review_count = m.group(1).replace(",", "")
        else:
            m = re.search(r"([\d,]+)\s+review", sidebar_text, re.IGNORECASE)
            if m:
                review_count = m.group(1).replace(",", "")
        print(f"\nGoogle review count: {review_count}")

        # Screenshot with panel open
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.screenshot(path=str(OUT / "screenshot-gap-2.png"),
                        clip={"x": 0, "y": 0, "width": 1280, "height": 900})
        print(f"saved: screenshot-gap-2.png ({(OUT/'screenshot-gap-2.png').stat().st_size//1024}KB)")

        # --- Parlon: search Baguio brows in UI ---
        print("\n=== Gap 3: Parlon Baguio ===")
        page.goto("https://www.parlon.ph/parlon/happy-brows/happy-brows-sm-baguio/services",
                  timeout=30000, wait_until="domcontentloaded")
        time.sleep(6)
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.screenshot(path=str(OUT / "screenshot-gap-3-parlon-happybrows.png"),
                        clip={"x": 0, "y": 0, "width": 1280, "height": 900})
        print(f"saved: screenshot-gap-3-parlon-happybrows.png ({(OUT/'screenshot-gap-3-parlon-happybrows.png').stat().st_size//1024}KB)")

        # Now load Parlon and use the search to show no INK & ARCH
        page.goto("https://www.parlon.ph", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        try:
            search_box = page.query_selector('input[type="search"]') or page.query_selector('input[placeholder*="search"]') or page.query_selector('input[placeholder*="Search"]')
            if search_box:
                search_box.click()
                time.sleep(0.5)
                search_box.type("INK ARCH Baguio", delay=80)
                time.sleep(3)
                page.screenshot(path=str(OUT / "screenshot-gap-3-parlon-search.png"),
                                clip={"x": 0, "y": 0, "width": 1280, "height": 900})
                print(f"saved: screenshot-gap-3-parlon-search.png ({(OUT/'screenshot-gap-3-parlon-search.png').stat().st_size//1024}KB)")
        except Exception as e:
            print(f"Parlon search attempt failed: {e}")

        # --- WhatClinic with anti-bot bypass ---
        print("\n=== Gap 3: WhatClinic Baguio ===")
        page.goto("https://www.whatclinic.com", timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)
        page.goto("https://www.whatclinic.com/cosmetic-plastic-surgery/philippines/baguio-city",
                  timeout=30000, wait_until="domcontentloaded")
        time.sleep(6)
        wc_text = page.inner_text("body")
        print("WhatClinic page text sample:")
        for line in wc_text.split("\n")[:30]:
            if line.strip():
                print(f"  {line.strip()}")
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.screenshot(path=str(OUT / "screenshot-gap-3-whatclinic.png"),
                        clip={"x": 0, "y": 0, "width": 1280, "height": 900})
        print(f"saved: screenshot-gap-3-whatclinic.png ({(OUT/'screenshot-gap-3-whatclinic.png').stat().st_size//1024}KB)")

        page.close()
        browser.close()

    print(f"\n=== FINAL: Google review count = {review_count} ===")


if __name__ == "__main__":
    main()
