# -*- coding: utf-8 -*-
"""Smoke suite - see Automation_Audit_Test_Cases.xlsx, sheet 'Test Cases', suite 'Smoke'."""
import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_smk02_add_one_value_to_each_field(guardrails, unique_value):
    """SMK-02: adding a value to each of the 4 fields creates a chip and
    marks the draft dirty (Deploy -> Discard/Save)."""
    expect(guardrails.deploy_button).to_be_visible()

    for i, field in enumerate(guardrails.all_fields()):
        value = f"{unique_value}-{i}"
        field.add(value)
        expect(field.chip(value)).to_be_visible()

    expect(guardrails.discard_button).to_be_visible()
    expect(guardrails.save_button).to_be_visible()
    expect(guardrails.deploy_button).to_be_hidden()


@pytest.mark.smoke
def test_smk04_remove_a_chip(guardrails):
    """SMK-04: removing a chip deletes it immediately and dirties the draft.

    Removes one of the pre-existing (seeded) chips rather than one just
    added in this test, so the net change versus the saved draft is
    unambiguous (add-then-remove-the-same-value in one flow nets back to
    the original saved state, which is a separate, not-yet-confirmed
    question about the app's dirty-tracking - see STATE-06 in the matrix)."""
    field = guardrails.subjects
    values_before = field.values()
    assert values_before, "expected at least one pre-seeded chip in 'Subjects'"
    target = values_before[0]

    field.remove(target)

    expect(field.chip(target)).to_be_hidden()
    assert guardrails.is_dirty()


@pytest.mark.smoke
def test_smk05_discard_reverts_all_pending_changes(guardrails, unique_value):
    """SMK-05: Discard (after confirming the modal) reverts every field to
    its last saved state and the header returns to 'Deploy'."""
    before = {f.heading: f.values() for f in guardrails.all_fields()}

    for i, field in enumerate(guardrails.all_fields()):
        field.add(f"{unique_value}-{i}")
    assert guardrails.is_dirty()

    guardrails.discard()

    expect(guardrails.deploy_button).to_be_visible()
    after = {f.heading: f.values() for f in guardrails.all_fields()}
    assert before == after, "fields did not revert to their pre-edit state"
