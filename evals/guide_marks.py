"""The guide marks (spec 054): keel-cloud 106's `guide-seen` (contract 20) and keel-web 080's welcome sheet, held over
one journey's record -- deterministic, zero spend, the shape of `evals/interviewer_marks.py` (one check a rule; a mark
whose subject the record does not carry is **unmeasured** -- reported, never passed).

Design of record: keel-cloud-docs `canon/designs/onboarding-videos-design-2026-10-17.md` §5 (the files are keel-web's
own `public/guide/`, the phone at 390 x 844), §7.1 (the welcome's twelve cues) and §8 D24 (the welcome at the start of
every project, once, Skip always visible and the only control). **The welcome only**: the openers (D25) and the
explainers (D26 / D27) are later specs, and the record keeps `openers` and `explainers` for them (G6 on).

A **journey** ruler with its own version: no model turn, corpus entry or instruction moves (the welcome is a video and
a flag), so `instructions/marks.py`'s `MARKS_VERSION` stays where it is (FR-4). The journey
(`evals/corpus_scenario.leg_welcome`) builds the record from what keel-web drew and sent and what the wire answered;
`score` reads only the record, so a unit test can seed a bad one and watch the mark fail (`tests/test_guide_marks.py`).

- **G1 once per project** (`welcome`): the sheet at the first open, where the overview the page received said
  `welcomeSeen: false`; absent at the next open (a plain `goto`) and on every corridor frame the journey read after;
  exactly one `guide-seen` POST from the page in the leg's window, and it is `{what: WELCOME}`.
- **G2 skippable from the first frame** (`welcome`): Skip visible, enabled and in view without scrolling (its box
  inside the viewport, `elementFromPoint` at its centre Skip) at 1280 x 720 and at 390 x 844; the sheet's only control
  with a word (a wordless control is allowed only as the face's sound toggle, 080 FR-2.1's speaker glyph -- judgement
  call 6); the reads taken before any cue but the wordmark (cue 1, the opening frame itself) fired; the press closed the
  sheet within a second.
- **G3 seen is remembered on the wire** (`welcome`): the press's POST `{what: WELCOME}` (no `stage`) answered 204, the
  same POST once more on the wire 204 (106's idempotence); `Overview.guide` `{welcomeSeen: true, openersSeen: []}`
  after, as the page received it at the next open and as the wire serves it; the overview's `revision` the same before
  the press, after it and after the repeat; the next founder write -- the context step's Save -- answered its success
  on the first press (keel-cloud's `proposeContext` is 202: it carries no `expectedRevision`), never 409.
- **G4 replay posts nothing** (`replay`): *Play the welcome again* (`guide-replay`, the Feedback panel's foot as 080
  builds it) opens the sheet near 0 s with Skip in view and Skip closes it; once more, a seek to the video's end closes
  it by itself; zero `guide-seen` requests across both; `welcomeSeen` still true, the revision unchanged.
- **G5 the cues fire in order** (`walk`): the served `welcome.cues.json` is the twelve of §7.1 in order, ids unique,
  `at` strictly rising; a seam `seek(at + 0.05)` per cue draws that cue's snippet each time, and `cuesFired` after each
  is the twelve's prefix to it (monotonic, no repeat, never shrinking).

G4 and G5 are measured once per matrix, on S-005's local journey; every other journey and the remote profile carry no
`replay` or `walk`, so the card reports them **unmeasured** and the record's `notes` say why (`REMOTE_WHY` /
`ELSEWHERE_WHY`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

#: Bumped whenever a mark is born, retired, or reads its record differently.
#: v1 (spec 054, keel-cloud 106 / keel-web 080, contract 20): G1 (once per project), G2 (skippable from the first
#: frame), G3 (seen is remembered on the wire), G4 (replay posts nothing) and G5 (the cues fire in order) born -- the
#: welcome only; `openers` and `explainers` are reserved for the specs that build D25 and D26 / D27 (G6 on).
GUIDE_MARKS_VERSION = 1

#: keel-web 080 FR-1 / design §7.1: the welcome's twelve cues, in the order they play (`welcome.cues.json`'s ids).
WELCOME_CUES = ("wordmark", "three-questions", "three-chips", "thirteen-dots", "phone-interview", "report", "rows-hold",
                "quote", "price-pilot", "promise", "explainer-pill", "start")
#: keel-web 080 FR-1: cue 2's `at` -- a read with no seam to ask (remote) is "before any cue but the wordmark" when the
#: video's clock is below it.
SECOND_CUE_AT = 13.25
#: How far past a cue's `at` the walk seeks (FR-3 b).
SEEK_PAST = 0.05
#: keel-web 080 `GUIDE_SKIP` (*Skip ›*): the one word on the sheet. G2 holds the word's first four letters, so the
#: chevron's spelling is the journey pass's DRIFT question, not a mark's.
SKIP_WORD = "Skip"
#: keel-web 080 FR-2.1: the face's sound toggle, a speaker glyph with no visible word (`GUIDE_SOUND_ON` / `_OFF`).
SOUND_LABELS = ("Sound on", "Sound off")
#: The two sizes Skip is read at (FR-2 b): the harness's window (Playwright's default) and the phone (design §5).
SIZES = ("1280x720", "390x844")
#: FR-2 c: the sheet gone within a second of the press.
GONE_MS = 1_000
#: FR-3 d: *Play again* starts the video near 0 s.
REPLAY_NEAR_S = 1.0
WELCOME = {"what": "WELCOME"}
#: Why G4 / G5 are unmeasured where they are (the `REMOTE_TYPES` precedent, `evals/corpus_scenario.py`).
REMOTE_WHY = ("keel-web reads window.__keelGuide only in its test build and staging serves the production build, so "
              "the cue walk and the replays (G4, G5) are not run on the remote profile")
ELSEWHERE_WHY = "the cue walk and the replays (G4, G5) are S-005's, once per matrix, on the local profile"


@dataclass(frozen=True)
class Check:
    mark: str
    rule: str
    measured: bool
    ok: bool
    detail: Any = None


def _posts(requests: list[dict] | None) -> list[dict]:
    return [r for r in requests or [] if (r.get("method") or "").upper() == "POST"]


# ------------------------------------------------------------------------------------------------ the marks

def once_per_project(r: dict) -> tuple[bool, Any]:
    """G1: the sheet at the first open with `welcomeSeen` false; absent at the next open and on every later frame; one
    WELCOME POST from the page."""
    w = r["welcome"]
    first, nxt = w["first_open"], w["next_open"]
    frames = list(w.get("later_frames") or [])
    posts = _posts(w.get("page_posts"))
    faults = []
    if not first.get("present"):
        faults.append("no sheet at the first open")
    if (first.get("received") or {}).get("welcomeSeen") is not False:
        faults.append({"first open received": first.get("received")})
    if nxt.get("count") != 0:
        faults.append({"sheets at the next open": nxt.get("count")})
    if not frames or any(n != 0 for n in frames):
        faults.append({"later frames' sheets": frames})
    if len(posts) != 1 or len(w.get("page_posts") or []) != 1 or posts[0].get("body") != WELCOME:
        faults.append({"page's guide-seen requests": w.get("page_posts")})
    return not faults, {"faults": faults, "frames": len(frames), "page_posts": len(w.get("page_posts") or [])}


def _skip_ok(read: dict | None) -> bool:
    read = read or {}
    return all(read.get(k) is True for k in ("visible", "enabled", "in_view", "hit"))


def only_skip(controls: list[dict]) -> tuple[bool, list]:
    """The sheet's controls are Skip (the only one with a word) and at most the face's wordless sound toggle."""
    worded = [c for c in controls if (c.get("words") or "").strip()]
    wordless = [c for c in controls if not (c.get("words") or "").strip()]
    faults = []
    if len(worded) != 1 or worded[0].get("testid") != "guide-skip" \
            or not (worded[0].get("words") or "").strip().startswith(SKIP_WORD):
        faults.append({"controls with a word": worded})
    stray = [c for c in wordless if c.get("label") not in SOUND_LABELS or c.get("tag") != "button"]
    if stray or len(wordless) > 1:
        faults.append({"wordless controls": wordless})
    return not faults, faults


def skippable_from_the_first_frame(r: dict) -> tuple[bool, Any]:
    """G2: Skip visible, enabled, in view at both sizes and the only control, before any cue; the press closes the
    sheet within 1 s."""
    w = r["welcome"]
    reads = w["skip_reads"]
    faults = []
    for size in SIZES:
        if not _skip_ok(reads.get(size)):
            faults.append({size: reads.get(size)})
    alone, control_faults = only_skip(w["controls"])
    faults += control_faults
    first = w["first_frame"]
    fired = first.get("cues_fired")
    if fired is not None and list(fired) not in ([], list(WELCOME_CUES[:1])):
        faults.append({"cues fired before the reads": fired})
    if fired is None and not float(first.get("current_time") or 0) < SECOND_CUE_AT:
        faults.append({"the video's clock at the reads": first.get("current_time")})
    gone = (w.get("press") or {}).get("gone_ms")
    if gone is None or gone > GONE_MS:
        faults.append({"gone_ms": gone})
    return not faults, {"faults": faults, "door": (w.get("press") or {}).get("door"), "gone_ms": gone}


def remembered_on_the_wire(r: dict) -> tuple[bool, Any]:
    """G3: 204 on `{what: WELCOME}`, 204 again on the repeat; `welcomeSeen` true after; revision unchanged; the next
    founder write answered on its first press."""
    w = r["welcome"]
    press = w["press"]
    faults = []
    requests = press.get("requests") or []
    if len(requests) != 1 or _posts(requests) != requests or requests[0].get("body") != WELCOME \
            or requests[0].get("status") != 204:
        faults.append({"the press's requests": requests})
    if (w.get("repeat") or {}).get("status") != 204:
        faults.append({"repeat": w.get("repeat")})
    seen = {"welcomeSeen": True, "openersSeen": []}
    if (w["next_open"].get("received") or {}) != seen:
        faults.append({"next open received": w["next_open"].get("received")})
    if w.get("wire_after") != seen:
        faults.append({"wire after": w.get("wire_after")})
    rev = w["revision"]
    if rev.get("before") is None or not rev.get("before") == rev.get("after_press") == rev.get("after_repeat"):
        faults.append({"revision": rev})
    write = w["next_write"]
    status = write.get("status")
    if not (isinstance(status, int) and 200 <= status < 300) or write.get("presses") != 1 or write.get("refused"):
        faults.append({"next write": write})
    return not faults, {"faults": faults, "revision": rev, "next_write": status}


def replay_posts_nothing(r: dict) -> tuple[bool, Any]:
    """G4: both replays open the sheet and close it with zero `guide-seen` requests."""
    x = r["replay"]
    first, second = x.get("first") or {}, x.get("second") or {}
    faults = []
    for name, one in (("first", first), ("second", second)):
        if not (one.get("opened") and one.get("closed")):
            faults.append({name: {"opened": one.get("opened"), "closed": one.get("closed")}})
        if one.get("requests"):
            faults.append({f"{name}'s guide-seen requests": one.get("requests")})
    if first.get("closed_by") != "skip" or not _skip_ok(first.get("skip")):
        faults.append({"first closed by": first.get("closed_by"), "skip": first.get("skip")})
    if not float(first.get("current_time") or 0) < REPLAY_NEAR_S:
        faults.append({"first's clock": first.get("current_time")})
    if second.get("closed_by") != "end":
        faults.append({"second closed by": second.get("closed_by")})
    if (x.get("after") or {}).get("welcomeSeen") is not True:
        faults.append({"after": x.get("after")})
    rev = x.get("revision") or {}
    if rev.get("before") is None or rev.get("before") != rev.get("after"):
        faults.append({"revision": rev})
    return not faults, {"faults": faults, "via": first.get("via")}


def cues_in_order(r: dict) -> tuple[bool, Any]:
    """G5: the twelve cues served in order, ids unique, `at` rising; each seek draws its cue and `cuesFired` grows by
    that id alone."""
    x = r["walk"]
    served = list(x.get("served") or [])
    ids = [c.get("id") for c in served]
    ats = [float(c.get("at")) for c in served]
    faults = []
    if tuple(ids) != WELCOME_CUES or len(set(ids)) != len(ids):
        faults.append({"served ids": ids})
    if any(b <= a for a, b in zip(ats, ats[1:])):
        faults.append({"served at": ats})
    before = list(x.get("before") or [])
    if before not in ([], list(WELCOME_CUES[:1])):
        faults.append({"fired before the walk": before})
    steps = list(x.get("steps") or [])
    if len(steps) != len(WELCOME_CUES):
        faults.append({"steps": len(steps)})
    previous = before
    for i, step in enumerate(steps):
        want = WELCOME_CUES[i] if i < len(WELCOME_CUES) else None
        fired = list(step.get("fired") or [])
        if step.get("id") != want or step.get("cue") != want:
            faults.append({i: {"id": step.get("id"), "drawn": step.get("cue"), "want": want}})
        if fired != list(WELCOME_CUES[:i + 1]) or len(fired) < len(previous) or len(set(fired)) != len(fired):
            faults.append({i: {"fired": fired, "before": previous}})
        previous = fired
    return not faults, {"faults": faults, "steps": len(steps)}


#: (mark id, the record key it reads, the rule). Order is the leg's.
MARKS: list[tuple[str, str, Callable[[dict], tuple[bool, Any]]]] = [
    ("G1", "welcome", once_per_project),
    ("G2", "welcome", skippable_from_the_first_frame),
    ("G3", "welcome", remembered_on_the_wire),
    ("G4", "replay", replay_posts_nothing),
    ("G5", "walk", cues_in_order),
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


def owed(record: dict) -> list[str]:
    """Every mark whose subject this record carries."""
    return [m for m, key, _ in MARKS if key in record]


def scorecard(record: dict) -> dict:
    checks = score(record)
    measured = [c for c in checks if c.measured]
    return {"version": GUIDE_MARKS_VERSION,
            "measured": len(measured), "met": sum(c.ok for c in measured),
            "unmeasured": [c.mark for c in checks if not c.measured],
            "why_unmeasured": record.get("notes") or {},
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok,
                        "detail": json.loads(json.dumps(c.detail, default=str))} for c in checks]}
