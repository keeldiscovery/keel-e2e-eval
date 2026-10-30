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
#: v8 (spec 073 FR-2, keel-web 113 FR-2): IM5 re-pinned -- *A word from you* is hidden and the leg writes no word, so
#: IM5 holds the founder's word absent: none stored and every role's thanks clip the thank-you's default words (keel-cloud
#: `InterviewComposer.done`, spoken by `PassageComposer.said`); a word stored by another door still owes the old rule.
#: v9 (spec 074 FR-2, keel-web 115 + 116, keel-cloud 136: one recorded path): every spoken window is recorded and written
#: down -- the browser's recogniser, its restart in the quiet gap and its `not-allowed` leg are gone. Re-pinned: IM9 (a
#: spoken answer is RECORDED, the page's one path -- SPOKEN was the recogniser's), IM19 (the first words leave the window
#: recording -- *Recording your answer.*, *Hearing you…* -- and the two finals are one recording, one `answer` read whose
#: words are both), IM21 (nothing recorded in a beat; there is no recogniser to start) and IM25 (the follow-up's windows
#: are all recorded: by the pause, by *Save and next* or to the cap; the browser path's two kinds retire). No mark is
#: dropped; IM5, IM14-IM18, IM20, IM22-IM24 and IM26 read their records as before (the walk drives them through the
#: recorder now).
#: v10 (spec 075 FR-1, keel-cloud 142 + keel-web 124, contract 41: up to two follow-ups, each asked on the answer it
#: hangs on): re-pinned -- IM23 (each follow-up asked where the harness's walk asks it: right after the item it hangs on
#: under *About that*, at most two, the end's *One last thing* only for a rung still owed; every route call carrying
#: `asked`, none once two were asked; the response's `followUps[]`), IM24 (a skip is not sent -- 124 FR-3 -- and the
#: walk goes on to the step after it, the next item where the follow-up hung on one before the last) and IM25 (the
#: windows of every follow-up asked, each belonging to a planned rung). IM27 (the FOLLOW_UP clips) reads its record as
#: before: keel-cloud 142 reuses every rung's clip as it is. No mark born or dropped.
#: v11 (spec 075 FR-5, keel-cloud 144 + keel-web 126, contract 42): re-pinned -- IM23 (one kicker, *One more thing*, on
#: the spot and at the end: the AI sheet's kicker and where-word and the text link's; *About that* / *One last thing*
#: retire), IM26 (the box is `asking` -- *Allow the microphone…*, *Cancel*, no waveform, no clock, nothing recorded --
#: before T2 listening; the take ends with nothing let go, and the page lets the microphone go on the done screen) and
#: IM27 (every FOLLOW_UP clip opens on *One more thing.*). No mark born or dropped.
#: v12 (spec 076 FR-5, keel-cloud 145 FR-5 + keel-web 127 FR-3, contract 43: a story chip ends the interview): re-pinned
#: -- IM22 (the story's window on the AI link, as before, AND the story's chip on a second AI link ends it: one chip-only
#: response -- `recency: true`, `anchorChip`, no story, `answers: []`, `format` AI_INTERVIEWER, no follow-ups -- no
#: follow-up route call, no pilot write, the done screen and the microphone off, the person's part-1 rows *Couldn't
#: recall one particular {occasion}* and no solution or money line listing them) and IM23 (a text walk whose person taps
#: the chip -- 05-paidly's Xavier Dubois, *I'd rather not say* -- reaches no item and no follow-up route: `asked` false,
#: nothing owed, no screen, no `followUps`). No mark born or dropped.
#: v12 kept (spec 083, keel-cloud 143 + keel-web 125, contract 44, 2026-10-28: the two studio faces, DAPHNE preselected,
#: SASKIA the leg's first pick): only the data moved -- IM28's face check, IM29's and IM30's names and IM30's retired
#: branch read `interviewer_fake` (FACES, FACE_NAMES, RETIRED) as before, and the fake now holds 143's two and the eight
#: retired; no mark's words changed, none born or dropped.
#: v13 (spec 086 FR-5, keel-cloud 154, contract 44 unchanged: every follow-up names the thing): re-pinned -- IM27 reads
#: each rung's clip against the words the leg records for it (`said`, `vs.follow_up_clip`: the registry's spoken line
#: filled with the project's job, idea name, founder's item, effort and step), not the registry's bare line; the served
#: `followUps[].spoken` is that filled line. No mark born or dropped.
#: v14 (spec 089 FR-3, keel-cloud 158 + keel-web 135, contract 46: Importance asks one, then one more): re-pinned --
#: IM20 reads the one-then-one-more walk (the first tap holds the item while the ITEM_MORE clip *And one more?* plays,
#: the second tap or *Nothing else* completes it) where it read two ticks and *Save and next*. No mark born or dropped.
INTERVIEWER_MARKS_VERSION = 14
#: The answer path's reads, which store nothing (keel-cloud 099 FR-1 / FR-4, the founder's routes of its T011): a dry
#: run that only asks them has written nothing.
READS = re.compile(r"/(interview|interviewer)/(classify|answer|transcribe|follow-up)$")
#: keel-web 072 FR-9's status words, restated where the marks read them (harness/interviewer_screens.py keeps the page's).
HELD = "Got it. Moving on… say no to change"
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"
#: keel-web 073 FR-3 / FR-6: the status through the quiet gap, and a Save's 500 ms advance.
HEARING = "Listening. Pause when you’re done."
#: keel-web 115 (spec 074, IM19 v9): the recorded path's status while a window records, and its heard line once a sound
#: came in -- nothing is heard before it is written down.
RECORDING = "Recording your answer. Pause when you’re done."
HEARING_YOU = "Hearing you…"
#: keel-web 115 FR-1 (spec 074, IM9 v9): the page's one way to take a spoken answer.
SPOKEN_HOW = "RECORDED"
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

#: keel-web 076 / keel-cloud 103's words and numbers, restated where the marks read them. keel-web 126 FR-5 (spec 075
#: FR-5): the one kicker, on the spot and at the end; keel-cloud 142's cap.
FOLLOW_UP_KICKER = "One more thing"
MAX_FOLLOW_UPS = 2
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
#: keel-web 126 FR-4 (IM26 v11): the box's `asking` card while the microphone is asked for.
SPEAK_ASKING = "Allow the microphone…"

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
#: keel-cloud `InterviewComposer.done`: the thank-you's default words, *Thank you -- your answers have gone to {first}.*,
#: spoken as *Thank you, your answers ...* (`PassageComposer.said`); read here after `fake.normal`.
THANKS_DEFAULT = "thank you your answers have gone to"
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
    """IM5: no founder's word is spoken -- none stored since keel-web 113 hid the word, every thanks clip the default."""
    pitch = fake.normal(r["word"])
    if not pitch:
        # v8 (spec 073 FR-2): no word written -- every role's THANKS clip is the default thank-you and nothing else
        clips = (r["recording"] or {}).get("clips") or []
        thanks = [c for c in clips if c.get("kind") == "THANKS"]
        off = [{"role": c.get("role"), "script": c.get("script")} for c in thanks
               if not fake.normal(c.get("script")).startswith(THANKS_DEFAULT)
               or len(fake.normal(c.get("script")).split()) > len(THANKS_DEFAULT.split()) + 3]
        return bool(thanks) and not off, {"word": None, "thanks": len(thanks), "off": off}
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
    `formatUsed` AI_INTERVIEWER. v9 (spec 074, keel-web 115): the spoken answers are RECORDED -- the page's one path --
    and none says SPOKEN (the browser recogniser's, retired)."""
    x = r["ai_answers"]
    body = x.get("body") or {}
    answers = body.get("answers") or []
    bad = [a.get("itemId") for a in answers
           if a.get("how") not in ("SPOKEN", "TAPPED", "TYPED", "RECORDED")
           or (a.get("how") in ("SPOKEN", "RECORDED") and not (a.get("heard") or "").strip())
           or len(a.get("heard") or "") > 600]
    spoken = [a for a in answers if a.get("how") == SPOKEN_HOW]
    retired = [a.get("itemId") for a in answers if a.get("how") == "SPOKEN"]
    ok = (body.get("format") == "AI_INTERVIEWER" and bool(answers) and bool(spoken) and not bad and not retired
          and (x.get("register_row") or {}).get("formatUsed") == "AI_INTERVIEWER")
    return ok, {"bad": bad, "answers": len(answers), "spoken": len(spoken), "said SPOKEN": retired,
                "format": body.get("format"), "formatUsed": (x.get("register_row") or {}).get("formatUsed")}


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
    aloud, then answered within a second, is ONE read: the first final leaves nothing ticked and the window recording
    (v9, keel-web 115: the status *Recording your answer. Pause when you're done.* and the heard line *Hearing you…*),
    no read in the gap, then one read (the recording's `answer`) whose words are both finals joined; the response
    carries the answer meant."""
    x = r["hear_out"]
    hearing = x.get("hearing") or []
    loud = [s for s in hearing if not _quiet(s)]
    first = x.get("after_first") or {}
    after = first.get("after") or {}
    reads = x.get("reads") or []
    joined = _norm(f"{x.get('first')} {x.get('second')}")
    ok = (bool(hearing) and not loud and bool(first) and not after.get("lit") and not after.get("field")
          and not after.get("preview") and after.get("status") == RECORDING and after.get("heard") == HEARING_YOU
          and first.get("still") is True
          and (x.get("between_ms") or 10 ** 9) <= WITHIN_MS and x.get("reads_in_gap") == 0
          and len(reads) == 1 and _norm(reads[0]) == joined and x.get("sent") == [x.get("meant")])
    return ok, {"question": x.get("question"), "first": x.get("first"), "second": x.get("second"),
                "between_ms": x.get("between_ms"), "after first": after, "reads in gap": x.get("reads_in_gap"),
                "reads": reads, "settled": x.get("settled"), "sent": x.get("sent"), "meant": x.get("meant"),
                "finals looked at": len(hearing), "lit while hearing": loud}


def taps_wait_for_save(r: dict) -> tuple[bool, Any]:
    """IM20 (keel-web 073 FR-6; v14, spec 089 FR-3: keel-cloud 158 and keel-web 135 FR-2): on Importance a tap is one
    pick, then one more -- the first tap marks one pick and nothing goes on by itself for 1.5 s (the same question,
    `listening`, no ring) while the second ask's *And one more?* clip plays (the item's ITEM_MORE, served `more`); the
    second tap (or *Nothing else*) completes the item and it goes on; the response carries the picks wanted, `how`
    TAPPED. (Before v14 two ticks enabled *Save and next* and a third was ignored.) Spec 090 FR-2 (keel-web 135 H-2):
    the walk reads `one` once the `more` clip has played and the sheet listens again (`at_tap_wait` keeps what the 1.5 s
    showed, the stage maybe still `speaking`), so the reading is the same and the version stays."""
    x = r["taps"]
    one, two = x.get("one") or {}, x.get("two") or {}
    want = sorted(x.get("want") or [])
    ok = (one.get("question_same") is True and one.get("phase") == "listening" and one.get("ring") is False
          and len(one.get("checked") or []) == 1 and one.get("more_played") is True
          and two.get("ring") is False
          and x.get("next") != x.get("question")
          and sorted(x.get("sent") or []) == want[:2] and x.get("sent_how") == "TAPPED")
    return ok, {k: x.get(k) for k in ("question", "want", "one", "two", "save_pressed", "statuses_after", "sent",
                                      "sent_how")}


def a_beat_after_the_passages(r: dict) -> tuple[bool, Any]:
    """IM21 (keel-web 075 FR-1, keel-cloud 101): after the problem and the idea passages -- and nowhere else -- a beat:
    `data-phase` beat for its 2 s, the status *Take a moment.* alone, the pill *pause*, no waveform, no question, no
    options, no button on the sheet, no recording begun inside it (v9, keel-web 115: the page's one ear -- there is no
    recogniser to start), then the next clip."""
    x = r["beat"]
    beats = x.get("beats") or []
    expected = x.get("expected") or []
    least = BEAT_SHARE * float(x.get("beat_ms") or 0)
    bad = [b for b in beats if not (
        b.get("statuses") == [BEAT] and set(b.get("pills") or []) == {BEAT_PILL} and b.get("micOn") is False
        and b.get("question") is False and b.get("options") is False and not b.get("buttons")
        and b.get("recordings_in") == 0
        and b.get("ms") is not None and b.get("ms") >= least and b.get("next") == "speaking")]
    after = [b.get("after_kind") for b in beats]
    ok = bool(expected) and after == expected and not bad and least > 0
    return ok, {"expected after": expected, "after": after, "ms": [b.get("ms") for b in beats],
                "off": [{k: b.get(k) for k in ("after_kind", "ms", "statuses", "pills", "micOn", "question",
                                               "options", "buttons", "recordings_in", "recordings_at_ms", "next")}
                        for b in bad]}


def the_storys_save(r: dict) -> tuple[bool, Any]:
    """IM22 (keel-web 074 FR-2): the story's window says *Take your time. Pause for a few seconds when you're done, or
    tap Save.*; *Save and next* is absent until a final is heard, then drawn and enabled; the story ends by the pause
    with nothing pressed (S-005) or by Save, read at once -- held inside the gap (S-006); held either way with the
    words heard, never classified, then on; and the response carries the story. v12 (spec 076 FR-5, keel-web 127
    FR-3): and the story's chip, tapped on a second AI link, ends the interview (`chip_ended_it`) -- owed wherever the
    story is walked."""
    ok, why = _the_storys_save(r)
    chip_ok, chip_why = chip_ended_it(r.get("story_chip") or {}) if r.get("story_chip") is not None else (False, None)
    return ok and chip_ok, {**why, "chip ends it": chip_ok, "chip": chip_why}


def _the_storys_save(r: dict) -> tuple[bool, Any]:
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


#: keel-cloud 145 FR-5 / keel-web 127 FR-3 (IM22 v12): the AI link's chip-only body, its format beside it.
CHIP_ONLY = {"recency": True, "anchorChip": "CANT_RECALL", "answers": [], "format": "AI_INTERVIEWER"}


def chip_ended_it(x: dict) -> tuple[bool, Any]:
    """IM22 v12's second half (spec 076 FR-5): the story's chip tapped on the AI link ends the interview -- the chip
    drawn as *I can't recall one particular {occasion}*; ONE `POST response`, 201, its body the chip-only submission
    (`pilotOptIn: false` the page's deprecated constant, nothing else); no follow-up route call and no pilot write; the
    done screen and *Microphone off*; and on the people rows the person read with the chip's words on part 1, on no
    solution or money line (`row_faults` empty)."""
    responses = x.get("responses") or []
    body = dict((responses[0] if responses else {}).get("body") or {})
    pilot_flag = body.pop("pilotOptIn", False)
    mic = x.get("mic_off") or {}
    ok = (x.get("chip") == x.get("want_chip") and len(responses) == 1 and responses[0].get("status") in (200, 201)
          and body == CHIP_ONLY and pilot_flag is False and not x.get("follow_up_calls") and x.get("pilot_writes") == 0
          and bool((x.get("done") or {}).get("text")) and mic.get("shown") is True and not x.get("row_faults"))
    return ok, {"chip": x.get("chip"), "want_chip": x.get("want_chip"), "responses": responses,
                "follow_up_calls": x.get("follow_up_calls"), "pilot_writes": x.get("pilot_writes"),
                "done": x.get("done"), "mic_off": mic.get("shown"), "row_faults": x.get("row_faults")}


def _kicker(asked: dict) -> str:
    """v11 (keel-web 126 FR-5): one kicker for every follow-up, on the spot (`on` its item) and at the end alike."""
    return FOLLOW_UP_KICKER


def _calls_ok(routes: list[dict], plan: list[dict]) -> bool:
    """Spec 075 (keel-cloud 142 FR-1): every route call 200 or 204, none once two were asked; the 200s on the plan's
    rungs in its order (one asked again after Back repeats its rung), each carrying `asked` -- the rungs asked before
    it -- and the harness's text."""
    rungs = [a["dimension"] for a in plan]
    by_rung = {a["dimension"]: a for a in plan}
    ok = [r for r in routes if r.get("status") == 200]
    if any(r.get("status") not in (200, 204) for r in routes):
        return False
    if any(len(((r.get("sent") or {}).get("asked") or [])) >= MAX_FOLLOW_UPS for r in routes):
        return False
    if list(dict.fromkeys((r.get("body") or {}).get("dimension") for r in ok)) != rungs:
        return False
    for r in ok:
        body = r.get("body") or {}
        a = by_rung[body.get("dimension")]
        if ((r.get("sent") or {}).get("asked") or []) != rungs[:rungs.index(a["dimension"])] \
                or body.get("text") != a.get("text"):
            return False
    return True


def _text_asked_right(t: dict) -> bool:
    """One text walk's follow-ups as IM23 holds them (v10, spec 075; v11 the one kicker): the route 200 on each of the
    harness's planned rungs and on nothing else, `asked` the rungs before it; each screen right after the item it hangs
    on (the end's only for a rung still owed) under *One more thing*, its text the route's; at most two; the response's
    `followUps` the rungs typed, in the order asked -- or, owed nothing, no 200, no screen, no `followUps`; and a walk
    that never reached the route (a gate No) asked nothing."""
    plan, routes, screens, sent = t.get("plan") or [], t.get("routes") or [], t.get("screens") or [], t.get("sent")
    if not t.get("asked"):
        return not routes and not screens and sent is None
    if not plan:
        return all(r.get("status") == 204 for r in routes) and not screens and sent is None
    lines = t.get("lines") or {}
    typed = [a["dimension"] for a in plan if lines.get(a["dimension"])]
    return (len(plan) <= MAX_FOLLOW_UPS and _calls_ok(routes, plan)
            and [s.get("rung") for s in screens] == [a["dimension"] for a in plan]
            and all(s.get("on") == a.get("on") and s.get("kicker") == _kicker(a) and s.get("question") == a.get("text")
                    for s, a in zip(screens, plan))
            and [f.get("dimension") for f in sent or []] == typed)


def _ai_asked_right(ai: dict) -> bool:
    """The AI link's follow-ups as IM23 holds them (v10): every 200 of the route on the harness's planned rungs with
    their text and each rung's clip, `asked` the rungs before it; the follow-ups met in the plan's order, every window
    opened on its rung's clip with its text (`followUp` step) right after its item (or at the end), under *One more
    thing* (v11); the said walk meets two, the second on the last item, and its response names both."""
    plan = ai.get("plan") or []
    clips = ai.get("want_clips") or {}
    routes = [a for a in ai.get("asked") or [] if a.get("route") == "follow-up"]
    met = (ai.get("walk") or {}).get("follow_ups") or []
    by_rung = {a["dimension"]: a for a in plan}
    if not plan or len(plan) > MAX_FOLLOW_UPS or not _calls_ok(routes, plan):
        return False
    if any(((r.get("body") or {}).get("clip") or {}).get("clipId") != clips.get((r.get("body") or {}).get("dimension"))
           for r in routes if r.get("status") == 200):
        return False
    if [m.get("rung") for m in met] != [a["dimension"] for a in plan] or not any(a.get("on") for a in plan):
        return False
    for m in met:
        a = by_rung[m["rung"]]
        if not m.get("windows") or not all(
                w.get("clip") == clips.get(m["rung"]) and w.get("question") == a.get("text")
                and w.get("step") == "followUp" and w.get("kicker") == _kicker(a) for w in m["windows"]):
            return False
    if ai.get("by") == "said":
        return len(plan) == MAX_FOLLOW_UPS and [f.get("dimension") for f in ai.get("sent") or []] == \
            [a["dimension"] for a in plan]
    return True


def asked_on_the_first_rung(r: dict) -> tuple[bool, Any]:
    """IM23 (keel-cloud 103, design §2 / §5; v10 spec 075, keel-cloud 142 / keel-web 124): each follow-up is asked
    where the harness's own walk (the LADDER copy, `vs.follow_up_plan`) asks it -- right after the item it hangs on,
    at most two, the end's only for a rung still owed, every one under *One more thing* (v11, keel-web 126) -- on every
    text walk (the route calls with `asked`, the screens, the response's `followUps`), on the AI link (each route
    reply's rung, text and clip, every window on its rung's clip) and on Try it yourself's twin where walked (with the
    first rung `asked`, the next owed or 204); none where nothing is owed, and none asked after a gate No."""
    x = r["follow_up"]
    text = x.get("text") or []
    bad = [t.get("person") for t in text if not _text_asked_right(t)]
    ai = x.get("ai")
    tried = x.get("try")
    then = (tried or {}).get("then")
    try_ok = tried is None or ((tried.get("status") == 200 and (tried.get("body") or {}).get("dimension")
                                == (tried.get("owed") or {}).get("dimension")
                                and (tried.get("clear") or {}).get("status") == 204)
                               and (then is None or then.get("status") == (200 if then.get("owed") else 204)))
    owed = [t for t in text if t.get("asked") and t.get("plan")]
    clear = [t for t in text if t.get("asked") and not t.get("plan")]
    ok = bool(owed) and bool(clear) and not bad and ai is not None and _ai_asked_right(ai) and try_ok
    return ok, {"text walks": len(text), "owed": len(owed), "owed nothing": len(clear), "wrong": bad,
                "two": sum(1 for t in owed if len(t.get("plan") or []) == MAX_FOLLOW_UPS),
                "on the spot": sum(1 for t in owed for a in t.get("plan") or [] if a.get("on")),
                "at the end": sum(1 for t in owed for a in t.get("plan") or [] if not a.get("on")),
                "rungs": sorted({a["dimension"] for t in owed for a in t.get("plan") or []}),
                "ai": None if ai is None else {"plan": [(a.get("dimension"), a.get("on")) for a in ai.get("plan") or []],
                                               "ok": _ai_asked_right(ai), "sent": ai.get("sent")},
                "try": tried and {"status": tried.get("status"), "clear": (tried.get("clear") or {}).get("status"),
                                  "then": then and then.get("status")}}


def skipped_honoured(r: dict) -> tuple[bool, Any]:
    """IM24 (keel-web 076, keel-cloud 103; v10 spec 075, keel-web 124 FR-3): a skip -- *Skip this one* pressed on a text
    link, or the AI interviewer's window left silent to its cap -- sends nothing for that rung (it is not in the
    response's `followUps`; the cloud stores the first owed rung with nothing sent as never answered), and the walk goes
    on to the step after it -- on the AI link with no didn't-catch: the next item where the follow-up hung on one before
    the last, else the pilot ask."""
    x = r["follow_up"]
    pressed = []
    for t in x.get("text") or []:
        lines = t.get("lines") or {}
        sent = [f.get("dimension") for f in t.get("sent") or []]
        for a, screen in zip(t.get("plan") or [], t.get("screens") or []):
            if t.get("asked") and not lines.get(a["dimension"]):
                pressed.append({"person": t.get("person"), "rung": a["dimension"], "on": a.get("on"),
                                "ok": screen.get("did") == "skipped" and a["dimension"] not in sent})
    silent = []
    ai = x.get("ai") or {}
    sent_ai = [f.get("dimension") for f in ai.get("sent") or []]
    for w in (ai.get("walk") or {}).get("windows") or []:
        if w.get("ended") == "cap":
            silent.append({"ok": w.get("rung") not in sent_ai and w.get("didnt_catch_played") == 0
                           and w.get("next_step") is not None and w.get("next_step") == w.get("want_next"), **w})
    ok = bool(pressed or silent) and all(p["ok"] for p in pressed) and all(s_["ok"] for s_ in silent)
    return ok, {"pressed": pressed,
                "silent": [{k: s_.get(k) for k in ("ok", "rung", "ran_ms", "cap_ms", "didnt_catch_played", "next_step",
                                                   "want_next")} for s_ in silent], "ai sent": ai.get("sent")}


def _written_down(w: dict) -> bool:
    heard = w.get("transcribed") or []
    return len(heard) == 1 and (heard[0].get("sent") or {}).get("maxSeconds") == 120 and heard[0].get("status") == 200


def _window_ok(w: dict) -> bool:
    """One follow-up window as IM25 holds it. v9 (spec 074, keel-web 115): every window is recorded -- ended by the pause
    (4 s after the last sound), by *Save and next* (read at once, inside the gap) or, nothing said, at the cap; each one
    with words written down once in its two-minute window. The browser path's windows (`wait`, `save`) retire with the
    recogniser."""
    if w.get("path") != "recorded":
        return False
    if w.get("ended") == "quiet":
        return (w.get("quiet_to_stop_ms") is not None
                and abs(w["quiet_to_stop_ms"] - SILENCE_FREE_MS) <= WINDOW_TOLERANCE_MS and not w.get("pressed")
                and not w.get("presses") and _written_down(w))
    if w.get("ended") == "save":
        return (w.get("pressed") is True and w.get("final_to_held_ms") is not None and w["final_to_held_ms"] < GAP_FREE_MS
                and [p.get("testid") for p in w.get("presses") or []] == ["ai-save"] and _written_down(w))
    if w.get("ended") == "cap":
        return (w.get("ran_ms") is not None and w.get("cap_ms") is not None and w["cap_ms"] <= FOLLOW_UP_CAP_MS
                and 0.95 * w["cap_ms"] <= w["ran_ms"] <= w["cap_ms"] + 2_000)
    return False


def two_minutes_four_seconds(r: dict) -> tuple[bool, Any]:
    """IM25 (design §5.3, D15): the recorded follow-up window ends 4,000 +/- 500 ms after the last sound and is written
    down in its two-minute window (`maxSeconds` 120), or on *Save and next* at once (IM22's measure) and written down
    the same, or -- nothing said -- runs to its cap (shortened through the seam, never past the page's 120 s, which
    keel-web's source holds). v9 (spec 074): every window is the recorded path's; the short form owes the pause and
    Save, the full leg the pause and the cap. v10 (spec 075, keel-web 124): the windows of every follow-up asked -- up
    to two, each on a rung the harness's walk plans."""
    x = r["follow_up_windows"]
    windows = x.get("windows") or []
    kinds = {(w.get("path"), w.get("ended")) for w in windows}
    # v10 (spec 075): the windows of every follow-up asked, each its planned rung's
    rungs = x.get("rungs")
    off = [w for w in windows if not _window_ok(w) or (rungs is not None and w.get("rung") not in rungs)]
    full = x.get("full") is True
    owed = {("recorded", "quiet"), ("recorded", "cap")} if full else {("recorded", "quiet"), ("recorded", "save")}
    ok = (bool(windows) and not off and x.get("page_cap_ms") == FOLLOW_UP_CAP_MS and owed <= kinds)
    return ok, {"windows": [{k: w.get(k) for k in ("path", "ended", "quiet_to_stop_ms", "ran_ms", "cap_ms",
                                                   "final_to_held_ms", "pressed")} for w in windows],
                "off": [w.get("ended") for w in off], "page cap": x.get("page_cap_ms"), "full": full, "rungs": rungs}


def _asking_ok(v: dict) -> bool:
    """v11 (keel-web 126 FR-4): the tap is `asking` while the permission is asked -- *Allow the microphone…* and
    *Cancel*, no waveform, no clock, no Done, the microphone asked once and nothing recorded, Continue off."""
    ta, during = v.get("asking") or {}, v.get("asking_counts") or {}
    return (ta.get("state") == "asking" and ta.get("asking") == SPEAK_ASKING and ta.get("cancel") is True
            and not ta.get("wave") and not ta.get("clock") and not ta.get("done") and during.get("acquired") == 1
            and not during.get("starts") and v.get("continue_enabled_asking") is False)


def _kept_ok(v: dict) -> bool:
    """v11 (keel-web 126 FR-4): the take's end let nothing go -- the microphone's releases at T4 are those before the
    pill (a dev build's StrictMode may stamp one at load) -- and the page let it go on the done screen."""
    before, counts = v.get("before_pill") or {}, v.get("counts") or {}
    at_done = v.get("released_at_done")
    return (counts.get("released") is not None and counts.get("released") == before.get("released")
            and at_done is not None and at_done > counts["released"])


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
            and t4.get("pill") == ADD_MORE and v.get("sent") == v.get("want") and ended
            and _asking_ok(v) and _kept_ok(v))


def _refused_ok(v: dict) -> bool:
    t6, before, after = v.get("t6") or {}, v.get("before_pill") or {}, v.get("after_pill") or {}
    return (before.get("acquired") == 0 and after.get("acquired") == 1 and not after.get("starts")
            and t6.get("state") == "typing-only" and t6.get("footer") == MIC_OFF_TYPING and v.get("pill_after") == 0)


def speak_or_type(r: dict) -> tuple[bool, Any]:
    """IM26 (keel-web 076 FR-6..FR-8, design §6): on a text link the story's box goes T1 -> T4 -- idle with *Speak* and
    nothing asked of the microphone, listening on the tap (the card, the waveform, the clock to 1:00, Continue off),
    *Writing it down…*, then the transcript **appended** to what was typed with the caret at the end, *Heard you.* and
    *Add more* -- `transcribe` with `maxSeconds` 60, the take ended by the 4 s quiet or by Done; the POSTed story is the
    box's; and T6 once: a refused microphone leaves typing only, said once. v11 (spec 075 FR-5, keel-web 126 FR-4):
    between the tap and T2 the box is `asking` (the seam holds the permission sheet until the walk grants it), and the
    microphone is kept through the take and let go by the page on the done screen."""
    x = r["speak"]
    takes = [v for v in x.values() if v.get("how") in ("quiet", "done")]
    refused = [v for v in x.values() if v.get("how") == "refused"]
    ok = bool(takes) and bool(refused) and all(_take_ok(v) for v in takes) and all(_refused_ok(v) for v in refused)
    return ok, {"takes": {v.get("person"): {"how": v.get("how"), "ok": _take_ok(v), "appended": v.get("appended"),
                                             "quiet_to_stop_ms": v.get("quiet_to_stop_ms"), "asking": _asking_ok(v),
                                             "kept": _kept_ok(v)} for v in takes},
                "refused": {v.get("person"): _refused_ok(v) for v in refused}}


def _said(role: dict, rung: str) -> str:
    """v13 (keel-cloud 154): a rung's clip words as the leg recorded them, filled with the project's words (`said`); a
    record from before v13 carries none and reads the registry's spoken wording, as it did."""
    return (role.get("said") or {}).get(rung) or fake.rung(rung)[3]


def the_follow_up_clips(r: dict) -> tuple[bool, Any]:
    """IM27 (keel-cloud 103 FR-6): every role's recording holds one FOLLOW_UP clip per rung its link walks, each saying
    *One more thing.* (v11, keel-cloud 144 FR-2) and the registry's spoken wording (the LADDER copy; v13, keel-cloud 154:
    filled with the project's words, the leg's `said`), DONE, served by
    rung -- never in the spoken order -- and (the full leg) a recording without them gains them on the first read: one
    DONE clip per rung per role in the same words, `{}` served before, READY throughout, no ledger row."""
    x = r["follow_up_clips"]
    roles = x.get("roles") or {}
    bad = {}
    for link, role in roles.items():
        want = role.get("want") or []
        # keel-cloud 118: a rung may carry a second *#also* clip (its other stem) beside its own -- not a rung of its
        # own, never served by rung (read by its item id); held as the leg holds it (spec 068: S-006 on the 129 build)
        every = role.get("clips") or []
        clips = [c for c in every if "#also" not in (c.get("itemId") or "")]
        also = [c for c in every if "#also" in (c.get("itemId") or "")]
        if not (want and [c.get("itemId") for c in clips] == want and role.get("served") == sorted(want)
                and all(fake.rung(c.get("itemId")) and c.get("status") == "DONE"
                        and c.get("script") == fake.follow_up_script(_said(role, c["itemId"])) for c in clips)
                and all(c["itemId"].split("#")[0] in want and c.get("status") == "DONE"
                        and str(c.get("script") or "").startswith(fake.ONE_MORE_THING) for c in also)):
            bad[link] = role
    back = x.get("backfill")
    back_ok = back is None and not x.get("full") or (
        back is not None and back.get("taken_out") == sum(len(r_.get("clips") or []) for r_ in roles.values())
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
