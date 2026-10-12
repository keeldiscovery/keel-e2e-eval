"""The calibration chat's marks (spec 035, `MARKS_VERSION` 17, judgement calls 76-80; keel-cloud 083).

Two screens, one job class (`calibration`, the standard tier): `CALIBRATION_CHAT` turns what a founder said
about one dimension into one measurable belief and writes the words of the one question strangers are asked;
`ITEM_FEEDBACK` makes a founder's change to the previewed item within the rules or refuses it naming one.

**What is keel-cloud's and what is restated.** `screenContracts validate` does not take either screen (no
`InferenceScreen.CALIBRATION_CHAT` in `ScreenContractTool`), so there is nothing to delegate to and nothing for a
parity test to compare with: the rules live in keel-cloud's `CalibrationChatRules` (CC1-CC8, C9, F1, F2) and
`ItemRules` (the five refusals), and this module restates them clause for clause, naming each. When the validator
takes the screens, `validate._SHAPE_MARKERS` already lists them and the batch starts carrying them; these marks then
stay as the corpus half (the expected measure, the expected follow-up, the leak of the founder's own words).

Six marks, each a pure function over the case and the model's answer:

- `one_measurable`: the COMPLETED answer carries one proposal of one kind in the dimension's `chat.measures`, the
  corpus's measure and family -- or `leave_out`, where the corpus says nothing fits (CC1, CC2, CC5-CC8).
- `follow_up_budget`: at most one NEEDS_INPUT, asked only where the corpus says one is expected; a needless
  follow-up and a missed one both fail (C9).
- `preview_rules`: what strangers will be shown stays code's -- the frame is the corpus's, no option the model wrote
  on a frame code builds, and a yes/no ends *..., or not?* (judged by structure only).
- `no_founder_leak`: no digit, number word, fraction word or run of the founder's own words in any respondent slot,
  and no idea word on a PROBLEM slot (LeakStems, extended to the founder's measure).
- `importance_list`: exactly six others, none naming the idea, none the problem in other words, no two the same
  thing (CC3, CC4).
- `feedback_obeys`: an allowed change is applied and nothing else changes; a forbidden request is refused with the
  right rule; the post-change item passes `ItemRules` (F1, F2, and `ItemRules.check` ported).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import yaml

from . import text as text_mod

MARKS = ("one_measurable", "follow_up_budget", "preview_rules", "no_founder_leak", "importance_list",
         "feedback_obeys")

SCREEN_CHAT = "CALIBRATION_CHAT"
SCREEN_FEEDBACK = "ITEM_FEEDBACK"
CHAT_SCREENS = (SCREEN_CHAT, SCREEN_FEEDBACK)

IDEAS_PATH = Path(__file__).parent / "chat_ideas.yaml"
FEEDBACK_PATH = Path(__file__).parent / "chat_feedback.yaml"

IMPORTANCE = "problem.importance"
#: `ItemFramer.OTHERS`: the problem plus exactly six others.
OTHERS = 6

#: `ItemRules.Rule`, as the wire names them.
RULES = ("SHOWS_NUMBER", "SHOWS_BELIEF", "LEADING_OPTION", "DROPS_ESCAPE", "CHANGES_FRAME")
#: `ItemRules.ESCAPES`, `SUPPORTING`, `BALANCED_FRAMES`, `REMOVABLE`.
ESCAPES = frozenset({"NONE", "CANT_TELL", "WORSE", "EXCLUDED", "ESCAPE"})
SUPPORTING = frozenset({"YES", "YES_CONDITIONAL", "PASS"})
BALANCED_FRAMES = frozenset({"balanced", "effort_yes_no"})
REMOVABLE = frozenset({"SOMEONE_ELSE", "ITEM"})
#: The frames whose options code builds whole (`ItemFramer`): a model-written `choices` on one is a model
#: writing a band, a range or an escape, which it never does.
CODE_BUILT_FRAMES = frozenset({"segmented_0_to_7", "band_ladder", "word_bands", "switch_threshold",
                               "balanced", "effort_yes_no", "how_often", "price_ladder", "cost_total"})
#: The frames whose options the model writes (a list's items, a chain, a step, a ladder, a fit point's places).
MODEL_LISTED_FRAMES = frozenset({"top_three", "single_pick", "furthest_rung", "fit_point"})
YES_NO_FRAMES = BALANCED_FRAMES

#: `CalibrationChatRules.MONEY`, **with the word ending it lacks**: keel-cloud's pattern is `\b(pay|...|plan|...)` with
#: no closing boundary, so *payroll*, *ordering* and *planning* all read as money and a payroll question about an
#: effort is refused CC5. The intent is money, not a word that starts like it; reported to keel-cloud, not copied.
MONEY = re.compile(r"\b(pay|pays|paid|paying|buy|buys|bought|purchase|price|cost|costs|subscribe|"
                   r"subscription|order|pre-order|plan)\b|[£$€]", re.IGNORECASE)
HABIT_FREQUENCIES = ("most_days", "few_week", "rarely")
PRICE_UNITS = ("PER_PERIOD", "PER_ITEM", "PER_SEAT", "PAID_TIER")

#: `ItemRules.numberWords()`.
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
                9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 15: "fifteen", 20: "twenty",
                30: "thirty", 40: "forty", 45: "forty-five", 60: "sixty", 90: "ninety"}
#: The founder's measure in words: every number word and fraction a founder says an amount with. `ItemRules`
#: knows the digits it was handed; the chat is handed only what was said, so this reads the saying.
_SAID_NUMBER_WORDS = frozenset(NUMBER_WORDS.values()) | {"zero", "thirteen", "fourteen", "sixteen", "seventeen",
                                                         "eighteen", "nineteen", "fifty", "seventy", "eighty",
                                                         "hundred", "thousand", "million", "dozen", "couple",
                                                         "half", "halves", "quarter", "quarters", "third",
                                                         "thirds", "fifth", "tenth", "double", "twice", "triple",
                                                         "thrice"}
#: A fraction the founder said, and the percentage it is also said as: `about half` is `50%` to a respondent.
_FRACTION_AS_PERCENT = {"half": "50", "halves": "50", "quarter": "25", "quarters": "25", "third": "33",
                        "thirds": "33", "tenth": "10", "fifth": "20", "double": "100", "twice": "100"}
_DIGITS = re.compile(r"\d[\d,]*(?:\.\d+)?")


# ----------------------------------------------------------------------------------------- the sheets

def ideas() -> dict:
    """The eval's own idea sheet (`chat_ideas.yaml`), by idea id."""
    return yaml.safe_load(IDEAS_PATH.read_text(encoding="utf-8")) or {}


def feedback_cases() -> list:
    """The eval's own `ITEM_FEEDBACK` cases (`chat_feedback.yaml`)."""
    document = yaml.safe_load(FEEDBACK_PATH.read_text(encoding="utf-8")) or {}
    return list(document.get("cases") or [])


# ------------------------------------------------------------------------------------------ the score

@dataclass
class ChatScore:
    case_id: str
    kind: str                       # CHAT | FEEDBACK
    marks: dict = field(default_factory=dict)       # mark -> True | False | None (does not apply / unmeasured)
    faults: list = field(default_factory=list)      # [(mark, why)]


def totals(scores) -> dict:
    """Each mark summed over the cases it applies to: `{mark: {hit, of}}`, a value, and whether it was measured.
    A mark no case reached stays `None` -- an unmeasured mark is not a met one (call 13)."""
    out = {"chat_cases": sum(1 for s in scores if s.kind == "CHAT"),
           "feedback_cases": sum(1 for s in scores if s.kind == "FEEDBACK")}
    for mark in MARKS:
        verdicts = [s.marks[mark] for s in scores if s.marks.get(mark) is not None]
        hit, of = sum(1 for v in verdicts if v), len(verdicts)
        out[mark] = (hit / of) if of else None
        out[f"{mark}_of"] = of
        out[f"{mark}_hit"] = hit
    return out


# --------------------------------------------------------------------------------------- text helpers

def _words(text) -> list:
    return re.findall(r"[a-z]+", (text or "").lower())


def _contains_run(haystack: list, needle: list) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    return any(haystack[i:i + len(needle)] == needle for i in range(len(haystack) - len(needle) + 1))


def _stems(text) -> set:
    return {text_mod.stem(w) for w in text_mod.content_words(text)}


def same_thing(a, b) -> bool:
    """`CalibrationChatRules.sameThing`: one's content stems all in the other's."""
    x, y = _stems(a), _stems(b)
    return bool(x) and bool(y) and (x >= y or y >= x)


def idea_word(text, idea_words) -> str | None:
    """`CalibrationChatRules.ideaWord`: the idea's own word whose stems all appear in `text`, or None."""
    stems = _stems(text)
    for word in idea_words or []:
        idea = _stems(word)
        if idea and stems >= idea:
            return word
    return None


def _clean(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def slots_of(proposal: dict) -> list:
    """The texts a stranger is shown that the model wrote: the question, the occasion, the list's items, the
    problem's own item, the none / conditional / someone-else labels and a tier's name."""
    out = []
    for key in ("question", "occasion", "own_item", "none_label", "condition_label", "someone_else", "tier"):
        text = _clean((proposal or {}).get(key))
        if text:
            out.append(text)
    out += [t for t in (_clean(c) for c in (proposal or {}).get("choices") or []) if t]
    return out


# ------------------------------------------------------------------------------------ one_measurable

def _proposal_of(result):
    """(proposal-or-None, faults): CC1 -- one proposal, never `proposals`, never two kinds."""
    if not isinstance(result, dict):
        return None, ["CC1: a completed chat carries one proposal, or leave_out"]
    if "proposals" in result:
        return None, ["CC1: one measure per dimension -- `proposals` was sent"]
    proposal = result.get("proposal")
    if not isinstance(proposal, dict):
        return None, ["CC1: a completed chat carries one proposal, or leave_out"]
    kind = proposal.get("kind")
    if isinstance(kind, list) and len(kind) != 1:
        return None, [f"CC1: one measure per dimension; {len(kind)} were given"]
    return proposal, []


def one_measurable(case, chat_block: dict, result) -> tuple:
    """`(passed, faults)`. `case` is a corpus `ChatCase`; `chat_block` the registry's `chat` for its dimension."""
    if case.leaves_out:
        leave = result.get("leave_out") if isinstance(result, dict) else None
        if isinstance(leave, dict) and not isinstance(result.get("proposal"), dict):
            return True, []
        return False, ["the corpus says nothing measurable fits: expected leave_out and no proposal"]
    proposal, faults = _proposal_of(result)
    if proposal is None:
        if isinstance(result, dict) and isinstance(result.get("leave_out"), dict):
            return False, [f"left out where the corpus measures it as {case.measure}"]
        return False, faults
    kind = proposal.get("kind")
    kind = kind[0] if isinstance(kind, list) else kind
    if kind not in (chat_block or {}).get("measures", []):
        faults.append(f"CC2: {case.dimension} is measured as one of {(chat_block or {}).get('measures')}, "
                      f"not {kind}")
    elif kind != case.measure:
        faults.append(f"the corpus expects {case.measure}, the proposal is {kind}")
    if case.family and proposal.get("family") != case.family:
        faults.append(f"the corpus expects family {case.family}, the proposal is {proposal.get('family')}")
    unit = proposal.get("unit")
    if case.dimension == "solution.adoption_friction":
        if unit == "money" or MONEY.search(" ".join(filter(None, [_clean(proposal.get("question")),
                                                                  _clean(proposal.get("claim"))]))):
            faults.append("CC5: money is never an effort -- it is tested on price")
        if proposal.get("family") == "HABIT" and proposal.get("habit_frequency") not in HABIT_FREQUENCIES:
            faults.append(f"CC8: a habit carries how often the founder expects it: one of {HABIT_FREQUENCIES}")
    if case.dimension == "commercial.commitment":
        steps = [s for s in (proposal.get("choices") or []) if _clean(s)]
        if steps:
            for step in steps[:-1]:
                if MONEY.search(step):
                    faults.append(f"CC6: money is on the last step only; '{step}' is earlier")
            if not MONEY.search(steps[-1]):
                faults.append(f"CC6: the ladder ends in money; '{steps[-1]}' involves none")
    if case.dimension == "commercial.price":
        unit_word = proposal.get("price_unit")
        if unit_word not in PRICE_UNITS:
            faults.append(f"CC7: a price names how it is sold -- {PRICE_UNITS}")
        elif unit_word == "PER_ITEM" and not (isinstance(proposal.get("items_per_period"), (int, float))
                                               and proposal["items_per_period"] > 0):
            faults.append("CC7: a price per item needs how many a buyer gets per period")
    if not _clean(proposal.get("question")):
        faults.append("a proposal carries the one question strangers are asked")
    return not faults, faults


# ----------------------------------------------------------------------------------- follow_up_budget

def follow_up_budget(case, outcomes) -> tuple:
    """`(passed, faults)`. `outcomes` is the model's NEEDS_INPUT / COMPLETED sequence over the chat, with the
    questions of each NEEDS_INPUT as `("NEEDS_INPUT", n_questions)` or the bare word. At most one is asked (C9);
    exactly when the corpus expects one."""
    asked = [o for o in outcomes if (o[0] if isinstance(o, tuple) else o) == "NEEDS_INPUT"]
    faults = []
    if len(asked) > 1:
        faults.append(f"C9: {len(asked)} follow-ups; at most one")
    for o in asked:
        if isinstance(o, tuple) and o[1] != 1:
            faults.append(f"a follow-up is one question; this one asked {o[1]}")
    if len(asked) <= 1:
        if case.follow_up and not asked:
            faults.append("a follow-up was expected (two things named, or no number or unit) and none was asked")
        if asked and not case.follow_up:
            faults.append("a needless follow-up: the corpus names one measure with a number and a unit")
    return not faults, faults


# ------------------------------------------------------------------------------------- preview_rules

def preview_rules(case, chat_block: dict, result) -> tuple:
    """The respondent slots keep to what code frames. Restates `ItemRules` on a proposal rather than on an item:
    the frame is the corpus's and untouched, the model wrote no option on a frame code builds (no band, range or
    escape of its own), and a yes/no ends *..., or not?* with nothing written on its side."""
    proposal = result.get("proposal") if isinstance(result, dict) else None
    if case.leaves_out:
        return not isinstance(proposal, dict), [] if not isinstance(proposal, dict) else \
            ["a left-out dimension shows strangers nothing"]
    if not isinstance(proposal, dict):
        return False, ["no proposal, so nothing to preview"]
    faults = []
    kind = proposal.get("kind")
    kind = kind[0] if isinstance(kind, list) else kind
    frames = ((chat_block or {}).get("respondent") or {}).get("frames") or {}
    frame = frames.get("HABIT") if proposal.get("family") == "HABIT" else frames.get(kind)
    if frame != case.respondent:
        faults.append(f"CHANGES_FRAME: the kind of question is code's: {case.respondent}, not {frame}")
    choices = [c for c in (proposal.get("choices") or []) if _clean(c)]
    if case.respondent in CODE_BUILT_FRAMES and choices:
        faults.append(f"CHANGES_FRAME: code builds {case.respondent}'s answers; the model wrote {len(choices)}")
    if case.respondent in YES_NO_FRAMES:
        question = (_clean(proposal.get("question")) or "").lower()
        if not question.endswith(", or not?"):
            faults.append('LEADING_OPTION: a yes-or-no question ends "..., or not?" so neither answer '
                          'sounds like the expected one')
    for label_key in ("none_label", "condition_label", "someone_else"):
        label = (_clean(proposal.get(label_key)) or "")
        if re.search(r"\d", label):
            faults.append(f"CHANGES_FRAME: '{label}' carries a number; code writes every number")
    return not faults, faults


# -------------------------------------------------------------------------------------- no_founder_leak

def founder_numbers(*texts) -> list:
    """What the founder said an amount with, as a respondent could read it back: every digit run, every number
    word and fraction word -- and the percentage a fraction is also said as (*half* is *50%*)."""
    found = []
    for text in texts:
        for run in _DIGITS.findall(text or ""):
            found.append(run.replace(",", ""))
        for word in _words(text):
            if word in _SAID_NUMBER_WORDS:
                found.append(word)
                if word in _FRACTION_AS_PERCENT:
                    found.append(_FRACTION_AS_PERCENT[word])
    seen, out = set(), []
    for item in found:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _slot_numbers(text, numbers) -> str | None:
    """The first of the founder's numbers a slot carries, as digits (a whole token, as `ItemRules.numberIn`
    reads) or as a word."""
    lower = (text or "").lower()
    tokens = [t.rstrip(".") for t in re.split(r"[^0-9a-z.]+", lower) if t]
    words = _words(lower)
    for number in numbers:
        if number.isdigit() or re.fullmatch(r"\d+\.\d+", number):
            if number in tokens or number in [t.replace(",", "") for t in re.findall(r"\d[\d,]*(?:\.\d+)?", lower)]:
                return number
        elif number in words:
            return number
        elif "-" in number and _contains_run(words, _words(number)):
            return number
    return None


def _belief_runs(text) -> list:
    """Every run of three or more words of the founder's own saying that has at least two content words: a run
    `ItemRules.SHOWS_BELIEF` would call the belief's own words."""
    words = _words(text)
    runs = []
    for size in (3, 4, 5):
        for i in range(len(words) - size + 1):
            run = words[i:i + size]
            if sum(1 for w in run if w not in text_mod.STOPLIST and len(w) >= 3) >= 2:
                runs.append(run)
    return runs


def no_founder_leak(case, idea_words, result, context_words=()) -> tuple:
    """`(passed, faults)` over every slot the model wrote for strangers."""
    proposal = result.get("proposal") if isinstance(result, dict) else None
    if not isinstance(proposal, dict):
        return True, []        # nothing is shown
    slots = slots_of(proposal)
    numbers = founder_numbers(case.founder)
    runs = _belief_runs(" ".join(filter(None, [case.founder, _clean((result or {}).get("belief_draft")),
                                               _clean(proposal.get("claim"))])))
    # The founder's own words are the answer's items when the answer is a list, a chain, a step or a ladder, so the
    # belief is read in the sentences strangers are asked, never in the options the founder named.
    sentences = {_clean(proposal.get("question")), _clean(proposal.get("occasion"))}
    faults = []
    for slot in slots:
        hit = _slot_numbers(slot, numbers)
        if hit:
            faults.append(f"SHOWS_NUMBER: '{hit}' is the founder's own number, in '{slot}'")
        slot_words = _words(slot)
        for run in runs if slot in sentences else ():
            if _contains_run(slot_words, run):
                faults.append(f"SHOWS_BELIEF: '{' '.join(run)}' is the founder's own saying, in '{slot}'")
                break
        if case.dimension.startswith("problem."):
            word = idea_word(slot, idea_words)
            if word:
                faults.append(f"names the idea ('{word}') in a PROBLEM slot: '{slot}'")
    return not faults, faults


# --------------------------------------------------------------------------------------- importance_list

def importance_list(case, idea_words, result) -> tuple:
    """CC3, CC4 and the near-neighbour merge: exactly six others, none naming the idea, none the problem in other
    words, no two the same thing."""
    proposal = result.get("proposal") if isinstance(result, dict) else None
    if not isinstance(proposal, dict):
        return False, ["no proposal, so no list"]
    choices = [c for c in (proposal.get("choices") or []) if _clean(c)]
    own = _clean(proposal.get("own_item"))
    faults = []
    if len(choices) != OTHERS:
        faults.append(f"CC3: Importance lists the problem plus exactly six others; {len(choices)} were given")
    if not own:
        faults.append("CC3: the problem is one part of the job (own_item), and it was not sent")
    for index, item in enumerate(choices):
        word = idea_word(item, idea_words)
        if word:
            faults.append(f"CC4: '{item}' names the idea ('{word}')")
        if own and same_thing(own, item):
            faults.append(f"CC4: '{item}' is the problem in other words")
        for other in choices[index + 1:]:
            if same_thing(item, other):
                faults.append(f"near-neighbours not merged: '{item}' and '{other}'")
    return not faults, faults


# ----------------------------------------------------------------------------------------- ItemRules

def _option_map(item) -> dict:
    return {o["code"]: o for o in item.get("options") or []}


def item_check(reference: dict, candidate: dict, *, numbers=(), claim=None, addable=()) -> tuple | None:
    """`ItemRules.check`, clause for clause and in its order: `(RULE, said)` for the first rule `candidate` breaks
    against `reference` and the founder's numbers and belief, else `None`."""
    frame = reference.get("frame")
    if frame != candidate.get("frame", frame):
        return "CHANGES_FRAME", "the kind of question is code's"
    before, after = _option_map(reference), _option_map(candidate)
    for option in reference.get("options") or []:
        if option.get("kind") in ESCAPES and option["code"] not in after:
            return "DROPS_ESCAPE", f"'{option['label']}' stays"
    for option in candidate.get("options") or []:
        if option["code"] in before:
            continue
        kind = option.get("kind")
        if kind in SUPPORTING:
            return "LEADING_OPTION", f"'{option['label']}' adds an answer on your side"
        if kind is None or frame is None or kind not in set(addable):
            return "CHANGES_FRAME", f"'{option['label']}' isn't a kind of answer this question takes"
    bands_before = [o["code"] for o in reference.get("options") or [] if o.get("kind") == "BAND"]
    bands_after = [o["code"] for o in candidate.get("options") or [] if o.get("kind") == "BAND"]
    if bands_before != bands_after:
        return "CHANGES_FRAME", "the ranges are built around your number; they can't be changed"
    for code in bands_before:
        if before[code]["label"] != after[code]["label"]:
            return "CHANGES_FRAME", "the ranges are built around your number; they can't be relabelled"
    for option in reference.get("options") or []:
        kind = option.get("kind")
        if kind is not None and kind not in ESCAPES and kind not in REMOVABLE and kind != "BAND" \
                and option["code"] not in after:
            return "CHANGES_FRAME", f"'{option['label']}' is one of the answers this kind of question always offers"
    if frame in BALANCED_FRAMES:
        yes = sum(1 for o in candidate["options"] if o.get("kind") in ("YES", "YES_CONDITIONAL"))
        no = sum(1 for o in candidate["options"] if o.get("kind") in ("PROBABLY_NOT", "NO"))
        if yes != no:
            return "LEADING_OPTION", f"a yes-or-no question offers two answers each way; this one offers {yes} yes and {no} no"
        if not (candidate.get("question") or "").strip().lower().endswith(", or not?"):
            return "LEADING_OPTION", 'a yes-or-no question ends "..., or not?"'
    texts = [candidate.get("question") or ""] + [o["label"] for o in candidate.get("options") or []
                                                 if o.get("kind") != "BAND"]
    for text in texts:
        number = number_in(text, numbers)
        if number:
            return "SHOWS_NUMBER", f"'{number}' is your own number"
    if claim:
        run = _words(claim)
        for text in texts:
            if len(run) >= 3 and _contains_run(_words(text), run):
                return "SHOWS_BELIEF", f'it says what you believe ("{claim}")'
    return None


def _plain(number) -> str:
    d = Decimal(str(number)).normalize()
    return format(d, "f")


def number_in(text, numbers) -> str | None:
    """`ItemRules.numberIn`: the first of the founder's numbers a text carries, as digits or as a word."""
    if not text:
        return None
    lower = text.lower()
    tokens = [t for t in re.split(r"[^0-9a-z.]+", lower) if t]
    for number in numbers:
        digits = _plain(number)
        for token in tokens:
            bare = token[:-1] if token.endswith(".") else token
            if bare == digits:
                return digits
        if Decimal(str(number)) == Decimal(str(number)).to_integral_value():
            word = NUMBER_WORDS.get(int(Decimal(str(number))))
            if word and _contains_run(_words(lower), _words(word)):
                return word
    return None


def apply_change(item: dict, change: dict) -> dict:
    """`CalibrationChatRules.candidate`: the item with the feedback's changes -- the question, labels by code, one
    option added or removed."""
    change = change or {}
    question = _clean(change.get("question")) or item.get("question")
    labels = {e["code"]: e["label"] for e in change.get("labels") or []
              if isinstance(e, dict) and e.get("code") and e.get("label")}
    remove = _clean(change.get("remove_option"))
    options = []
    for option in item.get("options") or []:
        if option["code"] == remove:
            continue
        options.append({**option, "label": labels.get(option["code"], option["label"])})
    add = change.get("add_option")
    if isinstance(add, dict) and _clean(add.get("label")):
        kind = add.get("kind")
        code = "something_else_person" if kind == "SOMEONE_ELSE" else f"added_{len(options) + 1}"
        options.append({"code": code, "label": add["label"].strip(), "kind": kind})
    return {**item, "question": question, "options": options}


# --------------------------------------------------------------------------------------- feedback_obeys

def feedback_obeys(case: dict, result) -> tuple:
    """`(passed, faults)` for one `ITEM_FEEDBACK` case: F1 (it says what it did), F2 (a refusal names a rule), an
    allowed change applied and nothing else changed, a forbidden request refused with the right rule, and the
    post-change item passing `ItemRules` whatever the model said (D3)."""
    faults = []
    if not isinstance(result, dict) or not _clean(result.get("said")):
        return False, ["F1: a feedback result says what changed, or why not"]
    refused = result.get("refused")
    rule = refused.get("rule") if isinstance(refused, dict) else None
    if rule is not None and rule not in RULES:
        return False, [f"F2: '{rule}' is not one of {RULES}"]
    expect = case["expect"]
    item = {**case["item"], "frame": case["frame"]}
    if expect["outcome"] == "refuse":
        if rule != expect["rule"]:
            faults.append(f"refused {rule or 'nothing'}; the right rule is {expect['rule']}")
        if result.get("change"):
            candidate = apply_change(item, result["change"])
            if item_check(item, candidate, numbers=case.get("founder_numbers") or (),
                          claim=case.get("claim"), addable=case.get("addable") or ()) is None \
                    and candidate != item:
                faults.append("the forbidden request was applied beside the refusal")
        return not faults, faults
    # an allowed change
    if rule is not None:
        return False, [f"refused {rule} an allowed change: nothing was applied"]
    change = result.get("change")
    if not isinstance(change, dict) or not change:
        return False, ["an allowed change was asked for and none was made"]
    candidate = apply_change(item, change)
    broken = item_check(item, candidate, numbers=case.get("founder_numbers") or (),
                        claim=case.get("claim"), addable=case.get("addable") or ())
    if broken:
        faults.append(f"{broken[0]}: the changed item breaks a rule the model should have refused")
    before, after = _option_map(item), _option_map(candidate)
    added = [o for code, o in after.items() if code not in before]
    removed = [code for code in before if code not in after]
    relabelled = [code for code in before if code in after and before[code]["label"] != after[code]["label"]]
    reworded = candidate.get("question") != item.get("question")
    want = expect.get("change") or {}
    if bool(want.get("reword")) != reworded:
        faults.append("the question was reworded" if reworded else "the question was to be reworded and was not")
    want_add = [want["add_kind"]] if want.get("add_kind") else []
    if [o.get("kind") for o in added] != want_add:
        faults.append(f"added {[o.get('kind') for o in added]}; expected {want_add}")
    if sorted(removed) != sorted(want.get("remove") or []):
        faults.append(f"removed {removed}; expected {want.get('remove') or []}")
    if sorted(relabelled) != sorted(want.get("relabel") or []):
        faults.append(f"relabelled {relabelled}; expected {want.get('relabel') or []}")
    return not faults, faults


# ------------------------------------------------------------------------------------------ scoring

def score_chat(case, chat_block: dict, idea_words, outcome, result, *, questions=0, failed=None) -> ChatScore:
    """One answered `CALIBRATION_CHAT` case. The chat is one call here: a NEEDS_INPUT is the follow-up asked, and
    the reply to it is not scripted (T012), so the marks that read a proposal are unmeasured on that case."""
    score = ChatScore(case_id=case.case_id, kind="CHAT")
    sequence = [("NEEDS_INPUT", questions)] if outcome == "NEEDS_INPUT" else ["COMPLETED"] if outcome else []

    def put(mark, verdict):
        passed, why = verdict
        score.marks[mark] = bool(passed)
        score.faults += [(mark, w) for w in why]

    if failed or not outcome:
        for mark in ("one_measurable", "follow_up_budget", "preview_rules", "no_founder_leak"):
            score.marks[mark] = False
        if case.dimension == IMPORTANCE:
            score.marks["importance_list"] = False
        score.faults.append(("one_measurable", f"no answer: {failed or 'no outcome'}"))
        return score
    put("follow_up_budget", follow_up_budget(case, sequence))
    if outcome == "COMPLETED":
        put("one_measurable", one_measurable(case, chat_block, result))
        put("preview_rules", preview_rules(case, chat_block, result))
        put("no_founder_leak", no_founder_leak(case, idea_words, result))
        if case.dimension == IMPORTANCE and not case.leaves_out:
            put("importance_list", importance_list(case, idea_words, result))
    return score


def score_feedback(case: dict, outcome, result, *, failed=None) -> ChatScore:
    score = ChatScore(case_id=case["id"], kind="FEEDBACK")
    if failed or outcome != "COMPLETED":
        score.marks["feedback_obeys"] = False
        score.faults.append(("feedback_obeys", f"no answer: {failed or outcome or 'no outcome'}"))
        return score
    passed, why = feedback_obeys(case, result)
    score.marks["feedback_obeys"] = bool(passed)
    score.faults += [("feedback_obeys", w) for w in why]
    return score
