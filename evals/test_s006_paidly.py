"""S-006: `05-paidly`, the widest B2B entry, walked through the vector corridor (spec 039; spec 041: corpus
revision 10, keel-web 063 / 064; spec 042: corpus revision 11, contract 14; spec 043: contract 15, the contacts leg).

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

**The founder names the idea** (spec 042, keel-cloud 090 D14). Paidly's founder types *Invoice payout service* over
S2's what line instead of saving Keel's *payment within seven days*: the wire's idea and short name become *invoice
payout service* (sentence case read mid-sentence), every translator's reveal and idea card and every decision-maker's
opening screen read *Imagine invoice payout service.*, and the Relative advantage question is *On your last invoice,
would invoice payout service have made things better, or not?*. The other two journeys keep Keel's draft name.

**Frequency is asked** since revision 11 (keel-cloud 091 FR-G): the founder's *2 to 3 months out of 3* fits the
`{3, MONTHS}` window, so spec 041's D-1 left-out Frequency is gone here -- asked of every translator, holding up (n 9,
median 2).
"""

from __future__ import annotations

from functools import partial

from evals import contacts_leg, corpus_scenario, interviewer_leg, sample_export
from harness import vectors_script as vs

ENTRY_ID = "05-paidly"
FLOOR = 5


def _paidly_extras(j, sample: sample_export.Pending | None = None) -> None:
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

    with j.recorder.step("S-006: each decision-maker's link opens with the idea's three lines (D9) and asks "
                         "Ability to pay and Purchase friction; each translator's kicker counts two parts",
                         party="participant", kind="assert") as h:
        firsts = {p.person: (j.walked[p.person]["screens"] or [{}])[0] for p in deciders}
        kickers = {p.person: [s.get("kicker") for s in j.walked[p.person]["screens"] if s.get("screen") == "item"]
                   for p in primary if j.walked[p.person]["screens"][1:]}
        b2b_asked = {p.person: [i.get("dimension") for q in j.interviews[p.person].get("parts") or []
                                for i in q.get("items") or []] for p in deciders}
        h.record_assert({"first screen": "idea", "asked": ["commercial.ability_to_pay",
                                                           "commercial.purchase_friction"], "parts": "of 2"},
                        {"firsts": firsts, "asked": b2b_asked, "kickers": kickers})
        for p in deciders:
            assert firsts[p.person].get("screen") == "idea", firsts[p.person]
            assert firsts[p.person].get("kicker") == j.interviews[p.person]["idea"]["kicker"], firsts[p.person]
            assert {"commercial.ability_to_pay", "commercial.purchase_friction"} <= set(b2b_asked[p.person])
        assert kickers and all(k and all("of 2" in (w or "") for w in k) for k in kickers.values()), kickers

    with j.recorder.step("S-006: the commercial vector is counted over the eight decision-makers",
                         party="stack", kind="assert") as h:
        commercial = {k: v.get("n") for k, v in standings.items()
                      if k.startswith("commercial.") and v.get("status") != "LEFT_OUT"}
        h.record_assert({k: len(deciders) for k in commercial}, commercial)
        assert all(n == len(deciders) for n in commercial.values()), commercial
        # spec 064 FR-6: the title (05-paidly carries none, so the role word is sent as it) or the role
        assert any(str(j.founder.decider.get(k) or "").lower() in j.screens["COMMERCIAL"]["decider_banner"].lower()
                   for k in ("title", "role") if j.founder.decider.get(k)), j.screens["COMMERCIAL"]["decider_banner"]

    with j.recorder.step(f"S-006: the floor is {FLOOR} on every dimension, and every paidly "
                         "dimension clears it with a real status", party="stack", kind="assert") as h:
        floors = {k: v.get("floor") for k, v in standings.items()}
        asked = {k: (v.get("n"), v.get("status")) for k, v in standings.items()
                 if v.get("status") != "LEFT_OUT"}
        h.record_assert({"floor": FLOOR}, {"floors": floors, "asked": asked})
        assert set(floors.values()) == {FLOOR}, floors
        for key, (n, status) in asked.items():
            assert n >= FLOOR and status not in ("TOO_FEW_TO_CALL", "NOT_ASKED_YET"), (key, n, status)

    with j.recorder.step("S-006: twenty people asked and twenty answered, on the report (keel-web 077: the eyebrow and "
                         "the foot carry the count; the people tile went with the deck)",
                         party="founder", kind="assert") as h:
        people = j.standings.get("people") or {}
        board = j.screens["board"]
        h.record_assert({"invited": 20, "answered": 20, "eyebrow": "Overview · locked · 20 answered"},
                        {"people": people, "eyebrow": board["eyebrow"], "foot": board["foot"]})
        assert people.get("invited") == 20 and people.get("answered") == 20, people
        assert board["eyebrow"] == "Overview · locked · 20 answered", board["eyebrow"]
        assert "20 answered" in board["foot"], board["foot"]


    named = vs.idea_name_of(vs.IDEA_NAMES[ENTRY_ID])
    with j.recorder.step(f"S-006: the founder's name for the idea, {vs.IDEA_NAMES[ENTRY_ID]!r}, is on the wire and on "
                         "every stranger's screen that names the idea (keel-cloud 090, D14)",
                         party="participant", kind="assert") as h:
        idea = j.get(j.project("/idea")) or {}
        card = vs.idea_card(named)
        question = vs.benefit_question(vs.occasion(j.entry), named)
        reveals = {p.person: (j.interviews[p.person].get("reveal") or {}).get("what") for p in primary
                   if j.interviews[p.person].get("reveal")}
        openings = {p.person: (j.interviews[p.person].get("idea") or {}).get("what") for p in deciders}
        asked = {p.person: next((i.get("question") for q in j.interviews[p.person].get("parts") or []
                                 for i in q.get("items") or [] if i.get("dimension") == "solution.relative_advantage"),
                                None) for p in primary if j.interviews[p.person].get("parts")}
        cards = {p.person: [s.get("idea_card") for s in j.walked[p.person]["screens"]
                            if s.get("screen") == "item" and s.get("dimension") == "solution.relative_advantage"]
                 for p in primary}
        h.record_assert({"what": named, "shortName": named, "card": card, "question": question},
                        {"idea": idea, "reveals": reveals, "openings": openings, "asked": asked, "cards": cards})
        assert named == "invoice payout service" and card == "Imagine invoice payout service.", (named, card)
        assert idea.get("what") == named and idea.get("shortName") == named, idea
        assert named != j.entry.solution_mechanism["short_name"], named
        assert reveals and set(reveals.values()) == {card}, reveals
        assert openings and set(openings.values()) == {card}, openings
        asked = {k: v for k, v in asked.items() if v is not None}
        assert asked and set(asked.values()) == {question}, asked
        drawn = [c for cs in cards.values() for c in cs]
        assert drawn and set(drawn) == {card}, cards

    with j.recorder.step("S-006: Frequency is asked on the three months and holds up -- revision 11's months out of "
                         "3 fit the window (spec 041's D-1 gone here)", party="participant", kind="assert") as h:
        frequency = standings["problem.frequency"]
        h.record_assert({"status": "HOLDING_UP", "n": 9, "founder": "2 to 3 months out of 3"},
                        {"frequency": {k: frequency.get(k) for k in ("status", "n", "interval")},
                         "screen": j.framing["problem.frequency"][0].get("question")})
        assert vs.frequency_fits(j.entry)
        assert frequency.get("status") == "HOLDING_UP" and frequency.get("n") == 9, frequency
        assert "3 months" in (j.framing["problem.frequency"][0].get("question") or ""), j.framing["problem.frequency"]

    # Spec 060 (design §18.11): with KEEL_SAMPLE_EXPORT set, the finished project at its twenty answers -- before the two
    # legs below add three more -- is exported as the landing's sample (`make sample`). Unset, nothing happens here.
    if sample is not None:
        sample.take(j)
    # Spec 043 (keel-cloud 093, contract 15): the decision-makers found through Contacts, on the wire, last -- its one
    # answer moves no standing this module holds above.
    contacts_leg.leg_contacts(j)
    # Spec 044 (keel-cloud 094, contract 16; keel-web 069): the AI interviewer, recorded on Keel's door after the
    # contacts leg -- its two answered links come last too, and move no standing held above.
    interviewer_leg.leg_interviewer(j)


def test_s006_paidly(stack, founder_one, browser, run_dir):
    sample = sample_export.pending(run_dir)
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s006-paidly", extra=partial(_paidly_extras, sample=sample))
    if sample is not None:
        # spec 060 FR-3: a refused export fails the run once S-006's own marks are all scored
        sample.settle()
