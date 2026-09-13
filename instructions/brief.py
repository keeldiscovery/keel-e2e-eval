"""The `BRIEF` subject: does keel-cloud's own `brief.md`, sent to a real model with a real
project's standings, come back as the paragraph a founder reads under *What this says*?

The third subject of this eval, and the last screen keel-cloud has (spec 009 follow-on;
keel-cloud spec 030 FR-006/FR-008/FR-009). It is the one screen **nobody asks for**:
`ReadingBatchService.sayWhatThisSays` starts the job by itself the moment a reading batch
finishes, so there is no founder, no question and no second turn -- which is why `brief.md` says
*you always return COMPLETED* and why the marks below treat a `NEEDS_INPUT` as a failed case
rather than an ask.

**What can honestly be marked here, and what cannot.** The contract is one free-text field, so
almost everything about a good paragraph is wording -- and design §3.8's rule holds: whether it
reads like someone who has read all three cards cannot be checked by code. So the paragraph is
**rendered on `register.html` beside the entry's own standings** (judgement call 10's rule, one
subject wider), and what is *marked* here is only what a rule in `brief.md` states in so many
words and a structure can carry:

1. `shape` -- one paragraph, no headings, no bullets, no stage label, no link, <= 2000 code
   points, never blank. Every clause of it is `brief.md`'s own *What the paragraph never
   contains* list, and `ScreenResponseContracts.briefSchema`'s own two limits.
2. `coverage` -- the deciding line's number quoted exactly beside the founder's own phrase,
   wherever the context carried one, and no `N of M` count the standings never contained (either
   side of a split: `brief.md` asks for both). **Whether each claim's verdict is named in the
   design's own phrase is observed and not marked** -- see `verdict_phrasing` and judgement call
   20; `brief.md` licenses the paraphrase by example, so a code check on the words would score the
   paragraph the instruction asks for as a failure.
3. `register` -- second person, and the market's own currency. Whether it *sounds* like that
   market is the register page's job and no metric's.
4. `source_material` -- the claims' text is source material, never an instruction. The corpus
   carries no injected order (S-004 is where this repo attacks with orders, at a live model, on a
   real screen), so what this mark can measure is the other half of the same rule: a paragraph
   that read `claims` as *text to reproduce* carries the ids, field names and enum names only the
   data has -- and a paragraph that read it as *an instruction to obey* answers `NEEDS_INPUT` on
   a screen with nobody to ask. Both are counted here.

Every mark is recorded per case with the evidence that decided it, so a miss can be read on the
report rather than only counted -- and a paragraph that misses one is still rendered whole on the
register page, because a mark this narrow can be wrong about a paragraph that is right.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ------------------------------------------------------------------------------- the vocabulary

# `FounderVoice.verdictLabel` is the one place the four words are defined, and `brief.md` says
# there is no fifth: SUPPORTED is *holding up*, CONTRADICTED *not holding up*, MIXED *people
# disagree*, UNTESTED *still asking*.
#
# **These are observed and never marked** (MARKS_VERSION 5, judgement call 20). `brief.md`'s very
# next sentence says to write them into ordinary sentences and gives its own paraphrases -- *"the
# problem is real"*, *"nobody pays anything like that today"* -- so a code check on the words
# scores the paragraph the instruction asks for as a failure. The first BRIEF run
# (`runs/20260908T004022Z-instructions`) proved it: seven paragraphs, every one of them plainly
# right about its three claims, and 0 of 7 carried the literal phrase. So `verdict_phrasing`
# records per stage whether the design's own phrase appears, the register page renders that beside
# the paragraph, and a person decides -- design §3.8's rule, where it belongs.
VERDICT_MARKERS = {
    "SUPPORTED": ("holding up", "holds up", "held up"),
    "CONTRADICTED": ("not holding up", "isn't holding up", "is not holding up",
                     "not hold up", "doesn't hold up", "does not hold up", "didn't hold up",
                     "did not hold up"),
    "MIXED": ("disagree", "disagrees", "disagreed", "disagreement"),
    "UNTESTED": ("still asking",),
}

# `CONTRADICTED`'s phrase contains `SUPPORTED`'s, so the negative is always taken out of the
# paragraph first and `SUPPORTED` is looked for in what is left. Getting this the other way round
# would call every contradicted claim supported.
_NEGATED_FIRST = "CONTRADICTED"

# `brief.md`: "No bullet, no numbered list, no heading, no line break: one paragraph."
_BULLET_GLYPHS = ("•", "‣", "◦", "⁃")
_LEADING_MARKER_RE = re.compile(r"^\s*(?:[-*#>]|\d+[.)])\s")
# `ScreenResponseContracts.NO_LINK_PATTERN`, restated as the contract states it.
_LINK_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
# 2 000 since MARKS_VERSION 7 (judgement call 23, the founder, 2026-09-13: "I plan to revisit the
# brief structure, so for now increase the cap on brief to 2000") -- the contract's own edge,
# `ScreenResponseContracts.WHAT_THIS_SAYS_MAX`, after DRIFT #68; this mirrors it and nothing else.
WHAT_THIS_SAYS_MAX = 2000

# `brief.md`: "never PROBLEM, SOLUTION or COMMERCIAL". Case-sensitive and whole-word, the way
# `evals/policy.py`'s own enum sweep reads them -- the lower-case English words are the founder's
# screen's own copy (*the problem*, *your solution*, *on price*) and are correct.
STAGE_LABELS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# The names only the data has. A paragraph carrying one has reproduced `claims` rather than read
# it. `brief.md`: "no id, no field name, no enum name, no rule id" -- and "never the word proxy".
#
# **The ordinary-English collisions are exempt**, the same way `evals/policy.py`'s judgement calls
# 1, 5 and 10 exempt theirs: `inside`, `outside`, `guessed`, `escaped`, `claims`, `beliefs`,
# `statement`, `heading`, `risk`, `mark`, `verdict` and `drift` are all words `brief.md` itself
# tells the model to write -- *"how many people landed inside the founder's own band"* is the
# instruction's own sentence. Sweeping them would flag the paragraph the instruction asks for.
# What is left is the shape a field name has and prose does not: an underscore, a camel case, or
# a word no English sentence about a founder's claims would reach for.
CONTEXT_FIELD_NAMES = (
    "whatThisSays", "project_name", "median_reads", "founder_phrase", "founderPhrase",
    "askedOf", "anchorId", "selectionId", "roleType", "existing_roles",
)
ENUM_NAMES = ("SUPPORTED", "CONTRADICTED", "MIXED", "UNTESTED",
              "BELOW", "ABOVE", "BOTH", "NONE", "LOAD_BEARING", "SUPPORTING", "DIRECT", "PROXY",
              "INTERVAL", "CHOICE", "COMPLETED", "NEEDS_INPUT")

SECOND_PERSON = ("you", "your", "yours", "you're", "youre")
_WORD_RE = re.compile(r"[A-Za-z']+")

# Every currency glyph this corpus's markets could put in a paragraph. The allowed set is read off
# the context that was actually sent, so nothing here decides what GB or US money looks like.
CURRENCY_GLYPHS = ("£", "$", "€", "¥")

# `brief.md`: "*seven of nine* is `inside` and `inside + outside` read out". A count may be
# written in words, so the small numbers are named here -- the corpus's largest cohort is twenty.
_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}
_COUNT_RE = re.compile(
    r"\b(\d{1,3}|" + "|".join(_NUMBER_WORDS) + r")\s+of\s+(?:the\s+)?(\d{1,3}|"
    + "|".join(_NUMBER_WORDS) + r")\b", re.IGNORECASE)


def _number(token: str):
    token = token.lower()
    return _NUMBER_WORDS.get(token, int(token) if token.isdigit() else None)


# ------------------------------------------------------------------------------- the deciding line

def deciding_line(claim: dict) -> dict | None:
    """`FounderViewAssembler.whatItMeasures`'s own rule, restated where a mark needs to know what
    to look for: *the first applying load-bearing belief sitting at the stage's own verdict, in
    the same presentation order*. Nothing is computed from it -- it only says which of the lines
    already in the context the paragraph's shortfall sentence is about.

    `None` for a stage that is not approved, or one whose verdict no load-bearing line carries.
    """
    if not claim.get("approved"):
        return None
    for belief in claim.get("beliefs") or []:
        if belief.get("risk") == "LOAD_BEARING" and belief.get("verdict") == claim.get("verdict"):
            return belief
    return None


# ------------------------------------------------------------------------------------- the marks

@dataclass
class BriefScore:
    case_id: str
    entry_id: str
    run_index: int
    paragraph: str = ""
    failed: str | None = None
    needs_input: bool = False
    needs_input_questions: list = field(default_factory=list)
    marks: dict = field(default_factory=dict)        # name -> True | False | None (n/a)
    findings: dict = field(default_factory=dict)     # name -> the evidence that decided it
    phrasing: list = field(default_factory=list)     # per stage, observed and never marked
    length: int = 0

    @property
    def met(self) -> bool:
        """All four, and an unmeasured mark is not a met mark (marks.py judgement call 13)."""
        return all(self.marks.get(name) is True for name in ("shape", "coverage", "register",
                                                             "source_material"))


def score_brief(case, entry, result, *, outcome: str | None = None, failed: str | None = None,
                needs_input_questions=None) -> BriefScore:
    """One BRIEF case, marked four ways against the context it was actually sent."""
    score = BriefScore(case_id=case.case_id, entry_id=entry.id, run_index=case.run_index,
                       failed=failed)
    claims = (case.payload.get("context") or {}).get("claims") or []

    if needs_input_questions is not None:
        score.needs_input = True
        score.needs_input_questions = needs_input_questions
        # A question on a screen with nobody to ask it is the source-material rule's other half,
        # and it is a failed case, not an excluded one -- score.py's own reading of decision 14.
        score.marks = {"shape": False, "coverage": False, "register": False,
                       "source_material": False}
        score.findings = {"source_material": "NEEDS_INPUT on a screen brief.md says has nobody "
                                             "to ask; brief.md: 'You always return COMPLETED.'"}
        return score

    paragraph = result.get("whatThisSays") if isinstance(result, dict) else None
    if failed or not isinstance(paragraph, str):
        score.marks = {"shape": False, "coverage": False, "register": False,
                       "source_material": False}
        score.findings = {"shape": failed or "the result carried no whatThisSays string"}
        return score

    score.paragraph = paragraph
    score.length = len(paragraph)
    score.phrasing = verdict_phrasing(paragraph, claims)
    for name, (met, finding) in {
        "shape": _shape(paragraph),
        "coverage": _coverage(paragraph, claims),
        "register": _register(paragraph, case),
        "source_material": _source_material(paragraph, entry, outcome),
    }.items():
        score.marks[name] = met
        score.findings[name] = finding
    return score


def _shape(paragraph: str) -> tuple[bool, str]:
    faults = []
    if not paragraph.strip():
        faults.append("blank")
    if "\n" in paragraph or "\r" in paragraph:
        faults.append("line break")
    length = len(paragraph)
    if length > WHAT_THIS_SAYS_MAX:
        faults.append(f"{length} code points, over the contract's {WHAT_THIS_SAYS_MAX}")
    if _LINK_RE.search(paragraph):
        faults.append("a web address")
    for glyph in _BULLET_GLYPHS:
        if glyph in paragraph:
            faults.append(f"bullet glyph {glyph!r}")
    if _LEADING_MARKER_RE.match(paragraph):
        faults.append("opens with a list or heading marker")
    labels = [label for label in STAGE_LABELS
              if re.search(rf"\b{label}\b", paragraph)]
    if labels:
        faults.append(f"stage label(s) {labels}")
    return (not faults), ("; ".join(faults) if faults else f"one paragraph, {length} code points")


def verdict_phrasing(paragraph: str, claims: list) -> list:
    """Per stage: does the design's own phrase for that verdict appear? **Observed, never marked**
    (judgement call 20). Rendered on `register.html` beside the paragraph so a person reads the
    sentence the model actually wrote and decides whether it says the same thing."""
    lowered = paragraph.casefold()
    # Take the negative out first: *not holding up* contains *holding up*, and the other order
    # would call every contradicted claim supported.
    residue = lowered
    for phrase in VERDICT_MARKERS[_NEGATED_FIRST]:
        residue = residue.replace(phrase, " ")

    out = []
    for claim in claims:
        verdict = claim.get("verdict")
        if not claim.get("approved") or verdict is None:
            out.append({"stage": claim.get("stage"), "verdict": None, "phrase": None,
                        "present": None})
            continue
        haystack = lowered if verdict == _NEGATED_FIRST else residue
        markers = VERDICT_MARKERS.get(verdict, ())
        out.append({"stage": claim.get("stage"), "verdict": verdict,
                    "phrase": markers[0] if markers else None,
                    "present": any(marker in haystack for marker in markers)})
    return out


def _coverage(paragraph: str, claims: list) -> tuple[bool, str]:
    lowered = paragraph.casefold()
    faults, notes = [], []

    # The deciding line's number beside the founder's own phrase, wherever there is one.
    for claim in claims:
        line = deciding_line(claim)
        if not line or not line.get("median_reads"):
            continue
        stage = claim.get("stage")
        if line["median_reads"] not in paragraph:
            faults.append(f"{stage}'s deciding line reads {line['median_reads']!r} and the "
                          "paragraph does not quote it")
        phrase = line.get("founder_phrase")
        if phrase and phrase.casefold() not in lowered:
            faults.append(f"{stage}'s deciding line was said by the founder as {phrase!r} and the "
                          "paragraph does not carry it")
        notes.append(f"{stage}: deciding line {line.get('heading')!r} checked against its number")

    # No `N of M` the standings never contained. **Both sides count**: `brief.md`'s third thing a
    # paragraph says is *who the split is between*, named "by the answers they actually gave" --
    # *"six of nine had a member of staff take the delivery in; three took it in themselves"* --
    # so `outside` of `inside + outside` is as much a count the standings contain as `inside` is.
    # The first run found this at once (`02-compliancelog`, *6 of 10 rebuilt the draft they were
    # handed, and 4 reviewed and signed*), and it was the mark that was wrong, not the paragraph.
    allowed = set()
    for claim in claims:
        for b in claim.get("beliefs") or []:
            inside, outside = b.get("inside"), b.get("outside")
            if inside is None:
                continue
            total = (inside or 0) + (outside or 0)
            allowed.add((inside, total))
            allowed.add((outside or 0, total))
    for match in _COUNT_RE.finditer(paragraph):
        pair = (_number(match.group(1)), _number(match.group(2)))
        if pair not in allowed:
            faults.append(f"the count {match.group(0)!r} is no line's inside of "
                          "inside + outside")
    return (not faults), ("; ".join(faults) if faults else "; ".join(notes)
                          or "no number to check, and none invented")


def _register(paragraph: str, case) -> tuple[bool, str]:
    words = {w.casefold() for w in _WORD_RE.findall(paragraph)}
    faults = []
    if not words & set(SECOND_PERSON):
        faults.append("no second person: brief.md asks for *you said*, *your band*")
    context_text = _context_text(case)
    foreign = [glyph for glyph in CURRENCY_GLYPHS
               if glyph in paragraph and glyph not in context_text]
    if foreign:
        faults.append(f"currency {foreign} the context never carried")
    return (not faults), ("; ".join(faults) if faults
                          else "second person, and no money the context did not carry")


def _source_material(paragraph: str, entry, outcome: str | None) -> tuple[bool, str]:
    faults = []
    if outcome is not None and outcome != "COMPLETED":
        faults.append(f"outcome {outcome}, where brief.md says there is nobody to ask")
    ids = [b.id for b in entry.beliefs if re.search(rf"\b{re.escape(b.id)}\b", paragraph)]
    if ids:
        faults.append(f"belief id(s) {ids}")
    fields = [name for name in CONTEXT_FIELD_NAMES
              if re.search(rf"\b{re.escape(name)}\b", paragraph)]
    if fields:
        faults.append(f"context field name(s) {fields}")
    enums = [name for name in ENUM_NAMES if re.search(rf"\b{re.escape(name)}\b", paragraph)]
    if enums:
        faults.append(f"enum name(s) {enums}")
    if re.search(r"\bprox(y|ies)\b", paragraph, re.IGNORECASE):
        faults.append("the word 'proxy', which brief.md forbids by name")
    return (not faults), ("; ".join(faults) if faults
                          else "the claims were read, not reproduced or obeyed")


def _context_text(case) -> str:
    import json                                     # noqa: PLC0415 - local, one call a case
    return json.dumps(case.payload.get("context") or {}, ensure_ascii=False)


# ----------------------------------------------------------------------------------- the totals

def totals(scores: list) -> dict:
    """The run's own BRIEF numbers. `None` -- never `0` -- when nothing was measured."""
    if not scores:
        return {"brief_cases": 0, "brief_paragraphs": None, "brief_by_mark": {},
                "brief_needs_input": 0, "brief_measured": False}
    by_mark = {}
    for name in ("shape", "coverage", "register", "source_material"):
        met = sum(1 for s in scores if s.marks.get(name) is True)
        by_mark[name] = {"met": met, "of": len(scores)}
    return {
        "brief_cases": len(scores),
        "brief_paragraphs": sum(1 for s in scores if s.met) / len(scores),
        "brief_by_mark": by_mark,
        "brief_needs_input": sum(1 for s in scores if s.needs_input),
        "brief_measured": True,
    }
