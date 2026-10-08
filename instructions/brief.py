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

5. `no_claim_words` (`MARKS_VERSION` 9, judgement call 35) -- the sentence that names a threshold
   dimension (status vocabulary reaches `BAR_SET`) or the Price row (`NOT_TESTED_BY_DESIGN`)
   carries no claim word: *works*, *effective*, *proves*, *will save*, *confirmed*... A bar is set,
   never cleared, and a hypothesis is not tested, so a sentence that says otherwise about either is
   the one claim the interviews cannot support.

**At v9 the context is the vectors** (spec 029 FR-019): three vectors, each with its verdict, its
deciding deal-breaker (`expected.vector_verdicts[v].deciding`, the worst one) and every
dimension's standing under it -- one paragraph a project at the 2 000 edge, one case an entry.

Every mark is recorded per case with the evidence that decided it, so a miss can be read on the
report rather than only counted -- and a paragraph that misses one is still rendered whole on the
register page, because a mark this narrow can be wrong about a paragraph that is right.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ------------------------------------------------------------------------------- the vocabulary

# The verdict words, keyed by the `Status` the context carries (MARKS_VERSION 9). **Observed and
# never marked** (judgement call 20): `brief.md` licenses the paraphrase by example, so a code check
# on the words would score the paragraph the instruction asks for as a failure. `verdict_phrasing`
# records per vector whether the design's own phrase appears, the register renders it, a person
# decides.
VERDICT_MARKERS = {
    "HOLDING_UP": ("holding up", "holds up", "held up"),
    "NOT_HOLDING_UP": ("not holding up", "isn't holding up", "is not holding up",
                       "not hold up", "doesn't hold up", "does not hold up", "didn't hold up",
                       "did not hold up"),
    "PEOPLE_DISAGREE": ("disagree", "disagrees", "disagreed", "disagreement"),
    "TOO_FEW_TO_CALL": ("too few",),
    "BAR_SET": ("bar is set", "bar set", "sets the bar", "set the bar"),
    "NOT_TESTED_BY_DESIGN": ("not tested", "untested"),
    "NOT_ASKED_YET": ("not asked",),
    "LEFT_OUT": ("left out",),
}

# `NOT_HOLDING_UP`'s phrase contains `HOLDING_UP`'s, so the negative is always taken out of the
# paragraph first and `HOLDING_UP` is looked for in what is left. Getting this the other way round
# would call every vector that is not holding up one that is.
_NEGATED_FIRST = "NOT_HOLDING_UP"

#: The statuses whose sentences may carry no claim word (call 35): a bar is set, never met; a
#: price is a hypothesis, never tested.
CLAIM_SCOPED_STATUSES = ("BAR_SET", "NOT_TESTED_BY_DESIGN")
CLAIM_WORDS = ("works", "worked", "effective", "proves", "proven", "confirmed", "will save",
               "saves", "validated", "delivers")
_CLAIM_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in CLAIM_WORDS) + r")\b",
                       re.IGNORECASE)
_SENTENCE_RE = re.compile(r"(?<=[.!?;])\s+")

# `brief.md`: "No bullet, no numbered list, no heading, no line break: one paragraph."
_BULLET_GLYPHS = ("•", "‣", "◦", "⁃")
_LEADING_MARKER_RE = re.compile(r"^\s*(?:[-*#>]|\d+[.)])\s")
# `ScreenResponseContracts.NO_LINK_PATTERN`, restated as the contract states it.
_LINK_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
# 2 000 since MARKS_VERSION 7 (judgement call 23, the founder, 2026-09-13: "I plan to revisit the
# brief structure, so for now increase the cap on brief to 2000") -- the contract's own edge,
# `ScreenResponseContracts.WHAT_THIS_SAYS_MAX`, after DRIFT #68; this mirrors it and nothing else.
WHAT_THIS_SAYS_MAX = 2000

# `brief.md`: "never PROBLEM, SOLUTION or COMMERCIAL" -- the three vector names. Case-sensitive and
# whole-word, the way `evals/policy.py`'s own enum sweep reads them -- the lower-case English words
# are the founder's screen's own copy (*the problem*, *your solution*, *on price*) and are correct.
VECTOR_LABELS = ("PROBLEM", "SOLUTION", "COMMERCIAL")
STAGE_LABELS = VECTOR_LABELS

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
    # MARKS_VERSION 9: the vector context's own field names.
    "belief_sentence", "belief_phrase", "n_anchored", "n_guessed", "vector_verdicts",
    "optionCounts", "founder_calibration", "status_vocabulary", "actor_plural",
)
#: The eight `Status` words, the two weights, the drift words and the outcomes (marks §2.6). The
#: vector names are swept by `shape` as labels and here as names, both whole-word upper-case.
ENUM_NAMES = ("HOLDING_UP", "NOT_HOLDING_UP", "PEOPLE_DISAGREE", "TOO_FEW_TO_CALL", "BAR_SET",
              "NOT_TESTED_BY_DESIGN", "NOT_ASKED_YET", "LEFT_OUT", "DEAL_BREAKER", "SHAPES",
              "PROBLEM", "SOLUTION", "COMMERCIAL",
              "BELOW", "ABOVE", "BOTH", "NONE", "COMPLETED", "NEEDS_INPUT")
#: Every dotted dimension key -- `problem.duration` is the data's name, never a founder's word.
_DOTTED_KEY_RE = re.compile(r"\b(?:problem|solution|commercial)\.[a-z_]+\b")

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

def deciding_line(vector_standing: dict) -> dict | None:
    """The dimension a vector's verdict turns on: `expected.vector_verdicts[v].deciding`, the
    vector's worst deal-breaker (judgement call 35), looked up among the dimensions the context
    carried. Nothing is computed from it -- it only says which dimension the paragraph's sentence
    about that vector must be about. `None` when the vector names none or carries no such
    dimension."""
    deciding = (vector_standing or {}).get("deciding")
    if not deciding:
        return None
    for dimension in vector_standing.get("dimensions") or []:
        if dimension.get("key") == deciding:
            return dimension
    return None


# ------------------------------------------------------------------------------------- the marks

MARK_NAMES = ("shape", "coverage", "register", "source_material", "no_claim_words")


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
    phrasing: list = field(default_factory=list)     # per vector, observed and never marked
    length: int = 0
    subject: str = "BRIEF"

    @property
    def met(self) -> bool:
        """All five, and an unmeasured mark is not a met mark (marks.py judgement call 13)."""
        return all(self.marks.get(name) is True for name in MARK_NAMES)


def _vectors(case) -> list:
    return (case.payload.get("context") or {}).get("vectors") or []


def claim_scoped_names(vectors: list, registry=None) -> list:
    """The dimension names whose sentences carry no claim word: every dimension whose
    `answers.status_vocabulary` reaches `BAR_SET` or `NOT_TESTED_BY_DESIGN` (the registry), or --
    without one -- whose standing in the context is one of the two."""
    names = []
    for vector in vectors:
        for d in vector.get("dimensions") or []:
            scoped = d.get("status") in CLAIM_SCOPED_STATUSES
            if registry is not None and registry.has(d.get("key")):
                vocabulary = registry.by_key(d["key"]).status_vocabulary
                scoped = scoped or any(s in vocabulary for s in CLAIM_SCOPED_STATUSES)
            if scoped and d.get("name"):
                names.append(d["name"])
    return names


def score_brief(case, entry, result, *, outcome: str | None = None, failed: str | None = None,
                needs_input_questions=None, registry=None) -> BriefScore:
    """One BRIEF case, marked five ways against the context it was actually sent."""
    score = BriefScore(case_id=case.case_id, entry_id=entry.id, run_index=case.run_index,
                       failed=failed)
    vectors = _vectors(case)
    registry = registry if registry is not None else getattr(entry, "registry", None)

    if needs_input_questions is not None:
        score.needs_input = True
        score.needs_input_questions = needs_input_questions
        score.marks = {name: False for name in MARK_NAMES}
        score.findings = {"source_material": "NEEDS_INPUT on a screen brief.md says has nobody "
                                             "to ask; brief.md: 'You always return COMPLETED.'"}
        return score

    paragraph = result.get("whatThisSays") if isinstance(result, dict) else None
    if failed or not isinstance(paragraph, str):
        score.marks = {name: False for name in MARK_NAMES}
        score.findings = {"shape": failed or "the result carried no whatThisSays string"}
        return score

    score.paragraph = paragraph
    score.length = len(paragraph)
    score.phrasing = verdict_phrasing(paragraph, vectors)
    for name, (met, finding) in {
        "shape": _shape(paragraph),
        "coverage": _coverage(paragraph, vectors),
        "register": _register(paragraph, case),
        "source_material": _source_material(paragraph, entry, outcome),
        "no_claim_words": no_claim_words(paragraph, claim_scoped_names(vectors, registry)),
    }.items():
        score.marks[name] = met
        score.findings[name] = finding
    return score


def no_claim_words(paragraph: str, names: list) -> tuple[bool, str]:
    """Call 35: a sentence naming a `BAR_SET` or `NOT_TESTED_BY_DESIGN` dimension (by `name`,
    case-folded) carries none of `CLAIM_WORDS`. The same word in a sentence about another
    dimension is that sentence's business, not this mark's."""
    faults = []
    lowered_names = [n.casefold() for n in names]
    for sentence in _SENTENCE_RE.split(paragraph):
        folded = sentence.casefold()
        named = [n for n in lowered_names if n in folded]
        if not named:
            continue
        claims = sorted({m.group(1).lower() for m in _CLAIM_RE.finditer(sentence)})
        if claims:
            faults.append(f"the sentence naming {', '.join(named)} carries {', '.join(claims)}: "
                          f"{sentence.strip()!r}")
    return (not faults), ("; ".join(faults) if faults else
                          f"no claim word beside {', '.join(names) or 'no threshold dimension'}")


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
    labels = [label for label in VECTOR_LABELS
              if re.search(rf"\b{label}\b", paragraph)]
    if labels:
        faults.append(f"vector label(s) {labels}")
    return (not faults), ("; ".join(faults) if faults else f"one paragraph, {length} code points")


def verdict_phrasing(paragraph: str, vectors: list) -> list:
    """Per vector: does the design's own phrase for that verdict appear? **Observed, never marked**
    (judgement call 20). Rendered on `register.html` beside the paragraph."""
    lowered = paragraph.casefold()
    residue = lowered
    for phrase in VERDICT_MARKERS[_NEGATED_FIRST]:
        residue = residue.replace(phrase, " ")
    out = []
    for vector in vectors:
        verdict = vector.get("verdict")
        if verdict is None:
            out.append({"vector": vector.get("vector"), "verdict": None, "phrase": None,
                        "present": None})
            continue
        haystack = lowered if verdict == _NEGATED_FIRST else residue
        markers = VERDICT_MARKERS.get(verdict, ())
        out.append({"vector": vector.get("vector"), "verdict": verdict,
                    "phrase": markers[0] if markers else None,
                    "present": any(marker in haystack for marker in markers)})
    return out


def _allowed_counts(vectors: list) -> set:
    """Every `N of M` the context carried: `inside`/`outside` of `n`, and every `optionCounts`
    row of `n` (call 21's two sides, and the set dimensions' own counts at v9)."""
    allowed = set()
    for vector in vectors:
        for d in vector.get("dimensions") or []:
            n = d.get("n_anchored")
            inside, outside = d.get("inside"), d.get("outside")
            if inside is not None:
                total = n if n is not None else (inside or 0) + (outside or 0)
                allowed.add((inside, total))
                allowed.add((outside if outside is not None else total - inside, total))
            counts = d.get("option_counts")
            if isinstance(counts, str) and n is not None:
                for part in counts.split(","):
                    if "=" in part:
                        try:
                            allowed.add((int(part.split("=")[1].strip()), n))
                        except ValueError:
                            pass
    return allowed


def _option_pairs(dimension: dict) -> set:
    """A set dimension's own `N of M`s: every `optionCounts` row of `n`."""
    counts, n = dimension.get("option_counts"), dimension.get("n_anchored")
    pairs = set()
    if isinstance(counts, str) and n is not None:
        for part in counts.split(","):
            if "=" in part:
                try:
                    pairs.add((int(part.split("=")[1].strip()), n))
                except ValueError:
                    pass
    return pairs


def _counts_in(paragraph: str) -> set:
    return {(_number(m.group(1)), _number(m.group(2))) for m in _COUNT_RE.finditer(paragraph)}


def _coverage(paragraph: str, vectors: list) -> tuple[bool, str]:
    lowered = paragraph.casefold()
    faults, notes = [], []
    # The deciding line's number beside the founder's own phrase, wherever there is one.
    for vector in vectors:
        line = deciding_line(vector)
        if not line:
            continue
        name = vector.get("vector")
        observed = line.get("observed")
        if observed and observed not in paragraph:
            faults.append(f"{name}'s deciding line ({line.get('key')}) reads {observed!r} and the "
                          "paragraph does not quote it")
        # Call 42: a set's line with no money figure (and no band counts) is said in its option counts -- one of them,
        # as `N of M`, is what the check asks for.
        own = _option_pairs(line) if line.get("inside") is None else set()
        if not observed and own and not (_counts_in(paragraph) & own):
            faults.append(f"{name}'s deciding line ({line.get('key')}) is a set and the paragraph "
                          "quotes none of its option counts as N of M")
        # brief.md, "The four things the paragraph says", 2: `founder_phrase` against `observed`
        # on every bet whose verdict is `NOT_HOLDING_UP` -- and on no other (a holding bet is said
        # "with the count that settled it", a split "by the answers they actually gave"). The
        # phrase is "what the founder said ... and nothing else": no paraphrase is licensed.
        phrase = line.get("founder_phrase")
        if (vector.get("verdict") == "NOT_HOLDING_UP" and observed and phrase
                and phrase.casefold() not in lowered):
            faults.append(f"{name}'s deciding line was said by the founder as {phrase!r} and the "
                          "paragraph does not carry it")
        notes.append(f"{name}: deciding line {line.get('key')} checked")
    allowed = _allowed_counts(vectors)
    for match in _COUNT_RE.finditer(paragraph):
        pair = (_number(match.group(1)), _number(match.group(2)))
        if pair not in allowed:
            faults.append(f"the count {match.group(0)!r} is no dimension's inside, outside or "
                          "option count of n")
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
    keys = sorted(set(_DOTTED_KEY_RE.findall(paragraph)))
    if keys:
        faults.append(f"dimension key(s) {keys}")
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
                          else "the standings were read, not reproduced or obeyed")


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
