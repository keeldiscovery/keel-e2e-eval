"""Spec 151 FR-9: the copilot call bench, offline -- no key, no call, no audio rendered.

The questionnaire read from a stored bundle fragment; the catalogue's rules (each with a passing and a failing script);
the plan; the fake writer's scripts passing the same rules; every stack through a fake transport (the Realtime
transcription protocol included); the scorer on canned events for every bar, one passing and one failing run each; the
certificate line; the cost arithmetic; and `DRY=1` end to end with the network refused.
"""

from __future__ import annotations

import copy
import json
import re
import wave
from pathlib import Path

import pytest

from evals.copilot import bars as B
from evals.copilot import bench, clients, plan, questionnaire as qmod, render, report, score, writer
from evals.copilot import catalogue as cat
from evals.copilot.fakes import FakeClients, FakeRealtime
from evals.copilot.stacks import AudioDirect, RunningState, TurnByTurn, base, canned_events, parse_stacks
from evals.copilot.stacks.running_state import LIVE_MODEL, LiveTranscriber
from evals.noise import pipeline as noise
from stack.config import REPO_ROOT

HERE = REPO_ROOT / "evals" / "copilot"
FRAGMENT = REPO_ROOT / "tests" / "fixtures" / "copilot" / "backtest-fragment.json"


@pytest.fixture(scope="module")
def q() -> dict:
    return qmod.load()


@pytest.fixture(scope="module")
def frag() -> dict:
    return qmod.extract(json.loads(FRAGMENT.read_text(encoding="utf-8")), source="fragment")


def scripts_for(q, round_, n=None):
    entries = plan.build(round_, q)
    entries = entries if n is None else entries[:: max(1, len(entries) // n)][:n]
    recs = [writer.FakeWriter(q).write(e) for e in entries]
    assert all(r["kept"] for r in recs), [r["faults"] for r in recs if not r["kept"]][:3]
    return [r["script"] for r in recs]


# ------------------------------------------------------------------------------------- FR-1 the questionnaire

def test_the_fragment_is_read_in_served_order_with_the_noise_kinds(frag):
    items = frag["items"]
    assert [i["id"] for i in items] == ["q1", "q2", "q3", "q4", "q5", "q6"]
    assert [(i["link"], i["control"], i["kind"]) for i in items] == [
        ("PRIMARY", "gate", "gate"), ("PRIMARY", "story", "free"), ("PRIMARY", "pick_two", "multi"),
        ("COMMERCIAL_B2B", "value_box", "number"), ("COMMERCIAL_B2B", "price_ladder", "single"),
        ("COMMERCIAL_B2B", "single_choice", "single")]
    gate, story, pick, box, price, money = items
    assert gate["options"] == ["Yes", "No"] and gate["escape"] is None
    assert story["question"].startswith("Think of the most recent time")
    assert pick["pick"] == 2 and pick["escape"] == "None of these"
    assert box["unit"] == "hours" and box["nothing"] == "None" and box["range"] == qmod.OPEN_RANGE
    assert price["spoken"]["under"] == "Under $50, or $50 to under $200?" and "pick" not in price
    assert money["spoken"]["anchor"] == "Think of the price you just gave." and money["asked_after"]
    assert frag["links"]["PRIMARY"]["idea"] == {"what": "Imagine a helper for the weekly task.",
                                                "how": "It does the first pass for you."}


def test_an_item_reads_through_norm_out_unchanged(frag):
    pick = qmod.noise_item(frag["items"][2])
    assert noise.norm_out(pick, {"picks": [4, 1, 2]}) == {"picks": [1, 4]}
    assert noise.norm_out(qmod.noise_item(frag["items"][3]), {"value": 12}) == {"value": 12}


def test_an_unknown_control_is_refused_by_name():
    bundle = json.loads(FRAGMENT.read_text(encoding="utf-8"))
    bundle["respondents"]["PRIMARY"]["served"]["parts"][0]["items"][0]["control"] = "slider_ten"
    with pytest.raises(qmod.UnknownControl, match="slider_ten"):
        qmod.extract(bundle)


def test_the_committed_fixture_is_the_bundles_six_items(q):
    assert Path(q["path"]).name == "questionnaire-08-fresco.json"
    assert q["source"] == "20261109T195556Z-backtest-08-fresco"
    assert [i["kind"] for i in q["items"]] == ["number", "single", "single", "single", "single", "single"]
    assert [i["control"] for i in q["items"]] == ["value_box", "price_ladder", "single_choice", "fixed_four",
                                                 "duration_bands", "fixed_four"]
    assert all(i["spoken"]["stem"] for i in q["items"])
    bundle = REPO_ROOT / "runs" / q["source"] / "backtest.json"
    if bundle.is_file():                                                       # the bundle kept beside the runs
        fresh = qmod.extract(json.loads(bundle.read_text(encoding="utf-8")), source=q["source"])
        assert fresh["items"] == q["items"]


# --------------------------------------------------------------------------------------- FR-2 the catalogue

FR2_FOUNDER = ["verbatim", "light_reword", "options_own_words", "options_reordered_or_missing", "story_prompt",
               "meaning_changed", "preface", "stacked", "leading", "restart", "clarifying", "follow_up",
               "follow_ups_in_a_row", "own_note", "any_order", "went_back", "answered_for_them", "back_channel"]
FR2_RESPONDENT = ["straight", "story_first", "hedged", "late_negation", "number_for_yes_no", "different_question",
                  "counter_question", "interrupted", "two_voices"]


def test_the_catalogue_holds_every_kind_of_the_page():
    assert list(cat.FOUNDER) == FR2_FOUNDER and list(cat.RESPONDENT) == FR2_RESPONDENT
    assert cat.VERDICTS == ("as_written", "same_meaning", "options_own_words", "meaning_changed", "stacked", "leading",
                            "follow_up", "own_note", "back_channel", "nothing")
    assert cat.TIERS == ("sure", "likely", "unsure")
    assert cat.STATES == ("listening", "answered", "follow_up", "note", "paused", "done")
    for k in cat.KINDS.values():
        assert set(k.applies_to) <= set(cat.ITEM_KINDS) and k.describe
        assert k.verdict is None or k.verdict in cat.VERDICTS
    # every kind either has a rule on its words or says why not
    assert set(cat.WORD_RULES) | set(cat.NO_WORD_RULE) == set(cat.KINDS)
    assert not set(cat.WORD_RULES) & set(cat.NO_WORD_RULE)


def test_the_expected_tier_is_capped_by_the_asking_kind():
    assert cat.expected_tier("verbatim", "straight") == "sure"
    assert cat.expected_tier("story_prompt", "straight") == "likely"
    assert cat.expected_tier("meaning_changed", "hedged") == "likely"
    assert cat.expected_tier("story_prompt", "different_question") == "unsure"
    assert cat.expected_tier(None, "hedged") == "likely"


def _persona_words(q) -> list[str]:
    """The proper nouns and trade words the committed questionnaire carries: none may reach the bench's own text."""
    text = " ".join([q["links"][k]["idea"]["what"] + " " + q["links"][k]["idea"]["how"] for k in q["links"]]
                    + [i["question"] for i in q["items"]])
    words = {w for w in re.findall(r"\b[A-Z][A-Za-z]{2,}\b", text)} - {"Imagine", "During", "Then", "With", "Last",
                                                                      "What", "Think", "If", "Could", "The", "It"}
    return sorted(words | {"superintendent", "daily log", "site walk"})


def test_the_bench_is_persona_agnostic(q):
    words = _persona_words(q)
    assert "Fresco" in words and "Procore" in words
    files = [HERE / n for n in ("catalogue.py", "plan.py", "writer.py", "score.py", "bars.py", "report.py",
                                "bench.py", "render.py", "clients.py", "fakes.py", "questionnaire.py")]
    files += sorted((HERE / "stacks").glob("*.py")) + sorted((HERE / "instructions").glob("*.md"))
    for path in files:
        # the fixture's file name may carry the entry id (the brief); nothing else may
        text = path.read_text(encoding="utf-8").replace(qmod.DEFAULT_FIXTURE.name, "")
        for w in words:
            assert not re.search(r"\b" + re.escape(w) + r"\b", text, re.I), (path.name, w)


def _script(turns, round_=1):
    return {"id": "t", "round": round_, "questionnaire": "x", "turns": turns}


def _turn(t, who, text, *, kind=None, q=None, verdict=None, option=None, tier=None, state="listening", gap=0.5):
    return {"t": t, "who": who, "text": text, "silence_after": gap, "kind": kind,
            "truth": {"q": q, "verdict": verdict, "option": option, "tier": tier, "state_after": state}}


def _ask_answer(q, *, ask_text=None, ask_kind="verbatim", verdict="as_written", answer="Under 1 week.",
                beh="straight", option=None, tier="sure"):
    item = qmod.by_id(q)["q5"]
    return [_turn(1, "founder", ask_text or item["spoken"]["stem"], kind=ask_kind, q="q5", verdict=verdict),
            _turn(6, "them", answer, kind=beh, q="q5", option=option or {"picks": [1]}, tier=tier, state="answered")]


def test_a_verbatim_turn_must_be_the_stem(q):
    assert cat.validate(_script(_ask_answer(q)), q) == []
    bad = _ask_answer(q, ask_text="How long would the check take, would you say?")
    assert any("verbatim turn is not the spoken stem" in f for f in cat.validate(_script(bad), q))


def test_own_words_options_carry_no_label(q):
    good = _ask_answer(q, ask_text="How long would that take, a few days or a long time?", ask_kind="options_own_words",
                       verdict="options_own_words")
    assert cat.validate(_script(good), q) == []
    bad = _ask_answer(q, ask_text="How long, under 1 week or longer?", ask_kind="options_own_words",
                      verdict="options_own_words")
    assert any("own-words options say Keel's label" in f for f in cat.validate(_script(bad), q))


def test_a_follow_up_comes_after_an_answered_question(q):
    good = _ask_answer(q) + [_turn(9, "founder", "Why is that?", kind="follow_up", q="q5", verdict="follow_up",
                                   state="follow_up")]
    assert cat.validate(_script(good), q) == []
    bad = [_turn(1, "founder", "Why is that?", kind="follow_up", q="q5", verdict="follow_up", state="follow_up")]
    assert any("follow-up before its question was answered" in f for f in cat.validate(_script(bad), q))


def test_a_back_channel_carries_no_question_mark(q):
    good = _ask_answer(q) + [_turn(9, "founder", "Right, okay.", kind="back_channel", verdict="back_channel",
                                   state="answered")]
    assert cat.validate(_script(good), q) == []
    bad = _ask_answer(q) + [_turn(9, "founder", "Right, okay?", kind="back_channel", verdict="back_channel",
                                  state="answered")]
    assert any("back-channel turn carries a question mark" in f for f in cat.validate(_script(bad), q))


def test_an_own_note_asks_something(q):
    good = _ask_answer(q) + [_turn(9, "founder", "And how many people are on a typical site for you?",
                                   kind="own_note", verdict="own_note", state="note")]
    assert cat.validate(_script(good), q) == []
    bad = _ask_answer(q) + [_turn(9, "founder", "Great, that's all I needed, thanks for your time.", kind="own_note",
                                  verdict="own_note", state="note")]
    assert any("own note that asks nothing" in f for f in cat.validate(_script(bad), q))


def test_the_clocks_are_monotone(q):
    turns = _ask_answer(q)
    turns[1]["t"] = 1.2                                                        # before the first turn's silence ends
    assert any("clocks not monotone" in f for f in cat.validate(_script(turns), q))


def test_the_round_length_is_held(q):
    turns = _ask_answer(q)
    turns[1]["t"] = 75
    assert any("runs past round 1" in f for f in cat.validate(_script(turns), q))


def test_a_restart_breaks_and_a_preface_ends_with_the_stem(q):
    stem = qmod.by_id(q)["q5"]["spoken"]["stem"]
    assert cat.validate(_script(_ask_answer(q, ask_text=f"If you... sorry, {stem}", ask_kind="restart")), q) == []
    assert any("restart carries no break" in f for f in
               cat.validate(_script(_ask_answer(q, ask_text=f"If you {stem}", ask_kind="restart")), q))
    assert cat.validate(_script(_ask_answer(q, ask_text=f"Okay so, one more thing here. {stem}",
                                            ask_kind="preface")), q) == []
    assert any("preface does not end with the stem" in f for f in
               cat.validate(_script(_ask_answer(q, ask_text=f"{stem} Okay?", ask_kind="preface")), q))


def test_the_respondent_rules(q):
    late = _ask_answer(q, answer="Over 3 months... no, actually, under 1 week.", beh="late_negation")
    assert cat.validate(_script(late), q) == []
    assert any("late negation" in f for f in cat.validate(_script(
        _ask_answer(q, answer="Under 1 week, honestly, for sure.", beh="late_negation")), q))
    other = _ask_answer(q, answer="The tools are the problem.", beh="different_question", option={"unclear": True},
                        tier="unsure")
    other[1]["truth"]["state_after"] = "listening"
    assert cat.validate(_script(other), q) == []
    other[1]["truth"]["option"], other[1]["truth"]["tier"] = {"picks": [1]}, "unsure"
    assert any("different question must read unclear" in f for f in cat.validate(_script(other), q))
    wrong_tier = _ask_answer(q, beh="hedged", answer="Mostly under 1 week.", tier="sure")
    assert any("where the catalogue says likely" in f for f in cat.validate(_script(wrong_tier), q))


def test_a_counter_question_ends_with_a_question_mark(q):
    turns = _ask_answer(q)[:1] + [
        _turn(6, "them", "What do you mean?", kind="counter_question", q="q5", verdict="nothing"),
        _turn(8, "founder", "I mean for you yourself.", kind="clarifying", q="q5", verdict="same_meaning"),
        _turn(11, "them", "Under 1 week.", q="q5", option={"picks": [1]}, tier="sure", state="answered")]
    assert cat.validate(_script(turns), q, kinds=["counter_question", "clarifying"]) == []
    turns[1]["text"] = "What do you mean."
    assert any("counter-question that is no question" in f for f in cat.validate(_script(turns), q))


def test_every_planned_kind_must_appear_and_the_option_shape_is_checked(q):
    assert any("kind stacked is on no turn" in f for f in cat.validate(_script(_ask_answer(q)), q, kinds=["stacked"]))
    bad = _ask_answer(q, option={"picks": [9]})
    assert any("a pick outside 1..6" in f for f in cat.validate(_script(bad), q))
    bad = _ask_answer(q, option={"value": 3})
    assert any("value on a non-number item" in f for f in cat.validate(_script(bad), q))


def test_any_order_is_read_from_the_order_asked(q):
    items = qmod.by_id(q)
    ask = lambda t, iid: _turn(t, "founder", items[iid]["spoken"]["stem"], kind="verbatim", q=iid,  # noqa: E731
                               verdict="as_written")
    answer = lambda t, iid: _turn(t, "them", items[iid]["options"][0] + ".", kind="straight", q=iid,  # noqa: E731
                                  option={"picks": [1]}, tier="sure", state="answered")
    in_order = [ask(1, "q2"), answer(8, "q2"), ask(12, "q3"), answer(20, "q3")]
    out_of_order = [ask(1, "q3"), answer(8, "q3"), ask(12, "q2"), answer(20, "q2")]
    assert cat.validate(_script(out_of_order), q, kinds=["any_order"]) == []
    faults = cat.validate(_script(in_order), q, kinds=["any_order"])
    assert any("asked in Keel's order" in f for f in faults)


# --------------------------------------------------------------------------------------------- FR-3 the plan

def test_round_one_is_every_applicable_combination_up_to_700(q):
    entries = plan.build(1, q)
    assert len(entries) == 608 <= plan.R1_CAP
    assert len({(tuple(e["items"]), json.dumps(e["founder"]), json.dumps(e["respondent"]), tuple(e["extras"]))
                for e in entries}) == len(entries)
    assert {k for e in entries for k in e["kinds"]} == {k for k in cat.KINDS if cat.KINDS[k].first_round == 1} - {
        "number_for_yes_no"}                                                    # the fixture has no gate
    assert all(e["respondent"][e["items"][0]] == "counter_question" for e in entries if "clarifying" in e["kinds"])
    assert plan.build(1, q) == entries                                         # seeded: reproducible


def test_the_cap_draws_when_the_combinations_pass_700(q):
    big = {"items": [dict(it, id=f"q{n}") for n, it in enumerate(q["items"] * 2, 1)], "links": {}}
    entries = plan.build(1, big)
    assert len(entries) == plan.R1_CAP and plan.build(1, big) == entries


def test_the_long_rounds_cover_their_kinds(q):
    r2, r3, r4 = plan.build(2, q), plan.build(3, q), plan.build(4, q)
    assert (len(r2), len(r3), len(r4)) == (200, 120, 12)
    assert all(plan.coverage(r2).get(k) for k in cat.FOLLOW_UP_KINDS)
    assert all(len(e["items"]) == 2 for e in r2)
    assert all(len(e["items"]) == len(q["items"]) for e in r3)
    assert all(e["never_reached"] and e["silence"] == 300 and e["follow_ups"][e["long_item"]] >= 10 for e in r4)


def test_the_fake_writer_passes_every_round_one_script(q):
    recs = [writer.FakeWriter(q).write(e) for e in plan.build(1, q)]
    assert sum(r["kept"] for r in recs) == 608


@pytest.mark.parametrize("round_", [2, 3, 4])
def test_the_fake_writer_passes_the_long_rounds(q, round_):
    assert scripts_for(q, round_, 12)


def test_the_writer_prompt_names_the_kinds_and_the_spoken_forms(q):
    e = plan.build(1, q)[0]
    body = writer.request_body(e, q, "questionnaire-08-fresco")
    assert body["model"] == "claude-sonnet-5-5" and body["thinking"] == {"type": "adaptive"}
    assert "temperature" not in body and body["max_tokens"] == writer.MAX_TOKENS[1]
    user = body["messages"][0]["content"]
    assert all(k in user for k in e["kinds"]) and "spoken stem:" in user and "option 1:" in user
    system = body["system"]
    for v in cat.VERDICTS + cat.TIERS + cat.STATES:
        assert v in system, v


def _reply(obj) -> dict:
    return {"content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": json.dumps(obj)}],
            "usage": {"input_tokens": 1000, "output_tokens": 500}}


class _Queue:
    def __init__(self, replies):
        self.replies, self.bodies = list(replies), []

    def messages(self, body):
        self.bodies.append(copy.deepcopy(body))
        return self.replies.pop(0), 10


def test_the_model_writer_rewrites_once_then_drops(q):
    e = plan.build(1, q)[0]
    good = writer.compose(e, q)
    bad = copy.deepcopy(good)
    bad["turns"][0]["text"] = "Something else entirely?"
    fixed = _Queue([_reply(bad), _reply(good)])
    rec = writer.ModelWriter(fixed, q, "x").write(e)
    assert rec["kept"] and rec["tries"] == 2 and rec["usage"] == {"input_tokens": 2000, "output_tokens": 1000}
    second = fixed.bodies[1]["messages"]
    assert [m["role"] for m in second] == ["user", "assistant", "user"] and "verbatim turn" in second[2]["content"]
    assert second[1]["content"][0]["type"] == "thinking"                        # the first reply passed back unchanged
    assert rec["cost_usd"] == pytest.approx((2000 * 2 + 1000 * 10) / 1e6)
    dropped = writer.ModelWriter(_Queue([_reply(bad), {"content": [{"type": "text", "text": "no json"}]}]), q,
                                 "x").write(e)
    assert not dropped["kept"] and dropped["faults"] == ["the reply is not one JSON object"] and "script" not in dropped


def test_the_sample_reads_words_beside_truth(q):
    md = writer.sample_markdown(scripts_for(q, 1, 3), 20)
    assert md.count("\n## r1-") == 3 and "| t | who | words | kind | q | verdict | option | tier | box after |" in md


# --------------------------------------------------------------------------------------------- FR-4 rendering

def test_the_timeline_waits_for_the_silence_and_overlaps_a_turn_talked_over():
    turns = [{"t": 0, "who": "founder", "silence_after": 0.5}, {"t": 1, "who": "them", "silence_after": 0,
                                                                "kind": "interrupted"},
             {"t": 2, "who": "founder", "silence_after": 0.5}, {"t": 0, "who": "them", "silence_after": 0}]
    c = render.timeline(turns, [3.0, 2.0, 1.0, 1.0])
    assert [(x["start"], x["end"]) for x in c] == [(0.0, 3.0), (3.5, 5.5), (4.9, 5.9), (6.4, 7.4)]


def test_noise_is_r3_only_and_at_most_a_tenth(q):
    scripts = [{"id": f"r3-{n:04d}"} for n in range(1, 121)]
    picked = render.noise_plan(scripts, round_=3, snrs="10")
    assert len(picked) == 12 and {v["bed"] for v in picked.values()} == set(render.NOISE_BEDS)
    assert all(v["snr"] == 10 for v in picked.values())
    assert render.noise_plan(scripts, round_=3, snrs="10", share=0.5) == picked
    assert render.noise_plan(scripts, round_=1, snrs="10") == {}
    assert render.noise_plan(scripts, round_=3, snrs=None) == {}
    assert render.voices("ash:coral") == ("ash", "coral") and render.voices("") == render.DEFAULT_VOICES


# ------------------------------------------------------------------------------------------- FR-5 the stacks

def _track(path: Path, seconds: float):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(render.SR)
        w.writeframes(b"\x01\x00" * int(seconds * render.SR))


@pytest.fixture()
def audio_run(q, tmp_path):
    s = scripts_for(q, 1, 3)[2]                                                 # four turns, both speakers twice
    clocks = render.timeline(s["turns"], [2.0] * len(s["turns"]))
    end = clocks[-1]["end"] + 1
    _track(tmp_path / "founder.wav", end)
    _track(tmp_path / "them.wav", end)
    return s, clocks, tmp_path


def test_the_haiku_request_is_the_noise_pipelines():
    body = base.haiku_body("sys", "user")
    ref = noise.request_body(qmod.noise_item({"kind": "single", "options": ["a"], "escape": None}), "x", "sys")
    assert {k: body[k] for k in ("model", "max_tokens", "thinking", "output_config")} == \
        {k: ref[k] for k in ("model", "max_tokens", "thinking", "output_config")}
    assert "temperature" not in body


def test_event_from_reads_a_reply_as_the_product_would(q):
    items = qmod.by_id(q)
    ev = base.event_from({"q": "q2", "verdict": None, "option": {"picks": [3, 1]}, "tier": "high",
                          "state": "answered"}, turn=1, who="them", items=items, current="q2", state="listening")
    assert ev["option"] == {"picks": [3]} and ev["tier"] == "sure" and ev["state"] == "answered"
    ev = base.event_from({"q": "q9", "verdict": "asked", "option": {"picks": [1]}, "tier": "sure", "state": "odd"},
                         turn=0, who="founder", items=items, current=None, state="listening")
    assert (ev["q"], ev["verdict"], ev["option"], ev["tier"], ev["state"]) == (None, None, None, None, "listening")
    ev = base.event_from({"q": "q1", "option": {"value": 2_000_000_000}, "tier": "sure"}, turn=0, who="them",
                         items=items, current="q1", state="listening")
    assert ev["option"] == {"unclear": True} and ev["tier"] == "unsure"           # out of range reads unclear
    assert base.event_from(None, turn=0, who="them", items=items, current=None, state="answered")["parsed"] is False
    # a founder verdict echoed onto the respondent's line is noise: the option is still read, nothing moves
    ev = base.event_from({"q": "q1", "verdict": "same_meaning", "option": {"value": 20}, "tier": "likely",
                          "state": "answered", "reason": "echo"}, turn=1, who="them", items=items, current="q1",
                         state="listening")
    assert (ev["verdict"], ev["option"], ev["tier"]) == (None, {"value": 20}, "likely")
    assert base.advance(ev, "q1") == "q1" and ev["reply"]["reason"] == "echo"
    ev = base.event_from({"q": "q1", "verdict": "follow_up", "option": {"value": 20}}, turn=1, who="them",
                         items=items, current="q1", state="follow_up")
    assert ev["verdict"] == "follow_up" and ev["option"] is None       # a follow-up reply is never an answer


def test_the_sheet_prints_every_clock_in_seconds():
    from evals.copilot import report, score
    assert report._v(score._cell("G.worst_s", 125.404, 10)) == "125.404 s"
    assert report._v(score._cell("A.same_meaning", 89.5, 10)) == "89.5%"


@pytest.mark.parametrize("stack", [TurnByTurn(), RunningState()])
def test_the_text_stacks_on_a_perfect_fake_reproduce_the_truth(q, stack):
    for s in scripts_for(q, 2, 4):
        fake = FakeClients(s)
        evs = stack.run(s, q, fake, level="text")
        canned = canned_events(s)
        assert [(e["q"], e["verdict"], e["option"], e["state"]) for e in evs] == \
            [(c["q"], c["verdict"], c["option"], c["state"]) for c in canned]
        assert all(e["t_emitted"] == 0.4 and e["parts"]["wait"] == 0.0 for e in evs)
        assert len(fake.requests) == len(s["turns"])
        assert all(b["system"].startswith("You ") for b in fake.requests)


def test_stack_two_holds_a_window_of_the_transcript(q):
    s = scripts_for(q, 3, 1)[0]
    fake = FakeClients(s)
    RunningState(window=5).run(s, q, fake, level="text")
    last = fake.requests[-1]["messages"][0]["content"].split("Transcript so far (newest last):\n")[1].splitlines()
    assert len(last) == 5 and last[-1].endswith(s["turns"][-1]["text"].strip())
    assert fake.requests[0]["system"] == base.instruction("copilot-state.md")


def test_stack_one_at_the_audio_level_cuts_each_turn_and_transcribes_it(q, audio_run):
    s, clocks, d = audio_run
    fake = FakeClients(s)
    evs = TurnByTurn().run(s, q, fake, level="audio", audio_dir=d, clocks=clocks)
    sent = [r for r in fake.requests if "transcribe" in r]
    assert len(sent) == len(s["turns"]) and all(r["transcribe"] > 44 for r in sent)
    assert sent[0]["keywords"][0] == q["items"][0]["spoken"]["stem"]          # no current item yet: the stems
    assert sent[1]["keywords"][: len(qmod.labels(qmod.by_id(q)[s["turns"][0]["truth"]["q"]]))] == \
        qmod.labels(qmod.by_id(q)[s["turns"][0]["truth"]["q"]])               # then the current item's labels first
    assert all(e["parts"]["transcribe"] == 0.3 and e["parts"]["wait"] > 0 for e in evs)
    assert evs[0]["usage"]["transcribe_s"] > 0


def test_stack_two_speaks_the_realtime_transcription_protocol(q, audio_run):
    s, clocks, d = audio_run
    fake = FakeClients(s)
    evs = RunningState().run(s, q, fake, level="audio", audio_dir=d, clocks=clocks)
    founder, them = fake.sockets
    hello = founder.sent[0]
    assert hello["type"] == "session.update" and hello["session"]["type"] == "transcription"
    inp = hello["session"]["audio"]["input"]
    assert inp["transcription"]["model"] == LIVE_MODEL == "gpt-live-transcribe" and inp["turn_detection"] is None
    assert inp["format"] == {"type": "audio/pcm", "rate": 24_000}
    commits = sum(1 for sock in (founder, them) for m in sock.sent if m["type"] == "input_audio_buffer.commit")
    assert commits == len(s["turns"])
    assert all(m["type"] in ("session.update", "input_audio_buffer.append", "input_audio_buffer.commit")
               for sock in (founder, them) for m in sock.sent)
    assert [e["heard"] for e in evs] == [t["text"] for t in s["turns"]] and founder.closed and them.closed
    assert all(e["usage"]["live_s"] == pytest.approx(2.0) for e in evs)


def test_the_live_transcriber_gives_up_on_a_failed_turn():
    class Failing(FakeRealtime):
        def send(self, raw):
            self.sent.append(json.loads(raw))
            if self.sent[-1]["type"] == "input_audio_buffer.commit":
                self.inbox.append(json.dumps({"type": "conversation.item.input_audio_transcription.failed"}))

    text, _ms = LiveTranscriber(Failing(None)).say(b"\x00\x00" * 2400)
    assert text == ""


def test_stack_three_sends_the_turn_as_audio_and_has_no_text_level(q, audio_run):
    s, clocks, d = audio_run
    fake = FakeClients(s, audio_usage={"prompt_tokens": 900, "completion_tokens": 40,
                                       "prompt_tokens_details": {"audio_tokens": 600}})
    evs = AudioDirect().run(s, q, fake, level="audio", audio_dir=d, clocks=clocks)
    body = fake.requests[0]
    assert body["model"] == "gpt-audio-mini" and body["modalities"] == ["text"]
    part = body["messages"][1]["content"][1]
    assert part["type"] == "input_audio" and part["input_audio"]["format"] == "wav"
    assert body["messages"][0]["content"] == base.instruction("copilot-audio.md")
    assert [(e["q"], e["verdict"]) for e in evs] == [(c["q"], c["verdict"]) for c in canned_events(s)]
    assert evs[0]["usage"] == {"audio_tokens_in": 600, "audio_text_in": 300, "audio_text_out": 40}
    with pytest.raises(SystemExit, match="no text level"):
        AudioDirect().run(s, q, fake, level="text")


def test_the_instructions_use_the_tiers_and_the_verdict_words():
    for name in ("copilot-match.md", "copilot-state.md", "copilot-audio.md"):
        text = base.instruction(name)
        for v in cat.VERDICTS + cat.TIERS + cat.STATES:
            assert f'"{v}"' in text, (name, v)
        assert '{"picks": [n]}' in text and "Output shape:" in text


def test_stacks_are_named_by_number():
    assert parse_stacks(None) == [1, 2, 3] and parse_stacks("2,1") == [1, 2]
    with pytest.raises(SystemExit):
        parse_stacks("4")


# ------------------------------------------------------------------------------------------- FR-6 the scorer

@pytest.fixture(scope="module")
def r2(q):
    return scripts_for(q, 2)


@pytest.fixture(scope="module")
def r4(q):
    return scripts_for(q, 4, 12)


def _events(scripts, change=None):
    out = {}
    for s in scripts:
        evs = canned_events(s)
        if change:
            for i, (t, e) in enumerate(zip(s["turns"], evs, strict=True)):
                change(s, i, t, e, evs)
        out[s["id"]] = evs
    return out


def _readable(t):
    tr = t["truth"]
    return t["who"] == "them" and tr["verdict"] is None and tr["option"] and not tr["option"].get("unclear")


def _answer_offered(s, i):
    return score._offered(score._asking(s["turns"], i, s["turns"][i]["truth"]["q"]))


def _wrong(e):
    if "value" in (e["option"] or {}):
        e["option"] = {"value": 99}
    else:
        e["option"] = {"picks": [6]} if e["option"] != {"picks": [6]} else {"picks": [5]}


FAILS = {
    "A.same_meaning": lambda s, i, t, e, evs: t["truth"]["verdict"] in cat.MEANING_KEPT and e.update(q=None),
    "A.options_own_words": lambda s, i, t, e, evs: t["truth"]["verdict"] == "options_own_words" and e.update(
        verdict="same_meaning"),
    "A.meaning_changed": lambda s, i, t, e, evs: t["truth"]["verdict"] == "meaning_changed" and e.update(
        verdict="same_meaning"),
    "A.precision": lambda s, i, t, e, evs: t["truth"]["verdict"] in cat.QUESTION_VERDICTS and e.update(
        verdict="follow_up"),
    "B.offered": lambda s, i, t, e, evs: _readable(t) and _answer_offered(s, i) and (
        _wrong(e) or e.update(tier="likely")),
    "B.not_offered": lambda s, i, t, e, evs: _readable(t) and not _answer_offered(s, i) and (
        _wrong(e) or e.update(tier="likely")),
    "B.confident_wrong": lambda s, i, t, e, evs: _readable(t) and (_wrong(e) or e.update(tier="sure")),
    "C.tagged": lambda s, i, t, e, evs: t["truth"]["verdict"] == "follow_up" and e.update(q=None),
    "C.boundaries": lambda s, i, t, e, evs: (i + 1 < len(s["turns"]) and t["truth"]["verdict"] == "follow_up"
                                             and s["turns"][i + 1]["truth"]["verdict"] != "follow_up"
                                             and evs[i + 1].update(q=t["truth"]["q"], verdict="follow_up")),
    "D.false_move": lambda s, i, t, e, evs: (t["who"] == "founder" and t["truth"]["verdict"] == "follow_up"
                                             and e.update(verdict="as_written",
                                                          q=next(x for x in ("q1", "q2") if x != t["truth"]["q"]))),
    "D.keys": lambda s, i, t, e, evs: t["truth"]["verdict"] in cat.QUESTION_VERDICTS and e.update(q=None),
    "D.behind_s": lambda s, i, t, e, evs: t["truth"]["verdict"] in cat.QUESTION_VERDICTS and e.update(t_emitted=5.0),
    "E.unsure": lambda s, i, t, e, evs: _readable(t) and e.update(tier="unsure", option={"unclear": True}),
    "E.honest": lambda s, i, t, e, evs: _readable(t) and i % 2 == 1 and e.update(tier="unsure",
                                                                                 option={"unclear": True}),
    "F.late_mapping": lambda s, i, t, e, evs: t["t"] >= score.LATE_S and e.update(q=None),
    "F.limits": lambda s, i, t, e, evs: t["truth"]["state_after"] == "paused" and e.update(state="listening"),
    "G.question_s": lambda s, i, t, e, evs: t["who"] == "founder" and e.update(t_emitted=3.0),
    "G.answer_s": lambda s, i, t, e, evs: t["who"] == "them" and e.update(t_emitted=3.0),
    "G.worst_s": lambda s, i, t, e, evs: i == 0 and s["id"].endswith("1") and e.update(t_emitted=9.0),
}


def test_every_bar_has_a_failing_case():
    assert set(FAILS) == {c for c, *_ in B.BARS}


@pytest.mark.parametrize("cell", [c for c, *_ in B.BARS])
def test_every_bar_passes_on_the_truth_and_fails_when_broken(q, r2, r4, cell):
    scripts, round_ = (r4, 4) if cell.startswith("F.") else (r2, 2)
    good = score.sheet(scripts, _events(scripts), q, round_=round_, level="text", stack="canned", number=0)
    assert good["cells"][cell]["status"] == "ok" and good["cells"][cell]["n"] > 0, good["cells"][cell]
    assert good["certificate"]["verdict"] == "PASS", good["certificate"]["line"]
    bad = score.sheet(scripts, _events(scripts, FAILS[cell]), q, round_=round_, level="text", stack="canned",
                      number=0)
    assert bad["cells"][cell]["status"] == "fail", bad["cells"][cell]
    assert bad["certificate"]["verdict"] == "FAIL"


def test_the_confusion_matrix_is_by_habit_kind(q, r2):
    sh = score.sheet(r2, _events(r2, FAILS["A.options_own_words"]), q, round_=2, level="text", stack="s", number=1)
    row = sh["A"]["confusion"]["options_own_words"]
    assert row["right"] == 0 and row["q_right"] == row["n"] and row["got"] == {"same_meaning": row["n"]}
    assert sh["A"]["options_own_words_rows"]


def test_a_noisy_script_is_reported_not_gated(q, r2):
    broken = _events(r2, FAILS["B.offered"])
    noisy = {s["id"] for s in r2}
    sh = score.sheet(r2, broken, q, round_=2, level="audio", stack="s", number=1, noisy=noisy)
    assert sh["cells"]["B.offered"]["status"] == "not measured" and sh["B"]["noisy"]


# ------------------------------------------------------------------------------------------- the certificate

def test_the_certificate_line(q, r2):
    one = scripts_for(q, 1, 40)
    cert = score.sheet(one, _events(one), q, round_=1, level="text", stack="turn_by_turn", number=1)["certificate"]
    assert cert["verdict"] == "PASS" and cert["line"].startswith(
        "Certificate (the founder's bars, 2026-11-10; round 1, text, stack 1 turn_by_turn): PASS.")
    assert "C.tagged" in cert["not_applicable"] and "F.limits" in cert["not_applicable"]   # R1 gates A, B, E, G
    bad = score.sheet(r2, _events(r2, FAILS["A.precision"]), q, round_=2, level="text", stack="x", number=2)
    assert bad["certificate"]["failing"] == "A.same_meaning"                    # the first failing cell, in order
    assert "the first failing cell is A.same_meaning (same-meaning rewords (and as written) mapped right): 0.0% < 95" \
        in bad["certificate"]["line"]
    tiny = score.sheet(one[:1], _events(one[:1]), q, round_=1, level="text", stack="x", number=1)["certificate"]
    assert tiny["verdict"] == "INCOMPLETE" and "cells not measured" in tiny["line"]
    slow = score.sheet(r2, _events(r2, FAILS["G.answer_s"]), q, round_=2, level="text", stack="x", number=2)
    assert "G.answer_s" in slow["certificate"]["line"] and "3.0 > 2" in slow["certificate"]["line"]


def test_the_bars_are_the_pages():
    bars = {c: (o, b) for c, o, b, _ in B.BARS}
    assert bars["A.same_meaning"] == (">=", 95.0) and bars["A.meaning_changed"] == (">=", 90.0)
    assert bars["B.offered"] == (">=", 100.0) and bars["B.not_offered"] == (">=", 90.0)
    assert bars["B.confident_wrong"] == ("<=", 2.0) and bars["C.boundaries"] == (">=", 85.0)
    assert bars["D.false_move"] == ("<=", 2.0) and bars["E.unsure"] == ("<=", 10.0) and bars["E.honest"] == (">=", 80.0)
    assert bars["G.question_s"] == ("<=", 1.5) and bars["G.answer_s"] == ("<=", 2.0)
    assert bars["G.worst_s"] == ("<=", 4.0)


# ------------------------------------------------------------------------------------------------ the costs

def test_the_cost_arithmetic():
    events = {"s": [{"usage": {"haiku_in": 1_000_000, "haiku_out": 1_000_000, "transcribe_s": 60, "live_s": 120,
                               "audio_tokens_in": 1_000_000, "audio_text_out": 7}}]}
    c = score.costs(events, [{"turns": [{"t": 899}]}])
    assert c["usd"] == {"anthropic": 0.6, "openai_transcribe": 0.0045, "openai_live": 0.034, "openai_audio": 10.0}
    assert c["total_usd"] == pytest.approx(10.6385) and c["call_minutes"] == 15.0
    assert c["per_30_min_call_usd"] == pytest.approx(21.277) and c["unpriced"] == ["audio_text_out"]
    assert writer.cost({"input_tokens": 1_000_000, "output_tokens": 1_000_000}) == 12.0
    assert score.run_costs([{"cost_usd": 0.25}, {"cost_usd": 0.5}], 120) == {"writer_usd": 0.75, "tts_usd": 0.03,
                                                                             "tts_minutes": 2.0}


# --------------------------------------------------------------------------------------- FR-7 the command

@pytest.fixture()
def no_network(monkeypatch):
    import requests

    def refuse(*a, **k):
        raise AssertionError("a network call in an offline test")
    monkeypatch.setattr(requests, "post", refuse)
    monkeypatch.setattr(clients.HttpClients, "realtime", refuse)


def test_dry_runs_with_no_key_and_spends_nothing(tmp_path, no_network, capsys):
    env = {}
    assert bench.run(["--round", "1", "--level", "text", "--dry", "--runs-dir", str(tmp_path)], env=env) == 0
    (run_dir,) = list(tmp_path.glob("*-copilot-bench-r1-text"))
    for name in ("plan.json", "writer.jsonl", "scripts.jsonl", "sample.md", "events.jsonl", "transcripts.jsonl",
                 "sheet.json", "sheet.md", "register-row.md", "page/index.html", "sheet-1-turn_by_turn.json",
                 "sheet-2-running_state.md", "sheet-3-audio_direct.json"):
        assert (run_dir / name).is_file(), name
    assert (run_dir / "audio").is_dir() and not list((run_dir / "audio").iterdir())
    assert len((run_dir / "scripts.jsonl").read_text().splitlines()) == 3
    assert (run_dir / "sample.md").read_text().count("\n## r1-") == 3
    assert not (tmp_path / report.REGISTER).exists()                           # DRY appends no register row
    sheet = json.loads((run_dir / "sheet.json").read_text())
    assert sheet["dry"] and [s["number"] for s in sheet["stacks"]] == [1, 2, 3]
    assert sheet["run_cost"] == {"writer_usd": 0.0, "tts_usd": 0.0, "tts_minutes": 0.0}
    assert all(s["cost"]["total_usd"] == 0 for s in sheet["stacks"])
    out = capsys.readouterr().out
    assert out.count("Certificate (the founder's bars") == 3


@pytest.mark.parametrize("round_", ["2", "4"])
def test_dry_runs_every_round(tmp_path, no_network, round_):
    assert bench.run(["--round", round_, "--level", "audio", "--dry", "--runs-dir", str(tmp_path)], env={}) == 0


def test_a_paid_run_is_refused_by_name_without_both_keys(tmp_path, no_network):
    with pytest.raises(SystemExit) as refused:
        bench.run(["--round", "1", "--level", "text", "--runs-dir", str(tmp_path)],
                  env={"KEEL_OPENAI_API_KEY": "sk-secret-151"})
    assert "KEEL_ANTHROPIC_API_KEY" in str(refused.value) and "sk-secret-151" not in str(refused.value)
    assert not list(tmp_path.iterdir())
    assert clients.keys_from({"KEEL_OPENAI_API_KEY": "a", "KEEL_ANTHROPIC_API_KEY": "b"}) == {"openai": "a",
                                                                                            "anthropic": "b"}


def test_sample_stops_before_any_stack(tmp_path, monkeypatch, no_network, q):
    calls = []

    monkeypatch.setattr(bench.writer, "ModelWriter", lambda c, qq, name: writer.FakeWriter(qq, name))
    class Never:
        levels = ("text", "audio")

        def __init__(self):
            calls.append(1)

    monkeypatch.setattr(bench, "STACKS", {n: Never for n in (1, 2, 3)})
    env = {"KEEL_OPENAI_API_KEY": "a", "KEEL_ANTHROPIC_API_KEY": "b"}
    assert bench.run(["--round", "1", "--level", "text", "--limit", "5", "--sample", "2", "--runs-dir",
                      str(tmp_path)], env=env) == 0
    (run_dir,) = list(tmp_path.glob("*-copilot-bench-r1-text"))
    assert (run_dir / "sample.md").read_text().count("\n## r1-") == 2 and not (run_dir / "events.jsonl").exists()
    assert calls == []


def test_the_paid_command_runs_nowhere_but_its_own_target():
    make = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    targets = {m.group(1): m.group(2) for m in re.finditer(r"^([a-z-]+):[^\n]*\n((?:\t[^\n]*\n)+)", make, re.M)}
    body = targets["copilot-bench"]
    assert "evals.copilot.bench" in body and "KEEL_ANTHROPIC_API_KEY" in body and "KEEL_OPENAI_API_KEY" in body
    assert '[ -z "$(DRY)" ]' in body and "$(if $(DRY),--dry,)" in body
    for name in ("eval", "unit", "eval-all", "matrix-check", "noise-check"):
        assert "copilot-bench" not in targets.get(name, "") and "evals.copilot" not in targets.get(name, ""), name
    assert "copilot-bench" in make.split("\n\n")[1]                            # in .PHONY
    assert not list(HERE.rglob("test_*.py"))                                  # nothing `make eval` would collect
    for path in (REPO_ROOT / "matrix").glob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")   # (Copilot the host CLI is a matrix axis)
            assert "copilot-bench" not in text and "evals.copilot" not in text, path


def test_agents_md_names_the_bench_beside_the_noise_certificate():
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    noise_at, bench_at = agents.index("**The noise-capture certificate**"), agents.index("**The copilot call bench**")
    assert 0 < bench_at - noise_at < 3000
    para = agents[bench_at:bench_at + 3000]
    for name in ("make copilot-bench", "evals/copilot/writer.py", "copilot-match.md", "copilot-state.md",
                 "copilot-audio.md", "evals/copilot/stacks/", "KEEL_OPENAI_API_KEY", "KEEL_ANTHROPIC_API_KEY",
                 "tests/test_copilot_bench.py", "DRY=1"):
        assert name in para, name
    assert "four named places" in agents                                       # argued beside, not a fifth


def test_the_page_carries_every_stack_and_script(q, tmp_path):
    scripts = scripts_for(q, 1, 3)
    events = {n: _events(scripts) for n in (1, 2)}
    sheets = [score.sheet(scripts, events[n], q, round_=1, level="audio", stack=f"s{n}", number=n) for n in (1, 2)]
    path = report.page(tmp_path, sheets, scripts, events, audio=True)
    text = path.read_text(encoding="utf-8")
    assert text.count("<audio controls") == 2 * len(scripts) and all(s["id"] in text for s in scripts)
    assert "prefers-color-scheme: dark" in text


def test_tts_retries_a_read_timeout(tmp_path, monkeypatch):
    import requests
    import numpy as np
    import soundfile as sf
    from evals.noise import synth
    calls = []
    wav = tmp_path / "ok.wav"
    sf.write(wav, np.zeros(2400, dtype="float32"), 24000)

    class R:
        status_code, content = 200, wav.read_bytes()
        def raise_for_status(self): pass

    def post(*a, **k):
        calls.append(1)
        if len(calls) < 3:
            raise requests.ConnectionError("Read timed out.")
        return R()
    monkeypatch.setattr(requests, "post", post)
    monkeypatch.setattr("time.sleep", lambda s: None)
    synth.KEY = "x"
    synth.tts("hello", "alloy", tmp_path / "out.wav")
    assert len(calls) == 3 and (tmp_path / "out.wav").exists()
