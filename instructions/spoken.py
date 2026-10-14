"""The spoken-form marks: every item of every corpus questionnaire, as keel-cloud composed it, held to the
spoken-question guidelines (spec 040 FR-005; `canon/designs/spoken-questions-guidelines.md` §2-§5, §8; keel-cloud
088 FR-001 / FR-005; judgement calls 79-81).

**What is checked, and against what.** The record is keel-cloud's (`instructions/cloud_corpus.py` reads
`build/spoken-corpus.txt`); the rules are the guidelines' -- the eval keeps no copy of the renderer
(`SpokenForm`, `ItemFrames`): it checks that what keel-cloud composed has the shape §2-§5 require. One unit
an item, one unit an `asked` face; a unit with any fault is not clean, and `spoken_form` is clean / units.

Per composed item (§2, §3, §4, §5):

- `S1` the stem is one question of at most **20** words -- **25** on Existing sacrifice and Relative advantage
  (keel-cloud 088 judgement call 12: their unchanged frames carry an unbounded context slot -- `{circumstance}`,
  `{occasion}` and the short name -- and four corpus items run 21 to 24 words; **the mark holds them at 25 until the
  founder decides** to shorten the frames or bound the slots);
- `S2` the anchor, where there is one, and the stem are the screen's question, and a part sets one anchor at most;
- `S3` at most **five** options (Price's ladder **six**); none on a number (Frequency, Existing sacrifice);
- `S4` every option at most **nine** words, and the founder-written ones (Importance's five, Current solution's
  five) at least **three** -- the three-word floor is not asked of the registry's fixed answers or the ladder
  (keel-cloud 088 judgement call 14: *Yes*, *No*, *Yes, easily* are the record);
- `S5` the options are **parallel and exclusive**: never a sentence (no closing `.`, `?` or `!`), no two the same
  once case and punctuation are set aside, and the escape never among them;
- `S6` **one escape, said last**: the guidelines' §5 escape for the dimension (none on Commitment), and the spoken
  block's last line *Or say {escape}.*;
- `S7` the count line is §3's *I'll read {N} options[; pick two].*, N the options said (four on Price's first step),
  *pick two* exactly on Importance; none on a number;
- `S8` the options line is §3's *a; b; ...; or z.* -- the options in the screen's order, said to the person
  (first person turned, keel-cloud 088 judgement call 5); Price's first step is *Under {low}; {the middle band};
  over {high}; or {the last}* (§4);
- `S9` the transform is the one §4 names where its dimension is -- Importance `one_then_one_more`, Relative
  advantage `yes_no_per_benefit`, Price `two_steps` -- and `none` everywhere else;
- `S10` Commitment's step is said to the stranger once: *would you {step}* carries no second *you*.

Per `asked` face of a corpus list (design §4, keel-cloud 088 FR-003's `K` rules, which hold the model's faces):
`K2` at most 20 words and the question it frames into at most 20; `K3` the second person; `K4` no digit the
label does not carry (no founder value reaches a stranger but the label's own); `K5` no product word on a part-1
item (vacuous for both list dimensions today, kept for the guidelines' sake); `K6` no question mark. The same
function marks the model's faces on the `ASKED` screen (`score.score_asked`).

**Five corpus items are known and named, not counted** (judgement call 81): revision 10 holds 06-repeatline's
Commitment step *introduce you to the practice's IT supplier* (composed: *would you introduce you to ...*, `S10`)
and four Compatibility faces with no *you* (`K3`) -- 01-countly's *did the invoice come with the delivery itself*,
which keel-cloud 088 saw, and three this mark found beside it: 02-compliancelog's *was every completion already
recorded in the learning system*, 03-lullaby's *was the room quiet enough for a phone to hear the cry* and
07-mulchrun's *was there room at the curb of that job for a mulch drop* (none of the four is the tested item).
keel-cloud 088 left them to this spec; the plan allows one corpus revision and 087 spent it, so they are the next
revision's items (spec 040 *Follow-ups*). `KNOWN` lists them; each is reported with its evidence and leaves the denominator.
A known fault that is no longer found is itself a fault -- the ledger must shrink with the corpus.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .registry import (ADOPTION_KEY, BENEFIT_KEY, COMMITMENT_KEY, COMPATIBILITY_KEY, CURRENT_SOLUTION_KEY,
                       FREQUENCY_KEY, IMPORTANCE_KEY, PRICE_KEY, SACRIFICE_KEY, words)

#: §2: a stem is at most 20 words; keel-cloud 088 call 12's two unchanged frames, 25.
STEM_MAX_WORDS = 20
LONG_FRAME_MAX_WORDS = 25
LONG_FRAMES = (SACRIFICE_KEY, BENEFIT_KEY)
#: §2: at most five options (Price six), each 3 to 9 words.
MAX_OPTIONS = 5
PRICE_MAX_OPTIONS = 6
OPTION_MAX_WORDS = 9
OPTION_MIN_WORDS = 3
#: The options the founder wrote, held to the three-word floor (call 80).
FOUNDER_WORDED = (IMPORTANCE_KEY, CURRENT_SOLUTION_KEY)
#: The items asked as a number: no options, no count line.
NUMERIC = (FREQUENCY_KEY, SACRIFICE_KEY)

#: §5, the one escape per dimension, by its label (the gate is never composed here; Commitment has none).
ESCAPES = {
    "problem.frequency": "I can't recall",
    "problem.importance": "None of these",
    "problem.current_solution_satisfaction": "Someone else does the checking",
    "solution.compatibility": "I can't tell",
    "solution.relative_advantage": "I can't tell",
    "solution.adoption_friction": "I can't tell",
    "commercial.existing_sacrifice": "I can't recall",
    "commercial.price": "I can't say",
    "commercial.ability_to_pay": "I can't recall one",
    "commercial.buyer_payer_alignment": "I can't recall one",
    "commercial.purchase_friction": "I can't recall",
    "commercial.commitment": None,
}

#: §4: the three transforms, by dimension; every other item is `none`.
TRANSFORMS = {IMPORTANCE_KEY: "one_then_one_more", BENEFIT_KEY: "yes_no_per_benefit", PRICE_KEY: "two_steps"}

#: The list dimensions whose items carry an `asked` face (design §4).
FACED = (COMPATIBILITY_KEY, ADOPTION_KEY)

#: Call 81: the corpus-r10 wording items the next corpus revision fixes -- `(entry, key, rule, item code or None)`.
KNOWN = (
    ("06-repeatline", COMMITMENT_KEY, "S10", None),
    ("01-countly", COMPATIBILITY_KEY, "K3", "invoice_came_with_it"),
    ("02-compliancelog", COMPATIBILITY_KEY, "K3", "completions_recorded"),
    ("03-lullaby", COMPATIBILITY_KEY, "K3", "quiet_enough"),
    ("07-mulchrun", COMPATIBILITY_KEY, "K3", "room_at_curb"),
)

_NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
_COUNT_LINE = re.compile(r"^I'll read (two|three|four|five|six) options(; pick two)?\.$")
_YOU = re.compile(r"\b(you|your|yours|yourself|you'd|you're|you've|you'll)\b", re.IGNORECASE)
_DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
_FIRST_PERSON = {"i": "you", "me": "you", "we": "you", "us": "you", "i'm": "you're", "we're": "you're",
                 "i'd": "you'd", "we'd": "you'd", "i've": "you've", "we've": "you've", "i'll": "you'll",
                 "we'll": "you'll", "my": "your", "our": "your", "mine": "yours", "ours": "yours",
                 "myself": "yourself"}
_FIRST_PERSON_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(w) for w in _FIRST_PERSON), key=len,
                                                       reverse=True)) + r")\b", re.IGNORECASE)
#: keel-cloud 058's `Vocabulary.PRODUCT_WORDS` (call 45), for `K5`.
PRODUCT_WORDS = ("app", "apps", "platform", "dashboard", "portal", "plugin", "api", "saas", "website",
                 "algorithm", "device", "automate", "automates", "automated", "automating", "automation",
                 "integrate", "integrates", "integrated", "integration", "integrations", "sync", "syncs",
                 "synced", "syncing")
_PRODUCT = re.compile(r"(?<![^\W_])(" + "|".join(PRODUCT_WORDS) + r")(?![^\W_])", re.IGNORECASE)


def said(text) -> str:
    """A label as it is said to the person, for comparing (088 call 5): the first person turned, a semicolon a
    comma, case and the closing stop set aside -- "No, I decided on my own" and "no, you decided on your own" agree."""
    text = str(text or "").strip().rstrip(".").replace(";", ",")
    text = _FIRST_PERSON_RE.sub(lambda m: m.group(0) if m.group(0) == "US" else _FIRST_PERSON[m.group(0).lower()],
                                text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _form(label) -> str:
    return re.sub(r"[\W_]+", " ", re.sub(r"['‘’]", "", str(label or "").lower())).strip()


def _is_sentence(label) -> bool:
    return str(label or "").rstrip().endswith((".", "?", "!"))


def stem_limit(key: str) -> int:
    return LONG_FRAME_MAX_WORDS if key in LONG_FRAMES else STEM_MAX_WORDS


def item_faults(item) -> list:
    """Every `S` fault of one composed item (a `cloud_corpus.ComposedItem`), `[]` when it keeps the record."""
    faults = []
    key = item.key
    # S1: one question, at most 20 words (25 on the two unchanged frames, call 79).
    most = stem_limit(key)
    if words(item.stem) > most:
        faults.append(f"S1: the stem {item.stem!r} is {words(item.stem)} words; at most {most}")
    if not item.stem.strip().endswith("?") and key != ADOPTION_KEY:
        faults.append(f"S1: the stem {item.stem!r} is not a question")
    # S2: the anchor and the stem are the screen's question.
    joined = ((item.anchor + " ") if item.anchor else "") + item.stem
    if joined != item.question:
        faults.append(f"S2: the anchor and stem read {joined!r}; the screen asks {item.question!r}")
    # S3 / S4 / S5: the options.
    options = list(item.options)
    if key in NUMERIC:
        if options:
            faults.append(f"S3: {len(options)} options on a number")
    else:
        most = PRICE_MAX_OPTIONS if key == PRICE_KEY else MAX_OPTIONS
        if not options or len(options) > most:
            faults.append(f"S3: {len(options)} options; at most {most}")
    for label in options:
        n = words(label)
        if n > OPTION_MAX_WORDS:
            faults.append(f"S4: the option {label!r} is {n} words; at most {OPTION_MAX_WORDS}")
        if key in FOUNDER_WORDED and n < OPTION_MIN_WORDS:
            faults.append(f"S4: the option {label!r} is {n} words; a founder's option is at least "
                          f"{OPTION_MIN_WORDS}")
        if _is_sentence(label):
            faults.append(f"S5: the option {label!r} is a sentence; an option is a phrase")
    forms = [_form(label) for label in options]
    twice = sorted({f for f in forms if forms.count(f) > 1})
    if twice:
        faults.append(f"S5: the options {twice} are not exclusive (said twice)")
    # S6: one escape, the guidelines' own, said last.
    want = ESCAPES.get(key, "absent")
    if want == "absent":
        faults.append(f"S6: {key} has no escape in the guidelines' §5 table")
    elif item.escape != want:
        faults.append(f"S6: the escape is {item.escape!r}; §5's is {want!r}")
    if item.escape is not None:
        if _form(item.escape) in forms:
            faults.append(f"S6: the escape {item.escape!r} is also an option")
        match = re.match(r"^Or say (.+)\.$", item.escape_line or "")
        if not match or said(match.group(1)) != said(item.escape):
            faults.append(f"S6: the escape line is {item.escape_line!r}; §3 says 'Or say {{escape}}.' last")
    elif item.escape_line is not None:
        faults.append(f"S6: an escape line {item.escape_line!r} on an item with no escape")
    # S7 / S8: the template's count and options lines.
    transform = TRANSFORMS.get(key, "none")
    if key in NUMERIC:
        if item.count_line is not None:
            faults.append(f"S7: a count line {item.count_line!r} on a number")
        if not item.options_line.strip().endswith("."):
            faults.append(f"S8: the answer line {item.options_line!r} is not one sentence")
    else:
        spoken = _first_step(options) if key == PRICE_KEY else options
        n = len(spoken)
        count = _COUNT_LINE.match(item.count_line or "")
        if not count or count.group(1) != (_NUMBER_WORDS[n] if n < len(_NUMBER_WORDS) else str(n)) \
                or bool(count.group(2)) != (key == IMPORTANCE_KEY):
            faults.append(f"S7: the count line is {item.count_line!r}; §3 says 'I'll read "
                          f"{_NUMBER_WORDS[n] if n < len(_NUMBER_WORDS) else n} options"
                          f"{'; pick two' if key == IMPORTANCE_KEY else ''}.'")
        line = item.options_line or ""
        pieces = line[:-1].split("; ") if line.endswith(".") else []
        if pieces and len(pieces) > 1 and pieces[-1].startswith("or "):
            pieces[-1] = pieces[-1][3:]
        else:
            pieces = None
        if pieces is None or [said(p) for p in pieces] != [said(o) for o in spoken]:
            faults.append(f"S8: the options line is {line!r}; §3 says the {n} options in order, '...; or z.'")
    # S9: the transform.
    if item.transform != transform:
        faults.append(f"S9: the transform is {item.transform!r}; §4 names {transform!r} for {key}")
    # S10: Commitment's step said once to the stranger.
    if key == COMMITMENT_KEY:
        step = item.stem.split("would you ", 1)[1] if "would you " in item.stem else ""
        if re.search(r"\byou\b", step, re.IGNORECASE):
            faults.append(f"S10: the step reads {item.stem!r}; 'would you {{step}}' says 'you' twice -- the step "
                          "is the stranger's, in base form, with no second 'you'")
    return faults


def _first_step(options: list) -> list:
    """§4, Price's first step: under the middle band, the middle band, over it, or the last."""
    if len(options) != 6 or " to " not in options[2]:
        return options
    low, high = options[2].split(" to ", 1)
    return [f"Under {low}", options[2], f"Over {high}", options[5]]


def framed(key: str, occasion: str | None, asked: str) -> str:
    """The question a face is framed into (design §5.1), to count its words: *On your last {occasion},
    {asked}?* and *{Asked}. Would you do that, or not?*."""
    clause = str(asked or "").strip().rstrip("?.").strip()
    if key == ADOPTION_KEY:
        return (clause[:1].upper() + clause[1:]) + ". Would you do that, or not?"
    return f"On your last {occasion or 'time'}, {clause}?"


def face_faults(asked: str, label: str, key: str, occasion: str | None, part: int = 2) -> list:
    """Every `K2`-`K6` fault of one `asked` face against its label (keel-cloud 088 FR-003, restated)."""
    faults = []
    asked = str(asked or "").strip()
    if not asked:
        return ["K2: the face is empty"]
    if words(asked) > STEM_MAX_WORDS:
        faults.append(f"K2: {asked!r} is {words(asked)} words; a clause is at most {STEM_MAX_WORDS}")
    question = framed(key, occasion, asked)
    if words(question) > STEM_MAX_WORDS:
        faults.append(f"K2: framed, it reads {question!r}, {words(question)} words; at most {STEM_MAX_WORDS}")
    if not _YOU.search(asked):
        faults.append(f"K3: {asked!r} is not said to the stranger (no you / your)")
    for digit in _DIGITS.findall(asked):
        if digit not in str(label or ""):
            faults.append(f"K4: {digit!r} is a number the label {label!r} does not carry (no founder value)")
    if part == 1:
        product = _PRODUCT.search(asked)
        if product:
            faults.append(f"K5: {product.group(1)!r} names a product in part 1")
    if "?" in asked:
        faults.append(f"K6: {asked!r} carries a question mark; the frame adds it")
    return faults


@dataclass
class SpokenScore:
    """`spoken_form` over a corpus: one unit an item and one a face, the known items apart."""

    units: int = 0
    clean: int = 0
    faults: list = field(default_factory=list)      # [{entry, key, unit, evidence}]
    known: list = field(default_factory=list)       # the call-81 items, found
    missing_known: list = field(default_factory=list)
    measured: bool = False
    reason: str | None = None
    by_entry: dict = field(default_factory=dict)    # entry -> {units, clean}

    @property
    def spoken_form(self):
        return (self.clean / self.units) if (self.measured and self.units) else None


def _known(entry_id: str, key: str, rule: str, code) -> bool:
    return (entry_id, key, rule, code) in KNOWN


def score(cloud, corpus, *, entry_ids=None) -> SpokenScore:
    """Every composed item and every corpus `asked` face of the entries asked for (all by default)."""
    result = SpokenScore(measured=True)
    found_known = set()
    for entry in corpus.entries:
        if entry_ids is not None and entry.id not in entry_ids:
            continue
        row = result.by_entry.setdefault(entry.id, {"units": 0, "clean": 0})
        items = cloud.items_of(entry.id)
        if not items:
            # One unit, never clean: an entry keel-cloud composed nothing for is a fault, not an unmeasured mark.
            result.units += 1
            row["units"] += 1
            result.faults.append({"entry": entry.id, "key": None, "unit": "items",
                                  "evidence": "keel-cloud composed no item for this entry"})
            continue
        anchors = {}
        for item in items:
            if item.anchor:
                anchors[item.part] = anchors.get(item.part, 0) + 1
        for item in items:
            faults = item_faults(item)
            if anchors.get(item.part, 0) > 1 and item.anchor:
                faults.append(f"S2: part {item.part} sets {anchors[item.part]} anchors; one per part")
            unit_known = [f for f in faults if _known(entry.id, item.key, f.split(":")[0], None)]
            for f in unit_known:
                found_known.add((entry.id, item.key, f.split(":")[0], None))
                result.known.append({"entry": entry.id, "key": item.key, "unit": "item", "evidence": f})
            rest = [f for f in faults if f not in unit_known]
            if unit_known and not rest:
                continue                                         # call 81: named, out of the denominator
            result.units += 1
            row["units"] += 1
            if rest:
                result.faults.append({"entry": entry.id, "key": item.key, "unit": "item",
                                      "evidence": "; ".join(rest)})
            else:
                result.clean += 1
                row["clean"] += 1
        for key in FACED:
            saved = entry.founder_list(key)
            for item in (saved or {}).get("items") or []:
                if not item.get("asked"):
                    continue
                faults = face_faults(item["asked"], item.get("label"), key, entry.occasion())
                unit_known = [f for f in faults if _known(entry.id, key, f.split(":")[0], item.get("code"))]
                for f in unit_known:
                    found_known.add((entry.id, key, f.split(":")[0], item.get("code")))
                    result.known.append({"entry": entry.id, "key": key, "unit": f"asked {item.get('code')}",
                                         "evidence": f})
                rest = [f for f in faults if f not in unit_known]
                if unit_known and not rest:
                    continue
                result.units += 1
                row["units"] += 1
                if rest:
                    result.faults.append({"entry": entry.id, "key": key, "unit": f"asked {item.get('code')}",
                                          "evidence": "; ".join(rest)})
                else:
                    result.clean += 1
                    row["clean"] += 1
    for known in KNOWN:
        if (entry_ids is None or known[0] in entry_ids) and corpus.by_id(known[0]) is not None \
                and known not in found_known:
            result.missing_known.append(known)
            result.units += 1
            result.faults.append({"entry": known[0], "key": known[1], "unit": "known",
                                  "evidence": f"call 81 names {known[2]} here and it is no longer found -- strike "
                                              "it from spoken.KNOWN"})
    return result


def unmeasured(reason: str) -> SpokenScore:
    return SpokenScore(measured=False, reason=reason)
