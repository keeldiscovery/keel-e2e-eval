"""Spec 130 FR-1 / FR-3: the three sharing journeys (S-018, S-019, S-020) wired onto S-016's walk and marked for
`make remote` -- the structure only; the journeys themselves run on the staging twin, by the coordinator."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from evals import scope_journey, sharing_leg

ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------- FR-1 / FR-3: the journeys

@pytest.mark.parametrize("module, runs", [("test_s018_share_link", "run_link"),
                                          ("test_s019_share_viewer", "run_viewer"),
                                          ("test_s020_share_co_founder", "run_co_founder")])
def test_the_three_journeys_are_marked_for_make_remote(module, runs):
    import importlib                                                    # noqa: PLC0415
    mod = importlib.import_module(f"evals.{module}")
    assert any(m.name == "remote" for m in (mod.pytestmark if isinstance(mod.pytestmark, list) else [mod.pytestmark]))
    assert f"sharing_leg.{runs}(" in inspect.getsource(mod)
    assert "remote:" in (ROOT / "pytest.ini").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert 'remote: venv\n\tKEEL_EVAL_PROFILE=remote $(PY) -m pytest evals -q -m "remote and not live"' in makefile


def test_the_journeys_walk_s016s_study_to_its_answers_then_share():
    assert sharing_leg.ENTRY_FROM is scope_journey.money_entry and sharing_leg.SCOPE == "COMMERCIAL"
    source = inspect.getsource(scope_journey.run)
    assert "walk(j, before_lock=before_lock)" in source and "after(j)" in source
    assert "before_lock(j)\n    cs.leg_lock(j)" in inspect.getsource(scope_journey.walk)
    assert "before_lock=co.before_lock, after=co.after" in inspect.getsource(sharing_leg.run_co_founder)
    assert sharing_leg.EXTRA_PROJECTS + 1 == 6, "FR-3: six own projects, two pages of five"
    assert sharing_leg.REWORDED != scope_journey.FRICTION["answer"]["items"][2]["label"]
    assert len(sharing_leg.REWORDED.split()) <= 9, "a Check row's nine words"
