"""Spec 076: the harness follows keel-cloud 145 (contract 43) and keel-web 127 -- the founder's second walk of
2026-10-27. Stackless: the words and rules restated here are held to the products' own sources (keel-cloud-docs master,
keel-web master, through `stack.toml`'s sibling paths), and the walks' new reads to small pages."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from harness import interviewer_fake as fake
from instructions import brief_facts as bf
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import spoken
from stack.config import load_config
from tests import v9_fixtures as fx

CONFIG = load_config(validate=False)


def _cloud(path: str) -> str:
    return (CONFIG.keel_cloud / path).read_text()


def _web(path: str) -> str:
    return (CONFIG.keel_web / path).read_text()


@pytest.fixture(scope="module")
def corpus():
    fx.canon_entry("01-countly.yaml")
    return corpus_mod.load(CONFIG.keel_cloud).bind(fx.registry())


def _entry(corpus, entry_id: str):
    return next(e for e in corpus.entries if e.id == entry_id)


# ----------------------------------------------------------------- FR-2 Buyer and payer is direction-aware


def test_a_named_roles_supports_are_both_answers_as_the_registry_says():
    """keel-cloud 145 FR-2: with a role named, *had to agree* and *decided alone* both support the founder; the two
    *someone else* answers count against (the registry's `supports`, held in `test_follow_up_ladder.py` too)."""
    assert fake.BUYER_SUPPORTS == ("had_to_agree", "decided_alone")
    named = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=fake.BUYER_SUPPORTS)
    owed = lambda code: fake.owed([{"dimension": "commercial.buyer_payer_alignment", "codes": [code]}],  # noqa: E731
                                  named, "COMMERCIAL_B2B", b2b=True)
    assert [d for d, _ in owed("decided_alone")] == [] and [d for d, _ in owed("had_to_agree")] == []
    assert [d for d, _ in owed("someone_else_agreed")] == ["commercial.buyer_payer_alignment"]
    assert [d for d, _ in owed("someone_else_decided")] == ["commercial.buyer_payer_alignment"]


def test_the_role_takes_its_the_as_belief_sentence_reads_it():
    """keel-cloud 145 FR-2 (`BeliefSentence.theRole`): an acronym takes *the*, a role's own article is lower-cased, a
    person's name is kept bare."""
    assert chain_mod.the_role("CEO") == "the CEO"
    assert chain_mod.the_role("CFO") == "the CFO"
    assert chain_mod.the_role("HR director") == "the HR director"
    assert chain_mod.the_role("The HR director") == "the HR director"
    assert chain_mod.the_role("restaurant owner") == "the restaurant owner"
    assert chain_mod.the_role("Priya") == "Priya"
    assert chain_mod.the_role("their manager") == "their manager"
    source = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/BeliefSentence.java")
    assert 'ACRONYM = java.util.regex.Pattern.compile("^[A-Z]{2,4}s?$")' in source
    assert chain_mod.ACRONYM.pattern == "^[A-Z]{2,4}s?$"


def test_the_buyer_labels_give_an_acronym_role_its_the():
    """keel-cloud 145 FR-2 (`ItemFrames.buyerPayerLabel`, `buyerPayerAtPriceLabel`): *Yes, the CEO had to agree*,
    *No, the CEO would have to agree*."""
    labels = spoken.buyer_answers("CEO")
    assert labels[0] == "Yes, the CEO had to agree" and labels[2] == "No, the CEO would have to agree"
    assert spoken.buyer_answers(None)[0] == "Yes, someone else had to agree"


def test_the_brief_line_and_the_said_line_on_a_named_role(corpus):
    """keel-cloud 145 FR-2: the brief's fact line *k of n · {role} had to agree, or they decided alone*, and the said
    line the belief after *You said* -- *You said the HR director has to agree.*; with *Nobody else* tested both as
    before (*decided on their own*; *You said nobody else has to agree.*)."""
    registry = fx.registry()
    compliance = _entry(corpus, "02-compliancelog")
    card = next(c for c in bf.cards_for(compliance, registry) if c["key"] == "commercial.buyer_payer_alignment")
    assert card["line"] == "the HR director had to agree, or they decided alone"
    assert cs.buyer_said(compliance) == "You said the HR director has to agree."
    countly = _entry(corpus, "01-countly")
    card = next(c for c in bf.cards_for(countly, registry) if c["key"] == "commercial.buyer_payer_alignment")
    assert card["line"] == "decided on their own"
    assert cs.buyer_said(countly) == "You said nobody else has to agree."
    brief = _cloud("src/main/java/com/keeldiscovery/cloud/application/BriefFacts.java")
    assert '" had to agree, or they decided alone"' in brief
    said = _cloud("src/main/java/com/keeldiscovery/cloud/application/StandingsAssembler.java")
    assert 'return "You said " + phrase + " has to agree.";' in said


def test_every_six_journey_entry_tests_nobody_else_so_no_golden_reading_moves(corpus):
    """Spec 076 FR-2: the six journeys walk 01-countly and 05-paidly (and 07-mulchrun), each testing *Nobody else* --
    the direction-aware rule moves none of their rows; 02-compliancelog's (the HR director) is the one row keel-cloud
    145 proposed for revision 17 -- recorded since keel-cloud 147 (spec 080): REVISION is 17, the proposed map gone,
    the row's two readings `SPEC_147_ROW_FROM` / `_TO`."""
    for entry_id in ("01-countly", "05-paidly", "07-mulchrun"):
        assert (_entry(corpus, entry_id).tested("commercial.buyer_payer_alignment") or {}).get("code") == "nobody_else"
    assert corpus_mod.REVISION == 18      # spec 086: r18 (152) moved no standing; the row stays as 147 recorded it
    row = _entry(corpus, "02-compliancelog").expected["standings"]["commercial.buyer_payer_alignment"]
    assert (row["status"], row["drift"], row["inside"], row["n"]) == ("HOLDING_UP", "none", 7, 9)
    golden = _cloud("src/test/java/com/keeldiscovery/cloud/corpus/GoldenCorpusTest.java")
    assert "PROPOSED_REVISION_17" not in golden and "PROPOSED_FROM" not in golden
    assert "status: PEOPLE_DISAGREE, drift: both, n: 9, " in golden and "inside: 5, outside: 4," in golden
    assert "status: HOLDING_UP, drift: none, n: 9, inside: 7, outside: 2," in golden


# ----------------------------------------------------------------- FR-1 Ability to pay's bars


def _budget_row(b2b: bool = True, **over) -> dict:
    options = [{"code": "existing_line", "label": "An existing budget line", "count": 4, "founderNamed": True},
               {"code": "new_line_signed_off", "label": "A new budget line", "count": 2, "founderNamed": False},
               {"code": "taken_from_other_spend", "label": "Taken from other spending", "count": 1,
                "founderNamed": True},
               {"code": "no_budget", "label": "No budget", "count": 1, "founderNamed": False}]
    row = {"dimension": cs.ABILITY, "founderSaid": cs.vs_screens.COUNTS_SENTENCE[b2b],
           "choice": {"founderCodes": ["existing_line", "taken_from_other_spend"], "optionCounts": options}}
    row.update(over)
    return row


def _drawn(row: dict) -> list:
    return [{"label": o["label"], "muted": not o["founderNamed"]} for o in row["choice"]["optionCounts"]]


def test_the_budget_bars_draw_the_supports_on_and_the_said_line_is_the_counts_sentence():
    """keel-cloud 145 FR-1, keel-web 127 FR-5: on Ability to pay read off the budget question the served supports are
    the budget codes among the options, drawn on, the rest muted; no *which you didn't name*; the said line the counts
    sentence alone."""
    row = _budget_row()
    assert cs.budget_bars_faults(row, _drawn(row), "Ability to pay ...", True) == []
    muted = _budget_row(choice={"founderCodes": [], "optionCounts": [dict(o, founderNamed=False)
                                                                     for o in row["choice"]["optionCounts"]]})
    # the old all-muted bars (before 145): served unnamed and drawn muted -- all three faults
    assert {next(iter(f)) for f in cs.budget_bars_faults(muted, _drawn(muted), "", True)} == {"founderCodes",
                                                                                             "founderNamed",
                                                                                             "bars drawn"}
    assert cs.budget_bars_faults(row, [dict(b, muted=True) for b in _drawn(row)], "", True)
    assert cs.budget_bars_faults(row, _drawn(row), "2 more, which you didn't name", True)
    # a row read another way is not this check's
    assert cs.budget_bars_faults(_budget_row(founderSaid="Keel reads your price against what the problem costs "
                                                         "them today."), [], "", True) == []
    chain = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/CommercialChain.java")
    assert 'BUDGET_SUPPORTS = List.of(FROM_SPEND, "existing_line", "taken_from_other_spend")' in chain
    assert 'FROM_SPEND = "from_spend"' in chain
    assert cs.vs_screens.BUDGET_SUPPORTS == ("from_spend", "existing_line", "taken_from_other_spend")
    said = _cloud("src/main/java/com/keeldiscovery/cloud/application/StandingsAssembler.java")
    assert "return com.keeldiscovery.cloud.domain.vectors.CommercialChain.countsSentence(b2b);" in said
    page = _web("src/components/answers/DimensionStagePage.tsx")
    assert 'className={`dimbar${option.founderNamed ? "" : " dimbar--muted"}`}' in page


# ----------------------------------------------------------------- FR-3 Send more is the name alone


def test_someone_i_know_is_the_name_alone():
    """keel-web 127 FR-1: no second box, and the batch sends `people: [{personName}]`."""
    made = {"about_boxes": 0, "sent": {"people": [{"personName": "Kate Alder"}], "format": "TEXT"}}
    assert cs.name_alone_faults(made, "Kate Alder") == []
    assert cs.name_alone_faults({**made, "about_boxes": 1}, "Kate Alder")
    assert cs.name_alone_faults({**made, "sent": {"people": [{"personName": "Kate Alder", "about": "x"}]}},
                                "Kate Alder")
    popup = _web("src/components/interviews/SendMorePopup.tsx")
    assert "[{ personName: name.trim() }]" in popup and "send-about" not in popup
    from harness import interviews_screens as iv                       # noqa: PLC0415
    assert iv.SEND_ABOUT_LABEL not in popup
    import inspect                                                      # noqa: PLC0415
    assert "about" not in inspect.signature(iv.Interviews.send_someone).parameters


# ----------------------------------------------------------------- FR-4 The screener on the decision-maker's link


def test_the_decision_makers_screener_is_codes_third_person_question():
    """keel-cloud 145 FR-4b (`RespondentQuestionsRules.deciderChip`), mirrored: the cloud's own examples, and 05-paidly's
    -- the one journey entry whose WHICH PEOPLE carries a qualifier on a SOMEONE_ELSE study."""
    from harness import vectors_script as vs                           # noqa: PLC0415
    assert vs.decider_chip("run payroll for at least 50 employees", "payroll practitioners") == \
        "Do the payroll practitioners you decide for run payroll for at least 50 employees?"
    assert vs.decider_chip("work at a company with at least 50 employees", "x") == \
        "Does your company have at least 50 employees?"
    assert vs.decider_chip("are past the beginner stage", "language learners") == \
        "Are the language learners you decide for past the beginner stage?"
    assert vs.decider_chip("work at a hotel group that runs a call center", "agents") == \
        "Do you work at a hotel group that runs a call center?"
    assert vs.decider_chip(None, "x") is None
    source = _cloud("src/main/java/com/keeldiscovery/cloud/application/RespondentQuestionsRules.java")
    assert '"Do the " + people + " you decide for " + text + "?"' in source
    assert '"Does your " + org.group(1).strip() + " have " + org.group(2).strip() + "?"' in source


def test_which_journey_entries_serve_the_screener(corpus):
    """Spec 076 FR-4: of the journey entries 05-paidly is SOMEONE_ELSE with a condition (S-006, and S-014's healthy
    copy); 01-04 are SAME_PERSON. Spec 077 (keel-cloud 146): 05-paidly's screener names *the people* once (DRIFT #99
    closed), and 07-mulchrun now serves one too -- its place condition drawn by code on the confirm (146 FR-1); the
    entries are held in `tests/test_drawn_screener_seams_077.py`."""
    from harness import vectors_script as vs                           # noqa: PLC0415
    served = {e.id: vs.decider_condition(e) for e in corpus.entries}
    assert [k for k, v in served.items() if v] == ["05-paidly", "07-mulchrun"]
    assert served["05-paidly"] == {"question": "Do the people you decide for work mostly for agencies?",
                                   "inCodes": ["YES"]}


def _person(**over):
    from harness import vectors_script as vs                           # noqa: PLC0415
    base = dict(person="P", link=vs.LINK_B2B, recency=None, story=None, anchor_chip=None, picks=[],
                pilot_opt_in=False, anchoring=None)
    base.update(over)
    return vs.PersonInputs(**base)


def test_an_outside_decision_maker_sends_outside_segment_alone():
    """keel-web 127 FR-2: `{outsideSegment: true, answers: []}` on the decision-maker's link too; inside as before."""
    assert _person(in_segment=False).response("t") == {"outsideSegment": True, "answers": []}
    assert _person().response("t") == {"answers": []}
    web = _web("src/lib/interviewAnswers.ts")
    assert "if (isOutsideSegment(interview, gate)) return { outsideSegment: true, answers: [] };" in web


def test_the_screener_screen_is_first_and_the_idea_after_it():
    condition = {"question": "Do the people you decide for work mostly for agencies?", "inCodes": ["YES"]}
    drawn = {"screen": "condition", "question": condition["question"], "kicker": None, "options": ["Yes", "No"],
             "continue_before": False, "continue_after": True, "back": 0}
    interview = {"kind": "COMMERCIAL_LINK", "condition": condition, "idea": {"kicker": "k"}}
    assert cs.condition_screen_faults(interview, [drawn, {"screen": "idea"}]) == []
    assert cs.condition_screen_faults(interview, [drawn], inside=False) == []
    assert cs.condition_screen_faults(interview, [{"screen": "idea"}])
    assert cs.condition_screen_faults(interview, [dict(drawn, kicker="Part 1"), {"screen": "idea"}])
    assert cs.condition_screen_faults(interview, [dict(drawn, continue_before=True), {"screen": "idea"}])
    assert cs.condition_screen_faults(interview, [drawn, {"screen": "item"}])
    assert cs.condition_screen_faults({"kind": "COMMERCIAL_LINK", "idea": {}}, [{"screen": "idea"}]) == []
    gate = _web("src/components/interview/GateScreen.tsx")
    assert 'data-testid="condition-screen"' in gate and 'heading="h1"' in gate
    contract = _cloud("canon/openapi-v2.yaml")
    assert int(re.search(r"x-keel-contract: (\d+)", contract).group(1)) >= 43
    assert "Spec 145 (FR-4, contract 43): COMMERCIAL_LINK only -- the screener, asked before `idea`" in contract


# ----------------------------------------------------------------- FR-5 A story chip ends the interview


def test_a_story_chip_sends_the_chip_only_submission():
    """keel-cloud 145 FR-5, keel-web 127 FR-3: the gate's Yes and the chip, no story, no answers."""
    from harness import vectors_script as vs                           # noqa: PLC0415
    pick = vs.Pick(dimension="problem.importance", codes=["a"])
    chip = _person(link=vs.LINK_PRIMARY, recency=True, anchor_chip="RATHER_NOT_SAY", story="x", picks=[pick])
    assert chip.response("t") == {"recency": True, "anchorChip": "RATHER_NOT_SAY", "answers": []}
    assert chip.ends_on_chip
    told = _person(link=vs.LINK_PRIMARY, recency=True, story="It was a Tuesday.", picks=[pick])
    assert not told.ends_on_chip and told.response("t")["story"] == "It was a Tuesday."
    web = _web("src/lib/interviewAnswers.ts")
    assert "if (endsOnChip(gate)) return { recency: true, anchorChip: gate.anchorChip, answers: [], pilotOptIn: false };" \
        in web
    flow = _web("src/lib/aiInterviewFlow.ts")
    assert "void this.endOnChip();" in flow


def test_the_chip_people_rows_read_the_cloud_words():
    """keel-cloud 145 FR-5 (`VectorEvidence.endedOn`): part 1's rows read the chip's words; no later line lists them."""
    from harness import vectors_script as vs                           # noqa: PLC0415
    assert cs.ended_on("CANT_RECALL", "delivery") == "Couldn't recall one particular delivery"
    assert cs.ended_on("RATHER_NOT_SAY", "delivery") == "Would rather not say"
    evidence = _cloud("src/main/java/com/keeldiscovery/cloud/application/VectorEvidence.java")
    assert 'case CANT_RECALL -> "Couldn\'t recall one particular "' in evidence
    assert 'case RATHER_NOT_SAY -> "Would rather not say";' in evidence
    person = _person(person="Xavier", link=vs.LINK_PRIMARY, recency=True, anchor_chip="RATHER_NOT_SAY")
    row = lambda key, people: {"dimension": key, "status": "HOLDING_UP", "people": people}  # noqa: E731
    xavier = {"personName": "Xavier", "readAs": "Would rather not say"}
    good = {"vectors": [{"vector": "PROBLEM", "dimensions": [row("problem.prevalence", []),
                                                               row("problem.importance", [xavier])]},
                        {"vector": "SOLUTION", "dimensions": [row("solution.compatibility", [])]}]}
    assert cs.chip_people_faults(good, [person], {"Xavier": {"occasion": "invoice"}})[0] == []
    listed = {"vectors": good["vectors"][:1] + [{"vector": "SOLUTION", "dimensions": [
        row("solution.compatibility", [{"personName": "Xavier", "readAs": "not counted · a guess"}])]}]}
    assert cs.chip_people_faults(listed, [person], {})[0]
    unread = {"vectors": [{"vector": "PROBLEM", "dimensions": [row("problem.importance", [])]}]}
    assert cs.chip_people_faults(unread, [person], {})[0]


def test_the_interviewer_marks_moved_to_12():
    from evals import interviewer_marks as marks                       # noqa: PLC0415
    from evals import report_marks as rm                               # noqa: PLC0415
    from instructions import marks as instruction_marks                 # noqa: PLC0415
    assert marks.INTERVIEWER_MARKS_VERSION == 13 and rm.REPORT_MARKS_VERSION == 3      # 086 FR-5: IM27
    assert instruction_marks.MARKS_VERSION == 21 and corpus_mod.REVISION == 18      # spec 080: r17, v21 stands; spec 086: r18
    ok, _ = marks.chip_ended_it({"chip": "I can't recall one particular delivery",
                                 "want_chip": "I can't recall one particular delivery",
                                 "responses": [{"status": 201, "body": {**marks.CHIP_ONLY, "pilotOptIn": False}}],
                                 "pilot_writes": 0, "follow_up_calls": [], "done": {"text": "Thank you"},
                                 "mic_off": {"shown": True}, "row_faults": []})
    assert ok


# ----------------------------------------------------------------- FR-6 Junk out of Insights


def test_the_script_groups_the_junk_not_about_this(corpus):
    """Spec 076 FR-6: S-005's Priya Natarajan types *Meow, you are a fool.* on her one rung, and the THEMES script puts it
    in NOT_ABOUT_THIS, last; every other answer grouped as `FakeThemes` groups it."""
    from harness import vectors_script as vs                           # noqa: PLC0415
    countly = _entry(corpus, "01-countly")
    people = vs.person_inputs(countly)
    assert vs.junk_follow_ups(countly, people) == [("problem.current_solution_satisfaction", "Meow, you are a fool.")]
    priya = next(p for p in people if p.person == "Priya Natarajan")
    assert vs.follow_up_line(countly, priya, {"dimension": "problem.current_solution_satisfaction"}) == \
        "Meow, you are a fool."
    entries = vs.themes_entries(countly, vs.walked_follow_ups(countly, people))
    current = next(e for e in entries if e.get("dimension") == "problem.current_solution_satisfaction")
    assert current["result"]["themes"][-1] == {"label": fake.NOT_ABOUT_THIS, "answers": ["Meow, you are a fool."]}
    # nowhere else, and not on the scope journeys' copies
    assert all(fake.NOT_ABOUT_THIS not in [t["label"] for t in (e.get("result") or {}).get("themes") or []]
               for e in entries if e.get("dimension") != "problem.current_solution_satisfaction")
    import dataclasses                                                  # noqa: PLC0415
    assert vs.junk_follow_ups(dataclasses.replace(countly, scope="PROBLEM"), people) == []
    assert vs.junk_follow_ups(_entry(corpus, "05-paidly"), vs.person_inputs(_entry(corpus, "05-paidly"))) == []
    themes = _cloud("src/main/resources/keel/inference-instructions/themes.md")
    assert "`NOT_ABOUT_THIS`" in themes


def test_the_insights_box_counts_the_junk_apart():
    """keel-cloud 145 FR-6, keel-web 127 FR-4: `notAboutThis` the junk under the people, off the quotes, the line."""
    from evals import report_marks as rm                               # noqa: PLC0415
    assert fake.not_about_this_line(1) == "1 answer was not about this."
    assert fake.not_about_this_line(3) == "3 answers were not about this."
    translate = _web("src/lib/translate.ts")
    assert 'export const notAboutThisLine = (n: number): string => (n === 1 ? "1 answer was not about this." : ' \
           '`${n} answers were not about this.`);' in translate
    key = "problem.current_solution_satisfaction"
    people = [{"invitationId": "a", "personName": "Priya", "followUp": "Meow, you are a fool."},
              {"invitationId": "b", "personName": "Aisha", "followUp": "A quick check."}]
    standings = {"vectors": [{"vector": "PROBLEM", "dimensions": [{"dimension": key, "people": people}]}]}
    insight = {"dimension": key, "state": "GROUPED", "notAboutThis": 1,
               "quotes": [{"invitationId": "b", "text": "A quick check."}], "themes": []}
    box = {"key": key, "not_about": "1 answer was not about this."}
    assert rm.not_about_this_faults(standings, key, insight, box, strict=True) == []
    assert rm.not_about_this_faults(standings, key, {**insight, "notAboutThis": 0}, box, strict=True)
    assert rm.not_about_this_faults(standings, key, insight, {**box, "not_about": None}, strict=True)
    quoted = {**insight, "quotes": insight["quotes"] + [{"invitationId": "a", "text": "Meow, you are a fool."}]}
    assert rm.not_about_this_faults(standings, key, quoted, box, strict=True)
    assert rm.not_about_this_faults(standings, key, {**insight, "themes": [{"label": fake.NOT_ABOUT_THIS}]}, box,
                                    strict=True)
    # a box recorded before contract 43 reads as 0 and draws no line
    assert rm.not_about_this_faults({"vectors": []}, key, {"state": "GROUPED"}, {"key": key}, strict=False) == []


def test_a_lone_answer_not_about_this_is_its_own_group_until_a_second_arrives():
    """keel-cloud 119 / `ThemesOnReturn`: one follow-up answer on a line starts no THEMES job -- ON_THEIR_OWN, quoted,
    `notAboutThis` 0 (S-005 after four answers; runs/DRIFT.md #98)."""
    from evals import report_marks as rm                               # noqa: PLC0415
    key = "problem.current_solution_satisfaction"
    people = [{"invitationId": "a", "personName": "Priya", "followUp": "Meow, you are a fool."}]
    standings = {"vectors": [{"vector": "PROBLEM", "dimensions": [{"dimension": key, "people": people}]}]}
    insight = {"dimension": key, "state": "GROUPED", "notAboutThis": 0,
               "quotes": [{"invitationId": "a", "text": "Meow, you are a fool."}],
               "themes": [{"label": fake.ON_THEIR_OWN, "quotes": [{"invitationId": "a", "text": "Meow, you are a fool."}]}]}
    assert rm.not_about_this_faults(standings, key, insight, {"key": key, "not_about": None}, strict=True) == []


def test_the_dry_runs_hello_on_the_gates_id_is_not_the_story():
    """Spec 076 (075 FR-5 first walked on S-006): keel-web's mic test transcribes on the first item, the gate's id, so
    the hello there is not a second story take."""
    from evals import interviewer_leg as leg                           # noqa: PLC0415
    gate = "g-1"
    drawn = {"transcribed": [{"itemId": gate, "maxSeconds": None, "status": 200, "text": "hello"},
                             {"itemId": gate, "maxSeconds": None, "status": 200, "text": leg.DRY_RUN_STORY}],
             "answered": [], "story": {"reached": True, "hold": {"status": leg.ivs.HELD, "heard": leg.DRY_RUN_STORY},
                                       "sheet_text": "", "statuses": []}}
    assert leg.dry_run_written_down(drawn, gate, leg.DRY_RUN_STORY) == []
    flow = _web("src/lib/aiInterviewFlow.ts")
    assert 'return first?.kind === "gate" ? first.gate.itemId' in flow
