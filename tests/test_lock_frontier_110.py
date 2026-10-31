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
    registry moved) -- a stand-in for the rerun the coordinator owes."""
    source = KEEL_CLOUD / cloud_mod.SPOKEN_FILE
    if not source.is_file() or not (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file():
        pytest.skip("no keel-cloud spoken record or registry of record")
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
    target.write_text(f"{SACRIFICE_KEY} [part 3]\n".join(moved), encoding="utf-8")
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
    assert score.faults == [] and (score.units, score.clean) == (109, 109), score.faults
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
    assert wording_mod.frequency_respondent(w, palus) == f"In the last 3 months, on how many months did {palus}?"
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
