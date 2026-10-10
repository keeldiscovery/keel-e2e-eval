"""The seven context builders at `MARKS_VERSION` 11 (spec 029 contracts/screen-shapes.md §2; T018;
spec 030: the calibrated slice per persona, call 47; spec 031: the names and figures, calls 55, 57).

Every key the exporter names, in the exporter's order, filled from the corpus entry and the
registry and nothing else -- and, as much to the point, what each one must **not** carry: no
solution field on the PROBLEM calibration job (US2.1), no mechanism and no founder answer on Part 1,
no `stage` and no `anchors[]` on a read, no `claims` on the brief.
"""

from __future__ import annotations

import pytest

from instructions import context as context_mod
from tests import v9_fixtures as fx


@pytest.fixture()
def entry():
    return fx.entry()


@pytest.fixture()
def registry():
    return fx.registry()


def test_every_builder_fills_the_exporters_keys_in_the_exporters_order(entry, registry):
    keys = ["market", "unknown_key", "project_name", "context_fields"]
    built = context_mod.build_context_interpret(entry, keys)
    assert list(built) == keys, "the order is the contract (ScreenContextBuilder's LinkedHashMap)"
    assert built["unknown_key"] is None, "an unknown key is written null, never dropped"


def test_context_interpret_carries_the_four_slots_and_nothing_from_the_mechanism(entry):
    built = context_mod.build_context_interpret(entry)
    assert built["context_fields"] == {"who": "commuter", "what": "get out of the door on time",
                                       "when": "the morning they cannot find their keys",
                                       "which_people": "commuters in Leeds who cycle to work",
                                       "recall_window": {"count": 7, "unit": "NIGHTS"}}, \
        "an entry with no window sends the default, as proposeContext sends the founder's"
    assert built["project_name"] == entry.title
    assert "whistle" not in repr(built) and "tag" not in repr(built)


def test_problem_interpret_carries_the_context_and_no_solution_field(entry):
    built = context_mod.build_problem_interpret(entry)
    assert set(built) == {"context", "market"}
    assert built["context"]["window"] == "the last 7 nights", \
        "058's slots carry the recall window's words"
    assert built["context"]["actor_plural"] == "commuters who cycle"
    assert context_mod.seed_of(entry, "PROBLEM_INTERPRET") == entry.statements["problem"]


def test_solution_mechanism_reads_the_corpus_problem_sentence_never_a_live_answer(entry):
    built = context_mod.build_solution_mechanism(entry)
    assert built["problem_statement"] == entry.interpretations["problem"]
    assert context_mod.seed_of(entry, "SOLUTION_MECHANISM") == entry.statements["solution"]


def _dotted(dimension: dict) -> set:
    out = set()
    for key, value in dimension.items():
        if key in ("founder", "respondent"):
            out |= {f"{key}.{inner}" for inner in value}
        else:
            out.add(key)
    return out


def test_the_problem_calibration_job_carries_the_slice_with_thirteen_fields_and_no_solution(
        entry, registry):
    built = context_mod.build_calibration(entry, "PROBLEM", registry)
    assert built["vector"] == "PROBLEM"
    assert built["interpretation"] == {"statement": entry.interpretations["problem"]}, \
        "US2.1: the PROBLEM job's interpretation is the problem statement and no solution field"
    assert "mechanism" not in built and "solution" not in built and "persona" not in built
    prevalence = built["dimensions"][0]
    assert "{window}" not in repr(prevalence) and "7 nights" in prevalence["founder"]["guidance"], \
        "the registry's window placeholders are filled, as 058's RegistrySlices.filled does"
    dimensions = built["dimensions"]
    assert [d["key"] for d in dimensions] == \
        [d.key for d in registry.calibrated_slice("PROBLEM", entry.b2b())]
    assert len(dimensions) == 4
    expected = {"key", "order", "name", "meaning", "weight", "founder.control", "founder.guidance",
                "founder.normalized", "founder.option_rule", "founder.belief_template",
                "founder.unsure_allowed", "respondent.anchor", "respondent.guidance"}
    for dimension in dimensions:
        assert _dotted(dimension) == expected, dimension["key"]


def test_the_solution_and_commercial_jobs_see_the_mechanism_and_the_persona(entry, registry):
    solution = context_mod.build_calibration(entry, "SOLUTION", registry)
    card = solution["interpretation"]
    assert card["mechanism"] == entry.solution_mechanism["mechanism"]
    assert card["mechanism_terms"] == entry.solution_mechanism["mechanism_terms"]
    assert "not_assumed" not in card, "the claims the card stripped are never handed on"
    assert card["short_name"] is None, "call 55: the corpus records no short name at r5"
    commercial = context_mod.build_calibration(entry, "COMMERCIAL", registry)
    assert commercial["interpretation"] == {"summary": None, "decider_role": None, "b2b": False,
                                            "offer_name": None}, \
        "072: the persona map with the offer's name (none recorded at r5, call 55)"
    keys = [d["key"] for d in commercial["dimensions"]]
    assert keys == ["commercial.existing_sacrifice", "commercial.price",
                    "commercial.buyer_payer_alignment", "commercial.commitment"], \
        "call 47: a B2C job is never shown the b2b_only pair; Price is asked of whoever pays"
    b2b = fx.entry(fx.ENTRY_B2B)
    built = context_mod.build_calibration(b2b, "COMMERCIAL", registry)
    assert len(built["dimensions"]) == 6 and built["interpretation"]["b2b"] is True


def test_a_name_the_corpus_records_reaches_the_job_and_the_validator(entry, registry):
    """Call 55: a short name / offer name the corpus records is handed on as keel-cloud hands it --
    on the SOLUTION card and the respondents' mechanism, on the COMMERCIAL persona map and part 3."""
    import dataclasses                                                      # noqa: PLC0415
    named = dataclasses.replace(
        entry, solution_mechanism=dict(entry.solution_mechanism, short_name="a beeping tag"),
        interpretations=dict(entry.interpretations, offer_name="a way to find the keys"))
    assert context_mod.build_calibration(named, "SOLUTION", registry)["interpretation"][
        "short_name"] == "a beeping tag"
    assert context_mod.build_calibration(named, "COMMERCIAL", registry)["interpretation"][
        "offer_name"] == "a way to find the keys"
    keys = context_mod.DEFAULT_KEYS["RESPONDENT_QUESTIONS"] + ["offer_name"]
    part3 = context_mod.build_respondent(named, 3, named.plan(registry), registry, keys)
    assert part3["offer_name"] == "a way to find the keys"
    assert part3["mechanism"]["short_name"] == "a beeping tag"
    assert "offer_name" not in context_mod.build_respondent(named, 1, named.plan(registry),
                                                            registry, keys), "part 3 only"
    assert context_mod.validation_mechanism(named)["short_name"] == "a beeping tag"
    assert "offer_name" not in context_mod.build_respondent(named, 3, named.plan(registry),
                                                            registry), \
        "the export decides the keys: 073's context-keys.json names no offer_name"


def test_part_one_carries_no_mechanism_and_no_founder_answer_ever(entry, registry):
    plan = entry.plan()
    built = context_mod.build_respondent(entry, 1, plan, registry)
    assert "mechanism" not in built
    assert [item["key"] for item in built["items"]] == plan[1]
    assert set(built["items"][0]["respondent"]) == {"anchor", "control", "guidance",
                                                     "option_rule", "chips"}
    text = repr(built)
    for value in ("one of the top three", "is hit and miss", "2 to 4 nights", "hit_and_miss"):
        assert value not in text, f"a founder answer reached the respondent screen: {value}"
    assert built["founder_options"] == {}, \
        "058's founderOptions: the model-written sets only, and Part 1 has none at v10"
    part3 = context_mod.build_respondent(entry, 3, plan, registry)
    assert part3["founder_options"]["commercial.existing_sacrifice"] == \
        ["spare_keys", "locksmith", "none", "nothing"], "the founder's option SET, never their pick"


def test_the_respondent_screen_is_shown_the_founders_labels_where_the_entry_records_them(registry):
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    lullaby = corpus_mod.load_file(fx.canon_entry("03-lullaby.yaml"), registry=registry)
    part3 = context_mod.build_respondent(lullaby, 3, lullaby.plan(), registry)
    assert part3["founder_options"]["commercial.commitment"][1] == "Install the app", \
        "058 (afe36fd): production sends the calibration's LABELS, never the codes"
    assert part3["founder_options"]["commercial.existing_sacrifice"][-1] == \
        "None of these; they cope with what they have"


def test_parts_two_and_three_carry_the_mechanism_and_the_b2b_link_does_not(entry, registry):
    for part in (2, 3):
        built = context_mod.build_respondent(entry, part, entry.plan(), registry)
        assert built["mechanism"]["output"] == entry.solution_mechanism["output"]
        assert built["link"] == "PRIMARY"
    b2b = context_mod.build_respondent(entry, 3, entry.plan(), registry,
                                       link=context_mod.LINK_B2B)
    assert "mechanism" not in b2b, "058: the decision-maker's link carries no mechanism key"


def test_the_b2b_link_carries_the_registrys_b2b_block():
    b2b = fx.entry(fx.ENTRY_B2B)
    built = context_mod.build_respondent(b2b, 3, b2b.plan(), b2b.registry,
                                         link=context_mod.LINK_B2B)
    assert built["link"] == "COMMERCIAL_B2B"
    sacrifice = next(i for i in built["items"] if i["key"] == "commercial.existing_sacrifice")
    assert sacrifice["respondent"]["b2b"]["anchor"] == "last_cycle"


def test_a_read_carries_an_invitation_and_one_story_and_no_stage_or_anchors(entry):
    person = entry.person("Bo Brand")
    built = context_mod.build_interpret(entry, person)
    assert built == {"invitation_id": "09-fixture/Bo Brand",
                     "story": {"prompt": None, "text": person.story, "chip": None}}
    assert "anchors" not in built and "stage" not in repr(built)


def test_the_brief_carries_three_vectors_with_their_verdicts_and_belief_sentences(entry, registry):
    built = context_mod.build_brief(entry)
    assert list(built) == ["project_name", "market", "context", "vectors"]
    assert "claims" not in built
    vectors = built["vectors"]
    assert [v["vector"] for v in vectors] == ["PROBLEM", "SOLUTION", "COMMERCIAL"]
    problem = vectors[0]
    assert (problem["verdict"], problem["deciding"]) == ("NOT_HOLDING_UP", "problem.importance")
    assert [d["key"] for d in problem["dimensions"]] == \
        [d.key for d in registry.calibrated_slice("PROBLEM", entry.b2b())]
    frequency = next(d for d in problem["dimensions"] if d["key"] == "problem.frequency")
    assert frequency["belief_sentence"] == \
        entry.founder_calibration["problem.frequency"]["belief_sentence"]
    assert frequency["founder_phrase"] == "2 to 4 nights out of 7"
    assert frequency["observed"] == "2.5 nights out of 7", \
        "the median in the founder's own unit (call 19)"
    assert frequency["below"] is None and frequency["above"] is None
    commercial = vectors[2]
    assert [d["key"] for d in commercial["dimensions"]] == [
        "commercial.existing_sacrifice", "commercial.price", "commercial.buyer_payer_alignment",
        "commercial.commitment"], "call 47: a B2C brief carries no b2b_only row"
    price = commercial["dimensions"][1]
    assert price["observed"] == "4 of 8 said it would be worth £2 a month or more", "call 57"
    assert commercial["dimensions"][0]["observed"] == "a median £12 over three months"


def test_the_stage_shaped_builders_are_gone():
    for name in ("earlier_lines", "build_questions", "anchors_for", "roles_for",
                 "measurements_for", "claims_for", "build_assumptions", "build_reading"):
        assert not hasattr(context_mod, name), name


@pytest.mark.parametrize("name, window, words", [
    ("01-countly.yaml", {"count": 1, "unit": "MONTHS"}, "the last month"),
    ("02-compliancelog.yaml", {"count": 3, "unit": "MONTHS"}, "the last 3 months"),
    ("03-lullaby.yaml", {"count": 7, "unit": "NIGHTS"}, "the last 7 nights"),
    ("06-repeatline.yaml", {"count": 1, "unit": "SHIFTS"}, "the last shift"),
])
def test_an_r4_entrys_own_window_reaches_every_screen_that_reads_it(name, window, words):
    """keel-cloud 058 `5fc7220`: `context.recall_window` is sent as `{count, unit}` on
    CONTEXT_INTERPRET (`proposeContext`) and as its words in the slots (`ScreenContextBuilder`),
    and fills the registry's `{window}` in every calibration slice."""
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    entry = corpus_mod.load_file(fx.canon_entry(name), registry=fx.registry())
    assert context_mod.build_context_interpret(entry)["context_fields"]["recall_window"] == window
    assert context_mod.build_problem_interpret(entry)["context"]["window"] == words
    slice_ = context_mod.build_calibration(entry, "PROBLEM", fx.registry())["dimensions"]
    assert words in repr(slice_) and "{window}" not in repr(slice_)
