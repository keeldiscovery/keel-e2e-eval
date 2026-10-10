"""The golden corpus at revision 6, read and never written (spec 029 FR-006/FR-012, data-model §2;
spec 030 FR-002, judgement call 49; spec 031 FR-002, judgement call 51; spec 032 FR-002, call 60).

`canon/designs/measured-beliefs/corpus/*.yaml` in the keel-cloud checkout is the corpus. This
module opens those files, hashes them on the way in, and offers `verify_unchanged()` so the end of
a run can prove nothing here moved while it ran. **If an instruction cannot reach a golden, the
instruction is wrong** -- or the design is, and it goes back to step 1. Never the corpus.

**Revision 6 only** (call 60). `MARKS_VERSION` 12 reads keel-cloud 074's schema: revision 3's
shape (`context`, `interpretations.problem`, `solution_mechanism`, `persona`, the golden plan
`respondent_questions`, people with a gate answer, a story, a chip, a golden anchoring and picks by
dimension, `expected.standings` + `expected.vector_verdicts`) on the registry of **thirteen**, with
`founder_calibration` keyed by the entry's **calibrated set** -- twelve keys on a B2C persona,
thirteen on a B2B one (calls 47, 59) -- and the six `Status` words. Revision 6 adds, to revision 5's
Price and units (keel-cloud `sim/check_corpus_r6.py`'s K, D, U and T), what this module checks:
Existing sacrifice's founder answer is a **cost estimate** `{mode, low, high, rate?, period,
currency}` (or `unsure`) and its belief the engine's sentence; Price takes the cost's **period**;
Ability to pay is **derived** on every entry -- `{ratio_low, ratio_high, band}` recomputed here from
the cost and the price (`derive_ability`, keel-cloud's `AbilityToPay.derive` mirrored), `unsure`
exactly when the cost or the price is; every Existing sacrifice pick records its recall `period`; a
B2B entry records a top-level `hourly_rate`; a decision-maker on the `COMMERCIAL_B2B` link has no
story and no chip and is `ANCHORED` by rule (keel-cloud 075); a B2C Existing sacrifice standing
may record `time_only` / `time_only_hours` (people who gave only time, reported apart). A file at
any other revision (a revision-5 file is named as v11's, a revision-4 one as v10's, a revision-3
one as v9's), or still carrying `beliefs`, `questionnaire`, `expected.buckets`, `expected.stages`
or a per-anchor answer, is a **refusal to start** by entry and by key -- never a fallback, the same
shape v8's scalar-`stage` refusal had.

Three things the corpus says (since r3) that the code has to carry:

1. **The plan is derived, and the file's own plan is a check on it** (calls 30, 47). `plan()` is
   the registry's keys asked on each part's link (`Registry.link_of`: part 3 of a B2B study is the
   decision-maker's `COMMERCIAL_B2B` link, and asks Ability to pay and Purchase friction too), by part, that the
   founder did not leave out; the file's `respondent_questions` must hold exactly those keys per
   part, or the file disagrees with the registry it is keyed by -- a refusal.
2. **The chipped story is a corpus fact, not a judgement** (call 33 amended, FR-017). `readable()` is
   the people who passed the gate, carry no chip and wrote a story; nobody else is ever shown to the
   reader, and a chip-carrying person's golden `GUESSED` is checked by `compare_correctness`.
3. **`no_leak`'s list is the corpus's** (call 32). `vocabulary()` stems the golden
   `solution_mechanism` and subtracts the problem's own words; the stems excluded only because the
   problem's world spells them with another inflection are kept beside it as the **inflection
   ledger**, because those -- and only those -- are the ties the judge is asked about.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from . import text as text_mod
from .registry import (ABILITY_BANDS, ABILITY_KEY, AMOUNTS_CONTROL, COST_MODES, DEAL_BREAKERS,
                       LINK_B2B, LINK_PRIMARY, PERIODS, PRICE_KEY, PRICE_PERIODS, SACRIFICE_KEY,
                       UNITS, VECTORS, RecallWindow)

REVISION = 6

#: The revisions a refusal names by the rubric that read them (calls 49, 51).
_REVISION_OF = {3: "MARKS_VERSION 9's corpus, on the registry of twenty-five",
                4: "MARKS_VERSION 10's corpus, on the registry of twelve (no Price, no units)",
                5: "MARKS_VERSION 11's corpus, before cost first (a tick list for Existing sacrifice, "
                   "Price over month / year / one-off, Ability to pay asked of the founder)"}

#: `sim/check_corpus_r5.py`'s `CURRENCY` (keel-cloud `Market.currency`'s table, the corpus's markets):
#: a founder price is in its market's currency, never another.
MARKET_CURRENCY = {"GB": "GBP", "US": "USD", "IE": "EUR", "FR": "EUR", "DE": "EUR", "IN": "INR",
                   "CA": "CAD", "AU": "AUD"}

#: keel-cloud 073's `PriceLadder.POINTS`: the one ladder, the same numbers in every currency.
LADDER_POINTS = (1, 2, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 5000, 10000)
WOULD_NOT_PAY = "would_not_pay"


def price_placeable(low) -> bool:
    """`PriceLadder.placeable`: a founder's low of at least 1 and under 10,000."""
    return isinstance(low, (int, float)) and not isinstance(low, bool) \
        and LADDER_POINTS[0] <= low < LADDER_POINTS[-1]


def price_floor(low):
    """`PriceLadder.founderFloor`: the ladder point at or below the founder's low."""
    return next(p for p in reversed(LADDER_POINTS[:-1]) if low >= p) if low >= 1 else LADDER_POINTS[0]


def price_ladder_codes(low) -> list:
    """`PriceLadder.bands`' codes: five consecutive bands with the founder's in the middle three
    (clamped at the ladder's ends), then `would_not_pay` -- what a Price plan row must hold."""
    if not price_placeable(low):
        raise ValueError(f"a founder's low of {low!r} is off the ladder (1 to under 10,000)")
    f = LADDER_POINTS.index(price_floor(low))
    k = max(0, min(f - 1, len(LADDER_POINTS) - 4))

    def plain(n):
        return str(int(n)) if float(n).is_integer() else str(n)
    return ([f"under_{plain(LADDER_POINTS[k])}"]
            + [f"band_{plain(LADDER_POINTS[i])}_{plain(LADDER_POINTS[i + 1])}"
               for i in range(k, k + 3)]
            + [f"over_{plain(LADDER_POINTS[k + 3])}", WOULD_NOT_PAY])

STAGES = VECTORS

#: The recall periods an Existing sacrifice pick is asked over (`Period.recall`: a day is asked over a
#: week, a year over the last three months).
RECALL_PERIODS = ("week", "month", "quarter")

#: `sim/check_corpus_r6.py`'s `SYMBOL` / `WORDS`: the engine's sentences, mirrored for the belief checks.
_SYMBOL = {"GBP": "\u00a3", "USD": "$", "EUR": "\u20ac"}
_PERIOD_WORDS = {"day": "a day", "week": "a week", "month": "a month", "quarter": "a quarter",
                 "year": "a year"}
_BAND_WORDS = {"small_share": "a small share of what the problem costs them",
               "mostly_from_spend": "it could mostly be paid from what they already spend",
               "new_money": "more than the problem costs them today; they would need to find new money",
               "some_from_spend": "some could pay it from what they already spend; others would need "
                                  "to spend more"}


def _half_up(x) -> int:
    from decimal import ROUND_HALF_UP, Decimal                       # noqa: PLC0415
    return int(Decimal(repr(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def money_text(value, currency) -> str:
    """`CostEstimate.amount`: the symbol, thousands with commas, pennies only where there are some."""
    v = round(float(value), 2)
    text = f"{int(v):,}" if v == int(v) else f"{v:,.2f}"
    return _SYMBOL.get(currency, (currency or "") + " ") + text


def _number_text(value) -> str:
    v = float(value)
    return str(int(v)) if v == int(v) else str(v)


def cost_money(cost: dict) -> tuple:
    """`CalibrationAnswer.Cost.moneyLow / moneyHigh`: hours at the rate on `HOURS`."""
    if cost["mode"] == "HOURS":
        return cost["low"] * cost["rate"], cost["high"] * cost["rate"]
    return cost["low"], cost["high"]


def cost_said(cost: dict) -> str:
    """`CostEstimate.said`: *about £10 to £30 a month*, or *30 to 60 hours a quarter, about $2,400 to $4,800*."""
    period = _PERIOD_WORDS[cost["period"]]
    low, high = cost_money(cost)
    spread = money_text(low, cost["currency"]) if low == high else \
        f"{money_text(low, cost['currency'])} to {money_text(high, cost['currency'])}"
    if cost["mode"] == "HOURS":
        hours = _number_text(cost["low"]) if cost["low"] == cost["high"] else \
            f"{_number_text(cost['low'])} to {_number_text(cost['high'])}"
        return f"{hours} hours {period}, about {spread}"
    return f"about {spread} {period}"


def derive_ability(cost: dict, price: dict) -> dict:
    """`AbilityToPay.derive` (founder decision 2, 2026-10-10): whole percent, `price low / cost high`
    to `price high / cost low`; `some_from_spend` when the range crosses 100%, else by the high end --
    under 50 `small_share`, up to 100 `mostly_from_spend`, over `new_money`."""
    low, high = cost_money(cost)
    ratio_low = _half_up(price["low"] * 100 / high)
    ratio_high = _half_up(price["high"] * 100 / low)
    band = ("some_from_spend" if ratio_low < 100 < ratio_high else "small_share" if ratio_high < 50
            else "mostly_from_spend" if ratio_high <= 100 else "new_money")
    return {"ratio_low": ratio_low, "ratio_high": ratio_high, "band": band}


def ability_value(derived: dict) -> str:
    """`AbilityToPay.value`: *31% to 125% of what the problem costs them today: ...*."""
    ratio = f"{derived['ratio_low']}%" if derived["ratio_low"] == derived["ratio_high"] else \
        f"{derived['ratio_low']}% to {derived['ratio_high']}%"
    return f"{ratio} of what the problem costs them today: {_BAND_WORDS[derived['band']]}"

#: The six `Status` words (keel-cloud 071; registry-schema; marks §2.5).
STATUSES = ("HOLDING_UP", "NOT_HOLDING_UP", "PEOPLE_DISAGREE", "TOO_FEW_TO_CALL", "NOT_ASKED_YET",
            "LEFT_OUT")

#: The drift words `expected.standings[*].drift` may carry (`null` beside them).
DRIFTS = ("above", "below", "both", "none")

CHIPS = ("cant_recall", "rather_not_say")
ANCHORINGS = ("ANCHORED", "GUESSED")

#: The keys revision 2 carried and revision 3 dropped (marks §4 *Dropped*).
R2_KEYS = ("beliefs", "questionnaire", "normalization_rationale")
R2_EXPECTED_KEYS = ("buckets", "stages")


class CorpusError(RuntimeError):
    """The corpus could not be read, or moved while a run was in flight."""


#: The two links a person answers on (FR-010): the primary interview, and -- on a B2B entry -- the
#: decision-maker's Part 3 (`COMMERCIAL_B2B`: no gate, no context card, no reveal). The registry's
#: words, re-exported.
assert (LINK_PRIMARY, LINK_B2B) == ("PRIMARY", "COMMERCIAL_B2B")


@dataclass(frozen=True)
class Person:
    person: str
    recency: str | None        # "yes" | "no" -- the gate (problem.prevalence); None on the B2B link
    story: str | None
    chip: str | None
    anchoring: str | None      # golden; None when recency == "no"
    picks: dict
    pilot_opt_in: bool = False
    link: str = LINK_PRIMARY

    @property
    def gate_yes(self) -> bool:
        return self.link == LINK_PRIMARY and self.recency == "yes"

    @property
    def readable(self) -> bool:
        """Gate-yes, un-chipped, with a story typed -- the only people `INTERPRET` is shown."""
        return self.gate_yes and self.chip is None and bool((self.story or "").strip())


@dataclass(frozen=True)
class Entry:
    id: str
    title: str
    revision: int
    market: dict
    statements: dict
    roles: list
    context: dict
    interpretations: dict
    solution_mechanism: dict
    persona: dict
    founder_calibration: dict
    respondent_questions: dict
    answers: list
    expected: dict
    path: Path
    sha256: str
    registry: object = None
    #: The entry's top-level `hourly_rate` (`{value, currency}`) on a B2B entry; `None` on B2C (call 60).
    raw_rate: object = None

    # ------------------------------------------------------------------ the people

    def people(self) -> list[Person]:
        return [_person(raw) for raw in self.answers]

    def gate_yes(self) -> list[Person]:
        return [p for p in self.people() if p.gate_yes]

    def deciders(self) -> list[Person]:
        """The B2B entry's decision-makers, who answer Part 3 on their own link (FR-010)."""
        return [p for p in self.people() if p.link == LINK_B2B]

    def readable(self) -> list[Person]:
        return [p for p in self.people() if p.readable]

    def person(self, name: str) -> Person | None:
        return next((p for p in self.people() if p.person == name), None)

    def role(self, role_id: str) -> dict | None:
        return next((r for r in self.roles if r.get("id") == role_id), None)

    def b2b(self) -> bool:
        """Whether the decision-maker is a role of its own (FR-010) -- the `COMMERCIAL_B2B` link."""
        return isinstance((self.persona or {}).get("decision_maker"), dict)

    def decision_maker_role(self) -> str | None:
        maker = (self.persona or {}).get("decision_maker")
        return maker.get("role") if isinstance(maker, dict) else None

    # ---------------------------------------------------------------------- the plan

    def unsure(self, key: str) -> bool:
        return bool((self.founder_calibration.get(key) or {}).get("unsure"))

    def price(self) -> dict | None:
        """The founder's Price, `{low, high, period, currency}`, or `None` when they left it out
        (call 51; Mulch Run's per-yard price is on no period of the ladder)."""
        answer = (self.founder_calibration.get(PRICE_KEY) or {}).get("answer")
        return answer if isinstance(answer, dict) else None

    def cost(self) -> dict | None:
        """The founder's cost estimate, `{mode, low, high, rate?, period, currency}`, or `None` when
        they left it out (call 60)."""
        answer = (self.founder_calibration.get(SACRIFICE_KEY) or {}).get("answer")
        return answer if isinstance(answer, dict) else None

    def hourly_rate(self) -> float | None:
        """The B2B entry's top-level `hourly_rate.value` (call 60), else `None`."""
        value = (self.raw_rate or {}).get("value") if isinstance(self.raw_rate, dict) else None
        return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    def units(self, key: str = SACRIFICE_KEY) -> dict:
        """`{kind: unit}` for a kind of cost: the plan row's (founder kinds and distractors), the
        founder's own over it (call 51)."""
        row = dict(((self.respondent_questions or {}).get(key) or {}).get("units") or {})
        row.update((self.founder_calibration.get(key) or {}).get("units") or {})
        return row

    def link_of(self, part: int) -> str:
        """The link a part is asked on: part 3 of a B2B study is the decision-maker's (decision 26)."""
        return LINK_B2B if (self.b2b() and part == 3) else LINK_PRIMARY

    def calibrated_keys(self, registry=None) -> list:
        """The keys this entry calibrates (calls 47, 59): the registry's thirteen less Purchase friction
        on a B2C persona (twelve); without a registry bound, `founder_calibration`'s own keys."""
        registry = registry if registry is not None else self.registry
        if registry is not None:
            return registry.calibrated_keys(self.b2b())
        return list(self.founder_calibration)

    def plan(self, registry=None) -> dict:
        """`{1: [key], 2: [key], 3: [key]}` (calls 30, 47): the registry's keys asked on each
        part's own link (`link_of`), by part, the founder did not leave out, in order. Without a
        registry bound, the file's own golden plan (`respondent_questions`) by part, in file order
        -- the two are checked equal on load."""
        registry = registry if registry is not None else self.registry
        if registry is not None:
            return {part: registry.plan_keys(part, self.founder_calibration, self.link_of(part),
                                             self.b2b()) for part in (1, 2, 3)}
        out = {1: [], 2: [], 3: []}
        for key, row in (self.respondent_questions or {}).items():
            part = (row or {}).get("part")
            if part in out:
                out[part].append(key)
        return out

    # ----------------------------------------------------------- the founder's labels

    def founder_option_codes(self, key: str) -> list:
        """The codes of the options the founder's calibration showed for a model-written set: the
        golden plan row's codes less the respondent-only rows code appends (call 38), keeping a
        founder-side `none` / `nothing` -- the founder saw it; code appends the respondent's."""
        return founder_codes_of((self.respondent_questions or {}).get(key) or {})

    def founder_labels(self, key: str) -> dict | None:
        """`{code: label}` -- the labels the founder saw (`founder_calibration[key].labels`, one per
        `founder_option_codes`, in order), what production's `founderOptions` carries; `None` where
        the entry records none."""
        labels = (self.founder_calibration.get(key) or {}).get("labels")
        if not labels:
            return None
        return dict(zip(self.founder_option_codes(key), labels))

    # ------------------------------------------------------------- the mechanism's words

    def _mechanism_texts(self) -> list[str]:
        mechanism = self.solution_mechanism or {}
        # Call 39: `mechanism`, `output`, `not_assumed` (and `mechanism_terms`, below) only --
        # never `trigger` (it describes the problem moment) nor `actor`.
        texts = [str(mechanism.get(k) or "") for k in ("mechanism", "output")]
        texts += [str(t) for t in mechanism.get("not_assumed") or []]
        return texts

    def _problem_texts(self) -> list[str]:
        texts = [str(v) for v in (self.context or {}).values() if v]
        texts.append(str((self.statements or {}).get("problem") or ""))
        texts.append(str((self.interpretations or {}).get("problem") or ""))
        # The gate stories only: a decision-maker's story on the B2B link is about a past purchase
        # -- platform fees, a tool they bought -- which is the commercial world, not the problem's.
        texts += [p.story for p in self.people() if p.story and p.link == LINK_PRIMARY]
        return texts

    def _problem_words(self) -> dict:
        """stem -> the problem-world spellings of it."""
        out = {}
        for chunk in self._problem_texts():
            for word in text_mod.content_words(chunk):
                out.setdefault(text_mod.stem(word), set()).add(word)
        return out

    def _mechanism_words(self) -> dict:
        out = {}
        for chunk in self._mechanism_texts():
            for word in text_mod.content_words(chunk):
                out.setdefault(text_mod.stem(word), set()).add(word)
        for term in (self.solution_mechanism or {}).get("mechanism_terms") or []:
            tokens = text_mod.content_words(term)
            if len(text_mod.words(term)) == 1 and tokens:
                out.setdefault(text_mod.stem(tokens[0]), set()).add(tokens[0])
        return out

    def vocabulary(self) -> set[str]:
        """The stems `no_leak`'s sweep A looks for (calls 32, 39): the content words of the golden
        mechanism's `mechanism`, `output` and `not_assumed` (never `trigger` or `actor`) and its
        single-word `mechanism_terms`, stemmed, less the stoplist and every stem of the
        problem's own words (`context`, `statements.problem`, `interpretations.problem`, every
        story). Multi-word terms are `mechanism_phrases()`."""
        problem = self._problem_words()
        return {s for s in self._mechanism_words() if s not in problem}

    def mechanism_phrases(self) -> list[tuple]:
        """The multi-word `mechanism_terms` (*most likely*), stemmed in order, matched as phrases."""
        out = []
        for term in (self.solution_mechanism or {}).get("mechanism_terms") or []:
            if len(text_mod.words(term)) > 1:
                out.append(tuple(text_mod.stem_sequence(term)))
        return out

    def inflection_ledger(self) -> dict:
        """`{stem: {"mechanism": [...], "problem": [...]}}` -- the stems excluded from the vocabulary
        **only** because the problem's world spells them with another inflection (*listens* in the
        mechanism, *listened* in a story). A hit on one is a tie, and a tie goes to the judge."""
        problem = self._problem_words()
        out = {}
        for stem, spellings in self._mechanism_words().items():
            if stem in problem and not (spellings & problem[stem]):
                out[stem] = {"mechanism": sorted(spellings), "problem": sorted(problem[stem])}
        return out

    def mechanism_one_liner(self) -> str:
        """The judge's clause (marks §2.3), composed by code from the golden mechanism's four
        fields -- never from a live `SOLUTION_MECHANISM` answer (call 32)."""
        m = self.solution_mechanism or {}
        return (f"{m.get('actor', '')}, {m.get('trigger', '')}, {m.get('mechanism', '')}; "
                f"it gives {m.get('output', '')}").strip()


@dataclass
class Corpus:
    entries: list
    directory: Path
    hashes: dict = field(default_factory=dict)

    def verify_unchanged(self) -> None:
        """Re-hash every file. A difference is a failed run, not a warning.

        The corpus is the reviewer, not the subject: quietly adjusting it is exactly what freezing
        it exists to prevent, and a run that could have done so proves nothing.
        """
        for path, digest in self.hashes.items():
            current = _sha256(Path(path))
            if current != digest:
                raise CorpusError(
                    f"{path} changed while the run was in flight: {digest} -> {current}. "
                    "The corpus is frozen (keel-cloud spec 029 SC-009); this run has measured "
                    "nothing.")

    def by_id(self, entry_id: str):
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def bind(self, registry) -> "Corpus":
        """Every entry checked against the registry the export carried, and bound to it -- the
        key refusals that need the registry (data-model §2) are taken here, before a case is
        built."""
        bound = []
        for entry in self.entries:
            _check_keys(entry, registry)
            bound.append(replace(entry, registry=registry))
        self.entries = bound
        return self


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_dir(keel_cloud: Path) -> Path:
    return Path(keel_cloud) / "canon" / "designs" / "measured-beliefs" / "corpus"


def source_dir(keel_cloud: Path) -> Path:
    """The directory `load()` reads: keel-cloud's canon, and nowhere else (call 49)."""
    return corpus_dir(keel_cloud)


def load(keel_cloud: Path, *, registry=None) -> Corpus:
    """Every `NN-name.yaml` in keel-cloud's corpus directory, in filename order, each at revision
    5 -- one file at another revision refuses the whole corpus, by entry and by key (calls 49, 51)."""
    directory = source_dir(keel_cloud)
    if not directory.is_dir():
        raise CorpusError(
            f"no corpus at {directory} -- this eval reads keel-cloud's own golden set, and "
            "cannot invent one")
    files = sorted(p for p in directory.glob("*.yaml"))
    if not files:
        raise CorpusError(f"{directory} holds no *.yaml entries")
    entries, hashes = [], {}
    for path in files:
        entry = load_file(path, registry=registry)
        hashes[str(path)] = entry.sha256
        entries.append(entry)
    return Corpus(entries=entries, directory=directory, hashes=hashes)


def load_file(path, *, registry=None) -> Entry:
    """One revision-5 file, checked; bound to `registry` (and checked against it) when given."""
    path = Path(path)
    digest = _sha256(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    entry = _entry(raw, path, digest)
    if registry is not None:
        _check_keys(entry, registry)
        entry = replace(entry, registry=registry)
    return entry


# ------------------------------------------------------------------------------- the refusals

def _refuse(entry_id, message, path) -> CorpusError:
    return CorpusError(f"{entry_id}: {message} (spec 032 FR-002; judgement calls 49, 51, 60). {path}")


def _check_revision(raw: dict, path: Path) -> None:
    entry_id = raw.get("id") or path.name
    revision = raw.get("revision")
    if revision != REVISION:
        was = (f" -- revision {revision} is {_REVISION_OF[revision]}"
               if revision in _REVISION_OF else "")
        raise _refuse(entry_id, f"revision is {revision if revision is not None else 'absent'}; "
                                f"this eval reads revision {REVISION} only{was}", path)
    for key in R2_KEYS:
        if key in raw:
            raise _refuse(entry_id, f"carries `{key}`, which revision 3 dropped", path)
    for key in R2_EXPECTED_KEYS:
        if key in (raw.get("expected") or {}):
            raise _refuse(entry_id, f"carries `expected.{key}`, which revision 3 dropped", path)
    for person in raw.get("answers") or []:
        if "anchors" in (person or {}):
            raise _refuse(entry_id, f"{person.get('person')} carries `anchors`; a revision-3 "
                                    "person answers one gate story", path)


def founder_codes_of(row: dict) -> list:
    """`Entry.founder_option_codes` on a plan row."""
    from .registry import RESPONDENT_ESCAPES                  # noqa: PLC0415
    return [c for c in (row or {}).get("codes") or []
            if c not in RESPONDENT_ESCAPES or c in FOUNDER_NONE]


#: The founder's own *none of these* option (Existing sacrifice's `none`; r3 spells it `nothing`):
#: shown to the founder, so it has a label; on the respondent screen code appends it.
FOUNDER_NONE = ("none", "nothing")


def _check_shape(raw: dict, path: Path) -> None:
    entry_id = raw.get("id") or path.name
    # `context.recall_window: {count, unit}` (founder decision 42; keel-cloud 058 `cb0422a`):
    # optional -- an entry without one reads the default, 7 nights -- and refused when unreadable.
    try:
        RecallWindow.read((raw.get("context") or {}).get("recall_window"))
    except ValueError as why:
        raise _refuse(entry_id, f"context.recall_window: {why}", path) from None
    for key, value in (raw.get("founder_calibration") or {}).items():
        if not isinstance(value, dict) or not ("answer" in value or value.get("unsure") is True):
            raise _refuse(entry_id, f"founder_calibration[{key}] carries neither `answer` nor "
                                    "`unsure: true`", path)
        labels = value.get("labels")
        if labels is not None:
            codes = founder_codes_of((raw.get("respondent_questions") or {}).get(key) or {})
            if (not isinstance(labels, list) or not all(isinstance(x, str) and x.strip()
                                                         for x in labels)
                    or len(labels) != len(codes)):
                raise _refuse(entry_id, f"founder_calibration[{key}].labels must be one label per "
                                        f"founder option {codes}", path)
    b2b = isinstance((raw.get("persona") or {}).get("decision_maker"), dict)
    for person in raw.get("answers") or []:
        name = person.get("person")
        recency = person.get("recency")
        link = person.get("link", LINK_PRIMARY)
        if link not in (LINK_PRIMARY, LINK_B2B):
            raise _refuse(entry_id, f"{name}'s link is {link!r}", path)
        if link == LINK_B2B:
            if not b2b:
                raise _refuse(entry_id, f"{name} answers on the B2B link of an entry whose "
                                        "decision-maker is the same person", path)
            if recency is not None:
                raise _refuse(entry_id, f"{name} answers on the B2B link and carries a gate "
                                        "answer; the decision-maker is never asked the gate", path)
            if person.get("anchoring") != "ANCHORED":
                raise _refuse(entry_id, f"{name} answers on the B2B link and is "
                                        f"{person.get('anchoring')!r}; a decision-maker is ANCHORED by "
                                        "rule (keel-cloud 075)", path)
            for field_ in ("story", "chip"):
                if person.get(field_) not in (None, ""):
                    raise _refuse(entry_id, f"{name} answers on the B2B link and carries `{field_}`; "
                                            "the decision-maker's link has no story screen "
                                            "(keel-cloud 075)", path)
            foreign = [k for k in person.get("picks") or {} if not str(k).startswith("commercial.")]
            if foreign:
                raise _refuse(entry_id, f"{name} answers on the B2B link and picks {foreign[0]}; "
                                        "the link is Part 3 only", path)
            continue
        if recency not in ("yes", "no"):
            raise _refuse(entry_id, f"{name}'s recency is {recency!r}; the gate is yes or no", path)
        if recency == "no":
            for key in ("story", "chip", "anchoring"):
                if person.get(key) not in (None, ""):
                    raise _refuse(entry_id, f"{name} answered No at the gate and carries `{key}`; "
                                            "a gate-No answers nothing more", path)
            if person.get("picks"):
                raise _refuse(entry_id, f"{name} answered No at the gate and carries picks; a "
                                        "gate-No answers nothing more", path)
            continue
        chip = person.get("chip")
        if chip is not None and chip not in CHIPS:
            raise _refuse(entry_id, f"{name}'s chip is {chip!r}; the chips are {CHIPS}", path)
        anchoring = person.get("anchoring")
        if anchoring not in ANCHORINGS:
            raise _refuse(entry_id, f"{name}'s anchoring is {anchoring!r}", path)
        if chip is not None and anchoring != "GUESSED":
            raise _refuse(entry_id, f"{name} carries the chip {chip} and is {anchoring}; a chipped "
                                    "story is GUESSED by code (call 33 amended)", path)
    _check_price_and_units(raw, entry_id, path)
    maker = (raw.get("persona") or {}).get("decision_maker")
    if isinstance(maker, dict):
        role_ids = {r.get("id") for r in raw.get("roles") or []}
        if maker.get("role") not in role_ids:
            raise _refuse(entry_id, f"persona.decision_maker names the role {maker.get('role')!r}, "
                                    f"which is not in roles ({', '.join(sorted(map(str, role_ids)))})",
                          path)
    elif maker != "same_person":
        raise _refuse(entry_id, f"persona.decision_maker is {maker!r}; it is same_person or "
                                "{role: <id>}", path)
    _check_cost_first(raw, entry_id, path)
    expected = raw.get("expected") or {}
    for key, standing in (expected.get("standings") or {}).items():
        status = (standing or {}).get("status")
        if status not in STATUSES:
            raise _refuse(entry_id, f"expected.standings[{key}].status is {status!r}, outside "
                                    "Status", path)
        drift = (standing or {}).get("drift")
        if drift is not None and drift not in DRIFTS:
            raise _refuse(entry_id, f"expected.standings[{key}].drift is {drift!r}", path)
    for vector, verdict in (expected.get("vector_verdicts") or {}).items():
        if vector not in VECTORS:
            raise _refuse(entry_id, f"expected.vector_verdicts names {vector!r}", path)
        if (verdict or {}).get("verdict") not in STATUSES:
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].verdict is "
                                    f"{(verdict or {}).get('verdict')!r}, outside Status", path)
        deciding = (verdict or {}).get("deciding")
        if deciding not in DEAL_BREAKERS[vector]:
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].deciding is {deciding!r}, "
                                    f"not a DEAL_BREAKER of {vector}", path)


def _check_price_and_units(raw: dict, entry_id, path: Path) -> None:
    """Revision 5's own checks (call 51; `check_corpus_r5.py`'s P and U): the founder's Price on the
    ladder in the market's currency, its plan row the ladder's codes, every price pick a row code;
    Existing sacrifice's units money · hours · count, its plan row `branch_pick_amounts`, and every
    pick `{currency, amounts: [{kind, value?, unit?}]}` with each kind on the row in the row's unit."""
    calibration = raw.get("founder_calibration") or {}
    plan = raw.get("respondent_questions") or {}
    country = (raw.get("market") or {}).get("country")
    price = calibration.get(PRICE_KEY)
    if isinstance(price, dict) and not price.get("unsure"):
        answer = price.get("answer")
        if not isinstance(answer, dict):
            raise _refuse(entry_id, f"founder_calibration[{PRICE_KEY}].answer is {answer!r}; a "
                                    "price is {low, high, period, currency}", path)
        low, high = answer.get("low"), answer.get("high")
        if not price_placeable(low) or not isinstance(high, (int, float)) or high < low:
            raise _refuse(entry_id, f"founder_calibration[{PRICE_KEY}] is {low!r} to {high!r}: off "
                                    "the ladder (a low of 1 to under 10,000, the high not below it)",
                          path)
        if answer.get("period") not in PRICE_PERIODS:
            raise _refuse(entry_id, f"founder_calibration[{PRICE_KEY}].period is "
                                    f"{answer.get('period')!r}, not one of {PRICE_PERIODS}", path)
        if country in MARKET_CURRENCY and answer.get("currency") != MARKET_CURRENCY[country]:
            raise _refuse(entry_id, f"founder_calibration[{PRICE_KEY}].currency is "
                                    f"{answer.get('currency')!r}; the market ({country}) prices in "
                                    f"{MARKET_CURRENCY[country]}, never another", path)
        codes = (plan.get(PRICE_KEY) or {}).get("codes")
        if PRICE_KEY in plan and codes != price_ladder_codes(low):
            raise _refuse(entry_id, f"respondent_questions[{PRICE_KEY}].codes are {codes}; the "
                                    f"ladder around a low of {low:g} is {price_ladder_codes(low)}",
                          path)
    for where, units in (("founder_calibration", (calibration.get(SACRIFICE_KEY) or {}).get("units")),
                         ("respondent_questions", (plan.get(SACRIFICE_KEY) or {}).get("units"))):
        for kind, unit in (units or {}).items():
            if unit not in UNITS:
                raise _refuse(entry_id, f"{where}[{SACRIFICE_KEY}].units[{kind}] is {unit!r}, not "
                                        f"one of {UNITS}", path)
    row = plan.get(SACRIFICE_KEY)
    if row is not None and row.get("control") != AMOUNTS_CONTROL:
        raise _refuse(entry_id, f"respondent_questions[{SACRIFICE_KEY}].control is "
                                f"{row.get('control')!r}; revision 6 asks {AMOUNTS_CONTROL}", path)
    row_codes = [str(c) for c in (row or {}).get("codes") or []]
    row_units = (row or {}).get("units") or {}
    price_codes = [str(c) for c in (plan.get(PRICE_KEY) or {}).get("codes") or []]
    for person in raw.get("answers") or []:
        picks = person.get("picks") or {}
        name = person.get("person")
        pick = picks.get(SACRIFICE_KEY)
        if pick is not None and not (isinstance(pick, dict) and "chip" in pick):
            if not isinstance(pick, dict) or not isinstance(pick.get("amounts"), list):
                raise _refuse(entry_id, f"{name}'s {SACRIFICE_KEY} pick is {pick!r}; revision 6 "
                                        "answers {currency, period, amounts: [{kind, value?, unit?}]}", path)
            for amount in pick["amounts"]:
                kind, unit = (amount or {}).get("kind"), (amount or {}).get("unit")
                if row_codes and str(kind) not in row_codes:
                    raise _refuse(entry_id, f"{name}'s {SACRIFICE_KEY} kind {kind!r} is not on the "
                                            "plan row", path)
                if unit is not None and unit != row_units.get(kind):
                    raise _refuse(entry_id, f"{name}'s {SACRIFICE_KEY} kind {kind!r} is in {unit!r}; "
                                            f"the row counts it in {row_units.get(kind)!r}", path)
        band = picks.get(PRICE_KEY)
        if band is not None and not isinstance(band, dict) and price_codes \
                and str(band) not in price_codes:
            raise _refuse(entry_id, f"{name}'s {PRICE_KEY} pick {band!r} is not one of the "
                                    f"ladder's {price_codes}", path)


def _check_cost_first(raw: dict, entry_id, path: Path) -> None:
    """Revision 6's own checks (call 60; `check_corpus_r6.py`'s K, D and U): the founder's cost estimate
    and its sentence, Price on the cost's period, Ability to pay recomputed, every Existing sacrifice
    pick with its recall period, the B2B entry's hourly rate."""
    calibration = raw.get("founder_calibration") or {}
    country = (raw.get("market") or {}).get("country")
    b2b = isinstance((raw.get("persona") or {}).get("decision_maker"), dict)
    sacrifice = calibration.get(SACRIFICE_KEY) or {}
    price_cal = calibration.get(PRICE_KEY) or {}
    rate = raw.get("hourly_rate")
    if b2b:
        value = rate.get("value") if isinstance(rate, dict) else None
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise _refuse(entry_id, "a B2B entry records `hourly_rate` {value above 0, currency} "
                                    "(revision 6)", path)
    cost = None
    if not sacrifice.get("unsure"):
        cost = sacrifice.get("answer")
        if not isinstance(cost, dict) or cost.get("mode") not in COST_MODES:
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}].answer is {cost!r}; a cost "
                                    "estimate is {mode: AMOUNT | HOURS, low, high, rate?, period, "
                                    "currency}", path)
        if cost["mode"] == "HOURS" and (not b2b or not isinstance(cost.get("rate"), (int, float))
                                        or cost["rate"] <= 0):
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}] is HOURS on a B2C entry, or "
                                    "with no rate above 0 (a person's own time is never priced)", path)
        low, high = cost.get("low"), cost.get("high")
        if not isinstance(low, (int, float)) or isinstance(low, bool) or low <= 0 \
                or not isinstance(high, (int, float)) or high < low:
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}] is {low!r} to {high!r}: a "
                                    "cost low is above 0 and the high not below it", path)
        if cost.get("period") not in PERIODS:
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}].period is "
                                    f"{cost.get('period')!r}, not one of {PERIODS}", path)
        if country in MARKET_CURRENCY and cost.get("currency") != MARKET_CURRENCY[country]:
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}].currency is "
                                    f"{cost.get('currency')!r}; the market ({country}) is "
                                    f"{MARKET_CURRENCY[country]}", path)
        want = f"The problem already costs the payer {cost_said(cost)}."
        if sacrifice.get("belief_sentence") != want:
            raise _refuse(entry_id, f"founder_calibration[{SACRIFICE_KEY}].belief_sentence is "
                                    f"{sacrifice.get('belief_sentence')!r}; the engine's is {want!r}",
                          path)
    price = None if price_cal.get("unsure") else price_cal.get("answer")
    if cost is not None and isinstance(price, dict) and price.get("period") != cost.get("period"):
        raise _refuse(entry_id, f"founder_calibration[{PRICE_KEY}].period is {price.get('period')!r}; "
                                f"it is the cost estimate's, {cost.get('period')!r} (revision 6)", path)
    ability = calibration.get(ABILITY_KEY)
    if ability is None:
        raise _refuse(entry_id, f"founder_calibration lacks {ABILITY_KEY}; it is derived and "
                                "calibrated on every entry (revision 6)", path)
    if cost is None or not isinstance(price, dict):
        if not ability.get("unsure"):
            raise _refuse(entry_id, f"founder_calibration[{ABILITY_KEY}] is answered; the cost or the "
                                    "price is left out, so it is too", path)
    else:
        derived = derive_ability(cost, price)
        if ability.get("answer") != derived:
            raise _refuse(entry_id, f"founder_calibration[{ABILITY_KEY}].answer is "
                                    f"{ability.get('answer')!r}; derived from the cost and the price it "
                                    f"is {derived!r}", path)
        if derived["band"] not in ABILITY_BANDS:
            raise _refuse(entry_id, f"{ABILITY_KEY}'s band {derived['band']!r}", path)
        sentence = f"Your price is {ability_value(derived)}."
        if ability.get("belief_sentence") != sentence:
            raise _refuse(entry_id, f"founder_calibration[{ABILITY_KEY}].belief_sentence is "
                                    f"{ability.get('belief_sentence')!r}; the engine's is {sentence!r}",
                          path)
    for person in raw.get("answers") or []:
        pick = (person.get("picks") or {}).get(SACRIFICE_KEY)
        if isinstance(pick, dict) and "chip" not in pick and pick.get("period") not in RECALL_PERIODS:
            raise _refuse(entry_id, f"{person.get('person')}'s {SACRIFICE_KEY} pick records period "
                                    f"{pick.get('period')!r}; revision 6 records the recall period it "
                                    f"was asked over, one of {RECALL_PERIODS}", path)


def _check_keys(entry: Entry, registry) -> None:
    """The refusals that need the registry: every dimension-keyed map keyed by the entry's
    calibrated set (calls 47, 59: the registry's thirteen less Purchase friction on a B2C persona),
    every fixed-code founder answer one of the registry's codes (call 51), and
    the file's own plan equal to the one the registry derives per link (data-model §2-§3)."""
    registry_keys = set(registry.keys())
    keys = set(registry.calibrated_keys(entry.b2b()))
    persona = "B2B" if entry.b2b() else "B2C"

    def outside(key) -> str:
        if key not in registry_keys:
            return "which is not a registry key"
        return (f"which a {persona} entry does not calibrate (b2b_only; judgement call 47)")

    for key, value in entry.founder_calibration.items():
        if key not in registry_keys or (value or {}).get("unsure"):
            continue
        fixed = registry.by_key(key).fixed_codes
        answer = (value or {}).get("answer")
        picked = answer if isinstance(answer, list) else [answer] if isinstance(answer, str) else []
        foreign = [c for c in picked if fixed is not None and c not in fixed]
        if foreign:
            raise _refuse(entry.id, f"founder_calibration[{key}] answers {foreign[0]!r}, which is not "
                                    f"one of the registry's codes {fixed} (call 51: Ability to pay's "
                                    "rungs were renamed)", entry.path)
    calibrated = set(entry.founder_calibration)
    for key in sorted(calibrated - keys):
        raise _refuse(entry.id, f"founder_calibration names {key}, {outside(key)}", entry.path)
    if calibrated != keys:
        missing = sorted(keys - calibrated)
        raise _refuse(entry.id, f"founder_calibration is not exactly the {len(keys)} keys a "
                                f"{persona} entry calibrates; missing {', '.join(missing)}",
                      entry.path)
    for person in entry.answers:
        for key in (person.get("picks") or {}):
            if key not in keys:
                raise _refuse(entry.id, f"{person.get('person')} picks {key}, {outside(key)}",
                              entry.path)
    for key in entry.respondent_questions or {}:
        if key not in keys:
            raise _refuse(entry.id, f"respondent_questions carries {key}, {outside(key)}",
                          entry.path)
    standings = set(entry.expected.get("standings") or {})
    for key in sorted(standings - keys):
        raise _refuse(entry.id, f"expected.standings carries {key}, {outside(key)}", entry.path)
    if standings and standings != keys:
        raise _refuse(entry.id, f"expected.standings is not exactly the {len(keys)} calibrated "
                                f"keys; missing {', '.join(sorted(keys - standings))}", entry.path)
    derived = entry.plan(registry)
    for part, plan_keys in derived.items():
        recorded = [k for k, row in (entry.respondent_questions or {}).items()
                    if (row or {}).get("part") == part]
        if sorted(recorded) != sorted(plan_keys):
            raise _refuse(entry.id, f"respondent_questions part {part} holds "
                                    f"{', '.join(recorded) or 'nothing'}; the registry plans "
                                    f"{', '.join(plan_keys) or 'nothing'} (call 30)", entry.path)


def _person(raw: dict) -> Person:
    return Person(person=raw.get("person"), recency=raw.get("recency"),
                  story=raw.get("story") or None, chip=raw.get("chip"),
                  anchoring=raw.get("anchoring"), picks=dict(raw.get("picks") or {}),
                  pilot_opt_in=bool(raw.get("pilot_opt_in")),
                  link=raw.get("link", LINK_PRIMARY))


def _entry(raw: dict, path: Path, digest: str) -> Entry:
    if not isinstance(raw, dict):
        raise CorpusError(f"{path} is not a corpus entry")
    _check_revision(raw, path)
    _check_shape(raw, path)
    return Entry(
        id=raw["id"],
        title=raw.get("title", ""),
        revision=raw["revision"],
        market=raw.get("market") or {},
        statements=raw.get("statements") or {},
        roles=raw.get("roles") or [],
        context=raw.get("context") or {},
        interpretations=raw.get("interpretations") or {},
        solution_mechanism=raw.get("solution_mechanism") or {},
        persona=raw.get("persona") or {},
        founder_calibration=raw.get("founder_calibration") or {},
        respondent_questions=raw.get("respondent_questions") or {},
        answers=raw.get("answers") or [],
        expected=raw.get("expected") or {},
        path=path,
        sha256=digest,
        raw_rate=raw.get("hourly_rate"),
    )
