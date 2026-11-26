"""Spec 162 (keel-cloud 272, contract 90; keel-web 260): **the solution study on three surfaces, from one script** -- the
stranger's side of the solution link as machinery, beside `harness/three_surfaces.py` (spec 161's four questions): the
link's order and its words (the opening, the screener, the bridge, the problem's film, the check, the brand plate and
its two lines, the idea's film, the three yes-or-no questions, their whys, the pilot ask), the people every solution
study is walked with (FR-7: every why), the responses they send on the wire, the founder's page (FR-8: three share
bars, evidence-only So lines, no benefit scale) and the three surfaces' records (FR-9). Pure functions over JSON -- the
legs judge.

Every word is keel-cloud 272's (`SolutionLink`, `SolutionQuestions`, the registry's three `follow_up` blocks at
`DimensionRegistry.VERSION` 7) copied word for word; nothing here composes a question for the product.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from harness import three_surfaces as ts

# ------------------------------------------------------------------------------------------- the words (contract 90)

COMPATIBILITY, RELATIVE_ADVANTAGE, ADOPTION_FRICTION = (
    "solution.compatibility", "solution.relative_advantage", "solution.adoption_friction")
#: keel-cloud 272 FR-1: the three, in the order asked.
SOLUTION_DIMENSIONS = (COMPATIBILITY, RELATIVE_ADVANTAGE, ADOPTION_FRICTION)
#: keel-cloud 272 FR-1 (D4): `yes_no` -- Yes · No, code's, in this order, no escape; letters A and B.
YES_NO = "yes_no"
YES_NO_CODES = ("yes", "no")
YES_NO_LABELS = ("Yes", "No")
#: keel-cloud 272 FR-1 (`SolutionQuestions`): the three questions -- Compatibility with the job's -ing form and the
#: brand's name (its giving way where the job takes it past 20 words), Relative advantage the base job, Adoption friction
#: its setup form (where a setup was named) or its no-setup form.
COMPATIBILITY_Q = "Would {task_ing} this way, with {name}, fit into how you work?"
COMPATIBILITY_GIVING = "Would doing it this way, with {name}, fit into how you work?"
RELATIVE_ADVANTAGE_Q = "Compared with the way you {task} today, would {name} be better?"
RELATIVE_ADVANTAGE_GIVING = "Compared with the way you do it today, would {name} be better?"
ADOPTION_SETUP_Q = "Before you could use {name} for this, you would need {the setup}. Could you start without much trouble?"
ADOPTION_NONE_Q = "Could you start using {name} for this tomorrow, with nothing to set up first?"
#: Spec 172 FR-6 (keel-cloud 285 FR-1, `SolutionQuestions.FILM_*`): where the link serves both films the three questions
#: are code's own short frames, *this* the idea's film just watched -- two slots only, `{name}` (the brand as given,
#: `NO_NAME` where there is none) and `{the setup}` (the founder's rows, as many whole rows as keep that sentence within
#: `FILM_MAX_WORDS`); a link that serves no film keeps 272's frames above (the item's `framed`, `three_surfaces.framed_of`).
COMPATIBILITY_FILM = "Would this fit how you work?"
RELATIVE_ADVANTAGE_FILM = "Would {name} be better than how you do it today?"
ADOPTION_SETUP_FILM = "You would first need {the setup}. Could you start without much trouble?"
ADOPTION_NONE_FILM = "Could you start using {name} without much trouble?"
NO_NAME = "this idea"
#: keel-cloud 285 FR-6 (its DRIFT: per sentence): every sentence of the film's frames at most seventeen words.
FILM_MAX_WORDS = 17
#: keel-cloud 272 FR-2 (the registry's three `follow_up` blocks): each why and its heading.
WHYS = {COMPATIBILITY: ("What would get in the way?", "What would get in the way"),
        RELATIVE_ADVANTAGE: ("What would it have to do better?", "What it would have to do better"),
        ADOPTION_FRICTION: ("What makes it a trouble?", "What makes it a trouble")}
#: keel-cloud 272 FR-3 (`SolutionLink`): the link's words around the films.
OPENING = "{founder} believes {people} have a problem when they {task}."
OPENING_SPLIT = "{founder} believes {people} have a problem. It comes when they {task}."
ONE_QUESTION = "First, one question."
TO_THE_FILM = "Let us see it."
PLATE_BEFORE = "Now {founder} has built {name}."
PLATE_AFTER = "and believes it solves this. Let us see."
PILOT = "Would you try {name} for real?"
#: keel-cloud 267 / 272 (`PassageComposer.INTRODUCED`, `HOW_TO_ANSWER`; 272 judgement call 3): the opening clip the orb and
#: the face say is the interviewer's introduction and how to answer, then `passages.opening` -- the card's intro reads
#: the same three sentences (its `third` form).
INTRODUCED = "I'm Keel's interviewer. I'm an AI, not a person."
HOW_TO_ANSWER = "Say the answer that fits, or tap it."
#: keel-cloud 272 FR-5 (`CallScriptComposer.Plate`): the card's first-person plate line.
PLATE_BEFORE_FIRST = "Now I have built {name}."
#: The spoken-form cap (keel-cloud `SpokenForm.STEM_MAX_WORDS`): every sentence at most 20 words.
SENTENCE_MAX_WORDS = 20
#: keel-cloud 270 FR-2 (272 keeps it): at most two whys an interview.
MAX_FOLLOW_UPS = ts.MAX_FOLLOW_UPS
#: Spec 162 FR-8 (the founder's copy rule of 2026-11-15: the site says what did not hold, never what to do): the words a
#: So line may never carry.
RECOMMENDATION_WORDS = ("should", "next", "try")


def sentences(text: str | None) -> list[str]:
    """A line's sentences (split after `.`, `?` or `!` and a space)."""
    return [s for s in re.split(r"(?<=[.?!])\s+", " ".join(str(text or "").split())) if s]


def words(text: str | None) -> int:
    return len(re.findall(r"[A-Za-z0-9'’$%,.-]+", str(text or "")))


def over_cap(text: str | None) -> list[str]:
    """The sentences past the spoken-form cap (20 words)."""
    return [s for s in sentences(text) if len(s.split()) > SENTENCE_MAX_WORDS]


def _pattern(template: str, **fixed: str) -> re.Pattern:
    """A template as a pattern: the named placeholders fixed, every other placeholder any words."""
    out = ""
    for piece in re.split(r"(\{[a-z_ ]+\})", template):
        if piece.startswith("{") and piece.endswith("}"):
            key = piece[1:-1]
            out += re.escape(fixed[key]) if key in fixed else ".+?"
        else:
            out += re.escape(piece)
    return re.compile("^" + out + "$")


def question_faults(interview: dict | None, *, name: str, setup: list[str] | None) -> list[dict]:
    """Spec 162 FR-6 on the wire (keel-cloud 272 FR-1): the three items as served -- `yes_no`, *Yes* · *No* in order, no
    escape; Compatibility carries the brand's name (the job's -ing form or the giving way), Relative advantage the base
    job (or its giving way), Adoption friction its setup form where the founder named a setup (each row's words in it)
    and its no-setup form where none; every sentence at most 20 words. Spec 172 FR-6 (keel-cloud 285): an item framed
    `film` is held to the short frames instead (`COMPATIBILITY_FILM` ..., each sentence at most 17 words)."""
    faults: list[dict] = []
    for key in SOLUTION_DIMENSIONS:
        item = ts.item_of(interview or {}, key)
        if not item:
            faults.append({key: "not served"})
            continue
        labels = [o.get("label") for o in item.get("options") or []]
        if item.get("control") != YES_NO or labels != list(YES_NO_LABELS) or item.get("escape"):
            faults.append({key: "not yes_no", "control": item.get("control"), "options": labels,
                           "escape": item.get("escape")})
        q = " ".join(str(item.get("question") or "").split())
        if ts.framed_of(item) == ts.FRAMED_FILM:
            # spec 172 FR-6 (keel-cloud 285 FR-1): after the two films, code's short frames
            said = name or NO_NAME
            if key == COMPATIBILITY:
                ok = q == COMPATIBILITY_FILM
            elif key == RELATIVE_ADVANTAGE:
                ok = q == RELATIVE_ADVANTAGE_FILM.replace("{name}", said)
            elif setup:
                ok = bool(_pattern(ADOPTION_SETUP_FILM).match(q)) and ts._bare(setup[0]).split()[0] in ts._bare(q)
            else:
                ok = q == ADOPTION_NONE_FILM.replace("{name}", said)
            if not ok:
                faults.append({key: "the question's words (film)", "question": q, "setup": setup})
            long = [x for x in sentences(q) if len(x.split()) > FILM_MAX_WORDS]
            if long:
                faults.append({key: f"a sentence past {FILM_MAX_WORDS} words", "sentences": long})
            if (item.get("spoken") or {}).get("stem") and ts._words((item.get("spoken") or {}).get("stem")) != ts._words(q):
                faults.append({key: "spoken differs from text", "spoken": (item.get("spoken") or {}).get("stem")})
            continue
        if key == COMPATIBILITY:
            ok = _pattern(COMPATIBILITY_Q, name=name).match(q) or q == COMPATIBILITY_GIVING.replace("{name}", name)
        elif key == RELATIVE_ADVANTAGE:
            ok = _pattern(RELATIVE_ADVANTAGE_Q, name=name).match(q) or q == RELATIVE_ADVANTAGE_GIVING.replace(
                "{name}", name)
        elif setup:
            ok = _pattern(ADOPTION_SETUP_Q, name=name).match(q) and ts._bare(setup[0]).split()[-1] in ts._bare(q)
        else:
            ok = q == ADOPTION_NONE_Q.replace("{name}", name)
        if not ok:
            faults.append({key: "the question's words", "question": q, "setup": setup})
        if over_cap(q):
            faults.append({key: "a sentence past 20 words", "sentences": over_cap(q)})
        if (item.get("spoken") or {}).get("stem") and ts._words((item.get("spoken") or {}).get("stem")) != ts._words(q):
            faults.append({key: "spoken differs from text", "spoken": (item.get("spoken") or {}).get("stem")})
    return faults


def link_faults(interview: dict | None, *, founder: str, name: str, tagline: str | None,
                pilot: bool = True) -> list[dict]:
    """Spec 162 FR-5 on the wire (keel-cloud 272 FR-3, FR-4): the solution link's words -- `passages.opening` the
    founder's first name and the problem (one sentence, or two past the cap) and *First, one question.* where the
    screener follows; `passages.toTheFilm` *Let us see it.*; the check found by its words (*In {window}, have you
    encountered this issue?*, keel-cloud 277 FR-1, `three_surfaces.is_gate_words`); the problem's film and
    the idea's film both served; `plate` the brand (the name, the tagline) with `before` *Now {founder} has built
    {name}.* and `after` *and believes it solves this. Let us see.*; the idea card's three lines nowhere (`reveal`
    absent); the pilot ask *Would you try {name} for real?* where the founder offered one; every sentence within the
    cap."""
    iv = interview or {}
    faults: list[dict] = []
    passages = iv.get("passages") or {}
    gate = iv.get("gate") or {}
    screener = bool(((gate.get("condition") or iv.get("condition") or {}).get("question")))
    opening = ts._words(passages.get("opening"))
    first = OPENING.split("{people}")[0].replace("{founder}", founder)
    if not opening.startswith(first) or (screener != opening.endswith(ONE_QUESTION)):
        faults.append({"opening": opening, "founder": founder, "screener": screener})
    if passages.get("toTheFilm") != TO_THE_FILM:
        faults.append({"toTheFilm": passages.get("toTheFilm")})
    if not ts.is_gate_words(gate.get("question")):                      # spec 169 FR-1: by its words
        faults.append({"check": gate.get("question")})
    if not (iv.get("story") or {}).get("scenes") or not (iv.get("ideaStory") or {}).get("scenes"):
        faults.append({"films": {"story": bool(iv.get("story")), "ideaStory": bool(iv.get("ideaStory"))}})
    plate = iv.get("plate") or {}
    if plate.get("name") != name or (tagline is not None and plate.get("tagline") != tagline) \
            or plate.get("before") != PLATE_BEFORE.replace("{founder}", founder).replace("{name}", name) \
            or plate.get("after") != PLATE_AFTER:
        faults.append({"plate": plate})
    if "reveal" in iv and iv.get("reveal"):
        faults.append({"reveal": "the idea card served beside the film"})
    asked = (iv.get("pilot") or {}).get("question")
    if pilot and asked != PILOT.replace("{name}", name):
        faults.append({"pilot": asked})
    if not pilot and asked:
        faults.append({"pilot": "asked where the founder offered none", "question": asked})
    for where, text in (("opening", opening), ("plate.before", plate.get("before")), ("plate.after", plate.get("after")),
                        ("pilot", asked), ("toTheFilm", passages.get("toTheFilm"))):
        if over_cap(text):
            faults.append({where: "a sentence past 20 words", "sentences": over_cap(text)})
    return faults


def films_lines(interview: dict | None) -> dict:
    """The two films' lines as the link serves them (the lines to read instead), in order."""
    iv = interview or {}
    return {"problem": list((iv.get("story") or {}).get("readInstead") or []),
            "idea": list((iv.get("ideaStory") or {}).get("readInstead") or [])}


# ------------------------------------------------------------------------------------------- the people (FR-7)

#: Spec 162 FR-7: the five people every solution study is walked with -- their three answers, and the whys they are owed
#: (keel-cloud 272 FR-2: a why after every No, in the order asked, at most two; the third `capped`).
SOLUTION_ROSTER = (
    {"who": "yes on all three", "picks": {COMPATIBILITY: "yes", RELATIVE_ADVANTAGE: "yes", ADOPTION_FRICTION: "yes"},
     "owed": [], "capped": []},
    {"who": "a No on Compatibility alone", "picks": {COMPATIBILITY: "no", RELATIVE_ADVANTAGE: "yes",
                                                     ADOPTION_FRICTION: "yes"}, "owed": [COMPATIBILITY], "capped": []},
    {"who": "a No on Relative advantage alone", "picks": {COMPATIBILITY: "yes", RELATIVE_ADVANTAGE: "no",
                                                          ADOPTION_FRICTION: "yes"},
     "owed": [RELATIVE_ADVANTAGE], "capped": []},
    {"who": "a No on Adoption friction alone", "picks": {COMPATIBILITY: "yes", RELATIVE_ADVANTAGE: "yes",
                                                         ADOPTION_FRICTION: "no"},
     "owed": [ADOPTION_FRICTION], "capped": []},
    {"who": "three Nos", "picks": {COMPATIBILITY: "no", RELATIVE_ADVANTAGE: "no", ADOPTION_FRICTION: "no"},
     "owed": [COMPATIBILITY, RELATIVE_ADVANTAGE], "capped": [ADOPTION_FRICTION]},
)
#: What each person says to a why (any words; the fake transcriber hears them as said).
WHY_SAID = {COMPATIBILITY: "We would have to change how the whole team signs off first.",
            RELATIVE_ADVANTAGE: "It would have to catch what our own checks miss.",
            ADOPTION_FRICTION: "Connecting the two systems would take our IT team weeks."}


def owed(picks: dict[str, str]) -> tuple[list[str], list[str]]:
    """keel-cloud 272 FR-2, restated: the whys a person is owed -- every No, in the order asked -- up to two; the rest
    capped."""
    nos = [k for k in SOLUTION_DIMENSIONS if picks.get(k) == "no"]
    return nos[:MAX_FOLLOW_UPS], nos[MAX_FOLLOW_UPS:]


def answers_for(person: dict, interview: dict) -> list[dict]:
    """The three items one of `SOLUTION_ROSTER` answers, as `ItemAnswer`s (one option id each, by its label)."""
    out = []
    for key in SOLUTION_DIMENSIONS:
        item = ts.item_of(interview or {}, key)
        label = YES_NO_LABELS[YES_NO_CODES.index(person["picks"][key])]
        out.append({"itemId": item.get("itemId"), "optionIds": [ts.option_id(item, label=label)
                                                                or ts.option_id(item, code=person["picks"][key])]})
    return out


def response_for(person: dict, interview: dict, *, fmt: str, whys: list[dict]) -> dict:
    """Spec 162 FR-7 on the wire: the response one of `SOLUTION_ROSTER` sends on a 272 link -- the check's Yes
    (`recency: true`), no story (the film anchors it), the three answers, each why answered in order."""
    body: dict = {"format": fmt, "recency": True, "answers": answers_for(person, interview)}
    if whys:
        body["followUps"] = [{"dimension": w["dimension"], "text": WHY_SAID.get(str(w["dimension"]), "Because it does."),
                              "how": "RECORDED"} for w in whys]
    return body


def themes_entries(said: dict[str, list[str]]) -> list[dict]:
    """The scripted runtime's THEMES for the three solution rungs: one theme a rung, its label sharing words with its
    answers, never the rung's name."""
    labels = {COMPATIBILITY: "The whole team signs off first", RELATIVE_ADVANTAGE: "Catch what our checks miss",
              ADOPTION_FRICTION: "Connecting the two systems"}
    return [{"dimension": k, "outcome": "COMPLETED",
             "result": {"themes": [{"label": labels[k], "answers": sorted(set(v))}]}}
            for k, v in (said or {}).items() if k in labels and v]


# ------------------------------------------------------------------------------------------- the founder's page (FR-8)

def standing_of(standings: dict, key: str) -> dict:
    for vector in (standings or {}).get("vectors") or []:
        for row in (vector.get("dimensions") or []) + (vector.get("standings") or []):
            if row.get("dimension") == key:
                return row
    return {}


def share_faults(standings: dict, picks: list[dict[str, str]] | None = None) -> list[dict]:
    """Spec 162 FR-8 (keel-cloud 272 FR-6): the three Overview cards as share bars -- `chart.share` `{yes, n, proportion,
    founderBand}` (the founder's band `p_60_80` with its edges), the two bars' counts *Yes* and *No*, no `chart.benefit`;
    where `picks` (every person's answers) is given, `yes` and `n` are theirs."""
    faults: list[dict] = []
    for key in SOLUTION_DIMENSIONS:
        row = standing_of(standings, key)
        chart = row.get("chart") or {}
        share = chart.get("share")
        if not share:
            faults.append({key: "chart.share absent", "chart": sorted(chart)})
            continue
        if "benefit" in chart:
            faults.append({key: "chart.benefit served (keel-cloud 272: gone)"})
        if not share.get("founderBand"):
            faults.append({key: "founderBand", "share": share})
        if picks is not None:
            said = [p[key] for p in picks if p.get(key) in YES_NO_CODES]
            want = (said.count("yes"), len(said))
            if (share.get("yes"), share.get("n")) != want:
                faults.append({key: "yes / n", "served": [share.get("yes"), share.get("n")], "want": list(want)})
            elif want[1] and abs(float(share.get("proportion") or 0) - round(want[0] / want[1], 2)) > 0.011:
                faults.append({key: "proportion", "served": share.get("proportion")})
        counts = ((row.get("choice") or {}).get("optionCounts")) or []
        if counts and [ts._bare(c.get("label")) for c in counts] != [ts._bare(x) for x in YES_NO_LABELS]:
            faults.append({key: "bars", "labels": [c.get("label") for c in counts]})
    return faults


def so_line_faults(standings: dict) -> list[dict]:
    """Spec 162 FR-8: the three cards' So lines are evidence only -- no *should*, *next*, *try* -- and no benefit scale
    anywhere on the page (`a_lot_better`, *A lot better*)."""
    faults: list[dict] = []
    for key in SOLUTION_DIMENSIONS:
        row = standing_of(standings, key)
        for field in ("so", "soLine", "insight", "line"):
            text = str(row.get(field) or "")
            bad = [w for w in RECOMMENDATION_WORDS if re.search(rf"\b{w}\b", text, re.I)]
            if bad:
                faults.append({key: field, "words": bad, "text": text})
    blob = repr(standings)
    for word in ("a_lot_better", "A lot better", "a_little_better", "benefit_scale"):
        if word in blob:
            faults.append({"benefit scale": word})
    return faults


def brief_faults(facts: dict, picks: list[dict[str, str]] | None = None) -> list[dict]:
    """Spec 162 FR-8 (keel-cloud 272 FR-6): the brief's solution rows on `{yes, n, share, founderBand}`, no `benefit`."""
    solution = (facts or {}).get("solution") or {}
    rows = {r.get("key"): r for r in solution.get("rows") or []}
    faults: list[dict] = []
    if "benefit" in solution:
        faults.append({"facts.solution.benefit": "served (keel-cloud 272: gone)"})
    for key in SOLUTION_DIMENSIONS:
        r = rows.get(key)
        if not r:
            faults.append({key: "no brief row"})
            continue
        missing = [f for f in ("yes", "n", "share", "founderBand") if r.get(f) is None]
        if missing:
            faults.append({key: "missing", "fields": missing})
        if picks is not None:
            said = [p[key] for p in picks if p.get(key) in YES_NO_CODES]
            if (r.get("yes"), r.get("n")) != (said.count("yes"), len(said)):
                faults.append({key: "yes / n", "served": [r.get("yes"), r.get("n")],
                               "want": [said.count("yes"), len(said)]})
    return faults


def insights_faults(standings: dict, *, capped_by: dict[str, int] | None = None) -> list[dict]:
    """Spec 162 FR-7 (keel-cloud 272 FR-2, spec 119's view): the solution's Insights cards -- each rung's heading the
    registry's (*What would get in the way*, *What it would have to do better*, *What makes it a trouble*), the quotes
    carrying the option *No*, `capped` an integer with `asked + capped = against`, `tookBy` nowhere; `capped_by` the
    least capped each rung must show."""
    faults: list[dict] = []
    for i in (standings or {}).get("insights") or []:
        key = i.get("dimension")
        if key not in WHYS:
            continue
        if "tookBy" in i:
            faults.append({key: "tookBy served"})
        if not isinstance(i.get("capped"), int):
            faults.append({key: "capped", "served": i.get("capped")})
        elif int(i.get("asked") or 0) + int(i.get("capped") or 0) != int(i.get("against") or 0):
            faults.append({key: "asked + capped != against", "asked": i.get("asked"), "capped": i.get("capped"),
                           "against": i.get("against")})
        if i.get("rungHeading") not in (None, WHYS[key][1]):
            faults.append({key: "rungHeading", "served": i.get("rungHeading"), "want": WHYS[key][1]})
        for q in i.get("quotes") or []:
            if ts._bare(q.get("option") or q.get("optionLabel")) != ts._bare(ts.NO_OPTION):
                faults.append({key: "a quote without the option No", "quote": q})
        if capped_by and int(i.get("capped") or 0) < capped_by.get(key, 0):
            faults.append({key: "capped below the roster's", "capped": i.get("capped"), "want": capped_by[key]})
    return faults


# ------------------------------------------------------------------------------------------- three surfaces (FR-9)

def served_record(interview: dict | None) -> list[dict]:
    """Spec 162 FR-9 on the wire: the orb's or the face's script of a solution link as served, step by step -- the
    opening, the screener, the bridge, the problem's film (its lines), the check, the plate (its two lines), the idea's
    film (its lines), the three questions (their options, their whys), the pilot ask."""
    iv = interview or {}
    passages = iv.get("passages") or {}
    plate = iv.get("plate") or {}
    films = films_lines(iv)
    said = passages.get("opening")
    out = [ts.step("opening", f"{INTRODUCED} {HOW_TO_ANSWER} {said}" if said else said)]
    gate = iv.get("gate") or {}
    condition = (gate.get("condition") or iv.get("condition") or {}).get("question")
    if condition:
        out.append(ts.step("screener", condition, ["Yes", "No"]))
    out.append(ts.step("bridge", passages.get("toTheFilm")))
    out.append(ts.step("film:problem", " | ".join(films["problem"])))
    out.append(ts.step("check", gate.get("question"), ["Yes", ts._words(gate.get("noLabel") or "No")]))
    out.append(ts.step("plate", " ".join(x for x in (plate.get("before"), plate.get("after")) if x)))
    out.append(ts.step("film:idea", " | ".join(films["idea"])))
    whys = {}
    for f in iv.get("followUps") or []:
        if isinstance(f, dict) and f.get("dimension"):
            whys.setdefault(str(f["dimension"]), []).append(f.get("spoken") or f.get("text"))
    for part in iv.get("parts") or []:
        for item in part.get("items") or []:
            out.append(ts.step(str(item.get("dimension") or item.get("itemId")), item.get("question"),
                               ts._labels(item.get("options")), whys.get(str(item.get("dimension")))))
    if (iv.get("pilot") or {}).get("question"):
        out.append(ts.step("pilot", iv["pilot"]["question"], ["Yes", "No"]))
    return out


def _third(form: Any) -> str | None:
    if isinstance(form, dict):
        return form.get("third") or form.get("first")
    return form


def card_record(script: dict | None) -> list[dict]:
    """Spec 162 FR-9 on the wire: the Copilot card's script of the same study (`CallScript`, keel-cloud 272 FR-5) as
    the same steps -- the intro's opening, the gate passage's screener, bridge, the problem film's lines and the check,
    the plate passage's two lines and the idea film's lines, the three items with their hints, the pilot ask -- each in
    the link's form (`third`; the card reads `first`, the founder's own: its words are compared where the link has
    them)."""
    out: list[dict] = []
    for p in (script or {}).get("passages") or []:
        kind = p.get("kind")
        if kind == "intro":
            out.append(ts.step("opening", _third(p.get("text"))))
        elif kind == "gate":
            condition = (p.get("condition") or {}).get("question")
            if condition:
                out.append(ts.step("screener", condition, ["Yes", "No"]))
            out.append(ts.step("bridge", p.get("bridge")))
            out.append(ts.step("film:problem", " | ".join(p.get("lines") or [])))
            out.append(ts.step("check", p.get("stem"), ts._labels(p.get("options")), ts._hints(p.get("followUp"))
                               if p.get("followUp") else None))
        elif kind == "plate":
            out.append(ts.step("plate", " ".join(x for x in (_third(p.get("before")), _third(p.get("after"))) if x)))
            out.append(ts.step("film:idea", " | ".join(p.get("lines") or [])))
        elif kind == "item":
            out.append(ts.step(str(p.get("dimension") or p.get("itemId")), p.get("stem"), ts._card_labels(p),
                               ts._hints(p.get("followUp"))))
        elif kind == "pilot":
            out.append(ts.step("pilot", _third(p.get("question")), ["Yes", "No"]))
    return out


def card_problem_lines(script: dict | None) -> list[str]:
    """Spec 172 FR-5 (keel-cloud 283 FR-8): the problem film's lines the card's gate passage carries (on a solution
    study, the recap's five)."""
    for p in (script or {}).get("passages") or []:
        if p.get("kind") == "gate":
            return [ts._words(x) for x in p.get("lines") or []]
    return []


def first_person_faults(script: dict | None, *, name: str) -> list[dict]:
    """Spec 162 FR-9 (keel-cloud 272 FR-5): the card's first-person forms -- the opening *I believe ...*, the plate's
    *Now I have built {name}.* and *and I believe it solves this. Let us see.*"""
    faults: list[dict] = []
    for p in (script or {}).get("passages") or []:
        if p.get("kind") == "intro" and not str(((p.get("text") or {}).get("first")) or "").startswith("I believe"):
            faults.append({"intro.first": (p.get("text") or {}).get("first")})
        if p.get("kind") == "plate":
            before = (p.get("before") or {}).get("first")
            if before != PLATE_BEFORE_FIRST.replace("{name}", name):
                faults.append({"plate.before.first": before})
            if "I believe" not in str((p.get("after") or {}).get("first") or ""):
                faults.append({"plate.after.first": (p.get("after") or {}).get("first")})
    return faults


def solution_steps(records: Iterable[dict]) -> list[str]:
    return [r["step"] for r in records]


#: keel-cloud 269 / 272 (`StoryOnTheLink.FILM_WORDS_PER_SECOND`, `filmSeconds`): a film's lines at 2.5 words a second and a
#: second's hold on each scene; the plate's three seconds (keel-web 259 / 260 `PLATE_MS`).
FILM_WORDS_PER_SECOND = 2.5
PLATE_SECONDS = 3.0


def film_seconds(lines: list[str] | None) -> float:
    lines = [x for x in lines or [] if x is not None]
    if not lines:
        return 0.0
    return sum(len(x.split()) for x in lines if x.strip()) / FILM_WORDS_PER_SECOND + len(lines)


def first_question_seconds(interview: dict | None) -> dict:
    """Spec 162 FR-5 (D6: measured and recorded, never asserted): the time to the first of the three questions on a
    solution link as the cloud counts it -- the opening, the screener's own answer aside, the bridge, the problem's film,
    the check, the plate's two lines and its three seconds, the idea's film -- each line at 2.5 words a second."""
    iv = interview or {}
    passages, plate = iv.get("passages") or {}, iv.get("plate") or {}
    films = films_lines(iv)
    said = sum(len(str(x or "").split()) for x in (passages.get("opening"), passages.get("toTheFilm"),
                                                    (iv.get("gate") or {}).get("question"), plate.get("before"),
                                                    plate.get("after")))
    parts = {"spoken": round(said / FILM_WORDS_PER_SECOND, 1), "problem film": round(film_seconds(films["problem"]), 1),
             "plate": PLATE_SECONDS, "idea film": round(film_seconds(films["idea"]), 1)}
    return {"seconds": round(sum(parts.values()), 1), "parts": parts, "minutes served": iv.get("minutes")}
