"""The golden corpus at revision 12, read and never written (spec 029 FR-006/FR-012, data-model §2;
spec 030 FR-002, judgement call 49; ...; spec 038 FR-001, call 81; spec 040 FR-002, call 78; spec 042 call 110;
spec 053 FR-1).

**Revision 12 only** (spec 053; keel-cloud 105): revision 11's rules, and the six GB entries in the US and in dollars
-- *"the currency amount should be dollars, because we are primarily targeting US markets"* (the founder, 2026-10-17):
`market: {country: US, region: <a state or null>, language: en-US}`, every money node `currency: USD` with the same
digits, a few words in the US register; no standing, count or verdict moved. A revision-11 file is refused by name as
v19's and v20's, in pounds. The checker's rule U (every entry US, in dollars) is **not** mirrored here -- the eval's
own fixtures 09 / 10 stay GB on purpose, the reader's one non-US path -- a canon-only unit test holds the canon to it.
What follows is revision 11's account, which r12 keeps:
**Revision 11** (call 110; keel-cloud 091 FR-G): revision 10's rules, and the respondent words a file authors
held to the model's -- every `asked` face says *you* or *your* (`K3`), Commitment's step carries no *you* of its own
(`S10`: code says it as *would you {step}*) -- and 05-paidly's Frequency in its window's unit (months out of 3). A
revision-10 file is refused by name as v18's. What follows is revision 10's account, which r11 keeps:
**Revision 10** (call 78; keel-cloud 087, `design-2026-10-14.md`): **all thirteen dimensions decide**
(D3) -- a vector's verdict is the worst status of every dimension it calibrates, a tie to the first in
registry order, every dimension left out `NOT_TESTED` -- and seven dimensions are the founder's **lists**
(D4, D5, D7): Importance's five (own item first), Current solution's second-person `phrase` and five
outcomes, Compatibility's 2-4 conditions and Adoption friction's 1-4 efforts (each `{code, label, asked}`,
one `picked`), Relative advantage's 1-4 benefits, Buyer and payer's `Nobody else` and at most two roles
(one `picked`), Purchase friction's 1-4 steps on a B2B entry (one `picked`) and Commitment's one `step`.
The stranger answers a **fixed set with one escape** (D2): a respondent row carries its `escape` code, a
fixed-answer row the registry's codes, a pick is a code of its row, two distinct codes on Importance, or
`{chip: <the row's escape>}` -- never Commitment's, which has none. There is **no guessed flag** (D8) and
**no one-unit window** (D13): a recall window counts at least two (`01-countly` {4, WEEKS}, `06-repeatline`
{7, DAYS}), and every entry records `context.occasion`.

`canon/designs/measured-beliefs/corpus/*.yaml` in the keel-cloud checkout is the corpus. This
module opens those files, hashes them on the way in, and offers `verify_unchanged()` so the end of
a run can prove nothing here moved while it ran. **If an instruction cannot reach a golden, the
instruction is wrong** -- or the design is, and it goes back to step 1. Never the corpus.

What this reader checks is the **shape half** of keel-cloud's `sim/check_corpus_r12.py` less r12's new rule U (r11's S, W, L, R
and A rules, and r9's P, K, D, U, O); the recount (its C) is keel-cloud's engine's, asked through
`COMPARE` (`compare_correctness`), and the checker's own -- this repository keeps no copy of the
arithmetic. The registry-bound halves (a list's `saves`, a row's control, codes and escape, a pick's
code) are taken in `Corpus.bind` / `load_file(registry=...)`, against the registry the export carried.

Three things the corpus says (since r3) that the code has to carry:

1. **The plan is derived, and the file's own plan is a check on it** (calls 30, 47). `plan()` is
   the registry's keys asked on each part's link, by part, that the founder did not leave out; the
   file's `respondent_questions` must hold exactly those keys per part, or the file disagrees with the
   registry it is keyed by -- a refusal.
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
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from . import text as text_mod
from .registry import (ABILITY_BANDS, ABILITY_KEY, BENEFIT_CODES, BENEFIT_CONTROL, BENEFIT_KEY,
                       BENEFIT_MAX_TICKS, COMMITMENT_KEY, COST_MODES, COST_TOTAL_CONTROL,
                       FREQUENCY_KEY, IMPORTANCE_KEY, LINK_B2B, LINK_PRIMARY, PERIODS, PRICE_KEY,
                       PRICE_PERIODS, SACRIFICE_KEY, VECTORS, RecallWindow, words)

REVISION = 12

#: The revisions a refusal names by the rubric that read them (calls 49, 51, 78).
_REVISION_OF = {3: "MARKS_VERSION 9's corpus, on the registry of twenty-five",
                4: "MARKS_VERSION 10's corpus, on the registry of twelve (no Price, no units)",
                5: "MARKS_VERSION 11's corpus, before cost first (a tick list for Existing sacrifice, "
                   "Price over month / year / one-off, Ability to pay asked of the founder)",
                6: "MARKS_VERSION 12's corpus, before the buyer's one total (Existing sacrifice a kinds "
                   "tick list with an amount per kind, `branch_pick_amounts`, option counts)",
                7: "MARKS_VERSION 13's and 14's corpus, before direction-aware verdicts (a person beyond the "
                   "founder's band on the supporting side read as outside it; no `stronger` / `short` drift)",
                8: "MARKS_VERSION 15's and 16's corpus, before benefit first (Relative advantage a single choice "
                   "among the founder's advantages, `choice_majority`)",
                9: "MARKS_VERSION 17's corpus, before the October redesign (nine deal-breakers and four SHAPES, "
                   "model-written option sets, chips and `something_else`, a one-unit window)",
                10: "MARKS_VERSION 18's corpus, before keel-cloud 091 (four Compatibility faces with no 'you', "
                    "06-repeatline's 'introduce you to', 05-paidly's Frequency in invoices out of 7)",
                11: "MARKS_VERSION 19's and 20's corpus, in pounds (six GB entries, before keel-cloud 105: "
                    "'the currency amount should be dollars')"}

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
    """`CostEstimate.said`: *about $10 to $30 a month*, or *30 to 60 hours a quarter, about $2,400 to $4,800*."""
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

#: A vector's verdict may also be `NOT_TESTED` (keel-cloud 082 / 087: every dimension of the vector was left
#: out); a dimension's status never is.
VERDICTS = STATUSES + ("NOT_TESTED",)

#: The drift words `expected.standings[*].drift` may carry at revision 10 (`null` beside them). `above` /
#: `below` went with `choice_majority` (keel-cloud 087): no rule reaches them.
DRIFTS = ("both", "none", "stronger", "short")

#: A gate story's chip (the corpus records them as the people gave them; `GUESSED` by code).
CHIPS = ("cant_recall", "rather_not_say")
ANCHORINGS = ("ANCHORED", "GUESSED")

#: The keys revision 2 carried and revision 3 dropped (marks §4 *Dropped*).
R2_KEYS = ("beliefs", "questionnaire", "normalization_rationale")
R2_EXPECTED_KEYS = ("buckets", "stages")

#: The seven dimensions revision 10 reshaped into founder lists (keel-cloud 087's *Corpus revision 10*):
#: no `belief_phrase`, no `labels`.
RESHAPED = ("problem.importance", "problem.current_solution_satisfaction", "solution.compatibility",
            "solution.adoption_friction", "commercial.buyer_payer_alignment",
            "commercial.purchase_friction", "commercial.commitment")
#: The words a list label may never be (`check_corpus_r11.py`'s NOT_SURE).
NOT_SURE = ("not sure", "unsure", "don't know", "dont know", "no idea")
#: A `context.occasion` is a noun of one to four words (rule W).
OCCASION_MAX_WORDS = 4
#: An `asked` clause is at most twenty words and asks nothing (design §4; rule L).
ASKED_MAX_WORDS = 20
_DIGITS = re.compile(r"\d+(?:[.,]\d+)?")
#: r11's K3 and S10 (`check_corpus_r11.py`): a face carries the second person; a Commitment step carries no "you".
_YOU = re.compile(r"(?i)\b(you|your|you'd|you're|yours)\b")
_YOU_ALONE = re.compile(r"(?i)\byou\b")


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
    #: Spec 062 follow-up (2026-10-22): a back-test person's own words for the one follow-up question the interview
    #: owes them, in place of the harness's pooled lines (`vectors_script.FOLLOW_UP_LINES`); golden entries carry none.
    follow_up: str | None = None

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
    #: Spec 062 FR-1: a back-test entry's top-level `idea_name` (what `harness/vectors_script.IDEA_NAMES` carries for a
    #: golden entry -- the name its founder types on S2); `None` on every golden entry.
    idea_name: str | None = None
    #: Spec 062 FR-1: True when the entry was read from the back-test directory (`load(..., backtest=True)`).
    backtest: bool = False

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
        (Mulch Run's per-yard price is on no period of the ladder)."""
        answer = (self.founder_calibration.get(PRICE_KEY) or {}).get("answer")
        return answer if isinstance(answer, dict) else None

    def cost(self) -> dict | None:
        """The founder's cost estimate, `{mode, low, high, rate?, period, currency}`, or `None`."""
        answer = (self.founder_calibration.get(SACRIFICE_KEY) or {}).get("answer")
        return answer if isinstance(answer, dict) else None

    def hourly_rate(self) -> float | None:
        """The B2B entry's top-level `hourly_rate.value` (call 60), else `None`."""
        value = (self.raw_rate or {}).get("value") if isinstance(self.raw_rate, dict) else None
        return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    def occasion(self) -> str | None:
        """`context.occasion` (revision 10, rule W): one time it happens -- *delivery*, *night*."""
        occasion = (self.context or {}).get("occasion")
        return occasion if isinstance(occasion, str) and occasion.strip() else None

    def window(self) -> RecallWindow:
        return RecallWindow.read((self.context or {}).get("recall_window")) or RecallWindow(7, "NIGHTS")

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

    # ------------------------------------------------------------------ the founder's lists

    def founder_list(self, key: str) -> dict | None:
        """A list dimension's saved list (087 FR-007, the lock's `SavedList`): `{items: [{code, label,
        asked?}], picked: int | None, phrase: str | None}`; `None` when left out or not a list."""
        answer = (self.founder_calibration.get(key) or {}).get("answer")
        if not isinstance(answer, dict) or not isinstance(answer.get("items"), list):
            return None
        return {"items": [dict(i) for i in answer["items"] if isinstance(i, dict)],
                "picked": answer.get("picked"), "phrase": answer.get("phrase")}

    def tested(self, key: str) -> dict | None:
        """The one item the founder picked (design §1's *tested item*), or Importance's own item / the
        Commitment step (item 0 of a list with no pick); `None` when the list is absent."""
        saved = self.founder_list(key)
        if not saved or not saved["items"]:
            return None
        picked = saved.get("picked")
        index = picked if isinstance(picked, int) and 0 <= picked < len(saved["items"]) else 0
        return saved["items"][index]

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


def backtest_dir(keel_cloud: Path) -> Path:
    """Spec 062 FR-1: the back-test entries, beside the golden corpus -- real founders' ideas written from public
    material in the corpus schema, with no golden expectations. Read by `make backtest` alone."""
    return Path(keel_cloud) / "canon" / "designs" / "measured-beliefs" / "backtest"


#: Spec 062 FR-1: the two top-level keys a back-test entry may carry and a golden entry never does.
BACKTEST_KEYS = ("idea_name", "sources")
#: keel-cloud `IdeaLines.NAME_MAX_WORDS` (L5): the founder's name for the idea on S2 is at most five words.
IDEA_NAME_MAX_WORDS = 5


def load(keel_cloud: Path, *, registry=None, directory: Path | None = None, backtest: bool = False) -> Corpus:
    """Every `NN-name.yaml` in keel-cloud's corpus directory, in filename order, each at revision
    5 -- one file at another revision refuses the whole corpus, by entry and by key (calls 49, 51).

    Spec 062: `backtest=True` reads the back-test directory (`backtest_dir`, or `directory` when given) instead, every
    file through the same refusals plus FR-1's three differences (`_check_backtest`); an empty or absent back-test
    directory is an empty corpus, never a refusal. A golden load never reads that directory."""
    if backtest:
        directory = Path(directory) if directory is not None else backtest_dir(keel_cloud)
        files = sorted(p for p in directory.glob("*.yaml")) if directory.is_dir() else []
    else:
        directory = Path(directory) if directory is not None else source_dir(keel_cloud)
        if not directory.is_dir():
            raise CorpusError(
                f"no corpus at {directory} -- this eval reads keel-cloud's own golden set, and "
                "cannot invent one")
        files = sorted(p for p in directory.glob("*.yaml"))
        if not files:
            raise CorpusError(f"{directory} holds no *.yaml entries")
    entries, hashes = [], {}
    for path in files:
        entry = load_file(path, registry=registry, backtest=backtest)
        hashes[str(path)] = entry.sha256
        entries.append(entry)
    return Corpus(entries=entries, directory=directory, hashes=hashes)


def load_file(path, *, registry=None, backtest: bool = False) -> Entry:
    """One revision-5 file, checked; bound to `registry` (and checked against it) when given. `backtest` (spec 062):
    a back-test entry -- `expected` absent or empty, `idea_name` required, `sources` ignored."""
    path = Path(path)
    digest = _sha256(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    entry = _entry(raw, path, digest, backtest=backtest)
    if registry is not None:
        _check_keys(entry, registry)
        entry = replace(entry, registry=registry)
    return entry



# ------------------------------------------------------------------------------- the refusals

def _refuse(entry_id, message, path) -> CorpusError:
    return CorpusError(f"{entry_id}: {message} (spec 042; judgement calls 49, 78, 110). {path}")


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


def _out_of(raw: dict):
    """Frequency's axis: the founder's "... out of N" (`check_corpus_r11.py`'s `out_of`), else `None`."""
    answer = ((raw.get("founder_calibration") or {}).get(FREQUENCY_KEY) or {}).get("answer")
    match = re.search(r"out of (\d+)\s*$", str((answer or {}).get("unit") or "") if isinstance(answer, dict) else "")
    return int(match.group(1)) if match else None


def _digits(text) -> set:
    return set(_DIGITS.findall(str(text or "")))


def _check_shape(raw: dict, path: Path) -> None:
    """The registry-free half of `check_corpus_r11.py`'s S, W, L (shape; r11's K3 and S10), A (people) and r9's money
    rules."""
    entry_id = raw.get("id") or path.name
    context = raw.get("context") or {}
    # Rule W (D13): a window of at least two units, never one; an occasion of one to four words.
    try:
        window = RecallWindow.read(context.get("recall_window"))
    except ValueError as why:
        raise _refuse(entry_id, f"context.recall_window: {why}", path) from None
    if window is None:
        raise _refuse(entry_id, "context.recall_window is absent; revision 10 records every entry's window "
                                "(D13: at least two units)", path)
    occasion = context.get("occasion")
    if not isinstance(occasion, str) or not 1 <= words(occasion) <= OCCASION_MAX_WORDS or "?" in occasion:
        raise _refuse(entry_id, f"context.occasion is {occasion!r}; revision 10 records one to "
                                f"{OCCASION_MAX_WORDS} words, no question", path)
    statements = " ".join(str(v) for v in (raw.get("statements") or {}).values())
    for key, value in (raw.get("founder_calibration") or {}).items():
        if not isinstance(value, dict) or not ("answer" in value or value.get("unsure") is True):
            raise _refuse(entry_id, f"founder_calibration[{key}] carries neither `answer` nor "
                                    "`unsure: true`", path)
        if "labels" in value or "units" in value:
            raise _refuse(entry_id, f"founder_calibration[{key}] carries `labels` / `units`; revision 10's "
                                    "lists carry their own labels and there are no kinds", path)
        if key in RESHAPED and "belief_phrase" in value:
            raise _refuse(entry_id, f"founder_calibration[{key}] carries a `belief_phrase`; revision 10 "
                                    "reshaped it into a list (the belief sentence is the template's)", path)
        answer = value.get("answer")
        if key in RESHAPED and not value.get("unsure"):
            if not isinstance(answer, dict) or not isinstance(answer.get("items"), list) \
                    or not answer["items"]:
                raise _refuse(entry_id, f"founder_calibration[{key}].answer is {answer!r}; revision 10 "
                                        "records the founder's list {items: [{code, label}], ...}", path)
        if isinstance(answer, dict) and isinstance(answer.get("items"), list):
            codes = []
            for i, item in enumerate(answer["items"]):
                where = f"founder_calibration[{key}].answer.items[{i}]"
                if not isinstance(item, dict) or not item.get("code") or not str(item.get("label") or "").strip():
                    raise _refuse(entry_id, f"{where} is {item!r}; an item is {{code, label}}", path)
                codes.append(item["code"])
                label = str(item["label"])
                if any(word in label.lower() for word in NOT_SURE):
                    raise _refuse(entry_id, f"{where}.label {label!r} carries a not-sure word", path)
                foreign = sorted(_digits(label) - _digits(statements))
                if foreign:
                    raise _refuse(entry_id, f"{where}.label {label!r} carries {foreign[0]!r}, a number the "
                                            "entry's statements do not (rule L)", path)
                asked = item.get("asked")
                if asked is not None and (not isinstance(asked, str) or not 1 <= words(asked) <= ASKED_MAX_WORDS
                                          or "?" in asked):
                    raise _refuse(entry_id, f"{where}.asked {asked!r} is not a clause of 1 to "
                                            f"{ASKED_MAX_WORDS} words with no question mark", path)
                if asked is not None and not _YOU.search(asked):
                    # r11 (keel-cloud 091, DRIFT #77): a face is said to the stranger -- `K3`.
                    raise _refuse(entry_id, f"{where}.asked {asked!r} is said to the stranger and carries no "
                                            "'you' or 'your' (rule L, K3)", path)
                if key == COMMITMENT_KEY and _YOU_ALONE.search(label):
                    # r11 (keel-cloud 091): code says the step as "would you {step}" -- `S10`.
                    raise _refuse(entry_id, f"{where}.label {label!r} carries 'you'; code says it as "
                                            "'would you {step}' (rule L, S10)", path)
            if len(set(codes)) != len(codes):
                raise _refuse(entry_id, f"founder_calibration[{key}]'s list repeats a code: {codes}", path)
    b2b = isinstance((raw.get("persona") or {}).get("decision_maker"), dict)
    for person in raw.get("answers") or []:
        name = person.get("person")
        recency = person.get("recency")
        link = person.get("link", LINK_PRIMARY)
        for key, pick in (person.get("picks") or {}).items():
            if isinstance(pick, dict) and ("rough" in pick or "rough_guess" in pick):
                raise _refuse(entry_id, f"{name}'s {key} pick carries a guessed flag; D8: numbers are "
                                        "taken as said, there is no guessed flag", path)
            if isinstance(pick, dict) and "somethingElse" in pick or pick == "something_else":
                raise _refuse(entry_id, f"{name}'s {key} pick is 'Something else', which revision 10 "
                                        "deleted (D2)", path)
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
        frequency = (person.get("picks") or {}).get(FREQUENCY_KEY)
        most = _out_of(raw)
        if frequency is not None and not (isinstance(frequency, dict) and "chip" in frequency) and (
                not isinstance(frequency, int) or isinstance(frequency, bool)
                or (most is not None and not 0 <= frequency <= most)):
            raise _refuse(entry_id, f"{name}'s {FREQUENCY_KEY} pick is {frequency!r}; a whole number from 0 "
                                    f"to the founder's out of {most} (rule A)", path)
    _check_price_and_total(raw, entry_id, path)
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
    _check_benefit_first(raw, entry_id, path)
    expected = raw.get("expected") or {}
    for key, standing in (expected.get("standings") or {}).items():
        status = (standing or {}).get("status")
        if status not in STATUSES:
            raise _refuse(entry_id, f"expected.standings[{key}].status is {status!r}, outside "
                                    "Status", path)
        drift = (standing or {}).get("drift")
        if drift is not None and drift not in DRIFTS:
            raise _refuse(entry_id, f"expected.standings[{key}].drift is {drift!r}; revision 10's drifts are "
                                    f"{DRIFTS}", path)
    for vector, verdict in (expected.get("vector_verdicts") or {}).items():
        if vector not in VECTORS:
            raise _refuse(entry_id, f"expected.vector_verdicts names {vector!r}", path)
        word = (verdict or {}).get("verdict")
        if word not in VERDICTS:
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].verdict is {word!r}, outside "
                                    "Status", path)
        deciding = (verdict or {}).get("deciding")
        if word == "NOT_TESTED":
            if deciding is not None:
                raise _refuse(entry_id, f"expected.vector_verdicts[{vector}] is NOT_TESTED and names "
                                        f"{deciding!r}; every dimension was left out", path)
        elif not str(deciding or "").startswith(vector.lower() + "."):
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].deciding is {deciding!r}, not a "
                                    f"{vector} dimension (D3: any of them decides)", path)


def _check_benefit_first(raw: dict, entry_id, path: Path) -> None:
    """Rule B's shape half at revision 10 (call 81 kept, call 78): the founder's Relative advantage is a list of one
    to four distinct benefits `{items: [{code, label}]}` (or `unsure`); its plan row is the code-written benefit
    item; every pick is `{answer, advantages}` with the advantages a non-empty subset of the founder's codes exactly
    under `positive`, or the escape."""
    calibration = (raw.get("founder_calibration") or {}).get(BENEFIT_KEY)
    if calibration is None:
        return
    row = (raw.get("respondent_questions") or {}).get(BENEFIT_KEY)
    if row is not None and (row.get("control") != BENEFIT_CONTROL or list(row.get("codes") or []) != list(BENEFIT_CODES)):
        raise _refuse(entry_id, f"respondent_questions[{BENEFIT_KEY}] is {row.get('control')!r} over codes "
                                f"{row.get('codes')!r}; revision 10 asks {BENEFIT_CONTROL} over "
                                f"{list(BENEFIT_CODES)}", path)
    if calibration.get("unsure"):
        return
    items = (calibration.get("answer") or {}).get("items") if isinstance(calibration.get("answer"), dict) else None
    if not isinstance(items, list) or not 1 <= len(items) <= BENEFIT_MAX_TICKS:
        raise _refuse(entry_id, f"founder_calibration[{BENEFIT_KEY}].answer is {calibration.get('answer')!r}; "
                                f"revision 10 lists one to {BENEFIT_MAX_TICKS} benefits, {{items: [{{code, label}}]}}",
                      path)
    ticks = [i.get("code") for i in items if isinstance(i, dict)]
    for person in raw.get("answers") or []:
        pick = (person.get("picks") or {}).get(BENEFIT_KEY)
        if pick is None or (isinstance(pick, dict) and "chip" in pick):
            continue
        if not isinstance(pick, dict) or pick.get("answer") not in BENEFIT_CODES:
            raise _refuse(entry_id, f"{person.get('person')}'s {BENEFIT_KEY} pick is {pick!r}; revision 10 "
                                    f"answers {{answer: {' | '.join(BENEFIT_CODES)}, advantages: [...]}}", path)
        advantages = pick.get("advantages") or []
        if (pick["answer"] == "positive") != bool(advantages) or not set(advantages) <= set(ticks):
            raise _refuse(entry_id, f"{person.get('person')}'s {BENEFIT_KEY} pick {pick!r}: its advantages are "
                                    f"a non-empty subset of the founder's {ticks} exactly under positive", path)


def _check_price_and_total(raw: dict, entry_id, path: Path) -> None:
    """Revision 5's Price checks (call 51; `check_corpus_r5.py`'s P): the founder's Price on the ladder
    in the market's currency, its plan row the ladder's codes, every price pick a row code; and revision
    7's Existing sacrifice (call 68; `check_corpus_r7.py`'s O): no kinds, `cost_total`, one total a pick."""
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
    row = plan.get(SACRIFICE_KEY)
    if row is not None and (row.get("control") != COST_TOTAL_CONTROL or row.get("codes")
                            or row.get("units")):
        raise _refuse(entry_id, f"respondent_questions[{SACRIFICE_KEY}] is {row.get('control')!r} with "
                                f"codes {row.get('codes')!r}; revision 7 asks {COST_TOTAL_CONTROL}, "
                                "with no codes and no units", path)
    price_codes = [str(c) for c in (plan.get(PRICE_KEY) or {}).get("codes") or []]
    for person in raw.get("answers") or []:
        picks = person.get("picks") or {}
        name = person.get("person")
        pick = picks.get(SACRIFICE_KEY)
        if pick is not None and not (isinstance(pick, dict) and "chip" in pick):
            value = pick.get("value") if isinstance(pick, dict) else None
            if not isinstance(pick, dict) or "amounts" in pick or not (
                    pick.get("nothing") is True or (
                        pick.get("mode") in COST_MODES and isinstance(value, (int, float))
                        and not isinstance(value, bool) and value >= 0)):
                raise _refuse(entry_id, f"{name}'s {SACRIFICE_KEY} pick is {pick!r}; revision 7 answers "
                                        "{mode: AMOUNT | HOURS, value, currency, period}, "
                                        "{nothing: true, currency, period} or {chip}", path)
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
                                    "(since revision 6)", path)
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
                                f"it is the cost estimate's, {cost.get('period')!r} (since revision 6)", path)
    ability = calibration.get(ABILITY_KEY)
    if ability is None:
        raise _refuse(entry_id, f"founder_calibration lacks {ABILITY_KEY}; it is derived and "
                                "calibrated on every entry (since revision 6)", path)
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
    if "optionCounts" in ((raw.get("expected") or {}).get("standings") or {}).get(SACRIFICE_KEY, {}):
        raise _refuse(entry_id, f"expected.standings[{SACRIFICE_KEY}] records optionCounts; revision 7 "
                                "has no kinds to count", path)
    for person in raw.get("answers") or []:
        pick = (person.get("picks") or {}).get(SACRIFICE_KEY)
        if isinstance(pick, dict) and "chip" not in pick and pick.get("period") not in RECALL_PERIODS:
            raise _refuse(entry_id, f"{person.get('person')}'s {SACRIFICE_KEY} pick records period "
                                    f"{pick.get('period')!r}; revision 7 records the recall period it "
                                    f"was asked over, one of {RECALL_PERIODS}", path)


def _check_list(entry: Entry, registry, key: str) -> None:
    """Rule L, against the registry's `founder.saves` (087 FR-007): the count (a fixed first item -- Buyer and
    payer's `Nobody else` -- among it), the words an item, `picked` exactly where the registry picks one and in
    range, the `phrase` exactly where it carries one, an `asked` face on every item exactly where it asks."""
    dimension = registry.by_key(key)
    saves = dimension.saves
    saved = entry.founder_list(key)
    if saved is None:
        raise _refuse(entry.id, f"founder_calibration[{key}] is a {dimension.founder_control} with no list",
                      entry.path)
    items = saved["items"]
    low, high = saves.get("min_items", 1), saves.get("max_items", len(items))
    if not low <= len(items) <= high:
        raise _refuse(entry.id, f"founder_calibration[{key}] lists {len(items)} items; the registry saves "
                                f"{low} to {high}", entry.path)
    for i, item in enumerate(items):
        if words(item.get("label")) > saves.get("max_words", 9):
            raise _refuse(entry.id, f"founder_calibration[{key}].items[{i}].label {item.get('label')!r} is "
                                    f"{words(item.get('label'))} words; the registry saves at most "
                                    f"{saves.get('max_words')}", entry.path)
        if bool(saves.get("asked")) != bool(item.get("asked")):
            raise _refuse(entry.id, f"founder_calibration[{key}].items[{i}] "
                                    f"{'lacks' if saves.get('asked') else 'carries'} an `asked` face; the "
                                    f"registry {'asks' if saves.get('asked') else 'does not ask'} one", entry.path)
    first = saves.get("fixed_first")
    if first and (not items or (items[0].get("code"), items[0].get("label")) != (first.get("code"),
                                                                                first.get("label"))):
        raise _refuse(entry.id, f"founder_calibration[{key}]'s item 0 is {items[0] if items else None!r}; the "
                                f"registry fixes it as {first!r}", entry.path)
    picked = saved.get("picked")
    if saves.get("picked"):
        if not isinstance(picked, int) or isinstance(picked, bool) or not 0 <= picked < len(items):
            raise _refuse(entry.id, f"founder_calibration[{key}].picked is {picked!r}; the founder picks one "
                                    f"of the {len(items)} items (D7)", entry.path)
    elif picked is not None:
        raise _refuse(entry.id, f"founder_calibration[{key}] carries `picked`; the registry picks none on a "
                                f"{dimension.founder_control}", entry.path)
    if bool(saves.get("phrase")) != bool(str(saved.get("phrase") or "").strip()):
        raise _refuse(entry.id, f"founder_calibration[{key}] {'lacks' if saves.get('phrase') else 'carries'} a "
                                "`phrase`", entry.path)


def _check_row(entry: Entry, registry, key: str, row: dict) -> None:
    """Rule R, against the registry (087 FR-001, 088): the row's control and escape are the registry's; a fixed
    answer set is the registry's codes in order; Importance's codes are the founder's five with `own_item` its item 0;
    Current solution's the founder's five outcomes in order."""
    dimension = registry.by_key(key)
    if row.get("control") != dimension.respondent_control:
        raise _refuse(entry.id, f"respondent_questions[{key}].control is {row.get('control')!r}; the registry's is "
                                f"{dimension.respondent_control!r}", entry.path)
    escape = (dimension.escape or {}).get("code")
    if row.get("escape") != escape:
        raise _refuse(entry.id, f"respondent_questions[{key}].escape is {row.get('escape')!r}; the registry's one "
                                f"escape is {escape!r}", entry.path)
    codes = list(row.get("codes") or [])
    if dimension.fixed_answers and codes != dimension.fixed_answer_codes:
        raise _refuse(entry.id, f"respondent_questions[{key}].codes are {codes}; the registry fixes "
                                f"{dimension.fixed_answer_codes}", entry.path)
    saved = entry.founder_list(key)
    if key == IMPORTANCE_KEY and saved:
        own = saved["items"][0].get("code")
        if row.get("own_item") != own or sorted(codes) != sorted(i.get("code") for i in saved["items"]):
            raise _refuse(entry.id, f"respondent_questions[{key}] asks {codes} with own item "
                                    f"{row.get('own_item')!r}; the founder's five are "
                                    f"{[i.get('code') for i in saved['items']]}, own first", entry.path)
    if dimension.respondent_control == "single_choice_5" and saved \
            and codes != [i.get("code") for i in saved["items"]]:
        raise _refuse(entry.id, f"respondent_questions[{key}].codes are {codes}; the founder's five outcomes in "
                                f"order are {[i.get('code') for i in saved['items']]}", entry.path)


def _check_pick(entry: Entry, registry, person: dict, key: str, pick) -> None:
    """Rule A's pick shapes (087 FR-004, D2, D8): an escape is exactly `{chip: <the row's escape>}` (Commitment has
    none); Importance two distinct codes of its row; a fixed answer, a Current solution outcome or a Price band one
    code of its row."""
    row = (entry.respondent_questions or {}).get(key) or {}
    name = person.get("person")
    if isinstance(pick, dict) and "chip" in pick:
        escape = (registry.by_key(key).escape or {}).get("code")
        if escape is None or pick.get("chip") != escape or set(pick) != {"chip"}:
            raise _refuse(entry.id, f"{name}'s {key} pick is {pick!r}; its one escape is {escape!r}"
                                    + (" (Commitment has none)" if key == COMMITMENT_KEY else ""), entry.path)
        return
    control = row.get("control")
    codes = [str(c) for c in row.get("codes") or []]
    if control == "pick_two":
        if not isinstance(pick, list) or len(pick) != 2 or len(set(pick)) != 2 \
                or not set(map(str, pick)) <= set(codes):
            raise _refuse(entry.id, f"{name}'s {key} pick is {pick!r}; Importance is two distinct codes of "
                                    f"{codes}", entry.path)
    elif control in ("fixed_four", "fixed_three", "single_choice_5", "single_choice") and codes:
        if not isinstance(pick, str) or pick not in codes:
            raise _refuse(entry.id, f"{name}'s {key} pick is {pick!r}, not one of {codes}", entry.path)


def _check_keys(entry: Entry, registry) -> None:
    """The refusals that need the registry: every dimension-keyed map keyed by the entry's calibrated set (calls
    47, 59), every fixed-code founder answer one of the registry's codes, every list against its `saves` (L),
    every row against the registry (R), every pick its row's (A), and the file's own plan equal to the one the
    registry derives per link (data-model §2-§3)."""
    registry_keys = set(registry.keys())
    keys = set(registry.calibrated_keys(entry.b2b()))
    persona = "B2B" if entry.b2b() else "B2C"

    def outside(key) -> str:
        if key not in registry_keys:
            return "which is not a registry key"
        return f"which a {persona} entry does not calibrate (b2b_only; judgement call 47)"

    for key, value in entry.founder_calibration.items():
        if key not in registry_keys or (value or {}).get("unsure"):
            continue
        dimension = registry.by_key(key)
        fixed = dimension.fixed_codes
        answer = (value or {}).get("answer")
        if fixed is not None and isinstance(answer, str) and answer not in fixed:
            raise _refuse(entry.id, f"founder_calibration[{key}] answers {answer!r}, which is not one of the "
                                    f"registry's codes {fixed}", entry.path)
        if dimension.founder_list:
            _check_list(entry, registry, key)
    calibrated = set(entry.founder_calibration)
    for key in sorted(calibrated - keys):
        raise _refuse(entry.id, f"founder_calibration names {key}, {outside(key)}", entry.path)
    if calibrated != keys:
        missing = sorted(keys - calibrated)
        raise _refuse(entry.id, f"founder_calibration is not exactly the {len(keys)} keys a "
                                f"{persona} entry calibrates; missing {', '.join(missing)}",
                      entry.path)
    for key, row in (entry.respondent_questions or {}).items():
        if key not in keys:
            raise _refuse(entry.id, f"respondent_questions carries {key}, {outside(key)}", entry.path)
        _check_row(entry, registry, key, row or {})
    for person in entry.answers:
        for key, pick in (person.get("picks") or {}).items():
            if key not in keys:
                raise _refuse(entry.id, f"{person.get('person')} picks {key}, {outside(key)}",
                              entry.path)
            _check_pick(entry, registry, person, key, pick)
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
                  link=raw.get("link", LINK_PRIMARY),
                  follow_up=(str(raw.get("follow_up")).strip() or None) if raw.get("follow_up") else None)


def _check_backtest(raw: dict, path: Path, backtest: bool) -> None:
    """Spec 062 FR-1, the only differences between a back-test entry and a golden one: `expected` absent or empty,
    a top-level `idea_name` (the founder's name for the idea, at most five words), and `sources` (ignored). A golden
    entry carries neither key; a back-test entry carries no golden expectations."""
    entry_id = raw.get("id") or path.name
    if not backtest:
        for key in BACKTEST_KEYS:
            if key in raw:
                raise _refuse(entry_id, f"carries `{key}`, a back-test key (spec 062); a golden entry names its "
                                        "idea through IDEA_NAMES and carries no sources", path)
        return
    expected = raw.get("expected")
    if expected not in (None, {}):
        raise _refuse(entry_id, "carries `expected`; a back-test entry has no golden expectations (spec 062 FR-1: "
                                "the verdict is the finding) -- remove the block or leave it empty", path)
    name = raw.get("idea_name")
    if not isinstance(name, str) or not name.strip():
        raise _refuse(entry_id, f"idea_name is {name!r}; a back-test entry names its idea as the founder types it "
                                "on S2 (spec 062 FR-1)", path)
    if len(name.split()) > IDEA_NAME_MAX_WORDS:
        raise _refuse(entry_id, f"idea_name {name!r} is {len(name.split())} words; the founder's name for the idea "
                                f"is at most {IDEA_NAME_MAX_WORDS} (keel-cloud IdeaLines L5)", path)


def _entry(raw: dict, path: Path, digest: str, *, backtest: bool = False) -> Entry:
    if not isinstance(raw, dict):
        raise CorpusError(f"{path} is not a corpus entry")
    _check_revision(raw, path)
    _check_backtest(raw, path, backtest)
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
        idea_name=(raw.get("idea_name").strip() if backtest else None),
        backtest=backtest,
    )
