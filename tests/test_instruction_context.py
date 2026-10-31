"""The eight context builders at `MARKS_VERSION` 18 (spec 029 contracts/screen-shapes.md §2; T018;
spec 030: the calibrated slice per persona, call 47; spec 031: the names, call 55; spec 040: contract 13 --
the founder-lists job's `saves` and `answers`, the respondent items' one `escape`, the ASKED job, the brief's
facts, calls 83-85).

Every key the exporter names, in the exporter's order, filled from the corpus entry and the
registry and nothing else -- and, as much to the point, what each one must **not** carry: no
solution field on the PROBLEM calibration job (US2.1), no weight anywhere (D3), no mechanism and no
founder answer on Part 1, no `founder_options` on any respondent job (keel-cloud 087), no `stage` and no
`anchors[]` on a read, no `claims` on the brief.
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


def test_the_problem_calibration_job_carries_the_slice_its_saves_and_no_solution(entry, registry):
    """`RegistrySlices.calibrationSlice` (keel-cloud 087): no weight, a list dimension's `saves`, a founder field the
    registry leaves out not written; the seed-time job's `answers` is empty (087 call 8)."""
    built = context_mod.build_calibration(entry, "PROBLEM", registry)
    assert built["vector"] == "PROBLEM"
    assert built["answers"] == {}, "the corpus records no Answer-screen text"
    assert list(built) == context_mod.DEFAULT_KEYS["CALIBRATION_QUESTIONS"]
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
    expected = {"key", "order", "name", "meaning", "founder.control", "founder.guidance",
                "founder.normalized", "founder.option_rule", "founder.belief_template",
                "founder.unsure_allowed", "respondent.anchor", "respondent.guidance"}
    for dimension in dimensions:
        listed = registry.by_key(dimension["key"]).founder_list
        assert _dotted(dimension) == expected | ({"founder.saves"} if listed else set()), dimension["key"]
        assert "weight" not in repr(dimension), "D3: all thirteen decide"
    importance = next(d for d in dimensions if d["key"] == "problem.importance")
    assert importance["founder"]["saves"]["min_items"] == importance["founder"]["saves"]["max_items"] == 5


def test_the_solution_and_commercial_jobs_see_the_mechanism_and_the_persona(entry, registry):
    solution = context_mod.build_calibration(entry, "SOLUTION", registry)
    card = solution["interpretation"]
    assert card["mechanism"] == entry.solution_mechanism["mechanism"]
    assert card["mechanism_terms"] == entry.solution_mechanism["mechanism_terms"]
    assert "not_assumed" not in card, "the claims the card stripped are never handed on"
    assert card["short_name"] == "a tag that beeps back", "call 55: the corpus's own short name"
    commercial = context_mod.build_calibration(entry, "COMMERCIAL", registry)
    assert commercial["interpretation"] == {"summary": None, "decider_role": None, "b2b": False,
                                            "offer_name": "a fix for lost keys"}, \
        "072: the persona map with the offer's name (call 55)"
    keys = [d["key"] for d in commercial["dimensions"]]
    assert keys == ["commercial.existing_sacrifice", "commercial.price",
                    "commercial.buyer_payer_alignment", "commercial.commitment"], \
        "calls 47, 61: a B2C job is never shown Purchase friction, nor the derived Ability to pay"
    b2b = fx.entry(fx.ENTRY_B2B)
    built = context_mod.build_calibration(b2b, "COMMERCIAL", registry)
    assert len(built["dimensions"]) == 5 and built["interpretation"]["b2b"] is True
    assert "commercial.ability_to_pay" not in [d["key"] for d in built["dimensions"]]


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
    no_offer = [k for k in keys if k != "offer_name"]
    assert "offer_name" not in context_mod.build_respondent(named, 3, named.plan(registry),
                                                            registry, no_offer), \
        "the export decides the keys: a key list without offer_name writes none"


def test_part_one_carries_no_mechanism_and_no_founder_answer_ever(entry, registry):
    """keel-cloud 087 / 088: each item carries the registry's respondent fields with its one `escape` (no
    `chips`), and no respondent job is handed `founder_options` -- every respondent word is code's."""
    plan = entry.plan()
    built = context_mod.build_respondent(entry, 1, plan, registry)
    assert list(built) == [k for k in context_mod.DEFAULT_KEYS["RESPONDENT_QUESTIONS"]
                           if k not in ("mechanism", "offer_name")]
    assert "mechanism" not in built and "founder_options" not in built
    assert [item["key"] for item in built["items"]] == plan[1]
    for item in built["items"]:
        assert set(item["respondent"]) == {"anchor", "control", "guidance", "option_rule", "escape"}
        assert "chips" not in repr(item)
    frequency = next(i for i in built["items"] if i["key"] == "problem.frequency")
    assert frequency["respondent"]["escape"] == {"code": "cant_recall", "label": "I can't recall",
                                                 "counts": "apart"}
    gate = next(i for i in built["items"] if i["key"] == "problem.prevalence")
    assert gate["respondent"]["escape"] is None, "the gate has no way out"
    text = repr(built)
    for value in ("Finding the keys on the way out", "your way of finding them", "2 to 4 nights", "p_60_80"):
        assert value not in text, f"a founder answer reached the respondent screen: {value}"
    part3 = context_mod.build_respondent(entry, 3, plan, registry)
    assert "founder_options" not in part3
    commitment = next(i for i in part3["items"] if i["key"] == "commercial.commitment")
    assert commitment["respondent"]["escape"] is None, "Commitment has none"
    assert "install the app" not in repr(part3)


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


def test_no_screen_builds_a_brief_context_since_keel_cloud_104(entry, registry):
    """Spec 052 (call 116): keel-cloud 104 deleted the BRIEF screen, so no context is built for it; the facts this
    repository reads (`brief_facts.facts_for`, what `instructions/overview.py` draws from) keep their shape: the
    decision over every dimension, the vector words, the money, the pilot, one card a dimension, what broke, what was
    not asked and the price median."""
    from instructions import brief_facts                                # noqa: PLC0415
    assert not hasattr(context_mod, "build_brief") and "BRIEF" not in context_mod.DEFAULT_KEYS
    facts = brief_facts.facts_for(entry, registry)
    assert [v["words"] for v in facts["vectors"]] == ["Holding up", "Holding up", "Not holding up"]
    assert facts["decision"] == {"label": "BUILD_BUT_CHANGE", "howSure": "MEDIUM",
                                 "reason": "Smallest group: 7 people.", "smallestN": 7, "split": False,
                                 "notTested": []}
    assert facts["money"] == {"currency": "GBP", "currencySymbol": "\u00a3", "period": "month",
                              "periodWords": "a month"}
    assert facts["pilot"]["optedIn"] == 3 and facts["pilot"]["finished"] == 10      # spec 064 FR-6a: gate Yes alone
    assert [c["key"] for c in facts["cards"]] == registry.calibrated_keys(False)
    assert facts["cards"][0]["number"] == "10 of 12" and facts["cards"][0]["line"] == "had it in the last 7 nights"
    assert facts["commercial"]["broke"]["key"] == "commercial.existing_sacrifice"
    assert "broke" not in facts["problem"] and "broke" not in facts["solution"]
    assert {n["key"] for n in facts["commercial"]["notAsked"]} == {
        "commercial.ability_to_pay", "commercial.buyer_payer_alignment", "commercial.purchase_friction"}
    assert facts["commercial"]["priceMedian"] == {"edgeSaid": "\u00a32 a month", "chose": 5, "n": 8}
    assert not {"sharpest", "targets", "keys"} & set(facts), "keel-cloud 104 deleted them"


def test_the_asked_job_is_one_list_its_frame_and_its_items_by_index(entry, registry):
    """keel-cloud 088 FR-003 (`ScreenContextBuilder`'s ASKED): `{key, name, frame}` with `{asked}` where the face
    goes, the slots, the market, and the founder's items `[{index, label}]` -- never the faces themselves."""
    built = context_mod.build_asked(entry, "solution.compatibility", registry)
    assert list(built) == context_mod.DEFAULT_KEYS["ASKED"] == ["dimension", "context", "market", "items"]
    assert built["dimension"] == {"key": "solution.compatibility", "name": "Compatibility",
                                  "frame": "On your last morning, {asked}?"}
    assert built["items"] == [{"index": 0, "label": "They had a phone to hand"},
                              {"index": 1, "label": "Their keys were on one ring"}]
    assert "asked\"" not in repr(built["items"]) and "did you have" not in repr(built), "the faces are the job's to write"
    adoption = context_mod.build_asked(entry, "solution.adoption_friction", registry)
    # spec 112 FR-4 (keel-cloud 171 FR-4b: `AskedRules.framed`, the asked job's frame): was *{asked}. Would you ...*
    assert adoption["dimension"]["frame"] == "To use it, you'd {asked}. Would you do that, or not?"
    assert adoption["items"] == [{"index": 0, "label": "Clip a tag to the key ring"}]
    assert built["context"]["window"] == "the last 7 nights"
    keys = ["items", "dimension", "unknown"]
    assert list(context_mod.build_asked(entry, "solution.compatibility", registry, keys)) == keys


def test_the_stage_shaped_builders_are_gone():
    for name in ("earlier_lines", "build_questions", "anchors_for", "roles_for",
                 "measurements_for", "claims_for", "build_assumptions", "build_reading"):
        assert not hasattr(context_mod, name), name


@pytest.mark.parametrize("name, window, words", [
    ("01-countly.yaml", {"count": 4, "unit": "WEEKS"}, "the last 4 weeks"),
    ("02-compliancelog.yaml", {"count": 3, "unit": "MONTHS"}, "the last 3 months"),
    ("03-lullaby.yaml", {"count": 7, "unit": "NIGHTS"}, "the last 7 nights"),
    ("06-repeatline.yaml", {"count": 7, "unit": "DAYS"}, "the last 7 days"),
])
def test_an_entrys_own_window_reaches_every_screen_that_reads_it(name, window, words):
    """keel-cloud 058 `5fc7220`, D13: `context.recall_window` is sent as `{count, unit}` on CONTEXT_INTERPRET and as
    its words in the slots, and fills the registry's `{window}` in every calibration slice -- 01's {1, MONTHS} is
    {4, WEEKS} and 06's {1, SHIFTS} {7, DAYS} at revision 10."""
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    entry = corpus_mod.load_file(fx.canon_entry(name), registry=fx.registry())
    assert context_mod.build_context_interpret(entry)["context_fields"]["recall_window"] == window
    assert context_mod.build_problem_interpret(entry)["context"]["window"] == words
    slice_ = context_mod.build_calibration(entry, "PROBLEM", fx.registry())["dimensions"]
    assert words in repr(slice_) and "{window}" not in repr(slice_)
