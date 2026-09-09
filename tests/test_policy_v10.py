"""Policy v10 (`evals/policy.py` judgement call 13): `ORI-U1` stops exempting a screen that
cannot exist.

The check asks *does this screen orient the founder about which project this is*, and it has
always skipped the screens a founder reaches before any project is in view. There were two --
`login` and `setup`. keel-cloud spec 032 retires `/v2/setup` and keel-web spec 014 retires the
screen (google-sign-in-design.md §4.7), so `setup` is a value nothing can capture. An exemption
for a screen that cannot occur is not harmless: it is a hole a future capture could be tagged
into, and the check would skip rather than fail.

Both sides are fixtured here, stacklessly, because a narrowing that only ever showed the quiet
half would be indistinguishable from having done nothing.
"""

from __future__ import annotations

from evals import policy
from harness import scoring
from harness.steps import Recorder


def _checks_for(scorecard: dict, check_id: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"]
            if c["check_id"] == check_id]


def _score(tmp_path):
    return scoring.score_bundle(tmp_path, scenario="policy-v10", complete=True)


def test_the_version_is_ten():
    assert policy.POLICY_VERSION == 10


# ------------------------------------------- the quiet half: login is still, correctly, exempt

def test_the_login_screen_is_still_exempt_from_ori_u1(tmp_path):
    """It is the one screen a founder reaches with no project and no session, and since spec 015's
    second half it is provably the same screen on a fresh instance and a busy one -- there is no
    `accountExists` branch left for it to have two shapes of."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder signs in with Google", party="founder", kind="browser") as h:
            h.capture_text("screen", "login")

    assert _checks_for(_score(tmp_path), "ORI-U1") == []


# --------------------------------------- the loud half: setup is no longer a free pass

def test_a_screen_captured_as_setup_is_no_longer_exempt(tmp_path):
    """v9 skipped this silently. v10 fails it, which is the only honest answer: `/setup` does not
    exist, so a capture claiming to be it is a harness fault, and a fault that scores as a skip is
    a fault nobody reads."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("something captured itself as the retired setup screen",
                            party="founder", kind="browser") as h:
            h.capture_text("screen", "setup")

    checks = _checks_for(_score(tmp_path), "ORI-U1")
    assert len(checks) == 1
    assert checks[0]["pass"] is False


def test_an_ordinary_screen_with_an_identity_still_passes(tmp_path):
    """The check's whole point, unchanged by the narrowing."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the overview", party="founder", kind="browser") as h:
            h.capture_text("screen", "overview")
            h.capture_text("identity", "Payroll exceptions")

    checks = _checks_for(_score(tmp_path), "ORI-U1")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


def test_the_exemption_list_is_one_screen_long():
    """Read off the source, because the tuple is the whole of the decision."""
    import inspect

    from harness import rubric

    source = inspect.getsource(rubric._ui_visit_checks)
    assert 'screen != "login"' in source
    assert '("login", "setup")' not in source
