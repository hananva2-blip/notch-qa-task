# -*- coding: utf-8 -*-
"""
Shared fixtures for the Automation Audit test suite.

Configuration (env vars, all optional - sensible defaults point at the
feature instance used to design this suite):

    GUARDRAILS_BASE_URL   default: https://guardio.app.getnotch.dev
    GUARDRAILS_VERSION    default: NM-17AUGUST-143816
    GUARDRAILS_STORAGE_STATE
        Path to a Playwright storage_state JSON (cookies/localStorage) for
        an already-authenticated session, applied when Playwright launches
        its own browser. Works for apps whose session lives in a cookie or
        localStorage.
    GUARDRAILS_CDP_URL
        CDP endpoint (e.g. http://localhost:9222) of an already-running,
        manually-authenticated Chrome instance. When set, the suite attaches
        to that browser's existing, already-logged-in context instead of
        launching its own browser and replaying GUARDRAILS_STORAGE_STATE.

        This app's login goes through Google -> a Descope-based SSO
        (auth.getnotch.dev / auth.getnotch.com) and back to the app - but
        the app domain itself (guardio.app.getnotch.dev) never receives a
        capturable cookie or localStorage entry once logged in (confirmed
        by inspecting a captured storage_state: 46 cookies, all for Google
        and the auth/SSO domains, zero for the app domain, zero
        localStorage origins - while the browser that produced it was
        demonstrably fully logged into the real app). The session is
        evidently kept somewhere storage_state can't reach (most likely
        IndexedDB, or an in-memory token re-issued per load), so
        GUARDRAILS_STORAGE_STATE alone cannot authenticate a
        freshly-launched browser against this app. GUARDRAILS_CDP_URL
        sidesteps that by reusing the real, already-authenticated browser
        instead of trying to export/replay its session.

Every test that mutates the draft MUST end in a known-clean state (Discard,
never Save) so the suite can run repeatedly against the same shared DEV
draft without accumulating test data. The one exception (persistence via
Save) is intentionally left as a manual/CI-only case - see SMK-03 in the
test case matrix - rather than automated here, to avoid permanently
mutating shared environment data on every run.
"""
import os
import uuid

import pytest

from pages.guardrails_page import GuardrailsPage

BASE_URL = os.environ.get("GUARDRAILS_BASE_URL", "https://guardio.app.getnotch.dev")
VERSION = os.environ.get("GUARDRAILS_VERSION", "NM-17AUGUST-143816")
STORAGE_STATE = os.environ.get("GUARDRAILS_STORAGE_STATE")
CDP_URL = os.environ.get("GUARDRAILS_CDP_URL")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = {**browser_context_args, "viewport": {"width": 1456, "height": 900}}
    if STORAGE_STATE:
        args["storage_state"] = STORAGE_STATE
    return args


@pytest.fixture(scope="session")
def browser(playwright, browser_type, browser_type_launch_args):
    """Default: launch a fresh browser. If GUARDRAILS_CDP_URL is set,
    attach to an already-running, already-authenticated Chrome instead -
    see the module docstring for why that's needed against this app."""
    if CDP_URL:
        b = playwright.chromium.connect_over_cdp(CDP_URL)
        yield b
        # Don't close - it's the user's manually-managed debug browser,
        # not one this suite owns.
    else:
        b = browser_type.launch(**browser_type_launch_args)
        yield b
        b.close()


@pytest.fixture
def context(browser, browser_context_args):
    if CDP_URL:
        # Reuse the existing, already-authenticated context instead of
        # creating an empty new one (a fresh context on this same browser
        # would still be logged out).
        yield browser.contexts[0]
    else:
        ctx = browser.new_context(**browser_context_args)
        yield ctx
        ctx.close()


@pytest.fixture
def guardrails(page) -> GuardrailsPage:
    gp = GuardrailsPage(page, BASE_URL, VERSION)
    gp.goto()
    yield gp
    # Safety net: never leave a dirty/unsaved draft behind for the next test
    # or the next engineer who opens this draft.
    if gp.is_dirty():
        gp.discard()


@pytest.fixture
def unique_value():
    """A short, guaranteed-unique value for tests that add a new chip,
    so runs never collide with each other or with real seeded data."""
    return f"qa-{uuid.uuid4().hex[:8]}"
