"""Spec 131 FR-1b -- the thirteen dimension cards, held to keel-cloud's registry by test (foolproof by test).

`quality/readers/dimensions.md` carries one card per registry dimension, written by hand and reviewed by the founder.
Here every card is read against its registry row (keel-cloud's `dimension-registry.json`, the export of the YAML of
record) and the compare rules' code where the registry is silent (`instructions/chain.BUDGET_SUPPORTS`, keel-cloud's
`CommercialChain`), so a card that drifts from its row fails `make unit`:

- **the row**: the card's key and order, its vector, the registry's `meaning` word for word, the founder `control`, the
  stranger's `control`, `answers.compare_rule`, `supporting_side`, `supports`, `conditional`, the floor, `b2b_only` /
  `b2b_link_only`, and the founder's *I'm not sure* (`unsure_allowed`, `left_out`);
- **the shape**: the counts of `founder.saves` (how many rows, how many words), the order of the stranger's
  `fixed_answers` (Prevalence: the gate's *Yes · No*; Current solution: `outcome_1` to `outcome_5`; Prevalence's founder
  fifths);
- **For / Against / Neither**: the codes on the card's lines equal the codes the registry's `answers` block counts, by
  its compare rule;
- **the escape**: `respondent.escape` -- none, or its code, its label and how it counts;
- **the examples** (FR-1b, FR-6): each card's good example is scored R7 2 and its bad one R7 0 by a scripted reader
  (`scripted_r7`) that reads the card -- its **Escape**, its **Fixed answers**, its **For** / **Against** -- and applies
  FR-1c's four questions in order to the example as a structured screen: the measure, the shape, the balance (*could
  the belief ever be supported? ever refuted?*), the escape. Where what breaks a bad example is a fact about the people
  a reader knows from the persona (a gate everyone answers Yes, a step someone else takes, a percent of a thing that is
  not money), the screen carries that fact as the reader would read it; the card's rule is the one applied. Every
  example's words are the card's own (a reworded card breaks its example here, not silently).

No model, no stack, no network; the registry is read from the keel-cloud checkout `stack.toml` names (skipped without
one).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from harness import working_rung as wr
from instructions import chain as chain_mod
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
REGISTRY_REL = "src/main/resources/keel/dimension-registry.json"
WORKING_RUNG_REL = "src/main/java/com/keeldiscovery/cloud/domain/vectors/WorkingRung.java"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_CLOUD}")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(_cloud(REGISTRY_REL))


@pytest.fixture(scope="module")
def rows(registry) -> dict:
    return {d["key"]: d for d in registry["dimensions"]}


TEXT = cards.cards_text()
KEYS = cards.keys(TEXT)


def _flat(text: str) -> str:
    return " ".join(str(text).split())


def _body(key: str) -> str:
    return cards.card(key, TEXT)


# ------------------------------------------------------------------------------------------------ the cards

def test_thirteen_cards_in_the_registrys_order(registry):
    assert KEYS == [d["key"] for d in sorted(registry["dimensions"], key=lambda d: (
        ("PROBLEM", "SOLUTION", "COMMERCIAL").index(d["vector"]), d["order"]))]
    assert len(KEYS) == 13 == len(set(KEYS))
    for key in KEYS:                                      # each card once, its two markers in order
        assert TEXT.count(f"<!-- card:{key}:begin -->") == 1 == TEXT.count(f"<!-- card:{key}:end -->")


def test_a_card_is_the_text_between_its_markers_and_nothing_above_the_first():
    body = _body("problem.current_solution_satisfaction")
    assert body.startswith("### Current solution · `problem.current_solution_satisfaction`")
    assert body.endswith("Re-\n  saving it is refused until the first rung is reworded.")
    assert "**What a card is.**" not in body and "<!--" not in body
    assert cards.card_for(None, TEXT) is None and cards.card_for("", TEXT) is None
    assert cards.card_for("problem.no_such_row", TEXT) is None
    assert cards.card_for("solution.compatibility", TEXT) == _body("solution.compatibility")
    with pytest.raises(cards.CardError):
        cards.card("problem.no_such_row", TEXT)


@pytest.mark.parametrize("key", KEYS)
def test_the_card_says_its_rows_meaning_word_for_word(key, rows):
    assert cards.meaning(_body(key)) == rows[key]["meaning"]


@pytest.mark.parametrize("key", KEYS)
def test_the_registry_line_is_the_rows(key, rows):
    row, line = rows[key], cards.registry_line(_body(key))
    assert line.startswith(f"{row['vector']}, order {row['order']} ·"), line
    assert f"founder `{row['founder']['control']}`" in line
    assert f"stranger `{row['respondent']['control']}`" in line
    assert f"compare `{row['answers']['compare_rule']}`" in line
    side = row["answers"].get("supporting_side")
    assert (f"supporting side `{side}`" in line) if side else ("supporting side" not in line)
    assert f"floor {row['answers']['floor']}" in line
    supports = row["respondent"].get("supports")
    said = re.search(r"· supports (.*?) ·", line)
    assert (cards.codes(said.group(1)) == supports) if supports else said is None, (key, line)
    conditional = row["respondent"].get("conditional")
    said = re.search(r"· conditional (.*?) ·", line)
    assert (cards.codes(said.group(1)) == [conditional]) if conditional else said is None
    assert ("`b2b_only`" in line) == bool(row.get("b2b_only"))
    assert ("`b2b_link_only`" in line) == bool(row["respondent"].get("b2b_link_only"))


@pytest.mark.parametrize("key", KEYS)
def test_the_founders_not_sure_is_the_rows(key, rows):
    row, line, escape = rows[key], cards.registry_line(_body(key)), cards.section(_body(key), 4)
    if row["founder"]["unsure_allowed"]:
        assert "no *I'm not sure*" not in line
        assert re.search(r"\bleft out\b|\bleaves .{0,40}\bout\b", _flat(escape)), key
    else:                                                 # Prevalence: the gate is the denominator
        assert "no *I'm not sure*" in line and "Unreachable" in row["left_out"]["note"]
        assert "unreachable" in _flat(escape).lower()


# ------------------------------------------------------------------------------------------------ the shape

def _saves_said(line: str) -> tuple[int, int, int] | None:
    match = re.search(r"saves (?:exactly (\d+)|(\d+) to (\d+)),[^;)]*?\b(\d+) words", line)
    if not match:
        return None
    low = int(match.group(1) or match.group(2))
    high = int(match.group(1) or match.group(3))
    return low, high, int(match.group(4))


@pytest.mark.parametrize("key", KEYS)
def test_the_shapes_counts_are_the_saves(key, rows):
    """The card's *saves* -- how many rows, how many words -- are `founder.saves`'s; a row with no saved list says
    none."""
    saves, said = rows[key]["founder"].get("saves"), _saves_said(cards.registry_line(_body(key)))
    if not saves:
        assert said is None, key
        return
    assert said == (saves["min_items"], saves["max_items"], saves["max_words"]), key
    line = cards.registry_line(_body(key))
    assert ("picked" in line) == bool(saves.get("picked"))
    assert ("own first" in line) == bool(saves.get("own_first"))
    fixed = saves.get("fixed_first")
    assert (f"`{fixed['code']}` fixed first" in line) if fixed else "fixed first" not in line


@pytest.mark.parametrize("key", KEYS)
def test_the_fixed_answers_are_the_rows_in_order(key, rows):
    row, body = rows[key], _body(key)
    said = cards.fixed_answer_codes(body)
    fixed = [a["code"] for a in row["respondent"].get("fixed_answers") or []]
    if key == "problem.prevalence":                       # the gate: code renders *Yes · No*
        assert row["respondent"]["option_rule"].startswith("Yes · No")
        assert said == ["yes", "no"]
    elif key == "commercial.purchase_friction":           # five bands of code's, then the one fixed answer
        assert fixed == ["not_needed"] and "`not_needed` *It wouldn't be needed*" in _flat(cards.section(body, 2))
    else:
        assert said == fixed, key
    for answer in row["respondent"].get("fixed_answers") or []:
        assert f"`{answer['code']}`" in body


def test_current_solutions_five_outcomes_and_prevalences_fifths(rows):
    shape = _flat(cards.section(_body("problem.current_solution_satisfaction"), 2))
    assert "**exactly five outcomes, best to worst** (codes `outcome_1` to `outcome_5`)" in shape
    saves = rows["problem.current_solution_satisfaction"]["founder"]["saves"]
    assert saves["min_items"] == saves["max_items"] == 5 and saves["max_words"] == 9
    fifths = _flat(cards.section(_body("problem.prevalence"), 2))
    assert cards.codes(fifths.split("**Exactly five options", 1)[1].split("The first is", 1)[0]) == \
        rows["problem.prevalence"]["founder"]["normalized"]["codes"]


# ---------------------------------------------------------------------------- for, against, neither (by code)

def _expected_sides(row: dict) -> dict:
    """`{(variant, side): [codes]}` -- what the registry's `answers` block counts, by its compare rule (and, where the
    registry is silent, the compare's code: `CommercialChain.BUDGET_SUPPORTS`, `CONSUMER_BUDGET`)."""
    rule = row["answers"]["compare_rule"]
    respondent = row["respondent"]
    fixed = [a["code"] for a in respondent.get("fixed_answers") or []]
    escape = respondent.get("escape")
    apart = [escape["code"]] if escape and escape["counts"] == "apart" else []
    if rule == "proportion_from_gate":
        return {("", "for"): ["yes"], ("", "against"): ["no"], ("", "neither"): []}
    if rule == "interval_contains_median":
        return {("", "for"): [], ("", "against"): [], ("", "neither"): apart}
    if rule == "share_in_picks":
        assert row["founder"]["saves"]["own_first"] and escape["counts"] == "against"
        return {("", "for"): ["own"], ("", "against"): [escape["code"]], ("", "neither"): []}
    if rule == "below_line":
        return {("", "for"): ["outcome_3", "outcome_4", "outcome_5"], ("", "against"): row["follow_up"]["against"],
                ("", "neither"): apart}
    if rule == "fixed_last_two_against":
        assert respondent["supports"] == fixed[:2]
        return {("", "for"): fixed[:2], ("", "against"): fixed[2:], ("", "neither"): apart}
    if rule == "ordinal_band":
        return {("", "for"): [], ("", "against"): [chain_mod.WOULD_NOT_PAY], ("", "neither"): apart}
    if rule == "cost_covers_price":
        business = [c for c in fixed if c in chain_mod.BUDGET_SUPPORTS]
        consumer = list(chain_mod.CONSUMER_BUDGET)
        return {("(budget, business)", "for"): business,
                ("(budget, business)", "against"): [c for c in fixed if c not in business] + ["no_budget"],
                ("(budget, consumer)", "for"): [c for c in consumer if c in chain_mod.BUDGET_SUPPORTS],
                ("(budget, consumer)", "against"): [c for c in consumer if c not in chain_mod.BUDGET_SUPPORTS],
                ("", "neither"): []}
    if rule == "first_supports":
        alone = "decided_alone"
        return {("A role tested", "for"): [c for c in fixed if c in respondent["supports"]],
                ("A role tested", "against"): [c for c in fixed if c not in respondent["supports"]],
                ("Nobody else tested", "for"): [alone],
                ("Nobody else tested", "against"): [c for c in fixed if c != alone],
                ("", "neither"): apart}
    if rule == "duration_band":
        return {("", "for"): respondent["supports"], ("", "against"): [], ("", "neither"): apart}
    raise AssertionError(f"a compare rule this test does not read: {rule}")


@pytest.mark.parametrize("key", KEYS)
def test_for_against_and_neither_are_the_codes_the_registry_counts(key, rows):
    row = rows[key]
    said = cards.sides(_body(key))
    expected = _expected_sides(row)
    if key == "problem.current_solution_satisfaction":
        # the escape is one of two by the act (keel-cloud 172: `handed_off`): the registry's, or *I can't recall*
        assert said.pop(("", "neither")) == [row["respondent"]["escape"]["code"], "cant_recall"]
        expected.pop(("", "neither"))
        assert "after answer 2" in _flat(cards.section(_body(key), 3)) or "on a line after 2" in _flat(
            cards.section(_body(key), 3))
        compare = rows[key]["answers"]["compare_rule"]
        assert compare == "below_line"
    assert said == expected, key


def test_the_registrys_below_line_is_the_cards_direction(registry):
    """The amendment's correction (2026-11-03): the rungs below the line count for the founder's belief (*still falls
    short*), the rungs above it against -- the registry's `below_line`, as the card states it."""
    below = registry["common"]["compare_rules"]["below_line"]
    assert "answers 3, 4 and 5 support (today's way falls short), 1 and 2 count against" in below
    card = _flat(cards.section(_body("problem.current_solution_satisfaction"), 3))
    assert "**For the belief:** every rung **below** the line" in card
    assert "**Against the belief:** every rung **above** the line" in card


# ------------------------------------------------------------------------------------------------ the escape

@pytest.mark.parametrize("key", KEYS)
def test_the_escape_is_the_rows(key, rows):
    escape, line = rows[key]["respondent"].get("escape"), cards.escape_line(_body(key))
    registry_line = cards.registry_line(_body(key))
    if escape is None:
        assert line.startswith("none"), (key, line)
        assert "· escape none ·" in registry_line
        return
    assert f"`{escape['code']}`" in line and f"*{escape['label']}*" in line, (key, line)
    assert f"escape `{escape['code']}`" in registry_line
    assert escape["counts"] in line, (key, escape["counts"])


def test_the_cards_shortfall_words_are_working_rungs_and_keel_clouds():
    """keel-cloud 203's `WorkingRung`: the card's negations are code's, and this repository's restatement is the Java
    pattern word for word."""
    java = _cloud(WORKING_RUNG_REL)
    block = java.split("static final Pattern SHORTFALL = Pattern.compile(", 1)[1].split(");", 1)[0]
    pattern = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', block)).replace("\\\\", "\\")
    assert pattern == "(?i)" + wr.SHORTFALL.pattern
    negations = set(re.findall(r'"(\w+)"', java.split("NEGATIONS = Set.of(", 1)[1].split(")", 1)[0]))
    assert negations == set(wr.NEGATIONS)
    healthy = _flat(cards.section(_body("problem.current_solution_satisfaction"), 3))
    said = healthy.split("unless the word before it negates it", 1)[1].split(")", 1)[0]
    assert set(re.findall(r"\*(\w+)\*", said)) == set(wr.NEGATIONS)
    for word in ("inconsistent", "uneven", "unsupported", "too weak", "never enough", "not enough", "failed",
                 "falls short", "not good enough", "didn't work", "did not work", "doesn't work", "never worked",
                 "cost them money"):
        assert f"*{word}*" in healthy and wr.shortfall(word) == word.lower(), word


# ------------------------------------------------------------------------------- the examples, R7 by a scripted reader

def _amount(label: str) -> float:
    """The lower edge of a price band (*Under $500* 0, *$800 to under $2,500* 800, *$5,000 or more* 5000)."""
    if label.lower().startswith("under"):
        return 0.0
    match = re.search(r"\$?([\d,]+(?:\.\d+)?)", label)
    return float(match.group(1).replace(",", "")) if match else -1.0


def scripted_r7(body: str, screen: dict) -> tuple[int, str]:
    """A scripted reader's R7 on one screen, from the card it was handed (FR-1c's questions, in order): `(score,
    why)`. 2 all met; 0 a rule broken. The rules read off the card: its **Escape** (none, or one that must be there),
    its **Fixed answers** (the shape: the screen's codes are the card's, in order), its **For** / **Against** (the
    balance: at least one option can count each way); and its Healthy lines as the screen's facts say them."""
    facts = screen.get("facts") or {}
    stem = screen.get("stem") or ""
    options = list(screen.get("options") or [])
    # 1. the measure -- every option on the one measure the card names
    unit = screen.get("unit")
    if unit and not re.search(rf"\bon how many {re.escape(unit)}\b", stem):
        return 0, f"the stem drops the unit: it never asks on how many {unit}"
    if screen.get("box_unit") and screen.get("founder_unit") and \
            screen["founder_unit"].split()[0].lower() not in screen["box_unit"].lower():
        return 0, f"the box counts {screen['box_unit']}, the founder's cost is {screen['founder_unit']}"
    if facts.get("of_money") is False:
        return 0, "a percent of something that is not money is not a price anyone can pay"
    # 2. the shape -- the count, the order, the first and the last, the founder's own row
    fixed = cards.fixed_answer_codes(body)
    codes = screen.get("codes")
    if fixed and screen.get("fixed", True):
        if codes is None or [c for c in fixed if c in codes] != codes:
            return 0, f"the options are not the card's fixed answers in order ({codes} against {fixed})"
    if screen.get("step") and not options[0].lower().endswith(screen["step"].lower()):
        return 0, f"the first yes ({options[0]!r}) names no step of the founder's"
    if screen.get("founder_time_typed") is False:
        return 0, "the edge the scale turns on is a time the founder never typed"
    # 3. the balance -- could the belief ever be supported? ever refuted?
    sides = cards.sides(body)
    variant = screen.get("variant", "")
    for_codes = set(sides.get((variant, "for"), []))
    against_codes = set(sides.get((variant, "against"), []))
    pro = con = 0
    if "line" in screen:                                  # Current solution: above the line against, below it for
        above = options[:screen["line"]]
        if wr.working(options, screen["line"]) < len(above):
            return 0, f"a rung above the line is a shortfall ({above[wr.working(options, screen['line'])]!r}): no rung " \
                      "where today's way works, the belief tested against nothing"
        pro, con = len(options) - screen["line"], screen["line"]
    elif "low" in screen:                                 # a number from the founder's low up counts for
        values = [float(o) for o in options]
        pro, con = sum(v >= screen["low"] for v in values), sum(v < screen["low"] for v in values)
    elif "price_low" in screen:
        edges = [_amount(o) for o in options if o != "I wouldn't pay for this"]
        if screen["price_low"] not in edges:
            return 0, "no band edge sits exactly at the founder's low"
        pro, con = sum(e >= screen["price_low"] for e in edges), sum(e < screen["price_low"] for e in edges) + 1
    elif "founder_time" in screen:
        at = next((i for i, o in enumerate(options) if o.startswith(screen["founder_time"])), None)
        if at is None:
            return 0, "no band starts at the founder's time"
        pro, con = at + 1, len(options) - 1 - at
    elif screen.get("box_unit"):
        pro = con = 1                                     # an open box: any number below the founder's low, any above
    else:
        pro = sum(1 for c in (codes or []) if c in for_codes)
        con = sum(1 for c in (codes or []) if c in against_codes)
        escape_code = screen.get("escape_code")
        con += int(bool(escape_code) and escape_code in against_codes)
    if facts.get("true_of_everyone"):
        return 0, "every one of these people would answer one way: the belief can never be refuted"
    if facts.get("someone_elses_step"):
        return 0, "the step is someone else's: no option answers whether this person would take it"
    if screen.get("founder_roles") and variant == "Nobody else tested":
        return 0, "the founder named a role, and the belief says nobody else: his own answer counts against him"
    if not pro:
        return 0, "nothing can count for the belief: it can never be supported"
    if not con:
        return 0, "nothing can count against the belief: it can never be refuted"
    # 4. the escape -- there where the card requires one, absent where it forbids one
    line = cards.escape_line(body)
    escape = screen.get("escape")
    if line.startswith("none"):
        if escape:
            return 0, f"an escape ({escape!r}) on an item the card says has none"
    elif not escape:
        return 0, "the escape the card requires is missing"
    elif f"*{escape}" not in line:
        return 0, f"the escape {escape!r} is not the card's"
    return 2, "the measure, the shape, the balance and the escape all as the card says"


#: Each card's two examples (its section 5) as the screens they describe -- the words the card's own. `facts` are what
#: a reader knows from the persona and the founder's material, said where they decide R7.
EXAMPLES = {
    "problem.prevalence": {
        "good": {"stem": "In the last 5 working days, did you type up the daily log after your site walks?",
                 "options": ["Yes", "No"], "codes": ["yes", "no"], "escape": None},
        "bad": {"stem": "In the last 5 working days, did you log site-walk photos and notes?",
                "options": ["Yes", "No"], "codes": ["yes", "no"], "escape": None,
                "facts": {"true_of_everyone": True}}},
    "problem.frequency": {
        "good": {"stem": "In the last 7 nights, on how many nights did you have to work out why your baby was crying?",
                 "options": ["1", "2", "3", "4", "5", "6", "7"], "unit": "nights", "low": 4,
                 "escape": "I can't recall"},
        "bad": {"stem": "In the last 3 months, on how many did you leave raised cash sitting in your bank's money "
                        "market fund?", "options": ["1", "2", "3"], "unit": "months", "low": 2,
                "escape": "I can't recall"}},
    "problem.importance": {
        "good": {"stem": "Think of your last night. Which one of these would you most like made easier?",
                 "options": ["Getting the baby back down after a feed", "Working out what the cry means",
                             "Getting back to sleep yourself", "Keeping track of the night's feeds"],
                 "codes": ["rival_1", "own", "rival_2", "rival_3"], "escape": "None of these",
                 "escape_code": "none_of_these"},
        "bad": {"stem": "Think of your last shift. Which one of these would you most like made easier?",
                "options": ["Handling guests' requests at the desk", "Keeping rates right on every channel",
                            "Answering booking emails and group requests", "Getting through the check-in rush"],
                "codes": ["rival_1", "rival_2", "rival_3", "rival_4"], "escape": "None of these",
                "escape_code": "none_of_these"}},
    "problem.current_solution_satisfaction": {
        "good": {"options": ["Evidence was clear enough to decide", "Inconsistent evidence across the decks",
                             "Unsupported claims reached the committee", "Evidence too weak to decide on",
                             "Never enough evidence to decide"], "line": 1, "escape": "Someone else did it"},
        "lullaby": {"options": ["Knew what the baby needed straight away", "Got it right after one wrong guess",
                                "It took a few tries to find it", "Tried everything before anything worked",
                                "Nothing worked; the baby settled alone"], "line": 2,
                    "escape": "Someone else did it"},
        "bad": {"options": ["Inconsistent", "Too uneven", "Unsupported", "Too weak", "Never enough"], "line": 1,
                "escape": "Someone else did it"}},
    "solution.compatibility": {
        "good": {"stem": "On your last site walk, could you have spoken into your phone over the noise?",
                 "options": ["Yes, easily", "Yes, most of the time", "Only sometimes", "No"],
                 "codes": ["yes_easily", "yes_with_steps", "only_with_help", "no"], "escape": "I can't tell"},
        "bad": {"stem": "On your last site walk, was your job already keeping its daily logs in Procore or ACC?",
                "options": ["Yes", "Yes, with some steps", "No"], "codes": ["yes_easily", "yes_with_steps", "no"],
                "escape": "I can't tell", "facts": {"true_of_everyone": True}}},
    "solution.relative_advantage": {
        "good": {"stem": "Think of the last night when you had to work out what the baby needs. Would Lullaby, a phone "
                         "app that listens to crying, have done that better for you, or not?",
                 "options": ["A lot better", "A little better", "No difference", "Worse"],
                 "codes": ["a_lot_better", "a_little_better", "no_difference", "worse"], "escape": "I can't tell"},
        "bad": {"stem": "Which of these would have made your last night better?",
                "options": ["Fewer tries before the baby settles", "Knowing why the baby cried",
                            "Getting back to sleep sooner"], "codes": None, "escape": "I can't tell"}},
    "solution.adoption_friction": {
        "good": {"stem": "To use it, you'd hold your phone near the cot for ten seconds. Would you do that, or not?",
                 "options": ["Yes", "Only if it didn't wake the baby", "Probably not", "No"],
                 "codes": ["yes", "yes_if_worth_it", "probably_not", "no"], "escape": "I can't tell"},
        "bad": {"stem": "To use it, you'd get your clinic manager to approve it. Would you do that, or not?",
                "options": ["Yes", "Yes, if it was clearly worth it", "Probably not", "No"],
                "codes": ["yes", "yes_if_worth_it", "probably_not", "no"], "escape": "I can't tell",
                "facts": {"someone_elses_step": True}}},
    "commercial.existing_sacrifice": {
        "good": {"stem": "Last month, about how many hours per site did your team spend on the daily log?",
                 "options": [], "box_unit": "hours per site last month", "founder_unit": "hours per site a month",
                 "escape": "I can't recall"},
        "bad": {"stem": "Last year, about how many days did cash sit in your operating account?", "options": [],
                "box_unit": "days", "founder_unit": "2% of the balance per company a year", "escape": None}},
    "commercial.price": {
        "good": {"stem": "What would Fresco be worth to you a month, per site?",
                 "options": ["Under $500", "$500 to under $800", "$800 to under $2,500", "$2,500 to under $5,000",
                             "$5,000 or more", "I wouldn't pay for this"], "price_low": 800.0,
                 "escape": "I can't say"},
        "bad": {"stem": "Fresco takes a fee of a percent of the daily log. What fee would feel fair to you?",
                "options": ["Under 1%", "1% to under 2%"], "escape": "I can't say", "facts": {"of_money": False}}},
    "commercial.ability_to_pay": {
        "good": {"stem": "You said about $800 to $2,500 a month. If you went ahead at that, where would the money "
                         "come from?",
                 "options": ["An existing budget line", "Charged to the teams or sites that use it",
                             "A new budget line, signed off for it", "A grant or outside funding",
                             "Taken from other spending"],
                 "codes": ["existing_line", "charged_to_users", "new_line_signed_off", "outside_funding",
                           "taken_from_other_spend"], "variant": "(budget, business)", "escape": "I can't say"},
        "bad": {"stem": "where would the money come from?",
                "options": ["A budget line we already had", "A new budget line, signed off", "Taken from other spending",
                            "There was no budget for it"],
                "codes": ["existing_line", "new_line_signed_off", "taken_from_other_spend", "no_budget"],
                "variant": "(budget, business)", "escape": None}},
    "commercial.buyer_payer_alignment": {
        "good": {"stem": "Could you sign off on about 0.25% of the balance a year yourself, or would the board have to "
                         "agree?",
                 "options": ["I could sign off myself", "The board would have to agree",
                             "Several people would have to agree", "It's someone else's call"],
                 "codes": ["decided_alone", "had_to_agree", "someone_else_agreed", "someone_else_decided"],
                 "variant": "A role tested", "founder_roles": ["The board"], "escape": "I can't say"},
        "bad": {"stem": "Could you sign off on it yourself, or would someone else have to agree?", "options": [],
                "codes": ["decided_alone", "had_to_agree", "someone_else_agreed", "someone_else_decided"],
                "variant": "Nobody else tested", "founder_roles": ["The board"], "escape": "I can't say"}},
    "commercial.purchase_friction": {
        "good": {"stem": "If you bought Expanse, how long would a security review of an agent on every node take?",
                 "options": ["Under 2 weeks", "2 to under 6 weeks", "6 weeks to 3 months", "3 to 6 months",
                             "Over 6 months", "It wouldn't be needed"], "founder_time": "6 weeks",
                 "founder_time_typed": True, "escape": "I can't tell"},
        "bad": {"stem": "If you bought Fresco, how long would a signed contract take?",
                "options": ["Under 1 week", "1 to under 2 weeks", "2 weeks to 1 month", "1 to 3 months",
                            "Over 3 months", "It wouldn't be needed"], "founder_time": "2 weeks",
                "founder_time_typed": False, "escape": "I can't tell"}},
    "commercial.commitment": {
        "good": {"stem": "If it were ready today, would you start a paid pilot on one site, or not?",
                 "options": ["Yes, I'd start a paid pilot on one site", "Probably yes", "Probably not", "No"],
                 "codes": ["yes_start", "yes_after_trying", "probably_not", "no"],
                 "step": "start a paid pilot on one site", "escape": None},
        "bad": {"stem": "If it were ready today, would you order a pair with free returns, or not?",
                "options": ["Yes, I'd start one", "Yes, after trying it first", "Probably not", "No"],
                "codes": ["yes_start", "yes_after_trying", "probably_not", "no"],
                "step": "order a pair with free returns", "escape": None}},
}


def test_every_card_has_its_two_examples_here():
    assert sorted(EXAMPLES) == sorted(KEYS)


@pytest.mark.parametrize("key", KEYS)
def test_the_examples_are_the_cards_own_words(key):
    """A reworded example breaks here: every stem and option above is the card's section 5, word for word."""
    said = _flat(cards.section(_body(key), 5))
    for name, screen in EXAMPLES[key].items():
        for words in [screen.get("stem")] + list(screen.get("options") or []):
            if words:
                assert _flat(words) in said, (key, name, words)


@pytest.mark.parametrize("key", KEYS)
def test_the_good_example_is_r7_2_and_the_bad_one_r7_0(key):
    body = _body(key)
    five = _flat(cards.section(body, 5))
    assert "**Good (R7 2)**" in five and "**Bad (R7 0)**" in five and "**What breaks it:**" in five
    for name, screen in EXAMPLES[key].items():
        score, why = scripted_r7(body, screen)
        assert score == (0 if name == "bad" else 2), (key, name, why)


def test_the_angel_group_scale_is_r7_0_for_want_of_a_working_rung():
    """FR-6: the angel-group scale of 2026-11-03 -- five shortfalls, the line under the first -- is a 0 by the card's own
    rule, wherever the line sits; redrawn with a working rung on top it is a 2."""
    body = _body("problem.current_solution_satisfaction")
    five = EXAMPLES["problem.current_solution_satisfaction"]["bad"]
    for line in (1, 2, 3, 4):
        score, why = scripted_r7(body, {**five, "line": line})
        assert score == 0 and "no rung where today's way works" in why
    keel = ["Inconsistent evidence across the decks", "Unsupported claims reached the committee",
            "Evidence too weak to decide on", "Never enough evidence to decide", "The screening failed outright"]
    assert scripted_r7(body, {"options": keel, "line": 1, "escape": "Someone else did it"})[0] == 0
    assert scripted_r7(body, EXAMPLES["problem.current_solution_satisfaction"]["good"]) == (
        2, "the measure, the shape, the balance and the escape all as the card says")


def test_a_scale_where_every_option_counts_one_way_is_r7_0():
    """FR-1c: a scale where every option counts one way is a 0 -- Frequency's range from 1 (every button for), a
    Compatibility item served the two yeses alone, Commitment served an escape it must not have."""
    frequency = {**EXAMPLES["problem.frequency"]["good"], "low": 1}
    assert scripted_r7(_body("problem.frequency"), frequency)[0] == 0
    yeses = {**EXAMPLES["solution.compatibility"]["good"], "options": ["Yes, easily", "Yes, most of the time"],
             "codes": ["yes_easily", "yes_with_steps"]}
    assert scripted_r7(_body("solution.compatibility"), yeses) == (
        0, "nothing can count against the belief: it can never be refuted")
    escaped = {**EXAMPLES["commercial.commitment"]["good"], "escape": "I can't tell"}
    assert scripted_r7(_body("commercial.commitment"), escaped)[0] == 0
    bare = {**EXAMPLES["solution.relative_advantage"]["good"], "escape": None}
    assert scripted_r7(_body("solution.relative_advantage"), bare) == (0, "the escape the card requires is missing")


# --------------------------------------------- spec 132 FR-4 (keel-cloud 205 FR-4): the Open points 205 settled

REGISTRY_YAML_REL = "canon/designs/vectors/dimension-registry.yaml"
#: The cards whose Open points keel-cloud 205 settled, each moved into the card's lines word for word as the registry's
#: `_note_205` (YAML of record; dropped from the JSON) says it -- and the Open point each replaced, gone.
SETTLED_205 = {"problem.prevalence": ("Registry vs spec 184 FR-1.",),
               "problem.frequency": ("Registry vs spec 184 FR-2.",),
               "solution.adoption_friction": ("Registry row's notes vs its own rule and spec 198.",),
               "commercial.ability_to_pay": ("Registry vs spec 181 FR-2 and code.",),
               "commercial.purchase_friction": ("Spec 182 FR-6 vs registry.",),
               "commercial.commitment": ("Registry notes vs specs 180 and 198.", "Registry vs spec 199 FR-5.")}
SETTLED_LABEL = "**Settled by keel-cloud 205 (the registry's note):**"


@pytest.fixture(scope="module")
def yaml_rows() -> dict:
    import yaml                                                         # noqa: PLC0415
    return {d["key"]: d for d in yaml.safe_load(_cloud(REGISTRY_YAML_REL))["dimensions"]}


def _note_205(row: dict) -> str:
    return row.get("_note_205") or (row.get("respondent") or {}).get("_note_205")


def _open(body: str) -> str:
    return body.split("#### Open", 1)[1] if "#### Open" in body else ""


@pytest.mark.parametrize("key", sorted(SETTLED_205))
def test_the_open_points_205_settled_are_the_cards_lines_in_the_registrys_words(key, yaml_rows):
    """Spec 132 FR-4: each settled point is out of *Open* and on the card's lines, the registry's `_note_205` word for
    word (one space between words), outside the Open section."""
    body, note = _body(key), _note_205(yaml_rows[key])
    assert note and note.startswith("2026-11-03, spec 205 (FR-4;"), key
    lines = body.split("#### Open", 1)[0]
    said = re.search(re.escape(SETTLED_LABEL) + r"(.*?)(?:\n- |\n\n|$)", lines, re.S)
    assert said and _flat(said.group(1)) == _flat(note), key
    for point in SETTLED_205[key]:
        assert f"**{point}**" not in _open(body), (key, point)


def test_no_card_but_the_six_carries_a_205_note_and_the_others_are_unmoved(yaml_rows):
    """Spec 132 FR-4: no other card line moves -- the settled line is on the six alone, and every Open point 205 did not
    settle stands (Prevalence's and Frequency's *Not settled*, Frequency's bands, Current solution's two, Existing
    sacrifice's two, Ability to pay's chain note, Buyer and payer's belief and item)."""
    for key in KEYS:
        assert (SETTLED_LABEL in _body(key)) == (key in SETTLED_205), key
        assert (_note_205(yaml_rows[key]) is not None) == (key in SETTLED_205), key
    kept = {"problem.prevalence": ["Not settled."], "problem.frequency": ["Spec 131 vs registry.", "Not settled."],
            "problem.current_solution_satisfaction": ["Spec 131 vs registry.", "Spec 203 FR-3 vs code."],
            "commercial.existing_sacrifice": ["Spec 198 FR-3 vs registry.", "Registry vs code (spec 128 FR-21)."],
            "commercial.ability_to_pay": ["Registry note vs the chain."],
            "commercial.buyer_payer_alignment": ["Belief vs item (registry `_why_199`, spec 199 FR-1)."]}
    for key in KEYS:
        found = re.findall(r"^- \*\*(.+?)\*\*", _open(_body(key)), re.M)
        assert found == kept.get(key, []), (key, found)
    assert "(served `cant_say`: see the escape)" in cards.registry_line(_body("commercial.ability_to_pay"))


def test_commitments_drift_template_is_the_registrys_without_now(rows):
    """Spec 132 FR-4 / FR-5 (keel-cloud 205 FR-4): Commitment's `drift_template` loses *now*; the card says it word for
    word, and no *now* is left in it."""
    drift = rows["commercial.commitment"]["answers"]["drift_template"]
    assert drift == "you said most would {founder} · {observed} of {n} would"
    assert f"**The drift template:** *{drift}*" in _flat(cards.section(_body("commercial.commitment"), 3))
