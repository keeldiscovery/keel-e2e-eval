"""S-014: the healthy project -- every dimension holding up on ten or more, nobody owed a follow-up (spec 052 FR-7;
keel-cloud 104, keel-web 077; design `report-and-follow-up-design-2026-10-17.md` §4.2 *Nothing is failing*, D9).

**Judgement call 1: a built entry, not a real one.** No revision-11 corpus entry holds on every dimension on ten or more
-- every one of the seven has a vector not holding up, split or too few (`expected.vector_verdicts`) -- so the journey
walks 05-paidly with every person supporting (`evals/preludes.healthy_entry`), the way keel-cloud's
`InsightsSimulationTest` builds its baseline from the same entry: the founder's market, statements, lists, calibration
and window are 05-paidly's own; the answers are ten specialists and ten decision-makers who each support every rung.
Its expected standings were held once to keel-cloud's own engine at zero spend (16 of 16, `instructions/compare.py`).

What only this journey says, on top of everything the corpus legs hold:

* **nobody is owed a follow-up**: every served standing holds up on n >= 10, `insights[]` is empty, and no person row
  on a stage page carries a `followUp` (051's IM23 none case is the walk's to see on both links);
* **the Insights view is *Nothing is failing*** (`report_insights`), the Pilot view lists the corpus's sign-ups
  (`report_pilot`), and the binding ends after page 3 and the breakdown, with no *In their words* and no *What to do
  next* (`report_binding`); `report_no_repeat` holds on the empty view;
* all five report marks were measured and met.
"""

from __future__ import annotations

from evals import corpus_scenario, preludes
from evals import report_marks

ENTRY_ID = preludes.HEALTHY_FROM


def _green_extras(j) -> None:
    dims = [d for v in j.standings.get("vectors") or [] for d in v.get("dimensions") or []]
    with j.recorder.step("S-014: every dimension holds up on ten or more and nobody is owed a follow-up -- no insight, "
                         "no follow-up on any person's row", party="founder", kind="assert") as h:
        weak = [(d.get("dimension"), d.get("status"), d.get("n")) for d in dims
                if d.get("status") != "HOLDING_UP" or int(d.get("n") or 0) < preludes.HEALTHY_N]
        followed = [(d.get("dimension"), p.get("personName")) for d in dims for p in d.get("people") or []
                    if p.get("followUp")]
        h.record_assert({"weak": [], "insights": [], "follow-ups": []},
                        {"weak": weak, "insights": j.standings.get("insights"), "follow-ups": followed,
                         "decision": ((j.standings.get("facts") or {}).get("decision") or {}).get("label")})
        assert not weak, weak
        assert j.standings.get("insights") == [], j.standings.get("insights")
        assert not followed, followed
        assert ((j.standings.get("facts") or {}).get("decision") or {}).get("label") == "BUILD"
    with j.recorder.step("S-014: the report says nothing more -- Nothing is failing, the sign-ups listed, the binding "
                         "ending after page 3 and the breakdown; all five report marks measured and met",
                         party="founder", kind="assert") as h:
        card = j.screens.get("report-marks") or {}
        checks = {c["mark"]: c for c in card.get("checks") or []}
        insights = j.screens.get("insights") or {}
        pages = [p.get("page") for p in (j.screens.get("printed") or {}).get("pages") or []]
        h.record_assert({"marks": {m: True for m in report_marks.MARK_NAMES}, "empty": "Nothing is failing",
                         "pages": "1, 2, 3, then the breakdown"},
                        {"marks": {m: (c["measured"], c["ok"]) for m, c in checks.items()},
                         "empty": insights.get("empty"), "pages": pages})
        assert all(checks.get(m, {}).get("measured") and checks[m]["ok"] for m in report_marks.MARK_NAMES), checks
        assert "Nothing is failing" in (insights.get("empty") or ""), insights.get("empty")
        assert pages[:3] == [1, 2, 3] and len(pages) >= 4, pages


def test_s014_green(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir, entry_id=ENTRY_ID, slug="s014-green",
                        extra=_green_extras, entry_from=preludes.healthy_entry)
