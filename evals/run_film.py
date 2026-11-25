"""Spec 163 FR-2: the film leg of `make film-walk` -- one entry's problem film told, built and captured on the stack.

**Not a scenario, and never collected by a directory run** (not `test_*.py`: `make eval`, `make unit` and the matrix
never collect it; `quality/film.py` names it on pytest's command line through `make film-leg`).

For one entry (`KEEL_FILM_ENTRY`) on one door (`KEEL_FILM_DOOR`):

* **keel** (PAID, the founder's word): the stack booted from this shell -- `KEEL_ANTHROPIC_API_KEY` (Keel's AI reads
  every beat), `KEEL_OPENAI_API_KEY` and `KEEL_PICTURES=openai` (keel-cloud 273 draws the real pictures; the clips are
  the real voice) -- refused when a stack already answers (it was not booted with the keys), as `make backtest`
  refuses; a founder outside `fake-for` signs up on Keel's AI; the seven beats are told **in the entry's own words**
  (`film_frames.entry_beats`) on the wire as keel-web 257's page sends them (`StoryWire`).
* **fake** (free, the local walk of FR-7): the stack as it stands or booted (`KEEL_PICTURES` must not be `openai`),
  a founder inside `fake-for`: keel-cloud's fakes answer -- `FakeStoryReadings` reads the beats from its own script
  (so the script's own words are told: the film is the script's story, the entry names the bundle and the persona
  card alone), `FakePictures` draws each picture as a 48 x 32 PNG from its prompt's hash.

Then, either door: a PROBLEM project (`POST /v2/projects`), the beats, the boxes' yes (`story/confirm`), the build
waited for, and **the film captured before any stranger sees it** (`film_frames.FilmCamera`: fourteen frames, the
story, the pictures, the setting and the prompts, the ledger's rows) into `KEEL_FILM_OUT/film/<entry>/` (the walk's
bundle), with its own evidence (transcript, screenshots) in `runs/<stamp>-film-<entry>/`.

**Spec 165: then the strangers on the film's link, on the same project** (`harness/film_strangers.py`; 163's
judgement call 1 closed -- no second, typed project is made): the project locked (the window, the calibration, the
credits, the ready page's lock, the questions READY; a step that does not hold fails the leg by name), its link sent
to the entry's first `KEEL_FILM_PEOPLE` people (`quality/cycle.toml`'s seven; the PROBLEM scope's own-link people in
corpus order), each walking the film link on the orb with their recorded answers mapped onto the four questions, then
the founder's page read after them (§B's screens, spec 164's reads) and the bundle `make read-screens` reads written
as `backtest.json` (`kind: "film"`) in the evidence folder, named in `film.json` (`screens_bundle`). `KEEL_FILM_TYPOS=1`
types the founder's beats with a person's typos on Keel's door (spec 126's typist; the fakes tell their own script).

**Spec 166: then the solution half, on a project made from the problem's** (`KEEL_FILM_SCOPES` naming SOLUTION, the
walk's `[film] scopes`): a SOLUTION project created on the problem's (`parentProjectId`, by the same founder, as the
product's *A new solution* does), the problem's film stamped as played, the brand typed and the four beats told
(`film_frames.entry_idea_beats`: the entry's words on Keel's door, typed with typos on `KEEL_FILM_TYPOS=1`; the fakes'
idea script on the fakes), the board's yes, the build (keel-cloud reusing the problem film's character sheet), **the
solution film captured before any stranger sees it** (`FilmCamera(kind="solution")`: the plate, up to eleven scenes on
both viewports, the pictures and the sheet, the plan and the reviews) into `KEEL_FILM_OUT/film/<entry>/solution/`
(`film.json` `kind: "solution"`), the pilot ask answered yes; then the lock on SOLUTION, the entry's people of the
SOLUTION scope on its link (the three yes-or-no questions, the whys) and the founder's page after them, the bundle
`backtest.json` (`kind: "film-solution"`) in `runs/<stamp>-film-<entry>-solution/`. `KEEL_FILM_ONLY=solution` walks
that half alone on the stack that holds the walk's problem project (`film/<entry>/film.json`'s project and founder),
attaching to it; `KEEL_FILM_KEEP=1` leaves a stack the leg booted standing (one entry), so such a half can follow.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from harness import film_frames as ff
from harness import film_strangers as fs
from harness import story_screens as ss
from harness.browser import Auth
from harness.steps import Recorder
from stack import ledger
from stack import remote
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown

ENTRY_VAR, DOOR_VAR, OUT_VAR = "KEEL_FILM_ENTRY", "KEEL_FILM_DOOR", "KEEL_FILM_OUT"
#: Spec 165: how many of the entry's people answer on the film's link (`quality/cycle.toml`'s `people` when unsaid),
#: and whether the founder's beats are typed with typos (Keel's door alone).
PEOPLE_VAR, TYPOS_VAR = "KEEL_FILM_PEOPLE", "KEEL_FILM_TYPOS"
#: Spec 166 FR-7: the halves the leg walks (`PROBLEM`, `SOLUTION`; the walk's `[film] scopes` / `SCOPES=`), the half it
#: walks alone (`solution`, on the stack holding the walk's problem project) and whether a stack it booted stays up.
SCOPES_VAR, ONLY_VAR, KEEP_VAR = "KEEL_FILM_SCOPES", "KEEL_FILM_ONLY", "KEEL_FILM_KEEP"
#: Spec 165: the stand-in that tops a short balance to the grant before the lock (as `three_views.fr1_d` does).
STAND_IN_SPEC = "165"
DOORS = ("keel", "fake")
KEYS = ("KEEL_ANTHROPIC_API_KEY", "KEEL_OPENAI_API_KEY")
#: Outside keel-cloud's `fake-for` (the eval stack's default lists `keel-e2e-eval.test`): Keel's AI and the pictures.
PAID_DOMAIN = "keel-backtest.test"
FAKE_DOMAIN = "keel-e2e-eval.test"

ENTRY = (os.environ.get(ENTRY_VAR) or "").strip()
DOOR = (os.environ.get(DOOR_VAR) or "keel").strip().lower()

pytestmark = pytest.mark.live


def refusal(env: dict | None = None) -> str | None:
    """One sentence where the leg cannot run as asked, else None. Reads presence only: no key is logged or echoed."""
    env = os.environ if env is None else env
    door = (env.get(DOOR_VAR) or "keel").strip().lower()
    if door not in DOORS:
        return f"make film-leg refuses: DOOR={door} -- `keel` (paid: Keel's AI and the real pictures) or `fake` (free)"
    if not (env.get(ENTRY_VAR) or "").strip():
        return "make film-leg refuses: no ENTRY -- name a back-test entry (keel-cloud canon/designs/measured-beliefs/backtest)"
    if not (env.get(OUT_VAR) or "").strip():
        return "make film-leg refuses: no OUT -- the walk's bundle the film is written into (`make film-walk` names it)"
    if door == "keel":
        missing = [k for k in KEYS if not (env.get(k) or "").strip()]
        if missing:
            return (f"make film-leg refuses: {', '.join(missing)} not set in this shell -- DOOR=keel reads every beat on "
                    "Keel's AI and draws the real pictures (keel-cloud 273's `openai` port); never logged or echoed")
        if (env.get("KEEL_PICTURES") or "").strip().lower() != "openai":
            return ("make film-leg refuses: KEEL_PICTURES is not `openai` -- DOOR=keel films the real pictures "
                    "(keel-cloud 273 `keel.v2.pictures.adapter`); `DOOR=fake` films FakePictures for free")
    elif (env.get("KEEL_PICTURES") or "").strip().lower() == "openai":
        return "make film-leg refuses: DOOR=fake with KEEL_PICTURES=openai -- the free walk never draws a paid picture"
    return None


def scopes(env: dict | None = None) -> list[str]:
    """Spec 166 FR-7: the halves walked -- `KEEL_FILM_SCOPES` (comma-separated), else `quality/cycle.toml` `[film] scopes`."""
    env = os.environ if env is None else env
    raw = (env.get(SCOPES_VAR) or "").strip()
    if raw:
        return [x.strip().upper() for x in raw.split(",") if x.strip()]
    from quality import film_table as ft                                   # noqa: PLC0415
    return list(ft.load_film_config()["scopes"])


def only(env: dict | None = None) -> str | None:
    env = os.environ if env is None else env
    return (env.get(ONLY_VAR) or "").strip().lower() or None


def keep(env: dict | None = None) -> bool:
    env = os.environ if env is None else env
    return (env.get(KEEP_VAR) or "").strip().lower() in ("1", "on", "true", "yes")


def people_cap(env: dict | None = None) -> int:
    """Spec 165: the people sent on the film's link -- `KEEL_FILM_PEOPLE`, else `quality/cycle.toml`'s `people`."""
    env = os.environ if env is None else env
    raw = (env.get(PEOPLE_VAR) or "").strip()
    if raw:
        return int(raw)
    from quality import cycle as cyc                                       # noqa: PLC0415
    return int(cyc.resolve_people(None, cyc.load_config()) or 7)


def typos_on(env: dict | None = None) -> bool:
    env = os.environ if env is None else env
    return (env.get(TYPOS_VAR) or "").strip().lower() in ("1", "on", "true", "yes")


@pytest.fixture(scope="session")
def stack(stack_config):
    """DOOR=keel: refused when a stack answers (not booted with the keys), else booted from this shell and torn down.
    DOOR=fake: attached as it stands, or booted and torn down (the eval profile's rule)."""
    said = refusal()
    if said:
        pytest.exit(said, returncode=2)
    if stack_config.is_remote:
        pytest.exit("make film-leg refuses: the film is walked on the local eval stack only", returncode=2)
    up = quick_gates_pass(stack_config)
    if only() == "solution":
        # spec 166 FR-7: the solution half alone, on the stack that holds the walk's problem project -- never booted here
        # (a stack brought up again starts empty: `docker compose down -v`)
        if not up:
            pytest.exit("make film-leg refuses: ONLY=solution walks on the stack that holds the walk's problem project, "
                        "and none answers on the eval ports -- walk both halves again (ONLY= unset)", returncode=2)
        yield stack_config
        return
    if up and DOOR == "keel":
        pytest.exit("make film-leg refuses: a stack already answers on the eval ports and was not booted from this shell "
                    "with the keys -- `make down` first (DOOR=keel brings its own stack up and down)", returncode=2)
    if not up:
        boot(stack_config)
    try:
        yield stack_config
    finally:
        if not up and not keep():
            stack_teardown(stack_config)


def _entry_yaml(stack) -> tuple[dict, Path]:
    import hashlib                                                         # noqa: PLC0415

    import yaml                                                            # noqa: PLC0415
    from instructions import corpus as corpus_mod                         # noqa: PLC0415
    path = corpus_mod.backtest_dir(stack.keel_cloud) / f"{ENTRY}.yaml"
    if not path.is_file():
        pytest.exit(f"make film-leg refuses: no back-test entry {ENTRY} at {path}", returncode=2)
    raw = path.read_bytes()
    return {"yaml": yaml.safe_load(raw) or {}, "sha256": hashlib.sha256(raw).hexdigest()}, path


@pytest.mark.bundle(f"film-{ENTRY or 'none'}")
def test_film_leg(stack, browser, run_dir):
    entry, entry_path = _entry_yaml(stack)
    out = Path(os.environ[OUT_VAR]) / ff.FILM_DIR / ENTRY
    out.mkdir(parents=True, exist_ok=True)
    recorder = Recorder(run_dir)
    stamp = time.strftime("%H%M%S", time.gmtime())
    domain = PAID_DOMAIN if DOOR == "keel" else FAKE_DOMAIN
    halves = scopes()
    alone = only()
    # spec 166 FR-7: ONLY=solution -- the problem half recorded in this walk (its project, its founder) is reused
    kept_problem = _problem_record(out) if alone == "solution" else {}
    again = _stub_founder(kept_problem) if alone == "solution" else None
    own_ai = None
    if DOOR == "fake":
        # spec 165 (judgement call 1): the free walk's founder is on her own AI through the code story, the scripted
        # runtime answering every job (as e2e-157's founder is) -- this stack has no key, so Keel's door answers only
        # the story's readings, the pictures, the voice and the transcriber (`fake-for`), never the calibration, the
        # questions, the readings of the stories or the groupings the people's answers need
        from evals import three_views as tv                                # noqa: PLC0415
        own_ai = tv.Run(stack, browser, recorder, run_dir)
        own_ai.open(founder=again)
        founder, context, page = own_ai.founder, own_ai.context, own_ai.page
    else:
        founder = again or remote.register_cell_identity(
            stack, f"film · {ENTRY} · {time.strftime('%Y-%m-%d', time.gmtime())}", name=f"Film Founder {stamp}",
            id=f"film-{ff.safe_name(ENTRY)}-{stamp}", email=f"film-{ff.safe_name(ENTRY)}-{stamp}@{domain}")
        context = browser.new_context()
        page = context.new_page()
    cloud = stack.cloud_base_url.rstrip("/")

    def call(method: str, path: str, body: dict | None = None):
        kwargs: dict = {"timeout": 60_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = context.request.fetch(f"{cloud}{path}", method=method, **kwargs)
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001 - an empty body
            payload = response.text()
        return response.status, payload

    def get_bytes(path: str):
        response = context.request.get(f"{cloud}{path}", timeout=60_000)
        return response.status, response.body(), response.headers.get("content-type")

    owed: list[str] = []                                 # every half's failures, asserted once both are written
    try:
        if own_ai is None:
            auth = Auth(page, recorder, stack.web_base_url)
            auth.sign_in(founder) if again else auth.sign_up(founder)
        versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8")) \
            if (run_dir / "versions.json").is_file() else {}
        if alone == "solution":
            project_id = kept_problem["project_id"]
            status, story = call("GET", f"/v2/projects/{project_id}/story")
            state = ((story or {}).get("build") or {}).get("state") if isinstance(story, dict) else None
            with recorder.step(f"spec 166: ONLY=solution -- the walk's problem project {project_id} on this stack, the "
                               "same founder", party="founder", kind="assert") as h:
                h.record_assert({"status": 200, "build": "ready"}, {"status": status, "build": state})
                assert status == 200 and state == "ready", (
                    f"make film-leg refuses: the walk's problem project {project_id} is not on this stack with its film "
                    f"(GET story {status}, build {state}) -- a stack brought up again starts empty; walk both halves "
                    "again (ONLY= unset)")
            strangers_ok = True
        else:
            project_id, story, state, strangers_ok = problem_half(
                stack, browser, recorder, context, page, run_dir, founder, entry, entry_path, out, call, get_bytes,
                versions, stamp, own_ai=own_ai, owed=owed)
        if "SOLUTION" in halves and state == "ready":
            solution = solution_half(stack, browser, recorder, context, page, run_dir, founder, entry, entry_path,
                                     project_id, story, versions, stamp, call, get_bytes, own_ai=own_ai)
            owed += solution_owed(solution)
        elif "SOLUTION" in halves:
            owed.append(f"spec 166: the solution half was not walked -- the problem's build ended {state!r}")
    finally:
        if own_ai is not None:
            from harness.connect import stop_runtime                       # noqa: PLC0415
            try:
                own_ai.close()
            finally:
                stop_runtime(stack, recorder)                              # the runtime this leg started
        else:
            context.close()
    assert not owed, "; ".join(owed)


def _problem_record(out: Path) -> dict:
    """Spec 166 FR-7: the problem half this walk recorded for the entry (`film/<entry>/film.json`): its project and the
    founder who told it -- refused by name where there is none."""
    path = Path(out) / "film.json"
    try:
        film = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pytest.exit(f"make film-leg refuses: ONLY=solution and no problem half recorded at {path} -- name the walk whose "
                    "problem leg this entry walked (RUN=)", returncode=2)
    if not film.get("project_id") or not (film.get("founder") or {}).get("id"):
        pytest.exit(f"make film-leg refuses: ONLY=solution and {path} names no problem project or no founder (a walk "
                    "before spec 166) -- walk both halves again", returncode=2)
    return film


def _stub_founder(film: dict):
    from stack.auth import StubFounder                                     # noqa: PLC0415
    f = film.get("founder") or {}
    return StubFounder(id=f["id"], sub=f["sub"], email=f["email"], name=f["name"])


def founder_record(founder) -> dict:
    """The founder who told the problem (spec 166 FR-7: `ONLY=solution` signs in as them again)."""
    return {k: getattr(founder, k, None) for k in ("id", "sub", "email", "name")}


def problem_half(stack, browser, recorder, context, page, run_dir: Path, founder, entry: dict, entry_path: Path,
                 out: Path, call, get_bytes, versions: dict, stamp: str, *, own_ai=None, owed: list) \
        -> tuple[str, dict, str | None, bool]:
    """Specs 163 and 165, unchanged: the PROBLEM project, the seven beats, the build, the film captured, then the
    strangers on its link and the founder's page after them. Returns `(project, the served story, the build's state,
    whether the strangers' leg held)`; what did not hold is added to `owed`."""
    status, me = call("GET", "/v2/me")
    market = {"country": str(((entry["yaml"].get("market") or {}).get("country")) or "US")}
    with recorder.step(f"spec 163: a PROBLEM project for {ENTRY} ({DOOR} door)", party="founder", kind="assert") as h:
        status, created = call("POST", "/v2/projects", {"name": f"163 film {ENTRY} {stamp}", "scope": "PROBLEM",
                                                        "market": market})
        h.record_assert({"status": 201}, {"status": status, "me": {k: (me or {}).get(k) for k in ("aiPath",)}})
        assert status < 300 and isinstance(created, dict) and created.get("projectId"), (status, created)
    project_id = created["projectId"]
    wire = ss.StoryWire(call, project_id)
    typed: list = []
    if DOOR == "keel":
        beats = ff.entry_beats(entry["yaml"])
        telling = "the entry's own words"
        if typos_on():
            # spec 165 (TYPOS=1 on the founder's words, as the quality walk types them): spec 126's typist
            beats, typed = fs.typed_beats(beats, _vs_entry(stack, 1), seed=ENTRY)
            telling += f", typed with {len(typed)} typo(s)"
    else:
        beats = list(ss.said_turns(ss.fake_readings(stack.keel_cloud)))
        telling = "keel-cloud's fake readings script (FakeStoryReadings) -- not the entry's words"
    with recorder.step(f"spec 163: the seven beats told on the wire ({telling})", party="founder") as h:
        told = wire.tell(beats)
        h.record_wire({"beats": [n for n, _ in beats]}, {"next": [b.get("next") for b in told]})
    confirmed = wire.confirm()
    with recorder.step("spec 163: the boxes' yes, then the build (the pictures, the clips)", party="founder",
                       kind="assert") as h:
        story = ff.wait_built(wire.story, timeout_s=600 if DOOR == "keel" else 180)
        state = (story.get("build") or {}).get("state")
        h.record_assert({"confirm": 200, "build": "ready"}, {"confirm": confirmed.get("status"), "build": state,
                                                             "failedScene": (story.get("build") or {}).get("failedScene")})
    faults = ff.chapter_faults(story) if state == "ready" else [
        {"what": f"the build ended {state!r} (failedScene {(story.get('build') or {}).get('failedScene')}: "
                 f"{(story.get('build') or {}).get('failedLine')})", "owed": "keel-cloud 273 FR-3",
         "detail": json.dumps((story.get("build") or {}).get("checked"))[:300], "frame": None}]
    frames, pictures = [], []
    if state == "ready":
        camera = ff.FilmCamera(browser, context.storage_state(), stack.web_base_url, out)
        with recorder.step("spec 163: the film captured -- each scene held, the phone and the laptop",
                           party="founder") as h:
            frames, shot_faults = camera.shoot(project_id, story)
            faults += shot_faults
            h.record_wire({"frames": len(frames)}, {"faults": [f["what"] for f in shot_faults]})
        pictures = ff.fetch_pictures(get_bytes, story, out)
        faults += ff.picture_faults(pictures)
    try:
        account = ledger.founder_account(stack, founder.sub)
        spent = ff.ledger_rows(ledger.rows(stack, account["id"]), project_id)
    except ledger.LedgerUnavailable as e:
        spent = {"rows": [], "unread": str(e)[:200], "usd": None}
    # spec 165: the strangers on the film's link, on this project -- the lock, the people, the founder's page after
    strangers, refused = None, None
    if state == "ready":
        strangers, refused = strangers_leg(stack, browser, recorder, context, page, run_dir, founder, entry,
                                           entry_path, project_id, versions, stamp, typed, own_ai=own_ai)
    film = {
        "spec": "163", "entry": {"id": ENTRY, "path": str(entry_path), "sha256": entry["sha256"]},
        "door": DOOR, "telling": telling, "project_id": project_id,
        "stack": {"keel-cloud": ((versions.get("keel-cloud") or {}).get("commit") or "")[:8],
                  "keel-web": ((versions.get("keel-web") or {}).get("commit") or "")[:8]},
        "pictures_adapter": os.environ.get("KEEL_PICTURES") or "fake",
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "evidence": str(run_dir),
        "build_state": state, "lines": ff.lines_of(story), "frames": frames,
        "pictures": [p for p in pictures if p.get("path")], "pictures_served": pictures,
        "beats": ff.beats_record(told, dict(beats)), "verdict_line": story.get("verdictLine"),
        "ledger": spent, "dollars": spent.get("usd"),
        "measures": {"faults": faults, "frames": len(frames), "pictures": sum(1 for p in pictures if p.get("path"))},
        # spec 165: the one project the strangers answered on, and the bundle read-screens reads
        "screens_bundle": str(run_dir) if strangers else None,
        "strangers": strangers, **({"refused": refused} if refused else {}),
        **({"typos": typed} if typed else {}),
        # spec 166 FR-7: the founder who told it (`ONLY=solution` signs in as them again on the same stack)
        "founder": founder_record(founder),
    }
    ff.write_folder(out, story=story, film=film)
    print(f"\nfilm: {out} -- {len(frames)} frames, {film['measures']['pictures']} pictures, build {state}, "
          f"{len(faults)} capture fault(s)")
    if strangers:
        print(f"strangers: {strangers['answered']} of {strangers['people']} answered on the film's link "
              f"(project {project_id}); {len(strangers['after_screens'])} screen(s) after the answers; "
              f"read-screens bundle {run_dir}")
    if state != "ready":
        owed.append(f"the build ended {state}")
    elif len(frames) != 2 * ff.SCENES:
        owed.append(f"{len(frames)} frames of {2 * ff.SCENES}: {[f['what'] for f in faults]}")
    if refused:
        owed.append(str(refused))
    elif state == "ready" and not (strangers and strangers["answered"] == strangers["people"]):
        owed.append(f"spec 165: {strangers and strangers['answered']} of {strangers and strangers['people']} people "
                    f"answered on the film's link: {[(w['person'], w.get('error'), w['response']) for w in (strangers or {}).get('walks') or []]}")
    elif state == "ready" and not strangers["after_screens"]:
        owed.append("spec 165: the founder's page shot nothing after the answers")
    return project_id, story, state, bool(strangers) and not refused



def _vs_entry(stack, cap: int, scope: str = fs.SCOPE):
    """The entry as `vectors_script` reads it, under `scope` (the PROBLEM scope; spec 166 the SOLUTION one) and the walk's
    cap (spec 106's `people_cap`)."""
    import dataclasses                                                     # noqa: PLC0415

    from harness import vectors_script as vs                               # noqa: PLC0415
    _, read = vs.entry_for(stack.keel_cloud, ENTRY, backtest=True)
    return dataclasses.replace(read, scope=scope, people_cap=int(cap))


def strangers_leg(stack, browser, recorder, context, page, run_dir: Path, founder, entry: dict, entry_path: Path,
                  project_id: str, versions: dict, stamp: str, typed: list, *, own_ai=None
                  ) -> tuple[dict | None, str | None]:
    """Spec 165 FR-1, FR-2 on the stack: the film's project locked, the people on its link, the founder's page after
    them, `backtest.json` written. Returns `(the strangers' record, None)` or `(None, the refusal naming the step)`.
    `own_ai` (the free walk, a `three_views.Run`): the founder's scripted runtime -- the lock bought on Keel's door by
    a stand-in and the questions written on her own (`three_views.lock_once`'s way), the stories read ANCHORED, the
    groupings handed after the answers."""
    from evals import three_views as tv                                    # noqa: PLC0415
    from harness import three_surfaces as ts                               # noqa: PLC0415
    from harness import vectors_script as vs                               # noqa: PLC0415
    run = own_ai or fs.FilmRun(stack=stack, browser=browser, recorder=recorder, context=context, page=page, stamp=stamp)
    cap = people_cap()

    def top_up():
        account = ledger.founder_account(stack, founder.sub)
        return ledger.stand_in_balance(stack, account["id"], f"film-{stamp}", to=ledger.GRANT_CREDITS,
                                       spec=STAND_IN_SPEC, label="topped",
                                       what="the balance topped to the grant to see the film's project locked")

    press = fs.press_on_the_ready_page(run, project_id)
    if own_ai is not None:
        own_ai.load_runtime("PROBLEM")
        pressed_on_keels_door = press

        def press():
            # the lock bought on Keel's door (a stand-in grant, `three_views.lock_once`), the door given back after:
            # the questions are written on her own door (`lock_project` retries a FAILED set once)
            account = own_ai.account_id
            ledger.stand_in_keels_door(stack, account, f"{project_id[:8]}-door-{stamp}", spec=STAND_IN_SPEC)
            try:
                return pressed_on_keels_door()
            finally:
                ledger.restore_own_door(stack, account, f"{project_id[:8]}-restore-{stamp}", spec=STAND_IN_SPEC)

    with recorder.step("spec 165: the film's project locked -- the window, the calibration, the credits, the ready "
                       "page's lock, the questions READY", party="founder", kind="assert") as h:
        try:
            # the entry's window on Keel's door; the free walk tells the fake script, whose window is the default
            lock = fs.lock_project(run.call, project_id,
                                   window=fs.recall_window(entry["yaml"] if own_ai is None else {}),
                                   press=press, need=0 if own_ai is not None else tv.PROJECT_PRICE, top_up=top_up)
        except fs.LockFailed as failed:
            h.record_assert({"locked": True}, {"locked": False, "step": failed.step, "detail": failed.detail})
            return None, str(failed)
        h.record_assert({"locked": True}, {"locked": True, **lock})
    plans = fs.people_plans(vs.person_inputs(_vs_entry(stack, cap)))
    kept: dict = {}
    if own_ai is not None:
        own_ai.load_runtime("PROBLEM", extra={"INTERPRET": [ts.ANCHORED] * max(12, 2 * len(plans))})
    with recorder.step(f"spec 165: the film's link sent to {len(plans)} people, each walking the four questions",
                       party="participant", kind="assert") as h:
        walks = fs.walk_people(run, project_id, plans, out=kept)
        h.record_assert({"answered": len(plans)}, {"answered": sum(1 for w in walks if w["response"]["status"] == 201
                                                                   and w["done"]),
                                                   "walks": [{k: w.get(k) for k in ("person", "steps", "whys",
                                                                                     "response", "error")}
                                                             for w in walks]})
    with recorder.step("spec 165: the founder's page after the answers -- the stage page, the cards, Insights, the "
                       "ways, the brief", party="founder") as h:
        handed = None
        if own_ai is not None:
            def handed():
                said = fs.said_by_rung(kept.get("walked") or {})
                own_ai.load_runtime("PROBLEM", extra={
                    "THEMES": fs.themes_script(said),
                    "EXPERIENCE_WAYS": [fs.ways_script(fs.stories_told(walks, kept.get("walked") or {}),
                                                       (own_ai.get(f"/v2/projects/{project_id}/story") or {}).get("act"))],
                    "INTERPRET": [ts.ANCHORED] * max(12, 2 * len(plans))})
        after = fs.founder_page_after(run, project_id, run_dir, before_settle=handed)
        h.record_wire({"after": "the answers leg and spec 164's reads"},
                      {"screens": len(after["after_screens"]), "checks": after["founder_page"]["checks"]})
    who = fs.watched(plans)
    respondents = fs.respondents_record(who, (kept.get("interviews") or {}).get(who),
                                        (kept.get("walked") or {}).get(who))
    commits = {name: ((versions.get(name) or {}).get("commit") or "") for name in ("keel-cloud", "keel-web")}
    bundle = fs.screens_bundle(
        entry={"id": ENTRY, "title": entry["yaml"].get("title"), "path": str(entry_path), "sha256": entry["sha256"]},
        project_id=project_id, door=DOOR, stack=commits, people=cap, lock=lock, plans=plans, walks=walks,
        respondents=respondents, after_screens=after["after_screens"], answers_leg=after["answers_leg"],
        brief=after["brief"], themes_settled=after["themes_settled"], founder_page=after["founder_page"],
        run=run_dir.name, typos=typed)
    (run_dir / "backtest.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False, default=str) + "\n",
                                           encoding="utf-8")
    return {"project_id": project_id, "people": len(plans), "watched": who,
            "answered": sum(1 for w in walks if w["response"]["status"] == 201 and w["done"]),
            "walks": walks, "lock": lock, "after_screens": [s.get("screen") for s in after["after_screens"]],
            "founder_page": after["founder_page"]["checks"]}, None


# ------------------------------------------------------------------------------------------------ spec 166: the solution

#: Spec 166 FR-1: the solution's evidence folder beside the leg's (`runs/<stamp>-film-<entry>-solution/`), the bundle
#: `make read-screens` reads for the solution's project.
SOLUTION_SUFFIX = "-solution"


def solution_words(stack, entry: dict, problem_story: dict) -> dict:
    """What the founder says on the solution half: on Keel's door the entry's words (`film_frames.entry_idea_beats`),
    typed with typos on `TYPOS=1` (the brand typed exactly: a typed page); on the fakes keel-cloud's idea script
    (`FakeStoryReadings` answers its own words alone) under the brand it is told with -- the plainest telling (beat 2
    none, beat 3's unmatched limitation matched by its correction), as spec 162's `plain`."""
    composed = ff.entry_idea_beats(entry["yaml"], problem_story)
    if DOOR == "keel":
        beats, then, typed = list(composed["beats"]), {n: list(w) for n, w in composed["then"].items()}, []
        telling = "the entry's own words (film_frames.entry_idea_beats)"
        if typos_on():
            vs_entry = _vs_entry(stack, 1)
            beats, typed = fs.typed_beats(beats, vs_entry, seed=f"{ENTRY}:idea")
            for n, words in list(then.items()):
                said, slips = fs.typed_beats([(n, w) for w in words], vs_entry, seed=f"{ENTRY}:idea-then")
                then[n] = [w for _, w in said]
                typed += [{**slip, "field": f"then-{slip['field']}"} for slip in slips]
            typed = [{**slip, "field": f"idea-{slip['field']}"} for slip in typed]
            telling += f", typed with {len(typed)} typo(s)"
        return {"brand": composed["brand"], "beats": beats, "then": then, "telling": telling, "typed": typed,
                "composed": composed}
    script = ss.idea_scripts(ss.fake_readings(stack.keel_cloud))
    return {"brand": {"name": ss.IDEA_NAME, "tagline": ss.IDEA_TAGLINE, "colour": ss.IDEA_COLOUR},
            "beats": [(1, script["workflow"]), (2, script["setup_none"]), (3, script["limits"]), (4, script["joy"])],
            "then": {1: [script["first_step"]] if script.get("first_step") else [], 3: [script["match"]],
                     4: [script["joy"]]},
            "telling": "keel-cloud's fake idea script (FakeStoryReadings) -- not the entry's words", "typed": [],
            "composed": composed}


def idea_questions(entry: dict, problem_story: dict, name: str) -> dict[int, str]:
    """keel-cloud 271's four questions as the founder hears them (`story_screens.idea_question`, the story's people, its
    job, its limitations and its cost filled) -- what the founder-reader reads beside the founder's words."""
    person = problem_story.get("person") or {}
    actor = ((entry["yaml"].get("context") or {}).get("actor")) or person.get("who")
    return {n: ss.idea_question(n, name=name, person=actor, people=person.get("who"), job=person.get("job"),
                                limits=list(problem_story.get("limits") or []), cost=problem_story.get("cost"))
            for n in ss.IDEA_BEATS}


def idea_beats_record(told: list[dict], said: dict[int, str], asked: dict[int, str]) -> list[dict]:
    """What Keel said to the founder on each of the four beats, off the wire (`IdeaWire.tell`): the question, the
    founder's words, the ask and the readback served (the last answer's)."""
    out = []
    for b in told:
        n = b.get("turn")
        answers = b.get("answers") or [{}]
        ask = next((a.get("ask") for a in answers if a.get("ask")), None)
        if ask is None and len(answers) > 1:
            ask = answers[0].get("readback")          # beat 3's unmatched limitation: its readback asks
        out.append({"turn": n, "asked": asked.get(n), "founder": said.get(n), "ask": ask,
                    "readback": answers[-1].get("readback"), "status": answers[-1].get("status")})
    return out


def solution_half(stack, browser, recorder, context, page, run_dir: Path, founder, entry: dict, entry_path: Path,
                  problem_id: str, problem_story: dict, versions: dict, stamp: str, call, get_bytes, *,
                  own_ai=None) -> dict:
    """Spec 166 FR-1 to FR-3 on the stack: the SOLUTION project made on the problem's, the founder's solution told, the
    build, the solution film captured, the pilot's yes, then the strangers on its link and the founder's page after
    them; `film/<entry>/solution/` written. Returns the solution film's record."""
    out = ff.film_dir(Path(os.environ[OUT_VAR]), ENTRY, "solution")
    out.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    market = {"country": str(((entry["yaml"].get("market") or {}).get("country")) or "US")}
    if own_ai is not None:
        own_ai.load_runtime("SOLUTION")            # her own AI writes the solution's chain and questions (spec 162)
    with recorder.step(f"spec 166: a SOLUTION project made on the problem's ({problem_id}, parentProjectId), by the "
                       "same founder", party="founder", kind="assert") as h:
        request = {"name": f"166 solution {ENTRY} {stamp}", "scope": "SOLUTION", "market": market,
                   "parentProjectId": problem_id}
        status, created = call("POST", "/v2/projects", request)
        lineage = (created or {}).get("lineage") if isinstance(created, dict) else None
        h.record_assert({"status": 201, "lineage.problemProjectId": problem_id},
                        {"status": status, "lineage": lineage})
        assert status < 300 and isinstance(created, dict) and created.get("projectId"), (status, created)
    solution = created["projectId"]
    wire = ss.IdeaWire(call, solution)
    words = solution_words(stack, entry, problem_story)
    brand = words["brand"]
    with recorder.step(f"spec 166: the problem's film stamped as played, the brand typed ({brand['name']}), the four "
                       f"beats told on the wire ({words['telling']})", party="founder") as h:
        stamped = wire.stamp()
        branded = wire.brand(name=brand["name"], colour=brand.get("colour"), tagline=brand.get("tagline"))
        assert (branded.get("status") or 500) < 300, f"the brand refused: {branded}"
        told = wire.tell(words["beats"], words["then"])
        h.record_wire({"stamp": stamped.get("status"), "brand": branded.get("status"),
                       "beats": [n for n, _ in words["beats"]]},
                      {"next": [b.get("next") for b in told],
                       "asks": {b["turn"]: [a.get("ask") or a.get("readback") for a in b["answers"][:-1]]
                                for b in told}})
    confirmed = wire.confirm()
    with recorder.step("spec 166: the board's yes, then the build (the plate, the pictures on the problem's sheet, the "
                       "clips)", party="founder", kind="assert") as h:
        view = wire.built(timeout_s=900 if DOOR == "keel" else 240)
        build = view.get("build") or {}
        state = build.get("state")
        h.record_assert({"confirm": 200, "build": "ready"},
                        {"confirm": confirmed.get("status"), "build": state,
                         **{k: build.get(k) for k in ("failedChapter", "failedScene", "failedReason")}})
    to_film_s = round(time.monotonic() - began, 1)
    faults = ff.idea_chapter_faults(view) if state == "ready" else [
        {"what": f"the solution's build ended {state!r} (failedChapter {build.get('failedChapter')}, failedScene "
                 f"{build.get('failedScene')}: {build.get('failedReason') or build.get('failedLine')})",
         "owed": "keel-cloud 271 FR-10 / 273 FR-3 / 275 FR-2", "detail": json.dumps(build.get("checked"))[:300],
         "frame": None}]
    frames, pictures = [], []
    if state == "ready":
        camera = ff.FilmCamera(browser, context.storage_state(), stack.web_base_url, out, kind="solution")
        with recorder.step("spec 166: the solution film captured before any stranger -- the plate, each scene held, "
                           "the phone and the laptop", party="founder") as h:
            frames, shot_faults = camera.shoot(solution, view)
            faults += shot_faults
            h.record_wire({"frames": len(frames)}, {"faults": [f["what"] for f in shot_faults]})
        pictures = ff.fetch_pictures(get_bytes, view, out)
        faults += ff.picture_faults(pictures)
    problem_sheet = ff.drawn(problem_story).get("sheetAssetId")
    solution_sheet = ff.drawn(view).get("sheetAssetId")
    pilot = wire.pilot(True) if state == "ready" else None
    final = wire.idea() or view
    try:
        account = ledger.founder_account(stack, founder.sub)
        spent = ff.ledger_rows(ledger.rows(stack, account["id"]), solution, charges=ff.IDEA_CHARGES)
    except ledger.LedgerUnavailable as e:
        spent = {"rows": [], "unread": str(e)[:200], "usd": None}
    strangers, refused = None, None
    if state == "ready" and pilot and (pilot.get("status") or 500) < 300:
        strangers, refused = solution_strangers_leg(stack, browser, recorder, context, page, run_dir, founder, entry,
                                                    entry_path, solution, problem_id, versions, stamp, words["typed"],
                                                    own_ai=own_ai)
    said = dict(words["beats"])
    film = {
        "spec": "166", "kind": "solution", "entry": {"id": ENTRY, "path": str(entry_path), "sha256": entry["sha256"]},
        "door": DOOR, "telling": words["telling"], "project_id": solution, "problem_project_id": problem_id,
        "create": {"sent": request, "status": status, "lineage": lineage},
        "stack": {"keel-cloud": ((versions.get("keel-cloud") or {}).get("commit") or "")[:8],
                  "keel-web": ((versions.get("keel-web") or {}).get("commit") or "")[:8]},
        "pictures_adapter": os.environ.get("KEEL_PICTURES") or "fake",
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "evidence": str(run_dir),
        "build_state": state, "to_film_s": to_film_s, "brand": brand,
        "composed": words["composed"] if DOOR == "keel" else {"brand": words["composed"]["brand"],
                                                              "beats": words["composed"]["beats"],
                                                              "note": "composed, not told: the fakes tell their script"},
        "lines": ff.lines_of(view), "chapters": [s.get("chapter") for s in ff.scenes(view)],
        "plate": ff.drawn(view).get("plate"), "frames": frames,
        "pictures": [p for p in pictures if p.get("path")], "pictures_served": pictures,
        "missing": ff.missing_scenes(view),
        "sheet": {"asset": solution_sheet, "problem": problem_sheet,
                  "reused": bool(solution_sheet) and solution_sheet == problem_sheet},
        "beats": idea_beats_record(told, said, idea_questions(entry, problem_story, brand["name"])),
        "verdict_line": final.get("verdictLine"), "pilot_ask": final.get("pilotAsk"),
        "pilot": {"sent": (pilot or {}).get("sent"), "status": (pilot or {}).get("status"), "now": final.get("pilot")},
        "ledger": spent, "dollars": spent.get("usd"),
        "measures": {"faults": faults, "frames": len(frames), "pictures": sum(1 for p in pictures if p.get("path")),
                     "missing": ff.missing_scenes(view)},
        "screens_bundle": (strangers or {}).get("bundle"), "strangers": strangers,
        **({"refused": refused} if refused else {}), **({"typos": words["typed"]} if words["typed"] else {}),
    }
    ff.write_folder(out, story=final, film=film, idea=ff.idea_board(final))
    print(f"\nsolution film: {out} -- {len(frames)} frames, {film['measures']['pictures']} pictures, build {state}, "
          f"{len(faults)} capture fault(s), {to_film_s} s to the film; project {solution} on the problem {problem_id}")
    if strangers:
        print(f"strangers: {strangers['answered']} of {strangers['people']} answered on the solution link; "
              f"{len(strangers['after_screens'])} screen(s) after the answers; read-screens bundle {strangers['bundle']}")
    return film


def solution_owed(film: dict) -> list[str]:
    """What the solution half did not hold, named (the leg fails on any, after both halves are written)."""
    out = []
    state = film.get("build_state")
    if state != "ready":
        out.append(f"spec 166: the solution's build ended {state}")
        return out
    scenes_n = len([x for x in film.get("lines") or [] if x.get("scene") != "ask"])
    want = 2 * (scenes_n + 1)                          # every scene and the plate, on both viewports
    if len(film.get("frames") or []) != want:
        out.append(f"spec 166: {len(film.get('frames') or [])} solution frames of {want}: "
                   f"{[f['what'] for f in (film.get('measures') or {}).get('faults') or []]}")
    if film.get("refused"):
        out.append(str(film["refused"]))
        return out
    s = film.get("strangers") or {}
    if not s or s.get("answered") != s.get("people"):
        out.append(f"spec 166: {s.get('answered')} of {s.get('people')} people answered on the solution link: "
                   f"{[(w['person'], w.get('error'), w['response']) for w in s.get('walks') or []]}")
    elif not s.get("after_screens"):
        out.append("spec 166: the solution's founder page shot nothing after the answers")
    return out


def solution_strangers_leg(stack, browser, recorder, context, page, run_dir: Path, founder, entry: dict,
                           entry_path: Path, project_id: str, problem_id: str, versions: dict, stamp: str,
                           typed: list, *, own_ai=None) -> tuple[dict | None, str | None]:
    """Spec 166 FR-3 on the stack: the solution's project locked (the ready page's lock; a short balance topped by the
    stand-in), its link sent to the entry's people of the SOLUTION scope, each walking the solution link, the founder's
    page after them, `backtest.json` (`kind: "film-solution"`) written in `runs/<stamp>-film-<entry>-solution/`."""
    import shutil                                                          # noqa: PLC0415

    from evals import three_views as tv                                    # noqa: PLC0415
    from harness import vectors_script as vs                               # noqa: PLC0415
    run = own_ai or fs.FilmRun(stack=stack, browser=browser, recorder=recorder, context=context, page=page, stamp=stamp)
    cap = people_cap()
    folder = run_dir.parent / f"{run_dir.name}{SOLUTION_SUFFIX}"
    folder.mkdir(parents=True, exist_ok=True)
    if (run_dir / "versions.json").is_file():
        shutil.copyfile(run_dir / "versions.json", folder / "versions.json")

    def top_up():
        account = ledger.founder_account(stack, founder.sub)
        return ledger.stand_in_balance(stack, account["id"], f"film-sol-{stamp}", to=ledger.GRANT_CREDITS,
                                       spec=STAND_IN_SPEC, label="topped",
                                       what="the balance topped to the grant to see the solution's project locked")

    press = fs.press_on_the_ready_page(run, project_id)
    if own_ai is not None:
        pressed_on_keels_door = press

        def press():
            account = own_ai.account_id
            ledger.stand_in_keels_door(stack, account, f"{project_id[:8]}-door-{stamp}", spec=STAND_IN_SPEC)
            try:
                return pressed_on_keels_door()
            finally:
                ledger.restore_own_door(stack, account, f"{project_id[:8]}-restore-{stamp}", spec=STAND_IN_SPEC)

    with recorder.step("spec 166: the solution's project locked -- the SOLUTION calibration written at the board's yes, "
                       "the credits, the ready page's lock, the questions READY", party="founder", kind="assert") as h:
        try:
            lock = fs.lock_project(run.call, project_id, window=None, press=press,
                                   need=0 if own_ai is not None else tv.PROJECT_PRICE, top_up=top_up,
                                   scope=fs.SOLUTION_SCOPE)
        except fs.LockFailed as failed:
            h.record_assert({"locked": True}, {"locked": False, "step": failed.step, "detail": failed.detail})
            return None, str(failed).replace("the film's project", "the solution's project")
        h.record_assert({"locked": True}, {"locked": True, **lock})
    plans = fs.solution_plans(vs.person_inputs(_vs_entry(stack, cap, scope=fs.SOLUTION_SCOPE)))
    kept: dict = {}
    with recorder.step(f"spec 166: the solution's link sent to {len(plans)} people, each walking the two films, the "
                       "plate and the three questions", party="participant", kind="assert") as h:
        walks = fs.walk_solution_people(run, project_id, plans, out=kept)
        h.record_assert({"answered": len(plans)},
                        {"answered": sum(1 for w in walks if w["response"]["status"] == 201 and w["done"]),
                         "walks": [{k: w.get(k) for k in ("person", "steps", "whys", "owed", "response", "error")}
                                   for w in walks]})
    answered = [p for p, w in zip(plans, walks) if w["response"]["status"] == 201 and w["done"]
                and p["screener"] == "yes" and p["gate"]]
    with recorder.step("spec 166: the solution's founder page after the answers -- the stage page, the three cards, "
                       "Insights, the brief", party="founder") as h:
        handed = None
        if own_ai is not None:
            def handed():
                own_ai.load_runtime("SOLUTION", extra={"THEMES": fs.themes_script(
                    fs.said_by_rung(kept.get("walked") or {}))})
        after = fs.founder_page_after(run, project_id, folder, before_settle=handed, scope=fs.SOLUTION_SCOPE,
                                      picks=[p["picks"] for p in answered])
        h.record_wire({"after": "the answers leg and spec 162's reads"},
                      {"screens": len(after["after_screens"]), "checks": after["founder_page"]["checks"]})
    who = fs.solution_watched(plans)
    respondents = fs.respondents_record(who, (kept.get("interviews") or {}).get(who),
                                        (kept.get("walked") or {}).get(who))
    commits = {name: ((versions.get(name) or {}).get("commit") or "") for name in ("keel-cloud", "keel-web")}
    bundle = fs.screens_bundle(
        entry={"id": ENTRY, "title": entry["yaml"].get("title"), "path": str(entry_path), "sha256": entry["sha256"]},
        project_id=project_id, door=DOOR, stack=commits, people=cap, lock=lock, plans=plans, walks=walks,
        respondents=respondents, after_screens=after["after_screens"], answers_leg=after["answers_leg"],
        brief=after["brief"], themes_settled=after["themes_settled"], founder_page=after["founder_page"],
        run=folder.name, typos=typed, scope=fs.SOLUTION_SCOPE, parent=problem_id)
    (folder / "backtest.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False, default=str) + "\n",
                                          encoding="utf-8")
    return {"project_id": project_id, "people": len(plans), "watched": who, "bundle": str(folder),
            "answered": sum(1 for w in walks if w["response"]["status"] == 201 and w["done"]),
            "walks": walks, "lock": lock, "after_screens": [s.get("screen") for s in after["after_screens"]],
            "founder_page": after["founder_page"]["checks"]}, None
