"""Spec 112 -- the harness reads keel-cloud 171: the adoption frame, the marked suggestion, the founder's efforts in
the screen.

FR-1 the stranger's frame is *To use {name}, you'd {step}. Would you do that, or not?* (*To use it, ...*): the step in
base form (`spoken.step`, keel-cloud `SpokenCap.step`), held to 20 words by the cloud's give-way, the *it* swap where
the founder's row does not name the idea, then the lock's give-way to the founder's row; `K2` measures the whole
clause in the unnamed frame (`AskedRules.framed`). FR-2 one suggested Adoption friction row, last, with its why: `L5`
admits it, `L1` counts the founder's efforts, the walk names it off the flag and never picks it unless the entry did.
FR-3 the founder-lists screen hands a back-test entry's typed Answer to the writer and marks the redraft by 171.

Every sentence the cloud pins is pinned here as keel-cloud-docs `f4ca175f`'s tests write it
(`AdoptionStepsAreTheFoundersTest`, `AfterTheRerunsOn130Test`, `AfterTheRerunsOn131Test`).
"""
from __future__ import annotations

import json
import types
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from evals import backtest as bt
from evals import corpus_scenario
from harness import vectors_script as vs
from instructions import context as context_mod
from instructions import run as run_mod
from instructions import score as score_mod
from instructions import screen_entries as screen_mod
from instructions import spoken as spoken_mod
from instructions import validate as validate_mod
from stack.config import load_config
from tests import v9_fixtures as fx

ADOPTION = "solution.adoption_friction"
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
ASK = "Would you do that, or not?"


# ------------------------------------------------------------------------------------------- FR-1: the frame

def test_the_frame_reads_as_a_sentence_named_and_unnamed():
    """171 FR-4b's own sentence, named and unnamed, at most 20 words and never *means* / *You'd*."""
    clause = "let an AI answer your guests in your hotel's voice"
    named = spoken_mod.adoption_friction(clause, "Codyco")
    unnamed = spoken_mod.adoption_friction(clause)
    assert named == f"To use Codyco, you'd let an AI answer your guests in your hotel's voice. {ASK}"
    assert unnamed == f"To use it, you'd let an AI answer your guests in your hotel's voice. {ASK}"
    for stem in (named, unnamed):
        assert " means " not in stem and not stem.startswith("You'd")
        assert spoken_mod.words(stem) <= spoken_mod.STEM_MAX_WORDS
    assert spoken_mod.to_use(None, "scan it") == spoken_mod.to_use("  ", "scan it") == f"To use it, you'd scan it. {ASK}"


@pytest.mark.parametrize("stored, step", [
    ("Hold the phone near the cot", "hold the phone near the cot"),
    ("you'd upload your ID card", "upload your ID card"),
    ("would you share your ID card to sign up", "share your ID card to sign up"),
    ("You had to talk out loud to an AI tutor", "talk out loud to an AI tutor"),
    ("You would have to pay a verified seller", "pay a verified seller"),
    ("you need to scan each delivery", "scan each delivery"),
    ("You would have worn the glasses whenever you talked with hearing people",
     "wear the glasses whenever you talk with hearing people"),
    ("you wore the glasses", "wear the glasses"),
    ("you took short videos and talked over them", "take short videos and talk over them"),
    ("you could talk over the noise", "talk over the noise"),
    ("you were on site", "be on site"),
    ("They upload their last pay registers", "upload your last pay registers"),
    # 132's leading clause, moved to the end in the present
    ("When the repair was done, would you speak the fix into your phone.",
     "speak the fix into your phone when the repair is done"),
    # a clause's own purpose: the frame's *To use* says what the step is for
    ("to set it up, you'd upload your last 12 months of pay registers", "upload your last 12 months of pay registers"),
    # *them* stays the object (`StrangerGrammar.THIRD` turns *they* / *their*, never *them*)
    ("take short videos and talk over them", "take short videos and talk over them"),
])
def test_every_stored_shape_is_said_in_base_form_after_youd(stored, step):
    """171 FR-4b / T012 (`SpokenCap.step`): English's small words and the verb tables, nothing else."""
    assert spoken_mod.step(stored) == step


@pytest.mark.parametrize("asked, name, served", [
    # the cloud's own pins (`theStrangersFrameReadsAsASentenceNamedAndUnnamed`)
    ("you'd hold your phone near the cot for ten seconds", "Lullaby",
     f"To use Lullaby, you'd hold your phone near the cot for ten seconds. {ASK}"),
    ("You would have to pay a verified seller you have never met", "Karsa",
     f"To use Karsa, you'd pay a verified seller you have never met. {ASK}"),
    ("would you share your ID card to sign up", None, f"To use it, you'd share your ID card to sign up. {ASK}"),
    ("to set it up, you'd upload your last 12 months of pay registers, once", None,
     f"To use it, you'd upload your last 12 months of pay registers, once. {ASK}"),
    ("you wore the glasses whenever you talked with hearing people", "AirCaps",
     f"To use AirCaps, you'd wear the glasses whenever you talk with hearing people. {ASK}"),
    # past the cap: the phrase set off by commas is the first to give way (131 FR-4), named and unnamed
    ("you wore the glasses, paired to your phone, whenever you talked with hearing people", "AirCaps",
     f"To use AirCaps, you'd wear the glasses whenever you talk with hearing people. {ASK}"),
    ("you wore the glasses, paired to your phone, whenever you talked with hearing people", None,
     f"To use it, you'd wear the glasses whenever you talk with hearing people. {ASK}"),
    # past the cap with the leading clause moved to the end (21): the question part (132 FR-1)
    ("When the repair was done, would you speak the fix into your phone.", "Pairio",
     f"To use Pairio, you'd speak the fix into your phone. {ASK}"),
    ("When the repair was done, would you speak the fix into your phone.", None,
     f"To use it, you'd speak the fix into your phone. {ASK}"),
    # a name that takes the frame past the cap gives way to *it*
    ("let an AI answer your guests in your hotel's voice", "Codyco Front Desk Assistant",
     f"To use it, you'd let an AI answer your guests in your hotel's voice. {ASK}"),
])
def test_the_frame_at_and_over_the_cap_takes_each_fallback(asked, name, served):
    assert spoken_mod.adoption_friction(asked, name) == served
    assert spoken_mod.words(served) <= spoken_mod.STEM_MAX_WORDS


def test_past_every_form_the_whole_step_and_then_the_founders_row():
    """Past every fallback the frame is the whole step (`adoption_frame`, over 20); the lock then gives way to the
    founder's row in the same frame (`SpokenCap.plain`: named, *it* where the name takes it past 20), and with no row
    to the plain frame -- the served stem `vectors_script.adoption_statement` mirrors."""
    lemma = "you'd review and merge the prompt changes it opens in your codebase"
    whole = spoken_mod.adoption_friction(lemma, "Lemma")
    assert whole == spoken_mod.adoption_frame(lemma) and spoken_mod.words(whole) == 21
    assert vs.adoption_statement(lemma, "Lemma", "Review and merge the prompt changes it opens") == \
        f"To use Lemma, you'd review and merge the prompt changes it opens. {ASK}"
    assert vs.adoption_statement("take short videos and talk over them as you walk the site", "Fresco",
                                 "Take short videos and talk over them on walks") == \
        f"To use Fresco, you'd take short videos and talk over them on walks. {ASK}"
    issen = "you'd talk out loud in the language to an AI tutor on your phone every day"
    assert vs.adoption_statement(issen, "Issen", "Talk out loud to an AI tutor") == \
        f"To use Issen, you'd talk out loud to an AI tutor. {ASK}"
    # the row past 20 with the name: *it*
    row = "Talk out loud to an AI tutor every evening"
    assert vs.adoption_statement(issen, "The Issen Speaking Practice Companion", row) == \
        f"To use it, you'd talk out loud to an AI tutor every evening. {ASK}"
    # a row past 20 even with *it*: the plain frame
    assert vs.adoption_statement(issen, "Issen", "Talk out loud to an AI tutor on the phone every evening") == \
        vs.ADOPTION_PLAIN
    assert vs.adoption_statement(issen, "Issen") == vs.ADOPTION_PLAIN == "Would it fit the way you do things, or not?"
    assert vs.adoption_statement("  ", "Issen") is None


def test_the_clause_names_the_idea_with_it_where_the_founders_row_does_not():
    """171 FR-4 (`ItemFrames.saysIt`, `theStrangersClauseSaysItNeverTheBrandTheFoundersRowDidNotName`)."""
    assert spoken_mod.adoption_friction("forward your unanswered booking calls to Codyco", "Codyco",
                                        "Forward unanswered calls to it") == \
        f"To use Codyco, you'd forward your unanswered booking calls to it. {ASK}"
    assert spoken_mod.adoption_friction("open the Codyco app and check Codyco's call log", "Codyco",
                                        "Check the call log") == \
        f"To use Codyco, you'd open its app and check its call log. {ASK}"
    # the founder typed the brand into their row: theirs, kept
    assert spoken_mod.adoption_friction("connect Codyco to your hotel's PMS", "Codyco",
                                        "Connect Codyco to the hotel's PMS") == \
        f"To use Codyco, you'd connect Codyco to your hotel's PMS. {ASK}"
    # a short name in plain words is never turned
    plain = spoken_mod.adoption_friction("hold your phone near the cot", "a suggested reason for crying",
                                         "Hold the phone near the cot")
    assert "its" not in plain and "hold your phone near the cot" in plain
    # with no row known the two-argument frame swaps nothing; the lock's call (`adoption_statement`) does
    assert spoken_mod.adoption_friction("let Codyco answer your guests", "Codyco") == \
        f"To use Codyco, you'd let Codyco answer your guests. {ASK}"
    assert vs.adoption_statement("let Codyco answer your guests in your hotel's voice", "Codyco",
                                 "Let an AI answer guests in the hotel's voice") == \
        f"To use Codyco, you'd let it answer your guests in your hotel's voice. {ASK}"


def test_k2_measures_the_clause_in_the_new_frame_and_the_asked_job_is_handed_it():
    """171 `k2MeasuresTheClauseInTheNewFrameAndTheAskedJobIsHandedIt`: ten words fit, eleven are 21 framed."""
    ten = "let an AI answer your guests in your hotel's voice"
    eleven = "let an AI answer all your guests in your hotel's voice"
    assert spoken_mod.words(ten) == spoken_mod.ADOPTION_CLAUSE_MAX_WORDS == 10
    label = "Let an AI answer guests in the hotel's voice"
    assert spoken_mod.face_faults(ten, label, ADOPTION, "booking call") == []
    faults = spoken_mod.face_faults(eleven, label, ADOPTION, "booking call")
    assert faults == [f"K2: framed, it reads \"To use it, you'd {eleven}. {ASK}\", 21 words; at most 20"]
    assert context_mod.asked_frame(ADOPTION, "night") == f"To use it, you'd {{asked}}. {ASK}"
    # the frame's own *you'd* never answers K3 for a clause whose subject is someone else
    assert [f for f in spoken_mod.face_faults("the cry wakes the whole house", "x", ADOPTION, None)
            if f.startswith("K3")]


def test_the_served_stem_is_compared_with_the_founders_row():
    """`backtest.cloud_130` hands the mirror the tested row's label: a served stem in 171's frame reads clean."""
    lists = {ADOPTION: {"pickedIndex": 0, "items": [
        {"label": "Let an AI answer guests in the hotel's voice",
         "asked": "you'd let Codyco answer your guests in your hotel's voice"}]}}
    served = f"To use Codyco, you'd let it answer your guests in your hotel's voice. {ASK}"
    interview = {"kind": "FULL", "reveal": {"what": "Imagine Codyco."},
                 "parts": [{"part": 2, "items": [{"dimension": ADOPTION, "question": served}]}]}
    entry = types.SimpleNamespace(window=lambda: None, context={})
    j = types.SimpleNamespace(entry=entry, interviews={"Andreas": interview}, findings=[],
                              project=lambda path: f"/v2/projects/p{path}", get=lambda path: {"lists": lists},
                              changed={})
    assert vs.served_idea_name(interview) == "Codyco"
    assert bt.cloud_130(j).get("stems", []) == []


def test_the_gallery_keeps_its_recorded_run_and_the_mirror_says_the_new_frame():
    """FR-1's gallery line, as built (tasks.md): `expected-interview-fresco.json` pins what the 2026-10-22 run of record
    SERVED (the gallery exports a run's served questions verbatim, `evals/gallery.py`), so 123's statement stays there
    -- a project locked before keel-cloud 171 keeps its stored question (171 T014). The same founder row today is
    composed in the new frame: its 14-word clause gives way to the row (171 *not foreseen* 1)."""
    fixtures = Path(__file__).parent / "fixtures" / "gallery"
    pinned = json.loads((fixtures / "expected-interview-fresco.json").read_text(encoding="utf-8"))
    served = [i for i in json.dumps(pinned).split('"question": ') if "take short videos" in i]
    assert served and served[0].startswith('"You would have to take short videos')
    plan = json.loads((fixtures / "20261022T164045Z-backtest-08-fresco" / "export" / "plan.json")
                      .read_text(encoding="utf-8"))
    row = next(v for k, v in _walk(plan) if k == ADOPTION and isinstance(v, dict) and v.get("items"))["items"][0]
    assert vs.adoption_statement(row["asked"], "Fresco", row["label"]) == \
        f"To use Fresco, you'd take short videos and talk over them on walks. {ASK}"


def _walk(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


# ------------------------------------------------------------------------------------- FR-2: the suggestion

EFFORTS = [{"label": "Let an AI answer guests in the hotel's voice",
            "asked": "let an AI answer your guests in your hotel's voice"},
           {"label": "Set which calls the AI hands to the desk", "asked": "set which calls it hands to your desk"}]
KEELS = {"label": "Forward the calls you miss to it", "asked": "forward the calls you miss to it", "suggested": True,
         "suggested_why": "It answers only the calls it is given."}


def _faults(items):
    return score_mod.list_faults({"key": ADOPTION, "list": {"items": items}}, fx.registry().by_key(ADOPTION))


def test_one_suggested_step_with_its_why_is_outside_the_founders_one_to_four():
    """171 FR-2: L5 admits one, L1 counts the founder's efforts -- five rows (four typed and Keel's) pass, six fault
    *besides the one suggested step*."""
    assert ADOPTION in score_mod.SUGGESTED_ON
    assert _faults(EFFORTS + [KEELS]) == []
    four = EFFORTS * 2
    assert _faults(four + [KEELS]) == []
    assert _faults(four + EFFORTS[:1] + [KEELS]) == [
        f"L1: {ADOPTION} takes 1 to 4 items besides the one suggested step, and 5 were written"]
    # with no suggestion five rows are five of the founder's
    assert _faults(four + EFFORTS[:1]) == [f"L1: {ADOPTION} takes 1 to 4 items, and 5 were written"]


def test_two_suggestions_are_refused_and_a_missing_why_is_a_breach():
    two = EFFORTS + [KEELS, {**KEELS, "label": "Connect it to your phone line", "asked": "connect it to your phone line"}]
    assert [f for f in _faults(two) if f.startswith("L5")] == [
        "L5: item 4: Keel suggests at most one item, on Purchase friction (a step it adds), Compatibility (the condition "
        "most likely to be missing) and Adoption friction (a one-time step the actor takes, last) only"]
    no_why = {k: v for k, v in KEELS.items() if k != "suggested_why"}
    assert _faults(EFFORTS + [no_why]) == [
        "L5: item 3: the suggested step carries suggested_why -- what in the Answer or the idea calls for it, in one "
        "sentence"]
    assert _faults(EFFORTS + [{**KEELS, "suggested_why": "  "}])[0].startswith("L5: item 3: the suggested step")


def test_the_suggestion_stays_refused_elsewhere():
    """The other lists keep 121's L5: Relative advantage never carries one."""
    key = "solution.relative_advantage"
    items = [{"label": "Hours back at the end of the day"}, {"label": "Action items the same day", "suggested": True}]
    faults = score_mod.list_faults({"key": key, "list": {"items": items}}, fx.registry().by_key(key))
    assert [f for f in faults if f.startswith("L5")]


@dataclass
class _J:
    strict: bool = False
    findings: list = field(default_factory=list)


def _answer(labels, picked=0):
    return vs.CalibrationAnswer(dimension=ADOPTION, text="; ".join(labels), body={
        "dimension": ADOPTION, "list": {"items": [{"label": label} for label in labels], "pickedIndex": picked}})


def _question(rows):
    return {"dimension": ADOPTION, "draft": {"items": rows}}


TYPED = [EFFORTS[0]["label"], EFFORTS[1]["label"]]
SERVED_KEELS = {"label": KEELS["label"], "suggested": True, "suggestedWhy": KEELS["suggested_why"]}


def test_keel_added_reads_the_suggested_flag_and_names_its_why():
    """FR-2: 104's finding becomes *Keel suggested: '...' -- why*, read off the flag (the wire's `suggestedWhy`)."""
    question = _question([{"label": TYPED[0]}, {"label": TYPED[1]}, SERVED_KEELS])
    answer = _answer(TYPED)
    assert corpus_scenario.keel_suggested(question) == [{"label": KEELS["label"], "why": KEELS["suggested_why"]}]
    assert corpus_scenario.keel_added(question, answer) == [KEELS["label"]]
    j = _J()
    corpus_scenario._name_keel_added(j, ADOPTION, question, answer)
    assert [f["what"] for f in j.findings] == [
        "Adoption friction: Keel suggested: 'Forward the calls you miss to it' -- It answers only the calls it is given."]
    assert j.findings[0]["served"]["suggested"] == [{"label": KEELS["label"], "why": KEELS["suggested_why"]}]
    # the founder's own rows alone: nothing to name
    j = _J()
    corpus_scenario._name_keel_added(j, ADOPTION, _question([{"label": TYPED[0]}, {"label": TYPED[1]}]), answer)
    assert j.findings == []


def test_a_reworded_founder_row_is_never_called_keels_and_an_unmarked_invention_is_named_apart():
    """The flag, not a label diff: a founder row reworded (spec 108) is no *Keel suggested*; a row typed by no one and
    marked by no one is named as drafted unmarked (171 FR-1 says the writer drafts none)."""
    reworded = "Let an AI answer the guests in the hotel's voice"
    question = _question([{"label": reworded}, {"label": TYPED[1]}, {"label": "Train the staff on it"},
                          SERVED_KEELS])
    answer = _answer(TYPED)
    assert corpus_scenario.keel_added(question, answer) == [KEELS["label"]]
    assert corpus_scenario.keel_unmarked(question, answer) == ["Train the staff on it"]
    j = _J()
    corpus_scenario._name_keel_added(j, ADOPTION, question, answer)
    assert [f["what"] for f in j.findings] == [
        "Adoption friction: Keel suggested: 'Forward the calls you miss to it' -- It answers only the calls it is "
        "given.", "Adoption friction: Keel added, unmarked: 'Train the staff on it'"]
    # another dimension keeps 104's label diff
    compat = {"dimension": "solution.compatibility", "draft": {"items": [{"label": "A"}, {"label": "B"}]}}
    assert corpus_scenario.keel_added(compat, _answer(["A"])) == ["B"]
    assert corpus_scenario.keel_suggested(compat) == []


def test_choose_never_lands_on_a_suggested_row_unless_the_entry_picked_it():
    """FR-2: the near row (spec 108) is the founder's alone -- a suggested row as near as the typed label is never the
    pick; a typed label found on both is the founder's row; the entry's own pick of Keel's row word for word is."""
    want = "Forward missed calls to it"
    # the only row near the typed label is Keel's suggested one: the walk stops by name, never picks it
    question = _question([{"label": TYPED[1]}, {"label": "Forward the missed calls to it", "suggested": True,
                                                "suggestedWhy": "x"}])
    assert corpus_scenario.nearest_rows(want, ["Forward the missed calls to it"], [want, TYPED[1]]) == [
        "Forward the missed calls to it"]
    with pytest.raises(vs.VectorsScriptError, match="not on the drafted list"):
        corpus_scenario._choose_label(_J(), question, _answer([want, TYPED[1]]))
    # the same label on a typed row and on Keel's: the founder's row
    both = _question([{**SERVED_KEELS, "label": TYPED[0]}, {"label": TYPED[0]}, {"label": TYPED[1]}])
    assert corpus_scenario._choose_label(_J(), both, _answer(TYPED)) == (TYPED[0], 1)
    # the entry's typed pick is Keel's row word for word: picked
    picked = _question([{"label": TYPED[0]}, {"label": TYPED[1]}, SERVED_KEELS])
    assert corpus_scenario._choose_label(_J(), picked, _answer([*TYPED, KEELS["label"]], 2)) == (KEELS["label"], 2)
    # Keel's row never counts as near a typed one that was left out
    left = _question([{"label": TYPED[1]}, {**SERVED_KEELS, "label": "Let an AI answer the guests in the hotel's voice"}])
    assert corpus_scenario.keel_left_out(left, _answer(TYPED)) == [TYPED[0]]


def test_the_default_belief_is_the_founders_first_typed_row():
    """171 FR-3 (`SavedList.tested()` / `firstTyped()`): with no pick, the first row not marked suggested."""
    keels, first, second = {"label": "K", "suggested": True}, {"label": "A"}, {"label": "B"}
    assert bt._tested_item({"items": [keels, first, second]}) == first
    assert bt._tested_item({"items": [first, second, keels]}) == first
    assert bt._tested_item({"items": [first, second, keels], "pickedIndex": 2}) == keels
    assert bt._tested_item({"items": [keels]}) == keels
    assert bt._tested_item({"items": []}) == {}


# ------------------------------------------------------------------------------------------ FR-3: the screen

def _backtest_present(entry_id):
    if not (screen_mod.corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml").is_file():
        pytest.skip(f"keel-cloud has no back-test entry {entry_id}")


@pytest.mark.parametrize("entry_id, typed, name", [
    ("21-codyco", ["Let an AI answer guests in the hotel's voice", "Set which calls the AI hands to the desk"], "Codyco"),
    ("17-expanse", ["Use the suggested sizes instead of padding", "Apply the line-level code fixes it suggests"],
     "Expanse"),
    ("08-fresco", ["Take short videos and talk over them on walks", "Check and fix the notes before they go out"],
     "Fresco"),
])
def test_the_screen_hands_the_writer_the_entrys_typed_answer(tmp_path, entry_id, typed, name):
    """FR-3: `K=<id>/CALIBRATION_SOLUTION` names the entry's SOLUTION redrafts; the Adoption friction one is handed one
    dimension and the founder's typed Answer (`answers` was always `{}`), and carries 171's mark row."""
    _backtest_present(entry_id)
    needle = f"{entry_id}/CALIBRATION_SOLUTION"
    extras = screen_mod.load(KEEL_CLOUD, needle)
    assert [e.id for e in extras.backtest] == [entry_id]
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, needle=needle,
                                   n_runs=3)
    assert cases and all(c.kind == "CALIBRATION" and c.meta["source"] == "backtest" for c in cases)
    assert all(c.case_id.startswith(f"{entry_id}/CALIBRATION_SOLUTION/") for c in cases)
    steps = [c for c in cases if c.meta["dimension"] == ADOPTION]
    assert [c.case_id for c in steps] == [f"{entry_id}/CALIBRATION_SOLUTION/ADOPTION_FRICTION/run{n}" for n in (1, 2, 3)]
    context = steps[0].payload["context"]
    assert [d["key"] for d in context["dimensions"]] == [ADOPTION]
    assert context["answers"] == {ADOPTION: "; ".join(typed)}
    assert steps[0].meta["registry_slice"] == [ADOPTION] and steps[0].meta["vector"] == "SOLUTION"
    assert steps[0].meta["steps"] == {"mark": "171", "dimension": ADOPTION, "typed": typed,
                                      "names": screen_mod.brand_names(extras.backtest[0])}
    assert name in steps[0].meta["steps"]["names"]
    # every other list the entry typed is redrafted with its own Answer, no 171 row
    for case in cases:
        key = case.meta["dimension"]
        assert list(case.payload["context"]["answers"]) == [key]
        assert ("steps" in case.meta) == (key == ADOPTION)
    # the one dimension alone, by its name
    only = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                  needle=f"{needle}/ADOPTION_FRICTION", n_runs=1)
    assert [c.case_id for c in only] == [f"{entry_id}/CALIBRATION_SOLUTION/ADOPTION_FRICTION/run1"]
    # the validator is handed the state the job was: the one dimension and the Answer
    batch = validate_mod.build_batch([(only[0], {"vector": "SOLUTION", "questions": []})])
    assert batch["cases"][0]["answers"] == {ADOPTION: "; ".join(typed)}
    assert batch["cases"][0]["registry_slice"] == [ADOPTION]


def test_a_golden_entrys_seed_time_job_is_unchanged():
    """FR-3 builds back-test redrafts only: the golden corpus's CALIBRATION job still carries `answers` `{}`."""
    built = context_mod.build_calibration(fx.entry(), "SOLUTION", fx.registry())
    assert built["answers"] == {} and len(built["dimensions"]) > 1


ROW = {"mark": "171", "dimension": ADOPTION, "typed": TYPED, "names": ["Codyco", "missed calls booked by AI"]}


def _result(items):
    return {"vector": "SOLUTION", "questions": [{"key": ADOPTION, "list": {"items": items}, "respondent_note": "x"}]}


def test_the_171_mark_holds_the_founders_efforts_first_and_one_suggestion_last():
    held = screen_mod.steps_mark("21-codyco", ROW, outcome="COMPLETED", result=_result(EFFORTS + [KEELS]))
    assert held["held"] and held["faults"] == []
    assert held["suggested"] == [{"label": KEELS["label"], "why": KEELS["suggested_why"]}]
    assert held["clause_words"] == [10, 8, 7] and held["drafted"] == [*TYPED, KEELS["label"]]
    assert screen_mod.steps_mark("21-codyco", ROW, outcome="COMPLETED", result=_result(EFFORTS))["held"]
    assert "171 held" in screen_mod.probe_line(held) and "Keel suggested" in screen_mod.probe_line(held)


@pytest.mark.parametrize("items, outcome, fault", [
    ([EFFORTS[1], EFFORTS[0], KEELS], "COMPLETED", "not first and as typed"),
    ([KEELS, *EFFORTS], "COMPLETED", "not first and as typed"),
    ([{**EFFORTS[0], "label": "Let an AI answer the guests"}, EFFORTS[1]], "COMPLETED", "not first and as typed"),
    ([*EFFORTS, {"label": "Train the staff", "asked": "train your staff"}], "COMPLETED", "is not marked suggested"),
    ([*EFFORTS, KEELS, {**KEELS, "label": "Connect it"}], "COMPLETED", "2 suggested rows"),
    ([EFFORTS[0], EFFORTS[1], {k: v for k, v in KEELS.items() if k != "suggested_why"}], "COMPLETED",
     "carries no suggested_why"),
    ([{**EFFORTS[0], "asked": "let Codyco answer your guests in your hotel's voice"}, EFFORTS[1]], "COMPLETED",
     "names ['Codyco']"),
    ([*EFFORTS, {**KEELS, "asked": "forward your missed calls to codyco"}], "COMPLETED", "names ['Codyco']"),
    ([], "NEEDS_INPUT", "not COMPLETED"),
])
def test_the_171_mark_names_each_fault(items, outcome, fault):
    mark = screen_mod.steps_mark("21-codyco", ROW, outcome=outcome, result=_result(items))
    assert not mark["held"] and any(fault in f for f in mark["faults"]), mark["faults"]


def test_the_suggestion_out_of_place_is_a_fault():
    items = [EFFORTS[0], KEELS, EFFORTS[1]]
    mark = screen_mod.steps_mark("21-codyco", {**ROW, "typed": TYPED[:1]}, outcome="COMPLETED", result=_result(items))
    assert any("is not last" in f for f in mark["faults"]), mark["faults"]


def test_the_run_marks_a_backtest_redraft_off_its_first_turn(tmp_path):
    """FR-3 wired: `_score_probe` writes the 171 mark into the case's diff and `state.probes`; the other redrafts of
    the entry carry none, as before."""
    _backtest_present("21-codyco")
    needle = "21-codyco/CALIBRATION_SOLUTION"
    extras = screen_mod.load(KEEL_CLOUD, needle)
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, needle=needle,
                                   n_runs=1)
    steps = next(c for c in cases if c.meta["dimension"] == ADOPTION)
    other = next(c for c in cases if c.meta["dimension"] != ADOPTION)
    state = run_mod._RunState()
    answer = types.SimpleNamespace(outcome="COMPLETED", result=_result(EFFORTS + [KEELS]), schema_valid=True,
                                   schema_error=None, error=None, questions=None)
    diff = run_mod._score(steps, None, answer, None, state, judge=None)
    mark = run_mod._score_probe(steps, answer, diff, state)
    assert mark["held"] and diff["probe"]["mark"] == "171" and diff["failed"] is None and "171 held" in diff["line"]
    assert [m["case_id"] for m in state.probes] == ["21-codyco/CALIBRATION_SOLUTION/ADOPTION_FRICTION/run1"]
    bad = types.SimpleNamespace(**{**vars(answer), "result": _result([KEELS, *EFFORTS])})
    diff = run_mod._score(steps, None, bad, None, state, judge=None)
    run_mod._score_probe(steps, bad, diff, state)
    assert diff["failed"].startswith("probe: the founder's efforts are not first and as typed")
    diff = run_mod._score(other, None, answer, None, state, judge=None)
    assert run_mod._score_probe(other, answer, diff, state) is None and diff["source"] == "backtest"
    assert len(state.probes) == 2
