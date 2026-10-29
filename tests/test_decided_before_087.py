"""Decided before (spec 087): the founder's decisions are recorded in `quality/decisions.toml`, and a weak row he has
already decided is snoozed and listed, not advised again -- with no model, no stack, no network and no key.

The fake records are spec 079's fixture cycle (`tests/fixtures/quality/cycle/`: one weak row, `PROBLEM · respondent ·
problem.importance · item`, fixed at a registry row) with a decisions file written per test; the acceptance's dry run
reads the real cycle `quality/cycles/20261028-f48f256.md` and the real file of record.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from quality import cycle, decisions as dec, table
from tests import test_quality_cycle_079 as c079

REPO = Path(__file__).resolve().parent.parent
RECORD = c079.RECORD
CLOUD = c079.CLOUD
WEAK_ROW = c079.WEAK_ROW
F48 = REPO / "quality" / "cycles" / "20261028-f48f256.md"
F48_ADVICE = REPO / "quality" / "cycles" / "20261028-f48f256-advice.md"

ROW = {"scope": "PROBLEM", "audience": "respondent", "dimension": "problem.importance", "screen": "item"}


def entry(**kw) -> dict:
    base = {"id": "D-1", "cycle": "20261101-abcdef1", "proposals": [1], "row": dict(ROW),
            "fix": "dimension-registry.json", "decision": "declined", "until": "never",
            "why": "FIXTURE-WHY-ONE: the founder said no."}
    base.update(kw)
    return base


def _toml_value(v) -> str:
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml_value(x)}" for k, x in v.items()) + " }"
    return json.dumps(v, ensure_ascii=False)


def write(path: Path, *entries: dict) -> Path:
    blocks = ["[[decision]]\n" + "".join(f"{k} = {_toml_value(v)}\n" for k, v in e.items()) for e in entries]
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


class Never:
    """A runner that fails the test if anything is called: a dry run and a snoozed row send nothing."""

    def __init__(self):
        self.seen = []

    def __call__(self, argv, **kw):
        self.seen.append(argv)
        raise AssertionError(f"nothing is called: {argv}")


def dry(capsys, decisions_path: Path, record: Path = RECORD) -> tuple[int, str]:
    runner = Never()
    code = cycle.advise(["--cycle", str(record), "--cloud", str(CLOUD), "--decisions", str(decisions_path),
                         "--dry-run"], runner=runner)
    assert runner.seen == []
    return code, capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ FR-1 the record

def test_the_file_of_record_parses_and_every_row_names_scored_scopes_and_screens():
    found = dec.load(dec.DECISIONS_PATH)
    assert len(found) == 20 and [d["id"] for d in found] == [f"D-2026-10-29-{i:02d}" for i in range(1, 21)]
    records = {p.stem for p in cycle.record_files(REPO / "quality" / "cycles")}
    for d in found:
        assert d["cycle"] in records, f"{d['id']} names a committed cycle record"
        assert set(d["_row"]["scope"] or cycle.SCOPES) <= set(cycle.SCOPES), d["id"]
        assert set(d["_row"]["audience"] or ("founder",)) <= {"founder", "respondent"}, d["id"]
        assert set(d["_row"]["screen"] or dec.SCREENS) <= set(dec.SCREENS), d["id"]
        assert d["decision"] != "taken" or d.get("spec"), f"{d['id']}: a taken decision names its spec"
        assert d["why"].strip()
    assert {d["decision"] for d in found} == {"taken", "declined", "held"}
    assert {d["until"] for d in found} == {"spec-merged", "never", "20261028-f48f256"}
    assert not any(d.get("merged") for d in found), "nothing it names had merged when it was written"


def test_the_screens_are_the_ones_the_cycle_scores():
    kinds = set()
    for path in [*(REPO / "quality" / "scores").rglob("*.json"), *c079.SCORES.rglob("*.json")]:
        body = json.loads(path.read_text(encoding="utf-8"))
        kinds |= {s["kind"] for s in body.get("screens") or []}
        if body.get("insights"):
            kinds.add("insights")
    assert kinds and kinds <= set(dec.SCREENS), sorted(kinds - set(dec.SCREENS))
    assert set(table._FOUNDER_FILES) <= set(dec.SCREENS)


@pytest.mark.parametrize("change, said", [
    ({"why": None}, "lacks why"),
    ({"decision": "maybe"}, "decision 'maybe' is not one of taken, declined, held"),
    ({"until": "soon"}, "until 'soon' is not one of spec-merged, never or a cycle id"),
    ({"row": {**ROW, "scope": "EVERYTHING"}}, "row.scope names EVERYTHING, which the cycle does not score"),
    ({"row": {**ROW, "audience": "investor"}}, "row.audience names investor, which the cycle does not score"),
    ({"row": {**ROW, "screen": ["item", "homepage"]}}, "row.screen names homepage, which the cycle does not score"),
    ({"row": {**ROW, "dimension": "importance"}}, "row.dimension names importance"),
    ({"row": {"scope": "*", "audience": "*", "screen": "*"}}, "row must carry exactly scope, audience, dimension"),
    ({"row": {**ROW, "screen": ["*", "item"]}}, "`*` stands alone"),
    ({"decision": "taken", "until": "spec-merged"}, "a taken decision names the spec(s) it became"),
    ({"merged": "abc1234"}, "merged ends a spec-merged snooze only"),
    ({"untill": "never"}, "carries untill, which no decision has"),
    ({"cycle": "last week"}, "is not a cycle id"),
    ({"fix": []}, "fix is [] -- a string, a list of strings, or `*`"),
])
def test_a_file_that_is_not_the_shape_is_refused_by_name(tmp_path, change, said):
    e = {k: v for k, v in {**entry(), **change}.items() if v is not None}
    with pytest.raises(dec.DecisionsError) as raised:
        dec.load(write(tmp_path / "decisions.toml", e))
    assert said in str(raised.value)


def test_an_id_used_twice_is_refused_and_no_file_is_no_decision(tmp_path):
    with pytest.raises(dec.DecisionsError, match="the id D-1 is used twice"):
        dec.load(write(tmp_path / "d.toml", entry(), entry()))
    assert dec.load(tmp_path / "none.toml") == []
