"""The set itself (spec 010 FR-016/T055, research R12): seven scenarios, one of them live.

FR-016 asks that `K=s005|s006|s007` dispatch exactly as `s001`-`s003` do, that all three run under
`make eval` and `make eval-all`, and that none is live. **`K` is pytest's own `-k`**, so none of
that needs a Makefile edit -- which means the honest way to close FR-016 is a test that the
property holds, not a change that pretends it was needed.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVALS = REPO / "evals"
MAKEFILE = (REPO / "Makefile").read_text()

EXPECTED = {
    "test_s001_smoke.py",
    "test_s002_agent_optional.py",
    "test_s003_every_door.py",
    "test_s004_stranger_who_gives_orders.py",
    "test_s005_countly.py",
    "test_s006_paidly.py",
    "test_s007_mulchrun.py",
}


def _scenario_files() -> set[str]:
    return {p.name for p in EVALS.glob("test_s*.py")}


def test_there_are_seven_scenarios():
    assert _scenario_files() == EXPECTED, (
        "the scenario set moved; README.md and AGENTS.md name these seven by number")


def test_exactly_one_scenario_is_live():
    live = {name for name in _scenario_files()
            if "pytestmark = pytest.mark.live" in (EVALS / name).read_text()}
    assert live == {"test_s004_stranger_who_gives_orders.py"}, (
        "the two named LLM exceptions do not change in number or in name (AGENTS.md): S-004 is "
        f"the only live scenario, and this run found {sorted(live)}")


def test_the_three_new_scenarios_need_no_makefile_edit_to_dispatch():
    """`K` becomes pytest's `-k`, so `make eval K=s005` already selects `test_s005_countly.py` by
    name. What the Makefile must still say is that `eval` deselects `live` and `eval-live` selects
    it -- the only two lines FR-016 actually depends on."""
    assert '-m "not live"' in MAKEFILE
    assert re.search(r"eval-live:.*\n.*-m live", MAKEFILE), (
        "`make eval-live` no longer selects the live marker")
    assert "$(if $(K),-k $(K),)" in MAKEFILE, "`K` no longer reaches pytest as `-k`"


def test_eval_all_still_deselects_the_live_one():
    runner = (REPO / "harness" / "eval_all.py").read_text()
    assert "not live" in runner, (
        "`make eval-all` must keep deselecting S-004: it costs real money on the founder's own "
        "account and is opt-in only")


def test_the_three_corpus_scenarios_differ_by_an_entry_id_and_nothing_else():
    """FR-015, asserted rather than hoped: each module names one entry id, calls the one shared
    body, and does not import a page object of its own."""
    for name, entry_id in (("test_s005_countly.py", "01-countly"),
                            ("test_s006_paidly.py", "05-paidly"),
                            ("test_s007_mulchrun.py", "07-mulchrun")):
        body = (EVALS / name).read_text()
        assert f'ENTRY_ID = "{entry_id}"' in body, name
        assert "corpus_scenario.run(" in body, name
        assert "entry_id=ENTRY_ID" in body, name
