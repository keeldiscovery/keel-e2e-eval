"""`register.html` at `MARKS_VERSION` 9 (spec 029 FR-022, contracts/screen-shapes.md §7; T033, T041).

The one page with no number on it. Per entry: the three interpretations, verbatim, marked only
*accepted* or *refused (rule id)* by the aggregate; the 25 calibration questions in registry order
beside the registry's own founder question, the founder's chosen phrase and the belief sentence r3
records; the respondent items beside the plan row, the reveal between parts 1 and 2, the B2B link on
its own. **No score, no tick, no cross, no `met`, no `mark`** -- judgement call 10.
"""

from __future__ import annotations

import re

import pytest

from instructions import corpus as corpus_mod
from instructions import report as report_mod
from tests import v9_fixtures as fx

LULLABY = fx.CORPUS_R3 / "03-lullaby.yaml"


@pytest.fixture()
def corpus():
    entry = corpus_mod.load_file(LULLABY, registry=fx.registry())
    return corpus_mod.Corpus(entries=[entry], directory=LULLABY.parent)


def _produced(registry):
    out = {
        "CONTEXT_INTERPRET": ("03-lullaby/CONTEXT_INTERPRET/run1",
                              {"understands": "Keel understands: parents at night."}),
        "PROBLEM_INTERPRET": ("03-lullaby/PROBLEM_INTERPRET/run1",
                              {"statement": "Parents cannot tell what the cry means."}),
        "SOLUTION_MECHANISM": ("03-lullaby/SOLUTION_MECHANISM/run1", {"actor": "the parent"}),
    }
    for vector in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
        out[f"CALIBRATION_{vector}"] = (f"03-lullaby/CALIBRATION_{vector}/run1",
                                        fx.calibration_result(registry, vector))
    return {"03-lullaby": out}


_AGGREGATE = {
    "03-lullaby/CONTEXT_INTERPRET/run1": {"accepted": True},
    "03-lullaby/PROBLEM_INTERPRET/run1": {"accepted": False,
                                          "refusal": {"kind": "rule", "rule": "P1"}},
}


def _visible(html: str) -> str:
    return re.sub(r"<style>.*?</style>", "", html, flags=re.S)


def _render(tmp_path, corpus, produced):
    blocks = report_mod.register_blocks(corpus, produced, fx.registry(), _AGGREGATE)
    return report_mod.render_register(tmp_path, entries_by_market=blocks,
                                      paragraphs={}).read_text(encoding="utf-8")


def test_the_calibration_block_is_the_registry_in_order_beside_the_founder(tmp_path, corpus):
    registry = fx.registry()
    blocks = report_mod.register_blocks(corpus, _produced(registry), registry, _AGGREGATE)
    block = blocks["GB · en-GB"]["03-lullaby"]
    rows = block["calibration"]
    assert [r["key"] for r in rows] == registry.keys()
    prevalence = rows[0]
    assert prevalence["founder_question"].startswith("Out of 10 parents of babies")
    assert prevalence["belief_phrase"] == "Most"
    assert prevalence["belief_sentence"].startswith("Most of these parents")
    urgency = next(r for r in rows if r["key"] == "problem.urgency")
    assert urgency["belief_phrase"] is None
    assert urgency["belief_sentence"] == "Left out: you weren't sure."


def test_the_three_interpretations_are_marked_only_accepted_or_refused_by_rule(tmp_path, corpus):
    html = _render(tmp_path, corpus, _produced(fx.registry()))
    assert "CONTEXT_INTERPRET</b> — accepted" in html
    assert "PROBLEM_INTERPRET</b> — refused (P1)" in html
    assert "SOLUTION_MECHANISM</b> — not shown to the aggregate" in html
    assert "Parents cannot tell what the cry means." in html


def test_the_register_carries_no_score_tick_cross_met_or_mark(tmp_path, corpus):
    html = _visible(_render(tmp_path, corpus, _produced(fx.registry())))
    assert "✓" not in html and "✗" not in html
    for word in ("score", "met", "mark"):
        assert not re.search(rf"\b{word}\b", html, re.IGNORECASE), word


def test_the_respondent_block_sits_beside_the_plan_with_the_reveal_between_parts(tmp_path, corpus):
    entry = corpus.entries[0]
    produced = _produced(fx.registry())
    for part in (1, 2, 3):
        produced["03-lullaby"][f"RESPONDENT_PART{part}"] = (
            f"03-lullaby/RESPONDENT_PART{part}/run1", fx.respondent_result(entry, part))
    produced["03-lullaby"]["RESPONDENT_B2B"] = (
        "03-lullaby/RESPONDENT_B2B/run1", fx.respondent_result(entry, 3, link="COMMERCIAL_B2B"))
    blocks = report_mod.register_blocks(corpus, produced, fx.registry(), _AGGREGATE)
    block = blocks["GB · en-GB"]["03-lullaby"]
    assert len(block["respondent"]) == 23
    gate = block["respondent"][0]
    assert (gate["key"], gate["part"], gate["control"], gate["codes"]) == (
        "problem.prevalence", 1, "gate_yes_no", ["yes", "no"])
    assert block["reveal"]["title"] == "What we are testing"
    assert len(block["b2b"]) == 6

    html = _visible(report_mod.render_register(tmp_path, entries_by_market=blocks,
                                               paragraphs={}).read_text(encoding="utf-8"))
    part1_end = html.index("problem.current_solution_satisfaction</b> · part 1")
    reveal = html.index("<b>The reveal</b>")
    part2_start = html.index("solution.compatibility</b> · part 2")
    assert part1_end < reveal < part2_start, "the reveal sits between parts 1 and 2"
    assert "The decision-maker's link (COMMERCIAL_B2B)" in html
    for word in ("score", "met", "mark"):
        assert not re.search(rf"\b{word}\b", html, re.IGNORECASE), word
