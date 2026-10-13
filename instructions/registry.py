"""keel-cloud's dimension registry, read from the export and checked before a case is built
(spec 029 FR-021, data-model §1, research R4; cut to twelve by keel-cloud 071 and spec 030; thirteen
again since keel-cloud 073 and spec 031, Price back; cost first since keel-cloud 074 and spec 032).

The registry is the **golden** for `dimension_coverage` and `option_validity` (judgement calls 30
and 31): every control, code, bin, belief template and plan part a scorer checks a question
against. keel-cloud 058 exports it as `dimension-registry.json` beside `model-routing.json`;
`instructions/contract.read` loads it through `from_document` here. Nothing in this module is a
copy of the cloud's registry -- the fixture under `tests/fixtures/registry/` is a hand-sized slice
of keel-cloud 074's export.

**The eight invariants are this repository's to check** (keel-cloud `registry-schema.md`
§Invariants; spec 030 judgement call 46), because a mark of 1.00 is honest only against a registry
that is itself well formed -- marks §2.2: *"1.00 is honest only because the registry fixes the
codes"*. A registry that fails one is a **refusal to start** naming the invariant and the key,
never a warning and never a score. At `MARKS_VERSION` 12 and 13 the registry is **thirteen keys, 4 / 3 / 6**
(judgement call 59; keel-cloud 074's `DimensionRegistry`, mirrored): nine of them deal-breakers that
can each read `NOT_HOLDING_UP`; `asked_in_v1` is gone (a registry still carrying it is refused as
unknown-shaped, not ignored); the entry-level `b2b_only` sits on **Purchase friction alone** and
Ability to pay is `b2b_link_only` on the respondent side (calibrated on every persona, asked on the
decision-maker's link only); Existing sacrifice's founder control is `cost_estimate` over the five
periods and the modes `AMOUNT · HOURS` (and, since v13, no `code_rule`: there are no kinds of cost),
its respondent control `cost_total` yields a number (so it is drawn as an interval, invariant 6); Price is back as SHAPES over the same five periods
(`day · week · month · quarter · year`, fixed to the cost's); Ability to pay's founder control is
`derived` -- a `price_cost_ratio` from the registry's own keys, read by `cost_covers_price`.

**What a project calibrates, answers and asks is read here, never typed by a scorer** (calls 46,
47, 59): `calibrated(b2b)` is every entry less the `b2b_only` one when the persona is not B2B (twelve
on B2C, thirteen on B2B); `answered(b2b)` is that less the `derived` one, which code writes -- what
the calibration job writes questions for (eleven / twelve); and `plan_keys(part, founder_calibration,
link, b2b)` is what one link asks in one part -- keel-cloud 074's `DimensionRegistry.calibrated` /
`answered` / `asked` and `EvidencePlan`, mirrored.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: Invariant 1: 13 keys, 4 / 3 / 6 (keel-cloud 073: `commercial.price` back at commercial order 2).
PER_VECTOR = {"PROBLEM": 4, "SOLUTION": 3, "COMMERCIAL": 6}

#: Invariant 2: the nine deal-breakers, exactly (`registry-schema.draft.md` §Invariants 2). Fixed
#: by the schema rather than read off the file, because the point of the invariant is that the file
#: cannot quietly promote or demote one.
DEAL_BREAKERS = {
    "PROBLEM": ("problem.prevalence", "problem.importance",
                "problem.current_solution_satisfaction"),
    "SOLUTION": ("solution.compatibility", "solution.relative_advantage",
                 "solution.adoption_friction"),
    "COMMERCIAL": ("commercial.existing_sacrifice", "commercial.buyer_payer_alignment",
                   "commercial.commitment"),
}

#: Invariant 3: `b2b_only` on exactly Purchase friction (calibrated and asked only on a B2B persona),
#: `b2b_link_only` on exactly Ability to pay (calibrated on every persona, asked on the
#: decision-maker's link only; keel-cloud 074), and every entry asked in the part of its own vector
#: -- 4 / 3 / 6 entries a part. On `PRIMARY` that is 3 / 3 / 4 after the gate; on `COMMERCIAL_B2B`
#: the commercial part whole, 6.
B2B_ONLY = ("commercial.purchase_friction",)
B2B_LINK_ONLY = ("commercial.ability_to_pay",)
PER_PART = {1: 4, 2: 3, 3: 6}
PART_VECTOR = {1: "PROBLEM", 2: "SOLUTION", 3: "COMMERCIAL"}

#: The two links a person answers on (keel-cloud `RespondentLink`).
LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"

#: The respondent controls a person taps or types and that owe no options (the model writes `null`):
#: Frequency's 0-to-7 control, and the number it becomes on a recall window longer than 7.
NUMERIC_RESPONDENT_CONTROLS = ("segmented_0_to_7", "number_with_unit")
#: Invariant 6: the respondent controls whose answer is a number (`answers.shape == interval`) --
#: keel-cloud 077's `RespondentControl.yieldsNumber`. `cost_total` joins the two above (Existing sacrifice
#: is drawn as an interval, D-6) and, unlike v12's `branch_pick_amounts`, owes no options at all (call 67).
COST_TOTAL_CONTROL = "cost_total"
NUMBER_YIELDING_CONTROLS = NUMERIC_RESPONDENT_CONTROLS + (COST_TOTAL_CONTROL,)

#: Invariant 7: the one gate.
GATE_KEY = "problem.prevalence"
GATE_CONTROL = "gate_yes_no"

#: Respondent-only codes the registry adds on the respondent side and never offers the founder
#: (registry decision 12).
FIXED_RESPONDENT_CODES = {
    "commercial.commitment": ("nothing_yet",),
}

#: Codes a respondent item adds that are no founder's option: the escapes and the respondent-only
#: fixed codes above. What is left of a golden plan row's codes once these go is the founder's own
#: option set -- `founder_options` on the respondent screen, and what `option_validity` requires
#: present.
RESPONDENT_ESCAPES = ("something_else", "nothing", "never_came_up", "would_not_fit",
                      "nothing_would_change", "free_or_gift", "it_was_free", "would_not_reach",
                      "nothing_yet", "would_not_pay")

#: The founder-side numeric control: no options, a spec the registry owns.
NUMERIC_FOUNDER_CONTROLS = ("numeric_interval",)

#: Price (keel-cloud 073, judgement call 50; 074): the founder states a range, rendered by code over the
#: cost's period -- no options, and no question text the model writes (call 53).
PRICE_KEY = "commercial.price"
PRICE_FOUNDER_CONTROL = "price_range"
#: keel-cloud 074's `Period.wires()`: the five periods a cost is stated over, and a price is fixed to.
PERIODS = ("day", "week", "month", "quarter", "year")
#: Invariant 5 (074): a `price_range` entry's periods are exactly `PriceLadder.PERIODS` = `Period.wires()`.
PRICE_PERIODS = PERIODS
#: The cost estimate (074): the founder's control on Existing sacrifice, its modes (`CalibrationAnswer.Cost.MODES`).
COST_FOUNDER_CONTROL = "cost_estimate"
COST_MODES = ("AMOUNT", "HOURS")
#: Ability to pay (074): derived by code from the cost and the price, read by `cost_covers_price`.
ABILITY_KEY = "commercial.ability_to_pay"
DERIVED_FOUNDER_CONTROL = "derived"
DERIVED_COMPARE_RULE = "cost_covers_price"
#: `AbilityToPay`'s four bands (with decision 2, 2026-10-10).
ABILITY_BANDS = ("small_share", "mostly_from_spend", "some_from_spend", "new_money")
#: Relative advantage, benefit first (keel-cloud 085, call 81): the founder ticks one to four advantages
#: (`multi_choice`), and the respondent's item is code's whole -- better / no difference / worse, and under
#: better the founder's ticks -- read by `benefit_first`. The model writes the founder's question and five
#: options as before, and for the respondent the item's key alone.
BENEFIT_KEY = "solution.relative_advantage"
BENEFIT_CONTROL = "benefit_with_advantages"
BENEFIT_RULE = "benefit_first"
BENEFIT_FOUNDER_CONTROL = "multi_choice"
BENEFIT_CODES = ("positive", "neutral", "negative")
BENEFIT_MAX_TICKS = 4
#: The respondent controls whose question and options are wholly code's (calls 53, 67, 81): the model owes
#: the item's key and nothing else, and nothing it writes there is read. Since keel-cloud 077 that is
#: Price's ladder and Existing sacrifice's one total (no kinds, so no options and no units); since 085
#: Relative advantage's benefit item -- on the **respondent** side only (its founder question is still the
#: model's, so `score.model_text` / `is_swept` read the code-written control on the respondent side only).
CODE_WRITTEN_RESPONDENT_CONTROLS = ("price_ladder", COST_TOTAL_CONTROL, BENEFIT_CONTROL)
#: Existing sacrifice's respondent control since 077: one total (`AMOUNT | HOURS`, one number) over the
#: founder's recall period. `branch_pick_amounts` (073-076) is gone, and is refused by name.
GONE_AMOUNTS_CONTROL = "branch_pick_amounts"
#: Existing sacrifice: its question names no offer (keel-cloud 072 D-2).
SACRIFICE_KEY = "commercial.existing_sacrifice"


def names_the_offer(dimension) -> bool:
    """`ScreenResultApplier.namesTheOffer` (call 55): the questions W3 / W8 hold to the name --
    every SOLUTION and COMMERCIAL entry but Existing sacrifice, which asks what the problem already
    costs and names no offer (keel-cloud 072 D-2)."""
    return dimension.vector != "PROBLEM" and dimension.key != SACRIFICE_KEY


#: keel-cloud 058 (2026-10-07): the registry carries `{window}` / `{window_unit}` placeholders, the
#: project's recall window, filled by code. Founder decision 42 (2026-10-08) made the window COUNT +
#: UNIT, chosen at the Context step; every r3 entry records its own as `context.recall_window`.
_WINDOW_UNITS = {
    # Appended only, never reordered -- `RecallWindow.Unit`'s order and words.
    "NIGHTS": ("night", "nights"), "DAYS": ("day", "days"),
    "WORKING_DAYS": ("working day", "working days"), "WEEKS": ("week", "weeks"),
    "MONTHS": ("month", "months"), "CYCLES": ("cycle", "cycles"), "SHIFTS": ("shift", "shifts"),
}
_LEGACY_WINDOWS = {"SEVEN_NIGHTS": (7, "NIGHTS"), "SEVEN_DAYS": (7, "DAYS"),
                   "FIVE_WORKING_DAYS": (5, "WORKING_DAYS"), "THIRTY_DAYS": (30, "DAYS"),
                   "LAST_CYCLE": (1, "CYCLES")}


@dataclass(frozen=True)
class RecallWindow:
    """keel-cloud 058's `domain.vectors.RecallWindow` (5fc7220), mirrored: the words `{window}` and
    `{window_unit}` are filled with. Code fills both; a model never does -- and since keel-cloud 072
    code writes the windowed questions too, so the ways `C7` / `R8` accepted a question naming the
    window (`said`, `is_named_in`) retired with those rules (judgement call 52)."""

    count: int
    unit: str

    def __post_init__(self):
        if self.unit not in _WINDOW_UNITS:
            raise ValueError(f"{self.unit!r} is not a recall-window unit; use one of "
                                f"{list(_WINDOW_UNITS)}")
        if not isinstance(self.count, int) or isinstance(self.count, bool) or self.count < 1:
            raise ValueError(f"a recall window counts at least one "
                                f"{_WINDOW_UNITS[self.unit][0]}, and this was {self.count!r}")

    @property
    def singular(self) -> str:
        return _WINDOW_UNITS[self.unit][0]

    @property
    def plural(self) -> str:
        return _WINDOW_UNITS[self.unit][1]

    def words(self) -> str:
        """`{window}`: "the last 7 nights", or "the last shift" for a count of 1."""
        return f"the last {self.singular}" if self.count == 1 else \
            f"the last {self.count} {self.plural}"

    def unit_words(self) -> str:
        """`{window_unit}` -- Java's `unit()`: Frequency's unit, "nights out of 7"."""
        return f"{self.plural} out of {self.count}"

    def fill(self, text):
        return None if text is None else \
            text.replace("{window_unit}", self.unit_words()).replace("{window}", self.words())

    @property
    def frames_frequency(self) -> bool:
        """`WindowFrame.framesFrequency`: Frequency is code's sentence on a window of more than one
        unit ("those 7 nights"); a one-unit window keeps a model-written question (call 52)."""
        return self.count > 1

    def to_map(self) -> dict:
        """`{count, unit}`, as the wire and the job carry it."""
        return {"count": self.count, "unit": self.unit}

    @classmethod
    def read(cls, raw):
        """`RecallWindow.read`: a `{count, unit}` map, or a legacy five-value name (upcast);
        `None` reads `None`, anything else is refused."""
        if raw is None or isinstance(raw, cls):
            return raw
        if isinstance(raw, dict):
            count, unit = raw.get("count"), raw.get("unit")
            if not isinstance(count, (int, float)) or isinstance(count, bool) \
                    or float(count) != int(count) or unit is None:
                raise ValueError(f"a recall window is {{count, unit}}, and this was {raw!r}")
            return cls(int(count), str(unit))
        legacy = _LEGACY_WINDOWS.get(str(raw))
        if legacy is None:
            raise ValueError(f"{raw!r} is not a recall window")
        return cls(*legacy)


#: `RecallWindow.DEFAULT`: what a project reads when nothing was chosen.
DEFAULT_WINDOW = RecallWindow(7, "NIGHTS")


def fill_window(node, window=DEFAULT_WINDOW):
    """`node` (a string, dict or list) with both placeholders filled -- what a job is handed
    (`ScreenContextBuilder.RegistrySlices.filled`)."""
    window = window or DEFAULT_WINDOW
    if isinstance(node, str):
        return window.fill(node)
    if isinstance(node, dict):
        return {k: fill_window(v, window) for k, v in node.items()}
    if isinstance(node, list):
        return [fill_window(v, window) for v in node]
    return node


class RegistryUnavailable(RuntimeError):
    """The registry could not be read, or it fails an invariant -- a reason to stop, never a score."""


@dataclass(frozen=True)
class Dimension:
    key: str
    vector: str
    order: int
    name: str
    meaning: str
    weight: str
    founder: dict
    respondent: dict
    answers: dict
    left_out: dict = field(default_factory=dict)
    lullaby: dict = field(default_factory=dict)
    #: keel-cloud 071: calibrated and asked only when the persona is B2B (074: Purchase friction alone).
    b2b_only: bool = False

    @property
    def normalized(self) -> dict:
        return self.founder.get("normalized") or {}

    @property
    def codes(self):
        """The fixed founder codes, or the string `model_written`, or `None` for a numeric spec."""
        return self.normalized.get("codes")

    @property
    def fixed_codes(self) -> list | None:
        codes = self.codes
        return list(codes) if isinstance(codes, list) else None

    @property
    def part(self):
        return self.respondent.get("part")

    @property
    def founder_numeric(self) -> bool:
        return self.founder.get("control") in NUMERIC_FOUNDER_CONTROLS

    @property
    def founder_price(self) -> bool:
        """Price's founder side (call 53): a range and a period, code's input and code's question."""
        return self.founder.get("control") == PRICE_FOUNDER_CONTROL

    @property
    def founder_cost(self) -> bool:
        """Existing sacrifice's founder side (074): a cost estimate rendered and framed by code."""
        return self.founder.get("control") == COST_FOUNDER_CONTROL

    @property
    def derived(self) -> bool:
        """Ability to pay's founder side (074): written by code, asked of no one, in no model job."""
        return self.founder.get("control") == DERIVED_FOUNDER_CONTROL

    @property
    def b2b_link_only(self) -> bool:
        """Calibrated on every persona, asked on the decision-maker's link only (074)."""
        return self.respondent.get("b2b_link_only") is True

    @property
    def respondent_code_written(self) -> bool:
        """An item whose question and options are wholly code's (call 53: the Price ladder)."""
        return self.respondent.get("control") in CODE_WRITTEN_RESPONDENT_CONTROLS

    @property
    def benefit_first(self) -> bool:
        """Relative advantage since keel-cloud 085: read by `benefit_first`, asked by `benefit_with_advantages`."""
        return self.answers.get("compare_rule") == BENEFIT_RULE

    @property
    def respondent_numeric(self) -> bool:
        return self.respondent.get("control") in NUMERIC_RESPONDENT_CONTROLS + (GATE_CONTROL,)

    @property
    def founder_code_framed(self) -> bool:
        """Questions code composes whole (calls 53, 61, 67): Price and Existing sacrifice (and Ability to pay,
        which is asked of no one). The model owes these no question text, and no options."""
        return self.founder_price or self.founder_cost or self.derived

    @property
    def status_vocabulary(self) -> list:
        return list(self.answers.get("status_vocabulary") or [])


@dataclass(frozen=True)
class Registry:
    dimensions: tuple
    common: dict = field(default_factory=dict)
    version: object = None
    source: str = ""

    def keys(self) -> list[str]:
        return [d.key for d in self.dimensions]

    def by_key(self, key: str) -> Dimension:
        for dimension in self.dimensions:
            if dimension.key == key:
                return dimension
        raise KeyError(key)

    def has(self, key: str) -> bool:
        return any(d.key == key for d in self.dimensions)

    def slice(self, vector: str) -> list[Dimension]:
        """The calibration job's input for one vector: its dimensions, in `order`."""
        return sorted((d for d in self.dimensions if d.vector == vector), key=lambda d: d.order)

    def part_of(self, key: str):
        return self.by_key(key).part

    def codes_of(self, key: str):
        return self.by_key(key).codes

    def fixed_respondent_codes(self, key: str) -> list[str]:
        return list(FIXED_RESPONDENT_CODES.get(key, ()))

    def deal_breakers(self, vector: str) -> list[str]:
        return [d.key for d in self.slice(vector) if d.weight == "DEAL_BREAKER"]

    def b2b_only(self) -> list[str]:
        return [d.key for d in self.dimensions if d.b2b_only]

    def b2b_link_only(self) -> list[str]:
        return [d.key for d in self.dimensions if d.b2b_link_only]

    def calibrated(self, b2b: bool) -> list[Dimension]:
        """The entries a project calibrates (calls 47, 59; keel-cloud 074 `calibrated(b2b)`): every
        entry, less the `b2b_only` one when the persona is not B2B -- in vector order, then
        `order`. Twelve on B2C, thirteen on B2B."""
        return [d for vector in VECTORS for d in self.slice(vector) if b2b or not d.b2b_only]

    def calibrated_keys(self, b2b: bool) -> list[str]:
        return [d.key for d in self.calibrated(b2b)]

    def calibrated_slice(self, vector: str, b2b: bool) -> list[Dimension]:
        """One vector's calibrated entries: the standings' and the verdicts' set."""
        return [d for d in self.slice(vector) if b2b or not d.b2b_only]

    def answered(self, b2b: bool) -> list[Dimension]:
        """keel-cloud 074 `answered(vector, b2b)`: the calibrated entries less the `derived` one, which
        code writes (call 59). Eleven on B2C, twelve on B2B."""
        return [d for d in self.calibrated(b2b) if not d.derived]

    def answered_slice(self, vector: str, b2b: bool) -> list[Dimension]:
        """One vector's answered entries: the calibration job's input, and its coverage and validity
        denominator (call 61)."""
        return [d for d in self.calibrated_slice(vector, b2b) if not d.derived]

    def asked(self, link: str, b2b: bool) -> list[Dimension]:
        """The entries one link asks (keel-cloud 074 `asked(link, b2b)`): on `PRIMARY` every entry
        less the `b2b_only` and `b2b_link_only` ones; on `COMMERCIAL_B2B` the commercial slice whole,
        and only on a B2B persona."""
        if link == LINK_B2B:
            return self.slice("COMMERCIAL") if b2b else []
        return [d for vector in VECTORS for d in self.slice(vector)
                if not d.b2b_only and not d.b2b_link_only]

    @staticmethod
    def link_of(part: int, b2b: bool) -> str:
        """The link a part is asked on (keel-cloud `EvidencePlan`, decision 26): part 3 of a B2B
        study is the decision-maker's, never the primary link's."""
        return LINK_B2B if (b2b and part == 3) else LINK_PRIMARY

    def plan_keys(self, part: int, founder_calibration: dict, link: str = LINK_PRIMARY,
                  b2b: bool = False) -> list[str]:
        """The respondent items of one part on one link (calls 30, 47): asked on that link, in this
        part, and not left out by the founder -- in vector order, then `order`. What production's
        `EVIDENCE_PLAN` hands the job, and the respondent denominator of `dimension_coverage`."""
        out = []
        for d in self.asked(link, b2b):
            if d.part != part:
                continue
            answer = (founder_calibration or {}).get(d.key) or {}
            if answer.get("unsure"):
                continue
            out.append(d.key)
        return out


# ------------------------------------------------------------------------------------- reading

def _dimension(raw: dict) -> Dimension:
    return Dimension(
        key=raw.get("key"), vector=raw.get("vector"), order=raw.get("order"),
        name=raw.get("name") or "", meaning=raw.get("meaning") or "",
        weight=raw.get("weight"), founder=dict(raw.get("founder") or {}),
        respondent=dict(raw.get("respondent") or {}), answers=dict(raw.get("answers") or {}),
        left_out=dict(raw.get("left_out") or {}), lullaby=dict(raw.get("lullaby") or {}),
        b2b_only=raw.get("b2b_only") is True)


def from_document(document, *, source: str = "", check: bool = True) -> Registry:
    """A registry from its exported shape -- `{version?, common, dimensions: [...]}` -- checked
    against the eight invariants unless `check` is false (the invariant tests ask for the
    unchecked object to show each refusal on its own)."""
    if not isinstance(document, dict) or not isinstance(document.get("dimensions"), list):
        raise RegistryUnavailable(
            f"{source or 'the registry'} is not a dimension registry: expected an object with a "
            "`dimensions` list (registry-schema.draft.md)")
    registry = Registry(dimensions=tuple(_dimension(d) for d in document["dimensions"]),
                        common=dict(document.get("common") or {}),
                        version=document.get("version"), source=source)
    if check:
        faults = check_invariants(registry)
        if faults:
            raise RegistryUnavailable(
                f"{source or 'the registry'} fails registry-schema.draft.md's invariants -- "
                "refusing to build a case against it:\n  " + "\n  ".join(faults))
    return registry


def load(path, *, check: bool = True) -> Registry:
    """`dimension-registry.json` (or a YAML fixture of the same shape), read whole."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegistryUnavailable(f"could not read the registry at {path}: {exc}") from exc
    if path.suffix in (".yaml", ".yml"):
        import yaml                                       # noqa: PLC0415 - fixtures only
        document = yaml.safe_load(text)
    else:
        try:
            document = json.loads(text)
        except ValueError as exc:
            raise RegistryUnavailable(f"{path} is not JSON: {exc}") from exc
    return from_document(document, source=str(path), check=check)


# ---------------------------------------------------------------------------------- invariants

_PROPORTION_BIN = re.compile(r"^p_(\d+)_(\d+)$")
_BAND = re.compile(r"^(\d+)-(\d+)$")
_OPEN_BAND = re.compile(r"^(\d+)\+$")


def _bins_contiguous(bins) -> bool:
    """Ordered integer edges stepping by one, or contiguous string bands (`0-5`, `5-10`, `20+`)."""
    if not isinstance(bins, list) or len(bins) < 2:
        return False
    if all(isinstance(b, int) for b in bins):
        return all(b2 > b1 for b1, b2 in zip(bins, bins[1:]))
    previous_upper = None
    for index, band in enumerate(bins):
        band = str(band)
        match = _BAND.match(band)
        if match:
            lower, upper = int(match.group(1)), int(match.group(2))
            if upper <= lower or (previous_upper is not None and lower != previous_upper):
                return False
            previous_upper = upper
            continue
        match = _OPEN_BAND.match(band)
        if match and index == len(bins) - 1:
            return previous_upper is None or int(match.group(1)) == previous_upper
        return False
    return True


def _proportion_bins_contiguous(codes: list) -> bool:
    edges = []
    for code in codes:
        match = _PROPORTION_BIN.match(str(code))
        if not match:
            return True                       # not a proportion bin list; nothing to check
        edges.append((int(match.group(1)), int(match.group(2))))
    return all(a[1] == b[0] for a, b in zip(edges, edges[1:])) and edges[0][0] == 0 \
        and edges[-1][1] == 100


def check_invariants(registry: Registry) -> list[str]:
    """Every invariant the registry fails, one sentence each naming the invariant and the key."""
    faults = []
    dims = list(registry.dimensions)
    keys = [d.key for d in dims]

    total = sum(PER_VECTOR.values())
    split = " / ".join(str(n) for n in PER_VECTOR.values())

    # 0. The shape v10 reads: `asked_in_v1` is gone (call 46) -- refused as unknown-shaped, never
    #    ignored, because a registry still carrying it is not the one this rubric was written for.
    for d in dims:
        if "asked_in_v1" in d.respondent:
            faults.append(f"unknown shape: {d.key} carries respondent.asked_in_v1, which keel-cloud "
                          "071 removed (every entry is asked; b2b_only marks the B2B pair) -- "
                          "judgement call 46")

    # 1. 13 keys, 4 / 3 / 6, `order` contiguous from 1 within each vector (call 50).
    if len(keys) != total or len(set(keys)) != len(keys):
        faults.append(f"invariant 1 ({total} unique keys): the registry has {len(set(keys))} "
                      f"unique of {len(keys)}")
    for vector, count in PER_VECTOR.items():
        in_vector = [d for d in dims if d.vector == vector]
        orders = sorted(d.order for d in in_vector if isinstance(d.order, int))
        if len(in_vector) != count:
            faults.append(f"invariant 1 ({split}): {vector} has {len(in_vector)} dimensions")
        if orders != list(range(1, len(in_vector) + 1)):
            bad = [d.key for d in in_vector
                   if not isinstance(d.order, int) or not 1 <= d.order <= len(in_vector)]
            faults.append(f"invariant 1 (order contiguous from 1): {vector}'s orders are "
                          f"{orders}" + (f"; out of place: {', '.join(bad)}" if bad else ""))
    unknown = [d.key for d in dims if d.vector not in VECTORS]
    if unknown:
        faults.append(f"invariant 1 (vectors): {', '.join(unknown)} name no vector")

    # 2. The nine deal-breakers, exactly.
    expected = {k for keys_ in DEAL_BREAKERS.values() for k in keys_}
    actual = {d.key for d in dims if d.weight == "DEAL_BREAKER"}
    for key in sorted(actual - expected):
        faults.append(f"invariant 2 (the nine deal-breakers): {key} is a DEAL_BREAKER and the "
                      "schema does not make it one")
    for key in sorted(expected - actual):
        faults.append(f"invariant 2 (the nine deal-breakers): {key} is not a DEAL_BREAKER")
    for d in dims:
        if d.weight not in ("DEAL_BREAKER", "SHAPES"):
            faults.append(f"invariant 2 (weights): {d.key} weighs {d.weight!r}")

    # 3. `b2b_only` on exactly Purchase friction, `b2b_link_only` on exactly Ability to pay (074);
    #    every entry asked in its own vector's part, 4 / 3 / 6.
    flagged = {d.key for d in dims if d.b2b_only}
    for key in sorted(flagged - set(B2B_ONLY)):
        faults.append(f"invariant 3 (b2b_only on exactly {', '.join(B2B_ONLY)}): {key} is "
                      "b2b_only and the schema does not make it so")
    for key in sorted(set(B2B_ONLY) - flagged):
        faults.append(f"invariant 3 (b2b_only on exactly {', '.join(B2B_ONLY)}): {key} is not "
                      "b2b_only")
    link_flagged = {d.key for d in dims if d.b2b_link_only}
    for key in sorted(link_flagged - set(B2B_LINK_ONLY)):
        faults.append(f"invariant 3 (b2b_link_only on exactly {', '.join(B2B_LINK_ONLY)}): {key} is "
                      "b2b_link_only and the schema does not make it so")
    for key in sorted(set(B2B_LINK_ONLY) - link_flagged):
        faults.append(f"invariant 3 (b2b_link_only on exactly {', '.join(B2B_LINK_ONLY)}): {key} is "
                      "not b2b_link_only")
    parts = " / ".join(str(n) for n in PER_PART.values())
    for part, count in PER_PART.items():
        in_part = [d.key for d in dims if d.part == part]
        if len(in_part) != count:
            faults.append(f"invariant 3 (parts {parts}): part {part} has {len(in_part)}")
    for d in dims:
        if d.part not in PER_PART:
            faults.append(f"invariant 3 (parts): {d.key} is asked with part {d.part!r}; every "
                          "entry is asked")
        elif PART_VECTOR[d.part] != d.vector:
            faults.append(f"invariant 3 (parts): {d.key} is asked in part {d.part}, which asks "
                          f"{PART_VECTOR[d.part]}")

    # 4. `{value}` exactly once in every belief template.
    for d in dims:
        template = str(d.founder.get("belief_template") or "")
        if template.count("{value}") != 1:
            faults.append(f"invariant 4 ({{value}} exactly once): {d.key}'s belief template "
                          f"carries it {template.count('{value}')} times")

    # 5. Fixed codes 4-6, none repeated; numeric bins contiguous and ordered; a `price_range`
    #    entry's periods exactly the five of `Period.wires` (keel-cloud 074, `PriceLadder.PERIODS`; `one_off` was 073's).
    for d in dims:
        codes = d.fixed_codes
        if codes is not None:
            if not 4 <= len(codes) <= 6:
                faults.append(f"invariant 5 (4-6 codes): {d.key} has {len(codes)}")
            if len(set(codes)) != len(codes):
                repeated = sorted({c for c in codes if codes.count(c) > 1})
                faults.append(f"invariant 5 (no code repeated): {d.key} repeats "
                              f"{', '.join(repeated)}")
            if not _proportion_bins_contiguous(codes):
                faults.append(f"invariant 5 (contiguous bins): {d.key}'s proportion bins have a "
                              "gap")
        elif d.codes is not None and d.codes != "model_written":
            faults.append(f"invariant 5 (codes): {d.key}'s codes are {d.codes!r}")
        if d.normalized.get("kind") == PRICE_FOUNDER_CONTROL or d.founder_price:
            periods = d.normalized.get("periods")
            if list(periods or []) != list(PRICE_PERIODS):
                faults.append(f"invariant 5 (price periods): {d.key}'s periods are {periods!r}, not "
                              f"{list(PRICE_PERIODS)}")
        # keel-cloud 074: a cost names the five periods and the two modes; an entry is derived on both
        # sides or neither, is read by cost_covers_price, and is derived from registry keys.
        if d.normalized.get("kind") == "cost" or d.founder_cost:
            periods, modes = d.normalized.get("periods"), d.normalized.get("modes")
            if list(periods or []) != list(PERIODS):
                faults.append(f"invariant 5 (cost periods): {d.key}'s periods are {periods!r}, not "
                              f"{list(PERIODS)}")
            if list(modes or []) != list(COST_MODES):
                faults.append(f"invariant 5 (cost modes): {d.key}'s modes are {modes!r}, not "
                              f"{list(COST_MODES)}")
            if "code_rule" in d.normalized:        # keel-cloud 077: no kinds of cost anywhere
                faults.append(f"invariant 5 (a cost has no kinds): {d.key} carries a code_rule; "
                              "keel-cloud 077 removed the respondent's kinds")
            if d.respondent.get("control") != COST_TOTAL_CONTROL:
                faults.append(f"invariant 5 (one total): {d.key}'s respondent control is "
                              f"{d.respondent.get('control')!r}, not {COST_TOTAL_CONTROL!r}")
        derived_kind = d.normalized.get("kind") == "price_cost_ratio"
        if derived_kind != d.derived:
            faults.append(f"invariant 5 (derived on both sides): {d.key} is derived on one side only: "
                          f"control {d.founder.get('control')!r}, normalized "
                          f"{d.normalized.get('kind')!r}")
        if derived_kind:
            sources = list(d.normalized.get("from") or [])
            if not sources or not all(k in keys for k in sources):
                faults.append(f"invariant 5 (derived from keys): {d.key} is derived from {sources!r}, "
                              "which are not all registry keys")
            if d.answers.get("compare_rule") != DERIVED_COMPARE_RULE:
                faults.append(f"invariant 5 (derived is cost_covers_price): {d.key} is derived and "
                              f"read by {d.answers.get('compare_rule')!r}")
        # keel-cloud 085: the benefit rule and the benefit control go together, the founder ticks a set.
        if d.benefit_first != (d.respondent.get("control") == BENEFIT_CONTROL):
            faults.append(f"invariant 5 (benefit on both sides): {d.key} is read by "
                          f"{d.answers.get('compare_rule')!r} on a {d.respondent.get('control')!r} control")
        if d.benefit_first and d.founder.get("control") != BENEFIT_FOUNDER_CONTROL:
            faults.append(f"invariant 5 (the founder ticks advantages): {d.key}'s founder control is "
                          f"{d.founder.get('control')!r}, not {BENEFIT_FOUNDER_CONTROL!r}")
        bins = d.normalized.get("bins")
        if bins is not None and not _bins_contiguous(bins):
            faults.append(f"invariant 5 (contiguous bins): {d.key}'s bins {bins} are not "
                          "contiguous and ordered")

    # 6. `answers.shape == interval` iff the respondent control yields a number (074: Existing
    #    sacrifice's `cost_total` since 077; `branch_pick_amounts` before).
    for d in dims:
        numeric = d.respondent.get("control") in NUMBER_YIELDING_CONTROLS
        shape = d.answers.get("shape")
        if numeric != (shape == "interval"):
            faults.append(f"invariant 6 (interval iff numeric control): {d.key} answers as "
                          f"{shape!r} on a {d.respondent.get('control')!r} control")

    # 7. The gate is problem.prevalence's, and nobody else's.
    gates = [d.key for d in dims if d.respondent.get("control") == GATE_CONTROL]
    if gates != [GATE_KEY]:
        faults.append(f"invariant 7 (the one gate): gate_yes_no is on "
                      f"{', '.join(gates) or 'no dimension'}, and must be on {GATE_KEY} alone")

    # 8. Every deal-breaker can fail: its status vocabulary reaches NOT_HOLDING_UP (keel-cloud 071).
    for d in dims:
        if d.weight == "DEAL_BREAKER" and "NOT_HOLDING_UP" not in d.status_vocabulary:
            faults.append(f"invariant 8 (a deal-breaker can fail): {d.key} is a DEAL_BREAKER whose "
                          "status vocabulary never reaches NOT_HOLDING_UP")
    return faults
