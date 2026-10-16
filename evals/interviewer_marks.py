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

#: Bumped whenever a mark is born, retired, or reads its record differently.
INTERVIEWER_MARKS_VERSION = 1

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
READ_REASON = re.compile(r"^(read-on-arrival:[0-9a-f-]{36}|brief:on-return|retry:[23]:[0-9a-f-]{36})$")


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
    """IM1: the first recording is ONE `INTERVIEWER_RECORDING` HOLD of -400 (price_version 9, no job, this project) and
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
    link serves it; and one DIDNT_CATCH a role."""
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
        this = said == want and catches == 1
        ok = ok and this
        out[name] = {"ok": this, "said": said, "want": want, "didntCatch": catches}
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
    no ledger row, and the page posts nothing."""
    x = r["dry_run"]
    ok = (x.get("tryRun") is True and x.get("clips", 0) > 0 and x.get("before") == x.get("after")
          and not x.get("writes"))
    return ok, x


def heard_on_every_answer(r: dict) -> tuple[bool, Any]:
    """IM9: the AI link's `POST response` says `format` AI_INTERVIEWER and carries `how` on every answer and `heard`
    on every spoken one (at most 600 characters; spec 044 FR-003 "heard on every spoken answer" -- a value typed into
    a field carries none, DRIFT #89); the register's row then reads `formatUsed` AI_INTERVIEWER."""
    x = r["ai_answers"]
    body = x.get("body") or {}
    answers = body.get("answers") or []
    bad = [a.get("itemId") for a in answers
           if a.get("how") not in ("SPOKEN", "TAPPED", "TYPED")
           or (a.get("how") == "SPOKEN" and not (a.get("heard") or "").strip())
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
    every reading or brief HOLD the leg's ledger holds says why it was written (a brief `brief:on-return`): none was
    pressed by the founder, and no brief is written by a batch."""
    holds = [x for x in r["ledger"] if x.get("kind") == "HOLD" and x.get("action") in ("INTERPRET", "BRIEF")]
    unexplained = [x for x in holds if not READ_REASON.match(x.get("reason") or "")]
    per = {}
    for a in r["arrivals"]:
        mine = [x for x in a.get("holds") or [] if x.get("action") == "INTERPRET"
                and x.get("reason") == f"read-on-arrival:{a['invitationId']}"]
        per[a["invitationId"]] = len(mine)
    ok = bool(per) and all(1 <= n <= 3 for n in per.values()) and not unexplained
    return ok, {"arrivals": per, "unexplained": unexplained, "holds": len(holds)}


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
