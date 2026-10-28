"""Spec 075: the harness follows keel-cloud 139-142 and keel-web 122-124 -- up to two follow-ups, each asked right
after the answer it hangs on, the end's only for a rung still owed (every one under *One more thing* since keel-web
126; *About that* and *One last thing* before); `asked[]` on the
route, `followUps[]` on the response and on `PilotPerson`; the money-only study's one kind; the cost step's *Per* and
*of* and its rate row; the Price step's cost box in hours; Ability to pay said as Keel's reading.

Zero spend: the ladder and the plan offline, the words held to the product checkouts `stack.toml` names, the text
link's follow-up screen read in a real page.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import corpus_scenario as cs
from evals import interviewer_leg as leg
from evals import interviewer_marks as marks
from evals import report_marks
from evals import scope_journey
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from stack.config import load_config

CONFIG = load_config(validate=False)
IMP, CUR, COMPAT, RA, AF = ("problem.importance", "problem.current_solution_satisfaction", "solution.compatibility",
                            "solution.relative_advantage", "solution.adoption_friction")
PRICE, BUYER, FRICTION, COMMIT = ("commercial.price", "commercial.buyer_payer_alignment",
                                  "commercial.purchase_friction", "commercial.commitment")
B2B_ORDER = ["problem.frequency", IMP, CUR, COMPAT, RA, AF]
FOUNDER = fake.Founder(importance_item="own", price_low=None, buyer_supports=("had_to_agree",))


def _web(rel: str) -> str:
    path = Path(CONFIG.keel_web) / rel
    if not path.is_file():
        pytest.skip(f"keel-web has no {rel}")
    return path.read_text(encoding="utf-8")


def _cloud(rel: str) -> str:
    path = Path(CONFIG.keel_cloud) / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    return path.read_text(encoding="utf-8")


def _pick(dimension: str, *codes: str) -> dict:
    return {"dimension": dimension, "codes": list(codes), "chip": None}


# --------------------------------------------------------------------------- FR-1: the ladder, keel-cloud 142 FR-1

def test_the_route_passes_over_what_was_asked():
    picks = [_pick(IMP, "rival_1", "rival_2"), _pick(CUR, "outcome_1"), _pick(COMPAT, "no")]
    assert fake.first_rung(picks, FOUNDER, b2b=True) == IMP
    assert fake.first_rung(picks, FOUNDER, b2b=True, asked=(IMP,)) == CUR
    assert fake.first_rung(picks, FOUNDER, b2b=True, asked=(IMP, CUR)) == COMPAT
    assert fake.first_rung(picks, FOUNDER, b2b=True, asked=(IMP, CUR, COMPAT)) is None
    # the deciding lines still come first; `asked` only takes rungs out of the walk
    assert fake.first_rung(picks, FOUNDER, b2b=True, first=(COMPAT,)) == COMPAT
    assert fake.first_rung(picks, FOUNDER, b2b=True, first=(COMPAT,), asked=(COMPAT,)) == IMP


def test_each_follow_up_is_asked_right_after_its_item_and_two_at_most():
    picks = [_pick(IMP, "rival_1", "rival_2"), _pick(CUR, "outcome_1"), _pick(COMPAT, "no"), _pick(RA, "neutral")]
    plan = fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True)
    assert plan == [{"dimension": IMP, "also": False, "on": IMP}, {"dimension": CUR, "also": False, "on": CUR}]
    assert len(plan) == fake.MAX_FOLLOW_UPS == ivs.MAX_FOLLOW_UPS == marks.MAX_FOLLOW_UPS == 2


def test_an_answer_owing_none_asks_nothing_and_a_later_one_is_asked_on_its_own_item():
    picks = [_pick(IMP, "own", "rival_1"), _pick(CUR, "outcome_5"), _pick(RA, "neutral")]
    assert fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True) == [{"dimension": RA, "also": False, "on": RA}]
    assert fake.asks([_pick(IMP, "own", "rival_1")], FOUNDER, B2B_ORDER, b2b=True) == []


def test_the_last_items_rung_is_asked_on_the_spot_and_the_end_keeps_what_is_owed():
    # the last item's own rung: on the spot (the end's call answers it), and the end asked once more
    picks = [_pick(AF, "no")]
    assert fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True) == [{"dimension": AF, "also": False, "on": AF}]
    # a call held past the beat (`late`): the page went on, the rung stays owed -- the end asks it, *One last thing*
    picks = [_pick(RA, "neutral"), _pick(AF, "yes")]
    assert fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True, late=(RA,)) == [{"dimension": RA, "also": False, "on": None}]
    # one late and one on the last item: the end's call returns the first rung owed (keel-cloud 142 judgement call 2),
    # the earlier one, under *One last thing* -- and after the end's follow-up the response goes (124 FR-2)
    picks = [_pick(RA, "neutral"), _pick(AF, "no")]
    assert fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True, late=(RA,)) == [{"dimension": RA, "also": False, "on": None}]


def test_a_second_stem_is_asked_on_the_spot_too():
    picks = [_pick(AF, "yes_if_worth_it")]
    assert fake.asks(picks, FOUNDER, B2B_ORDER, b2b=True) == [{"dimension": AF, "also": True, "on": AF}]


def test_only_a_rung_the_link_walks_calls_and_none_after_a_skip_counts_less():
    # a decision-maker's link walks the commercial rungs alone: a primary rung's answer is asked nothing
    order = [PRICE, "commercial.ability_to_pay", BUYER, FRICTION, COMMIT]
    picks = [_pick(BUYER, "someone_else_decided"), _pick(FRICTION, "yes_quick"), _pick(COMMIT, "no")]
    plan = fake.asks(picks, FOUNDER, order, "COMMERCIAL_B2B", b2b=True)
    assert [a["dimension"] for a in plan] == [BUYER, FRICTION]
    # where the served rungs are fewer, an item that is none asks nothing; the end's call still walks the ladder
    assert fake.asks(picks, FOUNDER, order, "COMMERCIAL_B2B", b2b=True, rungs=[COMMIT]) == [
        {"dimension": BUYER, "also": False, "on": None}]


def test_the_plan_composes_each_question_and_where_it_hangs():
    corpus, entry = vs.entry_for(CONFIG.keel_cloud, "05-paidly")
    talia = next(p for p in vs.person_inputs(entry) if p.person == "Talia Ben-David")
    interview = {"parts": [{"items": [{"dimension": d, "options": []} for d in B2B_ORDER]}],
                 "followUps": [{"dimension": d} for d in fake.walks("PRIMARY", True)], "occasion": "invoice"}
    plan = vs.follow_up_plan(entry, talia.picks, vs.LINK_PRIMARY, interview, "tok")
    assert [(a["dimension"], a["on"]) for a in plan] == [(IMP, IMP), (CUR, CUR)]
    assert plan[1]["text"] == fake.spoken_of(CUR)                   # keel-cloud 129 FR-3: said as it reads
    # the first rung's call held past the beat: every later call returns that earlier rung, so nothing more is asked on
    # the spot and the end asks it
    late = vs.follow_up_plan(entry, talia.picks, vs.LINK_PRIMARY, interview, "tok", late=(IMP,))
    assert [(a["dimension"], a["on"]) for a in late] == [(IMP, None)]
    assert vs.LATE_FOLLOW_UPS == {"05-paidly": ("Wen Zhang",)}


# ------------------------------------------------------------------------------ FR-1: the words, keel-web 124

def test_the_one_kicker_and_the_cap_are_keel_webs():
    """Spec 075 FR-5 (keel-web 126 FR-5): one kicker, *One more thing*, on the spot and at the end -- the spot's
    `FOLLOW_UP_SPOT_KICKER` is gone from keel-web, and from the harness's three copies."""
    text = _web("src/lib/translate.ts")
    assert re.search(r'export const FOLLOW_UP_KICKER = "([^"]*)";', text).group(1) == ivs.FOLLOW_UP_KICKER \
        == fake.FOLLOW_UP_KICKER == marks.FOLLOW_UP_KICKER == "One more thing"
    assert "FOLLOW_UP_SPOT_KICKER" not in text
    assert not any(hasattr(m, "FOLLOW_UP_SPOT_KICKER") for m in (ivs, fake, marks))
    flow = _web("src/lib/aiInterviewFlow.ts")
    assert re.search(r"export const MAX_FOLLOW_UPS = (\d+);", flow).group(1) == str(ivs.MAX_FOLLOW_UPS)
    page = _web("src/routes/participant/RespondentInterview.tsx")
    assert "FOLLOW_UP_SPOT_KICKER" not in page and "only={!spot && followUps.length === 1}" in page
    screen = _web("src/components/interview/FollowUpScreen.tsx")
    assert "kicker = FOLLOW_UP_KICKER," in screen
    assert "followUpLine = (rung: string, text: string): string => `${FOLLOW_UP_KICKER} · ${rung}:" in text


def test_the_response_and_the_pilot_person_carry_the_list():
    want = cs._want_follow_ups([{"dimension": IMP}, {"dimension": CUR}, {"dimension": RA}],
                               {IMP: "Those first.", CUR: None, RA: "Fewer emails."})
    assert want == [{"dimension": IMP, "text": "Those first.", "how": "TYPED", "skipped": False},
                    {"dimension": RA, "text": "Fewer emails.", "how": "TYPED", "skipped": False}]
    assert cs._want_follow_ups([{"dimension": IMP}], {IMP: None}) is None            # a skip is not sent
    standings = {"facts": {"cards": [{"key": IMP, "name": "Importance"}, {"key": CUR, "name": "Current solution"}]}}
    person = {"invitationId": "i", "name": "Tom", "link": "PRIMARY", "gate": True, "answers": [],
              "followUps": [{"dimension": IMP, "text": "a"}, {"dimension": CUR, "text": "b"}],
              "followUp": {"dimension": IMP, "text": "a"}}
    inside = report_marks.expected_person(standings, person)["inside"]
    assert inside[-6:] == ["One more thing", "Importance", "a", "One more thing", "Current solution", "b"]
    # a read before contract 41: the one `followUp`
    old = dict(person, followUps=None)
    assert report_marks.expected_person(standings, old)["inside"][-3:] == ["One more thing", "Importance", "a"]
    assert cs.follow_up_line("Importance", "a") == "One more thing · Importance: \u201ca\u201d"


def test_the_stored_follow_ups_read_the_list_of_document_32():
    source = inspect.getsource(__import__("stack.ledger", fromlist=["x"]).stored_follow_ups)
    assert "->'followUps' AS" in source and "->'followUp' AS follow_up" in source and "[row[\"follow_up\"]]" in source


def test_the_wire_legs_send_the_list_and_never_the_old_one():
    recorded = inspect.getsource(leg._recorded_follow_up)
    assert 'body["followUps"] = [one]' in recorded and '"asked": [owed["dimension"]]' in recorded
    assert '"followUps": [one, dict(one, text="y")]' in recorded                      # two on one rung: 422
    assert inspect.getsource(cs._normal_body).count('"followUps"') == 1


# --------------------------------------------------------------------- FR-1: the text link's screen, in a page

class _Reply:
    def __init__(self, status: int, body: dict, sent: dict):
        self.status = status
        self._body = body
        self.request = SimpleNamespace(post_data_json=sent)

    def json(self):
        return self._body


SCREEN = """
<main class="iv-body iv-follow-up" data-testid="iv-follow-up">
  <p class="iv-kicker">{kicker}</p><h1 class="iv-q">{question}</h1>
  <p class="iv-note">In your own words. A sentence or two is plenty.</p>
  <div class="sot" data-state="idle"><textarea aria-label="Your answer"></textarea>
    <div class="sot__bar"><span>{hint}</span></div></div>
  <button type="button" class="btn link" data-testid="iv-follow-up-skip"
          onclick="document.body.innerHTML='<h1 class=iv-q>Next one?</h1>'">Skip this one</button>
  <button type="button" class="btn primary" disabled
          onclick="window.__typed=document.querySelector('textarea').value;document.body.innerHTML='<h1 class=iv-q>Next one?</h1>'">Continue</button>
</main>
<script>window.__typed = null; document.querySelector('textarea').addEventListener('input', (e) => {{
  document.querySelector('.btn.primary').disabled = !e.target.value.trim(); }});</script>
"""


def _screen_walk(page, on: str | None, question: str, rung: str, lines, *, hint: str = "", line_for=None):
    page.set_content(SCREEN.format(kicker=ivs.FOLLOW_UP_KICKER, question=question, hint=hint))
    walk = vs_screens.Interview(page, _Recorder())
    walk._lines, walk._line_for, walk.follow_ups_seen, walk.follow_up_seen = lines, line_for, [], None
    walk._route_responses = [_Reply(204, {}, {"answers": []}),
                             _Reply(200, {"dimension": rung, "text": question, "itemId": "f"},
                                    {"answers": [], "asked": [IMP]})]
    walk._responded = False
    drawn = walk._follow_up_screen(on)
    walk._after_follow_up(drawn)
    return drawn, page.evaluate("window.__typed || null")


class _Recorder:
    def step(self, *a, **k):
        import contextlib  # noqa: PLC0415
        return contextlib.nullcontext(SimpleNamespace(add_screenshot=lambda *a: None, capture_text=lambda *a: None))


def test_the_text_links_follow_up_screen_is_read_and_answered_by_its_rung():
    from playwright.sync_api import sync_playwright                         # noqa: PLC0415

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            q = "You said it would not have made much difference. What would have?"
            drawn, typed = _screen_walk(page, RA, q, RA, lambda r: {RA: "Fewer emails."}.get(r))
            assert (drawn["on"], drawn["kicker"], drawn["question"], drawn["rung"]) == (RA, "One more thing", q, RA)
            assert drawn["did"] == "typed" and typed == "Fewer emails." and drawn["only"] is False
            assert drawn["continue_enabled_empty"] is False and drawn["continue_enabled_typed"] is True
            assert drawn["route"]["sent"]["asked"] == [IMP]
            # the end's, with its hint: no line for the rung -> Skip this one
            drawn, typed = _screen_walk(page, None, q, RA, lambda r: None, hint=ivs.FOLLOW_UP_HINT)
            assert (drawn["on"], drawn["did"], drawn["only"], typed) == (None, "skipped", True, None)
            # a line written for another rung is never typed on this one (spec 067 FR-3)
            drawn, typed = _screen_walk(page, RA, q, RA, lambda r: "Mine.", line_for=COMMIT)
            assert drawn["did"] == "skipped" and drawn["line_for"] == COMMIT and typed is None
        finally:
            browser.close()


def test_after_send_the_spot_is_told_from_the_end_by_its_rung():
    """Spec 075 FR-5 (keel-web 126 FR-5): with one kicker, the follow-ups *Send my answers* opens are told apart by the
    rung the route answered -- the last item's own is asked on the spot (`on` that item), any other is the end's."""
    from playwright.sync_api import sync_playwright                         # noqa: PLC0415

    interview = {"parts": [{"items": [{"dimension": IMP}, {"dimension": RA}]}]}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            for rung, want in ((RA, RA), (COMMIT, None)):
                q = f"About {rung}?"
                page.set_content(SCREEN.format(kicker=ivs.FOLLOW_UP_KICKER, question=q, hint=""))
                walk = vs_screens.Interview(page, _Recorder())
                walk._lines, walk._line_for, walk.follow_ups_seen, walk.follow_up_seen = (lambda r: None), None, [], None
                walk._route_responses = [_Reply(200, {"dimension": rung, "text": q, "itemId": "f"},
                                                {"answers": [], "asked": []})]
                walk._responded = False
                walk._end_follow_ups(interview, timeout_s=0.5)
                assert [(d["on"], d["rung"], d["kicker"]) for d in walk.follow_ups_seen] == \
                    [(want, rung, "One more thing")]
        finally:
            browser.close()


def test_a_late_items_call_is_held_past_the_beat():
    assert vs_screens.LATE_FOLLOW_UP_S > ivs.BEAT_MS / 1000
    held = inspect.getsource(vs_screens.Interview._held_route)
    assert "time.sleep(LATE_FOLLOW_UP_S)" in held and "route.continue_()" in held
    walk = inspect.getsource(vs_screens.Interview._items)
    assert 'self._hold_next = item.get("dimension") in self._late_items' in walk


# --------------------------------------------------------------------- FR-1: the AI link's walk, keel-web 124

def test_the_ai_person_is_asked_two_on_the_short_form_and_one_on_the_full():
    source = inspect.getsource(leg._answer_ai_on_screen)
    assert 'want=2 if record.get("short") else 1' in source
    person = inspect.getsource(leg._ai_person)
    assert "against[0]" in person and "fake.LOCK_RULE" in person


def test_the_way_back_is_never_tried_with_an_owed_answer():
    interview = {"followUps": [{"dimension": COMPAT}, {"dimension": CUR}, {"dimension": PRICE}]}
    owes = leg._owes(SimpleNamespace(), interview, "tok")
    item = {"dimension": COMPAT}
    assert owes(item, vs.option_id("tok", COMPAT, "no")) and owes(item, vs.option_id("tok", COMPAT, "only_with_help"))
    assert not owes(item, vs.option_id("tok", COMPAT, "yes_easily"))
    assert owes({"dimension": CUR}, "any") and owes({"dimension": PRICE}, "any")      # read off the founder's own
    assert not owes({"dimension": "problem.frequency"}, "any")                         # no rung on this link
    assert "safe = [i for i in others if not self.owes(" in inspect.getsource(leg._Walk.answer)


def test_end_is_pressed_in_the_second_follow_ups_hold_on_the_said_walk():
    source = inspect.getsource(leg._Walk.follow_up)
    assert 'end_in_hold=by == "said"' in source and 'if met["index"] > 0:' in source
    assert '"want_next"' in source and "_step_after" in inspect.getsource(leg._Walk._silent_window)


# --------------------------------------------------------------------------- FR-2: the founder's screens

def test_the_money_only_walk_holds_one_kind():
    assert "one_kind(j)" in inspect.getsource(scope_journey.walk)
    source = inspect.getsource(scope_journey.one_kind)
    assert "assert kinds == [vs.LINK_B2B]" in source and "[c.get(\"label\") for c in cards] == [decider]" in source


def test_the_cost_step_words_are_keel_webs():
    text = _web("src/lib/translate.ts")
    for name in ("CHAIN_UNIT_HELP", "CHAIN_HOURS_BASE_HELP", "CHAIN_BASE_HELP", "HOURLY_RATE_DEFAULTED"):
        assert re.search(rf'export const {name} = "([^"]*)";', text).group(1) == getattr(vs_screens, name), name
    frame = re.search(r"export const priceCostBox = \(said: string\): string => `([^`]*)`;", text).group(1)
    assert frame.replace("${said}", "{said}") == vs_screens.PRICE_COST_BOX
    control = _web("src/components/calibration/FounderControl.tsx")
    for testid in ("chain-unit", "chain-base", "chain-rate", "chain-low"):
        assert f'"{testid}"' in control, testid
    assert 'id="chain-unit-help"' in control or "chain-unit-help" in control


def test_the_fill_is_keel_clouds_default():
    persona = {"decider": {"role": "Finance manager"}, "problemActor": "payroll practitioner"}
    confirmed = {"state": "CONFIRMED", "occasion": {"noun": "invoice run"}, "fields": {"occasion": "run"}}
    assert cs.chain_fill(persona, confirmed, True) == {"unit": "Finance manager", "base": "invoice run"}
    assert cs.chain_fill(persona, confirmed, False)["unit"] == "payroll practitioner"
    assert cs.chain_fill(persona, {**confirmed, "occasion": {"noun": "Working day"}}, True)["base"] is None
    assert cs.chain_fill(persona, {**confirmed, "occasion": {}}, True)["base"] == "run"
    assert cs.chain_fill(persona, {**confirmed, "state": "DRAFT"}, True)["base"] is None


def test_the_cost_box_on_hours_reads_as_keel_cloud_140_says():
    cost = {"mode": "HOURS", "low": 40, "high": 80, "period": "month"}
    assert cs.hours_cost_box(cost, 80, "$3,200 to $6,400 a month") == \
        "40 to 80 hours a month at $80 an hour, $3,200 to $6,400 a month"
    assert cs.hours_cost_box({**cost, "low": 60, "high": 60}, 80, "$4,800 a month") == \
        "60 hours a month at $80 an hour, $4,800 a month"
    test = _cloud("src/test/java/com/keeldiscovery/cloud/protocol/founder/CostBoxSaysHowTest.java")
    assert "40 to 80 hours a month at $80 an hour, $3,200 to $6,400 a month" in test


def test_ability_to_pay_is_said_as_keels_reading():
    chain = _cloud("src/main/java/com/keeldiscovery/cloud/domain/vectors/CommercialChain.java")
    assert f'KEEL_READS = "{vs_screens.KEEL_READS}"' in chain
    flat = re.sub(r'"\s*\+\s*"', "", chain)
    for b2b, sentence in vs_screens.COUNTS_SENTENCE.items():
        assert sentence in flat, b2b
    for reading in cs.KEEL_READINGS:
        assert reading in chain, reading
    source = inspect.getsource(cs._hold_the_ability_line)
    assert 'said.startswith("You said " + r)' in source and "COUNTS_SENTENCE[vs.is_b2b(j.entry)]" in source


# ---------------------------------------------------------------------------------------- FR-4: nothing else

def test_the_versions_move_as_the_spec_says():
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    from instructions import marks as instruction_marks                 # noqa: PLC0415

    # spec 075 FR-1 moved it to 10; FR-5 (keel-cloud 144, keel-web 126) to 11 -- IM23, IM26, IM27 re-pinned; spec 076
    # FR-5 (keel-cloud 145, keel-web 127) to 12 -- IM22, IM23 (held in test_founder_walk_076.py)
    assert marks.INTERVIEWER_MARKS_VERSION >= 11
    assert instruction_marks.MARKS_VERSION == 21 and corpus_mod.REVISION == 17      # spec 080: r17, v21 stands
