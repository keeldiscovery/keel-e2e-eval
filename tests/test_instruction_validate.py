"""The batch this eval hands the aggregate (spec 025 US6, FR-018/FR-019, T017).

`validate.py`'s whole argument is that the only honest way to ask what the aggregate refuses is to
hand it to the aggregate. That argument only holds if the batch shows the aggregate the state the
screen would really have arrived into — which is why `roles` has always travelled with a case, why
`earlier_beliefs` now does too, and why a `QUESTIONS` case carries the **`measurements` the model
was shown** rather than letting the validator seed a project of its own.

**And if the aggregate cannot take a shape this batch needs, the run says so by name and reports
the marks that depended on it unmeasured.** Never a warning, never scored as a refusal: an
unmeasured mark is not a met mark (judgement call 13), and a green run that never showed the
aggregate a questionnaire, or showed it a reference with nothing to resolve against, is the one way
this rubric could flatter itself.
"""

from __future__ import annotations

from instructions import prompts as prompts_mod
from instructions import validate as validate_mod

EARLIER = [
    {"stage": "PROBLEM", "line": 1, "heading": "It costs them hours",
     "statement": "It costs one to two hours.", "measure": {"kind": "DURATION", "unit": "hours"},
     "band": {"lower": {"value": 1}, "upper": {"value": 2}}, "role": "Managers",
     "risk": "LOAD_BEARING"},
    {"stage": "PROBLEM", "line": 2, "heading": "They do it weekly",
     "statement": "It happens most weeks.", "measure": None,
     "band": {"options": ["yes", "no"], "expected": "yes"}, "role": "Managers",
     "risk": "SUPPORTING"},
]


def _case(kind, subject, screen, *, context=None, roles=()):
    payload = prompts_mod.payload_for("I", context or {}, {"allowed_outcomes": ["COMPLETED"]})
    return prompts_mod.Case(case_id=f"e/{subject}/run1", kind=kind, entry_id="e", screen=screen,
                            subject=subject, run_index=1, payload=payload,
                            existing_roles=list(roles))


def _assumptions_case(**kw):
    return _case("ASSUMPTIONS", "SOLUTION", "SOLUTION_ASSUMPTIONS",
                 context={"solution_statement": "The solution.", "market": {"country": "GB"},
                          "earlier_lines": EARLIER},
                 roles=[{"label": "Managers", "roleType": "MANAGER", "about": "runs it"}], **kw)


MEASUREMENTS = [
    {"index": 0, "stage": "PROBLEM", "heading": "It costs them hours",
     "statement": "It costs one to two hours.", "risk": "LOAD_BEARING", "mark": "DIRECT",
     "role": "Managers",
     "expectation": {"type": "INTERVAL",
                     "measure": {"kind": "DURATION", "unit": "hours", "per": None},
                     "lower": {"value": 1, "inclusive": True, "exact": False},
                     "upper": {"value": 2, "inclusive": True, "exact": False}}},
    {"index": 1, "stage": "SOLUTION", "heading": "They would look in the tool",
     "statement": "They would look into it in the tool itself.", "risk": "SUPPORTING",
     "mark": "DIRECT", "role": "Managers",
     "expectation": {"type": "CHOICE", "options": ["yes", "no"], "expected": "yes"}},
]


def _questions_case(measurements=()):
    return _case("QUESTIONS", "QUESTIONS", "QUESTIONS",
                 context={"project_name": "Entry", "market": {"country": "GB"},
                          "measurements": list(measurements)})


# ---------------------------------------------------------------------------- FR-018: the shapes

def test_an_assumptions_case_carries_the_earlier_beliefs_in_the_order_earlier_lines_numbered_them():
    batch = validate_mod.build_batch([(_assumptions_case(), {"assumptions": []})])

    case = batch["cases"][0]
    assert case["screen"] == "SOLUTION_ASSUMPTIONS"
    assert [(b["stage"], b["line"]) for b in case["earlier_beliefs"]] == [("PROBLEM", 1),
                                                                         ("PROBLEM", 2)]
    assert case["earlier_beliefs"] == EARLIER, \
        "the same objects the context carried -- one place decides the ordinal"
    assert case["statement"] == "The solution."
    assert case["roles"][0]["label"] == "Managers"


def test_an_assumptions_case_with_no_earlier_stage_carries_an_empty_list_rather_than_no_key():
    case = _case("ASSUMPTIONS", "PROBLEM", "PROBLEM_ASSUMPTIONS",
                 context={"problem_statement": "The problem."})

    batch = validate_mod.build_batch([(case, {"assumptions": []})])

    assert batch["cases"][0]["earlier_beliefs"] == []


def test_a_questions_case_is_emitted_as_its_own_kind_and_carries_no_earlier_beliefs():
    """It names no stage and reads no earlier line: the whole project's settled measurements are
    what it was handed, and they travel on their own key."""
    batch = validate_mod.build_batch([(_questions_case(), {"introduction": "x", "anchors": []})])

    case = batch["cases"][0]
    assert case["screen"] == "QUESTIONS"
    assert "earlier_beliefs" not in case
    assert case["measurements"] == []


def test_a_questions_case_carries_the_measurements_the_model_was_given_in_their_own_order():
    """FR-018, Discovered D18. `reads` is a 0-based index into this array; an array the validator
    seeded itself resolves the index to a belief the model never saw."""
    batch = validate_mod.build_batch(
        [(_questions_case(MEASUREMENTS), {"introduction": "x", "anchors": []})])

    case = batch["cases"][0]
    assert [m["index"] for m in case["measurements"]] == [0, 1]
    assert case["measurements"] == MEASUREMENTS, \
        "the same objects the context carried -- one place decides the index"


def test_a_questions_case_whose_context_carried_no_measurements_carries_an_empty_list():
    batch = validate_mod.build_batch([(_questions_case(), {"anchors": []})])
    assert batch["cases"][0]["measurements"] == []


def test_a_case_that_produced_nothing_is_not_in_the_batch():
    batch = validate_mod.build_batch([(_assumptions_case(), None)])
    assert batch["cases"] == []


# ------------------------------------------------------------- FR-019: what the validator cannot do

def test_a_batch_needs_only_the_shapes_it_actually_reaches_for():
    """A run is never failed for a capability nothing in it used. A reference that was never
    written needs no `earlier_beliefs`."""
    plain = validate_mod.build_batch([(_assumptions_case(), {"assumptions": [{"heading": "h"}]})])
    assert validate_mod.shapes_needed(plain) == set()

    referencing = validate_mod.build_batch([(_assumptions_case(), {"assumptions": [
        {"heading": "h", "reads": {"stage": "PROBLEM", "line": 1}}]})])
    assert validate_mod.shapes_needed(referencing) == {"earlier_beliefs"}

    questions = validate_mod.build_batch([(_questions_case(), {"anchors": []})])
    assert validate_mod.shapes_needed(questions) == {"questions"}

    seeded = validate_mod.build_batch([(_questions_case(MEASUREMENTS), {"anchors": []})])
    assert validate_mod.shapes_needed(seeded) == {"questions", "measurements"}


def test_an_unreadable_sibling_takes_no_shape_at_all(tmp_path):
    """A prerequisite that has not landed is not a capability to assume."""
    assert validate_mod.shapes_taken(tmp_path) == {"earlier_beliefs": False, "questions": False,
                                                   "measurements": False}


def test_a_shape_the_validator_does_not_take_is_named_with_its_prerequisite(tmp_path):
    batch = validate_mod.build_batch([(_questions_case(), {"anchors": []})])

    reasons = validate_mod.unmet_prerequisites(tmp_path, batch)

    assert len(reasons) == 1
    assert "QUESTIONS" in reasons[0]
    assert "Prerequisite for keel-cloud" in reasons[0]
    assert "spec 048 FR-015" in reasons[0]


def test_a_questions_case_the_validator_cannot_seed_from_measurements_is_named_by_its_own_key(
        tmp_path):
    """FR-019 for the key D18 added: a canned project of three beliefs makes every index past the
    third a shape refusal of the eval's own making, so the marks go unmeasured by name."""
    batch = validate_mod.build_batch([(_questions_case(MEASUREMENTS), {"anchors": []})])

    reasons = validate_mod.unmet_prerequisites(tmp_path, batch)

    seeding = [r for r in reasons if "`measurements`" in r]
    assert len(seeding) == 1
    assert "canned project of three settled beliefs" in seeding[0]
    assert "`rule_refusal_rate` and `shape_refusals` are UNMEASURED" in seeding[0]


def test_a_reference_with_no_earlier_beliefs_support_names_the_marks_it_leaves_unmeasured(tmp_path):
    batch = validate_mod.build_batch([(_assumptions_case(), {"assumptions": [
        {"heading": "h", "reads": {"stage": "PROBLEM", "line": 1}}]})])

    reasons = validate_mod.unmet_prerequisites(tmp_path, batch)

    assert len(reasons) == 1
    assert "rule_refusal_rate` and `shape_refusals` are UNMEASURED" in reasons[0]
    assert "they are not zero, and they are not met" in reasons[0]


def test_a_batch_that_reaches_for_nothing_has_no_unmet_prerequisite(tmp_path):
    batch = validate_mod.build_batch([(_assumptions_case(), {"assumptions": [{"heading": "h"}]})])
    assert validate_mod.unmet_prerequisites(tmp_path, batch) == []


def test_the_shapes_are_read_off_keel_clouds_own_validator():
    """Reading a sibling to learn a fact about it is what this package already does for the
    contract, the instructions and the routing table; what it never does is keep a copy."""
    from stack.config import load_config                                    # noqa: PLC0415

    taken = validate_mod.shapes_taken(load_config(validate=False).keel_cloud)

    assert set(taken) == {"earlier_beliefs", "questions", "measurements"}
    assert all(isinstance(v, bool) for v in taken.values())
