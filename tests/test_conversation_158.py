"""Spec 158: the conversation's machinery with no stack -- beat 3's long telling and what the cloud's fake reader keeps
of it, the orb's states held in order, the report's beats, the stored-words read's guard -- and the mirror of the
subjects: keel-cloud 263 (contract 83, the five questions, the fake readings on the beats) and keel-web 245's hooks,
read from the sibling checkouts the stack runs."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from evals import three_views as tv
from evals import three_views_report as report
from harness import story_screens as ss
from stack import ledger
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)

#: keel-cloud 263 T0 (`f6f88a5f`, unchanged at master `69158457`): sha256 of `canon/openapi-v2.yaml` at contract 83.
CONTRACT_83 = "40706a958491cb5bc195f36eb843b8d04a027682f9bb4541b74762cc36e0de4d"
#: keel-cloud 263 `FakeStoryReadings.SENTENCES`: an unscripted beat 3 is read a sentence a row.
SENTENCES = re.compile(r"(?<=[.;!?])\s+")
#: keel-cloud 263 `StoryTurns`: four limitations kept, nine words a row, forty words a readback.
LIMITS_MAX, ROW_MAX_WORDS, READBACK_MAX_WORDS = 4, 9, 40


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"{path} is not in the sibling checkout")
    return path


def readings() -> dict:
    _need(CLOUD / ss.FAKE_READINGS)
    script = ss.fake_readings(CLOUD)
    if not any(int(t.get("turn", 0)) == 3 and (t.get("result") or {}).get("limits") for t in script.get("turns") or []):
        pytest.skip("keel-cloud before 263 (the fake readings not yet on the beats)")
    return script


# ------------------------------------------------------------------------------------------- beat 3, told long

#: keel-cloud 268 `FakeStoryReadings`: a sentence opening on *Today* is the way, one opening on *In the end* the cost.
WAY_OR_COST = re.compile(r"(?i)^(?:(?:today|these days|right now)[,\s]|(?:so\s+)?(?:in the end|it costs them|which means)"
                         r"[,:\s])")


def echo_rows(words: str) -> list[str]:
    """What `FakeStoryReadings` reads an unscripted beat 3 as: each sentence a row (its end punctuation off, nine
    words at most, capitalised), repeats dropped, four kept -- spec 161 (keel-cloud 268 FR-1): the way's sentence and
    the cost's are not rows."""
    rows: list[str] = []
    for sentence in SENTENCES.split(words.strip().rstrip(".!? ")):
        if WAY_OR_COST.match(sentence.strip()):
            continue
        row = " ".join(re.sub(r"[.!?;,\s]+$", "", sentence.strip()).split()[:ROW_MAX_WORDS])
        row = row[:1].upper() + row[1:]
        if row and row.lower() not in (r.lower() for r in rows):
            rows.append(row)
    return rows


def limits_readback(rows: list[str], kept_four: bool) -> str:
    """keel-cloud 263 `StoryService.limitsReadback`: the rows named under forty words, a row at a time."""
    numbers = ["none", "one", "two", "three", "four"]
    opening = "I kept the four that matter most: " if kept_four else f"I heard {numbers[min(len(rows), 4)]}: "
    budget = READBACK_MAX_WORDS - len(opening.split()) - 2
    line = opening
    for i, row in enumerate(rows):
        words = len(row.split())
        if words > budget:
            break
        budget -= words
        line += ("" if i == 0 else "; ") + (row if i == 0 else row[0].lower() + row[1:])
    return line + ". Anything else?"


def test_the_long_telling_is_long_names_five_and_says_the_cost():
    script = readings()
    words, rows = ss.long_beat_3(script)
    assert ss.LONG_ANSWER_MIN <= len(words) <= ss.LONG_ANSWER_MAX
    assert len(rows) == 4 and rows[:3] == ss.limits_read(script)[:3]
    five = ss.limits_read(script)[:3] + list(ss.MORE_LIMITS)
    assert all(limit.lower() in words.lower() for limit in five)
    assert (ss.heard_cost(script) or "someone gets paid wrong").lower() in words.lower()
    # no hanging word at its end (keel-web 245 FR-5: an answer ending on one is held)
    assert words.rstrip(".").split()[-1].lower() not in ("the", "a", "an", "and", "so", "but", "or", "like", "um", "uh",
                                                          "that", "which", "because")


def test_the_fake_reader_keeps_the_four_it_opens_with_and_names_them_back():
    script = readings()
    words, rows = ss.long_beat_3(script)
    read = echo_rows(words)
    assert len(read) > LIMITS_MAX and read[:LIMITS_MAX] == rows
    said = limits_readback(read[:LIMITS_MAX], kept_four=True)
    assert len(said.split()) <= READBACK_MAX_WORDS
    assert not tv._named(rows, said)                                  # every cross named back


def test_the_correction_narrows_with_its_word():
    assert ss.CORRECTION_4_WORD in ss.CORRECTION_4
    assert not re.search(r"(?i)^(yes|yeah|yep|right|correct|that is all)\b", ss.CORRECTION_4)


def test_said_turns_refuses_a_script_off_the_beats():
    with pytest.raises(ValueError):
        ss.said_turns({"turns": [{"turn": 1, "heard": "a"}, {"turn": 2, "heard": "b"}, {"turn": 6, "heard": "c"}]})
    with pytest.raises(ValueError):                         # spec 161: 263's four beats are no longer the script
        ss.said_turns({"turns": [{"turn": n, "heard": str(n), "result": {}} for n in (1, 2, 3, 4)]})
    ok = {"turns": [{"turn": n, "heard": str(n), "result": {}} for n in (1, 2, 3, 4, 5, 7)]
          + [{"turn": 5, "heard": "fix", "correction": True, "result": {"only_those_who": "x"}}]}
    assert ss.said_turns(ok) == [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (7, "7")]
    assert ss.reading_of(ok, 5, correction=True) == {"only_those_who": "x"}


def test_the_said_name_carries_the_colour():
    assert ss.said_name("Runcheck") == "Runcheck, in blue"
    assert ss.rgb_of(ss.SAID_COLOUR[1]) == "rgb(47, 109, 181)"


# ------------------------------------------------------------------------------------------- the orb, the report

def test_the_orb_states_fold_and_hold_in_order():
    log = [{"state": s, "path": p} for s, p in (("paused", "/a"), ("speaking", "/b"), ("speaking", "/b"),
                                                ("listening", "/b"), ("hearing", "/b"), ("listening", "/b"),
                                                ("writing", "/b"), ("speaking", "/b"), ("listening", "/b"))]
    seq = ss.orb_sequence(log, "/b")
    assert seq == ["speaking", "listening", "hearing", "listening", "writing", "speaking", "listening"]
    assert ss.holds_in_order(seq, ss.BEAT_ORB)
    assert not ss.holds_in_order(["speaking", "listening", "writing", "speaking"], ss.BEAT_ORB)


def test_the_report_names_the_beats():
    told = [{"label": "the long telling", "project": "12345678-aaaa", "beats": [
        {"turn": 3, "asked": {"question": ss.STORY_QUESTIONS[3]}, "put": {"sent": {"text": "x" * 1600},
                                                                         "body": {"readback": "I kept the four"}},
         "readback": {"limits": ["A", "B"]}, "orb": ss.BEAT_ORB, "next": "4"},
        {"turn": 4, "asked": {"question": ss.STORY_QUESTIONS[4]}, "put": {"sent": {"text": "y"}, "body": {
            "readback": "S. Right?"}}, "readback": {}, "orb": [], "next": "5",
         "correction": {"sent": {"text": ss.CORRECTION_4}, "body": {"readback": "Got it: Europe."}}}]}]
    md = "\n".join(report.beats_markdown(told))
    assert "## The beats (spec 158)" in md and "### the long telling -- `12345678`" in md
    assert "| 3 | How do they do it today" in md and "1600 chars" in md and "A; B" in md
    assert "speaking > listening > hearing > writing > speaking" in md
    assert f"then *{ss.CORRECTION_4}*: Got it: Europe." in md
    assert report.beats_markdown(None) == []


def test_the_stored_words_read_refuses_what_is_not_an_id():
    with pytest.raises(ledger.LedgerUnavailable):
        ledger.story_turns(CONFIG, "not-a-project")


def test_the_founder_legs_are_158s():
    assert [leg for leg, _ in tv.FOUNDER_LEGS] == ["FR-1a", "FR-1b", "FR-1c", "FR-1d"]
    assert [key for key, _, _ in tv.FR1A_TOLD] == ["a-script", "a-long"]


# ------------------------------------------------------------------------------------------- the subjects' mirror

def test_contract_83_is_the_one_the_walk_reads():
    text = _need(CLOUD / "canon" / "openapi-v2.yaml").read_bytes()
    if b"costDrafted" not in text:
        pytest.skip("keel-cloud before 263")
    for route in ("/v2/projects/{projectId}/story/turns/{n}", "/v2/projects/{projectId}/story/turns/{n}/draft",
                  "/v2/projects/{projectId}/story/confirm", "/v2/projects/{projectId}/idea/turns/{n}"):
        assert f"  {route}:".encode() in text, route
    for field in (b"costDrafted", b"correction", b"offerName", b"maxLength: 20000"):
        assert field in text, field
    digest = hashlib.sha256(text).hexdigest()
    if digest != CONTRACT_83:
        pytest.skip(f"keel-cloud's contract moved past 83 ({digest[:12]}): re-cut this pin")
    assert digest == CONTRACT_83


def test_the_five_questions_are_keel_clouds_and_keel_webs():
    turns = _need(CLOUD / "src" / "main" / "java" / "com" / "keeldiscovery" / "cloud" / "domain" / "story"
                  / "StoryTurns.java").read_text(encoding="utf-8")
    lines = _need(WEB / "src" / "lib" / "storyLines.ts").read_text(encoding="utf-8")
    for n, question in ss.STORY_QUESTIONS.items():
        assert f'"{question}"' in turns, (n, question)            # spec 161: keel-cloud 268's seven
    for n, question in (ss.STORY_QUESTIONS if ss.web_has_257(WEB) else ss.STORY_QUESTIONS_263).items():
        assert f'"{question}"' in lines, (n, question)            # keel-web 257's seven, 245's five before it


def test_keel_webs_silence_hook_is_in_the_test_build():
    flow = _need(WEB / "src" / "components" / "story" / "StoryFlow.tsx").read_text(encoding="utf-8")
    assert "window.__keelSilence = hook" in flow and 'import.meta.env.MODE !== "test"' in flow
    conversation = (WEB / "src" / "lib" / "story" / "conversation.ts").read_text(encoding="utf-8")
    assert "SILENCE_MS = 4_000" in conversation


def test_the_fake_colours_hold_the_one_said():
    fake = _need(CLOUD / "src" / "main" / "java" / "com" / "keeldiscovery" / "cloud" / "application" / "story"
                 / "FakeStoryReadings.java").read_text(encoding="utf-8")
    if (CLOUD / "src/main/java/com/keeldiscovery/cloud/domain/story/IdeaTurns.java").exists() and \
            "TAGLINE_MAX_WORDS" in (CLOUD / "src/main/java/com/keeldiscovery/cloud/domain/story/IdeaTurns.java").read_text():
        # spec 162 (keel-cloud 271 FR-2): the brand is typed -- no colour is said, the fake's colour table is gone
        assert f'"{ss.SAID_COLOUR[0]}", "{ss.SAID_COLOUR[1]}"' not in fake
    else:
        assert f'"{ss.SAID_COLOUR[0]}", "{ss.SAID_COLOUR[1]}"' in fake
