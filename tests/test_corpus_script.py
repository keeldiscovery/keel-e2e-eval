"""The corpus -> script generator, with no stack, no browser and no money spent (spec 010 FR-033,
T008; contracts/generated-script-contract.md).

Acceptance scenario 7 -- *every belief, anchor, selection and person's answer in the script came
from the entry, and the script contains no value the entry does not carry* -- is a **unit test
before it is a run**: `test_every_literal_in_the_script_came_from_the_entry` below asserts it
against all three chosen corpus entries and the smoke's own fixture, in under a second.
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from harness import corpus_script as cs
from instructions import corpus as corpus_reader
from stack.config import load_config

CHOSEN = ("01-countly", "05-paidly", "07-mulchrun")


# ------------------------------------------------------------------------------ a canned entry

CANNED = {
    "id": "00-canned",
    "title": "Canned — a fixture that is not the corpus",
    "market": {"country": "GB", "region": None, "language": "en-GB"},
    "statements": {"problem": "A problem.", "solution": "A solution.", "commercial": "A price."},
    "roles": [{"id": "r1", "label": "Someone", "roleType": "PRACTITIONER", "about": "does a thing"}],
    "beliefs": [
        {"id": "B1", "stage": "PROBLEM", "heading": "It happens", "statement": "It happened.",
         "founderPhrase": "most weeks", "risk": "LOAD_BEARING", "askedOf": "r1", "mark": "DIRECT",
         "expectation": {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"},
         "selection": "S1"},
        {"id": "B2", "stage": "PROBLEM", "heading": "It takes a while",
         "statement": "It took an hour.", "founderPhrase": "about an hour", "risk": "SUPPORTING",
         "askedOf": "r1", "mark": "PROXY",
         "expectation": {"type": "INTERVAL",
                         "measure": {"kind": "DURATION", "unit": "hours", "per": None},
                         "lower": {"value": 1, "inclusive": True, "exact": False}, "upper": None},
         "selection": "S2"},
    ],
    "questionnaire": {"anchors": [
        {"id": "A1", "stage": "PROBLEM", "prompt": "Tell us what happened.",
         "taps": ["hasn't happened", "can't recall"],
         "selections": [
             {"id": "S1", "prompt": "Did it?", "control": "OPTIONS", "multiSelect": False,
              "options": ["yes", "no"], "escape": ["can't recall"]},
             {"id": "S2", "prompt": "How long?", "control": "BUCKETS", "escape": ["can't recall"]},
         ]},
    ]},
    "answers": [
        {"person": "Ada Lovelace",
         "anchors": {"A1": {"text": "Last Tuesday, for about an hour.", "anchoring": "ANCHORED"}},
         "picks": {"S1": "yes", "S2": "1 h to 2 h"}},
        {"person": "Grace Hopper",
         "anchors": {"A1": {"text": "", "tap": "can't recall"}},
         "picks": {"S1": "can't recall"}},
    ],
    "expected": {"buckets": {"S2": ["under 1 h", "1 h to 2 h", "more than 2 h, say roughly"]}},
}


def _entry(raw=None, tmp_path=None):
    raw = copy.deepcopy(raw if raw is not None else CANNED)
    path = (tmp_path or __import__("pathlib").Path(".")) / f"{raw['id']}.yaml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    return cs.entry_from_file(path)[1]


@pytest.fixture
def canned(tmp_path):
    return _entry(tmp_path=tmp_path)


# ------------------------------------------------------------------------------- what comes out

def test_a_canned_entry_becomes_a_script_keyed_by_screen(canned):
    script = cs.generate(canned)
    assert set(script.screens) == {
        "PROBLEM_FRAME", "SOLUTION_FRAME", "COMMERCIAL_FRAME", "PROBLEM_ASSUMPTIONS", "INTERPRET",
        "BRIEF"}
    # Rule 6: a screen the entry cannot produce is absent, not present-and-empty -- the executor
    # refusing by name is a better failure than answering the wrong shape.
    assert "SOLUTION_ASSUMPTIONS" not in script.screens
    assert "COMMERCIAL_ASSUMPTIONS" not in script.screens


def test_the_assumptions_envelope_is_the_contract_shape(canned):
    result = cs.generate(canned).screens["PROBLEM_ASSUMPTIONS"][0]["result"]
    assert set(result) == {"assumptions", "questionnaire", "normalization_rationale"}
    assert set(result["questionnaire"]) == {"introduction", "anchors"}
    first, second = result["assumptions"]
    # V4: there is no `askedOf` on the wire. The first belief naming a role introduces it; every
    # later one reuses it by label.
    assert first["role"] == {"new": {"label": "Someone", "roleType": "PRACTITIONER",
                                     "about": "does a thing"}}
    assert second["role"] == {"reuse": "Someone"}
    assert first["founderPhrase"] == "most weeks"
    assert second["mark"] == "PROXY"
    # The null keys the corpus writes inside an expectation are dropped: the wire types them as an
    # object and a string, and an absent bound is the same claim as a null one.
    assert second["expectation"]["measure"] == {"kind": "DURATION", "unit": "hours"}
    assert "lower" in second["expectation"] and "upper" not in second["expectation"]


def test_the_questionnaire_carries_enum_taps_and_no_stage_key(canned):
    anchors = cs.generate(canned).screens["PROBLEM_ASSUMPTIONS"][0]["result"]["questionnaire"]["anchors"]
    assert anchors[0]["taps"] == ["HASNT_HAPPENED", "CANT_RECALL"]
    assert "stage" not in anchors[0]
    assert all("stage" not in s for s in anchors[0]["selections"])


def test_interpret_is_one_entry_per_reading_in_order_and_omits_a_blank_anchor(canned):
    """Rule 2, corrected by contact with the real aggregate: one entry per **reading**, in the
    entry's order -- not one per person. keel-cloud queues no reading job for somebody who wrote
    nothing at all (`05-paidly`'s Yara Haddad), and an entry for them would sit in the executor's
    cursor and hand every later person the wrong judgement."""
    interpret = cs.generate(canned).screens["INTERPRET"]
    assert len(interpret) == 1                            # Ada wrote; Grace did not
    # stage travels with anchorId (measured-beliefs decision 18, DRIFT #37): a link can carry
    # occasions from more than one approved stage, and every stage's own questionnaire numbers its
    # first occasion A1, so the pair -- not the bare id -- is what the reader hands back.
    assert interpret[0]["result"]["anchorings"] == [
        {"stage": "PROBLEM", "anchorId": "A1", "anchoring": "ANCHORED"}]
    # rule 4: only the running stack knows the real invitation id, so the generator never writes it
    assert all("invitationId" not in e["result"] for e in interpret)


def test_a_correction_re_emits_the_whole_card_plus_reply_and_changes(canned):
    correction = cs.Correction(stage="PROBLEM", belief_id="B1",
                                message="line 1 is wrong", expected_change="It happened twice.")
    result = cs.generate(canned, correction=correction).screens["PROBLEM_ASSUMPTIONS.correction"][0]["result"]
    assert set(result) >= {"assumptions", "questionnaire", "normalization_rationale",
                            "reply", "changes"}
    assert result["changes"] == [{"heading": "It happens", "before": "It happened.",
                                   "after": "It happened twice."}]
    assert result["assumptions"][0]["statement"] == "It happened twice."
    assert result["assumptions"][1]["statement"] == "It took an hour."   # nothing else moved


def test_the_typed_inputs_carry_the_market_the_statements_and_every_pick(canned):
    founder = cs.founder_inputs(canned)
    assert founder.project_name == canned.title
    assert (founder.market.country, founder.market.region) == ("GB", None)
    assert founder.market.language == "en-GB"    # recorded, never typed (V7)
    people = cs.person_inputs(canned)
    assert [p.person for p in people] == ["Ada Lovelace", "Grace Hopper"]
    assert people[0].role_id == "r1"
    assert people[0].pick("S2").values == ["1 h to 2 h"]
    assert people[0].pick("S2").is_escape is False
    assert people[1].pick("S1").is_escape is True
    assert people[1].anchors[0].tap == "CANT_RECALL"
    assert people[1].written() == []


# --------------------------------------------- Q7: a selection id belongs to its own stage alone

def test_a_selection_id_reused_on_a_different_stage_resolves_to_its_own_stage(tmp_path):
    """Measured-beliefs design decision 18, `Q7` (DRIFT #37): a selection id is unique only within
    one stage's own questionnaire and free to repeat on another's -- a live model numbers every
    stage fresh from `S1`. `by_selection` used to be built once for the whole entry, so whichever
    stage's own `S1` happened to be authored last would silently validate every other stage's pick
    against it too; `role_of_anchor` matched a bare selection id the same way. Here PROBLEM's own
    `S1` is a yes/no and SOLUTION's own `S1` -- a different role's, on a different anchor -- is a
    red/blue, and each person's pick is checked, and the script's two assumption cards and two
    reading entries stay distinct rather than merged into one."""
    raw = copy.deepcopy(CANNED)
    raw["roles"].append({"id": "r2", "label": "Someone else", "roleType": "PRACTITIONER",
                          "about": "does another thing"})
    raw["beliefs"].append({
        "id": "B3", "stage": "SOLUTION", "heading": "Which one", "statement": "It was the red one.",
        "risk": "LOAD_BEARING", "askedOf": "r2", "mark": "DIRECT",
        "expectation": {"type": "CHOICE", "options": ["red", "blue"], "expected": "red"},
        "selection": "S1"})
    raw["questionnaire"]["anchors"].append({
        "id": "A2", "stage": "SOLUTION", "prompt": "Think of that again.",
        "selections": [{"id": "S1", "prompt": "Which colour?", "control": "OPTIONS",
                         "multiSelect": False, "options": ["red", "blue"],
                         "escape": ["can't recall"]}]})
    raw["answers"] = [
        {"person": "Ada Lovelace",
         "anchors": {"A1": {"text": "Last Tuesday, for about an hour.", "anchoring": "ANCHORED"}},
         "picks": {"S1": "yes", "S2": "1 h to 2 h"}},
        {"person": "Zora Okafor",
         "anchors": {"A2": {"text": "It was red, definitely.", "anchoring": "ANCHORED"}},
         "picks": {"S1": "red"}},
    ]
    entry = _entry(raw, tmp_path)

    screens = cs.generate(entry).screens
    problem_s1 = screens["PROBLEM_ASSUMPTIONS"][0]["result"]["questionnaire"]["anchors"][0][
        "selections"][0]
    solution_s1 = screens["SOLUTION_ASSUMPTIONS"][0]["result"]["questionnaire"]["anchors"][0][
        "selections"][0]
    assert problem_s1["id"] == solution_s1["id"] == "S1"
    assert problem_s1["options"] == ["yes", "no"]
    assert solution_s1["options"] == ["red", "blue"]          # a different S1, on a different stage

    # Each pick is validated against -- and carries only the value legal for -- its own stage's S1.
    people = cs.person_inputs(entry)
    by_name = {p.person: p for p in people}
    assert by_name["Ada Lovelace"].role_id == "r1"
    assert by_name["Zora Okafor"].role_id == "r2"
    assert by_name["Ada Lovelace"].pick("S1").values == ["yes"]
    assert by_name["Zora Okafor"].pick("S1").values == ["red"]

    # Two distinct reading entries, each keyed by (stage, anchorId) -- not merged into one because
    # both happen to write under an anchor that answers to the label `S1`/`A1` conventions share.
    interpret = screens["INTERPRET"]
    assert len(interpret) == 2
    assert interpret[0]["result"]["anchorings"] == [
        {"stage": "PROBLEM", "anchorId": "A1", "anchoring": "ANCHORED"}]
    assert interpret[1]["result"]["anchorings"] == [
        {"stage": "SOLUTION", "anchorId": "A2", "anchoring": "ANCHORED"}]


# ---------------------------------------------------------------------- FR-004, the four refusals

def test_refusal_no_selection(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["beliefs"][0]["selection"] = "S99"
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.generate(_entry(raw, tmp_path))
    assert "00-canned" in str(exc.value) and "S99" in str(exc.value)


def test_refusal_unknown_pick(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["answers"][0]["picks"]["S1"] = "maybe"
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.person_inputs(_entry(raw, tmp_path))
    assert "maybe" in str(exc.value) and "Ada Lovelace" in str(exc.value)


def test_refusal_unknown_tap(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["questionnaire"]["anchors"][0]["taps"] = ["hasn't happened", "shrug"]
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.generate(_entry(raw, tmp_path))
    assert "shrug" in str(exc.value) and "TAP_ENUM" in str(exc.value)


def test_refusal_no_anchoring(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["answers"][0]["anchors"]["A1"].pop("anchoring")
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.generate(_entry(raw, tmp_path))
    assert "Ada Lovelace" in str(exc.value) and "A1" in str(exc.value)


def test_a_refusal_is_never_a_warning(tmp_path):
    """Every one of the four raises. None returns a partial script with a note attached -- a
    generator that guesses is a golden set that has stopped being golden."""
    assert issubclass(cs.CorpusScriptError, Exception)


# ---------------------------------------------------------------------------------- the drift fold

@pytest.mark.parametrize("corpus_drift,wire_drift,expected", [
    ("none", "NONE", True), ("below", "BELOW", True), ("above", "ABOVE", True),
    ("both", "BOTH", True), ("BOTH", "both", True),
    ("none", "BELOW", False), ("below", "none", False),
    (None, "NONE", False),          # an absent drift and a NONE drift are different claims
    ("none", None, False), (None, None, False),
])
def test_drift_equal(corpus_drift, wire_drift, expected):
    assert cs.drift_equal(corpus_drift, wire_drift) is expected


# ------------------------------------------------------- the real entries: provenance and the cap

def _corpus_entries():
    config = load_config(validate=False)
    corpus = corpus_reader.load(config.keel_cloud)
    return [corpus.by_id(entry_id) for entry_id in CHOSEN]


def _all_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_strings(item)


def _entry_strings(entry):
    raw = yaml.safe_load(entry.path.read_text(encoding="utf-8"))
    out = set()
    for text in _all_strings(raw):
        out.add(text)
        out.add(" ".join(text.split()))     # the folded form of a YAML block scalar
    return out


@pytest.mark.parametrize("entry_id", CHOSEN + ("payroll-exceptions",))
def test_every_literal_in_the_script_came_from_the_entry(entry_id):
    """Contract rule 1, and the spec's own acceptance scenario 7 -- asserted before a stack is
    ever booted. The only strings a script may carry that the entry does not are the six screen
    keys, the outcome words, the `_` metadata keys, the enum tap names, and the two required
    strings rule 5 names."""
    if entry_id == "payroll-exceptions":
        from evals import payroll_exceptions as fx
        entry = fx.entry()
    else:
        entry = next(e for e in _corpus_entries() if e.id == entry_id)
    script = cs.generate(entry)
    allowed = _entry_strings(entry)
    allowed |= set(script.screens)                                   # screen keys
    allowed |= {"COMPLETED", "outcome", "result"}
    allowed |= {"assumptions", "questionnaire", "introduction", "anchors",
                 "normalization_rationale", "heading", "statement", "risk", "mark",
                 "expectation", "selection", "role", "new", "reuse", "founderPhrase",
                 "label", "roleType", "about", "market", "id", "prompt", "control",
                 "multiSelect", "options", "escape", "other", "taps", "type", "measure",
                 "kind", "unit", "per", "lower", "upper", "value", "inclusive", "exact",
                 "expected", "anchorings", "stage", "anchorId", "anchoring", "unprompted", "flags",
                 "whatThisSays"}
    allowed |= set(cs.TAP_ENUM.values())                             # the enum tap names
    # Rule 5's required strings: the three the wire demands and the entry does not carry. The
    # BRIEF paragraph joins the other two here for the same reason -- it is composed, from the
    # entry's own `expected.stages` and nothing else, and `test_the_brief_paragraph_says_only_
    # what_the_entry_says` below is what holds it to that.
    allowed |= {cs.introduction_for(entry), cs.normalization_rationale_for(entry),
                cs.what_this_says_for(entry)}

    strays = sorted({s for s in _all_strings(script.screens) if s not in allowed})
    assert not strays, f"{entry_id}: the script carries values the entry does not: {strays}"


@pytest.mark.parametrize("entry_id", CHOSEN)
def test_no_stage_exceeds_the_wires_maxitems_of_eight(entry_id):
    """V4: `assumptions` and `questionnaire.anchors` are each `maxItems: 8`. `01-countly`'s
    PROBLEM is exactly eight beliefs and one anchor -- at the cap, not over it, which is a fact
    worth a test rather than a coincidence to discover mid-run."""
    entry = next(e for e in _corpus_entries() if e.id == entry_id)
    for stage in cs.STAGES:
        assert len(entry.beliefs_for(stage)) <= cs.MAX_ITEMS
        assert len(entry.anchors_for(stage)) <= cs.MAX_ITEMS


def test_countlys_problem_stage_sits_exactly_on_the_cap():
    entry = next(e for e in _corpus_entries() if e.id == "01-countly")
    assert len(entry.beliefs_for("PROBLEM")) == cs.MAX_ITEMS
    assert len(entry.anchors_for("PROBLEM")) == 1


def test_the_shared_selection_is_one_selection_named_twice():
    """Acceptance 3a's own precondition: countly's `P4a` and `P4b` both name `S4`, which is the
    corpus's only exercise of rule Q4 anywhere. `group` never goes on the wire -- they simply
    both name the same selection, which is how a shared pick list happens at all."""
    entry = next(e for e in _corpus_entries() if e.id == "01-countly")
    assumptions = cs.generate(entry).screens["PROBLEM_ASSUMPTIONS"][0]["result"]["assumptions"]
    shared = [a for a in assumptions if a["selection"] == "S4"]
    assert len(shared) == 2
    assert all("group" not in a for a in shared)


@pytest.mark.parametrize("entry_id", CHOSEN)
def test_the_script_serialises_with_its_provenance(entry_id):
    entry = next(e for e in _corpus_entries() if e.id == entry_id)
    body = json.loads(json.dumps(cs.generate(entry).to_json()))
    assert body["_entry_id"] == entry_id
    assert body["_entry_sha256"] == entry.sha256
    assert body["_source"].endswith(entry.path.name)
    assert body["_generated_by"] == "harness/corpus_script.py"


# --------------------------------------------------- a role is new once, on the stage it appears

def test_a_role_is_introduced_once_across_the_whole_entry(tmp_path):
    """Live-confirmed the hard way (`runs/20260907T142617Z-s001-smoke`): a role introduced on
    PROBLEM already exists on the project by the time the SOLUTION screen answers, and keel-cloud
    refuses a second `role.new` with the same label **by name** --

        result.assumptions[0].role.new.label: a role labeled 'A payroll manager' already exists

    keel-runtime's own bundled-script generator never met this because it writes one stage and
    stops. This one writes three, so `role.new` is scoped to the entry, not the stage."""
    raw = copy.deepcopy(CANNED)
    raw["beliefs"].append({
        "id": "B3", "stage": "SOLUTION", "heading": "Still them", "statement": "They did it again.",
        "risk": "SUPPORTING", "askedOf": "r1", "mark": "DIRECT",
        "expectation": {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"},
        "selection": "S3"})
    raw["questionnaire"]["anchors"].append({
        "id": "A2", "stage": "SOLUTION", "prompt": "And then?",
        "selections": [{"id": "S3", "prompt": "Again?", "control": "OPTIONS",
                         "multiSelect": False, "options": ["yes", "no"], "escape": ["can't recall"]}]})
    entry = _entry(raw, tmp_path)
    screens = cs.generate(entry).screens
    assert screens["PROBLEM_ASSUMPTIONS"][0]["result"]["assumptions"][0]["role"] == {
        "new": {"label": "Someone", "roleType": "PRACTITIONER", "about": "does a thing"}}
    assert screens["SOLUTION_ASSUMPTIONS"][0]["result"]["assumptions"][0]["role"] == {
        "reuse": "Someone"}


@pytest.mark.parametrize("entry_id", CHOSEN)
def test_no_role_is_introduced_twice_in_any_chosen_entry(entry_id):
    entry = next(e for e in _corpus_entries() if e.id == entry_id)
    screens = cs.generate(entry).screens
    introduced: list[str] = []
    for stage in cs.STAGES:
        key = cs.ASSUMPTIONS_SCREEN[stage]
        for assumption in screens.get(key, [{}])[0].get("result", {}).get("assumptions", []):
            new = assumption["role"].get("new")
            if new:
                introduced.append(new["label"])
    assert len(introduced) == len(set(introduced)), (
        f"{entry_id} introduces a role twice: {introduced}")
    assert len(introduced) == len(entry.roles), (
        f"{entry_id} has {len(entry.roles)} roles and introduces {introduced}")


# ------------------------------------------------------------------- BRIEF, and *What this says*
#
# keel-cloud starts a `BRIEF` job of its own every time a reading batch finishes
# (`ReadingBatchService.sayWhatThisSays`), and the one field it comes back with is what the
# overview renders under *What this says*. A script with no `BRIEF` entry does not skip that job,
# it fails it -- `ScriptedExecutor` refusing by name, the exception swallowed by
# `sayWhatThisSays`'s own catch, and the founder left reading `whatThisSaysNote` forever. Six
# green scripted runs said nothing about the paragraph because no scripted run had ever produced
# one; these are the tests that keep it produced.

BRIEF_MAX = 1200                    # `ScreenResponseContracts.RATIONALE_OR_NOTE_MAX`, restated
                                    # here so a drift in the module's own constant is a red test


def test_every_entry_carries_a_brief_entry_of_the_contract_shape(canned):
    for entry in list(_corpus_entries()) + [canned, __import__(
            "evals.payroll_exceptions", fromlist=["entry"]).entry()]:
        brief = cs.generate(entry).screens["BRIEF"]
        assert len(brief) == 1, f"{entry.id}: one entry is enough -- the cursor repeats the last"
        assert brief[0]["outcome"] == "COMPLETED"
        # The whole contract: one field, and nothing else on the result.
        assert set(brief[0]["result"]) == {"whatThisSays"}


@pytest.mark.parametrize("entry_id", CHOSEN + ("payroll-exceptions",))
def test_the_brief_paragraph_satisfies_keel_clouds_own_result_schema(entry_id):
    """`{"whatThisSays": string}`, non-blank, <= 1200 code points, and no link anywhere in it
    (`ScreenResponseContracts.briefSchema`, `NO_LINK_PATTERN`, `ScreenResultApplier.briefCommand`).
    A paragraph that fails any of these is a `RESULT_INVALID` on the wire, mid-run, with the
    failure swallowed -- so it is checked here instead."""
    if entry_id == "payroll-exceptions":
        from evals import payroll_exceptions as fx
        entry = fx.entry()
    else:
        entry = next(e for e in _corpus_entries() if e.id == entry_id)
    paragraph = cs.generate(entry).screens["BRIEF"][0]["result"]["whatThisSays"]
    assert isinstance(paragraph, str) and paragraph.strip()
    assert len(paragraph) <= BRIEF_MAX
    assert not cs.NO_LINK.search(paragraph), paragraph


def test_the_brief_paragraph_is_marked_scripted_and_says_one_sentence_a_stage(canned):
    """It names the entry, says the referee wrote it, and then says one thing per stage. A reader
    of a bundle must never mistake this for a model's judgement."""
    paragraph = cs.generate(canned).screens["BRIEF"][0]["result"]["whatThisSays"]
    assert paragraph.startswith("Scripted by the referee from corpus entry 00-canned,")
    assert "not written by a model" in paragraph
    for claim in cs.STAGE_CLAIM.values():
        assert paragraph.count(claim) == 1, f"{claim} should be said once: {paragraph!r}"


def test_the_brief_paragraph_reads_the_entrys_own_stage_verdicts(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["expected"]["stages"] = {"PROBLEM": "CONTRADICTED", "SOLUTION": "MIXED",
                                 "COMMERCIAL": "SUPPORTED"}
    paragraph = cs.what_this_says_for(_entry(raw, tmp_path))
    assert "The problem claim is not holding up." in paragraph
    assert "The solution claim has people disagreeing." in paragraph
    assert "The commercial claim is holding up." in paragraph


def test_a_stage_the_entry_judges_not_is_said_to_be_unjudged_rather_than_invented(canned):
    """`CANNED` (and this repo's own `payroll_exceptions.yaml`) judge no stage. Saying *not
    tested* there would be the generator writing a verdict the entry never wrote."""
    paragraph = cs.what_this_says_for(canned)
    assert paragraph.count("carries no verdict in this entry.") == 3
    for word in cs.VERDICT_SENTENCE.values():
        assert word not in paragraph


def test_a_verdict_the_four_do_not_carry_is_refused_by_name(tmp_path):
    raw = copy.deepcopy(CANNED)
    raw["expected"]["stages"] = {"PROBLEM": "PROBABLY_FINE"}
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.what_this_says_for(_entry(raw, tmp_path))
    assert "PROBABLY_FINE" in str(exc.value) and "00-canned" in str(exc.value)


def test_a_paragraph_over_the_wires_cap_is_refused_rather_than_sent(tmp_path, monkeypatch):
    raw = copy.deepcopy(CANNED)
    raw["id"] = "00-canned"
    entry = _entry(raw, tmp_path)
    monkeypatch.setattr(cs, "WHAT_THIS_SAYS_MAX", 20)
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.what_this_says_for(entry)
    assert "caps it at 20" in str(exc.value)


def test_a_paragraph_carrying_a_link_is_refused_rather_than_sent(tmp_path, monkeypatch):
    entry = _entry(tmp_path=tmp_path)
    monkeypatch.setitem(cs.STAGE_CLAIM, "PROBLEM", "See https://example.test the problem claim")
    with pytest.raises(cs.CorpusScriptError) as exc:
        cs.what_this_says_for(entry)
    assert "carries a link" in str(exc.value)


def test_brief_is_the_screen_name_keel_clouds_own_context_keys_export_uses():
    """The executor infers the screen from the context key set, so the script's key must be
    keel-cloud's own name for it -- read from keel-runtime's bundled copy of that export rather
    than trusted (#33's lesson)."""
    config = load_config(validate=False)
    table = json.loads((config.keel_runtime / "keel_runtime" / "testing" / "contracts"
                        / "context-keys.json").read_text(encoding="utf-8"))
    assert cs.BRIEF_SCREEN in table
    assert sorted(table[cs.BRIEF_SCREEN]) == ["claims", "market", "project_name"]
