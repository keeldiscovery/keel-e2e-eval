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

**Spec 161** (keel-cloud 268-270, contract 87; keel-web 257 / 258): the founder's legs tell seven beats (the way and
the shortfall, the cost, the role's other tasks; the long beats closed by *That's it.*), read the board's seven rows and
the served verdict line, and pass the window page to the ready page with no belief page (the three PROBLEM beliefs
written at the boxes' yes). Where the keel-web checkout the stack serves does not yet carry 257 the story is told on the
wire as 257's page sends it (`story_screens.StoryWire`) and every screen check is named pending keel-web 257.

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
from harness import vectors_screens as vs_screens
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
                ("FR-1b", "the solution from nothing: the which-problem page, the problem's film and the opening, the "
                          "brand typed, four long beats, the board, the film in chapters, the verdict and the pilot "
                          "ask, the ready page (spec 162); a failed build walked once"),
                ("FR-1c", "the money from nothing: the pages, the orb moment, the persona pre-filled, one lock charge, "
                          "the link; then a money study with only a name, to the persona step"),
                ("FR-1d", "the defined problem project from the list: resumed, calibrated, refused on a drained grant, "
                          "locked once, a link sent"))
#: Spec 159 (keel-cloud 267, keel-web 253 / 254): the text view is the orb view -- a TEXT link is the AI player with
#: the orb in the face's place.
VIEWS = ("orb", "avatar", "copilot")
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
        #: Spec 158c: every conversation's turn as keel-web 249 makes it plain -- the hand-overs and the chime, the
        #: guide sheets met (the report's *The turn*).
        self.turns: list[dict] = []
        #: Spec 159: every orb (and face) link walked -- the stage's sequence, the orb's runs, how each question was
        #: answered, what was never to be drawn, the response (the report's *The orb*).
        self.orbs: list[dict] = []
        #: Spec 159 FR-2: each study's orb link as served (the same-words check reads it beside the avatar's).
        self.orb_wires: dict[str, dict] = {}

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

    def script_for(self, scope: str, *, consumed: int = 0, extra: dict | None = None) -> dict:
        base = vs.generate(self.base_entry(scope)).to_json()
        script = ss.story_runtime_script(base, self.readings, self.prevalence, STORY_WINDOW)
        for screen, entries in (extra or {}).items():
            # spec 161: the walk's own THEMES (chosen by dimension, before the base's catch-all) and EXPERIENCE_WAYS
            script[screen] = list(entries) + list(script.get(screen) or [])
        if consumed:
            # the chain's answer already applied on the project (at the story's or the idea's yes): a runtime started
            # again begins its cursor past it, so the founder's redrafts meet their own answers
            for screen in ("CALIBRATION_QUESTIONS", "CALIBRATION_QUESTIONS+repair"):
                entries = script.get(screen) or []
                if len(entries) > consumed:
                    script[screen] = entries[consumed:]
        return script

    def load_runtime(self, scope: str, *, consumed: int = 0, extra: dict | None = None) -> None:
        """The scripted runtime on `scope`'s script: written into the bundle, the runtime asked to go, and started again
        on it (it reconnects on the credential its home holds -- no code, no new door). `consumed`: the chain's answers
        the project already took (the scripted executor's cursor starts at 0 on every start). `extra` (spec 161): more
        entries by screen, put first -- the walk's THEMES and EXPERIENCE_WAYS -- always a fresh start."""
        key = f"{scope}:{consumed}" + (":extra" if extra else "")
        if not extra and self.runtime_scope in (scope, key) and not consumed:
            return
        if not extra and self.runtime_scope == key:
            return
        script = self.script_for(scope, consumed=consumed, extra=extra)
        (self.run_dir / "script.json").write_text(json.dumps(script, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        (self.run_dir / f"script-{scope.lower()}.json").write_text(json.dumps(script, indent=1, ensure_ascii=False)
                                                                   + "\n", encoding="utf-8")
        if self.runtime_scope is not None:
            stop_runtime(self.stack, self.recorder)
            start_runtime_via_skill(self.stack, self.recorder, env_extra={
                "KEEL_SCRIPT": str(self.run_dir / "script.json"), "KEEL_CONTEXT_KEYS": str(self.keys_path)})
        self.runtime_scope = key if (consumed or extra) else scope

    # ------------------------------------------------------------------------------------- set up
    def open(self, founder=None) -> None:
        """A fresh founder (a stub identity of this run), her own AI through the code story, the runtime on the
        problem's script; the founder's context carries the speech seam. Spec 166 FR-7 (`ONLY=solution`): `founder`, one
        already registered on this stack (a `StubFounder`), signs in again instead."""
        exported = contract_mod.export(self.stack.keel_cloud, self.run_dir / "export")
        # spec 161 FR-12: the contract the stack's keel-cloud serves, read on `x-keel-contract` (contract 87)
        self.contract_read = contract_version(self.stack.keel_cloud)
        self.registry = exported.registry
        self.keys_path = self.run_dir / "context-keys.json"
        self.keys_path.write_text(json.dumps(vs.context_keys_for(exported.context_keys), indent=2) + "\n",
                                  encoding="utf-8")
        label = f"{stack_remote.cell_name()} · e2e-157 · {time.strftime('%Y-%m-%d', time.gmtime())}"
        self.founder = founder or stack_remote.register_cell_identity(self.stack, label,
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


#: Spec 161 (keel-cloud 269 judgement call 20): the story's status after the boxes' yes -- `defined`, or on a PROBLEM study
#: `calibrating` / `calibrated` (the three beliefs written at the yes).
YES_STATUSES = ("defined", "calibrating", "calibrated")
#: Spec 161 FR-12: the HTTP contract the walk is written to -- keel-cloud 270's (the four questions, every why, the ways).
#: Spec 162 FR-11: keel-cloud 272's, **90** (271's founder's solution at 88, 273's pictures at 89, 272's three questions).
CONTRACT_161 = 87
CONTRACT = 90


def contract_version(keel_cloud) -> int | None:
    """`info.x-keel-contract` of the keel-cloud checkout the stack serves (`canon/openapi-v2.yaml`), or None."""
    import yaml                                                                 # noqa: PLC0415
    try:
        doc = yaml.safe_load((Path(keel_cloud) / "canon" / "openapi-v2.yaml").read_text(encoding="utf-8"))
        return int((doc.get("info") or {}).get("x-keel-contract"))
    except Exception:  # noqa: BLE001 - unread
        return None


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


def _names_a_prefix(rows: list[str], said: str | None) -> bool:
    """keel-cloud 263 / 268 FR-1: beat 3's readback names the limitations a row at a time within its forty words (the
    way's clause first since 268), so the rows it names are the first ones, at least one, and it stays under forty."""
    named = [r for r in rows if r not in _named(rows, said)]
    return bool(named) and rows[:len(named)] == named and len(str(said or "").split()) <= 40


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
    run.turns.append({"label": label, "chime": v, "sheets": ss.sheet_verdict(read.get("sheets") or [])})
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
    for t in run.turns[::-1]:
        if t["label"] == label:
            t["guide"] = {k: guide.get(k) for k in ("welcomeSeen", "openersSeen")}
            break
    leg.check(run, f"{label}: one film -- the stage opener alone on the conversation (one sheet at a time, no welcome "
                   f"sheet), and after it both seen (openersSeen has {stage}, welcomeSeen true)",
              v["one_film"] and stage in (guide.get("openersSeen") or []) and guide.get("welcomeSeen") is True,
              screen="the conversation's opening (guide-opener, guide-welcome)", view="founder + wire",
              detail={"sheets": v, "guide": {k: guide.get(k) for k in ("welcomeSeen", "openersSeen")},
                      "woke": woke.get("sheets") if isinstance(woke, dict) else woke}, stop=False)


#: Spec 161 FR-1: the founder's ways of telling beat 3 on the legs (one leg each): the script's words, the long telling,
#: the two parts across the quiet, the limitations alone (code's one ask walked).
TELLINGS = ("script", "long", "two-part", "limits-only")


def pending_web(run: Run, leg: Leg, spec: str, label: str, what: list[str], *, screen: str) -> None:
    """Spec 161 (the brief's rule): where the keel-web checkout the stack serves does not yet carry keel-web `spec`, the
    screen checks written to it are not run -- one failed check names them, `stop=False`, *pending keel-web {spec}*."""
    leg.check(run, f"{label}: pending keel-web {spec} -- the screen checks written to it not run: " + "; ".join(what),
              False, screen=screen, view="founder", detail={"pending": f"keel-web {spec}", "checks": what},
              stop=False)
    leg.notes.append(f"{label}: keel-web {spec} is not in the checkout -- told on the wire; {len(what)} screen checks "
                     f"pending keel-web {spec}")


#: The screen checks of the founder's story a keel-web before 257 cannot hold (spec 161 FR-1 to FR-3).
SCREEN_CHECKS_257 = ["the seven questions asked (`story-q`)", "no button but the orb on any beat",
                     "the long beats closed by *That's it.* and sent without it",
                     "beat 3 in two parts across 7 s of quiet, *Take your time.*",
                     "the board's seven rows lit in turn (`story-boxes`, the tasks row)",
                     "a correction on the tasks row redrawn", "the verdict line on `story-verdict`",
                     "the film held longer on the pain scene", "no belief page after the window page"]


def _beat3_words(run: Run, telling: str) -> tuple[str, list[str]]:
    """The words beat 3 is told with on a leg, and the rows (the limitations) a reading keeps."""
    if telling == "long":
        return ss.long_beat_3(run.readings)
    if telling == "two-part":
        first, second = ss.two_part_beat_3(run.readings)
        return f"{first} {second}", ss.limits_read(run.readings)
    if telling == "limits-only":
        return ss.limits_only_beat_3(run.readings), ss.limits_read(run.readings)
    return dict(ss.said_turns(run.readings))[3], ss.limits_read(run.readings)


def story_wire_checks(run: Run, leg: Leg, label: str, beats: dict, story: dict, *, telling: str,
                      rows: list[str], said: dict, view: str) -> None:
    """Spec 161 FR-1 on the wire (keel-cloud 268, contract 87): each beat read as keel-cloud 268 reads it -- beat 3's
    limitations (and its way, or the one ask where the words named none), beat 4's cost, beat 7's other tasks, beat 6
    owed only where beat 2 named no moment -- and the story's slots after the last beat."""
    def body(n: int) -> dict:
        b = beats.get(n) or {}
        return ((b.get("way") or b.get("put") or {}).get("body") or {})
    read3 = body(3).get("story") or {}
    want_way = telling == "limits-only" or ss.steps_read(run.readings)
    leg.check(run, f"{label}: beat 3 read into {len(rows)} limitations and today's way apart (keel-cloud 268 FR-1)",
              list(read3.get("limits") or [])[:len(rows)] == rows and (not want_way or bool(read3.get("steps"))
                                                                       or bool(read3.get("act"))),
              screen="define/story/3", view=view,
              detail={"limits": read3.get("limits"), "want": rows, "steps": read3.get("steps"), "act": read3.get("act"),
                      "readback": body(3).get("readback")}, stop=False)
    if telling == "limits-only":
        b3 = beats.get(3) or {}
        leg.check(run, f"{label}: the limitations alone -- code asks once, *{ss.WAY_ASK}*, on beat 3, and the next words "
                       "are read as the way (the limitations kept)",
                  b3.get("ask") == ss.WAY_ASK and bool((body(3).get("story") or {}).get("steps"))
                  and list(read3.get("limits") or [])[:len(rows)] == rows,
                  screen="define/story/3 (the way's ask)", view=view,
                  detail={"ask": b3.get("ask"), "way": ((b3.get("way") or {}).get("sent")), "story": {
                      k: read3.get(k) for k in ("steps", "act", "limits")}}, stop=False)
    if telling != "limits-only" and ss.heard_cost(run.readings) and telling == "script":
        leg.check(run, f"{label}: the cost heard on beat 3 is on the board before beat 4, and beat 4 is still asked "
                       "(keel-cloud 268 FR-2)", bool(read3.get("cost")) and 4 in beats,
                  screen="define/story/3 -> 4", view=view, detail={"cost after beat 3": read3.get("cost"),
                                                                   "beats": sorted(beats)}, stop=False)
    cost = ss.cost_read(run.readings)
    read4 = body(4).get("story") or {}
    leg.check(run, f"{label}: beat 4 asks the cost and reads it (*{cost}*)",
              4 in beats and (telling != "script" or _bare(read4.get("cost")) == _bare(cost)) and bool(read4.get("cost")),
              screen="define/story/4", view=view, detail={"cost": read4.get("cost"), "want": cost,
                                                          "readback": body(4).get("readback")}, stop=False)
    owed = ss.moment_beat(run.readings) == ss.WHEN_BEAT
    leg.check(run, f"{label}: beat 6 (*When does that come up?*) asked {'because beat 2 named no moment' if owed else 'never: beat 2 named the moment'}",
              (ss.WHEN_BEAT in beats) == owed, screen="define/story/6", view=view,
              detail={"beats": sorted(beats), "owed": owed}, stop=False)
    tasks = ss.other_tasks_read(run.readings)
    leg.check(run, f"{label}: beat 7 reads the role's other tasks ({len(tasks)} rows; keel-cloud 268 FR-3) and the "
                   "story is ready for the board (`next` check)",
              [_bare(t) for t in (body(7).get("story") or {}).get("otherTasks") or []] == [_bare(t) for t in tasks]
              and str((beats.get(7) or {}).get("next") or (body(7).get("next"))) in ("check", "8", "None"),
              screen="define/story/7", view=view,
              detail={"otherTasks": (body(7).get("story") or {}).get("otherTasks"), "want": tasks,
                      "next": (beats.get(7) or {}).get("next")}, stop=False)
    sent = {n: (((b.get("put") or {}).get("sent")) or {}).get("text") for n, b in beats.items()}
    leg.check(run, f"{label}: every beat's words sent whole and with no done word at their end (keel-web 257 FR-11)",
              all(not ss.ends_on_a_done_word(t) for t in sent.values() if t)
              and all(_bare(sent[n]) == _bare(said[n]) for n in said
                      if n in sent and not (n == 3 and telling == "limits-only")),
              screen="define/story/1..7", view=view,
              detail={n: (len(t or ""), (t or "")[-40:]) for n, t in sent.items()}, stop=False)


def board_checks(run: Run, leg: Leg, label: str, story: dict, *, view: str) -> None:
    """Spec 161 FR-1 on the wire: the board's rows as the story serves them (keel-cloud 268 FR-4) -- who, the job, the
    when, today's way, the limitations, the cost and the other tasks, each filled."""
    person = story.get("person") or {}
    filled = {"who": person.get("who"), "job": person.get("job"), "when": person.get("when"),
              "today": story.get("act") or story.get("steps"), "limits": story.get("limits"),
              "cost": story.get("cost"), "otherTasks": story.get("otherTasks")}
    leg.check(run, f"{label}: the story serves the board's seven rows -- who, job, when, today, falls short, costs, "
                   "other tasks (`StoryView.otherTasks` two to four)",
              all(bool(v) for v in filled.values()) and 2 <= len(story.get("otherTasks") or []) <= 4,
              screen="GET story (the board's rows)", view=view, detail=filled, stop=False)


def verdict_wire_checks(run: Run, leg: Leg, label: str, project_id: str, story: dict, *, view: str) -> dict:
    """Spec 161 FR-2 on the wire (keel-cloud 269 FR-6): after the boxes' yes the verdict line is served word for word,
    the three PROBLEM beliefs are written (Prevalence and Frequency `p_60_80`, Importance the own row then the other
    tasks), the review table reads them and is complete -- no belief page owed."""
    line = story.get("verdictLine")
    leg.check(run, f"{label}: `StoryView.verdictLine` served after the yes, word for word (*{ss.VERDICT_LINE[:60]}...*)",
              line == ss.VERDICT_LINE, screen="GET story (after the yes)", view=view,
              detail={"verdictLine": line}, stop=False)
    review = wait_review(run, project_id)
    read = vs_screens.written_beliefs(review)
    tasks = [_bare(t) for t in story.get("otherTasks") or []]
    leg.check(run, f"{label}: the review table's three rows read as written at the yes -- *6 or 7 in 10* on Prevalence, "
                   "the bin on Frequency, Importance the own row first then the other tasks; complete (no belief page "
                   "owed)", review.get("complete") is True and read["prevalence"] == ["p_60_80"]
              and read["frequency"] == ["p_60_80"] and len(read["importance"]) >= 3
              and [_bare(x) for x in read["importance"][1:]] == tasks and read["dimensions"] == 3,
              screen="review/PROBLEM", view=view,
              detail={"read": read, "complete": review.get("complete"), "counts": review.get("counts"),
                      "tasks": story.get("otherTasks")}, stop=False)
    return review


def wait_review(run: Run, project_id: str, *, timeout_s: float = 30) -> dict:
    deadline = time.monotonic() + timeout_s
    review: dict = {}
    while time.monotonic() < deadline:
        review = run.get(f"/v2/projects/{project_id}/review/PROBLEM") or {}
        if review.get("complete"):
            return review
        time.sleep(1)
    return review


def scenes_checks(run: Run, leg: Leg, label: str, drawn: dict, cost: str | None, *, view: str, where: str) -> None:
    """Spec 161 FR-3 (keel-cloud 268 FR-5): the film's seven scenes, the seventh the pain with its picture, `costLine`
    its line, eight clips."""
    v = ss.scenes_verdict(drawn, cost=cost)
    leg.check(run, f"{label}: the film's seven scenes -- the seventh alone `pain: true`, its line the cost with a picture, "
                   "`costLine` equal to it, eight clips", v["ok"], screen=where, view=view, detail=v, stop=False)


def keep_founder(run: Run, label: str, project_id: str, story: dict, *, wire: bool, beats: dict, telling: str,
                 heard: dict | None = None) -> None:
    """Spec 161 FR-12: what the report's *The founder's seven beats* keeps of one story -- the beats answered, the board's
    seven rows as served, the verdict line served (and heard on the screens), the film's scenes."""
    person = story.get("person") or {}
    run.__dict__.setdefault("founder_beats", []).append({
        "label": label, "project": project_id, "wire": wire, "telling": telling, "beats": sorted(beats),
        "board": {"who": person.get("who"), "job": person.get("job"), "when": person.get("when"),
                  "today": story.get("act") or story.get("steps"), "limits": story.get("limits"),
                  "cost": story.get("cost"), "otherTasks": story.get("otherTasks")},
        "verdictLine": story.get("verdictLine"), "verdict_heard": heard,
        "scenes": ss.scenes_verdict(((story.get("build") or {}).get("story")) or {}, cost=story.get("cost"))})


def tell_on_the_wire(run: Run, leg: Leg, project_id: str, label: str, *, telling: str = "script",
                     correction: str | None = None, tasks_fix: bool = False, back_to: str | None = None) -> dict:
    """Spec 161 with keel-web 257 not in the checkout: the founder's seven beats told on the wire (`StoryWire`), the
    board's rows and a correction read off the story, the boxes' yes, the build, the verdict line and the beliefs
    written -- every cloud read held -- and the screen checks pending keel-web 257 by name. The page is then taken where
    the story's yes would land: the window page (stored on the wire), or the return trip."""
    # the page before keel-web 257 is taken off the story's route first, so its own five-beat conversation can send
    # nothing while the seven are told on the wire (the browser's storage -- a waiting start -- is kept)
    run.page.goto("about:blank")
    wire = ss.StoryWire(run.call, project_id)
    told = list(ss.said_turns(run.readings))
    words3, rows = _beat3_words(run, telling)
    if telling == "long":
        told[0] = (1, told[0][1] + ss.LONG_WHO_SUFFIX)
    limits_only = (ss.limits_only_beat_3(run.readings), ss.way_answer(run.readings)) if telling == "limits-only" \
        else None
    seen = wire.tell(told, words3=words3 if telling in ("long", "two-part") else None, limits_only=limits_only)
    said = {n: (words3 if n == 3 else w) for n, w in told}
    beats = {s["turn"]: s for s in seen}
    run.beats.append({"label": f"{label} (on the wire)", "project": project_id, "beats": [
        {"turn": b["turn"], "asked": b["asked"], "put": b.get("way") or b["put"], "readback": {},
         "orb": [], "next": b.get("next")} for b in seen]})
    story = wire.story()
    story_wire_checks(run, leg, label, beats, story, telling=telling, rows=rows, said=said, view="wire")
    if correction:
        fixed = wire.correct(correction)
        after = (fixed.get("body") or {})
        leg.check(run, f"{label}: *{correction}* on the board is a story/correct that narrows the condition",
                  (fixed.get("status") or 500) < 400 and ss.CORRECTION_4_WORD in json.dumps(after.get("story") or {}),
                  screen="the board (story/correct)", view="wire",
                  detail={"status": fixed.get("status"), "changed": after.get("changed"),
                          "readback": after.get("readback")}, stop=False)
    if tasks_fix:
        fix = ss.tasks_correction(run.readings)
        if fix:
            fixed = wire.correct(fix[0])
            after = (fixed.get("body") or {})
            leg.check(run, f"{label}: a correction of the other tasks by voice (*{fix[0]}*) rewrites the tasks row "
                           "(`changed` names `otherTasks`; keel-cloud 268 FR-4)",
                      (fixed.get("status") or 500) < 400 and "otherTasks" in (after.get("changed") or [])
                      and [_bare(t) for t in (after.get("story") or {}).get("otherTasks") or []] == [_bare(t) for t in fix[1]],
                      screen="the board (story/correct, the tasks row)", view="wire",
                      detail={"status": fixed.get("status"), "changed": after.get("changed"),
                              "otherTasks": (after.get("story") or {}).get("otherTasks"), "want": fix[1]}, stop=False)
    story = wire.story()
    board_checks(run, leg, label, story, view="wire")
    confirmed = wire.confirm()
    leg.check(run, f"{label}: the boxes' yes (story/confirm 200; a PROBLEM study `calibrating` at its yes, the beliefs "
                   "written -- keel-cloud 269 judgement call 20 -- else defined)", confirmed["status"] == 200
              and (confirmed.get("body") or {}).get("status") in YES_STATUSES, screen="the board (the yes)", view="wire",
              detail={"status": confirmed["status"], "body": {k: (confirmed.get("body") or {}).get(k)
                                                              for k in ("status", "verdictLine")}})
    built = wire.built()
    drawn = (built.get("build") or {}).get("story") or {}
    leg.check(run, f"{label}: the build reaches ready, the check passed",
              (built.get("build") or {}).get("state") == "ready"
              and ((built.get("build") or {}).get("checked") or {}).get("pass") is True,
              screen="the build", view="wire", detail={k: (built.get("build") or {}).get(k) for k in ("state", "checked")})
    scenes_checks(run, leg, label, drawn, built.get("cost"), view="wire", where="GET story (the build's story)")
    verdict_wire_checks(run, leg, label, project_id, built, view="wire")
    pending_web(run, leg, "257", label, SCREEN_CHECKS_257, screen="define/story/* (keel-web 257)")
    keep_founder(run, label, project_id, wire.story(), wire=True, beats=beats, telling=telling)
    landed = None
    if back_to == "solution":
        landed = f"{run.web}/?start=solution&problem={project_id}"
    elif back_to == "money":
        landed = f"{run.web}/?start=money&problem={project_id}"
    if landed:
        run.page.goto(landed, wait_until="load")
    return {"walk": wire, "landed": landed or run.page.url, "story": built, "beats": beats, "wire": True}


def tell_the_story(run: Run, leg: Leg, project_id: str, label: str, *, telling: str = "script",
                   correction: str | None = None, tasks_fix: bool = False, back_to: str | None = None,
                   goto: bool = True) -> dict:
    """Spec 161 FR-1 to FR-3: one problem project told in seven beats -- on keel-web 257's screens where the checkout
    carries it (`tell_on_screen`), else on the wire with every screen check pending keel-web 257 by name
    (`tell_on_the_wire`). `telling`: beat 3 as the script says it, the long telling, in two parts across the quiet, or
    the limitations alone (code's one ask walked)."""
    if not ss.web_has_257(run.stack.keel_web):
        return tell_on_the_wire(run, leg, project_id, label, telling=telling, correction=correction,
                                tasks_fix=tasks_fix, back_to=back_to)
    return tell_on_screen(run, leg, project_id, label, telling=telling, correction=correction, tasks_fix=tasks_fix,
                          back_to=back_to, goto=goto)


def tell_on_screen(run: Run, leg: Leg, project_id: str, label: str, *, telling: str = "script",
                   correction: str | None = None, tasks_fix: bool = False, back_to: str | None = None,
                   goto: bool = True) -> dict:
    """keel-web 245 / 249 / 257 on one problem project, nothing pressed: the opening (the stage's opener passed, or the
    begin screen's orb; *Ready?*; the quiet), the seven beats said once each (the long beats closed by *That's it.*;
    beat 3 as `telling` says; `correction` after beat 5), the boxes (the board's seven rows; `tasks_fix` a correction of
    the tasks row by voice) by the quiet, the build, the story by the quiet, the verdict line heard. The checks: the
    questions verbatim, no button but the orb on any screen, the orb's states through each beat, the long beats' done
    word, beat 3's red crosses, beat 6 asked only where owed, the board, the build `ready`, the seven scenes, and where
    the quiet lands."""
    walk = ss.StoryWalk(run.page, run.recorder, run.web)
    opening = walk.open_start(project_id, goto=goto)
    woke = opening["woke"]
    leg.check(run, f"{label}: the opening -- the stage's opener passed by its Skip or the begin screen's orb tapped "
                   "(*Tap me to begin.*), then *Ready?* and the quiet open beat 1; no button but the orb",
              opening["landed"].rstrip("/").endswith("/define/story/1")
              and (woke["begin"] or "opener" in woke["sheets"]
                   or bool(ss.sheet_verdict(walk.sheets_of(project_id))["opener_on"]))
              and (opening["start"].get("question") == ss.STORY_READY) and not opening["start"].get("buttons")
              and not ((woke.get("begin_screen") or {}).get("buttons")),
              screen="define/story/start", detail=opening)
    told = list(ss.said_turns(run.readings))
    words3, rows = _beat3_words(run, telling)
    if telling == "long":
        told[0] = (1, told[0][1] + ss.LONG_WHO_SUFFIX)
    seen = walk.tell(told, long3=words3 if telling == "long" else None, correction=correction,
                     two_part=ss.two_part_beat_3(run.readings) if telling == "two-part" else None,
                     limits_only=(words3, ss.way_answer(run.readings)) if telling == "limits-only" else None)
    said = {n: (words3 if n == 3 else w) for n, w in told}
    beats = {s["turn"]: s for s in seen}
    run.beats.append({"label": label, "project": project_id, "beats": seen})
    # the questions, the buttons, the wire
    asked = {n: (b["asked"].get("question")) for n, b in beats.items()}
    leg.check(run, f"{label}: Keel asks each beat's question as keel-cloud 268 words it (keel-web 257 FR-1)",
              all(asked[n] == ss.STORY_QUESTIONS[n] for n in asked), screen="define/story/1..7", detail=asked)
    pressed = {n: sorted(set((b["asked"].get("buttons") or []) + ((b.get("readback") or {}).get("buttons") or [])
                             + ((b.get("corrected") or {}).get("buttons") or []))) for n, b in beats.items()}
    leg.check(run, f"{label}: no button on any beat but the orb (no Tap to talk, Type instead, Send, That is all, Yes)",
              not any(pressed.values()), screen="define/story/1..7", detail=pressed)
    small = {n: {k: b["asked"].get(k) for k in ("orbs", "orbSize", "glow", "line")} for n, b in beats.items()}
    leg.check(run, f"{label}: the small orb on every beat (one, at most 44 px), its state line beside it, no glow "
                   "(keel-web 249 FR-1)",
              all(v["orbs"] == 1 and (v["orbSize"] or 99) <= 44 and v["line"] and not v["glow"] for v in small.values()),
              screen="define/story/1..7 (story-orb, story-state)", detail=small, stop=False)
    answers = [w for w in walk.writes if re.search(r"/story/turns/\d$", w["path"]) and (w["sent"] or {}).get("text")
               and not (w["sent"] or {}).get("correction")]
    by_beat: dict[int, list[str]] = {}
    for w in answers:
        by_beat.setdefault(int(w["path"].rsplit("/", 1)[-1]), []).append((w["sent"] or {}).get("text") or "")
    whole = all(_bare(" ".join(by_beat.get(n) or [])) == _bare(said[n] if not (n == 3 and telling == "limits-only")
                                                                  else f"{said[3]} {ss.way_answer(run.readings)}")
                for n in beats)
    leg.check(run, f"{label}: every beat sent as said, the words whole, every answer 200",
              whole and all((w["status"] or 0) < 400 for w in walk.writes if "/story/turns/" in w["path"]),
              screen="define/story/1..7", detail=[(w["path"].split("/story/")[-1], w["status"],
                                                   len(((w["sent"] or {}).get("text")) or ""), (w["sent"] or {}).get("done"),
                                                   (w["sent"] or {}).get("correction")) for w in walk.writes
                                                  if "/story/turns/" in w["path"]])
    long_beats = {n: b for n, b in beats.items() if n in ss.LONG_BEATS}
    done_words = {n: [t[-30:] for t in by_beat.get(n) or [] if ss.ends_on_a_done_word(t)] for n in long_beats}
    closed_by = {n: (b.get("closed") or {}).get("by") for n, b in long_beats.items()}
    leg.check(run, f"{label}: the long beats (3, 4, 7) closed by *{ss.DONE_WORD}* said as their last words, never by the "
                   "quiet, and the words sent carry no done word (keel-web 257 FR-11)",
              not any(done_words.values()) and closed_by.get(3) != "the quiet" and set(long_beats) == set(ss.LONG_BEATS),
              screen="define/story/3, 4, 7", detail={"done words sent": done_words, "closed by": closed_by,
                                                      "subs": {n: (b["asked"].get("sub")) for n, b in long_beats.items()}},
              stop=False)
    if telling == "two-part":
        q = (beats.get(3) or {}).get("two_part") or {}
        leg.check(run, f"{label}: beat 3 in two parts across {ss.TWO_PART_QUIET_S:g} s of quiet -- nothing sent in the "
                       f"quiet, the beat still open, the state line *{ss.THINK_LINE}*, the second part joined to the "
                       "first, *That's it.* closing it (keel-web 257 FR-11)",
                  q.get("sent_in_the_quiet") == 0 and q.get("still_on_the_beat") and q.get("think_line")
                  and q.get("joined"), screen="define/story/3 (the quiet)", detail=q, stop=False)
    transcribed = [((w.get("body") or {}).get("text")) for w in walk.writes if w["path"].endswith("/story/transcribe")]
    heard_all = " ".join(_bare(t) for t in transcribed if t)
    leg.check(run, f"{label}: every answer written down through story/transcribe, heard as said (the fake: the words "
                   "in, the same words out)", all(_bare(said[n])[:200] in heard_all for n in beats
                                                  if not (n == 3 and telling in ("two-part",))),
              screen="define/story/1..7", detail={"heard": [t[:120] if t else t for t in transcribed]}, stop=False)
    orbs = {n: b.get("orb") for n, b in beats.items()}
    leg.check(run, f"{label}: the orb through every beat -- speaking (the question), listening, hearing, writing, "
                   "speaking (Keel's next line), and from writing straight to speaking",
              all(ss.holds_in_order(o or [], ss.BEAT_ORB) and ss.writing_then_speaking(o or []) for o in orbs.values()),
              screen="define/story/1..7 (story-orb data-state)", detail=orbs, stop=False)
    story_now = run.get(f"/v2/projects/{project_id}/story") or {}
    story_wire_checks(run, leg, label, beats, story_now, telling=telling, rows=rows, said=said, view="founder + wire")
    # beat 3: every limitation, broken out, named back
    b3 = beats.get(3) or {}
    read3 = (((b3.get("way") or b3.get("put") or {}).get("body") or {}))
    limits = list((read3.get("story") or {}).get("limits") or [])
    crosses = list((b3.get("readback") or {}).get("limits") or [])
    leg.check(run, f"{label}: beat 3's answer read into {len(rows)} red crosses (`story-card-limit`), the readback naming "
                   "each, the done word closing the list (next 4)",
              limits == rows and (not crosses or crosses == rows) and _names_a_prefix(rows, read3.get("readback"))
              and str((b3.get("closed") or {}).get("next") or b3.get("next")) == "4",
              screen="define/story/3", detail={"limits": limits, "crosses": crosses, "want": rows,
                                               "readback": read3.get("readback"), "closed": b3.get("closed"),
                                               "next": b3.get("next")}, stop=False)
    if telling == "long" and not run.remote:
        kept = ledger.story_turns(run.stack, project_id)
        leg.check(run, "the story keeps beat 3's words whole (project_story's turn 3: every character, nothing cut)",
                  _norm_words(kept.get(3)) == _norm_words(said[3]), screen="the stored story (no route serves the words)",
                  view="wire", detail={"stored": len(kept.get(3) or ""), "said": len(said[3]),
                                       "ends": (kept.get(3) or "")[-80:]}, stop=False)
    b5 = beats.get(ss.ALL_OF_THEM_BEAT) or {}
    read5 = ((b5.get("put") or {}).get("body") or {})
    sentence = ((read5.get("story") or {}).get("person") or {}).get("sentence")
    leg.check(run, f"{label}: beat 5's reading is the sentence, its readback the sentence then *Right?*",
              bool(sentence) and read5.get("readback") == f"{sentence.strip()} Right?", screen="define/story/5",
              detail={"readback": read5.get("readback"), "sentence": sentence}, stop=False)
    # the boxes, by the quiet (a correction of the condition deferred from beat 5, or of the tasks row)
    fix = ss.tasks_correction(run.readings) if tasks_fix else None
    # the board as drawn before any correction: its rows are the story's as the beats left it
    story_before = run.get(f"/v2/projects/{project_id}/story") or {}
    boxes = walk.boxes(correction=fix[0] if fix else None)
    card = boxes["screen"].get("card") or {}
    want_rows = {"person": (story_before.get("person") or {}).get("who"), "limits": rows,
                 "tasks": list(story_before.get("otherTasks") or [])}
    board = ss.board_rows_verdict(card, want_rows)
    leg.check(run, f"{label}: the board -- *What Keel understood* read by `data-box`: who, job, when, today, falls short, "
                   "costs, other tasks (`tasks` last, keel-web 257 FR-3); *Is that right?*; no button; the quiet confirms "
                   "(story/confirm 200, defined)",
              boxes["confirm"]["status"] == 200 and (boxes["confirm"]["body"] or {}).get("status") in YES_STATUSES
              and boxes["screen"].get("said") == ss.BOXES_ASK and not boxes["screen"].get("buttons")
              and card.get("label") == ss.CARD_LABEL and board["ok"],
              screen="define/story/check (boxes)",
              detail={"board": board, "rows": ss.card_rows(card), "said": boxes["screen"].get("said"),
                      "lit": boxes.get("lit"), "buttons": boxes["screen"].get("buttons"),
                      "confirm": boxes["confirm"]["status"]}, stop=False)
    lit = [set(str(x).split(",")) for x in boxes.get("lit") or []]
    leg.check(run, f"{label}: Keel narrates the board row by row, the tasks row last (`data-lit`)",
              bool(lit) and all(x <= set(ss.CARD_ROWS) for x in lit) and any("tasks" in x for x in lit),
              screen="define/story/check (boxes)", detail={"lit": boxes.get("lit")}, stop=False)
    if fix:
        fixed = boxes.get("correction") or {}
        body = fixed.get("body") or {}
        redrawn = ss.card_rows(((boxes.get("corrected") or {}).get("card")) or {})
        leg.check(run, f"{label}: *{fix[0]}* said on the board is a story/correct of the tasks row -- `changed` names "
                       "`otherTasks` and the tasks row is redrawn with the new list",
                  (fixed.get("status") or 500) < 400 and "otherTasks" in (body.get("changed") or [])
                  and all(_bare(t) in _bare(redrawn.get("tasks")) for t in fix[1]),
                  screen="define/story/check (the tasks row corrected)",
                  detail={"sent": fixed.get("sent"), "changed": body.get("changed"), "tasks row": redrawn.get("tasks"),
                          "want": fix[1]}, stop=False)
    elif correction:
        stored = ((run.get(f"/v2/projects/{project_id}/story") or {}).get("person") or {}).get("onlyThoseWho") or ""
        leg.check(run, f"{label}: *{correction}* narrows the condition, said after beat 5 or on the board",
                  ss.CORRECTION_4_WORD in stored, screen="define/story/5 -> check", view="wire",
                  detail={"stored": stored, "deferred": walk.deferred_correction}, stop=False)
    turn_screen(run, leg, label, boxes["screen"], "define/story/check (boxes)", card=True)
    built = walk.building_then_story()
    if built["state"] == "story":
        turn_screen(run, leg, label, built.get("story") or {}, "define/story/check (story)")
        measure_fit(run, leg, run.page, label, FOUNDER_PLAYER, where="define/story/check (story)",
                    view="founder · desktop", phone=False, state=FOUNDER_STATE)
    story = run.get(f"/v2/projects/{project_id}/story") or {}
    build = story.get("build") or {}
    drawn = build.get("story") or {}
    leg.check(run, f"{label}: the build reaches ready, the check passed, the story drawn; no button",
              built["state"] == "story" and build.get("state") == "ready" and (build.get("checked") or {}).get("pass")
              is True and not (built.get("story") or {}).get("buttons") and not ((built.get("building") or {}).get("buttons")),
              screen="define/story/check (building, story)",
              detail={"screen": built.get("state"), "build": {k: build.get(k) for k in ("state", "checked")},
                      "room": drawn.get("roomId"), "scenes": len(drawn.get("scenes") or [])})
    scenes_checks(run, leg, label, drawn, story.get("cost"), view="wire", where="define/story/check (story)")
    lands = {"solution": r"/\?start=solution", "money": r"/\?start=money"}.get(back_to or "", r"/define/context")
    yes = walk.story_yes(lands=re.compile(lands), verdict=True)
    heard_verdict = yes.get("verdict") or {}
    leg.check(run, f"{label}: after the film's yes Keel says the verdict line on its card (`story-verdict`), word for "
                   "word the served `verdictLine`, then *Say yes, or just tell me if you want a different bar.*; the "
                   "quiet goes on (keel-web 257 FR-4)",
              heard_verdict.get("drawn") is True and _bare(story.get("verdictLine") or ss.VERDICT_LINE)
              in _bare(heard_verdict.get("words"))
              and any(ss.VERDICT_ASK in x for x in heard_verdict.get("said") or []),
              screen="define/story/check (the verdict)", detail={"heard": heard_verdict,
                                                                 "verdictLine": story.get("verdictLine")}, stop=False)
    verdict_wire_checks(run, leg, label, project_id, story, view="wire")
    keep_founder(run, label, project_id, run.get(f"/v2/projects/{project_id}/story") or story, wire=False, beats=beats,
                 telling=telling, heard=heard_verdict)
    if back_to == "solution":
        said_then = [yes.get("said")] + list((yes.get("verdict") or {}).get("said") or [])
        leg.check(run, f"{label}: the quiet after the verdict goes back to the solution (the which-problem page, the "
                       "problem picked)", "start=solution" in str(yes.get("landed") or "")
                  and (yes.get("said") in (ss.BACK_TO_SOLUTION, ss.STORY_ASK) or (yes.get("verdict") or {}).get("drawn")),
                  screen="define/story/check (story)", detail={"yes": yes, "said": said_then}, stop=False)
    read = walk.turn_read()
    hand_over_checks(run, leg, label, read, "define/story/*", beat_path=r"/define/story/\d$")
    heard = ss.heard_verdict(read["heard"], said, lambda n: f"/define/story/{n}")
    leg.check(run, f"{label}: each beat's words shown as heard -- in *What I hear* (`story-heard`) on the beat's screen, "
                   "in quotation marks -- and never among Keel's lines (`story-words` Keel's alone; keel-web 249 FR-4)",
              heard["all_shown"] and heard["words_keels_only"] and heard["quoted"],
              screen="define/story/1..7 (story-heard, story-words)", detail=heard, stop=False)
    one_film(run, leg, label, project_id, walk.sheets_of(project_id), "PROBLEM", woke)
    walk.stop_listening()
    return {"walk": walk, "landed": yes["landed"], "story": story, "beats": beats}


#: Spec 161 FR-2 (keel-web 257 FR-5): where the window page's forward press lands on a spoken PROBLEM project -- the
#: ready page (the PROBLEM study's next stage), never a belief page.
READY_PATH = re.compile(r"/define/ready")
BELIEF_PATH = re.compile(r"/define/problem/(q/\d|seed)")


def window_then_ready(run: Run, leg: Leg, project_id: str, label: str, *, wire: bool = False) -> dict:
    """Spec 161 FR-2 after the story's yes and the verdict: 244's window screen -- a page, no orb on it -- a window
    chosen and stored (`PUT context/window`), then the ready page: **no belief page is drawn** on a spoken PROBLEM
    project (keel-web 257 FR-5, keel-cloud 269 FR-6: the beliefs were written at the boxes' yes). `wire` (keel-web 257
    not in the checkout): the window stored on the wire and the corridor read off the calibration alone."""
    if wire:
        stored = ss.StoryWire(run.call, project_id).window(STORY_WINDOW)
        leg.check(run, f"{label}: the window stored (PUT context/window 200, on the wire)", stored["status"] == 200,
                  screen="define/context/window", view="wire", detail={"status": stored["status"]})
        calibration = wait_calibration(run, project_id, "PROBLEM")
        leg.check(run, f"{label}: the PROBLEM calibration answered at the yes -- the three questions served answered, "
                       "none owed (no belief page to walk; `CalibrationView.total` 3)",
                  vs_screens.calibration_answered(calibration), screen="calibration/PROBLEM", view="wire",
                  detail={"state": calibration.get("state"), "total": calibration.get("total"),
                          "answered": [q.get("dimension") for q in calibration.get("questions") or []
                                       if q.get("answer")]}, stop=False)
        return {"calibration": calibration, "landed": None}
    page = run.page
    page.wait_for_timeout(1500)
    url = page.url
    window_page = "/define/context/window" in url and page.locator("[data-testid=context-window-page]").count() > 0 \
        and page.locator("[data-testid=context-window-page]").first.is_visible()
    leg.check(run, f"{label}: the verdict's quiet opens 244's window screen -- a page, no orb on it", window_page
              and page.locator(ss.ORB).count() == 0, screen="define/context/window",
              detail={"url": url, "window page": window_page, "orb": page.locator(ss.ORB).count()}, stop=False)
    shot = ss._BrowserStep(run.recorder, page, "founder")
    stored = None
    seen: list[str] = []
    with run.recorder.step(f"{label}: the window chosen, then on to the ready page", party="founder") as h:
        if window_page:
            page.locator("button.cwindow__chip").first.click()
            with page.expect_response(lambda r: r.request.method == "PUT" and r.url.split("?")[0]
                                      .endswith("/context/window"), timeout=30_000) as got:
                page.get_by_role("button", name=re.compile(r"save and continue", re.I)).first.click()
            stored = {"status": got.value.status, "sent": got.value.request.post_data_json}
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not READY_PATH.search(page.url):
            if page.url not in seen:
                seen.append(page.url)
            page.wait_for_timeout(250)
        page.wait_for_timeout(1000)
        landed = page.url
        h.add_screenshot(shot.screenshot(f"after-the-window-{label}"))
    if window_page:
        leg.check(run, f"{label}: the window stored (PUT context/window 200)", (stored or {}).get("status") == 200,
                  screen="define/context/window", view="wire", detail=stored)
    leg.check(run, f"{label}: the window's forward press goes on to the ready page -- no belief page drawn on a spoken "
                   "PROBLEM project (keel-web 257 FR-5)", bool(READY_PATH.search(landed))
              and not any(BELIEF_PATH.search(u) for u in seen + [landed]), screen="define/context -> define/ready",
              detail={"landed": landed, "seen": seen}, stop=False)
    calibration = wait_calibration(run, project_id, "PROBLEM")
    return {"calibration": calibration, "landed": landed}


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

#: FR-1 (a)'s two problem projects: the script's own words (spec 161: the tasks row corrected on the board), and the
#: long telling with the condition's correction (spec 158 FR-1).
FR1A_TOLD = (("a-script", "the script's words", "script"), ("a-long", "the long telling", "long"))
#: Spec 161 FR-1: how beat 3 is told on the problems FR-1 (b) and (c) start -- in two parts across the quiet on the
#: solution's, the limitations alone (code's one ask walked) on the money's.
FR1B_TELLING = "two-part"
FR1C_TELLING = "limits-only"


def fr1_a(run: Run, leg: Leg) -> None:
    """Two problem projects by voice, to the ready page (spec 161: seven beats, the board's seven rows, the verdict line,
    no belief page): one told in the script's own words (every reading scripted, the cost heard on beat 3 and asked
    again on beat 4, the tasks row corrected on the board), one told the long way (beat 3 over 1,500 characters -- the
    way, five limitations and a cost in one breath, read by the cloud's echo; *only the ones in Europe* after beat 5)."""
    wire = not ss.web_has_257(run.stack.keel_web)
    leg.check(run, f"the stack's keel-cloud serves contract {CONTRACT} (`x-keel-contract`; keel-cloud 268-273)",
              run.__dict__.get("contract_read") == CONTRACT, screen="canon/openapi-v2.yaml", view="wire",
              detail={"x-keel-contract": run.__dict__.get("contract_read")}, stop=False)
    if wire:
        leg.notes.append("keel-web 257 is not in the keel-web checkout the stack serves: every story is told on the wire "
                         "(the cloud's reads held) and the founder's screen checks are pending keel-web 257, by name")
    for key, label, telling in FR1A_TOLD:
        name = f"161 problem {telling} {run.stamp}"
        run.new_project(name, "PROBLEM")
        # spec 158c FR-8: the guide sheet is held, not pressed past by the market step -- on a new problem project it is
        # the stage opener on the story route (keel-web 249 FR-6), which the walk itself passes and reads
        pid = MarketStep(run.page, run.recorder, run.web).start(welcome="hold")
        run.projects[key] = pid
        run.names[key] = name
        run.page.wait_for_timeout(1500)
        leg.check(run, f"{label}: a new problem project opens on its conversation", "/define" in run.page.url,
                  screen="/p/{id}", detail=run.page.url, stop=False)
        tell_the_story(run, leg, pid, label, telling=telling,
                       correction=ss.CORRECTION_4 if telling == "long" else None, tasks_fix=telling == "script")
        window_then_ready(run, leg, pid, label, wire=wire)
        if not wire:
            phone_story(run, leg, pid, label)
    review = run.get(f"/v2/projects/{run.projects['a-script']}/review/PROBLEM") or {}
    want = ss.reading_of(run.readings, max(n for n, _ in ss.said_turns(run.readings))).get("statement")
    leg.check(run, "the statement is the last beat's reading's (keel-cloud 263 judgement call 4: drafted on the beats)",
              review.get("statement") == want, screen="review/PROBLEM", view="wire",
              detail={"statement": review.get("statement"), "want": want}, stop=False)


# ------------------------------------------------------------------------------------------------ FR-1 (b)

#: Spec 162 FR-1 (keel-cloud 271 FR-13's special scripts): how each solution leg tells its four beats -- FR-1b's solution
#: beat 1 with advantages alone (code's ask), beat 2 with two rows, beat 3 in two parts across the quiet with one
#: limitation left unmatched and corrected to a cross, beat 4 a feature first (code's ask); the money's solution (FR-1c)
#: beat 1 with its steps, beat 2 with none, beat 3 corrected to a match, beat 4 the joy at once; the failed build's
#: (FR-3) the plainest telling.
IDEA_TELLINGS = ("asks", "plain", "failed")


def idea_plan(run: Run, telling: str) -> dict[int, dict]:
    """The four beats' words for one of `IDEA_TELLINGS`, every word the cloud's fake script's (`ss.idea_scripts`)."""
    s = ss.idea_scripts(run.readings)
    limits = s["limits"]
    if telling == "asks":
        cut = limits.find("That is the first one.") + len("That is the first one.")
        return {1: {"words": s["advantages_only"], "then": [s["first_step"]]},
                2: {"words": s["setup"]},
                3: {"words": limits, "two_part": (limits[:cut].strip(), limits[cut:].strip()), "then": [s["cross"]]},
                4: {"words": s["features"][0], "then": [s["joy"]]}}
    if telling == "plain":
        return {1: {"words": s["workflow"]}, 2: {"words": s["setup_none"]}, 3: {"words": limits, "then": [s["match"]]},
                4: {"words": s["joy"]}}
    return {1: {"words": s["workflow"]}, 2: {"words": s["setup"]}, 3: {"words": limits, "then": [s["cross"]]},
            4: {"words": s["joy"]}}


def _sent(answer: dict) -> str:
    return str((answer.get("sent") or {}).get("text") or "")


def idea_beats_checks(run: Run, leg: Leg, label: str, beats: dict, plan: dict, story: dict, idea: dict,
                      *, name: str) -> None:
    """Spec 162 FR-1 on the four beats: the questions 271's (filled from the brand and the story), every beat closed by
    the done word (never the quiet) and sent without it, the asks and the cross as code words them, the two parts."""
    limits = list(story.get("limits") or [])
    rows_q = {n: (b.get("question") or "") for n, b in beats.items()}
    templates = {n: re.compile("^" + re.escape(ss.IDEA_QUESTIONS[n]).replace(re.escape("{name}"), re.escape(name))
                               .replace(re.escape("{role}"), ".+?").replace(re.escape("{task}"), ".+?")
                               .replace(re.escape("{n}"), r"\w+").replace(re.escape("{the limitations}"), ".+?")
                               .replace(re.escape("{the pain}"), ".+?") + "$") for n in ss.IDEA_BEATS}
    exact3 = ss.idea_question(3, name=name, limits=limits)
    leg.check(run, f"{label}: Keel asks the four beats in keel-cloud 271's words, the brand's name in them (beat 3 "
                   "word for word: the limitations counted and named)",
              all(templates[n].match(_norm_words(rows_q.get(n))) for n in ss.IDEA_BEATS)
              and _norm_words(rows_q.get(3)) == exact3, screen="define/idea/1..4 (story-q)",
              detail={"asked": rows_q, "beat 3 want": exact3}, stop=False)
    sent = {n: [_sent(a) for a in b["answers"]] for n, b in beats.items()}
    closed = {n: [a.get("done") for a in b["answers"]] for n, b in beats.items()}
    leg.check(run, f"{label}: every beat a long beat -- closed by *That's it.* said as the last words, never by the "
                   "quiet; each answer sent whole and without the done word; the last answer of each closes it "
                   "(`done: true`)",
              all(closed[n] and closed[n][-1] is True and all(x is not True for x in closed[n][:-1])
                  for n in ss.IDEA_BEATS)
              and all(t and not ss.ends_on_a_done_word(t) for ts_ in sent.values() for t in ts_),
              screen="define/idea/1..4", detail={"sent": {n: [t[:80] for t in v] for n, v in sent.items()},
                                                 "done": closed}, stop=False)
    want_sent = {n: [plan[n]["words"]] + list(plan[n].get("then") or []) for n in ss.IDEA_BEATS}
    leg.check(run, f"{label}: the words heard are the words said, beat by beat (the fake transcriber)",
              all([_bare(t) for t in sent[n]] == [_bare(t) for t in want_sent[n]] for n in ss.IDEA_BEATS),
              screen="define/idea/1..4", view="founder + wire",
              detail={n: {"sent": [t[:60] for t in sent[n]], "said": [t[:60] for t in want_sent[n]]}
                      for n in ss.IDEA_BEATS}, stop=False)
    asks = {n: [a.get("ask") for a in b["answers"] if a.get("ask")] for n, b in beats.items()}
    readbacks = {n: [a.get("readback") for a in b["answers"]] for n, b in beats.items()}
    unmatched = [a.get("limit") for a in (idea.get("limitAnswers") or []) if not a.get("solved")]
    s = ss.idea_scripts(run.readings)
    if plan[1].get("then"):
        leg.check(run, f"{label}: beat 1 answered with advantages alone -- code's one ask (*{ss.STEP_ASK}*) said, the "
                       "steps answered after it; the workflow read with who does each step",
                  asks[1] == [ss.STEP_ASK] and len(idea.get("workflow") or []) >= 1
                  and all(w.get("by") in ("PERSON", "PRODUCT") for w in idea.get("workflow") or []),
                  screen="define/idea/1 (the ask)", view="founder + wire",
                  detail={"asks": asks[1], "workflow": idea.get("workflow")}, stop=False)
    if len(beats[3]["answers"]) > 1:
        first = beats[3]["answers"][0]
        crossed = plan[3]["then"][0] == s["cross"]
        held = [a.get("limit") for a in (idea.get("limitAnswers") or []) if not a.get("solved")]
        want_ask = ss.unmatched_line(ss.UNMATCHED_ASK, [limits[i] for i, a in enumerate(
            ss.idea_reading_of(run.readings, 3, plan[3]["words"]).get("limit_answers") or []) if not a.get("solved")])
        last = readbacks[3][-1] or ""
        leg.check(run, f"{label}: beat 3 -- one limitation left unmatched: the readback asks *{want_ask}* (`done: "
                       "false`), the next words sent as its correction (`correction: true`), then "
                       + ("the cross said (*I will show ... as not solved.*), the limitation crossed on the board"
                          if crossed else "every limitation matched"),
                  first.get("done") is False and want_ask in str(first.get("readback") or "")
                  and (beats[3]["answers"][1].get("sent") or {}).get("correction") is True
                  and ((ss.unmatched_line(ss.NOT_SOLVED, held) in last and bool(held)) if crossed else not held),
                  screen="define/idea/3 (the ask, the correction)", view="founder + wire",
                  detail={"readbacks": readbacks[3], "want ask": want_ask, "unmatched": unmatched}, stop=False)
    if plan[4].get("then"):
        leg.check(run, f"{label}: beat 4 answered with a feature -- code's one ask (*{ss.FEATURE_ASK}*), then the joy; "
                       "the joy read, not a feature", asks[4] == [ss.FEATURE_ASK] and bool(idea.get("joy"))
                  and idea.get("joyIsFeature") is False, screen="define/idea/4 (the ask)", view="founder + wire",
                  detail={"asks": asks[4], "joy": idea.get("joy")}, stop=False)
    if plan[3].get("two_part"):
        q = beats[3].get("two_part") or {}
        leg.check(run, f"{label}: beat 3 in two parts across {ss.TWO_PART_QUIET_S:.0f} s of quiet -- nothing sent in the "
                       f"quiet, the beat still open, *{ss.THINK_LINE}*; the two parts sent as one answer",
                  q.get("sent_in_the_quiet") == 0 and q.get("still_on_the_beat") and q.get("think_line")
                  and q.get("joined"), screen="define/idea/3 (the quiet)", detail=q, stop=False)
    if plan[2]["words"] == s["setup_none"]:
        leg.check(run, f"{label}: beat 2 -- none to set up: *{ss.NOTHING_TO_SET_UP}* read back, `setupNone`",
                  readbacks[2][-1] == ss.NOTHING_TO_SET_UP and idea.get("setupNone") is True and not idea.get("setup"),
                  screen="define/idea/2", view="founder + wire", detail={"readback": readbacks[2]}, stop=False)
    else:
        leg.check(run, f"{label}: beat 2 -- the setup's rows read back (*Before they can start: ...*)",
                  str(readbacks[2][-1] or "").startswith("Before they can start: ") and bool(idea.get("setup")),
                  screen="define/idea/2", view="founder + wire", detail={"readback": readbacks[2],
                                                                         "setup": idea.get("setup")}, stop=False)
    leg.check(run, f"{label}: no button on any beat but the orb", all(
        not (b.get("asked") or {}).get("buttons") for b in beats.values()), screen="define/idea/1..4",
        detail={n: (b.get("asked") or {}).get("buttons") for n, b in beats.items()}, stop=False)


def idea_leg(run: Run, leg: Leg, solution: str, label: str, *, telling: str = "plain", back_to_money: bool = False,
             before_yes: Callable[[], None] | None = None, name: str = ss.IDEA_NAME,
             tagline: str = ss.IDEA_TAGLINE) -> dict:
    """Spec 162 FR-1 to FR-3 (keel-web 259 on keel-cloud 271 / 273): the problem's film then the opening, the brand
    typed, the four long beats (`telling`: `IDEA_TELLINGS`), the board's six rows by the quiet, the build, the plate and
    the film in its chapters, then -- on a solution -- the verdict line, the pilot ask answered yes and the ready page;
    on a money start's solution the quiet goes back to the money start."""
    idea = ss.IdeaWalk(run.page, run.recorder, run.web)
    problem = run.get(f"/v2/projects/{solution}/story") or {}
    opened = idea.film_then_opening(solution)
    people = ((problem.get("person") or {}).get("who")) or ""
    brand = idea.brand_page(name=name, tagline=tagline)
    # the idea is served once its brand is saved (before it `GET idea/spoken` is a 404: keel-web 259 judgement call 2)
    view0 = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    leg.check(run, f"{label}: the problem's film plays through the one player, then Keel says the opening (*Now we know "
                   f"what {people} are trying to do ...*, the served `opening`), then `story/confirm` stamped with no "
                   "words -- no board, no *still the problem*; the brand page opens",
              opened["film"] and opened["said"] == ss.idea_opening(people)
              and (not view0.get("opening") or opened["said"] == view0.get("opening"))
              and opened["confirm"]["status"] == 200 and not opened["confirm"]["sent"] and not opened["board"]
              and not opened["still"], screen="define/idea/start",
              detail={"said": opened["said"], "served": view0.get("opening"), "film": opened["film"],
                      "confirm": opened["confirm"]["status"], "sent": opened["confirm"]["sent"],
                      "board": opened["board"], "still": opened["still"], "woke": opened.get("woke")})
    sent = brand["put"]["sent"] or {}
    leg.check(run, f"{label}: the brand page -- a page, no orb; the name, a colour and the tagline typed; the logo line "
                   "read word for word; a non-square PNG refused on the spot with that same line, nothing uploaded; "
                   "*Continue* sends `PUT idea/brand {name, colour, tagline}` and beat 1 opens",
              brand["orb"] == 0 and brand["line"] == ss.LOGO_LINE and brand["fault"] == ss.LOGO_LINE
              and not brand["uploads"] and brand["put"]["status"] == 200 and sent.get("name") == name
              and sent.get("tagline") == tagline and str(sent.get("colour") or "").lower() == ss.IDEA_COLOUR,
              screen="define/idea/brand", detail={k: brand.get(k) for k in ("orb", "line", "fault", "uploads", "count",
                                                                              "preview")} | {"put": brand["put"]})
    plan = idea_plan(run, telling)
    beats = idea.beats(plan)
    run.beats.append({"label": f"{label} (the solution's four beats)", "project": solution,
                      "beats": list(beats.values()), "idea": True})
    view = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    idea_beats_checks(run, leg, label, beats, plan, problem, view, name=name)
    board = idea.boxes()
    verdict = ss.board_six_verdict(board["card"], view, name=name, tagline=tagline)
    leg.check(run, f"{label}: the board -- six rows by `data-box` in order (the product with the tagline, *With it*, "
                   "*Before that*, *What it does*, *In the way* with its ticks and crosses, *What they get*), each "
                   "holding the idea's words; *Is that your idea?*; no button; the quiet confirms (idea/confirm 200)",
              verdict["ok"] and board["said"] == ss.IDEA_BOXES_ASK and board["confirm"]["status"] == 200
              and not (board["screen"] or {}).get("buttons"), screen="define/idea/check (the board)",
              detail={"verdict": verdict, "said": board["said"], "confirm": board["confirm"]["status"],
                      "rows": ss.card_rows(board["card"])}, stop=False)
    lit = [x for x in board["lit"] if x and "," not in x]
    leg.check(run, f"{label}: Keel names the six rows in the board's order, each lit as named",
              [k for k in dict.fromkeys(lit)][:6] == [k for k in ss.IDEA_BOARD_ROWS if k in ss.card_rows(board["card"])],
              screen="define/idea/check (the board)", detail={"lit": board["lit"]}, stop=False)
    film = idea.building_then_film()
    spoken = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    build = spoken.get("build") or {}
    leg.check(run, f"{label}: the idea's build reaches ready; the film drawn", film["state"] == "story"
              and build.get("state") == "ready", screen="define/idea/check (story)",
              detail={"screen": film["state"], "build": build.get("state"), "failed": film.get("failed")})
    scenes = ss.idea_scenes_verdict(build.get("story"), spoken, name=name, tagline=tagline)
    run.__dict__.setdefault("idea_films", []).append({"label": label, "verdict": scenes})
    leg.check(run, f"{label}: the film in five chapters -- at most eleven scenes, the opening line *This time, {name} is "
                   "on the screen.*, the setup scene iff a setup, one scene a step, the limitations' marks the board's, "
                   "the advantage iff read, the joy last (`joy: true`, the board's joy), the brand on every screen, a "
                   "picture on every scene (FakePictures), one clip a line, the plate the brand with its tagline",
              scenes["ok"], screen="GET idea (build.story)", view="wire", detail=scenes, stop=False)
    plate = film.get("plate") or {}
    words = [ss.CHAPTER_WORDS[c] for c in scenes["chapters"]]
    leg.check(run, f"{label}: the plate (the name and the tagline) alone about three seconds before the film, then the "
                   "chapters' words on the band in order (*Before*, *The task*, *What it solves*, ...)",
              bool(plate.get("text")) and _bare(name) in _bare(plate.get("text"))
              and (plate.get("held_s") or 0) >= 2.0 and film["chapters"] == [w for w in words if w in film["chapters"]]
              and len(film["chapters"]) >= 2, screen="define/idea/check (the plate, the film)",
              detail={"plate": plate, "chapters": film["chapters"], "want": words, "pictures": film["pictures"]},
              stop=False)
    if before_yes:
        before_yes()
    if back_to_money:
        landed = idea.film_yes_to_money()
        leg.check(run, f"{label}: the film's quiet goes back to the money start (no verdict, no pilot ask there)",
                  "start=money" in landed["landed"] and not landed["verdict"], screen="define/idea/check -> money",
                  detail=landed, stop=False)
        return {"name": name, "landed": landed["landed"], "plan": plan, "idea": spoken}
    after = idea.film_yes_verdict_pilot()
    final = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    leg.check(run, f"{label}: after the film's yes the verdict line on its card (`story-verdict`), word for word the "
                   f"served `verdictLine` (*{ss.SOLUTION_VERDICT_LINE[:40]}...*), then *{ss.VERDICT_ASK}*; the quiet "
                   "goes on", after["verdict"]["drawn"] and _norm_words(after["verdict"]["words"]).endswith(
                       _norm_words(final.get("verdictLine"))) and final.get("verdictLine") == ss.SOLUTION_VERDICT_LINE
              and any(ss.VERDICT_ASK in x for x in after["verdict"]["said"]), screen="define/idea/check (the verdict)",
              detail={"verdict": after["verdict"], "served": final.get("verdictLine")}, stop=False)
    put = after["pilot"]["put"]
    leg.check(run, f"{label}: the pilot ask heard word for word (*{ss.pilot_ask(name)}*, the served `pilotAsk`), a yes "
                   "said; `PUT idea/pilot {offer: true}` on the wire (200), the idea's `pilot` true",
              after["pilot"]["ask"] == final.get("pilotAsk") == ss.pilot_ask(name) and put["status"] == 200
              and (put["sent"] or {}).get("offer") is True and final.get("pilot") is True,
              screen="define/idea/check (the pilot ask)", view="founder + wire",
              detail={"pilot": after["pilot"], "served": final.get("pilotAsk"), "pilot now": final.get("pilot")},
              stop=False)
    return {"name": name, "landed": after["landed"], "plan": plan, "idea": final, "after": after}


def ready_checks(run: Run, leg: Leg, solution: str, label: str, landed: str) -> None:
    """Spec 162 FR-2: the ready page with no belief page on a spoken SOLUTION project -- the three SOLUTION beliefs
    written at the board's yes (*6 or 7 in 10* each, `p_60_80`), nothing owed; the Before screen's pilot question
    absent (`pilot-first-step` not drawn, no pilot screen)."""
    leg.check(run, f"{label}: the pilot's yes goes on to the ready page -- no belief page drawn on a spoken SOLUTION "
                   "project (`calibrates(spoken)` on SOLUTION)", bool(READY_PATH.search(landed))
              and "/define/solution/q/" not in landed and not vs_screens.calibrates("SOLUTION", "SOLUTION", spoken=True),
              screen="define/ready", detail={"landed": landed}, stop=False)
    review = run.get(f"/v2/projects/{solution}/review/SOLUTION") or {}
    rows = vs_screens.solution_written(review, wait_calibration(run, solution, "SOLUTION"))
    leg.check(run, f"{label}: the SOLUTION review table's three rows as written at the yes -- *6 or 7 in 10* on "
                   "Compatibility, Relative advantage and Adoption friction (`p_60_80`), complete",
              rows["codes"] == {k: ["p_60_80"] for k in vs_screens.SOLUTION_WRITTEN}
              and all(rows["labels"].get(k) == vs_screens.SOLUTION_BIN_LABEL for k in vs_screens.SOLUTION_WRITTEN),
              screen="review/SOLUTION", view="wire", detail=rows, stop=False)
    page = run.page
    shown: list[dict] = []
    for screen in ("word", "pilot", "interviewer"):
        page.goto(f"{run.web}/p/{solution}/define/ready/{screen}", wait_until="load")
        page.wait_for_timeout(1500)
        shown.append({"screen": screen, "url": page.url, "pilot-first-step": page.get_by_test_id(
            "pilot-first-step").count(), "pilot-pick": page.get_by_test_id("pilot-pick").count(),
            "counter": _safe(lambda: page.get_by_test_id("before-counter").first.inner_text())
            if page.get_by_test_id("before-counter").count() else None})
    leg.check(run, f"{label}: the Before step's pilot question is absent where the pilot was answered by voice -- no "
                   "pilot screen, no `pilot-first-step` (the counter as drawn kept in the detail)",
              all(s_["pilot-first-step"] == 0 and s_["pilot-pick"] == 0 for s_ in shown),
              screen="define/ready (Before people see it)", detail=shown, stop=False)
    plan = run.get(f"/v2/projects/{solution}/plan") or {}
    leg.notes.append(f"{label}: the Before step as drawn after the spoken pilot -- {shown}; plan pilotEnabled "
                     f"{plan.get('pilotEnabled')}")


def failed_build_walk(run: Run, leg: Leg) -> None:
    """Spec 162 FR-3: a failed build walked once -- a solution on the defined problem of FR-1a, the brand the cloud's
    scripted review always answers no on (`ideaReviews`), the beats told, the board's yes: the build fails on its chapter
    (`failedChapter`), Keel says *Keel could not draw {chapter}. Say that part again?* and opens that beat again."""
    problem = run.projects.get("a-script")
    reviews = run.readings.get("ideaReviews") or []
    if not problem or not reviews:
        leg.notes.append("the failed build was not walked: no defined problem of FR-1a, or no scripted review")
        return
    failing = str(reviews[0].get("name"))
    run.new_project(f"162 solution failed {run.stamp}", "SOLUTION")
    start = ss.SolutionStart(run.page, run.recorder, run.web)
    start.press_start()
    start.read()
    run.load_runtime("SOLUTION")
    made = start.pick(problem)
    solution = str((made["body"] or {}).get("projectId"))
    run.projects["b-failed"] = solution
    idea = ss.IdeaWalk(run.page, run.recorder, run.web)
    idea.film_then_opening(solution)
    idea.brand_page(name=failing, tagline=ss.IDEA_TAGLINE)
    idea.beats(idea_plan(run, "failed"))
    idea.boxes()
    film = idea.building_then_film()
    build = ((run.get(f"/v2/projects/{solution}/idea/spoken") or {}).get("build")) or {}
    failed = film.get("failed") or {}
    chapter = build.get("failedChapter")
    want = ss.failed_say(chapter or "", build.get("failedReason"))      # spec 167 FR-2: with 275's reason
    reopened = str(failed.get("reopened") or "")
    beat = build.get("failedBeat") or ss.BEAT_OF_CHAPTER.get(str(chapter))
    leg.check(run, f"a failed build (the brand *{failing}*, reviewed no twice): `build.state` failed with its chapter "
                   f"(`failedChapter` {chapter}), *{want}* said on the building screen (`data-failed-chapter`), then "
                   "that part's beat opened again",
              build.get("state") == "failed" and bool(chapter) and failed.get("chapter") == chapter
              and failed.get("said") == want and reopened == ("brand" if chapter == "brand" else str(beat)),
              screen="define/idea/check (the failed build)", view="founder + wire",
              detail={"build": {k: build.get(k) for k in ("state", "failedChapter", "failedBeat", "failedScene")},
                      "screen": failed, "want": want}, stop=False)


def fr1_b(run: Run, leg: Leg) -> None:
    name = f"162 solution {run.stamp}"
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
    told = tell_the_story(run, leg, problem, "the solution's problem", telling=FR1B_TELLING, back_to="solution",
                          goto=False)
    leg.check(run, "the story's quiet is the return trip: the which-problem page with the problem just agreed picked",
              f"problem={problem}" in told["landed"], screen="define/story/check -> /?start=solution",
              detail=told["landed"])
    try:
        run.page.wait_for_function(
            "(p) => { const rows = [...document.querySelectorAll('[data-testid=solution-candidate]')]; "
            "return rows.length > 0 && rows[0].getAttribute('data-project') === p && rows[0].hasAttribute('data-picked'); }",
            arg=problem, timeout=20_000)
    except Exception:  # noqa: BLE001 - recorded, judged below
        pass
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
    done = idea_leg(run, leg, solution, "the solution", telling="asks")
    run.__dict__["founders_solution"] = {"label": "the solution", "project": solution, **{
        k: done.get(k) for k in ("name", "landed")}, "idea": done.get("idea"), "after": done.get("after")}
    ready_checks(run, leg, solution, "the solution", done["landed"])
    calibration = wait_calibration(run, solution, "SOLUTION")
    leg.check(run, "the SOLUTION calibration answered at the board's yes -- the three questions served answered, none "
                   "owed (keel-cloud 271 judgement call 16: `calibrated`)",
              vs_screens.solution_calibration_answered(calibration), screen="calibration/SOLUTION", view="wire",
              detail={"state": calibration.get("state"), "total": calibration.get("total"),
                      "answered": calibration.get("answered")}, stop=False)
    failed_build_walk(run, leg)


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
    rows = (run.get("/v2/me/projects") or {}).get("mine") or []
    wire = next((r for r in rows if r.get("projectId") == problem), {})
    # spec 164 mirror 10 (keel-web 258, DRIFT #114 resolved): the list nests it on `defined`, `calibrating` and
    # `calibrated` -- the wire's row says where it nests (`story_screens.parent_of`, keel-web `storyList.parentOf`)
    parent = (ss.parent_of(wire, rows) or {}).get("projectId")
    nested = "Defined, not sent" in (drawn.get("text") or "") and (drawn.get("href") or "").endswith(problem)
    leg.check(run, "the list nests the defined problem project under the study that uses it, *Defined, not sent* "
                   "(on `defined`, `calibrating` or `calibrated`; keel-web 258)",
              nested and parent == solution and (wire.get("definition") or {}).get("status") in YES_STATUSES,
              screen="/ (the project list)",
              detail={"drawn": drawn, "parent (storyList)": parent,
                      "wire": {k: wire.get(k) for k in ("definition", "lineage", "story")}}, stop=False)
    with run.recorder.step("FR-1d: the founder opens it from the list", party="founder"):
        if nested:
            row.click()
        else:
            # spec 161 (DRIFT #114): the problem project drawn as a study of its own -- opened at its own address
            page.goto(f"{run.web}/p/{problem}", wait_until="load")
        page.wait_for_url(re.compile(rf"/p/{problem}"), timeout=30_000)
        page.wait_for_timeout(2500)
    resumed = page.url
    leg.check(run, "it resumes at the window screen", "/define/context/window" in resumed
              or page.locator("[data-testid=context-window-page]").count() > 0, screen="/p/{id} (resume)",
              detail={"url": resumed, "card": _safe(lambda: page.locator(".understands").first.inner_text())},
              stop=False)
    run.load_runtime("PROBLEM")
    j = run.journey("d", "PROBLEM", problem)
    # spec 161 FR-2: a spoken PROBLEM project walks no belief page -- the window, then the ready page; the review table's
    # three rows read as written at the boxes' yes
    on_screen = ss.web_has_257(run.stack.keel_web) and "/define/context/window" in resumed
    window_then_ready(run, leg, problem, "the defined problem", wire=not on_screen)
    review = wait_review(run, problem)
    read = vs_screens.written_beliefs(review)
    leg.check(run, "the review table's three rows as written: *6 or 7 in 10* (Prevalence), the bin (Frequency), "
                   "Importance the own row first then the other tasks -- no belief page walked",
              review.get("complete") is True and read["prevalence"] == ["p_60_80"] and read["frequency"] == ["p_60_80"]
              and len(read["importance"]) >= 3 and read["dimensions"] == 3, screen="review/PROBLEM", view="wire",
              detail=read, stop=False)
    try:
        cs.plan_complete(j)
        planned = True
    except AssertionError as missed:
        planned = False
        leg.notes.append(f"the plan: {str(missed)[:300]}")
    leg.check(run, "calibrated with no belief page: the plan reads complete over the problem", planned,
              screen="GET plan", view="wire", detail=j.changed.get("plan_complete"))
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
    told = tell_the_story(run, leg, problem, "the money's problem", telling=FR1C_TELLING, back_to="money",
                          goto=False)
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
    done = idea_leg(run, leg, solution, "the money's solution", telling="plain", back_to_money=True,
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
    money_card(run, leg, "the money's replay", replay, done["name"], idea=done.get("idea"))
    ss.pass_the_welcome(page)
    context = run.get(f"/v2/projects/{money}/context") or {}
    idea_view = run.get(f"/v2/projects/{money}/idea") or {}
    actor = ss.reading_of(run.readings, 1).get("actor")
    leg.check(run, "the persona screen, pre-filled: the chain's actor and the idea's name",
              (context.get("fields") or {}).get("actor") is not None and bool(idea_view.get("what") or
                                                                              idea_view.get("shortName") or done["name"]),
              screen="define/persona", detail={"context": context.get("fields"), "actor (script)": actor,
                                               "idea": {k: idea_view.get(k) for k in ("what", "shortName", "line")}})
    j = run.journey("c", "COMMERCIAL", money)
    # the idea's name every money question uses is the chain's (keel-cloud 261 FR-2: Price names the idea)
    # spec 162 (keel-cloud 271): a spoken idea's name is its brand's (the typed idea's `shortName` where one was typed)
    j.idea_name = str(idea_view.get("shortName") or idea_view.get("what") or done["name"] or "")
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


def money_card(run: Run, leg: Leg, label: str, replay: dict, product: str, *, idea: dict | None = None) -> None:
    """Spec 158c FR-7 (keel-web 249 FR-5): the money front's replay is the card -- *What Keel understood*, the person,
    *The product* with the name (`today`), no cost row, nothing drawn -- under the small orb, no glow; its one
    hand-over chimed once; no welcome sheet on `define/money/start` (FR-8). Spec 162 FR-4 (keel-web 259 FR-9): on a
    spoken idea (`idea`, its board) the replay reads the board's rows -- the workflow, the setup, the statement, the
    limitations and the joy -- in place of the product sentence and the *So* line."""
    card = replay["screen"].get("card") or {}
    rows = ss.card_rows(card)
    if idea and idea.get("workflow"):
        said = [_norm_words(x.get("text")) for x in replay["screen"].get("words") or []]
        verdict = ss.board_six_verdict({"rows": [r for r in card.get("rows") or [] if r.get("box") in
                                                 ss.IDEA_BOARD_ROWS]}, idea, name=product, tagline=None)
        leg.check(run, f"{label}: the replay reads the idea's board (by `data-box`: the person, then *{product}*, the "
                       "workflow, the setup, the statement, the limitations and the joy), no product sentence, no *So* "
                       "row, no cost row (keel-web 259 FR-9)",
                  "person" in rows and not verdict["missing"] and "today" not in rows and "cost" not in rows
                  and all(k in rows for k in ("workflow", "statement", "joy")), screen="define/money/start (story-boxes)",
                  detail={"rows": rows, "verdict": verdict, "lit": card.get("lit"), "said": said}, stop=False)
    else:
        leg.check(run, f"{label}: the card (by `data-box`: the person, *The product* naming *{product}*, no cost row)",
                  card.get("label") == ss.CARD_LABEL and "person" in rows and _bare(product) in _bare(rows.get("today"))
                  and "cost" not in rows, screen="define/money/start (story-boxes)",
                  detail={"rows": rows, "lit": card.get("lit")}, stop=False)
    turn_screen(run, leg, label, replay["screen"], "define/money/start", card=True)
    read = replay.get("turn") or {}
    v = (read.get("chime") or {})
    run.turns.append({"label": label, "chime": v, "sheets": ss.sheet_verdict(read.get("sheets") or [])})
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
