"""`instructions/corpus.py` at revision 13 (spec 064: r12's rules and the commercial chain, rule C, where an entry
states it -- the fixture states none, so it reads as r12): the loader on a hand-sized entry (spec 029 FR-006, data-model
§2-§3; T012; at revision 10 by spec 040 T004, judgement call 78; at revision 11 by spec 042, call 110 -- revision
10's rules and r11's K3 / S10 in L; at revision 12 by spec 053 -- r11's rules, the canon in dollars, the fixture
kept GB; earlier revisions by specs 030-038). The file keeps its r11 name (history).

Everything the scorers read off an entry -- the plan, the founder's lists and their tested item, the
vocabulary and its inflection ledger, who is readable -- is checked here on `tests/fixtures/corpus/09-fixture.yaml`,
which a person can count by hand: 12 people, Kit and Lu answer No at the gate, Jo chips, Ivy's story is vague, eight
are anchored; Buyer and payer is left out. And every refusal of revision 10's S / W / L / R / A rules (the shape half
of keel-cloud's `check_corpus_r11.py`) is made to happen once, from a one-line change to that file, naming the entry
and the key -- the registry-free ones on the file alone, the registry-bound ones (a list's `saves`, a row's control,
codes and escape, a pick's code) only once the registry is bound.
"""

from __future__ import annotations

import pytest

from instructions import corpus as corpus_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


def test_the_plan_is_four_three_three(entry):
    plan = entry.plan()
    assert {part: len(keys) for part, keys in plan.items()} == {1: 4, 2: 3, 3: 3}
    assert plan[3] == ["commercial.existing_sacrifice", "commercial.price", "commercial.commitment"]
    assert plan[1][0] == "problem.prevalence", "the gate is Part 1's first item"
    assert "commercial.buyer_payer_alignment" not in plan[3], "left out by the founder"
    assert "commercial.ability_to_pay" not in plan[3], "b2b_link_only, and this entry is B2C"


def test_the_plan_without_a_registry_is_the_files_own_golden_plan():
    unbound = corpus_mod.load_file(fx.ENTRY)
    assert {p: len(k) for p, k in unbound.plan().items()} == {1: 4, 2: 3, 3: 3}


def test_a_b2b_entry_calibrates_thirteen_and_routes_part_three_to_the_decision_maker():
    """Calls 47, 59 and decision 26: Purchase friction calibrated and asked, and Ability to pay asked,
    on COMMERCIAL_B2B; a B2C entry calibrates twelve."""
    b2b = fx.entry(fx.ENTRY_B2B)
    assert len(b2b.calibrated_keys()) == 13 and len(fx.entry().calibrated_keys()) == 12
    assert b2b.link_of(3) == "COMMERCIAL_B2B" and b2b.link_of(1) == "PRIMARY"
    assert b2b.plan()[3] == ["commercial.existing_sacrifice", "commercial.price",
                             "commercial.ability_to_pay", "commercial.purchase_friction",
                             "commercial.commitment"]
    assert [p.person for p in b2b.deciders()] == ["Max Moss", "Nia Noor", "Oz Oduya", "Pip Penn", "Quin Qadir"]


def test_the_window_and_the_occasion_are_revision_tens(entry):
    """Rule W (D13): a window of at least two units, and one time it happens."""
    assert entry.window().to_map() == {"count": 7, "unit": "NIGHTS"}
    assert entry.occasion() == "morning"


def test_the_founders_lists_and_their_tested_items(entry):
    """087 FR-007: a list is `{items, picked, phrase}`; the tested item is the picked one, Importance's own item
    and the Commitment step being item 0 of a list with no pick."""
    compatibility = entry.founder_list("solution.compatibility")
    assert compatibility["picked"] == 0 and len(compatibility["items"]) == 2
    assert entry.tested("solution.compatibility")["code"] == "phone_to_hand"
    assert entry.tested("problem.importance")["code"] == "finding_keys"
    assert entry.founder_list("problem.current_solution_satisfaction")["phrase"] == "your way of finding them"
    assert entry.tested("commercial.commitment")["label"] == "install the app"
    assert entry.founder_list("commercial.buyer_payer_alignment") is None, "left out"
    assert entry.founder_list("problem.frequency") is None, "not a list"
    assert entry.tested("commercial.price") is None


def test_the_price_and_the_ladder_are_read(entry):
    """Call 51: the founder's range, its period and currency; the row the ladder's five bands around a low of 3
    (the 2-5 band in the middle) plus would_not_pay."""
    assert entry.price() == {"low": 3, "high": 5, "period": "month", "currency": "GBP"}
    assert corpus_mod.price_ladder_codes(3) == entry.respondent_questions["commercial.price"]["codes"]
    assert corpus_mod.price_ladder_codes(500) == [
        "under_250", "band_250_500", "band_500_1000", "band_1000_2500", "over_2500", "would_not_pay"]
    assert corpus_mod.price_ladder_codes(1)[:2] == ["under_1", "band_1_2"], "clamped at the foot"
    assert corpus_mod.price_ladder_codes(9999)[-2:] == ["over_10000", "would_not_pay"], \
        "clamped at the head"
    with pytest.raises(ValueError):
        corpus_mod.price_ladder_codes(10000)


def test_the_vocabulary_is_the_mechanisms_stems_and_none_of_the_problems(entry):
    vocabulary = entry.vocabulary()
    assert {"tag", "beep", "whistl", "loud"} <= vocabulary
    for problem_word in ("key", "morn", "door", "commuter", "cycl", "lost"):
        assert problem_word not in vocabulary
    assert entry.mechanism_phrases() == [("key", "ring")]


def test_the_inflection_ledger_carries_the_one_planted_collision(entry):
    ledger = entry.inflection_ledger()
    assert ledger == {"listen": {"mechanism": ["listens"], "problem": ["listened"]}}
    assert "listen" not in entry.vocabulary(), "a tie is the judge's, never a plain fault"


def test_the_one_liner_is_the_golden_mechanisms_four_fields(entry):
    line = entry.mechanism_one_liner()
    for part in ("the commuter", "when the keys are not where they were left",
                 "whistles once", "a beep from the tag"):
        assert part in line


def test_who_is_read_who_passed_the_gate_and_who_answered_at_all(entry):
    assert len(entry.people()) == 12
    assert len(entry.gate_yes()) == 10
    readable = [p.person for p in entry.readable()]
    assert len(readable) == 9
    assert "Jo Judd" not in readable, "a chipped story is GUESSED by code, never read"
    assert "Kit Kerr" not in readable and "Lu Lam" not in readable
    assert "Ivy Ives" in readable, "a vague story without a chip is read -- and is GUESSED"


def test_b2b_is_the_decision_maker_being_a_role(entry):
    assert entry.b2b() is False
    b2b = fx.entry(fx.ENTRY_B2B)
    assert b2b.b2b() is True and b2b.decision_maker_role() == "buyer"


def test_the_hash_and_verify_unchanged_are_unchanged(tmp_path):
    path = fx.write_entry(tmp_path, fx.raw_entry())
    corpus = corpus_mod.Corpus(entries=[corpus_mod.load_file(path)], directory=tmp_path,
                               hashes={str(path): corpus_mod._sha256(path)})
    corpus.verify_unchanged()
    path.write_text(path.read_text() + "\n# moved\n")
    with pytest.raises(corpus_mod.CorpusError, match="changed while the run was in flight"):
        corpus.verify_unchanged()


def _person(raw, name):
    return next(p for p in raw["answers"] if p["person"] == name)


def _fc(raw, key):
    return raw["founder_calibration"][key]


def _items(raw, key):
    return raw["founder_calibration"][key]["answer"]["items"]


def _revision(n, words):
    return (lambda r: r.__setitem__("revision", n),
            f"revision is {n}; this eval reads revision 16 only -- revision {n} is {words}")


#: The registry-free refusals: the file alone is refused.
MUTATIONS = {
    "revision 2": (lambda r: r.__setitem__("revision", 2), "revision is 2"),
    "no revision": (lambda r: r.pop("revision"), "revision is absent"),
    "revision 3": _revision(3, "MARKS_VERSION 9's corpus"),
    "revision 4": _revision(4, "MARKS_VERSION 10's corpus"),
    "revision 5": _revision(5, "MARKS_VERSION 11's corpus"),
    "revision 6": _revision(6, "MARKS_VERSION 12's corpus"),
    "revision 7": _revision(7, "MARKS_VERSION 13's and 14's corpus"),
    "revision 8": _revision(8, "MARKS_VERSION 15's and 16's corpus, before benefit first"),
    "revision 9": _revision(9, "MARKS_VERSION 17's corpus, before the October redesign"),
    # spec 042 call 110: revision 10 refused by name
    "revision 10": _revision(10, "MARKS_VERSION 18's corpus, before keel-cloud 091"),
    # spec 053: revision 11 refused by name, in pounds
    "revision 11": _revision(11, "MARKS_VERSION 19's and 20's corpus, in pounds (six GB entries, before keel-cloud "
                                 "105: 'the currency amount should be dollars')"),
    # spec 064 FR-1: revision 12 refused by name, before the commercial chain
    "revision 12": _revision(12, "MARKS_VERSION 20's corpus, before the commercial chain (keel-cloud 115: a cost "
                                 "with no unit, a price with no shape)"),
    # spec 068 FR-1: revision 15 refused by name, before keel-cloud 129's 112 moved Commitment picks
    "revision 15": _revision(15, "MARKS_VERSION 20's corpus before keel-cloud 129 (112 back-test Commitment picks "
                                 "`yes_after_trying` where the founder's list is the step alone"),
    # r11's two rules in L (keel-cloud 091 FR-G, DRIFT #77): K3 on a face, S10 on Commitment's step
    "a face with no you": (lambda r: _items(r, "solution.compatibility")[0].__setitem__(
        "asked", "was the phone to hand"), "is said to the stranger and carries no 'you' or 'your' (rule L, K3)"),
    "a step that says you": (lambda r: _items(r, "commercial.commitment")[0].__setitem__(
        "label", "introduce you to the IT team"), "carries 'you'; code says it as 'would you {step}' (rule L, S10)"),
    "beliefs": (lambda r: r.__setitem__("beliefs", []), "`beliefs`"),
    "questionnaire": (lambda r: r.__setitem__("questionnaire", {}), "`questionnaire`"),
    "buckets": (lambda r: r["expected"].__setitem__("buckets", {}), "`expected.buckets`"),
    "stages": (lambda r: r["expected"].__setitem__("stages", {}), "`expected.stages`"),
    "anchors": (lambda r: _person(r, "Ann Abbott").__setitem__("anchors", {}), "`anchors`"),
    # rule W (D13)
    "a one-unit window": (lambda r: r["context"].__setitem__("recall_window", {"count": 1, "unit": "MONTHS"}),
                          "context.recall_window: a recall window counts at least 2"),
    "a shift window": (lambda r: r["context"].__setitem__("recall_window", {"count": 7, "unit": "SHIFTS"}),
                       "'SHIFTS' is not a recall-window unit"),
    "the last cycle": (lambda r: r["context"].__setitem__("recall_window", "LAST_CYCLE"),
                       "'LAST_CYCLE' is not a recall window"),
    "no window": (lambda r: r["context"].pop("recall_window"), "context.recall_window is absent"),
    "no occasion": (lambda r: r["context"].pop("occasion"), "context.occasion is None"),
    "an occasion of five words": (lambda r: r["context"].__setitem__("occasion", "a cold wet winter morning"),
                                  "context.occasion is 'a cold wet winter morning'"),
    # rule L, its shape half
    "labels on a founder entry": (lambda r: _fc(r, "problem.prevalence").__setitem__("labels", ["x"]),
                                  "founder_calibration[problem.prevalence] carries `labels` / `units`"),
    "a belief phrase on a reshaped dimension": (
        lambda r: _fc(r, "solution.compatibility").__setitem__("belief_phrase", "a phone to hand"),
        "founder_calibration[solution.compatibility] carries a `belief_phrase`"),
    "a reshaped answer that is a code": (
        lambda r: _fc(r, "problem.importance").__setitem__("answer", "top_three"),
        "founder_calibration[problem.importance].answer is 'top_three'; revision 10 records the founder's list"),
    "an item with no label": (lambda r: _items(r, "problem.importance")[1].pop("label"),
                              "founder_calibration[problem.importance].answer.items[1] is"),
    "a not-sure label": (lambda r: _items(r, "problem.importance")[2].__setitem__("label", "Not sure what else"),
                         "items[2].label 'Not sure what else' carries a not-sure word"),
    "a digit the statements do not carry": (
        lambda r: _items(r, "solution.adoption_friction")[0].__setitem__("label", "Clip 7 tags to the key ring"),
        "carries '7', a number the entry's statements do not"),
    "an asked face with a question mark": (
        lambda r: _items(r, "solution.compatibility")[0].__setitem__("asked", "did you have your phone?"),
        "items[0].asked 'did you have your phone?' is not a clause"),
    "an asked face of 21 words": (
        lambda r: _items(r, "solution.compatibility")[0].__setitem__("asked", " ".join(["you"] * 21)),
        "is not a clause of 1 to 20 words"),
    "a list repeating a code": (lambda r: _items(r, "problem.importance")[1].__setitem__("code", "finding_keys"),
                                "founder_calibration[problem.importance]'s list repeats a code"),
    # rule A, its shape half (D8, D2)
    "a guessed flag": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "commercial.existing_sacrifice", {"mode": "AMOUNT", "value": 20, "currency": "GBP", "period": "month",
                                          "rough": True}),
        "Ann Abbott's commercial.existing_sacrifice pick carries a guessed flag"),
    "something else": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "solution.compatibility", "something_else"), "is 'Something else', which revision 10 deleted"),
    "a frequency above the founder's out of": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("problem.frequency", 8),
        "Ann Abbott's problem.frequency pick is 8; a whole number from 0 to the founder's out of 7"),
    "a frequency that is not a whole number": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("problem.frequency", 2.5),
        "problem.frequency pick is 2.5"),
    # rule B at revision 10
    "a benefit answer that is not a list": (
        lambda r: _fc(r, "solution.relative_advantage").__setitem__("answer", ["shorter_time"]),
        "revision 10 lists one to 4 benefits"),
    "five benefits": (
        lambda r: _fc(r, "solution.relative_advantage").__setitem__(
            "answer", {"items": [{"code": f"b{i}", "label": f"Benefit {chr(97 + i)}"} for i in range(5)]}),
        "revision 10 lists one to 4 benefits"),
    "the old single-choice benefit row": (
        lambda r: r["respondent_questions"]["solution.relative_advantage"].__setitem__("control", "single_choice"),
        "revision 10 asks benefit_with_advantages over"),
    "a benefit pick that is a bare code": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("solution.relative_advantage", "shorter_time"),
        "Ann Abbott's solution.relative_advantage pick is 'shorter_time'; revision 10 answers"),
    "positive without an advantage": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "solution.relative_advantage", {"answer": "positive"}), "exactly under positive"),
    "an advantage the founder did not list": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "solution.relative_advantage", {"answer": "positive", "advantages": ["less_worry"]}),
        "exactly under positive"),
    # r9's money rules, kept
    "a price off the ladder": (
        lambda r: _fc(r, "commercial.price")["answer"].__setitem__("low", 10000),
        "founder_calibration[commercial.price] is 10000 to 5: off the ladder"),
    "a price on a period outside the five": (
        lambda r: _fc(r, "commercial.price")["answer"].__setitem__("period", "one_off"),
        "founder_calibration[commercial.price].period is 'one_off'"),
    "a price on another period than the cost's": (
        lambda r: _fc(r, "commercial.price")["answer"].__setitem__("period", "week"),
        "it is the cost estimate's, 'month' (since revision 6)"),
    "a price in another currency": (
        lambda r: _fc(r, "commercial.price")["answer"].__setitem__("currency", "USD"),
        "the market (GB) prices in GBP, never another"),
    "a price row that is not the ladder": (
        lambda r: r["respondent_questions"]["commercial.price"].__setitem__(
            "codes", ["under_5", "band_5_10", "band_10_20", "band_20_50", "over_50", "would_not_pay"]),
        "respondent_questions[commercial.price].codes are"),
    "a price pick off the row": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("commercial.price", "band_20_50"),
        "Ann Abbott's commercial.price pick 'band_20_50' is not one of the ladder's"),
    "a cost that is a list": (
        lambda r: _fc(r, "commercial.existing_sacrifice").__setitem__("answer", ["spare_keys"]),
        "a cost estimate is {mode: AMOUNT | HOURS"),
    "hours on a B2C entry": (
        lambda r: _fc(r, "commercial.existing_sacrifice")["answer"].update(mode="HOURS", rate=20),
        "is HOURS on a B2C entry"),
    "a cost low of nothing": (
        lambda r: _fc(r, "commercial.existing_sacrifice")["answer"].__setitem__("low", 0), "a cost low is above 0"),
    "a cost sentence that is not the engine's": (
        lambda r: _fc(r, "commercial.existing_sacrifice").__setitem__("belief_sentence", "They spend a lot."),
        "the engine's is 'The problem already costs the payer about"),
    "an ability that is not derived": (
        lambda r: _fc(r, "commercial.ability_to_pay")["answer"].__setitem__("band", "new_money"),
        "derived from the cost and the price it is"),
    "ability to pay missing": (lambda r: r["founder_calibration"].pop("commercial.ability_to_pay"),
                               "founder_calibration lacks commercial.ability_to_pay"),
    "a cost pick with no recall period": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice", {"mode": "AMOUNT", "value": 3, "currency": "GBP"}),
        "records period None"),
    "the old cost control": (
        lambda r: r["respondent_questions"]["commercial.existing_sacrifice"].__setitem__(
            "control", "branch_pick_amounts"), "revision 7 asks cost_total, with no codes and no units"),
    "an r6 cost pick": (
        lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
            "commercial.existing_sacrifice",
            {"currency": "GBP", "period": "quarter", "amounts": [{"kind": "spare_keys", "value": 3}]}),
        "{mode: AMOUNT | HOURS, value, currency, period}"),
    "option counts on the cost standing": (
        lambda r: r["expected"]["standings"]["commercial.existing_sacrifice"].__setitem__(
            "optionCounts", "spare_keys=2"), "records optionCounts; revision 7 has no kinds to count"),
    # the people, and expected
    "neither answer nor unsure": (
        lambda r: r["founder_calibration"].__setitem__("problem.prevalence", {"belief_phrase": "x"}),
        "founder_calibration[problem.prevalence] carries neither"),
    "gate-No with a story": (lambda r: _person(r, "Kit Kerr").__setitem__("story", "Tuesday."),
                             "Kit Kerr answered No at the gate and carries `story`"),
    "gate-No with picks": (lambda r: _person(r, "Lu Lam").__setitem__(
        "picks", {"problem.frequency": 2}), "Lu Lam answered No at the gate and carries picks"),
    "chip anchored": (lambda r: _person(r, "Jo Judd").__setitem__("anchoring", "ANCHORED"),
                      "Jo Judd carries the chip cant_recall and is ANCHORED"),
    "unknown role": (lambda r: r.__setitem__("persona", {"decision_maker": {"role": "cfo"}}),
                     "names the role 'cfo'"),
    "status outside Status": (
        lambda r: r["expected"]["standings"]["problem.importance"].__setitem__("status", "MIXED"),
        "expected.standings[problem.importance].status is 'MIXED'"),
    "a retired status": (
        lambda r: r["expected"]["standings"]["solution.compatibility"].__setitem__("status", "BAR_SET"),
        "expected.standings[solution.compatibility].status is 'BAR_SET', outside Status"),
    "an above drift": (
        lambda r: r["expected"]["standings"]["solution.compatibility"].__setitem__("drift", "above"),
        "expected.standings[solution.compatibility].drift is 'above'; revision 10's drifts are"),
    "deciding not of the vector": (
        lambda r: r["expected"]["vector_verdicts"]["PROBLEM"].__setitem__("deciding", "solution.compatibility"),
        "deciding is 'solution.compatibility', not a PROBLEM dimension (D3: any of them decides)"),
    "NOT_TESTED naming a dimension": (
        lambda r: r["expected"]["vector_verdicts"]["SOLUTION"].__setitem__("verdict", "NOT_TESTED"),
        "expected.vector_verdicts[SOLUTION] is NOT_TESTED and names 'solution.compatibility'"),
}


def _drop_picked(r):
    _fc(r, "solution.compatibility")["answer"].pop("picked")


#: The registry-bound refusals: the file's shape is fine, the registry it is keyed by is not.
KEY_MUTATIONS = {
    "a founder key short": (lambda r: r["founder_calibration"].pop("problem.importance"),
                            "missing problem.importance"),
    "a founder key foreign": (lambda r: r["founder_calibration"].__setitem__(
        "problem.vibes", {"unsure": True}), "names problem.vibes, which is not a registry key"),
    "a b2b_only key on a B2C entry": (lambda r: r["founder_calibration"].__setitem__(
        "commercial.purchase_friction", {"answer": {"items": [{"code": "x", "label": "A sign-off"}], "picked": 0},
                                         "belief_sentence": "x"}),
        "names commercial.purchase_friction, which a B2C entry does not calibrate (b2b_only; "
        "judgement call 47)"),
    "a b2b_only pick on a B2C entry": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "commercial.purchase_friction", "yes_quick"),
        "Ann Abbott picks commercial.purchase_friction, which a B2C entry does not calibrate"),
    "a standing short": (lambda r: r["expected"]["standings"].pop("problem.importance"),
                         "expected.standings is not exactly the 12 calibrated keys"),
    "a fifth not the registry's": (lambda r: _fc(r, "problem.prevalence").__setitem__("answer", "p_0_10"),
                                   "answers 'p_0_10', which is not one of the registry's codes"),
    "a pick foreign": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__("problem.vibes", 1),
                       "Ann Abbott picks problem.vibes"),
    "a plan key foreign": (lambda r: r["respondent_questions"].__setitem__(
        "problem.vibes", {"part": 1}), "respondent_questions carries problem.vibes"),
    "a standing foreign": (lambda r: r["expected"]["standings"].__setitem__(
        "problem.vibes", {"status": "LEFT_OUT"}), "expected.standings carries problem.vibes"),
    "the plan disagrees": (lambda r: r["respondent_questions"].pop("problem.importance"),
                           "respondent_questions part 1"),
    # rule L against `founder.saves`
    "Importance with four": (lambda r: _items(r, "problem.importance").pop(),
                             "founder_calibration[problem.importance] lists 4 items; the registry saves 5 to 5"),
    "Compatibility with one": (lambda r: _items(r, "solution.compatibility").pop(),
                               "founder_calibration[solution.compatibility] lists 1 items; the registry saves 2 to 4"),
    "a label of ten words": (
        lambda r: _items(r, "solution.compatibility")[1].__setitem__(
            "label", "Their keys were all kept together on the very same ring"),
        "founder_calibration[solution.compatibility].items[1].label"),
    "no pick on Compatibility": (_drop_picked, "founder_calibration[solution.compatibility].picked is None"),
    "a pick out of range": (lambda r: _fc(r, "solution.compatibility")["answer"].__setitem__("picked", 2),
                            "founder_calibration[solution.compatibility].picked is 2"),
    "a pick on Commitment": (lambda r: _fc(r, "commercial.commitment")["answer"].__setitem__("picked", 0),
                             "founder_calibration[commercial.commitment] carries `picked`"),
    "no phrase on Current solution": (
        lambda r: _fc(r, "problem.current_solution_satisfaction")["answer"].pop("phrase"),
        "founder_calibration[problem.current_solution_satisfaction] lacks a `phrase`"),
    "no face on a Compatibility item": (lambda r: _items(r, "solution.compatibility")[0].pop("asked"),
                                        "founder_calibration[solution.compatibility].items[0] lacks an `asked`"),
    "a face on a benefit": (lambda r: _items(r, "solution.relative_advantage")[0].__setitem__(
        "asked", "you'd search for less time"), "founder_calibration[solution.relative_advantage].items[0] "
                                                "carries an `asked`"),
    "Buyer and payer without Nobody else first": (
        lambda r: r["founder_calibration"].__setitem__(
            "commercial.buyer_payer_alignment",
            {"answer": {"items": [{"code": "partner", "label": "Their partner"}], "picked": 0},
             "belief_sentence": "x"}),
        "founder_calibration[commercial.buyer_payer_alignment]'s item 0 is"),
    # rule R against the registry
    "a row's control": (lambda r: r["respondent_questions"]["solution.compatibility"].__setitem__(
        "control", "single_choice"), "respondent_questions[solution.compatibility].control is 'single_choice'"),
    "a row's escape": (lambda r: r["respondent_questions"]["solution.compatibility"].__setitem__(
        "escape", "cant_recall"), "respondent_questions[solution.compatibility].escape is 'cant_recall'; the "
                                  "registry's one escape is 'cant_tell'"),
    "a row with no escape": (lambda r: r["respondent_questions"]["problem.frequency"].pop("escape"),
                             "respondent_questions[problem.frequency].escape is None"),
    "an escape on Commitment's row": (lambda r: r["respondent_questions"]["commercial.commitment"].__setitem__(
        "escape", "cant_tell"), "respondent_questions[commercial.commitment].escape is 'cant_tell'"),
    "fixed answers out of order": (lambda r: r["respondent_questions"]["solution.adoption_friction"].__setitem__(
        "codes", ["yes_if_worth_it", "yes", "probably_not", "no"]), "the registry fixes"),
    "Importance's own item": (lambda r: r["respondent_questions"]["problem.importance"].__setitem__(
        "own_item", "the_traffic"), "with own item 'the_traffic'"),
    "Current solution out of order": (
        lambda r: r["respondent_questions"]["problem.current_solution_satisfaction"].__setitem__(
            "codes", ["mostly_works", "works_well", "hit_and_miss", "works_poorly", "no_reliable_way"]),
        "the founder's five outcomes in order"),
    # rule A against the rows
    "Importance picked once": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "problem.importance", ["finding_keys"]), "Ann Abbott's problem.importance pick is ['finding_keys']"),
    "Importance picked twice the same": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "problem.importance", ["finding_keys", "finding_keys"]), "Importance is two distinct codes"),
    "Importance a code off the row": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "problem.importance", ["finding_keys", "the_rain"]), "Importance is two distinct codes"),
    "an escape that is not the row's": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "problem.current_solution_satisfaction", {"chip": "cant_tell"}), "its one escape is 'someone_else_checks'"),
    "an escape on Commitment": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "commercial.commitment", {"chip": "cant_tell"}), "(Commitment has none)"),
    "a fixed answer off the row": (lambda r: _person(r, "Ann Abbott")["picks"].__setitem__(
        "solution.compatibility", "after_first_attempt_fails"),
        "Ann Abbott's solution.compatibility pick is 'after_first_attempt_fails', not one of"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_every_refusal_names_the_entry_and_the_key(tmp_path, name):
    mutate, words = MUTATIONS[name]
    raw = fx.raw_entry()
    mutate(raw)
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    assert str(refusal.value).startswith("09-fixture: "), refusal.value
    assert words in str(refusal.value), refusal.value


@pytest.mark.parametrize("name", sorted(KEY_MUTATIONS))
def test_every_registry_refusal_names_the_entry_and_the_key(tmp_path, name):
    mutate, words = KEY_MUTATIONS[name]
    raw = fx.raw_entry()
    mutate(raw)
    path = fx.write_entry(tmp_path, raw)
    corpus_mod.load_file(path)                      # the shape alone is fine...
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(path, registry=fx.registry())   # ...the registry is not
    assert str(refusal.value).startswith("09-fixture: "), refusal.value
    assert words in str(refusal.value), refusal.value


def test_both_fixtures_and_their_escapes_are_accepted_whole():
    """The green half: the two fixtures load and bind, escapes and all (Flo's none_of_these, Gus's
    someone_else_checks and cant_tell, Di's cant_recall; Pip's two on the decision-maker's link)."""
    for path in (fx.ENTRY, fx.ENTRY_B2B):
        entry = fx.entry(path)
        chips = [(p.person, k) for p in entry.people() for k, v in p.picks.items()
                 if isinstance(v, dict) and "chip" in v]
        assert chips, path
    assert ("Flo Fay", "problem.importance") in [(p.person, k) for p in fx.entry().people()
                                                  for k, v in p.picks.items() if isinstance(v, dict) and "chip" in v]


def test_the_loader_reads_keel_clouds_canon_and_nowhere_else(tmp_path):
    """Call 49: the configured directory is the only source -- an older file there refuses by
    name, never a fallback to a fixture directory."""
    keel_cloud = tmp_path / "keel-cloud"
    directory = corpus_mod.corpus_dir(keel_cloud)
    directory.mkdir(parents=True)
    raw = fx.raw_entry()
    fx.write_entry(directory, raw, "02-new.yaml")
    assert corpus_mod.source_dir(keel_cloud) == directory
    assert [e.id for e in corpus_mod.load(keel_cloud).entries] == ["09-fixture"]
    fx.write_entry(directory, dict(raw, revision=9), "01-old.yaml")
    with pytest.raises(corpus_mod.CorpusError, match="revision is 9"):
        corpus_mod.load(keel_cloud)


# ---------------------------------------------- FR-010: the decision-maker's link on a B2B entry

def _decider(**over):
    return {"person": "Bea Buyer", "link": "COMMERCIAL_B2B", "recency": None,
            "story": None, "chip": None, "anchoring": "ANCHORED",
            "picks": {"commercial.ability_to_pay": "existing_line"}, **over}


def test_a_decision_maker_answers_part_three_on_their_own_link(tmp_path):
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw["answers"].append(_decider())
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw), registry=fx.registry())
    assert "Bea Buyer" in [p.person for p in entry.deciders()]
    assert "Bea Buyer" not in [p.person for p in entry.readable()], "a decider is never read"
    assert len(entry.gate_yes()) == 10, "and is never asked the gate"


@pytest.mark.parametrize("path, raw_entry, mutation, words", [
    ("b2b", fx.ENTRY_B2B, {"recency": "yes"}, "is never asked the gate"),
    ("b2b", fx.ENTRY_B2B, {"picks": {"problem.frequency": 2}}, "the link is Part 3 only"),
    ("b2b", fx.ENTRY_B2B, {"story": "Last month we bought a fleet tag."}, "no story screen"),
    ("b2b", fx.ENTRY_B2B, {"anchoring": "GUESSED"}, "ANCHORED by rule"),
    ("primary", fx.ENTRY, {}, "decision-maker is the same person"),
])
def test_a_decision_maker_out_of_place_is_refused(tmp_path, path, raw_entry, mutation, words):
    raw = fx.raw_entry(raw_entry)
    raw["answers"].append(_decider(**mutation))
    with pytest.raises(corpus_mod.CorpusError) as refusal:
        corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    assert words in str(refusal.value)
