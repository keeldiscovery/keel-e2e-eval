"""S-006: `05-paidly`, the widest B2B entry, walked through the vector corridor (spec 039).

Twenty people on **two links**: twelve freelance translators answer parts 1 and 2 on the primary
link, and eight agency project managers -- the decision-makers -- answer part 3 alone on their own
commercial link (no gate, no reveal). It is the only entry here whose commercial vector is counted
over people who never saw the problem's questions, so it is the one that proves the decision-maker's
link is counted at all (keel-cloud 075 found one that counted nowhere).

**The floor-of-five extra, re-read.** Until revision 2 this module asserted `S6`, a line with exactly
five anchored people, reading a real verdict. Revision 9 has no paidly dimension at exactly five --
the smallest anchored count is eight -- so that assertion has no subject left (spec 039 D-6). What
survives of it is the floor itself, which is now the wire's to say: every dimension carries
`floor: 5`, and every paidly dimension sits above it and calls a real status.
"""

from __future__ import annotations

from evals import corpus_scenario
from harness import vectors_script as vs

ENTRY_ID = "05-paidly"
FLOOR = 5


def _paidly_extras(j) -> None:
    standings = {d["dimension"]: d for v in j.standings.get("vectors") or []
                 for d in v.get("dimensions") or []}
    deciders = [p for p in j.people if p.link == vs.LINK_B2B]
    primary = [p for p in j.people if p.link == vs.LINK_PRIMARY]

    with j.recorder.step("S-006: two respondent types -- translators on the full link, agency "
                         "project managers on the commercial link, part 3 alone",
                         party="participant", kind="assert") as h:
        kinds = {p.person: j.interviews[p.person].get("kind") for p in j.people}
        parts = {p.person: sorted(q.get("part") for q in j.interviews[p.person].get("parts") or [])
                 for p in j.people}
        h.record_assert({"primary": [len(primary), "FULL", [1, 2]],
                         "decision-makers": [len(deciders), "COMMERCIAL_LINK", [3]]},
                        {"kinds": kinds, "parts": parts})
        assert (len(primary), len(deciders)) == (12, 8), (len(primary), len(deciders))
        for p in primary:
            assert kinds[p.person] == "FULL" and parts[p.person] == [1, 2], (p.person, parts[p.person])
            assert j.interviews[p.person].get("gate"), p.person
        for p in deciders:
            assert kinds[p.person] == "COMMERCIAL_LINK" and parts[p.person] == [3], p.person
            assert not j.interviews[p.person].get("gate"), p.person

    with j.recorder.step("S-006: the commercial vector is counted over the eight decision-makers",
                         party="stack", kind="assert") as h:
        commercial = {k: v.get("n") for k, v in standings.items()
                      if k.startswith("commercial.") and v.get("status") != "LEFT_OUT"}
        h.record_assert({k: len(deciders) for k in commercial}, commercial)
        assert all(n == len(deciders) for n in commercial.values()), commercial
        assert "agency project managers" in j.screens["COMMERCIAL"]["decider_banner"].lower(), (
            j.screens["COMMERCIAL"]["decider_banner"])

    with j.recorder.step(f"S-006: the floor is {FLOOR} on every dimension, and every paidly "
                         "dimension clears it with a real status", party="stack", kind="assert") as h:
        floors = {k: v.get("floor") for k, v in standings.items()}
        asked = {k: (v.get("n"), v.get("status")) for k, v in standings.items()
                 if v.get("status") != "LEFT_OUT"}
        h.record_assert({"floor": FLOOR}, {"floors": floors, "asked": asked})
        assert set(floors.values()) == {FLOOR}, floors
        for key, (n, status) in asked.items():
            assert n >= FLOOR and status not in ("TOO_FEW_TO_CALL", "NOT_ASKED_YET"), (key, n, status)

    with j.recorder.step("S-006: twenty people asked and twenty answered, on the board",
                         party="founder", kind="assert") as h:
        people = j.standings.get("people") or {}
        h.record_assert({"invited": 20, "answered": 20},
                        {"people": people, "tiles": j.screens["board"]["tiles"]})
        assert people.get("invited") == 20 and people.get("answered") == 20, people
        assert "20" in j.screens["board"]["tiles"], j.screens["board"]["tiles"]


def test_s006_paidly(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s006-paidly", extra=_paidly_extras)
