"""
Connects to an already-running, manually-authenticated Chrome (started with
--remote-debugging-port=9222) and saves its session to state.json, so the
pytest suite can reuse it without ever driving a login screen itself.

Run this AFTER logging in manually in the separate debug Chrome window.
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    context.storage_state(path="state.json")
    browser.close()
    print("Saved state.json - the debug Chrome window can be closed now.")
