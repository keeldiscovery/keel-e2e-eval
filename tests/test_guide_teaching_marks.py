"""Spec 057: the teaching videos' marks G6-G12 (`evals/guide_marks.py`) -- each met on a good record, failed by a fault
seeded into it, and passing as **not applicable** where the served manifest says its clips are absent (today: only
`report-read`, `report-fails`, `stage-problem-1`, `stage-solution-1` are rendered). The tables of Acceptance 1:
sheet-once, the two-pill rule, the chapter chip, the pair choice, the word guard."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from evals import guide_marks as marks
from harness import vectors_screens as vs
from stack.config import load_config

POST = "/v2/projects/7/guide-seen"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _post(body: dict, status: int = 204) -> list[dict]:
    return [{"method": "POST", "path": POST, "body": body, "status": status}]


def _pill(clip: str, fresh: bool = False) -> dict:
    return {"clip": clip, "words": "", "label": None, "fresh": fresh}


def report(applicable: bool = True) -> dict:
    if not applicable:
        return {"applicable": False, "later": [0, 0, 0]}
    return {"applicable": True,
            "first_open": {"present": True, "received": {"welcomeSeen": True, "openersSeen": [], "reportSeen": False,
                                                         "lineFailedSeen": False},
                           "src": "http://localhost:5173/guide/report-read.mp4"},
            "press": {"door": "skip", "gone_ms": 80, "requests": _post({"report": True})},
            "wire_after": {"welcomeSeen": True, "openersSeen": [], "reportSeen": True, "lineFailedSeen": False},
            "next_open": {"count": 0, "received": {"reportSeen": True}, "screen": True},
            "later": [0, 0, 0]}


def overview(read: bool = True, fails: bool = True, watched: bool = True) -> dict:
    reads = [{"when": "board-too-few", "failing": False, "lineFailedSeen": False,
              "pills": [_pill("report-read")] if read else []},
             {"when": "board", "failing": True, "lineFailedSeen": False,
              "pills": ([_pill("report-read")] if read else []) + ([_pill("report-fails", True)] if fails else [])}]
    out = {"read_present": read, "fails_present": fails, "reads": reads}
    if watched and fails:
        out["watched"] = {"opened": True, "closed": True, "requests": _post({"lineFailed": True}),
                          "fresh_after": False, "wire_after": {"lineFailedSeen": True}}
    return out


def chapters(keys, *, seam: bool = True, b2b: bool = False) -> dict:
    one = {"chapters": list(keys), "b2b": b2b, "applicable": True, "opened": True, "seam": seam, "closed": True,
           "requests": [], "chip_first": "Chapter 1 of 2 · The two lines", "src_first": f"/guide/{keys[0]}.mp4"}
    if seam:
        one.update({"chip_second": "Chapter 2 of 2 · The two lists", "src_second": f"/guide/{keys[1]}.mp4"})
    return one


def absent_stage(keys, b2b: bool = False) -> dict:
    return {"chapters": list(keys), "b2b": b2b, "applicable": False, "pills": []}


def stages(*, b2b: bool = False, present: bool = True) -> dict:
    make = chapters if present else absent_stage
    return {"PROBLEM": make(marks.STAGE_CHAPTERS["PROBLEM"]), "SOLUTION": make(marks.STAGE_CHAPTERS["SOLUTION"]),
            "COMMERCIAL": make(marks.MONEY_CHAPTERS[b2b], b2b=b2b)}


def explainers(present: bool = True) -> dict:
    return {"questions": {k: {"clip": c, "present": present, "pills": [_pill(c)] if present else []}
                          for k, c in marks.EXPLAINERS.items()},
            "bands": {"PROBLEM": {"dimension": "problem.prevalence", "clip": "explain-prevalence", "opened": True,
                                  "disabled_before": False, "fields_before": 5, "disabled_open": True,
                                  "fields_open": 0, "closed": True, "requests": [], "disabled_after": False,
                                  "fields_after": 5}}
            if present else {},
            "owed_bands": ["PROBLEM"] if present else []}


def openers(present: bool = True) -> dict:
    return {"stages": {v: ({"present": True, "shown": True,
                            "press": {"door": "skip", "gone_ms": 70,
                                      "requests": _post({"what": "OPENER", "stage": v})}}
                           if present else {"present": False, "shown": False}) for v in marks.VECTORS},
            "final": list(marks.VECTORS) if present else [], "later": [0, 0, 0]}


def captions(present: bool = True) -> dict:
    clips = {k: {"served": True, "words": [], "cues": 40} for k in ("report-read", "report-fails")} if present else {}
    return {"clips": clips, "snippets": ["Worth solving", "12 of 20 said yes"] if present else []}


def full(**kw) -> dict:
    return {"report": report(), "overview": overview(), "stages": stages(b2b=kw.get("b2b", False)),
            "explainers": explainers(), "openers": openers(), "captions": captions()}


#: Today's renders: the two report clips and chapter 1 of two stages -- G8-G11 not applicable, G6/G7/G12 measured.
def today() -> dict:
    return {"report": report(), "overview": overview(), "stages": stages(present=False),
            "explainers": explainers(False), "openers": openers(False), "captions": captions()}


def _check(record: dict, mark: str) -> marks.Check:
    return {c.mark: c for c in marks.score(record)}[mark]


def _met(record: dict, mark: str) -> None:
    check = _check(record, mark)
    assert check.measured and check.ok and check.applicable, check


def _failed(record: dict, mark: str) -> None:
    check = _check(record, mark)
    assert check.measured and not check.ok, check


# ------------------------------------------------------------------------------------------- good records

@pytest.mark.parametrize("b2b", [False, True])
def test_every_teaching_mark_is_met_with_every_clip_present(b2b):
    card = marks.scorecard(full(b2b=b2b))
    teaching = [c for c in card["checks"] if c["mark"] in ("G6", "G7", "G8", "G9", "G10", "G11", "G12")]
    assert all(c["measured"] and c["ok"] and c["applicable"] for c in teaching), teaching
    assert card["not_applicable"] == []


def test_todays_renders_leave_g8_to_g11_not_applicable_and_never_red():
    card = marks.scorecard(today())
    assert card["not_applicable"] == ["G8", "G9", "G10", "G11"], card
    assert all(c["ok"] for c in card["checks"] if c["measured"]), card["checks"]
    assert marks.owed(today()) == ["G6", "G7", "G8", "G9", "G10", "G11", "G12"]


def test_every_mark_not_applicable_when_nothing_is_rendered():
    record = {"report": report(False), "overview": overview(False, False), "stages": stages(present=False),
              "explainers": explainers(False), "openers": openers(False), "captions": captions(False)}
    card = marks.scorecard(record)
    assert card["not_applicable"] == ["G6", "G7", "G8", "G9", "G10", "G11", "G12"]
    assert card["met"] == card["measured"] == 7


def test_the_design_ids_name_every_new_mark():
    assert set(marks.DESIGN_IDS) == {"G6", "G7", "G8", "G9", "G10", "G11", "G12", "G13", "G14", "G15", "G16", "G17"}


# ---------------------------------------------------------------------------------- G6: the sheet once

@pytest.mark.parametrize("fault", [
    lambda r: r["first_open"].update(present=False),
    lambda r: r["first_open"]["received"].update(reportSeen=True),
    lambda r: r["first_open"].update(src="/guide/welcome.mp4"),
    lambda r: r["press"].update(requests=_post({"report": True}) * 2),
    lambda r: r["press"].update(requests=_post({"what": "REPORT"})),
    lambda r: r["press"].update(requests=_post({"report": True}, 422)),
    lambda r: r["press"].update(gone_ms=None),
    lambda r: r["wire_after"].update(reportSeen=False),
    lambda r: r["next_open"].update(count=1),
    lambda r: r.update(later=[0, 1, 0]),
], ids=["no sheet", "seen already", "another clip", "two posts", "wrong body", "refused", "never closed",
        "wire forgot", "again at the next open", "again later"])
def test_g6_sheet_once_faults(fault):
    record = full()
    fault(record["report"])
    _failed(record, "G6")


def test_g6_an_absent_clip_with_a_sheet_anyway_fails():
    record = full()
    record["report"] = {"applicable": False, "later": [1, 0]}
    _failed(record, "G6")


# ------------------------------------------------------------------------------- G7: the two-pill rule

@pytest.mark.parametrize("pills,failing,seen,ok", [
    (["report-read"], False, False, True),
    (["report-read", ("report-fails", True)], True, False, True),
    (["report-read", ("report-fails", False)], True, True, True),
    (["report-read", ("report-fails", True)], False, False, False),       # a second pill with nothing failed
    (["report-read"], True, False, False),                                # no second pill on a failed line
    (["report-read", ("report-fails", False)], True, False, False),       # not fresh before it was watched
    (["report-read", ("report-fails", True)], True, True, False),         # still fresh after
    ([], False, False, False),                                            # no How to read this
    (["report-read", "report-read"], False, False, False),                # two bands' pills
], ids=["one pill", "two, fresh", "two, watched", "second without a failure", "no second", "not fresh",
        "fresh after", "none", "two firsts"])
def test_g7_two_pill_rule(pills, failing, seen, ok):
    drawn = [_pill(p) if isinstance(p, str) else _pill(*p) for p in pills]
    record = full()
    record["overview"] = {"read_present": True, "fails_present": True,
                          "reads": [{"when": "board", "failing": failing, "lineFailedSeen": seen, "pills": drawn}]}
    check = _check(record, "G7")
    assert check.ok is ok, check


def test_g7_pills_read_by_words_when_no_clip_key_is_carried():
    record = full()
    record["overview"]["reads"][1]["pills"] = [{"clip": None, "words": "How to read this · 2 min", "fresh": False},
                                               {"clip": None, "words": "When a line fails · 1 min", "fresh": True}]
    record["overview"]["reads"][0]["pills"] = [{"clip": None, "words": "How to read this · 2 min", "fresh": False}]
    _met(record, "G7")
    assert not marks.is_pill({"words": "How to read these charts · 3 min"}, "report-read")


@pytest.mark.parametrize("fault", [
    lambda w: w.update(requests=[]),
    lambda w: w.update(requests=_post({"lineFailed": True}) * 2),
    lambda w: w.update(fresh_after=True),
    lambda w: w.update(wire_after={"lineFailedSeen": False}),
], ids=["no post", "two posts", "still fresh", "wire forgot"])
def test_g7_watching_faults(fault):
    record = full()
    fault(record["overview"]["watched"])
    _failed(record, "G7")


def test_g7_an_absent_clip_draws_no_pill():
    record = full()
    record["overview"] = overview(read=False, fails=True, watched=False)
    record["overview"]["reads"][0]["pills"] = [_pill("report-read")]
    _failed(record, "G7")


# ------------------------------------------------------------------------------- G8: the chapter chip

@pytest.mark.parametrize("fault", [
    lambda o: o.update(opened=False),
    lambda o: o.update(chip_first="Chapter 2 of 2"),
    lambda o: o.update(chip_second="Chapter 1 of 2"),
    lambda o: o.update(src_second="/guide/stage-problem-1.mp4"),
    lambda o: o.update(src_first="/guide/welcome.mp4"),
    lambda o: o.update(closed=False),
], ids=["no band", "chip starts at 2", "chip never moves", "chapter 2 replays 1", "another clip", "never closed"])
def test_g8_chapter_faults(fault):
    record = full()
    fault(record["stages"]["PROBLEM"])
    _failed(record, "G8")


def test_g8_without_the_seam_holds_chapter_one_alone():
    record = full()
    record["stages"]["PROBLEM"] = chapters(marks.STAGE_CHAPTERS["PROBLEM"], seam=False)
    _met(record, "G8")


def test_g8_one_chapter_present_is_not_applicable():
    record = full()
    record["stages"] = stages(present=False)
    assert _check(record, "G8").applicable is False and _check(record, "G8").ok


# ------------------------------------------------------------------------------------- G9: the pair

@pytest.mark.parametrize("b2b,played,ok", [
    (False, marks.MONEY_CHAPTERS[False], True),
    (True, marks.MONEY_CHAPTERS[True], True),
    (False, marks.MONEY_CHAPTERS[True], False),
    (True, marks.MONEY_CHAPTERS[False], False),
], ids=["consumer pair", "business pair", "consumer played business", "business played consumer"])
def test_g9_pair_choice(b2b, played, ok):
    record = full(b2b=b2b)
    one = record["stages"]["COMMERCIAL"]
    one["src_first"], one["src_second"] = f"/guide/{played[0]}.mp4", f"/guide/{played[1]}.mp4"
    assert _check(record, "G9").ok is ok


# -------------------------------------------------------------------------------------- G10, G11

@pytest.mark.parametrize("fault", [
    lambda x: x["questions"]["problem.importance"].update(pills=[]),
    lambda x: x["questions"]["problem.importance"].update(pills=[_pill("explain-importance")] * 2),
    lambda x: x["bands"]["PROBLEM"].update(disabled_open=False),
    lambda x: x["bands"]["PROBLEM"].update(disabled_after=True),
    lambda x: x["bands"]["PROBLEM"].update(fields_open=5),
    lambda x: x["bands"]["PROBLEM"].update(fields_after=0),
    lambda x: x["bands"]["PROBLEM"].update(closed=False),
    lambda x: x.update(bands={}),
    lambda x: x["questions"]["idea"].update(pills=[]),
], ids=["missing pill", "two pills", "primary live while open", "primary dead after", "field under the band",
        "field never back", "never closed", "no band",
        "no pill on Your idea"])
def test_g10_explainer_faults(fault):
    record = full()
    fault(record["explainers"])
    _failed(record, "G10")


def test_g10_an_absent_explainer_with_a_pill_fails():
    record = full()
    record["explainers"] = explainers(False)
    record["explainers"]["questions"]["commercial.price"]["pills"] = [
        _pill("explain-price")]
    _failed(record, "G10")


@pytest.mark.parametrize("fault", [
    lambda x: x["stages"]["SOLUTION"].update(shown=False),
    lambda x: x["stages"]["SOLUTION"]["press"].update(requests=_post({"what": "OPENER"})),
    lambda x: x.update(final=["SOLUTION", "PROBLEM", "COMMERCIAL"]),
    lambda x: x.update(final=["PROBLEM", "SOLUTION"]),
    lambda x: x.update(later=[0, 1]),
], ids=["not shown", "no stage", "out of order", "one missing", "came back"])
def test_g11_opener_faults(fault):
    record = full()
    fault(record["openers"])
    _failed(record, "G11")


def test_g11_only_the_present_openers_are_owed_in_order():
    record = full()
    record["openers"]["stages"]["SOLUTION"] = {"present": False, "shown": False}
    record["openers"]["final"] = ["PROBLEM", "COMMERCIAL"]
    _met(record, "G11")


# ---------------------------------------------------------------------------------- G12: the word guard

@pytest.mark.parametrize("text,found", [
    ("Congratulations. The project is set up.", []),
    ("as described above", []),
    ("midnight and overnight", []),
    ("parents of a newborn", ["parents"]),
    ("the Baby cries at Night", ["Baby", "cries", "Night"]),
    ("crying, cried, cries", ["crying", "cried", "cries"]),
    ("Payroll in chocolate", ["Payroll", "chocolate"]),
    ("a lullaby app", ["lullaby"]),
], ids=["clean", "described", "midnight", "parents", "baby night", "cry forms", "payroll chocolate", "lullaby"])
def test_g12_word_guard(text, found):
    assert marks.project_words(text) == found


@pytest.mark.parametrize("fault", [
    lambda x: x["clips"]["report-read"].update(words=["parents"]),
    lambda x: x["clips"]["report-fails"].update(served=False),
    lambda x: x["snippets"].append("Nights a week the baby wakes"),
], ids=["caption word", "not served", "snippet word"])
def test_g12_faults(fault):
    record = full()
    fault(record["captions"])
    _failed(record, "G12")


# -------------------------------------------------------------------------------------------- the reads

@pytest.mark.parametrize("body", [
    {"report-read": {"present": True, "duration": 112.4}, "explain-price": {"present": False}},
    {"clips": {"report-read": {"present": True, "duration": 112.4}, "explain-price": {"present": False}}},
    [{"key": "report-read", "present": True, "duration": 112.4}, {"key": "explain-price", "present": False}],
], ids=["map", "under clips", "list"])
def test_the_manifest_reads_every_shape(body):
    assert vs.normal_manifest(body) == {"report-read": {"present": True, "duration": 112.4},
                                        "explain-price": {"present": False, "duration": None}}


@pytest.mark.parametrize("body", [None, "<!doctype html>", {"version": 1}])
def test_an_unserved_manifest_is_every_clip_absent(body):
    assert vs.normal_manifest(body) == {}


def test_g3_reads_the_welcome_flags_alone_on_contract_22():
    assert marks._welcome_flags({"welcomeSeen": True, "openersSeen": [], "reportSeen": False,
                                 "lineFailedSeen": False}) == {"welcomeSeen": True, "openersSeen": []}


def test_086s_pill_test_ids_name_the_family():
    assert marks.is_pill({"testid": "guide-pill-explain", "words": "Hear this one · 36 s"}, "explain-prevalence")
    assert marks.is_pill({"testid": "guide-pill-report-fails", "words": "When a line fails"}, "report-fails")
    assert not marks.is_pill({"testid": "guide-pill-stage", "words": "How to read these charts"}, "report-read")


def test_the_corridor_frame_reads_pills_and_openers():
    import inspect
    source = inspect.getsource(vs.Corridor.frame)
    assert '"pills"' in source and '"openers": self.page.locator(GUIDE_OPENER).count()' in source


# -------------------------------------------------------------------------- against keel-web's own files

def _guide_dir() -> Path:
    return load_config(validate=False).keel_web / "public" / "guide"


def test_g12_every_vtt_keel_web_carries_has_no_project_word():
    """Judgement call 1's unit half: the journey reads the served vtts; this reads the checkout's (skips before 086)."""
    vtts = sorted(p for p in _guide_dir().glob("*.vtt") if p.name != "welcome.vtt")
    if not vtts:
        pytest.skip("keel-web predates spec 086 (no teaching vtt)")
    found = {p.name: marks.project_words(p.read_text(encoding="utf-8")) for p in vtts}
    assert not {k: v for k, v in found.items() if v}, found


def test_every_present_clip_in_keel_webs_manifest_is_one_the_marks_know():
    path = _guide_dir() / "manifest.json"
    if not path.is_file():
        pytest.skip("keel-web predates spec 086 (no manifest)")
    import json
    keys = set(vs.normal_manifest(json.loads(path.read_text(encoding="utf-8"))))
    known = {"report-read", "report-fails", *marks.OPENERS.values(), *marks.EXPLAINERS.values(),
             *(k for pair in marks.STAGE_CHAPTERS.values() for k in pair),
             *(k for pair in marks.MONEY_CHAPTERS.values() for k in pair), "explain-your-idea",
             *marks.PAGE_CLIPS}                                       # spec 059: keel-web 088's three page clips
    # keel-web 090 added two landing clips (landing-intro, sample-question) that no mark reads: a public page's
    # tour and the sample's question, outside the teaching marks (061 follow-up, 2026-10-22).
    # keel-web 110 / 111 (spec 071): the home's video card (home-intro), Try one's solution and money questions
    # (sample-question-solution / -money) and the four scoped *How to read this* clips (report-read-<scope>: a study of
    # one scope's Overview -- never met by an ALL journey, which reads report-read). None is a teaching mark's.
    public = {"welcome", "interviewer-sample", "landing-intro", "sample-question", "home-intro",
              "sample-question-solution", "sample-question-money"}
    scoped = {"report-read-problem", "report-read-solution", "report-read-solution-money", "report-read-money"}
    assert keys and keys <= known | public | scoped, sorted(keys - known - public - scoped)


@pytest.mark.parametrize("testid", ["guide-report", "guide-opener", "guide-pill-new", "guide-band", "guide-chapter"])
def test_every_teaching_selector_is_in_keel_web(testid):
    root = load_config(validate=False).keel_web / "src"
    if not (_guide_dir() / "manifest.json").is_file():
        pytest.skip("keel-web predates spec 086")
    hits = [p for p in root.rglob("*.tsx")
            if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")
            or f'testId="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert f"'{testid}'" in Path(vs.__file__).read_text(encoding="utf-8")


def test_a_full_record_is_not_mutated_by_scoring():
    record = full()
    before = copy.deepcopy(record)
    marks.scorecard(record)
    assert record == before


def test_g10_a_primary_off_before_an_answer_is_held_to_its_own_before():
    record = full()
    record["explainers"]["bands"]["PROBLEM"].update(disabled_before=True, disabled_after=True)
    _met(record, "G10")


# ------------------------------------------------------- the pass-by: every journey but S-005 skips the sheets

class _Sheet:
    """GuideWelcome's stand-in: `up` sheets now, `comes` whether a due one arrives; Skip recorded."""
    def __init__(self, up: int, comes: bool):
        self.up, self.comes, self.skipped = up, comes, 0

    def count(self):
        return self.up

    def present(self, timeout_s=10):
        return self.comes

    def _press_skip(self):
        self.skipped += 1

    def _close(self, press):
        press()
        return {"gone_ms": 40, "requests": _post({"report": True})}


class _Recorder:
    from contextlib import contextmanager

    def __init__(self):
        self.notes = []

    @contextmanager
    def step(self, name, *, party, kind):
        self.notes.append((name, kind))
        yield type("H", (), {})()


class _Page:
    url = "http://localhost:5173/p/7/define/problem/seed"


def _pass(monkeypatch, kind, *, up=0, comes=True, guide=None, present=True, stage=None):
    made = {}

    def sheet(page, recorder, base, *, sheet):
        made["selector"] = sheet
        made["sheet"] = _Sheet(up, comes)
        return made["sheet"]

    monkeypatch.setattr(vs, "GuideWelcome", sheet)
    monkeypatch.setattr(vs, "_due_guide", lambda page, base: guide)
    monkeypatch.setitem(vs._MANIFESTS, "http://web", {"opener-the-problem": {"present": present},
                                                       "report-read": {"present": present}})
    recorder = _Recorder()
    out = vs.pass_teaching_sheet(_Page(), recorder, "http://web", kind, stage)
    return out, made, recorder


SEEN = {"welcomeSeen": True, "openersSeen": [], "reportSeen": False, "lineFailedSeen": False}


@pytest.mark.parametrize("guide,present,up,shown", [
    (SEEN, True, 0, True),                                       # due: waited for and skipped
    ({**SEEN, "openersSeen": ["PROBLEM"]}, True, 0, False),      # seen: no wait
    (SEEN, False, 0, False),                                     # clip absent: no wait
    ({"welcomeSeen": True, "openersSeen": []}, True, 0, False),  # a cloud before contract 22
    ({**SEEN, "openersSeen": ["PROBLEM"]}, True, 1, True),       # already up: skipped whatever the wire says
], ids=["due", "seen", "absent", "contract 20", "up"])
def test_the_opener_is_passed_by_at_a_stages_first_open(monkeypatch, guide, present, up, shown):
    out, made, recorder = _pass(monkeypatch, "opener", guide=guide, present=present, up=up)
    assert out["shown"] is shown
    assert made["selector"] == vs.GUIDE_OPENER
    assert made["sheet"].skipped == (1 if shown else 0)
    assert [k for _, k in recorder.notes] == (["note"] if shown else [])
    if shown:
        assert out["stage"] == "PROBLEM"     # read off the address, as 086's stageOfPath does


@pytest.mark.parametrize("guide,shown", [(SEEN, True), ({**SEEN, "reportSeen": True}, False)], ids=["due", "seen"])
def test_the_report_sheet_is_passed_by_at_the_reports_first_open(monkeypatch, guide, shown):
    out, made, recorder = _pass(monkeypatch, "report", guide=guide)
    assert out["shown"] is shown and made["selector"] == vs.GUIDE_REPORT
    assert made["sheet"].skipped == (1 if shown else 0)


def test_only_s005_measures_the_teaching_marks():
    import inspect
    from evals import corpus_scenario
    assert "teaching=True" in (REPO_ROOT / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    for name in ("test_s006_paidly.py", "test_s007_mulchrun.py", "test_s014_green.py"):
        assert "teaching=True" not in (REPO_ROOT / "evals" / name).read_text(encoding="utf-8")
    assert "teaching: bool = False" in inspect.getsource(corpus_scenario.run)
    for page_object in (vs.Corridor.seed, vs.Corridor.persona, vs.Answers._report):
        assert "pass_teaching_sheet(" in inspect.getsource(page_object)
