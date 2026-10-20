"""The guide marks (spec 054): keel-cloud 106's `guide-seen` (contract 20) and keel-web 080's welcome sheet, held over
one journey's record -- deterministic, zero spend, the shape of `evals/interviewer_marks.py` (one check a rule; a mark
whose subject the record does not carry is **unmeasured** -- reported, never passed).

Design of record: keel-cloud-docs `canon/designs/onboarding-videos-design-2026-10-17.md` §5 (the files are keel-web's
own `public/guide/`, the phone at 390 x 844), §7.1 (the welcome's twelve cues) and §8 D24 (the welcome at the start of
every project, once, Skip always visible and the only control). G1-G5 are the welcome's (spec 054); the teaching
videos' G6-G12 follow below (spec 057).

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

**Spec 057 (keel-web 086, keel-cloud 109, contract 22; design §15 D42-D49): the teaching videos, G6-G12.** Only the
clips keel-web's `public/guide/manifest.json` says are `present` are owed: a mark whose clips are all absent **passes as
not applicable** (`Check.applicable` False, listed under the card's `not_applicable`), and where it can, still holds
that an absent clip drew nothing (086 FR-1: no pill, no sheet). A missing render never turns a mark red.

- **G6 the report sheet plays once** (`report`, D44): `report-read` in the sheet at the report's first open over an
  overview that said `reportSeen: false`; Skip posts `{report: true}` once, 204; the wire says `reportSeen: true` after;
  no sheet at the next open nor at any later read of the report.
- **G7 the Overview's pills** (`overview`, D45): *How to read this* (`report-read`) at every read; *When a line fails*
  (`report-fails`) only while the wire has a line NOT_HOLDING_UP or PEOPLE_DISAGREE, `fresh` until `lineFailedSeen`;
  where it was watched to its end (local: the seam), one `{lineFailed: true}` 204 and the dot gone after.
- **G8 the stage band plays two chapters** (`stages`, D46): on each stage page whose two chapters are present, the pill
  opens one band whose chip reads *1 of 2*, then (the seam's seek past chapter 1's end; local only) *2 of 2*, each
  chapter's face on its own clip.
- **G9 the money pair** (`stages`, D47): Will they pay's chapters are `stage-money-b2c-1/2` on a consumer project and
  `stage-money-b2b-1/2` on a business one -- as the band plays them.
- **G10 an explainer under every question** (`explainers`, D27): each calibration question whose `explain-<slug>` is
  present draws its pill (absent: none), *Your idea* (S2) among them; on each stage's first question whose explainer
  is present the band is opened: it hides the question's fields and disables the card's primary while open, and Skip
  gives both back as they were (the primary is already off before an answer is picked, so the fields carry the proof).
- **G11 the openers once per stage** (`openers`, D25): each present opener in the sheet at its stage's first open, Skip
  posting `{what: OPENER, stage}` once, 204; `openersSeen` fills in Vector order (PROBLEM, SOLUTION, COMMERCIAL) with
  exactly the present ones; no opener over any later corridor frame.
- **G12 no project word** (`captions`, D42): no served `/guide/<key>.vtt` of a present clip, and no snippet text the
  journey read, contains `night|baby|cry|parent|payroll|chocolate|lullaby` (as words: *described* is not *cry*).

G4 and G5 are measured once per matrix, on S-005's local journey; every other journey and the remote profile carry no
`replay` or `walk`, so the card reports them **unmeasured** and the record's `notes` say why (`REMOTE_WHY` /
`ELSEWHERE_WHY`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

#: Bumped whenever a mark is born, retired, or reads its record differently.
#: v1 (spec 054, keel-cloud 106 / keel-web 080, contract 20): G1 (once per project), G2 (skippable from the first
#: frame), G3 (seen is remembered on the wire), G4 (replay posts nothing) and G5 (the cues fire in order) born -- the
#: welcome only; `openers` and `explainers` are reserved for the specs that build D25 and D26 / D27 (G6 on).
#: v2 (spec 057, keel-web 086 / keel-cloud 109, contract 22): G6 (the report sheet once), G7 (the Overview's two pills),
#: G8 (two chapters on a stage band), G9 (the money pair by kind), G10 (an explainer under every question), G11 (the
#: openers once per stage, in Vector order) and G12 (no project word in a caption or snippet) born, each passing as
#: not applicable where the manifest says its clips are absent; G3 reads `welcomeSeen` / `openersSeen` alone (contract
#: 22's guide carries two more flags).
GUIDE_MARKS_VERSION = 2

#: keel-web 081 FR-2 / design §7.1 v2: the welcome's fourteen cues, in the order they play (`welcome.cues.json`'s
#: ids); 080's twelve gained `contacts` and `interviewer-clip` after `phone-interview` (the founder, 2026-10-18).
WELCOME_CUES = ("wordmark", "three-questions", "three-chips", "thirteen-dots", "phone-interview", "contacts",
                "interviewer-clip", "report", "rows-hold", "quote", "price-pilot", "promise", "explainer-pill", "start")
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
    #: Spec 057: False where every clip the mark reads is absent from the manifest -- it passes as not applicable.
    applicable: bool = True


def _welcome_flags(guide: dict | None) -> dict | None:
    """The two flags G3 holds (contract 22's guide also carries `reportSeen` and `lineFailedSeen`)."""
    if not isinstance(guide, dict):
        return guide
    return {k: guide.get(k) for k in ("welcomeSeen", "openersSeen")}


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
    if _welcome_flags(w["next_open"].get("received")) != seen:
        faults.append({"next open received": w["next_open"].get("received")})
    if _welcome_flags(w.get("wire_after")) != seen:
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
    """G5: the fourteen cues served in order, ids unique, `at` rising; each seek draws its cue and `cuesFired` grows by
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


# ---------------------------------------------------------------------------- spec 057: the teaching videos

#: keel-cloud 109's `guide-seen` bodies for the report and the line-failed video (sent exactly so, keel-web 086 FR-6).
REPORT = {"report": True}
LINE_FAILED = {"lineFailed": True}
#: The statuses that make a line failed (keel-web 086 FR-6).
FAILING = ("NOT_HOLDING_UP", "PEOPLE_DISAGREE")
#: The Vector order `openersSeen` fills in (D25).
VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")
OPENERS = {"PROBLEM": "opener-the-problem", "SOLUTION": "opener-your-solution", "COMMERCIAL": "opener-will-they-pay"}
#: Each stage page's two chapters (086 FR-7); Will they pay's by the project's kind (D47).
STAGE_CHAPTERS = {"PROBLEM": ("stage-problem-1", "stage-problem-2"),
                  "SOLUTION": ("stage-solution-1", "stage-solution-2")}
MONEY_CHAPTERS = {True: ("stage-money-b2b-1", "stage-money-b2b-2"), False: ("stage-money-b2c-1", "stage-money-b2c-2")}
#: Each calibration question's explainer clip (086 FR-5, clips.json's keys); Ability to pay has no screen.
EXPLAINERS = {"problem.prevalence": "explain-prevalence", "problem.frequency": "explain-frequency",
              "problem.importance": "explain-importance",
              "problem.current_solution_satisfaction": "explain-current-solution",
              "solution.compatibility": "explain-compatibility",
              "solution.relative_advantage": "explain-relative-advantage",
              "solution.adoption_friction": "explain-adoption-friction",
              "commercial.existing_sacrifice": "explain-existing-sacrifice", "commercial.price": "explain-price",
              "commercial.buyer_payer_alignment": "explain-buyer-and-payer",
              "commercial.purchase_friction": "explain-purchase-friction",
              "commercial.commitment": "explain-commitment",
              # S2, the idea's screen (*Your idea*, not a dimension: the solution's first screen, 086 FR-5)
              "idea": "explain-your-idea"}
#: The pills' words (086 FR-4 / FR-10), the fallback where a pill carries no `data-clip`.
PILL_WORDS = {"report-read": "How to read this", "report-fails": "When a line fails",
              "stage": "How to read these charts", "explain": "Hear this one"}
#: D42 / 086 FR-10: no project word in a caption or a snippet. As words, plurals and -ing forms included.
PROJECT_WORDS = re.compile(r"\b(nights?|bab(?:y|ies)|cr(?:y|ies|ied|ying)|parents?|parenting|payroll|"
                           r"chocolates?|lullab(?:y|ies))\b", re.IGNORECASE)
#: Why a part of a mark is not run on the remote profile (no `__keelGuide` in the production build).
REMOTE_SEAM_WHY = ("staging serves keel-web's production build, which has no window.__keelGuide: chapter 2's chip (G8) "
                   "and the line-failed video's end (G7) are not run on the remote profile")

NOT_APPLICABLE = None


def project_words(text: str | None) -> list[str]:
    """Every project word in `text` (D42), as found."""
    return [m.group(0) for m in PROJECT_WORDS.finditer(text or "")]


def is_pill(pill: Any, key: str) -> bool:
    """The pill read is `key`'s: by `data-clip`, else by its words (`PILL_WORDS`; explainers and stages by family)."""
    if isinstance(pill, str):
        pill = {"clip": pill if pill.startswith(("report-", "stage-", "explain-", "opener-")) else None,
                "words": pill}
    pill = pill or {}
    if pill.get("clip"):
        return pill["clip"] == key
    family = key if key in PILL_WORDS else key.split("-", 1)[0]
    if pill.get("testid"):
        # keel-web 086 `GuidePlacement`: `guide-pill-{id}`, the id `report-read`, `report-fails`, `stage` or `explain`
        return pill["testid"] == f"guide-pill-{family}"
    words = PILL_WORDS.get(family)
    if not (words and str(pill.get("words") or "").startswith(words)):
        return False
    # 086's pills carry no clip key: *How to read this* is not *How to read these charts*
    return not (family == "report-read" and str(pill.get("words")).startswith(PILL_WORDS["stage"]))


def _one_post(requests: list[dict] | None, body: dict) -> bool:
    requests = list(requests or [])
    return len(requests) == 1 and _posts(requests) == requests and requests[0].get("body") == body \
        and requests[0].get("status") == 204


def report_sheet_once(r: dict) -> tuple[bool | None, Any]:
    """G6: the report sheet once, `{report: true}` posted, `reportSeen` remembered."""
    x = r["report"]
    first = x.get("first_open") or {}
    if not x.get("applicable"):
        ok = not first.get("present") and not any(x.get("later") or [])
        return (NOT_APPLICABLE if ok else False), {"report-read": "absent", "sheets": x.get("later")}
    faults = []
    if not first.get("present"):
        faults.append("no report sheet at the report's first open")
    if (first.get("received") or {}).get("reportSeen") is not False:
        faults.append({"first open received": first.get("received")})
    if "report-read" not in str(first.get("src") or ""):
        faults.append({"the sheet's clip": first.get("src")})
    press = x.get("press") or {}
    if not _one_post(press.get("requests"), REPORT) or press.get("gone_ms") is None:
        faults.append({"press": press})
    if (x.get("wire_after") or {}).get("reportSeen") is not True:
        faults.append({"wire after": x.get("wire_after")})
    nxt = x.get("next_open") or {}
    if nxt.get("count") != 0 or (nxt.get("received") or {}).get("reportSeen") is not True:
        faults.append({"next open": nxt})
    later = list(x.get("later") or [])
    if any(n != 0 for n in later):
        faults.append({"later reads' sheets": later})
    return not faults, {"faults": faults, "later": len(later)}


def overview_pills(r: dict) -> tuple[bool | None, Any]:
    """G7: *How to read this* always; *When a line fails* only with a failed line, fresh until watched."""
    x = r["overview"]
    read_on, fails_on = bool(x.get("read_present")), bool(x.get("fails_present"))
    faults = []
    for i, one in enumerate(x.get("reads") or []):
        pills = list(one.get("pills") or [])
        reads = [p for p in pills if is_pill(p, "report-read")]
        fails = [p for p in pills if is_pill(p, "report-fails")]
        if len(reads) != (1 if read_on else 0):
            faults.append({i: {"How to read this": reads, "present": read_on}})
        want = 1 if (fails_on and one.get("failing")) else 0
        if len(fails) != want:
            faults.append({i: {"When a line fails": fails, "failing": one.get("failing"), "present": fails_on}})
        elif want and bool(fails[0].get("fresh")) != (one.get("lineFailedSeen") is not True):
            faults.append({i: {"fresh": fails[0].get("fresh"), "lineFailedSeen": one.get("lineFailedSeen")}})
    watched = x.get("watched")
    if watched:
        if not _one_post(watched.get("requests"), LINE_FAILED):
            faults.append({"watched posted": watched.get("requests")})
        if watched.get("fresh_after") is not False or (watched.get("wire_after") or {}).get("lineFailedSeen") \
                is not True:
            faults.append({"after watching": watched})
    if not (read_on or fails_on):
        return (NOT_APPLICABLE if not faults else False), {"report-read": "absent", "report-fails": "absent",
                                                          "faults": faults}
    return not faults, {"faults": faults, "reads": len(x.get("reads") or []), "watched": bool(watched)}


def _chapters_ok(one: dict, keys: tuple) -> list:
    faults = []
    if not one.get("opened"):
        faults.append("the pill opened no band")
        return faults
    if "1 of 2" not in str(one.get("chip_first") or ""):
        faults.append({"chip first": one.get("chip_first")})
    if keys[0] not in str(one.get("src_first") or ""):
        faults.append({"chapter 1 plays": one.get("src_first"), "want": keys[0]})
    if one.get("seam"):
        if "2 of 2" not in str(one.get("chip_second") or ""):
            faults.append({"chip second": one.get("chip_second")})
        if keys[1] not in str(one.get("src_second") or ""):
            faults.append({"chapter 2 plays": one.get("src_second"), "want": keys[1]})
    if not one.get("closed"):
        faults.append("the band did not close on Skip")
    return faults


def stage_two_chapters(r: dict) -> tuple[bool | None, Any]:
    """G8: each stage band with both chapters present plays them, the chip 1 of 2 then 2 of 2."""
    x = r["stages"]
    faults, measured = [], []
    for vector, one in x.items():
        if not one.get("applicable"):
            continue
        measured.append(vector)
        faults += [{vector: f} for f in _chapters_ok(one, tuple(one.get("chapters") or ()))]
    if not measured:
        return NOT_APPLICABLE, {"absent": {v: one.get("chapters") for v, one in x.items()}}
    return not faults, {"faults": faults, "stages": measured}


def money_pair(r: dict) -> tuple[bool | None, Any]:
    """G9: Will they pay's chapters are the consumer pair on a consumer project, the business pair on a business one."""
    one = r["stages"].get("COMMERCIAL") or {}
    want = MONEY_CHAPTERS[bool(one.get("b2b"))]
    if not one.get("applicable"):
        return NOT_APPLICABLE, {"absent": list(want)}
    faults = []
    if tuple(one.get("chapters") or ()) != want:
        faults.append({"chapters": one.get("chapters"), "want": list(want)})
    faults += _chapters_ok(one, want)
    return not faults, {"faults": faults, "b2b": bool(one.get("b2b")), "pair": list(want)}


def explainer_under_every_question(r: dict) -> tuple[bool | None, Any]:
    """G10: a present explainer's pill under its question (an absent one's none); its band disables the primary."""
    x = r["explainers"]
    faults, present = [], []
    for key, q in (x.get("questions") or {}).items():
        clip = q.get("clip") or EXPLAINERS.get(key)
        drawn = [p for p in q.get("pills") or [] if clip and is_pill(p, clip)]
        if q.get("present"):
            present.append(key)
        if len(drawn) != (1 if q.get("present") else 0):
            faults.append({key: {"pills": q.get("pills"), "present": q.get("present")}})
    bands = x.get("bands") or {}
    for vector in x.get("owed_bands") or []:
        band = bands.get(vector)
        if not band or not band.get("opened") or not band.get("closed") or band.get("disabled_open") is not True \
                or band.get("disabled_after") != band.get("disabled_before") \
                or band.get("fields_open") != 0 or not (band.get("fields_before") or 0) > 0 \
                or band.get("fields_after") != band.get("fields_before"):
            faults.append({vector: band or "no band opened on the stage's first question"})
    if not present:
        return (NOT_APPLICABLE if not faults else False), {"absent": len(x.get("questions") or {}), "faults": faults}
    return not faults, {"faults": faults, "present": present, "bands": sorted(bands)}


def openers_once(r: dict) -> tuple[bool | None, Any]:
    """G11: each present opener once at its stage's first open, `{what: OPENER, stage}` posted, `openersSeen` in order."""
    x = r["openers"]
    stages = x.get("stages") or {}
    faults, present = [], [v for v in VECTORS if (stages.get(v) or {}).get("present")]
    for vector in VECTORS:
        one = stages.get(vector) or {}
        if one.get("present"):
            if not one.get("shown"):
                faults.append({vector: "no opener at the stage's first open"})
            elif not _one_post((one.get("press") or {}).get("requests"), {"what": "OPENER", "stage": vector}):
                faults.append({vector: one.get("press")})
        elif one.get("shown"):
            faults.append({vector: "an opener whose clip is absent was shown"})
    if list(x.get("final") or []) != present:
        faults.append({"openersSeen": x.get("final"), "want": present})
    later = list(x.get("later") or [])
    if any(n for n in later):
        faults.append({"openers over later frames": later})
    if not present:
        return (NOT_APPLICABLE if not faults else False), {"absent": list(OPENERS.values()), "faults": faults}
    return not faults, {"faults": faults, "present": present}


def no_project_word(r: dict) -> tuple[bool | None, Any]:
    """G12: no caption of a present clip and no snippet text read carries a project word."""
    x = r["captions"]
    clips = x.get("clips") or {}
    faults = []
    for key, one in clips.items():
        found = one.get("words") if "words" in one else project_words(one.get("text"))
        if not one.get("served"):
            faults.append({key: "its vtt is not served"})
        elif found:
            faults.append({key: found})
    for text in x.get("snippets") or []:
        if project_words(text):
            faults.append({"snippet": text, "words": project_words(text)})
    if not clips:
        return (NOT_APPLICABLE if not faults else False), {"present": [], "faults": faults}
    return not faults, {"faults": faults, "clips": sorted(clips), "snippets": len(x.get("snippets") or [])}


#: (mark id, the record key it reads, the rule). Order is the leg's.
MARKS: list[tuple[str, str, Callable[[dict], tuple[bool, Any]]]] = [
    ("G1", "welcome", once_per_project),
    ("G2", "welcome", skippable_from_the_first_frame),
    ("G3", "welcome", remembered_on_the_wire),
    ("G4", "replay", replay_posts_nothing),
    ("G5", "walk", cues_in_order),
    ("G6", "report", report_sheet_once),
    ("G7", "overview", overview_pills),
    ("G8", "stages", stage_two_chapters),
    ("G9", "stages", money_pair),
    ("G10", "explainers", explainer_under_every_question),
    ("G11", "openers", openers_once),
    ("G12", "captions", no_project_word),
]
#: Spec 057 FR-3: each new mark's design ids (design §15).
DESIGN_IDS = {"G6": "D44", "G7": "D45", "G8": "D43 D46", "G9": "D47", "G10": "D27", "G11": "D25", "G12": "D42 D48"}


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
        if ok is NOT_APPLICABLE:
            checks.append(Check(mark, doc, measured=True, ok=True, detail=detail, applicable=False))
            continue
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
            "not_applicable": [c.mark for c in checks if c.measured and not c.applicable],
            "why_unmeasured": record.get("notes") or {},
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok,
                        "applicable": c.applicable,
                        "detail": json.loads(json.dumps(c.detail, default=str))} for c in checks]}
