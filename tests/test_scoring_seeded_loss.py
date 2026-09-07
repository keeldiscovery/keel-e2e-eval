"""T013 (SC-002): seeded-loss fixtures. Each test corrupts exactly one thing and asserts exactly
the check the design says should catch it fails (or, for the brief waiver, passes-but-flagged) --
proving the rubric has teeth, not just plumbing.

spec 005-connect-stack FR-010/FR-011 (policy v6): the agent-cycle/agent-handoff/agent-refusal
fixtures are retired along with the wire protocol they observed -- there is no more founder-agent
HTTP surface for ORI-H1/GUI-H1/ORI-R1/GUI-R1 to sweep, and `interpret_context` is retired as a FID
hop. The weight-2 verbatim-participant-speech rule moves to `participant_page`
(`evals/policy.py`'s `fid_weight`, module docstring judgement call 9) -- fixtured below.
"""

from __future__ import annotations

from evals import policy
from evals.facts import Fact
from harness import scoring
from harness.steps import Recorder


def _checks_for(scorecard: dict, check_id_prefix: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"]
            if c["check_id"].startswith(check_id_prefix)]


def _score(tmp_path, facts=None):
    if facts:
        scoring.write_facts(tmp_path, facts)
    return scoring.score_bundle(tmp_path, scenario="seeded-loss", complete=True)


# --------------------------------------------------------------------- truncated statement (FID)

def test_truncated_statement_fails_its_named_fid_check(tmp_path):
    """The stage screen renders only a truncated prefix of the founder's statement -- the fact
    never reaches that hop verbatim, so the FID check must fail and name the fact + hop."""
    recorder = Recorder(tmp_path)
    full_statement = "Payroll managers lose hours every month manually chasing down payroll exceptions."
    truncated = "Payroll managers lose hours every month manually chasing down payroll…"  # cut short
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("stage_screen", truncated)

    facts = {"problem_statement": Fact(text=full_statement, kind="statement", hops=["stage_screen"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-problem_statement-stage_screen")
    assert len(checks) == 1
    check = checks[0]
    assert check["pass"] is False
    assert check["waived"] is None
    assert check["evidence"]["fact_id"] == "problem_statement"
    assert check["evidence"]["hop"] == "stage_screen"


def test_fact_reaching_its_hop_verbatim_passes(tmp_path):
    """Control for the above: the same fact, rendered in full, passes."""
    recorder = Recorder(tmp_path)
    statement = "Payroll managers lose hours every month manually chasing down payroll exceptions."
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("stage_screen", f"THE PROBLEM\n{statement}")

    facts = {"problem_statement": Fact(text=statement, kind="statement", hops=["stage_screen"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-problem_statement-stage_screen")
    assert len(checks) == 1
    assert checks[0]["pass"] is True
    assert checks[0]["waived"] is None


# ------------------------------------------------------------------------- leaked enum (CLA-U1)

def test_leaked_enum_token_fails_cla_u1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            # A raw Risk enum token leaking into rendered page text.
            h.capture_text("stage_screen", "THE PROBLEM\nRisk: LOAD_BEARING")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U1")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "LOAD_BEARING" in checks[0]["detail"]


def test_clean_page_text_passes_cla_u1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("stage_screen", "THE PROBLEM\nHolding up")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U1")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


# ---------------------------------------------------------------- retired string leak (CLA-U4)

def test_retired_string_fails_cla_u4(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the history drawer", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage_screen", "Conversation history is empty.")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U4")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "Conversation history" in checks[0]["detail"]


def test_clean_text_passes_cla_u4(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage_screen", "Here's what we understood.")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U4")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


# ------------------------------------------------------------- gendered pronoun leak (CLA-U5)

def test_gendered_pronoun_fails_cla_u5_when_a_participant_is_named(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the people table", party="founder", kind="browser") as h:
            h.capture_text("screen", "people")
            h.capture_text("participant_names", "Dana Okafor")
            h.capture_text("stage_screen", "Dana Okafor answered. Her answers are in.")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "her" in checks[0]["detail"]


def test_cla_u5_is_skipped_when_no_participant_is_named(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage_screen", "Holding up.")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "CLA-U5") == []


# -------------------------------------------------------------- waiting state with no words (GUI-U3)

def test_waiting_state_with_no_words_fails_gui_u3(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the chat", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("waiting_text", "...")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "GUI-U3")
    assert len(checks) == 1
    assert checks[0]["pass"] is False


def test_waiting_state_naming_what_is_waited_for_passes_gui_u3(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the chat", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("waiting_text", "Reading what you wrote…")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "GUI-U3")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


# -------------------------------------------------------------- the waiver that retired with v8

def test_policy_8_carries_no_waivers_at_all(tmp_path):
    """Policy 7's one waiver excused `("assumption", "brief")` -- a Brief screen keel-web no longer
    has (`BriefRoute.tsx` is gone, and with it `/p/:id/brief`). v8 retires the hop and the waiver
    together and replaces neither: a review card quotes the founder's own phrase verbatim, so
    there is nothing left to excuse. A waiver that outlived its screen is a check that passes for
    a reason nobody can look at, which is worse than no check."""
    assert policy.WAIVERS == {}
    assert policy.waiver_for("assumption", "review_card") is None
    assert "brief" not in policy.HOP_IDS
    assert "brief" not in policy.HOP_INTERACTION_TYPES


# ------------------------------------------------------ corrupt answer at participant_page (w2)

def test_corrupt_answer_at_participant_page_fails_its_weight_2_check(tmp_path):
    """Policy v6: the weight-2 verbatim-speech rule now lives at `participant_page` -- the
    founder's own People-page read of a participant's answer, `harness/browser.py`'s
    `People.open_answers` capture."""
    recorder = Recorder(tmp_path)
    true_answer = "I spent three hours last month chasing down four payroll exceptions."
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens Dana's answers", party="founder", kind="browser") as h:
            h.capture_text("screen", "invitations")
            # Corrupted: not the participant's actual words.
            h.capture_text("participant_page", "Everything is fine, no issues.")

    facts = {"answer_problem": Fact(text=true_answer, kind="answer", hops=["participant_page"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-answer_problem-participant_page")
    assert len(checks) == 1
    check = checks[0]
    assert check["pass"] is False
    assert check["weight"] == 2


def test_verbatim_answer_at_participant_page_passes_its_weight_2_check(tmp_path):
    recorder = Recorder(tmp_path)
    answer = "I spent three hours last month chasing down four payroll exceptions."
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens Dana's answers", party="founder", kind="browser") as h:
            h.capture_text("screen", "invitations")
            h.capture_text("participant_page", answer)

    facts = {"answer_problem": Fact(text=answer, kind="answer", hops=["participant_page"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-answer_problem-participant_page")
    assert len(checks) == 1
    assert checks[0]["pass"] is True
    assert checks[0]["weight"] == 2


def test_hop_never_captured_fails_in_the_unresolved_bucket(tmp_path):
    """A fact declaring a hop that no interaction of the right type ever rendered (a genuinely
    missing screen, not a scenario-declared absence) fails, named, rather than being silently
    skipped."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("arrival"):
        with recorder.step("founder arrives", party="founder", kind="browser") as h:
            h.capture_text("arrival_display", "Welcome back.")

    facts = {"problem_statement": Fact(text="anything", kind="statement", hops=["brief"])}
    scorecard = _score(tmp_path, facts)

    bucket = next((e for e in scorecard["interactions"] if e["id"] == "FID-UNRESOLVED"), None)
    assert bucket is not None
    checks = [c for c in bucket["checks"] if c["check_id"] == "FID-problem_statement-brief"]
    assert len(checks) == 1
    assert checks[0]["pass"] is False
