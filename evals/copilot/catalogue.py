"""Spec 151 FR-2: the catalogue, as data -- the founder's habits and the respondent's behaviours of the methodology
page (2026-11-10), each a kind with its truth rule, so the scorer needs no per-script judgement.

A kind says: its side, the item kinds it applies to, the first round it can appear in, the verdict (founder) or tier
(respondent) it produces, the state the box is in after it, whether the founder offered Keel's options while asking
(B's two bars), and the **mechanical rule** the script writer's output is checked against offline (`validate`). A kind
whose truth is a matter of meaning (a reworded window, a leading tone) has no rule on its words: its truth is checked
for consistency (the verdict on the turn is the kind's) and the founder's reviewer reads a sample (`SAMPLE=20`). Which
kinds have a rule on the words is `WORD_RULES`; which do not, and why, is `NO_WORD_RULE`.

No trade, company or study words anywhere here: the examples are shapes, the questionnaire supplies the words.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: A's verdicts on a founder turn (the page's list, the spec's names), and `back_channel` / `nothing`.
VERDICTS = ("as_written", "same_meaning", "options_own_words", "meaning_changed", "stacked", "leading", "follow_up",
            "own_note", "back_channel", "nothing")
#: The verdicts that say *a Keel question was asked*.
QUESTION_VERDICTS = ("as_written", "same_meaning", "options_own_words", "meaning_changed", "stacked", "leading")
#: Meaning kept: as written or reworded; A's first bar reads these two as one.
MEANING_KEPT = ("as_written", "same_meaning")
#: The AI interviewer's three tiers (keel-cloud's classifier says high / medium / low: read onto these in order).
TIERS = ("sure", "likely", "unsure")
CONFIDENCE_TIER = {"high": "sure", "medium": "likely", "low": "unsure"}
#: The box's states.
STATES = ("listening", "answered", "follow_up", "note", "paused", "done")
SPEAKERS = ("founder", "them")
ITEM_KINDS = ("gate", "single", "multi", "number", "free")
CLOSED = ("gate", "single", "multi", "number")
WITH_OPTIONS = ("gate", "single", "multi")


@dataclass(frozen=True)
class Kind:
    name: str
    side: str                                   # founder | them
    describe: str                               # what the writer is told (a shape, no trade words)
    applies_to: tuple = ITEM_KINDS
    first_round: int = 1
    verdict: str | None = None                  # founder: the verdict on its turn; them: None (or nothing/follow_up)
    tier: str | None = None                     # them: the tier of the answer read; founder: a cap on it
    state_after: str | None = None
    offers_options: bool | None = None          # founder asking kinds: were Keel's options offered
    asking: bool = False                        # founder: the turn asks a Keel question
    needs: tuple = ()                           # a respondent kind it must meet (clarifying needs counter_question)
    word_rule: bool = False                     # a mechanical rule on the turn's words (validate)
    extra: dict = field(default_factory=dict)


FOUNDER = {k.name: k for k in [
    Kind("verbatim", "founder", "reads Keel's spoken question exactly as written (the stem; the anchor first when "
         "there is one)", verdict="as_written", state_after="listening", offers_options=True, asking=True,
         word_rule=True),
    Kind("light_reword", "founder", "asks the same question in slightly different words, the time window and the "
         "subject kept", verdict="same_meaning", state_after="listening", offers_options=False, asking=True,
         word_rule=True),
    Kind("options_own_words", "founder", "asks the question and offers the options in their own words, none of "
         "Keel's option labels said as written", applies_to=WITH_OPTIONS, verdict="options_own_words",
         state_after="listening", offers_options=True, asking=True, word_rule=True),
    Kind("options_reordered_or_missing", "founder", "offers the options in a different order, or leaves one out",
         applies_to=WITH_OPTIONS, verdict="options_own_words", state_after="listening", offers_options=True,
         asking=True, word_rule=True),
    Kind("story_prompt", "founder", "asks for a story instead of the question (\"walk me through the last time...\"); "
         "the answer is read from the story", verdict="same_meaning", tier="likely", state_after="listening",
         offers_options=False, asking=True, word_rule=True),
    Kind("meaning_changed", "founder", "asks something close but drops or changes what makes it Keel's question (the "
         "time window, the subject, the number)", verdict="meaning_changed", tier="likely", state_after="listening",
         offers_options=False, asking=True),
    Kind("preface", "founder", "rambles a preface, then reads the question as written", verdict="as_written",
         state_after="listening", offers_options=True, asking=True, word_rule=True),
    Kind("stacked", "founder", "asks two of Keel's questions in one breath", verdict="stacked", state_after="listening",
         offers_options=False, asking=True, extra={"items_needed": 2}),
    Kind("leading", "founder", "asks the question so it suggests the answer (\"you do that every time, right?\")",
         verdict="leading", state_after="listening", offers_options=False, asking=True),
    Kind("restart", "founder", "starts the question, breaks off (marked with ...), and starts again",
         verdict="as_written", state_after="listening", offers_options=True, asking=True, word_rule=True),
    Kind("clarifying", "founder", "after the respondent asks what they mean, explains the question -- still the same "
         "question, not a new one", verdict="same_meaning", state_after="listening", needs=("counter_question",),
         word_rule=True),
    Kind("follow_up", "founder", "after the answer, digs into it (\"why is that?\"); tagged to the question just asked",
         first_round=2, verdict="follow_up", state_after="follow_up", word_rule=True),
    Kind("follow_ups_in_a_row", "founder", "two or three follow-ups in a row, each with its reply, all under the same "
         "question", first_round=2, verdict="follow_up", state_after="follow_up", word_rule=True),
    Kind("own_note", "founder", "talks about something that belongs to no Keel question", verdict="own_note",
         state_after="note", word_rule=True),
    Kind("any_order", "founder", "asks the questions in an order other than Keel's", first_round=2, word_rule=True),
    Kind("went_back", "founder", "after another question, goes back and asks an earlier one again", first_round=2,
         verdict="same_meaning", state_after="listening", asking=True, offers_options=False, word_rule=True),
    Kind("answered_for_them", "founder", "says the answer for the respondent (\"so that's a yes, basically\") -- not "
         "the respondent's answer", verdict="nothing", word_rule=True),
    Kind("back_channel", "founder", "small talk or back-channel (\"right, okay, yeah\"); opens nothing",
         verdict="back_channel", word_rule=True),
]}

RESPONDENT = {k.name: k for k in [
    Kind("straight", "them", "answers plainly and briefly", tier="sure", state_after="answered", word_rule=True),
    Kind("story_first", "them", "tells a story first and gives the answer only at the end", tier="sure",
         state_after="answered", word_rule=True),
    Kind("hedged", "them", "answers with a hedge or an exception kept (\"mostly, not always\")", applies_to=CLOSED,
         tier="likely", state_after="answered"),
    Kind("late_negation", "them", "starts one way and corrects to the other at the end; the correction wins",
         applies_to=CLOSED, tier="sure", state_after="answered", word_rule=True),
    Kind("number_for_yes_no", "them", "answers a yes-or-no question with a count (\"four times, maybe five\")",
         applies_to=("gate",), tier="sure", state_after="answered", word_rule=True),
    Kind("different_question", "them", "answers a different question; nothing to read -- ask again",
         applies_to=CLOSED, tier="unsure", state_after="listening", word_rule=True),
    Kind("counter_question", "them", "asks what the founder means; no answer yet", tier=None, state_after="listening",
         word_rule=True),
    Kind("interrupted", "them", "is talked over mid-answer (the turn breaks off, marked with --); unsure unless the "
         "words are clear", applies_to=CLOSED, tier="unsure", state_after="listening", word_rule=True),
    Kind("two_voices", "them", "a second person on their side answers; not the respondent's answer, kept as a note",
         tier=None, state_after=None, word_rule=True),
]}

KINDS = {**FOUNDER, **RESPONDENT}
#: Kinds shown by the script's shape, not by one turn (the order the questions are asked in).
SCRIPT_KINDS = ("any_order",)
#: The founder kinds that ask; the others need an asking turn of their own around them.
ASKING = tuple(k for k, v in FOUNDER.items() if v.asking and k != "went_back")
#: Round 2's follow-up kinds (drawn so each is covered).
FOLLOW_UP_KINDS = ("follow_up", "follow_ups_in_a_row", "answered_for_them", "back_channel", "any_order", "went_back",
                   "own_note")
ANSWER_KINDS = tuple(k for k in RESPONDENT)

WORD_RULES = tuple(k for k, v in KINDS.items() if v.word_rule)
NO_WORD_RULE = {
    "meaning_changed": "whether the window, the subject or the number was dropped is a question of meaning; checked "
                       "only that the turn is not the stem and carries the verdict, then read by the reviewer",
    "stacked": "two questions in one breath has no reliable mark in the words (one question mark, an 'and' that "
               "may be inside one question); the verdict is checked, the reviewer reads it",
    "leading": "a leading tone is meaning, not form; the verdict is checked, the reviewer reads it",
    "hedged": "a hedge is meaning; checked only through its tier (likely) and a read option",
}


def expected_tier(founder_kind: str | None, respondent_kind: str) -> str | None:
    """The tier an answer must be read at: the respondent's kind's, capped by the founder kind that asked (a story
    prompt or a changed meaning cannot be read *sure*)."""
    tier = RESPONDENT[respondent_kind].tier
    cap = FOUNDER[founder_kind].tier if founder_kind in FOUNDER else None
    if tier is None or cap is None:
        return tier
    return max(tier, cap, key=TIERS.index)


def applicable(kind: str, item: dict, *, round_: int, n_items: int = 1) -> bool:
    k = KINDS[kind]
    if item["kind"] not in k.applies_to or round_ < k.first_round:
        return False
    return n_items >= k.extra.get("items_needed", 1)


# ------------------------------------------------------------------------------------------------ the words

def norm(s: str | None) -> str:
    """Lower case, curly quotes straightened, every mark but letters, digits, `$` and `'` dropped, spaces collapsed."""
    s = (s or "").lower().replace("’", "'").replace("‘", "'")
    s = re.sub(r"[^a-z0-9$' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def says(text: str, label: str) -> bool:
    """The label said as written, whole words."""
    lab = norm(label)
    return bool(lab) and re.search(r"(?<![a-z0-9$'])" + re.escape(lab) + r"(?![a-z0-9'])", norm(text)) is not None


def stems(item: dict) -> list[str]:
    sp = item.get("spoken") or {}
    stem = sp.get("stem") or item.get("question") or ""
    out = [stem]
    if sp.get("anchor"):
        out.append(f"{sp['anchor']} {stem}")
    if item.get("question") and item["question"] not in out:
        out.append(item["question"])
    return out


BREAK = re.compile(r"(\.\.\.|…|\s--|—|\bsorry\b)", re.I)
CUT = re.compile(r"(--|—|\.\.\.|…)\s*$")
CORRECTION = re.compile(r"\b(no|not|actually|wait)\b", re.I)
NUMBER = re.compile(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|once|twice)\b",
                    re.I)

#: Round lengths (seconds, the last turn's start): R1 under a minute, R2 two to four, R3 twelve to thirty, R4 45-60.
ROUND_SECONDS = {1: (0, 60), 2: (60, 240), 3: (600, 1800), 4: (2700, 3600)}


# ------------------------------------------------------------------------------------------- the validation

def _option_faults(item: dict, option) -> list[str]:
    if option is None:
        return []
    if not isinstance(option, dict):
        return ["option is not an object"]
    if "any" in option:
        return [f for o in option["any"] for f in _option_faults(item, o)]
    keys = set(option)
    if keys == {"unclear"} and option["unclear"] is True:
        return []
    if keys == {"escape"} and option["escape"] is True:
        return [] if item.get("escape") else ["escape on an item with no escape"]
    if keys == {"value"}:
        return [] if item["kind"] == "number" and isinstance(option["value"], (int, float)) else ["value on a "
                                                                                                 "non-number item"]
    if keys == {"picks"}:
        n = len(item.get("options") or [])
        picks = option["picks"]
        if item["kind"] not in WITH_OPTIONS or not isinstance(picks, list) or not picks:
            return ["picks on an item with no options"]
        if any(not isinstance(p, int) or isinstance(p, bool) or not 1 <= p <= n for p in picks):
            return [f"a pick outside 1..{n}"]
        if item["kind"] in ("gate", "single") and len(picks) != 1:
            return ["more than one pick on a single"]
        return []
    return [f"option shape {sorted(keys)} is none of picks / escape / value / unclear / any"]


def form_faults(script: dict, items: dict) -> list[str]:
    """The fixed form (FR-3) and the clocks."""
    faults = []
    for key in ("id", "round", "questionnaire", "turns"):
        if key not in script:
            faults.append(f"script has no {key}")
    turns = script.get("turns") or []
    if not turns:
        return faults + ["script has no turns"]
    prev_t, prev_gap = None, 0.0
    for i, turn in enumerate(turns):
        where = f"turn {i}"
        if turn.get("who") not in SPEAKERS:
            faults.append(f"{where}: who {turn.get('who')!r}")
        if not isinstance(turn.get("text"), str) or not turn["text"].strip():
            faults.append(f"{where}: no text")
        t, gap = turn.get("t"), turn.get("silence_after", 0)
        if not isinstance(t, (int, float)) or not isinstance(gap, (int, float)) or gap < 0:
            faults.append(f"{where}: clocks are not numbers")
            continue
        if prev_t is not None and t < prev_t + prev_gap:
            faults.append(f"{where}: clocks not monotone ({t} < {prev_t} + {prev_gap})")
        prev_t, prev_gap = t, gap
        truth = turn.get("truth")
        if not isinstance(truth, dict):
            faults.append(f"{where}: no truth")
            continue
        q = truth.get("q")
        if q is not None and q not in items:
            faults.append(f"{where}: q {q!r} is not an item id")
        v = truth.get("verdict")
        if v is not None and v not in VERDICTS:
            faults.append(f"{where}: verdict {v!r}")
        if turn.get("who") == "founder" and v is None:
            faults.append(f"{where}: a founder turn with no verdict")
        if truth.get("tier") is not None and truth["tier"] not in TIERS:
            faults.append(f"{where}: tier {truth['tier']!r}")
        if truth.get("state_after") not in STATES:
            faults.append(f"{where}: state_after {truth.get('state_after')!r}")
        if truth.get("option") is not None:
            if q is None:
                faults.append(f"{where}: an option with no q")
            else:
                faults += [f"{where}: {f}" for f in _option_faults(items[q], truth["option"])] if q in items else []
        if turn.get("kind") is not None and turn["kind"] not in KINDS:
            faults.append(f"{where}: kind {turn['kind']!r} is not in the catalogue")
    low, high = ROUND_SECONDS.get(script.get("round"), (0, 1e9))
    last = turns[-1].get("t") if isinstance(turns[-1].get("t"), (int, float)) else 0
    if last > high:
        faults.append(f"the call runs past round {script.get('round')}'s {high} s (last turn at {last} s)")
    if last < low:
        faults.append(f"the call is shorter than round {script.get('round')}'s {low} s (last turn at {last} s)")
    return faults


def _answered_before(turns: list, i: int, q: str) -> bool:
    return any(t["who"] == "them" and t["truth"].get("q") == q and t["truth"].get("option") is not None
               and t["truth"].get("verdict") is None for t in turns[:i])


def _asked_order(turns: list) -> list[str]:
    order = []
    for t in turns:
        tr = t.get("truth") or {}
        if t.get("who") == "founder" and tr.get("verdict") in QUESTION_VERDICTS and tr.get("q") \
                and tr["q"] not in order:
            order.append(tr["q"])
    return order


def _asking_kind(turns: list, i: int, q: str) -> str | None:
    """The kind of the last founder turn before `i` that asked `q`."""
    for t in reversed(turns[:i]):
        tr = t.get("truth") or {}
        if t.get("who") == "founder" and tr.get("q") == q and tr.get("verdict") in QUESTION_VERDICTS:
            return t.get("kind")
    return None


def turn_faults(script: dict, items: dict, questionnaire_order: list[str]) -> list[str]:
    """Every turn's kind rule, and the rules that hold whatever the kind."""
    turns = script["turns"]
    faults = []
    for i, turn in enumerate(turns):
        tr, text, kind = turn["truth"], turn["text"], turn.get("kind")
        q = tr.get("q")
        item = items.get(q) if q else None
        where = f"turn {i} ({kind or tr.get('verdict')})"
        # whatever the kind
        if tr.get("verdict") == "back_channel" and "?" in text:
            faults.append(f"{where}: a back-channel turn carries a question mark")
        if turn["who"] == "founder" and tr.get("verdict") == "follow_up" and not (q and _answered_before(turns, i, q)):
            faults.append(f"{where}: a follow-up before its question was answered")
        if turn["who"] == "founder" and tr.get("option") is not None:
            faults.append(f"{where}: a founder turn carries an answer")
        if kind is None:
            continue
        k = KINDS[kind]
        if k.side != turn["who"]:
            faults.append(f"{where}: a {k.side} kind on a {turn['who']} turn")
            continue
        if k.side == "founder" and k.verdict and tr.get("verdict") != k.verdict:
            faults.append(f"{where}: verdict {tr.get('verdict')} is not the kind's {k.verdict}")
        if item is not None and item["kind"] not in k.applies_to:
            faults.append(f"{where}: {kind} does not apply to a {item['kind']} item")
        if kind == "verbatim" and not any(norm(text) == norm(s) for s in stems(item or {})):
            faults.append(f"{where}: a verbatim turn is not the spoken stem")
        elif kind == "light_reword" and any(norm(text) == norm(s) for s in stems(item or {})):
            faults.append(f"{where}: a light reword is the stem as written")
        elif kind == "meaning_changed" and any(norm(text) == norm(s) for s in stems(item or {})):
            faults.append(f"{where}: a changed meaning is the stem as written")
        elif kind == "options_own_words":
            said = [o for o in (item or {}).get("options") or [] if says(text, o)]
            if said:
                faults.append(f"{where}: own-words options say Keel's label(s) {said}")
        elif kind == "options_reordered_or_missing":
            opts = (item or {}).get("options") or []
            found = sorted((norm(text).find(norm(o)), o) for o in opts if says(text, o))
            if [o for _, o in found] == opts:
                faults.append(f"{where}: every option offered, in Keel's order")
        elif kind == "story_prompt" and any(norm(text) == norm(s) for s in stems(item or {})):
            faults.append(f"{where}: a story prompt is the stem as written")
        elif kind == "preface":
            n = norm(text)
            if not any(n.endswith(norm(s)) and len(n.split()) >= len(norm(s).split()) + 3 for s in stems(item or {})):
                faults.append(f"{where}: a preface does not end with the stem after a few words")
        elif kind == "restart" and not BREAK.search(text):
            faults.append(f"{where}: a restart carries no break (... or sorry)")
        elif kind == "clarifying":
            prev = turns[i - 1] if i else None
            if not (prev and prev["who"] == "them" and prev["truth"].get("q") == q
                    and prev["truth"].get("option") is None):
                faults.append(f"{where}: a clarifying line that does not follow a counter-question on its item")
        elif kind == "follow_ups_in_a_row":
            same = [j for j, t in enumerate(turns) if t["who"] == "founder" and t["truth"].get("verdict") == "follow_up"
                    and t["truth"].get("q") == q]
            if len(same) < 2:
                faults.append(f"{where}: fewer than two follow-ups under {q}")
        elif kind == "own_note" and (q is not None or tr.get("verdict") != "own_note"):
            faults.append(f"{where}: an own note tagged to a question")
        elif kind == "any_order":
            order = _asked_order(turns)
            if len(order) < 2 or order == [x for x in questionnaire_order if x in order]:
                faults.append(f"{where}: the questions were asked in Keel's order")
        elif kind == "went_back":
            order = [t["truth"].get("q") for t in turns[:i] if t["who"] == "founder"
                     and t["truth"].get("verdict") in QUESTION_VERDICTS]
            if q not in order or order[-1] == q:
                faults.append(f"{where}: went back to a question not asked before, or asked just before")
        elif kind == "answered_for_them":
            prev = turns[i - 1] if i else None
            if not (prev and prev["who"] == "them") or tr.get("option") is not None:
                faults.append(f"{where}: answered-for-them does not follow the respondent, or carries an answer")
        elif kind == "back_channel" and q is not None:
            faults.append(f"{where}: a back-channel turn tagged to a question")
        # respondent kinds
        if k.side == "them" and kind not in ("counter_question", "two_voices"):
            want = expected_tier(_asking_kind(turns, i, q), kind) if q else k.tier
            if tr.get("tier") != want:
                faults.append(f"{where}: tier {tr.get('tier')} where the catalogue says {want}")
        if kind == "straight" and (tr.get("option") is None and (item or {}).get("kind") in CLOSED
                                   or len(text.split()) > 15):
            faults.append(f"{where}: a straight answer is long or reads nothing")
        elif kind == "story_first" and (len(text.split()) < 20 or tr.get("option") is None
                                        and (item or {}).get("kind") in CLOSED):
            faults.append(f"{where}: a story-first answer is short or reads nothing")
        elif kind == "late_negation":
            words = text.split()
            if not CORRECTION.search(" ".join(words[len(words) // 3:])) or tr.get("option") is None:
                faults.append(f"{where}: a late negation with no correction late in it, or nothing read")
        elif kind == "number_for_yes_no" and (not NUMBER.search(text) or "picks" not in (tr.get("option") or {})):
            faults.append(f"{where}: a number-for-yes-no with no number, or no yes/no read")
        elif kind == "different_question" and tr.get("option") != {"unclear": True}:
            faults.append(f"{where}: a different question must read unclear")
        elif kind == "counter_question" and (not text.rstrip().endswith("?") or tr.get("option") is not None):
            faults.append(f"{where}: a counter-question that is no question, or reads an answer")
        elif kind == "interrupted" and not CUT.search(text):
            faults.append(f"{where}: an interrupted turn that does not break off (--)")
        elif kind == "two_voices":
            near = [turns[j] for j in (i - 1, i + 1) if 0 <= j < len(turns)]
            if tr.get("option") is not None or tr.get("verdict") != "nothing" or not any(t["who"] == "them"
                                                                                         for t in near):
                faults.append(f"{where}: a second voice that reads an answer, or stands alone")
    return faults


def validate(script: dict, questionnaire: dict, *, kinds: list[str] | None = None) -> list[str]:
    """Every fault of a written script against the catalogue's rules: the form, the clocks, every turn's kind, and every
    kind the plan named appearing on a turn. `[]` is a script the bench keeps."""
    items = {it["id"]: it for it in questionnaire["items"]}
    faults = form_faults(script, items)
    if faults:
        return faults
    faults = turn_faults(script, items, [it["id"] for it in questionnaire["items"]])
    seen = {t.get("kind") for t in script["turns"]}
    for k in kinds or []:
        if k in SCRIPT_KINDS:
            order = _asked_order(script["turns"])
            if len(order) < 2 or order == [x for x in (it["id"] for it in questionnaire["items"]) if x in order]:
                faults.append(f"the plan's kind {k}: the questions were asked in Keel's order")
        elif k not in seen:
            faults.append(f"the plan's kind {k} is on no turn")
    return faults
