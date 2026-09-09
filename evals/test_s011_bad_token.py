"""S-011 -- a token that isn't right (spec `015-stub-oidc-and-two-founders`, second half;
keel-cloud `canon/designs/google-sign-in-design.md` §10.7, §5.5, decision 13).

**Deterministic, in `make eval`, no model, no runtime, one browser.** §5.5 is a table of ten
failure modes and five founder-voiced lines, and a table nobody executes is a wish. This executes
it.

The shape of every case is the same: something about the sign-in is wrong, and keel-cloud lands
the browser back on `/login` with the right sentence under the button, **opens no session** and
**creates no account**. Nothing in this file asserts what keel-cloud logged; the log is for a
server operator and is deliberately not the founder's business (§5.5).

**Where the lie comes from.** The stub issuer's `?stub_break=<what>` (§10.1) makes the next ID
token wrong in exactly one declared way -- `iss`, `aud`, `exp`, `sig`, `nonce`, `email_verified` --
so what is measured is *keel-cloud refusing*, never the stub's ability to lie (that is a `make
unit` assertion, in `tests/test_stub_oidc.py`, against the token the stub actually produces). The
break rides through the picker's own hidden fields, so the click that follows is the same click
every other scenario makes.

Three cases come from somewhere else, because they are not token defects at all:

- **cancelled** -- the picker's own *Cancel*, which is the stub's `error=access_denied`. §5.5
  renders this as a plain line and **not an error banner**: a founder changing their mind is not a
  fault and must not be dressed as one.
- **replay** (G2) -- the exact callback URL, opened a second time. A replay and a stale back
  button are the same thing to the founder, so they get the same sentence as an expiry.
- **tamper** (G1) -- a `state` minted in a different browser context. This is the CSRF binding: the
  row exists and has never been consumed, and it is still refused, because the state is not on
  *this* browser's session.

**The allowed-domain case is conditional, and says so.** `stack/oidc.py:cloud_env` deliberately
sets no `KEEL_GOOGLE_ALLOWED_DOMAIN` -- the open posture is what the scenarios exercise (§10.3) --
and neither stub identity declares an `hd`. So G8's *domain* line is driven only when a run has an
allowed domain configured, and is recorded as skipped, with its reason, when it does not. It is
never silently absent.

Moments cited: §1.0 (arrival).
"""

from __future__ import annotations

import os
import re
import time

from harness.browser import Auth, Landing
from harness.evidence import finalize_run
from harness.steps import Recorder

#: §5.5's five lines, verbatim from keel-web's `lib/translate.ts` `AUTH_ERROR_TEXT`. They are
#: written out here rather than imported from anywhere, because keel-web is the thing under
#: referee: a line that quietly changed on both sides at once is a line nobody is checking.
LINES = {
    "expired": "That sign-in took too long, or it started in a different browser. "
               "Try again from here.",
    "failed": "Google couldn't finish signing you in. Try again in a moment.",
    "unverified": "That Google account's email address hasn't been verified. "
                  "Verify it with Google, then come back.",
    "domain": "Keel is set up for one organisation's Google accounts, and that one isn't it.",
    "cancelled": "No problem — nothing happened.",
}

#: Each `stub_break`, and the rule it trips and the line it must produce (§5.5). `nonce` is G1 and
#: therefore *expired*, not *failed*: to the founder a mismatched nonce and a stale tab are the
#: same event, and §5.5's whole point is five lines a person can act on rather than ten they
#: cannot.
BREAKS = (
    ("iss", "G4", "failed"),
    ("aud", "G4", "failed"),
    ("exp", "G5", "failed"),
    ("sig", "G3", "failed"),
    ("nonce", "G1", "expired"),
    ("email_verified", "G7", "unverified"),
)

#: What must never be on the login screen (§11's never-logged list, and the founder's own screen is
#: stricter than the log). A JWT is three base64url runs separated by dots; the rest are the words
#: a wire error would arrive wearing.
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}")
FORBIDDEN = ("id_token", "access_token", "code_verifier", "client_secret", "invalid_grant",
             "Bearer ", "stub-access-token", "auth_error=", "G1", "G3", "G4", "G5", "G7", "G8",
             "302", "401", "500")


def _screen_is_clean(page) -> dict:
    """No wire token, no rule id, no status code, no JSON -- **a sentence** (P1, P7). Read off the
    whole rendered page, not just the line, because a refusal that leaked into a toast or a
    console-fed banner would still be on the founder's screen."""
    text = page.locator("body").inner_text()
    leaks = [needle for needle in FORBIDDEN if needle in text]
    jwt = _JWT.search(text)
    return {"leaks": leaks, "jwt": bool(jwt), "text": text[:600]}


def test_s011_bad_token(stack, founder_one, founder_two, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    other = None
    cases: list[dict] = []

    def _me_status() -> int:
        return context.request.get(f"{cloud_base}/v2/me", timeout=10_000).status

    def _assert_refused(page, auth, *, code: str, label: str, quiet: bool = False) -> None:
        """One refusal, asserted the one way every refusal is asserted (§10.7)."""
        with recorder.step(f"§1.0: {label} -- the login screen says the {code} line, in a "
                            "sentence, and no session was opened",
                            party="founder", kind="assert") as h:
            read = auth.login_screen()
            line = auth.auth_error_text()
            clean = _screen_is_clean(page)
            me = _me_status()
            h.record_assert({"on": "/login", "line": LINES[code], "banner": not quiet,
                              "/v2/me": 401, "leaks": []},
                             {"url": page.url, "line": line,
                              "banner": bool(read["error_banner"].strip()),
                              "/v2/me": me, **clean})
            cases.append({"case": label, "auth_error": code, "line": line, "me": me})
            assert "/login" in page.url, f"{label}: the browser is not on /login ({page.url})"
            assert line == LINES[code], (
                f"{label}: expected §5.5's {code} line, got {line!r}")
            assert me == 401, (
                f"{label}: a session was opened by a sign-in that was refused (/v2/me was {me})")
            assert not clean["leaks"] and not clean["jwt"], (
                f"{label}: the login screen carried wire detail a founder cannot act on: "
                f"{clean['leaks']} jwt={clean['jwt']}")
            if quiet:
                assert not read["error_banner"].strip(), (
                    f"{label}: rendered in an error banner. A founder changing their mind is not "
                    "a fault and §5.5 says it must not be dressed as one")
            else:
                assert read["error_banner"].strip(), (
                    f"{label}: a refusal rendered as a plain hint rather than a banner")

    try:
        page = context.new_page()
        auth = Auth(page, recorder, web_base)

        with recorder.step("§1.0: nobody is signed in, and the login screen is the same screen "
                            "a busy instance shows (L1)", party="founder", kind="assert") as h:
            read = auth.open_login()
            h.record_assert({"title": "Log in", "one way in": True, "/v2/me": 401},
                             {**read, "/v2/me": _me_status()})
            assert read["title"].strip() == "Log in", read
            assert read["google_button"], "the login screen has no Continue with Google"
            assert _me_status() == 401, "something had already opened a session"

        # -------------------------------------------------- the six declared ways a token is wrong
        for break_name, rule, code in BREAKS:
            auth.sign_in(founder_one, stub_break=break_name, expect="login")
            _assert_refused(page, auth, code=code, label=f"{rule} / stub_break={break_name}")

        # ------------------------------------------------------------------ the person cancelled
        auth.sign_in(founder_one, cancel=True, expect="login")
        _assert_refused(page, auth, code="cancelled", label="cancelled at the picker", quiet=True)

        # ----------------------------------------------------- G2, the replay and the back button
        callbacks: list[str] = []
        page.on("framenavigated", lambda frame: (
            callbacks.append(frame.url) if "/v2/auth/google/callback" in frame.url else None))
        page.on("request", lambda request: (
            callbacks.append(request.url) if "/v2/auth/google/callback" in request.url else None))
        auth.sign_in(founder_one)          # a real, successful sign-in -- the thing to replay
        with recorder.step("§1.0: the successful sign-in opened a session and landed home",
                            party="founder", kind="assert") as h:
            me = context.request.get(f"{cloud_base}/v2/me", timeout=10_000)
            body = me.json() if me.status == 200 else {}
            h.record_assert({"/v2/me": 200, "name": founder_one.name},
                             {"/v2/me": me.status, "name": body.get("name")})
            assert me.status == 200 and body.get("name") == founder_one.name, (
                f"the six refusals above left the real login broken: {me.status} {body}")
        assert callbacks, "no callback navigation was observed; the replay case cannot be driven"
        callback_url = callbacks[0]

        Landing(page, recorder, web_base).log_out()
        page.goto(callback_url, wait_until="load")
        _assert_refused(page, auth, code="expired", label="G2 / the callback URL, replayed")

        # ------------------------------------------- G1, a state minted in a different browser
        other = browser.new_context()
        other_page = other.new_page()
        other_page.goto(f"{web_base}/login", wait_until="load")
        other_page.get_by_role("link", name=Auth.GOOGLE_BUTTON).click()
        other_page.get_by_role("heading", name="Choose an account").wait_for(
            state="visible", timeout=20_000)
        # That other browser's own authorize request -- its `state` is on *its* servlet session.
        stolen = other_page.url
        page.goto(f"{stolen}&identity={founder_two.id}", wait_until="load")
        _assert_refused(page, auth, code="expired",
                        label="G1 / a state minted in a different browser")

        # ---------------------------------------------------- G8, only when a run configures it
        allowed_domain = os.environ.get("KEEL_GOOGLE_ALLOWED_DOMAIN")
        with recorder.step("§1.0: the allowed-domain refusal (G8)", party="founder",
                            kind="assert") as h:
            if not allowed_domain:
                h.record_wire(None, {
                    "skipped": True,
                    "why": "this run has no KEEL_GOOGLE_ALLOWED_DOMAIN. stack/oidc.py:cloud_env "
                           "deliberately sets none -- the open posture is what the scenarios "
                           "exercise (§10.3) -- and neither stub identity declares an `hd`, so "
                           "there is no wrong domain to be wrong about. Set the variable for the "
                           "run and this case drives itself.",
                    "line_it_would_show": LINES["domain"]})
            else:
                h.record_wire(None, {"allowed_domain": allowed_domain})
        if allowed_domain:
            auth.sign_in(founder_one, expect="login")
            _assert_refused(page, auth, code="domain",
                            label=f"G8 / no hd against {allowed_domain}")

        # ------------------------------------------- no account was created by any of the above
        with recorder.step("§1.0: none of it created an account -- the real sign-in still names "
                            "the same founder", party="founder", kind="assert") as h:
            auth.sign_in(founder_one)
            me = context.request.get(f"{cloud_base}/v2/me", timeout=10_000).json()
            h.record_assert({"name": founder_one.name, "email": founder_one.email},
                             {"name": me.get("name"), "email": me.get("email"),
                              "cases": len(cases)})
            assert me.get("name") == founder_one.name and me.get("email") == founder_one.email, (
                f"a refused sign-in left an account behind, or moved this one: {me}")

        passed = True
    finally:
        for ctx in (other, context):
            if ctx is not None:
                ctx.close()
        finalize_run(run_dir, slug="s011-bad-token", facts={}, passed=passed,
                     failed_step=None if passed else "see transcript.jsonl",
                     duration_s=time.monotonic() - started)

    assert passed
