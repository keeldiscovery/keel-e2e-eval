"""T013 (SC-002): seeded-loss fixtures. Each test corrupts exactly one thing and asserts exactly
the check the design says should catch it fails (or, for the brief waiver, passes-but-flagged) --
proving the rubric has teeth, not just plumbing.
"""

from __future__ import annotations

from evals.scenario import Fact
from harness import scoring
from harness.evidence import _read_transcript
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
    with recorder.interaction("ui-visit"):
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
    with recorder.interaction("ui-visit"):
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
    with recorder.interaction("ui-visit"):
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
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("stage_screen", "THE PROBLEM\nHolding up")

    scorecard = _score(tmp_path)
    checks = _checks_for(scorecard, "CLA-U1")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


# ------------------------------------------------------------------ empty display (ORI-H1/GUI-H1)

def test_empty_handoff_display_fails_ori_h1_and_gui_h1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-handoff"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW", "display": "", "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    ori = _checks_for(scorecard, "ORI-H1")
    gui = _checks_for(scorecard, "GUI-H1")
    assert len(ori) == 1 and ori[0]["pass"] is False
    assert len(gui) == 1 and gui[0]["pass"] is False


# -------------------------------------------------------- agent-refusal (S-007, ORI-R1/GUI-R1)

def test_actionable_refusal_passes_ori_r1_and_gui_r1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-refusal"):
        with recorder.step("get_next after a concurrent commit", party="agent", kind="protocol") as h:
            h.capture_text("rule", "concurrency")
            h.capture_text("problem", "the project moved on before this token could be used")
            h.capture_text("remedy", "call get_next again for a fresh token, then resubmit the same payload")

    scorecard = _score(tmp_path)
    ori = _checks_for(scorecard, "ORI-R1")
    gui = _checks_for(scorecard, "GUI-R1")
    assert len(ori) == 1 and ori[0]["pass"] is True
    assert len(gui) == 1 and gui[0]["pass"] is True


def test_remedy_that_only_restates_the_problem_fails_gui_r1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-refusal"):
        with recorder.step("get_next after a concurrent commit", party="agent", kind="protocol") as h:
            h.capture_text("rule", "concurrency")
            h.capture_text("problem", "the token is stale")
            h.capture_text("remedy", "the token is stale")

    scorecard = _score(tmp_path)
    gui = _checks_for(scorecard, "GUI-R1")
    assert len(gui) == 1 and gui[0]["pass"] is False


def test_missing_rule_name_fails_ori_r1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-refusal"):
        with recorder.step("some refusal", party="agent", kind="protocol") as h:
            h.capture_text("remedy", "try again with a fresh token")

    scorecard = _score(tmp_path)
    ori = _checks_for(scorecard, "ORI-R1")
    assert len(ori) == 1 and ori[0]["pass"] is False


# ---------------------------------------------------------- brief summarizing: waived, not failed

def test_brief_summarizing_an_assumption_passes_waived_with_reference(tmp_path):
    """The brief renders a founder-authored summary sentence, not the raw assumption statement --
    policy's `brief-findings-summarize` waiver means this counts as pass, flagged, citing
    keel-cloud's api-design.md §6a (design §5's first shipped waiver)."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the brief", party="founder", kind="browser") as h:
            h.capture_text("screen", "brief")
            h.capture_text("brief", "Payroll managers do spend hours a month chasing exceptions "
                                     "(1 of 1 respondents).")  # summarized, not verbatim

    facts = {
        "assumption_problem": Fact(
            text="Payroll managers spend multiple hours every month manually chasing down payroll exceptions.",
            kind="assumption", hops=["brief"],
        ),
    }
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-assumption_problem-brief")
    assert len(checks) == 1
    check = checks[0]
    assert check["pass"] is True
    assert check["waived"] is not None
    assert check["waived"]["reference"] == "keel-cloud specs/projectv2/api-design.md §6a"


# -------------------------------------------------------- corrupt answer at interpret_context (w2)

def test_corrupt_answer_at_interpret_context_fails_its_weight_2_check(tmp_path):
    recorder = Recorder(tmp_path)
    true_answer = "I spent three hours last month chasing down four payroll exceptions."
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_context(response)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {"answers": [
                {"assumptionId": "a1", "assumptionStatement": "stmt",
                 # Corrupted: not the participant's actual words.
                 "text": "Everything is fine, no issues."},
            ]}})
            h.capture_text("interpret_context", "stmt\nEverything is fine, no issues.")

    facts = {"answer_problem": Fact(text=true_answer, kind="answer", hops=["interpret_context"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-answer_problem-interpret_context")
    assert len(checks) == 1
    check = checks[0]
    assert check["pass"] is False
    assert check["weight"] == 2


def test_verbatim_answer_at_interpret_context_passes_its_weight_2_check(tmp_path):
    recorder = Recorder(tmp_path)
    answer = "I spent three hours last month chasing down four payroll exceptions."
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_context(response)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {"answers": [
                {"assumptionId": "a1", "assumptionStatement": "stmt", "text": answer},
            ]}})
            h.capture_text("interpret_context", f"stmt\n{answer}")

    facts = {"answer_problem": Fact(text=answer, kind="answer", hops=["interpret_context"])}
    scorecard = _score(tmp_path, facts)

    checks = _checks_for(scorecard, "FID-answer_problem-interpret_context")
    assert len(checks) == 1
    assert checks[0]["pass"] is True
    assert checks[0]["weight"] == 2


def test_hop_never_captured_fails_in_the_unresolved_bucket(tmp_path):
    """A fact declaring a hop that no interaction of the right type ever rendered (a genuinely
    missing screen, not a scenario-declared absence) fails, named, rather than being silently
    skipped."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {"kind": "action", "action": "CREATE",
                                                          "token": "t", "requirements": [],
                                                          "instruction": {"purpose": "p", "content": "c"},
                                                          "context": [], "detail": {}}})

    facts = {"problem_statement": Fact(text="anything", kind="statement", hops=["brief"])}
    scorecard = _score(tmp_path, facts)

    bucket = next((e for e in scorecard["interactions"] if e["id"] == "FID-UNRESOLVED"), None)
    assert bucket is not None
    checks = [c for c in bucket["checks"] if c["check_id"] == "FID-problem_statement-brief"]
    assert len(checks) == 1
    assert checks[0]["pass"] is False
