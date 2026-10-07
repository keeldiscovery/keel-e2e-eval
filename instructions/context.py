"""The `context` object a screen would have been given (spec 009 FR-005; spec 029
`contracts/screen-shapes.md` §2).

Every key `context-keys.json` names for the screen, **in that order**, `null` where the corpus has
no value. Order is load-bearing: `ScreenContextBuilder` returns a `LinkedHashMap` "so the AI reads
the rendered object in exactly the order this class writes it", and a harness that assembled the
same keys in a different order would be measuring a different prompt. Nothing here decides which
keys exist -- keel-cloud's exporter does, and an unknown key is filled with `None` rather than
dropped, so a screen that gains one is visible in the prompt instead of silently absent. The
`DEFAULT_KEYS` below are only what a builder fills when it is handed no export (the unit tests):
`contracts/screen-shapes.md` §2's order, the request to keel-cloud 058, corrected when 058 ships.

**Every input is the corpus's own, never another screen's live output** (marks-v9 §1): the
calibration job reads r3's `context`, `interpretations.problem` and `solution_mechanism`; the
respondent job reads the plan the eval derived by code from `founder_calibration` (call 30) and is
**never** handed a founder answer; the reader is handed one gate story; the brief is handed
`expected.standings` and the belief sentences r3 records (research R9 -- this repo composes none).

At `MARKS_VERSION` 8 this module also numbered the earlier stages' lines, the questionnaire's
measurements and the brief's claims. All three retired with the subjects they fed (judgement calls
28 and 29); `TAP_ENUM`/`tap_enum` stay because `harness/` still drives today's product with them
(plan O-1).
"""

from __future__ import annotations

from . import contract as contract_mod

# data-model.md note 2 (spec 009): the corpus writes the tap the way a person reads it; the wire
# wants the enum name. Kept for `harness/corpus_script.py` and `harness/stranger_stories.py`, which
# drive today's product (spec 029 O-1); no v9 builder reads it.
TAP_ENUM = {
    "hasn't happened": "HASNT_HAPPENED",
    "hasnt happened": "HASNT_HAPPENED",
    "it hasn't happened": "HASNT_HAPPENED",
    "can't recall": "CANT_RECALL",
    "cant recall": "CANT_RECALL",
    "rather not say": "RATHER_NOT_SAY",
}


def tap_enum(tap):
    """The enum name for a corpus tap, or `None` for no tap. An unknown tap is passed through
    upper-cased rather than dropped, so a corpus that grew a tap shows up in the prompt as itself
    instead of disappearing."""
    if tap is None:
        return None
    key = str(tap).strip().lower()
    return TAP_ENUM.get(key, key.upper().replace(" ", "_").replace("'", ""))


VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: `contracts/screen-shapes.md` §2's key order per screen -- used only when no export is handed in.
DEFAULT_KEYS = {
    contract_mod.SCREEN_CONTEXT_INTERPRET: ["context_fields", "market", "project_name"],
    contract_mod.SCREEN_PROBLEM_INTERPRET: ["context", "market", "interaction_history"],
    contract_mod.SCREEN_SOLUTION_MECHANISM: ["context", "problem", "market",
                                             "interaction_history"],
    contract_mod.SCREEN_CALIBRATION: ["vector", "context", "market", "problem", "mechanism",
                                      "persona", "dimensions"],
    contract_mod.SCREEN_RESPONDENT: ["part", "link", "context", "market", "founder_name",
                                     "items", "founder_options", "mechanism"],
    contract_mod.SCREEN_INTERPRET: ["invitation_id", "story"],
    contract_mod.SCREEN_BRIEF: ["project_name", "market", "context", "vectors"],
}

#: The five fields of r3's `context` a screen is handed (`understood` is the golden sentence
#: `CONTEXT_INTERPRET` would write, and is never an input).
CONTEXT_FIELDS = ("actor", "actor_plural", "job", "circumstance", "segment")

#: On a calibration job, which vector may see which interpretation (US2.1): **the PROBLEM job
#: carries no solution field at all** -- a mechanism in the problem's questions is the leak
#: `no_leak` exists to catch, and the context is where it would come from.
_CALIBRATION_SEES = {"problem": VECTORS, "mechanism": ("SOLUTION", "COMMERCIAL"),
                     "persona": ("COMMERCIAL",)}
_SOLUTION_KEYS = ("mechanism", "solution", "solution_mechanism", "solution_statement")

#: The thirteen registry fields a calibration job is handed per dimension (instruction-table §B
#: row 3), as `(section, field)` -- `section` `None` for a top-level field.
CALIBRATION_FIELDS = (
    (None, "key"), (None, "order"), (None, "name"), (None, "meaning"), (None, "weight"),
    ("founder", "control"), ("founder", "guidance"), ("founder", "normalized"),
    ("founder", "option_rule"), ("founder", "belief_template"), ("founder", "unsure_allowed"),
    ("respondent", "anchor"), ("respondent", "guidance"),
)

#: The registry fields a respondent item carries (screen-shapes §2).
RESPONDENT_FIELDS = ("anchor", "control", "guidance", "option_rule", "chips")

LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"


def _fill(keys, values: dict) -> dict:
    """Every key in the exporter's order, `None` where this builder has no value."""
    return {key: values.get(key) for key in keys}


def market_of(entry) -> dict | None:
    """`ScreenContextBuilder.market`'s own three keys, in its own order."""
    market = entry.market or {}
    if not market:
        return None
    return {"country": market.get("country"), "region": market.get("region"),
            "language": market.get("language")}


def context_of(entry) -> dict:
    """r3's `context`, the five fields a screen reads, in their order."""
    context = entry.context or {}
    return {name: context.get(name) for name in CONTEXT_FIELDS}


def problem_statement(entry) -> str | None:
    """The golden `PROBLEM_INTERPRET` sentence r3 records (research R16, plan O-3)."""
    return (entry.interpretations or {}).get("problem")


def mechanism_of(entry) -> dict:
    """The golden `SOLUTION_MECHANISM` answer r3 records -- `mechanism_terms` is no_leak's and is
    not part of what the screen would have written, so it is not handed on."""
    mechanism = dict(entry.solution_mechanism or {})
    mechanism.pop("mechanism_terms", None)
    return mechanism


def invitation_id(entry, person) -> str:
    """A stable synthetic id -- no invitation exists, and the reading result must echo this back."""
    return f"{entry.id}/{person.person}"


# ------------------------------------------------------------- the three interpretation screens

def build_context_interpret(entry, keys=None) -> dict:
    """`CONTEXT_INTERPRET`: the four context slots as the founder typed them, under the names the
    Context step asks them by -- and nothing from `solution_mechanism`."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_CONTEXT_INTERPRET] if keys is None else keys
    context = entry.context or {}
    return _fill(keys, {
        "context_fields": {"who": context.get("actor"), "what": context.get("job"),
                           "when": context.get("circumstance"),
                           "which_people": context.get("segment")},
        "market": market_of(entry),
        "project_name": entry.title,
    })


def build_problem_interpret(entry, keys=None) -> dict:
    """`PROBLEM_INTERPRET`: the typed seed goes in `input.content` (`seed_of`), and the context
    carries the corpus's own context -- never a solution field."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_PROBLEM_INTERPRET] if keys is None else keys
    return _fill(keys, {"context": context_of(entry), "market": market_of(entry),
                        "interaction_history": []})


def build_solution_mechanism(entry, keys=None) -> dict:
    """`SOLUTION_MECHANISM`: the solution seed in `input.content`, the context, and the corpus's
    own problem sentence as `problem.statement` -- never a live `PROBLEM_INTERPRET` answer."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_SOLUTION_MECHANISM] if keys is None else keys
    return _fill(keys, {"context": context_of(entry), "market": market_of(entry),
                        "problem": {"statement": problem_statement(entry)},
                        "problem_statement": problem_statement(entry),
                        "interaction_history": []})


def seed_of(entry, screen: str) -> str:
    """What the founder typed in chat, for the two screens whose `input.content` it is."""
    statements = entry.statements or {}
    if screen == contract_mod.SCREEN_PROBLEM_INTERPRET:
        return str(statements.get("problem") or "")
    if screen == contract_mod.SCREEN_SOLUTION_MECHANISM:
        return str(statements.get("solution") or "")
    return ""


# --------------------------------------------------------------------------- calibration (062)

def calibration_dimension(dimension) -> dict:
    """One registry dimension as a calibration job sees it: exactly the thirteen fields."""
    out = {}
    for section, name in CALIBRATION_FIELDS:
        if section is None:
            out[name] = getattr(dimension, name)
        else:
            out.setdefault(section, {})[name] = getattr(dimension, section).get(name)
    return out


def build_calibration(entry, vector: str, registry=None, keys=None) -> dict:
    """`CALIBRATION_QUESTIONS` for one vector: the vector, the context, the market, the vector's
    own interpretation and the registry slice. **A key the vector may not see is not written at
    all** -- on the PROBLEM job there is no mechanism and no solution key, not even a `null` one
    (US2.1), because a field the model was shown empty still names the thing it must not ask
    about."""
    registry = registry if registry is not None else entry.registry
    keys = DEFAULT_KEYS[contract_mod.SCREEN_CALIBRATION] if keys is None else keys
    values = {
        "vector": vector,
        "context": context_of(entry),
        "market": market_of(entry),
        "problem": {"statement": problem_statement(entry)},
        "mechanism": mechanism_of(entry),
        "persona": dict(entry.persona or {}),
        "dimensions": [calibration_dimension(d) for d in registry.slice(vector)],
    }
    out = {}
    for key in keys:
        sees = _CALIBRATION_SEES.get(key)
        if sees is not None and vector not in sees:
            continue
        if vector == "PROBLEM" and key in _SOLUTION_KEYS:
            continue
        out[key] = values.get(key)
    return out


# ---------------------------------------------------------------------------- respondent (063)

def founder_option_codes(entry, registry, key: str) -> list:
    """The founder's option set for one dimension, as codes: the registry's fixed codes, or -- for
    a `model_written` set -- the golden plan row's codes less the escapes and respondent-only codes
    (`registry.RESPONDENT_ESCAPES`). Never which of them the founder picked."""
    from .registry import RESPONDENT_ESCAPES                  # noqa: PLC0415
    dimension = registry.by_key(key)
    if dimension.fixed_codes is not None:
        return list(dimension.fixed_codes)
    row = (entry.respondent_questions or {}).get(key) or {}
    return [c for c in row.get("codes") or [] if c not in RESPONDENT_ESCAPES]


def respondent_item(dimension, *, link: str = LINK_PRIMARY) -> dict:
    respondent = dimension.respondent
    item = {"key": dimension.key, "order": dimension.order, "name": dimension.name,
            "respondent": {name: respondent.get(name) for name in RESPONDENT_FIELDS}}
    if link == LINK_B2B and respondent.get("b2b"):
        item["respondent"]["b2b"] = dict(respondent["b2b"])
    return item


def build_respondent(entry, part: int, plan: dict | None = None, registry=None, keys=None, *,
                     link: str = LINK_PRIMARY) -> dict:
    """`RESPONDENT_QUESTIONS` for one part: the plan's items for that part with the registry's
    respondent fields, the founder's option *sets* (never an answer), and the mechanism on parts 2
    and 3 only -- Part 1 is asked before the reveal, and a mechanism there is a leak by
    construction. The B2B link is Part 3's items for the decision-maker, with the registry's `b2b`
    block beside each (no context card and no reveal: the template's, not this builder's)."""
    registry = registry if registry is not None else entry.registry
    plan = plan if plan is not None else entry.plan(registry)
    keys = DEFAULT_KEYS[contract_mod.SCREEN_RESPONDENT] if keys is None else keys
    item_keys = list(plan.get(part) or [])
    values = {
        "part": part,
        "link": link,
        "context": context_of(entry),
        "market": market_of(entry),
        # The corpus records a project and its people, never the founder's name: written and left
        # `null` rather than invented (v8's `build_questions` rule, one screen along).
        "founder_name": None,
        "items": [respondent_item(registry.by_key(k), link=link) for k in item_keys],
        "founder_options": {k: founder_option_codes(entry, registry, k) for k in item_keys},
    }
    if part in (2, 3):
        values["mechanism"] = mechanism_of(entry)
    out = {}
    for key in keys:
        if key == "mechanism" and part == 1:
            continue
        out[key] = values.get(key)
    return out


def founder_values(entry, keys) -> dict:
    """The founder's answers for the plan's keys -- **for the validator's batch only** (`R3` is
    checked against values the model was never shown, screen-shapes §6). Never in a context."""
    return {k: {"answer": (entry.founder_calibration.get(k) or {}).get("answer"),
                "belief_phrase": (entry.founder_calibration.get(k) or {}).get("belief_phrase")}
            for k in keys}


# ------------------------------------------------------------------------------- INTERPRET (064)

def build_interpret(entry, person, keys=None) -> dict:
    """`INTERPRET`, narrowed to the gate story (A-1, call 33): an invitation id and one story. No
    `stage`, no `anchors[]` -- and no case is ever built for a chipped or empty story, which is
    `GUESSED` by code (FR-017). r3 records no story prompt, so `prompt` is written and `null`."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_INTERPRET] if keys is None else keys
    return _fill(keys, {"invitation_id": invitation_id(entry, person),
                        "story": {"prompt": None, "text": person.story, "chip": None}})


# ------------------------------------------------------------------------------------ BRIEF (065)

def observed_of(entry, key: str, standing: dict) -> str | None:
    """The deciding line's number, **in the founder's own unit and not keel-cloud's phrase** --
    the median with the unit the founder's answer carried (judgement call 19's rule, at v9: this
    repo does not own `Measure.say` and keeps no copy of it). `None` where the standing carries no
    median."""
    median = standing.get("median")
    if median is None:
        return None
    if isinstance(median, float) and median.is_integer():
        median = int(median)
    answer = (entry.founder_calibration.get(key) or {}).get("answer")
    unit = answer.get("unit") if isinstance(answer, dict) else None
    return f"{median} {unit}" if unit else str(median)


def _guessed_count(entry, key: str) -> int:
    return sum(1 for p in entry.gate_yes() if p.anchoring == "GUESSED" and key in p.picks)


def brief_dimension(entry, dimension, standing: dict) -> dict:
    calibration = entry.founder_calibration.get(dimension.key) or {}
    return {
        "key": dimension.key,
        "name": dimension.name,
        "weight": dimension.weight,
        "status": standing.get("status"),
        "belief_sentence": calibration.get("belief_sentence"),
        "founder_phrase": calibration.get("belief_phrase"),
        "observed": observed_of(entry, dimension.key, standing),
        "inside": standing.get("inside"),
        "outside": standing.get("outside"),
        # `Standing.below`/`above` are the engine's; the corpus records the side, not the count.
        "below": None,
        "above": None,
        "drift": standing.get("drift"),
        "n_anchored": standing.get("n"),
        "n_guessed": _guessed_count(entry, dimension.key),
        # Beyond screen-shapes §2's list, and named as such: a set dimension's standing *is* its
        # option counts (marks §2.6 allows every `optionCounts` row of `n` as an `N of M`), so a
        # paragraph about one cannot be written, or checked, without them.
        "option_counts": standing.get("optionCounts"),
    }


def vectors_for(entry, registry) -> list:
    """`vectors[]`: each vector's verdict and deciding dimension, and every dimension's standing
    under it, in registry order -- from `expected` and the registry and nothing else."""
    standings = (entry.expected or {}).get("standings") or {}
    verdicts = (entry.expected or {}).get("vector_verdicts") or {}
    out = []
    for vector in VECTORS:
        verdict = verdicts.get(vector) or {}
        out.append({
            "vector": vector,
            "verdict": verdict.get("verdict"),
            "deciding": verdict.get("deciding"),
            "dimensions": [brief_dimension(entry, d, standings.get(d.key) or {})
                           for d in registry.slice(vector)],
        })
    return out


def build_brief(entry, keys=None, registry=None) -> dict:
    """The `BRIEF` screen's context: the project, the market, the context, and the three vectors
    with every dimension's standing -- one case a project (FR-019). No `claims`, no `stage`."""
    registry = registry if registry is not None else entry.registry
    keys = DEFAULT_KEYS[contract_mod.SCREEN_BRIEF] if keys is None else keys
    return _fill(keys, {"project_name": entry.title, "market": market_of(entry),
                        "context": context_of(entry), "vectors": vectors_for(entry, registry)})
