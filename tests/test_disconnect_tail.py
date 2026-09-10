"""Stackless: spec `011-keel-disconnect`. There is a door out, the referee uses the founder's own
one, and `make down` reads the outcome rather than hoping.

Design of record: keel-cloud `canon/designs/keel-disconnect-design.md` §8.4 (this repo's own
section) with §7's invariants. Everything here runs offline against a temporary directory shaped
like keel-connect-skill and a fake `subprocess.run`; the live half is S-001's tail, whose run of
record is named in `specs/011-keel-disconnect/tasks.md`.

Three of these read this repo's own source. That is on purpose and it is the same reason spec
012's suite gives: "the tail goes through the script, never through `python3 -m keel_runtime`" and
"the bound is two seconds" are properties of the *code*, and a property nobody can observe without
a live stack is a property that quietly stops holding.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from harness.connect import stop_runtime_via_skill
from harness.steps import Recorder
from stack import lifecycle
from stack import runtime as stack_runtime
from stack.config import REPO_ROOT, load_config
from stack.runtime import DisconnectScriptMissing

S001 = REPO_ROOT / "evals" / "test_s001_smoke.py"
S008 = REPO_ROOT / "evals" / "test_s008_bundled_runtime.py"


@pytest.fixture
def skill_tree(tmp_path):
    """keel-connect-skill after `make runtime` *and* after its spec `002-keel-disconnect`: two
    scripts beside a `keel_runtime/` package."""
    skill = tmp_path / "keel-connect-skill"
    (skill / "scripts").mkdir(parents=True)
    (skill / "scripts" / "keel_connect_check.py").write_text("# the way in\n")
    (skill / "scripts" / "keel_disconnect.py").write_text("# the way out\n")
    (skill / "keel_runtime").mkdir()
    (skill / "keel_runtime" / "__main__.py").write_text("# the runtime that travelled\n")
    (skill / "RUNTIME_VERSION").write_text("0.1.0+638c0dc\n")
    return skill


@pytest.fixture
def config(tmp_path, skill_tree):
    base = load_config(tmp_path / "absent.toml", validate=False)
    return replace(base, keel_connect_skill=skill_tree)


def _answering(monkeypatch, body: str, *, seen: dict | None = None):
    """A `subprocess.run` that answers one line of JSON, whatever it is asked."""

    class _Completed:
        returncode = 0
        stdout = body
        stderr = ""

    def _fake_run(cmd, **kwargs):
        if seen is not None:
            seen.setdefault("cmds", []).append(cmd)
            seen["env"] = kwargs.get("env")
        return _Completed()

    monkeypatch.setattr(stack_runtime.subprocess, "run", _fake_run)


# --------------------------------------------- the founder's own door, with no fallback under it

def test_the_script_only_path_answers_in_the_skills_own_vocabulary(config, skill_tree,
                                                                    monkeypatch):
    seen: dict = {}
    _answering(monkeypatch,
               '{"outcome": "disconnected", "pid": 41213, "waited_ms": 84, '
               '"signal": "SIGTERM", "environment": "localhost:18080"}\n', seen=seen)

    body = stack_runtime.disconnect_via_skill_script(config)

    assert body["outcome"] == "disconnected"
    assert body["via"] == stack_runtime.VIA_SKILL_SCRIPT
    assert str(skill_tree / "scripts" / "keel_disconnect.py") in seen["cmds"][0]
    assert "--home" in seen["cmds"][0], (
        "one home, resolved once: the script's contract says it does not guess one")


def test_the_script_only_path_hands_the_script_a_scrubbed_environment(config, monkeypatch):
    """T-1 again, on the way out. An ambient `KEEL_RUNTIME_PATH` would make the script resolve a
    *checkout* and disconnect a runtime the referee never started."""
    monkeypatch.setenv("KEEL_RUNTIME_PATH", "/a/checkout")
    monkeypatch.setenv("KEEL_HOME", "/somebody/elses/.keel")
    seen: dict = {}
    _answering(monkeypatch, '{"outcome": "not_running", "environment": "localhost:18080"}\n',
               seen=seen)

    stack_runtime.disconnect_via_skill_script(config)

    assert "KEEL_RUNTIME_PATH" not in seen["env"]
    assert "KEEL_HOME" not in seen["env"]


def test_the_script_only_path_is_none_when_the_skill_has_no_way_out(config, skill_tree):
    (skill_tree / "scripts" / "keel_disconnect.py").unlink()
    assert stack_runtime.disconnect_via_skill_script(config) is None


def test_the_script_only_path_is_none_when_the_script_says_something_unparseable(config,
                                                                                 monkeypatch):
    _answering(monkeypatch, "Traceback (most recent call last):\n")
    assert stack_runtime.disconnect_via_skill_script(config) is None


def test_make_downs_door_still_falls_through_and_the_tails_does_not(config, skill_tree,
                                                                     monkeypatch):
    """The one-sentence difference between the two, asserted rather than described: with no
    `keel_disconnect.py` at all, `disconnect` reaches the bundled runtime's own command and
    `stop_runtime_via_skill` refuses."""
    (skill_tree / "scripts" / "keel_disconnect.py").unlink()
    seen: dict = {}
    _answering(monkeypatch, '{"outcome": "not_running", "environment": "localhost:18080"}\n',
               seen=seen)

    body = stack_runtime.disconnect(config)
    assert body["via"] == "bundled keel_runtime disconnect"
    assert seen["cmds"][0][1:4] == ["-m", "keel_runtime", "disconnect"]


def test_the_tail_refuses_when_the_skill_has_no_way_out(config, skill_tree, tmp_path):
    (skill_tree / "scripts" / "keel_disconnect.py").unlink()
    recorder = Recorder(tmp_path / "run")
    with pytest.raises(DisconnectScriptMissing) as excinfo:
        stop_runtime_via_skill(config, recorder)
    assert "keel_disconnect.py" in str(excinfo.value)
    assert "no fallback" in str(excinfo.value)


def test_the_tail_returns_the_outcome_and_confirms_it_against_status(config, tmp_path,
                                                                     monkeypatch):
    _answering(monkeypatch,
               '{"outcome": "disconnected", "pid": 41213, "environment": "localhost:18080"}\n')
    monkeypatch.setattr(stack_runtime, "status", lambda _config: {"running": False})
    recorder = Recorder(tmp_path / "run")

    body = stop_runtime_via_skill(config, recorder)

    assert body["outcome"] == "disconnected"
    assert body["via"] == stack_runtime.VIA_SKILL_SCRIPT
    entry = json.loads(recorder.transcript_path.read_text().splitlines()[0])
    assert entry["ok"] is True
    assert entry["response"]["disconnect"]["outcome"] == "disconnected"


def test_the_tail_fails_on_the_one_outcome_a_caller_must_treat_as_a_failure(config, tmp_path,
                                                                            monkeypatch):
    """The disconnect contract's guarantee 3 (D6): on `did_not_stop` the process is still polling
    and the heartbeat was deliberately left in place."""
    _answering(monkeypatch,
               '{"outcome": "did_not_stop", "pid": 41213, "waited_ms": 15003, '
               '"message": "stuck", "environment": "localhost:18080"}\n')
    monkeypatch.setattr(stack_runtime, "status", lambda _config: {"running": True})
    recorder = Recorder(tmp_path / "run")

    with pytest.raises(RuntimeError, match="did not stop"):
        stop_runtime_via_skill(config, recorder)
    entry = json.loads(recorder.transcript_path.read_text().splitlines()[0])
    assert entry["ok"] is False


def test_the_tail_fails_when_the_outcome_and_the_heartbeat_disagree(config, tmp_path, monkeypatch):
    _answering(monkeypatch,
               '{"outcome": "disconnected", "pid": 41213, "environment": "localhost:18080"}\n')
    monkeypatch.setattr(stack_runtime, "status", lambda _config: {"running": True})
    recorder = Recorder(tmp_path / "run")

    with pytest.raises(RuntimeError, match="still reads running"):
        stop_runtime_via_skill(config, recorder)


# ------------------------------------------------------------------------- the file, and the home

def test_the_heartbeat_is_named_where_keel_runtime_names_it(config):
    assert stack_runtime.HEARTBEAT_FILENAME == "runtime.heartbeat.json"
    assert stack_runtime.heartbeat_path(config) == \
        stack_runtime.home_dir(config) / "runtime.heartbeat.json"
    playground = replace(config, profile="playground", cloud_port=18081)
    assert stack_runtime.heartbeat_path(playground).parent.name == "keel-home-playground", (
        "two profiles never share a home, and so never share a heartbeat either")


# ------------------------------------------------------- `make down` puts its outcome in the log

def test_make_down_prints_the_disconnect_outcome_and_which_door_answered(config, monkeypatch,
                                                                         capsys):
    """§8.4: "`make down` calls the command instead of hand-rolling it" -- and the outcome goes
    into the teardown line, so a stack log is evidence that the runtime was asked and answered."""
    monkeypatch.setattr(lifecycle.runtime, "disconnect",
                        lambda _config: {"outcome": "not_running",
                                          "via": stack_runtime.VIA_SKILL_SCRIPT})
    monkeypatch.setattr(lifecycle, "teardown_all_processes", lambda _profile: None)
    monkeypatch.setattr(lifecycle.postgres, "down", lambda _config: None)
    # No `lifecycle.auth.clear_stored` to stub any more: `runs/.stack/founder.json` went with
    # the password (keel-cloud google-sign-in-design.md §10.4), so teardown has no credential to
    # clear and `stack/lifecycle.py` no longer imports `stack.auth` at all.
    monkeypatch.setattr(lifecycle.oidc, "clear_key", lambda _config: None)
    monkeypatch.setattr(lifecycle.time, "sleep", lambda _s: None)

    lifecycle.teardown(config)

    log = capsys.readouterr().out
    assert "keel-runtime: not_running" in log
    assert stack_runtime.VIA_SKILL_SCRIPT in log, (
        "the log must name which of the two doors answered, or a green teardown says nothing "
        "about whether the founder's own script was ever exercised")
    assert "WARNING" not in log


def test_make_down_warns_loudly_on_did_not_stop_and_still_tears_the_rest_down(config, monkeypatch,
                                                                              capsys):
    stopped = {}
    monkeypatch.setattr(lifecycle.runtime, "disconnect",
                        lambda _config: {"outcome": "did_not_stop", "pid": 41213,
                                          "via": stack_runtime.VIA_SKILL_SCRIPT})
    monkeypatch.setattr(lifecycle, "teardown_all_processes",
                        lambda _profile: stopped.setdefault("processes", True))
    monkeypatch.setattr(lifecycle.postgres, "down",
                        lambda _config: stopped.setdefault("postgres", True))
    # No `lifecycle.auth.clear_stored` to stub any more: `runs/.stack/founder.json` went with
    # the password (keel-cloud google-sign-in-design.md §10.4), so teardown has no credential to
    # clear and `stack/lifecycle.py` no longer imports `stack.auth` at all.
    monkeypatch.setattr(lifecycle.oidc, "clear_key", lambda _config: None)
    monkeypatch.setattr(lifecycle.time, "sleep", lambda _s: None)

    lifecycle.teardown(config)

    log = capsys.readouterr().out
    assert "WARNING: the runtime did not stop" in log
    assert stopped == {"processes": True, "postgres": True}, (
        "a teardown that raised would leave Postgres and two JVMs behind (FR-003)")


# ------------------------------------------------------------------- what S-001's tail must say

def test_the_tail_never_shells_the_runtimes_own_command():
    """§8.4, in as many words: "shelling `scripts/keel_disconnect.py`, never
    `python3 -m keel_runtime disconnect`"."""
    body = S001.read_text()
    assert "stop_runtime_via_skill" in body
    # The *call*, not the words: the tail's own comment quotes the design's sentence, and a grep
    # that could not tell a citation from an invocation would forbid writing down the reason
    # (spec 012 settled this same point for `--runtime-path`).
    assert "stack_runtime.disconnect(" not in body, (
        "the tail must not reach the module-level door that falls back to the runtime's own "
        "command")
    assert '"keel_runtime"' not in body, (
        "nothing in the smoke shells `-m keel_runtime` -- the skill is one of the four "
        "applications under referee, on the way out as well as the way in")
    assert "stop_runtime(" not in body, (
        "`stop_runtime` is `make down`'s door and would accept the fallback; the tail referees "
        "the skill's own script")


def test_the_tail_asserts_all_four_things_the_design_lists():
    body = S001.read_text()
    assert 'stopped["outcome"] == "disconnected"' in body, "1. the script's outcome"
    assert "heartbeat.exists()" in body, "2. the heartbeat is gone"
    assert "No agent connected* again" in body, "3. the landing line, proven both ways"
    assert "gone_at + 2.0" in body, "4. and the bound that is the entire assertion"


def test_the_two_second_bound_is_measured_from_the_disconnect_and_not_from_a_page_load():
    """The tightness is the assertion (§8.4): thirty seconds "would pass with no goodbye
    implemented at all". A bound whose clock started after a browser navigation would be just as
    empty, so the ordering is asserted here rather than left to a reviewer's eye."""
    body = S001.read_text()
    gone_at = body.index("gone_at = time.monotonic()")
    bound = body.index("deadline = gone_at + 2.0")
    landing = body.index("No agent connected* again")
    assert gone_at < bound < landing, (
        "the /v2/me bound must be measured, and spent, before the landing is reloaded")


def test_the_tail_is_idempotent_by_the_contracts_own_rule():
    body = S001.read_text()
    assert 'stopped_again["outcome"] == "not_running"' in body, (
        "D10: a second disconnect against the same home is `not_running`, not an error")


# --------------------------------------------------- and what S-008 says now the goodbye is real

def test_s008_asserts_the_goodbye_rather_than_recording_which_path_it_saw():
    """`runs/DRIFT.md` #47 is resolved: keel-connect-skill re-ran `make runtime` and the bundled
    copy now carries `CloudClient.end_agent_session`, so the probe became an assertion."""
    body = S008.read_text()
    assert 'assert path == "goodbye"' in body
    assert 'if path == "staleness":' not in body, (
        "the staleness branch was the debt #47 recorded; asserting the goodbye is what closes it")


def test_drift_47_is_marked_resolved_and_names_the_run_that_did_it():
    drift = (REPO_ROOT / "runs" / "DRIFT.md").read_text()
    heading = next(line for line in drift.splitlines() if line.startswith("## 47."))
    assert "RESOLVED" in heading, heading
    section = drift.split("## 47.", 1)[1].split("\n## ", 1)[0]
    assert "s001-smoke" in section or "s008-bundled-runtime" in section, (
        "a resolution with no run behind it is a claim, not evidence")
