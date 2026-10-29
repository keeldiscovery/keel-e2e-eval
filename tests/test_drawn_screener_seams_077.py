"""Spec 077: the harness follows keel-cloud 146 (the drawn screener's seams) -- 07-mulchrun's place drawn whole by code
(FR-1), a qualifier said once in the read-back and the segment line (FR-2), the decision-maker's chip naming the people
once (FR-3, DRIFT #99 closed), and "when" once (FR-4). Stackless: every wording is 146's own pin
(`DrawnScreenerSeamsTest`), and the rules are held to keel-cloud-docs' sources through `stack.toml`'s sibling paths."""

from __future__ import annotations

import pytest

from evals import corpus_scenario as cs
from harness import qualifiers as q
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

CONFIG = load_config(validate=False)

#: S-007's founder's WHICH PEOPLE (and the cloud test's `DFW`).
DFW = "landscaping crew leads in the Dallas-Fort Worth suburbs, spring season"


def _cloud(path: str) -> str:
    return (CONFIG.keel_cloud / path).read_text()


@pytest.fixture(scope="module")
def corpus():
    fx.canon_entry("01-countly.yaml")
    return corpus_mod.load(CONFIG.keel_cloud).bind(fx.registry())


def _entry(corpus, entry_id: str):
    return next(e for e in corpus.entries if e.id == entry_id)


# ----------------------------------------------------------------- FR-1 07-mulchrun carries a code-drawn screener


def test_mulchrun_carries_the_place_code_draws_and_the_fake_writes_none(corpus):
    """146 FR-1: the cloud draws *are based in the Dallas-Fort Worth suburbs* on the confirm (the scripted
    CONTEXT_INTERPRET writes the core alone); the part-1 job, handed it, writes the chip 146 pins, YES inside."""
    mulch = _entry(corpus, "07-mulchrun")
    assert vs.scripted_segment(mulch) == {"core": DFW, "condition": None}
    assert vs.context_result(mulch)["segment"] == {"core": DFW, "condition": None}
    assert vs.segment_of(mulch) == {"core": DFW, "condition": "are based in the Dallas-Fort Worth suburbs"}
    assert vs.chip_of(mulch) == {"question": "Are you based in the Dallas-Fort Worth suburbs?", "inside": "YES"}
    assert vs.respondent_result(mulch, 1, vs.LINK_PRIMARY)["condition"] == vs.chip_of(mulch)
    assert DFW == mulch.context["segment"], "the row's core is the founder's WHICH PEOPLE, as the fake writes it"
    for entry in corpus.entries:
        if entry.id not in vs.DRAWN:
            assert vs.scripted_segment(entry) == vs.segment_of(entry), entry.id
    source = _cloud("src/test/java/com/keeldiscovery/cloud/application/DrawnScreenerSeamsTest.java")
    assert 'isEqualTo("are based in the Dallas-Fort Worth suburbs")' in source
    assert '.isEqualTo("Are you based in the Dallas-Fort Worth suburbs?")' in source


def test_mulchrun_sentence_after_confirm_is_the_cards(corpus):
    """146 FR-2 on S-007: the core keeps the place, so the confirmed sentence is the card's word for word -- no *, who
    are based in ...* (the thorough pass's red at the confirm step); the segment line is the core alone. Re-pinned by
    spec 085 to keel-cloud 149's two sentences (the job after *they want to*): the rule pinned here did not move."""
    mulch = _entry(corpus, "07-mulchrun")
    card = vs.read_back(mulch)
    assert card == vs.read_back(mulch, confirmed=True) == (
        "Landscaping crew leads in the Dallas-Fort Worth suburbs, spring season. When a job needs mulch and the crew has "
        "to fetch it from the supply yard, they want to get the mulch onto the beds and the crew onto the next job, "
        "counting the last 2 weeks.")
    assert "who are based" not in card
    assert vs.segment_line(mulch) == DFW


def test_the_card_draws_the_settled_condition(corpus):
    """Spec 084 (keel-cloud 148 FR-1): the card's *Only people who:* line is the settled condition -- on 07 the one code
    draws (the confirmed segment's, though the result writes none); elsewhere the scripted one, as before."""
    mulch = _entry(corpus, "07-mulchrun")
    assert vs.card_condition(mulch) == "are based in the Dallas-Fort Worth suburbs" == vs.segment_of(mulch)["condition"]
    assert vs.scripted_segment(mulch)["condition"] is None
    paidly = _entry(corpus, "05-paidly")
    assert vs.card_condition(paidly) == "work mostly for agencies" == vs.scripted_segment(paidly)["condition"]


# ----------------------------------------------------------------- FR-2 a qualifier is said once


def test_in_core_holds_146s_own_pins():
    """146 `DrawnScreenerSeamsTest.Fr2*`, mirrored: a core that keeps the part takes no clause; one that lost it does.
    The sentences re-pinned by spec 085 to keel-cloud 149's shape (as 149 re-pinned `DrawnScreenerSeamsTest`)."""
    window = vs.Window(3, "MONTHS")
    assert q.in_core(DFW, "are based in the Dallas-Fort Worth suburbs")
    assert q.in_core("payroll practitioners who run payroll for at least 50 employees",
                     "run payroll for at least 50 employees")
    assert q.in_core("payroll managers at companies with at least 50 employees",
                     "work at a company with at least 50 employees"), "code's frame is not the founder's words"
    assert q.in_core("nurses in Texas", "work in Texas"), "the model's condition naming the core's qualifier"
    assert not q.in_core("Freelance translators in the US", "work mostly for agencies")
    assert not q.in_core("payroll practitioners who run payroll", "run payroll for at least 50 employees"), \
        "a number the core lacks"
    assert not q.in_core("people with a foreign currency account", "have no foreign currency account"), \
        "a negation the core lacks"
    assert vs.sentence("payroll practitioners who run payroll for at least 50 employees",
                       "run payroll for at least 50 employees", "they run payroll", "run payroll without errors",
                       window) == ("Payroll practitioners who run payroll for at least 50 employees. When they run "
                                   "payroll, they want to run payroll without errors, counting the last 3 months.")
    assert vs.sentence("Freelance translators in the US", "work mostly for agencies", "a job comes in", "quote for it",
                       window) == ("Freelance translators in the US, who work mostly for agencies. When a job comes "
                                   "in, they want to quote for it, counting the last 3 months.")
    assert vs.sentence("people in Pakistan who earn in rupees", "have no foreign currency account", "the rupee falls",
                       "move their savings", window).startswith(
        "People in Pakistan who earn in rupees and have no foreign currency account. When")
    assert ", who have no foreign currency account. When" in vs.sentence(
        "people with a foreign currency account", "have no foreign currency account", "the rupee falls",
        "move their savings", window)


def test_the_rule_reads_core_and_condition_alone():
    """146 judgement call 1: Issen's *not starting from zero* against *are past the beginner stage* shares no words,
    so the clause is still added."""
    core = "adults learning a language at intermediate level or above, not starting from zero"
    assert not q.in_core(core, "are past the beginner stage")
    assert q.segment(core, "are past the beginner stage").endswith(", who are past the beginner stage")


def test_the_journeys_read_backs_and_segment_lines(corpus):
    """FR-2 on the corpus: 05-paidly's line unchanged (the core lost the qualifier); 01-05 keep their clauses; 06 and
    07 have none to add. The read-back re-pinned by spec 085 (keel-cloud 149: the segment its own sentence)."""
    paidly = _entry(corpus, "05-paidly")
    assert vs.segment_line(paidly) == "freelance translators in the US, who work mostly for agencies"
    assert vs.read_back(paidly).startswith("Freelance translators in the US, who work mostly for agencies. When an "
                                           "agency has approved the invoice")
    for entry_id in ("01-countly", "02-compliancelog", "03-lullaby", "04-linerly", "05-paidly"):
        entry = _entry(corpus, entry_id)
        seg = vs.segment_of(entry)
        assert vs.segment_line(entry) == f"{seg['core']}, who {seg['condition']}", entry_id
    assert vs.segment_line(_entry(corpus, "06-repeatline")) == _entry(corpus, "06-repeatline").context["segment"]


def test_the_segment_line_keeps_its_own_join():
    """146 judgement call 3 (`ContextSlots.segmentLine`): the core alone where it says the condition, else *, who*."""
    assert q.segment_line("payroll practitioners who run payroll for at least 50 employees",
                          "run payroll for at least 50 employees") == \
        "payroll practitioners who run payroll for at least 50 employees"
    assert q.segment_line("freelance translators in the US", "work mostly for agencies") == \
        "freelance translators in the US, who work mostly for agencies"
    assert q.segment_line("x", None) == "x"


def test_the_mirror_reads_the_clouds_patterns():
    """The patterns are 146's, held to `Qualifiers.java` and `ReadBack.java` so a change there fails here first."""
    source = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/Qualifiers.java")
    assert '"|(?-i:\\\\bin (?:the )?[A-Z][\\\\w.]*)"' in source
    assert '"(?i)\\\\s(?:who|whose|that|which|in|at|with|of|from|across|on|for)\\\\b"' in source
    assert '"(?i)^(?:who\\\\s+)?(?:are\\\\s+based\\\\s+in|works?\\\\s+at(?:\\\\s+an?)?|are|is|have|has)\\\\s+"' in source
    assert "lost.size() <= FounderWords.MOST_DROPPED && kept > lost.size()" in source
    assert 'people.replaceAll("(?i)\\\\b(\\\\w{3,}?)ing\\\\b", "$1")' in source
    read_back = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/ReadBack.java")
    assert '"(?i)^(?:while|when|whenever|during|as)\\\\b.*"' in read_back
    assert "Qualifiers.inCore(segment, who)" in read_back
    words = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/FounderWords.java")
    assert "public static final int MOST_DROPPED = 1;" in words


def test_founder_words_mirror():
    assert q.stem("calls") == q.stem("call") and q.stem("agencies") == "agency"[:5]
    assert q.dropped("work mostly for agencies", "freelance translators work for agencies") == ["mostly"]
    assert q.negation_dropped("have no account", "people with an account")
    assert not q.negation_dropped("have no account", "people with no account")


# ----------------------------------------------------------------- FR-3 the decision-maker's chip names the people once


def test_the_decision_makers_chip_holds_146s_four_shapes():
    """146 `DrawnScreenerSeamsTest.Fr3*`, mirrored: cut, cut at the qualifier's own preposition, whole, *the people*,
    and the organisation's as 145 wrote it."""
    assert vs.decider_chip("run payroll for at least 50 employees",
                           "payroll practitioners who run payroll for at least 50 employees") == \
        "Do the payroll practitioners you decide for run payroll for at least 50 employees?"
    assert vs.decider_chip("are past the beginner stage", "language learners at intermediate level or above") == \
        "Are the language learners you decide for past the beginner stage?"
    assert vs.decider_chip("use a baby monitor at night", "parents of babies under six months") == \
        "Do the parents of babies under six months you decide for use a baby monitor at night?"
    assert vs.decider_chip("work mostly for agencies", "freelance translators working for agencies") == \
        "Do the people you decide for work mostly for agencies?"
    assert vs.decider_chip("work at a company with at least 50 employees",
                           "payroll managers at companies with at least 50 employees") == \
        "Does your company have at least 50 employees?"
    assert vs.decider_chip("are based in the Dallas-Fort Worth suburbs",
                           "landscaping crew leads in the Dallas-Fort Worth suburbs") == \
        "Are the landscaping crew leads you decide for based in the Dallas-Fort Worth suburbs?"
    assert vs.decider_chip("work mostly for agencies", None) == "Do the people you decide for work mostly for agencies?"
    source = _cloud("src/test/java/com/keeldiscovery/cloud/application/DrawnScreenerSeamsTest.java")
    assert 'isEqualTo("Do the people you decide for work mostly for agencies?")' in source
    rules = _cloud("src/main/java/com/keeldiscovery/cloud/application/RespondentQuestionsRules.java")
    assert "static String deciderPeople(String clause, String actorPlural)" in rules


def test_head_and_says():
    """146 FR-3's two helpers on the journeys' plurals and 146's own."""
    assert q.head("landscaping crew leads in the Dallas suburbs") == "landscaping crew leads"
    assert q.head("learners at intermediate level") == "learners", "judgement call 5: the qualifier's own preposition"
    assert q.head("freelance translators working for agencies") is None
    assert q.head("parents of babies under six months") is None
    assert q.head("who run payroll") is None, "no word before the qualifier"
    assert q.says("freelance translators working for agencies", "work mostly for agencies"), \
        "judgement call 4: one word of difference, working read as work"
    assert not q.says("payroll practitioners", "run payroll for at least 50 employees"), "the number is missing"
    assert not q.says("language learners", "are past the beginner stage")


def test_which_journey_entries_serve_the_decision_makers_screener(corpus):
    """Spec 077: 05-paidly's decision-makers are served *the people* (DRIFT #99 closed), and 07-mulchrun -- SOMEONE_ELSE,
    its condition now drawn by code -- serves the cut shape on S-007's decision-makers' links."""
    served = {e.id: vs.decider_condition(e) for e in corpus.entries}
    assert [k for k, v in served.items() if v] == ["05-paidly", "07-mulchrun"]
    assert served["05-paidly"] == {"question": "Do the people you decide for work mostly for agencies?",
                                   "inCodes": ["YES"]}
    assert served["07-mulchrun"] == {"question": "Are the landscaping crew leads you decide for based in the "
                                                 "Dallas-Fort Worth suburbs?", "inCodes": ["YES"]}
    for want in served.values():
        if want:
            assert want["question"].startswith(("Do the ", "Are the ")) and " you decide for " in want["question"]
            assert len(want["question"].split()) <= vs.STEM_MAX_WORDS


# ----------------------------------------------------------------- FR-4 "when" once


def test_when_once_on_every_line():
    """146 `DrawnScreenerSeamsTest.Fr4*`, mirrored: the three lines on *while running payroll* and on *the payroll
    run*; the five conjunctions of 145 and no more. The sentence re-pinned by spec 085 to keel-cloud 149's (the
    circumstance's first letter raised, the job after *they want to*)."""
    assert q.default_about("while running payroll") == "what it is like while running payroll"
    assert q.default_about("the payroll run") == "what it is like when the payroll run"
    assert q.interview_topic("Athul", "payroll practitioners", "while running payroll") == \
        "Athul is exploring what it is like for payroll practitioners while running payroll."
    assert q.interview_topic("Athul", "payroll practitioners", "the payroll run") == \
        "Athul is exploring what it is like for payroll practitioners when the payroll run."
    assert vs.sentence("payroll practitioners", None, "while running payroll", "get the numbers right", None) == \
        "Payroll practitioners. While running payroll, they want to get the numbers right."
    assert vs.sentence("payroll practitioners", None, "the payroll run", "get the numbers right", None) == \
        "Payroll practitioners. When the payroll run, they want to get the numbers right."
    assert vs.sentence("payroll practitioners", None, "when the payroll runs", "get it right", None) == \
        "Payroll practitioners. When the payroll runs, they want to get it right."
    for c in ("while", "when", "whenever", "during", "as"):
        assert q.with_when(f"{c} it happens") == f"{c} it happens"
    for c in ("after", "before", "once", "if", "assembling"):
        assert q.with_when(f"{c} it happens") == f"when {c} it happens"


def test_no_journey_circumstance_opens_with_a_conjunction(corpus):
    """FR-4: no corpus entry's circumstance opens with one today, so every journey's line keeps its *when* -- since
    keel-cloud 149 (spec 085) the second sentence's *When*."""
    for entry in corpus.entries:
        assert not q.OPENS_WITH_CONJUNCTION.match(entry.context["circumstance"]), entry.id
        assert f". When {entry.context['circumstance']}, they " in vs.read_back(entry), entry.id


# ----------------------------------------------------------------- the confirm step


def test_the_confirm_step_holds_the_stored_condition():
    """FR-1 on the wire: the confirmed context's `segment.condition` is the condition code drew (07) or the model's
    kept (01-05); a context that serves none holds none."""
    assert cs.confirmed_segment_faults({"segment": {"core": DFW, "condition": "are based in the Dallas-Fort Worth "
                                                                              "suburbs"}},
                                       {"core": DFW, "condition": "are based in the Dallas-Fort Worth suburbs"}) == []
    assert cs.confirmed_segment_faults({"segment": {"core": DFW, "condition": "are based in the Dallas"}},
                                       {"core": DFW, "condition": "are based in the Dallas-Fort Worth suburbs"})
    assert cs.confirmed_segment_faults({"segment": {"core": "x"}}, {"core": "x", "condition": None}) == []
