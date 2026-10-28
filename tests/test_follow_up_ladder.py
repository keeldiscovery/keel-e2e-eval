"""Spec 051 (keel-cloud 103, keel-web 076, contract 19's interview side): the harness's LADDER copy -- the independent
check of the cloud's walk -- held to the registry export the stack runs; `first_rung` against a hand-worked table (one
case a rung, the escape, the chip, the commercial link, the lock's rule, nothing owed); `fill` against
`FollowUpComposer`'s own defaults and words; the fake's FOLLOW_UP lines; keel-web 076's words, caps and seam as the walk
reads them; the corpus people's follow-up lines; the two new ledger reads refused on the remote profile."""

from __future__ import annotations

import json
import re
import uuid

import pytest

from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import vectors_script as vs
from stack import ledger
from stack.config import load_config

CONFIG = load_config(validate=False)


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


def _registry() -> dict:
    text = _cloud("src/main/resources/keel/dimension-registry.json")
    registry = json.loads(text)
    if not any(e.get("follow_up") for e in registry["dimensions"]):
        pytest.skip("keel-cloud predates spec 103 (no follow_up blocks)")
    return registry


# ------------------------------------------------------------------------------------- the copy, held

def test_the_ladder_is_the_registrys_own():
    """Every rung, in the registry's order (vector, then `order`), with its `against` set (or `lock_rule`), its text
    and its spoken wording, exactly; the five without a block are NO_FOLLOW_UP."""
    registry = _registry()
    vectors = ("PROBLEM", "SOLUTION", "COMMERCIAL")
    entries = sorted(registry["dimensions"], key=lambda e: (vectors.index(e["vector"]), e["order"]))
    theirs = [(e["key"], e["follow_up"]["against"] if e["follow_up"]["against"] == fake.LOCK_RULE
               else tuple(e["follow_up"]["against"]), e["follow_up"]["text"], e["follow_up"]["spoken"])
              for e in entries if e.get("follow_up")]
    assert list(fake.LADDER) == theirs
    assert tuple(e["key"] for e in entries if not e.get("follow_up")) == fake.NO_FOLLOW_UP
    checks = registry.get("checks", {}).get("9_follow_up") or {}
    assert tuple(checks.get("rungs") or ()) == fake.RUNGS and tuple(checks.get("without") or ()) == fake.NO_FOLLOW_UP
    assert sorted(checks.get("lock_rule") or ()) == sorted(r[0] for r in fake.LADDER if r[1] == fake.LOCK_RULE)


def test_each_texts_placeholders_are_the_registrys_and_fill_knows_them():
    for e in _registry()["dimensions"]:
        block = e.get("follow_up")
        if block:
            assert re.findall(r"\{[a-z_]+\}", block["text"]) == block["placeholders"], e["key"]
            assert all(p in fake.FILL_DEFAULTS for p in block["placeholders"]), e["key"]
            assert not re.search(r"[{}]", block["spoken"]), e["key"]


def test_the_composers_defaults_and_its_one_more_thing():
    composer = _cloud("src/main/java/com/keeldiscovery/cloud/application/FollowUpComposer.java")
    defaults = re.search(r"DEFAULTS = Map\.of\((.*?)\);", composer, re.S)
    pairs = dict(re.findall(r'"(\{[a-z_]+\})",\s*"([^"]*)"', defaults.group(1) if defaults else ""))
    assert pairs == fake.FILL_DEFAULTS
    assert f'WOULD_NOT_PAY_BAND = "{fake.WOULD_NOT_PAY_BAND}"' in composer
    passages = _cloud("src/main/java/com/keeldiscovery/cloud/application/interviewer/PassageComposer.java")
    # keel-cloud 144 FR-2 (spec 075 FR-5): the lead-in is *One more thing.*; *One last thing.* is the retired one
    assert f'ONE_MORE_THING = "{fake.ONE_MORE_THING} "' in passages
    assert "ONE_LAST_THING =" not in passages and fake.RETIRED_LEAD_IN == "One last thing."
    price = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/PriceLadder.java")
    points = re.search(r"POINTS = List\.of\(([^)]*)\)", price, re.S)
    assert points and tuple(int(x.replace("_", "")) for x in re.findall(r"[\d_]+", points.group(1))) == \
        fake.PRICE_POINTS
    compare = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/Compare.java")
    assert f'BUYER_DECIDED_ALONE = "{fake.BUYER_ALONE}"' in compare


def test_the_buyer_answers_and_supports_are_the_registrys():
    entry = next(e for e in _registry()["dimensions"] if e["key"] == "commercial.buyer_payer_alignment")
    assert tuple(a["code"] for a in entry["respondent"]["fixed_answers"]) == fake.BUYER_ANSWERS
    assert tuple(entry["respondent"]["supports"]) == fake.BUYER_SUPPORTS


def test_the_consent_line_is_the_composers_own():
    from evals.corpus_scenario import CONSENT_GONE, CONSENT_TEXT        # noqa: PLC0415

    composer = _cloud("src/main/java/com/keeldiscovery/cloud/application/InterviewComposer.java")
    m = re.search(r'CONSENT_TEXT = ((?:"[^"]*"\s*\+?\s*)+);', composer)
    assert m and "".join(re.findall(r'"([^"]*)"', m.group(1))) == CONSENT_TEXT
    assert CONSENT_GONE not in CONSENT_TEXT and "with your name as they have it" in CONSENT_TEXT


# ------------------------------------------------------------------------------------- the walk, by hand

NOBODY = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=(fake.BUYER_ALONE,))
NAMED = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=fake.BUYER_SUPPORTS)


def _p(dimension: str, *codes: str, chip: str | None = None) -> dict:
    return {"dimension": dimension, "codes": list(codes), "chip": chip}


#: Everything supporting the founder (a B2C link that answers all eight rungs, "Nobody else" tested, a £30 low).
CLEAR = [_p("problem.importance", "rival_1", "own"), _p("problem.current_solution_satisfaction", "outcome_3"),
         _p("solution.compatibility", "yes_easily"), _p("solution.relative_advantage", "positive"),
         _p("solution.adoption_friction", "yes"), _p("commercial.price", "band_20_50"),
         _p("commercial.buyer_payer_alignment", "decided_alone"), _p("commercial.purchase_friction", "yes_long"),
         _p("commercial.commitment", "yes_start")]


def _with(*changed: dict) -> list[dict]:
    by = {p["dimension"]: p for p in changed}
    return [by.get(p["dimension"], p) for p in CLEAR]


TABLE = [
    ("nothing owed", CLEAR, NOBODY, "PRIMARY", False, None),
    ("Importance: the own item not picked", _with(_p("problem.importance", "rival_1", "rival_2")), NOBODY, "PRIMARY",
     False, "problem.importance"),
    ("Importance: None of these, the escape that counts against",
     _with(_p("problem.importance", chip="NONE_OF_THESE")), NOBODY, "PRIMARY", False, "problem.importance"),
    ("Importance left out of the lock: no rung", _with(_p("problem.importance", "rival_1", "rival_2")),
     fake.Founder(importance_item=None, price_low=30.0, buyer_supports=(fake.BUYER_ALONE,)), "PRIMARY", False, None),
    ("Current solution: works well", _with(_p("problem.current_solution_satisfaction", "outcome_1")), NOBODY,
     "PRIMARY", False, "problem.current_solution_satisfaction"),
    ("Current solution: an escape is apart",
     _with(_p("problem.current_solution_satisfaction", chip="SOMEONE_ELSE_CHECKS")), NOBODY, "PRIMARY", False, None),
    ("Compatibility: only with help", _with(_p("solution.compatibility", "only_with_help")), NOBODY, "PRIMARY", False,
     "solution.compatibility"),
    ("Relative advantage: no difference", _with(_p("solution.relative_advantage", "neutral")), NOBODY, "PRIMARY",
     False, "solution.relative_advantage"),
    ("Adoption friction: probably not", _with(_p("solution.adoption_friction", "probably_not")), NOBODY, "PRIMARY",
     False, "solution.adoption_friction"),
    ("Price: a band below the founder's", _with(_p("commercial.price", "band_10_20")), NOBODY, "PRIMARY", False,
     "commercial.price"),
    ("Price: I wouldn't pay", _with(_p("commercial.price", "would_not_pay")), NOBODY, "PRIMARY", False,
     "commercial.price"),
    ("Price: the founder's band and above hold", _with(_p("commercial.price", "over_100")), NOBODY, "PRIMARY", False,
     None),
    ("Price: I can't say is apart", _with(_p("commercial.price", chip="CANT_SAY")), NOBODY, "PRIMARY", False, None),
    ("Price: no price in the lock", _with(_p("commercial.price", "would_not_pay")),
     fake.Founder(importance_item="own", price_low=None, buyer_supports=(fake.BUYER_ALONE,)), "PRIMARY", False, None),
    ("Buyer and payer, Nobody else tested: had to agree", _with(_p("commercial.buyer_payer_alignment",
                                                                   "had_to_agree")), NOBODY, "PRIMARY", False,
     "commercial.buyer_payer_alignment"),
    ("Buyer and payer, a role tested: had to agree supports", _with(_p("commercial.buyer_payer_alignment",
                                                                       "had_to_agree")), NAMED, "PRIMARY", False, None),
    # keel-cloud 128 FR-20 (`FollowUpComposer.closes`): decided alone is against a named role, but the pick closes the
    # line -- nobody had to agree -- so it owes no follow-up (Codyco)
    ("Buyer and payer, a role tested: decided alone closes the line",
     [_p("commercial.buyer_payer_alignment", "decided_alone")], NAMED, "COMMERCIAL_B2B", True, None),
    ("Commitment: yes, after trying it first (its second stem, keel-cloud 118)",
     _with(_p("commercial.commitment", "yes_after_trying"), _p("commercial.purchase_friction", "yes_long")),
     NOBODY, "PRIMARY", False, None),
    ("Commitment: probably not", _with(_p("commercial.commitment", "probably_not")), NOBODY, "PRIMARY", False,
     "commercial.commitment"),
    ("Purchase friction: quick is against the fear (a rung since keel-cloud 118)",
     _with(_p("commercial.purchase_friction", "yes_quick")), NOBODY, "PRIMARY", False, "commercial.purchase_friction"),
    ("the first rung wins", _with(_p("solution.compatibility", "no"), _p("commercial.commitment", "no")), NOBODY,
     "PRIMARY", False, "solution.compatibility"),
    ("a B2B practitioner's link walks no commercial rung", _with(_p("commercial.commitment", "no")), NOBODY, "PRIMARY",
     True, None),
    ("the decision-maker's link walks the commercial rungs only",
     [_p("problem.importance", "rival_1", "rival_2"), _p("commercial.price", "band_10_20")], NOBODY,
     "COMMERCIAL_B2B", True, "commercial.price"),
]


@pytest.mark.parametrize("name,picks,founder,link,b2b,want", TABLE, ids=[t[0] for t in TABLE])
def test_first_rung_by_hand(name, picks, founder, link, b2b, want):
    """The against walk (spec 064 FR-7: keel-cloud 118's ladder); the second stems are `test_the_second_stems`."""
    stems = [d for d, apart in fake.owed(picks, founder, link, b2b=b2b) if not apart]
    assert (stems[0] if stems else None) == want


def test_the_second_stems_and_the_deciding_line_first():
    """keel-cloud 118 FR-4: an answer a rung's `also` names is owed its second stem (the conditional yes, the long
    purchase); the deciding lines are walked first, then registry order."""
    assert fake.first_stem(CLEAR, NOBODY) == ("commercial.purchase_friction", True)
    assert fake.first_stem(_with(_p("commercial.commitment", "yes_after_trying")), NOBODY, "COMMERCIAL_B2B",
                           b2b=True) == ("commercial.purchase_friction", True)
    both = _with(_p("problem.importance", "rival_1", "rival_2"), _p("problem.current_solution_satisfaction",
                                                                   "outcome_1"))
    assert fake.first_rung(both, NOBODY) == "problem.importance"
    assert fake.first_rung(both, NOBODY, first=["problem.current_solution_satisfaction"]) == \
        "problem.current_solution_satisfaction"
    assert fake.ordered(fake.RUNGS, ["commercial.commitment", "commercial.commitment"])[:2] == (
        "commercial.commitment", "problem.importance")
    standings = {"vectors": [
        {"vector": "PROBLEM", "verdict": "PEOPLE_DISAGREE", "dimensions": [
            {"dimension": "problem.prevalence", "status": "HOLDING_UP"},
            {"dimension": "problem.importance", "status": "PEOPLE_DISAGREE"},
            {"dimension": "problem.current_solution_satisfaction", "status": "PEOPLE_DISAGREE"}]},
        {"vector": "SOLUTION", "verdict": "TOO_FEW_TO_CALL", "dimensions": []},
        {"vector": "COMMERCIAL", "verdict": "NOT_HOLDING_UP", "dimensions": [
            {"dimension": "commercial.price", "status": "PEOPLE_DISAGREE"},
            {"dimension": "commercial.commitment", "status": "NOT_HOLDING_UP"}]}]}
    assert fake.deciding_lines(standings) == ["problem.importance", "commercial.commitment"]
    assert fake.fill("commercial.commitment", {"{smaller_step}": "the free trial"}, also=True) == \
        "What would the free trial have to show you?"
    assert fake.spoken_of("commercial.purchase_friction", also=True) == "What took the time?"
    chain = fake.Founder(importance_item="own", price_low=1.0, chain_price=True)
    assert fake.first_rung([_p("commercial.price", "band_0.5_1")], chain, "COMMERCIAL_B2B", b2b=True) == \
        "commercial.price"
    assert fake.first_rung([_p("commercial.price", "band_1_2")], chain, "COMMERCIAL_B2B", b2b=True) is None
    assert fake.first_rung([_p("commercial.price", "upfront.band_250_599", "band_10_20")], chain, "COMMERCIAL_B2B",
                           b2b=True) is None, "a two-step price has no rung (keel-cloud 115 judgement call 8)"


def test_first_rung_reads_only_what_the_link_serves():
    picks = _with(_p("problem.importance", "rival_1", "rival_2"), _p("commercial.commitment", "no"))
    served = {p["dimension"] for p in CLEAR} - {"problem.importance"}
    assert fake.first_rung(picks, NOBODY, served=served - {"commercial.purchase_friction"}) == "commercial.commitment"


def test_every_rung_is_a_case_of_the_table():
    assert {t[5] for t in TABLE if t[5]} == set(fake.RUNGS)


# ------------------------------------------------------------------------------------- the fill

def test_fill_and_its_words():
    assert fake.lower("Matching deliveries") == "matching deliveries" and fake.lower("POS tools") == "POS tools"
    assert fake.joined(["A", "B"], "and") == "a and b" and fake.joined(["A", "B", "C"], "or") == "a, b or c"
    assert fake.joined([None, " "], "and") is None
    assert fake.fill("problem.importance", {"{their_picks}": "a and b", "{founder_item}": "c"}) == \
        "You picked a and b over c. What makes those more pressing?"
    assert fake.fill("problem.importance", {}) == ("You picked other difficulties over this one. What makes those "
                                                   "more pressing?")
    assert fake.fill("commercial.price", {"{band}": fake.WOULD_NOT_PAY_BAND}) == \
        "You put it at nothing. What would make it worth more?"
    assert fake.fill("commercial.commitment", {}) == "What would you start with instead?"
    assert fake.price_floor("under_10") == 0 and fake.price_floor("band_20_50") == 20
    assert fake.price_floor("over_100") == 100 and fake.price_floor("would_not_pay") is None


def test_the_fakes_follow_up_lines():
    assert fake.KINDS[-1] == "FOLLOW_UP" and "FOLLOW_UP" in fake.UNSPOKEN
    assert fake.follow_up_script(fake.rung("problem.importance")[3]) == (
        "One more thing. You put other difficulties ahead of this one. What makes those more pressing?")
    assert fake.walks("COMMERCIAL_B2B", True) == ("commercial.price", "commercial.buyer_payer_alignment",
                                                  "commercial.purchase_friction", "commercial.commitment")
    assert len(fake.walks("PRIMARY", True)) == 5 and len(fake.walks("PRIMARY", False)) == 9
    assert all(fake.fake_seconds(fake.follow_up_script(r[3])) >= 1.0 for r in fake.LADDER)


# ------------------------------------------------------------------------------------- keel-web 076, restated

@pytest.mark.parametrize("name", ["FOLLOW_UP_KICKER", "FOLLOW_UP_NOTE", "FOLLOW_UP_SKIP", "FOLLOW_UP_HINT",
                                  "SPEAK_HINT_STORY", "SPEAK_OR_TYPE_PLACEHOLDER", "SPEAK_TYPE_PLACEHOLDER",
                                  "SPEAK_LABEL", "SPEAK_ADD_MORE", "SPEAK_LISTENING", "SPEAK_LISTENING_NOTE",
                                  "SPEAK_MIC_OFF", "HEARING_YOU", "SPEAK_ASKING", "AI_REASON_DIDNT_CATCH",
                                  "AI_SECOND_MISS_FREE", "AI_REASON_NO_MATCH"])
def test_the_follow_up_and_box_words_are_keel_webs(name):
    text = _web("src/lib/translate.ts")
    m = re.search(rf"export const {name} = \"([^\"]*)\";", text)
    assert m and m.group(1) == getattr(ivs, name), (name, m and m.group(1))


def test_the_heard_line_and_the_caps_are_keel_webs():
    text = _web("src/lib/translate.ts")
    lead = re.search(r'SPEAK_HEARD_LEAD = "([^"]*)"', text).group(1)
    rest = re.search(r'SPEAK_HEARD = "([^"]*)"', text).group(1)
    assert f"{lead} {rest}" == ivs.SPEAK_HEARD
    path = _web("src/lib/answerPath.ts")
    # keel-web 082 (D36): the recorded silence by window kind, the same two values as the quiet gaps
    assert re.search(r"export const QUIET_OPTION_MS = (\d[\d_]*);", path).group(1).replace("_", "") == \
        str(ivs.SILENCE_OPTION_MS)
    assert re.search(r"export const QUIET_FREE_MS = (\d[\d_]*);", path).group(1).replace("_", "") == \
        str(ivs.SILENCE_FREE_MS)
    assert "SILENCE_OPTION_MS = QUIET_OPTION_MS;" in path and "SILENCE_FREE_MS = QUIET_FREE_MS;" in path
    assert re.search(r"FOLLOW_UP_RECORD_CAP_MS = (\d[\d_]*);", path).group(1).replace("_", "") == \
        str(ivs.FOLLOW_UP_RECORD_CAP_MS)
    assert ivs.FOLLOW_UP_SEAM_CAP_MS < ivs.FOLLOW_UP_RECORD_CAP_MS


def test_the_seam_keys_the_walk_sets_are_keel_webs():
    seam = _web("src/components/interview/ai/useSpeechRecognition.ts")
    for key in ("followUpCapMs", "silenceMs", "storyCapMs", "recorder", "mic", "earcons"):
        assert re.search(rf"\b{key}\?:", seam), key
    # spec 074 (keel-web 115): no recogniser on any seam; the box's microphone refused through `mic(level, true)`
    text = ivs.text_seam(refused=True)
    assert "Recognition" not in text and "mic(() => window.__levelNow, true)" in text and "__micAcquired" in text
    assert "mic(() => window.__levelNow, false)" in ivs.text_seam()
    assert "followUpCapMs = 9000" in ivs.follow_up_cap_seam(9000)
    assert "followUpCapMs" not in ivs.SPEECH_SEAM
    box = _web("src/components/interview/SpeakOrTypeBox.tsx")
    for testid in ("iv-mic", "iv-listening", "iv-mic-clock", "iv-mic-cancel", "iv-mic-done"):
        assert f'data-testid="{testid}"' in box, testid
    assert 'data-testid="iv-follow-up"' in _web("src/components/interview/FollowUpScreen.tsx")
    assert 'data-testid="ai-skip"' in _web("src/components/interview/ai/Sheet.tsx")


# ------------------------------------------------------------------------------------- the corpus people's lines

@pytest.mark.parametrize("entry_id", ["01-countly", "05-paidly", "07-mulchrun"])
def test_the_follow_up_lines(entry_id):
    _, entry = vs.entry_for(CONFIG.keel_cloud, entry_id)
    people = vs.person_inputs(entry)
    founder = vs.founder_side(entry)
    names = {w.lower() for p in people for w in p.person.split()}
    rungs: dict[str, list] = {}
    for p in people:
        # spec 076 FR-5 (keel-web 127 FR-3): a story chip ends the interview at the gate -- nothing is asked of them
        asked = p.link == vs.LINK_B2B or (p.recency and not p.ends_on_chip)
        rung = fake.first_rung(p.picks, founder, p.link, b2b=vs.is_b2b(entry)) if asked else None
        if rung:
            rungs.setdefault(rung, []).append(p)
        if p.follow_up is not None:
            assert rung and not re.search(r"\d", p.follow_up), (p.person, p.follow_up)
            assert not ({w.strip(".,").lower() for w in p.follow_up.split()} & names), (p.person, p.follow_up)
            assert p.follow_up.count(".") == 1 and p.follow_up.endswith("."), p.follow_up
    assert rungs, entry_id
    for rung, on in rungs.items():
        assert any(p.follow_up for p in on), (entry_id, rung)          # someone on every failing rung types
    assert any(p.recency and not fake.first_rung(p.picks, founder, p.link, b2b=vs.is_b2b(entry))
               for p in people)                                         # someone is owed nothing
    skippers = [p.person for p in people if p.follow_up is None and p.person in vs.FOLLOW_UP_SKIPS[entry_id]]
    assert skippers == list(vs.FOLLOW_UP_SKIPS[entry_id])
    spoken = vs.STORY_SPOKEN[entry_id]
    assert all(next(p for p in people if p.person == who).story for who in spoken), spoken


def test_the_founder_side_of_three_entries():
    sides = {eid: vs.founder_side(vs.entry_for(CONFIG.keel_cloud, eid)[1])
             for eid in ("01-countly", "05-paidly", "07-mulchrun")}
    assert sides["01-countly"] == fake.Founder("own", 30.0, (fake.BUYER_ALONE,))
    assert sides["07-mulchrun"].price_low is None                        # no price yet: no Price rung


# ------------------------------------------------------------------------------------- the new reads

class _Remote:
    is_remote = True


@pytest.mark.parametrize("call", [lambda c: ledger.stand_in_no_follow_ups(c, str(uuid.uuid4())),
                                  lambda c: ledger.stored_follow_ups(c, str(uuid.uuid4()))])
def test_the_follow_up_reads_are_never_reached_on_the_remote_profile(call):
    with pytest.raises(ledger.LedgerUnavailable, match="remote"):
        call(_Remote())


# ------------------------------------------------------------------------------------- the remote profile types

class _Handle:
    def __init__(self, steps: list, name: str, kind: str):
        self.step = {"name": name, "kind": kind}
        steps.append(self.step)

    def record_wire(self, expected, actual):
        self.step["wire"] = (expected, actual)

    def record_assert(self, expected, actual):
        self.step["assert"] = (expected, actual)

    def capture_text(self, *_):
        pass


class _Recorder:
    def __init__(self):
        self.steps: list = []

    def step(self, name, *, party="stack", kind="assert"):
        import contextlib  # noqa: PLC0415

        @contextlib.contextmanager
        def cm():
            yield _Handle(self.steps, name, kind)
        return cm()


class _Context:
    def __init__(self):
        self.scripts: list[str] = []
        self.request = self

    def get(self, url, timeout=None):
        return type("R", (), {"json": staticmethod(lambda: {"kind": "FULL", "parts": []})})()

    def add_init_script(self, script):
        self.scripts.append(script)

    def new_page(self):
        return object()

    def close(self):
        pass


class _Walked(Exception):
    pass


def _answer_priya(monkeypatch, stack):
    """`corpus_scenario._answer_one` for 01-countly's Priya Natarajan (STORY_SPOKEN "quiet") up to her walk: what the
    stranger's context had installed, and the `speak` the walk was handed."""
    from types import SimpleNamespace  # noqa: PLC0415

    from evals import corpus_scenario as cs  # noqa: PLC0415

    seen: dict = {}

    class _Interview:
        def __init__(self, page, recorder):
            pass

        def open(self, link):
            pass

        def walk(self, person, interview, by_item, *, follow_up=None, speak=None, follow_up_rung=None, lines=None,
                 late=()):
            seen["speak"] = speak
            raise _Walked

    context = _Context()
    monkeypatch.setattr(cs.vs_screens, "Interview", _Interview)
    monkeypatch.setattr(cs.vs, "follow_up_question", lambda *a, **k: None)
    monkeypatch.setattr(cs.vs, "follow_up_plan", lambda *a, **k: [])                    # spec 075: nothing asked
    person = SimpleNamespace(person="Priya Natarajan", recency=True, story="It was a Tuesday.", picks=[],
                             link=vs.LINK_PRIMARY, follow_up=None, response=lambda token, recall: {"answers": []})
    assert vs.STORY_SPOKEN["01-countly"][person.person] == "quiet"
    recorder = _Recorder()
    j = SimpleNamespace(browser=SimpleNamespace(new_context=lambda: context), cloud_base="http://cloud",
                        interviews={}, entry=SimpleNamespace(id="01-countly"), links={person.person: "http://link"},
                        recorder=recorder, stack=stack, strict=True, speak={})
    with pytest.raises(_Walked):
        cs._answer_one(j, person, "tok")
    return context.scripts, seen["speak"], recorder.steps


def test_the_remote_profile_installs_no_speech_seam_and_types_the_story(monkeypatch):
    """Amendment 2026-10-17: staging serves keel-web's production build, which never reads `window.__keelSpeech`, so on
    the remote profile the story's speaker gets no seam and types (`speak` None), and a note says it was skipped."""
    scripts, speak, steps = _answer_priya(monkeypatch, _Remote())
    assert speak is None
    assert not any("__keelSpeech" in s for s in scripts), scripts
    notes = [s for s in steps if s["kind"] == "note"]
    assert len(notes) == 1 and "skipped on the remote profile" in notes[0]["name"], steps


def test_the_local_profile_still_speaks_through_the_seam(monkeypatch):
    scripts, speak, steps = _answer_priya(monkeypatch, type("Local", (), {"is_remote": False})())
    assert speak == "quiet"
    assert any("__keelSpeech" in s for s in scripts) and not [s for s in steps if s["kind"] == "note"], steps


def test_the_interviewer_scorecard_owes_nothing_on_the_remote_profile(monkeypatch, tmp_path):
    """The interviewer leg's remote return writes its card with nothing owed, IM26 unmeasured, and the one line why."""
    from types import SimpleNamespace  # noqa: PLC0415

    from evals import interviewer_leg as leg  # noqa: PLC0415

    monkeypatch.setattr(leg, "_own_ai", lambda j, wire, record: None)
    recorder = _Recorder()
    recorder.run_dir = str(tmp_path)
    j = SimpleNamespace(entry=SimpleNamespace(id="01-countly"), project_id="p", recorder=recorder, stack=_Remote())
    leg._leg(j, short=True)
    card = json.loads((tmp_path / "interviewer-marks.json").read_text(encoding="utf-8"))
    assert card["owed"] == [] and "IM26" in card["unmeasured"] and "remote profile" in card["note"], card
    assert any("none owed on the remote profile" in s["name"] for s in recorder.steps), recorder.steps
