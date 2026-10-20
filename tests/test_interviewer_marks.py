"""Spec 044: the AI interviewer marks (`evals/interviewer_marks.py`) over a record shaped like the leg's -- each met on a
good record and each failed by a fault seeded into it, so no mark is a pass that cannot fail; the fake and charge v9
restated (`harness/interviewer_fake.py`) against keel-cloud's own sources where the checkout carries them; the new
reads in `stack/ledger.py` refused on the remote profile; the leg's shape (the stand-ins reversed in a `finally`)."""

from __future__ import annotations

import copy
import inspect
import uuid

import pytest

from evals import interviewer_marks as marks
from harness import interviewer_fake as fake
from stack import ledger
from stack.config import load_config

PROJECT = str(uuid.uuid4())
NAME = "invoice payout service"
HOW = ("You send an invoice and the service pays you within seven days. It collects from the agency later.")
BELIEF = "The people building it believe it would get translators paid on time."
PITCH = "I spent six years chasing agencies for my own invoices and I want nobody else to have to."
HELD = "Got it. Moving on… say no to change"
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"


def _pair(action: str) -> list[dict]:
    return [{"kind": "HOLD", "credits": -400, "action": action, "price_version": fake.PRICE_VERSION, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": None, "actual_cost_micro_usd": None},
            {"kind": "SPEND", "credits": 0, "action": action, "price_version": None, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": 400, "actual_cost_micro_usd": 2_000_000}]


AI_INVITATION = str(uuid.uuid4())
CHOICE_INVITATION = str(uuid.uuid4())


def _reading(action: str, reason: str | None) -> dict:
    return {"kind": "HOLD", "credits": -35, "action": action, "price_version": fake.PRICE_VERSION, "project_id": PROJECT,
            "inference_job_id": str(uuid.uuid4()), "reason": reason}


def _clip(role: str, kind: str, item: str | None = None, script: str = "Words.", attempts: int = 1) -> dict:
    return {"id": str(uuid.uuid4()), "role": role, "kind": kind, "itemId": item, "script": script, "status": "DONE",
            "attempts": attempts, "durationSeconds": 0.1, "bytes": 1000}


SOLUTION = (f"Now the idea. It is called {NAME}. It claims to send an invoice and the service pays you within seven "
            f"days, and the benefit is it would get translators paid on time. I'll ask you 2 questions about that.")


RA = "solution.relative_advantage"
RA_TEXT = "You said a shorter reconciliation would have made no difference to your last delivery. What would have?"
RA_CLIP = str(uuid.uuid4())


def _text_walk(person: str, rung: str | None, line: str | None) -> dict:
    """One text walk's follow-up as `evals/corpus_scenario._hold_the_follow_up` records it."""
    if rung is None:
        return {"person": person, "asked": True, "owed": None, "route": {"status": 204, "body": {}}, "screen": None,
                "sent": None, "line": None}
    text = f"Question on {rung}."
    sent = {"dimension": rung, "text": line, "how": "TYPED", "skipped": False} if line else \
        {"dimension": rung, "skipped": True}
    return {"person": person, "asked": True, "owed": {"dimension": rung, "text": text},
            "route": {"status": 200, "body": {"dimension": rung, "text": text, "itemId": "f", "spoken": "x"}},
            "screen": {"kicker": "One last thing", "question": text, "did": "typed" if line else "skipped"},
            "sent": sent, "line": line}


def _ai_follow_up() -> dict:
    """S-006's AI link: the recorded path -- 4 s after the last sound, Back, then the silent window to the cap."""
    route = {"route": "follow-up", "status": 200, "sent": {"answers": []},
             "body": {"dimension": RA, "text": RA_TEXT, "itemId": "fu", "clip": {"clipId": RA_CLIP}}}
    heard = {"route": "transcribe", "status": 200, "sent": {"itemId": "fu", "maxSeconds": 120}, "body": {"text": "yes"}}
    windows = [{"which": "first", "step": "followUp", "question": RA_TEXT, "clip": RA_CLIP, "path": "recorded",
                "ended": "quiet", "quiet_to_stop_ms": 3_960, "transcribed": [heard]},
               {"which": "second", "step": "followUp", "question": RA_TEXT, "clip": RA_CLIP, "path": "recorded",
                "ended": "cap", "ran_ms": 9_004, "cap_ms": 9_000, "didnt_catch_played": 0, "next": "Last question"}]
    return {"owed": {"dimension": RA, "text": RA_TEXT}, "by": "recorded", "asked": [route, heard, route],
            "walk": {"windows": windows}, "clips": {RA: {"clipId": RA_CLIP}},
            "sent": {"dimension": RA, "skipped": True}}


def _take(person: str, how: str) -> dict:
    want = "It was Tuesday. yes"
    return {"person": person, "how": how, "t1": {"state": "idle", "pill": "Speak"},
            "before_pill": {"acquired": 0, "starts": []}, "after_pill": {"acquired": 1, "starts": [10.0]},
            "t2": {"state": "listening", "card": True, "wave": True, "clock": "0:00 · up to 1:00"},
            "continue_enabled_listening": False, "t3": {"state": "writing", "writing": "Writing it down…"},
            "t4": {"state": "heard", "value": want, "caret": len(want), "footer": "Heard you. Fix anything that’s wrong.",
                   "pill": "Add more"},
            "transcribed": [{"itemId": "g", "maxSeconds": 60, "status": 200, "text": "yes"}], "appended": "yes",
            "want": want, "sent": want, "quiet_to_stop_ms": 3_950 if how == "quiet" else None}


def _refused(person: str) -> dict:
    return {"person": person, "how": "refused", "before_pill": {"acquired": 0, "starts": []},
            "after_pill": {"acquired": 1, "starts": []},
            "t6": {"state": "typing-only", "footer": "The microphone is off, so it’s typing on this one."},
            "pill_after": 0}


def _follow_up_clips() -> dict:
    primary = ["problem.importance", "problem.current_solution_satisfaction", "solution.compatibility", RA,
               "solution.adoption_friction"]
    commercial = ["commercial.price", "commercial.buyer_payer_alignment", "commercial.commitment"]
    roles = {link: {"want": dims, "served": sorted(dims),
                    "clips": [{"itemId": d, "status": "DONE", "script": fake.follow_up_script(fake.rung(d)[3])}
                              for d in dims]} for link, dims in (("PRIMARY", primary), ("COMMERCIAL_B2B", commercial))}
    want = {"PRIMARY": sorted(primary), "COMMERCIAL_B2B": sorted(commercial)}
    return {"roles": roles, "full": True,
            "backfill": {"taken_out": 8, "stored": {f"{k}:{d}": {"ok": True} for k, v in want.items() for d in v},
                         "served_before": {"PRIMARY": [], "COMMERCIAL_B2B": []}, "served_after": copy.deepcopy(want),
                         "want": want,
                         "statuses": ["READY"], "ledger_rows_added": 0}}


def _media(type_: str, ms: int, *, face: str | None = None, intro: bool = False, muted: bool = False,
           current: float = 0.0, src: str = "") -> dict:
    """One media event as `harness/interviewer_screens.HEAR_JS` logs it."""
    return {"type": type_, "ms": ms, "face": face, "intro": intro, "muted": muted, "paused": type_ != "playing",
            "currentTime": current, "duration": 5.2, "src": src, "error": None}


def _hear_face() -> dict:
    """Spec 058 IM28: Chukwu tapped in the popup's carousel, her hello played in the card, the still back."""
    src = "http://localhost:5173/interviewer/faces/chukwu.mp4"
    return {"face": "CHUKWU", "hello": fake.hello_path("CHUKWU"), "sent": {"face": "CHUKWU"}, "ended": True,
            "before": {"picked": False, "glyph": True, "video": False, "videos": 0, "still": True,
                       "glyphs": {"JIA": True, "MARIEKE": True, "CHUKWU": True}},
            "events": [_media("play", 40, face="CHUKWU", src=src), _media("playing", 120, face="CHUKWU", src=src),
                       _media("pause", 5_330, face="CHUKWU", current=5.2, src=src),
                       _media("ended", 5_331, face="CHUKWU", current=5.2, src=src)],
            "polls": [], "elapsed_ms": 5_400,
            "after": {"picked": True, "still": True, "video": False, "videos": 0, "waited_ms": 100},
            "checked": ["CHUKWU"]}


def _hear_intro() -> dict:
    """Spec 058 IM29: *Hear Chukwu* on the Let-them-choose intro, the buttons enabled throughout."""
    src = "http://localhost:5173/interviewer/faces/chukwu.mp4"
    return {"face": "CHUKWU", "hello": fake.hello_path("CHUKWU"), "ended": True,
            "before": {"words": "Hear Chukwu · 5 s", "label": "Hear Chukwu", "still": True, "video": False,
                       "videos": 0, "buttons": {"choice-talk": True, "choice-write": True}},
            "events": [_media("playing", 90, intro=True, src=src), _media("ended", 5_300, intro=True, current=5.2,
                                                                          src=src)],
            "polls": [[True, True]] * 52, "elapsed_ms": 5_350,
            "after": {"still": True, "video": False, "videos": 0, "waited_ms": 0,
                      "buttons": {"choice-talk": True, "choice-write": True}}}


def good() -> dict:
    """A record as S-006's leg writes one: Chukwu at the first recording, Livia after the change, one fail-once
    retried (spec 058: Tito and Judy before)."""
    primary = [_clip("PRIMARY", "OPENING", script=fake.OPENING),
               _clip("PRIMARY", "PROBLEM", script="Translators wait months to be paid. I'll ask you 2 questions."),
               _clip("PRIMARY", "ITEM", "problem.recency"), _clip("PRIMARY", "ITEM", "problem.importance"),
               _clip("PRIMARY", "SOLUTION", script=SOLUTION),
               _clip("PRIMARY", "ITEM", "solution.relative_advantage"),
               _clip("PRIMARY", "ITEM_MORE", "solution.relative_advantage"),
               _clip("PRIMARY", "ITEM", "solution.compatibility", attempts=2),
               _clip("PRIMARY", "PILOT", script=fake.PILOT_ASK), _clip("PRIMARY", "THANKS", script="Thank you."),
               _clip("PRIMARY", "DIDNT_CATCH", script=fake.DIDNT_CATCH),
               _clip("PRIMARY", "IS_THAT_RIGHT", script=fake.IS_THAT_RIGHT)]
    commercial = [_clip("COMMERCIAL_B2B", "OPENING", script=fake.OPENING),
                  _clip("COMMERCIAL_B2B", "SOLUTION", script=SOLUTION),
                  _clip("COMMERCIAL_B2B", "COMMERCIAL", script="Last, the money side. 2 questions."),
                  _clip("COMMERCIAL_B2B", "ITEM", "commercial.ability_to_pay"),
                  _clip("COMMERCIAL_B2B", "ITEM", "commercial.purchase_friction"),
                  _clip("COMMERCIAL_B2B", "PILOT", script=fake.PILOT_ASK),
                  _clip("COMMERCIAL_B2B", "THANKS", script="Thank you."),
                  _clip("COMMERCIAL_B2B", "DIDNT_CATCH", script=fake.DIDNT_CATCH),
                  _clip("COMMERCIAL_B2B", "IS_THAT_RIGHT", script=fake.IS_THAT_RIGHT)]
    return {
        "entry": "05-paidly", "project_id": PROJECT,
        "ledger": [{"kind": "GRANT", "credits": 1500, "action": None, "price_version": None},
                   *_pair("INTERVIEWER_RECORDING"), *_pair("INTERVIEWER_CHANGE"),
                   _reading("INTERPRET", f"read-on-arrival:{AI_INVITATION}"), _reading("THEMES", "themes:on-return"),
                   {"kind": "PURCHASE", "credits": -800, "action": None, "price_version": None}],
        "screens": {"L1": "Who asks the questions. Keel records your interviewer once for this project. Lock and record "
                          "the interviewer",
                    "S1": "Chukwu asks your questions. Recording now, usually ready in about five minutes. 3 of 19 clips",
                    "S2": "Recorded today at 16:02. Change who asks · 400 AI credits",
                    "S3": "AI interviewer · Chukwu Text only Let them choose The interviewer is already recorded."},
        "wire_views": [{"face": {"code": "CHUKWU"}, "status": "READY", "progress": {"done": 19, "total": 19},
                        "changePrice": 400, "faces": [{"code": "LIVIA"}]},
                       {"interviewer": {"face": "CHUKWU", "status": "RECORDING"}, "revision": 40}],
        "recording": {"face": "LIVIA", "status": "READY", "clips": primary + commercial},
        "roles": {"PRIMARY": {"kind": "FULL", "parts": [
                      {"part": 1, "items": ["problem.recency", "problem.importance"]},
                      {"part": 2, "items": ["solution.relative_advantage", "solution.compatibility"]}]},
                  "COMMERCIAL_B2B": {"kind": "COMMERCIAL_LINK", "parts": [
                      {"part": 3, "items": ["commercial.ability_to_pay", "commercial.purchase_friction"]}]}},
        "idea": {"name": NAME, "how": HOW, "belief": BELIEF},
        "word": PITCH,
        "pilot": {"served": {"ai link": True, "try PRIMARY": True}, "answered": "YES", "before": 4, "after": 5},
        "range": {"part": {"status": 206, "content_range": "bytes 0-99/1000", "accept_ranges": "bytes", "length": 100},
                  "whole": {"status": 200, "accept_ranges": "bytes", "length": 1000},
                  "foreign": {"status": 404}},
        "dry_run": {"tryRun": True, "clips": 11,                             # 099: the dry run's reads store nothing
                    "writes": [{"method": "POST",
                                "url": f"http://localhost:18080/v2/projects/{PROJECT}/interviewer/classify"}],
                    "before": {"invitations": 21, "answered": 20, "pilot": 4, "ledger": 3},
                    "after": {"invitations": 21, "answered": 20, "pilot": 4, "ledger": 3}},
        "ai_answers": {"body": {"format": "AI_INTERVIEWER", "answers": [
                           {"itemId": "a", "how": "SPOKEN", "heard": "about three, maybe four"},
                           {"itemId": "b", "how": "TAPPED", "heard": ""},
                           {"itemId": "c", "how": "TYPED", "heard": "200"},
                           {"itemId": "d", "how": "TYPED"},                     # a value typed into the field
                           {"itemId": "e", "how": "RECORDED", "heard": "the second one"}]},
                       "register_row": {"formatUsed": "AI_INTERVIEWER"}},
        "change": {"face": "LIVIA", "face_before": "CHUKWU", "face_after": "LIVIA", "ready_face": "LIVIA",
                   "balance_before": 1100, "balance_after": 700, "trail": ["RECORDING", "RECORDING", "READY"]},
        "low_balance": {"status": 422, "balance": 100, "balance_after": 100, "ledger_rows_added": 0,
                        "face_before": "LIVIA", "face_after": "LIVIA",
                        "body": {"rule": "credits", "code": "INSUFFICIENT_CREDITS_FOR_INTERVIEWER", "required": 400,
                                 "available": 100, "remedy": fake.INSUFFICIENT_REMEDY.format(required=400,
                                                                                            available=100)}},
        "retry": {"status": "READY", "ledger_rows_added": 0, "clip": {"attempts": 2, "status": "DONE"}},
        "hold": {"holds": [{"question": "Did it happen?", "status": HELD, "lit": ["Yes"], "heard": "", "went_on": True,
                            "presses": [], "said": "yes"},
                           {"question": "Which fits?", "status": HELD, "lit": ["Agency A"], "heard": "", "went_on": True,
                            "presses": [], "said": "agency a"}],
                 "veto": {"question": "Which fits?", "said": "no", "reopened": True, "lit": ["Agency A"]},
                 "statuses": [{"status": "Listening…"}, {"status": HELD}], "saw_thats_my_answer": False,
                 # spec 049 (keel-web 073 FR-7): the pilot's spoken yes held with the ring, on by itself
                 "pilot": {"question": "Would you like to try it?", "status": HELD, "lit": ["Yes"], "ring": True,
                           "finish": True, "went_on": True, "presses": [], "done": True, "said": "yes"},
                 "finish_presses": 0},
        # spec 049 (keel-web 073 FR-1 / FR-2): the question read aloud, then the answer -- one read, nothing lit
        "hear_out": {"question": "Would Agency have made things better for you, or not?", "item": "r",
                     "first": "Would Agency have made things better for you", "second": "No difference",
                     "between_ms": 420, "reads_in_gap": 0,
                     "after_first": {"said": "Would Agency have made things better for you", "phase": "listening",
                                     "before": {"lit": [], "field": None, "preview": "", "heard": "", "status": ""},
                                     "after": {"lit": [], "field": None, "preview": "",
                                               "heard": "Would Agency have made things better for you hearing",
                                               "status": "Listening. Pause when you’re done."}, "still": True},
                     "reads": ["Would Agency have made things better for you No difference"],
                     "meant": "No difference", "sent": ["No difference"], "settled": "held",
                     "hearing": [{"said": "about three", "phase": "listening",
                                  "before": {"lit": [], "field": "", "preview": ""},
                                  "after": {"lit": [], "field": "", "preview": ""}, "still": True},
                                 {"said": "yes", "phase": "confirming",
                                  "before": {"lit": ["Agency C"], "field": None, "preview": ""},
                                  "after": {"lit": ["Agency C"], "field": None, "preview": ""}, "still": True}]},
        # spec 049 (keel-web 073 FR-6): a pick-two by taps waits for Save and next
        "taps": {"question": "Which two?", "item": "p", "want": ["Agency A", "Agency C"],
                 "one": {"shown": True, "enabled": False, "words": "Save and next", "ring": False, "phase": "listening",
                         "checked": ["Agency A"], "question_same": True},
                 "two": {"shown": True, "enabled": True, "words": "Save and next", "ring": False, "phase": "listening",
                         "checked": ["Agency A", "Agency C"]},
                 "third": {"tapped": "Agency B", "shown": True, "enabled": True, "ring": False, "phase": "listening",
                           "checked": ["Agency A", "Agency C"]},
                 "statuses_after_save": ["Got it."], "next": "Which fits?", "sent": ["Agency C", "Agency A"],
                 "sent_how": "TAPPED"},
        "confirm": {"turns": [{"question": "Which one?", "status": IS_THAT_RIGHT, "lit": ["Agency A"],
                               "yes": "Yes, that’s it", "went_on": True, "meant": ["Agency C"], "sent": ["Agency C"],
                               "said": "the first one, wait, actually the third", "answered": "yes",
                               # spec 050 (keel-web 074 FR-3): the yes held
                               "held": {"phase": "held", "ring": True, "unsure": ["false"], "status": HELD,
                                        "lit": ["Agency C"], "went_on": True}}]},
        "back": {"from": "Next?", "question": "Which fits?", "button": "‹ Back to question 4", "to": "Which fits?",
                 "lit_on_return": ["Agency B"], "said_first": "Agency B", "changed_to": "Agency A", "forward": "Next?",
                 "sent": ["Agency A"], "sent_how": "TAPPED"},
        "mic_test": {"before": {"mic_test": True, "start_enabled": False, "mic_heard": None},
                     "after": {"mic_test": True, "start_enabled": True, "mic_heard": "Heard: hello"}},
        "recorded": {"silence": {"status": 200, "heard": "", "unclear": True, "reason": "silence"},
                     "status": 201, "body": {"answers": [{"itemId": "a", "how": "RECORDED", "heard": "the first"}]},
                     "register_row": {"status": "ANSWERED", "formatUsed": "AI_INTERVIEWER"}},
        # spec 050 (keel-web 075 FR-1): a beat after the problem and the idea passages
        "beat": {"expected": ["PROBLEM", "SOLUTION"], "beat_ms": 2000,
                 "beats": [{"after_kind": kind, "ms": 2004, "statuses": ["Take a moment."], "pills": ["pause"],
                            "micOn": False, "question": False, "options": False, "buttons": [], "starts_in": 0,
                            "recordings_in": 0, "next": "speaking"} for kind in ("PROBLEM", "SOLUTION")]},
        # spec 050 (keel-web 074 FR-2): the story ended by its Save
        "story": {"by": "save", "question": "Tell me about it.", "said": "It was a Tuesday and the agency was late",
                  "status_before": "Take your time. Pause for a few seconds when you’re done, or tap Save.",
                  "save_before": {"shown": False}, "save_after_final": {"shown": True, "enabled": True},
                  "pressed": True, "final_to_held_ms": 410, "press_to_held_ms": 60,
                  "presses": [{"kind": "press", "testid": "ai-save"}], "classified": 0, "held_phase_seen": True,
                  "held": {"status": HELD, "heard": "It was a Tuesday and the agency was late heard", "went_on": True},
                  "next": "Which fits?", "sent": "It was a Tuesday and the agency was late"},
        # spec 051: the one follow-up (IM23-IM27)
        "follow_up": {"text": [_text_walk("Tom", "problem.importance", "Those two first."),
                               _text_walk("Lena", "problem.importance", None),
                               _text_walk("Marcus", None, None),
                               {"person": "Oliver", "asked": False, "owed": None, "route": {}, "screen": None,
                                "sent": None, "line": None}],
                      "ai": _ai_follow_up(), "try": {"status": 200, "owed": {"dimension": RA},
                                                     "body": {"dimension": RA, "text": RA_TEXT},
                                                     "clear": {"status": 204}}},
        "follow_up_windows": {"windows": _ai_follow_up()["walk"]["windows"], "full": True, "page_cap_ms": 120_000},
        "speak": {"Priya": _take("Priya", "quiet"), "Nadia": _take("Nadia", "done"), "Hana": _refused("Hana")},
        "follow_up_clips": _follow_up_clips(),
        # spec 058: tap to hear (IM28) and the respondent hears her (IM29)
        "hear_face": _hear_face(), "hear_intro": _hear_intro(),
        "arrivals": [{"invitationId": AI_INVITATION, "holds": [_reading("INTERPRET", f"read-on-arrival:{AI_INVITATION}")]},
                     {"invitationId": CHOICE_INVITATION,
                      "holds": [_reading("INTERPRET", f"read-on-arrival:{CHOICE_INVITATION}")]}],
    }


def _by_mark(record: dict) -> dict:
    return {c.mark: c for c in marks.score(record)}


def test_a_good_record_meets_every_mark():
    checks = _by_mark(good())
    assert all(c.measured and c.ok for c in checks.values()), {m: c.detail for m, c in checks.items() if not c.ok}
    card = marks.scorecard(good())
    assert (card["measured"], card["met"], card["unmeasured"]) == (29, 29, [])
    assert card["version"] == marks.INTERVIEWER_MARKS_VERSION == 6
    assert [m for m, _, _ in marks.MARKS] == [f"IM{i}" for i in range(1, 30)]


def test_the_story_ended_by_the_pause_meets_im22_with_nothing_pressed():
    record = good()
    record["story"] = {**record["story"], "by": "wait", "pressed": False, "presses": [], "press_to_held_ms": None,
                       "final_to_held_ms": 4100}
    assert _by_mark(record)["IM22"].ok, _by_mark(record)["IM22"].detail
    record["story"]["presses"] = [{"kind": "press", "testid": "ai-save"}]                # pressed on the wait path
    assert not _by_mark(record)["IM22"].ok


def test_the_short_form_measures_what_it_carries_and_nothing_else():
    record = {k: v for k, v in good().items()
              if k in ("entry", "project_id", "ledger", "recording", "roles", "idea", "word", "range")}
    record["ledger"] = [x for x in record["ledger"] if x.get("action") != "INTERVIEWER_CHANGE"]
    checks = _by_mark(record)
    assert {m for m, c in checks.items() if c.measured} == {"IM1", "IM3", "IM4", "IM5", "IM7"}
    assert all(checks[m].ok for m in ("IM1", "IM3", "IM4", "IM5", "IM7")), {m: checks[m].detail for m in checks}


def _seed(path: list, value) -> dict:
    record = copy.deepcopy(good())
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value(target[path[-1]]) if callable(value) else value
    return record


def _clips(fn):
    return lambda rec: {**rec, "clips": fn(rec["clips"])}


SEEDED = [
    ("IM1", ["ledger"], lambda rows: rows + _pair("INTERVIEWER_RECORDING")),            # charged twice
    ("IM1", ["ledger"], lambda rows: [r for r in rows if not (r["action"] == "INTERVIEWER_RECORDING"
                                                               and r["kind"] == "SPEND")]),  # half a pair
    ("IM1", ["ledger", 1, "price_version"], 8),                                          # the old charge table
    ("IM1", ["ledger", 1, "credits"], -35),                                              # the lock's job price
    ("IM1", ["ledger", 2, "actual_cost_micro_usd"], 1_430_000),                         # the vendor's bill passed on
    ("IM1", ["ledger", 1, "inference_job_id"], str(uuid.uuid4())),                       # held on a job
    ("IM2", ["screens", "L1"], "Who asks the questions · 400 credits"),                  # a price on Lock
    ("IM2", ["screens", "S1"], "Chukwu asks your questions. Recording now ($1.43)."),
    ("IM2", ["screens", "S3"], "AI interviewer · Chukwu · 400 credits"),
    ("IM2", ["screens", "S2"], "Recorded today at 16:02. Change who asks"),              # the one action missing
    ("IM2", ["screens"], lambda s: {k: v for k, v in s.items() if k != "S3"}),           # a screen not drawn
    ("IM2", ["wire_views"], lambda v: v + [{"interviewer": {"face": "CHUKWU", "creditsCharged": 400}}]),
    ("IM3", ["recording"], _clips(lambda c: [c[4]] + c[:4] + c[5:])),                    # the idea before the problem
    ("IM3", ["recording"], _clips(lambda c: c[:8] + [c[9], c[8]] + c[10:])),              # thanks before the pilot
    ("IM3", ["recording"], _clips(lambda c: c[:2] + [c[3], c[2]] + c[4:])),               # items out of order
    ("IM3", ["recording"], _clips(lambda c: c[:7] + c[8:])),                              # an item's clip missing
    ("IM3", ["recording"], _clips(lambda c: c[:5] + [c[6], c[5]] + c[7:])),               # a follow-up before its item
    ("IM3", ["recording"], _clips(lambda c: [x for x in c if not (x["kind"] == "DIDNT_CATCH"
                                                                    and x["role"] == "COMMERCIAL_B2B")])),
    ("IM3", ["recording"], _clips(lambda c: [x for x in c if not (x["kind"] == "IS_THAT_RIGHT"
                                                                    and x["role"] == "PRIMARY")])),  # 099's line missing
    ("IM3", ["recording"], _clips(lambda c: c + [_clip("PRIMARY", "IS_THAT_RIGHT")])),   # twice
    ("IM3", ["recording"], _clips(lambda c: [x for x in c if x["role"] == "PRIMARY"])),   # a role with no clips
    ("IM3", ["recording"], _clips(lambda c: [x for x in c if not (x["kind"] == "SOLUTION"
                                                                    and x["role"] == "COMMERCIAL_B2B")])),
    ("IM4", ["idea", "name"], "payment within seven days"),                              # another name spoken
    ("IM4", ["recording"], _clips(lambda c: [{**x, "script": x["script"].replace(
        "it would get translators paid on time", "it helps")} if x["kind"] == "SOLUTION" else x for x in c])),
    ("IM4", ["recording"], _clips(lambda c: [{**x, "script": "Now the idea. It is called invoice payout service."}
                                             if x["kind"] == "SOLUTION" else x for x in c])),
    ("IM4", ["recording"], _clips(lambda c: [x for x in c if x["kind"] != "SOLUTION"])),
    ("IM5", ["recording"], _clips(lambda c: [{**x, "script": f"Thank you. {PITCH}"}
                                             if x["kind"] == "THANKS" else x for x in c])),
    ("IM5", ["recording"], _clips(lambda c: [{**x, "script": "Thank you. I spent six years chasing agencies for "
                                                             "invoices."} if x["kind"] == "THANKS" else x for x in c])),
    ("IM5", ["word"], ""),                                                                # nothing to hold it to
    ("IM6", ["recording"], _clips(lambda c: [x for x in c if not (x["kind"] == "PILOT" and x["role"] == "PRIMARY")])),
    ("IM6", ["recording"], _clips(lambda c: [{**x, "script": "Would you like to hear about the pilot and the gift "
                                                             "card?"} if x["kind"] == "PILOT" else x for x in c])),
    ("IM6", ["pilot", "after"], 4),                                                       # the Yes counted nowhere
    ("IM6", ["pilot", "served", "ai link"], False),                                       # an AI interview with none
    ("IM6", ["pilot", "answered"], None),                                                 # skipped
    ("IM7", ["range", "part", "status"], 200),                                            # no Range support
    ("IM7", ["range", "part", "content_range"], None),
    ("IM7", ["range", "part", "length"], 1000),                                           # the whole clip sent
    ("IM7", ["range", "whole", "accept_ranges"], None),
    ("IM7", ["range", "foreign", "status"], 206),                                         # another project's clip served
    ("IM8", ["dry_run", "after", "invitations"], 22),                                     # the dry run made a link
    ("IM8", ["dry_run", "after", "ledger"], 5),                                           # or charged
    ("IM8", ["dry_run", "writes"], [{"method": "POST", "url": "/v2/i/x/interview/response"}]),
    ("IM8", ["dry_run", "tryRun"], None),
    ("IM8", ["dry_run", "writes"], lambda w: w + [{"method": "POST", "url": "/v2/i/x/interview/pilot"}]),
    ("IM9", ["ai_answers", "body", "format"], "TEXT"),
    ("IM9", ["ai_answers", "body", "answers", 0, "heard"], ""),                          # a spoken answer, nothing heard
    ("IM9", ["ai_answers", "body", "answers", 1], {"itemId": "b"}),                       # no how
    ("IM9", ["ai_answers", "body", "answers", 2, "heard"], "x" * 601),
    ("IM9", ["ai_answers", "body", "answers"], lambda a: [x for x in a if x["how"] != "SPOKEN"]),
    ("IM9", ["ai_answers", "register_row", "formatUsed"], None),
    ("IM9", ["ai_answers", "body", "answers", 4, "heard"], ""),                          # recorded, nothing heard
    ("IM9", ["ai_answers", "body", "answers", 4, "how"], "WHISPERED"),
    ("IM10", ["ledger"], lambda rows: [r for r in rows if r["action"] != "INTERVIEWER_CHANGE"]),  # changed for free
    ("IM10", ["ledger"], lambda rows: rows + _pair("INTERVIEWER_CHANGE")),                # charged twice
    ("IM10", ["change", "balance_after"], 1100),
    ("IM10", ["change", "trail"], ["READY"]),                                             # never re-recorded
    ("IM10", ["change", "ready_face"], "CHUKWU"),                                           # READY on the old face
    ("IM11", ["low_balance", "status"], 200),                                             # changed anyway
    ("IM11", ["low_balance", "body", "remedy"], "Not enough credits."),
    ("IM11", ["low_balance", "ledger_rows_added"], 2),
    ("IM11", ["low_balance", "face_after"], "CHUKWU"),
    ("IM11", ["low_balance", "body", "available"], 0),
    ("IM12", ["retry", "clip", "attempts"], 1),                                           # never failed, never retried
    ("IM12", ["retry", "ledger_rows_added"], 2),                                          # the retry paid again
    ("IM12", ["retry", "status"], "FAILED"),
    ("IM13", ["ledger"], lambda rows: rows + [_reading("INTERPRET", None)]),          # a reading the founder pressed
    ("IM13", ["arrivals", 0, "holds"], []),                                             # an answer never read
    ("IM13", ["arrivals", 1, "holds"], [_reading("INTERPRET", "read-on-arrival:" + str(uuid.uuid4()))]),
    ("IM13", ["arrivals", 0, "holds"], lambda h: h * 4),                                # read four times
    ("IM13", ["ledger"], lambda rows: rows + [_reading("THEMES", "brief:on-return")]),  # 104's retired reason
    ("IM14", ["hold", "saw_thats_my_answer"], True),                                     # the old button drawn
    ("IM14", ["hold", "holds", 0, "presses"], [{"kind": "press", "testid": "ai-next"}]), # a press in the hold
    ("IM14", ["hold", "holds", 1, "went_on"], False),                                    # held and stuck
    ("IM14", ["hold", "holds"], []),                                                     # never held
    ("IM14", ["hold", "veto", "reopened"], False),                                       # "no" ignored
    ("IM14", ["hold", "statuses"], [{"status": "Listening…"}]),                          # the words never drawn
    ("IM15", ["confirm", "turns"], []),                                                  # never asked
    ("IM15", ["confirm", "turns", 0, "sent"], ["Agency A"]),                             # the unsure pick sent
    ("IM15", ["confirm", "turns", 0, "yes"], None),                                      # no Yes chip
    ("IM15", ["confirm", "turns", 0, "status"], "Listening…"),
    ("IM16", ["back", "button"], None),                                                  # no Back drawn
    ("IM16", ["back", "lit_on_return"], []),                                             # reopened blank
    ("IM16", ["back", "sent"], ["Agency B"]),                                            # the first answer sent
    ("IM16", ["back", "sent_how"], "SPOKEN"),
    ("IM16", ["back", "forward"], "Which fits?"),                                        # stuck behind
    ("IM17", ["mic_test", "after", "mic_heard"], None),                                  # nothing heard drawn
    ("IM17", ["mic_test", "before", "start_enabled"], True),                             # Start before the test
    ("IM17", ["mic_test", "after", "start_enabled"], False),
    ("IM18", ["recorded", "silence", "reason"], "vendor"),                               # silence sent on
    ("IM18", ["recorded", "silence", "heard"], "you"),                                   # Whisper's ghost
    ("IM18", ["recorded", "status"], 422),                                               # RECORDED refused
    ("IM18", ["recorded", "body", "answers", 0, "how"], "SPOKEN"),
    ("IM18", ["recorded", "register_row", "status"], "OPENED"),
    # spec 049: the pilot's hold (IM14), hearing them out (IM19), taps that wait for Save (IM20)
    ("IM14", ["hold", "pilot", "ring"], False),                                          # no ring on the pilot
    ("IM14", ["hold", "finish_presses"], 1),                                             # Finish pressed
    ("IM14", ["hold", "pilot"], None),                                                   # the pilot never held
    ("IM19", ["hear_out", "after_first", "after", "lit"], ["Yes"]),                      # lit on the first final
    ("IM19", ["hear_out", "reads"], ["Would Agency have made things better for you", "No difference"]),  # two reads
    ("IM19", ["hear_out", "reads_in_gap"], 1),                                           # read before the gap ran
    ("IM19", ["hear_out", "after_first", "after", "status"], "Got that…"),
    ("IM19", ["hear_out", "between_ms"], 2_400),                                         # not within a second
    ("IM19", ["hear_out", "hearing", 0, "after", "field"], "3"),                         # filled while speaking
    ("IM19", ["hear_out", "sent"], ["It would have made things better"]),
    ("IM20", ["taps", "one", "enabled"], True),                                          # Save on at one tick
    ("IM20", ["taps", "one", "question_same"], False),                                   # went on at one tick
    ("IM20", ["taps", "one", "ring"], True),                                             # a tick held
    ("IM20", ["taps", "two", "enabled"], False),
    ("IM20", ["taps", "third", "checked"], ["Agency A", "Agency B", "Agency C"]),          # a third ticked
    ("IM20", ["taps", "sent_how"], "SPOKEN"),
    # spec 050: the held yes (IM15), the beat (IM21), the story's Save (IM22)
    ("IM15", ["confirm", "turns", 0, "held"], None),                                     # straight on, not held
    ("IM15", ["confirm", "turns", 0, "held", "unsure"], ["true"]),                       # held still unsure
    ("IM15", ["confirm", "turns", 0, "held", "ring"], False),
    ("IM21", ["beat", "beats"], lambda b: b[:1]),                                        # no beat after the idea
    ("IM21", ["beat", "beats"], lambda b: b + [{**b[0], "after_kind": "OPENING"}]),     # a beat after the opening
    ("IM21", ["beat", "beats", 0, "starts_in"], 1),                                      # a window opened in it
    ("IM21", ["beat", "beats", 0, "micOn"], True),                                       # the waveform drawn
    ("IM21", ["beat", "beats", 0, "statuses"], ["Take a moment.", "Listening. Say the one that fits, or tap it."]),
    ("IM21", ["beat", "beats", 1, "ms"], 200),                                           # the e2e fake's beat
    ("IM21", ["beat", "beats", 1, "pills"], ["listening"]),
    ("IM21", ["beat", "beats", 0, "question"], True),                                    # a question drawn in it
    ("IM21", ["beat", "beats", 0, "next"], "listening"),                                 # listened straight after
    ("IM21", ["beat", "expected"], []),                                                  # nothing to hold it to
    ("IM22", ["story", "status_before"], "Listening. Say the one that fits, or tap it."),
    ("IM22", ["story", "save_before", "shown"], True),                                   # Save before a word
    ("IM22", ["story", "save_after_final", "shown"], False),                             # no Save after one
    ("IM22", ["story", "final_to_held_ms"], 4_200),                                      # Save waited for the gap
    ("IM22", ["story", "classified"], 1),                                                # the story classified
    ("IM22", ["story", "held", "heard"], "It was a Tuesday"),                            # words lost
    ("IM22", ["story", "held_phase_seen"], False),
    ("IM22", ["story", "sent"], ""),                                                     # the story not sent
    # spec 051: the one follow-up
    ("IM23", ["follow_up", "text", 0, "route", "body", "dimension"], "problem.frequency"),  # the wrong rung asked
    ("IM23", ["follow_up", "text", 2, "route"], {"status": 200, "body": {"dimension": RA}}),  # asked of one owed none
    ("IM23", ["follow_up", "text", 0, "screen"], None),                                  # owed, never shown
    ("IM23", ["follow_up", "text", 0, "screen", "question"], "Something else?"),         # the screen's own words
    ("IM23", ["follow_up", "text", 0, "sent"], {"dimension": "commercial.price", "text": "x", "how": "TYPED"}),
    ("IM23", ["follow_up", "text", 3, "route"], {"status": 204}),                       # asked after a gate No
    ("IM23", ["follow_up", "ai", "walk", "windows", 1, "clip"], str(uuid.uuid4())),     # another rung's clip played
    ("IM23", ["follow_up", "ai", "asked", 2, "body", "text"], "You said it."),          # the second ask's text
    ("IM23", ["follow_up", "ai"], None),                                                 # the AI link never walked
    ("IM23", ["follow_up", "try", "clear", "status"], 200),                              # the twin asked one owed none
    ("IM23", ["follow_up", "text"], lambda t: [x for x in t if x.get("owed") is None]),  # nobody owed one
    ("IM24", ["follow_up", "text", 1, "sent"], {"dimension": "problem.importance", "text": "", "skipped": True}),
    ("IM24", ["follow_up", "text", 1, "sent"], {"dimension": "problem.importance", "skipped": False}),
    ("IM24", ["follow_up", "ai", "sent"], {"dimension": RA, "text": "yes", "how": "RECORDED", "skipped": False}),
    ("IM24", ["follow_up", "ai", "walk", "windows", 1, "didnt_catch_played"], 1),         # a didn't-catch loop
    ("IM24", ["follow_up", "ai", "walk", "windows", 1, "next"], "Question 9 of 9"),      # asked again, not the pilot
    ("IM25", ["follow_up_windows", "windows", 0, "quiet_to_stop_ms"], 1_900),            # 074's 2 s, not 4
    ("IM25", ["follow_up_windows", "windows", 0, "transcribed", 0, "sent", "maxSeconds"], 60),  # the story's minute
    ("IM25", ["follow_up_windows", "windows", 1, "ran_ms"], 4_100),                      # stopped long before the cap
    ("IM25", ["follow_up_windows", "windows", 1, "cap_ms"], 180_000),                    # past two minutes
    ("IM25", ["follow_up_windows", "page_cap_ms"], 60_000),
    ("IM25", ["follow_up_windows", "windows"], lambda w: w[:1]),                         # the silent window unseen
    ("IM25", ["follow_up_windows", "windows"], lambda w: w + [{"path": "browser", "ended": "save", "pressed": True,
                                                               "final_to_held_ms": 4_300, "presses": []}]),
    ("IM26", ["speak", "Priya", "before_pill", "acquired"], 1),                          # the mic asked on load
    ("IM26", ["speak", "Priya", "t4", "value"], "yes"),                                  # replaced, not appended
    ("IM26", ["speak", "Priya", "t4", "caret"], 0),                                      # the caret left behind
    ("IM26", ["speak", "Priya", "transcribed", 0, "maxSeconds"], 120),                   # the follow-up's window
    ("IM26", ["speak", "Priya", "sent"], "It was Tuesday."),                             # the append not sent
    ("IM26", ["speak", "Priya", "quiet_to_stop_ms"], 2_000),
    ("IM26", ["speak", "Nadia", "continue_enabled_listening"], True),                    # Continue on while listening
    ("IM26", ["speak", "Hana", "t6", "footer"], ""),                                     # T6 said nothing
    ("IM26", ["speak", "Hana", "after_pill", "starts"], [12.0]),                         # recorded on a refused mic
    ("IM26", ["speak"], lambda v: {k: x for k, x in v.items() if x["how"] != "refused"}),  # T6 never walked
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips"], lambda c: c[:-1]),        # a rung's clip missing
    ("IM27", ["follow_up_clips", "roles", "COMMERCIAL_B2B", "clips", 0, "script"], "One last thing."),
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips", 0, "status"], "FAILED"),
    ("IM27", ["follow_up_clips", "backfill", "ledger_rows_added"], 1),                   # the backfill charged
    ("IM27", ["follow_up_clips", "backfill", "statuses"], ["READY", "RECORDING"]),
    ("IM27", ["follow_up_clips", "backfill", "served_after", "PRIMARY"], []),           # never served again
    ("IM27", ["follow_up_clips", "backfill"], None),                                     # the full leg never seeded it
]

#: Spec 058 acceptance 1: the two evaluators' tables -- each fault fails its mark, alone.
_ENDED = 3
HEAR_FACE_FAULTS = [
    ("picked already", ["hear_face", "before", "picked"], True),
    ("no glyph on the card", ["hear_face", "before", "glyph"], False),
    ("an unpicked card with no glyph", ["hear_face", "before", "glyphs", "JIA"], False),
    ("a clip showing before the tap", ["hear_face", "before", "video"], True),
    ("never ended", ["hear_face", "events"], lambda ev: ev[:_ENDED]),
    ("never played", ["hear_face", "events"], lambda ev: [e for e in ev if e["type"] != "playing"]),
    ("muted", ["hear_face", "events", 1, "muted"], True),
    ("another clip", ["hear_face", "events", 1, "src"], "http://localhost:5173/interviewer/faces/livia.mp4"),
    ("over 8 s long", ["hear_face", "events", _ENDED, "duration"], 9.0),
    ("ended over 8 s after playing", ["hear_face", "events", _ENDED, "ms"], 8_200),
    ("stopped short of the end", ["hear_face", "events", _ENDED, "currentTime"], 2.0),
    ("a media error", ["hear_face", "events"], lambda ev: ev + [dict(ev[0], type="error", error=4)]),
    ("another card played", ["hear_face", "events"], lambda ev: ev + [dict(ev[1], face="JIA")]),
    ("the still never returned", ["hear_face", "after", "still"], False),
    ("the clip still showing", ["hear_face", "after", "video"], True),
    ("not picked by the tap", ["hear_face", "after", "picked"], False),
    ("two checked", ["hear_face", "checked"], ["LIVIA", "CHUKWU"]),
    ("another face posted", ["hear_face", "sent"], {"face": "LIVIA"}),
    ("the hello not served", ["hear_face", "hello"], None),
    ("a retired face", ["hear_face", "face"], "TITO"),
]
HEAR_INTRO_FAULTS = [
    ("other words", ["hear_intro", "before", "words"], "Listen"),
    ("another name", ["hear_intro", "before", "words"], "Hear Livia · 5 s"),
    ("no still before", ["hear_intro", "before", "still"], False),
    ("never ended", ["hear_intro", "events"], lambda ev: ev[:1]),
    ("muted", ["hear_intro", "events", 0, "muted"], True),
    ("played outside the intro", ["hear_intro", "events"], lambda ev: [dict(e, intro=False) for e in ev]),
    ("another clip", ["hear_intro", "events", 0, "src"], "http://localhost:5173/interviewer/faces/jia.mp4"),
    ("over 8 s long", ["hear_intro", "events", 1, "duration"], 8.5),
    ("the still never returned", ["hear_intro", "after", "still"], False),
    ("the clip still showing", ["hear_intro", "after", "video"], True),
    ("Talk disabled while playing", ["hear_intro", "polls"], lambda p: p[:10] + [[False, True]] + p[10:]),
    ("Write gone while playing", ["hear_intro", "polls"], lambda p: p[:10] + [[True, None]]),
    ("never polled", ["hear_intro", "polls"], []),
    ("Write disabled before", ["hear_intro", "before", "buttons", "choice-write"], False),
    ("Talk disabled after", ["hear_intro", "after", "buttons", "choice-talk"], False),
    ("only one button", ["hear_intro", "after", "buttons"], {"choice-talk": True}),
    ("the hello not served", ["hear_intro", "hello"], "/interviewer/faces/chukwu.webp"),
]
SEEDED += [("IM28", path, value) for _, path, value in HEAR_FACE_FAULTS]
SEEDED += [("IM29", path, value) for _, path, value in HEAR_INTRO_FAULTS]


@pytest.mark.parametrize("why,path,value", HEAR_FACE_FAULTS + HEAR_INTRO_FAULTS,
                         ids=[w for w, _, _ in HEAR_FACE_FAULTS + HEAR_INTRO_FAULTS])
def test_a_hear_fault_fails_its_mark_alone(why, path, value):
    checks = _by_mark(_seed(path, value))
    failed = {m for m, c in checks.items() if not c.ok}
    assert failed == {"IM28" if path[0] == "hear_face" else "IM29"}, (why, failed)


def test_the_hello_ended_by_the_still_alone_and_a_glyph_on_every_unpicked_card_meet_im28():
    record = good()
    record["hear_face"]["events"] = [e for e in record["hear_face"]["events"] if e["type"] in ("playing", "ended")]
    assert _by_mark(record)["IM28"].ok, _by_mark(record)["IM28"].detail
    record["hear_face"]["before"]["glyphs"] = {}
    assert not _by_mark(record)["IM28"].ok


@pytest.mark.parametrize("mark,path,value", SEEDED, ids=[f"{m}-{i}" for i, (m, _, _) in enumerate(SEEDED)])
def test_each_mark_fails_on_its_seeded_fault(mark, path, value):
    checks = _by_mark(_seed(path, value))
    assert checks[mark].measured and not checks[mark].ok, checks[mark].detail


def test_every_mark_has_a_seeded_fault():
    assert {m for m, _, _ in SEEDED} == {m for m, _, _ in marks.MARKS}


def test_a_record_missing_a_key_is_unmeasured_not_passed():
    record = good()
    del record["retry"]
    assert not _by_mark(record)["IM12"].measured and not _by_mark(record)["IM12"].ok


def test_the_price_word_finds_a_price_and_leaves_plain_words_alone():
    for priced in ("400 credits", "1 credit", "$2", "£1.50", "the price", "it costs", "charged"):
        assert marks.PRICE_WORD.search(priced), priced
    for plain in ("Recorded today at 16:02", "Lock and record the interviewer", "Keel records your interviewer once",
                  "Tap a face to pick. The voice goes with the face."):
        assert not marks.PRICE_WORD.search(plain), plain


# ------------------------------------------------------------------------------- the fake and charge v9, restated

def test_charge_v9_and_the_fixed_lines():
    assert (fake.PRICE_VERSION, fake.CREDITS, fake.COST_MICRO_USD, fake.CHANGE_PRICE) == (10, 400, 2_000_000, 400)
    assert fake.FACES == ("LIVIA", "JIA", "MARIEKE", "CHUKWU") and fake.PRESELECTED == "LIVIA"
    assert fake.RETIRED == ("JUDY", "JIN", "ANNA", "DAPHNE", "TITO") and not set(fake.RETIRED) & set(fake.FACES)
    assert fake.preview_path("CHUKWU") == "/interviewer/faces/chukwu.webp"
    assert fake.hello_path("LIVIA") == "/interviewer/faces/livia.mp4"
    assert fake.REFUSAL_STATUS == {"INTERVIEWER_NOT_READY": 409, "INTERVIEWER_NEEDS_CREDITS": 422,
                                   "FACE_UNKNOWN": 422, "INTERVIEWER_FAILED": 409,
                                   "INSUFFICIENT_CREDITS_FOR_INTERVIEWER": 422}
    assert fake.fake_seconds("one two three") == 1.0 and fake.fake_seconds(" ".join(["w"] * 23)) == 2.3 and fake.first_sentence("A b. C d.") == "A b."
    assert fake.normal("It’s  CALLED, ‘x’!") == "it's called 'x'"


def _cloud_text(rel: str) -> str:
    path = load_config(validate=False).keel_cloud / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel} (before spec 094)")
    return path.read_text(encoding="utf-8")


def test_the_faces_are_keel_clouds_own():
    text = _cloud_text("src/main/java/com/keeldiscovery/cloud/domain/interviewer/InterviewerFace.java")
    import re                                                             # noqa: PLC0415
    assert tuple(re.findall(r"^\s+([A-Z]+)\(\"", text, re.M)) == fake.FACES
    assert "PRESELECTED = LIVIA" in text


def test_the_kinds_are_keel_clouds_own():
    text = _cloud_text("src/main/java/com/keeldiscovery/cloud/domain/interviewer/ClipKind.java")
    import re                                                             # noqa: PLC0415
    body = text.split("enum ClipKind", 1)[1]
    # keel-cloud 101 closes the constants on ";" (a method follows them)
    assert tuple(re.findall(r"^\s+([A-Z_]+)[,;]?$", body, re.M)) == fake.KINDS


# ------------------------------------------------------------------------------------------ the new reads

class _Remote:
    is_remote = True


@pytest.mark.parametrize("call", [lambda c: ledger.recording(c, str(uuid.uuid4())),
                                  lambda c: ledger.pilot_opt_in(c, str(uuid.uuid4()), str(uuid.uuid4())),
                                  lambda c: ledger.stand_in_old_words(c, str(uuid.uuid4()), {str(uuid.uuid4()): "x"}),
                                  lambda c: ledger.stand_in_keels_door(c, str(uuid.uuid4()), "r", spec="044"),
                                  lambda c: ledger.stand_in_balance(c, str(uuid.uuid4()), "r", to=100, spec="044")])
def test_the_interviewer_reads_are_never_reached_on_the_remote_profile(call):
    with pytest.raises(ledger.LedgerUnavailable, match="remote"):
        call(_Remote())


def test_a_stand_in_names_its_spec():
    assert ledger.key_prefix("044") == "e2e-eval:044:" and ledger.KEY_PREFIX == ledger.key_prefix("043")
    assert "spec 044" in ledger.reason("044", "x") and "spec 043" in ledger.reason("043", "x")
    with pytest.raises(ledger.LedgerUnavailable):
        ledger.recording(type("Local", (), {"is_remote": False})(), "1; DROP TABLE project_content")


# --------------------------------------------------------------- spec 050: keel-cloud 101's framing lines, restated

def _composer() -> str:
    text = _cloud_text("src/main/java/com/keeldiscovery/cloud/application/interviewer/PassageComposer.java")
    if "COMMERCIAL_ROUTE" not in text:
        pytest.skip("keel-cloud predates spec 101 (no framing lines)")
    return text


@pytest.mark.parametrize("name", ["INTRODUCED", "HOW_TO_ANSWER", "FULL_ROUTE", "COMMERCIAL_ROUTE", "PROBLEM_CLOSE",
                                  "SOLUTION_CLOSE", "SOLUTION_OPENING", "COMMERCIAL_OPENING", "DIDNT_CATCH",
                                  "IS_THAT_RIGHT", "ONE_MORE"])
def test_the_framing_lines_are_the_composers_own(name):
    import re                                                             # noqa: PLC0415
    m = re.search(rf"\b{name} =\s*\"([^\"]*)\";", _composer())
    mine = fake.MORE if name == "ONE_MORE" else getattr(fake, name)
    assert m and m.group(1) == mine, (name, m and m.group(1), mine)


def test_the_composers_number_words_fallback_and_the_shape_of_its_sentences():
    import re                                                             # noqa: PLC0415
    text = _composer()
    words = re.search(r"NUMBER_WORDS = List\.of\(([^)]*)\)", text, re.S)
    assert words and tuple(re.findall(r'"(\w+)"', words.group(1))) == fake.NUMBER_WORDS
    assert f'"{fake.FOUNDER_FALLBACK}"' in text and '" has an idea for a problem you may know."' in text
    assert '"Then I\'ll ask you "' in text and '"about it"' in text and '"on whether it would help you"' in text


def test_the_fakes_framing_lines():
    assert fake.opening("Maya") == ("I'm Keel's interviewer. I'm an AI, not a person. Maya has an idea for a problem "
                                    "you may know. First the problem, then the idea, with a few questions about each. "
                                    "Say the answer that fits, or tap it.")
    assert fake.opening("  ", True) == ("I'm Keel's interviewer. I'm an AI, not a person. The founder has an idea for a "
                                        "problem you may know. First the idea, then a few questions on the money side. "
                                        "Say the answer that fits, or tap it.")
    assert fake.OPENING == fake.opening(None)
    assert fake.problem_passage("Payroll runs late.", 4) == ("Payroll runs late. That's the problem. Take a moment with "
                                                            "it. Then I'll ask you four questions about it.")
    assert fake.solution_close(1) == ("That's the idea. Take a moment. Then I'll ask you one question on whether it "
                                      "would help you.")
    assert fake.number(12) == "twelve" and fake.number(13) == "13"


def test_the_words_from_before_101_differ_and_keep_the_count():
    problem = fake.problem_passage("Payroll runs late.", 4)
    assert fake.before_101("PROBLEM", problem) == "Payroll runs late. I'll ask you four questions about that."
    solution = f"{fake.SOLUTION_OPENING} It is called X. {fake.solution_close(3)}"
    assert fake.before_101("SOLUTION", solution) == "Now the idea. It is called X. I'll ask you three questions about that."
    assert fake.before_101("OPENING", fake.opening("Maya")) == fake.OPENING_BEFORE_101 != fake.OPENING
