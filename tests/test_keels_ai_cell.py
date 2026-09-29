"""The **other door**, held stackless (spec `024-keels-ai-cell`).

S-012 has been the journey through a *host* since spec 019. Spec 024 widens it by a **door**:
keel-cloud `canon/designs/ai-credits-design.md` §6 -- *"The door decides the AI"* -- so a founder
who signs up with Google runs on Keel's own AI, with no CLI, no plugin, no skill, no device
approval and no runtime anywhere, and keel-cloud answers every job on its own Anthropic account.

Everything about that door that can be known without a twin is known here: the axis, the bundle's
name, the two vocabularies (`keel` the door and `api` the wire), the refusals that keep leg one
*skipped* rather than *quietly passed*, the wire readers, the cell, the coverage rules that keep
it off every merge, and the make target.

Nothing here shells anything, needs a stack, opens a browser or spends a credit.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from harness import agent_host, keel_host
from matrix import cells as matrix_cells

REPO = Path(__file__).resolve().parent.parent
SCENARIO = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text(encoding="utf-8")
MAKEFILE = (REPO / "Makefile").read_text(encoding="utf-8")
WORKFLOW = (REPO / ".github" / "workflows" / "matrix.yml").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------- the axis, widened

def test_keel_is_a_value_of_the_journeys_host_axis():
    """One scenario, four doors. A fourteenth scenario would have been a fourth named LLM place
    in `AGENTS.md` and would have had to be argued for; widening a named place is what the
    amendment rule permits, and is what specs 019 and 022 already did."""
    assert agent_host.journey_host({"KEEL_JOURNEY_HOST": "keel"}) == "keel"
    assert "keel" in agent_host.HOSTS


def test_the_default_is_still_copilot_so_every_earlier_command_still_means_what_it_meant():
    assert agent_host.journey_host({}) == "copilot"
    assert agent_host.DEFAULT_HOST == "copilot"


def test_a_typo_near_the_new_value_is_still_refused_by_name():
    with pytest.raises(agent_host.UnknownHost) as exc:
        agent_host.journey_host({"KEEL_JOURNEY_HOST": "keels"})
    assert "keels" in str(exc.value) and "keel" in str(exc.value)


def test_only_the_keel_door_has_no_cli():
    """What the rest of the harness and `matrix/cells.py` actually branch on. Three hosts bring a
    founder's own CLI; one is a door."""
    assert agent_host.HOSTS_WITHOUT_A_CLI == ("keel",)
    assert agent_host.has_a_cli("claude") and agent_host.has_a_cli("copilot")
    assert agent_host.has_a_cli("codex")
    assert not agent_host.has_a_cli("keel")


def test_the_door_is_called_keel_and_the_wire_is_called_api():
    """spec 024 FR-002, the decision this cell turns on. `keel` is the door -- the cell id, the
    bundle name, the summary row, the founder in the twin's picker. `api` is what keel-cloud's own
    executor reports as `execution.host` (keel-cloud spec 045 FR-043), because there is no CLI and
    no host, only an HTTP client against a provider. Two words, two subjects, and the bundle
    carries both."""
    assert agent_host.EXECUTOR_FOR_HOST["keel"] == "api"
    assert keel_host.KeelHost.executor == "api"
    assert agent_host.EXECUTOR_FOR_HOST["claude"] == "claude"
    assert agent_host.EXECUTOR_FOR_HOST["copilot"] == "copilot"
    assert agent_host.EXECUTOR_FOR_HOST["codex"] == "codex"


def test_the_bundle_is_named_for_the_door():
    assert agent_host.bundle_slug("keel", "full", "none") == "s012-journey-keel"
    assert agent_host.bundle_slug("keel", "short", "none") == "s012-journey-keel-short"


def test_the_absence_of_an_install_is_never_spelled_in_a_name():
    """`none` is the absence of a road, not a third one -- a bundle called
    `s012-journey-keel-none` would read as a third packaging of a skill that was never installed.
    The Spec Kit road, which *is* a road, still names itself."""
    assert agent_host.NO_INSTALL == "none"
    assert "none" in agent_host.INSTALLS
    assert agent_host.bundle_slug("keel", "full", agent_host.NO_INSTALL) == "s012-journey-keel"
    assert agent_host.bundle_slug("claude", "full", "speckit") == "s012-journey-claude-speckit"


def test_the_grant_is_written_down_once():
    """Asserted twice on that door -- as the integer `/v2/me` answers and as the sentence keel-web
    renders from it -- so a run where only one moved says which (keel-cloud spec 044 FR-017)."""
    assert agent_host.KEELS_AI_GRANT == 1500
    assert f"{agent_host.KEELS_AI_GRANT:,} credits available" == "1,500 credits available"


# -------------------------------------------------------- leg one is skipped, and it is refused

@pytest.mark.parametrize("method,args", [
    ("add_marketplace", ()),
    ("install_plugin", ()),
    ("plugin_list", ()),
    ("skill_proof", ()),
    ("install_extension", (Path("/nowhere"),)),
    ("extension_proof", ()),
    ("envelope_facts", ({},)),
])
def test_every_host_leg_method_raises_rather_than_returning_an_empty_result(method, args, tmp_path):
    """**The difference between *skipped* and *asserted loosely* is this file.** A method that
    returned `{"found": False}` would let a future edit assert something about an install that
    never happened and pass; one that raises makes that edit fail at the first call, with a
    sentence naming the spec."""
    host = keel_host.KeelHost(home=tmp_path / "no-host-home", keel_home=tmp_path / "keel-home",
                              base_url="http://localhost:18080", artifacts=tmp_path / "art")
    with pytest.raises(keel_host.NoHostHere) as exc:
        getattr(host, method)(*args)
    assert "024" in str(exc.value)


def test_saying_the_founders_three_words_to_this_door_raises(tmp_path):
    host = keel_host.KeelHost(home=tmp_path / "no-host-home", keel_home=tmp_path / "keel-home",
                              base_url="http://localhost:18080", artifacts=tmp_path / "art")
    with pytest.raises(keel_host.NoHostHere):
        host.say("keel connect", slug="connect-1")


def test_this_door_runs_no_subprocess_and_counts_them(tmp_path):
    host = keel_host.KeelHost(home=tmp_path / "no-host-home", keel_home=tmp_path / "keel-home",
                              base_url="http://localhost:18080", artifacts=tmp_path / "art")
    assert host.subprocesses_run == 0


def test_the_fresh_keel_home_is_left_empty_because_nothing_will_ever_write_in_it(tmp_path):
    """Every other host writes `config.json` there so the runtime the skill starts and the runtime
    this harness asks are provably the same Keel. There is no runtime here, and that one file
    would cost the scenario its cleanest assertion."""
    keel_home = tmp_path / "keel-home"
    host = keel_host.KeelHost(home=tmp_path / "no-host-home", keel_home=keel_home,
                              base_url="http://localhost:18080", artifacts=tmp_path / "art")
    assert host.write_home_config() is None
    assert keel_home.is_dir() and list(keel_home.iterdir()) == []


def test_readiness_is_free_and_says_why_there_is_nothing_to_check():
    ready = agent_host.readiness("keel")
    assert ready["ok"] is True and ready["reason"] is None
    assert ready["version"] is None
    assert "no host CLI" in ready["why"]


def test_the_credential_plan_says_there_is_none_and_whose_key_it_is(tmp_path):
    host = keel_host.KeelHost(home=tmp_path / "no-host-home", keel_home=tmp_path / "keel-home",
                              base_url="http://localhost:18080", artifacts=tmp_path / "art")
    plan = host.credential_plan()
    assert plan["variable"] is None and plan["isolated_home"] is False
    assert "none" in plan["how"] and "never leaves" in plan["how"]


def test_the_host_type_lookup_finds_it():
    assert agent_host.host_type("keel") is keel_host.KeelHost


# ------------------------------------------------------------------- what the wire is read for

def test_the_execution_report_is_read_for_the_host_the_cost_and_the_two_models():
    facts = keel_host.execution_facts({
        "job_id": "j1", "status": "COMPLETED",
        "execution": {"host": "api", "host_version": "anthropic-java/1.2.3",
                      "model_requested": "claude-sonnet-5", "model_used": "claude-sonnet-5",
                      "retried_unpinned": False, "actual_cost_micro_usd": 307484}})
    assert facts["host"] == "api"
    assert facts["actual_cost_micro_usd"] == 307484
    assert facts["cost_reported"] is True
    assert facts["model_requested"] == "claude-sonnet-5"
    assert facts["model_used"] == "claude-sonnet-5"


def test_a_missing_cost_reads_as_not_reported_rather_than_as_zero():
    """keel-cloud's `actual_cost_micro_usd` is optional and **null on every job today** -- X6 is
    deliberately unmet until an executor reports it. A reader that turned null into 0 would let
    the cell pass on the one thing spec 045 exists to deliver."""
    facts = keel_host.execution_facts({"job_id": "j1", "execution": {"host": "api"}})
    assert facts["actual_cost_micro_usd"] is None
    assert facts["cost_reported"] is False


def test_a_boolean_is_not_an_integer_of_micro_dollars():
    facts = keel_host.execution_facts({"execution": {"host": "api",
                                                     "actual_cost_micro_usd": True}})
    assert facts["cost_reported"] is False


def test_a_job_with_no_execution_block_at_all_reads_as_nothing_reported():
    facts = keel_host.execution_facts({"job_id": "j1", "status": "FAILED"})
    assert facts["host"] is None and facts["cost_reported"] is False


@pytest.mark.parametrize("reason", sorted(keel_host.NAMED_REASONS))
def test_each_of_keels_ais_four_named_reasons_is_found_in_the_message_it_travels_in(reason):
    """keel-cloud spec 045 Assumption 11: **none of the four is an `error.code`.** The five wire
    codes are not extended, because a sixth would be a founder-visible vocabulary change keel-web
    has no spec for -- so the reason rides in `error_message`, which is free text, and the code
    beside it is one of the ordinary five."""
    assert keel_host.named_reason(f"LLM_UNAVAILABLE: {reason}") == reason
    assert keel_host.named_reason(f"something before {reason} and after") == reason


def test_an_ordinary_failure_names_none_of_them():
    assert keel_host.named_reason("EXECUTOR_TIMEOUT") is None
    assert keel_host.named_reason("") is None
    assert keel_host.named_reason(None) is None


def test_the_four_reasons_are_the_four_spec_045_names():
    assert sorted(keel_host.NAMED_REASONS) == [
        "KEEL_AI_DAILY_CAP", "KEEL_AI_DISABLED", "KEEL_AI_RESTARTED", "KEEL_AI_TIMEOUT"]


# ------------------------------------------------------------------ what the scenario says it does

def test_the_scenario_reads_the_door_off_the_host_axis_and_nowhere_else():
    assert "KEELS_AI = not agent_host.has_a_cli(HOST)" in SCENARIO


def test_the_founder_signs_up_at_the_signup_door_and_signs_in_everywhere_else():
    """keel-cloud spec 044 FR-014: the door is the whole of the message. keel-cloud reads it off
    the pre-login record's own stored `return_to` -- `/` from `/signup`, `/connect?user_code=…`
    from the code story -- so nothing about `ai_path` travels from this harness, and nothing
    could."""
    assert "auth.sign_up(founder_one)" in SCENARIO
    assert "auth.sign_in(founder_one)" in SCENARIO


def test_the_scenario_fails_fast_on_a_shut_door_rather_than_waiting_out_a_timeout():
    """spec 024 FR-010. `KEEL_AI_DISABLED` is answered before a socket is opened; a run that
    waited five minutes for it and then reported a timeout would be reporting the referee's own
    patience instead of the product's own sentence."""
    assert "_refuse_if_the_door_is_shut(recorder, get_json, project_id)" in SCENARIO
    assert "NAMED_REASON_POLL_S" in SCENARIO
    assert "class KeelsAiRefused" in SCENARIO


def test_only_the_keel_door_chunks_its_wait_and_the_three_cli_hosts_are_untouched():
    """Do not weaken any existing cell: on the three CLI doors the wait is the one call it has
    been since spec 016, in one branch guarded by the axis."""
    assert "if not KEELS_AI:\n        return chat.wait_for_agent_turn(timeout_s=timeout_s)" in SCENARIO


def test_the_follow_ups_are_never_spent_on_a_door_with_no_key_behind_it():
    assert ("if KEELS_AI:\n            _refuse_if_the_door_is_shut(recorder, get_json, "
            "project_id)") in SCENARIO


def test_the_scenario_asserts_the_doors_own_six_facts():
    """FR-005 through FR-009, each by the words it is asserted in."""
    for needle in (
        '"aiPath") == "KEEL"',                       # FR-005, the wire
        "credits available",                         # FR-005, the shell line
        "shell.agent_line_present()",                # FR-005, the absence of the other line
        "credits_after_first_job < credits_before",  # FR-006
        'r["host"] != EXPECTED_EXECUTOR',            # FR-007, execution.host == "api"
        'not r["cost_reported"]',                    # FR-007, actual_cost_micro_usd
        "host.subprocesses_run == 0",                # FR-008
        "_the_screens_say_keel",                     # FR-009
    ):
        assert needle in SCENARIO, needle


def test_nothing_on_the_keel_door_shells_the_skills_way_out():
    """spec 011's `keel disconnect` tail is the founder's own door out and proves
    `agent.connected` went false. Here nothing was ever connected, so shelling that script would
    assert something about a repository this door does not touch."""
    assert "there is no way out to take" in SCENARIO
    assert SCENARIO.count("disconnect_via_skill_script") == 1, (
        "the disconnect must stay in the CLI-door arm alone")


def test_the_bundle_says_it_is_the_keel_door_and_carries_no_cli_version():
    assert "_the_keel_door_in_one_line" in SCENARIO
    assert '"cli, why"' in SCENARIO


# --------------------------------------------------------------------------------- the cell

def test_the_matrix_knows_keel_as_an_axis_value_with_no_cli():
    matrix = matrix_cells.load()
    assert matrix.hostless_hosts == ("keel",)
    assert "keel" not in matrix.axes["host"], (
        "a hostless door in `[axes].host` would make the weekly product owe an OS x Python grid "
        "for a cell that installs nothing and executes nothing")
    assert "keel" in matrix.all_hosts


def test_there_is_exactly_one_keel_cell_and_it_is_weekly_whole_and_installs_nothing():
    matrix = matrix_cells.load()
    weekly = [c for c in matrix.cells("weekly") if c.host == "keel"]
    assert [c.id for c in weekly] == ["macos-latest-keel-py3.13"]
    assert weekly[0].legs == "full"
    assert weekly[0].install == matrix_cells.NO_INSTALL
    assert weekly[0].scenarios == ("s012",)
    for other in ("per_change", "nightly"):
        assert not [c for c in matrix.cells(other) if c.host == "keel"]


def test_the_cells_id_does_not_spell_the_absence_of_an_install():
    cell = matrix_cells.Cell(os="macos-latest", host="keel", python="3.13", scenarios=("s012",),
                             install=matrix_cells.NO_INSTALL)
    assert cell.id == "macos-latest-keel-py3.13"


def test_the_weekly_set_is_nine_cells_and_per_change_is_still_one():
    matrix = matrix_cells.load()
    assert len(matrix.cells("weekly")) == 9
    assert len(matrix.cells("per_change")) == 1
    assert matrix.cells("per_change")[0].host == "claude"


def test_a_keel_cell_in_per_change_is_refused_and_the_message_says_whose_money_it_is():
    """The rule that matters most. Every other live cell spends the founder's own plan; this one
    spends **Keel's** Anthropic account, the company's, at about $2.44 of inference a journey. A
    merge that bought one would bill the company on every push."""
    matrix = matrix_cells.load()
    broken = matrix_cells.Matrix(
        axes=matrix.axes, live=matrix.live, default_scenarios=matrix.default_scenarios,
        sets={**matrix.sets,
              "per_change": matrix.sets["per_change"] + (
                  matrix_cells.Cell(os="macos-latest", host="keel", python="3.13",
                                    scenarios=("s012",), install=matrix_cells.NO_INSTALL),)},
        unmeasured_hosts=matrix.unmeasured_hosts, everyday_hosts=matrix.everyday_hosts,
        everyday_os=matrix.everyday_os, suspended_os=matrix.suspended_os,
        suspended_python=matrix.suspended_python, hostless_hosts=matrix.hostless_hosts)
    problems = matrix_cells.coverage_problems(broken)
    assert any("Keel's** Anthropic account" in p or "Keel's own AI" in p for p in problems), problems


def test_a_second_keel_cell_is_refused():
    matrix = matrix_cells.load()
    broken = matrix_cells.Matrix(
        axes=matrix.axes, live=matrix.live, default_scenarios=matrix.default_scenarios,
        sets={**matrix.sets,
              "weekly": matrix.sets["weekly"] + (
                  matrix_cells.Cell(os="windows-latest", host="keel", python="3.13",
                                    scenarios=("s012",), install=matrix_cells.NO_INSTALL),)},
        unmeasured_hosts=matrix.unmeasured_hosts, everyday_hosts=matrix.everyday_hosts,
        everyday_os=matrix.everyday_os, suspended_os=matrix.suspended_os,
        suspended_python=matrix.suspended_python, hostless_hosts=matrix.hostless_hosts)
    problems = matrix_cells.coverage_problems(broken)
    assert any("exactly one Keel's-AI cell" in p for p in problems), problems


def test_the_keel_cell_does_not_disturb_the_weekly_product_or_the_spec_kit_rule():
    """It is not part of the product and it is not a packaging road, so the six-cell product, the
    one Spec Kit cell and the 3.9 floor are all still owed and still counted without it."""
    assert matrix_cells.coverage_problems(matrix_cells.load()) == []


def test_the_shipped_file_validates():
    matrix_cells.validate(matrix_cells.load())


def test_the_workflow_needs_no_change_for_it():
    """spec 024 FR-014: every host-specific thing the cell job does is already gated on
    `matrix.cell.host == '<name>'`, so a `keel` cell installs no CLI, receives no secret and pins
    no model -- which is right, because the only key involved lives on the twin and is
    keel-cloud's."""
    for gate in ("matrix.cell.host == 'claude'", "matrix.cell.host == 'copilot'",
                 "matrix.cell.host == 'codex'"):
        assert gate in WORKFLOW
    assert "matrix.cell.host == 'keel'" not in WORKFLOW, (
        "a keel cell must match no host-gated step: it installs nothing and holds no secret")


# ------------------------------------------------------------------------------ the one command

def test_the_make_target_is_the_journey_with_the_host_axis_set_and_nothing_else():
    assert "keels-ai: venv" in MAKEFILE
    recipe = MAKEFILE.split("keels-ai: venv", 1)[1].split("\n\n", 1)[0]
    assert "eval-live K=s012 HOST=keel" in recipe
    assert "LEGS=full" in recipe
    assert "PROFILE=$(if $(PROFILE),$(PROFILE),remote)" in recipe, (
        "the door only exists on a deployment carrying keel-cloud 044+045 and keel-web 024")
    assert "keels-ai" in MAKEFILE.split("\n")[6], "the target is not in .PHONY"


def test_the_make_target_says_whose_money_it_spends():
    head = MAKEFILE.split("keels-ai: venv", 1)[0]
    assert "COMPANY'S MONEY" in head.upper()
    assert "$2.44" in head and "1,250 credits" in head
