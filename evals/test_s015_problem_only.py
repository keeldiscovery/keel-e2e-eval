"""S-015: the problem study, short (spec 071 FR-2; keel-cloud 133, keel-web 109).

01-countly as a problem study (`evals/scope_journey.problem_entry`): the choose screen's problem card, Context, the
problem chat and its four calibrations, *Before people see it* (the word and who asks -- no pilot), the lock; one link a
restaurant manager; each walks the gate, the story and part 1 and meets the thank-you with no pilot box. Countly's own
four problem standings, held; the Overview reads *Should you build it?*, no Pilot tab, no tiles, one card and a one-piece
ship; the decision by the rule (Current solution split them: *Not yet*). SC1-SC8 (`evals/scope_marks.py`).
"""

from __future__ import annotations

from evals import scope_journey


def test_s015_problem_only(stack, founder_one, browser, run_dir):
    scope_journey.run(stack, founder_one, browser, run_dir, scope="PROBLEM", entry_from=scope_journey.problem_entry,
                      slug="s015-problem-only")
