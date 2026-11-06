"""Spec 143 FR-1 -- the review switch in the cycle (keel-cloud spec 209's `keel.review.respondent-questions`,
`KEEL_REVIEW_RESPONDENT_QUESTIONS`).

The stack hands keel-cloud the shell's environment whole and never sets the switch (unset is OFF, as keel-cloud has
it); `stack.cloud.review_switch` reads it as Spring does; the walk's bundle records it (`backtest.json`'s
`review_switch`); the cycle record's head line names it (*review ON* / *review OFF*) beside routing, RUBRIC_VERSION and
the reader; a record whose walks disagree is refused as a mixed cycle. No stack, no model, no key.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from quality import cycle
from stack import cloud as cloud_stack
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
ENV = cloud_stack.REVIEW_SWITCH_ENV


# --------------------------------------------------------------------------------------------- the variable

@pytest.mark.parametrize("value,want", [(None, "OFF"), ("", "OFF"), ("false", "OFF"), ("FALSE", "OFF"), ("0", "OFF"),
                                        ("off", "OFF"), ("true", "ON"), ("TRUE", "ON"), (" on ", "ON"), ("1", "ON"),
                                        ("yes", "ON")])
def test_the_switch_is_read_as_keel_cloud_reads_it(value, want):
    env = {} if value is None else {ENV: value}
    assert cloud_stack.review_switch(env) == want


def test_a_value_keel_cloud_cannot_read_is_refused_by_name():
    with pytest.raises(ValueError, match=ENV):
        cloud_stack.review_switch({ENV: "maybe"})


def test_the_variable_is_the_one_keel_cloud_reads():
    path = KEEL_CLOUD / "src/main/resources/application.yml"
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD}")
    assert "respondent-questions: ${KEEL_REVIEW_RESPONDENT_QUESTIONS:false}" in path.read_text(encoding="utf-8")


def test_the_stack_hands_it_through_and_never_turns_it_on(monkeypatch):
    """`build_env` copies the environment whole: set, keel-cloud gets it; unset, nothing sets it (keel-cloud's OFF)."""
    config = load_config(validate=False)
    monkeypatch.delenv(ENV, raising=False)
    assert ENV not in cloud_stack.build_env(config)
    monkeypatch.setenv(ENV, "true")
    assert cloud_stack.build_env(config)[ENV] == "true"


# ------------------------------------------------------------------------------------------------ the bundle

def test_the_bundle_records_the_switch(monkeypatch):
    monkeypatch.setenv(ENV, "true")
    assert bt.review_switch() == "ON"
    monkeypatch.delenv(ENV)
    assert bt.review_switch() == "OFF"
    md = bt.markdown({"review_switch": "ON", "respondents": {}, "founder_screens": []})
    assert ", review **ON** (spec 209)" in md
    assert "review **" not in bt.markdown({"respondents": {}, "founder_screens": []}), "a bundle before 143"


def test_walk_one_reads_the_switch_off_the_bundle(tmp_path):
    runs = tmp_path / "runs"

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / "20261106T100000Z-backtest-21-codyco"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": "PROBLEM",
                                                     "review_switch": "ON", "founder_screens": []}))
            stdout.write(f"run bundle: {run}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps(["21-codyco"], ["PROBLEM"], "host", tmp_path / "work") if s["study"]]
    study = cycle.walk_one("21-codyco", "PROBLEM", steps, door="host", runner=fake, runs_dir=runs)
    assert study.review_switch == "ON"
    assert cycle._study_data(study)["review_switch"] == "ON"
    assert "review_switch" not in cycle._study_data(cycle.Study("a", "PROBLEM")), "a bundle before 143, as 140's"


# ------------------------------------------------------------------------------------------- the record

def _record(**kw) -> dict:
    return {"record": "20261106-ac81bf6", "why": "w", "started": "s", "ended": "e", "seconds": 60, "door": "keel",
            "entries": ["21-codyco"], "scopes": ["PROBLEM"], "cloud_sha": "ac81bf6", "web_sha": "d280012",
            "cloud_branch": "master", "routing_versions": ["17"], "rubric_version": 5,
            "reader": {"model": "claude-opus-5-5", "effort": "medium"}, "bar_pct": 80,
            "weak_rule": {"zero_entries": 2, "mean_under": 1.5}, "studies": [], "walks": None,
            "head": {"score_pct": 85.0, "flagged_pct": 3.0, "screens": 10, "founder": {}, "respondent": {}},
            "baseline": None, "against_baseline": None, "previous": None,
            "cost": {"walk_usd": 0, "read_usd": 0, "total_usd": 0}, "weak_rows": [], **kw}


def head_line(record: dict) -> str:
    return next(x for x in cycle.render_record(record).splitlines() if x.startswith("Spec 079. Walked "))


def test_the_head_line_names_the_switch():
    on, off, before = head_line(_record(review_switch="ON")), head_line(_record(review_switch="OFF")), \
        head_line(_record())
    assert "; reader claude-opus-5-5 (medium); review ON (spec 209); the bar 80%;" in on
    assert "; reader claude-opus-5-5 (medium); review OFF (spec 209); the bar 80%;" in off
    assert "review" not in before and "; reader claude-opus-5-5 (medium); the bar 80%;" in before, \
        "a record before 143 renders as it did"
    assert on == ("Spec 079. Walked s -> e (1.0 min) through DOOR=keel on keel-cloud `ac81bf6` (master) and keel-web "
                  "`d280012`; routing v17; RUBRIC_VERSION 5; reader claude-opus-5-5 (medium); review ON (spec 209); "
                  "the bar 80%; weak = a 0 in 2 entries or a mean under 1.5 (quality/cycle.toml).")


def test_the_cycle_has_one_switch_or_is_refused_as_mixed():
    on = {"entry": "21-codyco", "scope": "PROBLEM", "review_switch": "ON"}
    off = {"entry": "10-palus", "scope": "PROBLEM", "review_switch": "OFF"}
    older = {"entry": "08-fresco", "scope": "PROBLEM"}
    assert cycle.review_of("ON", [on, older]) == "ON"
    assert cycle.review_of(None, [on, on]) == "ON"
    assert cycle.review_of(None, [older]) is None
    with pytest.raises(cycle.Refused, match="a mixed cycle.*21-codyco · PROBLEM review ON; 10-palus · PROBLEM review OFF"):
        cycle.review_of(None, [on, off])
    with pytest.raises(cycle.Refused, match="OFF at the kick-off"):
        cycle.review_of("OFF", [on])


def test_compose_records_the_switch_and_refuses_a_mixed_cycle(tmp_path):
    kw = dict(name="20261106-ac81bf6", why="the review on", door="keel", cloud_sha="ac81bf6", web_sha="d280012",
              started="s", ended="e", seconds=1.0, cfg=cycle.load_config(), baseline_path=tmp_path / "BASELINE.md",
              cycles_dir=tmp_path, decisions=[])
    S = cycle.Study
    text, data = cycle.compose([S("21-codyco", "PROBLEM", review_switch="ON")], review="ON", **kw)
    assert data["review_switch"] == "ON" and data["studies"][0]["review_switch"] == "ON"
    assert "review ON (spec 209)" in text
    _, data = cycle.compose([S("21-codyco", "PROBLEM")], **kw)
    assert "review_switch" not in data, "a record before 143 keeps its shape"
    with pytest.raises(cycle.Refused, match="a mixed cycle"):
        cycle.compose([S("21-codyco", "PROBLEM", review_switch="ON"), S("10-palus", "PROBLEM", review_switch="OFF")],
                      review="ON", **kw)


def test_a_mixed_record_is_refused_when_read(tmp_path):
    data = _record(review_switch="ON", studies=[{"entry": "21-codyco", "scope": "PROBLEM", "review_switch": "ON"},
                                                {"entry": "10-palus", "scope": "PROBLEM", "review_switch": "OFF"}])
    path = tmp_path / "20261106-ac81bf6.md"
    path.write_text(cycle.render_record(data), encoding="utf-8")
    with pytest.raises(cycle.Refused, match="a mixed cycle"):
        cycle.load_record(path)
    data["studies"][1]["review_switch"] = "ON"
    path.write_text(cycle.render_record(data), encoding="utf-8")
    assert cycle.load_record(path)["review_switch"] == "ON"


def test_preflight_refuses_a_switch_keel_cloud_cannot_read(tmp_path, monkeypatch):
    monkeypatch.setattr(cycle, "git_dirty", lambda path: [])
    hard, _ = cycle.preflight(entries=[], scopes=["PROBLEM"], door="host", why="w", build=None, dry=True,
                              cloud=tmp_path, env={ENV: "maybe"}, which=lambda n: "/usr/bin/claude")
    assert any(ENV in h for h in hard)
    hard, _ = cycle.preflight(entries=[], scopes=["PROBLEM"], door="host", why="w", build=None, dry=True,
                              cloud=tmp_path, env={ENV: "true"}, which=lambda n: "/usr/bin/claude")
    assert not any(ENV in h for h in hard)


def test_the_runbook_says_to_export_it():
    runbook = (Path(cycle.QUALITY) / "CYCLE.md").read_text(encoding="utf-8")
    assert f"export {ENV}=true" in runbook
    assert f"`{ENV}`" in (Path(cycle.REPO) / "README.md").read_text(encoding="utf-8")
