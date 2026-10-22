"""Spec 062: the back-test runner -- a real founder's idea walked on Keel's AI, locally, recorded, never held to a corpus.

`make backtest ENTRY=<id>` (the Makefile; the pytest entry is `evals/run_backtest.py`, which no `make eval`, `make
unit`, matrix cell or checker collects -- it is not a `test_*.py` file). The entry is a **back-test entry**
(`instructions/corpus.py`, `load(..., backtest=True)`: keel-cloud's `canon/designs/measured-beliefs/backtest/`), a
corpus-shaped file written from public material with no golden expectations. What this module owns:

1. **The refusals** (FR-2): no `KEEL_ANTHROPIC_API_KEY` in the caller's shell, no `ENTRY`, a stack already answering
   (its keel-cloud was booted without this shell's key, so the target brings its own up and down), keel-cloud not saying
   *Keel's AI is ON* -- each one sentence. The key is passed to keel-cloud through the environment `stack/cloud.py`
   hands it and is never read, logged, echoed or written here; only its presence is checked.
2. **The founder** (FR-2): `Backtest Founder`, `backtest@keel-backtest.test`, registered at run time on the local
   stub (`POST /identities`, ungated locally) -- outside keel-cloud's `keel.v2.vendors.fake-for` -- and signed up through
   keel-web's `/signup`, the one door that makes an account on Keel's AI. Contacts, renders and the transcriber stay the
   local stack's fakes (`stack/cloud.py`), so nothing but model calls leaves the machine.
3. **The camera** (FR-3): one full-page screenshot of every founder screen as it is about to be answered, and of every
   served respondent screen on one person a link, into `runs/<run>/screens/` as `founder-NN-<slug>.png` /
   `respondent-<link>-NN-<slug>.png`, with what each screen drew (kicker, question, hint, the options as rendered).
4. **The export** (FR-3): 060/061's at the last answer into `runs/<run>/export/`, names kept, no verdict gate (the
   contract export moves to `runs/<run>/contract-export/` on this run alone).
5. **The transcript** (FR-4): `runs/<run>/backtest.md` (for reading) and `backtest.json` (for a judge), from the
   camera, the recorder's captures and the wire -- founder screens, respondent questions per link, the brief, the
   readings beside the file's anchoring, and cost and time. Nothing in either is asserted.

It lives in `evals/` beside `corpus_scenario.py`, whose `run()` it is handed to (`backtest=`).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

#: FR-2: the one variable the caller's shell must carry. Its value is never read here.
KEY_VAR = "KEEL_ANTHROPIC_API_KEY"
#: The entry `make backtest ENTRY=` names, as the pytest entry reads it.
ENTRY_VAR = "KEEL_BACKTEST_ENTRY"
#: keel-cloud `keel.v2.vendors.fake-for`'s default (`application.yml`), and the variable a shell may override it with.
FAKE_FOR_VAR = "KEEL_VENDORS_FAKE_FOR"
FAKE_FOR_DEFAULT = "keel-e2e-eval.test"

#: FR-2: the back-test founder, registered on the local stub at run time (its `sub` is the stub's `cell-backtest`).
IDENTITY_ID = "backtest"
IDENTITY_NAME = "Backtest Founder"
IDENTITY_EMAIL = "backtest@keel-backtest.test"

#: How many times longer a wait on a model may take than the scripted journeys' -- S-012's on the Keel door
#: (`agent_host` `keels_ai_job_wait_s` 660 s over the scripted 60 s).
PATIENCE = 11.0

#: Where the run's own files go, under `runs/<run>/`.
SCREENS_DIR = "screens"
EXPORT_DIR = "export"
CONTRACT_DIR = "contract-export"
MARKDOWN = "backtest.md"
RECORD = "backtest.json"

#: keel-cloud `AnthropicClientFactory`'s startup line when the key reached it.
KEEL_AI_ON = "Keel's AI is ON"

#: keel-web's link words in a file name.
LINK_SLUG = {"PRIMARY": "primary", "COMMERCIAL_B2B": "decision-maker"}


# ------------------------------------------------------------------------------------------------ 1. refusals

def refusal(env: dict | None = None) -> str | None:
    """FR-2's one sentence when the caller's shell carries no key, else `None`. Reads presence only."""
    env = os.environ if env is None else env
    if not (env.get(KEY_VAR) or "").strip():
        return (f"make backtest refuses: {KEY_VAR} is not set in this shell -- the local stack passes it to keel-cloud, "
                "which answers every job of the back-test on Keel's AI (spec 062 FR-2); it is never logged, echoed or "
                "written")
    return None


def entry_refusal(env: dict | None = None) -> str | None:
    env = os.environ if env is None else env
    if not (env.get(ENTRY_VAR) or "").strip():
        return ("make backtest refuses: no ENTRY -- name a back-test entry, `make backtest ENTRY=<id>` (keel-cloud "
                "canon/designs/measured-beliefs/backtest/<id>.yaml)")
    return None


def stack_up_refusal() -> str:
    return ("make backtest refuses: a stack is already answering on the eval ports, and its keel-cloud was not booted "
            f"from this shell, so it may carry no {KEY_VAR} -- `make down` first; the back-test brings its own stack "
            "up and down")


def fake_for(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    value = env.get(FAKE_FOR_VAR)
    return FAKE_FOR_DEFAULT if value is None else value


def in_fake_for(email: str, listed: str) -> bool:
    """keel-cloud `FakeFor.matches`: exact emails and bare domains, comma- or space-separated, case-insensitive."""
    entries = {e.strip().lower() for e in re.split(r"[,\s]+", listed or "") if e.strip()}
    e = (email or "").strip().lower()
    if e in entries:
        return True
    at = e.rfind("@")
    return 0 <= at < len(e) - 1 and e[at + 1:] in {x for x in entries if "@" not in x}


def keel_ai_on(cloud_log: Path) -> bool:
    try:
        return KEEL_AI_ON in Path(cloud_log).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


# -------------------------------------------------------------------------------------------------- 3. camera

#: What one screen drew, read in the page: the kicker, the stem, the hint, every option as rendered (radios,
#: checkboxes, a list's rows -- a textarea's value where the row is editable), the chips, and the main column's text.
READ_JS = """() => {
  const one = (sel) => { const e = document.querySelector(sel); return e ? (e.innerText || e.value || "").trim() : ""; };
  const all = (sel) => Array.from(document.querySelectorAll(sel))
      .map((e) => (e.innerText || e.value || "").replace(/\\s+/g, " ").trim()).filter(Boolean);
  const rows = Array.from(document.querySelectorAll("li.listrow")).map((li) => {
      const ta = li.querySelector("textarea"); return ((ta && ta.value) || li.innerText || "").replace(/\\s+/g, " ").trim();
  }).filter(Boolean);
  const dialog = document.querySelector("[role=dialog]");
  const scope = dialog || document.querySelector("main") || document.body;
  return {kicker: one(".corridor__kicker, .iv-kicker, .guided-step__kicker"),
          question: one("[role=dialog] h2, h1.calib__q, h1.iv-q, .guided-step__question, h1"),
          hint: one(".calib__hint, .iv-tick, .iv-note, .ccard__sub"),
          options: all((dialog ? "[role=dialog] " : "") + "[role=radio], " + (dialog ? "[role=dialog] " : "") + "[role=checkbox]"),
          rows: rows, chips: all(".calib__chip, .iv-chips button"),
          text: (scope.innerText || "").slice(0, 6000)};
}"""


def _safe_slug(slug: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "-" for c in slug).strip("-")[:70] or "screen"


@dataclass
class Camera:
    """FR-3's screenshots. `founder` is handed to every founder page object (`Corridor.camera`, `Interviews.camera`,
    `create_project(camera=)`); `respondent(person, page)` answers a callable for the one person a link it watches and
    None for everyone else. A shot never fails the journey: a failure is recorded on the shot."""
    run_dir: Path
    page: Any
    watched: dict                                  # link -> the person whose screens are taken
    founder_shots: list = field(default_factory=list)
    respondent_shots: dict = field(default_factory=dict)
    _taken: set = field(default_factory=set)

    @property
    def directory(self) -> Path:
        path = Path(self.run_dir) / SCREENS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _take(self, page, name: str, slug: str) -> dict:
        shot: dict = {"file": f"{SCREENS_DIR}/{name}", "slug": slug, "url": None}
        try:
            try:
                page.evaluate("document.fonts.ready")
            except Exception:  # noqa: BLE001 - a font wait never blocks evidence
                pass
            shot["url"] = page.url
            shot.update(page.evaluate(READ_JS) or {})
            page.screenshot(path=str(self.directory / name), full_page=True)
        except Exception as missed:  # noqa: BLE001 - recorded, never raised: the camera is evidence, not a step
            shot["error"] = repr(missed)[:300]
        return shot

    def founder(self, slug: str) -> None:
        """One founder screen. The send screen is taken once (its first opening), not once a person."""
        if slug.startswith("send-"):
            if slug in self._taken:
                return
            self._taken.add(slug)
        n = len(self.founder_shots) + 1
        self.founder_shots.append({"n": n, **self._take(self.page, f"founder-{n:02d}-{_safe_slug(slug)}.png", slug)})

    def respondent(self, person, page) -> Callable[[str], None] | None:
        link = getattr(person, "link", None)
        if self.watched.get(link) != getattr(person, "person", None):
            return None
        shots = self.respondent_shots.setdefault(link, {"person": person.person, "shots": []})["shots"]
        word = LINK_SLUG.get(link, str(link).lower())

        def shoot(slug: str) -> None:
            n = len(shots) + 1
            shots.append({"n": n, **self._take(page, f"respondent-{word}-{n:02d}-{_safe_slug(slug)}.png", slug)})
        return shoot


def watched_people(people: list) -> dict:
    """One person a link whose walk serves every screen: on the primary link the first who passed the gate with a
    story typed and no chip (so the gate, every item and the reveal are drawn), else the first; on the decision-maker's
    link the first."""
    out: dict = {}
    for p in people:
        if p.link in out:
            continue
        if p.link == "PRIMARY" and not (p.recency and (p.story or "").strip() and not p.anchor_chip):
            continue
        out[p.link] = p.person
    for p in people:
        out.setdefault(p.link, p.person)
    return out


# --------------------------------------------------------------------------------------------- the run's seam

@dataclass
class Backtest:
    """What `corpus_scenario.run(..., backtest=...)` calls: `sign_in`, `camera`, `lap` (each leg's wall time), `after`
    (the export) and `finish` (the transcript, whatever happened)."""
    run_dir: Path
    stack: Any
    patience: float = PATIENCE
    contract_dir: str = CONTRACT_DIR
    started: float = field(default_factory=time.monotonic)
    legs: list = field(default_factory=list)
    founder_identity: Any = None
    me_at_signup: dict = field(default_factory=dict)
    export: dict | None = None
    cam: Camera | None = None

    # ---------------------------------------------------------------------------------------- 2. the founder

    def identity(self):
        """The back-test founder on the local stub: registered now (`POST /identities`), or -- registered earlier on
        this same stub process -- the same one again."""
        from stack import remote                                  # noqa: PLC0415
        from stack.auth import StubFounder                        # noqa: PLC0415
        label = f"back-test · {time.strftime('%Y-%m-%d', time.gmtime())}"
        try:
            return remote.register_cell_identity(self.stack, label, name=IDENTITY_NAME, id=IDENTITY_ID,
                                                  email=IDENTITY_EMAIL)
        except remote.RegistryRefused as refused:
            if getattr(refused, "status", None) != 409:
                raise
            from stack.stub_oidc.registry import SUB_PREFIX       # noqa: PLC0415
            return StubFounder(id=IDENTITY_ID, sub=f"{SUB_PREFIX}{IDENTITY_ID}", email=IDENTITY_EMAIL,
                               name=IDENTITY_NAME)

    def sign_in(self, j):
        """FR-2: signed up through keel-web's /signup as the back-test founder; held before anything is asked of Keel's
        AI -- keel-cloud said *Keel's AI is ON* at boot, `/v2/me` reads `aiPath: KEEL` and the founder's email, and that
        email is outside `fake-for`."""
        from harness.browser import Auth, Landing                 # noqa: PLC0415
        from stack.config import REPO_ROOT                        # noqa: PLC0415
        founder = self.identity()
        cloud_log = REPO_ROOT / "runs" / ".stack" / "cloud.log"
        listed = fake_for()
        with j.recorder.step("back-test (spec 062 FR-2): keel-cloud booted with Keel's AI on, and the founder is outside "
                             "fake-for", party="stack", kind="assert") as h:
            h.record_assert({"cloud log": KEEL_AI_ON, "fake-for": f"does not match {IDENTITY_EMAIL}"},
                            {"keel ai on": keel_ai_on(cloud_log), "fake-for": listed,
                             "in fake-for": in_fake_for(founder.email, listed)})
            assert keel_ai_on(cloud_log), (f"keel-cloud's log ({cloud_log}) never said {KEEL_AI_ON!r}: the key did not "
                                           "reach it, so every job would fail KEEL_AI_DISABLED")
            assert not in_fake_for(founder.email, listed), (founder.email, listed)
        Auth(j.page, j.recorder, j.web_base).sign_up(founder)
        Landing(j.page, j.recorder, j.web_base).visit()
        with j.recorder.step("back-test (spec 062 FR-2): the account is on Keel's AI -- /signup made it, aiPath KEEL, "
                             "the grant on the wire", party="founder", kind="assert") as h:
            me = j.get("/v2/me") or {}
            self.me_at_signup = {k: me.get(k) for k in ("aiPath", "email", "name", "creditsAvailable")}
            h.record_assert({"aiPath": "KEEL", "email": IDENTITY_EMAIL}, self.me_at_signup)
            assert me.get("aiPath") == "KEEL", me
            assert (me.get("email") or "").lower() == IDENTITY_EMAIL, me
        self.founder_identity = founder
        return founder

    def pass_welcome(self, j, *, timeout_s: float = 30.0) -> dict:
        """The guide's welcome over the project's first screen, passed by with Skip (the golden journeys judge it in
        `leg_welcome`; here it is not the subject). Waited for up to `timeout_s`, not `MarketStep.start`'s 5 s: on a
        fresh local stack vite compiles the sheet's lazy chunk on its first request, and the dry run of 2026-10-22 saw
        it land after the 5 s pass and cover the context step's Save."""
        from harness import vectors_screens as vs_screens          # noqa: PLC0415
        sheet = vs_screens.GuideWelcome(j.page, j.recorder, j.web_base)
        if not sheet.present(timeout_s=timeout_s):
            return {"shown": False}
        return {"shown": True, **sheet.skip()}

    def camera(self, j) -> Camera:
        self.cam = Camera(run_dir=self.run_dir, page=j.page, watched=watched_people(j.people))
        return self.cam

    def lap(self, name: str) -> None:
        """FR-4.5: the wall time since the last lap (or the start), named for the leg that just ended."""
        now = time.monotonic()
        since = self.legs[-1]["_at"] if self.legs else self.started
        self.legs.append({"leg": name, "seconds": round(now - since, 1), "_at": now})

    # ---------------------------------------------------------------------------------------------- 4. export

    def after(self, j) -> None:
        """FR-3: the 060/061 export at the last answer into `runs/<run>/export/`, names kept, no verdict gate. A
        refusal (a survivor of the withholding) is recorded, never raised: the transcript is the run's product."""
        from evals import sample_export                           # noqa: PLC0415
        try:
            result = sample_export.export_sample(j, Path(self.run_dir) / EXPORT_DIR, run_dir=self.run_dir, gated=False)
            self.export = {k: result[k] for k in ("card", "size", "dir", "people") if k in result}
            self.export["files"] = len(result["manifest"]["files"])
        except sample_export.SampleRefused as refused:
            self.export = {"refused": refused.reasons}

    # ------------------------------------------------------------------------------------------ 5. transcript

    def finish(self, j, *, passed: bool, failed_step: Any = None) -> dict:
        """FR-4: `backtest.json` and `backtest.md`, from whatever the journey reached. Never raises."""
        record: dict = {"spec": "062", "run": Path(self.run_dir).name, "passed": passed,
                        "failed_step": _step_name(failed_step),
                        "wall_s": round(time.monotonic() - self.started, 1),
                        "legs": [{k: v for k, v in leg.items() if k != "_at"} for leg in self.legs]}
        try:
            record.update(transcript(j, self))
        except Exception as broke:  # noqa: BLE001 - the transcript is evidence; it must never mask the run
            record["transcript_error"] = repr(broke)[:500]
        try:
            (Path(self.run_dir) / RECORD).write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str)
                                                     + "\n", encoding="utf-8")
            (Path(self.run_dir) / MARKDOWN).write_text(markdown(record), encoding="utf-8")
        except Exception as broke:  # noqa: BLE001
            (Path(self.run_dir) / "backtest_error.txt").write_text(repr(broke), encoding="utf-8")
        return record


def _step_name(step: Any) -> str | None:
    if step is None:
        return None
    return getattr(step, "name", None) or str(step)


def _sha(path: Path | None) -> str | None:
    if path is None or not Path(path).is_dir():
        return None
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True,
                              encoding="utf-8", timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _safe(read: Callable[[], Any], default: Any = None) -> Any:
    try:
        return read()
    except Exception as missed:  # noqa: BLE001 - one section's miss never loses the others
        return {"error": repr(missed)[:300]} if default is None else default


# --------------------------------------------------------------------------------- FR-4.1 the founder's screens

def _vector_of(key: str) -> str:
    return key.split(".", 1)[0].upper()


def founder_answer(j, slug: str) -> Any:
    """The founder's answer from the file for one screen slug (what was typed or picked there)."""
    f = j.founder
    answers = {a.dimension: a for v in ("PROBLEM", "SOLUTION", "COMMERCIAL") for a in (f.calibration.get(v) or [])}
    if slug == "name":
        return f.project_name
    if slug == "market":
        return {"country": f.country, "region": f.region}
    if slug == "context":
        return {**f.context_fields, "recall window": f.window.as_wire()}
    if slug in ("context-card",):
        return "Yes, that's it"
    if slug == "problem-seed":
        return f.problem_seed
    if slug == "problem-card":
        return "Yes, that's the problem"
    if slug == "solution-seed":
        return f.solution_seed
    if slug == "solution-card":
        return "Looks right"
    if slug == "idea":
        return {"what (typed)": f.idea_name, "how / belief": "saved as Keel drafted them"}
    if slug == "persona":
        return f.decider
    if slug in ("persona-who-answers", "ready-word", "ready-pilot"):
        return "Continue"
    if slug == "ready-interviewer":
        return "Lock and record the interviewer (the face Keel preselects)"
    if slug == "send-format":
        return "Text only"
    if slug == "send-who":
        return "Someone I know: each person by name"
    kind, _, key = slug.partition("-")
    answer = answers.get(key)
    if answer is None:
        return None
    if answer.unsure:
        return "left out of the study (the founder is unsure)"
    if kind == "q":
        return {k: v for k, v in answer.as_wire().items() if k != "dimension"}
    if kind == "answer":
        return answer.text
    if kind == "check":
        return "saved as Keel drafted it"
    if kind == "choose":
        listed = answer.listed or {}
        index = listed.get("pickedIndex") or 0
        items = listed.get("items") or []
        return {"pickedIndex": index, "the file's item": (items[index] or {}).get("label") if index < len(items) else None,
                "picked on screen": "the served list's item at that index (or its last)"}
    return None


def read_back(j, slug: str, wire: dict) -> Any:
    """What Keel read back for one screen: the *Keel understands* card, the statement, the idea's lines, the belief
    sentence and the *Keel will test* box, the frame -- from the wire and what the screen drew."""
    if slug in ("context", "context-card"):
        return {"understands": (wire.get("context") or {}).get("understands")}
    if slug in ("problem-seed", "problem-card"):
        return {"statement": (wire.get("review/PROBLEM") or {}).get("statement")}
    if slug in ("solution-seed", "solution-card", "idea"):
        idea = wire.get("idea") or {}
        return {k: idea.get(k) for k in ("what", "how", "belief", "shortName", "approved")}
    if slug in ("persona", "persona-who-answers"):
        persona = wire.get("persona") or {}
        return {"respondentTypes": [{k: t.get(k) for k in ("label", "commercialLink")}
                                    for t in persona.get("respondentTypes") or []], "decider": persona.get("decider")}
    _, _, key = slug.partition("-")
    if "." not in key:
        return None
    rows = {r.get("dimension"): r for r in (wire.get(f"review/{_vector_of(key)}") or {}).get("rows") or []}
    row = rows.get(key) or {}
    seen = (j.framing or {}).get(key) or []
    screen = {"q": "single", "answer": "answer", "check": "check", "choose": "choose"}.get(slug.split("-", 1)[0])
    drawn = next((s for s in seen if s.get("screen") == screen), {}) if screen else {}
    out = {"belief": row.get("belief"), "left out": bool(row.get("leftOut") or row.get("unsure")) or None,
           "frame": (drawn.get("frame") or {}).get("progress")}
    if drawn.get("belief"):
        out["belief line on screen"] = drawn.get("belief")
    test = drawn.get("test_after") or drawn.get("test")
    if test:
        out["keel will test"] = test.get("belief")
        out["bar"] = test.get("bar")
    return {k: v for k, v in out.items() if v not in (None, "")}


def _wire(j) -> dict:
    reads = {}
    for key in ("context", "review/PROBLEM", "review/SOLUTION", "review/COMMERCIAL", "idea", "persona", "plan",
                "standings", "invitations", "overview"):
        reads[key] = _safe(lambda k=key: j.get(j.project(f"/{k}")), {})
    return reads


def founder_screens(j, cam: Camera | None, wire: dict) -> list[dict]:
    out = []
    for shot in (cam.founder_shots if cam else []):
        slug = shot.get("slug") or ""
        out.append({"n": shot["n"], "screen": slug, "file": shot.get("file"), "kicker": shot.get("kicker"),
                    "question": shot.get("question"), "hint": shot.get("hint"),
                    "options": shot.get("options") or [], "rows": shot.get("rows") or [],
                    "chips": shot.get("chips") or [], "answer": _safe(lambda s=slug: founder_answer(j, s)),
                    "keel read back": _safe(lambda s=slug: read_back(j, s, wire)),
                    **({"camera error": shot["error"]} if shot.get("error") else {})})
    return out


# -------------------------------------------------------------------------------- FR-4.2 the respondent questions

def _labels(rows: list | None, key: str = "label") -> list:
    return [(r or {}).get(key) for r in rows or []]


def served_items(interview: dict) -> dict:
    """The interview as the respondent page fetched it: the idea, the gate, every item in order (wording, control,
    every option label, the escape) and the reveal."""
    parts = []
    for part in interview.get("parts") or []:
        items = []
        for item in part.get("items") or []:
            items.append({"dimension": item.get("dimension"), "question": item.get("question"),
                          "control": item.get("control"), "hint": item.get("hint"),
                          "options": _labels(item.get("options")), "advantages": _labels(item.get("advantages")),
                          "escape": (item.get("escape") or {}).get("label")})
        parts.append({"part": part.get("part"), "kicker": part.get("kicker"), "items": items})
    gate = interview.get("gate") or None
    return {"kind": interview.get("kind"), "occasion": interview.get("occasion"),
            "idea": interview.get("idea"), "gate": gate, "parts": parts, "reveal": interview.get("reveal")}


def respondent_questions(j, cam: Camera | None) -> dict:
    out = {}
    for link, person in (cam.watched if cam else {}).items():
        shots = ((cam.respondent_shots.get(link) or {}).get("shots") or []) if cam else []
        out[link] = {"person": person, "served": served_items((j.interviews or {}).get(person) or {}),
                     "drawn": ((j.walked or {}).get(person) or {}).get("screens") or [],
                     "screens": [s.get("file") for s in shots]}
    return out


# ------------------------------------------------------------------------------------------- FR-4.3 the brief

def brief(standings: dict) -> dict:
    facts = standings.get("facts") or {}
    decision = facts.get("decision") or {}
    stages = {}
    for vector in ("problem", "solution", "commercial"):
        stage = facts.get(vector) or {}
        stages[vector.upper()] = {"broke": stage.get("broke"), "notAsked": stage.get("notAsked")}
    insights = []
    for i in standings.get("insights") or []:
        insights.append({"dimension": i.get("dimension"), "name": i.get("name"), "status": i.get("status"),
                         "rungHeading": i.get("rungHeading"), "noQuestionWhy": i.get("noQuestionWhy"),
                         "against": i.get("against"), "asked": i.get("asked"), "answered": i.get("answered"),
                         "themes": [{"label": t.get("label"), "count": t.get("count"),
                                     "evidence": [{"name": q.get("name"), "text": q.get("text")}
                                                  for q in t.get("quotes") or []]}
                                    for t in i.get("themes") or []],
                         "raw": i.get("raw"), "rawQuotes": [{"name": q.get("name"), "text": q.get("text")}
                                                           for q in i.get("rawQuotes") or []]})
    return {"decision": {k: decision.get(k) for k in ("label", "howSure", "reason", "smallestN", "split", "notTested")},
            "verdicts": {v.get("vector"): v.get("words") or v.get("verdict") for v in facts.get("vectors") or []},
            "cards": [{k: c.get(k) for k in ("key", "name", "number", "line", "status", "statusWords", "keelBar")}
                      for c in facts.get("cards") or []],
            "stages": stages, "insights": insights, "pilot": standings.get("pilot"),
            "price": standings.get("priceMedian"), "people": standings.get("people"),
            "contextUnderstands": standings.get("contextUnderstands")}


# ------------------------------------------------------------------------------------------ FR-4.4 the readings

def readings(j, invitations: dict) -> list[dict]:
    by_name = {r.get("personName"): r.get("invitationId") or r.get("id")
               for r in (invitations or {}).get("invitations") or []}
    out = []
    for p in j.people:
        row = {"person": p.person, "link": p.link, "gate": p.recency, "story": p.story,
               "chip": p.anchor_chip, "file anchoring": p.anchoring}
        invitation = by_name.get(p.person)
        if invitation:
            detail = _safe(lambda i=invitation: j.get(j.project(f"/invitations/{i}")), {})
            interview = (detail or {}).get("interview") or {}
            row["model anchoring"] = interview.get("anchoring")
            row["status"] = (detail or {}).get("status")
        row["same"] = (row.get("model anchoring") == p.anchoring) if p.anchoring else None
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------ FR-4.5 cost and time

def cost(j) -> dict:
    from harness import keel_host                                  # noqa: PLC0415
    interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
    per_job = keel_host.jobs_with_their_execution(j.get, interactions)
    total = sum(r.get("actual_cost_micro_usd") or 0 for r in per_job)
    by_class: dict = {}
    for r in per_job:
        c = by_class.setdefault(r.get("screen") or "?", {"jobs": 0, "micro_usd": 0, "models": set()})
        c["jobs"] += 1
        c["micro_usd"] += r.get("actual_cost_micro_usd") or 0
        if r.get("model_used"):
            c["models"].add(r["model_used"])
    for c in by_class.values():
        c["models"] = sorted(c["models"])
        c["usd"] = round(c["micro_usd"] / 1_000_000, 4)
    return {"jobs": len(per_job), "micro_usd": total, "usd": round(total / 1_000_000, 4),
            "by_class": by_class, "models": sorted({r.get("model_used") for r in per_job if r.get("model_used")}),
            "hosts": sorted({str(r.get("host")) for r in per_job}),
            "not settled": [{k: r.get(k) for k in ("screen", "status", "error")} for r in per_job
                            if r.get("status") != "COMPLETED"],
            "not on the wire": ("the answer path's classifier calls (keel-cloud 099) are no job, so their cost is not "
                                "here; tokens are not on the wire either"),
            "per_job": [{k: r.get(k) for k in ("screen", "status", "model_requested", "model_used",
                                               "actual_cost_micro_usd", "host")} for r in per_job]}


def transcript(j, bt: Backtest) -> dict:
    if j is None:
        return {"journey": "never opened"}
    entry = j.entry
    wire = _wire(j)
    standings = wire.get("standings") or j.standings or {}
    me = _safe(lambda: j.get("/v2/me"), {})
    return {
        "entry": {"id": entry.id, "title": entry.title, "path": str(entry.path), "sha256": entry.sha256,
                  "idea_name": getattr(entry, "idea_name", None), "b2b": entry.b2b()},
        "stack": {"keel-cloud": _sha(getattr(j.stack, "keel_cloud", None)),
                  "keel-web": _sha(getattr(j.stack, "keel_web", None))},
        "founder": {"identity": IDENTITY_EMAIL, "at sign-up": bt.me_at_signup,
                    "credits now": (me or {}).get("creditsAvailable"), "project": j.project_id},
        "founder_screens": founder_screens(j, bt.cam, wire),
        "respondents": respondent_questions(j, bt.cam),
        "brief": _safe(lambda: brief(standings)),
        "readings": _safe(lambda: readings(j, wire.get("invitations") or {}), []),
        "cost": _safe(lambda: cost(j)),
        "export": bt.export,
        "screenshots": {"founder": len(bt.cam.founder_shots) if bt.cam else 0,
                        "respondent": {link: len(v.get("shots") or [])
                                       for link, v in (bt.cam.respondent_shots if bt.cam else {}).items()}},
    }


# --------------------------------------------------------------------------------------------- the markdown

def _q(value: Any) -> str:
    if value in (None, "", [], {}):
        return "--"
    if isinstance(value, (dict, list)):
        return "`" + json.dumps(value, ensure_ascii=False) + "`"
    return str(value).replace("\n", " ")


def markdown(r: dict) -> str:
    """`backtest.md`: for reading. Every value as served; nothing asserted."""
    entry = r.get("entry") or {}
    b = r.get("brief") or {}
    decision = b.get("decision") or {}
    c = r.get("cost") or {}
    shots = r.get("screenshots") or {}
    lines = [f"# Back-test: {entry.get('title') or entry.get('id') or '?'}", "",
             f"- Entry: `{entry.get('id')}` ({entry.get('path')}), the founder's idea name *{entry.get('idea_name')}*",
             f"- Run: `{r.get('run')}` -- {'walked to the end' if r.get('passed') else 'stopped at: ' + _q(r.get('failed_step'))}",
             f"- Stack: keel-cloud `{(r.get('stack') or {}).get('keel-cloud')}`, keel-web "
             f"`{(r.get('stack') or {}).get('keel-web')}`, Keel's AI (local), founder `{IDENTITY_EMAIL}`",
             f"- Decision: **{decision.get('label')}** ({decision.get('howSure')}; {decision.get('reason')})",
             f"- Verdicts: {_q(b.get('verdicts'))}",
             f"- Pilot: {_q(b.get('pilot', {}) and {k: (b.get('pilot') or {}).get(k) for k in ('optedIn', 'finished', 'percent')})}"
             f"; price: {_q((b.get('price') or {}).get('edgeSaid') if isinstance(b.get('price'), dict) else b.get('price'))}",
             f"- Cost: ${c.get('usd')} over {c.get('jobs')} jobs; models {_q(c.get('models'))}",
             f"- Wall time: {r.get('wall_s')} s; screenshots: {shots.get('founder')} founder, "
             f"{_q(shots.get('respondent'))} respondent",
             f"- Export: {_q(r.get('export'))}",
             "", "Nothing here is asserted: the model's words are the finding (spec 062 FR-4).", ""]
    lines += ["## 1. Founder screens, in order", ""]
    for s in r.get("founder_screens") or []:
        lines.append(f"### {s['n']:02d}. {s['screen']}  (`{s.get('file')}`)")
        for label, key in (("Kicker", "kicker"), ("Question", "question"), ("Hint", "hint")):
            if s.get(key):
                lines.append(f"- {label}: {_q(s[key])}")
        if s.get("options"):
            lines.append("- Options: " + " | ".join(str(o) for o in s["options"]))
        if s.get("rows"):
            lines.append("- List: " + " | ".join(str(o) for o in s["rows"]))
        if s.get("chips"):
            lines.append("- Chips: " + " | ".join(str(o) for o in s["chips"]))
        lines.append(f"- Founder (from the file): {_q(s.get('answer'))}")
        lines.append(f"- Keel read back: {_q(s.get('keel read back'))}")
        lines.append("")
    lines += ["## 2. Respondent questions, per link", ""]
    for link, v in (r.get("respondents") or {}).items():
        served = v.get("served") or {}
        lines.append(f"### {link} -- as served to {v.get('person')} ({served.get('kind')})")
        if served.get("idea"):
            lines.append(f"- Idea: {_q(served['idea'])}")
        if served.get("gate"):
            lines.append(f"- Gate: {_q(served['gate'])}")
        for part in served.get("parts") or []:
            lines.append(f"- Part {part.get('part')}:")
            for n, item in enumerate(part.get("items") or [], start=1):
                lines.append(f"  {n}. **{item.get('question')}** ({item.get('dimension')}, {item.get('control')})")
                opts = item.get("options") or item.get("advantages") or []
                if opts:
                    lines.append("     options: " + " | ".join(str(o) for o in opts))
                if item.get("escape"):
                    lines.append(f"     escape: {item['escape']}")
        if served.get("reveal"):
            lines.append(f"- Reveal: {_q(served['reveal'])}")
        lines.append("- Screens: " + ", ".join(f"`{f}`" for f in v.get("screens") or []))
        lines.append("")
    lines += ["## 3. The brief", "", f"- Decision: {_q(decision)}", f"- Verdicts: {_q(b.get('verdicts'))}", ""]
    for card in b.get("cards") or []:
        lines.append(f"- **{card.get('name')}** {card.get('number')} -- {card.get('line')} -- {card.get('statusWords')}"
                     + (f" (Keel's bar: {card['keelBar']})" if card.get("keelBar") else ""))
    lines.append("")
    for vector, stage in (b.get("stages") or {}).items():
        lines.append(f"- {vector}: broke {_q(stage.get('broke'))}; not asked {_q(stage.get('notAsked'))}")
    lines += ["", "### Insights", ""]
    for i in b.get("insights") or []:
        lines.append(f"- **{i.get('name')}** ({i.get('status')}; against {i.get('against')}, asked {i.get('asked')}, "
                     f"answered {i.get('answered')}) {i.get('rungHeading') or i.get('noQuestionWhy') or ''}")
        for t in i.get("themes") or []:
            lines.append(f"  - {t.get('label')} ({t.get('count')})")
            for q in t.get("evidence") or []:
                lines.append(f"    - {q.get('name')}: \"{q.get('text')}\"")
        for q in i.get("rawQuotes") or []:
            lines.append(f"  - (raw) {q.get('name')}: \"{q.get('text')}\"")
    lines += ["", f"- Pilot: {_q(b.get('pilot'))}", f"- Price: {_q(b.get('price'))}", ""]
    lines += ["## 4. Readings: the model's anchoring beside the file's", "",
              "| Person | Link | Gate | File | Model | Same |", "|---|---|---|---|---|---|"]
    for row in r.get("readings") or []:
        lines.append(f"| {row.get('person')} | {row.get('link')} | {_q(row.get('gate'))} | {_q(row.get('file anchoring'))}"
                     f" | {_q(row.get('model anchoring'))} | {_q(row.get('same'))} |")
    lines += ["", "## 5. Cost and time", "",
              f"- Summed: {c.get('micro_usd')} micro-USD (${c.get('usd')}), {c.get('jobs')} jobs, hosts {_q(c.get('hosts'))}",
              f"- Models: {_q(c.get('models'))}"]
    for name, k in (c.get("by_class") or {}).items():
        lines.append(f"- {name}: {k.get('jobs')} jobs, ${k.get('usd')}, {_q(k.get('models'))}")
    if c.get("not settled"):
        lines.append(f"- Not settled: {_q(c.get('not settled'))}")
    lines.append(f"- {c.get('not on the wire', '')}")
    lines += ["", f"Wall time {r.get('wall_s')} s:"]
    for leg in r.get("legs") or []:
        lines.append(f"- {leg.get('leg')}: {leg.get('seconds')} s")
    if r.get("transcript_error"):
        lines += ["", f"Transcript error: {r['transcript_error']}"]
    return "\n".join(lines) + "\n"
