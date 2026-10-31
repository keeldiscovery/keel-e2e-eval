"""Every number a run reports (spec 009 FR-011/FR-013; spec 029 data-model §6, marks-v9 §2; spec 040, the October
redesign).

Three rules run through all of it, unchanged since `MARKS_VERSION` 1.

**Nothing is averaged before it is reported.** Each of the N runs is scored on its own and the
report carries the spread; a case that passes twice and fails once is an unstable instruction, not
a 67 %.

**`GUESSED` precision and recall are never optional** (call 5). Most stories in this corpus are
anchored, so a reader that answered `ANCHORED` to everything scores high on accuracy and has recall
zero on the one judgement the instrument exists to make.

**Three ways of being wrong stay three lines** (call 6): schema-invalid, shape refusal, rule
refusal -- three different instruction fixes, never summed.

**At `MARKS_VERSION` 18 the model writes no question at all** (keel-cloud 087 / 088; calls 77-85). What it writes,
and what is scored here by code against the registry keel-cloud exports:

- `score_calibration` (`CALIBRATION_QUESTIONS`, `founder-lists.md`) -- coverage: one entry a dimension of the vector's
  answered slice, in order (C1); validity: Prevalence's `event` (E1-E3) and its five fifths (C2-C4), Frequency / Price
  / Existing sacrifice their key and note alone (C2), and **every list dimension's draft** held to `L1`-`L5` against
  the registry's `founder.saves` -- with the `asked` face of a Compatibility or Adoption friction item held to the
  `K` rules too, because a drafted face the founder keeps reaches a stranger unchanged (keel-cloud 088 FR-003's
  vouching; call 85); no_leak: sweep A over the PROBLEM job's written words (Prevalence's clause and fifths,
  Importance's five, Current solution's phrase and outcomes);
- `score_respondent` (`RESPONDENT_QUESTIONS`) -- coverage: one `{key}` a planned item (R1); validity: the gate's
  `event` (E1-E4: framed, the gate and Frequency at most 20 words); no_leak: sweeps A and B over that one clause;
  every other item is code's whole, and anything else a model writes there is not read;
- `score_asked` (`ASKED`, `asked.md`) -- coverage: every index handed phrased once (K1); validity: each face's
  `K2`-`K6` (`instructions/spoken.face_faults`);
- `score_interpret` -- one anchoring judgement a readable person (call 33);
- `score_compare` -- keel-cloud's engine against `expected` (call 34; `instructions/compare.py`).

(`brief.score_brief` and its seven reading marks retired at v20 with keel-cloud 104's BRIEF screen; call 116.)

The deterministic marks -- `spoken_form` (`instructions/spoken.py`) and `brief_facts`
(`instructions/brief_facts.compare`), born at v18, and `report_overview` (`instructions/overview.compare`), born at
v20 -- are measured at zero spend, beside `compare_correctness`.

`totals` rolls each over **its own** denominator and never another's.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import context as context_mod
from . import spoken as spoken_mod
from . import text as text_mod
from . import wording as wording_mod
from .registry import ADOPTION_KEY, COMPATIBILITY_KEY, DEFAULT_WINDOW, GATE_KEY, PURCHASE_FRICTION_KEY, words


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
    `respondent` block (guidance, option_rule, the escape, the fixed answers, the B2B variant), its
    founder `option_rule` and `guidance`, and the registry's `common` block. Wording the registry
    tells the model to use is never a leak. Its `lullaby` worked example is not read: it names
    Lullaby's mechanism."""
    if dimension is None:
        return set()
    founder = dimension.founder or {}
    texts = list(_strings(dimension.respondent or {}))
    texts += list(_strings([founder.get("option_rule"), founder.get("guidance"),
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


# ------------------------------------------------------------- calibration (founder-lists.md; calls 30-32, 85)

#: Call 44: a not-sure OPTION is one whose whole label, normalised, is one of these (keel-cloud 058's C3).
_NOT_SURE_LABELS = frozenset({"im not sure", "not sure", "dont know", "i dont know", "unsure",
                              "prefer not to say"})
_NOT_SURE_RE = re.compile(r"not sure|don't know|dont know|unsure", re.IGNORECASE)
#: C4's ceiling on a belief phrase, in characters (keel-cloud 062, founder decision 32).
_BELIEF_PHRASE_MAX = 120
#: L4 (keel-cloud 087 `ScreenResultApplier.ASKED_MAX_WORDS`): a drafted face is 1 to 20 words.
ASKED_MAX_WORDS = 20
_DIGITS = re.compile(r"\d+(?:[.,]\d+)?")


def _label_form(label) -> str:
    """keel-cloud 058's R2 comparison: case, apostrophes, whitespace and punctuation ignored."""
    text = re.sub(r"['\u2018\u2019]", "", str(label or "").lower())
    return re.sub(r"[\W_]+", " ", text).strip()


def _is_not_sure_label(label) -> bool:
    return _label_form(label) in _NOT_SURE_LABELS


@dataclass
class CalibrationScore:
    case_id: str
    entry_id: str
    subject: str                 # the vector, the part, or the asked dimension
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
    """Call 30: exactly one entry a dimension, in `order`. A doubled, a missing, a foreign or
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


def sources_of(context: dict | None) -> str:
    """`ScreenResultApplier.sourceText`: the job's `answers`, `interpretation` and `context`, the only numbers a
    draft may copy (L3, keel-cloud 087 call 10)."""
    context = context or {}
    return " ".join(json.dumps(context.get(k), ensure_ascii=False) for k in ("answers", "interpretation", "context")
                    if context.get(k) is not None)


#: keel-cloud 161 FR-1 (`ItemFrames.YOUR_WAY_OF`): the opening a drafted Current solution phrase must not carry.
_YOUR_WAY_OF = re.compile(r"^(?i:your\s+way\s+of)\s+")
#: keel-cloud 121 FR-3 (`ScreenResultApplier`'s `L5`, the founder's "Agree." of 2026-10-22, contract 31): the two
#: dimensions Keel may mark one item `suggested` on -- Purchase friction (a step it adds) and Compatibility (the condition
#: most likely to be missing, the Choose screen's pre-pick). Spec 093 FR-3: the harness said *Purchase friction only*.
#: Spec 112 FR-2 (keel-cloud 171 FR-2): and Adoption friction -- one one-time step the founder did not type, last, with
#: its `suggested_why`, outside the founder's 1 to 4 (`L1`) and never the default belief (`SavedList.tested()`).
SUGGESTED_ON = (PURCHASE_FRICTION_KEY, COMPATIBILITY_KEY, ADOPTION_KEY)


#: Spec 091 FR-1: the parts of a founder's Answer that name a difficulty each -- one a line, a bullet, a `;` or a `,`
#: apart (a serial list's last *and* / *or* too: *A, B and C* is three); a lone *and* with no comma list is one
#: difficulty (*settling the baby and finding the bottle*), as the Answer's own words leave it.
_BULLET = re.compile(r"^(?:[-*\u2022\u00b7]+|\d+[.)])\s*")
_SERIAL_LAST = re.compile(r"^(.+?)\s+(?:and|or)\s+(.+)$", re.I)
#: An Answer that names no other difficulty (*Nothing else*, *None*): the own item alone (keel-cloud 097 F9).
_NAMES_NONE = re.compile(r"^(?:nothing(?:\s+else)?|none|no|nope|n/?a|nobody)[.!]?$", re.I)


def named_difficulties(answer) -> list[str]:
    """Spec 091 FR-1 (`founder-lists.md`'s `rival_list` bullet): the other difficulties the founder's Importance Answer
    names, in its order -- what Keel's draft writes after the problem itself, adding none. A list Answer is one difficulty
    an element; a text one is split on lines, bullets, `;` and `,` (and a serial list's last *and* / *or*)."""
    if answer is None:
        return []
    texts = [str(a) for a in answer] if isinstance(answer, (list, tuple)) else [str(answer)]
    named = []
    for text in texts:
        chunks = [c for c in re.split(r"\s*[;\n\r]+\s*", text) if c.strip()]
        for chunk in chunks:
            parts = [_BULLET.sub("", p).strip() for p in re.split(r"\s*,\s*", chunk)]
            parts = [re.sub(r"^(?:and|or)\s+", "", p, flags=re.I).strip(" .") for p in parts if p.strip(" .")]
            if len(parts) > 1:
                last = _SERIAL_LAST.match(parts[-1])
                if last:
                    parts[-1:] = [last.group(1).strip(" ."), last.group(2).strip(" .")]
            named += [p for p in parts if p and not _NAMES_NONE.match(p)]
    return named


def _draft_count(dimension, answers: dict | None) -> tuple[int, int, str]:
    """`(low, high, why)`: how many items a DRAFT of this list dimension carries (spec 091 FR-1). Importance
    (`rival_list`) is held to the draft's own rule, never the save's: with no founder Answer for it the problem itself
    alone (one item), with one the problem itself and the N difficulties the Answer names (1 + N, at most
    `saves.max_items`) -- `saves.min_items` is the rule at Save (keel-cloud 087 / 152), once the founder has named the
    others, and is read where a saved list is checked (`corpus._check_list`), never here. Every other list keeps the
    registry's bounds, less a fixed first item code adds."""
    saves = dimension.saves
    fixed = 1 if saves.get("fixed_first") else 0
    if dimension.founder_control == "rival_list":
        answer = (answers or {}).get(dimension.key)
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            return 1, 1, "the problem itself alone, with no founder Answer"
        named = len(named_difficulties(answer))
        count = min(1 + named, int(saves.get("max_items") or 1 + named))
        return count, count, (f"the problem itself and the {count - 1} "
                              f"difficult{'y' if count - 1 == 1 else 'ies'} the founder's Answer names"
                              if named else "the problem itself alone: the founder's Answer names no other")
    low = max(0, int(saves.get("min_items") or 0) - fixed)
    high = int(saves.get("max_items") or 0) - fixed
    return low, high, ""


def list_faults(question: dict, dimension, *, sources: str = "", occasion: str | None = None,
                answers: dict | None = None) -> list:
    """`L1`-`L5` on one list dimension's draft (keel-cloud 087 `ScreenResultApplier.draft`, restated), and on a
    Compatibility or Adoption friction item's `asked` face the `K` rules (call 85). `answers` is the job's `answers`
    slot (`{}` on the seed-time job; the founder's Answer by key on a redraft): Importance's count reads it (spec 091)."""
    faults = []
    saves = dimension.saves
    draft = question.get("list")
    if not isinstance(draft, dict) or not isinstance(draft.get("items"), list):
        return [f"L1: {dimension.key} is a {dimension.founder_control}; write its draft list"]
    if question.get("options"):
        faults.append(f"L1: {dimension.key} is a list; it carries `list`, never options")
    fixed = 1 if saves.get("fixed_first") else 0
    low, high, why = _draft_count(dimension, answers)
    items = [i for i in draft["items"] if isinstance(i, dict)]
    # spec 112 FR-2 (keel-cloud 171 FR-2, `ScreenResultApplier.draft`): Adoption friction's one suggested step is
    # Keel's, outside the founder's 1 to 4 -- L1 counts the founder's efforts (a second suggested item is L5's)
    keels = min(1, sum(1 for i in items if i.get("suggested"))) if dimension.key == ADOPTION_KEY else 0
    counted = len(items) - keels
    if not low <= counted <= high:
        faults.append(f"L1: {dimension.key} takes {'exactly ' + str(low) if low == high else f'{low} to {high}'} "
                      f"item{'' if high == 1 else 's'}{' besides Nobody else' if fixed else ''}"
                      f"{' besides the one suggested step' if keels else ''}"
                      f"{f' ({why})' if why else ''}, and {counted} were written")
    phrase = str(draft.get("phrase") or "").strip()
    if saves.get("phrase") and not phrase:
        # spec 093 FR-3 (keel-cloud 161 T002): L1 in 161's words
        faults.append("L1: Current solution carries the phrase today's way is asked by, the act in the people's words "
                      "('checking for errors')")
    elif saves.get("phrase") and _YOUR_WAY_OF.match(phrase):
        # keel-cloud 161 T002: the phrase is the people's -- the bare act, never Keel's *your way of*
        faults.append(f"L1: {phrase!r} opens on 'your way of'; write the act alone, in the people's words "
                      f"({phrase[_YOUR_WAY_OF.match(phrase).end():].strip()!r})")
    suggested = 0
    allowed = set(_DIGITS.findall(sources))
    for i, item in enumerate(items):
        label = str(item.get("label") or "")
        count = words(label)
        if count == 0 or count > int(saves.get("max_words") or 9):
            faults.append(f"L2: item {i + 1} is 1 to {saves.get('max_words')} words; {label!r} is {count}")
        for text in (label, item.get("asked")):
            for number in _DIGITS.findall(str(text or "")):
                if number not in allowed:
                    faults.append(f"L3: {number!r} in item {i + 1} is a number the founder did not write")
        if _is_not_sure_label(label):
            faults.append(f"C3: {label!r} is a not-sure item; the chip is UI")
        if saves.get("asked"):
            asked = str(item.get("asked") or "")
            if not 1 <= words(asked) <= ASKED_MAX_WORDS or "?" in asked:
                faults.append(f"L4: item {i + 1} carries the stranger's clause, second person, 1 to "
                              f"{ASKED_MAX_WORDS} words and no question mark")
            else:
                faults += [f"{f} (item {i + 1})" for f in spoken_mod.face_faults(asked, label, dimension.key,
                                                                                   occasion, dimension.part)]
        if item.get("suggested"):
            suggested += 1
            if dimension.key not in SUGGESTED_ON or suggested > 1:
                # spec 093 FR-3: the cloud's L5 since keel-cloud 121 -- Purchase friction and Compatibility; spec 112
                # FR-2 (keel-cloud 171 FR-2): and Adoption friction's one one-time step, never elsewhere
                faults.append(f"L5: item {i + 1}: Keel suggests at most one item, on Purchase friction (a step it "
                              "adds), Compatibility (the condition most likely to be missing) and Adoption friction (a "
                              "one-time step the actor takes, last) only")
            elif dimension.key == ADOPTION_KEY and not str(item.get("suggested_why") or "").strip():
                # keel-cloud 171 FR-2: a breach, the strict reading's refusal (Compatibility's missing why stays a
                # note the harness does not count, call 124)
                faults.append(f"L5: item {i + 1}: the suggested step carries suggested_why -- what in the Answer or "
                              "the idea calls for it, in one sentence")
    hit = wording_mod.money(" ".join([str(draft.get("phrase") or "")] + [
        str(t) for i in items for t in (i.get("label"), i.get("asked")) if t]))
    if hit:
        faults.append(f"W9: {hit!r} is money; code renders every amount")
    return faults


def calibration_checks(question: dict, dimension, *, window=DEFAULT_WINDOW, sources: str = "",
                       occasion: str | None = None, answers: dict | None = None) -> list:
    """Every structural rule the founder-lists job is held to, for one dimension's entry; `[]` is valid.

    Prevalence owes its `event` clause (E1-E3) and its five fifths, each a label and a belief phrase (C2-C4);
    Frequency, Price and Existing sacrifice owe their key and note alone (C2) -- anything else is code's; every list
    dimension owes its draft (`list_faults`). A `question` the model writes anywhere is not read (keel-cloud 087:
    the list dimensions' questions are their Answer prompts, code's), so it is never a fault."""
    faults = []
    key = dimension.key
    if dimension.founder_list:
        return list_faults(question, dimension, sources=sources, occasion=occasion, answers=answers)
    if question.get("list"):
        faults.append(f"L1: {key} is no list; a draft is written only for the seven list dimensions")
    options = question.get("options")
    if dimension.founder_price or dimension.founder_cost or dimension.founder_numeric:
        if options:
            faults.append(f"C2: {len(options)} options on {dimension.name}; its input is code's")
        # `ScreenResultApplier.refuseMoney`: W9 reads the event and the options of every entry
        hit = wording_mod.money(" ".join(str(t) for t in [question.get("event")] + [
            v for o in options or [] if isinstance(o, dict) for v in (o.get("label"), o.get("belief_phrase"))]
            if t))
        if hit:
            faults.append(f"W9: {hit!r} is money; code renders every amount")
        return faults
    if key == GATE_KEY:
        event = question.get("event")
        if not event:
            faults.append("E2: Prevalence carries `event`, the clause of what happened; code writes the "
                          "question around it")
        else:
            fault = wording_mod.event_fault(event, window)
            if fault:
                faults.append(fault)
        hit = wording_mod.money(" ".join(str(t) for t in [event] + [
            v for o in options or [] if isinstance(o, dict) for v in (o.get("label"), o.get("belief_phrase"))] if t))
        if hit:
            faults.append(f"W9: {hit!r} is money; code renders every amount")
    fixed = dimension.fixed_codes or []
    if not isinstance(options, list) or len(options) != len(fixed):
        faults.append(f"C2: {len(options or [])} options; the registry fixes {len(fixed)} codes, joined by "
                      "position")
        return faults
    labels = [_label_form(o.get("label")) if isinstance(o, dict) else "" for o in options]
    twice = sorted({label for label in labels if label and labels.count(label) > 1})
    if twice:
        faults.append(f"label(s) repeated: {twice}")
    for option in options:
        if not isinstance(option, dict):
            faults.append(f"option {option!r} is not an object")
            continue
        label, phrase = option.get("label"), option.get("belief_phrase")
        stripped = (phrase or "").strip()
        if _is_not_sure_label(label):
            faults.append(f"C3: {label!r} is a not-sure option -- the chip is UI")
        if not stripped:
            faults.append(f"C4: option {label!r} carries no belief_phrase")
        elif len(stripped) > _BELIEF_PHRASE_MAX:
            faults.append(f"C4: option {label!r}: its belief_phrase is {len(stripped)} characters, longer than "
                          f"{_BELIEF_PHRASE_MAX}")
        elif _NOT_SURE_RE.search(stripped):
            faults.append(f"C4: option {label!r}: its belief_phrase carries a not-sure word")
    return faults


def written_texts(question: dict, dimension) -> list:
    """What a reader is shown of a calibration entry the model wrote: Prevalence's clause and its fifths, a list's
    phrase, labels and faces -- swept by `no_leak` on the PROBLEM job."""
    texts = [question.get("event")] if dimension.key == GATE_KEY else []
    for option in question.get("options") or []:
        if isinstance(option, dict):
            texts += [option.get("label"), option.get("belief_phrase")]
    draft = question.get("list") if isinstance(question.get("list"), dict) else {}
    texts.append(draft.get("phrase"))
    for item in draft.get("items") or []:
        if isinstance(item, dict):
            texts += [item.get("label"), item.get("asked")]
    return [t for t in texts if t]


def is_swept(dimension, *, founder: bool = True) -> bool:
    """Whether `no_leak` sweeps an entry at all: on the founder's side Prevalence and the lists (the model's words
    a reader is shown), on the respondent's side the gate alone (its clause is the one model-written respondent
    word, keel-cloud 088). Read off the registry, so a dry run counts the same denominator."""
    if founder:
        return dimension.key == GATE_KEY or dimension.founder_list
    return dimension.key == GATE_KEY


def score_calibration(case, entry, registry, result, *, judge=None,
                      failed: str | None = None) -> CalibrationScore:
    """One `CALIBRATION_QUESTIONS` case: coverage against the vector's answered slice (call 30), validity against
    the registry (calls 31, 85), and -- on the PROBLEM vector -- sweep A over every written word (call 45)."""
    vector = case.meta.get("vector") or case.subject
    slice_keys = [d.key for d in registry.answered_slice(vector, entry.b2b())]
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
    window = context_mod.window_of(entry)
    sent = case.payload.get("context") if getattr(case, "payload", None) else None
    sources, built = sources_of(sent), None
    if not sent or not sources:
        built = context_mod.build_calibration(entry, vector, registry)
        sources = sources or sources_of(built)
    # spec 091 FR-1: the job's `answers` slot (`{}` on the seed-time job) -- Importance's draft count reads it
    answers = (sent if isinstance(sent, dict) and sent else built or {}).get("answers") or {}
    for question in questions:
        key = question.get("key")
        if key not in slice_keys:
            continue
        dimension = registry.by_key(key)
        score.validity_of += 1
        checks = calibration_checks(question, dimension, window=window, sources=sources,
                                    occasion=entry.occasion(), answers=answers)
        if checks:
            score.faults.append({"key": key, "check": "option_validity", "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        if vector == "PROBLEM" and is_swept(dimension):
            score.leak_of += 1
            swept = sweep_a_calibration(written_texts(question, dimension), entry,
                                        exclude=registry_stems(registry, dimension))
            score.leak_hits += swept["hits"]
            score.leak_judged += swept["judged"]
            score.leak_hit_items += 1 if swept["hits"] else 0
            if swept["fault"]:
                score.faults.append({"key": key, "check": "no_leak", "evidence": swept["evidence"]})
            else:
                score.leak_clean += 1
    return score


# -------------------------------------------------------------- respondent (the gate's clause; calls 30-32, 83)

_NUMBER_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])")


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


def respondent_checks(item: dict, dimension, *, window=DEFAULT_WINDOW) -> list:
    """The gate's clause (keel-cloud 088 FR-002): `event` present, E1-E3 (`WindowFrame.fault`) and E4 (framed, the
    gate and the Frequency question at most 20 words each), W9 (no money). Every other item is code's whole: its
    key is all the model owes, and nothing else it writes is read."""
    if dimension.key != GATE_KEY:
        return []
    event = item.get("event")
    if not event:
        return ["E2: the gate carries `event`, the clause of what happened; code writes the question around it"]
    faults = []
    fault = wording_mod.event_fault(event, window)
    if fault:
        faults.append(fault)
    else:
        framed = wording_mod.framed_fault(event, window)
        if framed:
            faults.append(framed)
    hit = wording_mod.money(event)
    if hit:
        faults.append(f"W9: {hit!r} is money; code renders every amount")
    return faults


def score_respondent(case, entry, registry, plan, result, *, judge=None,
                     failed: str | None = None) -> RespondentScore:
    """One `RESPONDENT_QUESTIONS` case: coverage against the plan's part (call 30, R1: one `{key}` an item, in
    order); validity on the gate's clause alone (call 83); sweep A (the stranger has not been told the idea) and
    sweep B (the founder's own values) over that one clause, on Part 1 of the primary link."""
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
    for item in items:
        key = item.get("key")
        if key not in keys or key != GATE_KEY:
            continue
        dimension = registry.by_key(key)
        founder = entry.founder_calibration.get(key) or {}
        score.validity_of += 1
        checks = respondent_checks(item, dimension, window=window)
        if checks:
            score.faults.append({"key": key, "check": "option_validity", "evidence": "; ".join(checks)})
        else:
            score.validity_hit += 1
        if not (part == 1 and link == "PRIMARY"):
            continue
        stems = [item.get("event")]
        score.leak_of += 1
        swept = sweep_a(stems, entry, judge, exclude=registry_stems(registry, dimension))
        score.leak_hits += swept["hits"]
        score.leak_judged += swept["judged"]
        item_hit = bool(swept["hits"])
        if swept["fault"]:
            score.faults.append({"key": key, "check": "no_leak", "sweep": "A", "evidence": swept["evidence"]})
        else:
            score.leak_clean += 1
        score.leak_of += 1
        swept = sweep_b(stems, dimension, founder, window)
        score.leak_hits += swept["hits"]
        score.leak_hit_items += 1 if (item_hit or swept["hits"]) else 0
        if swept["fault"]:
            score.faults.append({"key": key, "check": "no_leak", "sweep": "B", "evidence": swept["evidence"]})
        else:
            score.leak_clean += 1
    return score


# ------------------------------------------------------------------------ ASKED (asked.md; call 84's K rules)

@dataclass
class AskedScore(CalibrationScore):
    dimension: str = ""


def score_asked(case, entry, registry, result, *, failed: str | None = None) -> AskedScore:
    """One `ASKED` case (keel-cloud 088 FR-003): coverage -- every index handed phrased once, no other (K1);
    validity -- each face's K2-K6 against its label (`spoken.face_faults`)."""
    key = case.meta.get("dimension")
    handed = {int(i["index"]): i.get("label") for i in case.meta.get("items") or [] if isinstance(i, dict)}
    score = AskedScore(case_id=case.case_id, entry_id=entry.id, subject=case.subject, run_index=case.run_index,
                       coverage_of=len(handed), failed=failed, dimension=key or "")
    items = (result or {}).get("items") if isinstance(result, dict) else None
    if failed or not isinstance(items, list):
        score.failed = failed or "the result carried no items list"
        return score
    faces = [i for i in items if isinstance(i, dict)]
    indices = [i.get("index") for i in faces]
    coverage = []
    foreign = [i for i in indices if i not in handed]
    twice = sorted({i for i in indices if isinstance(i, int) and indices.count(i) > 1})
    missing = sorted(set(handed) - {i for i in indices if isinstance(i, int)})
    if foreign:
        coverage.append(f"K1: {foreign} are not indices this job was handed ({sorted(handed)})")
    if twice:
        coverage.append(f"K1: {twice} phrased twice")
    if missing:
        coverage.append(f"K1: {missing} not phrased")
    score.coverage_passed = not coverage
    score.coverage_hit = len(handed) if score.coverage_passed else 0
    for fault in coverage:
        score.faults.append({"key": key, "check": "dimension_coverage", "evidence": fault})
    part = registry.by_key(key).part if key and registry.has(key) else 2
    seen = set()
    for face in faces:
        index = face.get("index")
        if index not in handed or index in seen:
            continue
        seen.add(index)
        score.validity_of += 1
        faults = spoken_mod.face_faults(face.get("asked"), handed[index], key, entry.occasion(), part)
        if faults:
            score.faults.append({"key": f"{key}[{index}]", "check": "option_validity",
                                 "evidence": "; ".join(faults)})
        else:
            score.validity_hit += 1
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
    """Coverage, validity and leak over one screen's cases (calibration, respondent or asked)."""
    return {
        "cases": len(scores),
        "coverage": {"hit": _sum(scores, "coverage_hit"), "of": _sum(scores, "coverage_of")},
        "validity": {"hit": _sum(scores, "validity_hit"), "of": _sum(scores, "validity_of")},
        "leak": {"clean": _sum(scores, "leak_clean"), "of": _sum(scores, "leak_of")},
    }


def totals(calibration_scores=(), respondent_scores=(), interpret_scores=(), compare_scores=(),
           *, asked_scores=(), spoken_score=None, facts_scores=(), overview_scores=(), errored: int = 0,
           refusals_by_rule: dict | None = None, shape_refusals: int = 0, schema_invalid: int = 0,
           refusals_measured: bool = False, refusals_shown: int = 0, judge_calls: int = 0,
           leak_hits: int | None = None, leak_judged: int | None = None, refusals_unmeasured_kinds=()) -> dict:
    """The run's own numbers (data-model §6), each summed over its own denominator."""
    calibration = _question_screen(calibration_scores)
    respondent = _question_screen(respondent_scores)
    asked = _question_screen(asked_scores)
    screens = (calibration, respondent, asked)
    every = list(calibration_scores) + list(respondent_scores) + list(asked_scores)

    coverage_of = sum(s["coverage"]["of"] for s in screens)
    validity_of = sum(s["validity"]["of"] for s in screens)
    leak_of = sum(s["leak"]["of"] for s in screens)
    hits = _sum(every, "leak_hits") if leak_hits is None else leak_hits
    judged = _sum(every, "leak_judged") if leak_judged is None else leak_judged
    hit_items = _sum(every, "leak_hit_items")

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

    facts_measured = bool(facts_scores) and all(s.measured for s in facts_scores)
    facts_checks = sum(s.checks for s in facts_scores if s.measured)
    facts_agreed = sum(s.agreed for s in facts_scores if s.measured)

    overview_measured = bool(overview_scores) and all(s.measured for s in overview_scores)
    overview_checks = sum(s.checks for s in overview_scores if s.measured)
    overview_agreed = sum(s.agreed for s in overview_scores if s.measured)

    spoken = spoken_score
    spoken_measured = bool(spoken is not None and spoken.measured)

    return {
        "calibration_cases": calibration["cases"],
        "calibration_coverage": calibration["coverage"],
        "calibration_validity": calibration["validity"],
        "calibration_leak": calibration["leak"],
        "respondent_cases": respondent["cases"],
        "respondent_coverage": respondent["coverage"],
        "respondent_validity": respondent["validity"],
        "respondent_leak": respondent["leak"],
        "asked_cases": asked["cases"],
        "asked_coverage": asked["coverage"],
        "asked_validity": asked["validity"],
        "dimension_coverage": _fraction(sum(s["coverage"]["hit"] for s in screens), coverage_of),
        "option_validity": _fraction(sum(s["validity"]["hit"] for s in screens), validity_of),
        "no_leak": _fraction(sum(s["leak"]["clean"] for s in screens), leak_of),
        "leak_hits": hits,
        "leak_judged": judged,
        "leak_hit_items": hit_items,
        # Items the judge decided over items with any hit -- one unit, reported, never marked.
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
        # Calls 79-81: the composed wording, marked once, at zero spend.
        "spoken_form": spoken.spoken_form if spoken_measured else None,
        "spoken_measured": spoken_measured,
        "spoken_units": spoken.units if spoken_measured else 0,
        "spoken_clean": spoken.clean if spoken_measured else 0,
        "spoken_known": len(spoken.known) if spoken_measured else 0,
        "spoken_unmeasured": None if spoken is None or spoken.measured else spoken.reason,
        # Call 82: keel-cloud's cards and pilot against this repository's reading, at zero spend.
        "brief_facts_checks": facts_checks,
        "brief_facts_agreed": facts_agreed,
        "brief_facts": _fraction(facts_agreed, facts_checks) if facts_measured else None,
        "brief_facts_measured": facts_measured,
        "brief_facts_reported_diffs": sum(len(s.reported_diffs) for s in facts_scores),
        "brief_facts_unmeasured": [{"entry": s.entry_id, "reason": s.reason}
                                   for s in facts_scores if not s.measured],
        # Call 117: the Overview a founder reads, from keel-cloud's facts against this repository's reading.
        "report_overview_checks": overview_checks,
        "report_overview_agreed": overview_agreed,
        "report_overview": _fraction(overview_agreed, overview_checks) if overview_measured else None,
        "report_overview_measured": overview_measured,
        "report_overview_unmeasured": [{"entry": s.entry_id, "reason": s.reason}
                                       for s in overview_scores if not s.measured],
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
