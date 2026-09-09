"""What S-010 and S-011 promise, checked where no stack is needed (spec
`015-stub-oidc-and-two-founders`, second half; keel-cloud
`canon/designs/google-sign-in-design.md` §10.6, §10.7).

Neither scenario can be *run* here -- both need a browser and a live keel-cloud. What can be
checked stacklessly is everything a run finds out too late and too expensively: that S-010 goes at
every route §4.3 lists rather than a convenient subset, that S-011 drives every one of §10.7's
cases and asserts §5.5's exact five lines, and that neither has quietly grown a bypass. This is
the same posture `tests/test_page_object_calls_exist.py` takes to page objects.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
S010 = REPO / "evals" / "test_s010_two_founders.py"
S011 = REPO / "evals" / "test_s011_bad_token.py"

#: §4.3's complete list of founder-reachable routes that were not owner-scoped. S-010 goes at
#: every one of them; a subset would prove the check exists somewhere rather than everywhere.
THE_TEN_READS = ("overview", "stages/", "invitations", "invitations/", "roles", "/preview",
                 "people", "readings", "readings/", "standing")
THE_WRITES = ("/approval", "invitations", "readings")


def _source(path: pathlib.Path) -> str:
    return path.read_text()


# --------------------------------------------------------------------------------------- S-010

def test_s010_goes_at_every_route_4_3_lists():
    body = _source(S010)
    missing = [name for name in THE_TEN_READS if name not in body]
    assert not missing, (
        f"S-010 does not reach every route §4.3 names -- missing {missing}. A subset proves the "
        "owner check exists somewhere, not everywhere, which is the defect §4.3 is a list of")
    for write in THE_WRITES:
        assert write in body, f"S-010 never writes at {write!r}"


def test_s010_asserts_an_empty_body_and_not_only_a_status():
    """§4.5/O3: a `Refusal` with a rule id would undo the whole point of not saying 403, so the
    body is part of the assertion, not decoration."""
    body = _source(S010)
    assert "response.status == 404 and not body.strip()" in body
    assert "byte-identical" in body or "shape" in body


def test_s010_uses_a_second_browser_context_and_not_a_second_tab():
    """A new tab shares the cookie jar; the whole scenario would then be one founder twice."""
    body = _source(S010)
    assert body.count("browser.new_context()") >= 2
    assert "fresh browser context" in body or "fresh cookie jar" in body.lower()


def test_s010_re_reads_founder_as_revision_and_reading_batches():
    """The half-execution §4.3 names: `POST /readings` snapshotted the victim's project and wrote
    a `reading_batch` row *before* the downstream gate refused. Only a re-read catches that."""
    body = _source(S010)
    assert "revision_before" in body and "revision_after" in body
    assert "batches_after" in body


def test_s010_reads_each_founder_reads_own_id_key():
    """**A harness fault this test exists because of.** The three ids S-010 needs to build §4.3's
    by-id routes each live under a different key, and the first pass guessed `id` for all of them.
    A key that comes back `None` turns a real id into `NOWHERE`, and the scenario then proves that
    a project which exists nowhere answers 404 -- which it does, and which is not the point.

    Confirmed against the live wire, keel-cloud `866a611`:
      GET .../invitations -> {"invitations": [{"invitationId": ...}]}
      GET .../roles       -> {"roles":       [{"roleId": ...}]}
      GET .../readings    -> [{"batchId": ...}]                       (a bare list)
      GET /v2/projects    -> [{"projectId": ...}]                     (not `id`)
    """
    body = _source(S010)
    assert '_first(invitations_a, "invitations", "invitationId")' in body
    assert '_first(roles_a, "roles", "roleId")' in body
    assert '_first(readings_a, None, "batchId")' in body
    assert 'row.get("projectId")' in body
    assert 'row.get("id")' not in body


def test_s010_reads_the_revision_after_its_own_write():
    """`revision_before` is what step 5 re-reads to prove founder B moved nothing. S-010 mints an
    invitation of its own when A's project has none, and inviting somebody moves the revision -- so
    a read taken a moment too early would fail the check on this scenario's own write."""
    body = _source(S010)
    invite = body.index("invitation_urls = _invite_one(")
    read = body.index('revision_before = overview_a.get("revision")')
    assert invite < read, "the revision is read before S-010's own invitation moves it"


def test_s010_never_signs_founder_b_in_as_founder_a():
    body = _source(S010)
    assert "sign_in(founder_two)" in body
    assert "sign_in(founder_one)" in body


# --------------------------------------------------------------------------------------- S-011

def _module(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(), filename=str(path))


def _constant_dict(path: pathlib.Path, name: str) -> dict:
    for node in ast.walk(_module(path)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{path.name} has no {name}")


def test_s011_carries_5_5s_five_lines_verbatim():
    """Written out in the scenario rather than imported from keel-web: keel-web is the thing under
    referee, and a line that changed on both sides at once is a line nobody is checking."""
    lines = _constant_dict(S011, "LINES")
    assert set(lines) == {"expired", "failed", "unverified", "domain", "cancelled"}
    assert lines["expired"] == ("That sign-in took too long, or it started in a different "
                                "browser. Try again from here.")
    assert lines["failed"] == "Google couldn't finish signing you in. Try again in a moment."
    assert lines["unverified"] == ("That Google account's email address hasn't been verified. "
                                   "Verify it with Google, then come back.")
    assert lines["domain"] == ("Keel is set up for one organisation's Google accounts, and that "
                               "one isn't it.")
    assert lines["cancelled"] == "No problem — nothing happened."
    for line in lines.values():
        assert line[0].isupper() and line.rstrip().endswith((".", "!")), (
            f"a founder-voiced refusal is a SENTENCE, not a rule id or a status code: {line!r}")


def test_s011_drives_every_stub_break_the_stub_can_produce():
    """The stub declares six; a scenario that drove five would leave one lie nobody refuses."""
    from stack.stub_oidc.server import STUB_BREAKS

    breaks = _constant_dict(S011, "BREAKS")
    assert {name for name, _, _ in breaks} == set(STUB_BREAKS)


def test_s011_maps_each_break_to_the_line_5_5_names():
    breaks = {name: (rule, code) for name, rule, code in _constant_dict(S011, "BREAKS")}
    assert breaks["iss"] == ("G4", "failed")
    assert breaks["aud"] == ("G4", "failed")
    assert breaks["exp"] == ("G5", "failed")
    assert breaks["sig"] == ("G3", "failed")
    # G1, and therefore *expired*: to the founder a mismatched nonce and a stale tab are the same
    # event, and §5.5's whole point is five lines a person can act on rather than ten they cannot.
    assert breaks["nonce"] == ("G1", "expired")
    assert breaks["email_verified"] == ("G7", "unverified")


@pytest.mark.parametrize("case", ["cancel=True", "replayed", "a state minted in a different "
                                  "browser", "KEEL_GOOGLE_ALLOWED_DOMAIN"])
def test_s011_drives_the_cases_that_are_not_token_defects(case):
    """Cancel, replay (G2), a foreign-session state (G1), and the allowed domain (G8). The last is
    conditional on a run configuring one, and is recorded as skipped rather than silently absent."""
    assert case in _source(S011)


def test_s011_asserts_no_session_was_opened_and_no_wire_detail_reached_the_screen():
    body = _source(S011)
    assert "assert me == 401" in body, "a refused sign-in that opened a session would pass"
    assert "_JWT" in body and "FORBIDDEN" in body


def test_s011_proves_the_real_login_still_works_afterwards():
    """A refusal suite that broke the happy path and never noticed would be worse than no suite."""
    body = _source(S011)
    assert "the six refusals above left the real login broken" in body
    assert "a refused sign-in left an account behind" in body
