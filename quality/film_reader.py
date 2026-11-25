"""The film reader (spec 163 FR-3): `make read-films RUN=<bundle> [DRY=1] [ENTRY=<id>] [FOUNDER=0]`.

A film-walk bundle (`make film-walk`, spec 163 FR-2) carries, per entry, `film/<entry>/`: the fourteen frames
(`frames/scene-<n>-phone.png`, `-laptop.png`), the served story (`story.json`), the pictures (`pictures/scene-<n>.png`,
`pictures/sheet.png`), the setting and the prompts (`prompts.json`) and the capture's record (`film.json`: the lines
with their chapter marks, the beats Keel asked the founder, the verdict line, the ledger, the measures). Each film is
read in **one call through the Anthropic API with vision** -- the persona card (the entry's context, roles, today's way
and problem statement), the lines, the setting and the prompts, then every frame and picture as an image, then the
rubric (`quality/FILM-RUBRIC.md`) -- and answered as the criteria with their whys, `missing[]` and an `instead` line
per criterion under 2. `film_pct` and the flag are code's.

**The door is the Anthropic Messages API** (`POST /v1/messages`, raw HTTP through `requests`: no SDK is installed here
and nothing is pip-installed), the model and effort pinned in `quality/readers.toml` `[film_reader]` (`claude-opus-5-5`,
`output_config.effort` medium, adaptive thinking -- Opus 5.5 cannot disable it), the refusal fallback on
(`fallbacks: "default"`, beta `server-side-fallback-2026-07-01`; a fallback is recorded in the score file by name, as
the model that served the film). The key is the shell's `KEEL_ANTHROPIC_API_KEY`, read into the `x-api-key` header
alone, never logged, echoed or written. **The `claude` CLI door is refused for this reader** (`refuse_cli`): it cannot
carry the frames. A run refuses before its first call without the key.

**The founder's beats** (FR-1): after the film, the founder-reader of `make read-screens` (the `claude` CLI, `[reader]`,
`quality/readers/film-founder.md`) reads each of Keel's lines to the founder -- the seven beat questions as asked, the
readback or ask after each, the verdict line -- one call a line, on R1, R2, R3 and R5; `founder_pct` beside `film_pct`.
`FOUNDER=0` skips them (the file then says `founder: null`).

A full run writes `quality/scores/<bundle>-film-<entry>.json` (committed) with the reader block and
`FILM_RUBRIC_VERSION`; every prompt and answer is recorded under `runs/<stamp>-read-films-<bundle>/calls/` (the images
by path, never inlined). `DRY=1` writes the prompts (the images named in place) and calls nothing.

**Spec 166 FR-4: both films.** Every film folder of the walk is read with its kind: `film/<entry>/` as the problem's
(F1-F8), `film/<entry>/solution/` as the solution's (S1-S9, `film.json` `kind: "solution"`); `KIND=` reads one kind
alone. The solution's request (`film-reader.md` between its `solution-*` markers) carries the persona card, **the
problem's limitations and cost** (the problem film's `story.json`), **the founder's idea board** (`idea.json`), the
lines with their chapter marks, the plate's words, the setting and the frame plan, the prompts, then the plate frame,
every scene's frames, the pictures and the character sheet, then `prompt_solution()`. Its score file is
`quality/scores/<bundle>-film-<entry>-solution.json` (`kind: "solution"`); the founder's beats on the solution (the four
beats, the verdict line and the pilot ask) are read into the same file. **The size rule**: a request whose images pass
`MAX_REQUEST_BYTES` drops the laptop frames first (then the phone frames of the pictures already handed, never the
pictures) and says so -- in the request and in the score file (`dropped`).

Never in `make eval`, `make unit`, the matrix, a checker or a schedule; PAID (about $0.30 a film at list price, plus the
founder's beats on the founder's plan), run on the founder's word.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from quality import film_rubric as fr
from quality import readers

REPO = Path(__file__).resolve().parent.parent
QUALITY = REPO / "quality"
READERS_TOML = QUALITY / "readers.toml"
PROMPT_PATH = QUALITY / "readers" / "film-reader.md"
FOUNDER_PROMPT_PATH = QUALITY / "readers" / "film-founder.md"
SCORES_DIR = QUALITY / "scores"
RUNS_DIR = REPO / "runs"
FILM_DIR = "film"

KEY_NAME = "KEEL_ANTHROPIC_API_KEY"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2026-10-21"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
#: The one door this reader runs through (`[film_reader] door`).
API_DOOR = "anthropic api"
#: The phone and the laptop frames (FR-2), in the order they are handed.
VIEWPORTS = ("phone", "laptop")
#: The request's ceiling: the API takes 32 MB; the images are base64 (4/3 of their bytes).
MAX_REQUEST_BYTES = 30 * 1024 * 1024
#: keel-web 261 / keel-cloud 273's chapter words, by the served key (carried across the scenes of a chapter).
CHAPTER_WORDS = {"who": "Who", "task": "The task", "today": "Today", "shortfall": "Where it falls short",
                 "cost": "What it costs them", "before": "Before", "solves": "What it solves", "better": "Better",
                 "joy": "What they get"}
#: Spec 166: the two films, and where the solution's folder sits beside the problem's.
KINDS = ("problem", "solution")
SOLUTION_DIR = "solution"


class Refused(RuntimeError):
    """A reason to stop before the first call -- printed as one sentence, exit 2."""


# ------------------------------------------------------------------------------------------------ the config

def load_film_reader(path: Path | None = None) -> dict:
    """`quality/readers.toml` `[film_reader]`, checked: the model, the effort and the vendor named, the door the API's
    (`refuse_cli`)."""
    with Path(path or READERS_TOML).open("rb") as handle:
        raw = tomllib.load(handle)
    cfg = dict(raw.get("film_reader") or {})
    for key in ("model", "effort", "vendor", "door"):
        if not cfg.get(key):
            raise Refused(f"quality/readers.toml has no film_reader.{key} (spec 163 FR-3)")
    refuse_cli(cfg["door"])
    cfg.setdefault("max_tokens", 16000)
    cfg.setdefault("timeout_s", 600)
    for key, value in (("usd_per_mtok_in", 4.0), ("usd_per_mtok_out", 20.0), ("usd_per_mtok_cache_read", 0.2)):
        cfg.setdefault(key, value)
    return cfg


def refuse_cli(door: str) -> None:
    """FR-3: the film reader runs through the Anthropic API with vision alone -- the `claude` CLI door cannot carry the
    frames and is refused by name, as is any other door."""
    said = str(door or "").strip().lower()
    if said != API_DOOR:
        if "cli" in said or "claude" in said or said == "host":
            raise Refused(f"make read-films refuses the door {door!r}: the film reader reads the frames and pictures as "
                          "images, which the `claude` CLI door cannot carry -- it runs through the Anthropic API with "
                          f"vision alone (quality/readers.toml [film_reader] door = \"{API_DOOR}\", spec 163 FR-3)")
        raise Refused(f"make read-films refuses the door {door!r}: the film reader's one door is \"{API_DOOR}\" "
                      "(spec 163 FR-3)")


def key_refusal(env: dict | None = None) -> str | None:
    env = os.environ if env is None else env
    if not (env.get(KEY_NAME) or "").strip():
        return (f"make read-films refuses: {KEY_NAME} is not set in this shell -- the film reader runs through the "
                "Anthropic API with vision (spec 163 FR-3); the key is read into the request header alone and never "
                "logged, echoed or written")
    return None


def template(path: Path, part: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    begin, end = f"<!-- {part}:begin -->", f"<!-- {part}:end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise Refused(f"{Path(path).name} must carry one `{part}:begin` and one `{part}:end` marker")
    return text.split(begin, 1)[1].split(end, 1)[0].strip() + "\n"


# --------------------------------------------------------------------------------------------- the bundle

def film_folders(run_dir: Path, only: str | None = None, kind: str | None = None) -> list[Path]:
    """Every film folder of a bundle that carries its capture's record (`film.json`), in entry order: the problem's
    `film/<entry>/`, then (spec 166) the solution's `film/<entry>/solution/`. `only` an entry; `kind` one kind."""
    root = Path(run_dir) / FILM_DIR
    folders = []
    for entry in (sorted(p for p in root.glob("*") if p.is_dir()) if root.is_dir() else []):
        if only and entry.name != only:
            continue
        for folder in (entry, entry / SOLUTION_DIR):
            if (folder / "film.json").is_file() and (kind is None or film_kind(folder) == kind):
                folders.append(folder)
    return folders


def film_kind(folder: Path) -> str:
    """A film folder's kind: `film.json`'s `kind`, else the folder's place (`solution/` beside the problem's)."""
    try:
        said = json.loads((Path(folder) / "film.json").read_text(encoding="utf-8")).get("kind")
    except (OSError, json.JSONDecodeError):
        said = None
    return said if said in KINDS else ("solution" if Path(folder).name == SOLUTION_DIR else "problem")


def entry_of(folder: Path) -> str:
    folder = Path(folder)
    return folder.parent.name if folder.name == SOLUTION_DIR else folder.name


def resolve_run(run: str | Path) -> Path:
    if not run:
        raise Refused("make read-films refuses: no RUN -- name a film-walk bundle, `make read-films RUN=runs/<bundle>` "
                      "(spec 163 FR-3)")
    run_dir = Path(run).expanduser()
    if not run_dir.is_absolute() and not run_dir.exists():
        run_dir = RUNS_DIR / run_dir
    if not film_folders(run_dir):
        raise Refused(f"make read-films refuses: {run_dir} has no film/<entry>/film.json -- only a bundle `make "
                      "film-walk` wrote is read (spec 163 FR-2)")
    return run_dir


def load_entry_card(film: dict, directory: Path | None = None) -> dict:
    """The entry yaml the film was walked for -- from the keel-cloud checkout stack.toml names (else the path the
    capture recorded) -- with whether it is byte for byte the one walked."""
    entry = film.get("entry") or {}
    candidates = []
    if directory:
        candidates.append(Path(directory) / f"{entry.get('id')}.yaml")
    if entry.get("path"):
        candidates.append(Path(entry["path"]))
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        raise Refused(f"make read-films refuses: no entry yaml for {entry.get('id')} (looked at "
                      f"{[str(p) for p in candidates]})")
    raw = path.read_bytes()
    data = yaml.safe_load(raw) or {}
    sources = path.parent / (data.get("sources") or f"{entry.get('id')}.sources.md")
    sha = hashlib.sha256(raw).hexdigest()
    return {"id": entry.get("id"), "yaml": data, "yaml_path": str(path), "sha256": sha,
            "matches_bundle": sha == entry.get("sha256"),
            "sources": sources.read_text(encoding="utf-8") if sources.is_file() else ""}


def persona_card(entry_yaml: dict) -> str:
    """FR-3: the persona card -- the entry's context (as `make read-screens` hands it), its practitioners' roles,
    today's way and the problem statement whole (its limitations and its cost are inside it)."""
    lines = ["The person (the entry's context, in the founder's words):", *readers.context_lines(entry_yaml)]
    roles = [r for r in entry_yaml.get("roles") or [] if r.get("roleType") != "BUYER"] or (entry_yaml.get("roles") or [])
    for role in roles:
        lines.append(f"  role: {role.get('label', '')} -- {role.get('about', '')}")
    today = (entry_yaml.get("current_solution") or {}).get("today")
    if today:
        lines.append(f"  today's way: {today}")
    problem = (entry_yaml.get("statements") or {}).get("problem")
    lines += ["", "The founder's problem statement, whole (every limitation it names, and what it costs them):",
              f"  {problem or '(none recorded)'}"]
    return "\n".join(lines)


def chapters(scenes: list[dict]) -> list[str | None]:
    """The chapter mark each scene is drawn under: the served key on the chapter's opening scene, carried across the
    scenes of its chapter (keel-web 261 judgement call 2); none on the ask."""
    out, now = [], None
    for scene in scenes:
        if scene.get("chapter"):
            now = scene["chapter"]
        out.append(None if scene.get("ask") else now)
    return out


def lines_block(story: dict) -> str:
    """The film's lines in order with their chapter marks (the build's scenes); on the idea film (spec 166) the
    limitations' ticks and crosses, the joy scene, the brand on the screen and a frame dropped (`pictureMissing`)."""
    scenes = list(((story.get("build") or {}).get("story") or {}).get("scenes") or [])
    rows = []
    for i, (scene, mark) in enumerate(zip(scenes, chapters(scenes)), 1):
        tags = []
        if mark:
            tags.append(f"chapter: {CHAPTER_WORDS.get(mark, mark)}")
        if scene.get("pain"):
            tags.append("the pain scene")
        if scene.get("joy"):
            tags.append("the joy scene")
        if scene.get("marks"):
            tags.append("marks: " + "; ".join(f"{m.get('limit')} {'(tick)' if m.get('mark') == 'tick' else '(cross)'}"
                                              for m in scene["marks"]))
        if (scene.get("screen") or {}).get("name"):
            tags.append(f"the brand on the screen: {scene['screen']['name']}")
        if scene.get("ask"):
            tags.append("the ask, on the wiped board, no picture")
        elif scene.get("pictureMissing"):
            tags.append("NO PICTURE: the frame was left out (pictureMissing); the player holds the picture before, "
                        "or the plain ground where it is the first scene")
        elif not scene.get("pictureAssetId"):
            tags.append("NO PICTURE SERVED")
        rows.append(f"{i}. {scene.get('line') or ''}" + (f"  [{'; '.join(tags)}]" if tags else ""))
    ask = ((story.get("build") or {}).get("story") or {}).get("askLine")
    if ask:
        rows.append(f"{len(scenes) + 1}. {ask}  [the ask, on the wiped board, no picture]")
    return "\n".join(rows) or "(the build served no scene)"


def setting_block(prompts: dict) -> str:
    setting = prompts.get("setting") or {}
    if not setting:
        return "(no setting on the build)"
    return "\n".join(f"  {k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in setting.items())


def prompts_block(prompts: dict) -> str:
    """The build's prompts as the reader needs them: every paragraph once -- the style rule, the character and the place
    as the first prompt says them -- then, per prompt, only what is new in it (the scene's moment and cue, a re-draw's
    reasons)."""
    seen: set[str] = set()
    rows = []
    for p in prompts.get("prompts") or []:
        scene = "the sheet" if p.get("scene") in (None, "sheet") else f"scene {p.get('scene')}"
        fresh = []
        for para in re.split(r"\n\s*\n", str(p.get("prompt") or "")):
            flat = " ".join(para.split())
            if flat and flat not in seen:
                seen.add(flat)
                fresh.append(flat)
        rows.append(f"- {scene} (attempt {p.get('attempt', 1)}): " + (" / ".join(fresh) or "(as above)"))
    return "\n".join(rows) or "(no prompt on the build)"


#: Spec 167 FR-3 (keel-web 263 FR-2, FR-3): the layout each frame was held in, in the reader's words -- the caption over
#: the picture's lower third (a phone; a laptop around a landscape film, as 261 drew it), or beside the picture in the
#: words' column (a laptop, a portrait film).
LAYOUT_WORDS = {"over": "the caption over the picture's lower third", "column": "the caption beside the picture"}


def frame_label(frame: dict) -> str:
    """Spec 167 FR-3: a scene frame's label names the viewport AND the layout (so legibility, F8 / S9, and the line
    matching its picture, F6 / S7, are read right), the stage's shape, and a frame left out. A frame captured before 167
    carries no layout: it was 261's, the caption over the picture on both viewports."""
    layout = frame.get("layout") or "over"
    stage = frame.get("stage") or {}
    shape = {"portrait": "a tall stage", "landscape": "a wide stage"}.get(frame.get("ratio") or "")
    size = f" {stage.get('w')} x {stage.get('h')}" if shape and stage.get("w") and stage.get("h") else ""
    label = (f"Frame -- scene {frame['scene']} on the {frame['viewport']} ({frame.get('size', '')}), "
             f"{LAYOUT_WORDS.get(layout, LAYOUT_WORDS['over'])}" + (f", {shape}{size}" if shape else ""))
    if frame.get("missing"):
        label += (", this scene's own picture left out (the picture before held still)" if frame.get("held") else
                  ", this scene's own picture left out (the plain ground)" if frame.get("ground") else
                  ", this scene's own picture left out")
    return label + ", as the founder's player held it"


def images(folder: Path, film: dict) -> list[dict]:
    """The images in the order they are handed (FR-3): the fourteen frames (scene by scene, phone then laptop), then the
    pictures (scene by scene), then the character sheet. Each `{label, path}`; a frame or picture the capture did not
    write is named and left out (the reader is told it is missing). Spec 166: the solution's plate frames first."""
    out = []
    for frame in film.get("frames") or []:
        if frame.get("scene") == "plate":
            out.append({"label": f"Frame -- the brand plate on the {frame['viewport']} ({frame.get('size', '')}), alone "
                                 "before scene 1", "path": folder / frame["path"], "viewport": frame["viewport"]})
            continue
        out.append({"label": frame_label(frame), "path": folder / frame["path"], "viewport": frame["viewport"]})
    for pic in film.get("pictures") or []:
        what = "the character sheet" if pic.get("scene") == "sheet" else f"the picture of scene {pic['scene']}"
        out.append({"label": f"Picture -- {what}, as keel-cloud stored it", "path": folder / pic["path"]})
    return [i for i in out if Path(i["path"]).is_file()]


def _b64_size(path: Path) -> int:
    return 4 * ((Path(path).stat().st_size + 2) // 3)


def fit(handed: list[dict], ceiling: int = MAX_REQUEST_BYTES) -> tuple[list[dict], list[str]]:
    """Spec 166 FR-4, the size rule: the images that fit under the request's ceiling (base64), and what was left out --
    the laptop frames first (from the last scene back), then the phone frames; the pictures and the sheet never."""
    kept = list(handed)
    dropped: list[str] = []
    total = sum(_b64_size(i["path"]) for i in kept)
    for viewport in ("laptop", "phone"):
        for image in [i for i in reversed(kept) if i.get("viewport") == viewport]:
            if total <= ceiling:
                break
            kept.remove(image)
            total -= _b64_size(image["path"])
            dropped.append(image["label"])
    return kept, dropped


def problem_block(problem_story: dict | None) -> str:
    """Spec 166 FR-4: the problem's limitations and cost, from the problem film's served story (`story.json`)."""
    story = problem_story or {}
    person = story.get("person") or {}
    limits = [x for x in story.get("limits") or [] if x]
    lines = [f"  who: {person.get('who') or '(not served)'}", f"  the task: {person.get('job') or '(not served)'}"]
    if story.get("act"):
        lines.append(f"  today's way: {story['act']}")
    lines.append("  the limitations, in order:" if limits else "  the limitations: (none served)")
    lines += [f"    {i}. {x}" for i, x in enumerate(limits, 1)]
    lines.append(f"  what it costs them: {story.get('cost') or '(not served)'}")
    return "\n".join(lines)


def board_block(idea: dict | None) -> str:
    """Spec 166 FR-4: the founder's idea board (`idea.json`, the served `IdeaView`'s rows)."""
    idea = idea or {}
    brand = idea.get("brand") or {}
    rows = [f"  the product: {brand.get('name') or '(no name)'}"
            + (f" -- {brand['tagline']}" if brand.get("tagline") else "")
            + (f" (colour {brand['colour']})" if brand.get("colour") else "")]
    if idea.get("whatItIs"):
        rows.append(f"  what it is: {idea['whatItIs']}")
    setup = idea.get("setup") or []
    rows.append("  before that (the setup): " + ("; ".join(setup) if setup else
                                                  "nothing to set up" if idea.get("setupNone") else "(not said)"))
    steps = idea.get("workflow") or []
    rows.append("  with it (the steps):" if steps else "  with it (the steps): (none read)")
    rows += [f"    {i}. {s.get('step')} ({'the person' if s.get('by') == 'PERSON' else 'the product'})"
             for i, s in enumerate(steps, 1)]
    if idea.get("statement"):
        rows.append(f"  what it does: {idea['statement']}")
    answers = idea.get("limitAnswers") or []
    rows.append("  in the way (each limitation, its mark):" if answers else "  in the way: (none read)")
    rows += [f"    - {a.get('limit')}: {'tick -- ' + str(a.get('how') or '') if a.get('solved') else 'cross (not solved)'}"
             for a in answers]
    rows.append(f"  better: {idea.get('advantage') or '(nothing beyond the limitations)'}")
    rows.append(f"  what they get: {idea.get('joy') or '(not read)'}" + (" -- said as a feature"
                                                                          if idea.get("joyIsFeature") else ""))
    return "\n".join(rows)


def plate_block(story: dict) -> str:
    plate = (((story.get("build") or {}).get("story") or {}).get("plate")) or {}
    if not plate:
        return "(no plate on the build)"
    return (f"  {plate.get('name') or ''}" + (f" -- {plate['tagline']}" if plate.get("tagline") else "")
            + (f" (colour {plate['colour']})" if plate.get("colour") else ""))


def plan_block(prompts: dict) -> str:
    plan = prompts.get("plan") or []
    if not plan:
        return "(no frame plan on the build)"
    rows = ["The frame plan (what each frame was to contain, and how its check went):"]
    for r in plan:
        rows.append(f"  - scene {r.get('scene')} ({CHAPTER_WORDS.get(r.get('chapter'), r.get('chapter') or '--')}): "
                    f"{r.get('contains')} [{r.get('status')}" + (f": {r['reason']}" if r.get("reason") else "") + "]")
    return "\n".join(rows)


def build_request(folder: Path, film: dict, story: dict, prompts: dict, entry: dict, cfg: dict, *,
                  kind: str = "problem", problem_story: dict | None = None, idea: dict | None = None,
                  ceiling: int = MAX_REQUEST_BYTES) -> dict:
    """The one Messages API request for one film: the body, and the prompt text with every image named in place (what
    the calls folder records). Spec 166: a solution film with the problem's story and the idea board; the size rule."""
    handed, dropped = fit(images(folder, film), ceiling)
    said_dropped = ("Left out to keep this request under its size (the laptop frames first): "
                    + "; ".join(dropped) + ".") if dropped else ""
    values = {"persona": persona_card(entry["yaml"]), "lines": lines_block(story), "setting": setting_block(prompts),
              "prompts": prompts_block(prompts), "rubric": fr.prompt_of(kind),
              "criteria": ", ".join(fr.KINDS[kind])}
    if kind == "solution":
        values |= {"problem": problem_block(problem_story), "board": board_block(idea), "plate": plate_block(story),
                   "plan": plan_block(prompts), "dropped": said_dropped}
    part = "solution-" if kind == "solution" else ""
    before = readers.fill(template(PROMPT_PATH, f"{part}before-images"), values)
    after = readers.fill(template(PROMPT_PATH, f"{part}after-images"), values)
    if dropped and kind != "solution":
        before += "\n" + said_dropped + "\n"
    content, named, size = [{"type": "text", "text": before}], [before], 0
    for image in handed:
        data = Path(image["path"]).read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        size += len(b64)
        content += [{"type": "text", "text": image["label"]},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}}]
        named.append(f"{image['label']}\n[image: {Path(image['path']).relative_to(folder)}, {len(data)} bytes]")
    content.append({"type": "text", "text": after})
    named.append(after)
    if size > ceiling:
        raise Refused(f"make read-films refuses {folder.name}: its images are {size // (1024 * 1024)} MB in base64 with "
                      f"every frame left out, over the request's {ceiling // (1024 * 1024)} MB -- the pictures are "
                      "larger than keel-cloud 273's 2 MB each")
    body = {"model": cfg["model"], "max_tokens": int(cfg["max_tokens"]),
            "output_config": {"effort": cfg["effort"]}, "thinking": {"type": "adaptive"},
            "fallbacks": "default", "messages": [{"role": "user", "content": content}]}
    return {"body": body, "text": "\n\n".join(named), "images": sum(1 for c in content if c["type"] == "image"),
            "image_b64_bytes": size, "dropped": dropped}


# --------------------------------------------------------------------------------------------- the door

@dataclass
class FilmDoor:
    """One bounded, recorded door to the Messages API: one film a call. `post` is `requests.post` (a stub in tests)."""

    config: dict
    run_dir: Path
    post: object = None
    env: dict | None = None
    calls: list = field(default_factory=list)

    def ask(self, label: str, request: dict) -> dict:
        """`{answer, cost_usd, seconds, error, model, fallback, usage}`; the prompt (images by path) and the answer are
        recorded under `calls/`."""
        env = os.environ if self.env is None else self.env
        key = (env.get(KEY_NAME) or "").strip()
        started = time.monotonic()
        body, error, status = {}, None, None
        if self.post is None:
            import requests                                              # noqa: PLC0415
            self.post = requests.post
        try:
            response = self.post(API_URL, json=request["body"], timeout=float(self.config.get("timeout_s", 600)),
                                 headers={"x-api-key": key, "anthropic-version": API_VERSION,
                                          "anthropic-beta": FALLBACK_BETA, "content-type": "application/json"})
            status = getattr(response, "status_code", None)
            body = response.json()
            if status is not None and status >= 400:
                error = f"HTTP {status}: {str((body.get('error') or {}).get('message') or body)[:300]}"
            elif body.get("stop_reason") == "refusal":
                error = f"refused ({(body.get('stop_details') or {}).get('category')})"
        except Exception as exc:                                          # noqa: BLE001 - recorded, the film unread
            error = f"{type(exc).__name__}: {str(exc)[:300]}"
        text = "".join(b.get("text", "") for b in body.get("content") or [] if b.get("type") == "text")
        usage = body.get("usage") or {}
        fallback = [b for b in body.get("content") or [] if b.get("type") == "fallback"]
        result = {"answer": None if error else text, "cost_usd": self.cost(usage), "seconds":
                  round(time.monotonic() - started, 1), "error": error, "status": status,
                  "model": body.get("model"), "fallback": [{"from": (b.get("from") or {}).get("model"),
                                                            "to": (b.get("to") or {}).get("model")} for b in fallback],
                  "usage": {k: usage.get(k) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens",
                                                       "cache_creation_input_tokens")}}
        calls = self.run_dir / "calls"
        calls.mkdir(parents=True, exist_ok=True)
        index = len(self.calls) + 1
        (calls / f"{index:03d}-{label}.prompt.txt").write_text(request["text"], encoding="utf-8")
        (calls / f"{index:03d}-{label}.answer.json").write_text(
            json.dumps({**result, "raw": {k: v for k, v in body.items() if k != "content"},
                        "content": body.get("content")}, indent=2, ensure_ascii=False), encoding="utf-8")
        self.calls.append({"label": label, **result})
        return result

    def cost(self, usage: dict) -> float:
        cfg = self.config
        usd = ((usage.get("input_tokens") or 0) * float(cfg["usd_per_mtok_in"])
               + (usage.get("cache_creation_input_tokens") or 0) * float(cfg["usd_per_mtok_in"]) * 1.25
               + (usage.get("cache_read_input_tokens") or 0) * float(cfg["usd_per_mtok_cache_read"])
               + (usage.get("output_tokens") or 0) * float(cfg["usd_per_mtok_out"])) / 1_000_000
        return round(usd, 4)


AGAIN_TAIL = ("\n\nYour previous reply could not be read: {error}. Reply again with the one JSON object and nothing "
              "else.")


def read_film(door: FilmDoor, label: str, request: dict, kind: str) -> tuple[dict, bool]:
    """One film read, and once more with the fault named where the answer could not be read (spec 122's rule)."""
    said = door.ask(label, request)
    if said["error"]:
        raise fr.FilmRubricError(said["error"])
    try:
        return fr.parse_film_answer(said["answer"], kind=kind), False
    except fr.FilmRubricError as first:
        body = json.loads(json.dumps(request["body"]))
        body["messages"][0]["content"][-1]["text"] += AGAIN_TAIL.format(error=first)
        again = door.ask(f"{label}-again", {**request, "body": body, "text": request["text"] +
                                            AGAIN_TAIL.format(error=first)})
        if again["error"]:
            raise fr.FilmRubricError(f"first: {first}; again: {again['error']}") from None
        try:
            return fr.parse_film_answer(again["answer"], kind=kind), True
        except fr.FilmRubricError as second:
            raise fr.FilmRubricError(f"first: {first}; again: {second}") from None


# ------------------------------------------------------------------------------------- the founder's beats

def founder_lines(film: dict) -> list[dict]:
    """Keel's lines to the founder on the walk, in order (FR-1): each beat's question as asked, with the readback or the
    ask that followed it where the wire served one, then the film's one question (spec 170, keel-web 268 / 269: the
    verdict step retired; a record made before it, with no `film_ask`, keeps the verdict line it was said)."""
    out = []
    for beat in film.get("beats") or []:
        said = [f"Keel asks: {beat.get('asked') or ''}".strip()]
        if beat.get("founder"):
            said.append(f"You said: {beat['founder']}")
        if beat.get("ask"):
            said.append(f"Keel asks again: {beat['ask']}")
        if beat.get("readback"):
            said.append(f"Keel reads back: {beat['readback']}")
        out.append({"beat": f"beat {beat.get('turn')}", "said": "\n".join(said)})
    if film.get("film_ask"):
        out.append({"beat": "the film's question", "said": f"After the film, Keel asks: {film['film_ask']}"})
    elif film.get("verdict_line"):
        out.append({"beat": "the verdict line", "said": f"After the film, Keel says: {film['verdict_line']}"})
    if film.get("pilot_ask"):
        # spec 166 FR-4 (163 FR-1: the solution's four beats and the pilot ask)
        out.append({"beat": "the pilot ask", "said": f"Then Keel asks: {film['pilot_ask']}"})
    return out


def founder_prompts(film: dict, entry: dict) -> list[tuple[dict, str]]:
    persona = readers.founder_persona(entry)
    lines = founder_lines(film)
    out = []
    for i, line in enumerate(lines):
        earlier = "\n".join(f"- {x['beat']}: {x['said'].splitlines()[0]}" for x in lines[:i]) or "(none: this is the first)"
        out.append((line, readers.fill(template(FOUNDER_PROMPT_PATH, "beat"),
                                        {"persona": persona, "rubric": fr.prompt_founder(), "earlier": earlier,
                                         "beat": line["said"]})))
    return out


# ------------------------------------------------------------------------------------------------ the run

def _json_or_empty(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def film_measures(film: dict) -> dict:
    """The film's `measures` as the score file carries them, with spec 168 FR-2's `lock_retried` (true|false): the
    founder's retry pressed on the lock's calibration -- `film.json`'s `measures.lock_retried`, else its `lock`, else
    the strangers' lock record (`strangers.lock`)."""
    measures = dict(film.get("measures") or {})
    if not isinstance(measures.get("lock_retried"), bool):
        lock = film.get("lock") or ((film.get("strangers") or {}).get("lock")) or {}
        measures["lock_retried"] = bool(lock.get("calibration_retried"))
    return measures


def score_path(scores_dir: Path, bundle: str, entry: str, kind: str = "problem") -> Path:
    """FR-3: `quality/scores/<bundle>-film-<entry>.json`; spec 166 FR-4: the solution's `...-film-<entry>-solution.json`."""
    return Path(scores_dir) / f"{bundle}-film-{entry}{'-solution' if kind == 'solution' else ''}.json"


def bundle_name(run_dir: Path) -> str:
    return Path(run_dir).name


def run(argv=None, *, post=None, cli_runner=None, env=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.film_reader", description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", default="")
    parser.add_argument("--entry", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-founder", action="store_true")
    parser.add_argument("--kind", default=None, choices=sorted(fr.KINDS))
    parser.add_argument("--out", default=None)
    parser.add_argument("--scores-dir", default=str(SCORES_DIR))
    args = parser.parse_args(argv)
    env = os.environ if env is None else env
    try:
        run_dir = resolve_run(args.run)
        cfg = load_film_reader()
        folders = film_folders(run_dir, args.entry, args.kind)
        if not folders:
            raise Refused(f"make read-films refuses: no film/{args.entry or '<entry>'}/"
                          f"{'solution/' if args.kind == 'solution' else ''}film.json in {run_dir}")
        if not args.dry_run:
            said = key_refusal(env)
            if said:
                raise Refused(said)
    except Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    now = dt.datetime.now(dt.timezone.utc)
    out = Path(args.out) if args.out else RUNS_DIR / (f"{now.strftime('%Y%m%dT%H%M%SZ')}-read-films-"
                                                       f"{bundle_name(run_dir)}{'-dry' if args.dry_run else ''}")
    out.mkdir(parents=True, exist_ok=True)
    door = FilmDoor(cfg, out, post=post, env=env)
    cli = None
    if not args.no_founder and not args.dry_run:
        cli = readers.Reader(readers.load_reader_config(), out, **({"runner": cli_runner} if cli_runner else {}))
        try:
            cli.probe()
        except readers.Refused as reason:
            print(f"{reason} (the founder's beats; FOUNDER=0 reads the films alone)", file=sys.stderr)
            return 2
    written = []
    for folder in folders:
        film = json.loads((folder / "film.json").read_text(encoding="utf-8"))
        story = json.loads((folder / "story.json").read_text(encoding="utf-8")) if (folder / "story.json").is_file() else {}
        prompts = json.loads((folder / "prompts.json").read_text(encoding="utf-8")) \
            if (folder / "prompts.json").is_file() else {}
        kind = film_kind(folder)
        problem_story, idea = None, None
        if kind == "solution":
            problem_story = _json_or_empty(folder.parent / "story.json")
            idea = _json_or_empty(folder / "idea.json")
        try:
            entry = load_entry_card(film, readers.entries_dir())
            request = build_request(folder, film, story, prompts, entry, cfg, kind=kind, problem_story=problem_story,
                                    idea=idea)
        except Refused as reason:
            print(str(reason), file=sys.stderr)
            return 2
        label = f"film-{entry_of(folder)}{'-solution' if kind == 'solution' else ''}"
        if args.dry_run:
            (out / f"{label}.prompt.txt").write_text(request["text"], encoding="utf-8")
            beats = founder_prompts(film, entry) if not args.no_founder else []
            for i, (line, prompt) in enumerate(beats, 1):
                (out / f"{label}-founder-{i:02d}.prompt.txt").write_text(prompt, encoding="utf-8")
            print(f"dry run: {entry_of(folder)} ({kind}) -- one film call ({request['images']} images, "
                  f"{request['image_b64_bytes'] // 1024} KB in base64) and {len(beats)} founder's beats written to "
                  f"{out}; no call made, no score written")
            continue
        started = time.monotonic()
        try:
            score, again = read_film(door, label, request, kind)
        except fr.FilmRubricError as reason:
            print(f"  {entry_of(folder)} ({kind}): the film unread -- {reason}", file=sys.stderr)
            continue
        founder = None
        founder_cost = 0.0
        if cli is not None:
            rows, unread = [], []
            for line, prompt in founder_prompts(film, entry):
                parse = (lambda raw, b=line["beat"], s=line["said"]: fr.parse_founder_beat(raw, beat=b, said=s))
                try:
                    row, _ = readers.ask_twice(cli, f"{label.removeprefix('film-')}-{line['beat'].replace(' ', '-')}",
                                               prompt, parse)
                    rows.append(row)
                except Exception as reason:                              # noqa: BLE001 - the beat unread, named
                    unread.append({"beat": line["beat"], "error": str(reason)[:300]})
            founder = {**fr.founder_summary(rows), "beats_scored": rows, "unread": unread}
            founder["beats"] = rows
            del founder["beats_scored"]
            founder_cost = round(sum(c["cost_usd"] for c in cli.calls if not c["cached"]), 4)
        film_calls = [c for c in door.calls if c["label"].startswith(label)]
        record = {
            "entry": entry["id"], "kind": kind, "bundle": bundle_name(run_dir),
            "cloud_sha": (film.get("stack") or {}).get("keel-cloud"), "web_sha": (film.get("stack") or {}).get("keel-web"),
            "film_rubric_version": fr.FILM_RUBRIC_VERSION,
            "reader": {k: cfg[k] for k in ("model", "effort", "vendor", "door")} | {
                "served_by": film_calls[-1].get("model") if film_calls else None,
                "fallback": [f for c in film_calls for f in c.get("fallback") or []]},
            "founder_reader": ({k: cli.config[k] for k in ("model", "effort", "vendor", "door")} if cli else None),
            "cost_usd": round(sum(c["cost_usd"] for c in film_calls) + founder_cost, 4),
            "film_cost_usd": round(sum(c["cost_usd"] for c in film_calls), 4), "founder_cost_usd": founder_cost,
            "walk_usd": film.get("dollars"),
            "seconds": round(time.monotonic() - started, 1), "scored_at": now.isoformat(timespec="seconds"),
            "asked_again": again,
            "entry_yaml": {"sha256": entry["sha256"], "matches_bundle": entry["matches_bundle"]},
            "persona_card": persona_card(entry["yaml"]),
            "film": score, "founder": founder,
            "frames": {"frames": [f["path"] for f in film.get("frames") or []],
                       "pictures": [p["path"] for p in film.get("pictures") or []],
                       "folder": str(folder.relative_to(REPO) if REPO in folder.parents else folder)},
            # spec 168 FR-2: `lock_retried` always there (true|false), read from the film's lock where an older
            # film.json's measures do not carry it
            "measures": film_measures(film),
            # spec 166 FR-4: what the size rule left out (the laptop frames first), said
            "dropped": request.get("dropped") or [],
            **({"project_id": film.get("project_id"), "problem_project_id": film.get("problem_project_id")}
               if kind == "solution" else {}),
        }
        fr.validate_file(record, name=label)
        path = score_path(Path(args.scores_dir), bundle_name(run_dir), entry["id"], kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
        print(f"{entry['id']} ({kind}): film_pct {score['film_pct']}{' FLAGGED' if score['flagged'] else ''}, founder_pct "
              f"{(founder or {}).get('founder_pct')}, ${record['cost_usd']} in {record['seconds']} s -> {path}")
    if not args.dry_run:
        print(f"{len(written)} film score file(s) written; calls recorded under {out / 'calls'}")
    return 0 if (args.dry_run or written) else 1


if __name__ == "__main__":
    sys.exit(run())
