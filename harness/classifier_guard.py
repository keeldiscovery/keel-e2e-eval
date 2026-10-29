"""The classifier guard (spec 048 FR-3, and FR-2's live check): the 170 spoken-answer cases of
`harness/classifier_cases.py` sent to a real `classify` route -- the stack's (keel-cloud 099's `FakeClassifier`, which
every `fake-for` founder and every keyless box gets) or, in the weekly live column, staging's for a founder outside
`fake-for` (Keel's AI on the light tier) -- and judged the way keel-cloud's `FakeClassifierCasesTest` judges them:

* **right** -- what a careful human would record (`matches`, the port of that test's `matches`);
* **safe** -- not right, but `unclear` or below `high`: the didn't-catch path or "Is that right?", never a wrong row;
* **wrong** -- a confident wrong answer. The guard's one bar: **none**. The four corrections the old matcher recorded
  wrong with confidence (`CORRECTIONS`) must come back right.

Spec 049 (keel-cloud 100): the copy gains the group `readaloud` -- they read the question or the options aloud, then
answer -- held to the same bar (never a confident wrong answer) and counted on its own (`Report.groups`).

**The cases are carried onto the link's own items** (judgement call 1 of spec 048's guard). The route builds the
question from the item the link serves -- the page never sends labels (keel-cloud 099 FR-1) -- so a case written
against the check's payroll item can only be asked of a served item of the same kind, and its words must point at the
served labels the way they pointed at the case's. `transpose` does exactly that and nothing more: a whole label said
becomes the served label at the same place; each remaining word of a case label becomes a served-label word that sits
in **the same set of places** (a word only label 2 has becomes a word only served label 2 has; "payroll", in labels 1
and 5, becomes a word served labels 1 and 5 share); the escape's words become the served escape's; every other word is
kept. The expected answer is positional, so it carries over unchanged. A case whose words cannot be carried that way
(no served word sits in those places, a kept word that a served label also carries, a range or unit that differs) is
**not asked**, and is named with its reason -- never counted as a pass.

Machinery, not judgement: `run` returns the outcomes, the leg (`evals/interviewer_leg.py`) and the live check
(`evals/test_classifier_live.py`) assert.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from harness import classifier_cases as cases

#: keel-cloud `FakeClassifierCasesTest.CORRECTIONS`: must pass outright, wherever they can be asked.
CORRECTIONS = ("the first one wait actually the third", "option 4 instead of 3", "not the second, the fourth",
               "three days, no wait, five")

#: keel-cloud 099 design §6: about 500 input + 60 output tokens on Haiku 4.5 -- the live check's budget arithmetic.
COST_PER_CALL_USD = 0.0006
LIVE_BUDGET_USD = 0.10

#: Every reason keel-cloud's FakeClassifier and `Classification.validated` write (099 at keel-cloud-docs 0f582b2, 100's
#: three at d2f00d4;
#: `tests/test_classifier_guard.py` holds this to the source where the checkout carries it). A live run whose every
#: reason is one of these was answered by the fake -- its founder is in `fake-for` -- and proves nothing of the model.
FAKE_REASONS = frozenset({
    "a unit that is neither an amount nor hours", "agreed", "all except", "all of them", "amount",
    "both an amount and hours", "both", "correction", "escape", "inside a label", "key words",
    "no amount or hours heard", "no amount or hours", "no number heard", "no number", "no option matched", "no unit",
    "no yes or no heard", "not one of the options", "nothing heard", "ordinal", "out of range", "replaced",
    "the label said", "the story is not classified", "two answers", "two labels fit", "unclear", "which one?",
    "yes or no", "number", "two numbers heard", "hours", "minutes as hours", "days as hours", "a day", "an hour",
    "half a day", "half an hour", "a day and a half", "days and a half", "part of a day",
    # keel-cloud 100: a yes and a no heard with no correction between; the options read aloud and none settled on;
    # what follows the last pause, read at most medium
    "yes and no heard", "read the options aloud, settled on none", "read aloud first", ""})
#: What keel-cloud's KeelsAiClassifier answers when the model did not (099 FR-2: never an error to the page).
FAILED_REASONS = frozenset({"timeout", "vendor"})


def fake_reason(reason: str | None) -> bool:
    return (reason or "") in FAKE_REASONS or (reason or "").startswith("more than ")


# ------------------------------------------------------------------- keel-cloud FakeClassifier's word rules, restated

_STOP = {"the", "a", "an", "of", "in", "on", "to", "it", "and", "or", "from", "again", "their", "your", "my", "was",
         "were", "did", "does", "under", "with", "that", "this", "had", "have", "put", "took", "its", "still", "never",
         "where", "came", "into", "down", "out", "up", "would", "made", "been", "before", "less", "more", "any", "not",
         "one", "ones", "uh", "um", "erm", "hmm"}
_NUMBER_WORDS = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
                 "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
                 "nought", "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
                 "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"}
_ORDINALS = {"first", "second", "third", "fourth", "fifth", "sixth", "1st", "2nd", "3rd", "4th", "5th"}
#: Words that carry the turn rather than an option -- agreement (FakeClassifier `AGREE`), corrections (`MARKER`,
#: `INSTEAD_OF`, `SWAP`), counting and places ("all", "both", "last", "option") -- never carried onto a served word,
#: even where a check label happens to hold one ("Got it *right* after one wrong guess"; "that's right").
_PROTECTED = {"yes", "yeah", "yep", "yup", "right", "correct", "exactly", "sure", "absolutely", "definitely", "totally",
              "perfect", "okay", "fine", "good", "that's", "thats", "actually", "wait", "sorry", "mean", "make",
              "scratch", "hang", "instead", "swap", "replace", "change", "all", "both", "every", "each", "except",
              "but", "last", "option", "number", "none", "nope", "nah", "never"}
#: A currency said (FakeClassifier `CURRENCY`, and the symbols its fold reads).
_CURRENCY = re.compile(r"\$|£|€|\b(dollars?|bucks|usd|d[oó]lares|pounds?|quid|gbp|euros?|eur)\b", re.I)


def _norm(text: str) -> str:
    text = (text or "").replace("’", "'").lower()
    return " ".join(re.findall(r"[a-z0-9áéíóúñü']+", text))


def _significant(word: str) -> bool:
    return len(word) >= 3 and word not in _STOP and word not in _NUMBER_WORDS and word not in _ORDINALS


def _sig(label: str) -> list[str]:
    return [w for w in _norm(label).split() if _significant(w)]


def _singular(word: str) -> str:
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


def same(a: str, b: str) -> bool:
    """FakeClassifier `same`: equal, equal but for a plural, or the same first six letters of two long words."""
    return a == b or _singular(a) == _singular(b) or (len(a) >= 6 and len(b) >= 6 and a[:6] == b[:6])


def _places(word: str, labels: list[str]) -> frozenset[int]:
    """The 1-based places of the labels a word sits in (by `same`)."""
    return frozenset(i + 1 for i, label in enumerate(labels) if any(same(word, w) for w in _sig(label)))


# ------------------------------------------------------------------------------------------------- the cases

@dataclass(frozen=True)
class Case:
    group: str
    item: str
    said: str
    expected: dict
    previous: tuple[int, ...] | None = None

    @property
    def name(self) -> str:
        prev = f" (after {list(self.previous)})" if self.previous else ""
        return f"{self.item}: {self.said!r}{prev}"


def all_cases() -> list[Case]:
    """The 155 answers (137 of 099, 18 `readaloud` of 100) and the 15 confirmation turns, in the check's order."""
    out = [Case(group, item, said, expected) for group, item, said, expected in cases.CASES]
    out += [Case("confirm", item, said, expected, tuple(previous) if previous else None)
            for item, previous, said, expected in cases.CONFIRM]
    return out


# -------------------------------------------------------------------------------------------- the served items

@dataclass(frozen=True)
class Served:
    """One question a link serves, as keel-cloud's `SpokenItem.of` reads it (099 FR-2's table)."""
    item_id: str
    dimension: str
    kind: str                       # gate | number | single | multi | amount_or_hours
    options: tuple[str, ...] = ()
    escape: str | None = None
    pick: int = 0
    low: int | None = None
    high: int | None = None
    unit: str | None = None
    currency: str | None = None
    ask: str | None = None          # "second" for Importance's second ask (keel-cloud 158 T014)

    @property
    def shape(self) -> str:
        return f"{self.dimension}{'/' + self.ask if self.ask else ''} ({self.kind}, {len(self.options)} options)"


_FROM_TO = re.compile(r"from\s+(\d+)\s+to\s+(\d+)", re.I)
_OUT_OF = re.compile(r"out of\s+(\d+)", re.I)
#: Importance's controls: keel-cloud 158's `pick_one_then_one` (contract 46) and `pick_two` as served before it.
PICK_CONTROLS = ("pick_one_then_one", "pick_two")
#: Frequency's controls: keel-cloud 158's `segmented_1_to_n` (contract 46: a count from 1) and the number box, and
#: `segmented_0_to_7`, which a run recorded before 46 served.
FREQUENCY_CONTROLS = ("segmented_1_to_n", "segmented_0_to_7", "number_with_unit")
_SINGLE = {"single_choice", "single_choice_5", "fixed_four", "fixed_three", "price_ladder", "scale_four"}


def _range(item: dict) -> tuple[int | None, int | None]:
    scale = item.get("scale")
    if scale:
        return int(scale["min"]), int(scale["max"])
    line = ((item.get("spoken") or {}).get("optionsLine")) or ""
    m = _FROM_TO.search(line)
    if m:
        return int(m.group(1)), int(m.group(2))
    # keel-cloud 158 (contract 46): a number box serves its least count (`numeric.min` 1); one served before 46 has none
    numeric = item.get("numeric") or {}
    low = int(numeric["min"]) if numeric.get("min") is not None else 0
    m = _OUT_OF.search(numeric.get("defaultUnit") or "")
    return (low, int(m.group(1))) if m else (low, None)


def served_items(interview: dict, market_currency: str | None = None) -> list[Served]:
    """Every question of a served `Interview` the classifier reads -- the gate, each item, and Importance's second ask
    (keel-cloud 158 `ask: second`; 159 retired the advantages ask with `benefit_with_advantages`) -- built exactly as
    keel-cloud `SpokenItem.of` builds them. The story is never
    classified, so it is not here."""
    out: list[Served] = []
    gate = interview.get("gate") or {}
    if gate.get("itemId"):
        out.append(Served(gate["itemId"], gate.get("dimension") or "gate", "gate", ("Yes", "No")))
    for part in interview.get("parts") or []:
        for item in part.get("items") or []:
            control = item.get("control") or ""
            options = tuple(o.get("label") for o in item.get("options") or [])
            escape = (item.get("escape") or {}).get("label")
            base = dict(item_id=item.get("itemId"), dimension=item.get("dimension") or "")
            if control in PICK_CONTROLS:
                out.append(Served(**base, kind="multi", options=options, escape=escape, pick=2))
                second = item.get("secondAsk")
                if control == "pick_one_then_one" and second:
                    # keel-cloud 158 T014 (`ask: second`): the second ask reads one pick over the same labels, with
                    # its own escape *Nothing else* -- never *None of these*
                    out.append(Served(**base, kind="single", options=options,
                                      escape=(second.get("escape") or {}).get("label"), ask="second"))
            elif control in FREQUENCY_CONTROLS:
                low, high = _range(item)
                out.append(Served(**base, kind="number", escape=escape, low=low, high=high,
                                  unit=(item.get("numeric") or {}).get("defaultUnit")))
            elif control == "cost_total":
                out.append(Served(**base, kind="amount_or_hours", escape=escape,
                                  currency=(item.get("costTotal") or {}).get("currency") or market_currency))
            else:
                out.append(Served(**base, kind="single", options=options, escape=escape))
    return out


def case_item(key: str) -> Served:
    """A check item (`classifier_cases.ITEMS`) as a `Served`, for the identity transposition the unit tests read."""
    raw = cases.ITEMS[key]
    rng = raw.get("range") or [None, None]
    return Served(item_id=key, dimension=key, kind=raw["kind"], options=tuple(raw.get("options") or ()),
                  escape=raw.get("escape"), pick=int(raw.get("pick") or 0), low=rng[0], high=rng[1],
                  unit="days ago" if raw["kind"] == "number" else None,
                  currency="USD" if raw["kind"] == "amount_or_hours" else None)


# -------------------------------------------------------------------------------------------- the transposition

@dataclass(frozen=True)
class Asked:
    """One case carried onto one served item: what is said, what is held, and what a careful human would record."""
    case: Case
    served: Served
    said: str
    previous: list[str] | None
    expected: dict


@dataclass(frozen=True)
class NotAsked:
    case: Case
    reason: str


def _same_shape(item: Served, served: Served) -> str | None:
    if item.kind != served.kind:
        return f"no served {item.kind}"
    if item.kind in ("single", "multi") and len(item.options) != len(served.options):
        return f"no served {item.kind} of {len(item.options)} options"
    if item.kind == "multi" and item.pick != served.pick:
        return f"no served pick-{item.pick or 'any'}"
    return None


_TIME_WORD = re.compile(r"\b(days?|weeks?|months?|years?|yesterday|today|tonight|ago|hace|d[ií]as?)\b", re.I)
_DIGIT_OR_WORD = re.compile(r"\d|\b(" + "|".join(sorted(_NUMBER_WORDS)) + r")\b", re.I)


def _values(expected: dict) -> list[dict]:
    return [v for e in expected["any"] for v in _values(e)] if "any" in expected else [expected]


def _number_fits(case: Case, item: Served, served: Served) -> str | None:
    """A number case is asked of a served number with the check's own range and days as is; of another range only
    when nothing in it is a time ("yesterday" is a day only where days are asked) and what it expects is a value in
    that range, the escape, or unclear with no number said at all ("quite a lot")."""
    if (item.low, item.high) == (served.low, served.high) and "day" in (served.unit or ""):
        return None
    if _TIME_WORD.search(case.said):
        return f"a time said, and the served number is not days from {item.low} to {item.high}"
    lo, hi = served.low if served.low is not None else 0, served.high
    for v in _values(case.expected):
        if "value" in v and not (lo <= float(v["value"]) and (hi is None or float(v["value"]) <= hi)):
            return f"{v['value']} is outside the served range {lo} to {hi}"
        if v.get("unclear") and _DIGIT_OR_WORD.search(case.said):
            return f"unclear only out of the check's range {item.low} to {item.high}"
    return None


#: Marks a served label or escape put in whole: kept as it stands, never mapped word by word.
_KEPT = "\x00"
_WORD = re.compile(r"[a-z0-9áéíóúñü']+")
_TOKEN = re.compile(r"[a-z0-9áéíóúñü']+|[^a-z0-9áéíóúñü']+")


def _tokens(text: str) -> list[str]:
    """Words and what lies between them, so the commas and dots the classifier reads ("no, the second"; "not the
    second, the fourth") are kept exactly where they were said."""
    return _TOKEN.findall((text or "").replace("’", "'").lower())


def _replace_phrase(tokens: list[str], phrase: str, new: str) -> tuple[list[str], bool]:
    """Every run of words equal to `phrase`'s (whatever lies between them) replaced by `new`, as one kept token."""
    want = _norm(phrase).split()
    if not want:
        return tokens, False
    words = [i for i, tok in enumerate(tokens) if _WORD.fullmatch(tok)]
    for k in range(len(words) - len(want) + 1):
        if [tokens[words[k + j]] for j in range(len(want))] == want:
            first, last = words[k], words[k + len(want) - 1]
            replaced = tokens[:first] + [_KEPT + new.lower().replace("’", "'")] + tokens[last + 1:]
            return _replace_phrase(replaced, phrase, new)[0], True
    return tokens, False


def _has_run(text: str, phrase: str) -> bool:
    want = _norm(phrase)
    return bool(want) and f" {want} " in f" {_norm(text)} "


def transpose(case: Case, served: Served) -> Asked | NotAsked:
    """`case` asked of `served`, or the reason it cannot be (see the module docstring)."""
    item = case_item(case.item)
    wrong = _same_shape(item, served) or (_number_fits(case, item, served) if item.kind == "number" else None)
    if wrong:
        return NotAsked(case, wrong)
    tokens = _tokens(case.said)
    expected = dict(case.expected)
    case_escape, served_escape = item.escape, served.escape
    if case.expected.get("escape") and not served_escape:
        return NotAsked(case, "the served item has no escape")
    if case_escape and served_escape and _norm(case_escape) != _norm(served_escape):
        tokens, said_it = _replace_phrase(tokens, case_escape, served_escape)
        if not said_it and case.expected.get("escape"):
            return NotAsked(case, f"the escape said in other words than {served_escape!r}")
    # whole labels first (kept whole), then each remaining label word to a served word in the same places
    whole: set[int] = set()
    for i, label in enumerate(item.options):
        if _norm(label) != _norm(served.options[i]):
            tokens, said_it = _replace_phrase(tokens, label, served.options[i])
        else:
            said_it = _has_run(case.said, label)
        if said_it:
            whole.add(i)
    served_words = {w for o in served.options for w in _sig(o)}
    out: list[str] = []
    swapped: dict[str, str] = {}
    for tok in tokens:
        if tok.startswith(_KEPT):
            out.append(tok[1:])
            continue
        if not _WORD.fullmatch(tok) or not _significant(tok):
            out.append(tok)
            continue
        places = _places(tok, list(item.options))
        if places == _places(tok, list(served.options)):
            out.append(tok)                             # it points where it pointed (or nowhere, on both)
            continue
        if tok in _PROTECTED and not _places(tok, list(served.options)):
            out.append(tok)                             # a turn word, pointing at no served label
            continue
        if not places or tok in _PROTECTED:
            return NotAsked(case, f"{tok!r} points at served labels {sorted(_places(tok, list(served.options)))} "
                                  f"and at check labels {sorted(places)}")
        if tok not in swapped:
            pool = sorted({s for s in served_words if _places(s, list(served.options)) == places}
                          - set(swapped.values()), key=lambda s: (s != tok, not same(tok, s), s))
            if not pool:
                return NotAsked(case, f"no served word sits where {tok!r} does (labels {sorted(places)})")
            # a word the served labels carry already (give or take a plural) is kept as said
            swapped[tok] = tok if same(tok, pool[0]) else pool[0]
        out.append(swapped[tok])
    said = "".join(out).strip()
    # a served label said whole that the case did not say whole ("no" against a served "No") reads otherwise
    for i, label in enumerate(served.options):
        if i not in whole and _has_run(said, label):
            return NotAsked(case, f"what is said holds the served label {label!r} whole")
    # an amount said with no currency is the market's (FakeClassifier and 099 FR-3), not the check's US dollar
    if served.kind == "amount_or_hours" and not _CURRENCY.search(case.said):
        expected = _with_currency(expected, served.currency)
    previous = None
    if case.previous:
        previous = [served.options[n - 1] for n in case.previous] if served.options else [str(n) for n in case.previous]
    return Asked(case, served, said, previous, expected)


def _with_currency(expected: dict, currency: str | None) -> dict:
    if "any" in expected:
        return {"any": [_with_currency(e, currency) for e in expected["any"]]}
    if expected.get("unit") == "AMOUNT" and currency and expected.get("currency") == "USD":
        return {**expected, "currency": currency}       # the check's own default; a currency it named stays
    return expected


def plan(served: Iterable[Served], chosen: Iterable[Case] | None = None) -> tuple[list[Asked], list[NotAsked]]:
    """Each case on the first served item it can be carried onto (the gate's on the gate, and so on)."""
    served = list(served)
    asked: list[Asked] = []
    skipped: list[NotAsked] = []
    for case in chosen if chosen is not None else all_cases():
        reasons = []
        own = tuple(_norm(o) for o in case_item(case.item).options)
        # a served item carrying the check's own labels first (code's own words, word for word)
        for s in sorted(served, key=lambda s: tuple(_norm(o) for o in s.options) != own):
            got = transpose(case, s)
            if isinstance(got, Asked):
                asked.append(got)
                break
            reasons.append(f"{s.shape}: {got.reason}")
        else:
            skipped.append(NotAsked(case, "; ".join(reasons) or "the link serves no item"))
    return asked, skipped


# -------------------------------------------------------------------------------------------------- the judge

def matches(served: Served, expected: dict, got: dict) -> bool:
    """keel-cloud `FakeClassifierCasesTest.matches`: the expected shape read off a `Classification`."""
    if "any" in expected:
        return any(matches(served, one, got) for one in expected["any"])
    if expected.get("agree"):
        return bool(got.get("agree"))
    if got.get("agree"):
        return False
    if expected.get("unclear"):
        return bool(got.get("unclear"))
    if got.get("unclear"):
        return False
    if expected.get("escape"):
        return bool(got.get("escape"))
    if got.get("escape"):
        return False
    if "picks" in expected:
        have = sorted(list(served.options).index(p) + 1 for p in got.get("picks") or [] if p in served.options)
        return len(have) == len(got.get("picks") or []) and have == sorted(expected["picks"])
    if "value" in expected:
        if got.get("value") is None or abs(float(got["value"]) - float(expected["value"])) > 1e-9:
            return False
        if "unit" not in expected:
            return True
        if expected["unit"] != got.get("unit"):
            return False
        return "currency" not in expected or expected["currency"] == got.get("currency")
    return False


def verdict(asked: Asked, got: dict) -> str:
    """right, safe (unclear or below high), or wrong (a confident wrong answer)."""
    if matches(asked.served, asked.expected, got):
        return "right"
    if got.get("unclear") or got.get("confidence") != "high":
        return "safe"
    return "wrong"


@dataclass
class Outcome:
    asked: Asked
    status: int
    got: dict
    verdict: str

    def row(self) -> dict:
        return {"case": self.asked.case.name, "item": self.asked.served.shape, "said": self.asked.said,
                "previous": self.asked.previous, "expected": self.asked.expected, "status": self.status,
                "got": {k: self.got.get(k) for k in ("picks", "escape", "value", "unit", "currency", "confidence",
                                                     "runnerUp", "agree", "unclear", "reason")},
                "verdict": self.verdict}


@dataclass
class Report:
    outcomes: list[Outcome] = field(default_factory=list)
    skipped: list[NotAsked] = field(default_factory=list)

    def count(self, which: str) -> int:
        return sum(o.verdict == which for o in self.outcomes)

    @property
    def wrong(self) -> list[Outcome]:
        return [o for o in self.outcomes if o.verdict == "wrong"]

    @property
    def refused(self) -> list[Outcome]:
        return [o for o in self.outcomes if o.status != 200]

    @property
    def corrections(self) -> dict[str, str]:
        return {o.asked.case.said: o.verdict for o in self.outcomes if o.asked.case.said in CORRECTIONS}

    @property
    def answered_by_fake(self) -> bool:
        """Every answer's reason is one the fake writes (see `FAKE_REASONS`)."""
        return bool(self.outcomes) and all(fake_reason(o.got.get("reason")) for o in self.outcomes)

    @property
    def model_never_answered(self) -> bool:
        return bool(self.outcomes) and all((o.got.get("reason") or "") in FAILED_REASONS for o in self.outcomes)

    def groups(self) -> dict[str, dict]:
        """Per case group (`readaloud`, `pick2`, ..., `confirm`): asked, right, safe, wrong, not asked."""
        out: dict[str, dict] = {}
        for o in self.outcomes:
            g = out.setdefault(o.asked.case.group, {"asked": 0, "right": 0, "safe": 0, "wrong": 0, "not asked": 0})
            g["asked"] += 1
            if o.verdict in ("right", "safe", "wrong"):
                g[o.verdict] += 1
        for s in self.skipped:
            out.setdefault(s.case.group, {"asked": 0, "right": 0, "safe": 0, "wrong": 0, "not asked": 0})["not asked"] += 1
        return out

    def summary(self) -> dict:
        return {"cases": len(self.outcomes) + len(self.skipped), "asked": len(self.outcomes),
                "right": self.count("right"), "safe": self.count("safe"), "wrong": len(self.wrong),
                "refused": len(self.refused), "corrections": self.corrections,
                "not asked": len(self.skipped), "groups": self.groups(),
                "wrong cases": [o.row() for o in self.wrong], "refused cases": [o.row() for o in self.refused]}

    def to_json(self) -> dict:
        return {**self.summary(), "outcomes": [o.row() for o in self.outcomes],
                "skipped": [{"case": s.case.name, "reason": s.reason} for s in self.skipped]}


def body(asked: Asked, language: str = "en-GB") -> dict:
    """The `ClassifyRequest` the page would send for this case (contract 18; `ask` amended at implementation)."""
    out: dict[str, Any] = {"itemId": asked.served.item_id, "heard": asked.said, "language": language}
    if asked.previous:
        out["previous"] = asked.previous
    if asked.served.ask:
        out["ask"] = asked.served.ask
    return out


def run(post: Callable[[dict], tuple[int, dict]], served: Iterable[Served], *,
        chosen: Iterable[Case] | None = None, language: str = "en-GB", limit: int | None = None) -> Report:
    """Every case that can be carried onto `served`, sent through `post` (one `ClassifyRequest` -> status, body)."""
    asked, skipped = plan(served, chosen)
    if limit is not None and len(asked) > limit:
        raise ValueError(f"{len(asked)} calls planned, over the {limit} allowed")
    report = Report(skipped=skipped)
    for a in asked:
        status, got = post(body(a, language))
        got = got if isinstance(got, dict) else {}
        report.outcomes.append(Outcome(a, status, got, verdict(a, got) if status == 200 else "refused"))
    return report
