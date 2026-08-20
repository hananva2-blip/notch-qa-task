# -*- coding: utf-8 -*-
"""
Shared fixtures for the Automation Audit test suite.

Configuration (env vars, all optional - sensible defaults point at the
feature instance used to design this suite):

    GUARDRAILS_BASE_URL   default: https://guardio.app.getnotch.dev
    GUARDRAILS_VERSION    default: NM-17AUGUST-143816
    GUARDRAILS_STORAGE_STATE
        Path to a Playwright storage_state JSON (cookies/localStorage) for an
        already-authenticated session. The app did not present a login
        screen during exploration, but production/staging almost certainly
        requires SSO - export a storage state once via
        `playwright codegen --save-storage=state.json <url>` after logging
        in manually, and point this env var at it.

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


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = {**browser_context_args, "viewport": {"width": 1456, "height": 900}}
    if STORAGE_STATE:
        args["storage_state"] = STORAGE_STATE
    return args


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
