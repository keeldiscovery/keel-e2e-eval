"""S-005: `01-countly`, the B2C entry, walked through the vector corridor (spec 039; spec 041: corpus revision 10,
keel-web 063 / 064; spec 042: revision 11, contract 14 -- Keel's draft name for the idea kept on S2; spec 043: contract 15,
a consumer study's Contacts refused NOT_B2B).

Countly is the corpus's B2C entry with the most people (twelve), and it earns its place three ways:

* **one respondent type.** The owner-manager has the problem, uses the idea and pays, so the persona
  is `SAME_PERSON`: one role, one link, all three parts asked of the same people, no commercial link.
* **the floor, missed by one.** Four of the managers gave only their time, so Existing sacrifice has
  four anchored money answers -- one under keel-cloud's floor of five -- and reads *Too few to call*,
  which is also the COMMERCIAL verdict. A screen that called a status on four people would be the
  floor applied one person too late.
* **the window of four weeks.** Revision 10 re-windowed it from *the last month* to `{4, WEEKS}` (D13: no
  window counts fewer than two), so the Frequency `runs/DRIFT.md` #74 found unasked is now drawn on the
  founder's screen and asked of every person on *those 4 weeks* -- and stands where the corpus says.
"""

from __future__ import annotations

from evals import contacts_leg, corpus_scenario, interviewer_leg
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

    # D13 (keel-cloud 087; spec 040): no window counts fewer than two -- Countly's is {4, WEEKS} at revision 10 -- so
    # Frequency is on the founder's screens and asked of everyone, and it stands where the corpus says (spec 041).
    with j.recorder.step("S-005: the window counts four weeks, Frequency is asked of everyone and holds up (D13)",
                         party="participant", kind="assert") as h:
        asked = {name: sorted(i.get("dimension") for p in iv.get("parts") or [] for i in p.get("items") or [])
                 for name, iv in j.interviews.items() if iv.get("parts")}
        frequency = standings["problem.frequency"]
        h.record_assert({"window": vs.window_words(j.founder.window), "frequency asked": True,
                         "status": "HOLDING_UP", "n": 8},
                        {"asked": asked, "frequency": {k: frequency.get(k) for k in ("status", "n", "interval")},
                         "screen": j.framing["problem.frequency"][0]["question"]})
        assert j.founder.window.as_wire() == {"count": 4, "unit": "WEEKS"}, j.founder.window
        assert asked and all("problem.frequency" in dims for dims in asked.values()), asked
        assert frequency.get("status") == "HOLDING_UP" and frequency.get("n") == 8, frequency
        assert "4 weeks" in j.framing["problem.frequency"][0]["question"], j.framing["problem.frequency"]

    # Spec 076 FR-6 (keel-cloud 145 FR-6, keel-web 127 FR-4): Priya Natarajan's follow-up is not about the question --
    # the script groups it NOT_ABOUT_THIS, so the Insights box counts it apart and still shows it under her
    corpus_scenario.hold_not_about_this(j)
    # Spec 043 (keel-cloud 093 D10): Contacts are B2B only; a consumer study is refused NOT_B2B, before the door.
    contacts_leg.leg_contacts_not_b2b(j)
    # Spec 044: the AI interviewer's short form on a consumer study -- the recording's charge, READY, one AI link.
    interviewer_leg.leg_interviewer_short(j)


def test_s005_countly(stack, founder_one, browser, run_dir):
    # Spec 054 FR-3: once per matrix, the welcome's cue walk and its two replays (local profile only; Escape closes it).
    # Spec 073 FR-1: the confirmed context re-opened and Edit pressed -- keel-web 113's fourth context state.
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s005-countly", extra=_countly_extras, welcome_walk=True, teaching=True,
                        context_edit=True)
