# -*- coding: utf-8 -*-
"""Functional suite - see Automation_Audit_Test_Cases.xlsx, suite 'Functional'."""
import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_func01_add_new_unique_value(guardrails, unique_value):
    """FUNC-01: a new unique value typed + Enter is appended as a chip and
    the input is cleared, ready for the next entry."""
    field = guardrails.email_patterns
    before_count = field.chip_count()

    field.add(unique_value)

    expect(field.chip(unique_value)).to_be_visible()
    assert field.chip_count() == before_count + 1
    assert field.input.input_value() == ""


@pytest.mark.functional
def test_func05_remove_existing_seeded_chip(guardrails):
    """FUNC-05: removing one existing (pre-seeded) chip leaves every other
    chip in the field untouched."""
    field = guardrails.subjects
    values_before = field.values()
    assert values_before, "expected at least one pre-seeded chip in 'Subjects'"
    target = values_before[0]

    field.remove(target)

    values_after = field.values()
    assert target not in values_after
    assert values_after == [v for v in values_before if v != target]
