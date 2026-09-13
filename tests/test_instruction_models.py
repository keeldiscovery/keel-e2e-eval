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
    "classes": {"frame": "standard", "assumptions": "standard", "reframe": "standard",
                "reading": "light", "brief": "standard"},
}


def _case(kind, case_id="e/PROBLEM/run1"):
    screen = {"ASSUMPTIONS": "PROBLEM_ASSUMPTIONS", "READING": "INTERPRET", "BRIEF": "BRIEF"}[kind]
    return prompts_mod.Case(case_id=case_id, kind=kind, entry_id="e", screen=screen,
                            subject="PROBLEM", run_index=1,
                            payload=prompts_mod.payload_for("I", {"k": None}, {"allowed_outcomes": ["COMPLETED"]}))


# ------------------------------------------------------------------ 1. class -> tier -> model


def test_the_resolver_walks_class_to_tier_to_the_hosts_row():
    table = models_mod.parse(TABLE)
    assert table.resolve("codex", "assumptions") == "gpt-5.6-terra"
    assert table.resolve("codex", "reading") == "gpt-5.5-mini"
    assert table.resolve("codex", "brief") == "gpt-5.6-terra"
    assert table.resolve_kind("claude", "READING") == "haiku"
    assert table.resolve_screen("claude", "SOLUTION_REFRAME") == "sonnet"


def test_a_missing_host_is_no_pin_never_a_failure():
    table = models_mod.parse(TABLE)
    assert table.resolve("gemini", "assumptions") is None
    assert table.job_map("gemini", "ASSUMPTIONS") is None
    assert table.models_used("gemini") == {"assumptions": None, "reading": None, "brief": None}


def test_a_missing_tier_on_a_hosts_row_is_the_clis_default_for_that_class():
    """Copilot's row names `standard` only, so its readings run unpinned and the record says so."""
    table = models_mod.parse(TABLE)
    assert table.resolve("copilot", "reading") is None
    assert table.models_used("copilot") == {"assumptions": "gpt-5.6-luna", "reading": None,
                                            "brief": "gpt-5.6-luna"}


def test_the_empty_table_the_cloud_ships_first_pins_nothing_anywhere():
    table = models_mod.parse({"version": 1, "hosts": {}, "classes": TABLE["classes"]})
    for host in ("claude", "copilot", "codex"):
        assert table.models_used(host) == {"assumptions": None, "reading": None, "brief": None}


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
                "classes": {**TABLE["classes"], "assumptions": "frontier"}}
    table = models_mod.parse(document)
    assert table.resolve("codex", "assumptions") == "c"
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
    assert run_mod.main(["--host", "codex", "--models", str(bad)]) == 2
    assert "ladder is exactly" in capsys.readouterr().err


# ------------------------------------------------------------- 4. the pin is the wire's own key


def test_the_pin_is_the_sixth_key_of_the_payload_and_never_the_environment(monkeypatch):
    monkeypatch.delenv("KEEL_CODEX_MODEL", raising=False)
    table = models_mod.parse(TABLE)
    cases = [_case("ASSUMPTIONS"), _case("READING", "e/Tom/run1"), _case("BRIEF", "e/BRIEF/run1")]
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
    assumptions = _case("ASSUMPTIONS")
    models_mod.stamp([assumptions], None, "copilot")
    assert "model" not in assumptions.payload, "no table: the payload is exactly what it was"


def test_stamping_after_the_prompt_leaves_the_prompt_untouched():
    """Design §5: `model` is the cloud's choice, not the model's, and is not visible in the
    prompt. The prompt is rendered from the payload *before* the key lands."""
    case = _case("ASSUMPTIONS")
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
    reading, assumptions = _case("READING"), _case("ASSUMPTIONS")
    models_mod.stamp([reading, assumptions], table, "codex")

    models_mod.apply_fallback(executor, reading, table, routing_runtime=False)
    assert executor.model == "gpt-5.5-mini"
    models_mod.apply_fallback(executor, assumptions, table, routing_runtime=False)
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
    assert block["models_used"] == {"assumptions": "gpt-5.6-terra", "reading": "gpt-5.5-mini",
                                    "brief": "gpt-5.6-terra"}
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
                               "models_used": {"assumptions": "gpt-5.6-terra",
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
    assert "assumptions <code>gpt-5.6-terra</code>" in html
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
    (directory / "contracts").mkdir(parents=True)
    (directory / "manifest.json").write_text(json.dumps({"screens": ["INTERPRET"]}))
    (directory / "context-keys.json").write_text(json.dumps({"INTERPRET": ["anchors"]}))
    (directory / "contracts" / "INTERPRET.json").write_text(json.dumps(
        {"allowed_outcomes": ["COMPLETED"], "completed_result_schema": {}}))
    if with_table:
        (directory / "model-routing.json").write_text(json.dumps(TABLE))


def test_an_export_without_the_fourth_file_reads_as_before_and_says_it_has_no_table(tmp_path):
    _export(tmp_path, with_table=False)
    exported = contract_mod.read(tmp_path)
    assert exported.for_screen("INTERPRET")["allowed_outcomes"] == ["COMPLETED"]
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
    while its envelope says otherwise (found live on 2026-09-13, Copilot answered on the default)."""
    import sys
    from instructions import runner
    sys.path.insert(0, str((__import__("pathlib").Path(__file__).resolve().parents[2] / "keel-runtime")))
    import keel_runtime.executor as executor_module
    import keel_runtime.poller as poller
    assert "model" in executor_module.InferenceRequest.__dataclass_fields__

    class Host:
        host_key = "codex"
    payload = {"model": {"codex": "gpt-6-astra", "copilot": "x"}}
    assert runner._model_kwarg(executor_module, Host(), payload) == {"model": "gpt-6-astra"}
    assert runner._model_kwarg(executor_module, Host(), {}) == {"model": None}
    assert poller._model_for(Host(), payload) == "gpt-6-astra"
