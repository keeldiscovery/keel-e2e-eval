"""Spec 129 -- the harness follows keel-cloud 202 (the defects of cycles 7 and 8, the cloud's half).

No harness code pinned 202's served strings (its tasks.md checked: *needed to call it*, *bar: no more than*, the tally);
what the harness mirrors is the gate (D4: the occasion's clause past the spoken cap cut by its trailing phrases before
the job is ever taken -- 18-careforce's reversed claim), read by `backtest.cloud_131` as a finding against the served
gate, and the words the readers are handed for the stage tally (D3: it counts beliefs, and says *too few to call*).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from quality import readers
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


@pytest.fixture(scope="module")
def entries():
    try:
        registry = cloud_mod.registry_of_record(KEEL_CLOUD)
    except Exception as missing:  # noqa: BLE001 - a checkout without the registry of record skips, as every mirror does
        pytest.skip(f"no keel-cloud registry of record: {missing}")
    return {e.id: e for e in corpus_mod.load(KEEL_CLOUD, registry=registry, backtest=True).entries}


def test_careforces_gate_is_the_occasion_cut_to_the_cap_never_the_job(entries):
    careforce = entries["18-careforce"]
    window = vs.window_of(careforce)
    circumstance = careforce.context.get("circumstance")
    gate = vs.gate_from_circumstance(window, circumstance)
    assert gate == "In the last 5 working days, did you have to call the day's list of patients?"
    assert not vs.gate_asks_the_job(careforce, gate)
    clause = "have to call the day's list of patients"
    assert vs.fitted("have to call the day's list of patients due for a screening or visit", window) == clause
    assert len(vs.frequency_served(window, clause).split()) <= vs.STEM_MAX_WORDS


def test_a_clause_that_fits_is_never_cut(entries):
    codyco = entries["21-codyco"]
    window = vs.window_of(codyco)
    assert vs.gate_from_circumstance(window, codyco.context.get("circumstance")) == (
        "In the last 7 days, did a booking call come in on your shift?")
    assert vs.fitted("a booking call come in on your shift", window) is None
    assert vs.fitted("", window) is None


def test_a_possessive_time_word_is_no_period():
    assert vs.possessive_time("have to call the day's list of patients") == (
        "have to call the occasion's list of patients")
    assert vs.possessive_time("check the list every day") == "check the list every day"
    assert vs.possessive_time(None) is None


def test_the_readers_are_told_the_tally_counts_beliefs():
    body, _ = readers._after_body({"kind": "stage", "n": 1, "stage": "PROBLEM", "page": {
        "kicker": "The problem · 7 people answered · 3 to 7 counted", "title": "t", "headline": "h",
        "tally": "6 beliefs: 2 holding · 1 not holding · 2 did not hold · 1 too few to call"}}, 3)
    assert ("The tally over the cards (how many of the beliefs hold, do not, did not hold, are split or are too few to "
            "call): 6 beliefs: 2 holding") in "\n".join(body)
