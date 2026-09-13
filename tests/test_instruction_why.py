"""The spend rule at the door (design §7.1, the founder, 2026-09-13)."""
import pytest

from instructions import why


def test_a_screen_takes_the_three_changes_and_a_new_model():
    for w in ("instruction:brief.md", "prompt:executor.py", "contract:ScreenResponseContracts.java",
              "new-model:codex:gpt-6-astra"):
        assert why.check(w, screen=True, dry_run=False)["event"] == w.split(":")[0]


def test_the_full_run_takes_a_new_model_only():
    assert why.check("new-model:copilot:gpt-5.4-mini", screen=False, dry_run=False) == {
        "event": "new-model", "host": "copilot", "model": "gpt-5.4-mini"}
    for w in ("instruction:brief.md", "prompt:x", "contract:y"):
        with pytest.raises(why.NoReason):
            why.check(w, screen=False, dry_run=False)


def test_no_reason_no_run_and_a_dry_run_needs_none():
    with pytest.raises(why.NoReason):
        why.check(None, screen=True, dry_run=False)
    with pytest.raises(why.NoReason):
        why.check("", screen=False, dry_run=False)
    assert why.check(None, screen=False, dry_run=True) is None


def test_malformed_reasons_are_refused_with_the_policy():
    for w in ("because", "new-model:codex", "instruction:", "refactor:poller.py"):
        with pytest.raises(why.NoReason) as e:
            why.check(w, screen=True, dry_run=False)
        assert "§7.1" in str(e.value)
