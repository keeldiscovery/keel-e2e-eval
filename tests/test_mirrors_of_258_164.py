"""Spec 164: the mirrors of keel-web 258 -- the stranger-side reads of spec 161 moved to the screens 258 drew, with no
stack: the card's walked record read by passage kind (FR-2), the card's machine (two follow-ups a call, Frequency's
`also`, the gate's follow-up on a No), Frequency's digits on the card, the founder's page as drawn (the Frequency chart,
the ways panel, Insights' `capped`, the breakdown on bands), the fake's `owed` on `recency`, the list's nesting."""

from __future__ import annotations

from evals import report_marks as rm
from evals import three_views_strangers as strangers
from harness import interviewer_fake as fake
from harness import story_screens as ss
from harness import three_surfaces as ts

SCREENER = "Do you work at a company with more than 50 employees?"
FREQ_Q = "When you check the rota before it goes out, how often does it happen?"
IMP_Q = "Of the things you do as a plot keeper, which would you most like made easier?"
IMP_ROWS = ["Running the month-end reports", "Checking the rota before it goes out", "Keeping the forms up to date"]


def _script(*, gate_follow_up: bool = True) -> dict:
    gate = {"kind": "gate", "itemId": "g", "dimension": ts.PREVALENCE, "stem": ts.GATE_WORDS,
            "spoken": {"stem": ts.GATE_WORDS}, "condition": {"question": SCREENER, "inCodes": ["yes"]},
            "options": [{"optionId": "YES", "label": "Yes"}, {"optionId": "NO", "label": "No"}],
            "story": {"prompt": "Tell me about it."}}
    if gate_follow_up:
        gate["followUp"] = {"against": ["NO"], "hint": {"first": ts.PREVALENCE_WHY, "third": ts.PREVALENCE_WHY}}
    freq = {"kind": "item", "itemId": "i1", "dimension": ts.FREQUENCY, "control": "choice", "picks": 1,
            "stem": FREQ_Q, "spoken": {"stem": FREQ_Q},
            "options": [{"optionId": c, "label": x} for c, x in zip(ts.FREQUENCY_CODES, ts.FREQUENCY_LABELS)],
            "followUp": {"against": ["about_half", "now_and_then"],
                         "hint": {"first": ts.DIFFERENCE_WHY, "third": ts.DIFFERENCE_WHY},
                         "also": {"on": ["never"], "hint": {"first": ts.NEVER_WHY, "third": ts.NEVER_WHY}}}}
    imp = {"kind": "item", "itemId": "i2", "dimension": ts.IMPORTANCE, "control": "choice", "picks": 2,
           "stem": IMP_Q, "spoken": {"stem": IMP_Q},
           "options": [{"optionId": f"r{i}", "label": x} for i, x in enumerate(IMP_ROWS)],
           "followUp": {"against": ["r0", "r2"], "hint": {"first": "What mattered more to you?",
                                                          "third": "What mattered more to you?"}}}
    return {"passages": [{"kind": "intro"}, gate, freq, imp, {"kind": "pilot", "itemId": "p",
                                                            "question": {"first": "Would you try it?"}}]}


def _strips(passages: list[dict], reads: list[tuple[str, str, list[str], list[str]]]) -> list[dict]:
    """Strips as `copilot_walk` keeps them: `(phase, read, options, badges)`, each read as its passage."""
    out = []
    for phase, read, options, badges in reads:
        p = ts.passage_of(read, passages) if phase == "reading" else None
        out.append({"phase": phase, "head": "", "read": read, "options": options, "badges": badges,
                    "passage_kind": (p or {}).get("kind"), "passage_item": (p or {}).get("itemId"),
                    "passage_dimension": (p or {}).get("dimension")})
    return out


# ------------------------------------------------------------------------------------------- FR-2 the walked record

def test_the_cards_passages_put_the_condition_before_the_gate_and_the_check_where_no_gate_is():
    kinds = [p["kind"] for p in ts.card_passages(_script())]
    assert kinds == ["intro", "condition", "gate", "item", "item", "pilot"]
    money = {"passages": [{"kind": "intro"}, {"kind": "reveal"}, {"kind": "item", "itemId": "x", "stem": "Who pays?"}]}
    assert [p["kind"] for p in ts.card_passages(money, check="Does your team have this problem?")] == \
        ["intro", "check", "reveal", "item"]
    assert [p["kind"] for p in ts.card_passages(money)] == ["intro", "reveal", "item"]


def test_the_cards_walked_record_reads_each_strip_by_its_passage_not_its_place():
    """The run of record of 2026-11-24: the card's strips were keyed by their place (`?`, `1`, `2`) and the intro was
    read as the gate. Read by passage, the intro is passed over and the gate is the gate."""
    passages = ts.card_passages(_script())
    strips = _strips(passages, [
        ("reading", "Tell Tom the problem you are looking into.", [], []),
        ("reading", SCREENER, ["Yes", "No"], ["A", "B"]),
        ("reading", ts.GATE_WORDS, ["Yes", "No"], ["A", "B"]),
        ("reading", FREQ_Q, list(ts.FREQUENCY_LABELS), list(ts.FREQUENCY_DIGITS)),
        ("reading", IMP_Q, IMP_ROWS, ["A", "B", "C"]),
        ("follow-up", "What mattered more to you?", [], []),
        ("reading", "Would you try it?", ["Yes", "No"], ["A", "B"])])
    record = ts.strips_record(strips)
    assert [s["step"] for s in record] == ["screener", "gate", ts.FREQUENCY, ts.IMPORTANCE]
    gate = record[1]
    assert (gate["words"], gate["options"]) == (ts.GATE_WORDS, ["Yes", "No"])
    assert record[3]["follow_ups"] == ["What mattered more to you?"]
    orb = [ts.step("screener", SCREENER, ["Yes", "No"]), ts.step("gate", ts.GATE_WORDS, ["Yes", "No"]),
           ts.step(ts.FREQUENCY, FREQ_Q, list(ts.FREQUENCY_LABELS)),
           ts.step(ts.IMPORTANCE, IMP_Q, IMP_ROWS, ["What mattered more to you?"])]
    assert ts.same_script({"orb": orb, "face": orb, "card": record})["same"] is True
    assert ts.gate_words(record) == ts.GATE_WORDS


def test_a_strip_no_passage_reads_is_never_a_step():
    passages = ts.card_passages(_script())
    strips = _strips(passages, [("reading", "Something the script does not say.", ["Yes"], ["A"])])
    assert strips[0]["passage_kind"] is None and ts.strips_record(strips) == []


# ------------------------------------------------------------------------------------------- mirror 7 the card's machine

def test_the_cards_machine_opens_two_follow_ups_a_call_and_the_second_stem_on_never():
    passages = ts.card_passages(_script())
    assert ts.card_follow_ups(passages, [("g", ["YES"]), ("i1", ["about_half"]), ("i2", ["r0"])]) == [
        {"itemId": "i1", "hint": ts.DIFFERENCE_WHY}, {"itemId": "i2", "hint": "What mattered more to you?"}]
    assert ts.card_follow_ups(passages, [("g", ["YES"]), ("i1", ["never"]), ("i2", ["r1"])]) == [
        {"itemId": "i1", "hint": ts.NEVER_WHY}]
    assert ts.card_follow_ups(passages, [("g", ["YES"]), ("i1", ["every_time"]), ("i2", ["r1"])]) == []
    # a pick-two opens it only when every pick went against
    assert ts.card_follow_ups(passages, [("i2", ["r0", "r1"])]) == []
    # the gate's No with a follow-up opens it at once; two a call at most
    assert ts.card_follow_ups(passages, [("g", ["NO"]), ("i2", ["r0"]), ("i1", ["about_half"])]) == [
        {"itemId": "g", "hint": ts.PREVALENCE_WHY}, {"itemId": "i2", "hint": "What mattered more to you?"}]
    assert ts.CARD_MAX_FOLLOW_UPS == 2


def test_a_no_on_a_gate_with_a_follow_up_goes_on_to_importance_alone():
    assert ts.card_no_path(ts.card_passages(_script())) == ["followUp", ts.IMPORTANCE, "pilot"]
    assert ts.card_no_path(ts.card_passages(_script(gate_follow_up=False))) == ["screened"]
    passages = ts.card_passages(_script(gate_follow_up=False))
    assert ts.card_follow_ups(passages, [("g", ["NO"])]) == []


# ------------------------------------------------------------------------------------------- mirror 6 the digits

def test_frequencys_bubbles_carry_the_digits_and_every_other_question_letters():
    passages = ts.card_passages(_script())
    good = _strips(passages, [("reading", FREQ_Q, list(ts.FREQUENCY_LABELS), list(ts.FREQUENCY_DIGITS)),
                              ("reading", IMP_Q, IMP_ROWS, ["A", "B", "C"])])
    assert ts.badge_faults(good) == []
    lettered = _strips(passages, [("reading", FREQ_Q, list(ts.FREQUENCY_LABELS), ["A", "B", "C", "D", "E"])])
    assert ts.badge_faults(lettered)[0]["want"] == ["1", "2", "3", "4", "5"]
    digits = _strips(passages, [("reading", IMP_Q, IMP_ROWS, ["1", "2", "3"])])
    assert ts.badge_faults(digits)[0]["want"] == ["A", "B", "C"]


def test_the_orbs_rows_are_kept_for_the_card_to_answer_on():
    rows = [{"screen": "question", "key": "gate", "options": [], "said": "yes"},
            {"screen": "question", "key": ts.FREQUENCY, "options": list(ts.FREQUENCY_LABELS), "said": "B",
             "want_lit": "BMost times"},
            {"screen": "question", "key": ts.IMPORTANCE, "options": IMP_ROWS, "said": IMP_ROWS[0]},
            {"screen": "question", "key": "solution.compatibility", "options": ["Yes", "No"], "said": "tap: No"}]
    assert strangers.answered_rows(rows) == {ts.FREQUENCY: 1, ts.IMPORTANCE: 0, "solution.compatibility": 1}


def test_the_wire_only_path_of_a_keel_web_before_258_is_retired():
    for name in ("pending_258", "pending_check", "SCREEN_CHECKS_258"):
        assert not hasattr(strangers, name), name


# ------------------------------------------------------------------------------------------- mirrors 2-5, 9: the page drawn

def _frequency_row() -> dict:
    return {"dimension": ts.FREQUENCY,
            "chart": {"frequency": {"forCodes": list(ts.FOR_CODES), "share": 0.4, "n": 5, "founderBand": "6 or 7 in 10"}},
            "choice": {"optionCounts": [{"code": c, "label": x, "count": n} for c, x, n in
                                        zip(ts.FREQUENCY_CODES, ts.FREQUENCY_LABELS, (1, 1, 1, 1, 1))]}}


def test_frequencys_chart_is_five_bands_two_for_the_founder_and_its_caption():
    row = _frequency_row()
    drawn = {"chart": "frequency", "frequency_caption": "2 of 5 said most times or every time · you said 6 or 7 in 10",
             "bars": [{"label": x, "count": "1", "for": i < 2} for i, x in enumerate(ts.FREQUENCY_LABELS)]}
    assert ts.frequency_chart_faults(drawn, row) == []
    window = dict(drawn, chart="window-ladder")
    assert ts.frequency_chart_faults(window, row)[0] == {"chart": "window-ladder", "want": "frequency"}
    wrong = dict(drawn, bars=[dict(b, **{"for": True}) for b in drawn["bars"]], frequency_caption="2 of 5")
    kinds = [next(iter(f)) for f in ts.frequency_chart_faults(wrong, row)]
    assert kinds == ["data-for", "caption"]


def test_the_ways_panel_as_drawn():
    ways = {"state": "GROUPED", "read": 4, "groups": [{"label": "Check it line by line", "count": 2, "founders": True},
                                                      {"label": "A colleague checks the numbers", "count": 1},
                                                      {"label": "ON_THEIR_OWN", "count": 1}]}
    drawn = {"present": True, "after_prevalence": True, "head": "How they do it today",
             "line": "read from the 4 experiences, not asked", "reading": None,
             "rows": [{"label": "Check it line by line", "founders": True, "yours": "your way", "n": "2"},
                      {"label": "A colleague checks the numbers", "founders": False, "yours": None, "n": "1"},
                      {"label": "On their own", "founders": False, "yours": None, "n": "1"}]}
    assert ts.ways_panel_faults(drawn, ways) == []
    assert ts.ways_panel_faults(dict(drawn, after_prevalence=False, before="problem.frequency"), ways)[0]["place"]
    grouping = {"present": True, "after_prevalence": True, "head": "How they do it today", "reading": "Reading …",
                "rows": []}
    assert ts.ways_panel_faults(grouping, {"state": "GROUPING", "read": 4, "groups": []}) == []
    assert ts.ways_panel_faults({"present": False}, None) == []
    assert ts.ways_panel_faults({"present": False}, ways) == [{"panel": "not drawn", "ways": ways}]
    assert ts.ways_read_from(1) == "read from the 1 experience, not asked"


def test_the_breakdowns_frequency_is_its_bands_and_no_current_solution_row():
    facts = {"problem": {"frequency": {"n": 5, "mostOrEvery": 2, "bands": [
        {"code": c, "label": x, "count": n} for c, x, n in zip(ts.FREQUENCY_CODES, ts.FREQUENCY_LABELS, (4, 5, 1, 0, 2))]}}}
    want = "Every time 4 · Most times 5 · About half the time 1 · Now and then 0 · Never 2"
    assert rm.breakdown_frequency(facts) == want
    assert rm.breakdown_faults([{"key": ts.FREQUENCY, "facts": want}], facts) == []
    assert rm.breakdown_faults([{"key": ts.FREQUENCY, "facts": "2.5 months out of 3"}], facts)[0]["want"] == want
    assert rm.breakdown_faults([{"key": rm.CURRENT_SOLUTION, "facts": None}], facts)
    assert rm.breakdown_frequency({"problem": {"frequency": {"middle": "2.5 months out of 3"}}}) == "2.5 months out of 3"


def test_insights_capped_in_place_of_took_by():
    assert fake.insights_capped(1, 3) == "1 of the 3 was past the two-question cap"
    assert rm.capped_line({"capped": 2, "against": 6}) == "2 of the 6 were past the two-question cap"
    box = rm.expected_box({"dimension": ts.FREQUENCY, "name": "Frequency", "status": "PEOPLE_DISAGREE",
                           "state": "RAW", "capped": 1, "against": 3, "asked": 2, "quotes": [], "rawQuotes": []})
    assert box["capped"] == "1 of the 3 was past the two-question cap" and "took_by" not in box


# ------------------------------------------------------------------------------------------- mirror 8, mirror 10

def test_owed_on_recency_false_is_prevalence_first_and_importance_alone():
    founder = fake.Founder(importance_item="own")
    picks = [{"dimension": "problem.importance", "codes": ["rival_1"], "chip": None},
             {"dimension": "solution.compatibility", "codes": ["no"], "chip": None}]
    assert fake.owed(picks, founder, b2b=True, recency=False) == [("problem.prevalence", False),
                                                                    ("problem.importance", False)]
    assert fake.owed(picks, founder, b2b=True, recency=False, asked=("problem.prevalence",)) == [
        ("problem.importance", False)]
    assert fake.first_rung(picks, founder, b2b=True, recency=False) == "problem.prevalence"
    assert ("problem.prevalence", False) not in fake.owed(picks, founder, b2b=True)


def test_the_list_nests_a_problem_project_before_the_lock():
    solution = {"projectId": "s", "lineage": {"problemProjectId": "p"}}
    for status in ("defined", "calibrating", "calibrated"):
        row = {"projectId": "p", "definition": {"status": status}}
        assert ss.parent_of(row, [solution, row]) is solution
    locked = {"projectId": "p", "definition": {"status": "locked"}}
    assert ss.parent_of(locked, [solution, locked]) is None


def test_a_posted_frequency_is_read_back_to_its_band():
    interview = {"parts": [{"items": [{"itemId": "i1", "dimension": ts.FREQUENCY,
                                       "options": [{"optionId": f"o{i}", "label": x}
                                                   for i, x in enumerate(ts.FREQUENCY_LABELS)]}]}]}
    assert ts.frequency_code_of(interview, {"answers": [{"itemId": "i1", "optionIds": ["o1"]}]}) == "most_times"
    assert ts.frequency_code_of(interview, {"answers": []}) is None


def test_the_invitation_of_a_link_made_on_send_more():
    made = {"url": "https://x/i/t2", "batch": {"links": [{"invitationId": "a", "url": "https://x/i/t1"},
                                                          {"invitationId": "b", "url": "https://x/i/t2"}]}}
    assert strangers.made_invitation(made) == "b"
    assert strangers.made_invitation({"url": "u", "batch": {"links": [{"invitationId": "c"}]}}) == "c"
    assert strangers.made_invitation({"url": "u", "batch": {}}) is None


class _Run:
    def __init__(self, walks):
        self.__dict__["study_walks"] = {"problem": walks}

    def get(self, path):
        return {}


def test_the_studys_other_yes_sayers_count_on_the_founders_page():
    interview = {"parts": [{"items": [{"itemId": "i1", "dimension": ts.FREQUENCY,
                                       "options": [{"optionId": f"o{i}", "label": x}
                                                   for i, x in enumerate(ts.FREQUENCY_LABELS)]}]}]}
    walks = [{"url": "u1", "interview": interview, "invitation": "v1",
              "sent": {"recency": True, "story": "It happened.", "answers": [{"itemId": "i1", "optionIds": ["o1"]}]}},
             {"url": "u2", "interview": interview, "invitation": "v2",
              "sent": {"recency": True, "anchorChip": "CANT_RECALL", "answers": []}},
             {"url": "u3", "interview": interview, "invitation": "v3", "sent": {"recency": False, "answers": []}}]
    assert strangers.other_yes_sayers(_Run(walks), "p", "problem") == {"picks": ["most_times"],
                                                                        "stories": [("v1", "It happened.")]}


def test_the_cards_question_is_its_anchor_then_its_stem():
    strips = [{"phase": "reading", "read": "Would it have helped you?", "anchor": "Think of the last time.",
               "options": ["A lot better"], "passage_kind": "item", "passage_dimension": "solution.relative_advantage"}]
    assert ts.strips_record(strips)[0]["words"] == "Think of the last time. Would it have helped you?"


def test_a_walked_why_is_compared_by_where_it_is_asked_not_its_words():
    orb = [ts.step(ts.IMPORTANCE, IMP_Q, IMP_ROWS, ["You picked filing over checking. Why did that matter more?"])]
    card = [ts.step(ts.IMPORTANCE, IMP_Q, IMP_ROWS, ["What mattered more to you?"])]
    assert ts.same_script({"orb": orb, "card": card}, follow_up_words=False)["same"] is True
    assert ts.same_script({"orb": orb, "card": card})["differs"] == ["follow_ups"]
    none = [ts.step(ts.IMPORTANCE, IMP_Q, IMP_ROWS)]
    assert ts.same_script({"orb": orb, "card": none}, follow_up_words=False)["differs"] == ["follow_ups"]
