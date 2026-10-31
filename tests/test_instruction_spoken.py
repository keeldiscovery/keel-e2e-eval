"""The spoken-form marks and the cloud corpus they read (spec 040 FR-005; `spoken-questions-guidelines.md` §2-§5, §8;
keel-cloud 088 FR-001 / FR-003 / FR-005; judgement calls 79-81; spec 042 calls 111-112; spec 065).

Each of `S1`-`S10` and `K2`-`K6` fails once for its own reason on a hand-built item and passes on the good one, and the
real record -- keel-cloud's `build/spoken-corpus.txt` over corpus revision 13 -- keeps every rule, every stem at most
20 words, with no item known apart. Stackless and modelless: the real record and keel-cloud's `dimension-registry.json`
of record are read from the keel-cloud checkout `stack.toml` names (skipped by name when its corpus test has not run).

**Spec 065: the record reads the registry.** The hand-built items are held to the fixture registry (`fx.registry()`,
087's slice); the real record to keel-cloud's registry of record (`cloud_corpus.registry_of_record`), so a registry
change moves the record and this test together. Five changes the guard counted as 34 faults on master were keel-cloud's
own, on purpose, and are now read from the registry rather than a fixed table: Current solution's escape *Someone
else did it* (123 FR-3); Existing sacrifice's registry escape *I don't know* (115 / 123's escapes), said *I can't
recall* on a cost stated before the chain (spec 077's cost total, `CommercialChain.side`) -- and since keel-cloud 170
(spec 110 FR-2) the registry's own *I can't recall* (a record written before 170 is skipped by name,
`fx.skip_a_spoken_record_before_170`); Compatibility's four to the
condition's verb, *Yes, easily · Yes, mostly · Only sometimes · No* on an ability (123 FR-8); Buyer and payer's revised
four (123 FR-5); Commitment's options from the founder's step, three bands on a free step (118 FR-1 / FR-2), held to
nine words, counted whole (129 FR-15, spec 068 FR-2). `spoken.KNOWN` stays empty.
"""

from __future__ import annotations

import dataclasses
import types

import pytest

from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from instructions import spoken as spoken_mod
from tests import v9_fixtures as fx

ComposedItem = cloud_mod.ComposedItem
#: The registry the hand-built items are held to (087's slice: *Someone else does the checking*, the permission four).
REG = fx.registry()


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


def _faults(item, registry=REG, entry=None) -> list:
    return spoken_mod.item_faults(item, registry, entry)


def _rules(item, registry=REG, entry=None) -> list:
    return [f.split(":")[0] for f in _faults(item, registry, entry)]


def test_a_good_item_keeps_every_rule():
    assert _faults(_item()) == []


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
    assert _faults(buyer) == []
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


def test_every_stem_is_held_to_twenty_words_the_two_frames_too():
    """Call 111 (keel-cloud 091 FR-E): Relative advantage's and Existing sacrifice's frames were shortened, so spec
    040's 25-word allowance (call 79) is gone -- a 21-word stem is an S1 fault on every dimension."""
    # spec 089 FR-4 (keel-cloud 159): the scale's frame and four options, no transform (`yes_no_per_benefit` retired);
    # spec 113 FR-3 (keel-cloud 173): in 173's frame, the occasion inside the question
    stem = ("Would a key tag that beeps loudly have made your last busy morning before work go better for you, or "
            "not?")
    assert len(stem.split()) == 21
    benefit = _item(key="solution.relative_advantage", question=stem, stem=stem,
                    options=("A lot better", "A little better", "No difference", "Worse"),
                    count_line="I'll read four options.",
                    options_line="A lot better; a little better; no difference; or worse.", transform="none")
    assert _rules(benefit) == ["S1"]
    assert _rules(dataclasses.replace(benefit, transform="yes_no_per_benefit")) == ["S1", "S9"]
    # the short form over the cap (`ScaleFour.shortened`) says the idea *it* and keeps the occasion
    short = "Would it have made your last busy morning before work go better for you, or not?"
    assert len(short.split()) <= 20 and "busy morning before work" in short
    assert _faults(dataclasses.replace(benefit, question=short, stem=short)) == []
    assert {spoken_mod.stem_limit(k) for k in ("commercial.existing_sacrifice", "solution.relative_advantage",
                                                "problem.importance")} == {20}
    assert not hasattr(spoken_mod, "LONG_FRAMES")


def test_importance_asks_one_then_one_more_and_never_says_pick_two():
    """Spec 089 FR-3 (keel-cloud 158 T013, 160 FR-3): the question asks for one (*Think of your last {occasion}. Which
    one of these ...?*), the count line adds nothing, and *And one more?* is the item's ITEM_MORE clip -- a count line
    that still says *; pick two* is an S7 fault; the transform stays `one_then_one_more`."""
    labels = ("Getting through the morning traffic", "Finding the keys on the way out", "Riding in wet weather",
              "Fixing a flat tyre on the way", "Finding somewhere safe to park")
    stem = "Think of your last morning. Which one of these would you most like made easier?"
    importance = _item(key="problem.importance", part=1, question=stem, stem=stem, options=labels,
                       escape="None of these", count_line="I'll read five options.",
                       options_line="Getting through the morning traffic; finding the keys on the way out; riding "
                                    "in wet weather; fixing a flat tyre on the way; or finding somewhere safe to park.",
                       escape_line="Or say none of these.", transform="one_then_one_more")
    assert _faults(importance) == []
    assert _rules(dataclasses.replace(importance, count_line="I'll read five options; pick two.")) == ["S7"]
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
    assert _faults(price) == []
    assert _rules(dataclasses.replace(price, options_line="Under £1; £1 to £2; over £2; or you wouldn't pay for "
                                                          "this.")) == ["S8"]


def test_a_number_has_no_options_and_no_count_line():
    # spec 089 FR-5 (keel-cloud 160 FR-2, 158 T004): window first, and a count from 1. Spec 115 FR-2 re-pin (keel-cloud
    # 174 FR-5): past five steps the voice asks for the range -- *Say a number from 1 to 7.* (*A number ...* until 174)
    stem = "In the last 7 nights, on how many nights did that happen?"
    assert spoken_mod.count_answer_line(7) == "Say a number from 1 to 7."
    frequency = _item(key="problem.frequency", part=1, question=stem, stem=stem, options=(),
                      escape="I can't recall", count_line=None, options_line=spoken_mod.count_answer_line(7),
                      escape_line="Or say you can't recall.")
    assert _faults(frequency) == []
    assert _rules(dataclasses.replace(frequency, count_line="I'll read eight options.")) == ["S7"]
    assert _rules(dataclasses.replace(frequency, options=("0", "1"))) == ["S3"]


def test_commitment_has_no_escape_and_says_its_step_once():
    stem = "If it were ready today, would you install the app, or not?"
    commitment = _item(key="commercial.commitment", part=3, question=stem, stem=stem,
                       options=("Yes, I'd start one", "Yes, after trying it first", "Probably not", "No"),
                       escape=None, options_line="Yes, you'd start one; yes, after trying it first; probably not; "
                                                 "or no.", escape_line=None)
    assert _faults(commitment) == []
    doubled = "If it were ready today, would you introduce you to the IT supplier, or not?"
    assert _rules(dataclasses.replace(commitment, stem=doubled, question=doubled)) == ["S10"]
    assert set(_rules(dataclasses.replace(commitment, escape="I can't tell", escape_line="Or say you can't tell."))) \
        == {"S6"}, "named off the registry, and said on an item with none: both S6"


def test_the_anchor_is_split_off_and_set_once_a_part():
    item = _item(key="problem.current_solution_satisfaction", part=1,
                 # spec 089 FR-5 (keel-cloud 160 FR-4): *How did {phrase} go?*; spec 093 FR-1 (keel-cloud 161): the
                 # phrase bare
                 question="Think of the last morning. How did finding them go?",
                 anchor="Think of the last morning.", stem="How did finding them go?",
                 options=("Found them straight away", "Found them after a quick look", "It took a full search",
                          "Found them only after being late", "Never found them that morning"),
                 escape="Someone else does the checking", count_line="I'll read five options.",
                 options_line="Found them straight away; found them after a quick look; it took a full search; found "
                              "them only after being late; or never found them that morning.",
                 escape_line="Or say someone else does the checking.")
    assert _faults(item) == []
    assert _rules(dataclasses.replace(item, anchor=None)) == ["S2"]


# ------------------------------------------------------------------- spec 065: the record reads the registry

def _registry(**rows):
    """The fixture registry with some respondent rows rewritten -- `key=dict(...)` merged into its `respondent`."""
    document = fx.registry_document()
    for dimension in document["dimensions"]:
        dimension["respondent"].update(rows.get(dimension["key"]) or {})
    return registry_mod.from_document(document, source="spec 065 fixture", check=False)


def _entry(*, chain=False, b2b=False, steps=()):
    items = [{"code": "step", "label": label} for label in steps]
    return types.SimpleNamespace(chain=lambda: chain, b2b=lambda: b2b,
                                 founder_list=lambda key: {"items": items} if key == "commercial.commitment" else None)


CURRENT = dict(key="problem.current_solution_satisfaction", part=1,
               question="How did finding them go?",            # spec 093 FR-1 (keel-cloud 161): the phrase bare
               stem="How did finding them go?",
               options=("Found them straight away", "Found them after a quick look", "It took a full search",
                        "Found them only after being late", "Never found them that morning"),
               escape="Someone else did it", count_line="I'll read five options.",
               options_line="Found them straight away; found them after a quick look; it took a full search; found "
                            "them only after being late; or never found them that morning.",
               escape_line="Or say someone else did it.")


def test_the_escape_is_the_registrys_so_a_registry_change_moves_the_record_with_it():
    """FR-1: the same item keeps S6 under a registry whose row says *Someone else did it* (123 FR-3) and breaks it under
    087's slice, which says *Someone else does the checking* -- no table in between."""
    revised = _registry(**{"problem.current_solution_satisfaction": {"escape": {
        "code": "someone_else_checks", "label": "Someone else did it", "counts": "apart"}}})
    assert _faults(_item(**CURRENT), revised) == []
    assert _rules(_item(**CURRENT)) == ["S6", "S6"], "named and said off 087's escape"
    assert not hasattr(spoken_mod, "ESCAPES")
    assert _rules(_item(key="problem.not_a_dimension")) == ["S6"], "off the registry there is no escape of record"


def test_a_cost_stated_before_the_chain_is_said_with_spec_077s_escape():
    """FR-1 (`CommercialChain.side`): under registry decision 24 the row names *I don't know*; a cost stated before the
    chain is served spec 077's cost total and says *I can't recall* -- and a value box on the chain says the row's."""
    revised = _registry(**{"commercial.existing_sacrifice": {"control": "value_box", "escape": {
        "code": "dont_know", "label": "I don't know", "counts": "apart"}}})
    stem = "Last month, what did it cost you when the keys went missing?"
    cost = _item(key="commercial.existing_sacrifice", part=3, question=stem, stem=stem, options=(),
                 escape="I don't know", count_line=None, options_line="An amount, or a number of hours; nothing is 0.",
                 escape_line="Or say you can't recall.")
    assert _faults(cost, revised, _entry(chain=False)) == []
    assert _rules(cost, revised, _entry(chain=True)) == ["S6"], "on the chain the value box says 'I don't know'"
    assert _faults(dataclasses.replace(cost, escape_line="Or say you don't know."), revised, _entry(chain=True)) == []
    assert spoken_mod.served_escape(revised, "commercial.existing_sacrifice") == "I don't know", "no entry: the row"


def test_a_count_line_disagreeing_with_the_served_options_is_still_a_fault():
    """FR-4: the count names the served number -- Commitment's three bands on a free step (118 FR-1), Compatibility's
    ability four (123 FR-8) -- and one that does not is S7, as it always was."""
    stem = "If it were ready today, would you install the app, or not?"
    three = _item(key="commercial.commitment", part=3, question=stem, stem=stem,
                  options=("Yes, I'd install the app", "Probably not", "No"), escape=None,
                  count_line="I'll read three options.",
                  options_line="Yes, you'd install the app; probably not; or no.",
                  escape_line=None)
    assert _faults(three) == []
    assert _rules(dataclasses.replace(three, count_line="I'll read four options.")) == ["S7"]
    assert _rules(dataclasses.replace(three, options_line="Yes, you'd install the app; probably not; no.")) == ["S8"], \
        "a missing 'or' is still a fault"
    ability = _item(options=tuple(spoken_mod.ABILITY_ANSWERS.values()),
                    options_line="Yes, easily; yes, mostly; only sometimes; or no.")
    assert _faults(ability) == []
    assert _rules(dataclasses.replace(ability, count_line="I'll read five options.")) == ["S7"]


def test_commitments_options_are_counted_whole_and_held_to_nine_words():
    """Spec 068 FR-2 (keel-cloud 129 FR-15, `SpokenForm.STEP_OPTION_MAX_WORDS` 11 -> 9): *Yes, I'd* and the step together
    are the option, held to nine like every other dimension's -- Code Four's *Yes, I'd run a free pilot with a few
    officers* (ten) is a fault; 129 serves Lullaby's step cut to *Yes, I'd allow it to use the microphone* (eight)."""
    stem = "If it were ready today, would you allow it to use the microphone at night, or not?"
    eight = "Yes, I'd allow it to use the microphone"
    commitment = _item(key="commercial.commitment", part=3, question=stem, stem=stem,
                       options=(eight, "Probably not", "No"), escape=None, count_line="I'll read three options.",
                       options_line="Yes, you'd allow it to use the microphone; probably not; or no.",
                       escape_line=None)
    assert len(eight.split()) == 8 and _faults(commitment) == []
    ten = "Yes, I'd run a free pilot with a few officers"
    assert len(ten.split()) == 10 and spoken_mod.STEP_OPTION_MAX_WORDS == spoken_mod.OPTION_MAX_WORDS == 9
    assert "S4" in _rules(dataclasses.replace(commitment, options=(ten, "Probably not", "No"),
                                              options_line="Yes, you'd run a free pilot with a few officers; "
                                                           "probably not; or no."))
    assert spoken_mod.first_yes("Run a free pilot with a few officers") == "Yes, I'd run a free pilot"
    long_option = "Yes, easily and with no help from the front office"
    assert len(long_option.split()) == 10 and "S4" in _rules(_item(options=(long_option, "No")))


def test_commitment_names_no_escape_and_a_served_one_is_a_fault():
    """Spec 068 FR-2 (129 FR-9's escape open, T025 there): Commitment's escape is none in the registry and on the item;
    an item served with one names an escape the registry does not give."""
    assert spoken_mod.registry_escape(REG, "commercial.commitment") is None
    assert spoken_mod.item_escape(REG, "commercial.commitment") is None
    stem = "If it were ready today, would you start a paid pilot, or not?"
    commitment = _item(key="commercial.commitment", part=3, question=stem, stem=stem,
                       options=("Yes, I'd start a paid pilot", "Probably not", "No"), escape="I can't say",
                       count_line="I'll read three options.",
                       options_line="Yes, you'd start a paid pilot; probably not; or no.",
                       escape_line="Or say you can't say.")
    assert "S6" in _rules(commitment)


def test_the_labels_an_item_may_be_served_with_are_the_registrys():
    """FR-1: `served_labels` -- the fixed answers, Compatibility's ability four beside them, Commitment's options from
    the entry's step (and its smaller step, when the list carries one); the step lowered as `BeliefSentence.lower`."""
    compatibility = spoken_mod.served_labels(REG, "solution.compatibility")
    assert compatibility[:4] == ["Yes, easily", "Yes, with some steps", "Only with help or approval", "No"]
    assert set(spoken_mod.ABILITY_ANSWERS.values()) <= set(compatibility)
    commitment = spoken_mod.served_labels(REG, "commercial.commitment", _entry(steps=("Start a paid pilot",
                                                                                      "A free trial")))
    assert commitment[-2:] == ["Yes, I'd start a paid pilot", "Yes, after a free trial first"]
    assert spoken_mod.served_labels(REG, "commercial.commitment", _entry(steps=("IT sign-off",)))[-1] == \
        "Yes, I'd IT sign-off", "an acronym keeps its capitals"
    assert spoken_mod.served_labels(None, "solution.compatibility") == []
    assert spoken_mod.served_labels(REG, "problem.frequency") == []


R13_TEXT = """
== 09-fixture
solution.compatibility [part 2]
  Q: On your last morning, could you reach your phone?
  options: [Yes, easily, Yes, mostly, Only sometimes, No]
  escape: I can't tell
  spoken: anchor=null | stem=On your last morning, could you reach your phone? | count=I'll read four options. | options=Yes, easily; yes, mostly; only sometimes; or no. | escape=Or say you can't tell. | transform=none
commercial.commitment [part 3]
  Q: If it were ready today, would you install the app, or not?
  options: [Yes, I'd install the app, Probably not, No]
  escape: null
  spoken: anchor=null | stem=If it were ready today, would you install the app, or not? | count=I'll read three options. | options=Yes, you'd install the app; probably not; or no. | escape=null | transform=none
"""


def test_the_served_options_are_read_back_whole_with_the_registrys_labels():
    """FR-1: before spec 065 *Yes, mostly* and *Yes, I'd install the app* were split at their comma (the labels were
    the fixture's), and the count line was blamed for the parser's count; with the registry's served labels they are
    whole."""
    corpus = types.SimpleNamespace(by_id=lambda entry_id: _entry(steps=("install the app",)))
    items = cloud_mod.parse_spoken(R13_TEXT, cloud_mod.known_labels_for(corpus, REG))["09-fixture"]
    assert [len(i.options) for i in items] == [4, 3]
    assert all(_faults(i, REG, corpus.by_id(i.entry)) == [] for i in items)
    split = cloud_mod.parse_spoken(R13_TEXT, None)["09-fixture"]
    assert [len(i.options) for i in split] == [6, 4] and "S7" in _rules(split[0])


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
    # spec 112 FR-4 (keel-cloud 171 FR-4b): Adoption friction's frame is *To use it, you'd {step}.*, the clause's own
    # *you'd* dropped into it (was 123's *You'd scan it. Would you do that, or not?*)
    assert spoken_mod.framed("solution.adoption_friction", None, "you'd scan it.") == \
        "To use it, you'd scan it. Would you do that, or not?"


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
    assert all(_faults(i) == [] for i in items)


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

def _keel_cloud():
    from stack.config import load_config                              # noqa: PLC0415
    return load_config(validate=False).keel_cloud


@pytest.fixture(scope="module")
def real():
    keel_cloud = _keel_cloud()
    if not (keel_cloud / cloud_mod.SPOKEN_FILE).is_file():
        pytest.skip("keel-cloud's SpokenGuidelinesCorpusTest has not written build/spoken-corpus.txt -- run "
                    "`./gradlew test --tests '*SpokenGuidelinesCorpusTest'` in the keel-cloud checkout")
    fx.canon_entry("01-countly.yaml")                                 # skips by name off revision 13
    fx.skip_a_spoken_record_before_159(keel_cloud)                    # spec 089: a record before 158 / 159
    if not (keel_cloud / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip(f"no registry of record at {keel_cloud / cloud_mod.REGISTRY_FILE}")
    registry = cloud_mod.registry_of_record(keel_cloud)               # spec 065 FR-1: the registry of record
    corpus = corpus_mod.load(keel_cloud).bind(registry)
    return corpus, cloud_mod.read(keel_cloud, corpus=corpus, registry=registry)


def test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart(real):
    """Calls 111, 112 (keel-cloud 091), spec 065: the record held to keel-cloud's registry of record keeps every rule
    with no item named apart -- 74 composed items and 35 faces, 109 of 109. On master before spec 065 the same record
    held to the fixture registry and the fixed §5 table was 75 of 109: 34 faults, every one keel-cloud 118 / 123's own
    change (the module docstring's five), none a fault of the record."""
    corpus, cloud = real
    fx.skip_a_spoken_record_before_170(_keel_cloud(), corpus.entries[0].registry)    # spec 110 FR-2
    fx.skip_a_spoken_record_before_174(_keel_cloud(), corpus.entries[0].registry)    # spec 115 FR-0
    score = spoken_mod.score(cloud, corpus)
    assert score.faults == [], score.faults
    assert (score.units, score.clean, score.spoken_form) == (109, 109, 1.0)
    assert spoken_mod.KNOWN == () and score.known == [] and score.missing_known == []
    assert sum(len(cloud.items_of(e.id)) for e in corpus.entries) == 74, "seventy-four composed items, the gate aside"


def test_the_record_follows_registry_revision_13s_five_changes(real):
    """Spec 065 FR-2: each of the five changes, as the record carries it and the registry of record names it."""
    corpus, cloud = real
    registry = corpus.entries[0].registry
    items = {(i.entry, i.key): i for e in corpus.entries for i in cloud.items_of(e.id)}
    lullaby = lambda key: items[("03-lullaby", key)]                  # noqa: E731
    assert spoken_mod.registry_escape(registry, "problem.current_solution_satisfaction") == "Someone else did it"
    assert lullaby("problem.current_solution_satisfaction").escape_line == "Or say someone else did it."
    sacrifice = lullaby("commercial.existing_sacrifice")
    # keel-cloud 170 (spec 110 FR-2): the registry's row names *I can't recall* (was *I don't know*), the off-chain
    # escape it was already said with
    fx.skip_a_spoken_record_before_170(_keel_cloud(), registry)
    assert spoken_mod.registry_escape(registry, sacrifice.key) == spoken_mod.OFF_CHAIN_COST_ESCAPE == "I can't recall"
    assert (sacrifice.escape, sacrifice.escape_line) == ("I can't recall", "Or say you can't recall.")
    assert spoken_mod.served_escape(registry, sacrifice.key, corpus.by_id("03-lullaby")) == "I can't recall"
    # keel-cloud 128 FR-13b (corpus revision 15): Lullaby's *your phone was within reach* is a fact, so a fact's four --
    # spec 115 FR-1 re-pin (keel-cloud 174 FR-3): since 174 the registry's own four (`FACT_ANSWERS`); a record written
    # before 174 says 128's *Yes · Mostly · Partly · No* (`FACT_ANSWERS_128`)
    fact_four = spoken_mod.FACT_ANSWERS_128 if fx.spoken_record_before_174(_keel_cloud()) else spoken_mod.FACT_ANSWERS
    assert lullaby("solution.compatibility").options == tuple(fact_four.values())
    assert items[("05-paidly", "solution.compatibility")].options == tuple(
        a["label"] for a in registry.by_key("solution.compatibility").fixed_answers), "a permission keeps the four"
    # keel-cloud 128 FR-5 / FR-18: with no role named, the four are distinct answers
    assert lullaby("commercial.buyer_payer_alignment").options == ("Yes, someone else had to agree",
                                                                  "No, I decided on my own",
                                                                  "Yes, several people had to agree",
                                                                  "No, someone else decided for me")
    commitment = lullaby("commercial.commitment")
    # corpus revision 14 (keel-cloud 127): Lullaby's list carries its smaller step, so the second yes is served;
    # keel-cloud 129 FR-15 cuts the step to its share of the whole option's nine (*at night* goes): words, not codes
    assert commitment.options == ("Yes, I'd allow it to use the microphone",
                                  "Yes, after a look at how it listens first", "Probably not", "No")
    assert commitment.count_line == "I'll read four options."
    assert not hasattr(spoken_mod, "ESCAPES"), "the escapes are the registry's, never a table"


def test_the_ability_four_are_the_registrys_own_words(real):
    """Spec 065 FR-1 (123 FR-8): `ABILITY_ANSWERS` is the registry's Compatibility guidance and its worked example, on
    the registry's four codes -- were keel-cloud to reword them, this fails beside the record. Spec 115 FR-1 re-pin
    (keel-cloud 174 FR-3, T009): the registry's Lullaby block showed the ability four for a fact; Lullaby's condition
    (*their phone was within reach of the cot*) is a fact, so the block now shows the registry's own four, which are
    `FACT_ANSWERS` and the row's fixed answers."""
    corpus, _ = real
    compatibility = corpus.entries[0].registry.by_key("solution.compatibility")
    assert list(spoken_mod.ABILITY_ANSWERS) == compatibility.fixed_answer_codes
    assert " · ".join(spoken_mod.ABILITY_ANSWERS.values()) in compatibility.respondent["guidance"]
    registry_four = [a["label"] for a in compatibility.fixed_answers]
    assert list(spoken_mod.FACT_ANSWERS.values()) == registry_four
    assert compatibility.lullaby["respondent_options"][:4] == registry_four


def test_a_known_item_no_longer_found_is_still_a_fault_were_one_named(real, monkeypatch):
    """Call 81's ledger, kept empty (call 112): were an item named again and not found, the mark would say so."""
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
    assert set(score.by_entry) == {"03-lullaby"} and score.units == 15
    assert score.known == []
