"""Spec 161: **the four questions, on three surfaces, from one script** -- the stranger's side of keel-cloud 269 / 270
(contract 87) and keel-web 258, as machinery: what the orb, the face and the Copilot card say, step by step, read off
the wire (the served `Interview`, the call's `CallScript`) or off the walks (`evals/three_views_strangers.py`'s rows and
strips), and compared (FR-9); the people each problem study is walked with (FR-5, FR-7: every why); the responses those
people send on the wire; and the reads of the founder's page (FR-7, FR-8). Pure functions over JSON -- the legs judge.

The words are keel-cloud's (contract 87, `canon/openapi-v2.yaml`, the registry's three `follow_up` blocks) and keel-web
258's; nothing here composes a question.

* **The gate's words** (269 FR-1): on a link that serves the film, *Did this happen to you?* -- no window phrase.
* **Frequency** (269 FR-3): `fixed_five`, five rows in order -- *Every time* / *Most times* / *About half the time* /
  *Now and then* / *Never*, codes `every_time` .. `never`, no escape; A and B count for the founder, C, D and E against
  (`working_rung.frequency_side`).
* **A No goes on** (269 FR-2, 270 FR-1): after the gate's No the Prevalence follow-up on the spot (*How do you go about
  it, and what keeps this from happening to you?*), then Importance, the pilot ask, the thanks; the response
  `{recency: false, answers: [Importance], followUps: [Prevalence's]}` -- no story, no Frequency.
* **Every why** (270 FR-2): a person is asked on every rung they are against on, up to two, the fewest first.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

# ------------------------------------------------------------------------------------------- the words (contract 87)

#: keel-cloud 269 FR-1 (`story_gate`, `StoryGate.TEMPLATE`): the gate after the film, on every surface.
GATE_WORDS = "Did this happen to you?"
#: keel-cloud 269 FR-3 (`FrequencyScale`): the five codes and labels, in the served order; letters A-E.
FREQUENCY_CODES = ("every_time", "most_times", "about_half", "now_and_then", "never")
FREQUENCY_LABELS = ("Every time", "Most times", "About half the time", "Now and then", "Never")
#: keel-cloud 269 FR-3: the share scale's rule -- the two codes that count for the founder.
FOR_CODES = ("every_time", "most_times")
#: keel-cloud 269 FR-3: Frequency's question, composed by code from the story's job (*How often does it happen to you?*
#: where the job would take it past twenty words).
FREQUENCY_QUESTION = "When you {job}, how often does it happen?"
FREQUENCY_WITHOUT_THE_JOB = "How often does it happen to you?"
#: keel-cloud 269 FR-4: Importance's question and its second ask.
IMPORTANCE_QUESTION = "Of the things you do as a {actor}, which would you most like made easier?"
IMPORTANCE_AGAIN = "And one more?"
#: keel-cloud 270 FR-1 (the registry's three blocks): each why's words and its heading.
PREVALENCE_WHY = "How do you go about it, and what keeps this from happening to you?"
PREVALENCE_HEADING = "What keeps it from happening to them"
DIFFERENCE_WHY = "What makes the difference between the times it happens and the times it does not?"
DIFFERENCE_HEADING = "What makes the difference"
NEVER_WHY = "You said it happened to you. Tell me about that time."
NEVER_HEADING = "A yes, then never"
#: keel-cloud 270 FR-1: Frequency's rung is against on these two; its second stem on `never` after a yes.
FREQUENCY_AGAINST = ("about_half", "now_and_then")
#: keel-cloud 270 FR-2: at most two whys an interview (`MAX_FOLLOW_UPS`).
MAX_FOLLOW_UPS = 2
#: The three PROBLEM rungs (keel-cloud 269 FR-5: Current solution gone).
PREVALENCE, FREQUENCY, IMPORTANCE = "problem.prevalence", "problem.frequency", "problem.importance"
CURRENT_SOLUTION = "problem.current_solution_satisfaction"
#: keel-cloud 270 FR-5: the No-sayers' quotes carry the option *No*.
NO_OPTION = "No"


# ------------------------------------------------------------------------------------------- one record a surface

def _words(text: Any) -> str:
    """Words compared as said: whitespace runs as one space, the ends stripped (case kept -- the words are the wire's)."""
    return " ".join(str(text or "").split())


def _bare(text: Any) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", str(text or "").lower().replace("’", "'")))


def _labels(options: Iterable[dict] | None) -> list[str]:
    return [_words(o.get("label")) for o in options or [] if isinstance(o, dict) and o.get("label")]


def step(key: str, words: str | None, options: list[str] | None = None, follow_ups: list[str] | None = None) -> dict:
    """One step of a surface's script: the step's key (the screener, the gate, an item's dimension, the check), the
    question's words, the options' labels in order, the follow-up stems owed on it (in the ladder's order)."""
    return {"step": key, "words": _words(words), "options": list(options or []),
            "follow_ups": [_words(f) for f in follow_ups or [] if f]}


def served_record(interview: dict | None) -> list[dict]:
    """Spec 161 FR-9 on the wire: the orb's or the face's script as the link serves it (`GET /v2/i/{token}/interview`)
    -- the screener (`gate.condition` or the link's `condition`), the gate (its question, Yes and the served No label,
    the Prevalence why), the decision-maker's check, then every item (its question, its options, its whys: the served
    `followUps`' words for its dimension)."""
    iv = interview or {}
    whys: dict[str, list[str]] = {}
    for f in iv.get("followUps") or []:
        if isinstance(f, dict) and f.get("dimension"):
            whys.setdefault(str(f["dimension"]), []).append(f.get("spoken") or f.get("text"))
    out: list[dict] = []
    gate = iv.get("gate") or {}
    condition = (gate.get("condition") or iv.get("condition") or {}).get("question")
    if condition:
        out.append(step("screener", condition, ["Yes", "No"]))
    if gate:
        out.append(step("gate", gate.get("question"), ["Yes", _words(gate.get("noLabel") or "No")],
                        whys.get(str(gate.get("dimension") or PREVALENCE))))
    check = (iv.get("problemCheck") or {}).get("question")
    if check:
        out.append(step("check", check, ["Yes", "No"]))
    for part in iv.get("parts") or []:
        for item in part.get("items") or []:
            out.append(step(str(item.get("dimension") or item.get("itemId")), item.get("question"),
                            _labels(item.get("options")), whys.get(str(item.get("dimension")))))
    return out


def _hints(follow: dict | None) -> list[str]:
    """The rung's hint as the card says it. A second stem's hint (`also`) is kept apart (`_also`): the link serves one
    `followUps` entry a rung and plays the second stem from its clip alone, so only the rung's words are compared."""
    hint = (follow or {}).get("hint") or {}
    return [hint.get("third") or hint.get("first")] if hint else []


def _also(follow: dict | None) -> list[str]:
    also = ((follow or {}).get("also") or {}).get("hint") or {}
    return [also.get("third") or also.get("first")] if also else []


def _card_labels(passage: dict) -> list[str]:
    """A card passage's answers as labels: the options it files by id (a ladder's opening bands, which only open its
    second step, carry no id) and each second step's, in order."""
    labels = [_words(o.get("label")) for o in passage.get("options") or [] if o.get("optionId")]
    for side in ("under", "over"):
        labels += _labels(((passage.get("twoSteps") or {}).get(side) or {}).get("options"))
    return labels


def card_record(script: dict | None) -> list[dict]:
    """Spec 161 FR-9 on the wire: the Copilot card's script (`GET .../calls/{callId}/script`, keel-cloud 248's
    `CallScript`) as the same steps -- the gate's condition (the screener, asked before the gate), the gate (its stem,
    its two answers, the Prevalence hint), every item (its stem, the options it files, its hints: the rung's and the
    second stem's). Intro, reveal and pilot passages are not questions of the four and are not compared."""
    out: list[dict] = []
    for p in (script or {}).get("passages") or []:
        kind = p.get("kind")
        if kind == "gate":
            condition = (p.get("condition") or {}).get("question")
            if condition:
                out.append(step("screener", condition, ["Yes", "No"]))
            out.append(step("gate", p.get("stem"), _labels(p.get("options")), _hints(p.get("followUp"))))
        elif kind == "item":
            one = step(str(p.get("dimension") or p.get("itemId")), p.get("stem"), _card_labels(p),
                       _hints(p.get("followUp")))
            if _also(p.get("followUp")):
                one["also"] = _also(p.get("followUp"))       # reported, not compared (see `_hints`)
            if p.get("twoSteps"):
                one["ladder"] = True          # the card lays a ladder out in two steps: its bands compared as a set
            out.append(one)
    return out


def walked_record(rows: list[dict] | None, *, whys: dict[str, list[str]] | None = None) -> list[dict]:
    """Spec 161 FR-9 off a walk (the orb's or the face's `link_walk` rows, keel-web 258): each question sheet as a step
    -- its words, its rows' labels in order -- with the follow-up stems asked after it folded onto it; `whys` the
    stems by dimension where the walk names them."""
    out: list[dict] = []
    for r in rows or []:
        if r.get("screen") != "question":
            continue
        if r.get("step") == "followUp" or r.get("follow_up"):
            if out:
                out[-1]["follow_ups"].append(_words(r.get("question")))
            continue
        if not r.get("key"):
            continue                                     # the story, the pilot ask: not one of the script's questions
        out.append(step(str(r["key"]), r.get("question"),
                        ["Yes", "No"] if r["key"] in ("screener", "gate", "check") and not r.get("options")
                        else [_words(o) for o in r.get("options") or []]))
    return out


def strips_record(strips: list[dict] | None) -> list[dict]:
    """Spec 161 FR-9 off the Copilot card's walk (`copilot_walk` strips, keel-web 258 FR-5): each question strip as a
    step -- its words (`read`, the card's question) and its answers' labels (the card's digits are not compared); a
    follow-up strip folded onto the step before it."""
    out: list[dict] = []
    for s in strips or []:
        if s.get("phase") == "follow-up":
            if out:
                out[-1]["follow_ups"].append(_words(s.get("read") or s.get("head")))
            continue
        if s.get("phase") not in ("reading", "second-step"):
            continue
        out.append(step(str(s.get("key") or s.get("question") or "?"), s.get("read"),
                        [_words(o) for o in s.get("options") or []]))
    return out


#: Steps a surface may not carry (the screener, the decision-maker's check): compared where all three carry them.
OPTIONAL_STEPS = ("screener", "check")


def same_script(records: dict[str, list[dict]], *, reference: str = "orb") -> dict:
    """Spec 161 FR-9: the surfaces' records held equal step for step -- the question's words, the options' labels in
    order, the follow-up stems (the face's clip routes and the card's digits are never in a record). `same`, or the first
    step and surface where one differs (`at`, `surface`, `step`, `differs`: which of words / options / follow_ups /
    the step itself, and both records there)."""
    # the screener and the decision-maker's check are compared only where every surface carries them: the call's
    # script files the gate's screener on the gate passage and has no passage of the check -- noted, never a part
    absent = {}
    for key in OPTIONAL_STEPS:
        lacking = [name for name, rec in records.items() if not any(s.get("step") == key for s in rec)]
        if lacking and len(lacking) < len(records):
            absent[key] = lacking
    records = {name: [s for s in rec if s.get("step") not in absent] for name, rec in records.items()}
    # a price or duration ladder: the card says its middle band first and the second steps after (its digits and its
    # steps are the card's own), so its bands are held as a set beside the served order
    ladders = {s.get("step") for rec in records.values() for s in rec if s.get("ladder")}

    def plain(rec: list[dict]) -> list[dict]:
        return [{k: (sorted(v) if k == "options" and s.get("step") in ladders else v)
                 for k, v in s.items() if k not in ("ladder", "also")} for s in rec]
    records = {name: plain(rec) for name, rec in records.items()}
    ref = records.get(reference) or []
    parts: list[dict] = []
    for surface, rec in records.items():
        if surface == reference:
            continue
        for i in range(max(len(ref), len(rec))):
            a = ref[i] if i < len(ref) else None
            b = rec[i] if i < len(rec) else None
            if a == b:
                continue
            differs = (["missing on " + surface] if b is None else ["missing on " + reference] if a is None
                       else [k for k in ("step", "words", "options", "follow_ups") if a.get(k) != b.get(k)])
            parts.append({"at": i, "surface": surface, "step": (a or b or {}).get("step"), "differs": differs,
                          reference: a, surface + "_record": b})
    if parts:
        first = parts[0]
        # the first step and surface where one differs, then every other part (so one difference hides none after it)
        return {"same": False, **first, "parts": [{k: x[k] for k in ("at", "surface", "step", "differs")}
                                                   for x in parts], "not_on_every_surface": absent}
    return {"same": True, "steps": len(ref), "surfaces": sorted(records), "not_on_every_surface": absent}


def gate_words(record: list[dict]) -> str | None:
    """The gate's words in a record."""
    return next((s["words"] for s in record if s["step"] == "gate"), None)


# ------------------------------------------------------------------------------------------- the order on a film link

def screener_first(stage: list[str], *, screener: bool) -> dict:
    """Spec 161 FR-4 (keel-web 258 FR-2b): the order on a film link -- the opening passage, the screener (its own
    counted step), the film, *Begin*, then the gate; without a screener: the opening, the film, the gate. `stage` is the
    walk's steps as `story_screens.walk_steps` names them (`speaking:...`, `listening:Question 1 of ...`,
    `film:problem+begin`, ...), reduced here to `opening`, `screener`, `film`, `gate`."""
    seen: list[str] = []
    for s in stage:
        name = s.split(":")[0] if ":" in s else s
        key = ("film" if s.startswith("film:problem") else "screener" if "screener" in s
               else "gate" if "gate" in s else "opening" if name == "speaking" and not seen else None)
        if key and (not seen or seen[-1] != key):
            seen.append(key)
    want = ["opening", "screener", "film", "gate"] if screener else ["opening", "film", "gate"]
    folded = [k for k in seen if k in want]
    first = []
    for k in folded:
        if k not in first:
            first.append(k)
    return {"ok": first[:len(want)] == want, "order": first, "want": want}


# ------------------------------------------------------------------------------------------- the people (FR-5, FR-7)

#: Spec 161 FR-5, FR-7: the five people every problem study is walked with -- their gate, their Frequency answer,
#: whether they picked the own row on Importance, and the whys they are owed (270 FR-2, the fewest first: Frequency's
#: before Importance's), with the words they say to each.
ROSTER = (
    {"who": "about half, the own row picked", "gate": True, "frequency": "about_half", "own": True,
     "owed": [FREQUENCY], "stems": [DIFFERENCE_WHY]},
    {"who": "every time, the own row not picked", "gate": True, "frequency": "every_time", "own": False,
     "owed": [IMPORTANCE], "stems": [None]},
    {"who": "now and then, the own row not picked", "gate": True, "frequency": "now_and_then", "own": False,
     "owed": [FREQUENCY, IMPORTANCE], "stems": [DIFFERENCE_WHY, None]},
    {"who": "a yes, then never", "gate": True, "frequency": "never", "own": True,
     "owed": [FREQUENCY], "stems": [NEVER_WHY]},
    {"who": "the No-sayer", "gate": False, "frequency": None, "own": True,
     "owed": [PREVALENCE], "stems": [PREVALENCE_WHY]},
)
#: The words each of them says to a why (any words; the fake transcriber hears them as said); `NEVER_SAID` to the second
#: stem.
WHY_SAID = {PREVALENCE: "We check it twice before it goes out, so it rarely gets that far.",
            FREQUENCY: "It depends on how many changes came in that week.",
            IMPORTANCE: "Those take more of my week than this one does."}
NEVER_SAID = "It was the week the rates changed, and it never came back."
#: The story a yes-sayer tells (any words); each person of `ROSTER` tells their own (`STORIES`, in the roster's order:
#: two the founder's way, one another way, one none), so the ways read from them group.
STORY_SAID = "It happened last week, and it took the whole afternoon to sort out."
STORIES = ("Last week I went down the report line by line and it took the whole afternoon.",
           "I asked a colleague to check the numbers with me before it went out.",
           "I compared it with the last report line by line until every figure matched.",
           "It happened once, and I fixed it the next morning.")
#: The scripted runtime's groupings of those words (keel-runtime 012 resolves THEMES by the answers' texts): one theme a
#: rung, its label sharing words with its answers (keel-cloud 119 T11), never the rung's name (T5).
THEMES = {PREVALENCE: [{"label": "Check it twice before it goes out", "answers": [WHY_SAID[PREVALENCE]]}],
          FREQUENCY: [{"label": "Depends on the changes that week", "answers": [WHY_SAID[FREQUENCY]]},
                      {"label": "The week the rates changed", "answers": [NEVER_SAID]}],
          IMPORTANCE: [{"label": "Those take more of my week", "answers": [WHY_SAID[IMPORTANCE]]}]}
#: keel-cloud 270 FR-3: the leftovers' group of the ways (`Insight.ON_THEIR_OWN`).
ON_THEIR_OWN = "ON_THEIR_OWN"
#: The second way's label (its words the second story's).
ANOTHER_WAY = "A colleague checks the numbers"


def themes_entries(said: dict[str, list[str]] | None = None) -> list[dict]:
    """The scripted runtime's THEMES entries for the three PROBLEM rungs (`{dimension, outcome, result: {themes: [{label,
    answers}]}}`), each theme kept only where one of its answers was said on that rung (`said`: rung -> the texts sent;
    all of `THEMES` where none given)."""
    out = []
    for dimension, themes in THEMES.items():
        kept = [t for t in themes if said is None or any(a in (said.get(dimension) or []) for a in t["answers"])]
        if kept:
            out.append({"dimension": dimension, "outcome": "COMPLETED", "result": {"themes": kept}})
    return out


#: The scripted reading of a roster story (`INTERPRET`): ANCHORED, so every yes-sayer's answers count on the founder's
#: page (a GUESSED story is shown hollow and counted nowhere) -- the runtime fills the invitation id from the job.
ANCHORED = {"outcome": "COMPLETED", "result": {"anchoring": "ANCHORED", "unprompted": [], "flags": []}}


def ways_entry(stories: list[tuple[str, str]], founder_act: str | None) -> dict:
    """The scripted runtime's EXPERIENCE_WAYS answer (keel-cloud 270 FR-3, `{ways: [{label, answerIds}]}`) over the
    stories told (`(invitationId, text)`, `STORIES`' words): the two told the founder's way under the founder's act word
    for word, the colleague's under `ANOTHER_WAY`, the one that names no way `ON_THEIR_OWN` -- every story once."""
    founders, another, alone = [], [], []
    for invitation, text in stories:
        if text in (STORIES[0], STORIES[2]):
            founders.append(invitation)
        elif text == STORIES[1]:
            another.append(invitation)
        else:
            alone.append(invitation)
    ways = []
    if founders and founder_act:
        ways.append({"label": founder_act, "answerIds": founders})
    elif founders:
        alone += founders
    if another:
        ways.append({"label": ANOTHER_WAY, "answerIds": another})
    if alone:
        ways.append({"label": ON_THEIR_OWN, "answerIds": alone})
    return {"outcome": "COMPLETED", "result": {"ways": ways}}


def owed_whys(gate: bool, frequency: str | None, own: bool) -> list[str]:
    """keel-cloud 270 FR-2, restated: the rungs a PROBLEM-study person is against on -- the gate's No (Prevalence), a
    Frequency of About half or Now and then, or Never after a yes (its second stem), Importance without the own row --
    up to two, in order (Prevalence on the spot, Frequency after its answer, Importance at the end)."""
    out = []
    if not gate:
        out.append(PREVALENCE)
    elif frequency in FREQUENCY_AGAINST or frequency == "never":
        out.append(FREQUENCY)
    if not own:
        out.append(IMPORTANCE)
    return out[:MAX_FOLLOW_UPS]


def item_of(interview: dict, dimension: str) -> dict:
    return next((i for p in (interview or {}).get("parts") or [] for i in p.get("items") or []
                 if i.get("dimension") == dimension), {})


def option_id(item: dict, *, code: str | None = None, label: str | None = None, index: int | None = None) -> str | None:
    """A served option's id by its normalised code, its label, or its place."""
    options = item.get("options") or []
    for i, o in enumerate(options):
        if code is not None and (o.get("normalized") == code or o.get("code") == code):
            return o.get("optionId")
        if label is not None and _bare(o.get("label")) == _bare(label):
            return o.get("optionId")
        if index is not None and i == index:
            return o.get("optionId")
    return None


def own_option(item: dict, *, other_tasks: Iterable[str] = (), own_label: str | None = None) -> dict | None:
    """Importance's own row as served -- the wire marks none (`ItemOption` is `{optionId, label}`), so it is the row
    labelled as the founder's own (`own_label`, the review's first Importance row) or else the one row that is not
    among the story's other tasks (keel-cloud 269 FR-4: the rows are `otherTasks` plus the own row)."""
    options = item.get("options") or []
    if own_label:
        found = next((o for o in options if _bare(o.get("label")) == _bare(own_label)), None)
        if found:
            return found
    others = {_bare(t) for t in other_tasks}
    rest = [o for o in options if _bare(o.get("label")) not in others]
    return rest[0] if len(rest) == 1 else None


def importance_picks(item: dict, *, own: bool, other_tasks: Iterable[str] = (), own_label: str | None = None) -> list:
    """Two picks on Importance: the own row and another, or two rows that are not the own row."""
    mine = own_option(item, other_tasks=other_tasks, own_label=own_label)
    ids = [o.get("optionId") for o in item.get("options") or []]
    others = [i for i in ids if not mine or i != mine.get("optionId")]
    return ([mine.get("optionId")] + others[:1]) if (own and mine) else others[:2]


def frequency_answer(item: dict, code: str) -> dict:
    """Frequency's answer on the wire (`fixed_five`: one option id, by its label -- the five are served in order)."""
    oid = option_id(item, label=FREQUENCY_LABELS[FREQUENCY_CODES.index(code)]) \
        or option_id(item, index=FREQUENCY_CODES.index(code))
    return {"itemId": item.get("itemId"), "optionIds": [oid]}


def answers_for(person: dict, interview: dict, *, other_tasks: Iterable[str] = (), own_label: str | None = None) -> list:
    """The items one of `ROSTER` answers, as `ItemAnswer`s: Frequency's code after a yes, Importance's two picks."""
    importance = item_of(interview, IMPORTANCE)
    answers = [{"itemId": importance.get("itemId"),
                "optionIds": importance_picks(importance, own=person["own"], other_tasks=other_tasks,
                                              own_label=own_label)}]
    if person["gate"]:
        answers.insert(0, frequency_answer(item_of(interview, FREQUENCY), person["frequency"]))
    return answers


def response_for(person: dict, interview: dict, *, fmt: str, whys: list[dict], other_tasks: Iterable[str] = (),
                 own_label: str | None = None) -> dict:
    """Spec 161 FR-5 / FR-7 on the wire: the response one of `ROSTER` sends -- a yes-sayer the story, Frequency's code
    and two Importance picks; the No-sayer `recency: false`, the Importance answer alone; each why answered in order
    (`whys`: what the follow-up route returned, `{dimension, ...}`)."""
    body: dict = {"format": fmt, "recency": bool(person["gate"])}
    if person["gate"]:
        body["story"] = person.get("story") or STORY_SAID
    body["answers"] = answers_for(person, interview, other_tasks=other_tasks, own_label=own_label)
    if whys:
        body["followUps"] = [{"dimension": w["dimension"], "text": why_said(w), "how": "RECORDED"} for w in whys]
    return body


def why_said(why: dict) -> str:
    """What a person says to one why: the second stem's words where the stem asked is Never's, else the rung's."""
    if _bare(why.get("text") or why.get("spoken")) == _bare(NEVER_WHY):
        return NEVER_SAID
    return WHY_SAID.get(str(why.get("dimension")), "Because it does.")


# ------------------------------------------------------------------------------------------- the founder's page (FR-7, FR-8)

def frequency_row(standings: dict) -> dict:
    """Frequency's standing on the founder's page (`StandingsView.vectors[].dimensions[]`, a `DimensionStanding`)."""
    for vector in (standings or {}).get("vectors") or []:
        for row in (vector.get("dimensions") or []) + (vector.get("standings") or []):
            if row.get("dimension") == FREQUENCY:
                return row
    return {}


def frequency_faults(row: dict, *, picks: list[str] | None = None) -> list:
    """Spec 161 FR-8 (keel-cloud 269 FR-3): Frequency as five bands -- `chart.frequency` `{forCodes: [every_time,
    most_times], share, n, founderBand}`, no `chart.window`, the five counts in order; where `picks` (every yes-sayer's
    code) is given, `n` and `share` are theirs."""
    faults = []
    chart = row.get("chart") or {}
    f = chart.get("frequency")
    if not f:
        return [{"chart.frequency": "absent", "chart": sorted(chart)}]
    if list(f.get("forCodes") or []) != list(FOR_CODES):
        faults.append({"forCodes": f.get("forCodes")})
    if "window" in chart:
        faults.append({"chart.window": "served (keel-cloud 269: gone)"})
    if not f.get("founderBand"):
        faults.append({"founderBand": f.get("founderBand")})
    if picks is not None:
        n = len(picks)
        share = round(sum(1 for p in picks if p in FOR_CODES) / n, 2) if n else 0
        if f.get("n") != n or abs(float(f.get("share") or 0) - share) > 0.011:
            faults.append({"n/share": {"served": [f.get("n"), f.get("share")], "want": [n, share]}})
    counts = ((row.get("choice") or {}).get("optionCounts")) or []
    if counts and [_bare(c.get("label")) for c in counts] != [_bare(x) for x in FREQUENCY_LABELS]:
        faults.append({"bands": [c.get("label") for c in counts]})
    return faults


def current_solution_anywhere(*views: Any) -> list[str]:
    """Spec 161 FR-8 (keel-cloud 269 FR-5): where Current solution still shows -- every JSON path naming its key."""
    out: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if k == CURRENT_SOLUTION or k == "currentSolution":
                    out.append(f"{path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{path}[{i}]")
        elif value == CURRENT_SOLUTION:
            out.append(path)
    for n, view in enumerate(views):
        walk(view, f"view{n}")
    return out


def ways_faults(overview: dict, standings: dict, *, stories: int, founder_way: str | None = None) -> list:
    """Spec 161 FR-8 (keel-cloud 270 FR-3, FR-4): the ways panel's wire -- `Overview.ways` absent with fewer than two
    stories; with two or more `{state, groups, read}`, GROUPED on the scripted reader, the founder's way flagged where a
    group is labelled by it; nothing of it on `insights[]`."""
    faults = []
    ways = (overview or {}).get("ways")
    if stories < 2:
        return [{"ways": "served under two stories"}] if ways else []
    if not ways:
        return [{"ways": "absent with two or more stories"}]
    if ways.get("state") != "GROUPED":
        faults.append({"state": ways.get("state"), "read": ways.get("read")})
    groups = ways.get("groups") or []
    if ways.get("state") == "GROUPED" and not groups:
        faults.append({"groups": "none while GROUPED"})
    if founder_way and groups and not any(g.get("founders") for g in groups):
        faults.append({"founders": "no group flagged as the founder's way", "groups": groups})
    if any("ways" in (i or {}) or (i or {}).get("dimension") == "ways" for i in (standings or {}).get("insights") or []):
        faults.append({"insights": "the ways on the Insights tab"})
    return faults


def insights_faults(standings: dict) -> list:
    """Spec 161 FR-7 (keel-cloud 270 FR-2, FR-5; spec 119's view): every card read -- no `tookBy` anywhere, `capped` an
    integer with `asked + capped == against`, the three PROBLEM rungs' headings the registry's, a No-sayer's quote with
    option *No*, Frequency's quotes with their band's label, the dissent frame on a held line."""
    faults = []
    headings = {PREVALENCE: PREVALENCE_HEADING, FREQUENCY: DIFFERENCE_HEADING}
    for i in (standings or {}).get("insights") or []:
        key = i.get("dimension")
        if "tookBy" in i:
            faults.append({key: "tookBy served (keel-cloud 270: gone)"})
        if not isinstance(i.get("capped"), int):
            faults.append({key: "capped", "served": i.get("capped")})
        elif int(i.get("asked") or 0) + int(i.get("capped") or 0) != int(i.get("against") or 0):
            faults.append({key: "asked + capped != against", "asked": i.get("asked"), "capped": i.get("capped"),
                           "against": i.get("against")})
        if key in headings and i.get("rungHeading") != headings[key]:
            faults.append({key: "rungHeading", "served": i.get("rungHeading"), "want": headings[key]})
        if key == FREQUENCY and i.get("alsoHeading") not in (None, NEVER_HEADING):
            faults.append({key: "alsoHeading", "served": i.get("alsoHeading")})
        for q in i.get("quotes") or []:
            option = q.get("option") or q.get("optionLabel")
            if key == PREVALENCE and _bare(option) != _bare(NO_OPTION):
                faults.append({key: "a No-sayer's quote without the option No", "quote": q})
            if key == FREQUENCY and _bare(option) not in [_bare(x) for x in FREQUENCY_LABELS]:
                faults.append({key: "a Frequency quote without its band", "quote": q})
        if i.get("dissent") and not str(i.get("frame") or "").startswith(f"{i.get('name')} held,"):
            faults.append({key: "dissent frame", "frame": i.get("frame")})
    return faults


def brief_frequency_faults(facts: dict, *, picks: list[str] | None = None) -> list:
    """Spec 161 FR-8 (keel-cloud 269 FR-3): `BriefFacts.problem.frequency` on bands -- `{n, bands: [{code, label,
    count}], mostOrEvery}`, the five in order, no `median` / `middle`; the counts the picks' where given."""
    f = ((facts or {}).get("problem") or {}).get("frequency")
    if not f:
        return [{"facts.problem.frequency": "absent"}]
    faults = []
    if "median" in f or "middle" in f:
        faults.append({"median/middle": "served (keel-cloud 269: gone)"})
    bands = f.get("bands") or []
    if [b.get("code") for b in bands] != list(FREQUENCY_CODES):
        faults.append({"bands": [b.get("code") for b in bands]})
    if picks is not None:
        want = {c: picks.count(c) for c in FREQUENCY_CODES}
        got = {b.get("code"): b.get("count") for b in bands}
        if got != want or f.get("mostOrEvery") != sum(want[c] for c in FOR_CODES) or f.get("n") != len(picks):
            faults.append({"counts": got, "want": want, "mostOrEvery": f.get("mostOrEvery"), "n": f.get("n")})
    return faults
