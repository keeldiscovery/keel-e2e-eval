"""The AI interviewer marks (spec 044): keel-cloud spec 094's and keel-web 069's rules, held over one interviewer leg's
record -- deterministic, zero spend, the shape of `evals/contacts_marks.py` (one check a rule, all of them owed, nothing
named apart).

A **journey** ruler with its own version: the recording is code's (`PassageComposer` composes every script from the
lock; no model turn anywhere in 094), so `instructions/marks.py`'s `MARKS_VERSION` stays where it is (spec 044 FR-001).
The leg (`evals/interviewer_leg.py`) builds the record from what the wire answered, what keel-web drew, what
`credit_ledger` holds and the recording keel-cloud stored (`stack/ledger.py`); `score` reads only the record, so a unit
test can seed a bad one and watch the mark fail (`tests/test_interviewer_marks.py`).

A mark whose subject the record does not carry is **unmeasured** -- reported, never passed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from harness import interviewer_fake as fake

#: Bumped whenever a mark is born, retired, or reads its record differently. v2 (spec 048, keel-cloud 099 / keel-web 072,
#: contract 18): IM14-IM18 born (the hold, "Is that right?", the way back, Test your mic, RECORDED); IM3 reads one
#: IS_THAT_RIGHT a role beside DIDNT_CATCH; IM8 reads a classify / answer / transcribe call as no write; IM9 takes
#: RECORDED, with its words.
#: v3 (spec 049, keel-cloud 100 / keel-web 073, contract 18 unchanged): IM19 (hears them out) and IM20 (taps wait for
#: Save) born; IM14 reads the pilot ask's hold too (held with the ring, on by itself, *Finish* never pressed).
#: v4 (spec 050, keel-cloud 101 / keel-web 074 + 075, contract 18 unchanged): IM21 (a beat after the passages) and IM22
#: (the story's Save) born; IM15 reads the held yes (`data-phase` held, the ring, `data-unsure` "false").
#: v5 (spec 051, keel-cloud 103 / keel-web 076, contract 18 -> 19 on the interview side): IM23 (asked on the first rung
#: against), IM24 (skipped honoured), IM25 (two minutes, four seconds), IM26 (speak or type) and IM27 (the follow-up
#: clips) born; IM3 and IM6 read FOLLOW_UP as unspoken (it plays only when the walk finds its rung).
#: v5 kept (spec 055, keel-web 082 D35/D36, 2026-10-18): the gap split by window kind -- options 2.0 s
#: (`GAP_OPTION_MS`), free text 4.0 s (`GAP_FREE_MS`, `SILENCE_FREE_MS`); IM22 and IM25 measure free-text windows only
#: (the story, the follow-up), so they read the free gap and no mark reads its record differently.
#: v6 (spec 058, keel-cloud 110 / keel-web 087, contract 23): the four faces (LIVIA preselected where JUDY was); IM28
#: (tap to hear: a tap on an unpicked card picks it and her hello plays inside the card to its end, the still returns,
#: the picked face is posted) and IM29 (the respondent hears her: *Hear <name>* on the Let-them-choose intro, the
#: choice buttons enabled throughout) born.
#: v7 (spec 059, keel-web 088, contract 24): IM30 (the band's *Hear <name>*: on Sent after the recording, `persona-hear`
#: plays her hello inside the who-asks band to its end, 8 s or less, the still returns; absent for a retired face) born;
#: the leg's W1 replay reading retires with *How it works* (keel-web 088 FR-1) -- it was a leg step, never a row here.
INTERVIEWER_MARKS_VERSION = 7
#: The answer path's reads, which store nothing (keel-cloud 099 FR-1 / FR-4, the founder's routes of its T011): a dry
#: run that only asks them has written nothing.
READS = re.compile(r"/(interview|interviewer)/(classify|answer|transcribe|follow-up)$")
#: keel-web 072 FR-9's status words, restated where the marks read them (harness/interviewer_screens.py keeps the page's).
HELD = "Got it. Moving on… say no to change"
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"
#: keel-web 073 FR-3 / FR-6: the status through the quiet gap, and a Save's 500 ms advance.
HEARING = "Listening. Pause when you’re done."
ANSWERED = "Got it."
#: keel-web 073 FR-2's quiet gap: a second final said within a second of the first joins the same utterance.
WITHIN_MS = 1_000
#: keel-web 074 FR-2 / 075 FR-1's words, restated where the marks read them.
STORY = "Take your time. Pause for a few seconds when you’re done, or tap Save."
BEAT = "Take a moment."
BEAT_PILL = "pause"
#: A beat shorter than this share of its length (`BEAT_MS`, 2.0 s) is not the beat.
BEAT_SHARE = 0.9
#: keel-web 074's gap (`QUIET_MS`, 4.0 s), split by keel-web 082 (D36): the free-text gap (`QUIET_FREE_MS`, the story
#: and the follow-up) stays 4.0 s -- a Save that reads the story at once is held well inside it; the option gap
#: (`QUIET_OPTION_MS`) is 2.0 s and no mark measures it.
GAP_FREE_MS = 4_000
GAP_OPTION_MS = 2_000

#: keel-web 076 / keel-cloud 103's words and numbers, restated where the marks read them.
FOLLOW_UP_KICKER = "One last thing"
LAST_QUESTION = "Last question"
#: keel-web 082: the recorded path's silence on a free-text window (`SILENCE_FREE_MS`; options are 2.0 s).
SILENCE_FREE_MS = 4_000
WINDOW_TOLERANCE_MS = 500
FOLLOW_UP_CAP_MS = 120_000
STORY_CAP = "1:00"
SPEAK = "Speak"
ADD_MORE = "Add more"
HEARD_YOU = "Heard you. Fix anything that’s wrong."
MIC_OFF_TYPING = "The microphone is off, so it’s typing on this one."
WRITING_DOWN = "Writing it down…"

#: A price word on a screen that must carry none (decision 1: "no price shown").
PRICE_WORD = re.compile(r"\bcredits?\b|[$£€]\s?\d|\bprice[sd]?\b|\bcosts?\b|\bpaid\b|\bcharge[sd]?\b", re.I)
#: A key on the wire that would carry the recording's own price (only `changePrice` may).
PRICE_KEY = re.compile(r"price|credit|cost|charge", re.I)
ALLOWED_PRICE_KEYS = {"changePrice"}
#: S2's one priced action, the single place a number of credits is drawn (decision 3).
CHANGE_ACTION = f"Change who asks · {fake.CHANGE_PRICE} AI credits"
CONTENT_WORD = 4          # a word of at least this many letters counts toward a line's coverage
COVERAGE = 0.8            # the share of a line's content words the solution passage must say
SHINGLE = 6               # six words of the founder's word in a row, spoken, is the word spoken
#: keel-cloud 095 FR-E / 096: why a reading's or a brief's HOLD was written without a click -- a reading on arrival, the
#: brief on the founder's return (096; 095's `brief:after-batch` is retired), a lost race's retry. A founder's own POST
#: readings carries none.
#: Spec 052 (keel-cloud 104): the brief's `brief:on-return` left with the BRIEF job; its THEMES jobs hold `themes:on-return`.
READ_REASON = re.compile(r"^(read-on-arrival:[0-9a-f-]{36}|themes:on-return|retry:[23]:[0-9a-f-]{36})$")
#: The HOLD actions IM13 explains: a reading, and since keel-cloud 104 the themes job (the brief's was BRIEF).
READ_ACTIONS = ("INTERPRET", "THEMES")


@dataclass(frozen=True)
class Check:
    mark: str
    rule: str
    measured: bool
    ok: bool
    detail: Any = None


def _keys(value: Any, path: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            out.append(f"{path}{k}")
            out += _keys(v, f"{path}{k}.")
    elif isinstance(value, list):
        for v in value:
            out += _keys(v, path)
    return out


def _pairs(rows: list[dict], action: str, project_id: str) -> tuple[list[dict], list[dict]]:
    """Every HOLD / SPEND row of one action, and the faults in their shape (charge v9's pass-through pair)."""
    mine = [x for x in rows if x.get("action") == action]
    holds = [x for x in mine if x.get("kind") == "HOLD"]
    spends = [x for x in mine if x.get("kind") == "SPEND"]
    faults = [x for x in holds
              if int(x.get("credits") or 0) != -fake.CREDITS or x.get("price_version") != fake.PRICE_VERSION
              or x.get("inference_job_id") is not None or x.get("project_id") != project_id]
    faults += [x for x in spends
               if int(x.get("credits") or 0) != 0 or x.get("price_credits") != fake.CREDITS
               or x.get("actual_cost_micro_usd") != fake.COST_MICRO_USD or x.get("inference_job_id") is not None
               or x.get("project_id") != project_id]
    faults += [x for x in mine if x.get("kind") not in ("HOLD", "SPEND")]
    return mine, faults


def _coverage(line: str, script: str) -> float:
    want = [w for w in fake.normal(line).split() if len(w) >= CONTENT_WORD]
    have = set(fake.normal(script).split())
    return 1.0 if not want else sum(w in have for w in want) / len(want)


# ------------------------------------------------------------------------------------------------ the marks

def one_recording_pair(r: dict) -> tuple[bool, Any]:
    """IM1: the first recording is ONE `INTERVIEWER_RECORDING` HOLD of -400 (the price version of record, no job, this project) and
    its SPEND of 0 carrying 400 and 2,000,000 µUSD -- never a second for a retry, a change or a re-read."""
    mine, faults = _pairs(r["ledger"], fake.RECORDING, r["project_id"])
    kinds = sorted(x.get("kind") for x in mine)
    return kinds == ["HOLD", "SPEND"] and not faults, {"rows": mine, "faults": faults}


def no_price_shown(r: dict) -> tuple[bool, Any]:
    """IM2: no price word on L1, S1, S2 or S3 -- S2's one action, *Change who asks · 400 AI credits*, aside -- and no
    key on the founder's interviewer wire carries a price but `changePrice`."""
    screens = r["screens"]
    s2 = screens.get("S2") or ""
    priced = {name: PRICE_WORD.findall((text or "").replace(CHANGE_ACTION, "") if name == "S2" else (text or ""))
              for name, text in screens.items() if name in ("L1", "S1", "S2", "S3")}
    priced = {k: v for k, v in priced.items() if v}
    keys = sorted({k for body in r.get("wire_views") or [] for k in _keys(body)
                   if PRICE_KEY.search(k.rsplit(".", 1)[-1]) and k.rsplit(".", 1)[-1] not in ALLOWED_PRICE_KEYS})
    drawn = {"L1", "S1", "S2", "S3"} <= set(screens) and CHANGE_ACTION in s2
    return drawn and not priced and not keys, {"priced": priced, "keys": keys, "drawn": sorted(screens),
                                               "change action drawn": CHANGE_ACTION in s2}


def _expected_kinds(role: dict) -> list[tuple[str, str | None]]:
    """A role's spoken order, from what its link is served: the opening, each part's passage and its items in order,
    the pilot ask, thanks. A commercial link opens on the idea (094 FR-B: "its idea lines first" -- the SOLUTION
    passage with no items of its own), then the money side."""
    out: list[tuple[str, str | None]] = [("OPENING", None)]
    if role.get("kind") == "COMMERCIAL_LINK":
        out.append(("SOLUTION", None))
    for part in role["parts"]:
        out.append((fake.PASSAGE_OF_PART[int(part["part"])], None))
        out += [("ITEM", dim) for dim in part["items"]]
    return out + [("PILOT", None), ("THANKS", None)]


def spoken_order(r: dict) -> tuple[bool, Any]:
    """IM3: every role's clips in the spoken order -- OPENING, PROBLEM and part 1's items, SOLUTION and part 2's,
    COMMERCIAL and part 3's (a follow-up right after the item it hangs on), PILOT, THANKS -- each item once, as its
    link serves it; and one DIDNT_CATCH and (keel-cloud 099) one IS_THAT_RIGHT a role, neither in the order."""
    sets = fake.role_sets(r["recording"])
    out: dict = {}
    ok = bool(r["roles"]) and set(sets) == set(r["roles"])
    for name, role in r["roles"].items():
        clips = sets.get(name) or []
        said = []
        for c in fake.spoken(clips):
            if c.get("kind") == "ITEM_MORE":
                if not said or said[-1] != ("ITEM", c.get("itemId")):
                    said.append(("ITEM_MORE?", c.get("itemId")))
                continue
            said.append((c.get("kind"), c.get("itemId") if c.get("kind") == "ITEM" else None))
        want = _expected_kinds(role)
        catches = sum(c.get("kind") == "DIDNT_CATCH" for c in clips)
        unsure = sum(c.get("kind") == "IS_THAT_RIGHT" for c in clips)
        this = said == want and catches == 1 and unsure == 1
        ok = ok and this
        out[name] = {"ok": this, "said": said, "want": want, "didntCatch": catches, "isThatRight": unsure}
    return ok, out


def solution_three_facts(r: dict) -> tuple[bool, Any]:
    """IM4: the solution passage says the idea's **name**, what it **claims** (the first sentence of its how) and its
    **benefit** (the belief line) -- on every role that hears it."""
    idea = r["idea"]
    passages = [c for c in (r["recording"] or {}).get("clips") or [] if c.get("kind") == "SOLUTION"]
    name, claim = idea.get("name") or "", fake.first_sentence(idea.get("how") or "")
    belief = fake.benefit(idea.get("belief") or "")
    out = []
    for c in passages:
        script = c.get("script") or ""
        out.append({"role": c.get("role"), "name": bool(name) and fake.normal(name) in fake.normal(script),
                    "claim": round(_coverage(claim, script), 2), "belief": round(_coverage(belief, script), 2)})
    ok = bool(passages) and bool(claim) and bool(belief) and all(
        x["name"] and x["claim"] >= COVERAGE and x["belief"] >= COVERAGE for x in out)
    return ok, {"passages": out, "idea": {"name": name, "claim": claim, "belief": belief}}


def no_founders_word(r: dict) -> tuple[bool, Any]:
    """IM5: no clip says the founder's word (`DoneScreen.word.pitch`): not whole, not six words of it in a row."""
    pitch = fake.normal(r["word"])
    words = pitch.split()
    shingles = {" ".join(words[i:i + SHINGLE]) for i in range(max(1, len(words) - SHINGLE + 1))} if words else set()
    hits = [{"role": c.get("role"), "kind": c.get("kind")} for c in (r["recording"] or {}).get("clips") or []
            if pitch and (pitch in fake.normal(c.get("script")) or any(s in fake.normal(c.get("script"))
                                                                        for s in shingles))]
    return bool(pitch) and bool((r["recording"] or {}).get("clips")) and not hits, {"hits": hits, "words": len(words)}


def pilot_last_and_counted(r: dict) -> tuple[bool, Any]:
    """IM6: the pilot ask is in every role's set, once, the last line before thanks, in code's words; every AI interview
    served carries it; and the stranger's Yes on the AI link lands in the overview's pilot count."""
    sets = fake.role_sets(r["recording"])
    roles = {}
    for name, clips in sets.items():
        said = [c.get("kind") for c in fake.spoken(clips)]
        pilots = [c for c in clips if c.get("kind") == "PILOT"]
        roles[name] = (said[-2:] == ["PILOT", "THANKS"] and len(pilots) == 1
                       and fake.normal(pilots[0].get("script")) == fake.normal(fake.PILOT_ASK))
    p = r["pilot"]
    served = p.get("served") or {}
    counted = p.get("answered") == "YES" and p.get("after") == (p.get("before") or 0) + 1
    ok = bool(roles) and all(roles.values()) and bool(served) and all(served.values()) and counted
    return ok, {"roles": roles, "served": served, "count": {k: p.get(k) for k in ("answered", "before", "after")}}


def range_served(r: dict) -> tuple[bool, Any]:
    """IM7: a clip answers **206** to a Range request (`Content-Range` `bytes a-b/size`, `Accept-Ranges: bytes`, the
    asked bytes), 200 whole with `Accept-Ranges`, and **404** for a clip of another project on this link."""
    x = r["range"]
    part = x.get("part") or {}
    whole = x.get("whole") or {}
    m = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", part.get("content_range") or "")
    ok = (part.get("status") == 206 and m is not None and part.get("accept_ranges") == "bytes"
          and m is not None and int(m.group(2)) - int(m.group(1)) + 1 == part.get("length")
          and whole.get("status") == 200 and whole.get("accept_ranges") == "bytes"
          and (m is None or int(m.group(3)) == whole.get("length"))
          and (x.get("foreign") or {}).get("status") == 404)
    return ok, x


def dry_run_wrote_nothing(r: dict) -> tuple[bool, Any]:
    """IM8: *Try it yourself* is served (`tryRun`, the clips) and writes nothing -- no invitation, no response, no pilot,
    no ledger row, and the page posts nothing but the answer path's reads (classify / answer / transcribe store
    nothing, keel-cloud 099)."""
    x = r["dry_run"]
    writes = [w for w in x.get("writes") or [] if not READS.search((w.get("url") or "").split("?")[0])]
    ok = (x.get("tryRun") is True and x.get("clips", 0) > 0 and x.get("before") == x.get("after") and not writes)
    return ok, {**x, "writes that store": writes}


def heard_on_every_answer(r: dict) -> tuple[bool, Any]:
    """IM9: the AI link's `POST response` says `format` AI_INTERVIEWER and carries `how` on every answer and `heard`
    on every spoken one (at most 600 characters; spec 044 FR-003 "heard on every spoken answer" -- a value typed into
    a field carries none, DRIFT #89; keel-cloud 099: RECORDED is spoken too); the register's row then reads
    `formatUsed` AI_INTERVIEWER."""
    x = r["ai_answers"]
    body = x.get("body") or {}
    answers = body.get("answers") or []
    bad = [a.get("itemId") for a in answers
           if a.get("how") not in ("SPOKEN", "TAPPED", "TYPED", "RECORDED")
           or (a.get("how") in ("SPOKEN", "RECORDED") and not (a.get("heard") or "").strip())
           or len(a.get("heard") or "") > 600]
    spoken = [a for a in answers if a.get("how") == "SPOKEN"]
    ok = (body.get("format") == "AI_INTERVIEWER" and bool(answers) and bool(spoken) and not bad
          and (x.get("register_row") or {}).get("formatUsed") == "AI_INTERVIEWER")
    return ok, {"bad": bad, "answers": len(answers), "spoken": len(spoken), "format": body.get("format"),
                "formatUsed": (x.get("register_row") or {}).get("formatUsed")}


def the_change_pair(r: dict) -> tuple[bool, Any]:
    """IM10: changing who asks is ONE `INTERVIEWER_CHANGE` HOLD / SPEND pair of 400 at price_version 9, the balance
    400 lower, the line back to RECORDING and then READY on the new face."""
    x = r["change"]
    mine, faults = _pairs(r["ledger"], fake.CHANGE, r["project_id"])
    trail = x.get("trail") or []
    ok = (sorted(m.get("kind") for m in mine) == ["HOLD", "SPEND"] and not faults
          and x.get("balance_before") - x.get("balance_after") == fake.CREDITS
          and x.get("face_after") == x.get("face") and "RECORDING" in trail and trail[-1:] == ["READY"]
          and x.get("ready_face") == x.get("face"))
    return ok, {"rows": mine, "faults": faults, **x}


def refused_at_low_balance(r: dict) -> tuple[bool, Any]:
    """IM11: at a balance under 400 the change is refused **422 INSUFFICIENT_CREDITS_FOR_INTERVIEWER** with `required`
    400, `available` the balance and keel-cloud's sentence; nothing is charged and the face stays."""
    x = r["low_balance"]
    body = x.get("body") or {}
    want = fake.INSUFFICIENT_REMEDY.format(required=fake.CREDITS, available=x.get("balance"))
    ok = (x.get("status") == 422 and body.get("code") == fake.INSUFFICIENT and body.get("required") == fake.CREDITS
          and body.get("available") == x.get("balance") < fake.CREDITS and body.get("remedy") == want
          and x.get("ledger_rows_added") == 0 and x.get("face_after") == x.get("face_before")
          and x.get("balance_after") == x.get("balance"))
    return ok, {"want remedy": want, **x}


def the_retry_free(r: dict) -> tuple[bool, Any]:
    """IM12: the clip the fake failed once is retried by the recorder on its own (two attempts, DONE), the recording
    still READY, and the retry wrote no ledger row."""
    x = r["retry"]
    clip = x.get("clip") or {}
    ok = (clip.get("attempts") == 2 and clip.get("status") == "DONE" and x.get("status") == "READY"
          and x.get("ledger_rows_added") == 0)
    return ok, x


def read_on_arrival(r: dict) -> tuple[bool, Any]:
    """IM13 (keel-cloud 095 / 096): on Keel's door every answer with words is read on arrival -- its INTERPRET HOLD says
    `read-on-arrival:<invitationId>`, at most three attempts a reading (a retry says `retry:<n>:<parent>`) -- and
    every reading or themes HOLD the leg's ledger holds says why it was written (a themes job `themes:on-return`, keel-cloud
    104, where the brief's said `brief:on-return`): none was pressed by the founder, and none is written by a batch."""
    holds = [x for x in r["ledger"] if x.get("kind") == "HOLD" and x.get("action") in READ_ACTIONS]
    unexplained = [x for x in holds if not READ_REASON.match(x.get("reason") or "")]
    per = {}
    for a in r["arrivals"]:
        mine = [x for x in a.get("holds") or [] if x.get("action") == "INTERPRET"
                and x.get("reason") == f"read-on-arrival:{a['invitationId']}"]
        per[a["invitationId"]] = len(mine)
    ok = bool(per) and all(1 <= n <= 3 for n in per.values()) and not unexplained
    return ok, {"arrivals": per, "unexplained": unexplained, "holds": len(holds)}


def held_then_on(r: dict) -> tuple[bool, Any]:
    """IM14 (keel-web 072 FR-4 / FR-5): a confident spoken answer is **held** -- the status reads *Got it. Moving on…
    say no to change* with the pick lit -- and the next question comes by itself, nothing pressed in the hold; a word of
    protest in a hold reopens the question; and *That's my answer* is never in the DOM."""
    x = r["hold"]
    holds = x.get("holds") or []
    clean = [h for h in holds if HELD in (h.get("status") or "") and h.get("went_on") and not h.get("presses")
             and (h.get("lit") or h.get("heard"))]
    veto = x.get("veto") or {}
    # v3 (keel-web 073 FR-7): the pilot ask's spoken yes is held like any other -- the ring on Yes, *Finish* on the
    # sheet -- and goes on to the thanks by itself; *Finish* is never pressed on the spoken route
    pilot = x.get("pilot") if "pilot" in x else {"not walked": True}
    pilot_ok = pilot is None or "not walked" in pilot or (
        HELD in (pilot.get("status") or "") and pilot.get("ring") is True and pilot.get("went_on") is True
        and not pilot.get("presses") and pilot.get("done") is True and not x.get("finish_presses"))
    ok = (bool(clean) and len(clean) == len(holds) and x.get("saw_thats_my_answer") is False
          and (not veto or veto.get("reopened") is True) and pilot is not None and pilot_ok
          and any(HELD in (s.get("status") or "") for s in x.get("statuses") or []))
    return ok, {"holds": len(holds), "clean": len(clean), "veto": veto,
                "thats my answer seen": x.get("saw_thats_my_answer"), "statuses": len(x.get("statuses") or []),
                "pilot": pilot, "finish presses": x.get("finish_presses")}


def _held_yes(held: dict | None) -> bool:
    """keel-web 074 FR-3: the answer to *Is that right?* held -- `data-phase` held, *Got it. Moving on… say no to
    change*, the ring on the lit row, every lit row `data-unsure` "false"."""
    held = held or {}
    unsure = held.get("unsure") or []
    return (held.get("phase") == "held" and HELD in (held.get("status") or "") and held.get("ring") is True
            and bool(unsure) and all(u == "false" for u in unsure))


def asked_is_that_right(r: dict) -> tuple[bool, Any]:
    """IM15 (FR-2): an unsure read asks *Is that right? Say yes, or tell me the right one* with a pick lit and the
    *Yes, that's it* chip; the answer to it settles the question and is **held** (v4, keel-web 074 FR-3: `data-phase`
    held, the ring, the lit row `data-unsure` "false") before the next question; and the response carries what the
    stranger meant for that item."""
    x = r["confirm"]
    turns = x.get("turns") or []
    good = [c for c in turns if IS_THAT_RIGHT in (c.get("status") or "") and c.get("lit") and c.get("yes")
            and c.get("went_on") and c.get("sent") == c.get("meant") and _held_yes(c.get("held"))]
    return bool(turns) and len(good) == len(turns), {"turns": turns, "held": len(good)}


def went_back(r: dict) -> tuple[bool, Any]:
    """IM16 (FR-6): from the next question *‹ Back to question n* reopens the previous one with its answer lit; it
    is changed by a tap and the interview goes forward again; the one response carries the changed answer, TAPPED."""
    x = r["back"]
    ok = (bool(x.get("button")) and x.get("to") == x.get("question") and bool(x.get("lit_on_return"))
          and x.get("lit_on_return") != [x.get("changed_to")] and x.get("forward") == x.get("from")
          and x.get("sent") == [x.get("changed_to")] and x.get("sent_how") == "TAPPED")
    return ok, x


def mic_tested(r: dict) -> tuple[bool, Any]:
    """IM17 (FR-7): the AI link's intro asks *Test your mic* before Start; "hello" said reads *Heard: hello*, and
    *Start the interview* is enabled by it."""
    x = r["mic_test"]
    before, after = x.get("before") or {}, x.get("after") or {}
    ok = (before.get("mic_test") is True and before.get("start_enabled") is False
          and after.get("mic_heard") == "Heard: hello" and after.get("start_enabled") is True)
    return ok, {"before": {k: before.get(k) for k in ("mic_test", "start_enabled", "mic_heard")},
                "after": {k: after.get(k) for k in ("mic_test", "start_enabled", "mic_heard")}}


def recorded_accepted(r: dict) -> tuple[bool, Any]:
    """IM18 (keel-cloud 099 FR-4 / FR-7): a recording under the silence floor is read as silence on `answer` --
    `heard` empty, unclear, reason silence, nothing transcribed -- and a response whose spoken answers say `how`
    RECORDED is accepted and stored as answered on an AI link."""
    x = r["recorded"]
    silence = x.get("silence") or {}
    answers = (x.get("body") or {}).get("answers") or []
    ok = (silence.get("status") == 200 and silence.get("heard") == "" and silence.get("unclear") is True
          and silence.get("reason") == "silence"
          and x.get("status") in (200, 201) and any(a.get("how") == "RECORDED" for a in answers)
          and (x.get("register_row") or {}).get("status") == "ANSWERED"
          and (x.get("register_row") or {}).get("formatUsed") == "AI_INTERVIEWER")
    return ok, {"silence": silence, "status": x.get("status"), "register_row": x.get("register_row"),
                "recorded": sum(a.get("how") == "RECORDED" for a in answers)}


def _norm(text: str | None) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", (text or "").replace("’", "'").lower()))


def _quiet(sample: dict) -> bool:
    """One final said on a question's or a confirmation's window, looked at inside the quiet gap: nothing newly
    ticked, the field as it was, no preview drawn by the words (a miss's reason drawn before them may stay)."""
    before, after = sample.get("before") or {}, sample.get("after") or {}
    return (set(after.get("lit") or []) <= set(before.get("lit") or []) and after.get("field") == before.get("field")
            and after.get("preview") in ("", None, before.get("preview")))


def hears_them_out(r: dict) -> tuple[bool, Any]:
    """IM19 (keel-web 073 FR-1 / FR-2, keel-cloud 100): nothing is lit before the utterance ends -- after a final, inside
    the quiet gap, no row newly ticked, no field filled, no preview, on every spoken answer -- and a question read
    aloud, then answered within a second, is ONE read: the first final leaves nothing ticked and the status *Listening.
    Pause when you're done.*, no `classify` in the gap, then one `classify` whose `heard` is both finals joined; the
    response carries the answer meant."""
    x = r["hear_out"]
    hearing = x.get("hearing") or []
    loud = [s for s in hearing if not _quiet(s)]
    first = x.get("after_first") or {}
    after = first.get("after") or {}
    reads = x.get("reads") or []
    joined = _norm(f"{x.get('first')} {x.get('second')}")
    ok = (bool(hearing) and not loud and bool(first) and not after.get("lit") and not after.get("field")
          and not after.get("preview") and after.get("status") == HEARING and first.get("still") is True
          and (x.get("between_ms") or 10 ** 9) <= WITHIN_MS and x.get("reads_in_gap") == 0
          and len(reads) == 1 and _norm(reads[0]) == joined and x.get("sent") == [x.get("meant")])
    return ok, {"question": x.get("question"), "first": x.get("first"), "second": x.get("second"),
                "between_ms": x.get("between_ms"), "after first": after, "reads in gap": x.get("reads_in_gap"),
                "reads": reads, "settled": x.get("settled"), "sent": x.get("sent"), "meant": x.get("meant"),
                "finals looked at": len(hearing), "lit while hearing": loud}


def taps_wait_for_save(r: dict) -> tuple[bool, Any]:
    """IM20 (keel-web 073 FR-6): on a pick-two a tap only ticks -- one tick draws *Save and next* disabled and nothing
    goes on by itself for 1.5 s (the same question, `listening`, no ring); two ticks enable it; a third row tapped is
    ignored; Save shows *Got it.* and goes on; the response carries both picks, `how` TAPPED."""
    x = r["taps"]
    one, two, three = x.get("one") or {}, x.get("two") or {}, x.get("third") or {}
    want = sorted(x.get("want") or [])
    ok = (one.get("shown") is True and one.get("enabled") is False and one.get("question_same") is True
          and one.get("phase") == "listening" and one.get("ring") is False and len(one.get("checked") or []) == 1
          and two.get("shown") is True and two.get("enabled") is True and sorted(two.get("checked") or []) == want
          and two.get("ring") is False
          and (not three.get("tapped") or sorted(three.get("checked") or []) == want)
          and ANSWERED in (x.get("statuses_after_save") or []) and x.get("next") != x.get("question")
          and sorted(x.get("sent") or []) == want and x.get("sent_how") == "TAPPED")
    return ok, {k: x.get(k) for k in ("question", "want", "one", "two", "third", "statuses_after_save", "sent",
                                      "sent_how")}


def a_beat_after_the_passages(r: dict) -> tuple[bool, Any]:
    """IM21 (keel-web 075 FR-1, keel-cloud 101): after the problem and the idea passages -- and nowhere else -- a beat:
    `data-phase` beat for its 2 s, the status *Take a moment.* alone, the pill *pause*, no waveform, no question, no
    options, no button on the sheet, no recogniser started and no recording begun inside it, then the next clip."""
    x = r["beat"]
    beats = x.get("beats") or []
    expected = x.get("expected") or []
    least = BEAT_SHARE * float(x.get("beat_ms") or 0)
    bad = [b for b in beats if not (
        b.get("statuses") == [BEAT] and set(b.get("pills") or []) == {BEAT_PILL} and b.get("micOn") is False
        and b.get("question") is False and b.get("options") is False and not b.get("buttons")
        and b.get("starts_in") == 0 and b.get("recordings_in") == 0
        and b.get("ms") is not None and b.get("ms") >= least and b.get("next") == "speaking")]
    after = [b.get("after_kind") for b in beats]
    ok = bool(expected) and after == expected and not bad and least > 0
    return ok, {"expected after": expected, "after": after, "ms": [b.get("ms") for b in beats],
                "off": [{k: b.get(k) for k in ("after_kind", "ms", "statuses", "pills", "micOn", "question",
                                               "options", "buttons", "starts_in", "recordings_in", "next")}
                        for b in bad]}


def the_storys_save(r: dict) -> tuple[bool, Any]:
    """IM22 (keel-web 074 FR-2): the story's window says *Take your time. Pause for a few seconds when you're done, or
    tap Save.*; *Save and next* is absent until a final is heard, then drawn and enabled; the story ends by the pause
    with nothing pressed (S-005) or by Save, read at once -- held inside the gap (S-006); held either way with the
    words heard, never classified, then on; and the response carries the story."""
    x = r["story"]
    before, after, held = x.get("save_before") or {}, x.get("save_after_final") or {}, x.get("held") or {}
    by = x.get("by")
    ended = (by == "wait" and not x.get("pressed") and not x.get("presses")) or (
        by == "save" and x.get("pressed") is True and x.get("press_to_held_ms") is not None
        and x.get("final_to_held_ms") is not None and x.get("final_to_held_ms") < GAP_FREE_MS
        and [p.get("testid") for p in x.get("presses") or []] == ["ai-save"])
    said = _norm(x.get("said"))
    ok = (x.get("status_before") == STORY and before.get("shown") is False and after.get("shown") is True
          and after.get("enabled") is True and ended and x.get("held_phase_seen") is True
          and HELD in (held.get("status") or "") and bool(said) and said in _norm(held.get("heard"))
          and held.get("went_on") is True and x.get("classified") == 0 and x.get("next") != x.get("question")
          and _norm(x.get("sent")) == said)
    return ok, {k: x.get(k) for k in ("by", "status_before", "save_before", "save_after_final", "pressed",
                                      "final_to_held_ms", "press_to_held_ms", "presses", "classified", "sent")} | {
        "held": {k: held.get(k) for k in ("status", "heard", "went_on")}}


def _text_asked_right(t: dict) -> bool:
    """One text walk's follow-up as IM23 holds it: the route 200 on the harness's rung with its text, the screen
    showing that text under *One last thing*, the response naming that rung -- or, owed nothing, 204, no screen, no
    `followUp`; and a walk that never reached the route (a gate No) asked nothing."""
    owed, route, screen, sent = t.get("owed"), t.get("route") or {}, t.get("screen"), t.get("sent")
    if not t.get("asked"):
        return not route and not screen and sent is None
    if not owed:
        return route.get("status") == 204 and not screen and sent is None
    body = route.get("body") or {}
    return (route.get("status") == 200 and body.get("dimension") == owed.get("dimension")
            and body.get("text") == owed.get("text") and bool(screen) and screen.get("question") == body.get("text")
            and screen.get("kicker") == FOLLOW_UP_KICKER and (sent or {}).get("dimension") == owed.get("dimension"))


def _ai_asked_right(ai: dict) -> bool:
    """The AI link's follow-up as IM23 holds it: every ask of the route on the harness's rung with its text and the
    rung's clip, every window opened on that clip with that text (`followUp` step), the response naming the rung."""
    owed = ai.get("owed") or {}
    # keel-cloud 118: the rung's #also clip where the owed stem is one (the leg names it as `want_clip`)
    want_clip = ai.get("want_clip") or ((ai.get("clips") or {}).get(owed.get("dimension")) or {}).get("clipId")
    routes = [a for a in ai.get("asked") or [] if a.get("route") == "follow-up"]
    windows = (ai.get("walk") or {}).get("windows") or []
    return (bool(owed) and bool(want_clip) and bool(routes) and bool(windows)
            and all(a.get("status") == 200 and (a.get("body") or {}).get("dimension") == owed.get("dimension")
                    and (a.get("body") or {}).get("text") == owed.get("text")
                    and ((a.get("body") or {}).get("clip") or {}).get("clipId") == want_clip for a in routes)
            and all(w.get("clip") == want_clip and w.get("question") == owed.get("text") and w.get("step") == "followUp"
                    for w in windows)
            and (ai.get("sent") or {}).get("dimension") == owed.get("dimension"))


def asked_on_the_first_rung(r: dict) -> tuple[bool, Any]:
    """IM23 (keel-cloud 103, design §2 / §5): the one follow-up is asked on exactly the first rung against -- the
    harness's own walk (`first_rung`, the LADDER copy) -- on every text walk (the route, the screen, the response), on
    the AI link (the route's rung and text, the rung's FOLLOW_UP clip into every window) and on Try it yourself's twin
    where walked; none where nothing is owed, and none asked after a gate No."""
    x = r["follow_up"]
    text = x.get("text") or []
    bad = [t.get("person") for t in text if not _text_asked_right(t)]
    ai = x.get("ai")
    tried = x.get("try")
    try_ok = tried is None or ((tried.get("status") == 200 and (tried.get("body") or {}).get("dimension")
                                == (tried.get("owed") or {}).get("dimension")
                                and (tried.get("clear") or {}).get("status") == 204))
    owed = [t for t in text if t.get("asked") and t.get("owed")]
    clear = [t for t in text if t.get("asked") and not t.get("owed")]
    ok = bool(owed) and bool(clear) and not bad and ai is not None and _ai_asked_right(ai) and try_ok
    return ok, {"text walks": len(text), "owed": len(owed), "owed nothing": len(clear), "wrong": bad,
                "rungs": sorted({t["owed"]["dimension"] for t in owed}),
                "ai": None if ai is None else {"owed": (ai.get("owed") or {}).get("dimension"),
                                               "ok": _ai_asked_right(ai), "sent": ai.get("sent")},
                "try": tried and {"status": tried.get("status"), "clear": (tried.get("clear") or {}).get("status")}}


def skipped_honoured(r: dict) -> tuple[bool, Any]:
    """IM24 (keel-web 076, keel-cloud 103): a skip -- *Skip this one* pressed on a text link, or the AI interviewer's
    window left silent to its cap -- posts `{dimension, skipped: true}` with no text, and the pilot ask follows (the AI
    link: no didn't-catch, *Last question* next)."""
    x = r["follow_up"]
    pressed = [t for t in x.get("text") or [] if t.get("asked") and t.get("owed") and not t.get("line")]
    good = [t for t in pressed if t.get("sent") == {"dimension": t["owed"]["dimension"], "skipped": True}
            and (t.get("screen") or {}).get("did") == "skipped"]
    silent = []
    ai = x.get("ai") or {}
    for w in (ai.get("walk") or {}).get("windows") or []:
        if w.get("ended") == "cap":
            silent.append({"ok": ai.get("sent") == {"dimension": (ai.get("owed") or {}).get("dimension"),
                                                    "skipped": True}
                           and w.get("didnt_catch_played") == 0 and w.get("next") == LAST_QUESTION, **w})
    ok = bool(pressed or silent) and len(good) == len(pressed) and all(s["ok"] for s in silent)
    return ok, {"pressed": [t.get("person") for t in pressed], "pressed and sent skipped": len(good),
                "silent": [{k: s.get(k) for k in ("ok", "ran_ms", "cap_ms", "didnt_catch_played", "next")}
                           for s in silent], "ai sent": ai.get("sent")}


def _window_ok(w: dict) -> bool:
    if w.get("path") == "recorded" and w.get("ended") == "quiet":
        heard = w.get("transcribed") or []
        return (w.get("quiet_to_stop_ms") is not None
                and abs(w["quiet_to_stop_ms"] - SILENCE_FREE_MS) <= WINDOW_TOLERANCE_MS
                and len(heard) == 1 and (heard[0].get("sent") or {}).get("maxSeconds") == 120
                and heard[0].get("status") == 200)
    if w.get("path") == "recorded" and w.get("ended") == "cap":
        return (w.get("ran_ms") is not None and w.get("cap_ms") is not None and w["cap_ms"] <= FOLLOW_UP_CAP_MS
                and 0.95 * w["cap_ms"] <= w["ran_ms"] <= w["cap_ms"] + 2_000)
    if w.get("path") == "browser" and w.get("ended") == "wait":
        return (not w.get("pressed") and not w.get("presses") and w.get("final_to_held_ms") is not None
                and w["final_to_held_ms"] >= 0.9 * GAP_FREE_MS)
    if w.get("path") == "browser" and w.get("ended") == "save":
        return (w.get("pressed") is True and w.get("final_to_held_ms") is not None and w["final_to_held_ms"] < GAP_FREE_MS
                and [p.get("testid") for p in w.get("presses") or []] == ["ai-save"])
    return False


def two_minutes_four_seconds(r: dict) -> tuple[bool, Any]:
    """IM25 (design §5.3, D15): the recorded follow-up window ends 4,000 +/- 500 ms after the last sound and is written
    down in its two-minute window (`maxSeconds` 120), or -- nothing said -- runs to its cap (shortened through the
    seam, never past the page's 120 s, which keel-web's source holds); the browser path's ends on the pause (nothing
    pressed, after the 4 s gap) or on *Save and next* (at once), as the story's does (IM22's measure)."""
    x = r["follow_up_windows"]
    windows = x.get("windows") or []
    kinds = {(w.get("path"), w.get("ended")) for w in windows}
    off = [w for w in windows if not _window_ok(w)]
    full = x.get("full") is True
    ok = (bool(windows) and not off and x.get("page_cap_ms") == FOLLOW_UP_CAP_MS
          and (not full or {("recorded", "quiet"), ("recorded", "cap")} <= kinds))
    return ok, {"windows": [{k: w.get(k) for k in ("path", "ended", "quiet_to_stop_ms", "ran_ms", "cap_ms",
                                                   "final_to_held_ms", "pressed")} for w in windows],
                "off": [w.get("ended") for w in off], "page cap": x.get("page_cap_ms"), "full": full}


def _take_ok(v: dict) -> bool:
    t1, t2, t3, t4 = (v.get(k) or {} for k in ("t1", "t2", "t3", "t4"))
    before, after = v.get("before_pill") or {}, v.get("after_pill") or {}
    heard = v.get("transcribed") or []
    ended = (v.get("how") == "done") or (v.get("quiet_to_stop_ms") is not None
                                         and abs(v["quiet_to_stop_ms"] - SILENCE_FREE_MS) <= WINDOW_TOLERANCE_MS)
    return (t1.get("state") == "idle" and t1.get("pill") == SPEAK and before.get("acquired") == 0
            and not before.get("starts") and after.get("acquired") == 1
            and t2.get("state") == "listening" and t2.get("card") and t2.get("wave")
            and (t2.get("clock") or "").endswith(f"up to {STORY_CAP}") and v.get("continue_enabled_listening") is False
            and t3.get("state") == "writing" and t3.get("writing") == WRITING_DOWN
            and len(heard) == 1 and heard[0].get("maxSeconds") == 60 and heard[0].get("status") == 200
            and bool(v.get("appended")) and t4.get("state") == "heard" and t4.get("value") == v.get("want")
            and t4.get("caret") == len(v.get("want") or "") and t4.get("footer") == HEARD_YOU
            and t4.get("pill") == ADD_MORE and v.get("sent") == v.get("want") and ended)


def _refused_ok(v: dict) -> bool:
    t6, before, after = v.get("t6") or {}, v.get("before_pill") or {}, v.get("after_pill") or {}
    return (before.get("acquired") == 0 and after.get("acquired") == 1 and not after.get("starts")
            and t6.get("state") == "typing-only" and t6.get("footer") == MIC_OFF_TYPING and v.get("pill_after") == 0)


def speak_or_type(r: dict) -> tuple[bool, Any]:
    """IM26 (keel-web 076 FR-6..FR-8, design §6): on a text link the story's box goes T1 -> T4 -- idle with *Speak* and
    nothing asked of the microphone, listening on the tap (the card, the waveform, the clock to 1:00, Continue off),
    *Writing it down…*, then the transcript **appended** to what was typed with the caret at the end, *Heard you.* and
    *Add more* -- `transcribe` with `maxSeconds` 60, the take ended by the 4 s quiet or by Done; the POSTed story is the
    box's; and T6 once: a refused microphone leaves typing only, said once."""
    x = r["speak"]
    takes = [v for v in x.values() if v.get("how") in ("quiet", "done")]
    refused = [v for v in x.values() if v.get("how") == "refused"]
    ok = bool(takes) and bool(refused) and all(_take_ok(v) for v in takes) and all(_refused_ok(v) for v in refused)
    return ok, {"takes": {v.get("person"): {"how": v.get("how"), "ok": _take_ok(v), "appended": v.get("appended"),
                                             "quiet_to_stop_ms": v.get("quiet_to_stop_ms")} for v in takes},
                "refused": {v.get("person"): _refused_ok(v) for v in refused}}


def the_follow_up_clips(r: dict) -> tuple[bool, Any]:
    """IM27 (keel-cloud 103 FR-6): every role's recording holds one FOLLOW_UP clip per rung its link walks, each saying
    *One last thing.* and the registry's spoken wording (the LADDER copy), DONE, served by rung -- never in the spoken
    order -- and (the full leg) a recording without them gains them on the first read: one DONE clip per rung per
    role in the same words, `{}` served before, READY throughout, no ledger row."""
    x = r["follow_up_clips"]
    roles = x.get("roles") or {}
    bad = {}
    for link, role in roles.items():
        want = role.get("want") or []
        clips = role.get("clips") or []
        if not (want and [c.get("itemId") for c in clips] == want and role.get("served") == sorted(want)
                and all(fake.rung(c.get("itemId")) and c.get("status") == "DONE"
                        and c.get("script") == fake.follow_up_script(fake.rung(c["itemId"])[3]) for c in clips)):
            bad[link] = role
    back = x.get("backfill")
    back_ok = back is None and not x.get("full") or (
        back is not None and back.get("taken_out") == sum(len(r_.get("want") or []) for r_ in roles.values())
        and all(v.get("ok") for v in (back.get("stored") or {}).values()) and bool(back.get("stored"))
        and all(v == [] for v in (back.get("served_before") or {}).values())
        and back.get("served_after") == back.get("want") and back.get("statuses") == ["READY"]
        and back.get("ledger_rows_added") == 0)
    ok = bool(roles) and not bad and "FOLLOW_UP" in fake.UNSPOKEN and back_ok
    return ok, {"roles": {k: {"want": v.get("want"), "clips": len(v.get("clips") or [])} for k, v in roles.items()},
                "off": bad, "backfill": back}


def _clip_heard(events: list[dict], hello: str | None) -> dict:
    """One clip's play as the page's media events tell it: the first `playing` and the `ended` after it, sound on,
    the served hello, no longer than `fake.HELLO_MAX_S` (its duration and the time from playing to ended), no error."""
    playing = next((e for e in events if e.get("type") == "playing"), None)
    ended = next((e for e in events if e.get("type") == "ended"), None)
    errors = [e for e in events if e.get("type") == "error" or e.get("error")]
    played_ms = ended["ms"] - playing["ms"] if playing and ended else None
    duration = (ended or playing or {}).get("duration")
    ok = bool(playing and ended and hello and not errors and playing.get("muted") is False
              and (playing.get("src") or "").endswith(hello) and duration and duration <= fake.HELLO_MAX_S
              and played_ms is not None and 0 < played_ms <= fake.HELLO_MAX_S * 1000
              and (ended.get("currentTime") or 0) >= duration - 0.25)
    return {"ok": ok, "played_ms": played_ms, "duration": duration,
            "muted": playing.get("muted") if playing else None, "src": playing.get("src") if playing else None,
            "errors": len(errors)}


def tap_to_hear(r: dict) -> tuple[bool, Any]:
    """IM28 (keel-web 087 FR-2): a tap on an unpicked card picks it and her hello plays inside that card -- a `video`
    in the card, sound on, the served `helloUrl` -- to its end (8 s or less), and the still returns; every unpicked
    card carries the play glyph, no other card plays, and the face picked is the one posted."""
    x = r["hear_face"]
    face, before, after = x.get("face"), x.get("before") or {}, x.get("after") or {}
    mine = [e for e in x.get("events") or [] if e.get("face") == face]
    others = [e for e in x.get("events") or [] if e.get("face") != face and e.get("type") in ("play", "playing")]
    clip = _clip_heard(mine, x.get("hello"))
    ok = (face in fake.FACES and x.get("hello") == fake.hello_path(face) and before.get("picked") is False
          and before.get("glyph") is True and bool(before.get("glyphs")) and all(before["glyphs"].values())
          and before.get("video") is False and clip["ok"] and not others
          and after.get("picked") is True and after.get("still") is True and after.get("video") is False
          and x.get("checked") == [face] and x.get("sent") == {"face": face})
    return ok, {"face": face, "clip": clip, "before": before, "after": after, "others": len(others),
                "checked": x.get("checked"), "sent": x.get("sent")}


def the_respondent_hears_her(r: dict) -> tuple[bool, Any]:
    """IM29 (keel-web 087 FR-3): on the intro when the founder let them choose, *Hear <name>* plays her hello in place
    of the round still -- sound on, the served `helloUrl`, to its end -- and the still returns; *Talk to <name>* and
    *Answer in writing* stay enabled before, throughout (polled) and after."""
    x = r["hear_intro"]
    face, before, after = x.get("face"), x.get("before") or {}, x.get("after") or {}
    name = fake.FACE_NAMES.get(face or "", "")
    clip = _clip_heard([e for e in x.get("events") or [] if e.get("intro")], x.get("hello"))
    polls = x.get("polls") or []
    enabled = (len(before.get("buttons") or {}) == 2 and all((before.get("buttons") or {}).values())
               and len(after.get("buttons") or {}) == 2 and all((after.get("buttons") or {}).values())
               and bool(polls) and all(p == [True, True] for p in polls))
    ok = (bool(name) and x.get("hello") == fake.hello_path(face) and (before.get("words") or "").startswith(
              f"Hear {name}") and before.get("still") is True and before.get("video") is False and clip["ok"]
          and after.get("still") is True and after.get("video") is False and enabled)
    return ok, {"face": face, "words": before.get("words"), "clip": clip, "polls": len(polls),
                "disabled_polls": sum(p != [True, True] for p in polls), "after": after}


def the_band_hears_her(r: dict) -> tuple[bool, Any]:
    """IM30 (keel-web 088 FR-2): on Sent after the recording, the who-asks band's *Hear <name> · 5 s* (`persona-hear`,
    her name, never *her*) plays her hello inside the band -- sound on, the served `helloUrl`, to its end, `data-hearing`
    while it plays -- and the still returns; a retired face (no hello) draws no such button."""
    x = r["hear_band"]
    face, before, after = x.get("face"), x.get("before") or {}, x.get("after") or {}
    name = fake.FACE_NAMES.get(face or "", "")
    if x.get("retired") or face in fake.RETIRED:
        ok = x.get("present") is False and not x.get("hello")
        return ok, {"face": face, "retired": True, "present": x.get("present")}
    events = x.get("events") or []
    clip = _clip_heard([e for e in events if e.get("band")], x.get("hello"))
    outside = [e for e in events if not e.get("band") and e.get("type") in ("play", "playing")]
    ok = (x.get("present") is True and bool(name) and x.get("hello") == fake.hello_path(face)
          and (before.get("words") or "") == f"Hear {name} · 5 s" and before.get("still") is True
          and before.get("video") is False and x.get("hearing_while") is True and clip["ok"] and not outside
          and after.get("still") is True and after.get("video") is False and not after.get("hearing"))
    return ok, {"face": face, "words": before.get("words"), "clip": clip, "hearing_while": x.get("hearing_while"),
                "outside": len(outside), "after": after}


#: (mark id, the record key it reads, the rule). Order is the leg's.
MARKS: list[tuple[str, str, Callable[[dict], tuple[bool, Any]]]] = [
    ("IM1", "ledger", one_recording_pair),
    ("IM2", "screens", no_price_shown),
    ("IM3", "roles", spoken_order),
    ("IM4", "idea", solution_three_facts),
    ("IM5", "word", no_founders_word),
    ("IM6", "pilot", pilot_last_and_counted),
    ("IM7", "range", range_served),
    ("IM8", "dry_run", dry_run_wrote_nothing),
    ("IM9", "ai_answers", heard_on_every_answer),
    ("IM10", "change", the_change_pair),
    ("IM11", "low_balance", refused_at_low_balance),
    ("IM12", "retry", the_retry_free),
    ("IM13", "arrivals", read_on_arrival),
    ("IM14", "hold", held_then_on),
    ("IM15", "confirm", asked_is_that_right),
    ("IM16", "back", went_back),
    ("IM17", "mic_test", mic_tested),
    ("IM18", "recorded", recorded_accepted),
    ("IM19", "hear_out", hears_them_out),
    ("IM20", "taps", taps_wait_for_save),
    ("IM21", "beat", a_beat_after_the_passages),
    ("IM22", "story", the_storys_save),
    ("IM23", "follow_up", asked_on_the_first_rung),
    ("IM24", "follow_up", skipped_honoured),
    ("IM25", "follow_up_windows", two_minutes_four_seconds),
    ("IM26", "speak", speak_or_type),
    ("IM27", "follow_up_clips", the_follow_up_clips),
    ("IM28", "hear_face", tap_to_hear),
    ("IM29", "hear_intro", the_respondent_hears_her),
    ("IM30", "hear_band", the_band_hears_her),
]


def score(record: dict) -> list[Check]:
    checks = []
    for mark, key, rule in MARKS:
        doc = (rule.__doc__ or "").strip().split("\n")[0]
        if key not in record:
            checks.append(Check(mark, doc, measured=False, ok=False))
            continue
        try:
            ok, detail = rule(record)
        except (KeyError, TypeError, IndexError, ValueError, AttributeError) as broken:
            ok, detail = False, {"record could not be read": repr(broken)}
        checks.append(Check(mark, doc, measured=True, ok=bool(ok), detail=detail))
    return checks


def scorecard(record: dict) -> dict:
    checks = score(record)
    measured = [c for c in checks if c.measured]
    return {"version": INTERVIEWER_MARKS_VERSION,
            "measured": len(measured), "met": sum(c.ok for c in measured),
            "unmeasured": [c.mark for c in checks if not c.measured],
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok, "detail": c.detail}
                       for c in checks]}
