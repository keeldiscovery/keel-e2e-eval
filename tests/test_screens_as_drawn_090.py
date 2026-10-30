"""Spec 090 -- the harness walks the money screens as keel-web 134 draws them, the three controls as keel-web 135 draws
them, the five recorded 0s sent as 1, and Send more's words as keel-web 130 draws them.

FR-1 the cost box asks the mode first under a line that names the cost, who pays it and the core of the loss; the price
shapes are six named choices, each clicked by its own id (`chain-share-COST_BASE` is gone).
"""

from __future__ import annotations

import pytest

from evals import corpus_scenario as cs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.steps import Recorder
from stack.config import load_config


# ------------------------------------------------------------------------------------- FR-1: the money screens

def test_the_modes_are_134s_words():
    """keel-web 134 `CHAIN_COST_MODE_WORD`: *A share they lose* (was *A rate they lose*)."""
    assert vs_screens.CHAIN_MODE_WORD == {"MONEY": "Money they spend", "HOURS": "Time it takes",
                                          "RATE": "A share they lose"}


@pytest.mark.parametrize("payer, core, line", [
    ("the buyer's organisation", "each job", "How would you put the cost of each job to the buyer's organisation?"),
    ("deaf and hard-of-hearing adults", "each conversation",
     "How would you put the cost of each conversation to deaf and hard-of-hearing adults?"),
    (None, "each night", "How would you put the cost of each night?"),
    ("parents of babies", None, "How would you put what it costs parents of babies?"),
    (None, None, "How would you put what it costs them?"),
])
def test_the_line_is_134s_four_forms(payer, core, line):
    """keel-web 134 T003 (`costHowLine`): both parts, the core alone, the payer alone, neither."""
    assert vs_screens.cost_how_line(payer, core) == line


def test_the_lines_parts_are_the_pages_reads():
    """keel-web 134 `costPayer` / `costCore`: the buyer's organisation on B2B (never the people who do the work),
    else the context's people lower-cased as a sentence takes them, an acronym kept; the core *each <occasion>*."""
    context = {"segment": {"core": "Deaf and hard-of-hearing adults"}}
    assert vs_screens.cost_line_parts(True, context, "Conversation") == ("the buyer's organisation", "each conversation")
    assert vs_screens.cost_line_parts(False, context, "conversation") == ("deaf and hard-of-hearing adults",
                                                                         "each conversation")
    assert vs_screens.cost_line_parts(False, {"segment": {"core": "HR leads at startups"}}, None) == (
        "HR leads at startups", None)
    assert vs_screens.cost_line_parts(False, {}, None) == (None, None)


@pytest.mark.parametrize("price, choice", [
    ({"shape": "AMOUNT_PERIOD", "low": 10, "high": 20}, "chain-shape-AMOUNT_PERIOD"),
    ({"shape": "SHARE", "low": 5}, "chain-shape-SHARE"),
    ({"shape": "SHARE", "shareBase": "COST_BASE", "low": 5}, "chain-shape-SHARE"),
    ({"shape": "SHARE", "shareBase": "RECOVERED", "low": 5}, "chain-share-RECOVERED"),
    ({"shape": "UPFRONT_THEN", "upfrontLow": 100, "low": 10}, "chain-shape-UPFRONT_THEN"),
    ({"shape": "UPFRONT_THEN", "upfrontLow": 100, "thenNothing": True}, "chain-then-nothing"),
    ({"shape": "FREE"}, "chain-shape-FREE"),
])
def test_the_price_is_one_of_six_named_choices_clicked_by_its_id(price, choice):
    """keel-web 134 FR-2 (J-4): one click on the choice's own id, then its numbers; `chain-share-COST_BASE` is never
    clicked (gone), nor a shape's first choice before its second outcome."""
    log: list = []

    class Box:
        def __init__(self, key):
            self.key = key

        @property
        def first(self):
            return self

        def count(self):
            return 1

        def click(self):
            log.append(("click", self.key))

        def fill(self, value):
            log.append(("fill", self.key, value))

        def inner_text(self):
            return "per site · a month"

    class Page:
        def get_by_test_id(self, key):
            return Box(key)

        def locator(self, key):
            return Box(key)

    corridor = vs_screens.Corridor.__new__(vs_screens.Corridor)
    corridor.page = Page()
    seen = corridor._chain_price(price)
    clicks = [k for kind, k, *_ in log if kind == "click"]
    assert clicks == [choice] and seen["choice"] == choice
    assert "chain-share-COST_BASE" not in str(log)
    fills = [k for kind, k, *_ in log if kind == "fill"]
    assert fills == {"AMOUNT_PERIOD": ["chain-price-low", "chain-price-high"], "SHARE": ["chain-share"],
                     "UPFRONT_THEN": ["chain-upfront"] + ([] if price.get("thenNothing") else ["chain-plan"]),
                     "FREE": []}[price["shape"]]


@pytest.fixture(scope="module")
def countly():
    _corpus, entry = vs.entry_for(load_config(validate=False).keel_cloud, "01-countly")
    return entry


def _journey(tmp_path, entry, context, persona=None):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=entry,
                   founder=None, people=[], project_id="p1", scope=entry.scope)
    j.get = lambda path: context if path.endswith("/context") else (persona or {})
    return j


CONTEXT = {"state": "CONFIRMED", "segment": {"core": "Payroll practitioners"}, "occasion": {"noun": "payroll run"},
           "fields": {"circumstance": "they close the month and the numbers do not tie"}}


def test_the_mode_first_hold_takes_the_composed_line(tmp_path, countly):
    """FR-1: nothing of *Per* or the periods before the mode; the line is the composed one, never the circumstance."""
    j = _journey(tmp_path, countly, CONTEXT)
    owed, shape = cs.cost_line_owed(vs.is_b2b(countly), CONTEXT, {})
    payer = "the buyer's organisation" if vs.is_b2b(countly) else "payroll practitioners"
    assert owed == f"How would you put the cost of each payroll run to {payer}?" and shape.fullmatch(owed)
    cs._hold_the_mode_first(j, {"order": "mode-first", "before_mode": {"unit": 0, "periods": 0}, "line": owed})


@pytest.mark.parametrize("seen", [
    {"before_mode": {"unit": 1, "periods": 0}},                                     # *Per* drawn before the mode
    {"before_mode": {"unit": 0, "periods": 6}},                                     # the periods before the mode
    {"line": "How would you put what it costs them?"},                              # the old line where both are served
    {"line": "How would you put the cost of when they close the month and the numbers do not tie to them?"},
])
def test_the_mode_first_hold_fails_the_old_order_and_the_old_line(tmp_path, countly, seen):
    owed, _shape = cs.cost_line_owed(vs.is_b2b(countly), CONTEXT, {})
    drawn = {"order": "mode-first", "before_mode": {"unit": 0, "periods": 0}, "line": owed, **seen}
    with pytest.raises(AssertionError):
        cs._hold_the_mode_first(_journey(tmp_path, countly, CONTEXT), drawn)


def test_with_no_context_the_line_names_the_payer_or_nothing(tmp_path, countly):
    """The shorter forms where the wire serves less: no confirmed context -- no core, and the people only on B2B."""
    owed, shape = cs.cost_line_owed(False, {}, {})
    assert owed == vs_screens.CHAIN_COST_HOW and shape.fullmatch(owed)
    owed, shape = cs.cost_line_owed(True, {}, {})
    assert owed == "How would you put what it costs the buyer's organisation?" and shape.fullmatch(owed)


# ------------------------------------------------------------------------- FR-2: the three controls as 135 builds them

import inspect                                                          # noqa: E402

from evals import backtest as bt                                        # noqa: E402
from evals import gallery as g                                          # noqa: E402
from evals import interviewer_leg                                       # noqa: E402
from harness import interviewer_screens as ivs                          # noqa: E402


def test_h1_the_ai_sheets_second_ask_is_read_from_its_own_line():
    """H-1: *And one more?* is `[data-testid=ai-sheet] [data-testid=second-ask]`; `.iv-q` stays the item's question, so
    neither `more_said` nor the loop guard reads `.iv-q` / the status for it."""
    reader = inspect.getsource(ivs.Player.second_ask)
    assert 'get_by_test_id("ai-sheet").get_by_test_id("second-ask")' in reader
    walk = inspect.getsource(interviewer_leg._Walk.tap_one_then_one)
    assert '"more_said": p.second_ask() == one_more' in walk and "vs.ONE_MORE in" not in walk
    assert "p.question() in (question, vs.ONE_MORE)" not in walk
    assert "vs.ONE_MORE" not in inspect.getsource(interviewer_leg._wait_next)


def test_h2_the_first_taps_state_is_read_after_the_more_clip():
    """H-2: `one` (IM20's phase, ring, ticks) is read once the `more` clip has played and the sheet listens; what 1.5 s
    showed is kept as `at_tap_wait`."""
    walk = inspect.getsource(interviewer_leg._Walk.tap_one_then_one)
    tapped, waited, clip, listening, read = (walk.index("p.tap(want[0])"), walk.index("ivs.TAP_WAIT_MS"),
                                             walk.index("_played_at(p, more_clip) < tapped_at"),
                                             walk.index('p.phase() != "listening"'), walk.index("one = {**p.save_state()"))
    assert tapped < waited < clip < listening < read
    assert '"at_tap_wait": at_wait' in walk


def test_h3_h4_importance_with_picks_is_taken_before_the_escape():
    """H-3: a pick with `chip: NOTHING_ELSE` is the pick, then *Nothing else* -- never the first ask's *None of these*
    (`tap_chip` taps the first chip). H-4: one pick by speech is held, the second ask waited for, then *Nothing else*."""
    answer = inspect.getsource(interviewer_leg._Walk.answer)
    chip = answer.index('if ans.get("chip"):')
    assert answer.index("self.tap_one_then_one(") < chip and answer.index("self.one_by_speech(") < chip
    speech = inspect.getsource(interviewer_leg._Walk.one_by_speech)
    assert speech.index("self.held(entry, label)") < speech.index("p.second_ask()") < speech.index(
        "p.tap_chip_named(nothing)") < speech.index("_wait_next(p, entry[\"question\"])")
    assert interviewer_leg.PICK_CONTROLS == ("pick_one_then_one",)


def test_h5_the_hint_is_pick_one_on_importance_and_the_scale():
    """H-5: *Pick one.* (`RESPONDENT_PICK_ONE`) over `pick_one_then_one` and `scale_four`; *Pick two.* is gone."""
    assert vs_screens.IV_PICK_ONE == "Pick one." and not hasattr(vs_screens, "IV_PICK_TWO")
    assert cs.PICK_ONE_HINTED == {"pick_one_then_one", "scale_four"}
    held = inspect.getsource(cs)
    assert 'want["hint"] = vs_screens.IV_PICK_ONE' in held and "IV_PICK_TWO" not in held


def test_h6_h7_h11_the_text_pages_second_ask():
    """H-11: the second ask waited for by its test id; H-6: *2 of 2 picked* read after the second tap; H-7: the pressed
    *Nothing else* read by `aria-pressed`."""
    src = inspect.getsource(vs_screens.Interview._one_then_one)
    wait, second, picked = (src.index('get_by_test_id("second-ask")'), src.index("option(options[ids[1]]).click()"),
                            src.index('"picked_line"'))
    assert wait < second < picked and ".iv-chips button[aria-pressed=true]" in src


def test_h8_no_pick_two_path_is_left():
    """H-8: contract 47 never serves `pick_two` -- the walks' checkbox path, its hint and its counts are gone; the
    module note no longer says tapped checkboxes wait for *Save and next*."""
    assert "pick_two" not in cs.ROW_CONTROLS and "pick_two" not in cs.PICKS_NEEDED
    assert 'role = "radio"' in inspect.getsource(vs_screens.Interview._answer)
    assert "tapped checkboxes wait for *Save and next* (`save_state`)" not in ivs.__doc__


def test_h9_no_advantages_are_read_off_a_47_wire():
    """H-9: an item served on contract 47 is written with no `advantages` (no empty list); a run recorded before 47
    keeps its benefits as recorded."""
    served = {"dimension": "solution.relative_advantage", "question": "Q?", "control": "scale_four",
              "options": [{"optionId": "a", "label": "A lot better"}], "escape": {"label": "I can't tell"}}
    assert "advantages" not in g._item(served, {}) and "advantagesPrompt" not in g._item(served, {})
    row = bt.served_items({"parts": [{"part": 2, "items": [served]}]})["parts"][0]["items"][0]
    assert "advantages" not in row and "advantagesPrompt" not in row
    old = {**served, "advantages": [{"label": "Hours back"}]}
    assert list(g._item(old, {}))[:8] == ["dimension", "kicker", "question", "control", "hint", "options",
                                         "advantages", "escape"]


# ------------------------------------------------------------------------------- FR-4: Send more's words (keel-web 130)

from harness import interviews_screens as iv                            # noqa: E402


def test_send_mores_two_ways_are_130s_words():
    """keel-web 130 FR-5 (`SEND_WHO`): *People I know by name* / *People I found with Keel*; the radio is matched on the
    name's start, the line after it."""
    assert (iv.WHO_OWN, iv.WHO_DATASET) == ("People I know by name", "People I found with Keel")
    src = inspect.getsource(iv.Interviews.send_someone) if hasattr(iv, "Interviews") else inspect.getsource(iv)
    assert 'name=re.compile(rf"^{re.escape(WHO_OWN)}")' in src


@pytest.mark.parametrize("name", ["Would the construction superintendent decide to use and pay for Fresco, or would "
                                  "someone else?", "Would parents of babies under six months decide to use and pay for "
                                  "it, or would someone else?"])
def test_the_persona_question_is_found_by_its_shape(name):
    """keel-web 130 FR-1 (`personaQuestion`): the question names the WHO and the idea; the old question is not it."""
    assert vs_screens.PERSONA_QUESTION.match(name)
    assert not vs_screens.PERSONA_QUESTION.match("Who makes the buying decision?")


@pytest.mark.parametrize("label, same", [("The construction superintendent decides", True),
                                         ("Parents of babies under six months decide", True),
                                         ("Someone else decides", False),
                                         ("The same person would decide to pay", False)])
def test_the_first_option_is_the_actor_deciding(label, same):
    """keel-web 130 FR-1 (`personaSame`, `PERSONA_SOMEONE_ELSE`)."""
    assert bool(vs_screens.PERSONA_SAME.match(label)) is same
    assert vs_screens.PERSONA_SOMEONE_ELSE == "Someone else decides"


@pytest.mark.parametrize("people, title", [
    ("payroll practitioners", "Who should ask payroll practitioners your questions?"),
    ("parents of babies under six months old at home", "Who should ask them your questions?"),   # past ten words
    (None, "Who should ask them your questions?"),
])
def test_l1s_title_names_the_people_within_ten_words(people, title):
    """keel-web 130 FR-2 (`beforeInterviewerTitle`)."""
    assert vs_screens.l1_title(people) == title


def test_the_lock_screens_words_are_130s():
    """keel-web 130 FR-2 / FR-3: *Lock and record {face}*, *Lock and write the questions*, the own-AI line, *Offer a
    pilot?*."""
    assert vs_screens.before_lock_record("Daphne") == "Lock and record Daphne"
    assert vs_screens.BEFORE_LOCK_RECORD.match("Lock and record Saskia")
    assert vs_screens.BEFORE_LOCK_APPROVE == "Lock and write the questions"
    assert vs_screens.BEFORE_INTERVIEWER_OWN.startswith("This account runs on its own AI")
    assert vs_screens.PILOT_TITLE == "Offer a pilot?"


def _l1_journey(tmp_path, countly, core):
    j = cs.Journey(recorder=Recorder(tmp_path), page=None, context=None, web_base="", cloud_base="", entry=countly,
                   founder=None, people=[], project_id="p1", scope=countly.scope)
    j.get = lambda path: {"segment": {"core": core}} if path.endswith("/context") else {}
    j.receipt = {}
    return j


def test_the_l1_holds_take_130s_title(tmp_path, countly):
    j = _l1_journey(tmp_path, countly, "Payroll practitioners")
    drawn = {"counters": cs.before_counters(j.scope), "ready": {"pilot_title": "Offer a pilot?"},
             "l1": {"title": "Who should ask payroll practitioners your questions?", "carousel": False,
                    "sub": vs_screens.BEFORE_INTERVIEWER_OWN, "button": vs_screens.BEFORE_LOCK_APPROVE}}
    cs._keels_door_l1(j, drawn)
    cs._own_door_l1(j, drawn)
    drawn["l1"]["title"] = "Who asks the questions"
    with pytest.raises(AssertionError):
        cs._keels_door_l1(j, drawn)
