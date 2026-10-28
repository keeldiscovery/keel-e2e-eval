"""Spec 076: the harness follows keel-cloud 145 (contract 43) and keel-web 127 -- the founder's second walk of
2026-10-27. Stackless: the words and rules restated here are held to the products' own sources (keel-cloud-docs master,
keel-web master, through `stack.toml`'s sibling paths), and the walks' new reads to small pages."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from harness import interviewer_fake as fake
from instructions import brief_facts as bf
from instructions import chain as chain_mod
from instructions import corpus as corpus_mod
from instructions import spoken
from stack.config import load_config
from tests import v9_fixtures as fx

CONFIG = load_config(validate=False)


def _cloud(path: str) -> str:
    return (CONFIG.keel_cloud / path).read_text()


def _web(path: str) -> str:
    return (CONFIG.keel_web / path).read_text()


@pytest.fixture(scope="module")
def corpus():
    fx.canon_entry("01-countly.yaml")
    return corpus_mod.load(CONFIG.keel_cloud).bind(fx.registry())


def _entry(corpus, entry_id: str):
    return next(e for e in corpus.entries if e.id == entry_id)


# ----------------------------------------------------------------- FR-2 Buyer and payer is direction-aware


def test_a_named_roles_supports_are_both_answers_as_the_registry_says():
    """keel-cloud 145 FR-2: with a role named, *had to agree* and *decided alone* both support the founder; the two
    *someone else* answers count against (the registry's `supports`, held in `test_follow_up_ladder.py` too)."""
    assert fake.BUYER_SUPPORTS == ("had_to_agree", "decided_alone")
    named = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=fake.BUYER_SUPPORTS)
    owed = lambda code: fake.owed([{"dimension": "commercial.buyer_payer_alignment", "codes": [code]}],  # noqa: E731
                                  named, "COMMERCIAL_B2B", b2b=True)
    assert [d for d, _ in owed("decided_alone")] == [] and [d for d, _ in owed("had_to_agree")] == []
    assert [d for d, _ in owed("someone_else_agreed")] == ["commercial.buyer_payer_alignment"]
    assert [d for d, _ in owed("someone_else_decided")] == ["commercial.buyer_payer_alignment"]


def test_the_role_takes_its_the_as_belief_sentence_reads_it():
    """keel-cloud 145 FR-2 (`BeliefSentence.theRole`): an acronym takes *the*, a role's own article is lower-cased, a
    person's name is kept bare."""
    assert chain_mod.the_role("CEO") == "the CEO"
    assert chain_mod.the_role("CFO") == "the CFO"
    assert chain_mod.the_role("HR director") == "the HR director"
    assert chain_mod.the_role("The HR director") == "the HR director"
    assert chain_mod.the_role("restaurant owner") == "the restaurant owner"
    assert chain_mod.the_role("Priya") == "Priya"
    assert chain_mod.the_role("their manager") == "their manager"
    source = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/BeliefSentence.java")
    assert 'ACRONYM = java.util.regex.Pattern.compile("^[A-Z]{2,4}s?$")' in source
    assert chain_mod.ACRONYM.pattern == "^[A-Z]{2,4}s?$"


def test_the_buyer_labels_give_an_acronym_role_its_the():
    """keel-cloud 145 FR-2 (`ItemFrames.buyerPayerLabel`, `buyerPayerAtPriceLabel`): *Yes, the CEO had to agree*,
    *No, the CEO would have to agree*."""
    labels = spoken.buyer_answers("CEO")
    assert labels[0] == "Yes, the CEO had to agree" and labels[2] == "No, the CEO would have to agree"
    assert spoken.buyer_answers(None)[0] == "Yes, someone else had to agree"


def test_the_brief_line_and_the_said_line_on_a_named_role(corpus):
    """keel-cloud 145 FR-2: the brief's fact line *k of n · {role} had to agree, or they decided alone*, and the said
    line the belief after *You said* -- *You said the HR director has to agree.*; with *Nobody else* tested both as
    before (*decided on their own*; *You said nobody else has to agree.*)."""
    registry = fx.registry()
    compliance = _entry(corpus, "02-compliancelog")
    card = next(c for c in bf.cards_for(compliance, registry) if c["key"] == "commercial.buyer_payer_alignment")
    assert card["line"] == "the HR director had to agree, or they decided alone"
    assert cs.buyer_said(compliance) == "You said the HR director has to agree."
    countly = _entry(corpus, "01-countly")
    card = next(c for c in bf.cards_for(countly, registry) if c["key"] == "commercial.buyer_payer_alignment")
    assert card["line"] == "decided on their own"
    assert cs.buyer_said(countly) == "You said nobody else has to agree."
    brief = _cloud("src/main/java/com/keeldiscovery/cloud/application/BriefFacts.java")
    assert '" had to agree, or they decided alone"' in brief
    said = _cloud("src/main/java/com/keeldiscovery/cloud/application/StandingsAssembler.java")
    assert 'return "You said " + phrase + " has to agree.";' in said


def test_every_six_journey_entry_tests_nobody_else_so_no_golden_reading_moves(corpus):
    """Spec 076 FR-2: the six journeys walk 01-countly and 05-paidly (and 07-mulchrun), each testing *Nobody else* --
    the direction-aware rule moves none of their rows; 02-compliancelog's (the HR director) is the one row keel-cloud
    145 proposes for revision 17, and REVISION stays 16."""
    for entry_id in ("01-countly", "05-paidly", "07-mulchrun"):
        assert (_entry(corpus, entry_id).tested("commercial.buyer_payer_alignment") or {}).get("code") == "nobody_else"
    assert corpus_mod.REVISION == 16
    golden = _cloud("src/test/java/com/keeldiscovery/cloud/corpus/GoldenCorpusTest.java")
    assert '"02-compliancelog commercial.buyer_payer_alignment", "HOLDING_UP/NONE/7"' in golden
    assert '"02-compliancelog commercial.buyer_payer_alignment", "PEOPLE_DISAGREE/BOTH/5"' in golden
