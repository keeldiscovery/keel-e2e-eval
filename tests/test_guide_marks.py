"""Spec 054: the guide marks (`evals/guide_marks.py`) over records shaped like the journeys' -- S-005 local (the walk
and the replays), S-006 local (the welcome alone) and a remote one (no seam) -- each mark met on a good record and failed
by a fault seeded into it, so no mark is a pass that cannot fail; an absent subject is unmeasured, never passed."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from evals import corpus_scenario
from evals import guide_marks as marks
from instructions import marks as instruction_marks
from stack.config import load_config

REPO = Path(__file__).resolve().parent.parent
#: Spec 057's marks, unmeasured on a record that carries only the welcome's subjects.
TEACHING = ["G6", "G7", "G8", "G9", "G10", "G11", "G12"]
#: Spec 059's marks (Interviews › Sent), unmeasured on a record that carries none of their subjects.
SENT = ["G13", "G14", "G15", "G16", "G17"]
#: keel-web 080 FR-1's hand-worked times (`welcome.cues.json`).
ATS = (0.3, 13.25, 23.7, 33.67, 46.38, 51.84, 60.46, 73.82, 76.39, 80.92, 83.13, 86.08, 92.51, 98.31)  # keel-web 081, v2
SKIP = {"present": True, "visible": True, "enabled": True, "in_view": True, "hit": True, "focused": True,
        "words": "Skip ›"}
CONTROLS = [{"tag": "button", "testid": None, "role": None, "words": "", "label": "Sound on", "visible": True},
            {"tag": "button", "testid": "guide-skip", "role": None, "words": "Skip ›", "label": None, "visible": True}]


def welcome(*, door: str = "skip", seam: bool = True) -> dict:
    """The `welcome` record `leg_welcome` writes (local unless `seam` is False)."""
    return {
        "profile": "local" if seam else "remote", "door": door,
        "first_open": {"present": True, "received": {"welcomeSeen": False, "openersSeen": []},
                       "url": "http://localhost:5173/p/7/define/context"},
        "first_frame": {"cues_fired": [] if seam else None, "current_time": 0.0},
        "skip_reads": {"1280x720": dict(SKIP), "390x844": dict(SKIP)},
        "controls": copy.deepcopy(CONTROLS),
        "press": {"door": door, "gone_ms": 240,
                  "requests": [{"method": "POST", "path": "/v2/projects/7/guide-seen", "body": {"what": "WELCOME"},
                                "status": 204}]},
        "repeat": {"status": 204},
        "revision": {"before": 1, "after_press": 1, "after_repeat": 1},
        "next_open": {"count": 0, "received": {"welcomeSeen": True, "openersSeen": []}, "screen": True,
                      "overviews": 1},
        "wire_after": {"welcomeSeen": True, "openersSeen": []},
        "next_write": {"method": "PUT", "path": "/v2/projects/7/context", "status": 202, "presses": 1, "refused": []},
        "page_posts": [{"method": "POST", "path": "/v2/projects/7/guide-seen", "body": {"what": "WELCOME"},
                        "status": 204}],
        "later_frames": [0, 0, 0, 0],
        "seconds": 3.4,
    }


def walk() -> dict:
    ids = marks.WELCOME_CUES
    return {"served": [{"id": i, "at": a} for i, a in zip(ids, ATS)], "before": [], "held": True,
            "steps": [{"id": i, "seek": round(a + 0.05, 2), "cue": i, "fired": list(ids[:n + 1])}
                      for n, (i, a) in enumerate(zip(ids, ATS))]}


def replay() -> dict:
    return {"first": {"found": True, "via": "the Feedback panel", "opened": True, "current_time": 0.0, "skip": dict(SKIP),
                      "closed": True, "closed_by": "skip", "requests": []},
            "second": {"found": True, "via": "the Feedback panel", "opened": True, "closed": True, "closed_by": "end",
                       "requests": []},
            "after": {"welcomeSeen": True, "openersSeen": []}, "revision": {"before": 1, "after": 1}}


def s005_local() -> dict:
    return {"welcome": welcome(door="escape"), "walk": walk(), "replay": replay()}


def s006_local() -> dict:
    return {"welcome": welcome(), "notes": {"G4": marks.ELSEWHERE_WHY, "G5": marks.ELSEWHERE_WHY}}


def remote() -> dict:
    return {"welcome": welcome(seam=False), "notes": {"G4": marks.REMOTE_WHY, "G5": marks.REMOTE_WHY}}


def _by_mark(record: dict) -> dict:
    return {c.mark: c for c in marks.score(record)}


def _fails(record: dict, mark: str) -> None:
    check = _by_mark(record)[mark]
    assert check.measured and not check.ok, check


# ---------------------------------------------------------------------------------------------- good records

def test_the_version_is_three_and_the_instruction_marks_did_not_move():
    assert marks.GUIDE_MARKS_VERSION == 3
    assert instruction_marks.MARKS_VERSION == 23                  # spec 059 call 3: a journey ruler moved; 078: `read`; 093: L1/L5; 091: L1's draft count
    source = (REPO / "evals" / "guide_marks.py").read_text(encoding="utf-8")
    assert "v1 (spec 054, keel-cloud 106 / keel-web 080, contract 20)" in source
    assert "v2 (spec 057, keel-web 086 / keel-cloud 109, contract 22)" in source
    assert "v3 (spec 059, keel-web 088 / keel-cloud 111, contract 24)" in source
    assert [m for m, _, _ in marks.MARKS] == ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11",
                                              "G12", "G13", "G14", "G15", "G16", "G17"]


def test_every_mark_is_met_on_s005s_local_record():
    card = marks.scorecard(s005_local())
    assert card["version"] == 3
    assert card["measured"] == card["met"] == 5 and card["unmeasured"] == TEACHING + SENT, card
    assert marks.owed(s005_local()) == ["G1", "G2", "G3", "G4", "G5"]


@pytest.mark.parametrize("record,why", [(s006_local, marks.ELSEWHERE_WHY), (remote, marks.REMOTE_WHY)])
def test_elsewhere_g1_to_g3_are_met_and_g4_g5_unmeasured_with_the_why(record, why):
    card = marks.scorecard(record())
    assert card["measured"] == card["met"] == 3, card
    assert card["unmeasured"] == ["G4", "G5", *TEACHING, *SENT]
    assert card["why_unmeasured"] == {"G4": why, "G5": why}
    assert marks.owed(record()) == ["G1", "G2", "G3"]
    for check in card["checks"]:
        if check["mark"] in ("G4", "G5"):
            assert check["measured"] is False and check["ok"] is False


def test_the_remote_why_is_the_seams_build_rule():
    assert "window.__keelGuide only in its test build" in marks.REMOTE_WHY
    assert "staging serves the production build" in marks.REMOTE_WHY


@pytest.mark.parametrize("key,mark", [("walk", "G5"), ("replay", "G4")])
def test_an_absent_subject_is_unmeasured_and_never_passed(key, mark):
    record = s005_local()
    del record[key]
    check = _by_mark(record)[mark]
    assert not check.measured and not check.ok
    assert mark not in marks.owed(record)


def test_no_welcome_record_leaves_g1_to_g3_unmeasured():
    card = marks.scorecard({})
    assert card["measured"] == 0 and card["unmeasured"] == ["G1", "G2", "G3", "G4", "G5", *TEACHING, *SENT]


def test_a_record_that_cannot_be_read_fails_rather_than_crashes():
    record = s006_local()
    record["welcome"]["first_open"] = None
    check = _by_mark(record)["G1"]
    assert check.measured and not check.ok and "record could not be read" in check.detail


# ------------------------------------------------------------------------------------------------ G1 faults

def test_g1_fails_on_a_second_sheet_at_the_next_open():
    record = s006_local()
    record["welcome"]["next_open"]["count"] = 1
    _fails(record, "G1")


def test_g1_fails_on_a_sheet_over_a_later_frame():
    record = s006_local()
    record["welcome"]["later_frames"] = [0, 0, 1]
    _fails(record, "G1")


def test_g1_fails_when_no_later_frame_was_read():
    record = s006_local()
    record["welcome"]["later_frames"] = []
    _fails(record, "G1")


def test_g1_fails_on_a_second_welcome_post():
    record = s006_local()
    record["welcome"]["page_posts"].append(copy.deepcopy(record["welcome"]["page_posts"][0]))
    _fails(record, "G1")


def test_g1_fails_when_the_first_open_said_seen_or_drew_nothing():
    record = s006_local()
    record["welcome"]["first_open"]["received"] = {"welcomeSeen": True, "openersSeen": []}
    _fails(record, "G1")
    record = s006_local()
    record["welcome"]["first_open"]["present"] = False
    _fails(record, "G1")


# ------------------------------------------------------------------------------------------------ G2 faults

def test_g2_fails_on_skip_below_the_fold_at_the_phone_size():
    record = s006_local()
    record["welcome"]["skip_reads"]["390x844"].update({"in_view": False, "hit": False})
    _fails(record, "G2")


def test_g2_fails_on_skip_covered_at_the_desktop_size():
    record = s006_local()
    record["welcome"]["skip_reads"]["1280x720"]["hit"] = False
    _fails(record, "G2")


def test_g2_fails_on_a_size_never_read():
    record = s006_local()
    del record["welcome"]["skip_reads"]["390x844"]
    _fails(record, "G2")


def test_g2_fails_on_a_second_control_on_the_sheet():
    record = s006_local()
    record["welcome"]["controls"].append({"tag": "a", "testid": None, "words": "Play again later", "label": None})
    _fails(record, "G2")


def test_g2_fails_on_a_wordless_control_that_is_not_the_sound_toggle():
    record = s006_local()
    record["welcome"]["controls"].append({"tag": "button", "testid": None, "words": "", "label": "Close"})
    _fails(record, "G2")


def test_g2_fails_when_skip_is_not_the_worded_control():
    record = s006_local()
    record["welcome"]["controls"][1]["words"] = "Continue"
    _fails(record, "G2")


def test_g2_takes_the_sheet_with_no_sound_toggle():
    record = s006_local()
    record["welcome"]["controls"] = [c for c in record["welcome"]["controls"] if c["testid"] == "guide-skip"]
    assert _by_mark(record)["G2"].ok


def test_g2_fails_when_cues_had_fired_before_the_reads():
    record = s006_local()
    record["welcome"]["first_frame"]["cues_fired"] = ["wordmark", "three-questions"]
    _fails(record, "G2")
    record = remote()
    record["welcome"]["first_frame"]["current_time"] = 14.0
    _fails(record, "G2")


def test_g2_takes_the_wordmark_as_the_opening_frame():
    record = s006_local()
    record["welcome"]["first_frame"]["cues_fired"] = ["wordmark"]
    assert _by_mark(record)["G2"].ok


def test_g2_fails_on_a_close_slower_than_a_second_or_none():
    record = s006_local()
    record["welcome"]["press"]["gone_ms"] = 1_400
    _fails(record, "G2")
    record["welcome"]["press"]["gone_ms"] = None
    _fails(record, "G2")


# ------------------------------------------------------------------------------------------------ G3 faults

def test_g3_fails_on_a_409_on_the_next_write():
    record = s006_local()
    record["welcome"]["next_write"].update({"status": 409, "refused": [{"status": 409}]})
    _fails(record, "G3")


def test_g3_fails_on_a_second_press_of_the_next_write():
    record = s006_local()
    record["welcome"]["next_write"]["presses"] = 2
    _fails(record, "G3")


def test_g3_fails_on_a_revision_moved_by_the_post():
    record = s006_local()
    record["welcome"]["revision"]["after_press"] = 2
    _fails(record, "G3")
    record = s006_local()
    record["welcome"]["revision"]["after_repeat"] = 2
    _fails(record, "G3")


def test_g3_fails_on_a_post_not_answered_204_or_carrying_a_stage():
    record = s006_local()
    record["welcome"]["press"]["requests"][0]["status"] = 200
    _fails(record, "G3")
    record = s006_local()
    record["welcome"]["press"]["requests"][0]["body"] = {"what": "WELCOME", "stage": "PROBLEM"}
    _fails(record, "G3")
    record = s006_local()
    record["welcome"]["press"]["requests"] = []
    _fails(record, "G3")


def test_g3_fails_on_a_repeat_not_204():
    record = s006_local()
    record["welcome"]["repeat"]["status"] = 409
    _fails(record, "G3")


def test_g3_fails_when_the_wire_forgot():
    record = s006_local()
    record["welcome"]["wire_after"] = {"welcomeSeen": False, "openersSeen": []}
    _fails(record, "G3")
    record = s006_local()
    record["welcome"]["next_open"]["received"] = {"welcomeSeen": True, "openersSeen": ["PROBLEM"]}
    _fails(record, "G3")


# ------------------------------------------------------------------------------------------------ G4 faults

def test_g4_fails_on_a_post_during_a_replay():
    record = s005_local()
    record["replay"]["first"]["requests"] = [{"method": "POST", "body": {"what": "WELCOME"}, "status": 204}]
    _fails(record, "G4")
    record = s005_local()
    record["replay"]["second"]["requests"] = [{"method": "POST", "body": {"what": "WELCOME"}, "status": 204}]
    _fails(record, "G4")


def test_g4_fails_on_a_replay_that_never_opened_or_never_closed():
    record = s005_local()
    record["replay"]["first"]["opened"] = False
    _fails(record, "G4")
    record = s005_local()
    record["replay"]["second"]["closed"] = False
    _fails(record, "G4")


def test_g4_fails_on_a_replay_that_did_not_start_near_zero_or_hid_skip():
    record = s005_local()
    record["replay"]["first"]["current_time"] = 40.0
    _fails(record, "G4")
    record = s005_local()
    record["replay"]["first"]["skip"]["in_view"] = False
    _fails(record, "G4")


def test_g4_fails_on_a_moved_revision_or_a_forgotten_flag():
    record = s005_local()
    record["replay"]["revision"]["after"] = 2
    _fails(record, "G4")
    record = s005_local()
    record["replay"]["after"] = {"welcomeSeen": False, "openersSeen": []}
    _fails(record, "G4")


# ------------------------------------------------------------------------------------------------ G5 faults

def test_g5_fails_on_cue_ids_out_of_order():
    record = s005_local()
    served = record["walk"]["served"]
    served[3]["id"], served[4]["id"] = served[4]["id"], served[3]["id"]
    _fails(record, "G5")


def test_g5_fails_on_a_drawn_cue_out_of_order():
    record = s005_local()
    record["walk"]["steps"][5]["cue"] = "rows-hold"
    _fails(record, "G5")


def test_g5_fails_on_cues_fired_shrinking():
    record = s005_local()
    record["walk"]["steps"][6]["fired"] = list(marks.WELCOME_CUES[:3])
    _fails(record, "G5")


def test_g5_fails_on_a_cue_fired_twice():
    record = s005_local()
    record["walk"]["steps"][2]["fired"] = ["wordmark", "three-questions", "three-questions"]
    _fails(record, "G5")


def test_g5_fails_on_eleven_cues():
    record = s005_local()
    record["walk"]["served"] = record["walk"]["served"][:11]
    record["walk"]["steps"] = record["walk"]["steps"][:11]
    _fails(record, "G5")


def test_g5_fails_on_at_not_strictly_rising_or_a_duplicate_id():
    record = s005_local()
    record["walk"]["served"][7]["at"] = record["walk"]["served"][6]["at"]
    _fails(record, "G5")
    record = s005_local()
    record["walk"]["served"][11]["id"] = "wordmark"
    _fails(record, "G5")


def test_g5_takes_the_wordmark_already_fired_before_the_walk():
    record = s005_local()
    record["walk"]["before"] = ["wordmark"]
    assert _by_mark(record)["G5"].ok
    record["walk"]["before"] = ["wordmark", "three-questions"]
    _fails(record, "G5")


# ------------------------------------------------------------------------------------------ against keel-web

def _web_080() -> Path:
    root = load_config(validate=False).keel_web
    if not (root / "public" / "guide" / "welcome.cues.json").is_file():
        pytest.skip("keel-web predates spec 080 (no public/guide/welcome.cues.json)")
    return root


def test_the_twelve_cues_are_keel_webs_own():
    served = json.loads((_web_080() / "public/guide/welcome.cues.json").read_text(encoding="utf-8"))
    assert tuple(c["id"] for c in served) == marks.WELCOME_CUES
    assert served[1]["at"] == marks.SECOND_CUE_AT
    assert tuple(c["at"] for c in served) == ATS


def test_the_words_are_keel_webs_own():
    translate = (_web_080() / "src/lib/translate.ts").read_text(encoding="utf-8")
    assert "GUIDE_SKIP" in translate and '"Skip' in translate
    for label in marks.SOUND_LABELS:
        assert f'"{label}"' in translate, label


# ------------------------------------------------------------------------------------------- the journeys

def test_the_record_carries_every_corridor_frame_after_the_welcome():
    j = corpus_scenario.Journey(recorder=None, page=None, context=None, web_base="", cloud_base="", entry=None,
                                founder=None, people=[])
    j.guide = {"welcome": welcome()}
    j.framing = {"idea": [{"frame": {"welcome": 0}}],
                 "problem.prevalence": [{"frame": {"welcome": 0}}, {"frame": {"welcome": 1}}]}
    record = corpus_scenario.guide_record(j)
    assert record["welcome"]["later_frames"] == [0, 0, 1]
    assert j.guide["welcome"]["later_frames"] == [0, 0, 0, 0], "the journey's own record is not rewritten"
    assert not marks.score(record)[0].ok


def test_every_corpus_journey_holds_the_welcome_and_only_s005_walks_it():
    scenario = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    assert "journey.hold_welcome = True" in scenario
    assert "leg_welcome(journey, walk=welcome_walk)" in scenario and "_score_guide(journey)" in scenario
    assert 'welcome="hold" if j.hold_welcome else "pass"' in scenario
    s005 = (REPO / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    assert "welcome_walk=True" in s005
    for other in ("test_s006_paidly.py", "test_s007_mulchrun.py", "test_s014_green.py",
                  "test_s012_journey_through_a_host.py"):
        assert "welcome" not in (REPO / "evals" / other).read_text(encoding="utf-8"), other


def test_the_frame_holds_no_sheet():
    frame = {"progress": "Problem · 1 of 4", "dots": 4, "now": 1, "done": 0, "nav_locked": True, "nav_links": 0}
    corpus_scenario._hold_frame({**frame, "welcome": 0}, "PROBLEM", 1, 4)
    with pytest.raises(AssertionError):
        corpus_scenario._hold_frame({**frame, "welcome": 1}, "PROBLEM", 1, 4)


@pytest.mark.parametrize("face,ok", [
    ({"paused": False, "muted": True, "readyState": 4, "currentTime": 0.2, "currentTimeLater": 0.8, "error": None}, True),
    ({"paused": True, "muted": True, "readyState": 0, "currentTime": 0, "currentTimeLater": 0, "error": 4}, True),
    ({"paused": False, "muted": False, "readyState": 4, "currentTime": 0.2, "currentTimeLater": 0.8, "error": None},
     True),  # D31: sound on by default is playing too
    ({"paused": True, "muted": True, "readyState": 4, "currentTime": 0.2, "currentTimeLater": 0.2, "error": None}, False),
    ({"paused": False, "muted": True, "readyState": 4, "readyStateLater": 4, "currentTime": 0.2,
      "currentTimeLater": 0.2, "error": None}, False),
    ({"paused": False, "muted": True, "readyState": 1, "readyStateLater": 1, "currentTime": 0.0,
      "currentTimeLater": 0.0, "error": None}, True),
    # spec 057 D-01: loaded only during the 600 ms (1 -> 4) -- recorded, the clock not yet owed a move
    ({"paused": False, "muted": False, "readyState": 1, "readyStateLater": 4, "currentTime": 0.0,
      "currentTimeLater": 0.0, "error": None}, True),
    (None, False),
])
def test_playing_is_unpaused_muted_or_not_and_a_decode_error_or_a_slow_load_is_only_a_note(face, ok):
    assert corpus_scenario._playing(face)[0] is ok
