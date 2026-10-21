"""Spec 059: Interviews › Sent reworked in the guide marks, G13-G17 (`evals/guide_marks.py`) -- each met on a good
record, failed by a fault seeded into it, not applicable where the served manifest says the page clips are absent. The
tables of Acceptance 1: the sheet once, the order, the range words for n = 4 / 10 / 11 / 14, the count words, the csv
line count, the sort flip; and the Sent-open helper's pass-by, which leaves a journey that only passed the sheet with
no G13 subject (FR-4)."""

from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import corpus_scenario
from evals import guide_marks as marks
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from stack.config import load_config

POST = "/v2/projects/7/guide-seen"
SEEN = {"welcomeSeen": True, "openersSeen": ["PROBLEM", "SOLUTION", "COMMERCIAL"], "reportSeen": True,
        "lineFailedSeen": False}


def _post(body: dict, status: int = 204) -> list[dict]:
    return [{"method": "POST", "path": POST, "body": body, "status": status}]


def interviews(applicable: bool = True) -> dict:
    if not applicable:
        return {"judged": True, "applicable": False, "first_open": {"present": False}, "later": [{"shown": False}]}
    return {"judged": True, "applicable": True,
            "first_open": {"present": True, "received": {**SEEN, "interviewsSeen": False},
                           "src": "http://localhost:5173/guide/page-interviews-first.mp4"},
            "press": {"door": "skip", "gone_ms": 90, "requests": _post({"interviews": True})},
            "wire_after": {**SEEN, "interviewsSeen": True},
            "next_open": {"count": 0, "received": {**SEEN, "interviewsSeen": True}, "screen": True},
            "later": [{"shown": False, "url": "/p/7/interviews/sent"}] * 4}


def sent_pill(*, seam: bool = True) -> dict:
    one = {"applicable": True, "pills": [{"testid": "guide-pill-page", "words": "How this page works · 3 min"}],
           "opened": True, "in_place": True, "seam": seam, "chip_first": "Chapter 1 of 2 · Where to start",
           "src_first": "/guide/page-interviews-first.mp4", "closed": True, "requests": [], "pill_back": True}
    if seam:
        one.update({"chip_second": "Chapter 2 of 2 · This page", "src_second": "/guide/page-sent.mp4"})
    return one


def contacts_pill(view: str = "datasets") -> dict:
    if view != "datasets":
        return {"view": view, "applicable": True, "pills": []}
    return {"view": "datasets", "applicable": True,
            "pills": [{"testid": "guide-pill-page", "words": "How this page works · 2 min"}],
            "opened": True, "src": "/guide/page-contacts.mp4", "chip": "", "closed": True, "requests": []}


def order(*, band: bool = True, when: str = "after the first recording") -> dict:
    regions = {"kicker": 80, "total": 110, "pill": 150, "band": 210 if band else None, "cards": 300 if band else 210,
               "links": 620 if band else 530}
    return {"when": when, "regions": regions, "words": {}, "how_it_works": 0, "pill_owed": True, "band_owed": band}


def sent_order() -> dict:
    return {"readings": [order(band=False, when="after the links"), order()], "band_owed": True}


def links(n: int = 12) -> dict:
    names = [f"Person {i:02d}" for i in range(n)]
    page = names[:10]
    one = {"when": "after the links", "n": n, "drawn": n,
           "frame": {"heading": f"Links · {n}", "search": n >= 6, "download": "Download (.csv)",
                     "same_row": n >= 6, "download_row": True,
                     "range": marks.range_owed(n)[0], "prev": False if n > 10 else None,
                     "next": True if n > 10 else None,
                     "sorts": {"who": "none", "format": "none", "made": "descending", "status": "none"},
                     "rows": page},
           "sort": {"column": "made", "before": "descending", "after": "ascending", "rows": page[::-1],
                    "back": {"column": "made", "before": "ascending", "after": "descending", "rows": page}},
           "csv": {"header": marks.CSV_HEADER, "lines": n + 1}}
    if n >= 6:
        one["search"] = {"term": page[0], "found": [page[0]], "range": None,
                         "cleared": {"rows": page, "range": one["frame"]["range"]}}
    if n > 10:
        one["next_page"] = {"moved": True, "range": marks.sent_range(11, min(n, 20), n), "rows": names[10:20],
                            "next": n > 20, "prev": True}
    return {"readings": [one]}


def _kind(label, rtype, made, answered, aim):
    return {"label": label, "respondentType": rtype, "linksMade": made, "answered": answered, "aim": aim}


def role_counts() -> dict:
    kinds = [_kind("Translators", "PRIMARY", 11, 6, "aim for 4 more"),
             _kind("Agency project managers", "COMMERCIAL_B2B", 0, 0, "aim for 8 more")]
    invitations = [{"respondentType": "PRIMARY", "status": "ANSWERED"}] * 6 + \
        [{"respondentType": "PRIMARY", "status": "SENT"}] * 5
    cards = [{"label": "Translators", "button": "Send links", "count": "6 answered of 11 sent · aim for 4 more",
              "hints": 0},
             {"label": "Agency project managers", "button": "Send links",
              "count": "nothing sent yet · invite about 7", "hints": 0}]
    return {"readings": [{"when": "after the first recording", "cards": cards, "kinds": kinds,
                          "invitations": invitations, "drawn_rows": 11}]}


def full() -> dict:
    return {"interviews": interviews(), "page_pills": {"sent": sent_pill(), "contacts": contacts_pill("consumer")},
            "sent_order": sent_order(), "links": links(), "role_counts": role_counts()}


def _check(record: dict, mark: str) -> marks.Check:
    return {c.mark: c for c in marks.score(record)}[mark]


def _met(record: dict, mark: str) -> None:
    check = _check(record, mark)
    assert check.measured and check.ok and check.applicable, (mark, check.detail)


def _failed(record: dict, mark: str) -> None:
    check = _check(record, mark)
    assert check.measured and not check.ok, (mark, check.detail)


# ------------------------------------------------------------------------------------------- good records

def test_every_sent_mark_is_met_on_the_guide_journeys_record():
    card = marks.scorecard(full())
    sent = [c for c in card["checks"] if c["mark"] in marks.SENT_MARKS]
    assert len(sent) == 5 and all(c["measured"] and c["ok"] and c["applicable"] for c in sent), sent
    assert marks.owed(full())[-5:] == list(marks.SENT_MARKS)


def test_the_links_journey_carries_g14s_contacts_half_and_g16s_paging():
    record = {"page_pills": {"contacts": contacts_pill()}, "links": links(28)}
    card = marks.scorecard(record)
    assert marks.owed(record) == ["G14", "G16"]
    assert all(c["ok"] for c in card["checks"] if c["mark"] in ("G14", "G16")), card["checks"]


def test_the_sent_marks_pass_as_not_applicable_where_the_page_clips_are_absent():
    record = {"interviews": interviews(False), "page_pills": {"sent": {"applicable": False, "pills": []},
                                                              "contacts": {"view": "datasets", "applicable": False,
                                                                           "pills": []}}}
    card = marks.scorecard(record)
    assert card["not_applicable"] == ["G13", "G14"], card


def test_the_design_ids_and_the_version():
    assert marks.GUIDE_MARKS_VERSION == 3
    assert {m: marks.DESIGN_IDS[m] for m in marks.SENT_MARKS} == {
        "G13": "D44", "G14": "D43 D46", "G15": "D43 (088 FR-1)", "G16": "088 FR-4", "G17": "088 FR-3"}


# ------------------------------------------------------------------------------- G13: the sheet once

@pytest.mark.parametrize("fault", [
    lambda r: r["first_open"].update(present=False),
    lambda r: r["first_open"]["received"].update(interviewsSeen=True),
    lambda r: r["first_open"].update(received=SEEN),                                     # a contract-22 cloud
    lambda r: r["first_open"].update(src="/guide/report-read.mp4"),
    lambda r: r["press"].update(requests=_post({"interviews": True}) * 2),
    lambda r: r["press"].update(requests=_post({"report": True})),
    lambda r: r["press"].update(requests=_post({"interviews": True}, 422)),
    lambda r: r["press"].update(gone_ms=None),
    lambda r: r["wire_after"].update(interviewsSeen=False),
    lambda r: r["next_open"].update(count=1),
    lambda r: r["next_open"]["received"].update(interviewsSeen=False),
    lambda r: r["later"].append({"shown": True, "url": "/p/7/interviews/sent"}),
], ids=["no sheet", "said seen", "no flag", "another clip", "two posts", "another body", "refused", "never gone",
        "wire forgot", "again next open", "next open unseen", "again later"])
def test_g13_fails_on_each_fault(fault):
    record = full()
    fault(record["interviews"])
    _failed(record, "G13")


def test_g13_an_absent_clip_drawing_a_sheet_fails():
    record = {"interviews": interviews(False)}
    record["interviews"]["later"].append({"shown": True})
    _failed(record, "G13")


# --------------------------------------------------------------------------------- G14: the page pills

@pytest.mark.parametrize("half,fault", [
    ("sent", lambda r: r.update(opened=False)),
    ("sent", lambda r: r.update(in_place=False)),
    ("sent", lambda r: r.update(chip_first="Chapter 1 of 2 · This page")),
    ("sent", lambda r: r.update(src_first="/guide/page-sent.mp4")),
    ("sent", lambda r: r.update(chip_second="Chapter 2 of 3 · This page")),
    ("sent", lambda r: r.update(src_second="/guide/page-interviews-first.mp4")),
    ("sent", lambda r: r.update(closed=False)),
    ("sent", lambda r: r.update(pill_back=False)),
    ("contacts", lambda r: r.update(src="/guide/page-sent.mp4")),
    ("contacts", lambda r: r.update(chip="Chapter 1 of 1 · This page")),
    ("contacts", lambda r: r.update(closed=False)),
    ("contacts", lambda r: r.update(opened=False)),
    ("contacts", lambda r: r.update(pills=[])),
], ids=["sent no band", "not in place", "chip 1 words", "chapter 1 clip", "chip 2 words", "chapter 2 clip",
        "sent never closed", "pill not back", "contacts clip", "a chip on one clip", "contacts never closed",
        "contacts no band", "contacts no pill"])
def test_g14_fails_on_each_fault(half, fault):
    record = {"page_pills": {"sent": sent_pill(), "contacts": contacts_pill()}}
    _met(record, "G14")
    fault(record["page_pills"][half])
    _failed(record, "G14")


def test_g14_on_the_remote_profile_reads_chapter_one_alone():
    _met({"page_pills": {"sent": sent_pill(seam=False)}}, "G14")


@pytest.mark.parametrize("view", ["consumer", "credits line"])
def test_g14_a_pill_off_the_datasets_view_fails(view):
    record = {"page_pills": {"contacts": {"view": view, "applicable": True,
                                          "pills": [{"testid": "guide-pill-page"}]}}}
    _failed(record, "G14")


# -------------------------------------------------------------------------------------- G15: the order

@pytest.mark.parametrize("fault", [
    lambda r: r["regions"].update(pill=50),                              # the pill above the kicker
    lambda r: r["regions"].update(band=400),                             # the band under the cards
    lambda r: r["regions"].update(links=200),                            # the links before the cards (068's order)
    lambda r: r["regions"].update(total=None),
    lambda r: r["regions"].update(pill=None),
    lambda r: r["regions"].update(band=None),
    lambda r: r.update(how_it_works=1),
], ids=["pill above the kicker", "band under the cards", "links first", "no total", "no pill", "no band",
        "How it works"])
def test_g15_fails_on_each_fault(fault):
    record = full()
    fault(record["sent_order"]["readings"][1])
    _failed(record, "G15")


def test_g15_a_band_never_drawn_where_one_is_owed_fails():
    record = {"sent_order": {"readings": [order(band=False, when="after the links")], "band_owed": True}}
    _failed(record, "G15")
    record["sent_order"]["band_owed"] = False                           # the remote profile: no interviewer leg
    _met(record, "G15")


# ---------------------------------------------------------------------------------- G16: the links table

@pytest.mark.parametrize("n,words,on", [(4, None, False), (10, None, False), (11, "1–10 of 11", True),
                                        (14, "1–10 of 14", True)])
def test_g16_the_range_owed_by_the_number_of_links(n, words, on):
    assert marks.range_owed(n) == (words, on)
    _met({"links": links(n)}, "G16")


@pytest.mark.parametrize("n,drawn,nxt", [(14, "1–10 of 13", True), (14, "1–10 of 14", False), (14, None, None),
                                         (11, "1–11 of 11", False), (10, "1–10 of 10", True), (4, "1–10 of 4", None)])
def test_g16_a_wrong_range_or_next_fails(n, drawn, nxt):
    record = {"links": links(n)}
    record["links"]["readings"][0]["frame"].update(range=drawn, next=nxt)
    _failed(record, "G16")


def test_g16_ten_or_fewer_may_draw_the_whole_range_with_next_off():
    record = {"links": links(4)}
    record["links"]["readings"][0]["frame"].update(range="1–4 of 4", next=False)
    _met(record, "G16")


@pytest.mark.parametrize("lines,ok", [(13, True), (12, False), (11, False), (14, False)])
def test_g16_the_csv_is_the_header_and_one_line_a_link(lines, ok):
    record = {"links": links(12)}
    record["links"]["readings"][0]["csv"]["lines"] = lines
    (_met if ok else _failed)(record, "G16")


def test_g16_csv_lines_counts_088s_file():
    text = marks.CSV_HEADER + "\n" + "\n".join(f'"Okafor, Hannah",Practitioner,Your own list,Text,2026-10-20,Not opened,'
                                               for _ in range(14)) + "\n"
    assert marks.csv_lines(text) == 15
    assert marks.csv_lines("") == 0


@pytest.mark.parametrize("before,after,back,ok", [
    ("descending", "ascending", "descending", True), ("ascending", "descending", "ascending", True),
    ("descending", "descending", "descending", False), ("none", "ascending", "none", False),
    ("descending", "ascending", "ascending", False)])
def test_g16_the_made_heading_flips_aria_sort(before, after, back, ok):
    record = {"links": links(12)}
    record["links"]["readings"][0]["sort"].update(before=before, after=after, back={"after": back})
    (_met if ok else _failed)(record, "G16")


@pytest.mark.parametrize("fault", [
    lambda r: r["search"].update(found=["Person 00", "Person 01"]),
    lambda r: r["search"]["cleared"].update(rows=["Person 00"]),
    lambda r: r.pop("search"),
    lambda r: r["frame"].update(same_row=False),
    lambda r: r["frame"].update(download="Download the links (.csv)"),
    lambda r: r["csv"].update(header="name,format"),
    lambda r: r["frame"].update(heading="Links · 9"),
    lambda r: r["frame"].update(rows=r["frame"]["rows"] + ["Person 10"]),
    lambda r: r["next_page"].update(range="1–10 of 12"),
    lambda r: r["sort"].update(column="who"),
], ids=["search did not narrow", "clear did not restore", "never searched", "download apart", "other words",
        "other header", "heading count", "eleven rows a page", "Next did not move", "another heading"])
def test_g16_fails_on_each_fault(fault):
    record = {"links": links(12)}
    fault(record["links"]["readings"][0])
    _failed(record, "G16")


def test_g16_under_six_links_no_search_box_is_owed():
    record = {"links": links(4)}
    assert "search" not in record["links"]["readings"][0]
    _met(record, "G16")
    record["links"]["readings"][0]["frame"]["download_row"] = False
    _failed(record, "G16")


# ---------------------------------------------------------------------------------- G17: the role counts

@pytest.mark.parametrize("kind,words", [
    (_kind("A", "PRIMARY", 11, 6, "aim for 4 more"), "6 answered of 11 sent · aim for 4 more"),
    (_kind("A", "PRIMARY", 11, 10, "aim for 0 more"), "10 answered of 11 sent · enough for now"),
    (_kind("A", "PRIMARY", 12, 12, "aim for -2 more"), "12 answered of 12 sent · enough for now"),
    (_kind("A", "PRIMARY", 3, 0, "plenty"), "0 answered of 3 sent · plenty"),                 # drawn verbatim
    (_kind("A", "PRIMARY", 0, 0, "aim for 7 more"), None),
])
def test_g17_the_count_words(kind, words):
    assert marks.role_count_words(kind) == words


@pytest.mark.parametrize("drawn,ok", [("nothing sent yet · invite about 7", True), ("nothing sent yet", True),
                                      ("Invite about 7", False), ("0 answered of 0 sent · aim for 8 more", False)])
def test_g17_a_kind_with_no_links(drawn, ok):
    record = {"role_counts": role_counts()}
    record["role_counts"]["readings"][0]["cards"][1]["count"] = drawn
    (_met if ok else _failed)(record, "G17")


@pytest.mark.parametrize("fault", [
    lambda r: r["cards"][0].update(count="6 answered of 12 sent · aim for 4 more"),
    lambda r: r["cards"][0].update(count="6 answered of 11 sent · enough for now"),
    lambda r: r["cards"][0].update(hints=1),                                         # the old line under the buttons
    lambda r: r["invitations"].pop(),                                                # the register says ten
    lambda r: r.update(drawn_rows=10),
    lambda r: r["cards"].pop(),
], ids=["sent number", "enough too soon", "count line under", "register disagrees", "rows drawn", "a card missing"])
def test_g17_fails_on_each_fault(fault):
    record = {"role_counts": role_counts()}
    fault(record["role_counts"]["readings"][0])
    _failed(record, "G17")


# ------------------------------------------------------------------- G12: the three page clips are read

def test_g12_reads_the_three_page_clips_with_the_rest():
    clips = {k: {"served": True, "words": [], "cues": 9} for k in ("report-read", *marks.PAGE_CLIPS)}
    record = {"captions": {"clips": clips, "snippets": [], "present": sorted(clips), "manifest": 29}}
    _met(record, "G12")
    record["captions"]["clips"]["page-sent"]["words"] = ["payroll"]
    _failed(record, "G12")
    del record["captions"]["clips"]["page-sent"]
    _failed(record, "G12")                                    # present in the manifest and not read


# ------------------------------------------------------------------- FR-4: the pass-by and the record

def _journey(guide: dict) -> SimpleNamespace:
    return SimpleNamespace(guide=guide, framing={}, teach=None)


def test_a_journey_that_only_passed_the_sheet_carries_no_g13_subject():
    guide = {"welcome": {}, "interviews": {"judged": False, "passed": [{"shown": True, "requests": []}]},
             "notes": {"G4": "elsewhere"}}
    record = corpus_scenario.guide_record(_journey(guide))
    assert "interviews" not in record and record["interviews_passed"] == [{"shown": True, "requests": []}]
    assert set(record["notes"]) >= {"G4", *marks.SENT_MARKS}
    assert "G13" not in marks.owed(record)


def test_the_guide_journeys_judged_record_is_kept_and_its_marks_owed():
    guide = {"interviews": interviews(), "links": links()}
    record = corpus_scenario.guide_record(_journey(guide))
    assert record["interviews"]["judged"] is True and "interviews_passed" not in record
    assert {"G13", "G16"} <= set(marks.owed(record))
    assert set(record["notes"]) == {"G14", "G15", "G17"}


class _Page:
    def __init__(self, url: str):
        self.url = url

    def locator(self, _sel):
        return SimpleNamespace(count=lambda: 0, first=None)

    def on(self, *_):                         # `_BrowserStep` listens for the console
        return None


def test_the_helper_waits_for_nothing_off_sent_and_records_nothing_shown():
    guide: dict = {}
    out = iv.pass_interviews_sheet(_Page("http://x/p/7/interviews/contacts"), recorder=None, base="http://x",
                                   guide=guide)
    assert out == {"shown": False, "why": "not on Sent"}
    assert guide == {"interviews": {"judged": False, "passed": []}}


def test_the_helper_keeps_every_later_open_on_the_judged_record():
    guide = {"interviews": {"judged": True, "later": []}}
    iv.pass_interviews_sheet(_Page("http://x/p/7/interviews/contacts"), recorder=None, base="http://x", guide=guide)
    assert guide["interviews"]["later"] == [{"shown": False, "url": "http://x/p/7/interviews/contacts"}]


def test_every_way_into_sent_goes_through_the_helper():
    """FR-4 / judgement call 2: the helper lives in `interviews_screens`; `Interviews.land`, `Contacts.go_to_send_more`
    and `Persona.sent` call it, and `walkthrough_again` (the *How it works* replay) is gone."""
    source = Path(iv.__file__).read_text(encoding="utf-8")
    persona = Path(ivs.__file__).read_text(encoding="utf-8")
    assert source.count("pass_interviews_sheet(") >= 3 and "_iv.pass_interviews_sheet(" in persona
    assert "def walkthrough_again" not in persona
    assert "Show all" not in source.split("class Contacts")[0].split("def register")[1].split("def _row")[0]


# ------------------------------------------------------------------- keel-web 088's own ids and words

def _web_088() -> Path:
    root = load_config(validate=False).keel_web
    table = root / "src/components/interviews/LinksTable.tsx"
    if not table.is_file():
        pytest.skip("keel-web predates spec 088 (no links table)")
    return root


@pytest.mark.parametrize("testid", ["links", "links-search", "links-download", "links-prev", "links-next",
                                    "links-range", "role-count", "persona-hear"])
def test_every_088_selector_is_in_keel_web(testid):
    root = _web_088() / "src"
    assert [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")], testid


def test_088s_words_are_the_harness_words():
    root = _web_088()
    translate = (root / "src/lib/translate.ts").read_text(encoding="utf-8")
    for word in (iv.SEE_ANSWERS, iv.NEW_LINK, iv.SENT_DOWNLOAD, iv.SENT_SEARCH_LABEL, iv.GUIDE_PILL_PAGE,
                 marks.ENOUGH, "Where to start", "This page", "nothing sent yet"):
        assert f'"{word}"' in translate, word
    assert "`${from}–${to} of ${total}`" in translate and iv.sent_range(1, 10, 14) == "1–10 of 14"
    assert "`${action}, ${name}`" in translate and iv.row_action(iv.NEW_LINK, "Hannah") == "New link, Hannah"
    assert '["name", "kind", "from", "format", "link made", "status", "answered at"]' in translate
    assert ",".join(iv.SENT_CSV_HEADER) == marks.CSV_HEADER
    assert 'testId="guide-interviews"' in (root / "src/routes/founder/interviews/InterviewsRoute.tsx").read_text(
        encoding="utf-8")
    sent = (root / "src/components/interviews/SentPage.tsx").read_text(encoding="utf-8")
    assert "HOW_IT_WORKS_LABEL" not in sent and 'id: "page"' in sent
    sizes = (root / "src/lib/sentTable.ts").read_text(encoding="utf-8")
    assert f"LINKS_PAGE_SIZE = {iv.LINKS_PAGE_SIZE}" in sizes and f"LINKS_SEARCH_FROM = {iv.LINKS_SEARCH_FROM}" in sizes
