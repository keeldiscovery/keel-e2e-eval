"""`instructions/prompts.py`: production's payload, and keel-runtime's own renderer (FR-018).

The payload shape is `InferenceJobService.buildRequestPayload`'s, including the empty-content
sentinel an auto screen carries. The rendering is keel-runtime's `build_prompt`, imported from the
sibling checkout and never copied -- so this test also proves the import path works, which is the
thing that breaks silently when a sibling moves.
"""

from __future__ import annotations

import pytest

from instructions import prompts as prompts_mod
from stack.config import load_config

CONTRACT = {
    "allowed_outcomes": ["NEEDS_INPUT", "COMPLETED"],
    "completed_result_schema": {"type": "object", "required": ["assumptions"],
                                "properties": {"assumptions": {"type": "array"}}},
    "needs_input_schema": {"type": "object", "required": ["questions"]},
}


@pytest.fixture(scope="module")
def executor_module():
    config = load_config(validate=False)
    try:
        executor, _validator = prompts_mod.load_runtime(config.keel_runtime)
    except prompts_mod.RuntimeUnavailable as reason:
        pytest.skip(str(reason))
    return executor


def test_the_payload_is_production_s_four_keys_with_the_empty_content_sentinel():
    payload = prompts_mod.payload_for("THE INSTRUCTION", {"problem_statement": "x"}, CONTRACT)

    assert list(payload) == ["instruction", "context", "interaction_history", "input",
                             "response_contract"]
    assert payload["interaction_history"] == [], "this is always turn one"
    assert payload["input"] == {"content": ""}, \
        "an auto screen carries the empty-string sentinel, not a founder's typing"
    assert payload["response_contract"] is CONTRACT, "the contract goes in whole and unreshaped"


def test_the_prompt_is_keel_runtimes_own_and_carries_the_context_verbatim(executor_module):
    payload = prompts_mod.payload_for(
        "THE INSTRUCTION", {"problem_statement": "Managers lose two hours.", "market": None},
        CONTRACT)

    prompt = prompts_mod.render(executor_module, payload)

    assert prompt.startswith("TASK\nTHE INSTRUCTION")
    assert "CONTRACT" in prompt
    assert "SOURCE MATERIAL" in prompt.upper()
    assert "<<<KEEL-DATA " in prompt and "<<<END KEEL-DATA " in prompt
    assert "project_context:" in prompt
    assert "Managers lose two hours." in prompt
    assert "founder_text:" in prompt


def test_the_nonce_is_fresh_on_every_call_so_the_fence_cannot_be_guessed(executor_module):
    payload = prompts_mod.payload_for("i", {"a": 1}, CONTRACT)

    first = prompts_mod.render(executor_module, payload)
    second = prompts_mod.render(executor_module, payload)

    assert first != second, "two renderings differ only in the nonce, and they must differ"
    assert first.replace(_nonce(first), "N") == second.replace(_nonce(second), "N")


def _nonce(prompt: str) -> str:
    marker = "<<<KEEL-DATA "
    start = prompt.index(marker) + len(marker)
    return prompt[start:prompt.index(">>>", start)]


# ------------------------------------------------- spec 029 FR-016: the eight subjects, in order


from instructions import run as run_mod                                        # noqa: E402
from tests import v9_fixtures as fx                                            # noqa: E402


@pytest.fixture()
def cases(tmp_path):
    return prompts_mod.build_cases(fx.entry(), fx.exported(tmp_path), fx.instructions(),
                                   fx.FakeRuntime, n_runs=1)


def test_the_seeded_screens_carry_the_seed_as_input_content():
    payload = prompts_mod.payload_for("i", {}, CONTRACT, content="the founder typed this")
    assert payload["input"] == {"content": "the founder typed this"}


def test_build_cases_emits_twenty_model_cases_and_one_compare_row_in_fr_016s_order(cases):
    """Spec 040 (call 84): the two `ASKED` cases -- one a saved Compatibility and Adoption friction list -- come
    after the three calibration jobs, as a Save does after the Check screens."""
    ids = [c.case_id for c in cases]
    assert ids[:11] == [
        "09-fixture/CONTEXT_INTERPRET/run1", "09-fixture/PROBLEM_INTERPRET/run1",
        "09-fixture/SOLUTION_MECHANISM/run1", "09-fixture/CALIBRATION_PROBLEM/run1",
        "09-fixture/CALIBRATION_SOLUTION/run1", "09-fixture/CALIBRATION_COMMERCIAL/run1",
        "09-fixture/ASKED_COMPATIBILITY/run1", "09-fixture/ASKED_ADOPTION_FRICTION/run1",
        "09-fixture/RESPONDENT_PART1/run1", "09-fixture/RESPONDENT_PART2/run1",
        "09-fixture/RESPONDENT_PART3/run1"]
    reads = [c for c in cases if c.kind == "READING"]
    assert len(reads) == 9 and ids[11:20] == [c.case_id for c in reads]
    assert {c.subject for c in reads}.isdisjoint({"Jo Judd", "Kit Kerr", "Lu Lam"}), \
        "no read for a gate-No or a chipped story (FR-017)"
    assert ids[20:] == ["09-fixture/COMPARE"], "no BRIEF case since keel-cloud 104 (spec 052, call 116)"
    model = [c for c in cases if c.kind != "COMPARE"]
    assert len(model) == 20, "SC-003: 3 + 3 + 2 + 3 + 9"
    assert [c.kind for c in cases[:11]] == ["CONTEXT", "FRAME", "FRAME"] + ["CALIBRATION"] * 3 \
        + ["ASKED"] * 2 + ["RESPONDENT"] * 3


def test_an_asked_case_is_handed_its_list_by_index_and_keeps_it_for_the_scorer(cases):
    asked = next(c for c in cases if c.case_id == "09-fixture/ASKED_COMPATIBILITY/run1")
    assert asked.screen == "ASKED" and asked.subject == "COMPATIBILITY"
    assert asked.meta["dimension"] == "solution.compatibility"
    assert asked.meta["items"] == asked.payload["context"]["items"] == [
        {"index": 0, "label": "They had a phone to hand"}, {"index": 1, "label": "Their keys were on one ring"}]
    assert asked.meta["validation_mechanism"]["mechanism_terms"] == ["tag", "whistle", "beep", "key ring"]
    assert "did you have your phone" not in asked.prompt, "the corpus's own faces are the golden, never shown"


def test_a_list_left_out_builds_no_asked_case(tmp_path):
    import dataclasses                                                      # noqa: PLC0415
    entry = fx.entry()
    calibration = dict(entry.founder_calibration)
    calibration["solution.adoption_friction"] = {"unsure": True, "belief_sentence": "Left out."}
    left = dataclasses.replace(entry, founder_calibration=calibration)
    cases = prompts_mod.build_cases(left, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, n_runs=1)
    assert [c.subject for c in cases if c.kind == "ASKED"] == ["COMPATIBILITY"]


def test_no_brief_case_is_built_and_build_cases_takes_no_facts(tmp_path):
    """Spec 052 (call 116): keel-cloud 104 deleted the BRIEF screen; no case kind, no facts handed in."""
    import inspect                                                           # noqa: PLC0415
    cases = prompts_mod.build_cases(fx.entry(), fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, n_runs=1)
    assert "BRIEF" not in {c.kind for c in cases} and "BRIEF" not in prompts_mod.KINDS
    assert "brief_facts" not in inspect.signature(prompts_mod.build_cases).parameters


def test_the_real_corpus_builds_142_model_cases_and_the_denominators_per_n(tmp_path):
    """Spec 040: on revision 10 at N=1 -- 7 context, 14 frame, 21 calibration, 14 asked, 21 respondent, 65 reads
    (142; the 7 briefs left with keel-cloud 104, spec 052) and 7 COMPARE rows; coverage 80 calibration + 81 respondent + 35 asked, validity 122 (80 entries,
    7 gates, 35 faces), `no_leak` 35 sweeps (sweep A on 4 PROBLEM entries and the gate, sweep B on the gate, an
    entry). Read off the cases, never typed."""
    from stack.config import load_config                                    # noqa: PLC0415
    from instructions import corpus as corpus_mod                           # noqa: PLC0415
    for name in ("01-countly", "07-mulchrun"):
        fx.canon_entry(f"{name}.yaml")
    corpus = corpus_mod.load(load_config(validate=False).keel_cloud, registry=fx.registry())
    exported = fx.exported(tmp_path)
    cases = []
    for entry in corpus.entries:
        cases += prompts_mod.build_cases(entry, exported, fx.instructions(), fx.FakeRuntime, n_runs=1)
    counts = run_mod._counts(cases)
    assert counts == {"CONTEXT": 7, "FRAME": 14, "CALIBRATION": 21, "ASKED": 14, "RESPONDENT": 21,
                      "READING": 65, "COMPARE": 7}
    assert sum(n for kind, n in counts.items() if kind != "COMPARE") == 142
    rows = run_mod.denominators(cases)
    assert sum(r["calibration"] for r in rows.values()) == 80
    assert sum(sum(r["respondent"].values()) for r in rows.values()) == 81
    assert sum(r["asked"] for r in rows.values()) == 35
    assert sum(r["validity"] for r in rows.values()) == 122
    assert sum(r["sweep_a"] + r["sweep_b"] for r in rows.values()) == 35
    assert run_mod._denominator_line(rows) == (
        "denominators read off the registry, per N: dimension_coverage 80 calibration + 81 respondent + 35 asked "
        "· option_validity 122 · no_leak 35 sweeps")


def test_the_compare_row_is_a_row_and_never_a_call(cases):
    row = next(c for c in cases if c.kind == "COMPARE")
    assert row.payload == {} and row.prompt == "" and row.run_index == 0
    assert row.compare_input["entry"] == "09-fixture"
    assert len(row.compare_input["founder_calibration"]) == len(fx.entry().calibrated_keys()) \
        == 12, "calls 47, 59: the entry's calibrated set, read"


def test_the_b2b_entry_asks_part_three_on_its_own_link_and_nowhere_else(tmp_path):
    """Call 47 (keel-cloud `EvidencePlan`, decision 26): part 3 of a B2B study is the
    decision-maker's COMMERCIAL_B2B job -- three respondent jobs on either persona, never four."""
    cases = prompts_mod.build_cases(fx.entry(fx.ENTRY_B2B), fx.exported(tmp_path),
                                    fx.instructions(), fx.FakeRuntime, n_runs=1)
    b2b = [c for c in cases if c.case_id.endswith("RESPONDENT_B2B/run1")]
    assert len(b2b) == 1 and b2b[0].meta["link"] == "COMMERCIAL_B2B"
    assert b2b[0].meta["part"] == 3
    assert "commercial.ability_to_pay" in b2b[0].meta["plan"]
    respondent = [c.subject for c in cases if c.kind == "RESPONDENT"]
    assert respondent == ["PART1", "PART2", "B2B"]


def test_n_runs_repeats_each_model_case_and_never_the_compare_row(tmp_path):
    cases = prompts_mod.build_cases(fx.entry(), fx.exported(tmp_path), fx.instructions(),
                                    fx.FakeRuntime, n_runs=3)
    assert len([c for c in cases if c.kind != "COMPARE"]) == 60, "SC-010"
    assert len([c for c in cases if c.kind == "COMPARE"]) == 1


def test_every_payload_carries_its_screens_instruction_and_its_contract(cases):
    for case in cases:
        if case.kind == "COMPARE":
            continue
        assert case.payload["instruction"] == f"INSTRUCTION FOR {case.screen}"
        assert "COMPLETED" in case.payload["response_contract"]["allowed_outcomes"]
        assert case.prompt.startswith(f"INSTRUCTION FOR {case.screen}")


def test_the_respondent_case_keeps_the_founder_values_for_the_batch_and_out_of_the_prompt(cases):
    part1 = next(c for c in cases if c.case_id == "09-fixture/RESPONDENT_PART1/run1")
    frequency = part1.meta["founder_values"]["problem.frequency"]
    assert frequency["answer"] == {"lower": 2, "upper": 4, "unit": "nights out of 7"}
    assert "2 to 4 nights" not in part1.prompt
    assert part1.meta["swept"] == ["problem.prevalence"], "call 83: the gate's clause is the one swept"
    part2 = next(c for c in cases if c.case_id == "09-fixture/RESPONDENT_PART2/run1")
    assert part2.meta["swept"] == []


def _select(cases, needle):
    return run_mod.select(cases, needle)


def test_a_slash_needle_selects_the_reads_and_no_interpretation(cases):
    selected = _select(cases, "09-fixture/INTERPRET")
    assert len(selected) == 9 and {c.kind for c in selected} == {"READING"}


@pytest.mark.parametrize("word, kind, count", [
    ("context", "CONTEXT", 1), ("frame", "FRAME", 2), ("calibration", "CALIBRATION", 3),
    ("asked", "ASKED", 2), ("respondent", "RESPONDENT", 3), ("reading", "READING", 9), ("compare", "COMPARE", 1)])
def test_each_kind_word_selects_its_kind(cases, word, kind, count):
    selected = _select(cases, word)
    assert len(selected) == count and {c.kind for c in selected} == {kind}


def test_an_entry_needle_selects_the_compare_row_and_a_screen_needle_does_not(cases):
    assert any(c.kind == "COMPARE" for c in _select(cases, "09-fixture"))
    assert not any(c.kind == "COMPARE" for c in _select(cases, "09-fixture/CALIBRATION"))


def test_a_needle_matching_nothing_builds_no_case(cases):
    assert _select(cases, "nothing-like-this") == []
