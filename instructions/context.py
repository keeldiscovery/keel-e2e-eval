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
calibration job reads the corpus's `context`, `interpretations.problem` and `solution_mechanism` (and, since
keel-cloud 087, an empty `answers`: the seed-time job drafts every list from the interpretation alone, and the
corpus records no Answer-screen text); the respondent job reads the plan the eval derived by code from
`founder_calibration` (call 30) and is **never** handed a founder answer; the `ASKED` job (keel-cloud 088) is
handed one list's labels by index; the reader is handed one gate story. (The brief's context left with the BRIEF
screen, keel-cloud 104; spec 052.)

At `MARKS_VERSION` 8 this module also numbered the earlier stages' lines, the questionnaire's
measurements and the brief's claims. All three retired with the subjects they fed (judgement calls
28 and 29); `TAP_ENUM`/`tap_enum` stay because `harness/` still drives today's product with them
(plan O-1).
"""

from __future__ import annotations

from . import contract as contract_mod
from . import wording as wording_mod
from .registry import LINK_B2B, LINK_PRIMARY, DEFAULT_WINDOW, RecallWindow, fill_window

# data-model.md note 2 (spec 009): the corpus writes the tap the way a person reads it; the wire
# wants the enum name. Kept for `harness/corpus_script.py` (the classic S-001 and S-004), which
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

#: The key order per screen when no export is handed in (the unit tests): keel-cloud 058's export at
#: `14a1430` for the five new screens, and screen-shapes §2's narrowed keys for `INTERPRET`.
DEFAULT_KEYS = {
    contract_mod.SCREEN_CONTEXT_INTERPRET: ["context_fields", "market", "project_name"],
    contract_mod.SCREEN_PROBLEM_INTERPRET: ["context", "market"],
    contract_mod.SCREEN_SOLUTION_MECHANISM: ["context", "problem_statement", "market"],
    contract_mod.SCREEN_CALIBRATION: ["vector", "context", "market", "interpretation",
                                      "dimensions", "answers"],
    contract_mod.SCREEN_RESPONDENT: ["part", "link", "context", "market", "founder_name",
                                     "items", "problem", "condition", "mechanism", "offer_name"],
    contract_mod.SCREEN_ASKED: ["dimension", "context", "market", "items"],
    contract_mod.SCREEN_INTERPRET: ["invitation_id", "story"],
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

#: The registry fields a calibration job is handed per dimension (`RegistrySlices.calibrationSlice`, keel-cloud
#: 087: no weight, and the list dimensions' `saves`), as `(section, field)` -- `section` `None` for a top-level
#: field. A founder field the registry leaves out is not written (the cloud writes only non-null ones).
CALIBRATION_FIELDS = (
    (None, "key"), (None, "order"), (None, "name"), (None, "meaning"),
    ("founder", "control"), ("founder", "guidance"), ("founder", "normalized"),
    ("founder", "option_rule"), ("founder", "belief_template"), ("founder", "unsure_allowed"),
    ("founder", "saves"), ("respondent", "anchor"), ("respondent", "guidance"),
)

#: The registry fields a respondent item carries (`RegistrySlices.respondentItems`, keel-cloud 088: the one
#: `escape` where `chips` were).
RESPONDENT_FIELDS = ("anchor", "control", "guidance", "option_rule", "escape")

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


def window_of(entry) -> RecallWindow:
    """The entry's recall window -- r3's `context.recall_window: {count, unit}` (founder decision
    42, keel-cloud 058 `5fc7220`), read as `RecallWindow.read` reads it, else keel-cloud's default
    (7 nights), as `ScreenContextBuilder.window` reads a project with no confirmed context."""
    return RecallWindow.read((entry.context or {}).get("recall_window")) or DEFAULT_WINDOW


def context_of(entry) -> dict:
    """r3's `context`: the five slots a screen reads, in their order, and the recall window's words
    (keel-cloud 058's `slots`, T002)."""
    context = entry.context or {}
    out = {name: context.get(name) for name in CONTEXT_FIELDS}
    out["window"] = window_of(entry).words()
    return out


def problem_statement(entry) -> str | None:
    """The golden `PROBLEM_INTERPRET` sentence r3 records (research R16, plan O-3)."""
    return (entry.interpretations or {}).get("problem")


def short_name_of(entry) -> str | None:
    """The idea's one short name (W3, call 55): the corpus's `solution_mechanism.short_name`, or
    `None` where an entry records none; the eval never takes it from a live screen's answer."""
    name = (entry.solution_mechanism or {}).get("short_name")
    return name if isinstance(name, str) and name.strip() else None


def offer_name_of(entry) -> str | None:
    """The offer's one problem-side name (W8, call 55): the corpus's `interpretations.offer_name`,
    or `None` where an entry records none."""
    name = (entry.interpretations or {}).get("offer_name")
    return name if isinstance(name, str) and name.strip() else None


def cost_period_of(entry) -> str | None:
    """The founder's cost period (call 62), `None` where they left the cost out."""
    return (entry.cost() or {}).get("period") if hasattr(entry, "cost") else None


def cost_recall_of(entry) -> str:
    """`ScreenContextBuilder.costRecall` (call 62): the recall words of the founder's cost period -- the
    words `{cost_period}` is filled with in the registry's guidance (W10, which held the model's question to
    them, retired at v13: code writes the question)."""
    return wording_mod.recall_words(cost_period_of(entry))


def fill_cost(node, recall: str):
    """`RegistrySlices.filledCost`: the registry's `{cost_period}` placeholder filled with the recall words,
    everywhere in a respondent item (keel-cloud 074 fills it on respondent items only)."""
    if isinstance(node, str):
        return node.replace("{cost_period}", recall)
    if isinstance(node, dict):
        return {k: fill_cost(v, recall) for k, v in node.items()}
    if isinstance(node, list):
        return [fill_cost(v, recall) for v in node]
    return node


def mechanism_of(entry) -> dict:
    """The golden `SOLUTION_MECHANISM` answer r3 records, as keel-cloud hands it on: the four
    fields, the terms (`mechanismForRespondents`) and since 072 the `short_name` (the corpus's, else
    `null`, call 55), never `not_assumed` -- the claims it stripped."""
    m = entry.solution_mechanism or {}
    out = {k: m.get(k) for k in ("actor", "trigger", "mechanism", "output", "mechanism_terms")}
    out["short_name"] = short_name_of(entry)
    return out


def validation_mechanism(entry) -> dict:
    """The golden mechanism as the VALIDATOR's state only -- the four fields, `not_assumed`, the
    terms and the short name the job was handed, so keel-cloud applies R4 with the project's real
    vocabulary on a Part 1 (or B2B) entry, whose job is handed no mechanism, and W3 to no name the
    job was not given (its Lullaby fixture carries one). Never in a prompt context."""
    m = entry.solution_mechanism or {}
    out = {k: m.get(k) for k in ("actor", "trigger", "mechanism", "output", "not_assumed",
                                 "mechanism_terms")}
    out["short_name"] = short_name_of(entry)
    return out


def interpretation_of(entry, vector: str):
    """keel-cloud's calibration `interpretation` (058 T002; 071; 072): the problem statement alone on
    PROBLEM -- no solution key exists in that job -- the mechanism card on SOLUTION (with its
    `short_name`), and on COMMERCIAL the persona map `{summary, decider_role, b2b, offer_name}`
    (call 55). 058 composes the card's `statement` from the four fields (`Mechanism.compose`); this
    eval keeps no copy of that, so it hands the founder's solution seed instead and says so. The
    corpus records no persona summary, so it is `null`; the decider is the role's label."""
    if vector == "PROBLEM":
        return {"statement": problem_statement(entry)}
    if vector == "SOLUTION":
        return {"statement": (entry.statements or {}).get("solution"), **mechanism_of(entry)}
    role = entry.role(entry.decision_maker_role()) if entry.b2b() else None
    return {"summary": None, "decider_role": (role or {}).get("label"), "b2b": entry.b2b(),
            "offer_name": offer_name_of(entry)}


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
        # VectorCorridorService.proposeContext's order: the four fields, then the window.
        "context_fields": {"who": context.get("actor"), "what": context.get("job"),
                           "when": context.get("circumstance"),
                           "which_people": context.get("segment"),
                           "recall_window": window_of(entry).to_map()},
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
    """One registry dimension as a calibration job sees it: `CALIBRATION_FIELDS`, a founder field the registry
    does not carry left out as the cloud leaves it out."""
    out = {}
    for section, name in CALIBRATION_FIELDS:
        if section is None:
            out[name] = getattr(dimension, name)
            continue
        value = getattr(dimension, section).get(name)
        if section == "founder" and value is None:
            out.setdefault(section, {})
            continue
        out.setdefault(section, {})[name] = value
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
        "interpretation": interpretation_of(entry, vector),
        "problem": {"statement": problem_statement(entry)},
        "mechanism": mechanism_of(entry),
        "persona": dict(entry.persona or {}),
        # Calls 47, 59, 61: the vector's ANSWERED slice -- Purchase friction only on a B2B persona, and
        # never the derived one (Ability to pay is written by code; the job is not asked for it).
        "dimensions": fill_window([calibration_dimension(d)
                                   for d in registry.answered_slice(vector, entry.b2b())],
                                  window_of(entry)),
        # keel-cloud 087 call 8: a redraft carries one dimension and the founder's Answer for it; the seed-time
        # job -- the one this eval measures -- carries none (the corpus records no Answer-screen text).
        "answers": {},
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

def respondent_item(dimension, *, link: str = LINK_PRIMARY) -> dict:
    respondent = dimension.respondent
    item = {"key": dimension.key, "order": dimension.order, "name": dimension.name,
            "respondent": {name: respondent.get(name) for name in RESPONDENT_FIELDS}}
    if link == LINK_B2B and respondent.get("b2b"):
        item["respondent"]["b2b"] = dict(respondent["b2b"])
    return item


def problem_of(entry) -> str | None:
    """keel-cloud 116 FR-1 (`ScreenContextBuilder.prevalenceClause`, `VectorCorridor.prevalenceClause`): the founder's
    Prevalence clause the part-1 job writes the gate from -- `WindowFrame.eventFromPrevalence` over the founder's
    Prevalence question. The eval's walk writes that question's `event` as `vectors_script.event_past` (the scripted
    `CALIBRATION_QUESTIONS`), so the clause read back is it: the golden entries' own (`PROBLEM_CLAUSES`), else *had a
    time when {circumstance}* (a back-test entry records no founder clause of its own). Spec 110 FR-4."""
    from harness import vectors_script as vs                            # noqa: PLC0415 - harness reads this module
    try:
        return vs.event_past(entry)
    except (KeyError, TypeError):
        return None


def condition_of(entry) -> str | None:
    """keel-cloud 120 FR-2 (`VectorCorridor.segmentCondition`): the segment's condition the chip asks before the gate,
    as the confirmed context stores it (`vectors_script.card_condition`), `None` where there is none. Spec 110 FR-4."""
    from harness import vectors_script as vs                            # noqa: PLC0415
    try:
        return vs.card_condition(entry)
    except (KeyError, TypeError):
        return None


def _hands_condition(entry, part: int, link: str) -> bool:
    """`ScreenContextBuilder` (keel-cloud 120 FR-2, 145 FR-4b, 166 FR-2): the condition rides part 1, the
    decision-maker's part 3, and the person's own part 3 on a study that serves no gate (`StudyScope.servesGate`:
    neither the problem nor the solution in scope)."""
    if part == 1:
        return True
    if part != 3:
        return False
    if link == LINK_B2B:
        return True
    scope = getattr(entry, "scope", None) or "ALL"
    return scope == "COMMERCIAL"


def build_respondent(entry, part: int, plan: dict | None = None, registry=None, keys=None, *,
                     link: str = LINK_PRIMARY) -> dict:
    """`RESPONDENT_QUESTIONS` for one part: the plan's items for that part with the registry's
    respondent fields (never a founder answer -- keel-cloud 087 dropped `founder_options`), and the
    mechanism on parts 2 and 3 only -- Part 1 is asked before the reveal, and a mechanism there is a
    leak by construction. The B2B link is Part 3's items for the decision-maker, with the registry's
    `b2b` block beside each. Since keel-cloud 088 the job writes the gate's clause and nothing else."""
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
        "items": fill_cost(fill_window([respondent_item(registry.by_key(k), link=link)
                                        for k in item_keys], window_of(entry)),
                           cost_recall_of(entry)),             # call 62: `{cost_period}` filled
    }
    # keel-cloud 116 FR-1 / 120 FR-2 (spec 110 FR-4): part 1 is handed the founder's Prevalence clause and the
    # segment's condition -- until spec 110 the export's two keys were written `null`, so every screen of this job wrote
    # the gate from `context.circumstance`, the path the instruction keeps for a missing `problem`
    if part == 1:
        values["problem"] = problem_of(entry)
    if _hands_condition(entry, part, link):
        values["condition"] = condition_of(entry)
    if part in (2, 3) and link != LINK_B2B:
        values["mechanism"] = mechanism_of(entry)
    if part == 3:
        # keel-cloud 072 (W8): part 3 on either link names the offer by its own key -- written only
        # where the export's key list carries `offer_name` (the exporter decides the keys).
        values["offer_name"] = offer_name_of(entry)
    out = {}
    for key in keys:
        if key == "mechanism" and (part == 1 or link == LINK_B2B):
            continue
        if key == "offer_name" and part != 3:           # 072: part 3 only, on either link
            continue
        if key == "problem" and part != 1:              # 116: the part-1 job alone
            continue
        if key == "condition" and not _hands_condition(entry, part, link):
            continue
        out[key] = values.get(key)
    return out


# ---------------------------------------------------------------------------------- ASKED (088)

def asked_frame(key: str, occasion: str | None) -> str:
    """`AskedRules.framed(dimension, occasion, "{asked}")`: the question code puts a face into (design §5.1). Spec 112
    FR-1 (keel-cloud 171 FR-4b, `ItemFrames.adoptionFrame`): Adoption friction's is *To use it, you'd {asked}. Would you
    do that, or not?* (was *{asked}. Would you do that, or not?*)."""
    if key == "solution.adoption_friction":
        return "To use it, you'd {asked}. Would you do that, or not?"
    return f"On your last {occasion or 'time'}, {{asked}}?"


def asked_items(entry, key: str) -> list:
    """`[{index, label}]`: the founder's list items to phrase, by their index in the list -- the corpus's own."""
    saved = entry.founder_list(key) or {}
    return [{"index": i, "label": item.get("label")} for i, item in enumerate(saved.get("items") or [])]


def build_asked(entry, key: str, registry=None, keys=None) -> dict:
    """`ASKED` (keel-cloud 088 FR-003): one list dimension -- `{key, name, frame}` -- the context slots, the
    market and the items by index, as `ScreenContextBuilder` hands them on a Save."""
    registry = registry if registry is not None else entry.registry
    keys = DEFAULT_KEYS[contract_mod.SCREEN_ASKED] if keys is None else keys
    name = registry.by_key(key).name if registry is not None else key
    return _fill(keys, {"dimension": {"key": key, "name": name, "frame": asked_frame(key, entry.occasion())},
                        "context": context_of(entry), "market": market_of(entry),
                        "items": asked_items(entry, key)})


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
                        "story": {"prompt": None, "text": person.story, "chip": None},
                        # keel-cloud 058 still exports INTERPRET's v8 keys (`anchors`) until 064
                        # narrows it: the one gate story is handed as the one anchor written under.
                        "anchors": [{"anchor_id": "story", "prompt": None, "text": person.story,
                                     "tap": None}]})
