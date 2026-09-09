"""S-010 -- two founders, one instance (spec `015-stub-oidc-and-two-founders`, second half;
keel-cloud `canon/designs/google-sign-in-design.md` §10.6, decision 12).

**Deterministic, in `make eval`, no model at all.** The brief called this *"S-004's second
founder"*. S-004 is *the stranger who gives orders* -- live, model-backed, and deselected from
`make eval`/`make eval-all` -- so isolation assertions living there would be proven only when
somebody opts into a paid run, which is the opposite of what an isolation test is for. So it lives
here, and the runtime it connects runs keel-runtime's own **scripted** executor.

**Both founders exist because both signed in.** There is no fixture that inserts a row, no setup
call, and no second password. Founder A is *Eval Founder* and founder B is *Nour Haddad*; each
clicks their own name on the stub issuer's account picker, and keel-cloud creates the account off
the `sub` in the ID token it verified. The first founder gets no special treatment (decision 3),
and this scenario is the only place that is observable.

**What is measured**, in the design's own order:

  1  founder A signs in; the landing greets *Eval Founder* and `/v2/me` carries A's own address.
  2  A connects a runtime (scripted) and builds a project: three stages approved, one person
     invited, one answer read -- so every route below has something real to refuse.
  3  founder B signs in in a **fresh browser context** (a new cookie jar, not a new tab); the
     landing greets *Nour Haddad*, and A's session, polled again, still carries A's own name (O5).
  4  B's `GET /v2/projects` is `[]` -- A's project is absent, not merely unopenable.
  5  every founder route in §4.3 answers B a **bare 404**: the ten reads, the two writes, the
     reading batch that used to half-execute, and `GET /v2/inference-interactions?project_id=`.
     A's project revision, re-read on A's session, is unchanged.
  6  the two 404s are the same 404 -- another founder's project and an id that exists nowhere are
     byte-identical in status, body and headers (O3).
  7  the participant page still names the **owner** (O4): opened by nobody, in a third context, it
     says *Eval Founder* and not whichever row an unordered `LIMIT 1` would have returned.
  8  B is a founder, not a spectator, and A's runtime is not B's agent: B's `/v2/me` reads
     `agent.connected: false` while A's still reads true, B's `POST /v2/projects` is refused for
     want of **B's own** agent (a refusal about B, never a 404 and never a silent success on A's
     runtime), and A's project list is untouched at the end.

**A note on what is deliberately not here.** §10.6's *"the code survives login"* block (`return_to`
carrying a `user_code` through the round trip) belongs to the connect journey and is asserted where
that journey is -- `harness/browser.py:Auth.sign_in(return_to=...)` drives it and S-011 exercises
the same `return_to` machinery on the refusal side. A second *runtime* for founder B is not
attempted at all: this profile has one runtime home, and two would collide on it.

The referee owns no product code: a leak here is a `runs/DRIFT.md` entry, never a workaround.

Moments cited: §1.0 (arrival), §1.2 (the overview), §2.1 (the participant's page).
"""

from __future__ import annotations

import re
import time
import uuid

from evals.preludes import approved_project_with_one_read
from harness.browser import Auth, Connect, Landing, ParticipantPage, People
from harness.connect import start_runtime_via_skill
from harness.evidence import finalize_run
from harness.steps import Recorder

#: A well-formed project id that exists nowhere -- step 6's other side. It has to be *well formed*
#: for the comparison to mean anything: a malformed id could be refused by a different code path
#: (a converter, a validator) and would compare two different 404s.
NOWHERE = str(uuid.UUID(int=0x5010_0000_0000_0000_0000_0000_0000_0001))


def _project_id_from_url(url: str) -> str:
    match = re.search(r"/p/([^/?#]+)", url)
    if not match:
        raise AssertionError(f"not on a project route, cannot read the project id: {url}")
    return match.group(1)


def _connect_agent(page, stack, recorder, script_path=None) -> dict:
    """A's runtime, on the scripted executor -- the same connect walk S-001 opens with."""
    env_extra = {"KEEL_SCRIPT": str(script_path)} if script_path else None
    result = start_runtime_via_skill(stack, recorder, env_extra=env_extra)
    if result["outcome"] == "authorization_started":
        connect = Connect(page, recorder)
        frame = connect.open(result["verification_uri"])
        assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()
    return result


def _first(payload, wrapper: str | None, id_key: str):
    """The first row's own id, off whichever shape this founder read uses: a bare list, or a list
    under `wrapper`. Returns `None` when there is nothing there, which the caller turns into a
    well-formed id that exists nowhere."""
    rows = payload if isinstance(payload, list) else (payload or {}).get(wrapper) or []
    return rows[0].get(id_key) if rows else None


#: The one person S-010 invites when it has to mint an invitation of its own. Not a corpus name:
#: nothing about this scenario reads an answer, and a name from a fixture would suggest otherwise.
INVITED = "Sam Okonjo"


def _invite_one(page, recorder, web_base: str, project_id: str, role_label: str) -> dict[str, str]:
    """One invitation, on whichever role the project actually has. Returns `{person: url}`, the
    shape `evals/preludes.invite_everyone` returns."""
    people = People(page, recorder, web_base)
    people.open(project_id)
    if page.locator(".role").count() == 0:
        people.switch_to_kinds_tab()
    people.open_send_popup(role_label)
    people.fill_who(INVITED, about=f"{role_label}, asked about one real occasion.")
    people.go_to_preview()
    url = people.generate_link(INVITED.split()[0])
    people.close_popup()
    return {INVITED: url}


def _bare_404(response, where: str) -> dict:
    """§4.5/O1/O3: on the founder surface an ownership failure is indistinguishable from a wrong
    id -- **404, and the body is empty**. A `Refusal` body with a rule id would undo the whole
    point of not saying 403, so the body is asserted as well as the status."""
    body = response.text()
    return {"where": where, "status": response.status, "body": body,
            "ok": response.status == 404 and not body.strip()}


def test_s010_two_founders(stack, founder_one, founder_two, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False

    context_a = browser.new_context()
    context_b = None
    context_nobody = None

    def _a(path: str):
        return context_a.request.get(f"{cloud_base}{path}", timeout=15_000)

    def _a_json(path: str) -> dict:
        return _a(path).json()

    try:
        page_a = context_a.new_page()

        # ------------------------------------------------------------------------ 1: A signs in
        Auth(page_a, recorder, web_base).sign_in(founder_one)
        landing_a = Landing(page_a, recorder, web_base)
        arrival_a = landing_a.visit()
        with recorder.step("§1.0: the landing greets founder A by their own Google name",
                            party="founder", kind="assert") as h:
            greeting = landing_a.greeting()
            me_a = _a_json("/v2/me")
            h.record_assert({"greeting names": founder_one.name,
                              "me.name": founder_one.name, "me.email": founder_one.email},
                             {"greeting": greeting, "me": me_a})
            assert founder_one.name.split()[0] in greeting, (
                f"expected the landing to greet {founder_one.name!r}, got {greeting!r}")
            assert me_a["name"] == founder_one.name, (
                f"/v2/me must answer about the caller (§4.4), got {me_a!r}")
            assert me_a["email"] == founder_one.email, me_a
            # `picture` is null for both stub identities by design (§10.2) -- the header's
            # no-picture fallback is the state the whole eval set runs in. Recorded, not required.
            h.record_wire(None, {"picture": me_a.get("picture")})

        # ------------------------------------------------- 2: A's runtime, and A's whole project
        if not arrival_a["agent_connected"]:
            _connect_agent(page_a, stack, recorder)
        landing_a.visit()
        rows = landing_a.project_rows()
        if rows:
            # Warm after S-001 or S-002 in the same stack session: that project is already
            # approved through every stage and has people on it, which is more state to refuse
            # than this scenario would build for itself.
            landing_a.open_project(0)
            project_a = _project_id_from_url(page_a.url)
            invitation_urls = {}
        else:
            project_a, invitation_urls = approved_project_with_one_read(
                page_a, recorder, browser, web_base=web_base, cloud_base=cloud_base)

        roles_a = _a_json(f"/v2/projects/{project_a}/roles")

        if not invitation_urls:
            # **Step 7 is never skipped.** The participant page naming the owner rather than
            # whichever row an unordered `LIMIT 1` returned (O4) is the assertion that fails today
            # for a reason that has nothing to do with sign-in, which is exactly why it is here --
            # so an invitation is minted rather than inherited.
            #
            # **The role label comes off the wire, never off a fixture.** Warm in a full
            # `make eval-all` pass, the project A already has is whichever one is listed first --
            # Countly, Paidly, Mulchrun or Payroll -- and each carries its own role labels. A
            # fixture's label typed into `open_send_popup` would look for a card that project has
            # never had.
            role_label = _first(roles_a, "roles", "label")
            assert role_label, f"founder A's project has no role to invite anyone to: {roles_a}"
            invitation_urls = _invite_one(page_a, recorder, web_base, project_a, role_label)

        # **Read after the invitation, never before it.** Inviting somebody moves the project's
        # revision, and `revision_before` is what step 5 re-reads to prove founder B moved nothing.
        # Taken a moment too early it would be this scenario's own write that failed the check.
        overview_a = _a_json(f"/v2/projects/{project_a}/overview")
        revision_before = overview_a.get("revision")
        invitations_a = _a_json(f"/v2/projects/{project_a}/invitations")
        readings_a = _a_json(f"/v2/projects/{project_a}/readings")

        # **The wire's own key names, not a guess.** Each founder read wraps its rows differently
        # and each row names its id after itself: `invitations` under an `invitations` key with
        # `invitationId`, `roles` under `roles` with `roleId`, and `readings` as a **bare list** of
        # `batchId`. `tests/test_two_founders_and_refusals.py` pins all three, because a key that
        # comes back `None` here would quietly turn a real id into `NOWHERE` and S-010 would prove
        # that a nonexistent project 404s -- which it does, and which is not the point.
        invitation_id = _first(invitations_a, "invitations", "invitationId") or NOWHERE
        role_id = _first(roles_a, "roles", "roleId") or NOWHERE
        batch_id = _first(readings_a, None, "batchId") or NOWHERE
        stage_type = (overview_a.get("stages") or [{}])[0].get("type") or "PROBLEM"

        with recorder.step("§1.2: founder A's project is real, and its parts are nameable",
                            party="stack", kind="assert") as h:
            h.record_assert({"project": "an id", "revision": "an integer"},
                             {"project": project_a, "revision": revision_before,
                              "invitation": invitation_id, "role": role_id, "batch": batch_id,
                              "stage": stage_type})
            assert project_a and revision_before is not None, overview_a

        # --------------------------------------------------- 3: B signs in, in a fresh cookie jar
        context_b = browser.new_context()
        page_b = context_b.new_page()

        def _b(path: str):
            return context_b.request.get(f"{cloud_base}{path}", timeout=15_000)

        Auth(page_b, recorder, web_base, party="founder-b").sign_in(founder_two)
        landing_b = Landing(page_b, recorder, web_base, party="founder-b")
        arrival_b = landing_b.visit()
        with recorder.step("§1.0: the second founder is greeted as themselves, and the first "
                            "still as themselves (O5)", party="founder-b", kind="assert") as h:
            greeting_b = landing_b.greeting()
            me_b = _b("/v2/me").json()
            me_a_again = _a_json("/v2/me")
            h.record_assert({"B greeted": founder_two.name, "B email": founder_two.email,
                              "A still": founder_one.name},
                             {"greeting": greeting_b, "me_b": me_b, "me_a": me_a_again})
            assert founder_two.name.split()[0] in greeting_b, (
                f"expected the landing to greet {founder_two.name!r}, got {greeting_b!r}")
            assert me_b["name"] == founder_two.name and me_b["email"] == founder_two.email, (
                f"/v2/me answered B with somebody else's row (the `LIMIT 1` defect §4.3 names): "
                f"{me_b!r}")
            assert me_a_again["name"] == founder_one.name, (
                f"founder A's own session started answering as somebody else: {me_a_again!r}")
            assert me_b["name"] != me_a_again["name"], "both sessions read the same account"

        with recorder.step("§1.0: nothing was refused on the way in, and no setup screen exists "
                            "to have been reached", party="founder-b", kind="assert") as h:
            h.record_assert({"auth_error": None, "frame": "L1 or L2"},
                             {"url": page_b.url, "frame": arrival_b["frame"]})
            assert "auth_error" not in page_b.url, page_b.url
            assert "/setup" not in page_b.url, (
                "there is no setup route left to route to (§4.7)")

        # ------------------------------------------------------------ 4: B's landing is B's alone
        with recorder.step("§1.0: founder B's project list is empty -- A's project is absent, "
                            "not merely unopenable", party="founder-b", kind="assert") as h:
            listed = _b("/v2/projects").json()
            names = listed if isinstance(listed, list) else listed.get("projects", listed)
            h.record_assert([], names)
            assert names == [] or names == {} or names is None, (
                f"founder B's landing showed somebody else's projects: {listed!r}")
            assert arrival_b["has_projects"] is False, (
                f"founder B's landing rendered a project list: {arrival_b}")

        # ------------------------------------ 5: every founder route in §4.3, on B's own session
        reads = [
            (f"/v2/projects/{project_a}/overview", "overview"),
            (f"/v2/projects/{project_a}/stages/{stage_type}", "stages/{stage}"),
            (f"/v2/projects/{project_a}/invitations", "invitations"),
            (f"/v2/projects/{project_a}/invitations/{invitation_id}", "invitations/{id}"),
            (f"/v2/projects/{project_a}/roles", "roles"),
            (f"/v2/projects/{project_a}/roles/{role_id}/preview", "roles/{id}/preview"),
            (f"/v2/projects/{project_a}/people", "people"),
            (f"/v2/projects/{project_a}/readings", "readings"),
            (f"/v2/projects/{project_a}/readings/{batch_id}", "readings/{id}"),
            (f"/v2/projects/{project_a}/standing", "standing"),
        ]
        with recorder.step("§1.2 wire: all ten of §4.3's reads answer founder B a bare 404 "
                            "(O1, O3)", party="founder-b", kind="assert") as h:
            results = [_bare_404(_b(path), where) for path, where in reads]
            h.record_assert({"every one": "404 with an empty body"}, results)
            bad = [r for r in results if not r["ok"]]
            assert not bad, (
                "another founder's project must be indistinguishable from a wrong id -- 404, and "
                f"the body empty (§4.5). These were not: {bad}")

        # **Well-formed bodies, on purpose.** Each carries the fields its own DTO declares and
        # `revision_before`, the revision A's project is genuinely at -- so a 404 here is the
        # ownership check and never a body keel-cloud could not read. `POST /readings` declares no
        # body at all.
        writes = [
            (f"/v2/projects/{project_a}/stages/{stage_type}/approval",
             {"expectedRevision": revision_before}, "POST stages/{stage}/approval"),
            (f"/v2/projects/{project_a}/invitations",
             {"roleId": role_id, "personName": "Nobody At All",
              "about": "a person founder B has no business inviting",
              "expectedRevision": revision_before}, "POST invitations"),
            (f"/v2/projects/{project_a}/readings", None, "POST readings"),
        ]
        with recorder.step("§1.2 wire: the two writes and the reading batch answer B the same "
                            "bare 404 -- and the batch does not half-execute",
                            party="founder-b", kind="assert") as h:
            results = []
            for path, body, where in writes:
                response = (context_b.request.post(f"{cloud_base}{path}", data=body,
                                                    timeout=15_000)
                            if body is not None
                            else context_b.request.post(f"{cloud_base}{path}", timeout=15_000))
                results.append(_bare_404(response, where))
            batches_after = _a_json(f"/v2/projects/{project_a}/readings")
            h.record_assert({"every one": "404 with an empty body",
                              "A's reading batches": "unchanged"},
                             {"writes": results, "before": readings_a, "after": batches_after})
            bad = [r for r in results if not r["ok"]]
            assert not bad, (
                f"a write on another founder's project must be a bare 404 (§4.5): {bad}")
            assert batches_after == readings_a, (
                "POST /readings wrote a reading_batch row on another founder's project before "
                f"refusing (§4.3's half-execution): {readings_a} -> {batches_after}")

        with recorder.step("§1.2 wire: the interactions read is scoped too, and A's project is "
                            "untouched", party="founder-b", kind="assert") as h:
            interactions = _b(f"/v2/inference-interactions?project_id={project_a}")
            revision_after = _a_json(f"/v2/projects/{project_a}/overview").get("revision")
            h.record_assert({"interactions": 404, "revision": revision_before},
                             {"interactions": interactions.status, "revision": revision_after})
            assert interactions.status == 404, (
                f"GET /v2/inference-interactions?project_id= answered B "
                f"{interactions.status}, not 404")
            assert revision_after == revision_before, (
                f"founder A's project moved while founder B was poking at it: "
                f"{revision_before} -> {revision_after}")

        # ------------------------------------------------- 6: the two 404s are the same 404 (O3)
        with recorder.step("§1.2 wire: another founder's project and an id that exists nowhere "
                            "are byte-identical (O3)", party="founder-b", kind="assert") as h:
            theirs = _b(f"/v2/projects/{project_a}/overview")
            nowhere = _b(f"/v2/projects/{NOWHERE}/overview")
            shape = lambda r: {  # noqa: E731 - a local, read once, two lines below
                "status": r.status, "body": r.text(),
                "content_type": (r.headers or {}).get("content-type"),
            }
            theirs_shape, nowhere_shape = shape(theirs), shape(nowhere)
            h.record_assert(theirs_shape, nowhere_shape)
            assert theirs_shape == nowhere_shape, (
                "a 403 in 404's clothing: another founder's project answered differently from an "
                f"id that exists nowhere. {theirs_shape} vs {nowhere_shape}")

        # ---------------------------------------- 7: the participant page names the owner (O4)
        if invitation_urls:
            context_nobody = browser.new_context()
            page_nobody = context_nobody.new_page()
            participant = ParticipantPage(page_nobody, recorder)
            url = next(iter(invitation_urls.values()))
            participant.open(url)
            with recorder.step("§2.1: the participant's form names the project's owner, not "
                                "whichever founder a LIMIT 1 found (O4)",
                                party="participant", kind="assert") as h:
                asked_by = page_nobody.locator("body").inner_text()
                h.record_assert({"names": founder_one.name, "never": founder_two.name},
                                 {"page": asked_by[:600]})
                assert founder_one.name in asked_by, (
                    f"the participant page does not name the owner {founder_one.name!r}")
                assert founder_two.name not in asked_by, (
                    f"the participant page named the *other* founder {founder_two.name!r} -- "
                    "FounderNames resolved through the instance, not through project.ownerId")

        # ----------------------------- 8: B is a founder, and A's runtime is not B's agent
        with recorder.step("§1.0: A's runtime still polls for A and is not B's agent",
                            party="stack", kind="assert") as h:
            me_a_now = _a_json("/v2/me")
            me_b_now = _b("/v2/me").json()
            h.record_assert({"A connected": True, "B connected": False},
                             {"A": me_a_now.get("agent"), "B": me_b_now.get("agent")})
            assert (me_a_now.get("agent") or {}).get("connected") is True, (
                f"founder A's runtime stopped being connected while B was signing in: {me_a_now}")
            assert (me_b_now.get("agent") or {}).get("connected") is False, (
                f"founder B inherited founder A's runtime: {me_b_now}")

        with recorder.step("§1.0: founder B is a founder, not a spectator -- and is told about "
                            "their own agent, never handed somebody else's",
                            party="founder-b", kind="assert") as h:
            created = context_b.request.post(f"{cloud_base}/v2/projects",
                                             data={"name": "Nour's own", "market":
                                                   {"country": "GB", "region": None}},
                                             timeout=15_000)
            body = created.text()
            h.record_assert({"status": "201, or a refusal naming B's own agent",
                              "never": "404, and never a project on A's runtime"},
                             {"status": created.status, "body": body[:400]})
            assert created.status != 404, (
                "founder B was refused as if they were not a founder at all; the ownership rule "
                "is 404 for *another founder's project*, never for the founder themselves")
            if created.status >= 400:
                assert "agent" in body.lower(), (
                    f"B's creation was refused for something other than B's own agent: {body}")

        with recorder.step("§1.0 wire: founder A's project list is exactly A's, at the end of "
                            "all of it", party="stack", kind="assert") as h:
            listed = _a_json("/v2/projects")
            rows = listed if isinstance(listed, list) else listed.get("projects", [])
            # `GET /v2/projects` rows name the id `projectId`, not `id`.
            ids = [row.get("projectId") for row in rows] if isinstance(rows, list) else []
            h.record_assert({"contains": project_a}, {"ids": ids})
            assert project_a in ids, (
                f"founder A's own project left A's list: {listed!r}")

        passed = True
    finally:
        for context in (context_nobody, context_b, context_a):
            if context is not None:
                context.close()
        finalize_run(run_dir, slug="s010-two-founders", facts={}, passed=passed,
                     failed_step=None if passed else "see transcript.jsonl",
                     duration_s=time.monotonic() - started)

    assert passed
