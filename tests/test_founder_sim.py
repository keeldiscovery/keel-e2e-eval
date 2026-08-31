"""Stackless tests for the shaping gauntlet's founder simulator (harness/founder_sim.py):
fact-gating (a probe releases exactly its own fact and never another, twice never re-"reveals"),
a non-probe deflects without volunteering anything, and no opener ever leaks a fact ahead of time.
Runs under `make unit` -- no stack, no `claude` CLI required."""

from __future__ import annotations

from harness.founder_sim import (ASSUMPTIONS, COMMERCIAL, DEFLECTIONS, FACT_IDS, PROBLEM,
                                  SOLUTION, STAGE_OPENERS, FounderSimulator)


def test_a_matched_probe_releases_exactly_its_own_fact():
    sim = FounderSimulator()
    outcome = sim.respond("Who exactly has this problem -- which segment?")
    assert outcome.fact_id == "who"
    assert outcome.newly_earned is True
    assert outcome.reply == sim.fact_text("who")
    assert sim.earned == {"who": 1}


def test_a_matched_probe_never_leaks_another_facts_text():
    sim = FounderSimulator()
    outcome = sim.respond("How often does this happen?")
    assert outcome.fact_id == "frequency"
    for other_id in FACT_IDS:
        if other_id == "frequency":
            continue
        assert sim.fact_text(other_id) not in outcome.reply


def test_mechanism_probe_takes_priority_over_a_generic_how():
    """module docstring's priority-order judgement call: "how does it work" must resolve to
    mechanism, not accidentally match a different probe merely because it contains "how"."""
    sim = FounderSimulator()
    outcome = sim.respond("Can you tell me how does it work in practice?")
    assert outcome.fact_id == "mechanism"


def test_an_unmatched_turn_deflects_and_volunteers_nothing():
    sim = FounderSimulator()
    outcome = sim.respond("That's an interesting idea, tell me more about your day.")
    assert outcome.fact_id is None
    assert outcome.newly_earned is False
    assert outcome.reply in DEFLECTIONS
    for fact_id in FACT_IDS:
        assert sim.fact_text(fact_id) not in outcome.reply
    assert sim.earned == {}


def test_deflections_cycle_deterministically_not_randomly():
    sim = FounderSimulator()
    first_pass = [sim.respond("unrelated small talk").reply for _ in range(len(DEFLECTIONS))]
    second_pass = [sim.respond("unrelated small talk").reply for _ in range(len(DEFLECTIONS))]
    assert first_pass == list(DEFLECTIONS)
    assert second_pass == list(DEFLECTIONS)  # cycles back to the start, same order every lap


def test_a_fact_already_earned_is_echoed_not_re_revealed_as_new():
    sim = FounderSimulator()
    first = sim.respond("Who has this problem?")
    second = sim.respond("Sorry, remind me who has this problem again?")
    assert first.newly_earned is True
    assert second.fact_id == "who"
    assert second.newly_earned is False
    assert sim.fact_text("who") in second.reply  # still says the fact...
    assert second.reply != first.reply  # ...but doesn't repeat the identical "reveal" line
    assert sim.earned == {"who": 1}  # earned turn index is not overwritten by the repeat


def test_never_released_names_exactly_the_unearned_facts():
    sim = FounderSimulator()
    sim.respond("Who has this problem?")
    sim.respond("How often does it happen?")
    never = sim.never_released()
    assert set(never) == {"cost", "mechanism", "price"}
    assert never["cost"] == sim.fact_text("cost")


def test_no_opener_ever_contains_any_facts_text():
    """The design's own "never volunteers": a vague opener must not accidentally already contain
    the very fact it's designed to make the agent ask for."""
    sim = FounderSimulator()
    for stage in (PROBLEM, SOLUTION, COMMERCIAL, ASSUMPTIONS):
        opener = sim.opener(stage)
        for fact_id in FACT_IDS:
            assert sim.fact_text(fact_id) not in opener, (stage, fact_id)


def test_every_stage_has_a_vague_opener():
    for stage in (PROBLEM, SOLUTION, COMMERCIAL, ASSUMPTIONS):
        assert stage in STAGE_OPENERS
        assert STAGE_OPENERS[stage].strip()


def test_continue_or_new_question_gets_a_new_project_answer_without_leaking_facts() -> None:
    sim = FounderSimulator()
    out = sim.respond("You have one project in progress -- want to continue with it, or is this a new project?")
    assert "new project" in out.reply.lower()
    assert out.fact_id is None
    assert not sim.earned
