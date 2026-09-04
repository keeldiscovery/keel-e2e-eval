"""Prelude helpers shared between scenarios (spec 006-agent-optional FR-004).

`walk_stage` is moved here, verbatim in behavior, out of `evals/test_s001_smoke.py` -- both S-001
and S-002 drive the identical guided-step walk (C1-C8 -> R1 -> approve -> R4), and keeping it in
one place means the two scenarios cannot quietly drift apart on what "approve a stage" means.
S-001 imports it from here now; it used to be a local closure of its own test function.

`approved_project_with_one_read` is S-002's own prelude (spec's edge case: "it runs after S-001 in
the same stack session where possible; otherwise it builds its own prelude by driving S-001's
first two steps with the runtime up. The prelude is a helper, not a second copy of S-001."):
builds a project approved through every stage (People does not unlock on less -- keel-web's
`SideNav.tsx` own `gateOpen` needs every stage approved, not just the problem card), with the
payroll-manager role invited once and that participant's own answer already read -- the
pre-logout state spec 006's own US1 scenario opens from. Only used when S-002 cannot simply reuse
an already-run S-001's own project in the same stack session.
"""

from __future__ import annotations

from typing import Callable

from playwright.sync_api import Page

from evals import payroll_exceptions as fx
from harness.browser import Chat, Landing, ParticipantBrowser, People, StageCard
from harness.steps import Recorder

GetJson = Callable[[str], dict]


def stage_from_overview(overview_body: dict, stage_type: str) -> dict:
    return next(s for s in overview_body["stages"] if s["type"] == stage_type)


def walk_stage(page: Page, recorder: Recorder, get_json: GetJson, project_id: str, stage_type: str,
               opening: str, statement: str, *, needs_followup: bool) -> None:
    """One pass of C1-C8 -> R1 -> approve -> R4, for whichever stage is currently the guided
    step's own live draft. `get_json` is the caller's own `GET {cloud_base}{path}` (a plain
    function so this module never has to know which browser context or cloud port it's driving
    against)."""
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
        before = stage_from_overview(get_json(f"/v2/projects/{project_id}/overview"), stage_type)
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
        after = stage_from_overview(get_json(f"/v2/projects/{project_id}/overview"), stage_type)
        h.record_assert({"framed": True, "approved": True}, after)
        assert after["framed"] is True and after["approved"] is True, (
            f"US2 acceptance scenario 3: expected {stage_type} framed+approved, got {after}")


def approved_project_with_one_read(
    page: Page, recorder: Recorder, browser, *, web_base: str, cloud_base: str,
    project_name: str = fx.PROJECT_NAME,
) -> tuple[str, dict[str, str]]:
    """Builds a project approved through every stage, with the payroll-manager role (Dana Okafor)
    invited once and her own answer already read by the agent -- the pre-logout state spec 006's
    own US1 scenario opens from ("continuing from a project that already exists and has been
    approved through at least the problem card, with invitations already sent and at least one
    answer already read").

    Assumes the founder is already logged in, on the landing, with the agent already connected
    (the caller drives arrival/connect itself -- this is the "S-001's first two steps" the spec's
    edge case names, not a third copy of them).

    Returns `(project_id, invite_urls)` -- `invite_urls` names only the one participant this
    prelude invited (Dana Okafor), so a caller that wants a second, still-unread invitation of its
    own (US1 step 4) invites a genuinely different person rather than re-deriving role labels.
    """
    context = page.context

    def get_json(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=10_000).json()

    landing = Landing(page, recorder, web_base)
    project_id = landing.name_project(project_name)

    walk_stage(
        page, recorder, get_json, project_id, "PROBLEM",
        "Payroll managers keep losing time every month chasing down payroll exceptions.",
        fx.PROBLEM_STATEMENT, needs_followup=True,
    )
    # Live-confirmed (S-001, run 20260903T220650Z): approval opens the next stage's own draft,
    # which makes the approved card read-only, so the "Continue to step 3" link never renders
    # there -- `continue_to_next_step` goes where that link would have gone (the overview, which
    # mounts the next stage's chat) when it is absent.
    StageCard(page, recorder).continue_to_next_step()

    solution_chat = Chat(page, recorder)
    solution_chat.send(
        "An exceptions queue inside the payroll tool that assigns an owner to every exception.")
    solution_chat.wait_for_agent_turn(timeout_s=60)
    solution_chat.save_confirmation()
    solution_chat.wait_for_review(project_id, "SOLUTION", timeout_s=60)
    solution_card = StageCard(page, recorder)
    solution_card.open(project_id, "SOLUTION")
    solution_card.approve()
    solution_card.continue_to_next_step()

    walk_stage(
        page, recorder, get_json, project_id, "COMMERCIAL",
        "$30 a seat per month, billed annually upfront.", fx.COMMERCIAL_STATEMENT,
        needs_followup=False,
    )
    StageCard(page, recorder).go_to_people()

    people = People(page, recorder)
    people.open(project_id)
    participant = fx.PARTICIPANTS[0]  # Dana Okafor, "A payroll manager"
    people.open_send_popup(participant.role_label)
    people.fill_who(participant.name, about=f"{participant.role_label} at a 400-person company.")
    people.go_to_preview()
    invite_url = people.generate_link(participant.name.split()[0])
    people.close_popup()

    participant_context = browser.new_context()
    try:
        participant_page = participant_context.new_page()
        pb = ParticipantBrowser(participant_page, recorder)
        pb.open(invite_url)
        pb.start()
        pb.answer(participant.answer_texts())
        pb.submit()
    finally:
        participant_context.close()

    people.switch_to_who_tab()
    people.read_all_and_wait(timeout_s=60)

    return project_id, {participant.name: invite_url}
