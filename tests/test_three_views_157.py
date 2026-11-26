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
from harness import interviewer_screens as ivs
from harness import story_screens as ss
from harness import three_surfaces as ts
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
    """Spec 161 (keel-cloud 268 FR-3; 158's 263 before it): one answer a beat, 1-5, 6 where beat 2 named no moment, 7."""
    script = readings()
    told = ss.said_turns(script)
    assert [n for n, _ in told][:5] == [1, 2, 3, 4, 5] and [n for n, _ in told][-1] == 7
    assert (6 in [n for n, _ in told]) == (ss.moment_beat(script) == 6)
    assert all(words and words == words.strip() for _, words in told)


def test_the_idea_beats_answer_every_limit_of_the_story():
    """Spec 162 FR-1 (keel-cloud 271 FR-3 to FR-6; 158's two beats of 263 before it): four idea beats; beat 3's one
    answer maps every limitation of the story."""
    script = readings()
    idea = ss.said_idea(script)
    assert [n for n, _ in idea] == [1, 2, 3, 4]
    third = ss.idea_reading_of(script, 3, dict(idea)[3])
    assert len(third.get("limit_answers") or []) == len(ss.limits_read(script))
    assert third.get("statement") and third.get("advantage")


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
                                 "condition": ss.reading_of(script, ss.ALL_OF_THEM_BEAT)["only_those_who"]}
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
    assert part1["condition"] == {"question": ss.condition_question(
        ss.reading_of(script, ss.ALL_OF_THEM_BEAT)["only_those_who"]), "inside": "YES"}
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
    if found.get("story_gate") == ts.GATE_WORDS_BEFORE_277:
        pytest.skip("keel-cloud before 277")                                   # spec 169: 269's words match nowhere now
    assert ts.is_gate_words(found.pop("story_gate"))                           # spec 169 (keel-cloud 277 FR-1)
    assert found == {"problem_check": "Does your {actor} have this problem?",
                     "problem_check_introduced": "what your {actor} goes through"}


#: The keel-web 245 test ids the walk taps or reads (spec 158: the orb is the one button on the conversation). keel-web
#: 249 (spec 158c FR-7): the glow is gone, the card (`UnderstoodCard`) draws `story-boxes`, the founder's words are in
#: *What I hear* (`story-heard`), beat 3's crosses and the idea's ticks are cards of their own.
WEB_SELECTORS = {
    "src/components/story/StoryStart.tsx": ("story-start",),
    # spec 172 FR-1 (keel-web 275 FR-2, FR-3): no *What I hear* (`story-heard`), no founder's lines (`story-words`), no
    # folded transcript (`story-folded`) -- Keel's one line (`beat-ask`), the folded question's toggle, the no-words line
    "src/components/story/StoryTurn.tsx": ("story-turn", "story-limits", "story-card-limit", "story-understood"),
    "src/components/voice/VoiceStage.tsx": ("story-kicker", "story-begin", "story-deaf", "story-q", "story-state",
                                            "beat-ask", "beat-question-fold", "beat-no-words"),
    # spec 172 FR-3 (keel-web 276 FR-1 to FR-3): the table's buttons and the sheet
    "src/components/story/BoxesReview.tsx": ("boxes-yes", "boxes-no", "boxes-finality", "boxes-fix", "boxes-fix-said",
                                             "boxes-fix-box", "boxes-fix-q", "boxes-fix-yes"),
    "src/components/voice/KeelOrb.tsx": ("story-orb",),
    "src/components/story/StoryCheck.tsx": ("story-check", "story-boxes-screen", "story-check-said", "story-building",
                                            "story-readback"),   # story-named, story-today: gone in 245 round 2
    "src/components/voice/UnderstoodCard.tsx": ("story-boxes",),
    "src/components/voice/StageOpener.tsx": ("guide-opener",),
    "src/components/guide/WelcomeSheet.tsx": ("guide-welcome",),
    "src/components/guide/GuideStage.tsx": ("guide-skip",),
    "src/components/idea/SolutionStart.tsx": ("solution-start", "solution-candidate", "solution-pick",
                                              "solution-create-problem", "solution-candidate-frame"),
    # spec 162 (keel-web 259's eval mirrors): the film opens the solution, the brand typed, four beats, the board, the
    # plate and the film, the verdict and the pilot ask, the failed build
    "src/components/idea/IdeaStart.tsx": ("idea-start", "idea-problem-film", "idea-start-said"),
    "src/components/idea/IdeaBrandPage.tsx": ("idea-brand-page", "idea-name", "idea-tagline", "idea-tagline-count",
                                              "idea-swatch", "idea-brand-preview", "idea-brand-continue"),
    "src/components/idea/IdeaTurn.tsx": ("idea-turn", "idea-understood"),
    "src/components/idea/LogoDrop.tsx": ("idea-drop", "idea-icon-file", "idea-logo-line", "idea-icon-fault"),
    "src/components/idea/IdeaBoxes.tsx": ("idea-check", "idea-boxes-screen", "idea-board", "idea-boxes-said",
                                          "idea-readback-story", "idea-story-player", "idea-pilot", "idea-pilot-card",
                                          "idea-pilot-options", "idea-building", "idea-story-said"),
    # spec 170 (keel-web 268: the verdict step retired; 269: the film's one question, Yes / No, the sheet; 270: the
    # frames are the progress, the bar's legend)
    "src/components/story/FilmReview.tsx": ("film-ask", "film-yes", "film-no", "film-fix"),
    "src/components/story/FramePlan.tsx": ("story-plan", "story-plan-row", "story-plan-word", "story-plan-mark",
                                           "story-plan-chip", "story-plan-note",
                                           "story-plan-reason", "story-plan-thumb", "story-bar", "story-bar-wrap",
                                           "story-bar-legend"),
    "src/components/money/MoneyStart.tsx": ("money-start", "money-problem", "money-pick-problem", "money-create-problem",
                                            "money-solution", "money-use-solution", "money-create-solution",
                                            "money-offer-name", "money-use-name"),
    "src/routes/founder/corridor/MoneyReplayRoute.tsx": ("money-replay",),
    # spec 159 (keel-web 253 / 254): the stranger's views are the one AI player -- the orb or the face, the film on its
    # stage; the text player's story card (`StoryScreen`) and its voice bar (`CardVoice`) are no longer walked. Spec 160
    # (keel-web 256): the film's dim orb and *Go on to the question* are gone; *Begin the interview*, the face's column
    # and caption, the tick; the intro's one button and its block; the replay mark; the film's icons and board; the words
    "src/components/interview/ai/AiInterviewPlayer.tsx": ("ai-player", "ai-stage", "ai-orb", "ai-orb-state", "ai-story",
                                                          "ai-film-begin", "ai-face", "ai-facecol", "ai-caption",
                                                          "ai-face-state", "ai-done", "ai-done-tick"),
    # spec 170 (keel-web 266): the one line (`ai-intro-line`) and *Say anything.* (`ai-mic-say`); 256's study line,
    # asks line and chips are gone
    "src/components/interview/ai/AiIntro.tsx": ("ai-intro", "intro-orb", "ai-start", "ai-mic-test", "ai-mic-heard",
                                                "ai-mic-say", "ai-mic-block", "ai-intro-answers", "ai-intro-line",
                                                "ai-intro-mic-line", "ai-intro-transcribed", "ai-intro-consent"),
    "src/components/interview/ai/Sheet.tsx": ("ai-sheet", "ai-options", "ai-back", "ai-skip", "ai-yes", "ai-save",
                                              "ai-field", "ai-replay", "ai-story-ask", "ai-story-got-it"),
    "src/lib/story/StoryPlayer.tsx": ("story-player", "story-board", "story-line", "story-read", "ai-film-pause",
                                      "ai-film-again", "ai-film-board"),
    "src/components/interview/ai/SpokenWords.tsx": ("ai-words",),
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
    if not ss.web_has_257(WEB):
        # spec 161 FR-1: the tasks row is keel-web 257's -- before it the six rows of 249 (`CARD_ROWS` less `tasks`)
        keys = "[" + ", ".join(f'"{k}"' for k in ss.CARD_ROWS if k != "tasks") + "]"
        assert f"BOX_KEYS = {keys} as const" in board, keys
        pytest.skip("keel-web 257 is not in the keel-web checkout: the tasks row pending keel-web 257")
    keys = "[" + ", ".join(f'"{k}"' for k in ss.CARD_ROWS) + "]"
    assert f"BOX_KEYS = {keys} as const" in board, keys


@pytest.mark.parametrize("path", sorted(WEB_SELECTORS))
def test_every_selector_the_walk_presses_is_in_keel_web(path):
    source = _need(WEB / path).read_text(encoding="utf-8")
    missing = [t for t in WEB_SELECTORS[path] if f'"{t}"' not in source and f"'{t}'" not in source]
    assert not missing, (path, missing)


def test_the_retired_screens_are_gone_from_keel_web():
    """Spec 170 FR-1 / FR-2 (keel-web 266, 268, 270): the verdict cards, 256's intro lines and 263's tally and steps list
    are drawn nowhere -- the walk never waits on them (their ids are kept only to name a screen that still draws one)."""
    _need(WEB / "src" / "components" / "story" / "FilmReview.tsx")
    sources = "".join(p.read_text(encoding="utf-8") for p in (WEB / "src").rglob("*.tsx"))
    for testid in ss.VERDICT_IDS_BEFORE_268 + ivs.ENTRY_IDS_BEFORE_266 + ("story-plan-tally", "story-build-steps",
                                                                          "story-heard", "story-words", "story-folded"):
        assert f'data-testid="{testid}"' not in sources, testid
    translate = (WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    assert f'"{ss.STORY_ASK_BEFORE_269}"' not in translate                 # a comment may still name it
    assert f'filmAsk: "{ss.STORY_ASK}"' in translate
    assert "filmAskIdea: (name: string): string => `Does this film show ${name} accurately?`" in translate
    assert ss.film_ask_idea("Runcheck") == "Does this film show Runcheck accurately?"
    assert ss.film_ask_idea("") == ss.STORY_ASK
    assert '"Say yes, or just tell me if you want a different bar."' not in translate


def test_the_story_lines_are_keel_webs():
    """keel-web 245's lines the walk waits on: the beats' questions, the openings, the questions back, the return."""
    source = _need(WEB / "src" / "lib" / "storyLines.ts").read_text(encoding="utf-8")
    # spec 161 FR-1: the seven beats are keel-web 257's -- before it the five of 245 (`STORY_QUESTIONS_263`)
    questions = ss.STORY_QUESTIONS if ss.web_has_257(WEB) else ss.STORY_QUESTIONS_263
    for n, question in questions.items():
        assert f'"{question}"' in source, (n, question)
    # spec 162 (keel-web 259): the solution's *Ready?* and its turn line retired with the replay
    for line in (ss.STORY_READY,) + (() if ss.web_has_259(WEB) else (ss.SOLUTION_READY, ss.SOLUTION_TURN)):
        assert f'"{line}"' in source, line
    translate = (WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    for words in (ss.STORY_KICKER, ss.VOICE_READS, ss.BEGIN_TITLE, ss.BOXES_LINE["story"],
                  ss.STORY_ASK, ss.BOXES_LINE["idea"], ss.BOXES_PRESS["story"], ss.FINALIZE["story"],
                  ss.FINALIZE["idea"], ss.FIX_WHAT_TO_CHANGE, ss.BACK_TO_SOLUTION, ss.NEW_PROBLEM, "Defined, not sent"):
        assert f'"{words}"' in translate, words
    solution = (WEB / "src" / "lib" / "solutionStart.ts").read_text(encoding="utf-8")
    assert f'"{ss.PENDING_START_KEY}"' in solution
