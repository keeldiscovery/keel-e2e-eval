"""S-001, the smoke (spec 005-connect-stack FR-013): keel-cloud `canon/journeys.md` §3 (the
2026-09-03 connect-stack amendment) walked once, end to end, deterministically, against the real
four applications -- Postgres, keel-cloud, keel-web, and keel-runtime started through
keel-connect-skill's own script. No Prism, no LLM: keel-runtime answers every inference job from
its bundled, scripted payroll-exceptions journey (`../keel-runtime/keel_runtime/testing/scripts/
payroll-exceptions.json`), mirrored in `evals/payroll_exceptions.py`.

Journey coverage (CANON.md's ledger, `canon/journeys.md` §3, 2026-09-03): this is the one module
proving §1.0 (arrival: login, connect by device code, gated landing), §1.1 (the idea becomes three
bets), §1.2 (review before spend), §1.4 (approve every framed card, then invite), §1.5 (waiting --
the UI counts, never interprets), §1.6 (reading what came back), §1.7 (where it stands), §1.10
(the brief as a derived standing), §2.1 (the stranger's four honest lines, consent by starting),
§2.2 (answering; every question skippable), §2.3 (thanks, no promises the product can't keep).
§1.3, §1.8, §1.9, §2.4 are WAIVED in keel-cloud `canon/CANON.md` §5 -- deferred by the founder, or
not on this smoke's path.

Wire assertions (US2 acceptance scenarios 1, 3, 4) go through the founder browser context's own
`request` object -- it shares the same cookie jar as the page, so a plain `GET` reaches the same
founder session the UI is driving, no second login needed.
"""

from __future__ import annotations

import time

from evals import payroll_exceptions as fx
from harness.browser import Auth, Brief, Chat, Connect, Landing, ParticipantBrowser, People, Shell, StageCard
from harness.connect import start_runtime_via_skill
from harness.evidence import finalize_run
from harness.steps import Recorder


_STANDING_LISTS = ("holdingUp", "notHoldingUp", "peopleDisagree", "untested")


def _stage(overview_body: dict, stage_type: str) -> dict:
    return next(s for s in overview_body["stages"] if s["type"] == stage_type)


def _counts_note_for(stage_card_body: dict, heading: str) -> str | None:
    """`FounderDtos.Belief.countsNote` for the belief headed `heading`, off `GET .../stages/{stage}`."""
    for group in stage_card_body.get("groups", []):
        for belief in group.get("loadBearing", []) + group.get("supporting", []):
            if belief.get("heading") == heading:
                return belief.get("countsNote")
    return None


def test_s001_smoke(stack, founder_credentials, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=10_000).json()

    def _walk_stage(project_id: str, stage_type: str, opening: str, statement: str,
                     *, needs_followup: bool) -> None:
        """One pass of C1-C8 -> R1 -> approve -> R4, for whichever stage is currently the guided
        step's own live draft."""
        chat = Chat(page, recorder)
        chat.send(opening)
        turn = chat.wait_for_agent_turn(timeout_s=60)
        if needs_followup:
            with recorder.step(f"§1.1: the agent's follow-up question on {stage_type}",
                                party="agent", kind="assert") as h:
                h.record_assert(fx.PROBLEM_FOLLOWUP_QUESTION, turn["agent_reply"])
                assert fx.PROBLEM_FOLLOWUP_QUESTION in turn["agent_reply"], (
                    f"expected the scripted follow-up question on {stage_type}, got {turn!r}")
            chat.send(fx.PROBLEM_FOLLOWUP_ANSWER)
            turn = chat.wait_for_agent_turn(timeout_s=60)

        with recorder.step(f"§1.1: {stage_type}'s understood claim matches the script verbatim",
                            party="founder", kind="assert") as h:
            card = chat.confirmation_card()
            h.record_assert(statement, card)
            assert card is not None, f"expected C5's confirmation card to render for {stage_type}"
            assert card["claim"] == statement, (
                f"expected the {stage_type} claim verbatim, got {card['claim']!r}")
        chat.save_confirmation()
        chat.wait_for_review(project_id, stage_type, timeout_s=60)

        with recorder.step(f"§1.2 wire: {stage_type} is still unframed before approval",
                            party="stack", kind="assert") as h:
            before = _stage(_get(f"/v2/projects/{project_id}/overview"), stage_type)
            h.record_assert({"framed": False}, before)
            assert before["framed"] is False, (
                f"US2 acceptance scenario 3: expected {stage_type} still a draft, got {before}")

        stage_card = StageCard(page, recorder)
        opened = stage_card.open(project_id, stage_type)
        with recorder.step(f"§1.2: the {stage_type} card reads Reviewing",
                            party="founder", kind="assert") as h:
            h.record_assert("reviewing", opened["status"])
            assert "review" in opened["status"].lower(), (
                f"expected Reviewing on {stage_type}, got {opened['status']!r}")
        stage_card.approve()

        with recorder.step(f"§1.2 wire: {stage_type} is framed and approved after approval",
                            party="stack", kind="assert") as h:
            after = _stage(_get(f"/v2/projects/{project_id}/overview"), stage_type)
            h.record_assert({"framed": True, "approved": True}, after)
            assert after["framed"] is True and after["approved"] is True, (
                f"US2 acceptance scenario 3: expected {stage_type} framed+approved, got {after}")

    try:
        page = context.new_page()

        # -------------------------------------------------------------------------------- §1.0
        Auth(page, recorder, web_base).log_in(
            email=founder_credentials.email, password=founder_credentials.password)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()
        with recorder.step("§1.0: landing reads no agent connected and is gated",
                            party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            gated = landing.is_gated()
            h.record_assert({"gated": True, "agent_connected": False},
                             {"gated": gated, "agent_connected": arrival["agent_connected"]})
            assert gated, f"expected the landing gated before any agent connects (frame {arrival['frame']})"
            assert not arrival["agent_connected"], f"expected no agent connected yet, got {agent_line!r}"
            assert "no agent" in agent_line.lower() or "not connected" in agent_line.lower(), (
                f"expected 'No agent connected' on the landing, got {agent_line!r}")

        with recorder.step("§1.0: keel-connect-skill starts the runtime", party="stack", kind="assert") as h:
            result = start_runtime_via_skill(stack, recorder)
            h.record_assert("authorization_started", result.get("outcome"))
            assert result["outcome"] == "authorization_started", (
                f"expected a freshly-reset runtime home to need device approval, got {result}")
        verification_uri = result["verification_uri"]

        connect = Connect(page, recorder)
        frame = connect.open(verification_uri)
        with recorder.step("§1.0: the verification URI opens frame B", party="founder", kind="assert") as h:
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()

        landing.visit()
        with recorder.step("§1.0: landing reads agent connected", party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            h.record_assert("agent connected", agent_line)
            assert "agent connected" in agent_line.lower(), (
                f"expected 'Agent connected' on the landing, got {agent_line!r}")

        # US2 acceptance scenario 1: within 30s, /v2/me reads agent.connected: true (already true
        # by now -- `Connect.wait_for_connected` just proved it on the screen; this is the wire
        # half of the same acceptance scenario).
        with recorder.step("§1.0 wire: GET /v2/me reads agent.connected within 30s",
                            party="stack", kind="assert") as h:
            # `approvedAt` lands the instant the founder clicks Approve; `connected` also needs
            # the runtime's own next heartbeat/poll cycle to land (keel-runtime's long-poll
            # window), so a brief gap between the screen's own optimistic "Agent connected" and
            # the wire agreeing is expected -- poll up to the acceptance scenario's own 30s.
            deadline = time.monotonic() + 30
            me = _get("/v2/me")
            connected = bool((me.get("agent") or {}).get("connected"))
            while not connected and time.monotonic() < deadline:
                page.wait_for_timeout(1_000)
                me = _get("/v2/me")
                connected = bool((me.get("agent") or {}).get("connected"))
            h.record_assert(True, connected)
            assert connected, f"US2 acceptance scenario 1: /v2/me never reported agent.connected: {me}"

        # -------------------------------------------------------------------------------- §1.1
        project_id = landing.name_project(fx.PROJECT_NAME)

        _walk_stage(
            project_id, "PROBLEM",
            "Payroll managers keep losing time every month chasing down payroll exceptions.",
            fx.PROBLEM_STATEMENT, needs_followup=True,
        )
        # R4 -> step 3. Live-confirmed (run 20260903T220650Z): approval opens the next stage's
        # own draft, which makes the approved card read-only, so the "Continue to step 3" link
        # never renders there -- `continue_to_next_step` goes where that link goes (the
        # overview, which mounts the next stage's chat).
        StageCard(page, recorder).continue_to_next_step()

        # §1.1 (again): during the solution draft, the mockup of record's "S2" -- clicking The
        # problem in the nav shows the approved card, draft kept.
        solution_chat = Chat(page, recorder)
        solution_chat.send(
            "An exceptions queue inside the payroll tool that assigns an owner to every exception.")
        solution_chat.wait_for_agent_turn(timeout_s=60)
        with recorder.step("§1.1: the solution draft is kept while viewing the approved problem card",
                            party="founder", kind="assert") as h:
            Shell(page, recorder).click_stage_link("PROBLEM")
            note = solution_chat.draft_kept_note()
            h.record_assert("draft kept, names step 3", note)
            assert note, "expected a draft-kept note while the solution step is mid-draft"
        solution_chat.back_to_step()
        with recorder.step("§1.1: solution's understood claim matches the script verbatim",
                            party="founder", kind="assert") as h:
            card = solution_chat.confirmation_card()
            h.record_assert(fx.SOLUTION_STATEMENT, card)
            assert card is not None and card["claim"] == fx.SOLUTION_STATEMENT, (
                f"expected the solution claim verbatim, got {card!r}")
        solution_chat.save_confirmation()
        solution_chat.wait_for_review(project_id, "SOLUTION", timeout_s=60)

        with recorder.step("§1.2 wire: SOLUTION is still unframed before approval",
                            party="stack", kind="assert") as h:
            before = _stage(_get(f"/v2/projects/{project_id}/overview"), "SOLUTION")
            h.record_assert({"framed": False}, before)
            assert before["framed"] is False
        solution_card = StageCard(page, recorder)
        solution_card.open(project_id, "SOLUTION")
        solution_card.approve()
        with recorder.step("§1.2 wire: SOLUTION is framed and approved after approval",
                            party="stack", kind="assert") as h:
            after = _stage(_get(f"/v2/projects/{project_id}/overview"), "SOLUTION")
            h.record_assert({"framed": True, "approved": True}, after)
            assert after["framed"] is True and after["approved"] is True
        solution_card.continue_to_next_step()  # see the PROBLEM note above

        _walk_stage(project_id, "COMMERCIAL",
                    "$30 a seat per month, billed annually upfront.", fx.COMMERCIAL_STATEMENT,
                    needs_followup=False)
        # S4: the last card approved -- People unlocks (journeys §1.4, the three-section
        # navigation amendment) and the closing note's own *Go to People →* is the onward door.
        # DRIFT #16 (resolved, keel-web `6912f7e`): the note used to never render at all, so this
        # used to route through the side nav instead; both checks stand now -- the unlock, and
        # the note's own button actually working.
        shell = Shell(page, recorder)
        with recorder.step("§1.4: People unlocks once every framed card is approved",
                            party="founder", kind="assert") as h:
            locked = shell.people_locked()
            h.record_assert({"people_locked": False}, {"people_locked": locked,
                                                        "why": shell.people_locked_reason()})
            assert not locked, "expected the side nav's People entry to unlock after the last approval"
        StageCard(page, recorder).go_to_people()

        # -------------------------------------------------------------------------------- §1.4
        people = People(page, recorder)
        people.open(project_id)
        with recorder.step("§1.4: People opens on one card per role", party="founder", kind="assert") as h:
            labels = " | ".join(card["label"] for card in people.role_cards())
            h.record_assert([fx.PAYROLL_MANAGER_ROLE, fx.PAYROLL_TEAM_LEAD_ROLE], labels)
            assert fx.PAYROLL_MANAGER_ROLE in labels, f"expected the payroll manager role card, got {labels!r}"
            assert fx.PAYROLL_TEAM_LEAD_ROLE in labels, f"expected the team-lead role card, got {labels!r}"

        invite_urls: dict[str, str] = {}
        for participant in fx.PARTICIPANTS:
            # §1.4: from the first invitation the page has two views behind a toggle -- after
            # a link is generated it shows *Who's been asked* (live-confirmed, run
            # 20260904T013357Z), so every later send starts from *Kinds of people*.
            if page.locator(".role").count() == 0:
                people.switch_to_kinds_tab()
            people.open_send_popup(participant.role_label)
            people.fill_who(participant.name, about=f"{participant.role_label} at a 400-person company.")
            people.go_to_preview()
            invite_urls[participant.name] = people.generate_link(participant.name.split()[0])
            people.close_popup()

        people.switch_to_who_tab()
        with recorder.step("§1.4/§1.5: the table lists all three, not opened",
                            party="founder", kind="assert") as h:
            rows = people.table_rows()
            h.record_assert(len(fx.PARTICIPANTS), len(rows))
            assert len(rows) == len(fx.PARTICIPANTS), f"expected {len(fx.PARTICIPANTS)} rows, got {rows}"
            for row in rows:
                assert "not opened" in row["their_answer"].lower(), (
                    f"§1.5: expected {row['person']!r} to read 'Not opened', got {row['their_answer']!r}")

        # -------------------------------------------------------------------------------- §2.1-3
        for participant in fx.PARTICIPANTS:
            participant_context = browser.new_context()
            try:
                participant_page = participant_context.new_page()
                pb = ParticipantBrowser(participant_page, recorder)
                pb.open(invite_urls[participant.name])
                pb.start()
                pb.answer(participant.answer_texts())
                pb.submit()
            finally:
                participant_context.close()

        # The founder's table now reads Answered; open P9 for each person and read their own
        # words back verbatim (§1.6: "the founder can see any answer in the person's own words at
        # any time; seeing changes nothing") -- every participant, so each one's typed answers
        # reach FID's `participant_page` hop on the founder's own screen, not only Dana's.
        people.open(project_id)
        for participant in fx.PARTICIPANTS:
            first_name = participant.name.split()[0]
            people.open_answers_popup(first_name)
            answers = people.answers_popup_text()
            with recorder.step(f"§1.6/§2.2: P9 shows {first_name}'s own words verbatim",
                                party="founder", kind="assert") as h:
                joined = "\n".join(row["answer"] for row in answers["qa"])
                missing = [text for text in participant.answers.values() if text not in joined]
                h.record_assert(list(participant.answers.values()), joined)
                assert not missing, f"expected {first_name}'s own words in P9, missing {missing}"
            people.close_answers_popup()

        # -------------------------------------------------------------------------------- §1.6
        read_result = people.read_all_and_wait(timeout_s=60)
        with recorder.step("§1.6: the toast names what moved", party="founder", kind="assert") as h:
            h.record_assert("non-empty toast", read_result["toast_text"])
            assert read_result["toast_text"].strip(), (
                "expected a non-empty toast after the agent read the new answers")
        people.follow_toast_link()

        # -------------------------------------------------------------------------------- §1.7
        with recorder.interaction("ui_visit"):
            with recorder.step("§1.7: the overview shows the three cards' standing",
                                party="founder", kind="assert") as h:
                h.capture_text("screen", "overview")
                body_text = page.locator("body").inner_text()
                h.capture_text("stage_screen", body_text)
                shot = recorder.next_screenshot_name("overview-standing")
                page.screenshot(path=str(recorder.screenshot_path(shot)), full_page=True)
                h.add_screenshot(shot)
                h.record_assert(
                    [fx.PROBLEM_HEADLINE, fx.SOLUTION_HEADLINE, fx.COMMERCIAL_HEADLINE], body_text)
                for headline in (fx.PROBLEM_HEADLINE, fx.SOLUTION_HEADLINE, fx.COMMERCIAL_HEADLINE):
                    assert headline in body_text, f"expected {headline!r} on the overview"

        problem_evidence = StageCard(page, recorder)
        problem_evidence.open(project_id, "PROBLEM")
        # The belief whose verdict matches the card's own status (here the MIXED one) renders
        # open by default (`StageRoute.tsx`'s firstMatchingVerdictId) -- expand only if it
        # didn't, since `.b-top` toggles and a second click would collapse it.
        split_row = page.locator(".belief", has_text=fx.PROBLEM_BELIEF_HOURS_NOT_MINUTES).first
        if split_row.locator(".b-top").first.get_attribute("aria-expanded") != "true":
            problem_evidence.expand_belief(fx.PROBLEM_BELIEF_HOURS_NOT_MINUTES)
        with recorder.step("§1.7: the split belief shows counted-for and counted-against quotes",
                            party="founder", kind="assert") as h:
            drill = problem_evidence.drilldown(fx.PROBLEM_BELIEF_HOURS_NOT_MINUTES)
            h.record_assert({"for": ">=1", "against": ">=1"}, drill)
            assert drill["for"] and drill["against"], f"expected both sides quoted, got {drill}"

        commercial_evidence = StageCard(page, recorder)
        commercial_evidence.open(project_id, "COMMERCIAL")
        with recorder.step("§1.7: the price card reads Not holding up", party="founder", kind="assert") as h:
            status = commercial_evidence.status_word()
            h.record_assert(fx.COMMERCIAL_HEADLINE, status)
            assert fx.COMMERCIAL_HEADLINE.lower() in status.lower(), (
                f"expected {fx.COMMERCIAL_HEADLINE!r} on the price card, got {status!r}")

        # US2 acceptance scenario 4: every applying belief in exactly one standing list, and each
        # `line` equal to the same belief's `countsNote` on its own stage card.
        with recorder.step("§1.7 wire: the standing lists every belief exactly once",
                            party="stack", kind="assert") as h:
            standing = _get(f"/v2/projects/{project_id}/standing")
            all_lines = [line for name in _STANDING_LISTS for line in standing.get(name, [])]
            seen: dict[str, int] = {}
            for line in all_lines:
                seen[line["heading"]] = seen.get(line["heading"], 0) + 1
            duplicated = {heading: n for heading, n in seen.items() if n != 1}
            h.record_assert({"lists": list(_STANDING_LISTS), "duplicated": {}},
                             {"headings": sorted(seen), "duplicated": duplicated})
            assert all_lines, "expected a non-empty standing read"
            assert not duplicated, f"expected every belief exactly once across the standing lists: {duplicated}"

        with recorder.step("§1.7 wire: each standing line equals its belief's own countsNote",
                            party="stack", kind="assert") as h:
            mismatches = []
            for stage_type, heading in (
                ("PROBLEM", fx.PROBLEM_BELIEF_HOURS_NOT_MINUTES),
                ("SOLUTION", fx.SOLUTION_BELIEF_NOWHERE_TO_LIVE),
                ("COMMERCIAL", fx.COMMERCIAL_BELIEF_ANNUALLY_UPFRONT),
            ):
                counts_note = _counts_note_for(_get(f"/v2/projects/{project_id}/stages/{stage_type}"), heading)
                line = next((line for line in all_lines if line["heading"] == heading), None)
                if line is None or line["line"] != counts_note:
                    mismatches.append({"heading": heading, "line": line, "countsNote": counts_note})
            h.record_assert([], mismatches)
            assert not mismatches, f"standing lines disagree with the stage cards' countsNote: {mismatches}"

        # ---------------------------------------------------------------------------------§1.10
        Shell(page, recorder).open_brief()
        brief = Brief(page, recorder)
        brief.open(project_id)
        with recorder.step("§1.10: the brief lists every belief by verdict",
                            party="founder", kind="assert") as h:
            headings = brief.list_headings()
            h.record_assert(">=1 heading", headings)
            assert headings, "expected at least one belief-status list on the brief"
        brief.view_print()
        who = brief.who_was_asked()
        with recorder.step("§1.10: the print view names who was asked", party="founder", kind="assert") as h:
            joined = " | ".join(who)
            h.record_assert([p.name for p in fx.PARTICIPANTS], joined)
            for participant in fx.PARTICIPANTS:
                assert participant.name in joined, f"expected {participant.name!r} in Who was asked: {who}"

        passed = True
    finally:
        context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s001-smoke", facts=fx.facts(), passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
