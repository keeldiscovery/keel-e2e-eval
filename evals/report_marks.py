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
  per stage the name, the pill, no lead line (v2: keel-web 113 FR-4 keeps it on the brief's page one) and every row
  (name, status word, card or *nobody has answered this yet*, its link to the stage page) in the registry's order, the
  foot; `StandingsView.priceMedian` equals
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
  foot); page 1 draws no row, and every panel's lead lines as `instructions/overview.py` draws them from the wire (v2:
  the sheet's own words, as its frame is); the breakdown's tokens are the stage pages' and the standings' (every number on it a
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
from instructions.brief_facts import BAR_LINES, BROKE_ON, DID_NOT_HOLD, _plain, bar_words

#: Bumped whenever a mark is born, retired, or reads its record differently.
#: v1 (spec 052): the five born. v2 (spec 073 FR-3, keel-web 113 FR-4): the panel lead line leaves the full Overview --
#: `report_overview` holds it absent there (the rows carry the state as before) and `report_binding` holds it on page one,
#: counted as the sheet's own words (113 J-13).
REPORT_MARKS_VERSION = 2

# ------------------------------------------------------------------------- the Pilot view's words (as 077)

WHAT_THEY_AGREED = "What they agreed to"
WHAT_THEY_AGREED_LINE = ("They ticked the box at the end of the interview: Keel may share their name and address with "
                         "you for a pilot. Everything they answered is under their name.")
DM_ONLY = "Decision-makers answer the money part only."
KEEL_NEVER_EMAILS = "Keel never emails on your behalf. You write to them from your own mailbox."
NOBODY_SIGNED_UP = "Nobody has signed up yet."
SOURCE_WORDS = {"KNOWN": "You know them", "DATASET": "Contacts dataset", "KEEL_MANAGED": "Keel-managed"}
ONE_LAST_THING = "One last thing"

# ------------------------------------------------------------------------------ the binding's words (as 077)

PREPARING = "Preparing your brief…"
INSIGHTS_PAGE_TITLE = "What the people who did not agree said"
BREAKDOWN_PAGE_TITLE = "Every card, every answer"
#: The breakdown tables' own chrome (their headings), which no view draws.
BREAKDOWN_CHROME = ("Dimension", "Card", "Answers", "Status", "Tested:", "Not tested:", "You said", "theirs",
                    "Budget source:", "Not asked yet", BREAKDOWN_PAGE_TITLE, "Price table", "From",
                    "Already lose this much or more", "Already spend this much or more", "Chose this band or higher",
                    "Start here", "Test this", "Half or more would pay", "or more")
#: The old brief's words that may never come back on the sheet (design §4.5).
OLD_BRIEF_WORDS = ("What to do next",)

_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December")


def day_words(instant: str | None) -> str:
    """keel-web 077 `dayWords`: *17 October 2026*, from an instant's UTC day (the binding's tab title)."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(instant or ""))
    return f"{int(m.group(3))} {_MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else ""


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
    served = {v.get("vector"): {k: v[k] for k in ("dimensionsHolding", "dimensionsTotal", "peopleAnswered") if k in v}
              for v in standings.get("vectors") or []}
    people = standings.get("people") or {}
    return ov.overview(facts, price_median=standings.get("priceMedian"), n_of=n_of(standings),
                       use_facts_median=False, served=served, answered=people.get("answered"))


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
        missing = ov.in_order(g.get("head"), [w["name"], w["pill"]])
        if missing:
            faults.append({f"panel:{vector}": {"head": g.get("head")}, "missing": missing})
        # keel-web 113 FR-4 (spec 073 FR-3): the full Overview's panels draw no lead line -- the rows carry the detail;
        # the lead is held on the brief's page one (`binding_faults`)
        if g.get("lead") or g.get("leads"):
            faults.append({f"panel:{vector}": {"lead": g.get("lead"), "leads": g.get("leads")},
                           "want": "no lead line on the full Overview"})
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
#: keel-cloud 119: `insights[]` worst status first, the vectors' order within a status.
_INSIGHT_RANK = {"NOT_HOLDING_UP": 0, "PEOPLE_DISAGREE": 1, "TOO_FEW_TO_CALL": 2, "NOT_ASKED_YET": 3, "HOLDING_UP": 4,
                 "LEFT_OUT": 5}


def failing_dimensions(standings: dict) -> list[str]:
    """Every dimension not holding up or split, worst first, then in the registry's (the cards') order."""
    order = {k: i for i, k in enumerate(card_order(standings))}
    rows = [d for d in _dims(standings) if d.get("status") in BROKE_ON]
    rows.sort(key=lambda d: (_RANK[d.get("status")], order.get(d.get("dimension"), 99)))
    return [d.get("dimension") for d in rows]


def worded_dimensions(standings: dict) -> list[str]:
    """Spec 064 FR-8a (keel-cloud 119 FR-1): a box for every dimension on which at least one follow-up with words is
    stored, any status -- worst status first, the registry's order within one."""
    order = {k: i for i, k in enumerate(card_order(standings))}
    rows = [d for d in _dims(standings) if follow_up_answers(standings, d.get("dimension"))]
    rows.sort(key=lambda d: (_INSIGHT_RANK.get(d.get("status"), 9), order.get(d.get("dimension"), 99)))
    return [d.get("dimension") for d in rows]


def thin(standings: dict) -> bool:
    """The *Nothing to read into yet* state, keel-web 079's `insightsStateOf` (design §4.2's rule, DRIFT #93 closed):
    no box, and the verdict KEEP_INTERVIEWING, or nobody has answered (`pilot.finished` 0), or a card TOO_FEW_TO_CALL.
    *Nothing is failing* -- whose line says every dimension holds on 10 or more people -- only on a called verdict
    with no box (spec 052 call 4, back to the design's rule by the amendment of 2026-10-17 (b))."""
    facts = standings.get("facts") or {}
    if (facts.get("decision") or {}).get("label") == "KEEP_INTERVIEWING":
        return True
    if int((facts.get("pilot") or {}).get("finished") or 0) == 0:
        return True
    return any(c.get("status") == "TOO_FEW_TO_CALL" for c in facts.get("cards") or [])


def _theme_label(theme: dict) -> str:
    return fake.ON_THEIR_OWN_WORDS if theme.get("label") == fake.ON_THEIR_OWN else str(theme.get("label") or "")


#: keel-web 106 FR-2 (`CONSUMER_WORDS`, keel-cloud 128 FR-5): the words a consumer study's report never says.
CONSUMER_REPORT_WORDS = ("decision-makers", "decision-maker", "the payer", "per person", "new money")


def consumer_report_words(board: dict | None, insights: dict | None) -> list:
    """Spec 068 FR-4 (keel-web 106 FR-2): every place a consumer study's report says one of `CONSUMER_REPORT_WORDS` in
    its own words -- the Overview's tiles, panel leads and rows, the Insights boxes' heads, rung headings, frames, theme
    labels, footers and the not-asked lines; never a person's quote. `[{where, word, text}]`, empty when clean."""
    places = []
    for name, tile in ((board or {}).get("tiles") or {}).items():
        places.append((f"tile:{name}", tile.get("text")))
    for vector, panel in ((board or {}).get("panels") or {}).items():
        places.append((f"lead:{vector}", panel.get("lead")))
        places += [(f"row:{r.get('key')}", r.get("text")) for r in panel.get("rows") or []]
    for box in (insights or {}).get("boxes") or []:
        key = box.get("key")
        places += [(f"insight:{key}:{part}", box.get(part)) for part in ("head", "concern", "frame", "took_by")]
        places += [(f"insight:{key}:theme", t.get("label")) for t in box.get("themes") or []]
    places += [(f"not_asked:{n.get('key')}", n.get("text")) for n in (insights or {}).get("not_asked") or []]
    out = []
    for where, text in places:
        low = " ".join(str(text or "").split()).lower()
        for word in CONSUMER_REPORT_WORDS:
            if re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", low):
                out.append({"where": where, "word": word, "text": text})
    return out


def guessed_of(standings: dict) -> frozenset:
    """keel-web 106 FR-4 (`insightFooter.guessedOf`, keel-cloud 128 FR-17; spec 068 FR-4): the invitations whose story
    was read GUESSED -- their words are never quoted as a said answer, but drawn apart at the box's foot."""
    return frozenset(str(p.get("invitationId")) for v in standings.get("vectors") or []
                     for d in v.get("dimensions") or [] for p in d.get("people") or []
                     if p.get("anchoring") == "GUESSED" and p.get("invitationId") is not None)


_SPLIT_WORD = re.compile(r"(?i)^people disagree$")


def line_word(key: str | None, status: str | None, standing: dict | None = None, card: dict | None = None) -> str:
    """Spec 070 FR-3 (keel-web `lineWordOf` over `barWord`, spec 106 FR-3): the box's pill as keel-web draws it -- the
    card's served word (its `statusWords` before ` · `) where the card's status is the box's, so a Purchase friction fear
    that did not hold reads the card's own *Your fear was ... Not the blocker you expected.* (S-014 on the 130 build);
    on a bar line's amber never *People disagree* (`bar_words`); else the status's word."""
    served = ov.head((card or {}).get("statusWords")) if card and card.get("status") == status \
        and (card or {}).get("statusWords") else None
    engine = served or bar_words(key, {**(standing or {}), "status": status})
    if status != "PEOPLE_DISAGREE" or key not in BAR_LINES:
        return engine
    if served and not _SPLIT_WORD.match(served.strip()):
        return served
    return bar_words(key, {**(standing or {}), "status": status})


def pill_words(standings: dict) -> list[str]:
    """Spec 070 FR-3: every served box's pill (`line_word`) -- the card's own line drawn again, the view's own words for
    D6 as the frame and the heading are."""
    cards = {c.get("key"): c for c in ((standings or {}).get("facts") or {}).get("cards") or []}
    rows = {d.get("dimension"): d for v in (standings or {}).get("vectors") or [] for d in v.get("dimensions") or []}
    return [line_word(i.get("dimension"), i.get("status"), rows.get(i.get("dimension")), cards.get(i.get("dimension")))
            for i in (standings or {}).get("insights") or []]


def expected_box(insight: dict, standing: dict | None = None, guessed: frozenset = frozenset(),
                 card: dict | None = None) -> dict:
    """One box's words, from its served `insights[]` entry (contract 28, keel-web 095): the name and pill, the split
    line, the rung heading alone, the dissent frame, *Only k of the n*, then by state -- GROUPED the themes (*On their
    own* last), GROUPING *Keel is grouping what they said…* and the quotes, RAW *In their own words*, the note and the
    quotes."""
    state = insight.get("state") or ("RAW" if insight.get("raw") else "GROUPED")
    said = lambda q: str(q.get("invitationId")) not in guessed  # noqa: E731 - keel-web 106 FR-4: GUESSED drawn apart
    themes = [{"label": _theme_label(t), "count": t.get("count"),
               "quotes": [fake.quote_words(q) for q in t.get("quotes") or [] if said(q)]}
              for t in insight.get("themes") or []] if state == "GROUPED" else []
    every = [q for t in insight.get("themes") or [] for q in t.get("quotes") or []] if state == "GROUPED" else \
        list(insight.get("rawQuotes") or insight.get("quotes") or [])
    loose = [fake.quote_words(q) for q in (insight.get("rawQuotes") or insight.get("quotes") or []) if said(q)]
    # keel-web 106 FR-3 (keel-cloud 128 FR-8, spec 068 FR-4): a bar line's amber is *Did not hold* past the bar, with no
    # split note (Purchase friction's held fear *Holding up*); the standing's counts decide it, the insight's status else
    word = line_word(insight.get("dimension"), insight.get("status"), standing, card)
    return {
        "key": insight.get("dimension"), "state": state, "dissent": bool(insight.get("dissent")),
        "head": [insight.get("name"), word],
        "split": fake.SPLIT_NOTE if insight.get("status") == "PEOPLE_DISAGREE" and word != DID_NOT_HOLD else None,
        "concern": insight.get("rungHeading") or None,
        "frame": insight.get("frame") if insight.get("dissent") else None,
        "themes": themes,
        "took_by": fake.took_by(insight.get("asked"), insight.get("against"), insight.get("tookBy"))
        if insight.get("tookBy") else None,
        "grouping": loose if state == "GROUPING" else None,
        "raw": loose if state == "RAW" else None,
        "note": insight.get("note") if state == "RAW" else None,
        "guessed": [fake.quote_words(q) for q in every if not said(q)],
    }


def predicted_themes(standings: dict, insight: dict) -> list[dict]:
    """The fake's grouping (`interviewer_fake.themes`, keel-cloud 119's `FakeThemes`: up to three, then ON_THEIR_OWN)
    of the dimension's quotes, in answer order -- served as the standings serve themes: each its count and every quote,
    shortest first."""
    quotes = insight.get("quotes") or []
    by_id = {q.get("invitationId"): {"name": q.get("name"), "text": q.get("text")} for q in quotes}
    if len(quotes) == 1:
        # keel-cloud 119 judgement call 4: one answer is its own group, with no call -- GROUPED, ON_THEIR_OWN
        return [{"label": fake.ON_THEIR_OWN, "count": 1, "quotes": fake.served_quotes(list(by_id), by_id)}]
    grouped = fake.themes([{"id": q.get("invitationId"), "text": q.get("text")} for q in quotes],
                          insight.get("name") or "")
    return [{"label": t["label"], "count": len(t["answerIds"]), "quotes": fake.served_quotes(t["answerIds"], by_id)}
            for t in grouped["themes"]]


def insight_faults(standings: dict, page: dict, *, strict: bool, names: dict) -> list:
    """Spec 064 FR-8 / 8a / 8b (keel-cloud 119, keel-web 095): one box per dimension with words, any status, worst
    first and the held lines' dissent boxes after the rest; every quote a named person's own follow-up, the themes
    covering each once (at most three, then *On their own*), `answered` the quotes'; the failing lines with no words
    as `notAsked` lines; GROUPED on the scripted stack, its themes the fake's grouping."""
    faults = []
    want_dims = worded_dimensions(standings)
    served = {i.get("dimension"): i for i in standings.get("insights") or []}
    if sorted(served) != sorted(want_dims):
        faults.append({"insights[] dimensions": sorted(served), "with words": sorted(want_dims)})
    order = [i.get("dimension") for i in standings.get("insights") or []]
    drawn_order = [k for k in order if not (served.get(k) or {}).get("dissent")] + \
        [k for k in order if (served.get(k) or {}).get("dissent")]
    boxes = page.get("boxes") or []
    if [b.get("key") for b in boxes] != drawn_order:
        faults.append({"boxes": [b.get("key") for b in boxes], "want": drawn_order})
    for key, insight in served.items():
        quotes = insight.get("quotes") or []
        if int(insight.get("answered") or 0) != len(quotes) or not quotes:
            faults.append({key: "answered is not the quotes'", "answered": insight.get("answered"), "quotes": len(quotes)})
        if insight.get("noQuestionWhy") is not None:
            faults.append({key: "noQuestionWhy is served (keel-cloud 119: always null)", "insight": insight})
        heading = insight.get("rungHeading")
        if heading and insight.get("tookBy") is not None and int(insight.get("asked") or 0) + sum(
                int(t.get("count") or 0) for t in insight.get("tookBy") or []) != int(insight.get("against") or 0):
            faults.append({key: "asked + tookBy != against", "insight": insight})
        themes = insight.get("themes") or []
        state = insight.get("state")
        if state not in ("GROUPING", "GROUPED", "RAW"):
            faults.append({key: "state", "served": state})
        if themes and state != "GROUPED":
            faults.append({key: "themes served while not GROUPED", "state": state})
        if state == "GROUPED":
            own = [t for t in themes if t.get("label") == fake.ON_THEIR_OWN]
            named = [t for t in themes if t.get("label") != fake.ON_THEIR_OWN]
            if len(named) > fake.THEMES_MAX or len(own) > 1 or (own and themes[-1] is not own[0]):
                faults.append({key: "at most three themes, then ON_THEIR_OWN last", "themes": themes})
            ids = [q.get("invitationId") for t in themes for q in t.get("quotes") or []]
            if sorted(map(str, ids)) != sorted(str(q.get("invitationId")) for q in quotes):
                faults.append({key: "the themes do not cover every quote once", "themes": ids,
                               "quotes": [q.get("invitationId") for q in quotes]})
            for t in themes:
                if int(t.get("count") or 0) != len(t.get("quotes") or []):
                    faults.append({key: "a theme's count is not its quotes'", "theme": t})
        said = {}
        for a in follow_up_answers(standings, key):
            said.setdefault(a["id"], set()).add(a["text"])
        for q in quotes + [q for t in themes for q in t.get("quotes") or []] + list(insight.get("rawQuotes") or []):
            if q.get("text") not in said.get(q.get("invitationId"), set()) or names.get(q.get("invitationId")) != q.get("name"):
                faults.append({key: "a quote not a named person's own follow-up", "quote": q,
                               "said": sorted(said.get(q.get("invitationId"), set())),
                               "name": names.get(q.get("invitationId"))})
            if q in quotes and q.get("side") not in ("FOR", "AGAINST", "APART"):
                faults.append({key: "a quote's side", "quote": q})
        if strict and state != "GROUPED":
            faults.append({key: "not GROUPED on the scripted stack", "state": state, "note": insight.get("note")})
        if strict and state == "GROUPED":
            want = predicted_themes(standings, insight)
            have = [{"label": t.get("label"), "count": t.get("count"),
                     "quotes": [{k: q.get(k) for k in ("invitationId", "name", "text")} for q in t.get("quotes") or []]}
                    for t in themes]
            if have != want:
                faults.append({key: "themes are not the fake's grouping", "served": have, "fake": want})
        if heading and heading not in (fake.RUNG_HEADINGS.get(key), (fake.ALSO.get(key) or (None,) * 4)[3]):
            faults.append({key: "rung heading", "served": heading, "registry": fake.RUNG_HEADINGS.get(key)})
    by_key = {b.get("key"): b for b in boxes}
    for key in want_dims:
        if key not in served or key not in by_key:
            continue
        standing = next((d for v in standings.get("vectors") or [] for d in v.get("dimensions") or []
                         if d.get("dimension") == key), None)
        card = next((c for c in ((standings.get("facts") or {}).get("cards") or []) if c.get("key") == key), None)
        want, got = expected_box(served[key], standing, guessed_of(standings), card), by_key[key]
        if sorted(ov.norm(q) for q in got.get("guessed") or []) != sorted(ov.norm(q) for q in want["guessed"]):
            faults.append({key: "the GUESSED words apart (keel-web 106 FR-4)", "drawn": got.get("guessed"),
                           "wire": want["guessed"]})
        missing = ov.in_order(got.get("head"), want["head"])
        if got.get("state") != want["state"] or bool(got.get("dissent")) != want["dissent"]:
            faults.append({key: "the box's state", "drawn": [got.get("state"), got.get("dissent")],
                           "wire": [want["state"], want["dissent"]]})
        for part in ("split", "took_by", "frame"):
            if want[part] is not None:
                missing += ov.in_order(got.get("text"), [want[part]])
            elif got.get(part):
                faults.append({key: f"{part} drawn where the wire has none", "drawn": got.get(part)})
        if want["concern"] is not None and ov.norm(got.get("concern")) != ov.norm(want["concern"]):
            faults.append({key: "the rung heading drawn", "drawn": got.get("concern"), "wire": want["concern"]})
        drawn = got.get("themes") or []
        if [(ov.norm(t.get("label")), t.get("count")) for t in drawn] != \
                [(ov.norm(t["label"]), t["count"]) for t in want["themes"]]:
            faults.append({key: "themes", "drawn": drawn, "wire": want["themes"]})
        else:
            for wt, gt in zip(want["themes"], drawn):
                if [ov.norm(q) for q in gt.get("quotes") or []] != [ov.norm(q) for q in wt["quotes"]]:
                    faults.append({key: f"quotes of {wt['label']}", "drawn": gt.get("quotes"), "wire": wt["quotes"]})
        if want["grouping"] is not None:
            missing += ov.in_order(got.get("text"), [fake.GROUPING_LINE] + want["grouping"])
        if want["raw"] is not None:
            missing += ov.in_order(got.get("text"), [fake.IN_THEIR_WORDS] + ([want["note"]] if want["note"] else [])
                                   + want["raw"])
        if missing:
            faults.append({key: got.get("text"), "missing": missing})
    not_asked = standings.get("notAsked") or []
    worded = set(want_dims)
    for n in not_asked:
        if n.get("dimension") in worded:
            faults.append({"notAsked names a line with words": n})
    drawn_na = [(n.get("key"), ov.norm(n.get("text"))) for n in page.get("not_asked") or []]
    want_na = [(n.get("dimension"), ov.norm(fake.not_asked_line(n))) for n in not_asked]
    if drawn_na != want_na:
        faults.append({"notAsked lines": drawn_na, "wire": want_na})
    if not want_dims:
        n = int(((standings.get("facts") or {}).get("pilot") or {}).get("finished") or 0)
        if not_asked:
            want_empty = [fake.NOTHING_TO_READ_YET, fake.NO_WORDS_LINE]
        elif thin(standings):
            want_empty = [fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(n)]
        else:
            want_empty = [fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE]
        missing = ov.in_order(page.get("empty"), want_empty)
        if missing or boxes:
            faults.append({"empty state": page.get("empty"), "want": want_empty, "boxes": len(boxes)})
    elif page.get("empty"):
        faults.append({"empty state drawn beside boxes": page.get("empty")})
    return faults


def report_insights(r: dict) -> tuple[bool, Any]:
    """One box a dimension with words, worst first (spec 064 FR-8: keel-cloud 119, keel-web 095), its served words;
    the themes the fake's on the stack; the failing lines with none as one muted line each; else the right empty
    state."""
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
    # spec 070 FR-3: each box's pill is the card's own line drawn again (keel-web `lineWordOf`) -- the view's own words
    own = list(page.get("own_lines") or []) + [w for w in pill_words(r["standings"]) if w]
    found = repeats(page.get("text"), page.get("quotes"), own, numbers)
    return not found, {"repeated": found}


# ------------------------------------------------------------------------------------------- the Pilot

def window_words(standings: dict) -> str | None:
    card = next((c for c in (standings.get("facts") or {}).get("cards") or []
                 if c.get("key") == "problem.prevalence"), None) or {}
    line = str(card.get("line") or "")
    # spec 064 FR-4a (keel-cloud 116): "<the founder's clause> in the last <window>", or "had it in <window>"
    if line.startswith("had it in "):
        return line[len("had it in "):]
    head, sep, tail = line.rpartition(" in the last ")
    return f"the last {tail}" if sep else None


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
    if people and ov.in_order(page.get("foot") or page.get("text"), [KEEL_NEVER_EMAILS]):
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
    want_leads = {v: p["lead"] for v, p in expected_overview(standings)["panels"].items()}
    for page in pages:
        n = page.get("page")
        own = tokens(page.get("text")) - tokens(frame_text(page))
        if n == 1:
            # keel-web 113 FR-4 (spec 073 FR-3): page one keeps every panel's lead lines, the wire's drawing, and they
            # are the sheet's own words (113 J-13: D10 counts them as it counts the frame)
            leads = page.get("leads") or {}
            for vector in ov.VECTORS:
                missing = ov.in_order(leads.get(vector), want_leads[vector])
                if missing:
                    faults.append({f"page 1 lead:{vector}": leads.get(vector), "missing": missing})
            own -= tokens(" ".join(str(x or "") for x in leads.values()))
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
