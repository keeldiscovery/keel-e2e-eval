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
    if up and DOOR == "keel":
        pytest.exit("make film-leg refuses: a stack already answers on the eval ports and was not booted from this shell "
                    "with the keys -- `make down` first (DOOR=keel brings its own stack up and down)", returncode=2)
    if not up:
        boot(stack_config)
    try:
        yield stack_config
    finally:
        if not up:
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
    founder = remote.register_cell_identity(stack, f"film · {ENTRY} · {time.strftime('%Y-%m-%d', time.gmtime())}",
                                            name=f"Film Founder {stamp}", id=f"film-{ff.safe_name(ENTRY)}-{stamp}",
                                            email=f"film-{ff.safe_name(ENTRY)}-{stamp}@{domain}")
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

    try:
        Auth(page, recorder, stack.web_base_url).sign_up(founder)
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
        versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8")) \
            if (run_dir / "versions.json").is_file() else {}
        # spec 165: the strangers on the film's link, on this project -- the lock, the people, the founder's page after
        strangers, refused = None, None
        if state == "ready":
            strangers, refused = strangers_leg(stack, browser, recorder, context, page, run_dir, founder, entry,
                                               entry_path, project_id, versions, stamp, typed)
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
        }
        ff.write_folder(out, story=story, film=film)
        print(f"\nfilm: {out} -- {len(frames)} frames, {film['measures']['pictures']} pictures, build {state}, "
              f"{len(faults)} capture fault(s)")
        if strangers:
            print(f"strangers: {strangers['answered']} of {strangers['people']} answered on the film's link "
                  f"(project {project_id}); {len(strangers['after_screens'])} screen(s) after the answers; "
                  f"read-screens bundle {run_dir}")
        assert state == "ready", f"the build ended {state}"
        assert len(frames) == 2 * ff.SCENES, f"{len(frames)} frames of {2 * ff.SCENES}: {[f['what'] for f in faults]}"
        assert not refused, refused
        assert strangers and strangers["answered"] == strangers["people"], \
            f"spec 165: {strangers and strangers['answered']} of {strangers and strangers['people']} people answered " \
            f"on the film's link: {[(w['person'], w.get('error'), w['response']) for w in (strangers or {}).get('walks') or []]}"
        assert strangers["after_screens"], "spec 165: the founder's page shot nothing after the answers"
    finally:
        context.close()


def _vs_entry(stack, cap: int):
    """The entry as `vectors_script` reads it, under the PROBLEM scope and the walk's cap (spec 106's `people_cap`)."""
    import dataclasses                                                     # noqa: PLC0415

    from harness import vectors_script as vs                               # noqa: PLC0415
    _, read = vs.entry_for(stack.keel_cloud, ENTRY, backtest=True)
    return dataclasses.replace(read, scope=fs.SCOPE, people_cap=int(cap))


def strangers_leg(stack, browser, recorder, context, page, run_dir: Path, founder, entry: dict, entry_path: Path,
                  project_id: str, versions: dict, stamp: str, typed: list) -> tuple[dict | None, str | None]:
    """Spec 165 FR-1, FR-2 on the stack: the film's project locked, the people on its link, the founder's page after
    them, `backtest.json` written. Returns `(the strangers' record, None)` or `(None, the refusal naming the step)`."""
    from evals import three_views as tv                                    # noqa: PLC0415
    from harness import vectors_script as vs                               # noqa: PLC0415
    run = fs.FilmRun(stack=stack, browser=browser, recorder=recorder, context=context, page=page, stamp=stamp)
    cap = people_cap()

    def top_up():
        account = ledger.founder_account(stack, founder.sub)
        return ledger.stand_in_balance(stack, account["id"], f"film-{stamp}", to=ledger.GRANT_CREDITS,
                                       spec=STAND_IN_SPEC, label="topped",
                                       what="the balance topped to the grant to see the film's project locked")

    with recorder.step("spec 165: the film's project locked -- the window, the calibration, the credits, the ready "
                       "page's lock, the questions READY", party="founder", kind="assert") as h:
        try:
            lock = fs.lock_project(run.call, project_id, window=fs.recall_window(entry["yaml"]),
                                   press=fs.press_on_the_ready_page(run, project_id),
                                   need=tv.PROJECT_PRICE, top_up=top_up)
        except fs.LockFailed as failed:
            h.record_assert({"locked": True}, {"locked": False, "step": failed.step, "detail": failed.detail})
            return None, str(failed)
        h.record_assert({"locked": True}, {"locked": True, **lock})
    plans = fs.people_plans(vs.person_inputs(_vs_entry(stack, cap)))
    kept: dict = {}
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
        after = fs.founder_page_after(run, project_id, run_dir)
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
