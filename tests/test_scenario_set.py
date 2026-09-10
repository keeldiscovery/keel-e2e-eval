"""The set itself (spec 010 FR-016/T055, research R12; spec 012 adds the eighth, spec 013 the
ninth, spec 015's second half the tenth and eleventh, and spec 016 the twelfth): **twelve**
scenarios, **two** of them live.

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
    # spec 012-bundled-runtime: the runtime that travelled inside the skill, resolved with no
    # `KEEL_RUNTIME_PATH` anywhere, connected, said twice, and disconnected again (A-7).
    "test_s008_bundled_runtime.py",
    # spec 013-skill-distribution: four packaging trees, four installers, one skill -- the same
    # contract shapes byte for byte on the far side of an install (A-6).
    "test_s009_skill_distribution.py",
    # spec 015-stub-oidc-and-two-founders, second half (keel-cloud google-sign-in-design.md
    # §10.6): two founders on one instance, and every one of another founder's routes a bare 404.
    "test_s010_two_founders.py",
    # ... and §10.7: the callback's own refusals, each with the founder-voiced line §5.5 names.
    "test_s011_bad_token.py",
    # spec 016-copilot-e2e: GitHub Copilot as the **host** that loads and runs the skill, and as
    # the **thinker** that answers the journey. The third named LLM place, argued for on
    # AGENTS.md's own terms rather than quietly written -- see `test_the_third_llm_place_is_named`.
    "test_s012_copilot_host_and_thinker.py",
}


def _scenario_files() -> set[str]:
    return {p.name for p in EVALS.glob("test_s*.py")}


def test_there_are_twelve_scenarios():
    assert _scenario_files() == EXPECTED, (
        "the scenario set moved; README.md and AGENTS.md name these twelve by number")


def test_the_two_new_scenarios_are_deterministic_and_in_the_smoke():
    """S-010 and S-011 are the whole reason design decisions 12 and 13 exist: isolation and the
    refusal table are proven by `make eval`, on no model and no money, rather than by a live run
    somebody has to opt into."""
    for name in ("test_s010_two_founders.py", "test_s011_bad_token.py"):
        body = (EVALS / name).read_text()
        assert "pytest.mark.live" not in body, f"{name} must not be live"
        assert "claude" not in body.lower(), (
            f"{name} names a model; both new scenarios are deterministic by design")


def test_exactly_two_scenarios_are_live():
    """AGENTS.md's rule is not "no third LLM" -- it is that a third **is argued for and added to
    that line rather than quietly written**. Spec 016 is that argument and S-012 is that third
    place, so this test moved deliberately and in the same commit as the sentence it enforces."""
    live = {name for name in _scenario_files()
            if "pytestmark = pytest.mark.live" in (EVALS / name).read_text()}
    assert live == {"test_s004_stranger_who_gives_orders.py",
                     "test_s012_copilot_host_and_thinker.py"}, (
        "the named LLM exceptions do not change in number or in name without AGENTS.md changing "
        f"with them; this run found {sorted(live)}")


def test_the_third_llm_place_is_named_in_agents_md():
    """The other half of the amendment, and the half a test can hold: a live scenario that
    AGENTS.md does not name is exactly the "quietly written" third the rule forbids."""
    agents = (REPO / "AGENTS.md").read_text()
    assert "test_s012_copilot_host_and_thinker.py" in agents, (
        "S-012 is live and AGENTS.md does not name it -- the LLM exceptions are named in one "
        "place on purpose")
    assert "three named places" in agents, (
        "AGENTS.md still says there are two named LLM places while three exist")


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
