# -*- coding: utf-8 -*-
"""Validation & Boundary suite - see Automation_Audit_Test_Cases.xlsx.

VAL-06 documents a real defect observed while exploring the feature: after a
rejected duplicate submission, the input can retain the leftover text and
concatenate it with the next value typed. The test is written to describe
the CORRECT expected behavior (input clears after a rejected duplicate) and
will FAIL against the current implementation - that failure is the point:
it is a regression guard for the fix.
"""
import pytest
from playwright.sync_api import expect


@pytest.mark.validation
def test_val01_empty_submit_creates_no_chip(guardrails):
    """VAL-01: pressing Enter on an empty input must not create a chip."""
    field = guardrails.words_in_assistant_reply
    before = field.chip_count()

    field.input.click()
    field.input.press("Enter")

    assert field.chip_count() == before
    assert not guardrails.is_dirty()


@pytest.mark.validation
def test_val03_leading_trailing_whitespace_is_trimmed(guardrails):
    """VAL-03: '  spaced word  ' is stored as 'spaced word' - outer
    whitespace trimmed, internal space between words preserved."""
    field = guardrails.words_in_assistant_reply

    field.add("   spaced word   ")

    assert "spaced word" in field.values()
    assert "   spaced word   " not in field.values()


@pytest.mark.validation
def test_val04_exact_duplicate_is_rejected(guardrails):
    """VAL-04: submitting a value that already exists must not create a
    second identical chip."""
    field = guardrails.email_patterns
    existing = field.values()
    assert "noreply" in existing, "expected the seeded 'noreply' pattern to be present"
    before_count = field.chip_count()

    field.add("noreply")

    assert field.chip_count() == before_count, "a duplicate chip was created"


@pytest.mark.validation
@pytest.mark.xfail(reason="Known defect (VAL-06): input retains stale text after a "
                           "rejected duplicate and concatenates it with the next entry.",
                    strict=False)
def test_val06_input_clears_after_rejected_duplicate(guardrails, unique_value):
    """VAL-06: after a duplicate is rejected, the input must be empty so the
    next typed value is not corrupted by leftover text."""
    field = guardrails.email_patterns
    assert "noreply" in field.values()

    field.input.click()
    field.input.fill("noreply")
    field.input.press("Enter")  # rejected as a duplicate

    assert field.input.input_value() == "", (
        "input still contains stale text after a rejected duplicate submission"
    )

    field.add(unique_value)
    expect(field.chip(unique_value)).to_be_visible()
    assert not field.has_value(f"{unique_value}noreply"), (
        "the stale 'noreply' text was concatenated onto the next entry"
    )
