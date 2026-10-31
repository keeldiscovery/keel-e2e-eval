"""Spec 111 (keel-cloud 176, `FoundersOwnNamesTest`): the harness's M5 mirror lets the parenthesis, list and
design-note rules yield to the founder's seed -- a parenthesis or a list whose every name stands whole in the founder's
texts (split on commas and *or* / *and*), and a design note whose phrase to the end of its clause was typed, are the
founder's -- and the reveal is said for the ear as keel-cloud's `RevealWords.aloud` says it: a parenthesis of names
*such as A, B or C*, a list past five *A, B and others*. Stackless."""

from __future__ import annotations

import re
from pathlib import Path

from evals import corpus_scenario as cs
from evals import interviewer_marks as im
from harness import interviewer_fake as fake
from instructions import corpus as corpus_mod
from instructions import spoken
from quality import readers
from tests.test_after_131 import FRAME, KEEL_CLOUD, _backtest, _refusal_body, keels_words

#: keel-cloud 176 `support/FoundersNames`: Codyco's and Pairio's how lines keeping their seeds' names.
CODYCO_HOW = ("You forward the calls nobody picks up to Codyco. Codyco answers in the hotel's voice, takes the payment "
              "and writes the confirmed booking straight into the PMS (OPERA Cloud, Sihot, Apaleo), handing a call to "
              "the desk by rules the hotel sets.")
PAIRIO_HOW = ("You ask Pairio by voice or with a photo at the machine, and it answers from the manuals; then you speak "
              "the fix and Pairio turns it into a fault report, connected to SAP, Maximo or SharePoint.")
PAIRIO_LIST_ROWS = ["connected to SAP, Maximo or SharePoint", "to SAP, Maximo or SharePoint",
                    "SAP, Maximo or SharePoint"]


def _texts(entry_id: str):
    return corpus_mod.founder_texts(_backtest(entry_id))


# ------------------------------------------------------------------------------- the reading of names and clauses

def test_names_split_on_commas_and_or_and():
    """`RevealWords.names`: commas, *or*, *and*, an Oxford comma before them -- each name whole."""
    assert corpus_mod.names_of("OPERA Cloud, Sihot, Apaleo") == ["OPERA Cloud", "Sihot", "Apaleo"]
    assert corpus_mod.names_of("SAP, Maximo or SharePoint") == ["SAP", "Maximo", "SharePoint"]
    assert corpus_mod.names_of("SAP, Maximo, and SharePoint") == ["SAP", "Maximo", "SharePoint"]
    assert corpus_mod.names_of("Procore and ACC") == ["Procore", "ACC"]
    assert corpus_mod.names_of("") == []


def test_a_clause_runs_to_its_next_comma_stop_or_bracket():
    """`RevealWords.toClauseEnd`: from the note's start to the next `, ; : . ! ? ( )`, else the line's end."""
    text = FRAME + "do the calling the way the staff would, without an integration project."
    at = text.index("without")
    assert corpus_mod.to_clause_end(text, at) == "without an integration project"
    assert corpus_mod.to_clause_end("use cheap charging pads along the lines", 0) == \
        "use cheap charging pads along the lines"


# ------------------------------------------------------------------------------- the parenthesis

def test_codycos_parenthesis_as_typed_is_no_fault():
    """`codycoCardWithItsParenthesisAsTypedHasNoM5Breach...`, mirrored: on 21-codyco's own texts the card that keeps
    its seed's *PMS (OPERA Cloud, Sihot, Apaleo)* has no M5 fault at all; without the texts the rule still fires."""
    texts = _texts("21-codyco")
    lines = {"how": CODYCO_HOW, "belief": FRAME + "turn the calls that ring out into bookings."}
    assert corpus_mod.m5_faults(lines, founder_texts=texts) == []
    assert [(f["fault"], f["word"]) for f in corpus_mod.m5_faults(lines)] == [
        ("trade word", "PMS"), ("names in parentheses", "(OPERA Cloud, Sihot, Apaleo)")]


def test_a_parenthesis_with_one_keel_name_is_a_fault():
    """`aParenthesisKeelIntroducedIsRefusedNamingItAndNotOneTheFounderTyped`: *Mews* is Keel's, so the parenthesis is
    the line's fault, named whole -- the founder's *OPERA Cloud* and *Apaleo* beside it do not make it theirs."""
    keels = CODYCO_HOW.replace("(OPERA Cloud, Sihot, Apaleo)", "(OPERA Cloud, Mews, Apaleo)")
    assert corpus_mod.m5_faults({"how": keels}, founder_texts=_texts("21-codyco")) == [
        {"line": "how", "word": "(OPERA Cloud, Mews, Apaleo)", "fault": "names in parentheses"}]


def test_the_rule_reads_past_the_founders_parenthesis():
    """176 T001 (its *did not foresee* 4): the rule reads every parenthesis of the line, skips the founder's, and the
    first one left is the line's one fault."""
    how = "It writes into the PMS (OPERA Cloud, Sihot, Apaleo) and texts the guest (WhatsApp, Signal)."
    faults = corpus_mod.m5_faults({"how": how}, founder_texts=_texts("21-codyco"))
    assert faults == [{"line": "how", "word": "(WhatsApp, Signal)", "fault": "names in parentheses"}]


# ------------------------------------------------------------------------------- the list

def test_pairios_list_as_typed_is_no_edit_and_its_rows_stand_down():
    """`pairioListAsTypedIsAccepted`, mirrored: 16-pairio's seed types *SAP, Maximo or SharePoint*, so the edit leaves
    the list as typed (no edit: None) and its three list rows do not fire; its *CMMS* / *ERP* rows do."""
    pairio = _backtest("16-pairio")
    typed = corpus_mod.founder_texts(pairio)
    assert corpus_mod.typed_whole(corpus_mod.names_of("SAP, Maximo or SharePoint"), typed)
    assert corpus_mod.plain_line(pairio, "how", PAIRIO_HOW, "SAP, Maximo or SharePoint") is None
    fired = [p for p, _ in corpus_mod.LOCK_PLAIN_WORDS["16-pairio"] if corpus_mod._row_fires(p, typed)]
    assert fired == ["CMMS", "ERP"]
    moved = corpus_mod.plain_line(pairio, "how", PAIRIO_HOW.replace("a fault report", "a CMMS fault report"), "CMMS")
    assert "CMMS" not in moved and moved.endswith("connected to SAP, Maximo or SharePoint.")


def test_a_list_keel_brought_in_is_still_moved():
    """`aListKeelIntroducedIsRefusedAtTheLockNamingIt`: *SAP, Oracle or Fiix* beside the founder's *SAP* is Keel's list
    and the edit keeps one name; on a Pairio seed without its three names the list rows fire again, all five."""
    pairio = _backtest("16-pairio")
    keels = PAIRIO_HOW.replace("SAP, Maximo or SharePoint", "SAP, Oracle or Fiix")
    assert corpus_mod.plain_line(pairio, "how", keels, "SAP, Oracle or Fiix") == \
        PAIRIO_HOW.replace("SAP, Maximo or SharePoint", "SAP")
    unnamed = keels_words(pairio, "SAP", "Maximo", "SharePoint")
    typed = corpus_mod.founder_texts(unnamed)
    assert [p for p, _ in corpus_mod.LOCK_PLAIN_WORDS["16-pairio"] if corpus_mod._row_fires(p, typed)] == \
        [*PAIRIO_LIST_ROWS, "CMMS", "ERP"]
    assert corpus_mod.plain_line(unnamed, "how", PAIRIO_HOW, "SAP, Maximo or SharePoint") == \
        PAIRIO_HOW.replace("connected to SAP, Maximo or SharePoint", "connected to your maintenance system")


# ------------------------------------------------------------------------------- the design note

def test_a_design_note_the_founder_typed_is_theirs_and_a_lone_verb_is_not():
    """`aDesignNoteTheFounderTypedIsTheirsAndALoneVerbIsNot`, word for word: Karsa's *no jargon* where the seed types
    *with no jargon*; a seed's *use* never exempts *use cheap charging pads along the lines*, the whole phrase does."""
    karsa = {"how": "You pay a verified local seller.", "belief": FRAME + "need no jargon."}
    seed = "An app that looks like a currency exchange: the saver pays a verified local seller, with no jargon."
    assert [f["word"] for f in corpus_mod.m5_faults(karsa)] == ["no jargon"]
    assert corpus_mod.m5_faults(karsa, founder_texts=[seed]) == []
    pads = {"how": "You charge on the way.", "belief": "use cheap charging pads along the lines"}
    assert corpus_mod.m5_faults(pads, founder_texts=["Drones use the grid; we use the lines."]) == [
        {"line": "belief", "word": "use", "fault": "design note"}]
    assert corpus_mod.m5_faults(pads, founder_texts=["Our drones use cheap charging pads along the lines."]) == []


def test_careforces_typed_note_is_no_fault_and_no_edit_and_keels_is_both():
    """18-careforce's seed types *without an integration project*: the note is the founder's (no fault, no edit); on a
    seed without the phrase it is Keel's -- the fault, and the edit to the entry's first benefit."""
    careforce = _backtest("18-careforce")
    belief = FRAME + "do the calling the way the staff would, without an integration project."
    assert corpus_mod.m5_faults({"belief": belief}, founder_texts=corpus_mod.founder_texts(careforce)) == []
    assert corpus_mod.plain_line(careforce, "belief", belief, "without an integration project") is None
    keels = keels_words(careforce, "without an integration project")
    assert [f["word"] for f in corpus_mod.m5_faults({"belief": belief},
                                                   founder_texts=corpus_mod.founder_texts(keels))] == \
        ["without an integration project"]
    assert corpus_mod.plain_line(keels, "belief", belief, "without an integration project") == \
        FRAME + "get patients reached without calling back again and again."


def test_codycos_note_is_keels_to_its_clauses_end():
    """107's Codyco re-pin, held here too: *need no change to the front desk* is not in Codyco's seed -- the one fault
    left on that card is the design note."""
    faults = corpus_mod.m5_faults({"how": CODYCO_HOW, "belief": FRAME + "need no change to the front desk."},
                                  founder_texts=_texts("21-codyco"))
    assert faults == [{"line": "belief", "word": "need no change", "fault": "design note"}]


# ------------------------------------------------------------------------------- FR-4: fewer lock_refused findings

def test_codyco_and_pairio_cards_as_typed_meet_no_refusal():
    """FR-4: the cards that keep the seeds' names draw no M5 fault on their own texts, so a back-test walk meets no
    lock refusal for them and records no `lock_refused` finding -- the spec working. A refusal Keel's words still draw
    (Pairio's *CMMS*) is answered on that word alone, the founder's list kept."""
    assert corpus_mod.m5_faults({"how": CODYCO_HOW}, founder_texts=_texts("21-codyco")) == []
    assert corpus_mod.m5_faults({"how": PAIRIO_HOW}, founder_texts=_texts("16-pairio")) == []
    pairio = _backtest("16-pairio")
    lines = {"how": PAIRIO_HOW.replace("a fault report", "a CMMS fault report"), "belief": FRAME + "get it back up."}
    edits = []

    def edit(e):
        edits.append(e)
        lines.update(e)
    out = cs.answer_refused_lock(cs.lock_refusal(422, _refusal_body("how", "CMMS")), entry=pairio,
                                 read_lines=lambda: dict(lines), edit=edit,
                                 relock=lambda: {"status": 200, "receipt": {"version": 1}})
    assert out["passes"] == 1 and [f["word"] for f in out["findings"]] == ["CMMS"]
    assert "connected to SAP, Maximo or SharePoint." in edits[0]["how"] and "CMMS" not in edits[0]["how"]


# ------------------------------------------------------------------------------- FR-3: the reveal said aloud

def test_the_spoken_cap_is_keel_clouds_own():
    """`RevealWords.SPOKEN_NAMES_MAX = SpokenForm.MAX_OPTIONS` (5), read off keel-cloud's source."""
    src = KEEL_CLOUD / "src/main/java/com/keeldiscovery/cloud/domain"
    reveal = (src / "project/RevealWords.java").read_text()
    form = (src / "vectors/SpokenForm.java").read_text()
    assert re.search(r"SPOKEN_NAMES_MAX\s*=\s*com\.keeldiscovery\.cloud\.domain\.vectors\.SpokenForm\.MAX_OPTIONS",
                     reveal)
    assert re.search(r"MAX_OPTIONS\s*=\s*5;", form)
    assert spoken.SPOKEN_NAMES_MAX == spoken.MAX_OPTIONS == 5


def test_a_typed_parenthesis_is_said_such_as():
    """`theSpokenFormReadsOnlyTheNamesShape` and Codyco's clip: *such as A, B or C*, a closing comma where the sentence
    goes on; one name set off by commas; a lower-case parenthesis as typed; a plain line unchanged."""
    aloud = spoken.reveal_aloud
    assert "straight into the PMS, such as OPERA Cloud, Sihot or Apaleo, handing a call to the desk" in aloud(CODYCO_HOW)
    assert aloud("into the PMS (OPERA Cloud, Sihot, Apaleo).") == "into the PMS, such as OPERA Cloud, Sihot or Apaleo."
    assert aloud("the hotel's booking system (OPERA Cloud) takes it.") == \
        "the hotel's booking system, OPERA Cloud, takes it."
    assert aloud("a call center (or a front desk) picks up") == "a call center (or a front desk) picks up"
    assert aloud("You upload the pay register.") == "You upload the pay register."
    assert aloud(PAIRIO_HOW) == PAIRIO_HOW


def test_a_list_past_five_is_said_two_and_others():
    """`aKeptListOverTheSpokenCapSaysTwoAndAndOthers`: six names in a parenthesis or bare are the first two and *and
    others*; five are said whole."""
    aloud = spoken.reveal_aloud
    six = CODYCO_HOW.replace("(OPERA Cloud, Sihot, Apaleo)", "(OPERA Cloud, Sihot, Apaleo, Mews, Protel, Cloudbeds)")
    said = aloud(six)
    assert "into the PMS, such as OPERA Cloud, Sihot and others, handing" in said
    assert "Apaleo" not in said and "(" not in said
    assert aloud("connected to SAP, Maximo, SharePoint, Fiix, Limble or UpKeep.") == "connected to SAP, Maximo and others."
    assert aloud("connected to SAP, Maximo, SharePoint, Fiix or Limble.") == \
        "connected to SAP, Maximo, SharePoint, Fiix or Limble."


def test_the_solution_clip_mirror_says_the_names_aloud():
    """`PassageComposer.idea` / `aloud`: the fake's idea passage and the problem sentence before *Now the idea.* say
    the parenthesis *such as*, never a bracket; a spaced double dash is still a comma."""
    passage = fake.idea_passage("It is called Codyco.", CODYCO_HOW, FRAME + "turn the calls that ring out into bookings.")
    assert "straight into the PMS, such as OPERA Cloud, Sihot or Apaleo, handing" in passage
    assert "(" not in passage and passage.endswith("into bookings.")
    problem = "Hotels lose the calls their PMS (OPERA Cloud, Sihot, Apaleo) never sees -- after hours."
    assert fake.solution_opening(problem) == ("Hotels lose the calls their PMS, such as OPERA Cloud, Sihot or Apaleo, "
                                              "never sees, after hours. Now the idea.")


def test_im4_reads_the_how_as_the_clip_says_it():
    """IM4 on a how of six typed names: the clip says *OPERA Cloud, Sihot and others*, which IM4 measures against the
    how as said -- not the four names the clip, by keel-cloud 176, leaves unsaid."""
    first = "Codyco writes the booking into the PMS (OPERA Cloud, Sihot, Apaleo, Mews, Protel, Cloudbeds)."
    belief = FRAME + "turn the calls that ring out into bookings."
    script = " ".join([fake.solution_opening(), fake.idea_passage("It is called Codyco.", first, belief),
                       fake.solution_close(3)])
    ok, out = im.solution_three_facts({"idea": {"name": "Codyco", "how": first, "belief": belief},
                                       "recording": {"clips": [{"kind": "SOLUTION", "role": "PRIMARY",
                                                                "script": script}]}})
    assert ok, out
    assert "such as OPERA Cloud, Sihot and others" in script and "Cloudbeds" not in script
    claim = fake.first_sentence(first)
    assert im._coverage(claim, script) < im.COVERAGE, "the how as typed would have failed IM4 on the clip as said"


def test_the_readers_reveal_screen_says_the_names_aloud():
    """The quality readers' reveal screen: the card is drawn as typed, and the line the AI interviewer says reads the
    parenthesis *such as ...*."""
    card = "Codyco\n" + CODYCO_HOW
    bundle = {"respondents": {"PRIMARY": {"served": {}, "drawn": [{"screen": "reveal", "kicker": "The idea",
                                                                   "card": card}]}}}
    [screen] = readers.respondent_screens(bundle)["PRIMARY"]
    assert "(OPERA Cloud, Sihot, Apaleo)" in screen.full
    assert "such as OPERA Cloud, Sihot or Apaleo, handing" in screen.said and "(" not in screen.said


def test_the_spoken_mirror_is_keel_clouds_source():
    """The ported pieces stand in keel-cloud's source as mirrored: `aloud`'s *such as*, `spokenList`'s *and others*,
    `names`' split, `toClauseEnd`'s stops, and `PassageComposer` reading the idea and the problem through `aloud`."""
    root = Path(KEEL_CLOUD) / "src/main/java/com/keeldiscovery/cloud"
    reveal = (root / "domain/project/RevealWords.java").read_text()
    composer = (root / "application/interviewer/PassageComposer.java").read_text()
    assert '"such as " + spokenList(listed, "or")' in reveal
    assert '" and others"' in reveal
    assert 'split("\\\\s*,\\\\s*(?:(?:or|and)\\\\s+)?|\\\\s+(?:or|and)\\\\s+")' in reveal
    assert 'Pattern.compile("[,;:.!?()]")' in reveal
    assert "join(sentence(aloud(what)), sentence(aloud(how)), sentence(aloud(belief)))" in composer
    assert composer.count("aloud(reveal.problem())") == 2 and "aloud(interview.idea().problem())" in composer
