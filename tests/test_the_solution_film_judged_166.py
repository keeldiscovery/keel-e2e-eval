"""Spec 166: the solution film walked and judged, the table ranked and compared -- the mirrors `make unit` holds, nothing
paid (FR-8).

The founder's solution in an entry's words (`film_frames.entry_idea_beats`, on the payroll and Lullaby fixtures: the
brand, the four beats, the setup-none case, the joy, the spoken-form caps); the camera on the idea film (the chapter
keys, the plate frame, a dropped picture) on a local page; the solution's folder; the solution request's parts in
order and the size rule; the score file's shape for `kind: solution`; the table's rank (both films, one film, a failed
leg), the verdict on either film and the comparison with a baseline; the walk's plan with both halves, SCOPES, ONLY and
the preflight's refusals; the solution study's people, lock and bundle -- no stack and no model.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from playwright.sync_api import sync_playwright

from harness import film_frames as ff
from harness import film_strangers as fs
from harness import story_screens as ss
from quality import film as film_walk
from quality import film_reader as fread
from quality import film_rubric as fr
from quality import film_table as ft
from quality import readers

REPO = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / "fixtures" / "film_166"
FIX_163 = Path(__file__).resolve().parent / "fixtures" / "film_163"


def entry(name: str) -> dict:
    return yaml.safe_load((FIX / f"{name}.yaml").read_text(encoding="utf-8"))


PAYROLL_STORY = {"person": {"who": "payroll practitioners", "job": "run payroll"},
                 "limits": ["The hours come from systems that don't agree", "Nobody tells them when a rate changes",
                            "Mistakes are found after the money has gone"],
                 "cost": "A pay run they check twice and still fear"}
LULLABY_STORY = {"person": {"who": "parents of babies under six months",
                            "job": "work out what the baby needs and settle them"},
                 "limits": ["They cannot tell what the cry means", "They try one thing after another"],
                 "cost": "Twenty minutes of guessing every time"}


# ----------------------------------------------------------------------------------------------- FR-1 the founder's words

def test_the_payroll_solution_in_its_own_words_four_beats_and_no_setup():
    said = ff.entry_idea_beats(entry("payroll"), PAYROLL_STORY)
    assert [n for n, _ in said["beats"]] == [1, 2, 3, 4]
    beats = dict(said["beats"])
    # the brand: the name, a tagline under eight words (the offer name runs to twelve: the short name), a swatch
    assert said["brand"]["name"] == "Runsure" and said["brand"]["tagline"] == "A checked pay run"
    assert said["brand"]["colour"] in ss.BRAND_SWATCHES
    assert said["brand"]["colour"] == ss.BRAND_SWATCHES[98 % len(ss.BRAND_SWATCHES)]
    # beat 1: the statement's first sentence alone, then the steps -- trigger, the actor doing the mechanism -- the output
    assert beats[1].startswith("A checker that reads every line of the pay run and flags each one that changed since "
                               "last period.") and "It runs before sign-off" not in beats[1]
    assert "When the run is ready to be signed off, the practitioner opens the checker" in beats[1]
    assert beats[1].endswith("What comes out is every line that changed, flagged before sign-off.")
    # beat 2: nothing recorded to set up -- the setup-none words (keel-cloud 271 FR-4 reads none)
    assert beats[2] == ff.SETUP_NONE and said["setup"] == []
    # beat 3: the mechanism once, then one clause a limitation of the problem story -- spec 168 FR-3: each answered
    # in the entry's words, the brand's name and the mechanism as a bare clause; `not_assumed` never said
    for limit in PAYROLL_STORY["limits"]:
        assert f"{limit}: Runsure opens the checker, which reads the run and compares every line with last period." \
            in beats[3]
    assert "takes care of that" not in beats[3]
    assert "the mistakes stop for good" not in json.dumps(said)
    # beat 4: the joy set against the problem's cost (no Relative-advantage row: the cost's opposite)
    assert beats[4] == "Instead of a pay run they check twice and still fear, they get no more a pay run they check " \
                       "twice and still fear."
    assert said["then"][1][0].startswith("First: when the run is ready") and said["then"][4][0].startswith(
        "They get back what it cost them")
    assert ff.idea_beat_faults(said, entry("payroll"), PAYROLL_STORY) == []


def test_the_lullaby_solution_with_its_setup_and_its_joy():
    said = ff.entry_idea_beats(entry("lullaby"), LULLABY_STORY)
    beats = dict(said["beats"])
    assert said["brand"]["name"] == "Lullaby" and said["brand"]["tagline"] == "Something that helps at night"
    # the founder's Adoption-friction rows that are not the mechanism's own step: the microphone, not the ten seconds
    assert said["setup"] == ["let the app use the microphone at night"]
    assert beats[2] == "Before they can start, they need to let the app use the microphone at night."
    assert "the parent holds the phone near the cot for about ten seconds while it listens" in beats[1]
    assert said["joy"] == "fewer tries before the baby settles"
    assert beats[4] == "Instead of twenty minutes of guessing every time, they get fewer tries before the baby settles."
    assert "stops the guessing" not in json.dumps(said) and "settles the baby faster" not in json.dumps(said)
    assert ff.idea_beat_faults(said, entry("lullaby"), LULLABY_STORY) == []


def test_beat_three_answers_each_limitation_with_the_entrys_mechanism_168():
    # spec 168 FR-3: *{Limit}: {name} {mechanism}.* -- the same clause for every limitation (the entry holds no answer
    # per limitation, none is invented); the stock *takes care of that* gone; `then[3]` unchanged
    for name, story in (("payroll", PAYROLL_STORY), ("lullaby", LULLABY_STORY)):
        said = ff.entry_idea_beats(entry(name), story)
        beat3 = dict(said["beats"])[3]
        brand = said["brand"]["name"]
        mechanism = ff._bare_end(entry(name)["solution_mechanism"]["mechanism"])
        for limit in story["limits"]:
            assert f"{limit}: {brand} {mechanism}." in beat3
        assert beat3.count(f": {brand} {mechanism}.") == len(story["limits"])
        assert "takes care of that" not in json.dumps(said)
        steps = ff._steps_sentence(entry(name)["solution_mechanism"])
        assert said["then"][3] == ["Because " + ff._lower_first(steps).rstrip(".") + ", every one of those is dealt with."]
        # FR-5: the spoken-form caps as today (one wording, no placeholder, no number the entry does not say)
        assert ff.idea_beat_faults(said, entry(name), story) == []
    assert dict(ff.entry_idea_beats(entry("lullaby"), LULLABY_STORY)["beats"])[3].endswith(
        "They try one thing after another: Lullaby holds the phone near the cot for about ten seconds while it listens.")
    # a mechanism that opens on its own subject, not its verb: the name leads it in (one rule, nothing invented)
    own_subject = {**entry("payroll"), "solution_mechanism": {
        **entry("payroll")["solution_mechanism"], "mechanism": "a checker reads the run and compares every line."}}
    beat3 = dict(ff.entry_idea_beats(own_subject, PAYROLL_STORY)["beats"])[3]
    assert "Nobody tells them when a rate changes: With Runsure, a checker reads the run and compares every line." in beat3
    assert ff.limit_answer("Runsure", {}) == ""
    no_mechanism = {**entry("payroll"), "solution_mechanism": {"actor": "the practitioner"}}
    beat3 = dict(ff.entry_idea_beats(no_mechanism, PAYROLL_STORY)["beats"])[3]
    assert "Nobody tells them when a rate changes." in beat3 and "Runsure." not in beat3.split("like this.", 1)[1]


def test_every_beat_is_held_to_the_spoken_form_caps():
    said = ff.entry_idea_beats(entry("lullaby"), LULLABY_STORY)
    bad = {**said, "beats": [(1, "It costs {cost} for 37 people."), (2, "None"), (3, "x" * 20_000), (4, "ok")],
           "brand": {"name": "One two three four five six", "tagline": "a b c d e f g h i"}}
    faults = ff.idea_beat_faults(bad, entry("lullaby"), LULLABY_STORY)
    assert any("placeholder" in f for f in faults) and any("'37'" in f for f in faults)
    assert any("20,000" in f for f in faults) and any("one to five words" in f for f in faults)
    assert any("past eight words" in f for f in faults)


def test_the_idea_is_told_on_the_wire_as_the_page_sends_it():
    sent = []
    answers = {1: [{"next": 1, "done": False, "ask": ss.STEP_ASK}, {"next": 2, "done": True}],
               3: [{"next": 3, "done": False, "readback": "I did not understand how x is solved. Can you think about it?"},
                   {"next": 4, "done": True}]}

    def call(method, path, body):
        sent.append((method, path, body))
        n = int(path.rsplit("/", 1)[-1]) if "/turns/" in path else None
        queue = answers.get(n)
        return 200, (queue.pop(0) if queue else {"next": "check", "done": True})
    wire = ss.IdeaWire(call, "s1")
    wire.stamp()
    wire.brand(name="Runsure", colour="#1f7a5a", tagline="A checked pay run")
    told = wire.tell([(1, "one"), (2, "two"), (3, "three"), (4, "four")], {1: ["steps"], 3: ["again"]})
    assert [b["turn"] for b in told] == [1, 2, 3, 4]
    turns = [(p.rsplit("/", 1)[-1], b) for m, p, b in sent if "/turns/" in p]
    assert turns == [("1", {"text": "one"}), ("1", {"text": "steps"}), ("2", {"text": "two"}), ("3", {"text": "three"}),
                     ("3", {"text": "again", "correction": True}), ("4", {"text": "four"})]
    assert sent[0] == ("POST", "/v2/projects/s1/story/confirm", None)
    assert sent[1] == ("PUT", "/v2/projects/s1/idea/brand", {"name": "Runsure", "colour": "#1f7a5a",
                                                             "tagline": "A checked pay run"})
    with pytest.raises(AssertionError, match="still open"):
        ss.IdeaWire(lambda m, p, b: (200, {"done": False, "ask": "?"}), "s2").beat(1, "words")


# ----------------------------------------------------------------------------------------------- FR-2 the solution film

IDEA_LINES = ["This time, Runsure is on the screen.", "You open Runsure when the run is ready.",
              "Runsure flags every line that changed.", "The hours, the rates, the late mistakes.",
              "Every line checked, not a sample.", "A pay run you can sign off calmly."]
IDEA_CHAPTERS = {1: "before", 2: "task", 4: "solves", 5: "better", 6: "joy"}


def idea_view(missing: int | None = None) -> dict:
    scenes = []
    for n, line in enumerate(IDEA_LINES, 1):
        scene = {"line": line, "pictogramId": "screen", "clipId": f"k{n}", "pictureAssetId": f"i{n}",
                 "screen": {"name": "Runsure", "colour": "#1f7a5a"},
                 **({"chapter": IDEA_CHAPTERS[n]} if n in IDEA_CHAPTERS else {}), **({"joy": True} if n == 6 else {})}
        if n == 4:
            scene["marks"] = [{"limit": "The hours", "mark": "tick"}, {"limit": "The late mistakes", "mark": "cross"}]
        if n == missing:
            scene["pictureAssetId"], scene["pictureMissing"] = None, True
        scenes.append(scene)
    return {"brand": {"name": "Runsure", "tagline": "A checked pay run", "colour": "#1f7a5a"},
            "workflow": [{"step": "open Runsure when the run is ready", "by": "PERSON"}], "setup": [], "setupNone": True,
            "statement": "Runsure flags every line that changed.", "joy": "A pay run you can sign off calmly",
            "limitAnswers": [{"limit": "The hours", "solved": True, "how": "reads both systems"},
                             {"limit": "The late mistakes", "solved": False, "how": None}],
            "advantage": "Every line checked, not a sample.", "verdictLine": "I will call this real ...",
            "pilotAsk": "Now Runsure is defined. Would you like ...", "pilot": True,
            "build": {"state": "ready", "failedReason": None,
                      "story": {"scenes": scenes, "askLine": "Is that how it would go for you?",
                                "clipIds": [f"k{n}" for n in range(1, 8)], "sheetAssetId": "sheet1",
                                "plate": {"name": "Runsure", "tagline": "A checked pay run", "colour": "#1f7a5a"}},
                      "pictures": {"setting": {"place": "a small office", "props": ["a desk", "a lamp", "a screen"],
                                               "garments": ["a cardigan"], "timeOfDay": "late afternoon"},
                                   "prompts": [{"scene": None, "attempt": 1, "prompt": "Draw this one character..."}],
                                   "plan": [{"scene": n, "chapter": IDEA_CHAPTERS.get(n), "line": line,
                                             "contains": f"frame {n}", "status": "passed", "reason": None}
                                            for n, line in enumerate(IDEA_LINES, 1)],
                                   "reviews": [{"scene": 1, "attempt": 1, "character": True, "scene_ok": True,
                                                "text_seen": False, "brand": True, "reason": "fine"}], "kept": 0}}}


def _as_283(view: dict) -> dict:
    """Spec 172 FR-4 (keel-cloud 283 FR-1): the same film in three chapters -- the steps go on where `solves` and
    `better` were, no marks."""
    for scene in view["build"]["story"]["scenes"]:
        if scene.get("chapter") in ("solves", "better"):
            scene.pop("chapter")
        scene.pop("marks", None)
    for row in view["build"]["pictures"]["plan"]:
        if row.get("chapter") in ("solves", "better"):
            row["chapter"] = None
    return view


def test_the_idea_films_chapter_keys_and_a_dropped_picture():
    view = _as_283(idea_view(missing=3))
    assert ff.idea_chapter_faults(view) == []                       # a dropped frame is recorded, never a fault
    assert ff.missing_scenes(view) == [3]
    # spec 172 FR-4: a draft still carrying 271's `solves` / `better` is a DRIFT line for each, never the order's fault
    drift = ff.idea_chapter_faults(idea_view())
    assert drift and all(f.get("drift") for f in drift) and any("'solves'" in f["what"] for f in drift)
    bad = _as_283(idea_view())
    scenes = bad["build"]["story"]["scenes"]
    scenes[1]["chapter"], scenes[3]["chapter"] = "joy", "task"
    scenes[5].pop("joy")
    scenes[2]["pictureAssetId"] = None
    said = [f["what"] for f in ff.idea_chapter_faults(bad)]
    assert any("chapter marks" in w for w in said) and any("joy scene" in w for w in said)
    assert any("scene 3 is served with no picture and no `pictureMissing`" in w for w in said)


def png() -> bytes:
    import struct
    import zlib

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\x88\x88\x88" * 6 for _ in range(4))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 6, 4, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


IDEA_PLAYER = """<!doctype html><html><head><style>
body{margin:0;font:16px/24px sans-serif} .sty-stage{position:relative;width:100%;max-width:640px;aspect-ratio:2/3;
background:#888;overflow:hidden} .sty-stage img{position:absolute;inset:0;width:100%;height:100%;opacity:0}
.sty-stage img[data-on]{opacity:1} .sty-pcap{position:absolute;left:8px;right:8px;bottom:8px;margin:0;color:#fff}
.idea-plate{position:fixed;inset:0;background:#1f7a5a;color:#fff}
</style></head><body><main><div class="vstage" data-voice="begin"><button data-testid="story-orb">o</button></div>
<div class="sty-player" data-mode="pictures" data-testid="idea-story-player"><div class="sty-stage" data-testid="story-stage" data-step="-1">
__IMGS__<span class="sty-chapter" data-testid="story-chapter"></span>
<p class="sty-pcap" data-testid="story-line"></p></div></div></main>
<script>
const S = __STORY__;
const words = {before:'Before', task:'The task', solves:'What it solves', better:'Better', joy:'What they get'};
document.querySelector('[data-testid=story-orb]').addEventListener('click', async () => {
  document.querySelector('.vstage').setAttribute('data-voice', 'on');
  const plate = document.createElement('div');
  plate.className = 'idea-plate idea-plate--full'; plate.setAttribute('data-testid', 'idea-plate');
  plate.innerHTML = '<p>' + S.plate.name + '</p><p>' + S.plate.tagline + '</p>';
  document.body.appendChild(plate);
  await new Promise((r) => setTimeout(r, 900));        // the plate alone, then the film
  plate.remove();
  const stage = document.querySelector('[data-testid=story-stage]');
  let mark = null, last = null;
  for (let i = 0; i <= S.scenes.length; i++) {
    await fetch('/v2/clips/' + S.clipIds[i]);
    const scene = S.scenes[i];
    stage.setAttribute('data-step', String(i));
    if (scene && scene.chapter) mark = scene.chapter;
    document.querySelector('[data-testid=story-chapter]').textContent = scene ? words[mark] : '';
    document.querySelector('[data-testid=story-line]').innerHTML = '<span class="sty-pcap__words">' + (scene ? scene.line : S.askLine) + '</span>';
    // keel-web 263 FR-9: a frame left out holds the picture before, still (`data-held`)
    const own = scene ? scene.pictureAssetId : null, shown = scene ? (own || last) : null;
    if (own) last = own;
    document.querySelectorAll('img[data-asset]').forEach((im) => { const on = im.getAttribute('data-asset') === shown;
      on ? im.setAttribute('data-on', '') : im.removeAttribute('data-on');
      on && !own ? im.setAttribute('data-held', '') : im.removeAttribute('data-held'); });
    await new Promise((r) => setTimeout(r, 120));
  }
});
</script></body></html>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_solution_film_is_captured_with_its_plate_and_its_chapters(browser, tmp_path):
    view = idea_view(missing=3)
    drawn = view["build"]["story"]
    imgs = "".join(f'<img data-testid="story-picture" data-asset="{x["pictureAssetId"]}" '
                   f'src="/v2/assets/{x["pictureAssetId"]}">' for x in drawn["scenes"] if x.get("pictureAssetId"))
    page = IDEA_PLAYER.replace("__IMGS__", imgs).replace("__STORY__", json.dumps(drawn))
    asked, opened = [], []

    def serve_page(route):
        opened.append(route.request.url)
        route.fulfill(status=200, content_type="text/html", body=page)

    def serve_clip(route):
        asked.append(route.request.url.rsplit("/", 1)[-1])
        route.fulfill(status=200, content_type="audio/mpeg", body=b"")

    camera = ff.FilmCamera(browser, {"cookies": [], "origins": []}, "http://film.test", tmp_path, inits=("",),
                           routes=(("http://film.test/p/**", serve_page),
                                   ("**/v2/assets/**", lambda r: r.fulfill(status=200, content_type="image/png",
                                                                           body=png())),
                                   ("**/v2/clips/**", serve_clip)), kind="solution")
    frames, faults = camera.shoot("s1", view)
    assert faults == [] and all(u.endswith("/p/s1/define/idea/check") for u in opened)
    assert [f["scene"] for f in frames] == ["plate", "plate"] + [n for n in range(1, 7) for _ in range(2)]
    plate = frames[0]
    assert plate["path"] == "frames/plate-phone.png" and "Runsure" in plate["caption"] and "A checked pay run" in \
        plate["caption"]
    by = {(f["scene"], f["viewport"]): f for f in frames}
    assert by[(2, "phone")]["chapter"] == "The task" and by[(4, "laptop")]["chapter"] == "What it solves"
    assert by[(6, "phone")]["chapter"] == "What they get" and by[(6, "phone")]["caption"] == IDEA_LINES[5]
    # the dropped frame (spec 167, keel-web 263 FR-9): the picture before held still, recorded `missing`, no fault
    assert by[(3, "laptop")]["shown"] == "i2" and by[(3, "laptop")]["held"] and by[(3, "laptop")]["missing"]
    assert all((tmp_path / f["path"]).is_file() for f in frames)
    assert asked.count("k1") == 2 and asked.count("k7") == 2


def test_the_solution_folder_its_pictures_and_its_log(tmp_path):
    view = idea_view(missing=3)

    def get_bytes(path):
        return 200, png(), "image/png"
    pictures = ff.fetch_pictures(get_bytes, view, tmp_path)
    assert [p["scene"] for p in pictures] == [1, 2, 3, 4, 5, 6, "sheet"]
    assert pictures[2]["missing"] is True and pictures[2]["path"] is None and ff.picture_faults(pictures) == []
    out = ff.film_dir(tmp_path / "walk", "e1", "solution")
    assert out == tmp_path / "walk" / "film" / "e1" / "solution"
    ff.write_folder(out, story=view, film={"kind": "solution"}, idea=ff.idea_board(view))
    prompts = json.loads((out / "prompts.json").read_text())
    assert set(prompts) >= {"setting", "prompts", "plan", "reviews", "kept", "failedReason"}
    assert len(prompts["plan"]) == 6 and prompts["kept"] == 0
    idea = json.loads((out / "idea.json").read_text())
    assert idea["joy"] == "A pay run you can sign off calmly" and idea["setupNone"] is True and "build" not in idea
    lines = ff.lines_of(view)
    assert lines[3]["marks"][1]["mark"] == "cross" and lines[5]["joy"] and lines[2]["pictureMissing"]
    assert lines[-1]["scene"] == "ask"
    # the problem's folder keeps its two files' shape
    ff.write_folder(tmp_path / "p", story={"build": {"pictures": {"setting": {}, "prompts": [], "plan": [1]}}},
                    film={})
    assert set(json.loads((tmp_path / "p" / "prompts.json").read_text())) == {"setting", "prompts"}
    assert not (tmp_path / "p" / "idea.json").exists()


def test_the_solution_ledger_names_its_rows():
    rows = [{"project_id": "s1", "kind": "SPEND", "action": a, "credits": 0, "actual_cost_micro_usd": 1000}
            for a in ("IDEA_TURN", "IDEA_TURN", "STORY_PICTURES", "PICTURE_REVIEW", "STORY_CHECK")] + \
           [{"project_id": "p1", "kind": "SPEND", "action": "IDEA_TURN", "credits": 0, "actual_cost_micro_usd": 9}]
    spent = ff.ledger_rows(rows, "s1", charges=ff.IDEA_CHARGES)
    assert spent["by_charge"] == {"IDEA_TURN": 2, "STORY_CHECK": 1, "STORY_PICTURES": 1, "PICTURE_REVIEW": 1}
    assert spent["usd"] == 0.005 and "by_charge" not in ff.ledger_rows(rows, "s1")


# ----------------------------------------------------------------------------------------------- FR-4 the reader

def solution_walk(root: Path, *, entry_id: str = "fixture-film", big: bool = False) -> Path:
    """A walk with a problem film (163's fixture folder) and a solution film beside it."""
    walk = root / "20261125T120000Z-film-walk"
    problem = walk / "film" / entry_id
    problem.mkdir(parents=True)
    (problem / "story.json").write_text(json.dumps(PAYROLL_STORY))
    (problem / "film.json").write_text(json.dumps({"entry": {"id": entry_id, "path": str(FIX_163 / "entry.yaml")},
                                                   "frames": [], "pictures": []}))
    folder = walk / "film" / entry_id / "solution"
    (folder / "frames").mkdir(parents=True)
    (folder / "pictures").mkdir(parents=True)
    view = idea_view()
    frames, pictures = [], []
    body = png() + (b"\0" * 200_000 if big else b"")
    for n in ["plate", *range(1, 7)]:
        for v, size in (("phone", "390x844"), ("laptop", "1280x800")):
            rel = f"frames/{'plate' if n == 'plate' else f'scene-{n}'}-{v}.png"
            (folder / rel).write_bytes(body)
            frames.append({"scene": n, "viewport": v, "size": size, "path": rel})
    for n in range(1, 7):
        (folder / f"pictures/scene-{n}.png").write_bytes(png())
        pictures.append({"scene": n, "asset": f"i{n}", "path": f"pictures/scene-{n}.png", "png": [6, 4]})
    (folder / "pictures/sheet.png").write_bytes(png())
    pictures.append({"scene": "sheet", "asset": "sheet1", "path": "pictures/sheet.png", "png": [6, 4]})
    film = {"spec": "166", "kind": "solution", "entry": {"id": entry_id, "path": str(FIX_163 / "entry.yaml")},
            "project_id": "s1", "problem_project_id": "p1", "stack": {"keel-cloud": "c7079b59", "keel-web": "1ca065b3"},
            "frames": frames, "pictures": pictures, "dollars": 0.0, "measures": {"faults": []},
            "beats": [{"turn": n, "asked": f"Idea question {n}?", "founder": f"Words {n}.", "ask": None,
                       "readback": f"Read {n}."} for n in (1, 2, 3, 4)],
            "verdict_line": view["verdictLine"], "pilot_ask": view["pilotAsk"]}
    ff.write_folder(folder, story=view, film=film, idea=ff.idea_board(view))
    return walk


def test_every_film_folder_is_read_with_its_kind(tmp_path):
    walk = solution_walk(tmp_path)
    folders = fread.film_folders(walk)
    assert [(fread.entry_of(f), fread.film_kind(f)) for f in folders] == [("fixture-film", "problem"),
                                                                           ("fixture-film", "solution")]
    assert [fread.film_kind(f) for f in fread.film_folders(walk, kind="solution")] == ["solution"]
    assert fread.score_path(Path("s"), "w", "e", "solution") == Path("s/w-film-e-solution.json")
    assert fread.score_path(Path("s"), "w", "e") == Path("s/w-film-e.json")


def test_the_solution_request_names_its_parts_in_order(tmp_path):
    walk = solution_walk(tmp_path)
    folder = walk / "film" / "fixture-film" / "solution"
    film = json.loads((folder / "film.json").read_text())
    card = fread.load_entry_card(film)
    request = fread.build_request(folder, film, json.loads((folder / "story.json").read_text()),
                                  json.loads((folder / "prompts.json").read_text()), card,
                                  fread.load_film_reader(), kind="solution", problem_story=PAYROLL_STORY,
                                  idea=json.loads((folder / "idea.json").read_text()))
    first = request["body"]["messages"][0]["content"][0]["text"]
    parts = ["The person (the entry's context", "## The problem this solution answers",
             "Nobody tells them when a rate changes", "what it costs them: A pay run they check twice",
             "## The founder's idea board", "the product: Runsure -- A checked pay run",
             "before that (the setup): nothing to set up", "The late mistakes: cross (not solved)",
             "## The film's lines", "chapter: What it solves", "marks: The hours (tick); The late mistakes (cross)",
             "the joy scene", "## The brand plate", "## Where Keel was told to draw it", "The frame plan",
             "## The drawing prompts"]
    at = [first.index(p) for p in parts]
    assert at == sorted(at)
    content = request["body"]["messages"][0]["content"]
    labels = [c["text"] for c in content if c["type"] == "text"][1:-1]
    assert labels[0].startswith("Frame -- the brand plate on the phone") and labels[1].startswith(
        "Frame -- the brand plate on the laptop") and labels[2].startswith("Frame -- scene 1 on the phone")
    assert request["images"] == 14 + 6 + 1 and request["dropped"] == []
    last = content[-1]["text"]
    assert fr.prompt_solution() in last and "s1, s2, s3, s4, s5, s6, s7, s8, s9" in last and "{{" not in first + last


def test_the_size_rule_drops_the_laptop_frames_first_and_says_so(tmp_path):
    walk = solution_walk(tmp_path, big=True)
    folder = walk / "film" / "fixture-film" / "solution"
    film = json.loads((folder / "film.json").read_text())
    args = (folder, film, json.loads((folder / "story.json").read_text()),
            json.loads((folder / "prompts.json").read_text()), fread.load_entry_card(film), fread.load_film_reader())
    whole = sum(fread._b64_size(i["path"]) for i in fread.images(folder, film))
    request = fread.build_request(*args, kind="solution", problem_story=PAYROLL_STORY, ceiling=whole - 1)
    assert request["dropped"] and all("laptop" in d for d in request["dropped"])
    assert request["dropped"][0].startswith("Frame -- scene 6 on the laptop")
    assert "Left out to keep this request under its size (the laptop frames first)" in \
        request["body"]["messages"][0]["content"][0]["text"]
    with pytest.raises(fread.Refused, match="every frame left out"):
        fread.build_request(*args, kind="solution", problem_story=PAYROLL_STORY, ceiling=10)


def solution_answer() -> dict:
    scores = {f"s{i}": 2 for i in range(1, 10)} | {"s4": 1, "s9": 0}
    text = json.dumps({"scores": scores, "whys": {k: f"why {k}" for k in scores}, "missing": ["The late mistakes"],
                       "instead": {"s4": "Mark the late mistakes with a cross.", "s9": "No writing on the screen."}})
    return {"model": "claude-opus-5-5", "stop_reason": "end_turn", "content": [{"type": "text", "text": text}],
            "usage": {"input_tokens": 1000, "output_tokens": 100}}


def test_the_solution_score_file_is_its_own(tmp_path):
    walk = solution_walk(tmp_path)

    class Answer:
        status_code = 200

        def json(self):
            return solution_answer()
    sent = []
    code = fread.run(["--run", str(walk), "--kind", "solution", "--no-founder", "--out", str(tmp_path / "out"),
                      "--scores-dir", str(tmp_path / "scores")],
                     post=lambda url, **k: (sent.append(k["json"]), Answer())[1],
                     env={"KEEL_ANTHROPIC_API_KEY": "test-key-not-real"})
    assert code == 0 and len(sent) == 1
    path = tmp_path / "scores" / f"{walk.name}-film-fixture-film-solution.json"
    record = fr.validate_file(json.loads(path.read_text()))
    assert record["kind"] == "solution" and record["film"]["kind"] == "solution"
    assert record["film"]["film_pct"] == round(100 * 15 / 18, 1) and record["film"]["flagged"]
    assert record["project_id"] == "s1" and record["problem_project_id"] == "p1" and record["dropped"] == []
    assert record["measures"]["lock_retried"] is False                # spec 168 FR-2: always there, true|false
    assert not (tmp_path / "scores" / f"{walk.name}-film-fixture-film.json").exists()


def test_the_founders_beats_on_the_solution_end_on_the_pilot_ask(tmp_path):
    walk = solution_walk(tmp_path)
    film = json.loads((walk / "film" / "fixture-film" / "solution" / "film.json").read_text())
    lines = fread.founder_lines(film)
    assert [x["beat"] for x in lines] == ["beat 1", "beat 2", "beat 3", "beat 4", "the verdict line", "the pilot ask"]
    assert lines[-1]["said"].startswith("Then Keel asks: Now Runsure is defined.")


# ----------------------------------------------------------------------------------------------- FR-5 / FR-6 the table

def film_file(entry_id: str, kind: str, pct_scores: dict, *, bundle: str = "w", founder: int | None = 2,
              usd: float = 0.3) -> dict:
    names = fr.KINDS[kind]
    scores = {c: pct_scores.get(c, 2) for c in names}
    film = fr.film_score(kind, scores, {c: "why" for c in names}, [],
                         {c: "instead" for c in names if scores[c] < 2})
    beats = [{"beat": "beat 1", "said": "x", "r1": founder, "r2": founder, "r3": founder, "r5": founder,
              "why1": "", "why2": "", "why3": "", "why5": "", "instead": ""}] if founder is not None else []
    return {"entry": entry_id, "kind": kind, "bundle": bundle, "cloud_sha": "c7079b59", "web_sha": "1ca065b3",
            "film_rubric_version": fr.FILM_RUBRIC_VERSION, "reader": {}, "founder_reader": None, "cost_usd": usd,
            "seconds": 1.0, "scored_at": "2026-11-25T12:00:00+00:00", "film": film,
            "founder": fr.founder_summary(beats) | {"beats": beats} if beats else None,
            "frames": {}, "walk_usd": 0.5, "_path": f"{bundle}-film-{entry_id}-{kind}.json"}


def table_of(files, solution_questions=None) -> list[dict]:
    return ft.rows(files, {}, 80.0, [], solution_questions)


def test_the_rank_on_both_films_one_film_and_a_failed_leg():
    files = [film_file("e1", "problem", {"f1": 1}), film_file("e1", "solution", {}),          # 93.8 / 100 -> 96.9
             film_file("e2", "problem", {}),                                                    # the solution failed
             film_file("e3", "problem", {"f2": 1, "f3": 1}), film_file("e3", "solution", {"s1": 1}),  # 87.5 / 94.4
             film_file("e4", "problem", {"f1": 1}), film_file("e4", "solution", {})]           # ties e1
    entries = ft.entry_rows(table_of(files))
    assert [(e["entry"], e["rank"]) for e in entries] == [("e2", 1), ("e1", 2), ("e4", 3), ("e3", 4)]
    by = {e["entry"]: e for e in entries}
    assert by["e2"]["alone"] == "problem" and by["e1"]["alone"] is None and by["e1"]["rank_pct"] == 96.9
    assert by["e3"]["rank_pct"] == round((87.5 + round(100 * 17 / 18, 1)) / 2, 1)
    # a tie on the mean is broken by the problem film, then by name
    files.append(film_file("e5", "problem", {"f1": 1}))
    files.append(film_file("e5", "solution", {}))
    order = [e["entry"] for e in ft.entry_rows(table_of(files))]
    assert order.index("e1") < order.index("e4") < order.index("e5")


def test_the_verdict_names_an_entry_under_the_bar_on_either_film():
    files = [film_file("e1", "problem", {}), film_file("e1", "solution", {"s9": 0}),
             film_file("e2", "problem", {"f4": 0}), film_file("e2", "solution", {}),
             film_file("e3", "problem", {}), film_file("e3", "solution", {})]
    v = ft.verdict(table_of(files), [])
    assert v["failed"] == ["e1", "e2"] and v["under"] == {"e1": ["solution"], "e2": ["problem"]}
    assert v["entries"] == 3 and v["passed"] == 1 and not v["round_passes"]
    assert v["mean_solution_pct"] == round((round(100 * 16 / 18, 1) + 100 + 100) / 3, 1)
    found = ft.findings(table_of(files))
    assert {(f["entry"], f["kind"], f["criterion"]) for f in found} == {("e1", "solution", "S9"),
                                                                        ("e2", "problem", "F4")}
    assert "Observation (the solution film, e1)" in ft.drift_text(found, start=1, bundle="w")
    weak = fr.weak_criteria([{**f, "film": f["film"]} for f in files])
    assert {(w["kind"], w["criterion"]) for w in weak} >= {("problem", "f4"), ("solution", "s9")}


def test_a_lock_retried_is_a_drift_finding_and_marked_in_the_entry_heading_168(tmp_path):
    # spec 168 FR-2: a record with `calibration_retried` -> `measures.lock_retried` in the score file -> the DRIFT
    # line *(capture): the lock's calibration was written again on the founder's retry* with the film's frames, and
    # *lock retried* beside *flagged* in the entry's heading; the comparison untouched
    film = {"measures": {"faults": [], "frames": 14}, "lock": {"locked": True, "calibration_retried": True}}
    assert fread.film_measures(film) == {"faults": [], "frames": 14, "lock_retried": True}
    assert fread.film_measures({"measures": {}, "strangers": {"lock": {"calibration_retried": True}}})["lock_retried"]
    assert fread.film_measures({"measures": {"faults": []}})["lock_retried"] is False
    retried = {**film_file("e1", "problem", {"f4": 0}), "measures": fread.film_measures(film),
               "frames": {"folder": "runs/w/film/e1", "frames": ["frames/phone-1.png", "frames/laptop-1.png",
                                                                 "frames/phone-2.png"]}}
    plain = {**film_file("e2", "problem", {}), "measures": fread.film_measures({"measures": {}})}
    solution = {**film_file("e1", "solution", {}), "measures": {"lock_retried": True}}
    table = table_of([retried, plain, solution])
    found = [f for f in ft.findings(table) if f["what"] == ft.LOCK_RETRIED_WHAT]
    assert [(f["entry"], f["kind"], f["criterion"]) for f in found] == [("e1", "problem", "capture"),
                                                                       ("e1", "solution", "capture")]
    assert found[0]["frames"] == ["runs/w/film/e1/frames/phone-1.png", "runs/w/film/e1/frames/laptop-1.png"]
    assert found[1]["frames"] == []                                   # no frame on the solution's where none
    assert "POST calibration/PROBLEM/retry" in found[0]["why"] and "calibration/SOLUTION/retry" in found[1]["why"]
    cfg = {"film_bar_pct": 80.0, "holdout": []}
    text = ft.render(table, [retried, plain, solution], [], cfg, bundle="w", found=ft.findings(table))
    assert "- e1 (capture): the lock's calibration was written again on the founder's retry -- " \
           "runs/w/film/e1/frames/phone-1.png, runs/w/film/e1/frames/laptop-1.png" in text
    assert "- e1 (the solution film) (capture): the lock's calibration was written again on the founder's retry -- " \
           "no frame" in text
    assert "### e1 -- the problem film, film_pct 87.5, flagged, lock retried" in text
    assert "### e1 -- the solution film, film_pct 100.0, lock retried" in text
    assert "### e2 -- the problem film, film_pct 100.0\n" in text
    drift = ft.drift_text(found, start=7, bundle="w")
    assert "## 7. Observation (the film, e1): the lock's calibration was written again on the founder's retry" in drift
    # the comparison is unchanged: no lock measure among its moves
    cmp = ft.compare(table, table_of([film_file("e1", "problem", {"f4": 0}), film_file("e2", "problem", {})]))
    assert not any("lock" in k for moves in cmp["moves"].values() for k in moves)


def test_the_comparison_tells_each_move_and_the_entries_added_and_missing():
    before = table_of([film_file("e1", "problem", {"f1": 0}), film_file("e2", "problem", {})])
    now = table_of([film_file("e1", "problem", {}), film_file("e1", "solution", {"s4": 1}),
                    film_file("e3", "problem", {})], {"e1": {"qa_pct": 90.0, "after_pct": 80.0}})
    cmp = ft.compare(now, before)
    assert cmp["both"] == ["e1"] and cmp["added"] == ["e3"] and cmp["missing"] == ["e2"]
    moves = cmp["moves"]["e1"]
    assert moves["F1"] == "0 -> 2 (+2)" and moves["problem film_pct"] == "87.5 -> 100.0 (+12.5)"
    assert moves["S4"] == "-- -> 1" and moves["solution film_pct"] == f"-- -> {round(100 * 17 / 18, 1)}"
    assert moves["§A solution"] == "-- -> 90.0" and moves["$ problem"] == "0.8 -> 0.8 (±0.0)"
    assert cmp["means"]["mean_problem_pct"] == "93.8 -> 100.0 (+6.2)"
    text = "\n".join(ft.compared_markdown(cmp, name="`20261125-b48e1f4-film.md`", bundle="b"))
    assert "## Compared with `20261125-b48e1f4-film.md`" in text and "Entries added (not in the baseline): e3." in text
    assert "Entries missing (in the baseline, not here): e2." in text and "| F1 | 0 -> 2 (+2) |" in text


def test_the_record_and_film_table_keep_the_comparison_and_never_overwrite_another_bundles_record(tmp_path):
    scores, cycles = tmp_path / "scores", tmp_path / "cycles"
    scores.mkdir()
    cycles.mkdir()
    for f in [film_file("e1", "problem", {}, bundle="now-walk"), film_file("e1", "solution", {}, bundle="now-walk"),
              film_file("e1", "problem", {"f1": 1}, bundle="old-walk")]:
        name = f"{f['bundle']}-film-e1{'-solution' if f['kind'] == 'solution' else ''}.json"
        (scores / name).write_text(json.dumps({k: v for k, v in f.items() if k != "_path"}))
    (cycles / "20261125-c7079b5-film.md").write_text("# The film, judged\n\nBundle `old-walk` · ...\n")
    code = ft.main(["--run", "now-walk", "--scores-dir", str(scores), "--table", str(tmp_path / "FILM-TABLE.md"),
                    "--cycles-dir", str(cycles), "--baseline", "old-walk"])
    assert code == 0
    text = (tmp_path / "FILM-TABLE.md").read_text()
    assert "## Compared with `20261125-c7079b5-film.md`" in text and "| F1 | 1 -> 2 (+1) |" in text
    assert (cycles / "20261125-c7079b5-film.md").read_text().startswith("# The film, judged\n\nBundle `old-walk`")
    assert (cycles / "20261125-c7079b5-film-now.md").read_text() == text
    assert "| 1 | e1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 100.0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 100.0 | 100.0 | no |" \
        in text
    assert ft.main(["--run", "now-walk", "--scores-dir", str(scores), "--table", str(tmp_path / "T.md"),
                    "--cycles-dir", str(cycles), "--baseline", "nobody"]) == 2


def test_the_solution_projects_are_read_off_the_walk(tmp_path):
    (tmp_path / "walk.json").write_text(json.dumps({"entries": [
        {"entry": "e1", "project_id": "p1", "screens": "x-film-e1",
         "solution": {"project_id": "s1", "screens_bundle": "/r/x-film-e1-solution"}},
        {"entry": "e2", "project_id": "p2", "screens": "x-film-e2", "solution": {"build": "failed"}}]}))
    assert ft.solution_projects_of(tmp_path) == {"e1": {"bundle": "x-film-e1-solution", "project_id": "s1"}}
    assert ft.projects_of(tmp_path)["e1"] == {"bundle": "x-film-e1", "project_id": "p1"}


# ----------------------------------------------------------------------------------------------- FR-7 the walk's switches

def test_the_walks_plan_with_both_halves_scopes_and_only(tmp_path):
    both = film_walk.plan_steps(["e1"], door="keel", walk=tmp_path, people=7, typos=True,
                                scopes=["PROBLEM", "SOLUTION"])
    assert [s["what"] for s in both] == ["film", "read", "read-solution"]
    assert "SCOPES=PROBLEM,SOLUTION" in both[0]["argv"] and both[2]["argv"][-1] == "RUN=<solution-bundle>"
    alone = film_walk.plan_steps(["e1"], door="keel", walk=tmp_path, people=7, typos=True, scopes=["PROBLEM"])
    assert [s["what"] for s in alone] == ["film", "read"] and "SCOPES=PROBLEM" in alone[0]["argv"]
    again = film_walk.plan_steps(["e1"], door="keel", walk=tmp_path, people=7, typos=True, only="solution")
    assert [s["what"] for s in again] == ["film", "read-solution"]
    assert {"SCOPES=SOLUTION", "ONLY=solution"} <= set(again[0]["argv"]) and again[0]["log"].endswith(
        "e1.film-solution.log")
    fake = film_walk.plan_steps(["e1"], door="fake", walk=tmp_path, people=7, typos=True, scopes=["PROBLEM", "SOLUTION"])
    assert [s["what"] for s in fake] == ["film"]
    assert film_walk.resolve_scopes(None, {"scopes": ["PROBLEM", "SOLUTION"]}) == ["PROBLEM", "SOLUTION"]
    assert film_walk.resolve_scopes("problem", {"scopes": ["PROBLEM", "SOLUTION"]}) == ["PROBLEM"]
    for bad in ("SOLUTION", "PROBLEM,MONEY"):
        with pytest.raises(film_walk.Refused):
            film_walk.resolve_scopes(bad, {"scopes": []})


def test_the_preflight_refuses_an_entry_with_no_solution_words(tmp_path):
    from quality import cycle as cyc
    known = tmp_path / cyc.BACKTEST_REL
    known.mkdir(parents=True)
    (known / "e1.yaml").write_text(yaml.safe_dump({"statements": {"problem": "p"}}))
    (known / "e2.yaml").write_text(yaml.safe_dump(entry("payroll")))
    hard, _ = film_walk.preflight(["e1", "e2"], door="fake", why="", dry=False, cloud=tmp_path, env={},
                                  scopes=["PROBLEM", "SOLUTION"])
    assert hard == ["the entry e1 has no statements.solution and no solution_mechanism -- the solution half has no "
                    "words to tell (SCOPES=PROBLEM walks the problem alone)"]
    assert film_walk.preflight(["e1"], door="fake", why="", dry=False, cloud=tmp_path, env={},
                               scopes=["PROBLEM"])[0] == []
    hard, _ = film_walk.preflight(["e2"], door="fake", why="", dry=False, cloud=tmp_path, env={}, only="solution")
    assert hard and "without RUN" in hard[0]
    walk = tmp_path / "w"
    (walk / "film" / "e2").mkdir(parents=True)
    (walk / "film" / "e2" / "film.json").write_text(json.dumps({"project_id": "p1"}))
    hard, _ = film_walk.preflight(["e2"], door="fake", why="", dry=False, cloud=tmp_path, env={}, only="solution",
                                  walk=walk)
    assert hard and "records no problem project with its founder" in hard[0]
    (walk / "film" / "e2" / "film.json").write_text(json.dumps({"project_id": "p1", "founder": {"id": "f"}}))
    assert film_walk.preflight(["e2"], door="keel", why="w", dry=False, cloud=tmp_path, only="solution", walk=walk,
                               env={"KEEL_ANTHROPIC_API_KEY": "k", "KEEL_OPENAI_API_KEY": "k",
                                    "KEEL_PICTURES": "openai"}, which=lambda b: "/bin/x",
                               stack_up=lambda: True)[0] == []      # ONLY=solution walks on the stack that stands
    assert any("KEEP=1 with more than one entry" in h for h in film_walk.preflight(
        ["e1", "e2"], door="fake", why="", dry=False, cloud=tmp_path, env={}, keep=True)[0])


def stub_two_halves(walk: Path, *, solution_built: str = "ready"):
    seen = []

    def run(argv, stdout=None, stderr=None):
        seen.append(argv)
        if "film-leg" in argv:
            e = next(a.split("=", 1)[1] for a in argv if a.startswith("ENTRY="))
            folder = walk / "film" / e
            (folder / "solution").mkdir(parents=True, exist_ok=True)
            (folder / "film.json").write_text(json.dumps({"project_id": "p1", "screens_bundle": "/r/x-film-e1",
                                                          "strangers": {"people": 7, "answered": 7},
                                                          "founder": {"id": "f1"}}))
            sol = {"kind": "solution", "entry": {"id": e}, "project_id": "s1", "problem_project_id": "p1",
                   "build_state": solution_built,
                   "screens_bundle": "/r/x-film-e1-solution" if solution_built == "ready" else None,
                   "strangers": {"people": 7, "answered": 7} if solution_built == "ready" else None}
            (folder / "solution" / "film.json").write_text(json.dumps(sol))
            return SimpleNamespace(returncode=0 if solution_built == "ready" else 1)
        bundle = argv[-1].split("=", 1)[1]
        stdout.write(f"score file: quality/scores/e1/{Path(bundle).name}.json\n")
        return SimpleNamespace(returncode=0)
    return run, seen


PAID = {"KEEL_ANTHROPIC_API_KEY": "k", "KEEL_OPENAI_API_KEY": "k", "KEEL_PICTURES": "openai"}


def test_walk_json_names_both_projects_both_bundles_and_both_score_files(tmp_path):
    walk = tmp_path / "w"
    runner, seen = stub_two_halves(walk)
    code = film_walk.walk(["--entries", "08-fresco", "--why", "w", "--door", "keel", "--out", str(walk),
                           "--scopes", "PROBLEM,SOLUTION"], runner=runner, env=PAID, which=lambda b: "/bin/x",
                          stack_up=lambda: False)
    record = json.loads((walk / "walk.json").read_text())
    row = record["entries"][0]
    assert code == 0 and record["spec"] == "163+165+166" and record["scopes"] == ["PROBLEM", "SOLUTION"]
    assert (row["project_id"], row["screens"], row["score_file"]) == ("p1", "x-film-e1", "quality/scores/e1/x-film-e1.json")
    sol = row["solution"]
    assert (sol["project_id"], sol["problem_project_id"], sol["screens"], sol["score_file"]) == (
        "s1", "p1", "x-film-e1-solution", "quality/scores/e1/x-film-e1-solution.json")
    assert sol["captured"] and seen[2][-1] == "RUN=/r/x-film-e1-solution"


def test_a_failed_solution_leg_reads_nothing_of_it_and_the_walk_fails(tmp_path):
    walk = tmp_path / "w"
    runner, seen = stub_two_halves(walk, solution_built="failed")
    code = film_walk.walk(["--entries", "08-fresco", "--why", "w", "--door", "keel", "--out", str(walk),
                           "--scopes", "PROBLEM,SOLUTION"], runner=runner, env=PAID, which=lambda b: "/bin/x",
                          stack_up=lambda: False)
    sol = json.loads((walk / "walk.json").read_text())["entries"][0]["solution"]
    assert code == 1 and sol["build"] == "failed" and sol["read"].startswith("not run") and len(seen) == 2


def test_only_solution_keeps_the_problems_record(tmp_path):
    walk = tmp_path / "w"
    runner, _ = stub_two_halves(walk)
    film_walk.walk(["--entries", "08-fresco", "--why", "w", "--door", "keel", "--out", str(walk), "--scopes",
                    "PROBLEM,SOLUTION"], runner=runner, env=PAID, which=lambda b: "/bin/x", stack_up=lambda: False)
    first = json.loads((walk / "walk.json").read_text())
    runner, seen = stub_two_halves(walk)
    code = film_walk.walk(["--entries", "08-fresco", "--why", "again", "--door", "keel", "--only", "solution",
                           "--run", str(walk)], runner=runner, env=PAID, which=lambda b: "/bin/x",
                          stack_up=lambda: True)
    again = json.loads((walk / "walk.json").read_text())
    assert code == 0 and [s[-1] for s in seen][-1] == "RUN=/r/x-film-e1-solution"
    assert "ONLY=solution" in seen[0] and again["started"] == first["started"]
    assert again["entries"][0]["project_id"] == "p1" and again["again"][0]["only"] == "solution"


def test_the_leg_reads_its_switches_and_the_cycle_walks_both():
    from evals import run_film
    assert run_film.scopes({"KEEL_FILM_SCOPES": "problem"}) == ["PROBLEM"]
    assert run_film.scopes({}) == ["PROBLEM", "SOLUTION"]                   # quality/cycle.toml [film] scopes
    assert run_film.only({"KEEL_FILM_ONLY": "Solution"}) == "solution" and run_film.only({}) is None
    assert run_film.keep({"KEEL_FILM_KEEP": "1"}) and not run_film.keep({})
    with (REPO / "quality" / "cycle.toml").open("rb") as handle:
        assert tomllib.load(handle)["film"]["scopes"] == ["PROBLEM", "SOLUTION"]


# ----------------------------------------------------------------------------------------------- FR-3 the strangers

def person(name, *, picks: dict, recency=True, in_segment=True, follow_up=None, link="PRIMARY"):
    return SimpleNamespace(person=name, link=link, recency=recency, in_segment=in_segment, follow_up=follow_up,
                           picks=[SimpleNamespace(dimension=k, codes=[v] if v else []) for k, v in picks.items()])


def test_the_solution_studys_people_answer_yes_or_no_in_their_recorded_words():
    from harness import solution_surfaces as sol
    c, r, a = sol.SOLUTION_DIMENSIONS
    plans = fs.solution_plans([
        person("Ana", picks={c: "yes", r: "a_lot_better", a: "yes_easily"}),
        person("Ben", picks={c: "no", r: "worse", a: "only_with_help"}, follow_up="It would not fit our week."),
        person("Cy", picks={c: "yes", r: None, a: "yes"}),
        person("Di", picks={}, recency=False),
        person("Ed", picks={}, in_segment=False),
        person("Fay", picks={c: "yes"}, link="B2B")])
    by = {p["person"]: p for p in plans}
    assert "Fay" not in by
    assert by["Ana"]["picks"] == {c: "yes", r: "yes", a: "yes"} and "remapped" not in by["Ana"]
    assert by["Ben"]["picks"] == {c: "no", r: "no", a: "no"} and by["Ben"]["why"] == "It would not fit our week."
    assert by["Cy"]["remapped"] == [{"dimension": r, "recorded": None, "sent": "no"}]
    assert by["Di"]["gate"] is False and by["Ed"]["screener"] == "no"
    assert fs.owed_whys(by["Ben"]) == [c, r] and fs.owed_whys(by["Di"]) == [] and fs.owed_whys(by["Ana"]) == []
    assert fs.solution_watched(plans) == "Ben"
    assert fs.solution_walk_plan(by["Ben"]) == {"who": "Ben", "screener": "yes", "gate": True,
                                                "picks": by["Ben"]["picks"], "why": "It would not fit our week."}
    # spec 169 FR-1: the check on the solution link found by the gate's new words, answered by `recency`
    from harness import three_surfaces as ts
    link = {"gate": {"question": ts.GATE_EXAMPLE}, "story": {"scenes": [{}]}, "ideaStory": {"scenes": [{}]}}
    assert [ts.gate_answer("In the last 7 days, have you encountered this issue?", link,
                           fs.solution_walk_plan(by[n])) for n in ("Ben", "Di")] == ["yes", "no"]
    assert ts.gate_answer(ts.GATE_WORDS_BEFORE_277, link, fs.solution_walk_plan(by["Ben"])) is None


def test_the_solutions_lock_reads_its_own_calibration_and_stores_no_window():
    calls = []

    def call(method, path, body):
        calls.append((method, path))
        if path.endswith("/calibration/SOLUTION"):
            return 200, {"state": "CALIBRATED", "total": 3, "answered": 3}
        if path == "/v2/me":
            return 200, {"creditsAvailable": 2000}
        if path.endswith("/overview"):
            return 200, {"questionsState": "READY"}
        return 200, {}
    lock = fs.lock_project(call, "s1", window=None, press=lambda: (201, {}), need=2000, scope=fs.SOLUTION_SCOPE,
                           sleep=lambda s: None)
    assert lock["questions"] == "READY" and lock["scope"] == "SOLUTION"
    assert not any(p.endswith("/context/window") for _, p in calls)
    assert fs.calibration_ready({"state": "READY"}) and not fs.calibration_ready({"total": 3, "answered": 3})
    with pytest.raises(fs.LockFailed, match="the SOLUTION calibration"):
        fs.lock_project(lambda m, p, b: (200, {"state": "CALIBRATING", "total": 3, "answered": 1}), "s1", window=None,
                        press=lambda: (201, {}), need=0, scope=fs.SOLUTION_SCOPE, sleep=lambda s: None,
                        calibration_wait_s=0)


def test_the_solutions_bundle_is_read_as_a_films(tmp_path):
    bundle = fs.screens_bundle(entry={"id": "e1"}, project_id="s1", door="fake", stack={}, people=7, lock={},
                               plans=[], walks=[], respondents={"PRIMARY": {"person": "Ben"}}, after_screens=[{}],
                               answers_leg=None, brief=None, themes_settled=None, founder_page=None, run="r",
                               scope=fs.SOLUTION_SCOPE, parent="p1")
    assert (bundle["kind"], bundle["scope"], bundle["spec"], bundle["problem_project_id"]) == (
        "film-solution", "SOLUTION", "166", "p1")
    (tmp_path / "backtest.json").write_text(json.dumps(bundle))
    run_dir, read = readers.load_bundle(str(tmp_path))
    assert read["kind"] == "film-solution" and readers.bundle_scope(read) == "SOLUTION"


# ----------------------------------------------------------------------------------------------- FR-10

def test_no_respondent_question_instruction_is_touched_here():
    # the founder's beats composed from an entry are the founder's words to Keel; nothing here writes or reads an
    # instruction that generates a respondent's question (keel-cloud's `respondent-questions*.md`, the spoken-form
    # guidelines)
    for module in (ff, fs, film_walk, fread, ft):
        assert "respondent-questions" not in Path(module.__file__).read_text(encoding="utf-8")
