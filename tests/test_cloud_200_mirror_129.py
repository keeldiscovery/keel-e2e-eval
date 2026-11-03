"""Spec 129 -- the harness follows keel-cloud 200 (the follow-up refers back in the people's words).

keel-cloud 200 gives the rows a follow-up refers back to a hidden short name (two to five words in the persona's own
words, written with the row, never shown to the founder) and says it in the row's place. Here: the named wordings held
to the registry export (`interviewer_fake.NAMED` / `ALSO_NAMED`), Importance's count of picks and its count-free clip;
`ShortName.fault` restated (`harness/short_names.fault`) on keel-cloud's own Palus fixtures; the scripted writer's short
names (`short_names.compose`) and the face-less ASKED job on the founder's typed Importance rows; today's wording where
a row has none (a project confirmed before 200, a back-test's model-written names); the ASKED schema; L29 and K9 by
name; and the readers' one line on a follow-up screen (RUBRIC_VERSION 4).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from evals import backtest as bt
from harness import interviewer_fake as fake
from harness import short_names as sn
from harness import vectors_script as vs
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from quality import readers, rubric
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    return path.read_text(encoding="utf-8")


def _registry() -> dict:
    registry = json.loads(_cloud("src/main/resources/keel/dimension-registry.json"))
    if not any((e.get("follow_up") or {}).get("named") for e in registry["dimensions"]):
        pytest.skip("keel-cloud predates spec 200 (no follow_up.named)")
    return registry


@pytest.fixture(scope="module")
def golden():
    try:
        registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    except Exception as missing:  # noqa: BLE001 - a checkout without the registry of record skips
        pytest.skip(f"no keel-cloud registry of record: {missing}")
    return {e.id: e for e in corpus_mod.load(KEEL_CLOUD, registry=registry).entries}


# ------------------------------------------------------------------------------- FR-3: the named wordings, held

def test_the_named_wordings_are_the_registrys_own():
    registry = _registry()
    named = {e["key"]: {k: v for k, v in e["follow_up"]["named"].items() if not k.startswith("_")}
             for e in registry["dimensions"] if (e.get("follow_up") or {}).get("named")}
    also = {e["key"]: {k: v for k, v in e["follow_up"]["also"]["named"].items() if not k.startswith("_")}
            for e in registry["dimensions"] if ((e.get("follow_up") or {}).get("also") or {}).get("named")}
    assert named == fake.NAMED
    assert also == fake.ALSO_NAMED
    composer = _cloud(APPLICATION + "FollowUpComposer.java")
    assert 'Map.entry("{short_name}", "that"), Map.entry("{smaller_name}", "that first step")' in composer
    assert fake.FILL_DEFAULTS["{short_name}"] == "that" and fake.FILL_DEFAULTS["{smaller_name}"] == "that first step"


def test_importance_counts_the_picks_in_its_text_and_never_in_its_clip():
    block = fake.NAMED["problem.importance"]
    assert "the one you picked" in fake.named_text(block, fake.picks_counted("problem.importance", ["rival_1"]))
    assert "the ones you picked" in fake.named_text(block, fake.picks_counted("problem.importance",
                                                                              ["rival_1", "rival_2"]))
    assert fake.named_text(block, fake.picks_counted("problem.importance", ["rival_1", fake.NOTHING_ELSE_CODE])) \
        == block["one"], "Nothing else is never a pick"
    assert fake.named_text(block, 0) == block["text"] == block["spoken"], "None of these: the count-free wording"
    values = {"{short_name}": "matching deliveries"}
    assert fake.spoken_filled("problem.importance", values) == (
        "You did not pick matching deliveries. What made you choose differently?"), "the clip never counts"


def test_a_row_with_no_short_name_reads_todays_wording():
    assert fake.named_of("problem.importance", {"{short_name}": None}) is None
    assert fake.spoken_filled("problem.importance", {"{founder_item}": "matching deliveries"}) == fake.LADDER[0][3] \
        .replace("{founder_item}", "matching deliveries")
    assert fake.named_of("commercial.commitment", {"{short_name}": "starting a trial"}, also=True) is None, \
        "the second stem says the smaller step's own name"
    assert fake.named_of("commercial.commitment", {"{smaller_name}": "short call with us"}, also=True) is not None


# --------------------------------------------------------------------------- FR-4: ShortName.fault, restated

PALUS_ROWS = ["Leaving cash earning little after fees", "Making the raise last as long as possible",
              "Keeping cash safe above the insured limit", "Getting cash back fast when needed",
              "Moving money between accounts without mistakes"]
PALUS_NAMES = ["low yield on your cash", "making the raise last", "cash above the insured limit",
               "getting cash back fast", "moving money between accounts"]
PALUS_WORDS = ("startup finance leads; keep the raise safe and earning until the company spends it; Startups park their "
               "raise in a bank account, where the cash sits at a low yield after fees; they park untouched cash in the "
               "bank's treasury money market fund")
PALUS_IDEA = ["Palus", "a treasury account that moves idle cash"]


def test_short_name_fault_is_keel_clouds_on_its_own_fixtures():
    for row, name in zip(PALUS_ROWS, PALUS_NAMES):
        assert sn.fault("L29", name, row, PALUS_WORDS, PALUS_IDEA) is None, name
    assert sn.fault("K9", "getting your phone online", "Their phone was with them and online",
                    "deaf or hard-of-hearing adults; get the phone online", ["AirCaps"]) is None
    row = PALUS_ROWS[0]
    assert "6 words" in sn.fault("L29", "low yield on all your cash", row, PALUS_WORDS, PALUS_IDEA)
    assert "1 words" in sn.fault("L29", "cash", row, PALUS_WORDS, PALUS_IDEA)
    assert "the idea's name, 'Palus'" in sn.fault("L29", "Palus for your cash", row, PALUS_WORDS, PALUS_IDEA)
    assert "never a pronoun" in sn.fault("L29", "leaving it earning little", row, PALUS_WORDS, PALUS_IDEA)
    assert "the row repeated" in sn.fault("L29", "getting cash back, fast.", "Getting cash back fast", PALUS_WORDS,
                                          PALUS_IDEA)
    assert "says 'dimension'" in sn.fault("L29", "the low yield dimension", row, PALUS_WORDS, PALUS_IDEA)
    assert "'app', a product word" in sn.fault("L29", "the cash app", row, PALUS_WORDS, PALUS_IDEA)
    assert "a claim word" in sn.fault("L29", "faster cash back", PALUS_ROWS[3], PALUS_WORDS, PALUS_IDEA)
    assert sn.fault("L29", "the payroll app", "Checking the payroll app", "payroll practitioners; run payroll in the "
                                                                          "app") is None
    assert sn.fault("L29", "payroll errors", "Fixing mistakes", "payroll practitioners; run payroll without errors") \
        is None
    source = _cloud(VECTORS + "ShortName.java")
    assert "MIN_WORDS = 2;" in source and "MAX_WORDS = 5;" in source
    for word in sn.PRONOUNS:
        assert f'"{word}"' in source, word
    assert "SHORT_NAME_MAX = 60;" in _cloud(APPLICATION + "ScreenResponseContracts.java")


# ----------------------------------------------------------------------- FR-1: the scripted writer, the fakes

def test_the_scripted_writer_cuts_the_row_down_in_its_own_words():
    assert sn.compose("Matching deliveries against their invoices") == "matching deliveries"
    assert sn.compose("Filling gaps in the staff schedule") == "filling gaps"
    assert sn.compose("Scan each delivery on arrival", gerund=vs.gerund) == "scanning each delivery on arrival"
    assert sn.compose("start a read-only trial", gerund=vs.gerund) == "starting a read-only trial"
    assert sn.compose("Knowing what the cry means") is None, "five words, no cut: the row reads today's wording"
    assert sn.compose("Their phone was within reach of the cot") is None, "a clause, not a noun or -ing phrase"
    assert sn.compose("install the app", gerund=vs.gerund) is None, "a product word"
    for row in PALUS_ROWS:
        name = sn.compose(row)
        assert name is None or sn.fault("L29", name, row) is None, row


def test_the_drafts_carry_the_short_names_and_the_typed_rows_are_named_by_the_asked_job(golden):
    countly = golden["01-countly"]
    draft = vs.drafted_list(countly, "problem.importance")
    assert [i.get("short_name") for i in draft["items"]] == ["matching deliveries", "filling gaps"]
    assert vs.importance_first_draft(countly)["items"] == [{"label": "Matching deliveries against their invoices",
                                                            "short_name": "matching deliveries"}]
    asked = vs.importance_asked_result(countly)
    labels = [i["label"] for i in vs.founder_list(countly, "problem.importance")["items"]]
    assert [labels[i["index"]] for i in asked["items"]] == vs.importance_typed(countly)
    assert all(set(i) == {"index", "short_name"} for i in asked["items"]), "face-less: the short name alone"
    script = vs.generate(countly)
    assert script.screens[vs.ASKED_SCREEN][0] == {"outcome": "COMPLETED", "result": asked}, \
        "the problem stage's Save runs the first ASKED job"
    adoption = vs.drafted_list(countly, "solution.adoption_friction")
    assert all(i.get("short_name") and i.get("asked") for i in adoption["items"])


def test_a_typed_row_the_writer_cannot_name_leaves_the_whole_list_unnamed(golden):
    paidly = golden["05-paidly"]
    if any(sn.compose(label) is None for label in vs.importance_typed(paidly)):
        assert vs.row_short_names(paidly, "problem.importance") == {}
        assert vs.importance_asked_result(paidly) is None
        assert all("short_name" not in i for i in vs.drafted_list(paidly, "problem.importance")["items"])


def test_a_back_test_entry_names_nothing_its_model_does():
    class Backtest:
        id = "10-palus"
        backtest = True
    assert vs.row_short_names(Backtest(), "problem.importance") == {}
    assert vs.list_short_name(Backtest(), "solution.relative_advantage") is None


def test_the_follow_up_says_the_short_name_in_the_rows_place(golden):
    countly = golden["01-countly"]
    values = vs.lock_values(countly, {"occasion": "delivery"}, "problem.importance", "matching deliveries against their "
                                                                                     "invoices")
    assert values["{short_name}"] == "matching deliveries"
    assert vs.follow_up_clip(countly, {"occasion": "delivery"}, "problem.importance") == (
        "You did not pick matching deliveries. What made you choose differently?")
    effort = vs.lock_values(countly, {}, "solution.adoption_friction")["{short_name}"]
    assert effort == vs.tested_short_name(countly, "solution.adoption_friction")
    assert vs.follow_up_clip(countly, {}, "solution.adoption_friction") == f"What makes {effort} too much trouble for you?"


def test_a_served_named_wording_is_the_products_on_a_back_test():
    values = {"{occasion}": "night", "{solution_name}": "Lullaby"}
    pattern = fake.named_pattern("problem.importance", values)
    assert pattern.match("You did not pick knowing what a cry means. What made the one you picked more pressing for "
                         "you?")
    assert not pattern.match("You did not pick it. What made you choose differently?"), "one word is no short name"
    advantage = fake.named_pattern("solution.relative_advantage", values)
    assert advantage.match("You said Lullaby wouldn't make much difference on your last night. What would make "
                           "settling the baby better for you, if anything?")


# ---------------------------------------------------------------------------- the ASKED schema, the rule names

def test_the_asked_schema_requires_the_index_alone_and_takes_a_short_name():
    contracts = _cloud(APPLICATION + "ScreenResponseContracts.java")
    assert 'Map<String, Object> item = object(List.of("index"), properties);' in contracts
    assert 'properties.put("short_name", described(SHORT_NAME_MAX, ROW_SHORT_NAME_RULE));' in contracts
    assert "ASKED_MAX_ITEMS = com.keeldiscovery.cloud.domain.vectors.DimensionRegistry.MAX_FIXED_ANSWERS;" in contracts
    assert "public static final int CONTRACT_VERSION = 25;" in contracts, "200 moved no contract"


def test_l29_and_k9_are_reported_by_name():
    assert '"K9: write this row\'s short name' in _cloud(APPLICATION + "AskedRules.java")
    assert "L29" in _cloud(APPLICATION + "ScreenResultApplier.java")
    rows = [{"screen": "CALIBRATION_QUESTIONS", "detail": "breach result.questions[0].list.items[0].short_name: L29: "
                                                          "'low yield on all your cash' is 6 words"},
            {"screen": "ASKED", "turns": [{"content": "K9: write this row's short name -- two to five words"}]}]
    assert [n["rule"] for n in bt.lock_notes(None, rows)] == ["L29", "K9"]


# ----------------------------------------------------------------- the readers' one line (RUBRIC_VERSION 4)

def test_the_readers_one_line_is_handed_on_a_follow_up_screen_alone():
    line = rubric.prompt_follow_up()
    assert "\n" not in line and "reference back" in line and "as you would say it" in line
    assert rubric.RUBRIC_VERSION == 5 == rubric.file_version()
    versions = rubric.rubric_text().split("## Versions", 1)[1].split("- **3**", 1)[0]
    assert "- **4** (spec 129" in versions and "Version-3 files are set aside" in versions
    assert line not in rubric.prompt_rubric() and line not in rubric.prompt_spoken(), "never on another screen"
    source = Path(readers.__file__).read_text(encoding="utf-8")
    assert re.search(r"rubric\.prompt_follow_up\(\) if screen\.kind == rubric\.FOLLOW_UP_KIND", source)
    assert rubric.FOLLOW_UP_KIND == "follow_up"
