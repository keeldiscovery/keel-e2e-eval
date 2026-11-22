"""Spec 157: **the three views, end to end** -- the spoken problem, the solution and the money chain (keel-cloud 259 /
260 / 261, keel-web 241 / 242 / 243) walked once on the stack, nothing bought.

One run (`make e2e-157`, `evals/e2e_157_three_views.py`) is a chain of legs over one founder:

* **FR-1, the founder's legs.** (a) two problem projects told the same seven turns, one by *I would rather type the
  answers* and one through the spoken screen (the seam's recorder, the stack's FakeTranscriber: typed text in, the same
  text out), each to the boxes' yes, the build `ready`, the story's yes, the window screen and Prevalence, and their
  context and statement equal on the wire (keel-cloud 259's acceptance pair); (b) a solution start with no problem
  project: the problem created from it, its story, the return trip with it picked, the brand with a colour, the three
  turns, the boxes, the day with the idea, Compatibility with Relative advantage pre-filled; (c) the money start
  (keel-web 243 -- written to its spec, run where it has landed); (d) the problem project of (b), opened from the list
  (*Defined, not sent*), resumed, calibrated, refused at the lock on a drained grant, then locked once (the ledger's one
  PROJECT charge) and a link sent.
* **FR-2, the stranger's legs** (`evals/three_views_strangers.py`): the text, avatar and copilot views of each locked
  project's link.

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
FOUNDER_LEGS = (("FR-1a", "the problem, typed and spoken, to Prevalence; the 259 acceptance pair"),
                ("FR-1b", "the solution start with no problem project, to Compatibility with Relative advantage pre-filled"),
                ("FR-1c", "the money start with nothing, to the persona pre-filled, one lock charge, the links"),
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


# ------------------------------------------------------------------------------------------------ the story

def tell_the_story(run: Run, leg: Leg, project_id: str, mode: str, *, back_to_solution: bool = False,
                   back_to_money: bool = False) -> dict:
    """keel-web 241 on one problem project: the opening, the seven turns in `mode`, the boxes, the build, the story's
    yes. Checks the person card filled from the script, the boxes' yes 200 (`defined`), the build `ready` with the
    check passed on the scripted room, and where the yes lands."""
    walk = ss.StoryWalk(run.page, run.recorder, run.web)
    opening = walk.open_start(project_id)
    leg.check(run, f"{mode}: the opening lists the six things, Start and *I would rather type the answers*",
              len(opening["six"]) == 6 and bool(opening["type"]), screen="define/story/start", detail=opening)
    walk.begin(mode)
    told = ss.said_turns(run.readings)
    seen = walk.tell(told, mode)
    puts = [w for w in walk.writes if "/story/turns/" in w["path"]]
    leg.check(run, f"{mode}: every turn sent as the founder said it, every answer 200",
              all((w["status"] or 0) < 400 for w in puts) and
              [((w["sent"] or {}).get("text")) for w in puts if (w["sent"] or {}).get("text")] == [t for _, t in told],
              screen="define/story/1..7", detail=[(w["path"].split("/story/")[-1], w["status"], (w["sent"] or {}))
                                                  for w in puts])
    turn4 = next((s["screen"] for s in seen if s["turn"] == 4), {})
    want_sentence = ss.reading_of(run.readings, 4).get("sentence")
    leg.check(run, f"{mode}: turn 4's card carries the sentence naming the person, and the readback's two answers",
              turn4.get("sentence") == want_sentence, screen="define/story/4", detail=turn4)
    turn6 = next((s["screen"] for s in seen if s["turn"] == 6), {})
    leg.check(run, f"{mode}: turn 6 lists each limit as a red cross; *That is all* closes the list (next 7)",
              turn6.get("limits") == ss.limits_read(run.readings) and (turn6.get("closed") or {}).get("next") == 7,
              screen="define/story/6", detail=turn6)
    if mode == "spoken":
        transcribed = [w for w in walk.writes if w["path"].endswith("/story/transcribe")]
        heard = [((w.get("body") or {}).get("text")) for w in transcribed]
        leg.check(run, "spoken: every utterance written down through story/transcribe, heard as said (the fake: "
                       "typed text in, the same text out)",
                  all(t in heard for _, t in told), screen="define/story/1..7", detail={"heard": heard})
    boxes = walk.boxes()
    leg.check(run, f"{mode}: the boxes' yes is story/confirm 200, the story defined",
              (boxes["confirm"]["status"] == 200 and (boxes["confirm"]["body"] or {}).get("status") == "defined"
               and boxes["back"] == 0), screen="define/story/check (boxes)",
              detail={k: boxes[k] for k in ("state", "back")} | {"confirm": boxes["confirm"]["status"]})
    built = walk.building_then_story()
    story = run.get(f"/v2/projects/{project_id}/story") or {}
    build = story.get("build") or {}
    leg.check(run, f"{mode}: the build reaches ready, the check passed, the scripted room, eight lines with a clip each",
              (built["state"] == "story" and build.get("state") == "ready" and (build.get("checked") or {}).get("pass")
               is True and (build.get("story") or {}).get("roomId") == ss.scripted_room(run.readings)),
              screen="define/story/check (building, story)",
              detail={"screen": built, "build": {k: build.get(k) for k in ("state", "checked")},
                      "room": (build.get("story") or {}).get("roomId"),
                      "scenes": len((build.get("story") or {}).get("scenes") or [])})
    yes_words = built.get("yes")
    want_words = ss.STORY_YES_MONEY if back_to_money else ss.STORY_YES_BACK if back_to_solution else ss.STORY_YES
    leg.check(run, f"{mode}: the story's one button reads *{want_words}*", yes_words == want_words,
              screen="define/story/check (story)", detail=yes_words, stop=False)
    landed = walk.story_yes(lands=re.compile(r"/\?start=money" if back_to_money else r"/\?start=solution|/define/context"
                                             if back_to_solution else r"/define/context"))
    walk.stop_listening()
    return {"walk": walk, "landed": landed, "story": story}


def window_then_prevalence(run: Run, leg: Leg, project_id: str, mode: str) -> dict:
    """After the story's yes: the window screen (keel-web 241 FR-1: context 2 of 2, `define/context/window`), its Save,
    then Prevalence (`define/problem/q/1`) with the story's own question. Where the window screen is not drawn -- the
    confirm stores keel-cloud's default window (259 FR-3, `RecallWindow.DEFAULT`), so keel-web's `windowOwed` reads
    false and the confirmed card is drawn instead, whose *Continue to the problem* opens the problem's seed chat
    (runs/DRIFT.md #103) -- both are failed checks by name, and the walk goes on to Prevalence by its address so the
    rest of the leg is still measured."""
    page = run.page
    page.wait_for_timeout(1500)
    url = page.url
    window_page = "/define/context/window" in url and page.locator("[data-testid=context-window-page]").count() > 0 \
        and page.locator("[data-testid=context-window-page]").first.is_visible()
    card = page.locator(".understands").count() > 0
    leg.check(run, f"{mode}: the story's yes opens the window screen (context 2 of 2)", window_page,
              screen="define/context/window", detail={"url": url, "window page": window_page,
                                                     "confirmed card instead": card,
                                                     "card": _safe(lambda: page.locator(".understands")
                                                                   .first.inner_text()) if card else None,
                                                     "drift": "runs/DRIFT.md #103"}, stop=False)
    shot = ss._BrowserStep(run.recorder, page, "founder")
    with run.recorder.step(f"{mode}: on to the problem's first question", party="founder") as h:
        if window_page:
            page.locator("button.cwindow__chip").first.click()
            page.get_by_role("button", name=re.compile(r"save and continue", re.I)).first.click()
        else:
            page.get_by_role("button", name=re.compile(r"continue to the problem", re.I)).first.click()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not re.search(r"/define/problem/(q/1|seed)", page.url):
            page.wait_for_timeout(250)
        page.wait_for_timeout(1000)
        landed = page.url
        h.add_screenshot(shot.screenshot(f"after-the-context-{mode}"))
    leg.check(run, f"{mode}: the context's forward press goes on to Prevalence (define/problem/q/1), never the seed "
                   "chat the story already answered", "/define/problem/q/1" in landed, screen="define/context -> "
              "define/problem/q/1", detail={"landed": landed, "drift": "runs/DRIFT.md #103"}, stop=False)
    if "/define/problem/q/1" not in landed:
        page.goto(f"{run.web}/p/{project_id}/define/problem/q/1", wait_until="load")
    page.locator("h1").first.wait_for(state="visible", timeout=60_000)
    page.wait_for_timeout(1500)
    shot.screenshot(f"prevalence-{mode}")
    calibration = wait_calibration(run, project_id, "PROBLEM")
    prevalence = next((q for q in calibration.get("questions") or [] if q.get("dimension") == "problem.prevalence"), {})
    heading = _safe(lambda: page.locator("main h1, .ccard h1").first.inner_text())
    leg.check(run, f"{mode}: Prevalence is drawn with the story's own event (the chain applied on the founder's runtime)",
              calibration.get("state") == "READY" and run.prevalence["event"] in (prevalence.get("question") or ""),
              screen="define/problem/q/1", detail={"state": calibration.get("state"),
                                                   "question": prevalence.get("question"), "drawn": heading})
    return {"calibration": calibration}


def wire_pair(run: Run, project_id: str) -> dict:
    """What 259's acceptance pair compares, off the wire: the context (fields, the read-back, the occasion, the segment,
    the window) and the problem's statement."""
    context = run.get(f"/v2/projects/{project_id}/context") or {}
    review = run.get(f"/v2/projects/{project_id}/review/PROBLEM") or {}
    return {"fields": context.get("fields"), "understands": context.get("understands"),
            "occasion": context.get("occasion"), "segment": context.get("segment"), "state": context.get("state"),
            "statement": review.get("statement")}


# ------------------------------------------------------------------------------------------------ FR-1 (a)

def fr1_a(run: Run, leg: Leg) -> None:
    pairs = {}
    for mode in ("typed", "spoken"):
        name = f"157 problem {mode} {run.stamp}"
        run.new_project(name, "PROBLEM")
        pid = MarketStep(run.page, run.recorder, run.web).start()
        run.projects[f"a-{mode}"] = pid
        run.names[f"a-{mode}"] = name
        run.page.wait_for_timeout(1500)
        leg.check(run, f"{mode}: a new problem project opens on the story (its context not confirmed)",
                  "/define/story" in run.page.url or "/define" in run.page.url, screen="/p/{id}",
                  detail=run.page.url, stop=False)
        tell_the_story(run, leg, pid, mode)
        pairs[mode] = wire_pair(run, pid)
        window_then_prevalence(run, leg, pid, mode)
    typed, spoken = pairs["typed"], pairs["spoken"]
    leg.check(run, "259's acceptance pair: the typed path and the spoken path, the same words, leave the same context "
                   "and the same statement on the wire",
              typed == spoken and bool(typed.get("statement")) and typed.get("state") == "CONFIRMED",
              screen="GET context + review/PROBLEM", view="wire", detail={"typed": typed, "spoken": spoken})
    want = ss.reading_of(run.readings, 7, ss.said_turns(run.readings)[-1][1]).get("statement")
    leg.check(run, "the statement is the turn-7 reading's (keel-cloud 259 judgement call 4)",
              typed.get("statement") == want, screen="review/PROBLEM", view="wire",
              detail={"statement": typed.get("statement"), "want": want})


# ------------------------------------------------------------------------------------------------ FR-1 (b)

def fr1_b(run: Run, leg: Leg) -> None:
    name = f"157 solution {run.stamp}"
    run.new_project(name, "SOLUTION")
    start = ss.SolutionStart(run.page, run.recorder, run.web)
    start.press_start()
    opened = start.read()
    leg.check(run, "the market's Start on a solution scope opens the solution start and creates nothing",
              opened["create"] == "Create a problem project" and (opened["pending"] or {}).get("scope") == "SOLUTION",
              screen="solution start", detail=opened)
    problem = start.create_problem()
    run.projects["b-problem"] = problem
    run.names["b-problem"] = ss.problem_name_of(name)
    created = start.created_problem
    leg.check(run, "*Create a problem project* is one POST: scope PROBLEM, the problem's name, then its story opens",
              created["status"] == 201 and (created["sent"] or {}).get("scope") == "PROBLEM"
              and (created["sent"] or {}).get("name") == ss.problem_name_of(name),
              screen="solution start", detail=created)
    told = tell_the_story(run, leg, problem, "typed", back_to_solution=True)
    leg.check(run, "the story's yes is the return trip: the solution start with the problem just agreed picked",
              f"problem={problem}" in told["landed"], screen="define/story/check -> /?start=solution",
              detail=told["landed"])
    back = start.read()
    first = (back["rows"] or [{}])[0]
    leg.check(run, "back on the start: the agreed problem first, picked, *Continue with this problem*",
              first.get("project") == problem and first.get("picked") is True
              and first.get("press") == "Continue with this problem", screen="solution start (picked)", detail=back)
    run.load_runtime("SOLUTION")
    made = start.pick(problem)
    solution = str((made["body"] or {}).get("projectId"))
    run.projects["b-solution"] = solution
    run.names["b-solution"] = name
    leg.check(run, "the pick is the one create request: scope SOLUTION and parentProjectId the problem project; lineage "
                   "names it", made["status"] == 201 and (made["sent"] or {}).get("parentProjectId") == problem
              and ((made["body"] or {}).get("lineage") or {}).get("problemProjectId") == problem,
              screen="solution start", detail=made)
    idea = ss.IdeaWalk(run.page, run.recorder, run.web)
    still = idea.still(solution)
    leg.check(run, "Still the problem: the picked problem read back, its yes is story/confirm 200",
              still["confirm"]["status"] == 200, screen="define/idea/start", detail=still)
    said = ss.said_idea(run.readings)
    turns = idea.turns(said, "spoken")
    brand = turns["brand"]
    leg.check(run, "turn 1: the name read, the brand's colour picked (PUT idea/brand 200 with the colour)",
              brand["status"] == 200 and (brand["sent"] or {}).get("colour") == ss.BRAND_SWATCHES[1],
              screen="define/idea/1", detail=brand)
    want_line = ss.idea_reading_of(run.readings, 2).get("readback")
    leg.check(run, "turn 2: *Imagine {name}, a ...* read back", want_line in (turns.get("readback") or ""),
              screen="define/idea/2", detail={"drawn": turns.get("readback"), "want": want_line})
    last = ss.idea_reading_of(run.readings, 3, said[-1][1])
    leg.check(run, "turn 3: every limit answered; the new way drafted under them",
              turns["new_way"] == list(last.get("new_way") or []) and all((a["status"] or 0) < 400
                                                                          for a in turns["limits"]),
              screen="define/idea/3", detail={"new_way": turns["new_way"], "limits": turns["limits"]})
    boxes = idea.boxes()
    leg.check(run, "the idea's boxes: Yes, that is my idea -- idea/confirm 200", boxes["confirm"]["status"] == 200,
              screen="define/idea/check (boxes)", detail=boxes["confirm"]["status"])
    built = idea.building_then_story()
    spoken = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    leg.check(run, "the idea's build reaches ready; the day with the idea drawn", built["state"] == "story"
              and ((spoken.get("build") or {}).get("state") == "ready"), screen="define/idea/check (story)",
              detail={"screen": built, "build": (spoken.get("build") or {}).get("state")})
    landed = idea.story_yes()
    leg.check(run, "the idea's story's yes lands on Compatibility", bool(ss.COMPATIBILITY_PATH.search(landed)),
              screen="define/solution/q/1", detail=landed)
    calibration = wait_calibration(run, solution, "SOLUTION")
    ra = next((q for q in calibration.get("questions") or [] if q.get("dimension") == "solution.relative_advantage"),
              {})
    benefits = list(last.get("benefits") or [])
    said_what = json.dumps(ra.get("answerWhat") or ra.get("answer") or "")
    leg.check(run, "Relative advantage arrives pre-filled with the two benefits (keel-cloud 260 judgement call 12)",
              all(b in said_what for b in benefits), screen="define/solution (Relative advantage)", view="wire",
              detail={"answerWhat": ra.get("answerWhat"), "benefits": benefits, "state": calibration.get("state")})


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


def send_link(run: Run, leg: Leg, key: str, project_id: str, fmt: str, *, person: str | None = None,
              decider: bool = False) -> dict:
    """One link on Sent's *Send more*, the person named (a corpus person of the base entry)."""
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == vs.LINK_B2B) == decider), kinds[0] if kinds else {})
    who = person or next(p.person for p in vs.person_inputs(run.base_entry("PROBLEM")))
    sent = iv_screens.Interviews(run.page, run.recorder, run.web)
    sent.land(project_id)                      # Sent, its first-open walkthrough passed (spec 059)
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


def fr1_c(run: Run, leg: Leg) -> None:
    """keel-web 243 FR-1 (keel-cloud 261 FR-1 / FR-2): a money start with nothing -- screen 1 *Create a problem project*,
    its story, back with it picked; screen 2 *Create a solution project* on it, its idea, back; *Use {name}*: the money
    project created on the solution, the persona screen with the chain's actor and the idea's name filled; Existing
    sacrifice's prompt the story's cost line; the money calibrated, locked once (one PROJECT charge), the decision-maker's
    link sent."""
    if not web_has_243(run):
        leg.status = "written, not run"
        leg.why = ("keel-web 243 (the money start) is not in the keel-web checkout the stack serves "
                   f"({MONEY_START_SOURCE} absent): written to specs/243's spec.md, not run")
        return
    page = run.page
    name = f"157 money {run.stamp}"
    run.new_project(name, "COMMERCIAL")
    with run.recorder.step("FR-1c: the market's Start on the money scope opens the money start", party="founder"):
        page.get_by_role("button", name=re.compile(r"^start$", re.I)).first.click()
        page.locator("[data-testid=money-start][data-screen=problem]").first.wait_for(state="visible", timeout=30_000)
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        page.get_by_test_id("money-create-problem").first.click()
    problem = str((got.value.json() or {}).get("projectId"))
    run.projects["c-problem"] = problem
    leg.check(run, "screen 1's *Create a problem project*: one POST, scope PROBLEM, then its story",
              got.value.status == 201 and (got.value.request.post_data_json or {}).get("scope") == "PROBLEM",
              screen="money start · the problem", detail=got.value.request.post_data_json)
    page.locator(ss.STORY_START).first.wait_for(state="visible", timeout=30_000)
    told = tell_the_story(run, leg, problem, "typed", back_to_money=True)
    leg.check(run, "the story's yes goes back to the money start", "start=money" in told["landed"],
              screen="define/story/check -> /?start=money", detail=told["landed"])
    picked = page.locator(f"[data-testid=money-problem][data-project='{problem}']").first
    picked.wait_for(state="visible", timeout=30_000)
    leg.check(run, "back on screen 1: the problem just agreed, picked", picked.get_attribute("data-picked") is not None,
              screen="money start · the problem", detail=_safe(lambda: picked.inner_text()))
    picked.get_by_test_id("money-pick-problem").click()
    page.locator("[data-testid=money-start][data-screen=solution]").first.wait_for(state="visible", timeout=30_000)
    run.load_runtime("SOLUTION")
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0].endswith("/v2/projects"),
                              timeout=30_000) as got:
        page.get_by_test_id("money-create-solution").first.click()
    solution = str((got.value.json() or {}).get("projectId"))
    run.projects["c-solution"] = solution
    leg.check(run, "screen 2's *Create a solution project*: scope SOLUTION on the problem (parentProjectId)",
              got.value.status == 201 and (got.value.request.post_data_json or {}).get("parentProjectId") == problem,
              screen="money start · the solution", detail=got.value.request.post_data_json)
    idea = ss.IdeaWalk(page, run.recorder, run.web)
    idea.still(solution)
    idea.turns(ss.said_idea(run.readings), "typed")
    idea.boxes()
    built = idea.building_then_story()
    leg.check(run, "the idea's story's one button reads *Yes, exactly my idea · back to will they pay*",
              built.get("yes") == ss.IDEA_YES_MONEY, screen="define/idea/check (story)", detail=built.get("yes"),
              stop=False)
    run.load_runtime("COMMERCIAL")
    idea.story_yes(lands=re.compile(r"start=money"))
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
              and (body.get("lineage") or {}).get("problemProjectId") == problem, screen="money start · the solution",
              detail={"sent": got.value.request.post_data_json, "lineage": body.get("lineage")})
    page.wait_for_url(re.compile(r"/define/persona"), timeout=60_000)
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
