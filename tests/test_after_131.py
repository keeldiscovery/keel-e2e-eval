"""Spec 070 (keel-cloud 131, contract 37): the harness half after 131, stackless -- the refused lock answered on the
idea card (FR-1), the spoken mirror (FR-2), the report_insights mark's fear-held head (FR-3). Every served sentence
quoted here is 131's own (its tasks.md, `AfterTheRerunsOn130Test`) or the 2026-10-24 re-runs' (keel-cloud-docs
`judgements/*-rerun-130.md`)."""

from __future__ import annotations

from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
FRAME = corpus_mod.BELIEF_FRAME


def _golden_entries():
    return corpus_mod.load(KEEL_CLOUD, registry=fx.registry()).entries


def _backtest(entry_id: str):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def _refusal_body(line: str, word: str, fault: str = "M5: a trade word") -> dict:
    """`Project.lock`'s refusal as `ProtocolErrorAdvice` serves it (`VectorRefusalBody`: rule, problem, remedy, code)."""
    return {"rule": "lock", "code": "TEXT_REFUSED",
            "problem": f"the idea card's {line} line still says '{word}', which a stranger may not follow: {fault}",
            "remedy": "edit that line on the idea card in plain words (or mark the word as the audience's own), then "
                      "lock"}


# ------------------------------------------------------------------------------- FR-1: the M5 mirror and the edit

CODYCO_HOW = ("You forward the calls nobody picks up to Codyco. Codyco answers in the hotel's voice, answers the guest's "
              "questions, takes the payment and writes the confirmed booking into the PMS (OPERA Cloud, Sihot, Apaleo).")
TRANSLOAD_HOW = ("You and your crew scan barcodes as usual. The software links each scan to that freight in the "
                 "terminal's security camera video, fits a 3D box to it, and compares it with the paperwork.")
TRANSLOAD_BELIEF = FRAME + "need no change to the dock workflow."
CODE_FOUR_HOW = "Code Four ties each fact to its clip and adds check words for you to catch. You review and sign."
PALUS_HOW = ("The tool puts your long-term reserve into a managed portfolio of short-duration, floating-rate, "
             "government-backed mortgage bonds, held in your company's name at a regulated firm.")


def test_no_golden_reveal_trips_the_m5_mirror():
    """131 FR-5's guard (`AfterTheRerunsOn129Test`, unmoved): the golden seven's idea lines carry no M5 fault, so their
    lock is never refused and a golden walk never meets FR-1."""
    entries = _golden_entries()
    assert len(entries) == 7
    for entry in entries:
        assert corpus_mod.m5_faults(vs.idea_lines(entry)) == [], entry.id


def test_the_m5_mirror_reads_the_cloud_order():
    """`RevealWords.m5`: the trade word first, then the names in parentheses, a design note on the belief only; the
    founder's audience words exempt."""
    faults = corpus_mod.m5_faults({"how": CODYCO_HOW, "belief": TRANSLOAD_BELIEF})
    assert [(f["line"], f["word"]) for f in faults] == [
        ("how", "PMS"), ("how", "(OPERA Cloud, Sihot, Apaleo)"), ("belief", "workflow"),
        ("belief", "need no change")]
    assert corpus_mod.m5_faults({"how": "it writes into the PMS."}, audience_words=["PMS"]) == []
    for belief in ("use cheap charging pads along the lines", "adapt to your level, goals and interests",
                   "do the calling the way the staff would, without an integration project"):
        assert [f["fault"] for f in corpus_mod.m5_faults({"belief": FRAME + belief + "."})] == ["design note"], belief
    assert corpus_mod.m5_faults({"belief": FRAME + "get every pole checked without walking the line."}) == []


def test_codyco_the_pms_and_its_names_go_in_one_edit():
    """Codyco's *PMS* -> *the hotel's booking system* (the judge's words) and the parenthesised list dropped in the same
    edit, so the second M5 fault on the line is not a second refusal."""
    after = corpus_mod.plain_line(_backtest("21-codyco"), "how", CODYCO_HOW, "PMS")
    assert after.endswith("writes the confirmed booking into the hotel's booking system.")
    assert corpus_mod.m5_faults({"how": after}) == []


def test_the_entries_own_plain_words():
    """Transload's *3D box*, Code Four's coined *check words*, Palus's bond phrase: each entry's own plain phrase."""
    transload = corpus_mod.plain_line(_backtest("12-transload"), "how", TRANSLOAD_HOW, "3D box")
    assert "measures the freight from the video" in transload and "3D" not in transload
    code_four = corpus_mod.plain_line(_backtest("14-code-four"), "how", CODE_FOUR_HOW, "check words")
    assert code_four == ("Code Four ties each fact to its clip and adds a few planted mistakes for you to catch. "
                         "You review and sign.")
    palus = corpus_mod.plain_line(_backtest("10-palus"), "how", PALUS_HOW, "short-duration")
    assert "a managed portfolio of short-term government-backed bonds, held in" in palus
    for after in (transload, code_four, palus):
        assert corpus_mod.m5_faults({"how": after}) == [], after


def test_a_design_note_belief_is_the_entrys_first_benefit():
    """131 FR-5's shape: Voltair's *use cheap charging pads* reads *get every pole checked without walking the line*
    (131's own test words); Issen's *adapt to*, Careforce's *without an integration project*, Transload's *need no
    change to the dock workflow* their first benefits, under the belief's frame."""
    voltair = corpus_mod.plain_line(_backtest("15-voltair"), "belief",
                                    FRAME + "use cheap charging pads along the lines.", "use")
    assert voltair == FRAME + "get every pole checked without walking the line."
    issen = corpus_mod.plain_line(_backtest("11-issen"), "belief",
                                  FRAME + "adapt to your level, goals and interests.", "adapt to")
    assert issen == FRAME + "get speaking practice any time, no tutor to book."
    careforce = corpus_mod.plain_line(_backtest("18-careforce"), "belief", FRAME + "do the calling the way the staff "
                                      "would, without an integration project.", "without an integration project")
    assert careforce == FRAME + "get patients reached without calling back again and again."
    transload = corpus_mod.plain_line(_backtest("12-transload"), "belief", TRANSLOAD_BELIEF, "workflow")
    assert transload == FRAME + "get every undercharged shipment caught, not just a sample."
    for after in (voltair, issen, careforce, transload):
        assert corpus_mod.m5_faults({"belief": after}) == [] and len(after) <= 200, after


def test_the_generic_fallback_and_the_fixs_own_suggestion():
    """An entry with no map: the names in parentheses dropped, an M5 word by its plain words; the fix's quoted
    suggestion taken where it offers one (131's fix offers none); a word no rule knows is no edit (None)."""
    class Bare:
        id = "99-none"

        @staticmethod
        def first_benefit():
            return None
    assert corpus_mod.plain_line(Bare(), "how", "It syncs with your ERP (SAP, Oracle) every night.", "ERP") == \
        "It syncs with the business system every night."
    assert corpus_mod.fix_suggestion(_refusal_body("how", "PMS")["remedy"], "PMS") is None
    assert corpus_mod.fix_suggestion('say "the hotel\'s booking system" instead of \'PMS\'', "PMS") == \
        "the hotel's booking system"
    assert corpus_mod.plain_line(Bare(), "how", "It reads the LiDAR scan.", "LiDAR") is None
    assert corpus_mod.plain_line(Bare(), "how", "It reads the LiDAR scan.", "LiDAR",
                                 'replace it with "laser"') == "It reads the laser scan."


# ------------------------------------------------------------------------------- FR-1: the walk, stubbed

def test_the_refusal_is_read_off_its_422():
    refused = cs.lock_refusal(422, _refusal_body("how", "PMS"))
    assert refused["line"] == "how" and refused["word"] == "PMS" and refused["rule"] == "lock"
    assert refused["fix"].startswith("edit that line on the idea card")
    assert cs.lock_refusal(200, {"version": 1}) is None
    assert cs.lock_refusal(422, {"code": "UNCALIBRATED", "problem": "x"}) is None
    assert cs.lock_refusal(422, {**_refusal_body("belief", "use"), "fix": "say it plainly"})["fix"] == "say it plainly"


class _Card:
    """The idea card behind the stubs: the lines the wire serves, edited by the stubbed Check screen."""

    def __init__(self, lines: dict, answers: list):
        self.lines = dict(lines)
        self.answers = list(answers)
        self.edits: list[dict] = []

    def read(self) -> dict:
        return dict(self.lines)

    def edit(self, edits: dict) -> dict:
        self.edits.append(dict(edits))
        self.lines.update(edits)
        return {"typed": edits}

    def relock(self) -> dict:
        return self.answers.pop(0)


def test_a_stubbed_422_then_a_second_pass_200():
    """Codyco: the lock refused on *PMS*, the how line edited once (the decider's how too, which the cloud names *how*),
    the second lock 200 -- one `lock_refused` finding with the words before and after."""
    entry = _backtest("21-codyco")
    decider = "Your agents forward the calls nobody picks up; Codyco writes each booking into the PMS."
    card = _Card({"how": CODYCO_HOW, "howDecider": decider, "belief": FRAME + "book the calls that ring out."},
                 [{"status": 200, "receipt": {"version": 1, "questions": {"interactionIds": ["i-1"]}}}])
    out = cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "PMS")), entry=entry, read_lines=card.read,
                                 edit=card.edit, relock=card.relock)
    assert out["status"] == 200 and out["passes"] == 1 and out["receipt"]["version"] == 1
    assert list(card.edits[0]) == ["how", "howDecider"]
    assert corpus_mod.m5_faults(card.lines) == []
    [finding] = out["findings"]
    assert finding["what"] == "lock_refused" and finding["rule"] == "lock" and finding["code"] == "TEXT_REFUSED"
    assert finding["line"] == "how" and finding["word"] == "PMS" and finding["edited"] is True
    assert finding["before"]["how"] == CODYCO_HOW and "the hotel's booking system" in finding["after"]["how"]


def test_two_lines_refused_one_after_the_other():
    """Transload: *3D box* on how, then the design-note belief -- two refusals on two lines, each edited once."""
    entry = _backtest("12-transload")
    card = _Card({"how": TRANSLOAD_HOW, "belief": TRANSLOAD_BELIEF},
                 [{"status": 422, "receipt": _refusal_body("belief", "workflow")}, {"status": 200, "receipt": {}}])
    out = cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "3D box")), entry=entry,
                                 read_lines=card.read, edit=card.edit, relock=card.relock)
    assert out["passes"] == 2 and [f["line"] for f in out["findings"]] == ["how", "belief"]
    assert corpus_mod.m5_faults(card.lines) == []


def test_a_second_refusal_of_the_same_line_stops_with_the_words_named():
    entry = _backtest("21-codyco")
    card = _Card({"how": CODYCO_HOW}, [{"status": 422, "receipt": _refusal_body("how", "Sihot")}])
    with pytest.raises(AssertionError, match="refused the idea card's how line again"):
        cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "PMS")), entry=entry, read_lines=card.read,
                               edit=card.edit, relock=card.relock)
    assert len(card.edits) == 1


def test_a_word_no_edit_moves_stops_before_any_edit():
    entry = _backtest("15-voltair")
    card = _Card({"how": "The drones take photos, LiDAR and thermal readings."}, [])
    with pytest.raises(AssertionError, match="no plain edit moves it"):
        cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "LiDAR")), entry=entry,
                               read_lines=card.read, edit=card.edit, relock=card.relock)
    assert card.edits == []
