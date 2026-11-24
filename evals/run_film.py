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
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from harness import film_frames as ff
from harness import story_screens as ss
from harness.browser import Auth
from harness.steps import Recorder
from stack import ledger
from stack import remote
from stack.lifecycle import boot, quick_gates_pass
from stack.lifecycle import teardown as stack_teardown

ENTRY_VAR, DOOR_VAR, OUT_VAR = "KEEL_FILM_ENTRY", "KEEL_FILM_DOOR", "KEEL_FILM_OUT"
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
        if DOOR == "keel":
            beats = ff.entry_beats(entry["yaml"])
            telling = "the entry's own words"
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
        }
        ff.write_folder(out, story=story, film=film)
        print(f"\nfilm: {out} -- {len(frames)} frames, {film['measures']['pictures']} pictures, build {state}, "
              f"{len(faults)} capture fault(s)")
        assert state == "ready", f"the build ended {state}"
        assert len(frames) == 2 * ff.SCENES, f"{len(frames)} frames of {2 * ff.SCENES}: {[f['what'] for f in faults]}"
    finally:
        context.close()
