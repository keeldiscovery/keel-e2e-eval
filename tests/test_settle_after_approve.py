"""`settle_after_approve` -- the one read between the approve click and the wire assertion.

Found live (S-012 on Copilot, `runs/20260910T223341Z-s012-copilot-host-and-thinker-live`): the
approve click hit keel-cloud's Q6 (the introduction named the expected role), the apply was
refused, the one retry (keel-cloud DRIFT #38) redrew the card ten seconds later, and the harness
-- which had only ever waited for the button to leave -- asserted "approved" against a card that
was back in front of the founder, unapproved. Stackless: the browser is three lambdas.
"""

from harness.browser import settle_after_approve


def _clock(steps):
    it = iter(steps)
    return lambda: next(it)


def test_the_approved_note_settles_it_at_once():
    slept = []
    out = settle_after_approve(is_approved=lambda: True, is_offered=lambda: False,
                               sleep=lambda: slept.append(1), clock=_clock([0.0, 0.0]))
    assert out == "approved"
    assert slept == []


def test_the_approve_button_coming_back_is_a_redraw():
    polls = iter([False, False, True])
    out = settle_after_approve(is_approved=lambda: False, is_offered=lambda: next(polls),
                               sleep=lambda: None, clock=_clock([0.0, 1.0, 2.0, 3.0]))
    assert out == "redrawn"


def test_neither_within_the_budget_is_unsettled_never_a_guess():
    out = settle_after_approve(is_approved=lambda: False, is_offered=lambda: False,
                               sleep=lambda: None, timeout_s=5.0,
                               clock=_clock([0.0, 1.0, 3.0, 6.0]))
    assert out == "unsettled"


def test_an_approved_note_beats_a_button_that_is_also_there():
    out = settle_after_approve(is_approved=lambda: True, is_offered=lambda: True,
                               sleep=lambda: None, clock=_clock([0.0, 0.0]))
    assert out == "approved"
