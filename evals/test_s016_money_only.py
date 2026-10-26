"""S-016: money alone, B2B, short (spec 071 FR-3; keel-cloud 133, keel-web 109).

01-countly with the restaurant owner deciding (`evals/scope_journey.money_entry`), as money alone: the choose screen's
money card, Context with no recall window, the problem chat, the idea card (*Your idea*), who decides, the money
calibration, the lock; **only the decision-maker's link** is issued, one an owner; each opens with the problem in one
spoken sentence, the idea card, then part 3 (no gate). The Overview reads *Will they pay?*, the Pilot and *What they
would pay* tiles, one card, a one-piece ship; the decision by the rule. SC1-SC7 (`evals/scope_marks.py`).
"""

from __future__ import annotations

from evals import scope_journey


def test_s016_money_only(stack, founder_one, browser, run_dir):
    scope_journey.run(stack, founder_one, browser, run_dir, scope="COMMERCIAL", entry_from=scope_journey.money_entry,
                      slug="s016-money-only")
