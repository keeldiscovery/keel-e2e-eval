"""Stackless: spec 012-bundled-runtime. The runtime the referee runs is the one that travelled
inside the skill, the home it runs against still names its Keel, and the way it stops is a
`disconnect` whose outcome is read rather than a signal sent and hoped for.

Every test here runs offline against a temporary directory shaped like keel-connect-skill. The
two that read this repo's own source do so on purpose: "no `--runtime-path` is passed" and "no
`kill` survives" are properties of the *code*, not of a run, and a property nobody can observe
without a live stack is a property that quietly stops holding.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from stack import runtime as stack_runtime
from stack.config import REPO_ROOT, load_config
from stack.runtime import BundledRuntimeMissing


@pytest.fixture
def skill_tree(tmp_path):
    """A directory shaped like keel-connect-skill after `make runtime`: scripts beside a
    `keel_runtime/` package and a `RUNTIME_VERSION` naming the commit it was copied from."""
    skill = tmp_path / "keel-connect-skill"
    (skill / "scripts").mkdir(parents=True)
    (skill / "scripts" / "keel_connect_check.py").write_text("# the skill's own script\n")
    (skill / "keel_runtime").mkdir()
    (skill / "keel_runtime" / "__main__.py").write_text("# the runtime that travelled\n")
    (skill / "RUNTIME_VERSION").write_text("0.1.0+abc1234\n")
    return skill


@pytest.fixture
def config(tmp_path, skill_tree):
    """A `StackConfig` pointing at the fake skill, with everything else this repo's own."""
    base = load_config(tmp_path / "absent.toml", validate=False)
    return replace(base, keel_connect_skill=skill_tree)


# ------------------------------------------------------------ FR-001/FR-002: which runtime runs

def test_the_bundled_runtime_is_the_package_beside_the_skills_scripts(config, skill_tree):
    assert stack_runtime.bundled_runtime_dir(config) == skill_tree / "keel_runtime"
    assert stack_runtime.bundled_runtime_present(config)
    assert stack_runtime.require_bundled_runtime(config) == skill_tree / "keel_runtime"


def test_a_directory_without_a_main_is_not_a_runtime(config, skill_tree):
    """The same test the skill's own `_runtime_location.py` makes: a `keel_runtime/` with no
    `__main__.py` cannot be run as `-m keel_runtime`, so it is not a runtime."""
    (skill_tree / "keel_runtime" / "__main__.py").unlink()
    assert not stack_runtime.bundled_runtime_present(config)


def test_the_gate_names_the_one_command_that_builds_it_and_does_not_run_it(config, skill_tree):
    import shutil

    shutil.rmtree(skill_tree / "keel_runtime")
    with pytest.raises(BundledRuntimeMissing) as excinfo:
        stack_runtime.require_bundled_runtime(config)
    message = str(excinfo.value)
    assert f"make -C {skill_tree} runtime" in message, message
    assert str(skill_tree / "keel_runtime") in message
    assert "writes to a sibling repository" in message, (
        "the gate must say why it names the command rather than running it -- this repo owns no "
        "product code and never writes to a sibling")


def test_the_runtime_version_stamp_is_read_and_its_absence_is_not_fatal(config, skill_tree):
    assert stack_runtime.bundled_runtime_version(config) == "0.1.0+abc1234"
    (skill_tree / "RUNTIME_VERSION").unlink()
    assert stack_runtime.bundled_runtime_version(config) is None


def test_the_checkout_is_no_longer_what_runs_but_is_still_what_is_read(config):
    """`stack.toml`'s `keel_runtime` stays: `harness/canary.py` reads keel-runtime's own cap
    defaults out of it and `instructions/prompts.py` imports its `build_prompt`. What changed is
    that nothing *runs* it any more."""
    source = (REPO_ROOT / "stack" / "runtime.py").read_text()
    assert "config.keel_runtime" not in source, (
        "spec 012: the runtime this stack runs is the bundled one, never the checkout")
    assert "config.keel_connect_skill" in source


# ------------------------------------------------------------------- FR-004: the ambient variables

def test_the_three_variables_that_name_a_runtime_a_home_or_a_keel_are_scrubbed():
    env = stack_runtime.scrubbed_env(base_env={
        "KEEL_RUNTIME_PATH": "/somewhere/keel-runtime",
        "KEEL_HOME": "/Users/ada/.keel-playground",
        "KEEL_BASE_URL": "http://localhost:18081",
        "PATH": "/usr/bin",
    })
    assert "KEEL_RUNTIME_PATH" not in env
    assert "KEEL_HOME" not in env
    assert "KEEL_BASE_URL" not in env
    assert env["PATH"] == "/usr/bin"


def test_the_job_knobs_are_deliberately_not_scrubbed():
    """`runs/DRIFT.md` #46 settled this: the referee reads the caps the runtime is actually under
    and names where each came from, rather than clearing them to make a bundle look tidier."""
    env = stack_runtime.scrubbed_env(base_env={"KEEL_JOB_MAX_TURNS": "8",
                                                "KEEL_JOB_BUDGET_USD": "1.00"})
    assert env["KEEL_JOB_MAX_TURNS"] == "8"
    assert env["KEEL_JOB_BUDGET_USD"] == "1.00"


def test_extra_values_win_over_the_inherited_environment():
    env = stack_runtime.scrubbed_env({"KEEL_SCRIPT": "/runs/x/script.json"},
                                      base_env={"KEEL_SCRIPT": "/stale.json"})
    assert env["KEEL_SCRIPT"] == "/runs/x/script.json"


def test_the_runtime_environment_puts_the_skill_root_first_on_pythonpath(config, skill_tree,
                                                                          monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "/somebody/elses/path")
    monkeypatch.setenv("KEEL_RUNTIME_PATH", "/a/checkout")
    env = stack_runtime.runtime_env(config)
    assert env["PYTHONPATH"].split(":")[0] == str(skill_tree)
    assert "/somebody/elses/path" in env["PYTHONPATH"], (
        "prepended, not replaced -- a caller who set PYTHONPATH for their own reasons keeps it")
    assert env["PYTHONSAFEPATH"] == "1"
    assert "KEEL_RUNTIME_PATH" not in env


def test_the_runtime_environment_sets_pythonpath_when_there_was_none(config, skill_tree,
                                                                      monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    assert stack_runtime.runtime_env(config)["PYTHONPATH"] == str(skill_tree)


# --------------------------------------------------------- FR-004: the home that names its Keel

def test_the_home_is_still_this_repos_own_one_per_profile(config):
    assert stack_runtime.home_dir(config) == REPO_ROOT / "runs" / ".stack" / "keel-home"
    playground = replace(config, profile="playground", cloud_port=18081)
    assert stack_runtime.home_dir(playground) == (
        REPO_ROOT / "runs" / ".stack" / "keel-home-playground")


def test_each_profiles_base_url_is_its_own(config):
    assert config.cloud_base_url == "http://localhost:18080"
    assert replace(config, profile="playground", cloud_port=18081).cloud_base_url == \
        "http://localhost:18081"


def test_reset_wipes_the_home_and_leaves_it_naming_this_profiles_keel(config, tmp_path,
                                                                      monkeypatch):
    home = tmp_path / "keel-home"
    monkeypatch.setattr(stack_runtime, "home_dir", lambda _config: home)
    home.mkdir()
    (home / "credentials.json").write_text("a credential from a previous run")

    stack_runtime.reset(config)

    assert not (home / "credentials.json").exists(), (
        "spec 005 edge case: no credential or heartbeat from a prior run survives a `make up`")
    assert json.loads((home / "config.json").read_text()) == {
        "base_url": "http://localhost:18080"}


def test_the_home_names_its_keel_because_status_has_no_base_url_flag(config, tmp_path,
                                                                     monkeypatch):
    """keel-runtime's `status` parser takes `--home` and nothing else, so the address it reports
    can only come from the environment (scrubbed), the built-in cloud default (empty) or the
    home's own `config.json`. That is why this file is written -- without it a run's
    `environment` reads null and FR-004 is unassertable."""
    home = tmp_path / "keel-home"
    monkeypatch.setattr(stack_runtime, "home_dir", lambda _config: home)
    stack_runtime.ensure_home_names_keel(config)
    assert json.loads((home / "config.json").read_text())["base_url"] == \
        "http://localhost:18080"


def test_ensuring_the_home_names_its_keel_never_removes_anything(config, tmp_path, monkeypatch):
    home = tmp_path / "keel-home"
    monkeypatch.setattr(stack_runtime, "home_dir", lambda _config: home)
    home.mkdir()
    (home / "credentials.json").write_text("mid-session, and still needed")
    (home / "config.json").write_text('{"base_url": "http://localhost:18080", "extra": 1}')

    stack_runtime.ensure_home_names_keel(config)

    assert (home / "credentials.json").read_text() == "mid-session, and still needed"
    assert json.loads((home / "config.json").read_text())["extra"] == 1, (
        "an existing config.json is left alone -- this is the guarantee, not the wipe")


# ------------------------------------------------------------------ FR-003: kill became disconnect

def test_nothing_in_this_stack_signals_a_runtime_any_more():
    source = (REPO_ROOT / "stack" / "runtime.py").read_text()
    assert "def kill(" not in source, "spec 012: `kill` became `disconnect` (design §11)"
    assert "SIGTERM" not in source and "os.kill" not in source, (
        "the runtime is asked to go and the answer is read; nothing here sends it a signal")
    assert "def disconnect(" in source


def test_both_vocabularies_are_accepted_because_two_contracts_name_these_outcomes():
    """keel-runtime says `stopped`/`timeout`; keel-connect-skill's script renames them
    `disconnected`/`did_not_stop` for a founder's ears. This stack calls whichever of the two
    exists, so it must know both names."""
    assert set(stack_runtime.STOPPED_OUTCOMES) == {
        "stopped", "disconnected", "not_running", "stale_pid_cleared"}
    assert set(stack_runtime.DID_NOT_STOP_OUTCOMES) == {"timeout", "did_not_stop"}


def test_disconnect_prefers_the_skills_own_script_when_it_exists(config, skill_tree, monkeypatch):
    (skill_tree / "scripts" / "keel_disconnect.py").write_text("# the founder's way out\n")
    seen = {}

    class _Completed:
        returncode = 0
        stdout = '{"outcome": "stopped", "pid": 41213, "environment": "localhost:18080"}\n'
        stderr = ""

    def _fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return _Completed()

    monkeypatch.setattr(stack_runtime.subprocess, "run", _fake_run)
    body = stack_runtime.disconnect(config)

    assert str(skill_tree / "scripts" / "keel_disconnect.py") in seen["cmd"]
    assert "--home" in seen["cmd"]
    assert body["outcome"] == "stopped"
    assert body["via"] == "keel-connect-skill/scripts/keel_disconnect.py"


def test_disconnect_falls_back_to_the_bundled_runtimes_own_command(config, skill_tree,
                                                                   monkeypatch):
    """keel-connect-skill's spec `002-keel-disconnect` may not have landed. The command that
    script shells is still there, one layer lower, answering the same four outcomes."""
    assert not (skill_tree / "scripts" / "keel_disconnect.py").exists()
    seen = {}

    class _Completed:
        returncode = 0
        stdout = '{"outcome": "not_running", "environment": "localhost:18080"}\n'
        stderr = ""

    def _fake_run(cmd, **kwargs):
        seen["cmd"] = cmd
        return _Completed()

    monkeypatch.setattr(stack_runtime.subprocess, "run", _fake_run)
    body = stack_runtime.disconnect(config)

    assert seen["cmd"][1:4] == ["-m", "keel_runtime", "disconnect"]
    assert body["outcome"] == "not_running"
    assert body["via"] == "bundled keel_runtime disconnect"


def test_a_teardown_is_never_blocked_by_a_sibling_that_cannot_answer(config, skill_tree):
    """Idempotence, exactly as `kill` had it: `make down` must still stop Postgres and two JVMs
    when the skill checkout is gone."""
    import shutil

    shutil.rmtree(skill_tree / "keel_runtime")
    body = stack_runtime.disconnect(config)
    assert body["outcome"] == "unavailable"
    assert str(stack_runtime.home_dir(config)) in body["message"]


def test_teardown_disconnects_instead_of_killing():
    source = (REPO_ROOT / "stack" / "lifecycle.py").read_text()
    assert "runtime.disconnect(config)" in source
    assert "runtime.kill(" not in source
    assert "require_bundled_runtime" in source, (
        "FR-002: `make up` refuses to boot without the runtime a founder would run")


# ------------------------------------------- FR-005: what the harness and the scenarios now say

def test_the_harness_no_longer_hands_the_skill_a_checkout():
    source = (REPO_ROOT / "harness" / "connect.py").read_text()
    # The *argv element*, not the word: the module's docstring explains at length why the flag is
    # gone, and a grep that could not tell an explanation from an invocation would be a test that
    # forbids writing down the reason.
    assert '"--runtime-path"' not in source, (
        "T-1: the skill must resolve the runtime that travelled inside it, not one we point at")
    assert "scrubbed_env" in source, (
        "dropping the flag is not enough -- an inherited KEEL_RUNTIME_PATH would put the checkout "
        "back and the run would referee the wrong runtime")


def test_the_seventh_outcome_has_somewhere_to_land():
    from harness import connect as harness_connect

    assert issubclass(harness_connect.PythonTooOld, RuntimeError)
    source = (REPO_ROOT / "harness" / "connect.py").read_text()
    assert 'outcome == "python_too_old"' in source


def test_s001_asserts_which_keel_it_reached():
    source = (REPO_ROOT / "evals" / "test_s001_smoke.py").read_text()
    assert 'expected_environment = f"localhost:{stack.cloud_port}"' in source
    assert 'result.get("environment") == expected_environment' in source


def test_the_run_bundle_names_the_runtime_that_actually_ran():
    """The bundled package is gitignored in keel-connect-skill, so `git rev-parse` cannot name
    it; `RUNTIME_VERSION` is the record, and a run that could not name its runtime would be a run
    nobody can reproduce."""
    source = (REPO_ROOT / "harness" / "evidence.py").read_text()
    assert "bundled, the one that runs" in source
    assert "bundled_runtime_version" in source


def test_s008_exists_and_is_not_live():
    module = REPO_ROOT / "evals" / "test_s008_bundled_runtime.py"
    body = module.read_text()
    assert "pytestmark = pytest.mark.live" not in body, (
        "the two named LLM exceptions do not change in number or in name (AGENTS.md)")
    assert "keel-skill-design.md" in body, "a scenario cites the design it proves"
    assert "runs/DRIFT.md` #47" in body, "the goodbye is recorded as owed, not asserted away"
