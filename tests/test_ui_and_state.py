# -*- coding: utf-8 -*-
"""UI/UX and State Management suites - see Automation_Audit_Test_Cases.xlsx."""
import pytest
from playwright.sync_api import expect


@pytest.mark.ui
def test_ui05_header_reflects_dirty_state(guardrails, unique_value):
    """UI-05: the header swaps 'Deploy' for 'Discard'/'Save' the instant a
    field becomes dirty, and swaps back once changes are discarded."""
    expect(guardrails.deploy_button).to_be_visible()
    expect(guardrails.discard_button).to_be_hidden()

    guardrails.subjects.add(unique_value)

    expect(guardrails.discard_button).to_be_visible()
    expect(guardrails.save_button).to_be_visible()
    expect(guardrails.deploy_button).to_be_hidden()

    guardrails.discard()

    expect(guardrails.deploy_button).to_be_visible()
    expect(guardrails.discard_button).to_be_hidden()


@pytest.mark.ui
def test_ui06_discard_modal_keep_editing_preserves_pending_edit(guardrails, unique_value):
    """UI-06: 'Keep editing' in the Discard confirmation modal must cancel
    the discard and leave the pending edit in place."""
    field = guardrails.words_in_assistant_reply
    field.add(unique_value)
    assert guardrails.is_dirty()

    guardrails.keep_editing()

    expect(field.chip(unique_value)).to_be_visible()
    assert guardrails.is_dirty(), "edit was lost even though 'Keep editing' was chosen"


@pytest.mark.state
def test_state02_discarded_add_does_not_survive_reload(guardrails, unique_value):
    """STATE-02: an added-then-discarded value must not reappear after a
    page reload (confirms Discard never reached persistence)."""
    field = guardrails.email_patterns
    field.add(unique_value)
    guardrails.discard()

    guardrails.reload()

    assert not guardrails.email_patterns.has_value(unique_value)
