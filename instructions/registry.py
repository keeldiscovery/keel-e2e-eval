"""keel-cloud's dimension registry, read from the export and checked before a case is built
(spec 029 FR-021, data-model §1, research R4; registry 4 since keel-cloud 087 and spec 040).

The registry is the **golden** for `dimension_coverage` and `option_validity` (judgement calls 30
and 31): every control, code, list bound, escape, fixed answer, belief template and plan part a
scorer checks a result against. keel-cloud 058 exports it as `dimension-registry.json` beside
`model-routing.json`; `instructions/contract.read` loads it through `from_document` here. Nothing in
this module is a copy of the cloud's registry -- the fixture under `tests/fixtures/registry/` is a
hand-sized slice of keel-cloud 087's export.

**Registry 4** (keel-cloud 087, `design-2026-10-14.md` §2; spec 040, judgement call 77): **all thirteen
dimensions decide** (D3) -- there is no weight, no DEAL_BREAKER and no SHAPES anywhere, and a registry
still carrying `weight`, `respondent.chips`, `common.chips`, `common.something_else` or
`answers.status_vocabulary` is refused as unknown-shaped (invariant 0), never read. Seven dimensions are
founder lists (`rival_list`, `scale_lines`, `item_list`, `benefit_list`, `role_list`, `one_step`) whose
`founder.saves` bounds what the lock stores; every respondent item carries **one escape at most**
(`respondent.escape {code, label, counts}`), and the five reshaped ones a registry-fixed answer set
(`respondent.fixed_answers`, `supports`, `conditional`). Every respondent word is code's (keel-cloud
088): the model writes the gate's `event` clause and nothing else on the respondent side.

**The eight invariants are this repository's to check** (keel-cloud `registry-schema.md`
§Invariants; spec 030 judgement call 46), because a mark of 1.00 is honest only against a registry
that is itself well formed. At registry 4 (087 FR-002): 1 keys (13, 4 / 3 / 6); 2 one escape at most,
only Importance's counts against, none on the gate or Commitment; 3 b2b (Purchase friction `b2b_only`,
Ability to pay `b2b_link_only`); 4 `{value}` exactly once in every belief template but the
`benefit_list`'s, which has none; 5 codes (Prevalence's fifths, a list control's `saves`, fixed answers
unique, the cost / price / derived / benefit shapes); 6 interval iff numeric control; 7 one gate; 8 every
respondent option set fits the spoken guidelines -- at most five fixed answers, each at most nine words.
A registry that fails one is a **refusal to start** naming the invariant and the key.

**What a project calibrates, answers and asks is read here, never typed by a scorer** (calls 46,
47, 59): `calibrated(b2b)` is every entry less the `b2b_only` one when the persona is not B2B (twelve
on B2C, thirteen on B2B); `answered(b2b)` is that less the `derived` one, which code writes -- what
the calibration job writes for (eleven / twelve); and `plan_keys(part, founder_calibration, link,
b2b)` is what one link asks in one part.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: Invariant 1: 13 keys, 4 / 3 / 6.
PER_VECTOR = {"PROBLEM": 4, "SOLUTION": 3, "COMMERCIAL": 6}

#: Invariant 3: `b2b_only` on exactly Purchase friction, `b2b_link_only` on exactly Ability to pay, and
#: every entry asked in the part of its own vector -- 4 / 3 / 6 entries a part.
B2B_ONLY = ("commercial.purchase_friction",)
B2B_LINK_ONLY = ("commercial.ability_to_pay",)
PER_PART = {1: 4, 2: 3, 3: 6}
PART_VECTOR = {1: "PROBLEM", 2: "SOLUTION", 3: "COMMERCIAL"}

#: The two links a person answers on (keel-cloud `RespondentLink`).
LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"

#: Invariant 7: the one gate.
GATE_KEY = "problem.prevalence"
GATE_CONTROL = "gate_yes_no"
FREQUENCY_KEY = "problem.frequency"
IMPORTANCE_KEY = "problem.importance"
CURRENT_SOLUTION_KEY = "problem.current_solution_satisfaction"
COMPATIBILITY_KEY = "solution.compatibility"
ADOPTION_KEY = "solution.adoption_friction"
BUYER_KEY = "commercial.buyer_payer_alignment"
PURCHASE_FRICTION_KEY = "commercial.purchase_friction"
COMMITMENT_KEY = "commercial.commitment"

#: The respondent controls whose answer is a number (`answers.shape == interval`, invariant 6):
#: Frequency's 0-to-7 control and the number it becomes on a longer window, and Existing sacrifice's
#: one total (keel-cloud 077).
NUMERIC_RESPONDENT_CONTROLS = ("segmented_0_to_7", "number_with_unit")
COST_TOTAL_CONTROL = "cost_total"
#: Registry decision 24 (keel-cloud 115, spec 064 FR-1): the stranger's cost is one value box in the founder's own unit
#: and period (`interval`); a project whose cost was stated before the chain keeps `cost_total`.
VALUE_BOX_CONTROL = "value_box"
NUMBER_YIELDING_CONTROLS = NUMERIC_RESPONDENT_CONTROLS + (COST_TOTAL_CONTROL, VALUE_BOX_CONTROL)

#: keel-cloud 087's `FounderControl`: the founder lists (D4, D5, D7) beside the five unchanged controls.
LIST_FOUNDER_CONTROLS = ("rival_list", "scale_lines", "item_list", "benefit_list", "role_list", "one_step")
FOUNDER_CONTROLS = ("single_choice", "numeric_interval") + LIST_FOUNDER_CONTROLS + (
    "cost_estimate", "price_range", "derived")
#: keel-cloud 087's `RespondentControl`.
RESPONDENT_CONTROLS = ("gate_yes_no", "segmented_0_to_7", "number_with_unit", "single_choice",
                       "single_choice_5", "pick_two", "fixed_four", "fixed_three", "cost_total",
                       "price_ladder", "benefit_with_advantages", "value_box")
#: The controls whose answers are the registry's fixed set (`respondent.fixed_answers`).
FIXED_ANSWER_CONTROLS = ("fixed_four", "fixed_three")
#: keel-cloud 087's `CompareRule`.
COMPARE_RULES = ("proportion_from_gate", "interval_contains_median", "share_in_picks", "below_line",
                 "fixed_last_two_against", "benefit_first", "ordinal_band", "cost_covers_price",
                 "first_supports", "caution_turned")
#: An escape is apart, or (Importance's alone) counted against (087 FR-004).
ESCAPE_COUNTS = ("apart", "against")

#: Invariant 8 (087 FR-002, the spoken guidelines §2): a fixed answer set is at most five answers, each
#: at most nine words.
MAX_FIXED_ANSWERS = 5
MAX_ANSWER_WORDS = 9

#: The founder-side numeric control: no options, a spec the registry owns.
NUMERIC_FOUNDER_CONTROLS = ("numeric_interval",)

#: Price (keel-cloud 073 / 074): the founder states a range, rendered by code over the cost's period.
PRICE_KEY = "commercial.price"
PRICE_FOUNDER_CONTROL = "price_range"
#: keel-cloud 074's `Period.wires()`: the five periods a cost is stated over, and a price is fixed to.
PERIODS = ("day", "week", "month", "quarter", "year")
PRICE_PERIODS = PERIODS
#: keel-cloud 115 (registry decision 24): the chain's six periods -- the five and `each` -- on the cost and the price.
CHAIN_PERIODS = PERIODS + ("each",)
#: The cost estimate (074): the founder's control on Existing sacrifice, its modes.
COST_FOUNDER_CONTROL = "cost_estimate"
COST_MODES = ("AMOUNT", "HOURS")
#: keel-cloud 115 (registry decision 24): the chain's three ways a cost is put -- money, time, a rate.
CHAIN_COST_MODES = ("MONEY", "HOURS", "RATE")
#: Ability to pay (074): derived by code from the cost and the price, read by `cost_covers_price`.
ABILITY_KEY = "commercial.ability_to_pay"
DERIVED_FOUNDER_CONTROL = "derived"
DERIVED_COMPARE_RULE = "cost_covers_price"
#: `AbilityToPay`'s four bands (with decision 2, 2026-10-10).
ABILITY_BANDS = ("small_share", "mostly_from_spend", "some_from_spend", "new_money")
#: Relative advantage, benefit first (keel-cloud 085; 087 makes the founder's ticks a `benefit_list`).
BENEFIT_KEY = "solution.relative_advantage"
BENEFIT_CONTROL = "benefit_with_advantages"
BENEFIT_RULE = "benefit_first"
BENEFIT_FOUNDER_CONTROL = "benefit_list"
BENEFIT_CODES = ("positive", "neutral", "negative")
BENEFIT_MAX_TICKS = 4
#: Existing sacrifice: its question names no offer (keel-cloud 072 D-2).
SACRIFICE_KEY = "commercial.existing_sacrifice"

#: Invariant 0: the registry-3 shape keel-cloud 087 removed (D3, D2) -- refused by name, never ignored.
GONE_ENTRY_KEYS = ("weight",)
GONE_RESPONDENT_KEYS = ("chips", "asked_in_v1", "codes")
GONE_ANSWER_KEYS = ("status_vocabulary",)
GONE_COMMON_KEYS = ("chips", "something_else")


#: keel-cloud 058 (2026-10-07): the registry carries `{window}` / `{window_unit}` placeholders, the
#: project's recall window, filled by code. Founder decision 42 made the window COUNT + UNIT; D13
#: (2026-10-14, keel-cloud 087) took the one-unit window away: `CYCLES` and `SHIFTS` are gone and a
#: window counts at least two.
_WINDOW_UNITS = {
    # `RecallWindow.Unit`'s order and words.
    "NIGHTS": ("night", "nights"), "DAYS": ("day", "days"),
    "WORKING_DAYS": ("working day", "working days"), "WEEKS": ("week", "weeks"),
    "MONTHS": ("month", "months"),
}
_LEGACY_WINDOWS = {"SEVEN_NIGHTS": (7, "NIGHTS"), "SEVEN_DAYS": (7, "DAYS"),
                   "FIVE_WORKING_DAYS": (5, "WORKING_DAYS"), "THIRTY_DAYS": (30, "DAYS")}
#: D13: the smallest count a recall window takes.
WINDOW_MIN_COUNT = 2


@dataclass(frozen=True)
class RecallWindow:
    """keel-cloud's `domain.vectors.RecallWindow`, mirrored: the words `{window}` and `{window_unit}`
    are filled with. Code fills both; a model never does. Since D13 (keel-cloud 087) a window counts at
    least two of nights / days / working days / weeks / months -- so Frequency is asked on every
    project and there is no one-unit branch anywhere (DRIFT #74 closed by construction)."""

    count: int
    unit: str

    def __post_init__(self):
        if self.unit not in _WINDOW_UNITS:
            raise ValueError(f"{self.unit!r} is not a recall-window unit; use one of "
                             f"{list(_WINDOW_UNITS)} (CYCLES and SHIFTS went with D13)")
        if not isinstance(self.count, int) or isinstance(self.count, bool) \
                or self.count < WINDOW_MIN_COUNT:
            raise ValueError(f"a recall window counts at least {WINDOW_MIN_COUNT} "
                             f"{_WINDOW_UNITS[self.unit][1]} (D13: no one-unit window), and this was "
                             f"{self.count!r}")

    @property
    def singular(self) -> str:
        return _WINDOW_UNITS[self.unit][0]

    @property
    def plural(self) -> str:
        return _WINDOW_UNITS[self.unit][1]

    def words(self) -> str:
        """`{window}`: "the last 7 nights"."""
        return f"the last {self.count} {self.plural}"

    def unit_words(self) -> str:
        """`{window_unit}` -- Java's `unit()`: Frequency's unit, "nights out of 7"."""
        return f"{self.plural} out of {self.count}"

    def fill(self, text):
        return None if text is None else \
            text.replace("{window_unit}", self.unit_words()).replace("{window}", self.words())

    def to_map(self) -> dict:
        """`{count, unit}`, as the wire and the job carry it."""
        return {"count": self.count, "unit": self.unit}

    @classmethod
    def read(cls, raw):
        """`RecallWindow.read`: a `{count, unit}` map, or a legacy multi-unit name (upcast); `None`
        reads `None`, anything else -- `LAST_CYCLE` among it -- is refused."""
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


def words(text) -> int:
    """`DimensionRegistry.words` / `SpokenForm.words`: whitespace-separated words."""
    return len(str(text or "").split())


class RegistryUnavailable(RuntimeError):
    """The registry could not be read, or it fails an invariant -- a reason to stop, never a score."""


@dataclass(frozen=True)
class Dimension:
    key: str
    vector: str
    order: int
    name: str
    meaning: str
    founder: dict
    respondent: dict
    answers: dict
    left_out: dict = field(default_factory=dict)
    lullaby: dict = field(default_factory=dict)
    #: keel-cloud 071: calibrated and asked only when the persona is B2B (074: Purchase friction alone).
    b2b_only: bool = False
    #: The entry's own top-level keys as exported, so invariant 0 can name a removed one.
    raw_keys: tuple = ()

    @property
    def normalized(self) -> dict:
        return self.founder.get("normalized") or {}

    @property
    def codes(self):
        """The fixed founder codes (Prevalence's fifths), or `None`."""
        return self.normalized.get("codes")

    @property
    def fixed_codes(self) -> list | None:
        codes = self.codes
        return list(codes) if isinstance(codes, list) else None

    @property
    def part(self):
        return self.respondent.get("part")

    @property
    def founder_control(self):
        return self.founder.get("control")

    @property
    def respondent_control(self):
        return self.respondent.get("control")

    @property
    def founder_numeric(self) -> bool:
        return self.founder_control in NUMERIC_FOUNDER_CONTROLS

    @property
    def founder_price(self) -> bool:
        return self.founder_control == PRICE_FOUNDER_CONTROL

    @property
    def founder_cost(self) -> bool:
        return self.founder_control == COST_FOUNDER_CONTROL

    @property
    def derived(self) -> bool:
        """Ability to pay's founder side (074): written by code, asked of no one, in no model job."""
        return self.founder_control == DERIVED_FOUNDER_CONTROL

    @property
    def founder_list(self) -> bool:
        """A founder list (087 D5, D7): the model drafts it, the founder edits it, the lock stores it."""
        return self.founder_control in LIST_FOUNDER_CONTROLS

    @property
    def saves(self) -> dict:
        """`founder.saves` -- `{min_items, max_items, max_words, picked, phrase?, own_first?, asked?,
        fixed_first?}` -- on a list dimension, `{}` elsewhere."""
        return dict(self.founder.get("saves") or {})

    @property
    def b2b_link_only(self) -> bool:
        """Calibrated on every persona, asked on the decision-maker's link only (074)."""
        return self.respondent.get("b2b_link_only") is True

    @property
    def escape(self) -> dict | None:
        """The one escape (087 FR-001; the spoken guidelines §5), `{code, label, counts}`, or `None`."""
        escape = self.respondent.get("escape")
        return dict(escape) if isinstance(escape, dict) else None

    @property
    def fixed_answers(self) -> list:
        """`respondent.fixed_answers` -- `[{code, label}]` -- or `[]`."""
        return [dict(a) for a in self.respondent.get("fixed_answers") or [] if isinstance(a, dict)]

    @property
    def fixed_answer_codes(self) -> list:
        return [a.get("code") for a in self.fixed_answers]

    @property
    def benefit_first(self) -> bool:
        """Relative advantage since keel-cloud 085: read by `benefit_first`, asked by `benefit_with_advantages`."""
        return self.answers.get("compare_rule") == BENEFIT_RULE

    @property
    def compare_rule(self):
        return self.answers.get("compare_rule")


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
        """One vector's dimensions, in `order`."""
        return sorted((d for d in self.dimensions if d.vector == vector), key=lambda d: d.order)

    def part_of(self, key: str):
        return self.by_key(key).part

    def b2b_only(self) -> list[str]:
        return [d.key for d in self.dimensions if d.b2b_only]

    def b2b_link_only(self) -> list[str]:
        return [d.key for d in self.dimensions if d.b2b_link_only]

    def calibrated(self, b2b: bool) -> list[Dimension]:
        """The entries a project calibrates (calls 47, 59): every entry, less the `b2b_only` one when
        the persona is not B2B -- in vector order, then `order`. Twelve on B2C, thirteen on B2B. **All of
        them decide** (D3): a vector's verdict is the worst of its calibrated dimensions."""
        return [d for vector in VECTORS for d in self.slice(vector) if b2b or not d.b2b_only]

    def calibrated_keys(self, b2b: bool) -> list[str]:
        return [d.key for d in self.calibrated(b2b)]

    def calibrated_slice(self, vector: str, b2b: bool) -> list[Dimension]:
        """One vector's calibrated entries: the standings' and the verdict's set."""
        return [d for d in self.slice(vector) if b2b or not d.b2b_only]

    def answered(self, b2b: bool) -> list[Dimension]:
        """keel-cloud 074 `answered(vector, b2b)`: the calibrated entries less the `derived` one."""
        return [d for d in self.calibrated(b2b) if not d.derived]

    def answered_slice(self, vector: str, b2b: bool) -> list[Dimension]:
        """One vector's answered entries: the calibration job's slice, and its coverage denominator."""
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
        """The link a part is asked on: part 3 of a B2B study is the decision-maker's."""
        return LINK_B2B if (b2b and part == 3) else LINK_PRIMARY

    def plan_keys(self, part: int, founder_calibration: dict, link: str = LINK_PRIMARY,
                  b2b: bool = False) -> list[str]:
        """The respondent items of one part on one link (calls 30, 47): asked on that link, in this
        part, and not left out by the founder -- in vector order, then `order`.

        Spec 064 FR-3 (keel-cloud 115 `EvidencePlan.asked`): on a study in the commercial chain a price FREE to them
        asks no price item, and a same-person study whose cost and price share no base (the `budget` reading) asks the
        consumer budget item on the primary link, in Ability to pay's registry place; part 3 of a B2B study stays the
        decision-maker's link as before."""
        from . import chain as chain_mod                                    # noqa: PLC0415
        calibration = founder_calibration or {}
        cost = None if (calibration.get(SACRIFICE_KEY) or {}).get("unsure") else \
            (calibration.get(SACRIFICE_KEY) or {}).get("answer")
        price = None if (calibration.get(PRICE_KEY) or {}).get("unsure") else \
            (calibration.get(PRICE_KEY) or {}).get("answer")
        in_chain = chain_mod.cost_in_chain(cost) and chain_mod.price_in_chain(price)
        consumer_budget = in_chain and not b2b and link == LINK_PRIMARY \
            and chain_mod.reading(cost, price) == "budget"
        dims = self.asked(link, b2b)
        if consumer_budget:
            dims = [d for vector in VECTORS for d in self.slice(vector)
                    if not d.b2b_only and (not d.b2b_link_only or d.key == ABILITY_KEY)]
        out = []
        for d in dims:
            if d.part != part:
                continue
            answer = calibration.get(d.key) or {}
            if answer.get("unsure"):
                continue
            if d.key == PRICE_KEY and in_chain and (price or {}).get("shape") == "FREE":
                continue
            out.append(d.key)
        return out


# ------------------------------------------------------------------------------------- reading

def _dimension(raw: dict) -> Dimension:
    return Dimension(
        key=raw.get("key"), vector=raw.get("vector"), order=raw.get("order"),
        name=raw.get("name") or "", meaning=raw.get("meaning") or "",
        founder=dict(raw.get("founder") or {}),
        respondent=dict(raw.get("respondent") or {}), answers=dict(raw.get("answers") or {}),
        left_out=dict(raw.get("left_out") or {}), lullaby=dict(raw.get("lullaby") or {}),
        b2b_only=raw.get("b2b_only") is True, raw_keys=tuple(raw))


def from_document(document, *, source: str = "", check: bool = True) -> Registry:
    """A registry from its exported shape -- `{version?, common, dimensions: [...]}` -- checked
    against the eight invariants unless `check` is false."""
    if not isinstance(document, dict) or not isinstance(document.get("dimensions"), list):
        raise RegistryUnavailable(
            f"{source or 'the registry'} is not a dimension registry: expected an object with a "
            "`dimensions` list (registry-schema.md)")
    registry = Registry(dimensions=tuple(_dimension(d) for d in document["dimensions"]),
                        common=dict(document.get("common") or {}),
                        version=document.get("version"), source=source)
    if check:
        faults = check_invariants(registry)
        if faults:
            raise RegistryUnavailable(
                f"{source or 'the registry'} fails registry-schema.md's invariants -- "
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

    # 0. The shape registry 4 reads: what keel-cloud 087 removed is refused by name, never ignored.
    for d in dims:
        for name in GONE_ENTRY_KEYS:
            if name in d.raw_keys:
                faults.append(f"unknown shape: {d.key} carries `{name}`, which keel-cloud 087 removed "
                              "(D3: all thirteen dimensions decide) -- judgement call 77")
        for name in GONE_RESPONDENT_KEYS:
            if name in d.respondent:
                faults.append(f"unknown shape: {d.key} carries respondent.{name}, which keel-cloud "
                              "087 / 088 removed (one escape, code's codes) -- judgement call 77")
        for name in GONE_ANSWER_KEYS:
            if name in d.answers:
                faults.append(f"unknown shape: {d.key} carries answers.{name}, which keel-cloud 087 "
                              "removed (every dimension reaches the five statuses) -- judgement call 77")
    for name in GONE_COMMON_KEYS:
        if name in registry.common:
            faults.append(f"unknown shape: the registry carries common.{name}, which keel-cloud 087 "
                          "removed -- judgement call 77")

    # 1. 13 keys, 4 / 3 / 6, `order` contiguous from 1 within each vector.
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

    # 2. One escape at most (087 FR-002): `{code, label, counts}`; only Importance's counts against;
    #    none on the gate or Commitment.
    for d in dims:
        raw = d.respondent.get("escape")
        if raw is None:
            if d.key not in (GATE_KEY, COMMITMENT_KEY):
                faults.append(f"invariant 2 (one escape): {d.key} carries none; only the gate and "
                              "Commitment have no way out")
            continue
        if not isinstance(raw, dict) or not raw.get("code") or not raw.get("label") \
                or raw.get("counts") not in ESCAPE_COUNTS:
            faults.append(f"invariant 2 (one escape): {d.key}'s escape is {raw!r}; it is one "
                          f"{{code, label, counts: {' | '.join(ESCAPE_COUNTS)}}}")
            continue
        if d.key in (GATE_KEY, COMMITMENT_KEY):
            faults.append(f"invariant 2 (one escape): {d.key} carries an escape; the gate and "
                          "Commitment have none")
        if (raw.get("counts") == "against") != (d.key == IMPORTANCE_KEY):
            faults.append(f"invariant 2 (one escape): {d.key}'s escape counts "
                          f"{raw.get('counts')!r}; only Importance's counts against")

    # 3. `b2b_only` on exactly Purchase friction, `b2b_link_only` on exactly Ability to pay;
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

    # 4. `{value}` exactly once in every belief template but the benefit list's, which has none.
    for d in dims:
        template = str(d.founder.get("belief_template") or "")
        want = 0 if d.benefit_first else 1           # the benefit list's template names no value
        if template.count("{value}") != want:
            faults.append(f"invariant 4 ({{value}} {'never' if want == 0 else 'exactly once'}): "
                          f"{d.key}'s belief template carries it {template.count('{value}')} times")

    # 5. Codes: the controls are keel-cloud 087's; Prevalence's fifths 4-6, unique, contiguous; a list
    #    control's `saves` bounds; fixed answers unique, their supports theirs; the price, cost, derived
    #    and benefit shapes.
    for d in dims:
        if d.founder_control not in FOUNDER_CONTROLS:
            faults.append(f"invariant 5 (founder controls): {d.key}'s founder control is "
                          f"{d.founder_control!r}, not one of keel-cloud 087's")
        if d.respondent_control not in RESPONDENT_CONTROLS:
            faults.append(f"invariant 5 (respondent controls): {d.key}'s respondent control is "
                          f"{d.respondent_control!r}, not one of keel-cloud 087's")
        if d.compare_rule not in COMPARE_RULES:
            faults.append(f"invariant 5 (compare rules): {d.key} is read by {d.compare_rule!r}, not "
                          "one of keel-cloud 087's")
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
        elif d.codes is not None:
            faults.append(f"invariant 5 (codes): {d.key}'s codes are {d.codes!r}")
        if d.founder_list:
            saves = d.saves
            low, high, most = saves.get("min_items"), saves.get("max_items"), saves.get("max_words")
            if not (isinstance(low, int) and isinstance(high, int) and 0 < low <= high
                    and isinstance(most, int) and most > 0 and isinstance(saves.get("picked"), bool)):
                faults.append(f"invariant 5 (a list's saves): {d.key} is a {d.founder_control} whose "
                              f"saves are {saves!r}; it bounds min_items <= max_items, max_words and "
                              "picked")
        elif d.founder.get("saves") is not None:
            faults.append(f"invariant 5 (a list's saves): {d.key} carries saves on a "
                          f"{d.founder_control!r} control")
        answers = d.fixed_answer_codes
        if d.respondent_control in FIXED_ANSWER_CONTROLS and not answers:
            faults.append(f"invariant 5 (fixed answers): {d.key} is {d.respondent_control} with no "
                          "fixed_answers")
        if answers:
            if len(set(answers)) != len(answers) or not all(answers):
                faults.append(f"invariant 5 (fixed answers unique): {d.key}'s codes are {answers}")
            supports = list(d.respondent.get("supports") or [])
            if not set(supports) <= set(answers):
                faults.append(f"invariant 5 (fixed answers): {d.key}'s supports {supports} are not "
                              f"among its answers {answers}")
            conditional = d.respondent.get("conditional")
            if conditional is not None and conditional not in supports:
                faults.append(f"invariant 5 (fixed answers): {d.key}'s conditional {conditional!r} is "
                              "not one of its supports")
        if d.normalized.get("kind") == PRICE_FOUNDER_CONTROL or d.founder_price:
            periods = d.normalized.get("periods")
            if list(periods or []) not in (list(PRICE_PERIODS), list(CHAIN_PERIODS)):
                faults.append(f"invariant 5 (price periods): {d.key}'s periods are {periods!r}, not "
                              f"{list(PRICE_PERIODS)} (nor the chain's {list(CHAIN_PERIODS)}, keel-cloud 115)")
        if d.normalized.get("kind") == "cost" or d.founder_cost:
            periods, modes = d.normalized.get("periods"), d.normalized.get("modes")
            if list(periods or []) not in (list(PERIODS), list(CHAIN_PERIODS)):
                faults.append(f"invariant 5 (cost periods): {d.key}'s periods are {periods!r}, not "
                              f"{list(PERIODS)} (nor the chain's {list(CHAIN_PERIODS)}, keel-cloud 115)")
            if list(modes or []) not in (list(COST_MODES), list(CHAIN_COST_MODES)):
                faults.append(f"invariant 5 (cost modes): {d.key}'s modes are {modes!r}, not "
                              f"{list(COST_MODES)} (nor the chain's {list(CHAIN_COST_MODES)}, keel-cloud 115)")
            if "code_rule" in d.normalized:        # keel-cloud 077: no kinds of cost anywhere
                faults.append(f"invariant 5 (a cost has no kinds): {d.key} carries a code_rule; "
                              "keel-cloud 077 removed the respondent's kinds")
            if d.respondent_control not in (COST_TOTAL_CONTROL, VALUE_BOX_CONTROL):
                faults.append(f"invariant 5 (one total): {d.key}'s respondent control is "
                              f"{d.respondent_control!r}, not {COST_TOTAL_CONTROL!r} nor keel-cloud 115's "
                              f"{VALUE_BOX_CONTROL!r}")
        derived_kind = d.normalized.get("kind") == "price_cost_ratio"
        if derived_kind != d.derived:
            faults.append(f"invariant 5 (derived on both sides): {d.key} is derived on one side only: "
                          f"control {d.founder_control!r}, normalized {d.normalized.get('kind')!r}")
        if derived_kind:
            sources = list(d.normalized.get("from") or [])
            if not sources or not all(k in keys for k in sources):
                faults.append(f"invariant 5 (derived from keys): {d.key} is derived from {sources!r}, "
                              "which are not all registry keys")
            if d.compare_rule != DERIVED_COMPARE_RULE:
                faults.append(f"invariant 5 (derived is cost_covers_price): {d.key} is derived and "
                              f"read by {d.compare_rule!r}")
        if d.benefit_first != (d.respondent_control == BENEFIT_CONTROL):
            faults.append(f"invariant 5 (benefit on both sides): {d.key} is read by "
                          f"{d.compare_rule!r} on a {d.respondent_control!r} control")
        if d.benefit_first and d.founder_control != BENEFIT_FOUNDER_CONTROL:
            faults.append(f"invariant 5 (the founder lists benefits): {d.key}'s founder control is "
                          f"{d.founder_control!r}, not {BENEFIT_FOUNDER_CONTROL!r}")
        bins = d.normalized.get("bins")
        if bins is not None and not _bins_contiguous(bins):
            faults.append(f"invariant 5 (contiguous bins): {d.key}'s bins {bins} are not "
                          "contiguous and ordered")

    # 6. `answers.shape == interval` iff the respondent control yields a number.
    for d in dims:
        numeric = d.respondent_control in NUMBER_YIELDING_CONTROLS
        shape = d.answers.get("shape")
        if numeric != (shape == "interval"):
            faults.append(f"invariant 6 (interval iff numeric control): {d.key} answers as "
                          f"{shape!r} on a {d.respondent_control!r} control")

    # 7. The gate is problem.prevalence's, and nobody else's.
    gates = [d.key for d in dims if d.respondent_control == GATE_CONTROL]
    if gates != [GATE_KEY]:
        faults.append(f"invariant 7 (the one gate): gate_yes_no is on "
                      f"{', '.join(gates) or 'no dimension'}, and must be on {GATE_KEY} alone")

    # 8. Every respondent option set fits the spoken guidelines (087 FR-002): at most five fixed
    #    answers, each at most nine words.
    for d in dims:
        answers = d.fixed_answers
        if len(answers) > MAX_FIXED_ANSWERS:
            faults.append(f"invariant 8 (spoken: at most {MAX_FIXED_ANSWERS} answers): {d.key} has "
                          f"{len(answers)}")
        for answer in answers:
            if words(answer.get("label")) > MAX_ANSWER_WORDS:
                faults.append(f"invariant 8 (spoken: at most {MAX_ANSWER_WORDS} words an answer): "
                              f"{d.key}'s {answer.get('label')!r} is {words(answer.get('label'))}")
    return faults
