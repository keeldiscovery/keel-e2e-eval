"""Spec 167: the mirrors of keel-web 263 and keel-cloud 275 -- the camera on the portrait stage and the laptop's words'
column, the frame plan on the building screen, a frame left out, the failed build's reason, the stills' ratio, the
reader told the layout. Local pages that lay out as keel-web 263's (one DOM at every width, the layout decided in CSS),
no stack and no model (FR-5: nothing paid).
"""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from evals import three_views_strangers as tvs
from harness import film_frames as ff
from harness import interviewer_screens as ivs
from harness import story_screens as ss
from quality import film_reader as fread
from stack.config import load_config

REPO = Path(__file__).resolve().parent.parent
WEB = Path(load_config(validate=False).keel_web)


def png(w: int, h: int) -> bytes:
    raw = b"".join(b"\x00" + b"\x88\x88\x88" * w for _ in range(h))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


LINES = ["Example workers in small teams.", "They keep the day's list.", "They write it on paper.",
         "The list gets lost on the way back.", "Two people copy the same item.", "The copy is late.",
         "They stay an hour after closing."]
CHAPTERS = {1: "who", 2: "task", 3: "today", 4: "shortfall", 7: "cost"}


def story(missing: int | None = None) -> dict:
    scenes = []
    for n, line in enumerate(LINES, 1):
        scene = {"line": line, "clipId": f"c{n}", "pictureAssetId": f"a{n}",
                 **({"chapter": CHAPTERS[n]} if n in CHAPTERS else {}), **({"pain": True} if n == 7 else {})}
        if n == missing:
            scene["pictureAssetId"], scene["pictureMissing"] = None, True
        scenes.append(scene)
    return {"build": {"state": "ready", "story": {"scenes": scenes, "askLine": "Is that how it goes for you?",
                                                  "clipIds": [f"c{n}" for n in range(1, 9)], "sheetAssetId": "sheet1"}}}


#: keel-web 263's film as one DOM at every width: `story-film` (`display: contents` at 720 px and under, a grid above it
#: on a portrait film), the words' column `story-side` (not drawn on a phone), the stage 2:3 on a portrait film, its own
#: pill and caption not drawn beside the column; a frame left out holds the picture before (`data-held`).
PLAYER_263 = """<!doctype html><html><head><style>
body{margin:0;font:16px/24px sans-serif} main{padding:0 16px}
.sty-film{display:contents} .sty-side{display:none}
.sty-stage{position:relative;width:100%;aspect-ratio:3/2;background:#bcbcbd;overflow:hidden}
.sty-stage[data-ratio=portrait]{aspect-ratio:2/3;max-width:420px}
.sty-stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0}
.sty-stage img[data-on]{opacity:1}
.sty-pcap{position:absolute;left:8px;right:8px;bottom:8px;margin:0;color:#fff}
.sty-chapter{position:absolute;left:8px;top:8px}
@media (min-width:721px){
  .sty-film[data-ratio=portrait]{display:grid;grid-template-columns:420px 1fr;grid-template-areas:"stage side";gap:24px}
  .sty-film[data-ratio=portrait] > .sty-player{grid-area:stage}
  .sty-film[data-ratio=portrait] > .sty-side{grid-area:side;display:flex;flex-direction:column;gap:8px}
  .sty-film[data-ratio=portrait] .sty-side .sty-pcap{position:static;color:#222;font-size:20px;line-height:28px}
  .sty-film[data-ratio=portrait] .sty-stage:not([data-ask]) .sty-chapter,
  .sty-film[data-ratio=portrait] .sty-stage:not([data-ask]) .sty-pcap{display:none}
}
</style></head><body><main><div class="vstage" data-voice="on"><button data-testid="story-orb">o</button></div>
<div class="sty-film" data-testid="story-film" data-ratio="__RATIO__">
<div class="sty-side" data-testid="story-side"><span class="sty-chapter" data-testid="story-side-chapter"></span>
<p class="sty-pcap" data-testid="story-side-line"></p></div>
<div class="sty-player" data-mode="pictures" data-testid="story-player" data-ratio="__RATIO__">
<div class="sty-stage" data-testid="story-stage" data-step="-1" data-ratio="__RATIO__">
__IMGS__<span class="sty-chapter" data-testid="story-chapter"></span>
<p class="sty-pcap" data-testid="story-line"></p></div></div></div></main>
<script>
const S = __STORY__;
const words = {who:'Who', task:'The task', today:'Today', shortfall:'Where it falls short', cost:'What it costs them'};
(async () => {
  const stage = document.querySelector('[data-testid=story-stage]');
  let mark = null, last = null;
  for (let i = 0; i < 8; i++) {
    await fetch('/v2/clips/' + S.clipIds[i]);
    const scene = S.scenes[i];
    stage.setAttribute('data-step', String(i));
    if (scene) stage.removeAttribute('data-ask'); else stage.setAttribute('data-ask', '');
    if (scene && scene.chapter) mark = scene.chapter;
    const pill = scene ? words[mark] : '';
    const line = '<span class="sty-pcap__words">' + (scene ? scene.line : S.askLine) + '</span>';
    document.querySelector('[data-testid=story-chapter]').textContent = pill;
    document.querySelector('[data-testid=story-side-chapter]').textContent = pill;
    document.querySelector('[data-testid=story-line]').innerHTML = line;
    document.querySelector('[data-testid=story-side-line]').innerHTML = scene ? line : '';
    const own = scene ? scene.pictureAssetId : null;
    const shown = scene ? (own || last) : null;
    if (own) last = own;
    document.querySelectorAll('img[data-asset]').forEach((im) => {
      const on = im.getAttribute('data-asset') === shown;
      on ? im.setAttribute('data-on', '') : im.removeAttribute('data-on');
      on && !own ? im.setAttribute('data-held', '') : im.removeAttribute('data-held');
    });
    scene && !shown ? stage.setAttribute('data-ground', '') : stage.removeAttribute('data-ground');
    await new Promise((r) => setTimeout(r, 120));
  }
})();
</script></body></html>"""


def page_263(s: dict, ratio: str) -> str:
    drawn = s["build"]["story"]
    imgs = "".join(f'<img data-testid="story-picture" data-asset="{x["pictureAssetId"]}" '
                   f'src="/v2/assets/{x["pictureAssetId"]}">' for x in drawn["scenes"] if x.get("pictureAssetId"))
    return PLAYER_263.replace("__IMGS__", imgs).replace("__STORY__", json.dumps(drawn)).replace("__RATIO__", ratio)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def shoot(browser, tmp_path, s: dict, ratio: str, picture: bytes):
    html = page_263(s, ratio)
    camera = ff.FilmCamera(browser, {"cookies": [], "origins": []}, "http://film.test", tmp_path, inits=("",),
                           routes=(("http://film.test/p/**", lambda r: r.fulfill(status=200, content_type="text/html",
                                                                                 body=html)),
                                   ("**/v2/assets/**", lambda r: r.fulfill(status=200, content_type="image/png",
                                                                           body=picture)),
                                   ("**/v2/clips/**", lambda r: r.fulfill(status=200, content_type="audio/mpeg",
                                                                          body=b""))))
    return camera.shoot("p1", s)


# ----------------------------------------------------------------------------------------------- FR-1 the camera

def test_the_camera_reads_the_portrait_stage_and_the_laptops_words_column(browser, tmp_path):
    s = story(missing=5)
    frames, faults = shoot(browser, tmp_path, s, "portrait", png(16, 24))
    assert faults == [], faults
    assert len(frames) == 14
    by = {(f["scene"], f["viewport"]): f for f in frames}
    phone, laptop = by[(4, "phone")], by[(4, "laptop")]
    # the phone: `display: contents`, the caption over the stage's lower third, inside it; the stage 2:3
    assert phone["film_display"] == "contents" and phone["layout"] == "over" and phone["inside"] is True
    assert phone["ratio"] == "portrait" and phone["stage_ratio"] == pytest.approx(1.5, abs=0.01)
    assert phone["stage"]["w"] == 358 and phone["caption"] == LINES[3] and phone["chapter"] == "Where it falls short"
    # the laptop: a grid, the caption and the pill drawn beside the stage (the stage's own not drawn), whole
    assert laptop["film_display"] == "grid" and laptop["layout"] == "column"
    assert laptop["beside"] is True and laptop["in_window"] is True and laptop["clipped"] is False
    assert laptop["inside"] is False                                 # beside, never over the picture
    assert laptop["caption"] == LINES[3] and laptop["chapter"] == "Where it falls short"
    assert laptop["stage"] == {"w": 420, "h": 630} and laptop["caption_box"]["x"] >= 420
    # a frame left out: recorded on the frame, the picture before held still, never a fault
    assert by[(5, "phone")]["missing"] is True and by[(5, "laptop")]["held"] is True and by[(5, "laptop")]["shown"] == "a4"
    assert "missing" not in by[(4, "phone")]
    assert ff.stage_summary(frames) == {"phone": {"layouts": ["over"], "ratios": ["portrait"], "stages": ["358x537"]},
                                        "laptop": {"layouts": ["column"], "ratios": ["portrait"],
                                                   "stages": ["420x630"]}}


def test_a_landscape_film_keeps_261s_layout_on_the_laptop(browser, tmp_path):
    # FakePictures' 48 x 32 (and a film drawn before 275): the stage takes the picture's ratio, the caption stays over it
    frames, faults = shoot(browser, tmp_path, story(), "landscape", png(48, 32))
    assert faults == []
    laptop = next(f for f in frames if f["viewport"] == "laptop")
    assert laptop["layout"] == "over" and laptop["film_display"] == "contents" and laptop["inside"] is True
    assert laptop["ratio"] == "landscape" and laptop["stage_ratio"] < 1


def test_each_layout_is_held_to_its_own_rule():
    base = {"scene": 3, "path": "frames/scene-3-laptop.png", "caption": "x", "rows": 2}
    assert ff.frame_faults({**base, "layout": "column", "beside": True, "in_window": True, "clipped": False,
                            "inside": False}, "laptop") == []
    for bad in ({"beside": False}, {"in_window": False}, {"clipped": True}):
        said = ff.frame_faults({**base, "layout": "column", "beside": True, "in_window": True, "clipped": False,
                                **bad}, "laptop")
        assert len(said) == 1 and "not whole beside the stage" in said[0]["what"] and "263" in said[0]["owed"]
    said = ff.frame_faults({**base, "layout": "over", "inside": False}, "laptop")
    assert len(said) == 1 and "not wholly inside the stage" in said[0]["what"]
    assert [f["what"] for f in ff.frame_faults({**base, "layout": "over", "inside": True, "rows": 4}, "phone")] == [
        "scene 3's caption runs to 4 rows on the phone (at most 3)"]
    assert ff.frame_faults({**base, "layout": "over", "inside": True, "rows": 4}, "laptop") == []
    # a frame left out shows the picture before held, or the ground; neither is keel-web 263 FR-9's
    assert ff.frame_faults({**base, "layout": "over", "inside": True, "missing": True, "held": True}, "phone") == []
    assert ff.frame_faults({**base, "layout": "over", "inside": True, "missing": True, "ground": True}, "phone") == []
    assert "263 FR-9" in ff.frame_faults({**base, "layout": "over", "inside": True, "missing": True}, "phone")[0]["owed"]


def test_a_pictures_size_is_recorded_both_sizes_accepted(tmp_path):
    assert ff.picture_drawn((1024, 1536)) == {"ratio": "portrait", "drawn": "275"}
    assert ff.picture_drawn((1536, 1024)) == {"ratio": "landscape", "drawn": "before 275"}
    assert ff.picture_drawn((48, 32)) == {"ratio": "landscape", "drawn": "other"}
    assert ff.picture_drawn(None) == {"ratio": None, "drawn": None}
    s = story(missing=2)
    pictures = ff.fetch_pictures(lambda path: (200, png(16, 24), "image/png"), s, tmp_path)
    assert pictures[0]["png"] == [16, 24] and pictures[0]["ratio"] == "portrait"
    assert pictures[1]["missing"] is True and ff.picture_faults(pictures) == []


def test_the_problem_films_frame_left_out_is_no_fault():
    s = story(missing=6)
    assert ff.chapter_faults(s) == [] and ff.missing_scenes(s) == [6]
    s["build"]["story"]["scenes"][5].pop("pictureMissing")
    assert any("scene 6 is served with no picture and no `pictureMissing`" in f["what"] for f in ff.chapter_faults(s))


# ----------------------------------------------------------------------------------------------- FR-2 the founder's screens

def test_the_tally_and_the_failed_lines_are_keel_webs():
    rows = [{"status": "passed"}, {"status": "passed"}, {"status": "drawn"}, {"status": "failed"}, {"status": "planned"},
            {"status": "dropped"}, {"status": "planned"}]
    assert ss.plan_tally(rows) == "7 frames planned · 2 passed · 1 checking · 1 drawing again · 1 left out"
    assert ss.plan_tally(rows, 5) == "5 of 7 pictures kept · 7 frames planned · 2 passed · 1 checking · 1 drawing " \
                                     "again · 1 left out"
    assert ss.plan_tally([{"status": "planned"}]) == "1 frame planned"
    assert ss.picture_failed_say(None) == "Keel could not draw that part. Say it again?"
    assert ss.picture_failed_say("  ") == "Keel could not draw that part. Say it again?"
    assert ss.picture_failed_say("The film shows a screen with words on it.") == (
        "Keel could not draw that part: The film shows a screen with words on it. Say it again?")
    assert ss.failed_say("joy", "It ends on the product!") == (
        "Keel could not draw what they get: It ends on the product. Say that part again?")
    assert ss.failed_say("joy") == "Keel could not draw what they get. Say that part again?"


def test_the_words_mirror_keel_web_263():
    translate = WEB / "src" / "lib" / "translate.ts"
    plan = WEB / "src" / "components" / "story" / "FramePlan.tsx"
    if not plan.exists() or not translate.exists():
        pytest.skip("keel-web 263 not in the checkout")
    text = translate.read_text(encoding="utf-8")
    assert "`Keel could not draw that part: ${bareReason(reason)}. Say it again?`" in text
    assert "`Keel could not draw ${part}: ${bareReason(reason)}. Say that part again?`" in text
    assert 'say: "Keel could not draw that part. Say it again?"' in text
    for words in ("frames\"} planned", "passed`", "checking`", "drawing again`", "left out`", "pictures kept`"):
        assert words in text, words
    source = plan.read_text(encoding="utf-8")
    for testid in ("story-plan", "story-plan-tally", "story-plan-row", "story-plan-reason", "story-plan-word"):
        assert f'data-testid="{testid}"' in source
    player = (WEB / "src" / "lib" / "story" / "StoryPlayer.tsx").read_text(encoding="utf-8")
    for testid in ("story-film", "story-side", "story-side-line", "story-side-chapter"):
        assert f'"{testid}"' in player, testid


PLAN_PAGE = """<!doctype html><html><head><meta charset="utf-8"></head><body><div class="vstage" data-voice="on"></div>
<div data-testid="story-building"><section data-testid="story-plan"><p data-testid="story-plan-tally"></p><ol></ol>
</section><h1 data-testid="story-q">Keel is drawing your story</h1></div>
<script>
const steps = [["planned", "planned"], ["passed", "drawn"], ["passed", "dropped"]];
let at = 0;
function draw() {
  const rows = steps[Math.min(at, steps.length - 1)];
  const words = {drawn: 'checking', failed: 'drawing again', dropped: 'left out'};
  const count = (s) => rows.filter((r) => r === s).length;
  const parts = [rows.length + ' frames planned'];
  [['passed', 'passed'], ['drawn', 'checking'], ['failed', 'drawing again'], ['dropped', 'left out']]
    .forEach(([s, w]) => { if (count(s)) parts.push(count(s) + ' ' + w); });
  document.querySelector('[data-testid=story-plan-tally]').textContent = parts.join(' · ');
  document.querySelector('ol').innerHTML = rows.map((s, i) => '<li data-testid="story-plan-row" data-scene="' + (i + 1)
    + '" data-status="' + s + '"><span data-testid="story-plan-mark" aria-label="' + s + '"></span>'
    + (words[s] ? '<span data-testid="story-plan-word">' + words[s] + '</span>' : '')
    + (s === 'dropped' ? '<span data-testid="story-plan-reason">Text was seen in the picture.</span>' : '') + '</li>').join('');
  at += 1;
  if (at < steps.length) setTimeout(draw, 300);
}
draw();
</script></body></html>"""


def test_the_building_screens_plan_is_read_and_held_to_its_rule(browser):
    calls = {"n": 0}

    def read_view():
        calls["n"] += 1
        state = "building" if calls["n"] < 6 else "ready"
        return {"build": {"state": state, "pictures": {"plan": [{"scene": 1, "status": "passed"},
                                                                {"scene": 2, "status": "dropped"}], "kept": 0}}}
    view, record = ff.watch_building(browser, {"cookies": [], "origins": []}, "http://film.test", "p1", read_view,
                                     inits=("",), poll_ms=200,
                                     routes=(("http://film.test/p/**", lambda r: r.fulfill(
                                         status=200, content_type="text/html; charset=utf-8", body=PLAN_PAGE)),))
    assert record["error"] is None and record["drawn"] is True and record["state"] == "ready"
    assert record["path"] == "define/story/check" and record["opened_while"] == "building"
    last = record["reads"][-1]
    assert last["tally"] == "2 frames planned · 1 passed · 1 left out" and all(r["tally_holds"] for r in record["reads"])
    assert last["rows"][1] == {"scene": "2", "status": "dropped", "kept": False, "word": "left out",
                               "reason": "Text was seen in the picture.", "mark": "dropped"}
    assert record["served"] == [["1:passed", "2:dropped"]]
    assert ff.building_faults(record, view) == []
    wrong = {**record, "reads": [{**last, "tally": "2 frames planned", "tally_holds": False}]}
    assert "263 FR-8" in ff.building_faults(wrong, view)[0]["owed"]


def test_a_failed_builds_line_is_held_with_and_without_its_reason():
    failed = {"build": {"state": "failed", "failedScene": 4, "failedReason": "A label had writing on it."}}
    assert ff.building_faults({"failed_said": "Keel could not draw that part: A label had writing on it. Say it again?"},
                              failed) == []
    said = ff.building_faults({"failed_said": "Keel could not draw that part. Say it again?"}, failed)
    assert len(said) == 1 and "263 FR-10" in said[0]["owed"]
    before = {"build": {"state": "failed", "failedScene": 4}}
    assert ff.building_faults({"failed_said": "Keel could not draw that part. Say it again?"}, before) == []
    chapter = {"build": {"state": "failed", "failedChapter": "solves", "failedReason": "It shows no tick."}}
    assert ff.building_faults({"failed_said": "Keel could not draw what it solves: It shows no tick. Say that part "
                                              "again?"}, chapter) == []


LINK_PAGE = """<!doctype html><html><head><style>
.sty-film{display:contents} .sty-side{display:none}
@media (min-width:721px){ .sty-film[data-ratio=portrait]{display:grid;grid-template-columns:420px 1fr}
  .sty-film[data-ratio=portrait] > .sty-side{display:block}
  .sty-film[data-ratio=portrait] .sty-stage:not([data-ask]) .sty-pcap{display:none} }
.sty-stage{width:100%;max-width:420px;aspect-ratio:2/3}
</style></head><body><div data-testid="ai-story" data-kind="problem">
<div class="sty-film" data-testid="story-film" data-ratio="portrait">
<div class="sty-side" data-testid="story-side"><span data-testid="story-side-chapter">The task</span>
<p class="sty-pcap" data-testid="story-side-line">They keep the day's list.</p></div>
<div data-testid="story-player" data-state="playing"><div class="sty-stage" data-testid="story-stage" data-step="1"
data-ratio="portrait"><span data-testid="story-chapter">The task</span>
<p class="sty-pcap" data-testid="story-line">They keep the day's list.</p></div></div></div></div>
<div data-testid="copilot-still" data-ratio="portrait" style="width:80px;height:120px"></div></body></html>"""


@pytest.mark.parametrize("viewport,layout", [((1280, 800), "column"), ((390, 844), "over")])
def test_the_links_film_and_the_copilot_still_are_read_as_drawn(browser, viewport, layout):
    context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
    page = context.new_page()
    page.set_content(LINK_PAGE)
    film = page.evaluate(ivs.FILM_JS)
    assert film["layout"] == layout and film["ratio"] == "portrait" and film["mode"] == "pictures"
    assert film["sig"]["line"] == "They keep the day's list." and film["chapter"] == "The task"
    assert film["captionFrom"] == ("story-side-line" if layout == "column" else "story-line")
    assert tvs.still_of(page) == {"still_ratio": "portrait", "still_box": [80, 120]}
    context.close()


# ----------------------------------------------------------------------------------------------- FR-3 the reader

def test_each_frames_label_names_the_viewport_and_the_layout(tmp_path):
    phone = {"scene": 2, "viewport": "phone", "size": "390x844", "path": "frames/scene-2-phone.png", "layout": "over",
             "ratio": "portrait", "stage": {"w": 358, "h": 537}}
    laptop = {**phone, "viewport": "laptop", "size": "1280x800", "path": "frames/scene-2-laptop.png",
              "layout": "column", "stage": {"w": 420, "h": 630}}
    assert fread.frame_label(phone) == ("Frame -- scene 2 on the phone (390x844), the caption over the picture's lower "
                                        "third, a tall stage 358 x 537, as the founder's player held it")
    assert fread.frame_label(laptop) == ("Frame -- scene 2 on the laptop (1280x800), the caption beside the picture, a "
                                         "tall stage 420 x 630, as the founder's player held it")
    assert "this scene's own picture left out (the picture before held still)" in fread.frame_label(
        {**laptop, "missing": True, "held": True})
    # a frame captured before 167 (261's layout): the caption over the picture on both viewports
    old = {"scene": 1, "viewport": "laptop", "size": "1280x800", "path": "frames/scene-1-laptop.png"}
    assert fread.frame_label(old).startswith("Frame -- scene 1 on the laptop (1280x800), the caption over the picture's")
    for f in (phone, laptop):
        (tmp_path / f["path"]).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f["path"]).write_bytes(png(4, 6))
    labels = [i["label"] for i in fread.images(tmp_path, {"frames": [phone, laptop]})]
    assert labels == [fread.frame_label(phone), fread.frame_label(laptop)]


def test_the_readers_prompt_names_the_layout_and_the_rubric_is_unmoved():
    prompt = (REPO / "quality" / "readers" / "film-reader.md").read_text(encoding="utf-8")
    assert prompt.count("the caption on the picture or beside it, as each frame's") == 2
    assert "the caption beside the picture" in prompt
    rubric = (REPO / "quality" / "FILM-RUBRIC.md").read_text(encoding="utf-8")
    assert "beside the picture" not in rubric                       # the rubric's words unchanged by this spec


# ----------------------------------------------------------------------------------------------- FR-5

def test_no_respondent_question_instruction_is_touched_here():
    # the mirrors read keel-web's screens and keel-cloud's served fields; nothing here writes or reads an instruction
    # that generates a respondent's question (the AI-avatar spoken-form guidelines untouched)
    for module in (ff, ss, ivs, fread, tvs):
        assert "respondent-questions" not in Path(module.__file__).read_text(encoding="utf-8")
