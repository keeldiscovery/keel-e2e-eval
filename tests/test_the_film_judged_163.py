"""Spec 163: the film, judged -- the mirrors `make unit` holds, nothing paid (FR-7).

The rubric pasted from `quality/FILM-RUBRIC.md` (FR-1); the film reader's request, answer and score file against a
recorded answer and a stub door, and its refusal of the `claude` CLI door (FR-3); the founder's beats through a stub
CLI; the table on three fixture scores -- one passing, one with a 0 on F4, one weak on F8 -- with the bar, the weak
criteria, the round's verdict and the DRIFT findings (FR-4, FR-8); the holdout and the walk's refusals (FR-2, FR-5); the
adviser's rule-never-a-case refusal (FR-6); and the frames' capture -- the held clock on a page that plays like keel-web
261's picture film, fourteen frames, the pictures, the ledger -- on a local page, no stack and no model.
"""

from __future__ import annotations

import json
import shutil
import struct
import tomllib
import zlib
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import sync_playwright

from harness import film_frames as ff
from quality import film as film_walk
from quality import film_advise as fa
from quality import film_reader as fread
from quality import film_rubric as fr
from quality import film_table as ft
from quality import readers, rubric

REPO = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / "fixtures" / "film_163"
SCORES = FIX / "scores"


def png(w: int = 6, h: int = 4, rgb: tuple = (136, 136, 136)) -> bytes:
    """A valid 8-bit RGB PNG, no image library (FakePictures' shape)."""
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


LINES = ["Example workers in small teams.", "They keep the day's list.", "They write it on paper.",
         "The list gets lost on the way back.", "Two people copy the same item.", "The copy is late.",
         "They stay an hour after closing."]
CHAPTERS = {1: "who", 2: "task", 3: "today", 4: "shortfall", 7: "cost"}
ASK = "Is that how it goes for you? That is what we want to find out."


def story() -> dict:
    scenes = [{"line": line, "pictogramId": "arrives", "clipId": f"c{n}", "pictureAssetId": f"a{n}",
               **({"chapter": CHAPTERS[n]} if n in CHAPTERS else {}), **({"pain": True} if n == 7 else {})}
              for n, line in enumerate(LINES, 1)]
    return {"verdictLine": "I will call this real if at least six in ten say it happened.",
            "build": {"state": "ready", "story": {"roomId": "office", "scenes": scenes, "askLine": ASK,
                                                  "clipIds": [f"c{n}" for n in range(1, 9)], "sheetAssetId": "sheet1"},
                      "pictures": {"setting": {"place": "a small back room", "props": ["a desk", "a lamp", "a list"],
                                               "garments": ["a work apron"], "timeOfDay": "evening"},
                                   "prompts": [{"scene": None, "attempt": 1, "prompt": "Draw this one character..."},
                                               {"scene": 1, "attempt": 1, "prompt": "Style: ... the room."}]}}}


def walk_folder(root: Path, entry: str = "fixture-film") -> Path:
    """A film-walk bundle as `make film-walk` writes it: `film/<entry>/` with fourteen frames, seven pictures and the
    sheet, the story, the prompts and the capture's record."""
    walk = root / "20261124T230000Z-film-walk"
    folder = walk / "film" / entry
    (folder / "frames").mkdir(parents=True)
    (folder / "pictures").mkdir(parents=True)
    frames, pictures = [], []
    for n in range(1, 8):
        for view, size in (("phone", "390x844"), ("laptop", "1280x800")):
            rel = f"frames/scene-{n}-{view}.png"
            (folder / rel).write_bytes(png())
            frames.append({"scene": n, "viewport": view, "size": size, "path": rel})
        (folder / f"pictures/scene-{n}.png").write_bytes(png(48, 32))
        pictures.append({"scene": n, "asset": f"a{n}", "path": f"pictures/scene-{n}.png", "png": [48, 32]})
    (folder / "pictures/sheet.png").write_bytes(png(48, 32))
    pictures.append({"scene": "sheet", "asset": "sheet1", "path": "pictures/sheet.png", "png": [48, 32]})
    s = story()
    beats = [{"turn": n, "asked": f"Question {n}?", "founder": f"Words {n}.", "ask": None, "readback": f"Read {n}."}
             for n in (1, 2, 3, 4, 5, 7)]
    film = {"spec": "163", "entry": {"id": entry, "path": str(FIX / "entry.yaml"), "sha256": "0" * 64},
            "door": "fake", "project_id": "p1", "stack": {"keel-cloud": "b48e1f49", "keel-web": "69e9f2a5"},
            "frames": frames, "pictures": pictures, "beats": beats, "verdict_line": s["verdictLine"],
            "dollars": 0.0, "measures": {"faults": []}, "lines": ff.lines_of(s)}
    ff.write_folder(folder, story=s, film=film)
    return walk


# ----------------------------------------------------------------------------------------------- FR-1 the rubric

def test_the_rubric_file_says_its_version_and_holds_the_three_tables():
    assert fr.file_version() == fr.FILM_RUBRIC_VERSION == 1
    assert [r["id"] for r in fr.criteria("problem")] == list(fr.F_CRITERIA)
    assert [r["id"] for r in fr.criteria("solution")] == list(fr.S_CRITERIA)
    assert [r["id"] for r in fr.criteria("founder")] == ["r1", "r2", "r3", "r5"]
    names = {r["id"]: r["name"] for r in fr.criteria("problem")}
    assert names == {"f1": "The persona", "f2": "The task", "f3": "Today's way", "f4": "Every limitation",
                     "f5": "The pain", "f6": "Clearly spelled out", "f7": "End to end", "f8": "Legible"}
    f8 = next(r for r in fr.criteria("problem") if r["id"] == "f8")
    assert "text inside a picture" in f8["0"] and "phone" in f8["question"] and "laptop" in f8["question"]


def test_the_weak_rule_is_the_question_rubrics():
    assert fr.FILM_WEAK == {"zero_entries": rubric.WEAK_ZERO_ENTRIES, "mean_under": rubric.WEAK_MEAN}


def test_the_rubric_is_pasted_whole_into_the_reader_prompt():
    filled = readers.fill(fread.template(fread.PROMPT_PATH, "after-images"),
                          {"rubric": fr.prompt_problem(), "criteria": ", ".join(fr.F_CRITERIA)})
    assert fr.prompt_problem() in filled
    assert "{{" not in filled
    assert "<!-- film-problem" not in fr.prompt_problem()
    solution = fr.prompt_of("solution")
    assert "S9" in solution and "F1" not in solution


def test_a_film_answer_is_read_and_its_number_is_codes():
    raw = json.loads((FIX / "api-answer.json").read_text())["content"][1]["text"]
    score = fr.parse_film_answer(raw)
    assert score["scores"]["f4"] == 1 and score["film_pct"] == 87.5 and score["flagged"] is False
    assert set(score["instead"]) == {"f4", "f8"} and score["missing"] == ["two people copy the same item"]
    body = json.loads(raw)
    body["film_pct"] = 12.0                                         # the reader's own number is never read
    assert fr.parse_film_answer(json.dumps(body))["film_pct"] == 87.5


@pytest.mark.parametrize("change, said", [
    (lambda b: b["whys"].pop("f3"), "no why"),
    (lambda b: b["instead"].pop("f4"), "no instead line"),
    (lambda b: b["scores"].update({"s1": 2}), "on a problem film"),
    (lambda b: b["scores"].update({"f2": None}), "f2 must be 0, 1 or 2"),
    (lambda b: b.update({"missing": "a string"}), "must be a list"),
])
def test_an_answer_out_of_shape_is_refused(change, said):
    body = json.loads(json.loads((FIX / "api-answer.json").read_text())["content"][1]["text"])
    change(body)
    with pytest.raises(fr.FilmRubricError, match=said):
        fr.parse_film_answer(json.dumps(body))


def test_a_founder_beat_is_scored_on_four_criteria_alone():
    row = fr.parse_founder_beat('{"r1": 2, "why1": "a", "r2": 1, "why2": "b", "r3": 2, "why3": "c", "r5": 0, '
                                '"why5": "d", "instead": "e"}', beat="beat 1", said="Keel asks: who?")
    assert tuple(row) == fr.FOUNDER_BEAT_KEYS
    assert fr.founder_summary([row])["founder_pct"] == 62.5
    with pytest.raises(fr.FilmRubricError, match="R1, R2, R3 and R5 alone"):
        fr.parse_founder_beat('{"r1": 2, "r2": 2, "r3": 2, "r5": 2, "r6": 2}', beat="b", said="s")


# ----------------------------------------------------------------------------------------------- FR-3 the reader

def test_the_reader_is_pinned_to_the_api_with_vision():
    with (REPO / "quality" / "readers.toml").open("rb") as handle:
        pinned = tomllib.load(handle)["film_reader"]
    assert (pinned["model"], pinned["effort"], pinned["door"]) == ("claude-opus-5-5", "medium", "anthropic api")
    assert fread.load_film_reader()["door"] == fread.API_DOOR


@pytest.mark.parametrize("door", ["claude CLI", "claude", "host"])
def test_the_cli_door_is_refused_for_the_film_reader(door, tmp_path):
    with pytest.raises(fread.Refused, match="cannot carry"):
        fread.refuse_cli(door)
    toml = tmp_path / "readers.toml"
    toml.write_text(f'[film_reader]\nmodel = "claude-opus-5-5"\neffort = "medium"\nvendor = "anthropic"\ndoor = "{door}"\n')
    with pytest.raises(fread.Refused, match="Anthropic API with vision"):
        fread.load_film_reader(toml)


def test_a_paid_read_refuses_without_the_key(tmp_path, capsys):
    walk = walk_folder(tmp_path)
    code = fread.run(["--run", str(walk), "--out", str(tmp_path / "out"), "--scores-dir", str(tmp_path / "scores")],
                     env={})
    assert code == 2 and "KEEL_ANTHROPIC_API_KEY is not set" in capsys.readouterr().err
    assert not (tmp_path / "scores").exists()


class Answer:
    def __init__(self, body, status=200):
        self.body, self.status_code = body, status

    def json(self):
        return self.body


def cli_stub(answers: list[str]):
    """The `claude` CLI as `readers.Reader` reads it: the last stdout line, one JSON object a call."""
    said = iter(answers)

    class Done:
        def __init__(self, result):
            self.stdout = json.dumps({"result": result, "total_cost_usd": 0.0}) + "\n"
            self.stderr = ""

    def run(argv, **kw):
        return Done(next(said))
    return run


def test_one_film_is_one_call_and_its_score_file_is_written(tmp_path, monkeypatch):
    walk = walk_folder(tmp_path)
    sent = []

    def post(url, json=None, timeout=None, headers=None):
        sent.append({"url": url, "body": json, "headers": headers})
        return Answer(__import__("json").loads((FIX / "api-answer.json").read_text()))

    beat = '{"r1": 2, "why1": "a", "r2": 2, "why2": "b", "r3": 2, "why3": "c", "r5": 1, "why5": "d", "instead": "e"}'
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    code = fread.run(["--run", str(walk), "--out", str(tmp_path / "out"), "--scores-dir", str(tmp_path / "scores")],
                     post=post, cli_runner=cli_stub(["ready"] + [beat] * 7),
                     env={"KEEL_ANTHROPIC_API_KEY": "test-key-not-real"})
    assert code == 0 and len(sent) == 1
    request = sent[0]
    assert request["url"] == fread.API_URL
    assert request["headers"]["x-api-key"] == "test-key-not-real"
    assert request["headers"]["anthropic-beta"] == fread.FALLBACK_BETA
    body = request["body"]
    assert body["model"] == "claude-opus-5-5" and body["output_config"] == {"effort": "medium"}
    assert body["thinking"] == {"type": "adaptive"} and body["fallbacks"] == "default"
    content = body["messages"][0]["content"]
    images = [c for c in content if c["type"] == "image"]
    assert len(images) == 14 + 7 + 1                                   # the frames, the pictures, the sheet
    assert all(c["source"]["media_type"] == "image/png" for c in images)
    labels = [c["text"] for c in content if c["type"] == "text"]
    assert labels[1].startswith("Frame -- scene 1 on the phone") and labels[2].startswith("Frame -- scene 1 on the laptop")
    first = content[0]["text"]
    assert "example workers in small teams" in first and "the list gets lost on the way back" in first
    assert "chapter: Where it falls short" in first and ASK in first and "a small back room" in first
    assert fr.prompt_problem() in content[-1]["text"]
    path = fread.score_path(tmp_path / "scores", walk.name, "fixture-film")
    record = fr.validate_file(json.loads(path.read_text()))
    assert set(fr.FILE_KEYS) <= set(record)
    assert record["film_rubric_version"] == 1 and record["film"]["film_pct"] == 87.5
    assert record["reader"]["door"] == "anthropic api" and record["reader"]["served_by"] == "claude-opus-5-5"
    assert record["film_cost_usd"] == round((31000 * 4 + 2500 * 20) / 1e6, 4)
    assert record["founder"]["beats"][0]["beat"] == "beat 1" and len(record["founder"]["beats"]) == 7
    assert record["founder"]["beats"][-1]["beat"] == "the verdict line"
    assert record["founder"]["founder_pct"] == 87.5
    assert "test-key-not-real" not in path.read_text()
    calls = list((tmp_path / "out" / "calls").glob("*.prompt.txt"))
    assert calls and all("test-key-not-real" not in c.read_text() for c in calls)
    assert "[image: frames/scene-1-phone.png" in (tmp_path / "out" / "calls" / "001-film-fixture-film.prompt.txt").read_text()


def test_a_dry_read_writes_the_prompts_and_calls_nothing(tmp_path):
    walk = walk_folder(tmp_path)

    def post(*a, **k):
        raise AssertionError("a dry run calls nothing")
    code = fread.run(["--run", str(walk), "--dry-run", "--out", str(tmp_path / "out"),
                      "--scores-dir", str(tmp_path / "scores")], post=post, env={})
    assert code == 0 and (tmp_path / "out" / "film-fixture-film.prompt.txt").is_file()
    assert len(list((tmp_path / "out").glob("film-fixture-film-founder-*.prompt.txt"))) == 7
    assert not (tmp_path / "scores").exists()


# ----------------------------------------------------------------------------------------------- FR-4 the table

def test_the_table_on_three_fixture_scores(tmp_path):
    drift = tmp_path / "DRIFT.md"
    drift.write_text("# DRIFT\n\n## 115. Observation (an earlier one)\n\ntext\n")
    code = ft.main(["--run", "fixture-walk", "--scores-dir", str(SCORES), "--table", str(tmp_path / "FILM-TABLE.md"),
                    "--cycles-dir", str(tmp_path / "cycles"), "--drift", "--drift-path", str(drift)])
    assert code == 0
    files = ft.load_films("fixture-walk", SCORES)
    table = ft.rows(files, {}, 80.0, [])
    by = {r["entry"]: r for r in table}
    assert by["entry-a"]["passes"] and by["entry-a"]["film_pct"] == 100.0
    assert not by["entry-b"]["passes"] and by["entry-b"]["flagged"]             # a 0 on F4 fails at 81.2
    assert by["entry-c"]["passes"] and by["entry-c"]["film_pct"] == 87.5        # weak on F8, over the bar, no 0
    assert ft.verdict(table, [])["round_passes"] is False
    weak = {w["criterion"] for w in fr.weak_criteria(files)}
    assert weak == {"f4", "f8"}
    text = (tmp_path / "FILM-TABLE.md").read_text()
    # spec 166 FR-5: both films an entry, ranked -- a problem film alone is marked, its S columns `--`
    assert "| 3 | entry-b (problem film alone) | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 1 | 81.2 | " + " | ".join(["--"] * 10) \
        + " | 81.2 | problem |" in text
    assert "**F4** (problem)" in text and "**F8** (problem)" in text and "the round **fails**" in text
    # the integrator wrote the founder's nine into [film] holdout (2026-11-25): none of them is in the fixture bundle
    assert "No holdout entry is in this bundle: this is not the round of record." in text
    assert "- F4 0: Two limitations share one scene" in text and "fixture-walk/film/entry-b/frames/scene-1-phone.png" in text
    assert (tmp_path / "cycles" / "20261124-b48e1f4-film.md").read_text() == text
    appended = drift.read_text()
    assert "## 116. Observation (the film, entry-b): a limitation of the problem statement with no scene of its own" \
        in appended and "Found by spec `163-the-film-judged`" in appended and "Not shown: the list gets lost." in appended


def test_a_holdout_entry_short_fails_the_round_by_name():
    table = ft.rows(ft.load_films("fixture-walk", SCORES), {}, 80.0, ["entry-b"])
    v = ft.verdict(table, ["entry-b"])
    assert v["holdout_failed"] == ["entry-b"] and v["round_passes"] is False


def test_the_question_and_page_scores_sit_beside_the_film(tmp_path):
    scores = tmp_path / "scores"
    shutil.copytree(SCORES, scores)
    (scores / "entry-a").mkdir()
    # spec 165 FR-3: §A is the strangers' screens of the film's link (a founder screen is never in it)
    screens = [{"kind": "gate", "audience": "respondent", "r1": 2, "r2": 2, "r3": 2, "r4": 2, "r5": 2,
                "r6": 2, "r7": None},
               {"kind": "q-problem.prevalence", "audience": "founder", "r1": 0, "r2": 0, "r3": 0, "r4": 0, "r5": 0,
                "r6": None, "r7": None},
               {"kind": "stage", "audience": "founder", "b1": 2, "b2": 1, "b3": 2, "b4": 2, "b5": 2, "b6": None}]
    (scores / "entry-a" / "x.json").write_text(json.dumps({"entry": "entry-a", "bundle": "bt-entry-a",
                                                           "screens": screens, "summary": {"overall": {"after_pct": 90.0}}}))
    got = ft.question_scores("fixture-walk", scores, {"entry-a": "bt-entry-a"})
    assert got["entry-a"]["qa_pct"] == 100.0 and got["entry-a"]["after_pct"] == 90.0


def test_two_film_rubric_versions_are_never_tabled_together(tmp_path):
    shutil.copytree(SCORES, tmp_path / "s")
    path = tmp_path / "s" / "fixture-walk-film-entry-c.json"
    obj = json.loads(path.read_text())
    obj["film_rubric_version"] = 2
    path.write_text(json.dumps(obj))
    with pytest.raises(ft.Refused, match="never"):
        ft.load_films("fixture-walk", tmp_path / "s")


def test_the_bar_and_the_holdout_live_in_cycle_toml():
    cfg = ft.load_film_config()
    # the integrator wrote the founder's nine (2026-11-25, the trial on two); spec 166 walks both halves
    assert cfg["film_bar_pct"] == 80.0 and len(cfg["holdout"]) == 9 and all(isinstance(e, str) for e in cfg["holdout"])
    assert cfg["scopes"] == ["PROBLEM", "SOLUTION"]
    with (REPO / "quality" / "cycle.toml").open("rb") as handle:
        assert tomllib.load(handle)["gallery"]["entry_mean_pct"] == cfg["film_bar_pct"]


# ----------------------------------------------------------------------------------------------- FR-2 / FR-5 the walk

def test_the_holdout_walk_is_refused_while_the_list_is_empty():
    with pytest.raises(film_walk.Refused, match="holdout is empty"):
        film_walk.resolve_entries("holdout", {"entries": []}, {"holdout": []})
    assert film_walk.resolve_entries("holdout", {"entries": []}, {"holdout": ["x", "y"]}) == ["x", "y"]


def test_the_paid_walk_refuses_without_its_keys_and_the_free_one_never_draws_a_paid_picture(tmp_path):
    hard, _ = film_walk.preflight(["e"], door="keel", why="w", dry=False, cloud=tmp_path, env={},
                                  which=lambda b: "/bin/x", stack_up=lambda: False)
    assert any("KEEL_ANTHROPIC_API_KEY, KEEL_OPENAI_API_KEY not set" in h for h in hard)
    assert any("KEEL_PICTURES is not `openai`" in h for h in hard)
    hard, _ = film_walk.preflight(["e"], door="keel", why="w", dry=False, cloud=tmp_path,
                                  env={"KEEL_ANTHROPIC_API_KEY": "k", "KEEL_OPENAI_API_KEY": "k", "KEEL_PICTURES": "openai"},
                                  which=lambda b: "/bin/x", stack_up=lambda: True)
    assert hard == ["a stack already answers on the eval ports -- `make down` first: each step brings its own stack "
                    "booted from this shell"]
    hard, _ = film_walk.preflight(["e"], door="fake", why="", dry=False, cloud=tmp_path, env={"KEEL_PICTURES": "openai"},
                                  which=lambda b: None)
    assert hard and "never draws a paid picture" in hard[0]


def test_the_paid_walk_is_the_film_leg_then_the_readers(tmp_path):
    # spec 165 (163's judgement call 1 closed): no back-test step -- the film leg walks the people on its own project
    steps = film_walk.plan_steps(["e1"], door="keel", walk=tmp_path, people=7, typos=True)
    assert [s["what"] for s in steps] == ["film", "read"]
    assert steps[0]["argv"][-5:-2] == ["ENTRY=e1", "DOOR=keel", f"OUT={tmp_path}"]
    assert [s["what"] for s in film_walk.plan_steps(["e1"], door="fake", walk=tmp_path, people=7, typos=True)] == ["film"]


def test_the_film_leg_refuses_as_the_walk_does():
    from evals import run_film
    assert run_film.refusal({"KEEL_FILM_ENTRY": "e", "KEEL_FILM_OUT": "o", "KEEL_FILM_DOOR": "keel"}).startswith(
        "make film-leg refuses: KEEL_ANTHROPIC_API_KEY, KEEL_OPENAI_API_KEY not set")
    assert run_film.refusal({"KEEL_FILM_ENTRY": "e", "KEEL_FILM_OUT": "o", "KEEL_FILM_DOOR": "fake"}) is None
    assert "never draws a paid picture" in run_film.refusal({"KEEL_FILM_ENTRY": "e", "KEEL_FILM_OUT": "o",
                                                             "KEEL_FILM_DOOR": "fake", "KEEL_PICTURES": "openai"})


def test_nothing_paid_runs_from_make_unit():
    assert not (REPO / "evals" / "run_film.py").name.startswith("test_")
    makefile = (REPO / "Makefile").read_text()
    unit = makefile.split("\nunit: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "film" not in unit and "tests" in unit
    assert "film-walk" not in makefile.split("\neval: venv\n", 1)[1].split("\n\n", 1)[0]


def test_the_entrys_beats_are_one_rule_in_its_own_words():
    entry = yaml.safe_load((FIX / "entry.yaml").read_text())
    beats = ff.entry_beats(entry)
    assert [n for n, _ in beats] == [1, 2, 3, 4, 5, 6, 7]
    said = dict(beats)
    assert said[1].startswith("Example workers in small teams")
    assert "the list gets lost on the way back" in said[3] and said[3].startswith("Today: They write it on paper")
    assert said[7] == "Their other tasks: Ordering the stock; Answering the phone."
    card = fread.persona_card(entry)
    assert "actor_plural: example workers in small teams" in card and "Example payers" not in card
    assert "today's way: They write it on paper and copy it in later." in card


# ----------------------------------------------------------------------------------------------- the capture

PLAYER = """<!doctype html><html><head><style>
body{margin:0;font:16px/24px sans-serif} .sty-stage{position:relative;width:100%;max-width:640px;aspect-ratio:3/2;
background:#888;overflow:hidden} .sty-stage img{position:absolute;inset:0;width:100%;height:100%;opacity:0}
.sty-stage img[data-on]{opacity:1} .sty-pcap{position:absolute;left:8px;right:8px;bottom:8px;margin:0;color:#fff}
</style></head><body><main><div class="vstage" data-voice="begin"><button data-testid="story-orb">o</button></div>
<div class="sty-player" data-mode="pictures" data-testid="story-player"><div class="sty-stage" data-testid="story-stage" data-step="-1">
__IMGS__<span class="sty-chapter" data-testid="story-chapter"></span>
<p class="sty-pcap" data-testid="story-line"></p></div></div></main>
<script>
const S = __STORY__;
const words = {who:'Who', task:'The task', today:'Today', shortfall:'Where it falls short', cost:'What it costs them'};
document.querySelector('[data-testid=story-orb]').addEventListener('click', async () => {
  document.querySelector('.vstage').setAttribute('data-voice', 'on');
  const stage = document.querySelector('[data-testid=story-stage]');
  let mark = null;
  for (let i = 0; i < 8; i++) {
    await fetch('/v2/clips/' + S.clipIds[i]);             // a scene stands until the next line's clip sounds
    const scene = S.scenes[i];
    stage.setAttribute('data-step', String(i));
    if (scene && scene.chapter) mark = scene.chapter;
    document.querySelector('[data-testid=story-chapter]').textContent = scene ? words[mark] : '';
    document.querySelector('[data-testid=story-line]').innerHTML = '<span class="sty-pcap__words">' + (scene ? scene.line : S.askLine) + '</span>';
    document.querySelectorAll('img[data-asset]').forEach((im, k) => k === i ? im.setAttribute('data-on', '') : im.removeAttribute('data-on'));
    await new Promise((r) => setTimeout(r, 150));
  }
});
</script></body></html>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_frames_are_captured_each_scene_held(browser, tmp_path):
    s = story()
    drawn = s["build"]["story"]
    imgs = "".join(f'<img data-testid="story-picture" data-asset="{x["pictureAssetId"]}" '
                   f'src="/v2/assets/{x["pictureAssetId"]}">' for x in drawn["scenes"])
    page = PLAYER.replace("__IMGS__", imgs).replace("__STORY__", json.dumps(drawn))
    asked = []

    def serve_page(route):
        route.fulfill(status=200, content_type="text/html", body=page)

    def serve_asset(route):
        route.fulfill(status=200, content_type="image/png", body=png(48, 32))

    def serve_clip(route):
        asked.append(route.request.url.rsplit("/", 1)[-1])
        route.fulfill(status=200, content_type="audio/mpeg", body=b"")

    camera = ff.FilmCamera(browser, {"cookies": [], "origins": []}, "http://film.test", tmp_path, inits=("",),
                           routes=(("http://film.test/p/**", serve_page), ("**/v2/assets/**", serve_asset),
                                   ("**/v2/clips/**", serve_clip)))
    frames, faults = camera.shoot("p1", s)
    assert faults == []
    assert len(frames) == 14 and [f["scene"] for f in frames] == [n for n in range(1, 8) for _ in range(2)]
    assert all((tmp_path / f["path"]).is_file() for f in frames)
    by = {(f["scene"], f["viewport"]): f for f in frames}
    assert by[(4, "phone")]["caption"] == LINES[3] and by[(4, "phone")]["chapter"] == "Where it falls short"
    assert by[(5, "laptop")]["chapter"] == "Where it falls short" and by[(5, "laptop")]["shown"] == "a5"
    assert by[(7, "phone")]["size"] == "390x844" and by[(7, "laptop")]["size"] == "1280x800"
    assert all(f["inside"] for f in frames) and all(f["step"] == str(f["scene"] - 1) for f in frames)
    assert asked.count("c1") == 2 and asked.count("c8") == 2           # every clip let go, on both viewports


def test_the_pictures_the_ledger_and_the_folder(tmp_path):
    s = story()

    def get_bytes(path):
        return (200, png(48, 32), "image/png") if path.endswith(("a3", "sheet1")) or path[-2] == "a" else (404, b"", None)
    pictures = ff.fetch_pictures(get_bytes, s, tmp_path)
    assert [p["scene"] for p in pictures] == [1, 2, 3, 4, 5, 6, 7, "sheet"]
    assert pictures[0]["png"] == [48, 32] and (tmp_path / "pictures" / "scene-1.png").is_file()
    assert ff.picture_faults(pictures) == []
    rows = [{"project_id": "p1", "kind": "SPEND", "action": "STORY_PICTURES", "credits": 0,
             "actual_cost_micro_usd": 400_000},
            *[{"project_id": "p1", "kind": "SPEND", "action": "PICTURE_REVIEW", "credits": 0,
               "actual_cost_micro_usd": 6_000}] * 7,
            {"project_id": "p1", "kind": "SPEND", "action": "STORY_CHECK", "credits": 0, "actual_cost_micro_usd": 9},
            {"project_id": "p2", "kind": "SPEND", "action": "STORY_PICTURES", "credits": 0, "actual_cost_micro_usd": 1}]
    spent = ff.ledger_rows(rows, "p1")
    assert (spent["story_pictures"], spent["picture_review"], spent["credits"], spent["usd"]) == (1, 7, 0, 0.442)
    assert ff.chapter_faults(s) == []
    s["build"]["story"]["scenes"][4]["pictureAssetId"] = None
    s["build"]["story"]["scenes"][3].pop("chapter")
    said = [f["what"] for f in ff.chapter_faults(s)]
    assert any("scene 4's chapter mark is None" in w for w in said) and any("scene 5 is served with no picture" in w
                                                                             for w in said)
    assert ff.png_size(b"not a png") is None


# ----------------------------------------------------------------------------------------------- FR-6 the adviser

def test_the_adviser_proposes_a_rule_never_a_case():
    files = ft.load_films("fixture-walk", SCORES)
    assert fa.names_a_case({"change": "Draw entry-b's room bigger.", "why": ""}, files).startswith("it names an entry")
    assert "condition on who the people are" in fa.names_a_case(
        {"change": "If the person is a cook, draw a kitchen.", "why": ""}, files)
    assert fa.names_a_case({"change": "Draw every limitation as its own scene, one a line.", "why": "plain"}, files) is None
    weak = next(w for w in fr.weak_criteria(files) if w["criterion"] == "f4")
    block = fa.anonymise(fa.failing_block(weak, files), files)
    assert "entry-b" not in block and "film 2: 0" in block
    with pytest.raises(rubric.RubricError, match="where"):
        fa.parse_proposal('{"where": "somewhere", "change": "x", "rung": "words"}')
