"""S-012's own stackless tests (spec `016-copilot-e2e`).

Everything here is a property that would otherwise only be observable **during a paid run** --
which is the same reason spec 013's packaging beds have stackless tests: the argv a live leg builds,
the environment it hands a child, and the readers that turn a runtime's artefacts into an
assertion. A live run is the wrong place to discover that a flag name was wrong.

Nothing here shells `copilot`, and nothing here needs a stack, a browser or a model.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import copilot_host


# ------------------------------------------------------------------------------------ the argv

class _Recorded:
    """Captures the argv `_run_copilot` would run, without running it."""

    def __init__(self):
        self.argv = None

    def __call__(self, argv, **kwargs):
        self.argv = argv
        raise RuntimeError("not run on purpose")


def _host(tmp_path: Path, **kw) -> copilot_host.CopilotHost:
    return copilot_host.CopilotHost(
        home=tmp_path / "copilot-home", keel_home=tmp_path / "keel-home",
        base_url="http://localhost:18080", artifacts=tmp_path / "artifacts",
        base_env={"PATH": "/usr/bin", "KEEL_RUNTIME_PATH": "/somewhere/keel-runtime",
                  "KEEL_HOME": "/the/founders/home", "KEEL_BASE_URL": "http://elsewhere:1"},
        **kw)


def _argv(tmp_path: Path, **kw) -> list[str]:
    host = _host(tmp_path, **kw)
    recorded = _Recorded()
    import subprocess
    real = subprocess.run
    subprocess.run = recorded
    try:
        with pytest.raises(RuntimeError):
            copilot_host._run_copilot(host, "keel connect", timeout=1, slug="probe")
    finally:
        subprocess.run = real
    return recorded.argv


def test_the_prompt_is_the_founders_own_three_words(tmp_path):
    """`-p "keel connect"`, and nothing that names the skill, the plugin or the script. A prompt
    that said "run scripts/keel_connect_check.py" would prove the *shell* works and nothing about
    whether the host recognised what a founder means."""
    argv = _argv(tmp_path)
    assert argv[1] == "-p"
    assert argv[2] == "keel connect"
    joined = " ".join(argv).lower()
    for word in ("keel_connect_check", "skill.md", "plugin", "scripts/"):
        assert word not in joined, f"the prompt or its flags name {word!r}; the founder does not"


def test_bare_never_appears_and_is_pinned_as_forbidden(tmp_path):
    """spec 013's T-2 trap, kept even though this CLI has no such flag: `--bare` skips skill
    auto-discovery on the *other* host, and the whole of leg one is skill discovery."""
    argv = _argv(tmp_path)
    assert "--bare" in copilot_host.FORBIDDEN_FLAGS
    for flag in copilot_host.FORBIDDEN_FLAGS:
        assert flag not in argv


def test_the_two_grants_and_no_blanket_one(tmp_path):
    """`--allow-tool` twice, and never `--allow-all-tools`/`--allow-all`/`--yolo`. A blanket grant
    would make "the skill only needed python3" unobservable, and leg one records the tools the host
    actually called."""
    argv = _argv(tmp_path)
    grants = [argv[i + 1] for i, a in enumerate(argv) if a == "--allow-tool"]
    assert grants == ["shell(python3:*)", "skill"]
    for blanket in ("--allow-all-tools", "--allow-all", "--yolo", "--allow-all-paths"):
        assert blanket not in argv, f"{blanket} would hide what the skill actually needed"


def test_the_run_is_machine_readable_and_records_what_it_spent(tmp_path):
    argv = _argv(tmp_path)
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "--usage-output-file" in argv, (
        "without it there is no record of the premium requests the host legs spent")
    assert "--no-auto-update" in argv and "--no-ask-user" in argv


def test_the_referees_own_instructions_never_reach_the_host(tmp_path):
    """The run bundle lives inside keel-e2e-eval, whose `AGENTS.md` describes this harness and
    what its scenarios assert -- and Copilot loads custom instructions from the git root. A host
    briefed on the measurement is not the host a founder has."""
    assert "--no-custom-instructions" in _argv(tmp_path)


def test_the_model_is_pinned_only_when_there_is_one(tmp_path):
    """C-5: `--model` is passed when a slug is pinned and **absent** when it is not. A run that
    sent `--model auto` would be claiming a pin it does not have."""
    assert "--model" not in _argv(tmp_path, model=None)
    argv = _argv(tmp_path, model="claude-sonnet-5")
    assert argv[argv.index("--model") + 1] == "claude-sonnet-5"
    assert "auto" not in argv


# ----------------------------------------------------------------------------- the environment

def test_keel_runtime_path_is_scrubbed_and_the_two_homes_are_this_runs(tmp_path):
    """Invariant T-1, in the one place S-012 can lose it. The founder's own shell exports
    `KEEL_RUNTIME_PATH` (keel-connect-playground's settings do), and an inherited one would put the
    *checkout* back in place of the runtime that travelled inside the plugin."""
    env = _host(tmp_path, model="claude-sonnet-5", runtime_model="gpt-5.6-luna").env()
    assert "KEEL_RUNTIME_PATH" not in env
    assert env["COPILOT_HOME"] == str(tmp_path / "copilot-home")
    assert env["KEEL_HOME"] == str(tmp_path / "keel-home")
    assert env["KEEL_BASE_URL"] == "http://localhost:18080"


def test_the_hosts_model_and_the_runtimes_are_two_different_pins(tmp_path):
    """They answer two different questions and `runs/DRIFT.md` #59 made them disagree: leg one
    asks what a founder's own Copilot does with the skill (so it keeps the plan's own default),
    and leg two asks what keel-runtime's executor does with a job (so it pins a model the executor
    can actually read). Tying them together would mean choosing one subject's model to suit the
    other's."""
    env = _host(tmp_path, model="claude-sonnet-5", runtime_model="gpt-5.6-luna").env()
    assert env["KEEL_COPILOT_MODEL"] == "gpt-5.6-luna", (
        "KEEL_COPILOT_MODEL is the *runtime's* pin; the host's --model must not leak into it")
    argv = _argv(tmp_path, model="claude-sonnet-5", runtime_model="gpt-5.6-luna")
    assert argv[argv.index("--model") + 1] == "claude-sonnet-5", (
        "--model is the *host's* pin; the runtime's must not leak into it")


def test_no_model_env_when_the_runtime_is_not_pinned(tmp_path):
    assert "KEEL_COPILOT_MODEL" not in _host(tmp_path, runtime_model=None).env()


def test_the_fresh_keel_home_names_its_keel(tmp_path):
    """`keel status` and `keel_disconnect.py` take no `--base-url`, so a home that does not name
    its Keel answers `environment: null` -- and S-012 asserts `environment` reads this stack's own
    address. Same reason `stack/runtime.py::reset` writes one."""
    host = _host(tmp_path)
    path = host.write_home_config()
    assert json.loads(path.read_text())["base_url"] == "http://localhost:18080"


def test_a_token_in_the_shell_is_named_and_isolation_still_holds():
    """The three legitimate ways a run is authenticated, in the CLI's own precedence. A bundle
    that did not say which one answered would leave a reader unable to tell an isolated home from
    the founder's real one."""
    assert copilot_host.credential_plan({"COPILOT_GITHUB_TOKEN": "x"})["variable"] == \
        "COPILOT_GITHUB_TOKEN"
    assert copilot_host.credential_plan({"GH_TOKEN": "x"})["variable"] == "GH_TOKEN"
    assert copilot_host.credential_plan({"GITHUB_TOKEN": "x"})["variable"] == "GITHUB_TOKEN"
    plan = copilot_host.credential_plan({})
    assert plan["how"] == "stored OAuth, outside COPILOT_HOME"
    assert "yes" in plan["isolated_home"]


# ------------------------------------------------------------- reading what the skill left behind

LAUNCH_LOG = (
    "keel connect starting\n"
    "KEEL_USER_CODE=QK7M-2XBD\n"
    "KEEL_VERIFICATION_URI=http://localhost:5173/connect?user_code=QK7M-2XBD\n"
    "waiting for approval\n"
)


def test_the_launch_log_is_read_by_the_skills_own_prefixes():
    assert copilot_host.user_code_in(LAUNCH_LOG) == "QK7M-2XBD"
    assert copilot_host.verification_uri_in(LAUNCH_LOG) == \
        "http://localhost:5173/connect?user_code=QK7M-2XBD"


def test_a_log_with_no_code_reads_as_no_code_rather_than_a_guess():
    """The failure S-012 must be able to tell apart: a host that said something confident while
    the runtime printed nothing. Empty, absent and a log with only the URI must all be `None`."""
    assert copilot_host.user_code_in("") is None
    assert copilot_host.user_code_in("nothing happened here\n") is None
    assert copilot_host.user_code_in("KEEL_USER_CODE=\n") is None
    assert copilot_host.verification_uri_in("KEEL_USER_CODE=QK7M-2XBD\n") is None


LAUNCH_LOG_COPILOT = (
    "KEEL_ENVIRONMENT=localhost:18080 base_url=http://localhost:18080\n"
    "KEEL_EXECUTOR=copilot source=flag binary=/opt/homebrew/bin/copilot "
    "version=GitHub Copilot CLI 1.0.83. model=claude-sonnet-5\n"
    "KEEL_USER_CODE=RAJK-LMNE\n"
)


def test_the_runtimes_own_startup_line_says_which_executor_it_chose():
    """`runs/DRIFT.md` #58's answer. `keel status` reports the *caller's* resolution -- the
    contract says so in as many words -- so leg two's gate reads the line the running process
    printed from inside itself instead. `version=` carries spaces, which is why this is parsed by
    the keys it knows rather than split on whitespace."""
    read = copilot_host.launch_executor_in(LAUNCH_LOG_COPILOT)
    assert read == {"executor": "copilot", "source": "flag",
                    "binary": "/opt/homebrew/bin/copilot",
                    "version": "GitHub Copilot CLI 1.0.83.", "model": "claude-sonnet-5"}


def test_source_flag_is_the_whole_chain_in_one_word():
    """`SKILL.md` tells the host to add `--host copilot`; the skill's script maps that to
    `--executor copilot`; the runtime records it as `source=flag`. A run that came out `copilot`
    by `source=path` or `source=host` would be a runtime that **guessed right**, which proves
    nothing about the skill's own line -- so leg two asserts the source too."""
    assert copilot_host.launch_executor_in(LAUNCH_LOG_COPILOT)["source"] == "flag"
    guessed = copilot_host.launch_executor_in(
        "KEEL_EXECUTOR=copilot source=path binary=/opt/homebrew/bin/copilot\n")
    assert guessed["source"] == "path"


def test_a_log_with_no_startup_line_is_unknowable_rather_than_assumed():
    assert copilot_host.launch_executor_in("") is None
    assert copilot_host.launch_executor_in("KEEL_USER_CODE=QK7M-2XBD\n") is None


def test_the_scenario_reads_the_executor_from_the_log_and_not_from_status():
    """The correction itself, held: a future edit that put `status.get("executor")` back into an
    assertion would be re-asserting the caller's own environment."""
    assert "launch_executor_in" in SCENARIO
    assert 'assert status.get("executor")' not in SCENARIO, (
        "leg two is asserting `keel status`'s executor again; DRIFT #58 says that key describes "
        "the caller, not the runtime")


def test_the_code_shape_is_the_one_the_cloud_issues():
    assert copilot_host.looks_like_a_user_code("QK7M-2XBD")
    for bad in (None, "", "QK7M2XBD", "qk7m-2xbd", "QK7M-2XBD-EXTRA", "the code is QK7M-2XBD"):
        assert not copilot_host.looks_like_a_user_code(bad), bad


def test_the_heartbeat_is_read_or_honestly_absent(tmp_path):
    """The narrowest available proof that something really launched a runtime: a heartbeat written
    the moment `connect` has a pid and a home, in `awaiting_approval` (keel-runtime `bfc0ad6`,
    which closed `runs/DRIFT.md` #51). Missing and corrupt both read as `None` -- never as a pass.
    """
    home = tmp_path / "keel-home"
    home.mkdir()
    assert copilot_host.read_heartbeat(home) is None
    (home / copilot_host.HEARTBEAT_FILENAME).write_text("{not json")
    assert copilot_host.read_heartbeat(home) is None
    (home / copilot_host.HEARTBEAT_FILENAME).write_text(json.dumps(
        {"pid": 4242, "base_url": "http://localhost:18080",
         "state": copilot_host.STATE_AWAITING_APPROVAL, "last_heartbeat_at": "2026-09-10T20:00:00Z"}))
    beat = copilot_host.read_heartbeat(home)
    assert beat["state"] == copilot_host.STATE_AWAITING_APPROVAL
    assert beat["pid"] == 4242


# ------------------------------------------------------------------- reading what Copilot said

def _run(**kw) -> copilot_host.CopilotRun:
    base = {"argv": ["copilot"], "exit_code": 0, "reply_text": ""}
    base.update(kw)
    return copilot_host.CopilotRun(**base)


def test_premium_requests_come_from_copilots_own_numbers_and_never_become_dollars():
    """C-7: Copilot reports premium requests and the runtime does not invent a dollar figure. The
    usage file is preferred; the final `result` event is the fallback; **`None` is the answer when
    neither said**, because a `0` beside a metered run reads as free."""
    assert _run(usage={"totalPremiumRequestCost": 3}).premium_requests == 3
    assert _run(events=[{"type": "result", "usage": {"premiumRequests": 2}}]).premium_requests == 2
    assert _run().premium_requests is None
    run = _run(usage={"totalPremiumRequestCost": 3})
    assert not hasattr(run, "total_cost_usd")


def test_the_final_answer_skips_the_tool_calling_turns_empty_message():
    """keel-runtime's own rule (`executor._copilot_final_answer`): a turn that called a tool emits
    an `assistant.message` with empty content, so "the last assistant message" finds that one."""
    events = [
        {"type": "assistant.message", "data": {"content": "let me check", "model": "m"}},
        {"type": "assistant.message", "data": {"content": "", "toolRequests": [{"name": "shell"}]}},
    ]
    assert copilot_host._final_answer(events) == "let me check"
    assert copilot_host._final_answer([]) == ""


def test_the_model_that_answered_is_readable_from_either_place():
    """`runs/DRIFT.md` #53's question, asked of the host: the usage file's `currentModel` first,
    then the message that carried an answer."""
    assert _run(usage={"currentModel": "claude-sonnet-5"}).model == "claude-sonnet-5"
    assert _run(events=[{"type": "assistant.message",
                          "data": {"content": "ok", "model": "gpt-5.6-luna"}}]).model == \
        "gpt-5.6-luna"
    assert _run().model is None


def test_the_loose_connected_check_is_loose_and_is_never_the_only_evidence():
    assert copilot_host.mentions_connected("Keel is already connected on localhost:18080.")
    assert copilot_host.mentions_connected("Your runtime is connected.")
    assert not copilot_host.mentions_connected("Here is your code: QK7M-2XBD")
    assert not copilot_host.mentions_connected("")


# --------------------------------------------------------------------- reading the skill listing

#: The shape CLI 1.0.83 actually prints, captured from a real `copilot skill list --json` after a
#: real `copilot plugin install keel@keel` (2026-09-10). The others around it are plausible
#: neighbours, so a CLI upgrade that renames a key is a still-green run rather than a red one.
MEASURED_1_0_83 = [
    {"name": "keel-connect", "description": "Use when the user says or means \"keel connect\" ...",
     "source": "plugin",
     "path": "/tmp/copilot-home/installed-plugins/keel/keel/skills/keel-connect",
     "enabled": True},
    {"name": "customize-cloud-agent", "description": "...", "source": "builtin",
     "path": "/Users/x/Library/Caches/copilot/pkg/darwin-arm64/1.0.83/builtin/customize-cloud-agent",
     "enabled": True},
]


def test_the_shape_this_cli_really_prints_is_read_correctly():
    hit = copilot_host.find_skill(MEASURED_1_0_83)
    assert hit is not None and hit["entry"]["source"] == "plugin"
    assert copilot_host.describes_a_plugin(hit)


def test_a_builtin_skill_is_not_a_plugin_skill_however_its_path_reads():
    """The false positive the explicit source field exists to stop: an installed plugin's path
    contains `installed-plugins`, so a search over every value would call any skill under such a
    path a plugin skill. `source` is the only field that *means* it."""
    builtin = {"name": "keel-connect", "source": "builtin",
               "path": "/somewhere/installed-plugins/keel/skills/keel-connect"}
    assert not copilot_host.describes_a_plugin(copilot_host.find_skill([builtin]))


PLUGIN_SHAPES = [
    {"plugin": [{"name": "keel-connect", "description": "..."}]},
    {"skills": [{"name": "keel-connect", "source": "plugin", "plugin": "keel"}]},
    [{"name": "keel-connect", "kind": "Plugin"}],
    {"sources": {"Plugin": [{"name": "keel-connect"}]}},
]


@pytest.mark.parametrize("listing", PLUGIN_SHAPES)
def test_the_skill_is_found_and_read_as_a_plugin_skill_in_every_plausible_shape(listing):
    """This repository does not own `copilot skill list --json`'s schema, and a referee that
    pinned one would go red on a CLI upgrade that renamed a key while the skill was perfectly
    visible. The name is found structurally, and "from a plugin" is read from the fields beside it
    *or* from the path that reached it."""
    hit = copilot_host.find_skill(listing)
    assert hit is not None
    assert copilot_host.describes_a_plugin(hit)


def test_a_skill_that_is_not_a_plugin_skill_is_not_reported_as_one():
    """The assertion that would otherwise pass by accident: leg one installs a **plugin**, so a
    `keel-connect` sitting in `~/.copilot/skills/` from some earlier experiment must not satisfy
    it."""
    hit = copilot_host.find_skill({"personal": [{"name": "keel-connect", "source": "personal"}]})
    assert hit is not None
    assert not copilot_host.describes_a_plugin(hit)


def test_an_absent_skill_is_absent():
    assert copilot_host.find_skill({"plugin": [{"name": "something-else"}]}) is None
    assert copilot_host.find_skill(None) is None
    assert not copilot_host.describes_a_plugin(None)


# ------------------------------------------------------------------ the scenario's own promises

SCENARIO = (Path(__file__).resolve().parent.parent / "evals"
            / "test_s012_copilot_host_and_thinker.py").read_text()


def test_the_scenario_never_starts_the_runtime_itself():
    """The measurement, held by a test. Leg one is *"did Copilot decide to run the skill"*, and a
    line here that ran `keel_connect_check.py`, or `start_runtime_via_skill`, or
    `python3 -m keel_runtime connect`, would answer that question for it."""
    for forbidden in ("keel_connect_check", "start_runtime_via_skill", "reconnect(",
                      "-m keel_runtime"):
        assert forbidden not in SCENARIO, (
            f"S-012 names {forbidden!r}; only Copilot may start leg one's runtime")


def test_the_scenario_never_names_an_executor():
    """FR-006 is only worth asserting if nothing here chose the executor: `status.executor ==
    'copilot'` must be the *skill's* doing, via `SKILL.md`'s `--host copilot`."""
    # Read as *code*, not as prose: the module's own docstring explains why it never passes the
    # flag, and a substring search over the whole file would find that explanation.
    import ast
    literals = {node.value for node in ast.walk(ast.parse(SCENARIO))
                if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    argv_tokens = {lit for lit in literals if lit.startswith("--")}
    assert "--executor" not in argv_tokens, argv_tokens
    assert 'executor="copilot"' not in SCENARIO


def test_the_scenario_asserts_the_runtimes_artefacts_before_it_reads_a_reply():
    """FR-003, as an ordering property: the heartbeat assertion comes before the one loose read of
    Copilot's own words, so a bundle can never show a run whose only evidence was prose."""
    heartbeat_at = SCENARIO.index("read_heartbeat(keel_home)\n            h.record_assert")
    mentions_at = SCENARIO.index("mentions_connected(second.reply_text)")
    assert heartbeat_at < mentions_at


def test_the_pinned_model_is_one_keel_runtime_can_actually_read():
    """`runs/DRIFT.md` #59, held so the pin cannot drift back. Copilot's Anthropic-vendored
    `assistant.message` events carry no `phase`, and `_copilot_final_answer` reads only the
    `final_answer`-phase message -- so on `claude-sonnet-5`, the upgraded plan's own default,
    every keel-runtime job fails while the model answers correctly. The scenario pins a model that
    emits the field, and says why in the same place it says which."""
    from evals import test_s012_copilot_host_and_thinker as s012
    assert s012.RUNTIME_MODEL == "gpt-5.6-luna"
    assert "#59" in SCENARIO, (
        "the pin is a choice made because of a product fault; the entry that records that fault "
        "must be named beside it")


def test_the_scenario_is_live_and_skips_by_name():
    assert "pytestmark = pytest.mark.live" in SCENARIO
    assert "pytest.skip(ready[\"reason\"])" in SCENARIO, (
        "C-11: an absent host CLI produces a recorded skip with its reason, never a silent pass")


def test_the_settled_statuses_and_the_refused_ones_never_overlap():
    """Two readings of "this interaction ended well" that disagreed would make the run's central
    claim -- zero refusals, every job COMPLETED -- unfalsifiable."""
    from evals import test_s012_copilot_host_and_thinker as s012
    assert not (s012.SETTLED & s012.REFUSED)
    assert "APPLIED" in s012.SETTLED and "DOMAIN_REFUSED" in s012.REFUSED
