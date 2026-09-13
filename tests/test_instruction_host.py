"""`HOST={claude,copilot}`: the plumbing, and the four things it must never do (spec 014).

keel-cloud `canon/designs/keel-skill-design.md` §5.5 gives this eval a second host and one rule
about it: *"two runs under different hosts are different measurements and must never be
averaged."* Everything guarded here is a way that rule could be broken quietly —

1. a Copilot bundle carrying the **Claude prompt**, because a renderer moved and the fallback was
   silent (`render`, `build_cases`);
2. a Copilot report or register **titled as Claude's**, on the two pages a person reads with their
   own judgement (`render_report`, `render_register`, `rescore`);
3. a Copilot run reporting **`$0.00`**, which is a lie in the shape of a number (C-7);
4. a **second executor table** in this repository, drifting from keel-runtime's own (`get_executor`,
   `EXECUTOR_BINARIES`).

Stackless and modelless throughout: fakes stand in for both CLIs, because what is guarded is how
this package *chooses and records* a host, not what either CLI does.
"""

from __future__ import annotations

import json
import types

import pytest

from instructions import marks as marks_mod
from instructions import prompts as prompts_mod
from instructions import report as report_mod
from instructions import rescore as rescore_mod
from instructions import run as run_mod
from instructions import runner as runner_mod

# --------------------------------------------------------------------------------------- fakes


class _FakeRuntime:
    """Just enough of `keel_runtime.executor` to be chosen, rendered through and asked for a
    binary. Every name here exists on the real module at keel-runtime `271c01c`."""

    COPILOT_EXCLUDED_TOOLS = ("bash", "read")
    COPILOT_AUTH_MARKERS = ("not logged in", "no valid github token")

    @staticmethod
    def InferenceRequest(**kw):                       # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)

    @staticmethod
    def canonical_executor_name(name):
        return {"claude-code": "claude"}.get(name, name)

    @staticmethod
    def build_prompt(request):
        return "CLAUDE-BODY\n" + json.dumps(request.request_payload.get("context"))

    @staticmethod
    def _prompt_sections(request):
        return {"context": request.request_payload.get("context")}

    @staticmethod
    def _build_envelope_schema(contract):
        return {"schema-for": contract.get("allowed_outcomes")}

    @staticmethod
    def _render_copilot_prompt(sections, schema):
        return ("SYSTEM\n...\n\nRESPONSE\n" + json.dumps(schema)
                + "\n\nCLAUDE-BODY\n" + json.dumps(sections["context"]))


def _payload():
    return prompts_mod.payload_for("INSTRUCTION", {"market": "GB"},
                                   {"allowed_outcomes": ["COMPLETED"]})


class _Claudeish:
    timeout_seconds = 300.0
    max_turns = 6
    budget_usd = 1.0


class _Copilotish:
    """`CopilotExecutor` has **no** `max_turns` and **no** `budget_usd`: the CLI has no flag for
    either, and keel-runtime refuses to pretend otherwise (C-7)."""

    timeout_seconds = 300.0
    max_ai_credits = 30


@pytest.fixture(scope="module")
def real_runtime():
    """keel-runtime's **actual** executor module, from the sibling checkout.

    The binary table is the one thing here that must not be faked: the point of FR-002 is that
    `claude-code` -> `claude` is decided in `keel_runtime.config` and nowhere else, and a fake
    table would prove only that this test agrees with itself.
    """
    from stack.config import load_config                                     # noqa: PLC0415

    try:
        executor, _validator = prompts_mod.load_runtime(load_config(validate=False).keel_runtime)
    except prompts_mod.RuntimeUnavailable as reason:
        pytest.skip(str(reason))
    return executor


def _args(host="claude", **kw):
    base = dict(host=host, baseline=False, n_runs=1, filter=None, no_judge=False)
    base.update(kw)
    return types.SimpleNamespace(**base)


# ------------------------------------------------------------------- 1. the prompt is the host's


def test_the_copilot_prompt_is_the_runtimes_own_copilot_rendering_not_the_claude_one():
    """Design §5.4 (C-8): the body is shared, and the `SYSTEM` and `RESPONSE` sections Claude
    receives as `--system-prompt` and `--json-schema` flags move into the text on a CLI that has
    neither. A bundle recording the Claude rendering under a Copilot run would be publishing a
    prompt nobody sent."""
    claude = prompts_mod.render(_FakeRuntime, _payload(), host="claude")
    copilot = prompts_mod.render(_FakeRuntime, _payload(), host="copilot")

    assert claude.startswith("CLAUDE-BODY")
    assert "SYSTEM" not in claude and "RESPONSE" not in claude
    assert copilot.startswith("SYSTEM")
    assert "RESPONSE" in copilot
    assert "CLAUDE-BODY" in copilot, "the body is shared; only the two flag-shaped sections move"


def test_a_renamed_renderer_refuses_by_name_rather_than_sending_the_other_hosts_prompt():
    """The one failure a bundle cannot be re-read out of: the wrong prompt filed under the right
    host. So a keel-runtime without `_render_copilot_prompt` stops the run instead."""
    stripped = types.SimpleNamespace(
        InferenceRequest=_FakeRuntime.InferenceRequest,
        canonical_executor_name=_FakeRuntime.canonical_executor_name,
        build_prompt=_FakeRuntime.build_prompt,
        _prompt_sections=_FakeRuntime._prompt_sections,
        _build_envelope_schema=_FakeRuntime._build_envelope_schema)

    with pytest.raises(prompts_mod.RuntimeUnavailable) as raised:
        prompts_mod.render(stripped, _payload(), host="copilot")

    assert "_render_copilot_prompt" in str(raised.value)
    assert "will not substitute" in str(raised.value)


def test_the_host_alias_is_keel_runtimes_and_an_unknown_host_is_passed_through_unguessed():
    assert prompts_mod.canonical_host(_FakeRuntime, "claude-code") == "claude"
    assert prompts_mod.canonical_host(_FakeRuntime, "copilot") == "copilot"
    assert prompts_mod.canonical_host(_FakeRuntime, "gemini") == "gemini"


def test_claude_code_the_alias_still_gets_the_claude_rendering():
    assert prompts_mod.render(_FakeRuntime, _payload(), host="claude-code").startswith(
        "CLAUDE-BODY")


def test_every_case_a_copilot_run_builds_carries_the_copilot_prompt(monkeypatch):
    """Not just the first: `build_cases` renders three kinds of case in three separate loops, and
    a host threaded into two of them would leave a bundle two-thirds honest."""
    seen = []

    def _record(executor_module, payload, *, job_id="eval", host="claude"):
        seen.append(host)
        return f"prompt-for-{host}"

    monkeypatch.setattr(prompts_mod, "render", _record)
    cases = _build_three_kinds(host="copilot")

    assert {c.kind for c in cases} == {"ASSUMPTIONS", "READING", "BRIEF"}, \
        "all three loops must be exercised or this test proves nothing"
    assert set(seen) == {"copilot"}
    assert {c.prompt for c in cases} == {"prompt-for-copilot"}


def _build_three_kinds(*, host):
    """One entry with one stage's beliefs, one person who wrote something, and a BRIEF."""
    contract = {"allowed_outcomes": ["COMPLETED"]}
    exported = types.SimpleNamespace(
        keys_for=lambda screen: ["market"] if "ASSUMPTIONS" in screen else
        (["invitation_id", "anchors"] if screen == "INTERPRET" else ["project_name"]),
        for_screen=lambda screen: contract)
    person = types.SimpleNamespace(
        person="p1", written=lambda: [("A1", {"text": "twice a week", "tap": None})])
    entry = types.SimpleNamespace(
        id="e1", title="Entry", market={"country": "GB"}, statements={"problem": "s"},
        expected={"stages": {}}, people=lambda: [person],
        beliefs_for=lambda stage: [], role=lambda rid: {}, anchor=lambda aid: {"stage": "PROBLEM"})
    instructions = {screen: "INSTRUCTION" for screen in
                    ("PROBLEM_ASSUMPTIONS", "SOLUTION_ASSUMPTIONS", "COMMERCIAL_ASSUMPTIONS",
                     "INTERPRET", "BRIEF")}
    return prompts_mod.build_cases(entry, exported, instructions, _FakeRuntime,
                                   n_runs=1, host=host)


# ------------------------------------------------------- 2. the executor is keel-runtime's choice


def test_the_binary_comes_from_keel_runtimes_own_table_not_from_the_host_word(real_runtime):
    """FR-002. `host` is never used as a command name: `claude-code` is a host and `claude` is a
    binary, and one place decides that -- `keel_runtime.config`, not this repo."""
    assert runner_mod.binary_for(real_runtime, "claude") == "claude"
    assert runner_mod.binary_for(real_runtime, "claude-code") == "claude"
    assert runner_mod.binary_for(real_runtime, "copilot") == "copilot"


def test_a_host_keel_runtime_has_no_binary_for_is_a_refusal_that_names_the_ones_it_has(
        real_runtime):
    with pytest.raises(runner_mod.NotReady) as raised:
        runner_mod.binary_for(real_runtime, "gemini")

    assert "gemini" in str(raised.value)
    assert "claude" in str(raised.value) and "copilot" in str(raised.value)


def test_run_py_constructs_its_executor_through_get_executor_and_never_names_a_class():
    """FR-003, guarded as source rather than behaviour, because the whole point is what is *not*
    written here: `runs/DRIFT.md` #33/#36/#41/#44/#45 is five instances of this referee keeping
    its own copy of something it does not own, and a second `{host: class}` table would be the
    sixth."""
    source = (run_mod.__file__ or "").replace(".pyc", ".py")
    body = open(source, encoding="utf-8").read()

    assert "executor_module.get_executor(" in body
    assert "ClaudeCodeExecutor(" not in body, "a class named here is a table that can drift"
    assert "CopilotExecutor(" not in body


# ------------------------------------------------------------------- 3. the pre-flight, per host


def test_a_dry_run_records_the_host_and_its_binary_and_asks_no_cli_for_a_version(
        tmp_path, real_runtime):
    (tmp_path / "keel-cloud").mkdir()
    (tmp_path / "keel-cloud" / "gradlew").write_text("")
    corpus = tmp_path / "keel-cloud" / "canon" / "designs" / "measured-beliefs" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "01.yaml").write_text("id: 01")
    (tmp_path / "keel-runtime" / "keel_runtime").mkdir(parents=True)
    (tmp_path / "keel-runtime" / "keel_runtime" / "executor.py").write_text("")
    config = types.SimpleNamespace(keel_cloud=tmp_path / "keel-cloud",
                                   keel_runtime=tmp_path / "keel-runtime")

    facts = runner_mod.preflight(config, dry_run=True, host="copilot",
                                 executor_module=real_runtime)

    assert facts == {"host": "copilot", "cli": "copilot", "cli_version": None}


def test_the_copilot_probe_is_decided_by_the_jsonl_and_not_by_the_exit_code(monkeypatch):
    """C-3, measured against 1.0.83: a run whose every tool was denied and whose task therefore
    failed **exited 0**, and a bogus token **exited 1** with no JSONL at all. A probe that read
    `returncode` would pass the first and fail the second, which is backwards."""
    failed_but_zero = _fake_run(returncode=0, stdout=json.dumps(
        {"type": "session.error", "data": {"message": "the task could not be completed"}}))
    monkeypatch.setattr(runner_mod.subprocess, "run", failed_but_zero)
    assert "session error" in runner_mod._copilot_ready("copilot", _FakeRuntime)

    fine_but_one = _fake_run(returncode=1, stdout=json.dumps(
        {"type": "assistant.message", "data": {"phase": "final_answer", "content": "ok"}}))
    monkeypatch.setattr(runner_mod.subprocess, "run", fine_but_one)
    assert runner_mod._copilot_ready("copilot", _FakeRuntime) is None


def test_an_unauthenticated_copilot_is_named_as_that_and_not_as_a_session_error(monkeypatch):
    """The marker is keel-runtime's `COPILOT_AUTH_MARKERS` -- the string that means "not logged
    in" is a measurement of a CLI and belongs where it was measured (C-6), not in a copy here.
    1.0.83 puts it on **stderr** with an empty stdout, so stderr is read too."""
    monkeypatch.setattr(runner_mod.subprocess, "run",
                        _fake_run(returncode=1, stdout="", stderr="Error: not logged in"))

    reason = runner_mod._copilot_ready("copilot", _FakeRuntime)

    assert "not logged in" in reason
    assert "COPILOT_GITHUB_TOKEN" in reason, "a refusal must name the way out of itself"


def test_a_copilot_probe_that_produced_no_jsonl_at_all_is_a_refusal(monkeypatch):
    monkeypatch.setattr(runner_mod.subprocess, "run",
                        _fake_run(returncode=0, stdout="", stderr=""))

    assert "no JSONL" in runner_mod._copilot_ready("copilot", _FakeRuntime)


def test_the_probe_excludes_every_tool_keel_runtime_excludes(monkeypatch):
    """The probe is the executor's own closed shape or it is not a probe of the same thing."""
    captured = {}

    def _capture(argv, **kw):
        captured["argv"] = argv
        return types.SimpleNamespace(returncode=0, stdout=json.dumps({"type": "result"}),
                                     stderr="")

    monkeypatch.setattr(runner_mod.subprocess, "run", _capture)
    runner_mod._copilot_ready("copilot", _FakeRuntime)

    for tool in _FakeRuntime.COPILOT_EXCLUDED_TOOLS:
        assert f"--excluded-tools={tool}" in captured["argv"]
    assert "--no-ask-user" in captured["argv"]


def _fake_run(*, returncode, stdout, stderr=""):
    def _run(argv, **kw):
        return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)
    return _run


# --------------------------------------------------------------------- 4. which model answered


def test_the_reported_model_comes_from_the_envelope_when_the_host_puts_it_there():
    assert runner_mod.reported_model({"model": "claude-opus-5"}) == "claude-opus-5"
    assert runner_mod.reported_model(
        {"modelUsage": {"b-model": {}, "a-model": {}}}) == "a-model, b-model"


def test_a_copilot_run_names_the_model_its_own_router_chose(monkeypatch):
    """`runs/DRIFT.md` #53: `CopilotExecutor.last_envelope` carries no model at all, so the only
    record of what answered is the router's own `session.auto_mode_resolved` event. C-5 requires a
    measured run to name the model it measured, so it is read from there."""
    executor = types.SimpleNamespace(last_events=[
        {"type": "session.auto_mode_resolved", "data": {"chosenModel": "mai-code-1.1-flash"}},
        {"type": "assistant.turn_end", "data": {}}])

    assert runner_mod.reported_model({"executor": "copilot"}, executor) == "mai-code-1.1-flash"


def test_a_run_that_named_no_model_anywhere_records_none_rather_than_a_guess():
    executor = types.SimpleNamespace(last_events=[{"type": "assistant.turn_end", "data": {}}])

    assert runner_mod.reported_model({"executor": "copilot"}, executor) is None


def test_the_usage_checkpoint_names_the_model_when_the_router_announced_no_choice():
    """A pinned `--model` run may emit no `auto_mode_resolved` at all."""
    executor = types.SimpleNamespace(last_events=[
        {"type": "session.usage_checkpoint",
         "data": {"promptCacheBreakState": [{"models": {"gpt-5.1": {"tool_count": 0}}}]}}])

    assert runner_mod.reported_model({}, executor) == "gpt-5.1"


# ----------------------------------------------------------- 5. premium requests, never dollars


def test_a_copilot_answer_carries_premium_requests_and_invents_no_dollar_figure():
    executor = _Executor(response={"outcome": "COMPLETED", "result": {}},
                         envelope={"num_turns": 2, "premium_requests": 1, "executor": "copilot"})

    answer = runner_mod.ask(_FakeExecutorModule, _FakeValidatorModule, executor,
                            _minimal_case())

    assert answer.premium_requests == 1
    assert answer.total_cost_usd is None, "C-7: no dollar figure the host did not give"


def test_the_report_states_a_run_s_spend_in_its_own_hosts_unit():
    assert report_mod._spend({"total_premium_requests": 131, "total_cost_usd": None}) == \
        "131 premium requests (this host reports no dollars)"
    assert report_mod._spend({"total_cost_usd": 41.7228}) == "$41.72"
    assert report_mod._spend({}) == "cost not reported"


def test_a_copilot_verdict_carries_no_zero_dollars():
    """A `$0.00` beside a run that really cost the founder a hundred premium requests is the
    worst number this bundle could publish: it reads as free."""
    assert "0.00" not in report_mod._spend({"total_premium_requests": 0})


class _FakeExecutorModule:
    class ExecutorUnavailable(Exception):
        pass

    class ExecutorTimeout(Exception):
        pass

    class ExecutorAuthFailure(Exception):
        pass

    class InvalidResponse(Exception):
        pass

    @staticmethod
    def InferenceRequest(**kw):                       # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)


class _FakeValidatorModule:
    class InvalidResponse(Exception):
        pass

    @staticmethod
    def validate_response(response, contract):
        return None


class _Executor:
    def __init__(self, *, response=None, envelope=None):
        self.response = response
        self.envelope = envelope
        self.last_envelope = None
        self.last_events = None

    def execute(self, request):
        self.last_envelope = self.envelope
        return self.response


def _minimal_case():
    return prompts_mod.Case(case_id="e/PROBLEM/run1", kind="ASSUMPTIONS", entry_id="e",
                            screen="PROBLEM_ASSUMPTIONS", subject="PROBLEM", run_index=1,
                            payload={"response_contract": {"allowed_outcomes": ["COMPLETED"]}})


# --------------------------------------------------------------- 6. the bundle says which host


def test_a_copilot_bundle_is_named_for_its_host_and_a_claude_one_keeps_the_name_it_had(tmp_path,
                                                                                       monkeypatch):
    made = []
    monkeypatch.setattr(report_mod, "new_run_dir",
                        lambda slug: made.append(slug) or (tmp_path / slug))
    monkeypatch.setattr(report_mod, "write_versions", lambda run_dir, config: None)
    for slug in ("instructions", "instructions-copilot", "instructions-baseline-copilot"):
        (tmp_path / slug).mkdir()

    report_mod.start_bundle(None, baseline=False, host="claude")
    report_mod.start_bundle(None, baseline=False, host="copilot")
    report_mod.start_bundle(None, baseline=True, host="copilot")

    assert made == ["instructions", "instructions-copilot", "instructions-baseline-copilot"], \
        "every run of record cited so far is a `-instructions` directory and stays one"


def test_the_manifest_is_written_before_the_first_call_and_names_host_cli_and_rubric(tmp_path):
    manifest = run_mod._manifest(_args("copilot"), {"cli": "copilot", "cli_version": "1.0.83"},
                                 _Copilotish(), None, None, "2026-09-09T00:00:00Z")
    report_mod.write_manifest(tmp_path, manifest)
    written = json.loads((tmp_path / "manifest.json").read_text())

    assert written["host"] == "copilot"
    assert written["cli"] == {"binary": "copilot", "version": "1.0.83"}
    # spec 022 (model routing) added the two per-class fields, `None` on a single-model run.
    assert written["model"] == {"pinned": None, "reported": None, "per_class": None,
                                "table": None}
    assert written["marks_version"] == marks_mod.MARKS_VERSION
    assert written["started_at"] == "2026-09-09T00:00:00Z"


def test_a_cap_this_host_does_not_have_is_none_rather_than_a_number_it_never_enforced():
    """`CopilotExecutor` has no turn cap and no dollar cap because the CLI has no flag for
    either. Reporting production's Claude numbers beside a Copilot run would describe a cap
    nothing enforced."""
    block = run_mod._model_block(_args("copilot"), {"cli": "copilot", "cli_version": "1.0.83"},
                                 _Copilotish(), None, "mai-code-1.1-flash")

    assert block["host"] == "copilot"
    assert block["job_max_turns"] is None
    assert block["job_budget_usd"] is None
    assert block["max_ai_credits"] == 30
    assert block["reported_model"] == "mai-code-1.1-flash"
    assert block["pinned_model"] is None


def test_the_claude_block_still_carries_the_three_caps_it_always_did():
    block = run_mod._model_block(_args("claude"), {"cli": "claude", "cli_version": "2.1.263"},
                                 _Claudeish(), None, "claude-opus-5")

    assert (block["job_timeout_seconds"], block["job_max_turns"], block["job_budget_usd"]) == \
        (300.0, 6, 1.0)


def test_the_judge_stays_on_claude_on_both_hosts_and_the_block_says_so():
    """The tie-breaker is the referee's, not the subject's: keeping it constant is what makes a
    comparison a comparison. Written down rather than assumed."""
    for host in ("claude", "copilot"):
        block = run_mod._model_block(_args(host), {}, _Claudeish(), None, None)
        assert block["judge_host"] == "claude"
    off = run_mod._model_block(_args("copilot", no_judge=True), {}, _Claudeish(), None, None)
    assert off["judge_host"] == "off"


# ----------------------------------------------------- 7. the two pages a person reads, titled


def test_the_report_names_the_host_in_its_title_and_refuses_to_be_averaged():
    path = _render_a_report(host="copilot")
    page = path.read_text(encoding="utf-8")

    assert "<title>Instruction eval on GitHub Copilot" in page
    assert "must never be averaged" in page


def test_the_register_says_whose_words_are_on_it_before_the_first_word(tmp_path):
    """FR-006, and the most expensive quiet mistake in the bundle: register is exactly what
    differs between two models, and this page is read with a person's own judgement."""
    path = report_mod.render_register(tmp_path, entries_by_market={}, paragraphs=None,
                                      host="copilot", cli_version="GitHub Copilot CLI 1.0.83.",
                                      model="mai-code-1.1-flash")
    page = path.read_text(encoding="utf-8")

    assert "<title>Register on GitHub Copilot" in page
    assert "Register — GitHub Copilot" in page
    assert "every word on this page was written by GitHub Copilot" in page
    assert "1.0.83" in page and "mai-code-1.1-flash" in page


def test_a_register_for_a_run_whose_cli_named_no_model_says_that_rather_than_nothing(tmp_path):
    page = report_mod.render_register(tmp_path, entries_by_market={}, paragraphs=None,
                                      host="copilot").read_text(encoding="utf-8")

    assert "model not reported by the CLI" in page


def test_a_rescored_copilot_bundle_keeps_its_own_host_on_the_page_it_rewrites(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"host": "copilot"}))
    assert rescore_mod._host_of(tmp_path, {}) == "copilot"


def test_a_bundle_taken_before_spec_014_rescores_as_claude_which_is_what_it_was(tmp_path):
    assert rescore_mod._host_of(tmp_path, {"model": {"claude_version": "2.1.263"}}) == "claude"
    assert rescore_mod._host_of(tmp_path, {"model": {"host": "copilot"}}) == "copilot"


def _render_a_report(*, host):
    from tests.test_instruction_modules_import import _SCORECARD             # noqa: PLC0415
    import copy                                                              # noqa: PLC0415
    import tempfile                                                          # noqa: PLC0415
    from pathlib import Path                                                 # noqa: PLC0415

    scorecard = copy.deepcopy(_SCORECARD)
    scorecard["model"].update({"host": host, "cli": host,
                               "cli_version": "GitHub Copilot CLI 1.0.83.",
                               "job_max_turns": None, "job_budget_usd": None,
                               "max_ai_credits": 30})
    verdict = {"scenario": "instructions", "baseline": False, "host": host, "n_runs": 1,
               "cases": 2, "errored": 0, "duration_s": 1.0, "total_cost_usd": None,
               "total_premium_requests": 131,
               "marks": marks_mod.judge(scorecard["totals"], marks_mod.load())}
    run_dir = Path(tempfile.mkdtemp())
    return report_mod.render_report(run_dir, verdict=verdict, scorecard=scorecard,
                                    versions={}, host=host)


# ---------------------------------------------------------------- 8. what this feature must not do


def test_the_rubric_did_not_move():
    """FR-008. A second host is not a rubric change: the same marks, judged the same way, asked
    of somebody else. A `MARKS_VERSION` bump here would make the two hosts' runs incomparable in
    the one direction the design needs them comparable."""
    # v6 (judgement call 22, the founder, 2026-09-12) moved the rule-refusal mark to a rate and
    # added the shape-refusal zero -- for every host at once, which is what keeps this test's
    # point: the hosts are still judged by one rubric, and no host got its own.
    assert marks_mod.MARKS_VERSION == 6
    assert marks_mod.DEFAULTS == {"anchoring_accuracy": 0.90, "golden_belief_recall": 0.80,
                                  "rule_refusal_rate": 0.02, "shape_refusals": 0,
                                  "brief_paragraphs": 1.00}


def test_the_makefile_defaults_to_claude_and_threads_the_host_through():
    from stack.config import REPO_ROOT                                      # noqa: PLC0415

    body = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "--host $(if $(HOST),$(HOST),claude)" in body
    assert "HOST=copilot" in body, "the target's own comment must show the way in"


@pytest.mark.parametrize("host", ["gemini", "", "claude,copilot"])
def test_an_unknown_host_is_refused_before_a_prerequisite_is_checked(host, capsys):
    """`choices` on the argument, not a check after the pre-flight: an unknown host must cost
    nothing at all, not a Gradle export and a corpus load first."""
    with pytest.raises(SystemExit) as raised:
        run_mod.main(["--host", host, "--dry-run"])

    assert raised.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
