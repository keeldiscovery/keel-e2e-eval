"""Spec 066: the back-test through the host door, stackless (FR-7).

The door switch (`DOOR=keel` unchanged to the byte, `DOOR=host` with a fake runtime that writes a user code and a
heartbeat into `keel_home`), the sign-in leg's assertions on a fixture `/v2/me`, the teardown (SIGTERM, then SIGKILL),
the jobs-on-the-host and CLI-usage readers, the transcript's host-door lines, and the runner's limit parsing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from harness import agent_host
from harness.steps import Recorder

REPO = Path(__file__).resolve().parent.parent
WEB = "http://localhost:5173"
CODE = "ABCD-EFGH"

#: The fake runtime: writes `awaiting_approval`, prints the code and the device page, writes `connected` once the test
#: drops `approved` into the home; on SIGTERM removes its heartbeat and exits (as keel-runtime's handler does) -- or,
#: with `--stubborn`, ignores SIGTERM so only SIGKILL ends it.
FAKE_RUNTIME = textwrap.dedent('''
    import json, os, signal, sys, time
    from pathlib import Path
    args = sys.argv[1:]
    home = Path(args[args.index("--home") + 1])
    home.mkdir(parents=True, exist_ok=True)
    beat = home / "runtime.heartbeat.json"
    def write(state):
        beat.write_text(json.dumps({"pid": os.getpid(), "state": state, "base_url": "http://localhost:18080",
                                    "agent_session_id": None if state == "awaiting_approval" else "s-1"}))
    def bye(*_):
        beat.unlink(missing_ok=True)
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal.SIG_IGN if "--stubborn" in args else bye)
    (home / "credentials.json").write_text("{}")
    write("awaiting_approval")
    print("KEEL_ENVIRONMENT=local base_url=http://localhost:18080", flush=True)
    print("KEEL_EXECUTOR=claude source=flag binary=/usr/bin/claude version=2.1.300", flush=True)
    print("KEEL_USER_CODE=ABCD-EFGH", flush=True)
    print("KEEL_VERIFICATION_URI=http://localhost:5173/connect?user_code=ABCD-EFGH", flush=True)
    while True:
        if (home / "approved").exists() and json.loads(beat.read_text())["state"] != "connected":
            write("connected")
        time.sleep(0.1)
''')


def _fake(tmp_path: Path, *, stubborn: bool = False) -> bt.HostRuntime:
    script = tmp_path / "fake_runtime.py"
    script.write_text(FAKE_RUNTIME, encoding="utf-8")
    home = tmp_path / "run" / bt.KEEL_HOME_DIR
    argv = [sys.executable, str(script), "--home", str(home)] + (["--stubborn"] if stubborn else [])
    return bt.HostRuntime(keel_home=home, argv=argv, cwd=tmp_path, env=dict(os.environ))


# ------------------------------------------------------------------------------------------ FR-1: the door switch

def test_the_door_is_keel_unless_host_is_named_and_anything_else_is_refused():
    assert bt.door({}) == "keel" and bt.door({bt.DOOR_VAR: " Host "}) == "host"
    with pytest.raises(bt.UnknownDoor, match="DOOR='hst' is not a door"):
        bt.door({bt.DOOR_VAR: "hst"})
    assert bt.host({}) == "claude"
    with pytest.raises(bt.UnknownDoor, match="HOST='copilot'"):
        bt.host({bt.HOST_VAR: "copilot"})
    assert bt.door_refusal({}) is None and bt.door_refusal({bt.DOOR_VAR: "keel", bt.HOST_VAR: "copilot"}) is None
    assert "HOST='codex'" in bt.door_refusal({bt.DOOR_VAR: "host", bt.HOST_VAR: "codex"})
    said = bt.door_refusal({bt.DOOR_VAR: "host", bt.MODEL_VAR: "opus"})
    assert said and "MODEL='opus'" in said and "spec 009" in said
    assert bt.door_refusal({bt.DOOR_VAR: "host"}) is None


def _make(*args: str, key: bool) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in (bt.KEY_VAR, "DOOR", "HOST", "MODEL", "ENTRY")}
    if key:
        env[bt.KEY_VAR] = "not-a-key"
    return subprocess.run(["make", "--no-print-directory", "-C", str(REPO), *args], capture_output=True,
                          encoding="utf-8", env=env, timeout=60)


SPEC_062_LINE = ("KEEL_EVAL_PROFILE=eval KEEL_BACKTEST_ENTRY=08-fresco .venv/bin/python -m pytest evals/run_backtest.py "
                 "-q -rs -l")


@pytest.mark.skipif(shutil.which("make") is None, reason="no make on PATH")
def test_door_keel_is_spec_062_byte_for_byte_and_door_host_asks_for_no_key():
    for args in (("-n", "backtest", "ENTRY=08-fresco"), ("-n", "backtest", "ENTRY=08-fresco", "DOOR=keel")):
        out = _make(*args, key=True)
        assert out.returncode == 0 and out.stdout.strip().splitlines()[-1] == SPEC_062_LINE, out.stdout
    refused = _make("backtest", "ENTRY=08-fresco", key=False)
    assert refused.returncode == 2 and bt.refusal({}) in refused.stdout, refused.stdout
    host = _make("-n", "backtest", "ENTRY=08-fresco", "DOOR=host", key=False)
    assert host.returncode == 0, host.stdout + host.stderr
    assert host.stdout.strip().splitlines()[-1] == (
        "KEEL_EVAL_PROFILE=eval KEEL_BACKTEST_ENTRY=08-fresco KEEL_BACKTEST_DOOR=host KEEL_BACKTEST_HOST=claude "
        ".venv/bin/python -m pytest evals/run_backtest.py -q -rs -l")
    wrong = _make("backtest", "ENTRY=08-fresco", "DOOR=side", key=True)
    assert wrong.returncode == 2 and "DOOR=side is not a door" in wrong.stdout


def test_the_runner_reads_the_door_and_the_keel_door_still_refuses_on_a_missing_key():
    source = (REPO / "evals" / "run_backtest.py").read_text(encoding="utf-8")
    assert "backtest.door_refusal()" in source and "backtest.refusal() or backtest.entry_refusal()" in source
    # spec 071 FR-4: the KEEL door's call is unchanged but for the study's scope (ALL when unsaid) -- and, since spec
    # 106 FR-2, the people a study sends (`PEOPLE=`, every person when unsaid), re-pinned with why
    assert ("backtest=backtest.Backtest(run_dir=run_dir, stack=stack, scope=backtest.scope(),\n"
            "                                                       people=backtest.people()))") in source
    assert "bt.stop_runtime()" in source


# ------------------------------------------------------------------------------- FR-2: the runtime and its login

def test_the_runtime_command_is_the_spec_s_and_keeps_its_credential_in_the_run(tmp_path):
    argv = bt.runtime_argv("http://localhost:18080", tmp_path / "keel_home", python="py")
    assert argv == ["py", "-m", "keel_runtime", "connect", "--base-url", "http://localhost:18080", "--executor",
                    "claude", "--host", "claude", "--home", str(tmp_path / "keel_home"), "--no-browser",
                    "--credential-backend", "file"]


def test_the_runtime_env_is_the_founder_s_login_and_nothing_of_this_session():
    shell = {"PATH": "/bin", "HOME": "/h", "CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "x", "CLAUDE_EFFORT": "max",
             "CLAUDE_CODE_OAUTH_TOKEN": "t", "CLAUDE_CONFIG_DIR": "/h/.claude-other", "ANTHROPIC_API_KEY": "k",
             bt.KEY_VAR: "k", "KEEL_RUNTIME_PATH": "/elsewhere", "PYTHONPATH": "."}
    env = bt.runtime_env(shell, pythonpath="/skill")
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "t" and env["CLAUDE_CONFIG_DIR"] == "/h/.claude-other"
    assert env["PYTHONPATH"] == "/skill" and env["PATH"] == "/bin"
    for gone in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_EFFORT", "ANTHROPIC_API_KEY", bt.KEY_VAR,
                 "KEEL_RUNTIME_PATH"):
        assert gone not in env, gone
    assert "CLAUDE_CONFIG_DIR" not in bt.runtime_env({"PATH": "/bin"}), "unset stays unset: the founder's ~/.claude"
    assert "env" not in repr(bt.HostRuntime(keel_home=Path("/k"), argv=[], cwd=Path("/"), env={"SECRET": "s"}))


def test_the_skill_s_versions_are_read_from_the_checkout(tmp_path):
    (tmp_path / "VERSION").write_text("2.5.0\n")
    (tmp_path / "RUNTIME_VERSION").write_text("0.8.0+abc\n")
    got = bt.connect_skill_versions(tmp_path)
    assert got["VERSION"] == "2.5.0" and got["RUNTIME_VERSION"] == "0.8.0+abc"


def test_the_host_door_patience_is_the_host_s_or_longer():
    assert bt.Backtest(run_dir=Path("/r"), stack=None).patience == bt.PATIENCE
    host = bt.Backtest(run_dir=Path("/r"), stack=None, door="host")
    assert host.host == "claude"
    assert host.patience * 60 >= agent_host.host_type("claude").keels_ai_job_wait_s
    assert host.patience * 60 >= 660 and host.keel_home == Path("/r") / bt.KEEL_HOME_DIR


# -------------------------------------------------------------------------- FR-2 / FR-5: a fake runtime, stopped

def test_a_fake_runtime_prints_its_code_connects_and_is_stopped_with_its_evidence_kept(tmp_path):
    runtime = _fake(tmp_path)
    runtime.start()
    try:
        assert runtime.wait_for_code(10) == (CODE, f"{WEB}/connect?user_code={CODE}")
        assert runtime.heartbeat()["state"] == agent_host.STATE_AWAITING_APPROVAL
        (runtime.keel_home / "approved").write_text("")
        assert runtime.wait_for_connected(10)["state"] == bt.STATE_CONNECTED
    finally:
        record = runtime.stop(grace_s=5)
    assert record["signal"] == "SIGTERM" and record["exit code"] == 0 and record["alive after"] is False
    assert record["heartbeat at the end"]["state"] == bt.STATE_CONNECTED
    assert json.loads((runtime.keel_home / bt.HEARTBEAT_LAST).read_text())["state"] == bt.STATE_CONNECTED
    assert agent_host.read_heartbeat(runtime.keel_home) is None, "the runtime removed its own on SIGTERM"
    assert CODE in runtime.log() and runtime.log_path.name == bt.RUNTIME_LOG
    assert record["credential removed"] == ["credentials.json"]
    assert not (runtime.keel_home / "credentials.json").exists()
    assert runtime.stop() is record, "idempotent"


def test_a_runtime_that_ignores_sigterm_is_killed(tmp_path):
    runtime = _fake(tmp_path, stubborn=True)
    runtime.start()
    assert runtime.wait_for_code(10)[0] == CODE
    started = time.monotonic()
    record = runtime.stop(grace_s=1)
    assert record["signal"] == "SIGKILL" and record["alive after"] is False and time.monotonic() - started < 10


def test_stop_runtime_is_a_no_op_on_the_keel_door():
    assert bt.Backtest(run_dir=Path("/r"), stack=None).stop_runtime() is None


# ------------------------------------------------------------------------------ FR-3: the sign-in leg, on fixtures

ME_OWN = {"aiPath": "OWN", "email": bt.IDENTITY_EMAIL, "name": bt.IDENTITY_NAME, "creditsAvailable": None}


def test_the_door_s_me_reads_own_and_the_back_test_founder():
    assert bt.host_door_refusal(ME_OWN) is None
    assert "not 'OWN'" in bt.host_door_refusal({**ME_OWN, "aiPath": "KEEL", "creditsAvailable": 2000})
    assert "email" in bt.host_door_refusal({**ME_OWN, "email": "eval-founder@keel-e2e-eval.test"})
    assert "not 'OWN'" in bt.host_door_refusal(None)


def _journey(tmp_path: Path, me: dict):
    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    skill = tmp_path / "skill"
    skill.mkdir(exist_ok=True)
    (skill / "VERSION").write_text("2.5.0\n")
    (skill / "RUNTIME_VERSION").write_text("0.8.0+abc\n")
    stack = SimpleNamespace(keel_connect_skill=skill, cloud_base_url="http://localhost:18080", is_remote=False)
    return SimpleNamespace(recorder=Recorder(run_dir), page=None, web_base=WEB, stack=stack, get=lambda path: me,
                           run_dir=run_dir)


def _door(monkeypatch, tmp_path: Path, me: dict):
    """The leg with the browser's steps stood in for (S-012's two helpers and the shared door reader), the founder's
    CLI ready, and `start_runtime` handing in the fake runtime; approving at /connect drops `approved` in its home."""
    from evals import preludes
    import harness.browser as browser
    j = _journey(tmp_path, me)
    b = bt.Backtest(run_dir=j.run_dir, stack=j.stack, door="host")
    seen: list = []

    def start(stack):
        b.runtime = _fake(tmp_path)
        b.runtime.keel_home = b.keel_home
        b.runtime.argv[b.runtime.argv.index("--home") + 1] = str(b.keel_home)
        b.runtime.start()
        return b.runtime

    def approve(page, recorder, code, uri, *, label, timeout_s):
        seen.append(("approve", code, uri, label))
        (b.keel_home / "approved").write_text("")

    monkeypatch.setattr(b, "start_runtime", start)
    monkeypatch.setattr(b, "identity", lambda: SimpleNamespace(id="backtest", email=bt.IDENTITY_EMAIL))
    monkeypatch.setattr(bt, "host_readiness", lambda *a, **k: {"version": "2.1.300 (Claude Code)", "loggedIn": True,
                                                               "authMethod": "claude.ai", "refusal": None})
    monkeypatch.setattr(preludes, "sign_in_with_the_code", lambda auth, rec, founder, code: seen.append(("sign", code)))
    monkeypatch.setattr(preludes, "approve_at_connect", approve)
    monkeypatch.setattr(preludes, "own_ai_door", lambda *a, **k: seen.append(("door",)))
    monkeypatch.setattr(browser, "Auth", lambda *a: SimpleNamespace())
    monkeypatch.setattr(browser, "Landing", lambda *a: SimpleNamespace(visit=lambda: {}))
    return j, b, seen


def test_the_host_door_signs_in_with_the_runtime_s_code_and_holds_on_own(monkeypatch, tmp_path):
    j, b, seen = _door(monkeypatch, tmp_path, ME_OWN)
    try:
        founder = b.sign_in(j)
    finally:
        record = b.stop_runtime()
    assert founder.email == bt.IDENTITY_EMAIL and b.me_at_signup["aiPath"] == "OWN"
    assert seen[0] == ("sign", CODE) and seen[1][:3] == ("approve", CODE, f"{WEB}/connect?user_code={CODE}")
    assert ("door",) in seen
    assert record["heartbeat at the end"]["state"] == bt.STATE_CONNECTED and record["alive after"] is False
    steps = [json.loads(line) for line in j.recorder.transcript_path.read_text().splitlines()]
    assert steps and all(s.get("ok") is not False for s in steps), steps
    door = json.loads((j.run_dir / "versions.json").read_text())["backtest door"]
    assert door["host"] == "claude" and door["keel-connect-skill"]["VERSION"] == "2.5.0"
    assert set(door["cli"]) <= {"version", "loggedIn", "authMethod", "oauth token in the shell", "CLAUDE_CONFIG_DIR"}


def test_the_host_door_stops_when_the_account_is_on_keel_s_ai(monkeypatch, tmp_path):
    j, b, _ = _door(monkeypatch, tmp_path, {**ME_OWN, "aiPath": "KEEL"})
    try:
        with pytest.raises(AssertionError, match="not 'OWN'"):
            b.sign_in(j)
    finally:
        assert b.stop_runtime()["alive after"] is False


# ------------------------------------------------------------------------- FR-3: the jobs on the host, the cost

def test_every_landed_job_must_name_the_host_and_its_model():
    per_job = [{"screen": "CONTEXT", "status": "COMPLETED", "host": "claude", "model_used": "claude-haiku-4-5"},
               {"screen": "FRAME", "status": "FAILED", "host": "claude", "model_requested": "claude-sonnet-5-5"},
               {"screen": "THEMES", "status": "QUEUED", "host": None}]
    got = bt.host_door_jobs(per_job + [{"screen": "R", "status": "CANCELLED", "host": None}])
    assert got["landed"] == 3 and got["completed"] == 1 and got["bad"] == []
    assert got["open"] == [{"screen": "THEMES", "status": "QUEUED"}]
    assert got["no execution"] == [{"screen": "R", "status": "CANCELLED"}]
    got = bt.host_door_jobs(per_job + [{"screen": "BRIEF", "status": "COMPLETED", "host": "api", "model_used": "m"},
                                       {"screen": "X", "status": "COMPLETED", "host": "claude"},
                                       {"screen": "Y", "status": "FAILED", "host": "api"}])
    assert [b["screen"] for b in got["bad"]] == ["BRIEF", "X", "Y"]


def test_the_cost_reads_the_cli_s_own_usage_else_says_not_priced(tmp_path):
    assert bt.cli_usage(tmp_path)["words"] == bt.NOT_PRICED and bt.cli_usage(tmp_path)["usd"] is None
    for job, usd in (("j1", 0.0123), ("j2", 0.02)):
        (tmp_path / "jobs" / job).mkdir(parents=True)
        (tmp_path / "jobs" / job / "envelope.json").write_text(json.dumps({
            "type": "result", "is_error": False, "total_cost_usd": usd, "num_turns": 2,
            "modelUsage": {"claude-sonnet-5-5": {"inputTokens": 10, "outputTokens": 5, "cacheReadInputTokens": 100}}}))
    got = bt.cli_usage(tmp_path)
    assert got["usd"] == 0.0323 and got["priced"] == 2 and got["tokens"]["inputTokens"] == 20
    assert "not billed" in got["words"]
    assert bt.cli_usage(tmp_path, ["j1"])["usd"] == 0.0123


# ---------------------------------------------------------------------- FR-4 / FR-6: the plan's limit, the runner

@pytest.mark.parametrize("text, at", [
    ("Claude AI usage limit reached|1761235200", "2025-10-23T16:00:00Z"),
    ("You've hit your limit · resets 3pm (Europe/London)", "3pm (Europe/London)"),
    ("5-hour limit reached ∙ resets 11:30am", "11:30am"),
    ("API Error: 429 rate_limit_error: try again at 14:05 UTC.", "14:05 UTC"),
    ("rate limit exceeded", None),
])
def test_the_plan_s_limit_is_read_with_the_time_it_names(text, at):
    found = bt.limit_in(text)
    assert found is not None and found["at"] == at, found


def test_ordinary_failures_are_not_the_plan_s_limit():
    for text in ("INVALID_LLM_RESPONSE: item of ten words", "EXECUTOR_TIMEOUT: 1429 s", ""):
        assert bt.limit_in(text) is None, text


def test_the_runner_waits_until_the_named_time_or_thirty_minutes():
    now = 1_761_220_000.0                                        # 2025-10-23T11:46:40Z
    assert bt.resume_epoch("2025-10-23T16:00:00Z", now=now) == 1_761_235_200
    london = bt.resume_epoch("3pm (Europe/London)", now=now)     # 15:00 BST = 14:00Z, later that day
    assert london == 1_761_228_000
    assert bt.resume_epoch("11am (Europe/London)", now=now) == london - 4 * 3600 + 86_400, "past: tomorrow's"
    assert bt.resume_epoch(None, now=now) == now + bt.LIMIT_DEFAULT_WAIT_S
    assert bt.resume_epoch("whenever", now=now) == now + bt.LIMIT_DEFAULT_WAIT_S


def _record(**extra) -> dict:
    return {"run": "20261023T000000Z-backtest-08-fresco", "passed": False, "failed_step": "leg_interview",
            "entry": {"id": "08-fresco", "title": "Fresco"}, "brief": {"decision": {"label": "NOT_YET"}},
            "door": {"door": "host", "words": bt.HOST_DOOR_WORDS, "cli": {"version": "2.1.300", "authMethod": "claude.ai"},
                     "model": "per job", "keel-connect-skill": {"VERSION": "2.5.0", "RUNTIME_VERSION": "0.8.0"}},
            "cost": {"jobs": 3, "usd": 0.0, "micro_usd": 0, "door": "host",
                     "cli": {"usd": 0.42, "priced": 3, "envelopes": 3, "tokens": {}, "words": "the CLI's own"}},
            "runtime": {"signal": "SIGTERM", "exit code": 0, "alive after": False}, **extra}


def test_the_host_door_s_markdown_says_who_answered_and_the_limit_it_stopped_on():
    md = bt.markdown(_record(limit_stop="3pm (Europe/London)", **{"plan limit": {"said": "hit your limit"}}))
    assert HOST_WORDS in md and "the CLI reported $0.42" in md and "Keel's AI (local)" not in md
    assert bt.limit_stop_in(md) == "3pm (Europe/London)"
    unnamed = bt.markdown(_record(limit_stop=""))
    assert bt.limit_stop_in(unnamed) == ""
    clean = bt.markdown(_record())
    assert bt.limit_stop_in(clean) is None
    priced_nowhere = _record()
    priced_nowhere["cost"]["cli"] = {"usd": None, "words": bt.NOT_PRICED}
    assert f"Cost: {bt.NOT_PRICED}" in bt.markdown(priced_nowhere)
    keel = bt.markdown({k: v for k, v in _record().items() if k not in ("door", "runtime")})
    assert "Keel's AI (local)" in keel and HOST_WORDS not in keel and "the CLI reported" not in keel


HOST_WORDS = "the founder's own Claude Code (host door)"


def _run_dir(tmp_path: Path, record: dict) -> Path:
    run = tmp_path / record["run"]
    run.mkdir(parents=True)
    (run / "transcript.jsonl").write_text("\n".join(json.dumps({"seq": n, "ok": n != 2}) for n in range(1, 5)) + "\n")
    (run / bt.RECORD).write_text(json.dumps(record))
    (run / bt.MARKDOWN).write_text(bt.markdown(record))
    return run


def test_the_runner_s_line_and_its_wait_come_from_the_run(tmp_path, capsys):
    run = _run_dir(tmp_path, _record(limit_stop="2099-01-01T00:00:00Z"))
    log = tmp_path / "08-fresco.log"
    log.write_text(f"...\nrun bundle: {run}\n1 failed in 900s\n")
    assert bt.run_dir_in(log.read_text()) == run
    row = bt.summary(run, "08-fresco")
    assert (row["steps"], row["bad"], row["decision"], row["limit_stop"]) == (4, 1, "NOT_YET", "2099-01-01T00:00:00Z")
    assert bt.main(["summary", str(log), "08-fresco"]) == 0
    printed = capsys.readouterr().out.strip().splitlines()
    line = printed[0]
    assert line.split("\t")[:5] == ["08-fresco", str(run), "steps 4", "bad 1", "NOT_YET"]
    # spec 067: the register's re-run row, the previous score read from keel-cloud's register when it has the entry
    assert printed[1].startswith("re-run row: | 08-fresco | (judged: to fill) | ") and "| to be judged |" in printed[1]
    assert bt.main(["resume", str(log), "08-fresco"]) == 0 and int(capsys.readouterr().out) > 86_400
    clean = _run_dir(tmp_path / "b", _record())
    log.write_text(f"run bundle: {clean}\n")
    assert bt.main(["resume", str(log), "08-fresco"]) == 0 and capsys.readouterr().out == ""


def test_the_runner_script_waits_alone_logs_each_entry_and_prints_one_line(tmp_path):
    script = REPO / "scripts" / "backtest-host.sh"
    body = script.read_text(encoding="utf-8")
    assert 'pgrep -f -- "-m [p]ytest evals"' in body and "RERUNS=3" in body and "runs/backtest-host" in body
    assert body.index("--no-print-directory down") < body.index("--no-print-directory backtest DOOR=host")
    for leak in ("set -x", "printenv", "env |", "auth status", "TOKEN", "KEY"):
        assert leak not in body, leak
    run = _run_dir(tmp_path, _record())
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "make").write_text(f'#!/bin/sh\necho "$@" >> {tmp_path}/make.calls\n'
                                  f'case "$*" in *backtest*) echo "run bundle: {run}";; esac\n')
    (bin_dir / "pgrep").write_text("#!/bin/sh\nexit 1\n")
    for f in bin_dir.iterdir():
        f.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(script, repo / "scripts" / script.name)
    (repo / "evals").symlink_to(REPO / "evals")
    (repo / "harness").symlink_to(REPO / "harness")
    out = subprocess.run(["bash", str(repo / "scripts" / script.name), "08-fresco"], capture_output=True,
                         encoding="utf-8", timeout=60,
                         env={"PATH": f"{bin_dir}:{os.environ['PATH']}", "HOME": str(tmp_path), "PY": sys.executable})
    assert out.returncode == 0, out.stderr
    lines = out.stdout.strip().splitlines()
    assert lines[0].split("\t")[:5] == ["08-fresco", str(run), "steps 4", "bad 1", "NOT_YET"]
    assert len(lines) == 2 and lines[1].startswith("re-run row: | 08-fresco |"), lines   # spec 067: the register's row
    calls = (tmp_path / "make.calls").read_text().splitlines()
    assert "down" in calls[0] and "backtest DOOR=host ENTRY=08-fresco" in calls[1] and len(calls) == 2
    assert (repo / "runs" / "backtest-host" / "08-fresco.log").is_file()


def test_each_job_s_result_event_usage_is_recorded_and_summed_into_the_markdown(tmp_path):
    (tmp_path / "jobs" / "j1").mkdir(parents=True)
    (tmp_path / "jobs" / "j1" / "envelope.json").write_text(json.dumps({
        "type": "result", "total_cost_usd": 0.01, "num_turns": 1, "duration_ms": 900,
        "usage": {"input_tokens": 3, "output_tokens": 7, "cache_read_input_tokens": 100,
                  "cache_creation_input_tokens": 5, "service_tier": "standard"},
        "modelUsage": {"claude-sonnet-5-5": {"inputTokens": 3, "outputTokens": 7, "costUSD": 0.01}}}))
    cli = bt.cli_usage(tmp_path)
    assert cli["usage"] == {"input_tokens": 3, "output_tokens": 7, "cache_read_input_tokens": 100,
                            "cache_creation_input_tokens": 5}
    assert cli["per_job"][0]["costUSD by model"] == {"claude-sonnet-5-5": 0.01}
    cli["per_job"][0]["screen"] = "PROBLEM_FRAME"
    record = _record()
    record["cost"]["cli"] = cli
    md = bt.markdown(record)
    assert "The result events' usage, summed" in md and "PROBLEM_FRAME `j1`: $0.01, in 3 / out 7" in md


def test_a_green_run_s_directory_is_found_without_the_bundle_line(tmp_path):
    """pytest -q prints no captured stdout on a pass, so the log has no `run bundle:`; the newest run written while the
    log was being written is the run. An older run of the same entry, or a run that never made its directory, is not."""
    import os, time
    runs = tmp_path / "runs"
    old = _run_dir(runs, _record()); old = old.rename(runs / "20260101T000000Z-backtest-08-fresco")
    past = time.time() - 3600
    os.utime(old / bt.RECORD, (past, past))
    log = tmp_path / "08-fresco.log"
    log.write_text(".\n1 passed in 700s\n")
    assert bt.run_dir_in(log.read_text()) is None
    assert bt.latest_run_dir("08-fresco", log, runs=runs) is None            # the old run is not this log's
    new = _run_dir(runs, _record()); new = new.rename(runs / "20260102T000000Z-backtest-08-fresco")
    log.write_text(".\n1 passed in 700s\n")
    assert bt.latest_run_dir("08-fresco", log, runs=runs) == new
    assert bt.latest_run_dir("08-fresco", None, runs=runs) == new
    assert bt.latest_run_dir("09-karsa", log, runs=runs) is None

