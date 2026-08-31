"""003-eval-set T001: policy v2 fixtures, plus founder-experience design's policy v3 fixtures
(evals/policy.py's module docstring, judgement call 4). Proves the v2 recalibration
(evals/policy.py judgement call 3; specs/eval-scoring-design.md §3's dated amendment; runs/
DRIFT.md #4's re-adjudication) by construction:

- a raw enum/field-name leak in an agent-cycle's `instruction`/`requirements` no longer fails
  anything (those texts are agent-facing, not swept any more);
- the same leak in a handoff's `display` still fails both `CLA-A1` and the new handoff `GUI-A2` --
  the one protocol text a founder actually receives stays checked at full strength.

...and the v3 additions by the same construction-not-assertion method:

- a commit's own `display` (`captured_text["commit_display"]`, `harness/driver.py`'s
  `_capture_commit_voice`) is swept for presence (`ORI-A3`), actionability + a well-formed door
  (`GUI-A3`), and vocabulary (`CLA-A2`) -- exactly as a handoff's always was, extended to the field
  that now travels on every commit;
- `verdictLabel`/`needLabel`, read off a ui-visit's own captured `state` snapshot, are swept for
  presence-once-relevant and vocabulary (`CLA-U3`);
- the `recorded` hop is a hop like any other to the generic FID engine -- one fixture proves it
  wires through end to end (a fact declaring `hops=["recorded"]` passes when the agent-cycle's
  captured `recorded` JSON contains it verbatim, fails when it doesn't).

Policy v4 (founder-experience round 2) adds three more fixtures, same construction-not-assertion
method: the arrival read's own greeting (`CLA-AR1`), the locked People section's own why
(`ORI-U3`), and the pointer-to-agent sentence's own missing door (`GUI-U2`).

Policy v5 (relay-design.md §12 item 5, evals/policy.py judgement call 7) adds three more, scored on
a new interaction type, `"chat-visit"` (`harness/browser.py`'s `ChatPane.capture`): a vocabulary/
structural sweep over the chat pane's own rendered turn text and playback table cells (`CLA-C1`),
presence-banner honesty against the relay's own wire truth (`ORI-C1`), and well-formed links inside
a chat turn (`GUI-C1`, the every-door-opens rule's chat-surface extension). Same construction-not-
assertion method as every prior bump.
"""

from __future__ import annotations

from evals import policy
from evals.scenario import Fact
from harness import scoring
from harness.steps import Recorder


def _checks_for(scorecard: dict, check_id: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"] if c["check_id"] == check_id]


def _score(tmp_path, facts=None):
    return scoring.score_bundle(tmp_path, scenario="policy-v4-fixture", complete=True, facts=facts)


def test_policy_version_is_5():
    assert policy.POLICY_VERSION == 5


# --------------------------------------- agent-cycle: no longer vocabulary-swept (US1 scenario 1)

def test_seeded_enum_in_instruction_and_requirements_no_longer_fails_anything(tmp_path):
    """A raw `Verdict` enum and a raw field name (`askedOf`), seeded into an agent-cycle's
    `instruction.content` and `requirements` -- exactly what tripped policy v1's CLA-A1/GUI-A2
    twenty times over on S-001 -- must not fail CLA-A1 or GUI-A2 under v2, because neither check
    applies to an agent-cycle interaction any more."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "action", "action": "INTRODUCE_ASSUMPTIONS", "token": "t",
                "instruction": {
                    "purpose": "introduce assumptions",
                    "content": "a load-bearing belief is CONTRADICTED when the majority of people "
                               "who spoke described the opposite",
                },
                "requirements": ["askedOf naming a role whose type is compatible with the stage"],
                "context": [], "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert cla == [], "CLA-A1 must not be emitted for an agent-cycle interaction under policy v2"
    assert gui_a2 == [], "GUI-A2 must not be emitted for an agent-cycle interaction under policy v2"
    # GUI-A1 (presence/sentence-shape) and ORI-A1 (non-empty instruction) are untouched.
    gui_a1 = _checks_for(scorecard, "GUI-A1")
    assert len(gui_a1) == 1 and gui_a1[0]["pass"] is True
    ori_a1 = _checks_for(scorecard, "ORI-A1")
    assert len(ori_a1) == 1 and ori_a1[0]["pass"] is True


# ------------------------------------------ handoff display: still swept (US1 scenario 2)

def test_seeded_enum_in_handoff_display_still_fails_cla_a1_and_gui_a2(tmp_path):
    """The one protocol text a founder actually receives -- a handoff's `display` -- stays swept
    at full strength: a raw enum there fails both CLA-A1 (unchanged from v1) and GUI-A2 (new
    under v2)."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-handoff"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW",
                "display": "The problem card's verdict is CONTRADICTED -- read the contradictions "
                           "handle before deciding what to do.",
                "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert len(cla) == 1 and cla[0]["pass"] is False
    assert "CONTRADICTED" in cla[0]["detail"]
    assert len(gui_a2) == 1 and gui_a2[0]["pass"] is False
    assert "CONTRADICTED" in gui_a2[0]["detail"]


def test_clean_handoff_display_passes_cla_a1_and_gui_a2(tmp_path):
    """Control for the above: a founder-phrased display with no leaks passes both."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-handoff"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "handoff", "reason": "REVIEW",
                "display": "The problem card is waiting for your approval -- read the questions "
                           "before anyone is asked.",
                "detail": {"stage": "PROBLEM"},
            }})

    scorecard = _score(tmp_path)
    cla = _checks_for(scorecard, "CLA-A1")
    gui_a2 = _checks_for(scorecard, "GUI-A2")
    assert len(cla) == 1 and cla[0]["pass"] is True
    assert len(gui_a2) == 1 and gui_a2[0]["pass"] is True


# ------------------------------------------------- policy v3: the commit's own display (US4-ish)

def test_commit_display_absent_emits_no_v3_checks(tmp_path):
    """A bundle scored before `SubmitResponse.display` existed (or a step that never reached a
    successful commit) must not fail `ORI-A3`/`GUI-A3`/`CLA-A2` -- they're skipped, not failed,
    exactly as `_agent_cycle_checks`'s own docstring says."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("get_next (project p1)", party="agent", kind="protocol") as h:
            h.record_wire({}, {"status": 200, "body": {
                "kind": "action", "action": "INTRODUCE_ROLES", "token": "t",
                "instruction": {"purpose": "introduce roles", "content": "name who could answer"},
                "requirements": ["at least one role"], "context": [], "detail": {},
            }})

    scorecard = _score(tmp_path)
    for check_id in ("ORI-A3", "GUI-A3", "CLA-A2"):
        assert _checks_for(scorecard, check_id) == [], f"{check_id} must not fire with no commit_display"


def test_seeded_enum_in_commit_display_fails_cla_a2_not_gui_a3(tmp_path):
    """A commit's own `display` -- policy v3's new home for the same vocabulary sweep a handoff's
    always got -- fails `CLA-A2` on a raw enum. `GUI-A3` is about the door alone (live-confirmed
    2026-08-30: reusing GUI-H1's actionability heuristic here mismeasured legitimate agent-to-
    agent continuations across every scenario) -- with no URL present, there is nothing for it to
    fail, so it passes even though the sentence leaks."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("submit INTRODUCE_ASSUMPTIONS", party="agent", kind="protocol") as h:
            h.capture_text("commit_display", "The belief is CONTRADICTED.")
            h.record_wire({}, {"status": 200, "body": {
                "projectId": "p1", "state": "OPEN", "revision": 2,
                "display": "The belief is CONTRADICTED.", "recorded": None,
            }})

    scorecard = _score(tmp_path)
    ori_a3 = _checks_for(scorecard, "ORI-A3")
    gui_a3 = _checks_for(scorecard, "GUI-A3")
    cla_a2 = _checks_for(scorecard, "CLA-A2")
    assert len(ori_a3) == 1 and ori_a3[0]["pass"] is True  # non-empty, >= 10 chars -- presence only
    assert len(gui_a3) == 1 and gui_a3[0]["pass"] is True  # no URL named -- nothing to fail
    assert len(cla_a2) == 1 and cla_a2[0]["pass"] is False
    assert "CONTRADICTED" in cla_a2[0]["detail"]


def test_clean_commit_display_with_a_door_passes_ori_a3_gui_a3_cla_a2(tmp_path):
    """A founder-worded commit display naming a next step and carrying a well-formed URL passes
    all three -- the positive control."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("submit INTRODUCE_ASSUMPTIONS", party="agent", kind="protocol") as h:
            h.capture_text("commit_display", "Your beliefs are recorded. The problem card is "
                            "waiting for your approval -- read the questions before anyone is "
                            "asked. http://localhost:5173/p/p1/s/PROBLEM")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "ORI-A3")[0]["pass"] is True
    assert _checks_for(scorecard, "GUI-A3")[0]["pass"] is True
    assert _checks_for(scorecard, "CLA-A2")[0]["pass"] is True


def test_commit_display_with_a_malformed_door_fails_gui_a3(tmp_path):
    """A URL-shaped substring that isn't actually `http(s)://` fails `GUI-A3`'s well-formedness
    half even though the sentence is otherwise founder-worded and actionable."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("submit INTRODUCE_ASSUMPTIONS", party="agent", kind="protocol") as h:
            h.capture_text("commit_display", "Read the questions before anyone is asked. "
                            "ftp://localhost:5173/p/p1/s/PROBLEM")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "GUI-A3")[0]["pass"] is False


# ----------------------------------------------- policy v3: verdictLabel/needLabel (CLA-U3)

def _ui_visit_with_state(tmp_path, state: dict):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("state", __import__("json").dumps(state))
    return recorder


def test_approved_stage_missing_verdict_label_fails_cla_u3(tmp_path):
    state = {"stages": [{"stage": "PROBLEM", "approved": True, "need": None,
                          "verdict": "SUPPORTED", "verdictLabel": None, "needLabel": None}]}
    _ui_visit_with_state(tmp_path, state)
    scorecard = _score(tmp_path)
    cla_u3 = _checks_for(scorecard, "CLA-U3")
    assert len(cla_u3) == 1 and cla_u3[0]["pass"] is False


def test_verdict_label_leaking_an_enum_fails_cla_u3(tmp_path):
    state = {"stages": [{"stage": "PROBLEM", "approved": True, "need": None,
                          "verdict": "SUPPORTED", "verdictLabel": "SUPPORTED", "needLabel": None}]}
    _ui_visit_with_state(tmp_path, state)
    scorecard = _score(tmp_path)
    cla_u3 = _checks_for(scorecard, "CLA-U3")
    assert len(cla_u3) == 1 and cla_u3[0]["pass"] is False


def test_evidence_need_excuses_a_missing_need_label(tmp_path):
    """`FounderVoice.needLabel` deliberately returns `null` for `EVIDENCE` (`verdictLabel` already
    carries the word) -- `CLA-U3` must not fail that as a missing label."""
    state = {"stages": [{"stage": "PROBLEM", "approved": True, "need": "EVIDENCE",
                          "verdict": "SUPPORTED", "verdictLabel": "Holding up", "needLabel": None}]}
    _ui_visit_with_state(tmp_path, state)
    scorecard = _score(tmp_path)
    cla_u3 = _checks_for(scorecard, "CLA-U3")
    assert len(cla_u3) == 1 and cla_u3[0]["pass"] is True


def test_clean_labels_pass_cla_u3(tmp_path):
    state = {"stages": [{"stage": "PROBLEM", "approved": True, "need": "INVITE",
                          "verdict": "UNTESTED", "verdictLabel": "Still asking",
                          "needLabel": "Nobody asked yet"}]}
    _ui_visit_with_state(tmp_path, state)
    scorecard = _score(tmp_path)
    cla_u3 = _checks_for(scorecard, "CLA-U3")
    assert len(cla_u3) == 1 and cla_u3[0]["pass"] is True


# ------------------------------------------------------- policy v3: the `recorded` FID hop

def test_recorded_hop_wires_through_the_generic_fid_engine(tmp_path):
    """`"recorded"` is a hop like any other to `harness/rubric.py`'s generic `_fid_checks` -- no
    new check code, just a new hop id (evals/policy.py's `HOP_IDS`/`HOP_INTERACTION_TYPES`) a
    scenario's own facts may declare."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("submit CREATE", party="agent", kind="protocol") as h:
            h.capture_text("recorded", '{"name": "Payroll Exception Radar", "problem": "..."}')

    facts = {"project_name": Fact(text="Payroll Exception Radar", kind="statement", hops=["recorded"])}
    scorecard = _score(tmp_path, facts=facts)
    fid = _checks_for(scorecard, "FID-project_name-recorded")
    assert len(fid) == 1 and fid[0]["pass"] is True


def test_recorded_hop_fails_when_the_fact_is_absent(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("agent-cycle"):
        with recorder.step("submit CREATE", party="agent", kind="protocol") as h:
            h.capture_text("recorded", '{"name": "A Different Name", "problem": "..."}')

    facts = {"project_name": Fact(text="Payroll Exception Radar", kind="statement", hops=["recorded"])}
    scorecard = _score(tmp_path, facts=facts)
    fid = _checks_for(scorecard, "FID-project_name-recorded")
    assert len(fid) == 1 and fid[0]["pass"] is False


# ------------------------------------------------------------ policy v4: the arrival read (CLA-AR1)

def test_arrival_display_absent_fails_cla_ar1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("arrival"):
        with recorder.step("founder-agent arrives: GET /v2/agent/state (no project)",
                            party="agent", kind="protocol") as h:
            h.capture_text("arrival_display", "")

    scorecard = _score(tmp_path)
    cla_ar1 = _checks_for(scorecard, "CLA-AR1")
    assert len(cla_ar1) == 1 and cla_ar1[0]["pass"] is False


def test_arrival_display_naming_a_raw_project_id_fails_cla_ar1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("arrival"):
        with recorder.step("founder-agent arrives: GET /v2/agent/state (no project)",
                            party="agent", kind="protocol") as h:
            h.capture_text("arrival_display",
                            "Welcome back -- project aa6c44c7-1234-4abc-9def-0123456789ab is waiting on two answers.")

    scorecard = _score(tmp_path)
    cla_ar1 = _checks_for(scorecard, "CLA-AR1")
    assert len(cla_ar1) == 1 and cla_ar1[0]["pass"] is False


def test_clean_arrival_greeting_passes_cla_ar1(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("arrival"):
        with recorder.step("founder-agent arrives: GET /v2/agent/state (no project)",
                            party="agent", kind="protocol") as h:
            h.capture_text("arrival_display",
                            "Welcome back -- Payroll Exception Radar is waiting on two answers.")

    scorecard = _score(tmp_path)
    cla_ar1 = _checks_for(scorecard, "CLA-AR1")
    assert len(cla_ar1) == 1 and cla_ar1[0]["pass"] is True


def test_arrival_greeting_naming_a_door_passes_cla_ar1(tmp_path):
    """Live-confirmed 2026-08-30 (eval-all run, S-007): a greeting's own embedded door
    legitimately carries the project id as a URL path segment -- a door, not a leak (`GUI-A3`'s
    own "when it points at a screen, contains a resolvable URL"). The id-free half only sweeps
    the sentence's own prose, stripping any URL first, the same exemption `clarity_violations`
    already gives every enum/field-name sweep."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("arrival"):
        with recorder.step("founder-agent arrives: GET /v2/agent/state (no project)",
                            party="agent", kind="protocol") as h:
            h.capture_text("arrival_display",
                            'Welcome back -- "Payroll Exception Radar" answers are still out for '
                            "the problem card. Nothing to do until someone replies. "
                            "http://localhost:5173/p/11e8fd7b-da1f-4dbd-a6da-4fdad7822c81/invitations")

    scorecard = _score(tmp_path)
    cla_ar1 = _checks_for(scorecard, "CLA-AR1")
    assert len(cla_ar1) == 1 and cla_ar1[0]["pass"] is True


# --------------------------------------------------------------- policy v4: ORI-U1 skips login/setup

def test_ori_u1_skipped_on_the_login_screen(tmp_path):
    """Live-confirmed 2026-08-30 (eval-all run, S-008): `/login`/`/setup` are visited before any
    project is even in view (`FounderBrowser.log_in`) -- there is no project identity marker for
    them to carry, so ORI-U1 must not fire there at all, rather than failing every scenario's own
    login step on inapplicable ground."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder logs in", party="founder", kind="browser") as h:
            h.capture_text("screen", "login")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "ORI-U1") == []


def test_ori_u1_still_fires_on_an_ordinary_project_screen(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "")

    scorecard = _score(tmp_path)
    ori_u1 = _checks_for(scorecard, "ORI-U1")
    assert len(ori_u1) == 1 and ori_u1[0]["pass"] is False


# ------------------------------------------------------- policy v4: the locked People why (ORI-U3)

def test_locked_people_why_leaking_wire_vocabulary_fails_ori_u3(tmp_path):
    """`capture_text` no-ops on an empty string (the real `.side-nav__locked-why` element can
    never actually render empty -- `peopleLockedReason()` is a fixed non-empty sentence), so the
    realistic failure this check exists to catch is a leaked enum, not a blank string."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("locked_reason", "Locked -- stage REVIEW pending")

    scorecard = _score(tmp_path)
    ori_u3 = _checks_for(scorecard, "ORI-U3")
    assert len(ori_u3) == 1 and ori_u3[0]["pass"] is False


def test_locked_people_with_a_founder_worded_why_passes_ori_u3(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("locked_reason", "Locked until every card you're currently reviewing is approved.")

    scorecard = _score(tmp_path)
    ori_u3 = _checks_for(scorecard, "ORI-U3")
    assert len(ori_u3) == 1 and ori_u3[0]["pass"] is True


def test_people_not_locked_emits_no_ori_u3(tmp_path):
    """No locked section on this visit at all -- skipped, not failed."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exception Radar")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "ORI-U3") == []


# --------------------------------------------------- policy v4: the pointer-to-agent door (GUI-U2)

def test_pointer_to_agent_sentence_with_a_url_fails_gui_u2(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("pointer_to_agent",
                            "Now work out your solution with your Keel agent. http://localhost:5173/p/p1")

    scorecard = _score(tmp_path)
    gui_u2 = _checks_for(scorecard, "GUI-U2")
    assert len(gui_u2) == 1 and gui_u2[0]["pass"] is False


def test_pointer_to_agent_sentence_with_no_url_passes_gui_u2(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the project overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("pointer_to_agent", "Now work out your solution with your Keel agent.")

    scorecard = _score(tmp_path)
    gui_u2 = _checks_for(scorecard, "GUI-U2")
    assert len(gui_u2) == 1 and gui_u2[0]["pass"] is True


def test_ordinary_affordance_emits_no_gui_u2(tmp_path):
    """An ordinary affordance never renders `.next.agent` at all, so `pointer_to_agent` is never
    captured -- this check has nothing to say about it, and it is free to carry a real link (e.g.
    the invite screen)."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui-visit"):
        with recorder.step("founder opens the problem stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage", "PROBLEM")
            h.capture_text("identity", "Payroll Exception Radar")
            h.capture_text("affordance", "Waiting for your approval.")

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "GUI-U2") == []


# --------------------------------------------------------------- policy v5: the chat surface (§12.5)

def _chat_visit(tmp_path, *, turns="", playback="", banner="", presence_state=None, links=""):
    recorder = Recorder(tmp_path)
    with recorder.interaction("chat-visit"):
        with recorder.step("founder reads the chat pane", party="founder", kind="browser") as h:
            h.capture_text("chat_turns", turns)
            if playback:
                h.capture_text("chat_playback_table", playback)
            h.capture_text("chat_presence_banner", banner)
            if presence_state is not None:
                h.capture_text("chat_presence_state", __import__("json").dumps(presence_state))
            if links:
                h.capture_text("chat_turn_links", links)
    return recorder


def test_seeded_enum_in_chat_turn_text_fails_cla_c1(tmp_path):
    _chat_visit(tmp_path, turns="YOUR KEEL AGENT: The belief is CONTRADICTED.")
    scorecard = _score(tmp_path)
    cla_c1 = _checks_for(scorecard, "CLA-C1")
    assert len(cla_c1) == 1 and cla_c1[0]["pass"] is False
    assert "CONTRADICTED" in cla_c1[0]["detail"]


def test_seeded_enum_in_playback_table_cells_fails_cla_c1(tmp_path):
    _chat_visit(tmp_path, turns="YOU: who could answer?",
                playback="Role | Can settle\nPayroll Ops Manager | INVITE the roles handle")
    scorecard = _score(tmp_path)
    cla_c1 = _checks_for(scorecard, "CLA-C1")
    assert len(cla_c1) == 1 and cla_c1[0]["pass"] is False


def test_clean_chat_pane_text_passes_cla_c1(tmp_path):
    _chat_visit(tmp_path, turns="YOU: Payroll exceptions.\nYOUR KEEL AGENT: Got it, tell me more.",
                playback="Role | Can settle\nPayroll Ops Manager | the problem, the solution")
    scorecard = _score(tmp_path)
    cla_c1 = _checks_for(scorecard, "CLA-C1")
    assert len(cla_c1) == 1 and cla_c1[0]["pass"] is True


def test_absent_banner_while_the_wire_reports_disconnected_fails_ori_c1(tmp_path):
    """The pane's own silence claims "connected" (design §5/§9: absence of banner IS the positive
    signal) -- if the relay's own wire truth disagrees, that is a founder-facing lie, not a missing
    affordance."""
    _chat_visit(tmp_path, banner="", presence_state={"connected": False})
    scorecard = _score(tmp_path)
    ori_c1 = _checks_for(scorecard, "ORI-C1")
    assert len(ori_c1) == 1 and ori_c1[0]["pass"] is False


def test_shown_banner_while_the_wire_reports_connected_fails_ori_c1(tmp_path):
    _chat_visit(tmp_path, banner="Your Keel agent isn't connected.", presence_state={"connected": True})
    scorecard = _score(tmp_path)
    ori_c1 = _checks_for(scorecard, "ORI-C1")
    assert len(ori_c1) == 1 and ori_c1[0]["pass"] is False


def test_banner_and_wire_truth_agreeing_passes_ori_c1(tmp_path):
    _chat_visit(tmp_path, banner="", presence_state={"connected": True})
    scorecard = _score(tmp_path)
    ori_c1 = _checks_for(scorecard, "ORI-C1")
    assert len(ori_c1) == 1 and ori_c1[0]["pass"] is True


def test_ori_c1_skipped_when_no_presence_state_was_captured(tmp_path):
    _chat_visit(tmp_path, banner="")
    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "ORI-C1") == []


def test_malformed_chat_turn_link_fails_gui_c1(tmp_path):
    _chat_visit(tmp_path, links="ftp://localhost:5173/p/p1")
    scorecard = _score(tmp_path)
    gui_c1 = _checks_for(scorecard, "GUI-C1")
    assert len(gui_c1) == 1 and gui_c1[0]["pass"] is False


def test_well_formed_chat_turn_link_passes_gui_c1(tmp_path):
    _chat_visit(tmp_path, links="http://localhost:5173/p/p1")
    scorecard = _score(tmp_path)
    gui_c1 = _checks_for(scorecard, "GUI-C1")
    assert len(gui_c1) == 1 and gui_c1[0]["pass"] is True


def test_gui_c1_skipped_when_no_chat_turn_links_were_captured(tmp_path):
    _chat_visit(tmp_path, turns="YOU: hi")
    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "GUI-C1") == []
