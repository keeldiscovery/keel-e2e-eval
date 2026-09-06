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
