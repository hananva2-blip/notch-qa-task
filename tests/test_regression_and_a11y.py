# -*- coding: utf-8 -*-
"""Regression and Accessibility suites - see Automation_Audit_Test_Cases.xlsx."""
import pytest
from playwright.sync_api import expect


@pytest.mark.regression
def test_reg01_fields_are_isolated_from_one_another(guardrails, unique_value):
    """REG-01: adding a value to one field must not affect the other 3
    Automation Audit fields."""
    others = [f for f in guardrails.all_fields() if f.heading != "Subjects"]
    before = {f.heading: f.values() for f in others}

    guardrails.subjects.add(unique_value)

    after = {f.heading: f.values() for f in others}
    assert before == after, "an edit to 'Subjects' leaked into another field"


@pytest.mark.ui
def test_ui03_click_near_a_chip_boundary_does_not_remove_it(guardrails):
    """UI-03: a click aimed just outside a chip's remove ('x') control must
    not remove that chip. This reproduces a real slip observed during manual
    exploration, where a click intended for empty space in the input row
    landed on an adjacent chip's remove button and silently deleted it."""
    field = guardrails.email_patterns
    values_before = field.values()
    assert values_before, "expected at least one pre-seeded chip"
    last_chip = field.chip(values_before[-1])

    box = last_chip.bounding_box()
    assert box is not None
    # Click just past the chip's right edge (still inside the field's
    # container, in what should be empty space / the input area) rather
    # than on the chip or its remove button.
    guardrails.page.mouse.click(box["x"] + box["width"] + 40, box["y"] + box["height"] / 2)

    assert field.values() == values_before, (
        "a click near the chip boundary unexpectedly removed a chip"
    )


@pytest.mark.a11y
@pytest.mark.xfail(reason="Known defect (A11Y-03): remove buttons expose only the glyph "
                           "'x' with no aria-label, so a screen-reader user can't tell "
                           "which chip they're about to remove.",
                    strict=False)
def test_a11y03_remove_button_has_descriptive_accessible_name(guardrails):
    """A11Y-03: a chip's remove control should announce which value it
    removes (e.g. 'Remove noreply'), not just the glyph 'x'."""
    field = guardrails.email_patterns
    values = field.values()
    assert values
    target = values[0]
    remove_button = field.chip(target).get_by_role("button")

    accessible_name = remove_button.get_attribute("aria-label") or remove_button.inner_text()

    assert target.lower() in (accessible_name or "").lower(), (
        f"remove button's accessible name ({accessible_name!r}) does not "
        f"reference the chip value {target!r}"
    )
