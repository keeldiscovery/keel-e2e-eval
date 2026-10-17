"""The report marks (spec 052): keel-cloud 104's `StandingsView` (contract 19, the standings side) as keel-web 077's
report draws it -- the Overview, the Insights view, the Pilot view and *Download the brief*, their binding -- held over
one journey's record. Deterministic, zero spend, the shape of `evals/feedback_marks.py`: one check a mark, a mark whose
subject the record does not carry is **unmeasured** (reported, never passed).

Design of record: keel-cloud-docs `canon/designs/report-and-follow-up-design-2026-10-17.md` §3 (the card lines), §4
(the three views and the binding), §7 (the themes), D6 (no number twice) and D10 (nothing on the sheet the tabs do not
show). The marks are `instructions/marks.py`'s MARKS_VERSION 20 (calls 116-120): `report_overview` is also measured at
zero spend in the instruction eval (`instructions/overview.py`, keel-cloud's facts against the corpus's); the other
four read a page and are this module's alone (call 120).

- **`report_overview`**: the page's Overview equals the one `instructions/overview.py` draws from the wire's
  `StandingsView` -- the verdict's label and words, its line (*{How sure}. {reason}* and each failing dimension, or on
  KEEP_INTERVIEWING *{n} people have answered.* with the link to Interviews), the ship's three bands, the two tiles,
  per stage the name, the pill, the lead lines and every row (name, status word, card or *nobody has answered this
  yet*, its link to the stage page) in the registry's order, the foot; `StandingsView.priceMedian` equals
  `facts.commercial.priceMedian`; and nothing of the old deck (no `p.overall`, people tile, `.snaprow`,
  `.panel__count`, *A band opens its stage*, disabled download).
- **`report_insights`**: one box per dimension not holding up or split, worst first, each the served `insights[]`
  entry's words -- the name, the pill, the split line, the rung's heading with *· {answered} of the {against} said
  why*, the themes (label, count, up to three quotes each ending *— {Name}*), *Only k of the n were asked here…*,
  *No follow-up on this rung: …*, the raw *In their words* -- with the served numbers consistent (`asked + Σ tookBy ==
  against`, counts within `answered`, at most three themes and three quotes) and every quote a named person's own
  follow-up words; on the scripted stack (`strict`) the themes are the fake's grouping of the rung's follow-up answers
  (`harness/interviewer_fake.themes`), word for word; else the right one of the two empty states.
- **`report_no_repeat`** (D6, a literal check): outside a quote and the view's own *said why* / *Only k of the n* lines,
  the Insights view's text carries no `\\d+ of \\d+`, no currency figure, no `\\d+ months? out of`, and none of the
  Overview cards' `number` strings.
- **`report_pilot`**: one row per `StandingsView.pilotPeople[]` entry, in its order, with its name, role words, source,
  email only where the link carried one (a dataset's), and inside the gate (or the decision-makers' line), the story,
  every answer and the follow-up; those people are the ones the walks opted in; *Nobody has signed up yet.* before
  any; *Keel never emails on your behalf…* present.
- **`report_binding`** (D10, tokens: call 2): the print route's pages 1-3 carry no word of four letters or more and no
  number that the Overview, the Insights and the Pilot views do not (their page frame apart: kicker, title, meta,
  foot); page 1 draws no row; the breakdown's tokens are the stage pages' and the standings' (every number on it a
  number `StandingsView` carries); no *What to do next* anywhere, no old headline, and on a healthy project no *In
  their words*; the tab's title is *{project} — Keel brief — {date}* and *Preparing your brief…* came first.

The words marked *as 077 defines* in `instructions/overview.py` and below are keel-web 077's spec's, written before 077
was built; the journey pass holds them to what 077 drew and moves them here, not in the marks.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from harness import interviewer_fake as fake
from instructions import overview as ov
from instructions.brief_facts import BROKE_ON, VERDICT_WORDS, _plain

#: Bumped whenever a mark is born, retired, or reads its record differently.
REPORT_MARKS_VERSION = 1

# ------------------------------------------------------------------------- the Pilot view's words (as 077)

WHAT_THEY_AGREED = "What they agreed to"
WHAT_THEY_AGREED_LINE = ("They ticked the box at the end of the interview: Keel may share their name and address with "
                         "you for a pilot. Everything they answered is under their name.")
DM_ONLY = "Decision-makers answer the money part only."
KEEL_NEVER_EMAILS = "Keel never emails on your behalf. You write to them from your own mailbox."
NOBODY_SIGNED_UP = "Nobody has signed up yet."
SOURCE_WORDS = {"KNOWN": "You know them", "DATASET": "Contacts dataset", "KEEL_MANAGED": "Contacts dataset"}
ONE_LAST_THING = "One last thing"

# ------------------------------------------------------------------------------ the binding's words (as 077)

PREPARING = "Preparing your brief…"
INSIGHTS_PAGE_TITLE = "What the people who did not agree said"
BREAKDOWN_PAGE_TITLE = "Every card, every answer"
#: The breakdown tables' own chrome (their headings), which no view draws.
BREAKDOWN_CHROME = ("Dimension", "Card", "Answers", "Status", "tested", "not tested", "you said", "theirs",
                    "budget source", BREAKDOWN_PAGE_TITLE)
#: The old brief's words that may never come back on the sheet (design §4.5).
OLD_BRIEF_WORDS = ("What to do next",)

MARK_NAMES = ("report_overview", "report_insights", "report_no_repeat", "report_pilot", "report_binding")


@dataclass(frozen=True)
class Check:
    mark: str
    rule: str
    measured: bool
    ok: bool
    detail: Any = None


# ------------------------------------------------------------------------------------------ helpers

def _dims(standings: dict) -> list[dict]:
    return [d for v in standings.get("vectors") or [] for d in v.get("dimensions") or []]


def n_of(standings: dict) -> dict:
    return {d.get("dimension"): d.get("n") for d in _dims(standings)}


def card_order(standings: dict) -> list[str]:
    return [c.get("key") for c in (standings.get("facts") or {}).get("cards") or []]


def names_of(standings: dict, record: dict | None = None) -> dict:
    """`{invitationId: name}`: the walks' own invitations where the record carries them, else the stage rows'."""
    out = {}
    for d in _dims(standings):
        for p in d.get("people") or []:
            if p.get("invitationId"):
                out.setdefault(p["invitationId"], p.get("personName") or p.get("name"))
    for inv_id, inv in ((record or {}).get("invitations") or {}).items():
        out[inv_id] = inv.get("name")
    return out


def follow_up_answers(standings: dict, dimension: str) -> list[dict]:
    """The rung's follow-up answers as the stage row serves them (`people[].followUp`, contract 19): `[{id, text,
    name}]` in the row's order -- the themes job's input, and the fake's."""
    row = next((d for d in _dims(standings) if d.get("dimension") == dimension), None) or {}
    return [{"id": p.get("invitationId"), "text": p.get("followUp"), "name": p.get("personName") or p.get("name")}
            for p in row.get("people") or [] if p.get("followUp")]


def tokens(text: str) -> set:
    """`report_binding`'s unit (call 2): every word of four letters or more, lower-cased, and every number."""
    text = ov.norm(text).lower()
    return set(re.findall(r"[^\W\d_]{4,}", text)) | set(re.findall(r"\d+(?:[.,]\d+)*", text))


def _numbers_in(value) -> set:
    out: set = set()
    if isinstance(value, dict):
        for v in value.values():
            out |= _numbers_in(v)
    elif isinstance(value, list):
        for v in value:
            out |= _numbers_in(v)
    elif isinstance(value, bool) or value is None:
        pass
    elif isinstance(value, (int, float)):
        out |= set(re.findall(r"\d+(?:[.,]\d+)*", _plain(value)))
    else:
        out |= set(re.findall(r"\d+(?:[.,]\d+)*", str(value)))
    return out


def _words_in(value) -> str:
    """Every string the standings carry, one text (the breakdown's allowed vocabulary besides the stage pages)."""
    if isinstance(value, dict):
        return " ".join(_words_in(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_words_in(v) for v in value)
    return value if isinstance(value, str) else ""


# --------------------------------------------------------------------------------------- the Overview

def expected_overview(standings: dict) -> dict:
    facts = standings.get("facts") or {}
    return ov.overview(facts, price_median=standings.get("priceMedian"), n_of=n_of(standings),
                       use_facts_median=False)


def _label_class(label: str) -> set:
    label = str(label or "")
    return {f"l-{label}", f"l-{label.lower()}", f"l-{label.lower().replace('_', '-')}"}


def overview_faults(standings: dict, page: dict) -> list:
    want = expected_overview(standings)
    faults = []
    facts_median = ((standings.get("facts") or {}).get("commercial") or {}).get("priceMedian")
    if standings.get("priceMedian") != facts_median:
        faults.append({"priceMedian": standings.get("priceMedian"), "facts.commercial.priceMedian": facts_median})
    if ov.in_order(page.get("eyebrow") or page.get("text"), [want["eyebrow"]]):
        faults.append({"eyebrow": page.get("eyebrow"), "want": want["eyebrow"]})
    hero, got = want["hero"], page.get("hero") or {}
    if got.get("label") != hero["label"] or ov.norm(got.get("verdict")) != hero["verdict"]:
        faults.append({"verdict": [got.get("label"), got.get("verdict")], "want": [hero["label"], hero["verdict"]]})
    if not (set(str(got.get("class") or "").split()) & _label_class(hero["label"])):
        faults.append({"verdict class": got.get("class"), "want": sorted(_label_class(hero["label"]))})
    missing = ov.in_order(got.get("text"), [hero["kicker"]] + hero["why"])
    if missing:
        faults.append({"hero": got.get("text"), "missing": missing})
    if bool(got.get("send_more")) is not hero["send_more"]:
        faults.append({"send more": got.get("send_more"), "want": hero["send_more"]})
    if hero["send_more"] and not str((got.get("send_more") or {}).get("href") or "").endswith("/interviews/sent"):
        faults.append({"send more href": got.get("send_more")})
    missing = ov.in_order(got.get("caption"), hero["caption"])
    if missing:
        faults.append({"caption": got.get("caption"), "missing": missing})
    bands = page.get("bands") or []
    if sorted(b.get("stage") for b in bands) != sorted(ov.VECTORS):
        faults.append({"bands": bands})
    for name in ("pilot", "price"):
        tile = (page.get("tiles") or {}).get(name) or {}
        missing = ov.in_order(tile.get("text"), want["tiles"][name])
        if missing or not tile.get("present"):
            faults.append({f"tile:{name}": tile.get("text"), "missing": missing})
    for vector in ov.VECTORS:
        w, g = want["panels"][vector], (page.get("panels") or {}).get(vector) or {}
        missing = ov.in_order(g.get("head"), [w["name"], w["pill"]]) + ov.in_order(g.get("lead"), w["lead"])
        if missing:
            faults.append({f"panel:{vector}": {"head": g.get("head"), "lead": g.get("lead")}, "missing": missing})
        rows = g.get("rows") or []
        if [r.get("key") for r in rows] != [r["key"] for r in w["rows"]]:
            faults.append({f"rows:{vector}": [r.get("key") for r in rows], "want": [r["key"] for r in w["rows"]]})
            continue
        for wr, gr in zip(w["rows"], rows):
            missing = ov.in_order(gr.get("text"), wr["parts"])
            if missing or not str(gr.get("href") or "").endswith(wr["href"]):
                faults.append({f"row:{wr['key']}": gr, "missing": missing, "href": wr["href"]})
    missing = ov.in_order(page.get("foot"), want["foot"])
    if missing:
        faults.append({"foot": page.get("foot"), "missing": missing})
    old = {k: v for k, v in (page.get("old_deck") or {}).items() if v}
    old_words = [w for w in ov.OLD_DECK_WORDS if w.lower() in ov.norm(page.get("text")).lower()]
    if old or old_words:
        faults.append({"the old deck": old, "words": old_words})
    download = page.get("download") or {}
    if not (download.get("present") and download.get("enabled")
            and str(download.get("href") or "").endswith("/print")):
        faults.append({"download": download})
    return faults


def report_overview(r: dict) -> tuple[bool, Any]:
    """The Overview is the wire's, drawn: verdict, line, ship, tiles, panels, rows, foot; nothing of the old deck."""
    faults = overview_faults(r["standings"], r["overview"])
    return not faults, {"faults": faults}


# --------------------------------------------------------------------------------------- the Insights

_RANK = {"NOT_HOLDING_UP": 0, "PEOPLE_DISAGREE": 1}


def failing_dimensions(standings: dict) -> list[str]:
    """Every dimension not holding up or split, worst first, then in the registry's (the cards') order."""
    order = {k: i for i, k in enumerate(card_order(standings))}
    rows = [d for d in _dims(standings) if d.get("status") in BROKE_ON]
    rows.sort(key=lambda d: (_RANK[d.get("status")], order.get(d.get("dimension"), 99)))
    return [d.get("dimension") for d in rows]


def thin(standings: dict) -> bool:
    """The *Nothing to read into yet* state: the decision says keep interviewing, or a card is too few or unasked
    (spec 052 call 4: *Nothing is failing* says every dimension holds on 10 or more, untrue on a project nobody has
    answered)."""
    facts = standings.get("facts") or {}
    if (facts.get("decision") or {}).get("label") == "KEEP_INTERVIEWING":
        return True
    return any(c.get("status") in ov.THIN for c in facts.get("cards") or [])


def expected_box(insight: dict) -> dict:
    """One box's words, from its served `insights[]` entry."""
    themes = [{"label": t.get("label"), "count": t.get("count"),
               "quotes": [fake.quote_words(q) for q in t.get("quotes") or []]} for t in insight.get("themes") or []]
    heading = insight.get("rungHeading")
    return {
        "key": insight.get("dimension"),
        "head": [insight.get("name"), VERDICT_WORDS.get(insight.get("status"), insight.get("status"))],
        "split": fake.SPLIT_NOTE if insight.get("status") == "PEOPLE_DISAGREE" else None,
        "concern": fake.said_why(heading, insight.get("answered"), insight.get("against")) if heading else None,
        "themes": themes,
        "took_by": fake.took_by(insight.get("asked"), insight.get("against"), insight.get("tookBy"))
        if insight.get("tookBy") else None,
        "no_follow_up": fake.no_follow_up(insight.get("noQuestionWhy"))
        if not heading and insight.get("noQuestionWhy") else None,
        "raw": [fake.quote_words(q) for q in insight.get("rawQuotes") or []] if insight.get("raw") else None,
    }


def predicted_themes(standings: dict, insight: dict) -> list[dict]:
    """The fake's grouping of the rung's follow-up answers, served as the standings serve themes."""
    answers = follow_up_answers(standings, insight.get("dimension"))
    by_id = {a["id"]: {"name": a["name"], "text": a["text"]} for a in answers}
    grouped = fake.themes([{"id": a["id"], "text": a["text"]} for a in answers], insight.get("name") or "")
    return [{"label": t["label"], "count": len(t["answerIds"]), "quotes": fake.served_quotes(t["answerIds"], by_id)}
            for t in grouped["themes"]]


def insight_faults(standings: dict, page: dict, *, strict: bool, names: dict) -> list:
    faults = []
    want_dims = failing_dimensions(standings)
    served = {i.get("dimension"): i for i in standings.get("insights") or []}
    if sorted(served) != sorted(want_dims):
        faults.append({"insights[] dimensions": sorted(served), "failing": sorted(want_dims)})
    boxes = page.get("boxes") or []
    if [b.get("key") for b in boxes] != want_dims:
        faults.append({"boxes": [b.get("key") for b in boxes], "want": want_dims})
    for key, insight in served.items():
        heading = insight.get("rungHeading")
        if heading and int(insight.get("asked") or 0) + sum(int(t.get("count") or 0) for t in insight.get("tookBy")
                                                             or []) != int(insight.get("against") or 0):
            faults.append({key: "asked + tookBy != against", "insight": insight})
        themes = insight.get("themes") or []
        if len(themes) > fake.THEMES_MAX or any(len(t.get("quotes") or []) > fake.QUOTES_MAX for t in themes) \
                or len(insight.get("rawQuotes") or []) > fake.QUOTES_MAX:
            faults.append({key: "more than three themes or quotes", "insight": insight})
        if sum(int(t.get("count") or 0) for t in themes) > int(insight.get("answered") or 0):
            faults.append({key: "themes count past answered", "insight": insight})
        said = {a["id"]: a["text"] for a in follow_up_answers(standings, key)}
        for q in [q for t in themes for q in t.get("quotes") or []] + list(insight.get("rawQuotes") or []):
            if said.get(q.get("invitationId")) != q.get("text") or names.get(q.get("invitationId")) != q.get("name"):
                faults.append({key: "a quote not a named person's own follow-up", "quote": q,
                               "said": said.get(q.get("invitationId")), "name": names.get(q.get("invitationId"))})
        if strict and heading and not insight.get("raw"):
            want = predicted_themes(standings, insight)
            have = [{"label": t.get("label"), "count": t.get("count"),
                     "quotes": [{k: q.get(k) for k in ("invitationId", "name", "text")} for q in t.get("quotes") or []]}
                    for t in themes]
            if have != want:
                faults.append({key: "themes are not the fake's grouping", "served": have, "fake": want})
        if heading and heading != fake.RUNG_HEADINGS.get(key):
            faults.append({key: "rung heading", "served": heading, "registry": fake.RUNG_HEADINGS.get(key)})
    by_key = {b.get("key"): b for b in boxes}
    for key in want_dims:
        if key not in served or key not in by_key:
            continue
        want, got = expected_box(served[key]), by_key[key]
        missing = ov.in_order(got.get("head"), want["head"])
        for part in ("split", "concern", "took_by", "no_follow_up"):
            if want[part] is not None:
                missing += ov.in_order(got.get("text"), [want[part]])
            elif part in ("split", "took_by", "no_follow_up") and got.get(part):
                faults.append({key: f"{part} drawn where the wire has none", "drawn": got.get(part)})
        drawn = got.get("themes") or []
        if [(ov.norm(t.get("label")), t.get("count")) for t in drawn] != \
                [(ov.norm(t["label"]), t["count"]) for t in want["themes"]]:
            faults.append({key: "themes", "drawn": drawn, "wire": want["themes"]})
        else:
            for wt, gt in zip(want["themes"], drawn):
                if [ov.norm(q) for q in gt.get("quotes") or []] != [ov.norm(q) for q in wt["quotes"]]:
                    faults.append({key: f"quotes of {wt['label']}", "drawn": gt.get("quotes"), "wire": wt["quotes"]})
        if want["raw"] is not None:
            missing += ov.in_order(got.get("text"), [fake.IN_THEIR_WORDS] + want["raw"])
        if missing:
            faults.append({key: got.get("text"), "missing": missing})
    if not want_dims:
        n = int(((standings.get("facts") or {}).get("pilot") or {}).get("finished") or 0)
        want_empty = [fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(n)] if thin(standings) \
            else [fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE]
        missing = ov.in_order(page.get("empty"), want_empty)
        if missing or boxes:
            faults.append({"empty state": page.get("empty"), "want": want_empty, "boxes": len(boxes)})
    elif page.get("empty"):
        faults.append({"empty state drawn beside boxes": page.get("empty")})
    return faults


def report_insights(r: dict) -> tuple[bool, Any]:
    """One box a failing dimension, worst first, its served words; the themes the fake's on the stack; else the right
    empty state."""
    standings = r["standings"]
    faults = insight_faults(standings, r["insights"], strict=bool(r.get("strict")), names=names_of(standings, r))
    return not faults, {"faults": faults, "strict": bool(r.get("strict"))}


def repeats(text: str, quotes, own_lines, numbers) -> list:
    """D6's literal check: what of `text`, once its quotes and its own *said why* lines are taken out, repeats a
    number -- a *k of n*, a currency figure, a *k months out of*, or one of the Overview cards' numbers."""
    rest = ov.norm(text)
    for cut in sorted([ov.norm(q) for q in list(quotes or []) + list(own_lines or []) if q], key=len, reverse=True):
        rest = rest.replace(cut, " ")
    found = [m.group(0) for p in ov.NO_REPEAT_PATTERNS for m in p.finditer(rest)]
    found += [n for n in numbers if n and ov.norm(n) in rest]
    return found


def report_no_repeat(r: dict) -> tuple[bool, Any]:
    """D6: the Insights view repeats no number the Overview shows (quotes and its own said-why lines apart)."""
    page = r["insights"]
    numbers = [c.get("number") for c in (r["standings"].get("facts") or {}).get("cards") or [] if c.get("number")]
    found = repeats(page.get("text"), page.get("quotes"), page.get("own_lines"), numbers)
    return not found, {"repeated": found}


# ------------------------------------------------------------------------------------------- the Pilot

def window_words(standings: dict) -> str | None:
    card = next((c for c in (standings.get("facts") or {}).get("cards") or []
                 if c.get("key") == "problem.prevalence"), None) or {}
    line = str(card.get("line") or "")
    return line[len("had it in "):] if line.startswith("had it in ") else None


def expected_person(standings: dict, person: dict) -> dict:
    names = {c.get("key"): c.get("name") for c in (standings.get("facts") or {}).get("cards") or []}
    source = SOURCE_WORDS.get(person.get("source"), person.get("source"))
    if person.get("source") == "DATASET" and person.get("datasetName"):
        source = person["datasetName"]
    inside = []
    if person.get("link") == "COMMERCIAL_B2B" or person.get("gate") is None:
        inside.append(DM_ONLY)
    else:
        window = window_words(standings)
        inside += [f"Had it in {window}" if window else "Had it in", "Yes" if person.get("gate") else "No"]
    if person.get("story"):
        inside.append(person["story"])
    for answer in person.get("answers") or []:
        inside += [answer.get("name"), answer.get("words")]
    follow = person.get("followUp")
    if follow:
        inside += [ONE_LAST_THING, names.get(follow.get("dimension"), follow.get("dimension")), follow.get("text")]
    return {"invitation": person.get("invitationId"), "summary": [person.get("name"), person.get("words"), source],
            "email": person.get("email"), "inside": inside}


def pilot_faults(standings: dict, page: dict, *, opted_in=None, invitations=None) -> list:
    faults = []
    people = standings.get("pilotPeople") or []
    want_tile = ov.tiles(standings.get("facts") or {}, standings.get("priceMedian"))["pilot"]
    tile = (page.get("tiles") or {}).get("pilot") or {}
    missing = ov.in_order(tile.get("text"), want_tile)
    if missing:
        faults.append({"pilot tile": tile.get("text"), "missing": missing})
    agreed = (page.get("tiles") or {}).get("agreed") or {}
    missing = ov.in_order(agreed.get("text"), [WHAT_THEY_AGREED, WHAT_THEY_AGREED_LINE])
    if missing:
        faults.append({"what they agreed to": agreed.get("text"), "missing": missing})
    rows = page.get("people") or []
    if [p.get("invitation") for p in rows] != [p.get("invitationId") for p in people]:
        faults.append({"rows": [p.get("invitation") for p in rows], "pilotPeople": [p.get("invitationId")
                                                                                    for p in people]})
    else:
        for person, row in zip(people, rows):
            want = expected_person(standings, person)
            missing = ov.in_order(row.get("summary"), want["summary"]) + ov.in_order(row.get("inside"), want["inside"])
            if ov.norm(row.get("email")) != ov.norm(want["email"]):
                missing.append(f"email {want['email']!r}, drawn {row.get('email')!r}")
            if missing:
                faults.append({person.get("invitationId"): row, "missing": missing})
    for person in people:
        if person.get("email") and person.get("source") != "DATASET":
            faults.append({person.get("invitationId"): "an email on a link that carried none", "person": person})
        carried = ((invitations or {}).get(person.get("invitationId")) or {}).get("email")
        if invitations is not None and person.get("email") and person.get("email") != carried:
            faults.append({person.get("invitationId"): "an email the invitation did not carry",
                           "served": person.get("email"), "invitation": carried})
    if opted_in is not None and sorted(p.get("invitationId") for p in people) != sorted(opted_in):
        faults.append({"pilotPeople": sorted(p.get("invitationId") for p in people), "opted in": sorted(opted_in)})
    if not people:
        if ov.in_order(page.get("none"), [NOBODY_SIGNED_UP]):
            faults.append({"nobody yet": page.get("none"), "want": NOBODY_SIGNED_UP})
    elif page.get("none"):
        faults.append({"nobody yet drawn beside people": page.get("none")})
    if ov.in_order(page.get("foot") or page.get("text"), [KEEL_NEVER_EMAILS]):
        faults.append({"foot": page.get("foot"), "want": KEEL_NEVER_EMAILS})
    return faults


def report_pilot(r: dict) -> tuple[bool, Any]:
    """One row a served pilot person, the walks' own opt-ins; emails where a dataset link carried one; the foot."""
    faults = pilot_faults(r["standings"], r["pilot"], opted_in=r.get("opted_in"), invitations=r.get("invitations"))
    return not faults, {"faults": faults}


# ----------------------------------------------------------------------------------------- the binding

def frame_text(page: dict) -> str:
    return " ".join(str(page.get(k) or "") for k in ("kicker", "title", "meta", "foot"))


def binding_faults(r: dict) -> list:
    binding, standings = r["binding"], r["standings"]
    faults = []
    pages = binding.get("pages") or []
    numbered = [p.get("page") for p in pages]
    if numbered[:3] != [1, 2, 3] or len(pages) < 4:
        faults.append({"pages": numbered, "want": "1, 2, 3, then the breakdown"})
    views = {1: (r.get("overview") or {}).get("text"), 2: (r.get("insights") or {}).get("text"),
             3: (r.get("pilot") or {}).get("text")}
    for page in pages:
        n = page.get("page")
        own = tokens(page.get("text")) - tokens(frame_text(page))
        if n in views:
            extra = own - tokens(views[n])
            if extra:
                faults.append({f"page {n}": "words no view shows", "extra": sorted(extra)})
            if n == 1 and page.get("rows"):
                faults.append({"page 1": f"{page.get('rows')} rows drawn (the lead lines only)"})
        elif isinstance(n, int) and n >= 4:
            allowed = tokens(" ".join((r.get("stage_pages") or {}).values())) | tokens(_words_in(standings)) \
                | tokens(" ".join(BREAKDOWN_CHROME)) | _numbers_in(standings)
            extra = own - allowed
            if extra:
                faults.append({f"page {n}": "words or numbers neither the stage pages nor the standings carry",
                               "extra": sorted(extra)})
    sheet = ov.norm(" ".join(p.get("text") or "" for p in pages)).lower()
    for words in OLD_BRIEF_WORDS:
        if words.lower() in sheet:
            faults.append({"the old brief": words})
    if binding.get("old_headline"):
        faults.append({"the old brief": "a headline"})
    if not failing_dimensions(standings) and fake.IN_THEIR_WORDS.lower() in sheet:
        faults.append({"a healthy project's sheet": fake.IN_THEIR_WORDS})
    want_title = f"{r.get('project')} — Keel brief — {r.get('date')}"
    if ov.norm(binding.get("title")) != ov.norm(want_title):
        faults.append({"title": binding.get("title"), "want": want_title})
    if not binding.get("preparing_seen"):
        faults.append({"preparing": f"{PREPARING!r} was not drawn before the pages"})
    return faults


def report_binding(r: dict) -> tuple[bool, Any]:
    """D10: the sheet's pages 1-3 say nothing their views do not; the breakdown nothing the stage pages and the
    standings do not; no old brief; the title and the wait."""
    faults = binding_faults(r)
    return not faults, {"faults": faults}


# -------------------------------------------------------------------------------------------- the card

#: `(mark, the record keys it reads, the rule)`.
MARKS = [
    ("report_overview", ("standings", "overview"), report_overview),
    ("report_insights", ("standings", "insights"), report_insights),
    ("report_no_repeat", ("standings", "insights"), report_no_repeat),
    ("report_pilot", ("standings", "pilot"), report_pilot),
    ("report_binding", ("standings", "binding", "overview", "insights", "pilot"), report_binding),
]


def score(record: dict) -> list[Check]:
    checks = []
    for mark, keys, rule in MARKS:
        doc = (rule.__doc__ or "").strip().split("\n")[0]
        if not all(k in record for k in keys):
            checks.append(Check(mark, doc, measured=False, ok=False))
            continue
        try:
            ok, detail = rule(record)
        except (KeyError, TypeError, IndexError, ValueError, AttributeError) as broken:
            ok, detail = False, {"record could not be read": repr(broken)}
        checks.append(Check(mark, doc, measured=True, ok=bool(ok), detail=detail))
    return checks


def owed(record: dict) -> list[str]:
    """Every mark whose subject this record carries."""
    return [m for m, keys, _ in MARKS if all(k in record for k in keys)]


def scorecard(record: dict) -> dict:
    checks = score(record)
    measured = [c for c in checks if c.measured]
    return {"version": REPORT_MARKS_VERSION,
            "measured": len(measured), "met": sum(c.ok for c in measured),
            "unmeasured": [c.mark for c in checks if not c.measured],
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok,
                        "detail": json.loads(json.dumps(c.detail, default=str))} for c in checks]}
