"""Spec 085: the harness reads the read-back as keel-cloud 149 writes it -- the sentence in two sentences with a verb
before the job (FR-1, `vectors_script.sentence`, `qualifiers.they`) and the condition code draws keeping the founder's
subject, a list read as one part (FR-2, `qualifiers`, `vectors_script.condition_from`). Stackless: every wording is
149's own pin (`ReadBackReadsOnceTest`, `ReadBackReadsOnceApplierTest`), and the patterns are held to keel-cloud-docs'
sources through `stack.toml`'s sibling paths, so a change there fails here first."""

from __future__ import annotations

import pytest

from harness import qualifiers as q
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

CONFIG = load_config(validate=False)

SEVEN_NIGHTS = vs.Window(7, "NIGHTS")            # keel-cloud `RecallWindow.DEFAULT`
SEVEN_DAYS = vs.Window(7, "DAYS")

#: 149's 08-fresco slots (`ReadBackReadsOnceApplierTest.Fresco`) and the sentence it pins.
FRESCO_CORE = "construction superintendents at US general contractors"
FRESCO_WHEN = "the day's site walks are done and the photos and notes still have to go into the daily log"
FRESCO_WHAT = "keep an accurate record of the day's work on site"
FRESCO_WHICH_PEOPLE = "superintendents at US general contractors whose jobs run on Procore or ACC"
FRESCO_SENTENCE = ("Construction superintendents at US general contractors, who have jobs that run on Procore or ACC. "
                   "When the day's site walks are done and the photos and notes still have to go into the daily log, "
                   "they want to keep an accurate record of the day's work on site, counting the last 5 working days.")

#: 149's 10-palus words (`ReadBackReadsOnceApplierTest.Palus`).
PALUS_WHICH_PEOPLE = ("venture-backed startups in the US within two years of a raise, banking with Mercury, Brex or "
                      "similar")
PALUS_AS_TYPED = f"finance leads at {PALUS_WHICH_PEOPLE}"
PALUS_BANKS = "work at a startup that banks with Mercury, Brex or similar"
PALUS_WHEN = "the company decides where cash from a raise sits until it is needed"
PALUS_WHAT = "keep the money from a raise safe and earning until the company spends it"


def _cloud(path: str) -> str:
    return (CONFIG.keel_cloud / path).read_text()


@pytest.fixture(scope="module")
def corpus():
    fx.canon_entry("01-countly.yaml")
    return corpus_mod.load(CONFIG.keel_cloud).bind(fx.registry())


def _entry(corpus, entry_id: str):
    return next(e for e in corpus.entries if e.id == entry_id)


# ----------------------------------------------------------------- FR-1 the sentence has a verb before the job


def test_lullaby_reads_in_two_sentences():
    """149 `ReadBackReadsOnceTest.lullabyReadsInTwoSentences`, word for word."""
    assert vs.sentence("first-time parents in the US", "have a baby under six months",
                       "the baby cries during the night", "work out what the baby needs and settle the baby",
                       SEVEN_NIGHTS) == (
        "First-time parents in the US, who have a baby under six months. When the baby cries during the night, they "
        "want to work out what the baby needs and settle the baby, counting the last 7 nights.")


def test_the_journeys_lullaby_and_149s_fresco(corpus):
    """03-lullaby as the journeys script it (`SEGMENTS`' core and condition, the corpus's circumstance and job); 08-fresco
    on 149's slots and its condition (`ReadBackReadsOnceApplierTest.Fresco.SENTENCE`)."""
    assert vs.read_back(_entry(corpus, "03-lullaby")) == (
        "First-time parents in the US, who have a baby under six months. When the baby cries in the night, they want "
        "to work out what the baby needs and settle them, counting the last 7 nights.")
    assert vs.sentence(FRESCO_CORE, "have jobs that run on Procore or ACC", FRESCO_WHEN, FRESCO_WHAT,
                       vs.Window(5, "WORKING_DAYS")) == FRESCO_SENTENCE


def test_aircaps_reads_the_job_on_its_own_verb():
    assert vs.sentence("deaf and hard-of-hearing adults in the US", "talk with hearing people every week",
                       "a conversation with hearing people is too fast or too noisy to follow",
                       "follow and join a face-to-face conversation", SEVEN_DAYS) == (
        "Deaf and hard-of-hearing adults in the US, who talk with hearing people every week. When a conversation with "
        "hearing people is too fast or too noisy to follow, they want to follow and join a face-to-face conversation, "
        "counting the last 7 days.")


def test_a_job_with_a_want_of_its_own_takes_they_alone():
    assert vs.sentence("finance leads at venture-backed startups", None,
                       "the company decides where cash from a raise sits", "need to keep the money safe", None) == (
        "Finance leads at venture-backed startups. When the company decides where cash from a raise sits, they need to "
        "keep the money safe.")
    for job, said in (("want to keep the money safe", "they want to keep the money safe"),
                      ("try to keep the money safe", "they try to keep the money safe"),
                      ("have to keep the money safe", "they have to keep the money safe"),
                      ("must keep the money safe", "they must keep the money safe"),
                      ("needs to keep the money safe", "they need to keep the money safe"),
                      ("has to keep the money safe", "they have to keep the money safe"),
                      ("tries to keep the money safe", "they try to keep the money safe"),
                      ("trying to keep the money safe", "they are trying to keep the money safe"),
                      ("are trying to keep the money safe", "they are trying to keep the money safe"),
                      ("they keep the money safe", "they keep the money safe"),
                      ("to keep the money safe", "they want to keep the money safe"),
                      ("keep the money safe", "they want to keep the money safe"),
                      ("mustard the hot dogs", "they want to mustard the hot dogs")):
        assert q.they(job) == said, job


def test_while_keeps_its_word_raised_and_money_alone_reads_no_window():
    assert vs.sentence("payroll practitioners", None, "while running payroll", "get the numbers right", None) == \
        "Payroll practitioners. While running payroll, they want to get the numbers right."
    assert vs.sentence("first-time parents in the US", "have a baby under six months",
                       "the baby cries during the night", "work out what the baby needs and settle the baby",
                       None) == ("First-time parents in the US, who have a baby under six months. When the baby cries "
                                 "during the night, they want to work out what the baby needs and settle the baby.")


def test_the_segment_keeps_a_conditions_own_pronoun():
    """148 FR-2 (`ReadBack.segment`, `ReadBackOwnPronounTest`), mirrored with 149: a condition that opens with *whose*,
    *that* or *which* keeps it after a comma; after a core's own *who* clause it is joined by *and*; the segment line is
    the same whole (`ContextSlots.segmentLine` reads `ReadBack.segment`)."""
    assert q.segment("insurance adjusters", "whose work is documented in digital systems") == \
        "insurance adjusters, whose work is documented in digital systems"
    assert q.segment("people in Pakistan who earn in rupees", "whose savings are in rupees") == \
        "people in Pakistan who earn in rupees and whose savings are in rupees"
    assert q.segment("insurance adjusters", "who settle claims") == "insurance adjusters, who settle claims"
    assert q.segment_line("insurance adjusters", "whose work is documented in digital systems") == \
        "insurance adjusters, whose work is documented in digital systems"
    assert q.segment_line("people in Pakistan who earn in rupees", "have no foreign currency account") == \
        "people in Pakistan who earn in rupees and have no foreign currency account"


def test_the_sentence_mirror_reads_the_clouds_read_back():
    """FR-1's patterns and joins are 149's, held to `ReadBack.java`."""
    source = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/ReadBack.java")
    assert 'out.append(". ").append(upperFirst(withWhen(when))).append(", ").append(they(what));' in source
    assert '"(?i)^(?:(?:want|need|try|have)\\\\s+to|must)\\\\s.*"' in source
    assert '"(?i)^(wants|needs|tries|has)\\\\s+to\\\\s+(.*)$"' in source
    assert '"(?i)^(?:are\\\\s+)?trying\\\\s+to\\\\s+(.*)$"' in source
    assert 'return "they want " + job;' in source and 'return "they want to " + job;' in source
    assert '"(?i)^(?:whose|that|which)\\\\s.*"' in source
    slots = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/ContextSlots.java")
    assert "return ReadBack.segment(segment, segmentCondition);" in slots
