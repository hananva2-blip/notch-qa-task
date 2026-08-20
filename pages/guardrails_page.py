# -*- coding: utf-8 -*-
"""
Page Object for the 'Automation Audit' block of the Guardrails config page.

    Config > Automation > Guardrails > Automation Audit

The 4 fields in scope (Emails patterns to unassign / Subjects / Words in User
Message / Words in Assistant's Reply) are all built from the same repeated
component: a bordered box holding one chip <div> per existing value (each chip
is `<div>{value}<button>x</button></div>`) followed by a `<textarea>` that
creates a new chip on Enter.

The app does not expose stable `data-testid` / `aria-label` hooks on this
component (see A11Y-03 in the test case matrix), so this page object locates
each field by its own heading text and then scopes down from there, rather
than depending on the auto-generated styled-components class names (which are
not safe to hardcode - they change across builds). This is flagged as a
recommendation for the engineering team in the accompanying test plan.
"""
from __future__ import annotations

from playwright.sync_api import Page, Locator, expect


class AutomationAuditField:
    """One chip/tag-list field inside the Automation Audit section."""

    def __init__(self, page: Page, heading: str):
        self.page = page
        self.heading = heading
        # The heading text sits 3 DOM levels above the container that holds
        # both the existing chips and the <textarea> used to add new ones.
        self._heading_loc = page.get_by_text(heading, exact=True)
        self.container: Locator = self._heading_loc.locator("xpath=ancestor::div[3]")

    @property
    def input(self) -> Locator:
        return self.container.get_by_role("textbox")

    def _chip_entries(self) -> list[tuple[str, Locator]]:
        """(value, chip-div-locator) for every chip currently rendered.

        Each chip's remove control is a <button> whose direct parent is the
        chip <div> (`<div>{value}<button>x</button></div>`). Reading the
        button's own text and stripping it off the parent's inner_text()
        recovers the value directly from the DOM relationship, rather than
        splitting the whole container's text by line - which is fragile,
        since whether the browser's innerText algorithm puts the value and
        the remove glyph on the same visual line or not is layout-dependent
        and not something a test should rely on.
        """
        buttons = self.container.get_by_role("button")
        entries = []
        for i in range(buttons.count()):
            btn = buttons.nth(i)
            chip_div = btn.locator("xpath=..")
            full_text = chip_div.inner_text()
            btn_text = btn.inner_text()
            if btn_text and full_text.endswith(btn_text):
                value = full_text[: -len(btn_text)].strip()
            else:
                value = full_text.strip()
            entries.append((value, chip_div))
        return entries

    def chip(self, value: str) -> Locator:
        """The chip <div> for an exact value."""
        for v, chip_div in self._chip_entries():
            if v == value:
                return chip_div
        # No match: return a locator that resolves to nothing, so
        # `expect(...).to_be_hidden()`-style assertions still behave
        # sensibly for a value that isn't (or is no longer) present.
        return self.container.locator("xpath=.//*[false()]")

    def chip_count(self) -> int:
        # Every chip div has exactly one <button> (the remove control);
        # the trailing input has none, so counting buttons in the
        # container gives an accurate chip count.
        return self.container.get_by_role("button").count()

    def has_value(self, value: str) -> bool:
        return value in self.values()

    def values(self) -> list[str]:
        return [v for v, _ in self._chip_entries()]

    def add(self, value: str) -> None:
        self.input.click()
        self.input.fill(value)
        self.input.press("Enter")

    def remove(self, value: str) -> None:
        self.chip(value).get_by_role("button").click()


class GuardrailsPage:
    """Automation Audit section of the Guardrails config page."""

    def __init__(self, page: Page, base_url: str, version: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.version = version

    # -- navigation ----------------------------------------------------
    def goto(self) -> None:
        self.page.goto(f"{self.base_url}/config/guardrails?version={self.version}")
        self.email_patterns.container.scroll_into_view_if_needed()

    def reload(self) -> None:
        self.page.reload()
        self.email_patterns.container.scroll_into_view_if_needed()

    # -- the 4 fields in scope ------------------------------------------
    @property
    def email_patterns(self) -> AutomationAuditField:
        return AutomationAuditField(self.page, "Emails patterns to unassign")

    @property
    def subjects(self) -> AutomationAuditField:
        return AutomationAuditField(self.page, "Subjects")

    @property
    def words_in_user_message(self) -> AutomationAuditField:
        return AutomationAuditField(self.page, "Words in User Message")

    @property
    def words_in_assistant_reply(self) -> AutomationAuditField:
        return AutomationAuditField(self.page, "Words in Assistant's Reply")

    def all_fields(self) -> list[AutomationAuditField]:
        return [self.email_patterns, self.subjects, self.words_in_user_message,
                self.words_in_assistant_reply]

    # -- draft header: Deploy  <->  Discard / Save ----------------------
    @property
    def deploy_button(self) -> Locator:
        return self.page.get_by_role("button", name="Deploy", exact=True)

    @property
    def save_button(self) -> Locator:
        return self.page.get_by_role("button", name="Save", exact=True)

    @property
    def discard_button(self) -> Locator:
        return self.page.get_by_role("button", name="Discard", exact=True)

    def is_dirty(self) -> bool:
        return self.discard_button.is_visible()

    def save(self) -> None:
        self.save_button.click()

    def discard(self) -> None:
        self.discard_button.click()
        modal_discard = self.page.get_by_role("button", name="Discard", exact=True).last
        expect(self.page.get_by_text("Discard changes", exact=True)).to_be_visible()
        modal_discard.click()

    def keep_editing(self) -> None:
        self.discard_button.click()
        self.page.get_by_role("button", name="Keep editing").click()
