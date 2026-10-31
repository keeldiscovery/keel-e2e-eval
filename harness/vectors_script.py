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

from harness import interview_charge
from harness import loss_line as ll
from harness import qualifiers
from instructions import chain as chain_mod
from instructions import corpus as corpus_reader
from instructions.registry import (COMMITMENT_KEY, FREQUENCY_MIN, IMPORTANCE_CONTROL, NOTHING_ELSE_CHIP,
                                   NOTHING_ELSE_LABEL, ONE_MORE)

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

    keel-cloud counts Frequency in the window's own unit, on an axis from 1 to the window's count (spec 089 FR-2,
    keel-cloud 158: the respondent's `segmented_1_to_n` runs 1..count, a number box from 1; a 0 after the yes is
    SHAPE_MISMATCH, and the five recorded 0s are sent as 1, `ZERO_SENT_AS_ONE`, spec 090 FR-3). The corpus keeps
    Frequency on the founder's
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


#: keel-cloud 088 `E4` (measured since keel-cloud 160 on `frequencyMeasured`, the frame below): framed, the gate ("In the
#: last 3 months, did you ...?") and the Frequency question
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
    """keel-cloud `WindowFrame.frequencyMeasured(window, event)` (160 judgement call 2): the Frequency question E4
    measures a gate's clause on -- *On how many of those {n} {unit} did you {event}?*, the frame before 160, kept so no
    gate moves. What is served is `frequency_served` (window first), held by `frequency_held`."""
    return f"On how many of those {window_words(window)} did you {event}?"


def counted_in(window: Window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.countedIn`, spec 115 FR-2): *on* a day or a night, *in* a week or a month."""
    return "in" if window.unit in ("WEEKS", "MONTHS") else "on"


def short_unit(window: Window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.shortUnit`): the unit's plural, its last word alone where it has two (*working
    days*: *days*) -- said once in full in the window, once more short."""
    return _UNIT_WORDS[window.unit][1].split(" ")[-1]


def window_first(window: Window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.windowFirst`): the Frequency frames' opening -- *In the last 3 months, in how many
    months *, *In the last 5 working days, on how many days * -- the unit always said, as it is counted."""
    return f"In the last {window_words(window)}, {counted_in(window)} how many {short_unit(window)} "


def frequency_served(window: Window, event: str | None) -> str:
    """keel-cloud 160 FR-2 (`WindowFrame.frequencyRespondent(window, event)`): the window first and plainly, then the
    gate's one event -- *In the last 7 nights, on how many nights did you have to work out why your baby was crying?*;
    with no clause *In the last 7 nights, on how many nights did that happen?*. Since keel-cloud 174 FR-5 (spec 115
    FR-2) the opening is `window_first`'s: *in how many* weeks and months, a two-word unit short the second time."""
    lead = f"{window_first(window)}did "
    return f"{lead}{subject_led(event)}?" if (event or "").strip() else f"{lead}that happen?"


def frequency_served_before174(window: Window, event: str | None) -> str:
    """keel-cloud 174 (`WindowFrame.frequencyRespondentBefore174`): the frame as it read from 160 to 173 -- *on how many
    {the unit in full}* whatever the unit -- read on a stored item, never served for a new one."""
    lead = f"In the last {window_words(window)}, on how many {_UNIT_WORDS[window.unit][1]} did "
    return f"{lead}{subject_led(event)}?" if (event or "").strip() else f"{lead}that happen?"


def frequency_unit_dropped(window: Window, event: str | None) -> str | None:
    """keel-cloud 174 FR-5 (`WindowFrame.unitDropped`): what 160's held frame served past the cap from 160 to 173, the
    unit dropped -- *In the last 3 months, on how many did you ...?* -- read on a stored item so it is never served
    again (`frequency_held` no longer writes it); None with no clause."""
    return f"In the last {window_words(window)}, on how many did {subject_led(event)}?" if (event or "").strip() \
        else None


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
    # spec 077 FR-1 (keel-cloud 146 FR-1): the condition keel-cloud draws on the confirm from the founder's WHICH PEOPLE
    # (*in the Dallas-Fort Worth suburbs*, a place that is not the market's country) -- the fake writes none (`DRAWN`)
    "07-mulchrun": ("landscaping crew leads in the Dallas-Fort Worth suburbs, spring season",
                    "are based in the Dallas-Fort Worth suburbs", "Are you based in the Dallas-Fort Worth suburbs?",
                    "YES"),
}

#: Spec 077 FR-1 (keel-cloud 145 FR-4a, 146 FR-1): the `SEGMENTS` rows whose condition is **code's**, drawn on the
#: confirm from the founder's WHICH PEOPLE -- the scripted CONTEXT_INTERPRET writes the core alone (`scripted_segment`),
#: the confirmed context carries the condition (`segment_of`), and the part-1 job, handed it, writes the chip.
DRAWN = frozenset({"07-mulchrun"})


def segment_of(entry) -> dict:
    """`{core, condition}` as the confirmed context stores it (keel-cloud 120 FR-2): the entry's own segment as the core
    with no condition where `SEGMENTS` names none. Since spec 077 the condition of a `DRAWN` row is code's, drawn on the
    confirm (keel-cloud 146 FR-1); every other row's is the model's, kept (145 judgement call 5)."""
    if entry.id in SEGMENTS:
        core, condition, _, _ = SEGMENTS[entry.id]
        return {"core": core, "condition": condition}
    return {"core": _ctx(entry)["segment"], "condition": None}


def scripted_segment(entry) -> dict:
    """`{core, condition}` as the scripted CONTEXT_INTERPRET writes it: `segment_of`, but the core alone on a `DRAWN`
    row (spec 077 FR-1: 07-mulchrun's condition is code's, never the fake's)."""
    seg = segment_of(entry)
    return {"core": seg["core"], "condition": None} if entry.id in DRAWN else seg


def card_condition(entry) -> str | None:
    """The condition the context card draws before the confirm (*Only people who: ...*, keel-web 096): since keel-cloud
    148 FR-1 (spec 084) the settled one (`segment_of`) -- code's drawn condition on a `DRAWN` row, the scripted one
    elsewhere -- never the result's as written."""
    return segment_of(entry)["condition"]


def segment_line(entry) -> str:
    """`ContextSlots.segmentLine()` (keel-cloud 120, 146 FR-2): the core, then *, who {condition}* unless the core
    already says the condition -- what the brief's header and every job read."""
    seg = segment_of(entry)
    return qualifiers.segment_line(seg["core"], seg["condition"])


def chip_of(entry) -> dict | None:
    """The gate's segment chip the scripted part-1 job writes (`condition: {question, inside}`), or None."""
    if entry.id not in SEGMENTS:
        return None
    _, _, question, inside = SEGMENTS[entry.id]
    return {"question": question, "inside": inside}


def decider_chip(condition: str | None, actor_plural: str | None) -> str | None:
    """keel-cloud 145 FR-4b / 146 FR-3 (`RespondentQuestionsRules.deciderChip`, mirrored): the decision-maker's screener
    -- the condition in the third person about the people they decide for, named once (`decider_people`): (*Do the
    payroll practitioners you decide for run
    payroll for at least 50 employees?*, *Are the ... you decide for past the beginner stage?*); a condition about the
    organisation itself asked as it is (*work at a company with at least 50 employees* -> *Does your company have at
    least 50 employees?*; any other *work at / for ...* as part 1's chip, *Do you work at ...?*); held to the spoken cap
    (20 words), None where it does not fit. Part 3 is code's at the lock, so this is what the link serves."""
    if not condition or not condition.strip():
        return None
    text = _condition_clause(condition)
    org = re.match(r"(?i)^works?\s+at\s+(?:an?\s+)?(.+?)\s+with\s+(.+)$", text)
    be = re.match(r"(?i)^(?:are|is|am)\s+(.+)$", text)
    if org:
        asked = f"Does your {org.group(1).strip()} have {org.group(2).strip()}?"
    elif re.match(r"(?i)^works?\s+(?:at|for)\b", text):
        asked = f"Are you {be.group(1)}?" if be else f"Do you {text}?"
    else:
        people = decider_people(text, actor_plural)
        asked = f"Are the {people} you decide for {be.group(1)}?" if be else f"Do the {people} you decide for {text}?"
    return asked if _words(asked) <= STEM_MAX_WORDS else None


def _condition_clause(condition: str) -> str:
    """keel-cloud `WindowFrame.clause` as the chips read the condition: runs of space as one, no closing full stop, a
    leading capital lowered (not an acronym's)."""
    text = " ".join(condition.split())
    while text.endswith("."):
        text = text[:-1].strip()
    if len(text) > 1 and text[0].isupper() and not text[1].isupper():
        text = text[0].lower() + text[1:]
    return text


def chip_from(condition: str | None) -> str | None:
    """keel-cloud 131 FR-6 / 166 FR-1 (`RespondentQuestionsRules.chipFrom`, mirrored): the condition said to the person
    in the second person -- *are past the beginner stage* -> *Are you past the beginner stage?*, *run one or two sites*
    -> *Do you run one or two sites?* -- held to the spoken cap (20 words), None where it does not fit. Spec 100: what
    the money study's person link serves as `Interview.condition` (part 3 is code's at the lock, so code asks it)."""
    if not condition or not condition.strip():
        return None
    text = _condition_clause(condition)
    be = re.match(r"(?i)^(?:are|is|am)\s+(.+)$", text)
    asked = f"Are you {be.group(1)}?" if be else f"Do you {text}?"
    return asked if _words(asked) <= STEM_MAX_WORDS else None


def money_condition(entry) -> dict | None:
    """Spec 100 (keel-cloud 166 FR-1, keel-web 145 FR-1; contract 49 `Interview.condition`): what the person's link of a
    money-only consumer study serves at the top level -- kind FULL, no gate, the screener before the idea:
    `{question, inCodes: [YES]}` from the confirmed context's condition (`chip_from`); None where the context carries
    none (or it does not fit 20 words: E7), under any scope that serves the gate (its chip rides on `gate.condition`),
    and on a B2B entry (money alone gives the person no link there; the decision-maker's is `decider_condition`)."""
    if serves_gate(entry) or is_b2b(entry):
        return None
    question = chip_from(segment_of(entry)["condition"])
    return {"question": question, "inCodes": ["YES"]} if question else None


def decider_people(clause: str, actor_plural: str | None) -> str:
    """keel-cloud 146 FR-3 (`RespondentQuestionsRules.deciderPeople`, DRIFT #99 closed), mirrored: the people named
    once before *you decide for* -- `actor_plural`'s head where its qualifier can be cut (*payroll practitioners who run
    payroll ...* -> *payroll practitioners*; *landscaping crew leads in the Dallas suburbs* -> *landscaping crew
    leads*), `actor_plural` whole where it carries none, *people* where the clause says what it says (*freelance
    translators working for agencies* + *work mostly for agencies*) or none is handed."""
    if actor_plural is None or not actor_plural.strip():
        return "people"
    cut = qualifiers.head(actor_plural)
    if cut is not None:
        return cut
    return "people" if qualifiers.says(actor_plural, clause) else actor_plural.strip()


def decider_condition(entry) -> dict | None:
    """Spec 076 FR-4 (keel-cloud 145 FR-4b, contract 43 `Interview.condition`): what the decision-maker's link serves
    on a SOMEONE_ELSE study whose context carries a condition -- `{question, inCodes}`, before the idea; None on a
    study with no condition (or no decision-maker's link)."""
    if not is_b2b(entry):
        return None
    question = decider_chip(segment_of(entry)["condition"], _ctx(entry).get("actor_plural"))
    return {"question": question, "inCodes": ["YES"]} if question else None


def _phrase(text) -> str:
    return qualifiers.phrase(text)


def _upper_first(text: str) -> str:
    return text[:1].upper() + text[1:]


def sentence(segment_core, condition, circumstance, job, window: "Window | None") -> str | None:
    """keel-cloud `ReadBack.sentence(core, condition, circumstance, job, window)`, since keel-cloud 149 FR-2 two
    sentences, so the job has a verb before it and the founder reads it once, and since keel-cloud 168 the window a
    third sentence of its own: *"<Segment>. When <when>, they want to <what>. We'll ask about the last <window>."* --
    the segment whole as `qualifiers.segment` says it (the condition after *, who*, or *and* where the core has its
    own *who*, a condition's own *whose* / *that* / *which* kept (148 FR-2), and since 146 FR-2 not at all where the
    core already says it), a capital and a full stop; then the circumstance after
    *when* said once (146 FR-4, `qualifiers.with_when`), its first letter raised (*While running payroll, ...*), a comma
    and the job on the people's verb (`qualifiers.they`: *they want to {job}*, *they {job}* where it opens with *want
    to*, *need to*, *try to*, *have to* or *must*, *they are trying to ...* on *trying to*) and a full stop; then *We'll
    ask about the last {window}.* as its own sentence (168: never *, counting ...* on the job), or nothing where the
    window is None (spec 135's scope rule, as `read_back` hands it: the two sentences as before, byte for byte); None
    where the segment, the circumstance or the job is missing."""
    segment, when, what = _phrase(segment_core), _phrase(circumstance), _phrase(job)
    if not (segment and when and what):
        return None
    said = qualifiers.segment(segment, condition)
    out = f"{_upper_first(said)}. {_upper_first(qualifiers.with_when(when))}, {qualifiers.they(what)}"
    return out + "." + (f" We'll ask about the last {window_words(window)}." if window else "")


#: keel-web 147 FR-1 `readBackSaysWindow` (`lib/contextReach.ts`, web master `d6dc5a9`): the served sentence ends with
#: keel-cloud 168's window sentence, *We'll ask about the last
#: {window}.* -- straight or curly apostrophe, after a space or at the start, the sentence trimmed.
READ_BACK_SAYS_WINDOW = re.compile(r"(?:^|\s)We['\u2019]ll ask about the last [^.]+\.$")


def read_back_says_window(understands: str | None) -> bool:
    """keel-web 147 `readBackSaysWindow`: True where the served sentence already says its window (keel-cloud 168), so
    the card's muted *Counting the last {window}.* line would say it twice; False for a sentence with no window."""
    return bool(READ_BACK_SAYS_WINDOW.search((understands or "").strip()))


def read_back(entry, *, window=True, confirmed: bool = False) -> str | None:
    """keel-cloud 122 `ReadBack.sentence` over the scripted slots -- what the context card serves since 122; never the
    model's line. The card's is read off the result (`scripted_segment`); `confirmed` reads the stored context's
    (`segment_of`: on a `DRAWN` row the condition code drew) -- since keel-cloud 146 FR-2 the two are the same sentence
    wherever the core already says the drawn qualifier (07-mulchrun)."""
    seg = segment_of(entry) if confirmed else scripted_segment(entry)
    # keel-cloud `ReadBack`: the window's sentence (168) is left out where the founder set none (spec 071: money
    # alone asks no window, keel-web 109 FR-3) -- and, since keel-cloud 135, wherever the scope serves no gate, whatever
    # window is stored (spec 072 FR-2, DRIFT #96 closed)
    if window is True:
        window = window_of(entry)
    return sentence(seg["core"], seg["condition"], _ctx(entry).get("circumstance"), _ctx(entry).get("job"),
                    window or None)


def context_result(entry) -> dict:
    """CONTEXT_INTERPRET's result (screen response contract 23): the slots, `segment` as `{core, condition}` (keel-cloud
    120), the plain occasion noun, `window.proposed` null; no `understands` -- the sentence is code's since 122."""
    ctx = _ctx(entry)
    return {"actor": ctx["actor"], "actor_plural": ctx["actor_plural"], "job": ctx["job"],
            "circumstance": ctx["circumstance"], "segment": scripted_segment(entry), "occasion": occasion(entry),
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


#: keel-cloud 173 `ScaleFour.FRAME`: Relative advantage's tail after the idea's name, the occasion inside it (spec 173
#: FR-2: the occasion never leaves the stranger's question), filled by `benefit_frame` as `OccasionNoun.fill` fills it.
BENEFIT_FRAME = "have made your last {occasion} go better for you, or not?"
#: keel-cloud `ScaleFour.FRAME_159`: spec 159 to 172's tail, what an item stored before 173 carries after its *On your
#: last {occasion}, would {name}* -- served as stored (`served_benefit_question`), never rewritten into 173's words.
BENEFIT_FRAME_159 = "have made it go better for you, or not?"
#: keel-cloud `ScaleFour.OLD_FRAME`: spec 091 to 158's tail, which an item stored before contract 47 carries.
BENEFIT_FRAME_085 = "have made things better, or not?"
#: keel-cloud 173 `SpokenCap.PLAIN[SOLUTION_RELATIVE_ADVANTAGE]`: the plain frame of an item stored before 173.
BENEFIT_PLAIN_159 = f"Would it {BENEFIT_FRAME_159}"


def fill_occasion(template: str, noun: str | None) -> str:
    """keel-cloud `OccasionNoun.fill` (spec 129 FR-8): a template's `{occasion}` filled with the context's own noun; with
    none (blank, the placeholder *time*) *your last {occasion}* reads *the last time*, never *your last time*."""
    own = (noun or "").strip()
    if own and own.lower() not in ("time", "times"):
        return template.replace("{occasion}", own)
    return (template.replace("on their last {occasion}", "the last time").replace("on your last {occasion}", "the last time")
            .replace("their last {occasion}", "the last time").replace("your last {occasion}", "the last time")
            .replace("that last {occasion}", "that time").replace("last {occasion}", "last time")
            .replace("{occasion}", "time"))


def benefit_frame(occasion_word: str | None) -> str:
    """keel-cloud 173 `ScaleFour.frame`: `BENEFIT_FRAME` with the occasion in -- the context's own noun, else *the last
    time*."""
    return fill_occasion(BENEFIT_FRAME, occasion_word)


def benefit_shortened(occasion_word: str | None) -> str:
    """keel-cloud 173 `ScaleFour.shortened`: the question over the cap -- the idea said *it*, the occasion kept (the
    frame is eleven words and an occasion at most eight, so it always fits)."""
    return f"Would it {benefit_frame(occasion_word)}"


def benefit_question(occasion_word: str, name: str) -> str:
    """keel-cloud 173 `ScaleFour.question` (spec 173 FR-2; 159 FR-1, 091 FR-E before it): Relative advantage's stem around
    the idea's current name -- *Would {name} have made your last {occasion} go better for you, or not?* (*... the last
    time ...* with no noun, *the idea* with no name), or, past the 20-word spoken cap, *Would it have made your last
    {occasion} go better for you, or not?* -- the idea's noun shortened, never the occasion dropped (159's plain frame
    *Would {name} have made it go better ...* is gone)."""
    idea = (name or "").strip() or "the idea"
    asked = f"Would {idea} {benefit_frame(occasion_word)}"
    return asked if _words(asked) <= STEM_MAX_WORDS else benefit_shortened(occasion_word)


def benefit_question_159(occasion_word: str, name: str) -> str:
    """Spec 159 to 172's composition (`ScaleFour.question` before 173), kept to read an item stored before 173: *On your
    last {occasion}, would {name} have made it go better for you, or not?*, past 20 words *Would {name} have made it go
    better for you, or not?*. Never what a project locked since 173 is served."""
    idea = (name or "").strip() or "the idea"
    asked = f"On your last {(occasion_word or '').strip() or 'time'}, would {idea} {BENEFIT_FRAME_159}"
    return asked if _words(asked) <= STEM_MAX_WORDS else f"Would {idea} {BENEFIT_FRAME_159}"


_OCCASIONED = re.compile(r"^Would (.+?) have made ((?:your last .+?)|(?:the last time)) go better for you, or not\?$")


def benefit_held_with_its_occasion(stem: str | None) -> str | None:
    """keel-cloud 173 `ScaleFour.heldWithItsOccasion`: a stem in 173's words past the cap (or failing the stranger's
    grammar) at serving says the idea *it* and keeps the occasion as stored; None for any other stem (an item stored
    before 173 falls to its plain frame, `BENEFIT_PLAIN_159`, as it did)."""
    if stem is None:
        return None
    m = _OCCASIONED.match(stem.strip())
    return f"Would it have made {m.group(2)} go better for you, or not?" if m else None


def benefit_frame_of(question: str | None) -> str | None:
    """Which composition a served Relative advantage question is in: `"173"` (the occasion inside, *Would ... have made
    your last / the last time go better ...*), `"159"` (*... have made it go better ...*, an item stored before 173),
    `"085"` (*... made things better ...*, before contract 47), else None. A spec-120 anchor before it is read past."""
    text = (question or "").strip()
    at = text.find(". ")
    if at > 0 and text.startswith("Think "):
        text = text[at + 2:].strip()
    if _OCCASIONED.match(text):
        return "173"
    if text.endswith(BENEFIT_FRAME_159):
        return "159"
    if text.endswith(BENEFIT_FRAME_085):
        return "085"
    return None


def served_benefit_question(stored: str | None, name: str | None = None) -> str | None:
    """keel-cloud 173 `SpokenCap.held`'s Relative advantage step (with 159's `ScaleFour.goBetter`): the question a stored
    item is served with. 085's *made things better* is served in 159's words; a 173 stem past the cap is
    `benefit_held_with_its_occasion`'s; an item stored before 173 past the cap falls to 159's plain frame, the idea's
    `name` where it is known and fits (`SpokenCap.plain`), else `BENEFIT_PLAIN_159`. Every other stem -- 159's within the
    cap, 173's within it -- is served as stored: a locked project keeps its question and its clips (spec 173 T006). The
    grammar check beside the cap (`StrangerGrammar`) is not mirrored, as before 173."""
    if stored is None or not stored.strip():
        return stored
    text = stored.replace(BENEFIT_FRAME_085, BENEFIT_FRAME_159).strip()
    anchor, stem = None, text
    at = text.find(". ")
    if at > 0 and text.startswith("Think "):
        anchor, stem = text[:at + 1], text[at + 2:].strip()
    if _words(stem) > STEM_MAX_WORDS:
        plain = f"Would {name.strip()} {BENEFIT_FRAME_159}" if (name or "").strip() else None
        kept = benefit_held_with_its_occasion(stem) or plain
        stem = kept if kept and _words(kept) <= STEM_MAX_WORDS else BENEFIT_PLAIN_159
    return stem if anchor is None else f"{anchor} {stem}"


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


def expected_j1(entry, audience_words=()) -> list[str]:
    """Spec 064 FR-5b (keel-cloud 121): the J1 notes the scripted idea's how and belief draw, the words, in order (the
    idea's `notes[].word`) -- less, since spec 107 (keel-cloud 175 `Vocabulary.jargon(text, exempt, founderTexts)`),
    every word typed in the founder's own texts (`corpus.founder_texts`: the context's typed fields, the two seeds, the
    audience words; `corpus.typed_in`: whole, case aside, a hyphen joins). 05-paidly's scripted how says *platform* and
    so does its own solution seed (*A platform that pays the translator ...*), so it draws none."""
    lines = idea_lines(entry)
    typed = corpus_reader.founder_texts(entry, audience_words)
    exempt = {str(w).strip().lower() for w in audience_words or () if w}
    how = jargon(lines["how"])
    words = how + [w for w in jargon(lines["belief"]) if w not in how]
    return [w for w in words if w.lower() not in exempt and not corpus_reader.typed_in(w, typed)]


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


# ------------------------------------------------------------------------- spec 071: the study's scope

#: keel-cloud 133 FR-1 `StudyScope.vectors()`.
SCOPE_VECTORS = {"PROBLEM": ("PROBLEM",), "SOLUTION": ("SOLUTION",), "SOLUTION_COMMERCIAL": ("SOLUTION", "COMMERCIAL"),
                 "COMMERCIAL": ("COMMERCIAL",), "ALL": VECTORS}
#: keel-cloud 133 FR-7: the Overview's headline question per scope (`StandingsView.question`).
SCOPE_QUESTION = {"PROBLEM": "Should you build it?", "SOLUTION": "Does it fit?",
                  "SOLUTION_COMMERCIAL": "Does it fit, and will they pay?", "COMMERCIAL": "Will they pay?",
                  "ALL": "Should you build it?"}
PART_VECTOR = {1: "PROBLEM", 2: "SOLUTION", 3: "COMMERCIAL"}


def scope_of(entry) -> str:
    return getattr(entry, "scope", None) or "ALL"


def scope_vectors(entry) -> tuple:
    """The vectors the entry's scope tests, in the ship's order (keel-cloud 133 FR-1)."""
    return SCOPE_VECTORS[scope_of(entry)]


def serves_gate(entry) -> bool:
    """keel-cloud 133 FR-4: the gate (and the recall window, its clock) wherever the problem or the solution is in scope
    -- counted with the problem, the anchor alone in the solution studies; money alone has none."""
    vectors = scope_vectors(entry)
    return "PROBLEM" in vectors or "SOLUTION" in vectors


def gate_counts(entry) -> bool:
    """keel-cloud 133 FR-5: the gate feeds Prevalence only where the problem is in scope (`GateItem.counts`)."""
    return "PROBLEM" in scope_vectors(entry)


def serves_part(entry, part: int, link: str) -> bool:
    """keel-cloud 133 FR-4: whether `part` is served on `link` under the entry's scope. Part 1 on the primary link
    wherever the gate is (the gate alone in the solution studies); part 2 with the solution; part 3 with the money --
    on the decision-maker's link on a B2B persona, on the one link otherwise (never on the primary link of a B2B study,
    as under ALL)."""
    if scope_of(entry) == "ALL":
        return True                             # exactly today: `plan_keys` decides every part as it always has
    vectors = scope_vectors(entry)
    if link == LINK_B2B:
        return part == 3 and "COMMERCIAL" in vectors
    if part == 1:
        return serves_gate(entry)
    if part == 3 and is_b2b(entry):
        return False
    return PART_VECTOR[part] in vectors


def chained_out_of_scope(entry) -> tuple:
    """Spec 072 FR-3: names nothing. runs/DRIFT.md #97 (spec 071) is closed by keel-cloud 134 FR-2: `ScreenChain` chains
    a vector's CALIBRATION_QUESTIONS only where `project.scope().vectors()` holds it, so no study writes a slice for a
    vector it does not calibrate -- and the script carries none."""
    return ()


def primary_link(entry) -> bool:
    """keel-cloud 133 `StudyScope.primaryLink(b2b)`: no link to the person with the problem on B2B money alone."""
    return not (scope_of(entry) == "COMMERCIAL" and is_b2b(entry))


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
#: keel-cloud 115's value box: *None* (the number 0, counted), *I can't recall* (the escape, apart), *I'd rather not
#: say* (apart, a consumer link) -- sent as `chip`. The labels were *Nothing* and *I don't know* until keel-cloud 170
#: (spec 110 FR-3, `CommercialChain.NOTHING_LABEL` / `DONT_KNOW_LABEL`); the codes did not move.
VALUE_BOX_CHIPS = {"nothing": "NOTHING", "dont_know": "DONT_KNOW", "rather_not_say": "RATHER_NOT_SAY"}
VALUE_BOX_LABELS = {"NOTHING": "None", "DONT_KNOW": "I can't recall", "RATHER_NOT_SAY": "I'd rather not say"}


def value_box_escapes(consumer: bool) -> list[str]:
    """`CommercialChain.valueBoxEscapes`: the chips recorded apart, as served codes -- *I can't recall*, and *I'd rather
    not say* on a consumer link."""
    return ["DONT_KNOW", "RATHER_NOT_SAY"] if consumer else ["DONT_KNOW"]


# ------------------------------------------------------- the stranger's cost item (keel-cloud 170 FR-5, mirrored)
# `CommercialChain.costQuestion` (the chain branch the lock stores), `strangerCostLabel`, `valueBoxAnswerLine`, over
# `harness.loss_line`'s `LossLine` (spec 110 FR-3). A cost is the founder's chain answer as the corpus and the wire carry
# it: `mode`, `measure`, `base`, `unit`, `period`, `lossPhrase`.

_COST_OPENERS = {"day": "Yesterday", "week": "Last week", "month": "Last month", "quarter": "In the last three months",
                 "year": "Last year", "each": "The last time"}
_MONEY_MODES = ("MONEY", "AMOUNT")
_COUNTLESS = frozenset(("rupees", "dollars", "euros", "pounds", "pesos", "funds", "savings", "earnings", "proceeds",
                        "payments", "fees", "costs", "charges", "sales", "hours", "minutes", "days"))


def _blank(text) -> bool:
    return text is None or not str(text).strip()


def cost_measure(cost: dict):
    """`Cost.measureOrDefault`: the typed measure, else *hours* on HOURS and *$* on money, else `None`."""
    if not _blank(cost.get("measure")):
        return str(cost["measure"]).strip()
    return "hours" if cost.get("mode") == "HOURS" else "$" if cost.get("mode") in _MONEY_MODES else None


def _said(text: str, team: bool) -> str:
    text = text.strip()
    return text if team else ll.second_person(text, False)


def _who(team: bool, pasted) -> str:
    return "your team" if team and not ll.third_person(pasted) else "you"


def _held(ladder: list[str]) -> str:
    return next((stem for stem in ladder if ll.words(stem) <= STEM_MAX_WORDS), ladder[-1])


def _in_their_past(text: str, team: bool) -> str:
    now = any(ll.clean(w) == "now" for w in ll.java_split(text))
    return text if team else ll.second_person(text, not now)


def _subject_said(subject: str, team: bool) -> str:
    return subject if team else ll.second_person(subject, False)


def _much(thing: str) -> str:
    first = ll.clean(thing.strip().split()[0])
    if first in ll.DETERMINERS:
        return "of " + thing
    return "in " + thing if ll.is_plural(ll.clean(thing.strip().split()[-1])) else thing


def _plural_head(base: str) -> bool:
    return any(not ll.clean(w).endswith("'s") and ll.is_plural(ll.clean(w)) for w in base.strip().split()[:4])


def _clauses(clause: str) -> list[str]:
    cut = ll.without_its_clause(clause)
    return [clause] + ([cut] if cut is not None and cut.strip() else [])


def count_noun(base) -> bool:
    """`CommercialChain.countNoun`: a base of things counted one by one (*the shipments*), never money or time."""
    if _blank(base):
        return False
    parts = base.strip().lower().split()
    at = 1 if parts[0] in ("the", "a", "an", "your", "their", "our", "its") else 0
    lower = next((w for w in parts[at:at + 3] if w.endswith("s") and not w.endswith("ss")), None)
    return lower is not None and lower not in _COUNTLESS


def gone_without(base):
    """`CommercialChain.goneWithout`: the thing a base names as time gone without, else `None`."""
    if _blank(base):
        return None
    m = re.fullmatch(r"(?:the |their |your )?(.+?)\s+(?:that\s+)?(?:they|you|people|we)?\s*(?:go|goes|went|gone|going|do"
                     r"|did)\s+without|(?:the |their |your )?(.+?)\s+(?:that\s+)?(?:they|you|people|we)\s+(?:miss|missed"
                     r"|lose|lost)", base.strip(), re.IGNORECASE)
    if not m:
        return None
    thing = (m.group(1) if m.group(1) is not None else m.group(2)).strip()
    return thing or None


def without_purpose(loss):
    """`CommercialChain.withoutPurpose`: a loss without its purpose clause, where at least three words stay."""
    if loss is None:
        return None
    m = re.fullmatch(r"(.+?)\s+(?:up\s+)?(?:in order\s+)?to\s+[a-z]+\b.*", loss)
    if not m:
        return None
    kept = m.group(1).strip()
    return kept if ll.words(kept) >= 3 and kept != loss else None


def same_words(a, b) -> bool:
    """`CommercialChain.sameWords`: case, articles and person aside, the same words (a loss that is only the base)."""
    if a is None or b is None:
        return False

    def norm(t):
        t = ll.second_person(t, False).lower()
        t = re.sub(r"\b(the|a|an)\b", "", t)
        return re.sub(r"[^a-z0-9%]+", " ", t).strip()
    return norm(a) == norm(b)


def _loss_count(ladder, opening, team, loss) -> None:
    if loss is None or loss.shape == ll.NONE:
        return
    thing = _said(loss.thing, team)
    for clause in _clauses(loss.clause):
        if loss.shape == ll.DOES:
            asked = thing + " " + _in_their_past(ll.past(clause), team)
        elif loss.shape == ll.DONE:
            asked = thing + " were " + _in_their_past(ll.past(clause), team)
        else:
            asked = thing + " did " + _subject_said(loss.subject, team) + " " + _in_their_past(ll.after_did(clause), team)
        for about in (", about how many ", ", how many "):
            ladder.append(opening + about + asked + "?")


def _loss_share(ladder, opening, team, loss, base) -> None:
    be = " were " if count_noun(base) or _plural_head(base) else " was "
    for clause in _clauses(loss.clause):
        if loss.shape == ll.DOES:
            asked = base + " " + _in_their_past(ll.past(clause), team)
        elif loss.shape == ll.DONE:
            asked = base + be + _in_their_past(ll.past(clause), team)
        else:
            asked = base + " did " + _subject_said(loss.subject, team) + " " + _in_their_past(ll.after_did(clause), team)
        for about in (", about what share of ", ", what share of "):
            ladder.append(opening + about + asked + "?")


def _loss_missed(ladder, opening, team, loss) -> None:
    thing = _said(loss.thing, team)
    rest = "" if not loss.clause.strip() else _in_their_past(ll.past(loss.clause), team)
    forms = []
    if loss.rest_is_a_place():
        forms.append((thing, rest))
        shorter = without_purpose(rest)
        if shorter is not None:
            forms.append((thing, shorter))
        cut = ll.without_its_clause(rest)
        if cut is not None:
            forms.append((thing, cut))
    else:
        whole = (thing + " " + rest).strip()
        forms.append((whole, ""))
        shorter = without_purpose(whole)
        if shorter is not None:
            forms.append((shorter, ""))
    for said, where in forms:
        for about in (", about how much ", ", how much "):
            whom = _who(team, said + " " + where)
            for person in ([whom] if whom == "you" else [whom, "you"]):
                ladder.append(opening + about + _much(said) + " did " + person + " miss"
                              + ("" if not where.strip() else " " + where) + "?")


def cost_question(team: bool, occasion, job, cost: dict) -> str:
    """`CommercialChain.costQuestion(team, circumstance, occasion, job, period, cost)` on a chain cost (spec 110 FR-3,
    keel-cloud 170 FR-5): the stranger's cost question in their own terms, held to the spoken cap by each frame's
    give-way ladder. HOURS *spend on* the thing (or the time gone without, *miss*); RATE the founder's loss line's verb
    and thing (`LossLine`) -- a share of the base, a count of the thing -- else the measure's neutral *miss*; MONEY
    *what did ... cost*. No frame says *lose* by default. `team` is the decision-maker's link (`corridor.isB2b()`)."""
    over = cost.get("period") if cost.get("period") in _COST_OPENERS else "month"
    opening = _COST_OPENERS[over]
    base = None if _blank(cost.get("base")) else _said(str(cost["base"]), team)
    noun = ll.occasion_noun(occasion)
    doing = None if _blank(job) else _said(str(job).strip(), team)
    unit = str(cost["unit"]).strip() if team and not _blank(cost.get("unit")) else None
    ladder: list[str] = []
    if cost.get("mode") == "HOURS":
        missed = None if cost.get("base") is None else gone_without(cost.get("base"))
        if missed is not None:
            ladder.append(f"{opening}, about how many hours of {_said(missed, team)} did {_who(team, missed)} miss?")
        elif base is not None or noun is not None:
            thing = base if base is not None else ll.plural(noun)
            if unit is not None and ll.words(unit) <= 2:
                ladder.append(f"{opening}, about how many hours per {unit} did {_who(team, thing)} spend on {thing}?")
            ladder.append(f"{opening}, about how many hours did {_who(team, thing)} spend on {thing}?")
        if doing is not None:
            ladder.append(f"{opening}, about how many hours did it take {_who(team, doing)} to {doing}?")
        ladder.append(f"{opening}, about how many hours did {_who(team, None)} spend on this?")
        return _held(ladder)
    if cost.get("mode") == "RATE":
        measure = cost_measure(cost)
        share = measure is None or measure.strip() == "%"
        loss = ll.read(cost.get("lossPhrase"))
        if loss is not None and same_words(cost.get("lossPhrase"), base):
            loss = None
        if not share:
            _loss_count(ladder, opening, team, loss)
            ladder.append(f"{opening}, about how many {measure.strip()} did {_who(team, None)} miss?")
        else:
            loss_open = f"On your last {noun}" if not team and noun is not None else opening
            openings = [opening] if loss_open == opening else [loss_open, opening]
            if loss is not None and loss.shape != ll.NONE and base is not None:
                for each in openings:
                    _loss_share(ladder, each, team, loss, base)
            elif loss is not None and loss.shape == ll.NONE:
                for each in openings:
                    _loss_missed(ladder, each, team, loss)
            if base is not None:
                ladder.append(opening + (", about what share of " if count_noun(base) else ", about how much of ")
                              + base + " did " + _who(team, base) + " miss?")
        ladder.append(f"{opening}, about how much did {_who(team, None)} miss?")
        return _held(ladder)
    if over == "each" and noun is not None:
        thing = base if base is not None else "it"
        ladder.append(f"On your last {noun}, what did {thing} cost" + ("" if unit is None else f" per {unit}") + "?")
    if base is not None:
        ladder.append(f"{opening}, what did {base} cost {_who(team, base)}?")
    if noun is not None:
        ladder.append(f"{opening}, what did {ll.plural(noun)} cost {_who(team, None)}?")
    if doing is not None:
        ladder.append(f"{opening}, what did it cost {_who(team, doing)} to {doing}?")
    ladder.append(f"{opening}, what did it cost {_who(team, None)}?")
    return _held(ladder)


def _label_time(period, unit) -> str:
    over = period if period in _COST_OPENERS else "month"
    per = "" if _blank(unit) else "per " + str(unit).strip()
    if over == "each":
        return per or "the last time"
    opening = _COST_OPENERS[over]
    time = opening[0].lower() + opening[1:]
    return (per + " " if per else "") + time


def _without_possessive(base: str) -> str:
    m = re.fullmatch(r"(?:the|their|your|its|our)\s+\S+'s\s+(.+)", base.strip(), re.IGNORECASE)
    return m.group(1) if m else base.strip()


def stranger_cost_label(cost: dict, occasion, role_word, team: bool) -> str:
    """`CommercialChain.strangerCostLabel` (keel-cloud 170 FR-5): the label after the stranger's value box, one plain
    phrase -- *hours per site last month*, *conversations last month*, *% of GPU hours last month*, a consumer's share
    *% of the rupees you move to dollars*, money *of the pole inspections per pole*."""
    unit = (str(cost["unit"]).strip() if not _blank(cost.get("unit"))
            else None if _blank(role_word) else str(role_word).strip()) if team else None
    period = cost.get("period")
    when = _label_time(period, unit)
    if cost.get("mode") == "HOURS":
        return ("hours " + when).strip()
    if cost.get("mode") == "RATE":
        measure = cost_measure(cost)
        if measure is not None and measure.strip() != "%":
            return (measure.strip() + " " + when).strip()
        base = str(cost["base"]).strip() if not _blank(cost.get("base")) else ll.occasion_noun(occasion)
        if not team:
            return ("% " + ("" if base is None else "of " + _said(base, False))).strip()
        return ("% " + ("" if base is None else "of " + _without_possessive(base) + " ") + _label_time(period, None)).strip()
    base = None if _blank(cost.get("base")) or (period == "each" and unit is not None) else str(cost["base"]).strip()
    return (("" if base is None else "of " + _said(base, team) + " ") + when).strip()


def cost_item(entry) -> dict | None:
    """The stranger's Existing sacrifice item as keel-cloud 170 composes it from an entry that states the chain
    (`RespondentQuestionsRules.costItem`, `InterviewComposer.valueBoxItem`; spec 110 FR-3): the question, the label after
    the box, the *None* chip, the chips recorded apart, the item's escape and the spoken answer and escape lines, on the
    link that carries part 3 (the decision-maker's on a B2B study). `None` off the chain (a cost stated before it is
    spec 077's, `CostEstimate.respondentQuestion`, and not mirrored here)."""
    cost = entry.cost() if hasattr(entry, "cost") else None
    if not entry.chain() or not cost:
        return None
    team = is_b2b(entry)
    ctx = _ctx(entry)
    role_word = (entry.decision_maker_role() if team else None) or ctx.get("actor")
    label = stranger_cost_label(cost, entry.occasion(), role_word, team)
    return {"question": cost_question(team, entry.occasion(), ctx.get("job"), cost), "label": label,
            "nothing": {"code": "NOTHING", "label": VALUE_BOX_LABELS["NOTHING"]},
            "chips": [{"code": c, "label": VALUE_BOX_LABELS[c]} for c in value_box_escapes(not team)],
            "escape": {"code": "DONT_KNOW", "label": VALUE_BOX_LABELS["DONT_KNOW"]},
            "optionsLine": value_box_answer_line(cost, label), "escapeLine": "Or say you can't recall."}


def value_box_answer_line(cost: dict, label) -> str:
    """`CommercialChain.valueBoxAnswerLine` (keel-cloud 170 FR-5): the value box's spoken answer line names the label --
    *A percent of GPU hours last month, or a low and a high; none is 0.* -- where `SpokenForm.VALUE_BOX_ANSWER_LINE`
    said *in the unit on the screen*."""
    text = "" if label is None else str(label).strip()
    if cost.get("mode") in _MONEY_MODES:
        what = "An amount" + ("" if not text else " " + text)
    elif text.startswith("% "):
        what = "A percent " + text[2:].strip()
    elif text == "%":
        what = "A percent"
    else:
        what = "A number" + ("" if not text else " of " + text)
    return what + ", or a low and a high; none is 0."
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
#: Spec 089 FR-4 (keel-cloud 159): Relative advantage left this list -- the stranger answers the scale's four, never the
#: founder's benefits.
PICKED_AMONG_ITEMS = ("problem.importance", "problem.current_solution_satisfaction")


def wire_codes(entry, key: str) -> dict[str, str]:
    """`{corpus code: wire code}` for a list dimension whose items the stranger picks among (Importance's
    five, Current solution's five outcomes); `{}` elsewhere."""
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
#: Spec 086 (keel-cloud 152, corpus revision 18): the five phrases are the bin's share as the registry's option rule
#: now says them (*under 2 in 10 ... at least 8 in 10*, recorded capitalised, 152's judgement call 8) -- every corpus
#: entry's chosen phrase is its bin's, so a default and a chosen phrase never differ; they read *Only a few ... Nearly
#: all* through revision 17.
PREVALENCE_OPTIONS = [
    ("Fewer than 2 in 10", "p_0_20", "Under 2 in 10"),
    ("2 or 3 in 10", "p_20_40", "2 to 3 in 10"),
    ("4 or 5 in 10", "p_40_60", "4 to 5 in 10"),
    ("6 or 7 in 10", "p_60_80", "6 to 7 in 10"),
    ("8 or more in 10", "p_80_100", "At least 8 in 10"),
]


#: keel-cloud 161 FR-1 (`ItemFrames.YOUR_WAY_OF`): the opening a Current solution phrase stored before 161 carries.
YOUR_WAY_OF = re.compile(r"^(?i:your\s+way\s+of)\s+")


def bare_phrase(phrase: str | None) -> str | None:
    """keel-cloud 161 FR-1 (`ItemFrames.bare`): the Current solution phrase is the bare act in the people's words -- a
    phrase that opens on *your way of* (any case, any spacing) is read without it; any other stripped of its edges."""
    if phrase is None:
        return None
    text = phrase.strip()
    opening = YOUR_WAY_OF.match(text)
    return text[opening.end():].strip() if opening else text


def one_act(phrase: str | None) -> str | None:
    """keel-cloud 128 FR-16 (`ItemFrames.oneAct`): a phrase names one act -- *finding the fix and logging it* keeps
    *finding the fix*, *catching and fixing that failure* keeps *catching that failure*."""
    if phrase is None:
        return None
    text = phrase.strip()
    shared = re.match(r"^(.*?\b[a-z]+ing) and [a-z]+ing\b(.*)$", text)
    if shared:
        return (shared.group(1) + shared.group(2)).strip()
    two = re.match(r"^(.*?\b[a-z]+ing\b.*?),? and [a-z]+ing\b.*$", text)
    if two:
        return two.group(1).strip()
    return text


def said_phrase(phrase: str | None) -> str | None:
    """keel-cloud 161 FR-1 (`ItemFrames.said`): the phrase as the stranger hears it -- bare, one act, no closing stop or
    question mark; None where there is none. The frame (*How did {said} go?*) and the follow-up's `{phrase}` say it."""
    bare = bare_phrase(phrase)
    if not bare:
        return None
    said = one_act(bare)
    while said.endswith((".", "?")):
        said = said[:-1].strip()
    return said or None


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
            raise VectorsScriptError(f"{entry.id}: {key} carries no phrase (L1)")
        # spec 093 FR-1 (keel-cloud 161 FR-1): the draft writes the act bare, as the model now does -- the corpus's
        # *your way of ...* read with the opening stripped (`ItemFrames.bare`), so no scripted draft earns an `L1` note
        draft["phrase"] = bare_phrase(saved["phrase"])
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


def _same_words(a: str | None, b: str | None) -> bool:
    return " ".join(str(a or "").lower().split()).rstrip(".") == " ".join(str(b or "").lower().split()).rstrip(".")


def rungs_plan(entry, drawn: list[str], max_items: int) -> dict:
    """Spec 067 FR-2 (keel-cloud 128 FR-16; Pairio typed two of five): what the founder does to Keel's draft on the
    Check screen so that every one of the entry's Current-solution rungs is served, in the entry's order. The rungs are
    positional (code's positional codes, `single_choice_5`), so the founder's rung i goes in row i: a drawn row that
    does not carry it word for word is **edited** over (`edit`: (row index, label) -- Karsa, 2026-10-23: Keel redrafted
    three of five and the walk stopped for want of room), a rung past the drawn rows is typed into a new row (`add`)
    while the screen's `max_items` has room, and a rung past that stops the walk by name (`cannot`)."""
    labels = [i["label"] for i in founder_list(entry, "problem.current_solution_satisfaction")["items"]]
    plan = {"edit": [], "add": [], "cannot": []}
    for i, label in enumerate(labels):
        if i < len(drawn):
            if not _same_words(label, drawn[i]):
                plan["edit"].append((i, label))
        elif i < int(max_items):
            plan["add"].append(label)
        else:
            plan["cannot"].append(label)
    return plan


def saved_list(entry, key: str) -> dict:
    """The list as the founder saves it and the wire stores it (keel-cloud `SavedList`): every item, in
    order, with code's positional codes, `asked` where the dimension carries faces, `pickedIndex` where it
    picks, Current solution's `phrase` -- bare since spec 093 FR-1 (keel-cloud 161): the founder saves the draft's
    phrase as Keel drafted it, the act without *your way of*."""
    saved = founder_list(entry, key)
    items = []
    for i, item in enumerate(saved["items"]):
        out = {"code": wire_code(key, i), "label": item["label"]}
        if key in ASKED_FACES and item.get("asked"):
            out["asked"] = item["asked"]
        items.append(out)
    picked = saved.get("picked")
    return {"items": items, "pickedIndex": int(picked) if key in PICKED and picked is not None else None,
            "phrase": bare_phrase(saved.get("phrase")) if key == "problem.current_solution_satisfaction" else None}


#: keel-web's Answer box on a list dimension: *Up to 25 words* (the founder's words Keel drafts the list from).
ANSWER_MAX_WORDS = 25


def answer_drops(entry, key: str) -> list[str]:
    """The labels `answer_text` cannot fit in the Answer box -- what the founder would never type, so Keel would never
    draft (spec 067 FR-1: the judges of Palus, Transload, Expanse, Veles and Codyco found one dropped)."""
    if not (entry.founder_list(key) or {}).get("items"):
        return []
    labels = _answer_labels(entry, key)
    typed = answer_text(entry, key).split("; ")
    return [label for label in labels if label not in typed]


def check_answer_box(entry) -> None:
    """Spec 067 FR-1 (keel-cloud 128 FR-17, FR-20): at load, no list label is over the Answer box's 25 words, and
    Importance's Answer names every difficulty it is to name inside it (Current solution's rungs past the box are typed
    on the Check screen instead, FR-2) -- else the run stops here, naming the label, never after a paid walk."""
    for key in (k for k in LIST_CONTROLS if (entry.founder_list(k) or {}).get("items")):
        for item in entry.founder_list(key)["items"]:
            if _words(item.get("label")) > ANSWER_MAX_WORDS:
                raise VectorsScriptError(f"{entry.id}: {key}'s item {item['label']!r} is {_words(item['label'])} words; "
                                         f"the Answer box takes {ANSWER_MAX_WORDS} (spec 067 FR-1)")
    importance = "problem.importance"
    if (entry.founder_list(importance) or {}).get("items") and not entry.unsure(importance):
        dropped = answer_drops(entry, importance)
        if dropped:
            raise VectorsScriptError(
                f"{entry.id}: problem.importance's Answer takes {ANSWER_MAX_WORDS} words and the founder's items need "
                f"{_words('; '.join(_answer_labels(entry, importance)))} -- {', '.join(repr(d) for d in dropped)} would "
                "be dropped, so Keel would never draft it and strangers never be offered it (spec 067 FR-1; keel-cloud "
                "128 FR-17, FR-20)")


def _answer_labels(entry, key: str) -> list[str]:
    """The labels the founder's Answer on `key` names, in order, before the box's cap."""
    saved = founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != NOBODY_ELSE[0]]
    if key == "problem.importance":
        labels = importance_named(entry)
    if key == "problem.current_solution_satisfaction" and saved.get("phrase"):
        labels = [saved["phrase"]] + labels
    return labels


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
        if _words(candidate) > ANSWER_MAX_WORDS:
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
    in_scope = scope_vectors(entry)
    for vector in VECTORS:
        if vector not in in_scope:
            # spec 071: only the scope's vectors are calibrated (keel-cloud 133 FR-3), and since keel-cloud 134 FR-2 only
            # theirs are chained (spec 072 FR-3, DRIFT #97 closed): nothing is scripted for another vector
            continue
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
    if not serves_part(entry, part, link):
        return []                               # spec 071 (keel-cloud 133 FR-4): a part the scope does not serve
    if part == 1 and "PROBLEM" not in scope_vectors(entry):
        return ["problem.prevalence"]           # 133 FR-5: the gate alone, the anchor, uncounted
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
    decision-maker's link's) are code's, written with the lock. Spec 071 (keel-cloud 133 T010): none where the scope
    serves no gate (money alone has no model job)."""
    return [(1, LINK_PRIMARY)] if serves_gate(entry) else []


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


def read_owed(entry, name: str) -> bool:
    """Spec 101 FR-1: whether `name`'s answer queues a reading on the study the entry is walked under -- a readable
    person (`readable_people`) on a study that serves the gate, where the story is asked. Money alone serves no gate
    (keel-cloud 133 FR-4: the person's link opens with the idea card, then part 3), so nobody types a story there, no
    answer awaits a reading (keel-cloud `Invitation.awaitsReading`) and the founder's `POST readings` is refused
    `NOTHING_TO_READ` -- the file's story is not the walk's."""
    return serves_gate(entry) and any(p.person == name for p in readable_people(entry))


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
    vectors = scope_vectors(entry)
    screens: dict[str, list[dict]] = {
        CONTEXT_SCREEN: [_completed(context_result(entry))],
        PROBLEM_SCREEN: [_completed(problem_result(entry))],
    }
    # spec 071 (keel-cloud 133): the idea card wherever the solution or the money is in scope; the solution's lists'
    # faces only with the solution; part 1's one job only where the gate is served
    if "SOLUTION" in vectors or "COMMERCIAL" in vectors:
        screens[MECHANISM_SCREEN] = [_completed(mechanism_result(entry))]
    screens[CALIBRATION_SCREEN] = [_completed(calibration_result(entry, vector, only))
                                   for vector, only in calibration_jobs(entry)]
    asked = [_completed(asked_result(entry, key)) for key in ("solution.compatibility", "solution.adoption_friction")
             if not entry.unsure(key)] if "SOLUTION" in vectors else []
    if asked:
        screens[ASKED_SCREEN] = asked
    for part, link in respondent_jobs(entry):
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
    # spec 076 FR-6: and the one answer not about this, on the rung its person is asked (`JUNK_FOLLOW_UPS`)
    return [(rung, FOLLOW_UP_LINES[rung][0]) for rung in fake.RUNGS] + junk_follow_ups(entry, people)


#: Spec 076 FR-6 (keel-cloud 145 FR-6, keel-web 127 FR-4): the one person a golden journey has type an answer that is
#: not about the question on their follow-up -- 01-countly's Priya Natarajan (S-005), owed one rung alone (Current
#: solution), so the rung her words land on is known before the run and the THEMES script can place them. The fake's
#: grouping (`interviewer_fake.themes_with_junk`) puts them in NOT_ABOUT_THIS.
JUNK_FOLLOW_UPS = {"01-countly": {"Priya Natarajan": "Meow, you are a fool."}}


def junk_rung(entry, person) -> str | None:
    """Spec 076 FR-6: the one rung a `JUNK_FOLLOW_UPS` person's words land on -- on the whole study (S-005; the scope
    journeys reuse 01-countly and are left as they were) and only where they are owed exactly one follow-up, so the
    script knows the rung before the run; None otherwise (they type the pooled line, as everyone else)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    if person is None or scope_of(entry) != "ALL" or person.person not in (JUNK_FOLLOW_UPS.get(entry.id) or {}):
        return None
    owed = fake.owed(person.picks, founder_side(entry), person.link, b2b=is_b2b(entry))
    return owed[0][0] if len(owed) == 1 else None


def junk_follow_ups(entry, people) -> list[tuple[str, str]]:
    """`[(rung, text)]`: each `JUNK_FOLLOW_UPS` person's words on the one rung they are owed (`junk_rung`). The person
    answers first on 01-countly and keel-cloud starts no THEMES job on fewer than two answers (`ThemesOnReturn`), so
    every job over that rung carries the words and the pooled line both -- the scripted theme resolves."""
    out = []
    for name, text in (JUNK_FOLLOW_UPS.get(entry.id) or {}).items():
        rung = junk_rung(entry, next((p for p in people if p.person == name), None))
        if rung is not None:
            out.append((rung, text))
    return out


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
        # spec 076 FR-6 (keel-cloud 145 FR-6): an answer not about this in its own NOT_ABOUT_THIS group, last
        grouped = fake.themes_with_junk([{"id": str(i), "text": t} for i, t in enumerate(texts)], NAMES[key])["themes"]
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
    check_answer_box(entry)
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


def founder_pilot(entry) -> bool:
    """Spec 114 FR-1 (keel-web 146 FR-2): the founder's pick on the pilot screen -- True for *Yes, ask them*, False for
    *No pilot*. Yes on every entry: the corpus's `pilot_opt_in` people expect the pilot line at the end (spec 067 FR-6),
    and no entry, golden or back-test, records a founder who opts out (none carries a founder-side pilot answer). An
    entry object that says `founder_pilot = False` (a test's) picks No."""
    return getattr(entry, "founder_pilot", True) is not False


@dataclass(frozen=True)
class Pick:
    """One item's answer, by dimension and by the wire's code -- the ids are computed per token."""
    dimension: str
    codes: list = field(default_factory=list)
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
        return Pick(dimension=self.dimension, codes=self.codes, cost=cost, scale=self.scale, chip=self.chip,
                    cost_period=period)

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
        # spec 089 FR-4 (keel-cloud 159, contract 47): `advantageIds` is gone -- Relative advantage is one code
        return out


#: Spec 088 FR-2: the stranger's two posts on the scripted path, Begin before the response (`scripted_posts`).
BEGIN_PATH = interview_charge.BEGIN_PATH
RESPONSE_PATH = "/interview/response"


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
    #: Spec 067 FR-3: the rung this person's own line was written for (`follow_up: {dimension, text}`), or None.
    follow_up_dimension: str | None = None
    #: Spec 064 FR-7: a corpus pick the served options cannot carry, re-expressed (`(dimension, corpus, sent)`) -- a
    #: finding, never a silent drop (Commitment's *yes, after trying it first* where no smaller step is served).
    remapped: tuple = ()
    #: Spec 089 FR-2: the scripted person's notes -- what the walk sends other than the file records, each named in
    #: words (a recorded Frequency 0 after a yes sent as 1, `ZERO_SENT_AS_ONE`, spec 090 FR-3).
    notes: tuple = ()
    #: Spec 102 FR-1 (keel-cloud 133 FR-4): whether the study the person is walked under serves the gate (`serves_gate`,
    #: set by `person_inputs`). Off the gate -- money alone -- nobody is asked *Yes, I recall* and nobody types a story:
    #: `recency`, `story` and `anchor_chip` stay the file's record and are never sent.
    gate: bool = True

    def scripted_posts(self, token: str, recall_period: str | None = None, **extra) -> list[tuple[str, dict | None]]:
        """Spec 088 FR-2 (keel-cloud 156, contract 45): what a scripted person posts, in order -- `POST
        /v2/i/{token}/interview/begin` first (no body; keel-web 131's intro posts it on Begin, and it writes the one
        INTERVIEW row of 30 on Keel's door), then the one response (`response`, with `extra` fields such as `format`).
        A scripted person is charged as a real one is."""
        return [(BEGIN_PATH, None), (RESPONSE_PATH, {**self.response(token, recall_period), **extra})]

    def response(self, token: str, recall_period: str | None = None) -> dict:
        """The one `POST /v2/i/{token}/interview/response` body; a cost total re-expressed over
        `recall_period`, the period the interview asks it over."""
        answers = [p.asked_over(recall_period).as_wire(token) for p in self.picks]
        if not self.in_segment:
            # spec 076 FR-4 (keel-cloud 145 FR-4b, keel-web 127 FR-2): the decision-maker's screener answered outside
            # sends `outsideSegment` alone too, as part 1's chip does
            return {"outsideSegment": True, "answers": []}
        if self.link == LINK_B2B:
            return {"answers": answers}
        if not self.gate:
            # spec 102 FR-1 (keel-cloud 133 FR-4, keel-web 145): money alone's FULL link serves no gate -- the page posts
            # the answers alone (beside `followUps` / `pilotOptIn`), as the decision-maker's link does; the file's story
            # and chip are the gate's, which this study never asks. FR-2: a recorded gate No has nothing to send
            if self.recency is False:
                raise VectorsScriptError(NO_ANSWERS_OFF_THE_GATE.format(person=self.person))
            return {"answers": answers}
        if not self.recency:
            return {"recency": False, "answers": []}
        if self.anchor_chip:
            # spec 076 FR-5 (keel-cloud 145 FR-5, keel-web 127 FR-3, contract 43): a story chip ends the interview --
            # the gate's Yes and the chip, no story, no answers (a chip is never sent with answers any more)
            return {"recency": True, "anchorChip": self.anchor_chip, "answers": []}
        body: dict = {"recency": True, "answers": answers}
        if self.story:
            body["story"] = self.story
        return body

    @property
    def ends_on_chip(self) -> bool:
        """Spec 076 FR-5: the gate's Yes with a story chip -- the interview ends at the gate (keel-web 127 FR-3)."""
        # spec 102 FR-2: off the gate no chip is asked, so none ends the interview
        return bool(self.gate and self.recency and self.in_segment and self.anchor_chip and self.link != LINK_B2B)


#: Spec 102 FR-2: the refusal of a file person with a gate No on a study that serves no gate -- the page asks them part
#: 3, and the file records no money answers for them (a gate No is asked nothing more).
NO_ANSWERS_OFF_THE_GATE = ("{person}: the file records a gate No (recency: false), but money alone serves no gate "
                           "(keel-cloud 133 FR-4) -- the page asks them part 3 and the file has no answers for it; a "
                           "revision would have to record their money picks (and a gate Yes, or no gate answer) for the "
                           "walk to send them (spec 102 FR-2)")
#: Spec 102 FR-4: a person outside the segment on a study that serves no gate, where the money link asks no screener.
#: Spec 100: keel-cloud 166 / keel-web 145 serve it as `Interview.condition` wherever the people carry a condition, so
#: the link that still serves none is a project locked before 166 (its part 3 stored no chip, 166's *not foreseen* 4) or
#: a condition past the spoken cap (E7: no chip stored).
OUTSIDE_OFF_THE_GATE = ("{person}: outside the segment; the money link served no screener (keel-cloud 166 serves "
                        "`condition` there -- a project locked before it, or a condition past 20 words, has none), so "
                        "they are not walked (spec 100)")


def not_walked_off_the_gate(person, interview: dict) -> str | None:
    """Spec 102 FR-2 / FR-4: why `person` is not walked on a study that serves no gate (money alone's FULL link), or
    None -- walked as everyone is. A gate No in the file has no money answers to give (`NO_ANSWERS_OFF_THE_GATE`, the
    words `PersonInputs.response` refuses with); a person outside the segment cannot be screened until the served
    interview carries `condition` (keel-cloud 166 / keel-web 145) -- where it does (spec 100) they are walked to the
    screener's exit, `{outsideSegment: true, answers: []}` sent. Never on the decision-maker's link, never where the
    gate is served."""
    if getattr(person, "gate", True) or person.link == LINK_B2B:
        return None
    if not getattr(person, "in_segment", True):
        return None if (interview or {}).get("condition") else OUTSIDE_OFF_THE_GATE.format(person=person.person)
    if person.recency is False:
        return NO_ANSWERS_OFF_THE_GATE.format(person=person.person)
    return None


#: Spec 112's addendum (keel-cloud 172, `ItemFrames.escapeFor`): Current solution's two ways out on the wire -- the
#: registry's *Someone else did it* where the list writer's `handed_off` call was true (or the list carries none), *I
#: can't recall* where it was false. keel-cloud refuses the other one (*not this question's way out*).
CURRENT_SOLUTION_KEY = "problem.current_solution_satisfaction"
CURRENT_SOLUTION_ESCAPES = ("SOMEONE_ELSE_CHECKS", "CANT_RECALL")
ESCAPE_SENT_AS_SERVED = ("{person}: Current solution's escape is served as {label!r} (keel-cloud 172: the list writer "
                         "judged the act one that {can} be handed off); the file's {was} is sent as {code}, the code "
                         "served (spec 112's addendum)")


#: Spec 115 FR-0 (keel-cloud 174 FR-2): Purchase friction's two codes -- *I can't tell* since 174, *I can't recall* on a
#: build before it (and in revision 19's record, read as *I can't tell* by `corpus.spec174_escape`). keel-cloud refuses
#: the one not served (*not this question's way out*).
PURCHASE_FRICTION_KEY = "commercial.purchase_friction"
PURCHASE_FRICTION_ESCAPES = ("CANT_TELL", "CANT_RECALL")
FRICTION_SENT_AS_SERVED = ("{person}: Purchase friction's escape is served as {label!r} (a build {when} keel-cloud 174); "
                           "the walk's {was} is sent as {code}, the code served (spec 115 FR-0)")


def served_escape_picks(person: "PersonInputs", items: dict) -> tuple["PersonInputs", list[str]]:
    """Spec 112's addendum (keel-cloud 172): the walk sends the code served. A person's Current solution escape that is
    not the served item's (`items[dimension].escape.code`) is sent as the served one, and each re-expression is named
    (`ESCAPE_SENT_AS_SERVED`); with nothing served, or the served code the file's, the person is unchanged. Spec 115
    FR-0 (keel-cloud 174): Purchase friction's the same way (`PURCHASE_FRICTION_ESCAPES`, `FRICTION_SENT_AS_SERVED`) --
    the person carries `CANT_TELL` (the record read through `corpus.spec174_escape`), sent as `CANT_RECALL` only where a
    build before 174 serves it."""
    import dataclasses                                                 # noqa: PLC0415
    ways = {CURRENT_SOLUTION_KEY: CURRENT_SOLUTION_ESCAPES, PURCHASE_FRICTION_KEY: PURCHASE_FRICTION_ESCAPES}
    served = {key: (items.get(key) or {}).get("escape") or {} for key in ways}
    codes = {key: str(served[key].get("code") or "").upper() for key in ways}
    picks, notes = [], []
    for pick in person.picks:
        code = codes.get(pick.dimension)
        if code in ways.get(pick.dimension, ()) and pick.chip in ways[pick.dimension] and pick.chip != code:
            label = served[pick.dimension].get("label")
            if pick.dimension == CURRENT_SOLUTION_KEY:
                notes.append(ESCAPE_SENT_AS_SERVED.format(person=person.person, label=label,
                                                          can="cannot" if code == "CANT_RECALL" else "can",
                                                          was=pick.chip.lower(), code=code.lower()))
            else:
                notes.append(FRICTION_SENT_AS_SERVED.format(person=person.person, label=label,
                                                            when="before" if code == "CANT_RECALL" else "after",
                                                            was=pick.chip.lower(), code=code.lower()))
            pick = dataclasses.replace(pick, chip=code)
        picks.append(pick)
    return (dataclasses.replace(person, picks=picks), notes) if notes else (person, [])


#: keel-cloud `Period`'s days, the one table a cost total is normalised by.
PERIOD_DAYS = {"day": 1.0, "week": 7.0, "month": 30.4375, "quarter": 91.3125, "year": 365.25}


def _pick(entry, key: str, raw) -> Pick:
    if isinstance(raw, dict) and raw.get("chip"):
        chip = str(raw["chip"])
        if chip not in ESCAPES:
            raise VectorsScriptError(f"{entry.id}: {key}'s chip {chip!r} is not an escape at contract 14")
        # spec 115 FR-0 (keel-cloud 174 FR-2): revision 19's Purchase friction `cant_recall` is read as `cant_tell`
        # through the reader's one rule; `served_escape_picks` then sends the code served
        return Pick(dimension=key, chip=corpus_reader.spec174_escape(key, chip).upper())
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
    # spec 089 FR-1 (keel-cloud 159, revision 19): Relative advantage's pick is one code of the scale, sent as it is
    if key == "problem.frequency":
        return Pick(dimension=key, scale=int(raw))
    if isinstance(raw, list):
        return Pick(dimension=key, codes=[on_the_wire(entry, key, str(c)) for c in raw])
    return Pick(dimension=key, codes=[on_the_wire(entry, key, str(raw))])


# ---------------------------------------------------------------- spec 051: the founder's side of the ladder

def founder_side(entry, *, line: int | None = None):
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
    # keel-cloud 128 FR-21: an up-front-then price is held on both steps -- the up front's own low as well
    upfront = float(price["upfrontLow"]) if chain and chain_mod.two_steps(price) and price.get("upfrontLow") is not None \
        else None
    return fake.Founder(importance_item=wire_code("problem.importance", 0) if importance and importance["items"]
                        else None, price_low=low, buyer_supports=supports, chain_price=chain, current_line=line,
                        upfront_low=upfront)


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


_THING_COULD_NOT = re.compile(
    r"(?i)^(?:could|can|would)\s+(?!you\b)(?:[a-z'-]+\s+){1,5}?have\s+([a-z]+(?:ed|en|wn|ne|ght|ld))\b(.*)$")


def thing_could_not(asked: str | None) -> str | None:
    """keel-cloud 131 FR-10 (`FollowUpComposer.thingCouldNot`): a condition of their thing, *could your hotel's phone
    system have forwarded unanswered calls to another number*, as the verb phrase after *You said you couldn't* --
    *have forwarded unanswered calls to another number*; None for any other shape."""
    text = re.sub(r"[?.]+$", "", (asked or "").strip())
    m = _THING_COULD_NOT.match(text) if text else None
    return f"have {m.group(1).lower()}{m.group(2)}" if m else None


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
#: Spec 075 (keel-web 124 FR-1's latency rule, judgement call): whose follow-up route call, made right after the item
#: their one rung hangs on, the text walk holds past the beat -- the page goes on, the rung stays owed and the end asks
#: it at the end (with *The only extra question.*), so a golden journey meets the end's follow-up too.
LATE_FOLLOW_UPS = {"05-paidly": ("Wen Zhang",)}
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
        if person.link != LINK_B2B and (not person.recency or getattr(person, "ends_on_chip", False)):
            # a gate No, or (spec 076 FR-5) a story chip: the interview ended at the gate, nothing is asked
            continue
        rung = fake.first_rung(person.picks, founder, person.link, b2b=is_b2b(entry))
        if rung is None:
            continue
        if rung == junk_rung(entry, person):
            out[person.person] = JUNK_FOLLOW_UPS[entry.id][person.person]
            continue
        own = getattr(person, "follow_up", None)
        out[person.person] = None if person.person in FOLLOW_UP_SKIPS.get(entry.id, ()) \
            or (own is None and getattr(entry, "backtest", False)) else (own or FOLLOW_UP_LINES[rung][0])
    return out


def follow_up_line(entry, person, owed: dict | None) -> str | None:
    """What `person` types on the follow-up they are actually asked (`owed`, the walk at answer time): None for a
    skipper or where nothing is owed; a back-test person's own words where the file has them; else that rung's line."""
    if not owed or person.person in FOLLOW_UP_SKIPS.get(entry.id, ()):
        return None
    if owed.get("dimension") is not None and owed.get("dimension") == junk_rung(entry, person):
        # spec 076 FR-6: this person's words are not about the question (*Meow, you are a fool.*)
        return JUNK_FOLLOW_UPS[entry.id][person.person]
    mine = next((p for p in entry.people() if p.person == person.person), None)
    own = getattr(mine, "follow_up", None)
    if own and getattr(mine, "follow_up_dimension", None) and mine.follow_up_dimension != owed.get("dimension") \
            and not getattr(entry, "backtest", False):
        # spec 067 FR-3: a line written for one rung is never typed on another (golden entries carry none)
        return None
    if own is None and getattr(entry, "backtest", False):
        # a back-test person says only what the file gives them: with no words of their own on the rung actually
        # asked, they skip -- the pooled line is the golden journeys' (its insights would otherwise rest on filler;
        # the judges of 10-palus and 12-transload named three such boxes)
        return None
    return own or FOLLOW_UP_LINES[owed["dimension"]][0]


def fact_said(label: str | None) -> str | None:
    """keel-cloud 128 FR-13b (`FollowUpComposer.factSaid`): the tested fact as a statement said to the stranger -- the
    founder's label in the second person, no closing full stop, its first letter lowered."""
    text = (label or "").strip()
    if not text:
        return None

    def person(m):
        w = m.group(1)
        out = {"they're": "you're", "they've": "you've", "they'd": "you'd", "they'll": "you'll", "their": "your",
               "theirs": "yours", "themselves": "yourself"}.get(w.lower(), "you")
        return out[:1].upper() + out[1:] if w[:1].isupper() else out
    about_them = bool(re.match(r"(?i)^(?:their|they)\b", text))
    text = _THIRD.sub(person, text)
    if about_them:
        # keel-cloud 131 FR-3: a label about them (*Their phone was with them and online*) said to the person whole
        text = re.sub(r"\bthem\b", "you", text)
    while text.endswith("."):
        text = text[:-1]
    return fake_lower(text)


def fact_said_back(code: str | None, pick: str | None, said: str) -> str:
    """keel-cloud 174 FR-3 (`FollowUpComposer`, spec 115 FR-1): a fact answered No or the third, said back as the fact --
    *You said no to this: {fact}.*; the registry's third said as picked, held to the spoken cap, *You said only with help
    or approval: {fact}.* (*... to this:* ran past 20 words on 13-aircaps); a stored *Partly* (an item locked before 174)
    keeps 128's *You said only partly to this: {fact}.* -- each closing *What got in the way?*."""
    if code != "only_with_help":
        lead = "You said no to this: "
    elif pick == "Partly" or pick is None:
        lead = "You said only partly to this: "
    else:
        lead = f"You said {fake_lower(pick.strip())}: "
    return f"{lead}{said}. What got in the way?"


_HAD = re.compile(r"^(?:did you have|you had|you have|do you have)\s+(?:(?:a|an|any|the)\s+)?(.+)$")


def had_no(condition: str | None) -> str | None:
    """keel-cloud 129 FR-6 (`ItemFrames.hadNo`): a have-fact answered No said back as the fact -- *You said you had no
    bank account in your own name. What do you use instead?* -- or None where the condition is no have-fact."""
    text = (condition or "").strip()
    while text.endswith(("?", ".")):
        text = text[:-1].strip()
    if not text:
        return None
    text = fact_said(text) or ""
    match = _HAD.fullmatch(text)
    if not match:
        return None
    thing = re.sub(r"\s+(?:that|which)\s+you\s+.*$", "", match.group(1)).strip()
    if re.match(r"(?i)^(?:your|my|their|his|her|its|our)\s", thing):
        # keel-cloud 131 FR-3 (`ItemFrames.hadNo`): a thing that is someone's -- *You said you didn't have your phone with
        # you*, never *you had no your phone ...* (AirCaps)
        own = re.sub(r"(?i)\s+(?:and|during|when|while|whenever)\s+.*$", "", thing).strip()
        return f"You said you didn't have {own}. What do you use instead?"
    return f"You said you had no {thing}. What do you use instead?" if thing else None


#: keel-cloud 129 FR-3 (`FollowUpComposer.SAID_AS_SPOKEN`): the rungs whose text is their spoken line where the filled
#: text would paste the pick or the benefit labels -- a follow-up composed whole for the answer keeps its words.
SAID_AS_SPOKEN = ("problem.current_solution_satisfaction", "solution.relative_advantage",
                  # keel-cloud 131 FR-7: Importance's text pasted the picks and the own item -- it is its spoken line
                  "problem.importance")


def from_served(question: str | None, pick: str | None) -> str | None:
    """keel-cloud 128 FR-14 (`FollowUpComposer.fromServed`): Compatibility's follow-up from the served question where the
    condition gives no clause -- *You said no to this: did the list come straight out of the EMR? What got in the way?*"""
    asked = (question or "").strip()
    if not asked:
        return None
    at = asked.find(". ")
    if asked.startswith("Think ") and at > 0:
        asked = asked[at + 2:].strip()
    asked = re.sub(r"^On your last [^,]+, ", "", asked)
    if not asked:
        return None
    said = "no" if pick is None else fake_lower(pick.strip())
    return f"You said {said} to this: {asked[:1].lower() + asked[1:]} What got in the way?"


def served_idea_name(interview: dict) -> str | None:
    """The idea's name as the interview serves it (`Reveal.what`, *Imagine {name}.*: keel-cloud 090) -- the
    corridor's `ideaName` the composer says."""
    what = ((interview.get("reveal") or {}).get("what") or "").strip()
    m = re.match(r"^Imagine (.+?)\.?$", what)
    return m.group(1).strip() if m else None


def follow_up_question(entry, picks: list, link: str, interview: dict, token: str, first=(), *,
                       line: int | None = None, asked=(), stem: tuple[str, bool] | None = None) -> dict | None:
    """Spec 051 FR-2 / judgement call 1: the follow-up the cloud's route returns for these picks on this link -- the
    stem by the harness's own walk (spec 064 FR-7, keel-cloud 118: the deciding lines `first` taken first, an answer a
    second stem is asked on owed too; spec 075, keel-cloud 142 FR-1: a rung in `asked` passed over) and its text filled
    the way `FollowUpComposer` fills it, from the served labels (`interview`, the person's own link) and the founder's
    own words -- or None. `stem` composes that one stem's question instead (`follow_up_plan`). The walk holds the
    route's answer and the screen to it."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    from instructions import spoken as spoken_mod                     # noqa: PLC0415

    served = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    if stem is None:
        stem = fake.first_stem(picks, founder_side(entry, line=line), link, b2b=is_b2b(entry), served=set(served),
                               first=first, asked=asked)
    if stem is None:
        return None
    rung, also = stem
    item = served.get(rung) or {}
    labels = {o.get("optionId"): o.get("label") for o in item.get("options") or []}
    label = lambda code: labels.get(option_id(token, rung, code))  # noqa: E731
    pick = next((p for p in picks if p.dimension == rung), None)
    codes = list(pick.codes) if pick else []
    name = served_idea_name(interview) or _typed_idea_name(entry)
    # keel-cloud 154 FR-1 (`FollowUpComposer.lockValues`): {job}, {solution_name}, {occasion} and the lock's words on
    # every rung, either stem; then the person's
    values: dict[str, str | None] = lock_values(entry, interview, rung,
                                                label(founder_side(entry).importance_item)
                                                if rung == "problem.importance" else None)
    if also:
        pass
    elif rung == "problem.importance":
        values["{their_picks}"] = fake.joined([label(c) for c in codes], "and")
    elif rung == "problem.current_solution_satisfaction":
        values["{their_answer}"] = fake.lower(label(codes[0]) if codes else None)
    elif rung == "solution.compatibility":
        # keel-cloud 126 (FR-5b, `ItemFrames.couldNot`): "You said you couldn't {condition}" -- the tested item's
        # stranger face (`asked`, else its label) as the verb phrase after "couldn't"; "always ..." where they read
        # Only sometimes (123 FR-8), "... without help or approval" where they read Only with help or approval; the
        # composer's "do that" where the face has none of the shapes
        tested = entry.tested("solution.compatibility") or {}
        condition = could_not(tested.get("asked") or tested.get("label"))
        if condition is None:
            # keel-cloud 131 FR-10: a condition of their thing said back as the person's
            condition = thing_could_not(tested.get("asked") or tested.get("label"))
        picked = (label(codes[0]) or "").lower() if codes else ""
        if condition is not None and codes and codes[0] == "only_with_help":
            condition = "always " + condition if picked.startswith("only sometimes") \
                else condition + " without help or approval"
        values["{condition}"] = condition
        values["{would}"] = ("only work sometimes" if picked.startswith("only sometimes")
                             else "only work with help" if picked.startswith("only with help") else "not work")
        # keel-cloud 128 FR-13b: a fact answered No or Partly is said back as the fact, never "you couldn't ..."; 174
        # FR-3 (spec 115 FR-1): a fact is served the registry's four since 174, so the item is a fact by its tested
        # condition (`spoken.is_fact`, the lock's `ItemFrames.fact`) as well as by a stored *Partly*
        code = codes[0] if codes else None
        fact = label("only_with_help") == "Partly" or spoken_mod.is_fact(tested.get("asked") or tested.get("label"),
                                                                          tested.get("label"))
        said = fact_said(tested.get("label")) if fact and code in ("only_with_help", "no") else None
        if said:
            values[WHOLE_TEXT] = fact_said_back(code, label(code), said)
        # keel-cloud 129 FR-6: a have-fact answered No is said back as the fact (Karsa's bank account)
        if code == "no" and fact:
            had = had_no(tested.get("asked") or tested.get("label"))
            if had:
                values[WHOLE_TEXT] = had
        # keel-cloud 128 FR-14: with no clause to say "you couldn't" of, the served question is quoted
        if values["{condition}"] is None and WHOLE_TEXT not in values and item:
            quoted = from_served(item.get("question") or item.get("text"), label(code))
            if quoted:
                values[WHOLE_TEXT] = quoted
    elif rung == "solution.relative_advantage":
        # spec 089 FR-4 (keel-cloud 159): no benefit is named -- the scale's *worse* is said as worse
        if codes[:1] == ["worse"]:
            # keel-cloud 128 FR-16: the follow-up quotes the pick that was made (Walter picked worse)
            values[WHOLE_TEXT] = (f"You said {fake.named(name)} would have made things worse. "
                                  "What would have helped instead?")
    elif rung == "commercial.buyer_payer_alignment":
        # keel-cloud 128 FR-19: asked about this purchase at the founder's price, followed up in its tense; 154 FR-2:
        # naming it
        if str(item.get("question") or item.get("text") or "").startswith("Could you sign off on "):
            values[WHOLE_TEXT] = f"Who would have to agree to {fake.named(name)}, and what would they need to see?"
    elif rung == "commercial.price":
        values["{band}"] = fake.WOULD_NOT_PAY_BAND if codes[:1] == [fake.WOULD_NOT_PAY] else \
            fake.lower(label(codes[0]) if codes else None)
        # keel-cloud 130 FR-7 (`FollowUpComposer.priceSaidBack`): composed whole, so text and spoken line are one
        # wording -- *below {the price shown}*, the band said back (the chain's up-front pick first), else *low*; never
        # the registry's *below what we asked* where no price was shown (the would-not-pay sentence still comes first)
        values[WHOLE_TEXT] = fake.price_said_back(item.get("question") or item.get("text"), values["{band}"], name)
    if rung == "commercial.purchase_friction":
        # keel-cloud 128 FR-12: asked about this purchase, followed up in its tense -- on the long purchase's second
        # stem too (`FollowUpComposer.values` runs for either stem; S-006 and S-007 on the 129 build: *What would take the
        # time?*, said as it reads)
        stem = str(item.get("question") or item.get("text") or "")
        if stem.startswith("If ") and " bought " in stem and codes:   # "If you bought …", "If your terminal bought …"
            # keel-cloud 154 FR-2: the purchase named, never *it*
            values[WHOLE_TEXT] = f"What would take the time in buying {fake.named(name)}?" if codes[0] == "yes_long" \
                else f"What would slow down buying {fake.named(name)}, if anything?"
    whole = values.pop(WHOLE_TEXT, None)
    # keel-cloud 154 FR-1: the spoken line is filled too -- the project's words, as the clip says them
    filled = fake.spoken_filled(rung, values, also=also)
    text = whole if whole is not None else fake.fill(rung, values, also=also)
    # keel-cloud 129 FR-3: Current solution's and Relative advantage's text is their spoken line (the filled text pasted
    # the pick or the benefit labels); a text composed whole keeps its words
    if whole is None and not also and rung in SAID_AS_SPOKEN:
        text = filled
    would_not_pay = rung == "commercial.price" and codes[:1] == [fake.WOULD_NOT_PAY] and not also
    if would_not_pay:
        # keel-cloud 126 FR-6a / 154 FR-2 (`FollowUpComposer.wouldNotPayText`): its own sentence, the idea named
        text = fake.would_not_pay_text(name)
    # keel-cloud 128 FR-12: a follow-up composed whole for the answer given is said as it reads (129: and the would-not-pay)
    # keel-cloud 131 FR-10 (`FollowUpComposer.ask`'s `saidBack`): a Compatibility follow-up that says its condition
    # back is spoken as it reads, on every path (ability, fact, partly, no) -- not the registry's *that step would be hard*
    said_back = rung == "solution.compatibility" and not also and text != filled \
        and fake.FILL_DEFAULTS["{condition}"] not in text
    spoken = text if whole is not None or would_not_pay or said_back else filled
    return {"dimension": rung, "text": text, "spoken": spoken, "also": also}


def _typed_idea_name(entry) -> str | None:
    """The idea's name as keel-cloud stores it (`corridor.ideaName`), or None where the entry gives none."""
    try:
        return idea_name(entry)
    except VectorsScriptError:
        return None


def lock_values(entry, interview: dict | None, rung: str, founder_item: str | None = None) -> dict[str, str | None]:
    """keel-cloud 154 FR-1 (`FollowUpComposer.lockValues`): the values a rung's words take from the project alone, the same
    for everyone on a role's link -- `{occasion}`; `{job}`, the context's job said whole as an -ing phrase
    (`job_gerund`); `{solution_name}`, the idea's name as typed; and per rung the founder's own Importance item as served
    (`founder_item`, else the saved list's own item), the tested effort and Commitment's step as -ing phrases
    (`SpokenCap.gerund` of the label lowered), the smaller step, and (keel-cloud 161) Current solution's `{phrase}` as
    the question says it (`said_phrase`). A value with no words is None (its default is read)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    interview = interview or {}
    values: dict[str, str | None] = {"{occasion}": interview.get("occasion"),
                                     "{job}": job_gerund(_ctx(entry).get("job")),
                                     "{solution_name}": served_idea_name(interview) or _typed_idea_name(entry)}
    if rung == "problem.importance":
        own = founder_item
        if own is None:
            saved = entry.founder_list("problem.importance") or {}
            own = ((saved.get("items") or [{}])[0] or {}).get("label")
        values["{founder_item}"] = fake.lower(own)
    elif rung == "solution.adoption_friction":
        effort = founder_follow_up_words(entry)["{effort}"]
        values["{effort}"] = gerund(fake.lower(effort.strip())) if effort and effort.strip() else None
    elif rung == "problem.current_solution_satisfaction":
        # spec 093 FR-2 (keel-cloud 161 T003, `FollowUpComposer.lockValues`): `{phrase}`, the locked phrase as the
        # question says it (`ItemFrames.said`: a stored *your way of ...* read bare)
        values["{phrase}"] = said_phrase((entry.founder_list("problem.current_solution_satisfaction") or {}).get("phrase"))
    elif rung == "commercial.commitment":
        step = (entry.tested("commercial.commitment") or {}).get("label")
        values["{step}"] = gerund(fake.lower(step.strip())) if step and step.strip() else None
        smaller = smaller_step(entry)
        values["{smaller_step}"] = the_step(smaller) if smaller else None
    return values


def follow_up_clip(entry, interview: dict | None, rung: str, *, also: bool = False) -> str:
    """keel-cloud 154 FR-1 (`FollowUpComposer.clip`): one rung's spoken line as the clip recorded at the lock says it --
    the project's words filled -- the same words `GET interview`'s `followUps[].spoken` serves for that rung."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    return fake.spoken_filled(rung, lock_values(entry, interview, rung), also=also)


#: keel-cloud 128 (`FollowUpComposer.WHOLE_TEXT`): the values key a follow-up composed whole for the answer is carried
#: under -- said as it reads.
WHOLE_TEXT = "{whole_text}"


def follow_up_plan(entry, picks: list, link: str, interview: dict, token: str, first=(), *,
                   line: int | None = None, late=()) -> list[dict]:
    """Spec 075 (keel-cloud 142, keel-web 124): every follow-up the page asks these picks on this link, in the order
    asked -- each `follow_up_question`'s `{dimension, text, spoken, also}` and `on`, the served item's dimension it is
    asked right after, or None for the end's (both under *One more thing* since keel-web 126). At most two (`fake.asks`, the page's
    own walk over the served items' order and the served `followUps[]` rungs); `late` the items whose call the walk
    holds past the beat (their rung asked at the end instead)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415

    order = [i.get("dimension") for part in interview.get("parts") or [] for i in part.get("items") or []]
    rungs = [f.get("dimension") for f in interview.get("followUps") or []] or None
    founder = founder_side(entry, line=line)
    plan = fake.asks(picks, founder, order, link, b2b=is_b2b(entry), served=set(order), first=first, rungs=rungs,
                     late=late)
    out = []
    for asked in plan:
        question = follow_up_question(entry, picks, link, interview, token, first, line=line,
                                      stem=(asked["dimension"], asked["also"]))
        out.append({**question, "on": asked["on"]})
    return out


def the_step(step: str) -> str:
    """keel-cloud 118 `ItemFrames.theStep`: *the free trial* for *a free trial*; a step with its own article kept."""
    low = step.lower()
    if low.startswith("a "):
        return "the " + step[2:]
    if low.startswith("an "):
        return "the " + step[3:]
    return step if low.startswith(("the ", "your ", "their ", "my ")) else "the " + step


def _second_person(text: str) -> str:
    """`StrangerGrammar.secondPerson(text, false)`, narrowly: every *they* / *their* the stranger's own, case kept."""
    def person(m):
        w = m.group(1)
        out = {"they're": "you're", "they've": "you've", "they'd": "you'd", "they'll": "you'll", "their": "your",
               "theirs": "yours", "themselves": "yourself"}.get(w.lower(), "you")
        return out[:1].upper() + out[1:] if w[:1].isupper() else out
    return _THIRD.sub(person, text)


def _trim_end(text: str | None) -> str:
    out = str(text or "").strip()
    while out.endswith((".", "?")):
        out = out[:-1].strip()
    return out


#: keel-cloud 131 FR-4 (`SpokenCap.STEP_VERBS` beside a few of `StrangerGrammar.presentVerb`'s): verbs a step joins
#: with *and*, turned to -ing with the head.
STEP_VERBS = frozenset(("correct", "merge", "approve", "sign", "edit", "record", "speak", "share", "submit", "test",
                        "deploy", "delete", "remove", "keep", "fix", "talk", "narrate", "photograph", "film", "scan",
                        "label", "tag", "confirm", "check", "send", "save", "upload", "take", "read", "review", "open",
                        "run", "walk", "write", "wear", "pay", "use", "call", "book", "answer", "watch", "go", "make"))
#: The few irregular pasts a step is stored in (`StrangerGrammar.baseOfPast`, narrowly).
_PAST = {"wore": "wear", "took": "take", "spoke": "speak", "went": "go", "made": "make", "saw": "see", "got": "get",
         "wrote": "write", "ran": "run", "gave": "give", "sent": "send", "kept": "keep", "came": "come",
         "brought": "bring", "bought": "buy", "paid": "pay", "found": "find", "held": "hold", "left": "leave"}


def _base_of_past(word: str) -> str | None:
    """`StrangerGrammar.baseOfPastLoose`, narrowly: an irregular past by name, a regular one shorn of its *-ed*."""
    low = word.lower()
    if low in _PAST:
        return _PAST[low]
    if low.endswith("ied") and len(low) > 4:
        return low[:-3] + "y"
    if low.endswith("ed") and len(low) > 4:
        stem = low[:-2]
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
            return stem[:-1]                                         # stopped -> stop
        if stem.endswith(("at", "ur", "ar", "id", "ov", "iv", "ag", "rg", "ng", "us", "as", "ad", "ok")) \
                or stem.endswith(("rc", "dg", "rs", "nc", "ys", "ud", "ac")):
            return stem + "e" if not stem.endswith(("ng", "ok", "ys")) else stem
        return stem
    return None


def _ing(verb: str) -> str:
    """`SpokenCap.ing`: *take* -> *taking*, *run* -> *running*, *wore* -> *wearing* (a past to its base first)."""
    lower = verb.lower()
    if lower in _PAST:
        lower = _PAST[lower]
    if lower.endswith("ing") and len(lower) > 4:
        return lower
    if lower.endswith("ie"):
        return lower[:-2] + "ying"
    if lower.endswith("e") and not lower.endswith(("ee", "ye", "oe")) and len(lower) > 2:
        return lower[:-1] + "ing"
    if re.fullmatch(r"[^aeiou]*[aeiou][bdgmnprt]", lower) and len(lower) <= 4:
        return lower + lower[-1] + "ing"
    return lower + "ing"


def gerund(step: str) -> str:
    """keel-cloud 129 FR-2 / 131 FR-4 (`SpokenCap.gerund`): the founder's step as it followed *{Name} means* (since
    keel-cloud 171 no longer the frame's -- `adoption_statement` says the step in base form, spec 112 FR-1; the
    follow-up rungs' `{effort}` and `{step}` still read it) -- *Pay a
    verified seller they have never met* reads *paying a verified seller you have never met*; every verb joined by
    *and* in -ing (*taking short videos and talking over them*, *reading and correcting every draft*); a step stored as a
    question (*Would you speak the fix ...*) or a past statement (*you wore the glasses ... whenever you talked*) read
    as the step (*wearing the glasses ... whenever you talk*)."""
    text = _second_person(_trim_end(step))
    text = re.sub(r"(?i)^(?:would|will|could|can) you\s+", "", text, count=1)
    text = re.sub(r"(?i)^(you'd|you would|you will|you'll)\s+(have to\s+)?", "", text, count=1)
    text = re.sub(r"(?i)^(you\s+)?(have to|need to|had to|would have to)\s+", "", text, count=1)
    you = re.match(r"(?i)^you\s+([a-z]+)\b", text)
    if you and (you.group(1).lower() in _PAST or you.group(1).lower().endswith("ed")
                or you.group(1).lower() in STEP_VERBS):
        text = text[4:].strip()
    words = text.split()
    if not words:
        return text
    out = [_ing(words[0])]
    for i in range(1, len(words)):
        word, lower, before = words[i], words[i].lower(), words[i - 1].lower()
        turned = word
        if before == "and" and (i == 2 or lower in STEP_VERBS or lower in _PAST) and not lower.endswith("ing"):
            turned = _ing(lower)
        elif before in ("you", "they") and lower != "had" and (lower.endswith("ed") or lower in _PAST) \
                and _base_of_past(lower):
            turned = _base_of_past(lower)
        out.append(turned)
    return " ".join(out)


#: keel-cloud 154 (`SpokenCap.OBJECT_OPENERS`): the words an object opens on, which tell a verb after *and* from a noun.
OBJECT_OPENERS = frozenset(("the", "a", "an", "your", "their", "them", "it", "its", "his", "her", "our", "my", "every",
                            "each", "all", "any", "some", "this", "that", "these", "those", "up", "out", "down", "off",
                            "back"))


def job_gerund(job: str | None) -> str | None:
    """keel-cloud 154 FR-1 (`SpokenCap.jobGerund`): the context's job (a base-form verb phrase) said as an -ing phrase
    (Relative advantage's rung, *What would make {job} better for you*; since keel-cloud 161 the Current solution rung
    says the founder's phrase, `{phrase}`, not the job) -- `gerund`, then every verb joined by *and* before its own object in -ing too (*work out what the baby needs and
    settle the baby* -> *working out what the baby needs and settling the baby*), while a noun of a list after *and*
    stays as typed (*memory, GPUs and run time*). Whole, never shortened; None for none."""
    if job is None or not job.strip():
        return None
    words = gerund(_trim_end(job.strip())).split()
    typed = _second_person(_trim_end(job.strip())).split()
    if len(typed) == len(words):
        for i in range(2, len(words)):
            opens = i + 1 < len(words) and words[i + 1].lower() in OBJECT_OPENERS
            if words[i - 1].lower() == "and" and words[i].lower() != typed[i].lower() and not opens:
                words[i] = typed[i]
    for i in range(2, len(words) - 1):
        word = words[i].lower()
        if (words[i - 1].lower() == "and" and words[i + 1].lower() in OBJECT_OPENERS and re.fullmatch(r"[a-z]+", word)
                and not word.endswith("ing") and word not in OBJECT_OPENERS and not word.endswith("s")):
            words[i] = _ing(word)
    return " ".join(words)


def adoption_statement(asked: str | None, name: str | None, label: str | None = None) -> str | None:
    """Spec 112 FR-1 (keel-cloud 171 FR-4, FR-4b: `ItemFrames.adoptionFriction(asked, name, label)` at the lock, then
    `SpokenCap.held`): the served Adoption friction question -- *To use Karsa, you'd pay a verified seller you have
    never met. Would you do that, or not?* -- the stored clause in base form after *you'd* (`spoken.step`), a clause
    naming the capitalised idea where the founder's row does not said with *it* (`spoken.says_it`), named where a form of
    it fits 20 words (whole, without a phrase set off by commas, a question's step without its leading clause), else
    *To use it, ...* by the same give-way; past them all the lock gives way to the founder's row (`label`) in the same
    frame (`SpokenCap.plain`: named, *it* where the name takes it past 20), and past that to the plain *Would it fit the
    way you do things, or not?*. Was 130's *{Name} means {gerund}.*, None with no name (now *To use it*). None with no
    clause. keel-cloud's grammar check (`StrangerGrammar.fault`) is not mirrored, so a served stem it moved is a
    finding (`backtest.cloud_130`), never a stop."""
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    thing = _trim_end(asked)
    if not thing:
        return None
    idea = (name or "").strip() or None
    # the lock's call: the tested row's label, `""` where none is known (`RespondentItems.fromList`)
    composed = spoken_mod.adoption_friction(thing, idea, label or "")
    if _words(composed) <= STEM_MAX_WORDS:
        return composed
    row = _trim_end(label)
    if row:
        kept = spoken_mod.to_use(idea, spoken_mod.step(row))
        if idea is not None and _words(kept) > STEM_MAX_WORDS:
            kept = spoken_mod.to_use(None, spoken_mod.step(row))
        if _words(kept) <= STEM_MAX_WORDS:
            return kept
    return ADOPTION_PLAIN


#: keel-cloud `SpokenCap.PLAIN`'s Adoption friction frame: the question with nothing of the founder's pasted in.
ADOPTION_PLAIN = "Would it fit the way you do things, or not?"


#: keel-cloud 130 FR-10 (`ItemFrames.NAMED_STEP`): what a founder's step may name, with *the*, that the card has to have
#: introduced first.
_NAMED_STEP = re.compile(r"(?i)\bthe ((?:free |paid |first |money-back )?(?:trial|pilot|walkthrough|demo|session|"
                         r"onboarding call|setup call|test run|course|programme|program))\b")


def with_article(thing: str) -> str:
    """`WindowFrame.withArticle`: *a trial*, *an onboarding call*; a thing with its own article kept."""
    text = (thing or "").strip()
    low = text.lower()
    if low.startswith(("a ", "an ", "the ")):
        return text
    vowel = bool(low) and low[0] in "aeiou" and not low.startswith(("uni", "use", "usu", "eu", "one"))
    if low.startswith(("hour", "honest", "heir")):
        vowel = True
    return ("an " if vowel else "a ") + text


def commitment_plain(step: str) -> str:
    """`ItemFrames.commitment(step)`: *If it were ready today, would you {step}, or not?*"""
    return f"If it were ready today, would you {fake_lower(step.strip())}, or not?"


def commitment_stem(step: str | None, name: str | None, card: str | None) -> str | None:
    """keel-cloud 130 FR-10 (`ItemFrames.commitment(step, name, card)`): the step is named before it is asked -- a step
    naming *the trial* (a pilot, a walkthrough, ...) the card does not name opens on one clause introducing it, *Issen
    starts with a trial. Would you pay for one month after the trial, or not?* (the *If it were ready today* opener goes
    where the two would pass 20 words); a step that introduces its own (*a money-back pilot*), one the card names, or no
    card asks the plain stem."""
    if step is None or not step.strip():
        return None
    plain = commitment_plain(step)
    if not card or not card.strip():
        return plain
    named = _NAMED_STEP.search(step)
    if not named:
        return plain
    thing = named.group(1).lower()
    head = re.sub(r"^(?:free|paid|first|money-back) ", "", thing)
    if re.search(r"\b" + re.escape(head) + r"\b", card.lower()):
        return plain
    idea = (name or "").strip() or "It"
    bridge = f"{idea} starts with {with_article(thing)}."
    for asked in (plain, f"Would you {fake_lower(step.strip())}, or not?"):
        stem = f"{bridge} {asked}"
        if _words(stem) <= STEM_MAX_WORDS:
            return stem
    return plain


#: keel-cloud 130 FR-6 (`RespondentQuestionsRules.withoutNegativeClause`).
_NEGATIVE_TAIL = re.compile(r"(?i)^(.+?),?\s+(?:and|but)\s+(?:not|no|never|nobody|nothing|none)\b.*$")
_DETERMINERS = ("the", "a", "an", "their", "our", "its")


def own_subject_event(asked: str | None) -> str | None:
    """keel-cloud 130 FR-6 (`RespondentQuestionsRules.ownSubjectEvent`): an occasion clause in question order with a
    subject of its own -- *did a booking call come in on your shift* -- as the gate's clause, *a booking call come in on
    your shift*, the person's own time kept (130 judgement call 1); None for *did you ...* or any other shape. Narrowly:
    the subject is read as a determiner and a noun before the verb (`WindowFrame.subjectLed`'s present-verb list is not
    mirrored)."""
    text = str(asked or "").strip()
    low = text.lower()
    if not low.startswith("did ") or low.startswith("did you "):
        return None
    clause = text[4:].strip()
    words = clause.lower().split()
    return clause if len(words) > 2 and words[0] in _DETERMINERS else None


def without_negative_clause(circumstance: str | None) -> str | None:
    """keel-cloud 130 FR-6 (`RespondentQuestionsRules.withoutNegativeClause`): the circumstance cut before the negative
    clause it ends on -- Codyco's *booking calls come in on every shift, after hours, at peak and on holidays, and not
    every one gets answered* reads *booking calls come in on every shift, after hours, at peak and on holidays*; None
    where there is none, or fewer than three words stand before it."""
    if circumstance is None:
        return None
    cut = _NEGATIVE_TAIL.fullmatch(circumstance.strip())
    return cut.group(1).strip() if cut and _words(cut.group(1)) >= 3 else None


#: keel-cloud 131 FR-1 (`RespondentQuestionsRules.ORGANISATION`): a subject that is the person's organisation, said *you*.
_ORGANISATION = re.compile(r"^(?:the|your|their|our|a|an)\s+(?:[a-z-]+\s+)?(?:company|team|business|startup|firm|hotel|"
                           r"organisation|organization|department|plant|agency|practice|clinic|school|shop|store|group|"
                           r"terminal|site|contractor|utility|lab|office|restaurant|venue|employer)$")
_SUBJECT_ADVERBS = ("still", "already", "just", "often", "always", "usually", "sometimes", "again")
#: The present verbs a back-test circumstance opens its event on (narrowly: `StrangerGrammar.presentVerb`'s list is not
#: mirrored), by their base.
_EVENT_VERBS = frozenset(("come", "go", "decide", "start", "arrive", "break", "fail", "ring", "sit", "land", "need",
                          "run", "open", "close", "stop", "crash", "show", "happen", "get", "send", "ship", "call",
                          "book", "drop", "miss", "turn", "end", "finish", "walk", "pay", "move", "raise", "hit"))
_STOPS = ("and", "but", "until", "because", "unless", "that", "which", "who", "so", "or")


def _present_base(word: str) -> str | None:
    """`RespondentQuestionsRules.presentBase`, narrowly: *decides* -> *decide*, *goes* -> *go*, *starts* -> *start*."""
    low = word.lower()
    if low.endswith("oes") and low[:-2] in _EVENT_VERBS:
        return low[:-2]
    if low.endswith("ies") and low[:-3] + "y" in _EVENT_VERBS:
        return low[:-3] + "y"
    if low.endswith("es") and low[:-2] in _EVENT_VERBS:
        return low[:-2]
    if low.endswith("s") and low[:-1] in _EVENT_VERBS:
        return low[:-1]
    return None


def first_verb_phrase(clause: str, keep: int) -> str:
    """keel-cloud 131 FR-1 (`RespondentQuestionsRules.firstVerbPhrase`): the clause cut at its first verb phrase -- a
    comma, a second clause, *until*, *because*, a relative *that* / *which* / *who* -- after its first `keep` words."""
    out = []
    for i, word in enumerate(clause.strip().split()):
        if i >= keep and word.lower() in _STOPS:
            break
        if i >= keep - 1 and word.endswith(","):
            out.append(word[:-1])
            break
        out.append(word)
    return re.sub(r"[,;:]$", "", " ".join(out)).strip()


def circumstance_event(circumstance: str | None) -> str | None:
    """keel-cloud 131 FR-1 (`RespondentQuestionsRules.circumstanceEvent`), narrowly: the founder's circumstance as the
    occasion's event said to the person -- the trailing negative cut, a compound on the occasion's state giving its
    second clause (*a call's body-cam footage*), the subject and its verb read, the clause cut at its first verb
    phrase; an organisation said *you* (*decide where cash from a raise would sit*), a thing kept with *the* said
    *your* (*your agent in production start failing on real inputs*, *a machine on your line go down*), a bare plural
    *a* {one} (*a booking call come in on your shift*), *every* {noun} *your* {noun}. None where no subject and event
    verb are read (a state: *is too fast*, *are due*) -- the mirror knows only `_EVENT_VERBS`."""
    if not circumstance or not circumstance.strip():
        return None
    text = re.sub(r"(?i)^when\s+", "", circumstance.strip().rstrip("."))
    cut = without_negative_clause(text)
    text = cut or text
    possessor = None
    state = re.match(r"(?i)^(.+?)\s+(?:is|are)\s+(?:over|done|finished|complete|ended)\s*,?\s+and\s+(.+)$", text)
    if state:
        possessor, text = state.group(1).strip(), state.group(2).strip()
    tokens = text.split()
    if len(tokens) < 2:
        return None
    verb_at, plural = -1, False
    if tokens[0].lower() in ("they", "you"):
        verb_at = 1
    else:
        for i in range(1, len(tokens)):
            word = re.sub(r"[,.;:]$", "", tokens[i].lower())
            if word in _SUBJECT_ADVERBS:
                continue
            if word in ("has", "have", "is", "are"):
                verb_at, plural = i, word in ("have", "are")
                break
            nxt = tokens[i + 1].lower() if i + 1 < len(tokens) else ""
            if _present_base(word) and not (nxt in _EVENT_VERBS):
                verb_at = i
                break
            if word in _EVENT_VERBS and tokens[i - 1].lower().endswith("s") and not tokens[i - 1].lower().endswith("ss"):
                verb_at, plural = i, True
                break
    if verb_at < 1:
        return None
    subject = " ".join(t for t in tokens[:verb_at] if t.lower() not in _SUBJECT_ADVERBS)
    verb = tokens[verb_at].lower()
    rest = " ".join(tokens[verb_at + 1:])
    low_subject = subject.lower()
    person = low_subject in ("they", "you") or bool(_ORGANISATION.match(low_subject))
    passive = re.match(r"(?i)^to be ([a-z]+)\b\s*(.*)$", rest)
    if verb in ("has", "have") and passive:
        base = _base_of_past(passive.group(1))
        if base is None or person:
            return None
        thing = subject
        if possessor:
            owner = possessor + ("'" if possessor.endswith("s") else "'s")
            thing = re.sub(r"(?i)^(its|their)\s+", owner + " ", thing)
        thing = re.sub(r"(?i)^their\s+", "your ", thing)
        said = f"have to {base} {thing}" + (f" {passive.group(2).strip()}" if passive.group(2).strip() else "")
        return first_verb_phrase(said, 3 + len(thing.split()))
    if verb in ("is", "are", "has", "have"):
        return None
    base = verb if (person and verb_at == 1 and tokens[0].lower() in ("they", "you")) or plural else _present_base(verb)
    if base is None:
        return None
    wh = re.search(r"(?i)\b(where|what|whether|which|how|when)\b((?:\s+[a-z'-]+){1,6}?)\s+([a-z]+s)\b", rest)
    if wh and _present_base(wh.group(3)):
        rest = rest[:wh.start(3)] + "would " + _present_base(wh.group(3)) + rest[wh.end(3):]
    rest = re.sub(r"(?i)\bevery\s+(?=[a-z])", "your ", rest)
    rest = re.sub(r"\bcan\b", "could", re.sub(r"\bwill\b", "would", rest))
    if person:
        return first_verb_phrase(_second_person(base + (f" {rest}" if rest else "")), 1)
    if low_subject.startswith("the "):
        thing = "your " + subject[4:]
    elif not re.match(r"^(a|an|your|their|our|its|this|that|one)\s", low_subject) and low_subject.endswith("s") \
            and not low_subject.endswith("ss"):
        one = subject[:-3] + "y" if subject.endswith("ies") else subject[:-1]
        thing = with_article(one)
    else:
        thing = subject
    thing = re.sub(r"(?i)\s(on|in|at|of|from)\s+the\s+", r" \1 your ", thing)
    thing = re.sub(r"(?i)^their\s+", "your ", thing)
    return first_verb_phrase(f"{thing} {base}" + (f" {rest}" if rest else ""), len(thing.split()) + 1)


#: keel-cloud 170 FR-3b (spec 110 FR-2): *any* and *some* open a subject of their own too.
_SUBJECT_LED = ("the", "a", "an", "their", "our", "its", "every", "each", "your", "any", "some")


def subject_led(clause: str) -> str:
    """`WindowFrame.subjectLed`, narrowly (131 FR-1 T003): a clause opening on a determiner has a subject of its own and
    is framed *did {clause}*; else *did you {clause}*."""
    words = clause.split()
    return clause if len(words) > 2 and words[0].lower() in _SUBJECT_LED else f"you {clause}"


def gate_from_circumstance(window: Window, circumstance: str | None) -> str | None:
    """keel-cloud 131 FR-1's gate on the circumstance's event (`WindowFrame.gate` over `circumstanceEvent`), or None."""
    clause = circumstance_event(circumstance)
    return f"In the last {window_words(window)}, did {subject_led(clause)}?" if clause else None


def frequency_held(window: Window, clause: str) -> str:
    """keel-cloud 160 FR-2 (`WindowFrame.frequencyHeld`) on 131 FR-2: the served Frequency held to the spoken cap -- the
    whole (`frequency_served`); past 20 words the clause cut by its trailing phrases (the rightmost preposition first);
    else *... did that happen?*, the unit said (the grammar check is not mirrored). Keel-cloud 174 FR-5 (spec 115 FR-2)
    retired 160's judgement call 4, the unit dropped (*In the last 7 days, on how many did you ...?*,
    `frequency_unit_dropped`): the unit is never dropped."""
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    whole = frequency_served(window, clause)
    if _words(whole) <= STEM_MAX_WORDS:
        return whole
    frame = _words(whole) - _words(clause)
    cut = spoken_mod.cut_to_fit(clause, STEM_MAX_WORDS - frame)
    held = frequency_served(window, cut)
    return held if cut != clause and _words(held) <= STEM_MAX_WORDS else frequency_served(window, None)


def frequency_held_before160(window: Window, clause: str) -> str:
    """keel-cloud 160 judgement call 3 (`WindowFrame.frequencyHeldBefore160`): a Frequency stored before 160 is served
    in its own frame, held as 131 held it -- *On how many of those {n} {unit} did ...?*, the clause cut, else *... did
    that happen?*."""
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    lead = f"On how many of those {window_words(window)} did "
    whole = f"{lead}{subject_led(clause)}?"
    if _words(whole) <= STEM_MAX_WORDS:
        return whole
    frame = _words(whole) - _words(clause)
    cut = spoken_mod.cut_to_fit(clause, STEM_MAX_WORDS - frame)
    held = f"{lead}{subject_led(cut)}?"
    return held if cut != clause and _words(held) <= STEM_MAX_WORDS else \
        f"On how many of those {window_words(window)} did that happen?"


def gate_asks_the_job(entry, gate_question: str | None) -> bool:
    """keel-cloud 130 FR-6's fault, read on the wire: the gate fell to the job (*In the last 7 days, did you turn every
    guest who calls into a booking?*), which inverts the count -- the event comes first now."""
    job = _phrase(_ctx(entry).get("job"))
    if not job or not gate_question:
        return False
    job = job[:1].lower() + job[1:] if len(job) > 1 and not job[1].isupper() else job
    return gate_question.strip() == f"In {entry.window().words()}, did you {job}?"


#: keel-cloud 130 FR-8 (`ScreenResultApplier.QUALIFIER`): the parts of the founder's WHICH PEOPLE that qualify them.
QUALIFIER = re.compile(r"(?i)\b(not starting|or above|or more|at least|with no|without|already|beyond the|past the|"
                       r"no longer|level)\b|\b\d[\d,]*\s*(?:to|-|\u2013)\s*\d[\d,]*\b|"
                       r"\b(?:bank|banks|banking|run|runs|work|works) (?:with|on)\b")
_NEGATIVE_QUALIFIER = re.compile(r"(?i)\bnot (?:starting|beginning) (?:from|at) (?:zero|scratch)\b|"
                                 r"\bnot (?:complete |total |absolute )?beginners?\b")


def condition_from(part: str | None, before: str | None = None) -> str | None:
    """keel-cloud 130 FR-8 (`ScreenResultApplier.conditionFrom`, X12): one qualifier of the founder's people as a
    condition completing *Only people who ...* -- *not starting from zero* -> *are past the beginner stage*, *with no X*
    -> *have no X*, *departments of 10 to 200 officers* -> *work at a department with 10 to 200 officers*, *that bank
    with Mercury or Brex* -> *bank with Mercury or Brex*, *at intermediate level or above* -> *are at intermediate level
    or above*; None otherwise (145's amount, relative-clause and place branches and the cloud's last branch, a part
    opening on a present verb, are not mirrored). Since keel-cloud 149 FR-3 (spec 085 FR-2), in the cloud's order before
    the tool branch: a thing of the people's keeps its subject (*whose jobs run on Procore or ACC* -> *have jobs that run
    on Procore or ACC*, `qualifiers.thing_of_theirs`); 131's *at X that run Y* frame (`qualifiers.organisation_frame`);
    an organisation qualified by a participle or a relative clause, named in the part or in the founder's words said
    `before` it, draws that frame on its head noun (*..., banking with Mercury, Brex or similar* after *venture-backed
    startups ...* -> *work at a startup that banks with Mercury, Brex or similar*, `qualifiers.organisations_clause`) --
    so the tool branch draws only where the people are the subject."""
    if part is None or not part.strip():
        return None
    text = re.sub(r"(?i)^(?:who|that|which)\s+", "", part.strip(), count=1)
    if _NEGATIVE_QUALIFIER.search(text):
        return "are past the beginner stage"
    drawn = (qualifiers.thing_of_theirs(text) or qualifiers.organisation_frame(text)
             or qualifiers.organisations_clause(part.strip(), before))
    if drawn:
        return drawn
    without = re.search(r"(?i)\b(?:with no|without)\s+(.+)$", text)
    if without:
        return "have no " + without.group(1).strip()
    size = re.search(r"(?i)\b([a-z]+?)s\s+(?:of|with)\s+(\d[\d,]*\s*(?:to|-|\u2013)\s*\d[\d,]*\s+[a-z]+)", text)
    if size:
        return f"work at a {size.group(1).lower()} with {size.group(2).strip()}"
    tool = re.search(r"(?i)\b((?:bank|banks|run|runs|work|works) (?:with|on) .+)$", text)
    if tool:
        out = tool.group(1).strip()
        for plural, one in (("banks", "bank"), ("runs", "run"), ("works", "work")):
            out = re.sub(rf"(?i)^{plural}\b", one, out, count=1)
        return out
    level = re.search(r"(?i)\b(at (?:an? )?[a-z -]*?level(?: or (?:above|higher|more))?|at least .+|past the .+)$", text)
    if level:
        return "are " + level.group(1).strip()
    return None


def drawn_condition(which_people: str | None, segment: str | None = None) -> str | None:
    """keel-cloud 130 FR-8 (`ScreenResultApplier.drawnCondition`, X12): the condition code draws, past the repair turn,
    where the result writes none and the founder's people are qualified -- a negative qualifier first (the one the
    read-back loses), else the first qualifier that gives one; None where none does. Issen's *adults ... at intermediate
    level or above, not starting from zero* draws *are past the beginner stage*. Since keel-cloud 149 FR-3 the parts are
    `qualifiers.parts` (never inside a list: *banking with Mercury, Brex or similar* is one), each drawn with the words
    said before it in its own text (where an organisation it qualifies is named)."""
    parts: list[str] = []
    before: dict[str, str] = {}
    for text in (which_people, segment):
        said = ""
        for raw in qualifiers.parts(text or ""):
            part = raw.strip()
            before.setdefault(part, said)
            said += part + ", "
            if QUALIFIER.search(part):
                parts.append(part)
    parts.sort(key=lambda p: 0 if re.search(r"(?i)\b(not|no|without|never|no longer)\b", p) else 1)
    for part in parts:
        drawn = condition_from(part, before.get(part, ""))
        if drawn is not None:
            return drawn
    return None


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


#: Spec 089 FR-2 (keel-cloud 158 T003, contract 46): a Frequency answer counts from 1 -- a 0 after the yes is refused
#: 400 SHAPE_MISMATCH and nothing is stored. Corpus revision 19 records five people who answered 0 after a yes (158's
#: *What did not hold*); the corpus is never edited and the engine reads them as recorded, but the wire cannot carry
#: them. Spec 090 FR-3 (the founder, 2026-10-30, `quality/decisions.toml` D-2026-10-30-01 taken: "update the harness to
#: send 1"): each of the five is sent as the count 1 -- `{"scale": 1}` on the segmented control, 1 in the number box on
#: the long window -- the logical floor of a yes now that the control starts at 1; each still named in the scripted
#: person's notes and the journey's findings. (Spec 089 sent them as *I can't recall*, CANT_RECALL.) `(entry, person):
#: window` -- the window each was asked over, as 158 found them.
ZERO_SENT_AS_ONE = {("04-linerly", "Bruno Costa"): "12 MONTHS", ("04-linerly", "Dmitri Volkov"): "12 MONTHS",
                    ("04-linerly", "Gwen Price"): "12 MONTHS", ("05-paidly", "Petra Novak"): "3 MONTHS",
                    ("05-paidly", "Talia Ben-David"): "3 MONTHS"}
#: The decision the five were sent on.
ZERO_DECISION = "D-2026-10-30-01"


def zero_note(person: str, entry_id: str) -> str:
    """The note a 0 sent as 1 carries: who, what the file records, what is sent and why."""
    return (f"{person} ({entry_id}) recorded problem.frequency 0 after a yes; keel-cloud 158 counts from 1, so the walk "
            f"sends 1 (the founder's {ZERO_DECISION}: a yes followed by a count of 1 is the floor) -- the corpus is "
            "unchanged")


def _frequency_from_one(entry, person: str, picks: list) -> tuple[list, tuple]:
    """Spec 090 FR-3 (spec 089 FR-2's replay moved): a recorded Frequency below 1 (`registry.FREQUENCY_MIN`) sent as the
    count 1, and named. Only the five `ZERO_SENT_AS_ONE` names are expected; any other 0 is sent as 1 and named the
    same way (a back-test record the founder has not seen), never dropped silently."""
    import dataclasses                                                 # noqa: PLC0415
    out, notes = [], []
    for pick in picks:
        if pick.dimension == "problem.frequency" and pick.scale is not None and pick.scale < FREQUENCY_MIN:
            out.append(dataclasses.replace(pick, scale=FREQUENCY_MIN))
            notes.append(zero_note(person, entry.id))
        else:
            out.append(pick)
    return out, tuple(notes)


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


#: Spec 082 FR-1 (keel-cloud 133): the scopes whose project has no COMMERCIAL_B2B kind -- the B2B link is the money
#: study's, so a walk under one of these sends the PRIMARY people alone.
PRIMARY_ONLY_SCOPES = ("PROBLEM", "SOLUTION")

#: Spec 101 FR-2 (keel-cloud 133 FR-4, 139): the scopes whose project on a B2B entry has no PRIMARY kind -- money alone,
#: where someone else decides, offers the decision-maker's link only (the register's `kinds` is COMMERCIAL_B2B alone),
#: so a walk under one of these sends the decision-makers alone. On a B2C entry the one FULL link takes everyone.
DECIDERS_ONLY_SCOPES = ("COMMERCIAL",)

#: Spec 101 FR-2: why a person of the entry is not on the study, by the rule that left them out.
NOT_ON_STUDY = {
    "PRIMARY_ONLY": "the money study's (keel-cloud 133): the project has no decision-maker's kind under this scope",
    "DECIDERS_ONLY": "money alone on a B2B entry: the decision-maker's link only (keel-cloud 133)",
    # spec 106 FR-2: the walk sends seven people a study (quality/cycle.toml `people`, `make quality-walk PEOPLE=`)
    "PAST_THE_CAP": "past the study's first {n} on the person's own link, in corpus order (spec 106 FR-2)",
}


def _scoped_people(entry) -> list:
    """Spec 082 FR-1 / spec 101 FR-2: the people the study's scope sends, before spec 106's cap."""
    people = list(entry.people())
    if scope_of(entry) in PRIMARY_ONLY_SCOPES:
        return [p for p in people if p.link != LINK_B2B]
    if scope_of(entry) in DECIDERS_ONLY_SCOPES and is_b2b(entry):
        return [p for p in people if p.link == LINK_B2B]
    return people


def study_people(entry) -> list:
    """Spec 082 FR-1: the entry's people the study under `entry.scope` sends a link to -- under PROBLEM or SOLUTION the
    PRIMARY people alone (the B2B people are the money study's, keel-cloud 133, and the project has no kind to send them
    on); under SOLUTION_COMMERCIAL and ALL every person, as before. Spec 101 FR-2: under COMMERCIAL on a B2B entry the
    decision-makers alone (keel-cloud 133 FR-4: the person's own link is not offered where the money is the whole study
    and someone else decides); under COMMERCIAL on a B2C entry every person, on the one FULL link.

    Spec 106 FR-2: with `entry.people_cap` (the walk's `PEOPLE=`, seven in a quality cycle) the people on the person's
    own link are the first that many of those, in corpus order; the decision-makers are never narrowed (a B2B money
    study sends all its deciders). No cap, everyone as before."""
    people = _scoped_people(entry)
    cap = getattr(entry, "people_cap", None)
    if not cap:
        return people
    own = [p.person for p in people if p.link != LINK_B2B][:int(cap)]
    return [p for p in people if p.link == LINK_B2B or p.person in own]


def not_on_study(entry) -> tuple[list[str], str | None]:
    """Spec 101 FR-2: the entry's people `study_people` leaves out, in corpus order, and why (`NOT_ON_STUDY`); ([], None)
    where the study sends everyone. Spec 106 FR-2: the people past the cap are named with its own reason, after the
    scope's where both leave someone out."""
    scoped = {p.person for p in _scoped_people(entry)}
    sent = {p.person for p in study_people(entry)}
    left = [p.person for p in entry.people() if p.person not in sent]
    if not left:
        return [], None
    why = []
    if any(p.person not in scoped for p in entry.people()):
        why.append(NOT_ON_STUDY["PRIMARY_ONLY" if scope_of(entry) in PRIMARY_ONLY_SCOPES else "DECIDERS_ONLY"])
    if any(name in scoped for name in left):
        why.append(NOT_ON_STUDY["PAST_THE_CAP"].format(n=entry.people_cap))
    return left, "; ".join(why)


def capped(entry) -> list[str]:
    """Spec 106 FR-2: the people the study's scope would send and its cap leaves out, in corpus order."""
    sent = {p.person for p in study_people(entry)}
    return [p.person for p in _scoped_people(entry) if p.person not in sent]


def person_inputs(entry) -> list[PersonInputs]:
    """Every person the study sends a link to (`study_people`: spec 082 FR-1), with their inputs; the follow-up lines are
    worked out over that list, so nothing downstream (the themes screen, `inputs.json`) names a person never sent."""
    people = []
    for person in study_people(entry):
        asked = set(plan_keys(entry, 1, person.link) + plan_keys(entry, 2, person.link)
                    + plan_keys(entry, 3, person.link)) if person.link == LINK_PRIMARY else \
            set(plan_keys(entry, 3, LINK_B2B))
        if person.link == LINK_PRIMARY and is_b2b(entry):
            asked -= set(plan_keys(entry, 3, LINK_PRIMARY))
        asked.discard("problem.prevalence")
        picks = [_pick(entry, key, raw) for key, raw in (person.picks or {}).items() if key in asked]
        picks, remapped = _served_commitment(entry, picks)
        picks, notes = _frequency_from_one(entry, person.person, picks)
        people.append(PersonInputs(
            person=person.person, link=person.link,
            recency=None if person.link == LINK_B2B or not person.in_segment else person.recency == "yes",
            story=person.story, anchor_chip=STORY_CHIPS.get(person.chip) if person.chip else None,
            picks=picks if person.in_segment else [],
            # spec 071 (keel-cloud 133 FR-4): the problem study asks no pilot question -- nobody can opt in
            pilot_opt_in=person.pilot_opt_in and person.in_segment and scope_of(entry) != "PROBLEM",
            anchoring=person.anchoring, in_segment=person.in_segment, remapped=remapped, notes=notes,
            gate=serves_gate(entry)))
    import dataclasses                                                 # noqa: PLC0415

    lines = follow_up_lines(entry, people)
    # spec 062 follow-up (2026-10-22): a back-test person who is owed a follow-up answers in their own words
    # (`Person.follow_up` in the file) where the file has them; the pooled line otherwise, as every golden entry does
    own = {p.person: p.follow_up for p in entry.people() if getattr(p, "follow_up", None)}
    rung_of = {p.person: p.follow_up_dimension for p in entry.people() if getattr(p, "follow_up_dimension", None)}
    # spec 068 FR-3 (keel-cloud 129 FR-12): a moved person's bare line written for the second yes belongs to Commitment
    rung_of.update({p.person: COMMITMENT_KEY for p in people if p.person not in rung_of
                    and moved_line_for_the_second_yes(entry, p) and own.get(p.person)})
    return [dataclasses.replace(p, follow_up=(own.get(p.person) if p.person in lines and own.get(p.person)
                                              else lines.get(p.person)),
                                follow_up_dimension=rung_of.get(p.person)) for p in people]


def moved_line_for_the_second_yes(entry, person) -> bool:
    """Spec 068 FR-3 (keel-cloud 129 FR-12): whether `person` is one of the people the revision-16 entry's header names
    (their Commitment `yes_after_trying` moved to `yes_start`) and the follow-up their file line was written for was
    the second yes -- the rung the revision-15 walk owed them first: their picks with Commitment read as r15 served it on
    a step-alone list (no conditional option, so *probably not*: `_served_commitment`), the static ladder. Such a line
    is Commitment's: typed only where the served follow-up lands on Commitment, never on another rung."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    import dataclasses                                                 # noqa: PLC0415
    if person.person not in getattr(entry, "commitment_moved", ()) or not getattr(person, "in_segment", True):
        return False
    if person.link != LINK_B2B and not person.recency:
        return False
    was = [dataclasses.replace(pick, codes=[NOT_SERVED_YES]) if pick.dimension == COMMITMENT_KEY else pick
           for pick in person.picks]
    return fake.first_rung(was, founder_side(entry), person.link, b2b=is_b2b(entry)) == COMMITMENT_KEY


def inside_inputs(entry, name: str) -> "PersonInputs":
    """Spec 067 FR-6: `name`'s inputs as a person inside the segment -- their recorded gate answer, story and picks --
    for a back-test page that serves no segment chip although the entry answers it NO (the chip is the model's to write,
    keel-cloud 120 FR-2): the walk goes on as the person the page can ask, and the difference is the journey's finding."""
    import dataclasses                                                 # noqa: PLC0415
    answers = [{k: v for k, v in raw.items() if k not in ("condition", "in_segment")} if raw.get("person") == name
               else raw for raw in entry.answers]
    return next(p for p in person_inputs(dataclasses.replace(entry, answers=answers)) if p.person == name)


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
