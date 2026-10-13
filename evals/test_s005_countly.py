"""S-005: `01-countly`, the B2C entry, walked through the vector corridor (spec 039).

Countly is the corpus's B2C entry with the most people (twelve), and it earns its place three ways:

* **one respondent type.** The owner-manager has the problem, uses the idea and pays, so the persona
  is `SAME_PERSON`: one role, one link, all three parts asked of the same people, no commercial link.
* **the floor, missed by one.** Four of the managers gave only their time, so Existing sacrifice has
  four anchored money answers -- one under keel-cloud's floor of five -- and reads *Too few to call*,
  which is also the COMMERCIAL verdict. A screen that called a status on four people would be the
  floor applied one person too late.
* **the one-unit window.** It counts the gate over *the last month*. keel-cloud asks no Frequency on
  a one-unit window (spec 078), and that is where `runs/DRIFT.md` #74 was found: no screen asks it,
  and the standings cannot be read until it carries an answer.
"""

from __future__ import annotations

from evals import corpus_scenario
from harness import vectors_script as vs

ENTRY_ID = "01-countly"
FLOOR = 5


def _countly_extras(j) -> None:
    standings = {d["dimension"]: d for v in j.standings.get("vectors") or []
                 for d in v.get("dimensions") or []}

    with j.recorder.step("S-005: one respondent type, every part on one link, no commercial link",
                         party="founder", kind="assert") as h:
        persona = j.get(j.project("/persona")) or {}
        types = persona.get("respondentTypes") or []
        kinds = {i.get("kind") for i in j.interviews.values()}
        parts = {p.get("part") for i in j.interviews.values() for p in i.get("parts") or []}
        h.record_assert({"types": 1, "kinds": ["FULL"], "parts": [1, 2, 3]},
                        {"types": types, "kinds": sorted(kinds), "parts": sorted(parts)})
        assert len(types) == 1 and not types[0].get("commercialLink"), types
        assert kinds == {"FULL"}, kinds
        assert parts == {1, 2, 3}, parts

    with j.recorder.step(f"S-005: Existing sacrifice sits one under the floor of {FLOOR} and is "
                         "too few to call, on the wire and on the commercial page",
                         party="founder", kind="assert") as h:
        row = standings["commercial.existing_sacrifice"]
        drawn = j.screens["COMMERCIAL"]["rows"]["commercial.existing_sacrifice"]["status"]
        h.record_assert({"floor": FLOOR, "n": FLOOR - 1, "status": "TOO_FEW_TO_CALL"},
                        {"floor": row.get("floor"), "n": row.get("n"), "status": row.get("status"),
                         "screen": drawn})
        assert row.get("floor") == FLOOR, row.get("floor")
        assert row.get("n") == FLOOR - 1, row.get("n")
        assert row.get("status") == "TOO_FEW_TO_CALL", row.get("status")
        assert drawn.startswith(corpus_scenario.STATUS_WORD["TOO_FEW_TO_CALL"]), drawn

    with j.recorder.step("S-005: the one-unit window asks no Frequency of anybody (spec 078)",
                         party="participant", kind="assert") as h:
        asked = sorted({i.get("dimension") for iv in j.interviews.values()
                        for p in iv.get("parts") or [] for i in p.get("items") or []})
        h.record_assert({"window": vs.window_words(j.founder.window), "frequency asked": False},
                        {"asked": asked})
        assert vs.one_unit_window(j.entry), j.founder.window
        assert "problem.frequency" not in asked, asked


def test_s005_countly(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s005-countly", extra=_countly_extras)
