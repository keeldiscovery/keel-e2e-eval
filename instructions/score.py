"""Every number a run reports (spec 009 FR-011/FR-013; spec 029 data-model §6, marks-v9 §2).

Three rules run through all of it, unchanged since `MARKS_VERSION` 1.

**Nothing is averaged before it is reported.** Each of the N runs is scored on its own and the
report carries the spread; a case that passes twice and fails once is an unstable instruction, not
a 67 %.

**`GUESSED` precision and recall are never optional** (call 5). Most stories in this corpus are
anchored, so a reader that answered `ANCHORED` to everything scores high on accuracy and has recall
zero on the one judgement the instrument exists to make.

**Three ways of being wrong stay three lines** (call 6): schema-invalid, shape refusal, rule
refusal -- three different instruction fixes, never summed.

At `MARKS_VERSION` 9 the subjects moved (call 28). `score_assumptions`, `score_reading` and the
alignment they rode on retired with `align.py` (call 29). What scores now:

- `score_compare` -- keel-cloud's engine against `expected` (call 34; `instructions/compare.py`);
- `score_calibration` / `score_respondent` -- `dimension_coverage`, `option_validity` and `no_leak`
  by code against the registry (calls 30-32; spec 029 US2/US3);
- `score_interpret` -- one anchoring judgement a readable person (call 33; US3);
- `brief.score_brief` -- four per-case marks, all or nothing (calls 35, 48).

At `MARKS_VERSION` 10 no count is typed here (call 47): every denominator is the registry's and the
entry's -- the calibrated slice per persona, the plan per part and link.

At `MARKS_VERSION` 11 the subjects' words moved and these checks follow (calls 52-56; keel-cloud
072 / 073, mirrored in `instructions/wording.py`): Prevalence and the gate are read as their `event`
clause, held to E1-E3; Frequency on a framed window and Price owe no text; W7, W9 and U1 are
structural; W3 / W8 hold to the names the corpus records; and the wording rules the subject only
instructs (S1, W1, W2, W5, W6) are counted per question into `wording`, reported, never marked.

At `MARKS_VERSION` 12 the two money questions are code's (calls 59-63; keel-cloud 074) and Ability to pay
-- derived -- is not in the calibration job at all, so its denominator is the *answered* set.

At `MARKS_VERSION` 13 the buyer's cost is one total (call 67; keel-cloud 077): Existing sacrifice owes
**nothing** on either screen, as Price does -- the calibration job's entry is its key (and note), options
refused with C2; the respondent job's item is its key alone, code composing the question over the recall
period. `W10` and `U1` retire (there is no model text and there are no kinds to hold them to).

`totals` rolls each over **its own** denominator and never another's.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import brief as brief_mod
from . import text as text_mod
from . import context as context_mod
from . import wording as wording_mod
from .registry import (DEFAULT_WINDOW, GATE_CONTROL, GATE_KEY, NUMERIC_FOUNDER_CONTROLS,
                       NUMERIC_RESPONDENT_CONTROLS, names_the_offer)


# ------------------------------------------------------------------------------------ compare

@dataclass
class CompareCaseScore:
    case_id: str
    entry_id: str
    subject: str = "COMPARE"
    checks: int = 0
    agreed: int = 0
    mismatches: list = field(default_factory=list)
    reported_diffs: list = field(default_factory=list)
    measured: bool = False
    reason: str | None = None

    @property
    def compare_correctness(self):
        return (self.agreed / self.checks) if (self.measured and self.checks) else None


def score_compare(case, entry, compare_score) -> CompareCaseScore:
    """One entry's `COMPARE` row: the diff `compare.py` made, carried onto the case. An engine that
    could not be asked is `measured: false` with its reason, and stays that way (call 13)."""
    return CompareCaseScore(case_id=case.case_id, entry_id=entry.id,
                            checks=compare_score.checks, agreed=compare_score.agreed,
                            mismatches=list(compare_score.mismatches),
                            reported_diffs=list(compare_score.reported_diffs),
                            measured=compare_score.measured, reason=compare_score.reason)


# -------------------------------------------------------------------------------- no_leak (§2.3)

def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


def registry_stems(registry, dimension) -> set:
    """Call 44a: the stems of the registry's own wording for the dimension being asked -- its
    `respondent` block (guidance, option_rule, chips, the B2B variant), its founder `option_rule`
    and `code_rule` (where the fixed escape labels are written: *None of these*), and the
    registry's `common` block (chips, *Something else*, placeholders). Wording the registry tells
    the model to use is never a leak. Its `lullaby` worked example is not read: it names
    Lullaby's mechanism."""
    if dimension is None:
        return set()
    founder = dimension.founder or {}
    texts = list(_strings(dimension.respondent or {}))
    texts += list(_strings([founder.get("option_rule"),
                            (founder.get("normalized") or {}).get("code_rule")]))
    texts += list(_strings(getattr(registry, "common", None) or {}))
    return {text_mod.stem(w) for t in texts for w in text_mod.content_words(t)}


#: Call 45 (decision 47): keel-cloud 058's `Vocabulary.PRODUCT_WORDS`, whole-word and
#: case-insensitive -- what the runtime can refuse in a PROBLEM calibration question before any
#: mechanism is confirmed.
PRODUCT_WORDS = (
    "app", "apps", "platform", "dashboard", "portal", "plugin", "api", "saas", "website",
    "algorithm", "device",
    "automate", "automates", "automated", "automating", "automation",
    "integrate", "integrates", "integrated", "integration", "integrations",
    "sync", "syncs", "synced", "syncing")
_PRODUCT_RE = re.compile(r"(?<![^\W_])(" + "|".join(PRODUCT_WORDS) + r")(?![^\W_])", re.IGNORECASE)


def sweep_a_calibration(texts, entry, exclude=frozenset()) -> dict:
    """Sweep A on a PROBLEM calibration question (call 45, decision 47): only what the runtime
    can apply at that step -- the product-word list, and the golden mechanism's own
    `mechanism_terms` (single words by stem, less the registry's wording for the dimension,
    call 44a; multi-word terms as phrases) -- in the question, its options and their belief
    phrases. A hit is a fault; nothing here goes to the judge."""
    blob = " ".join(str(t) for t in texts if t)
    hits = [m.group(1).lower() for m in _PRODUCT_RE.finditer(blob)]
    terms = [t for t in (entry.solution_mechanism or {}).get("mechanism_terms") or []]
    single = {text_mod.stem(t.lower()) for t in terms if len(text_mod.words(t)) == 1}
    single -= set(exclude)
    for word in text_mod.content_words(blob):
        if text_mod.stem(word) in single:
            hits.append(word)
    for phrase in entry.mechanism_phrases():
        if text_mod.phrase_in(phrase, blob):
            hits.append(" ".join(phrase))
    evidence = f"product or mechanism-term word(s) {sorted(set(hits))}" if hits else ""
    return {"fault": bool(hits), "hits": len(hits), "judged": 0, "evidence": evidence}


def sweep_a(texts, entry, judge, options=(), exclude=frozenset()) -> dict:
    """Sweep A (call 32): the golden mechanism's stems -- and its multi-word terms, as phrases -- in
    a question's stem (*texts*) and its option labels (*options*). A vocabulary hit **in the stem**
    is a fault outright. A hit on an **inflection-ledger** stem anywhere, or a vocabulary hit
    **only in an option label** (call 43: *phone*, *wheel*, *caught* -- generic nouns of the
    problem's own world, offered as answers rather than asked about; a multi-word term likewise,
    *signed off*), is a tie: the judge is asked
    once, cached, whether the question tells a stranger what the solution is, and only `SAME` is a
    fault. Every other word is the problem's own and is no hit at all.

    Returns `{fault: bool, hits: int, judged: int, evidence: str}`."""
    vocabulary = entry.vocabulary()
    ledger = entry.inflection_ledger()

    def swept(blob):
        direct, ties = [], []
        for word in text_mod.content_words(blob):
            stem = text_mod.stem(word)
            if stem in exclude:                                    # call 44a
                continue
            if stem in vocabulary:
                direct.append(word)
            elif stem in ledger:
                ties.append(word)
        for phrase in entry.mechanism_phrases():
            if text_mod.phrase_in(phrase, blob):
                direct.append(" ".join(phrase))
        return direct, ties

    stem_blob = " ".join(str(t) for t in texts if t)
    option_blob = " ".join(str(t) for t in options if t)
    blob = " ".join(b for b in (stem_blob, option_blob) if b)
    hits, stem_ties = swept(stem_blob)
    option_hits, option_ties = swept(option_blob)
    ties = stem_ties + option_ties
    judged = 0
    tie_fault = False
    if (ties or option_hits) and not hits:
        judged = 1
        tie_fault = bool(judge is not None and judge.reveals_solution(
            blob, entry.mechanism_one_liner(),
            context=",".join(sorted(set(ties + option_hits)))))
    fault = bool(hits) or tie_fault
    if hits:
        evidence = f"mechanism word(s) {sorted(set(hits))}"
    elif ties or option_hits:
        parts = []
        if option_hits:
            parts.append(f"mechanism word(s) in an option label {sorted(set(option_hits))}")
        if ties:
            parts.append(f"inflection tie(s) {sorted(set(ties))}")
        evidence = (f"{', '.join(parts)}, judged "
                    f"{'SAME -- it reveals the solution' if tie_fault else 'DIFFERENT'}")
    else:
        evidence = ""
    return {"fault": fault, "hits": len(hits) + len(option_hits) + len(ties), "judged": judged,
            "evidence": evidence}


# ------------------------------------------------------------- calibration (062; calls 30-32)

_NOT_SURE_RE = re.compile(r"not sure|don't know|dont know|unsure", re.IGNORECASE)
#: Call 44: a not-sure OPTION is one whose whole label, normalised, is one of these -- never a
#: label that merely contains the words (*Not sure it would fit* is a reason, not a chip);
#: keel-cloud 058's C3 makes the same change.
_NOT_SURE_LABELS = frozenset({"im not sure", "not sure", "dont know", "i dont know", "unsure",
                              "prefer not to say"})


def _is_not_sure_label(label) -> bool:
    return _label_form(label) in _NOT_SURE_LABELS
#: C4's ceiling on a belief phrase, in characters (keel-cloud 062, founder decision 32).
_BELIEF_PHRASE_MAX = 120
_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_LADDER_RE = re.compile(r"(B2C|B2B):\s*([a-z_, ]+)\.")


@dataclass
class CalibrationScore:
    case_id: str
    entry_id: str
    subject: str                 # the vector
    run_index: int
    coverage_of: int = 0
    coverage_hit: int = 0
    coverage_passed: bool = False
    validity_of: int = 0
    validity_hit: int = 0
    leak_of: int = 0
    leak_clean: int = 0
    leak_hits: int = 0
    leak_judged: int = 0
    leak_hit_items: int = 0      # questions/items with any no_leak hit (judged_fraction's base)
    faults: list = field(default_factory=list)      # [{key, check, evidence}]
    #: Call 56: the reported wording counts (`WORDING_KEYS`), never a mark.
    wording: dict = field(default_factory=dict)
    failed: str | None = None

    @property
    def coverage(self):
        return _fraction(self.coverage_hit, self.coverage_of)

    @property
    def validity(self):
        return _fraction(self.validity_hit, self.validity_of)

    @property
    def leak(self):
        return _fraction(self.leak_clean, self.leak_of)


def _coverage_faults(produced_keys: list, expected_keys: list) -> list:
    """Call 30: exactly one question a dimension, in `order`. A doubled, a missing, a foreign or
    an out-of-order key each fails the case."""
    faults = []
    missing = [k for k in expected_keys if k not in produced_keys]
    doubled = sorted({k for k in produced_keys if produced_keys.count(k) > 1})
    foreign = [k for k in produced_keys if k not in expected_keys]
    if missing:
        faults.append(f"missing {', '.join(missing)}")
    if doubled:
        faults.append(f"doubled {', '.join(doubled)}")
    if foreign:
        faults.append(f"outside the slice {', '.join(foreign)}")
    if not faults and produced_keys != expected_keys:
        faults.append(f"out of order: {', '.join(produced_keys)}")
    return faults


def _ladder_codes(dimension, b2b: bool) -> list | None:
    if dimension.normalized.get("kind") != "ladder":
        return None
    if b2b and (dimension.respondent.get("b2b") or {}).get("ladder_rungs"):
        return list(dimension.respondent["b2b"]["ladder_rungs"])
    for side, codes in _LADDER_RE.findall(dimension.normalized.get("code_rule") or ""):
        if (side == "B2B") == b2b:
            return [c.strip() for c in codes.split(",") if c.strip()]
    return None


#: The fixed codes a `model_written` rule names and the founder's options must carry (marks §2.2).
_REQUIRED_MODEL_WRITTEN: dict = {}              # v13: Existing sacrifice has no kinds, so no fixed `none`


def model_text(question: dict, dimension, window=DEFAULT_WINDOW, *, founder: bool = False) -> str | None:
    """The question text the model wrote **and a reader is shown** (calls 52, 61): `None` on Prevalence
    and the gate (the frame is code's around the `event`), on Frequency over a framed window, on
    Price (code's sentence) and on Existing sacrifice (code asks *What does it cost ... today?* of the founder
    and *{Last month}, what did it cost ... ?* of the buyer; any question the model writes is not read, v13).
    The one-unit window keeps its question."""
    if dimension.key == GATE_KEY or dimension.founder_price or dimension.respondent_code_written:
        return None
    if founder and dimension.founder_cost:
        return None
    if dimension.key == "problem.frequency" and window.frames_frequency:
        return None
    return question.get("question")


def _named_faults(text, dimension, *, short_name=None, offer_name=None) -> list:
    """W3 / W8 (call 55): a SOLUTION question carries the idea's short name, a COMMERCIAL one --
    Existing sacrifice aside -- the offer's; held only to a name the corpus records."""
    if not names_the_offer(dimension):
        return []
    name, rule = ((short_name, "W3") if dimension.vector == "SOLUTION" else (offer_name, "W8"))
    if name and not wording_mod.carries(text, name):
        what = "the idea by its short name" if rule == "W3" else "the offer by its one name"
        return [f"{rule}: the question does not name {what}, {name!r}, verbatim"]
    return []


def calibration_checks(question: dict, dimension, *, b2b: bool = False,
                       window=DEFAULT_WINDOW, short_name=None, offer_name=None) -> list:
    """Every structural rule of marks §2.2's calibration side, for one question; `[]` is valid.

    v11 (calls 52-55): Prevalence owes its `event` clause (E1-E3); Frequency on a framed window owes
    no text and a text written anyway is ignored; Price owes its key alone (options are C2); every
    other entry owes its question. W7 on a question, W9 on everything written, U1 on every Existing
    sacrifice kind but `none` (retired at v13), W3 / W8 where the corpus records the name.

    v13 (call 67): Existing sacrifice owes its key (and note) alone, as Price does -- options are C2
    (there are no kinds of cost), any question text the model wrote is ignored (never a fault, never
    held to W7 / W9 / W8); W9 still reads its `event`."""
    faults = []
    key = dimension.key
    event = question.get("event")
    # The text the applier reads: a framed Frequency's and Price's question is set aside before W7
    # and W9 are asked (`ScreenResultApplier`: `withQuestion(null)`), Prevalence's is not.
    asked = None if (dimension.founder_price or dimension.founder_cost
                     or (key == "problem.frequency" and window.frames_frequency)) \
        else question.get("question")
    written = " \n ".join(str(t) for t in [asked, event] + [
        v for o in question.get("options") or [] if isinstance(o, dict)
        for v in (o.get("label"), o.get("belief_phrase"))] if t)
    if dimension.founder_price or dimension.founder_cost:       # calls 53, 67: code's whole
        if question.get("options"):
            faults.append(f"C2: {len(question['options'])} options on "
                          f"{'Price' if dimension.founder_price else 'Existing sacrifice'}; its "
                          "range and period are code's input")
        hit = wording_mod.money(event)
        if hit:
            faults.append(f"W9: {hit!r} is money; code renders every amount")
        return faults
    if key == GATE_KEY:
        if not event:
            faults.append("E2: Prevalence carries `event`, the clause of what happened; code "
                          "writes the question around it")
        else:
            fault = wording_mod.event_fault(event, window)
            if fault:
                faults.append(fault)
    elif key == "problem.frequency" and window.frames_frequency:
        pass                                              # call 52: code's sentence, text ignored
    elif not str(question.get("question") or "").strip():
        faults.append("no question written")
    if asked:
        hint = wording_mod.tick_all(asked)
        if hint:
            faults.append(f"W7: {hint!r} is the control's hint; the question never says it")
    hit = wording_mod.money(written)
    if hit:
        faults.append(f"W9: {hit!r} is money; code renders every amount in the project's currency")
    text = model_text(question, dimension, window, founder=True)
    if text:
        faults += _named_faults(text, dimension, short_name=short_name, offer_name=offer_name)
    options = question.get("options")
    numeric = dimension.founder.get("control") in NUMERIC_FOUNDER_CONTROLS
    if numeric:
        if options:
            faults.append(f"{len(options)} options on a numeric control "
                          f"({dimension.founder.get('control')}) -- the registry owns its spec")
        spec = question.get("normalized")
        if isinstance(spec, dict):
            for name in ("unit_options", "default_unit", "axis_max", "axis_step", "extend_by",
                         "bins"):
                if name in spec and spec[name] != dimension.normalized.get(name):
                    faults.append(f"numeric spec {name} is {spec[name]!r}, the registry's is "
                                  f"{dimension.normalized.get(name)!r}")
        options = []
    elif not isinstance(options, list) or not options:
        return [f"no options on a closed control ({dimension.founder.get('control')})"]

    # keel-cloud 062 / instruction table §B #3, rule C2: the result carries **no code**. Option i
    # *is* the registry's code i -- the server joins by position -- so the order is the registry's by
    # construction and the count is the check. An explicit `normalized` a model writes anyway is a
    # cross-check against the position, never the join.
    stated = [o.get("normalized") if isinstance(o, dict) else None for o in options]
    labels = [text_mod.normalise(o.get("label")) if isinstance(o, dict) else "" for o in options]
    fixed = dimension.fixed_codes
    if fixed is not None:
        if len(options) != len(fixed):
            faults.append(f"{len(options)} options; the registry fixes {len(fixed)} codes, joined "
                          "by position")
        for index, code in enumerate(stated):
            if code is None:
                continue
            if code not in fixed:
                faults.append(f"option {index + 1} names {code!r}, which is not the registry's")
            elif index < len(fixed) and code != fixed[index]:
                faults.append(f"option {index + 1} names {code!r}; by position it is "
                              f"{fixed[index]!r} -- codes out of registry order")
    elif not numeric:
        ladder = _ladder_codes(dimension, b2b)
        if ladder is not None:
            if len(options) != len(ladder):
                faults.append(f"{len(options)} options; the ladder has {len(ladder)} rungs, "
                              "joined by position")
            elif any(c is not None and c != ladder[i] for i, c in enumerate(stated)):
                faults.append(f"the ladder is {ladder}, the options name {stated}")
        elif not 4 <= len(options) <= 6:
            faults.append(f"{len(options)} options; the rule asks 4-6")
        # A model-written set's codes are slugged from the labels by code (058 T053); when a model
        # states them anyway, they must at least be slugs and carry the fixed codes the rule names.
        written = [c for c in stated if c is not None]
        bad = [c for c in written if not isinstance(c, str) or not _SLUG_RE.match(c)]
        if bad:
            faults.append(f"code(s) {bad} are not slugs")
        if written:
            missing = [c for c in _REQUIRED_MODEL_WRITTEN.get(dimension.key, ())
                       if c not in written]
            if missing:
                faults.append(f"the code rule's fixed code(s) {missing} are missing")
    repeated = sorted({c for c in stated if c is not None and stated.count(c) > 1})
    if repeated:
        faults.append(f"code(s) repeated: {repeated}")
    twice = sorted({label for label in labels if label and labels.count(label) > 1})
    if twice:
        faults.append(f"label(s) repeated: {twice}")
    for option in options:
        if not isinstance(option, dict):
            faults.append(f"option {option!r} is not an object")
            continue
        label, phrase = option.get("label"), option.get("belief_phrase")
        # C4 as keel-cloud 062 reads it (call 37): a phrase EQUAL to its label is accepted; an
        # empty one, one over 120 characters, or one carrying a not-sure word is a fault.
        stripped = (phrase or "").strip()
        if not stripped:
            faults.append(f"option {label!r} carries no belief_phrase")
        elif len(stripped) > _BELIEF_PHRASE_MAX:
            faults.append(f"option {label!r}: its belief_phrase is {len(stripped)} characters, "
                          f"longer than {_BELIEF_PHRASE_MAX}")
        elif _NOT_SURE_RE.search(stripped):
            faults.append(f"option {label!r}: its belief_phrase carries a not-sure word")
        if _is_not_sure_label(label):
            faults.append(f"option {label!r} is a not-sure option -- the chip is UI")
    template = question.get("belief_template")
    if template is not None:
        if str(template).count("{value}") != 1:
            faults.append("the belief template does not carry {value} exactly once")
        if template != dimension.founder.get("belief_template"):
            faults.append("the belief template is not the registry's")
    # C7 retired (call 52): the window is in the sentence because code puts it there.
    return faults


def _question_texts(question: dict, dimension=None, window=DEFAULT_WINDOW, *, founder: bool = False) -> list:
    """The question's stem, alone (call 43: its options are swept apart) -- since v11 what the model
    wrote and a reader is shown (call 52): the `event` clause on Prevalence and the gate, no text on
    a code-written sentence."""
    if dimension is None:
        return [question.get("question")]
    return [model_text(question, dimension, window, founder=founder), question.get("event")
            if dimension.key == GATE_KEY else None]


def is_swept(dimension, window=DEFAULT_WINDOW, *, founder: bool = False) -> bool:
    """Whether `no_leak` sweeps an item at all (calls 52, 53, 61): never Price, never Frequency
    over a framed window, and -- on the founder's side -- never Existing sacrifice: code writes every
    word of those, so there is no model text to sweep. Read off the registry and the entry's window,
    so a dry run counts the same denominator."""
    if dimension.founder_price or dimension.respondent_code_written:
        return False
    if founder and dimension.founder_cost:
        return False
    return not (dimension.key == "problem.frequency" and window.frames_frequency)


#: The reported wording counts (call 56), summed per case and over the run -- never a mark.
WORDING_KEYS = ("questions", "words", "w1", "w2", "w6", "s1", "options", "w5")


def _wording(score, text, labels, *, founder: bool) -> None:
    if not text:
        return
    counted = wording_mod.reported(text, founder=founder)
    w = score.wording
    w["questions"] = w.get("questions", 0) + 1
    w["words"] = w.get("words", 0) + counted["words"]
    for name in ("w1", "w2", "w6", "s1"):
        w[name] = w.get(name, 0) + int(bool(counted.get(name)))
    labels = [label for label in labels if label]
    w["options"] = w.get("options", 0) + len(labels)
    w["w5"] = w.get("w5", 0) + wording_mod.long_options(labels)


def _option_texts(question: dict) -> list:
    texts = []
    for option in question.get("options") or []:
        if isinstance(option, dict):
            texts += [option.get("label"), option.get("belief_phrase")]
        else:
            texts.append(option)
    return texts


def score_calibration(case, entry, registry, result, *, judge=None,
                      failed: str | None = None) -> CalibrationScore:
    """One `CALIBRATION_QUESTIONS` case (062): coverage against the vector's slice (call 30),
    validity against the registry (call 31), and -- on the PROBLEM vector -- sweep A over every
    question and its options (call 32). Evidence per fault, so a miss is read, not only counted."""
    vector = case.meta.get("vector") or case.subject
    slice_keys = [d.key for d in registry.answered_slice(vector, entry.b2b())]         # calls 47, 61
    score = CalibrationScore(case_id=case.case_id, entry_id=entry.id, subject=vector,
                             run_index=case.run_index, coverage_of=len(slice_keys), failed=failed)
    questions = (result or {}).get("questions") if isinstance(result, dict) else None
    if failed or not isinstance(questions, list):
        score.failed = failed or "the result carried no questions list"
        return score
    questions = [q for q in questions if isinstance(q, dict)]
    produced = [q.get("key") for q in questions]
    coverage = _coverage_faults(produced, slice_keys)
    score.coverage_passed = not coverage
    score.coverage_hit = len(slice_keys) if score.coverage_passed else 0
    for fault in coverage:
        score.faults.append({"key": None, "check": "dimension_coverage", "evidence": fault})
    b2b = entry.b2b()
    window = context_mod.window_of(entry)
    for question in questions:
        key = question.get("key")
        if key not in slice_keys:
            continue
        dimension = registry.by_key(key)
        score.validity_of += 1
        checks = calibration_checks(question, dimension, b2b=b2b, window=window,
                                    short_name=context_mod.short_name_of(entry),
                                    offer_name=context_mod.offer_name_of(entry))
        if checks:
            score.faults.append({"key": key, "check": "option_validity",
                                 "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        _wording(score, model_text(question, dimension, window, founder=True),
                 [o.get("label") for o in question.get("options") or [] if isinstance(o, dict)],
                 founder=True)
        if vector == "PROBLEM" and is_swept(dimension, window, founder=True):
            score.leak_of += 1
            swept = sweep_a_calibration(                                   # call 45
                _question_texts(question, dimension, window, founder=True) + _option_texts(question), entry,
                exclude=registry_stems(registry, registry.by_key(key)))
            score.leak_hits += swept["hits"]
            score.leak_judged += swept["judged"]
            score.leak_hit_items += 1 if swept["hits"] else 0
            if swept["fault"]:
                score.faults.append({"key": key, "check": "no_leak",
                                     "evidence": swept["evidence"]})
            else:
                score.leak_clean += 1
    return score


# -------------------------------------------------------------- respondent (063; calls 30-32)

#: Respondent controls whose answer is typed or tapped, never picked from a list -- the registry's
#: numeric controls (invariant 6), read, never restated.
_FREE_CONTROLS = NUMERIC_RESPONDENT_CONTROLS
#: Call 38: controls whose options code writes (the axis, Yes/No); the model writes `null`.
_NULL_CONTROLS = _FREE_CONTROLS + (GATE_CONTROL,)
_NUMBER_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])")


def _option_label(option):
    return option.get("label") if isinstance(option, dict) else option


def _option_code(option):
    return option.get("code") if isinstance(option, dict) else None


def _registry_numbers(dimension, window=DEFAULT_WINDOW) -> set:
    """The numbers a respondent item may carry because the registry puts them there -- band edges,
    the axis, the project's recall window -- and never because the founder said them."""
    numbers = set()
    normalized = dimension.normalized
    for edge in normalized.get("bins") or []:
        numbers |= {float(n) for n in _NUMBER_RE.findall(str(edge))}
    for name in ("axis_max", "axis_step"):
        if isinstance(normalized.get(name), (int, float)):
            numbers.add(float(normalized[name]))
    if any(marker in (side.get("guidance") or "") for side in (dimension.founder,
                                                                  dimension.respondent)
           for marker in ("{window}", "{window_unit}", window.words(), window.unit_words())):
        numbers.add(float(window.count))
    return numbers


def _founder_numbers(answer) -> set:
    if not isinstance(answer, dict):
        return set()
    # `RespondentQuestionsRules.numbers`: an interval's bounds and (074) a cost estimate's low and high
    return {float(v) for k, v in answer.items()
            if k in ("lower", "upper", "value", "low", "high") and isinstance(v, (int, float))
            and not isinstance(v, bool)}


def respondent_checks(item: dict, dimension, plan_row: dict, founder_answer=None, *,
                      founder_labels: dict | None = None, window=DEFAULT_WINDOW,
                      part: int | None = None, short_name=None, offer_name=None) -> list:
    """Every structural rule of marks §2.2's respondent side, for one item; `[]` is valid.

    Call 38: **code appends, never the model** -- *Something else*, every respondent-only code the
    registry names (`registry.RESPONDENT_ESCAPES`) and every band, scale-axis and gate option -- so
    the golden plan row's `codes` (the engine's truth) are judged less those. What the model owes:
    a fixed-code control (and the ladder) one label per remaining code, the count exact; a set
    every founder label (058's R2 comparison, or its code; `founder_labels` is `{code: label}`
    from the corpus, the codes standing in where it records none) plus 2-3 distractors, a
    categorical pick (Target circumstance) the founder's labels and no distractor; Importance 4-6
    difficulties (keel-cloud's instruction; the server moves the problem's own off the top); a
    band, numeric or gate control the question only, `options` null. `founder_answer` is unused
    here since the bands are code's (sweep B still reads it).

    v11 (calls 52-55): Price is code's whole and owes nothing (what a model writes there is not
    read); the gate owes its `event` clause (E1-E3); Frequency over a framed window owes no text;
    every other item owes its question; W7 on a question, W9 on everything written, W3 on part 2 and W8
    on part 3 where the corpus records the name.

    v13 (call 67): Existing sacrifice (`cost_total`) is code's whole, as Price is -- the item is its key
    alone, nothing a model writes there is read, and W10 / U1 are retired. Ability to pay's four rungs
    are the respondent's fixed codes, so it is not a set."""
    from .registry import RESPONDENT_ESCAPES                  # noqa: PLC0415
    faults = []
    control = dimension.respondent.get("control")
    if dimension.respondent_code_written:                           # calls 53, 67: Price, the total
        return faults
    event = item.get("event")
    if dimension.key == GATE_KEY:
        if not event:
            faults.append("E2: the gate carries `event`, the clause of what happened; code writes "
                          "the question around it")
        else:
            fault = wording_mod.event_fault(event, window)
            if fault:
                faults.append(fault)
    elif dimension.key == "problem.frequency" and window.frames_frequency:
        pass                                              # call 52: code's sentence, text ignored
    elif not str(item.get("question") or "").strip():
        faults.append("no question written")
    text = model_text(item, dimension, window)
    if text:
        hint = wording_mod.tick_all(text)
        if hint:
            faults.append(f"W7: {hint!r} is the control's hint; the question never says it")
        if part in (2, 3) and names_the_offer(dimension):
            faults += _named_faults(text, dimension, short_name=short_name if part == 2 else None,
                                    offer_name=offer_name if part == 3 else None)
    written = " \n ".join(str(t) for t in [text, event] + [
        _option_label(o) for o in item.get("options") or []] if t)
    hit = wording_mod.money(written)
    if hit:
        faults.append(f"W9: {hit!r} is money; code renders every amount in the project's currency")
    if plan_row.get("control") not in (None, control):
        faults.append(f"the plan's control {plan_row.get('control')!r} is not the registry's "
                      f"{control!r}")
    if item.get("control") not in (None, control):
        faults.append(f"control {item.get('control')!r}; the registry's is {control!r}")
    for name in ("chips", "anchor"):
        if name in item and item[name] != dimension.respondent.get(name):
            faults.append(f"{name} {item[name]!r}; the registry's is "
                          f"{dimension.respondent.get(name)!r}")
    options = item.get("options")
    if control in _NULL_CONTROLS:
        if options:
            faults.append(f"{len(options)} options on a {control} control; code writes them")
        return faults
    if not isinstance(options, list) or not options:
        return faults + [f"no options on a closed {control} control"]
    want = [c for c in plan_row.get("codes") or [] if c not in RESPONDENT_ESCAPES]
    labels = [str(_option_label(o) or "") for o in options]
    codes = [_option_code(o) for o in options]
    for label in labels:                    # call 44: the WHOLE normalised label, never a prefix
        if is_escape_label(label):
            faults.append(f"escape row {label!r} written by the model; code appends it")
    for label in labels:
        if _is_not_sure_label(label):
            faults.append(f"option {label!r} is a not-sure option -- the chip is UI")
    coded = [c for c in codes if c]
    repeated = sorted({c for c in coded if coded.count(c) > 1})
    if repeated:
        faults.append(f"code(s) repeated: {repeated}")
    if plan_row.get("own_item"):                                   # Importance
        if not 4 <= len(options) <= 6:
            faults.append(f"{len(options)} difficulties; Importance takes 4 to 6")
        return faults
    is_set = (dimension.fixed_codes is None and not dimension.founder_numeric
              and not dimension.derived and control != "multi_choice_ladder")
    if not is_set:
        if want and len(options) != len(want):
            faults.append(f"{len(options)} options; the plan has {len(want)}"
                          + (" (the scale is fixed: nothing added)"
                             if control == "single_choice_5" else ""))
        if coded:
            missing = [c for c in want if c not in coded]
            foreign = [c for c in coded if c not in want]
            if missing:
                faults.append(f"missing code(s) {missing}")
            if foreign:
                faults.append(f"code(s) {foreign} are not the plan's")
        return faults
    from .corpus import FOUNDER_NONE                          # noqa: PLC0415
    shown = founder_labels or {c: c for c in want}
    founder = {_label_form(label): code for code, label in shown.items()}
    required = [c for c in shown if c not in RESPONDENT_ESCAPES and c not in FOUNDER_NONE
                and not is_escape_label(shown[c])]
    matched, distractors = set(), 0
    for label, code in zip(labels, codes):
        hit = code if code in shown else founder.get(_label_form(label))
        if hit:
            matched.add(hit)
        else:
            distractors += 1
    missing = [shown[c] for c in required if c not in matched]
    if missing:
        faults.append(f"missing founder label(s) {missing}")
    if dimension.normalized.get("kind") == "categorical":
        if distractors:
            faults.append(f"{distractors} distractor(s); a categorical pick on the founder's "
                          "labels takes none")
    elif not 2 <= distractors <= 3:
        faults.append(f"{distractors} distractor(s); a set takes 2 to 3")
    return faults


#: The escape rows keel-cloud 058 appends by code (`RespondentQuestionsRules.ESCAPES`, 4ea3062),
#: by their LABEL: production slugs the founder's escape (*None of these*) as
#: `none_of_these_<...>`, never the bare `none`, so a fixed slug cannot find it.
ESCAPE_LABELS = frozenset({
    "at no point that time", "nothing would have changed", "i wouldnt have reached for it at all",
    "nothing", "it was free or a gift", "it was free", "nothing it never came up", "nothing yet",
    "something else", "none of these"})


def is_escape_label(label) -> bool:
    """A code-appended escape row, told by its label (*None of these; they cope with what they
    have* included: the founder's own escape, which the respondent screen's code appends)."""
    form = _label_form(label)
    return form in ESCAPE_LABELS or form.startswith("none of these")


def _label_form(label) -> str:
    """keel-cloud 058's R2 comparison: case, apostrophes, whitespace and punctuation ignored."""
    text = re.sub(r"['\u2018\u2019]", "", str(label or "").lower())
    return re.sub(r"[\W_]+", " ", text).strip()


def sweep_b(texts, dimension, founder: dict, window=DEFAULT_WINDOW) -> dict:
    """Sweep B (call 32): the founder's own value for dimension *d* -- the chosen phrase, or a
    number they gave that the registry did not fix -- in respondent item *d*. A hit is a fault: the
    stranger is being told the answer the founder hopes for. *texts* are the item's question
    stem only -- never its option labels (call 40: a fixed-code control shows every rung, the
    founder's among them, and a set shows the founder's labels verbatim by R2), and never the
    part's reveal (call 44b: R6's claim-word rule governs it, and it names the mechanism's
    moment)."""
    blob = " ".join(str(t) for t in texts if t)
    hits = []
    phrase = text_mod.normalise((founder or {}).get("belief_phrase"))
    if phrase and phrase in text_mod.normalise(blob):
        hits.append(f"the founder's phrase {phrase!r}")
    said = _founder_numbers((founder or {}).get("answer")) - _registry_numbers(dimension, window)
    shown = {float(n) for n in _NUMBER_RE.findall(blob)}
    for number in sorted(said & shown):
        hits.append(f"the founder's number {number:g}")
    return {"fault": bool(hits), "hits": len(hits), "evidence": "; ".join(hits)}


@dataclass
class RespondentScore(CalibrationScore):
    part: int = 0
    link: str = "PRIMARY"


def score_respondent(case, entry, registry, plan, result, *, judge=None,
                     failed: str | None = None) -> RespondentScore:
    """One `RESPONDENT_QUESTIONS` case (063): coverage against the plan's part (call 30), validity
    on the respondent side of §2.2, sweep A on Part 1's items (the stranger has not been told the
    idea yet) and sweep B on every item's stem, never the reveal (call 44b; the founder's own values, never
    shown to a stranger; call 40: not its option labels)."""
    part = case.meta.get("part")
    link = case.meta.get("link") or "PRIMARY"
    plan = plan if plan is not None else entry.plan(registry)
    keys = list(plan.get(part) or [])
    score = RespondentScore(case_id=case.case_id, entry_id=entry.id, subject=case.subject,
                            run_index=case.run_index, coverage_of=len(keys), failed=failed,
                            part=part, link=link)
    items = (result or {}).get("items") if isinstance(result, dict) else None
    if failed or not isinstance(items, list):
        score.failed = failed or "the result carried no items list"
        return score
    items = [i for i in items if isinstance(i, dict)]
    produced = [i.get("key") for i in items]
    coverage = _coverage_faults(produced, keys)
    score.coverage_passed = not coverage
    score.coverage_hit = len(keys) if score.coverage_passed else 0
    for fault in coverage:
        score.faults.append({"key": None, "check": "dimension_coverage", "evidence": fault})
    window = context_mod.window_of(entry)
    short_name = context_mod.short_name_of(entry)
    reveal = (result or {}).get("reveal") if isinstance(result, dict) else None
    if part == 2 and link == "PRIMARY" and short_name and isinstance(reveal, dict) and \
            not wording_mod.carries(f"{reveal.get('title') or ''} {reveal.get('body') or ''}",
                                    short_name):
        score.faults.append({"key": "reveal", "check": "option_validity",          # call 55
                             "evidence": f"W3: the reveal does not name the idea by its short "
                                         f"name, {short_name!r}, verbatim"})
    for item in items:
        key = item.get("key")
        if key not in keys:
            continue
        dimension = registry.by_key(key)
        plan_row = (entry.respondent_questions or {}).get(key) or {}
        founder = entry.founder_calibration.get(key) or {}
        score.validity_of += 1
        checks = respondent_checks(item, dimension, plan_row, founder.get("answer"),
                                   founder_labels=entry.founder_labels(key), window=window,
                                   part=part, short_name=short_name,
                                   offer_name=context_mod.offer_name_of(entry))
        if checks:
            score.faults.append({"key": key, "check": "option_validity",
                                 "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        _wording(score, model_text(item, dimension, window),
                 [_option_label(o) for o in item.get("options") or []], founder=False)
        if not is_swept(dimension, window):                        # calls 52, 53
            continue
        stems = _question_texts(item, dimension, window)
        item_hit = False
        if part == 1 and link == "PRIMARY":
            score.leak_of += 1
            swept = sweep_a(stems, entry, judge,                            # call 43
                            options=[_option_label(o) for o in item.get("options") or []],
                            exclude=registry_stems(registry, dimension))
            score.leak_hits += swept["hits"]
            score.leak_judged += swept["judged"]
            item_hit = bool(swept["hits"])
            if swept["fault"]:
                score.faults.append({"key": key, "check": "no_leak", "sweep": "A",
                                     "evidence": swept["evidence"]})
            else:
                score.leak_clean += 1
        score.leak_of += 1
        swept = sweep_b(stems, dimension, founder, window)                # calls 40, 44b
        score.leak_hits += swept["hits"]
        score.leak_hit_items += 1 if (item_hit or swept["hits"]) else 0
        if swept["fault"]:
            score.faults.append({"key": key, "check": "no_leak", "sweep": "B",
                                 "evidence": swept["evidence"]})
        else:
            score.leak_clean += 1
    return score


# ------------------------------------------------------------------ INTERPRET (064; call 33)

@dataclass
class InterpretScore:
    case_id: str
    entry_id: str
    subject: str                  # the person
    run_index: int
    given: int = 1
    answered: int = 0
    agreed: int = 0
    golden: str | None = None
    produced: object = None
    confusion: dict = field(default_factory=lambda: {"aa": 0, "ag": 0, "ga": 0, "gg": 0})
    missing_ids: list = field(default_factory=list)
    extra_ids: list = field(default_factory=list)
    shape_fault: int = 0
    failed: str | None = None

    @property
    def anchoring_accuracy(self):
        return _fraction(self.agreed, self.answered)


def score_interpret(case, entry, person, result, *, failed: str | None = None) -> InterpretScore:
    """One read of one gate story: the model's word against the corpus's (call 33, one judgement a
    respondent). **Keyed on the person**: the result's `invitationId` must be the one the context
    carried, and a `stage` or an `anchorId` a model writes anyway is neither read nor refused (US3.4).
    An `anchoring` outside `ANCHORED`/`GUESSED` is a shape refusal, counted against the zero."""
    expected_id = f"{entry.id}/{person.person}"
    score = InterpretScore(case_id=case.case_id, entry_id=entry.id, subject=person.person,
                           run_index=case.run_index, golden=person.anchoring, failed=failed)
    if failed or not isinstance(result, dict):
        score.missing_ids = [person.person]
        return score
    invitation = result.get("invitationId")
    if invitation is not None and invitation != expected_id:
        score.extra_ids = [invitation]
        score.missing_ids = [person.person]
        return score
    answer = result.get("anchoring")
    anchorings = result.get("anchorings")
    if answer is None and isinstance(anchorings, list) and len(anchorings) == 1 \
            and isinstance(anchorings[0], dict):
        # keel-cloud's INTERPRET contract is still v8's (`anchorings[]`) until 064 narrows it: one
        # story, one anchoring -- its `anchorId` neither read nor refused.
        answer = anchorings[0].get("anchoring")
    score.produced = answer
    if answer not in ("ANCHORED", "GUESSED"):
        if answer is not None:
            score.shape_fault = 1
        score.missing_ids = [person.person]
        return score
    score.answered = 1
    score.agreed = int(answer == person.anchoring)
    key = ("g" if person.anchoring == "GUESSED" else "a") + ("g" if answer == "GUESSED" else "a")
    score.confusion[key] += 1
    return score


# ------------------------------------------------------------------------------------- totals

def _fraction(hit, of):
    return (hit / of) if of else None


def _sum(scores, name) -> int:
    return sum(int(getattr(s, name, 0) or 0) for s in scores)


def wording_totals(scores) -> dict:
    """Call 56: the reported wording counts over `scores`, never a mark."""
    out = {name: 0 for name in WORDING_KEYS}
    for score in scores:
        for name, value in (getattr(score, "wording", None) or {}).items():
            out[name] = out.get(name, 0) + int(value or 0)
    return out


def _question_screen(scores) -> dict:
    """Coverage, validity and leak over one question screen's cases (calibration or respondent)."""
    return {
        "cases": len(scores),
        "coverage": {"hit": _sum(scores, "coverage_hit"), "of": _sum(scores, "coverage_of")},
        "validity": {"hit": _sum(scores, "validity_hit"), "of": _sum(scores, "validity_of")},
        "leak": {"clean": _sum(scores, "leak_clean"), "of": _sum(scores, "leak_of")},
    }


def totals(calibration_scores=(), respondent_scores=(), interpret_scores=(), compare_scores=(),
           *, brief_scores=(), errored: int = 0, refusals_by_rule: dict | None = None,
           shape_refusals: int = 0, schema_invalid: int = 0, refusals_measured: bool = False,
           refusals_shown: int = 0, judge_calls: int = 0, leak_hits: int | None = None,
           leak_judged: int | None = None, refusals_unmeasured_kinds=()) -> dict:
    """The run's own numbers (data-model §6), each summed over its own denominator."""
    calibration = _question_screen(calibration_scores)
    respondent = _question_screen(respondent_scores)
    both = list(calibration_scores) + list(respondent_scores)

    coverage_of = calibration["coverage"]["of"] + respondent["coverage"]["of"]
    validity_of = calibration["validity"]["of"] + respondent["validity"]["of"]
    leak_of = calibration["leak"]["of"] + respondent["leak"]["of"]
    hits = _sum(both, "leak_hits") if leak_hits is None else leak_hits
    judged = _sum(both, "leak_judged") if leak_judged is None else leak_judged
    hit_items = _sum(both, "leak_hit_items")

    # INTERPRET: one judgement a readable person (call 33). The chipped are outside every count.
    answered = _sum(interpret_scores, "answered")
    agreed = _sum(interpret_scores, "agreed")
    confusion = {"aa": 0, "ag": 0, "ga": 0, "gg": 0}
    for s in interpret_scores:
        for key, value in (getattr(s, "confusion", None) or {}).items():
            confusion[key] = confusion.get(key, 0) + value
    called_guessed = confusion["ag"] + confusion["gg"]
    was_guessed = confusion["ga"] + confusion["gg"]
    interpret_shape = _sum(interpret_scores, "shape_fault")

    compare_measured = bool(compare_scores) and all(s.measured for s in compare_scores)
    checks = sum(s.checks for s in compare_scores if s.measured)
    compare_agreed = sum(s.agreed for s in compare_scores if s.measured)

    brief = brief_mod.totals(list(brief_scores or []))

    return {
        **brief,
        "calibration_cases": calibration["cases"],
        "calibration_coverage": calibration["coverage"],
        "calibration_validity": calibration["validity"],
        "calibration_leak": calibration["leak"],
        "respondent_cases": respondent["cases"],
        "respondent_coverage": respondent["coverage"],
        "respondent_validity": respondent["validity"],
        "respondent_leak": respondent["leak"],
        # Call 56: reported per screen, never marked (`marks.judge` reads none of it).
        "wording": {"calibration": wording_totals(calibration_scores),
                    "respondent": wording_totals(respondent_scores)},
        "dimension_coverage": _fraction(calibration["coverage"]["hit"]
                                        + respondent["coverage"]["hit"], coverage_of),
        "option_validity": _fraction(calibration["validity"]["hit"]
                                     + respondent["validity"]["hit"], validity_of),
        "no_leak": _fraction(calibration["leak"]["clean"] + respondent["leak"]["clean"], leak_of),
        "leak_hits": hits,
        "leak_judged": judged,
        "leak_hit_items": hit_items,
        # Items the judge decided over items with any hit -- one unit, reported, never marked
        # (a word count beside an item count read 0.72 on run 20261008T155720Z).
        "judged_fraction": (judged / hit_items) if hit_items else 0.0,
        "judge_calls": judge_calls,
        "anchoring_accuracy": _fraction(agreed, answered),
        "guessed_precision": _fraction(confusion["gg"], called_guessed),
        "guessed_recall": _fraction(confusion["gg"], was_guessed),
        "confusion": confusion,
        "people_given": _sum(interpret_scores, "given"),
        "people_answered": answered,
        "reading_missing_ids": sum(len(getattr(s, "missing_ids", []) or [])
                                   for s in interpret_scores),
        "reading_extra_ids": sum(len(getattr(s, "extra_ids", []) or []) for s in interpret_scores),
        "chipped_skipped": 0,
        "compare_checks": checks,
        "compare_agreed": compare_agreed,
        "compare_correctness": _fraction(compare_agreed, checks) if compare_measured else None,
        "compare_measured": compare_measured,
        "compare_reported_diffs": sum(len(s.reported_diffs) for s in compare_scores),
        "compare_unmeasured": [{"entry": s.entry_id, "reason": s.reason}
                               for s in compare_scores if not s.measured],
        "refusals_by_rule": dict(refusals_by_rule or {}),
        # v6 (call 22): how many answers the aggregate judged -- the rate's denominator.
        "refusals_shown": int(refusals_shown or 0),
        "refusals_measured": refusals_measured,
        "refusals_unmeasured_kinds": list(refusals_unmeasured_kinds or ()),
        # A produced reading whose `anchoring` is neither word is a shape refusal (spec 029 Edge
        # Cases), counted against the absolute zero beside the aggregate's own.
        "shape_refusals": int(shape_refusals or 0) + interpret_shape,
        "schema_invalid": schema_invalid,
        "errored": errored,
    }


def spread(scores: list, metric) -> dict:
    """Per case (entry + subject), the min and max of `metric` across the N runs.

    The point of reporting it: an average of a metric that was 1.0 once and 0.0 twice describes no
    run that happened.
    """
    buckets = {}
    for s in scores:
        value = metric(s)
        buckets.setdefault(f"{s.entry_id}/{s.subject}", []).append(value)
    out = {}
    for key, values in buckets.items():
        real = [v for v in values if v is not None]
        out[key] = {
            "runs": values,
            "min": min(real) if real else None,
            "max": max(real) if real else None,
        }
    return out
