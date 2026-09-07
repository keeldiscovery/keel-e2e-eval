"""D5, every opener, judged against canned DOMs (spec 010 FR-018/FR-033, T036).

`judge_opener` is a pure function over three reads of one region, so every verdict it can reach is
exercised here with no browser: **opens what it names**, **opens nothing**, and **opens but cannot
close**. The browser half (`open_opener`) is a mechanic -- it clicks and reads -- and the rule it
defers to is the one below.
"""

from __future__ import annotations

from harness import doors

# The opened card, as `StageRoute.tsx` renders it: a collapsed strip, and the same strip with its
# said box open. The region a scenario reads is the card.
COLLAPSED = "1. It costs hours, not minutes  deal-breaker  You said one to two hours."
EXPANDED = COLLAPSED + "  Dana Okafor  A payroll manager  “Last Tuesday I spent about two hours.”"
WRONG_PERSON = COLLAPSED + "  Wei Zhang  A payroll manager  “It lands on my desk every time.”"


def test_an_opener_that_opens_what_it_names_and_closes_back():
    v = doors.judge_opener(before=COLLAPSED, opened=EXPANDED, closed=COLLAPSED,
                            names="Dana Okafor")
    assert v.verdict == "opens"
    assert "closed back" in v.detail


def test_an_opener_that_reveals_nothing_is_d5():
    """A dot that is clicked and nothing appears. Dead in exactly the way a link to a blank page
    is dead -- which is why it gets a verdict rather than a shrug."""
    v = doors.judge_opener(before=COLLAPSED, opened=COLLAPSED, closed=COLLAPSED,
                            names="Dana Okafor")
    assert v.verdict == "opens_nothing"
    assert "nothing appeared" in v.detail


def test_an_opener_that_opens_somebody_elses_box_has_not_opened_what_it_names():
    """The control is labelled `Dana Okafor` and opens Wei Zhang's answer. Calling that "opens"
    would be the referee agreeing with the screen."""
    v = doors.judge_opener(before=COLLAPSED, opened=WRONG_PERSON, closed=COLLAPSED,
                            names="Dana Okafor")
    assert v.verdict == "opens_nothing"
    assert "not what the control names" in v.detail


def test_an_opener_that_will_not_close_back():
    v = doors.judge_opener(before=COLLAPSED, opened=EXPANDED, closed=EXPANDED,
                            names="Dana Okafor")
    assert v.verdict == "cannot_close"
    assert "close back" in v.detail


def test_a_one_way_reveal_is_judged_on_opening_alone():
    """A chip tap on the participant page reveals a *say roughly* box and there is nothing to
    close. `closed=None` says so rather than inventing a second click."""
    v = doors.judge_opener(before="How long did it take?",
                            opened="How long did it take? more than 1 day, say roughly  roughly how much?",
                            closed=None, names="roughly how much?")
    assert v.verdict == "opens"
    assert "one-way by design" in v.detail


def test_an_opener_promising_nothing_in_particular_is_judged_on_size_alone():
    v = doors.judge_opener(before="What it measures", opened="What it measures  1. It costs hours",
                            closed="What it measures")
    assert v.verdict == "opens"


def test_the_new_verdicts_are_in_the_registry_and_the_old_five_are_untouched():
    assert "opens_nothing" in doors.VERDICTS
    assert "cannot_close" in doors.VERDICTS
    for keel_clouds_own in ("opens", "not_found", "blank", "failed_request", "unreachable"):
        assert keel_clouds_own in doors.VERDICTS


def test_opener_rows_carry_the_control_its_promise_and_its_verdict():
    openers = [doors.Opener(source="/p/abc/s/PROBLEM", label="Dana Okafor", names="Dana Okafor")]
    rows = doors.opener_rows(openers, [doors.judge_opener(
        before=COLLAPSED, opened=EXPANDED, closed=COLLAPSED, names="Dana Okafor")])
    assert rows == [{"source": "/p/abc/s/PROBLEM", "label": "Dana Okafor", "names": "Dana Okafor",
                     "verdict": "opens", "detail": rows[0]["detail"]}]
