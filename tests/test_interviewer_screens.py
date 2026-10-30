"""Spec 044 T003: the AI interviewer's page objects (`harness/interviewer_screens.py`) against keel-web's own source --
the speech seam the eval drives exists only in a test-mode build (judgement call 1's "one check"), the eval's init
script is keel-web's fixture restated, and the words the page objects read are keel-web's own."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from stack.config import REPO_ROOT, load_config


def _web(rel: str) -> str:
    path = load_config(validate=False).keel_web / rel
    if not path.is_file():
        pytest.skip(f"keel-web has no {rel} (before spec 069)")
    return path.read_text(encoding="utf-8")


def test_the_speech_seam_is_read_only_in_a_test_build():
    """Every read of `window.__keelSpeech` in keel-web's app code sits under `import.meta.env.MODE === "test"`, which a
    production build folds to false and deletes with the seam (keel-web 069 judgement call 5)."""
    root = load_config(validate=False).keel_web / "src"
    if not (root / "components/interview/ai/useSpeechRecognition.ts").is_file():
        pytest.skip("keel-web predates spec 069")
    reads = []
    for path in root.rglob("*.ts*"):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"window\.__keelSpeech", text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line = text[line_start:text.find("\n", m.end())]
            # a comment names the seam (072's `/** ... window.__keelSpeech.classify ...`), never reads it
            if line.lstrip().startswith(("*", "/*", "//", "__keelSpeech?:")):
                continue
            reads.append((path.name, text[max(0, m.start() - 400):m.start()]))
    assert reads, "keel-web reads the seam nowhere"
    for name, before in reads:
        assert 'import.meta.env.MODE === "test"' in before, name


def test_the_eval_serves_keel_web_in_test_mode():
    config = (REPO_ROOT / "stack" / "vite.eval.config.ts").read_text(encoding="utf-8")
    assert 'mode: process.env.EVAL_WEB_MODE ?? "test"' in config


def _fixture_115() -> str:
    fixture = _web("tests/fixtures/interviewer/fakeSpeech.ts")
    if "PADDED_BYTES" not in fixture:
        pytest.skip("keel-web's fixture predates spec 115 (one recorded path)")
    return fixture


def test_the_init_script_is_keel_webs_fixture_restated():
    """Spec 074 FR-1 (keel-web 115 FR-5): the fake recorder and the always-granted microphone, restated -- the names a
    walk drives are the fixture's; the recogniser's fake and its controls are gone from both."""
    fixture = _fixture_115()
    for name in ("__keelSpeech", "__say", "__listening", "__level", "__holdStop", "__releaseStop", "__recordStarts",
                 "__recordStops", "__recordCancels", "__micReleased", "__micAcquired", "recorder", "mic"):
        assert name in fixture and name in ivs.SPEECH_SEAM, name
    for name in ("__speechError", "__speechEnd", "__recognisers", "Recognition", "__speechStarts"):
        assert name not in fixture and name not in ivs.SPEECH_SEAM, name


def _const(source: str, name: str) -> str:
    m = re.search(rf"const {name} = ([^;]+);", source)
    assert m, name
    return m.group(1).strip()


def test_say_is_keel_webs_fixture_restated():
    """Spec 074 FR-1: `__say(text, final = true)` as keel-web 115 FR-5 wrote it -- a final is said (joined to the
    window's finals), the level pulses `SAY_TICKS` ticks at `SOUND`, a non-final keeps the words provisional; `stop()`
    hands back the said words, finals then the words still being said, padded with zeros to `PADDED_BYTES`, as
    `audio/webm`; `cancel()` and `stop()` forget them; `__listening()` is the recorder running."""
    fixture = _fixture_115()
    for name in ("SAY_TICKS", "SOUND", "PADDED_BYTES"):
        assert _const(fixture, name) == _const(ivs.SPEECH_SEAM, name), name
    assert _const(fixture, "PADDED_BYTES") == "20 * 1024"
    squash = lambda t: re.sub(r"\s+", "", t.replace("'", '"'))  # noqa: E731 - the seam is JS in single quotes
    fx, ours = squash(fixture), squash(ivs.SPEECH_SEAM)
    for piece in ('if(final){said.push(text);speaking="";pulse=SAY_TICKS;}elsespeaking=text;',
                  'consttext=[...said,speaking].filter(Boolean).join("");',
                  'mimeType:"audio/webm"',
                  'newUint8Array(Math.max(PADDED_BYTES,words.length));',
                  'if(pulse>0){pulse-=1;level=SOUND;}elseif(speaking)level=SOUND;',
                  '=()=>recording;'):
        assert piece in fx, piece
        assert piece in ours, piece
    # keel-web's own `decodeSaid` and keel-cloud 136's fake transcriber trim the zero padding; so does the harness's
    assert "while (end > 0 && bytes[end - 1] === 0) end -= 1;" in fixture
    assert ivs.decode_said(__import__("base64").b64encode("about four".encode() + bytes(20 * 1024 - 10)).decode()) \
        == "about four"


def test_the_seam_records_what_was_said_in_a_real_page():
    """Spec 074 FR-1, run: the seam in a page -- a recording started, `__say` twice and a provisional word, the level
    loud for three ticks a final then quiet, `stop()` 20 KiB of `audio/webm` whose words are the finals joined and then
    the provisional one (decoded as keel-cloud 136's fake does), the next window empty (zeros alone), `__listening()`
    true only while it runs; the microphone granted and counted."""
    from playwright.sync_api import sync_playwright                         # noqa: PLC0415

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.add_init_script(ivs.SPEECH_SEAM)
            page.goto("about:blank")
            page.set_content("<p>seam</p>")
            got = page.evaluate("""async () => {
                const s = window.__keelSpeech;
                const levels = [];
                const granted = await s.mic.acquire();
                const before = window.__listening();
                await s.recorder.start((l) => levels.push(l));
                const during = window.__listening();
                window.__say('about four', true);
                window.__say('maybe five', true);
                window.__say('or six', false);
                await new Promise((r) => setTimeout(r, 450));
                const first = await s.recorder.stop();
                const after = window.__listening();
                await s.recorder.start(() => {});
                const second = await s.recorder.stop();
                s.mic.release();
                return { granted, before, during, after, levels, first, second,
                         starts: window.__recordStarts.length, stops: window.__recordStops.length,
                         released: window.__micReleased, acquired: window.__micAcquired,
                         sound: typeof window.__soundAt === 'number' };
            }""")
        finally:
            browser.close()
    import base64                                                             # noqa: PLC0415

    first = base64.b64decode(got["first"]["audio"])
    assert got["first"]["mimeType"] == "audio/webm" and len(first) == 20 * 1024
    assert ivs.decode_said(got["first"]["audio"]) == "about four maybe five or six"
    assert ivs.decode_said(got["second"]["audio"]) == "" and len(base64.b64decode(got["second"]["audio"])) == 20 * 1024
    assert got["granted"] is True and got["acquired"] == 1 and got["released"] == 1
    assert (got["before"], got["during"], got["after"]) == (False, True, False)
    assert got["levels"][:3] == [0.3, 0.3, 0.3] and got["sound"]
    assert (got["starts"], got["stops"]) == (2, 2)


@pytest.mark.parametrize("word", [ivs.PERSONA_RECORDING, ivs.PERSONA_NOT_RECORDED, ivs.TRY_IT_YOURSELF_RECORDING,
                                  ivs.TRY_NOTHING_STORED, ivs.SEND_TEXT_ONLY_LINKS, ivs.SEND_FORMAT_RECORDED,
                                  ivs.SEND_FORMAT_RECORDING, ivs.FORMAT_CREDITS_NOTE, ivs.RECORD_FACE_TITLE, ivs.CHANGE_FACE_TITLE,
                                  iv.TEXT_ONLY, iv.FORMAT_RECORDING, iv.FORMAT_NOT_RECORDED, iv.FORMAT_NEEDS_CREDITS])
def test_the_words_are_keel_webs_own(word):
    assert f'"{word}"' in _web("src/lib/translate.ts"), word


def test_the_templates_are_keel_webs_own():
    translate = _web("src/lib/translate.ts")
    assert "`${face} asks your questions.`" in translate and ivs.persona_asks("Daphne") == "Daphne asks your questions."
    assert "`Change who asks · ${creditsAmount(credits)} AI credits`" in translate
    assert ivs.change_who_asks(400) == "Change who asks · 400 AI credits"
    assert "`Record the interviewer · ${creditsAmount(credits)} AI credits`" in translate
    # keel-web 109 (keel-cloud 133 FR-9): *1 question* for one
    assert "`${face} asks your questions`" in translate
    assert '`${face} will ask you ${questions} question${questions === 1 ? "" : "s"}.`' in translate
    assert ivs.ai_intro_heading("Daphne", 1) == "Daphne will ask you 1 question."
    assert ivs.ai_intro_heading("Daphne", 9) == "Daphne will ask you 9 questions."


@pytest.mark.parametrize("testid", ["persona-line", "change-who-asks", "change-face-popup", "change-face-confirm",
                                    "try-it-yourself", "ai-intro", "start-talking", "choice-talk", "choice-write",
                                    "ai-stage", "ai-where", "ai-end", "ship-mark", "ai-sheet", "ai-options",
                                    "ai-field", "ai-preview", "ai-heard", "ai-type",
                                    "ai-typed", "ai-done", "face-carousel", "lock-and-record"])
def test_every_selector_the_page_objects_press_is_in_keel_web(testid):
    root = load_config(validate=False).keel_web / "src"
    if not (root / "components/interview/ai").is_dir():
        pytest.skip("keel-web predates spec 069")
    hits = [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert testid in Path(ivs.__file__).read_text(encoding="utf-8") + Path(
        REPO_ROOT / "harness" / "vectors_screens.py").read_text(encoding="utf-8"), testid


# ------------------------------------------------------------------ spec 048: keel-web 072's answer path

def _web_072() -> Path:
    root = load_config(validate=False).keel_web
    translate = root / "src/lib/translate.ts"
    if not translate.is_file() or "AI_MIC_TEST" not in translate.read_text(encoding="utf-8"):
        pytest.skip("keel-web predates spec 072 (no Test your mic)")
    return root


@pytest.mark.parametrize("testid", ["ai-yes", "ai-back", "ai-mic-test", "ai-mic-heard", "ai-status"])
def test_the_answer_paths_selectors_are_in_keel_web(testid):
    root = _web_072() / "src"
    hits = [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert testid in Path(ivs.__file__).read_text(encoding="utf-8"), testid


def test_thats_my_answer_is_gone_from_keel_web():
    """072 FR-5: `ai-answer` is removed from the sheet; the journey asserts it is never drawn."""
    root = _web_072() / "src"
    assert not [p.name for p in root.rglob("*.tsx") if 'data-testid="ai-answer"' in p.read_text(encoding="utf-8")]
    assert ivs.THATS_MY_ANSWER not in [m for m in re.findall(r'"([^"]+)"', (root / "lib/translate.ts").read_text(
        encoding="utf-8"))]


@pytest.mark.parametrize("word", [ivs.START_THE_INTERVIEW, ivs.MIC_TEST, ivs.SAY_HELLO, ivs.MIC_FALLBACK,
                                  ivs.INTRO_TRANSCRIBED, ivs.GOT_THAT, ivs.WRITING_DOWN, ivs.HELD, ivs.IS_THAT_RIGHT,
                                  ivs.YES_THATS_IT, ivs.SAVE_AND_NEXT, ivs.FINISH])
def test_the_answer_paths_words_are_keel_webs_own(word):
    assert f'"{word}"' in (_web_072() / "src/lib/translate.ts").read_text(encoding="utf-8"), word


def test_the_answer_paths_templates_are_keel_webs_own():
    translate = (_web_072() / "src/lib/translate.ts").read_text(encoding="utf-8")
    assert "`Heard: ${text}`" in translate and ivs.mic_heard("hello") == "Heard: hello"
    assert "`‹ Back to question ${n}`" in translate and ivs.back_to(4) == "‹ Back to question 4"


def test_the_seam_grants_the_mic_and_leaves_the_reads_real():
    """072 FR-7 / 115 FR-5, restated from keel-web's fixture: the seam's microphone is always granted with the
    fixture's steady level (0.12) and counted. The eval's seam puts no `classify` and no `answer` stand-in on it (spec
    048 judgement call 1): the page calls the real routes."""
    fixture = _fixture_115()
    assert "return !w.__micRefused" in fixture and "level: () => 0.12" in fixture
    assert "mic: mic(() => 0.12, false)" in ivs.SPEECH_SEAM
    assert "classify" not in ivs.SPEECH_SEAM and "answer:" not in ivs.SPEECH_SEAM


def test_the_player_never_presses_thats_my_answer():
    source = Path(ivs.__file__).read_text(encoding="utf-8")
    assert "def answer(" not in source and 'get_by_test_id("ai-answer")' not in source
    leg = (REPO_ROOT / "evals" / "interviewer_leg.py").read_text(encoding="utf-8")
    assert "player.answer()" not in leg and "player.next()" not in leg


# ------------------------------------------------------------------ spec 049: keel-web 073 hears them out

def _web_073() -> Path:
    root = load_config(validate=False).keel_web
    answer_path = root / "src/lib/answerPath.ts"
    if not answer_path.is_file() or "QUIET_" not in answer_path.read_text(encoding="utf-8"):
        pytest.skip("keel-web predates spec 073 (no quiet gap)")
    return root


def test_the_quiet_gap_is_keel_webs_own():
    source = (_web_073() / "src/lib/answerPath.ts").read_text(encoding="utf-8")
    if "QUIET_FREE_MS" not in source:          # 073 / 074: one gap, 1,500 then 4,000; the walk encodes neither
        m = re.search(r"QUIET_MS\s*=\s*([\d_]+)", source)
        assert m and 0 < int(m.group(1).replace("_", "")) <= ivs.GAP_TOLERATED_MS, m and m.group(0)
        return
    # keel-web 082 (D36): two gaps by window kind, restated; the walk tolerates the longer
    for name in ("QUIET_OPTION_MS", "QUIET_FREE_MS"):
        m = re.search(rf"export const {name} = ([\d_]+);", source)
        assert m and int(m.group(1).replace("_", "")) == getattr(ivs, name) <= ivs.GAP_TOLERATED_MS, name
    assert "seam.quietFreeMs ?? QUIET_FREE_MS" in source and "seam.quietMs ?? QUIET_OPTION_MS" in source


@pytest.mark.parametrize("word", [ivs.HEARING, ivs.ANSWERED, ivs.TAG_HEARING, ivs.TAG_NOT_TAKEN, ivs.RECORDING,
                                  ivs.HEARING_YOU])
def test_the_hearing_words_are_keel_webs_own(word):
    assert f'"{word}"' in (_web_073() / "src/lib/translate.ts").read_text(encoding="utf-8"), word


def test_tap_finish_is_gone_from_keel_web():
    """073 FR-7: the pilot's *Tap Finish when you're ready.* (`answeredPilot`) is gone -- the yes goes on by itself."""
    translate = (_web_073() / "src/lib/translate.ts").read_text(encoding="utf-8")
    assert "answeredPilot" not in translate and "Tap Finish when you" not in translate


@pytest.mark.parametrize("testid", ["ai-save", "ai-finish", "ai-ring"])
def test_the_save_finish_and_ring_selectors_are_in_keel_web(testid):
    root = _web_073() / "src"
    hits = [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert testid in Path(ivs.__file__).read_text(encoding="utf-8") + (
        REPO_ROOT / "evals" / "interviewer_leg.py").read_text(encoding="utf-8"), testid


def test_the_seam_listens_as_keel_webs_fixture_does_and_is_silent():
    """073 FR-8, 115 FR-5: keel-web's `__listening()` is the recorder running on the current window, which the eval's
    seam restates; the seam's `earcons: false` is a key keel-web reads."""
    fixture = _fixture_115()
    assert "w.__listening = () => recording;" in fixture
    assert "window.__listening = () => recording;" in ivs.SPEECH_SEAM
    assert "earcons: false" in ivs.SPEECH_SEAM
    seam = (_web_073() / "src/components/interview/ai/useSpeechRecognition.ts").read_text(encoding="utf-8")
    assert "earcons?: boolean" in seam and "s.earcons !== false" in seam
    assert "quietMs" not in ivs.SPEECH_SEAM                       # the journeys keep the default gap (073 FR-4)


# ------------------------------------------------------- spec 050: keel-web 074 (the story, the held yes) + 075 (beat)

def _web_075() -> Path:
    root = load_config(validate=False).keel_web
    flow = root / "src/lib/aiInterviewFlow.ts"
    if not flow.is_file() or "BEAT_MS" not in flow.read_text(encoding="utf-8"):
        pytest.skip("keel-web predates spec 075 (no beat)")
    return root


def test_the_beat_is_keel_webs_own_length():
    source = (_web_075() / "src/lib/aiInterviewFlow.ts").read_text(encoding="utf-8")
    m = re.search(r"BEAT_MS\s*=\s*([\d_]+)", source)
    assert m and int(m.group(1).replace("_", "")) == ivs.BEAT_MS, m and m.group(0)


@pytest.mark.parametrize("word", [ivs.STORY, ivs.BEAT, ivs.BEAT_PILL, ivs.MIC_OFF])
def test_the_story_beat_and_mic_off_words_are_keel_webs_own(word):
    assert f'"{word}"' in (_web_075() / "src/lib/translate.ts").read_text(encoding="utf-8"), word


@pytest.mark.parametrize("testid", ["ai-mic-off", "ai-mic-on", "ai-state", "ai-ring"])
def test_the_mic_and_beat_selectors_are_in_keel_web(testid):
    root = _web_075() / "src"
    hits = [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert testid in Path(ivs.__file__).read_text(encoding="utf-8"), testid


def test_the_lit_row_carries_data_unsure_and_the_stage_a_beat_phase():
    sheet = (_web_075() / "src/components/interview/ai/Sheet.tsx").read_text(encoding="utf-8")
    assert "data-unsure=" in sheet
    flow = (_web_075() / "src/lib/aiInterviewFlow.ts").read_text(encoding="utf-8")
    assert '"beat"' in flow


def test_the_seam_keeps_the_pages_beat_and_gap_and_stamps_every_start():
    """Spec 050 judgement call 3: the stack's journeys keep the page's 2 s beat and 4 s gap; the seam stamps every
    recording begun (spec 074: the one ear) and every release of the microphone (keel-web 116), so the leg can say
    nothing listened in a beat or after the thanks."""
    assert "beatMs" not in ivs.SPEECH_SEAM and "quietMs" not in ivs.SPEECH_SEAM and "silenceMs" not in ivs.SPEECH_SEAM
    assert "stamps('__recordStarts')" in ivs.SPEECH_SEAM and "stamps('__micReleasedAt')" in ivs.SPEECH_SEAM
    assert "__keelBeats" in ivs.FLOW_TIMELINE and "'beat'" in ivs.FLOW_TIMELINE


# ------------------------------------------------------------------ spec 058: keel-web 087's tap to hear

def _web_087() -> Path:
    root = load_config(validate=False).keel_web
    translate = root / "src/lib/translate.ts"
    if not translate.is_file() or "introHear" not in translate.read_text(encoding="utf-8"):
        pytest.skip("keel-web predates spec 087 (no tap to hear)")
    return root


@pytest.mark.parametrize("testid", [ivs.FACE_HEAR, ivs.INTRO_HEAR])
def test_the_hear_selectors_are_keel_webs_own(testid):
    root = _web_087() / "src"
    assert [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")], testid


def test_the_hear_words_and_the_four_hellos_are_keel_webs_own():
    root = _web_087()
    translate = (root / "src/lib/translate.ts").read_text(encoding="utf-8")
    assert "`Hear ${face} · ${seconds} s`" in translate and ivs.HEAR_PREFIX == "Hear "
    from harness import interviewer_fake as fake                          # noqa: PLC0415
    faces = root / "public"
    assert all((faces / fake.hello_path(f).lstrip("/")).is_file() for f in fake.FACES)
    # keel-web 087 FR-1: a retired face keeps its still (keel-cloud 110 serves its previewUrl); 094's, retired by
    # 110, have no hello; keel-web 125 FR-3 deletes nothing of 143's four (keel-cloud serves their helloUrl null)
    assert all((faces / fake.preview_path(f).lstrip("/")).is_file() for f in fake.FACES + fake.RETIRED)
    assert not any((faces / fake.hello_path(f).lstrip("/")).is_file() for f in fake.RETIRED_110)


def test_send_mores_credits_note_is_131s_and_read_apart_from_the_state_line():
    """Spec 092 FR-4a (keel-web 131 FR-3): `FORMAT_CREDITS_NOTE` under the rows (`format-credits`), drawn before the
    recorded / recording line; `formats_now` reads the note by its test id and the state line as the first other
    `.hint`, and S3 holds both and no greyed word on a row."""
    import inspect                                                              # noqa: PLC0415

    from evals import interviewer_leg                                           # noqa: PLC0415
    assert "export const FORMAT_CREDITS_NOTE = \"" + ivs.FORMAT_CREDITS_NOTE + "\";" in _web("src/lib/translate.ts")
    popup = _web("src/components/interviews/SendMorePopup.tsx")
    assert 'data-testid="format-credits"' in popup
    assert popup.index("FORMAT_CREDITS_NOTE}") < popup.index("SEND_FORMAT_RECORDED :"), "the note is the first hint"
    reader = inspect.getsource(ivs.Persona.formats_now)
    assert '.hint:not({FORMAT_CREDITS})' in reader and '"credits"' in reader
    held = inspect.getsource(interviewer_leg._screens_ready)
    assert 'formats["credits"] == ivs.FORMAT_CREDITS_NOTE' in held
    assert 'r["word"] is None for r in formats["rows"].values()' in held
