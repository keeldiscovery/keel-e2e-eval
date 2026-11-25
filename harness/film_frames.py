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
#: Spec 166 FR-2: the two films an entry carries -- the problem's at `film/<entry>/`, the solution's beside it at
#: `film/<entry>/solution/` (the problem's folder unchanged).
KINDS = ("problem", "solution")
SOLUTION_DIR = "solution"
#: The founder's player of each film (keel-web 257 / 259): where the camera opens it once the build is ready.
CHECK_PATH = {"problem": "define/story/check", "solution": "define/idea/check"}
#: keel-cloud 271 FR-9 / keel-web 259 FR-6: the idea film -- at most eleven scenes in five chapters, behind the brand
#: plate (`idea-plate`, alone for about three seconds before scene 1, shot as its own frame).
IDEA_MAX_SCENES = ss.IDEA_MAX_SCENES
IDEA_CHAPTERS = ss.IDEA_CHAPTERS
PLATE = "[data-testid=idea-plate]"
PLATE_TIMEOUT_MS = 30_000

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


# ------------------------------------------------------------------------------------------- spec 166: the idea's words

#: Spec 166 FR-1: the setup-none words (keel-cloud 271 FR-4 reads *none* as `setupNone`).
SETUP_NONE = "There is nothing to set up. They can start right away."
#: Spec 166 FR-1: the tagline is under eight words; the brand's name at most five (keel-cloud 271 FR-2's caps).
TAGLINE_MAX_WORDS = 7
NAME_MAX_WORDS = 5
#: Words too common to tell a setup row from a step of the mechanism (`_content`).
_COMMON = frozenset("the a an and or of to in on at for with by from into over under it its it's they them their "
                    "this that these those when then than as is are be been was were would could can will each every "
                    "before after while about all any some no not so if out up down off".split())


def _clean(text) -> str:
    return " ".join(str(text or "").split()).strip()


def _bare_end(text) -> str:
    return re.sub(r"[.!?;:,\s]+$", "", _clean(text))


def _lower_first(text: str) -> str:
    text = _clean(text)
    if len(text) < 2 or (text[0].isupper() and text[1].isupper()):
        return text
    return text[0].lower() + text[1:]


def _upper_first(text: str) -> str:
    text = _clean(text)
    return text[:1].upper() + text[1:] if text else ""


def _first_sentence(text) -> str:
    """The first sentence of a statement (cut after the first `.`, `?` or `!` followed by a space)."""
    text = _clean(text)
    cut = re.split(r"(?<=[.?!])\s+(?=[A-Z])", text, maxsplit=1)
    return cut[0] if cut else ""


def _joined(rows: list[str]) -> str:
    rows = [_bare_end(r) for r in rows if _clean(r)]
    if not rows:
        return ""
    return rows[0] if len(rows) == 1 else ", ".join(rows[:-1]) + " and " + rows[-1]


def _content(text) -> set[str]:
    """A phrase's content words, crudely stemmed (a trailing *s* dropped), the common ones left out."""
    out = set()
    for w in re.findall(r"[a-z][a-z'-]+", str(text or "").lower()):
        if len(w) <= 3 or w in _COMMON:
            continue
        out.add(w[:-1] if w.endswith("s") and not w.endswith("ss") else w)
    return out


def entry_number(entry_id: str) -> int:
    """The entry's number (`08-fresco` -> 8), else a stable count of its letters."""
    m = re.match(r"(\d+)", str(entry_id or ""))
    return int(m.group(1)) if m else sum(ord(c) for c in str(entry_id or ""))


def _capped(text: str, cap: int) -> str:
    words = _clean(text).split()
    return " ".join(words[:cap])


def idea_brand(entry_yaml: dict) -> dict:
    """Spec 166 FR-1: the brand the founder types -- the name (`idea_name`, else the title's name before its dash, at
    most five words), a tagline under eight words (`interpretations.offer_name`, else `solution_mechanism.short_name`, the
    first that fits; else the first's first seven words; its first letter raised, no full stop added) and a swatch of
    keel-web's five by the entry's number."""
    title = str(entry_yaml.get("title") or "")
    name = _clean(entry_yaml.get("idea_name")) or _clean(re.split(r"\s+[—–-]\s+", title, maxsplit=1)[0]) \
        or _clean(str(entry_yaml.get("id") or "").split("-", 1)[-1]).capitalize()
    name = _capped(name, NAME_MAX_WORDS)
    offers = [_bare_end(x) for x in ((entry_yaml.get("interpretations") or {}).get("offer_name"),
                                     (entry_yaml.get("solution_mechanism") or {}).get("short_name")) if _clean(x)]
    fitting = [x for x in offers if len(x.split()) <= TAGLINE_MAX_WORDS]
    tagline = _upper_first(fitting[0] if fitting else _capped(offers[0], TAGLINE_MAX_WORDS) if offers else "")
    swatches = ss.BRAND_SWATCHES
    return {"name": name, "tagline": tagline or None,
            "colour": swatches[entry_number(str(entry_yaml.get("id") or "")) % len(swatches)]}


def _verb_first(mechanism: str) -> bool:
    """Whether the mechanism clause opens on its verb (*takes a short video ...*, the actor its subject) rather than on
    its own subject (*its cameras link ...*, *the software reads ...*): one rule -- a first word ending in *s* that is no
    determiner."""
    first = (_clean(mechanism).split() or [""])[0].lower()
    return first.endswith("s") and first not in ("its", "his", "this", "has", "is", "was", "as")


def _steps_sentence(sm: dict) -> str:
    """The steps in one breath, trigger -> mechanism (the actor its subject where the clause opens on its verb)."""
    trigger, mechanism = _bare_end(sm.get("trigger")), _bare_end(sm.get("mechanism"))
    actor = _clean(sm.get("actor")) or "they"
    if not mechanism:
        return ""
    body = f"{actor} {mechanism}" if _verb_first(mechanism) else mechanism
    return _upper_first(f"{trigger}, {body}." if trigger else f"{body}.")


def idea_setup(entry_yaml: dict) -> list[str]:
    """Spec 166 FR-1 (judgement call 3): what the product needs in place before first use, in the founder's recorded words
    -- the founder's Adoption-friction rows (`founder_calibration.solution.adoption_friction`) that are not the
    mechanism's own steps (a row whose content words are mostly the mechanism's is a step, not a setup); none where the
    entry records none (or the founder was unsure)."""
    sm = entry_yaml.get("solution_mechanism") or {}
    recorded = ((entry_yaml.get("founder_calibration") or {}).get("solution.adoption_friction") or {})
    if recorded.get("unsure"):
        return []
    mech = _content(sm.get("mechanism"))
    out = []
    for item in ((recorded.get("answer") or {}).get("items") or []):
        label = _bare_end(item.get("label"))
        words = _content(label)
        if label and words and len(words & mech) / len(words) < 0.5:
            out.append(_lower_first(label))
    return out


def idea_joy(entry_yaml: dict, cost: str | None) -> str:
    """What they get back in the entry's words: the founder's first Relative-advantage row (what it makes better),
    else the opposite of the problem's cost said plainly (*no more ...*)."""
    rows = ((((entry_yaml.get("founder_calibration") or {}).get("solution.relative_advantage") or {}).get("answer")
             or {}).get("items") or [])
    first = next((_bare_end(r.get("label")) for r in rows if _clean(r.get("label"))), "")
    if first:
        return _lower_first(first)
    return f"no more {_lower_first(_bare_end(cost))}" if _clean(cost) else "the time back"


def entry_idea_beats(entry_yaml: dict, problem_story: dict | None) -> dict:
    """Spec 166 FR-1: the founder's solution in the entry's own words, by one rule for every entry, as keel-cloud 271's
    four questions ask it (judgement call 1: the spec's parts mapped onto the served order) --

    * the brand (`idea_brand`);
    * beat 1, the workflow: the product in one breath (`statements.solution`'s first sentence, else the mechanism's
      actor, mechanism and output), then the steps (trigger -> mechanism -> output);
    * beat 2, the setup: `idea_setup`'s rows, else the setup-none words;
    * beat 3, the limitations: the mechanism once, then one clause a limitation of the inherited problem story, each
      answered from it (`not_assumed` never said);
    * beat 4, the joy: what they get back, set against the problem story's cost (`idea_joy`).

    `then` holds the words said to keel-cloud 271's one ask on a beat: beat 1's *What happens first?* (the steps alone),
    beat 3's unmatched limitation (the mechanism again, as a correction), beat 4's feature (the joy alone). Returns
    `{brand, beats: [(n, words)], then: {n: [words]}, setup, joy}`."""
    story = problem_story or {}
    sm = entry_yaml.get("solution_mechanism") or {}
    brand = idea_brand(entry_yaml)
    name = brand["name"]
    statement = (entry_yaml.get("statements") or {}).get("solution")
    output = _bare_end(sm.get("output"))
    steps = _steps_sentence(sm)
    product = _first_sentence(statement) if _clean(statement) else \
        _upper_first(f"{_clean(sm.get('actor')) or 'They'} {_bare_end(sm.get('mechanism'))}") + "."
    product = product if product.endswith((".", "!", "?")) else product + "."
    out_line = f"What comes out is {_lower_first(output)}." if output else ""
    beat1 = " ".join(x for x in (product, steps, out_line) if x)
    setup = idea_setup(entry_yaml)
    beat2 = f"Before they can start, they need to {_joined(setup)}." if setup else SETUP_NONE
    limits = [_bare_end(x) for x in (story.get("limits") or []) if _clean(x)]
    how = steps or product
    clauses = " ".join(f"{_upper_first(lim)}: {name} takes care of that." for lim in limits)
    beat3 = " ".join(x for x in (f"{name} solves them like this. {how}", out_line, clauses) if x)
    cost = _bare_end(story.get("cost"))
    joy = idea_joy(entry_yaml, cost)
    beat4 = (f"Instead of {_lower_first(cost)}, they get {joy}." if cost else f"They get {joy}.")
    then = {1: [" ".join(x for x in (f"First: {_lower_first(steps)}" if steps else "", out_line) if x) or beat1],
            3: [f"Because {_lower_first(how).rstrip('.')}, every one of those is dealt with."],
            4: [f"They get back what it cost them: {joy}."]}
    return {"brand": brand, "beats": [(1, beat1), (2, beat2), (3, beat3), (4, beat4)], "then": then,
            "setup": setup, "joy": joy}


def idea_beat_faults(composed: dict, entry_yaml: dict, problem_story: dict | None = None) -> list[str]:
    """Spec 166 FR-8: the founder's words held to the spoken-form caps keel-cloud 271 holds them to -- the name at most
    five words, the tagline at most eight, every beat under 20,000 characters; no placeholder (`{`, `}`, *None*,
    *null*); no number a founder would not say (every number in the words is one of the entry's own or the story's)."""
    out = []
    brand = composed.get("brand") or {}
    if len(str(brand.get("name") or "").split()) > NAME_MAX_WORDS or not brand.get("name"):
        out.append(f"the name {brand.get('name')!r} is not one to five words")
    if brand.get("tagline") and len(str(brand["tagline"]).split()) > 8:
        out.append(f"the tagline {brand['tagline']!r} is past eight words")
    own = json.dumps(entry_yaml, ensure_ascii=False, default=str) + json.dumps(problem_story or {}, ensure_ascii=False)
    texts = [w for _, w in composed.get("beats") or []] + [w for ws in (composed.get("then") or {}).values() for w in ws]
    for text in texts:
        if len(text) >= 20_000:
            out.append(f"a beat of {len(text)} characters (keel-cloud caps a beat at 20,000)")
        if re.search(r"[{}]|\bNone\b|\bnull\b", text):
            out.append(f"a placeholder in {text[:80]!r}")
        for number in re.findall(r"\d[\d,.]*", text):
            if number.rstrip(".,") not in own:
                out.append(f"the number {number!r} is not the entry's own ({text[:60]!r})")
    return out


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


def film_dir(root: Path, entry: str, kind: str = "problem") -> Path:
    """Spec 166 FR-2: where one film of an entry is written under a walk's bundle."""
    base = Path(root) / FILM_DIR / entry
    return base / SOLUTION_DIR if kind == "solution" else base


def missing_scenes(story: dict) -> list[int]:
    """keel-cloud 275 FR-4: the scenes served with `pictureMissing` (a frame dropped on its own; the film still ready)."""
    return [n for n, s in enumerate(scenes(story), 1) if s.get("pictureMissing")]


def idea_chapter_faults(view: dict) -> list[dict]:
    """Spec 166 FR-2 (keel-cloud 271 FR-9, 273 FR-6, 275 FR-4) on the idea film: at most eleven scenes; the chapter keys
    in the order *before, task, solves, better, joy*, each once, `task`, `solves` and `joy` there; the joy the last scene
    (`joy: true`); a picture on every scene but one served `pictureMissing` (recorded, never a fault: 275 drops a frame
    on its own); one clip a line."""
    out = []
    rows = scenes(view)
    keys = [(n, s.get("chapter")) for n, s in enumerate(rows, 1) if s.get("chapter")]
    order = [k for _, k in keys]
    if not 0 < len(rows) <= IDEA_MAX_SCENES:
        out.append({"what": f"the idea film has {len(rows)} scenes, keel-cloud 271 serves one to eleven",
                    "owed": "keel-cloud 271 FR-9", "detail": "", "frame": None})
    if order != [k for k in IDEA_CHAPTERS if k in order] or len(set(order)) != len(order) \
            or not {"task", "solves", "joy"} <= set(order):
        out.append({"what": f"the idea film's chapter marks are {order}, keel-cloud 271 FR-9 puts them in the order "
                            f"{list(IDEA_CHAPTERS)} (task, solves and joy always)", "owed": "keel-cloud 271 FR-9",
                    "detail": "", "frame": None})
    if rows and not (rows[-1].get("joy") is True and rows[-1].get("chapter") in ("joy", None)
                     and sum(1 for s in rows if s.get("joy")) == 1):
        out.append({"what": "the idea film does not end on its one joy scene (`joy: true`, last)",
                    "owed": "keel-cloud 271 FR-9", "detail": rows[-1].get("line") or "",
                    "frame": f"{FRAMES_DIR}/scene-{len(rows)}-laptop.png"})
    for n, scene in enumerate(rows, 1):
        if not scene.get("pictureAssetId") and not scene.get("pictureMissing"):
            out.append({"what": f"scene {n} is served with no picture and no `pictureMissing`",
                        "owed": "keel-cloud 273 FR-3 / 275 FR-4", "detail": scene.get("line") or "",
                        "frame": f"{FRAMES_DIR}/scene-{n}-laptop.png"})
    clips = len(drawn(view).get("clipIds") or [])
    if clips and clips not in (len(rows), len(rows) + 1):
        out.append({"what": f"{clips} clips for {len(rows)} scenes and the ask (one a line)",
                    "owed": "keel-cloud 271 FR-9", "detail": "", "frame": None})
    return out


# ------------------------------------------------------------------------------------------- the camera

class FilmCamera:
    """The founder's player at `define/story/check` on one viewport at a time, each scene held (the next clip parked)
    while its frame is shot. `call` is a signed-in GET on keel-cloud (the founder's cookie)."""

    def __init__(self, browser, storage_state: dict, web_base: str, out: Path, *, inits: tuple[str, ...] = (),
                 routes: tuple = (), kind: str = "problem"):
        self.browser = browser
        #: Spec 166 FR-2: `solution` -- the idea film at `define/idea/check`, its plate shot first as its own frame.
        self.kind = kind
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
        frames.sort(key=lambda f: (0 if f["scene"] == "plate" else f["scene"],
                                   [v for v, _ in VIEWPORTS].index(f["viewport"])))
        return frames, faults

    def scene_count(self, story: dict) -> int:
        return min(IDEA_MAX_SCENES if self.kind == "solution" else SCENES, len(scenes(story)))

    def _plate(self, page, name: str, viewport: dict) -> tuple[dict | None, dict | None]:
        """keel-web 259 FR-6: the brand plate alone for about three seconds before scene 1 -- shot the moment it stands
        (`frames/plate-<viewport>.png`), then waited off so scene 1 is not shot under it."""
        rel = f"{FRAMES_DIR}/plate-{name}.png"
        plate = page.locator(PLATE).first
        try:
            plate.wait_for(state="visible", timeout=PLATE_TIMEOUT_MS)
        except Exception as e:  # noqa: BLE001 - recorded: the plate never stood
            return None, {"what": f"the brand plate never stood on the {name} before the idea film",
                          "owed": "keel-web 259 FR-6", "detail": str(e)[:200], "frame": None}
        page.mouse.move(0, 0)
        page.wait_for_timeout(150)
        text = " ".join((plate.inner_text(timeout=2_000) or "").split()) if page.locator(PLATE).count() else ""
        page.screenshot(path=str(self.out / rel), animations="disabled")
        frame = {"scene": "plate", "viewport": name, "size": f"{viewport['width']}x{viewport['height']}",
                 "path": rel, "caption": text, "chapter": None, "plate": True}
        try:
            page.wait_for_function(f"() => !document.querySelector('{PLATE}:not([data-fading])')",
                                   timeout=PLATE_TIMEOUT_MS)
        except Exception:  # noqa: BLE001 - the scene's own wait follows
            pass
        return frame, None

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
            page.goto(f"{self.web}/p/{project_id}/{CHECK_PATH[self.kind]}", wait_until="load")
            ss.wake(page)
            if self.kind == "solution":
                plate, missed = self._plate(page, name, viewport)
                frames += [plate] if plate else []
                faults += [missed] if missed else []
            for step in range(self.scene_count(story)):
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
    dropped = [{"scene": n, "asset": None, "path": None, "status": None, "bytes": 0, "content_type": None,
                "png": None, "missing": True} for n in missing_scenes(story)]
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
    return sorted(pictures + dropped, key=lambda p: (1, 0) if p["scene"] == "sheet" else (0, p["scene"]))


def picture_faults(pictures: list[dict]) -> list[dict]:
    out = []
    for p in pictures:
        if p.get("missing"):
            continue                    # keel-cloud 275 FR-4: a frame dropped on its own -- recorded, never a fault
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


#: Spec 166 FR-1: the solution leg's measured rows -- the idea's turns, the build's draft and review, the pictures and
#: their reviews, the clips.
IDEA_CHARGES = ("IDEA_TURN", "IDEA_DRAFT", "IDEA_REVIEW", "STORY_DRAFT", "STORY_CHECK", "STORY_PICTURES",
                "PICTURE_REVIEW", "SPEECH", "CLIP", "STORY_CLIPS", "IDEA_CORRECT", "STORY_CORRECT")


def ledger_rows(rows: list[dict], project_id: str, charges: tuple = PICTURE_CHARGES) -> dict:
    """FR-2: the build's `STORY_PICTURES` row (0 credits, its measured cost) and one `PICTURE_REVIEW` row per picture,
    off the founder's ledger; the dollars are their measured cost. Spec 166: `charges` the rows kept (the solution leg's
    `IDEA_CHARGES`)."""
    def charge(r):
        return r.get("action") if r.get("action") in charges else (r.get("kind") if r.get("kind") in charges else None)
    mine = [r for r in rows if str(r.get("project_id")) == str(project_id) and charge(r)]
    usd = round(sum((r.get("actual_cost_micro_usd") or 0) for r in mine) / 1_000_000, 4)
    out = {"rows": [{k: r.get(k) for k in ("kind", "action", "credits", "price_credits", "actual_cost_micro_usd",
                                            "reason")} for r in mine],
            "story_pictures": sum(1 for r in mine if charge_of(r) == "STORY_PICTURES"),
            "picture_review": sum(1 for r in mine if charge_of(r) == "PICTURE_REVIEW"),
            "credits": sum((r.get("credits") or 0) for r in mine), "usd": usd}
    if charges != PICTURE_CHARGES:
        out["by_charge"] = {c: sum(1 for r in mine if charge(r) == c) for c in charges if any(charge(r) == c
                                                                                            for r in mine)}
    return out


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


#: Spec 166 FR-2: the idea board the solution's reader is handed (`idea.json`) -- the served `IdeaView`'s rows.
IDEA_BOARD_KEYS = ("brand", "opening", "mechanism", "whatItIs", "howItWorks", "workflow", "setup", "setupNone",
                   "statement", "limits", "limitAnswers", "advantage", "joy", "joyIsFeature", "effort", "verdictLine",
                   "pilotAsk", "pilot")


def idea_board(view: dict) -> dict:
    return {k: (view or {}).get(k) for k in IDEA_BOARD_KEYS}


def build_log(story: dict) -> dict:
    """Spec 166 FR-2 (keel-cloud 273 / 275): what the drawing was asked and how it went -- the setting, every prompt, the
    frame plan, every review, the pictures kept from the build before, and a failed build's reason."""
    build = story.get("build") or {}
    pictures = build.get("pictures") or {}
    return {"setting": pictures.get("setting"), "prompts": pictures.get("prompts") or [],
            "plan": pictures.get("plan") or [], "reviews": pictures.get("reviews") or [], "kept": pictures.get("kept"),
            "failedReason": build.get("failedReason"), "failedScene": build.get("failedScene"),
            "failedChapter": build.get("failedChapter")}


def write_folder(out: Path, *, story: dict, film: dict, idea: dict | None = None) -> Path:
    """The film's folder: `story.json`, `prompts.json` and `film.json` -- and on the solution film (spec 166 FR-2)
    `idea.json` (the board) with the build's plan, reviews, kept and `failedReason` beside the prompts."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "story.json").write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pictures = (drawn(story) and ((story.get("build") or {}).get("pictures"))) or {}
    prompts = {"setting": pictures.get("setting"), "prompts": pictures.get("prompts") or []}
    if idea is not None:
        prompts = build_log(story)
        (out / "idea.json").write_text(json.dumps(idea, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prompts.json").write_text(json.dumps(prompts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "film.json").write_text(json.dumps(film, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out / "film.json"


def lines_of(story: dict) -> list[dict]:
    rows = []
    for n, s in enumerate(scenes(story), 1):
        rows.append({"scene": n, "line": s.get("line"), "chapter": s.get("chapter"), "pain": bool(s.get("pain")),
                     "pictureAssetId": s.get("pictureAssetId"), "clipId": s.get("clipId"),
                     # spec 166: the idea film's own marks -- the joy, the limitations' ticks and crosses, the brand
                     # on the screen, a frame dropped (keel-cloud 271 FR-9, 275 FR-4)
                     **({"joy": True} if s.get("joy") else {}), **({"marks": s["marks"]} if s.get("marks") else {}),
                     **({"screen": (s.get("screen") or {}).get("name")} if s.get("screen") else {}),
                     **({"pictureMissing": True} if s.get("pictureMissing") else {})})
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
