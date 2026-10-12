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
from . import corpus as corpus_mod
from . import wording as wording_mod
from .registry import (LINK_B2B, LINK_PRIMARY, DEFAULT_WINDOW, SACRIFICE_KEY, RecallWindow,
                       fill_window)

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

#: The key order per screen when no export is handed in (the unit tests): keel-cloud 058's export at
#: `14a1430` for the five new screens, and screen-shapes §2's narrowed keys for `INTERPRET` and
#: `BRIEF`, which 058 still exports in their v8 shape until keel-cloud 064 / 065 (tasks.md T002).
DEFAULT_KEYS = {
    contract_mod.SCREEN_CONTEXT_INTERPRET: ["context_fields", "market", "project_name"],
    contract_mod.SCREEN_PROBLEM_INTERPRET: ["context", "market"],
    contract_mod.SCREEN_SOLUTION_MECHANISM: ["context", "problem_statement", "market"],
    contract_mod.SCREEN_CALIBRATION: ["vector", "context", "market", "interpretation",
                                      "dimensions"],
    contract_mod.SCREEN_RESPONDENT: ["part", "link", "context", "market", "founder_name",
                                     "items", "founder_options", "mechanism"],
    contract_mod.SCREEN_INTERPRET: ["invitation_id", "story"],
    contract_mod.SCREEN_BRIEF: ["project_name", "market", "context", "facts", "beliefs", "stories"],
    # keel-cloud 083 (`ScreenContextBuilder.chatContext` / `feedbackContext`), in the order it writes them.
    contract_mod.SCREEN_CHAT: ["vector", "dimension", "proposal_id", "dimension_name", "meaning", "chat",
                               "context", "market", "statement", "depends_on", "idea_words", "b2b"],
    contract_mod.SCREEN_FEEDBACK: ["vector", "dimension", "frame", "item", "addable", "rules"],
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
        "interpretation": interpretation_of(entry, vector),
        "problem": {"statement": problem_statement(entry)},
        "mechanism": mechanism_of(entry),
        "persona": dict(entry.persona or {}),
        # Calls 47, 59, 61: the vector's ANSWERED slice -- Purchase friction only on a B2B persona, and
        # never the derived one (Ability to pay is written by code; the job is not asked for it).
        "dimensions": fill_window([calibration_dimension(d)
                                   for d in registry.answered_slice(vector, entry.b2b())],
                                  window_of(entry)),
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
    dimension = registry.by_key(key)
    if dimension.fixed_codes is not None:
        return list(dimension.fixed_codes)
    return entry.founder_option_codes(key)


def founder_option_labels(entry, registry, key: str) -> list:
    """keel-cloud 058's `founderOptions` for one model-written set: the LABELS the founder's
    calibration showed (`founder_calibration[key].labels`), in order -- never which were picked.
    An entry recording no labels falls back to the codes."""
    labels = entry.founder_labels(key)
    return list(labels.values()) if labels else founder_option_codes(entry, registry, key)


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
        "items": fill_cost(fill_window([respondent_item(registry.by_key(k), link=link)
                                        for k in item_keys], window_of(entry)),
                           cost_recall_of(entry)),             # call 62: `{cost_period}` filled
        # keel-cloud 058's `founderOptions`: the model-written sets only (the fixed codes are the
        # registry's, and the model has them already) -- the founder's LABELS, as production
        # sends them (`founder_calibration[key].labels`, r3).
        "founder_options": {k: founder_option_labels(entry, registry, k) for k in item_keys
                            if registry.by_key(k).fixed_codes is None
                            and not registry.by_key(k).founder_numeric
                            and not registry.by_key(k).derived
                            and not registry.by_key(k).founder_cost},   # call 67: no kinds any more
    }
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
                        "story": {"prompt": None, "text": person.story, "chip": None},
                        # keel-cloud 058 still exports INTERPRET's v8 keys (`anchors`) until 064
                        # narrows it: the one gate story is handed as the one anchor written under.
                        "anchors": [{"anchor_id": "story", "prompt": None, "text": person.story,
                                     "tap": None}]})


# ------------------------------------------------------------------------------------ BRIEF (065)

#: Call 42: a money figure carries its currency's symbol, as keel-cloud's `Market.symbolFor` does
#: (an unlisted currency is its code and a space); a currency the standing and the answers do not
#: name is the market's own.
CURRENCY_SYMBOL = {"GBP": "£", "USD": "$", "EUR": "€", "JPY": "¥"}
MARKET_CURRENCY = {"GB": "GBP", "US": "USD", "IE": "EUR", "DE": "EUR", "FR": "EUR", "JP": "JPY"}


def _number_words(value) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def _per_words(per) -> str:
    """keel-cloud's `perWords`: *per month*, *one-off* as it is; `three_months` read as words."""
    words = str(per).replace("_", " ").strip()
    return words if words.startswith("per ") or words == "one-off" else f"per {words}"


def is_set(entry, key: str, standing: dict) -> bool:
    """A set dimension: the founder picked several codes, or the standing is option counts."""
    answer = (entry.founder_calibration.get(key) or {}).get("answer")
    return isinstance(answer, list) or bool(standing.get("optionCounts"))


def _money(value) -> str:
    """`PriceLadder.money` after `Figures.round` (HALF_UP to a whole unit): 2500 -> "2,500"."""
    from decimal import ROUND_HALF_UP, Decimal                        # noqa: PLC0415
    whole = int(Decimal(str(value)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return f"{whole:,}"


def _hours(value) -> str:
    """`Figures.number`: one decimal at most, a whole number bare."""
    from decimal import ROUND_HALF_UP, Decimal                        # noqa: PLC0415
    one = Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return str(int(one)) if one == one.to_integral() else str(one)


def currency_of(entry) -> str | None:
    """The project's currency: the market's (keel-cloud 073 `Market.currency`), never guessed."""
    return MARKET_CURRENCY.get((entry.market or {}).get("country"))


def _amount(value, currency) -> str:
    """`CostEstimate.amount`: `rounded` (two places, half up, only where there are pennies) after the
    currency's prefix -- not Python's float `round`, which is banker's."""
    from decimal import ROUND_HALF_UP, Decimal                        # noqa: PLC0415
    stripped = Decimal(str(value)).normalize()
    if stripped.as_tuple().exponent > 0:
        stripped = stripped.quantize(Decimal(1))
    if stripped.as_tuple().exponent < 0:
        stripped = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = f"{int(stripped):,}" if stripped == stripped.to_integral() else f"{stripped:,.2f}"
    symbol = CURRENCY_SYMBOL.get(currency or "", f"{currency} ")
    return f"{symbol}{text}"


#: `Period.days`: a day 1, a week 7, a month 365.25 / 12, a quarter 365.25 / 4, a year 365.25 -- exact.
_DAYS = {"day": 1, "week": 7, "month": "30.4375", "quarter": "91.3125", "year": "365.25"}


def _period_days(period):
    from fractions import Fraction                                    # noqa: PLC0415
    return Fraction(_DAYS.get(period) or _DAYS["quarter"])


def time_only_people(entry) -> list:
    """`Compare.timeOnly` (call 65; keel-cloud 074 D-12, 077): the anchored, un-chipped B2C people whose one
    total is hours -- reported apart from Existing sacrifice, never £0. A *Nothing* is 0 and counted; B2B has
    none (hours are priced at the rate)."""
    if entry.b2b():
        return []
    out = []
    for person in entry.gate_yes():
        if person.anchoring != "ANCHORED" or person.chip:
            continue
        pick = person.picks.get(SACRIFICE_KEY)
        if not isinstance(pick, dict) or "chip" in pick or pick.get("nothing"):
            continue
        if pick.get("mode") == "HOURS" and isinstance(pick.get("value"), (int, float)):
            out.append((person, pick))
    return out


def _time_only_figure(entry, period_words: str, currency) -> str | None:
    """`Figures.timeOnly`: *3 lose only time: median 6 hours a month, valued getting them back at £5 to £10 a
    month, about £0.83 to £1.67 an hour* -- the median person's Price band (the lower middle, by the band's
    floor) over the median hours, per the founder's period."""
    from decimal import ROUND_HALF_UP, Decimal, localcontext         # noqa: PLC0415
    import statistics                                                 # noqa: PLC0415
    apart = time_only_people(entry)
    if not apart:
        return None
    founder = (entry.cost() or {}).get("period")
    who = f"{len(apart)} lose only time" if len(apart) != 1 else "1 loses only time"
    hours = []
    for _person, pick in apart:
        hours.append(pick["value"] * _period_days(founder) / _period_days(pick.get("period")))
    if not hours:
        return who
    with localcontext() as ctx:
        ctx.prec = 16                                                  # MathContext.DECIMAL64
        median = statistics.median(hours)
        median = Decimal(median.numerator) / Decimal(median.denominator)
        line = f"{who}: median {_hours(median)} hours {period_words}"
        bands = [p.picks.get("commercial.price") for p, _pick in apart]
        bands = sorted((b for b in bands if isinstance(b, str)),
                       key=lambda c: corpus_mod.band_floor(c) if corpus_mod.band_floor(c) is not None
                       else -1)
        if not bands or median <= 0:
            return line
        pick = bands[(len(bands) - 1) // 2]
        if pick == corpus_mod.WOULD_NOT_PAY or corpus_mod.band_floor(pick) is None:
            return line + ", and would not pay to get them back"
        kind, *edges = pick.split("_")
        low = None if kind == "under" else Decimal(edges[0])
        high = None if kind == "over" else Decimal(edges[0 if kind == "under" else 1])
        symbol = CURRENCY_SYMBOL.get(currency or "", f"{currency} ")
        if low is None:
            label, per_hour = f"Under {symbol}{_money(high)}", f"under {_amount(high / median, currency)} an hour"
        elif high is None:
            label, per_hour = f"Over {symbol}{_money(low)}", f"over {_amount(low / median, currency)} an hour"
        else:
            label = f"{symbol}{_money(low)} to {symbol}{_money(high)}"
            per_hour = f"{_amount(low / median, currency)} to {_amount(high / median, currency)} an hour"
        return f"{line}, valued getting them back at {label} {period_words}, about {per_hour}"


def cost_figure(entry, standing: dict) -> str | None:
    """Call 64: `Figures.cost`'s shape per the founder's period (keel-cloud 074) -- *a median £35 a month*, and
    on B2C the people who gave only time apart (*; 4 lose only time: median 3.7 hours a month, valued getting
    them back at £20 to £50 a month, about £5.45 to £13.64 an hour*). On B2B the corpus records the total
    median only, not its money / hours split, so the figure is the total alone (a deviation, recorded in
    call 64). `None` where the standing carries neither a median nor anyone apart."""
    currency = currency_of(entry)
    cost = entry.cost() if hasattr(entry, "cost") else None
    period_words = corpus_mod._PERIOD_WORDS.get((cost or {}).get("period"), "over three months")
    parts = []
    if standing.get("median") is not None:
        parts.append(f"a median {_amount(standing['median'], currency)} {period_words}")
    apart = _time_only_figure(entry, period_words, currency)
    if apart:
        parts.append(apart)
    return "; ".join(parts) or None


def ability_figure(entry, standing: dict) -> str | None:
    """Call 64: `Figures.ability` -- *{inside} of {n} already spend {price low} {period} or more*; `None`
    before anyone is counted or without a price."""
    answer = (entry.founder_calibration.get("commercial.price") or {}).get("answer")
    if not isinstance(answer, dict) or not standing.get("n") or standing.get("inside") is None:
        return None
    period = corpus_mod._PERIOD_WORDS.get(answer.get("period"), "")
    return (f"{standing['inside']} of {standing['n']} already spend "
            f"{_amount(answer['low'], answer.get('currency'))}" + (f" {period}" if period else "")
            + " or more")


def price_figure(entry, standing: dict) -> str | None:
    """Call 57, 64: `Figures.price` -- *{inside} of {n} said it would be worth {floor} {period} or
    more*, in the cost's period; `None` before anyone is counted or where the founder left Price out."""
    from .corpus import price_floor                                   # noqa: PLC0415
    answer = (entry.founder_calibration.get("commercial.price") or {}).get("answer")
    if not isinstance(answer, dict) or not standing.get("n") or standing.get("inside") is None:
        return None
    symbol = CURRENCY_SYMBOL.get(answer.get("currency"), f"{answer.get('currency')} ")
    period = corpus_mod._PERIOD_WORDS.get(answer.get("period"), "")
    return (f"{standing['inside']} of {standing['n']} said it would be worth {symbol}"
            f"{_money(price_floor(answer['low']))}" + (f" {period}" if period else "") + " or more")


def _money_of(entry, key: str, standing: dict) -> tuple[str | None, str | None]:
    """The currency and the period a set's money median is in: the standing's own, else the one
    every answer's `cost` agrees on (the median is taken over them), the currency else the
    market's. `(None, None)` where the answers carry no money at all."""
    costs = [(p.picks.get(key) or {}).get("cost") for p in entry.people()
             if isinstance(p.picks.get(key), dict)]
    costs = [c for c in costs if isinstance(c, dict)]
    if not costs and not (standing.get("currency") or standing.get("per")):
        return None, None
    currencies = {c.get("currency") for c in costs if c.get("currency")}
    periods = {c.get("per") for c in costs if c.get("per")}
    currency = standing.get("currency") or (currencies.pop() if len(currencies) == 1 else None)
    currency = currency or MARKET_CURRENCY.get((entry.market or {}).get("country"))
    per = standing.get("per") or (periods.pop() if len(periods) == 1 else None)
    return currency, per


def observed_of(entry, key: str, standing: dict) -> str | None:
    """The deciding line's number, **in the founder's own unit and not keel-cloud's phrase** --
    the median with the unit the founder's answer carried (judgement call 19's rule, at v9: this
    repo does not own `Measure.say` and keeps no copy of it). `None` where the standing carries no
    median.

    **Call 42**: a set dimension's median is money (Existing sacrifice: what they already pay), and
    a bare *165* is a number nobody can quote. It is written in the founder's unit -- *£165 per
    three months*, the currency's symbol and the period from the standing, else from the answers
    the median was taken over -- and a set whose money cannot be written so is `None`: the check
    then asks for its option counts (`N of M`), which is what such a paragraph can say.

    **Call 57 (v11)** supersedes call 42 on the two commercial figures keel-cloud 073 writes itself:
    Existing sacrifice's is `cost_figure` (*a median £22 over three months*) and Price's
    `price_figure` (*5 of 8 said it would be worth £5 a month or more*)."""
    if key == "commercial.existing_sacrifice":
        return cost_figure(entry, standing)                          # calls 57, 64
    if key == "commercial.price":
        return price_figure(entry, standing)                         # calls 57, 64
    if key == "commercial.ability_to_pay":
        return ability_figure(entry, standing)                       # call 64
    median = standing.get("median")
    if median is None:
        return None
    if is_set(entry, key, standing):
        currency, per = _money_of(entry, key, standing)
        if not (currency and per):
            return None
        symbol = CURRENCY_SYMBOL.get(currency, f"{currency} ")
        return f"{symbol}{_number_words(median)} {_per_words(per)}"
    median = _number_words(median)
    answer = (entry.founder_calibration.get(key) or {}).get("answer")
    if isinstance(answer, dict) and answer.get("currency"):
        # The price, as keel-cloud's `observedFigure` writes it: symbol, number, `per` words.
        return f"{CURRENCY_SYMBOL.get(answer['currency'], answer['currency'] + ' ')}{median}" \
            + (f" {_per_words(answer.get('per'))}" if answer.get("per") else "")
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
                           for d in registry.calibrated_slice(vector, entry.b2b())],
        })
    return out


def build_brief(entry, keys=None, registry=None) -> dict:
    """The `BRIEF` screen's context (keel-cloud 079, contract 9): the project, the market, the
    context, and the `facts`, `beliefs` and `stories` of `brief_facts` -- one case a project.
    The three vectors live on in `facts.vectors` (verdict words) and in `vectors_for`, which the
    scorer and the register still read off the entry."""
    from . import brief_facts                                          # noqa: PLC0415
    registry = registry if registry is not None else entry.registry
    keys = DEFAULT_KEYS[contract_mod.SCREEN_BRIEF] if keys is None else keys
    vectors = vectors_for(entry, registry)
    currency, per = _money_of(entry, "commercial.existing_sacrifice",
                              (entry.expected.get("standings") or {}).get(
                                  "commercial.existing_sacrifice") or {})
    cost = (entry.founder_calibration.get("commercial.existing_sacrifice") or {}).get("answer")
    if isinstance(cost, dict):                     # the founder's cost estimate fixes the period
        currency, per = cost.get("currency") or currency, cost.get("period") or per
    currency = currency or MARKET_CURRENCY.get((entry.market or {}).get("country"))
    context = context_of(entry)
    return _fill(keys, {"project_name": entry.title, "market": market_of(entry),
                        "context": context,
                        "facts": brief_facts.facts_for(entry, vectors, context, currency,
                                                       per, corpus_mod._PERIOD_WORDS.get(per, "")),
                        "beliefs": brief_facts.beliefs_for(vectors),
                        "stories": brief_facts.stories_for(entry)})


# ------------------------------------------------------------------- the calibration chat (083)

#: `ScreenContextBuilder.dependsOn`: the beliefs a chat reads beside its own.
CHAT_DEPENDS_ON = {"solution.relative_advantage": ("problem.current_solution_satisfaction",),
                   "commercial.price": ("commercial.existing_sacrifice",),
                   "solution.adoption_friction": ("problem.frequency",)}

_SLOT_FIELDS = ("actor", "actor_plural", "job", "circumstance", "segment")
_CURRENCY_WORD = {"GBP": "\u00a3", "USD": "$", "EUR": "\u20ac"}


def _one(value, symbol="") -> str:
    shown = f"{value:,.0f}" if isinstance(value, (int, float)) and float(value).is_integer() else str(value)
    return f"{symbol}{shown}"


def _number_phrase(low, high, unit, symbol="") -> str:
    span = _one(low, symbol) if low == high or high is None else f"{_one(low, symbol)} to {_one(high, symbol)}"
    return f"{span} {unit}".strip()


def belief_value(row, currency) -> str | None:
    """The `{value}` a founder's measured belief puts in `chat.belief_template`, from a six-scenario row: a
    number and its unit, an amount over a period, or `None` where the row is unsure or has no figure the
    template could say (the dependent belief is then simply absent, as in keel-cloud)."""
    if not isinstance(row, dict) or row.get("unsure"):
        return None
    symbol = _CURRENCY_WORD.get(currency, currency or "")
    for key in ("cost", "price"):
        if isinstance(row.get(key), dict):
            money = row[key]
            return _number_phrase(money["low"], money["high"], f"a {money['period']}", symbol)
    if row.get("low") is not None and row.get("unit"):
        return _number_phrase(row["low"], row.get("high"), row["unit"])
    return None


def fill_slots(text, slots: dict) -> str:
    """`Slots.fill`: the five context slots into `{actor}`, `{actor_plural}`, `{job}`..."""
    for name in _SLOT_FIELDS:
        text = text.replace("{" + name + "}", str(slots.get(name) or ""))
    return text


def build_calibration_chat(case, sheet: dict, scenario: dict, registry, keys=None) -> dict:
    """`CALIBRATION_CHAT` for one (idea, dimension), as `ScreenContextBuilder.chatContext` hands it: the dimension
    and its `chat` block with the opening filled, the context and market, the vector's statement, the beliefs
    this one reads beside it, the idea's own words and whether someone else pays. The founder's answer to the
    opening is the turn's content, not a key."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_CHAT] if keys is None else keys
    dimension = registry.by_key(case.dimension)
    chat = dimension.chat
    slots = dict(sheet["context"])
    window = RecallWindow.read(scenario["window"])
    currency = scenario.get("currency")
    block = {
        "opens_with": window.fill(fill_slots(chat["opens_with"], slots)),
        "measures": list(chat["measures"]),
        "follow_up": chat["follow_up"],
        "leave_out_allowed": chat["leave_out_allowed"],
        "asks_number": chat["asks_number"],
        "frames": dict(sorted(((chat.get("respondent") or {}).get("frames") or {}).items())),
    }
    depends = {}
    for key in CHAT_DEPENDS_ON.get(case.dimension, ()):
        row = (scenario.get("founder") or {}).get(key)
        value = belief_value(row, currency)
        template = (registry.by_key(key).chat or {}).get("belief_template")
        if value and template:
            depends[key] = fill_slots(template, slots).replace("{value}", value)
    values = {
        "vector": dimension.vector, "dimension": dimension.key,
        "proposal_id": f"p-{case.idea}-{dimension.key}",
        "dimension_name": dimension.name, "meaning": dimension.meaning, "chat": block,
        "context": {**slots, "window": window.words()}, "market": dict(sheet["market"]),
        "statement": (sheet.get("statements") or {}).get(dimension.vector),
        "depends_on": depends, "idea_words": list(sheet.get("idea_words") or []),
        "b2b": bool(scenario.get("b2b")),
    }
    return _fill(keys, values)


def build_item_feedback(case: dict, rules, keys=None) -> dict:
    """`ITEM_FEEDBACK`, as `ScreenContextBuilder.feedbackContext` hands it: the vector and dimension, the frame
    (code's), the item as it stands, the kinds an added option may take and the rules a change is held to. The
    founder's request is the turn's content."""
    keys = DEFAULT_KEYS[contract_mod.SCREEN_FEEDBACK] if keys is None else keys
    vector = case["dimension"].split(".", 1)[0].upper()
    return _fill(keys, {"vector": vector, "dimension": case["dimension"], "frame": case["frame"],
                        "item": {"question": case["item"]["question"],
                                 "options": [dict(o) for o in case["item"]["options"]]},
                        "addable": sorted(case.get("addable") or []), "rules": list(rules)})
