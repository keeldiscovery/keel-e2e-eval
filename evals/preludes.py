"""Prelude helpers shared between scenarios (spec 006-agent-optional FR-004; spec 010 T026).

Three things live here, and they are here because more than one scenario drives them and two
copies of "approve a stage" is how two scenarios quietly stop meaning the same thing:

- `create_project` -- name, market, start. The market step sits between naming and starting now
  (spec 013, design §3.8), so `POST /v2/projects` carries `{name, market}` and the project id
  comes back from `MarketStep.start()`, not from naming.
- `walk_stage` -- one pass of the guided walk: send the claim, read the confirmation card, save,
  wait for the review, approve.
- `run_corpus_scenario` -- **the whole body of S-005, S-006 and S-007** (FR-015): the three
  scenario modules differ by an entry id and nothing else. It lives in `evals/` rather than
  `harness/` deliberately: it is a scenario, not machinery, and it asserts.

`approved_project_with_one_read` is S-002's own prelude and is unchanged in purpose.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Callable

from playwright.sync_api import Page

from evals import corpus_facts
from harness import corpus_script
from harness.browser import (WAIT_PHASES, Chat, Landing, MarketStep, Overview, ParticipantPage,
                              People, ReviewCard)
from harness.steps import Recorder

GetJson = Callable[[str], dict]


def stage_from_overview(overview_body: dict, stage_type: str) -> dict:
    return next(s for s in overview_body["stages"] if s["type"] == stage_type)


def create_project(page: Page, recorder: Recorder, web_base: str,
                   founder: corpus_script.FounderInputs) -> str:
    """Name -> market -> start. Returns the new project id.

    The market's `language` is never typed: `CreateProjectRequest.market` carries only
    `{country, region}` and the server derives the rest (vendored fact V7). A `region` of `None`
    leaves the box empty -- never the word "null" (spec edge case).
    """
    landing = Landing(page, recorder, web_base)
    landing.visit()
    if page.locator(".guided-step").count() == 0:
        landing.start_new_project()
    landing.name_project(founder.project_name)
    market = MarketStep(page, recorder, web_base)
    market.fill(founder.market.country, founder.market.region)
    return market.start()


def walk_stage(page: Page, recorder: Recorder, get_json: GetJson, project_id: str, stage_type: str,
               opening: str, statement: str, *, needs_followup: bool = False,
               approve: bool = True) -> ReviewCard:
    """One pass of the guided walk for whichever stage is the live draft, ending on an approved
    card. `get_json` is the caller's own `GET {cloud_base}{path}`.

    `needs_followup` survives as a keyword and is now always false in practice: a generated script
    carries no `NEEDS_INPUT` entry, because an assumption screen may only ask when the statement
    is missing (keel-cloud decision 14) and the corpus always has one. The founder's one piece of
    mid-walk free text is the **correction turn at the review card**, which S-001 walks separately.
    """
    chat = Chat(page, recorder)
    chat.send(opening)
    turn = chat.wait_for_agent_turn(timeout_s=90)
    with recorder.step(f"§4.2: while the agent answers on {stage_type}, the chat narrates a phase "
                        "and counts the seconds", party="founder", kind="assert") as h:
        h.record_assert({"phase": "one of WAIT_PHASES", "elapsed": "<n> s"},
                         {"phase": turn.get("phase_line"), "elapsed": turn.get("elapsed_label")})
        assert turn.get("phase_line") in WAIT_PHASES, (
            f"expected the chat to narrate a waiting phase on {stage_type}, "
            f"saw {turn.get('phase_line')!r}")
        assert re.fullmatch(r"\d+ s", turn.get("elapsed_label") or ""), (
            f"expected the seconds counter beside the topic, saw {turn.get('elapsed_label')!r}")

    with recorder.step(f"§1.1: {stage_type}'s understood claim matches the script verbatim",
                        party="founder", kind="assert") as h:
        card = chat.confirmation_card()
        h.record_assert(statement, card)
        assert card is not None, f"expected the confirmation card to render for {stage_type}"
        assert card["claim"] == statement, (
            f"expected the {stage_type} claim verbatim, got {card['claim']!r}")
    chat.save_confirmation()
    landed = chat.wait_for_review(project_id, stage_type, timeout_s=90)
    with recorder.step(f"§4.4: the truth card kept the founder company on {stage_type}, and the "
                        "review opened itself", party="founder", kind="assert") as h:
        h.record_assert({"phase": "one of WAIT_PHASES", "truth": "non-empty"}, landed)
        assert landed["phase_line"] in WAIT_PHASES, (
            f"expected the rail to narrate a waiting phase, saw {landed['phase_line']!r}")
        assert landed.get("truth_seen"), (
            f"expected one truth at a time beneath the rail while waiting, "
            f"saw {landed.get('truth_seen')!r}")

    with recorder.step(f"§1.2 wire: {stage_type} is still unframed before approval",
                        party="stack", kind="assert") as h:
        before = stage_from_overview(get_json(f"/v2/projects/{project_id}/overview"), stage_type)
        h.record_assert({"framed": False}, before)
        assert before["framed"] is False, (
            f"expected {stage_type} still a draft before approval, got {before}")

    card = ReviewCard(page, recorder, _base_of(page))
    opened = card.open(project_id, stage_type)
    with recorder.step(f"§1.2: the {stage_type} card reads Reviewing",
                        party="founder", kind="assert") as h:
        h.record_assert("Reviewing", opened["status"])
        assert "review" in opened["status"].lower(), (
            f"expected Reviewing on {stage_type}, got {opened['status']!r}")
    if not approve:
        # The caller has something to do at the unapproved card first -- S-001's own correction
        # turn (FR-008). It approves when it is done.
        return card
    card.approve()

    with recorder.step(f"§1.2 wire: {stage_type} is framed and approved after approval",
                        party="stack", kind="assert") as h:
        after = stage_from_overview(get_json(f"/v2/projects/{project_id}/overview"), stage_type)
        h.record_assert({"framed": True, "approved": True}, after)
        assert after["framed"] is True and after["approved"] is True, (
            f"expected {stage_type} framed+approved, got {after}")
    return card


def _base_of(page: Page) -> str:
    from urllib.parse import urlsplit
    parts = urlsplit(page.url)
    return f"{parts.scheme}://{parts.netloc}"


# ------------------------------------------------------------- inviting and answering a whole entry

def invite_everyone(page: Page, recorder: Recorder, project_id: str, entry,
                    people_inputs: list[corpus_script.PersonInputs],
                    web_base: str) -> dict[str, str]:
    """One invitation per person, each sent to their own role's card. Returns
    `{person name: invite url}` in the entry's own `answers` order -- which is the order the
    scripted executor consumes its `INTERPRET` entries in, so it is the order the run must read
    people in too (contract rule 2)."""
    people = People(page, recorder, web_base)
    people.open(project_id)
    labels = {role["id"]: role["label"] for role in entry.roles or []}
    urls: dict[str, str] = {}
    for person in people_inputs:
        if page.locator(".role").count() == 0:
            people.switch_to_kinds_tab()
        label = labels[person.role_id]
        people.open_send_popup(label)
        people.fill_who(person.person, about=f"{label}, asked about one real occasion.")
        people.go_to_preview()
        urls[person.person] = people.generate_link(person.person.split()[0])
        people.close_popup()
    return urls


def answer_everyone(browser, recorder: Recorder, entry,
                    people_inputs: list[corpus_script.PersonInputs],
                    urls: dict[str, str]) -> list[dict[str, Any]]:
    """Each person, in their own isolated browser context -- no session with the founder, which is
    the whole point of a link a stranger can open."""
    typed: list[dict[str, Any]] = []
    for person in people_inputs:
        context = browser.new_context()
        try:
            page = context.new_page()
            participant = ParticipantPage(page, recorder)
            participant.open(urls[person.person])
            result = participant.answer_as(person, entry)
            participant.submit()
            typed.append({"person": person.person, **result})
        finally:
            context.close()
    return typed


# --------------------------------------------------------------------------- S-002's own prelude

def approved_project_with_one_read(
    page: Page, recorder: Recorder, browser, *, web_base: str, cloud_base: str,
    project_name: str | None = None,
) -> tuple[str, dict[str, str]]:
    """Builds a project approved through every stage, with the first role's first person invited
    and their answer already read -- the pre-logout state spec 006's US1 opens from.

    Rewritten for measured beliefs: the fixture is `evals/payroll_exceptions.yaml`, driven through
    the same generator every other scenario uses.
    """
    from evals import payroll_exceptions as fx
    from harness.browser import StageCard

    entry = fx.entry()
    founder = fx.founder()
    context = page.context

    def get_json(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=10_000).json()

    project_id = create_project(page, recorder, web_base, founder)
    for stage, opening in (("PROBLEM", founder.problem), ("SOLUTION", founder.solution),
                            ("COMMERCIAL", founder.commercial)):
        walk_stage(page, recorder, get_json, project_id, stage, opening,
                   founder.statement(stage))
        ReviewCard(page, recorder, web_base).continue_onward()

    people_inputs = fx.people()
    urls = invite_everyone(page, recorder, project_id, entry, people_inputs[:1], web_base)
    answer_everyone(browser, recorder, entry, people_inputs[:1], urls)

    people = People(page, recorder, web_base)
    people.open(project_id)
    people.switch_to_who_tab()
    people.read_all_and_wait(timeout_s=90)
    return project_id, urls
