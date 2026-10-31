"""Spec 110 (keel-cloud 170, cloud master `8c53497f`): the harness reads the lock's job on the frontier tier.

FR-1 (price version 14, RESPONDENT_QUESTIONS 70) is held where the mirror is (`test_credits_at_begin_088`,
`test_frontier_tier_105`). Here: FR-2, the gate's No (the attempt's *I didn't get to* retired, the page's own *No*), the
story clip's two chips as served, Existing sacrifice's escape *I can't recall* in S6, and `wording.gate()` framing a
clause that opens on *any* / *some* as its own subject; FR-3, the cost item's frame from the entry's typed loss line, its
chips and the value box's spoken label; FR-4, the screen reader's respondent case and 170's probe. Stackless and
modelless; keel-cloud's source is read from the checkout `stack.toml` names, skipped by name where it predates 170.
"""

from __future__ import annotations

import re
import shutil

import pytest

from evals import corpus_scenario as cs
from harness import interviewer_fake as fake
from harness import vectors_screens as vs_screens
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import spoken as spoken_mod
from instructions import wording as wording_mod
from instructions.registry import SACRIFICE_KEY
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = load_config(validate=False).keel_cloud
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
PASSAGES = "src/main/java/com/keeldiscovery/cloud/application/interviewer/PassageComposer.java"


def _cloud(rel: str, needle: str | None = None) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    text = path.read_text(encoding="utf-8")
    if needle is not None and needle not in text:
        pytest.skip(f"keel-cloud predates spec 170 ({rel} has no {needle!r})")
    return text


# ------------------------------------------------------------------------------------- FR-2: the gate's No

def _gate(*options: str) -> dict:
    return {"screen": "gate", "question": "In the last 4 weeks, did you lose the thread of a conversation?",
            "options": list(options), "chips": []}


def test_the_gate_draws_the_served_want_no_else_the_pages_own_no():
    assert cs.GATE_SERVED_NO_LABELS == (None, "I didn't") and cs.GATE_RETIRED_NO not in cs.GATE_SERVED_NO_LABELS
    assert cs.gate_no_label({}) == cs.gate_no_label({"noLabel": None}) == vs_screens.IV_NO == "No"
    assert cs.gate_no_label({"noLabel": "I didn't"}) == "I didn't"
    # an attempt stem since 170: no noLabel served, the page draws Yes / No
    assert cs.gate_no_faults(_gate("Yes", "No"), {"question": "x"}) == []
    # a want: the served *I didn't* drawn as the No
    assert cs.gate_no_faults(_gate("Yes", "I didn't"), {"noLabel": "I didn't"}) == []
    assert [next(iter(f)) for f in cs.gate_no_faults(_gate("Yes", "No"), {"noLabel": "I didn't"})] == ["gate No"]
    # a page that still draws the retired label where none is served is a fault, and so is the label served
    assert [next(iter(f)) for f in cs.gate_no_faults(_gate("Yes", "I didn't get to"), {})] == ["gate No"]
    served_retired = cs.gate_no_faults(_gate("Yes", "I didn't get to"), {"noLabel": "I didn't get to"})
    assert [next(iter(f)) for f in served_retired] == ["gate noLabel"] and served_retired[0]["retired"] is True
    # no gate drawn, or a gate with no question (the screener's outside exit): nothing to read
    assert cs.gate_no_faults(None, {"noLabel": "I didn't get to"}) == []
    assert cs.gate_no_faults({"screen": "gate", "question": None}, {}) == []


def test_occasion_stem_serves_only_the_wants_no():
    text = _cloud(VECTORS + "OccasionStem.java", "Spec 170")
    assert re.search(r'WANT_NO = "I didn\'t";', text) and cs.GATE_WANT_NO == "I didn't"
    assert "ATTEMPT_NO" not in text, "spec 120's attempt No is deleted"
    assert not re.search(r'=\s*"I didn\'t get to"', text), "no constant serves the retired label"


def test_the_harness_no_longer_expects_i_didnt_get_to():
    import inspect                                                      # noqa: PLC0415
    held = inspect.getsource(cs._hold_the_screens)
    assert '"I didn\'t get to"' not in held and "gate_no_faults(gate, served_gate)" in held
    assert 'gate.get("noLabel") or IV_NO' in inspect.getsource(vs_screens)


# ------------------------------------------------------------------------------ FR-2: the story clip's chips

def test_the_story_clip_says_the_served_chips_in_order():
    assert fake.story_escape(["CANT_RECALL", "RATHER_NOT_SAY"], "payroll run") == \
        "Or say: I can't recall one particular payroll run, or I'd rather not say."
    assert fake.story_escape(["RATHER_NOT_SAY", "CANT_RECALL"], "payroll run") == \
        "Or say: I'd rather not say, or I can't recall one particular payroll run.", "the served order"
    assert fake.story_escape(["CANT_RECALL"], None) == "Or say: I can't recall one particular time."
    assert fake.story_escape(["CANT_RECALL"], "  ") == "Or say: I can't recall one particular time."
    assert fake.story_escape([], "delivery") is None and fake.story_escape(None, "delivery") is None
    # the clip says the chip as the screen prints it
    assert fake.story_chip_word("CANT_RECALL", "delivery") == vs_screens.gate_chip_word("delivery")
    assert fake.STORY_RATHER_NOT_SAY == vs_screens.GATE_RATHER_NOT_SAY
    assert fake.GATE_YES_OR_NO == "Yes or no."


def test_the_story_clip_mirror_is_passage_composers_own():
    text = _cloud(PASSAGES, "storyEscape")
    body = text[text.index("static String storyEscape("):]
    body = body[:body.index("\n    }\n")]
    assert '"Or say: " + String.join(", or ", said) + "."' in body
    assert '"I can\'t recall one particular "' in body and '"time"' in body
    assert body.index('"CANT_RECALL"') < body.index('"RATHER_NOT_SAY"')
    assert re.search(r'RATHER_NOT_SAY = "I\'d rather not say";', text)
    assert "Yes or no." in _cloud("src/main/java/com/keeldiscovery/cloud/application/InterviewComposer.java")


# ---------------------------------------------------------------------- FR-2: S6 reads *I can't recall*

def test_existing_sacrifices_registry_escape_is_i_cant_recall():
    if not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip(f"no registry of record at {KEEL_CLOUD / cloud_mod.REGISTRY_FILE}")
    registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    if spoken_mod.registry_escape(registry, SACRIFICE_KEY) == fx.SACRIFICE_ESCAPE_BEFORE_170:
        pytest.skip("keel-cloud's registry predates spec 170 (Existing sacrifice's escape I don't know)")
    assert spoken_mod.registry_escape(registry, SACRIFICE_KEY) == spoken_mod.OFF_CHAIN_COST_ESCAPE == "I can't recall"
    assert registry.by_key(SACRIFICE_KEY).escape.get("code") == "dont_know", "the wire's code did not move"
    # on and off the chain: one escape, named and said
    from types import SimpleNamespace                                   # noqa: PLC0415
    on = SimpleNamespace(chain=lambda: True, b2b=lambda: True)
    off = SimpleNamespace(chain=lambda: False, b2b=lambda: True)
    assert spoken_mod.served_escape(registry, SACRIFICE_KEY, on) == spoken_mod.served_escape(
        registry, SACRIFICE_KEY, off) == spoken_mod.item_escape(registry, SACRIFICE_KEY, on) == "I can't recall"
    assert "*I don't know*, not *I can't recall*" not in (spoken_mod.__doc__ or ""), "the module note's item 2"
    assert "*I can't recall* since keel-cloud 170" in spoken_mod.__doc__


def _record_after_170(tmp_path):
    """keel-cloud's record, if any, with Existing sacrifice's escape as a run after 170 writes it (the one line the
    registry moved) -- a stand-in for the rerun the coordinator owes. Spec 115 FR-0: and Purchase friction's escape and
    its spoken line as a run after keel-cloud 174 writes them (*I can't tell*), where the record predates 174; a record
    written after 174 moves by neither."""
    source = KEEL_CLOUD / cloud_mod.SPOKEN_FILE
    if not source.is_file() or not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip("no keel-cloud spoken record or registry of record")
    fx.skip_without_brief_facts(KEEL_CLOUD)                           # spec 115: a record with no brief facts
    fx.canon_entry("01-countly.yaml")
    fx.skip_a_spoken_record_before_159(KEEL_CLOUD)
    registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    if spoken_mod.registry_escape(registry, SACRIFICE_KEY) == fx.SACRIFICE_ESCAPE_BEFORE_170:
        pytest.skip("keel-cloud's registry predates spec 170")
    target = tmp_path / cloud_mod.SPOKEN_FILE
    target.parent.mkdir(parents=True)
    shutil.copyfile(source, target)
    if (KEEL_CLOUD / cloud_mod.FACTS_DIR).is_dir():                     # `read` reads the brief facts beside it
        shutil.copytree(KEEL_CLOUD / cloud_mod.FACTS_DIR, tmp_path / cloud_mod.FACTS_DIR)
    text = target.read_text(encoding="utf-8")
    blocks = text.split(f"{SACRIFICE_KEY} [part 3]\n")
    moved = [blocks[0]] + [b.replace(f"\n  escape: {fx.SACRIFICE_ESCAPE_BEFORE_170}\n", "\n  escape: I can't recall\n", 1)
                           for b in blocks[1:]]
    friction = "commercial.purchase_friction [part 3]\n"
    blocks = f"{SACRIFICE_KEY} [part 3]\n".join(moved).split(friction)

    def told(block: str) -> str:
        # the Purchase friction item alone -- its indented lines, up to the next item's or entry's header
        item, rest = re.match(r"((?:  [^\n]*\n)*)(.*)\Z", block, re.S).groups()
        item = item.replace(f"\n  escape: {fx.FRICTION_ESCAPE_BEFORE_174}\n", "\n  escape: I can't tell\n", 1) \
            .replace("| escape=Or say you can't recall. |", "| escape=Or say you can't tell. |", 1)
        return item + rest
    target.write_text(friction.join([blocks[0]] + [told(b) for b in blocks[1:]]), encoding="utf-8")
    corpus = corpus_mod.load(KEEL_CLOUD).bind(registry)
    return registry, corpus, cloud_mod.read(tmp_path, corpus=corpus, registry=registry), source.read_text("utf-8") != \
        target.read_text("utf-8")


def test_a_record_written_after_170_keeps_every_rule(tmp_path):
    """Master's two spoken failures (this file's S6 and r19's Lullaby guard, 9 of 10) are the record's age: the same
    record with 170's one moved line is 109 of 109 and Lullaby 10 of 10."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest as bt                                    # noqa: PLC0415
    registry, corpus, cloud, _ = _record_after_170(tmp_path)
    score = spoken_mod.score(cloud, corpus)
    # spec 112 FR-4 (keel-cloud 171 FR-4b, its *not foreseen* 1): the corpus (r19) did not move, and five golden
    # Adoption friction faces -- 11 or 12 words, written to 163's *at most 12* -- are past *To use it, you'd*'s room:
    # each a `K2` on the framed line (was 109 of 109). The cloud never refuses a stored row (the lock gives way to the
    # founder's row); a corpus revision with 10-word faces is keel-cloud's to make.
    assert sorted((f["entry"], f["unit"]) for f in score.faults) == [
        ("01-countly", "asked scan_each_delivery"), ("02-compliancelog", "asked connect_once"),
        ("03-lullaby", "asked hold_phone_near_cot"), ("04-linerly", "asked fit_liner_once"),
        ("06-repeatline", "asked handle_exceptions")], score.faults
    assert all(f["key"] == "solution.adoption_friction" and f["evidence"].startswith("K2: framed, it reads \"To use it")
               for f in score.faults)
    assert (score.units, score.clean) == (109, 104)
    items = cloud.items_of("03-lullaby")
    served = [{"dimension": ci.key, "question": ci.question,
               "options": [{"optionId": str(n), "label": o} for n, o in enumerate(ci.options)],
               "escape": {"code": "X", "label": ci.escape} if ci.escape else None,
               "spoken": {"anchor": ci.anchor, "stem": ci.stem, "countLine": ci.count_line,
                          "optionsLine": ci.options_line, "escapeLine": ci.escape_line, "transform": ci.transform}}
              for ci in items]
    j = SimpleNamespace(entry=corpus.by_id("03-lullaby"), registry=registry,
                        interviews={"Amira Saleh": {"kind": "FULL", "parts": [{"part": 1, "items": served}]}})
    guard = bt.spoken_guard(j)
    assert (guard["items"], guard["clean"]) == (len(items), len(items)) == (10, 10), guard["red"]


def test_a_record_before_170_is_skipped_by_name(tmp_path):
    registry, *_ = _record_after_170(tmp_path)
    fx.skip_a_spoken_record_before_170(tmp_path, registry)              # the moved record: no skip
    stale = tmp_path / "stale"
    (stale / cloud_mod.SPOKEN_FILE).parent.mkdir(parents=True)
    (stale / cloud_mod.SPOKEN_FILE).write_text(f"01-countly\n{SACRIFICE_KEY} [part 3]\n  Q: Last month, what did it "
                                               f"cost you?\n  options: []\n  escape: I don't know\n", encoding="utf-8")
    with pytest.raises(pytest.skip.Exception, match="predates keel-cloud 170"):
        fx.skip_a_spoken_record_before_170(stale, registry)


# ------------------------------------------------------------------ FR-2: the gate framed as subjectLed

class _Window:
    count, singular, plural = 3, "month", "months"

    def words(self):
        return "the last 3 months"


def test_the_gate_frames_a_clause_that_opens_on_any_or_some_as_its_own_subject():
    w = _Window()
    palus = "any of the cash from your raise stay in your bank's money market fund"
    assert wording_mod.gate(w, palus) == f"In the last 3 months, did {palus}?"
    assert "did you any" not in wording_mod.gate(w, palus)
    assert wording_mod.gate(w, "some of the calls ring out after hours") == \
        "In the last 3 months, did some of the calls ring out after hours?"
    # spec 115 FR-2 re-pin (keel-cloud 174 FR-5): a month is counted *in* (*on how many months* until 174)
    assert wording_mod.frequency_respondent(w, palus) == f"In the last 3 months, in how many months did {palus}?"
    assert wording_mod.frequency_measured(w, palus) == f"On how many of those 3 months did {palus}?"
    # 116, 129, 130, 131's subjects, and the second person everywhere else
    assert wording_mod.subject_led("your team miss the deadline") == "your team miss the deadline"
    assert wording_mod.subject_led("freight cross the dock late") == "freight cross the dock late"
    assert wording_mod.subject_led("booking calls come in on every shift") == "booking calls come in on every shift"
    assert wording_mod.subject_led("the agent in production start failing") == "the agent in production start failing"
    assert wording_mod.subject_led("lose your keys") == "you lose your keys"
    assert wording_mod.subject_led("work out why your baby was crying") == "you work out why your baby was crying"
    assert wording_mod.subject_led("any cash") == "you any cash", "two words: no subject of its own (131's > 2)"
    # E4 measures the older frame without a second *you*: 22 words, past the cap (170's tasks.md, not foreseen 2)
    assert len(wording_mod.frequency_measured(w, palus).split()) == 22
    assert (wording_mod.framed_fault(palus, w) or "").startswith("E4: framed, the clause makes a question of 22 words")


def test_subject_led_mirrors_window_frame():
    text = _cloud(VECTORS + "WindowFrame.java", "spec 170 (FR-3b)")
    sets = re.findall(r'java\.util\.Set\.of\(([^)]*)\)\s*\.contains\(words\[0\]\)', text)
    assert sets, "WindowFrame.subjectLed's determiner set"
    assert tuple(re.findall(r'"(\w+)"', sets[0])) == wording_mod.SUBJECT_DETERMINERS
    from harness import vectors_script as vs                            # noqa: PLC0415
    assert {"any", "some"} <= set(vs._SUBJECT_LED)
    assert vs.subject_led("any of the cash from your raise stay in the fund").startswith("any of")


# ----------------------------------------------------------------------------- FR-3: the cost item, mirrored

from harness import loss_line as ll                                         # noqa: E402
from harness import vectors_script as vs                                    # noqa: E402

CHAIN_FIXTURES = "src/test/resources/commercial-chain"
BACKTEST = "canon/designs/measured-beliefs/backtest"


def _rate(measure, base, unit, period, loss):
    return {"mode": "RATE", "measure": measure, "base": base, "unit": unit, "period": period, "lossPhrase": loss}


def _asked(team, occasion, cost):
    question = vs.cost_question(team, occasion, None, cost if team else {**cost, "unit": None})
    assert ll.words(question) <= vs.STEM_MAX_WORDS, question
    low = question.lower()
    assert " lose" not in low and "come to" not in low and "(" not in low and "/" not in low, question
    return question


#: keel-cloud 170's `CostQuestionInTheirWordsTest`, case for case: the founder's line gives the verb and the thing (the
#: first four: Expanse word for word, Palus's *your team ... miss*, Codyco's share of the reservation calls, Lemma),
#: then the counts, then the neutral verbs where no line (or no verb) was typed.
FRAMES = [
    (True, "job submission", _rate("%", "the cluster's GPU hours", "cluster", "month",
                                   "GPU hours and memory that jobs reserve and never use"),
     "Last month, about what share of the cluster's GPU hours did jobs reserve and never use?"),
    (True, "cash decision", _rate("%", "the balance", "company", "year",
                                  "Interest on cash that sits in the operating account"),
     "Last year, about how much interest did your team miss on cash that sat in the operating account?"),
    (True, "reservation shift", _rate("%", "the reservation calls", "hotel", "month",
                                      "Bookings lost when a call rings out after hours, at peak or on a holiday"),
     "Last month, about what share of the reservation calls were lost?"),
    (True, "release", _rate("%", "the agent's runs in production", "agent", "month",
                            "Runs that fail in front of customers before anyone notices"),
     "Last month, about what share of the agent's runs in production failed in front of customers before anyone "
     "noticed?"),
    (False, "search", _rate("questions", "the questions they search", "person", "month",
                            "Questions they give up on because search shows only sellers' pages"),
     "Last month, about how many questions did you give up on because search showed only sellers' pages?"),
    (True, "quote", _rate("deals", "the deals they quote", "sales team", "month",
                          "Deals lost or signed on worse terms because the pricing was worked out by hand"),
     "Last month, how many deals were lost or signed on worse terms because the pricing was worked out by hand?"),
    (False, "reading session", _rate("days", "reading with no one listening", "child", "month",
                                     "School days the child reads with no one listening"),
     "Last month, about how many school days did the child read with no one listening?"),
    (True, "daily log", {"mode": "HOURS", "measure": "hours", "base": "the daily log", "unit": "site", "period": "month"},
     "Last month, about how many hours per site did your team spend on the daily log?"),
    (False, "group conversation", _rate("conversations", "the conversations they are in", "person", "month",
                                        "The thread of the conversation, and the moment with the people in it"),
     "Last month, about how many conversations did you miss?"),
    (True, "billing cycle", _rate("%", "the practice's collections", "practice", "month",
                                  "What billing staff or a billing company costs, plus claims rejected and never paid"),
     "Last month, about what share of the practice's collections did your team miss?"),
    (True, "shipment", _rate("%", "the shipments", "terminal", "month", None),
     "Last month, about what share of the shipments did your team miss?"),
]


@pytest.mark.parametrize("team, occasion, cost, question", FRAMES, ids=[f[1] for f in FRAMES])
def test_the_cost_frame_is_keel_cloud_170s(team, occasion, cost, question):
    assert _asked(team, occasion, cost) == question


def test_with_no_loss_line_the_frame_says_the_measures_neutral_verb():
    # a share and a count with no line: *miss*; hours: *spend on*; a line that says *now* keeps its present
    assert _asked(True, "shipment", _rate("%", "the shipments", "terminal", "month", None)).endswith(
        "did your team miss?")
    assert _asked(False, "x", _rate("conversations", None, None, "month", None)) == \
        "Last month, about how many conversations did you miss?"
    assert _asked(True, "x", {"mode": "HOURS", "base": None, "unit": "site", "period": "month"}) == \
        "Last month, about how many hours per site did your team spend on xes?", "the occasion's plural, as code makes it"
    assert _asked(True, "time", {"mode": "HOURS", "base": None, "unit": None, "period": "week"}) == \
        "Last week, about how many hours did your team spend on this?"
    assert "the sites you sell on now" in _asked(False, "sale", _rate("%", "the sales", "seller", "month",
                                                                      "Fees on every sale, on the sites they sell on now"))
    assert ll.read(None) is None and ll.read("  ") is None
    assert ll.read("What billing staff costs, plus claims never paid") is None, "a free relative names no thing"


def test_the_loss_line_is_read_in_four_shapes():
    assert ll.read("Runs that fail in front of customers before anyone notices").shape == ll.DOES
    done_by = ll.read("GPU hours and memory that jobs reserve and never use")
    assert (done_by.shape, done_by.thing, done_by.subject, done_by.clause) == (
        ll.DONE_BY, "GPU hours and memory", "jobs", "reserve and never use"), "an acronym keeps its capitals"
    assert ll.read("Bookings lost when a call rings out after hours").shape == ll.DONE
    none = ll.read("Interest on cash that sits in the operating account")
    assert (none.shape, none.thing, none.clause, none.rest_is_a_place()) == (
        ll.NONE, "interest", "on cash that sits in the operating account", True)
    assert ll.past("lost when a call rings out after hours") == "lost when a call rang out after hours"
    assert ll.after_did("reserve and never use") == "reserve and never use"
    assert ll.without_its_clause("lost when a call rings out") == "lost"


@pytest.mark.parametrize("cost, occasion, role, team, label", [
    (_rate("%", "the cluster's GPU hours", "cluster", "month", None), "job submission", "researcher", True,
     "% of GPU hours last month"),
    ({"mode": "HOURS", "measure": "hours", "base": "the daily log", "unit": "site", "period": "month"}, "daily log",
     "superintendent", True, "hours per site last month"),
    (_rate("conversations", "the conversations they are in", "person", "month", None), "group conversation", "wearer",
     False, "conversations last month"),
    (_rate("%", "the rupees they move to dollars", "person", "month", None), "conversion", "saver", False,
     "% of the rupees you move to dollars"),
    (_rate("weeks", "waiting for a first session", "referral", "each", None), "referral", "counsellor", True,
     "weeks per referral"),
])
def test_the_label_is_one_plain_phrase(cost, occasion, role, team, label):
    assert vs.stranger_cost_label(cost, occasion, role, team) == label
    assert " a month" not in label and "(" not in label


def test_the_value_boxs_spoken_line_names_the_label_and_its_chips_are_none_and_i_cant_recall():
    assert vs.value_box_answer_line(_rate("%", "x", "y", "month", None), "% of GPU hours last month") == \
        "A percent of GPU hours last month, or a low and a high; none is 0."
    assert vs.value_box_answer_line({"mode": "HOURS"}, "hours per site last month") == \
        "A number of hours per site last month, or a low and a high; none is 0."
    assert vs.value_box_answer_line({"mode": "MONEY"}, "per call minute") == \
        "An amount per call minute, or a low and a high; none is 0."
    assert vs.value_box_answer_line(_rate("%", None, None, "month", None), "%") == \
        "A percent, or a low and a high; none is 0."
    assert vs.VALUE_BOX_LABELS == {"NOTHING": "None", "DONT_KNOW": "I can't recall",
                                   "RATHER_NOT_SAY": "I'd rather not say"}
    assert vs.VALUE_BOX_CHIPS == {"nothing": "NOTHING", "dont_know": "DONT_KNOW", "rather_not_say": "RATHER_NOT_SAY"}
    assert vs.value_box_escapes(True) == ["DONT_KNOW", "RATHER_NOT_SAY"] and vs.value_box_escapes(False) == ["DONT_KNOW"]


def test_the_chip_words_mirror_commercial_chain():
    text = _cloud(VECTORS + "CommercialChain.java", "valueBoxAnswerLine")
    for name, code in (("NOTHING_LABEL", "NOTHING"), ("DONT_KNOW_LABEL", "DONT_KNOW"),
                       ("RATHER_NOT_SAY_LABEL", "RATHER_NOT_SAY")):
        assert re.search(rf'{name} = "{re.escape(vs.VALUE_BOX_LABELS[code])}";', text), name
    assert '", or a low and a high; none is 0."' in text and '"A percent "' in text


def _java_set(text: str, name: str) -> set[str]:
    at = text.index(f" {name} = Set.of(")
    body = re.sub(r"//[^\n]*", "", text[at:text.index(");", at)])            # the comments' quoted examples aside
    return set(re.findall(r'"([^"]+)"', body))


def test_the_loss_line_port_carries_keel_clouds_word_lists():
    text = _cloud(VECTORS + "LossLine.java", "enum Shape")
    for name in ("RELATIVE", "PREPOSITIONS", "SUBJECTS", "DETERMINERS", "JOINERS", "SUBORDINATORS", "AUXILIARIES",
                 "MORE_VERBS", "PARTICIPLES"):
        assert _java_set(text, name) == set(getattr(ll, name)), name
    grammar = _cloud(VECTORS + "StrangerGrammar.java", '"catch", "caught"')
    at = grammar.index("IRREGULAR = Map.ofEntries(")
    pairs = dict(re.findall(r'Map\.entry\("([^"]+)", "([^"]+)"\)', grammar[at:grammar.index(");", at)]))
    assert pairs == ll.IRREGULAR
    assert _java_set(grammar, "KEEP") == set(ll.KEEP)
    assert _java_set(grammar, "VERBS") == set(ll.VERBS)


def _fixtures():
    import json                                                             # noqa: PLC0415
    folder = KEEL_CLOUD / CHAIN_FIXTURES
    if not folder.is_dir():
        pytest.skip(f"keel-cloud has no {CHAIN_FIXTURES}")
    found = sorted(folder.glob("*.json"))
    out = [json.loads(f.read_text(encoding="utf-8")) for f in found]
    item = next(i for i in out[0]["expected"]["stranger"]["items"] if i["dimension"] == SACRIFICE_KEY)
    if item["valueBox"]["nothing"] != "None":
        pytest.skip("keel-cloud's worked cases predate spec 170")
    return [(f.stem, x) for f, x in zip(found, out)]


#: `CommercialChainFixturesTest.project`: every worked case's context carries Lullaby's job.
LULLABY_JOB = "work out what the baby needs and settle the baby"


def test_the_mirror_is_keel_clouds_seventeen_worked_cases():
    cases = _fixtures()
    assert len(cases) == 17
    for name, case in cases:
        given = case["input"]
        team = given["persona"].get("decider") == "SOMEONE_ELSE"
        role = given["persona"].get("role") if team else given["context"].get("actor")
        occasion = given["context"].get("occasion")
        item = next(i for i in case["expected"]["stranger"]["items"] if i["dimension"] == SACRIFICE_KEY)
        assert vs.cost_question(team, occasion, LULLABY_JOB, given["cost"]) == item["question"], name
        box = item["valueBox"]
        assert vs.stranger_cost_label(given["cost"], occasion, role, team) == box["label"], name
        assert box["nothing"] == vs.VALUE_BOX_LABELS["NOTHING"], name
        assert box["chips"] == [vs.VALUE_BOX_LABELS[c] for c in vs.value_box_escapes(not team)], name
        assert item["escape"] == vs.VALUE_BOX_LABELS["DONT_KNOW"], name


def _backtest(entry_id: str):
    path = KEEL_CLOUD / BACKTEST / f"{entry_id}.yaml"
    if not path.is_file() or not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip(f"no keel-cloud back-test entry {entry_id}")
    return corpus_mod.load_file(path, registry=cloud_mod.registry_of_record(KEEL_CLOUD), backtest=True)


@pytest.mark.parametrize("entry_id, question, label", [
    ("10-palus", "Last year, about how much interest did your team miss on cash that sat in the operating account?",
     "% of the balance last year"),
    ("17-expanse", "Last month, about what share of the cluster's GPU hours did jobs reserve and never use?",
     "% of GPU hours last month"),
    ("21-codyco", "Last month, about what share of the reservation calls were lost?",
     "% of the reservation calls last month"),
])
def test_the_three_entries_cost_items_are_170s_lines(entry_id, question, label):
    """170's tasks.md (FR-5 T014, not foreseen 6): Palus *your team* ... interest missed, Expanse word for word, Codyco
    the share of the reservation calls lost -- each from the entry's own typed `lossPhrase`, on its decision-maker's
    link."""
    entry = _backtest(entry_id)
    owed = vs.cost_item(entry)
    assert entry.b2b() and owed["question"] == question and owed["label"] == label
    assert owed["nothing"] == {"code": "NOTHING", "label": "None"}
    assert owed["chips"] == [{"code": "DONT_KNOW", "label": "I can't recall"}]
    assert owed["escape"]["label"] == "I can't recall" and owed["escapeLine"] == "Or say you can't recall."
    assert owed["optionsLine"] == vs.value_box_answer_line(entry.cost(), label)
    assert cs.cost_item_faults({"question": question, "valueBox": {"label": label},
                                "spoken": {"optionsLine": owed["optionsLine"]}}, owed) == {}


def test_the_screens_hold_reads_the_chip_words_and_writes_a_parted_question_as_a_finding():
    item = {"dimension": SACRIFICE_KEY, "question": "Last month, what did it cost you?",
            "escape": {"code": "DONT_KNOW", "label": "I can't recall"},
            "valueBox": {"label": "% of GPU hours last month", "nothing": {"code": "NOTHING", "label": "None"},
                         "chips": [{"code": "DONT_KNOW", "label": "I can't recall"}]}}
    assert cs.value_box_word_faults(item) == []
    old = {**item, "valueBox": {**item["valueBox"], "nothing": {"code": "NOTHING", "label": "Nothing"},
                                "chips": [{"code": "DONT_KNOW", "label": "I don't know"}]}}
    assert [w["want"] for w in cs.value_box_word_faults(old)[0]["value box words"]] == ["None", "I can't recall"]
    owed = {"question": "Last month, about what share of the cluster's GPU hours did jobs reserve and never use?",
            "label": "% of GPU hours last month", "optionsLine": "x", "escapeLine": "Or say you can't recall."}
    assert set(cs.cost_item_faults(item, owed)) == {"question"} and cs.cost_item_faults(item, None) == {}
    from types import SimpleNamespace                                       # noqa: PLC0415
    j = SimpleNamespace(entry=SimpleNamespace(id="x", chain=lambda: False, cost=lambda: None), findings=[])
    cs.cost_item_drift(j, item)
    assert j.findings == [], "off the chain nothing is owed"
    import inspect                                                          # noqa: PLC0415
    held = inspect.getsource(cs._hold_the_screens)
    assert "value_box_word_faults(item)" in held and "cost_item_drift(j, item)" in held


# ------------------------------------------------------------------------------ FR-4: the screen reader

import types                                                                # noqa: E402

import yaml                                                                 # noqa: E402

from instructions import context as context_mod                             # noqa: E402
from instructions import run as run_mod                                     # noqa: E402
from instructions import screen_entries as screen_mod                       # noqa: E402

#: keel-cloud 170's probe, restated (the live file is read below, skipped by name where absent).
JUDGEMENT_PROBE = {
    "id": "170-judgement-verb",
    "title": "Raised cash at a startup -- a gate whose founder words carry a verdict verb",
    "market": {"country": "US", "region": None, "language": "en-US"},
    "recall_window": {"count": 3, "unit": "MONTHS"},
    "job_context": {
        "part": 1, "link": "PRIMARY",
        "context": {"actor": "finance lead", "actor_plural": "finance leads at venture-backed startups",
                    "job": "earn interest on the cash from a raise without putting it at risk",
                    "circumstance": "finance leads leave their raised cash sitting idle in the bank's sweep account",
                    "segment": "venture-backed startups in the US that raised a round in the last two years",
                    "window": "the last 3 months"},
        "market": {"country": "US", "region": None, "language": "en-US"},
        "founder_name": None,
        "items": [{"key": "problem.prevalence"}, {"key": "problem.frequency"}, {"key": "problem.importance"},
                  {"key": "problem.current_solution_satisfaction"}],
        "problem": "left their raised cash sitting idle in the bank's sweep account",
        "condition": None},
    "probes": [{"screen": "RESPONDENT_QUESTIONS", "item": "problem.prevalence", "planted": ["leave", "sitting idle"],
                "verdict_words": ["idle", "sitting", "sit", "leave", "left", "still", "have to", "had to", "fail to",
                                  "waste", "struggle", "stuck"],
                "keeps": ["cash", "raise", "sweep account"],
                "register": "was any of the cash from your raise held in your bank's sweep account",
                "in_the_frame": "did any of the cash from your raise stay in your bank's sweep account?",
                "first_turn": {"outcome": "COMPLETED", "part": 1, "event": "one clause", "no_verdict_word": True,
                               "object_kept": True}}],
}
GOOD_EVENT = "any of the cash from your raise stay in your bank's sweep account"


def _checkout_110(tmp_path, probe=JUDGEMENT_PROBE):
    root = tmp_path / "keel-cloud"
    backtest, probes = corpus_mod.backtest_dir(root), screen_mod.probes_dir(root)
    backtest.mkdir(parents=True)
    probes.mkdir(parents=True)
    raw = fx.raw_entry()
    raw["id"] = "08-fixture-bt"
    raw.pop("expected", None)
    raw["idea_name"] = "The fixture idea"
    (backtest / "08-fixture-bt.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    (probes / f"{probe['id']}.yaml").write_text(yaml.safe_dump(probe, sort_keys=False), encoding="utf-8")
    return root


def test_build_respondent_hands_part_one_the_problem_and_the_condition():
    """keel-cloud 116 FR-1 / 120 FR-2 (`ScreenContextBuilder`): until spec 110 the export's `problem` and `condition`
    were written `null`, so every eval screen of this job wrote the gate from the circumstance."""
    entry, registry = fx.entry(), fx.registry()
    keys = context_mod.DEFAULT_KEYS["RESPONDENT_QUESTIONS"]
    assert keys.index("items") < keys.index("problem") < keys.index("condition") < keys.index("mechanism")
    part1 = context_mod.build_respondent(entry, 1, entry.plan(), registry, keys)
    assert part1["problem"] == vs.event_past(entry) and part1["problem"] is not None
    assert "condition" in part1 and part1["condition"] == vs.card_condition(entry)
    part2 = context_mod.build_respondent(entry, 2, entry.plan(), registry, keys)
    assert "problem" not in part2 and "condition" not in part2, "116 / 120: the part-1 job's alone"
    part3 = context_mod.build_respondent(entry, 3, entry.plan(), registry, keys)
    assert "problem" not in part3 and "condition" not in part3, "the person's part 3 on a study with a gate"
    b2b = context_mod.build_respondent(entry, 3, entry.plan(), registry, keys, link=context_mod.LINK_B2B)
    assert "condition" in b2b and "problem" not in b2b, "145 FR-4b: the decision-maker's link asks the screener"
    import dataclasses                                                      # noqa: PLC0415
    money_only = dataclasses.replace(entry, scope="COMMERCIAL")
    assert "condition" in context_mod.build_respondent(money_only, 3, entry.plan(), registry, keys), \
        "166 FR-2: the person's own part 3 on a study that serves no gate"


def test_a_golden_entrys_problem_is_its_own_prevalence_clause():
    if not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip("no keel-cloud registry of record")
    registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    countly = corpus_mod.load_file(fx.canon_entry("01-countly.yaml"), registry=registry)
    built = context_mod.build_respondent(countly, 1, countly.plan(registry), registry,
                                         context_mod.DEFAULT_KEYS["RESPONDENT_QUESTIONS"])
    assert built["problem"] == vs.PROBLEM_CLAUSES["01-countly"][0] == \
        "had to recount stock by hand after a mismatched delivery"
    assert built["condition"] == vs.card_condition(countly)


def test_a_backtest_entry_is_screened_on_respondent_part_one(tmp_path):
    root = _checkout_110(tmp_path)
    # spec 112 FR-3: the founder-lists redrafts joined after it (was the last of the four)
    assert screen_mod.BACKTEST_SCREENS[-2:] == ("RESPONDENT_QUESTIONS", "CALIBRATION_QUESTIONS")
    extras = screen_mod.load(root, "08-fixture-bt/RESPONDENT")
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                   needle="08-fixture-bt/RESPONDENT", n_runs=2)
    assert [c.case_id for c in cases] == ["08-fixture-bt/RESPONDENT_PART1/run1", "08-fixture-bt/RESPONDENT_PART1/run2"]
    case = cases[0]
    assert (case.kind, case.screen, case.subject) == ("RESPONDENT", "RESPONDENT_QUESTIONS", "PART1")
    assert case.meta["source"] == "backtest" and case.meta["part"] == 1 and case.meta["link"] == "PRIMARY"
    entry = extras.backtest[0]
    assert case.meta["plan"] == entry.plan(fx.exported(tmp_path).registry)[1]
    context = case.payload["context"]
    assert context["problem"] == vs.event_past(entry) and "condition" in context and "mechanism" not in context
    assert [i["key"] for i in context["items"]] == case.meta["plan"]
    assert screen_mod.is_extra(case) and screen_mod.plant_of(case) is None


def test_a_respondent_probe_is_read_and_built_from_its_job_context(tmp_path):
    root = _checkout_110(tmp_path)
    extras = screen_mod.load(root, "170-judgement-verb")
    assert extras.backtest == [] and [p.id for p in extras.probes] == ["170-judgement-verb"]
    probe = extras.probes[0]
    assert probe.respondent() and probe.recall_window == {"count": 3, "unit": "MONTHS"}
    plant = probe.plant_for("RESPONDENT_QUESTIONS")
    assert isinstance(plant, screen_mod.RespondentPlant) and plant.item == "problem.prevalence"
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                   needle="170-judgement-verb", n_runs=1)
    assert [c.case_id for c in cases] == ["170-judgement-verb/RESPONDENT_PART1/run1"]
    case = cases[0]
    assert case.kind == "RESPONDENT" and case.meta["source"] == "probe" and case.meta["part"] == 1
    context = case.payload["context"]
    assert list(context) == ["part", "link", "context", "market", "founder_name", "items", "problem", "condition"]
    assert context["problem"] == JUDGEMENT_PROBE["job_context"]["problem"] and context["condition"] is None
    gate = context["items"][0]
    assert gate["key"] == "problem.prevalence" and set(gate["respondent"]) >= {"anchor", "control", "escape"}
    assert screen_mod.plant_of(case) == plant, "the plant rides the case's meta whole"
    assert case.meta["probe"]["recall_window"] == {"count": 3, "unit": "MONTHS"}
    # 169's frame probe reads as it did
    assert screen_mod.load_probe.__doc__ and "job_context" in screen_mod.load_probe.__doc__


def test_a_broken_respondent_probe_refuses_by_name(tmp_path):
    import copy                                                             # noqa: PLC0415
    absent = copy.deepcopy(JUDGEMENT_PROBE)
    absent["probes"][0]["planted"] = ["parked"]
    root = _checkout_110(tmp_path, absent)
    with pytest.raises(corpus_mod.CorpusError, match="planted words"):
        screen_mod.load(root, "170-judgement-verb")
    other = copy.deepcopy(JUDGEMENT_PROBE)
    other["probes"][0]["item"] = "problem.nothing"
    path = tmp_path / "other.yaml"
    path.write_text(yaml.safe_dump(other), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="not among job_context's items"):
        screen_mod.load_probe(path)
    part3 = copy.deepcopy(JUDGEMENT_PROBE)
    part3["job_context"]["part"] = 3
    path.write_text(yaml.safe_dump(part3), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="part 1"):
        screen_mod.load_probe(path)


def _plant():
    row = JUDGEMENT_PROBE["probes"][0]
    return screen_mod.RespondentPlant(screen=row["screen"], item=row["item"], planted=tuple(row["planted"]),
                                      verdict_words=tuple(row["verdict_words"]), keeps=tuple(row["keeps"]),
                                      first_turn=dict(row["first_turn"]), register=row["register"],
                                      in_the_frame=row["in_the_frame"], recall_window=JUDGEMENT_PROBE["recall_window"])


def _result(event, part=1):
    return {"part": part, "link": "PRIMARY", "items": [{"key": "problem.prevalence", "event": event},
                                                       {"key": "problem.frequency"}]}


def test_the_probe_holds_an_event_with_no_verdict_word_that_keeps_the_object():
    mark = screen_mod.respondent_probe_mark("170-judgement-verb", _plant(), outcome="COMPLETED",
                                            result=_result(GOOD_EVENT))
    assert mark["held"] and mark["faults"] == [], mark
    assert mark["framed"] == "In the last 3 months, " + JUDGEMENT_PROBE["probes"][0]["in_the_frame"]
    assert "the gate's event says no verdict" in screen_mod.probe_line(mark)


@pytest.mark.parametrize("outcome, result, fault", [
    ("COMPLETED", _result("left the cash from your raise sitting idle in your bank's sweep account"),
     "says the verdict"),
    ("COMPLETED", _result("have to move the cash from your raise out of your bank's sweep account"),
     "says the verdict"),
    ("COMPLETED", _result("any of your money stay in the bank"), "drops the object"),
    ("COMPLETED", _result(GOOD_EVENT, part=2), "not part 1"),
    ("COMPLETED", {"part": 1, "items": [{"key": "problem.prevalence"}]}, "not one"),
    ("COMPLETED", _result("any of the cash from your raise stay in your bank's sweep account last month"),
     "not one clause"),
    ("NEEDS_INPUT", None, "not COMPLETED"),
])
def test_the_probe_marks_a_verdict_a_lost_object_and_a_wrong_turn(outcome, result, fault):
    mark = screen_mod.respondent_probe_mark("170-judgement-verb", _plant(), outcome=outcome, result=result)
    assert not mark["held"] and any(fault in f for f in mark["faults"]), mark["faults"]
    assert screen_mod.probe_line(mark).startswith("  probe FAULT")


def test_the_verdict_words_are_whole_words():
    """*sit* is never read inside *deposit*; *have to* is two words."""
    mark = screen_mod.respondent_probe_mark("170-judgement-verb", _plant(), outcome="COMPLETED",
                                            result=_result("deposit any of the cash from your raise into your bank's "
                                                           "sweep account"))
    assert mark["held"], mark["faults"]


def test_the_live_probe_reads_as_restated():
    path = screen_mod.probes_dir(KEEL_CLOUD) / "170-judgement-verb.yaml"
    if not path.is_file():
        pytest.skip("keel-cloud has no 170-judgement-verb probe")
    probe = screen_mod.load_probe(path)
    live = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert probe.respondent() and probe.job_context == live["job_context"] == JUDGEMENT_PROBE["job_context"]
    assert probe.plant_for("RESPONDENT_QUESTIONS").record() == _plant().record()
    # its expected wording holds its own mark
    assert screen_mod.respondent_probe_mark(probe.id, probe.plant_for("RESPONDENT_QUESTIONS"), outcome="COMPLETED",
                                            result=_result(GOOD_EVENT))["held"]


def test_the_run_never_scores_an_extra_and_marks_a_respondent_probe(tmp_path):
    root = _checkout_110(tmp_path)
    extras = screen_mod.load(root, "170-judgement-verb")
    case = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                  needle="170-judgement-verb", n_runs=1)[0]
    answer = types.SimpleNamespace(schema_valid=True, outcome="COMPLETED", result=_result(GOOD_EVENT), questions=[],
                                   error=None, schema_error=None)
    state = run_mod._RunState()
    diff = run_mod._score(case, None, answer, None, state, judge=None)      # no golden entry: never scored
    assert state.respondent == [] and "faults" not in diff
    mark = run_mod._score_probe(case, answer, diff, state)
    assert mark["held"] and state.probes == [mark] and diff["source"] == "probe" and not diff.get("failed")
    assert run_mod.denominators(run_mod._golden([case])) == {}
