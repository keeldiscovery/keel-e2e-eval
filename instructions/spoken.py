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
  spec 040's 25-word allowance; since keel-cloud 173, spec 113 FR-3, Relative advantage is *Would {name} have made your
  last {occasion} go better for you, or not?*, and past 20 words *Would it have made your last {occasion} ...* -- the
  short form keeps the occasion);
- `S2` the anchor, where there is one, and the stem are the screen's question, and a part sets one anchor at most;
- `S3` at most **five** options (Price's ladder **six**); none on a number (Frequency, Existing sacrifice);
- `S4` every option at most **nine** words, Commitment's counted whole at **eleven** (*Yes, I'd* and the step together
  are the option: keel-cloud 129 FR-15 took `SpokenForm.STEP_OPTION_MAX_WORDS` from 118's eleven to nine and cut the
  step to its share; keel-cloud 221 FR-1 put it back to eleven, the step whole, cut only past its own nine; spec 068
  FR-2, spec 141 FR-4),
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
Compatibility condition read as a **fact** was answered *Yes · Mostly · Partly · No* on the same four codes (128 FR-13b,
`FACT_ANSWERS_128`; since keel-cloud 174 FR-3, spec 115 FR-1, a fact is served the registry's own four, `FACT_ANSWERS`,
as a permission is -- *Mostly and Partly blur together* -- and the 128 four are read only on an item a lock stored before
174, whose labels are stored); Purchase friction is asked of **this** purchase, *Yes, and it would take a long time · Yes, but it would
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
#: step together, counted whole (spec 068 FR-2) -- at nine from 129 to 220; keel-cloud 221 FR-1 (spec 141 FR-4; cycle
#: 14, Codyco's *at one hotel* and Expanse's *for two weeks* cut off): eleven again, the step whole.
STEP_OPTION_MAX_WORDS = 11
#: keel-cloud 129 FR-15's cap, read only on an item a lock stored before 221 (the step cut to seven after *Yes, I'd*).
STEP_OPTION_MAX_WORDS_BEFORE221 = 9
#: keel-cloud 221 FR-1 (`ItemFrames.STEP_MAX_WORDS`): the step's own cap -- its share of the eleven after *Yes, I'd*.
STEP_MAX_WORDS = STEP_OPTION_MAX_WORDS - 2
OPTION_MIN_WORDS = 3
#: The options the founder wrote, held to the three-word floor (call 80).
FOUNDER_WORDED = (IMPORTANCE_KEY, CURRENT_SOLUTION_KEY)
#: The items asked as a number: no options, no count line.
NUMERIC = (FREQUENCY_KEY, SACRIFICE_KEY)


def count_answer_line(count: int) -> str:
    """keel-cloud `SpokenForm.countAnswerLine` (158 FR-1; 174 FR-5, spec 115 FR-2): Frequency's answer line on a window of
    `count` -- past five steps (`MAX_OPTIONS`) the range said, *Say a number from 1 to 7.*, never the steps one by one;
    five or fewer *A number from 1 to 5.*. The screen keeps its buttons."""
    return f"{'Say a number' if count > MAX_OPTIONS else 'A number'} from 1 to {count}."

#: keel-cloud `CommercialChain.side`: the escape an item is served with where its side is not the registry's row --
#: Existing sacrifice on a cost stated before the chain keeps spec 077's cost total (registry decision 24; since
#: keel-cloud 170 the registry's row says the same *I can't recall*, spec 110 FR-2), Ability to pay on a consumer link
#: is the consumer budget item.
OFF_CHAIN_COST_ESCAPE = "I can't recall"
CONSUMER_BUDGET_ESCAPE = "I can't say"
#: keel-cloud 172 (`ItemFrames.escapeFor`, `ItemFrames.CANT_RECALL`; spec 112's addendum): Current solution's escape
#: where Keel's list writer called the act one that could not be handed off (`handed_off: false`) -- *I can't recall*,
#: `cant_recall`, counted apart, said *Or say you can't recall.*; *Someone else did it* (the registry's
#: `someone_else_checks`) where the call is true or the list carries none. The call is stored on the server and never
#: reaches a wire, so the mirror reads it off the SERVED item's escape (`InterviewItem.escape`, `{code, label}`).
CANT_RECALL_CODE = "cant_recall"
CANT_RECALL_ESCAPE = "I can't recall"

#: keel-cloud 123 FR-8 (`ItemFrames.ABILITY_LABELS`, the registry's Compatibility guidance): the four answers to a
#: condition of ability, on the registry's own four codes; a condition of permission keeps the registry's labels.
#: Spec 118 FR-4c(c) (keel-cloud 185 FR-1, `ItemFrames.ABILITY_LABELS`): the ability's second yes reads *Yes, most of
#: the time* (it read *Yes, mostly* until 185 -- `ABILITY_ANSWERS_123`, on an item stored before it).
ABILITY_ANSWERS = {"yes_easily": "Yes, easily", "yes_with_steps": "Yes, most of the time",
                   "only_with_help": "Only sometimes", "no": "No"}
ABILITY_ANSWERS_123 = {"yes_easily": "Yes, easily", "yes_with_steps": "Yes, mostly", "only_with_help": "Only sometimes",
                       "no": "No"}


#: keel-cloud 174 FR-3 (`ItemFrames.compatibilityLabel`, spec 115 FR-1): a Compatibility condition read as a fact is
#: answered on the registry's own four, as a permission is -- never *Mostly* or *Partly*.
FACT_ANSWERS_174 = {"yes_easily": "Yes, easily", "yes_with_steps": "Yes, with some steps",
                    "only_with_help": "Only with help or approval", "no": "No"}
#: Spec 118 FR-4c(c) (keel-cloud 185 FR-1, `ItemFrames.FACT_THREE`): a fact is answered on three -- *Yes · Yes, with some
#: steps · No* -- `only_with_help` never served on a fact (`NOT_ON_A_FACT`); spoken *I'll read three options. Yes; yes,
#: with some steps; or no.* 174's four (`FACT_ANSWERS_174`) read only on an item stored before 185.
FACT_ANSWERS = {"yes_easily": "Yes", "yes_with_steps": "Yes, with some steps", "no": "No"}
FACT_CODES = tuple(FACT_ANSWERS)
#: keel-cloud 128 FR-13b (`ItemFrames.FACT_LABELS`, spec 067): the four a fact was answered on from 128 to 173, on the
#: same codes -- retired by 174 FR-3 and read only on an item a lock stored before 174 (its labels are stored), as
#: `FollowUpComposer`'s *Partly* reads it.
FACT_ANSWERS_128 = {"yes_easily": "Yes", "yes_with_steps": "Mostly", "only_with_help": "Partly", "no": "No"}
#: keel-cloud 128 FR-12 (`ItemFrames.PURCHASE_LABELS`): Purchase friction's three, reread for this purchase.
PURCHASE_ANSWERS = {"yes_long": "Yes, and it would take a long time", "yes_quick": "Yes, but it would be quick",
                    "not_needed": "No, it wouldn't be needed"}


def buyer_answers(role: str | None) -> list:
    """keel-cloud 198 FR-4 (`ItemFrames.buyerPayerLabel`, `buyerPayerAtPriceLabel`): Buyer and payer's labels beside the
    registry's, in its order, the person's own answer first and no Yes or No in front -- the consumer link's past answers
    (*I decided on my own · {The role} had to agree · Several people had to agree · It was someone else's call*, the
    registry's own but the named role) and the decision-maker's for this purchase at the founder's price (*I could sign
    off myself · {The role} would have to agree · Several people would have to agree · It's someone else's call*), with the
    role the founder named (`None`: *Nobody else* tested, the second *Someone else ...*). 128's six, served before 198,
    are `buyer_answers_128`."""
    from instructions.chain import the_role                           # noqa: PLC0415
    past_who = None if role is None else re.sub(r"^(?:their|your) ", "my ", the_role(role))
    who = None if role is None else the_role(role)
    return ["I decided on my own",
            "Someone else had to agree" if past_who is None else f"{_upper_first(past_who)} had to agree",
            "Several people had to agree", "It was someone else's call",
            "I could sign off myself",
            "Someone else would have to agree" if who is None else f"{_upper_first(who)} would have to agree",
            "Several people would have to agree", "It's someone else's call"]


def _upper_first(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def buyer_answers_128(role: str | None) -> list:
    """keel-cloud 128 FR-5 / FR-18 / FR-19 (`ItemFrames.buyerPayerLabel`, `buyerPayerAtPriceLabel`) as served from 128 to
    197 -- read only on an item a lock stored before 198 (its labels are stored)."""
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


#: keel-cloud 197's registry labels for Buyer and payer's four (read only on an item a lock stored before 198).
BUYER_LABELS_197 = ("Yes, they had to agree", "No, I decided on my own", "Someone else had to agree instead",
                    "No, someone else decided for me")


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


def handed_off_of(served) -> bool | None:
    """keel-cloud 172: the list writer's call on Current solution as the served item shows it -- False where the item is
    served the *I can't recall* escape (`cant_recall`, by its code or its label), True where it is served another,
    None where nothing served is handed (a list with no call reads as the registry's row). `served` is the served item
    (`{escape: {code, label}}`), its escape, or the escape's code or label."""
    if served is None:
        return None
    escape = served.get("escape", served) if isinstance(served, dict) else served
    if isinstance(escape, dict):
        code, label = escape.get("code"), escape.get("label")
    else:
        code, label = escape, escape
    if not code and not label:
        return None
    said = {str(code or "").strip().lower(), " ".join(str(label or "").split()).lower()}
    return not ({CANT_RECALL_CODE, CANT_RECALL_ESCAPE.lower()} & said)


def _current_solution_escape(registry, served):
    """keel-cloud 172 `ItemFrames.escapeFor`: *I can't recall* where the call was false, the registry's otherwise."""
    if handed_off_of(served) is False:
        return CANT_RECALL_ESCAPE
    return registry_escape(registry, CURRENT_SOLUTION_KEY)


def item_escape(registry, key: str, entry=None, served=None):
    """The escape an item **names** (spec 068 FR-2, keel-cloud 129's owed list): the registry's row, except Ability to
    pay on a consumer link, which is served as the consumer budget item with its own escape, *I can't say* (the guard
    called Issen's clean run RED on the registry's *I can't recall one*). Commitment's is none (129 FR-9's escape open).
    Existing sacrifice off the chain names the registry's and says spec 077's (`served_escape`), as the record does.
    Spec 112's addendum (keel-cloud 172): Current solution's is read off the SERVED item (`served`, `handed_off_of`) --
    *I can't recall* where the list's `handed_off` call was false, the registry's *Someone else did it* otherwise (and
    with nothing served: a list with no call)."""
    dimension = registry.by_key(key)
    if entry is not None and key == ABILITY_KEY and not entry.b2b():
        return CONSUMER_BUDGET_ESCAPE
    if points_back(entry, key):
        return pointed_back_escape(registry)
    if key == CURRENT_SOLUTION_KEY:
        return _current_solution_escape(registry, served)
    escape = dimension.escape
    return escape.get("label") if escape else None


def points_back(entry, key: str) -> bool:
    """keel-cloud 181 FR-2 (`CommercialChain.side`, `pointsBack`): Ability to pay on a B2B chain study with a price that
    is not free points back to the price, and its escape is not its registry row's (*I can't recall one* fitted a past
    tool) but Price's own."""
    if entry is None or key != ABILITY_KEY or not entry.b2b() or not callable(getattr(entry, "price", None)):
        return False
    from instructions import chain as chain_mod                        # noqa: PLC0415
    return chain_mod.asks_back(entry.price())


def pointed_back_escape(registry):
    """Spec 119 FR-5 (keel-cloud 181 FR-2): Ability to pay's escape of record where it points back -- read off the
    registry the item was served from (the bundle's `contract-export/dimension-registry.json`), never a pinned label:
    `CommercialChain.side` gives it Price's own escape (`cant_say`, *I can't say*; *the consumer's and Price's own*), so
    it is Price's row's escape in that export. The export's Ability to pay row still names `cant_recall_one`, which
    `side` replaces (S6 called every B2B money study of cycle 5 red on it)."""
    return registry_escape(registry, PRICE_KEY)


def served_escape(registry, key: str, entry=None, served=None):
    """The escape the item is served (and said) with: the registry's, read by the side keel-cloud serves it by
    (`CommercialChain.side`). Spec 112's addendum (keel-cloud 172): Current solution's off the served item, as
    `item_escape` -- said *Or say you can't recall.* where it is *I can't recall*."""
    dimension = registry.by_key(key)
    if key == CURRENT_SOLUTION_KEY:
        return _current_solution_escape(registry, served)
    if entry is not None:
        if key == SACRIFICE_KEY and dimension.respondent_control == VALUE_BOX_CONTROL and not entry.chain():
            return OFF_CHAIN_COST_ESCAPE
        if key == ABILITY_KEY and not entry.b2b():
            return CONSUMER_BUDGET_ESCAPE
        if points_back(entry, key):
            return pointed_back_escape(registry)
    return registry_escape(registry, key)


def served_labels(registry, key: str, entry=None) -> list:
    """Every label the registry says `key`'s item may be served with: its fixed answers; Compatibility's ability four
    beside them (123 FR-8), a fact's (the registry's four since keel-cloud 174, 128's on an item stored before it);
    Commitment's options written from the entry's step (118 FR-1)."""
    if registry is None or not registry.has(key):
        return []
    dimension = registry.by_key(key)
    labels = [a.get("label") for a in dimension.fixed_answers]
    if key == COMPATIBILITY_KEY:
        fixed = list(labels)
        labels += [ABILITY_ANSWERS.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)]
        labels += [FACT_ANSWERS.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)
                   if code in FACT_ANSWERS]
        # keel-cloud 185: an item stored before it keeps the ability's *Yes, mostly* (174's fact four is the registry's)
        labels += [ABILITY_ANSWERS_123.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)]
        # keel-cloud 174 FR-3: an item a lock stored before 174 keeps 128's fact four (its labels are stored)
        labels += [FACT_ANSWERS_128.get(code, label) for code, label in zip(dimension.fixed_answer_codes, fixed)]
    if key == PURCHASE_FRICTION_KEY:
        labels += list(PURCHASE_ANSWERS.values())
    if key == ADOPTION_KEY and entry is not None:
        # keel-cloud 198 FR-9 (`RespondentItems.onlyIfOptions`): the conditional yes is the stranger's own condition,
        # *Only if {condition}*, where the tested item carries one (the registry's fixed yes where none)
        tested = entry.tested(key) if callable(getattr(entry, "tested", None)) else None
        condition = (tested or {}).get("condition") or (tested or {}).get("only_if")
        if condition:
            labels.append(ONLY_IF + " ".join(str(condition).split()).rstrip("."))
    if key == BUYER_KEY:
        roles = [i.get("label") for i in (((entry.founder_list(key) or {}).get("items") or []) if entry else [])
                 if i.get("label") and i.get("code") != "nobody_else"]
        for role in roles + [None]:
            labels += buyer_answers(role) + buyer_answers_128(role)       # spec 130: 198's, and 128's on an older lock
        labels += list(BUYER_LABELS_197)
    if key == COMMITMENT_KEY and entry is not None:
        steps = [i.get("label") for i in ((entry.founder_list(key) or {}).get("items") or []) if i.get("label")]
        if steps:
            # spec 141 FR-4 (keel-cloud 221): the step whole; 129's cut Yes on an item a lock stored before 221
            labels += list(dict.fromkeys((first_yes(steps[0]), first_yes_before221(steps[0]))))
        if len(steps) > 1:
            labels += [second_yes(steps[1]), second_yes_118(steps[1])]   # spec 130: 198's soft yes, 118's on an older lock
            if second_yes_before221(steps[1]) not in labels:
                labels.append(second_yes_before221(steps[1]))
        labels.append(COMMITMENT_SECOND_YES_197)
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


#: keel-cloud 204 (`RowCap.DANGLING`): what a word-boundary cut never ends on.
_DANGLING = frozenset({"and", "or", "but", "nor", "so", "the", "a", "an", "of", "to", "with", "on", "at", "for", "in",
                       "from", "after", "before", "by", "during", "over", "across", "within", "into", "onto", "about",
                       "than", "that", "which", "who", "whose", "while", "when", "where", "because", "as", "if",
                       "against", "without", "through", "under", "per", "via", "their", "your", "its", "his", "her", "my",
                       "our"})
_EDGES = ";,.:|-–—/ "
_ALTERNATIVE = re.compile(r"^(.+)\s+(?:or|and)\s+\S.*$", re.S)


def row_cap_cut(label: str, most: int) -> str:
    """keel-cloud 204 (`RowCap.cut`, spec 204 FR-2): a founder-list row cut to at most `most` words -- as it is where it
    fits; else by its trailing phrases (`cut_to_fit`, 130's *They would have a bank account or wallet*), then a trailing
    *or* / *and* alternative; else the first `most` words on a word boundary, a dangling joiner, article or preposition
    and the separators at the end dropped. Never empty where the label has a word, never over the cap."""
    if label is None or words(label) <= most:
        return label
    cut = cut_to_fit(label, most)
    while words(cut) > most:
        alternative = _ALTERNATIVE.match(cut)
        if not alternative or words(alternative.group(1)) < 2:
            return _at_boundary(label, most)
        cut = cut_to_fit(alternative.group(1).strip(), most)
    return cut


def _at_boundary(label: str, most: int) -> str:
    """`RowCap.atBoundary`: the first `most` words, a dangling last word and the separators at the end dropped."""
    kept = str(label).strip().split()[:max(1, most)]
    while len(kept) > 1 and (not kept[-1].strip(_EDGES) or kept[-1].strip(_EDGES).lower() in _DANGLING):
        kept.pop()
    text = " ".join(kept)
    end = len(text)
    while end > 1 and text[end - 1] in _EDGES:
        end -= 1
    return text[:end]


def first_yes(step: str) -> str:
    """`ItemFrames.firstYes` since keel-cloud 221 FR-1 (spec 141 FR-4): *Yes, I'd {step}*, the step whole, cut only past
    its own nine (`STEP_MAX_WORDS`), so the option is at most eleven."""
    return "Yes, I'd " + cut_to_fit(_lower(str(step).strip()), STEP_MAX_WORDS)


def first_yes_before221(step: str) -> str:
    """`ItemFrames.firstYes` from 129 to 220: the step cut to its share of the option's nine -- read only on an item a
    lock stored before 221."""
    return "Yes, I'd " + cut_to_fit(_lower(str(step).strip()), OPTION_MAX_WORDS - 2)


def step_cut(step: str | None) -> str | None:
    """keel-cloud 221 FR-1 (`ItemFrames.stepCut`): the step as the Yes says it where the Yes had to cut it (a step past
    `STEP_MAX_WORDS`; the lock's S4 note names the cut), or None where it is whole."""
    if step is None or not str(step).strip():
        return None
    whole = _lower(str(step).strip())
    cut = cut_to_fit(whole, STEP_MAX_WORDS)
    return None if cut == whole else cut


def second_yes(smaller_step: str) -> str:
    """`ItemFrames.secondYes` since keel-cloud 198 FR-1: the soft yes, *Probably, after {smaller step} first*, never
    *first first* (129 FR-9); since keel-cloud 221 (spec 141 FR-4) held to Commitment's eleven less the frame and an
    act-first smaller step said in its -ing form (`smaller_said`); with no smaller step the registry's *Probably yes*
    (`ItemFrames.PROBABLY_YES`, served on every list since 198)."""
    return "Probably, after " + _second_step(smaller_step)


def second_yes_before221(smaller_step: str) -> str:
    """`ItemFrames.secondYes` from 198 to 220: cut to fit nine, the smaller step as typed -- read only on an item a lock
    stored before 221."""
    return "Probably, after " + _second_step(smaller_step, before221=True)


def second_yes_118(smaller_step: str) -> str:
    """`ItemFrames.secondYes` from 118 to 197: *Yes, after {smaller step} first* -- read only on an item a lock stored
    before 198 (the frame of its day: nine, the step as typed)."""
    return "Yes, after " + _second_step(smaller_step, before221=True)


def _second_step(smaller_step: str, before221: bool = False) -> str:
    said_step = _lower(str(smaller_step).strip()) if before221 else smaller_said(smaller_step)
    first = re.search(r"\bfirst$", said_step, re.IGNORECASE) is not None
    most = (OPTION_MAX_WORDS if before221 else STEP_OPTION_MAX_WORDS) - (2 if first else 3)
    step = cut_to_fit(said_step, most)
    return step + ("" if re.search(r"\bfirst$", step, re.IGNORECASE) else " first")


#: keel-cloud 221 FR-2 (`ItemFrames.ACT_VERBS`): acts a smaller step opens on that `StrangerGrammar.presentVerb` does not
#: carry.
SMALLER_ACT_VERBS = frozenset(("watch", "join", "test", "attend", "visit", "borrow", "hear", "listen", "view"))
#: keel-cloud 221 FR-2 (`ItemFrames.SIZE_OR_COST`): the modifiers a smaller step's act may carry -- never the act itself.
SIZE_OR_COST = frozenset(("free", "paid", "short", "quick", "small", "brief", "little", "single", "money-back",
                          "no-cost", "cost-free", "risk-free", "live", "guided", "online", "private", "personal"))


def opens_on_its_act(smaller_step: str | None) -> bool:
    """keel-cloud 221 FR-2 (`ItemFrames.opensOnItsAct`): whether a smaller step opens on its act's verb in base form
    (*try*, *look at*) -- two words at least."""
    from harness import qualifiers as q_mod                            # noqa: PLC0415 - `StrangerGrammar.presentVerb`
    parts = str(smaller_step or "").strip().split()
    if len(parts) < 2:
        return False
    first = parts[0].lower()
    return q_mod.present_verb(first) or first in SMALLER_ACT_VERBS


def smaller_said(smaller_step: str) -> str:
    """keel-cloud 221 FR-2 (`ItemFrames.smallerSaid`): the smaller step as a frame says it after *after* -- one that opens
    on its act (*try a pair of caption glasses*) in its -ing form (*trying a pair of caption glasses*, `SpokenCap.gerund`);
    a noun phrase (*a free trial*) as it is, lower-cased."""
    from harness import vectors_script as vs_mod                       # noqa: PLC0415 - `SpokenCap.gerund`'s port
    said = _lower(str(smaller_step).strip())
    return vs_mod.gerund(said) if opens_on_its_act(said) else said


def smaller_act(smaller_step: str | None) -> str | None:
    """keel-cloud 221 FR-2 (`ItemFrames.act`): a smaller step's act -- its first content word that says neither what it
    costs nor how big it is (`SIZE_OR_COST`, *ten-minute*) -- or None."""
    from harness import qualifiers as q_mod                            # noqa: PLC0415 - `FounderWords.dropped`
    for word in q_mod.dropped(smaller_step, ""):
        if word not in SIZE_OR_COST and not re.fullmatch(r"[a-z0-9]+-(?:minute|hour|day|week|month|year)s?", word):
            return word
    return None


def restates_the_step(step: str | None, smaller_step: str | None) -> bool:
    """keel-cloud 128 FR-6 / 221 FR-2 (`ItemFrames.restatesTheStep`): whether a smaller step restates part of the step
    itself -- its head (last content word) is the step's, half its words or more are, and (221) its act is the step's
    too; a smaller step naming a different act (*try*, *look*, *demo*) is not the step again, whatever nouns it shares
    (AirCaps' *try a pair of caption glasses* beside *order the caption glasses with free returns*)."""
    from harness import qualifiers as q_mod                            # noqa: PLC0415 - `FounderWords.dropped`
    if step is None or smaller_step is None:
        return False
    words_of = q_mod.dropped(smaller_step, "")
    if not words_of:
        return False
    head = words_of[-1]
    not_in_step = q_mod.dropped(smaller_step, step)
    act = smaller_act(smaller_step)
    return (head not in not_in_step and 2 * (len(words_of) - len(not_in_step)) >= len(words_of)
            and (act is None or act not in not_in_step))


#: keel-cloud 198 FR-1 (`ItemFrames.PROBABLY_YES`, the registry's `yes_after_trying` label): the soft yes where the list
#: carries no smaller step; the registry's label before 198, on an item stored before it.
PROBABLY_YES = "Probably yes"
COMMITMENT_SECOND_YES_197 = "Yes, after trying it first"
#: keel-cloud 198 FR-9 (`SavedList.ONLY_IF`): Adoption friction's conditional yes, the stranger's own condition after it.
ONLY_IF = "Only if "
#: keel-cloud 198 FR-2 (`SpokenForm.escapeLine`): *I can't say* said as itself, *Or say: I can't say.*
CANT_SAY = "I can't say"


def escape_line(escape) -> str | None:
    """keel-cloud `SpokenForm.escapeLine` (198 FR-2): the one escape said last, turned to the person -- *Or say you
    can't tell.* -- and *I can't say* as itself, *Or say: I can't say.*; None where there is none."""
    if escape is None:
        return None
    if str(escape).strip().lower() == CANT_SAY.lower():
        return f"Or say: {CANT_SAY}."
    return "Or say " + _lower(said_label(escape)) + "."


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
        # spec 119 FR-5 (keel-cloud 187 FR-3): the duration bands are read as Price's -- said in two steps, so S3 counts
        # the first step's four, never the screen's six
        counted = first_step(key, options) if key == PURCHASE_FRICTION_KEY else options
        if not options or len(counted) > most:
            faults.append(f"S3: {len(counted)} options; at most {most}")
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
        # spec 112's addendum (keel-cloud 172): Current solution's escape is the served item's -- the record's label
        served = {"label": item.escape} if key == CURRENT_SOLUTION_KEY else None
        named, spoken = item_escape(registry, key, entry, served), served_escape(registry, key, entry, served)
        if item.escape != named:
            faults.append(f"S6: the escape is {item.escape!r}; the registry's is {named!r}"
                          + (" (served apart on this link)" if named != registry_escape(registry, key) else ""))
        for escape in {item.escape, spoken} - {None}:
            if _form(escape) in forms:
                faults.append(f"S6: the escape {escape!r} is also an option")
        if spoken is not None:
            match = re.match(r"^Or say:? (.+)\.$", item.escape_line or "")    # keel-cloud 198 FR-2: "Or say: I can't say."
            if not match or said(match.group(1)) != said(spoken):
                faults.append(f"S6: the escape line is {item.escape_line!r}; §3 says 'Or say {{escape}}.' last, "
                              f"the escape served {spoken!r}")
        elif item.escape_line is not None:
            faults.append(f"S6: an escape line {item.escape_line!r} on an item with no escape")
    # S7 / S8: the template's count and options lines.
    transform = transform_of(key, options)
    if key in NUMERIC:
        if item.count_line is not None:
            faults.append(f"S7: a count line {item.count_line!r} on a number")
        if not item.options_line.strip().endswith("."):
            faults.append(f"S8: the answer line {item.options_line!r} is not one sentence")
    else:
        spoken = first_step(key, options)
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
        if key == PRICE_KEY and len(options) == 6 and any("%" in str(o) for o in options) and spoken != options:
            # spec 119 FR-5 (keel-cloud 185 FR-3, `SpokenForm.percentSaid`): a percent ladder's first step is said in
            # words (*Under a quarter of a percent; a quarter to under half a percent; half a percent or more; or you
            # wouldn't pay for this.*), so it is held to §3's shape -- the four in order, *Under ...* first, *... or
            # more* (or *Over ...*) third, the last option said whole after *; or* -- never to the screen's figures
            if not _percent_first_step_holds(pieces, options):
                faults.append(f"S8: the options line is {line!r}; §3 says the {n} options in order, '...; or z.'")
        elif pieces is None or [said(p) for p in pieces] != [said(o) for o in spoken]:
            faults.append(f"S8: the options line is {line!r}; §3 says the {n} options in order, '...; or z.'")
    # S9: the transform.
    if item.transform != transform:
        faults.append(f"S9: the transform is {item.transform!r}; §4 names {transform!r} for {key}")
    # S11 (spec 118 FR-3, keel-cloud 185): Price's second step, both lines, as the voice says them.
    faults += second_step_faults(item)
    # S10: Commitment's step said once to the stranger.
    if key == COMMITMENT_KEY:
        # keel-cloud 130 FR-10: an introduced step past 20 words opens its question *Would you* (spec 069 FR-1)
        halves = re.split(r"(?i)\bwould you ", item.stem, maxsplit=1)
        step = halves[1] if len(halves) > 1 else ""
        if re.search(r"\byou\b", step, re.IGNORECASE):
            faults.append(f"S10: the step reads {item.stem!r}; 'would you {{step}}' says 'you' twice -- the step "
                          "is the stranger's, in base form, with no second 'you'")
    return faults


def first_step(key: str, options: list) -> list:
    """What the voice says first: Price's first step (`_first_step`), the duration bands' (`duration_first_step`,
    keel-cloud 182 / 187), every other item's options as served."""
    if key == PRICE_KEY:
        return _first_step(options)
    if key == PURCHASE_FRICTION_KEY:
        return duration_first_step(options)
    return list(options)


def transform_of(key: str, options: list) -> str:
    """§4's transform for `key`: Importance `one_then_one_more`, Price `two_steps`; spec 119 FR-5 (keel-cloud 187 FR-3,
    `SpokenForm.of` on `DURATION_BANDS`): the duration bands `two_steps` where they are the six read in two steps (the
    fixed three of a list with no time, `none`); every other item `none`."""
    if key == PURCHASE_FRICTION_KEY:
        return "two_steps" if duration_first_step(options) != list(options) else "none"
    return TRANSFORMS.get(key, "none")


def duration_first_step(options: list) -> list:
    """keel-cloud 182 FR-2 (`SpokenForm.durationFirstStep`): the duration bands' first step, as Price's -- under the
    middle band, the middle band, over it, or that it wouldn't be needed (*Under 4 weeks; 4 weeks to 3 months; over 3
    months; or it wouldn't be needed.*); a band that says its unit once (*3 to 6 months*) lends it to its low edge
    (*Under 3 months*, *1 month* in the singular). Off the six (or a middle band with no *to*) the options as served."""
    options = list(options)
    if len(options) != 6:
        return options
    middle = str(options[2])
    if " to " not in middle:
        return options
    low, high = (part.strip() for part in middle.split(" to ", 1))
    if high.startswith("under "):
        high = high[len("under "):]
    if " " not in low:
        unit = high.rsplit(" ", 1)[-1]
        low = f"{low} {unit[:-1] if low == '1' and unit.endswith('s') else unit}"
    return [f"Under {low}", middle, f"Over {high}", options[5]]


def side_question(options: list, start: int) -> str:
    """keel-cloud 185 / 187 (`SpokenForm.sideQuestion`): one side's two bands from `start` (0 under the middle band, 3
    over it) as one short question in the screen's words -- *Under 2 weeks, or 2 to under 4 weeks?*, *3 to 6 months, or
    over 6 months?*, *Under $500, or $500 to under $800?* (percents are said in words by the cloud, not mirrored)."""
    one, two = (said_label(str(options[start + k]).strip().rstrip(".").strip()) for k in (0, 1))
    return f"{one[:1].upper() + one[1:]}, or {_lower(two)}?"


def said_label(label: str) -> str:
    """`SpokenForm.second`: a label said to the person, the first person turned (*I* -> *you*), its words otherwise as
    served."""
    return _FIRST_PERSON_RE.sub(lambda m: m.group(0) if m.group(0) == "US" else _FIRST_PERSON[m.group(0).lower()],
                                str(label or "").strip())


def _percent_first_step_holds(pieces, options: list) -> bool:
    """Spec 119 FR-5: a percent ladder's first step keeps §3's shape -- four pieces, *Under ...* first, the screen's
    middle band's place second, *... or more* / *Over ...* third, the last option said whole after *; or*."""
    if not pieces or len(pieces) != 4:
        return False
    first, _, third, last = pieces
    return first.startswith("Under ") and (third.endswith(" or more") or third.lower().startswith("over ")) \
        and said(last) == said(options[5])


def _first_step(options: list) -> list:
    """§4, Price's first step: under the middle band, the middle band, its top *or more* (spec 118 FR-3, keel-cloud 185
    FR-3: one home per edge -- the middle band reads *X to under Y*, step one *Y or more*), or the last. A ladder recorded
    before 185 (*X to Y*) keeps *Over Y*."""
    if len(options) != 6 or " to " not in options[2]:
        return options
    if " to under " in options[2]:
        low, high = options[2].split(" to under ", 1)
        return [f"Under {low}", options[2], f"{high} or more", options[5]]
    low, high = options[2].split(" to ", 1)
    return [f"Under {low}", options[2], f"Over {high}", options[5]]


def second_step(options: list) -> tuple[str, str] | None:
    """Spec 118 FR-3 (keel-cloud 185 FR-3, `SpokenForm.secondStep`): Price's second step on a money ladder -- the two
    bands on that side as one short question, no second escape: *Under $500, or $500 to under $800?*, *$2,500 to under
    $5,000, or $5,000 or more?*. None off the six. (A share's bands are said in words, *a quarter of a percent*, so a
    percent ladder is held to the shape alone, `second_step_faults`.)"""
    if len(options) != 6:
        return None
    return f"{options[0]}, or {options[1]}?", f"{options[3]}, or {options[4]}?"


def second_step_faults(item) -> list:
    """`S11` (spec 118 FR-3, keel-cloud 185 §17): on a Price item in two steps, the record carries both second-step
    lines (`under`, `over`), each one question of at most 20 words with one *, or* and no escape; on a money ladder each
    is the two bands said whole (`second_step`)."""
    if item.key not in (PRICE_KEY, PURCHASE_FRICTION_KEY) or item.transform != "two_steps":
        return []
    if item.key == PRICE_KEY and not (item.under or item.over) \
            and not (len(item.options) == 6 and " to under " in str(item.options[2])):
        return []                                      # a ladder recorded before 185 (*X to Y*) has no second step
    faults = []
    want = second_step(list(item.options))
    if item.key == PURCHASE_FRICTION_KEY:
        # spec 119 FR-5 (keel-cloud 187 FR-3): the duration bands' second step, read as Price's -- each side's two bands
        # (`side_question`), served on every lock since 187 (a lock before it serves none: no fault, the page composes)
        if not (item.under or item.over):
            return []
        want = (side_question(list(item.options), 0), side_question(list(item.options), 3)) \
            if len(item.options) == 6 else None
    for side, line in (("under", item.under), ("over", item.over)):
        if not line:
            faults.append(f"S11: no {side} line -- the second step says the side's two bands (keel-cloud 185 / 187)")
            continue
        if words(line) > STEM_MAX_WORDS or not line.endswith("?") or line.count(", or ") != 1 or "Or say" in line:
            faults.append(f"S11: the {side} line {line!r} is not one short question of two bands with no escape")
        elif want and not any("%" in o for o in item.options) and \
                line != (want[0] if side == "under" else want[1]):
            faults.append(f"S11: the {side} line is {line!r}; the side's two bands said whole are "
                          f"{want[0] if side == 'under' else want[1]!r}")
    return faults


#: keel-cloud `ItemFrames.toUse`'s question after the step (spec 112 FR-1; keel-cloud 171 FR-4b).
ADOPTION_ASK = "Would you do that, or not?"
#: keel-cloud 171 (`founder-lists.md`'s *Short*, the registry's option rule): an Adoption friction clause is at most
#: 10 words -- *To use {name}, you'd* is 10 framed with a one-word name or *it*. The option rule's; a fault of the
#: frame (`K2`, 20 framed) is the harness's measure, never this count (spec 112 FR-1).
ADOPTION_CLAUSE_MAX_WORDS = 10
#: keel-cloud `SpokenCap.LEADING_CLAUSE` (132 FR-1): a step stored with a leading clause before its question.
_LEADING_CLAUSE = re.compile(r"(?i)^([^,?]+?),\s*((?:would|will|could|can|do) you\s+.+)$")
#: keel-cloud `ItemFrames.questionPart`'s opener.
_ASKS_YOU = re.compile(r"(?i)^(?:would|will|could|can|do) you\s+.+$")
#: keel-cloud `StrangerGrammar.THIRD` (`secondPerson(text, false)`): the third person said to the stranger. *them* is
#: not one of them (*talk over them* keeps its object); spec 093's mirror turned it and is corrected here (spec 112).
_THIRD_TO_SECOND = {"they": "you", "their": "your", "theirs": "yours", "themselves": "yourself",
                    "they're": "you're", "they've": "you've", "they'd": "you'd", "they'll": "you'll"}
_THIRD_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(w) for w in _THIRD_TO_SECOND), key=len, reverse=True))
                       + r")\b", re.IGNORECASE)
#: keel-cloud `StrangerGrammar.IRREGULAR` (base -> past), as `baseOfPast` reads it back.
_IRREGULAR = {"are": "were", "is": "was", "have": "had", "has": "had", "do": "did", "does": "did", "go": "went",
              "get": "got", "make": "made", "take": "took", "see": "saw", "come": "came", "know": "knew", "find": "found",
              "give": "gave", "tell": "told", "feel": "felt", "leave": "left", "keep": "kept", "begin": "began",
              "run": "ran", "sit": "sat", "stand": "stood", "lose": "lost", "pay": "paid", "send": "sent",
              "spend": "spent", "buy": "bought", "bring": "brought", "think": "thought", "hold": "held",
              "can": "could", "will": "would", "may": "might", "must": "had to", "put": "put", "set": "set",
              "cut": "cut", "let": "let", "read": "read", "write": "wrote", "speak": "spoke", "meet": "met",
              "sell": "sold", "wake": "woke", "eat": "ate", "fall": "fell", "drive": "drove", "ride": "rode",
              "build": "built", "hear": "heard", "mean": "meant", "say": "said", "become": "became",
              "choose": "chose", "win": "won", "fly": "flew", "grow": "grew", "wear": "wore", "ring": "rang",
              "catch": "caught"}
#: keel-cloud 171 `SpokenCap.BE_DO_HAVE`: a statement's own *be*, *do* and *have*, in base form after *you'd*.
_BE_DO_HAVE = {"was": "be", "were": "be", "are": "be", "did": "do", "had": "have"}
#: keel-cloud 171 `SpokenCap.PARTICIPLES`: the participles that are no past (*worn*, *taken*) -- English's.
_PARTICIPLES = {"worn": "wear", "taken": "take", "given": "give", "seen": "see", "done": "do", "gone": "go",
                "written": "write", "spoken": "speak", "driven": "drive", "chosen": "choose", "known": "know",
                "grown": "grow", "flown": "fly", "eaten": "eat", "fallen": "fall", "ridden": "ride",
                "broken": "break", "woken": "wake", "begun": "begin", "shown": "show", "gotten": "get",
                "forgotten": "forget"}


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


def base_of_past(past: str) -> str | None:
    """keel-cloud `StrangerGrammar.baseOfPast`: the base of a past code can be sure of -- the irregulars, and the -ied,
    -ted, -ded, -cked, -lled pasts."""
    for base, said in _IRREGULAR.items():
        if said == past and base != past and not base.endswith("s") and base not in ("is", "are", "was", "were"):
            return base
    if past.endswith("ied") and len(past) > 4:
        return past[:-3] + "y"
    if re.fullmatch(r"[a-z]+(nt|st|ct|pt|ft|lt|rt|ck|ll|sh|ch|rk|rm|rn|wn|ss|nd|ld|rd)ed", past):
        return past[:-2]
    if re.fullmatch(r"[a-z]+eived", past):
        return past[:-1]
    if re.fullmatch(r"[a-z]+(ai|ea|ee|oa|oo|ou|ie)[a-z]ed", past):
        return past[:-2]
    return None


def base_of_past_loose(past: str) -> str | None:
    """keel-cloud `StrangerGrammar.baseOfPastLoose`: `base_of_past`, else a regular *-ed* undone."""
    sure = base_of_past(past)
    if sure is not None:
        return sure
    if not past.endswith("ed") or len(past) < 4:
        return None
    stem = past[:-2]
    if re.fullmatch(r".*([bdgmnprt])\1", stem):
        return stem[:-1]
    if re.fullmatch(r".*(ored|ared|ured|ired|ated|ized|ised|uced|aded|oded|iked|aked|oked|aved|ived|oved|ased)", past):
        return past[:-1]
    return stem


# ------------------------------------------------------- keel-cloud 174 FR-3 (spec 115 FR-1): a fact, read off both faces

#: keel-cloud `ItemFrames.PERMISSION_WORDS` (spec 123 FR-8): the words of a condition someone else grants.
PERMISSION_WORDS = (" allowed", " allow ", " allows ", " permitted", " permission", " approv", " sign off", " signed off",
                    " signs off", " sign-off", " authoris", " authoriz", " let you ", " clearance", " consent")
#: `ItemFrames.FACT_HEADS` (spec 129 FR-6): the head verbs of a condition that is so or is not.
FACT_HEADS = frozenset(("have", "has", "had", "own", "owns", "owned", "use", "uses", "used", "be", "is", "are", "was",
                        "were", "keep", "keeps", "kept"))
#: `ItemFrames.MODALS` (spec 129 FR-6): the modals that make a condition's head an ability.
MODALS = frozenset(("could", "can", "couldn't", "can't", "would", "will", "should", "might"))
_MODAL_ANYWHERE = re.compile(r"\b(could|can|couldn't|can't|able|would|will|should|might)\b")
_HEAD_DID = re.compile(r"^(?:did|do|does)\s+(?:you|they|we|i)\s+([a-z']+)")
_HEAD_AUX = re.compile(r"^(could|can|would|will|should|might|was|were|is|are|had|have|has)\b")
_HEAD_SUBJECT = re.compile(r"^(?:you|they|we|i|the [a-z]+|your [a-z]+|their [a-z]+)\s+(?:already\s+)?([a-z']+)")


def permission(condition) -> bool:
    """keel-cloud `ItemFrames.permission` (123 FR-8): someone has to allow it, read off the condition's words."""
    if condition is None:
        return False
    text = " " + str(condition).lower() + " "
    return any(word in text for word in PERMISSION_WORDS)


def head_verb(condition) -> str | None:
    """keel-cloud `ItemFrames.headVerb` (129 FR-6): the verb after the subject, or the auxiliary it opens on."""
    text = _clause(str(condition or "")).lower()
    for pattern in (_HEAD_DID, _HEAD_AUX, _HEAD_SUBJECT):
        m = pattern.search(text)
        if m:
            return m.group(1)
    return None


def _has_modal(condition) -> bool:
    """`ItemFrames.hasModal` (131 FR-3): a modal anywhere in the condition."""
    return bool(_MODAL_ANYWHERE.search(" " + _clause(str(condition or "")).lower() + " "))


def _label_verb(condition) -> str | None:
    """`ItemFrames.labelVerb` (131 FR-3): the first verb past a subject of any length, in the first seven words."""
    words = _clause(str(condition or "")).lower().split()
    for i, raw in enumerate(words[:7]):
        word = re.sub(r"[,.;:]$", "", raw)
        if word in MODALS or word in ("was", "were", "is", "are", "had", "has", "have", "did", "do", "does"):
            return word
        if i > 0 and base_of_past(word) is not None:
            return word
    return None


def past_fact(condition) -> bool:
    """`ItemFrames.pastFact` (131 FR-3): no modal, and its first verb a past or a form of *be*, *have* or *do*."""
    if condition is None or not str(condition).strip() or _has_modal(condition):
        return False
    verb = _label_verb(condition)
    return verb is not None and verb not in MODALS


def condition_fact(condition) -> bool:
    """`ItemFrames.fact(String)` (128 FR-13b, 129 FR-6): a condition with no modal, or one whose head is a *have* / *be*
    fact, and never a permission."""
    if condition is None or not str(condition).strip() or permission(condition):
        return False
    head = head_verb(condition)
    if head is not None and head in FACT_HEADS:
        return True
    if head is not None and head in MODALS:
        return False
    return not _MODAL_ANYWHERE.search(" " + _clause(str(condition)).lower() + " ")


def condition_kind(asked, label) -> str:
    """Spec 118 FR-4c(c) (keel-cloud 185 FR-1, `ItemFrames.conditionKind(asked, label)`): a Compatibility condition is a
    PERMISSION where either face says one (whatever else it says), else a FACT (`is_fact`), else an ABILITY -- which
    scale it is served: the registry's four, the fact's three (`FACT_ANSWERS`), the ability's four (`ABILITY_ANSWERS`)."""
    if permission(f"{asked or ''} {label or ''}"):
        return "PERMISSION"
    return "FACT" if is_fact(asked, label) else "ABILITY"


#: keel-cloud 225 FR-1 (`SavedList.KINDS`): the three kinds a Compatibility row's `kind` takes.
KINDS = ("ability", "fact", "permission")


def written_kind(kind) -> str | None:
    """keel-cloud 225 (`SavedList.kindOf`): a written kind as stored -- one of `KINDS`, lower-cased; else None."""
    text = None if kind is None else str(kind).strip().lower()
    return text if text in KINDS else None


def kind_of(kind, asked, label) -> str:
    """keel-cloud 225 FR-1 (`ItemFrames.kindOf(kind, asked, label)`; spec 141 FR-8): a row's kind, one reader -- the
    kind the writer wrote and code held, upper-cased as `condition_kind` says it, else 123's word test over both faces
    (every row stored before 225, and every row the founder reworded or added since). No `kind` is on any wire, so a
    mirror predicting a served item's labels or stem reads the served item where it can."""
    written = written_kind(kind)
    return written.upper() if written else condition_kind(asked if asked else label, label)


def opens_on_could(asked, label) -> bool:
    """keel-cloud 225 FR-1 (`ItemFrames.opensOnCould`): a row whose founder's face opens on *could* (*could forward ...*,
    *they could ...*) or whose stranger's face does (*could you have ...*)."""
    for face in (label, asked):
        if face is None or not str(face).strip():
            continue
        text = _clause(str(face)).lower()
        if text.startswith("could ") or re.match(r"^(?:they|you) could ", text):
            return True
    return False


def held_kind(item: dict) -> str:
    """keel-cloud 225 FR-1 (`ScreenResultApplier.heldKind`): the kind code keeps for one drafted Compatibility row -- the
    writer's, except that words naming an allower make it `permission`, and a could-row the word test reads an ability
    stays `ability` unless `kind_why` says otherwise; the word test where the writer wrote none."""
    label = item.get("label")
    asked = item.get("asked") if item.get("asked") and str(item.get("asked")).strip() else label
    words = condition_kind(asked, label)
    written = written_kind(item.get("kind"))
    if written is None:
        return words.lower()
    if words == "PERMISSION" and permission(f"{asked} {label}"):
        return "permission"
    if written != "ability" and words == "ABILITY" and opens_on_could(item.get("asked"), label) \
            and not str(item.get("kind_why") or "").strip():
        return "ability"
    return written


def is_fact(asked, label) -> bool:
    """keel-cloud `ItemFrames.fact(asked, label)` (129 FR-6, 131 FR-3), what `FollowUpComposer.lockFact` reads since 174
    FR-3: a Compatibility condition is a fact read off both its faces -- the stranger's `asked` and the founder's
    `label` -- since a fact is served the registry's four and no *Partly* says so any more."""
    both = f"{asked or ''} {label or ''}".strip()
    if condition_fact(both):
        return True
    if label is None or not str(label).strip():
        return False
    if past_fact(label) and (not permission(label) or not _has_modal(both)):
        return True
    if permission(label):
        return False
    return head_verb(label) in ("was", "were", "is", "are")


def _base_of_participle(participle: str) -> str | None:
    """keel-cloud 171 `SpokenCap.baseOfParticiple`."""
    if participle in _PARTICIPLES:
        return _PARTICIPLES[participle]
    sure = base_of_past(participle)
    if sure is not None:
        return sure
    return base_of_past_loose(participle) if participle.endswith("ed") else None


def leading_clause(step: str):
    """keel-cloud `SpokenCap.leadingClause` (132 FR-1): `(clause, question)` of a step stored with a leading clause
    before its question (*When the repair was done, would you speak ...*), else None."""
    if step is None or not str(step).strip():
        return None
    m = _LEADING_CLAUSE.match(_trim_end(step))
    if not m or len(m.group(1).strip().split()) < 2:
        return None
    return _belief_lower(m.group(1).strip()), m.group(2).strip()


def _present(clause: str) -> str:
    """keel-cloud `SpokenCap.present` (132 FR-1): a leading clause said in the present after the step."""
    text = _second_person(_belief_lower(clause.strip()))
    text = re.sub(r"(?i)\bwere\b", "are", re.sub(r"(?i)\bwas\b", "is", text))

    def turn(m):
        verb = m.group(1).lower()
        base = base_of_past_loose(verb) if (verb.endswith("ed") or base_of_past(verb) is not None) \
            and verb != "had" else None
        return "you " + (base or verb)
    return re.sub(r"(?i)\byou ([a-z]+)\b", turn, text)


def step(text: str) -> str:
    """keel-cloud 171 FR-4b (`SpokenCap.step`): the founder's step as Adoption friction's frame says it after *you'd*
    -- a base-form verb phrase in the second person: *you'd upload your ID card* -> *upload your ID card*, *You had to
    talk ...* -> *talk ...*, *You would have worn the glasses ... whenever you talked* -> *wear the glasses ...
    whenever you talk*, *When the repair was done, would you speak the fix into your phone* -> *speak the fix into your
    phone when the repair is done*, *to set it up, you'd upload ...* -> *upload ...*. English's small words and the
    verb tables code keeps, nothing else (spec 112 FR-1)."""
    if text is None or not str(text).strip():
        return text
    led = leading_clause(text)
    if led is not None:
        return step(led[1]) + " " + _present(led[0])
    out = _second_person(_trim_end(text))
    out = re.sub(r"(?i)^to [^,]+,\s*(?=(?:you'd|you would|you will|you'll|you)\s)", "", out, count=1)
    out = re.sub(r"(?i)^(?:would|will|could|can|do) you\s+", "", out, count=1)
    past = False
    perfect = re.fullmatch(r"(?i)(?:you'd|you would)\s+have\s+(?!to\b)([a-z]+)\b(.*)", out)
    if perfect and _base_of_participle(perfect.group(1).lower()) is not None:
        out = _base_of_participle(perfect.group(1).lower()) + perfect.group(2)
        past = True
    out = re.sub(r"(?i)^(?:you'd|you would|you will|you'll)\s+(?:have to\s+|need to\s+)?", "", out, count=1)
    out = re.sub(r"(?i)^(?:you\s+)?(?:had to|have to|has to|would have to|needed to|need to|needs to)\s+", "", out,
                 count=1)
    out = re.sub(r"(?i)^you\s+(?:could|can|should|might|may|must)\s+", "", out, count=1)
    you = re.fullmatch(r"(?i)you\s+([a-z']+)\b(.*)", out)
    if you:
        verb = you.group(1).lower()
        if verb in _BE_DO_HAVE:
            base = _BE_DO_HAVE[verb]
        elif verb in ("read", "put", "set", "cut", "let"):
            base = verb
        elif base_of_past(verb) is not None:
            base = base_of_past(verb)
        elif verb.endswith("ed"):
            base = base_of_past_loose(verb) or verb
        else:
            base = verb
        past = (base != verb and verb not in _BE_DO_HAVE) or verb in ("was", "were", "did", "had")
        out = base + you.group(2)
    said = out.strip().split()
    for i in range(1, len(said)):
        lower, before = said[i].lower(), said[i - 1].lower()
        a_past = (lower != "had" and (lower.endswith("ed") or base_of_past(lower) is not None)
                  and base_of_past_loose(lower) is not None and lower != "read")
        if a_past and (before == "you" or past and before == "and"):
            said[i] = base_of_past_loose(lower)
    return _belief_lower(" ".join(said))


def to_use(name: str | None, said_step: str) -> str:
    """keel-cloud 171 FR-4b (`ItemFrames.toUse`): *To use {name}, you'd {step}. Would you do that, or not?* -- *To use
    it, ...* where the idea has no name. Retires 130's *{Name} means {gerund}.* and 123's *You'd {asked}.*"""
    idea = "it" if name is None or not str(name).strip() else str(name).strip()
    return f"To use {idea}, you'd {said_step}. {ADOPTION_ASK}"


def question_part(asked: str) -> str | None:
    """keel-cloud `ItemFrames.questionPart` (132 FR-1): the question of a step stored as one, else None."""
    if asked is None or not str(asked).strip():
        return None
    led = leading_clause(asked)
    text = led[1] if led is not None else _clause(asked)
    return _belief_lower(text) if _ASKS_YOU.match(text) else None


def says_it(asked: str | None, name: str | None, label: str | None) -> str | None:
    """keel-cloud 171 FR-4 (`ItemFrames.saysIt`): `asked` with the idea's capitalised `name` said as *it* (*its* for
    *{name}'s* and *the {name} ...*) -- only where the founder's `label` does not carry the name (a row the founder
    typed with the brand keeps it); `asked` as it is otherwise."""
    if asked is None or name is None or not str(name).strip() or not str(name).strip()[0].isupper():
        return asked
    said = re.escape(str(name).strip())
    if not re.search(r"(?<![\w'])" + said + r"(?![\w])", asked) or (
            label is not None and re.search(r"(?i)(?<![\w'])" + said + r"(?![\w])", label)):
        return asked
    out = re.sub(r"(?i)\b(?:the|a|an)\s+" + said + r"(?=\s+[a-z])", "its", asked)
    out = re.sub(r"(?<![\w'])" + said + r"(?:'s|’s)", "its", out)
    return re.sub(r"(?<![\w'])" + said + r"(?![\w])", "it", out)


def _fitted(name: str | None, asked: str | None) -> str | None:
    """keel-cloud 171 FR-4b (`ItemFrames.fitted`): the first form of the step the frame holds to the spoken cap -- the
    step whole, then without a phrase set off by commas (131 FR-4), then a question's step without its leading clause
    (132 FR-1) -- or None. keel-cloud's `StrangerGrammar.fault` beside the cap is not mirrored (as before)."""
    if asked is None or not str(asked).strip():
        return None
    whole = step(_clause(asked))
    steps = [whole, re.sub(r",\s+[^,]+,\s+", " ", whole, count=1)]
    question = question_part(asked)
    if question is not None and leading_clause(asked) is not None:
        steps.append(step(question))
    for said in steps:
        framed_line = to_use(name, said)
        if words(framed_line) <= STEM_MAX_WORDS:
            return framed_line
    return None


def adoption_friction(asked: str | None, name: str | None = None, label: str | None = None) -> str:
    """keel-cloud 171 (`ItemFrames.adoptionFriction(asked, name, label)`, the lock's call): the stored clause with the
    idea's name said as *it* where the founder's row does not name it (`says_it`), framed named where a form of it fits
    20 words, else unnamed by the same give-way, else whole (`adoption_frame`) -- which the lock's hold then gives way
    to the founder's row (`vectors_script.adoption_statement`)."""
    if label is not None:
        asked = says_it(asked, name, label)
    if name is not None and str(name).strip() and asked is not None and str(asked).strip():
        fitted = _fitted(name, asked)
        if fitted is not None:
            return fitted
    fitted = _fitted(None, asked)
    return fitted if fitted is not None else adoption_frame(asked)


def adoption_frame(asked: str) -> str:
    """Spec 093 FR-4, spec 112 FR-1 (keel-cloud 171 FR-4b, `ItemFrames.adoptionFrame` as `AskedRules.framed` reads it):
    an Adoption friction clause as `K2` measures it -- *To use it, you'd {step}. Would you do that, or not?* around the
    **whole** step (`step`: a leading *would you* / *you'd* / *you had to* / *have to* / *need to* dropped, a past or a
    participle in base form, a leading clause moved to the end in the present, a clause's own *to ..., you'd* purpose
    dropped), no give-way -- so the harness and the cloud count the same words. (Before keel-cloud 171: *You'd ...* /
    *{asked}* in the second person, then the question.) 171's 10-word clause rule is the registry's option rule
    (`ADOPTION_CLAUSE_MAX_WORDS`), never a fault here."""
    return to_use(None, step(_clause(asked)))


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
    kept the model's *would you* and counted one word more than `ItemFrames`) -- since keel-cloud 171 *To use it, you'd
    {step}. Would you do that, or not?* around the whole step (spec 112 FR-1)."""
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
        # spec 093 FR-5: K3 judges the line as framed -- the frame's *you'd* addresses the person itself, so a
        # base-form clause (*open the app before picking the baby up*) reads to the stranger once framed; a clause
        # whose subject is someone or something else (*the cry ...*, *the room ...*) still does not. Spec 112 FR-1: the
        # step after keel-cloud 171's *To use it, you'd* is what is read (the frame's own *you'd* never counts for it)
        said_clause = question.rsplit(f". {ADOPTION_ASK}", 1)[0].split("you'd ", 1)[-1]
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


# ------------------------------------------------------------------- spec 111: the reveal said aloud (keel-cloud 176)

#: keel-cloud 176 FR-2 (`RevealWords.SPOKEN_NAMES_MAX = SpokenForm.MAX_OPTIONS`): the most names a spoken list holds --
#: the most labelled points a listener holds, §2's cap on the options a voice reads.
SPOKEN_NAMES_MAX = MAX_OPTIONS


def _spoken_list(names: list, join: str = "or") -> str:
    """`RevealWords.spokenList`: *A, B or C*; past `SPOKEN_NAMES_MAX` names, *A, B and others*."""
    if len(names) > SPOKEN_NAMES_MAX:
        return f"{names[0]}, {names[1]} and others"
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" {join} {names[-1]}"


def reveal_aloud(line):
    """Spec 111 FR-3 (keel-cloud 176 `RevealWords.aloud`, line for line): a reveal line as the AI interviewer says it --
    the founder's names are kept, the sound is held. A capitalised parenthesis of two or more names is said *, such as
    A, B or C* (with a closing comma where the sentence goes on: *into the PMS (OPERA Cloud, Sihot, Apaleo), handing* ->
    *into the PMS, such as OPERA Cloud, Sihot or Apaleo, handing*), another capitalised parenthesis as its words set off
    by commas; a list of names past `SPOKEN_NAMES_MAX`, in a parenthesis or bare, is said by its first two and *and
    others*. A lower-case parenthesis (*(or a front desk)*) is as typed; a line with neither is returned as it is. The
    written card is never read through this."""
    from .corpus import LIST_OF_NAMES, NAME, NAMES_IN_PARENTHESES, names_of  # noqa: PLC0415 (corpus is the M5 mirror)
    if line is None or not str(line).strip():
        return line
    line = str(line)
    out, last = [], 0
    for p in NAMES_IN_PARENTHESES.finditer(line):
        head = line[last:p.start()].rstrip()
        content = p.group()[1:-1].strip()
        listed = names_of(content)
        of_names = len(listed) >= 2 and all(re.fullmatch(NAME, n) for n in listed)
        out.append(head)
        if head:
            out.append(" " if head.endswith(",") else ", ")
        out.append("such as " + _spoken_list(listed) if of_names else content)
        rest = line[p.end():].lstrip()
        if rest and rest[0].isalnum():
            out.append(",")
        last = p.end()
    out.append(line[last:])

    def cut(m):
        listed = [m.group(1), *names_of(m.group(2)), m.group(3)]
        return _spoken_list(listed) if len(listed) > SPOKEN_NAMES_MAX else m.group()
    return LIST_OF_NAMES.sub(cut, "".join(out))


# ------------------------------------------------- spec 137 FR-2: keel-cloud 213's code-composed stranger words

def _spoken_words(text: str | None) -> int:
    """`SpokenForm.words`: whitespace-separated words."""
    return 0 if text is None or not str(text).strip() else len(str(text).split())


#: keel-cloud 213 FR-8 (`RespondentItems.commitmentOptions`): Commitment's third and fourth answers, the registry's.
COMMITMENT_PROBABLY_NOT = "Probably not"
COMMITMENT_NO = "No"


def commitment_answers(rows: list[str]) -> list[str]:
    """keel-cloud 213 FR-8 (`VectorsController.commitmentAnswers` over `RespondentItems.commitmentOptions`): the four
    answers strangers get on Commitment, as its Check row serves them -- *Yes, I'd {step}*, the soft yes (*Probably,
    after {smaller step} first* where the list carries one, else *Probably yes*), *Probably not*, *No*. A smaller step
    that restates the step itself (`ItemFrames.restatesTheStep`, not mirrored until spec 141) was read as one served; the walk
    holds the drawn four to the served `answers`, and this composition to the first and the last two. Since spec 141 FR-4
    (keel-cloud 221 FR-2) `restates_the_step` is mirrored: a smaller step that restates the step (its act too) is no
    soft yes of its own -- *Probably yes* -- and one naming another act is served."""
    steps = [str(r).strip() for r in rows or [] if r and str(r).strip()]
    if not steps:
        return []
    smaller = _lower(steps[1]) if len(steps) > 1 else None
    if restates_the_step(steps[0], smaller):
        smaller = None
    soft = second_yes(smaller) if smaller else PROBABLY_YES
    return [first_yes(steps[0]), soft, COMMITMENT_PROBABLY_NOT, COMMITMENT_NO]


#: keel-cloud 213 FR-8 (`VectorsController.COMMITMENT_NOTE`): the Check row's note where the step moves money nowhere.
COMMITMENT_NOTE = "Say where the money goes"


def commitment_note(step: str | None, name: str | None) -> str | None:
    """keel-cloud 213 FR-8 (`VectorsController.commitmentNote`): *Say where the money goes (into {Name}).* where the step
    moves the person's money and names no place it goes (`step_cost.moves_money_nowhere`: Palus' *move a small part of
    the reserve*), never a rewrite of the founder's step; None otherwise."""
    from . import step_cost as step_cost_mod                            # noqa: PLC0415
    if not step_cost_mod.moves_money_nowhere(step):
        return None
    return COMMITMENT_NOTE + ("." if not name or not str(name).strip() else f" (into {str(name).strip()}).")


def buyer_payer_at_price(role: str | None, name: str | None, price: str | None) -> str:
    """keel-cloud 213 FR-10a (`ItemFrames.buyerPayerAtPrice`): Buyer and payer's stranger stem at the founder's price --
    *Could you sign off on {what} yourself, or would {the role} have to agree?* -- a share first as *a fee of {share}*,
    then the share as asked, then the idea's name, then *it*, each within the 20 spoken words (Palus: *Could you sign off
    on about 0.25% of the balance a year yourself, or would the board have to agree?*); an up-front price says its
    period once."""
    from . import chain as chain_mod                                    # noqa: PLC0415
    who = "someone else" if role is None else chain_mod.the_role(role)
    idea = "it" if not name or not str(name).strip() else str(name).strip()
    said = None if price is None else re.sub(r",?\s+once$", "", str(price).strip(), count=1)
    fee = "a fee of " + re.sub(r"^about\s+", "", said, count=1) if said is not None and "%" in said else None
    for what in (fee, said, idea, "it"):
        if what is None or not what.strip():
            continue
        asked = f"Could you sign off on {what.strip()} yourself, or would {who} have to agree?"
        if _spoken_words(asked) <= STEM_MAX_WORDS:
            return asked
    return "Could you sign off on it yourself, or would someone else have to agree?"


#: keel-cloud 198 FR-8 (`ScaleFour.DONE_BETTER`): Relative advantage's tail after the idea, the job the anchor named.
DONE_BETTER = "have done that better for you, or not?"
_AT_STAKE_SMALL = frozenset({"the", "a", "an", "of", "on", "in", "at", "to", "for", "and", "or", "your", "their", "time",
                             "last", "day", "night", "week", "month"})


def _says_again(occasion: str | None, job: str | None) -> bool:
    """`ScaleFour.saysAgain` (keel-cloud 206 FR-4): whether the job says a content word of the occasion again."""
    if occasion is None or job is None:
        return False
    said = {w[:-1] if w.endswith("s") else w for w in re.split(r"[^a-z']+", job.lower())}
    for word in re.split(r"[^a-z']+", occasion.lower()):
        stem = word[:-1] if word.endswith("s") else word
        if word.strip() and word not in _AT_STAKE_SMALL and stem in said:
            return True
    return False


def at_stake(occasion: str | None, job: str) -> str:
    """`ScaleFour.atStake` (keel-cloud 198 FR-8): *Think of the last {occasion} when you had to {job}.*, *Think of the
    most recent time you had to {job}.* with no occasion noun -- the job in the second person."""
    from harness import loss_line as ll                                 # noqa: PLC0415 - `StrangerGrammar.secondPerson`
    from . import wording                                               # noqa: PLC0415 - it reads this module
    noun = None if occasion is None or not occasion.strip() or occasion.strip().lower() in ("time", "times") \
        else occasion.strip()
    doing = ll.second_person(re.sub(r"[.]+$", "", _lower(job.strip())), False)
    # keel-cloud 232 FR-7: the anchor through `ItemFrames.thinkOf` -- *last* said once where the noun opens on it
    return f"Think of the most recent time you had to {doing}." if noun is None else \
        wording.think_of("the", noun)[:-1] + f" when you had to {doing}."


def held_anchor(occasion: str | None, job: str) -> str | None:
    """`ScaleFour.heldAnchor` (keel-cloud 206 FR-4): the at-stake anchor held to the spoken cap by giving way -- the
    occasion and the job; the job without its trailing clause; *the most recent time*; None where none fits."""
    jobs = [job.strip()]
    trailing = re.match(r"(?i)^(.+?)\s+(?:until|without|so that|before|after|while|because|in order to)\s+.+$",
                        job.strip())
    if trailing and _spoken_words(trailing.group(1)) >= 3:
        jobs.append(trailing.group(1).strip())
    anchors = [] if _says_again(occasion, job) else [at_stake(occasion, doing) for doing in jobs]
    anchors += [at_stake(None, doing) for doing in jobs]
    return next((a for a in anchors if _spoken_words(a) <= STEM_MAX_WORDS), None)


def what_head(what: str) -> str | None:
    """keel-cloud 213 FR-6 (`ScaleFour.headOf`): a what-it-is's words before its first relative clause (*an AI
    reservation agent* of *an AI reservation agent that answers the calls nobody picks up*); None where it has none."""
    m = re.match(r"(?i)^(.+?)\s+(?:that|which|who|whose)\s+\S.*$", what.strip())
    return m.group(1).strip() if m and _spoken_words(m.group(1)) >= 2 else None


def hard_case(occasion: str | None, stem: str | None) -> str | None:
    """keel-cloud 214 FR-2 (`ScaleFour.hardCase`): the hard case the advantage is for -- *Think of the last {occasion}
    when {the stem's when clause}.*, *Think of the most recent time {clause}.* where the clause says the occasion's word
    again or there is no noun; None with no stem, no clause, or past the spoken cap."""
    from . import wording                                               # noqa: PLC0415 - it reads this module
    from . import writers_rules as writers_mod                          # noqa: PLC0415 - it reads this module
    if stem is None or not stem.strip():
        return None
    when = writers_mod.when_clause(stem)
    if when is None or not when.strip():
        return None
    when = re.sub(r"[.,;:!?]+$", "", when.strip()).strip()
    noun = None if occasion is None or not occasion.strip() or occasion.strip().lower() in ("time", "times") \
        else occasion.strip()
    again = set() if noun is None else set(writers_mod.roots(noun)) & set(writers_mod.roots(when))
    anchor = f"Think of the most recent time {when}." if noun is None or again else \
        wording.think_of("the", noun)[:-1] + f" when {when}."              # keel-cloud 232 FR-7
    return anchor if _spoken_words(anchor) <= STEM_MAX_WORDS else None


#: keel-cloud 219 (`HardCase.ITEM_LEAD`): the item's frame before the study's hard case, *Think of {hard_case}.*
HARD_CASE_LEAD = "Think of "


def hard_case_clean(field: str | None) -> str | None:
    """keel-cloud 219 (`HardCase.clean`): the field as served -- trimmed, runs of space as one, its trailing stops
    dropped, its first letter lowered (an acronym's capital kept); None with none."""
    if field is None or not str(field).strip():
        return None
    text = re.sub(r"[.,;:!?]+$", "", re.sub(r"\s+", " ", str(field).strip())).strip()
    return _lower(text) if text else None


def hard_case_said(field: str | None) -> str | None:
    """keel-cloud 219 (`HardCase.said`): the hard case as the item says it -- *the last time ...* said *the most recent
    time ...* (214's rule: *the last time* is 120's stem anchor); every other opening as written."""
    text = hard_case_clean(field)
    if text is None:
        return None
    return "the most recent time " + text[len("the last time "):] if text.lower().startswith("the last time ") else text


def hard_case_anchor(field: str | None) -> str | None:
    """keel-cloud 219 FR-4 (`HardCase.anchor`): *Think of {hard_case}.*; None with no field or past the spoken cap."""
    said = hard_case_said(field)
    if said is None:
        return None
    anchor = HARD_CASE_LEAD + said + "."
    return anchor if _spoken_words(anchor) <= STEM_MAX_WORDS else None


def advantage_stem(occasion: str | None, name: str | None, what_it_is: str | None, job: str | None,
                   stem: str | None = None, hard_case_field: str | None = None) -> str | None:
    """keel-cloud 213 FR-6 (`ScaleFour.question(occasion, stem, name, whatItIs, job)`): Relative advantage's stranger
    stem -- the anchor, then *Would {Name}, {what it is}, have done that better for you, or not?* as the card says: the
    whole what where the question fits the 20 spoken words, else the what cut by its trailing phrases (`cut_to_fit`),
    else its head (`what_head`); the bare name only where there is no what; *it* last. keel-cloud 214 FR-2: the anchor
    is the hard case (`hard_case`, the occasion stem's when clause), the job's at-stake anchor (`held_anchor`, 198 /
    206) only where there is no stem or it does not fit. None where no anchor fits (the cloud then serves 173's
    frame). keel-cloud 219 FR-4 (spec 141 FR-2; `ScaleFour.question(..., hardCase)`): the study's own hard case first,
    *Think of {hard_case}.* (`hard_case_anchor`), where it holds one that fits; then 214's, then 198's."""
    anchor = hard_case_anchor(hard_case_field)
    if anchor is None:
        anchor = hard_case(occasion, stem)
    if anchor is None and job is not None and job.strip():
        anchor = held_anchor(occasion, job)
    if anchor is None:
        return None
    named = None if not name or not name.strip() else name.strip()
    what = None if not what_it_is or not what_it_is.strip() else re.sub(r"[.,;:]+$", "", what_it_is.strip())
    ideas: list[str] = []
    if what is not None:
        whats = [what]
        room = STEM_MAX_WORDS - _spoken_words("Would " + DONE_BETTER) - (0 if named is None else _spoken_words(named))
        cut = cut_to_fit(what, max(1, room))
        if cut not in whats:
            whats.append(cut)
        head = what_head(what)
        if head is not None and head not in whats:
            whats.append(head)
        ideas += [f"{named}, {one}," if named is not None else one for one in whats]
    if named is not None and what is None:
        ideas.append(named)
    ideas.append("it")
    for idea in ideas:
        asked = f"Would {idea} {DONE_BETTER}"
        if _spoken_words(asked) <= STEM_MAX_WORDS:
            return anchor + " " + asked
    return None
