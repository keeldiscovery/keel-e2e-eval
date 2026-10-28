"""S-007: `07-mulchrun`, the entry whose founder left the price out, in Texas, walked through the vector corridor
(spec 039; spec 041: corpus revision 10, keel-web 063 / 064; spec 042: revision 11, contract 14 -- Frequency still left
out, D-1; spec 053: revision 12, where every entry is a US entry in dollars, so Mulch Run is no longer the only US
market nor -- with Linerly's Oregon -- the only region).

`{country: US, region: TX, language: en-US}` -- a non-null region, the dollar and American English, and a founder
who left the price out. What was asserted about miles, feet and cubic yards went with revision 2's bucket scales (no
revision-9 question offers a physical unit, spec 039 D-6); what survives is the market and the money:

* the market persisted as United States, Texas, in American English;
* every amount keel-cloud renders for this project is in dollars -- the founder's cost estimate on
  the commercial screen, the standings' figure -- and every page drew text; **no pound or euro reaches
  any page the founder reads** is every corpus journey's check since spec 053
  (`corpus_scenario.leg_one_currency`, `OTHER_CURRENCIES`);
* the founder's *No price yet* leaves Price **and** the Ability to pay derived from it out, and the
  commercial vector is still called, on the worst of the dimensions left (D3: all thirteen decide) --
  Purchase friction's split, as the corpus says.
"""

from __future__ import annotations

from evals import corpus_scenario
from harness import vectors_script as vs

ENTRY_ID = "07-mulchrun"


def _mulchrun_extras(j) -> None:
    standings = {d["dimension"]: d for v in j.standings.get("vectors") or []
                 for d in v.get("dimensions") or []}

    # spec 077 FR-1 (keel-cloud 145 FR-4a, 146 FR-1 / FR-3): the founder's *in the Dallas-Fort Worth suburbs* is a place
    # that is not the market's country, so code draws the condition on the confirm although the scripted context job
    # writes none -- every crew lead's FULL link asks the chip before the gate, every owner's commercial link asks the
    # screener in the third person (the people's head, the place said once) before the idea; all answered inside
    with j.recorder.step("S-007: the drawn screener -- every FULL link serves *Are you based in the Dallas-Fort Worth "
                         "suburbs?* before the gate, every decision-maker's link the third person before the idea; all "
                         "inside, none counted apart (keel-cloud 146 FR-1, FR-3)", party="participant", kind="assert") as h:
        chip = vs.chip_of(j.entry)
        want_chip = {"question": chip["question"], "inCodes": [chip["inside"]]}
        want_decider = vs.decider_condition(j.entry)
        primary = [p for p in j.people if p.link == vs.LINK_PRIMARY]
        deciders = [p for p in j.people if p.link == vs.LINK_B2B]
        chips = {p.person: (j.interviews[p.person].get("gate") or {}).get("condition") for p in primary}
        screeners = {p.person: j.interviews[p.person].get("condition") for p in deciders}
        drawn = {p.person: [s_.get("screen") for s_ in j.walked[p.person]["screens"][:2]] for p in deciders}
        outside = j.standings.get("outsideSegment")
        h.record_assert({"chip": want_chip, "screener": want_decider, "screens": ["condition", "idea"],
                         "outsideSegment": 0},
                        {"chips": chips, "screeners": screeners, "drawn": drawn, "outsideSegment": outside})
        assert primary and deciders, (len(primary), len(deciders))
        assert want_decider == {"question": "Are the landscaping crew leads you decide for based in the Dallas-Fort "
                                            "Worth suburbs?", "inCodes": ["YES"]}, want_decider
        for person, served in chips.items():
            assert {k: (served or {}).get(k) for k in want_chip} == want_chip, (person, served)
        for person, served in screeners.items():
            assert served == want_decider, (person, served)
            assert drawn[person] == ["condition", "idea"], (person, drawn[person])
        assert int(outside or 0) == 0, outside

    with j.recorder.step("S-007: the market persisted as United States, Texas, in en-US",
                         party="stack", kind="assert") as h:
        market = (j.get(j.project("/overview")) or {}).get("market") or {}
        h.record_assert({"country": "US", "region": "TX", "language": "en-US"}, market)
        assert market.get("country") == "US", market
        assert market.get("region") == "TX", market
        assert market.get("language") == "en-US", market

    # No pound or euro on any page is every corpus journey's check since spec 053 (`corpus_scenario.leg_one_currency`,
    # `corpus_scenario.OTHER_CURRENCIES`), run before this extra; what stays here is Mulch Run's own dollar.
    with j.recorder.step("S-007: every amount is in dollars, and every page the founder reads drew text",
                         party="founder", kind="assert") as h:
        sacrifice = standings["commercial.existing_sacrifice"]
        interval = sacrifice.get("interval") or {}
        pages = {name: (drawn.get("text") if isinstance(drawn, dict) else None) or ""
                 for name, drawn in j.screens.items()}
        h.record_assert({"currency": "USD", "symbol": "$"},
                        {"interval": interval, "figure": sacrifice.get("figure")})
        assert interval.get("currency") == "USD", interval
        assert "$" in (sacrifice.get("figure") or "") or "$" in (sacrifice.get("founderSaid") or ""), sacrifice
        assert "$" in pages["COMMERCIAL"], "the commercial page shows no dollar amount at all"
        assert all(text.strip() for text in pages.values()), "a page drew no text, so it swept nothing"

    with j.recorder.step("S-007: no price yet leaves Price and Ability to pay out, and the "
                         "commercial vector is still called on the dimensions left",
                         party="founder", kind="assert") as h:
        left = {k: standings[k].get("status") for k in ("commercial.price", "commercial.ability_to_pay")}
        commercial = next(v for v in j.standings.get("vectors") or [] if v.get("vector") == "COMMERCIAL")
        h.record_assert({"left out": ["LEFT_OUT", "LEFT_OUT"],
                         "verdict": j.entry.expected["vector_verdicts"]["COMMERCIAL"]["verdict"]},
                        {"left out": left, "verdict": commercial.get("verdict")})
        assert set(left.values()) == {"LEFT_OUT"}, left
        assert commercial.get("verdict") == j.entry.expected["vector_verdicts"]["COMMERCIAL"]["verdict"]
        for key in left:
            assert j.screens["COMMERCIAL"]["rows"][key]["amber"], key


def test_s007_mulchrun(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s007-mulchrun", extra=_mulchrun_extras)
