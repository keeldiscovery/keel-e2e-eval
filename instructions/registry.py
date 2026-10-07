"""keel-cloud's dimension registry, read from the export and checked before a case is built
(spec 029 FR-021, data-model §1, research R4).

The registry is the **golden** for `dimension_coverage` and `option_validity` (judgement calls 30
and 31): every control, code, bin, belief template and plan part a scorer checks a question
against. keel-cloud 058 exports it as `dimension-registry.json` beside `model-routing.json`;
`instructions/contract.read` loads it through `from_document` here. Nothing in this module is a
copy of the cloud's registry -- the design-time draft under
`specs/029-marks-v9-vectors/contracts/dimension-registry.yaml` is read by no code at run time, and
the fixture under `tests/fixtures/registry/` is a hand-sized slice of it.

**The seven invariants are this repository's to check** (`registry-schema.draft.md` §Invariants,
restated in data-model §1), because a mark of 1.00 is honest only against a registry that is itself
well formed -- marks §2.2: *"1.00 is honest only because the registry fixes the codes"*. A registry
that fails one is a **refusal to start** naming the invariant and the key, never a warning and
never a score.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: Invariant 1: 25 keys, 9 / 9 / 7.
PER_VECTOR = {"PROBLEM": 9, "SOLUTION": 9, "COMMERCIAL": 7}

#: Invariant 2: the nine deal-breakers, exactly (`registry-schema.draft.md` §Invariants 2). Fixed
#: by the schema rather than read off the file, because the point of the invariant is that the file
#: cannot quietly promote or demote one.
DEAL_BREAKERS = {
    "PROBLEM": ("problem.prevalence", "problem.frequency", "problem.duration"),
    "SOLUTION": ("solution.compatibility", "solution.relative_advantage",
                 "solution.effectiveness_threshold"),
    "COMMERCIAL": ("commercial.existing_sacrifice", "commercial.buyer_payer_alignment",
                   "commercial.commitment"),
}

#: Invariant 3: 23 asked in V1, parts 1 / 2 / 3 = 8 / 9 / 6.
ASKED_IN_V1 = 23
PER_PART = {1: 8, 2: 9, 3: 6}

#: Invariant 6: the respondent controls whose answer is a number (`answers.shape == interval`).
NUMERIC_RESPONDENT_CONTROLS = ("segmented_0_to_7", "number_with_unit", "single_choice_bands",
                               "two_numbers_optional")

#: Invariant 7: the one gate.
GATE_KEY = "problem.prevalence"
GATE_CONTROL = "gate_yes_no"

#: Respondent-only codes the registry adds on the respondent side and never offers the founder
#: (registry decision 12).
FIXED_RESPONDENT_CODES = {
    "solution.trust_risk": ("own_instinct",),
    "solution.target_circumstance": ("not_useful",),
    "commercial.commitment": ("nothing_yet",),
}

#: Codes a respondent item adds that are no founder's option: the escapes and the respondent-only
#: fixed codes above. What is left of a golden plan row's codes once these go is the founder's own
#: option set -- `founder_options` on the respondent screen, and what `option_validity` requires
#: present.
RESPONDENT_ESCAPES = ("something_else", "nothing", "nothing_much", "never_came_up",
                      "would_not_fit", "nothing_would_change", "nothing_worth_it", "free_or_gift",
                      "it_was_free", "would_not_reach", "own_instinct", "not_useful", "nothing_yet")

#: The founder-side numeric controls: no options, a spec the registry owns.
NUMERIC_FOUNDER_CONTROLS = ("numeric_interval", "numeric_threshold", "price_range")


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
    def asked_in_v1(self) -> bool:
        return bool(self.respondent.get("asked_in_v1"))

    @property
    def part(self):
        return self.respondent.get("part")

    @property
    def founder_numeric(self) -> bool:
        return self.founder.get("control") in NUMERIC_FOUNDER_CONTROLS

    @property
    def respondent_numeric(self) -> bool:
        return self.respondent.get("control") in NUMERIC_RESPONDENT_CONTROLS + (GATE_CONTROL,)

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

    def asked_in_v1(self, key: str) -> bool:
        return self.by_key(key).asked_in_v1

    def part_of(self, key: str):
        return self.by_key(key).part

    def codes_of(self, key: str):
        return self.by_key(key).codes

    def fixed_respondent_codes(self, key: str) -> list[str]:
        return list(FIXED_RESPONDENT_CODES.get(key, ()))

    def deal_breakers(self, vector: str) -> list[str]:
        return [d.key for d in self.slice(vector) if d.weight == "DEAL_BREAKER"]

    def plan_keys(self, part: int, founder_calibration: dict) -> list[str]:
        """The respondent items of one part (call 30): asked in V1, in this part, and not left out
        by the founder -- in vector order, then `order`. What production's `EVIDENCE_PLAN` hands
        the job, and the respondent denominator of `dimension_coverage`."""
        out = []
        for vector in VECTORS:
            for d in self.slice(vector):
                if not d.asked_in_v1 or d.part != part:
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
        left_out=dict(raw.get("left_out") or {}), lullaby=dict(raw.get("lullaby") or {}))


def from_document(document, *, source: str = "", check: bool = True) -> Registry:
    """A registry from its exported shape -- `{version?, common, dimensions: [...]}` -- checked
    against the seven invariants unless `check` is false (the invariant tests ask for the
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

    # 1. 25 keys, 9 / 9 / 7, `order` contiguous from 1 within each vector.
    if len(keys) != sum(PER_VECTOR.values()) or len(set(keys)) != len(keys):
        faults.append(f"invariant 1 (25 unique keys): the registry has {len(set(keys))} unique of "
                      f"{len(keys)}")
    for vector, count in PER_VECTOR.items():
        in_vector = [d for d in dims if d.vector == vector]
        orders = sorted(d.order for d in in_vector if isinstance(d.order, int))
        if len(in_vector) != count:
            faults.append(f"invariant 1 (9 / 9 / 7): {vector} has {len(in_vector)} dimensions")
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

    # 3. 23 asked in V1; parts 8 / 9 / 6.
    asked = [d for d in dims if d.asked_in_v1]
    if len(asked) != ASKED_IN_V1:
        extra = ", ".join(d.key for d in asked)
        faults.append(f"invariant 3 (23 asked in V1): {len(asked)} are asked"
                      + ("" if len(asked) < ASKED_IN_V1 else f" ({extra})"))
    for part, count in PER_PART.items():
        in_part = [d.key for d in asked if d.part == part]
        if len(in_part) != count:
            faults.append(f"invariant 3 (parts 8 / 9 / 6): part {part} has {len(in_part)}")
    for d in asked:
        if d.part not in PER_PART:
            faults.append(f"invariant 3 (parts): {d.key} is asked in V1 with part {d.part!r}")

    # 4. `{value}` exactly once in every belief template.
    for d in dims:
        template = str(d.founder.get("belief_template") or "")
        if template.count("{value}") != 1:
            faults.append(f"invariant 4 ({{value}} exactly once): {d.key}'s belief template "
                          f"carries it {template.count('{value}')} times")

    # 5. Fixed codes 4-6, none repeated; numeric bins contiguous and ordered.
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
        bins = d.normalized.get("bins")
        if bins is not None and not _bins_contiguous(bins):
            faults.append(f"invariant 5 (contiguous bins): {d.key}'s bins {bins} are not "
                          "contiguous and ordered")

    # 6. `answers.shape == interval` iff the respondent control is numeric.
    for d in dims:
        numeric = d.respondent.get("control") in NUMERIC_RESPONDENT_CONTROLS
        shape = d.answers.get("shape")
        if numeric != (shape == "interval"):
            faults.append(f"invariant 6 (interval iff numeric control): {d.key} answers as "
                          f"{shape!r} on a {d.respondent.get('control')!r} control")

    # 7. The gate is problem.prevalence's, and nobody else's.
    gates = [d.key for d in dims if d.respondent.get("control") == GATE_CONTROL]
    if gates != [GATE_KEY]:
        faults.append(f"invariant 7 (the one gate): gate_yes_no is on "
                      f"{', '.join(gates) or 'no dimension'}, and must be on {GATE_KEY} alone")
    return faults
