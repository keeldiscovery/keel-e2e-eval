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


# ------------------------------------------------------------------------------- FR-2: the follow-up mirror

def _golden(entry_id: str):
    return corpus_mod.load_file(corpus_mod.corpus_dir(KEEL_CLOUD) / f"{entry_id}.yaml", registry=fx.registry())


def _interview(rung: str, labels: dict, question: str = "q", token: str = "tok", part: int = 2) -> dict:
    item = {"dimension": rung, "question": question,
            "options": [{"optionId": vs.option_id(token, rung, code), "label": label} for code, label in labels.items()]}
    return {"occasion": "shift", "parts": [{"part": part, "items": [item]}]}


def test_importances_follow_up_text_is_its_spoken_line():
    """131 FR-7 (`SAID_AS_SPOKEN`): never the picks and the own item pasted (Codyco's 28 words)."""
    lullaby = _golden("03-lullaby")
    rung = "problem.importance"
    codes = [vs.wire_code(rung, i) for i in range(5)]
    owed = vs.follow_up_question(lullaby, [vs.Pick(dimension=rung, codes=codes[1:3])], vs.LINK_PRIMARY,
                                 _interview(rung, {c: f"Label {c}" for c in codes}, part=1), "tok")
    # spec 086 FR-5 (keel-cloud 154): the founder's own item said back, as served
    assert owed["text"] == owed["spoken"] == \
        f"You did not pick {vs.fake_lower('Label ' + codes[0])} as one to make easier. What made the others more " \
        "pressing for you?"


def test_compatibility_says_a_thing_condition_back_and_is_spoken_as_it_reads():
    """131 FR-10 (`thingCouldNot`, `saidBack`): Aylin's *Only sometimes* on Codyco's saved condition -- *You said you
    couldn't always have forwarded unanswered calls to another number. What got in the way?* (131's words), spoken the
    same; and No."""
    codyco = _backtest("21-codyco")
    rung = "solution.compatibility"
    labels = {"yes_easily": "Yes, easily", "yes_with_steps": "Yes, mostly", "only_with_help": "Only sometimes",
              "no": "No"}
    question = ("Think of your last reservation shift. Could your hotel's phone system have forwarded unanswered "
                "calls to another number?")
    sometimes = vs.follow_up_question(codyco, [vs.Pick(dimension=rung, codes=["only_with_help"])], vs.LINK_PRIMARY,
                                      _interview(rung, labels, question), "tok")
    assert sometimes["text"] == sometimes["spoken"] == ("You said you couldn't always have forwarded unanswered calls "
                                                        "to another number. What got in the way?")
    no = vs.follow_up_question(codyco, [vs.Pick(dimension=rung, codes=["no"])], vs.LINK_PRIMARY,
                               _interview(rung, labels, question), "tok")
    assert no["text"] == no["spoken"] == \
        "You said you couldn't have forwarded unanswered calls to another number. What got in the way?"
    assert vs.thing_could_not("could your hotel's phone system have forwarded unanswered calls to another number") == \
        "have forwarded unanswered calls to another number"
    assert vs.thing_could_not("could you scan it") is None


def test_a_fact_about_them_is_said_to_the_person_whole():
    """131 FR-3 (`factSaid`, `hadNo`, AirCaps): *your phone was with you and online*; *You said you didn't have your
    phone with you*, never *you had no your phone ...*."""
    assert vs.fact_said("Their phone was with them and online") == "your phone was with you and online"
    assert vs.had_no("did you have your phone with you and online during the conversation") == \
        "You said you didn't have your phone with you. What do you use instead?"
    assert vs.had_no("did you have a bank account in your own name") == \
        "You said you had no bank account in your own name. What do you use instead?"


# ------------------------------------------------------------------------------- FR-2: the narrow mirrors

def test_the_gate_on_the_circumstances_event_for_the_five_seeds():
    """131 FR-1 (T004), each seed's circumstance as its yaml states it: the five gates and Code Four's 20-word
    Frequency; a state gives none (AirCaps, Voltair)."""
    want = {"21-codyco": "In the last 7 days, did a booking call come in on your shift?",
            "10-palus": "did you decide where cash from a raise would sit?",
            "16-pairio": "did a machine on your line go down?",
            "20-lemma": "did your agent in production start failing on real inputs?",
            "14-code-four": "In the last 7 days, did you have to turn a call's body-cam footage into a written report?"}
    for entry_id, gate in want.items():
        entry = _backtest(entry_id)
        served = vs.gate_from_circumstance(vs.window_of(entry), entry.context["circumstance"])
        assert served.endswith(gate), (entry_id, served)
        assert len(served.split()) <= vs.STEM_MAX_WORDS, served
    code_four = _backtest("14-code-four")
    frequency = vs.frequency_held(vs.window_of(code_four), vs.circumstance_event(code_four.context["circumstance"]))
    # spec 089 FR-5 (keel-cloud 160 *What did not hold*): window first, Code Four's clause is 21 words even with the unit
    # said once, and *into* is no trailing phrase 131 cuts -- it falls to *did that happen?*; in the frame before 160 it
    # was whole at 20
    assert frequency == "In the last 7 days, on how many days did that happen?"
    before = vs.frequency_held_before160(vs.window_of(code_four),
                                         vs.circumstance_event(code_four.context["circumstance"]))
    assert before == ("On how many of those 7 days did you have to turn a call's body-cam footage into a written "
                      "report?") and len(before.split()) == 20
    for entry_id in ("13-aircaps", "15-voltair"):
        assert vs.circumstance_event(_backtest(entry_id).context["circumstance"]) is None, entry_id


def test_frequency_is_held_under_the_cap():
    """131 FR-2 (Fresco): cut by the trailing phrase; a clause no cut fits asks *did that happen?*. Spec 089 FR-5
    (keel-cloud 160 FR-2, judgement call 4): window first, the unit said once before the cut -- Fresco's 24 words still
    cut as before (*... by hand?*, 20); the frame before 160 held as 131 held it."""
    window = vs.Window(5, "WORKING_DAYS")
    assert vs.frequency_held(window, "type up the daily log by hand after the site walks") == \
        "In the last 5 working days, on how many working days did you type up the daily log by hand?"
    assert vs.frequency_held(window, "type it up") == \
        "In the last 5 working days, on how many working days did you type it up?"
    assert vs.frequency_held(window, "reconcile every single supplier delivery note against its matching invoice "
                                     "line") == "In the last 5 working days, on how many working days did that happen?"
    # the unit said once where that alone fits (keel-cloud 160 judgement call 4)
    assert vs.frequency_held(vs.Window(7, "DAYS"), "have to recount the stock by hand after a delivery") == \
        "In the last 7 days, on how many did you have to recount the stock by hand after a delivery?"
    assert vs.frequency_held_before160(window, "type up the daily log by hand after the site walks") == \
        "On how many of those 5 working days did you type up the daily log by hand?"
    assert vs.frequency_held_before160(window, "type it up") == "On how many of those 5 working days did you type it up?"


def test_the_adoption_frame_whole():
    """131 FR-4 (T013), through the named frame: every verb in -ing, a step stored as a question, a past statement, a
    phrase set off by commas dropped past the cap (AirCaps)."""
    assert vs.adoption_statement("take short videos and talk over them as you walk the site", "Fresco") == \
        "Fresco means taking short videos and talking over them as you walk the site. Would you do that, or not?"
    assert vs.adoption_statement("read and correct every draft before you sign it", "Code Four") == \
        "Code Four means reading and correcting every draft before you sign it. Would you do that, or not?"
    assert vs.adoption_statement("review and merge the prompt changes it opens in your codebase", "Lemma") == \
        "Lemma means reviewing and merging the prompt changes it opens in your codebase. Would you do that, or not?"
    assert vs.adoption_statement("Would you speak the fix into your phone when the job is done.", "Pairio") == \
        "Pairio means speaking the fix into your phone when the job is done. Would you do that, or not?"
    assert vs.adoption_statement("you wore the glasses, paired to your phone, whenever you talked with hearing people",
                                 "AirCaps") == \
        "AirCaps means wearing the glasses whenever you talk with hearing people. Would you do that, or not?"


def test_the_buyer_set_never_says_someone_else_instead():
    """131 FR-13: *No, the CFO would have to agree · Yes, I could sign off on it myself · No, several people would have
    to agree · No, it would be someone else's decision*."""
    from instructions import spoken as sp                               # noqa: PLC0415
    labels = sp.buyer_answers("the CFO")
    assert "No, someone else would have to agree instead" not in labels
    assert labels[2:] == ["No, the CFO would have to agree", "Yes, I could sign off on it myself",
                          "No, several people would have to agree", "No, it would be someone else's decision"]


def test_cloud_131_reads_the_served_words_beside_the_mirror_as_findings():
    """On a back-test the 131 words read beside the wire, each a finding, never a stop: the job asked by the gate, a
    21-word Frequency, *per pole, each*, *your officers get ...*, *... instead*; the lock's edits carried."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest                                          # noqa: PLC0415
    codyco = _backtest("21-codyco")
    items = [{"dimension": "problem.frequency", "question": " ".join(["word"] * 21) + "?"},
             {"dimension": "commercial.price", "question": "What would Codyco be worth to you per pole, each?",
              "whatYouGet": "your officers get the report done in minutes"},
             {"dimension": "commercial.buyer_payer_alignment", "question": "Could you sign off?",
              "options": [{"label": "No, someone else would have to agree instead"}]}]
    interview = {"gate": {"question": "In the last 7 days, did you turn every guest who calls into a booking?"},
                 "parts": [{"part": 1, "items": items}]}
    j = SimpleNamespace(entry=codyco, interviews={"Aylin": interview}, findings=[],
                        changed={"lock_refused": [{"what": "lock_refused", "line": "how", "word": "PMS"}]})
    got = backtest.cloud_131(j)
    assert got["gate"][0]["mirror"] == "In the last 7 days, did a booking call come in on your shift?"
    assert [len(got[k]) for k in ("frequency_over_the_cap", "per_each", "people_get", "buyer_instead")] == [1, 1, 1, 1]
    assert got["lock_refused"][0]["word"] == "PMS"
    assert len(j.findings) == 5
    clean = SimpleNamespace(entry=codyco, interviews={"Aylin": {"gate": {"question": got["gate"][0]["mirror"]},
                                                               "parts": []}}, findings=[], changed={})
    assert backtest.cloud_131(clean) == {} and clean.findings == []


# ------------------------------------------------------------------------------- FR-3: the fear-held head

FEAR = ("Your fear was the agency owner's approval. 10 of 10 said it was quick or not needed. Not the blocker you "
        "expected.")


def _s014_standings() -> dict:
    """S-014's served box on the 130 build (run 20261024T161428Z): Purchase friction HOLDING_UP, a held line's dissent,
    its card's statusWords the friction line keel-web draws as the pill."""
    key = "commercial.purchase_friction"
    return {"facts": {"cards": [{"key": key, "status": "HOLDING_UP", "statusWords": FEAR, "number": "10 of 10"},
                                {"key": "problem.prevalence", "status": "HOLDING_UP", "statusWords": "Holding up",
                                 "number": "0 of 10"}]},
            "vectors": [{"dimensions": [{"dimension": key, "status": "HOLDING_UP", "n": 10,
                                         "choice": {"optionCounts": [{"code": "yes_quick", "count": 10}]}}]}],
            "insights": [{"dimension": key, "name": "Purchase friction", "status": "HOLDING_UP", "dissent": True,
                          "frame": "Purchase friction held, 0 of 10; the 10 who said no:",
                          "rungHeading": "What did slow it down?"}]}


def test_the_box_pill_is_the_cards_served_word():
    """keel-web `lineWordOf`: the card's served word where its status is the box's -- the fear that did not hold reads
    the card's own line, not *Holding up*; a bar line's served *People disagree* is still *Did not hold*; no card, the
    status's word."""
    from evals import report_marks as rm                                # noqa: PLC0415
    standings = _s014_standings()
    key = "commercial.purchase_friction"
    card, row = standings["facts"]["cards"][0], standings["vectors"][0]["dimensions"][0]
    assert rm.line_word(key, "HOLDING_UP", row, card) == FEAR
    assert rm.expected_box(standings["insights"][0], row, frozenset(), card)["head"] == ["Purchase friction", FEAR]
    assert rm.line_word(key, "HOLDING_UP", row, None) == "Holding up"
    assert rm.line_word(key, "HOLDING_UP", row, {**card, "status": "PEOPLE_DISAGREE"}) == "Holding up"
    split = {"key": "solution.compatibility", "status": "PEOPLE_DISAGREE", "statusWords": "People disagree · a split"}
    assert rm.line_word("solution.compatibility", "PEOPLE_DISAGREE", {"n": 9}, split) == "Did not hold"
    assert rm.pill_words(standings) == [FEAR]


def test_the_pill_is_the_views_own_words_for_d6():
    """D6 on S-014's view: the pill's *10 of 10* is the card's own line drawn again, as the frame's *0 of 10* is the
    view's own line -- no number repeated; a count outside them still is."""
    from evals import report_marks as rm                                # noqa: PLC0415
    standings = _s014_standings()
    text = (f"Purchase friction {FEAR} What did slow it down? Purchase friction held, 0 of 10; the 10 who said no: "
            "finance (9) “Finance wanted written quotes.” — Kate Alder Yes, but it would be quick")
    page = {"text": text, "quotes": ["“Finance wanted written quotes.” — Kate Alder",
                                     "Yes, but it would be quick"],
            "own_lines": ["What did slow it down?", "Purchase friction held, 0 of 10; the 10 who said no:"]}
    assert rm.report_no_repeat({"standings": standings, "insights": page}) == (True, {"repeated": []})
    page["text"] += " 3 of 10 said more"
    assert rm.report_no_repeat({"standings": standings, "insights": page})[0] is False
