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
- `brief.score_brief` -- five per-case marks, all or nothing (call 35).

`totals` rolls each over **its own** denominator and never another's.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import brief as brief_mod
from . import text as text_mod
from .registry import NUMERIC_FOUNDER_CONTROLS


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

def sweep_a(texts, entry, judge) -> dict:
    """Sweep A (call 32): the golden mechanism's stems -- and its multi-word terms, as phrases -- in
    a question's text and options. A vocabulary hit is a fault outright. A hit on an
    **inflection-ledger** stem is a tie: the judge is asked once, cached, whether the question tells
    a stranger what the solution is, and only `SAME` is a fault. Every other word is the problem's
    own and is no hit at all.

    Returns `{fault: bool, hits: [word...], judged: int, evidence: str}`."""
    blob = " ".join(str(t) for t in texts if t)
    vocabulary = entry.vocabulary()
    ledger = entry.inflection_ledger()
    hits, ties = [], []
    for word in text_mod.content_words(blob):
        stem = text_mod.stem(word)
        if stem in vocabulary:
            hits.append(word)
        elif stem in ledger:
            ties.append(word)
    for phrase in entry.mechanism_phrases():
        if text_mod.phrase_in(phrase, blob):
            hits.append(" ".join(phrase))
    judged = 0
    tie_fault = False
    if ties and not hits:
        judged = 1
        tie_fault = bool(judge is not None and judge.reveals_solution(
            blob, entry.mechanism_one_liner(), context=",".join(sorted(set(ties)))))
    fault = bool(hits) or tie_fault
    if hits:
        evidence = f"mechanism word(s) {sorted(set(hits))}"
    elif ties:
        evidence = (f"inflection tie(s) {sorted(set(ties))}, judged "
                    f"{'SAME -- it reveals the solution' if tie_fault else 'DIFFERENT'}")
    else:
        evidence = ""
    return {"fault": fault, "hits": len(hits) + len(ties), "judged": judged,
            "evidence": evidence}


# ------------------------------------------------------------- calibration (062; calls 30-32)

_NOT_SURE_RE = re.compile(r"not sure|don't know|dont know|unsure", re.IGNORECASE)
#: C4's ceiling on a belief phrase, in characters (keel-cloud 062, founder decision 32).
_BELIEF_PHRASE_MAX = 120
_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_SEVEN_NIGHTS_RE = re.compile(r"\b(7|seven)\s+nights?\b", re.IGNORECASE)   # the default window
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
    faults: list = field(default_factory=list)      # [{key, check, evidence}]
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
_REQUIRED_MODEL_WRITTEN = {"commercial.existing_sacrifice": ("none",)}


def calibration_checks(question: dict, dimension, *, b2b: bool = False) -> list:
    """Every structural rule of marks §2.2's calibration side, for one question; `[]` is valid."""
    faults = []
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
        if _NOT_SURE_RE.search(str(label or "")):
            faults.append(f"option {label!r} is a not-sure option -- the chip is UI")
    template = question.get("belief_template")
    if template is not None:
        if str(template).count("{value}") != 1:
            faults.append("the belief template does not carry {value} exactly once")
        if template != dimension.founder.get("belief_template"):
            faults.append("the belief template is not the registry's")
    if dimension.key == "problem.prevalence" and not _SEVEN_NIGHTS_RE.search(
            str(question.get("question") or "")):
        faults.append("the gate's question does not carry the 7-night window")
    return faults


def _question_texts(question: dict) -> list:
    texts = [question.get("question")]
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
    slice_keys = [d.key for d in registry.slice(vector)]
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
    for question in questions:
        key = question.get("key")
        if key not in slice_keys:
            continue
        score.validity_of += 1
        checks = calibration_checks(question, registry.by_key(key), b2b=b2b)
        if checks:
            score.faults.append({"key": key, "check": "option_validity",
                                 "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        if vector == "PROBLEM":
            score.leak_of += 1
            swept = sweep_a(_question_texts(question), entry, judge)
            score.leak_hits += swept["hits"]
            score.leak_judged += swept["judged"]
            if swept["fault"]:
                score.faults.append({"key": key, "check": "no_leak",
                                     "evidence": swept["evidence"]})
            else:
                score.leak_clean += 1
    return score


# -------------------------------------------------------------- respondent (063; calls 30-32)

#: Respondent controls whose answer is typed or tapped, never picked from a list.
_FREE_CONTROLS = ("segmented_0_to_7", "number_with_unit", "two_numbers_optional")
#: Call 38: controls whose options code writes (bins, the axis, Yes/No); the model writes `null`.
_NULL_CONTROLS = _FREE_CONTROLS + ("single_choice_bands", "gate_yes_no")
_SOMETHING_ELSE_RE = re.compile(r"^\s*something else\b", re.IGNORECASE)
_NUMBER_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])")


def _option_label(option):
    return option.get("label") if isinstance(option, dict) else option


def _option_code(option):
    return option.get("code") if isinstance(option, dict) else None


def _registry_numbers(dimension) -> set:
    """The numbers a respondent item may carry because the registry puts them there -- band edges,
    the axis, the 7-night window -- and never because the founder said them."""
    numbers = set()
    normalized = dimension.normalized
    for edge in normalized.get("bins") or []:
        numbers |= {float(n) for n in _NUMBER_RE.findall(str(edge))}
    for name in ("axis_max", "axis_step"):
        if isinstance(normalized.get(name), (int, float)):
            numbers.add(float(normalized[name]))
    if "7 nights" in (dimension.founder.get("guidance") or "") or \
            "7 nights" in (dimension.respondent.get("guidance") or ""):
        numbers.add(7.0)
    return numbers


def _founder_numbers(answer) -> set:
    if not isinstance(answer, dict):
        return set()
    return {float(v) for k, v in answer.items()
            if k in ("lower", "upper", "value") and isinstance(v, (int, float))}


def respondent_checks(item: dict, dimension, plan_row: dict, founder_answer=None, *,
                      founder_labels: dict | None = None) -> list:
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
    here since the bands are code's (sweep B still reads it)."""
    from .registry import RESPONDENT_ESCAPES                  # noqa: PLC0415
    faults = []
    control = dimension.respondent.get("control")
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
    if any(_SOMETHING_ELSE_RE.match(label) for label in labels):
        faults.append("'Something else' written by the model; code appends it")
    for label in labels:
        if _NOT_SURE_RE.search(label):
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
              and control != "multi_choice_ladder")
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
    required = [c for c in shown if c not in RESPONDENT_ESCAPES and c not in FOUNDER_NONE]
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


def _label_form(label) -> str:
    """keel-cloud 058's R2 comparison: case, apostrophes, whitespace and punctuation ignored."""
    text = re.sub(r"['\u2018\u2019]", "", str(label or "").lower())
    return re.sub(r"[\W_]+", " ", text).strip()


def sweep_b(texts, dimension, founder: dict) -> dict:
    """Sweep B (call 32): the founder's own value for dimension *d* -- the chosen phrase, or a
    number they gave that the registry did not fix -- in respondent item *d*. A hit is a fault: the
    stranger is being told the answer the founder hopes for."""
    blob = " ".join(str(t) for t in texts if t)
    hits = []
    phrase = text_mod.normalise((founder or {}).get("belief_phrase"))
    if phrase and phrase in text_mod.normalise(blob):
        hits.append(f"the founder's phrase {phrase!r}")
    said = _founder_numbers((founder or {}).get("answer")) - _registry_numbers(dimension)
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
    idea yet) and sweep B on every item (the founder's own values, never shown to a stranger)."""
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
    for item in items:
        key = item.get("key")
        if key not in keys:
            continue
        dimension = registry.by_key(key)
        plan_row = (entry.respondent_questions or {}).get(key) or {}
        founder = entry.founder_calibration.get(key) or {}
        score.validity_of += 1
        checks = respondent_checks(item, dimension, plan_row, founder.get("answer"),
                                   founder_labels=entry.founder_labels(key))
        if checks:
            score.faults.append({"key": key, "check": "option_validity",
                                 "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        texts = [item.get("question")] + [_option_label(o) for o in item.get("options") or []]
        if part == 1 and link == "PRIMARY":
            score.leak_of += 1
            swept = sweep_a(texts, entry, judge)
            score.leak_hits += swept["hits"]
            score.leak_judged += swept["judged"]
            if swept["fault"]:
                score.faults.append({"key": key, "check": "no_leak", "sweep": "A",
                                     "evidence": swept["evidence"]})
            else:
                score.leak_clean += 1
        score.leak_of += 1
        swept = sweep_b(texts, dimension, founder)
        score.leak_hits += swept["hits"]
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
        "dimension_coverage": _fraction(calibration["coverage"]["hit"]
                                        + respondent["coverage"]["hit"], coverage_of),
        "option_validity": _fraction(calibration["validity"]["hit"]
                                     + respondent["validity"]["hit"], validity_of),
        "no_leak": _fraction(calibration["leak"]["clean"] + respondent["leak"]["clean"], leak_of),
        "leak_hits": hits,
        "leak_judged": judged,
        "judged_fraction": (judged / hits) if hits else 0.0,
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
