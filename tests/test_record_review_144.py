"""Spec 144 FR-3 -- the record: the review line counts the three dimensions the review reads and names the Checks shot
again after the band; the readers read a `check-{dim}-reviewed` screen as its dimension's (card and all); `make
read-table` folds it into its dimension's row. RUBRIC_VERSION stands; the readers' prompts are untouched.

No model, no stack, no network: fixture bundles and score files only.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from quality import cards, cycle, readers, rubric, table

FX = Path(__file__).resolve().parent / "fixtures" / "quality" / "scores"
IMP = "problem.importance"
COMPAT = "solution.compatibility"
CHANGED = {IMP: {"review_changed": [{"typed": "a", "label": "b", "why": "w"}, {"typed": "c", "label": None, "why": "w"}],
                 "band": {"line": "Keel changed one row and put one aside.", "why": "w"}},
           COMPAT: {"review_changed": [{"typed": "d", "label": "e", "why": "w"}], "band": {"line": "x", "why": "w"}}}


def _check(n: int, name: str, belief: str) -> dict:
    return {"n": n, "screen": name, "kicker": "Problem", "rows": ["one", "two"],
            "keel read back": {"belief line on screen": belief}}


def test_the_reviewed_check_is_its_dimensions_screen():
    """FR-3: the second shot is read as a Check of its dimension -- kind `check`, the dimension's card (R7) -- and the
    founder-reader's checked beliefs name it *after Keel's review*."""
    bundle = {"founder_screens": [_check(1, f"check-{IMP}", "Of these three ..."),
                                  _check(2, f"check-{IMP}-reviewed", "Of these three, after ...")]}
    first, second = readers.founder_screens(bundle)
    assert (second.kind, second.dimension, second.screen) == ("check", IMP, f"check-{IMP}-reviewed")
    assert second.card == first.card == IMP and cards.card_for(second.dimension) is not None
    assert second.meta()["dimension_card"] == IMP
    beliefs = readers.checked_beliefs(bundle).splitlines()
    assert beliefs == [f"- {IMP} (Problem): Of these three ...",
                       f"- {IMP}, after Keel's review (Problem): Of these three, after ..."]
    assert cards.fold_reviewed(f"{IMP}-reviewed") == IMP and cards.fold_reviewed(IMP) == IMP
    assert cards.fold_reviewed(None) is None


def test_read_table_folds_the_reviewed_screens_into_their_dimension(tmp_path):
    """FR-3: one row per (scope, dimension, audience, kind) -- a `check-{dim}-reviewed` screen counts in its dimension's
    Check row, whether its score file recorded the dimension folded (as the readers now do) or not."""
    src = sorted(FX.glob("bb-beta/*-r5-*.json"))[0]
    obj = json.loads(src.read_text())
    base = obj["screens"][0]
    for n, (screen, dim) in enumerate(((f"check-{IMP}", IMP), (f"check-{IMP}-reviewed", IMP),
                                       (f"check-{IMP}-reviewed", f"{IMP}-reviewed")), start=10):
        s = copy.deepcopy(base)
        s.update(n=n, screen=screen, kind="check", dimension=dim, dimension_card=IMP, r7=1, why7="why 7")
        obj["screens"].append(s)
    obj["summary"] = rubric.summaries(obj["screens"], obj.get("insights") or [])
    (tmp_path / "bb-beta").mkdir()
    (tmp_path / "bb-beta" / src.name).write_text(json.dumps(obj))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(table.load_scores(tmp_path)))}
    key = f"PROBLEM · founder · {IMP} · check"
    assert rows[key]["screens"] == 3
    assert not any(k.endswith(f"{IMP}-reviewed · check") for k in rows)
    row = rows[key]
    failing = cycle.failing_screens({**row, "weak_on": ["r7"]}, table.load_scores(tmp_path))
    assert sum(f"check-{IMP}-reviewed" in line for line in failing) == 2, "the adviser reads them under the row"


def test_the_record_counts_the_three_dimensions_and_names_the_second_shots():
    """FR-3: per bundle, the three dimensions counted (zeros kept) and the second shots named; the head's review line
    says both, by walk."""
    assert cycle.review_dims(CHANGED) == {IMP: {"changed": 1, "put_aside": 1},
                                          "problem.current_solution_satisfaction": {"changed": 0, "put_aside": 0},
                                          COMPAT: {"changed": 1, "put_aside": 0}}
    screens = [{"screen": f"check-{IMP}"}, {"screen": f"check-{IMP}-reviewed"}, {"screen": f"choose-{COMPAT}"},
               {"screen": f"check-{COMPAT}-reviewed"}]
    assert cycle.review_shots(screens) == [f"check-{IMP}-reviewed", f"check-{COMPAT}-reviewed"]
    d = {"review_switch": "ON", "studies": [
        {"entry": "21-codyco", "scope": "ALL", "review_rows": cycle.review_rows(CHANGED),
         "review_dims": cycle.review_dims(CHANGED), "review_shots": cycle.review_shots(screens)},
        {"entry": "10-palus", "scope": "ALL", "review_rows": {"changed": 0, "put_aside": 0},
         "review_dims": cycle.review_dims({}), "review_shots": []}]}
    assert cycle.review_line(d) == [
        "  - the review (spec 209, keel-cloud 232, 233): 2 founder rows changed and 1 put aside over 2 walks (each "
        "bundle's `lists_reviewed`) -- Importance 1 changed / 1 put aside, Current solution 0 changed / 0 put aside, "
        "Compatibility 1 changed / 0 put aside; the Check shot again after the band (keel-cloud 233, spec 144) on 2 "
        f"screens: 21-codyco · ALL `check-{IMP}-reviewed`, 21-codyco · ALL `check-{COMPAT}-reviewed`; the readers "
        "scored the screens as served, the second shots under their dimension"]
    d["studies"] = [d["studies"][1]]
    assert cycle.review_line(d)[0].endswith("; no Check stayed with the band (no second shot); the readers scored the "
                                            "screens as served, the second shots under their dimension")
    assert cycle.review_line({**d, "review_switch": "OFF"}) == []


def test_a_study_reads_its_bundles_review(tmp_path, monkeypatch):
    """FR-3: a walked study carries its bundle's per-dimension counts and second shots (only where the bundle is 144's:
    it records `review_holds`); the record's data block keeps them, and drops them where None."""
    study = cycle.Study(entry="21-codyco", scope="ALL")
    data = cycle._study_data(study)
    assert "review_dims" not in data and "review_shots" not in data
    study.review_dims, study.review_shots = cycle.review_dims(CHANGED), [f"check-{IMP}-reviewed"]
    data = cycle._study_data(study)
    assert data["review_shots"] == [f"check-{IMP}-reviewed"] and data["review_dims"][COMPAT]["changed"] == 1


def test_the_rubric_and_the_prompts_stand():
    """FR-3: RUBRIC_VERSION stands at 5; no reader prompt names the second shot."""
    assert rubric.RUBRIC_VERSION == 5
    prompts = Path(readers.__file__).resolve().parent / "readers"
    assert not any("-reviewed" in p.read_text(encoding="utf-8") for p in prompts.glob("*.md")
                   if p.name != "dimensions.md")
