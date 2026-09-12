"""S-002, the agent-optional day (spec 006-agent-optional): a founder connects a runtime, creates
a project, logs out; later the runtime is not running and they log back in. Creating a *new*
project must be disabled -- but everything else they own must still work: read the project, send
interview links, download the brief. "The local runtime is only needed to create a project or to
infer the result."

Journey coverage (keel-cloud `canon/journeys.md` §3, 2026-09-03): §1.0 (arrival -- the landing's
four shapes, L4 in particular), §1.4 (inviting, with no agent), §1.5 (waiting -- the table's own
two columns), §1.6 (reading what came back -- the one thing this scenario expects to find
*not* offered), §1.10 (the brief, a derived summary, no agent needed to read it).

**This scenario's own prediction (spec's "What I expect this to find")**: keel-web's People page
never consults the agent state at all -- the read action is disabled only by `unreadCount === 0`,
so with an unread answer and no runtime it is expected to be *offered*, not disabled with a
reason. If confirmed, that is US1 acceptance scenario 3 failing and a `runs/DRIFT.md` entry, never
a harness workaround (this repo owns no product code).

**Resolved findings this scenario now pins**: #17 (the read action is disabled with its reason when
no agent is connected), #18 (no stale completion toast after re-login) and #19 (a runtime that
reconnects silently binds the keel session that is open now -- the logout/login workaround this
file carried for one run is gone).

Prelude (spec edge case): reuses whatever project already exists in this same stack session (an
S-001 run, most naturally) if one does; otherwise builds its own via
`evals/preludes.approved_project_with_one_read` -- a project approved through every stage, one
role invited, one answer already read, agent connected throughout. Either way, this scenario's own
work starts once that baseline exists: log out, stop the runtime, log back in, and walk US1's
steps 2-8 against a *reused* project and a fresh agent-optional invitation of its own.
"""

from __future__ import annotations

import re
import time

from evals import payroll_exceptions as fx
from evals.facts import Fact
from evals.preludes import approved_project_with_one_read
from harness.browser import (Auth, Connect, Landing, OpenedCard, ParticipantPage, People,
                              PrintPage, Shell)
from harness.connect import reconnect, start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run
from harness.steps import Recorder

# A second, genuinely different payroll manager (spec US1 step 4: a fresh, still-unread
# invitation created while no agent is connected) -- same kind of person as `fx.PARTICIPANTS[0]`
# (Dana Okafor, already invited and read by the prelude). An invitation asks only what is still
# open for that kind of person at the moment it is generated (keel-cloud derives the asks from
# the aggregate; a belief the agent has already found holding up is not asked again), so Priya's
# page carries fewer questions than Dana's did -- live-confirmed (run
# `20260904T040636Z-s002-agent-optional`): one question, the solution-stage belief. Her answers are
# therefore an ordered list the harness types into whatever questions exist, first answer first,
# and the scenario asserts on -- and registers as facts -- only what was actually typed.
# spec 010: the fixture is data now (`evals/payroll_exceptions.yaml`), read through the same
# generator every other scenario uses. The second person is the fixture's own second one -- a
# genuinely different person of the same kind, whose invitation is created while no agent is
# connected (US1 step 4).
SECOND_PARTICIPANT = fx.people()[1]


def _facts(typed_answers: list[str]) -> dict[str, Fact]:
    """S-001's statements and roles, plus the words this scenario's own participant actually typed.
    The prelude's participants' *answers* are left out on purpose: their `participant_page` hop is
    the founder's P9 popup, and this scenario never opens it for them (the prelude reads Dana
    through the agent, not through P9). A fact registered for a screen the run never visits is not
    evidence of infidelity, it is a check with nothing to check -- live-confirmed (run
    `20260904T034746Z-s002-agent-optional`): FIDELITY 1.0 on a run where every word shown was
    shown verbatim. Priya's facts are likewise only the answers her page had questions for."""
    base = fx.facts()
    result = {
        # What this scenario itself puts on a screen, warm path or cold: the project's name and the
        # problem claim on the problem card (the only stage card it opens), all three claims on the
        # brief, and the one kind of person whose send popup it opens. The solution and commercial
        # cards, and the other two roles' popups, are the prelude's screens -- when the prelude runs
        # (cold) they are extra evidence, but a warm run that reuses S-001's project never visits
        # them, and a fact registered for an unvisited hop scored FIDELITY 3.5 on
        # `20260904T044246Z-s002-agent-optional` for words that were never shown wrongly.
        "name": base["name"],
        "statement.PROBLEM": base["statement.PROBLEM"],
        # spec 010: `brief` retired with the route it named; the download page is where all three
        # claims are read back now, and it needs no agent either.
        "statement.SOLUTION": Fact(text=base["statement.SOLUTION"].text, kind="statement",
                                    hops=["download"]),
        "statement.COMMERCIAL": Fact(text=base["statement.COMMERCIAL"].text, kind="statement",
                                      hops=["download"]),
    }
    for key, fact in base.items():
        if key.startswith("role."):
            result[key] = fact
    slug = SECOND_PARTICIPANT.person.lower().replace(" ", "_")
    for n, text in enumerate(typed_answers, start=1):
        result[f"{slug}_answer_{n}"] = Fact(text=text, kind="answer", hops=["participant_page"])
    return result


def _project_id_from_url(url: str) -> str:
    match = re.search(r"/p/([^/?#]+)", url)
    if not match:
        raise AssertionError(f"not on a project route, cannot read the project id: {url}")
    return match.group(1)


def _wait_for_agent_disconnected(get_json, recorder, *, timeout_s: float = 130) -> None:
    """`KeelSessionService.connection` (keel-cloud) recomputes "connected" fresh on every call
    from the bound agent session's own `lastSeenAt` -- killing the runtime by pid (`stop_runtime`)
    stops new heartbeats immediately, but the *previous* heartbeat still reads live until
    `keel.v2.connect.presence-threshold` has elapsed since it (shipped default `PT90S`, not
    shortened by this stack -- `application.yml`: "deliberately well over 3x poll-window so an
    agent between two long-polls doesn't trip itself"). A keel session opened inside that window
    auto-binds to the just-killed-but-not-yet-stale agent session (`KeelSessionService.open`'s own
    "most recently seen one"), so the landing can genuinely read agent-connected for up to ~90s
    after the runtime is truly dead. Live-confirmed (run `20260904T030131Z-s002-agent-optional`):
    re-login immediately after `stop_runtime` read L3, not L4.

    Waited out here, not asserted around -- the same way `Connect.wait_for_connected` waits for
    the opposite transition (spec's own 30s ceiling on that side; this side's ceiling is the
    presence threshold itself, plus margin)."""
    with recorder.step("waiting out keel-cloud's own presence threshold since the runtime died",
                        party="stack", kind="assert") as h:
        deadline = time.monotonic() + timeout_s
        me = get_json("/v2/me")
        connected = bool((me.get("agent") or {}).get("connected"))
        while connected and time.monotonic() < deadline:
            time.sleep(2)
            me = get_json("/v2/me")
            connected = bool((me.get("agent") or {}).get("connected"))
        h.record_assert(False, connected)
        if connected:
            h.fail(f"agent still reads connected {timeout_s}s after the runtime was stopped: {me}")
            raise AssertionError(
                f"agent still reads connected {timeout_s}s after the runtime was stopped: {me}")


def _connect_agent(page, stack, recorder) -> dict:
    """Runs the connect skill and, if it comes back needing device approval, drives frame B --
    the same connect walk `evals/test_s001_smoke.py` opens the smoke with. Tolerates
    `already_connected`/`connected` (a still-running runtime the new keel session already bound
    to automatically -- journeys §1.0's own "login ... binds a still-running runtime
    automatically") by skipping the browser approval it would have nothing left to approve."""
    result = start_runtime_via_skill(stack, recorder)
    if result["outcome"] == "authorization_started":
        connect = Connect(page, recorder)
        frame = connect.open(result["verification_uri"])
        with recorder.step("§1.0: the verification URI opens frame B", party="founder", kind="assert") as h:
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()
    return result


def test_s002_agent_optional(stack, founder_one, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    cloud_base = stack.cloud_base_url
    typed_answers: list[str] = []
    started = time.monotonic()
    passed = False
    context = browser.new_context()

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=10_000).json()

    def _get_response(path: str):
        return context.request.get(f"{cloud_base}{path}", timeout=10_000)

    def _post_raw(path: str, body: dict):
        return context.request.post(f"{cloud_base}{path}", data=body, timeout=10_000)

    try:
        page = context.new_page()

        # ---------------------------------------------------------- the baseline (spec edge case)
        Auth(page, recorder, web_base).sign_in(founder_one)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()

        if not arrival["agent_connected"]:
            _connect_agent(page, stack, recorder)

        if arrival["has_projects"]:
            # Same stack session as an already-run S-001 (or an earlier S-002) -- reuse that
            # project wholesale rather than building a second one alongside it.
            landing.visit()
            landing.open_project(0)
            project_id = _project_id_from_url(page.url)
        else:
            project_id, _ = approved_project_with_one_read(
                page, recorder, browser, web_base=web_base, cloud_base=cloud_base)

        # ------------------------------------------------------------------- US1 step 1: log out
        landing.visit()
        landing.log_out()
        stop_runtime(stack, recorder)

        # ------------------------------------------------------------ US1 step 2: L4 on re-login
        # US1's whole point is *the founder logs back in with no runtime*, and that second
        # login is now the Google round trip end to end -- start, the stub's picker, the callback,
        # a rotated session id and a fresh keel session. The assertions below it are untouched.
        Auth(page, recorder, web_base).sign_in(founder_one)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()
        if arrival["agent_connected"]:
            # The keel session this login just opened auto-bound to the just-killed runtime's own
            # agent session, which keel-cloud still reads as live (presence threshold, not yet
            # elapsed) -- wait it out rather than asserting into a real timing window (see
            # `_wait_for_agent_disconnected`'s own docstring).
            _wait_for_agent_disconnected(_get, recorder)
            arrival = landing.visit()
        locked = landing.new_project_locked_reason()
        with recorder.step("§1.0: the re-login landing reads L4 -- projects, no agent, creation locked",
                            party="founder", kind="assert") as h:
            h.record_assert(
                {"frame": "L4", "agent_connected": False, "locked_present": True, "locked_enabled": False},
                {"frame": arrival["frame"], "agent_connected": arrival["agent_connected"],
                 "locked_present": locked["present"], "locked_enabled": locked["enabled"],
                 "locked_reason": locked["reason"]})
            assert arrival["has_projects"], "expected the baseline project to still be there after re-login"
            assert not arrival["agent_connected"], (
                f"expected no agent connected right after re-login, got frame {arrival['frame']!r}")
            assert arrival["frame"] == "L4", f"expected L4 (projects, no agent), got {arrival['frame']!r}"
            assert locked["present"], "expected the locked New project card to render"
            assert not locked["enabled"], "expected New project disabled with no agent connected"
            assert locked["reason"], "US1 acceptance scenario 1: expected a reason beside the locked action"

        rows = landing.project_rows()
        with recorder.step("§1.0: every project row is still clickable on L4", party="founder", kind="assert") as h:
            h.record_assert(">=1 row", rows)
            assert rows, "expected at least one project row to still render on L4"

        with recorder.step("wire: POST /v2/projects refuses with no live agent",
                            party="stack", kind="assert") as h:
            response = _post_raw("/v2/projects", {"name": "S-002 wire probe (expected to refuse)"})
            body = response.json()
            h.record_assert({"status": 422, "rule": "agent"}, {"status": response.status, "body": body})
            assert response.status == 422, (
                f"US1 acceptance scenario 6: expected 422, got {response.status}: {body}")
            assert body.get("rule") == "agent", f"expected rule 'agent', got {body}"

        # ------------------------------------------------------------- US1 step 3: the project reads
        landing.open_project(0)
        project_id_now = _project_id_from_url(page.url)
        with recorder.step("the reopened project is the same one from before logout",
                            party="stack", kind="assert") as h:
            h.record_assert(project_id, project_id_now)
            assert project_id_now == project_id, f"expected the same project id, got {project_id_now!r}"
        project_id = project_id_now

        problem_card = OpenedCard(page, recorder, web_base)
        opened = problem_card.open(project_id, "PROBLEM")
        with recorder.step("the approved problem card still renders its claim and beliefs, no agent",
                            party="founder", kind="assert") as h:
            claim = problem_card.claim()
            # An *opened* card draws its beliefs as strip rows, not as `StageCard`'s review-time
            # `.belief .b-heading` list -- `belief_headings()` belongs to the review card and has
            # never existed here. Reading it off `OpenedCard` raised `AttributeError` three
            # minutes into a stack run, on the first `make eval-all` since spec 010 rewrote these
            # screens (`runs/20260907T164650Z-s002-agent-optional`; `runs/DRIFT.md` #33's note on
            # the referee's own grip).
            headings = [row["heading"] for row in problem_card.strips() if row["heading"]]
            is_draft = problem_card.is_draft()
            h.record_assert({"is_draft": False, "claim": ">=1 char", "beliefs": ">=1"},
                             {"is_draft": is_draft, "claim": claim, "beliefs": headings})
            assert not is_draft, f"expected the approved (not draft) problem card, got {opened}"
            assert claim, "expected the approved claim to still render with no agent"
            assert headings, "expected the beliefs to still render with no agent"

        shell = Shell(page, recorder)
        nav_status = shell.nav_status("PROBLEM")
        with recorder.step("the side nav's stage word still renders, unchanged and not disabled",
                            party="founder", kind="assert") as h:
            h.record_assert(">=1 char", nav_status)
            assert nav_status, "expected the problem stage's side-nav status word to still render"

        # ------------------------------------------------------ US1 step 4: inviting works, no agent
        people = People(page, recorder)
        people.open(project_id)
        if page.locator(".role").count() == 0:
            people.switch_to_kinds_tab()
        second_role = next(r["label"] for r in fx.entry().roles
                            if r["id"] == SECOND_PARTICIPANT.role_id)
        people.open_send_popup(second_role)
        people.fill_who(SECOND_PARTICIPANT.person,
                         about=f"{second_role}, asked about one real occasion.")
        preview = people.go_to_preview()
        with recorder.step("§1.4: the preview shows what they'll be asked, no agent needed",
                            party="founder", kind="assert") as h:
            h.record_assert(">=1 char", preview)
            assert preview, "expected a non-empty preview of what the participant will be asked"

        with page.expect_response(
            lambda r: r.url.endswith("/invitations") and r.request.method == "POST"
        ) as invite_resp_info:
            invite_url = people.generate_link(SECOND_PARTICIPANT.person.split()[0])
        invite_response = invite_resp_info.value
        with recorder.step("§1.4 wire: POST .../invitations succeeds with no live agent",
                            party="stack", kind="assert") as h:
            h.record_assert(201, invite_response.status)
            assert invite_response.status == 201, (
                f"US1 acceptance scenario 2: expected 201, got {invite_response.status}")
        people.close_popup()
        with recorder.step("§1.4: the generated link is real", party="founder", kind="assert") as h:
            h.record_assert("non-empty url", invite_url)
            assert invite_url, "expected a real invitation link, not a placeholder"

        participant_context = browser.new_context()
        try:
            participant_page = participant_context.new_page()
            pb = ParticipantPage(participant_page, recorder)
            pb.open(invite_url)
            pb.answer_as(SECOND_PARTICIPANT, fx.entry())
            typed_answers = [a.text for a in SECOND_PARTICIPANT.written() if a.text]
            pb.submit()
        finally:
            participant_context.close()

        # --------------------------------------------------- US1 step 5: reading is not offered
        # `usePeople` is a plain one-shot query, never polled (unlike the reading-batch query) --
        # the participant's own submission happened in a separate browser context, so this founder
        # page needs a fresh fetch (a re-`open`, exactly S-001's own pattern) before it shows it.
        people.open(project_id)
        people.switch_to_who_tab()
        rows = people.table_rows()
        first_name = SECOND_PARTICIPANT.person.split()[0]
        # The **last** row bearing this name, not the first. On the warm path this scenario reuses
        # S-001's own project, and spec 010 grew the smoke from three people to eleven -- so
        # `SECOND_PARTICIPANT` (`fx.people()[1]`, Wei Zhang) already has a row there, invited and
        # *read*, before S-002 invites its own. Matching the first row found the smoke's, whose
        # `Your agent` correctly reads *Read · today · …*, and S-002 failed asserting the one thing
        # it exists to assert (`runs/20260907T171131Z-s002-agent-optional`; `runs/DRIFT.md` #33).
        # The table lists invitations in the order they were sent, so the row this scenario just
        # created is the last of its name.
        target_row = next((r for r in reversed(rows) if first_name in r["person"]), None)
        with recorder.step("§1.5: the new answer shows in Their answer; Your agent reads Not read yet",
                            party="founder", kind="assert") as h:
            h.record_assert({"their_answer": "answered", "your_agent": "not read yet"}, target_row)
            assert target_row is not None, f"expected a row for {SECOND_PARTICIPANT.person!r}, got {rows}"
            assert "answered" in target_row["their_answer"].lower(), (
                f"expected Their answer to read Answered, got {target_row!r}")
            assert "not read yet" in target_row["your_agent"].lower(), (
                f"expected Your agent to read Not read yet, got {target_row!r}")

        # §1.6: seeing a person's own words needs no agent -- the founder's reading and the
        # agent's inference are two different things (screen-review design, People). This is the
        # sentence S-002 exists to pin, so it is asserted here with the runtime dead, and it is
        # also how Priya's typed answers reach FID's `participant_page` hop on the founder's screen.
        # `last=True` for the same reason `target_row` is read from the end: on the warm path
        # S-001's project already carries a read invitation for this person (`runs/DRIFT.md` #33).
        people.open_answers_popup(first_name, last=True)
        answers = people.answers_popup_text()
        with recorder.step(f"§1.6: with no agent, P9 still shows {first_name}'s own words verbatim",
                            party="founder", kind="assert") as h:
            joined = "\n".join(row["answer"] for row in answers["qa"])
            missing = [text for text in typed_answers if text not in joined]
            h.record_assert(typed_answers, joined)
            assert typed_answers, "expected the participant page to have carried at least one question"
            assert not missing, f"expected {first_name}'s own words in P9, missing {missing}"
        people.close_answers_popup()

        read_state = people.read_action_state()

        if read_state["enabled"]:
            # The predicted defect (spec's own "What I expect this to find"): the read action is
            # offered with no agent connected. Before failing the scenario over it, click it and
            # capture what actually happens -- the wire refusal AND the screen's own silence about
            # it -- so the DRIFT entry carries both kinds of evidence side by side, not just the
            # screen's own enabled state.
            with recorder.step("DRIFT evidence: clicking the offered read action with no agent",
                                party="stack", kind="assert") as h:
                with page.expect_response(
                    lambda r: r.url.endswith("/readings") and r.request.method == "POST"
                ) as click_resp_info:
                    page.get_by_role("button", name=re.compile("have your agent read", re.I)).click()
                click_response = click_resp_info.value
                click_body = click_response.json() if click_response.status != 204 else None
                page.wait_for_timeout(500)  # let any (absent) error UI settle before the screenshot
                shot = recorder.next_screenshot_name("people-read-clicked-refused")
                page.screenshot(path=str(recorder.screenshot_path(shot)), full_page=True)
                h.add_screenshot(shot)
                h.record_wire({"POST": "/readings"}, {"status": click_response.status, "body": click_body})
                h.capture_text("screen", "people")

        with recorder.step("§1.5/§1.6: the read action is disabled and states why, with no agent",
                            party="founder", kind="assert") as h:
            h.record_assert({"enabled": False, "reason": "non-empty"}, read_state)
            # US1 acceptance scenario 3 / this spec's own stated prediction: keel-web's People
            # page never consults the agent state, so the button stays offered on `unreadCount >
            # 0` alone. If this assertion fails, that is the finding -- record it in
            # runs/DRIFT.md with this screen's evidence beside the wire evidence above, never
            # worked around here.
            assert not read_state["enabled"], (
                "US1 scenario 3: expected the read action disabled with no agent connected, "
                f"got {read_state!r}")
            assert read_state["reason"], (
                f"US1 scenario 3: expected a reason shown beside the disabled read action, got {read_state!r}")

        # -------------------------------------------- US1 step 6: the download still downloads
        # spec 010: `/p/:id/brief` is gone with `BriefRoute.tsx`. What a founder downloads now is
        # the print page, and the sentence this step exists to pin is unchanged -- it needs no
        # agent, because it is derived from what is already recorded.
        print_page = PrintPage(page, recorder, web_base)
        print_page.open(project_id)
        with recorder.step("§1.10: the download renders its sheets with no agent",
                            party="founder", kind="assert") as h:
            sheets = print_page.sheets()
            h.record_assert(">= 1 sheet", len(sheets))
            assert sheets, "expected the download page to render its sheets with no agent"
        with recorder.step("§1.10: the download quotes who was asked, no agent",
                            party="founder", kind="assert") as h:
            quotes = print_page.quotes()
            h.record_assert(">=1 quote", len(quotes))
            assert quotes, "expected the download's own *In their words* quotes to render"

        with recorder.step("wire: GET .../standing reads 200 with no live agent",
                            party="stack", kind="assert") as h:
            response = _get_response(f"/v2/projects/{project_id}/standing")
            h.record_assert(200, response.status)
            assert response.status == 200, f"expected 200, got {response.status}: {response.text()}"

        # -------------------------------------------------------------------- US1 step 7: reconnect
        result = reconnect(stack, recorder)
        with recorder.step("wire: keel-connect-skill's own outcome for the reconnect",
                            party="stack", kind="assert") as h:
            h.record_assert("authorization_started | connected | already_connected", result.get("outcome"))

        if result["outcome"] == "authorization_started":
            # The spec's own narrated happy path: the prior device authorization was spent, a
            # fresh one is minted, and the founder approves it in the browser exactly as arrival
            # did (frame B).
            connect = Connect(page, recorder)
            frame = connect.open(result["verification_uri"])
            with recorder.step("§1.0: the verification URI opens frame B again", party="founder", kind="assert") as h:
                h.record_assert("B", frame)
                assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
            connect.approve()
            connect.wait_for_connected(timeout_s=30)
            connect.go_to_projects()
        else:
            # The stack's stored, still-valid runtime credential makes `keel_connect_check.py`
            # reconnect silently ("connected") -- no device code is minted, so there is no frame B
            # to approve. keel-cloud binds the new agent session to the founder's *currently open*
            # keel session as well as to the one that approved the credential
            # (`AgentSessionService.create`, the fix for runs/DRIFT.md #19), so the landing that is
            # already open must turn green on its own, within the runtime's first heartbeat. Before
            # that fix the only way through was to log out and back in; that workaround is gone,
            # so a regression here fails the run instead of being routed around.
            with recorder.step("§1.0: a silent reconnect binds the keel session that is open now (DRIFT #19)",
                                party="stack", kind="assert") as h:
                deadline = time.monotonic() + 40
                seen = landing.visit()
                while not seen["agent_connected"] and time.monotonic() < deadline:
                    time.sleep(2)
                    seen = landing.visit()
                h.record_assert({"agent_connected": True}, {"agent_connected": seen["agent_connected"]})
                h.capture_text("screen", "landing")
                assert seen["agent_connected"], (
                    "DRIFT #19 regressed: the reconnected runtime never bound the open keel session "
                    "(landing still reads no agent connected after 40s)")

        landing.visit()
        with recorder.step("§1.0: the agent line reads connected again", party="founder", kind="assert") as h:
            agent_line = shell.agent_line_text()
            h.record_assert("agent connected", agent_line)
            assert "agent connected" in agent_line.lower(), f"expected agent connected, got {agent_line!r}"

        landing.open_project(0)
        people = People(page, recorder)
        people.open(project_id)
        people.switch_to_who_tab()
        read_state = people.read_action_state()
        with recorder.step("§1.6: the read action is available again, reconnected",
                            party="founder", kind="assert") as h:
            h.record_assert({"enabled": True}, read_state)
            assert read_state["enabled"], f"expected the read action enabled once reconnected, got {read_state!r}"

        read_result = people.read_all_and_wait(timeout_s=60)
        with recorder.step("§1.6: the toast names what moved", party="founder", kind="assert") as h:
            h.record_assert("non-empty toast", read_result["toast_text"])
            assert read_result["toast_text"].strip(), "expected a non-empty toast after the agent read the answer"

        problem_card_after = OpenedCard(page, recorder, web_base)
        opened_after = problem_card_after.open(project_id, "PROBLEM")
        with recorder.step("§1.6: the card still carries a verdict once read",
                            party="founder", kind="assert") as h:
            h.record_assert("a status word", opened_after["status"])
            assert opened_after["status"], "expected the problem card to still show a status word"

        # --------------------------------------------------------- US1 step 8: new project allowed again
        landing.visit()
        arrival_final = landing.visit()
        new_project_enabled = landing.new_project_enabled()
        with recorder.step("§1.0: New project is live again, agent reconnected",
                            party="founder", kind="assert") as h:
            h.record_assert({"agent_connected": True, "new_project_enabled": True},
                             {"agent_connected": arrival_final["agent_connected"],
                              "new_project_enabled": new_project_enabled})
            assert arrival_final["agent_connected"], "expected the agent connected on the final landing visit"
            assert new_project_enabled, "expected New project enabled again once reconnected"

        passed = True
    finally:
        context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s002-agent-optional", facts=_facts(typed_answers), passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
