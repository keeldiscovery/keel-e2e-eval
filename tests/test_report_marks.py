"""Spec 052: the report marks (`evals/report_marks.py`), the Overview drawing (`instructions/overview.py`), the themes
fake (`harness/interviewer_fake.themes`) and the healthy project (`evals/preludes.healthy_entry`) -- stackless.

Every mark is shown green on a record whose page draws exactly what the wire says, and red on a seeded fault of its
own (call 13's other half: a mark that only ever showed green is indistinguishable from one that is always green).
The themes fake is held to keel-cloud 104's own cases (`executor-fixtures/THEMES/cases.json`, exported whole as
`themes-cases.json`), the rung headings and the no-question reasons to the registry export, and the healthy project's
answers to the ladder's `against` codes.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from evals import preludes
from evals import report_marks as rm
from harness import interviewer_fake as fake
from instructions import brief_facts as bf
from instructions import overview as ov
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
KEEL_WEB = Path(load_config(validate=False).keel_web)
THEMES_CASES = KEEL_CLOUD / "src" / "test" / "resources" / "keel" / "executor-fixtures" / "THEMES" / "cases.json"
REGISTRY_JSON = KEEL_CLOUD / "src" / "main" / "resources" / "keel" / "dimension-registry.json"

PROJECT = "Keyfinder"
DATE = "2026-10-17"
#: The commitment rung's follow-up answers on the decision-makers' link (invitation id, name, words).
FOLLOW_UPS = [("inv-nia", "Nia Noor", "A pilot with one office first."),
              ("inv-oz", "Oz Oduya", "A pilot on two desks."),
              ("inv-pip", "Pip Penn", "Paper tags for a month, then the app.")]


# --------------------------------------------------------------------------------------- the wire

def _n(card: dict) -> int:
    number = str(card.get("number") or "")
    return int(number.split(" of ")[1]) if " of " in number else 4


#: A held line's one follow-up (spec 064 FR-8a, keel-cloud 119: a dissent box; one answer is its own group).
DISSENT = ("inv-ann", "Ann Abbott", "Another app to open is too much on a busy morning.")


def _quote(i: str, n: str, t: str, *, option: str, side: str, heading: str) -> dict:
    return {"invitationId": i, "name": n, "text": t, "option": option, "side": side, "heading": heading}


def standings() -> dict:
    """A contract-28 `StandingsView` over the B2B fixture (spec 064 FR-8a, keel-cloud 119): Commitment split with three
    follow-ups (GROUPED by the fake), Adoption friction held with one (a dissent box, its own group), Purchase friction
    split with no words (a `notAsked` line); two pilot people, one a dataset's with an email."""
    facts = bf.facts_for(fx.entry(fx.ENTRY_B2B), fx.registry())
    cards = facts["cards"]
    names = {c["key"]: c["name"] for c in cards}
    vectors = []
    for vector in ov.VECTORS:
        dims = []
        for card in cards:
            if ov.stage_of(card["key"]) != vector:
                continue
            row = {"dimension": card["key"], "name": card["name"], "status": card["status"], "n": _n(card),
                   "people": []}
            if card["key"] == "commercial.commitment":
                row["people"] = [{"invitationId": i, "personName": n, "readAs": "said no", "followUp": t}
                                 for i, n, t in FOLLOW_UPS] + [{"invitationId": "inv-max", "personName": "Max Moss",
                                                                "readAs": "said yes"}]
            if card["key"] == "solution.adoption_friction":
                row["people"] = [{"invitationId": DISSENT[0], "personName": DISSENT[1], "readAs": "said no",
                                  "followUp": DISSENT[2]}]
            dims.append(row)
        verdict = next(v["verdict"] for v in facts["vectors"] if v["vector"] == vector)
        vectors.append({"vector": vector, "verdict": verdict, "dimensions": dims})
    heading = fake.RUNG_HEADINGS["commercial.commitment"]
    quotes = [_quote(i, n, t, option="No", side="AGAINST", heading=heading) for i, n, t in FOLLOW_UPS]
    by_id = {q["invitationId"]: q for q in quotes}
    grouped = fake.themes([{"id": q["invitationId"], "text": q["text"]} for q in quotes], "Commitment")["themes"]
    dissent = _quote(*DISSENT, option="No", side="AGAINST", heading=fake.RUNG_HEADINGS["solution.adoption_friction"])
    insights = [
        {"dimension": "commercial.commitment", "name": "Commitment", "status": "PEOPLE_DISAGREE",
         "rungHeading": heading, "noQuestionWhy": None, "against": 3, "asked": 3, "answered": 3, "skipped": 0,
         "tookBy": [], "state": "GROUPED", "note": None, "dissent": False, "frame": None, "quotes": quotes,
         "themes": [{"label": t["label"], "count": len(t["answerIds"]),
                     "quotes": sorted((by_id[i] for i in t["answerIds"]), key=lambda q: len(q["text"])),
                     "quoteIds": list(t["answerIds"])} for t in grouped],
         "raw": False, "rawQuotes": []},
        {"dimension": "solution.adoption_friction", "name": names["solution.adoption_friction"],
         "status": "HOLDING_UP", "rungHeading": fake.RUNG_HEADINGS["solution.adoption_friction"],
         "noQuestionWhy": None, "against": 1, "asked": 1, "answered": 1, "skipped": 0, "tookBy": [],
         "state": "GROUPED", "note": None, "dissent": True,
         "frame": "Adoption friction held, 7 of 8; the 1 who said no:", "quotes": [dissent],
         "themes": [{"label": fake.ON_THEIR_OWN, "count": 1, "quotes": [dissent], "quoteIds": [DISSENT[0]]}],
         "raw": False, "rawQuotes": []},
    ]
    not_asked = [{"dimension": "commercial.purchase_friction", "name": names["commercial.purchase_friction"],
                  "why": "nobody's follow-up landed here"}]
    people = [
        {"invitationId": "inv-ann", "name": "Ann Abbott", "link": "PRIMARY", "words": "people who have it",
         "source": "KNOWN", "datasetName": None, "email": None, "gate": True, "story": "I could not find my keys.",
         "answers": [{"dimension": "problem.frequency", "name": "Frequency", "words": "3 nights out of 7"}],
         "followUp": None},
        {"invitationId": "inv-max", "name": "Max Moss", "link": "COMMERCIAL_B2B", "words": "decision-makers",
         "source": "DATASET", "datasetName": "Office managers, London", "email": "max@moss.example", "gate": None,
         "story": None, "answers": [{"dimension": "commercial.price", "name": "Price", "words": "£2 to £5 a month"}],
         "followUp": {"dimension": "commercial.commitment", "text": "Install it on my phone first."}},
    ]
    return {"asOf": "2026-10-17T00:00:00Z", "revision": 9, "version": 25, "name": PROJECT, "people": {},
            "pilot": facts["pilot"], "priceMedian": facts["commercial"]["priceMedian"], "pilotPeople": people,
            "vectors": vectors, "facts": facts, "insights": insights, "notAsked": not_asked, "outsideSegment": 0}


# ---------------------------------------------------------------------- what a faithful page draws

def _join(*parts) -> str:
    return " ".join(str(p) for p in parts if p)


def board(st: dict) -> dict:
    want = rm.expected_overview(st)
    hero = want["hero"]
    panels = {}
    for vector in ov.VECTORS:
        w = want["panels"][vector]
        # keel-web 113 FR-4 (spec 073 FR-3): the full Overview draws no panel lead
        panels[vector] = {"present": True, "head": _join(w["name"], w["pill"]), "lead": "", "leads": 0,
                          "rows": [{"key": r["key"], "href": f"/p/x{r['href']}", "text": _join(*r["parts"])}
                                   for r in w["rows"]]}
    tiles = {k: {"present": True, "text": _join(*v)} for k, v in want["tiles"].items()}
    text = _join(want["eyebrow"], hero["kicker"], hero["verdict"], *hero["why"], *hero["caption"],
                 *(t["text"] for t in tiles.values()),
                 *(_join(p["head"], *(r["text"] for r in p["rows"])) for p in panels.values()),
                 *want["foot"])
    return {"views": ["Overview", "Insights", "Pilot"], "eyebrow": want["eyebrow"],
            "hero": {"label": hero["label"], "class": f"rp-verdict l-{hero['label']}", "verdict": hero["verdict"],
                     "text": _join(hero["kicker"], hero["verdict"], *hero["why"]),
                     "send_more": {"text": ov.SEND_TO_MORE, "href": "/p/x/interviews/sent"}
                     if hero["send_more"] else None,
                     "caption": _join(*hero["caption"])},
            "bands": [{"stage": v, "class": "band"} for v in ov.VECTORS], "tiles": tiles, "panels": panels,
            "foot": _join(*want["foot"]), "old_deck": {"p.overall": 0, ".snaprow": 0, ".panel__count": 0},
            "download": {"present": True, "enabled": True, "href": "/p/x/print", "target": "_blank"}, "text": text}


def insights_page(st: dict) -> dict:
    """What keel-web 095 draws from the standings: the boxes (dissent last), each by its state; the notAsked lines."""
    served = st.get("insights") or []
    order = [i for i in served if not i.get("dissent")] + [i for i in served if i.get("dissent")]
    boxes, quotes, own = [], [], []
    for insight in order:
        w = rm.expected_box(insight)
        themes = [{"label": t["label"], "count": t["count"], "quotes": list(t["quotes"])} for t in w["themes"]]
        theme_text = [_join(f"{t['label']} ({t['count']})", *t["quotes"]) for t in themes]
        loose = w["grouping"] or w["raw"] or []
        lead = [fake.GROUPING_LINE] if w["grouping"] else ([fake.IN_THEIR_WORDS] + ([w["note"]] if w["note"] else [])
                                                           if w["raw"] else [])
        text = _join(*w["head"], w["split"], w["concern"], w["frame"], *theme_text, w["took_by"], *lead, *loose)
        quotes += [q for t in themes for q in t["quotes"]] + list(loose)
        own += [x for x in (w["concern"], w["frame"], w["took_by"]) if x]
        boxes.append({"key": w["key"], "state": w["state"], "dissent": w["dissent"], "head": _join(*w["head"]),
                      "concern": w["concern"] or "", "frame": w["frame"], "themes": themes, "text": text,
                      "split": w["split"], "took_by": w["took_by"], "grouping": w["grouping"], "raw": w["raw"] or [],
                      "raw_note": w["note"]})
    not_asked = [{"key": n["dimension"], "text": fake.not_asked_line(n)} for n in st.get("notAsked") or []]
    empty = None
    if not boxes:
        n = st["facts"]["pilot"]["finished"]
        if not_asked:
            empty = _join(fake.NOTHING_TO_READ_YET, fake.NO_WORDS_LINE)
        else:
            empty = _join(fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(n)) if rm.thin(st) else \
                _join(fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE)
    return {"boxes": boxes, "empty": empty, "not_asked": not_asked, "quotes": quotes, "own_lines": own,
            "text": _join(*(b["text"] for b in boxes), *(n["text"] for n in not_asked), empty)}


def pilot_page(st: dict) -> dict:
    rows = []
    for person in st["pilotPeople"]:
        w = rm.expected_person(st, person)
        rows.append({"invitation": w["invitation"], "summary": _join(*w["summary"], w["email"]),
                     "email": w["email"], "inside": _join(*w["inside"])})
    tile = _join(*ov.tiles(st["facts"], st["priceMedian"])["pilot"])
    agreed = _join(rm.WHAT_THEY_AGREED, rm.WHAT_THEY_AGREED_LINE)
    none = rm.NOBODY_SIGNED_UP if not rows else None
    text = _join(tile, agreed, *(_join(r["summary"], r["inside"]) for r in rows), none, rm.KEEL_NEVER_EMAILS)
    return {"tiles": {"pilot": {"text": tile}, "agreed": {"text": agreed}}, "people": rows, "none": none,
            "foot": rm.KEEL_NEVER_EMAILS, "text": text}


def stage_pages(st: dict) -> dict:
    return {v["vector"]: _join(*(_join(d["name"], ov.head(next(c["statusWords"] for c in st["facts"]["cards"]
                                                               if c["key"] == d["dimension"])))
                                 for d in v["dimensions"]),
                               *(ov.card_words(c) for c in st["facts"]["cards"] if ov.stage_of(c["key"]) == v["vector"]))
            for v in st["vectors"]}


def binding(st: dict, views: dict) -> dict:
    def frame(n, kicker, title):
        return {"page": n, "kicker": kicker, "title": title, "meta": "office managers · GB · 17 answered",
                "foot": f"Keel brief · {PROJECT} · page {n}", "rows": 0}
    want = rm.expected_overview(st)
    leads = [line for v in ov.VECTORS for line in want["panels"][v]["lead"]]
    one = frame(1, "Keel brief · the overview", PROJECT)
    one["text"] = _join(rm.frame_text(one), want["hero"]["verdict"], *want["hero"]["why"],
                        *(_join(*t) for t in want["tiles"].values()), *leads)
    one["leads"] = {v: _join(*want["panels"][v]["lead"]) for v in ov.VECTORS}      # spec 073 FR-3: page one keeps them
    two = frame(2, "Keel brief · the insights", rm.INSIGHTS_PAGE_TITLE)
    two["text"] = _join(rm.frame_text(two), views["insights"]["text"])
    three = frame(3, "Keel brief · the pilot", "4 of 17 signed up")
    three["text"] = _join(rm.frame_text(three), views["pilot"]["text"])
    four = frame(4, "Keel brief · the breakdown", rm.BREAKDOWN_PAGE_TITLE)
    four["text"] = _join(rm.frame_text(four), "Dimension Card Answers Status",
                         *(_join(c["name"], ov.card_words(c), ov.head(c["statusWords"])) for c in st["facts"]["cards"]))
    return {"title": f"{PROJECT} — Keel brief — {DATE}", "preparing_seen": True,
            "pages": [one, two, three, four], "old_headline": 0, "text": ""}


def record(st: dict | None = None) -> dict:
    st = st or standings()
    views = {"overview": board(st), "insights": insights_page(st), "pilot": pilot_page(st)}
    return {"standings": st, "strict": True, "project": PROJECT, "date": DATE,
            "opted_in": [p["invitationId"] for p in st["pilotPeople"]],
            "invitations": {"inv-ann": {"name": "Ann Abbott", "email": None},
                            "inv-max": {"name": "Max Moss", "email": "max@moss.example"},
                            **{i: {"name": n, "email": None} for i, n, _t in FOLLOW_UPS}},
            "stage_pages": stage_pages(st), **views, "binding": binding(st, views)}


def _card(r):
    return {c.mark: c for c in rm.score(r)}


# ------------------------------------------------------------------------------- green, all five

def test_a_faithful_report_meets_all_five_marks():
    card = rm.scorecard(record())
    assert card["measured"] == card["met"] == 5, json.dumps(card["checks"], indent=2, default=str)
    assert card["unmeasured"] == [] and rm.owed(record()) == list(rm.MARK_NAMES)


def test_a_record_without_a_subject_leaves_its_marks_unmeasured_never_met():
    r = record()
    del r["insights"]
    checks = _card(r)
    assert not checks["report_insights"].measured and not checks["report_insights"].ok
    assert not checks["report_no_repeat"].measured and not checks["report_binding"].measured
    assert checks["report_overview"].ok and checks["report_pilot"].ok
    assert rm.owed(r) == ["report_overview", "report_pilot"]


# ----------------------------------------------------------------------------- report_overview

@pytest.mark.parametrize("fault, why", [
    (lambda r: r["overview"]["panels"]["COMMERCIAL"]["rows"][1].update(text="Price Holding up 5 of 5 at your band "
                                                                            "or more"), "a row's number not the card's"),
    (lambda r: r["overview"]["panels"]["PROBLEM"]["rows"].reverse(), "the rows out of the registry's order"),
    (lambda r: r["overview"]["hero"].update(label="BUILD", verdict="Build"), "the verdict not the decision's"),
    (lambda r: r["overview"]["hero"].update(text="Should you build it? Build, but change it Low."), "the why line cut"),
    (lambda r: r["overview"]["tiles"]["price"].update(text="What they would pay Not asked yet"), "the price tile"),
    (lambda r: r["overview"]["tiles"]["pilot"].update(text="Pilot None yet"), "the pilot tile"),
    (lambda r: r["overview"]["old_deck"].update({".snaprow": 1}), "the old deck's snaps drawn"),
    (lambda r: r["overview"].update(text=r["overview"]["text"] + " Every band opens its stage page"), "the old foot"),
    (lambda r: r["overview"]["download"].update(enabled=False), "the download disabled"),
    (lambda r: r["overview"]["panels"]["SOLUTION"]["rows"][0].update(href="/p/x/brief/breakdown#solution.c"),
     "a row linking to the old breakdown"),
    (lambda r: r["standings"].update(priceMedian={"edgeSaid": "£5 a month", "chose": 1, "n": 5}),
     "StandingsView.priceMedian not the facts'"),
])
def test_report_overview_fails_on_each_seeded_fault(fault, why):
    r = record()
    fault(r)
    check = _card(r)["report_overview"]
    assert check.measured and not check.ok, why
    assert check.detail["faults"], why


def test_the_overview_of_too_few_is_keep_interviewing_not_asked_and_nobody_yet():
    """FR-7's too-few state, drawn from a wire nobody has answered: *Keep interviewing* with the people line and the
    link to Interviews, the price tile *Not asked yet*, every row *nobody has answered this yet*."""
    entry = fx.entry(fx.ENTRY_B2B)
    empty = copy.deepcopy(entry.expected)
    for standing in empty["standings"].values():
        standing.clear()
        standing.update(status="NOT_ASKED_YET", n=0)
    for verdict in empty["vector_verdicts"].values():
        verdict["verdict"] = "NOT_ASKED_YET"
    import dataclasses                                                     # noqa: PLC0415
    blank = dataclasses.replace(entry, expected=empty, answers=[])
    facts = bf.facts_for(blank, fx.registry())
    drawn = ov.overview(facts)
    assert drawn["hero"]["verdict"] == "Keep interviewing" and drawn["hero"]["send_more"]
    assert drawn["hero"]["why"] == ["0 people have answered.", ov.CARD_NEEDS, ov.SEND_TO_MORE]
    assert drawn["tiles"]["price"] == [ov.PRICE_TILE_LABEL, ov.PRICE_NOT_ASKED, ov.PRICE_NOT_ASKED_LINE]
    assert drawn["tiles"]["pilot"] == [ov.PILOT_TILE_LABEL, ov.PILOT_NONE_YET, ov.PILOT_FILLS]
    assert all(r["parts"][2] == ov.NOBODY_YET for v in ov.VECTORS for r in drawn["panels"][v]["rows"])
    st = {"facts": facts, "vectors": [], "insights": [], "priceMedian": None}
    assert rm.thin(st) and rm.failing_dimensions(st) == [], \
        "keel-web 079: nobody answered is *Nothing to read into yet*; spec 052 call 4, DRIFT #93 closed"
    too_few = {"boxes": [], "empty": _join(fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(0))}
    assert rm.insight_faults(st, too_few, strict=True, names={}) == []
    as_read = {"boxes": [], "empty": fake.NOTHING_TO_READ_YET + fake.nothing_to_read_line(0)}   # h2 + line, no space
    assert rm.insight_faults(st, as_read, strict=True, names={}) == [], "the page's own join (staging 2026-10-17)"
    green = {"boxes": [], "empty": _join(fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE)}
    assert rm.insight_faults(st, green, strict=True, names={}), \
        "*Nothing is failing* at zero answers is the fault (DRIFT #93, keel-web 079)"


def test_the_lead_lines_follow_the_stage_status():
    st = standings()
    drawn = rm.expected_overview(st)["panels"]
    assert drawn["PROBLEM"]["lead"] == ["4 of 4 holding."]
    assert drawn["COMMERCIAL"]["lead"] == [
        "Purchase friction · 2 of 5 needed the office manager's sign-off, and it took a long time",
        "Commitment · 2 of 5 would install the app · 1 more after a look at it on a demo first"]  # the fixture's smaller step (r14)
    facts = copy.deepcopy(st["facts"])
    facts["vectors"][2]["verdict"] = "TOO_FEW_TO_CALL"
    for c in facts["cards"]:
        if c["key"] == "commercial.ability_to_pay":
            c["status"] = "TOO_FEW_TO_CALL"
    assert ov.panels(facts, {"commercial.existing_sacrifice": 4, "commercial.ability_to_pay": 4})["COMMERCIAL"][
        "lead"] == ["Too few to call: 4 answered, 5 are needed."]
    facts["vectors"][2]["verdict"] = "NOT_ASKED_YET"
    assert ov.panels(facts)["COMMERCIAL"]["lead"] == [ov.NOT_ASKED_LEAD]


def test_in_order_reads_words_in_order_and_ignores_the_markup_between():
    assert ov.in_order("Should you build it? Low. Smallest group", ["build it", "Low.", "smallest"]) == []
    assert ov.in_order("b a", ["a", "b"]) == ["b"], "order matters"
    assert ov.in_order("it’s", ["it's"]) == [], "the typographic apostrophe reads as the plain one"


# ------------------------------------------------------------------------- the DRY compare (call 117)

def test_report_overview_dry_agrees_with_its_own_reading_seven_checks():
    entry = fx.entry()
    registry = fx.registry()
    score = ov.compare(entry, registry, bf.facts_for(entry, registry))
    assert (score.agreed, score.checks) == (7, 7) and score.correctness == 1.0


@pytest.mark.parametrize("fault, part", [
    (lambda f: f["cards"][0].update(number="9 of 12"), "panel:PROBLEM"),
    (lambda f: f["decision"].update(howSure="LOW"), "hero"),
    (lambda f: f["commercial"].update(priceMedian=None), "tile:price"),
    (lambda f: f["pilot"].update(optedIn=0), "tile:pilot"),
    (lambda f: f["vectors"][1].update(verdict="NOT_HOLDING_UP"), "panel:SOLUTION"),
])
def test_report_overview_dry_names_the_part_a_seeded_fault_moves(fault, part):
    entry = fx.entry()
    registry = fx.registry()
    cloud = bf.facts_for(entry, registry)
    fault(cloud)
    score = ov.compare(entry, registry, cloud)
    assert part in [m["key"] for m in score.mismatches] and score.agreed < score.checks


def test_no_cloud_facts_leave_report_overview_unmeasured():
    score = ov.compare(fx.entry(), fx.registry(), None)
    assert score.measured is False and score.correctness is None


def test_keel_clouds_facts_draw_the_corpus_overview_on_all_seven_entries():
    """The DRY measure on the canon (49 of 49 at keel-cloud-docs 9a033fe): skipped while keel-cloud's
    build/brief-facts/ is absent or predates 104 (`tests/test_instruction_brief_facts.cloud_facts_at_104`)."""
    from tests.test_instruction_brief_facts import cloud_facts_at_104       # noqa: PLC0415
    registry, corpus, cloud = cloud_facts_at_104()
    scores = [ov.compare(e, registry, cloud.facts.get(e.id)) for e in corpus.entries]
    assert sum(s.checks for s in scores) == 49
    assert sum(s.agreed for s in scores) == 49, [m for s in scores for m in s.mismatches]


# ----------------------------------------------------------------------------- report_insights

@pytest.mark.parametrize("fault, why", [
    (lambda r: r["insights"]["boxes"].reverse(), "the dissent box before the failing one"),
    (lambda r: r["insights"]["boxes"].pop(), "a dimension with words and no box"),
    (lambda r: r["insights"]["boxes"][0]["themes"][0].update(count=3), "a theme's count not the wire's"),
    (lambda r: r["insights"]["boxes"][0]["themes"][0]["quotes"].reverse(), "the quotes out of order"),
    (lambda r: r["insights"]["boxes"][0].update(concern="What they would start with"),
     "the rung's heading not the served stem"),
    (lambda r: r["insights"].update(not_asked=[]), "the notAsked line not drawn"),
    (lambda r: r["insights"]["boxes"][0].update(took_by="Only 1 of the 2 were asked here: ..."),
     "a took-by line the wire has none of"),
    (lambda r: r["insights"]["boxes"][1].update(text="Adoption friction Holding up"), "the dissent frame not drawn"),
    (lambda r: r["standings"]["insights"][0]["themes"][0].update(label="office"), "the served themes not the fake's"),
    (lambda r: r["standings"]["insights"][0]["quotes"][0].update(name="Somebody Else"),
     "a quote under a name the invitation does not carry"),
    (lambda r: r["standings"]["insights"][0]["quotes"][0].update(text="Words nobody said."),
     "a quote nobody wrote"),
    (lambda r: r["standings"]["insights"][0].update(asked=2), "asked + took by != against"),
    (lambda r: r["standings"]["insights"].pop(0), "insights[] missing a dimension with words"),
    (lambda r: r["standings"]["insights"][0].update(state="GROUPING"), "not grouped on the scripted stack"),
    (lambda r: r["standings"]["insights"][0].update(answered=2), "answered is not the quotes'"),
    (lambda r: r["standings"]["insights"][0]["themes"].insert(0, {"label": fake.ON_THEIR_OWN, "count": 0,
                                                                  "quotes": []}), "ON_THEIR_OWN not last"),
    (lambda r: r["standings"]["notAsked"].append({"dimension": "commercial.commitment", "name": "Commitment",
                                                  "why": "x"}), "notAsked names a line with words"),
    (lambda r: r["insights"].update(empty="Nothing is failing"), "an empty state beside the boxes"),
])
def test_report_insights_fails_on_each_seeded_fault(fault, why):
    r = record()
    fault(r)
    check = _card(r)["report_insights"]
    assert check.measured and not check.ok, why


def test_the_insights_empty_states_are_the_right_one_of_the_two():
    st = standings()
    for c in st["facts"]["cards"]:
        c["status"], c["statusWords"] = "HOLDING_UP", "Holding up"
    for v in st["vectors"]:
        v["verdict"] = "HOLDING_UP"
        for d in v["dimensions"]:
            d["status"] = "HOLDING_UP"
    st["facts"]["decision"]["label"] = "BUILD"
    st["insights"], st["notAsked"] = [], []
    for v in st["vectors"]:
        for d in v["dimensions"]:
            d["people"] = []
    r = record(st)
    assert "Nothing is failing" in r["insights"]["empty"] and _card(r)["report_insights"].ok
    r["insights"]["empty"] = _join(fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(17))
    assert not _card(r)["report_insights"].ok, "the too-few state on a healthy project"
    st["facts"]["cards"][0]["status"] = "TOO_FEW_TO_CALL"
    r = record(st)
    assert r["insights"]["empty"].startswith(fake.NOTHING_TO_READ_YET) and _card(r)["report_insights"].ok
    r["insights"]["empty"] = _join(fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE)
    assert not _card(r)["report_insights"].ok, "a card too few to call is the too-few state, not Nothing is failing"
    for label, finished in (("KEEP_INTERVIEWING", 17), ("BUILD", 0)):
        st["facts"]["cards"][0]["status"] = "HOLDING_UP"
        st["facts"]["decision"]["label"], st["facts"]["pilot"]["finished"] = label, finished
        r = record(st)
        assert r["insights"]["empty"] == _join(fake.NOTHING_TO_READ_YET, fake.nothing_to_read_line(finished)) and \
            _card(r)["report_insights"].ok, (label, finished)
        r["insights"]["empty"] = _join(fake.NOTHING_FAILING, fake.NOTHING_FAILING_LINE)
        assert not _card(r)["report_insights"].ok, \
            f"keel-web 079: {label} with {finished} answered is the too-few state, not Nothing is failing"


def test_off_the_stack_the_themes_are_held_for_shape_only():
    """FR-9: on a live cell the labels are the model's -- a label the fake would not write is not a fault there."""
    r = record()
    r["standings"]["insights"][0]["themes"][0]["label"] = "rollout"
    r["insights"]["boxes"][0]["themes"][0]["label"] = "rollout"
    assert not _card(r)["report_insights"].ok
    r["strict"] = False
    assert _card(r)["report_insights"].ok


# --------------------------------------------------------------------------- report_no_repeat (D6)

def test_report_no_repeat_holds_on_the_faithful_view_and_inside_a_quote():
    r = record()
    quote = r["standings"]["insights"][0]["themes"][0]["quotes"][0]
    quote["text"] = "We tried 3 of 5 desks for £20."
    for q in r["standings"]["insights"][0]["quotes"]:
        if q["invitationId"] == quote["invitationId"]:
            q["text"] = quote["text"]
    row = r["standings"]["vectors"][2]["dimensions"][-1]["people"]
    next(p for p in row if p["invitationId"] == quote["invitationId"])["followUp"] = "We tried 3 of 5 desks for £20."
    r["insights"] = insights_page(r["standings"])
    assert "3 of 5" in r["insights"]["text"]
    assert _card(r)["report_no_repeat"].ok, "a quote is the person's own words"


@pytest.mark.parametrize("repeat", ["3 of 5 did not agree.", "£35 a month", "2.5 nights out of 7",
                                    "6 months out of 12", "6 of 8 put it in their top two"])
def test_report_no_repeat_fails_on_a_seeded_repeat(repeat):
    r = record()
    r["insights"]["text"] += " " + repeat
    check = _card(r)["report_no_repeat"]
    assert check.measured and not check.ok and check.detail["repeated"], repeat


def test_the_views_own_said_why_line_is_not_a_repeat():
    assert rm.repeats("What they would start with · 3 of the 3 said why Only 1 of the 3 were asked here: 2 had already "
                      "been asked about Price, the first rung they failed.",
                      [], ["What they would start with · 3 of the 3 said why",
                           "Only 1 of the 3 were asked here: 2 had already been asked about Price, the first rung "
                           "they failed."], ["3 of 5"]) == []


# ------------------------------------------------------------------------------------- report_pilot

@pytest.mark.parametrize("fault, why", [
    (lambda r: r["pilot"]["people"].pop(), "a served person not drawn"),
    (lambda r: r["pilot"]["people"][1].update(email=None), "the dataset's email not drawn"),
    (lambda r: r["pilot"]["people"][0].update(email="ann@abbott.example"), "an email the wire does not serve"),
    (lambda r: r["standings"]["pilotPeople"][0].update(email="ann@abbott.example"),
     "an email on a link that carried none"),
    (lambda r: r["pilot"]["people"][1].update(inside="Decision-makers answer the money part only."),
     "the answers and the follow-up not drawn"),
    (lambda r: r["pilot"].update(foot="", text=r["pilot"]["text"].replace(rm.KEEL_NEVER_EMAILS, "")),
     "no Keel never emails line"),
    (lambda r: r.update(opted_in=["inv-ann"]), "a served person nobody opted in"),
    (lambda r: r["pilot"]["tiles"]["agreed"].update(text="What they agreed to"), "the agreed tile's sentence"),
])
def test_report_pilot_fails_on_each_seeded_fault(fault, why):
    r = record()
    fault(r)
    check = _card(r)["report_pilot"]
    assert check.measured and not check.ok, why


def test_nobody_signed_up_is_its_own_line():
    st = standings()
    st["pilotPeople"] = []
    r = record(st)
    assert _card(r)["report_pilot"].ok
    r["pilot"]["none"] = None
    assert not _card(r)["report_pilot"].ok


# ---------------------------------------------------------------------------------- report_binding

@pytest.mark.parametrize("fault, why", [
    (lambda r: r["binding"]["pages"][1].update(text=r["binding"]["pages"][1]["text"] + " Recommendation"),
     "a word on page 2 the Insights view does not show"),
    (lambda r: r["binding"]["pages"][0].update(rows=13), "page 1 drew the rows"),
    (lambda r: r["binding"]["pages"][2].update(text=r["binding"]["pages"][2]["text"] + " 99"),
     "a number on page 3 the Pilot view does not show"),
    (lambda r: r["binding"]["pages"][3].update(text=r["binding"]["pages"][3]["text"] + " 4,321"),
     "a breakdown number the standings do not carry"),
    (lambda r: r["binding"]["pages"][3].update(text=r["binding"]["pages"][3]["text"] + " What to do next"),
     "the old brief's next tests"),
    (lambda r: r["binding"].update(old_headline=1), "the old brief's headline"),
    (lambda r: r["binding"]["pages"].pop(), "no breakdown"),
    (lambda r: r["binding"].update(title="Keel brief"), "the title is not the file name"),
    (lambda r: r["binding"].update(preparing_seen=False), "no Preparing your brief"),
    (lambda r: r["binding"]["pages"][0].update(leads={}), "page 1 drew no lead line (keel-web 113 FR-4)"),
    (lambda r: r["binding"]["pages"][0]["leads"].update(PROBLEM="1 of 4 holding."), "page 1's lead not the wire's"),
])
def test_report_binding_fails_on_each_seeded_fault(fault, why):
    r = record()
    fault(r)
    check = _card(r)["report_binding"]
    assert check.measured and not check.ok, why


def test_v2_the_full_overview_draws_no_lead_and_page_one_keeps_it():
    """Spec 073 FR-3 (keel-web 113 FR-4): a lead line on the full Overview is report_overview's fault; on page one the
    lead lines are the sheet's own words (113 J-13), so none of them is a word no view shows."""
    assert rm.REPORT_MARKS_VERSION == 2
    r = record()
    assert _card(r)["report_overview"].ok and _card(r)["report_binding"].ok
    one = r["binding"]["pages"][0]
    lead = one["leads"]["PROBLEM"]
    assert lead
    # a word only page one's lead carries is the sheet's own; the same word anywhere else on page one is not
    own = copy.deepcopy(r)
    own["binding"]["pages"][0].update(text=one["text"] + " Holdouts")
    own["binding"]["pages"][0]["leads"]["PROBLEM"] = lead + " Holdouts"
    assert _card(own)["report_binding"].ok, _card(own)["report_binding"].detail
    stray = copy.deepcopy(r)
    stray["binding"]["pages"][0].update(text=one["text"] + " Holdouts")
    assert not _card(stray)["report_binding"].ok
    r["overview"]["panels"]["PROBLEM"].update(lead=lead, leads=1)
    check = _card(r)["report_overview"]
    assert not check.ok and any("panel:PROBLEM" in f for f in check.detail["faults"]), check.detail


def test_a_healthy_projects_sheet_carries_no_in_their_words():
    st = standings()
    st["insights"], st["notAsked"] = [], []
    for v in st["vectors"]:
        for d in v["dimensions"]:
            d["status"], d["people"] = "HOLDING_UP", []
    r = record(st)
    assert _card(r)["report_binding"].ok
    r["binding"]["pages"][1]["text"] += " " + fake.IN_THEIR_WORDS
    r["insights"]["text"] += " " + fake.IN_THEIR_WORDS
    assert not _card(r)["report_binding"].ok, "D9: no In their words on a healthy project"


def test_tokens_are_words_of_four_letters_and_every_number():
    assert rm.tokens("The Problem · 3 of 4 holding, £1,250.50 a month") == {
        "problem", "holding", "month", "3", "4", "1,250.50"}


# ------------------------------------------------------------------------------- the themes fake (FR-2)

def test_the_themes_fake_is_held_to_keel_clouds_cases():
    """keel-cloud 104 FR-9: `FakeThemes`' rule, stop-word list and cases, exported as `themes-cases.json` (a copy of
    `executor-fixtures/THEMES/cases.json`) -- this copy groups them word for word."""
    if not THEMES_CASES.is_file():
        pytest.skip(f"no themes cases at {THEMES_CASES} (keel-cloud before 104)")
    exported = json.loads(THEMES_CASES.read_text(encoding="utf-8"))
    assert exported["fake"]["max"] == fake.THEMES_MAX
    assert sorted(exported["fake"]["stopWords"]) == sorted(fake.THEMES_STOP_WORDS)
    assert "first noun" in exported["fake"]["rule"] and "ties by first appearance" in exported["fake"]["rule"]
    assert {c["case_id"].split("/")[0] for c in exported["cases"]} == {
        "S03-importance", "C3-strong-problem-poor-way-incompatible"}
    for case in exported["cases"]:
        assert fake.themes(case["answers"], case["name"]) == case["result"], case["case_id"]
        assert case["rungHeading"] == fake.RUNG_HEADINGS[case["dimension"]]
    labels = {c["dimension"]: [t["label"] for t in c["result"]["themes"]] for c in exported["cases"]}
    # keel-cloud 119 (FR-3): every other answer in one last ON_THEIR_OWN group
    assert labels == {"problem.importance": ["work", "rates", "deadlines", fake.ON_THEIR_OWN],
                      "solution.compatibility": ["portal", "owner", "finance", fake.ON_THEIR_OWN]}


def test_the_first_noun_skips_stop_words_short_words_and_the_dimensions_name():
    assert fake.first_noun("It's the portal, always.") == "portal"
    assert fake.first_noun("It is so, too.") is None, "nothing but stop words and short words"
    assert fake.first_noun("An app is too much.") == "app", "three letters is enough"
    assert fake.first_noun("The app's fine") == "app's", "an inner apostrophe stays; it is not counted as a letter"
    assert fake.first_noun("Compatibility is the portal", frozenset({"compatibility"})) == "portal"
    assert fake.first_noun("'Rates' matter") == "rates", "edge apostrophes stripped"
    assert fake.first_noun("2024 rates") == "rates", "a digit is not a letter"


def test_the_fake_piles_by_size_ties_by_first_appearance_three_then_on_their_own():
    answers = [{"id": str(i), "text": t} for i, t in enumerate(
        ["Paper first.", "Pilot one office.", "Pilot two desks.", "Desks are small.", "Budget is tight.",
         "Desks again.", "Phone only.", "Nothing."])]
    assert fake.themes(answers) == {"themes": [{"label": "pilot", "answerIds": ["1", "2"]},
                                               {"label": "desks", "answerIds": ["3", "5"]},
                                               {"label": "paper", "answerIds": ["0"]},
                                               {"label": fake.ON_THEIR_OWN, "answerIds": ["4", "6", "7"]}]}


def test_served_quotes_are_every_quote_shortest_first():
    """keel-cloud 119 FR-2: the quote caps are gone -- every quote, the shortest first."""
    by_id = {str(i): {"name": f"P{i}", "text": "x" * (10 - i)} for i in range(5)}
    assert [q["invitationId"] for q in fake.served_quotes(["0", "1", "2", "3", "4"], by_id)] == ["4", "3", "2", "1",
                                                                                                "0"]


def test_the_rung_headings_and_no_question_reasons_are_the_registrys():
    """Registry decision 23 (keel-cloud 104), moved by 118: `follow_up.heading` on the nine rungs, `no_follow_up` on the
    four."""
    if not REGISTRY_JSON.is_file():
        pytest.skip(f"no registry export at {REGISTRY_JSON}")
    dims = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))["dimensions"]
    headings = {d["key"]: d["follow_up"]["heading"] for d in dims if (d.get("follow_up") or {}).get("heading")}
    reasons = {d["key"]: d["no_follow_up"] for d in dims if d.get("no_follow_up")}
    if not headings:
        pytest.skip("this keel-cloud checkout predates 104's headings")
    assert headings == fake.RUNG_HEADINGS
    assert reasons == fake.NO_FOLLOW_UP_WHY and tuple(reasons) == fake.NO_FOLLOW_UP


def test_the_insights_words_are_keel_web_077s():
    """Held to keel-web 077's source once it is on keel-web's master (the report components); skipped before."""
    source_dir = KEEL_WEB / "src" / "components" / "report"
    if not source_dir.is_dir():
        pytest.skip("keel-web carries no report components yet (077 not on master)")
    text = (KEEL_WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8") + "".join(
        p.read_text(encoding="utf-8") for p in source_dir.glob("*.ts*"))
    for words in (fake.SPLIT_NOTE, fake.IN_THEIR_WORDS, fake.NOTHING_TO_READ_YET, fake.NOTHING_FAILING,
                  fake.NOTHING_FAILING_LINE, ov.SHOULD_YOU_BUILD_IT, ov.EVERY_DIMENSION_HOLDS, ov.CARD_NEEDS,
                  ov.PRICE_TILE_LABEL, ov.PRICE_NOT_ASKED_LINE, ov.NOBODY_YET, ov.EVERY_ROW_OPENS,
                  rm.WHAT_THEY_AGREED, rm.DM_ONLY, rm.KEEL_NEVER_EMAILS, rm.NOBODY_SIGNED_UP,
                  rm.INSIGHTS_PAGE_TITLE, rm.BREAKDOWN_PAGE_TITLE):
        assert words in text.replace("\\u2019", "’"), words


# ------------------------------------------------------------------------------ the healthy project

def _canon(name):
    from instructions import corpus as corpus_mod                          # noqa: PLC0415
    return corpus_mod.load_file(fx.canon_entry(name), registry=fx.registry())


def test_the_healthy_project_is_paidly_with_ten_supporters_a_link():
    entry = _canon("05-paidly.yaml")
    healthy = preludes.healthy_entry(entry)
    people = healthy.people()
    assert [p.link for p in people].count("PRIMARY") == [p.link for p in people].count("COMMERCIAL_B2B") == 10
    assert all(p.anchoring == "ANCHORED" and p.recency == "yes" and p.story for p in people if p.link == "PRIMARY")
    assert {p.person for p in people if p.pilot_opt_in} == {p.person for p in entry.people() if p.pilot_opt_in}
    standings_ = healthy.expected["standings"]
    assert all(s["status"] == "HOLDING_UP" and s["n"] == 10 for s in standings_.values())
    assert {v["verdict"] for v in healthy.expected["vector_verdicts"].values()} == {"HOLDING_UP"}
    assert healthy.statements == entry.statements and healthy.founder_calibration == entry.founder_calibration
    with pytest.raises(ValueError):
        preludes.healthy_entry(_canon("01-countly.yaml"))


def test_the_healthy_answers_are_against_on_no_rung():
    """Nobody is owed a follow-up (051 IM23's none case): no pick is one of the registry's `against` codes; the own
    item is in the top two; the band is the founder's; *Nobody else* is tested and the decision-maker decided alone."""
    entry = _canon("05-paidly.yaml")
    picks = {**preludes.HEALTHY_PICKS["PRIMARY"], **preludes.HEALTHY_PICKS["COMMERCIAL_B2B"]}
    if REGISTRY_JSON.is_file():
        for dim in json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))["dimensions"]:
            against = (dim.get("follow_up") or {}).get("against")
            pick = picks.get(dim["key"])
            if dim["key"] == "commercial.purchase_friction":
                # keel-cloud 118 judgement call 9: every Purchase friction answer is owed a question (quick is against
                # the fear, the long purchase its second stem) -- no green project is owed nothing on that link
                assert pick in against + list((dim["follow_up"].get("also") or {}).get("on") or []), pick
                continue
            if isinstance(against, list) and isinstance(pick, str):
                assert pick not in against, dim["key"]
            if isinstance(pick, dict) and "answer" in pick:
                assert pick["answer"] not in (against or []), dim["key"]
    own = entry.founder_calibration["problem.importance"]["answer"]["items"][0]["code"]
    assert own in picks["problem.importance"]
    price = entry.founder_calibration["commercial.price"]["answer"]
    assert bf._floor_of(picks["commercial.price"]) == 50 <= price["low"] < 100
    assert entry.tested("commercial.buyer_payer_alignment")["code"] == "nobody_else"
    assert picks["commercial.buyer_payer_alignment"] == "decided_alone"
    assert bf.price_median_for(preludes.healthy_entry(entry)) == {"edgeSaid": "$50 a month", "chose": 10, "n": 10}


# ------------------------------------------------------- the THEMES script (keel-runtime 012, D-01 resolved)

def _runtime():
    """keel-runtime's own scripted executor (0.8.0, spec 012), read from the sibling checkout -- or a skip."""
    import importlib                                                       # noqa: PLC0415
    import sys                                                             # noqa: PLC0415
    root = Path(load_config(validate=False).keel_runtime)
    if not (root / "keel_runtime" / "testing" / "scripted_executor.py").is_file():
        pytest.skip(f"no keel-runtime checkout at {root}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    module = importlib.import_module("keel_runtime.testing.scripted_executor")
    if not hasattr(module, "_resolve_themes_result"):
        pytest.skip("this keel-runtime predates spec 012 (0.8.0)")
    return module, importlib.import_module("keel_runtime.executor")


def _failing(*keys):
    import types                                                           # noqa: PLC0415
    return types.SimpleNamespace(expected={"standings": {k: {"status": "NOT_HOLDING_UP"} for k in keys}})


def _job(executor_mod, dimension, name, answers):
    context = {"dimension": dimension, "name": name, "rungHeading": fake.RUNG_HEADINGS.get(dimension),
               "answers": answers}
    return executor_mod.InferenceRequest(job_id="j", interaction_id="i", turn_number=1,
                                         request_payload={"context": context})


def test_the_scripted_themes_resolve_on_the_runtime_to_the_fakes_grouping_of_the_same_texts():
    """C3-like (Compatibility) and S03-like (Importance): the script's entries, written from the answers' texts alone,
    resolved by keel-runtime 012 against the job's context, are exactly `FakeThemes`' result on that context (with
    keel-cloud 119's ON_THEIR_OWN last) -- whichever job arrives first, and the same when asked twice."""
    from harness import vectors_script as vs                               # noqa: PLC0415
    if not THEMES_CASES.is_file():
        pytest.skip(f"no themes cases at {THEMES_CASES}")
    runtime, executor_mod = _runtime()
    cases = json.loads(THEMES_CASES.read_text(encoding="utf-8"))["cases"]
    entry = _failing(*(c["dimension"] for c in cases))
    follow_ups = [(c["dimension"], a["text"]) for c in cases for a in c["answers"]]
    entries = vs.themes_entries(entry, follow_ups)
    assert [e.get("dimension") for e in entries] == [k for k in vs.NAMES if k in {c["dimension"] for c in cases}] \
        + [None], "one entry a dimension the walks post on, in registry order, then the catch-all"
    executor = runtime.ScriptedExecutor({"THEMES": entries})
    for case in reversed(cases + cases):
        got = executor.execute(_job(executor_mod, case["dimension"], case["name"], case["answers"]))
        assert got == {"outcome": "COMPLETED", "result": case["result"]}, case["case_id"]
        assert got["result"] == fake.themes(case["answers"], case["name"]), case["case_id"]


def test_a_dimension_nobody_scripted_gets_the_catch_alls_empty_themes():
    from harness import vectors_script as vs                               # noqa: PLC0415
    runtime, executor_mod = _runtime()
    entries = vs.themes_entries(_failing("commercial.price"), [("commercial.price", "A trial first.")])
    executor = runtime.ScriptedExecutor({"THEMES": entries})
    got = executor.execute(_job(executor_mod, "commercial.commitment", "Commitment",
                                [{"id": "a", "text": "Something nobody scripted."}]))
    assert got == {"outcome": "COMPLETED", "result": {"themes": []}}, "the raw fallback, not a refusal"
    assert vs.themes_entries(_failing(), []) == [{"outcome": "COMPLETED", "result": {"themes": []}}]


def test_a_text_two_people_typed_is_scripted_once():
    from harness import vectors_script as vs                               # noqa: PLC0415
    entries = vs.themes_entries(_failing("commercial.commitment"), [
        ("commercial.commitment", "A free trial on one small job first."),
        ("commercial.commitment", "A short demo with our own numbers in it."),
        ("commercial.commitment", "A free trial on one small job first."),
        ("commercial.price", "Seeing it work with our own clients first would.")])
    assert entries[1] == {"dimension": "commercial.commitment", "outcome": "COMPLETED", "result": {"themes": [
        {"label": "free", "answers": ["A free trial on one small job first."]},
        {"label": "short", "answers": ["A short demo with our own numbers in it."]}]}}
    assert [e.get("dimension") for e in entries] == ["commercial.price", "commercial.commitment", None], (
        "keel-cloud 119 groups held lines too: every dimension the walks post on, in registry order")


@pytest.mark.parametrize("name", ["01-countly.yaml", "05-paidly.yaml", "07-mulchrun.yaml"])
def test_every_rung_scripts_its_one_line_and_any_partial_context_resolves(name):
    """Spec 064 FR-7 (judgement call): one line a rung, so whoever the walk asks there -- the deciding line first,
    read at answer time -- types that line, and a THEMES job over any of the answers so far (keel-cloud 119 starts one
    at every batch's end) resolves on the runtime to the one theme of that line."""
    from harness import vectors_script as vs                               # noqa: PLC0415
    runtime, executor_mod = _runtime()
    entry = _canon(name)
    entries = vs.generate(entry).screens[vs.THEMES_SCREEN]
    assert [e.get("dimension") for e in entries] == list(fake.RUNGS) + [None]
    executor = runtime.ScriptedExecutor({"THEMES": entries})
    for rung in fake.RUNGS:
        line = vs.FOLLOW_UP_LINES[rung][0]
        for n in (2, 3, 5):
            answers = [{"id": f"i{k}", "text": line} for k in range(n)]
            got = executor.execute(_job(executor_mod, rung, vs.NAMES[rung], answers))
            assert got["result"] == fake.themes(answers, vs.NAMES[rung]), (rung, n)
            assert got["result"]["themes"][-1]["label"] != fake.ON_THEIR_OWN, (rung, n)


def test_the_healthy_project_scripts_the_catch_all_alone():
    from harness import vectors_script as vs                               # noqa: PLC0415
    healthy = preludes.healthy_entry(_canon("05-paidly.yaml"))
    assert vs.failing_keys(healthy) == []
    # keel-cloud 119: held lines are grouped too -- every rung's one line is scripted on every project
    assert [e.get("dimension") for e in vs.generate(healthy).screens[vs.THEMES_SCREEN]] == list(fake.RUNGS) + [None]
