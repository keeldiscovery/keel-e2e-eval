"""Policy v8 (spec 010 FR-025..FR-030, contracts/policy-v8-contract.md, T014).

The version bump itself, the eight hops, the retired `brief` and its waiver, the measured-beliefs
clarity vocabulary, the three retired evidence phrases, and the two new checks. The **seeded
losses** for ORI-U4, GUI-U4 and an `absent_hops` violation live at the bottom, in the same
construction-not-assertion shape `tests/test_scoring_seeded_loss.py` uses: build a transcript that
gets exactly one thing wrong, score it, and assert exactly the check that should catch it fails.
"""

from __future__ import annotations

from evals import policy
from evals.facts import Fact
from harness import scoring
from harness.steps import Recorder


def _checks_for(scorecard: dict, check_id: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"]
            if c["check_id"] == check_id]


def _score(run_dir, facts=None):
    return scoring.score_bundle(run_dir, scenario="policy-v8-fixture", complete=True,
                                 facts=facts or {})


# ------------------------------------------------------------------------------------ the bump

def test_v8_vocabulary_survives_every_later_bump():
    """The exact constant is the newest version's file to assert (`tests/test_policy_v9.py`, and
    `tests/test_policy_v6.py` before it) -- this file proves what **v8** claimed and that no later
    bump quietly took it away."""
    assert policy.POLICY_VERSION >= 8


def test_hop_ids_are_the_eight_measured_beliefs_screens():
    assert policy.HOP_IDS == ["stage_screen", "review_card", "invite_screen", "participant_page",
                               "overview", "opened_card", "answers_modal", "download"]


def test_brief_retires_with_the_route_it_named():
    """keel-web has no `/p/:id/brief` and no `BriefRoute.tsx`. A hop no screen can carry is a
    check with nothing to check."""
    assert "brief" not in policy.HOP_IDS
    assert "brief" not in policy.HOP_INTERACTION_TYPES
    assert policy.WAIVERS == {}


def test_participant_page_is_still_reachable_from_either_party():
    """The stranger's own render and the founder's read-back are both legitimate places to judge
    an answer's fidelity -- exactly as in policy 7."""
    assert policy.HOP_INTERACTION_TYPES["participant_page"] == ("participant_visit", "ui_visit")
    for hop in ("review_card", "overview", "opened_card", "answers_modal", "download"):
        assert policy.HOP_INTERACTION_TYPES[hop] == ("ui_visit",)


def test_nothing_is_reweighted():
    assert policy.CATEGORY_WEIGHTS == {"FIDELITY": 0.4, "GUIDANCE": 0.25,
                                        "ORIENTATION": 0.2, "CLARITY": 0.15}
    assert sum(policy.CATEGORY_WEIGHTS.values()) == 1.0
    assert policy.DEFAULT_WEIGHT == 1
    assert policy.FID_ANSWER_PARTICIPANT_PAGE_WEIGHT == 2
    assert policy.COMPLETION_GATE_SCORE == 2.0


# ------------------------------------------------------------------------------- the vocabulary

def test_every_measured_beliefs_family_is_swept():
    for token in ("INSIDE", "BELOW", "ABOVE", "OUTSIDE",
                   "ANCHORED", "GUESSED",
                   "HASNT_HAPPENED", "CANT_RECALL", "RATHER_NOT_SAY",
                   "COUNT", "DURATION", "MONEY", "SHARE", "TIME_SINCE", "PHYSICAL", "RATE",
                   "INTERVAL", "CHOICE", "DIRECT", "PROXY", "OPTIONS", "BUCKETS",
                   "PRACTITIONER", "BUYER", "CONSUMER", "GATEKEEPER"):
        assert token in policy.CLARITY_TOKENS, token


def test_manager_and_answers_are_exempted_by_name_with_their_excerpts():
    """The first red run decides, and it did (`runs/20260907T143953Z-s001-smoke`): the review
    card's own role-group heading reads "A PAYROLL MANAGER CAN ANSWER ALL FIVE" and the download's
    own column reads "THE ANSWERS", both upper-cased by CSS. Approved house copy, not leaks --
    exempted **by name**, never by softening the sweep."""
    assert "MANAGER" in policy._ENGLISH_COLLISION_EXEMPTIONS
    assert "ANSWERS" in policy._ENGLISH_COLLISION_EXEMPTIONS
    assert policy.enum_violations("A PAYROLL MANAGER CAN ANSWER ALL FIVE") == []
    assert policy.enum_violations("WHAT IT MEASURES · YOU SAID · THE ANSWERS") == []
    # and the neighbours in the same families are still swept
    assert policy.enum_violations("roleType PRACTITIONER") == ["PRACTITIONER"]
    assert policy.enum_violations("need: INVITE") == ["INVITE"]


def test_rate_and_share_are_not_pre_emptively_exempted():
    """Spec T011: the two predicted English-word collisions are **not** excused in advance. The
    first red run decides, and an exemption is added by name with its excerpt quoted -- never by
    softening the sweep."""
    assert "RATE" not in policy._ENGLISH_COLLISION_EXEMPTIONS
    assert "SHARE" not in policy._ENGLISH_COLLISION_EXEMPTIONS
    assert policy.enum_violations("kind: DURATION, placement INSIDE") == ["DURATION", "INSIDE"]


def test_the_evidence_drilldowns_vocabulary_is_retired():
    for phrase in ("counted for", "counted against", "said, but didn't count"):
        assert phrase in policy.RETIRED_STRINGS
    assert policy.retired_string_violations(
        "Three counted for, one counted against.") == ["counted against", "counted for"]


def test_the_four_direction_clauses_are_the_only_ones():
    assert policy.DRIFT_CLAUSES == {
        "smaller than you think", "bigger than you think",
        "less often than you think", "more often than you think"}
    assert policy.carries_direction("Not holding up · smaller than you think") is True
    assert policy.carries_direction("Not holding up") is False
    assert policy.carries_direction(None) is False


def test_the_two_new_checks_are_registered_with_their_attributes():
    assert policy.CHECKS["ORI-U4"]["attribute"] == "ORIENTATION"
    assert policy.CHECKS["GUI-U4"]["attribute"] == "GUIDANCE"


# ------------------------------------------------------------------- ORI-U4, seeded both ways

def _review_card(recorder, *, asked_first: str | None):
    with recorder.interaction("ui_visit"):
        with recorder.step("founder reads the review card", party="founder", kind="browser") as h:
            h.capture_text("screen", "review_card")
            h.capture_text("identity", "Payroll Exceptions")
            h.capture_text("review_card", "Five things must be true for this.")
            if asked_first is not None:
                h.capture_text("asked_first", asked_first)


def test_ori_u4_passes_when_the_card_names_the_story_and_then_the_picks(tmp_path):
    recorder = Recorder(tmp_path)
    _review_card(recorder, asked_first=(
        "The one story\n“Think of the last payroll run where something didn't reconcile.”\n"
        "Then\nthe three picks above, in this order, each with a way to say “can't recall”."))
    checks = _checks_for(_score(tmp_path), "ORI-U4")
    assert len(checks) == 1 and checks[0]["pass"] is True


def test_seeded_missing_asked_first_block_fails_ori_u4(tmp_path):
    """The block never renders. A founder is asked to approve a questionnaire without being shown
    what it opens with -- which is the whole thing ORI-U4 exists to notice."""
    recorder = Recorder(tmp_path)
    _review_card(recorder, asked_first=None)
    checks = _checks_for(_score(tmp_path), "ORI-U4")
    assert len(checks) == 1 and checks[0]["pass"] is False
    assert "asked first" in checks[0]["detail"]


def test_ori_u4_is_skipped_on_a_screen_that_is_not_a_review_card(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll Exceptions")
            h.capture_text("overview", "12 of 18 lines have answers")
    assert _checks_for(_score(tmp_path), "ORI-U4") == []


# ------------------------------------------------------------------- GUI-U4, seeded both ways

def _opened_card(recorder, beliefs_json: str):
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens a card", party="founder", kind="browser") as h:
            h.capture_text("screen", "opened_card")
            h.capture_text("identity", "Payroll Exceptions")
            h.capture_text("opened_card", "What it measures")
            h.capture_text("belief_statuses", beliefs_json)


def test_gui_u4_passes_when_an_interval_drifts_and_a_choice_does_not(tmp_path):
    recorder = Recorder(tmp_path)
    _opened_card(recorder, """[
      {"heading": "It costs hours", "expectation": "INTERVAL", "drift": "BELOW",
       "status": "Not holding up \\u00b7 smaller than you think"},
      {"heading": "They handle it", "expectation": "CHOICE", "drift": "NONE",
       "status": "Holding up"}]""")
    checks = _checks_for(_score(tmp_path), "GUI-U4")
    assert len(checks) == 1 and checks[0]["pass"] is True


def test_seeded_direction_invented_for_a_choice_fails_gui_u4(tmp_path):
    """Design §6.1: a Choice has no direction to show. A keel-web that invents one is exactly as
    wrong as one that omits a real one -- the check is deliberately two-sided."""
    recorder = Recorder(tmp_path)
    _opened_card(recorder, """[
      {"heading": "They handle it", "expectation": "CHOICE", "drift": "NONE",
       "status": "Not holding up \\u00b7 bigger than you think"}]""")
    checks = _checks_for(_score(tmp_path), "GUI-U4")
    assert len(checks) == 1 and checks[0]["pass"] is False
    assert "a CHOICE carries a direction" in checks[0]["detail"]


def test_seeded_direction_omitted_for_a_drifted_interval_fails_gui_u4(tmp_path):
    recorder = Recorder(tmp_path)
    _opened_card(recorder, """[
      {"heading": "It costs hours", "expectation": "INTERVAL", "drift": "ABOVE",
       "status": "Not holding up"}]""")
    checks = _checks_for(_score(tmp_path), "GUI-U4")
    assert len(checks) == 1 and checks[0]["pass"] is False
    assert "drifted ABOVE" in checks[0]["detail"]


def test_gui_u4_is_skipped_where_no_belief_carries_a_status_word(tmp_path):
    recorder = Recorder(tmp_path)
    _opened_card(recorder, """[{"heading": "It costs hours", "expectation": "INTERVAL",
                                 "drift": "NONE", "status": ""}]""")
    assert _checks_for(_score(tmp_path), "GUI-U4") == []


# ------------------------------------------------------------- absent_hops, seeded both ways

BAND = "you said 1 to 2"


def _participant_visit(recorder, page_text: str):
    with recorder.interaction("participant_visit"):
        with recorder.step("the stranger opens their link", party="participant", kind="browser") as h:
            h.capture_text("participant_page", page_text)


def test_a_band_absent_from_the_participant_page_passes(tmp_path):
    recorder = Recorder(tmp_path)
    _participant_visit(recorder, "How long did sorting that one out take? under 15 min · 1 h to 2 h")
    facts = {"band.P1": Fact(text=BAND, kind="assumption", hops=[],
                              absent_hops=["participant_page"])}
    checks = _checks_for(_score(tmp_path, facts), "FID-band.P1-participant_page-absent")
    assert len(checks) == 1 and checks[0]["pass"] is True


def test_seeded_band_leaking_onto_the_participant_page_fails_fidelity(tmp_path):
    """Design rule Q5, and the mockup's own line: *the band and the expected pick are yours; the
    people you ask never see them.* This is the first time `Fact.absent_hops` is scored at all."""
    recorder = Recorder(tmp_path)
    _participant_visit(recorder, f"How long did it take? (the founder said: {BAND} hours)")
    facts = {"band.P1": Fact(text=BAND, kind="assumption", hops=[],
                              absent_hops=["participant_page"])}
    checks = _checks_for(_score(tmp_path, facts), "FID-band.P1-participant_page-absent")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert checks[0]["attribute"] == "FIDELITY"
    assert "declared absent" in checks[0]["detail"]


def test_an_absence_cannot_be_proved_from_a_screen_nobody_looked_at(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("overview", "12 of 18 lines have answers")
    facts = {"band.P1": Fact(text=BAND, kind="assumption", hops=[],
                              absent_hops=["participant_page"])}
    checks = _checks_for(_score(tmp_path, facts), "FID-band.P1-participant_page-absent")
    assert len(checks) == 1 and checks[0]["pass"] is False
    assert "never captured" in checks[0]["detail"]


def test_absence_matching_is_the_same_matching_as_presence(tmp_path):
    """`policy.fact_reaches_hop` unchanged, both directions -- so normalization can never make an
    absence check stricter than its positive twin. Curly quotes and trailing punctuation are
    folded the same way here as there."""
    recorder = Recorder(tmp_path)
    _participant_visit(recorder, "the founder said “YOU SAID 1 TO 2”.")
    facts = {"band.P1": Fact(text=BAND, kind="assumption", hops=[],
                              absent_hops=["participant_page"])}
    checks = _checks_for(_score(tmp_path, facts), "FID-band.P1-participant_page-absent")
    assert checks[0]["pass"] is False


# ------------------------------------------------- the one absence that cannot honestly be claimed

def test_a_founder_phrase_that_is_its_own_option_word_is_not_declared_absent():
    """`01-countly`'s `C17`: the founder said *per site*, and `S17` asks "How is that tool priced?"
    with `per site` among the four answers. Rule `Q5` forbids a **line** that names the founder's
    number or answer; it cannot forbid the option list from containing the word the belief is
    about. Live-confirmed (`runs/20260907T145804Z-s005-countly`)."""
    from evals import corpus_facts
    from harness import corpus_script
    from stack.config import load_config

    _, entry = corpus_script.entry_for(load_config(validate=False).keel_cloud, "01-countly")
    facts = corpus_facts.facts_for(entry)
    assert facts["phrase.C17"].text == "per site"
    assert facts["phrase.C17"].absent_hops == []
    # and every other phrase still is
    assert facts["phrase.P1"].absent_hops == ["participant_page"]
