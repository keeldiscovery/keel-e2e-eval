"""Spec 082: the back-test under a scope -- the study's own people (FR-1), the cost box read when it is drawn (FR-2),
and a cycle record that names the walks that stopped and the sha that moved (FR-3).

Zero spend: the people from keel-cloud's back-test file and the golden B2B fixture, the cost step on a page double that
draws the *of* box only with the equation, the record composed from the 079 fixture cycle's score files.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from stack.config import load_config
from tests import v9_fixtures as fx

REPO = Path(__file__).resolve().parent.parent
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)


def _scoped(entry, scope: str):
    return dataclasses.replace(entry, scope=scope)


@pytest.fixture(scope="module")
def fresco():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "08-fresco.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {path}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


# ------------------------------------------------------------------------------- FR-1: the study's own people

def test_08_fresco_under_problem_and_solution_is_its_primary_people_alone(fresco):
    """FR-1: the cycle's KeyError 'COMMERCIAL_B2B' -- 08-fresco's eight B2B people are the money study's (keel-cloud
    133); under PROBLEM and SOLUTION the walk sends the twelve PRIMARY people and nobody else."""
    primary = [p.person for p in fresco.people() if p.link == vs.LINK_PRIMARY]
    b2b = [p.person for p in fresco.people() if p.link == vs.LINK_B2B]
    assert vs.is_b2b(fresco) and len(primary) == 12 and len(b2b) == 8
    for scope in ("PROBLEM", "SOLUTION"):
        people = vs.person_inputs(_scoped(fresco, scope))
        assert [p.person for p in people] == primary, scope
        assert {p.link for p in people} == {vs.LINK_PRIMARY}, scope


def test_08_fresco_under_all_and_commercial_is_every_person_in_the_file(fresco):
    """FR-1: the money study and the whole study send every person, as before."""
    everyone = [p.person for p in fresco.people()]
    for entry in (fresco, _scoped(fresco, "ALL"), _scoped(fresco, "COMMERCIAL")):
        assert [p.person for p in vs.person_inputs(entry)] == everyone, vs.scope_of(entry)
    assert vs.study_people(_scoped(fresco, "SOLUTION_COMMERCIAL")) == list(fresco.people())


def test_a_b2b_entry_under_a_scope_names_nobody_downstream_who_was_not_sent():
    """FR-1: the follow-up lines, the themes screen and `inputs.json` read the list that comes back -- under PROBLEM
    and SOLUTION no decision-maker is owed a line or written into the inputs; under ALL they are, as before."""
    entry = fx.entry(fx.ENTRY_B2B)
    deciders = {p.person for p in entry.people() if p.link == vs.LINK_B2B}
    assert deciders and deciders & set(vs.follow_up_lines(entry, vs.person_inputs(entry)))
    for scope in ("PROBLEM", "SOLUTION"):
        seed = _scoped(entry, scope)
        people = vs.person_inputs(seed)
        assert not deciders & {p.person for p in people}, scope
        lines = vs.follow_up_lines(seed, people)
        assert lines and not deciders & set(lines), (scope, lines)
        assert {p.person: p.follow_up for p in people if p.follow_up} == {k: v for k, v in lines.items() if v}
        inputs = vs.inputs_json(seed, vs.founder_inputs(seed), people)
        named = {p["person"] for p in inputs["people"]}
        assert named == {p.person for p in people} and not deciders & named, scope
        themes = vs.generate(seed).screens["THEMES"]
        assert themes == vs.themes_entries(seed, vs.walked_follow_ups(seed, people)), scope


def test_the_scope_reaches_person_inputs_through_the_entry_not_a_parameter():
    """FR-1: `corpus_scenario` and `scope_journey` replace `entry.scope` before they build the people; no new
    parameter."""
    import inspect                                                     # noqa: PLC0415

    from evals import corpus_scenario, scope_journey                   # noqa: PLC0415
    assert list(inspect.signature(vs.person_inputs).parameters) == ["entry"]
    source = inspect.getsource(corpus_scenario)
    at_replace = source.index("entry = dataclasses.replace(entry, scope=scope)")
    assert at_replace < source.index("people = vs.person_inputs(entry)", at_replace)
    walk = inspect.getsource(scope_journey)
    assert walk.index("entry.scope != scope") < walk.index("people = vs.person_inputs(entry)")
