"""Spec 044: the AI interviewer marks (`evals/interviewer_marks.py`) over a record shaped like the leg's -- each met on a
good record and each failed by a fault seeded into it, so no mark is a pass that cannot fail; the fake and charge v9
restated (`harness/interviewer_fake.py`) against keel-cloud's own sources where the checkout carries them; the new
reads in `stack/ledger.py` refused on the remote profile; the leg's shape (the stand-ins reversed in a `finally`)."""

from __future__ import annotations

import copy
import inspect
import uuid
from pathlib import Path

import pytest

from evals import interviewer_marks as marks
from harness import interview_charge as charge
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
    # spec 088 (keel-cloud 156): a reading's and the themes' HOLD is written at 0 from price version 12 (was -35 here,
    # an invented figure; INTERPRET was 10 and THEMES 8 at version 11)
    return {"kind": "HOLD", "credits": -charge.READ_PRICES[action], "action": action, "price_version": fake.PRICE_VERSION, "project_id": PROJECT,
            "inference_job_id": str(uuid.uuid4()), "reason": reason}


def _clip(role: str, kind: str, item: str | None = None, script: str = "Words.", attempts: int = 1) -> dict:
    return {"id": str(uuid.uuid4()), "role": role, "kind": kind, "itemId": item, "script": script, "status": "DONE",
            "attempts": attempts, "durationSeconds": 0.1, "bytes": 1000}


SOLUTION = (f"Now the idea. It is called {NAME}. It claims to send an invoice and the service pays you within seven "
            f"days, and the benefit is it would get translators paid on time. I'll ask you 2 questions about that.")


RA = "solution.relative_advantage"
RA_TEXT = "You said a shorter reconciliation would have made no difference to your last delivery. What would have?"
RA_CLIP = str(uuid.uuid4())


IMP = "problem.importance"
CUR = "problem.current_solution_satisfaction"


def _text_walk(person: str, plan: list[tuple[str, str | None]], lines: dict | None = None,
               *, late: bool = False) -> dict:
    """One text walk's follow-ups as `evals/corpus_scenario._hold_the_follow_up` records them (spec 075): `plan` the
    `(rung, on)` pairs in the order asked -- `on` the item it hangs on, None the end's (both under *One more thing*,
    keel-web 126); `lines` what was typed on each (absent: a skip); `late` a held call before the end's (its 200 dropped)."""
    lines = lines or {}
    asked: list[dict] = [{"dimension": r, "text": f"Question on {r}.", "on": on} for r, on in plan]
    routes = [{"status": 204, "body": {}, "sent": {"answers": []}}]
    if late and plan:
        routes.append({"status": 200, "body": {"dimension": plan[0][0], "text": f"Question on {plan[0][0]}.",
                                               "itemId": "f", "spoken": "x"}, "sent": {"answers": []}})
    for i, a in enumerate(asked):
        routes.append({"status": 200, "body": {"dimension": a["dimension"], "text": a["text"], "itemId": "f",
                                               "spoken": "x"},
                       "sent": {"answers": [], **({"asked": [b["dimension"] for b in asked[:i]]} if i else {})}})
    screens = [{"rung": a["dimension"], "on": a["on"], "kicker": "One more thing",
                "question": a["text"], "did": "typed" if lines.get(a["dimension"]) else "skipped"} for a in asked]
    sent = [{"dimension": a["dimension"], "text": lines[a["dimension"]], "how": "TYPED", "skipped": False}
            for a in asked if lines.get(a["dimension"])] or None
    return {"person": person, "asked": True, "plan": asked, "routes": routes, "screens": screens, "sent": sent,
            "lines": {a["dimension"]: lines.get(a["dimension"]) for a in asked}}


def _ai_follow_up() -> dict:
    """S-006's AI link (spec 075): the one follow-up asked on the spot after Relative advantage -- 4 s after the last
    sound, Back to the item, asked again, then the silent window to the cap, skipped and not sent, the next item next."""
    route = {"route": "follow-up", "status": 200, "sent": {"answers": []},
             "body": {"dimension": RA, "text": RA_TEXT, "itemId": "fu", "clip": {"clipId": RA_CLIP}}}
    none = {"route": "follow-up", "status": 204, "sent": {"answers": [], "asked": [RA]}, "body": {}}
    heard = {"route": "transcribe", "status": 200, "sent": {"itemId": "fu", "maxSeconds": 120}, "body": {"text": "yes"}}
    windows = [{"which": "first", "step": "followUp", "question": RA_TEXT, "clip": RA_CLIP, "path": "recorded",
                "kicker": "One more thing", "where": "One more thing", "rung": RA, "on": RA,
                "ended": "quiet", "quiet_to_stop_ms": 3_960, "transcribed": [heard]},
               {"which": "second", "step": "followUp", "question": RA_TEXT, "clip": RA_CLIP, "path": "recorded",
                "kicker": "One more thing", "where": "One more thing", "rung": RA, "on": RA,
                "ended": "cap", "ran_ms": 9_004, "cap_ms": 9_000, "didnt_catch_played": 0, "next": "Question 6 of 6",
                "next_step": "item", "want_next": "item"}]
    met = {"index": 0, "rung": RA, "on": RA, "item": RA, "item_question": "Would it have helped?", "windows": windows,
           "back": {"to": "Would it have helped?", "step": "item"}}
    return {"plan": [{"dimension": RA, "text": RA_TEXT, "spoken": RA_TEXT, "on": RA}], "lines": {RA: "x"},
            "by": "sound", "asked": [route, heard, route, none], "walk": {"windows": windows, "follow_ups": [met]},
            "clips": {RA: {"clipId": RA_CLIP}}, "want_clips": {RA: RA_CLIP}, "sent": None, "sent_old": None}


def _take(person: str, how: str) -> dict:
    want = "It was Tuesday. yes"
    return {"person": person, "how": how, "t1": {"state": "idle", "pill": "Speak"},
            "before_pill": {"acquired": 0, "starts": [], "released": 1}, "after_pill": {"acquired": 1, "starts": [10.0]},
            # spec 075 FR-5 (keel-web 126 FR-4): asking before listening, the microphone kept, then let go on done
            "asking": {"state": "asking", "asking": "Allow the microphone…", "cancel": True, "wave": False,
                       "clock": None, "done": False},
            "asking_counts": {"acquired": 1, "starts": []}, "continue_enabled_asking": False,
            "counts": {"released": 1}, "released_at_done": 2,
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
    # v13 (spec 086 FR-5, keel-cloud 154): each rung's clip says its spoken line filled with the project's words, as
    # the leg records them (`said`)
    words = {"{job}": "counting the stock", "{solution_name}": "Countly", "{founder_item}": "matching deliveries",
             "{effort}": "scanning each invoice", "{step}": "installing the app"}
    said = {d: fake.spoken_filled(d, words) for d in primary + commercial}
    roles = {link: {"want": dims, "served": sorted(dims), "said": {d: said[d] for d in dims},
                    "clips": [{"itemId": d, "status": "DONE", "script": fake.follow_up_script(said[d])}
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
    """Spec 058 IM28: Saskia tapped in the popup's carousel, her hello played in the card, the still back."""
    src = "http://localhost:5173/interviewer/faces/saskia.mp4"
    return {"face": "SASKIA", "hello": fake.hello_path("SASKIA"), "sent": {"face": "SASKIA"}, "ended": True,
            "before": {"picked": False, "glyph": True, "video": False, "videos": 0, "still": True,
                       "glyphs": {"SASKIA": True}},
            "events": [_media("play", 40, face="SASKIA", src=src), _media("playing", 120, face="SASKIA", src=src),
                       _media("pause", 5_330, face="SASKIA", current=5.2, src=src),
                       _media("ended", 5_331, face="SASKIA", current=5.2, src=src)],
            "polls": [], "elapsed_ms": 5_400,
            "after": {"picked": True, "still": True, "video": False, "videos": 0, "waited_ms": 100},
            "checked": ["SASKIA"]}


def _hear_intro() -> dict:
    """Spec 058 IM29: *Hear Saskia* on the Let-them-choose intro, the buttons enabled throughout."""
    src = "http://localhost:5173/interviewer/faces/saskia.mp4"
    return {"face": "SASKIA", "hello": fake.hello_path("SASKIA"), "ended": True,
            "before": {"words": "Hear Saskia · 5 s", "label": "Hear Saskia", "still": True, "video": False,
                       "videos": 0, "buttons": {"choice-talk": True, "choice-write": True}},
            "events": [_media("playing", 90, intro=True, src=src), _media("ended", 5_300, intro=True, current=5.2,
                                                                          src=src)],
            "polls": [[True, True]] * 52, "elapsed_ms": 5_350,
            "after": {"still": True, "video": False, "videos": 0, "waited_ms": 0,
                      "buttons": {"choice-talk": True, "choice-write": True}}}


def _hear_band() -> dict:
    """Spec 059 IM30: *Hear Saskia · 5 s* on Sent's who-asks band after the recording, her hello in the band's circle."""
    src = "http://localhost:5173/interviewer/faces/saskia.mp4"
    return {"present": True, "face": "SASKIA", "hello": fake.hello_path("SASKIA"), "retired": False, "ended": True,
            "before": {"words": "Hear Saskia · 5 s", "label": None, "still": True, "video": False, "videos": 1,
                       "hearing": None},
            "hearing_while": True,
            "events": [_media("play", 30, src=src) | {"band": True}, _media("playing", 95, src=src) | {"band": True},
                       _media("ended", 5_310, current=5.2, src=src) | {"band": True}],
            "polls": [], "elapsed_ms": 5_360,
            "after": {"still": True, "video": False, "videos": 1, "waited_ms": 0, "hearing": None}}



def _story_chip() -> dict:
    """Spec 076 FR-5: the AI link's chip walk as `_chip_ends_it` records it -- one chip-only response, nothing else."""
    return {"walked": [{"question": "Do you run one or two sites?", "chip": None, "did": ["said 'yes'"]},
                       {"question": "In the last 4 weeks, did a delivery not match its invoice?", "chip": None,
                        "did": ["said 'yes'"]},
                       {"question": "Tell me about the last one.", "chip": "I can't recall one particular delivery",
                        "did": ["tap the story's chip"]}],
            "chip": "I can't recall one particular delivery", "want_chip": "I can't recall one particular delivery",
            "responses": [{"status": 201, "body": {"recency": True, "anchorChip": "CANT_RECALL", "answers": [],
                                                   "pilotOptIn": False, "format": "AI_INTERVIEWER"}}],
            "pilot_writes": 0, "follow_up_calls": [], "done": {"text": "Thank you", "tryRun": False},
            "mic_off": {"shown": True}, "rows": {}, "row_faults": []}

def good() -> dict:
    """A record as S-006's leg writes one: Saskia at the first recording, Daphne after the change, one fail-once
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
                    "S1": "Saskia asks your questions. Recording now, usually ready in about five minutes. 3 of 19 clips",
                    "S2": "Recorded today at 16:02. Change who asks · 400 AI credits",
                    "S3": "AI interviewer · Saskia Text only Let them choose The interviewer is already recorded."},
        "wire_views": [{"face": {"code": "SASKIA"}, "status": "READY", "progress": {"done": 19, "total": 19},
                        "changePrice": 400, "faces": [{"code": "DAPHNE"}]},
                       {"interviewer": {"face": "SASKIA", "status": "RECORDING"}, "revision": 40}],
        "recording": {"face": "DAPHNE", "status": "READY", "clips": primary + commercial},
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
                           {"itemId": "a", "how": "RECORDED", "heard": "about three, maybe four"},
                           {"itemId": "b", "how": "TAPPED", "heard": ""},
                           {"itemId": "c", "how": "TYPED", "heard": "200"},
                           {"itemId": "d", "how": "TYPED"},                     # a value typed into the field
                           {"itemId": "e", "how": "RECORDED", "heard": "the second one"}]},
                       "register_row": {"formatUsed": "AI_INTERVIEWER"}},
        "change": {"face": "DAPHNE", "face_before": "SASKIA", "face_after": "DAPHNE", "ready_face": "DAPHNE",
                   "balance_before": 1100, "balance_after": 700, "trail": ["RECORDING", "RECORDING", "READY"]},
        "low_balance": {"status": 422, "balance": 100, "balance_after": 100, "ledger_rows_added": 0,
                        "face_before": "DAPHNE", "face_after": "DAPHNE",
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
                                     "after": {"lit": [], "field": None, "preview": "", "heard": "Hearing you…",
                                               "status": "Recording your answer. Pause when you’re done."},
                                     "still": True},
                     "reads": ["Would Agency have made things better for you No difference"],
                     "meant": "No difference", "sent": ["No difference"], "settled": "held",
                     "hearing": [{"said": "about three", "phase": "listening",
                                  "before": {"lit": [], "field": "", "preview": ""},
                                  "after": {"lit": [], "field": "", "preview": ""}, "still": True},
                                 {"said": "yes", "phase": "confirming",
                                  "before": {"lit": ["Agency C"], "field": None, "preview": ""},
                                  "after": {"lit": ["Agency C"], "field": None, "preview": ""}, "still": True}]},
        # spec 049 (keel-web 073 FR-6); spec 089 FR-3 (keel-web 135 FR-2): one pick, *And one more?*, then the second
        "taps": {"question": "Which one?", "item": "p", "want": ["Agency A", "Agency C"],
                 "one": {"shown": False, "enabled": None, "words": None, "ring": False, "phase": "listening",
                         "checked": ["Agency A"], "question_same": True, "more_played": True, "more_clip": "m1"},
                 "two": {"shown": False, "enabled": None, "ring": False, "phase": "listening",
                         "checked": ["Agency A", "Agency C"], "tapped": "Agency C"},
                 "save_pressed": False, "statuses_after": ["Got it."], "next": "Which fits?",
                 "sent": ["Agency C", "Agency A"], "sent_how": "TAPPED"},
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
                            "micOn": False, "question": False, "options": False, "buttons": [],
                            "recordings_in": 0, "next": "speaking"} for kind in ("PROBLEM", "SOLUTION")]},
        # spec 050 (keel-web 074 FR-2): the story ended by its Save
        "story": {"by": "save", "question": "Tell me about it.", "said": "It was a Tuesday and the agency was late",
                  "status_before": "Take your time. Pause for a few seconds when you’re done, or tap Save.",
                  "save_before": {"shown": False}, "save_after_final": {"shown": True, "enabled": True},
                  "pressed": True, "final_to_held_ms": 410, "press_to_held_ms": 60,
                  "presses": [{"kind": "press", "testid": "ai-save"}], "classified": 0, "held_phase_seen": True,
                  "held": {"status": HELD, "heard": "It was a Tuesday and the agency was late heard", "went_on": True},
                  "next": "Which fits?", "sent": "It was a Tuesday and the agency was late"},
        # spec 076 FR-5 (IM22 v12): the story's chip on a second AI link ends it
        "story_chip": _story_chip(),
        # spec 051: the one follow-up (IM23-IM27)
        # spec 075: two on the spot (Tom), a skip (Lena), the end's after a held call (Wen), none owed (Marcus)
        "follow_up": {"text": [_text_walk("Tom", [(IMP, IMP), (CUR, CUR)], {IMP: "Those two first.", CUR: "A check."}),
                               _text_walk("Lena", [(IMP, IMP)]),
                               _text_walk("Marcus", []),
                               {"person": "Oliver", "asked": False, "plan": [], "routes": [], "screens": [],
                                "sent": None, "lines": {}},
                               _text_walk("Wen", [(RA, None)], {RA: "Fewer emails."}, late=True)],
                      "ai": _ai_follow_up(), "try": {"status": 200, "owed": {"dimension": RA},
                                                     "body": {"dimension": RA, "text": RA_TEXT},
                                                     "clear": {"status": 204},
                                                     "then": {"status": 204, "owed": None}}},
        "follow_up_windows": {"windows": _ai_follow_up()["walk"]["windows"], "full": True, "page_cap_ms": 120_000,
                              "rungs": [RA]},
        "speak": {"Priya": _take("Priya", "quiet"), "Nadia": _take("Nadia", "done"), "Hana": _refused("Hana")},
        "follow_up_clips": _follow_up_clips(),
        # spec 058: tap to hear (IM28) and the respondent hears her (IM29)
        "hear_face": _hear_face(), "hear_intro": _hear_intro(),
        # spec 059: the band hears her (IM30)
        "hear_band": _hear_band(),
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
    assert (card["measured"], card["met"], card["unmeasured"]) == (30, 30, [])
    assert card["version"] == marks.INTERVIEWER_MARKS_VERSION == 14      # spec 086 FR-5: IM27; 089 FR-3: IM20
    assert [m for m, _, _ in marks.MARKS] == [f"IM{i}" for i in range(1, 31)]


DEFAULT_THANKS = "Thank you, your answers have gone to Maya."


def _no_word(script=DEFAULT_THANKS) -> dict:
    record = good()
    record["word"] = ""
    record["recording"] = {**record["recording"], "clips": [{**c, "script": script} if c["kind"] == "THANKS" else c
                                                            for c in record["recording"]["clips"]]}
    return record


def test_im5_v8_no_word_written_and_every_thanks_the_default():
    """Spec 073 FR-2 (keel-web 113 FR-2): no founder writes a word, so IM5 holds none stored and every role's thanks
    clip the thank-you's default words (`PassageComposer.said` of `InterviewComposer.done`'s thanks)."""
    check = _by_mark(_no_word())["IM5"]
    assert check.measured and check.ok, check.detail
    assert check.detail["word"] is None and check.detail["thanks"] == 2
    assert _by_mark(_no_word("Thank you, your answers have gone to The founder."))["IM5"].ok


@pytest.mark.parametrize("script", [
    "Thank you.",                                                                      # not the default words
    DEFAULT_THANKS + " " + "I started this because I spent years watching good people lose whole evenings.",
    "Your answers have gone to Maya.",                                                 # the thanks cut
])
def test_im5_v8_a_thanks_that_is_not_the_default_fails(script):
    assert not _by_mark(_no_word(script))["IM5"].ok


def test_im5_v8_no_thanks_clip_at_all_fails():
    record = _no_word()
    record["recording"]["clips"] = [c for c in record["recording"]["clips"] if c["kind"] != "THANKS"]
    assert not _by_mark(record)["IM5"].ok


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
    ("IM2", ["screens", "S1"], "Saskia asks your questions. Recording now ($1.43)."),
    ("IM2", ["screens", "S3"], "AI interviewer · Saskia · 400 credits"),
    ("IM2", ["screens", "S2"], "Recorded today at 16:02. Change who asks"),              # the one action missing
    ("IM2", ["screens"], lambda s: {k: v for k, v in s.items() if k != "S3"}),           # a screen not drawn
    ("IM2", ["wire_views"], lambda v: v + [{"interviewer": {"face": "SASKIA", "creditsCharged": 400}}]),
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
    ("IM5", ["word"], ""),                                    # no word, and the thanks is not the default (v8)
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
    ("IM9", ["ai_answers", "body", "answers"], lambda a: [x for x in a if x["how"] != "RECORDED"]),
    ("IM9", ["ai_answers", "body", "answers", 0, "how"], "SPOKEN"),                     # v9: the retired recogniser's
    ("IM9", ["ai_answers", "register_row", "formatUsed"], None),
    ("IM9", ["ai_answers", "body", "answers", 4, "heard"], ""),                          # recorded, nothing heard
    ("IM9", ["ai_answers", "body", "answers", 4, "how"], "WHISPERED"),
    ("IM10", ["ledger"], lambda rows: [r for r in rows if r["action"] != "INTERVIEWER_CHANGE"]),  # changed for free
    ("IM10", ["ledger"], lambda rows: rows + _pair("INTERVIEWER_CHANGE")),                # charged twice
    ("IM10", ["change", "balance_after"], 1100),
    ("IM10", ["change", "trail"], ["READY"]),                                             # never re-recorded
    ("IM10", ["change", "ready_face"], "SASKIA"),                                           # READY on the old face
    ("IM11", ["low_balance", "status"], 200),                                             # changed anyway
    ("IM11", ["low_balance", "body", "remedy"], "Not enough credits."),
    ("IM11", ["low_balance", "ledger_rows_added"], 2),
    ("IM11", ["low_balance", "face_after"], "SASKIA"),
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
    ("IM20", ["taps", "one", "question_same"], False),                                   # went on at one tap
    ("IM20", ["taps", "one", "ring"], True),                                             # a tap held
    ("IM20", ["taps", "one", "more_played"], False),                                     # no And one more?
    ("IM20", ["taps", "one", "checked"], ["Agency A", "Agency C"]),                        # two marked at one tap
    ("IM20", ["taps", "next"], "Which one?"),                                            # never went on
    ("IM20", ["taps", "sent_how"], "SPOKEN"),
    # spec 050: the held yes (IM15), the beat (IM21), the story's Save (IM22)
    ("IM15", ["confirm", "turns", 0, "held"], None),                                     # straight on, not held
    ("IM15", ["confirm", "turns", 0, "held", "unsure"], ["true"]),                       # held still unsure
    ("IM15", ["confirm", "turns", 0, "held", "ring"], False),
    ("IM21", ["beat", "beats"], lambda b: b[:1]),                                        # no beat after the idea
    ("IM21", ["beat", "beats"], lambda b: b + [{**b[0], "after_kind": "OPENING"}]),     # a beat after the opening
    ("IM21", ["beat", "beats", 0, "recordings_in"], 1),                                  # a window opened in it
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
    # spec 076 FR-5 (IM22 v12): the story's chip on the AI link ends it -- answers sent with it, a follow-up asked, the
    # pilot written, a second response, the chip's words wrong, the person on a money line
    ("IM22", ["story_chip", "responses", 0, "body", "answers"], [{"itemId": "a", "optionIds": ["o"]}]),
    ("IM22", ["story_chip", "responses", 0, "body", "story"], "It was a Tuesday"),
    ("IM22", ["story_chip", "follow_up_calls"], [200]),
    ("IM22", ["story_chip", "pilot_writes"], 1),
    ("IM22", ["story_chip", "responses"], lambda r: r + [{"status": 201, "body": {}}]),
    ("IM22", ["story_chip", "chip"], "I'd rather not say"),
    ("IM22", ["story_chip", "row_faults"], [{"Someone": "commercial.price", "listed past part 1": {}}]),
    ("IM22", ["story_chip", "mic_off", "shown"], False),
    ("IM22", ["story", "sent"], ""),                                                     # the story not sent
    # spec 051 / 075: the follow-ups
    ("IM23", ["follow_up", "text", 0, "routes", 1, "body", "dimension"], "problem.frequency"),  # the wrong rung asked
    ("IM23", ["follow_up", "text", 2, "routes"], [{"status": 200, "body": {"dimension": RA}}]),  # asked of one owed none
    ("IM23", ["follow_up", "text", 0, "screens"], []),                                     # owed, never shown
    ("IM23", ["follow_up", "text", 0, "screens", 0, "question"], "Something else?"),       # the screen's own words
    ("IM23", ["follow_up", "text", 0, "sent"], [{"dimension": "commercial.price", "text": "x", "how": "TYPED"}]),
    ("IM23", ["follow_up", "text", 3, "routes"], [{"status": 204}]),                       # asked after a gate No
    ("IM23", ["follow_up", "text", 0, "screens", 1, "kicker"], "One last thing"),          # v11: the retired end's words
    ("IM23", ["follow_up", "text", 0, "screens", 1, "on"], None),                          # the second kept for the end
    ("IM23", ["follow_up", "text", 4, "screens", 0, "kicker"], "About that"),              # v11: the retired spot's words
    ("IM23", ["follow_up", "text", 0, "routes", 2, "sent"], {"answers": []}),              # the first rung not `asked`
    ("IM23", ["follow_up", "text", 0, "routes"],
     lambda r: r + [{"status": 204, "sent": {"answers": [], "asked": [IMP, CUR]}}]),      # a call once two were asked
    ("IM23", ["follow_up", "text", 0],
     lambda t: _text_walk("Tom", [(IMP, IMP), (CUR, CUR), (RA, RA)], {IMP: "a", CUR: "b", RA: "c"})),  # three asked
    ("IM23", ["follow_up", "ai", "walk", "windows", 1, "clip"], str(uuid.uuid4())),       # another rung's clip played
    ("IM23", ["follow_up", "ai", "walk", "follow_ups", 0, "windows", 1, "kicker"], "One last thing"),
    ("IM23", ["follow_up", "ai", "asked", 2, "body", "text"], "You said it."),            # the second ask's text
    ("IM23", ["follow_up", "ai", "asked", 2, "sent"], {"answers": [], "asked": [RA]}),     # asked again with it `asked`
    ("IM23", ["follow_up", "ai"], None),                                                   # the AI link never walked
    ("IM23", ["follow_up", "try", "clear", "status"], 200),                                # the twin asked one owed none
    ("IM23", ["follow_up", "try", "then", "status"], 200),                                 # asked again with it `asked`
    ("IM23", ["follow_up", "text"], lambda t: [x for x in t if not x.get("plan")]),        # nobody owed one
    ("IM24", ["follow_up", "text", 1, "sent"], [{"dimension": IMP, "text": "", "skipped": True}]),  # a skip sent
    ("IM24", ["follow_up", "text", 1, "screens", 0, "did"], "typed"),
    ("IM24", ["follow_up", "ai", "sent"], [{"dimension": RA, "text": "yes", "how": "RECORDED", "skipped": False}]),
    ("IM24", ["follow_up", "ai", "walk", "windows", 1, "didnt_catch_played"], 1),           # a didn't-catch loop
    ("IM24", ["follow_up", "ai", "walk", "windows", 1, "next_step"], "pilot"),              # the next item skipped
    ("IM24", ["follow_up", "ai", "walk", "windows", 1, "next_step"], None),                 # never went on
    ("IM25", ["follow_up_windows", "windows", 0, "quiet_to_stop_ms"], 1_900),            # 074's 2 s, not 4
    ("IM25", ["follow_up_windows", "windows", 0, "transcribed", 0, "sent", "maxSeconds"], 60),  # the story's minute
    ("IM25", ["follow_up_windows", "windows", 1, "ran_ms"], 4_100),                      # stopped long before the cap
    ("IM25", ["follow_up_windows", "windows", 1, "cap_ms"], 180_000),                    # past two minutes
    ("IM25", ["follow_up_windows", "page_cap_ms"], 60_000),
    ("IM25", ["follow_up_windows", "windows"], lambda w: w[:1]),                         # the silent window unseen
    ("IM25", ["follow_up_windows", "windows"], lambda w: w + [{"path": "browser", "ended": "save", "pressed": True,
                                                               "final_to_held_ms": 300, "presses": [
                                                                   {"testid": "ai-save"}]}]),  # v9: no browser path
    ("IM25", ["follow_up_windows", "windows"], lambda w: w + [{"path": "recorded", "ended": "save", "pressed": True,
                                                               "final_to_held_ms": 4_300, "presses": []}]),
    ("IM25", ["follow_up_windows", "windows", 0, "rung"], CUR),                           # a window of no planned rung
    ("IM26", ["speak", "Priya", "before_pill", "acquired"], 1),                          # the mic asked on load
    ("IM26", ["speak", "Priya", "t4", "value"], "yes"),                                  # replaced, not appended
    ("IM26", ["speak", "Priya", "t4", "caret"], 0),                                      # the caret left behind
    ("IM26", ["speak", "Priya", "transcribed", 0, "maxSeconds"], 120),                   # the follow-up's window
    ("IM26", ["speak", "Priya", "sent"], "It was Tuesday."),                             # the append not sent
    ("IM26", ["speak", "Priya", "quiet_to_stop_ms"], 2_000),
    ("IM26", ["speak", "Nadia", "continue_enabled_listening"], True),                    # Continue on while listening
    ("IM26", ["speak", "Hana", "t6", "footer"], ""),                                     # T6 said nothing
    # v11 (spec 075 FR-5, keel-web 126 FR-4): asking skipped, recording while asking, released by the take, kept on done
    ("IM26", ["speak", "Priya", "asking", "state"], "listening"),
    ("IM26", ["speak", "Priya", "asking", "asking"], None),
    ("IM26", ["speak", "Priya", "asking", "wave"], True),
    ("IM26", ["speak", "Priya", "asking_counts", "starts"], [9.0]),
    ("IM26", ["speak", "Nadia", "continue_enabled_asking"], True),
    ("IM26", ["speak", "Priya", "counts", "released"], 2),
    ("IM26", ["speak", "Nadia", "released_at_done"], 1),
    ("IM26", ["speak", "Nadia", "released_at_done"], None),
    ("IM26", ["speak", "Hana", "after_pill", "starts"], [12.0]),                         # recorded on a refused mic
    ("IM26", ["speak"], lambda v: {k: x for k, x in v.items() if x["how"] != "refused"}),  # T6 never walked
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips"], lambda c: c[:-1]),        # a rung's clip missing
    ("IM27", ["follow_up_clips", "roles", "COMMERCIAL_B2B", "clips", 0, "script"], "One last thing."),
    # v11 (keel-cloud 144 FR-2): a clip still in the retired lead-in
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips", 0, "script"],
     lambda c: c.replace("One more thing.", "One last thing.", 1)),
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips", 0, "status"], "FAILED"),
    # v13 (keel-cloud 154): a clip in the registry's bare words, the project's not filled in
    ("IM27", ["follow_up_clips", "roles", "PRIMARY", "clips", 0, "script"],
     fake.follow_up_script(fake.rung("problem.importance")[3])),
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
    ("an unpicked card with no glyph", ["hear_face", "before", "glyphs", "SASKIA"], False),
    ("a clip showing before the tap", ["hear_face", "before", "video"], True),
    ("never ended", ["hear_face", "events"], lambda ev: ev[:_ENDED]),
    ("never played", ["hear_face", "events"], lambda ev: [e for e in ev if e["type"] != "playing"]),
    ("muted", ["hear_face", "events", 1, "muted"], True),
    ("another clip", ["hear_face", "events", 1, "src"], "http://localhost:5173/interviewer/faces/daphne.mp4"),
    ("over 8 s long", ["hear_face", "events", _ENDED, "duration"], 9.0),
    ("ended over 8 s after playing", ["hear_face", "events", _ENDED, "ms"], 8_200),
    ("stopped short of the end", ["hear_face", "events", _ENDED, "currentTime"], 2.0),
    ("a media error", ["hear_face", "events"], lambda ev: ev + [dict(ev[0], type="error", error=4)]),
    ("another card played", ["hear_face", "events"], lambda ev: ev + [dict(ev[1], face="DAPHNE")]),
    ("the still never returned", ["hear_face", "after", "still"], False),
    ("the clip still showing", ["hear_face", "after", "video"], True),
    ("not picked by the tap", ["hear_face", "after", "picked"], False),
    ("two checked", ["hear_face", "checked"], ["DAPHNE", "SASKIA"]),
    ("another face posted", ["hear_face", "sent"], {"face": "DAPHNE"}),
    ("the hello not served", ["hear_face", "hello"], None),
    ("a retired face", ["hear_face", "face"], "CHUKWU"),
]
HEAR_INTRO_FAULTS = [
    ("other words", ["hear_intro", "before", "words"], "Listen"),
    ("another name", ["hear_intro", "before", "words"], "Hear Daphne · 5 s"),
    ("no still before", ["hear_intro", "before", "still"], False),
    ("never ended", ["hear_intro", "events"], lambda ev: ev[:1]),
    ("muted", ["hear_intro", "events", 0, "muted"], True),
    ("played outside the intro", ["hear_intro", "events"], lambda ev: [dict(e, intro=False) for e in ev]),
    ("another clip", ["hear_intro", "events", 0, "src"], "http://localhost:5173/interviewer/faces/daphne.mp4"),
    ("over 8 s long", ["hear_intro", "events", 1, "duration"], 8.5),
    ("the still never returned", ["hear_intro", "after", "still"], False),
    ("the clip still showing", ["hear_intro", "after", "video"], True),
    ("Talk disabled while playing", ["hear_intro", "polls"], lambda p: p[:10] + [[False, True]] + p[10:]),
    ("Write gone while playing", ["hear_intro", "polls"], lambda p: p[:10] + [[True, None]]),
    ("never polled", ["hear_intro", "polls"], []),
    ("Write disabled before", ["hear_intro", "before", "buttons", "choice-write"], False),
    ("Talk disabled after", ["hear_intro", "after", "buttons", "choice-talk"], False),
    ("only one button", ["hear_intro", "after", "buttons"], {"choice-talk": True}),
    ("the hello not served", ["hear_intro", "hello"], "/interviewer/faces/saskia.webp"),
]
SEEDED += [("IM28", path, value) for _, path, value in HEAR_FACE_FAULTS]
SEEDED += [("IM29", path, value) for _, path, value in HEAR_INTRO_FAULTS]
#: Spec 059 acceptance 1: IM30's table -- each fault fails IM30 alone.
HEAR_BAND_FAULTS = [
    ("no button on a current face", ["hear_band", "present"], False),
    ("a pronoun", ["hear_band", "before", "words"], "Hear her · 5 s"),
    ("another name", ["hear_band", "before", "words"], "Hear Daphne · 5 s"),
    ("no still before", ["hear_band", "before", "still"], False),
    ("a clip showing before the tap", ["hear_band", "before", "video"], True),
    ("never marked hearing", ["hear_band", "hearing_while"], False),
    ("never ended", ["hear_band", "events"], lambda ev: ev[:2]),
    ("never played", ["hear_band", "events"], lambda ev: [e for e in ev if e["type"] != "playing"]),
    ("muted", ["hear_band", "events", 1, "muted"], True),
    ("played outside the band", ["hear_band", "events"], lambda ev: [dict(e, band=False) for e in ev]),
    ("another clip", ["hear_band", "events", 1, "src"], "http://localhost:5173/interviewer/faces/daphne.mp4"),
    ("over 8 s long", ["hear_band", "events", 2, "duration"], 8.5),
    ("ended over 8 s after playing", ["hear_band", "events", 2, "ms"], 8_300),
    ("stopped short of the end", ["hear_band", "events", 2, "currentTime"], 1.0),
    ("a media error", ["hear_band", "events"], lambda ev: ev + [dict(ev[0], type="error", error=4)]),
    ("the still never returned", ["hear_band", "after", "still"], False),
    ("the clip still showing", ["hear_band", "after", "video"], True),
    ("still marked hearing", ["hear_band", "after", "hearing"], "true"),
    ("the hello not served", ["hear_band", "hello"], None),
]
SEEDED += [("IM30", path, value) for _, path, value in HEAR_BAND_FAULTS]


@pytest.mark.parametrize("why,path,value", HEAR_FACE_FAULTS + HEAR_INTRO_FAULTS + HEAR_BAND_FAULTS,
                         ids=[w for w, _, _ in HEAR_FACE_FAULTS + HEAR_INTRO_FAULTS + HEAR_BAND_FAULTS])
def test_a_hear_fault_fails_its_mark_alone(why, path, value):
    checks = _by_mark(_seed(path, value))
    failed = {m for m, c in checks.items() if not c.ok}
    assert failed == {{"hear_face": "IM28", "hear_intro": "IM29", "hear_band": "IM30"}[path[0]]}, (why, failed)


def test_a_retired_face_meets_im30_by_drawing_no_hear_button():
    """Spec 059 FR-2: absent for a retired face -- no journey can record one (keel-cloud 110 refuses it FACE_UNKNOWN),
    so the branch is this table's: no button and no hello meets IM30; a button drawn for it fails. Spec 083: 094's
    TITO (retired by 110) and 143's CHUKWU (a constant, served with helloUrl null) alike."""
    for face in ("TITO", "CHUKWU"):
        record = good()
        record["hear_band"] = {"present": False, "face": face, "hello": fake.served_hello(face), "retired": True,
                               "state": "READY"}
        assert _by_mark(record)["IM30"].ok, _by_mark(record)["IM30"].detail
        record["hear_band"]["present"] = True
        assert not _by_mark(record)["IM30"].ok


def test_the_w1_replay_is_retired_and_says_why():
    """Spec 059 FR-2: the leg's W1 replay reading retires with keel-web 088's *How it works*; no row of the marks
    read it, and the leg's step says why."""
    from evals import interviewer_leg                                     # noqa: PLC0415
    assert "How it works" in interviewer_leg.W1_REPLAY_RETIRED and "088" in interviewer_leg.W1_REPLAY_RETIRED
    source = Path(interviewer_leg.__file__).read_text(encoding="utf-8")
    assert "walkthrough_again" not in source and "W1_REPLAY_RETIRED" in source
    assert "IM30" in interviewer_leg.SHORT_FORM
    assert not any(key == "W1" for _, key, _ in marks.MARKS)


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
    assert (fake.PRICE_VERSION, fake.CREDITS, fake.COST_MICRO_USD, fake.CHANGE_PRICE) == (12, 400, 2_000_000, 400)
    # spec 083 (keel-cloud 143): the two studio faces, DAPHNE preselected; 110's four retired with 094's (less DAPHNE)
    assert fake.FACES == ("DAPHNE", "SASKIA") and fake.PRESELECTED == "DAPHNE"
    assert fake.FACE_NAMES == {"DAPHNE": "Daphne", "SASKIA": "Saskia"}
    assert fake.RETIRED == ("JUDY", "JIN", "ANNA", "TITO", "LIVIA", "JIA", "MARIEKE", "CHUKWU")
    assert not set(fake.RETIRED) & set(fake.FACES)
    assert fake.preview_path("SASKIA") == "/interviewer/faces/saskia.webp"
    assert fake.hello_path("DAPHNE") == "/interviewer/faces/daphne.mp4"
    # 143 FR-4: a recording that carries a retired face is served with helloUrl null; its still as before
    assert fake.served_hello("SASKIA") == "/interviewer/faces/saskia.mp4" and fake.served_hello("LIVIA") is None
    assert fake.preview_path("LIVIA") == "/interviewer/faces/livia.webp" and fake.HELLO_MAX_S == 8.0
    assert fake.REFUSAL_STATUS == {"INTERVIEWER_NOT_READY": 409, "INTERVIEWER_NEEDS_CREDITS": 422,
                                   "FACE_UNKNOWN": 422, "INTERVIEWER_FAILED": 409,
                                   "INSUFFICIENT_CREDITS_FOR_INTERVIEWER": 422}
    assert fake.fake_seconds("one two three") == 1.0 and fake.fake_seconds(" ".join(["w"] * 23)) == 2.3 and fake.first_sentence("A b. C d.") == "A b."
    assert fake.normal("It’s  CALLED, ‘x’!") == "it's called 'x'"


def test_the_legs_two_picks_read_the_fake():
    """Spec 083 FR-2: the first recording is the face that is not the preselected one (SASKIA, as CHUKWU was to LIVIA),
    the change goes to the preselected one; both from the fake, never a literal."""
    from evals import interviewer_leg                                     # noqa: PLC0415
    assert (interviewer_leg.FIRST_FACE, interviewer_leg.CHANGED_FACE) == ("SASKIA", "DAPHNE")
    assert interviewer_leg.CHANGED_FACE == fake.PRESELECTED and interviewer_leg.FIRST_FACE in fake.FACES
    source = Path(interviewer_leg.__file__).read_text(encoding="utf-8")
    for literal in ('"SASKIA"', '"DAPHNE"', '"Saskia', '"Daphne', '"LIVIA"', '"CHUKWU"', "the four faces"):
        assert literal not in source, literal


def _cloud_text(rel: str) -> str:
    path = load_config(validate=False).keel_cloud / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel} (before spec 094)")
    return path.read_text(encoding="utf-8")


def test_the_faces_are_keel_clouds_own():
    """Spec 083 FR-3: keel-cloud 143's enum lists every constant, offered or retired, each closing on its offered flag
    (`InterviewerFace(..., boolean offered)`): the fake's FACES are the constants whose flag is true, in the enum's order
    (`OFFERED`, the order served), and RETIRED_143 those whose flag is false -- matched on the flag, not on the first two."""
    text = _cloud_text("src/main/java/com/keeldiscovery/cloud/domain/interviewer/InterviewerFace.java")
    import re                                                             # noqa: PLC0415
    constants = re.findall(r"^\s+([A-Z]+)\(\"[^;]*?,\s*(true|false)\)[,;]", text, re.M | re.S)
    assert tuple(code for code, offered in constants if offered == "true") == fake.FACES, constants
    assert tuple(code for code, offered in constants if offered == "false") == fake.RETIRED_143, constants
    assert f"PRESELECTED = {fake.PRESELECTED};" in text
    for code in fake.FACES:
        assert f'{code}("{fake.FACE_NAMES[code]}"' in text, code
    for code in fake.RETIRED_110:
        assert not re.search(rf"^\s+{code}\(", text, re.M), code       # 110 removed them: no constant


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
    text = _composer()
    if name == "ONE_MORE" and re.search(r"\bONE_MORE =\s*com\.keeldiscovery\.cloud\.domain\.vectors\.ItemFrames\.ONE_MORE;",
                                        text):
        # keel-cloud 158 T013: the clip's words are `ItemFrames.ONE_MORE`, the screen's and the voice's one constant
        text = _cloud_text("src/main/java/com/keeldiscovery/cloud/domain/vectors/ItemFrames.java")
    m = re.search(rf"\b{name} =\s*\"([^\"]*)\";", text)
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
