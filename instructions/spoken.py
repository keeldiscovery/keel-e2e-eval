"""The spoken-form marks: every item of every corpus questionnaire, as keel-cloud composed it, held to the
spoken-question guidelines (spec 040 FR-005; `canon/designs/spoken-questions-guidelines.md` §2-§5, §8; keel-cloud
088 FR-001 / FR-005; judgement calls 79-81).

**What is checked, and against what.** The record is keel-cloud's (`instructions/cloud_corpus.py` reads
`build/spoken-corpus.txt`); the rules are the guidelines' -- the eval keeps no copy of the renderer
(`SpokenForm`, `ItemFrames`): it checks that what keel-cloud composed has the shape §2-§5 require. One unit
an item, one unit an `asked` face; a unit with any fault is not clean, and `spoken_form` is clean / units.

Per composed item (§2, §3, §4, §5):

- `S1` the stem is one question of at most **20** words, every dimension's (keel-cloud 091 FR-E shortened the
  two frames 088 judgement call 12 had left at 21-24 -- Relative advantage *On your last {occasion}, would {name}
  have made things better, or not?*, Existing sacrifice stepping down until it fits -- so spec 042 call 111 drops
  spec 040's 25-word allowance);
- `S2` the anchor, where there is one, and the stem are the screen's question, and a part sets one anchor at most;
- `S3` at most **five** options (Price's ladder **six**); none on a number (Frequency, Existing sacrifice);
- `S4` every option at most **nine** words, Commitment's counted whole (*Yes, I'd* and the step together are the
  option: keel-cloud 129 FR-15 took `SpokenForm.STEP_OPTION_MAX_WORDS` from 118's eleven to nine and cuts the step to
  its share; spec 068 FR-2),
  and the founder-written ones (Importance's five, Current solution's five) at least **three** -- the three-word floor
  is not asked of the registry's fixed answers or the ladder (keel-cloud 088 judgement call 14: *Yes*, *No*, *Yes,
  easily* are the record);
- `S5` the options are **parallel and exclusive**: never a sentence (no closing `.`, `?` or `!`), no two the same
  once case and punctuation are set aside, and the escape never among them;
- `S6` **one escape, said last**: the escape the item names -- the registry's for the dimension, except where the side
  is served apart (Ability to pay on a consumer link is the budget item, *I can't say*: spec 068 FR-2), and none on
  Commitment (129 FR-9's escape is open) -- and the spoken block's last line *Or say {escape}.* with the escape the item
  is **served** with (spec 065 FR-1: the registry's, read by the side it is served by -- keel-cloud
  `CommercialChain.side`);
- `S7` the count line is §3's *I'll read {N} options.*, N the served options said (four on Price's first step); none on
  a number. *; pick two* is never said since keel-cloud 158 (spec 089 FR-3): Importance asks *which one of these*, then
  *And one more?* (the transform stays `one_then_one_more`), so a count line that adds it is a fault;
- `S8` the options line is §3's *a; b; ...; or z.* -- the options in the screen's order, said to the person
  (first person turned, keel-cloud 088 judgement call 5); Price's first step is *Under {low}; {the middle band};
  over {high}; or {the last}* (§4);
- `S9` the transform is the one §4 names where its dimension is -- Importance `one_then_one_more`, Price `two_steps`
  -- and `none` everywhere else (Relative advantage's `yes_no_per_benefit` retired with keel-cloud 159: the scale is one
  question and four short options);
- `S10` Commitment's step is said to the stranger once: *would you {step}* carries no second *you*.

Per `asked` face of a corpus list (design §4, keel-cloud 088 FR-003's `K` rules, which hold the model's faces):
`K2` at most 20 words and the question it frames into at most 20 (Adoption friction's frame keel-cloud's own since
spec 093 FR-4); `K3` the second person (on Adoption friction, the clause as framed: spec 093 FR-5); `K4` no digit the
label does not carry (no founder value reaches a stranger but the label's own); `K5` no product word on a part-1
item (vacuous for both list dimensions today, kept for the guidelines' sake); `K6` no question mark. The same
function marks the model's faces on the `ASKED` screen (`score.score_asked`).

**No corpus item is known apart any more** (spec 042 call 112). Spec 040's call 81 named five revision-10 items
(06-repeatline's Commitment step *introduce you to ...*, `S10`, and four Compatibility faces with no *you*, `K3`) and
left them out of the denominator; keel-cloud 091's corpus revision 11 rewrote all five (DRIFT #77, closed), so `KNOWN`
is empty, every item and face is counted, and the ledger's own fault -- a known item no longer found -- has nothing
left to fire on. The machinery stays for the day a revision is again known to be short of a rule.

**The record reads the registry, not a table** (spec 065 FR-1, FR-2). Until spec 065 the escapes were a fixed copy
of the guidelines' §5 and the labels an option list was read back with were the eval's fixture registry's, so when
keel-cloud changed them on purpose the guard counted 34 faults on a record that had followed its own registry. Five
changes, all on purpose, all keel-cloud's (registry revision 13 at keel-cloud-docs master):

1. Current solution's escape reads *Someone else did it*, not *Someone else does the checking* (123 FR-3);
2. Existing sacrifice's registry escape is *I can't recall* since keel-cloud 170 (spec 110 FR-2; the value box's chips
   read *None* and *I can't recall*, the wire's codes `NOTHING` / `DONT_KNOW` and the stored `dont_know` unmoved). From
   115 / 123's escapes (registry decision 24's value box) to 169 it was *I don't know*, while a cost stated before the
   chain, every golden entry's, was **served** spec 077's cost total and its *I can't recall* (`CommercialChain.side`,
   mirrored by `served_escape` as `OFF_CHAIN_COST_ESCAPE`); so on and off the chain the item now names and says one
   escape, *I can't recall*, and the spoken line is *Or say you can't recall.*;
3. Compatibility's four are drafted to the condition's verb: an ability reads *Yes, easily · Yes, mostly · Only
   sometimes · No* on the registry's four codes (123 FR-8, `ABILITY_ANSWERS`), a permission keeps the registry's;
4. Buyer and payer's four are the registry's revised four (*Someone else had to agree instead* · *No, someone else
   decided for me*, 123 FR-5);
5. Commitment's options are written from the founder's step -- *Yes, I'd {step}*, *Yes, after {smaller step} first*
   only when the list carries one, *Probably not*, *No* -- so a free step is three bands, not four (118 FR-1 / FR-2);
   and since they carry the step whole they are held to eleven words, not nine (118, the guidelines' §10 amendment:
   03-lullaby's *Yes, I'd allow it to use the microphone at night* is ten -- read back whole for the first time here,
   it had been split at its comma and never measured).

Spec 067 (keel-cloud 128, corpus revision 15) adds three more, all keel-cloud's code and none a registry change: a
Compatibility condition read as a **fact** is answered *Yes · Mostly · Partly · No* on the same four codes (128 FR-13b,
`FACT_ANSWERS`); Purchase friction is asked of **this** purchase, *Yes, and it would take a long time · Yes, but it would
be quick · No, it wouldn't be needed* (128 FR-12, `PURCHASE_ANSWERS`); Buyer and payer's four are distinct answers, the
consumer's past ones and the decision-maker's at the founder's price (128 FR-5, FR-18, FR-19, `buyer_answers`).

So the escape an item names is the registry's (`registry_escape`), the escape it says is the one it is served with
(`served_escape`), and the labels an option list is read back with are the ones the registry says the item may carry
(`served_labels`, used by `cloud_corpus.known_labels_for`). The rules keep their meaning: a stem over 20 words, a
missing *or*, a count line that disagrees with the options drawn are still faults; a registry change moves the record
and the test together. `KNOWN` stays empty.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .registry import (ABILITY_KEY, ADOPTION_KEY, BENEFIT_KEY, BUYER_KEY, COMMITMENT_KEY, COMPATIBILITY_KEY,
                       PURCHASE_FRICTION_KEY,
                       CURRENT_SOLUTION_KEY, FREQUENCY_KEY, IMPORTANCE_KEY, PRICE_KEY, SACRIFICE_KEY,
                       VALUE_BOX_CONTROL, words)

#: §2: a stem is at most 20 words, every dimension's (keel-cloud 091 FR-E; spec 042 call 111).
STEM_MAX_WORDS = 20
#: §2: at most five options (Price six), each 3 to 9 words.
MAX_OPTIONS = 5
PRICE_MAX_OPTIONS = 6
OPTION_MAX_WORDS = 9
#: keel-cloud 129 FR-15 (`SpokenForm.STEP_OPTION_MAX_WORDS`, 118's eleven): Commitment's option is *Yes, I'd* and the
#: step together, counted whole at nine like every other option (spec 068 FR-2).
STEP_OPTION_MAX_WORDS = 9
OPTION_MIN_WORDS = 3
#: The options the founder wrote, held to the three-word floor (call 80).
FOUNDER_WORDED = (IMPORTANCE_KEY, CURRENT_SOLUTION_KEY)
#: The items asked as a number: no options, no count line.
NUMERIC = (FREQUENCY_KEY, SACRIFICE_KEY)

#: keel-cloud `CommercialChain.side`: the escape an item is served with where its side is not the registry's row --
#: Existing sacrifice on a cost stated before the chain keeps spec 077's cost total (registry decision 24; since
#: keel-cloud 170 the registry's row says the same *I can't recall*, spec 110 FR-2), Ability to pay on a consumer link
#: is the consumer budget item.
OFF_CHAIN_COST_ESCAPE = "I can't recall"
CONSUMER_BUDGET_ESCAPE = "I can't say"

#: keel-cloud 123 FR-8 (`ItemFrames.ABILITY_LABELS`, the registry's Compatibility guidance): the four answers to a
#: condition of ability, on the registry's own four codes; a condition of permission keeps the registry's labels.
ABILITY_ANSWERS = {"yes_easily": "Yes, easily", "yes_with_steps": "Yes, mostly", "only_with_help": "Only sometimes",
                   "no": "No"}


#: keel-cloud 128 FR-13b (`ItemFrames.FACT_LABELS`, spec 067): a Compatibility condition read as a fact is answered as
#: a fact, on the same four codes.
FACT_ANSWERS = {"yes_easily": "Yes", "yes_with_steps": "Mostly", "only_with_help": "Partly", "no": "No"}
#: keel-cloud 128 FR-12 (`ItemFrames.PURCHASE_LABELS`): Purchase friction's three, reread for this purchase.
PURCHASE_ANSWERS = {"yes_long": "Yes, and it would take a long time", "yes_quick": "Yes, but it would be quick",
                    "not_needed": "No, it wouldn't be needed"}


def buyer_answers(role: str | None) -> list:
    """keel-cloud 128 FR-5 / FR-18 / FR-19 (`ItemFrames.buyerPayerLabel`, `buyerPayerAtPriceLabel`): Buyer and payer's
    labels beside the registry's -- the consumer link's past answers and the decision-maker's for this purchase at the
    founder's price -- with the role the founder named (`None`: *Nobody else* tested)."""
    # keel-cloud 145 FR-2 (spec 076 FR-2): the role with its *the* (`BeliefSentence.theRole`) -- an acronym takes it,
    # *Yes, the CEO had to agree*, never *Yes, CEO had to agree*
    from instructions.chain import the_role                           # noqa: PLC0415
    past_who = None if role is None else re.sub(r"^their ", "my ", the_role(role))
    who = None if role is None else the_role(role)
    return ["Yes, someone else had to agree" if past_who is None else f"Yes, {past_who} had to agree",
            "Yes, several people had to agree",
            "No, someone else would have to agree" if who is None else f"No, {who} would have to agree",
            "Yes, I could sign off on it myself", "No, several people would have to agree",
            # keel-cloud 131 FR-13: *No, someone else would have to agree instead* overlapped a named party and is
            # served no more -- *several people* is the third option either way
            "No, it would be someone else's decision"]


def _lower(label: str) -> str:
    """`BeliefSentence.lower`: the first letter lowered unless the second is a capital (an acronym)."""
    label = str(label or "")
    if len(label) > 1 and label[1].isupper():
        return label
    return label[:1].lower() + label[1:]


def registry_escape(registry, key: str):
    """The escape label the registry's row names for `key` (`None` where the row has none); `KeyError` off the
    registry."""
    escape = registry.by_key(key).escape
    return escape.get("label") if escape else None


def item_escape(registry, key: str, entry=None):
    """The escape an item **names** (spec 068 FR-2, keel-cloud 129's owed list): the registry's row, except Ability to
    pay on a consumer link, which is served as the consumer budget item with its own escape, *I can't say* (the guard
    called Issen's clean run RED on the registry's *I can't recall one*). Commitment's is none (129 FR-9's escape open).
    Existing sacrifice off the chain names the registry's and says spec 077's (`served_escape`), as the record does."""
    dimension = registry.by_key(key)
    if entry is not None and key == ABILITY_KEY and not entry.b2b():
        return CONSUMER_BUDGET_ESCAPE
    escape = dimension.escape
    return escape.get("label") if escape else None


def served_escape(registry, key: str, entry=None):
    """The escape the item is served (and said) with: the registry's, read by the side keel-cloud serves it by
    (`CommercialChain.side`)."""
    dimension = registry.by_key(key)
    if entry is not None:
        if key == SACRIFICE_KEY and dimension.respondent_control == VALUE_BOX_CONTROL and not entry.chain():
            return OFF_CHAIN_COST_ESCAPE
        if key == ABILITY_KEY and not entry.b2b():
            return CONSUMER_BUDGET_ESCAPE
    return registry_escape(registry, key)


def served_labels(registry, key: str, entry=None) -> list:
    """Every label the registry says `key`'s item may be served with: its fixed answers; Compatibility's ability four
    beside them (123 FR-8); Commitment's options written from the entry's step (118 FR-1)."""
    if registry is None or not registry.has(key):
        return []
    dimension = registry.by_key(key)
    labels = [a.get("label") for a in dimension.fixed_answers]
    if key == COMPATIBILITY_KEY:
        fixed = list(labels)
        labels += [ABILITY_ANSWERS.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)]
        labels += [FACT_ANSWERS.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)]
    if key == PURCHASE_FRICTION_KEY:
        labels += list(PURCHASE_ANSWERS.values())
    if key == BUYER_KEY:
        roles = [i.get("label") for i in (((entry.founder_list(key) or {}).get("items") or []) if entry else [])
                 if i.get("label") and i.get("code") != "nobody_else"]
        for role in roles + [None]:
            labels += buyer_answers(role)
    if key == COMMITMENT_KEY and entry is not None:
        steps = [i.get("label") for i in ((entry.founder_list(key) or {}).get("items") or []) if i.get("label")]
        if steps:
            labels.append(first_yes(steps[0]))
        if len(steps) > 1:
            labels.append(second_yes(steps[1]))
    return labels


_PREPOSITIONS = r"(?:with|on|at|for|in|from|after|before|by|during|over|across|within)"
_TRAILING = re.compile(r"^(.+?)\s+" + _PREPOSITIONS + r"\s+\S.*$")
_LAST_TRAILING = re.compile(r"^(.+)\s+" + _PREPOSITIONS + r"\s+\S.*$")


def cut_to_fit(step: str, most: int) -> str:
    """keel-cloud 129 FR-15 (`ItemFrames.cutToFit`): a step cut to `most` words by its trailing phrases, the last one
    opening on a preposition first (*allow it to use the microphone at night* -> *allow it to use the microphone*); a
    step that fits, or one with no such phrase left, as it is."""
    text = str(step or "").strip()
    while words(text) > most:
        last = _LAST_TRAILING.fullmatch(text)
        if not last or words(last.group(1)) < 2 or not _TRAILING.fullmatch(text):
            break
        text = last.group(1).strip()
    return text


def first_yes(step: str) -> str:
    """`ItemFrames.firstYes`: *Yes, I'd {step}*, the step cut to its share of the option's nine (129 FR-15)."""
    return "Yes, I'd " + cut_to_fit(_lower(str(step).strip()), OPTION_MAX_WORDS - 2)


def second_yes(smaller_step: str) -> str:
    """`ItemFrames.secondYes`: *Yes, after {smaller step} first*, cut to fit nine, never *first first* (129 FR-9,
    FR-15)."""
    said_step = _lower(str(smaller_step).strip())
    first = re.search(r"\bfirst$", said_step, re.IGNORECASE) is not None
    step = cut_to_fit(said_step, OPTION_MAX_WORDS - (2 if first else 3))
    return "Yes, after " + step + ("" if re.search(r"\bfirst$", step, re.IGNORECASE) else " first")


#: §4: the three transforms, by dimension; every other item is `none`.
#: Spec 089 FR-4 (keel-cloud 159 T005): Relative advantage's `yes_no_per_benefit` is retired -- one question and the
#: scale's four short options, no transform.
TRANSFORMS = {IMPORTANCE_KEY: "one_then_one_more", PRICE_KEY: "two_steps"}

#: The list dimensions whose items carry an `asked` face (design §4).
FACED = (COMPATIBILITY_KEY, ADOPTION_KEY)

#: Call 81's ledger of corpus wording items known to break a rule -- `(entry, key, rule, item code or None)`. Empty at
#: revision 11 (call 112: keel-cloud 091 fixed all five revision-10 items, DRIFT #77).
KNOWN: tuple = ()

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
    """Every stem's limit, 20 (call 111; the key is kept for the caller's sake)."""
    return STEM_MAX_WORDS


def item_faults(item, registry, entry=None) -> list:
    """Every `S` fault of one composed item (a `cloud_corpus.ComposedItem`) against the registry it was served from
    (and its corpus entry, for the side an item is served by), `[]` when it keeps the record."""
    faults = []
    key = item.key
    # S1: one question, at most 20 words (call 111).
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
    longest = STEP_OPTION_MAX_WORDS if key == COMMITMENT_KEY else OPTION_MAX_WORDS
    for label in options:
        n = words(label)
        if n > longest:
            faults.append(f"S4: the option {label!r} is {n} words; at most {longest}")
        if key in FOUNDER_WORDED and n < OPTION_MIN_WORDS:
            faults.append(f"S4: the option {label!r} is {n} words; a founder's option is at least "
                          f"{OPTION_MIN_WORDS}")
        if _is_sentence(label):
            faults.append(f"S5: the option {label!r} is a sentence; an option is a phrase")
    forms = [_form(label) for label in options]
    twice = sorted({f for f in forms if forms.count(f) > 1})
    if twice:
        faults.append(f"S5: the options {twice} are not exclusive (said twice)")
    # S6: one escape, the registry's, said last -- the one the item is served with (spec 065 FR-1).
    if registry is None or not registry.has(key):
        faults.append(f"S6: {key} is not in the registry, so it has no escape of record")
    else:
        named, spoken = item_escape(registry, key, entry), served_escape(registry, key, entry)
        if item.escape != named:
            faults.append(f"S6: the escape is {item.escape!r}; the registry's is {named!r}"
                          + (" (served apart on this link)" if named != registry_escape(registry, key) else ""))
        for escape in {item.escape, spoken} - {None}:
            if _form(escape) in forms:
                faults.append(f"S6: the escape {escape!r} is also an option")
        if spoken is not None:
            match = re.match(r"^Or say (.+)\.$", item.escape_line or "")
            if not match or said(match.group(1)) != said(spoken):
                faults.append(f"S6: the escape line is {item.escape_line!r}; §3 says 'Or say {{escape}}.' last, "
                              f"the escape served {spoken!r}")
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
                or bool(count.group(2)):
            faults.append(f"S7: the count line is {item.count_line!r}; §3 says 'I'll read "
                          f"{_NUMBER_WORDS[n] if n < len(_NUMBER_WORDS) else n} options.' (no '; pick two' since "
                          "keel-cloud 158)")
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
        # keel-cloud 130 FR-10: an introduced step past 20 words opens its question *Would you* (spec 069 FR-1)
        halves = re.split(r"(?i)\bwould you ", item.stem, maxsplit=1)
        step = halves[1] if len(halves) > 1 else ""
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


#: keel-cloud `ItemFrames.adoptionFriction`'s question after the clause.
ADOPTION_ASK = "Would you do that, or not?"
#: keel-cloud `SpokenCap.LEADING_CLAUSE` (132 FR-1): a step stored with a leading clause before its question.
_LEADING_CLAUSE = re.compile(r"(?i)^([^,?]+?),\s*((?:would|will|could|can|do) you\s+.+)$")
#: keel-cloud `ItemFrames.questionPart`'s opener, the words `adoptionFriction` turns into *You'd*.
_ASKS_YOU = re.compile(r"(?i)^(?:would|will|could|can|do) you\s+")
#: keel-cloud `StrangerGrammar.secondPerson`: the third person said to the stranger (the count does not move).
_THIRD_TO_SECOND = {"they": "you", "them": "you", "their": "your", "theirs": "yours", "themselves": "yourself",
                    "they're": "you're", "they've": "you've", "they'd": "you'd", "they'll": "you'll"}
_THIRD_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(w) for w in _THIRD_TO_SECOND), key=len, reverse=True))
                       + r")\b", re.IGNORECASE)
#: keel-cloud `StrangerGrammar.wouldDo`'s turns: *you had to* is asked *you would have to* -- one word more.
_WOULD_DO = (("you had to ", "you would have to "), ("you have to ", "you would have to "),
             ("you need to ", "you would need to "), ("you needed to ", "you would need to "))


def _belief_lower(text: str) -> str:
    """keel-cloud `BeliefSentence.lower`: the first letter lower-cased unless the second is a capital (an acronym)."""
    return text if len(text) > 1 and text[1].isupper() else text[:1].lower() + text[1:]


def _trim_end(text: str) -> str:
    t = str(text or "").strip()
    while t.endswith((".", "?")):
        t = t[:-1].strip()
    return t


def _clause(asked: str) -> str:
    """keel-cloud `ItemFrames.clause`: no closing stop or question mark, lower-cased as the frame takes it."""
    text = _trim_end(asked)
    return _belief_lower(text) if text else "it would have fitted"


def _second_person(text: str) -> str:
    def turn(m):
        said = _THIRD_TO_SECOND[m.group(1).lower()]
        return said[:1].upper() + said[1:] if m.group(1)[:1].isupper() else said
    return _THIRD_RE.sub(turn, text)


def adoption_frame(asked: str) -> str:
    """Spec 093 FR-4 (keel-cloud 163's tasks.md, `ItemFrames.adoptionFriction` as `AskedRules.framed` reads it): an
    Adoption friction clause as code frames it, so the harness and the cloud count the same words. A clause the model
    opens on *would you* (or *will / could / can / do you*) is said *You'd ...* -- its own *would you* counted as one
    word -- with a leading clause (*When the repair was done, would you ...*) said after it while the whole stays at
    most 20 words, then *Would you do that, or not?*; any other clause is said in the second person, *you had to* as
    *you would have to* (`StrangerGrammar.wouldDo`), capitalised, then the same question. 163's 12-word clause rule is
    the registry's (`option_rule`), never restated here. (keel-cloud's past-tense turn, *you wore* -> *you'd wear*, moves
    no word and is not restated.)"""
    trimmed = _trim_end(asked)
    led = _LEADING_CLAUSE.match(trimmed)
    led = (_belief_lower(led.group(1).strip()), led.group(2).strip()) if led and len(led.group(1).split()) >= 2 \
        else None
    text = led[1] if led else _clause(asked)
    if _ASKS_YOU.match(text):
        said = "You'd " + _ASKS_YOU.sub("", _clause(_belief_lower(text)), count=1)
        # `SpokenCap.present`: the leading clause said after it in the present (*was* -> *is*; no word moves)
        after = re.sub(r"(?i)\bwere\b", "are", re.sub(r"(?i)\bwas\b", "is", _second_person(_belief_lower(led[0])))) \
            if led else None
        whole = said if after is None else f"{said} {after}"
        line = f"{whole}. {ADOPTION_ASK}"
        return line if words(line) <= STEM_MAX_WORDS else f"{said}. {ADOPTION_ASK}"
    clause = _second_person(_clause(asked))
    for old, new in _WOULD_DO:
        if clause.lower().startswith(old):
            clause = (new[:1].upper() if clause[:1].isupper() else new[:1]) + new[1:] + clause[len(old):]
            break
    return f"{clause[:1].upper()}{clause[1:]}. {ADOPTION_ASK}"


#: Spec 093 FR-5: the words a clause's subject opens on when it is someone or something other than the stranger --
#: *the cry*, *the room*, *it*, *someone*. A base-form clause opens on its verb, and the frame's *Would you* is its
#: subject.
THIRD_PERSON_OPENERS = frozenset({"the", "a", "an", "this", "that", "these", "those", "it", "its", "it's", "he", "she",
                                  "his", "her", "someone", "somebody", "something", "everyone", "everybody", "nobody",
                                  "no", "there", "my", "our", "i", "we"})


def _third_person_subject(clause: str) -> bool:
    """Whether a framed clause opens on a subject other than the stranger (`THIRD_PERSON_OPENERS`)."""
    first = (re.findall(r"[A-Za-z']+", clause or "") or [""])[0].lower()
    return first in THIRD_PERSON_OPENERS


def framed(key: str, occasion: str | None, asked: str) -> str:
    """The question a face is framed into (design §5.1), to count its words: *On your last {occasion},
    {asked}?* and, on Adoption friction, keel-cloud's own frame (`adoption_frame`, spec 093 FR-4; before it the harness
    kept the model's *would you* and counted one word more than `ItemFrames`)."""
    clause = str(asked or "").strip().rstrip("?.").strip()
    if key == ADOPTION_KEY:
        return adoption_frame(asked)
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
    if key == ADOPTION_KEY:
        # spec 093 FR-5: K3 judges the line as framed -- *Would you {asked}. Would you do that, or not?* addresses the
        # person itself, so a base-form clause (*open the app before picking the baby up*) reads to the stranger once
        # framed; a clause whose subject is someone or something else (*the cry ...*, *the room ...*) still does not
        said_clause = question.rsplit(f". {ADOPTION_ASK}", 1)[0]
        if not _YOU.search(said_clause) and _third_person_subject(said_clause):
            faults.append(f"K3: {asked!r} is not said to the stranger: framed it reads {said_clause!r}, a third-person "
                          "subject and no you / your")
    elif not _YOU.search(asked):
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


def score(cloud, corpus, *, entry_ids=None, registry=None) -> SpokenScore:
    """Every composed item and every corpus `asked` face of the entries asked for (all by default), each item held to
    `registry` -- by default the one the entry is bound to (`Corpus.bind`, the export's or keel-cloud's of record)."""
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
            faults = item_faults(item, registry if registry is not None else entry.registry, entry)
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
