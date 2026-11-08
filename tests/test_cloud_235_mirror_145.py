"""Spec 145 -- the harness mirrors keel-cloud spec 235 (keel-cloud-docs master `74a04fb5`: the review rewrites the ladder
as one scale, and puts a rival aside rather than rewording it into the own row).

- FR-1 the mirrors: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at 235's
  `CARDS_SHA256` (Current solution §2 *The notes*, Importance §2 *The notes under the rows*); the band's new first line
  (`ReviewedRows.changed`: *Keel rewrote the scale so every answer is a step in {measure}.*) where the ladder was
  rewritten whole, 232's count line where the measure was dropped -- read by `review_band` / `lists_reviewed` and the
  bundle as served, whichever line it is.
- FR-3 the walk: nothing new -- a ladder with rungs 2-5 changed (Codyco's five as 235 FR-7 has them) passes the strict
  rung checks (spec 064 FR-5a) by `typed`; the walk plans no edit and never presses Put back.

No stack, no model, no key: the cloud's files are read where the checkout is there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from harness import vectors_script as vs
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
#: keel-cloud 235 FR-6: `RespondentReview.CARDS_SHA256` at keel-cloud-docs `74a04fb5` (was `98b7379b...`, 233).
CARDS_SHA256_235 = "3041f69cc95ae3ae951e5fd7a393c89acdc05ff31e9b67f3d48261ee4220ebcc"
CS = "problem.current_solution_satisfaction"

#: keel-cloud 235 FR-4 (`ReviewedRows.changed`): the band's first line where the ladder was rewritten whole.
SCALE_LINE = "Keel rewrote the scale so every answer is a step in {measure}."
MEASURE = "how soon a missed call was called back"

# keel-cloud 235 tasks.md, *What Codyco's Current solution Check serves with the switch on* (`TheLadderReadBackJourneyTest`):
# saved as cycle 16 saved it, the second answer applied whole (contract 63: `items[i].typed` / `why`, `changed`).
RUNGS_TYPED = ["Every missed call called back within the hour", "All called back that day",
               "Some called back when there was time", "Few were ever called back",
               "Calls that rang out were simply lost"]
RUNGS_SERVED = ["Every missed call called back within the hour", "All called back that day",
                "Called back the next day", "Called back days later", "Never called back"]
WHY = ["This rung grades whether and when calls got called back at all, not how soon.",
       "This rung grades how many calls were called back, not how soon.",
       "This rung grades whether a call was called back at all, not how soon."]
LADDER = {
    "items": [{"code": "outcome_1", "label": RUNGS_SERVED[0]}, {"code": "outcome_2", "label": RUNGS_SERVED[1]},
              *[{"code": f"outcome_{n + 3}", "label": RUNGS_SERVED[n + 2], "typed": RUNGS_TYPED[n + 2], "why": WHY[n]}
                for n in range(3)]],
    "phrase": "calling back guests whose calls rang out", "line": 2, "lineAfter": 1,
    "changed": {"line": SCALE_LINE.format(measure=MEASURE), "why": WHY[0]}}
#: The measure dropped (its own hold failed, or a put back dropped it): the same rows, 232's count line.
COUNTED = {**LADDER, "changed": {"line": "Keel changed three answers so they sit on one scale.", "why": WHY[0]}}


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------- FR-1 the cards

def test_the_reader_digest_is_235s_cards():
    """FR-1: the reader's cards are the cloud's vendored copy byte for byte, at 235's digest (the one constant the
    earlier pins read, `CARDS_SHA256_141`, moved with it) -- or a later round's (eval spec 147 moved the copy to
    keel-cloud 236 and 237's, `CARDS_SHA256_141`)."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_141
    assert sha in (CARDS_SHA256_235, CARDS_SHA256_141)
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours


def test_the_two_amended_sections_say_one_scale_and_put_aside():
    """FR-1 (235 FR-6): Current solution §2 -- the five rewritten as one scale on the first rung's measure, never a
    condition, held whole, one more turn, the band's new line; Importance §2 -- a part, a cause or a means put aside,
    never reworded."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "**The review rewrites the five as one scale** (specs 232, 235)" in text
    assert "never a condition or the reason it went that way" in text
    assert "Code holds the ladder whole or not at all" in text
    assert "the review is asked once more for the whole ladder, inside the Save's hold" in text
    assert "*Keel rewrote the scale so every answer is a step in {measure}.*" in text
    assert "**The review may change such a rival** (keel-cloud 232, 235)" in text
    assert "is **put aside, never reworded**" in text
    assert "*Choosing a seat where they can see every face*" in text
    assert "for each other rung that grades something else" not in text


# ------------------------------------------------------------------------------------------- FR-1 the band

def test_the_band_lines_are_the_clouds():
    """FR-1 (235 FR-4): the two Current solution lines the mirror fixtures carry are `ReviewedRows.changed`'s words."""
    rows = _cloud(VECTORS + "ReviewedRows.java")
    head, tail = SCALE_LINE.split("{measure}")
    assert f'new Changed("{head}" + list.measure()' in rows and f'+ "{tail}", why)' in rows
    assert '"Keel changed " + count(changed) + (changed == 1 ? " answer so it sits"' in rows
    assert '" answers so they sit") + " on one scale."' in rows
    assert "if (list.measure() != null && changed > 0)" in rows


def test_the_band_is_read_as_served_whichever_line():
    """FR-1: `review_band` / `lists_reviewed` / the bundle's line read the line served -- the new one where the ladder
    was rewritten whole, 232's where the measure was dropped; the changed rows the same either way."""
    assert vs.review_band(LADDER) == {"line": SCALE_LINE.format(measure=MEASURE), "why": WHY[0]}
    assert vs.review_band(COUNTED) == {"line": "Keel changed three answers so they sit on one scale.", "why": WHY[0]}
    assert vs.review_changed(LADDER) == vs.review_changed(COUNTED) == [
        {"typed": t, "label": lbl, "why": w} for t, lbl, w in zip(RUNGS_TYPED[2:], RUNGS_SERVED[2:], WHY)]
    views = {"PROBLEM": {"questions": [{"dimension": CS, "answer": {"list": LADDER}}]}}
    reviewed = vs.lists_reviewed(views)
    assert reviewed[CS]["band"]["line"] == SCALE_LINE.format(measure=MEASURE)
    j = SimpleNamespace(project=lambda path: path,
                        get=lambda path: views["PROBLEM"] if path == "/calibration/PROBLEM" else {})
    md = bt.markdown({"lists_reviewed": bt.lists_reviewed(j), "respondents": {}, "founder_screens": []})
    assert (f"- The review changed {CS}: *{SCALE_LINE.format(measure=MEASURE)}* '{RUNGS_TYPED[2]}' -> "
            f"'{RUNGS_SERVED[2]}'; '{RUNGS_TYPED[3]}' -> '{RUNGS_SERVED[3]}'; '{RUNGS_TYPED[4]}' -> "
            f"'{RUNGS_SERVED[4]}'") in md
