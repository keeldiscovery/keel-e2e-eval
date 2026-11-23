"""Spec 157: the three views' machinery with no stack -- the cloud's own story fixtures read and turned into the walk's
words and the runtime's script, the served cards a link owes a clip, the report and its log scan -- and the mirror of
the subjects: keel-cloud 259 / 260 / 261 (contract 81, the registry's story wording) and the keel-web 241 / 242
selectors the walk presses, read from the sibling checkouts the stack runs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from evals import three_views as tv
from evals import three_views_report as report
from harness import story_screens as ss
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)

#: keel-cloud 261 T3: sha256 of `canon/openapi-v2.yaml` at contract 81 (d838958b, unchanged at master 78237f87).
CONTRACT_81 = "f1c1733a9bfe9645f485b0ed0bb383246260ed569994ae83d08948be806685cf"


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"{path} is not in the sibling checkout (before keel-cloud 259 / keel-web 241)")
    return path


# ------------------------------------------------------------------------------------------- the cloud's fixtures

def readings() -> dict:
    _need(CLOUD / ss.FAKE_READINGS)
    return ss.fake_readings(CLOUD)


def test_the_beats_are_the_scripts_heard_words_in_order():
    """Spec 158 (keel-cloud 263 FR-1): one answer a beat, 1-4, and 5 where beat 2 named no moment."""
    script = readings()
    told = ss.said_turns(script)
    assert [n for n, _ in told][:4] == [1, 2, 3, 4]
    assert ([n for n, _ in told][4:] == [5]) == (ss.moment_beat(script) == 5)
    assert all(words and words == words.strip() for _, words in told)


def test_the_idea_beats_answer_every_limit_of_the_story():
    """Spec 158 (keel-cloud 263 FR-9): two idea beats; beat 2's one answer maps every limitation of the story."""
    script = readings()
    idea = ss.said_idea(script)
    assert [n for n, _ in idea] == [1, 2]
    second = ss.idea_reading_of(script, 2, idea[-1][1])
    assert len(second.get("limit_answers") or []) == len(ss.limits_read(script))
    assert second.get("new_way") and second.get("benefits")


def test_the_prevalence_fixture_carries_the_four_fields():
    _need(CLOUD / ss.EXAMPLE_PREVALENCE)
    prevalence = ss.example_prevalence(CLOUD)
    assert set(prevalence) == {"routine", "went_wrong", "no_sayer", "event"} and all(prevalence.values())


def test_the_context_result_is_the_scripts_slots():
    script = readings()
    result = ss.context_interpret_result(script, "DAILY")
    who, when = ss.reading_of(script, 1), ss.reading_of(script, ss.moment_beat(script))
    assert result["actor"] == who["actor"] and result["actor_plural"] == who["actor_plural"]
    assert result["occasion"] == {"noun": when["occasion"], "stem": when["occasion_stem"], "rhythm": "DAILY"}
    assert result["segment"] == {"core": who["segment_core"],
                                 "condition": ss.reading_of(script, 4)["only_those_who"]}
    assert result["window"] == {"proposed": None}


@pytest.mark.parametrize("window,rhythm", [({"count": 7, "unit": "NIGHTS"}, "DAILY"), ({"count": 4, "unit": "WEEKS"},
                                           "WEEKLY"), ({"count": 2, "unit": "MONTHS"}, "MONTHLY"),
                                          ({"count": 3, "unit": "MONTHS"}, "QUARTERLY")])
def test_the_rhythm_is_keel_clouds(window, rhythm):
    assert ss.rhythm_of(window) == rhythm


def test_the_screener_is_the_founders_condition_asked_yes_or_no():
    assert ss.condition_question("work at a company with more than 50 employees") == \
        "Do you work at a company with more than 50 employees?"
    assert ss.condition_question("") is None and ss.condition_question(None) is None


def _base() -> dict:
    return {"_entry_id": "base", "CONTEXT_INTERPRET": [ss.completed({"actor": "x"})],
            "CALIBRATION_QUESTIONS": [ss.completed({"vector": "PROBLEM", "questions": [
                {"key": "problem.prevalence", "routine": "r", "went_wrong": "w", "no_sayer": "n", "event": "e"},
                {"key": "problem.frequency"}]})],
            "CALIBRATION_QUESTIONS+repair": [ss.completed({"vector": "SOLUTION", "questions": [
                {"key": "solution.compatibility"}]})],
            "RESPONDENT_QUESTIONS": [ss.completed({"part": 1, "link": "PRIMARY", "items": [
                {"key": "problem.prevalence", "event": "old"}], "condition": {"question": "Old?", "inside": "YES"}})]}


def test_the_runtime_script_moves_exactly_three_answers():
    script = readings()
    prevalence = {"routine": "R", "went_wrong": "W", "no_sayer": "N", "event": "E"}
    base = _base()
    out = ss.story_runtime_script(base, script, prevalence, {"count": 7, "unit": "NIGHTS"})
    assert base["CALIBRATION_QUESTIONS"][0]["result"]["questions"][0]["event"] == "e"      # the base is not touched
    assert out["CONTEXT_INTERPRET"][0]["result"]["actor"] == ss.reading_of(script, 1)["actor"]
    q = out["CALIBRATION_QUESTIONS"][0]["result"]["questions"][0]
    assert {k: q[k] for k in prevalence} == prevalence
    assert out["CALIBRATION_QUESTIONS+repair"] == base["CALIBRATION_QUESTIONS+repair"]   # a solution answer, untouched
    part1 = out["RESPONDENT_QUESTIONS"][0]["result"]
    assert part1["items"][0]["event"] == "E"
    assert part1["condition"] == {"question": ss.condition_question(ss.reading_of(script, 4)["only_those_who"]),
                                  "inside": "YES"}
    assert "_story" in out


def test_served_cards_name_every_card_a_stranger_answers():
    interview = {"gate": {"itemId": "g", "clipId": "c1", "condition": {"question": "Q?", "clipId": "c0"}},
                 "parts": [{"items": [{"itemId": "i1", "dimension": "problem.frequency", "clipId": "c2"},
                                      {"itemId": "i2", "dimension": "problem.importance"}]}]}
    cards = ss.served_cards(interview)
    assert [c["kind"] for c in cards] == ["screener", "gate", "item", "item"]
    assert [c["itemId"] for c in cards if not c["clipId"]] == ["i2"]
    money = {"condition": {"question": "Q?", "clipId": "c0"}, "problemCheck": {"question": "Does your x have this "
                                                                                           "problem?", "clipId": "k"}}
    assert [c["kind"] for c in ss.served_cards(money)] == ["screener", "check"]


def test_the_problem_projects_name_is_keel_webs():
    assert ss.problem_name_of(" A study ") == "A study: the problem"


# ------------------------------------------------------------------------------------------- the report

def _legs():
    green = tv.Leg("FR-1a", "the problem", status="green", checks=[tv.Check("held", True, "s", "founder")])
    failed = tv.Leg("FR-2 problem · orb", "the link", status="failed", why="the gate (screen: gate; view: orb)",
                    checks=[tv.Check("the gate", False, "the gate card", "orb", {"got": 1})])
    unbuilt = tv.Leg("FR-1c", "money", status="written, not run", why="keel-web 243 not in the checkout")
    return [green, failed, unbuilt]


def test_the_report_names_every_check_and_a_failures_screen_and_view():
    md = report.report_markdown(_legs(), {"cloud": "c", "web": "w", "eval": "e", "profile": "eval", "started": "t",
                                          "seconds": 1, "bundle": "b"}, report.log_scan(""))
    assert "| FR-1a | the problem | **green** |" in md
    assert "[FAILED] the gate (screen: the gate card; view: orb)" in md
    assert "**written, not run** -- keel-web 243 not in the checkout" in md
    assert "**1 of 3 legs green.**" in md
    assert "no HeyGen, no OpenAI, no Anthropic host contacted" in md


def test_the_log_scan_sees_a_vendor_and_a_paid_clip():
    clean = report.log_scan("speech clip made: charge=SPEECH project=p clip=c cost_micro_usd=0\n")
    assert clean["clean"] is True and clean["speech_clips"] == 1
    for line in ("POST https://api.openai.com/v1/audio/speech", "OpenAiSpeech: ...", "api.heygen.com",
                 "speech clip made: charge=SPEECH project=p clip=c cost_micro_usd=1800"):
        assert report.log_scan(line)["clean"] is False, line
    assert report.log_scan(None)["measured"] is False
    assert "not measured" in report.scan_line(report.log_scan(None))


def test_the_legs_are_fr1_a_to_d_and_fr2s_nine():
    assert [leg for leg, _ in tv.FOUNDER_LEGS] == ["FR-1a", "FR-1b", "FR-1c", "FR-1d"]
    assert len(tv.STRANGER_LEGS) == 9
    # spec 159 (keel-web 253): the text view is the orb view
    assert {leg.split(" · ")[1] for leg, _ in tv.STRANGER_LEGS} == {"orb", "avatar", "copilot"}


# ------------------------------------------------------------------------------------------- the subjects' mirror

def test_contract_81_is_the_one_the_walk_reads():
    text = _need(CLOUD / "canon" / "openapi-v2.yaml").read_bytes()
    if b"/story/turns/{n}" not in text:
        pytest.skip("keel-cloud before 259")
    for route in ("/v2/projects/{projectId}/story", "/v2/projects/{projectId}/story/turns/{n}",
                  "/v2/projects/{projectId}/story/confirm", "/v2/projects/{projectId}/story/transcribe",
                  "/v2/projects/{projectId}/idea/turns/{n}", "/v2/projects/{projectId}/idea/brand",
                  "/v2/projects/{projectId}/idea/confirm", "/v2/projects/{projectId}/idea/spoken",
                  "/v2/projects/{projectId}/questionnaire/retry"):
        assert f"  {route}:".encode() in text, route
    for field in (b"problemCheck", b"introducedAs", b"ideaStory", b"readInstead", b"clipId", b"parentProjectId"):
        assert field in text, field
    digest = hashlib.sha256(text).hexdigest()
    if digest != CONTRACT_81:
        pytest.skip(f"keel-cloud's contract moved past 81 ({digest[:12]}): re-cut this pin")
    assert digest == CONTRACT_81


def test_the_registry_export_holds_the_story_wording():
    """keel-cloud 259 / 261: the derived registry the stack exports carries the three new respondent keys."""
    text = _need(CLOUD / "src" / "main" / "resources" / "keel" / "dimension-registry.json").read_text(encoding="utf-8")
    if "story_gate" not in text:
        pytest.skip("keel-cloud before 259")
    found = {}

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("story_gate", "problem_check", "problem_check_introduced"):
                    found[key] = value
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(json.loads(text))
    assert found == {"story_gate": "In your {window_last}, did this happen to you?",
                     "problem_check": "Does your {actor} have this problem?",
                     "problem_check_introduced": "what your {actor} goes through"}


#: The keel-web 245 test ids the walk taps or reads (spec 158: the orb is the one button on the conversation). keel-web
#: 249 (spec 158c FR-7): the glow is gone, the card (`UnderstoodCard`) draws `story-boxes`, the founder's words are in
#: *What I hear* (`story-heard`), beat 3's crosses and the idea's ticks are cards of their own.
WEB_SELECTORS = {
    "src/components/story/StoryStart.tsx": ("story-start",),
    "src/components/story/StoryTurn.tsx": ("story-turn", "story-limits", "story-card-limit", "story-folded",
                                           "story-understood"),
    "src/components/voice/VoiceStage.tsx": ("story-kicker", "story-begin", "story-deaf", "story-q", "story-state",
                                            "story-words", "story-heard"),
    "src/components/voice/KeelOrb.tsx": ("story-orb",),
    "src/components/story/StoryCheck.tsx": ("story-check", "story-boxes-screen", "story-check-said", "story-building",
                                            "story-readback"),   # story-named, story-today: gone in 245 round 2
    "src/components/voice/UnderstoodCard.tsx": ("story-boxes",),
    "src/components/voice/StageOpener.tsx": ("guide-opener",),
    "src/components/guide/WelcomeSheet.tsx": ("guide-welcome",),
    "src/components/guide/GuideStage.tsx": ("guide-skip",),
    "src/components/idea/SolutionStart.tsx": ("solution-start", "solution-candidate", "solution-pick",
                                              "solution-create-problem", "solution-candidate-frame"),
    "src/components/idea/IdeaStart.tsx": ("idea-still",),
    "src/components/idea/IdeaTurn.tsx": ("idea-turn", "idea-card-limit", "idea-understood"),
    "src/components/idea/LogoDrop.tsx": ("idea-drop",),
    "src/components/idea/IdeaBoxes.tsx": ("idea-check", "idea-boxes-screen", "idea-boxes-said", "idea-readback-story",
                                          "idea-story-player"),
    "src/components/money/MoneyStart.tsx": ("money-start", "money-problem", "money-pick-problem", "money-create-problem",
                                            "money-solution", "money-use-solution", "money-create-solution",
                                            "money-offer-name", "money-use-name"),
    "src/routes/founder/corridor/MoneyReplayRoute.tsx": ("money-replay",),
    # spec 159 (keel-web 253 / 254): the stranger's views are the one AI player -- the orb or the face, the film on its
    # stage; the text player's story card (`StoryScreen`) and its voice bar (`CardVoice`) are no longer walked
    "src/components/interview/ai/AiInterviewPlayer.tsx": ("ai-player", "ai-stage", "ai-orb", "ai-orb-state", "ai-story",
                                                          "ai-story-orb", "ai-story-go-on", "ai-face", "ai-done"),
    "src/components/interview/ai/AiIntro.tsx": ("ai-intro", "intro-orb", "start-talking", "ai-mic-test",
                                                "ai-mic-heard", "ai-mic-fallback"),
    "src/components/interview/ai/Sheet.tsx": ("ai-sheet", "ai-options", "ai-back", "ai-skip", "ai-yes", "ai-save",
                                              "ai-field"),
    "src/components/interviews/SentPage.tsx": ("try-it-yourself", "try-keel-voice"),
    "src/routes/landing/ProjectTabs.tsx": ("project-row-defined",),
    "src/routes/founder/calls/CopilotCard.tsx": ("show-story", "story-again", "show-idea-story", "copilot-grown",
                                                 "copilot-shrink", "copilot-still"),
}


def test_the_glow_and_the_rough_board_are_gone_and_the_walk_reads_neither():
    """Spec 158c FR-7: no `story-glow` (keel-web 249 FR-1: `KeelGlow` left `KeelOrb.tsx`) and no rough board (FR-5:
    `BoxBoard.tsx` removed); the walk's orb is the orb alone."""
    _need(WEB / "src" / "components" / "voice" / "UnderstoodCard.tsx")
    assert "story-glow" not in (WEB / "src" / "components" / "voice" / "KeelOrb.tsx").read_text(encoding="utf-8")
    assert not (WEB / "src" / "lib" / "story" / "BoxBoard.tsx").exists()
    # the orb is read off the orb alone; the snapshot only counts a glow (`glow`) to hold that none is drawn
    assert ss.ORB == "[data-testid=story-orb]" and "story-glow" not in ss.ORB_WATCH and "story-glow" not in ss._ORB_JS


def test_the_chime_counter_is_keel_webs_test_hook():
    """Spec 158c FR-7: `window.__keelChime` counts the hand-overs in the test build (keel-web 249 FR-3)."""
    source = _need(WEB / "src" / "lib" / "story" / "voice.ts").read_text(encoding="utf-8")
    assert "window.__keelChime = (window.__keelChime ?? 0) + 1" in source
    translate = (WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    for words in (ss.TURN_LISTENING, ss.TURN_READBACK):
        assert f'"{words}"' in translate, words


def test_the_card_rows_are_keel_webs():
    """Spec 158c FR-7: the walk reads the card's rows by `data-box`, keyed as keel-web's `BOX_KEYS` names them."""
    board = _need(WEB / "src" / "lib" / "story" / "board.ts").read_text(encoding="utf-8")
    keys = "[" + ", ".join(f'"{k}"' for k in ss.CARD_ROWS) + "]"
    assert f"BOX_KEYS = {keys} as const" in board, keys


@pytest.mark.parametrize("path", sorted(WEB_SELECTORS))
def test_every_selector_the_walk_presses_is_in_keel_web(path):
    source = _need(WEB / path).read_text(encoding="utf-8")
    missing = [t for t in WEB_SELECTORS[path] if f'"{t}"' not in source and f"'{t}'" not in source]
    assert not missing, (path, missing)


def test_the_story_lines_are_keel_webs():
    """keel-web 245's lines the walk waits on: the beats' questions, the openings, the questions back, the return."""
    source = _need(WEB / "src" / "lib" / "storyLines.ts").read_text(encoding="utf-8")
    for n, question in ss.STORY_QUESTIONS.items():
        assert f'"{question}"' in source, (n, question)
    for line in (ss.STORY_READY, ss.SOLUTION_READY, ss.SOLUTION_TURN):
        assert f'"{line}"' in source, line
    translate = (WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    for words in (ss.STORY_KICKER, ss.VOICE_READS, ss.BEGIN_TITLE, ss.BOXES_ASK, ss.STORY_ASK, ss.IDEA_BOXES_ASK,
                  ss.BACK_TO_SOLUTION, ss.NEW_PROBLEM, "Defined, not sent"):
        assert f'"{words}"' in translate, words
    solution = (WEB / "src" / "lib" / "solutionStart.ts").read_text(encoding="utf-8")
    assert f'"{ss.PENDING_START_KEY}"' in solution
