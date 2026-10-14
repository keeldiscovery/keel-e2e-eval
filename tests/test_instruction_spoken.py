"""The spoken-form marks and the cloud corpus they read (spec 040 FR-005; `spoken-questions-guidelines.md` §2-§5, §8;
keel-cloud 088 FR-001 / FR-003 / FR-005; judgement calls 79-81).

Each of `S1`-`S10` and `K2`-`K6` fails once for its own reason on a hand-built item and passes on the good one, and the
real record -- keel-cloud's `build/spoken-corpus.txt` over corpus revision 10 -- keeps every rule but the five corpus
items call 81 names, which are found, reported and kept out of the denominator. Stackless and modelless: the real
record is read from the keel-cloud checkout `stack.toml` names (skipped by name when its corpus test has not run).
"""

from __future__ import annotations

import dataclasses

import pytest

from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import spoken as spoken_mod
from tests import v9_fixtures as fx

ComposedItem = cloud_mod.ComposedItem


def _item(**kw) -> ComposedItem:
    """A Compatibility item that keeps every rule -- the green half every red half mutates by one thing."""
    base = dict(entry="09-fixture", key="solution.compatibility", part=2,
                question="On your last morning, did you have your phone to hand?",
                options=("Yes, easily", "Yes, with some steps", "Only with help or approval", "No"),
                escape="I can't tell", anchor=None, stem="On your last morning, did you have your phone to hand?",
                count_line="I'll read four options.",
                options_line="Yes, easily; yes, with some steps; only with help or approval; or no.",
                escape_line="Or say you can't tell.", transform="none")
    base.update(kw)
    return ComposedItem(**base)


def _rules(item) -> list:
    return [f.split(":")[0] for f in spoken_mod.item_faults(item)]


def test_a_good_item_keeps_every_rule():
    assert spoken_mod.item_faults(_item()) == []


def test_the_template_turns_the_first_person_when_it_is_said():
    """088 call 5: "No, I decided on my own" is said "no, you decided on your own"; a semicolon is said as a comma."""
    buyer = _item(key="commercial.buyer_payer_alignment", part=3,
                  question="Did anyone else have to agree before you paid for it?",
                  stem="Did anyone else have to agree before you paid for it?",
                  options=("Yes, they had to agree", "No, I decided on my own", "No, someone else had to agree",
                           "Someone else decided, not me"), escape="I can't recall one",
                  options_line="Yes, they had to agree; no, you decided on your own; no, someone else had to "
                               "agree; or someone else decided, not you.",
                  escape_line="Or say you can't recall one.")
    assert spoken_mod.item_faults(buyer) == []
    assert spoken_mod.said("Nothing worked; the baby settled alone") == "nothing worked, the baby settled alone"
    assert spoken_mod.said("The US office, my team") == "the us office, your team"


@pytest.mark.parametrize("change, rule", [
    (dict(stem=" ".join(["word"] * 20) + " too?", question=" ".join(["word"] * 20) + " too?"), "S1"),
    (dict(stem="On your last morning, you had your phone.", question="On your last morning, you had your phone."),
     "S1"),
    (dict(question="Something else entirely?"), "S2"),
    (dict(options=("Yes, easily", "Yes, with some steps", "Only with help", "Only with approval", "Mostly",
                   "No")), "S3"),
    (dict(options=("Yes, easily", "Yes, with some steps", "Only with help or approval from the office manager "
                   "first", "No")), "S4"),
    (dict(options=("Yes, easily.", "Yes, with some steps", "Only with help or approval", "No")), "S5"),
    (dict(options=("Yes, easily", "Yes easily", "Only with help or approval", "No")), "S5"),
    (dict(escape="I'd rather not say", escape_line="Or say you'd rather not say."), "S6"),
    (dict(escape_line="Or say nothing at all."), "S6"),
    (dict(escape_line=None), "S6"),
    (dict(count_line="I'll read five options."), "S7"),
    (dict(count_line="I'll read four options; pick two."), "S7"),
    (dict(options_line="Yes, easily; only with help or approval; yes, with some steps; or no."), "S8"),
    (dict(options_line="Yes, easily, yes, with some steps, only with help or approval, or no."), "S8"),
    (dict(transform="two_steps"), "S9"),
])
def test_each_spoken_rule_fails_once_for_its_own_reason(change, rule):
    """A change to the options is also a change to what is said, so S7 / S8 may follow it; nothing else may."""
    rules = _rules(_item(**change))
    assert rule in rules, rules
    allowed = {rule} | ({"S7", "S8"} if "options" in change else set())
    assert set(rules) <= allowed, rules


def test_the_two_unchanged_frames_are_held_at_twenty_five_until_the_founder_decides():
    """Call 79 (keel-cloud 088 call 12): Existing sacrifice and Relative advantage run to 25 words; every other stem
    20."""
    stem = ("Thinking of your last busy morning, would a tag that beeps back have made things better for you, or not, "
            "today?")
    assert 20 < len(stem.split()) <= 25
    benefit = _item(key="solution.relative_advantage", question=stem, stem=stem,
                    options=("It would have made things better", "No difference", "It would have made things worse"),
                    count_line="I'll read three options.",
                    options_line="It would have made things better; no difference; or it would have made things "
                                 "worse.", transform="yes_no_per_benefit")
    assert spoken_mod.item_faults(benefit) == []
    assert _rules(dataclasses.replace(benefit, key="solution.compatibility", transform="none")) == ["S1"]
    assert spoken_mod.stem_limit("commercial.existing_sacrifice") == 25 and spoken_mod.stem_limit(
        "problem.importance") == 20


def test_importance_picks_two_and_is_read_one_then_one_more():
    labels = ("Getting through the morning traffic", "Finding the keys on the way out", "Riding in wet weather",
              "Fixing a flat tyre on the way", "Finding somewhere safe to park")
    stem = "Thinking about that last morning, which two of these would you most like made easier?"
    importance = _item(key="problem.importance", part=1, question=stem, stem=stem, options=labels,
                       escape="None of these", count_line="I'll read five options; pick two.",
                       options_line="Getting through the morning traffic; finding the keys on the way out; riding "
                                    "in wet weather; fixing a flat tyre on the way; or finding somewhere safe to park.",
                       escape_line="Or say none of these.", transform="one_then_one_more")
    assert spoken_mod.item_faults(importance) == []
    assert _rules(dataclasses.replace(importance, count_line="I'll read five options.")) == ["S7"]
    assert _rules(dataclasses.replace(importance, transform="none")) == ["S9"]
    short = labels[:4] + ("Parking",)
    assert "S4" in _rules(dataclasses.replace(
        importance, options=short, options_line=importance.options_line.replace(
            "finding somewhere safe to park", "parking"))), "call 80: a founder's option is at least three words"


def test_price_is_read_in_two_steps_and_may_offer_six():
    options = ("Under £1", "£1 to £2", "£2 to £5", "£5 to £10", "Over £10", "I wouldn't pay for this")
    stem = "What would a fix for lost keys be worth to you a month?"
    price = _item(key="commercial.price", part=3, question=stem, stem=stem, options=options, escape="I can't say",
                  count_line="I'll read four options.",
                  options_line="Under £2; £2 to £5; over £5; or you wouldn't pay for this.",
                  escape_line="Or say you can't say.", transform="two_steps")
    assert spoken_mod.item_faults(price) == []
    assert _rules(dataclasses.replace(price, options_line="Under £1; £1 to £2; over £2; or you wouldn't pay for "
                                                          "this.")) == ["S8"]


def test_a_number_has_no_options_and_no_count_line():
    stem = "On how many of those 7 nights did that happen?"
    frequency = _item(key="problem.frequency", part=1, question=stem, stem=stem, options=(),
                      escape="I can't recall", count_line=None, options_line="A number from 0 to 7.",
                      escape_line="Or say you can't recall.")
    assert spoken_mod.item_faults(frequency) == []
    assert _rules(dataclasses.replace(frequency, count_line="I'll read eight options.")) == ["S7"]
    assert _rules(dataclasses.replace(frequency, options=("0", "1"))) == ["S3"]


def test_commitment_has_no_escape_and_says_its_step_once():
    stem = "If it were ready today, would you install the app, or not?"
    commitment = _item(key="commercial.commitment", part=3, question=stem, stem=stem,
                       options=("Yes, I'd start one", "Yes, after trying it first", "Probably not", "No"),
                       escape=None, options_line="Yes, you'd start one; yes, after trying it first; probably not; "
                                                 "or no.", escape_line=None)
    assert spoken_mod.item_faults(commitment) == []
    doubled = "If it were ready today, would you introduce you to the IT supplier, or not?"
    assert _rules(dataclasses.replace(commitment, stem=doubled, question=doubled)) == ["S10"]
    assert _rules(dataclasses.replace(commitment, escape="I can't tell", escape_line="Or say you can't tell.")) \
        == ["S6"]


def test_the_anchor_is_split_off_and_set_once_a_part():
    item = _item(key="problem.current_solution_satisfaction", part=1,
                 question="Think of the last morning. How well did your way of finding them work?",
                 anchor="Think of the last morning.", stem="How well did your way of finding them work?",
                 options=("Found them straight away", "Found them after a quick look", "It took a full search",
                          "Found them only after being late", "Never found them that morning"),
                 escape="Someone else does the checking", count_line="I'll read five options.",
                 options_line="Found them straight away; found them after a quick look; it took a full search; found "
                              "them only after being late; or never found them that morning.",
                 escape_line="Or say someone else does the checking.")
    assert spoken_mod.item_faults(item) == []
    assert _rules(dataclasses.replace(item, anchor=None)) == ["S2"]


# ------------------------------------------------------------------------ the asked faces (K2-K6)

@pytest.mark.parametrize("asked, label, key, rule", [
    ("did you have your phone to hand", "They had a phone to hand", "solution.compatibility", None),
    ("you'd upload your last 12 months of pay registers, once", "Upload 12 months of registers",
     "solution.adoption_friction", None),
    ("did the phone sit within reach", "Phone in reach", "solution.compatibility", "K3"),
    ("did you have your 2 phones", "They had a phone", "solution.compatibility", "K4"),
    ("did you have your phone to hand?", "They had a phone", "solution.compatibility", "K6"),
    (" ".join(["you"] * 21), "x", "solution.compatibility", "K2"),
    ("you'd clip a small tag to your key ring once and then whistle for it each day", "Clip a tag",
     "solution.adoption_friction", "K2"),
    ("", "x", "solution.compatibility", "K2"),
])
def test_each_face_rule_fails_once_for_its_own_reason(asked, label, key, rule):
    faults = spoken_mod.face_faults(asked, label, key, "morning")
    assert {f.split(":")[0] for f in faults} == ({rule} if rule else set()), faults


def test_k5_reads_a_product_word_on_a_part_one_item_only():
    assert spoken_mod.face_faults("did you open an app", "x", "solution.compatibility", "night", part=1)[0] \
        .startswith("K5:")
    assert spoken_mod.face_faults("did you open an app", "x", "solution.compatibility", "night", part=2) == []


def test_a_face_is_framed_as_design_5_1_frames_it():
    assert spoken_mod.framed("solution.compatibility", "delivery", "could you scan it?") == \
        "On your last delivery, could you scan it?"
    assert spoken_mod.framed("solution.adoption_friction", None, "you'd scan it.") == \
        "You'd scan it. Would you do that, or not?"


# ------------------------------------------------------------------------ the cloud corpus parser

def test_split_options_keeps_a_label_with_a_comma_whole_when_it_is_known():
    known = ["Yes, easily", "Yes, with some steps", "Only with help or approval", "No"]
    inner = "Yes, easily, Yes, with some steps, Only with help or approval, No"
    assert cloud_mod.split_options(inner, known) == known
    assert cloud_mod.split_options("Under £100, £500 to £1,000, Over £1,000") == [
        "Under £100", "£500 to £1,000", "Over £1,000"], "a thousands comma carries no space"
    assert cloud_mod.split_options("") == []


TEXT = """
== 09-fixture
solution.compatibility [part 2]
  Q: On your last morning, did you have your phone to hand?
  options: [Yes, easily, Yes, with some steps, Only with help or approval, No]
  escape: I can't tell
  spoken: anchor=null | stem=On your last morning, did you have your phone to hand? | count=I'll read four options. | options=Yes, easily; yes, with some steps; only with help or approval; or no. | escape=Or say you can't tell. | transform=none
commercial.commitment [part 3]
  Q: If it were ready today, would you install the app, or not?
  options: [Yes, I'd start one, Yes, after trying it first, Probably not, No]
  escape: null
  spoken: anchor=null | stem=If it were ready today, would you install the app, or not? | count=I'll read four options. | options=Yes, you'd start one; yes, after trying it first; probably not; or no. | escape=null | transform=none
"""


def test_the_spoken_corpus_text_is_read_back_into_items():
    registry = fx.registry()
    items = cloud_mod.parse_spoken(TEXT, cloud_mod.known_labels_for(None, registry))["09-fixture"]
    assert [i.key for i in items] == ["solution.compatibility", "commercial.commitment"]
    first, second = items
    assert first.part == 2 and first.options == ("Yes, easily", "Yes, with some steps",
                                                 "Only with help or approval", "No")
    assert first.anchor is None and first.escape_line == "Or say you can't tell." and first.transform == "none"
    assert second.escape is None and second.escape_line is None
    assert second.options[0] == "Yes, I'd start one"
    assert all(spoken_mod.item_faults(i) == [] for i in items)


def test_a_cloud_that_wrote_nothing_is_a_refusal_naming_the_prerequisite(tmp_path):
    with pytest.raises(cloud_mod.CloudCorpusUnavailable) as refusal:
        cloud_mod.read(tmp_path)
    assert "SpokenGuidelinesCorpusTest" in str(refusal.value)
    with pytest.raises(cloud_mod.CloudCorpusUnavailable):
        cloud_mod.produce(tmp_path)
    with pytest.raises(cloud_mod.CloudCorpusUnavailable):
        cloud_mod.read_bundle(tmp_path)
    assert spoken_mod.unmeasured("why").spoken_form is None


# ------------------------------------------------------------------- the real record (calls 79-81)

@pytest.fixture(scope="module")
def real():
    from stack.config import load_config                              # noqa: PLC0415
    keel_cloud = load_config(validate=False).keel_cloud
    if not (keel_cloud / cloud_mod.SPOKEN_FILE).is_file():
        pytest.skip("keel-cloud's SpokenGuidelinesCorpusTest has not written build/spoken-corpus.txt -- run "
                    "`./gradlew test --tests '*SpokenGuidelinesCorpusTest'` in the keel-cloud checkout")
    fx.canon_entry("01-countly.yaml")                                 # skips by name off revision 10
    registry = fx.registry()
    corpus = corpus_mod.load(keel_cloud).bind(registry)
    return corpus, cloud_mod.read(keel_cloud, corpus=corpus, registry=registry)


def test_the_corpus_record_keeps_every_rule_but_the_five_known_items(real):
    corpus, cloud = real
    score = spoken_mod.score(cloud, corpus)
    assert score.faults == [], score.faults
    assert (score.units, score.clean, score.spoken_form) == (104, 104, 1.0)
    found = sorted((k["entry"], k["key"], k["evidence"].split(":")[0]) for k in score.known)
    assert found == sorted((e, k, r) for e, k, r, _code in spoken_mod.KNOWN)
    assert score.missing_known == []
    assert sum(len(cloud.items_of(e.id)) for e in corpus.entries) == 74, "seventy-four composed items, the gate aside"


def test_a_known_item_no_longer_found_is_itself_a_fault(real, monkeypatch):
    """Call 81: the ledger shrinks with the corpus -- a stale entry in it fails the mark."""
    corpus, cloud = real
    stale = ("01-countly", "commercial.commitment", "S10", None)
    monkeypatch.setattr(spoken_mod, "KNOWN", spoken_mod.KNOWN + (stale,))
    score = spoken_mod.score(cloud, corpus)
    assert score.missing_known == [stale]
    assert any(f["unit"] == "known" and "strike it" in f["evidence"] for f in score.faults)
    assert score.spoken_form < 1.0


def test_a_selection_of_entries_marks_those_alone(real):
    corpus, cloud = real
    score = spoken_mod.score(cloud, corpus, entry_ids={"03-lullaby"})
    assert set(score.by_entry) == {"03-lullaby"} and score.units == 14
    assert [k["entry"] for k in score.known] == ["03-lullaby"]
