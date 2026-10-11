"""The `BRIEF` subject: does keel-cloud's own `brief.md`, sent to a real model with a real
project's counted facts, come back as the checked reading a founder sees on the brief page?

**Since keel-cloud 079 (contract 9, MARKS_VERSION 14)** the result is no longer one paragraph
(`whatThisSays`, retired with its four marks) but a structured reading: `{headline, tiles, problem:
{conclusion, infer}, solution: {conclusion}, commercial: {conclusion}, sharpest?, next: {sentence,
tests[]}, quotes[]}`, every sentence `{text <= 400, cites[] <= 13}`. The facts are keel-cloud's
(counted by code); the model only infers over them, and keel-cloud's `BriefReading.check`
(refusal `B7`) holds every inferred line to the facts it was written over.

**The checks are mirrored here, not invented.** `reading_problems` restates `BriefReading.check`
clause for clause -- the same messages, in the same order -- so a result can be marked offline and by
`rescore.py`; `tests/test_instruction_brief_reading.py` runs the real `screenContracts validate`
over the golden shape and its mutations and asserts both sides refuse the same ones. The aggregate's
own verdict stays the `rule_refusal_rate` mark (`validate.py`); these five marks say *which* kind
of fault a reading had. Participant names are checked here (the validator is handed none).

1. `shape` -- every sentence is `{text, cites}`, `text` 1..400, `cites` <= 13, `tests` <= 3,
   `quotes` <= 2 at <= 160, and a `sharpest` only where the facts carry a split.
2. `cites` -- every cite is a key in `facts.keys`, scoped per section (a tile cites its own vector;
   the headline and `next.sentence` any), every sentence cites one, `problem.infer` two distinct,
   each test's key is one of `facts.targets`, and `sharpest` cites its split, outcome or a problem.
3. `numbers` -- every digit run in a sentence is a number in the facts' JSON; only the market's
   currency symbol; a test carries no digit or number word.
4. `quotes` -- each quote is a verbatim piece of the named person's story.
5. `bans` -- no `will pay`/`will buy`, `proves`/`proven`/`validated`/`will save`/`it works`, web
   address, or participant's name.

Every mark is recorded per case with the evidence that decided it, and the reading is rendered whole
on `register.html` beside the facts it was written over (judgement call 10's rule).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

# `ScreenResponseContracts` -- BRIEF_*: the contract's own limits, mirrored and nothing else.
SENTENCE_MAX = 400
CITES_MAX = 13
TESTS_MAX = 3
QUOTES_MAX = 2
QUOTE_MAX = 160

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
_NUMBER_WORD = re.compile(r"(?i)\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                          r"twenty|thirty|forty|fifty|hundred|thousand|million|half|percent|"
                          r"per cent)\b")
_CURRENCY = re.compile(r"[£$€¥₹]")
_WEB = re.compile(r"(?i)(https?://|www\.|\b[a-z0-9-]+\.(com|io|co|net|org|app|ai|uk)\b)")
_PURCHASE = re.compile(r"(?i)\bwill\s+(pay|buy)\b")
_IDEA = re.compile(r"(?i)\b(proves|proven|validated|will save|it works)\b")

#: `BriefReading.SENTENCES`: where a sentence sits, and the dimension prefix it may cite (`None`: any).
SENTENCES = (("headline", None, None), ("tiles", "problem", "problem."),
             ("tiles", "solution", "solution."), ("tiles", "commercial", "commercial."),
             ("problem", "conclusion", "problem."), ("problem", "infer", "problem."),
             ("solution", "conclusion", "solution."), ("commercial", "conclusion", "commercial."),
             ("next", "sentence", None))

MARK_NAMES = ("shape", "cites", "numbers", "quotes", "bans")


def _section(value, key) -> dict:
    inner = value.get(key) if isinstance(value, dict) else None
    return inner if isinstance(inner, dict) else {}


def _cites(sentence) -> list:
    cites = sentence.get("cites") if isinstance(sentence, dict) else None
    return [str(c) for c in cites] if isinstance(cites, list) else []


def _normal(number: str) -> str:
    plain = number.replace(",", "").rstrip(".")
    try:
        return format(Decimal(plain).normalize(), "f")
    except InvalidOperation:
        return plain


def numbers_in(text: str) -> set:
    return {_normal(m.group()) for m in _NUMBER.finditer(text)}


def reading_problems(result, facts, stories, names=()) -> list:
    """`BriefReading.check`, restated: every `(mark, message)` a result has against the facts it
    was written over, the stories by invitation id and the names never to say. Messages are
    keel-cloud's own words. `facts` `None` checks only what needs none."""
    problems = []
    if not isinstance(result, dict):
        return [("shape", "result: missing")]
    keys = None if facts is None else {str(k) for k in facts.get("keys") or []}
    numbers = None if facts is None else numbers_in(json.dumps(facts, ensure_ascii=False))
    symbol = (facts or {}).get("money", {}).get("currencySymbol") if facts else None
    split = (facts or {}).get("sharpest") if facts else None

    def add(mark, message):
        problems.append((mark, message))

    def bans(path, text):
        if (m := _PURCHASE.search(text)):
            add("bans", f"{path}: '{m.group()}' claims a purchase; a stated price is what it "
                          "was said to be worth")
        if (m := _IDEA.search(text)):
            add("bans", f"{path}: '{m.group()}' claims the idea works; nobody has used it")
        if _WEB.search(text):
            add("bans", f"{path}: no web address")
        lower = text.lower()
        for name in names:
            if re.search(rf"\b{re.escape(name.lower())}\b", lower):
                add("bans", f"{path}: names a person ('{name}')")

    def money(path, text):
        for m in _CURRENCY.finditer(text):
            if symbol is None or m.group() not in symbol:
                add("numbers", f"{path}: the currency {m.group()} is not the market's")

    def sentence(path, value, vector):
        text = value.get("text") if isinstance(value, dict) else None
        if not isinstance(text, str) or not text.strip():
            add("shape", f"{path}: a sentence {{text, cites}} is missing")
            return
        if len(text) > SENTENCE_MAX:
            add("shape", f"{path}.text: {len(text)} characters, over {SENTENCE_MAX}")
        cites = _cites(value)
        if len(cites) > CITES_MAX:
            add("shape", f"{path}.cites: more than {CITES_MAX}")
        if not cites:
            add("cites", f"{path}.cites: cites at least one dimension")
        for cite in cites:
            if keys is not None and cite not in keys:
                add("cites", f"{path}.cites: '{cite}' is not a dimension on this project")
            elif vector is not None and not cite.startswith(vector):
                add("cites", f"{path}.cites: '{cite}' is not a {vector[:-1]} dimension")
        if numbers is not None:
            for m in _NUMBER.finditer(text):
                if _normal(m.group()) not in numbers:
                    add("numbers", f"{path}.text: the number {m.group()} is not in the facts")
        money(f"{path}.text", text)
        bans(f"{path}.text", text)

    for outer, inner, vector in SENTENCES:
        value = result.get(outer) if inner is None else _section(result, outer).get(inner)
        sentence(outer if inner is None else f"{outer}.{inner}", value, vector)
    infer = _cites(_section(result, "problem").get("infer"))
    if len(set(infer)) < 2:
        add("cites", f"problem.infer: cites at least two problem dimensions (cited {infer})")
    sharpest = result.get("sharpest")
    if sharpest is not None:
        if facts is not None and not split:
            add("shape", "sharpest: the facts carry no split, so there is no sharpest sentence")
        else:
            sentence("sharpest", sharpest, None)
            for cite in _cites(sharpest) if facts is not None else []:
                if not cite.startswith("problem.") and cite not in (split.get("split"),
                                                                    split.get("outcome")):
                    add("cites", f"sharpest: cites '{cite}', which is neither the split, the "
                                 "outcome nor a problem dimension")
    tests = _section(result, "next").get("tests")
    targets = None if facts is None else {str(t.get("key")) for t in facts.get("targets") or []
                                          if isinstance(t, dict)}
    if not isinstance(tests, list):
        add("shape", "next.tests: missing")
    else:
        if len(tests) > TESTS_MAX:
            add("shape", f"next.tests: at most {TESTS_MAX} tests")
        for i, test in enumerate(tests):
            test = test if isinstance(test, dict) else {}
            text = test.get("text") if isinstance(test.get("text"), str) else ""
            path = f"next.tests[{i}]"
            if not text.strip():
                add("shape", f"{path}.text: blank")
            if targets is not None and str(test.get("key")) not in targets:
                add("cites", f"{path}.key: '{test.get('key')}' is not a next-test target "
                             f"{sorted(targets)}")
            if _NUMBER.search(text) or _NUMBER_WORD.search(text):
                add("numbers", f"{path}.text: a test carries no number")
            money(f"{path}.text", text)
            bans(f"{path}.text", text)
    quotes = result.get("quotes")
    if not isinstance(quotes, list):
        add("shape", "quotes: missing")
    else:
        if len(quotes) > QUOTES_MAX:
            add("shape", f"quotes: at most {QUOTES_MAX}")
        for i, quote in enumerate(quotes):
            quote = quote if isinstance(quote, dict) else {}
            text = quote.get("text") if isinstance(quote.get("text"), str) else ""
            story = (stories or {}).get(str(quote.get("invitationId")))
            path = f"quotes[{i}]"
            if not text.strip() or len(text) > QUOTE_MAX:
                add("shape", f"{path}.text: 1 to {QUOTE_MAX} characters")
            if story is None:
                add("quotes", f"{path}.invitationId: '{quote.get('invitationId')}' has no story")
            elif text.strip() and text not in story:
                add("quotes", f"{path}.text: not a verbatim piece of that person's story")
    return problems


@dataclass
class BriefScore:
    case_id: str
    entry_id: str
    run_index: int
    reading: dict = field(default_factory=dict)
    failed: str | None = None
    needs_input: bool = False
    needs_input_questions: list = field(default_factory=list)
    marks: dict = field(default_factory=dict)        # name -> True | False | None (n/a)
    findings: dict = field(default_factory=dict)     # name -> the evidence that decided it
    length: int = 0                                  # characters across every sentence
    subject: str = "BRIEF"

    @property
    def paragraph(self) -> str:
        """The register's text: every sentence of the reading, in the order a founder reads it."""
        return reading_text(self.reading)

    @property
    def met(self) -> bool:
        """All five, and an unmeasured mark is not a met mark (marks.py judgement call 13)."""
        return all(self.marks.get(name) is True for name in MARK_NAMES)


def reading_text(reading) -> str:
    if not isinstance(reading, dict):
        return ""
    parts = []
    for outer, inner, _vector in SENTENCES:
        value = reading.get(outer) if inner is None else _section(reading, outer).get(inner)
        if isinstance(value, dict) and isinstance(value.get("text"), str):
            parts.append(f"{outer if inner is None else outer + '.' + inner}: {value['text']}")
    if isinstance(reading.get("sharpest"), dict):
        parts.append(f"sharpest: {reading['sharpest'].get('text')}")
    for test in _section(reading, "next").get("tests") or []:
        if isinstance(test, dict):
            parts.append(f"test [{test.get('key')}]: {test.get('text')}")
    for quote in reading.get("quotes") or []:
        if isinstance(quote, dict):
            parts.append(f"quote: {quote.get('text')}")
    return "\n".join(parts)


def _stories(context: dict) -> dict:
    return {str(s.get("invitation_id")): s.get("story") for s in context.get("stories") or []
            if isinstance(s, dict)}


def score_brief(case, entry, result, *, outcome: str | None = None, failed: str | None = None,
                needs_input_questions=None, registry=None) -> BriefScore:
    """One BRIEF case, marked five ways against the facts it was actually sent."""
    score = BriefScore(case_id=case.case_id, entry_id=entry.id, run_index=case.run_index,
                       failed=failed)
    del registry      # kept in the signature for the callers; the marks read no registry
    if needs_input_questions is not None:
        score.needs_input = True
        score.needs_input_questions = needs_input_questions
        score.marks = {name: False for name in MARK_NAMES}
        score.findings = {"shape": "NEEDS_INPUT on a screen brief.md says has nobody to ask; "
                                   "brief.md: 'You always return COMPLETED.'"}
        return score
    if failed or not isinstance(result, dict):
        score.marks = {name: False for name in MARK_NAMES}
        score.findings = {"shape": failed or "the result was no object"}
        return score
    context = case.payload.get("context") or {}
    names = [p.person for p in entry.people() if p.person]
    names += [n.split()[0] for n in names if len(n.split()[0]) >= 2]
    found = reading_problems(result, context.get("facts"), _stories(context), names)
    score.reading = result
    score.length = len(score.paragraph)
    for name in MARK_NAMES:
        mine = [message for mark, message in found if mark == name]
        score.marks[name] = not mine
        score.findings[name] = "; ".join(mine) if mine else {
            "shape": "every sentence {text, cites}, within its limits",
            "cites": "every cite a dimension of its section; two for problem.infer",
            "numbers": "every number the facts' own, the market's currency only",
            "quotes": "every quote verbatim from that person's story",
            "bans": "no purchase claim, no 'it works', no web address, no name"}[name]
    return score


# ----------------------------------------------------------------------------------- the totals

def totals(scores: list) -> dict:
    """The run's own BRIEF numbers. `None` -- never `0` -- when nothing was measured."""
    if not scores:
        return {"brief_cases": 0, "brief_paragraphs": None, "brief_by_mark": {},
                "brief_needs_input": 0, "brief_measured": False}
    by_mark = {}
    for name in MARK_NAMES:
        met = sum(1 for s in scores if s.marks.get(name) is True)
        by_mark[name] = {"met": met, "of": len(scores)}
    return {
        "brief_cases": len(scores),
        "brief_paragraphs": sum(1 for s in scores if s.met) / len(scores),
        "brief_by_mark": by_mark,
        "brief_needs_input": sum(1 for s in scores if s.needs_input),
        "brief_measured": True,
    }
