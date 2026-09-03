"""S-001, the smoke (spec 005-connect-stack T013): one founder's whole discovery, deterministic,
against the real four applications, with keel-runtime's scripted executor answering from its
bundled payroll-exceptions script (`evals/payroll_exceptions.py` mirrors it -- names, statements,
the participants' typed answers).

Journey coverage (CANON.md's ledger, `canon/journeys.md` §3, 2026-09-03): this is the one module
proving §1.0 (arrival: setup/login, connect by device code, gated landing), §1.1 (the idea becomes
three bets), §1.2 (review before spend), §1.4 (approve every framed card, then invite), §1.5
(waiting -- the UI counts, never interprets), §1.6 (reading what came back), §1.7 (where it
stands), §1.10 (the brief as a derived standing), §2.1 (the stranger's four honest lines, consent
by starting), §2.2 (answering; every question skippable), §2.3 (thanks, no promises the product
can't keep). §1.3, §1.8, §1.9, §2.4 are WAIVED in CANON.md §5 -- deferred by the founder, or not on
this smoke's path.

No LLM anywhere (spec FR-013's own rule): every inference job is answered by keel-runtime's
scripted executor, started only through keel-connect-skill's script (`harness/connect.py`) --
never `python3 -m keel_runtime` called directly by this harness.
"""

from __future__ import annotations

import re
import time

from evals import payroll_exceptions as fixture
from harness.browser import Auth, Brief, Chat, Connect, Landing, ParticipantBrowser, People, Shell, StageCard
from harness.connect import start_runtime_via_skill
from harness.evidence import finalize_run
from harness.steps import Recorder
from stack.auth import login_and_keel_session


def _project_id_from_url(url: str) -> str:
    match = re.search(r"/p/([0-9a-fA-F-]{8,})", url)
    assert match, f"expected a project id in the URL, got {url!r}"
    return match.group(1)


def test_s001_smoke(stack, founder_credentials, browser, run_dir):
    recorder = Recorder(run_dir)
    started = time.monotonic()
    passed = False
    failed_step: str | None = None
    context = browser.new_context()
    page = context.new_page()

    try:
        # ---------------------------------------------------------------------------- §1.0 Arrival
        # Login -> the landing reads "No agent connected" and is gated (L2) -- the runtime-home
        # gate leaves no heartbeat from a prior run (make up's own reset, spec edge cases), so
        # this is genuinely the first time this stack has ever read as connected.
        auth = Auth(page, f"http://localhost:{stack.web_port}", recorder)
        auth.log_in(email=founder_credentials.email, password=founder_credentials.password)

        landing = Landing(page, f"http://localhost:{stack.web_port}", recorder)
        landing.open()
        assert "no agent connected" in landing.agent_line_text().lower(), (
            f"§1.0: expected the landing to read 'No agent connected' before the runtime "
            f"connects, got {landing.agent_line_text()!r}")
        assert landing.is_gated(), "§1.0: expected the landing gated (L2) with no agent connected"

        # keel-runtime is started through keel-connect-skill's own script (spec edge cases: the
        # harness never shells `python3 -m keel_runtime` itself) -- its one line of JSON hands
        # back the device code the browser then opens and approves.
        started_runtime = start_runtime_via_skill(stack, recorder)
        assert started_runtime["outcome"] == "authorization_started", (
            f"§1.0: expected a fresh authorization_started outcome, got {started_runtime}")
        verification_uri = started_runtime["verification_uri"]

        connect = Connect(page, recorder)
        connect.open(verification_uri)
        connect.approve()

        landing.open()
        assert "agent connected" in landing.agent_line_text().lower(), (
            f"§1.0: expected the landing to read 'Agent connected' once the device is approved, "
            f"got {landing.agent_line_text()!r}")

        # US2 acceptance scenario 1: within 30s, /v2/me (via the founder session) reads
        # agent.connected: true.
        session, keel_session = login_and_keel_session(stack, founder_credentials)
        deadline = time.monotonic() + 30
        connected = bool(keel_session.bound_agent_session_id)
        while not connected and time.monotonic() < deadline:
            me = session.get(f"http://localhost:{stack.cloud_port}/v2/me", timeout=10).json()
            connected = bool((me.get("agent") or {}).get("connected"))
            if not connected:
                time.sleep(1)
        with recorder.step("wire: GET /v2/me reads agent.connected within 30s", party="stack", kind="assert") as h:
            h.record_assert(True, connected)
            assert connected, "US2 acceptance scenario 1: /v2/me never reported agent.connected"

        # ------------------------------------------------------------------- §1.1 Naming the idea
        landing.open()  # L1: the name field, now that an agent is connected
        landing.name_project(fixture.PROJECT_NAME)
        project_id = _project_id_from_url(page.url)

        chat = Chat(page, recorder)
        chat.send(fixture.PROBLEM_STATEMENT)
        chat.wait_for_state(r"reading|thinking|connected", timeout_ms=60_000)

        # The scripted PROBLEM_FRAME entry is NEEDS_INPUT first (keel-runtime spec 001 FR-003) --
        # the agent's one follow-up question, answered, before the statement lands verbatim.
        chat.wait_for_state(re.escape(fixture.PROBLEM_FOLLOWUP_QUESTION[:20]), timeout_ms=60_000)
        chat.send(fixture.PROBLEM_FOLLOWUP_ANSWER)

        chat.wait_for_understood(timeout_ms=60_000)
        understood = chat.understood_claim()
        with recorder.step("assert: C5 shows the script's statement verbatim (§1.1)", party="founder", kind="assert") as h:
            h.record_assert(fixture.PROBLEM_STATEMENT, understood)
            assert fixture.PROBLEM_STATEMENT in understood, (
                f"§1.1: expected C5's understood claim to be the script's statement verbatim, "
                f"got {understood!r}")
        chat.save_this()

        # US2 acceptance scenario 3: PROBLEM is still unframed on the wire until approval.
        overview_before_approve = session.get(
            f"http://localhost:{stack.cloud_port}/v2/projects/{project_id}/overview", timeout=10).json()
        problem_stage = next(s for s in overview_before_approve.get("stages", []) if s.get("stage") == "PROBLEM")
        with recorder.step("wire: PROBLEM is unframed before approval (§1.2, US2 scenario 3)",
                            party="stack", kind="assert") as h:
            h.record_assert("unframed-or-draft", problem_stage.get("framed"))
            assert not problem_stage.get("approved"), (
                "US2 acceptance scenario 3: PROBLEM already reads approved before any approval")

        # ------------------------------------------------------------------------- §1.2 The review
        stage_card = StageCard(page, recorder)
        stage_card.open("PROBLEM")
        assert "review" in stage_card.status_text().lower(), (
            f"§1.2: expected the problem card to read 'Reviewing', got {stage_card.status_text()!r}")
        stage_card.approve()

        overview_after_approve = session.get(
            f"http://localhost:{stack.cloud_port}/v2/projects/{project_id}/overview", timeout=10).json()
        problem_stage_after = next(s for s in overview_after_approve.get("stages", []) if s.get("stage") == "PROBLEM")
        with recorder.step("wire: PROBLEM reads framed+approved after approval (§1.2, US2 scenario 3)",
                            party="stack", kind="assert") as h:
            h.record_assert(True, problem_stage_after.get("approved"))
            assert problem_stage_after.get("approved"), (
                "US2 acceptance scenario 3: PROBLEM does not read approved after approval")
        stage_card.continue_to_next_step()

        # -------------------------------------------------------------- §1.1/§1.2 again: solution
        chat.send(fixture.SOLUTION_STATEMENT)
        chat.wait_for_understood(timeout_ms=60_000)
        solution_understood = chat.understood_claim()
        assert fixture.SOLUTION_STATEMENT in solution_understood, (
            f"§1.1: expected the solution's C5 to show the script's statement verbatim, "
            f"got {solution_understood!r}")

        # Mid-draft: click "The problem" in the nav -> S2 (approved card, "draft kept" note).
        shell = Shell(page)
        shell.open_stage_nav("The problem")
        draft_note = chat.draft_kept_note()
        with recorder.step("assert: S2 shows the draft-kept note for the in-progress step", party="founder", kind="assert") as h:
            h.record_assert(True, bool(draft_note))
            assert draft_note, "expected S2's draft-kept note while the solution step is mid-draft"
        chat.back_to_step()

        chat.save_this()
        stage_card.open("SOLUTION")
        stage_card.approve()
        stage_card.continue_to_next_step()

        # ------------------------------------------------------------ §1.1/§1.2 again: commercial
        chat.send(fixture.COMMERCIAL_STATEMENT)
        chat.wait_for_understood(timeout_ms=60_000)
        commercial_understood = chat.understood_claim()
        assert fixture.COMMERCIAL_STATEMENT in commercial_understood, (
            f"§1.1: expected the commercial's C5 to show the script's statement verbatim, "
            f"got {commercial_understood!r}")
        chat.save_this()
        stage_card.open("COMMERCIAL")
        stage_card.approve()

        # S4's three-part note: last card approved, People unlocks.
        stage_card.go_to_people()

        # -------------------------------------------------------------------------- §1.4 Inviting
        people = People(page, recorder)
        people.open()

        invite_urls: dict[str, str] = {}
        for participant in fixture.PARTICIPANTS:
            invite_urls[participant.name] = people.send_questions(
                participant.role_label, name=participant.name,
                about=f"{participant.name} can speak to this from where they sit.")

        people.toggle_who()
        rows = people.table_rows()
        with recorder.step("assert: the toggle's table lists all three, not opened (§1.4/§1.5)", party="founder", kind="assert") as h:
            h.record_assert(3, len(rows))
            assert len(rows) == len(fixture.PARTICIPANTS), (
                f"§1.4: expected {len(fixture.PARTICIPANTS)} rows in the who's-been-asked table, "
                f"got {len(rows)}")
            for row in rows:
                assert "not opened" in row["their_answer"].lower(), (
                    f"§1.5: expected {row['person']!r} to read 'Not opened' before any answer, "
                    f"got {row['their_answer']!r}")

        # ------------------------------------------------------------------- §2.1-§2.3 Answering
        for index, participant in enumerate(fixture.PARTICIPANTS):
            participant_context = browser.new_context()
            try:
                participant_page = participant_context.new_page()
                pb = ParticipantBrowser(participant_page, recorder)
                pb.open(invite_urls[participant.name])
                pb.start()
                answers = [
                    participant.problem_answer,
                    participant.solution_answer,
                    participant.commercial_answer,
                ]
                if index == 0:
                    # Spec US2 step 6: "skip one question" -- the first participant leaves one
                    # question blank; still a legal, non-empty submission.
                    pb.answer(answers + [None])
                else:
                    pb.answer(answers)
                pb.submit()
            finally:
                participant_context.close()

        # The founder's table now reads Answered; open P9 and read the words back verbatim.
        people.open()
        answers_popup = people.open_answers(fixture.PARTICIPANTS[0].name)
        with recorder.step("assert: P9 shows Dana's words verbatim (§1.6/§2.2)", party="founder", kind="assert") as h:
            joined = "\n".join(q["answer"] for q in answers_popup["questions"])
            h.record_assert(fixture.PARTICIPANTS[0].problem_answer, joined)
            assert fixture.PARTICIPANTS[0].problem_answer in joined, (
                f"§1.6: expected Dana's own words in P9, got {joined!r}")

        # -------------------------------------------------------------------------- §1.6 Reading
        people.have_agent_read()
        toast = people.toast_text()
        with recorder.step("assert: the toast names what moved (§1.6)", party="founder", kind="assert") as h:
            h.record_assert(True, len(toast.strip()) > 0)
            assert toast.strip(), "§1.6: expected the toast to name what moved after reading"
        people.see_the_overview()

        # ------------------------------------------------------------------------- §1.7 Standing
        stage_card.open("PROBLEM")
        assert fixture.PROBLEM_HEADLINE.lower() in stage_card.status_text().lower(), (
            f"§1.7: expected the problem card to read {fixture.PROBLEM_HEADLINE!r}, "
            f"got {stage_card.status_text()!r}")
        stage_card.open("SOLUTION")
        assert fixture.SOLUTION_HEADLINE.lower() in stage_card.status_text().lower(), (
            f"§1.7: expected the solution card to read {fixture.SOLUTION_HEADLINE!r}, "
            f"got {stage_card.status_text()!r}")
        stage_card.open("COMMERCIAL")
        assert fixture.COMMERCIAL_HEADLINE.lower() in stage_card.status_text().lower(), (
            f"§1.7: expected the commercial card to read {fixture.COMMERCIAL_HEADLINE!r}, "
            f"got {stage_card.status_text()!r}")

        # ------------------------------------------------------------------------- §1.7 Evidence
        stage_card.open("PROBLEM")
        stage_card.open_belief(fixture.PROBLEM_BELIEF_HOURS_NOT_MINUTES)
        quotes = stage_card.evidence_quotes(fixture.PROBLEM_BELIEF_HOURS_NOT_MINUTES)
        with recorder.step("assert: the problem belief shows counted-for/against reasons (§1.7)",
                            party="founder", kind="assert") as h:
            h.record_assert("for and against groups present", quotes)
            groups = {q["group"] for q in quotes}
            assert "for" in groups and "against" in groups, (
                f"§1.7: expected both a for and an against group on a 'People disagree' belief, "
                f"got groups={groups}")

        stage_card.open("COMMERCIAL")
        with recorder.step("assert: the commercial card is Not holding up, no reframe beneath (§1.7)",
                            party="founder", kind="assert") as h:
            h.record_assert(True, "not holding up" in stage_card.status_text().lower())
            assert "not holding up" in stage_card.status_text().lower()

        # US2 acceptance scenario 4: the standing read shows every applying belief exactly once,
        # each `line` equal to the same belief's `countsNote` on its own stage card.
        standing = session.get(
            f"http://localhost:{stack.cloud_port}/v2/projects/{project_id}/standing", timeout=10).json()
        all_lines = [
            entry.get("line") for bucket in standing.values() if isinstance(bucket, list)
            for entry in bucket if isinstance(entry, dict)
        ]
        with recorder.step("wire: the standing read's lines match the stage cards' countsNote (§1.7, US2 scenario 4)",
                            party="stack", kind="assert") as h:
            h.record_assert(fixture.COMMERCIAL_COUNTS_NOTE, all_lines)
            assert any(fixture.COMMERCIAL_COUNTS_NOTE in (line or "") for line in all_lines), (
                f"US2 acceptance scenario 4: expected the standing's own lines to include "
                f"{fixture.COMMERCIAL_COUNTS_NOTE!r}, got {all_lines}")

        # ---------------------------------------------------------------------------- §1.10 Brief
        shell.open_brief()
        brief = Brief(page, recorder)
        brief.open()
        headings = brief.list_headings()
        with recorder.step("assert: every belief appears in exactly one of the four lists (§1.10)",
                            party="founder", kind="assert") as h:
            h.record_assert(">=1 heading", headings)
            assert headings, "§1.10: expected at least one belief-status list on the brief"
        brief.download()
        who_was_asked = brief.who_was_asked()
        with recorder.step("assert: B2's document renders Who was asked (§1.10)", party="founder", kind="assert") as h:
            h.record_assert([p.name for p in fixture.PARTICIPANTS], who_was_asked)
            joined_who = "\n".join(who_was_asked)
            for participant in fixture.PARTICIPANTS:
                assert participant.name in joined_who, (
                    f"§1.10: expected {participant.name!r} in B2's Who was asked, got {who_was_asked}")

        passed = True
    finally:
        failed_step = recorder.failed_step
        context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s001-smoke", facts=fixture.facts(), passed=passed,
                     failed_step=failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
