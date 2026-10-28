"""Spec 075 FR-5: the harness follows keel-cloud 144 and keel-web 126 -- *One more thing.* in every FOLLOW_UP clip and the
one kicker on the page; contract 42's `POST /v2/projects/{id}/interviewer/transcribe` (Try it yourself writes the hello,
the story and the follow-up down as a link does); the text box's `asking` state and the microphone kept between takes.

Zero spend: the judges offline, the words and the route held to the product checkouts `stack.toml` names, the seam's
held permission sheet and the box's asking card read in a real page.
"""

from __future__ import annotations

import inspect
import re

import pytest

from evals import corpus_scenario as cs
from evals import interviewer_leg as leg
from evals import interviewer_marks as marks
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import vectors_screens as vs_screens
from stack.config import load_config

CONFIG = load_config(validate=False)
GATE = "g-try"


def _cloud(rel: str) -> str:
    path = CONFIG.keel_cloud / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    return path.read_text(encoding="utf-8")


def _web(rel: str) -> str:
    path = CONFIG.keel_web / rel
    if not path.is_file():
        pytest.skip(f"keel-web has no {rel}")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------ (a) One more thing

def test_every_follow_up_clip_opens_on_one_more_thing():
    passages = _cloud("src/main/java/com/keeldiscovery/cloud/application/interviewer/PassageComposer.java")
    assert 'ONE_MORE_THING = "One more thing. "' in passages and "ONE_LAST_THING =" not in passages
    assert fake.ONE_MORE_THING == "One more thing." and fake.RETIRED_LEAD_IN == "One last thing."
    for rung in fake.LADDER:
        script = fake.follow_up_script(rung[3])
        assert script.startswith("One more thing. ") and not script.startswith(fake.RETIRED_LEAD_IN), script


def test_the_leg_holds_the_clips_to_the_new_lead_in():
    clips = inspect.getsource(leg._follow_up_clips)
    assert "fake.ONE_MORE_THING" in clips and "One last thing" not in clips
    assert "One last thing" not in inspect.getsource(marks.the_follow_up_clips).split('"""')[-1]


def test_one_kicker_on_the_spot_and_at_the_end():
    asked = [{"dimension": "solution.relative_advantage", "on": "solution.relative_advantage"},
             {"dimension": "commercial.commitment", "on": None}]
    assert {marks._kicker(a) for a in asked} == {"One more thing"} == {ivs.FOLLOW_UP_KICKER}
    ai = inspect.getsource(leg._follow_up_on_the_ai_link)
    assert "FOLLOW_UP_SPOT_KICKER" not in ai and "kicker = ivs.FOLLOW_UP_KICKER" in ai
    end = inspect.getsource(vs_screens.Interview._end_follow_ups)
    assert "rung == last" in end and "FOLLOW_UP_SPOT_KICKER" not in end


def test_the_answers_line_reads_one_more_thing():
    assert cs.follow_up_line("Relative advantage", "Fewer emails.") == \
        "One more thing · Relative advantage: “Fewer emails.”"
    text = _web("src/lib/translate.ts")
    assert "export const followUpLine = (rung: string, text: string): string => `${FOLLOW_UP_KICKER} · ${rung}: " \
           "“${text}”`;" in text


# --------------------------------------------------------------------- (b) contract 42: the dry run's transcribe

def test_contract_42_names_the_dry_runs_transcribe():
    spec = _cloud("canon/openapi-v2.yaml")
    # spec 076: contract 43 (keel-cloud 145) keeps the route as 42 wrote it -- held at 42 or later
    assert int(re.search(r"x-keel-contract: (\d+)", spec).group(1)) >= 42
    block = spec.split("  /v2/projects/{projectId}/interviewer/transcribe:")[1].split("\n  /v2/")[0]
    assert "operationId: transcribeTryAnswer" in block and "TranscribeRequest" in block and "Transcript" in block
    web = _web("src/api/interview.ts")
    assert "/interviewer/transcribe" in web


def _drawn(**over) -> dict:
    drawn = {"transcribed": [{"itemId": "i-1", "maxSeconds": None, "status": 200, "text": "hello"},
                             {"itemId": GATE, "maxSeconds": None, "status": 200, "text": leg.DRY_RUN_STORY}],
             "answered": [{"url": "/v2/projects/p/interviewer/answer", "heard": "yes"}],
             "story": {"reached": True, "hold": {"status": ivs.HELD, "heard": leg.DRY_RUN_STORY},
                       "statuses": [{"status": ivs.STORY}, {"status": ivs.HELD}], "sheet_text": leg.DRY_RUN_STORY}}
    drawn.update(over)
    return drawn


def test_the_dry_run_writes_the_story_down():
    assert leg.dry_run_written_down(_drawn(), GATE, leg.DRY_RUN_STORY) == []


@pytest.mark.parametrize("over, fault", [
    ({"transcribed": [{"itemId": GATE, "status": 200, "text": leg.DRY_RUN_STORY}]}, "hello was not written down"),
    ({"answered": [{"url": "/x/interviewer/answer", "heard": "hello"}]}, "workaround"),
    ({"transcribed": [{"itemId": "i-1", "status": 200, "text": "hello"}]}, "not written down once"),
    ({"transcribed": [{"itemId": "i-1", "status": 200, "text": "hello"},
                      {"itemId": GATE, "status": 200, "text": ""}]}, "written down as"),
    ({"transcribed": [{"itemId": "i-1", "status": 200, "text": "hello"},
                      {"itemId": GATE, "status": 200, "text": leg.DRY_RUN_STORY, "maxSeconds": 120}]}, "maxSeconds"),
    ({"story": {"reached": False}}, "never reached"),
    ({"story": {"reached": True, "hold": {"status": "Recording your answer."}, "statuses": []}}, "not held"),
    ({"story": {"reached": True, "hold": {"status": ivs.HELD}, "statuses": [{"status": ivs.AI_REASON_NO_MATCH}]}},
     "a miss"),
    ({"story": {"reached": True, "hold": {"status": ivs.HELD}, "statuses": [],
                "sheet_text": ivs.AI_REASON_DIDNT_CATCH}}, "a miss"),
    ({"story": {"reached": True, "hold": {"status": ivs.HELD, "heard": "x not taken"}, "statuses": []}}, "a miss"),
])
def test_the_dry_runs_story_faults_are_named(over, fault):
    faults = leg.dry_run_written_down(_drawn(**over), GATE, leg.DRY_RUN_STORY)
    assert any(fault in f for f in faults), faults


def test_the_wire_check_asks_the_route_as_the_link_is_asked():
    source = inspect.getsource(leg._dry_run_transcribe)
    assert 'j.project("/interviewer/transcribe")' in source
    for want in ('"ITEM_NOT_ON_FORM"', '"SHAPE_MISMATCH"', "post(follow_id, line, 120)", "post(gate_id, story, 90)",
                 "post(link_gate, story)", "before == after"):
        assert want in source, want
    assert "_dry_run_transcribe(j, wire, record, interview)" in inspect.getsource(leg._ai_link)
    # the recording the route hears: the words' UTF-8, zero-padded to 20 KiB (the seam's own shape)
    import base64                                                              # noqa: PLC0415
    raw = base64.b64decode(leg._said_audio("hello"))
    assert len(raw) == 20 * 1024 and raw.rstrip(b"\x00") == b"hello"
    assert ivs.decode_said(leg._said_audio(leg.DRY_RUN_STORY)) == leg.DRY_RUN_STORY


def test_the_stack_serves_the_founders_route_with_the_same_fake():
    from stack import cloud                                                    # noqa: PLC0415
    source = inspect.getsource(cloud)
    assert '"KEEL_INTERVIEWER_TRANSCRIBER": "fake"' in source and '"KEEL_OPENAI_API_KEY": ""' in source


# ------------------------------------------------------------------- (c) keel-web 126 FR-4: asking, the mic kept

def test_the_held_permission_sheet_is_keel_webs():
    fixture = _web("tests/fixtures/interviewer/fakeSpeech.ts")
    assert "w.__micHeld" in fixture and "w.__grantMic = resolve" in fixture
    held = ivs.text_seam(held=True)
    assert "window.__micHeld = true;" in held and "window.__grantMic = resolve" in held
    assert "window.__micHeld = true;" not in ivs.text_seam() and "window.__micHeld = true;" not in ivs.SPEECH_SEAM
    text = _web("src/lib/translate.ts")
    assert re.search(r'export const SPEAK_ASKING = "([^"]*)";', text).group(1) == ivs.SPEAK_ASKING == \
        marks.SPEAK_ASKING
    box = _web("src/components/interview/SpeakOrTypeBox.tsx")
    assert 'data-testid="iv-mic-asking"' in box and '<span data-testid="iv-mic-say">{SPEAK_ASKING}</span>' in box
    sot = _web("src/lib/speakOrType.ts")
    assert '"idle" | "asking" | "listening"' in sot


ASKING = """
<main><div class="sot" data-state="asking"><textarea aria-label="Your answer" aria-hidden="true"></textarea>
  <div class="sot__listening sot__asking" data-testid="iv-mic-asking" role="status">
    <p class="sot__say"><span data-testid="iv-mic-say">Allow the microphone…</span></p>
    <div class="sot__row"><button type="button" class="btn" data-testid="iv-mic-cancel">Cancel</button></div>
  </div><div class="sot__bar"><span>A few lines is plenty.</span></div></div></main>
"""


def test_the_seam_holds_the_sheet_and_the_box_reads_asking():
    from playwright.sync_api import sync_playwright                          # noqa: PLC0415

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.add_init_script(ivs.text_seam(held=True))
            page.goto("about:blank")
            page.set_content(ASKING)
            page.evaluate("() => { window.__asked = window.__keelSpeech.mic.acquire().then((ok) => "
                          "{ window.__granted = ok; }); }")
            page.wait_for_timeout(200)
            box = ivs.SpeakBox(page, "main")
            assert page.evaluate("() => window.__granted === undefined")           # the sheet is still up
            read = box.read()
            assert (read["state"], read["asking"], read["cancel"], read["wave"], read["clock"], read["done"]) == \
                ("asking", ivs.SPEAK_ASKING, True, False, None, False)
            assert box.counts()["acquired"] == 1 and not box.counts()["starts"]
            box.grant()
            page.wait_for_function("() => window.__granted === true", timeout=2_000)
            # granted once: a later take's acquire is not held again
            assert page.evaluate("async () => await window.__keelSpeech.mic.acquire()") is True
        finally:
            browser.close()


def _take(**over) -> dict:
    v = {"before_pill": {"acquired": 0, "starts": [], "released": 1},
         "asking": {"state": "asking", "asking": ivs.SPEAK_ASKING, "cancel": True, "wave": False, "clock": None,
                    "done": False},
         "asking_counts": {"acquired": 1, "starts": []}, "continue_enabled_asking": False,
         "counts": {"released": 1}, "released_at_done": 2}
    v.update(over)
    return v


def test_im26_reads_asking_and_the_microphone_kept():
    assert marks._asking_ok(_take()) and marks._kept_ok(_take())
    assert not marks._asking_ok(_take(asking={"state": "listening"}))
    assert not marks._asking_ok(_take(asking_counts={"acquired": 1, "starts": [3.0]}))
    assert not marks._kept_ok(_take(counts={"released": 2}))                   # the take let it go (before 126)
    assert not marks._kept_ok(_take(released_at_done=1))                       # never let go on done
    walk = inspect.getsource(vs_screens.Interview._speak_story)
    assert walk.index('box.wait_state("asking")') < walk.index("box.grant()") < walk.index('box.wait_state("listening")')
    assert 'held=speak in ("quiet", "done")' in inspect.getsource(cs)
