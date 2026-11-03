"""Spec 130, the mirror owed by keel-cloud 197 (the cards keep the founder's words; keel-cloud-docs `cd0d736d`).

The model's short name -- the idea card's *what it is* -- is the kind of thing and what it does, at most **eight** words
(`Wording.SHORT_NAME_MAX_WORDS`, five until 197), never an outcome (`IdeaLines.isAnOutcome`, `W3`) and never empty
(`L6`); the founder's own name keeps spec 090's five (`IdeaLines.NAME_MAX_WORDS`, `corpus.IDEA_NAME_MAX_WORDS`). The walk
holds the served card to it as a finding (`corpus_scenario._note_what_it_is`), never a stop.
"""

from __future__ import annotations

import inspect
import re
import types
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from evals import scope_journey
from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
WORDING = "src/main/java/com/keeldiscovery/cloud/domain/vectors/Wording.java"
IDEA_LINES = "src/main/java/com/keeldiscovery/cloud/domain/project/IdeaLines.java"
CONTRACTS = "src/main/java/com/keeldiscovery/cloud/application/ScreenResponseContracts.java"


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    text = full.read_text(encoding="utf-8")
    if path == WORDING and "SHORT_NAME_MAX_WORDS = 8" not in text:
        pytest.skip("keel-cloud before 197: the short name is five words")
    return text


def test_the_short_name_is_eight_words_and_the_founders_name_five():
    assert f"public static final int SHORT_NAME_MAX_WORDS = {vs.SHORT_NAME_MAX_WORDS};" in _cloud(WORDING)
    lines = _cloud(IDEA_LINES)
    assert f"public static final int NAME_MAX_WORDS = {corpus_mod.IDEA_NAME_MAX_WORDS};" in lines
    assert (vs.SHORT_NAME_MAX_WORDS, vs.SHORT_NAME_MAX_WORDS_196, corpus_mod.IDEA_NAME_MAX_WORDS) == (8, 5, 5)
    contracts = _cloud(CONTRACTS)
    assert 'SHORT_NAME_RULE = "At most eight words: the kind of thing and what it does' in contracts
    assert "public static final int CONTRACT_VERSION = 25;" in contracts, "198's; 197 moved a description only"


def test_the_grammar_words_are_idea_lines_own():
    lines = _cloud(IDEA_LINES)
    body = lines[lines.index("CLOSES_THE_PHRASE = java.util.Set.of("):]
    body = body[:body.index(");")]
    assert set(re.findall(r'"([^"]+)"', body)) == vs.CLOSES_THE_PHRASE
    assert "public static boolean isAnOutcome(String shortName, String output)" in lines


@pytest.mark.parametrize("short_name, output, outcome", [
    ("missed-call bookings", "the confirmed booking written straight into the PMS", True),
    ("a confirmed booking in the PMS", "the confirmed booking written straight into the PMS", True),
    ("an AI reservation agent for missed hotel calls", "the confirmed booking written straight into the PMS", False),
    ("a phone app that listens to crying", "the need the app says is most likely", False),
    ("site walk notes with photos", "site walk notes with photos and a punch list", True),
    ("", "anything", False),
])
def test_an_outcome_is_told_from_the_kind_of_thing(short_name, output, outcome):
    assert vs.is_an_outcome(short_name, output) is outcome


def test_the_what_it_is_faults_are_findings_never_stops():
    output = "the confirmed booking written straight into the PMS"
    assert vs.what_it_is_faults("an AI reservation agent for missed hotel calls", output) == []
    assert vs.what_it_is_faults("missed-call bookings", output)[0].startswith("W3: 'missed-call bookings' names what")
    long = "an AI reservation agent that answers every missed hotel call"
    assert vs.what_it_is_faults(long, None) == [f"W3: '{long}' is 10 words; at most 8"]
    assert vs.what_it_is_faults("  ", output)[0].startswith("L6:")
    j = types.SimpleNamespace(entry=types.SimpleNamespace(solution_mechanism={"output": output}), findings=[])
    cs._note_what_it_is(j, {"what": "Codyco", "whatItIs": "missed-call bookings"})
    assert j.findings and j.findings[0]["what"] == "the idea card's what it is (keel-cloud 197 FR-3)"
    j.findings.clear()
    cs._note_what_it_is(j, {"what": "Codyco", "whatItIs": "an AI reservation agent for missed hotel calls"})
    assert j.findings == []
    assert "cs._note_what_it_is(j, idea)" in inspect.getsource(scope_journey.leg_idea_card)
    assert "_note_what_it_is(j, idea)" in inspect.getsource(cs)
