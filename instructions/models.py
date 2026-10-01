"""The model-routing table, read the way keel-cloud writes it, and pinned the way the cloud pins.

keel-cloud `canon/designs/model-routing-design.md` (2026-09-12, amended 2026-09-13): the cloud
keeps one table -- host × job class, three tiers -- and puts a per-host `model` map on every
inference job as the **sixth key** of `request_payload`. The runtime reads the entry for its own
host and passes it to its CLI; no entry, no flag. There is **no founder's pin** and no environment
knob (§6): the `KEEL_<HOST>_MODEL` variables of keel-runtime 0.4.0 go in 0.5.0.

This eval is the table's certifier (§7), so it pins a candidate **through the same key** the cloud
will send -- `case.payload["model"] = {<host>: <model>}` -- and never through the environment. A
run judged this way is the run the table actually claims: `standard` on the assumption and brief
cases, `light` on the readings, through the path a founder's job takes.

**Since keel-cloud spec 047 (table v6, 2026-09-30) a pin has two halves**, and this module reads
both. The table gains an optional `efforts` block of the same `host x tier` shape, and the wire
gains a seventh key `effort` beside `model`; keel-runtime 0.6.0 turns it into `claude --effort
<level>`. A certificate is a model AND an effort level: run `20260930T024851Z-instructions`
certified `claude-sonnet-5-5` *at effort `medium`*, and the Claude Code CLI's own default is
`xhigh` -- 3.7x the thinking and 2.4x the wall clock, for marks `medium` already holds.

**And this is why the eval never wanted `CLAUDE_CODE_EFFORT_LEVEL`.** Until v6 the only way to run
a subject at an effort was to export that variable, which is process-wide: it reached the judge too,
and `judge.judge_env()` had to strip it by name so a run could not score itself at its own setting.
The `effort` key is per job, travels the path a founder's job takes, and is recorded in the bundle
-- so a run of record can now *state* the effort it was taken at instead of it being a fact about
whoever typed the command.

The file is the design's §4 shape, read whole and never copied:

    {"version": 1,
     "hosts":   {"codex": {"standard": "gpt-5.6-terra", "light": "gpt-5.5-mini"}, ...},
     "_tiers":  ["light", "standard", "frontier"],            # informational, tolerated
     "classes": {"frame": "standard", "assumptions": "standard", "reframe": "standard",
                 "reading": "light", "brief": "standard"}}

A host with no row, or a row with no entry for a class's tier, is **no pin** -- the CLI's default,
recorded as `None` -- never a failure: the table ships empty and fills one run of record at a time.
An unknown class name, an unknown tier name, or a malformed file is a refusal to start, because a
typo that quietly defaulted would mis-measure the very thing this run exists to certify.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

#: The wire's sixth key (design §5).
MODEL_KEY = "model"

#: The wire's seventh key (design §5, keel-cloud spec 047). Written beside `model` and only when
#: the table pins one; absent means the CLI's own default, exactly as for `model`.
EFFORT_KEY = "effort"

#: The ladder an `efforts` value must name -- Claude Code 2.1.284's own `--effort` vocabulary
#: (`keel-runtime/tests/fixtures/claude/effort-help.txt`), which is also the API's
#: `output_config.effort` ladder and keel-cloud's `ModelRouting.EFFORT_LADDER`.
EFFORTS = ("low", "medium", "high", "xhigh", "max")

#: The ladder (design §3): light → standard → frontier. Exactly these three, in this order.
TIERS = ("light", "standard", "frontier")

#: The **six** job classes the cloud's `InferenceScreen.jobClass()` names (design §3). `questions`
#: joined at keel-cloud spec 048 FR-009, on the `light` tier, and **this list is why it had to**:
#: `parse` below raises `ModelsUnavailable` on a class name it does not know, so `MODELS=exported`
#: would have refused to start against the cloud's own table the moment it named one (spec 025
#: FR-012). Found by reading the table, not by a failed run.
CLASSES = ("frame", "assumptions", "reframe", "reading", "brief", "questions")

#: The **four** this eval measures, by the `Case.kind` it already sorts the corpus into.
KIND_TO_CLASS = {"ASSUMPTIONS": "assumptions", "READING": "reading", "BRIEF": "brief",
                 "QUESTIONS": "questions"}

#: Every screen's class, for a journey (S-012) that sees screens rather than kinds.
SCREEN_TO_CLASS = {
    "PROBLEM_FRAME": "frame", "SOLUTION_FRAME": "frame", "COMMERCIAL_FRAME": "frame",
    "PROBLEM_ASSUMPTIONS": "assumptions", "SOLUTION_ASSUMPTIONS": "assumptions",
    "COMMERCIAL_ASSUMPTIONS": "assumptions",
    "SOLUTION_REFRAME": "reframe", "COMMERCIAL_REFRAME": "reframe",
    "INTERPRET": "reading", "BRIEF": "brief", "QUESTIONS": "questions",
}

#: The classes a verdict reports, in the order a run runs them. `questions` joins here too, so the
#: verdict says which model wrote the questionnaires rather than leaving a fourth subject unnamed.
REPORTED_CLASSES = ("assumptions", "questions", "reading", "brief")

#: keel-runtime 0.4.0's per-host pin variables (design §2). Refused beside `--models`: a run that
#: pinned two ways would not know which one answered. Gone from the runtime at 0.5.0.
LEGACY_PIN_ENV = {"claude": "KEEL_CLAUDE_MODEL", "copilot": "KEEL_COPILOT_MODEL",
                  "codex": "KEEL_CODEX_MODEL"}

#: The first keel-runtime that reads `request_payload["model"]` (design §10 step 2).
ROUTING_RUNTIME = (0, 5, 0)

#: Where the table lives in a keel-cloud checkout (design §4), for a scenario that has the
#: checkout and not the exporter's output.
CLOUD_RESOURCE = Path("src") / "main" / "resources" / "keel" / "model-routing.json"

#: What the exporter writes beside the three contract files (the optional fourth).
EXPORTED_NAME = "model-routing.json"


class ModelsUnavailable(RuntimeError):
    """The table could not be read as the design describes it -- a reason to stop, never a score."""


@dataclass(frozen=True)
class ModelTable:
    """One routing table, validated. `source` says where it came from, for the bundle."""

    hosts: dict
    classes: dict
    version: object = None
    source: str = ""
    tiers: tuple = field(default=TIERS)
    #: The `efforts` block, `{host: {tier: effort}}` -- empty for a table older than v6, which
    #: means "no effort anywhere" and therefore every CLI's own default, exactly as an absent
    #: `hosts` row means the CLI's own model.
    efforts: dict = field(default_factory=dict)

    def tier_for(self, job_class: str) -> str | None:
        return self.classes.get(job_class)

    def resolve(self, host: str, job_class: str) -> str | None:
        """The model this host pins for this class, or `None` -- the CLI's default."""
        tier = self.tier_for(job_class)
        if tier is None:
            return None
        return (self.hosts.get(host) or {}).get(tier)

    def resolve_kind(self, host: str, kind: str) -> str | None:
        return self.resolve(host, KIND_TO_CLASS[kind])

    def resolve_screen(self, host: str, screen: str) -> str | None:
        job_class = SCREEN_TO_CLASS.get(screen)
        return None if job_class is None else self.resolve(host, job_class)

    def job_map(self, host: str, kind: str) -> dict | None:
        """The wire's `model` value for one case -- `{host: model}` -- or `None` for no key."""
        model = self.resolve_kind(host, kind)
        return None if model is None else {host: model}

    def resolve_effort(self, host: str, job_class: str) -> str | None:
        """The effort this host pins for this class, or `None` -- the CLI's own default.

        Looked up at the class's own tier and no other, which is what keeps a reading clean: the
        `reading` class routes to `light`, keel-cloud's `light` row carries no effort, and `effort`
        errors on Haiku 4.5.
        """
        tier = self.tier_for(job_class)
        if tier is None:
            return None
        return (self.efforts.get(host) or {}).get(tier)

    def resolve_effort_kind(self, host: str, kind: str) -> str | None:
        return self.resolve_effort(host, KIND_TO_CLASS[kind])

    def resolve_effort_screen(self, host: str, screen: str) -> str | None:
        job_class = SCREEN_TO_CLASS.get(screen)
        return None if job_class is None else self.resolve_effort(host, job_class)

    def effort_job_map(self, host: str, kind: str) -> dict | None:
        """The wire's `effort` value for one case -- `{host: effort}` -- or `None` for no key."""
        effort = self.resolve_effort_kind(host, kind)
        return None if effort is None else {host: effort}

    def efforts_used(self, host: str) -> dict:
        """The per-class record a verdict carries beside `models_used`, `None` where this host runs
        the class at its CLI's own default. `questions` routes to `light`, whose row carries no
        effort -- for the same reason a reading's does not."""
        return {job_class: self.resolve_effort(host, job_class)
                for job_class in REPORTED_CLASSES}

    def models_used(self, host: str) -> dict:
        """The per-class record a verdict carries: `{assumptions, questions, reading, brief}`,
        `None` where this host runs the class on its CLI's default."""
        return {job_class: self.resolve(host, job_class)
                for job_class in REPORTED_CLASSES}

    def names_for(self, host: str) -> set:
        """Every model this host's row names, any tier -- what a journey may see requested."""
        return {model for model in (self.hosts.get(host) or {}).values() if model}


def parse(document: object, *, source: str = "") -> ModelTable:
    """The design's §4 shape, or a refusal naming what is wrong with it."""
    if not isinstance(document, dict):
        raise ModelsUnavailable(f"{source or 'the model table'} is not a JSON object")
    hosts = document.get("hosts")
    classes = document.get("classes")
    if not isinstance(hosts, dict) or not isinstance(classes, dict):
        raise ModelsUnavailable(
            f"{source or 'the model table'} must carry `hosts` and `classes` objects "
            "(keel-cloud model-routing-design.md §4)")
    for host, row in hosts.items():
        if not isinstance(row, dict):
            raise ModelsUnavailable(f"hosts.{host} is not an object of tier -> model")
        for tier, model in row.items():
            if tier not in TIERS:
                raise ModelsUnavailable(
                    f"hosts.{host} names tier {tier!r}; the ladder is exactly "
                    f"{', '.join(TIERS)}")
            if not isinstance(model, str) or not model:
                raise ModelsUnavailable(f"hosts.{host}.{tier} must be a model name")
    for job_class, tier in classes.items():
        if job_class not in CLASSES:
            raise ModelsUnavailable(
                f"classes names {job_class!r}; the classes are exactly {', '.join(CLASSES)}")
        if tier not in TIERS:
            raise ModelsUnavailable(
                f"classes.{job_class} names tier {tier!r}; the ladder is exactly "
                f"{', '.join(TIERS)}")
    missing = [c for c in KIND_TO_CLASS.values() if c not in classes]
    if missing:
        raise ModelsUnavailable(
            f"classes says nothing about {', '.join(missing)} -- every class this eval measures "
            "must name its tier, so that a missing one is never a silent default")
    efforts = document.get("efforts")
    if efforts is None:
        efforts = {}
    elif not isinstance(efforts, dict):
        raise ModelsUnavailable(
            f"{source or 'the model table'}: `efforts` must be an object of host -> tier -> "
            "effort (keel-cloud model-routing-design.md §4, v6)")
    else:
        for host, row in efforts.items():
            if not isinstance(row, dict):
                raise ModelsUnavailable(f"efforts.{host} is not an object of tier -> effort")
            if host not in hosts:
                # keel-cloud refuses this at startup and so does this reader: an effort with no
                # model beside it pins how hard to think about a model nobody named.
                raise ModelsUnavailable(
                    f"efforts.{host} has no `hosts` row -- an effort with no model beside it "
                    "pins how hard to think about a model nobody named")
            for tier, effort in row.items():
                if tier not in TIERS:
                    raise ModelsUnavailable(
                        f"efforts.{host} names tier {tier!r}; the ladder is exactly "
                        f"{', '.join(TIERS)}")
                if effort not in EFFORTS:
                    raise ModelsUnavailable(
                        f"efforts.{host}.{tier} is {effort!r}; the CLI's ladder is exactly "
                        f"{', '.join(EFFORTS)}")
    tiers = document.get("_tiers")
    if tiers is not None and tuple(tiers) != TIERS:
        raise ModelsUnavailable(
            f"_tiers is {tiers!r}; the ladder is exactly {list(TIERS)} (design §3)")
    return ModelTable(hosts={h: dict(r) for h, r in hosts.items()}, classes=dict(classes),
                      version=document.get("version"), source=source,
                      efforts={h: dict(r) for h, r in efforts.items()})


def load(path: Path) -> ModelTable:
    path = Path(path)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ModelsUnavailable(f"could not read the model table at {path}: {exc}") from exc
    except ValueError as exc:
        raise ModelsUnavailable(f"{path} is not JSON: {exc}") from exc
    return parse(document, source=str(path))


def from_keel_cloud(keel_cloud: Path) -> ModelTable | None:
    """The checkout's own resource, or `None` while keel-cloud has no table yet (design §10 step
    1 not landed). Read from the source of truth, not copied; a scenario that has the checkout
    already reads the corpus the same way."""
    path = Path(keel_cloud) / CLOUD_RESOURCE
    if not path.is_file():
        return None
    return load(path)


def select(spec: str | None, *, host: str, exported=None, environ=None) -> ModelTable | None:
    """What `--models` asked for: nothing, a file, or `exported` -- the table keel-cloud's own
    exporter wrote beside the contracts, so a run of record can be "the cloud's own table".

    Refuses when a legacy `KEEL_<HOST>_MODEL` is also set: two pins, and no way to say which one
    answered.
    """
    if spec is None:
        return None
    environ = {} if environ is None else environ
    doubled = [name for name in LEGACY_PIN_ENV.values() if environ.get(name)]
    if doubled:
        raise ModelsUnavailable(
            f"--models and {', '.join(doubled)} were both given; a run pins one way. "
            "Unset the variable -- keel-runtime 0.5.0 no longer reads it (design §6)")
    if spec == "exported":
        if exported is None:
            raise ModelsUnavailable("--models exported needs keel-cloud's exported contract")
        table = getattr(exported, "model_routing", None)
        if table is None:
            raise ModelsUnavailable(
                f"keel-cloud's exporter wrote no {EXPORTED_NAME} beside the contracts -- "
                "`--models exported` measures the cloud's own table and there is none on this "
                "checkout (design §10 step 1)")
        return parse(table, source=f"exported:{exported.directory}")
    return load(Path(spec))


def stamp(cases, table: ModelTable | None, host: str) -> None:
    """Puts the wire's sixth and seventh keys on every case the table pins, **after** the prompt is
    rendered: they are the cloud's choice, not the model's, and never appear in the prompt (design
    §5). The payload order stays the cloud's -- the five keys `buildRequestPayload` writes, then
    `model`, then `effort`.

    `effort` is written only when the table pins one for that case's class, which since v6 means
    the Sonnet-tier classes on `claude` and nothing else: a reading routes to `light`, whose row
    carries no effort, because `effort` errors on Haiku 4.5. So a reading's payload is byte-
    identical to the one this function wrote before v6, and so is every Codex and Copilot case's.
    """
    for case in cases:
        case.model = None
        case.effort = None
        case.payload.pop(MODEL_KEY, None)
        case.payload.pop(EFFORT_KEY, None)
        if table is None:
            continue
        job_map = table.job_map(host, case.kind)
        if job_map is not None:
            case.payload[MODEL_KEY] = job_map
            case.model = job_map[host]
        effort_map = table.effort_job_map(host, case.kind)
        if effort_map is not None:
            case.payload[EFFORT_KEY] = effort_map
            case.effort = effort_map[host]


def runtime_version(module) -> tuple:
    """`keel_runtime.__version__` (or a `RUNTIME_VERSION` stamp such as `0.1.0+<sha>`) as a
    comparable tuple; `(0,)` when nothing is stated."""
    text = module if isinstance(module, str) else getattr(module, "__version__", "") or ""
    match = re.match(r"\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", text)
    if not match:
        return (0,)
    return tuple(int(part or 0) for part in match.groups())


def reads_the_job_key(module) -> bool:
    """Whether this keel-runtime takes its model from `request_payload["model"]` (0.5.0 and
    later) rather than from a constructor pin."""
    return runtime_version(module) >= ROUTING_RUNTIME


def apply_fallback(executor, case, table: ModelTable | None, *, routing_runtime: bool) -> None:
    """keel-runtime older than 0.5.0 ignores the job's `model` key; its three executors read
    `self.model` when they build their argv. So, on such a runtime only, the per-case pin is put
    there -- the same value the key carries, one case at a time, so the per-class run still
    measures what it claims. A 0.5.0 runtime is left alone: the key is the only source of truth."""
    if table is None or routing_runtime:
        return
    executor.model = case.model


#: Where keel-runtime 0.5.0 says what it requested and what answered (design §6): a job's own
#: `execution.json` when it writes one, else the same keys on its `envelope.json`.
JOB_MODEL_KEYS = ("model_requested", "model_used", "retried_unpinned")


def job_model_facts(job_dir: Path) -> dict:
    """`{model_requested, model_used, retried_unpinned, source}` for one runtime job directory,
    every value `None` (and `source` `None`) when the runtime wrote neither -- an older runtime,
    or a job that never got that far. Read, never inferred."""
    job_dir = Path(job_dir)
    for name in ("execution.json", "envelope.json"):
        path = job_dir / name
        if not path.is_file():
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(document, dict) and any(key in document for key in JOB_MODEL_KEYS):
            return {**{key: document.get(key) for key in JOB_MODEL_KEYS}, "source": name}
    return {**{key: None for key in JOB_MODEL_KEYS}, "source": None}


def describe(table: ModelTable | None, host: str) -> str:
    if table is None:
        return "nothing"
    used = table.models_used(host)
    return " · ".join(f"{job_class}={model or 'default'}" for job_class, model in used.items())


def executor_kwargs(host: str, pinned_model, routing_runtime: bool) -> dict:
    """The model keyword `get_executor` is given, by runtime generation.

    keel-runtime 0.5.0 (spec 009) dropped `copilot_model`/`codex_model` from `get_executor`: the
    model is the job's, read from `request_payload["model"]`, so a routing runtime gets no model
    keyword at all -- and a `KEEL_<HOST>_MODEL` pin would be silently ignored there, which the
    caller refuses before reaching here. An older runtime keeps the 0.4.0 shape."""
    if routing_runtime:
        return {}
    if host == "codex":
        return {"codex_model": pinned_model, "copilot_model": None}
    return {"copilot_model": pinned_model, "codex_model": None}
