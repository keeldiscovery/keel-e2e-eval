"""`instructions/models.py`: the model-routing table, read as keel-cloud writes it and pinned
through the job's own `model` key (keel-cloud `canon/designs/model-routing-design.md` §4-§7,
spec 022).

Stackless and modelless. What is guarded is how this eval *reads* the table and *where* it puts
the pin -- the sixth key of `request_payload`, never the environment -- because a run judged any
other way would not be the run the cloud's table claims.
"""

from __future__ import annotations

import json
import types

import pytest

from instructions import contract as contract_mod
from instructions import models as models_mod
from instructions import prompts as prompts_mod
from instructions import report as report_mod
from instructions import run as run_mod

TABLE = {
    "version": 1,
    "hosts": {
        "claude": {"standard": "sonnet", "light": "haiku"},
        "copilot": {"standard": "gpt-5.6-luna"},
        "codex": {"standard": "gpt-5.6-terra", "light": "gpt-5.5-mini"},
    },
    "_tiers": ["light", "standard", "frontier"],
    # MARKS_VERSION 18 (spec 029 FR-023; spec 040 call 84): the seven classes the eight model screens route
    # through. **This eval cannot start without all seven**: `parse` refuses a table that says nothing about
    # a class this eval measures, so none of these rows is optional here.
    "classes": {"context": "light", "frame": "standard", "calibration": "standard",
                "respondent": "standard", "reading": "light", "brief": "standard", "asked": "light"},
}


def _case(kind, case_id="e/CALIBRATION_PROBLEM/run1"):
    screen = {"CALIBRATION": "CALIBRATION_QUESTIONS", "READING": "INTERPRET", "BRIEF": "BRIEF",
              "CONTEXT": "CONTEXT_INTERPRET", "RESPONDENT": "RESPONDENT_QUESTIONS",
              "FRAME": "PROBLEM_INTERPRET", "COMPARE": "COMPARE"}[kind]
    return prompts_mod.Case(case_id=case_id, kind=kind, entry_id="e", screen=screen,
                            subject="PROBLEM", run_index=1,
                            payload=prompts_mod.payload_for("I", {"k": None}, {"allowed_outcomes": ["COMPLETED"]}))


# ------------------------------------------------------------------ 1. class -> tier -> model


def test_the_resolver_walks_class_to_tier_to_the_hosts_row():
    table = models_mod.parse(TABLE)
    assert table.resolve("codex", "calibration") == "gpt-5.6-terra"
    assert table.resolve("codex", "reading") == "gpt-5.5-mini"
    assert table.resolve("codex", "brief") == "gpt-5.6-terra"
    assert table.resolve_kind("claude", "READING") == "haiku"
    assert table.resolve_screen("claude", "SOLUTION_MECHANISM") == "sonnet"
    assert table.resolve_kind("claude", "COMPARE") is None, "COMPARE is never a model call"


def test_a_missing_host_is_no_pin_never_a_failure():
    table = models_mod.parse(TABLE)
    assert table.resolve("gemini", "calibration") is None
    assert table.job_map("gemini", "CALIBRATION") is None
    assert table.models_used("gemini") == {"context": None, "frame": None, "calibration": None, "respondent": None, "reading": None, "asked": None}


def test_a_missing_tier_on_a_hosts_row_is_the_clis_default_for_that_class():
    """Copilot's row names `standard` only, so its readings run unpinned and the record says so."""
    table = models_mod.parse(TABLE)
    assert table.resolve("copilot", "reading") is None
    assert table.models_used("copilot") == {"context": None, "frame": "gpt-5.6-luna",
                                            "calibration": "gpt-5.6-luna",
                                            "respondent": "gpt-5.6-luna", "reading": None,
                                            "asked": None}


def test_the_empty_table_the_cloud_ships_first_pins_nothing_anywhere():
    table = models_mod.parse({"version": 1, "hosts": {}, "classes": TABLE["classes"]})
    for host in ("claude", "copilot", "codex"):
        assert table.models_used(host) == {"context": None, "frame": None, "calibration": None, "respondent": None, "reading": None, "asked": None}


# ------------------------------------------------------------------------ 2. the file's edges


@pytest.mark.parametrize("bad, words", [
    ({"hosts": {"codex": {"premium": "x"}}, "classes": TABLE["classes"]}, "ladder is exactly"),
    ({"hosts": {}, "classes": {**TABLE["classes"], "essay": "standard"}}, "classes are exactly"),
    ({"hosts": {}, "classes": {**TABLE["classes"], "brief": "huge"}}, "ladder is exactly"),
    ({"hosts": {}, "classes": {"frame": "standard"}}, "says nothing about"),
    ({"hosts": {}, "classes": TABLE["classes"], "_tiers": ["small", "big"]}, "ladder is exactly"),
    ({"hosts": {"codex": {"standard": ""}}, "classes": TABLE["classes"]}, "must be a model name"),
    ({"hosts": []}, "must carry"),
    ([], "not a JSON object"),
])
def test_an_unknown_tier_class_or_shape_is_a_refusal_that_names_it(bad, words):
    with pytest.raises(models_mod.ModelsUnavailable, match=words):
        models_mod.parse(bad)


def test_the_three_tiers_are_all_accepted_and_the_informational_list_is_tolerated():
    document = {"version": 2, "_tiers": ["light", "standard", "frontier"],
                "hosts": {"codex": {"light": "a", "standard": "b", "frontier": "c"}},
                "classes": {**TABLE["classes"], "calibration": "frontier"}}
    table = models_mod.parse(document)
    assert table.resolve("codex", "calibration") == "c"
    assert table.version == 2


def test_a_file_is_read_whole_and_a_missing_or_broken_one_refuses_by_path(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps(TABLE))
    assert models_mod.load(path).source == str(path)
    with pytest.raises(models_mod.ModelsUnavailable, match="could not read"):
        models_mod.load(tmp_path / "missing.json")
    path.write_text("{not json")
    with pytest.raises(models_mod.ModelsUnavailable, match="not JSON"):
        models_mod.load(path)


def test_the_cloud_checkouts_own_resource_is_read_and_its_absence_is_none(tmp_path):
    assert models_mod.from_keel_cloud(tmp_path) is None
    resource = tmp_path / models_mod.CLOUD_RESOURCE
    resource.parent.mkdir(parents=True)
    resource.write_text(json.dumps(TABLE))
    assert models_mod.from_keel_cloud(tmp_path).resolve("codex", "reading") == "gpt-5.5-mini"


# ------------------------------------------------------- 3. --models and the legacy pin exclude


def test_models_and_a_legacy_pin_variable_refuse_each_other(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps(TABLE))
    with pytest.raises(models_mod.ModelsUnavailable, match="KEEL_CODEX_MODEL"):
        models_mod.select(str(path), host="codex", environ={"KEEL_CODEX_MODEL": "gpt-5.5"})
    with pytest.raises(models_mod.ModelsUnavailable, match="KEEL_COPILOT_MODEL"):
        models_mod.select("exported", host="codex", environ={"KEEL_COPILOT_MODEL": "x"})
    assert models_mod.select(None, host="codex", environ={"KEEL_CODEX_MODEL": "x"}) is None, \
        "no --models: the single-model pin of every run of record so far is untouched"


def test_models_exported_is_the_clouds_own_table_and_refuses_when_the_export_has_none(tmp_path):
    with_table = types.SimpleNamespace(directory=tmp_path, model_routing=TABLE)
    table = models_mod.select("exported", host="codex", exported=with_table, environ={})
    assert table.source == f"exported:{tmp_path}"
    without = types.SimpleNamespace(directory=tmp_path, model_routing=None)
    with pytest.raises(models_mod.ModelsUnavailable, match="model-routing.json"):
        models_mod.select("exported", host="codex", exported=without, environ={})
    with pytest.raises(models_mod.ModelsUnavailable, match="exported contract"):
        models_mod.select("exported", host="codex", exported=None, environ={})


def test_run_py_refuses_a_bad_table_before_the_preflight_and_the_lock(monkeypatch, tmp_path,
                                                                     capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"hosts": {}, "classes": {"brief": "enormous"}}))
    monkeypatch.setattr(run_mod, "load_config", lambda: pytest.fail("the config was loaded"))
    assert run_mod.main(["--host", "codex", "--models", str(bad), "--why", "new-model:codex:x"]) == 2
    assert "ladder is exactly" in capsys.readouterr().err


# ------------------------------------------------------------- 4. the pin is the wire's own key


def test_the_pin_is_the_sixth_key_of_the_payload_and_never_the_environment(monkeypatch):
    monkeypatch.delenv("KEEL_CODEX_MODEL", raising=False)
    table = models_mod.parse(TABLE)
    cases = [_case("CALIBRATION"), _case("READING", "e/Tom/run1"), _case("FRAME", "e/PROBLEM_INTERPRET/run1")]
    models_mod.stamp(cases, table, "codex")

    assert list(cases[0].payload) == ["instruction", "context", "interaction_history", "input",
                                      "response_contract", "model"], \
        "the five keys buildRequestPayload writes, in its order, then the cloud's sixth"
    assert cases[0].payload["model"] == {"codex": "gpt-5.6-terra"}
    assert cases[1].payload["model"] == {"codex": "gpt-5.5-mini"}
    assert cases[2].payload["model"] == {"codex": "gpt-5.6-terra"}
    assert [c.model for c in cases] == ["gpt-5.6-terra", "gpt-5.5-mini", "gpt-5.6-terra"]
    assert "KEEL_CODEX_MODEL" not in __import__("os").environ


def test_a_class_the_table_leaves_unpinned_gets_no_key_at_all():
    table = models_mod.parse(TABLE)
    reading = _case("READING")
    models_mod.stamp([reading], table, "copilot")
    assert "model" not in reading.payload and reading.model is None
    calibration = _case("CALIBRATION")
    models_mod.stamp([calibration], None, "copilot")
    assert "model" not in calibration.payload, "no table: the payload is exactly what it was"


def test_stamping_after_the_prompt_leaves_the_prompt_untouched():
    """Design §5: `model` is the cloud's choice, not the model's, and is not visible in the
    prompt. The prompt is rendered from the payload *before* the key lands."""
    case = _case("CALIBRATION")
    case.prompt = json.dumps(case.payload)
    models_mod.stamp([case], models_mod.parse(TABLE), "codex")
    assert "gpt-5.6-terra" not in case.prompt


# ------------------------------------------------- 5. an older runtime gets the same pin its way


def test_the_runtime_version_decides_who_reads_the_key():
    assert models_mod.runtime_version(types.SimpleNamespace(__version__="0.5.0")) == (0, 5, 0)
    assert models_mod.runtime_version("0.4.0+abc123") == (0, 4, 0)
    assert models_mod.runtime_version("") == (0,)
    assert models_mod.reads_the_job_key(types.SimpleNamespace(__version__="0.5.0"))
    assert models_mod.reads_the_job_key("0.6.1+sha")
    assert not models_mod.reads_the_job_key(types.SimpleNamespace(__version__="0.4.0"))
    assert not models_mod.reads_the_job_key(None)


def test_on_a_runtime_older_than_0_5_0_the_per_case_pin_lands_on_the_executor_instead():
    """keel-runtime 0.4.0's three executors read `self.model` when they build their argv and
    ignore the job key, so the same value is put there one case at a time. A 0.5.0 runtime is
    left alone: the key is the only source of truth."""
    table = models_mod.parse(TABLE)
    executor = types.SimpleNamespace(model="left-alone")
    reading, calibration = _case("READING"), _case("CALIBRATION")
    models_mod.stamp([reading, calibration], table, "codex")

    models_mod.apply_fallback(executor, reading, table, routing_runtime=False)
    assert executor.model == "gpt-5.5-mini"
    models_mod.apply_fallback(executor, calibration, table, routing_runtime=False)
    assert executor.model == "gpt-5.6-terra"

    executor.model = "left-alone"
    models_mod.apply_fallback(executor, reading, table, routing_runtime=True)
    assert executor.model == "left-alone"
    models_mod.apply_fallback(executor, reading, None, routing_runtime=False)
    assert executor.model == "left-alone", "no table: the single-model pin is not touched"


# ------------------------------------------------------------ 6. the verdict and the report say


def _args(host="codex", **kw):
    base = dict(host=host, baseline=False, n_runs=1, filter=None, no_judge=False, models=None)
    base.update(kw)
    return types.SimpleNamespace(**base)


class _Codexish:
    timeout_seconds = 300.0


def test_the_model_block_and_the_manifest_carry_the_per_class_pins_and_their_source(tmp_path):
    table = models_mod.parse(TABLE)
    facts = {"cli": "codex", "cli_version": "codex-cli 0.154.0"}
    block = run_mod._model_block(_args(), facts, _Codexish(), None, None, table=table)
    assert block["pinned_model"] is None
    assert block["models_used"] == {"context": "gpt-5.5-mini", "frame": "gpt-5.6-terra",
                                    "calibration": "gpt-5.6-terra",
                                    "respondent": "gpt-5.6-terra", "reading": "gpt-5.5-mini",
                                    "asked": "gpt-5.5-mini"}
    assert block["models_source"] == ""
    manifest = run_mod._manifest(_args(), facts, _Codexish(), None, None, "2026-09-13T00:00:00Z",
                                 table=table)
    assert manifest["model"]["per_class"] == block["models_used"]

    single = run_mod._model_block(_args(), facts, _Codexish(), "gpt-5.6-luna", None)
    assert single["pinned_model"] == "gpt-5.6-luna" and single["models_used"] is None, \
        "a single-model run's block is what every run of record so far carries, plus two nulls"
    old_manifest = run_mod._manifest(_args(), facts, _Codexish(), None, None, "t")
    assert old_manifest["model"] == {"pinned": None, "reported": None, "per_class": None,
                                     "table": None}


def test_the_report_names_the_per_class_pins_where_it_used_to_name_one_or_none(tmp_path):
    import copy                                                              # noqa: PLC0415
    from instructions import marks as marks_mod                              # noqa: PLC0415
    from tests.test_instruction_modules_import import _SCORECARD             # noqa: PLC0415

    scorecard = copy.deepcopy(_SCORECARD)
    scorecard["model"].update({"host": "codex", "cli": "codex", "cli_version": "codex-cli 0.154.0",
                               "pinned_model": None, "job_max_turns": None,
                               "job_budget_usd": None,
                               "models_used": {"calibration": "gpt-5.6-terra",
                                               "reading": None, "brief": "gpt-5.6-terra"},
                               "models_source": "exported:/x"})
    verdict = {"scenario": "instructions", "baseline": False, "host": "codex", "n_runs": 3,
               "cases": 48, "errored": 0, "duration_s": 1.0, "total_cost_usd": None,
               "total_premium_requests": None,
               "total_tokens": {"input_tokens": 1, "output_tokens": 1},
               "marks": marks_mod.judge(scorecard["totals"], marks_mod.load())}
    path = report_mod.render_report(tmp_path, verdict=verdict, scorecard=scorecard,
                                    versions={}, host="codex")
    html = path.read_text()
    assert "pinned per job class" in html
    assert "calibration <code>gpt-5.6-terra</code>" in html
    assert "reading <b>the CLI's default</b>" in html
    assert "exported:/x" in html
    assert "nothing pinned" not in html


def test_each_cases_envelope_records_the_model_the_wire_asked_for(tmp_path):
    case = _case("READING")
    models_mod.stamp([case], models_mod.parse(TABLE), "codex")
    answer = types.SimpleNamespace(outcome="COMPLETED", schema_valid=True, schema_error=None,
                                   recovery_pass=False, num_turns=1, total_cost_usd=None,
                                   premium_requests=None, reported_model=None, duration_s=0.1,
                                   error=None, result={}, questions=None, envelope={})
    report_mod.write_case(tmp_path, case, answer, {}, host="codex")
    written = json.loads((tmp_path / "cases" / case.bundle_path / "envelope.json").read_text())
    assert written["model_requested"] == "gpt-5.5-mini"


# ------------------------------------------------ 7. the exported contract's optional fourth file


def _export(directory, *, with_table):
    # Spec 029 FR-021: an export without `dimension-registry.json` is refused before any case is
    # built, so the export these two tests read carries the hand-sized registry slice.
    from tests import v9_fixtures as fx                                      # noqa: PLC0415
    fx.write_export(directory, routing=TABLE if with_table else None)


def test_an_export_without_the_fourth_file_reads_as_before_and_says_it_has_no_table(tmp_path):
    _export(tmp_path, with_table=False)
    exported = contract_mod.read(tmp_path)
    assert "COMPLETED" in exported.for_screen("INTERPRET")["allowed_outcomes"]
    assert exported.model_routing is None


def test_an_export_with_the_fourth_file_carries_the_clouds_table_whole(tmp_path):
    _export(tmp_path, with_table=True)
    exported = contract_mod.read(tmp_path)
    assert exported.model_routing == TABLE
    table = models_mod.select("exported", host="claude", exported=exported, environ={})
    assert table.resolve("claude", "reading") == "haiku"


# --------------------------------------------------------- 8. what a journey reads off a job dir


def test_a_jobs_model_facts_come_from_execution_json_then_the_envelope_and_else_are_none(tmp_path):
    job = tmp_path / "j1"
    job.mkdir()
    assert models_mod.job_model_facts(job)["source"] is None
    (job / "envelope.json").write_text(json.dumps({"model_requested": "haiku",
                                                   "model_used": "haiku"}))
    facts = models_mod.job_model_facts(job)
    assert (facts["model_requested"], facts["source"]) == ("haiku", "envelope.json")
    (job / "execution.json").write_text(json.dumps({"model_requested": "sonnet",
                                                    "model_used": "opus",
                                                    "retried_unpinned": True}))
    facts = models_mod.job_model_facts(job)
    assert facts == {"model_requested": "sonnet", "model_used": "opus", "retried_unpinned": True,
                     "source": "execution.json"}
    (job / "execution.json").write_text("{broken")
    assert models_mod.job_model_facts(job)["source"] == "envelope.json"


def test_an_envelope_without_the_keys_is_an_older_runtime_not_a_default_pin(tmp_path):
    job = tmp_path / "j2"
    job.mkdir()
    (job / "envelope.json").write_text(json.dumps({"is_error": False, "result": "..."}))
    assert models_mod.job_model_facts(job) == {"model_requested": None, "model_used": None,
                                               "retried_unpinned": None, "source": None}


def test_the_makefile_passes_models_to_both_targets():
    from stack.config import REPO_ROOT                                       # noqa: PLC0415
    text = (REPO_ROOT / "Makefile").read_text()
    assert text.count("$(if $(MODELS),--models $(MODELS),)") == 2


def test_executor_kwargs_follow_the_runtime_generation():
    from instructions import models
    assert models.executor_kwargs("codex", "gpt-6-astra", routing_runtime=True) == {}
    assert models.executor_kwargs("copilot", None, routing_runtime=True) == {}
    assert models.executor_kwargs("codex", "gpt-6-astra", routing_runtime=False) == {
        "codex_model": "gpt-6-astra", "copilot_model": None}
    assert models.executor_kwargs("copilot", "gpt-5-mini", routing_runtime=False) == {
        "copilot_model": "gpt-5-mini", "codex_model": None}


def test_ask_hands_the_jobs_model_to_a_routing_runtime_through_the_pollers_rule(tmp_path):
    """The one step production's poller does (spec 009) -- `InferenceRequest.model` from
    `request_payload["model"][host_key]` -- the eval does too, or a `--models` run is unpinned
    while its envelope says otherwise (found live on 2026-09-13, Copilot answered on the default).

    keel-cloud spec 047 / keel-runtime 0.6.0 add the second half of the pin on the same road, so
    the eval takes the effort from the poller's own `_effort_for` too. **Through the poller's
    functions, never a second copy of the rules**, and that matters more for the effort than for
    the model: the one thing this referee must never do is decide for itself how hard the subject
    thinks."""
    import sys
    from instructions import runner
    from stack.config import load_config                                      # noqa: PLC0415
    sys.path.insert(0, str(load_config(validate=False).keel_runtime))
    import keel_runtime.executor as executor_module
    import keel_runtime.poller as poller
    assert "model" in executor_module.InferenceRequest.__dataclass_fields__

    class Host:
        host_key = "codex"
    payload = {"model": {"codex": "gpt-6-astra", "copilot": "x"}}
    kwargs = runner._model_kwarg(executor_module, Host(), payload)
    assert kwargs["model"] == "gpt-6-astra"
    assert runner._model_kwarg(executor_module, Host(), {})["model"] is None
    assert poller._model_for(Host(), payload) == "gpt-6-astra"

    # The effort half, on a runtime new enough to have it. An older one simply has neither the
    # field nor the function and gets nothing for it, independently of the model.
    if "effort" in executor_module.InferenceRequest.__dataclass_fields__:
        class Claude:
            host_key = "claude"
        pinned = {"model": {"claude": "claude-sonnet-5-5"}, "effort": {"claude": "medium"}}
        assert runner._model_kwarg(executor_module, Claude(), pinned) == {
            "model": "claude-sonnet-5-5", "effort": "medium"}
        # A reading: the `light` row names a model and no effort, because `effort` errors on
        # Haiku 4.5. The payload carries no `effort` key at all and the runtime gets `None`.
        reading = {"model": {"claude": "claude-haiku-4-5-20251001"}}
        assert runner._model_kwarg(executor_module, Claude(), reading) == {
            "model": "claude-haiku-4-5-20251001", "effort": None}
        assert kwargs["effort"] is None, "codex has no efforts row and is handed no effort"


# ----------------------------------------------------------------- the pin's second half (v6)
#
# keel-cloud spec 047, table v6, run of record 20260930T024851Z-instructions: a certificate is a
# model AND an effort level. The table gains an `efforts` block of the same host x tier shape and
# the wire gains a seventh key `effort`; keel-runtime 0.6.0 turns it into `claude --effort <level>`.
#
# This is also how the eval stopped needing CLAUDE_CODE_EFFORT_LEVEL. That variable is process-wide:
# it reached the judge too, which is why `judge.judge_env()` strips it by name. The `effort` key is
# per job, travels the path a founder's job takes, and is recorded in the bundle -- so a run of
# record can now STATE the effort it was taken at instead of it being a fact about whoever typed
# the command.

V6 = {
    "version": 6,
    "hosts": {
        "claude": {"standard": "claude-sonnet-5-5", "light": "claude-haiku-4-5-20251001"},
        "codex": {"standard": "gpt-6-astra", "light": "gpt-5.4-mini"},
        "copilot": {"standard": "gpt-6-astra", "light": "gpt-5.4-mini"},
    },
    "efforts": {"claude": {"standard": "medium"}},
    "_tiers": ["light", "standard", "frontier"],
    "classes": {"context": "light", "frame": "standard", "calibration": "standard",
                "respondent": "standard", "reading": "light", "brief": "standard", "asked": "light"},
}


def test_v6_resolves_the_effort_at_the_classes_own_tier():
    table = models_mod.parse(V6, source="v6")

    assert table.resolve_effort("claude", "calibration") == "medium"
    assert table.resolve_effort("claude", "brief") == "medium"
    assert table.resolve_effort("claude", "frame") == "medium"
    # The reading is the one that matters: it routes to `light`, whose row carries no effort,
    # because `effort` ERRORS on Haiku 4.5. Nothing has to say so -- the shape says it.
    assert table.resolve_effort("claude", "reading") is None
    # And the other two hosts have no `efforts` row at all, because neither CLI has an effort flag.
    assert table.resolve_effort("codex", "calibration") is None
    assert table.resolve_effort("copilot", "brief") is None


def test_v6_efforts_used_is_the_per_class_record_a_verdict_carries():
    table = models_mod.parse(V6, source="v6")

    # Six classes at v9 (spec 029 FR-023): `context` and `reading` route to `light`, whose row
    # carries no effort -- `effort` errors on Haiku 4.5.
    assert table.efforts_used("claude") == {
        "context": None, "frame": "medium", "calibration": "medium", "respondent": "medium",
        "reading": None, "asked": None}
    assert table.efforts_used("codex") == {"context": None, "frame": None, "calibration": None, "respondent": None, "reading": None, "asked": None}


def test_a_table_older_than_v6_pins_no_effort_anywhere():
    """Absent means "the CLI's own default", never "fail" -- design §4's rule for `hosts`, applied
    to the second half of a pin. Every pre-v6 table still loads and every payload it stamps is
    byte-identical to what it stamped before."""
    without = {k: v for k, v in V6.items() if k != "efforts"}
    table = models_mod.parse(without, source="v5")

    assert table.efforts == {}
    assert table.resolve_effort("claude", "calibration") is None
    assert table.efforts_used("claude") == {"context": None, "frame": None, "calibration": None, "respondent": None, "reading": None, "asked": None}


def test_stamp_writes_the_seventh_key_and_leaves_a_reading_untouched():
    table = models_mod.parse(V6, source="v6")
    cases = [_case("CALIBRATION"), _case("READING"), _case("FRAME")]
    models_mod.stamp(cases, table, "claude")

    calibration, reading, brief = cases                 # `brief`: a standard-tier frame since spec 052
    assert calibration.payload["model"] == {"claude": "claude-sonnet-5-5"}
    assert calibration.payload["effort"] == {"claude": "medium"}
    assert calibration.effort == "medium"
    assert brief.payload["effort"] == {"claude": "medium"}
    # The reading: a model, and no `effort` key at all.
    assert reading.payload["model"] == {"claude": "claude-haiku-4-5-20251001"}
    assert "effort" not in reading.payload
    assert reading.effort is None
    # The key order the cloud writes: the five, then model, then effort.
    assert list(calibration.payload)[-2:] == ["model", "effort"]


def test_stamp_on_a_host_with_no_efforts_row_writes_no_seventh_key():
    table = models_mod.parse(V6, source="v6")
    cases = [_case("CALIBRATION")]
    models_mod.stamp(cases, table, "codex")

    assert cases[0].payload["model"] == {"codex": "gpt-6-astra"}
    assert "effort" not in cases[0].payload
    assert cases[0].effort is None


def test_stamp_clears_a_stale_effort_the_way_it_clears_a_stale_model():
    table = models_mod.parse({k: v for k, v in V6.items() if k != "efforts"}, source="v5")
    case = _case("CALIBRATION")
    case.payload["effort"] = {"claude": "xhigh"}
    case.effort = "xhigh"
    models_mod.stamp([case], table, "claude")

    assert "effort" not in case.payload
    assert case.effort is None


def test_an_effort_outside_the_cli_ladder_refuses_to_start():
    bad = dict(V6, efforts={"claude": {"standard": "ultra"}})
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.parse(bad, source="bad")
    assert "ultra" in str(refusal.value)
    assert "low, medium, high, xhigh, max" in str(refusal.value)


def test_an_effort_on_an_unknown_tier_refuses_to_start():
    bad = dict(V6, efforts={"claude": {"premium": "medium"}})
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.parse(bad, source="bad")
    assert "premium" in str(refusal.value)


def test_an_effort_for_a_host_with_no_models_row_refuses_to_start():
    """The one refusal `hosts` cannot give, and keel-cloud's `ModelRouting` gives it too: an effort
    with no model beside it pins how hard to think about a model nobody named."""
    bad = dict(V6, hosts={"claude": V6["hosts"]["claude"]},
               efforts={"codex": {"standard": "medium"}})
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.parse(bad, source="bad")
    assert "codex" in str(refusal.value)


def test_an_efforts_block_that_is_not_an_object_refuses_to_start():
    for value in ("medium", ["medium"], 7):
        with pytest.raises(models_mod.ModelsUnavailable):
            models_mod.parse(dict(V6, efforts=value), source="bad")


# ------------------------------------------------- spec 029 FR-023: the six classes of MARKS_VERSION 9

#: keel-cloud's own `model-routing.json` at v8 (`3e91cfc`), the table the export carries today.
V8_TABLE = {
    "version": 8,
    "hosts": {"claude": {"light": "claude-haiku-4-5-20251001", "standard": "claude-sonnet-5-5"}},
    "efforts": {"claude": {"standard": "medium"}},
    "_tiers": ["light", "standard", "frontier"],
    "classes": {"frame": "standard", "assumptions": "standard", "reframe": "standard",
                "reading": "light", "brief": "standard", "questions": "light"},
}


def test_a_table_naming_the_six_measured_classes_parses():
    table = models_mod.parse(TABLE)
    assert models_mod.MEASURED_CLASSES == ("context", "frame", "calibration", "respondent",
                                           "reading", "asked")
    assert "brief" in models_mod.DORMANT_CLASSES, "THEMES routes through it; no case measures it (spec 052)"
    assert table.resolve_kind("claude", "ASKED") == "haiku"
    assert table.resolve_screen("claude", "ASKED") == "haiku"
    assert models_mod.KIND_TO_CLASS["ASKED"] == models_mod.SCREEN_TO_CLASS["ASKED"] == "asked"
    assert table.resolve_kind("claude", "CONTEXT") == "haiku"
    assert table.resolve_kind("claude", "RESPONDENT") == "sonnet"
    assert table.resolve_screen("claude", "CALIBRATION_QUESTIONS") == "sonnet"


def test_keel_clouds_v8_table_refuses_naming_the_three_new_classes_and_its_version():
    """Research R5: the three dormant names parse, so the refusal is the *right* one -- the table
    says nothing about `context`, `calibration` or `respondent` -- and it names table version 8.
    Found by reading `parse` and keel-cloud's table, not by a failed run (025 D13 the other way)."""
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.parse(V8_TABLE, source="exported")
    words = str(refusal.value)
    for name in ("context", "calibration", "respondent", "asked", "version 8"):
        assert name in words, name
    assert "assumptions" not in words.split("--")[0], "the dormant names are tolerated"


def test_the_v9_screen_pin_file_is_refused_naming_asked():
    """Call 84: spec 029's pin names six classes; v18 measures seven, so it is refused -- by the missing `asked`,
    never silently defaulted."""
    from pathlib import Path                                                 # noqa: PLC0415
    path = (Path(__file__).resolve().parent.parent / "specs" / "029-marks-v9-vectors"
            / "contracts" / "models-screen.json")
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.load(path)
    assert "says nothing about asked" in str(refusal.value)


def test_keel_clouds_v11_table_routes_asked_to_light():
    """keel-cloud 088's table v11 (`asked: light`): Haiku on Claude, luna on Codex / Copilot."""
    v11 = {"version": 11, "_tiers": ["light", "standard", "frontier"],
           "hosts": {"claude": {"light": "claude-haiku-4-5-20251001", "standard": "claude-sonnet-5-5"},
                     "codex": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"}},
           "efforts": {"claude": {"standard": "medium"}},
           "classes": {"frame": "standard", "reading": "light", "brief": "standard", "context": "light",
                       "calibration": "standard", "respondent": "standard", "asked": "light"}}
    table = models_mod.parse(v11, source="exported")
    assert table.resolve("claude", "asked") == "claude-haiku-4-5-20251001"
    assert table.resolve("codex", "asked") == "gpt-5.6-luna"
    assert table.resolve_effort("claude", "asked") is None, "the light row carries no effort"


def test_a_table_naming_an_unknown_class_still_refuses_by_name():
    with pytest.raises(models_mod.ModelsUnavailable) as refusal:
        models_mod.parse(dict(TABLE, classes={**TABLE["classes"], "questionnaire": "light"}))

    assert "questionnaire" in str(refusal.value) and "classes are exactly" in str(refusal.value)


def test_models_used_and_efforts_used_report_exactly_the_six():
    table = models_mod.parse(TABLE)
    six = ["context", "frame", "calibration", "respondent", "reading", "asked"]
    assert list(table.models_used("claude")) == six
    assert list(table.efforts_used("claude")) == six


def test_the_wire_pins_a_context_case_on_the_light_row_and_writes_it_no_effort():
    table = models_mod.parse(V6, source="v6")
    case = _case("CONTEXT", case_id="e/CONTEXT_INTERPRET/run1")
    models_mod.stamp([case], table, "claude")
    assert case.payload[models_mod.MODEL_KEY] == {"claude": "claude-haiku-4-5-20251001"}
    assert models_mod.EFFORT_KEY not in case.payload
    assert case.effort is None


def test_a_compare_row_is_never_stamped():
    table = models_mod.parse(V6, source="v6")
    case = _case("COMPARE", case_id="e/COMPARE")
    models_mod.stamp([case], table, "claude")
    assert models_mod.MODEL_KEY not in case.payload and case.model is None


def test_classes_carry_every_class_the_live_routing_table_names():
    """Spec 091 FR-3a: keel-cloud's own `model-routing.json` (v13 carries `example_match`) parses here, and every class
    it names is one of `CLASSES` -- so the next class the cloud adds fails `make unit`, not a journey (s012 refused v13
    by the name *example_match* on 2026-10-30). `example_match` is the cloud's last class (`JobClass`), and `CLASSES`
    ends on it."""
    from stack.config import load_config                                    # noqa: PLC0415
    path = load_config(validate=False).keel_cloud / models_mod.CLOUD_RESOURCE
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {path.parent}")
    document = json.loads(path.read_text(encoding="utf-8"))
    unknown = [c for c in document["classes"] if c not in models_mod.CLASSES]
    assert not unknown, f"model-routing.json v{document.get('version')} names {unknown}; add them to CLASSES"
    models_mod.parse(document)
    assert models_mod.CLASSES[-1] == "example_match" and "example_match" in models_mod.DORMANT_CLASSES
    assert "example_match" not in models_mod.REPORTED_CLASSES, "no case measures it"


def test_the_validators_message_names_example_match():
    """Spec 091 FR-3a: the refusal of an unknown class lists the classes, `example_match` last."""
    table = json.loads(json.dumps(TABLE))
    table["classes"]["gallery"] = "light"
    with pytest.raises(models_mod.ModelsUnavailable, match=r"classes names 'gallery'; the classes are exactly "
                                                             r"context, frame, .*brief, example_match$"):
        models_mod.parse(table)
