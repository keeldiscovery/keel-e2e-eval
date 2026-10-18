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


def test_the_init_script_is_keel_webs_fixture_restated():
    fixture = _web("tests/fixtures/interviewer/fakeSpeech.ts")
    for name in ("__keelSpeech", "__say", "__speechError", "__speechEnd", "__recognisers", "Recognition"):
        assert name in fixture and name in ivs.SPEECH_SEAM, name


@pytest.mark.parametrize("word", [ivs.PERSONA_RECORDING, ivs.PERSONA_NOT_RECORDED, ivs.TRY_IT_YOURSELF_RECORDING,
                                  ivs.TRY_NOTHING_STORED, ivs.SEND_TEXT_ONLY_LINKS, ivs.SEND_FORMAT_RECORDED,
                                  ivs.SEND_FORMAT_RECORDING, ivs.RECORD_FACE_TITLE, ivs.CHANGE_FACE_TITLE,
                                  iv.TEXT_ONLY, iv.FORMAT_RECORDING, iv.FORMAT_NOT_RECORDED, iv.FORMAT_NEEDS_CREDITS])
def test_the_words_are_keel_webs_own(word):
    assert f'"{word}"' in _web("src/lib/translate.ts"), word


def test_the_templates_are_keel_webs_own():
    translate = _web("src/lib/translate.ts")
    assert "`${face} asks your questions.`" in translate and ivs.persona_asks("Tito") == "Tito asks your questions."
    assert "`Change who asks · ${creditsAmount(credits)} AI credits`" in translate
    assert ivs.change_who_asks(400) == "Change who asks · 400 AI credits"
    assert "`Record the interviewer · ${creditsAmount(credits)} AI credits`" in translate
    assert "`${face} asks your questions`" in translate and "`${face} will ask you ${questions} questions.`" in translate


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


def test_the_seam_ends_an_utterance_on_a_final_and_grants_the_mic():
    """072 FR-3 / FR-7, restated from keel-web's fixture: a final result is followed by the recogniser's end, and the
    seam's microphone is always granted. The eval's seam puts no `classify` on it (judgement call 1)."""
    fixture = _web(  # noqa: F841 - read for its presence
        "tests/fixtures/interviewer/fakeSpeech.ts")
    if "mic:" not in fixture:
        pytest.skip("keel-web's fixture predates spec 072")
    assert "if (final) setTimeout(" in ivs.SPEECH_SEAM and "onend" in ivs.SPEECH_SEAM
    assert "mic: { acquire: async () => true" in ivs.SPEECH_SEAM
    # keel-web 076: the fixture's microphone counts its acquisitions and is granted unless a test refused it
    # (`installRefusedMic`); before 076 it was granted outright
    assert "acquire: async () => true" in fixture or "return !w.__micRefused" in fixture
    assert "classify" not in ivs.SPEECH_SEAM


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


@pytest.mark.parametrize("word", [ivs.HEARING, ivs.ANSWERED, ivs.TAG_HEARING, ivs.TAG_NOT_TAKEN])
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
    """073 D-04 / FR-8: keel-web's fixture gains `__listening()` (the newest recogniser started and still handed
    results), which the eval's seam restates; the seam's `earcons: false` is a key keel-web reads."""
    fixture = _web("tests/fixtures/interviewer/fakeSpeech.ts")
    if "__listening" not in fixture:
        pytest.skip("keel-web's fixture predates spec 073")
    assert "__listening" in ivs.SPEECH_SEAM and "r.onresult" in ivs.SPEECH_SEAM
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
    recogniser started (and every recording begun) so the leg can say nothing listened in a beat."""
    assert "beatMs" not in ivs.SPEECH_SEAM and "quietMs" not in ivs.SPEECH_SEAM
    assert "__speechStarts" in ivs.SPEECH_SEAM and "__recordStarts" in ivs.SPEECH_SEAM
    assert "__keelBeats" in ivs.FLOW_TIMELINE and "'beat'" in ivs.FLOW_TIMELINE
