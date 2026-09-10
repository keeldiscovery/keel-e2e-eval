"""The stack-boot capture of the two doors, held stackless (spec `016-copilot-e2e`).

**The harness fault this exists to stop happening twice.** `evals/conftest.py`'s
`_capture_the_login_screen` is session-scoped and depended on by the `founder_one` fixture, which
means *every scenario in this repository* runs it before it runs anything of its own. It used to
visit `/` and wait fifteen seconds for a redirect to `/login`. keel-web spec `015-landing-page`
FR-001 removed that redirect on purpose -- *"`/` splits by session, not by redirect"*; a visitor
keel-cloud does not know now renders the landing page, because a login screen is a poor first
thing for a product to say about itself -- and landed it at keel-web `d5d8645`, after this
repository's last run of record.

The result was a `TimeoutError` in a session fixture: not one scenario red, but all twelve, and
none of them for a reason in their own subject. That is what a referee pinned to the past costs
(AGENTS.md), and it is a **harness fault**, not a `runs/DRIFT.md` entry -- keel-web changed a
thing keel-web owns, said so in its own spec, and left `/login` itself untouched
(*"it stays the one-button Google page of spec 014"*).

These are source-level properties, in the manner of `tests/test_skill_distribution.py`'s pins on
the acceptance bed's command lines: what a stackless test can hold about a function that only ever
runs with a browser and a stack in front of it.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFTEST = (REPO / "evals" / "conftest.py").read_text(encoding="utf-8")


def _capture_source() -> str:
    tree = ast.parse(CONFTEST)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_capture_the_login_screen":
            return ast.get_source_segment(CONFTEST, node) or ""
    raise AssertionError("evals/conftest.py no longer defines _capture_the_login_screen")


CAPTURE = _capture_source()


def test_the_login_screen_is_opened_directly_and_never_waited_for_as_a_redirect():
    """The fix itself. `Auth._goto_login` has always gone straight to `/login` -- which is why
    signing in never noticed the change -- and this capture now does the same."""
    assert '/login", wait_until="load"' in CAPTURE, (
        "the capture no longer opens /login directly")
    assert 'wait_for_url("**/login"' not in CAPTURE, (
        "the capture is waiting for a redirect from `/` to `/login` again; keel-web spec 015 "
        "FR-001 deliberately removed it, and every scenario in this repo pays for the wait")


def test_the_strangers_own_door_is_still_visited_and_still_asserted():
    """Dropping the `/` visit would have been the cheap fix and the wrong one: *what `/` shows
    somebody with no session* is exactly the thing that moved, so it is the thing a run of record
    should be able to show a reader."""
    assert '/", wait_until="load"' in CAPTURE, "the capture no longer visits `/` at all"
    assert '"/login" not in page.url' in CAPTURE, (
        "nothing asserts that a visitor with no session is *not* redirected -- so a keel-web that "
        "quietly put the redirect back would read as green")
    assert "landing-page-before-anyone-signed-in.png" in CAPTURE, (
        "the stranger's door is no longer captured")


def test_both_screens_still_refuse_a_password():
    """§10.8, unchanged by any of this and now asserted on both doors rather than one: there is no
    password anywhere, and a landing page is a new place one could appear."""
    assert CAPTURE.count('get_by_label("Password").count() == 0') == 2, (
        "the password assertion must stand on the landing page and on the login screen")


def test_the_login_screen_still_carries_exactly_one_way_in():
    assert 'name="Continue with Google"' in CAPTURE
    assert 'get_by_role("link"' in CAPTURE, (
        "keel-web renders the control as an anchor with class `btn google`, deliberately, because "
        "signing in is a navigation and not a fetch (README, harness fault 2 of spec 015)")


def test_the_capture_is_still_what_every_scenario_runs_before_anything_else():
    """The blast radius, held: this runs inside the session-scoped `founder_one` fixture, so a
    failure in it is twelve red scenarios and not one. A future edit that makes it slower or more
    fragile should have to see that sentence."""
    assert "_capture_the_login_screen(stack, browser)" in CONFTEST
    tree = ast.parse(CONFTEST)
    founder_one = next(node for node in ast.walk(tree)
                       if isinstance(node, ast.FunctionDef) and node.name == "founder_one")
    args = [a.arg for a in founder_one.args.args]
    assert args == ["stack", "browser"], (
        f"founder_one's dependencies moved to {args}; the L1 capture rides on `browser` being one "
        f"of them")
