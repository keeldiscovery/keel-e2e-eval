"""The vectors corpus becomes the script (spec 039; spec 041: corpus revision 10, contract 13; spec 042: corpus
revision 11, contract 14 -- one RESPONDENT_QUESTIONS job a lock, the founder's name for the idea).

One revision-11 corpus entry in; out come the three things S-005, S-006 and S-007 need to drive the
**vector corridor** deterministically, and nothing else:

1. a **keel-runtime scripted-executor script** keyed by screen name -- the corridor's screens
   (`CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`, `CALIBRATION_QUESTIONS`, `ASKED`,
   `RESPONDENT_QUESTIONS`), the gate-story reading (`INTERPRET`) and, since keel-cloud 104 (contract 19), the themes
   job (`THEMES`, one entry a failing dimension, chosen by dimension -- see `THEMES_SCREEN`; the brief's BRIEF left),
   every result written in contract 13's screen shapes (contract 14 moved no screen schema) from the entry's own
   stored texts;
2. the **context-keys table** that script is matched through (`context_keys_for`), derived from
   keel-cloud's own export rather than copied -- see that function for why it is not the export
   byte for byte;
3. the **founder's typed inputs** (the four context fields, the recall window, the two seeds, one
   answer per calibrated dimension -- a list dimension's Answer words, its saved list and its picked
   index -- and the persona) and **each person's typed inputs** (the gate, the story or chip, one
   answer per item, by dimension and by the wire's own code).

**Contract 13 (keel-cloud 087 / 088 / 089).** `CALIBRATION_QUESTIONS` answers a list dimension with its
Check-screen draft, `list {items[{label, asked?}], phrase?}` -- the entry's own founder list, which is
what the founder then saves untouched -- and runs once a vector *and once more for every list
dimension the founder answers* (`POST calibration/{vector}/draft`: the same key set, `answers`
carrying the founder's Answer), so its entries are the corridor's own order (`calibration_jobs`).
`RESPONDENT_QUESTIONS` writes the gate's clause and nothing else (`{key, event?}`) -- and since keel-cloud 091
(contract 14) it is **one job a lock**, part 1 on the primary link, the part that carries the gate; parts 2 and 3 are
composed by code in the lock's own commit, so the script answers part 1 alone; `ASKED` the
stranger's faces of a saved Compatibility / Adoption friction list (the corpus's own `asked`).

**The wire's codes are code's** (keel-cloud 087 judgement call 2): a list item is coded by position
(`own`, `rival_1`..; `outcome_1`..; `item_1`..; `benefit_1`..; `nobody_else`, `role_1`..; `step`),
while the corpus keeps revision 9's slugs. `wire_code` maps one onto the other by the item's place in
the founder's list, so a person's pick is sent -- and an `optionCounts` row compared -- on the wire's
code.

**One reader, one hash.** The entry is read through `instructions/corpus.py` -- the revision-11
reader the instruction eval already uses -- and never a second time.

**What the corpus does not carry is composed, and named** (`COMPOSED`). Revision 10 records the
founder's lists, the golden codes and people; it records no gate clause, no Prevalence option labels,
no Answer-screen words. A screen result needs them, so this module writes them in
one fixed register and spec 041's *Disagreements* list every one. A composed word never reaches an
assertion about a standing: the engine compares codes.

**Nothing generated is committed.** The script, the context-keys table and the typed inputs go into
the run bundle, so a run can never be green against a script that drifted from the corpus.

    python3 -m harness.vectors_script 01-countly     # prints the script it would write
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from instructions import chain as chain_mod
from instructions import corpus as corpus_reader

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# The screen names the script is keyed by (`context_keys_for`). Since keel-cloud 091 `RESPONDENT_QUESTIONS` is one
# name again, on part 1's key set: the lock starts that one job and no other (spec 042).
CONTEXT_SCREEN = "CONTEXT_INTERPRET"
PROBLEM_SCREEN = "PROBLEM_INTERPRET"
MECHANISM_SCREEN = "SOLUTION_MECHANISM"
CALIBRATION_SCREEN = "CALIBRATION_QUESTIONS"
RESPONDENT_SCREEN = "RESPONDENT_QUESTIONS"
INTERPRET_SCREEN = "INTERPRET"
#: keel-cloud 104 (contract 19): one job a failing dimension, `{dimension, name, rungHeading, answers[{id, text}]}`,
#: answered `{themes: [{label, answerIds}]}`. The ids are the invitations', minted on the stack, and the jobs run side
#: by side in no fixed order -- so keel-runtime 0.8.0's scripted executor (spec 012, bundled in keel-connect-skill
#: 2.5.0) chooses a THEMES entry by the context's `dimension`, never by the cursor, and resolves each theme scripted
#: by its answers' **texts** (`{label, answers: [text, ...]}`) to the context's ids by verbatim equality, refusing a
#: text the context does not carry. `themes_entries` writes one entry a dimension the walks leave failing with
#: follow-up answers -- the fake's grouping (`harness/interviewer_fake.themes`) of the very lines the walks post --
#: and a catch-all with no themes last, so a dimension nobody expected to fail serves the raw fallback, not a refusal.
THEMES_SCREEN = "THEMES"
#: `Insights.Due.context()`'s keys, in its order: the table must name THEMES by exactly these (keel-runtime 012 FR-1).
THEMES_KEYS = ("dimension", "name", "rungHeading", "answers")
#: keel-cloud 088 (contract 12): the `asked` faces of a saved Compatibility / Adoption friction list.
ASKED_SCREEN = "ASKED"
CORRIDOR_SCREENS = (CONTEXT_SCREEN, PROBLEM_SCREEN, MECHANISM_SCREEN, CALIBRATION_SCREEN,
                    ASKED_SCREEN, INTERPRET_SCREEN, THEMES_SCREEN)

LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"

# keel-cloud `IdeaLines.BELIEF_FRAME` (spec 084, rule L4): the idea's third line starts with it.
BELIEF_FRAME = "The people building it believe it would "

#: The one note every composed calibration question carries (`respondent_note` is required).
RESPONDENT_NOTE = "Respondents are asked about their own most recent time, never about this."

#: Every place this module writes a word the corpus does not record (spec 041 *Disagreements*).
COMPOSED = (
    "SOLUTION_MECHANISM.idea_how / idea_belief -- r10 records none; composed from the mechanism (keel-cloud 097 F7: "
    "no idea_what -- the idea's name is never the model's)",
    "CALIBRATION_QUESTIONS Prevalence's event and its five fifths' labels and belief phrases -- r10 records "
    "only the founder's chosen code and its phrase",
    "the founder's Answer-screen words on each list dimension -- r10 records the saved list, not the Answer "
    "it was drafted from; composed as the list's own labels, at most 25 words (Importance's: the others alone, "
    "spec 046 -- the own item is the problem, code's, locked first -- and on 01-countly one of them, on 05-paidly two, "
    "the founder typing the rest on the Check screen: IMPORTANCE_NAMED)",
    "RESPONDENT_QUESTIONS the gate's event clause -- r10 records none (keel-cloud 088 call 13); 'have a time "
    "when {circumstance}', or the referee's shorter clause where that frames past 20 words (E4)",
    "the founder's own name for the idea on S2 (keel-cloud 090, D14; 097 F7) -- r11 records Keel's short name only and "
    "no r11 solution seed carries a product name, so every founder types one: the entry's short name, or one entry's "
    "own (IDEA_NAMES)",
)


class VectorsScriptError(RuntimeError):
    """A value the corpus does not carry, or carries in a shape the wire cannot take. Named."""


# ------------------------------------------------------------------------------- the id codec

def _hash12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def item_id(token: str, dimension: str) -> str:
    """keel-cloud `InterviewIdCodec.itemId`: the gate's and each item's id, by dimension."""
    return _hash12(f"{token}|item|{dimension}")


def option_id(token: str, dimension: str, code: str) -> str:
    """keel-cloud `InterviewIdCodec.optionId`: an option's (and an advantage's) id, by its code."""
    return _hash12(f"{token}|option|{dimension}|{code}")


# ------------------------------------------------------------------------------- reading in

def load(keel_cloud, *, backtest: bool = False) -> corpus_reader.Corpus:
    """The corpus, through `instructions/corpus.py` and nothing else: revision 10 or a refusal. `backtest` (spec 062):
    the back-test directory beside it, read the same way."""
    return corpus_reader.load(keel_cloud, backtest=backtest)


def entry_for(keel_cloud, entry_id: str, *, backtest: bool = False):
    """`(corpus, entry)` for one id -- the golden corpus's, or with `backtest` (spec 062 FR-1) the back-test
    directory's. An id the directory does not hold is refused by name."""
    corpus = load(keel_cloud, backtest=backtest)
    entry = corpus.by_id(entry_id)
    if entry is None and backtest:
        raise VectorsScriptError(
            f"no back-test entry {entry_id!r} in {corpus.directory} "
            f"(it holds {', '.join(e.id for e in corpus.entries) or 'nothing'})")
    if entry is None:
        raise VectorsScriptError(
            f"no corpus entry {entry_id!r} in {corpus.directory} "
            f"(it holds {', '.join(e.id for e in corpus.entries)})")
    return corpus, entry


# ------------------------------------------------------------------------- the recall window

#: D13 (keel-cloud 087): CYCLES and SHIFTS went with the one-unit window; a window counts at least two.
_UNIT_WORDS = {"NIGHTS": ("night", "nights"), "DAYS": ("day", "days"),
               "WORKING_DAYS": ("working day", "working days"), "WEEKS": ("week", "weeks"),
               "MONTHS": ("month", "months")}


@dataclass(frozen=True)
class Window:
    count: int
    unit: str           # the wire's enum: NIGHTS | DAYS | WORKING_DAYS | WEEKS | MONTHS

    def as_wire(self) -> dict:
        return {"count": self.count, "unit": self.unit}


def window_of(entry) -> Window:
    raw = (entry.context or {}).get("recall_window") or {}
    if not raw.get("count") or int(raw["count"]) < 2 or raw.get("unit") not in _UNIT_WORDS:
        raise VectorsScriptError(f"{entry.id}: context.recall_window is {raw!r}; the wire needs "
                                 f"{{count >= 2, unit in {sorted(_UNIT_WORDS)}}} (D13)")
    return Window(count=int(raw["count"]), unit=str(raw["unit"]))


def frequency_fits(entry) -> bool:
    """Whether the corpus's Frequency can be stated on the entry's **own** recall window.

    keel-cloud counts Frequency in the window's own unit, on an axis from 0 to the window's count
    (the respondent's `segmented_0_to_7` runs 0..count). The corpus keeps Frequency on the founder's
    own "out of N", so where the founder's range or any pick lies past the window's count the founder
    cannot state it and no respondent can answer it, and the journey leaves Frequency **out** (`unsure`)
    rather than inventing a number (spec 039 D-1, spec 041 D-1, spec 042 D-1). Countly's {4, WEEKS}
    carries its "1 to 3 weeks out of 4" and, since revision 11 (keel-cloud 091), Paidly's {3, MONTHS}
    its "2 to 3 months out of 3": Frequency is asked on both. Mulch Run's "working days out of 7" on
    {2, WEEKS} still does not fit (091 judgement call 11 left it).
    """
    window = window_of(entry)
    answer = (entry.founder_calibration.get("problem.frequency") or {}).get("answer")
    if not isinstance(answer, dict):
        return False
    if float(answer.get("upper") or 0) > window.count:
        return False
    for person in entry.people():
        value = (person.picks or {}).get("problem.frequency")
        if isinstance(value, (int, float)) and value > window.count:
            return False
    return True


def window_words(window: Window) -> str:
    """keel-web `RECALL_WINDOW_WORDS`: "7 nights", "4 weeks" -- what the context card's *Counting the
    last ...* line carries."""
    return f"{window.count} {_UNIT_WORDS[window.unit][1]}"


# ------------------------------------------------------------------------- the founder's words

def _ctx(entry) -> dict:
    return entry.context or {}


def _sentence(text: str) -> str:
    text = " ".join(str(text).split()).strip()
    return text[:1].upper() + text[1:]


def _words(text: str) -> int:
    text = (text or "").strip()
    return len(text.split()) if text else 0


def short_name(entry) -> str:
    name = (entry.solution_mechanism or {}).get("short_name")
    if not name:
        raise VectorsScriptError(f"{entry.id}: solution_mechanism.short_name is missing")
    return str(name)


def offer_name(entry) -> str:
    name = (entry.interpretations or {}).get("offer_name")
    if not name:
        raise VectorsScriptError(f"{entry.id}: interpretations.offer_name is missing")
    return str(name)


def occasion(entry) -> str:
    """`context.occasion` (r10 records one on every entry: *delivery*, *invoice*, *yard run*)."""
    return entry.occasion() or "time"


#: Spec 064 FR-4a (keel-cloud 116, *Proposed after* in its tasks.md): the founder's Prevalence clause names the problem,
#: not the routine -- `(founder's clause, past tense, their words; the gate's clause, base form, said to the stranger)`,
#: each framed by code within E4's 20 words and with no time word (COMPOSED). 116 frames the gate *did {clause}* when the
#: clause opens *you* / *your*, else *did you {clause}*; none of these does.
PROBLEM_CLAUSES = {
    "01-countly": ("had to recount stock by hand after a mismatched delivery",
                   "have to recount stock by hand after a mismatched delivery"),
    "02-compliancelog": ("had to pull training completions into a spreadsheet by hand",
                         "have to pull training completions into a spreadsheet by hand"),
    "03-lullaby": ("had to work out why their baby was crying", "have to work out why your baby was crying"),
    "04-linerly": ("lost time to a puncture riding to or from work", "lose time to a puncture riding to or from work"),
    "05-paidly": ("waited beyond agreed terms to be paid for an approved invoice",
                  "wait beyond agreed terms to be paid for an approved invoice"),
    "06-repeatline": ("had to type a refill request in by hand", "have to type a refill request in by hand"),
    "07-mulchrun": ("waited at the supply yard for mulch for a job", "wait at the supply yard for mulch for a job"),
}


def event_past(entry) -> str:
    """Prevalence's clause for the founder (rules E1-E3): what happened, past tense, no time word -- since spec 064 the
    problem the founder counted (`PROBLEM_CLAUSES`), which keel-cloud 116 hands the gate's job as `problem`."""
    if entry.id in PROBLEM_CLAUSES:
        return PROBLEM_CLAUSES[entry.id][0]
    return f"had a time when {_ctx(entry)['circumstance']}"


#: keel-cloud 088 `E4`: framed, the gate ("In the last 3 months, did you ...?") and the Frequency question
#: ("On how many of those 3 months did you ...?") are each at most 20 words. Where "have a time when
#: {circumstance}" frames longer, the referee's shorter clause, in the same register (COMPOSED).
GATE_EVENTS = {
    "02-compliancelog": "have the training-compliance report fall due at quarter close",
    "04-linerly": "get a tyre puncture on the way to or from work",
    "05-paidly": "wait to be paid for an invoice an agency had approved",
    "07-mulchrun": "fetch mulch from the supply yard for a job",
}

#: keel-cloud `SpokenForm.STEM_MAX_WORDS`.
STEM_MAX_WORDS = 20


def gate_question(window: Window, event: str) -> str:
    """keel-cloud `WindowFrame.gate`."""
    return f"In the last {window_words(window)}, did you {event}?"


def frequency_question(window: Window, event: str) -> str:
    """keel-cloud `WindowFrame.frequencyRespondent(window, event)`."""
    return f"On how many of those {window_words(window)} did you {event}?"


def event_base(entry) -> str:
    """The gate's clause for the respondent: base form, second person, framed within E4's 20 words."""
    event = (PROBLEM_CLAUSES.get(entry.id) or (None, None))[1] or GATE_EVENTS.get(entry.id) \
        or f"have a time when {_ctx(entry)['circumstance']}"
    window = window_of(entry)
    longest = max(_words(gate_question(window, event)), _words(frequency_question(window, event)))
    if longest > STEM_MAX_WORDS:
        raise VectorsScriptError(f"{entry.id}: the gate's clause {event!r} frames a question of {longest} "
                                 f"words; E4 allows {STEM_MAX_WORDS} (add a shorter clause to GATE_EVENTS)")
    return event


#: Spec 064 FR-4 / 4b (keel-cloud 120's golden table): the segment's core and the condition the gate's chip asks, by entry
#: -- `(core, condition, chip question, the code inside)`; a condition completes *Only people who ...* (X6). 06 and 07
#: have none (a place, a role or a season is the core). The occasion stays the plain noun (no stem scripted: 120 says
#: 064 may keep it, and a stem would move every golden Importance, Current solution, Compatibility and Relative
#: advantage question's words -- judgement call).
SEGMENTS = {
    "01-countly": ("independent restaurant managers in the US", "run one or two sites", "Do you run one or two sites?",
                   "YES"),
    "02-compliancelog": ("HR managers at US firms", "work at a firm of 200 to 500 people",
                         "Does your firm have 200 to 500 people?", "YES"),
    "03-lullaby": ("first-time parents in the US", "have a baby under six months", "Is your baby under six months old?",
                   "YES"),
    "04-linerly": ("commuter cyclists in Portland", "ride thirty miles a week or more",
                   "Do you ride thirty miles a week or more?", "YES"),
    "05-paidly": ("freelance translators in the US", "work mostly for agencies", "Do you work mostly for agencies?",
                  "YES"),
}


def segment_of(entry) -> dict:
    """`{core, condition}` as the scripted CONTEXT_INTERPRET writes it (keel-cloud 120 FR-2): the entry's own segment as
    the core with no condition where `SEGMENTS` names none."""
    if entry.id in SEGMENTS:
        core, condition, _, _ = SEGMENTS[entry.id]
        return {"core": core, "condition": condition}
    return {"core": _ctx(entry)["segment"], "condition": None}


def segment_line(entry) -> str:
    """`ContextSlots.segmentLine()`: the core, then *, who {condition}* -- what the brief's header and every job read."""
    seg = segment_of(entry)
    return seg["core"] if not seg["condition"] else f"{seg['core'].strip()}, who {seg['condition']}"


def chip_of(entry) -> dict | None:
    """The gate's segment chip the scripted part-1 job writes (`condition: {question, inside}`), or None."""
    if entry.id not in SEGMENTS:
        return None
    _, _, question, inside = SEGMENTS[entry.id]
    return {"question": question, "inside": inside}


_RELATIVE = re.compile(r"(?i)\bwho\b")


def _phrase(text) -> str:
    out = " ".join(str(text or "").split())
    while out and out[-1] in ".,;:":
        out = out[:-1].strip()
    return out


def read_back(entry) -> str | None:
    """keel-cloud 122 `ReadBack.sentence` over the scripted slots: *"<Segment>, when <when>, <what>, counting the last
    <window>."* -- the core capitalised, the condition after *, who* (or * and* where the core has its own *who*), the
    circumstance, the job, the window's words. What the context card serves since 122; never the model's line."""
    seg = segment_of(entry)
    segment, when, what = _phrase(seg["core"]), _phrase(_ctx(entry).get("circumstance")), _phrase(_ctx(entry).get("job"))
    if when.lower().startswith("when "):
        when = when[5:].strip()
    if not (segment and when and what):
        return None
    who = _phrase(seg["condition"])
    if who.lower().startswith("who "):
        who = who[4:].strip()
    out = segment[:1].upper() + segment[1:]
    if who:
        out += (" and " if _RELATIVE.search(segment) else ", who ") + who
    out += f", when {when}, {what}, counting the last {window_words(window_of(entry))}."
    return out


def context_result(entry) -> dict:
    """CONTEXT_INTERPRET's result (screen response contract 23): the slots, `segment` as `{core, condition}` (keel-cloud
    120), the plain occasion noun, `window.proposed` null; no `understands` -- the sentence is code's since 122."""
    ctx = _ctx(entry)
    return {"actor": ctx["actor"], "actor_plural": ctx["actor_plural"], "job": ctx["job"],
            "circumstance": ctx["circumstance"], "segment": segment_of(entry), "occasion": occasion(entry),
            "window": {"proposed": None}}


def problem_result(entry) -> dict:
    return {"statement": (entry.interpretations or {})["problem"], "offer_name": offer_name(entry)}


def idea_lines(entry) -> dict:
    """The idea's three lines as r10 composed them: *Imagine {short_name}.*, the how, the belief. Since keel-cloud 097
    (F7) the what line is not the model's -- the script sends `idea_how` / `idea_belief` alone -- and the what is the
    name the founder types (`idea_name`)."""
    m = entry.solution_mechanism or {}
    what = f"Imagine {short_name(entry)}."
    how = _sentence(f"{m['trigger']}, {m['actor']} {m['mechanism']}; it gives {m['output']}.")
    belief = BELIEF_FRAME + f"make a real difference when {_ctx(entry)['circumstance']}."
    return {"what": what, "how": how[:300], "belief": belief[:200]}


#: keel-cloud 090 (D14): the founder names the idea on S2. Since keel-cloud 097 (F7) every founder does -- Keel drafts
#: no name and no r11 seed carries one (`seed_idea_name`) -- so every journey types the entry's short name, and one
#: entry's founder types a name of their own -- three plain words, no claim word (L3) and no product word, at most five
#: (L5) -- so one journey proves the name every later question uses is the founder's, not the card's (spec 042 call
#: 117, spec 046, COMPOSED).
IDEA_NAMES = {"05-paidly": "Invoice payout service"}

#: keel-cloud `IdeaLines.NAME_MAX_WORDS` (L5).
NAME_MAX_WORDS = 5


def idea_name_of(line: str) -> str:
    """keel-cloud `IdeaLines.nameOf` (spec 090): the name a what line carries -- a trailing full stop and a leading
    *Imagine* are not part of it, whitespace runs are one space, a leading article is kept (lower-cased), and a first
    word in sentence case is lower-cased when the name has more than one word and no other word starts with a
    capital (it is read mid-sentence)."""
    name = " ".join(str(line or "").split())
    while name.endswith("."):
        name = name[:-1].strip()
    if name[:7].lower() == "imagine" and (len(name) == 7 or name[7] == " "):
        name = name[7:].strip()
    if not name:
        return name
    words = name.split(" ")
    first = words[0]
    article = first.lower() in ("a", "an", "the")
    sentence_case = first[:1].isupper() and first[1:] == first[1:].lower()
    rest_lower = all(not w[:1].isupper() for w in words[1:])
    if article or (sentence_case and len(words) > 1 and rest_lower):
        words[0] = first.lower()
    return " ".join(words)


# keel-cloud 097 `IdeaName.fromSeed`, restated: a quoted phrase of one to five words with no sentence punctuation, else
# the first run of two to five capitalised words that is not only a sentence's opening capital, not a place and not
# acronyms alone; else nothing.
_QUOTED = re.compile(r'"([^"]{1,80})"|\u201c([^\u201d]{1,80})\u201d|\u2018([^\u2019]{1,80})\u2019')
_SEED_WORD = re.compile(r"[^\W_]+(?:[-'\u2019&][^\W_]+)*")
_OPENERS = {"a", "an", "the", "it", "its", "this", "that", "these", "those", "we", "our", "i", "my", "you", "your",
            "they", "their", "he", "she", "when", "if", "after", "before", "once", "then", "so", "and", "but",
            "imagine", "with", "for", "every", "each", "there", "here", "what", "how", "today", "now"}
_PLACE_WORDS = {"in", "at", "from", "near", "across", "around", "throughout"}
_ASCII_PUNCT = re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
_ASCII_PUNCT_NO_PAREN = re.escape("!\"#$%&'(*+,-./:;<=>?@[\\]^_`{|}~")


def _clean_name(phrase: str | None) -> str:
    phrase = re.sub(r"\s+", " ", (phrase or "").strip())
    phrase = re.sub(f"^[{_ASCII_PUNCT}]+|[{_ASCII_PUNCT_NO_PAREN}]+$", "", phrase)
    return phrase.strip()


def seed_idea_name(seed: str | None) -> str | None:
    """keel-cloud 097 `IdeaName.fromSeed` (judgement call 14): the product name the founder's solution seed carries, or
    `None`. keel-cloud also drops a name its Save rules (L1-L3, L5) would refuse; no r11 seed yields one either way."""
    if not seed or not seed.strip():
        return None
    for m in _QUOTED.finditer(seed):
        phrase = _clean_name(m.group(1) or m.group(2) or m.group(3))
        words = len(phrase.split(" ")) if phrase else 0
        if 1 <= words <= NAME_MAX_WORDS and not re.search(r"[.!?;:]", phrase):
            return phrase
    tokens = [(m.start(), m.end()) for m in _SEED_WORD.finditer(seed)]

    def text(t):
        return seed[t[0]:t[1]]

    def capitalised(t):
        return seed[t[0]].isupper()

    def sentence_start(t):
        before = seed[:t[0]].rstrip()
        return not before or before[-1] in ".!?:;\n\"\u201c("

    i = 0
    while i < len(tokens):
        if not capitalised(tokens[i]):
            i += 1
            continue
        end = i
        while end + 1 < len(tokens) and capitalised(tokens[end + 1]) \
                and re.fullmatch(r"[ \t]+", seed[tokens[end][1]:tokens[end + 1][0]]):
            end += 1
        start = i
        if sentence_start(tokens[i]) and text(tokens[i]).lower() in _OPENERS:
            start += 1
        place = start > 0 and start == i and text(tokens[i - 1]).lower() in _PLACE_WORDS
        words = end - start + 1
        acronyms = all(text(tokens[k]) == text(tokens[k]).upper() for k in range(start, end + 1))
        if not place and 2 <= words <= NAME_MAX_WORDS and not acronyms:
            return _clean_name(seed[tokens[start][0]:tokens[end][1]])
        i = end + 1
    return None


def idea_view(entry) -> dict:
    """`IdeaView` as keel-cloud serves it once the mechanism card lands (spec 090 FR-003; 097 F7): `what` the seed's
    product name or **None** (no r11 seed carries one), `how` and `belief` Keel's draft."""
    lines = idea_lines(entry)
    return {"what": seed_idea_name(" ".join(str((entry.statements or {}).get("solution") or "").split())),
            "how": lines["how"], "belief": lines["belief"]}


def idea_card(name: str) -> str:
    """keel-cloud `IdeaLines.card` (spec 090): the strangers' what line, composed by code -- *Imagine {name}.*"""
    return f"Imagine {name.strip()}."


def benefit_question(occasion_word: str, name: str) -> str:
    """keel-cloud `BenefitFirst.question` (spec 091 FR-E): Relative advantage's stem, around the idea's current name."""
    return f"On your last {occasion_word.strip() or 'time'}, would {name.strip() or 'the idea'} have made things " \
           "better, or not?"


def founder_idea_name(entry) -> str:
    """What the founder types as the idea's name on S2 (keel-cloud 097 F7: every founder names it) -- the entry's own
    (`IDEA_NAMES`; on a back-test entry its top-level `idea_name`, spec 062 FR-1) or its short name."""
    return IDEA_NAMES.get(entry.id) or getattr(entry, "idea_name", None) or short_name(entry)


def idea_name(entry) -> str:
    """The idea's name after S2 -- what the founder typed -- as keel-cloud stores it (`IdeaLines.nameOf`)."""
    return idea_name_of(founder_idea_name(entry))


#: keel-cloud 121 `Vocabulary.JARGON_WORDS` (T001): the words `J1` notes on the idea's lines (a note, never a refusal).
JARGON_WORDS = ("escrow", "stablecoin", "stablecoins", "api", "apis", "on-chain", "blockchain", "ledger", "ledgers",
                "saas", "workflow", "workflows", "orchestration", "platform", "integration", "integrations", "custody",
                "custodian", "kyc", "aml", "sdk", "webhook", "webhooks", "middleware", "tokenized", "tokenised",
                "smart contract", "fiat")


def jargon(text: str) -> list[str]:
    """`Vocabulary.jargon`: every jargon word `text` carries, as it spells it, in order, whole-word (a hyphen joins)."""
    out = []
    for m in re.finditer(r"[A-Za-z]+(?:-[A-Za-z]+)*(?:\s+contract)?", text or ""):
        word = m.group(0)
        for candidate in (word, word.split()[0]):
            if candidate.lower() in JARGON_WORDS and candidate not in out:
                out.append(candidate)
                break
    return out


def expected_j1(entry) -> list[str]:
    """Spec 064 FR-5b (keel-cloud 121): the J1 notes the scripted idea's how and belief draw -- 05-paidly's
    *platform* -- the words, in order (the idea's `notes[].word`)."""
    lines = idea_lines(entry)
    return jargon(lines["how"]) + [w for w in jargon(lines["belief"]) if w not in jargon(lines["how"])]


def mechanism_result(entry) -> dict:
    m = entry.solution_mechanism or {}
    terms = list(m.get("mechanism_terms") or [])
    if len(terms) < 3:
        # keel-cloud wants 3-8 mechanism terms; r10's Paidly records two. The short name's own
        # content words fill the list -- words the mechanism already uses, never new ones.
        for word in short_name(entry).split():
            if len(terms) >= 3:
                break
            if len(word) > 3 and word not in terms:
                terms.append(word)
    idea = idea_lines(entry)
    return {"actor": m["actor"], "trigger": m["trigger"], "mechanism": m["mechanism"],
            "output": m["output"], "not_assumed": list(m.get("not_assumed") or []),
            "mechanism_terms": terms, "short_name": short_name(entry),
            "idea_how": idea["how"], "idea_belief": idea["belief"]}


# ---------------------------------------------------------------------- the founder's calibration

def is_b2b(entry) -> bool:
    return entry.b2b()


def calibrated_keys(entry, vector: str) -> list[str]:
    """The registry slice the calibration job writes for `vector`, in registry order: Ability to pay
    never (derived), Purchase friction on a B2B persona only."""
    keys = {"PROBLEM": ["problem.prevalence", "problem.frequency", "problem.importance",
                        "problem.current_solution_satisfaction"],
            "SOLUTION": ["solution.compatibility", "solution.relative_advantage",
                         "solution.adoption_friction"],
            "COMMERCIAL": ["commercial.existing_sacrifice", "commercial.price",
                           "commercial.buyer_payer_alignment", "commercial.purchase_friction",
                           "commercial.commitment"]}[vector]
    if not is_b2b(entry):
        keys = [k for k in keys if k != "commercial.purchase_friction"]
    return keys


def founder_keys(entry, vector: str) -> list[str]:
    """The dimensions the founder's calibration screens show: the job's slice (D13: no one-unit window, so
    Frequency is shown on every project -- runs/DRIFT.md #74 closed)."""
    return calibrated_keys(entry, vector)


#: keel-cloud 087's list controls, by dimension (registry 4 `founder.control`).
LIST_CONTROLS = {
    "problem.importance": "rival_list",
    "problem.current_solution_satisfaction": "scale_lines",
    "solution.compatibility": "item_list",
    "solution.relative_advantage": "benefit_list",
    "solution.adoption_friction": "item_list",
    "commercial.buyer_payer_alignment": "role_list",
    "commercial.purchase_friction": "item_list",
    "commercial.commitment": "one_step",
}
#: `saves.picked`: the list is posted from Choose with the one item tested (keel-web 063 call 4).
PICKED = {"solution.compatibility", "solution.adoption_friction", "commercial.buyer_payer_alignment",
          "commercial.purchase_friction"}
#: `saves.asked`: each item carries the stranger's face (keel-cloud 088 FR-003).
ASKED_FACES = {"solution.compatibility", "solution.adoption_friction"}
#: Buyer and payer's fixed first item, code's (keel-cloud `SavedList.NOBODY_ELSE`).
NOBODY_ELSE = ("nobody_else", "Nobody else")
#: Every escape the registry gives an item (registry 4 `respondent.escape.code`).
ESCAPES = {"cant_recall", "cant_tell", "cant_say", "cant_recall_one", "none_of_these", "someone_else_checks",
           "dont_know", "rather_not_say"}
#: keel-cloud 115's value box: *Nothing* (the number 0, counted), *I don't know* (the escape, apart), *I'd rather not
#: say* (apart, a consumer link) -- sent as `chip`.
VALUE_BOX_CHIPS = {"nothing": "NOTHING", "dont_know": "DONT_KNOW", "rather_not_say": "RATHER_NOT_SAY"}
#: The gate story's chips (spec 064 FR-4 / 6a: keel-cloud 123 FR-3 serves RATHER_NOT_SAY again beside CANT_RECALL).
STORY_CHIPS = {"cant_recall": "CANT_RECALL", "rather_not_say": "RATHER_NOT_SAY"}
#: Contract 33's `GateItem.chips`, in the order drawn.
GATE_CHIPS = ("CANT_RECALL", "RATHER_NOT_SAY")

#: Registry 4's dimension names (`name`), for the referee's brief words only.
NAMES = {"problem.prevalence": "Prevalence", "problem.frequency": "Frequency",
         "problem.importance": "Importance", "problem.current_solution_satisfaction": "Current solution",
         "solution.compatibility": "Compatibility", "solution.relative_advantage": "Relative advantage",
         "solution.adoption_friction": "Adoption friction", "commercial.existing_sacrifice": "Existing sacrifice",
         "commercial.price": "Price", "commercial.ability_to_pay": "Ability to pay",
         "commercial.buyer_payer_alignment": "Buyer and payer",
         "commercial.purchase_friction": "Purchase friction", "commercial.commitment": "Commitment"}


def is_list(key: str) -> bool:
    return key in LIST_CONTROLS


def wire_code(key: str, index: int) -> str:
    """keel-cloud `SavedList.codeFor` (087 judgement call 2): a list item's code is its place."""
    control = LIST_CONTROLS[key]
    if control == "rival_list":
        return "own" if index == 0 else f"rival_{index}"
    if control == "scale_lines":
        return f"outcome_{index + 1}"
    if control == "benefit_list":
        return f"benefit_{index + 1}"
    if control == "role_list":
        return NOBODY_ELSE[0] if index == 0 else f"role_{index}"
    if control == "one_step":
        return "step"
    return f"item_{index + 1}"


def founder_list(entry, key: str) -> dict:
    """The entry's own saved list for a list dimension: `{items: [{code, label, asked?}], picked, phrase}`."""
    saved = entry.founder_list(key)
    if not saved or not saved["items"]:
        raise VectorsScriptError(f"{entry.id}: {key} carries no founder list; a list dimension is drafted "
                                 "from one")
    return saved


#: The list dimensions a stranger picks among the founder's own items; every other dimension's codes are
#: the registry's fixed ones and pass through unchanged.
PICKED_AMONG_ITEMS = ("problem.importance", "problem.current_solution_satisfaction", "solution.relative_advantage")


def wire_codes(entry, key: str) -> dict[str, str]:
    """`{corpus code: wire code}` for a list dimension whose items the stranger picks among (Importance's
    five, Current solution's five outcomes, Relative advantage's benefits); `{}` elsewhere."""
    if key not in PICKED_AMONG_ITEMS:
        return {}
    return {item["code"]: wire_code(key, i) for i, item in enumerate(founder_list(entry, key)["items"])}


def on_the_wire(entry, key: str, code: str) -> str:
    """One corpus code as the wire codes it."""
    return wire_codes(entry, key).get(code, code)


def _founder(entry, key: str) -> dict:
    return entry.founder_calibration.get(key) or {}


def _chosen_codes(entry, key: str) -> list[str]:
    answer = _founder(entry, key).get("answer")
    if isinstance(answer, str):
        return [answer]
    if isinstance(answer, list):
        return [str(a) for a in answer]
    return []


#: Prevalence's five fifths (keel-cloud's `single_choice` codes, by position) in a register that names no
#: product, mechanism, claim word or money (rules X1, C5, C6, W9); the founder's chosen code's phrase is the
#: corpus's own `belief_phrase`, so the belief sentence keel-cloud writes is the corpus's.
#: Spec 064 FR-6a (keel-cloud 123 FR-6): the labels are code's now (`PrevalenceBins`, written over the model's) and share
#: no edge; the script writes the same five so the draft reads as served.
PREVALENCE_OPTIONS = [
    ("Fewer than 2 in 10", "p_0_20", "Only a few"),
    ("2 or 3 in 10", "p_20_40", "A minority"),
    ("4 or 5 in 10", "p_40_60", "Around half"),
    ("6 or 7 in 10", "p_60_80", "Most"),
    ("8 or more in 10", "p_80_100", "Nearly all"),
]


def drafted_list(entry, key: str) -> dict:
    """The `CALIBRATION_QUESTIONS` result's `list` for a list dimension (founder-lists.md): the entry's own
    items in its order -- Buyer and payer's "Nobody else" left to code, which adds it -- each `label`, the
    `asked` face on Compatibility and Adoption friction, and Current solution's `phrase`."""
    saved = founder_list(entry, key)
    items = []
    for item in saved["items"]:
        if key == "commercial.buyer_payer_alignment" and item.get("code") == NOBODY_ELSE[0]:
            continue
        out = {"label": item["label"]}
        if key in ASKED_FACES:
            if not item.get("asked"):
                raise VectorsScriptError(f"{entry.id}: {key} item {item['label']!r} carries no `asked` face (L4)")
            out["asked"] = item["asked"]
        items.append(out)
    if key == "problem.importance":
        items = items[:1 + len(importance_named(entry))]     # Keel adds only what the Answer named (097 F9)
    draft: dict = {"items": items}
    if key == "problem.current_solution_satisfaction":
        if not saved.get("phrase"):
            raise VectorsScriptError(f"{entry.id}: {key} carries no second-person phrase (L1)")
        draft["phrase"] = saved["phrase"]
        # spec 064 FR-5a (keel-cloud 117): the leading rungs the founder typed, kept verbatim, and the line after D4's 2
        rungs = founder_rungs(entry)
        if rungs:
            draft["founder_rungs"] = rungs
            draft["line"] = min(2, rungs)
    return draft


def founder_rungs(entry) -> int:
    """How many of Current solution's outcomes the founder's Answer types (`answer_text`: the phrase, then as many whole
    labels as fit in 25 words) -- keel-cloud 117's `founder_rungs` (2 or 3 on every golden entry)."""
    key = "problem.current_solution_satisfaction"
    saved = founder_list(entry, key)
    labels = [i["label"] for i in saved["items"]]
    text = answer_text(entry, key)
    return sum(1 for label in labels if label in text.split("; "))


def saved_list(entry, key: str) -> dict:
    """The list as the founder saves it and the wire stores it (keel-cloud `SavedList`): every item, in
    order, with code's positional codes, `asked` where the dimension carries faces, `pickedIndex` where it
    picks, Current solution's `phrase`."""
    saved = founder_list(entry, key)
    items = []
    for i, item in enumerate(saved["items"]):
        out = {"code": wire_code(key, i), "label": item["label"]}
        if key in ASKED_FACES and item.get("asked"):
            out["asked"] = item["asked"]
        items.append(out)
    picked = saved.get("picked")
    return {"items": items, "pickedIndex": int(picked) if key in PICKED and picked is not None else None,
            "phrase": saved.get("phrase") if key == "problem.current_solution_satisfaction" else None}


def answer_text(entry, key: str) -> str:
    """The founder's words on a list dimension's Answer screen (at most 25): the list's own labels, joined,
    as many whole ones as fit -- r10 records the list the Answer was drafted from, not the Answer (COMPOSED).
    Buyer and payer with nobody else to agree is "Nobody" (keel-web's hint: *"Nobody" is an answer*)."""
    saved = founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != NOBODY_ELSE[0]]
    if key == "problem.importance":
        # keel-cloud 097 (F9): the Answer names the OTHER difficulties -- the own item is the problem itself, locked
        # first by code -- and Keel's redraft is the own item plus exactly those (spec 046 FM2); on two entries it
        # names fewer than the list holds and the founder types the rest on the Check screen (`IMPORTANCE_NAMED`).
        labels = importance_named(entry)
    if key == "problem.current_solution_satisfaction" and saved.get("phrase"):
        labels = [saved["phrase"]] + labels
    if not labels:
        return "Nobody"
    text = labels[0]
    for label in labels[1:]:
        candidate = f"{text}; {label}"
        if _words(candidate) > 25:
            break
        text = candidate
    return text


#: keel-cloud 097 `common.role_words` (registry decision 21), restated: the role nouns its `L6` refuses in a drafted list
#: item the founder's own words do not carry. `tests/test_feedback_marks.py` holds it equal to keel-cloud's export.
ROLE_WORDS = ("director", "manager", "CFO", "CTO", "CEO", "head", "officer", "VP", "partner", "spouse", "owner",
              "founder", "accountant", "lawyer", "HR", "finance", "legal", "procurement", "IT", "security team")


def role_pattern(word: str) -> re.Pattern:
    """keel-cloud 097 `RoleWords.pattern`, restated: whole words, a plural or possessive counted ("directors",
    "partner's", "owners'"); a word the registry writes in capitals (CFO, HR, IT, VP) matches in capitals only, so
    "it" is never IT; a word of more than one word ("security team") matches across any run of spaces."""
    stripped = word.strip()
    capitals = any(c.isalpha() for c in stripped) and stripped == stripped.upper()
    body = r"\s+".join(re.escape(part) for part in stripped.split())
    regex = rf"(?<![^\W_]){body}(?:s|es)?(?:['\u2019]s?)?(?![^\W_])"
    return re.compile(regex) if capitals else re.compile(regex, re.IGNORECASE)


def carries_role(text: str | None, word: str) -> bool:
    """`RoleWords.carries`: whether `text` carries `word` as a whole word, a plural or possessive counted."""
    if not text or not word or not word.strip():
        return False
    return bool(role_pattern(word).search(text))


def first_unnamed_role(text: str | None, role_words, founders_text: str) -> str | None:
    """`RoleWords.firstUnnamed`: the first role word `text` carries that the founder's text does not, in list order."""
    if not text or not text.strip():
        return None
    return next((w for w in role_words if carries_role(text, w) and not carries_role(founders_text, w)), None)


def founders_words_before_answers(entry) -> str:
    """The founder's own words keel-cloud's `L6` reads on a vector's FIRST draft -- before any Answer: the context
    fields as typed, the problem seed, the persona's decider and the confirmed mechanism card (097 call 6; the saved
    lists and the context slots it also reads are left out, so the script never leans on them)."""
    ctx = _ctx(entry)
    m = entry.solution_mechanism or {}
    parts = [ctx.get(k) for k in ("actor", "job", "circumstance", "segment")]
    parts += [(entry.statements or {}).get("problem")]
    parts += [m.get(k) for k in ("actor", "trigger", "mechanism", "output")] + list(m.get("not_assumed") or [])
    if is_b2b(entry):
        parts.append(entry.decision_maker_role())
    return " ".join(str(p) for p in parts if p)


#: keel-cloud 097 (F9, judgement call 12): Save and the lock need Importance's own item and two others.
IMPORTANCE_MIN_ITEMS = 3


#: Spec 046 FR-003 (keel-web 070 F9): how many of the other difficulties the founder's Importance Answer names, where
#: it names fewer than the corpus list holds -- the rest the founder types on the Check screen themselves. 01-countly's
#: Answer names ONE (own + 1: the screen asks for one more and Save waits for three, keel-web 071), 05-paidly's TWO (own +
#: 2, the Check screen with two others, Save on); every other entry names them all (COMPOSED).
IMPORTANCE_NAMED = {"01-countly": 1, "05-paidly": 2}


def importance_others(entry) -> list[str]:
    """The other difficulties of the entry's Importance list, in order (the own item is first and code's)."""
    return [i["label"] for i in founder_list(entry, "problem.importance")["items"][1:]]


def importance_named(entry) -> list[str]:
    """The other difficulties the founder's Importance Answer names -- and so Keel's redraft adds (097 F9: no more)."""
    others = importance_others(entry)
    return others[:IMPORTANCE_NAMED.get(entry.id, len(others))]


def importance_typed(entry) -> list[str]:
    """The other difficulties the founder types on Importance's Check screen, after Keel's redraft (070 F9)."""
    return importance_others(entry)[len(importance_named(entry)):]


def importance_first_draft(entry) -> dict:
    """keel-cloud 097 (F9, judgement call 10): Keel's first draft of Importance, before the founder's Answer, is the
    own item alone (`L1`: exactly one) -- the others come from the Answer and Keel adds none."""
    return {"items": [{"label": founder_list(entry, "problem.importance")["items"][0]["label"]}]}


def first_draft(entry, key: str) -> dict:
    """A list's first draft, before the founder's Answer (keel-cloud 097 F6, `L6`): the entry's own items less every one
    that names a role the founder had not yet written -- the role comes from the Answer, which the redraft reads
    (05-paidly's Purchase friction drafts *A security review* alone; the agency owner and finance come with the Answer).
    An item dropped is the corpus's, never replaced."""
    draft = drafted_list(entry, key)
    own = founders_words_before_answers(entry)
    texts = lambda item: [item.get("label"), item.get("asked")]  # noqa: E731
    kept = [item for item in draft["items"]
            if not any(first_unnamed_role(t, ROLE_WORDS, own) for t in texts(item))]
    if not kept and draft["items"]:
        raise VectorsScriptError(f"{entry.id}: every item of {key} names a role the founder has not written before "
                                 "the Answer, so no first draft keel-cloud's L6 takes can be read off the corpus")
    return {**draft, "items": kept}


def calibration_question(entry, key: str, *, first: bool = False) -> dict:
    """One question of the `CALIBRATION_QUESTIONS` result (contract 13): Prevalence's `event` and five
    fifths, a list dimension's `list`, and nothing but the key and the note on Frequency, the cost and the
    price (code's questions). `first`: the slice's first draft, where Importance is the own item alone (097)."""
    q: dict = {"key": key, "respondent_note": RESPONDENT_NOTE}
    if key == "problem.prevalence":
        q["event"] = event_past(entry)
        chosen = _chosen_codes(entry, key)
        phrase = _founder(entry, key).get("belief_phrase")
        q["options"] = [{"label": label,
                         "belief_phrase": phrase if (phrase and code in chosen) else default}
                        for label, code, default in PREVALENCE_OPTIONS]
    elif is_list(key):
        if first and key == "problem.importance":
            q["list"] = importance_first_draft(entry)
        elif first:
            q["list"] = first_draft(entry, key)
        else:
            q["list"] = drafted_list(entry, key)
    elif key not in ("problem.frequency", "commercial.price", "commercial.existing_sacrifice"):
        raise VectorsScriptError(f"{entry.id}: no calibration shape for {key}")
    return q


def calibration_result(entry, vector: str, only: str | None = None) -> dict:
    """A vector's calibration: every dimension of the slice, or -- a redraft -- the one list dimension the
    founder answered (keel-cloud 087 judgement call 8; `C1`: the keys are the one dimension redrafted)."""
    keys = [only] if only else calibrated_keys(entry, vector)
    return {"vector": vector, "questions": [calibration_question(entry, key, first=only is None) for key in keys]}


def calibration_jobs(entry) -> list[tuple[str, str | None]]:
    """Every `CALIBRATION_QUESTIONS` job a journey runs, in the order it runs them: a vector's slice on its
    seed's confirmation (the persona for COMMERCIAL), then one redraft per list dimension the founder
    answers in words (a dimension left out is not drafted). The scripted executor consumes a screen's
    entries in order and all of them share one key set, so this order is the script's."""
    jobs: list[tuple[str, str | None]] = []
    for vector in VECTORS:
        jobs.append((vector, None))
        for key in founder_keys(entry, vector):
            if is_list(key) and not entry.unsure(key):
                jobs.append((vector, key))
    return jobs


@dataclass(frozen=True)
class CalibrationAnswer:
    dimension: str
    body: dict          # the wire's CalibrationAnswer, `dimension` included
    #: A list dimension's Answer-screen words (None elsewhere, and where the founder left it out).
    text: str | None = None

    def as_wire(self) -> dict:
        return dict(self.body)

    @property
    def unsure(self) -> bool:
        return bool(self.body.get("unsure"))

    @property
    def listed(self) -> dict | None:
        return self.body.get("list")


def calibration_answers(entry, vector: str) -> list[CalibrationAnswer]:
    """One typed answer per calibrated dimension, the corpus's own (keel-cloud
    `VectorCorpusFixture.founderAnswer`'s mapping): codes for Prevalence, `interval` for Frequency, `cost` /
    `price` for the two commercial numbers, `list` (the saved list, posted as keel-web posts it: labels,
    the untouched faces, `pickedIndex`, `phrase`) for a list dimension, `unsure` for a dimension left out.
    Ability to pay is never sent -- it is derived."""
    out = []
    for key in founder_keys(entry, vector):
        founder = _founder(entry, key)
        answer = founder.get("answer")
        body: dict = {"dimension": key}
        text = None
        if founder.get("unsure") or answer is None:
            body["unsure"] = True
        elif key == "problem.frequency":
            if not frequency_fits(entry):
                body["unsure"] = True
            else:
                window = window_of(entry)
                body["interval"] = {"low": answer["lower"], "high": answer["upper"],
                                    "unit": f"{_UNIT_WORDS[window.unit][1]} out of {window.count}"}
        elif key == "commercial.existing_sacrifice" and chain_mod.cost_in_chain(answer):
            # spec 064 FR-2 (keel-cloud 115): a chain cost posts every field the entry carries
            body["cost"] = {k: answer[k] for k in sorted(chain_mod.CHAIN_FIELDS_COST) if answer.get(k) is not None}
        elif key == "commercial.existing_sacrifice":
            body["cost"] = {k: answer[k] for k in ("mode", "low", "high", "period") if k in answer}
            if answer.get("rate") is not None:
                body["cost"]["rate"] = answer["rate"]
        elif key == "commercial.price" and chain_mod.price_in_chain(answer):
            # a chain price posts its shape and its numbers, and no period (it is the cost's)
            body["price"] = {k: answer[k] for k in sorted(chain_mod.CHAIN_FIELDS_PRICE) if answer.get(k) is not None}
        elif key == "commercial.price":
            body["price"] = {k: answer[k] for k in ("low", "high", "period")}
        elif is_list(key):
            saved = saved_list(entry, key)
            listed: dict = {"items": [{k: v for k, v in item.items() if k != "code"} for item in saved["items"]],
                            "pickedIndex": saved["pickedIndex"]}
            if saved["phrase"]:
                listed["phrase"] = saved["phrase"]
            body["list"] = listed
            text = answer_text(entry, key)
        elif isinstance(answer, (str, list)):
            body["codes"] = _chosen_codes(entry, key)
        else:
            raise VectorsScriptError(f"{entry.id}: {key}'s founder answer {answer!r} has no wire shape")
        out.append(CalibrationAnswer(dimension=key, body=body, text=text))
    return out


def asked_result(entry, key: str) -> dict:
    """The `ASKED` result for one saved list (keel-cloud 088 FR-003): each item's stranger's face by its
    index, the corpus's own `asked` (K1: one face per index handed). The journey saves every list untouched,
    so code vouches for every face and no ASKED job runs; the entry is here so one would be answered."""
    saved = founder_list(entry, key)
    return {"items": [{"index": i, "asked": item["asked"]} for i, item in enumerate(saved["items"])
                      if item.get("asked")]}


def hourly_rate(entry) -> float | None:
    return entry.hourly_rate() if is_b2b(entry) else None


# ------------------------------------------------------------------- the respondent questions

def plan_keys(entry, part: int, link: str) -> list[str]:
    """The keys keel-cloud plans on `part` for `link`, in registry order: what the founder left out
    is not asked, Frequency is not asked where it was left out, and on a B2B study part 3 is the
    decision-maker's link and asks Ability to pay and Purchase friction too."""
    left_out = {key for key in entry.founder_calibration if entry.unsure(key)}
    if not frequency_fits(entry):
        left_out.add("problem.frequency")
    keys = {1: ["problem.prevalence", "problem.frequency", "problem.importance",
                "problem.current_solution_satisfaction"],
            2: ["solution.compatibility", "solution.relative_advantage",
                "solution.adoption_friction"],
            3: ["commercial.existing_sacrifice", "commercial.price", "commercial.ability_to_pay",
                "commercial.buyer_payer_alignment", "commercial.purchase_friction",
                "commercial.commitment"]}[part]
    if part == 3 and link != LINK_B2B:
        # spec 064 FR-3 (keel-cloud 115 FR-5): a same-person chain study whose cost and price share no base asks the
        # consumer budget item on the primary link, in Ability to pay's place
        drop = ("commercial.purchase_friction",) if entry.consumer_budget() else \
            ("commercial.ability_to_pay", "commercial.purchase_friction")
        keys = [k for k in keys if k not in drop]
    if entry.chain() and (entry.price() or {}).get("shape") == "FREE":
        left_out.add("commercial.price")             # 115 judgement call 9: free to them asks no price item
    return [k for k in keys if k not in left_out]


def respondent_jobs(entry) -> list[tuple[int, str]]:
    """The RESPONDENT_QUESTIONS jobs a lock starts: since keel-cloud 091 (contract 14, design §6) **one**, part 1 on the
    primary link -- the part that carries the gate's clause -- on either persona; parts 2 and 3 (on B2B part 3 the
    decision-maker's link's) are code's, written with the lock."""
    return [(1, LINK_PRIMARY)]


def respondent_item(entry, key: str) -> dict:
    """keel-cloud 088 FR-002: the item is `{key}`, the gate `{key, event}` -- every other word is code's."""
    if key == "problem.prevalence":
        return {"key": key, "event": event_base(entry)}
    return {"key": key}


def respondent_result(entry, part: int, link: str) -> dict:
    """RESPONDENT_QUESTIONS' result: the items, and on part 1 of the primary link the segment's chip (`condition:
    {question, inside}`, keel-cloud 120 FR-2 -- required, E5, where the job is handed a condition)."""
    out = {"part": part, "link": link,
           "items": [respondent_item(entry, key) for key in plan_keys(entry, part, link)]}
    chip = chip_of(entry)
    if chip and part == 1 and link == LINK_PRIMARY:
        out["condition"] = chip
    return out


# ------------------------------------------------------------------------- the readings, the brief

def readable_people(entry) -> list:
    """The people keel-cloud runs `INTERPRET` for, in corpus order: a gate yes on the primary link,
    no chip, a story typed. A chip or a blank story is GUESSED with no job; a gate no and a
    decision-maker's link are never read."""
    return [p for p in entry.people() if p.readable]


def interpret_entries(entry) -> list[dict]:
    out = []
    for person in readable_people(entry):
        if person.anchoring not in ("ANCHORED", "GUESSED"):
            raise VectorsScriptError(f"{entry.id}: {person.person!r} wrote a story and the corpus "
                                     f"records anchoring {person.anchoring!r}")
        out.append({"outcome": "COMPLETED",
                    "result": {"anchoring": person.anchoring, "unprompted": [], "flags": []}})
    return out


#: A stage's verdicts that `broke` (keel-cloud 089 judgement call 10): its answer must cite what broke.
BROKE = ("NOT_HOLDING_UP", "PEOPLE_DISAGREE")


def stage_cite(entry, vector: str) -> str:
    """The one dimension a stage's answer cites: the entry's deciding dimension (`broke.key` where the stage
    broke, keel-cloud 089 FR-007), else the stage's first dimension the founder did not leave out."""
    deciding = ((entry.expected.get("vector_verdicts") or {}).get(vector) or {}).get("deciding")
    if deciding:
        return str(deciding)
    keys = [k for k in founder_keys(entry, vector) if not entry.unsure(k)]
    if not keys:
        raise VectorsScriptError(f"{entry.id}: {vector} has no dimension to cite")
    return keys[0]


def broke_key(entry, vector: str) -> str | None:
    """The corpus's own `broke` for a stage: its deciding dimension when the verdict is a called failure."""
    verdict = (entry.expected.get("vector_verdicts") or {}).get(vector) or {}
    return verdict.get("deciding") if verdict.get("verdict") in BROKE else None


# ------------------------------------------------------------------------- the script itself

@dataclass(frozen=True)
class GeneratedScript:
    entry_id: str
    entry_sha256: str
    source: str
    screens: dict[str, list[dict]]

    def to_json(self) -> dict:
        out = {"_source": self.source, "_entry_id": self.entry_id,
               "_entry_sha256": self.entry_sha256, "_generated_by": "harness/vectors_script.py",
               "_generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        out.update(self.screens)
        return out


def _completed(result: dict) -> dict:
    return {"outcome": "COMPLETED", "result": result}


def generate(entry) -> GeneratedScript:
    """The runtime script for one entry. `CALIBRATION_QUESTIONS` is one entry per job of
    `calibration_jobs`, in the corridor's own order, because every one of them shares one key set and the
    scripted executor consumes a screen's entries in order. `ASKED` is one entry per saved list with faces,
    in corridor order. `INTERPRET` is one entry per readable person, in corpus order, which is why the
    journey reads after each person."""
    screens: dict[str, list[dict]] = {
        CONTEXT_SCREEN: [_completed(context_result(entry))],
        PROBLEM_SCREEN: [_completed(problem_result(entry))],
        MECHANISM_SCREEN: [_completed(mechanism_result(entry))],
        CALIBRATION_SCREEN: [_completed(calibration_result(entry, vector, only))
                             for vector, only in calibration_jobs(entry)],
    }
    asked = [_completed(asked_result(entry, key)) for key in ("solution.compatibility", "solution.adoption_friction")
             if not entry.unsure(key)]
    if asked:
        screens[ASKED_SCREEN] = asked
    (part, link), = respondent_jobs(entry)
    screens[RESPONDENT_SCREEN] = [_completed(respondent_result(entry, part, link))]
    interpret = interpret_entries(entry)
    if interpret:
        screens[INTERPRET_SCREEN] = interpret
    screens[THEMES_SCREEN] = themes_entries(entry, walked_follow_ups(entry, person_inputs(entry)))
    return GeneratedScript(entry_id=entry.id, entry_sha256=entry.sha256,
                           source=f"keel-cloud canon/designs/measured-beliefs/corpus/{entry.path.name}",
                           screens=screens)


# ------------------------------------------------------------------------- the themes (keel-cloud 104)

def failing_keys(entry) -> list[str]:
    """The dimensions the entry's standings leave not holding up or split, in registry order -- the ones keel-cloud
    asks THEMES about (`Insights.due`: NOT_HOLDING_UP / PEOPLE_DISAGREE)."""
    standings = (entry.expected or {}).get("standings") or {}
    return [k for k in NAMES if str((standings.get(k) or {}).get("status") or "").upper() in BROKE]


def walked_follow_ups(entry, people) -> list[tuple[str, str]]:
    """`[(rung, text)]` the script groups (spec 064 FR-7): every rung's one line (`FOLLOW_UP_LINES`) -- since keel-cloud
    118 the rung a person is asked on is the walk's at answer time, so the script cannot know who lands where, only that
    whoever does types that rung's line."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    return [(rung, FOLLOW_UP_LINES[rung][0]) for rung in fake.RUNGS]


def themes_entries(entry, follow_ups) -> list[dict]:
    """The script's THEMES entries (keel-runtime 012's shape): for each dimension the walks can give follow-up answers
    on (registry order, any status -- keel-cloud 119 groups held lines too), `{dimension, outcome: COMPLETED, result:
    {themes: [{label, answers}]}}` -- the fake's piles (`interviewer_fake.themes`, keel-cloud's `FakeThemes`, the
    leftovers ON_THEIR_OWN) of those answers, each pile's texts verbatim, once each -- then the catch-all, `{outcome:
    COMPLETED, result: {themes: []}}`, last."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    by_rung: dict[str, list[str]] = {}
    for rung, text in follow_ups:
        by_rung.setdefault(rung, []).append(text)
    out = []
    for key in NAMES:
        texts = by_rung.get(key)
        if not texts:
            continue
        grouped = fake.themes([{"id": str(i), "text": t} for i, t in enumerate(texts)], NAMES[key])["themes"]
        themes = []
        for pile in grouped:
            said: list[str] = []
            for i in pile["answerIds"]:
                if texts[int(i)] not in said:
                    said.append(texts[int(i)])
            themes.append({"label": pile["label"], "answers": said})
        out.append({"dimension": key, "outcome": "COMPLETED", "result": {"themes": themes}})
    out.append({"outcome": "COMPLETED", "result": {"themes": []}})
    return out


def context_keys_for(exported: dict) -> dict:
    """The scripted executor's screen table, from keel-cloud's own `context-keys.json` export.

    Two changes, each forced by keel-runtime's exact key-set match and each derived from the
    export rather than typed:

    * **`RESPONDENT_QUESTIONS` is part 1's key set.** The export writes the *union* of the key sets
      keel-cloud's `ScreenContextBuilder` can use -- part 1 carries no `mechanism` and no `offer_name`,
      part 2 adds `mechanism`, part 3 on the primary link adds both, part 3 on the decision-maker's link
      `offer_name` alone. Since keel-cloud 091 the lock starts part 1's job and no other, so the table
      names part 1's set alone (spec 041 aliased all four): a part 2 or 3 job, were the cloud ever to start
      one again, matches nothing, fails, and the journey's one-job step says why.
    * **The classic screens are dropped.** No classic job runs on a vectors project, and a table
      that cannot answer one is the honest table.
    * Nothing else: `CALIBRATION_QUESTIONS`, `ASKED`, `INTERPRET` and `THEMES` are the export's own sets.
    """
    out = {}
    for screen in CORRIDOR_SCREENS:
        if screen not in exported:
            raise VectorsScriptError(f"keel-cloud's export carries no context keys for {screen}")
        out[screen] = list(exported[screen])
    union = list(exported.get(RESPONDENT_SCREEN) or [])
    if not {"mechanism", "offer_name"} <= set(union):
        raise VectorsScriptError(
            f"keel-cloud's RESPONDENT_QUESTIONS keys {union} no longer carry both `mechanism` and "
            "`offer_name`; part 1's key set cannot be derived")
    out[RESPONDENT_SCREEN] = [k for k in union if k not in ("mechanism", "offer_name")]
    if tuple(out[THEMES_SCREEN]) != THEMES_KEYS:
        raise VectorsScriptError(f"keel-cloud's THEMES keys {out[THEMES_SCREEN]} are not {list(THEMES_KEYS)} "
                                 "(keel-runtime 012 matches the screen by exactly these four)")
    seen = {}
    for screen, keys in out.items():
        clash = seen.get(frozenset(keys))
        if clash:
            raise VectorsScriptError(f"{screen} and {clash} share the key set {sorted(keys)}")
        seen[frozenset(keys)] = screen
    return out


# ------------------------------------------------------------------------- the typed inputs

@dataclass(frozen=True)
class FounderInputs:
    project_name: str
    country: str
    region: str | None
    language: str
    context_fields: dict       # {actor, job, circumstance, segment}
    window: Window
    problem_seed: str
    solution_seed: str
    decider: dict              # PersonaInput.decider
    calibration: dict          # vector -> [CalibrationAnswer]
    hourly_rate: float | None
    #: What the founder types over S2's what line (keel-cloud 090); `None` saves Keel's draft untouched.
    idea_name: str | None = None


def founder_inputs(entry) -> FounderInputs:
    ctx = _ctx(entry)
    market = entry.market or {}
    statements = entry.statements or {}
    missing = [k for k in ("problem", "solution") if not statements.get(k)]
    if missing:
        raise VectorsScriptError(f"{entry.id}: no {', '.join(missing)} statement")
    if is_b2b(entry):
        # Spec 041 call 93: the persona's role as r10 records it (`persona.decision_maker.role`: *agency*,
        # *owner*), the word keel-cloud 087 read it as ("a B2B decider is the persona's role, 'the agency'"), so
        # Buyer and payer's belief -- "The agency decides, ..." -- is the corpus's; not the role's `label`.
        # spec 064 FR-6 / 6a (keel-cloud 123 FR-10, keel-web 099): a title for every B2B entry -- the entry's
        # `persona.decision_maker.title`, else the role word (keel-web holds Continue until one is typed)
        decider = {"kind": "SOMEONE_ELSE", "role": entry.decision_maker_role(),
                   "title": entry.decider_title() or entry.decision_maker_role()}
    else:
        decider = {"kind": "SAME_PERSON"}
    return FounderInputs(
        project_name=entry.title,
        # never reached (every entry records its market), but a fallback is a country keel-web 078 offers (spec 053)
        country=market.get("country") or "US", region=market.get("region"),
        language=market.get("language") or "en-US",
        context_fields={"actor": ctx["actor"], "job": ctx["job"],
                        "circumstance": ctx["circumstance"], "segment": ctx["segment"]},
        window=window_of(entry),
        problem_seed=" ".join(str(statements["problem"]).split()),
        solution_seed=" ".join(str(statements["solution"]).split()),
        decider=decider,
        calibration={v: calibration_answers(entry, v) for v in VECTORS},
        hourly_rate=hourly_rate(entry),
        idea_name=founder_idea_name(entry),
    )


@dataclass(frozen=True)
class Pick:
    """One item's answer, by dimension and by the wire's code -- the ids are computed per token."""
    dimension: str
    codes: list = field(default_factory=list)
    advantages: list = field(default_factory=list)
    cost: dict | None = None
    scale: int | None = None
    chip: str | None = None
    #: The recall period the corpus recorded a cost total over (`quarter` throughout r10 and r11).
    cost_period: str | None = None
    #: Spec 064 FR-3 (keel-cloud 115): a value box's answer, `{low, high}` in the founder's own unit and period (one
    #: number is both ends) -- sent as `interval`, never re-expressed.
    interval: dict | None = None

    def asked_over(self, period: str | None) -> "Pick":
        """This cost total re-expressed over `period`, the recall period keel-cloud asks it over
        (`InterviewItem.costTotal.recallPeriod`), by keel-cloud's own `Period` days -- so the cost the
        engine normalises to the founder's period is the corpus's to the last digit (spec 039 D-3). A value box's
        interval is never re-expressed: it is asked in the founder's period, and the r13 pick already is."""
        if self.interval is not None:
            return self
        if self.cost is None or not self.cost.get("value") or not period or not self.cost_period \
                or period == self.cost_period:
            return self
        factor = PERIOD_DAYS[period] / PERIOD_DAYS[self.cost_period]
        cost = {**self.cost, "value": round(float(self.cost["value"]) * factor, 6)}
        return Pick(dimension=self.dimension, codes=self.codes, advantages=self.advantages, cost=cost,
                    scale=self.scale, chip=self.chip, cost_period=period)

    def as_wire(self, token: str) -> dict:
        out: dict = {"itemId": item_id(token, self.dimension)}
        if self.chip:
            out["chip"] = self.chip
            return out
        if self.scale is not None:
            out["scale"] = self.scale
            return out
        if self.cost is not None:
            out["costTotal"] = dict(self.cost)
            return out
        if self.interval is not None:
            out["interval"] = {"low": self.interval["low"], "high": self.interval.get("high", self.interval["low"])}
            return out
        out["optionIds"] = [option_id(token, self.dimension, c) for c in self.codes]
        if self.advantages:
            out["advantageIds"] = [option_id(token, self.dimension, a) for a in self.advantages]
        return out


@dataclass(frozen=True)
class PersonInputs:
    person: str
    link: str
    recency: bool | None
    story: str | None
    anchor_chip: str | None
    picks: list
    pilot_opt_in: bool
    anchoring: str | None
    #: Spec 051 (keel-cloud 103): what this person types on the one follow-up when one is asked of them -- one
    #: composed sentence (`FOLLOW_UP_LINES`), no name, no digit; None presses *Skip this one*.
    follow_up: str | None = None
    #: Spec 064 FR-4 (keel-cloud 120): inside the segment's condition -- the chip answered inside; False is thanked at
    #: the chip and posts `{"outsideSegment": true, "answers": []}`.
    in_segment: bool = True
    #: Spec 064 FR-7: a corpus pick the served options cannot carry, re-expressed (`(dimension, corpus, sent)`) -- a
    #: finding, never a silent drop (Commitment's *yes, after trying it first* where no smaller step is served).
    remapped: tuple = ()

    def response(self, token: str, recall_period: str | None = None) -> dict:
        """The one `POST /v2/i/{token}/interview/response` body; a cost total re-expressed over
        `recall_period`, the period the interview asks it over."""
        answers = [p.asked_over(recall_period).as_wire(token) for p in self.picks]
        if self.link == LINK_B2B:
            return {"answers": answers}
        if not self.in_segment:
            return {"outsideSegment": True, "answers": []}
        if not self.recency:
            return {"recency": False, "answers": []}
        body: dict = {"recency": True, "answers": answers}
        if self.anchor_chip:
            body["anchorChip"] = self.anchor_chip
        elif self.story:
            body["story"] = self.story
        return body


#: keel-cloud `Period`'s days, the one table a cost total is normalised by.
PERIOD_DAYS = {"day": 1.0, "week": 7.0, "month": 30.4375, "quarter": 91.3125, "year": 365.25}


def _pick(entry, key: str, raw) -> Pick:
    if isinstance(raw, dict) and raw.get("chip"):
        chip = str(raw["chip"])
        if chip not in ESCAPES:
            raise VectorsScriptError(f"{entry.id}: {key}'s chip {chip!r} is not an escape at contract 14")
        return Pick(dimension=key, chip=chip.upper())
    if key == "commercial.existing_sacrifice" and entry.chain():
        # spec 064 FR-3 (keel-cloud 115 FR-2): the value box, in the founder's unit and period as the r13 pick is
        if not isinstance(raw, dict):
            raise VectorsScriptError(f"{entry.id}: {key} pick {raw!r} is not a value box")
        if raw.get("nothing"):
            return Pick(dimension=key, chip=VALUE_BOX_CHIPS["nothing"])
        return Pick(dimension=key, interval={"low": raw["low"], "high": raw.get("high", raw["low"])},
                    cost_period=raw.get("period"))
    if key == "commercial.existing_sacrifice":
        if not isinstance(raw, dict):
            raise VectorsScriptError(f"{entry.id}: {key} pick {raw!r} is not a cost total")
        if raw.get("nothing"):
            # D8 (keel-web 064 call 9): "nothing" is the number 0, typed -- as an amount
            return Pick(dimension=key, cost={"mode": "AMOUNT", "value": 0}, cost_period=raw.get("period"))
        return Pick(dimension=key, cost={"mode": raw["mode"], "value": raw["value"]},
                    cost_period=raw.get("period"))
    if key == "solution.relative_advantage":
        return Pick(dimension=key, codes=[raw["answer"]],
                    advantages=[on_the_wire(entry, key, a) for a in raw.get("advantages") or []])
    if key == "problem.frequency":
        return Pick(dimension=key, scale=int(raw))
    if isinstance(raw, list):
        return Pick(dimension=key, codes=[on_the_wire(entry, key, str(c)) for c in raw])
    return Pick(dimension=key, codes=[on_the_wire(entry, key, str(raw))])


# ---------------------------------------------------------------- spec 051: the founder's side of the ladder

def founder_side(entry):
    """The founder's side of the follow-up's walk (keel-cloud 103 `Ladder.Founder.of`, judgement call 2), read off the
    entry's own founder answers -- what the corridor locks: Importance's own item (`own`, the saved list's item 0; none
    when the list is absent), the price's low (none when the founder gave no price), and Buyer and payer's supporting
    answer by the tested item (`decided_alone` when "Nobody else" is tested, else the registry's `had_to_agree`)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415 - the ladder lives there

    importance = entry.founder_list("problem.importance")
    price = (_founder(entry, "commercial.price") or {}).get("answer")
    low = float(price["low"]) if isinstance(price, dict) and price.get("low") is not None else None
    chain = entry.chain()
    if chain:
        # keel-cloud 115 `Ladder.Founder.of`: held to its own rung edge -- the one-off on up front then nothing; free none
        low = None if price.get("shape") == "FREE" else float(
            price["upfrontLow"] if chain_mod.once(price) else price["low"])
    buyer = entry.founder_list("commercial.buyer_payer_alignment")
    supports = None
    if buyer and buyer["items"]:
        tested = entry.tested("commercial.buyer_payer_alignment") or {}
        supports = (fake.BUYER_ALONE,) if tested.get("code") == NOBODY_ELSE[0] else fake.BUYER_SUPPORTS
    return fake.Founder(importance_item=wire_code("problem.importance", 0) if importance and importance["items"]
                        else None, price_low=low, buyer_supports=supports, chain_price=chain)


_THIRD = re.compile(r"\b(they're|they've|they'd|they'll|theirs|their|themselves|they)\b", re.IGNORECASE)
_COULD_NOT_SHAPES = (
    (r"^(?:could|would|can|will) you (?:have been|be) (?:allowed|able|permitted) to (.+)$", r"\1"),
    (r"^you (?:could|would|can|will)(?: have been| be) (?:allowed|able|permitted) to (.+)$", r"\1"),
    (r"^you (?:were|are) (?:allowed|able|permitted) to (.+)$", r"\1"),
    (r"^(?:could|can) you (.+)$", r"\1"),
    (r"^you (?:could|can) (.+)$", r"\1"),
    (r"^(?:would|will) you (.+)$", r"\1"),
    (r"^you (?:would|will) (.+)$", r"\1"),
    (r"^did you (.+)$", r"\1"),
    (r"^you had (.+)$", r"have \1"),
    (r"^(?:were|are) you (.+)$", r"be \1"),
    (r"^you (?:were|are) (.+)$", r"be \1"),
    (r"^(?:was|is) your (\S+) (.+)$", r"have your \1 \2"),
    (r"^your (\S+) (?:was|is) (.+)$", r"have your \1 \2"),
)


def could_not(asked: str | None) -> str | None:
    """keel-cloud 126 `ItemFrames.couldNot`, mirrored: the condition's stranger face as the verb phrase after *You said
    you couldn't* -- the clause lower-cased and shorn of its *?*, every *they* / *their* the stranger's own, then one
    of the thirteen shapes; None where the face is none of them (the composer then says *do that*)."""
    text = (asked or "").strip()
    while text.endswith("?") or text.endswith("."):
        text = text[:-1].strip()
    if not text:
        return None
    text = fake_lower(text) or text

    def person(m):
        w = m.group(1).lower()
        return {"they're": "you're", "they've": "you've", "they'd": "you'd", "they'll": "you'll", "their": "your",
                "theirs": "yours", "themselves": "yourself"}.get(w, "you")
    text = _THIRD.sub(person, text)
    for pattern, out in _COULD_NOT_SHAPES:
        m = re.match(pattern, text)
        if m:
            return m.expand(out).strip()
    return None


def founder_follow_up_words(entry) -> dict[str, str | None]:
    """The founder's words a follow-up's text says (`FollowUpComposer.values`): the tested Compatibility condition and
    Adoption friction effort, each its saved list item's label as the founder wrote it."""
    return {"{condition}": (entry.tested("solution.compatibility") or {}).get("label"),
            "{effort}": (entry.tested("solution.adoption_friction") or {}).get("label")}


#: Spec 051 FR-11: the follow-up lines the corpus people type -- composed here (r11 records none), one sentence, no name
#: and no digit. **Spec 064 FR-7: one line a rung** (judgement call): since keel-cloud 118 the rung a person is asked on
#: depends on the deciding lines of the standings at that moment (read off the served standings at walk time), and
#: since 119 a THEMES job starts at the end of every reading batch over the answers so far -- while the scripted runtime
#: resolves a theme's texts verbatim and refuses one the context does not carry. One line a rung makes every partial
#: context resolve to the one theme of that line, whoever was asked there. (The first of each rung's three spec 051
#: lines is kept; Purchase friction, a rung since 118, gains its own.)
FOLLOW_UP_LINES = {
    "problem.importance": ("The other two land on me every single week, so they come first.",),
    "problem.current_solution_satisfaction": ("A quick check at the end of the day usually catches it.",),
    "solution.compatibility": ("Approval sits with someone else and they are rarely around.",),
    "solution.relative_advantage": ("Fewer emails back and forth would have helped far more.",),
    "solution.adoption_friction": ("Another step on a busy day is one step too many.",),
    "commercial.price": ("Proof that it saves time every month would make it worth more.",),
    "commercial.buyer_payer_alignment": ("My manager had to sign it off and wanted to see the cost.",),
    "commercial.purchase_friction": ("Finance wanted written quotes before anyone signed.",),
    "commercial.commitment": ("A free trial on one small job first.",),
}
#: Spec 051 FR-4: who presses *Skip this one* instead (one a scenario, on a rung others on it type for).
FOLLOW_UP_SKIPS = {"01-countly": ("Lena Fischer",), "05-paidly": ("Viktor Fern",), "07-mulchrun": ("Jamal Washington",)}
#: Spec 051 FR-5: whose story goes through the speak-or-type box, and how -- the take ended by the 4 s quiet ("quiet")
#: or by *Done* ("done"), or the microphone refused ("refused", T6) -- one of each kind a scenario at most.
STORY_SPOKEN = {"01-countly": {"Priya Natarajan": "quiet", "Hana Yoshida": "refused"},
                "05-paidly": {"Nadia Petrova": "done", "Omar Farouk": "refused"},
                "07-mulchrun": {"Travis Buckley": "quiet"}}


def follow_up_lines(entry, people: list) -> dict[str, str | None]:
    """`{person: line}` for every person a follow-up is owed by the harness's walk before anyone answered (registry
    order, no deciding line yet), the skippers' `None`; nobody else is in it. The walk at answer time may ask another
    rung (`follow_up_line` then types that rung's line)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415

    founder = founder_side(entry)
    out: dict[str, str | None] = {}
    for person in people:
        if person.link != LINK_B2B and not person.recency:
            continue
        rung = fake.first_rung(person.picks, founder, person.link, b2b=is_b2b(entry))
        if rung is None:
            continue
        out[person.person] = None if person.person in FOLLOW_UP_SKIPS.get(entry.id, ()) else FOLLOW_UP_LINES[rung][0]
    return out


def follow_up_line(entry, person, owed: dict | None) -> str | None:
    """What `person` types on the follow-up they are actually asked (`owed`, the walk at answer time): None for a
    skipper or where nothing is owed; a back-test person's own words where the file has them; else that rung's line."""
    if not owed or person.person in FOLLOW_UP_SKIPS.get(entry.id, ()):
        return None
    own = next((p.follow_up for p in entry.people() if p.person == person.person and getattr(p, "follow_up", None)),
               None)
    return own or FOLLOW_UP_LINES[owed["dimension"]][0]


def follow_up_question(entry, picks: list, link: str, interview: dict, token: str, first=()) -> dict | None:
    """Spec 051 FR-2 / judgement call 1: the one follow-up the cloud owes these picks on this link -- the stem by the
    harness's own walk (spec 064 FR-7, keel-cloud 118: the deciding lines `first` taken first, an answer a second stem
    is asked on owed too) and its text filled the way `FollowUpComposer` fills it, from the served labels (`interview`,
    the person's own link) and the founder's own words -- or None. The walk holds the route's answer and the screen to
    it."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415

    served = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    stem = fake.first_stem(picks, founder_side(entry), link, b2b=is_b2b(entry), served=set(served), first=first)
    if stem is None:
        return None
    rung, also = stem
    item = served.get(rung) or {}
    labels = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
    label = lambda code: labels.get(option_id(token, rung, code))  # noqa: E731
    pick = next((p for p in picks if p.dimension == rung), None)
    codes = list(pick.codes) if pick else []
    values: dict[str, str | None] = {"{occasion}": interview.get("occasion")}
    if also:
        step = smaller_step(entry)
        values["{smaller_step}"] = the_step(step) if step else None
    elif rung == "problem.importance":
        values["{their_picks}"] = fake.joined([label(c) for c in codes], "and")
        values["{founder_item}"] = fake.lower(label(founder_side(entry).importance_item))
    elif rung == "problem.current_solution_satisfaction":
        values["{their_answer}"] = fake.lower(label(codes[0]) if codes else None)
    elif rung == "solution.compatibility":
        # keel-cloud 126 (FR-5b, `ItemFrames.couldNot`): "You said you couldn't {condition}" -- the tested item's
        # stranger face (`asked`, else its label) as the verb phrase after "couldn't"; "always ..." where they read
        # Only sometimes (123 FR-8), "... without help or approval" where they read Only with help or approval; the
        # composer's "do that" where the face has none of the shapes
        tested = entry.tested("solution.compatibility") or {}
        condition = could_not(tested.get("asked") or tested.get("label"))
        picked = (label(codes[0]) or "").lower() if codes else ""
        if condition is not None and codes and codes[0] == "only_with_help":
            condition = "always " + condition if picked.startswith("only sometimes") \
                else condition + " without help or approval"
        values["{condition}"] = condition
        values["{would}"] = ("only work sometimes" if picked.startswith("only sometimes")
                             else "only work with help" if picked.startswith("only with help") else "not work")
    elif rung == "solution.relative_advantage":
        values["{benefit}"] = fake.joined([a.get("label") for a in item.get("advantages") or []], "or")
    elif rung == "solution.adoption_friction":
        values["{effort}"] = fake.lower(founder_follow_up_words(entry)["{effort}"])
    elif rung == "commercial.price":
        values["{band}"] = fake.WOULD_NOT_PAY_BAND if codes[:1] == [fake.WOULD_NOT_PAY] else \
            fake.lower(label(codes[0]) if codes else None)
    return {"dimension": rung, "text": fake.fill(rung, values, also=also), "spoken": fake.spoken_of(rung, also=also),
            "also": also}


def the_step(step: str) -> str:
    """keel-cloud 118 `ItemFrames.theStep`: *the free trial* for *a free trial*; a step with its own article kept."""
    low = step.lower()
    if low.startswith("a "):
        return "the " + step[2:]
    if low.startswith("an "):
        return "the " + step[3:]
    return step if low.startswith(("the ", "your ", "their ", "my ")) else "the " + step


def with_pick(person: "PersonInputs", dimension: str, codes: list[str]) -> "PersonInputs":
    """`person` with one pick's codes replaced (spec 051: the AI link's person made owed a follow-up)."""
    import dataclasses                                                 # noqa: PLC0415

    picks = [dataclasses.replace(p, codes=list(codes)) if p.dimension == dimension else p for p in person.picks]
    return dataclasses.replace(person, picks=picks)


#: keel-cloud 118 FR-1: the conditional yes is served only where the founder's Commitment list carries a smaller step.
CONDITIONAL_YES = "yes_after_trying"
NOT_SERVED_YES = "probably_not"


def smaller_step(entry) -> str | None:
    """keel-cloud 118 `ItemFrames.smallerStep`: the Commitment list's second item, lower-cased, or None (none served)."""
    saved = entry.founder_list("commercial.commitment")
    items = (saved or {}).get("items") or []
    label = items[1].get("label") if len(items) > 1 else None
    return fake_lower(label) if label and label.strip() else None


def fake_lower(label: str | None) -> str | None:
    if label is None:
        return None
    label = label.strip()
    return label if len(label) > 1 and label[1].isupper() else label[:1].lower() + label[1:]


def _served_commitment(entry, picks: list) -> tuple[list, tuple]:
    """Spec 064 FR-7 (keel-cloud 118 FR-1): Commitment's options are written from the founder's step -- *Yes, I'd
    {step}*, *Yes, after {smaller step} first* (`conditional: true`) only where the list carries a smaller step, then
    *Probably not*, *No*. A corpus `yes_after_trying` rides on the served conditional option where one is served, and
    on *probably not* where none is: the remap is returned, so the journey names it (a finding, not a silent drop)."""
    if smaller_step(entry) is not None:
        return picks, ()
    # corpus revision 14 (keel-cloud 127, rule T): a yes_after_trying answer exists only where the founder's list
    # carries a smaller step -- the remap to probably_not (spec 064 FR-7) is retired; an entry that still asks for it
    # is refused, never quietly re-read
    unserved = [pick for pick in picks if pick.dimension == "commercial.commitment" and pick.codes == [CONDITIONAL_YES]]
    if not unserved:
        return picks, ()
    if not entry.backtest:
        raise VectorsScriptError(f"{entry.id}: a yes_after_trying answer on commercial.commitment, but the founder's list "
                                 "carries no smaller step (keel-cloud 118 FR-1 serves no second yes; corpus revision 14 "
                                 "rule T)")
    # a back-test entry runs on Keel's AI, which may draft the smaller step itself (118 FR-1): the pick rides on
    # *probably not* for the script and goes back onto the served conditional option where one is served
    # (`corpus_scenario._served_options`), every remap left standing named as a finding
    import dataclasses                                                 # noqa: PLC0415
    out, remapped = [], []
    for pick in picks:
        if pick.dimension == "commercial.commitment" and pick.codes == [CONDITIONAL_YES]:
            out.append(dataclasses.replace(pick, codes=[NOT_SERVED_YES]))
            remapped.append(("commercial.commitment", CONDITIONAL_YES, NOT_SERVED_YES))
        else:
            out.append(pick)
    return out, tuple(remapped)


def person_inputs(entry) -> list[PersonInputs]:
    people = []
    for person in entry.people():
        asked = set(plan_keys(entry, 1, person.link) + plan_keys(entry, 2, person.link)
                    + plan_keys(entry, 3, person.link)) if person.link == LINK_PRIMARY else \
            set(plan_keys(entry, 3, LINK_B2B))
        if person.link == LINK_PRIMARY and is_b2b(entry):
            asked -= set(plan_keys(entry, 3, LINK_PRIMARY))
        asked.discard("problem.prevalence")
        picks = [_pick(entry, key, raw) for key, raw in (person.picks or {}).items() if key in asked]
        picks, remapped = _served_commitment(entry, picks)
        people.append(PersonInputs(
            person=person.person, link=person.link,
            recency=None if person.link == LINK_B2B or not person.in_segment else person.recency == "yes",
            story=person.story, anchor_chip=STORY_CHIPS.get(person.chip) if person.chip else None,
            picks=picks if person.in_segment else [], pilot_opt_in=person.pilot_opt_in and person.in_segment,
            anchoring=person.anchoring, in_segment=person.in_segment, remapped=remapped))
    import dataclasses                                                 # noqa: PLC0415

    lines = follow_up_lines(entry, people)
    # spec 062 follow-up (2026-10-22): a back-test person who is owed a follow-up answers in their own words
    # (`Person.follow_up` in the file) where the file has them; the pooled line otherwise, as every golden entry does
    own = {p.person: p.follow_up for p in entry.people() if getattr(p, "follow_up", None)}
    return [dataclasses.replace(p, follow_up=(own.get(p.person) if p.person in lines and own.get(p.person)
                                              else lines.get(p.person))) for p in people]


def people_to_invite(entry, count: int) -> tuple[list[PersonInputs], list[str]]:
    """S-012's people: the first `count` of the entry's people, in corpus order, whose answer a
    reading can be taken from -- a gate yes with a story typed -- and on a B2B entry the first `count`
    decision-makers beside them. Anyone passed over on the way is named, never silently replaced
    (a bundle that quietly measured a different person is worse than one that measured nobody)."""
    readable = {p.person for p in readable_people(entry)}
    chosen, skipped, deciders = [], [], []
    for person in person_inputs(entry):
        if person.link == LINK_B2B:
            if len(deciders) < count:
                deciders.append(person)
            continue
        if len(chosen) == count:
            continue
        if person.person in readable:
            chosen.append(person)
        else:
            skipped.append(person.person)
    return chosen + deciders, skipped


def inputs_json(entry, founder: FounderInputs, people: list[PersonInputs]) -> dict:
    return {"_entry_id": entry.id,
            "founder": {**asdict(founder),
                        "calibration": {v: [{**a.as_wire(), **({"_answer": a.text} if a.text else {})}
                                            for a in answers]
                                        for v, answers in founder.calibration.items()}},
            "people": [asdict(p) for p in people],
            "composed": list(COMPOSED)}


# ------------------------------------------------------------------------------------------- main

def _main(argv: list[str]) -> int:
    from stack.config import load_config

    if not argv:
        print(__doc__)
        return 2
    config = load_config(validate=False)
    _, entry = entry_for(config.keel_cloud, argv[0])
    print(json.dumps(generate(entry).to_json(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - a developer's five-minute check
    import sys

    raise SystemExit(_main(sys.argv[1:]))
