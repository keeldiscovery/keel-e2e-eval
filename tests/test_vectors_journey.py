"""Spec 039 / spec 041 / spec 042: the corpus journeys are vectors journeys -- the script, the typed inputs and the
legs, held without a stack, at corpus revision 11 and contract 14 (one RESPONDENT_QUESTIONS job a lock; the founder's
name for the idea).

Read through keel-cloud's own canon corpus, as the three scenarios read it, so a corpus edit that a
journey could no longer drive fails here before it fails twenty steps into a run. Every test that needs
the canon skips by name when `stack.toml`'s keel-cloud checkout carries none. Spec 040's judgement call 89
skipped them at revision 10 until the script wrote contract 13's shapes; spec 041 re-pointed it and they run.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from evals import corpus_scenario
from harness import vectors_script as vs

REPO = Path(__file__).resolve().parent.parent
ENTRIES = ("01-countly", "05-paidly", "07-mulchrun")

# keel-cloud `Vocabulary.PRODUCT_WORDS` and `CLAIM_WORDS`, restated for the checks below only.
PRODUCT_WORDS = {"app", "apps", "platform", "dashboard", "portal", "plugin", "api", "saas",
                 "website", "algorithm", "device"}
CLAIM_WORDS = {"works", "accurate", "accurately", "saves", "faster", "better", "reliable",
               "reliably", "trusted", "improves", "helps"}
# keel-cloud `WindowFrame.TIME_WORDS` (E1) and `FRAME_OPENINGS` (E3).
TIME_WORDS = {"last", "past", "recent", "recently", "ago", "today", "yesterday", "week", "weeks",
              "month", "months", "year", "years", "day", "days", "night", "nights", "shift",
              "shifts", "cycle", "cycles"}
FRAME_OPENINGS = ("in ", "how many", "did you", "out of", "do you think")
# Registry 4's `founder.saves` (keel-cloud 087 FR-001): (min, max, words) a list carries, Buyer and payer's
# fixed "Nobody else" not counted (code adds it).
#: The slice's first drafts (`calibration_result` with no `only`): keel-cloud 097 F9 drafts Importance as the own item alone.
SAVES = {"problem.importance": (1, 1, 9), "problem.current_solution_satisfaction": (5, 5, 9),
         "solution.compatibility": (2, 4, 9), "solution.relative_advantage": (1, 4, 9),
         "solution.adoption_friction": (1, 4, 9), "commercial.buyer_payer_alignment": (0, 2, 4),
         "commercial.purchase_friction": (1, 4, 9), "commercial.commitment": (1, 1, 9)}


def _entry(entry_id: str):
    from stack.config import load_config
    keel_cloud = Path(load_config(validate=False).keel_cloud)
    if not (keel_cloud / "canon" / "designs" / "measured-beliefs" / "corpus").is_dir():
        pytest.skip(f"no keel-cloud corpus at {keel_cloud}")
    return vs.entry_for(keel_cloud, entry_id)[1]


def _words(text: str) -> set:
    return set(re.findall(r"[a-z']+", text.lower()))


def _count(text: str) -> int:
    return len(text.split())


# ------------------------------------------------------------------------------- the id codec

def test_the_ids_are_keel_clouds_interview_id_codec():
    """`InterviewIdCodec`: the first twelve hex of sha256 over `token|item|dim` and
    `token|option|dim|code` -- which is what lets a pick be sent by code with no label matched."""
    assert vs.item_id("tok", "problem.importance") == hashlib.sha256(
        b"tok|item|problem.importance").hexdigest()[:12]
    assert vs.option_id("tok", "commercial.price", "band_20_50") == hashlib.sha256(
        b"tok|option|commercial.price|band_20_50").hexdigest()[:12]


def test_a_list_items_code_is_its_place_as_keel_cloud_codes_it():
    """keel-cloud `SavedList.codeFor` (087 judgement call 2): the wire never carries the corpus's slugs."""
    assert [vs.wire_code("problem.importance", i) for i in range(5)] == [
        "own", "rival_1", "rival_2", "rival_3", "rival_4"]
    assert vs.wire_code("problem.current_solution_satisfaction", 4) == "outcome_5"
    assert vs.wire_code("solution.relative_advantage", 0) == "benefit_1"
    assert vs.wire_code("solution.compatibility", 2) == "item_3"
    assert [vs.wire_code("commercial.buyer_payer_alignment", i) for i in range(3)] == [
        "nobody_else", "role_1", "role_2"]
    assert vs.wire_code("commercial.commitment", 0) == "step"


# ------------------------------------------------------------------------------- the script

@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_script_answers_every_corridor_screen_from_the_entry(entry_id):
    entry = _entry(entry_id)
    screens = vs.generate(entry).screens
    want = {vs.CONTEXT_SCREEN, vs.PROBLEM_SCREEN, vs.MECHANISM_SCREEN, vs.CALIBRATION_SCREEN,
            vs.ASKED_SCREEN, vs.RESPONDENT_SCREEN, vs.INTERPRET_SCREEN, vs.THEMES_SCREEN}
    assert set(screens) == want, "no BRIEF since keel-cloud 104; THEMES chosen by dimension (keel-runtime 012)"
    assert screens[vs.THEMES_SCREEN][-1] == {"outcome": "COMPLETED", "result": {"themes": []}}, "the catch-all last"
    assert [e["result"] for e in screens[vs.RESPONDENT_SCREEN]] == [vs.respondent_result(entry, 1, vs.LINK_PRIMARY)], (
        "keel-cloud 091: one RESPONDENT_QUESTIONS job a lock -- part 1 on the primary link, the gate's clause")
    calibration = [(e["result"]["vector"], [q["key"] for q in e["result"]["questions"]])
                   for e in screens[vs.CALIBRATION_SCREEN]]
    assert calibration == [(v, [only] if only else vs.calibrated_keys(entry, v))
                           for v, only in vs.calibration_jobs(entry)], (
        "one key set for every calibration job: the slice on each seed, then one redraft per list the founder "
        "answers, in the corridor's own order")
    assert [v for v, only in vs.calibration_jobs(entry) if only is None] == list(vs.VECTORS)
    assert len(screens[vs.INTERPRET_SCREEN]) == len(vs.readable_people(entry))
    assert [e["result"]["anchoring"] for e in screens[vs.INTERPRET_SCREEN]] == [
        p.anchoring for p in vs.readable_people(entry)]
    context = screens[vs.CONTEXT_SCREEN][0]["result"]
    assert context["understands"] == entry.context["understood"]
    assert context["occasion"] == entry.context["occasion"]
    assert screens[vs.PROBLEM_SCREEN][0]["result"]["statement"] == entry.interpretations["problem"]
    mechanism = screens[vs.MECHANISM_SCREEN][0]["result"]
    assert "idea_what" not in mechanism, "keel-cloud 097 F7: the idea's name is never the model's"
    assert mechanism["idea_how"] and mechanism["short_name"]
    assert mechanism["idea_belief"].startswith(vs.BELIEF_FRAME)
    assert 3 <= len(mechanism["mechanism_terms"]) <= 8
    asked = [e["result"] for e in screens[vs.ASKED_SCREEN]]
    assert asked == [vs.asked_result(entry, "solution.compatibility"),
                     vs.asked_result(entry, "solution.adoption_friction")]


def test_the_lock_starts_one_job_on_either_persona_and_part_three_stays_the_decision_makers():
    """keel-cloud 091 FR-D (contract 14): one RESPONDENT_QUESTIONS job a lock, part 1 on the primary link, B2C and B2B
    alike; part 3 of a B2B study is still planned for the decision-maker's link (code writes it), so the people on it
    still answer Ability to pay and Purchase friction."""
    for entry_id in ENTRIES:
        assert vs.respondent_jobs(_entry(entry_id)) == [(1, vs.LINK_PRIMARY)], entry_id
    paidly = _entry("05-paidly")
    assert {"commercial.ability_to_pay", "commercial.purchase_friction"} <= set(vs.plan_keys(paidly, 3, vs.LINK_B2B))


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_drafted_lists_keep_keel_clouds_rules(entry_id):
    """`founder-lists.md` as keel-cloud's applier holds it (087 L1-L5, C5, C6, W9) and Prevalence's clause
    (E1-E3), on the referee's results -- which keel-cloud would otherwise refuse with one repair turn the
    script cannot answer: each list the registry's count and words, Importance the own item alone (097 call 10),
    Current solution five and
    its phrase, every face at most 20 words and no question mark, no digit the sources lack, no product word on
    the problem's, no claim word on the solution's, no money anywhere."""
    entry = _entry(entry_id)
    sources = json.dumps([entry.context, entry.interpretations])
    for vector in vs.VECTORS:
        for q in vs.calibration_result(entry, vector)["questions"]:
            key = q["key"]
            texts = [q.get("event") or ""] + [o["label"] + " " + o["belief_phrase"] for o in q.get("options") or []]
            if vs.is_list(key):
                draft = q["list"]
                low, high, words = SAVES[key]
                assert low <= len(draft["items"]) <= high, (key, draft)
                for item in draft["items"]:
                    assert 1 <= _count(item["label"]) <= words, (key, item)
                    if key in vs.ASKED_FACES:
                        assert 1 <= _count(item["asked"]) <= 20 and "?" not in item["asked"], (key, item)
                    else:
                        assert "asked" not in item, (key, item)
                    assert "Nobody else" != item["label"], "code adds Buyer and payer's fixed first item"
                    texts += [item["label"], item.get("asked") or ""]
                if key == "problem.current_solution_satisfaction":
                    assert draft["phrase"].startswith("your "), draft
                    texts.append(draft["phrase"])
                else:
                    assert "phrase" not in draft
                answer = vs.answer_text(entry, key)
                for digit in re.findall(r"\d+", " ".join(texts)):
                    assert digit in sources + answer, (key, digit)
            else:
                assert "list" not in q
            text = " ".join(texts)
            if vector == "PROBLEM":
                assert not _words(text) & PRODUCT_WORDS, (key, text)
            if vector == "SOLUTION":
                claims = CLAIM_WORDS - ({"better"} if key == "solution.relative_advantage" else set())
                assert not _words(text) & claims, (key, text)
            if key == "problem.prevalence":
                assert len(q["options"]) == 5
                assert not re.search(r"\d", q["event"]) and not _words(q["event"]) & TIME_WORDS
                assert not q["event"].lower().startswith(FRAME_OPENINGS)
            assert not re.search(r"[£$€]", text), (key, text)


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_respondent_job_writes_the_gates_clause_and_nothing_else(entry_id):
    """keel-cloud 088 FR-002: `{key, event?}` per planned key, the event on the gate alone, held to E1-E4 --
    framed, the gate and the Frequency question are each at most 20 words -- and no product word or mechanism
    term in it (R4 on part 1)."""
    entry = _entry(entry_id)
    window = vs.window_of(entry)
    terms = {t.lower() for t in (entry.solution_mechanism or {}).get("mechanism_terms") or []}
    for part, link in vs.respondent_jobs(entry):
        result = vs.respondent_result(entry, part, link)
        assert [i["key"] for i in result["items"]] == vs.plan_keys(entry, part, link)
        for item in result["items"]:
            if item["key"] != "problem.prevalence":
                assert item == {"key": item["key"]}, item
                continue
            event = item["event"]
            assert not re.search(r"\d", event) and not _words(event) & TIME_WORDS, event
            assert not event.lower().startswith(FRAME_OPENINGS) and "?" not in event, event
            assert _count(vs.gate_question(window, event)) <= vs.STEM_MAX_WORDS
            assert _count(vs.frequency_question(window, event)) <= vs.STEM_MAX_WORDS
            assert not _words(event) & (PRODUCT_WORDS | terms), event


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_pick_rides_on_the_wires_own_code(entry_id):
    """A person's pick on a list the founder made is sent on the list's positional code (Importance's
    `own` / `rival_n`, Current solution's `outcome_n`, Relative advantage's `benefit_n`), and every
    `optionCounts` code the entry records maps onto one -- the fixed answers pass through unchanged."""
    entry = _entry(entry_id)
    importance = vs.wire_codes(entry, "problem.importance")
    own = (entry.founder_list("problem.importance") or {})["items"][0]["code"]
    assert importance[own] == "own" and sorted(importance.values()) == [
        "own", "rival_1", "rival_2", "rival_3", "rival_4"]
    for person in vs.person_inputs(entry):
        for pick in person.picks:
            codes = vs.wire_codes(entry, pick.dimension)
            if codes:
                assert set(pick.codes) <= set(codes.values()) | {"positive", "neutral", "negative"}, pick
            for code in pick.advantages:
                assert code.startswith("benefit_"), pick
            if pick.dimension == "problem.importance" and not pick.chip:
                assert len(pick.codes) == 2, pick
    for key, row in ((entry.expected or {}).get("standings") or {}).items():
        for code in corpus_scenario._option_counts(row.get("optionCounts", "")):
            wire = vs.on_the_wire(entry, key, code)
            assert wire == code or key in vs.PICKED_AMONG_ITEMS, (key, code, wire)


def test_the_screen_table_names_themes_by_its_four_keys_and_no_brief():
    """Spec 052: keel-cloud 104's THEMES is in the corridor's table by exactly `Insights.Due.context()`'s four keys (the
    runtime matches the screen by them, keel-runtime 012 FR-1); BRIEF is gone; a THEMES row the export moved is
    refused by name."""
    assert vs.THEMES_SCREEN in vs.CORRIDOR_SCREENS and "BRIEF" not in vs.CORRIDOR_SCREENS
    assert not hasattr(vs, "brief_result") and not hasattr(vs, "BRIEF_SCREEN")
    assert vs.THEMES_KEYS == ("dimension", "name", "rungHeading", "answers")
    exported = {screen: [f"{screen.lower()}_key"] for screen in vs.CORRIDOR_SCREENS}
    exported[vs.RESPONDENT_SCREEN] = ["part", "link", "items", "mechanism", "offer_name"]
    exported[vs.THEMES_SCREEN] = ["dimension", "name", "answers"]
    with pytest.raises(vs.VectorsScriptError, match="THEMES"):
        vs.context_keys_for(exported)
    exported[vs.THEMES_SCREEN] = list(vs.THEMES_KEYS)
    assert vs.context_keys_for(exported)[vs.THEMES_SCREEN] == list(vs.THEMES_KEYS)


# ------------------------------------------------------------------------------- the keys table

def test_the_respondent_screen_is_part_ones_key_set_derived_from_the_export():
    """keel-cloud 091: the lock's one job is part 1's, so the table names part 1's key set alone (the export's union
    less `mechanism` and `offer_name`) -- a part 2 or 3 job would match nothing (spec 041's four aliases are gone)."""
    union = ["part", "link", "context", "market", "founder_name", "items", "mechanism", "offer_name"]
    exported = {screen: [f"{screen.lower()}_key"] for screen in vs.CORRIDOR_SCREENS}
    exported[vs.RESPONDENT_SCREEN] = union
    exported[vs.THEMES_SCREEN] = list(vs.THEMES_KEYS)
    table = vs.context_keys_for(exported)
    base = [k for k in union if k not in ("mechanism", "offer_name")]
    assert table[vs.RESPONDENT_SCREEN] == base
    assert not any(k.startswith("RESPONDENT_QUESTIONS_") for k in table) and "PROBLEM_FRAME" not in table
    assert not hasattr(vs, "RESPONDENT_ALIASES")
    assert table[vs.ASKED_SCREEN] == ["asked_key"]
    assert len({frozenset(v) for v in table.values()}) == len(table), "two names share a key set"


def test_an_export_that_lost_the_per_part_keys_is_refused_by_name():
    exported = {screen: [screen] for screen in vs.CORRIDOR_SCREENS}
    exported[vs.RESPONDENT_SCREEN] = ["part", "link", "items"]
    with pytest.raises(vs.VectorsScriptError, match="mechanism"):
        vs.context_keys_for(exported)


# ------------------------------------------------------------------------------- the founder

def test_frequency_is_asked_where_the_window_carries_it_and_left_out_on_mulch_run():
    """D13 (spec 040): Countly's {4, WEEKS} carries its "1 to 3 weeks out of 4"; since revision 11 (keel-cloud 091
    FR-G) Paidly's {3, MONTHS} carries its "2 to 3 months out of 3" -- both asked. D-1 (spec 042): Mulch Run's
    "working days out of 7" on two weeks still does not (091 call 11), so the founder leaves it out and the standing
    asserted is LEFT_OUT."""
    for entry_id, interval in (("01-countly", {"low": 1, "high": 3, "unit": "weeks out of 4"}),
                               ("05-paidly", {"low": 2, "high": 3, "unit": "months out of 3"})):
        entry = _entry(entry_id)
        assert vs.frequency_fits(entry), entry_id
        problem = {a.dimension: a.body for a in vs.calibration_answers(entry, "PROBLEM")}
        assert problem["problem.frequency"]["interval"] == interval, entry_id
        assert corpus_scenario.expected_status(entry, "problem.frequency") == "HOLDING_UP", entry_id
        assert "problem.frequency" in vs.plan_keys(entry, 1, vs.LINK_PRIMARY), entry_id
    mulch = _entry("07-mulchrun")
    assert not vs.frequency_fits(mulch)
    assert corpus_scenario.expected_status(mulch, "problem.frequency") == "LEFT_OUT"
    problem = {a.dimension: a.body for a in vs.calibration_answers(mulch, "PROBLEM")}
    assert problem["problem.frequency"] == {"dimension": "problem.frequency", "unsure": True}


def test_idea_names_read_as_keel_cloud_derives_them():
    """keel-cloud 090 `IdeaLines.nameOf` restated (`vs.idea_name_of`): *Imagine* and the full stop are not the name, an
    article is kept and lower-cased, a sentence-case first word is lower-cased when nothing else is capitalised, a
    title-case name, a capital inside a word and a one-word name keep their case."""
    assert vs.idea_name_of("Imagine a payroll error checker.") == "a payroll error checker"
    assert vs.idea_name_of("Payroll error catcher") == "payroll error catcher"
    assert vs.idea_name_of("  Anomaly   detection tool. ") == "anomaly detection tool"
    assert vs.idea_name_of("The Payroll tool") == "the Payroll tool"
    assert vs.idea_name_of("Payroll Checker") == "Payroll Checker"
    assert vs.idea_name_of("PayCheck tool") == "PayCheck tool"
    assert vs.idea_name_of("Keel") == "Keel"
    assert vs.idea_name_of("imagine") == ""
    assert vs.idea_card("payroll error catcher") == "Imagine payroll error catcher."
    assert vs.benefit_question("payroll run", "a list of flagged employees") == (
        "On your last payroll run, would a list of flagged employees have made things better, or not?")


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_every_founder_names_the_idea_and_one_names_it_their_own_way(entry_id):
    """keel-cloud 097 F7 (spec 046 FM4): Keel drafts no name -- the idea is served with `what` null, because no r11 solution
    seed carries a product name (`IdeaName.fromSeed`, restated as `vs.seed_idea_name`) -- so every founder types one on
    S2: the entry's short name, or (05-paidly, `IDEA_NAMES`) a name of their own -- at most five words, no claim word
    (L5, L3) -- which every later question uses. Every composed stem it lands in stays within 20 words."""
    entry = _entry(entry_id)
    assert vs.seed_idea_name(entry.statements["solution"]) is None
    assert vs.idea_view(entry)["what"] is None
    typed = vs.founder_idea_name(entry)
    founder = vs.founder_inputs(entry)
    assert founder.idea_name == typed and 1 <= len(typed.split()) <= vs.NAME_MAX_WORDS
    if entry_id == "05-paidly":
        assert typed == "Invoice payout service" and vs.idea_name(entry) == "invoice payout service"
        assert not _words(typed) & (CLAIM_WORDS | PRODUCT_WORDS)
        assert len(vs.idea_card(vs.idea_name(entry))) <= 80
    else:
        assert typed == vs.short_name(entry) and vs.idea_name(entry) == vs.idea_name_of(vs.short_name(entry))
    assert _count(vs.benefit_question(vs.occasion(entry), vs.idea_name(entry))) <= vs.STEM_MAX_WORDS


def test_the_seed_name_rule_reads_as_keel_cloud_097_wrote_it():
    """keel-cloud 097 `IdeaName.fromSeed` restated (judgement call 14): a quoted phrase of one to five words without
    sentence punctuation; else the first run of two to five capitalised words that is not only a sentence's opening
    capital (a common opener dropped), not a place after *in* / *at* / *from* ..., not acronyms alone; else None."""
    assert vs.seed_idea_name('We call it "Payroll Guard". It checks the run.') == "Payroll Guard"
    assert vs.seed_idea_name("We call it \u201cPay Check\u201d, a checker.") == "Pay Check"
    assert vs.seed_idea_name('It is "a tool. that checks"') is None
    assert vs.seed_idea_name("Restaurants in New York would use Payroll Guard Pro daily.") == "Payroll Guard Pro"
    assert vs.seed_idea_name("The Payroll Guard checks every run.") == "Payroll Guard"
    assert vs.seed_idea_name("When the HR IT team runs payroll, nothing checks it.") is None
    assert vs.seed_idea_name("A platform that pays the translator within seven days.") is None
    assert vs.seed_idea_name("") is None and vs.seed_idea_name(None) is None


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_importance_is_drafted_as_the_own_item_then_what_the_answer_names(entry_id):
    """keel-cloud 097 F9 (judgement call 10; spec 046 FM2): the slice's first draft of Importance is the own item alone,
    the founder's Answer names the other difficulties (never the own item, which is code's, locked first), and the
    redraft from it is the own item and exactly those; on 01-countly the Answer names one and on 05-paidly two (the
    founder types the rest of the corpus list on the Check screen, keel-web 070 F9), elsewhere all four."""
    entry = _entry(entry_id)
    if entry.unsure("problem.importance"):
        pytest.skip("Importance left out")
    screens = vs.generate(entry).screens[vs.CALIBRATION_SCREEN]
    jobs = vs.calibration_jobs(entry)
    first = next(e for e, (v, only) in zip(screens, jobs) if v == "PROBLEM" and only is None)
    redraft = next(e for e, (v, only) in zip(screens, jobs) if only == "problem.importance")
    own, *others = [i["label"] for i in vs.founder_list(entry, "problem.importance")["items"]]
    named = vs.importance_named(entry)
    drafted = {q["key"]: q for q in first["result"]["questions"]}["problem.importance"]["list"]["items"]
    assert [i["label"] for i in drafted] == [own]
    assert [i["label"] for i in redraft["result"]["questions"][0]["list"]["items"]] == [own] + named
    answer = vs.answer_text(entry, "problem.importance")
    assert [p.strip() for p in answer.split(";")] == named and own not in answer
    assert named + vs.importance_typed(entry) == others, "the founder types the rest of their own list on Check"
    assert len(named) == {"01-countly": 1, "05-paidly": 2}.get(entry_id, len(others)), "one, two, then all named"
    assert vs.IMPORTANCE_MIN_ITEMS <= 1 + len(others) <= 5


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_founder_answers_on_the_wires_own_shapes(entry_id):
    entry = _entry(entry_id)
    founder = vs.founder_inputs(entry)
    commercial = {a.dimension: a.body for a in founder.calibration["COMMERCIAL"]}
    assert "commercial.ability_to_pay" not in commercial, "Ability to pay is derived, never sent"
    cost = commercial["commercial.existing_sacrifice"]
    assert set(cost["cost"]) >= {"mode", "low", "high", "period"}
    price = commercial["commercial.price"]
    assert price.get("unsure") or set(price["price"]) == {"low", "high", "period"}
    if vs.is_b2b(entry):
        assert founder.decider == {"kind": "SOMEONE_ELSE", "role": entry.decision_maker_role()}
    else:
        assert founder.decider == {"kind": "SAME_PERSON"}
    assert founder.window.as_wire() == entry.context["recall_window"]
    for vector in vs.VECTORS:
        for answer in founder.calibration[vector]:
            if not vs.is_list(answer.dimension) or answer.unsure:
                assert answer.text is None and "list" not in answer.body
                continue
            listed = answer.body["list"]
            saved = vs.saved_list(entry, answer.dimension)
            assert [i["label"] for i in listed["items"]] == [i["label"] for i in saved["items"]]
            assert listed["pickedIndex"] == saved["pickedIndex"]
            assert (listed["pickedIndex"] is not None) == (answer.dimension in vs.PICKED)
            assert "code" not in json.dumps(listed["items"]), "a code the client sends is ignored, so none is"
            assert 1 <= _count(answer.text) <= 25, answer.text


# ------------------------------------------------------------------------------- the people

def test_a_cost_total_is_re_expressed_over_the_period_it_is_asked_over():
    """D-3: revision 10 records every cost total over a quarter; keel-cloud asks over the founder's
    own period (a month here), so the amount is carried by keel-cloud's own `Period` days -- and
    "nothing" is the number 0 typed as an amount (D8), which needs no re-expressing."""
    pick = vs.Pick(dimension="commercial.existing_sacrifice", cost={"mode": "AMOUNT", "value": 150},
                   cost_period="quarter")
    month = pick.asked_over("month")
    assert month.cost["value"] == pytest.approx(150 * 30.4375 / 91.3125)
    assert month.cost_period == "month"
    assert pick.asked_over("quarter") is pick
    nothing = vs.Pick(dimension="commercial.existing_sacrifice", cost={"mode": "AMOUNT", "value": 0},
                      cost_period="quarter")
    assert nothing.asked_over("month") is nothing


def test_nothing_is_typed_as_zero_and_the_gate_story_chip_is_cant_recall_alone():
    """D8 / keel-web 064: Paidly's two decision-makers who lost nothing send `{AMOUNT, 0}`; Xavier Dubois's
    r10 `rather_not_say` story chip is gone from contract 13 and travels as CANT_RECALL (spec 041 D-4)."""
    entry = _entry("05-paidly")
    people = {p.person: p for p in vs.person_inputs(entry)}
    for name in ("Sara Cedar", "Wanda Gorse"):
        cost = next(p for p in people[name].picks if p.dimension == "commercial.existing_sacrifice")
        assert cost.as_wire("t")["costTotal"] == {"mode": "AMOUNT", "value": 0}
    assert people["Xavier Dubois"].anchor_chip == "CANT_RECALL"


def test_each_link_carries_only_its_own_parts():
    entry = _entry("05-paidly")
    for person in vs.person_inputs(entry):
        dims = {p.dimension for p in person.picks}
        if person.link == vs.LINK_B2B:
            assert all(d.startswith("commercial.") for d in dims), person.person
            assert "recency" not in person.response("t")
        else:
            assert not any(d.startswith("commercial.") for d in dims), person.person


def test_a_gate_no_is_the_counted_empty_body_and_a_chip_travels_alone():
    entry = _entry("07-mulchrun")
    people = {p.person: p for p in vs.person_inputs(entry)}
    no = next(p for p in people.values() if p.recency is False)
    assert no.response("t") == {"recency": False, "answers": []}
    chipped = next(p for p in people.values() if p.anchor_chip)
    body = chipped.response("t")
    assert body["anchorChip"] == "CANT_RECALL" and "story" not in body


# ------------------------------------------------------------------------------- the scenario

def test_the_scenario_is_one_function_per_leg_in_the_corridors_order():
    source = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    order = ["leg_project", "leg_context", "leg_interpret_problem", 'leg_calibrate(journey, "PROBLEM")',
             "leg_interpret_solution", 'leg_calibrate(journey, "SOLUTION")', "leg_persona",
             'leg_calibrate(journey, "COMMERCIAL")', "leg_lock", "leg_invite", "leg_interview",
             "leg_standings", "leg_report"]
    run = source[source.index("def run("):]
    at = [run.index(name) for name in order]
    assert at == sorted(at)
    for leg in ("leg_project", "leg_context", "leg_interpret_problem", "leg_interpret_solution",
                "leg_calibrate", "leg_persona", "leg_lock", "leg_invite", "leg_interview",
                "leg_standings", "leg_report"):
        assert f"def {leg}(" in source, leg


def test_the_scenario_carries_no_classic_reader_no_model_and_no_drift_74_step():
    source = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    for classic in ("corpus_script", "walk_stage", "ReviewCard", "OpenedCard", "expected.buckets",
                    "SUPPORTED", "CONTRADICTED", "DRIFT #74", "somethingElse", "RATHER_NOT_SAY"):
        assert classic not in source, classic
    assert "KEEL_SCRIPT" in source and "KEEL_CONTEXT_KEYS" in source, (
        "every job is answered by the scripted executor, through the derived keys table")


def test_every_product_defect_the_journey_steps_round_is_named_in_drift():
    source = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    screens = (REPO / "harness" / "vectors_screens.py").read_text(encoding="utf-8")
    drift = (REPO / "runs" / "DRIFT.md").read_text(encoding="utf-8")
    for number in ("78", "79", "80", "81"):
        assert f"DRIFT #{number}" in source and f"DRIFT.md #{number}" in source + screens, number
        assert re.search(rf"^## {number}\. ", drift, re.M), number


def test_the_three_corpus_extras_name_only_what_survived():
    s005 = (REPO / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    s006 = (REPO / "evals" / "test_s006_paidly.py").read_text(encoding="utf-8")
    s007 = (REPO / "evals" / "test_s007_mulchrun.py").read_text(encoding="utf-8")
    assert "TOO_FEW_TO_CALL" in s005 and "FLOOR = 5" in s005
    assert "FLOOR = 5" in s006 and "COMMERCIAL_LINK" in s006
    assert '"region") == "TX"' in s007 and "OTHER_CURRENCIES" in s007 and '"USD"' in s007
    # spec 053 FR-3d: the currency sweep is every corpus journey's, after the report
    scenario = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    assert corpus_scenario.OTHER_CURRENCIES == ("\N{POUND SIGN}", "€", "GBP", "EUR")
    assert "OTHER_CURRENCIES" in scenario
    assert "        leg_report(journey)\n        leg_one_currency(journey)\n" in scenario
    for body in (s005, s006, s007):
        assert "buckets" not in body and "MOCKUP" not in body and "one-unit window" not in body


class _Step:
    def __init__(self):
        self.asserted = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def record_assert(self, want, have):
        self.asserted = (want, have)


class _Recorder:
    def step(self, name, **kwargs):
        return _Step()


def _currency_journey(screens, market):
    from types import SimpleNamespace                                   # noqa: PLC0415
    return SimpleNamespace(entry=SimpleNamespace(id="01-countly",
                                                 market={"country": "US", "region": None, "language": "en-US"}),
                           screens=screens, recorder=_Recorder(), project=lambda path: path,
                           get=lambda url: {"market": market})


REPORT_DRAWN = {name: {"text": f"{name} $50 a month or more"} for name in corpus_scenario.REPORT_VIEWS}


def test_every_corpus_journey_sweeps_for_another_currency_and_holds_the_entrys_market():
    """Spec 053 FR-3d (call 3): no other currency on any drawn page, the report's views included, and the project's
    market the entry's own -- the sweep S-007 alone ran until revision 12, on every journey."""
    us = {"country": "US", "region": None, "language": "en-US"}
    corpus_scenario.leg_one_currency(_currency_journey(dict(REPORT_DRAWN, L1={"text": "$10 to $30"}), us))
    for leak in ("€20", "20 GBP", "EUR 20"):
        screens = dict(REPORT_DRAWN, COMMERCIAL={"text": f"about {leak} a month"})
        assert corpus_scenario.currency_leaks(screens) == {"COMMERCIAL": [c for c in corpus_scenario.OTHER_CURRENCIES
                                                                          if c in leak]}
        with pytest.raises(AssertionError):
            corpus_scenario.leg_one_currency(_currency_journey(screens, us))
    with pytest.raises(AssertionError, match="swept nothing"):
        corpus_scenario.leg_one_currency(_currency_journey(dict(REPORT_DRAWN, printed={"text": " "}), us))
    with pytest.raises(AssertionError):
        corpus_scenario.leg_one_currency(_currency_journey(REPORT_DRAWN, dict(us, country="GB", language="en-GB")))


def test_choose_picks_the_entrys_own_item_and_on_a_live_journey_the_models_at_that_place():
    answer = vs.CalibrationAnswer(dimension="solution.compatibility", body={
        "dimension": "solution.compatibility",
        "list": {"items": [{"label": "A"}, {"label": "B"}, {"label": "C"}], "pickedIndex": 2}}, text="A; B; C")
    question = {"dimension": "solution.compatibility", "draft": {"items": [{"label": "x"}, {"label": "y"}]}}

    class _J:
        strict = True
    assert corpus_scenario._choose_label(_J(), question, answer) == ("C", 2)
    _J.strict = False
    assert corpus_scenario._choose_label(_J(), question, answer) == ("y", 1)


def test_a_check_screen_is_read_in_the_corpus_shape():
    rows = [{"text": "Mine", "tag": "yours", "locked": True}, {"text": "Two", "tag": "", "locked": False}]
    assert corpus_scenario._drawn_list("problem.importance", {"rows": rows, "field": None}) == {
        "items": ["Mine", "Two"]}
    assert corpus_scenario._drawn_list("commercial.commitment", {"rows": [], "field": "install the app"}) == {
        "items": ["install the app"]}
    roles = [{"text": "manager · has the problem", "tag": "context", "locked": True}]
    assert corpus_scenario._drawn_list("commercial.buyer_payer_alignment", {"rows": roles, "field": None}) == {
        "items": []}


def test_the_inputs_bundle_records_what_was_composed():
    entry = _entry("01-countly")
    founder = vs.founder_inputs(entry)
    inputs = vs.inputs_json(entry, founder, vs.person_inputs(entry))
    assert inputs["composed"] == list(vs.COMPOSED)
    importance = next(a for a in inputs["founder"]["calibration"]["PROBLEM"]
                      if a["dimension"] == "problem.importance")
    assert importance["_answer"] and importance["list"]["items"][0]["label"] == (
        "Matching deliveries against their invoices")
    json.dumps(inputs)


def test_the_pilot_tile_is_worded_as_keel_web_077_words_it():
    """keel-web 077 FR-2 (`pilotSignedUp`, `pilotLinkLine`): *k of n signed up* over *p% · per link*; *None yet* and
    *fills as people finish* before anyone finishes (`instructions/overview.tiles`)."""
    from instructions import overview as ov                                 # noqa: PLC0415
    pilot = {"optedIn": 2, "finished": 20, "percent": 10, "perLink": [
        {"link": "PRIMARY", "words": "people who have it", "optedIn": 2, "finished": 12},
        {"link": "COMMERCIAL_B2B", "words": "decision-makers", "optedIn": 0, "finished": 8}]}
    assert ov.tiles({"pilot": pilot}, None)["pilot"] == [
        "Pilot", "2 of 20 signed up", "10% · 2 of 12 people who have it · 0 of 8 decision-makers"]
    assert ov.tiles({"pilot": {"finished": 0}}, None)["pilot"] == ["Pilot", "None yet", "fills as people finish"]
    assert not hasattr(corpus_scenario, "pilot_words") and not hasattr(corpus_scenario, "PAGE_ONE_BANS")
