"""Spec 039: the corpus journeys are vectors journeys -- the script, the typed inputs and the legs,
held without a stack.

Read through keel-cloud's own canon corpus (revision 9), as the three scenarios read it, so a corpus
edit that a journey could no longer drive fails here before it fails twenty steps into a run. Every
test that needs the canon skips by name when `stack.toml`'s keel-cloud checkout carries none.
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
TIME_WORDS = {"last", "past", "recent", "recently", "ago", "today", "yesterday", "week", "weeks",
              "month", "months", "year", "years", "day", "days", "night", "nights", "shift",
              "shifts", "cycle", "cycles"}


def _entry(entry_id: str):
    from stack.config import load_config
    keel_cloud = Path(load_config(validate=False).keel_cloud)
    if not (keel_cloud / "canon" / "designs" / "measured-beliefs" / "corpus").is_dir():
        pytest.skip(f"no keel-cloud corpus at {keel_cloud}")
    return vs.entry_for(keel_cloud, entry_id)[1]


def _words(text: str) -> set:
    return set(re.findall(r"[a-z']+", text.lower()))


# ------------------------------------------------------------------------------- the id codec

def test_the_ids_are_keel_clouds_interview_id_codec():
    """`InterviewIdCodec`: the first twelve hex of sha256 over `token|item|dim` and
    `token|option|dim|code` -- which is what lets a pick be sent by code with no label matched."""
    assert vs.item_id("tok", "problem.importance") == hashlib.sha256(
        b"tok|item|problem.importance").hexdigest()[:12]
    assert vs.option_id("tok", "commercial.price", "band_20_50") == hashlib.sha256(
        b"tok|option|commercial.price|band_20_50").hexdigest()[:12]


def test_the_slug_is_keel_clouds_first_four_words():
    assert vs.slug("None of these; they cope with what they have") == "none_of_these_they"
    assert vs.slug("Owner approval") == "owner_approval"
    assert vs.slug(vs.label_of_code("matching_deliveries")) == "matching_deliveries"


# ------------------------------------------------------------------------------- the script

@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_script_answers_every_corridor_screen_from_the_entry(entry_id):
    entry = _entry(entry_id)
    screens = vs.generate(entry).screens
    jobs = vs.respondent_jobs(entry)
    want = {vs.CONTEXT_SCREEN, vs.PROBLEM_SCREEN, vs.MECHANISM_SCREEN, vs.CALIBRATION_SCREEN,
            vs.INTERPRET_SCREEN, vs.BRIEF_SCREEN} | {vs.RESPONDENT_ALIASES[j] for j in jobs}
    assert set(screens) == want
    assert [e["result"]["vector"] for e in screens[vs.CALIBRATION_SCREEN]] == list(vs.VECTORS), (
        "the three calibration jobs share one key set, so their entries are the corridor's order")
    assert len(screens[vs.INTERPRET_SCREEN]) == len(vs.readable_people(entry))
    assert [e["result"]["anchoring"] for e in screens[vs.INTERPRET_SCREEN]] == [
        p.anchoring for p in vs.readable_people(entry)]
    context = screens[vs.CONTEXT_SCREEN][0]["result"]
    assert context["understands"] == entry.context["understood"]
    assert screens[vs.PROBLEM_SCREEN][0]["result"]["statement"] == entry.interpretations["problem"]
    mechanism = screens[vs.MECHANISM_SCREEN][0]["result"]
    assert mechanism["short_name"] in mechanism["idea_what"]
    assert mechanism["idea_belief"].startswith(vs.BELIEF_FRAME)
    assert 3 <= len(mechanism["mechanism_terms"]) <= 8


def test_a_b2b_entry_writes_part_three_for_the_decision_makers_link():
    assert (3, vs.LINK_B2B) in vs.respondent_jobs(_entry("05-paidly"))
    assert (3, vs.LINK_PRIMARY) in vs.respondent_jobs(_entry("01-countly"))


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_composed_calibration_words_keep_keel_clouds_rules(entry_id):
    """C5 (no product word in a PROBLEM question), C6 (no claim word in a SOLUTION question, but
    *better* on Relative advantage), W3/W8 (the short name and the offer's name), E1/E3 (the
    Prevalence clause carries no number, no time word, no frame opening) -- on the referee's own
    words, which keel-cloud would otherwise refuse with one repair turn the script cannot answer."""
    entry = _entry(entry_id)
    for vector in vs.VECTORS:
        for q in vs.calibration_result(entry, vector)["questions"]:
            text = " ".join([q.get("question") or "", q.get("event") or ""]
                            + [o["label"] + " " + o["belief_phrase"] for o in q.get("options") or []])
            if vector == "PROBLEM":
                assert not _words(text) & PRODUCT_WORDS, (q["key"], text)
            if vector == "SOLUTION":
                claims = CLAIM_WORDS - ({"better"} if q["key"] == "solution.relative_advantage" else set())
                assert not _words(text) & claims, (q["key"], text)
                if q.get("question"):
                    assert vs.short_name(entry) in q["question"], q
            if vector == "COMMERCIAL" and q.get("question"):
                assert vs.offer_name(entry) in q["question"], q
            if q["key"] == "problem.prevalence":
                assert not re.search(r"\d", q["event"]) and not _words(q["event"]) & TIME_WORDS
                assert not q["event"].lower().startswith(("in ", "how many", "did you"))
            assert not re.search(r"[£$€]", text), (q["key"], text)


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_respondent_words_keep_keel_clouds_rules(entry_id):
    entry = _entry(entry_id)
    for part, link in vs.respondent_jobs(entry):
        result = vs.respondent_result(entry, part, link)
        assert [i["key"] for i in result["items"]] == vs.plan_keys(entry, part, link)
        for item in result["items"]:
            question = item.get("question") or ""
            assert not re.search(r"\b(usually|typically|normally|generally)\b", question), item
            if part == 1:
                assert not _words(question + " ".join(item.get("options") or [])) & PRODUCT_WORDS
            if part == 2 and question:
                assert vs.short_name(entry) in question, item
            if part == 3 and question:
                assert vs.offer_name(entry) in question, item


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_importance_and_purchase_friction_slug_to_the_corpus_codes(entry_id):
    """A model-written set's codes are keel-cloud's slugs of its labels, so the labels this journey
    writes are each the slug-inverse of a corpus code -- and Importance's own item goes first."""
    entry = _entry(entry_id)
    row = entry.respondent_questions["problem.importance"]
    labels = vs.importance_labels(entry)
    assert vs.slug(labels[0]) == row["own_item"]
    assert {vs.slug(label) for label in labels} == {c for c in row["codes"] if c != "something_else"}
    if vs.is_b2b(entry):
        codes = [c for c in entry.respondent_questions["commercial.purchase_friction"]["codes"]
                 if c not in vs.RESPONDENT_ESCAPES]
        pairs = vs.purchase_friction_labels(entry)
        assert 4 <= len(pairs) <= 6
        assert [vs.slug(label) for label, _ in pairs][:len(codes)] == codes
        assert all(vs.slug(label) == code for label, code in pairs)


@pytest.mark.parametrize("entry_id", ENTRIES)
def test_the_brief_reading_cites_its_own_vectors_and_carries_no_number(entry_id):
    entry = _entry(entry_id)
    reading = vs.brief_result(entry)
    sentences = [reading["headline"], reading["next"]["sentence"],
                 *reading["tiles"].values(), reading["problem"]["conclusion"],
                 reading["problem"]["infer"], reading["solution"]["conclusion"],
                 reading["commercial"]["conclusion"]]
    for sentence in sentences:
        assert sentence["cites"] and not re.search(r"\d", sentence["text"]), sentence
        assert len(sentence["text"]) <= 400
    assert len(set(reading["problem"]["infer"]["cites"])) == 2
    for vector in ("problem", "solution", "commercial"):
        assert all(c.startswith(vector + ".") for c in reading["tiles"][vector]["cites"])
    assert reading["next"]["tests"] == [] and reading["quotes"] == []


# ------------------------------------------------------------------------------- the keys table

def test_the_respondent_screen_becomes_four_names_derived_from_the_export():
    union = ["part", "link", "context", "market", "founder_name", "items", "founder_options",
             "mechanism", "offer_name"]
    exported = {screen: [f"{screen.lower()}_key"] for screen in vs.CORRIDOR_SCREENS}
    exported[vs.RESPONDENT_SCREEN] = union
    table = vs.context_keys_for(exported)
    base = [k for k in union if k not in ("mechanism", "offer_name")]
    assert table["RESPONDENT_QUESTIONS_P1"] == base
    assert table["RESPONDENT_QUESTIONS_P2"] == base + ["mechanism"]
    assert table["RESPONDENT_QUESTIONS_P3"] == union
    assert table["RESPONDENT_QUESTIONS_P3_B2B"] == base + ["offer_name"]
    assert "RESPONDENT_QUESTIONS" not in table and "PROBLEM_FRAME" not in table
    assert len({frozenset(v) for v in table.values()}) == len(table), "two names share a key set"


def test_an_export_that_lost_the_per_part_keys_is_refused_by_name():
    exported = {screen: [screen] for screen in vs.CORRIDOR_SCREENS}
    exported[vs.RESPONDENT_SCREEN] = ["part", "link", "items"]
    with pytest.raises(vs.VectorsScriptError, match="mechanism"):
        vs.context_keys_for(exported)


# ------------------------------------------------------------------------------- the founder

def test_frequency_cannot_be_stated_on_any_of_the_three_entries_own_windows():
    """D-1: revision 9 keeps every Frequency on a 0-to-7 axis its own recall window cannot carry --
    so the journey leaves it out rather than inventing a number, and the standing it asserts is
    LEFT_OUT."""
    for entry_id in ENTRIES:
        entry = _entry(entry_id)
        assert not vs.frequency_fits(entry), entry_id
        assert corpus_scenario.expected_status(entry, "problem.frequency") == "LEFT_OUT"
        problem = {a.dimension: a.body for a in vs.calibration_answers(entry, "PROBLEM")}
        assert problem["problem.frequency"] == {"dimension": "problem.frequency", "unsure": True}


def test_a_one_unit_window_shows_no_frequency_screen_and_still_sends_its_answer():
    """runs/DRIFT.md #74: on `01-countly`'s one-unit window keel-web draws no Frequency screen, yet
    the standings 500 until it carries an answer -- so the answer travels on the wire, apart from the
    screens, and the founder's screens are asserted to be the job's slice less Frequency."""
    entry = _entry("01-countly")
    assert vs.one_unit_window(entry)
    assert "problem.frequency" not in vs.founder_keys(entry, "PROBLEM")
    assert "problem.frequency" in vs.calibrated_keys(entry, "PROBLEM")
    assert "problem.frequency" in [a.dimension for a in vs.calibration_answers(entry, "PROBLEM")]


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
    assert founder.decider["kind"] == ("SOMEONE_ELSE" if vs.is_b2b(entry) else "SAME_PERSON")
    assert founder.window.as_wire() == entry.context["recall_window"]


# ------------------------------------------------------------------------------- the people

def test_a_cost_total_is_re_expressed_over_the_period_it_is_asked_over():
    """D-3: revision 9 records every cost total over a quarter; keel-cloud asks over the founder's
    own period (a month here), so the amount is carried by keel-cloud's own `Period` days."""
    pick = vs.Pick(dimension="commercial.existing_sacrifice", cost={"mode": "AMOUNT", "value": 150},
                   cost_period="quarter")
    month = pick.asked_over("month")
    assert month.cost["value"] == pytest.approx(150 * 30.4375 / 91.3125)
    assert month.cost_period == "month"
    assert pick.asked_over("quarter") is pick
    nothing = vs.Pick(dimension="commercial.existing_sacrifice", cost={"nothing": True},
                      cost_period="quarter")
    assert nothing.asked_over("month") is nothing


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
             "leg_standings", "leg_brief"]
    run = source[source.index("def run("):]
    at = [run.index(name) for name in order]
    assert at == sorted(at)
    for leg in ("leg_project", "leg_context", "leg_interpret_problem", "leg_interpret_solution",
                "leg_calibrate", "leg_persona", "leg_lock", "leg_invite", "leg_interview",
                "leg_standings", "leg_brief"):
        assert f"def {leg}(" in source, leg


def test_the_scenario_carries_no_classic_reader_and_no_model():
    source = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    for classic in ("corpus_script", "walk_stage", "ReviewCard", "OpenedCard", "expected.buckets",
                    "SUPPORTED", "CONTRADICTED"):
        assert classic not in source, classic
    assert "KEEL_SCRIPT" in source and "KEEL_CONTEXT_KEYS" in source, (
        "every job is answered by the scripted executor, through the derived keys table")


def test_the_three_corpus_extras_name_only_what_survived():
    s005 = (REPO / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    s006 = (REPO / "evals" / "test_s006_paidly.py").read_text(encoding="utf-8")
    s007 = (REPO / "evals" / "test_s007_mulchrun.py").read_text(encoding="utf-8")
    assert "TOO_FEW_TO_CALL" in s005 and "FLOOR = 5" in s005
    assert "FLOOR = 5" in s006 and "COMMERCIAL_LINK" in s006
    assert '"region") == "TX"' in s007 and "OTHER_CURRENCIES" in s007
    for body in (s005, s006, s007):
        assert "buckets" not in body and "MOCKUP" not in body


def test_the_offered_codes_fall_back_only_on_a_live_journey():
    view = {"questions": [{"dimension": "commercial.purchase_friction",
                           "options": [{"normalized": "a"}, {"normalized": "b"}, {"normalized": "c"}]}]}
    answer = {"dimension": "commercial.purchase_friction", "codes": ["x", "y"]}

    class _J:
        strict = False
    assert corpus_scenario._offered_codes(_J(), answer, view)["codes"] == ["a", "b"]
    _J.strict = True
    with pytest.raises(AssertionError):
        corpus_scenario._offered_codes(_J(), answer, view)
    ok = {"dimension": "commercial.purchase_friction", "codes": ["b"]}
    assert corpus_scenario._offered_codes(_J(), ok, view) == ok


def test_the_inputs_bundle_records_what_was_composed():
    entry = _entry("01-countly")
    founder = vs.founder_inputs(entry)
    inputs = vs.inputs_json(entry, founder, vs.person_inputs(entry))
    assert inputs["composed"] == list(vs.COMPOSED)
    json.dumps(inputs)
