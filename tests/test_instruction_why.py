"""The spend rule at the door (design §7.1, the founder, 2026-09-13)."""
import pytest

from instructions import why


def test_a_screen_takes_the_three_changes_and_a_new_model():
    for w in ("instruction:brief.md", "prompt:executor.py", "contract:ScreenResponseContracts.java",
              "new-model:codex:gpt-6-astra"):
        assert why.check(w, screen=True, dry_run=False)["event"] == w.split(":")[0]


def test_the_full_run_takes_a_new_model_and_a_moved_rubric():
    assert why.check("new-model:copilot:gpt-5.4-mini", screen=False, dry_run=False) == {
        "event": "new-model", "host": "copilot", "model": "gpt-5.4-mini"}
    for w in ("instruction:brief.md", "prompt:x", "contract:y"):
        with pytest.raises(why.NoReason):
            why.check(w, screen=False, dry_run=False)


# -------------------------------------------------- spec 025 FR-023: the fifth event, `marks:`

def test_marks_earns_the_full_run_and_records_the_version_it_certifies():
    """The other four events name a change to the **subject**; this one names a change to the
    **ruler**. `README.md`'s standing gate reads *green at the current `MARKS_VERSION`*, so a rubric
    that moved has no run of record until one is spent."""
    assert why.check("marks:8", screen=False, dry_run=False) == {"event": "marks", "version": 8}


def test_marks_does_not_earn_a_screen():
    """A screen is one entry, and a rubric that moved has no green run *at all* until one is spent
    -- so `marks:` is full-run only, deliberately, and not merely permitted there."""
    with pytest.raises(why.NoReason) as refusal:
        why.check("marks:8", screen=True, dry_run=False)
    assert "does not earn a screen" in str(refusal.value)


def test_marks_needs_the_version_the_run_certifies():
    for bad in ("marks:", "marks:eight", "marks:v8"):
        with pytest.raises(why.NoReason):
            why.check(bad, screen=False, dry_run=False)


def test_the_four_existing_events_are_unchanged():
    assert why.SCREEN_EVENTS == ("instruction", "prompt", "contract", "new-model")
    assert "marks" not in why.SCREEN_EVENTS
    assert why.FULL_EVENTS == ("new-model", "marks")


def test_the_policy_says_why_marks_is_its_own_event():
    """The two dishonest alternatives were both considered: `new-model:` would put a lie on the
    bundle's manifest, which exists precisely so every run on disk says why it exists, and
    `contract:` earns a screen and would have to be argued past the door it was built to be."""
    assert "WHY=marks:<version>" in why.POLICY
    assert "the RULER" in why.POLICY


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
