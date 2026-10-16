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
    return [{"kind": "HOLD", "credits": -400, "action": action, "price_version": 9, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": None, "actual_cost_micro_usd": None},
            {"kind": "SPEND", "credits": 0, "action": action, "price_version": None, "project_id": PROJECT,
             "inference_job_id": None, "price_credits": 400, "actual_cost_micro_usd": 2_000_000}]


AI_INVITATION = str(uuid.uuid4())
CHOICE_INVITATION = str(uuid.uuid4())


def _reading(action: str, reason: str | None) -> dict:
    return {"kind": "HOLD", "credits": -35, "action": action, "price_version": 9, "project_id": PROJECT,
            "inference_job_id": str(uuid.uuid4()), "reason": reason}


def _clip(role: str, kind: str, item: str | None = None, script: str = "Words.", attempts: int = 1) -> dict:
    return {"id": str(uuid.uuid4()), "role": role, "kind": kind, "itemId": item, "script": script, "status": "DONE",
            "attempts": attempts, "durationSeconds": 0.1, "bytes": 1000}


SOLUTION = (f"Now the idea. It is called {NAME}. It claims to send an invoice and the service pays you within seven "
            f"days, and the benefit is it would get translators paid on time. I'll ask you 2 questions about that.")


def good() -> dict:
    """A record as S-006's leg writes one: Tito at the first recording, Judy after the change, one fail-once retried."""
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
                   _reading("INTERPRET", f"read-on-arrival:{AI_INVITATION}"), _reading("BRIEF", "brief:on-return"),
                   {"kind": "PURCHASE", "credits": -800, "action": None, "price_version": None}],
        "screens": {"L1": "Who asks the questions. Keel records your interviewer once for this project. Lock and record "
                          "the interviewer",
                    "S1": "Tito asks your questions. Recording now, usually ready in about five minutes. 3 of 19 clips",
                    "S2": "Recorded today at 16:02. Change who asks · 400 AI credits",
                    "S3": "AI interviewer · Tito Text only Let them choose The interviewer is already recorded."},
        "wire_views": [{"face": {"code": "TITO"}, "status": "READY", "progress": {"done": 19, "total": 19},
                        "changePrice": 400, "faces": [{"code": "JUDY"}]},
                       {"interviewer": {"face": "TITO", "status": "RECORDING"}, "revision": 40}],
        "recording": {"face": "JUDY", "status": "READY", "clips": primary + commercial},
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
        "change": {"face": "JUDY", "face_before": "TITO", "face_after": "JUDY", "ready_face": "JUDY",
                   "balance_before": 1100, "balance_after": 700, "trail": ["RECORDING", "RECORDING", "READY"]},
        "low_balance": {"status": 422, "balance": 100, "balance_after": 100, "ledger_rows_added": 0,
                        "face_before": "JUDY", "face_after": "JUDY",
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
                               "said": "the first one, wait, actually the third", "answered": "yes"}]},
        "back": {"from": "Next?", "question": "Which fits?", "button": "‹ Back to question 4", "to": "Which fits?",
                 "lit_on_return": ["Agency B"], "said_first": "Agency B", "changed_to": "Agency A", "forward": "Next?",
                 "sent": ["Agency A"], "sent_how": "TAPPED"},
        "mic_test": {"before": {"mic_test": True, "start_enabled": False, "mic_heard": None},
                     "after": {"mic_test": True, "start_enabled": True, "mic_heard": "Heard: hello"}},
        "recorded": {"silence": {"status": 200, "heard": "", "unclear": True, "reason": "silence"},
                     "status": 201, "body": {"answers": [{"itemId": "a", "how": "RECORDED", "heard": "the first"}]},
                     "register_row": {"status": "ANSWERED", "formatUsed": "AI_INTERVIEWER"}},
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
    assert (card["measured"], card["met"], card["unmeasured"]) == (20, 20, [])
    assert card["version"] == marks.INTERVIEWER_MARKS_VERSION == 3
    assert [m for m, _, _ in marks.MARKS] == [f"IM{i}" for i in range(1, 21)]


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
    ("IM2", ["screens", "S1"], "Tito asks your questions. Recording now ($1.43)."),
    ("IM2", ["screens", "S3"], "AI interviewer · Tito · 400 credits"),
    ("IM2", ["screens", "S2"], "Recorded today at 16:02. Change who asks"),              # the one action missing
    ("IM2", ["screens"], lambda s: {k: v for k, v in s.items() if k != "S3"}),           # a screen not drawn
    ("IM2", ["wire_views"], lambda v: v + [{"interviewer": {"face": "TITO", "creditsCharged": 400}}]),
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
    ("IM10", ["change", "ready_face"], "TITO"),                                           # READY on the old face
    ("IM11", ["low_balance", "status"], 200),                                             # changed anyway
    ("IM11", ["low_balance", "body", "remedy"], "Not enough credits."),
    ("IM11", ["low_balance", "ledger_rows_added"], 2),
    ("IM11", ["low_balance", "face_after"], "TITO"),
    ("IM11", ["low_balance", "body", "available"], 0),
    ("IM12", ["retry", "clip", "attempts"], 1),                                           # never failed, never retried
    ("IM12", ["retry", "ledger_rows_added"], 2),                                          # the retry paid again
    ("IM12", ["retry", "status"], "FAILED"),
    ("IM13", ["ledger"], lambda rows: rows + [_reading("INTERPRET", None)]),          # a reading the founder pressed
    ("IM13", ["arrivals", 0, "holds"], []),                                             # an answer never read
    ("IM13", ["arrivals", 1, "holds"], [_reading("INTERPRET", "read-on-arrival:" + str(uuid.uuid4()))]),
    ("IM13", ["arrivals", 0, "holds"], lambda h: h * 4),                                # read four times
    ("IM13", ["ledger"], lambda rows: rows + [_reading("BRIEF", "brief:after-batch")]), # 095's retired reason
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
]


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
    assert (fake.PRICE_VERSION, fake.CREDITS, fake.COST_MICRO_USD, fake.CHANGE_PRICE) == (9, 400, 2_000_000, 400)
    assert fake.FACES == ("JUDY", "JIN", "ANNA", "DAPHNE", "TITO") and fake.PRESELECTED == "JUDY"
    assert fake.preview_path("TITO") == "/interviewer/faces/tito.webp"
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
    assert "PRESELECTED = JUDY" in text


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
