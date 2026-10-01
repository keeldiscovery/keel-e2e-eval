"""The live journey under one questionnaire (spec `026-journey-one-questionnaire`).

Stackless, offline, and honest about what it can prove. S-012 is live: nothing here runs it, and
nothing here claims a green run. What these tests hold is the two things that **are** stackless and
that would have caught matrix run 36862514753 before a staging box was deployed and two model jobs
were bought:

1. **the scenario's own source** -- the shape `tests/test_journey_through_a_host.py` already uses:
   that the chips assertion is gone from the review step, that the three that stood with it still
   stand, that the step that now owns it is called where the founder waits, and that the ceiling is
   read off the host object rather than branched on by name;
2. **the new reader in `harness/refusals.py`** -- a pure function over the wire's own rows, which is
   the one piece of this spec that can be run for real.

The markup half -- that a review card with no questionnaire really does render no chips, and that
an approved card's `strip__read` really is the slice's founder-facing end -- is
`tests/test_review_card_chips_markup.py`, against keel-web's own markup.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import refusals

REPO = Path(__file__).resolve().parents[1]
SCENARIO = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text()


def _function_source(name: str) -> str:
    """The body of one top-level `def` in the scenario, up to the next top-level statement."""
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^\S)", SCENARIO, re.S | re.M)
    assert match, f"the scenario has no top-level `{name}`"
    return match.group(0)


def _code_of(name: str) -> str:
    """The same body with its `#` comment lines dropped.

    Load-bearing, not tidiness: the whole point of this spec is that the assertion it removes is
    **quoted** in the comment that replaced it, so a reader finds what left and why. A test that
    grepped the raw source would read that quotation as the assertion still standing -- and it did,
    on the first run of these tests.
    """
    return "\n".join(line for line in _function_source(name).splitlines()
                      if not line.strip().startswith("#"))


# ------------------------------------------------- phase 2: the review card asks for what it can have

def test_the_review_step_no_longer_requires_a_pick_list_on_every_line():
    """FR-002, and the whole of why this spec exists.

    keel-cloud 048 makes the questionnaire the project's, written by one `QUESTIONS` call after the
    last framed stage is approved. Every card `_read_the_lines` reads is read before that. Matrix
    run 36862514753 failed in under two minutes on the first of three.
    """
    body = _code_of("_read_the_lines")
    assert "assert all(line.get(\"chips\")" not in body, (
        "the review step still requires chips on every line -- the assertion run 36862514753 died "
        "on. It belongs to the questionnaire, not to a card drawn before one exists.")
    assert "offers no pick list at all" not in body, (
        "the old failure sentence is still in the review step")
    assert "assert all(line.get(\"chips\")" in _function_source("_read_the_lines"), (
        "the comment that replaced it no longer quotes it, so a reader cannot see what left")


def test_the_three_assertions_that_stood_beside_it_still_stand():
    """FR-001: numbered lines and a separated deal-breaker did not move, and nothing was weakened
    in the course of moving the fourth."""
    body = _function_source("_read_the_lines")
    assert "rendered no lines at all" in body
    assert "is unnumbered" in body
    assert "separates no deal-breaker" in body


def test_the_reason_stands_where_the_assertion_stood():
    """SC-003: a reader of the step can find the assertion that left it, and why, without opening
    keel-cloud. The three names are the three documents that decide it."""
    body = _function_source("_read_the_lines")
    for name in ("048", "026 FR-012", "36862514753"):
        assert name in body, f"the review step's comment never names {name}"
    assert "_the_questions_land" in body, (
        "the review step does not say where the moved assertion went")


def test_the_chips_are_still_recorded_so_the_bundle_keeps_the_number():
    """FR-003. A number that stops being asserted must not stop being written down: a run where a
    `SOLUTION` line carried chips is a run where keel-cloud 049's cross-stage half worked, and that
    is a finding for the bundle."""
    body = _code_of("_read_the_lines")
    assert "chipped" in body and "line.get(\"chips\")" in body, (
        "the review step records no chip count at all")
    assert "asserted nowhere" in body


def test_the_absence_of_chips_is_not_asserted_either():
    """FR-003. `assert not any(...)` here would go red on exactly the run that proves keel-cloud
    049 FR-013 works -- a later stage's line reading an earlier stage's measurement is given the
    referent's own control."""
    body = _code_of("_read_the_lines")
    assert "assert not chipped" not in body
    assert "049" in body, "the review step never says why an early chip is legal"
