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
from harness import short_names as short_names_mod
from harness import working_rung as working_rung_mod
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
#: Spec 154 FR-0 (keel-cloud 229, `ScreenContextBuilder`): Importance's Answer draft (and its redraft) is handed the
#: study's clause -- `problem_clause` {went_wrong, hard_case?} -- beside the calibration keys wherever the problem card
#: wrote a `went_wrong`; the scripted executor matches a screen by its exact key set, so that job is a second screen in
#: the table (`CALIBRATION_QUESTIONS` + `problem_clause`) with its own entries in the script (`generate`). keel-cloud's
#: own `context-keys.json` export names the base set alone.
CALIBRATION_WITH_CLAUSE_SCREEN = "CALIBRATION_QUESTIONS+problem_clause"
PROBLEM_CLAUSE_KEY = "problem_clause"
#: Likewise keel-cloud 228 (FR-3): Current solution's Answer is sent as its two boxes (what they do, how well it goes),
#: handed to its draft as `answer_parts` beside `answers` -- a third key set for the same screen.
CALIBRATION_WITH_PARTS_SCREEN = "CALIBRATION_QUESTIONS+answer_parts"
ANSWER_PARTS_KEY = "answer_parts"
CURRENT_SOLUTION_KEY = "problem.current_solution_satisfaction"
#: A refused draft's redraft is the same job handed `repair` (the refusal's words) beside its keys: a fourth, fifth and
#: sixth key set -- answered with the same entries again, so a refusal the corpus did not foresee surfaces as
#: keel-cloud's own *refused twice* with the rule's words, never as LLM_UNAVAILABLE.
REPAIR_KEY = "repair"
REPAIR_SUFFIX = "+repair"
CALIBRATION_SCREENS = (CALIBRATION_SCREEN, CALIBRATION_WITH_CLAUSE_SCREEN, CALIBRATION_WITH_PARTS_SCREEN)


def calibration_screen_of(entry, only: str | None, *, with_clause: bool) -> str:
    """Spec 154 FR-0: which key set a calibration job is matched through -- Importance's draft with the clause,
    Current solution's with the two boxes, every other the export's own."""
    if with_clause and only == "problem.importance":
        return CALIBRATION_WITH_CLAUSE_SCREEN
    if only == CURRENT_SOLUTION_KEY:
        return CALIBRATION_WITH_PARTS_SCREEN
    return CALIBRATION_SCREEN
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
#: clause opens *you* / *your*, else *did you {clause}*; none of these does. Spec 123 FR-2 (keel-cloud 193 FR-2): E4
#: measures the Frequency question **served** (window first, `frequency_served`), so five gate clauses that framed it
#: past 20 words are the scripted writer's shorter ones, the verb and the object kept, the founder's clause unchanged
#: (01 *have to recount stock by hand after a mismatched delivery*, 02 *have to pull training completions into a
#: spreadsheet by hand*, 04 *lose time to a puncture riding to or from work*, 05 *wait beyond agreed terms to be paid
#: for an approved invoice*, 07 *wait at the supply yard for mulch for a job* -- 21 or 22 words served).
#: Spec 136 FR-3 (keel-cloud 212 FR-1, FR-3): the founder's clause is the strangers' too -- code turns it to the second
#: person (`WindowFrame.strangersEvent`: *their* *your*, the past verb's base after *did*) -- and is at most the words
#: the window's frame leaves (`wording.event_max_words`: 9, 8 on working days). Five of the seven were 10 or 11 words;
#: each is cut, the act and its object kept (Paidly's *to be paid* off; the whole clause is the entry's `went_wrong`,
#: `ACT_THAT_HURTS`); Lullaby's and Repeatline's stand. The second clause is the first as code turns it.
PROBLEM_CLAUSES = {
    "01-countly": ("had to recount stock after a mismatched delivery",
                   "have to recount stock after a mismatched delivery"),
    "02-compliancelog": ("had to pull training completions into a spreadsheet",
                         "have to pull training completions into a spreadsheet"),
    "03-lullaby": ("had to work out why their baby was crying", "have to work out why your baby was crying"),
    "04-linerly": ("lost time to a puncture riding to work", "lose time to a puncture riding to work"),
    "05-paidly": ("waited beyond agreed terms for an approved invoice",
                  "wait beyond agreed terms for an approved invoice"),
    # spec 141 FR-5 (keel-cloud 224 FR-2, its owed list): *by hand* is a verdict word E8 now refuses -- the harness's
    # own fixture reworded to the act alone (the corpus untouched); `went_wrong` is not held to the list and keeps it
    "06-repeatline": ("had to type a refill request in", "have to type a refill request in"),
    "07-mulchrun": ("waited at the supply yard for mulch", "wait at the supply yard for mulch"),
}

#: Spec 136 FR-3 (keel-cloud 212 FR-2, founder-lists.md): the two fields the founder's writer writes beside Prevalence's
#: `event`, read by code and never served -- `routine`, what every one of the entry's people does in the window whether
#: or not the problem struck (from the context's job and circumstance), and `went_wrong`, the one part of the problem a
#: person with it had to do or put up with (the founder's whole clause, before FR-3's cut). The event is written from
#: `went_wrong`, never the routine (E7), no cause, result, judgement or state packed in (E8) -- held by test.
ACT_THAT_HURTS = {
    "01-countly": ("check a delivery in against its invoice",
                   "had to recount stock by hand after a mismatched delivery"),
    "02-compliancelog": ("send the training-compliance report at quarter close",
                         "had to pull training completions into a spreadsheet by hand"),
    # spec 139 FR-2 (keel-cloud 216 judgement call 8, `VectorFixtures.WENT_WRONG`): the cloud's own words, so the
    # registry's own row *Knowing what the cry means* is the hurt on its verb (L37b)
    "03-lullaby": ("settle the baby", "did not know why the baby cried"),
    "04-linerly": ("ride to or from work", "lost time to a puncture riding to or from work"),
    "05-paidly": ("invoice an agency for finished work",
                  "waited beyond agreed terms to be paid for an approved invoice"),
    "06-repeatline": ("take a patient's call for a prescription refill", "had to type a refill request in by hand"),
    "07-mulchrun": ("fetch mulch from the supply yard for a job", "waited at the supply yard for mulch for a job"),
}


#: Spec 139 FR-2 (keel-cloud 216 FR-1, `no_sayer`, E9): one of the entry's people who did the day's work in the window
#: and truly answers No to the event, and what was different for them -- written beside `routine` and `went_wrong`,
#: read by code and never served. The golden seven's own (Lullaby's is the cloud's `VectorFixtures.NO_SAYER`); held to
#: E9 by test. A back-test entry records no `routine` / `went_wrong`, so its scripted no-sayer is `NO_SAYER_ANY`.
#: Spec 148 FR-2 (keel-cloud 238 FR-2): the no-sayer names its No by a word of `went_wrong`, denied or not -- Countly's,
#: Linerly's and Mulchrun's (set apart by nothing the hurt names) each gain the hurt's word, said after what was different
#: (the harness's own fixtures; the corpus untouched).
NO_SAYERS = {
    "01-countly": "a manager whose every delivery that week matched its invoice, so no stock was recounted",
    "02-compliancelog": "an HR manager whose system pulled the completions for them",
    "03-lullaby": "a parent who knew at once what the cry meant",
    "04-linerly": "a rider whose tyres held all the way, so no time was lost",
    "05-paidly": "a freelancer whose agency paid on the day the terms said",
    "06-repeatline": "a receptionist whose refill requests came in already typed",
    "07-mulchrun": "a crew lead whose mulch was loaded the moment they arrived, so nobody waited",
}
#: Spec 139 FR-2: the scripted no-sayer where the entry records none -- persona-free, no verb of any routine.
NO_SAYER_ANY = "one of them for whom it went right that time"


def no_sayer(entry) -> str:
    """Spec 139 FR-2 (keel-cloud 216 FR-1): the scripted writer's `no_sayer` beside Prevalence's event."""
    return NO_SAYERS.get(entry.id, NO_SAYER_ANY)


#: Spec 141 FR-2 (keel-cloud 219 FR-2, `hard_case` / `hard_case_theirs`): the moment the problem cost them, as a stranger
#: recalls it and as the founder's belief reads it -- optional fields the scripted Prevalence (and, in a study without
#: the problem's questions, the scripted problem card) carries where an entry holds them. **None today**: the golden
#: seven's walks keep today's Relative advantage item and belief (219's owed list: *without them the build serves
#: today's wording, no pin moves*), and a back-test entry's scripted `went_wrong` (`event_past`) is no hurt a hard case
#: could carry under H1. `(hard_case, hard_case_theirs)` by entry id.
HARD_CASES: dict[str, tuple[str, str]] = {}


def hard_cases(entry) -> dict:
    """Spec 141 FR-2: `{hard_case, hard_case_theirs}` where the entry holds them (`HARD_CASES`), else `{}`."""
    held = HARD_CASES.get(getattr(entry, "id", None))
    return {} if held is None else {"hard_case": held[0], "hard_case_theirs": held[1]}


def problem_clause(entry) -> dict:
    """Spec 141 FR-2 (keel-cloud 219 FR-1, `ProblemClause`): the six clause fields the scripted problem card writes in a
    study without the problem's questions (`serves_gate` and not `gate_counts`: the gate is the solution studies'
    uncounted anchor) -- `event` (the founder's clause, `event_past`), `routine` / `went_wrong` (`act_that_hurts`),
    `no_sayer`, and the hard cases where held -- only where the entry holds the founder's own clause
    (`PROBLEM_CLAUSES`: its turned form is the gate's `event_base`, so the gate the card's clause asks is the writer's
    and no E10 note is served); `{}` elsewhere, where the card writes `statement` and `offer_name` alone as before."""
    if entry.id not in PROBLEM_CLAUSES or gate_counts(entry) or not serves_gate(entry):
        return {}
    routine, went_wrong = act_that_hurts(entry)
    return {"event": event_past(entry), "routine": routine, "went_wrong": went_wrong, "no_sayer": no_sayer(entry),
            **hard_cases(entry)}


def act_that_hurts(entry) -> tuple[str, str]:
    """Spec 136 FR-3: `(routine, went_wrong)` for the entry's Prevalence -- the golden seven's own (`ACT_THAT_HURTS`);
    elsewhere the context's job and the clause `event_past` writes (a back-test entry records no founder clause, and no
    back-test entry is walked on the scripted runtime: FR-4 names those over the cap)."""
    if entry.id in ACT_THAT_HURTS:
        return ACT_THAT_HURTS[entry.id]
    return _phrase(_ctx(entry).get("job")) or "do the job", event_past(entry)


def event_past(entry) -> str:
    """Prevalence's clause for the founder (rules E1-E3): what happened, past tense, no time word -- since spec 064 the
    problem the founder counted (`PROBLEM_CLAUSES`), which keel-cloud 116 hands the gate's job as `problem`."""
    if entry.id in PROBLEM_CLAUSES:
        return PROBLEM_CLAUSES[entry.id][0]
    return f"had a time when {_ctx(entry)['circumstance']}"


#: keel-cloud 088 `E4` (measured from keel-cloud 160 to 192 on `frequencyMeasured`; since keel-cloud 193 FR-2 on the
#: question served; since keel-cloud 216 FR-3 on 174's frame, `frequency_served_before216`, the cap's own): framed, the gate ("In the last 3 months, did you ...?") and the Frequency
#: question ("In the last 3 months, in how many months did you ...?") are each at most 20 words. Where "have a time when
#: {circumstance}" frames longer, the referee's shorter clause, in the same register (COMPOSED).
GATE_EVENTS = {
    "02-compliancelog": "have the training-compliance report fall due at quarter close",
    "04-linerly": "get a tyre puncture on the way to or from work",
    "05-paidly": "wait to be paid for an invoice an agency had approved",
    "07-mulchrun": "fetch mulch from the supply yard for a job",
    # spec 123 FR-2 (keel-cloud 193 FR-2): the B2B test fixture's *have a time when the morning they cannot find their
    # keys* serves a 22-word Frequency question window first, so the scripted writer shortens it, verb and object kept
    "10-fixture-b2b": "fail to find your keys in the morning",
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


def prevalence_people(segment_core: str | None, condition: str | None, actor_plural: str | None) -> str:
    """Spec 133 FR-3 (keel-cloud 211 FR-3, `WindowFrame.people`; cycle 10, proposal 30: on all five studies the founder's
    question named the bare people and dropped the segment's qualifiers): the people the founder's Prevalence question
    counts -- the segment whole as the context card says it (`ContextSlots.segmentLine`: `qualifiers.segment`, core and
    condition), its closing stop or comma off and closed with a comma where a comma opens a part of it, so the event
    reads as the people's; the context's `actor_plural` only where it holds no segment."""
    line = qualifiers.segment(segment_core, condition) if segment_core and str(segment_core).strip() else None
    if not line or not line.strip():
        return (actor_plural or "").strip()
    people = re.sub(r"[.,;:]+$", "", line.strip())
    return people + "," if ", " in people else people


def founder_prevalence_question(window: Window, people: str, event: str | None) -> str:
    """Spec 133 FR-3 (keel-cloud 211 FR-3, `WindowFrame.prevalence(window, slots, event)`): the founder's Prevalence
    question, composed by code -- *In the last {window}, how many out of 10 {people} {event}?*, the people
    `prevalence_people` (Lullaby: *... parents of babies under six months in the US had to work out why their baby was
    crying?*), the event the writer's clause (`WindowFrame.clause`: no closing stop, a leading capital lowered unless
    it opens an acronym)."""
    text = " ".join(str(event or "").split())
    while text.endswith("."):
        text = text[:-1].strip()
    if len(text) > 1 and text[0].isupper() and not text[1].isupper():
        text = text[0].lower() + text[1:]
    return f"In the last {window_words(window)}, how many out of 10 {people.strip()} {text}?"


def who_answers(title: str | None, role: str | None, co_deciders=()) -> str:
    """Spec 133 FR-3 (keel-cloud 211 FR-8, `PersonaModel.whoAnswers`; cycle 10, proposal 2: Codyco's *who answers*
    option read *Director*, the last word of the founder's decider): the decider's option on the persona's *who
    answers* list (`respondentTypes[].label`, printed as served by keel-web) -- the whole title as typed, its first
    letter up (the role where none was typed), never a word of it; once Buyer and payer is saved, *, with {roles}
    agreeing*, each role on the saved list (*Nobody else* aside) with its *the* (`chain.the_role`), joined with *and*:
    *Hotel group revenue director, with the hotel's owner agreeing*."""
    from instructions import chain as chain_mod                        # noqa: PLC0415
    from instructions import corpus as corpus_mod                      # noqa: PLC0415
    said = (title or "").strip() or (role or "").strip()
    whole = said[:1].upper() + said[1:]
    others = [chain_mod.the_role(r.strip()) for r in co_deciders or () if r and r.strip()]
    return f"{whole}, with {corpus_mod.joined(others)} agreeing" if others else whole


def window_first(window: Window) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.windowFirst`, spec 139 FR-2; cycle 13's Palus, the card's named pitfall): the
    Frequency frames' opening -- the unit said once, in the window phrase: *On how many of the last 3 months *, *On how
    many of the last 5 working days *."""
    return f"On how many of the last {window_words(window)} "


def window_first_before216(window: Window) -> str:
    """keel-cloud 174 FR-5 (`WindowFrame.windowFirstBefore216` since 216): the opening from 174 to 215 -- *In the last 3
    months, in how many months *, *In the last 5 working days, on how many days * -- read on stored items and the frame
    the event's cap and E4 measure a clause on (`RespondentQuestionsRules.measuredFrequency`), never composed."""
    return f"In the last {window_words(window)}, {counted_in(window)} how many {short_unit(window)} "


def frequency_served(window: Window, event: str | None) -> str:
    """keel-cloud 160 FR-2 (`WindowFrame.frequencyRespondent(window, event)`): the window first and plainly, then the
    gate's one event. Spec 139 FR-2 (keel-cloud 216 FR-3): the unit said once, in the window phrase -- *On how many of
    the last 7 nights did you have to work out why your baby was crying?*; with no clause *On how many of the last 7
    nights did that happen?* (174 to 215: `frequency_served_before216`)."""
    lead = f"{window_first(window)}did "
    return f"{lead}{subject_led(event)}?" if (event or "").strip() else f"{lead}that happen?"


def frequency_served_before216(window: Window, event: str | None) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.frequencyRespondentBefore216`): the frame as it read from 174 to 215 -- *In the
    last 7 nights, on how many nights did you ...?*, *in how many* weeks and months, a two-word unit short the second
    time -- read on a stored item (served in it, as its recorded clip says it) and the frame E4 and `fitted` measure a
    clause on, so the cap keeps 212's numbers."""
    lead = f"{window_first_before216(window)}did "
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
    fault = e4_fault(window_of(entry), event)
    if fault:
        raise VectorsScriptError(f"{entry.id}: {fault} (the scripted writer's shorter clause goes in GATE_EVENTS)")
    return event


def e4_fault(window: Window, event: str) -> str | None:
    """Spec 123 FR-2 (keel-cloud 193 FR-2, `RespondentQuestionsRules.gate`): framed, the gate and **the Frequency
    question served** (`frequency_served`, `servedFrequency`) are each at most 20 words; past the cap the breach names
    the longer and asks the writer to shorten the clause, keeping its verb and its object -- the clause is never cut
    (`frequency_held`'s cut is an item stored before 193's). Spec 139 FR-2 (keel-cloud 216 FR-3): the Frequency question
    measured on the frame the cap was set on (174's, `frequency_served_before216`); the frame served is a word shorter."""
    gate, frequency = gate_question(window, event), frequency_served_before216(window, event)
    longest = max(_words(gate), _words(frequency))
    if longest <= STEM_MAX_WORDS:
        return None
    gate_longest = _words(gate) >= longest
    which = "the gate" if gate_longest else "the Frequency question, as the cap measures it,"
    return (f"E4: framed, the clause makes {which} "
            f"{longest} words ('{gate if gate_longest else frequency}'); every question a stranger hears is at most "
            f"{STEM_MAX_WORDS} words, so shorten the clause, keeping its verb and its object")


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
    """**Retired by keel-cloud 185 FR-4** (`deciderChip` and `deciderPeople` gone; kept as the record of what a lock
    before 185 served -- `decider_condition` no longer reads it). keel-cloud 145 FR-4b / 146 FR-3 (`RespondentQuestionsRules.deciderChip`, mirrored): the decision-maker's screener
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
    study with no condition (or no decision-maker's link). Spec 118 FR-4c(e) (keel-cloud 185 FR-4, revision 21): the
    question writer writes it (`decider_condition`, one sentence about their own organisation, never *you decide for*;
    the scripted part-1 job writes the entry's `screeners.decider`, `decider_screener`) and the link serves the writer's;
    with none written, code asks the condition as part 1 does, said to the decision-maker (`chip_from`) -- never the
    retired *Do the {people} you decide for ...?* (`decider_chip`). Spec 123 FR-4 (keel-cloud 193 FR-4a,
    `RespondentQuestionsRules.condition` / `InterviewComposer`): with none written the link serves **no** condition
    (None) -- the fallback through `chip_from`, the segment's chip said to the decision-maker, is gone."""
    if not is_b2b(entry):
        return None
    written = decider_screener(entry)
    if written and segment_of(entry)["condition"]:
        return {"question": written["question"], "inCodes": [written.get("inside") or "YES"]}
    return None


def decider_screener(entry) -> dict | None:
    """Spec 118 FR-4c(e) (keel-cloud 185 FR-4 / T024): the decision-maker's condition as the question writer wrote it,
    `{question, inside}` -- the entry's `screeners.decider` (08-fresco, 10-palus, 17-expanse at revision 21); None where
    the entry records none (code's question then stands)."""
    found = (getattr(entry, "screeners", None) or {}).get("decider")
    if not isinstance(found, dict) or not str(found.get("question") or "").strip():
        return None
    return {"question": str(found["question"]).strip(), "inside": str(found.get("inside") or "YES")}


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
            "circumstance": ctx["circumstance"], "segment": scripted_segment(entry),
            "occasion": scripted_occasion(entry), "window": {"proposed": None}}


def scripted_occasion(entry) -> str:
    """Spec 137 FR-2 (keel-cloud 214 FR-2, `X14`; the coordinator's word, 2026-11-04): the occasion the scripted writer
    writes -- the corpus's own noun where it holds X14 (`writers_rules.occasion_fault`), else *time*, as the cloud's own
    fixtures now write it (10-palus' recorded *cash decision*; owed to a corpus revision), so no X14 note is served.
    Spec 139 FR-4: keel-cloud 217's revision 25 paid it (*cash review*); no entry's noun breaks X14 now."""
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    noun = occasion(entry)
    circumstance = _ctx(entry).get("circumstance")
    if writers_mod.occasion_fault(noun, None, circumstance, False) is None:
        return noun
    return "time" if writers_mod.occasion_fault("time", None, circumstance, False) is None else noun


def problem_result(entry) -> dict:
    """PROBLEM_INTERPRET's result: `statement` and `offer_name`; since keel-cloud 219 (spec 141 FR-2) the problem clause's
    fields beside them in a study without the problem's questions (`problem_clause`)."""
    return {"statement": (entry.interpretations or {})["problem"], "offer_name": offer_name(entry),
            **problem_clause(entry)}


#: Spec 148 FR-4 (keel-cloud 240 FR-4): the scripted belief's pointer where the circumstance would say the how again --
#: *the belief points back ('all of that')*, the cloud's own words.
BELIEF_POINTS_BACK = "make a real difference to all of that."


def seed_named(seed: str | None) -> str | None:
    """`IdeaName.named` (spec 128 FR-9): the name the founder quoted in the solution seed (one to five words, no
    sentence punctuation), or None -- the name M8 reads at the mechanism's apply."""
    for m in _QUOTED.finditer(seed or ""):
        phrase = _clean_name(m.group(1) or m.group(2) or m.group(3))
        if phrase and 1 <= len(phrase.split(" ")) <= NAME_MAX_WORDS and not re.search(r"[.!?;:]", phrase):
            return phrase
    return None


def idea_lines(entry) -> dict:
    """The idea's three lines as r10 composed them: *Imagine {short_name}.*, the how, the belief. Since keel-cloud 097
    (F7) the what line is not the model's -- the script sends `idea_how` / `idea_belief` alone -- and the what is the
    name the founder types (`idea_name`). Spec 148 FR-4 (keel-cloud 240 FR-4, M8 one check over the reveal): the
    scripted lines are heard once -- the first of the how's forms (whole; without its output clause; without its
    trigger; the mechanism alone) and the belief's (on the circumstance; pointing back, `BELIEF_POINTS_BACK`) that
    says nothing twice beside the what line (`m8_breaches`), so no scripted result spends a repair turn; an entry whose
    whole lines already are heard once is composed exactly as before."""
    m = entry.solution_mechanism or {}
    what = f"Imagine {short_name(entry)}."
    hows = [f"{m['trigger']}, {m['actor']} {m['mechanism']}; it gives {m['output']}.",
            f"{m['trigger']}, {m['actor']} {m['mechanism']}.",
            f"{m['actor']} {m['mechanism']}; it gives {m['output']}.", f"{m['actor']} {m['mechanism']}."]
    beliefs = [BELIEF_FRAME + f"make a real difference when {_ctx(entry)['circumstance']}.",
               BELIEF_FRAME + BELIEF_POINTS_BACK]
    suggested = (entry.idea_what() if hasattr(entry, "idea_what") else None) or short_name(entry)
    name = seed_named((getattr(entry, "statements", None) or {}).get("solution"))
    for how in hows:
        for belief in beliefs:
            said = _sentence(how)[:300]
            if not m8_breaches(name, suggested, said, belief[:200]):
                return {"what": what, "how": said, "belief": belief[:200]}
    return {"what": what, "how": _sentence(hows[0])[:300], "belief": beliefs[0][:200]}


# ------------------------------------------------------------- spec 148 FR-4: keel-cloud 240, the reveal heard once

#: keel-cloud 240 FR-4 (`IdeaLines.SMALL_WORDS`): the words that never make a thing said twice on their own -- grammar
#: words only, no trade.
IDEA_SMALL_WORDS = frozenset((
    "a", "an", "the", "and", "or", "but", "nor", "so", "yet", "then", "than", "as", "if", "when", "while", "where",
    "whether", "because", "though", "until", "before", "after", "since", "once", "to", "of", "in", "on", "at", "by", "for",
    "with", "from", "into", "onto", "over", "under", "through", "via", "near", "about", "around", "across", "along",
    "against", "between", "per", "up", "down", "out", "off", "without", "within", "inside", "during", "like", "is", "are",
    "was", "were", "be", "been", "being", "am", "do", "does", "did", "done", "have", "has", "had", "would", "will", "can",
    "could", "should", "may", "might", "must", "it", "its", "you", "your", "they", "them", "their", "we", "us", "our",
    "he", "him", "his", "she", "her", "i", "me", "my", "this", "that", "these", "those", "there", "here", "what", "which",
    "who", "whom", "whose", "how", "why", "not", "no", "never", "each", "every", "all", "any", "some", "more", "most",
    "much", "many", "few", "other", "another", "such", "same", "own", "also", "just", "only", "very", "too", "again",
    "ever", "even", "still", "both", "either", "neither", "imagine"))
#: keel-cloud 240 FR-4 (`IdeaLines.CLOSES_THE_PHRASE`): the words that close the what line's first noun phrase.
CLOSES_THE_PHRASE = frozenset((
    "to", "through", "into", "from", "in", "on", "at", "by", "with", "for", "of", "over", "under", "about", "across",
    "after", "before", "between", "during", "inside", "onto", "per", "via", "without", "within", "around", "against",
    "like", "near", "that", "which", "who", "whom", "whose", "where", "when", "while", "and", "or", "but", "so", "if",
    "as", "than", "because", "the", "a", "an", "your", "their", "its", "his", "her", "our", "my", "them", "it", "you",
    "they", "we", "this", "these", "those", "is", "are", "was", "were", "will", "would", "can", "could", "may", "might",
    "should", "does", "do", "has", "have", "then", "every", "each"))
#: keel-cloud `IdeaLines.CARD_OPENING`.
CARD_OPENING = "Imagine "
_EDGE = re.compile(r"^[^\w]+|[^\w]+$")


def _bare(word: str) -> str:
    return re.sub(r"^[\W_]+|[\W_]+$", "", word)


def what_is(words) -> str | None:
    """`IdeaLines.whatIs` (spec 185 FR-2): what it is as the card says it after the name -- one space, no trailing stop
    or leading comma, a capitalised article lower-cased; None when blank."""
    if words is None or not str(words).strip():
        return None
    text = " ".join(str(words).split())
    while text.endswith("."):
        text = text[:-1].strip()
    while text.startswith(","):
        text = text[1:].strip()
    if not text:
        return None
    first = text.split(" ")[0]
    if first in ("A", "An", "The"):
        text = first.lower() + text[len(first):]
    return text


def card_line(name, what) -> str:
    """`IdeaLines.card(name, whatItIs)` (spec 185 FR-2): *Imagine {name}, {what it is}.*, the name alone where what it is
    is the name itself."""
    said = what_is(what)
    if said is None or (name is not None and said.lower() == idea_name_of(name).lower()):
        return CARD_OPENING + ("" if name is None else str(name).strip()) + "."
    return CARD_OPENING + ("" if name is None else str(name).strip()) + ", " + said + "."


def _singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _heard_word(word: str) -> str:
    return _singular(re.sub(r"['’]s$", "", word.lower()))


def kind_of(what) -> str | None:
    """keel-cloud 240 FR-4 (`IdeaLines.kindOf`): the kind of thing a what line names -- its first noun phrase's last word
    before the word that closes it (or a comma), as heard; None where none."""
    line = what_is(what)
    if line is None:
        return None
    kind = None
    words = line.split()
    for i, raw in enumerate(words):
        word = _bare(raw)
        lower = word.lower()
        if i > 0 and lower in CLOSES_THE_PHRASE:
            break
        if word and lower not in IDEA_SMALL_WORDS:
            kind = _heard_word(word)
        if raw.endswith(","):
            break
    return kind if kind is not None and re.fullmatch(r"[^\W\d_]+", kind) else None


def idea_sentences(line) -> list[str]:
    """`IdeaLines.sentences` (spec 207 FR-3): a line's sentences, split after . ! or ? and a space."""
    if line is None or not str(line).strip():
        return []
    return [s for s in re.split(r"(?<=[.!?])\s+", str(line).strip()) if s.strip()]


def _heard_in(sentence: str, kind, opened: bool, offset: int) -> list[tuple]:
    raw = sentence.strip().split()
    bare = [_bare(w) for w in raw]
    closes = [bool(w) and not w[-1].isalnum() for w in raw]
    lower = [re.sub(r"['’]s$", "", b.lower()) for b in bare]
    key = [_singular(x) for x in lower]
    plain = lambda w: bool(w) and w not in IDEA_SMALL_WORDS                               # noqa: E731
    units = []
    for i in range(len(raw)):
        if not key[i]:
            continue
        opens = i == 0 and not opened
        if not opens and bare[i][:1].isupper() and bare[i] != "I" and bare[i] != bare[i][:1]:
            units.append(("name:" + key[i], bare[i], offset + i, offset + i))
        elif re.fullmatch(r"[^\W\d_]+(?:-[^\W\d_]+)+", bare[i]):
            units.append(("joined:" + key[i], bare[i], offset + i, offset + i))
        elif key[i] == kind:
            units.append(("kind:" + kind, bare[i], offset + i, offset + i))
        if i + 1 < len(raw) and not closes[i] and plain(lower[i]) and plain(lower[i + 1]):
            units.append(("words:" + key[i] + " " + key[i + 1], bare[i] + " " + bare[i + 1], offset + i, offset + i + 1))
    return units


def said_twice(name, what, how, belief) -> list[tuple[str, str]]:
    """keel-cloud 240 FR-4 (`IdeaLines.saidTwice`): what the reveal -- the name and what it is, the how, the belief, heard
    in a row -- says again: `(words, line)` with `line` *what*, *how* or *belief*, each thing once in the order heard, a
    word inside a longer thing said again not named apart. It hears a name (a capitalised word opening no sentence), a
    joined word, two plain words in a row (never across a comma) and the what line's kind; the belief's frame is never
    counted. Grammar only, persona-blind."""
    lines = []
    what_line = card_line(name, what) if name is not None and str(name).strip() else what_is(what)
    if what_line is not None:
        lines.append(("what", what_line))
    if how is not None and str(how).strip():
        lines.append(("how", str(how)))
    framed = belief is not None and str(belief).strip().startswith(BELIEF_FRAME)
    if belief is not None and str(belief).strip():
        lines.append(("belief", str(belief).strip()[len(BELIEF_FRAME):] if framed else str(belief)))
    kind = kind_of(what)
    heard: set = set()
    told: set = set()
    again: list[tuple[str, str]] = []
    for where, text in lines:
        frameless = framed and where == "belief"
        spans: list[tuple[int, int]] = []
        repeats: list[tuple] = []
        offset = 0
        for sentence in idea_sentences(text):
            units = _heard_in(sentence, kind, frameless and offset == 0, offset)
            offset += len(sentence.split())
            for unit_key, words, start, end in units:
                fresh = unit_key not in heard
                heard.add(unit_key)
                if not fresh and unit_key not in told and all(r[0] != unit_key for r in repeats):
                    repeats.append((unit_key, words, start, end))
        for unit_key, words, start, end in sorted(repeats, key=lambda r: -(r[3] - r[2])):
            if any(s <= start and end <= e for s, e in spans):
                continue
            spans.append((start, end))
            told.add(unit_key)
            again.append((words, where))
    return again


#: keel-cloud 240 FR-4 (`ScreenResultApplier`'s M8): the line a thing is heard again in, as the breach names it.
M8_LINES = {"what": "what line", "how": "how line", "belief": "belief"}


def m8_breaches(name, what, how, belief, how_decider=None, what_is_short_name: bool = False) -> list[tuple[str, str]]:
    """keel-cloud 240 FR-4 (`ScreenResultApplier`, after M7): `(path, why)` for every M8 the reveal draws -- each how
    voice read with the name, what it is and the belief; the path the line's (`result.idea_what`, or
    `result.short_name` where that is the suggestion; the how's own voice; `result.idea_belief`); once each."""
    what_path = "result.short_name" if what_is_short_name else "result.idea_what"
    out: list[tuple[str, str]] = []
    for line, path in ((how, "result.idea_how.primary"), (how_decider, "result.idea_how.decider")):
        if line is None or not str(line).strip():
            continue
        grouped: dict = {}
        for words, where in said_twice(name, what, line, belief):
            grouped.setdefault(where, []).append(f"'{words}'")
        for where, words in grouped.items():
            at = {"what": what_path, "how": path}.get(where, "result.idea_belief")
            why = ("M8: " + ", ".join(words) + (" is" if len(words) == 1 else " are") + " heard again in the "
                   + M8_LINES[where] + "; the name, what it is, the how and the belief are one reveal heard in a row, "
                   "so each thing is said once -- the what line's kind is 'it' after it, and the belief points back "
                   "('all of that')")
            if (at, why) not in out:
                out.append((at, why))
    return out


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


def what_it_is(words: str | None) -> str | None:
    """keel-cloud 185 `IdeaLines.whatIs`: the plain words cleaned -- stripped, a closing full stop and a leading comma
    dropped, a capitalised article (*A*, *An*, *The*) lowered; None when blank."""
    text = " ".join(str(words or "").split())
    while text.endswith("."):
        text = text[:-1].strip()
    while text.startswith(","):
        text = text[1:].strip()
    if not text:
        return None
    first = text.split(" ")[0]
    if first in ("A", "An", "The"):
        text = first.lower() + text[len(first):]
    return text


#: keel-cloud 197 FR-3 (`Wording.SHORT_NAME_MAX_WORDS`): the model's short name -- the kind of thing and what it does --
#: is at most eight words, its article counted (five until 197); the founder's own name keeps spec 090's five
#: (`IdeaLines.NAME_MAX_WORDS`, `corpus.IDEA_NAME_MAX_WORDS`, keel-web's *Name it in up to five words*).
SHORT_NAME_MAX_WORDS = 8
SHORT_NAME_MAX_WORDS_196 = 5
#: `IdeaLines.CLOSES_THE_PHRASE` (keel-cloud 197): the grammar words that close a phrase's first noun phrase.
CLOSES_THE_PHRASE = frozenset((
    "to through into from in on at by with for of over under about across after before between during inside onto per "
    "via without within around against like near that which who whom whose where when while and or but so if as than "
    "because the a an your their its his her our my them it you they we this these those is are was were will would can "
    "could may might should does do has have then every each").split())


def _phrase_of(phrase) -> list[str]:
    """`IdeaLines.phraseOf` (keel-cloud 197 FR-3): the words of a phrase's first noun phrase, lower-cased, a leading
    article skipped, closed by a grammar word or by a comma or full stop after a word; a hyphenated word by its last
    part (*missed-call* is *call*)."""
    kept: list[str] = []
    for raw in str(phrase or "").strip().split():
        bare = re.sub(r"^[^\w]+|[^\w]+$", "", raw).lower()
        if not bare:
            break
        if bare in CLOSES_THE_PHRASE:
            if kept:
                break
            continue
        kept.append(re.split(r"[-\u2010\u2011]", bare)[-1])
        if re.search(r"[,;:.!?)\u2014]$", raw):
            break
    return kept


def _singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def is_an_outcome(short_name, output) -> bool:
    """keel-cloud 197 FR-3 (`IdeaLines.isAnOutcome`, `W3`): a short name names what the person gets back when its head
    noun (the last word of its first noun phrase) is a word of the output's first noun phrase, a plural aside --
    *missed-call bookings* against *the confirmed booking written straight into the PMS*; never *an AI reservation
    agent for missed hotel calls*."""
    said = _phrase_of(short_name)
    if not said:
        return False
    head = _singular(said[-1])
    return any(_singular(w) == head for w in _phrase_of(output))


def what_it_is_faults(what_it_is, output) -> list[str]:
    """Spec 130 (keel-cloud 197 FR-3): what the idea card's plain words owe -- never empty on a drafted idea (`L6`), at
    most `SHORT_NAME_MAX_WORDS` words, and the kind of thing, never the outcome (`W3`). A finding, never a stop."""
    text = " ".join(str(what_it_is or "").split())
    if not text:
        return ["L6: the idea card's what it is is empty (keel-cloud 197 FR-3: never served empty)"]
    faults = []
    if len(text.split()) > SHORT_NAME_MAX_WORDS:
        faults.append(f"W3: '{text}' is {len(text.split())} words; at most {SHORT_NAME_MAX_WORDS}")
    if output and is_an_outcome(text, output):
        faults.append(f"W3: '{text}' names what the person gets back ('{output}'), not the kind of thing")
    return faults


def idea_card(name: str, what: str | None = None) -> str:
    """keel-cloud `IdeaLines.card` (spec 090): the strangers' what line, composed by code -- *Imagine {name}.* Spec 118
    FR-4c(d) (keel-cloud 185 FR-2, `IdeaLines.card(name, whatItIs)`): with the plain words, *Imagine {name}, {what it
    is}.* -- *Imagine Fresco, notes written from site videos.* -- the name said once where it is the plain words
    themselves; *Imagine {name}.* where there are none (a project from before 185)."""
    plain = what_it_is(what)
    if plain is None or plain.lower() == idea_name_of(name).lower():
        return f"Imagine {name.strip()}."
    return f"Imagine {name.strip()}, {plain}."


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


#: keel-cloud 237 FR-3 (`ScaleFour.HELPED` + the job + `HELPED_END`): the question after the hard case's anchor or the
#: stem's names the job -- *Would {idea} have helped you {job} better, or not?* (frame `"237"`).
BENEFIT_HELPED = re.compile(r"^Would (?P<idea>.+?) have helped you (?P<job>.+?) better, or not\?$")
#: keel-cloud 198 FR-8 (`ScaleFour.DONE_BETTER`): the at-stake anchor's tail, and since 237 the fallback where no rung of
#: the ladder fits with the job (frame `"198"`).
BENEFIT_DONE_BETTER = re.compile(r"^Would (?P<idea>.+?) have done that better for you, or not\?$")


def benefit_split(question: str | None) -> tuple[str | None, str]:
    """A served Relative advantage question as `(anchor, the question after it)` -- the anchor its first sentence where
    it opens on *Think* (spec 120's, 198's, 214's or 219's), else None."""
    text = (question or "").strip()
    at = text.find(". ")
    if at > 0 and text.startswith("Think "):
        return text[:at + 1], text[at + 2:].strip()
    return None, text


def benefit_frame_of(question: str | None) -> str | None:
    """Which composition a served Relative advantage question is in: `"237"` (*Would ... have helped you {job} better,
    or not?*, keel-cloud 237 FR-3), `"198"` (*... have done that better for you, or not?*: the at-stake anchor's, or no
    rung fitting with the job), `"173"` (the occasion inside, *Would ... have made your last / the last time go better
    ...*), `"159"` (*... have made it go better ...*, an item stored before 173), `"085"` (*... made things better ...*,
    before contract 47), else None. An anchor before it is read past (`benefit_split`)."""
    _, text = benefit_split(question)
    if BENEFIT_HELPED.match(text):
        return "237"
    if BENEFIT_DONE_BETTER.match(text):
        return "198"
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
    out = {"actor": m["actor"], "trigger": m["trigger"], "mechanism": m["mechanism"],
           "output": m["output"], "not_assumed": list(m.get("not_assumed") or []),
           "mechanism_terms": terms, "short_name": short_name(entry),
           "idea_how": idea["how"], "idea_belief": idea["belief"]}
    # spec 132 FR-11 (keel-cloud 207 FR-3, corpus revision 23): the writer's optional `idea_what` -- what the idea is
    # beside its name -- sent where the entry records one (the five cycle-9 back-test entries); none elsewhere, as a
    # result before 207 reads
    what = entry.idea_what() if hasattr(entry, "idea_what") else None
    if what:
        out["idea_what"] = what
    return out


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
COMPATIBILITY_KEY = "solution.compatibility"
ADOPTION_KEY = "solution.adoption_friction"
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
#: Spec 117 FR-2 (keel-cloud 178, `InterviewAnswers.item` reading `CommercialChain.NOTHING_LABEL`): the founder's
#: answers view (*See {name}'s answers*, the invitation's `interview.items[].answer`) and the Pilot tab
#: (`answers[].words`) print a NOTHING value box or cost total as the stranger's chip says it -- *None*, where they read
#: *Nothing* until 178 -- with `mode` / `chip` NOTHING and the value 0 beside it. The one word for both; no walk reads
#: the view's word today, and a check that does reads this.
ANSWERS_VIEW_NOTHING = VALUE_BOX_LABELS["NOTHING"]


def value_box_escapes(consumer: bool) -> list[str]:
    """`CommercialChain.valueBoxEscapes`: the chips recorded apart, as served codes -- *I can't recall* on every link
    since keel-cloud 198 FR-3 (the consumer's *I'd rather not say* gone; `consumer` kept for the callers)."""
    return ["DONT_KNOW"]


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


#: keel-cloud 198 FR-3 / 206 FR-5 (`CommercialChain.LOSS_WORDS`): the forms of *lose* -- and since 206 of *miss* -- a
#: stranger's cost question never says (the lock guard's `S15`, `loss_word`).
LOSS_WORDS = frozenset(("lose", "loses", "lost", "losing", "miss", "misses", "missed", "missing"))


def loss_word(stem: str | None) -> str | None:
    """`CommercialChain.lossWord`: the first form of *lose* or *miss* a stem says, or None."""
    if stem is None:
        return None
    return next((w for w in re.split(r"[^a-z']+", stem.lower()) if w in LOSS_WORDS), None)


def _held(ladder: list[str]) -> str:
    """`CommercialChain.held`: the first rung within the spoken cap, of the rungs that say no form of *lose* or *miss*
    (keel-cloud 198 FR-3, 206 FR-5; all of them where every rung says one); the last where none fits."""
    said = [stem for stem in ladder if loss_word(stem) is None]
    rungs = said or ladder
    return next((stem for stem in rungs if ll.words(stem) <= STEM_MAX_WORDS), rungs[-1])


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


#: Spec 132 FR-9 (keel-cloud 206 FR-5, `CommercialChain.GONE_WITHOUT`, `WENT_WRONG`, `PERCENT_OF`): the verb the stranger's
#: cost question says where the founder's loss line carries none of its own, or only *lose*'s or *miss*'s -- what the
#: person saw happen, never *miss*: money, time or a thing they *went without*; a counted thing that *fell through*; and
#: the question words that name a percent box's unit (never *how much* before a percent). English's words, no trade's.
GONE_WITHOUT = "go without"
WENT_WRONG = "fell through"
PERCENT_OF = "what percent of "
#: keel-cloud 206 (`CommercialChain.LOSS_OR_MISS`): the line's own verbs that say the thing went without naming what the
#: person saw.
LOSS_OR_MISS = frozenset(("lost", "lose", "loses", "missed", "miss", "misses"))
_SEEN_OPENERS = frozenset(("when", "whenever", "if", "as"))


def _without(thing: str) -> str:
    """`CommercialChain.without`: the thing gone without after a share's base -- *in interest* (a bare noun), *the value
    of the rupees ...* (a determiner first: the thing itself)."""
    first = ll.clean(thing.strip().split()[0])
    return thing if first in ll.DETERMINERS else "in " + thing


def without_the_measure(thing: str, measure: str) -> str:
    """`CommercialChain.withoutTheMeasure`: a thing's own *of* tail that names the counted measure again is said once --
    *the thread of the conversation*, counted in conversations, reads *the thread*."""
    m = re.fullmatch(r"(?i)(.+?)\s+of\s+(?:the |a |an |your |their )?((?:[^\W\d_]|['-])+)", thing.strip())
    if not m:
        return thing.strip()
    noun, counted = m.group(2).lower(), measure.strip().lower()
    return m.group(1).strip() if counted in (noun, noun + "s", noun + "es") else thing.strip()


def one_verb(clause):
    """`CommercialChain.oneVerb`: a verb clause that joins two verbs, the second negated, keeps the one the person sees
    -- *reserve and never use* reads *never use*; any other clause as it is."""
    if clause is None:
        return None
    m = re.fullmatch(r"(?i)(?:[^\W\d_]|['-])+\s+(?:and|or)\s+((?:never|not)\s+.+)", clause.strip())
    return m.group(1) if m else clause


def seen_event(loss, counted):
    """`CommercialChain.seenEvent`: a line whose own verb is *lose*'s or *miss*'s (*Bookings lost when a call rings out
    after hours ...*) names the event the person saw in the clause it opens -- *when a call rings out ...* -- where that
    clause's subject is the thing the box counts (*a call*, the base *the reservation calls*): the event from its verb on
    (*rings out after hours ...*), else None."""
    if loss is None or counted is None or loss.shape != ll.DONE:
        return None
    w = loss.clause.strip().split()
    if len(w) < 4 or ll.clean(w[0]) not in LOSS_OR_MISS:
        return None
    if ll.clean(w[1]) not in _SEEN_OPENERS:
        return None
    verb = ll.first_verb(w, 2, 4)
    if verb < 3:
        return None
    head = ll.clean(w[verb - 1])
    base = counted.strip().lower().split()
    base_head = ll.clean(base[-1])
    return " ".join(w[verb:]) if base_head in (head, head + "s", head + "es") else None


def _loss_count(ladder, opening, team, loss, measure, per: str = "") -> None:
    if loss is None or loss.shape == ll.NONE:
        return
    thing = _said(loss.thing, team)
    # spec 132 FR-9 (keel-cloud 206 FR-5): a lost or missed thing is asked by the event the line names after it, where
    # that event happens to the thing counted (*how many calls rang out*)
    event = seen_event(loss, measure)
    if event is not None:
        for clause in _clauses(event):
            for about in (", about how many ", ", how many "):
                ladder.append(opening + about + measure + per + " " + _in_their_past(ll.past(clause), team) + "?")
    for clause in _clauses(one_verb(loss.clause)):
        # spec 148 FR-3 (keel-cloud 239 FR-5): the typed unit after the thing (`per`, empty but on the B2B link)
        if loss.shape == ll.DOES:
            asked = thing + per + " " + _in_their_past(ll.past(clause), team)
        elif loss.shape == ll.DONE:
            asked = thing + per + " were " + _in_their_past(ll.past(clause), team)
        else:
            asked = thing + per + " did " + _subject_said(loss.subject, team) + " " \
                + _in_their_past(ll.after_did(clause), team)
        for about in (", about how many ", ", how many "):
            ladder.append(opening + about + asked + "?")


def _loss_share(ladder, opening, team, loss, base, per: str = "") -> None:
    be = " were " if count_noun(base) or _plural_head(base) else " was "
    # spec 132 FR-9 (keel-cloud 206 FR-5): the event the line names after a lost or missed share, where it happens to the
    # base (*what percent of the reservation calls rang out*)
    event = seen_event(loss, base)
    if event is not None:
        for clause in _clauses(event):
            for about in (", about " + PERCENT_OF, ", " + PERCENT_OF):
                ladder.append(opening + about + base + per + " " + _in_their_past(ll.past(clause), team) + "?")
    for clause in _clauses(one_verb(loss.clause)):
        if loss.shape == ll.DOES:
            asked = base + per + " " + _in_their_past(ll.past(clause), team)
        elif loss.shape == ll.DONE:
            asked = base + per + be + _in_their_past(ll.past(clause), team)
        else:
            asked = base + per + " did " + _subject_said(loss.subject, team) + " " \
                + _in_their_past(ll.after_did(clause), team)
        # keel-cloud 206 (FR-5): the question words name the box's unit, a percent
        for about in (", about " + PERCENT_OF, ", " + PERCENT_OF):
            ladder.append(opening + about + asked + "?")


def _loss_gone_without(ladder, opening, team, loss, base) -> None:
    """`CommercialChain.lossGoneWithout` (keel-cloud 206 FR-5; `lossMissed` before): a loss line with no verb of its own,
    asked with *go without* -- the box's unit named first where there is a base (*what percent of the balance did you go
    without in interest*), else *how much ... did you go without*."""
    thing = _said(loss.thing, team)
    rest = "" if not loss.clause.strip() else _in_their_past(ll.past(loss.clause), team)
    forms = []
    if loss.rest_is_a_place():
        # spec 148 FR-3 (keel-cloud 239 FR-3): a rest that reads as a place is never appended after the verb -- the
        # thing alone, and the line goes to the writer (the stem says the neutral verb)
        forms.append((thing, ""))
    else:
        whole = (thing + " " + rest).strip()
        forms.append((whole, ""))
        shorter = without_purpose(whole)
        if shorter is not None:
            forms.append((shorter, ""))
    if base is not None:
        for said, where in forms:
            tail = "" if not where.strip() else " " + where
            for about in (", about " + PERCENT_OF, ", " + PERCENT_OF):
                ladder.append(opening + about + base + " did " + LOSER + " " + GONE_WITHOUT + " " + _without(said)
                              + tail + "?")
        return
    for said, where in forms:
        tail = "" if not where.strip() else " " + where
        for about in (", about how much ", ", how much "):
            # spec 118 (keel-cloud 184 FR-8b (c), `CommercialChain.LOSER`): the person asked is the one who goes without
            # it -- *you*, never *your team*
            ladder.append(opening + about + _much(said) + " did " + LOSER + " " + GONE_WITHOUT + tail + "?")


#: keel-cloud 184 FR-8b (c) (`CommercialChain.LOSER`): a loss with the measure's neutral verb is the person's own.
LOSER = "you"


def _rate_stem(opening: str, noun, team: bool, base, cost: dict) -> tuple:
    """keel-cloud 222 FR-1 / 239 FR-1, FR-2, FR-5 (`CommercialChain.rateStem`): the RATE ladder read -- `(served, wanted,
    share, measure, as_typed, per)`. The ladder's rungs carry the typed unit first on the decision-maker's link (`per`,
    `per_unit`), then without; `wanted` -- the writer's `loss_clause` is asked -- is decided on the served stem itself
    (it says a neutral verb, `says_a_neutral_verb`), where a line was typed and the frame can name the thing; and the
    neutral verb is never served: where it is wanted (until the writer's clause lands, and past its second failure) or
    the stem says a banned word, code's plain not-done, else the founder's own line said to the person
    (`loss_not_done`; `as_typed` the Check's note)."""
    ladder: list[str] = []
    measure = cost_measure(cost)
    share = measure is None or measure.strip() == "%"
    loss = ll.read(cost.get("lossPhrase"))
    if loss is not None and same_words(cost.get("lossPhrase"), base):
        loss = None
    per = per_unit(cost, team, base if share else None if measure is None else measure.strip())
    if not share:
        if per:
            _loss_count(ladder, opening, team, loss, measure.strip(), per)
        _loss_count(ladder, opening, team, loss, measure.strip())
        if loss is not None and loss.shape == ll.NONE:
            thing = without_the_measure(_said(loss.thing, team), measure.strip())
            ladder.append(f"{opening}, in about how many {measure.strip()} did {LOSER} {GONE_WITHOUT} {thing}?")
        ladder.append(f"{opening}, about how many {measure.strip()} {WENT_WRONG}?")
    else:
        loss_open = f"On your last {noun}" if not team and noun is not None else opening
        openings = [opening] if loss_open == opening else [loss_open, opening]
        if loss is not None and loss.shape != ll.NONE and base is not None:
            for each in openings:
                if per:
                    _loss_share(ladder, each, team, loss, base, per)
                _loss_share(ladder, each, team, loss, base)
        elif loss is not None and loss.shape == ll.NONE:
            for each in openings:
                _loss_gone_without(ladder, each, team, loss, base)
        if base is not None:
            ladder.append(opening + ", about " + PERCENT_OF + base
                          + (" " + WENT_WRONG if count_noun(base) else " did " + LOSER + " " + GONE_WITHOUT) + "?")
    ladder.append(f"{opening}, about what percent did {LOSER} {GONE_WITHOUT}?")
    served = _held(ladder)
    frameable = base is not None if share else bool(measure and measure.strip())
    typed = not _blank(cost.get("lossPhrase"))
    wanted = typed and frameable and says_a_neutral_verb(served)
    counted = None if measure is None else measure.strip()
    if frameable and (wanted or banned_word(served) is not None):
        stem, as_typed = loss_not_done(opening, cost, base if share else None, per, None if share else counted)
        return stem, wanted, share, counted, as_typed, per
    return served, False, share, counted, False, per


def loss_clause_wanted(team: bool, occasion, cost: dict | None) -> bool:
    """keel-cloud 222 FR-1 (`CommercialChain.lossClauseWanted`): whether the founder's cost asks for the writer's
    `loss_clause` -- a RATE cost whose loss line code's own reading cannot ask, on the link the item is served on."""
    if not isinstance(cost, dict) or cost.get("mode") != "RATE":
        return False
    over = cost.get("period") if cost.get("period") in _COST_OPENERS else "month"
    # spec 148 FR-3 (keel-cloud 239 FR-4): the base the item asks on
    base = None if asked_base(cost) is None else _said(asked_base(cost), team)
    return _rate_stem(_COST_OPENERS[over], ll.occasion_noun(occasion), team, base, cost)[1]


#: keel-cloud 222 (`LossClause.RELATIVE`, `SUBJECTS`, `INVERTED`).
_CLAUSE_RELATIVE = frozenset(("that", "which", "who"))
_CLAUSE_SUBJECTS = frozenset(("you", "they", "we"))
_CLAUSE_INVERTED = frozenset(("were", "was", "could", "would", "did", "had"))


def _thing_roots(base, measure) -> set:
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    roots = set(writers_mod.roots(base)) if base is not None else set()
    if measure is not None and measure.strip() != "%":
        roots |= set(writers_mod.roots(measure))
    return roots


def loss_clause_said(clause, base, measure) -> str | None:
    """keel-cloud 222 FR-4 (`LossClause.said`): the clause as the frame takes it -- one that opens on the frame's thing
    (*booking calls that rang out unanswered* after *the reservation calls*) cut to its verb phrase, one opening on the
    person turned to a question's order (*you stopped following* -> *did you stop following*, *you were* -> *were
    you*); None with none."""
    from instructions import spoken as spoken_mod                       # noqa: PLC0415
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    if clause is None or not str(clause).strip():
        return None
    text = re.sub(r"[.,;:!?]+$", "", re.sub(r"\s+", " ", str(clause).strip())).strip()
    if not text:
        return None
    w = ll.lower_first(text).split(" ")
    thing = _thing_roots(base, measure)
    for i in range(1, min(len(w) - 1, 7)):
        x = w[i].lower()
        if x not in _CLAUSE_RELATIVE and x not in _CLAUSE_SUBJECTS:
            continue
        if set(writers_mod.roots(" ".join(w[:i]))) & thing:
            w = w[i + 1:] if x in _CLAUSE_RELATIVE else w[i:]
        break
    if len(w) >= 2 and w[0].lower() == "you":
        verb, rest = w[1].lower(), " ".join(w[2:])
        if verb in _CLAUSE_INVERTED and verb not in ("had", "did"):
            w = (("were" if verb == "was" else verb) + " you " + rest).strip().split(" ")
        else:
            base0 = spoken_mod.base_of_past_loose(verb)
            if base0 is not None and verb != "did":
                w = ("did you " + base0 + " " + rest).strip().split(" ")
    return " ".join(w).strip()


def loss_clause_frames(opening: str, clause: str, base, measure, per: str = "") -> list[str]:
    """keel-cloud 222 FR-4 (`CommercialChain.lossClauseFrames`): *{opener}, about what percent of {base} {clause}?* (a
    share) or *{opener}, about how many {measure} {clause}?* (a count), then each without *about*. Since keel-cloud 239
    FR-5 (spec 148 FR-3) with the typed unit after the base or measure (`per`) first, then the same without it."""
    asked = PERCENT_OF + base if base is not None else "how many " + str(measure)
    frames = []
    for unit in ([per, ""] if per else [""]):
        frames += [f"{opening}, about {asked}{unit} {clause}?", f"{opening}, {asked}{unit} {clause}?"]
    return frames


def loss_clause_question(opening: str, loss_clause, base, measure, per: str = "") -> str | None:
    """keel-cloud 222 FR-4 (`CommercialChain.lossClauseQuestion`): the first of the clause's frames within the spoken cap
    that says no banned word (since keel-cloud 239: `banned_word`, *lose* / *miss* and the neutral verbs); else None."""
    clause = loss_clause_said(loss_clause, base, measure)
    if clause is None:
        return None
    return next((rung for rung in loss_clause_frames(opening, clause, base, measure, per)
                 if banned_word(rung) is None and ll.words(rung) <= STEM_MAX_WORDS), None)


#: Spec 141 FR-7 (keel-cloud 222 FR-2): the writer's `loss_clause` the scripted part-1 result (since keel-cloud 239, on a
#: money-only study, part 3's) carries where an entry holds one and the cost wants it (`loss_clause_wanted`). **None today**: no golden entry's line falls to a neutral
#: verb, and the cycle-14 five (Codyco, Expanse, Palus, AirCaps, Fresco) were COMMERCIAL studies, which run no part-1
#: job (222's judgement call 2) -- so the item takes code's reading, as today (no pin moves).
LOSS_CLAUSES: dict[str, str] = {}


def scripted_loss_clause(entry) -> str | None:
    """Spec 141 FR-7: the scripted part-1 result's `loss_clause` -- the entry's (`LOSS_CLAUSES`) where its cost wants
    one on the link part 3 is served on, else None."""
    clause = LOSS_CLAUSES.get(getattr(entry, "id", None))
    cost = entry.cost() if callable(getattr(entry, "cost", None)) else None
    if clause is None or not loss_clause_wanted(is_b2b(entry), entry.occasion(), cost):
        return None
    return clause


# ------------------------------------------------------------- spec 148 FR-3: keel-cloud 239, the thing they see go

#: keel-cloud 239 FR-2 (`LossNotDone.NEUTRAL_PHRASES`): the two neutral verbs the rate ladder fell to, in any tense.
NEUTRAL_PHRASES = ("go without", "goes without", "went without", "gone without", "going without", "fell through",
                   "fall through", "falls through", "fallen through", "falling through")


def banned_word(stem: str | None) -> str | None:
    """keel-cloud 239 FR-2 (`LossNotDone.bannedWord`): the word no served Existing sacrifice item says -- *lose*'s and
    *miss*'s forms (`loss_word`), then *go without* and *fell through* in any tense -- or None."""
    said = loss_word(stem)
    if said is not None:
        return said
    text = " " + re.sub(r"[^a-z' ]+", " ", (stem or "").lower()) + " "
    return next((phrase for phrase in NEUTRAL_PHRASES if " " + phrase + " " in text), None)


def says_a_neutral_verb(stem: str | None) -> bool:
    """keel-cloud 239 FR-1 (`CommercialChain.saysANeutralVerb`): whether a stem says *go without* or *fell through*."""
    said = (stem or "").lower()
    return GONE_WITHOUT in said or WENT_WRONG in said


#: keel-cloud 239 FR-2 (`LossNotDone.NOT_DONE`): each banned verb's form to its plain not-done -- `(verb, of the thing,
#: words)`: *lose* *did you not keep*, *miss* / *go without* *did you not get*, *fall through* *did not go through*.
_NOT_DONE: dict = {}
for _form in ("lose", "loses", "lost", "losing"):
    _NOT_DONE[_form] = ("keep", False, 1)
for _form in ("miss", "misses", "missed", "missing"):
    _NOT_DONE[_form] = ("get", False, 1)
for _form in ("go", "goes", "went", "gone", "going"):
    _NOT_DONE[_form + " without"] = ("get", False, 2)
for _form in ("fell", "fall", "falls", "fallen", "falling"):
    _NOT_DONE[_form + " through"] = ("go through", True, 2)
#: `LossNotDone.NO_OBJECT`: words a verb's own object never opens on.
_NO_OBJECT = frozenset(("to", "when", "because", "before", "after", "until", "if", "while", "since", "as", "on", "in",
                        "at", "from", "by", "for", "with", "over", "during", "due", "than", "which", "who", "that",
                        "where", "once", "unless", "and", "or", "but"))


def _nd_words(text) -> list[str]:
    return [] if text is None or not str(text).strip() else str(text).strip().split()


def _nd_held(rungs: list[str]) -> str | None:
    """`LossNotDone.held`: the first rung within the spoken cap, else the shortest."""
    shortest = None
    for rung in rungs:
        if ll.words(rung) <= STEM_MAX_WORDS:
            return rung
        shortest = rung if shortest is None or ll.words(rung) < ll.words(shortest) else shortest
    return shortest


def _nd_frame(opening, base, per, measure, predicate, about) -> str:
    asked = "what percent of " + base if base is not None else "how many " + str(measure)
    return f"{opening}, {'about ' if about else ''}{asked}{per} {predicate}?"


def _nd_object(w: list[str], start: int) -> str | None:
    """`LossNotDone.object`: what the line names after its banned verb, where that is the verb's own object."""
    if start >= len(w) or ll.clean(w[start]) in _NO_OBJECT:
        return None
    end = start
    while end < len(w) and (end == start or ll.clean(w[end]) not in ll.SUBORDINATORS):
        end += 1
    obj = re.sub(r"[,;:.]+$", "", " ".join(w[start:end])).strip()
    return obj.lower() if obj else None


def _not_done_rungs(opening, cost: dict, base, per: str, measure) -> list[str]:
    """`LossNotDone.notDoneRungs`: the plain not-done -- a negated participle the line names (*unanswered* -> *did not get
    answered*), else one of the card's banned verbs said not done, keeping its own object (*did you not keep track of*);
    with the typed unit, then without; about, then not."""
    predicates: list[str] = []
    w = _nd_words(cost.get("lossPhrase"))
    i = 0
    while i < len(w) and not predicates:
        x = ll.clean(w[i])
        if len(x) > 5 and x.startswith("un") and not x.startswith("under") and ll.participle(x[2:]):
            predicates.append("did not get " + x[2:])
            i += 1
            continue
        two = x + " " + ll.clean(w[i + 1]) if i + 1 < len(w) else None
        said = _NOT_DONE.get(two) if two is not None and two in _NOT_DONE else _NOT_DONE.get(x)
        if said is not None:
            verb, of_the_thing, n = said
            obj = _nd_object(w, i + n)
            head = ("did not " if of_the_thing else "did you not ") + verb
            if obj is not None:
                predicates.append(head + " " + obj)
            predicates.append(head)
        i += 1
    rungs = []
    for with_unit in (True, False):
        if not with_unit and not per:
            continue
        for predicate in predicates:
            for about in (True, False):
                rungs.append(_nd_frame(opening, base, per if with_unit else "", measure, predicate, about))
    return [r for r in rungs if banned_word(r) is None]


def _nd_cut_at_a_place(said: str) -> str | None:
    w = _nd_words(said)
    for i in range(3, len(w)):
        x = ll.clean(w[i])
        if x in ll.PREPOSITIONS or x in ll.SUBORDINATORS:
            return re.sub(r"[,;:]+$", "", " ".join(w[:i]))
    return None


def _nd_thing(said: str) -> str | None:
    w = _nd_words(said)
    for i in range(1, len(w)):
        x = ll.clean(w[i])
        if x in ll.RELATIVE or x in ll.SUBJECTS or x in ll.PREPOSITIONS or w[i - 1].endswith(","):
            return re.sub(r"[,;:]+$", "", " ".join(w[:i]))
    return None


def _nd_plural_base(base: str) -> bool:
    head = None
    for word in _nd_words(base):
        x = ll.clean(word)
        if head is not None and (x in ll.PREPOSITIONS or x in ll.RELATIVE or x in ll.SUBJECTS):
            break
        head = x
    return head is not None and ll.is_plural(head)


def _nd_names_the_measure(thing: str, measure) -> bool:
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    shared = set(writers_mod.roots(thing)) & set(writers_mod.roots(measure or ""))
    return bool(shared) and without_the_measure(thing, measure or "") == thing.strip()


def _seen_go(opening, base, per: str, measure) -> list[str]:
    asked = "what percent of " + base if base is not None else "how many " + str(measure)
    return [f"{opening}, {about}{asked}{unit} did you see go?" for unit in ([per, ""] if per else [""])
            for about in ("about ", "")]


def _as_typed_rungs(opening, cost: dict, base, per: str, measure) -> list[str]:
    """`LossNotDone.asTypedRungs`: the founder's own line said to the person -- *... what percent of {base} was|were
    {line}?*, *... how many {line} were there?*, a count whose line names a thing other than the measure *in how many
    {measure} did you not get {thing}?* -- given way: the line whole, without its purpose, cut before its first clause or
    place, then its thing alone; a line that is only the base the words that set it apart, else *did you see go?*."""
    line = ll.lower_first(re.sub(r"[.!?]+$", "", str(cost.get("lossPhrase") or "").strip()))
    said = "" if not line.strip() else ll.past(ll.second_person(line, False))
    rungs: list[str] = []
    if base is not None and same_words(line, base):
        content, plain = [], True
        for word in _nd_words(said):
            x = ll.clean(word)
            if x in ll.DETERMINERS:
                continue
            plain = plain and x not in ll.PREPOSITIONS and x not in ll.RELATIVE and x not in ll.SUBJECTS \
                and x not in ll.SUBORDINATORS and not ll.verb_like(x)
            content.append(x)
        if plain and 2 <= len(content) <= 4:
            head = content[-1]
            rungs.append(f"{opening}, about what percent of the {head}{per}"
                         + (" were " if ll.is_plural(head) else " was ") + " ".join(content[:-1]) + "?")
        rungs += _seen_go(opening, base, per, None)
        return [r for r in rungs if banned_word(r) is None]
    forms = [said] if said.strip() else []
    shorter = None if not said.strip() else without_purpose(said)
    if shorter is not None:
        forms.append(shorter)
    cut = _nd_cut_at_a_place(said)
    if cut is not None:
        forms.append(cut)
    thing = None if not said.strip() else _nd_thing(said)
    if thing is not None:
        forms.append(thing)
    be = " were " if base is not None and _nd_plural_base(base) else " was "
    if base is None and thing is not None and not _nd_names_the_measure(thing, measure):
        said1 = without_the_measure(thing, measure or "")
        for unit in ([per, ""] if per else [""]):
            for about in (True, False):
                rungs.append(f"{opening}, in {'about ' if about else ''}how many {measure}{unit} did you not get "
                             f"{said1}?")
        rungs = [r for r in rungs if banned_word(r) is None]
        if rungs:
            return rungs
    distinct = list(dict.fromkeys(forms))
    for unit in ([per, ""] if per else [""]):
        for form in distinct:
            for about in (True, False):
                rungs.append(f"{opening}, {'about ' if about else ''}what percent of {base}{unit}{be}{form}?"
                             if base is not None else
                             f"{opening}, {'about ' if about else ''}how many {form} were there?")
    rungs = [r for r in rungs if banned_word(r) is None]
    if not rungs:
        rungs = _seen_go(opening, base, per, measure)
    return rungs


def loss_not_done(opening, cost: dict, base, per: str, measure) -> tuple[str | None, bool]:
    """keel-cloud 239 FR-2 (`LossNotDone.of`): the item code serves for a rate cost the writer could not ask -- `(stem,
    as_typed)`: the plain not-done where the line has a verb code can say so, else the founder's own line said to the
    person (`as_typed`, which the founder's Check notes; True only where a line was typed)."""
    rungs = _not_done_rungs(opening, cost, base, per, measure)
    if rungs:
        return _nd_held(rungs), False
    typed = not _blank(cost.get("lossPhrase"))
    return _nd_held(_as_typed_rungs(opening, cost, base, per, measure)), typed


def loss_not_done_rungs(opening, cost: dict, base, per: str, measure) -> list[str]:
    """`LossNotDone.rungs`: every rung `loss_not_done` can serve, in its order -- the banned-word test reads each."""
    return _not_done_rungs(opening, cost, base, per, measure) + _as_typed_rungs(opening, cost, base, per, measure)


def typed_unit(cost: dict | None) -> str | None:
    """`CommercialChain.typedUnit`: the founder's typed unit, or None."""
    return None if not isinstance(cost, dict) or _blank(cost.get("unit")) else str(cost["unit"]).strip()


def per_unit(cost: dict, team: bool, counted) -> str:
    """keel-cloud 239 FR-5 (`CommercialChain.perUnit`): the typed unit as the decision-maker's question says it, *" per
    cluster"* -- once: nothing where `counted` already names it, on a consumer link, or where none was typed (or it runs
    past three words)."""
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    unit = typed_unit(cost) if team else None
    if unit is None or ll.words(unit) > 3:
        return ""
    if counted is not None and set(writers_mod.roots(counted)) & set(writers_mod.roots(unit)):
        return ""
    return " per " + unit


def line_base(cost: dict | None) -> str | None:
    """keel-cloud 239 FR-4 (`CommercialChain.lineBase`): the plain base the loss line names (a share's thing *on* a noun
    phrase and nothing after it) where the typed base does not name it; else None."""
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    if not isinstance(cost, dict) or cost.get("mode") != "RATE":
        return None
    measure = cost_measure(cost)
    if measure is not None and measure.strip() != "%":
        return None
    read = ll.read(cost.get("lossPhrase"))
    if read is None or read.shape != ll.NONE or not read.clause.strip():
        return None
    w = read.clause.strip().split()
    if len(w) < 2 or ll.clean(w[0]) != "on":
        return None
    for word in w[1:]:
        x = ll.clean(word)
        if x in ll.RELATIVE or x in ll.SUBORDINATORS or x in ll.PREPOSITIONS or x in ll.SUBJECTS or ll.verb_like(x) \
                or word.endswith(","):
            return None
    phrase = re.sub(r"[.;:]+$", "", " ".join(w[1:])).strip()
    typed = str(cost.get("base") or "")
    if set(writers_mod.roots(phrase)) & set(writers_mod.roots(typed)) or same_words(phrase, typed):
        return None
    return phrase if ll.clean(w[1]) in ll.DETERMINERS else "the " + phrase


def asked_base(cost: dict | None) -> str | None:
    """keel-cloud 239 FR-4 (`CommercialChain.askedBase`): the base the stranger's item asks on -- the one the loss line
    names, where it names a plain one, else the base the founder typed."""
    if not isinstance(cost, dict):
        return None
    typed = None if _blank(cost.get("base")) else str(cost["base"]).strip()
    line = line_base(cost)
    return line if line is not None else typed


def base_note(cost: dict | None) -> str | None:
    """keel-cloud 239 FR-4 (`CommercialChain.baseNote`): the Check's line where the item asks on the line's base."""
    line = line_base(cost)
    return None if line is None else f"People are asked about {line}, the base your loss line names."


#: keel-cloud 239 FR-2 (`CommercialChain.AS_TYPED_NOTE`): the Check note's opening words.
AS_TYPED_NOTE = "Keel couldn't name what they see go in your loss line, so people are asked:"


def check_note(team: bool, occasion, cost: dict | None, served: str | None) -> str | None:
    """keel-cloud 239 FR-2 (`CommercialChain.checkNote`): the founder's Check note on Existing sacrifice where the item
    the people are served is the founder's own line said to them -- *Keel couldn't name ... "{served}" Reword it as what
    happens to the thing, in their words.* -- None everywhere else."""
    if served is None or not isinstance(cost, dict) or cost.get("mode") != "RATE":
        return None
    over = cost.get("period") if cost.get("period") in _COST_OPENERS else "month"
    base = None if asked_base(cost) is None else _said(asked_base(cost), team)
    rate = _rate_stem(_COST_OPENERS[over], ll.occasion_noun(occasion), team, base, cost)
    if not rate[4] or served != rate[0]:
        return None
    return f'{AS_TYPED_NOTE} "{served}" Reword it as what happens to the thing, in their words.'


def sacrifice_note(team: bool, occasion, cost: dict | None, served: str | None) -> str | None:
    """keel-cloud 239 FR-2, FR-4 (`VectorsController.sacrificeNote`, keel-web 183 T008's shape): the note the Existing
    sacrifice row of the founder's Check carries -- `base_note` then `check_note`, one space -- or None."""
    parts = [n for n in (base_note(cost), check_note(team, occasion, cost, served)) if n]
    return " ".join(parts) or None


def framed_per(cost: dict, team: bool) -> str:
    """keel-cloud 239 FR-5 (`CommercialChain.framedPer`): the typed unit as the clause's frame says it on the link."""
    measure = cost_measure(cost)
    share = measure is None or measure.strip() == "%"
    base = None if asked_base(cost) is None else _said(asked_base(cost), team)
    return per_unit(cost, team, base if share else measure.strip())


def cost_question(team: bool, occasion, job, cost: dict, loss_clause: str | None = None) -> str:
    """`CommercialChain.costQuestion(team, circumstance, occasion, job, period, cost)` on a chain cost (spec 110 FR-3,
    keel-cloud 170 FR-5): the stranger's cost question in their own terms, held to the spoken cap by each frame's
    give-way ladder. HOURS *spend on* the thing (or the time gone without); RATE the founder's loss line's verb and thing
    (`LossLine`) -- a share of the base, a count of the thing; MONEY *what did ... cost*. Spec 132 FR-9 (keel-cloud 206
    FR-5): never *miss* -- a line whose verb is *lose*'s or *miss*'s asked by the event it names (*rang out*), a two-part
    verb by its seen half (*never use*), a line with no verb of its own *go without* (time, money, a thing) or *fell
    through* (a counted thing); a percent box asked *what percent of*, never *how much*. `team` is the decision-maker's
    link (`corridor.isB2b()`).Spec 141 FR-7 (keel-cloud 222 FR-4): `loss_clause`, the writer's, framed where code's own
    reading of the line falls to a neutral verb (`_rate_stem`); None, or a line code reads, and the question is as
    before."""
    over = cost.get("period") if cost.get("period") in _COST_OPENERS else "month"
    opening = _COST_OPENERS[over]
    base = None if _blank(cost.get("base")) else _said(str(cost["base"]), team)
    if cost.get("mode") == "RATE" and asked_base(cost) is not None:
        base = _said(asked_base(cost), team)          # spec 148 FR-3 (keel-cloud 239 FR-4): the line's base
    noun = ll.occasion_noun(occasion)
    doing = None if _blank(job) else _said(str(job).strip(), team)
    unit = str(cost["unit"]).strip() if team and not _blank(cost.get("unit")) else None
    ladder: list[str] = []
    if cost.get("mode") == "HOURS":
        missed = None if cost.get("base") is None else gone_without(cost.get("base"))
        if missed is not None:
            # spec 148 FR-3 (keel-cloud 239 FR-2): never *go without* served -- the plain not-done
            ladder.append(f"{opening}, about how many hours of {_said(missed, team)} did {_who(team, missed)} "
                          "not get?")
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
        # spec 141 FR-7 (keel-cloud 222 FR-1, FR-4): where code's own reading of the line falls to a neutral verb, the
        # writer's clause in its place (`loss_clause_question`); everywhere else the ladder's own stem, word for word
        served, wanted, share, measure, _, per = _rate_stem(opening, noun, team, base, cost)
        written = loss_clause_question(opening, loss_clause, base if share else None, None if share else measure,
                                       per) if wanted else None
        return written if written is not None else served
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
        # spec 148 FR-3 (keel-cloud 239 FR-4, FR-5): the base the item asks on; the typed unit kept, said once
        base = asked_base(cost) if asked_base(cost) is not None else \
            str(cost["base"]).strip() if not _blank(cost.get("base")) else ll.occasion_noun(occasion)
        if not team:
            return ("% " + ("" if base is None else "of " + _said(base, False))).strip()
        of = "" if base is None else _without_possessive(base)
        return ("% " + ("" if base is None else "of " + of + per_unit(cost, True, of) + " ")
                + _label_time(period, None)).strip()
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
    # spec 141 FR-7 (keel-cloud 222 FR-2): the writer's clause off the scripted part-1 result, where it carries one
    return {"question": cost_question(team, entry.occasion(), ctx.get("job"), cost, scripted_loss_clause(entry)),
            "label": label,
            "nothing": {"code": "NOTHING", "label": VALUE_BOX_LABELS["NOTHING"]},
            "chips": [{"code": c, "label": VALUE_BOX_LABELS[c]} for c in value_box_escapes(not team)],
            "escape": {"code": "DONT_KNOW", "label": VALUE_BOX_LABELS["DONT_KNOW"]},
            "optionsLine": value_box_answer_line(cost, label), "escapeLine": "Or say you can't recall."}


def value_box_answer_line(cost: dict, label) -> str:
    """`CommercialChain.valueBoxAnswerLine` (keel-cloud 170 FR-5): the value box's spoken answer line names the label --
    *A percent of GPU hours last month.* -- where `SpokenForm.VALUE_BOX_ANSWER_LINE` said *in the unit on the screen*.
    Since keel-cloud 198 FR-3 the unit alone (it read *..., or a low and a high; none is 0.*, `value_box_answer_line_170`
    on a lock stored before 198)."""
    text = "" if label is None else str(label).strip()
    if cost.get("mode") in _MONEY_MODES:
        what = "An amount" + ("" if not text else " " + text)
    elif text.startswith("% "):
        what = "A percent " + text[2:].strip()
    elif text == "%":
        what = "A percent"
    else:
        what = "A number" + ("" if not text else " of " + text)
    return what + "."


def value_box_answer_line_170(cost: dict, label) -> str:
    """keel-cloud 170 to 197's answer line, *..., or a low and a high; none is 0.* (read on a lock stored before 198)."""
    return value_box_answer_line(cost, label)[:-1] + ", or a low and a high; none is 0."
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
        # spec 133 FR-2 (keel-cloud 118 FR-1, `SavedList.codeFor`): the step, then the smaller step its second yes is
        # written from (the harness sent *step* twice; the cloud's code is positional, so nothing it stored moved)
        return "step" if index == 0 else "smaller_step"
    return f"item_{index + 1}"


def founder_list(entry, key: str) -> dict:
    """The entry's own saved list for a list dimension: `{items: [{code, label, asked?}], picked, phrase}`."""
    saved = entry.founder_list(key)
    if not saved or not saved["items"]:
        raise VectorsScriptError(f"{entry.id}: {key} carries no founder list; a list dimension is drafted "
                                 "from one")
    return saved


def offer_rows(entry) -> list[str]:
    """Spec 132 FR-2 (keel-cloud 205 FR-1, `L32`): the Purchase friction rows the entry types that name the founder's own
    offer (a trial, a pilot, a guarantee, onboarding, money back: `instructions.friction.founders_offer`), in its order --
    what keel-cloud leaves off the list with a note (`FounderReason` L32), never an `L23`. No golden entry types one;
    since corpus revision 24 (keel-cloud 215, spec 135 FR-2) no gallery entry does either (08-fresco's and 21-codyco's
    own trials dropped, 14-code-four's and 17-expanse's reworded into the buyer's own step); five entries outside the
    gallery still do (22-andy-ai, 25-bidflow, 26-cubic, 27-blacksmith, 28-relvy-ai)."""
    from instructions import friction as friction_mod                  # noqa: PLC0415
    saved = entry.founder_list(PURCHASE_FRICTION_KEY) if hasattr(entry, "founder_list") else None
    return [i["label"] for i in (saved or {}).get("items") or [] if friction_mod.founders_offer(i.get("label"))]


#: Spec 135 FR-2: what the walk expects of `L32` on an entry that types no own-offer row -- reported, never asserted.
NO_OFFER_TYPED = "no own-offer row typed"


def offer_expectation(entry) -> str:
    """Spec 135 FR-2: the walk's `L32` expectation, reported in the transcript (`own_offer`) and never asserted --
    *no own-offer row typed* (every gallery entry since revision 24), else the rows the cloud is owed a note on."""
    rows = offer_rows(entry)
    return NO_OFFER_TYPED if not rows else "L32 owed on: " + "; ".join(rows)


def kept_items(entry, key: str) -> list[tuple[int, dict]]:
    """Spec 132 FR-2: the entry's list items the cloud keeps, `(index in the entry's list, item)` -- every item, but on
    Purchase friction the rows naming the founder's own offer (`offer_rows`), left out by keel-cloud 205's `L32`."""
    items = list(enumerate(founder_list(entry, key)["items"]))
    if key != PURCHASE_FRICTION_KEY:
        return items
    offers = set(offer_rows(entry))
    return [(i, item) for i, item in items if item.get("label") not in offers]


def kept_picked(entry, key: str) -> int | None:
    """Spec 132 FR-2 / FR-3 / FR-10: the picked index on the list as the cloud keeps it (`kept_items`) -- the entry's own
    pick; on Purchase friction, where the entry picked a row naming the founder's own offer (left out, `L32`), the
    first row kept (08-fresco and 14-code-four picked their trial at revision 23; since revision 24 no gallery entry
    types one, and 08-fresco's pick is `procore_check` itself, index 0 of two); on Buyer and payer the walker's pick
    (`buyer_payer_pick`). None where the list picks nothing."""
    saved = founder_list(entry, key)
    picked = saved.get("picked")
    if key == BUYER_PAYER_KEY:
        return buyer_payer_pick(entry)
    if picked is None or key != PURCHASE_FRICTION_KEY:
        return None if picked is None else int(picked)
    kept = [i for i, _ in kept_items(entry, key)]
    return kept.index(int(picked)) if int(picked) in kept else (0 if kept else None)


#: keel-cloud's Buyer and payer key (spec 132 FR-3 / FR-10).
BUYER_PAYER_KEY = "commercial.buyer_payer_alignment"


def buyer_payer_roles(entry) -> list[str]:
    """The roles the entry's Buyer and payer Answer names (every label but *Nobody else*), in its order."""
    saved = entry.founder_list(BUYER_PAYER_KEY) if hasattr(entry, "founder_list") else None
    return [i["label"] for i in (saved or {}).get("items") or [] if i.get("code") != NOBODY_ELSE[0]]


def buyer_payer_pick(entry) -> int:
    """Spec 132 FR-3 / FR-10 (keel-cloud 205's card, keel-web 168 FR-3): the index the walker picks on Buyer and payer's
    Choose -- 1, the one option holding every role the Answer names, wherever it names one (never *Nobody else*: Palus's
    corpus picks *Nobody else* beside *The board*, and the card says the board must agree first); 0, *Nobody else*,
    only where the Answer names nobody (then the list holds only *Nobody else* and the screen is a statement to
    confirm, sent as 0). Never by a role's label."""
    return 1 if buyer_payer_roles(entry) else 0


#: Spec 133 FR-2 (keel-cloud 211 FR-6, `L34`; the registry's Commitment guidance: *the obvious smaller step that costs
#: nothing and comes first ..., a noun phrase naming the same product ..., named by Keel with its reason*): the free
#: smaller step the scripted writer names where the entry's step costs the person money, data or a signature and its
#: list is the step alone -- keel-cloud's own words for Keel's step on such a list (`AfterTheReRunsTest`, Karsa's *a look
#: at how it works*); no trade's word, the same on every entry.
KEELS_SMALLER_STEP = "a look at how it works"


def keels_smaller_step(entry) -> dict | None:
    """Spec 133 FR-2 (keel-cloud 211 FR-6, `L34`): Commitment's second item as the scripted writer names it --
    `{label, reason}`, `KEELS_SMALLER_STEP` and why, in one sentence, the step costs the person something
    (`instructions.step_cost`) -- where the entry's list is its step alone and that step costs money, data or a
    signature (*pay*, *paid pilot*, *order*, *buy*, *read access*: eleven back-test entries; since keel-cloud 221 a data
    act too, *install*, *let it measure*); None where the step costs
    nothing or the entry's list already carries a smaller step (the golden 02, 03, 06). Since 211 `L19` keeps it (it
    drops Keel's step only where the step costs nothing) and `L7` reads its reason, so the draft spends no repair turn
    and the founder saves both rows, as the Check screen draws them."""
    from instructions import step_cost as step_cost_mod                # noqa: PLC0415
    saved = entry.founder_list(COMMITMENT_KEY) if hasattr(entry, "founder_list") else None
    items = (saved or {}).get("items") or []
    if len(items) != 1:
        return None
    step = str(items[0].get("label") or "")
    cost = step_cost_mod.of(step)
    if cost is None:
        return None
    return {"label": KEELS_SMALLER_STEP,
            "reason": f"'{step}' costs the person {cost.kind} ('{cost.word}'), so a smaller step that costs nothing "
                      "is offered first"}


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
    items in its order -- Buyer and payer's "Nobody else" left to code, which adds it -- each `label` and Current
    solution's `phrase`. **Spec 154 FR-0 (keel-cloud 245 FR-1): the draft carries no stranger's face and no condition**
    -- `asked` and `only_if` are the Save's ASKED job's to write for every row (ignored if sent) -- so Compatibility's
    and Adoption friction's rows are labels alone; the corpus face is still read for the row's `kind` (L-kind) and the
    stub's answer (`asked_result`)."""
    saved = founder_list(entry, key)
    items = []
    cap = ROW_CAP.get(key)
    # spec 132 FR-2 (keel-cloud 205 FR-1): the scripted writer leaves a Purchase friction row naming the founder's own
    # offer out, as the cloud's applier asks (`L32`: drafted, one repair turn; typed and left out, a note, never `L23`)
    for _, item in kept_items(entry, key):
        if key == "commercial.buyer_payer_alignment" and item.get("code") == NOBODY_ELSE[0]:
            continue
        # spec 131 (keel-cloud 204 FR-2): a corpus row over the row cap is refused once, then cut at the cap -- the
        # scripted writer's draft carries it cut (`RowCap.cut`), so the Check screen is always saveable
        from instructions import spoken as spoken_mod                 # noqa: PLC0415
        out = {"label": spoken_mod.row_cap_cut(item["label"], cap) if cap else item["label"]}
        if key in ASKED_FACES and not item.get("asked"):
            # the corpus still records a face per row (L4): the stub's ASKED answer reads it (`asked_result`)
            raise VectorsScriptError(f"{entry.id}: {key} item {item['label']!r} carries no `asked` face (L4)")
        # spec 154 FR-0 (keel-cloud 245 FR-1): no `asked` on the draft -- the Save's ASKED job phrases every row -- and no
        # `only_if` (132 FR-7's K8 on the draft is 245's: the condition comes back with the face from the asked job)
        if key == COMPATIBILITY_KEY:
            # spec 136 FR-3 (keel-cloud 212 FR-4, L35): each condition shows its test -- the corpus's conditions are the
            # ones the study tests, so every row is settled by nobody
            out["settled_by"] = "nobody"
            # spec 141 FR-8 (keel-cloud 225 FR-1, L-kind): the kind beside it, the word test's own reading
            # (`spoken.condition_kind`) -- today's frame kept, and no L-kind repair turn spent
            out["kind"] = spoken_mod.condition_kind(item["asked"], out["label"]).lower()
        items.append(out)
    if key == COMMITMENT_KEY and keels_smaller_step(entry):
        # spec 133 FR-2 (keel-cloud 211 FR-6, L34): a step that costs money, data or a signature carries Keel's free
        # smaller step with its reason (L7), so the draft spends no repair turn
        items.append(dict(keels_smaller_step(entry)))
    if key == "problem.importance":
        items = items[:1 + len(importance_named(entry))]     # Keel adds only what the Answer named (097 F9)
    # spec 129 (keel-cloud 200 FR-1): each row's hidden short name where the scripted writer can name it
    names = row_short_names(entry, key)
    for out in items:
        if names.get(out["label"]):
            out["short_name"] = names[out["label"]]
    draft: dict = {"items": items}
    own = list_short_name(entry, key)
    if own:
        draft["short_name"] = own
    if key == "problem.current_solution_satisfaction":
        if not saved.get("phrase"):
            raise VectorsScriptError(f"{entry.id}: {key} carries no phrase (L1)")
        # spec 093 FR-1 (keel-cloud 161 FR-1): the draft writes the act bare, as the model now does -- the corpus's
        # *your way of ...* read with the opening stripped (`ItemFrames.bare`), so no scripted draft earns an `L1` note
        draft["phrase"] = bare_phrase(saved["phrase"])
        # spec 064 FR-5a (keel-cloud 117): the leading rungs the founder typed, kept verbatim, and the line after D4's 2;
        # spec 131 (keel-cloud 203 FR-1, FR-2): with Keel's working rung above them, the line under it (1)
        rungs = founder_rungs(entry)
        if rungs:
            draft["founder_rungs"] = rungs
            draft["line"] = 1 if keels_working_first(entry) else min(2, rungs)
    return draft


#: keel-cloud 206 (`AskedRules.ONLY_IF_MAX_WORDS`, K7): a condition is 1 to 7 words read after *Only if*.
ONLY_IF_MAX_WORDS = 7
#: keel-cloud 198 FR-9 / 206 (`AskedRules.EVERY_STEP`, `WORTH`): what a condition never says -- true of every step.
_EVERY_STEP = re.compile(r"(?i)\b(?:easy|easier|simple|quick|quickly|saved? (?:me |us )?(?:time|money)|saves (?:me |us )?"
                         r"(?:time|money)|it worked well|it works well|worked well|helped me|helps me)\b|\bworth")
#: The scripted condition's tail: what the step risks in their work (keel-cloud 206 `ONLY_IF_RULE`: *what this step
#: risks or clashes with in their work, never true of every step*). Spec 139 FR-2 (keel-cloud 216 FR-5, K12): read as the
#: assurance -- a negated slow-down, no danger word (`assurance_fault`).
_CONDITION_TAIL = "never slowed my work"
#: `AskedRules.RISK` (keel-cloud 216 FR-5, K12): the words that name the danger the person fears.
RISK = re.compile(r"(?i)(?<![^\W\d_'])(?:risks?|fails?|failing|lose|loses|losing|breaks?|wrong|miss|misses|crash|"
                  r"crashes|down|needs? my|needs? your|judgement|judgment)(?![^\W\d_'])")
#: `AskedRules.NEGATED` (K12): a negation before the risk word turns it into the assurance.
NEGATED = re.compile(r"(?i)(?<![^\W\d_'])(?:not|no|never|without|nothing|none|[^\W\d_]+n['\u2019]t)(?![^\W\d_'])")


def assurance_fault(words: str | None) -> str | None:
    """`AskedRules.assuranceFault` (keel-cloud 216 FR-5, `K12`): a condition naming the danger the person fears (*they
    risk my job failing*, *missed calls need your own judgement*) -- a `RISK` word with no negation before it -- cannot be
    answered as a conditional Yes; refused as K7's faults are (past the repair turn the item is served with *Yes, if it
    was clearly worth it*). None where it names none, or each one it names is negated."""
    text = str(words or "")
    for risk in RISK.finditer(text):
        if not NEGATED.search(text[:risk.start()]):
            return (f"K12: 'Only if {text}' names the danger the person fears ('{risk.group()}'); the condition is what "
                    "would make this person say Yes -- what Keel has to do or promise, not what they fear (Only if it "
                    "hands me the hard calls; Only if failed jobs fall back to my numbers)")
    return None


def adoption_condition(item: dict) -> str:
    """Spec 132 FR-7 (keel-cloud 206 FR-4, `ONLY_IF_RULE`): the scripted writer's `only_if` for one Adoption friction
    item -- the entry's own condition where it records one (`condition` / `only_if`), else one tied to the step's risk:
    the step said as an -ing phrase (`gerund`) and *never slowed my work* -- what this step could break or slow in their
    work -- within K7's seven words (a step over three words said by its verb alone, or its two joined verbs: *wearing
    never slowed my work*, *checking and fixing never slowed my work*), never a word true of every step (*easy*,
    *quick*, *saves time*, *worth*). No trade's word: the step's own."""
    own = item.get("condition") or item.get("only_if")
    if own and str(own).strip():
        return str(own).strip()
    room = ONLY_IF_MAX_WORDS - len(_CONDITION_TAIL.split())
    said = gerund(str(item.get("label") or "")).split()
    if 0 < len(said) <= room:
        head = " ".join(said)
    elif len(said) >= 3 and said[1].lower() == "and":
        head = " ".join(said[:3])                                  # *checking and fixing*
    else:
        head = said[0] if said else "it"
    condition = f"{head} {_CONDITION_TAIL}"
    return condition if not _EVERY_STEP.search(condition) else f"it {_CONDITION_TAIL}"


#: keel-cloud 204 (FR-1): each founder list's row cap, the registry's `founder.saves.max_words` (9; Compatibility's
#: conditions 16; Buyer and payer's roles 4) -- held to the registry by test.
ROW_CAP = {"problem.importance": 9, "problem.current_solution_satisfaction": 9, "solution.compatibility": 16,
           "solution.relative_advantage": 9, "solution.adoption_friction": 9, "commercial.buyer_payer_alignment": 4,
           "commercial.purchase_friction": 9, "commercial.commitment": 9}


def keels_working_first(entry) -> bool:
    """keel-cloud 203 (FR-1, `FoundersRungs.keelsWorkingFirst`): whether Current solution's first rung is Keel's working
    outcome written above the founder's own -- where the entry's Answer types only shortfalls, its saved list carries
    the working rung on top marked `keel: true` (the founder never typed it). Such a first rung must read as working and
    the founder's first must be a shortfall (`WorkingRung`), else the entry is refused by name."""
    saved = entry.founder_list("problem.current_solution_satisfaction") if hasattr(entry, "founder_list") else None
    items = (saved or {}).get("items") or []
    if not items or not items[0].get("keel"):
        return False
    if len(items) < 2 or not working_rung_mod.works(items[0]["label"]) or working_rung_mod.works(items[1]["label"]):
        raise VectorsScriptError(f"{entry.id}: problem.current_solution_satisfaction's first rung is marked Keel's "
                                 "(`keel: true`): it must read as today's way working and stand above founder rungs "
                                 "that are shortfalls (keel-cloud 203 FR-1)")
    return True


def founder_rungs(entry) -> int:
    """How many of Current solution's outcomes the founder's Answer types (`answer_text`: the phrase, then as many whole
    labels as fit in 25 words) -- keel-cloud 117's `founder_rungs` (2 or 3 on every golden entry), counted from the top
    (`FoundersRungs.leading`): below Keel's working rung where it stands first (keel-cloud 203), only the founder's own."""
    key = "problem.current_solution_satisfaction"
    saved = founder_list(entry, key)
    top = 1 if keels_working_first(entry) else 0
    labels = [i["label"] for i in saved["items"]][top:]
    # spec 118 (keel-cloud 184 FR-8b (a)): the rungs are typed in the second box, *how it goes*, as its own sentence
    typed = current_solution_boxes(entry)[1].rstrip(".").split("; ")
    n = 0
    for label in labels:
        if label not in typed:
            break
        n += 1
    return n


def _same_words(a: str | None, b: str | None) -> bool:
    return " ".join(str(a or "").lower().split()).rstrip(".") == " ".join(str(b or "").lower().split()).rstrip(".")


# ------------------------------------------------------------- spec 143 FR-2: a list the review changed (keel-cloud 232)
#
# keel-cloud 232 FR-3 (contract 62), behind spec 209's review switch: a saved row the review changed carries the
# founder's own words as `typed` and the review's sentence as `why` (`label` is the row as changed, what strangers
# hear); a row the review put aside sits in the list's `putAside` (`{typed, why}`, camelCase on the wire; `put_aside`
# read too); `changed` is code's band, `{line, why}`. The walk counts a founder's row present when a row's `label` or
# its `typed` is the founder's words, or a put-aside row's `typed` is; it never presses Put back and never retypes a
# changed row. Generic over every list: no dimension is named here.

def _served(saved) -> dict:
    return saved if isinstance(saved, dict) else {}


def put_aside_of(saved) -> list[dict]:
    """The list's put-aside rows (`putAside`, or `put_aside`), in order; `[]` where none is served."""
    lst = _served(saved)
    rows = lst.get("putAside") if lst.get("putAside") is not None else lst.get("put_aside")
    return [r for r in rows or [] if isinstance(r, dict)]


def served_items(saved) -> list[dict]:
    return [i for i in _served(saved).get("items") or [] if isinstance(i, dict)]


def typed_is(want: str | None, row) -> bool:
    """Spec 143 FR-2: whether a served row (an item, or a put-aside row) is one the review changed from the founder's
    `want` -- its `typed` is their words."""
    return isinstance(row, dict) and bool(row.get("typed")) and _same_words(want, row.get("typed"))


def row_present(want: str, saved) -> bool:
    """A founder's row is on the served list: an item whose `label` is their words, or whose `typed` is (the review
    changed it), or a put-aside row whose `typed` is (the review put it aside) -- read as `_same_words` reads them."""
    return any(_same_words(want, i.get("label")) or _same_words(want, i.get("typed")) for i in served_items(saved)) \
        or any(_same_words(want, r.get("typed")) for r in put_aside_of(saved))


def missing_rows(wants: list[str], saved) -> list[str]:
    """The founder's rows (`wants`, in order) not on the served list by `row_present`."""
    return [w for w in wants if not row_present(w, saved)]


def held_by_review(wants: list[str], saved) -> list[str]:
    """The founder's rows the review holds: changed (an item's `typed`) or put aside -- present, never typed again."""
    return [w for w in wants if any(_same_words(w, i.get("typed")) for i in served_items(saved))
            or any(_same_words(w, r.get("typed")) for r in put_aside_of(saved))]


def typed_by_label(*lists) -> dict[str, str]:
    """`{served label: the founder's typed words}` over the changed rows of every list given (a question's `draft` and
    its saved `answer.list`), the first list's first."""
    out: dict[str, str] = {}
    for saved in lists:
        for i in served_items(saved):
            if i.get("typed") and i.get("label") and i["label"] not in out:
                out[i["label"]] = i["typed"]
    return out


def review_changed(saved) -> list[dict]:
    """Spec 143 FR-2: what the review did to one list, for `backtest.json` -- every changed row `{typed, label, why}` in
    the list's order, then every put-aside row `{typed, label: None, why}`; `[]` on a list the review left alone.

    Spec 149 FR-2 (keel-cloud 243 FR-4, contract 64): a put-aside row carries `replacedBy` (Keel's row standing in its
    place, read off the rows) and `keels` (its words were Keel's) where served, a changed row `typedKeels` (the words
    behind Put back were Keel's) -- each key absent where none is served, so a list before 243 reads as 143 wrote it.
    Keel's rows in place are counted apart (`review_in_place`), never as a changed row."""
    out = []
    for i in served_items(saved):
        if i.get("typed"):
            row = {"typed": i.get("typed"), "label": i.get("label"), "why": i.get("why")}
            if i.get("typedKeels"):
                row["typedKeels"] = True
            out.append(row)
    for r in put_aside_of(saved):
        row = {"typed": r.get("typed"), "label": None, "why": r.get("why")}
        by = replaced_by(r, saved)
        if by:
            row["replacedBy"] = by
        if r.get("keels"):
            row["keels"] = True
        out.append(row)
    return out


def in_place_of(item) -> str | None:
    """Spec 149 FR-2 (keel-cloud 243 FR-3, contract 64): the words of the row put aside that Keel's row stands in place
    of (`inPlaceOf`, `in_place_of` read too), or None."""
    if not isinstance(item, dict):
        return None
    said = item.get("inPlaceOf") if item.get("inPlaceOf") is not None else item.get("in_place_of")
    return said or None


def replaced_by(aside, saved) -> str | None:
    """Spec 149 FR-2 (keel-cloud 243 FR-4, `SavedList.replacedBy`): Keel's row standing in place of a put-aside row --
    the served `replacedBy`, else read off the rows (the item whose `inPlaceOf` is its words, case folded); None."""
    if not isinstance(aside, dict):
        return None
    served = aside.get("replacedBy") if aside.get("replacedBy") is not None else aside.get("replaced_by")
    if served:
        return served
    typed = " ".join(str(aside.get("typed") or "").lower().split())
    return next((i.get("label") for i in served_items(saved)
                 if in_place_of(i) and " ".join(in_place_of(i).lower().split()) == typed), None)


def review_in_place(saved) -> list[dict]:
    """Spec 149 FR-2 (keel-cloud 243 FR-3): Keel's rows standing in place of rows the review put aside, in the list's
    order -- `{label, inPlaceOf, why}` (`why` the served `suggestedWhy`); `[]` where none (a list before 243)."""
    return [{"label": i.get("label"), "inPlaceOf": in_place_of(i),
             "why": i.get("suggestedWhy") or i.get("suggested_why")}
            for i in served_items(saved) if in_place_of(i)]


def review_suggested(saved, draft=None) -> list[dict]:
    """Spec 147 FR-3 (keel-cloud 236 FR-2): the suggestion the review added at the Check -- a saved row served
    `suggested` with its why (`suggestedWhy`) whose label the Answer's draft (`draft`) does not carry, Keel's own (the
    draft's own suggested row, keel-cloud 121's mark on a founder's condition, is not this) -- as `{label, why}`, in the
    list's order; `[]` where none."""
    drafted = {" ".join(str(i.get("label") or "").lower().split()) for i in served_items(draft)}
    # spec 149 FR-3 (keel-cloud 243 FR-3): several now -- one in place of each row put aside (`inPlaceOf`, named), and
    # 236's at the end where nothing was put aside
    return [{"label": i.get("label"), "why": i.get("suggestedWhy") or i.get("suggested_why"),
             **({"inPlaceOf": in_place_of(i)} if in_place_of(i) else {})}
            for i in served_items(saved)
            if i.get("suggested") and (i.get("suggestedWhy") or i.get("suggested_why"))
            and " ".join(str(i.get("label") or "").lower().split()) not in drafted]


def as_drafted(saved) -> list[str]:
    """Spec 147 FR-3 (keel-cloud 236 FR-1): the served list's rows in the words they were saved with before the review
    -- each item's `typed` where the review changed it (a founder's row or Keel's), else its label -- then the put-aside
    rows' `typed`: every row present, whoever wrote it. Spec 149 FR-2 (keel-cloud 243 FR-3): Keel's row in place of a
    row put aside was never saved before the review (the row it stands for is, put aside) -- left out."""
    return [i.get("typed") or i.get("label") for i in served_items(saved) if not in_place_of(i)] + \
        [r.get("typed") for r in put_aside_of(saved)]


def review_band(saved) -> dict | None:
    """Spec 143 FR-2: the band's two sentences (`list.changed`: `line`, `why`), or None where none is served."""
    band = _served(saved).get("changed")
    if not isinstance(band, dict) or not band.get("line"):
        return None
    return {"line": band.get("line"), "why": band.get("why")}


def changed_over_cap(saved, cap: int) -> list[dict]:
    """Spec 143 FR-2: a changed row over the walk's own word cap (`cap`, the served `saves.maxWords`) -- a keel-cloud
    defect to file (232 holds a change to 9 words), never a retype: `{label, typed, words, cap}` each."""
    return [{"label": i.get("label"), "typed": i.get("typed"), "words": len(str(i.get("label") or "").split()),
             "cap": int(cap)}
            for i in served_items(saved) if i.get("typed") and len(str(i.get("label") or "").split()) > int(cap)]


def founder_words(saved) -> list[str]:
    """The served list read back to the founder's own words: each item's `typed` where the review changed it, else its
    `label`, then the put-aside rows' `typed` -- what the founder saved, whatever the review did. Spec 149 FR-2
    (keel-cloud 243 FR-3): Keel's row in place of a put-aside row is not the founder's (the row put aside is) -- left
    out."""
    return [i.get("typed") or i.get("label") for i in served_items(saved) if not in_place_of(i)] + \
        [r.get("typed") for r in put_aside_of(saved)]


def lists_reviewed(views: dict) -> dict:
    """Spec 143 FR-2: `{dimension: {"review_changed": [...], "band": {line, why} | None}}` over every saved list the
    calibration views (`{vector: GET calibration/{vector}}`) serve that the review changed -- `{}` where it changed
    none (the switch off, or nothing broke the card)."""
    out = {}
    for view in (views or {}).values():
        questions = view.get("questions") if isinstance(view, dict) else None
        for q in [q for q in questions or [] if isinstance(q, dict)]:
            saved = (q.get("answer") or {}).get("list")
            changed, band = review_changed(saved), review_band(saved)
            if changed or band:
                out[q.get("dimension")] = {"review_changed": changed, "band": band}
                # spec 149 FR-3 (keel-cloud 243 FR-3): Keel's rows in place, with the row each stands for (absent
                # where none, so a list before 243 reads as 143 wrote it)
                in_place = review_in_place(saved)
                if in_place:
                    out[q.get("dimension")]["in_place"] = in_place
    return out


# --------------------------------------- spec 149 FR-2: every read-back names its rows, and suggests in place (243)
#
# keel-cloud 243 (`RespondentReview.numbered`, `shiftOf`, `readBackReadings`, `ReviewedRows.held` / `floor`,
# `SavedList.replacedBy`, `ReviewedRows.changed`), mirrored on the harness's side so the staging shape of 2026-11-09 is
# guarded at this layer too: every read-back hands its rows `[{index, label}]` from 0 (Importance's rows, Current
# solution's rungs, Relative advantage's benefits and the ladder beside them; Compatibility's conditions were already
# numbered, 236); an answer whose indices run from 1 to the count handed is read shifted by one (`review.shift: 1`); an
# index outside both readings is a refusal line; beside each `drop` a `suggest` `{label, why}` stands where the dropped
# row stood (`inPlaceOf` on Keel's row, `replacedBy` on the row put aside, read off the rows); the floor counts only
# the drops with no row in their place; the band counts both. Generic over every list: no trade is named here, and
# code's word rules for a suggestion (`spokenFault`, `rowFault`, `pieceFault`) are keel-cloud's, never mirrored -- the
# mirror holds the places, the reasons and the counts.

#: The three read-backs 243 FR-1 numbers (the conditions' were numbered by 236): the dimension and the key the rows
#: are handed under.
READ_BACK_ROWS = {"problem.importance": "rows", "problem.current_solution_satisfaction": "rungs",
                  "solution.relative_advantage": "rows"}


def numbered(rows) -> list[dict]:
    """keel-cloud 243 FR-1 (`RespondentReview.numbered`): rows as the review is handed them -- `[{index, label}]` in
    order, the first index 0 (Importance's own row, Current solution's first rung, the lead benefit)."""
    return [{"index": i, "label": row} for i, row in enumerate(rows or [])]


def labels_of(handed) -> list[str]:
    """keel-cloud 243 FR-1 (`RespondentReview.labelsOf`): the labels of rows handed numbered, or as plain words (a job
    queued before 243)."""
    return [str(r.get("label")) if isinstance(r, dict) else str(r) for r in handed or []]


def read_back_context(dimension: str, rows, *, phrase: str | None = None, line_after: int | None = None,
                      clause: dict | None = None, ladder: dict | None = None) -> dict:
    """keel-cloud 243 FR-1: the `read_back` object of a read-back's context -- Importance `{rows}`, Current solution
    `{phrase, rungs, line_after}`, Relative advantage `{rows, clause, ladder}` (the ladder's `rungs` numbered too, 243
    judgement call 1) -- every row list handed `[{index, label}]` from 0."""
    key = READ_BACK_ROWS.get(dimension)
    if key is None:
        raise VectorsScriptError(f"{dimension}: no numbered read-back (243 FR-1 names Importance, Current solution and "
                                 "Relative advantage; Compatibility's conditions are 236's)")
    if key == "rungs":
        return {"phrase": phrase, "rungs": numbered(rows), "line_after": line_after}
    back: dict = {"rows": numbered(rows)}
    if dimension == "solution.relative_advantage":
        back["clause"] = clause
        back["ladder"] = None if ladder is None else {**ladder, "rungs": numbered(labels_of(ladder.get("rungs")))}
    return back


def review_shift(notes, count: int) -> int:
    """keel-cloud 243 FR-2 (`RespondentReview.shiftOf`): 1 where an answer's indices run from 1 to the count handed --
    none is 0 and the largest equals `count`, an index no 0-based reading has -- else 0."""
    indices = [int(n["index"]) for n in notes or [] if isinstance(n, dict) and isinstance(n.get("index"), (int, float))
               and not isinstance(n.get("index"), bool)]
    if not indices or count <= 0:
        return 0
    return 1 if min(indices) >= 1 and max(indices) == count else 0


def _suggestion(said) -> dict | None:
    if isinstance(said, dict) and isinstance(said.get("label"), str):
        return {"label": said["label"], "why": said.get("why") if isinstance(said.get("why"), str) else None}
    return None


def read_back_answer(answer, rows) -> dict:
    """keel-cloud 243 FR-2 / FR-3 (`RespondentReview.readBackReadings`): a read-back's answer as code reads it --
    `readings` (`{at, note, label, drop, suggest}` per note, `at` the row handed, shifted where the answer counted from
    1), `shift` (the log's `review.shift`), `refused` (one line per index outside both readings: *index 7 is outside the
    4 rows handed (0 to 3)*) and 236's top-level `suggest`."""
    rows = list(rows or [])
    notes = answer.get("notes") if isinstance(answer, dict) else None
    if not isinstance(notes, list):
        return {"readings": [], "shift": 0, "refused": [], "suggest": None}
    shift = review_shift(notes, len(rows))
    readings, refused = [], []
    for note in notes:
        if not isinstance(note, dict) or not isinstance(note.get("index"), (int, float)) \
                or isinstance(note.get("index"), bool):
            continue
        at = int(note["index"]) - shift
        if at < 0 or at >= len(rows):
            refused.append(f"index {int(note['index'])} is outside the {len(rows)} rows handed (0 to {len(rows) - 1}"
                           + (", the answer read from 1" if shift == 1 else "") + ")")
            continue
        readings.append({"at": at, "note": note.get("note") if isinstance(note.get("note"), str) else None,
                         "label": note.get("label") if isinstance(note.get("label"), str) else None,
                         "drop": note.get("drop") is True, "suggest": _suggestion(note.get("suggest"))})
    return {"readings": readings, "shift": shift, "refused": refused, "suggest": _suggestion(answer.get("suggest"))}


def read_back_notes(answer, rungs) -> list[tuple[str, str]]:
    """keel-cloud 243 FR-2 (`RespondentReview.readBackNotes`): the notes alone, each against the row it was written for
    (shifted as `read_back_answer` shifts) -- the first for an index said twice; a blank note, an index outside the
    rows, or a note that only says the row again is none."""
    rungs = list(rungs or [])
    notes = answer.get("notes") if isinstance(answer, dict) else None
    if not isinstance(notes, list):
        return []
    shift = review_shift(notes, len(rungs))
    by_index: dict[int, tuple[str, str]] = {}
    for note in notes:
        words = note.get("note") if isinstance(note, dict) else None
        if not isinstance(words, str) or not words.strip() or not isinstance(note.get("index"), (int, float)):
            continue
        at = int(note["index"]) - shift
        if at < 0 or at >= len(rungs) or at in by_index \
                or re.sub(r"[.!]+$", "", words.strip()).lower() == rungs[at].strip().lower():
            continue
        by_index[at] = (rungs[at], words)
    return [by_index[k] for k in sorted(by_index)]


def in_place_applied(rows, readings, *, floor: int, first_fixed: bool = True) -> dict:
    """keel-cloud 243 FR-3 (`ReviewedRows.rows` / `benefits` / `conditions`, the places, the floor and the pair): the
    list a read-back's answer comes to -- `{items, putAside, notes, refused}` in the wire's shape (contract 64). Each
    `drop` puts its row aside with its own note as the why; a `suggest` beside it stands where the dropped row stood
    (`suggested`, `suggestedWhy`, `inPlaceOf` the row's words; the put-aside carries `replacedBy`); a suggestion beside
    no drop, blank, with no why, or saying again a row as saved is a refusal line; the floor counts only the drops with
    no row in their place, the last rows giving way first (the note alone). A `label` beside a note (a rewrite) is
    applied as the row changed (`typed`, `why`). `first_fixed`: the first row is never changed or put aside
    (Importance's own row, the lead benefit). Code's word rules are keel-cloud's, never mirrored here."""
    labels = list(rows or [])
    notes: dict[int, str] = {}
    drops: list[int] = []
    rewrites: dict[int, str] = {}
    offered: dict[int, dict] = {}
    for r in readings or []:
        at = r["at"]
        if r.get("note") and at not in notes:
            notes[at] = r["note"]
        if r.get("suggest") and at not in offered:
            offered[at] = r["suggest"]
        if (first_fixed and at < 1) or at in drops or at in rewrites or not notes.get(at):
            continue
        label = (r.get("label") or "").strip() or None
        if label and label.lower() != labels[at].strip().lower():
            rewrites[at] = label
        elif label is None and r.get("drop"):
            drops.append(at)
    drops.sort()
    refused: list[str] = []
    in_place: dict[int, dict] = {}
    for at in sorted(offered):
        suggest = offered[at]
        text = " ".join(str(suggest.get("label") or "").split()) or None
        if at not in drops:
            fault = "beside no row put aside"
        elif text is None:
            fault = "blank"
        elif not suggest.get("why"):
            fault = "no why: a row in another's place says why"
        else:
            same = next((row for row in labels if _same_words(row, text)), None)
            fault = f"L14: '{text}' means what '{same.strip()}' means" if same is not None else None
        if fault:
            refused.append(f"suggest '{text or suggest.get('label')}' in place of '{labels[at]}': {fault}")
        else:
            in_place[at] = {"label": text, "why": suggest.get("why")}
    bare = [d for d in drops if d not in in_place]
    while bare and len(labels) - len(bare) < floor:
        last = bare.pop()
        drops.remove(last)
        refused.append(f"'{labels[last]}' put aside: the list keeps at least {floor} {'row' if floor == 1 else 'rows'}")
    items, aside, kept = [], [], []
    for i, label in enumerate(labels):
        if i in drops:
            aside.append({"typed": label, "why": notes.get(i)})
            if i in in_place:
                items.append({"label": in_place[i]["label"], "suggested": True, "suggestedWhy": in_place[i]["why"],
                              "inPlaceOf": label})
                aside[-1]["replacedBy"] = in_place[i]["label"]
        elif i in rewrites:
            items.append({"label": rewrites[i], "typed": label, "why": notes.get(i)})
        else:
            items.append({"label": label})
            if notes.get(i):
                kept.append({"row": label, "note": notes[i]})
    return {"items": items, "putAside": aside, "notes": kept, "refused": refused}


_BAND_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
_BAND_N = r"(one|two|three|four|five|\d+)"
#: keel-cloud 243 FR-4 (`ReviewedRows.changed`): the band's counts as served -- rows (answers, conditions) changed,
#: put aside (rows, benefits, conditions), and suggested in place (*... and suggested three in their place*, *...,
#: and suggested one in its place.*). Read off the served line, never built.
BAND_CHANGED = re.compile(rf"\bchanged {_BAND_N} (?:rows?|answers?|conditions?)\b")
BAND_PUT_ASIDE = re.compile(rf"\bput {_BAND_N}(?: (?:rows?|benefits?|conditions?))? aside\b")
BAND_IN_PLACE = re.compile(rf"\bsuggested {_BAND_N} in (?:its|their) place\b")


def _band_count(m) -> int:
    if m is None:
        return 0
    said = m.group(1)
    return _BAND_COUNT_WORDS.get(said, int(said) if said.isdigit() else 0)


def band_counts(line: str | None) -> dict:
    """Spec 149 FR-2 (keel-cloud 243 FR-4): what a served band's line counts -- `{changed, put_aside, in_place}` -- off
    its words (`BAND_CHANGED`, `BAND_PUT_ASIDE`, `BAND_IN_PLACE`); zeros on a line with none (or none served)."""
    text = str(line or "")
    return {"changed": _band_count(BAND_CHANGED.search(text)), "put_aside": _band_count(BAND_PUT_ASIDE.search(text)),
            "in_place": _band_count(BAND_IN_PLACE.search(text))}


def _band_word(n: int) -> str:
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))


def band_line(dimension: str, saved) -> str | None:
    """keel-cloud 243 FR-4 (`ReviewedRows.changed`, the line alone): the band's line code serves over a list the review
    changed -- Importance's and every other row list's, Relative advantage's (the moment not mirrored: read as served,
    147), Compatibility's, Current solution's count (235's scale line read as served) -- counting the rows changed, put
    aside and suggested in their place. None where nothing was changed or put aside."""
    items, aside = served_items(saved), put_aside_of(saved)
    changed = sum(1 for i in items if i.get("typed"))
    put = len(aside)
    suggested = sum(1 for i in items if in_place_of(i))
    if not changed and not put:
        return None
    place = f"in {'its' if suggested == 1 else 'their'} place"
    in_place = f" and suggested {_band_word(suggested)} {place}" if suggested else ""
    rows = "row" if put == 1 else "rows"
    moment = "at the moment your problem names."
    if dimension == "problem.current_solution_satisfaction":
        sits = "answer so it sits" if changed == 1 else "answers so they sit"
        return f"Keel changed {_band_word(changed)} {sits} on one scale."
    if dimension == "solution.relative_advantage":
        return (f"Keel put {_band_word(put)} {'benefit' if put == 1 else 'benefits'} aside{in_place}"
                f"{',' if suggested else ''} so what is left is what only your idea would have given them.")
    if dimension == "solution.compatibility":
        changes = (f"changed {_band_word(changed)} {'condition' if changed == 1 else 'conditions'} so strangers are asked "
                   "what they can do themselves")
        asides = f"put {_band_word(put)} " + ("condition aside because your segment already has it" if put == 1
                                         else "conditions aside because your segment already has them")
        suggests = f"suggested {_band_word(suggested)} {place}"
        if put == 0:
            return f"Keel {changes}."
        if changed == 0:
            return f"Keel {asides}" + (f", and {suggests}." if suggested else ".")
        return f"Keel {changes}, {asides}, and {suggests}." if suggested else f"Keel {changes}, and {asides}."
    if put == 0:
        return f"Keel changed {_band_word(changed)} {'row so it sits' if changed == 1 else 'rows so they sit'} {moment}"
    if suggested:
        head = f"changed {_band_word(changed)} {'row' if changed == 1 else 'rows'}, " if changed else ""
        rest = "every row sits" if suggested == put else "the rest sit"
        return f"Keel {head}put {_band_word(put)}{'' if changed else ' ' + rows} aside{in_place}, so {rest} {moment}"
    if not changed:
        return f"Keel put {_band_word(put)} {rows} aside so the rest sit {moment}"
    did = f"changed {_band_word(changed)} {'row' if changed == 1 else 'rows'}"
    return f"Keel {did} and put {_band_word(put)} aside so the rest sit {moment}"


#: Spec 149 FR-4: the small words a reason is read without when it is held to its row (`reason_row`).
_REASON_STOPS = frozenset("""a an the to of on in at by for with from into and or but so that this these those it its
    they them their there is are was were be been being has have had not no any all every one first row rows""".split())


def _reason_words(text: str | None) -> set[str]:
    words = re.findall(r"[a-z0-9]+", str(text or "").lower())
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words if w not in _REASON_STOPS and len(w) > 2}


def reason_row(why: str | None, rows: list[str]) -> int | None:
    """Spec 149 FR-4: the row (index into `rows`) a reason is most about -- the one sharing the most of its content
    words, with at least two shared and no other row as near; None where none stands out. A reason the review wrote
    for one row and code set under another (the staging misread) names the other row's words, not its own."""
    said = _reason_words(why)
    shared = [len(said & _reason_words(row)) for row in rows]
    if not shared:
        return None
    most = max(shared)
    return shared.index(most) if most >= 2 and shared.count(most) == 1 else None


def in_place_faults(handed: list[str], saved, *, first_fixed: bool = True,
                    notes: list[tuple[str, str]] | None = None) -> list[dict]:
    """Spec 149 FR-4 (keel-cloud 243, the staging shape of 2026-11-09): what a list the review changed must hold, read
    against the rows the founder saved (`handed`, in order, the own row first where `first_fixed`) -- each a fault
    `{what, ...}`, `[]` where it holds:

    - the right rows are struck: every row put aside is a row the founder saved, never the own row;
    - each reason on its own row: every row put aside carries a reason, no two the same, and none is more about another
      saved row than its own (`reason_row`);
    - a Keel row in each place: every row put aside with a row in its place (`replacedBy`, read off the rows) has Keel's
      row standing where it stood (`inPlaceOf` its words), and every Keel row in place stands for a row put aside;
    - nothing the founder saved is lost (`founder_words`);
    - the band counts both (`band_counts` against the list: put aside, suggested in place);
    - and a note kept under a row (`notes`, `(row, note)` as the Check draws them) is about that row, never another."""
    handed = [h for h in handed or [] if h]
    items, aside = served_items(saved), put_aside_of(saved)
    faults: list[dict] = []

    def at_of(words) -> int | None:
        return next((i for i, h in enumerate(handed) if _same_words(h, words)), None)

    whys = []
    for row in aside:
        at = at_of(row.get("typed"))
        if at is None:
            faults.append({"what": "a row put aside the founder never saved", "typed": row.get("typed")})
            continue
        if first_fixed and at == 0:
            faults.append({"what": "the own row put aside", "typed": row.get("typed")})
        why = " ".join(str(row.get("why") or "").split())
        if not why:
            faults.append({"what": "a row put aside with no reason", "typed": row.get("typed")})
        else:
            if any(_same_words(why, w) for w in whys):
                faults.append({"what": "two rows put aside with one reason", "typed": row.get("typed"), "why": why})
            whys.append(why)
            about = reason_row(why, handed)
            if about is not None and about != at:
                faults.append({"what": "a reason on the wrong row", "typed": row.get("typed"), "why": why,
                               "about": handed[about]})
    standing_aside = {i for i, h in enumerate(handed)
                      if any(_same_words(h, r.get("typed")) for r in aside)}
    in_place = {i: item for i, item in enumerate(items) if in_place_of(item)}
    for row in aside:
        by = replaced_by(row, saved)
        at = at_of(row.get("typed"))
        if not by or at is None:
            continue
        # where the struck row stood: its index, less the rows above it put aside with nothing in their place
        bare_above = sum(1 for i in standing_aside if i < at
                         and not replaced_by(next(r for r in aside if _same_words(handed[i], r.get("typed"))), saved))
        want = at - bare_above
        found = next((i for i, item in in_place.items() if _same_words(in_place_of(item), row.get("typed"))), None)
        if found is None:
            faults.append({"what": "no Keel row stands in place of a row put aside", "typed": row.get("typed"),
                           "replacedBy": by})
        elif found != want:
            faults.append({"what": "Keel's row does not stand where the row put aside stood", "typed": row.get("typed"),
                           "label": items[found].get("label"), "at": found, "want": want})
    for i, item in in_place.items():
        if not any(_same_words(in_place_of(item), r.get("typed")) for r in aside):
            faults.append({"what": "a Keel row in place of a row not put aside", "label": item.get("label"),
                           "inPlaceOf": in_place_of(item)})
    for row, said in notes or []:
        about = reason_row(said, handed)
        at = at_of(row)
        if about is not None and at is not None and about != at:
            faults.append({"what": "a note on the wrong row", "row": row, "note": said, "about": handed[about]})
    lost = [h for h in handed if not row_present(h, saved)]
    if lost:
        faults.append({"what": "a row the founder saved is lost", "rows": lost})
    band = review_band(saved)
    if band:
        counted = band_counts(band.get("line"))
        have = {"put_aside": len(aside), "in_place": len(in_place)}
        if (counted["put_aside"], counted["in_place"]) != (have["put_aside"], have["in_place"]):
            faults.append({"what": "the band does not count the list", "line": band.get("line"), "counted": counted,
                           "list": have})
    return faults


def rungs_plan(entry, drawn: list[str], max_items: int, typed: dict[str, str] | None = None) -> dict:
    """Spec 067 FR-2 (keel-cloud 128 FR-16; Pairio typed two of five): what the founder does to Keel's draft on the
    Check screen so that every one of the entry's Current-solution rungs is served, in the entry's order. The rungs are
    positional (code's positional codes, `single_choice_5`), so the founder's rung i goes in row i: a drawn row that
    does not carry it word for word is **edited** over (`edit`: (row index, label) -- Karsa, 2026-10-23: Keel redrafted
    three of five and the walk stopped for want of room), a rung past the drawn rows is typed into a new row (`add`)
    while the screen's `max_items` has room, and a rung past that stops the walk by name (`cannot`). Counted from the top
    (keel-cloud 203): where the entry carries Keel's working rung first (`keels_working_first`), row 0 is it and the
    founder's own rungs follow from row 1, as keel-cloud draws them.

    Spec 143 FR-2 (keel-cloud 232 FR-1): a drawn row the review changed carries the founder's rung as its `typed`
    (`typed`: `{served label: typed}`, `typed_by_label`) -- the rung is present, never typed over (no Put back)."""
    labels = [i["label"] for i in founder_list(entry, "problem.current_solution_satisfaction")["items"]]
    typed = typed or {}
    plan = {"edit": [], "add": [], "cannot": []}
    for i, label in enumerate(labels):
        if i < len(drawn):
            if not _same_words(label, drawn[i]) and not _same_words(label, typed.get(drawn[i])):
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
    # spec 132 FR-2 (keel-cloud 205 FR-1): a Purchase friction row naming the founder's own offer is left off the list
    # the cloud stores (`L32`), and a pick of it moves to the first row kept; FR-3 / FR-10 (keel-web 168): Buyer and
    # payer's pick is the walker's -- 1, every role named, wherever the Answer names one; 0, *Nobody else*, else
    for i, (_, item) in enumerate(kept_items(entry, key)):
        out = {"code": wire_code(key, i), "label": item["label"]}
        if key in ASKED_FACES and item.get("asked"):
            # spec 154 FR-0: the stored face is the asked job's -- Adoption friction's cut to the frame where the corpus's
            # does not fit (`adoption_face`)
            out["asked"] = adoption_face(item) if key == ADOPTION_KEY else item["asked"]
        items.append(out)
    if key == COMMITMENT_KEY and keels_smaller_step(entry):
        # spec 133 FR-2 (keel-cloud 211 FR-6): the founder saves Keel's free smaller step beside the step, as drawn
        items.append({"code": wire_code(key, len(items)), "label": keels_smaller_step(entry)["label"]})
    picked = kept_picked(entry, key)
    out = {"items": items, "pickedIndex": int(picked) if key in PICKED and picked is not None else None,
           "phrase": bare_phrase(saved.get("phrase")) if key == "problem.current_solution_satisfaction" else None}
    if key == PURCHASE_FRICTION_KEY and founder_duration(entry):
        # spec 118 FR-2 (keel-cloud 182 FR-1): the founder's time beside the step, `SavedList.duration`
        out["duration"] = founder_duration(entry)
    return out


def founder_duration(entry) -> dict | None:
    """Spec 118 FR-2 (keel-cloud 182 FR-1, revision 20): the founder's expected time beside Purchase friction's picked
    step, `{count, unit}` as the wire takes it -- the entry's own (08-fresco 2 WEEKS, 10-palus 4 WEEKS, 17-expanse 6
    WEEKS); None where the entry names none (the list is saved with no time and served the fixed three)."""
    found = entry.duration() if hasattr(entry, "duration") else None
    return found.as_wire() if found else None


_NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
                 "twelve")


def time_sourced(entry) -> bool:
    """Spec 130 (keel-cloud 199 FR-4, *Not foreseen*: *the about 2 weeks cycle 7's readers saw came from the back-test
    entries' recorded `duration` ..., author's choices the sources do not give*): whether the entry's own sources say the
    founder's time -- a line of its `{id}.sources.md` beside the yaml names the count and the unit (*2 weeks*, *two
    weeks*, *2-week*) beside Purchase friction (the row's name, its key, or *the founder's time*); a figure the sources
    give for something else (21-codyco's bookings *in 4 weeks*) is not the founder's time. A golden entry (no sources
    file) names no time and is never asked one. Spec 135: a `## Revision ...` section is the corpus's own trace of the
    rows a revision moved (keel-cloud 215's *the founder's 2 weeks kept* on 08-fresco), never a source -- the read stops
    at its heading."""
    found = entry.duration() if hasattr(entry, "duration") else None
    path = getattr(entry, "path", None)
    if found is None or path is None:
        return found is not None
    from pathlib import Path                                            # noqa: PLC0415
    sources = Path(path).parent / f"{entry.id}.sources.md"
    if not sources.is_file():
        return True                                                     # nothing to read it against: as recorded
    unit = found.said().split(" ", 1)[1].rstrip("s")
    counts = [str(found.count)] + ([_NUMBER_WORDS[found.count]] if found.count < len(_NUMBER_WORDS) else [])
    for line in sources.read_text(encoding="utf-8").lower().splitlines():
        if line.startswith("## revision"):
            break
        if not any(w in line for w in ("purchase friction", "purchase_friction", "founder's time")):
            continue
        if any(re.search(rf"\b{re.escape(c)}[ -]{re.escape(unit)}s?\b", line) for c in counts):
            return True
    return False


#: Spec 137 FR-4: the words of an entry's sources that make its plan after the one-off optional -- a free plan named
#: beside the paid one (13-aircaps: *free plan with unlimited captions; "Pro plan: $20/month"*), or the word itself.
_FREE_PLAN = re.compile(r"(?i)\bfree plan\b")
_PAID_PLAN = re.compile(r"(?i)\bplan\b[^.;]*?[$\u20ac\u00a3]\s?\d|[$\u20ac\u00a3]\s?\d[^.;]*?\bplan\b")
_OPTIONAL_PLAN = re.compile(r"(?i)\boptional\b[^.;]*\bplan\b")


def plan_optional_sourced(entry) -> bool:
    """Spec 137 FR-4 (keel-cloud 213 FR-1c, contract 59: `price.optional`): whether the entry's plan after the one-off
    is optional, read off its own `{id}.sources.md` -- a line that names a free plan beside a priced plan, or an optional
    plan -- until a corpus revision records the field (the yaml's `optional`, keel-cloud's; read first where it is
    there). Only an up-front-then price with a plan has one. A `## Revision ...` section is never a source (spec 135)."""
    price = ((getattr(entry, "founder_calibration", None) or {}).get("commercial.price") or {}).get("answer")
    if not isinstance(price, dict) or not chain_mod.two_steps(price):
        return False
    if price.get("optional") is not None:
        return price.get("optional") is True
    path = getattr(entry, "path", None)
    if path is None:
        return False
    from pathlib import Path                                            # noqa: PLC0415
    sources = Path(path).parent / f"{entry.id}.sources.md"
    if not sources.is_file():
        return False
    for line in sources.read_text(encoding="utf-8").splitlines():
        if line.lower().startswith("## revision"):
            break
        if _OPTIONAL_PLAN.search(line) or (_FREE_PLAN.search(line) and _PAID_PLAN.search(_FREE_PLAN.sub("", line))):
            return True
    return False


def founder_price(entry) -> dict | None:
    """Spec 137 FR-4: the price the founder types, as the corpus states it -- the plan's low and high as recorded
    (21-codyco's *€1,000 to €1,500*: 1000 and 1500) -- and `optional: True` where the plan is optional
    (`plan_optional_sourced`: 13-aircaps' *optional $20 a month plan*). None where the entry states no chain price."""
    price = ((getattr(entry, "founder_calibration", None) or {}).get("commercial.price") or {}).get("answer")
    if not chain_mod.price_in_chain(price):
        return None
    out = dict(price)
    if plan_optional_sourced(entry):
        out["optional"] = True
    return out


#: keel-cloud 220 FR-1 (`CostEstimate.priceQuestion`): the founder's Price question.
PRICE_QUESTION = "What price do you have in mind for {subject}?"
PRICE_QUESTION_NO_SUBJECT = "a fix for this"


def price_question(idea_name: str | None, offer_name: str | None) -> str:
    """Spec 141 FR-3 (keel-cloud 220 FR-1, `CostEstimate.priceQuestion` / `priceSubject`): *What price do you have in
    mind for {Name}?* -- the idea by its name where the study holds one, else the offer as the seed puts it, else *a fix
    for this*."""
    subject = next((str(x).strip() for x in (idea_name, offer_name) if x is not None and str(x).strip()), None)
    return PRICE_QUESTION.format(subject=subject or PRICE_QUESTION_NO_SUBJECT)


def price_belief_owed(entry) -> str | None:
    """Spec 137 FR-2 / FR-4 (keel-cloud 213 FR-1): the price belief the engine writes over what the walk types
    (`founder_price`) -- the plan's range whole, *then an optional {plan} plan* where it is optional, no unit where the
    user pays, no *per {unit}* beside a share of a named base. None where the entry states no chain price."""
    price = founder_price(entry)
    if price is None:
        return None
    cost = entry.cost() if callable(getattr(entry, "cost", None)) else None
    ctx = getattr(entry, "context", None) or {}
    persona = getattr(entry, "persona", None) or {}
    maker = persona.get("decision_maker") if isinstance(persona.get("decision_maker"), dict) else None
    b2b = maker is not None
    decider = (maker or {}).get("role")
    deciders = chain_mod.deciders((maker or {}).get("title") or decider, ctx.get("actor_plural"), b2b)
    said_occasion = ctx.get("occasion") if isinstance(ctx.get("occasion"), str) else ""
    # the loader's own inputs (`corpus._check_chain`): the decider's role, else the actor, is the role word
    return chain_mod.price_belief(price, cost, ctx.get("actor_plural"), said_occasion, decider or ctx.get("actor"),
                                  decider, deciders, getattr(entry, "idea_name", None), b2b)


#: Spec 130: the walker's own time for a golden entry that names none, typed only where the page draws no *not sure*.
GOLDEN_DEFAULT_DURATION = {"count": 2, "unit": "WEEKS"}


def walker_duration(entry) -> dict | None:
    """Spec 130 (keel-cloud 199 FR-4: the time is the founder's alone, asked, *not sure* an answer): what the walker
    answers on Purchase friction's time box. Spec 132 FR-8 (keel-cloud 206 *Owed elsewhere*: in cycle 9 the walker left
    the box empty on Palus, Expanse and Codyco, so the cloud saved the list with no time and served the fixed three): the
    walker types the entry's own time, the step's own (`founder_duration`: 10-palus 4 weeks, 17-expanse 6 weeks), and
    never leaves the box empty -- spec 130's `time_sourced` read no longer turns a recorded time into *not sure*; where
    the corpus records none, *I'm not sure* (`{unsure: True}`, the walker's own default beside it for a page that draws
    no such control)."""
    duration = founder_duration(entry)
    if duration is None:
        # a golden entry names no time (S-016 and its sharing journeys S-018..S-020, 2026-11-02 21:44 ET: all three
        # stopped at Purchase friction's Choose by spec 119's name): the walker answers *not sure*; where the page
        # draws no such control yet (keel-web owes it) the walker's OWN default is typed and the gap recorded
        return {"unsure": True, "default": True, **GOLDEN_DEFAULT_DURATION}
    return duration


def served_friction_picks(entry, person: "PersonInputs", items: dict) -> tuple["PersonInputs", list[str]]:
    """Spec 130 (keel-cloud 199 FR-4): where the founder answered the time *not sure*, Purchase friction is served the
    fixed three (`yes_long · yes_quick · not_needed`) and a person's recorded duration band is answered by revision 20's
    one rule turned back -- a band within the recorded time *quick*, a band from it *a long time*, *not needed* and a
    chip as they were; each re-expression named. With the bands served, or nothing served, the person is unchanged."""
    import dataclasses                                                 # noqa: PLC0415
    from instructions import friction as friction_mod                  # noqa: PLC0415
    served = items.get(PURCHASE_FRICTION_KEY) or {}
    offered = [str(o.get("optionId") or o.get("code") or "") for o in served.get("options") or []]
    if not offered or set(offered) - set(friction_mod.UNDATED_CODES):
        return person, []
    founder = entry.duration() if hasattr(entry, "duration") else None
    picks, notes = [], []
    for pick in person.picks:
        if pick.dimension == PURCHASE_FRICTION_KEY and pick.codes and pick.codes[0] not in offered:
            was = pick.codes[0]
            code = friction_mod.NOT_NEEDED if was == friction_mod.NOT_NEEDED else (
                "yes_quick" if friction_mod.within(was, founder) else friction_mod.LONG)
            notes.append(f"{person.person}: Purchase friction is served the fixed three (the founder's time not sure), "
                         f"so the recorded band '{was}' is answered '{code}'")
            pick = dataclasses.replace(pick, codes=[code])
        picks.append(pick)
    return (dataclasses.replace(person, picks=picks), notes) if notes else (person, [])


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
    """Spec 067 FR-1 (keel-cloud 128 FR-17, FR-20): at load, no list label is over the Answer box's 25 words -- else the
    run stops here, naming the label, never after a paid walk. Since spec 135 the rows past the box are typed on the
    Check screen on both lists (Importance's others, `importance_typed`; Current solution's rungs, FR-2), never a stop. Spec 131
    (keel-cloud 203): and Current solution's first rung reads as today's way working -- a list whose first rung is a
    shortfall is refused at Save, so an entry whose Answer types only shortfalls carries the working rung on top
    (`keels_working_first`)."""
    current = entry.founder_list("problem.current_solution_satisfaction") if hasattr(entry, "founder_list") else None
    if (current or {}).get("items") and not entry.unsure("problem.current_solution_satisfaction"):
        keels_working_first(entry)
        first = current["items"][0]["label"]
        if not working_rung_mod.works(first):
            raise VectorsScriptError(
                f"{entry.id}: problem.current_solution_satisfaction's first rung {first!r} is a shortfall "
                f"({working_rung_mod.shortfall(first)!r}): the scale opens on today's way getting the job done, and the "
                "Save refuses a first rung that falls short -- where the Answer types only shortfalls, put the working "
                "rung on top, marked `keel: true` (keel-cloud 203 FR-1, FR-2)")
    for key in (k for k in LIST_CONTROLS if (entry.founder_list(k) or {}).get("items")):
        for item in entry.founder_list(key)["items"]:
            if _words(item.get("label")) > ANSWER_MAX_WORDS:
                raise VectorsScriptError(f"{entry.id}: {key}'s item {item['label']!r} is {_words(item['label'])} words; "
                                         f"the Answer box takes {ANSWER_MAX_WORDS} (spec 067 FR-1)")
    # spec 135 (the coordinator's decision, 2026-11-04): Importance's others past the Answer's 25 words are no stop --
    # the Answer names those that fit and the founder types the rest on the Check screen (`importance_typed`), as
    # Current solution's rungs (spec 067 FR-2); only a single row longer than the box stops here (above)


def _answer_labels(entry, key: str) -> list[str]:
    """The labels the founder's Answer on `key` names, in order, before the box's cap."""
    saved = founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != NOBODY_ELSE[0]]
    if key == "problem.importance":
        labels = importance_named(entry)
    if key == "problem.current_solution_satisfaction" and saved.get("phrase"):
        labels = [saved["phrase"]] + labels
    return labels


def current_solution_boxes(entry) -> tuple[str, str]:
    """Spec 118 (keel-cloud 184 FR-8b (a), keel-web 150's two boxes): Current solution's Answer as the founder types it
    -- the first box *what they do*, their own words for today's way (the list's phrase as a sentence of its own, *Getting
    the day into the log.*), the second box *how it goes*, its own sentence (the outcomes the founder names, as many
    whole ones as fit that box's own 25 words -- spec 135: never counted with the first box -- *Caught by an alert
    within minutes; Caught by our evals the same day; ...*), the rest typed on the Check screen (spec 067 FR-2).
    Never the phrase and the labels run together by *"; "* -- with no full stop keel-web's split put all of it in the
    first box and left the second empty (cycle 4's run-together Answer). Spec 119 FR-6: on revision 22 the first box is
    the entry's `current_solution.today` where it records one."""
    key = "problem.current_solution_satisfaction"
    saved = founder_list(entry, key)
    phrase = bare_phrase(saved.get("phrase")) or ""
    what = _stopped(phrase) if phrase else ""
    # spec 119 FR-6 (keel-cloud 187 FR-4 (b), revision 22): where the entry records what they do today in the founder's
    # own words (`current_solution.today`, the 14 entries 08-21), that sentence is the first box -- never the list's
    # phrase. Spec 135 (the coordinator's decision, 2026-11-04): each box takes its own 25 words (keel-web 150 caps each
    # box; keel-cloud's `VectorCorridorService` reads the two apart, `first > ANSWER_MAX_WORDS || second > ...`), so the
    # rungs fill the second box up to its own 25 -- the two are never counted together
    today = entry.today() if hasattr(entry, "today") else None
    if today:
        what = _stopped(today)
    # the outcomes the Answer names are the ones it always named (the phrase and the labels within the box's 25 words,
    # so keel-cloud 117's `founder_rungs` -- the leading rungs typed, kept verbatim -- is unchanged), now in their own box
    # spec 131 (keel-cloud 203 FR-1): Keel's working rung, where it stands first, is never typed by the founder
    labels = [i["label"] for i in saved["items"]][1 if keels_working_first(entry) else 0:]
    named: list[str] = []
    for label in labels:
        if _words("; ".join(named + [label])) > ANSWER_MAX_WORDS:
            break
        named.append(label)
    how = "; ".join(named)
    return what, _stopped(how) if how else ""


def _stopped(text: str) -> str:
    """One sentence: its first letter raised, one closing full stop."""
    said = _sentence(text).rstrip(".").strip()
    return f"{said}." if said else ""


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
    if key == "problem.current_solution_satisfaction" and (saved.get("phrase") or entry.today()):
        # spec 118 (keel-cloud 184 FR-8b (a)): the two boxes, each its own sentence (`current_solution_boxes`), as one
        # Answer text the page splits at the first full stop (keel-web 150 `splitAnswer` / `joinAnswer`)
        what, how = current_solution_boxes(entry)
        return f"{what} {how}".strip()
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
#: 2, the Check screen with two others, Save on); every other entry names as many as fit the Answer's 25 words (COMPOSED;
#: spec 135: all of them, but on six gallery entries at corpus revision 24).
IMPORTANCE_NAMED = {"01-countly": 1, "05-paidly": 2}


def importance_others(entry) -> list[str]:
    """The other difficulties of the entry's Importance list, in order (the own item is first and code's)."""
    return [i["label"] for i in founder_list(entry, "problem.importance")["items"][1:]]


def importance_named(entry) -> list[str]:
    """The other difficulties the founder's Importance Answer names -- and so Keel's redraft adds (097 F9: no more).
    Spec 135 (the coordinator's decision, 2026-11-04): the walk does what a founder does with a 25-word box -- the
    Answer names the others that fit its `ANSWER_MAX_WORDS`, whole and in the entry's order, and stops at the first that
    does not (six gallery entries at corpus revision 24); the rest are typed on the Check screen (`importance_typed`).
    `IMPORTANCE_NAMED` (01-countly, 05-paidly) names fewer by design."""
    others = importance_others(entry)
    if entry.id in IMPORTANCE_NAMED:
        return others[:IMPORTANCE_NAMED[entry.id]]
    named: list[str] = []
    for label in others:
        if _words("; ".join(named + [label])) > ANSWER_MAX_WORDS:
            break
        named.append(label)
    return named


def importance_typed(entry) -> list[str]:
    """The other difficulties the founder types on Importance's Check screen, after Keel's redraft (070 F9): the ones
    the Answer did not name -- on 01-countly and 05-paidly by design, elsewhere those past the box's 25 words (spec
    135)."""
    return importance_others(entry)[len(importance_named(entry)):]


#: Spec 141 FR-8 (keel-cloud 229 FR-5, its owed list): the scripted founder-lists writer's `own_row` for the golden
#: seven -- the act these people do or put up with at the moment of `ACT_THAT_HURTS`' clause, held to A1-A4 by test
#: (`writers_rules.own_row_act_fault`); the cloud builder's candidates, word for word. Data beside `ACT_THAT_HURTS`, no
#: rule; an entry without one is served 223's row.
OWN_ROW_ACTS = {
    "01-countly": "Recounting stock by hand after a mismatched delivery",
    "02-compliancelog": "Pulling training completions into a spreadsheet by hand",
    "03-lullaby": "Knowing what the cry means",
    "04-linerly": "Fixing a puncture on the way to work",
    "05-paidly": "Chasing payment on an approved invoice past its terms",
    "06-repeatline": "Typing a refill request in by hand",
    "07-mulchrun": "Getting mulch loaded at the supply yard",
}


def own_row_act_fault(entry, act: str | None) -> str | None:
    """Spec 141 FR-8 (keel-cloud 229, `ScreenResultApplier.withWritersOwnRow`): `writers_rules.own_row_act_fault` on the
    entry's own words -- its `went_wrong` (and hard case where held), the context's job, circumstance, occasion and
    people, the idea's name, every word of the context the founder wrote."""
    import json                                                         # noqa: PLC0415
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    ctx = _ctx(entry)
    names = [n for n in (getattr(entry, "idea_name", None),) if n]
    return writers_mod.own_row_act_fault(act, act_that_hurts(entry)[1], hard_cases(entry).get("hard_case"),
                                         ctx.get("job"), ctx.get("circumstance"), occasion(entry),
                                         [ctx.get("actor"), ctx.get("actor_plural")], names,
                                         json.dumps(ctx, ensure_ascii=False))


def own_row_act(entry) -> str | None:
    """Spec 141 FR-8 (keel-cloud 229 FR-5): the scripted writer's `own_row` -- `OWN_ROW_ACTS`' act where the problem is in
    scope and it holds A1-A4 on the entry's words; None elsewhere (no field written)."""
    act = OWN_ROW_ACTS.get(getattr(entry, "id", None))
    if act is None or "PROBLEM" not in scope_vectors(entry) or own_row_act_fault(entry, act):
        return None
    return act


def code_own_row(entry) -> str | None:
    """Spec 141 FR-8 (keel-cloud 223 FR-1, `ScreenResultApplier.codesOwnRow` over `OwnRow.fromClause`; 229's
    `withWritersOwnRow` first -- the writer's act where it holds, `own_row_act`): the own row served in place of the
    writer's first Importance row on a scripted PROBLEM run -- the study's clause (the scripted
    Prevalence's `went_wrong`, `act_that_hurts`) as a noun phrase: the golden seven's *Recounting stock by hand after a
    mismatched delivery*, *Knowing why the baby cried* ... (223's owed list, word for word). None where the problem is
    not in scope, no row is read from the clause, or another row already says it (the writer's row then stands)."""
    from instructions import writers_rules as writers_mod                # noqa: PLC0415
    if "PROBLEM" not in scope_vectors(entry):
        return None
    # spec 141 FR-8 (keel-cloud 229 FR-1): the writer's act where it holds A1-A4, else 223's noun phrase
    row = own_row_act(entry) or writers_mod.own_row_from_clause(act_that_hurts(entry)[1])
    if row is None:
        return None
    others = [str(o).strip().rstrip(".!").lower() for o in importance_others(entry)]
    return None if row.lower() in others else row


def importance_first_draft(entry) -> dict:
    """keel-cloud 097 (F9, judgement call 10): Keel's first draft of Importance, before the founder's Answer, is the
    own item alone (`L1`: exactly one) -- the others come from the Answer and Keel adds none. Spec 129 (keel-cloud 200):
    with its short name where the scripted writer names the list's rows."""
    label = founder_list(entry, "problem.importance")["items"][0]["label"]
    name = row_short_names(entry, "problem.importance").get(label)
    return {"items": [{"label": label, **({"short_name": name} if name else {})}]}


# ----------------------------------------------------------------- spec 129: keel-cloud 200's hidden short names

def _short_name_ideas(entry) -> tuple[str, ...]:
    """The idea's names a short name never says (`ScreenResultApplier.ideaNames`): the typed name and the title."""
    try:
        typed = _typed_idea_name(entry)
    except (AttributeError, KeyError, TypeError):                       # an entry with no idea read: no name
        typed = None
    return tuple(n for n in (typed, getattr(entry, "title", None)) if n and str(n).strip())


def row_short_names(entry, key: str) -> dict[str, str]:
    """Spec 129 (keel-cloud 200 FR-1): the scripted founder-lists writer's hidden short name of each row of `key` (one of
    `ShortName.ROWS`), by label -- `short_names.compose`, the row cut down in its own words; Adoption friction's efforts
    and Commitment's step said as -ing phrases. **All or nothing where the founder types rows of his own** (Importance's
    typed rows, `importance_typed`): such a row is owed its short name by the `asked` job (`needsShortName`), which the
    script answers for every typed row or for none, so where one typed row cannot be named the list carries none and
    owes nothing (today's wording). A golden walk alone: a back-test entry runs on the model, whose names are its own."""
    if key not in short_names_mod.ROWS or getattr(entry, "backtest", False):
        return {}
    try:
        items = founder_list(entry, key)["items"]
    except VectorsScriptError:
        return {}
    ideas = _short_name_ideas(entry)
    out: dict[str, str] = {}
    for i, item in enumerate(items):
        turn = gerund if (key == ADOPTION_KEY or (key == COMMITMENT_KEY and i == 0)) else None
        name = short_names_mod.compose(item.get("label"), ideas, gerund=turn)
        if name:
            out[item["label"]] = name
    if key == "problem.importance" and any(label not in out for label in importance_typed(entry)):
        return {}
    return out


def list_short_name(entry, key: str) -> str | None:
    """Spec 129 (keel-cloud 200 FR-1, `ShortName.LISTS`): the list's own hidden short name -- Current solution's phrase,
    Relative advantage's job (as the rung says it, `job_gerund`) -- as the scripted writer names it, or None."""
    if key not in short_names_mod.LISTS or getattr(entry, "backtest", False):
        return None
    if key == "problem.current_solution_satisfaction":
        row = bare_phrase((entry.founder_list(key) or {}).get("phrase"))
    else:
        row = job_gerund(_ctx(entry).get("job"))
    return short_names_mod.compose(row, _short_name_ideas(entry)) if row else None


def importance_asked_result(entry) -> dict | None:
    """Spec 129 (keel-cloud 200 FR-1, `AskedRules`): the `ASKED` result for Importance's rows the founder types on the
    Check screen -- a face-less job (`frame` null) writing each handed row's `short_name` alone, by its index in the
    saved list; None where no row is typed or the list carries no short names (nothing is owed)."""
    typed = importance_typed(entry)
    names = row_short_names(entry, "problem.importance")
    if not typed or not names:
        return None
    labels = [item["label"] for item in founder_list(entry, "problem.importance")["items"]]
    return {"items": [{"index": labels.index(label), "short_name": names[label]} for label in typed]}


def tested_short_name(entry, rung: str) -> str | None:
    """Spec 129 (keel-cloud 200 FR-1, `FollowUpComposer.shortName`): the short name a rung's follow-up says -- the
    list's own on Current solution and Relative advantage, the tested row's elsewhere (Importance's own item, the
    condition, the effort, the step) -- or None (today's wording)."""
    if rung in short_names_mod.LISTS:
        return list_short_name(entry, rung)
    if rung not in short_names_mod.ROWS:
        return None
    if rung == "problem.importance":
        label = founder_list(entry, rung)["items"][0]["label"]
    else:
        label = (entry.tested(rung) or {}).get("label")
    return row_short_names(entry, rung).get(label) if label else None


def smaller_short_name(entry) -> str | None:
    """Spec 129 (keel-cloud 200 FR-1): Commitment's smaller step's short name (`{smaller_name}`), or None."""
    saved = entry.founder_list(COMMITMENT_KEY) or {}
    items = saved.get("items") or []
    label = items[1].get("label") if len(items) > 1 else None
    return row_short_names(entry, COMMITMENT_KEY).get(label) if label else None


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
        # spec 136 FR-3 (keel-cloud 212 FR-2): `routine` and `went_wrong` beside the event written from the second
        q["routine"], q["went_wrong"] = act_that_hurts(entry)
        # spec 139 FR-2 (keel-cloud 216 FR-1, E9): the one of them who truly answers No
        q["no_sayer"] = no_sayer(entry)
        q["event"] = event_past(entry)
        # spec 141 FR-2 (keel-cloud 219 FR-2): the two hard cases, optional, where the entry holds them
        q.update(hard_cases(entry))
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
        if key == "problem.importance" and own_row_act(entry):
            # spec 141 FR-8 (keel-cloud 229 FR-5): the writer's act from the clause beside the list, on the first write
            # and on a redraft alike (a redraft's context hands `problem_clause`, the clause it is held against)
            q["own_row"] = own_row_act(entry)
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
            # spec 118 (keel-cloud 180 FR-9, contract 50): `CalibrationAnswer.cost.rate` is gone -- hours stay hours
            body["cost"] = {k: answer[k] for k in sorted(chain_mod.CHAIN_FIELDS_COST - {"rate"})
                            if answer.get(k) is not None}
        elif key == "commercial.existing_sacrifice":
            body["cost"] = {k: answer[k] for k in ("mode", "low", "high", "period") if k in answer}
            if answer.get("rate") is not None:
                body["cost"]["rate"] = answer["rate"]
        elif key == "commercial.price" and chain_mod.price_in_chain(answer):
            # a chain price posts its shape and its numbers, and no period (it is the cost's); spec 137 FR-4: an optional
            # plan where the entry's price says so (`founder_price`)
            price = founder_price(entry) or answer
            body["price"] = {k: price[k] for k in sorted(chain_mod.CHAIN_FIELDS_PRICE) if price.get(k) is not None}
        elif key == "commercial.price":
            body["price"] = {k: answer[k] for k in ("low", "high", "period")}
        elif is_list(key):
            saved = saved_list(entry, key)
            listed: dict = {"items": [{k: v for k, v in item.items() if k != "code"} for item in saved["items"]],
                            "pickedIndex": saved["pickedIndex"]}
            if saved["phrase"]:
                listed["phrase"] = saved["phrase"]
            if saved.get("duration"):
                listed["duration"] = saved["duration"]
            body["list"] = listed
            text = answer_text(entry, key)
        elif isinstance(answer, (str, list)):
            body["codes"] = _chosen_codes(entry, key)
        else:
            raise VectorsScriptError(f"{entry.id}: {key}'s founder answer {answer!r} has no wire shape")
        out.append(CalibrationAnswer(dimension=key, body=body, text=text))
    return out


#: keel-cloud `ItemFrames.adoptionFrame` (spec 112, keel-cloud 171 FR-4b) and `AskedRules` K2: the question a stranger
#: hears is at most 20 words, the face framed (a leading *you'd* on the face is the frame's own, said once).
ADOPTION_FRAME = "To use it, you'd {asked}. Would you do that, or not?"
ASKED_MAX_WORDS = 20


def adoption_face(item: dict) -> str:
    """Spec 154 FR-0 (keel-cloud 245 FR-2 + K2): the stranger's face the asked job writes for one Adoption friction row --
    the corpus's own where it frames within 20 words; else (the job phrases every row now, where code once vouched for the
    corpus face unframed) the row's own step said to the stranger, *you'd {step}*, which the frame fits and K3 takes."""
    face = str(item.get("asked") or "").strip()
    bare = face[len("you'd "):] if face.lower().startswith("you'd ") else face
    if face and len(ADOPTION_FRAME.format(asked=bare).split()) <= ASKED_MAX_WORDS:
        return face
    label = str(item.get("label") or "").strip().rstrip(".")
    return f"you'd {label[:1].lower()}{label[1:]}" if label else face


def asked_result(entry, key: str) -> dict:
    """The `ASKED` result for one saved list (keel-cloud 088 FR-003): each item's stranger's face by its
    index, the corpus's own `asked` (K1: one face per index handed). **Spec 154 FR-0 (keel-cloud 245 FR-2)**: the draft
    carries no face, so the first Save hands the asked job **every row** of the list (after the read-back where the
    switch is on) and the stub answers every index -- a row the corpus records no face for is answered with its label
    read as the stranger's question, never left out."""
    saved = founder_list(entry, key)
    items = [{"index": i, "asked": (adoption_face(item) if key == ADOPTION_KEY else item.get("asked") or item["label"])}
             for i, item in enumerate(saved["items"])]
    if key == ADOPTION_KEY:
        # spec 154 FR-0 (keel-cloud 198 FR-9 K8, strict on the first turn): every Adoption friction row carries its
        # condition -- the entry's own, else the step's (`adoption_condition`); before 245 the draft carried it as `only_if`
        for out in items:
            out["condition"] = adoption_condition(saved["items"][out["index"]])
    # spec 129 (keel-cloud 200 FR-1): each faced row's hidden short name beside its face, where the writer names it
    names = row_short_names(entry, key)
    for out in items:
        name = names.get(saved["items"][out["index"]].get("label"))
        if name:
            out["short_name"] = name
    if key == ADOPTION_KEY:
        # spec 130 (keel-cloud 198 FR-9, screen response contract 25): Adoption friction's own condition is `condition`
        # (155's `only_if` retired) -- the entry's own where it records one, over the step's (spec 154: every row carries
        # one, `adoption_condition` above)
        for out in items:
            raw = saved["items"][out["index"]]
            condition = raw.get("condition") or raw.get("only_if")
            if condition:
                out["condition"] = str(condition).strip()
    return {"items": items}


def importance_probe_asked_results(entry) -> list[dict]:
    """Spec 154 FR-0: the two ASKED jobs the Importance probe's wire saves start (`corpus_scenario._importance_needs_three`,
    keel-cloud 200's `needsShortName` on each PUT): the own item and two others saved over the Check's list hands the own
    row alone (the corpus's own label is not the stored draft's -- keel-cloud 229 writes the own row from the clause as an
    act -- and the two typed rows are kept from the list before); the whole list saved again hands the rows past the
    third (not in the list before, not in the draft). Each row its short name, as `importance_asked_result` names them.
    Empty where the entry has no typed Importance rows (no probe runs)."""
    key = "problem.importance"
    if entry.unsure(key):
        return []
    labels = [i["label"] for i in saved_list(entry, key)["items"]]
    names = row_short_names(entry, key)

    def name(label: str) -> str:
        if names.get(label):
            return names[label]
        words = [w.strip(".,;:!?'\"") for w in label.lower().split()]
        return " ".join(w for w in words if w)[:60] if len(words) <= 5 else " ".join(words[:4])
    out = [{"items": [{"index": 0, "short_name": name(labels[0])}]}]
    if len(labels) > 3:
        out.append({"items": [{"index": i, "short_name": name(labels[i])} for i in range(3, len(labels))]})
    return out


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


def part_three_link(entry) -> str:
    """The link part 3 is routed to: the decision-maker's on B2B, else the primary (`EvidencePlan`)."""
    return LINK_B2B if is_b2b(entry) else LINK_PRIMARY


def part_three_writes(entry) -> bool:
    """Spec 148 FR-3 (keel-cloud 239 FR-1, `EvidencePlan.plan`'s `partThreeWrites`): on a study with no part 1 (money
    alone), part 3 is the writer's job where its Existing sacrifice item wants the `loss_clause` (the served stem would
    carry a neutral verb, `loss_clause_wanted`) and part 3 asks something on its link."""
    if serves_gate(entry) or "COMMERCIAL" not in scope_vectors(entry) or not entry.chain():
        return False
    cost = entry.cost() if callable(getattr(entry, "cost", None)) else None
    return bool(cost) and loss_clause_wanted(is_b2b(entry), entry.occasion(), cost) \
        and bool(plan_keys(entry, 3, part_three_link(entry)))


def respondent_jobs(entry) -> list[tuple[int, str]]:
    """The RESPONDENT_QUESTIONS jobs a lock starts: since keel-cloud 091 (contract 14, design §6) **one**, part 1 on the
    primary link -- the part that carries the gate's clause -- on either persona; parts 2 and 3 (on B2B part 3 the
    decision-maker's link's) are code's, written with the lock. Spec 071 (keel-cloud 133 T010): none where the scope
    serves no gate (money alone has no part 1) -- since keel-cloud 239 FR-1 (spec 148 FR-3) except part 3, on its link,
    where its Existing sacrifice item wants the writer's clause (`part_three_writes`): one job, held and priced as every
    lock's (70 credits)."""
    if serves_gate(entry):
        return [(1, LINK_PRIMARY)]
    return [(3, part_three_link(entry))] if part_three_writes(entry) else []


def respondent_item(entry, key: str) -> dict:
    """keel-cloud 088 FR-002: the item is `{key}` -- every other word is code's. Since keel-cloud 212 (spec 136 FR-3) the
    gate too where the study holds the founder's Prevalence clause (the problem in scope, `gate_counts`: code asks the
    founder's clause, said to them; an `event` written is ignored and noted, E10); only where it holds none (the
    solution studies' uncounted anchor) is the gate `{key, event}`, the writer's clause."""
    if key == "problem.prevalence" and not gate_counts(entry):
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
        # spec 118 FR-4c(e) (keel-cloud 185 FR-4, T018): on a study where someone else decides, the part-1 job writes the
        # decision-maker's clause beside the chip -- the entry's recorded one, where it records one
        decider = decider_screener(entry) if is_b2b(entry) else None
        if decider:
            out["decider_condition"] = decider
    # spec 141 FR-7 (keel-cloud 222 FR-2): beside them, the Existing sacrifice item's `loss_clause` where held -- on part 1;
    # since keel-cloud 239 FR-1 (spec 148 FR-3) on part 3 where the study has no part 1 and part 3 is the writer's job
    if (part == 1 and link == LINK_PRIMARY and serves_gate(entry)) or (part == 3 and part_three_writes(entry)
                                                                      and link == part_three_link(entry)):
        clause = scripted_loss_clause(entry)
        if clause:
            out["loss_clause"] = clause
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


def study_holds_went_wrong(entry) -> bool:
    """Spec 154 FR-0 (keel-cloud 229): whether the study's clause holds a went_wrong, so Importance's draft is handed
    `problem_clause` -- the Prevalence question's clause in a study with the problem's questions (the scripted writer
    writes it), the problem card's in one without."""
    vectors = scope_vectors(entry)
    return bool(problem_clause(entry).get("went_wrong")) or (
        "PROBLEM" in vectors and "problem.prevalence" in calibrated_keys(entry, "PROBLEM")
        and bool(act_that_hurts(entry)[1]))


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
    # spec 154 FR-0 (keel-cloud 229, `ScreenContextBuilder`): Importance's draft is handed `problem_clause` where the
    # study's clause holds a went_wrong -- `VectorCorridor.studyClause()`: the Prevalence question's clause in a study
    # with the problem's questions (the scripted writer writes `went_wrong` on it, `calibration_question`), the problem
    # card's in one without (`problem_clause(entry)`) -- so its entries are filed under the second key set, in order
    with_clause = study_holds_went_wrong(entry)
    # and keel-cloud 228 (FR-3): Current solution's Answer is sent in two boxes, so its draft is handed `answer_parts`
    for vector, only in calibration_jobs(entry):
        screen = calibration_screen_of(entry, only, with_clause=with_clause)
        result = _completed(calibration_result(entry, vector, only))
        screens.setdefault(screen, []).append(result)
        # the redraft of a refused draft answers with the same result (the corpus's), once more
        screens.setdefault(screen + REPAIR_SUFFIX, []).append(result)
    asked = [_completed(asked_result(entry, key)) for key in ("solution.compatibility", "solution.adoption_friction")
             if not entry.unsure(key)] if "SOLUTION" in vectors else []
    # spec 129 (keel-cloud 200 FR-1): the founder's typed Importance rows are owed their short names by an ASKED job at
    # the problem stage's Save -- the first ASKED job a walk runs, so its entry is first
    importance = importance_asked_result(entry) if "PROBLEM" in vectors and not entry.unsure("problem.importance") \
        else None
    if "PROBLEM" in vectors and not entry.unsure("problem.importance"):
        # spec 154 FR-0: the Importance probe's wire saves each start an ASKED job (short names), after the problem
        # stage's own (where the founder typed rows) and before the solution lists'
        asked = ([_completed(importance)] if importance else []) \
            + [_completed(x) for x in importance_probe_asked_results(entry)] + asked
    if asked:
        screens[ASKED_SCREEN] = asked
        # a refused asked turn's repair (the asked ladder) carries `repair`: answered with the same entries again
        screens[ASKED_SCREEN + REPAIR_SUFFIX] = list(asked)
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
    # spec 154 FR-0 (keel-cloud 229): Importance's draft carries `problem_clause` where the study holds a went_wrong --
    # a second key set for the same screen, matched by name (`generate` files those entries under it)
    out[CALIBRATION_WITH_CLAUSE_SCREEN] = [*out[CALIBRATION_SCREEN], PROBLEM_CLAUSE_KEY]
    out[CALIBRATION_WITH_PARTS_SCREEN] = [*out[CALIBRATION_SCREEN], ANSWER_PARTS_KEY]
    for screen in (*CALIBRATION_SCREENS, ASKED_SCREEN):
        out[screen + REPAIR_SUFFIX] = [*out[screen], REPAIR_KEY]
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
        if self.dimension == "problem.importance" and len(self.codes) == 1:
            # spec 139 FR-4 (keel-cloud 217 judgement call 1, 158 FR-2): a one-code Importance pick is the first pick,
            # then *Nothing else* -- the one id with `chip: NOTHING_ELSE`, as keel-web's second ask sends it
            out["chip"] = NOTHING_ELSE_CHIP
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
        # spec 130 (keel-cloud 198 FR-3): a value box's `rather_not_say` is its one escape since 198, `dont_know`
        if key == "commercial.existing_sacrifice" and entry.chain():
            chip = corpus_reader.spec198_chip(key, chip)
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
    # spec 130 (keel-cloud 198 FR-5): revision 22's Ability to pay `no_budget` is answered `outside_funding` (the one rule)
    if isinstance(raw, list):
        return Pick(dimension=key, codes=[on_the_wire(entry, key, corpus_reader.spec198_pick(key, str(c))) for c in raw])
    return Pick(dimension=key, codes=[on_the_wire(entry, key, corpus_reader.spec198_pick(key, str(raw)))])


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
        # spec 132 FR-3 / FR-10: the tested item is the walker's pick -- every role named (1) wherever the Answer names
        # one, *Nobody else* (0) only where it names nobody (Palus's corpus picks *Nobody else* beside the board)
        supports = (fake.BUYER_ALONE,) if buyer_payer_pick(entry) == 0 else fake.BUYER_SUPPORTS
    # keel-cloud 128 FR-21: an up-front-then price is held on both steps -- the up front's own low as well
    upfront = float(price["upfrontLow"]) if chain and chain_mod.two_steps(price) and price.get("upfrontLow") is not None \
        else None
    # spec 118 FR-2 (keel-cloud 182): Purchase friction's rung reads the founder's time; (183 T004) Compatibility's
    # second stem only where *Yes, with some steps* says its steps -- a permission's or a fact's, never an ability's
    duration = entry.duration() if hasattr(entry, "duration") else None
    tested = entry.tested("solution.compatibility") or {}
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    # spec 141 FR-8 (keel-cloud 225, `ItemFrames.kindOf`): a written kind first, else the word test
    steps = spoken_mod.kind_of(tested.get("kind"), tested.get("asked"), tested.get("label")) != "ABILITY" if tested \
        else True
    return fake.Founder(importance_item=wire_code("problem.importance", 0) if importance and importance["items"]
                        else None, price_low=low, buyer_supports=supports, chain_price=chain, current_line=line,
                        upfront_low=upfront, friction_days=duration.days() if duration else None,
                        compatibility_steps=steps)


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
        # spec 132 FR-15 (keel-cloud 208 FR-2, `pickSaid`): the person's own picks said back, each by its short form --
        # its row's short name, else the row cut -- the first, then the second where there were two
        said = [pick_said(entry, rung, label(c)) for c in codes if c != fake.NOTHING_ELSE_CODE]
        values["{their_pick}"] = said[0] if said else None
        values["{their_next}"] = said[1] if len(said) > 1 else None
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
        if said and values.get("{short_name}"):
            # keel-cloud 200 FR-3 (spec 129): the fact said back by its short name -- *You said no to getting your
            # phone online. What got in the way?*
            values[WHOLE_TEXT] = short_name_said_back(code, label(code), values["{short_name}"])
        elif said:
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
    if rung == "solution.adoption_friction" and codes:
        # keel-cloud 155 FR-2 (amended), 174 FR-7 (spec 115 FR-3, `FollowUpComposer`): the conditional yes said back as
        # the person's own condition where the option was served one (*Only if ...*), on the second stem it is asked on
        said = label(codes[0]) if codes[0] in fake.ALSO[rung][0] else None
        if said and said.startswith(fake.ONLY_IF):
            values[WHOLE_TEXT] = fake.only_if_said_back(said[len(fake.ONLY_IF):])
    band = fake.duration_said(label(codes[0])) if rung == "commercial.purchase_friction" and codes \
        and str(codes[0]).startswith("days_") else None
    if band is not None:
        # spec 132 FR-15 (keel-cloud 208 FR-1, FR-2): the duration band picked said back first, as a person says it --
        # *You said 1 to 3 months.* -- never *to under*, then the registry's one question; a list saved before 182 (its
        # fixed three) as before
        values[WHOLE_TEXT] = f"You said {band}. " + fake.fill(rung, values)
    elif rung == "commercial.purchase_friction":
        # keel-cloud 128 FR-12: asked about this purchase, followed up in its tense -- on the long purchase's second
        # stem too (`FollowUpComposer.values` runs for either stem; S-006 and S-007 on the 129 build: *What would take the
        # time?*, said as it reads)
        stem = str(item.get("question") or item.get("text") or "")
        if stem.startswith("If ") and " bought " in stem and codes:   # "If you bought …", "If your terminal bought …"
            # keel-cloud 154 FR-2: the purchase named, never *it*
            values[WHOLE_TEXT] = f"What would take the time in buying {fake.named(name)}?" if codes[0] == "yes_long" \
                else f"What would slow down buying {fake.named(name)}, if anything?"
    whole = values.pop(WHOLE_TEXT, None)
    # keel-cloud 154 FR-1: the spoken line is filled too -- the project's words, as the clip says them (since keel-cloud
    # 200 the named one where the row carries its short name)
    filled = fake.spoken_filled(rung, values, also=also)
    # keel-cloud 200 FR-3 (spec 129): where the row the stem refers back to carries its hidden short name, the named
    # wording -- on Importance by the count of the stranger's picks; today's wording otherwise (the fallback)
    named = fake.named_of(rung, values, also=also)
    if whole is not None:
        text = whole
    elif named:
        picks = fake.picks_counted(rung, codes)
        text = fake.fill_wording(fake.named_text(named, picks), values)
        if picks > 1 and fake.over_cap(text):
            # spec 132 FR-15 (keel-cloud 208 FR-2): two picks past the spoken cap say the first alone, *that* agreeing
            text = fake.fill_wording(fake.named_text(named, 1), values)
    else:
        text = fake.fill(rung, values, also=also)
    # keel-cloud 129 FR-3: Current solution's and Relative advantage's text is their spoken line (the filled text pasted
    # the pick or the benefit labels); a text composed whole keeps its words
    if whole is None and not also and rung in SAID_AS_SPOKEN and not named:
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
    # spec 132 FR-15 (keel-cloud 208 FR-1): a whole text's spoken line says a percent in words (*about a tenth to a
    # quarter of a percent a year*); the screen keeps its figures
    spoken = fake.percent_said(text) if whole is not None or would_not_pay or said_back else filled
    return {"dimension": rung, "text": text, "spoken": spoken, "also": also}


def pick_said(entry, rung: str, label: str | None) -> str | None:
    """keel-cloud 208 (`FollowUpComposer.pickSaid`): one of the person's Importance picks by its short form -- the row's
    hidden short name where the scripted writer named it (a golden walk), else the row cut (`said_short`)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    name = row_short_names(entry, rung).get(label) if label else None
    return name or fake.said_short(label)


def short_name_said_back(code: str | None, pick: str | None, name: str) -> str:
    """keel-cloud 200 FR-3 (`FollowUpComposer.values`, Compatibility's fact): the fact said back by its short name --
    *You said no to {name}.*, *You said only partly to {name}.* (Partly, or no label), *You said {pick} to {name}.* --
    then *What got in the way?*."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    if code != "only_with_help":
        lead = "You said no to "
    elif pick in (None, "Partly"):
        lead = "You said only partly to "
    else:
        lead = f"You said {fake.lower(pick)} to "
    return f"{lead}{name}. What got in the way?"


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
        values["{smaller_name}"] = smaller_short_name(entry)
    # spec 129 (keel-cloud 200 FR-3): the hidden short name of the row the rung refers back to, where the script wrote
    # one (a golden walk); None reads today's wording
    values["{short_name}"] = tested_short_name(entry, rung)
    # spec 132 FR-15 (keel-cloud 208 FR-2, `FollowUpComposer.lockValues`): never the whole row -- where the row has no
    # short name, the row cut (`said_short`): Importance's own item as the stranger saw it, Current solution's phrase as
    # asked; so the named wordings are said wherever the founder has an own item
    if values["{short_name}"] is None and rung == "problem.importance":
        values["{short_name}"] = fake.said_short(own)
    elif values["{short_name}"] is None and rung == "problem.current_solution_satisfaction":
        values["{short_name}"] = fake.said_short(values.get("{phrase}"))
    return values


def named_said(entry, interview: dict | None, rung: str, said: str | None, *, also: bool = False) -> bool:
    """Spec 129 (keel-cloud 200 FR-3): whether a served follow-up (`said`, its text or its spoken line) is one of the
    stem's named wordings, whatever short name the model wrote -- a back-test runs on the model, whose hidden names the
    walk never sees, so a named wording there is the product's, never a finding."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    pattern = fake.named_pattern(rung, lock_values(entry, interview, rung), also=bool(also))
    return bool(pattern and said and pattern.match(" ".join(str(said).split())))


def follow_up_clip(entry, interview: dict | None, rung: str, *, also: bool = False) -> str:
    """keel-cloud 154 FR-1 (`FollowUpComposer.clip`): one rung's spoken line as the clip recorded at the lock says it --
    the project's words filled -- the same words `GET interview`'s `followUps[].spoken` serves for that rung."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    return fake.spoken_filled(rung, lock_values(entry, interview, rung), also=also)


#: keel-cloud 128 (`FollowUpComposer.WHOLE_TEXT`): the values key a follow-up composed whole for the answer is carried
#: under -- said as it reads.
WHOLE_TEXT = "{whole_text}"


def follow_up_plan(entry, picks: list, link: str, interview: dict, token: str, first=(), *,
                   line: int | None = None, late=(), failing=(), whys=None) -> list[dict]:
    """Spec 075 (keel-cloud 142, keel-web 124): every follow-up the page asks these picks on this link, in the order
    asked -- each `follow_up_question`'s `{dimension, text, spoken, also}` and `on`, the served item's dimension it is
    asked right after, or None for the end's (both under *One more thing* since keel-web 126). At most two (`fake.asks`, the page's
    own walk over the served items' order and the served `followUps[]` rungs); `late` the items whose call the walk
    holds past the beat (their rung asked at the end instead)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415

    order = [i.get("dimension") for part in interview.get("parts") or [] for i in part.get("items") or []]
    rungs = [f.get("dimension") for f in interview.get("followUps") or []] or None
    founder = founder_side(entry, line=line)
    # spec 118 (keel-cloud 183): the asked items are the page's (an `askedAfter` item skipped is no item), and the
    # failing line with the fewest whys so far goes first (`failing` / `whys`, read off the run by the walk)
    plan = fake.asks(picks, founder, order, link, b2b=is_b2b(entry), served=set(order), first=first, rungs=rungs,
                     late=late, failing=failing, whys=whys)
    out = []
    for asked in plan:
        question = follow_up_question(entry, picks, link, interview, token, first, line=line,
                                      stem=(asked["dimension"], asked["also"]))
        out.append({**question, "on": asked["on"]})
    return out


def the_step(step: str) -> str:
    """keel-cloud 118 `ItemFrames.theStep`: *the free trial* for *a free trial*; a step with its own article kept; since
    keel-cloud 221 FR-2 (spec 141 FR-4) an act-first smaller step said as its act, *trying a pair of caption glasses*
    (`spoken.smaller_said`)."""
    from instructions import spoken as spoken_mod                       # noqa: PLC0415
    if spoken_mod.opens_on_its_act(spoken_mod._lower(step.strip())):
        return spoken_mod.smaller_said(step)
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


#: keel-cloud 202 D4 (`RespondentQuestionsRules.TRAILING`): the words a trailing phrase of an occasion's clause opens on
#: -- the prepositions, a relative, *due* (*patients due for a screening*); never *of*, which holds a noun to its head
#: (*the day's list of patients*).
TRAILING = ("with", "on", "at", "for", "in", "from", "after", "before", "by", "during", "over", "across", "within",
            "who", "that", "which", "where", "when", "due")


def fitted(clause: str | None, window: Window) -> str | None:
    """keel-cloud 202 D4 (`RespondentQuestionsRules.fitted`): the occasion's clause cut by its trailing phrases, the
    rightmost first (never before its fourth word), so the Frequency question served around it is within the spoken cap
    (`STEM_MAX_WORDS`); None where the clause is absent, already fits, or no cut fits. Spec 139 FR-2 (keel-cloud 216 FR-3,
    `measuredFrequency`): measured on 174's frame, so every clause code chooses keeps 212's numbers."""
    if not clause or not clause.strip():
        return None
    served = _words(frequency_served_before216(window, clause))
    if served <= STEM_MAX_WORDS:
        return None
    budget = STEM_MAX_WORDS - (served - _words(clause))
    words = clause.strip().split()
    while len(words) > budget:
        at = next((i for i in range(len(words) - 1, 2, -1) if words[i].lower() in TRAILING), -1)
        if at < 0:
            return None
        words = words[:at]
    cut = re.sub(r"[,;:]$", "", " ".join(words))
    return None if cut == clause.strip() else cut


def possessive_time(clause: str | None) -> str | None:
    """keel-cloud 202 D4 (`RespondentQuestionsRules.possessiveTime`): a time word in the possessive names the occasion's
    own thing, never a period (*the day's list of patients*), so E1 reads the clause without it."""
    return None if clause is None else re.sub(r"(?i)\b(?:day|night|week|month|year|shift|morning|evening)'s\b",
                                              "occasion's", clause)


def gate_from_circumstance(window: Window, circumstance: str | None) -> str | None:
    """keel-cloud 131 FR-1's gate on the circumstance's event (`WindowFrame.gate` over `circumstanceEvent`), or None.
    Since keel-cloud 202 D4 (18-careforce, cycle 8) the event past the spoken cap is cut by its trailing phrases
    (`fitted`) before the job is ever taken -- *In the last 5 working days, did you have to call the day's list of
    patients?*, never the job's goal met (*did you get every one of them booked?*), which inverted the count."""
    clause = circumstance_event(circumstance)
    clause = (fitted(clause, window) or clause) if clause else clause
    return f"In the last {window_words(window)}, did {subject_led(clause)}?" if clause else None


def frequency_held(window: Window, clause: str) -> str:
    """keel-cloud 160 FR-2 (`WindowFrame.frequencyHeld`) on 131 FR-2: the served Frequency held to the spoken cap -- the
    whole (`frequency_served`); past 20 words the clause cut by its trailing phrases (the rightmost preposition first);
    else *... did that happen?*, the unit said (the grammar check is not mirrored). Keel-cloud 174 FR-5 (spec 115 FR-2)
    retired 160's judgement call 4, the unit dropped (*In the last 7 days, on how many did you ...?*,
    `frequency_unit_dropped`): the unit is never dropped. Spec 139 FR-2 (keel-cloud 216 FR-3): in 216's frame, a word
    shorter, so a clause at the cap is served whole."""
    return _frequency_held_in(window, clause, frequency_served)


def frequency_held_before216(window: Window, clause: str) -> str:
    """keel-cloud 216 FR-3 (`WindowFrame.frequencyHeldBefore216`): a Frequency stored in 174's opening is served in it,
    held to the cap as it was -- the clause cut, else *... did that happen?*."""
    return _frequency_held_in(window, clause, frequency_served_before216)


def _frequency_held_in(window: Window, clause: str, frame_of) -> str:
    from instructions import spoken as spoken_mod                     # noqa: PLC0415
    whole = frame_of(window, clause)
    if _words(whole) <= STEM_MAX_WORDS:
        return whole
    frame = _words(whole) - _words(clause)
    cut = spoken_mod.cut_to_fit(clause, STEM_MAX_WORDS - frame)
    held = frame_of(window, cut)
    return held if cut != clause and _words(held) <= STEM_MAX_WORDS else frame_of(window, None)


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
    """keel-cloud 118 `ItemFrames.smallerStep`: the Commitment list's second item, lower-cased, or None (none served).
    Spec 133 FR-2 (keel-cloud 211 FR-6): where the entry's step costs something and its list is the step alone, Keel's
    free smaller step the founder saved (`keels_smaller_step`)."""
    saved = entry.founder_list("commercial.commitment")
    items = (saved or {}).get("items") or []
    label = items[1].get("label") if len(items) > 1 else (keels_smaller_step(entry) or {}).get("label")
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

# ------------------------------------------------- spec 118 FR-2 / FR-4c(b): the items the page asks, and how

def asked_after(item: dict, answers_by_item: dict) -> tuple[bool, str | None]:
    """Spec 118 FR-2 (keel-cloud 181 FR-1 / T003, keel-web 155 T020 `askedAfterQuestion`): whether the page asks `item`
    of this person, and the question it shows in place of the item's. An item served `askedAfter {itemId, answers}`
    (Ability to pay on a chain study with a price) is asked only where the person's answer to `itemId` sends exactly one
    entry's `optionIds`, in order -- that entry's `question` (*You said about {their band}. ...*) is drawn; any other
    answer (a lower band, *I wouldn't pay for this*, the escape, none) skips it: no screen, nothing said, no answer
    sent. An item with no `askedAfter` is asked of everyone who reaches it: `(True, None)`. `answers_by_item` is
    `{itemId: wire answer}` (`PersonInputs.response`'s `answers`)."""
    after = (item or {}).get("askedAfter")
    if not isinstance(after, dict):
        return True, None
    sent = (answers_by_item.get(after.get("itemId")) or {}).get("optionIds") or []
    for answer in after.get("answers") or []:
        if list(answer.get("optionIds") or []) == list(sent) and sent:
            return True, answer.get("question")
    return False, None


def asked_items(items: list, answers_by_item: dict) -> list:
    """The items of a part the page draws for this person, in order -- `asked_after` applied (spec 118 FR-2)."""
    return [i for i in items or [] if asked_after(i, answers_by_item)[0]]


def two_steps_of(item: dict) -> dict | None:
    """Spec 118 FR-4c(b) (keel-cloud 185 FR-3, keel-web 156 T013 `twoStepsOfItem`): a ladder asked in two steps -- its
    spoken form `two_steps` over six options with the second step's lines served (`spoken.under` / `over`) -- as
    `{under: [band 1, band 2], middle: band 3, over: [band 4, band 5], close: option 6, phrases: step one's four, under_line,
    over_line}`; the phrases are the served `optionsLine` split (*Under $800 · $800 to under $2,500 · $2,500 or more ·
    or you wouldn't pay for this*). None on any other item (a lock from before 185 serves no lines: one ask)."""
    spoken = (item or {}).get("spoken") or {}
    labels = [o.get("label") for o in (item or {}).get("options") or []]
    if spoken.get("transform") != "two_steps" or len(labels) != 6 or not spoken.get("under") or not spoken.get("over"):
        return None
    line = str(spoken.get("optionsLine") or "").strip()
    line = line[:-1] if line.endswith(".") else line
    phrases = [p.strip() for p in line.split("; ")]
    if phrases and phrases[-1].startswith("or "):
        phrases[-1] = phrases[-1][3:]
    return {"under": labels[:2], "middle": labels[2], "over": labels[3:5], "close": labels[5],
            "phrases": phrases, "under_line": spoken.get("under"), "over_line": spoken.get("over")}


def step_one(item: dict, label: str) -> tuple[str, str | None]:
    """What the person says at Price's first step to give `label`, and the side it opens (`under` / `over`) or None
    where the first step is the answer (the middle band, *I wouldn't pay for this*): a band on a side is said as step
    one's phrase for that side (*Under $800*, *$2,500 or more*) -- the voice asks the two bands next
    (`ai-sheet[data-ask=under|over]`), where the band itself is said. An item not in two steps: the label, at once."""
    steps = two_steps_of(item)
    if steps is None or len(steps["phrases"]) < 3:
        return label, None
    if label in steps["under"]:
        return steps["phrases"][0], "under"
    if label in steps["over"]:
        return steps["phrases"][2], "over"
    return label, None


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
