"""§1.7's accounting, and the step that names the party (spec 028 T030, FR-018 … FR-022).

Four pure functions, held against **matrix run 36895521843's own numbers** — transcript seq 251's
`per stage` block, copied below byte for byte from the bundle. The run that produced them is the
whole reason this file exists: `COMMERCIAL` had five lines, every one `untested`, five people
answered, and the assertion of record failed **keel-web's panel** for drawing no rows it had
nothing to draw. A panel has two parts and no third (keel-web spec 027 FR-008…FR-012), so an
all-untested stage draws nothing and must.

So two things are asserted here and they pull in opposite directions on purpose:

1. an all-untested stage **passes** the panel accounting — the zero is correct on both sides;
2. the same stage **fails** §1.7a, and the message names the stranger or keel-cloud from
   `BeliefStanding`'s own `guessed` and `inside`/`outside`.
"""

from __future__ import annotations

import pytest

from evals.test_s012_journey_through_a_host import (_panel_accounting, _stage_anchoring,
                                                     _stage_lines, _tail_number, _tested_lines,
                                                     _whose_fault)
from harness.browser import Overview

#: `GET /standing`'s four lists as run 36895521843 sent them, flattened into the shape
#: `_stage_lines` reads. Seq 251: PROBLEM 3/2/2/0, SOLUTION 3/1/0/1, COMMERCIAL 0/0/0/5.
RUN_STANDING = {
    "holdingUp": ([{"stage": "PROBLEM"}] * 3) + ([{"stage": "SOLUTION"}] * 3),
    "notHoldingUp": ([{"stage": "PROBLEM"}] * 2) + ([{"stage": "SOLUTION"}] * 1),
    "peopleDisagree": ([{"stage": "PROBLEM"}] * 2),
    "untested": ([{"stage": "SOLUTION"}] * 1) + ([{"stage": "COMMERCIAL"}] * 5),
}


def _panel(held: int, failed: int, *, held_tail: str | None = None,
           failed_tail: str | None = None) -> dict:
    """A panel as `Overview.panels()` returns one: `parts` keyed by the part's own `dt`, each a
    list of line rows with the tail row — where there is one — among them."""
    parts = {}
    if held or held_tail:
        parts[Overview.PANEL_HELD] = ([{"heading": f"held {n}"} for n in range(held)]
                                      + ([{"more": held_tail}] if held_tail else []))
    if failed or failed_tail:
        parts[Overview.PANEL_DID_NOT_HOLD] = ([{"heading": f"fell {n}"} for n in range(failed)]
                                              + ([{"more": failed_tail}] if failed_tail else []))
    return {"stage": "PROBLEM", "parts": parts}


def _card(*beliefs: dict) -> dict:
    return {"groups": [{"roleLabel": "New parents",
                        "loadBearing": list(beliefs[:1]), "supporting": list(beliefs[1:])}]}


def _belief(**standing) -> dict:
    return {"statement": "something", "standing": {"verdict": "UNTESTED", **standing}}


# ---------------------------------------------------------------------------- tested, not total

def test_tested_is_the_three_lists_the_panel_has_somewhere_to_draw():
    counted = _stage_lines(RUN_STANDING, "PROBLEM")
    assert counted == {"holdingUp": 3, "notHoldingUp": 2, "peopleDisagree": 2, "untested": 0,
                       "holding": 3, "total": 7}
    assert _tested_lines(counted) == 7


def test_untested_is_not_in_it_because_a_panel_has_two_parts_and_no_third():
    counted = _stage_lines(RUN_STANDING, "SOLUTION")
    assert counted["untested"] == 1 and counted["total"] == 5
    assert _tested_lines(counted) == 4


def test_an_all_untested_stage_tests_nothing_at_all():
    counted = _stage_lines(RUN_STANDING, "COMMERCIAL")
    assert counted["total"] == 5 and counted["untested"] == 5
    assert _tested_lines(counted) == 0


# ------------------------------------------------------------------------------- the accounting

@pytest.mark.parametrize("stage,held,failed", [("PROBLEM", 3, 4), ("SOLUTION", 3, 1),
                                               ("COMMERCIAL", 0, 0)])
def test_the_red_runs_own_three_panels_all_account_for_their_tested_lines(stage, held, failed):
    """Seq 251's own rows. `DID NOT HOLD` carries the split lines as well as the failed ones --
    PROBLEM's `notHoldingUp 2` + `peopleDisagree 2` is four rows -- which is why the accounting is
    one sum against one sum (spec 028 D-04)."""
    counted = _stage_lines(RUN_STANDING, stage)
    account = _panel_accounting(_panel(held, failed), counted)
    assert account["rows the panel accounts for"] == account["tested on the wire"]


def test_the_commercial_panel_that_failed_the_old_assertion_passes_this_one():
    counted = _stage_lines(RUN_STANDING, "COMMERCIAL")
    account = _panel_accounting(_panel(0, 0), counted)
    # The old fault: `counted["total"] and not (held or failed)` -- five lines, no rows.
    assert counted["total"] == 5 and account["HELD rows shown"] == 0
    assert account["tested on the wire"] == 0 == account["rows the panel accounts for"]


def test_a_tail_counts_at_its_own_number_because_a_budget_never_deletes_a_line():
    assert _tail_number(None) == 0
    assert _tail_number("2 more ›") == 2
    assert _tail_number("1 more, worth knowing ›") == 1
    assert _tail_number("more ›") == 0
    counted = _stage_lines(RUN_STANDING, "PROBLEM")
    closed = _panel(3, 3, failed_tail="1 more ›")
    assert _panel_accounting(closed, counted)["rows the panel accounts for"] == 7


def test_counting_only_the_visible_rows_would_have_failed_a_closed_panel():
    """The red run had no tails at all on any of its three panels (seq 251: `[null, null]`), so an
    accounting that ignored them would have passed that run and failed the next one (D-06)."""
    counted = _stage_lines(RUN_STANDING, "PROBLEM")
    closed = _panel(3, 3, failed_tail="1 more ›")
    visible_only = (_panel_accounting(closed, counted)["HELD rows shown"]
                    + _panel_accounting(closed, counted)["DID NOT HOLD rows shown"])
    assert visible_only == 6 != _tested_lines(counted)


def test_a_panel_that_drops_a_tested_line_is_caught():
    counted = _stage_lines(RUN_STANDING, "PROBLEM")
    assert _panel_accounting(_panel(3, 3), counted)["rows the panel accounts for"] == 6


def test_a_panel_that_invents_a_line_is_caught_too():
    counted = _stage_lines(RUN_STANDING, "SOLUTION")
    # The untested line drawn as a row: four tested, five accounted for.
    assert _panel_accounting(_panel(3, 2), counted)["rows the panel accounts for"] == 5
    assert _tested_lines(counted) == 4


def test_no_panel_at_all_accounts_for_nothing_rather_than_raising():
    counted = _stage_lines(RUN_STANDING, "PROBLEM")
    assert _panel_accounting(None, counted)["rows the panel accounts for"] == 0


# --------------------------------------------------------------- how the answers were read

def test_the_anchoring_is_summed_over_every_belief_the_card_carries():
    card = _card(_belief(inside=3, outside=2, guessed=1, escaped=0),
                 _belief(inside=0, outside=0, guessed=5, escaped=0),
                 _belief(inside=1, outside=4, guessed=0, escaped=2))
    assert _stage_anchoring(card) == {"anchored": 10, "guessed": 6, "escaped": 2, "lines": 3}


def test_a_card_with_no_groups_reads_zero_rather_than_raising():
    assert _stage_anchoring({}) == {"anchored": 0, "guessed": 0, "escaped": 0, "lines": 0}
    assert _stage_anchoring({"groups": [{"loadBearing": [{"statement": "x"}]}]})["lines"] == 1


def test_the_red_runs_commercial_stage_is_the_strangers_fault():
    """Five people answered, every answer a guess, nothing anchored: `BeliefStanding.guessed` is
    keel-cloud's own *answers shown to the founder that count towards nothing*, which is exactly
    what the filler sentence earned."""
    verdict = _whose_fault({"anchored": 0, "guessed": 5, "escaped": 0, "lines": 5})
    assert verdict.startswith("THE STRANGER'S")
    assert "composed from their own facts" in verdict, "it says where to look in §2.3"


def test_a_stage_everybody_escaped_is_the_strangers_fault_too_and_says_so_differently():
    verdict = _whose_fault({"anchored": 0, "guessed": 0, "escaped": 5, "lines": 5})
    assert verdict.startswith("THE STRANGER'S") and "escape" in verdict


def test_answers_that_counted_on_a_stage_with_nothing_standing_is_keel_clouds():
    verdict = _whose_fault({"anchored": 12, "guessed": 0, "escaped": 0, "lines": 5})
    assert verdict.startswith("KEEL-CLOUD'S")
    assert "DRIFT.md" in verdict, "a product fault is a drift entry, never a workaround here"


def test_a_stage_nobody_answered_at_all_names_nobody_as_a_liar():
    """Zero everywhere is *nobody was asked*, which §1.7a never reaches: it only looks at a stage
    whose `peopleAnswered` is at least the number invited. Held here so the branch is documented
    rather than discovered."""
    assert _whose_fault({"anchored": 0, "guessed": 0, "escaped": 0, "lines": 5}).startswith(
        "KEEL-CLOUD'S")


# ------------------------------------------------------------------- the step, where it stands

def test_the_new_step_stands_between_the_reading_and_the_deck():
    """It is about the readings, not about a screen, and the step that can blame this harness has
    to run before the steps that blame the product (plan Decision 9)."""
    from pathlib import Path

    source = Path("evals/test_s012_journey_through_a_host.py").read_text()
    toast = source.index("§1.6: the host read the answer")
    new_step = source.index("§1.7a: every approved stage was tested by somebody")
    paragraph = source.index("§1.7: *What this says*")
    bands = source.index("§1.7: the deck -- one band per stage")
    assert toast < new_step < paragraph < bands


def test_the_assertion_that_named_the_wrong_party_is_gone_for_cause():
    from pathlib import Path

    source = Path("evals/test_s012_journey_through_a_host.py").read_text()
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    assert 'counted["total"] and not (held or failed)' not in code, (
        "the fault that read an all-untested stage as a panel bug is back -- a panel has two "
        "parts and no third, so an all-untested stage draws nothing and must (spec 028 FR-019)")
    assert "panel shows none of them" not in code, (
        "the old fault's own message is back -- it blamed keel-web for obeying its own spec")
    # And the comment that says why it went is still there, which is the half that survives
    # deletion (AGENTS.md: invert or move, never delete).
    assert "the assertion that used to stand here is gone" in source
