"""The vectors corpus becomes the script (spec 039, the corpus journeys as vectors journeys).

**Since spec 040 the corpus is revision 10 and the contract 13** (keel-cloud 087 / 088 / 089): the keys table below
reads the new export (eight screens, `ASKED` among them) and the one-unit window's branches are gone (D13,
runs/DRIFT.md #74 closed). The script's *results* and the typed inputs below still write revision 9's shapes -- the
founder's model-written option sets, the respondent questionnaire, the brief's tiles -- and are re-pointed at the
founder lists, `{key, event}` items, the `asked` faces and the brief's answers by the later journey spec, once keel-web
specs 7, 8 and 10 land; until then the unit tests that read the corpus through them skip by name.

One revision-9 corpus entry in; out come the three things S-005, S-006 and S-007 need to drive the
**vector corridor** deterministically, and nothing else:

1. a **keel-runtime scripted-executor script** keyed by screen name -- the five corridor screens
   (`CONTEXT_INTERPRET`, `PROBLEM_INTERPRET`, `SOLUTION_MECHANISM`, `CALIBRATION_QUESTIONS`,
   `RESPONDENT_QUESTIONS`), the gate-story reading (`INTERPRET`) and the brief's reading (`BRIEF`),
   every result written from the entry's own stored texts and its own codes;
2. the **context-keys table** that script is matched through (`context_keys_for`), derived from
   keel-cloud's own export rather than copied -- see that function for why it is not the export
   byte for byte;
3. the **founder's typed inputs** (the four context fields, the recall window, the two seeds, one
   answer per calibrated dimension, the persona) and **each person's typed inputs** (the gate, the
   story or chip, one closed answer per item, by dimension and by code).

**One reader, one hash.** The entry is read through `instructions/corpus.py` -- the revision-9
reader the instruction eval already uses -- and never a second time.

**What the corpus does not carry is composed, and named** (`COMPOSED`). Revision 9 records the
golden *beliefs*, *codes* and *people*; it records no model *wording* -- no calibration question, no
option label for a registry-fixed scale, no respondent question, no Prevalence `event` clause, no
`occasion`, no idea lines. A screen result needs all of them, so this module writes them from the
entry's own context fields in one fixed register, and the spec's *disagreements* section lists every
one. A composed word never reaches an assertion about a standing: the engine compares codes.

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

from instructions import corpus as corpus_reader

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# The screen names the script is keyed by. `RESPONDENT_QUESTIONS` is four names, not one -- see
# `context_keys_for`.
CONTEXT_SCREEN = "CONTEXT_INTERPRET"
PROBLEM_SCREEN = "PROBLEM_INTERPRET"
MECHANISM_SCREEN = "SOLUTION_MECHANISM"
CALIBRATION_SCREEN = "CALIBRATION_QUESTIONS"
RESPONDENT_SCREEN = "RESPONDENT_QUESTIONS"
INTERPRET_SCREEN = "INTERPRET"
BRIEF_SCREEN = "BRIEF"
#: keel-cloud 088 (contract 12): the `asked` faces of a saved Compatibility / Adoption friction list. Its keys are
#: the export's own; what the script answers on it is the later journey spec's (spec 040 *Follow-ups*).
ASKED_SCREEN = "ASKED"
RESPONDENT_ALIASES = {(1, "PRIMARY"): "RESPONDENT_QUESTIONS_P1",
                      (2, "PRIMARY"): "RESPONDENT_QUESTIONS_P2",
                      (3, "PRIMARY"): "RESPONDENT_QUESTIONS_P3",
                      (3, "COMMERCIAL_B2B"): "RESPONDENT_QUESTIONS_P3_B2B"}
CORRIDOR_SCREENS = (CONTEXT_SCREEN, PROBLEM_SCREEN, MECHANISM_SCREEN, CALIBRATION_SCREEN,
                    ASKED_SCREEN, INTERPRET_SCREEN, BRIEF_SCREEN)

LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"

# keel-cloud `IdeaLines.BELIEF_FRAME` (spec 084, rule L4): the idea's third line starts with it.
BELIEF_FRAME = "The people building it believe it would "

#: The one note every composed calibration question carries (`respondent_note` is required).
RESPONDENT_NOTE = "Respondents are asked about their own most recent time, never about this."

#: Every place this module writes a word the corpus does not record (spec 039 *Disagreements*).
COMPOSED = (
    "CONTEXT_INTERPRET.occasion -- r9 records no occasion; composed as the word 'time'",
    "SOLUTION_MECHANISM.idea_what / idea_how / idea_belief -- r9 records none; composed from the mechanism",
    "CALIBRATION_QUESTIONS question texts, Prevalence's event, and the option labels and belief phrases of "
    "every registry-fixed scale -- r9 records only the founder's chosen code and its phrase",
    "CALIBRATION_QUESTIONS commercial.purchase_friction labels -- r9 records three labels that do not slug "
    "to its codes; the calibration needs four to six whose slugs are the codes",
    "RESPONDENT_QUESTIONS question texts, the gate's event, the fixed-scale labels and Importance's "
    "difficulty labels (each the slug-inverse of its corpus code)",
    "RESPONDENT_QUESTIONS commercial.purchase_friction distractors -- r9 records none; a set needs two",
    "BRIEF reading -- r9 records none; a referee-worded reading citing the entry's deal-breakers",
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

def load(keel_cloud) -> corpus_reader.Corpus:
    """The corpus, through `instructions/corpus.py` and nothing else: revision 9 or a refusal."""
    return corpus_reader.load(keel_cloud)


def entry_for(keel_cloud, entry_id: str):
    corpus = load(keel_cloud)
    entry = corpus.by_id(entry_id)
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
    (`numeric.axisMax`; the respondent's `segmented_0_to_7` runs 0..count), and frames it only on a
    window of more than one unit. Revision 9 keeps every Frequency belief and pick on a 0-to-7 axis
    in units of its own ("days out of 7", "invoices out of 7"), which the corpus README records as
    *known, not corrected*. Where the founder's range or any pick lies past the window's count the
    founder cannot state it and no respondent can answer it, so the journey leaves Frequency **out**
    (`unsure`) rather than inventing a number (spec 039 *Disagreements*, D-1).
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
    """keel-web `RECALL_WINDOW_WORDS`: "the last month", "7 nights", "2 weeks" -- what the context
    card's *Counting the last ...* line carries."""
    return f"{window.count} {_UNIT_WORDS[window.unit][1]}"


# ------------------------------------------------------------------------- composed labels

#: One label and one belief phrase per registry-fixed code, in a register that names no product,
#: no mechanism, no claim word and no money (rules X1, C5, C6, W9). The founder's chosen code's
#: phrase is replaced by the corpus's own `belief_phrase`, so the belief sentence keel-cloud writes is
#: the corpus's.
FIXED_LABELS = {
    "problem.prevalence": [
        ("Fewer than 2 in 10", "p_0_20", "Only a few"),
        ("2 to 4 in 10", "p_20_40", "A minority"),
        ("4 to 6 in 10", "p_40_60", "Around half"),
        ("6 to 8 in 10", "p_60_80", "Most"),
        ("8 to 10 in 10", "p_80_100", "Nearly all")],
    "problem.importance": [
        ("The biggest difficulty they face", "biggest", "the biggest difficulty"),
        ("One of their top three", "top_three", "one of the top three"),
        ("Somewhere in the middle", "middle", "a middling one"),
        ("A minor one next to the others", "minor", "a minor one"),
        ("It barely registers against the others", "negligible", "barely on the list")],
    "problem.current_solution_satisfaction": [
        ("Very well; they rarely feel stuck", "works_well", "serves them reliably"),
        ("Fairly well; it does the job most times", "mostly_works", "does the job most of the time"),
        ("Mixed; about half the time", "hit_and_miss", "is hit and miss"),
        ("Poorly; they often end up stuck", "works_poorly", "serves them poorly"),
        ("Very poorly; there is no reliable way", "no_reliable_way", "gives them no reliable way")],
    "solution.compatibility": [
        ("Straight away, before trying anything", "before_any_attempt",
         "right at the start, before anything is tried"),
        ("After the first attempt has not done it", "after_first_attempt_fails",
         "once the first attempt has failed"),
        ("After several attempts", "after_several_attempts", "only after several attempts"),
        ("Only once nothing else has done it", "only_when_nothing_works",
         "only when nothing else has done it"),
        ("It would not fit in at all", "would_not_fit", "nowhere; it would not fit")],
    "solution.relative_advantage": [
        ("Fewer things tried along the way", "fewer_attempts", "fewer things tried"),
        ("A shorter time from start to finish", "shorter_time", "a shorter time"),
        ("Less worry while it is happening", "less_worry", "less worry in the moment"),
        ("Less need to call on someone else", "less_help_needed", "less need for a second pair of hands"),
        ("Less strain afterwards", "easier_recovery", "an easier recovery afterwards")],
    "solution.adoption_friction": [
        ("Nothing extra at all", "nothing_extra", "nothing at all"),
        ("One tap to start", "one_tap", "a single tap"),
        ("A few taps", "a_few_taps", "a few taps"),
        ("A short one-time setup, then a tap", "setup_once", "a one-time setup, then a tap"),
        ("A longer setup done beforehand", "daytime_setup", "a proper setup done beforehand")],
    "commercial.buyer_payer_alignment": [
        ("The person who has the problem pays, with no one else to agree", "same_person",
         "the same person uses it, decides and pays"),
        ("They decide, but someone else pays", "user_decides_other_pays",
         "they decide and someone else pays"),
        ("They decide together with someone else", "joint_decision", "they decide jointly"),
        ("Someone else decides and pays", "someone_else_decides", "someone else decides and pays"),
        ("An institution pays", "institution_pays", "an institution pays")],
    "commercial.ability_to_pay": [
        ("From a budget line that already existed", "existing_line", "an existing line"),
        ("From a new line someone signed off", "new_line_signed_off", "a new line signed off"),
        ("Taken from other spending", "taken_from_other_spend", "taken from other spend"),
        ("There was no budget for it", "no_budget", "no budget")],
}

#: The B2C ladder's rungs (keel-cloud `ScreenResultApplier.B2C_RUNGS`) and the B2B one.
B2C_RUNGS = ("setup", "install", "mic", "next_episode", "contact_me")
B2B_RUNGS = ("call", "read_only_trial", "it_intro", "data", "paid_pilot")

#: The escapes keel-cloud appends to a respondent item and the model never writes
#: (`RespondentQuestionsRules.ESCAPES`), plus "Something else".
RESPONDENT_ESCAPES = {"would_not_fit", "would_not_reach", "free_or_gift", "it_was_free",
                      "never_came_up", "nothing_yet", "something_else"}


def slug(label: str) -> str:
    """keel-cloud `ScreenResultApplier.slugs` for one label: lower-cased, non-alphanumerics to
    `_`, the first four words."""
    import unicodedata
    base = unicodedata.normalize("NFD", label)
    base = "".join(c for c in base if unicodedata.category(c) != "Mn").lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
    words = base.split("_") if base else ["option"]
    return "_".join(words[:4])


def label_of_code(code: str) -> str:
    """The slug-inverse of a corpus code: `matching_deliveries` -> `Matching deliveries`."""
    text = code.replace("_", " ").strip()
    return text[:1].upper() + text[1:]


# ------------------------------------------------------------------------- the founder's words

def _ctx(entry) -> dict:
    return entry.context or {}


def _sentence(text: str) -> str:
    text = " ".join(str(text).split()).strip()
    return text[:1].upper() + text[1:]


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


def event_past(entry) -> str:
    """Prevalence's clause for the founder (rules E1-E3): what happened, past tense, no time word."""
    return f"had a time when {_ctx(entry)['circumstance']}"


def event_base(entry) -> str:
    """The gate's clause for the respondent: base form, second person."""
    return f"have a time when {_ctx(entry)['circumstance']}"


def context_result(entry) -> dict:
    ctx = _ctx(entry)
    return {"understands": ctx["understood"], "actor": ctx["actor"],
            "actor_plural": ctx["actor_plural"], "job": ctx["job"],
            "circumstance": ctx["circumstance"], "segment": ctx["segment"], "occasion": "time"}


def problem_result(entry) -> dict:
    return {"statement": (entry.interpretations or {})["problem"], "offer_name": offer_name(entry)}


def idea_lines(entry) -> dict:
    m = entry.solution_mechanism or {}
    what = f"Imagine {short_name(entry)}."
    how = _sentence(f"{m['trigger']}, {m['actor']} {m['mechanism']}; it gives {m['output']}.")
    belief = BELIEF_FRAME + f"make a real difference when {_ctx(entry)['circumstance']}."
    return {"what": what, "how": how[:300], "belief": belief[:200]}


def mechanism_result(entry) -> dict:
    m = entry.solution_mechanism or {}
    terms = list(m.get("mechanism_terms") or [])
    if len(terms) < 3:
        # keel-cloud wants 3-8 mechanism terms; r9's Paidly records two. The short name's own
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
            "idea_what": idea["what"], "idea_how": idea["how"], "idea_belief": idea["belief"]}


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


def _founder(entry, key: str) -> dict:
    return entry.founder_calibration.get(key) or {}


def _chosen_codes(entry, key: str) -> list[str]:
    answer = _founder(entry, key).get("answer")
    if isinstance(answer, str):
        return [answer]
    if isinstance(answer, list):
        return [str(a) for a in answer]
    return []


def purchase_friction_labels(entry) -> list[tuple[str, str]]:
    """`(label, code)` for the founder's Purchase friction options: one per corpus code (the plan
    row's codes less the escapes), each label the slug-inverse of its code so keel-cloud's slug is
    the corpus code, padded to four with a fixed fourth that slugs to no corpus code."""
    codes = [c for c in (entry.respondent_questions.get("commercial.purchase_friction") or {})
             .get("codes") or [] if c not in RESPONDENT_ESCAPES]
    pairs = [(label_of_code(c), c) for c in codes]
    for spare in ("Contract terms", "Training the team", "Changing habits"):
        if len(pairs) >= 4:
            break
        if slug(spare) not in codes:
            pairs.append((spare, slug(spare)))
    return pairs


def commitment_labels(entry) -> list[tuple[str, str]]:
    rungs = B2B_RUNGS if is_b2b(entry) else B2C_RUNGS
    labels = _founder(entry, "commercial.commitment").get("labels") or []
    if len(labels) != len(rungs):
        raise VectorsScriptError(f"{entry.id}: commercial.commitment carries {len(labels)} labels; "
                                 f"the ladder is {len(rungs)} rungs")
    return list(zip(labels, rungs))


def _phrase(entry, key: str, code: str, default: str) -> str:
    """The corpus's own belief phrase on the founder's chosen option -- the highest ticked rung on
    the ladder, the only tick on a one-tick set -- and the composed one elsewhere."""
    chosen = _chosen_codes(entry, key)
    phrase = _founder(entry, key).get("belief_phrase")
    if not phrase or code not in chosen:
        return default
    if key == "commercial.commitment":
        return phrase if code == chosen[-1] else default
    if len(chosen) > 1:
        return default
    return phrase


def calibration_question(entry, key: str) -> dict:
    ctx = _ctx(entry)
    q: dict = {"key": key, "respondent_note": RESPONDENT_NOTE}
    options: list[tuple[str, str]] = []
    if key == "problem.prevalence":
        q["event"] = event_past(entry)
    elif key == "problem.frequency":
        pass
    elif key in ("commercial.price", "commercial.existing_sacrifice"):
        pass
    elif key == "problem.importance":
        q["question"] = (f"Among the difficulties that come up when {ctx['circumstance']}, where "
                         "does this one rank?")
    elif key == "problem.current_solution_satisfaction":
        q["question"] = f"How well does today's way of handling it serve {ctx['actor_plural']}?"
    elif key == "solution.compatibility":
        q["question"] = f"At what point would {ctx['actor_plural']} turn to {short_name(entry)}?"
    elif key == "solution.relative_advantage":
        q["question"] = (f"What must {short_name(entry)} do better than today's way for them to "
                         "switch?")
    elif key == "solution.adoption_friction":
        q["question"] = (f"How much extra effort would they accept at that moment to get "
                         f"{short_name(entry)}?")
    elif key == "commercial.buyer_payer_alignment":
        q["question"] = f"Who decides on, and pays for, {offer_name(entry)}?"
    elif key == "commercial.purchase_friction":
        q["question"] = f"What could slow or stop them buying {offer_name(entry)}?"
        options = purchase_friction_labels(entry)
    elif key == "commercial.commitment":
        q["question"] = f"Which real next steps would they take now to try {offer_name(entry)}?"
        options = commitment_labels(entry)
    else:
        raise VectorsScriptError(f"{entry.id}: no calibration wording for {key}")
    if key in FIXED_LABELS and key != "commercial.ability_to_pay":
        q["options"] = [{"label": label, "belief_phrase": _phrase(entry, key, code, phrase)}
                        for label, code, phrase in FIXED_LABELS[key]]
    elif options:
        q["options"] = [{"label": label, "belief_phrase": _phrase(entry, key, code, label.lower())}
                        for label, code in options]
    return q


def calibration_result(entry, vector: str) -> dict:
    return {"vector": vector,
            "questions": [calibration_question(entry, key) for key in calibrated_keys(entry, vector)]}


@dataclass(frozen=True)
class CalibrationAnswer:
    dimension: str
    body: dict          # the wire's CalibrationAnswer, `dimension` included

    def as_wire(self) -> dict:
        return dict(self.body)


def calibration_answers(entry, vector: str) -> list[CalibrationAnswer]:
    """One typed answer per calibrated dimension, the corpus's own (keel-cloud
    `VectorCorpusFixture.founderAnswer`'s mapping): codes for a closed control, `interval` for
    Frequency, `cost` / `price` for the two commercial numbers, `unsure` for a dimension left out.
    Ability to pay is never sent -- it is derived."""
    out = []
    keys = founder_keys(entry, vector)
    for key in keys:
        founder = _founder(entry, key)
        answer = founder.get("answer")
        body: dict = {"dimension": key}
        if founder.get("unsure") or answer is None:
            body["unsure"] = True
        elif key == "problem.frequency":
            if not frequency_fits(entry):
                body["unsure"] = True
            else:
                window = window_of(entry)
                body["interval"] = {"low": answer["lower"], "high": answer["upper"],
                                    "unit": f"{_UNIT_WORDS[window.unit][1]} out of {window.count}"}
        elif key == "commercial.existing_sacrifice":
            body["cost"] = {k: answer[k] for k in ("mode", "low", "high", "period") if k in answer}
            if answer.get("rate") is not None:
                body["cost"]["rate"] = answer["rate"]
        elif key == "commercial.price":
            body["price"] = {k: answer[k] for k in ("low", "high", "period")}
        elif isinstance(answer, (str, list)):
            body["codes"] = _chosen_codes(entry, key)
        else:
            raise VectorsScriptError(f"{entry.id}: {key}'s founder answer {answer!r} has no wire shape")
        out.append(CalibrationAnswer(dimension=key, body=body))
    return out


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
        keys = [k for k in keys if k not in ("commercial.ability_to_pay",
                                              "commercial.purchase_friction")]
    return [k for k in keys if k not in left_out]


def respondent_jobs(entry) -> list[tuple[int, str]]:
    if is_b2b(entry):
        return [(1, LINK_PRIMARY), (2, LINK_PRIMARY), (3, LINK_B2B)]
    return [(1, LINK_PRIMARY), (2, LINK_PRIMARY), (3, LINK_PRIMARY)]


def importance_labels(entry) -> list[str]:
    """Importance's difficulties, the problem's own first (keel-cloud moves it off the top), each the
    slug-inverse of its corpus code so keel-cloud's slug is the corpus code."""
    row = entry.respondent_questions.get("problem.importance") or {}
    own = row.get("own_item")
    codes = [c for c in row.get("codes") or [] if c not in RESPONDENT_ESCAPES]
    if own not in codes:
        raise VectorsScriptError(f"{entry.id}: problem.importance's own_item {own!r} is not one of "
                                 f"its codes {codes}")
    ordered = [own] + [c for c in codes if c != own]
    return [label_of_code(c) for c in ordered]


def respondent_item(entry, key: str, part: int) -> dict:
    ctx = _ctx(entry)
    item: dict = {"key": key}
    if key in ("commercial.price", "commercial.existing_sacrifice", "solution.relative_advantage",
               "problem.frequency"):
        return item
    if key == "problem.prevalence":
        item["event"] = event_base(entry)
        return item
    if key == "problem.importance":
        item["question"] = (f"If you could make one part of that time easier, when "
                            f"{ctx['circumstance']}, which would it be?")
        item["options"] = importance_labels(entry)
        return item
    words = {
        "problem.current_solution_satisfaction": "That time, how well did your own way of handling it go?",
        "solution.compatibility": f"Think back to that time. At what point could {short_name(entry)} have fitted?",
        "solution.adoption_friction": (f"That time, how much could you have managed to get "
                                       f"{short_name(entry)}?"),
        "commercial.ability_to_pay": (f"When you last paid for {offer_name(entry)}, where did the money "
                                      "come from?"),
        "commercial.buyer_payer_alignment": f"Who would decide on, and pay for, {offer_name(entry)}?",
        "commercial.purchase_friction": (f"The last time you nearly bought {offer_name(entry)}, what got "
                                         "in the way?"),
        "commercial.commitment": f"Which of these would you actually do now to try {offer_name(entry)}?",
    }
    if key not in words:
        raise VectorsScriptError(f"{entry.id}: no respondent wording for {key}")
    item["question"] = words[key]
    if key in FIXED_LABELS:
        item["options"] = [label for label, code, _ in FIXED_LABELS[key]
                           if code not in RESPONDENT_ESCAPES]
    elif key == "commercial.purchase_friction":
        founder = [label for label, _ in purchase_friction_labels(entry)]
        # The founder's labels verbatim plus two distractors, the founder's first label never first
        # (rule R2). The distractors are the referee's and slug to no corpus code.
        item["options"] = ["Waiting for a quote", founder[0], "A competing offer"] + founder[1:]
    elif key == "commercial.commitment":
        item["options"] = [label for label, _ in commitment_labels(entry)]
    return item


def respondent_result(entry, part: int, link: str) -> dict:
    return {"part": part, "link": link,
            "items": [respondent_item(entry, key, part) for key in plan_keys(entry, part, link)]}


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


def deal_breaker_cites(entry) -> dict[str, list[str]]:
    """One or two dimension keys per vector to cite: the vector's deciding dimension first (it is
    always among `facts.keys`), then the next deal-breaker the founder did not leave out."""
    order = {"PROBLEM": ["problem.prevalence", "problem.importance",
                         "problem.current_solution_satisfaction"],
             "SOLUTION": ["solution.compatibility", "solution.relative_advantage",
                          "solution.adoption_friction"],
             "COMMERCIAL": ["commercial.existing_sacrifice", "commercial.buyer_payer_alignment",
                            "commercial.commitment"]}
    verdicts = entry.expected.get("vector_verdicts") or {}
    out = {}
    for vector, keys in order.items():
        keys = [k for k in keys if not entry.unsure(k)]
        deciding = (verdicts.get(vector) or {}).get("deciding")
        if deciding in keys:
            keys = [deciding] + [k for k in keys if k != deciding]
        out[vector] = keys[:2]
    return out


def brief_result(entry) -> dict:
    """The BRIEF reading, worded by the referee and checkable without a model: every sentence cites
    a deal-breaker of its own vector, carries no digit, no currency, no name and no banned word, and
    there are no tests, no quotes and no `sharpest` (keel-cloud `BriefReading.check`)."""
    cites = deal_breaker_cites(entry)
    who = entry.title.split("—")[0].strip()

    def sentence(text, keys):
        return {"text": text, "cites": list(keys)}

    lead = f"Scripted by the referee from the frozen corpus entry for {who}, not written by a model."
    return {
        "headline": sentence(lead, [cites["PROBLEM"][0]]),
        "tiles": {v.lower(): sentence(f"The {v.lower()} reading is the counted standing, as scripted.",
                                      cites[v][:1]) for v in VECTORS},
        "problem": {"conclusion": sentence("The problem is read off the deal-breakers below.",
                                           cites["PROBLEM"][:1]),
                    "infer": sentence("Two problem deal-breakers are read together here.",
                                      cites["PROBLEM"][:2])},
        "solution": {"conclusion": sentence("The solution is read off its deal-breakers.",
                                            cites["SOLUTION"][:1])},
        "commercial": {"conclusion": sentence("The commercial case is read off its deal-breakers.",
                                              cites["COMMERCIAL"][:1])},
        "next": {"sentence": sentence("Read the counted standings before deciding anything.",
                                      [cites["PROBLEM"][0]]),
                 "tests": []},
        "quotes": [],
    }


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
    """The runtime script for one entry. `CALIBRATION_QUESTIONS` is three entries in the corridor's
    own order -- PROBLEM on the problem's confirmation, SOLUTION on the mechanism's, COMMERCIAL on
    the persona -- because the job's context key set is the same for all three and the scripted
    executor consumes a screen's entries in order. `INTERPRET` is one entry per readable person, in
    corpus order, which is why the journey reads after each person."""
    screens: dict[str, list[dict]] = {
        CONTEXT_SCREEN: [_completed(context_result(entry))],
        PROBLEM_SCREEN: [_completed(problem_result(entry))],
        MECHANISM_SCREEN: [_completed(mechanism_result(entry))],
        CALIBRATION_SCREEN: [_completed(calibration_result(entry, v)) for v in VECTORS],
    }
    for part, link in respondent_jobs(entry):
        screens[RESPONDENT_ALIASES[(part, link)]] = [_completed(respondent_result(entry, part, link))]
    interpret = interpret_entries(entry)
    if interpret:
        screens[INTERPRET_SCREEN] = interpret
    screens[BRIEF_SCREEN] = [_completed(brief_result(entry))]
    return GeneratedScript(entry_id=entry.id, entry_sha256=entry.sha256,
                           source=f"keel-cloud canon/designs/measured-beliefs/corpus/{entry.path.name}",
                           screens=screens)


def context_keys_for(exported: dict) -> dict:
    """The scripted executor's screen table, from keel-cloud's own `context-keys.json` export.

    Three changes, each forced by keel-runtime's exact key-set match and each derived from the
    export rather than typed:

    * **`RESPONDENT_QUESTIONS` becomes four names.** The export writes the *union* of the four key
      sets keel-cloud's `ScreenContextBuilder` uses -- part 1 carries no `mechanism` and no
      `offer_name`, part 2 adds `mechanism`, part 3 on the primary link adds both, part 3 on the
      decision-maker's link adds `offer_name` alone -- so only one of the four would ever match.
      The three lock jobs land in keel-cloud's order, not the script's, so each part gets its own
      alias (`RESPONDENT_ALIASES`) and its own entry.
    * **The classic screens are dropped.** No classic job runs on a vectors project, and a table
      that cannot answer one is the honest table.
    * Nothing else: `CALIBRATION_QUESTIONS`, `INTERPRET` and `BRIEF` are the export's own sets.
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
            "`offer_name`; the four per-part key sets cannot be derived")
    base = [k for k in union if k not in ("mechanism", "offer_name")]
    out[RESPONDENT_ALIASES[(1, LINK_PRIMARY)]] = base
    out[RESPONDENT_ALIASES[(2, LINK_PRIMARY)]] = base + ["mechanism"]
    out[RESPONDENT_ALIASES[(3, LINK_PRIMARY)]] = union
    out[RESPONDENT_ALIASES[(3, LINK_B2B)]] = base + ["offer_name"]
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


def founder_inputs(entry) -> FounderInputs:
    ctx = _ctx(entry)
    market = entry.market or {}
    statements = entry.statements or {}
    missing = [k for k in ("problem", "solution") if not statements.get(k)]
    if missing:
        raise VectorsScriptError(f"{entry.id}: no {', '.join(missing)} statement")
    if is_b2b(entry):
        role = entry.role(entry.decision_maker_role()) or {}
        decider = {"kind": "SOMEONE_ELSE", "role": role.get("label") or entry.decision_maker_role()}
    else:
        decider = {"kind": "SAME_PERSON"}
    return FounderInputs(
        project_name=entry.title,
        country=market.get("country") or "GB", region=market.get("region"),
        language=market.get("language") or "en-GB",
        context_fields={"actor": ctx["actor"], "job": ctx["job"],
                        "circumstance": ctx["circumstance"], "segment": ctx["segment"]},
        window=window_of(entry),
        problem_seed=" ".join(str(statements["problem"]).split()),
        solution_seed=" ".join(str(statements["solution"]).split()),
        decider=decider,
        calibration={v: calibration_answers(entry, v) for v in VECTORS},
        hourly_rate=hourly_rate(entry),
    )


@dataclass(frozen=True)
class Pick:
    """One item's answer, by dimension and by code -- the ids are computed per token."""
    dimension: str
    codes: list = field(default_factory=list)
    advantages: list = field(default_factory=list)
    cost: dict | None = None
    scale: int | None = None
    chip: str | None = None
    #: The recall period the corpus recorded a cost total over (`quarter` throughout r9).
    cost_period: str | None = None

    def asked_over(self, period: str | None) -> "Pick":
        """This cost total re-expressed over `period`, the recall period keel-cloud asks it over
        (`InterviewItem.costTotal.recallPeriod`), by keel-cloud's own `Period` days -- so the cost the
        engine normalises to the founder's period is the corpus's to the last digit (spec 039 D-3)."""
        if self.cost is None or self.cost.get("nothing") or not period or not self.cost_period \
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
        out["optionIds"] = [option_id(token, self.dimension, c) for c in self.codes]
        if "something_else" in self.codes:
            out["somethingElse"] = True
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

    def response(self, token: str, recall_period: str | None = None) -> dict:
        """The one `POST /v2/i/{token}/interview/response` body; a cost total re-expressed over
        `recall_period`, the period the interview asks it over."""
        answers = [p.asked_over(recall_period).as_wire(token) for p in self.picks]
        if self.link == LINK_B2B:
            return {"answers": answers}
        if not self.recency:
            return {"recency": False, "answers": []}
        body: dict = {"recency": True, "answers": answers}
        if self.anchor_chip:
            body["anchorChip"] = self.anchor_chip
        elif self.story:
            body["story"] = self.story
        return body


_CHIPS = {"cant_recall": "CANT_RECALL", "rather_not_say": "RATHER_NOT_SAY"}

#: keel-cloud `Period`'s days, the one table a cost total is normalised by.
PERIOD_DAYS = {"day": 1.0, "week": 7.0, "month": 30.4375, "quarter": 91.3125, "year": 365.25}


def _pick(entry, key: str, raw) -> Pick:
    if isinstance(raw, dict) and raw.get("chip"):
        return Pick(dimension=key, chip=str(raw["chip"]).upper())
    if key == "commercial.existing_sacrifice":
        if not isinstance(raw, dict):
            raise VectorsScriptError(f"{entry.id}: {key} pick {raw!r} is not a cost total")
        if raw.get("nothing"):
            return Pick(dimension=key, cost={"nothing": True}, cost_period=raw.get("period"))
        return Pick(dimension=key, cost={"mode": raw["mode"], "value": raw["value"]},
                    cost_period=raw.get("period"))
    if key == "solution.relative_advantage":
        return Pick(dimension=key, codes=[raw["answer"]], advantages=list(raw.get("advantages") or []))
    if key == "problem.frequency":
        return Pick(dimension=key, scale=int(raw))
    if isinstance(raw, list):
        return Pick(dimension=key, codes=[str(c) for c in raw])
    return Pick(dimension=key, codes=[str(raw)])


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
        people.append(PersonInputs(
            person=person.person, link=person.link,
            recency=None if person.link == LINK_B2B else person.recency == "yes",
            story=person.story, anchor_chip=_CHIPS.get(person.chip) if person.chip else None,
            picks=picks, pilot_opt_in=person.pilot_opt_in, anchoring=person.anchoring))
    return people


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
                        "calibration": {v: [a.as_wire() for a in answers]
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
