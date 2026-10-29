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


# ----------------------------------------------------------------- FR-2 the drawn condition keeps its subject


def _founders_people(entry_id: str) -> str:
    """The founder's WHICH PEOPLE as the back-test entry records it (`context.segment`), read as plain YAML."""
    import yaml                                                        # noqa: PLC0415
    path = corpus_mod.backtest_dir(CONFIG.keel_cloud) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))["context"]["segment"]


def test_a_thing_of_theirs_keeps_the_founders_subject():
    """149 FR-3.1 (`Fresco.theToolBranchDrawsOnlyWhereThePeopleAreTheSubject`): *whose jobs run on ...* draws *have jobs
    that run on ...*, a singular thing with its article; the tool branch only where the people are the subject."""
    assert vs.condition_from(FRESCO_WHICH_PEOPLE) == "have jobs that run on Procore or ACC"
    assert vs.condition_from("researchers whose team shares a cluster") == "have a team that shares a cluster"
    assert vs.condition_from("superintendents who run on Procore") == "run on Procore"
    assert vs.condition_from("that bank with Mercury or Brex") == "bank with Mercury or Brex"
    assert q.thing_of_theirs("whose jobs") is None, "a thing with no verb says nothing of it"


def test_fresco_draws_its_condition_and_reads_149s_sentence():
    """08-fresco: the founder's WHICH PEOPLE (the back-test entry's) draws *have jobs that run on Procore or ACC*, and the
    sentence on 149's slots with it is 149's (`ReadBackReadsOnceApplierTest.Fresco.SENTENCE`)."""
    assert _founders_people("08-fresco") == FRESCO_WHICH_PEOPLE
    drawn = vs.drawn_condition(FRESCO_WHICH_PEOPLE)
    assert drawn == "have jobs that run on Procore or ACC"
    assert vs.sentence(FRESCO_CORE, drawn, FRESCO_WHEN, FRESCO_WHAT, vs.Window(5, "WORKING_DAYS")) == FRESCO_SENTENCE


def test_an_organisations_qualifier_draws_on_its_head_noun():
    """149 FR-3.2 (`Palus.theOrganisationsQualifierDrawsOnItsHeadNoun`): a participle or a relative clause on the
    organisation named before it draws 131's frame on the head noun; 131's own frame is unchanged."""
    assert _founders_people("10-palus") == PALUS_WHICH_PEOPLE
    assert vs.drawn_condition(PALUS_WHICH_PEOPLE) == PALUS_BANKS
    assert vs.condition_from("banking with Mercury, Brex or similar",
                             "venture-backed startups in the US within two years of a raise, ") == PALUS_BANKS
    assert vs.condition_from("banking with Mercury, Brex or similar") is None, \
        "no organisation named before it: the tool branch's, which reads *bank with*, never *banking with* (the cloud's)"
    assert vs.condition_from("founders who bank with Mercury, Brex or similar") == \
        "bank with Mercury, Brex or similar", "the people the subject"
    assert vs.condition_from("engineers at startups that run on AWS") == "work at a startup that runs on AWS"
    assert vs.condition_from("reservation agents at hotel groups in Germany that run a central reservations office or "
                             "call center") == ("work at a hotel group in Germany that runs a central reservations "
                                                "office or call center")


def test_palus_says_its_condition_once():
    """149 `Palus`: the core as typed already says code's draw (a participle is its verb, `bare`), so the sentence is
    the core alone; the core that dropped the bank clause takes it after *, who*."""
    assert q.in_core(PALUS_AS_TYPED, PALUS_BANKS)
    assert q.segment_line(PALUS_AS_TYPED, PALUS_BANKS) == PALUS_AS_TYPED
    assert vs.sentence(PALUS_AS_TYPED, PALUS_BANKS, PALUS_WHEN, PALUS_WHAT, vs.Window(3, "MONTHS")) == (
        "Finance leads at venture-backed startups in the US within two years of a raise, banking with Mercury, Brex or "
        "similar. When the company decides where cash from a raise sits until it is needed, they want to keep the money "
        "from a raise safe and earning until the company spends it, counting the last 3 months.")
    assert vs.sentence("finance leads at venture-backed startups in the US", PALUS_BANKS, PALUS_WHEN, PALUS_WHAT,
                       vs.Window(3, "MONTHS")).startswith(
        "Finance leads at venture-backed startups in the US, who work at a startup that banks with Mercury, Brex or "
        "similar. When the company decides")
    assert q.same_qualifier("banks with Mercury, Brex or similar", "banking with Mercury, Brex or similar")
    assert q.bare("banking, running, operating, owning") == "bank, run, operate, own"


def test_a_list_is_one_part():
    """149 FR-3.3 (`ReadBackReadsOnceApplierTest.aListIsOnePart`), and 149's judgement call 2: a list of activities is
    still split (an item opening on a lower-case *-ing* word is never an item)."""
    def stripped(text):
        return [part.strip() for part in q.parts(text)]
    assert stripped(PALUS_WHICH_PEOPLE) == ["venture-backed startups in the US within two years of a raise",
                                            "banking with Mercury, Brex or similar"]
    assert stripped("front-desk teams on OPERA Cloud, Sihot and Apaleo") == \
        ["front-desk teams on OPERA Cloud, Sihot and Apaleo"]
    assert stripped("learners at intermediate level or above, not starting from zero") == \
        ["learners at intermediate level or above", "not starting from zero"]
    assert stripped("people in Pakistan who earn in rupees and have no foreign currency account") == \
        ["people in Pakistan who earn in rupees", "have no foreign currency account"]
    assert stripped("growers in Germany, Italy or France") == ["growers in Germany, Italy or France"]
    assert stripped("cooks, cleaning or driving") == ["cooks", "cleaning or driving"]
    assert q.parts("a, b,") == ["a", " b"] and q.parts("") == [""], "as Java's String.split gives them"


def test_expanses_amount_is_not_the_harness_to_draw():
    """FR-3: 17-expanse's *have 100 or more GPUs* is 145's amount branch, which 149 left as it was and the harness's
    130-era draw does not mirror -- so it draws none, before and after 149 alike."""
    people = _founders_people("17-expanse")
    assert people == "researchers and ML engineers on SLURM or Kubernetes clusters of 100 or more GPUs"
    assert vs.drawn_condition(people) is None
    applier = _cloud("src/main/java/com/keeldiscovery/cloud/application/ScreenResultApplier.java")
    assert 'return ORGANISATIONS.contains(noun) ? "work at " + article(noun) + noun + " with " + rest : "have " + rest;' \
        in applier, "the amount branch 149 did not move"


def test_the_draw_mirror_reads_the_clouds_sources():
    """FR-2's patterns are 149's, held to `Qualifiers.java` and `ScreenResultApplier.java`."""
    source = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/Qualifiers.java")
    assert ('"(?!(?:who|whose|that|which|where|when|while|with|without|in|at|on|of|for"\n'
            '            + "|from|by|to|into|across|within|not|no|never|but|and|or)\\\\b|(?-i:[a-z]+(?:ing|ly))\\\\b)"'
            ) in source
    assert 'ITEM_OPENS + "[^,;\\\\s]+(?:\\\\s+(?!(?:and|or)\\\\b)[^,;\\\\s]+){0,2}"' in source
    assert ('"(?i)(?:,\\\\s*" + ITEM + ")*,\\\\s*" + ITEM + "\\\\s+(?:or|and)\\\\s+"\n'
            '            + ITEM_OPENS + "[^,;]+?(?=\\\\s+and\\\\b|\\\\s*[,;]|\\\\s*$)"') in source
    assert 'replaceAll("(?i)\\\\b(bank|work|own|employ)ing\\\\b", "$1")' in source
    assert "FounderWords.dropped(bare(qualifier), bare(condition)).isEmpty()" in source
    applier = _cloud("src/main/java/com/keeldiscovery/cloud/application/ScreenResultApplier.java")
    assert '"(?i)\\\\b(?:that|which)\\\\s+(bank|run|work|operate|own|employ)s?\\\\s+(.+)$"' in applier
    assert '"(?i)(?:^|\\\\s)(banking|running|working|operating|owning|employing)\\\\s+(.+)$"' in applier
    assert '"(?i)\\\\bwhose\\\\s+(.+)$"' in applier
    assert 'return "work at " + article(head) + head + " that " + base + "s " + clause.group(2).strip();' in applier
    order = [applier.index(marker) for marker in ("String theirs = thingOfTheirs(text);",
                                                  "String organisations = organisationsClause(part.strip(), before);",
                                                  '"(?i)\\\\b((?:bank|banks|run|runs|work|works) (?:with|on) .+)$"')]
    assert order == sorted(order), "the thing and the organisation before the tool branch"
    for noun in ("startup", "contractor"):
        assert (f'"{noun}"' in applier) is (noun in q.ORGANISATIONS), noun
