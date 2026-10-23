"""S-005, S-006 and S-007's whole body: the corpus journeys, as **vectors** journeys (spec 039; spec 041:
corpus revision 10, contract 13, keel-web 063's founder screens and 064's stranger's screens; spec 042: corpus
revision 11, contract 14 -- one RESPONDENT_QUESTIONS job a lock, the founder's name for the idea).

**The entry id is the only thing that differs between the three scenario modules** (spec 010
FR-015, kept): if `01-countly` needed one special case here, `05-paidly` would need two.

What the scenario does, in the founder's own order, one function per leg so a later spec can change
one leg and leave the others alone:

1. `leg_project`   -- the project on the entry's own market.
1b. `leg_welcome`  -- (spec 054, keel-cloud 106 / keel-web 080, design D24) the guide's welcome at the first open:
                      up over an overview saying `welcomeSeen: false`, playing muted with captions, Skip the one
                      control and in view at 1280 x 720 and 390 x 844; Skip (Escape on S-005) closes it and posts
                      `guide-seen {what: WELCOME}` once, 204, the revision unmoved; the next open has none and the
                      wire says `welcomeSeen: true`; on S-005 local the twelve cues walked through the seam and *Play
                      the welcome again* twice, posting nothing. Scored by the guide marks (`evals/guide_marks.py`).
2. `leg_context`   -- the four context fields and the entry's own recall window (D13: at least two);
                      CONTEXT_INTERPRET; *Yes, that's it*.
3. `leg_interpret_problem` -- the problem seed and PROBLEM_INTERPRET's card.
4. `leg_calibrate` -- one stage at a time, one dimension a screen (keel-web 063): Prevalence, Frequency,
                      the cost and the price on one screen each; every list dimension's *Answer* (the
                      founder's words, which Keel drafts the list from), *Check and save* and, where it
                      picks, *Choose*; each screen's counter, dots and locked nav; the stored lists and the
                      review on the wire.
5. `leg_interpret_solution` -- the solution seed, SOLUTION_MECHANISM's card, and **the idea as the
                      solution's first question**: S2, the three lines checked (one entry's founder
                      names the idea there, keel-cloud 090), Save approving them.
6. `leg_persona`   -- who decides; on a B2B entry the decision-maker's respondent type.
7. `leg_lock`      -- step 5's two screens, *Lock and write the questions*; ONE RESPONDENT_QUESTIONS job
                      (keel-cloud 091: part 1; parts 2 and 3 code's); READY; the lock stores every saved
                      list and its picked index (D7).
8. `leg_invite`    -- one link per corpus person: the primary link, or on a B2B entry the
                      decision-maker's commercial link.
9. `leg_interview` -- each person in their own browser context, no founder session, through keel-web
                      064's screens: the decision-maker's idea screen first, the gate (its one chip), every
                      item as served (one escape, last), two picks on Importance, the fixed answers,
                      "nothing" typed as 0; the idea card and the Relative advantage question on the
                      idea's current name (keel-cloud 090); the founder reads after each person.
10. `leg_standings` -- `GET standings` against the entry's `expected.standings` and `expected.vector_verdicts`
                      (codes mapped onto the wire's), then the report's Overview (keel-web 077) and the three
                      stage pages, one row's per-person list and every rung's *One last thing* line among them.
11. `leg_report`   -- the report on the wire (keel-cloud 104, spec 052): a card per dimension equal to the
                      eval's own reading of the entry (`instructions/brief_facts.py`, which the DRY compare
                      holds equal to keel-cloud's), what broke, the pilot and the price median; then keel-web
                      077's three views -- Overview, Insights, Pilot -- and *Download the brief*, their binding,
                      scored by the five report marks (`evals/report_marks.py`).
12. `leg_one_currency` -- (spec 053, design D19) no pound or euro on any page the journey drew, the
                      three views and the binding included (`OTHER_CURRENCIES`, S-007's sweep made every
                      journey's), and the project's market the entry's own: since revision 12 the US, en-US,
                      its region.

After them each scenario's `extra` runs: S-006's ends with **the contacts leg** (spec 043, keel-cloud 093,
`evals/contacts_leg.py`) on the wire, and S-005's with the B2C `NOT_B2B` refusal.

Every inference job is answered by keel-runtime's **scripted** executor from the entry's own stored
texts (`harness/vectors_script.py`); no model runs anywhere in this file (`evals/policy.py`).

It lives in `evals/` and not in `harness/` because it asserts. `harness/` is machinery.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from evals import corpus_facts
from evals import feedback_marks
from evals import guide_marks
from evals import report_marks
from evals.preludes import create_project, own_ai_door
from harness import interviewer_fake as fake
from harness import vectors_script as vs
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv_screens
from harness import vectors_screens as vs_screens
from harness.browser import Auth, Connect, Landing
from harness.connect import start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from instructions import chain as chain_mod
from instructions import brief_facts as brief_facts_mod
from instructions import contract as contract_mod
from stack import remote
from stack import runtime as stack_runtime

VECTORS = vs.VECTORS

#: keel-web's own words for a status (`translate.ts` `standingStatus`), named once here so the
#: three scenarios cannot drift apart on what *not holding up* is spelled like.
STATUS_WORD = {
    "HOLDING_UP": "Holding up",
    "NOT_HOLDING_UP": "Not holding up",
    "PEOPLE_DISAGREE": "People disagree",
    "TOO_FEW_TO_CALL": "Too few to call",
    "NOT_ASKED_YET": "Not asked yet",
    "LEFT_OUT": "Left out",
    "NOT_TESTED": "Not tested",
}

#: keel-web `VECTOR_WORD`, the counter's first word (*Problem · 3 of 4*).
STAGE_WORD = {"PROBLEM": "Problem", "SOLUTION": "Solution", "COMMERCIAL": "Commercial"}
#: keel-web 063 FR-003: the idea counts as Solution's first question and who decides as Commercial's.
STAGE_OFFSET = {"PROBLEM": 0, "SOLUTION": 1, "COMMERCIAL": 1}
#: keel-web `KEEL_TEST_PENDING`: the *Keel will test* box on a Choose screen before the pick.
KEEL_TEST_PENDING = "Pick one and the test appears here."
#: Where Keel sets the bar (design D4), the Check screen shows the belief (keel-web 063 FR-005).
KEEL_SET = {"problem.importance", "problem.current_solution_satisfaction", "solution.relative_advantage",
            "commercial.commitment"}

#: The settled and the refused ends of an interaction (keel-cloud `InteractionStatus`).
TERMINAL_BAD = {"RESULT_INVALID", "DOMAIN_REFUSED", "STATE_CONFLICT", "JOB_FAILED", "APPLY_ERROR",
                "ABANDONED"}

#: The count keys `expected.standings` may carry and the wire's own place for each
#: (`DimensionStanding.interval` / `.choice`, `n` on the row).
INTERVAL_KEYS = ("inside", "below", "above")

#: The controls whose served options the item screen draws as rows (keel-web 064 FR-003).
ROW_CONTROLS = {"single_choice", "single_choice_5", "price_ladder", "fixed_four", "fixed_three", "pick_two"}


# ------------------------------------------------------------------------------------ the journey

@dataclass
class Journey:
    """What every leg reads and writes: the recorder, the founder's page and its wire, the entry and
    its typed inputs, and what earlier legs learned (the project id, each person's token)."""
    recorder: Recorder
    page: Any
    context: Any
    web_base: str
    cloud_base: str
    entry: Any
    founder: vs.FounderInputs
    people: list
    script: vs.GeneratedScript | None = None
    browser: Any = None
    #: keel-cloud's exported registry (the run's own `export/`), which the brief's cards are read over.
    registry: Any = None
    project_id: str = ""
    tokens: dict = field(default_factory=dict)       # person -> token
    links: dict = field(default_factory=dict)        # person -> the link the founder sends
    corridor: Any = None
    answers: Any = None
    interviews: dict = field(default_factory=dict)   # person -> the interview the wire served
    walked: dict = field(default_factory=dict)       # person -> what their screens drew
    screens: dict = field(default_factory=dict)      # what the answer pages drew, by page
    framing: dict = field(default_factory=dict)      # dimension -> what its founder screens drew
    #: True on the three scripted corpus journeys: every model answer is the corpus's, so every
    #: screen and every standing is held to the entry. False on S-012, where a host's model writes
    #: the corridor: the same legs run, the same screens are held to the same wire, and nothing is
    #: held to the corpus's own words or counts (spec 016 FR-007's rule, kept).
    strict: bool = True
    #: How many times longer a wait on a model may take: 1 on the scripted journeys, more on S-012.
    patience: float = 1.0
    standings: dict = field(default_factory=dict)    # the last GET standings
    #: The idea's name every later question uses, as the wire stored it after S2 (`IdeaView.shortName`, keel-cloud 090).
    idea_name: str = ""
    #: The lock's receipt (`LockReceipt`), as keel-web received it from `POST lock`.
    receipt: dict = field(default_factory=dict)
    #: The stack and the identity the founder signed in as (spec 043: the contacts leg reads the ledger and stands the
    #: founder on Keel's door, `stack/ledger.py`). None on S-012, which never runs that leg.
    stack: Any = None
    founder_identity: Any = None
    #: Spec 046: the record `evals/feedback_marks.py` scores at the end of the journey (FM1-FM6).
    feedback: dict = field(default_factory=dict)
    #: Spec 052: the report marks' scorecard `_score_report` wrote (`report-marks.json`).
    report_card: dict = field(default_factory=dict)
    #: Spec 051: each text walk's follow-up (the harness's own rung, the route's answer, the screen, what was sent) and
    #: the story's box where it was spoken -- the interviewer marks read them (IM23, IM24, IM26).
    follow_ups: dict = field(default_factory=dict)
    speak: dict = field(default_factory=dict)
    #: Spec 054 FR-6: True on the corpus journeys (`run()` sets it): *Start* leaves keel-web 080's welcome up for
    #: `leg_welcome` to judge. False (S-012, every prelude): `MarketStep.start` passes it by.
    hold_welcome: bool = False
    #: Spec 054: the record `evals/guide_marks.py` scores (`welcome`, and on S-005 local `walk` and `replay`).
    guide: dict = field(default_factory=dict)
    #: Spec 054: what the founder's page sent and received about the guide, from *Start* to the context Save
    #: (`vs_screens.GuideWire`); detached after, so later legs pay nothing.
    guide_wire: Any = None
    #: Spec 057: keel-web 086's teaching videos (`vs_screens.GuideTeaching`), set by `run()` after the welcome; None
    #: elsewhere (S-012, the preludes), where every teaching read below is skipped.
    teach: Any = None
    #: Spec 062 FR-3: the back-test's camera (`evals/backtest.Camera`) -- a full-page screenshot of every founder screen
    #: as it is about to be answered and of every respondent screen on one person a link. None everywhere else.
    camera: Any = None
    #: Spec 062 FR-2: True when the founder signed up through keel-web's /signup and every job runs on Keel's AI (the
    #: back-test). The few own-door facts the corridor legs assert -- L1's one line, the greyed formats -- are read as
    #: Keel's door draws them instead. False on every other journey that calls these legs.
    keels_door: bool = False
    #: Spec 062: how many times a failed model job may be retried the way the founder's screen retries it (`POST
    #: calibration/{vector}/retry`, `POST questionnaire/retry`) -- 0 everywhere but the back-test, where a live model's
    #: refused result is a finding to record and step past, not the end of the walk. Every one is kept in `findings`.
    retries: int = 0
    findings: list = field(default_factory=list)
    #: Spec 064 (judgement call): a golden number the new build moved -- a standing, a count, a verdict, a card -- is
    #: a finding named with the served words beside the corpus's; it is recorded where it is read and the journey goes
    #: on, so one run names every one; `run` fails at the end on any (`deferred`).
    deferred: list = field(default_factory=list)

    # --------------------------------------------------------------------------- the wire

    def call(self, method: str, path: str, body: dict | None = None, *,
             ok: tuple = (200, 201, 202, 204)) -> tuple[int, Any]:
        url = f"{self.cloud_base}{path}"
        kwargs: dict = {"timeout": 20_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = self.context.request.fetch(url, method=method, **kwargs)
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001 - an empty 204 or a non-JSON error page
            payload = response.text()
        if response.status not in ok:
            raise AssertionError(f"{method} {path} answered {response.status}: {payload}")
        return response.status, payload

    def get(self, path: str) -> Any:
        return self.call("GET", path)[1]

    def project(self, suffix: str) -> str:
        return f"/v2/projects/{self.project_id}{suffix}"

    def revision(self) -> int:
        """The project's current revision, off the overview read every corridor write is held to."""
        return int((self.get(self.project("/overview")) or {}).get("revision") or 0)

    def wait_interaction(self, interaction_id: str, want: set, *, timeout_s: float = 90) -> dict:
        deadline = time.monotonic() + timeout_s
        last: dict = {}
        while time.monotonic() < deadline:
            last = self.get(f"/v2/inference-interactions/{interaction_id}") or {}
            status = last.get("status")
            if status in want:
                return last
            if status in TERMINAL_BAD:
                raise AssertionError(
                    f"interaction {interaction_id} ({last.get('screen')}) ended {status}: "
                    f"{last.get('diagnostic') or last.get('refusal')}")
            time.sleep(0.5)
        raise AssertionError(f"interaction {interaction_id} never reached {sorted(want)}: {last}")


def open_journey(recorder: Recorder, page, context, browser, stack, entry, founder, people, *,
                 script: vs.GeneratedScript | None = None, strict: bool = True,
                 patience: float = 1.0, registry=None) -> Journey:
    """One journey on one founder page: the legs below read and write it. S-005/6/7 open it strict
    on their scripted runtime; S-012 opens it with `strict=False` on a host's live model."""
    return Journey(recorder=recorder, page=page, context=context, web_base=stack.web_base_url,
                   cloud_base=stack.cloud_base_url, entry=entry, founder=founder, people=people,
                   script=script, browser=browser, strict=strict, patience=patience, registry=registry,
                   corridor=vs_screens.Corridor(page, recorder, stack.web_base_url, patience=patience),
                   answers=vs_screens.Answers(page, recorder, stack.web_base_url))


def _step(j: Journey, name: str, *, party: str = "stack", kind: str = "assert"):
    return j.recorder.step(name, party=party, kind=kind)


# ------------------------------------------------------------------------------- leg 1: context

def leg_project(j: Journey) -> None:
    """The project, on the landing's own name and market steps, on the entry's market."""
    founder = j.founder
    if j.hold_welcome:
        j.guide_wire = vs_screens.GuideWire(j.page).attach()
    j.project_id = create_project(j.page, j.recorder, j.web_base, _market_inputs(founder),
                                  welcome="hold" if j.hold_welcome else "pass",
                                  camera=j.camera.founder if getattr(j, "camera", None) is not None else None)
    with _step(j, "the market step's list is keel-cloud's (122 FR-4, `GET /v2/markets`): the entry's country is one "
                  "of `markets` -- or, for a country the table has not met, `other` offers it with its currency") as h:
        listed = j.get("/v2/markets") or {}
        countries = [m.get("country") for m in listed.get("markets") or []]
        other = [c.get("code") for c in (listed.get("other") or {}).get("countries") or []]
        h.record_wire({"GET": "/v2/markets", "country": founder.country},
                      {"markets": countries, "other": len(other), "kind": (listed.get("other") or {}).get("kind")})
        assert founder.country in countries or founder.country in other, (founder.country, countries)
    with _step(j, f"{j.entry.id}: the market is the one the entry names") as h:
        market = (j.get(j.project("/overview")) or {}).get("market") or {}
        h.record_assert({"country": founder.country, "region": founder.region,
                         "language": founder.language}, market)
        assert market.get("country") == founder.country, market
        assert (market.get("region") or None) == founder.region, market
        assert market.get("language") == founder.language, market
        # keel-cloud 122: `kind` is OTHER only on a market the table has not met; every corpus market is the table's
        assert market.get("kind") in (None, "OTHER") and (market.get("kind") == "OTHER") == (
            founder.country not in countries), market


def leg_context(j: Journey) -> None:
    """The context step: the four fields and the entry's own recall window, one CONTEXT_INTERPRET
    job, and *Yes, that's it*. Asserted on the card and on the wire: the sentence Keel understood
    (the entry's own `context.understood` on a scripted journey), and the four fields and the window
    the founder typed -- a window of at least two units (D13)."""
    founder = j.founder
    drawn = j.corridor.context(j.project_id, founder.context_fields, founder.window.as_wire())
    if j.guide_wire is not None:
        _next_write_after_the_welcome(j)
    with _step(j, "the card says what Keel understood -- code's sentence since keel-cloud 122, assembled from the slots "
                  "(the segment and its condition, the circumstance, the job, the window) -- and, where the segment "
                  "carries a condition, *Only people who: ...* (keel-web 096)", party="founder") as h:
        want = vs.read_back(j.entry) if j.strict else "a sentence"
        window_line = j.corridor.context_window_line()
        lines = j.corridor.context_lines()
        condition = vs.segment_of(j.entry)["condition"]
        want_lines = {"only_people_who": f"Only people who: {condition}." if condition else None}
        h.record_assert({"understands": want, "window": vs.window_words(founder.window), **want_lines},
                        {"understands": drawn, "window": window_line, **lines})
        assert drawn.strip(), "the context card drew no sentence"
        if j.strict:
            assert drawn == want, {"served": drawn, "assembled": want}
            assert lines.get("only_people_who") == want_lines["only_people_who"], lines
        assert vs.window_words(founder.window) in window_line, window_line
        j.screens["context_card"] = {"understands": drawn, "text": drawn, **lines}
    j.corridor.confirm_context()
    with _step(j, "the context is confirmed on the wire: the four fields, the sentence, the window "
                  "of at least two (D13)") as h:
        view = j.get(j.project("/context")) or {}
        fields = view.get("fields") or {}
        h.record_assert({**founder.context_fields, "recallWindow": founder.window.as_wire(),
                         "understands": drawn}, view)
        assert view.get("state") == "CONFIRMED", view
        assert view.get("understands") == drawn, (view.get("understands"), drawn)
        assert fields.get("recallWindow") == founder.window.as_wire(), fields
        assert int((fields.get("recallWindow") or {}).get("count") or 0) >= 2, fields
        for key, value in founder.context_fields.items():
            assert fields.get(key) == value, (key, fields)


def _market_inputs(founder: vs.FounderInputs):
    """`evals/preludes.create_project` reads a classic `FounderInputs`; this is the slice of one
    it touches -- the name and the market -- and nothing else."""
    from types import SimpleNamespace
    return SimpleNamespace(project_name=founder.project_name,
                           market=SimpleNamespace(country=founder.country, region=founder.region,
                                                  language=founder.language))


# ------------------------------------------------------------------------- leg 1b: the welcome

#: Spec 054 FR-5: `leg_welcome` adds at most this much to a journey (the sheet seen to the next open's absence read,
#: Skip at once; the cue walk excluded).
WELCOME_BUDGET_S = 5.0
#: Spec 054 FR-2 b: the two sizes Skip is read at -- the harness's window (no context passes a viewport, so
#: Playwright's default) and the phone (design §5).
WELCOME_SIZES = {"1280x720": {"width": 1280, "height": 720}, "390x844": {"width": 390, "height": 844}}
#: `HTMLMediaElement.error.code` 4 (the source cannot be played): Playwright's bundled Chromium (`evals/conftest.py`)
#: does not decode H.264, so the face may never play there -- a note, never a failure or a DRIFT (054 judgement call 1).
MEDIA_ERR_NO_DECODE = 4
#: keel-web 080's welcome is 86 s; the replay's end is sought past it (or past the duration the face reports).
WELCOME_SECONDS = 86.0
#: `welcome.vtt`'s first cue begins at 0.30 s: before it the live caption line is empty by design (`captionAt`).
FIRST_CAPTION_AT = 0.30


def _playing(face: dict | None) -> tuple[bool, str]:
    """054 judgement call 1 as amended by D31: "playing" is `paused` false at the first read; muted or not is recorded. The clock rising over
    600 ms and `readyState` are recorded, and the clock is required to move only where the browser has decoded enough
    to play (`readyState >= 3` at the second read); a MediaError 4 (no H.264 in the bundled Chromium) is a note."""
    if not face:
        return False, "no guide-face to read"
    # keel-web 081 / design D31: sound on by default where the browser allows it, muted with the glyph lit where it
    # refuses -- either is "playing"; the state is recorded, never required (054 call 1 asked for muted before D31).
    sound = "sound on" if face.get("muted") is False else "muted"
    if MEDIA_ERR_NO_DECODE in (face.get("error"), face.get("errorLater")):
        return True, "the browser cannot decode the mp4 (MediaError 4): recorded, not required"
    if face.get("paused") is not False:
        return False, "the face is paused"
    ready = int(face.get("readyStateLater", face.get("readyState")) or 0)
    rising = float(face.get("currentTimeLater") or 0) > float(face.get("currentTime") or 0)
    # spec 057 run D-01: a face that only reached HAVE_ENOUGH_DATA during the 600 ms (readyState 1 -> 4) has not yet had
    # a frame of the window to play in; its clock is owed a move only where it could already play at the first read.
    if ready >= 3 and int(face.get("readyState") or 0) >= 3 and not rising:
        return False, "the face has decoded enough to play but its clock did not move over 600 ms"
    return True, f"playing, {sound}" if rising else f"asked to play, {sound}, still loading (readyState {ready})"


def leg_welcome(j: Journey, *, walk: bool = False) -> None:
    """Spec 054 FR-2 / FR-3 / FR-5 (keel-cloud 106, keel-web 080, design D24): the guide's welcome at the first open of
    the project, judged and then skipped. Every read goes into `j.guide["welcome"]` (and on S-005's local journey
    `walk` and `replay`), which `_score_guide` scores; the leg itself asserts what the marks do not: the sheet is
    there to judge at all, the face plays muted with its captions (judgement call 1), and the leg's seconds."""
    remote = bool(getattr(j.stack, "is_remote", False))
    walk = walk and not remote
    door = "escape" if walk else "skip"
    guide = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base)
    wire = j.guide_wire
    record: dict = {"profile": "remote" if remote else "local", "door": door}
    j.guide["welcome"] = record

    with _step(j, "the guide's welcome is up at the first open of the project, over an overview that said "
                  "welcomeSeen: false (keel-web 080, D24)", party="founder") as h:
        present = guide.present(timeout_s=10)
        started = time.monotonic()
        record["first_frame"] = {"cues_fired": guide.cues_fired(), "current_time": guide.clock()}
        record["first_open"] = {"present": present, "received": wire.received() if wire else None,
                                "url": j.page.url}
        h.record_assert({"present": True, "received": {"welcomeSeen": False, "openersSeen": []}},
                        record["first_open"])
        assert present, f"G1: no guide-welcome at the first open ({j.page.url})"
    revision_before = j.revision()

    with _step(j, "Skip is visible, enabled and in view at 1280 x 720 and at 390 x 844, and the sheet's only "
                  "control, before any cue (D24)", party="founder") as h:
        original = j.page.viewport_size or WELCOME_SIZES["1280x720"]
        reads = {}
        for name, size in WELCOME_SIZES.items():
            if j.page.viewport_size != size:
                j.page.set_viewport_size(size)
            reads[name] = guide.skip_in_view()
            if name == "1280x720":
                record["controls"] = guide.controls()
        if j.page.viewport_size != original:
            j.page.set_viewport_size(original)
        record["skip_reads"] = reads
        h.record_assert({size: {"visible": True, "enabled": True, "in_view": True, "hit": True}
                         for size in WELCOME_SIZES}, {"reads": reads, "controls": record["controls"],
                                                      "first_frame": record["first_frame"]})

    with _step(j, "the face plays, with sound where the browser allows it (D31), and the captions are on: the live caption has words and "
                  f"the video carries a captions track ending {vs_screens.WELCOME_CAPTIONS}", party="founder") as h:
        face = record["face"] = guide.face()
        playing, how = _playing(face)
        if not playing and how.startswith("the face has decoded enough"):
            # a decoded face whose clock stood still over the 600 ms: the media clock of a headless Chromium under load
            # (builders and gradle beside the run) starts late -- read it once more after 1.5 s before calling it stalled
            j.page.wait_for_timeout(1500)
            face = record["face"] = guide.face()
            record["face"]["second_read"] = True
            playing, how = _playing(face)
        caption = guide.caption()
        nudged = None
        if not caption and guide.seam():
            # The face never played (no decode), so the clock is still 0 and the caption line is empty until the first
            # caption begins (0.30 s): the seam moves the line there, as a playing video would.
            guide.seek(FIRST_CAPTION_AT + guide_marks.SEEK_PAST)
            caption = nudged = guide.caption()
        if not caption and not guide.seam() and float((face or {}).get("currentTimeLater") or 0) >= FIRST_CAPTION_AT:
            # Remote: the clock passed the first caption during the face read, but the line paints on the next
            # timeupdate (about 250 ms apart) -- read it once more rather than fail a race the founder never sees.
            j.page.wait_for_timeout(600)
            caption = guide.caption()
        track = (face or {}).get("track") or {}
        record["captions"] = {"caption": caption, "visible": guide.caption_visible(), "nudged": nudged is not None,
                              "track": track}
        h.record_assert({"playing": True, "muted": "either (D31)", "caption": "words",
                         "track": f"…/{vs_screens.WELCOME_CAPTIONS}"},
                        {"face": face, "how": how, **record["captions"]})
        assert playing, {"face": face, "why": how}
        assert str(track.get("src") or "").endswith(vs_screens.WELCOME_CAPTIONS), track
        # The line is owed words wherever the seam can move it (local) or the clock has passed the first caption; on
        # the remote profile a face that never played (no decode, or still loading) leaves it empty before 0.30 s.
        if not remote or float((face or {}).get("currentTimeLater") or 0) >= FIRST_CAPTION_AT:
            assert caption.strip(), {"caption": caption, "face": face}
    if MEDIA_ERR_NO_DECODE in ((face or {}).get("error"), (face or {}).get("errorLater")):
        with _step(j, "the bundled Chromium cannot decode the welcome's mp4 (MediaError 4): the face shows its poster; "
                      "the cues run on the seam's clock (judgement call 1) -- a note, not a failure",
                   party="founder", kind="note") as h:
            h.request = {"src": (face or {}).get("src")}
            h.response = {"error": (face or {}).get("error"), "caption": caption, "nudged": nudged is not None}

    seconds = time.monotonic() - started
    if walk:
        _walk_the_cues(j, guide)
    else:
        why = guide_marks.REMOTE_WHY if remote else guide_marks.ELSEWHERE_WHY
        j.guide["notes"] = {"G4": why, "G5": why}
        with _step(j, f"the welcome's cue walk and replays are not run on this journey: {why}", party="founder",
                   kind="note") as h:
            h.request = {"profile": record["profile"], "walk": False}
            h.response = {"unmeasured": ["G4", "G5"]}
    resumed = time.monotonic()

    with _step(j, f"{'Escape' if door == 'escape' else 'Skip'} closes the welcome within a second and posts "
                  "guide-seen {what: WELCOME} once, 204; the same POST again is 204; the revision does not move "
                  "(keel-cloud 106)", party="founder") as h:
        press = guide.escape() if door == "escape" else guide.skip()
        record["press"] = press
        after_press = j.revision()
        status, _ = j.call("POST", j.project("/guide-seen"), {"what": "WELCOME"}, ok=(204, 404, 409, 422))
        record["repeat"] = {"status": status}
        record["revision"] = {"before": revision_before, "after_press": after_press, "after_repeat": j.revision()}
        h.record_assert({"requests": [{"method": "POST", "body": {"what": "WELCOME"}, "status": 204}],
                         "gone_ms": f"<= {guide_marks.GONE_MS}", "repeat": 204, "revision": "unchanged"},
                        {"press": press, "repeat": record["repeat"], "revision": record["revision"]})

    with _step(j, "the next open (a plain goto) shows no welcome, and the wire says welcomeSeen: true, openersSeen []",
               party="founder") as h:
        nxt = guide.absent(after=lambda: j.page.goto(f"{j.web_base}/p/{j.project_id}", wait_until="load"))
        seconds += time.monotonic() - resumed
        record["next_open"] = nxt
        record["wire_after"] = (j.get(j.project("/overview")) or {}).get("guide")
        h.record_assert({"count": 0, "received": {"welcomeSeen": True, "openersSeen": []},
                         "wire": {"welcomeSeen": True, "openersSeen": []}},
                        {**nxt, "wire": record["wire_after"]})

    record["seconds"] = round(seconds, 2)
    with _step(j, f"the welcome leg added {seconds:.1f} s (at most {WELCOME_BUDGET_S:.0f} s: the sheet seen to the "
                  "next open's absence read, the cue walk excluded -- FR-5)") as h:
        h.record_assert({"seconds": f"<= {WELCOME_BUDGET_S}"}, {"seconds": record["seconds"]})
        assert seconds <= WELCOME_BUDGET_S, record["seconds"]

    if walk:
        _replay_twice(j, guide)


def _walk_the_cues(j: Journey, guide) -> None:
    """FR-3 a / b (S-005, local): the twelve cues as served, then a seam seek to each `at + 0.05` in order, the snippet
    and `cuesFired` read after each. The face is paused first so the page's own clock cannot run on past the walk."""
    with _step(j, "the welcome's twelve cues, as served and walked through the seam in order (design §7.1)",
               party="founder") as h:
        served = guide.served_cues()
        walk = {"served": [{"id": c.get("id"), "at": c.get("at")} for c in served],
                "before": guide.cues_fired() or [], "held": guide.hold_face(), "steps": []}
        for cue in served:
            at = round(float(cue.get("at") or 0) + guide_marks.SEEK_PAST, 2)
            guide.seek(at)
            drawn = guide.wait_cue(str(cue.get("id")))
            walk["steps"].append({"id": cue.get("id"), "seek": at, "cue": drawn, "fired": guide.cues_fired()})
        j.guide["walk"] = walk
        h.add_screenshot(guide._b.screenshot("guide-walked"))
        h.record_assert({"ids": list(guide_marks.WELCOME_CUES)}, walk)


def _replay_twice(j: Journey, guide) -> None:
    """FR-3 d (S-005, local): *Play the welcome again* opens the sheet near 0 s with Skip in view and Skip closes it;
    once more, a seek to the end closes it by itself; neither posts, `welcomeSeen` stays true, the revision unmoved."""
    with _step(j, "Play the welcome again twice: Skip closes the first, the end the second, and neither posts "
                  "guide-seen (keel-web 080 FR-4)", party="founder") as h:
        before = j.revision()
        opened = guide.replay()
        first = {"found": opened["found"], "via": opened["via"], "opened": opened["opened"],
                 "current_time": guide.clock(), "skip": guide.skip_in_view()}
        closed = guide.skip() if opened["opened"] else {"gone_ms": None, "requests": []}
        first.update({"closed": closed["gone_ms"] is not None, "closed_by": "skip",
                      "requests": opened["requests"] + closed["requests"]})
        again = guide.replay()
        second = {"found": again["found"], "via": again["via"], "opened": again["opened"]}
        duration = ((guide.face() or {}).get("duration") or 0) if again["opened"] else 0
        ended = guide.end(max(WELCOME_SECONDS, float(duration)) + 0.5) if again["opened"] else \
            {"gone_ms": None, "requests": []}
        second.update({"closed": ended["gone_ms"] is not None, "closed_by": "end",
                       "requests": again["requests"] + ended["requests"]})
        replay = {"first": first, "second": second,
                  "after": (j.get(j.project("/overview")) or {}).get("guide"),
                  "revision": {"before": before, "after": j.revision()}}
        j.guide["replay"] = replay
        h.record_assert({"requests": 0, "welcomeSeen": True, "revision": "unchanged"}, replay)


def _next_write_after_the_welcome(j: Journey) -> None:
    """FR-2 d (G3): the founder's next write after the welcome was marked seen -- the context step's Save -- as the page
    received its answer, on its first press (`Corridor.context` has no second). keel-cloud's `proposeContext` answers
    202 and carries no `expectedRevision`; any 409 here names G3, not a minute's wait for a card. The wire is then
    detached: the page's `guide-seen` requests over the whole window go into the record (G1)."""
    wire = j.guide_wire
    writes = wire.writes_after_guide()
    saves = list(j.corridor.saves)
    first = writes[0] if writes else (saves[-1] if saves else {})
    record = j.guide.setdefault("welcome", {})
    record["next_write"] = {**first, "presses": len(saves) or 1,
                            "refused": [w for w in writes if w.get("status") == 409]}
    record["page_posts"] = wire.guide_posts()
    record["overviews"] = len(wire.overviews())
    wire.detach()
    j.guide_wire = None
    with _step(j, "the next founder write after the welcome -- the context Save -- answered on its first press, no "
                  "409 (the mark moved no revision: keel-cloud 106)", party="founder") as h:
        h.record_assert({"status": "2xx (proposeContext: 202)", "presses": 1, "refused": []},
                        record["next_write"])
        status = first.get("status")
        assert isinstance(status, int) and 200 <= status < 300 and not record["next_write"]["refused"], (
            f"G3: the next write after the welcome answered {status}", record["next_write"])


# ------------------------------------------------------------------ spec 057: the teaching videos (G6-G12)
#
# keel-web 086 / keel-cloud 109 (contract 22). Every read goes into `j.guide` under the mark's record key; a clip the
# served manifest says is absent costs nothing (no wait) and its mark passes as not applicable (guide_marks).

def _remote(j: Journey) -> bool:
    return bool(getattr(j.stack, "is_remote", False))


def teaching_start(j: Journey) -> None:
    """The manifest read once; the records the later legs fill, keyed as `guide_marks.MARKS` reads them."""
    teach = j.teach = vs_screens.GuideTeaching(j.page, j.recorder, j.web_base)
    manifest = teach.manifest()
    present = sorted(k for k, v in manifest.items() if v.get("present"))
    j.guide["report"] = {"applicable": teach.present("report-read")}
    j.guide["overview"] = {"read_present": teach.present("report-read"),
                           "fails_present": teach.present("report-fails"), "reads": []}
    j.guide["stages"] = {}
    j.guide["explainers"] = {"questions": {}, "bands": {}, "owed_bands": []}
    j.guide["openers"] = {"stages": {}, "final": None}
    j.guide["snippets"] = []
    with _step(j, f"the guide's manifest as keel-web serves it: {len(present)} of {len(manifest)} clips present "
                  "(keel-web 086 FR-1; an absent clip draws nothing and its mark passes as not applicable)") as h:
        h.record_assert({"served": True}, {"present": present,
                                           "absent": sorted(k for k in manifest if k not in present)})


def _overview_guide(j: Journey) -> dict:
    return (j.get(j.project("/overview")) or {}).get("guide") or {}


def _snippet(j: Journey, scope: str) -> None:
    text = vs_screens._tc(j.page.locator(f"{scope} {vs_screens.GUIDE_SNIPPET}"))
    if text:
        j.guide.setdefault("snippets", []).append(text)


def opener(j: Journey, vector: str) -> None:
    """G11 (D25): at the stage's first open, the opener sheet when its clip is present -- read, Skip pressed, the POST
    kept; an absent opener is only looked for (no wait)."""
    if j.teach is None:
        return
    key = guide_marks.OPENERS[vector]
    one: dict = {"present": j.teach.present(key)}
    j.guide["openers"]["stages"][vector] = one
    sheet = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base, sheet=vs_screens.GUIDE_OPENER)
    if not one["present"]:
        one["shown"] = sheet.count() > 0
        return
    with _step(j, f"{vector.lower()}: the opener plays once at the stage's first open, Skip posts "
                  f"{{what: OPENER, stage: {vector}}} (D25)", party="founder") as h:
        one["shown"] = sheet.present(timeout_s=10)
        if one["shown"]:
            _snippet(j, vs_screens.GUIDE_OPENER)
            one["press"] = sheet.skip()
        h.record_assert({"shown": True, "posted": {"what": "OPENER", "stage": vector}}, one)


def openers_final(j: Journey) -> None:
    if j.teach is not None:
        j.guide["openers"]["final"] = list(_overview_guide(j).get("openersSeen") or [])


def explainer_band(j: Journey, vector: str, question: dict) -> None:
    """G10 (D27): on each stage's first question, when its explainer is present, the pill opened -- the card's primary
    disabled while the band plays -- and Skip, the primary back."""
    if j.teach is None:
        return
    key = question.get("dimension")
    clip = guide_marks.EXPLAINERS.get(key)
    if not clip or not j.teach.present(clip):
        return
    j.guide["explainers"]["owed_bands"].append(vector)
    with _step(j, f"the explainer on {key}: its band stands in the field's place and disables the card's primary "
                  "while open; Skip gives both back (keel-web 086 FR-5)", party="founder") as h:
        before = {"disabled_before": j.teach.primary_disabled(), "fields_before": j.teach.fields()}
        opened = j.teach.open_pill("explain")
        band = {"dimension": key, "clip": clip, "opened": opened["opened"], **before,
                "disabled_open": j.teach.primary_disabled(), "fields_open": j.teach.fields()}
        if opened["opened"]:
            if opened["band"].get("snippet"):
                j.guide["snippets"].append(opened["band"]["snippet"])
            band.update(j.teach.band_skip())
        band["disabled_after"] = j.teach.primary_disabled()
        band["fields_after"] = j.teach.fields()
        j.guide["explainers"]["bands"][vector] = band
        h.record_assert({"opened": True, "disabled_open": True, "fields_open": 0, "closed": True,
                         "after": "as before"}, band)


def report_sheet(j: Journey) -> None:
    """G6 (D44): the report's first open plays `report-read` in the sheet over the Overview; Skip posts `{report: true}`
    204, the wire remembers `reportSeen`, and the next open draws none. When the clip is absent, nothing is waited for
    (the later report reads count the sheet: none may come)."""
    if j.teach is None or not j.guide["report"]["applicable"]:
        return
    record = j.guide["report"]
    sheet = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base, sheet=vs_screens.GUIDE_REPORT)
    wire = vs_screens.GuideWire(j.page).attach()
    with _step(j, "the report's first open plays report-read in the sheet; Skip posts {report: true} once, 204, and "
                  "the wire says reportSeen: true (keel-web 086 FR-6, keel-cloud 109)", party="founder") as h:
        try:
            j.page.goto(f"{j.web_base}/p/{j.project_id}", wait_until="load")
            present = sheet.present(timeout_s=15)
            wire.wait_overview(5)
            src = j.page.evaluate("(sel) => { const v = document.querySelector(sel); "
                                  "return v ? (v.currentSrc || v.src || '') : null; }",
                                  f"{vs_screens.GUIDE_REPORT} {vs_screens.GUIDE_FACE}")
            received = next((o["guide"] for o in wire.overviews() if o.get("guide") is not None), None)
            record["first_open"] = {"present": present, "received": received, "src": src}
            if present:
                _snippet(j, vs_screens.GUIDE_REPORT)
                record["press"] = sheet.skip()
        finally:
            wire.detach()
        record["wire_after"] = _overview_guide(j)
        record["next_open"] = sheet.absent(after=lambda: j.page.goto(f"{j.web_base}/p/{j.project_id}",
                                                                      wait_until="load"), seen_key="reportSeen")
        h.record_assert({"present": True, "posted": guide_marks.REPORT, "reportSeen": True, "next open": 0},
                        record)


def overview_read(j: Journey, when: str, board: dict) -> None:
    """G7 (D45): the pills one Overview read drew, beside whether the wire had a failed line then and `lineFailedSeen`."""
    if j.teach is None:
        return
    dims = [d for v in (j.standings or {}).get("vectors") or [] for d in v.get("dimensions") or []]
    j.guide["overview"]["reads"].append({
        "when": when, "pills": board.get("guide_pills") or [], "report_sheet": board.get("report_sheet"),
        "failing": any(d.get("status") in guide_marks.FAILING for d in dims),
        "lineFailedSeen": _overview_guide(j).get("lineFailedSeen")})


def watch_line_failed(j: Journey) -> None:
    """G7's second half (local, the seam): *When a line fails* played to its end posts `{lineFailed: true}` and the
    next open draws it without the dot."""
    x = j.guide.get("overview") if j.teach is not None else None
    last = (x or {}).get("reads") or []
    if not x or not x["fails_present"] or not last or not last[-1]["failing"]:
        return
    if _remote(j):
        j.guide.setdefault("notes", {})["G7"] = guide_marks.REMOTE_SEAM_WHY
        return
    with _step(j, "When a line fails, played to its end, posts {lineFailed: true} and its fresh dot is gone at the "
                  "next open (keel-web 086 FR-6)", party="founder") as h:
        opened = j.teach.open_pill("report-fails")
        if opened["band"].get("snippet"):
            j.guide["snippets"].append(opened["band"]["snippet"])
        duration = float((j.teach.manifest().get("report-fails") or {}).get("duration") or 600)
        ended = j.teach.band_end(duration + 0.5) if opened["opened"] else {"closed": False, "requests": []}
        j.page.goto(f"{j.web_base}/p/{j.project_id}", wait_until="load")
        j.page.get_by_test_id("report-views").first.wait_for(state="visible", timeout=30_000)
        fails = [p for p in j.teach.pills() if guide_marks.is_pill(p, "report-fails")]
        watched = {"opened": opened["opened"], **ended, "fresh_after": fails[0].get("fresh") if fails else None,
                   "wire_after": _overview_guide(j)}
        x["watched"] = watched
        h.record_assert({"requests": [guide_marks.LINE_FAILED], "fresh_after": False,
                         "lineFailedSeen": True}, watched)


def stage_band(j: Journey, vector: str) -> None:
    """G8 / G9 (D46 / D47): on the stage page `vector_page` left open, when both chapters are present, the pill's band
    -- chip *1 of 2* and chapter 1's clip; through the seam (local) a seek past chapter 1's end, chip *2 of 2* and
    chapter 2's clip -- then Skip. Absent chapters: recorded, nothing pressed."""
    if j.teach is None:
        return
    b2b = vs.is_b2b(j.entry)
    keys = guide_marks.MONEY_CHAPTERS[b2b] if vector == "COMMERCIAL" else guide_marks.STAGE_CHAPTERS[vector]
    one: dict = {"chapters": list(keys), "b2b": b2b, "applicable": all(j.teach.present(k) for k in keys)}
    j.guide["stages"][vector] = one
    if not one["applicable"]:
        one["pills"] = j.teach.pills()
        return
    with _step(j, f"the {vector.lower()} page's band plays two chapters, {keys[0]} then {keys[1]}, the chip 1 of 2 "
                  "then 2 of 2 (keel-web 086 FR-7)", party="founder") as h:
        opened = j.teach.open_pill("stage")
        band = opened["band"]
        one.update({"opened": opened["opened"], "chip_first": band.get("chip"), "src_first": band.get("src"),
                    "seam": j.teach.seam()})
        if band.get("snippet"):
            j.guide["snippets"].append(band["snippet"])
        if opened["opened"] and one["seam"]:
            first = float((j.teach.manifest().get(keys[0]) or {}).get("duration") or 0)
            j.teach.seek(first + 0.05)
            one["chip_second"] = j.teach.wait_chip("2 of 2")
            one["src_second"] = j.teach.band().get("src")
        elif not one["seam"]:
            j.guide.setdefault("notes", {})["G8"] = guide_marks.REMOTE_SEAM_WHY
        if opened["opened"]:
            one.update(j.teach.band_skip())
        h.record_assert({"chip": ["1 of 2", "2 of 2"], "chapters": list(keys), "closed": True}, one)


def captions_read(j: Journey) -> None:
    """G12 (D42): every present clip's served `/guide/<key>.vtt`, its project words (the text is not kept)."""
    if j.teach is None:
        return
    clips = {}
    manifest = j.teach.manifest()
    for key, row in sorted(manifest.items()):
        if row.get("present"):
            text = j.teach.vtt(key)
            clips[key] = {"served": text is not None, "words": guide_marks.project_words(text),
                          "cues": (text or "").count("-->")}
    # spec 059: the three page clips are read with the rest; `present` and `manifest` let G12 say none was skipped
    j.guide["captions"] = {"clips": clips, "snippets": list(j.guide.get("snippets") or []),
                           "present": sorted(k for k, row in manifest.items() if row.get("present")),
                           "manifest": len(manifest)}


# ------------------------------------------------------- spec 059: Interviews › Sent reworked (G13-G17)
#
# keel-web 088 / keel-cloud 111 (contract 24). The founder journey (S-005, `j.teach` set) holds the Interviews sheet up
# at its first open of Sent and judges it; every other open of Sent, on every journey, passes it by
# (`iv_screens.pass_interviews_sheet`, through `Interviews.land` / `Persona.sent`). The readings go into `j.guide`.

def _downloads(page):
    """A press that downloads a file, read back as text."""
    def press(click) -> str:
        from pathlib import Path                              # noqa: PLC0415
        with page.expect_download(timeout=20_000) as got:
            click()
        return Path(got.value.path()).read_text(encoding="utf-8")
    return press


def _guide_on(j: Journey) -> bool:
    """keel-web 088 `interviewsGuideOn`: the Interviews placements only on a contract-24 cloud."""
    return "interviewsSeen" in _overview_guide(j)


def interviews_sheet(j: Journey, sent) -> dict | None:
    """G13 (spec 059 FR-1): the founder's first open of Sent, the sheet held up -- `page-interviews-first` read, Skip
    pressed, the POST kept -- then the wire's `interviewsSeen` and the next open (none). Every later open of Sent is kept
    by the Sent-open helper in the record's `later`. Returns what W1 drew (or None), as `Interviews.land` does."""
    record = j.guide["interviews"] = {"judged": True, "applicable": j.teach.present(iv_screens.INTERVIEWS_CLIP),
                                      "later": []}
    sheet = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base, sheet=iv_screens.GUIDE_INTERVIEWS)
    wire = vs_screens.GuideWire(j.page).attach()
    with _step(j, "Sent's first open plays page-interviews-first in the sheet; Skip posts {interviews: true} once, "
                  "204, and the wire says interviewsSeen: true (keel-web 088 FR-0, keel-cloud 111)",
               party="founder") as h:
        try:
            walked = sent.land(j.project_id, sheet="hold")
            present = sheet.present(timeout_s=iv_screens.SHEET_WAIT_S if record["applicable"] else 3)
            src = j.page.evaluate("(sel) => { const v = document.querySelector(sel); "
                                  "return v ? (v.currentSrc || v.src || '') : null; }",
                                  f"{iv_screens.GUIDE_INTERVIEWS} {vs_screens.GUIDE_FACE}")
            received = next((o["guide"] for o in reversed(wire.overviews())
                             if isinstance(o.get("guide"), dict) and "interviewsSeen" in o["guide"]), None)
            record["first_open"] = {"present": present, "received": received, "src": src}
            if present:
                _snippet(j, iv_screens.GUIDE_INTERVIEWS)
                record["press"] = sheet.skip()
        finally:
            wire.detach()
        record["wire_after"] = _overview_guide(j)
        record["next_open"] = sheet.absent(
            after=lambda: j.page.goto(f"{j.web_base}/p/{j.project_id}/interviews/sent", wait_until="load"),
            seen_key="interviewsSeen", screen=".sent__kinds")
        h.record_assert({"present": True, "posted": guide_marks.INTERVIEWS, "interviewsSeen": True, "next open": 0},
                        record)
    return walked


def sent_pill(j: Journey) -> None:
    """G14's Sent half (keel-web 088 FR-1, D43): *How this page works* opens the band in the pill's place -- chapter 1
    *Where to start* on `page-interviews-first`, through the seam (local) chapter 2 *This page* on `page-sent` -- and
    Skip gives the pill back. Chapters absent: the pills read, nothing pressed."""
    if j.teach is None:
        return
    one: dict = {"applicable": all(j.teach.present(k) for k in guide_marks.SENT_CHAPTERS) and _guide_on(j)}
    j.guide.setdefault("page_pills", {})["sent"] = one
    pills = lambda: [p for p in j.teach.pills() if p.get("testid") == "guide-pill-page"]  # noqa: E731
    if not one["applicable"]:
        one["pills"] = pills()
        return
    with _step(j, "Sent's pill How this page works opens the band in its own place: Chapter 1 of 2 · Where to start, "
                  "then 2 of 2 · This page; Skip gives the pill back (keel-web 088 FR-1)", party="founder") as h:
        one["pills"] = pills()
        opened = j.teach.open_pill("page")
        band = opened["band"]
        one.update({"opened": opened["opened"], "chip_first": band.get("chip"), "src_first": band.get("src"),
                    "seam": j.teach.seam(),
                    "in_place": j.page.evaluate(
                        "() => !!document.querySelector('.sent__guide [data-testid=guide-band]') && "
                        "!document.querySelector('.sent__guide [data-testid=guide-pill-page]')")})
        if band.get("snippet"):
            j.guide["snippets"].append(band["snippet"])
        if opened["opened"] and one["seam"]:
            first = float((j.teach.manifest().get(guide_marks.SENT_CHAPTERS[0]) or {}).get("duration") or 0)
            j.teach.seek(first + 0.05)
            one["chip_second"] = j.teach.wait_chip("2 of 2")
            one["src_second"] = j.teach.band().get("src")
        elif not one["seam"]:
            j.guide.setdefault("notes", {})["G14"] = guide_marks.REMOTE_SEAM_WHY
        if opened["opened"]:
            one.update(j.teach.band_skip())
        one["pill_back"] = len(pills()) == 1
        h.record_assert({"chips": list(guide_marks.SENT_CHIPS), "in place": True, "closed": True, "pill back": True},
                        one)


def contacts_pill(j: Journey, view: str) -> None:
    """G14's Contacts half (keel-web 088 FR-5): on the datasets view the pill opens its one clip, `page-contacts`, with
    no chapter chip, and Skip closes it; on the consumer card (or the credits line) no pill at all (088 call 11)."""
    teach = j.teach or vs_screens.GuideTeaching(j.page, j.recorder, j.web_base)
    one: dict = {"view": view, "applicable": teach.present(guide_marks.CONTACTS_CLIP) and _guide_on(j)}
    j.guide.setdefault("page_pills", {})["contacts"] = one
    pill = j.page.locator(f"{vs_screens.GUIDE_PILL}[data-testid='guide-pill-page']")
    if one["applicable"] and view == "datasets":
        try:
            pill.first.wait_for(state="visible", timeout=10_000)
        except Exception:  # noqa: BLE001 - its absence is the mark's to read
            pass
    one["pills"] = [p for p in teach.pills() if p.get("testid") == "guide-pill-page"]
    if not (one["applicable"] and view == "datasets" and one["pills"]):
        return
    with _step(j, "Contacts' pill How this page works opens its one clip, page-contacts, with no chapter chip; Skip "
                  "closes it (keel-web 088 FR-5)", party="founder") as h:
        opened = teach.open_pill("page")
        band = opened["band"]
        one.update({"opened": opened["opened"], "src": band.get("src"), "chip": band.get("chip")})
        if band.get("snippet"):
            j.guide.setdefault("snippets", []).append(band["snippet"])
        if opened["opened"]:
            one.update(teach.band_skip())
        h.record_assert({"clip": guide_marks.CONTACTS_CLIP, "chip": "", "closed": True}, one)


def sent_reading(j: Journey, when: str, sent=None) -> None:
    """G15 and G17 (keel-web 088 FR-1, FR-3), on the guide journey: Sent's regions top to bottom and every control
    named *How it works*; each role card's count beside the wire's kinds and the register's own rows."""
    if j.teach is None:
        return
    sent = sent or iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    me = j.get("/v2/me") or {}
    band_owed = me.get("aiPath") != "OWN"                # 088: an account on its own AI draws no who-asks band
    if band_owed:
        try:
            j.page.get_by_test_id("persona-line").wait_for(state="visible", timeout=15_000)
        except Exception:  # noqa: BLE001 - its absence is the mark's to read
            pass
    with _step(j, f"Sent {when}: top to bottom the kicker and total, the pill, the who-asks band, the role cards, the "
                  "links, no How it works; each card's count in its action row as the register counts "
                  "(keel-web 088 FR-1, FR-3)", party="founder") as h:
        order = sent.order()
        register = j.get(j.project("/invitations")) or {}
        drawn = sent.register()
        cards = sent.kinds()
        pill_owed = any(j.teach.present(k) for k in guide_marks.SENT_CHAPTERS) and _guide_on(j)
        x = j.guide.setdefault("sent_order", {"readings": [], "band_owed": False})
        x["readings"].append({"when": when, **order, "pill_owed": pill_owed, "band_owed": band_owed})
        x["band_owed"] = x["band_owed"] or band_owed
        counts = {"when": when, "cards": cards, "drawn_rows": len(drawn),
                  "kinds": [{k: kind.get(k) for k in ("label", "respondentType", "linksMade", "answered", "aim")}
                            for kind in register.get("kinds") or []],
                  "invitations": [{"respondentType": v.get("respondentType"), "status": v.get("status")}
                                  for v in register.get("invitations") or []]}
        j.guide.setdefault("role_counts", {"readings": []})["readings"].append(counts)
        h.record_assert({"order": list(guide_marks.SENT_ORDER), "how it works": 0,
                         "counts": {k["label"]: guide_marks.role_count_words(k) or "nothing sent yet"
                                    for k in counts["kinds"]}},
                        {"order": order, "cards": cards})


def links_reading(j: Journey, when: str, sent=None) -> None:
    """G16 (keel-web 088 FR-4): the links table over every link -- its frame (heading, range, Next, the search row),
    Next once past ten, one row's name searched then cleared, *Made* sorted and sorted back, and the .csv downloaded."""
    sent = sent or iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    with _step(j, f"the links table {when}: one name searched and cleared, Made sorted both ways, the range and Next, "
                  "Download (.csv) in the search row with every link (keel-web 088 FR-4)", party="founder") as h:
        rows = sent.register()
        n = len((j.get(j.project("/invitations")) or {}).get("invitations") or [])
        frame = sent.links()
        one: dict = {"when": when, "n": n, "drawn": len(rows), "frame": frame}
        if n > guide_marks.PAGE_SIZE:
            one["next_page"] = sent.go_next()
        if frame.get("search"):
            texts = {r.get("Who"): " ".join(str(r.get(k) or "") for k in ("Who", "Format", "Status")).lower()
                     for r in rows}
            term = next((w for w in frame.get("rows") or [] if w and
                         sum(w.lower() in t for t in texts.values()) == 1), None)
            if term:
                found = sent.search(term)
                cleared = sent.search("")
                one["search"] = {"term": term, "found": found["rows"], "range": found["range"],
                                 "cleared": {"rows": cleared["rows"], "range": cleared["range"]}}
        sort = sent.sort("made")
        one["sort"] = {**sort, "back": sent.sort("made")}
        text = sent.download(_downloads(j.page))
        one["csv"] = {"header": (text.splitlines() or [""])[0], "lines": guide_marks.csv_lines(text)}
        j.guide.setdefault("links", {"readings": []})["readings"].append(one)
        want, on = guide_marks.range_owed(n)
        h.record_assert({"n": n, "range": want, "next": on, "csv lines": n + 1,
                         "sort": ["descending", "ascending", "descending"]}, one)


# ----------------------------------------------------------------------------- leg 2: interpret

def leg_interpret_problem(j: Journey) -> None:
    """The problem seed typed into the chat (the entry's own problem statement), PROBLEM_INTERPRET's
    card, and *Yes, that's the problem* -- which chains the PROBLEM calibration questions."""
    try:
        card = j.corridor.seed(j.project_id, "PROBLEM", j.founder.problem_seed, resend=getattr(j, "retries", 0))
    finally:
        _resent(j, "PROBLEM")
    want = vs.problem_result(j.entry)
    with _step(j, "the problem card is the entry's own interpretation", party="founder") as h:
        h.record_assert(want["statement"] if j.strict else "a statement", card["claim"])
        assert card["claim"].strip(), card
        if j.strict:
            assert card["claim"] == want["statement"], card
    j.corridor.confirm_seed("PROBLEM")
    with _step(j, "the confirmed statement and the offer's name are the entry's, on the wire") as h:
        review = j.get(j.project("/review/PROBLEM")) or {}
        h.record_assert({"statement": card["claim"]}, {"statement": review.get("statement")})
        assert review.get("statement") == card["claim"], review.get("statement")


def _resent(j: Journey, vector: str | None = None) -> None:
    """Spec 062: each time the back-test's founder sent a seed again (the chat refused the model's answer or asked),
    a finding -- with the product's own diagnostic for every refused job of that vector's screen (062 follow-up,
    2026-10-22: 11-issen's PROBLEM seed was refused four times and the chat said only *a shape this step can't use*;
    the reason, P1 on the word *apps*, was in the interaction row alone)."""
    resent = list(getattr(j.corridor, "resent", None) or [])
    if resent:
        j.corridor.resent = []
    refused: list[dict] = []
    if resent or vector:
        screen = {"PROBLEM": "PROBLEM_INTERPRET", "SOLUTION": "SOLUTION_MECHANISM"}.get(vector or "")
        try:
            rows = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
        except Exception:  # noqa: BLE001 - the diagnostic is evidence, never the end of the walk
            rows = []
        refused = [{"status": r.get("status"), "diagnostic": r.get("diagnostic") or r.get("refusal")}
                   for r in rows if (screen is None or r.get("screen") == screen)
                   and r.get("status") in TERMINAL_BAD | {"RESULT_INVALID"}]
    for n, row in enumerate(resent):
        finding = {"what": f"{row['vector']} seed sent again", "refused": row["chat said"]}
        # spec 064 FR-9 (keel-web 093): a refusal on Keel's door leads with the web's own words -- the anchor kept
        if vs_screens.REFUSED_LEAD in str(row["chat said"]):
            finding["anchor"] = vs_screens.REFUSED_LEAD
        if n < len(refused):
            finding["diagnostic"] = refused[n]
        j.findings.append(finding)
    if refused and not resent:
        j.findings.append({"what": f"{vector} seed refused", "diagnostics": refused})


def leg_interpret_solution(j: Journey) -> None:
    """The solution seed, SOLUTION_MECHANISM's card and *Looks right* (which chains the SOLUTION
    calibration), and then **the idea as the solution's first question** (keel-web 063 S2): the three lines
    the mechanism drafted, read on the Check screen under *Solution · 1 of n*, saved untouched -- Save is the
    approval the lock and every invitation wait on."""
    try:
        card = j.corridor.seed(j.project_id, "SOLUTION", j.founder.solution_seed, resend=getattr(j, "retries", 0))
    finally:
        _resent(j, "SOLUTION")
    m = j.entry.solution_mechanism
    with _step(j, "the mechanism card draws the entry's own actor, trigger, mechanism and output",
               party="founder") as h:
        want = [m["trigger"], m["mechanism"], m["output"]] if j.strict else []
        missing = [part for part in want if part not in card["text"]]
        h.record_assert(want, card)
        assert card["text"].strip(), card
        assert not missing, missing
    with _step(j, "the mechanism card offers no *Someone else would use it* (keel-web 070 F8): who decides is asked "
                  "once, on the persona step", party="founder") as h:
        offered = [words for words in vs_screens.SOMEONE_ELSE_USES if words in card["text"]]
        h.record_assert([], offered)
        assert not offered, offered
    j.corridor.confirm_seed("SOLUTION")
    view = _wait_calibration(j, "SOLUTION")
    typed = j.founder.idea_name
    _idea_unnamed(j, typed)
    seen = j.corridor.idea_check(typed)
    j.framing["idea"] = [seen]
    if seen["reloaded"]:
        # runs/DRIFT.md #78, closed by keel-web 066 (IdeaCheck refills from the served idea): spec 041 reloaded the page
        # once. The page object still reloads (so the bundle shows what followed), and the journey fails here.
        with _step(j, f"{j.entry.id}: DRIFT #78 came back -- S2 drew three empty lines and needed a reload "
                      "(closed by keel-web 066)", party="founder") as h:
            h.record_assert({"reloaded": False}, {"reloaded": True, "lines after the reload": seen["lines"]})
            raise AssertionError("DRIFT #78 came back: S2's lines were empty until the page was reloaded")
    with _step(j, "S2: What it is carries keel-web 066's live counter, n / 5 words, and Save is off over five "
                  "(keel-cloud 090 L5, D14)", party="founder") as h:
        counter = seen.get("counter") or {}
        drawn_words = len(seen["lines"]["what"].split())
        over = counter.get("over") or {}
        want = {"drawn": {"text": f"{drawn_words} / 5 words", "over": False, "save_enabled": drawn_words > 0},
                "over": {"typed": over.get("typed"), "text": f"{len(str(over.get('typed')).split())} / 5 words",
                         "over": True, "save_enabled": False},
                "named": {"text": f"{len(typed.split())} / 5 words", "over": False, "save_enabled": True}}
        named = dict(counter.get("named") or {})
        waiting = named.pop("waiting", None)
        seen_counter = {**counter, "named": named}
        h.record_assert(want, {**counter, "named_waiting": waiting})
        assert seen_counter == want, json.dumps({"screen": counter, "want": want}, indent=2)
        assert len(str(counter["over"]["typed"]).split()) == 6, counter
    with _step(j, "S2: the idea's how and belief are the mechanism's, the what line the name the founder typed "
                  "(keel-cloud 097 F7), under Solution · 1 of n, and Save approved them on the wire",
               party="founder") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_view(j.entry)
        total = len(view.get("questions") or []) + STAGE_OFFSET["SOLUTION"]
        name = vs.idea_name_of(typed)
        h.record_assert({**({k: want[k] for k in ("how", "belief")} if j.strict else {}), "typed": typed, "name": name,
                         "approved": True, "progress": f"Solution · 1 of {total}"},
                        {"screen": seen, "wire": idea})
        assert all((idea.get(k) or "").strip() for k in ("what", "how", "belief")), idea
        assert {k: idea.get(k) for k in ("how", "belief")} == {k: seen["lines"][k] for k in ("how", "belief")}, (
            idea, seen["lines"])
        assert not (idea.get("what") or "").lower().startswith("imagine"), idea
        assert idea.get("what") == name, (idea.get("what"), name)
        assert idea.get("approved") is True, idea
        assert idea.get("shortName") == idea.get("what"), idea
        _hold_frame(seen["frame"], "SOLUTION", 1, total)
        if j.strict:
            assert {k: seen["lines"][k] for k in ("how", "belief")} == {k: want[k] for k in ("how", "belief")}, (
                seen["lines"], want)
            assert idea.get("shortName") == vs.idea_name(j.entry), (idea, vs.idea_name(j.entry))
        j.idea_name = str(idea.get("shortName") or "")
        # spec 064 FR-5b (keel-cloud 121 J1, keel-web 097): the idea's notes are recomputed on every read and never
        # refuse -- 05-paidly's scripted how says *platform*, so its card carries the J1 note; every other none
        j.feedback.setdefault("idea_notes", idea.get("notes"))
        if j.strict:
            words = [n.get("word") for n in idea.get("notes") or [] if n.get("rule") == "J1"]
            assert [w.lower() for w in words] == [w.lower() for w in vs.expected_j1(j.entry)], (
                idea.get("notes"), vs.expected_j1(j.entry))
        named = j.feedback.setdefault("idea", {})
        named.update({"stored": idea.get("what"), "approved": idea.get("approved"), "typed_name": name})
        if not NAME_ON_THE_WIRE:
            named["screen"] = seen["unnamed"]
    if not NAME_ON_THE_WIRE:
        with _step(j, "S2 demands the name (keel-web 070 F7): the what box empty with its placeholder *Name it in up "
                      "to five words*, 0 / 5 words and Save off, until the founder typed one", party="founder") as h:
            want = {"value": "", "placeholder": feedback_marks.NAME_PLACEHOLDER, "save_enabled": False}
            h.record_assert(want, seen["unnamed"])
            assert seen["unnamed"] == want, seen["unnamed"]
    if typed != m["short_name"]:
        with _step(j, f"{j.entry.id}: the founder named the idea {typed!r} on S2, not the mechanism card's "
                      f"{m['short_name']!r} (keel-cloud 090, D14)", party="founder") as h:
            plan = j.get(j.project("/plan")) or {}
            h.record_assert({"shortName": vs.idea_name_of(typed), "plan.idea.what": vs.idea_name_of(typed)},
                            {"idea": idea, "plan.idea": plan.get("idea")})
            assert j.idea_name == vs.idea_name_of(typed) != m["short_name"], (j.idea_name, m["short_name"])
            assert len(typed.split()) <= 5, typed
            assert ((plan.get("idea") or {}).get("what")) == j.idea_name, plan.get("idea")


#: Spec 046 T004: True names the idea on the wire (`PUT idea`) before S2, so the screen opens on the name and its Save
#: approves it -- the stand-in until keel-web 070's S2 (the wire phase). False, since 070: S2 opens empty and the
#: journey types the name there.
NAME_ON_THE_WIRE = False


def _idea_unnamed(j: Journey, typed: str) -> None:
    """keel-cloud 097 F7 (spec 046 FM4): Keel no longer drafts the idea's name. The mechanism card landed with `what`
    null (no r11 seed carries a product name -- `vs.seed_idea_name`), and the server refuses an unnamed idea: approve
    is 422 IDEA_NAME_REQUIRED (097 call 16), and so is `PUT idea` with an empty name; neither writes. The journey then
    names it -- on the wire, `PUT idea` with the name it types (`NAME_ON_THE_WIRE`), until S2 types it."""
    seed_name = vs.seed_idea_name(j.founder.solution_seed)
    with _step(j, "the idea arrives unnamed (keel-cloud 097 F7): what is null, approve and an empty name are refused "
                  "422 IDEA_NAME_REQUIRED, and nothing is written", party="founder", kind="assert") as h:
        idea = j.get(j.project("/idea")) or {}
        revision = j.revision()
        named_on_arrival = not j.strict and (seed_name is not None or idea.get("what"))
        if named_on_arrival:
            # the two refusal probes are for an unnamed idea; on a named one they would write (a back-test seed that
            # names its product), so they are not sent
            approve = empty = None
            approve_body = empty_body = {}
        else:
            approve, approve_body = j.call("POST", j.project("/idea/approve"), {"expectedRevision": revision},
                                           ok=(200, 422))
            empty, empty_body = j.call("PUT", j.project("/idea"), {
                "expectedRevision": revision, "what": "", "how": idea.get("how"), "belief": idea.get("belief")},
                ok=(200, 422))
        after = j.get(j.project("/idea")) or {}
        refusals = {"approve": {"status": approve, "code": _refusal(approve_body)},
                    "empty": {"status": empty, "code": _refusal(empty_body)}}
        j.feedback["idea"] = {"seed_name": seed_name, "served": idea.get("what"), "refusals": refusals,
                              "typed": typed, "named_on": "wire" if NAME_ON_THE_WIRE else "screen"}
        h.record_assert({"seed name": None, "what": None, "approve": [422, feedback_marks.IDEA_NAME_REQUIRED],
                         "empty": [422, feedback_marks.IDEA_NAME_REQUIRED], "revision": revision},
                        {"seed name": seed_name, "idea": idea, "refusals": refusals, "after": after,
                         "bodies": [approve_body, empty_body]})
        if named_on_arrival:
            # a back-test seed may name the product (14-code-four's does, in every sentence); 097 F7 is a rule for
            # Keel's drafting, not for the founder's words -- what the wire served is recorded as a finding for the
            # judge (did Keel copy the seed's name into `what`?) and the walk goes on, naming it as the founder would
            j.findings.append({"what": "the idea arrived named (keel-cloud 097 F7 says Keel drafts no name): the seed "
                                       f"names {seed_name!r}, the wire served what={idea.get('what')!r}",
                               "served": {k: idea.get(k) for k in ("what", "approved", "shortName")}})
        else:
            assert seed_name is None, seed_name
            assert idea.get("what") is None and idea.get("approved") is False, idea
            for refusal in refusals.values():
                assert (refusal["status"], refusal["code"]) == (422, feedback_marks.IDEA_NAME_REQUIRED), refusals
        assert after.get("approved") is False and (named_on_arrival or after.get("revision") == revision), after
    if not NAME_ON_THE_WIRE:
        return
    with _step(j, f"the journey names the idea {vs.short_name(j.entry)!r} on the wire (PUT idea, spec 046 T004 until "
                  "keel-web 070's page objects) -- not approved until S2's Save", party="founder", kind="protocol") as h:
        body = {"expectedRevision": j.revision(), "what": vs.short_name(j.entry), "how": idea.get("how"),
                "belief": idea.get("belief")}
        _, named = j.call("PUT", j.project("/idea"), body)
        j.page.reload(wait_until="load")
        h.record_wire(body, named)
        assert named.get("what") == vs.idea_name_of(vs.short_name(j.entry)) and named.get("approved") is False, named


# ----------------------------------------------------------------------------- leg 3: calibrate

def _hold_frame(frame: dict, vector: str, position: int, total: int) -> None:
    """keel-web 063 FR-003 / FR-009: *Stage · k of n*, n dots with the k-th the hollow one (a question's
    Answer, Check and Choose share it), and the side nav locked with no link in it."""
    assert frame["progress"] == f"{STAGE_WORD[vector]} · {position} of {total}", frame
    assert frame["dots"] == total and frame["now"] == position, frame
    assert frame["done"] == position - 1, frame
    assert frame["nav_locked"] and frame["nav_links"] == 0, frame
    # Spec 054 FR-2 e (G1): the welcome never returns once seen -- no sheet over any corridor frame.
    assert frame.get("welcome", 0) == 0, frame


def _choose_label(j: Journey, question: dict, answer: vs.CalibrationAnswer) -> tuple[str, int]:
    """The one item Choose picks: the entry's own (its `pickedIndex`), read off the drafted list the
    screen shows -- on a live journey the model's list, its item at the entry's index or the last."""
    rows = (question.get("draft") or {}).get("items") or []
    listed = answer.listed or {}
    index = listed.get("pickedIndex") or 0
    if j.strict:
        return listed["items"][index]["label"], index
    held = min(index, max(0, len(rows) - 1))
    return (rows[held].get("label") if rows else listed["items"][index]["label"]), held


def leg_calibrate(j: Journey, vector: str) -> None:
    """One stage, on its screens, one dimension a screen (keel-web 063): CALIBRATION_QUESTIONS READY; each
    single question answered the way the entry answers it; each list dimension's Answer typed (the
    founder's words, `POST calibration/{vector}/draft`), its Check screen waited out while Keel drafts the
    list and saved untouched, and where it picks its Choose screen picking the entry's own item. Asserted
    on the screens -- every screen's *Stage · k of n*, dots and locked nav; each drafted list the entry's own
    words; the *Keel will test* box (none pre-picked on Choose) the entry's belief sentence; the stage's last
    primary naming the next stage -- and on the wire: the slice, every answer stored (a list's items with
    code's positional codes, its `asked` faces, its picked index, its phrase), the review complete with the
    entry's belief sentences and LEFT_OUT exactly where the founder was unsure."""
    view = _wait_calibration(j, vector)
    with _step(j, f"{vector.lower()}: the calibration offers exactly the registry's slice, in order",
               party="founder") as h:
        keys = [q.get("dimension") for q in view.get("questions") or []]
        want = vs.founder_keys(j.entry, vector)
        h.record_assert(want, keys)
        assert keys == want, keys
    j.corridor.wait_questions()
    answers = {a.dimension: a for a in j.founder.calibration[vector]}
    total = len(view.get("questions") or []) + STAGE_OFFSET[vector]
    questions = view.get("questions") or []
    if questions:
        explainer_band(j, vector, questions[0])
    conflicts = len(j.corridor.conflicts)
    for question in questions:
        key = question["dimension"]
        answer = answers[key]
        if not vs.is_list(key):
            if key == "commercial.existing_sacrifice" and not answer.unsure:
                _old_cost_on_the_wire(j, question, answer)
            j.framing[key] = [j.corridor.single(question, answer.as_wire())]
            if key in ("commercial.existing_sacrifice", "commercial.price") and j.framing[key][0].get("chain"):
                _hold_the_chain_screen(j, key, j.framing[key][0])
            continue
        _keep_draft(j, question, "first", None)
        if answer.unsure:
            j.framing[key] = [j.corridor.list_answer(question, None)]
            continue
        seen = [j.corridor.list_answer(question, answer.text)]
        drafted = _wait_calibration(j, vector)
        question = next((q for q in drafted.get("questions") or [] if q.get("dimension") == key), question)
        _keep_draft(j, question, "answer", answer.text)
        typed = vs.importance_typed(j.entry) if (key == "problem.importance" and j.strict) else []
        if typed:
            seen.append(j.corridor.list_check(question, add=typed, one_more=len(vs.importance_named(j.entry)) == 1))
            _hold_importance_check(j, seen[-1], typed)
        else:
            seen.append(j.corridor.list_check(question))
        if key in vs.PICKED:
            label, _ = _choose_label(j, question, answer)
            seen.append(j.corridor.list_choose(question, label))
        j.framing[key] = seen
    refused = j.corridor.conflicts[conflicts:]
    if refused:
        # runs/DRIFT.md #80, closed by keel-cloud 091 FR-A (`GET calibration/{vector}` reads the interaction first and
        # the project second, so a READY is always over the drafted project): spec 041 pressed again after the poll.
        # Spec 042 keeps the page object's second press only so the bundle shows what followed, and fails here.
        with _step(j, f"{j.entry.id}: DRIFT #80 came back -- {len(refused)} {vector.lower()} write(s) refused 409 "
                      "after a redraft (closed by keel-cloud 091)", party="founder") as h:
            h.record_assert({"refused": 0}, refused)
            raise AssertionError(f"DRIFT #80 came back: {json.dumps(refused)}")

    with _step(j, f"{vector.lower()}: every screen reads {STAGE_WORD[vector]} · k of {total} with its dots, "
                  "the side nav locked, and the stage's last primary names the next stage",
               party="founder") as h:
        frames = {k: [s["frame"] for s in j.framing[k]] for k in keys}
        h.record_assert({"total": total, "exit": vs_screens.STAGE_EXIT[vector]}, frames)
        for position, key in enumerate(keys, start=1 + STAGE_OFFSET[vector]):
            for frame in frames[key]:
                _hold_frame(frame, vector, position, total)
        last = j.framing[keys[-1]][-1]
        if not answers[keys[-1]].unsure:
            assert last["primary"] == vs_screens.STAGE_EXIT[vector], last["primary"]

    with _step(j, f"{vector.lower()}: each drafted list is the entry's own on its Check screen, Choose "
                  "opens with nothing picked, and the Keel-will-test box reads the entry's belief",
               party="founder") as h:
        mismatches = []
        lower_case = []
        for key in keys:
            seen = j.framing[key]
            if not vs.is_list(key) or answers[key].unsure:
                continue
            check = next(s for s in seen if s["screen"] == "check")
            choose = next((s for s in seen if s["screen"] == "choose"), None)
            if choose is not None:
                if choose["picked_before"] or choose["test_before"]["belief"] != KEEL_TEST_PENDING:
                    mismatches.append({"dimension": key, "choose": "something was pre-picked", "seen": choose})
            if not j.strict:
                continue
            drawn = _drawn_list(key, check)
            want = _corpus_list(j.entry, key)
            if drawn != want:
                mismatches.append({"dimension": key, "screen": drawn, "corpus": want})
            sentence = (j.entry.founder_calibration.get(key) or {}).get("belief_sentence")
            box = (choose or check).get("test_after") or (choose or check)["test"] \
                if (choose or key in KEEL_SET) else None
            if box is None or box["belief"] == sentence:
                continue
            if key == "commercial.buyer_payer_alignment" and _capital(box["belief"]) == sentence:
                lower_case.append({"dimension": key, "keel will test": box["belief"], "server": sentence})
                continue
            mismatches.append({"dimension": key, "keel will test": box["belief"], "corpus": sentence})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)
    if lower_case:
        # runs/DRIFT.md #79, closed by keel-web 066 (fillBelief capitalises): spec 041 held the preview equal but for
        # its first letter. Spec 042 fails the journey if the lower-case head is ever drawn again.
        with _step(j, f"{j.entry.id}: DRIFT #79 came back -- the Choose screen's Buyer-and-payer belief opens "
                      "lower-case (closed by keel-web 066)", party="founder") as h:
            h.record_assert({"server": [r["server"] for r in lower_case]},
                            {"screen": [r["keel will test"] for r in lower_case]})
            raise AssertionError(f"DRIFT #79 came back: {json.dumps(lower_case)}")

    cost = j.entry.cost() or {}
    if vector == "COMMERCIAL" and j.founder.hourly_rate is not None and (not j.entry.chain()
                                                                          or cost.get("mode") == "HOURS"):
        # spec 064 FR-2: on the chain only an HOURS cost is priced at a rate; off it, every B2B entry as before
        _hourly_rate(j)
    # the 097 F9 probe writes the entry's own Importance labels over Keel's draft through the API; on the back-test
    # (spec 062, `retries` set) what Keel drafted is the finding, so the probe is skipped (062 follow-up, 2026-10-22:
    # the 08-fresco and 10-palus judges saw the founder approve one list and strangers served another)
    if vector == "PROBLEM" and not answers["problem.importance"].unsure and not getattr(j, "retries", 0):
        _importance_needs_three(j)
    stored = _wait_calibration(j, vector)
    with _step(j, f"{vector.lower()}: every list is stored as the founder saved it -- code's positional codes, "
                  "the stranger's faces, the picked index, the phrase", party="stack") as h:
        mismatches = []
        for q in stored.get("questions") or []:
            key = q.get("dimension")
            if not vs.is_list(key) or answers[key].unsure:
                continue
            got = (q.get("answer") or {}).get("list") or {}
            items = [{k: i.get(k) for k in ("code", "label", "asked") if i.get(k) is not None}
                     for i in got.get("items") or []]
            have = {"items": items, "pickedIndex": got.get("pickedIndex"), "phrase": got.get("phrase")}
            if j.strict:
                want = vs.saved_list(j.entry, key)
                if have != want:
                    mismatches.append({"dimension": key, "wire": have, "corpus": want})
            else:
                codes = [i.get("code") for i in items]
                want_codes = [vs.wire_code(key, n) for n in range(len(items))]
                if key == "commercial.commitment" and len(codes) == 2 and codes[1] == "smaller_step":
                    # spec 064 FR-7a (keel-cloud 118 FR-1): the conditional yes is stored as the list's second item
                    want_codes = [want_codes[0], "smaller_step"]
                if codes != want_codes:
                    mismatches.append({"dimension": key, "wire": have, "want": "code's positional codes"})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)

    review = j.get(j.project(f"/review/{vector}")) or {}
    with _step(j, f"{vector.lower()}: the review is complete and reads the entry's belief sentences, "
                  "LEFT_OUT where the founder was unsure", party="stack") as h:
        rows = {r.get("dimension"): r for r in review.get("rows") or []}
        mismatches = []
        for key in vs.founder_keys(j.entry, vector) + (
                ["commercial.ability_to_pay"] if vector == "COMMERCIAL" else []):
            founder = j.entry.founder_calibration.get(key) or {}
            row = rows.get(key) or {}
            if founder.get("unsure") or (key == "problem.frequency" and not vs.frequency_fits(j.entry)):
                if not (row.get("leftOut") or row.get("unsure")):
                    mismatches.append({"dimension": key, "want": "left out", "row": row})
                continue
            if j.strict and row.get("belief") != founder.get("belief_sentence"):
                mismatches.append({"dimension": key, "wire": row.get("belief"),
                                   "corpus": founder.get("belief_sentence")})
        h.record_assert({"complete": True, "mismatches": []},
                        {"complete": review.get("complete"), "mismatches": mismatches,
                         "rows": review.get("rows")})
        assert review.get("complete") is True, review
        assert not mismatches, json.dumps(mismatches, indent=2)


def _capital(text: str) -> str:
    return text[:1].upper() + text[1:]


def _hold_importance_check(j: Journey, seen: dict, typed: list[str]) -> None:
    """keel-web 070 F9 / 071 on Importance's Check screen: the counter reads *yours + n* for what the Answer named; with
    one named the screen asks for one more in the founder's words and Save is disabled (071: the screen asks before
    the server's ONE_MORE_NEEDED); with two the ask is absent and Save on. The founder types the rest of their own
    list, the counter reads *yours + 4*, the ask is gone and Save is on. The *Keel will test* box's sentence counts the
    list as it stands: *out of two* / *three*, then *five* (keel-web 070 fills `{list_size}`)."""
    named = len(vs.importance_named(j.entry))
    x = seen["importance"]
    one = named == 1
    with _step(j, f"Importance's Check screen with {named} other{'s' if named != 1 else ''} (keel-web 070 F9): "
                  f"*yours + {named}*" + (", the ask for one more, Save off until three (keel-web 071)"
                                          if one else ", no ask, Save on") +
               f"; the founder types {len(typed)} more and it reads *yours + {named + len(typed)}*",
               party="founder") as h:
        size = ["zero", "one", "two", "three", "four", "five"]
        want = {"counter": f"yours + {named}", "ask": ONE_MORE_ASK if one else "",
                "save_enabled": not one, "added": typed, "counter_after": f"yours + {named + len(typed)}",
                "ask_after": "", "save_enabled_after": True, "test": f"out of {size[1 + named]}.",
                "test_after": f"out of {size[1 + named + len(typed)]}."}
        if one:
            want["save_disabled_below_three"] = True
        have = {k: x.get(k) for k in want if k not in ("test", "test_after")}
        have["test"] = next((f"out of {w}." for w in size if (seen["test"]["belief"] or "").endswith(f"out of {w}.")),
                            seen["test"]["belief"])
        have["test_after"] = next((f"out of {w}." for w in size
                                   if ((seen.get("test_after") or {}).get("belief") or "").endswith(f"out of {w}.")),
                                  (seen.get("test_after") or {}).get("belief"))
        h.record_assert(want, have)
        assert have == want, json.dumps({"screen": have, "want": want}, indent=2)
        j.feedback["importance_typed"] = list(typed)


#: keel-web 070 `listOneMore(1)`: the Check screen's ask below three in all.
ONE_MORE_ASK = "Name one more difficulty, in your own words. People pick two of these, so the list needs three."


def _keep_draft(j: Journey, question: dict, draft: str, answer: str | None) -> None:
    """Spec 046 (FM1, FM2): a list Keel drafted, as the wire served it on `GET calibration/{vector}` -- the slice's
    first draft, or the redraft from the founder's Answer -- with the Answer it was drafted from."""
    listed = question.get("draft") or {}
    key = question.get("dimension")
    fixed = vs.NOBODY_ELSE[0] if key == "commercial.buyer_payer_alignment" else None
    items = [{"label": i.get("label"), "asked": i.get("asked"), **({"fixed": True} if fixed and i.get("code") == fixed
                                                                    else {})}
             for i in listed.get("items") or []]
    j.feedback.setdefault("lists", []).append({"dimension": key, "draft": draft, "items": items,
                                               "phrase": listed.get("phrase"), "answer": answer})


def _importance_needs_three(j: Journey) -> None:
    """keel-cloud 097 F9 on the wire (spec 046 FR-003): strangers pick two, so Importance is saved with the own item
    and at least two others. The founder's saved list cut to the own item and one other is refused **422
    ONE_MORE_NEEDED** ("name one more difficulty") and writes nothing; cut to the own item and two it is saved (200)
    and its belief reads "out of three"; the founder's own list is then saved again and reads "out of five". The page
    is reloaded after, as `_hourly_rate` does, so its next write is at the new revision."""
    key = "problem.importance"
    saved = vs.saved_list(j.entry, key)
    labels = [{"label": i["label"]} for i in saved["items"]]

    def put(items: list[dict], ok: tuple) -> tuple[int, Any]:
        body = {"expectedRevision": j.revision(),
                "answers": [{"dimension": key, "list": {"items": items, "pickedIndex": None}}]}
        return j.call("PUT", j.project("/calibration/PROBLEM"), body, ok=ok)

    def belief(rows: Any) -> str:
        return next((r.get("belief") or "" for r in (rows or {}).get("rows") or [] if r.get("dimension") == key), "")

    with _step(j, "Importance needs three on the wire (keel-cloud 097 F9): the own item and one other is refused 422 "
                  "ONE_MORE_NEEDED and writes nothing; the own item and two others saves (200, \"out of three\"); "
                  "the founder's own list saves again (\"out of five\")", party="founder", kind="protocol") as h:
        before = j.revision()
        one, one_body = put(labels[:2], (422,))
        after_one = j.revision()
        two, two_body = put(labels[:3], (200,))
        back, back_body = put(labels, (200,))
        j.page.reload(wait_until="load")
        probe = {"own+1": {"status": one, "code": _refusal(one_body),
                           "remedy": (one_body or {}).get("remedy") if isinstance(one_body, dict) else None,
                           "revision moved": after_one != before},
                 "own+2": {"status": two, "belief": belief(two_body)},
                 "own+4": {"status": back, "belief": belief(back_body)}}
        j.feedback.setdefault("importance_probe", probe)
        h.record_wire({"own+1": labels[:2], "own+2": labels[:3], "own+4": labels}, probe)
        assert (one, _refusal(one_body)) == (422, feedback_marks.ONE_MORE_NEEDED), one_body
        assert probe["own+1"]["remedy"] == "name one more difficulty", one_body
        assert not probe["own+1"]["revision moved"], probe
        assert probe["own+2"]["belief"].endswith("out of three."), probe
        want = (j.entry.founder_calibration.get(key) or {}).get("belief_sentence")
        assert not j.strict or probe["own+4"]["belief"] == want, (probe, want)


def _drawn_list(key: str, check: dict) -> dict:
    """What a Check screen drew, in the corpus's shape: the editable labels in order, Importance's locked
    own item first, Current solution's phrase, Commitment's step."""
    rows = check["rows"]
    labels = [r["text"] for r in rows if not r["locked"]]
    if key == "problem.importance":
        own = [r["text"] for r in rows if r["locked"] and r["tag"] == "yours"]
        labels = own + labels
    if key == "commercial.commitment":
        labels = [check["field"]] if check["field"] is not None else labels
    out = {"items": labels}
    if key == "problem.current_solution_satisfaction":
        out["phrase"] = check["field"]
    return out


def _corpus_list(entry, key: str) -> dict:
    """The entry's own list as a Check screen draws it: Buyer and payer's "Nobody else" is code's and
    drawn nowhere on Check (it is Choose's first radio); Importance is drawn as Keel redrafted it, the own item and what
    the Answer named (the founder types the rest there, keel-web 070 F9)."""
    saved = vs.founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != vs.NOBODY_ELSE[0]]
    if key == "problem.importance":
        labels = labels[:1 + len(vs.importance_named(entry))]
    out = {"items": labels}
    if key == "problem.current_solution_satisfaction":
        out["phrase"] = saved.get("phrase")
    return out


def _old_cost_on_the_wire(j: Journey, question: dict, answer) -> None:
    """Spec 064 FR-2 (judgement call): keel-web 094 draws the commercial chain's cost step on a fresh project, where a
    cost needs a unit and a way that are the chain's -- so a corpus cost stated before the chain (AMOUNT or HOURS, no
    unit: every golden entry's, read as revision 12) cannot be typed there. It is written on the wire as the entry
    states it (`PUT calibration/COMMERCIAL`), and the page reloaded: keel-web then draws spec 074's controls for it
    (094 judgement call 1), which the founder answers exactly as before -- and keel-cloud keeps spec 077's cost total
    and spec 073's ladder for the strangers. A chain answer is typed on the chain's screens instead (no write here)."""
    body = answer.as_wire()
    if chain_mod.cost_in_chain(body.get("cost")) or not j.corridor.chain_screen("cost_estimate"):
        return
    with _step(j, "the corpus's cost is r12's (no unit): keel-web 094 draws the chain's step on a fresh project, so the "
                  "cost is written on the wire as the entry states it and the page reloaded onto spec 074's controls",
               party="founder", kind="protocol") as h:
        view = j.get(j.project("/calibration/COMMERCIAL")) or {}
        put = {"expectedRevision": view.get("revision"), "answers": [body]}
        status, saved = j.call("PUT", j.project("/calibration/COMMERCIAL"), put)
        j.page.reload(wait_until="load")
        drawn = j.corridor.chain_screen("cost_estimate")
        h.record_wire(put, {"status": status, "saved": saved, "chain screen after": drawn})
        assert not drawn, "keel-web still draws the chain's cost step over a stored cost from before the chain"


def _hold_the_chain_screen(j: Journey, key: str, seen: dict) -> None:
    """Spec 064 FR-2 (keel-web 094): the chain's cost step reads its equation back -- the founder's unit and period
    after the boxes (*· per site · a month*) -- and the price step its locked words, held to the cost's unit and
    period (never typed, never sent)."""
    cost = j.entry.cost() or {}
    period_words = chain_mod.CHAIN_PERIOD_WORDS.get(cost.get("period"), "")
    with _step(j, f"{key}: the chain's screen reads back the founder's unit and period (keel-web 094)",
               party="founder") as h:
        drawn = seen.get("per") if key == "commercial.existing_sacrifice" else seen.get("locked")
        want = [f"per {str(cost.get('unit') or '').strip()}", period_words]
        h.record_assert(want, seen)
        missing = [w for w in want if w and w not in (drawn or "")]
        assert not missing, {"drawn": drawn, "missing": missing}


def _hourly_rate(j: Journey) -> None:
    """A B2B entry records the hourly rate its brief prices hours at. keel-web draws the rate only
    under an HOURS cost estimate, and every corpus estimate is an AMOUNT, so where keel-cloud's
    market default is not the entry's the rate is set on the wire -- and the step says which it was."""
    view = j.get(j.project("/calibration/COMMERCIAL")) or {}
    rate = (view.get("hourlyRate") or {}).get("amount")
    with _step(j, "the hourly rate is the entry's own", party="stack", kind="protocol") as h:
        if rate is not None and float(rate) == float(j.founder.hourly_rate):
            h.record_wire({"hourlyRate": j.founder.hourly_rate}, {"default": rate, "set": False})
            return
        body = {"expectedRevision": view.get("revision"), "hourlyRate": j.founder.hourly_rate}
        _, saved = j.call("PUT", j.project("/calibration/COMMERCIAL"), body)
        # The write moved the project's revision under the page the founder is on (step 5), which would post
        # its lock at the revision it read: the page is reloaded, the way a founder coming back has it.
        j.page.reload(wait_until="load")
        h.record_wire(body, {"default": rate, "set": True, "saved": saved, "reloaded": j.page.url})


def _wait_calibration(j: Journey, vector: str, *, timeout_s: float = 90) -> dict:
    deadline = time.monotonic() + timeout_s * j.patience
    view: dict = {}
    while time.monotonic() < deadline:
        view = j.get(j.project(f"/calibration/{vector}")) or {}
        if view.get("state") == "READY":
            return view
        if view.get("state") == "FAILED":
            why = j.get(f"/v2/inference-interactions/{view.get('interactionId')}") or {}
            said = f"{why.get('status')}: {why.get('diagnostic') or why.get('refusal')}"
            if _retried(j, f"{vector} calibration", said, j.project(f"/calibration/{vector}/retry")):
                deadline = time.monotonic() + timeout_s * j.patience
                continue
            raise AssertionError(f"{vector}'s calibration questions FAILED: {said}")
        time.sleep(0.5)
    raise AssertionError(f"{vector}'s calibration questions never became READY: {view}")


def _retried(j: Journey, what: str, said: str, retry_path: str) -> bool:
    """Spec 062: a failed model job retried as the founder's screen retries it, while the journey has retries left
    (`Journey.retries`, 0 but on the back-test); the failure is a finding, recorded with the screen as it stood."""
    if getattr(j, "retries", 0) <= 0:
        return False
    j.retries -= 1
    camera = getattr(j, "camera", None)
    if camera is not None:
        camera.founder(f"failed-{what.replace(' ', '-').lower()}")
    with _step(j, f"{what}: Keel's AI's result was refused, and the founder retries it (spec 062: a finding, recorded)",
               party="founder", kind="note") as h:
        status, body = j.call("POST", retry_path, {}, ok=(200, 201, 202, 204, 409, 422))
        j.findings.append({"what": what, "refused": said, "retry": {"path": retry_path, "status": status}})
        h.record_wire({"POST": retry_path, "because": said}, {"status": status, "body": body})
        # the screen is reloaded on the retried job, the way a founder pressing Try again sees it start over
        j.page.reload(wait_until="load")
    return status in (200, 201, 202, 204)


def leg_persona(j: Journey) -> None:
    """Who decides to pay, on the persona step: the same person on a B2C entry, the entry's
    decision-maker role on a B2B one -- which is what gives a B2B study its second respondent type
    and its commercial link."""
    j.corridor.persona(j.founder.decider)
    with _step(j, "the persona yields one respondent type, or two on a B2B entry") as h:
        view = j.get(j.project("/persona")) or {}
        types = view.get("respondentTypes") or []
        want = 2 if vs.is_b2b(j.entry) else 1
        h.record_assert(want, types)
        assert len(types) == want, types
        if vs.is_b2b(j.entry):
            assert sum(1 for t in types if t.get("commercialLink")) == 1, types
            assert (view.get("decider") or {}).get("role") == j.founder.decider["role"], view
            # spec 064 FR-6 (keel-cloud 123 FR-10): the title sent is the one served
            assert view.get("deciderTitle") == j.founder.decider.get("title"), view


# ---------------------------------------------------------------------------------- leg 4: lock

def leg_lock(j: Journey) -> None:
    """Step 5's three screens since keel-web 069 (*A word from you* 1 of 3, *The pilot* 2 of 3, L1 *Who asks the
    questions* 3 of 3 -- on the own door one line and *Lock and approve*; the idea moved to S2), then the lock:
    **one** RESPONDENT_QUESTIONS job (keel-cloud 091, contract 14: part 1 on the
    primary link, the gate's clause; parts 2 and 3 -- on B2B part 3 the decision-maker's link's -- composed by code in
    the lock's own commit), READY before anyone is invited, and the lock storing every saved list with its picked
    index (design §6, D7)."""
    drawn = j.corridor.word_pilot_and_lock()
    j.receipt = drawn.get("receipt") or {}
    j.screens["L1"] = drawn.get("l1") or {}
    if getattr(j, "keels_door", False):
        _keels_door_l1(j, drawn)
    else:
        _own_door_l1(j, drawn)
    _lock_lands(j)


def _keels_door_l1(j: Journey, drawn: dict) -> None:
    """Spec 062 (Keel's door, keel-web 069): L1 draws the faces' carousel with one preselected and *Lock and record the
    interviewer*; the lock records that face (fake renders on the local stack). Held: the three counters and the title;
    the rest recorded."""
    with _step(j, "step 5 is three screens -- 1 of 3, 2 of 3 and L1 *Who asks the questions* 3 of 3, which on Keel's "
                  "door is the faces' carousel and *Lock and record the interviewer* (keel-web 069; spec 062)",
               party="founder") as h:
        l1 = drawn.get("l1") or {}
        h.record_assert({"counters": ["1 of 3", "2 of 3", "3 of 3"], "title": vs_screens.L1_TITLE,
                         "button": vs_screens.BEFORE_LOCK_RECORD},
                        {**l1, "counters": drawn["counters"], "receipt": j.receipt})
        assert drawn["counters"] == ["1 of 3", "2 of 3", "3 of 3"], drawn
        assert l1.get("title") == vs_screens.L1_TITLE, l1


def _own_door_l1(j: Journey, drawn: dict) -> None:
    with _step(j, "step 5 is three screens since keel-web 069 -- 1 of 3, 2 of 3 and L1 *Who asks the questions* 3 "
                  "of 3, which on an account on its own AI is one line and *Lock and approve*, no carousel; the "
                  "lock's receipt carries no interviewer (contract 16)", party="founder") as h:
        l1 = drawn.get("l1") or {}
        h.record_assert({"counters": ["1 of 3", "2 of 3", "3 of 3"], "title": vs_screens.L1_TITLE,
                         "sub": vs_screens.BEFORE_INTERVIEWER_OWN, "carousel": False,
                         "button": vs_screens.BEFORE_LOCK_APPROVE, "receipt.interviewer": None},
                        {**l1, "counters": drawn["counters"], "receipt": j.receipt})
        assert drawn["counters"] == ["1 of 3", "2 of 3", "3 of 3"], drawn
        assert l1.get("title") == vs_screens.L1_TITLE and l1.get("carousel") is False, l1
        assert l1.get("sub") == vs_screens.BEFORE_INTERVIEWER_OWN, l1
        assert l1.get("button") == vs_screens.BEFORE_LOCK_APPROVE, l1
        assert "interviewer" not in j.receipt, j.receipt


def _lock_lands(j: Journey) -> None:
    deadline = time.monotonic() + 120 * j.patience
    state = None
    while time.monotonic() < deadline:
        state = (j.get(j.project("/overview")) or {}).get("questionsState")
        if state == "FAILED" and _retried(j, "the questionnaire", "questionsState FAILED after the lock",
                                          j.project("/questionnaire/retry")):
            deadline = time.monotonic() + 120 * j.patience
            continue
        if state in ("READY", "FAILED"):
            break
        time.sleep(0.5)
    if state == "FAILED":
        # runs/DRIFT.md #81, closed by keel-cloud 091 FR-B (FAILED is believed over a fresh project): spec 041 read
        # again once before believing a FAILED. Spec 042 keeps no re-read -- a FAILED now fails the journey, and the
        # step says #81 may have come back if the job itself landed.
        interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
        landed = [i.get("status") for i in interactions if i.get("screen") == "RESPONDENT_QUESTIONS"]
        with _step(j, f"{j.entry.id}: the overview read the questions FAILED -- DRIFT #81 is closed by keel-cloud "
                      "091, so this is a failure, not a race to step round", party="stack") as h:
            h.record_assert({"questionsState": "READY"}, {"questionsState": state, "jobs": landed})
            raise AssertionError(f"questionsState FAILED after the lock (RESPONDENT_QUESTIONS jobs: {landed}); "
                                 "DRIFT #81 came back if every job is APPLIED")
    with _step(j, "the lock started ONE RESPONDENT_QUESTIONS job -- part 1, the gate's clause -- and no other "
                  "(keel-cloud 091, contract 14: LockReceipt.questions.interactionIds is exactly 1)") as h:
        ids = list(((j.receipt.get("questions") or {}).get("interactionIds")) or [])
        interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
        respondent = [i for i in interactions if i.get("screen") == "RESPONDENT_QUESTIONS"]
        h.record_assert({"interactionIds": 1, "RESPONDENT_QUESTIONS jobs": 1, "status": "APPLIED"},
                        {"receipt": j.receipt, "jobs": [{k: i.get(k) for k in ("interaction_id", "status", "job")}
                                                         for i in respondent]})
        assert len(ids) == 1, j.receipt
        retried = any(f.get("what") == "the questionnaire" for f in getattr(j, "findings", None) or [])
        if retried and len(respondent) > 1:
            # spec 062 follow-up (2026-10-22): on the back-test a questionnaire Keel's AI failed was retried the way the
            # founder's screen retries it (`_lock_lands`), so the project holds the refused job and the retried one;
            # the receipt's is among them and the last one landed -- recorded above, the retry is a finding already
            assert ids[0] in [i.get("interaction_id") for i in respondent], (ids, respondent)
            assert any(i.get("status") == "APPLIED" for i in respondent), respondent
        else:
            assert [i.get("interaction_id") for i in respondent] == ids, (ids, respondent)
            assert respondent[0].get("status") == "APPLIED", respondent[0]
    with _step(j, "the study is version 1, the three parts' questions are written, READY, and the lock "
                  "holds every saved list and its picked index (D7)") as h:
        plan = j.get(j.project("/plan")) or {}
        lists = plan.get("lists") or {}
        want = {key: vs.saved_list(j.entry, key) for v in VECTORS for key in vs.founder_keys(j.entry, v)
                if vs.is_list(key) and not j.entry.unsure(key)}
        have = {key: {"items": [{k: i.get(k) for k in ("code", "label", "asked") if i.get(k) is not None}
                                for i in (lists.get(key) or {}).get("items") or []],
                      "pickedIndex": (lists.get(key) or {}).get("pickedIndex"),
                      "phrase": (lists.get(key) or {}).get("phrase")} for key in want}
        h.record_assert({"locked": True, "version": 1, "questionsState": "READY",
                         "lists": want if j.strict else sorted(want)},
                        {"locked": plan.get("locked"), "version": plan.get("version"),
                         "questionsState": state, "lists": lists})
        assert plan.get("locked") is True and plan.get("version") == 1, plan
        assert state == "READY", (state, plan.get("questions"))
        assert set(want) <= set(lists), (sorted(want), sorted(lists))
        if j.strict:
            assert have == want, json.dumps({"lock": have, "corpus": want}, indent=2)


# -------------------------------------------------------------------------------- leg 5: invite

def leg_invite(j: Journey) -> None:
    """One link per corpus person, in corpus order, through keel-web 068's Interviews section (spec 043's second
    commit; the People page and its two popups are gone): Sent, W1 the walkthrough the first time this account
    arrives, then each kind's *Send the questions* / *Send more* -- Text, *Someone I know*, the person's name, *Make
    their link* -- for the specialist and, on a B2B entry, the decision-maker (one `POST invitations/batch` for both,
    068 call 11). The register is then held to the wire: newest link first, one row a person, Text, not opened."""
    register = j.get(j.project("/invitations")) or {}
    labels = {k.get("respondentType"): k.get("label") for k in register.get("kinds") or []}
    persona = j.get(j.project("/persona")) or {}
    primary = next(t for t in persona.get("respondentTypes") or [] if not t.get("commercialLink"))
    sent = iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    if getattr(j, "camera", None) is not None:
        sent.camera = j.camera.founder
    me_before = j.get("/v2/me") or {}
    # spec 059: the guide journey holds keel-web 088's Interviews sheet up at its first open and judges it (G13)
    walked = interviews_sheet(j, sent) if j.teach is not None else sent.land(j.project_id)
    with _step(j, "Interviews (keel-web 068 FR-002 / FR-003): the side nav's group with its three sub-rows, Sent "
                  "current; the walkthrough played exactly when the account had never seen it, and Got it stamped it",
               party="founder") as h:
        nav = sent.nav()
        me_after = j.get("/v2/me") or {}
        h.record_assert({"row": iv_screens.NAV_INTERVIEWS, "subs": iv_screens.SUBPAGES, "current": ["Sent"],
                         "walkthrough": me_before.get("walkthroughSeenAt") is None},
                        {"nav": nav, "walkthrough": walked, "seen before": me_before.get("walkthroughSeenAt"),
                         "seen after": me_after.get("walkthroughSeenAt")})
        assert nav["row"] == iv_screens.NAV_INTERVIEWS and (nav["href"] or "").endswith(
            f"/p/{j.project_id}/interviews/sent"), nav
        assert nav["subs"] == iv_screens.SUBPAGES and nav["current"] == ["Sent"], nav
        assert (walked is not None) == (me_before.get("walkthroughSeenAt") is None), (walked, me_before)
        if walked is not None:
            assert walked["title"] == iv_screens.WALKTHROUGH_TITLE and walked["patch"]["status"] == 200, walked
        assert me_after.get("walkthroughSeenAt"), me_after
    for person in j.people:
        kind = vs.LINK_B2B if person.link == vs.LINK_B2B else vs.LINK_PRIMARY
        about = None if kind == vs.LINK_B2B else f"{primary.get('label')}, asked about one real time."
        made = sent.send_someone(j.project_id, labels[kind], person.person, about)
        link = ((made["batch"] or {}).get("links") or [{}])[0]
        with _step(j, f"{person.person}: one link on the {kind} kind, handed back once and drawn as it came",
                   party="founder") as h:
            h.record_assert({"status": 201, "format": "TEXT", "drawn": link.get("url"), "personName": person.person},
                            {"status": made["status"], "format": (made["batch"] or {}).get("format"),
                             "drawn": made["url"], "link": link, "formats": made["formats"]})
            assert made["status"] == 201 and (made["batch"] or {}).get("format") == "TEXT", made
            assert made["url"] == link.get("url") and link.get("personName") == person.person, made
            # keel-web 069: *Text only*; on their own AI the other two greyed *needs Keel's credits*
            assert made["formats"].get(iv_screens.TEXT_ONLY, {}).get("checked") is True, made["formats"]
            if not getattr(j, "keels_door", False):  # spec 062: on Keel's door the other two are offered, and not picked
                assert all(f["disabled"] and f["word"] == iv_screens.FORMAT_NEEDS_CREDITS
                           for name, f in made["formats"].items() if name != iv_screens.TEXT_ONLY), made["formats"]
        j.links[person.person] = made["url"]
        j.tokens[person.person] = made["url"].rstrip("/").rsplit("/", 1)[-1]
    with _step(j, "every corpus person has a link of their own; the Sent register draws one row a person, newest "
                  "link first, as the wire lists them", party="founder") as h:
        wire = (j.get(j.project("/invitations")) or {}).get("invitations") or []
        drawn = sent.register()
        h.record_assert({"links": len(j.people), "order": [p.person for p in j.people][::-1]},
                        {"links": len(set(j.tokens.values())), "wire": [r.get("personName") for r in wire],
                         "drawn": drawn})
        assert len(set(j.tokens.values())) == len(j.people), j.tokens
        assert [r.get("personName") for r in wire] == [p.person for p in j.people][::-1], wire
        assert [r.get("Who") for r in drawn] == [r.get("personName") for r in wire], drawn
        assert {r.get("Format") for r in drawn} == {"Text"}, drawn
        assert all((r.get("Status") or "").startswith(iv_screens.REGISTER_STATUS["SENT"]) for r in drawn), drawn
    if j.teach is not None:
        # spec 059: Sent's order and the role counts (G15, G17), the links table (G16), Sent's pill (G14)
        sent_reading(j, "after the links", sent)
        links_reading(j, "after the links", sent)
        sent_pill(j)
    # keel-web 077 (spec 052 FR-7): before anyone finishes, the report is the too-few state (the pilot tile *None yet*).
    j.standings = j.get(j.project("/standings")) or {}
    report_sheet(j)
    _too_few(j, "before anyone answered")


# ----------------------------------------------------------------------------- leg 6: interview

def leg_interview(j: Journey) -> None:
    """Each person on their own link, in their own browser context with no founder session, through
    keel-web 064's screens: the decision-maker's idea screen first, the gate and its one chip, every item
    as served -- its kicker, its stem, its options, its ONE escape drawn last (none on Commitment) --
    Importance's two picks, the fixed answers, "nothing" typed as 0. The screens are held to the wire on
    every journey; the body the page POSTs is held to the corpus person's own answers, by item and by
    option id. The founder has their AI read after each person, so the scripted readings land on the
    corpus's own people in order."""
    for i, person in enumerate(j.people):
        _answer_one(j, person, j.tokens[person.person])
        _read(j, person)
        if i == 3:
            _too_few_answered(j, 4)
    _themes_on_return(j)


def _themes(j: Journey) -> list[dict]:
    interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
    return [i for i in interactions if i.get("screen") == "THEMES"]


#: An interaction still to land (keel-cloud `InteractionStatus`): the THEMES job is not done while one is open.
OPEN_STATUSES = {"PENDING", "CLAIMED", "RUNNING", "QUEUED", "DRAFT", "NEEDS_INPUT"}


def _themes_on_return(j: Journey, *, timeout_s: float = 90) -> None:
    """keel-cloud 104 (FR-4, `ThemesOnReturn`): the insights go stale on each new response and are regrouped when the
    founder comes back -- the founder's own read of the project (`GET overview` on their session) starts at most one
    THEMES job a failing dimension with follow-up answers, and each lands (a lost race retried, as the brief's was).
    The step waits until no THEMES is open and every served insight with answers carries themes or the raw fallback,
    and records what it saw; what the Insights view must say is `report_insights`'s (spec 052)."""
    with _step(j, "the insights wait for the founder (keel-cloud 104): the founder opens the project (GET overview), "
                  "at most one THEMES job a failing dimension is started, and every one lands",
               party="founder") as h:
        before = _themes(j)
        j.get(j.project("/overview"))
        deadline = time.monotonic() + timeout_s * j.patience
        standings: dict = {}
        while True:
            after = _themes(j)
            standings = j.get(j.project("/standings")) or {}
            # keel-cloud 119 (FR-4): every insight GROUPED or RAW -- GROUPING is still being grouped
            settled = all(i.get("state") in ("GROUPED", "RAW") for i in standings.get("insights") or [])
            if (settled and not any(t.get("status") in OPEN_STATUSES for t in after)) or time.monotonic() > deadline:
                break
            time.sleep(1)
        failing = report_marks.failing_dimensions(standings)
        seen = {t.get("interaction_id") for t in before}
        opened = [t for t in after if t.get("interaction_id") not in seen and t.get("status") != "STATE_CONFLICT"]
        h.record_assert({"THEMES on this return": f"at most one a failing dimension ({len(failing)} failing)",
                         "open": 0},
                        {"before": [(t.get("status"), t.get("interaction_id")) for t in before],
                         "after": [(t.get("status"), t.get("interaction_id")) for t in after],
                         "insights": [{k: i.get(k) for k in ("dimension", "answered", "state", "raw")}
                                      | {"themes": len(i.get("themes") or [])}
                                      for i in standings.get("insights") or []]})
        assert not any(t.get("status") in OPEN_STATUSES for t in after), after
        assert len(opened) <= len(failing), (opened, failing)
        bad = [t for t in after if t.get("status") in TERMINAL_BAD and t.get("status") != "STATE_CONFLICT"]
        if bad and getattr(j, "retries", 0):
            # spec 062: on the back-test an insight Keel's AI could not group is a finding, recorded, not the end
            j.findings.extend({"what": "THEMES", "refused": f"{t.get('status')}: {t.get('diagnostic')}"} for t in bad)
            bad = []
        assert not bad, bad


def _deciding_now(j: Journey) -> list[str]:
    """The called stages' deciding lines of the standings as they stand (keel-cloud 118 `FollowUpComposer.deciding`),
    read off the wire; none where no project is read (a stub)."""
    if not hasattr(j, "get") or not hasattr(j, "project"):
        return []
    return fake.deciding_lines(j.get(j.project("/standings")) or {})


def _typing(person, line: str | None):
    """`person` typing `line` on the follow-up they are asked (`vs.follow_up_line`)."""
    import dataclasses                                                 # noqa: PLC0415
    if dataclasses.is_dataclass(person):
        return dataclasses.replace(person, follow_up=line)
    person.follow_up = line
    return person


def _served_options(j: Journey, person, items: dict):
    """Spec 064 FR-7: a corpus *yes, after trying it first* the script put on *probably not* (no smaller step on the
    founder's list, so keel-cloud 118 serves no conditional yes) goes back to the conditional option where the
    interview serves one (`conditional: true`, a model-drafted smaller step on Keel's AI); every remap left standing is
    a finding, named with what was served."""
    import dataclasses                                                 # noqa: PLC0415
    if not getattr(person, "remapped", ()):
        return person
    item = items.get("commercial.commitment") or {}
    conditional = any(o.get("conditional") for o in item.get("options") or [])
    if conditional:
        picks = [dataclasses.replace(p, codes=[vs.CONDITIONAL_YES]) if p.dimension == "commercial.commitment"
                 and p.codes == [vs.NOT_SERVED_YES] else p for p in person.picks]
        return dataclasses.replace(person, picks=picks, remapped=())
    j.findings.append({"what": f"{person.person}: Commitment's corpus pick yes_after_trying has no served option "
                               "(keel-cloud 118: no smaller step on the founder's list); sent as probably_not",
                       "served": [o.get("label") for o in item.get("options") or []]})
    return person


def _answer_one(j: Journey, person, token: str) -> None:
    stranger = j.browser.new_context()
    try:
        interview = stranger.request.get(f"{j.cloud_base}/v2/i/{token}/interview",
                                         timeout=20_000).json()
        j.interviews[person.person] = interview
        items = {i.get("dimension"): i for part in interview.get("parts") or []
                 for i in part.get("items") or []}
        kind = "COMMERCIAL_LINK" if person.link == vs.LINK_B2B else "FULL"
        with _step(j, f"{person.person}: the {kind} interview carries every item this person "
                      "answers, and every option they pick", party="participant") as h:
            missing = [p.dimension for p in person.picks if p.dimension not in items]
            unoffered = []
            for pick in person.picks:
                item = items.get(pick.dimension) or {}
                offered = {o.get("optionId") for o in item.get("options") or []}
                offered |= {o.get("optionId") for o in (item.get("plan") or {}).get("options") or []}
                offered |= {a.get("id") for a in item.get("advantages") or []}
                unoffered += [(pick.dimension, code) for code in pick.codes + pick.advantages
                              if vs.option_id(token, pick.dimension, code) not in offered]
                box = item.get("valueBox") or {}
                chips = {(item.get("escape") or {}).get("code"), (box.get("nothing") or {}).get("code")}
                chips |= {c.get("code") for c in box.get("chips") or []}
                if pick.chip and pick.chip not in chips:
                    unoffered.append((pick.dimension, pick.chip))
            h.record_assert({"kind": kind, "missing": [], "unoffered": []},
                            {"kind": interview.get("kind"), "missing": missing,
                             "unoffered": unoffered, "items": sorted(items)})
            assert interview.get("kind") == kind, interview.get("kind")
            assert not missing, missing
            if j.strict:
                assert not unoffered, unoffered
        person = _served_options(j, person, items)
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        expected = person.response(token, recall)
        if unoffered:
            expected = _on_the_offered_options(expected, items)
        by_item = {a["itemId"]: a for a in expected.get("answers") or []}
        # spec 051 FR-5: one person a scenario speaks the story through the box (the text page's seam), one under a
        # refused microphone; everyone else's page runs with no seam at all -- and on the remote profile no page does
        speak = _speak_for(j, person)
        if speak:
            stranger.add_init_script(ivs.text_seam(refused=speak == "refused"))
        # spec 064 FR-7 (keel-cloud 118 FR-4): the deciding lines of the standings this person answers into are walked
        # first -- read off the served standings (`interviewer_fake.deciding_lines`), never recounted here
        inside = getattr(person, "in_segment", True)
        deciding = _deciding_now(j) if (person.link == vs.LINK_B2B or (person.recency and inside)) else []
        owed = vs.follow_up_question(j.entry, person.picks, person.link, interview, token, first=deciding) \
            if (person.link == vs.LINK_B2B or (person.recency and inside)) else None
        if owed is not None:
            owed["deciding"] = deciding
            person = _typing(person, vs.follow_up_line(j.entry, person, owed))
        page = stranger.new_page()
        screens = vs_screens.Interview(page, j.recorder)
        if getattr(j, "camera", None) is not None:
            screens.camera = j.camera.respondent(person, page)
        screens.open(j.links[person.person])
        walked = screens.walk(person, interview, by_item, follow_up=person.follow_up, speak=speak)
        j.walked[person.person] = walked
        _hold_the_screens(j, person, interview, walked)
        _hold_the_consent(j, person, walked)
        if speak:
            expected = _hold_the_box(j, person, interview, walked, expected, speak)
        _hold_the_follow_up(j, person, interview, walked, owed)
        with _step(j, f"{person.person}: the page sent exactly this person's answers",
                   party="participant") as h:
            sent = walked["body"] or {}
            h.record_assert(expected, sent)
            assert walked.get("status") in (200, 201), walked.get("status")
            assert _normal_body(sent) == _normal_body(expected), (sent, expected)
            h.capture_text("participant_page", "\n\n".join(walked["seen"]))
        if person.pilot_opt_in:
            screens.opt_in_to_pilot(interview)
    finally:
        stranger.close()


#: Why the story's box is typed on the remote profile (amendment 2026-10-17): keel-web reads the speech seam
#: (`window.__keelSpeech`) only in its test build (`import.meta.env.MODE === "test"`), and staging serves the production
#: build -- so `text_seam` would be ignored there and the box would never leave *listening*.
REMOTE_TYPES = ("keel-web reads window.__keelSpeech only in its test build and staging serves the production build, "
                "so the story is typed and the box's T1 -> T4 / T6 (IM26's speak) is skipped on the remote profile")


def _speak_for(j: Journey, person) -> str | None:
    """Spec 051 FR-5's speaker (`vs.STORY_SPOKEN`: "quiet", "done" or "refused") for this person's story, or None:
    nobody else speaks, and on the remote profile nobody does -- the page gets no seam, the story is typed as everyone
    else's is, and `_hold_the_box` is not run (the step says why)."""
    speak = vs.STORY_SPOKEN.get(j.entry.id, {}).get(person.person) if person.recency and person.story else None
    if speak and getattr(j.stack, "is_remote", False):
        with _step(j, f"{person.person}: the story's box is typed, not spoken ({speak}) -- {REMOTE_TYPES}",
                   party="participant", kind="note") as h:
            h.record_wire({"profile": getattr(j.stack, "profile", None), "speak": speak},
                          {"skipped": "IM26 speak: the seam, the take, T1 -> T4 / T6", "typed": True})
        return None
    return speak


#: keel-cloud 103 `InterviewComposer.CONSENT_TEXT` (D17, design §9): names travel with the words now. The served line,
#: held to keel-cloud's source by `tests/test_interviewer_marks.py`.
CONSENT_TEXT = ("Keel is storing what you say here and sharing it with the founder who invited you, with your name as "
                "they have it; they may quote your words in their report. There is no way to delete it once you send it.")
#: keel-web 069-075's door line, gone with keel-web 076 FR-5 (`CONSENT_PARTICIPANT_KEEL`).
CONSENT_GONE = "Nothing here asks for your name"


def _hold_the_consent(j: Journey, person, walked: dict) -> None:
    """Spec 051 FR-9 (keel-cloud 103 FR-8, keel-web 076 FR-5), a plain assertion: the intro's consent block is the
    served line -- the name as the founder has it, quotable in their report -- and the old door line is gone."""
    with _step(j, f"{person.person}: the intro's consent says the name travels with the words and may be quoted "
                  "(keel-cloud 103, D17); Nothing here asks for your name is gone", party="participant") as h:
        drawn = (walked.get("consent") or {}).get("text") or ""
        served = (j.interviews.get(person.person) or {}).get("consentText")
        h.record_assert({"served": CONSENT_TEXT, "drawn": CONSENT_TEXT, "gone": CONSENT_GONE},
                        {"served": served, "drawn": drawn})
        assert served == CONSENT_TEXT and " ".join(drawn.split()) == CONSENT_TEXT, (served, drawn)
        assert "with your name as they have it" in drawn and "quote your words in their report" in drawn, drawn
        assert CONSENT_GONE not in " ".join(walked.get("seen") or []), "the old door line is still drawn"


def _hold_the_box(j: Journey, person, interview: dict, walked: dict, expected: dict, how: str) -> dict:
    """Spec 051 FR-5 (keel-web 076 FR-6..FR-8; design §6's frames), on the story's box: T1 idle -- the placeholder,
    the *Speak* pill, nothing asked of the microphone and nothing recorded; T2 listening on the tap -- the card, the
    waveform, the clock *m:ss · up to 1:00*, Cancel and Done, Continue off; T3 *Writing it down…* with *Microphone off*;
    T4 heard -- the fake transcriber's words **appended** to what was typed, the caret at the end, *Heard you.*, the pill
    *Add more*; `transcribe` with `maxSeconds` 60 against the gate's item; the take ended by the 4 s quiet or by Done.
    T6 (refused): the tap asks once, the pill goes, the footer says so, the story is typed. Returns the body the page
    owes: the story as the box holds it."""
    x = walked.get("speak") or {}
    gate_item = (interview.get("gate") or {}).get("itemId")
    with _step(j, f"{person.person}: the story's box -- speak or type (keel-web 076, T1 -> T4" +
               (", T6: the microphone refused" if how == "refused" else f", the take ended by {how}") + ")",
               party="participant") as h:
        t1, before, after = x.get("t1") or {}, x.get("before_pill") or {}, x.get("after_pill") or {}
        record = {"person": person.person, "how": how, "t1": t1, "before_pill": before, "after_pill": after}
        h.record_assert({"t1": {"state": "idle", "pill": ivs.SPEAK_LABEL, "placeholder": ivs.SPEAK_OR_TYPE_PLACEHOLDER},
                         "before the pill": {"acquired": 0, "recordings": 0}}, x)
        assert t1.get("state") == "idle" and t1.get("pill") == ivs.SPEAK_LABEL, t1
        assert t1.get("placeholder") == ivs.SPEAK_OR_TYPE_PLACEHOLDER, t1
        assert before.get("acquired") == 0 and not before.get("starts"), before
        if how == "refused":
            t6 = x.get("t6") or {}
            record.update({"t6": t6, "pill_after": x.get("t6_pill"), "sent": None})
            assert t6.get("state") == "typing-only" and t6.get("footer") == ivs.SPEAK_MIC_OFF, t6
            assert x.get("t6_pill") == 0 and t6.get("placeholder") == ivs.SPEAK_TYPE_PLACEHOLDER, x
            assert after.get("acquired") == 1 and not after.get("starts"), after
            j.speak[person.person] = record
            return expected
        t2, t3, t4 = x.get("t2") or {}, x.get("t3") or {}, x.get("t4") or {}
        heard = [t for t in walked.get("transcribed") or [] if t.get("itemId") == gate_item]
        words = (heard[-1].get("text") or "").strip() if heard else ""
        want = f"{person.story.rstrip()} {words}" if words else person.story
        counts = x.get("counts") or {}
        ended_ms = None
        if how == "quiet":
            ended_ms = round((counts.get("stops") or [0])[-1] - x["quiet_at"]) if counts.get("stops") else None
        record.update({"t2": t2, "t3": t3, "t4": t4, "transcribed": heard, "appended": words, "want": want,
                       "continue_enabled_listening": x.get("continue_enabled_listening"), "counts": counts,
                       "quiet_to_stop_ms": ended_ms, "sent": (walked.get("body") or {}).get("story")})
        h.record_assert({"t2": {"state": "listening", "card": True, "wave": True, "clock": f"m:ss · up to "
                                                                                       f"{ivs.STORY_CAP}"},
                         "t3": {"state": "writing", "writing": ivs.WRITING_DOWN, "footer": ivs.MIC_OFF},
                         "t4": {"state": "heard", "value": want, "caret": len(want), "footer": ivs.SPEAK_HEARD,
                                "pill": ivs.SPEAK_ADD_MORE},
                         "transcribe": {"itemId": gate_item, "maxSeconds": 60, "status": 200}}, record)
        assert t2.get("state") == "listening" and t2.get("card") and t2.get("wave"), t2
        assert t2.get("cancel") and t2.get("done"), t2
        assert (t2.get("clock") or "").endswith(f"· up to {ivs.STORY_CAP}"), t2
        # read across 600 ms: Continue goes off through the box's state a render after the card is drawn (D-02)
        record["continue_while_listening"] = x.get("continue_while_listening")
        assert x.get("continue_enabled_listening") is False, x.get("continue_while_listening")
        assert after.get("acquired") == 1 and len(after.get("starts") or []) == 1, after
        assert t3.get("state") == "writing" and t3.get("writing") == ivs.WRITING_DOWN, t3
        assert t3.get("footer") == ivs.MIC_OFF, t3
        assert len(heard) == 1 and heard[0].get("maxSeconds") == 60 and heard[0].get("status") == 200, heard
        assert words, heard
        assert t4.get("state") == "heard" and t4.get("value") == want, (t4, want)
        assert t4.get("caret") == len(want) == t4.get("caretEnd"), t4
        assert t4.get("footer") == ivs.SPEAK_HEARD and t4.get("pill") == ivs.SPEAK_ADD_MORE, t4
        if how == "quiet":
            # the recorded path's quiet on a free-text window: 4 s after the last sound (keel-web 082 D36) (the level is read ten times a second)
            assert ended_ms is not None and ivs.SILENCE_FREE_MS - 500 <= ended_ms <= ivs.SILENCE_FREE_MS + 500, ended_ms
        else:
            assert x.get("done_at") is not None and (counts.get("stops") or [0])[-1] >= x["done_at"], x
        j.speak[person.person] = record
    return {**expected, "story": want}


def _hold_the_follow_up(j: Journey, person, interview: dict, walked: dict, owed: dict | None) -> None:
    """Spec 051 FR-4 (keel-cloud 103's route, keel-web 076 FR-1..FR-4): *Send my answers* posted the answers to the
    follow-up route (never after a gate No); it answers 200 exactly when the harness's own walk (`first_rung`) owes a
    follow-up, on that rung, its text the harness's own composition (judgement call 1), the spoken wording the
    registry's, no clip on a text link; the screen draws *One last thing*, that text, the note, the box, *Continue* off
    while empty and *Skip this one*; the response's `followUp` is the line typed (TYPED, `skipped` false) or the skip
    (`skipped` true, no text) -- and is absent when nothing is owed."""
    route = walked.get("follow_up_route") or {}
    seen = walked.get("follow_up") or {}
    sent = (walked.get("body") or {}).get("followUp")
    asked = person.link == vs.LINK_B2B or bool(person.recency)
    want_rung = (owed or {}).get("dimension")
    with _step(j, f"{person.person}: the one follow-up -- " + (f"owed on {want_rung}, asked and "
                                                               + ("typed" if person.follow_up else "skipped")
                                                               if owed else "nothing owed, nothing asked"),
               party="participant") as h:
        body = route.get("body") or {}
        record = {"person": person.person, "link": person.link, "owed": owed, "route": route, "screen": seen,
                  "sent": sent, "line": person.follow_up, "asked": asked}
        j.follow_ups[person.person] = record
        h.record_assert({"route": (200 if owed else 204) if asked else "not called", "dimension": want_rung,
                         "text": (owed or {}).get("text"), "screen": FOLLOW_UP_SCREEN if owed else None,
                         "followUp": _want_follow_up(owed, person.follow_up)}, record)
        if not asked:
            assert not route and not seen and sent is None, record
            return
        if getattr(j, "camera", None) is not None and bool(owed) != (route.get("status") == 200):
            # spec 062 follow-up (2026-10-22): on the back-test Keel's own drafted lists are served, so the rung the
            # product owes a follow-up on can differ from the harness's own walk (`first_rung`, computed on the
            # file's lists); what the product asked is the finding, and the person's page answered it (typed their
            # own line, or skipped where none was written for that rung)
            j.findings.append({"what": f"{person.person}: follow-up {'asked' if route.get('status') == 200 else 'not asked'}"
                                       f" where the harness owed {'one on ' + str(want_rung) if owed else 'none'}",
                               "refused": json.dumps({"route": body.get("dimension"), "text": body.get("text"),
                                                      "sent": sent})[:400]})
            return
        assert route.get("status") == (200 if owed else 204), route
        assert sent == _want_follow_up(owed, person.follow_up), {"sent": sent, "want": _want_follow_up(
            owed, person.follow_up)}
        if not owed:
            assert not seen, seen
            return
        assert body.get("dimension") == want_rung and body.get("spoken") == owed["spoken"], body
        assert body.get("itemId") and "clip" not in body, body                      # a text link plays nothing
        if j.strict:
            assert body.get("text") == owed["text"], {"route": body.get("text"), "harness": owed["text"]}
        assert seen.get("kicker") == ivs.FOLLOW_UP_KICKER and seen.get("question") == body.get("text"), seen
        assert seen.get("note") == ivs.FOLLOW_UP_NOTE and seen.get("skip") == ivs.FOLLOW_UP_SKIP, seen
        assert seen.get("continue_enabled_empty") is False, seen
        assert (seen.get("box") or {}).get("state") in ("idle", "typing-only"), seen.get("box")
        assert seen.get("did") == ("typed" if person.follow_up else "skipped"), seen
        if person.follow_up:
            assert seen.get("continue_enabled_typed") is True, seen


#: What the follow-up screen draws (keel-web 076 FR-3), for the step's record.
FOLLOW_UP_SCREEN = {"kicker": ivs.FOLLOW_UP_KICKER, "note": ivs.FOLLOW_UP_NOTE, "skip": ivs.FOLLOW_UP_SKIP}


def _want_follow_up(owed: dict | None, line: str | None) -> dict | None:
    """The response's `followUp` keel-web owes (076 judgement call 10): `{dimension, text, how, skipped: false}` typed,
    `{dimension, skipped: true}` skipped, none when nothing is owed."""
    if not owed:
        return None
    if line:
        return {"dimension": owed["dimension"], "text": line, "how": "TYPED", "skipped": False}
    return {"dimension": owed["dimension"], "skipped": True}


def _hold_the_screens(j: Journey, person, interview: dict, walked: dict) -> None:
    """keel-web 064, held to the wire on every journey: the decision-maker's link opens with the idea's
    three lines under the served kicker (D9); the gate's story chip is *I can't recall one particular
    {occasion}* alone; every item draws its served kicker and stem, its served options as rows, *Pick two.*
    on Importance, and its ONE escape -- the served label, after the control and before the buttons, none
    on Commitment."""
    for u in walked.get("unanswered") or []:
        j.findings.append({"what": f"{person.person}: the file has no pick on {u.get('dimension')}, which the link "
                                   f"asks; the walk took the escape {u.get('took')!r} (entry gap)", "served": u})
    with _step(j, f"{person.person}: every screen draws what the wire served -- the kicker, the stem, the "
                  "options, one escape last", party="participant") as h:
        faults = []
        screens = walked["screens"]
        idea = interview.get("idea")
        if interview.get("kind") == "COMMERCIAL_LINK" and idea:
            first = screens[0] if screens else {}
            if first.get("screen") != "idea" or first.get("kicker") != idea.get("kicker") \
                    or (idea.get("what") or "") not in (first.get("card") or ""):
                faults.append({"idea screen": first, "served": idea})
        gate = next((s for s in screens if s.get("screen") == "gate"), None)
        served_gate = interview.get("gate") or {}
        if gate is not None and person.recency:
            # keel-cloud 123 FR-3 / keel-web 099: the occasion's chip, then *I'd rather not say* where served
            want = [vs_screens.gate_chip_word(interview.get("occasion"))] + (
                [vs_screens.GATE_RATHER_NOT_SAY] if "RATHER_NOT_SAY" in (served_gate.get("chips") or []) else [])
            if [c.strip() for c in gate["chips"]] != want:
                faults.append({"gate chips": gate["chips"], "want": want})
        condition = served_gate.get("condition")
        if gate is not None and condition:
            # keel-cloud 120 / keel-web 096: the segment's chip before the gate, its question as served
            if (gate.get("chip") or {}).get("question") != condition.get("question"):
                faults.append({"segment chip": gate.get("chip"), "served": condition})
        if gate is not None and j.strict and interview.get("kind") == "FULL" and gate.get("question") is not None \
                and gate["question"] != served_gate.get("question"):
            faults.append({"gate": gate["question"], "served": served_gate.get("question")})
        by_dimension = {i.get("dimension"): i for p in interview.get("parts") or [] for i in p.get("items") or []}
        for drawn in (s for s in screens if s.get("screen") == "item"):
            item = by_dimension.get(drawn["dimension"]) or {}
            escape = item.get("escape")
            want = {"kicker": item.get("kicker"), "chips": [escape["label"]] if escape else []}
            box = item.get("valueBox")
            if box:
                # spec 064 FR-3 (keel-cloud 115): the value box draws its Nothing chip, then the chips recorded apart;
                # the registry's one escape (I don't know) is among them, never drawn twice
                want["chips"] = []
                for c in [box.get("nothing")] + list(box.get("chips") or []) + ([escape] if escape else []):
                    if c and c.get("label") and c["label"] not in want["chips"]:
                        want["chips"].append(c["label"])
            # keel-cloud 115 FR-4: an up-front-then price is one item drawn as two screens -- the up-front ladder, then
            # the plan's ("And after that, what would it be worth to you a month, per person?" with its own six rungs);
            # a drawn screen whose stem is the plan's is held to the plan's rows and question
            plan = item.get("plan") or {}
            on_plan = bool(plan) and drawn.get("question") == plan.get("question")
            if item.get("control") in ROW_CONTROLS:
                want["rows"] = [o.get("label") for o in (plan.get("options") if on_plan else item.get("options")) or []]
            if item.get("control") == "pick_two":
                want["hint"] = vs_screens.IV_PICK_TWO
            if not item.get("priceAnchor"):
                want["question"] = plan.get("question") if on_plan else item.get("question")
            have = {k: drawn.get(k) for k in want}
            if have != want:
                faults.append({"dimension": drawn["dimension"], "screen": have, "wire": want})
            order = drawn.get("order") or []
            control = next((n for n, c in enumerate(order) if "iv-control" in str(c)), None)
            chips = next((n for n, c in enumerate(order) if "iv-chips" in str(c)), None)
            buttons = next((n for n, c in enumerate(order) if "iv-actions" in str(c)), None)
            if escape and not (control is not None and chips is not None and buttons is not None
                               and control < chips < buttons):
                faults.append({"dimension": drawn["dimension"], "escape not last": order})
            if drawn["dimension"] == "commercial.commitment" and escape is not None:
                faults.append({"dimension": drawn["dimension"], "escape": escape, "want": None})
        h.record_assert([], faults)
        assert not faults, json.dumps(faults, indent=2)
    _hold_the_idea_name(j, person, interview, walked)


#: The dimension whose stem carries the idea's name (keel-cloud 085 / 091 `BenefitFirst.question`).
RA_KEY = "solution.relative_advantage"


def _hold_the_idea_name(j: Journey, person, interview: dict, walked: dict) -> None:
    """keel-cloud 090 (D14) on every journey: the idea card strangers read is *Imagine {name}.* and the Relative
    advantage question *On your last {occasion}, would {name} have made things better, or not?*, both composed by code
    around the idea's **current** name -- the one the wire stored after S2 (`IdeaView.shortName`): Keel's short name
    where the founder saved the draft untouched, the founder's own where they renamed it. Held on the wire (the served
    reveal / idea and the item's question) and on the screens (the reveal's or idea screen's card, and the idea card
    above the Relative advantage item)."""
    name = j.idea_name
    card = vs.idea_card(name)
    served = [("reveal", interview.get("reveal")), ("idea", interview.get("idea"))]
    items = {i.get("dimension"): i for p in interview.get("parts") or [] for i in p.get("items") or []}
    advantage = items.get(RA_KEY)
    if not any(lines for _, lines in served) and advantage is None:
        return                                       # a gate No: nothing about the idea was served
    with _step(j, f"{person.person}: the idea card and the Relative advantage question name the idea "
                  f"{name!r}, its current name (keel-cloud 090)", party="participant") as h:
        faults = []
        occasion = interview.get("occasion") or ""
        want_question = vs.benefit_question(occasion, name)
        for kind, lines in served:
            if lines and lines.get("what") != card:
                faults.append({kind: lines.get("what"), "want": card})
        served_q = (advantage or {}).get("question") or ""
        if advantage is not None and (served_q != want_question if j.strict else name not in served_q):
            # on the back-test the stem and the question are the model's (keel-cloud 120 opens the question with the
            # occasion stem); only the idea's current name is held there
            faults.append({"question": served_q, "want": want_question if j.strict else f"names {name!r}"})
        if j.strict and occasion != vs.occasion(j.entry):
            faults.append({"occasion": occasion, "corpus": vs.occasion(j.entry)})
        for drawn in walked["screens"]:
            if drawn.get("screen") in ("reveal", "idea") and card not in (drawn.get("card") or ""):
                faults.append({"screen": drawn.get("screen"), "card": drawn.get("card"), "want": card})
            if drawn.get("screen") == "item" and drawn.get("dimension") == RA_KEY and drawn.get("idea_card") != card:
                faults.append({"screen": "item", "idea card": drawn.get("idea_card"), "want": card})
        h.record_assert({"card": card, "question": want_question, "faults": []},
                        {"served": dict(served), "question": (advantage or {}).get("question"), "faults": faults})
        assert not faults, json.dumps(faults, indent=2)


def _on_the_offered_options(body: dict, items: dict) -> dict:
    """A live journey's answer on the options the model's lists made: an option id the item does not
    offer (a benefit the model's list has no place for) becomes the item's first options, as many as the
    person picked. Never reached on a scripted journey."""
    by_id = {i.get("itemId"): i for i in items.values()}
    answers = []
    for answer in body.get("answers") or []:
        item = by_id.get(answer.get("itemId")) or {}
        offered = [o.get("optionId") for o in item.get("options") or []]
        picked = answer.get("optionIds")
        if picked and not all(p in offered for p in picked):
            answer = {**answer, "optionIds": offered[:len(picked)]}
        advantages = [a.get("id") for a in item.get("advantages") or []]
        ticked = answer.get("advantageIds")
        if ticked and not all(a in advantages for a in ticked):
            answer = {**answer, "advantageIds": advantages[:len(ticked)]}
        answers.append(answer)
    return {**body, "answers": answers}


def _normal_body(body: dict) -> dict:
    """A response body with its order taken out -- answers by item, ids as sets -- and keel-web's
    one deprecated constant (`pilotOptIn: false`) dropped, so two bodies compare on what they say."""
    # spec 051: the follow-up is held on its own (`_hold_the_follow_up`), against the harness's walk
    out = {k: v for k, v in body.items() if k not in ("answers", "pilotOptIn", "followUp")}
    answers = {}
    for answer in body.get("answers") or []:
        a = dict(answer)
        for key in ("optionIds", "advantageIds"):
            if key in a:
                a[key] = sorted(a[key])
        if "costTotal" in a and a["costTotal"].get("value") is not None:
            a["costTotal"] = {**a["costTotal"], "value": round(float(a["costTotal"]["value"]), 4)}
        answers[a.pop("itemId")] = a
    out["answers"] = answers
    return out


def _read(j: Journey, person) -> None:
    """The person's answer is read when this person wrote a story the reader is shown; nobody else's answer queues a
    reading (a gate no, a chip, the decision-maker's link).

    **Since keel-cloud 095 (DRIFT #84 resolved for Keel's door)** a Keel's-door project reads every answer on arrival:
    the journey presses nothing, waits for the newest batch -- the arrival's, which it did not start -- and any after
    it to be DONE, and a `POST readings` of its own is refused 409 (`READING_IN_PROGRESS` while it runs,
    `NOTHING_TO_READ` once all is read). **On the founder's own AI with the agent connected before the answers**
    nothing reads on arrival (095 judgement call 14: the own door reads at its next connect or on the founder's own
    `POST readings`), so the founder's session asks for the reading on the wire -- the call People's button made --
    exactly as before (spec 044 call 151)."""
    readable = any(p.person == person.person for p in vs.readable_people(j.entry))
    if not readable:
        return
    door = (j.get("/v2/me") or {}).get("aiPath")
    if door == "KEEL":
        _read_on_arrival(j, person)
        return
    with _step(j, f"{person.person}'s answer: on their own AI with the agent connected nothing reads on arrival "
                  "(keel-cloud 095 call 14), so the founder's session asks for the reading on the wire",
               party="founder", kind="note") as h:
        deadline = time.monotonic() + 45 * j.patience
        while True:
            status, started = j.call("POST", j.project("/readings"), {}, ok=(201, 409))
            if status == 201:
                break
            if time.monotonic() > deadline:
                raise AssertionError(f"{person.person}'s answer never reached a reading: {started}")
            time.sleep(1)
        h.record_wire({"POST": "readings"}, started)
        batch = _batches_done(j, person)
    with _step(j, f"{person.person}'s answer is read, and nothing failed") as h:
        h.record_assert({"status": "DONE", "failed": []}, batch)
        assert batch.get("status") == "DONE", batch
        assert not batch.get("failed"), batch


def _batches_done(j: Journey, person, *, before: set | None = None) -> dict:
    """The newest reading batch, once it -- and any started after it -- is no longer running."""
    deadline = time.monotonic() + 90 * j.patience
    while True:
        batches = j.get(j.project("/readings")) or []
        batch = batches[0] if isinstance(batches, list) and batches else {}
        fresh = batch.get("batchId") not in (before or set())
        if fresh and batch.get("status") not in (None, "RUNNING", "PENDING"):
            return batch
        if time.monotonic() > deadline:
            raise AssertionError(f"{person.person}'s reading never finished: {batch}")
        time.sleep(1)


def _read_on_arrival(j: Journey, person) -> None:
    """keel-cloud 095 FR-A, on Keel's door: the answer is read on its own; the founder presses nothing."""
    with _step(j, f"{person.person}'s answer is read on arrival (keel-cloud 095): the founder presses nothing, the "
                  "newest batch -- one the journey did not start -- and any after it end DONE, and a POST readings "
                  "of the founder's is refused 409 READING_IN_PROGRESS or NOTHING_TO_READ", party="stack") as h:
        batch = _batches_done(j, person)
        status, refused = j.call("POST", j.project("/readings"), {}, ok=(409,))
        h.record_assert({"status": "DONE", "failed": [], "POST readings": [409, "READING_IN_PROGRESS",
                                                                           "NOTHING_TO_READ"]},
                        {"batch": batch, "POST readings": [status, _refusal(refused)]})
        if getattr(j, "retries", 0) and (batch.get("status") != "DONE" or batch.get("failed")):
            # spec 062: on the back-test a reading Keel's AI could not land is a finding, recorded, not the end
            j.findings.append({"what": f"{person.person}'s reading", "batch": batch})
        else:
            assert batch.get("status") == "DONE" and not batch.get("failed"), batch
        assert _refusal(refused) in ("READING_IN_PROGRESS", "NOTHING_TO_READ"), refused


def _refusal(body) -> str | None:
    """A reading's refusal names itself in `rule` (keel-cloud `ReadingRefusal`), a vector refusal in `code`."""
    body = body if isinstance(body, dict) else {}
    return body.get("code") or body.get("rule")


# ----------------------------------------------------------------------------- leg 7: standings

def expected_status(entry, key: str) -> str:
    """The entry's own status for `key`, but `LEFT_OUT` where this journey had to leave Frequency
    out (spec 039 / 041 / 042 D-1: the corpus's Frequency is on an "out of N" its own window cannot carry -- since
    revision 11 on Mulch Run alone)."""
    if key == "problem.frequency" and not vs.frequency_fits(entry):
        return "LEFT_OUT"
    return str(((entry.expected.get("standings") or {}).get(key) or {}).get("status") or "").upper()


def _option_counts(raw: str) -> dict[str, int]:
    out = {}
    for part in str(raw).split(","):
        code, _, count = part.strip().partition("=")
        if code:
            out[code.strip()] = int(count)
    return out


def leg_standings(j: Journey) -> None:
    """`GET standings` against the entry, dimension by dimension -- status, drift, n and every count
    the entry records, each `optionCounts` code on the wire's own code -- and every vector's verdict and
    deciding dimension; then the board and the three stage pages, one row's per-person list among them."""
    # the last answer settles a moment after its 2xx (keel-cloud 096: the brief on return): wait until the wire
    # counts every invited person as answered before anything is read, so the eyebrow's count is the final one
    for _ in range(30):
        people = (j.get(j.project("/standings")) or {}).get("people") or {}
        if not people.get("invited") or people.get("answered") == people.get("invited"):
            break
        time.sleep(2)
    j.standings = j.get(j.project("/standings")) or {}
    dims = {d.get("dimension"): d for v in j.standings.get("vectors") or []
            for d in v.get("dimensions") or []}
    expected = j.entry.expected.get("standings") or {}
    if not j.strict:
        with _step(j, "every vector stands, with a status from keel-cloud's own words on every "
                      "dimension (a live journey: nothing is held to the corpus)") as h:
            statuses = {k: d.get("status") for k, d in dims.items()}
            verdicts = {v.get("vector"): v.get("verdict") for v in j.standings.get("vectors") or []}
            h.record_assert({"vectors": list(VECTORS), "statuses": sorted(STATUS_WORD)},
                            {"verdicts": verdicts, "statuses": statuses})
            assert set(verdicts) == set(VECTORS), verdicts
            assert all(s in STATUS_WORD for s in list(statuses.values()) + list(verdicts.values())), (
                statuses, verdicts)
        _board(j)
        for vector in VECTORS:
            _vector_page(j, vector)
        return
    with _step(j, "every dimension stands where the entry says it does: status, drift and counts") as h:
        mismatches = []
        for key, want in expected.items():
            got = dims.get(key) or {}
            row: dict = {"dimension": key}
            status = expected_status(j.entry, key)
            if (got.get("status") or "") != status:
                row["status"] = {"wire": got.get("status"), "corpus": status}
            overridden = status != str(want.get("status") or "").upper()
            want_drift = "NONE" if overridden else str(want.get("drift") or "none").upper()
            if (got.get("drift") or "NONE") != want_drift:
                row["drift"] = {"wire": got.get("drift"), "corpus": want_drift}
            if not overridden and status != "LEFT_OUT":
                if "n" in want and int(got.get("n") or 0) != int(want["n"]):
                    row["n"] = {"wire": got.get("n"), "corpus": want["n"]}
                interval = got.get("interval") or {}
                for count in INTERVAL_KEYS:
                    if count in want and interval and int(interval.get(count) or 0) != int(want[count]):
                        row[count] = {"wire": interval.get(count), "corpus": want[count]}
                if "optionCounts" in want:
                    wire_counts = {o.get("code"): int(o.get("count") or 0)
                                   for o in (got.get("choice") or {}).get("optionCounts") or []}
                    for code, count in _option_counts(want["optionCounts"]).items():
                        wire_code = vs.on_the_wire(j.entry, key, code)
                        if wire_counts.get(wire_code, 0) != count:
                            row.setdefault("optionCounts", {})[code] = {
                                "wire": wire_counts.get(wire_code), "wire code": wire_code, "corpus": count}
            if len(row) > 1:
                mismatches.append(row)
        h.record_assert([], mismatches)
        _defer(j, "standings", mismatches)

    with _step(j, "every vector's verdict is the worst of its dimensions, the deciding one's, as the "
                  "entry says (D3: all thirteen decide)") as h:
        verdicts = {v.get("vector"): v for v in j.standings.get("vectors") or []}
        mismatches = []
        for vector, want in (j.entry.expected.get("vector_verdicts") or {}).items():
            got = verdicts.get(vector) or {}
            deciding = (dims.get(want.get("deciding")) or {}).get("status")
            if got.get("verdict") != want.get("verdict") or deciding != want.get("verdict"):
                mismatches.append({"vector": vector, "wire": got.get("verdict"),
                                   "deciding on the wire": deciding, "corpus": want})
        h.record_assert([], mismatches)
        _defer(j, "verdicts", mismatches)

    _board(j)
    for vector in VECTORS:
        _vector_page(j, vector)


def _defer(j: Journey, what: str, mismatches: list) -> None:
    """A golden number the build moved (spec 064): recorded on its step (the served beside the corpus's) and kept for
    the end of the journey (`Journey.deferred`), so the legs after it still run and name theirs."""
    if mismatches:
        j.deferred.append({"what": what, "mismatches": mismatches})


def _board(j: Journey) -> None:
    """The report's Overview (keel-web 077 FR-2), as the founder opens it after every answer was read: every part of it
    the wire's `StandingsView` drawn (`report_marks.overview_faults` -- the verdict and its line, the ship, the two
    tiles, per stage the pill, the lead lines and every row in the registry's order, the foot, the download live and
    nothing of the old deck). `report_overview` scores the same read again in `leg_report`."""
    board = j.screens["board"] = j.answers.board(j.project_id)
    overview_read(j, "board", board)
    # the page read the standings a moment ago; on the host door a late job (THEMES, a last reading) can settle between
    # the leg's earlier read and the page's, so the expectation is drawn from the standings as they are now
    j.standings = j.get(j.project("/standings")) or j.standings
    with _step(j, "the overview: the verdict, the two tiles and every stage's rows are the wire's cards, drawn "
                  "(keel-web 077)", party="founder") as h:
        want = report_marks.expected_overview(j.standings)
        faults = report_marks.overview_faults(j.standings, board)
        h.record_assert({"faults": [], "overview": want},
                        {"faults": faults, "hero": board["hero"], "tiles": board["tiles"],
                         "panels": {v: {k: p.get(k) for k in ("head", "lead")} for v, p in board["panels"].items()}})
        assert not faults, json.dumps(faults, indent=2, default=str)
    watch_line_failed(j)


#: keel-web 077's too-few words the founder reads before the fifth answer (spec 052 FR-7; the Insights view's by
#: keel-web 079's rule).
TOO_FEW_WORDS = ("Keep interviewing", "Nothing to read into yet", "Not asked yet", "nobody has answered this yet")


def _too_few_answered(j: Journey, n: int) -> None:
    """Spec 052 FR-7, the half that holds only after someone answered: with fewer than five on every card the Insights
    view is *Nothing to read into yet* with the served count (keel-web 079 `insightsStateOf`: Keep interviewing, nobody
    answered or a card too few to call, no box), the Overview *Keep interviewing* with *{n} people have answered.* --
    every word the wire's drawing."""
    j.standings = j.get(j.project("/standings")) or {}
    board = j.screens["board-four"] = j.answers.board(j.project_id)
    overview_read(j, "board-four", board)
    insights = j.screens["insights-four"] = j.answers.insights(j.project_id)
    with _step(j, f"the report after {n} answers: Keep interviewing, and the Insights view Nothing to read into yet "
                  "(spec 052 FR-7)", party="founder") as h:
        faults = report_marks.overview_faults(j.standings, board) + report_marks.insight_faults(
            j.standings, insights, strict=j.strict, names=report_marks.names_of(j.standings))
        h.record_assert({"faults": [], "verdict": TOO_FEW_WORDS[0], "insights": TOO_FEW_WORDS[1]},
                        {"faults": faults, "verdict": board["hero"]["verdict"], "insights": insights.get("empty"),
                         "thin": report_marks.thin(j.standings)})
        assert not faults, json.dumps(faults, indent=2, default=str)
        assert board["hero"]["verdict"] == TOO_FEW_WORDS[0], board["hero"]
        # spec 064 FR-8a (keel-cloud 119 / keel-web 095): a typed follow-up draws its card even with too few answers
        # to call, so the empty state is required only when nobody has typed a word yet
        if insights.get("boxes"):
            assert all(b.get("concern") or b.get("head") for b in insights["boxes"]), insights["boxes"]
        else:
            assert TOO_FEW_WORDS[1] in (insights.get("empty") or ""), insights.get("empty")


def _too_few(j: Journey, when: str) -> None:
    """Spec 052 FR-7 (widening 044's *None yet* read): before the fifth answer the report is the too-few state --
    *Keep interviewing*, the price tile *Not asked yet*, *nobody has answered this yet* on every commercial row not left
    out (a left-out one reads its served line, keel-web 077 call 8), and the
    Insights view's empty state -- every word the wire's drawing (`overview_faults`, `insight_faults`). Before anyone
    answered the verdict is Keep interviewing and `pilot.finished` 0, so keel-web 079 draws *Nothing to read into yet*
    with *0 people have answered* there (design §4.2's rule; DRIFT #93 closed, call 4 back to it by the amendment of
    2026-10-17 (b)), as after the fourth answer (`_too_few_answered`; call 5)."""
    board = j.screens["board-too-few"] = j.answers.board(j.project_id)
    overview_read(j, "board-too-few", board)
    insights = j.screens["insights-too-few"] = j.answers.insights(j.project_id)
    with _step(j, f"the report {when}: Keep interviewing, Not asked yet on the price tile, nobody has answered this "
                  "yet on every commercial row, and the Insights view's empty state (spec 052 FR-7)",
               party="founder") as h:
        faults = report_marks.overview_faults(j.standings, board) + report_marks.insight_faults(
            j.standings, insights, strict=j.strict, names=report_marks.names_of(j.standings))
        rows = [r.get("text") for r in board["panels"]["COMMERCIAL"]["rows"]]
        h.record_assert({"faults": [], "words": list(TOO_FEW_WORDS)},
                        {"faults": faults, "verdict": board["hero"]["verdict"], "price": board["tiles"]["price"],
                         "commercial rows": rows, "insights": insights.get("empty")})
        assert not faults, json.dumps(faults, indent=2, default=str)
        assert board["hero"]["verdict"] == TOO_FEW_WORDS[0], board["hero"]
        assert insights.get("empty"), "no empty state before anyone answered"
        assert TOO_FEW_WORDS[1] in insights["empty"], insights["empty"]
        assert TOO_FEW_WORDS[2] in board["tiles"]["price"]["text"], board["tiles"]["price"]
        # keel-web 077 call 8: a left-out card reads its served line, not *nobody has answered this yet*
        asked = [r.get("text") for r in board["panels"]["COMMERCIAL"]["rows"] if r.get("status") != "LEFT_OUT"]
        assert asked and all(TOO_FEW_WORDS[3] in (r or "") for r in asked), rows


def _vector_page(j: Journey, vector: str) -> None:
    """One stage page: a row per dimension, each status the wire's in keel-web's word (amber where
    left out), the vector's headline the wire's own, on a B2B commercial page the banner naming the
    decision-maker -- and the deciding row opened, its per-person list the wire's people, each read as the
    wire reads them (design §7.1: the people list shows `readAs`)."""
    standing = next(v for v in j.standings.get("vectors") or [] if v.get("vector") == vector)
    rows = standing.get("dimensions") or []
    deciding = (standing.get("deciding") or {}).get("dimension") if isinstance(standing.get("deciding"), dict) \
        else standing.get("deciding")
    if deciding not in {d.get("dimension") for d in rows}:
        deciding = vs.stage_cite(j.entry, vector) if j.strict else None
    opened = next((d for d in rows if d.get("dimension") == deciding and d.get("people")), None) or \
        next((d for d in rows if d.get("people")), None)
    rungs = [d.get("dimension") for d in rows if any(p.get("followUp") for p in d.get("people") or [])]
    page = j.screens[vector] = j.answers.vector_page(j.project_id, vector,
                                                     open_row=(opened or {}).get("dimension"),
                                                     follow_up_rows=rungs)
    with _step(j, f"the {vector.lower()} page: every dimension reads the wire's status in keel-web's "
                  "word, and one row's people are the wire's, each as it was read",
               party="founder") as h:
        mismatches = []
        for d in rows:
            key = d.get("dimension")
            row = page["rows"].get(key) or {}
            word = STATUS_WORD[d.get("status")]
            if not row.get("status", "").startswith(word):
                mismatches.append({"dimension": key, "screen": row.get("status"), "want": word})
            if d.get("status") == "LEFT_OUT" and not row.get("amber"):
                mismatches.append({"dimension": key, "screen": "not amber", "want": "amber"})
        people = [{"name": p.get("personName"), "readAs": p.get("readAs")} for p in (opened or {}).get("people") or []]
        h.record_assert({"headline": standing.get("headline"), "mismatches": [], "people": people},
                        {"headline": page["headline"], "mismatches": mismatches,
                         "rows": page["rows"], "people": page["people"], "opened": page["open_row"]})
        assert page["headline"] == standing.get("headline"), (page["headline"], standing.get("headline"))
        assert len(page["rows"]) == len(rows), page["rows"]
        assert not mismatches, json.dumps(mismatches, indent=2)
        assert page["people"] == people, (page["people"], people)
        assert page["keel_bars"] == 0, "a stage page draws Keel's bar (keel-web 067: page two alone)"
        if opened is not None:
            assert people, opened
        if vector == "COMMERCIAL" and vs.is_b2b(j.entry):
            # spec 064 FR-6 (keel-cloud 123 FR-10): the banner says the decider's title, the role where none was sent
            words = {str(j.founder.decider.get(k) or "").lower() for k in ("title", "role")} - {""}
            assert any(w in page["decider_banner"].lower() for w in words), (page["decider_banner"], words)
    stage_band(j, vector)
    if rungs:
        with _step(j, f"the {vector.lower()} page: every person who answered the follow-up shows it under their name, "
                      "One last thing · {rung}: \"...\" (design §5.4, spec 052 FR-8)", party="founder") as h:
            want = {d.get("dimension"): [{"name": p.get("personName"), "line": follow_up_line(d.get("name"),
                                                                                              p.get("followUp"))}
                                         for p in d.get("people") or [] if p.get("followUp")]
                    for d in rows if d.get("dimension") in rungs}
            have = {k: [x for x in v if x.get("line")] for k, v in (page.get("follow_ups") or {}).items()}
            h.record_assert(want, have)
            for key, lines in want.items():
                drawn = {x["name"]: report_marks.ov.norm(x["line"]) for x in have.get(key) or []}
                for line in lines:
                    assert drawn.get(line["name"]) == report_marks.ov.norm(line["line"]), (key, line, drawn)
                assert len(drawn) == len(lines), (key, drawn, lines)


def follow_up_line(rung: str, text: str) -> str:
    """keel-web's per-person follow-up line on a stage page (design §5.4): *One last thing · {rung}: "{text}"*."""
    return f"{report_marks.ONE_LAST_THING} · {rung}: \u201c{text}\u201d"


# -------------------------------------------------------------------------------- leg 8: the report

def expected_cards(j: Journey) -> list[dict]:
    """The entry's cards (keel-cloud 089 FR-001) as `instructions/brief_facts.py` reads them -- the reading
    spec 040's DRY compare proved equal to keel-cloud's own `BriefFactsCorpusTest` -- with the one
    dimension this journey had to leave out read as left out (D-1)."""
    standings = (j.entry.expected or {}).get("standings") or {}
    cards = []
    for dimension in j.registry.calibrated(j.entry.b2b()):
        standing = standings.get(dimension.key) or {}
        if expected_status(j.entry, dimension.key) == "LEFT_OUT":
            standing = {"status": "LEFT_OUT"}
        # spec 064 FR-4a (keel-cloud 116): Prevalence's line is the founder's clause the journey scripted, in the window
        cards.append(brief_facts_mod.card(j.entry, dimension, standing, clause=vs.event_past(j.entry)))
    return cards


def _card(card: dict) -> dict:
    return {k: card.get(k) for k in brief_facts_mod.CARD_FIELDS} | {
        "statusWords": str(card.get("statusWords") or "").split(" · ", 1)[0]}


def leg_report(j: Journey, *, timeout_s: float = 60) -> None:
    """The report over the same standings, **on the wire** (`GET standings`, keel-cloud 104, contract 19): on the
    scripted journeys every dimension's card is the entry's own (number, line, status), each stage's `broke` the
    entry's deciding dimension where the stage broke, each stage's `notAsked`, the pilot the entry's sign-ups over
    everyone who answered, and the price median the entry's own (`brief_facts.price_median_for`) -- at
    `StandingsView.priceMedian` and `facts.commercial.priceMedian` alike. Then keel-web 077's three views and the
    binding are read and the five report marks scored over them (`_score_report`). On a live journey nothing is held
    to the corpus and the Insights view is held for shape only (FR-9)."""
    standings = j.standings = j.get(j.project("/standings")) or {}
    facts = standings.get("facts") or {}
    with _step(j, "the standings carry the report's parts (contract 19): facts, pilot, priceMedian (present, maybe "
                  "null), pilotPeople, insights -- and no brief") as h:
        keys = sorted(standings)
        h.record_assert({"has": ["facts", "insights", "pilot", "pilotPeople", "priceMedian"], "no": ["brief"]}, keys)
        assert {"facts", "insights", "pilot", "pilotPeople", "priceMedian"} <= set(standings), keys
        assert "brief" not in standings, keys
    if j.strict and j.registry is not None:
        with _step(j, "the report's cards are the entry's own, one a dimension: number, line, status") as h:
            want_cards = [_card(c) for c in expected_cards(j)]
            have_cards = [_card(c) for c in facts.get("cards") or []]
            h.record_assert(want_cards, facts.get("cards"))
            _defer(j, "cards", [{"wire": w, "corpus": c} for w, c in zip(have_cards, want_cards) if w != c]
                   + ([{"wire": len(have_cards), "corpus": len(want_cards)}] if len(have_cards) != len(want_cards)
                      else []))
        with _step(j, "each stage broke where the entry's verdict is a called failure, on its deciding "
                      "dimension") as h:
            want_broke = {v: vs.broke_key(j.entry, v) for v in VECTORS}
            have_broke = {v: ((facts.get(v.lower()) or {}).get("broke") or {}).get("key") for v in VECTORS}
            h.record_assert(want_broke, have_broke)
            _defer(j, "broke", [] if have_broke == want_broke else [{"wire": have_broke, "corpus": want_broke}])
        with _step(j, "each stage's notAsked is the entry's, in keel-cloud 091's one house style (FR-F3)") as h:
            want_not = {v: expected_not_asked(j, v) for v in VECTORS}
            have_not = {v: [{k: n.get(k) for k in ("key", "name", "why")}
                            for n in (facts.get(v.lower()) or {}).get("notAsked") or []] for v in VECTORS}
            h.record_assert(want_not, have_not)
            assert have_not == want_not, json.dumps({"wire": have_not, "corpus": want_not}, indent=2)
        with _step(j, "the pilot: the entry's sign-ups over everyone who answered, per link -- in the facts and on "
                      "the standings") as h:
            want_pilot = brief_facts_mod.pilot_for(j.entry)
            h.record_assert(want_pilot, {"facts": facts.get("pilot"), "standings": standings.get("pilot")})
            _defer(j, "pilot", [] if facts.get("pilot") == want_pilot == standings.get("pilot") else [
                {"facts": facts.get("pilot"), "standings": standings.get("pilot"), "corpus": want_pilot}])
        with _step(j, "what they would pay: the entry's price median -- the highest edge half or more chose at or "
                      "above (keel-cloud 104 FR-1) -- at StandingsView.priceMedian and facts.commercial alike") as h:
            want = brief_facts_mod.price_median_for(j.entry)
            served = standings.get("priceMedian")
            have = {k: served.get(k) for k in brief_facts_mod.PRICE_MEDIAN_FIELDS} if isinstance(served, dict) \
                else served
            h.record_assert(want, {"standings": served, "facts": (facts.get("commercial") or {}).get("priceMedian")})
            assert have == want, (served, want)
            assert served == (facts.get("commercial") or {}).get("priceMedian"), (served, facts.get("commercial"))
    _score_report(j)


#: Spec 053 FR-3d (design D19: no founder page shows a pound): what may never appear on a page a corpus journey reads,
#: now that every corpus entry is a US entry in dollars (corpus revision 12). Moved here from S-007, whose own sweep
#: it was (the only US market until revision 12).
OTHER_CURRENCIES = ("£", "€", "GBP", "EUR")

#: The views `report_record` reads, which every corpus journey draws -- the sweep must have read each.
REPORT_VIEWS = ("board", "insights", "pilot", "printed")


def currency_leaks(screens: dict) -> dict:
    """`{page: [the other currencies its drawn text carries]}` over every page in `screens` that drew any."""
    pages = {name: (drawn.get("text") if isinstance(drawn, dict) else None) or ""
             for name, drawn in screens.items()}
    leaks = {name: [c for c in OTHER_CURRENCIES if c in text] for name, text in pages.items()}
    return {name: found for name, found in leaks.items() if found}


def leg_one_currency(j: Journey) -> None:
    """Spec 053 FR-3d (judgement call 3): an assertion in every corpus journey, not a mark. After the report, none of
    `OTHER_CURRENCIES` in any text `j.screens` drew -- the founder screens, the stage pages, the three views and the
    binding -- and the project's market is the entry's (`market` as the corpus records it: US, en-US, its region).
    A pound on a page after keel-web 078 is DRIFT #95 (spec 053 FR-6), never a tolerance here."""
    want = {"country": (j.entry.market or {}).get("country"), "region": (j.entry.market or {}).get("region"),
            "language": (j.entry.market or {}).get("language")}
    with _step(j, f"{j.entry.id}: the project's market is the entry's own -- {want['country']}, "
                  f"{want['language']}, region {want['region'] or 'none'}") as h:
        market = (j.get(j.project("/overview")) or {}).get("market") or {}
        have = {"country": market.get("country"), "region": market.get("region") or None,
                "language": market.get("language")}
        h.record_assert(want, have)
        assert have == want, (have, want)
    with _step(j, "no pound or euro reaches any page the founder reads, the report's three views and its binding "
                  "included (design D19)", party="founder") as h:
        leaks = currency_leaks(j.screens)
        read = sorted(name for name, drawn in j.screens.items()
                      if isinstance(drawn, dict) and (drawn.get("text") or "").strip())
        h.record_assert({"leaks": {}, "read": list(REPORT_VIEWS)}, {"leaks": leaks, "read": read})
        missing = [name for name in REPORT_VIEWS if name not in read]
        assert not missing, f"the sweep read no text on {missing}, so it swept nothing there"
        assert not leaks, leaks


def _invitations(j: Journey) -> dict:
    """`{invitationId: {name, email, source}}` off the register (the names the quotes and the pilot rows carry)."""
    rows = (j.get(j.project("/invitations")) or {}).get("invitations") or []
    return {(r.get("invitationId") or r.get("id")): {"name": r.get("personName"), "email": r.get("email"),
                                                      "source": r.get("source")}
            for r in rows if r.get("invitationId") or r.get("id")}


def report_record(j: Journey) -> dict:
    """The record `evals/report_marks.py` scores: the wire, the three views and the binding as drawn, the stage pages'
    text, the register's names, and the people the walks opted in (the corpus people who tick the box)."""
    invitations = _invitations(j)
    by_name = {v["name"]: k for k, v in invitations.items()}
    record = {
        "standings": j.standings, "strict": j.strict, "project": (j.standings or {}).get("name"),
        "date": report_marks.day_words((j.standings or {}).get("asOf")),
        "invitations": invitations,
        "opted_in": [by_name[p.person] for p in j.people if getattr(p, "pilot_opt_in", False) and p.person in by_name]
        if j.strict else None,
        "stage_pages": {v: (j.screens.get(v) or {}).get("text") or "" for v in VECTORS},
    }
    if record["opted_in"] is None:
        del record["opted_in"]
    record["overview"] = j.screens.get("board") or j.answers.board(j.project_id)
    record["insights"] = j.screens["insights"] = j.answers.insights(j.project_id)
    record["pilot"] = j.screens["pilot"] = j.answers.pilot(j.project_id)
    record["binding"] = j.screens["printed"] = j.answers.brief(j.project_id, printed=True)
    return record


def _score_report(j: Journey) -> dict:
    """The five report marks over the journey's record, written into the bundle (`report.json`,
    `report-marks.json`); the journey fails on any owed mark unmet."""
    from pathlib import Path                                  # noqa: PLC0415
    record = report_record(j)
    card = j.report_card = report_marks.scorecard(record)
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "report.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "report-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    require = report_marks.owed(record)
    with _step(j, f"report marks v{report_marks.REPORT_MARKS_VERSION} (spec 052): {card['met']} of {card['measured']} "
                  f"met ({', '.join(require) or 'none'} owed; {', '.join(card['unmeasured']) or 'none'} unmeasured)",
               party="stack") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
    return card


def expected_not_asked(j: Journey, vector: str) -> list[dict]:
    """`BriefFacts.<stage>.notAsked` as `instructions/brief_facts.py` reads the entry (keel-cloud 089 FR-002, 091
    FR-F3's house style), with the dimension this journey had to leave out read as left out (D-1)."""
    out = []
    b2b = j.entry.b2b()
    for d in j.registry.slice(vector):
        if d.b2b_only and not b2b:
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.NOT_ASKED_WHY[d.key]})
        elif expected_status(j.entry, d.key) == "LEFT_OUT":
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.LEFT_OUT_LINE})
        elif d.b2b_link_only and not b2b:
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.NOT_ASKED_WHY[d.key]})
    return out


# ------------------------------------------------------------------------------------- the whole

# --------------------------------------------------------------------------- the feedback marks

def feedback_record(j: Journey) -> dict:
    """Spec 046: the record `evals/feedback_marks.py` scores -- the lists Keel drafted (FM1) with the role words keel-cloud
    exported (`common.role_words`) and the founder's own words, Importance's drafts and saved list (FM2), and what the
    legs kept for FM3-FM6 (the base query, the idea, the AI flow, the typed fields)."""
    record = {k: v for k, v in j.feedback.items() if k not in ("lists", "importance_probe", "importance_typed")}
    lists = list(j.feedback.get("lists") or [])
    if lists:
        common = getattr(j.registry, "common", None) or {}
        record["lists"] = lists
        record["role_words"] = list(common.get("role_words") or [])
        record["founder_text"] = {
            "context": dict(j.founder.context_fields),
            "problem_seed": j.founder.problem_seed, "solution_seed": j.founder.solution_seed,
            "persona_roles": [j.founder.context_fields.get("actor")] + (
                [j.founder.decider["role"]] if j.founder.decider.get("role") else [])}
    key = "problem.importance"
    drafts = {x["draft"]: x for x in lists if x.get("dimension") == key}
    answer = next((a for v in VECTORS for a in j.founder.calibration[v] if a.dimension == key), None)
    if "first" in drafts and answer is not None and not answer.unsure:
        stored = (j.get(j.project("/plan")) or {}).get("lists") or {}
        named = [part.strip() for part in (answer.text or "").split(";") if part.strip()]
        record["importance"] = {
            "own": vs.founder_list(j.entry, key)["items"][0]["label"],
            "named": named,
            "first_draft": [i["label"] for i in drafts["first"]["items"]],
            "redraft": [i["label"] for i in (drafts.get("answer") or {}).get("items") or []],
            "saved": [i.get("label") for i in (stored.get(key) or {}).get("items") or []],
            "typed": list(j.feedback.get("importance_typed") or []),
            "probe": j.feedback.get("importance_probe")}
    return record


def score_feedback(j: Journey) -> dict:
    """The feedback marks over the journey's record, written into the bundle (`feedback.json`, `feedback-marks.json`);
    the journey fails on any owed mark unmet -- owed being every mark whose subject the record carries."""
    from pathlib import Path                                  # noqa: PLC0415
    record = feedback_record(j)
    card = feedback_marks.scorecard(record)
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "feedback.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "feedback-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    require = feedback_marks.owed(record)
    with _step(j, f"feedback marks v{feedback_marks.FEEDBACK_MARKS_VERSION} (spec 046): {card['met']} of "
                  f"{card['measured']} met ({', '.join(require) or 'none'} owed; "
                  f"{', '.join(card['unmeasured']) or 'none'} unmeasured)", party="stack") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
    return card


def guide_record(j: Journey) -> dict:
    """The guide marks' record (spec 054): what `leg_welcome` read, and every corridor frame the journey read after it
    (`Corridor.frame()["welcome"]`, the sheets over each -- G1's "never returns")."""
    record = {k: v for k, v in j.guide.items() if k != "snippets"}
    # spec 059: a journey that only passed keel-web 088's Interviews sheet by carries no G13 subject (only S-005 judges
    # it); the passes are kept beside the record, and every 059 mark it carries none of is unmeasured with the why
    passed = record.get("interviews")
    if passed is not None and not passed.get("judged"):
        record.pop("interviews")
        record["interviews_passed"] = passed.get("passed") or []
    keys = {m: key for m, key, _ in guide_marks.MARKS}
    absent = {m: guide_marks.SENT_ELSEWHERE_WHY for m in guide_marks.SENT_MARKS if keys[m] not in record}
    if absent:
        record["notes"] = {**absent, **(record.get("notes") or {})}
    frames = [(key, screen.get("frame") or {}) for key, seen in j.framing.items() for screen in seen
              if isinstance(screen, dict) and screen.get("frame")]
    if j.teach is not None:
        # G10: the pills on each question's first screen; G11: the openers over every corridor frame; G6: the report
        # sheet over every Overview read after the first open.
        firsts: dict = {}
        for key, frame in frames:
            firsts.setdefault(key, frame)
        record["explainers"] = {**j.guide["explainers"], "questions": {
            key: {"clip": guide_marks.EXPLAINERS[key], "present": j.teach.present(guide_marks.EXPLAINERS[key]),
                  "pills": frame.get("pills") or []}
            for key, frame in firsts.items() if key in guide_marks.EXPLAINERS}}
        record["openers"] = {**j.guide["openers"], "later": [frame.get("openers") or 0 for _, frame in frames]}
        record["report"] = {**j.guide["report"], "later": [r.get("report_sheet") or 0
                                                           for r in j.guide["overview"]["reads"]]}
    if "welcome" in record:
        record["welcome"] = dict(record["welcome"])
        record["welcome"]["later_frames"] = [(screen.get("frame") or {}).get("welcome")
                                             for seen in j.framing.values() for screen in seen
                                             if isinstance(screen, dict) and screen.get("frame")]
    return record


def _score_guide(j: Journey) -> dict:
    """The guide marks over the journey's record, written into the bundle (`guide.json`, `guide-marks.json`); the
    journey fails on any owed mark unmet -- owed being every mark whose subject the record carries (G4 / G5 only on
    S-005's local journey; elsewhere unmeasured, the record's `notes` saying why)."""
    from pathlib import Path                                  # noqa: PLC0415
    captions_read(j)
    record = guide_record(j)
    card = guide_marks.scorecard(record)
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "guide.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "guide-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    require = guide_marks.owed(record)
    with _step(j, f"guide marks v{guide_marks.GUIDE_MARKS_VERSION} (specs 054, 057, 059): {card['met']} of "
                  f"{card['measured']} "
                  f"met ({', '.join(require) or 'none'} owed; {', '.join(card['unmeasured']) or 'none'} unmeasured; "
                  f"{', '.join(card['not_applicable']) or 'none'} not applicable)",
               party="stack") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {"owed": {m: {"ok": c["ok"], "detail": c["detail"]}
                                                              for m, c in owed.items()},
                                                     "why unmeasured": card["why_unmeasured"]})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
    return card


def run(stack, founder_one, browser, run_dir, *, entry_id: str, slug: str,
        extra: Callable[[Journey], None] | None = None, entry_from: Callable | None = None,
        welcome_walk: bool = False, teaching: bool = False, backtest: Any = None) -> None:
    """The whole scenario. `entry_id` is the only argument that differs between S-005, S-006 and
    S-007. `extra` is the one seam: the thing only *its* entry can say, handed the `Journey`. `entry_from` is S-014's
    (spec 052 FR-7): the entry the journey walks, built from the canon one (`preludes.healthy_entry`) -- the canon's
    bytes are hashed and held unchanged as on every journey. `welcome_walk` is S-005's (spec 054 FR-3): on the local
    profile the welcome's twelve cues are walked through the seam and *Play the welcome again* pressed twice.
    `teaching` is S-005's too (spec 057): it measures G6-G12; every other journey passes keel-web 086's opener and
    report sheets by (`vs_screens.pass_teaching_sheet`, in the corridor and the report's page objects).

    `backtest` is spec 062's (`evals/backtest.Backtest`, `make backtest`): the entry is read from the back-test
    directory and walked with `strict=False` (S-012's mode) by a founder who signs up through keel-web's /signup, so
    every job runs on Keel's AI on the local stack -- no runtime, no script. Its camera takes the founder's and one
    person a link's screens, the export runs at the last answer with no verdict gate, the guide and feedback marks
    (S-005/6/7's regressions) are not scored, and `backtest.md` / `backtest.json` are written whatever happens."""
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    if backtest is None:
        cell_label = (f"{remote.cell_name()} · corpus {slug} · "
                      f"{time.strftime('%Y-%m-%d', time.gmtime())}")
        founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    try:
        corpus, entry = vs.entry_for(stack.keel_cloud, entry_id, backtest=backtest is not None)
    except (vs.VectorsScriptError, vs.corpus_reader.CorpusError) as refusal:
        import pytest                                       # noqa: PLC0415
        pytest.fail(f"{entry_id}: {refusal}", pytrace=False)
    if entry_from is not None:
        entry = entry_from(entry)
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    hashes_before = dict(corpus.hashes)
    script = vs.generate(entry) if backtest is None else None
    founder = vs.founder_inputs(entry)
    people = vs.person_inputs(entry)
    write_generated(run_dir, script=script.to_json() if script is not None else None,
                    inputs=vs.inputs_json(entry, founder, people))
    journey = None
    try:
        exported = contract_mod.export(stack.keel_cloud,
                                       run_dir / ("export" if backtest is None else backtest.contract_dir))
        keys_path = run_dir / "context-keys.json"
        keys_path.write_text(json.dumps(vs.context_keys_for(exported.context_keys), indent=2) + "\n",
                             encoding="utf-8")
        page = context.new_page()
        if getattr(stack, "is_remote", False):
            # Remote: the welcome's 11 MB mp4 delays the load event over the wire (a media element delays load until it
            # has current data); 30 s is not enough on a slow link, and nothing the founder sees waits on it.
            page.set_default_navigation_timeout(90_000)
        journey = open_journey(recorder, page, context, browser, stack, entry, founder, people,
                               script=script, registry=exported.registry, strict=backtest is None,
                               patience=1.0 if backtest is None else backtest.patience)
        journey.stack, journey.founder_identity = stack, founder_one
        if backtest is None:
            journey.hold_welcome = True
            user_code = _connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path)
            own_ai_door(page, recorder, stack, journey.get, through_the_code_story=bool(user_code))
            lap = _no_lap
        else:
            # spec 062 FR-2: signed up through /signup as the back-test founder (outside `fake-for`): Keel's AI
            journey.founder_identity = backtest.sign_in(journey)
            journey.keels_door = True
            journey.camera = backtest.camera(journey)
            journey.corridor.camera = journey.camera.founder
            lap = backtest.lap

        leg_project(journey)
        lap("leg_project")
        if backtest is None:
            leg_welcome(journey, walk=welcome_walk)
        else:
            backtest.pass_welcome(journey)
        if teaching:
            teaching_start(journey)
        else:
            # spec 057: G6-G12 are S-005's (the founder journey); here the corridor and the report pass the sheets by
            journey.guide.setdefault("notes", {}).update({m: guide_marks.TEACHING_ELSEWHERE_WHY
                                                          for m in guide_marks.TEACHING_MARKS})
        lap("teaching")
        leg_context(journey)
        lap("leg_context")
        opener(journey, "PROBLEM")
        leg_interpret_problem(journey)
        lap("leg_interpret_problem")
        leg_calibrate(journey, "PROBLEM")
        lap("leg_calibrate PROBLEM")
        opener(journey, "SOLUTION")
        leg_interpret_solution(journey)
        lap("leg_interpret_solution")
        leg_calibrate(journey, "SOLUTION")
        lap("leg_calibrate SOLUTION")
        opener(journey, "COMMERCIAL")
        leg_persona(journey)
        lap("leg_persona")
        leg_calibrate(journey, "COMMERCIAL")
        lap("leg_calibrate COMMERCIAL")
        openers_final(journey)
        leg_lock(journey)
        lap("leg_lock")
        leg_invite(journey)
        lap("leg_invite")
        leg_interview(journey)
        lap("leg_interview")
        leg_standings(journey)
        lap("leg_standings")
        leg_report(journey)
        leg_one_currency(journey)
        lap("leg_report and leg_one_currency")
        if extra is not None:
            extra(journey)
        if journey.deferred:
            with recorder.step(f"spec 064: {len(journey.deferred)} golden reading(s) the build moved -- each named on its "
                               "step, the served beside the corpus's", party="stack", kind="assert") as h:
                h.record_assert([], journey.deferred)
                raise AssertionError(json.dumps(journey.deferred, indent=2, default=str)[:20000])
        if backtest is None:
            score_feedback(journey)
            _score_guide(journey)
        else:
            # spec 062 FR-3: the export at the last answer, names kept, no verdict gate (060 FR-3 is golden-only)
            backtest.after(journey)
            lap("export")

        with recorder.step("the corpus hashes exactly as it did when the run began",
                           party="stack", kind="assert") as h:
            try:
                corpus.verify_unchanged()
            except Exception as moved:  # noqa: BLE001
                # spec 062 follow-up (2026-10-22): on the back-test an entry edited under a run (an author at work
                # while the money is spent) is a finding, not the end -- the walk and its transcript are untouched
                if backtest is None:
                    raise
                journey.findings.append({"what": "a back-test entry changed under the run", "refused": str(moved)[:400]})
            h.record_assert(hashes_before, dict(corpus.hashes))
        passed = True
    finally:
        if backtest is not None:
            # spec 062 FR-4: the transcript, from the recorder's captures and the wire, before the session closes
            backtest.finish(journey, passed=passed, failed_step=recorder.failed_step)
        context.close()
        finalize_run(run_dir, slug=slug, facts=corpus_facts.vectors_facts_for(entry),
                     passed=passed, failed_step=recorder.failed_step,
                     duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")


def _no_lap(_name: str) -> None:
    """`run()`'s lap on every journey but the back-test's, which records each leg's wall time (spec 062 FR-4.5)."""


def _connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path) -> str | None:
    """The runtime on this entry's script, then the founder signed in through the door the runtime's
    code opens (unchanged from the classic journeys: the runtime starts BEFORE the founder signs
    in, because keel-cloud decides the account's AI from the door it was created through)."""
    auth = Auth(page, recorder, web_base)
    if stack_runtime.status(stack).get("running"):
        stop_runtime(stack, recorder)
    if stack.is_remote:
        with recorder.step("the runtime home is put back the way `make up` leaves it",
                           party="stack", kind="protocol") as h:
            stack_runtime.reset(stack)
            h.record_wire({"home": str(stack_runtime.home_dir(stack))},
                          {"after": stack_runtime.status(stack)})
    result = start_runtime_via_skill(stack, recorder, env_extra={
        "KEEL_SCRIPT": str(run_dir / "script.json"),
        "KEEL_CONTEXT_KEYS": str(keys_path)})
    user_code = result.get("user_code")
    if result.get("outcome") == "authorization_started" and user_code:
        auth.sign_in_with_code(founder_one, user_code)
        connect = Connect(page, recorder)
        connect.open(result["verification_uri"])
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()
    else:
        # **No code, so no code story.** The runtime reconnected on a credential the home already
        # held, which is what a local profile does; `ai_path` is immutable, so this sign-in cannot
        # move it either way, and the ordinary door is what a returning founder uses.
        with recorder.step("no device code: the runtime reconnected on the credential its "
                           "home already held, so this founder signs in as a returning one",
                           party="stack", kind="note") as h:
            h.record_wire({"outcome": result.get("outcome")},
                          {"user_code": user_code,
                           "why it does not decide a door": (
                               "keel-cloud reads the door only on the branch that CREATES "
                               "the account (keel-cloud spec 044 FR-014); a returning "
                               "founder keeps whatever their row already says")})
        auth.sign_in(founder_one)
    Landing(page, recorder, web_base).visit()
    return user_code
