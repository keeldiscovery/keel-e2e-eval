"""Spec 163 FR-2: the founder's film captured for the film reader -- machinery, not judgement (`quality/film_reader.py`
judges; `quality/film_rubric.py` holds the ruler).

**The film** is keel-cloud 268 / 273's problem build as keel-web 261 plays it: seven scenes, each a drawn picture
(`StoryScene.pictureAssetId`, `GET /v2/assets/{id}`) with its line as the caption over the bottom third
(`[data-testid=story-stage] [data-testid=story-line]`) and its chapter mark (`story-chapter`: *Who*, *The task*,
*Today*, *Where it falls short*, *What it costs them*), then the ask on the wiped board. The founder's player is opened
at `define/story/check` once the build is ready (before the film's yes), on a phone (390 x 844) and a laptop (1280 x
800), with less motion asked for (no push-in, a cut for the crossfade: a frame is a photograph).

**The held clock.** The picture film follows the voice: a scene stands until the next line's clip sounds (keel-web 261
judgement call 7). Each scene is held, as keel-web's own frames hold it, by withholding the NEXT line's clip
(`/v2/clips/{clipIds[n+1]}`, the request parked on the route) until the frame is shot and the caption settled; then
the clip is let go and the next scene comes. Nothing of the page's own clock is faked.

**What is written** under `film/<entry>/` (FR-2): `frames/scene-<n>-phone.png` and `-laptop.png` (fourteen),
`story.json` (the served `GET story`, whole), `pictures/scene-<n>.png` and `pictures/sheet.png` (the PNGs keel-cloud
stored), `prompts.json` (`build.pictures.setting` and `.prompts`), and `film.json` -- the capture's record: the entry,
the project, the shas, the lines with their chapter marks, every frame (its caption, chapter mark, the picture shown,
the caption inside the stage, its rows), every picture (its id, bytes, PNG size), the beats Keel asked the founder
(for the founder-reader), the verdict line, the ledger's `STORY_PICTURES` and `PICTURE_REVIEW` rows and the dollars,
and `measures.faults` -- what the capture itself held false (a scene served with no picture, a caption outside the
stage or over three rows on the phone, a page that scrolls sideways on the phone, a chapter key off keel-cloud 273's
places): each a DRIFT candidate (`quality/film_table.findings`), never patched around.

**The founder's words** (`entry_beats`): on Keel's door the seven beats are told on the wire (`StoryWire`, as keel-web
257's page sends them) in the entry's own words -- built by one rule for every entry from its `context`, today's way
(`current_solution.today`), its problem statement and its Importance rows (the role's other tasks); no trade is named
here. On the fakes (`FakeStoryReadings` answers from its own script whatever is said) the script's own words are told
(`story_screens.said_turns`), so the build reaches `ready` on the script's draft: the free walk's film is the script's
story, the entry naming the bundle and the persona card alone.
"""

from __future__ import annotations

import json
import re
import struct
import time
from pathlib import Path

from harness import interviewer_screens as ivs
from harness import story_screens as ss

PHONE = {"width": 390, "height": 844}
LAPTOP = {"width": 1280, "height": 800}
#: The two frames of each scene, in the order they are shot and handed to the reader.
VIEWPORTS = (("phone", PHONE), ("laptop", LAPTOP))
#: keel-cloud 268: seven scenes, then the ask (eight lines, eight clips).
SCENES = 7
#: keel-cloud 273 FR-6: the chapter keys and the scene each opens on (the first limitation's scene is 4).
CHAPTER_AT = {1: "who", 2: "task", 3: "today", 4: "shortfall", 7: "cost"}
STAGE = "[data-testid=story-stage]"
LINE = f"{STAGE} [data-testid=story-line]"
#: keel-web 261 FR-2: the caption is at most three rows on a phone.
PHONE_ROWS_MAX = 3
SETTLE_MS = 400
SCENE_TIMEOUT_MS = 90_000

FILM_DIR = "film"
FRAMES_DIR = "frames"
PICTURES_DIR = "pictures"

#: One read of the stage at a held scene: the step, the caption and its rows, the chapter mark, the shown picture,
#: whether the caption sits wholly inside the stage, the pictures drawn, and whether the page scrolls sideways.
_READ_STAGE = r"""() => {
  const stage = document.querySelector('[data-testid=story-stage]');
  if (!stage) return null;
  const cap = stage.querySelector('[data-testid=story-line]');
  const words = cap ? cap.querySelector('.sty-pcap__words') : null;
  const s = stage.getBoundingClientRect();
  const c = cap ? cap.getBoundingClientRect() : null;
  const lh = words ? parseFloat(getComputedStyle(words).lineHeight) : NaN;
  const chapter = stage.querySelector('[data-testid=story-chapter]');
  const on = stage.querySelector('img[data-testid=story-picture][data-on]');
  const imgs = [...stage.querySelectorAll('img[data-asset]')];
  return {
    step: stage.getAttribute('data-step'), ask: stage.hasAttribute('data-ask'),
    caption: words ? words.textContent.replace(/\s+/g, ' ').trim() : '',
    rows: words && lh > 0 ? Math.round(words.getBoundingClientRect().height / lh) : null,
    inside: !!c && c.left >= s.left - 0.5 && c.right <= s.right + 0.5 && c.top >= s.top - 0.5 && c.bottom <= s.bottom + 0.5,
    chapter: chapter ? chapter.textContent.replace(/\s+/g, ' ').trim() : null,
    shown: on ? on.getAttribute('data-asset') : null,
    pictures_drawn: imgs.filter((i) => i.complete && i.naturalWidth > 0).length, pictures: imgs.length,
    stage: { w: Math.round(s.width), h: Math.round(s.height) },
    sideways: document.documentElement.scrollWidth > window.innerWidth,
    mode: (stage.closest('[data-mode]') || {}).getAttribute ? stage.closest('[data-mode]').getAttribute('data-mode') : null,
  };
}"""


# ------------------------------------------------------------------------------------------- the founder's words

def _sentence(text: str | None) -> str:
    text = " ".join(str(text or "").split()).strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?" else text + "."


def entry_beats(entry_yaml: dict) -> list[tuple[int, str]]:
    """The seven beats as the founder would tell them, in the entry's own words, by one rule for every entry: 1 who
    (`actor_plural`, the `segment`); 2 what and when (`job`, `circumstance`); 3 today's way and where it falls short
    (`current_solution.today`, then the problem statement whole -- its limitations are inside it); 4 what it costs them
    (the interpretation's problem line where the entry has one, else the problem statement); 5 all or some (the
    segment); 6 the when (the circumstance; told only where Keel asks it); 7 the role's other tasks (the Importance
    rows after the founder's own)."""
    ctx = entry_yaml.get("context") or {}
    statement = (entry_yaml.get("statements") or {}).get("problem") or ""
    today = (entry_yaml.get("current_solution") or {}).get("today") or ""
    cost = ((entry_yaml.get("interpretations") or {}).get("problem")) or statement
    rows = ((((entry_yaml.get("founder_calibration") or {}).get("problem.importance") or {}).get("answer") or {})
            .get("items") or [])
    others = [str(r.get("label") or "").strip() for r in rows[1:] if str(r.get("label") or "").strip()]
    who = ctx.get("actor_plural") or ctx.get("actor") or ""
    return [
        (1, _sentence(f"{who}" + (f", {ctx['segment']}" if ctx.get("segment") else ""))),
        (2, _sentence(f"They need to {ctx.get('job', '')}, when {ctx.get('circumstance', '')}")),
        (3, " ".join(x for x in (_sentence(f"Today: {today}") if today else "", _sentence(statement)) if x)),
        (4, _sentence(f"What it costs them: {cost}")),
        (5, _sentence(f"Some of them: {ctx.get('segment') or who}")),
        (6, _sentence(f"It happens when {ctx.get('circumstance', '')}")),
        (7, _sentence("Their other tasks: " + "; ".join(others)) if others else _sentence("Nothing else stands out")),
    ]


# ------------------------------------------------------------------------------------------- the served film

def drawn(story: dict) -> dict:
    return ((story.get("build") or {}).get("story")) or {}


def scenes(story: dict) -> list[dict]:
    return list(drawn(story).get("scenes") or [])


def clip_ids(story: dict) -> list[str]:
    """The eight lines' clips in order: `clipIds` where served, else each scene's `clipId` and the ask's."""
    ids = [c for c in drawn(story).get("clipIds") or [] if c]
    return ids or [s.get("clipId") for s in scenes(story) if s.get("clipId")]


def png_size(data: bytes) -> tuple[int, int] | None:
    """A PNG's width and height off its IHDR (no image library), or None where it is not a PNG."""
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def chapter_faults(story: dict) -> list[dict]:
    """keel-cloud 273 FR-6: `who` on scene 1, `task` on 2, `today` on 3, `shortfall` on the first limitation's (4),
    `cost` on the pain's (7), none elsewhere; and a picture on every scene."""
    out = []
    for n, scene in enumerate(scenes(story), 1):
        want = CHAPTER_AT.get(n)
        if (scene.get("chapter") or None) != want:
            out.append({"what": f"scene {n}'s chapter mark is {scene.get('chapter')!r}, keel-cloud 273 FR-6 puts "
                                f"{want!r} there", "owed": "keel-cloud 273 (`StoryScene.chapter`)",
                        "detail": scene.get("line") or "", "frame": f"{FRAMES_DIR}/scene-{n}-laptop.png"})
        if not scene.get("pictureAssetId"):
            out.append({"what": f"scene {n} is served with no picture (`pictureAssetId` absent on a 273 build)",
                        "owed": "keel-cloud 273 FR-3 (no stick fallback)", "detail": scene.get("line") or "",
                        "frame": f"{FRAMES_DIR}/scene-{n}-laptop.png"})
    if len(scenes(story)) != SCENES:
        out.append({"what": f"the film has {len(scenes(story))} scenes, keel-cloud 268 serves seven",
                    "owed": "keel-cloud 268 FR-5", "detail": "", "frame": None})
    return out


# ------------------------------------------------------------------------------------------- the camera

class FilmCamera:
    """The founder's player at `define/story/check` on one viewport at a time, each scene held (the next clip parked)
    while its frame is shot. `call` is a signed-in GET on keel-cloud (the founder's cookie)."""

    def __init__(self, browser, storage_state: dict, web_base: str, out: Path, *, inits: tuple[str, ...] = (),
                 routes: tuple = ()):
        self.browser = browser
        #: `(pattern, handler)` pairs put on each context before the clips' hold (a unit test's page and assets).
        self.routes = tuple(routes)
        self.storage_state = storage_state
        self.web = web_base.rstrip("/")
        self.out = Path(out)
        self.inits = inits or (ivs.SPEECH_SEAM, ss.ORB_WATCH)

    def shoot(self, project_id: str, story: dict) -> tuple[list[dict], list[dict]]:
        """Every scene on both viewports: `(frames, faults)`."""
        frames, faults = [], []
        for name, viewport in VIEWPORTS:
            got, bad = self._one(name, viewport, project_id, story)
            frames += got
            faults += bad
        frames.sort(key=lambda f: (f["scene"], [v for v, _ in VIEWPORTS].index(f["viewport"])))
        return frames, faults

    def _one(self, name: str, viewport: dict, project_id: str, story: dict) -> tuple[list[dict], list[dict]]:
        clips = clip_ids(story)
        held: dict[str, list] = {}
        released: set[str] = {clips[0]} if clips else set()

        def route(r):
            clip = r.request.url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
            if clip in clips and clip not in released:
                held.setdefault(clip, []).append(r)
            else:
                r.fallback()

        def release(clip: str | None) -> None:
            if not clip:
                return
            released.add(clip)
            for r in held.pop(clip, []):
                try:
                    r.fallback()
                except Exception:  # noqa: BLE001 - a request the page already gave up on
                    pass

        context = self.browser.new_context(viewport=viewport, storage_state=self.storage_state,
                                           reduced_motion="reduce")
        for script in self.inits:
            context.add_init_script(script)
        for pattern, handler in self.routes:
            context.route(pattern, handler)
        context.route("**/v2/clips/**", route)
        page = context.new_page()
        frames, faults = [], []
        frames_dir = self.out / FRAMES_DIR
        frames_dir.mkdir(parents=True, exist_ok=True)
        try:
            page.goto(f"{self.web}/p/{project_id}/define/story/check", wait_until="load")
            ss.wake(page)
            for step in range(min(SCENES, len(scenes(story)))):
                n = step + 1
                rel = f"{FRAMES_DIR}/scene-{n}-{name}.png"
                try:
                    page.locator(f"{STAGE}[data-step='{step}'] [data-testid=story-line]:not(:empty)").first.wait_for(
                        state="visible", timeout=SCENE_TIMEOUT_MS)
                    page.wait_for_function(
                        "() => [...document.querySelectorAll('img[data-asset]')]"
                        ".every((i) => i.complete && i.naturalWidth > 0)", timeout=30_000)
                except Exception as e:  # noqa: BLE001 - recorded: the scene never stood
                    faults.append({"what": f"scene {n} never stood on the {name} ({type(e).__name__})",
                                   "owed": "keel-web 261 (the film in pictures)", "detail": str(e)[:200],
                                   "frame": None})
                    break
                try:
                    page.locator(STAGE).first.scroll_into_view_if_needed(timeout=5_000)
                except Exception:  # noqa: BLE001 - already in view
                    pass
                page.mouse.move(0, 0)
                page.wait_for_timeout(SETTLE_MS)
                read = page.evaluate(_READ_STAGE) or {}
                page.screenshot(path=str(self.out / rel), animations="disabled")
                frame = {"scene": n, "viewport": name, "size": f"{viewport['width']}x{viewport['height']}",
                         "path": rel, **{k: read.get(k) for k in ("step", "caption", "rows", "inside", "chapter",
                                                                  "shown", "pictures", "pictures_drawn", "stage",
                                                                  "sideways", "mode")}}
                frames.append(frame)
                if read.get("inside") is False:
                    faults.append({"what": f"scene {n}'s caption is not wholly inside the stage on the {name}",
                                   "owed": "keel-web 261 FR-2 (the caption band)", "detail": read.get("caption") or "",
                                   "frame": rel})
                if name == "phone" and (read.get("rows") or 0) > PHONE_ROWS_MAX:
                    faults.append({"what": f"scene {n}'s caption runs to {read.get('rows')} rows on the phone (at "
                                           f"most {PHONE_ROWS_MAX})", "owed": "keel-web 261 FR-2",
                                   "detail": read.get("caption") or "", "frame": rel})
                if name == "phone" and read.get("sideways"):
                    faults.append({"what": f"the page scrolls sideways on the phone at scene {n}",
                                   "owed": "keel-web 261 FR-9", "detail": "", "frame": rel})
                release(clips[n] if n < len(clips) else None)
            for clip in list(held):
                release(clip)
        finally:
            context.close()
        return frames, faults


# ------------------------------------------------------------------------------------------- the rest of the folder

def fetch_pictures(get_bytes, story: dict, out: Path) -> list[dict]:
    """Every scene's picture and the sheet, as keel-cloud stored them (`GET /v2/assets/{id}`): `get_bytes(path)` ->
    `(status, bytes, content_type)`."""
    folder = Path(out) / PICTURES_DIR
    folder.mkdir(parents=True, exist_ok=True)
    wanted = [(n, s.get("pictureAssetId")) for n, s in enumerate(scenes(story), 1) if s.get("pictureAssetId")]
    if drawn(story).get("sheetAssetId"):
        wanted.append(("sheet", drawn(story)["sheetAssetId"]))
    pictures = []
    for scene, asset in wanted:
        status, data, kind = get_bytes(f"/v2/assets/{asset}")
        rel = f"{PICTURES_DIR}/{'sheet' if scene == 'sheet' else f'scene-{scene}'}.png"
        size = png_size(data or b"")
        if status < 400 and data:
            (Path(out) / rel).write_bytes(data)
        pictures.append({"scene": scene, "asset": asset, "path": rel if status < 400 and data else None,
                         "status": status, "bytes": len(data or b""), "content_type": kind,
                         "png": list(size) if size else None})
    return [p for p in pictures]


def picture_faults(pictures: list[dict]) -> list[dict]:
    out = []
    for p in pictures:
        if not p.get("path") or not p.get("png"):
            out.append({"what": f"the picture of {'the sheet' if p['scene'] == 'sheet' else 'scene ' + str(p['scene'])}"
                                f" is not a PNG served by `GET /v2/assets/{{id}}` (HTTP {p.get('status')})",
                        "owed": "keel-cloud 273 FR-4", "detail": p.get("asset") or "", "frame": None})
    return out


#: keel-cloud 273 FR-3 / FR-5: the measured rows of the pictures (`CreditLedgerEntry.measured`: kind SPEND, the charge's
#: name in `action`, 0 credits, the measured cost).
PICTURE_CHARGES = ("STORY_PICTURES", "PICTURE_REVIEW")


def charge_of(row: dict) -> str | None:
    return row.get("action") if row.get("action") in PICTURE_CHARGES else row.get("kind")


def ledger_rows(rows: list[dict], project_id: str) -> dict:
    """FR-2: the build's `STORY_PICTURES` row (0 credits, its measured cost) and one `PICTURE_REVIEW` row per picture,
    off the founder's ledger; the dollars are their measured cost."""
    mine = [r for r in rows if str(r.get("project_id")) == str(project_id) and charge_of(r) in PICTURE_CHARGES]
    usd = round(sum((r.get("actual_cost_micro_usd") or 0) for r in mine) / 1_000_000, 4)
    return {"rows": [{k: r.get(k) for k in ("kind", "action", "credits", "price_credits", "actual_cost_micro_usd",
                                            "reason")} for r in mine],
            "story_pictures": sum(1 for r in mine if charge_of(r) == "STORY_PICTURES"),
            "picture_review": sum(1 for r in mine if charge_of(r) == "PICTURE_REVIEW"),
            "credits": sum((r.get("credits") or 0) for r in mine), "usd": usd}


def beats_record(told: list[dict], said: dict[int, str]) -> list[dict]:
    """What Keel said to the founder on each beat, off the wire (`StoryWire.tell`): the question (keel-web's words for
    the beat), the founder's words, the ask and the readback served."""
    out = []
    for b in told:
        n = b.get("turn")
        last = (b.get("way") or b.get("put") or {})
        body = last.get("body") or {}
        first = ((b.get("put") or {}).get("body") or {})
        out.append({"turn": n, "asked": ss.STORY_QUESTIONS.get(n), "founder": said.get(n),
                    "ask": b.get("ask") or first.get("ask"), "readback": body.get("readback"),
                    "status": last.get("status")})
    return out


def write_folder(out: Path, *, story: dict, film: dict) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "story.json").write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pictures = (drawn(story) and ((story.get("build") or {}).get("pictures"))) or {}
    (out / "prompts.json").write_text(json.dumps({"setting": pictures.get("setting"),
                                                  "prompts": pictures.get("prompts") or []}, indent=2,
                                                 ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "film.json").write_text(json.dumps(film, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out / "film.json"


def lines_of(story: dict) -> list[dict]:
    rows = []
    for n, s in enumerate(scenes(story), 1):
        rows.append({"scene": n, "line": s.get("line"), "chapter": s.get("chapter"), "pain": bool(s.get("pain")),
                     "pictureAssetId": s.get("pictureAssetId"), "clipId": s.get("clipId")})
    if drawn(story).get("askLine"):
        rows.append({"scene": "ask", "line": drawn(story)["askLine"], "chapter": None, "pain": False,
                     "pictureAssetId": None, "clipId": None})
    return rows


def wait_built(read_story, *, timeout_s: float = 300) -> dict:
    """The build waited for until `ready` or `failed` (the pictures take minutes on the vendor)."""
    deadline = time.monotonic() + timeout_s
    story = read_story()
    while time.monotonic() < deadline and ((story.get("build") or {}).get("state") not in ("ready", "failed")):
        time.sleep(2)
        story = read_story()
    return story


def safe_name(text: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", text.lower()).strip("-")[:60]
