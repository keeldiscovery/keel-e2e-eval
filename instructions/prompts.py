"""The prompt, built by keel-runtime rather than written here (spec 009 FR-004, spec 014 FR-004).

`request_payload` is `InferenceJobService.buildRequestPayload`'s shape, including the
empty-content sentinel an auto screen carries -- `InferenceOrchestrator.start` passes `""` for a
screen with nothing founder-typed, and that empty string is what reaches the prompt's
`founder_text:` line. The rendering itself is `keel_runtime.executor.build_prompt`, imported and
never copied: the nonce fence, the `SOURCE MATERIAL` heading and the `TASK`/`CONTRACT` ordering
are the runtime's to define, and a copy of them here would be a second prompt to keep in step.

**Two hosts, one body, two renderings** (keel-cloud `canon/designs/keel-skill-design.md` §5.4,
C-8). The body is shared and must be: *"a comparison whose sides were sent different prompts
measures nothing"*. But Claude Code receives the fixed `SYSTEM_PROMPT` as `--system-prompt` and
the envelope schema as `--json-schema`, and **Copilot's CLI has neither flag**, so on that host
both move into the text above the fence. That difference is the runtime's own
`_render_copilot_prompt`, and it is called here rather than reproduced -- so `DRY=1 HOST=copilot`
prints what Copilot is actually sent, and `cases/**/prompt.txt` in a Copilot bundle is what
Copilot was actually sent.

A keel-runtime that no longer offers those renderers makes this module **refuse to start**, by
name. Falling back to the other host's rendering would measure the wrong prompt and file it under
the right host, which is the one failure a bundle cannot be re-read out of.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path


class RuntimeUnavailable(RuntimeError):
    """keel-runtime could not be imported -- a reason to stop, never a score."""


def load_runtime(keel_runtime: Path):
    """Imports `keel_runtime` from the sibling checkout named in `stack.toml`.

    Put on `sys.path` rather than vendored, for the same reason the contract is exported rather
    than copied: this repo floats at sibling HEAD, and a prompt built from a stale copy of the
    runtime would be a prompt production never sends.
    """
    keel_runtime = Path(keel_runtime).resolve()
    package = keel_runtime / "keel_runtime" / "__init__.py"
    if not package.is_file():
        raise RuntimeUnavailable(
            f"no keel_runtime package at {keel_runtime} -- this eval imports keel-runtime's own "
            "build_prompt and executor, and copies neither")
    if str(keel_runtime) not in sys.path:
        sys.path.insert(0, str(keel_runtime))
    if importlib.util.find_spec("keel_runtime") is None:
        raise RuntimeUnavailable(f"{keel_runtime} is not importable as `keel_runtime`")
    import keel_runtime.executor as executor          # noqa: PLC0415 - deliberate late import
    import keel_runtime.response_validator as validator  # noqa: PLC0415
    return executor, validator


#: `Case.kind` at `MARKS_VERSION` 9 (data-model §4). `FRAME` is the two typed-seed interpretations.
#: `CHAT` and `FEEDBACK` are the calibration chat's two screens (MARKS_VERSION 17, keel-cloud 083): one case an
#: (idea, dimension) and one a feedback request, neither belonging to a corpus entry.
KINDS = ("CONTEXT", "FRAME", "CALIBRATION", "RESPONDENT", "READING", "COMPARE", "BRIEF", "CHAT",
         "FEEDBACK")


@dataclass
class Case:
    """One prompt this run would send, and everything needed to explain it afterwards."""

    case_id: str
    kind: str                 # one of KINDS
    entry_id: str
    screen: str
    subject: str              # the screen, the vector, the part, the person, COMPARE or BRIEF
    run_index: int
    payload: dict
    prompt: str = ""
    existing_roles: list = field(default_factory=list)
    #: The model the wire's `model` key pins for this case (`instructions/models.py`), or `None`
    #: for the CLI's default. Stamped after the prompt is rendered; never in the prompt.
    model: str | None = None
    #: The effort the wire's `effort` key pins for this case (keel-cloud table v6, spec 047), or
    #: `None` for the CLI's own default. `None` on every `light`-tier case by construction (`effort`
    #: errors on Haiku 4.5). Stamped with the model; never in the prompt.
    effort: str | None = None
    #: What a scorer and the validator's batch need beside the payload: the vector, the part and
    #: plan, the person, the founder's values for `R3` -- never sent to the model.
    meta: dict = field(default_factory=dict)
    #: The `COMPARE` row's engine input (`compare.build_input`); `None` on every model case.
    compare_input: dict | None = None

    @property
    def bundle_path(self) -> str:
        """`<entry>/<screen-or-subject>[/<person>]/run<N>` -- the case id, one slug a segment."""
        parts = self.case_id.split("/")
        if self.kind == "COMPARE":
            return "/".join(_slug(p) for p in parts)
        if not parts[-1].startswith("run"):
            parts.append(f"run{self.run_index}")
        return "/".join(_slug(p) for p in parts)


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in text).strip("-")


def payload_for(instruction: str, context: dict, response_contract: dict,
                content: str = "") -> dict:
    """`InferenceJobService.buildRequestPayload`'s keys, in its order. `content` is what the founder
    typed in chat -- the seed, on the two interpretation screens that read one -- and the empty
    string on every screen started by itself."""
    return {
        "instruction": instruction,
        "context": context,
        "interaction_history": [],
        "input": {"content": content},
        "response_contract": response_contract,
    }


def _require(executor_module, name: str):
    """A keel-runtime attribute this eval cannot proceed without, or a refusal naming it."""
    attribute = getattr(executor_module, name, None)
    if attribute is None:
        raise RuntimeUnavailable(
            f"keel-runtime's executor has no `{name}` -- this eval renders each host's prompt "
            "with the runtime's own renderer and will not substitute another host's")
    return attribute


def render(executor_module, payload: dict, *, job_id: str = "eval", host: str = "claude") -> str:
    """keel-runtime's own renderer **for this host**. The nonce is fresh on every call, by design.

    `claude` gets `build_prompt`, unchanged since spec 009. `copilot` gets the same body with the
    `SYSTEM` and `RESPONSE` sections the CLI has no flag for placed above it -- keel-runtime's
    `_render_copilot_prompt`, called rather than copied (C-8).
    """
    request = executor_module.InferenceRequest(
        job_id=job_id, interaction_id=job_id, turn_number=1, request_payload=payload)
    # Codex (keel-runtime spec 008) has the same arrangement: no system-prompt flag and a schema
    # flag that strict structured outputs refuse for Keel's either/or envelope, so it gets the
    # same rendered prompt as Copilot -- the runtime's own function, not a copy.
    if canonical_host(executor_module, host) in ("copilot", "codex"):
        sections = _require(executor_module, "_prompt_sections")(request)
        schema = _require(executor_module, "_build_envelope_schema")(
            payload.get("response_contract") or {})
        return _require(executor_module, "_render_copilot_prompt")(sections, schema)
    return executor_module.build_prompt(request)


def canonical_host(executor_module, host: str) -> str:
    """keel-runtime's own alias table (`claude-code` -> `claude`), asked rather than copied.

    One place decides the alias and it is not this one -- `keel_runtime.config` -- so a `HOST` this
    eval does not recognise is reported as it was given rather than guessed at, exactly as the
    runtime reports it.
    """
    resolve = getattr(executor_module, "canonical_executor_name", None)
    return resolve(host) if callable(resolve) else host


def build_cases(entry, exported, instructions_by_screen, executor_module, *, n_runs: int = 3,
                host: str = "claude") -> list:
    """Every case one corpus entry produces at `MARKS_VERSION` 9, in FR-016's order and ids:

        <entry>/CONTEXT_INTERPRET/run<N>  <entry>/PROBLEM_INTERPRET/run<N>
        <entry>/SOLUTION_MECHANISM/run<N> <entry>/CALIBRATION_<VECTOR>/run<N> x3
        <entry>/RESPONDENT_PART<P>/run<N> x3 (+ <entry>/RESPONDENT_B2B/run<N> on a B2B entry)
        <entry>/INTERPRET/<person>/run<N> per readable person    <entry>/COMPARE    <entry>/BRIEF/run<N>

    The registry is the export's (`exported.registry`); the plan is derived from it by code (call
    30). **No `INTERPRET` case is built for a gate-No, a chipped or an empty story** -- the chip is
    `GUESSED` by code (FR-017) -- and the `COMPARE` row is a row, not a call: no index, no prompt,
    its payload empty and its engine input on `compare_input`.

    `n_runs` repeats each model case, because a case that passes twice and fails once is an
    unstable instruction rather than a two-thirds one -- `score.py` reports the spread.
    """
    from . import compare as compare_mod             # noqa: PLC0415 - avoids a circular import
    from . import context as context_mod              # noqa: PLC0415
    from . import contract as c                        # noqa: PLC0415
    from . import score as score_mod                   # noqa: PLC0415

    registry = getattr(exported, "registry", None) or entry.registry
    cases = []

    def add(case_id_stem, kind, screen, subject, context, *, content="", meta=None):
        payload = payload_for(instructions_by_screen[screen], context,
                              exported.for_screen(screen), content=content)
        for run_index in range(1, n_runs + 1):
            case = Case(case_id=f"{case_id_stem}/run{run_index}", kind=kind, entry_id=entry.id,
                        screen=screen, subject=subject, run_index=run_index, payload=payload,
                        meta=dict(meta or {}))
            case.prompt = render(executor_module, payload, job_id=_slug(case.case_id), host=host)
            cases.append(case)

    # The three interpretation screens: rendered, validated, never scored (A-2, call 28).
    add(f"{entry.id}/CONTEXT_INTERPRET", "CONTEXT", c.SCREEN_CONTEXT_INTERPRET,
        c.SCREEN_CONTEXT_INTERPRET,
        context_mod.build_context_interpret(entry, exported.keys_for(c.SCREEN_CONTEXT_INTERPRET)))
    for screen, builder in ((c.SCREEN_PROBLEM_INTERPRET, context_mod.build_problem_interpret),
                            (c.SCREEN_SOLUTION_MECHANISM, context_mod.build_solution_mechanism)):
        add(f"{entry.id}/{screen}", "FRAME", screen, screen,
            builder(entry, exported.keys_for(screen)),
            content=context_mod.seed_of(entry, screen))

    # Calibration: one constant, three jobs, one a vector (A-3).
    keys = exported.keys_for(c.SCREEN_CALIBRATION)
    for vector in context_mod.VECTORS:
        add(f"{entry.id}/CALIBRATION_{vector}", "CALIBRATION", c.SCREEN_CALIBRATION, vector,
            context_mod.build_calibration(entry, vector, registry, keys),
            meta={"vector": vector,
                  # Calls 47, 61: the ANSWERED slice -- the derived Ability to pay is not in the job.
                  "registry_slice": [d.key for d in registry.answered_slice(vector,
                                                                            entry.b2b())],
                  # Calls 52, 53: the keys whose model text a reader is shown, so `no_leak`'s
                  # denominator is read, never typed, on a dry run too.
                  "swept": [d.key for d in registry.answered_slice(vector, entry.b2b())
                            if score_mod.is_swept(d, context_mod.window_of(entry), founder=True)],
                  # Call 55: the names W3 / W8 hold to -- the corpus's, else none -- and the
                  # mechanism the validator holds them with (never its Lullaby fixture's).
                  "short_name": context_mod.short_name_of(entry),
                  "offer_name": context_mod.offer_name_of(entry),
                  "validation_mechanism": context_mod.validation_mechanism(entry),
                  "validation_problem_statement": context_mod.problem_statement(entry)})

    # Respondent: one job a part on its own link, handed the plan the eval derived (calls 30, 47) --
    # part 3 of a B2B study is the decision-maker's COMMERCIAL_B2B job, never a fourth one.
    plan = entry.plan(registry)
    keys = exported.keys_for(c.SCREEN_RESPONDENT)
    links = [(part, entry.link_of(part),
              "B2B" if entry.link_of(part) == context_mod.LINK_B2B else f"PART{part}")
             for part in (1, 2, 3)]
    for part, link, label in links:
        add(f"{entry.id}/RESPONDENT_{label}", "RESPONDENT", c.SCREEN_RESPONDENT, label,
            context_mod.build_respondent(entry, part, plan, registry, keys, link=link),
            meta={"part": part, "link": link, "plan": list(plan[part]),
                  "swept": [k for k in plan[part]
                            if score_mod.is_swept(registry.by_key(k), context_mod.window_of(entry))],
                  "short_name": context_mod.short_name_of(entry),
                  "offer_name": context_mod.offer_name_of(entry),
                  "founder_values": context_mod.founder_values(entry, plan[part]),
                  "validation_mechanism": context_mod.validation_mechanism(entry),
                  "validation_problem_statement": context_mod.problem_statement(entry)})

    # INTERPRET: one call a readable person -- never a gate-No, a chip or an empty story.
    keys = exported.keys_for(c.SCREEN_INTERPRET)
    for person in entry.readable():
        add(f"{entry.id}/INTERPRET/{person.person}", "READING", c.SCREEN_INTERPRET,
            person.person, context_mod.build_interpret(entry, person, keys),
            meta={"person": person.person})

    # COMPARE: keel-cloud's engine, at build time, for DRY and real runs alike (research R7).
    cases.append(Case(case_id=f"{entry.id}/COMPARE", kind="COMPARE", entry_id=entry.id,
                      screen=c.SCREEN_COMPARE, subject="COMPARE", run_index=0, payload={},
                      compare_input=compare_mod.build_input(entry, registry)))

    # BRIEF: one paragraph a project, last -- what a founder reads once every answer is read.
    add(f"{entry.id}/BRIEF", "BRIEF", c.SCREEN_BRIEF, "BRIEF",
        context_mod.build_brief(entry, exported.keys_for(c.SCREEN_BRIEF), registry))
    return cases


def build_chat_cases(corpus, exported, instructions_by_screen, executor_module, *, n_runs: int = 3,
                     host: str = "claude") -> list:
    """The calibration chat's cases (MARKS_VERSION 17): one `CALIBRATION_CHAT` case an (idea, dimension) of corpus
    r9's `chat/*.yaml` -- 41 at r9 -- the founder's words as the turn's content, and one `ITEM_FEEDBACK` case a
    row of `chat_feedback.yaml`, the founder's request as its content. `n_runs` repeats each, as every model
    case is. Nothing is called: this renders the prompts."""
    from . import chat as chat_mod                      # noqa: PLC0415 - avoids a circular import
    from . import context as context_mod                # noqa: PLC0415
    from . import contract as c                         # noqa: PLC0415

    registry = exported.registry
    sheets = chat_mod.ideas()
    scenarios = {s["id"]: s for s in corpus.scenarios}
    cases = []

    def add(case_id_stem, kind, screen, subject, entry_id, context, content, meta):
        payload = payload_for(instructions_by_screen[screen], context, exported.for_screen(screen),
                              content=content)
        for run_index in range(1, n_runs + 1):
            case = Case(case_id=f"{case_id_stem}/run{run_index}", kind=kind, entry_id=entry_id,
                        screen=screen, subject=subject, run_index=run_index, payload=payload,
                        meta=dict(meta))
            case.prompt = render(executor_module, payload, job_id=_slug(case.case_id), host=host)
            cases.append(case)

    keys = exported.keys_for(c.SCREEN_CHAT)
    for idea in corpus.chat:
        sheet, scenario = sheets.get(idea.id), scenarios.get(idea.id)
        if sheet is None or scenario is None:
            raise RuntimeUnavailable(f"chat idea {idea.id!r} has no sheet in chat_ideas.yaml or no scenario "
                                     "in verdicts/six-scenarios.yaml")
        for chat_case in idea.cases:
            add(f"chat/{idea.id}/{chat_case.dimension}", "CHAT", c.SCREEN_CHAT, chat_case.dimension,
                idea.id, context_mod.build_calibration_chat(chat_case, sheet, scenario, registry, keys),
                chat_case.founder,
                {"chat_case": chat_case, "idea_words": list(sheet.get("idea_words") or []),
                 "chat_block": registry.by_key(chat_case.dimension).chat, "b2b": idea.b2b})
    keys = exported.keys_for(c.SCREEN_FEEDBACK)
    for feedback in chat_mod.feedback_cases():
        add(f"chat/feedback/{feedback['id']}", "FEEDBACK", c.SCREEN_FEEDBACK, feedback["dimension"],
            "feedback", context_mod.build_item_feedback(feedback, chat_mod.RULES, keys),
            feedback["request"], {"feedback": feedback})
    return cases


def six_scenarios_case():
    """The row for corpus r9's `verdicts/six-scenarios.yaml`: a `COMPARE` row like an entry's (never a call, no
    prompt), measured by `compare.six_scenarios` and counted into `compare_correctness`."""
    from . import compare as compare_mod                # noqa: PLC0415
    from . import contract as c                         # noqa: PLC0415
    return Case(case_id=f"{compare_mod.SIX_ID}/COMPARE", kind="COMPARE", entry_id=compare_mod.SIX_ID,
                screen=c.SCREEN_COMPARE, subject="COMPARE", run_index=0, payload={})
