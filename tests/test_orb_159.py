"""Spec 159: the orb, walked -- the harness's machinery with no stack (the orb's collector read off a drawn page in a
headless Chromium, the wire's clip routes, the same-words key, the never-drawn read, the orb's ledger rule, the report's
*The orb*) and the mirror of the subjects: keel-cloud 267 (contract 84: `speaker`, the cards' `clipId` gone,
`KeelVoice.key`, `InferenceCharge` 20 and `CARD_SPEECH` at 0) and keel-web 253 (the one player, the orb's intro, the film
first, *Keel's voice*), read from the sibling checkouts the stack runs."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest
import yaml

from evals import three_views as tv
from evals import three_views_report as report
from evals import three_views_strangers as strangers
from harness import interview_charge as charge
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import story_screens as ss
from stack.config import load_config

CONFIG = load_config(validate=False)
CLOUD = Path(CONFIG.keel_cloud)
WEB = Path(CONFIG.keel_web)

#: keel-cloud 267 tasks.md (T5, unchanged at master `8bd57d6f`): sha256 of `canon/openapi-v2.yaml` at contract 84.
CONTRACT_84 = "1002eb90dafc9f2c83c2decc401b1c51c7df91bec1e9ac2443e615ad8b5b0b5b"
#: The schemas whose `clipId` contract 84 removed (keel-cloud 267 FR-4).
CARDS_WITHOUT_CLIP = ("GateItem", "InterviewItem", "FollowUp", "ProblemCheck")


def _need(path: Path) -> Path:
    if not path.exists():
        pytest.skip(f"{path} is not in the sibling checkout")
    return path


def _cloud_java(*parts: str) -> str:
    return _need(CLOUD.joinpath("src", "main", "java", "com", "keeldiscovery", "cloud", *parts)).read_text(
        encoding="utf-8")


# ------------------------------------------------------------------------------------------- the machinery

def test_the_views_are_the_orb_the_face_and_the_copilot():
    assert tv.VIEWS == ("orb", "avatar", "copilot")
    assert [leg for leg, _ in tv.STRANGER_LEGS][:3] == ["FR-2 problem · orb", "FR-2 problem · avatar",
                                                         "FR-2 problem · copilot"]


def test_the_speech_key_is_keel_voices():
    """`KeelVoice.key`: sha256 of the voice, a newline, the words with whitespace runs as one space and the ends
    stripped -- the same words keyed alike however they were spaced."""
    want = hashlib.sha256("nova\nHello there. Now the idea.".encode()).hexdigest()
    assert ss.speech_key("nova", "Hello there. Now the idea.") == want
    assert ss.speech_key("nova", "  Hello  there.\n\tNow the idea. ") == want
    assert ss.speech_key("alloy", "Hello there. Now the idea.") != want


def _player(route: str) -> dict:
    ref = lambda i: {"clipId": f"c{i}", "url": f"{route}c{i}", "seconds": 0.312}   # noqa: E731
    return {"speaker": "ORB", "face": None, "clips": {"opening": ref(1), "problem": None, "pilot": ref(2),
                                                      "followUp": {"r1": ref(3)}},
            "items": {"i1": {"clip": ref(4), "more": None}, "i2": {"clip": ref(5), "more": ref(6), "under": ref(7)}}}


def test_clip_refs_name_every_clip_where_it_sits():
    refs = ss.clip_refs(_player("/v2/clips/"))
    assert [w for w, _ in refs] == ["clips.opening", "clips.pilot", "clips.followUp.r1", "items.i1.clip",
                                    "items.i2.clip", "items.i2.more", "items.i2.under"]
    assert ss.clip_refs(None) == []


def test_a_card_carrying_a_clip_is_named():
    contract_84 = {"gate": {"itemId": "g", "condition": {"question": "Q?"}}, "problemCheck": {"question": "Does?"},
                   "parts": [{"items": [{"itemId": "i1", "dimension": "problem.frequency"}]}]}
    assert ss.cards_carrying_a_clip(contract_84) == []
    contract_83 = {"gate": {"itemId": "g", "clipId": "x", "condition": {"question": "Q?", "clipId": "y"}},
                   "parts": [{"items": [{"itemId": "i1", "dimension": "problem.frequency", "clipId": "z"}]}]}
    assert ss.cards_carrying_a_clip(contract_83) == ["gate", "gate.condition", "item problem.frequency"]


def _log(*rows: dict) -> list[dict]:
    base = {"state": None, "phase": None, "onStage": True, "speaker": "ORB", "film": None, "typed": [], "voiceBar": 0,
            "choice": 0, "readTap": False, "video": 0, "question": None, "where": None}
    return [{**base, **r} for r in rows]


def test_the_stage_reads_the_film_first_then_the_opening():
    log = _log({"onStage": False, "phase": "idle"}, {"phase": "story", "film": "problem", "state": "dim"},
               {"phase": "speaking", "state": "speaking"}, {"phase": "listening", "state": "listening"},
               {"phase": "listening", "state": "hearing"}, {"phase": "listening", "state": "writing"},
               {"phase": "held", "state": "paused"}, {"phase": "speaking", "state": "speaking"})
    assert ss.stage_sequence(log) == ["film:problem", "speaking", "listening", "held", "speaking"]
    runs = ss.orb_answer_runs(log)
    assert runs == [["dim"], ["speaking", "listening", "hearing", "writing", "paused"], ["speaking"]]
    assert ss.holds_in_order(runs[1], ["speaking", "listening", "hearing", "writing"])


def test_never_drawn_names_a_typed_box_and_the_old_chrome():
    clean = ss.never_drawn(_log({"phase": "listening"}))
    assert clean == {"typed": [], "voice_bar": False, "choice": False, "read_and_tap": False, "video": False}
    dirty = ss.never_drawn(_log({"phase": "typing", "typed": ["ai-typed"], "question": "Tell me"},
                                {"phase": "typing", "typed": ["ai-typed"], "question": "Tell me"},
                                {"voiceBar": 1, "readTap": True, "video": 1}))
    assert dirty["typed"] == [{"typed": ["ai-typed"], "where": None, "question": "Tell me", "phase": "typing"}]
    assert dirty["voice_bar"] and dirty["read_and_tap"] and dirty["video"] and not dirty["choice"]


def test_the_refused_seam_refuses_the_microphone():
    """Spec 160 FR-2: the refusal is `window.__micRefused` (keel-web's fixture's own name), so the walk can allow the
    microphone again (`Player.allow_mic`)."""
    refused = ivs.speech_seam(refused=True)
    assert "window.__micRefused = true;" in refused and "return !refused && !window.__micRefused;" in refused
    assert ivs.speech_seam() == ivs.SPEECH_SEAM and "mic(() => 0.12, false)" in ivs.SPEECH_SEAM
    assert "__micRefused = true" not in ivs.SPEECH_SEAM


def test_the_orbs_clips_buy_nothing():
    def row(action, credits, key="k"):
        return {"action": action, "credits": credits, "price_credits": 0 if action == "CARD_SPEECH" else -credits,
                "idempotency_key": key}
    assert charge.orb_charge_faults([row("CARD_SPEECH", 0), row("PROJECT", -2000), row("INTERVIEWER_RECORDING", -1500),
                                     row("TURN", 0)]) == []
    assert charge.orb_charge_faults([row("CARD_SPEECH", -3, "speech:x")]) == [
        "CARD_SPEECH row speech:x: credits -3, price 0, not 0", "a charge that is not bought: CARD_SPEECH -3 (speech:x)"]
    assert charge.orb_charge_faults([row("TURN", -1, "t")]) == ["a charge that is not bought: TURN -1 (t)"]


def test_the_walk_finds_the_item_a_sheet_asks():
    items = [{"text": "How often does it happen?", "control": "segmented_0_to_7"},
             {"text": "Which of these comes closest?", "control": "fixed_four"}]
    assert strangers.item_of(items, "Which of these comes closest?")["control"] == "fixed_four"
    assert strangers.item_of(items, "Something else") == {}
    assert strangers._option_index(["Yes", "No"], "no", 0) == 1
    assert strangers._option_index(["Maybe"], "no", 1) == 1
    assert strangers.person_at(["Ann", "Bo"], 1) == "Bo" and strangers.person_at(["Ann", "Bo"], 3) == "Bo 3"


def test_the_ways_are_taken_by_the_items_that_can_take_them():
    """159 FR-3: the letter and the tap on a one-pick item; the words on any item with rows but the price ladder."""
    ways = list(strangers.SPEAK_OR_TAP)
    assert strangers.way_for(ways, "pick_one_then_one") == "words"
    assert strangers.way_for(ways, "fixed_four") == "letter"
    assert strangers.way_for(ways, "price_ladder") is None and strangers.way_for(ways, None) is None
    assert strangers.way_for(["tap"], "fixed_four") == "tap" and strangers.way_for([], "fixed_four") is None
    assert strangers.way_for(["tap"], "pick_one_then_one") is None       # its tap goes straight to the second ask


def test_the_report_names_the_orb():
    orbs = [{"study": "problem", "link": "voice", "stage": ["film:problem", "speaking", "listening"],
             "orb": ["speaking > listening > hearing > writing"], "answers": [("Which comes closest?", "B", ["BOne"])],
             "films": [("problem", True, None)], "never": ss.never_drawn(_log({})),
             "response": {"status": 201, "format": "TEXT", "anchorChip": None, "answers": 6}, "done": "Thank you"}]
    md = report.report_markdown([], {"cloud": "c", "web": "w"}, report.log_scan(""), orbs=orbs)
    # spec 160 FR-8: *The orb* became *The two speakers*; the links walked are kept under it
    assert "## The two speakers (spec 160, keel-web 256 on keel-cloud 267; under the three surfaces since spec 161)" in md and "### The links walked" in md
    assert "| problem | voice | film:problem > speaking > listening |" in md
    assert "201 TEXT  (6 answers)" in md and "-> held `['BOne']`" in md


# ------------------------------------------------------------------------------------------- the collector, drawn

_PAGE = """<main>
  <div data-testid="ai-intro" data-speaker="ORB"><span data-testid="intro-orb">
    <span data-testid="story-orb" data-state="paused"></span></span></div>
  <div data-testid="ai-stage" data-phase="idle" data-speaker="ORB" hidden>
    <div data-testid="ai-orb" data-state="paused"><span data-testid="story-orb" data-state="paused"></span></div>
    <span data-testid="ai-where"></span>
  </div>
</main>"""


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright    # noqa: PLC0415
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as missing:  # noqa: BLE001 - no browser on this machine
            pytest.skip(f"no Chromium: {missing}")
        ctx = b.new_context()
        ctx.add_init_script(ss.ORB_INTERVIEW_WATCH)
        pg = ctx.new_page()
        yield pg
        b.close()


def test_the_collector_logs_the_film_the_orb_and_a_typed_box(page):
    page.set_content(_PAGE)
    page.evaluate("""() => { const s = document.querySelector('[data-testid=ai-stage]');
      document.querySelector('[data-testid=ai-intro]').remove(); s.removeAttribute('hidden');
      s.setAttribute('data-phase', 'story');
      s.insertAdjacentHTML('beforeend', '<div data-testid="ai-story" data-kind="problem" data-first=""></div>'); }""")
    page.wait_for_timeout(50)
    page.evaluate("""() => { document.querySelector('[data-testid=ai-story]').remove();
      const s = document.querySelector('[data-testid=ai-stage]'); s.setAttribute('data-phase', 'speaking');
      document.querySelector('[data-testid=ai-orb]').setAttribute('data-state', 'speaking'); }""")
    page.wait_for_timeout(50)
    page.evaluate("""() => { const s = document.querySelector('[data-testid=ai-stage]');
      s.setAttribute('data-phase', 'listening');
      document.querySelector('[data-testid=ai-orb]').setAttribute('data-state', 'listening');
      s.insertAdjacentHTML('beforeend', '<main data-testid="ai-sheet"><p class="iv-q">Tell me about it</p>'
        + '<textarea data-testid="ai-typed"></textarea></main>'); }""")
    page.wait_for_timeout(50)
    log = ss.iv_log(page)
    assert any(r["intro"] == "ORB" and not r["onStage"] for r in log)
    assert ss.stage_sequence(log) == ["film:problem", "speaking", "listening"]
    film = next(r for r in log if r.get("film"))
    assert film["first"] is True and film["hand"] is None
    assert ss.orb_sequence([r for r in log if r.get("state")]) == ["paused", "speaking", "listening"]
    assert ss.never_drawn(log)["typed"] == [{"typed": ["ai-typed"], "where": "", "question": "Tell me about it",
                                             "phase": "listening"}]


# ------------------------------------------------------------------------------------------- the subjects' mirror

def _contract() -> tuple[bytes, dict]:
    text = _need(CLOUD / "canon" / "openapi-v2.yaml").read_bytes()
    return text, yaml.safe_load(text)


def test_contract_84_is_the_one_the_walk_reads():
    text, doc = _contract()
    if doc["info"].get("x-keel-contract", 0) < 84:
        pytest.skip("keel-cloud before 267")
    schemas = doc["components"]["schemas"]
    player = schemas["InterviewerPlayer"]
    assert player["properties"]["speaker"]["enum"] == [ivs.SPEAKER_ORB, ivs.SPEAKER_AVATAR]
    assert {"speaker", "face"} <= set(player["required"])
    assert list(schemas["ClipRef"]["properties"]) == ["clipId", "url", "seconds"]
    for name in CARDS_WITHOUT_CLIP:
        assert "clipId" not in (schemas[name].get("properties") or {}), name
    digest = hashlib.sha256(text).hexdigest()
    if digest != CONTRACT_84:
        pytest.skip(f"keel-cloud's contract moved past 84 ({digest[:12]}): re-cut this pin")
    assert doc["info"]["x-keel-contract"] == 84


def test_keel_voice_keys_as_the_walk_keys():
    voice = _cloud_java("application", "KeelVoice.java")
    assert 'text.strip().replaceAll("\\\\s+", " ")' in voice
    assert 'sha.digest((voice + "\\n" + spoken(text)).getBytes(StandardCharsets.UTF_8))' in voice
    migration = _need(CLOUD / "src" / "main" / "resources" / "db" / "migration" / "V55__speech_clip.sql")
    assert "cache_key        text        NOT NULL UNIQUE" in migration.read_text(encoding="utf-8")


def test_the_player_names_its_two_speakers():
    player = _cloud_java("application", "interviewer", "InterviewerPlayer.java")
    if "ORB" not in player:
        pytest.skip("keel-cloud before 267")
    assert f'public static final String ORB = "{ivs.SPEAKER_ORB}";' in player
    assert f'public static final String AVATAR = "{ivs.SPEAKER_AVATAR}";' in player
    fake = _cloud_java("infrastructure", "interviewer", "FakeSpeech.java")
    assert 'SILENCE = "keel/speech/silent-300ms.mp3"' in fake


def test_the_charge_table_is_20_with_card_speech_at_0():
    table = next(CLOUD.joinpath("src", "main", "java").rglob("InferenceCharge.java"), None)
    if table is None:
        pytest.skip("no InferenceCharge in the checkout")
    text = table.read_text(encoding="utf-8")
    # spec 161 FR-11 (keel-cloud 270 FR-3): 21 -- EXPERIENCE_WAYS added at 0; CARD_SPEECH still 0 (267's 20 before it)
    version = int(re.search(r"public static final int VERSION = (\d+);", text).group(1))
    # spec 162 FR-10 (keel-cloud 273): 22 -- STORY_PICTURES and PICTURE_REVIEW added at 0; CARD_SPEECH still 0
    assert version in (charge.PRICE_VERSION_267, charge.PRICE_VERSION_270, charge.PRICE_VERSION_273)
    assert re.search(r"CARD_SPEECH\s*\(\s*0,", text)


def test_the_fake_classifier_reads_a_letter():
    """keel-cloud 266: *B* said is the second row on the fakes (the walk's letter)."""
    fake = _cloud_java("infrastructure", "interviewer", "FakeClassifier.java")
    assert "Spec 266" in fake and "letter" in fake


def test_keel_web_plays_the_orb():
    _need(WEB / ss.ORB_PLAYER_SOURCE)
    assert ss.web_has_orb(WEB)
    intro = (WEB / "src" / "components" / "interview" / "ai" / "AiIntro.tsx").read_text(encoding="utf-8")
    assert 'data-speaker={face ? "AVATAR" : "ORB"}' in intro and f'data-testid="{ivs.INTRO_ORB}"' in intro
    player = (WEB / ss.ORB_PLAYER_SOURCE).read_text(encoding="utf-8")
    for testid in (ivs.STAGE_ORB, ivs.STAGE_ORB_STATE):
        assert f'data-testid="{testid}"' in player, testid
    # spec 160 (keel-web 256 FR-3): the film's dim orb is gone
    assert f'data-testid="{ivs.FILM_ORB}"' not in player
    flow = (WEB / "src" / "lib" / "aiInterviewFlow.ts").read_text(encoding="utf-8")
    # spec 164 mirror 1 (keel-web 258 FR-2b): the film-first order is retired -- the opening, the screener on a step of
    # its own, then the film, then the gate; no problem passage on a film link
    assert '...(film ? [{ kind: "film" } as const] : [])' not in flow
    screener = flow.find('steps.push({ kind: "condition", condition: screener')
    assert 0 <= screener < flow.find('steps.push({ kind: "film" });')
    assert "if (!film) passage(\"problem\");" in flow
    orb = (WEB / "src" / "components" / "voice" / "KeelOrb.tsx").read_text(encoding="utf-8")
    assert 'data-testid="story-orb"' in orb


def test_the_orbs_words_are_keel_webs():
    translate = _need(WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    if "ORB_INTERVIEWER" not in translate:
        pytest.skip("keel-web before 253")
    assert 'ORB_INTERVIEWER = { name: "Keel AI", subject: "It", object: "it", isAre: "is" }' in translate
    # spec 160 (keel-web 256 FR-1): the intro names the orb *Keel* (`ORB_INTRO_NAME`) in `aiIntroSpoken`
    assert f'ORB_INTRO_NAME = "{ivs.ORB_NAME}"' in translate and ivs.ORB_STAGE_NAME == "Keel AI"
    assert ivs.ORB_NOT_A_PERSON == "A spoken interview with Keel, an AI interviewer, not a person."
    assert f'AI_STAGE_LABEL_ORB = "{ivs.ORB_STAGE_LABEL}"' in translate
    assert f'TEXT_FORMAT_NAME = "{iv.KEELS_VOICE}"' in translate
    assert f'"{ivs.RECORDING_MEANWHILE}"' in translate and f'"{ivs.KEELS_VOICE_LINE}"' in translate
    assert iv.FORMAT_NAMES == {"TEXT": iv.KEELS_VOICE, "AI_INTERVIEWER": "AI interviewer"}


def test_the_popup_offers_two_rows():
    popup = _need(WEB / "src" / "components" / "interviews" / "NewLinkPopup.tsx").read_text(encoding="utf-8")
    assert 'const FORMATS: InterviewFormat[] = ["TEXT", "AI_INTERVIEWER"];' in popup
    sent = (WEB / "src" / "components" / "interviews" / "SentPage.tsx").read_text(encoding="utf-8")
    assert f'data-testid="{ivs.TRY_KEEL_VOICE}"' in sent


def test_the_response_names_the_served_format():
    flow = _need(WEB / "src" / "lib" / "aiInterviewFlow.ts").read_text(encoding="utf-8")
    assert 'return formats.includes("AI_INTERVIEWER") ? "AI_INTERVIEWER" : "TEXT";' in flow
