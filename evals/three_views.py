"""Spec 157 / 158: **the three views, end to end** -- the problem, the solution and the money chain walked once on
the stack, nothing bought. Spec 158 moves the founder's legs onto **the conversation** (keel-web 245 on keel-cloud 263,
contract 83): four beats, one long answer each, the limitations broken out by Keel, nothing to press, nothing cut.

One run (`make e2e-157`, `evals/e2e_157_three_views.py`) is a chain of legs over one founder:

* **FR-1, the founder's legs** (spec 158 FR-1, FR-2, FR-5). (a) two problem projects by voice: one told in the cloud
  script's own words (every reading scripted, the cost heard), one told the long way (beat 3 over 1,500 characters,
  five limitations and a cost in one breath, kept whole; *only the ones in Europe* after beat 4's readback; the cost
  drafted from the limitations) -- each through the opening (the stage's opener or the begin screen), the beats with
  the orb's states and no button but the orb, the boxes and the story closed by the quiet, 244's window page (stored),
  then Prevalence; (b) a solution from nothing: the which-problem page, *A new problem*, its conversation, back with it
  picked, the problem replayed and closed by the quiet, the two idea beats (the name and a colour said; one answer into
  ticks and crosses), the idea's boxes, the build, the day with the idea (the name and the colour, clearly), then
  Compatibility with Relative advantage pre-filled; (c) a money study from nothing: the pages, the problem's and the
  solution's conversations, *Use {name}*, the one orb moment, today's persona step pre-filled, the lock once and the
  link -- then a money study with only a name, walked to the persona step; (d) the problem project of (b), opened from
  the list (*Defined, not sent*), resumed, calibrated, refused at the lock on a drained grant, then locked once (the
  ledger's one PROJECT charge) and a link sent.
* **FR-2, the stranger's legs** (`evals/three_views_strangers.py`, unchanged by 158 but for the beats' slots the story
  cards are spoken from): the text, avatar and copilot views of each locked project's link.

**Nothing paid.** The founder is a fresh stub identity on her own AI (the code story's door); every job is the scripted
runtime's on a script built for the story (`story_screens.story_runtime_script`: the 01-countly study of the scope with
the story's context, Prevalence and screener); every story reading, build, clip and transcript is keel-cloud's fakes.
Keel's door is stood in only around the lock (`stack/ledger.py`'s stand-ins under `e2e-eval:157:`), so the lock's own
PROJECT row is the product's; the questions the lock starts are then written on the founder's own door (`POST
questionnaire/retry`). The remote profile refuses every stand-in by name: those checks are skipped there and say so.

Every check is a `Leg.check` row (the report's lines); a failed check names the screen and the view.
"""

from __future__ import annotations

import dataclasses
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from evals import corpus_scenario as cs
from evals import scope_journey as sj
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv_screens
from harness import story_screens as ss
from harness import vectors_script as vs
from harness.browser import Landing, MarketStep, ScopeChoose
from harness.connect import start_runtime_via_skill, stop_runtime
from instructions import contract as contract_mod
from stack import ledger
from stack import remote as stack_remote
from stack import runtime as stack_runtime

SPEC = "157"
#: The stand-ins' key prefix (`e2e-eval:157:`) and their reason's spec.
STAND_IN_SPEC = SPEC
#: The corpus entry whose scoped studies are the runtime's base scripts (S-015 / S-016's seed).
BASE_ENTRY = sj.SCOPED_FROM
#: keel-cloud 258: what the lock buys (`PROJECT`, 2,000).
PROJECT_PRICE = 2000
#: The balance a drained grant is lowered to (under the price: the lock refuses, as today).
DRAINED_TO = 100
#: keel-cloud 251: the refusal's code at the lock.
INSUFFICIENT = "INSUFFICIENT_CREDITS_FOR_NEW_PROJECT"

#: The legs, in the report's order: FR-1 (a)-(d), then FR-2's nine.
FOUNDER_LEGS = (("FR-1a", "the problem by voice, twice (the script's words; the long telling and a correction), to the "
                          "window page and Prevalence"),
                ("FR-1b", "the solution from nothing: the which-problem page, the replay, the two idea beats, the day "
                          "with the idea, Compatibility with Relative advantage pre-filled"),
                ("FR-1c", "the money from nothing: the pages, the orb moment, the persona pre-filled, one lock charge, "
                          "the link; then a money study with only a name, to the persona step"),
                ("FR-1d", "the defined problem project from the list: resumed, calibrated, refused on a drained grant, "
                          "locked once, a link sent"))
VIEWS = ("text", "avatar", "copilot")
STUDIES = (("problem", "the problem link (gate No ends)"), ("solution", "the solution link (anchor No ends)"),
           ("money", "the decision-maker's link (third-person check No ends)"))
STRANGER_LEGS = tuple((f"FR-2 {study} · {view}", f"{words}: the {view} view") for study, words in STUDIES
                      for view in VIEWS)


class LegFailed(AssertionError):
    """A check that did not hold: the leg stops here, the screen and the view named."""


@dataclasses.dataclass
class Check:
    name: str
    ok: bool
    screen: str = ""
    view: str = ""
    detail: Any = None


@dataclasses.dataclass
class Leg:
    id: str
    title: str
    status: str = "not run"        # green | failed | written, not run | skipped | not run
    why: str = ""
    checks: list = dataclasses.field(default_factory=list)
    notes: list = dataclasses.field(default_factory=list)
    seconds: float = 0.0

    def check(self, run: "Run", name: str, ok: bool, *, screen: str, view: str = "founder", detail: Any = None,
              stop: bool = True) -> bool:
        """One named assertion: kept on the leg and in the transcript; a miss stops the leg (or, `stop=False`, is kept
        and the leg goes on -- the leg still fails)."""
        row = Check(name=name, ok=bool(ok), screen=screen, view=view, detail=detail)
        self.checks.append(row)
        with run.recorder.step(f"{self.id}: {name}", party="founder" if view == "founder" else "participant",
                               kind="assert") as h:
            h.record_assert({"holds": True, "screen": screen, "view": view}, {"holds": bool(ok), "detail": detail})
        if not ok and stop:
            raise LegFailed(f"{self.id} -- {name} (screen: {screen}; view: {view}): "
                            f"{json.dumps(detail, default=str)[:1500]}")
        return bool(ok)

    @property
    def failed_checks(self) -> list:
        return [c for c in self.checks if not c.ok]


# ------------------------------------------------------------------------------------------------ the run

class Run:
    """What every leg shares: the stack, the founder's browser context (the speech seam installed), the recorder, the
    cloud's fixtures, the runtime's current script, and the projects the legs made."""

    def __init__(self, stack, browser, recorder, run_dir: Path):
        self.stack = stack
        self.browser = browser
        self.recorder = recorder
        self.run_dir = Path(run_dir)
        self.web = stack.web_base_url
        self.cloud = stack.cloud_base_url
        self.remote = bool(getattr(stack, "is_remote", False))
        self.legs: dict[str, Leg] = {}
        for leg_id, title in FOUNDER_LEGS + STRANGER_LEGS:
            self.legs[leg_id] = Leg(leg_id, title)
        self.projects: dict[str, str] = {}
        self.names: dict[str, str] = {}
        self.journeys: dict[str, cs.Journey] = {}
        self.runtime_scope: str | None = None
        self.stamp = time.strftime("%H%M%S", time.gmtime())
        self.readings = ss.fake_readings(stack.keel_cloud)
        self.prevalence = ss.example_prevalence(stack.keel_cloud)
        self.founder = None
        self.context = None
        self.page = None
        self.ledger_since: str | None = None
        self.account_id: str | None = None
        self.findings: list = []
        #: Spec 158 FR-6: every conversation told, beat by beat (the report's *The beats*).
        self.beats: list[dict] = []
        #: Spec 158b: every drawn story measured -- where, on what, and `story_screens.measure_story`'s read (the
        #: report's *The drawn story*).
        self.fits: list[dict] = []

    # ------------------------------------------------------------------------------------- the wire
    def call(self, method: str, path: str, body: dict | None = None) -> tuple[int, Any]:
        kwargs: dict = {"timeout": 30_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = self.context.request.fetch(f"{self.cloud}{path}", method=method, **kwargs)
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001 - an empty body
            payload = response.text()
        return response.status, payload

    def get(self, path: str) -> Any:
        status, body = self.call("GET", path)
        return body if status < 400 else None

    def list_row(self, project_id: str) -> dict:
        for row in (self.get("/v2/me/projects") or {}).get("mine") or []:
            if row.get("projectId") == project_id:
                return row
        return {}

    # ------------------------------------------------------------------------------------- the scripts
    def base_entry(self, scope: str):
        corpus, entry = vs.entry_for(self.stack.keel_cloud, BASE_ENTRY)
        self._corpus = corpus
        if scope == "PROBLEM":
            return sj.problem_entry(entry)
        if scope == "COMMERCIAL":
            return sj.money_entry(entry)
        return solution_entry(entry)

    def script_for(self, scope: str, *, consumed: int = 0) -> dict:
        base = vs.generate(self.base_entry(scope)).to_json()
        script = ss.story_runtime_script(base, self.readings, self.prevalence, STORY_WINDOW)
        if consumed:
            # the chain's answer already applied on the project (at the story's or the idea's yes): a runtime started
            # again begins its cursor past it, so the founder's redrafts meet their own answers
            for screen in ("CALIBRATION_QUESTIONS", "CALIBRATION_QUESTIONS+repair"):
                entries = script.get(screen) or []
                if len(entries) > consumed:
                    script[screen] = entries[consumed:]
        return script

    def load_runtime(self, scope: str, *, consumed: int = 0) -> None:
        """The scripted runtime on `scope`'s script: written into the bundle, the runtime asked to go, and started again
        on it (it reconnects on the credential its home holds -- no code, no new door). `consumed`: the chain's answers
        the project already took (the scripted executor's cursor starts at 0 on every start)."""
        key = f"{scope}:{consumed}"
        if self.runtime_scope in (scope, key) and not consumed:
            return
        if self.runtime_scope == key:
            return
        script = self.script_for(scope, consumed=consumed)
        (self.run_dir / "script.json").write_text(json.dumps(script, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        (self.run_dir / f"script-{scope.lower()}.json").write_text(json.dumps(script, indent=1, ensure_ascii=False)
                                                                   + "\n", encoding="utf-8")
        if self.runtime_scope is not None:
            stop_runtime(self.stack, self.recorder)
            start_runtime_via_skill(self.stack, self.recorder, env_extra={
                "KEEL_SCRIPT": str(self.run_dir / "script.json"), "KEEL_CONTEXT_KEYS": str(self.keys_path)})
        self.runtime_scope = key if consumed else scope

    # ------------------------------------------------------------------------------------- set up
    def open(self) -> None:
        """A fresh founder (a stub identity of this run), her own AI through the code story, the runtime on the
        problem's script; the founder's context carries the speech seam."""
        exported = contract_mod.export(self.stack.keel_cloud, self.run_dir / "export")
        self.registry = exported.registry
        self.keys_path = self.run_dir / "context-keys.json"
        self.keys_path.write_text(json.dumps(vs.context_keys_for(exported.context_keys), indent=2) + "\n",
                                  encoding="utf-8")
        label = f"{stack_remote.cell_name()} · e2e-157 · {time.strftime('%Y-%m-%d', time.gmtime())}"
        self.founder = stack_remote.register_cell_identity(self.stack, label,
                                                           name=f"Founder {self.stamp}")
        self.context = self.browser.new_context()
        self.context.add_init_script(ivs.SPEECH_SEAM)
        self.context.add_init_script(ss.ORB_WATCH)          # spec 158 FR-2: the orb's states, logged
        self.page = self.context.new_page()
        if self.remote:
            self.page.set_default_navigation_timeout(90_000)
        script = self.script_for("PROBLEM")
        (self.run_dir / "script.json").write_text(json.dumps(script, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        # a fresh founder signs in through the code story's door alone: the runtime home is emptied first, so the
        # runtime asks for a code (a home holding a credential reconnects without one, and the sign-in would be the
        # plain door's -- Keel's AI)
        if stack_runtime.status(self.stack).get("running"):
            stop_runtime(self.stack, self.recorder)
        stack_runtime.reset(self.stack)
        cs._connect(self.stack, self.recorder, self.page, self.founder, self.web, self.run_dir, self.keys_path)
        self.runtime_scope = "PROBLEM"
        me = self.get("/v2/me") or {}
        with self.recorder.step("spec 157: the founder is on her own AI (the code story's door)", party="founder",
                                kind="assert") as h:
            h.record_assert({"aiPath": "OWN"}, {k: me.get(k) for k in ("aiPath", "email", "creditsAvailable")})
            assert me.get("aiPath") == "OWN", me
        if not self.remote:
            self.account_id = ledger.founder_account(self.stack, self.founder.sub)["id"]
            self.ledger_since = ledger.now(self.stack)

    def close(self) -> None:
        try:
            if self.account_id and not self.remote:
                acct = ledger.founder_account(self.stack, self.founder.sub)
                if acct.get("ai_path") != "OWN":
                    ledger.restore_own_door(self.stack, self.account_id, f"close-{self.stamp}", spec=STAND_IN_SPEC)
        finally:
            if self.context is not None:
                self.context.close()

    # ------------------------------------------------------------------------------------- shared moves
    def new_project(self, name: str, scope: str) -> None:
        """The landing's New project: the name, *What do you want to validate?* answered `scope`, the market step."""
        land = Landing(self.page, self.recorder, self.web)
        land.visit()
        if land.new_project_enabled() and self.page.locator(".guided-step").count() == 0:
            land.start_new_project()
        land.name_project(name, scope=scope)

    def journey(self, key: str, scope: str, project_id: str) -> cs.Journey:
        """A corpus journey over a story-defined project (the 01-countly study of `scope` as its inputs, never strict):
        the existing legs calibrate, lock and send on it."""
        entry = self.base_entry(scope)
        founder = vs.founder_inputs(entry)
        people = vs.person_inputs(entry)
        j = cs.open_journey(self.recorder, self.page, self.context, self.browser, self.stack, entry, founder, people,
                            registry=self.registry, strict=False)
        j.scope = scope
        j.project_id = project_id
        j.stack, j.founder_identity = self.stack, self.founder
        self.journeys[key] = j
        return j


#: The recall window the story's projects keep: the default the confirm stores (keel-cloud 259 FR-3; DRIFT #103).
STORY_WINDOW = {"count": 7, "unit": "NIGHTS"}


def _safe(read) -> str:
    try:
        return " ".join(str(read() or "").split())
    except Exception:  # noqa: BLE001 - a read
        return ""


def solution_entry(entry):
    """01-countly as a solution study (`scope: SOLUTION`): `expected` the entry's own solution standings and verdict."""
    expected = entry.expected or {}
    return dataclasses.replace(entry, scope="SOLUTION", expected={
        "standings": {k: v for k, v in (expected.get("standings") or {}).items() if k.startswith("solution.")},
        "vector_verdicts": {k: v for k, v in (expected.get("vector_verdicts") or {}).items() if k == "SOLUTION"}})


def timed(run: Run, leg_id: str, body: Callable[[Leg], None]) -> Leg:
    """Runs one leg: green when it returns with every check held, failed (the first miss's screen and view) else."""
    leg = run.legs[leg_id]
    started = time.monotonic()
    try:
        body(leg)
        leg.status = "failed" if leg.failed_checks else (leg.status if leg.status in ("written, not run",
                                                                                    "skipped") else "green")
        if leg.failed_checks and not leg.why:
            first = leg.failed_checks[0]
            leg.why = f"{first.name} (screen: {first.screen}; view: {first.view})"
    except LegFailed as missed:
        leg.status = "failed"
        leg.why = leg.why or str(missed).split(": {")[0][:600]
    except Exception as broke:  # noqa: BLE001 - the leg's own stop, named
        leg.status = "failed"
        leg.why = leg.why or f"{type(broke).__name__}: {str(broke)[:600]} (url: {run.page.url if run.page else '-'})"
    finally:
        leg.seconds = round(time.monotonic() - started, 1)
    return leg


# ------------------------------------------------------------------------------------------------ the conversation

def _norm_words(text: str | None) -> str:
    return " ".join(str(text or "").split()).strip()


def _bare(text: str | None) -> str:
    """Words compared without case, spacing or end punctuation."""
    return re.sub(r"[.!?,;:\s]+$", "", _norm_words(text).lower())


def _named(rows: list[str], said: str | None) -> list[str]:
    """The rows `said` does not name (compared without case or end punctuation)."""
    words = _bare(said)
    return [r for r in rows if _bare(r) not in words]


def turn_screen(run: Run, leg: Leg, label: str, snap: dict, screen: str, *, card: bool = False) -> None:
    """Spec 158c FR-7 (keel-web 249 FR-1): the small orb on the screen (one, at most 44 px), its state line beside it, no
    glow; where `card`, the card is clean (no drawing in it: no rough board)."""
    leg.check(run, f"{label}: {screen} -- the small orb (one, at most 44 px) with its state line, no glow"
                   + (", the card with no drawing in it" if card else ""),
              snap.get("orbs") == 1 and (snap.get("orbSize") or 99) <= 44 and bool(snap.get("line"))
              and not snap.get("glow") and (not card or ((snap.get("card") or {}).get("svg") == 0)),
              screen=screen, detail={k: snap.get(k) for k in ("orbs", "orbSize", "glow", "line", "sub", "orb")}
              | {"card svg": (snap.get("card") or {}).get("svg")}, stop=False)


def hand_over_checks(run: Run, leg: Leg, label: str, read: dict, screen: str, *, beat_path: str) -> None:
    """Spec 158c FR-7 (keel-web 249 FR-3): `window.__keelChime` rises by exactly one per hand-over, the state line says
    *Your turn.* in the very frame the orb first listens (*Your turn. I am listening.* on a beat), and the orb listens
    only where the microphone is open."""
    v = read["chime"]
    beats = [x for x in v["lines"] if re.search(beat_path, str(x.get("path") or ""))]
    leg.check(run, f"{label}: the hand-over -- the chime counted once per hand-over ({v['hand_overs']} hand-overs, "
                   f"{v['chimes']} chimes), *Your turn.* in the frame the orb first listens (*{ss.TURN_LISTENING}* on "
                   "every beat), the orb listening only with the microphone open",
              v["hand_overs"] > 0 and v["one_each"] and v["your_turn"] and v["mic_open"]
              and all(x.get("line") == ss.TURN_LISTENING for x in beats) and bool(beats),
              screen=f"{screen} (story-orb data-state, story-state, window.__keelChime)", detail=v, stop=False)


def one_film(run: Run, leg: Leg, label: str, project_id: str, sheets: list[dict], stage: str, woke: dict) -> None:
    """Spec 158c FR-8 (keel-web 249 FR-6): on a new project's conversation one sheet at most stands at once, the stage
    opener is the one film (no welcome sheet on the conversation's routes), and after its close the cloud has both seen:
    `guide.openersSeen` holds the stage and `guide.welcomeSeen` is true."""
    v = ss.sheet_verdict(sheets)
    guide = (run.get(f"/v2/projects/{project_id}/overview") or {}).get("guide") or {}
    leg.check(run, f"{label}: one film -- the stage opener alone on the conversation (one sheet at a time, no welcome "
                   f"sheet), and after it both seen (openersSeen has {stage}, welcomeSeen true)",
              v["one_film"] and stage in (guide.get("openersSeen") or []) and guide.get("welcomeSeen") is True,
              screen="the conversation's opening (guide-opener, guide-welcome)", view="founder + wire",
              detail={"sheets": v, "guide": {k: guide.get(k) for k in ("welcomeSeen", "openersSeen")},
                      "woke": woke.get("sheets") if isinstance(woke, dict) else woke}, stop=False)


def tell_the_story(run: Run, leg: Leg, project_id: str, label: str, *, long3: bool = False,
                   correction: str | None = None, back_to: str | None = None, goto: bool = True) -> dict:
    """keel-web 245 on one problem project, nothing pressed: the opening (the stage's opener passed, or the begin
    screen's orb; *Ready?*; the quiet), the beats said once each (beat 3 the long telling where `long3`; `correction`
    after beat 4's readback), the boxes by the quiet, the build, the story by the quiet. The checks: the questions
    verbatim, no button but the orb on any screen, the orb's states through each beat, beat 3's red crosses named by the
    readback and closed by the quiet, beat 5 asked only where owed, the boxes (no cost label; the cost box where a
    cost is known), the build `ready`, the cost on the story's seventh line, and where the quiet lands."""
    walk = ss.StoryWalk(run.page, run.recorder, run.web)
    opening = walk.open_start(project_id, goto=goto)
    woke = opening["woke"]
    leg.check(run, f"{label}: the opening -- the stage's opener passed by its Skip or the begin screen's orb tapped "
                   "(*Tap me to begin.*), then *Ready?* and the quiet open beat 1; no button but the orb",
              opening["landed"].rstrip("/").endswith("/define/story/1") and (woke["begin"] or "opener" in woke["sheets"])
              and (opening["start"].get("question") == ss.STORY_READY) and not opening["start"].get("buttons")
              and not ((woke.get("begin_screen") or {}).get("buttons")),
              screen="define/story/start", detail=opening)
    told = list(ss.said_turns(run.readings))
    words3, rows = (ss.long_beat_3(run.readings) if long3 else (dict(told)[3], ss.limits_read(run.readings)))
    if long3:
        told[0] = (1, told[0][1] + ss.LONG_WHO_SUFFIX)
    seen = walk.tell(told, long3=words3 if long3 else None, correction=correction)
    said = {n: (words3 if n == 3 else w) for n, w in told}
    beats = {s["turn"]: s for s in seen}
    run.beats.append({"label": label, "project": project_id, "beats": seen})
    # the questions, the buttons, the wire
    asked = {n: (b["asked"].get("question")) for n, b in beats.items()}
    leg.check(run, f"{label}: Keel asks each beat's question as keel-cloud 263 FR-1 words it",
              all(asked[n] == ss.STORY_QUESTIONS[n] for n in asked), screen="define/story/1..5",
              detail=asked)
    pressed = {n: sorted(set((b["asked"].get("buttons") or []) + (b["readback"].get("buttons") or [])
                             + ((b.get("corrected") or {}).get("buttons") or []))) for n, b in beats.items()}
    leg.check(run, f"{label}: no button on any beat but the orb (no Tap to talk, Type instead, Send, That is all, Yes)",
              not any(pressed.values()), screen="define/story/1..5", detail=pressed)
    small = {n: {k: b["asked"].get(k) for k in ("orbs", "orbSize", "glow", "line")} for n, b in beats.items()}
    leg.check(run, f"{label}: the small orb on every beat (one, at most 44 px), its state line beside it, no glow "
                   "(keel-web 249 FR-1)",
              all(v["orbs"] == 1 and (v["orbSize"] or 99) <= 44 and v["line"] and not v["glow"] for v in small.values()),
              screen="define/story/1..5 (story-orb, story-state)", detail=small, stop=False)
    answers = [w for w in walk.writes if re.search(r"/story/turns/\d$", w["path"]) and (w["sent"] or {}).get("text")
               and not (w["sent"] or {}).get("correction")]
    leg.check(run, f"{label}: every beat sent once as said (the words whole), every answer 200",
              [((w["sent"] or {}).get("text")) for w in answers] == [said[n] for n in sorted(beats)]
              and all((w["status"] or 0) < 400 for w in walk.writes if "/story/turns/" in w["path"]),
              screen="define/story/1..5", detail=[(w["path"].split("/story/")[-1], w["status"],
                                                   len(((w["sent"] or {}).get("text")) or ""), (w["sent"] or {}).get("done"),
                                                   (w["sent"] or {}).get("correction")) for w in walk.writes
                                                  if "/story/turns/" in w["path"]])
    transcribed = [((w.get("body") or {}).get("text")) for w in walk.writes if w["path"].endswith("/story/transcribe")]
    leg.check(run, f"{label}: every answer written down through story/transcribe, heard as said (the fake: the words "
                   "in, the same words out)", all(said[n] in transcribed for n in beats)
              and (not correction or correction in transcribed
                   or any(b.get("correction_deferred") for b in beats.values())), screen="define/story/1..5",
              detail={"heard": [t[:120] if t else t for t in transcribed]})
    orbs = {n: b.get("orb") for n, b in beats.items()}
    leg.check(run, f"{label}: the orb through every beat -- speaking (the question), listening, hearing, writing, "
                   "speaking (Keel's next line: no per-beat readback since keel-web 245 FR-4 as amended), and from "
                   "writing straight to speaking (keel-web 249: `listening` only where the microphone opened)",
              all(ss.holds_in_order(o or [], ss.BEAT_ORB) and ss.writing_then_speaking(o or []) for o in orbs.values()),
              screen="define/story/1..5 (story-orb data-state)", detail=orbs, stop=False)
    # beat 3: every limitation, broken out, named back, closed by the quiet
    b3 = beats.get(3) or {}
    read3 = ((b3.get("put") or {}).get("body") or {})
    limits = list((read3.get("story") or {}).get("limits") or [])
    crosses = list((b3.get("readback") or {}).get("limits") or [])
    leg.check(run, f"{label}: beat 3's one answer read into {len(rows)} red crosses (`story-card-limit`), the "
                   "readback naming each, the quiet closing the list (done: true, next 4)",
              limits == rows and crosses == rows and not _named(rows, read3.get("readback"))
              and (b3.get("closed") or {}).get("sent") == {"done": True} and (b3.get("closed") or {}).get("next") == 4,
              screen="define/story/3", detail={"limits": limits, "crosses": crosses, "want": rows,
                                               "readback": read3.get("readback"), "closed": b3.get("closed")})
    folded = (b3.get("readback") or {}).get("folded") or ""
    words_said = len(said[3].split())
    rb3 = b3.get("readback") or {}
    leg.check(run, f"{label}: the transcript folds to one line when the crosses arrive (*You spoke for m:ss · n words*); "
                   "*What I hear* gives way to it (keel-web 249 FR-4: no `story-heard` words left, `story-words` Keel's)",
              folded.startswith("You spoke for ") and f"· {words_said} word" in folded
              and not [w for w in rb3.get("heard") or [] if w.get("who") == "you"]
              and all(w.get("who") == "keel" for w in rb3.get("words") or []),
              screen="define/story/3 (story-folded)", detail={"folded": folded, "words said": words_said,
                                                              "heard": rb3.get("heard"), "words": rb3.get("words")},
              stop=False)
    understood = rb3.get("understood") or {}
    marks3 = ss.card_items(understood, "limits")
    leg.check(run, f"{label}: beat 3's crosses are a card of what Keel understood (`story-understood`: *What Keel "
                   "understood*, the row `limits`, every line a cross) -- never plain text on the turn screen "
                   "(keel-web 249 FR-4, FR-5)",
              understood.get("label") == ss.CARD_LABEL and [r.get("box") for r in understood.get("rows") or []]
              == ["limits"] and len(marks3) == len(rows) and all(m.get("mark") == "cross" for m in marks3)
              and [_bare(m.get("text")) for m in marks3] == [_bare(r) for r in rows],
              screen="define/story/3 (story-understood)", detail={"card": understood, "want": rows}, stop=False)
    if long3:
        sent3 = next((w for w in answers if w["path"].endswith("/story/turns/3")), {})
        text3 = (sent3.get("sent") or {}).get("text") or ""
        leg.check(run, f"{label}: beat 3's long answer -- {len(said[3])} characters, five limitations and a cost in one "
                       f"breath -- sent whole and taken (200, no 240 cut, keel-cloud 263 FR-2a)",
                  len(said[3]) >= ss.LONG_ANSWER_MIN and text3 == said[3] and (sent3.get("status") or 500) < 400
                  and bool((read3.get("readback") or "").startswith("I kept the four")),
                  screen="define/story/3", detail={"sent": len(text3), "status": sent3.get("status"),
                                                   "readback": read3.get("readback")})
        if run.remote:
            leg.notes.append(f"{label}: remote profile -- beat 3's stored words are not read (the twin's database)")
        else:
            kept = ledger.story_turns(run.stack, project_id)
            leg.check(run, f"{label}: the story keeps beat 3's words whole (project_story's turn 3: every character, "
                           "nothing cut)", _norm_words(kept.get(3)) == _norm_words(said[3]),
                      screen="the stored story (no route serves the words)", view="wire",
                      detail={"stored": len(kept.get(3) or ""), "said": len(said[3]),
                              "ends": (kept.get(3) or "")[-80:]})
    # beat 4 (and its correction)
    b4 = beats.get(4) or {}
    read4 = ((b4.get("put") or {}).get("body") or {})
    sentence = ((read4.get("story") or {}).get("person") or {}).get("sentence")
    leg.check(run, f"{label}: beat 4's readback is the sentence, then *Right?*",
              bool(sentence) and read4.get("readback") == f"{sentence.strip()} Right?", screen="define/story/4",
              detail={"readback": read4.get("readback"), "sentence": sentence})
    if correction and b4.get("correction"):
        fixed = b4.get("correction") or {}
        body = fixed.get("body") or {}
        condition = ((body.get("story") or {}).get("person") or {}).get("onlyThoseWho") or ""
        stored = ((run.get(f"/v2/projects/{project_id}/story") or {}).get("person") or {}).get("onlyThoseWho") or ""
        leg.check(run, f"{label}: *{correction}* after beat 4's readback is sent as a correction and narrows the "
                       "condition; the new readback says so (keel-cloud 263 FR-5)",
                  (fixed.get("sent") or {}).get("correction") is True and (fixed.get("status") or 500) < 400
                  and ss.CORRECTION_4_WORD in condition and ss.CORRECTION_4_WORD in stored
                  and ss.CORRECTION_4_WORD in (body.get("readback") or ""),
                  screen="define/story/4 (after the readback)", detail={"sent": fixed.get("sent"),
                                                                       "readback": body.get("readback"),
                                                                       "condition": condition, "stored": stored})
    straight = sorted(n for n, b in beats.items() if b.get("straight_on"))
    leg.notes.append(f"{label}: " + (f"beats {straight} went straight on (keel-web 245 FR-4 as amended 2026-11-22: no "
                                     "per-beat readback)" if straight else
                                     "every beat read back and waited for the quiet (the build before polish round 2)"))
    owed = ss.moment_beat(run.readings) == 5
    leg.check(run, f"{label}: beat 5 (*When does that come up?*) asked {'because beat 2 named no moment' if owed else 'never: beat 2 named the moment'}",
              (5 in beats) == owed, screen="define/story/5", detail={"beats": sorted(beats), "owed": owed})
    # the boxes, by the quiet
    before = run.get(f"/v2/projects/{project_id}/story") or {}
    boxes = walk.boxes()
    board = boxes["screen"].get("board") or ""
    if correction and boxes.get("correction"):
        # keel-web 245 FR-4 / FR-6 as amended (2026-11-22): no readback after beat 4 -- the correction is said on the
        # boxes after *Is that right?* and sent as `story/correct`
        fixed = boxes["correction"]
        body = fixed.get("body") or {}
        stored = ((run.get(f"/v2/projects/{project_id}/story") or {}).get("person") or {}).get("onlyThoseWho") or ""
        leg.check(run, f"{label}: *{correction}* said on the boxes after *Is that right?* is sent as story/correct "
                       "(the words whole, 200)", (fixed.get("sent") or {}).get("text") == correction
                  and (fixed.get("status") or 500) < 400, screen="define/story/check (boxes, the correction)",
                  detail={"sent": fixed.get("sent"), "status": fixed.get("status"), "changed": body.get("changed"),
                          "readback": body.get("readback")})
        leg.check(run, f"{label}: the correction on the boxes narrows the condition and the readback says so",
                  ss.CORRECTION_4_WORD in stored and ss.CORRECTION_4_WORD in (body.get("readback") or ""),
                  screen="define/story/check (boxes, the correction)", view="wire",
                  detail={"stored": stored, "readback": body.get("readback"), "changed": body.get("changed"),
                          "why it may not": "keel-cloud's FakeStoryReadings answers a story/correct it has no "
                                            "`corrections` entry for with *Nothing changed.*",
                          "drift": "runs/DRIFT.md #110"}, stop=False)
    elif correction and not b4.get("correction"):
        leg.check(run, f"{label}: *{correction}* said somewhere -- after beat 4's readback or on the boxes", False,
                  screen="define/story/4 -> check", detail={"beat 4": {k: b4.get(k) for k in ("straight_on", "next")},
                                                            "boxes": boxes.get("correction")}, stop=False)
    cost_before = before.get("cost")
    card = boxes["screen"].get("card") or {}
    by_box = ss.card_rows(card)
    crosses_on_card = [_bare(m.get("text")) for m in ss.card_items(card, "limits") if m.get("mark") == "cross"]
    person = (before.get("person") or {}).get("who")
    leg.check(run, f"{label}: the boxes are the card (keel-web 249 FR-5) -- *What Keel understood*, read by `data-box`: "
                   "the person, the limitations as crosses, the cost as the last row (*So*, no cost label) where a cost "
                   "is known; *Is that right?*; no button; the quiet confirms (story/confirm 200, defined)",
              boxes["confirm"]["status"] == 200 and (boxes["confirm"]["body"] or {}).get("status") == "defined"
              and boxes["screen"].get("said") == ss.BOXES_ASK and not boxes["screen"].get("buttons")
              and card.get("label") == ss.CARD_LABEL and ss.COST_TAG not in board
              and set(by_box) <= set(ss.CARD_ROWS) and "person" in by_box
              and (not person or _bare(person) in _bare(by_box.get("person")))
              and crosses_on_card == [_bare(r) for r in rows]
              and (not cost_before or (list(by_box)[-1:] == ["cost"] and _bare(cost_before) in _bare(by_box["cost"])
                                       and ss.card_name(card, "cost") == ss.CARD_COST_NAME)),
              screen="define/story/check (boxes)",
              detail={"rows": by_box, "names": {r.get("box"): r.get("name") for r in card.get("rows") or []},
                      "said": boxes["screen"].get("said"), "cost": cost_before,
                      "costDrafted": before.get("costDrafted"), "lit": boxes.get("lit"),
                      "buttons": boxes["screen"].get("buttons"), "confirm": boxes["confirm"]["status"]})
    turn_screen(run, leg, label, boxes["screen"], "define/story/check (boxes)", card=True)
    leg.check(run, f"{label}: Keel narrates the card row by row -- the rows lit are the card's own (`data-lit`)",
              bool(boxes.get("lit")) and all(set(str(x).split(",")) <= set(ss.CARD_ROWS) for x in boxes.get("lit") or []),
              screen="define/story/check (boxes)", detail={"lit": boxes.get("lit")}, stop=False)
    built = walk.building_then_story()
    if built["state"] == "story":
        # spec 158b: the drawn story read while it plays on the founder's screen (desktop)
        measure_fit(run, leg, run.page, label, FOUNDER_PLAYER, where="define/story/check (story)",
                    view="founder · desktop", phone=False, state=FOUNDER_STATE)
    story = run.get(f"/v2/projects/{project_id}/story") or {}
    build = story.get("build") or {}
    drawn = build.get("story") or {}
    want_room = ss.scripted_room(run.readings) if _bare((story.get("person") or {}).get("who")) == \
        _bare(ss.scripted_who(run.readings)) else None
    leg.check(run, f"{label}: the build reaches ready, the check passed{', the scripted room' if want_room else ''}, "
                   "the story drawn; no button",
              built["state"] == "story" and build.get("state") == "ready" and (build.get("checked") or {}).get("pass")
              is True and (want_room is None or drawn.get("roomId") == want_room)
              and not (built.get("story") or {}).get("buttons") and not ((built.get("building") or {}).get("buttons")),
              screen="define/story/check (building, story)",
              detail={"screen": built.get("state"), "build": {k: build.get(k) for k in ("state", "checked")},
                      "room": drawn.get("roomId"), "scenes": len(drawn.get("scenes") or [])})
    # the story's lines: six scenes, then the cost line (the seventh), then the ask line (keel-cloud 259 FR-5's draft)
    scenes = drawn.get("scenes") or []
    seventh = drawn.get("costLine") or ((scenes[6] or {}).get("line") if len(scenes) > 6 else None)
    cost = story.get("cost")
    heard = bool(cost_before) and not before.get("costDrafted")
    leg.check(run, f"{label}: the story's seventh line carries the cost -- {'heard' if heard else 'drafted from the limitations'}"
                   f" (`costDrafted` {'false' if heard else 'true'} on the wire, never on the screen)",
              bool(cost) and bool(seventh) and _bare(cost) in _bare(seventh)
              and story.get("costDrafted") is (not heard) and "drafted" not in _bare(board),
              screen="define/story/check (story)", view="wire",
              detail={"cost": cost, "costDrafted": story.get("costDrafted"), "before": cost_before,
                      "seventh": seventh, "costLine": drawn.get("costLine")})
    lands = {"solution": r"/\?start=solution", "money": r"/\?start=money"}.get(back_to or "", r"/define/context")
    yes = walk.story_yes(lands=re.compile(lands))
    if back_to == "solution":
        leg.check(run, f"{label}: the quiet after the story goes back to the solution, Keel saying so",
                  yes.get("said") in (ss.BACK_TO_SOLUTION, ss.STORY_ASK), screen="define/story/check (story)",
                  detail=yes, stop=False)
    read = walk.turn_read()
    hand_over_checks(run, leg, label, read, "define/story/*", beat_path=r"/define/story/\d$")
    heard = ss.heard_verdict(read["heard"], said, lambda n: f"/define/story/{n}")
    leg.check(run, f"{label}: each beat's words shown as heard -- in *What I hear* (`story-heard`) on the beat's screen "
                   "-- and never among Keel's lines (`story-words` Keel's alone; keel-web 249 FR-4)",
              heard["all_shown"] and heard["words_keels_only"], screen="define/story/1..5 (story-heard, story-words)",
              detail=heard, stop=False)
    one_film(run, leg, label, project_id, read["sheets"], "PROBLEM", woke)
    walk.stop_listening()
    return {"walk": walk, "landed": yes["landed"], "story": story, "beats": beats}


def window_then_prevalence(run: Run, leg: Leg, project_id: str, label: str) -> dict:
    """After the story's quiet: 244's window screen -- a page, no orb on it (keel-web 245 FR-13, keel-cloud 263 FR-11:
    the window stays a page; no spoken window) -- a window chosen and stored (`PUT context/window`), then Prevalence
    (`define/problem/q/1`) with the story's own question. Where the window screen is not drawn (runs/DRIFT.md #103)
    both are failed checks by name and the walk goes on to Prevalence by its address."""
    page = run.page
    page.wait_for_timeout(1500)
    url = page.url
    window_page = "/define/context/window" in url and page.locator("[data-testid=context-window-page]").count() > 0 \
        and page.locator("[data-testid=context-window-page]").first.is_visible()
    leg.check(run, f"{label}: the story's quiet opens 244's window screen -- a page, no orb on it", window_page
              and page.locator(ss.ORB).count() == 0, screen="define/context/window",
              detail={"url": url, "window page": window_page, "orb": page.locator(ss.ORB).count()}, stop=False)
    shot = ss._BrowserStep(run.recorder, page, "founder")
    stored = None
    with run.recorder.step(f"{label}: the window chosen, then on to the problem's first question", party="founder") as h:
        if window_page:
            page.locator("button.cwindow__chip").first.click()
            with page.expect_response(lambda r: r.request.method == "PUT" and r.url.split("?")[0]
                                      .endswith("/context/window"), timeout=30_000) as got:
                page.get_by_role("button", name=re.compile(r"save and continue", re.I)).first.click()
            stored = {"status": got.value.status, "sent": got.value.request.post_data_json}
        else:
            page.get_by_role("button", name=re.compile(r"continue to the problem", re.I)).first.click()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not re.search(r"/define/problem/(q/1|seed)", page.url):
            page.wait_for_timeout(250)
        page.wait_for_timeout(1000)
        landed = page.url
        h.add_screenshot(shot.screenshot(f"after-the-window-{label}"))
    if window_page:
        leg.check(run, f"{label}: the window stored (PUT context/window 200)", (stored or {}).get("status") == 200,
                  screen="define/context/window", view="wire", detail=stored)
    leg.check(run, f"{label}: the window's forward press goes on to Prevalence (define/problem/q/1), never the seed "
                   "chat the story already answered", "/define/problem/q/1" in landed, screen="define/context -> "
              "define/problem/q/1", detail={"landed": landed, "drift": "runs/DRIFT.md #103"}, stop=False)
    if "/define/problem/q/1" not in landed:
        page.goto(f"{run.web}/p/{project_id}/define/problem/q/1", wait_until="load")
    page.locator("h1").first.wait_for(state="visible", timeout=60_000)
    page.wait_for_timeout(1500)
    shot.screenshot(f"prevalence-{label}")
    calibration = wait_calibration(run, project_id, "PROBLEM")
    prevalence = next((q for q in calibration.get("questions") or [] if q.get("dimension") == "problem.prevalence"), {})
    heading = _safe(lambda: page.locator("main h1, .ccard h1").first.inner_text())
    leg.check(run, f"{label}: Prevalence is drawn with the story's own event (the chain applied on the founder's runtime)",
              calibration.get("state") == "READY" and run.prevalence["event"] in (prevalence.get("question") or ""),
              screen="define/problem/q/1", detail={"state": calibration.get("state"),
                                                   "question": prevalence.get("question"), "drawn": heading})
    return {"calibration": calibration}


# ------------------------------------------------------------------------------------------------ the drawn story (158b)

#: The founder's story player (keel-web 245 FR-6: `StoryCheck`'s story state) and its state line.
FOUNDER_PLAYER = "[data-testid=story-readback] .sty-player"
FOUNDER_STATE = "[data-testid=story-readback] [data-testid=story-state]"
#: The stranger's story card (keel-web 241 FR-7) and its *Play*.
STRANGER_PLAYER = "[data-testid=story-screen] [data-testid=story-player]"
STRANGER_STATE = "[data-testid=story-screen] [data-testid=story-play]"


def measure_fit(run: Run, leg: Leg, page, label: str, root: str, *, where: str, view: str, phone: bool,
                state: str | None = None, play: bool = False) -> dict:
    """Spec 158b: one drawn story read while it plays (`story_screens.measure_story`), kept on `run.fits`, and judged:
    no text on the drawing, the spoken line at most three rows, and on a phone the story fits. Never stops the leg."""
    measured = ss.measure_story(page, root, state=state, play=play)
    verdicts = ss.fit_verdicts(measured, phone=phone)
    party = "founder" if view.startswith("founder") else "participant"
    try:
        ss._BrowserStep(run.recorder, page, party).screenshot(
            f"drawn-story-{re.sub(r'[^a-z0-9]+', '-', (label + ' ' + view).lower()).strip('-')}")
    except Exception:  # noqa: BLE001 - a screenshot
        pass
    run.fits.append({"label": label, "where": where, "view": view, "phone": phone, "measured": measured,
                     "verdicts": {k: v[0] for k, v in verdicts.items()}})
    ok, detail = verdicts["drawn"]
    leg.check(run, f"{label}: no text on the drawing -- no label, caption or spoken line over a drawn figure, room or "
                   "pictogram while the story plays", ok, screen=where, view=view, detail=detail, stop=False)
    if phone:
        ok, detail = verdicts["fits"]
        leg.check(run, f"{label}: fits on a phone ({ss.PHONE['width']} x {ss.PHONE['height']}) -- the frame, the line "
                       "and the player's state inside the screen, nothing scrolling", ok, screen=where, view=view,
                  detail=detail, stop=False)
    ok, detail = verdicts["rows"]
    leg.check(run, f"{label}: the spoken line is at most {ss.LINE_ROWS_MAX} rows", ok, screen=where, view=view,
              detail=detail, stop=False)
    return measured


def phone_story(run: Run, leg: Leg, project_id: str, label: str) -> None:
    """Spec 158b: the founder's story again on a phone (390 x 844, her own cookies): `define/story/check` opened, the
    begin screen's orb tapped where it stands, and the story read while it plays."""
    phone, page = ss.phone_page(run.context, run.browser, inits=(ivs.SPEECH_SEAM, ss.ORB_WATCH))
    try:
        page.goto(f"{run.web}/p/{project_id}/define/story/check", wait_until="load")
        try:
            ss.wake(page, timeout_s=20)
        except AssertionError:
            pass                          # no begin screen and no voice: the story may stand without one
        try:
            page.locator(FOUNDER_PLAYER).first.wait_for(state="visible", timeout=30_000)
        except Exception:  # noqa: BLE001 - recorded by the read: never drawn
            pass
        measure_fit(run, leg, page, f"{label} (phone)", FOUNDER_PLAYER, where="define/story/check (story, reopened)",
                    view="founder · phone", phone=True, state=FOUNDER_STATE)
    finally:
        phone.close()


# ------------------------------------------------------------------------------------------------ FR-1 (a)

#: FR-1 (a)'s two problem projects: the script's own words, and the long telling with the correction (spec 158 FR-1).
FR1A_TOLD = (("a-script", "the script's words", False), ("a-long", "the long telling", True))


def fr1_a(run: Run, leg: Leg) -> None:
    """Two problem projects by voice, to Prevalence: one told in the script's own words (every reading scripted, the
    cost heard), one told the long way (beat 3 over 1,500 characters, five limitations and a cost in one breath, read
    by the cloud's echo; *only the ones in Europe* after beat 4's readback; the cost drafted from the limitations)."""
    for key, label, long3 in FR1A_TOLD:
        name = f"158 problem {'long' if long3 else 'script'} {run.stamp}"
        run.new_project(name, "PROBLEM")
        pid = MarketStep(run.page, run.recorder, run.web).start()
        run.projects[key] = pid
        run.names[key] = name
        run.page.wait_for_timeout(1500)
        leg.check(run, f"{label}: a new problem project opens on its conversation", "/define" in run.page.url,
                  screen="/p/{id}", detail=run.page.url, stop=False)
        tell_the_story(run, leg, pid, label, long3=long3, correction=ss.CORRECTION_4 if long3 else None)
        window_then_prevalence(run, leg, pid, label)
        phone_story(run, leg, pid, label)
    review = run.get(f"/v2/projects/{run.projects['a-script']}/review/PROBLEM") or {}
    want = ss.reading_of(run.readings, max(n for n, _ in ss.said_turns(run.readings))).get("statement")
    leg.check(run, "the statement is the last beat's reading's (keel-cloud 263 judgement call 4: drafted on beats 3-5)",
              review.get("statement") == want, screen="review/PROBLEM", view="wire",
              detail={"statement": review.get("statement"), "want": want})


# ------------------------------------------------------------------------------------------------ FR-1 (b)

def idea_leg(run: Run, leg: Leg, solution: str, label: str, *, back_to_money: bool = False,
             before_yes: Callable[[], None] | None = None) -> dict:
    """keel-web 245 FR-11 on a solution project: the problem replayed and closed by the quiet (never corrected), the
    two beats (the name with a colour said; how it solves the limitations), the idea's boxes by the quiet, the build,
    the day with the idea (the name and the colour on it, clearly), then the quiet goes on."""
    idea = ss.IdeaWalk(run.page, run.recorder, run.web)
    replay = idea.replay(solution)
    board = replay["screen"].get("board") or ""
    problem = run.get(f"/v2/projects/{solution}/story") or {}
    rcard = replay["screen"].get("card") or {}
    rrows = ss.card_rows(rcard)
    leg.check(run, f"{label}: the problem replayed -- its card (*What Keel understood*, read by `data-box`: the person, "
                   "the limitations, no cost row), the turn line, no button; the quiet stamps still the problem "
                   "(story/confirm 200), nothing corrected",
              replay["confirm"]["status"] == 200 and replay["screen"].get("said") == ss.SOLUTION_TURN
              and not replay["screen"].get("buttons") and not idea.writes_to(r"/story/correct$")
              and rcard.get("label") == ss.CARD_LABEL and "person" in rrows and "cost" not in rrows
              and set(rrows) <= set(ss.CARD_ROWS)
              and (not problem.get("cost") or _bare(problem.get("cost")) not in _bare(board)),
              screen="define/idea/start (the replay)",
              detail={"said": replay["screen"].get("said"), "rows": rrows, "cost": problem.get("cost"),
                      "woke": replay.get("woke"), "buttons": replay["screen"].get("buttons"),
                      "confirm": replay["confirm"]["status"]})
    turn_screen(run, leg, label, replay["screen"], "define/idea/start (the replay)", card=True)
    said = ss.said_idea(run.readings)
    name = str(ss.idea_reading_of(run.readings, 1).get("name") or said[0][1])
    words1 = ss.said_name(name)
    beats = idea.beats(said, name_words=words1)
    run.beats.append({"label": f"{label} (idea)", "project": solution, "beats": list(beats.values()), "idea": True})
    b1, b2 = beats[1], beats[2]
    brand = (((b1.get("put") or {}).get("body") or {}).get("idea") or {}).get("brand") or {}
    leg.check(run, f"{label}: idea beat 1 -- *{words1}*: the name read and the colour said written as its hex "
                   f"({ss.SAID_COLOUR[1]}); the drop zone the one control, no button",
              (b1["put"]["status"] or 500) < 400 and brand.get("name") == name
              and str(brand.get("colour") or "").lower() == ss.SAID_COLOUR[1] and b1["asked"].get("drop") is True
              and not b1["asked"].get("buttons") and not b1["readback"].get("buttons"),
              screen="define/idea/1", detail={"brand": brand, "asked": b1["asked"].get("question"),
                                              "buttons": b1["asked"].get("buttons")})
    read2 = ((b2.get("put") or {}).get("body") or {})
    answers = ((read2.get("idea") or {}).get("limitAnswers") or [])
    marks = b2["readback"].get("marks") or []
    leg.check(run, f"{label}: idea beat 2 -- one answer mapped to ticks and crosses, one a limitation, the readback "
                   "counting them; no button",
              (b2["put"]["status"] or 500) < 400 and len(marks) == len(answers) == len(ss.limits_read(run.readings))
              and [m.get("mark") for m in marks] == ["tick" if a.get("solved") else "cross" for a in answers]
              and bool(read2.get("readback")) and not b2["readback"].get("buttons"),
              screen="define/idea/2", detail={"marks": marks, "answers": answers, "readback": read2.get("readback")})
    iu = b2["readback"].get("understood") or {}
    imarks = ss.card_items(iu, "limits")
    leg.check(run, f"{label}: idea beat 2's ticks and crosses are a card (`idea-understood`: *What Keel understood*, the "
                   "row `limits`, each line `data-mark` tick or cross as the reading maps it; keel-web 249 FR-4)",
              iu.get("label") == ss.CARD_LABEL and [r.get("box") for r in iu.get("rows") or []] == ["limits"]
              and [m.get("mark") for m in imarks] == ["tick" if a.get("solved") else "cross" for a in answers],
              screen="define/idea/2 (idea-understood)", detail={"card": iu, "answers": answers}, stop=False)
    orbs = {n: b.get("orb") for n, b in beats.items()}
    leg.check(run, f"{label}: the orb through each idea beat -- speaking, listening, hearing, writing, speaking, and from "
                   "writing straight to speaking (keel-web 249)",
              all(ss.holds_in_order(o or [], ss.BEAT_ORB) and ss.writing_then_speaking(o or []) for o in orbs.values()),
              screen="define/idea/1..2", detail=orbs, stop=False)
    small = {n: {k: (b.get("asked") or {}).get(k) for k in ("orbs", "orbSize", "glow", "line")} for n, b in beats.items()}
    leg.check(run, f"{label}: the small orb on each idea beat (one, at most 44 px), its state line beside it, no glow",
              all(v["orbs"] == 1 and (v["orbSize"] or 99) <= 44 and v["line"] and not v["glow"] for v in small.values()),
              screen="define/idea/1..2 (story-orb, story-state)", detail=small, stop=False)
    boxes = idea.boxes()
    icard = boxes["screen"].get("card") or {}
    irows = ss.card_rows(icard)
    iticks = [m.get("mark") for m in ss.card_items(icard, "limits")]
    leg.check(run, f"{label}: the idea's boxes are the card -- by `data-box`: the person, *The product* with the name "
                   f"(`today`), *How it helps* as ticks and crosses (`limits`); *Is that your idea?*, no button, the quiet "
                   "confirms (idea/confirm 200)",
              boxes["confirm"]["status"] == 200 and boxes["screen"].get("said") == ss.IDEA_BOXES_ASK
              and not boxes["screen"].get("buttons") and icard.get("label") == ss.CARD_LABEL
              and "person" in irows and _bare(name) in _bare(irows.get("today"))
              and iticks == ["tick" if a.get("solved") else "cross" for a in answers],
              screen="define/idea/check (boxes)",
              detail={"said": boxes["screen"].get("said"), "rows": irows, "marks": iticks,
                      "names": {r.get("box"): r.get("name") for r in icard.get("rows") or []},
                      "confirm": boxes["confirm"]["status"]})
    turn_screen(run, leg, label, boxes["screen"], "define/idea/check (boxes)", card=True)
    built = idea.building_then_story(name)
    spoken = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    leg.check(run, f"{label}: the idea's build reaches ready; the day with the idea drawn", built["state"] == "story"
              and ((spoken.get("build") or {}).get("state") == "ready"), screen="define/idea/check (story)",
              detail={"screen": built["state"], "build": (spoken.get("build") or {}).get("state")})
    probe = built.get("brand") or {}
    label_ = probe.get("label") or {}
    colour = ss.rgb_of(ss.SAID_COLOUR[1])
    leg.check(run, f"{label}: the story carries the icon in the colour and the name clearly -- never faded, cropped or "
                   "shrunk (the review condition)",
              bool(label_) and (label_.get("opacity") or 0) >= 0.99 and label_.get("inside") is True
              and label_.get("clipped") is False and (label_.get("fontPx") or 0) >= 12 and label_.get("color") == colour
              and colour in (probe.get("badges") or []), screen="define/idea/check (story)",
              detail={"probe": probe, "want colour": colour})
    if before_yes:
        before_yes()
    landed = idea.story_yes(lands=re.compile(r"start=money") if back_to_money else ss.COMPATIBILITY_PATH)
    read = idea.turn_read()
    hand_over_checks(run, leg, label, read, "define/idea/*", beat_path=r"/define/idea/\d$")
    sheets = ss.sheet_verdict(read["sheets"])
    leg.check(run, f"{label}: no welcome sheet on the solution's conversation, one sheet at a time (keel-web 249 FR-6)",
              not sheets["welcome_on"] and sheets["one_at_a_time"], screen="define/idea/* (guide-opener, guide-welcome)",
              detail={"sheets": sheets, "woke": replay.get("woke")}, stop=False)
    heard = ss.heard_verdict(read["heard"], dict([(1, words1), (2, dict(said)[2])]), lambda n: f"/define/idea/{n}")
    leg.check(run, f"{label}: each idea beat's words shown as heard (*What I hear*, `story-heard`), never among Keel's "
                   "lines (keel-web 249 FR-4)", heard["all_shown"] and heard["words_keels_only"],
              screen="define/idea/1..2 (story-heard, story-words)", detail=heard, stop=False)
    return {"name": name, "landed": landed["landed"], "said": said}


def fr1_b(run: Run, leg: Leg) -> None:
    name = f"158 solution {run.stamp}"
    run.new_project(name, "SOLUTION")
    start = ss.SolutionStart(run.page, run.recorder, run.web)
    start.press_start()
    opened = start.read()
    defined = [k for k in ("a-script", "a-long") if run.projects.get(k)]
    leg.check(run, "the which-problem page: a page (no orb, nothing spoken), the defined problem projects listed with "
                   "their first frame, *A new problem*; nothing created",
              opened["orb"] == 0 and opened["create"].endswith(ss.NEW_PROBLEM)
              and (opened["pending"] or {}).get("scope") == "SOLUTION"
              and {r["project"] for r in opened["rows"]} >= {run.projects[k] for k in defined}
              and all(r["frame"] for r in opened["rows"]),
              screen="which problem (define a solution)", detail=opened)
    problem = start.create_problem()
    run.projects["b-problem"] = problem
    run.names["b-problem"] = ss.problem_name_of(name)
    created = start.created_problem
    leg.check(run, "*A new problem* is one POST: scope PROBLEM, the problem's name, then its conversation opens",
              created["status"] == 201 and (created["sent"] or {}).get("scope") == "PROBLEM"
              and (created["sent"] or {}).get("name") == ss.problem_name_of(name),
              screen="which problem", detail=created)
    told = tell_the_story(run, leg, problem, "the solution's problem", back_to="solution", goto=False)
    leg.check(run, "the story's quiet is the return trip: the which-problem page with the problem just agreed picked",
              f"problem={problem}" in told["landed"], screen="define/story/check -> /?start=solution",
              detail=told["landed"])
    back = start.read()
    first = (back["rows"] or [{}])[0]
    leg.check(run, "back on the page: the agreed problem first, picked, *Continue with this problem*",
              first.get("project") == problem and first.get("picked") is True
              and first.get("press") == "Continue with this problem", screen="which problem (picked)", detail=back)
    run.load_runtime("SOLUTION")
    made = start.pick(problem)
    solution = str((made["body"] or {}).get("projectId"))
    run.projects["b-solution"] = solution
    run.names["b-solution"] = name
    leg.check(run, "the pick is the one create request: scope SOLUTION and parentProjectId the problem project; lineage "
                   "names it", made["status"] == 201 and (made["sent"] or {}).get("parentProjectId") == problem
              and ((made["body"] or {}).get("lineage") or {}).get("problemProjectId") == problem,
              screen="which problem", detail=made)
    done = idea_leg(run, leg, solution, "the solution")
    leg.check(run, "the idea's story's quiet lands on Compatibility", bool(ss.COMPATIBILITY_PATH.search(done["landed"])),
              screen="define/solution/q/1", detail=done["landed"])
    calibration = wait_calibration(run, solution, "SOLUTION")
    ra = next((q for q in calibration.get("questions") or [] if q.get("dimension") == "solution.relative_advantage"),
              {})
    benefits = list(ss.idea_reading_of(run.readings, 2).get("benefits") or [])
    said_what = json.dumps(ra.get("answerWhat") or ra.get("answer") or "")
    leg.check(run, "Relative advantage arrives pre-filled with the idea's benefits (keel-cloud 260 judgement call 12)",
              bool(benefits) and all(b in said_what for b in benefits), screen="define/solution (Relative advantage)",
              view="wire", detail={"answerWhat": ra.get("answerWhat"), "benefits": benefits,
                                   "state": calibration.get("state")})


def wait_calibration(run: Run, project_id: str, vector: str, *, timeout_s: float = 60) -> dict:
    deadline = time.monotonic() + timeout_s
    view: dict = {}
    while time.monotonic() < deadline:
        view = run.get(f"/v2/projects/{project_id}/calibration/{vector}") or {}
        if view.get("state") in ("READY", "FAILED"):
            return view
        time.sleep(1)
    return view


# ------------------------------------------------------------------------------------------------ FR-1 (d)

def press_lock(run: Run) -> tuple[int, Any]:
    """The lock screen's one primary, pressed on the page; what `POST lock` answered."""
    button = run.page.get_by_test_id("lock-and-record").first
    button.wait_for(state="visible", timeout=30_000)
    run.page.wait_for_function("(b) => !b.disabled", arg=button.element_handle(), timeout=30_000)
    with run.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/lock"),
                                  timeout=30_000) as locked:
        button.click()
    try:
        body = locked.value.json()
    except Exception:  # noqa: BLE001
        body = locked.value.text()
    return locked.value.status, body


def fr1_d(run: Run, leg: Leg) -> None:
    problem, solution = run.projects.get("b-problem"), run.projects.get("b-solution")
    if not problem or not solution:
        leg.status, leg.why = "skipped", "FR-1(b) made no defined problem project"
        return
    page = run.page
    Landing(page, run.recorder, run.web).visit()
    row = page.locator(f"[data-testid=project-row-defined][data-under='{solution}']").first
    try:
        row.wait_for(state="visible", timeout=15_000)
        drawn = {"text": _safe(lambda: row.inner_text()), "href": row.get_attribute("href")}
    except Exception:  # noqa: BLE001 - recorded
        drawn = {"rows": _safe(lambda: page.locator(".project-list").first.inner_text())}
    wire = run.list_row(problem)
    leg.check(run, "the list nests the defined problem project under the study that uses it, *Defined, not sent*",
              "Defined, not sent" in (drawn.get("text") or "") and (drawn.get("href") or "").endswith(problem)
              and (wire.get("definition") or {}).get("status") == "defined", screen="/ (the project list)",
              detail={"drawn": drawn, "wire": {k: wire.get(k) for k in ("definition", "lineage", "story")}})
    with run.recorder.step("FR-1d: the founder opens it from the list", party="founder"):
        row.click()
        page.wait_for_url(re.compile(rf"/p/{problem}"), timeout=30_000)
        page.wait_for_timeout(2500)
    resumed = page.url
    leg.check(run, "it resumes at the window screen", "/define/context/window" in resumed
              or page.locator("[data-testid=context-window-page]").count() > 0, screen="/p/{id} (resume)",
              detail={"url": resumed, "card": _safe(lambda: page.locator(".understands").first.inner_text())},
              stop=False)
    run.load_runtime("PROBLEM")
    j = run.journey("d", "PROBLEM", problem)
    page.goto(f"{run.web}/p/{problem}/define/problem/q/1", wait_until="load")
    cs.leg_calibrate(j, "PROBLEM")
    cs.plan_complete(j)
    leg.check(run, "calibrated: the plan reads complete over the problem", True, screen="define/problem/*",
              detail=j.changed.get("plan_complete"))
    page.goto(f"{run.web}/p/{problem}/define/ready/interviewer", wait_until="load")
    if run.remote:
        leg.notes.append("remote profile: no stand-in -- the drained grant and the lock's charge are not walked; the "
                         "lock is the founder's own door's")
        status, body = press_lock(run)
        leg.check(run, "the lock (own door) taken", status in (200, 201), screen="define/ready (lock)", detail=body)
    else:
        acct = run.account_id
        ledger.stand_in_keels_door(run.stack, acct, f"d-door-{run.stamp}", spec=STAND_IN_SPEC)
        ledger.stand_in_balance(run.stack, acct, f"d-{run.stamp}", to=DRAINED_TO, spec=STAND_IN_SPEC, label="drained",
                                what=f"the balance drained to {DRAINED_TO} to see the lock refused")
        page.reload(wait_until="load")
        status, body = press_lock(run)
        leg.check(run, f"with {DRAINED_TO} credits the lock refuses as today (422 {INSUFFICIENT}), nothing locked",
                  status == 422 and (body or {}).get("code") == INSUFFICIENT
                  and not ((run.get(f"/v2/projects/{problem}/overview") or {}).get("locked")),
                  screen="define/ready (lock)", detail=body)
        ledger.stand_in_balance(run.stack, acct, f"d-{run.stamp}", to=ledger.GRANT_CREDITS, spec=STAND_IN_SPEC,
                                label="topped", what="the balance back to the grant to see the lock bought")
        try:
            before = ledger.now(run.stack)
            page.reload(wait_until="load")
            status, body = press_lock(run)
            rows = [r for r in ledger.rows(run.stack, acct, since=before)
                    if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
            charges = [r for r in rows if (r.get("credits") or 0) < 0]
            leg.check(run, f"with enough credits the lock is taken and the ledger shows one charge: the PROJECT's "
                           f"{PROJECT_PRICE}", status in (200, 201) and len(charges) == 1
                      and charges[0].get("action") == "PROJECT" and charges[0].get("credits") == -PROJECT_PRICE,
                      screen="define/ready (lock)", view="wire", detail={"status": status, "charges": charges,
                                                                          "rows": len(rows)})
        finally:
            ledger.restore_own_door(run.stack, acct, f"d-restore-{run.stamp}", spec=STAND_IN_SPEC)
        retry_questions(run, leg, problem)
    send_link(run, leg, "d", problem, "TEXT")


def retry_questions(run: Run, leg: Leg, project_id: str) -> None:
    """The lock's questions, started on Keel's door (no key on this stack: KEEL_AI_DISABLED), written again on the
    founder's own door -- `POST questionnaire/retry`, the screen's *Try again* -- by the scripted runtime."""
    deadline = time.monotonic() + 30
    state = None
    while time.monotonic() < deadline:
        state = (run.get(f"/v2/projects/{project_id}/overview") or {}).get("questionsState")
        if state in ("READY", "FAILED"):
            break
        time.sleep(1)
    if state != "READY":
        status, body = run.call("POST", f"/v2/projects/{project_id}/questionnaire/retry")
        run.recorder.note(f"questionnaire/retry on the own door: {status}", party="founder")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            state = (run.get(f"/v2/projects/{project_id}/overview") or {}).get("questionsState")
            if state == "READY":
                break
            time.sleep(1)
    leg.check(run, "the lock's questions READY (written on the founder's own door)", state == "READY",
              screen="define/ready -> Sent", view="wire", detail={"state": state})


def open_sent(run: Run, project_id: str) -> None:
    """Sent, with the account's first *Interviews · How it works* page got through (*Got it*, the PATCH of /v2/me) where
    it is drawn -- keel-web's page of that name since the find-people batch, which `Interviews.walkthrough`'s W1 reads
    by its older classes -- and keel-web 088's first-open sheet passed by."""
    page = run.page
    page.goto(f"{run.web}/p/{project_id}/interviews/sent", wait_until="load")
    page.locator(".sent__kinds, button:has-text('Got it')").first.wait_for(state="visible", timeout=60_000)
    got_it = page.get_by_role("button", name="Got it", exact=True)
    if not page.locator(".sent__kinds").count() and got_it.count():
        with run.recorder.step("Sent: the account's first *Interviews · How it works* -- Got it", party="founder"):
            got_it.first.click()
            page.wait_for_url(re.compile(r"/interviews/sent"), timeout=20_000)
    page.locator(".sent__kinds").first.wait_for(state="visible", timeout=60_000)
    iv_screens.pass_interviews_sheet(page, run.recorder, run.web)


def send_link(run: Run, leg: Leg, key: str, project_id: str, fmt: str, *, person: str | None = None,
              decider: bool = False) -> dict:
    """One link on Sent's *Send more*, the person named (a corpus person of the base entry)."""
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == vs.LINK_B2B) == decider), kinds[0] if kinds else {})
    who = person or next(p.person for p in vs.person_inputs(run.base_entry("PROBLEM")))
    sent = iv_screens.Interviews(run.page, run.recorder, run.web)
    open_sent(run, project_id)
    made = sent.send_someone(project_id, kind.get("label"), who, fmt)
    leg.check(run, f"a {fmt} link sent to {who}", made.get("status") == 201 and bool(made.get("url")),
              screen="Sent · Send more", detail={k: made.get(k) for k in ("status", "url", "formats")})
    run.findings.append({"link": key, "person": who, "url": made.get("url")})
    return made


# ------------------------------------------------------------------------------------------------ FR-1 (c)

#: keel-web 243's start component; the money legs run only where keel-web carries it (spec 157 judgement call 5).
MONEY_START_SOURCE = "src/components/money/MoneyStart.tsx"


def web_has_243(run: Run) -> bool:
    root = Path(run.stack.keel_web)
    if (root / MONEY_START_SOURCE).exists():
        return True
    return any("MoneyStart" in p.read_text(encoding="utf-8", errors="replace")
               for p in (root / "src").rglob("*.tsx") if p.name.startswith("Money"))


def money_start(run: Run) -> dict:
    """The market's Start on the money scope: keel-web 245 FR-12's which-problem page (a page, no orb)."""
    page = run.page
    with run.recorder.step("the market's Start on the money scope opens the which-problem page", party="founder"):
        page.get_by_role("button", name=re.compile(r"^start$", re.I)).first.click()
        root = page.locator("[data-testid=money-start][data-screen=problem]").first
        root.wait_for(state="visible", timeout=30_000)
        try:
            root.get_by_test_id("money-problem").first.wait_for(state="visible", timeout=10_000)
        except Exception:  # noqa: BLE001 - none listed: recorded
            pass
    return {"rows": [r.get_attribute("data-project") for r in root.get_by_test_id("money-problem").all()],
            "orb": page.locator(ss.ORB).count(), "title": _safe(lambda: root.locator("h2").first.inner_text())}


def fr1_c(run: Run, leg: Leg) -> None:
    """keel-web 245 FR-12 (243's money start, on the pages): a money study from nothing -- the which-problem page's *A
    new problem*, its conversation, back with it picked; the which-solution page's *A new solution*, its conversation,
    back; *Use {name}*: the money project created on the solution, the one orb moment (the problem replayed with the
    idea's box lit, the quiet), today's persona step pre-filled; Existing sacrifice's prompt the story's cost line; the
    money calibrated, locked once (one PROJECT charge), the decision-maker's link sent. Then a money study with only a
    name (keel-cloud 263 FR-10): the which-solution page's *Use this name*, its orb moment, the persona step -- walked
    that far only (no lock fixture for it in keel-cloud yet)."""
    if not web_has_243(run):
        leg.status = "written, not run"
        leg.why = ("keel-web 243 (the money start) is not in the keel-web checkout the stack serves "
                   f"({MONEY_START_SOURCE} absent): written to specs/243's spec.md, not run")
        return
    page = run.page
    name = f"158 money {run.stamp}"
    run.new_project(name, "COMMERCIAL")
    opened = money_start(run)
    leg.check(run, "the which-problem page: a page (no orb), the defined problem projects listed", opened["orb"] == 0
              and len(opened["rows"]) >= 2, screen="which problem (will they pay)", detail=opened)
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        page.get_by_test_id("money-create-problem").first.click()
    problem = str((got.value.json() or {}).get("projectId"))
    run.projects["c-problem"] = problem
    leg.check(run, "*A new problem*: one POST, scope PROBLEM, then its conversation",
              got.value.status == 201 and (got.value.request.post_data_json or {}).get("scope") == "PROBLEM",
              screen="which problem (will they pay)", detail=got.value.request.post_data_json)
    page.locator(ss.STORY_START).first.wait_for(state="visible", timeout=30_000)
    told = tell_the_story(run, leg, problem, "the money's problem", back_to="money", goto=False)
    leg.check(run, "the story's quiet goes back to the money start", "start=money" in told["landed"],
              screen="define/story/check -> /?start=money", detail=told["landed"])
    second = page.locator("[data-testid=money-start][data-screen=solution]").first
    second.wait_for(state="visible", timeout=30_000)
    leg.check(run, "back with the problem picked: the which-solution page (none prices it yet: *A new solution* and "
                   "*or just the name*), no orb", page.get_by_test_id("money-use-solution").count() == 0
              and page.get_by_test_id("money-create-solution").count() == 1
              and page.get_by_test_id("money-offer-name").count() == 1 and page.locator(ss.ORB).count() == 0,
              screen="which solution", detail=_safe(lambda: second.inner_text()))
    run.load_runtime("SOLUTION")
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        page.get_by_test_id("money-create-solution").first.click()
    solution = str((got.value.json() or {}).get("projectId"))
    run.projects["c-solution"] = solution
    leg.check(run, "*A new solution*: scope SOLUTION on the problem (parentProjectId)",
              got.value.status == 201 and (got.value.request.post_data_json or {}).get("parentProjectId") == problem,
              screen="which solution", detail=got.value.request.post_data_json)
    # the runtime moves to the money before the idea's quiet goes back (157's order: the money project is made next)
    done = idea_leg(run, leg, solution, "the money's solution", back_to_money=True,
                    before_yes=lambda: run.load_runtime("COMMERCIAL"))
    use = page.locator(f"[data-testid=money-solution][data-project='{solution}'] [data-testid=money-use-solution]").first
    use.wait_for(state="visible", timeout=30_000)
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        use.click()
    body = got.value.json() or {}
    money = str(body.get("projectId"))
    run.projects["c-money"] = money
    leg.check(run, "*Use {name}* creates the money project on the solution (scope COMMERCIAL, parentProjectId); lineage "
                   "names both", got.value.status == 201 and (got.value.request.post_data_json or {}).get("parentProjectId")
              == solution and (body.get("lineage") or {}).get("solutionProjectId") == solution
              and (body.get("lineage") or {}).get("problemProjectId") == problem, screen="which solution",
              detail={"sent": got.value.request.post_data_json, "lineage": body.get("lineage")})
    replay = ss.MoneyReplay(page, run.recorder, run.web).walk()
    said = replay["screen"].get("said") or ""
    leg.check(run, f"the one orb moment: the problem replayed with the idea's box lit, *This is the problem, and this is "
                   f"{done['name']}. Now, will they pay for it?*, the quiet -- then today's persona step; nothing corrected",
              said == f"This is the problem, and this is {done['name']}. Now, will they pay for it?"
              and replay["landed"].endswith("/define/persona") and not replay["corrected"]
              and not replay["screen"].get("buttons"), screen="define/money/start",
              detail={"said": said, "rows": ss.card_rows(replay["screen"].get("card")), "landed": replay["landed"],
                      "woke": replay.get("woke")})
    money_card(run, leg, "the money's replay", replay, done["name"])
    ss.pass_the_welcome(page)
    context = run.get(f"/v2/projects/{money}/context") or {}
    idea_view = run.get(f"/v2/projects/{money}/idea") or {}
    actor = ss.reading_of(run.readings, 1).get("actor")
    leg.check(run, "the persona screen, pre-filled: the chain's actor and the idea's name",
              (context.get("fields") or {}).get("actor") is not None and bool(idea_view.get("what") or
                                                                              idea_view.get("shortName")),
              screen="define/persona", detail={"context": context.get("fields"), "actor (script)": actor,
                                               "idea": {k: idea_view.get(k) for k in ("what", "shortName", "line")}})
    j = run.journey("c", "COMMERCIAL", money)
    # the idea's name every money question uses is the chain's (keel-cloud 261 FR-2: Price names the idea)
    j.idea_name = str(idea_view.get("shortName") or idea_view.get("what") or "")
    j.idea_what_it_is = idea_view.get("whatItIs")
    j.idea_line = idea_view.get("line") or None
    cs.leg_persona(j)
    calibration = wait_calibration(run, money, "COMMERCIAL")
    cost = next((q for q in calibration.get("questions") or [] if q.get("dimension") == "commercial.existing_sacrifice"),
                {})
    built_story = ((run.get(f"/v2/projects/{problem}/story") or {}).get("build") or {}).get("story") or {}
    leg.check(run, "Existing sacrifice's prompt is the problem story's cost line (keel-cloud 261 judgement call 6)",
              bool(cost.get("prompt")) and cost.get("prompt") == built_story.get("costLine"),
              screen="define/commercial (Existing sacrifice)", view="wire",
              detail={"prompt": cost.get("prompt"), "costLine": built_story.get("costLine")}, stop=False)
    cs.leg_calibrate(j, "COMMERCIAL")
    cs.plan_complete(j)
    page.goto(f"{run.web}/p/{money}/define/ready/interviewer", wait_until="load")
    lock_once(run, leg, j, money)
    send_link(run, leg, "c", money, "TEXT", decider=True)
    money_by_name(run, leg, problem, done["name"])


def money_card(run: Run, leg: Leg, label: str, replay: dict, product: str) -> None:
    """Spec 158c FR-7 (keel-web 249 FR-5): the money front's replay is the card -- *What Keel understood*, the person,
    *The product* with the name (`today`), no cost row, nothing drawn -- under the small orb, no glow; its one
    hand-over chimed once; no welcome sheet on `define/money/start` (FR-8)."""
    card = replay["screen"].get("card") or {}
    rows = ss.card_rows(card)
    leg.check(run, f"{label}: the card (by `data-box`: the person, *The product* naming *{product}*, no cost row)",
              card.get("label") == ss.CARD_LABEL and "person" in rows and _bare(product) in _bare(rows.get("today"))
              and "cost" not in rows, screen="define/money/start (story-boxes)",
              detail={"rows": rows, "lit": card.get("lit")}, stop=False)
    turn_screen(run, leg, label, replay["screen"], "define/money/start", card=True)
    read = replay.get("turn") or {}
    v = (read.get("chime") or {})
    sheets = ss.sheet_verdict(read.get("sheets") or [])
    leg.check(run, f"{label}: the one hand-over chimed once ({v.get('hand_overs')} hand-over(s), {v.get('chimes')} "
                   "chime(s)), *Your turn.* beside the listening orb; no welcome sheet, one sheet at a time",
              bool(v.get("hand_overs")) and v.get("one_each") and v.get("your_turn") and v.get("mic_open")
              and not sheets["welcome_on"] and sheets["one_at_a_time"], screen="define/money/start",
              detail={"chime": v, "sheets": sheets}, stop=False)


def money_by_name(run: Run, leg: Leg, problem: str, product: str) -> None:
    """Keel-cloud 263 FR-10 / keel-web 245 FR-12: a money study with only the product's name -- the which-problem page's
    pick, the which-solution page's *or just the name* (`offerName`, a PROBLEM parent), the orb moment with the name
    alone, the persona step. Walked to the persona step only: keel-cloud has no lock fixture for a name-only money
    study yet (263 judgement call 16), so nothing is calibrated or locked on it."""
    page = run.page
    name = f"158 money by name {run.stamp}"
    run.new_project(name, "COMMERCIAL")
    opened = money_start(run)
    row = page.locator(f"[data-testid=money-problem][data-project='{problem}'] [data-testid=money-pick-problem]").first
    row.wait_for(state="visible", timeout=30_000)
    row.click()
    page.locator("[data-testid=money-start][data-screen=solution]").first.wait_for(state="visible", timeout=30_000)
    page.get_by_test_id("money-offer-name").first.fill(product)
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        page.get_by_test_id("money-use-name").first.click()
    body = got.value.json() or {}
    sent = got.value.request.post_data_json or {}
    run.projects["c-money-name"] = str(body.get("projectId"))
    leg.check(run, f"*or just the name* -- *{product}*, *Use this name*: the money project on the problem itself "
                   "(offerName, a PROBLEM parent; lineage names the problem)",
              got.value.status == 201 and sent.get("offerName") == product and sent.get("parentProjectId") == problem
              and (body.get("lineage") or {}).get("problemProjectId") == problem,
              screen="which solution (or just the name)", detail={"page": opened, "sent": sent,
                                                                   "status": got.value.status,
                                                                   "lineage": body.get("lineage")})
    replay = ss.MoneyReplay(page, run.recorder, run.web).walk()
    said = replay["screen"].get("said") or ""
    leg.check(run, f"the orb moment with the name alone (*... and this is {product}. Now, will they pay for it?*), the "
                   "quiet, then the persona step", said.endswith(f"this is {product}. Now, will they pay for it?")
              and replay["landed"].endswith("/define/persona") and not replay["corrected"],
              screen="define/money/start (a name only)", detail={"said": said, "landed": replay["landed"],
                                                                  "rows": ss.card_rows(replay["screen"].get("card"))})
    money_card(run, leg, "the money by name's replay", replay, product)
    leg.notes.append("the money study with only a name was walked to the persona step and no further: keel-cloud has no "
                     "lock fixture for it yet (263 judgement call 16; spec 158's brief)")


def lock_once(run: Run, leg: Leg, j: cs.Journey, project_id: str) -> None:
    """The lock on Keel's door (a stand-in grant) -- one PROJECT charge -- then the questions on the own door."""
    if run.remote:
        status, body = press_lock(run)
        leg.check(run, "the lock (own door) taken", status in (200, 201), screen="define/ready (lock)", detail=body)
        return
    acct = run.account_id
    ledger.stand_in_keels_door(run.stack, acct, f"{project_id[:8]}-door-{run.stamp}", spec=STAND_IN_SPEC)
    try:
        before = ledger.now(run.stack)
        run.page.reload(wait_until="load")
        status, body = press_lock(run)
        rows = [r for r in ledger.rows(run.stack, acct, since=before)
                if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
        charges = [r for r in rows if (r.get("credits") or 0) < 0]
        leg.check(run, f"locked once, and the ledger's one charge is the PROJECT's {PROJECT_PRICE}",
                  status in (200, 201) and len(charges) == 1 and charges[0].get("action") == "PROJECT"
                  and charges[0].get("credits") == -PROJECT_PRICE, screen="define/ready (lock)", view="wire",
                  detail={"status": status, "charges": charges, "rows": len(rows)})
    finally:
        ledger.restore_own_door(run.stack, acct, f"{project_id[:8]}-restore-{run.stamp}", spec=STAND_IN_SPEC)
    retry_questions(run, leg, project_id)
