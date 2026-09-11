"""S-012 -- the journey through a host (specs `016-copilot-e2e`, `019-journey-through-a-host`
and `021-short-journey`).

**Live**, opt-in through `make eval-live K=s012`, never part of `make eval`/`make eval-all`, and it
spends the founder's own money on whichever host it is pointed at.

**One scenario, two hosts.** `KEEL_JOURNEY_HOST` (set by `make eval-live K=s012 HOST=claude|copilot`,
default `copilot` so the command that produced the spec 016 run of record still means what it
meant) decides which. keel-cloud `canon/designs/e2e-matrix-design.md` §5.1 is why: the matrix's
three axes are an OS, a Python and a **host**, and *"the scenario each cell runs is S-001, the
founder's journey, through the host"*. A scenario that existed for one host could only ever fill a
third of the grid.

What differs between the two hosts is a handful of flags, one environment variable and the way
each CLI prints what it knows -- all of it behind `harness/agent_host.py`. What does not differ is
everything below: the same legs, in the same order, asserting the same shapes, on the same wire.

Two legs, one runtime, and the runtime is what joins them.

**Leg one, the host.** keel-connect-skill's plugin is installed into a **fresh host home**
(`CLAUDE_CONFIG_DIR` / `COPILOT_HOME`) from the real public marketplace with that host's own two
commands, the CLI is asked whether it can see `keel-connect` and whether it came from the plugin,
and then the founder's three words -- *"keel connect"* -- are said to `claude -p` / `copilot -p`.
Everything after that is asserted against the **runtime's own artefacts**, never the host's prose:
the heartbeat file in state `awaiting_approval`, the launch log's `KEEL_USER_CODE=` and
`KEEL_VERIFICATION_URI=` lines, and the eval cloud's own answer to
`GET /v2/device-authorizations?user_code=`. A host that said *"Keel is connected!"* and started
nothing would pass a grep of its reply and fails every one of these.

**Leg two, the thinker.** That same runtime is on **that host's executor**, because the skill told
it so -- Copilot by `SKILL.md`'s one `--host copilot` line, Claude by the skill's own host
detection -- and nothing in this scenario passes an executor of its own; `source=flag` is asserted
beside the name, because a runtime that guessed right off a `PATH` would prove nothing about the
skill. Then the founder's journey from S-001's own legs, with the host's model answering every
screen: three stages framed, reviewed and approved as-is, one person invited and answered, the
reading read, *What this says* written, the overview and one card opened.

**Every card assertion is a shape or an absence** (spec 008's judgement call 8, and spec 016
FR-007). A live model's sentence is not stable and a test that pinned one would be measuring the
weather; what is asserted is that the card exists, carries numbered lines, separates at least one
deal-breaker, and was not refused.

**Two lengths, and the short one is what every qualifying change runs** (spec 021).
`KEEL_JOURNEY_LEGS=short` (`make eval-live K=s012 HOST=... LEGS=short`) stops the journey after the
**first model job** -- the host leg entire, then the PROBLEM frame's confirmation card landing --
and leaves by the same door. It asserts exactly the assertions the full journey makes up to that
point and **not one thing more**: nothing is read out of the model's prose that was not read out
of it before, and no new shape is claimed because the run is shorter. `full` is unchanged and is
what the nightly and weekly sets run. The bundle's own name carries the difference.

**The founder is a golden-corpus founder** (spec 021). `KEEL_JOURNEY_ENTRY`, default `03-lullaby`,
names an entry in keel-cloud's `canon/designs/measured-beliefs/corpus/`; the entry's title is the
project name, its market is the market, its three statements are typed verbatim, and its **first
person** answers with their own story text and their own picks. They are read through
`harness/corpus_script.py` -- the same `founder_inputs`/`person_inputs` the six scripted scenarios
read them through, reused rather than copied, so the journey's founder and the corpus scenarios'
founder are the same founder rather than two people who happen to agree. What this does **not**
change is the model's half: the beliefs, the roles, the anchors and the pick lists on a live run
are the host model's own, so the person's story goes into the anchors the model wrote, in order,
and their picks are used where the model's own option list happens to offer them. Which is which
is recorded in the bundle, never asserted (spec 016 FR-007).

**Not scored.** No attribute of `evals/policy.py` applies to a scenario about which host loaded a
skill and which model answered a job -- the same reason S-008 and S-009 are not scored. The
evidence is the transcript, the two host transcripts beside it, and the per-job envelopes.

The referee owns no product code: a fault here is a `runs/DRIFT.md` entry, never a workaround.
"""

from __future__ import annotations

import json
import os
import shutil
import time

import pytest

from evals.preludes import create_project
from harness import agent_host, canary as canary_mod, corpus_script, refusals
from stack import remote
from harness.browser import (Auth, Chat, Connect, Landing, OpenedCard, Overview, ParticipantPage,
                              People, ReviewCard, Shell)
from harness.evidence import finalize_run, write_block, write_generated, write_host
from harness.steps import Recorder
from stack import runtime as stack_runtime

pytestmark = pytest.mark.live

#: **Which host this run is the journey through**, resolved once, at import, from
#: `KEEL_JOURNEY_HOST`. An unknown value raises rather than falling back: a typo that quietly ran
#: the other host would spend the founder's money on a measurement nobody asked for.
HOST = agent_host.journey_host()


def _environment_of(base_url: str) -> str:
    """What keel-runtime's `status.environment` says for a base URL (its `config.environment_for`):
    `host:port` when the URL carries a port, the bare host otherwise. Mirrored here rather than
    imported so the referee never imports the runtime it is judging."""
    from urllib.parse import urlsplit
    parts = urlsplit(base_url)
    host = parts.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    return f"{host}:{parts.port}" if parts.port else host

#: **How much of this journey is run**, resolved once, at import, from `KEEL_JOURNEY_LEGS`
#: (spec 021). `short` is the host leg plus the first model job; `full` is everything. An unknown
#: value raises for the same reason an unknown host does -- one typo either overspends or
#: underspends the founder's money and files the result under the wrong name.
LEGS = agent_host.journey_legs()

#: True when this run stops after the PROBLEM frame's confirmation card. Read in exactly two
#: places below -- where leg two would go on, and where the bundle records what it did -- so the
#: short journey is a *stopping point* in the one story and never a second story.
SHORT = LEGS == "short"

#: **Whose founder walks it** -- an entry id in keel-cloud's golden corpus (`KEEL_JOURNEY_ENTRY`,
#: default `03-lullaby`). Resolved at import beside the other two axes; the entry itself is read
#: inside the test, where the stack fixture has told us where keel-cloud is.
ENTRY_ID = agent_host.journey_entry()

#: `runs/<stamp>-s012-journey-<host>[-short]/`. The matrix uploads one bundle per cell and a reader
#: looking at eighteen of them has only the name to go on until they open one.
BUNDLE = agent_host.bundle_slug(HOST, LEGS)

#: The founder's own three words. Not "run the keel connect skill", not "use the keel-connect
#: plugin to start the runtime" -- the point of leg one is that a host with the skill installed
#: recognises what a founder would actually type, and `SKILL.md`'s own description is what has to
#: do the recognising.
THE_FOUNDER_SAYS = "keel connect"

#: **C-5's pin, exercisable for the first time -- and load-bearing.** keel-runtime spec 005
#: measured on 2026-09-09 that CLI 1.0.83 refused every slug offered to `--model`, so
#: `CopilotExecutor.model` defaults to `None` and C-5 was closed by mechanism rather than by
#: measurement. On the upgraded plan **every** slug is accepted, so the pin is real at last; it is
#: passed through `KEEL_COPILOT_MODEL`, keel-runtime's own way in, because the skill passes no
#: `--copilot-model` and a founder passes nothing at all.
#:
#: **Why this slug and not the router's own default.** The plan's default is now `claude-sonnet-5`,
#: and on that model **every keel-runtime job fails** (`runs/DRIFT.md` **#59**): Copilot's
#: Anthropic-vendored `assistant.message` events carry no `phase` key, and
#: `executor._copilot_final_answer` reads only the `final_answer`-phase message, so a correct
#: answer in the right shape is thrown away and the job is reported failed with `exit_code: 0` and
#: no error anywhere. That run stands in `runs/` as the evidence, red, and nothing here is
#: asserted more loosely because of it.
#:
#: `gpt-5.6-luna` emits `phase` (measured, same CLI, same flags, one variable) **and** is the model
#: the router happened to choose for all 129 answered cases of
#: `runs/20260909T061537Z-instructions-copilot` -- so pinning it is also what makes this run and
#: that one the same measurement rather than two. C-5's own words: *`auto` is never used in a
#: measured run.*
RUNTIME_MODEL = "gpt-5.6-luna"

#: **What the runtime pins, per host -- and one of the two is deliberately nothing.**
#: keel-runtime's `ClaudeCodeExecutor._build_argv` never passes a model and there is no
#: `KEEL_CLAUDE_MODEL` to set, so a Claude journey's runtime model is **recorded, not pinned**:
#: read back off the per-job envelopes the CLI itself writes. Inventing a pin that the runtime
#: ignores would put a fact about the referee into the bundle.
RUNTIME_MODEL_FOR_HOST = {"copilot": RUNTIME_MODEL, "claude": None}

#: **The host's model is a different question, and gets the founder's own answer.** Leg one asks
#: what happens when the founder types "keel connect" into *their* CLI, so it pins what their CLI
#: would have chosen anyway -- Copilot CLI 1.0.83 on the upgraded plan logs *"Using default model:
#: claude-sonnet-5"*, and Claude Code's default is whatever that account is configured for, which
#: this run records rather than overrides. Pinning keeps the run reproducible without making it
#: unrepresentative; putting the runtime's slug here instead would have measured a founder nobody
#: is. On Copilot the two pins disagree because #59 made them disagree, and the bundle records
#: both and why.
HOST_MODEL_FOR_HOST = {"copilot": "claude-sonnet-5", "claude": None}

#: The Copilot-era name for the host pin's override, kept because a run record names it.
HOST_MODEL_ENV = ("KEEL_JOURNEY_HOST_MODEL", "KEEL_S012_HOST_MODEL")

#: The founder's own three, in the order the guided walk takes them.
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: What the runtime's own startup line must say before leg two spends anything (FR-006).
EXPECTED_EXECUTOR = agent_host.EXECUTOR_FOR_HOST[HOST]

#: keel-cloud's own terminal-failure statuses, borrowed from `harness/refusals.py` so the two
#: readings of "refused" cannot drift apart.
REFUSED = refusals.TERMINAL_FAILURE_STATUSES

#: The statuses an interaction is allowed to end this journey in. `APPLIED` is a stage that landed;
#: `ACCEPTED` is a frame whose own chained child did the applying; `AWAITING_CONFIRMATION` is a card
#: sitting on the screen waiting for the founder, which is where the last one legitimately is.
SETTLED = frozenset({"APPLIED", "ACCEPTED", "AWAITING_CONFIRMATION"})

#: Bounded, benign, and never an attack: what the founder says when a live model answers a claim
#: box with a question instead of a card. Spec 008's own allowance -- *a question is an answer, and
#: the walk goes on* -- with S-004's ceiling of three, so a model that will not land a claim costs
#: a known number of premium requests rather than an open-ended one.
FOLLOW_UPS = [
    "That is the whole of it. Please write up what you have understood.",
    "Nothing else to add -- go ahead and write up the claim from what I have said.",
    "I have no more detail. Write up what you have understood so far.",
]


def _now() -> float:
    return time.monotonic()


def _land_the_card(page, recorder, get_json, project_id, stage, opening, *, timeout_s=300.0):
    """**The first model job of a stage**: the founder says their statement, the host's model
    thinks, and a confirmation card carrying a non-empty claim comes back.

    Split out of `_walk_stage_live` for spec 021 and for nothing else: the short journey ends here,
    on the PROBLEM stage, and the full journey goes straight on from here into the review. Both
    call this; neither has a copy of it. The assertion the short run makes is therefore *literally*
    the assertion the full run makes at the same point, rather than a second one written to look
    like it.
    """
    chat = Chat(page, recorder)
    chat.send(opening)
    turn = _agent_answers(chat, recorder, get_json, project_id, stage, timeout_s=timeout_s)
    card = chat.confirmation_card()
    stops: list[dict] = []

    for round_no, benign in enumerate(FOLLOW_UPS, start=1):
        if card is not None:
            break
        stopped = (turn or {}).get("stopped")
        if stopped:
            stops.append(stopped)
        why = ("its job failed" if stopped else "it came back with a question")
        with recorder.step(f"§1.1: {stage} produced no card because {why}, so the founder says "
                            f"more ({round_no} of {len(FOLLOW_UPS)})",
                            party="founder", kind="note") as h:
            h.record_wire({"benign": benign},
                           {"the wire": stopped,
                            "reply": (turn or {}).get("agent_reply", "")[:2000]})
        chat.send(benign)
        turn = _agent_answers(chat, recorder, get_json, project_id, stage, timeout_s=timeout_s)
        card = chat.confirmation_card()
    if (turn or {}).get("stopped"):
        stops.append(turn["stopped"])

    with recorder.step(f"§1.1: {stage} comes back as a confirmation card the host's model wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"a card": "with a non-empty claim", "stops": []},
                         {"card": card, "what stopped it, in keel-cloud's own words": stops})
        assert card is not None, (
            f"{HOST} never landed a confirmation card on {stage} after {len(FOLLOW_UPS)} "
            f"benign follow-ups"
            + ("; the wire says: " + " | ".join(refusals.describe(s) for s in stops)
               if stops else ", and the wire had nothing to add"))
        assert (card.get("claim") or "").strip(), f"the {stage} card carries no claim: {card!r}"
    if stops:
        # A stage that landed only after a job of its own had failed is still a green stage --
        # and it is also a fact about this host that the bundle must not lose.
        with recorder.step(f"§1.1: {stage} landed, but not on the first try",
                            party="stack", kind="note") as h:
            h.record_wire(None, {"jobs that failed before the card": stops})
    return chat, card


def _walk_stage_live(page, recorder, get_json, project_id, stage, opening, *, timeout_s=300.0):
    """One stage of the guided walk, against a **live** model.

    Deliberately not `evals/preludes.py::walk_stage`. That one asserts the confirmation card's
    claim **verbatim** against the generated script, which is exactly right for a scripted executor
    and meaningless against a model that writes its own sentence; and its 90-second waits are a
    scripted runtime's, not a live one's. Copying it here rather than growing a `live=` branch on
    it is the choice spec 016's plan states: `walk_stage` is six deterministic scenarios' contract
    with the corpus, and a conditional in it would make all six read like this one.
    """
    chat, _card = _land_the_card(page, recorder, get_json, project_id, stage, opening,
                                 timeout_s=timeout_s)
    chat.save_confirmation()
    landed = chat.wait_for_review(project_id, stage, timeout_s=timeout_s + 180)
    with recorder.step(f"§1.2: the {stage} review opened itself, with no button pressed",
                        party="founder", kind="assert") as h:
        h.record_assert({"the review opened": True}, landed)

    card_page = ReviewCard(page, recorder, _web_base_of(page))
    opened = card_page.open(project_id, stage)
    with recorder.step(f"§1.2: the {stage} card reads Reviewing", party="founder",
                        kind="assert") as h:
        h.record_assert("Reviewing", opened["status"])
        assert "review" in opened["status"].lower(), (
            f"expected Reviewing on {stage}, got {opened['status']!r}")

    # FR-007: shapes, never content.
    with recorder.step(f"§1.2: the {stage} card carries numbered lines and separates at least one "
                        "deal-breaker", party="founder", kind="assert") as h:
        lines = card_page.lines()
        rule_lines = card_page.rule_lines()
        h.record_assert({"lines": ">= 1, each numbered", "rule lines": "one names deal-breakers"},
                         {"lines": len(lines), "rule lines": rule_lines,
                          "headings": [line.get("heading") for line in lines],
                          "first line": (lines[0] if lines else None)})
        assert lines, f"the {stage} card rendered no lines at all"
        unnumbered = [line.get("heading") for line in lines
                      if not str(line.get("number") or "").strip()]
        assert not unnumbered, f"a {stage} line is unnumbered: {unnumbered}"
        assert any("deal-breaker" in line.lower() for line in rule_lines), (
            f"the {stage} card separates no deal-breaker from what is worth knowing: "
            f"{rule_lines!r}")
        assert all(line.get("chips") for line in lines), (
            f"a {stage} line offers no pick list at all: "
            f"{[l.get('heading') for l in lines if not l.get('chips')]}")

    card_page.approve()
    with recorder.step(f"§1.2 wire: {stage} is framed and approved after approval, and nothing on "
                        "the chain was refused", party="stack", kind="assert") as h:
        overview_body = get_json(f"/v2/projects/{project_id}/overview") or {}
        after = next((s for s in overview_body.get("stages") or [] if s.get("type") == stage), {})
        refusal = refusals.stage_refusal(get_json, project_id, stage)
        h.record_assert({"framed": True, "approved": True, "refusal": None},
                         {**after, "refusal": refusal})
        assert refusal is None, f"{stage} was refused: {refusals.describe(refusal)}"
        assert after.get("framed") is True and after.get("approved") is True, (
            f"expected {stage} framed+approved, got {after}")
    return card_page


def _agent_answers(chat, recorder, get_json, project_id, stage, *, timeout_s):
    """`Chat.wait_for_agent_turn`, plus S-004's own lesson: **when the screen stops changing, ask
    the wire why.** A chain keel-cloud refused, or a job that failed, leaves the chat reading
    *Connected* for ever, so a wait on the screen can only ever report that nobody answered
    (`runs/DRIFT.md` #37).

    Returns the turn, or -- when the wire has an answer the screen does not -- `{"stopped":
    <the wire's own words>}`, which is not a turn and which the caller treats as *this round
    produced no card*. It does **not** raise: on a live walk a stage whose job failed is a stage
    the founder can still say something else to, and `_walk_stage_live`'s bounded follow-ups are
    exactly what a founder does next. The run fails, legibly and with keel-cloud's own sentence,
    only once those are spent.
    """
    try:
        return chat.wait_for_agent_turn(timeout_s=timeout_s)
    except TimeoutError as exc:
        stopped = refusals.why_the_stage_stopped(get_json, project_id, stage)
        if stopped is None:
            raise
        with recorder.step(f"the wire says why the {stage} chat stopped answering",
                            party="stack", kind="note") as h:
            h.record_wire(None, stopped)
        _ = exc
        return {"stopped": stopped, "agent_reply": ""}


#: **The last resort, and only that** (spec 021). The stranger's words are the corpus person's own
#: -- one story per anchor they wrote under, in the corpus's own order -- and this sentence is used
#: only where a live model wrote more anchors than that person has stories for. Its *content* is
#: asserted nowhere either way: what leg two needs from the stranger is that a real answer reached
#: keel-cloud and produced a reading, not that any particular words did.
THE_STRANGER_SAYS = ("I am thinking of the last time this happened to me, and it went much the "
                     "way I described above.")


def _story_texts(person) -> list[str]:
    """The corpus person's own story text, per anchor they wrote under, in the corpus's order.

    `PersonInputs.written()` is `harness/corpus_script.py`'s own reading of *wrote something* --
    the same one the six scripted scenarios type from -- so a blank anchor in the corpus is a
    blank anchor here and this repository has one answer to that question, not two.
    """
    return [(a.text or "").strip() for a in person.written() if (a.text or "").strip()]


def _their_pick(person, options: list[str]) -> tuple[str, bool]:
    """Which of the **model's own** options this corpus person picked, and whether it is theirs.

    A live run has no corpus questionnaire: the anchors and the pick lists are the host model's,
    invented from the founder's three statements, and a corpus selection id (`S2`) names nothing on
    the page. So the match is by **value**, case- and space-insensitively, across every pick the
    person made: *"3 to 4"* is theirs whichever selection the model hung it under. Where nothing
    of theirs is offered, the first option is taken -- exactly what this scenario did before spec
    021 -- and the caller records which of the two happened.

    Returns `(option, it_was_theirs)`. Never asserts: a model that offered none of the person's
    answers has written a different questionnaire, which is a finding for the bundle and not a
    failure of the journey (FR-007).
    """
    theirs = {str(v).strip().casefold() for pick in person.picks for v in pick.values}
    for option in options:
        if str(option).strip().casefold() in theirs:
            return option, True
    return options[0], False


def _invite_one_live(page, recorder, project_id: str, web_base: str, person_name: str) -> str:
    """Invite one person to **whichever role the screen actually offers**.

    Deliberately not `evals/preludes.py::invite_everyone`, which reads its role labels out of the
    corpus entry (`{role["id"]: role["label"] for role in entry.roles}`). That is right for a
    scripted run, where the script *is* the corpus, and wrong here: on a live run the roles are
    **the host's model's**, invented from the founder's own three statements, and the entry's own
    *"New parents"* is a label nothing on this page need ever have had. This repository has made
    that exact mistake
    once already, in S-010 -- *"asked a warm project for a fixture's role"* -- and the fix was the
    same one: read the label off the screen.
    """
    people = People(page, recorder, web_base)
    people.open(project_id)
    if page.locator(".role").count() == 0:
        people.switch_to_kinds_tab()
    cards = people.role_cards()
    with recorder.step("§1.4: the roles on the People page are the ones the host wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"role cards": ">= 1, each with a label"}, cards)
        assert cards, "the approved cards produced no role to ask anybody"
        assert cards[0]["label"].strip(), f"a role card has no label: {cards[0]!r}"
    label = cards[0]["label"]
    people.open_send_popup(label)
    people.fill_who(person_name, about=f"{label}, asked about one real occasion.")
    people.go_to_preview()
    url = people.generate_link(person_name.split()[0])
    people.close_popup()
    return url


def _answer_whatever_is_asked(browser, recorder, url: str, person) -> dict:
    """The corpus person answers **the questions the page actually asks**, in their own context.

    `ParticipantPage.answer_as(person, entry)` resolves a corpus person's answers against the
    *corpus's* own anchor and selection prompts. On a live project there is no corpus
    questionnaire: the anchors are the ones the host wrote, and every one of that method's
    `offers(prompt)` checks would fail silently into `skipped`, submitting an empty page. So this
    reads the rendered page instead -- the same move S-004 makes with `_page_choice`, for the same
    reason: *what is offered is the page's to say.*

    What spec 021 changed is **whose words go into it**. The story under the nth anchor is the
    corpus person's own nth story, and a selection is answered with their own value wherever the
    model's option list offers it. Where it does not -- a model that asked something the corpus
    person was never asked -- the first option is taken, as before, and the bundle says which
    answers were theirs and which were the fallback. Nothing about either is asserted; what leg two
    needs is a real answer on the wire (FR-007).
    """
    stories = _story_texts(person)
    context = browser.new_context()
    try:
        page = context.new_page()
        participant = ParticipantPage(page, recorder)
        participant.open(url)
        drawn = participant.anchors()
        with recorder.step("§2.1: the stranger's page carries the questions the host wrote",
                            party="participant", kind="assert") as h:
            h.record_assert({"anchors": ">= 1"}, drawn)
            assert drawn, f"the invitation link rendered no questions at all: {url}"
        answered, picked, theirs_used, fell_back = [], [], [], []
        told = 0
        for anchor in drawn:
            prompt = anchor.get("prompt") or ""
            if not prompt:
                continue
            hers = told < len(stories)
            story = stories[told] if hers else THE_STRANGER_SAYS
            participant.tell_story(prompt, story)
            told += 1
            answered.append({"prompt": prompt[:60], "said": story[:200],
                              "whose": (person.person if hers else
                                        "nobody's -- the model wrote more anchors than this "
                                        "person has stories, so the last resort was typed")})
            (theirs_used if hers else fell_back).append(f"anchor: {prompt[:50]}")
            for selection in anchor.get("selections") or []:
                options = participant.options_for(selection, anchor_prompt=prompt)
                if not options:
                    continue
                option, was_theirs = _their_pick(person, options)
                participant.pick(selection, [option], anchor_prompt=prompt)
                picked.append(f"{selection[:40]} -> {option}"
                              + ("" if was_theirs else "  (the page's own first option; none of "
                                                        "this person's answers was offered)"))
                (theirs_used if was_theirs else fell_back).append(f"pick: {selection[:44]}")
        participant.submit()
        with recorder.step(f"§2.3: {person.person} sent their answers",
                            party="participant", kind="assert") as h:
            h.record_assert({"anchors answered": len(drawn)},
                             {"answered": answered, "picked": picked,
                              "the corpus person's own words and answers, used": theirs_used,
                              "the model asked what the corpus did not, so the page's own answer "
                              "was taken": fell_back})
            assert answered, "the stranger typed nothing anywhere"
        return {"answered": answered, "picked": picked, "theirs": theirs_used,
                "not theirs": fell_back}
    finally:
        context.close()


def _web_base_of(page) -> str:
    from urllib.parse import urlsplit
    parts = urlsplit(page.url)
    return f"{parts.scheme}://{parts.netloc}"


# --------------------------------------------------------------------------------- the scenario

@pytest.mark.bundle(BUNDLE)
def test_s012_journey_through_a_host_live(stack, founder_one, browser, run_dir):
    ready = agent_host.readiness(HOST)
    if not ready["ok"]:
        pytest.skip(ready["reason"])

    recorder = Recorder(run_dir)
    # Spec 017: the stack's own addresses -- `http://localhost:<port>` on the eval and playground
    # profiles, the twin's URLs on `remote` -- and the founder this run signs in as: the built-in
    # Eval Founder locally, a founder registered for this cell against the twin's gated chooser.
    web_base = stack.web_base_url
    cloud_base = stack.cloud_base_url
    cell_label = (f"{remote.cell_name()} · {HOST} · journey ({LEGS}) · "
                  f"{time.strftime('%Y-%m-%d', time.gmtime())}")
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    started = _now()
    passed = False
    context = browser.new_context()

    # **The founder, and the one person, come from the golden corpus** (spec 021) -- through
    # `harness/corpus_script.py`, which is the same module the six scripted scenarios read the
    # same entry through. Reused rather than copied: `founder_inputs` already refuses an entry
    # with a missing statement by name, `person_inputs` already refuses a person offered an anchor
    # their role is not asked, and a second reader here would be a second chance to be wrong about
    # both. A corpus this run cannot reach raises with the directory it looked in -- never a
    # fallback to some other founder, because a bundle that quietly measured a different person is
    # worse than one that measured nobody.
    corpus, entry = corpus_script.entry_for(stack.keel_cloud, ENTRY_ID)
    founder = corpus_script.founder_inputs(entry)
    # **The entry's beliefs, roles, anchors and taps are a *script's* data and are read nowhere
    # below.** On a live run the host's model writes all four. What this run takes from the entry
    # is exactly what a founder types (the name, the market, the three statements) and exactly
    # what one person says (their story per anchor, their picks) -- and the model's half stays
    # free and shape-asserted (spec 016 FR-007).
    person = corpus_script.person_inputs(entry)[0]
    person_name = person.person
    write_generated(run_dir, inputs={"entry": entry.id,
                                     "project": founder.project_name,
                                     "market": founder.market.country,
                                     "statements": {stage: founder.statement(stage)
                                                     for stage in STAGES},
                                     "person": person_name,
                                     "their stories": _story_texts(person),
                                     "their picks": {p.selection_id: p.values
                                                      for p in person.picks},
                                     "host": HOST,
                                     "legs": LEGS})
    # The sixth and seventh facts a reader of eighteen bundles needs after the five repositories:
    # whose founder walked it, and how far.
    write_block(run_dir, "journey", {
        "entry": entry.id, "entry_sha256": entry.sha256, "title": founder.project_name,
        "person": person_name, "legs": LEGS,
        "legs, what that means": (
            "the host leg entire, plus the first model job -- the PROBLEM frame's confirmation "
            "card -- and then the way out" if SHORT else
            "both legs: three stages framed, reviewed and approved, one person invited and "
            "answered, the reading read, the brief written, the overview and one card opened"),
        "corpus": str(corpus.directory)})

    keel_home = run_dir / "keel-home"
    host_home_dir = run_dir / f"{HOST}-home"
    artifacts = run_dir / HOST
    model = os.environ.get("KEEL_COPILOT_MODEL") or RUNTIME_MODEL_FOR_HOST[HOST]
    host_model = next((os.environ[name] for name in HOST_MODEL_ENV if os.environ.get(name)),
                      HOST_MODEL_FOR_HOST[HOST])
    # C-5 again: an unpinned run measures the router, not a model. It is still allowed -- spec 005
    # shipped exactly that -- but the bundle must never imply a pin that was refused. On Copilot
    # both probes are free (`-p ""` is refused before inference), so this costs nothing to be sure
    # of; on Claude there is no free probe and `model_accepted` says so rather than pretending,
    # which is why an unpinned Claude run (the default) never reaches either branch.
    if model and not agent_host.host_type(HOST).model_accepted(model):
        with recorder.step("C-5: `--model` refuses the runtime's slug on this account, so that "
                            "half of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": model, "whose": "the runtime's"}, {"pinned": None})
        model = None
    if host_model and not agent_host.host_type(HOST).model_accepted(host_model):
        with recorder.step("C-5: `--model` refuses the host's slug on this account, so that half "
                            "of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": host_model, "whose": "the host's"}, {"pinned": None})
        host_model = None

    host = agent_host.build_host(HOST, home=host_home_dir, keel_home=keel_home,
                                 base_url=cloud_base, artifacts=artifacts,
                                 model=host_model, runtime_model=model)
    host.write_home_config()
    credential = host.credential_plan()
    # **versions.json says which host, which CLI and which models** (spec 019). The run_dir fixture
    # has already written the five repositories this run stood on; this adds the sixth thing a
    # matrix cell is defined by and a reader of eighteen bundles needs first.
    write_host(run_dir, {"host": HOST, "cli": ready["version"], "binary": host.binary,
                         "home_var": host.home_var, "home": str(host_home_dir),
                         "work_dir": str(host.work_dir),
                         "executor expected": EXPECTED_EXECUTOR,
                         "model (the host's own --model)": host_model,
                         "model (the runtime's)": model,
                         "model (the runtime's), how": (
                             "pinned through KEEL_COPILOT_MODEL" if model else
                             "not pinned -- this host's executor takes no model, so the bundle "
                             "records what answered instead"),
                         "credential": credential})

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=20_000).json()

    def _status() -> dict:
        return stack_runtime.status(stack, home=keel_home)

    try:
        page = context.new_page()
        Auth(page, recorder, web_base).sign_in(founder_one)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()

        with recorder.step("§1.0: the landing reads no agent connected, and this run's own homes "
                            "are empty", party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            h.record_assert({"agent_connected": False, "heartbeat": None},
                             {"agent_connected": arrival["agent_connected"],
                              "agent line": agent_line,
                              "heartbeat": agent_host.read_heartbeat(keel_home),
                              "KEEL_HOME": str(keel_home),
                              host.home_var: str(host_home_dir)})
            assert not arrival["agent_connected"], (
                f"expected no agent connected yet, got {agent_line!r}")
            assert agent_host.read_heartbeat(keel_home) is None, (
                f"this run's KEEL_HOME already carries a heartbeat before {HOST} has said a word")

        # ======================================================= LEG ONE: the host that loads it
        with recorder.step(f"leg one: how this {HOST} is authenticated, and which model it pins",
                            party="stack", kind="note") as h:
            h.record_wire({host.home_var: str(host_home_dir)},
                           {"credential": credential,
                            "cli": ready["version"],
                            "pinned_model (the host's own --model)": host_model,
                            "pinned_model (the runtime's)": model,
                            "why they differ": ("runs/DRIFT.md #59 -- on Copilot the plan's "
                                                "default model answers correctly and keel-runtime "
                                                "cannot read it, so the host keeps the founder's "
                                                "own default and the runtime pins one it can "
                                                "read. On Claude the runtime's executor takes no "
                                                "model at all, so there is nothing to pin and the "
                                                "bundle records what answered."),
                            "KEEL_RUNTIME_PATH in the child": "scrubbed (T-1)",
                            "the session this harness runs in": "scrubbed, so the skill's own "
                                                                "host detection sees one host"})

        with recorder.step("leg one: the plugin is installed from the real marketplace with "
                            f"{HOST}'s own two commands", party="stack", kind="assert") as h:
            added = host.add_marketplace()
            installed = host.install_plugin()
            h.record_wire({"marketplace": agent_host.MARKETPLACE_SOURCE,
                            "plugin": agent_host.PLUGIN_SPEC},
                           {"add": added, "install": installed,
                            "list": host.plugin_list()})
            assert added["exit_code"] == 0, (
                f"`{' '.join(added['cmd'])}` failed: {added['stderr'] or added['stdout']}")
            assert installed["exit_code"] == 0, (
                f"`{' '.join(installed['cmd'])}` failed: "
                f"{installed['stderr'] or installed['stdout']}")

        with recorder.step(f"leg one: {HOST} sees keel-connect, and as a plugin skill",
                            party="stack", kind="assert") as h:
            proof = host.skill_proof()
            h.record_assert({"skill": agent_host.SKILL_NAME, "source": "a plugin"},
                             {"found": proof["found"], "from a plugin": proof["from_plugin"],
                              "detail": proof["detail"], "raw": proof["raw"][:4000]})
            assert proof["found"], (
                f"`{' '.join(proof['cmd'])}` does not name {agent_host.SKILL_NAME!r} after the "
                f"plugin installed cleanly: {proof['raw'][:1000]!r}")
            assert proof["from_plugin"], (
                f"{agent_host.SKILL_NAME!r} is visible but not as a plugin skill: "
                f"{proof['detail']!r}")

        with recorder.step(f'leg one: the founder says "keel connect" to {HOST}, once',
                            party="founder", kind="protocol") as h:
            first = host.say(THE_FOUNDER_SAYS, slug="connect-1")
            h.record_wire({"argv": first.argv, "cwd": str(host.work_dir)},
                           {"exit_code": first.exit_code, "model": first.model,
                            "spend": first.spend(),
                            "tools": first.tools_used,
                            "reply": first.reply_text[:4000],
                            "stderr": first.stderr[:2000],
                            "transcript": str(first.transcript_path)})

        with recorder.step("leg one: a runtime is really there -- the heartbeat says "
                            "`awaiting_approval`", party="stack", kind="assert") as h:
            heartbeat = agent_host.read_heartbeat(keel_home)
            h.record_assert({"state": agent_host.STATE_AWAITING_APPROVAL,
                              "pid": "a live one", "agent_session_id": None},
                             heartbeat)
            assert heartbeat is not None, (
                f"{HOST} answered but no runtime heartbeat exists under this run's KEEL_HOME "
                f"({keel_home}) -- so nothing was started, whatever the reply said. It said: "
                f"{first.reply_text[:400]!r}")
            assert heartbeat.get("state") == agent_host.STATE_AWAITING_APPROVAL, (
                f"expected a runtime waiting for device approval, the heartbeat reads "
                f"{heartbeat.get('state')!r}")
            assert heartbeat.get("pid"), f"the heartbeat names no pid: {heartbeat!r}"

        with recorder.step("leg one: the launch log carries the code and the device page URL",
                            party="stack", kind="assert") as h:
            log_text = agent_host.read_launch_log(keel_home)
            user_code = agent_host.user_code_in(log_text)
            verification_uri = agent_host.verification_uri_in(log_text)
            h.record_assert({"KEEL_USER_CODE=": "XXXX-XXXX",
                              "KEEL_VERIFICATION_URI=": f"{web_base}/connect"},
                             {"user_code": user_code, "verification_uri": verification_uri,
                              "log": log_text[:2000]})
            assert agent_host.looks_like_a_user_code(user_code), (
                f"no `KEEL_USER_CODE=` line of the right shape in {keel_home}/"
                f"{agent_host.LAUNCH_LOG_FILENAME}: {log_text[:500]!r}")
            assert verification_uri and verification_uri.startswith(f"{web_base}/connect"), (
                f"the launch log's verification URI is not this stack's own /connect: "
                f"{verification_uri!r}")

        with recorder.step("leg one: the code is one **this Keel** issued, and it is not approved "
                            "yet", party="stack", kind="assert") as h:
            response = context.request.get(
                f"{cloud_base}/v2/device-authorizations?user_code={user_code}", timeout=20_000)
            body = response.json() if response.ok else {"status": response.status}
            h.record_assert({"http": 200, "approved": False},
                             {"http": response.status, "body": body})
            assert response.ok, (
                f"the eval cloud does not know the code {HOST} relayed ({user_code!r}): "
                f"HTTP {response.status}. A code this Keel never issued means the skill talked to "
                f"a different Keel, or the host invented one.")
            assert not body.get("approved"), (
                f"the code was already approved before the founder touched it: {body}")

        connect = Connect(page, recorder)
        frame = connect.open(verification_uri)
        with recorder.step("leg one: the verification URI opens the device-decision frame",
                            party="founder", kind="assert") as h:
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
            on_screen = connect.user_code()
            assert user_code in on_screen, (
                f"the screen shows {on_screen!r} where the launch log said {user_code!r}")
        connect.approve()
        connect.wait_for_connected(timeout_s=60)

        with recorder.step('leg one: the founder says "keel connect" a second time -- the skill\'s '
                            "`already_connected`", party="founder", kind="protocol") as h:
            second = host.say(THE_FOUNDER_SAYS, slug="connect-2")
            h.record_wire({"argv": second.argv},
                           {"exit_code": second.exit_code, "model": second.model,
                            "spend": second.spend(),
                            "tools": second.tools_used,
                            "reply": second.reply_text[:4000],
                            "transcript": str(second.transcript_path)})

        with recorder.step("leg one: the runtime's own `status` says connected -- and the host's "
                            "reply says so too (loosely, and never on its own)",
                            party="stack", kind="assert") as h:
            status = _status()
            said_connected = agent_host.mentions_connected(second.reply_text)
            h.record_assert({"running": True, "connected": True, "reply mentions connected": True},
                             {"status": status, "reply mentions connected": said_connected,
                              "reply": second.reply_text[:1000]})
            assert status.get("running"), f"the runtime is not running after approval: {status}"
            assert status.get("connected"), (
                f"the runtime never completed device approval: {status}")
            assert said_connected, (
                f"the runtime is connected but {HOST}'s second reply never says so, so the "
                f"skill's `already_connected` was not relayed: {second.reply_text[:400]!r}")

        # ==================================================== LEG TWO: the host that answers it
        with recorder.step(f"leg two: the runtime is on the {EXPECTED_EXECUTOR} executor, because "
                            "the skill told it which host it was running under and nothing here "
                            "named an executor", party="stack", kind="assert") as h:
            # **Read off the runtime's own startup line, not off `keel status`** (`runs/DRIFT.md`
            # #58). keel-cloud's contract defines `status.executor` as *"which executor this home
            # **would** run a job with ... resolved the same way `connect` resolves it"* -- the
            # caller's resolution, not the live process's. Asked from this harness (a Claude Code
            # session, so `CLAUDECODE=1` is in the environment `resolve_executor` reads) it
            # answers `claude` about a runtime whose own log says `KEEL_EXECUTOR=copilot`. That
            # is the first thing this scenario found and it is recorded, not adapted around: the
            # `status` reading goes into the bundle beside the one that knows.
            #
            # **`source=flag` is asserted on both hosts, and it is the same chain both times.**
            # Copilot gets there because `SKILL.md` carries the one D5 exception telling it to add
            # `--host copilot`; Claude gets there because the skill's own `detect_host` reads the
            # `CLAUDECODE=1` its CLI sets for the shell it runs the script in. Either way the
            # *script* passes `--executor`, so the runtime records an explicit term -- and a run
            # that arrived at the right name by `source=path` or `source=host` would be a runtime
            # that guessed right, which proves nothing about the skill.
            launched = agent_host.launch_executor_in(agent_host.read_launch_log(keel_home))
            status = _status()
            h.record_assert({"KEEL_EXECUTOR": EXPECTED_EXECUTOR, "source": "flag"},
                             {"the runtime's own startup line": launched,
                              "keel status (DRIFT #58: the caller's resolution, not this "
                              "runtime's)": {"executor": status.get("executor"),
                                             "executor_on_path": status.get("executor_on_path")},
                              "environment": status.get("environment")})
            assert launched is not None, (
                f"the runtime left no `KEEL_EXECUTOR=` line in {keel_home}/"
                f"{agent_host.LAUNCH_LOG_FILENAME}, so which executor it chose is unknowable")
            assert launched["executor"] == EXPECTED_EXECUTOR, (
                f"the runtime is on {launched['executor']!r}, not {EXPECTED_EXECUTOR!r} -- the "
                f"skill did not tell it which host it was running under (SKILL.md's D5 "
                f"exception for Copilot; the script's own host detection for Claude)")
            assert launched.get("source") == "flag", (
                f"the runtime chose {EXPECTED_EXECUTOR!r} by {launched.get('source')!r} rather "
                f"than by an explicit term -- the skill is meant to *tell* it, so a run that "
                f"guessed right off an environment marker has not proven the skill's line works")
            assert status.get("environment") == _environment_of(cloud_base), (
                f"the runtime names {status.get('environment')!r}, not this stack's Keel")

        with recorder.step("C-5: the pin the skill's own launch carried -- or, on a host whose "
                            "executor takes no model, the absence of one, said out loud",
                            party="stack", kind="assert") as h:
            h.record_assert({"model": model}, {"the runtime's own startup line": launched,
                                               "pinned": bool(model)})
            if model:
                assert launched.get("model") == model, (
                    f"the runtime launched with model {launched.get('model')!r} where this run "
                    f"pinned {model!r}: `KEEL_COPILOT_MODEL` did not reach the executor")

        project_id = create_project(page, recorder, web_base, founder)

        # **The first model job, and on the short journey the only one** (spec 021). The founder
        # types the entry's PROBLEM statement and the host's model answers it with a confirmation
        # card. `_land_the_card` is one function, called from here and from `_walk_stage_live`, so
        # the assertion the short run makes is *the same assertion* the full run makes at the same
        # point -- not a copy of it that would have to be kept in step.
        if SHORT:
            _land_the_card(page, recorder, _get, project_id, "PROBLEM",
                           founder.statement("PROBLEM"))
            # Nothing is asserted about *stopping*: the short journey does less, it does not do
            # something else. This is a note, and every assertion below it -- no refusals, every
            # job COMPLETED, what it cost, the founder's own way out -- is one both lengths make.
            with recorder.step("spec 021: the short journey stops here -- the host leg and the "
                                "first model job are what a qualifying change buys",
                                party="stack", kind="note") as h:
                h.record_wire({agent_host.LEGS_ENV: LEGS},
                               {"asserted": "the plugin from the public marketplace, the skill "
                                            "seen as a plugin skill, a runtime awaiting "
                                            "approval, a code this Keel issued, the device "
                                            "approved, `already_connected`, the executor chosen "
                                            "by flag, the pin, and one confirmation card",
                                "not run, and run nightly and weekly instead": (
                                    "the PROBLEM review, SOLUTION, COMMERCIAL, the person, the "
                                    "reading, *What this says*, the overview and one card"),
                                "the founder this run typed as": founder.project_name,
                                "the entry they came from": entry.id})
        else:
            for stage in STAGES:
                _walk_stage_live(page, recorder, _get, project_id, stage, founder.statement(stage))
                ReviewCard(page, recorder, web_base).continue_onward()

            people = People(page, recorder, web_base)
            people.open(project_id)
            with recorder.step("§1.4: People unlocks once every framed card is approved",
                                party="founder", kind="assert") as h:
                locked = Shell(page, recorder).people_locked()
                h.record_assert({"people_locked": False}, {"people_locked": locked})
                assert not locked, "People stayed locked after all three approvals"

            url = _invite_one_live(page, recorder, project_id, web_base, person_name)
            _answer_whatever_is_asked(browser, recorder, url, person)

            people.open(project_id)
            people.switch_to_who_tab()
            read_result = people.read_all_and_wait(timeout_s=420)
            with recorder.step("§1.6: the host read the answer, and the toast names what moved",
                                party="founder", kind="assert") as h:
                h.record_assert("a non-empty toast", read_result["toast_text"])
                assert read_result["toast_text"].strip(), (
                    "the reading produced no toast, so nothing was read")

            overview = Overview(page, recorder, web_base)
            with recorder.step("§1.7: *What this says* -- the paragraph the host wrote, unasked",
                                party="founder", kind="assert") as h:
                # keel-cloud starts a BRIEF job by itself when a reading batch finishes
                # (`ReadingBatchService.sayWhatThisSays`), so the founder is given nothing to wait on
                # and this polls the wire the runtime is answering.
                deadline = _now() + 420
                paragraph = None
                while _now() < deadline:
                    wire = _get(f"/v2/projects/{project_id}/overview") or {}
                    paragraph = wire.get("whatThisSays")
                    if paragraph and paragraph.strip():
                        break
                    page.wait_for_timeout(3_000)
                overview.open(project_id)
                on_screen = overview.what_this_says_paragraph()
                h.record_assert({"whatThisSays": "non-empty, and rendered verbatim"},
                                 {"wire": paragraph, "screen": on_screen})
                assert paragraph and paragraph.strip(), (
                    "no *What this says* paragraph after the reading -- the BRIEF job the host was "
                    "given never produced one")
                assert on_screen == paragraph, (
                    f"the overview renders {on_screen!r}, not the server's own {paragraph!r}")

            with recorder.step("§1.7: the overview carries the bar, the legend and three stage cards",
                                party="founder", kind="assert") as h:
                counts = overview.lines_with_answers()
                legend = overview.legend()
                cards = overview.stage_cards()
                h.record_assert({"stage cards": 3, "legend": list(overview.LEGEND_WORDS)},
                                 {"lines with answers": counts, "legend": legend,
                                  "stage cards": [c["bet"] for c in cards]})
                assert len(cards) == 3, [c["bet"] for c in cards]
                assert set(legend) == set(overview.LEGEND_WORDS), legend

            opened = OpenedCard(page, recorder, web_base)
            opened.open(project_id, "PROBLEM")
            with recorder.step("§1.7: one card, opened -- strips, numbers and a status on each",
                                party="founder", kind="assert") as h:
                strips = opened.strips()
                h.record_assert({"strips": ">= 1, each with a number and a status"},
                                 {"strips": len(strips), "first": (strips[0] if strips else None)})
                assert strips, "the opened PROBLEM card rendered no strips"
                for strip in strips:
                    assert str(strip.get("number") or "").strip(), f"an unnumbered strip: {strip!r}"

        # ------------------------------------------------- what it cost, and what never happened
        with recorder.step("leg two: zero refusals, every job COMPLETED",
                            party="stack", kind="assert") as h:
            interactions = context.request.get(
                f"{cloud_base}/v2/inference-interactions?project_id={project_id}",
                timeout=20_000).json()
            refused = [{"interaction_id": i.get("interaction_id"), "screen": i.get("screen"),
                        "status": i.get("status"), "detail": i.get("detail"),
                        "diagnostic": i.get("diagnostic")}
                       for i in interactions if i.get("status") in REFUSED]
            unsettled = [{"interaction_id": i.get("interaction_id"), "screen": i.get("screen"),
                          "status": i.get("status")}
                         for i in interactions if i.get("status") not in SETTLED]
            bad_jobs = [{"job_id": (i.get("job") or {}).get("job_id"), "screen": i.get("screen"),
                         "status": (i.get("job") or {}).get("status"),
                         "error": (i.get("job") or {}).get("error")}
                        for i in interactions
                        if i.get("job") and (i.get("job") or {}).get("status") != "COMPLETED"]
            h.record_assert({"refusals": [], "jobs not COMPLETED": []},
                             {"interactions": len(interactions), "refusals": refused,
                              "not settled": unsettled, "jobs not COMPLETED": bad_jobs,
                              "statuses": sorted({i.get("status") for i in interactions})})
            assert not refused, f"the host's work was refused: {refused}"
            assert not bad_jobs, f"a job did not complete: {bad_jobs}"
            assert not unsettled, f"an interaction never settled: {unsettled}"

        with recorder.step("what it cost, in this host's own unit and never converted into the "
                            "other's (C-7)", party="stack", kind="note") as h:
            rows = canary_mod.wait_for_envelopes(keel_home, timeout_s=180)
            per_job = []
            for row in rows:
                facts = host.envelope_facts(row["envelope"])
                per_job.append({"job_id": row["job_id"], **facts})
            caps = canary_mod.cap_sources(stack.keel_runtime, keel_home)
            spend = {"host legs": [run.spend() for run in (first, second)],
                     "thinking (keel-runtime jobs)": [
                         {k: v for k, v in row.items()
                          if k in ("job_id", "premium_requests", "total_cost_usd", "model")}
                         for row in per_job],
                     "jobs": len(rows),
                     "pinned_model (runtime)": model,
                     "pinned_model (host)": host_model,
                     "reported model (host)": second.model,
                     "cap sources": caps}
            h.record_wire({"per job": per_job}, spend)
            (run_dir / "spend.json").write_text(json.dumps(
                {"host": HOST, **spend, "per job": per_job}, indent=2) + "\n")
            errored = [r for r in per_job if r["is_error"]]
            assert per_job, "the runtime wrote no job envelopes at all"
            assert not errored, f"a keel-runtime job envelope reports an error: {errored}"
            # **The second, independent proof that this host did the thinking** -- where the
            # envelope can carry it. `CopilotExecutor._envelope` stamps `executor` on every job,
            # written by the process that ran it, so the startup line says which executor was
            # *chosen* and this says which one *answered*. `ClaudeCodeExecutor` passes the CLI's
            # own `result` event through unchanged and that event names no executor, so on that
            # host the cross-check does not exist and the bundle says so rather than the scenario
            # quietly asserting less on both.
            if host.envelope_names_its_executor:
                wrong_host = [r for r in per_job if r["executor"] != EXPECTED_EXECUTOR]
                assert not wrong_host, (
                    f"a job was answered by an executor that is not {EXPECTED_EXECUTOR!r}: "
                    f"{wrong_host}")
            else:
                with recorder.step("...and on this host the per-job envelope names no executor "
                                    "at all, so the startup line is the only reading there is",
                                    party="stack", kind="note") as note:
                    note.record_wire(None, {"envelope keys": sorted(rows[0]["envelope"] or {}),
                                            "why": per_job[0]["why"]})
        print(f"\nS-012 {LEGS} journey through {HOST} as {founder.project_name!r} "
              f"({entry.id}): {len(rows)} jobs; "
              f"host legs {[run.spend() for run in (first, second)]}; "
              f"runtime model {model or 'unpinned (this executor takes none)'}")

        # ------------------------------------------------------------------- the way a founder goes
        with recorder.step('§1.0: "keel disconnect" against this run\'s own home',
                            party="stack", kind="assert") as h:
            outcome = stack_runtime.disconnect_via_skill_script(stack, home=keel_home, timeout=60)
            after = _status()
            h.record_assert({"outcome": "disconnected", "running after": False},
                             {"disconnect": outcome, "after": after})
            assert outcome is not None, (
                "keel-connect-skill's own way out answered nothing at all")
            assert outcome.get("outcome") in stack_runtime.STOPPED_OUTCOMES, (
                f"the runtime did not stop: {outcome}")
            assert not after.get("running", False), (
                f"disconnect answered {outcome.get('outcome')!r} but status still reads running: "
                f"{after}")

        passed = True
    finally:
        context.close()
        shutil.rmtree(host.work_dir, ignore_errors=True)
        # Spec 017 / e2e-matrix-design §6.4: the verdict goes onto the cell's own founder in the
        # twin's chooser, so the founder's morning picker reads it. Local profiles: no I/O.
        if stack.is_remote:
            verdict = "PASSED" if passed else f"FAILED at {recorder.failed_step or 'an unnamed step'}"
            try:
                remote.label_cell_identity(stack, founder_one.id, f"{cell_label} — {verdict}")
            except Exception as exc:  # noqa: BLE001 - the label is evidence, never the verdict
                print(f"\ncould not label the cell's founder in the chooser: {exc}")
        # `facts.json` is the scorer's own registry and this scenario is unscored, so it would
        # otherwise be `{}`. One string goes in beside it -- a *string*, so `scoring.read_facts`
        # skips it rather than reading an empty Fact out of it -- because a bundle whose verdict
        # says `s012-journey-claude` should say which host, which CLI and which model in the
        # file a reader opens next. The structured record is `versions.json`'s `host` block.
        finalize_run(run_dir, slug=BUNDLE, passed=passed,
                     facts={"the journey's host": (
                         f"{HOST} · {ready['version']} · host model "
                         f"{host_model or 'the account default, recorded not pinned'} · runtime "
                         f"model {model or 'unpinned (this executor takes none)'}"),
                            "the journey's founder": (
                         f"{ENTRY_ID} · {founder.project_name} · "
                         f"{founder.market.country} · one person, {person_name}"),
                            "the journey's length": (
                         f"{LEGS} · " + ("the host leg and the first model job" if SHORT else
                                          "both legs, whole"))},
                     failed_step=recorder.failed_step, duration_s=_now() - started)
        print(f"\nrun bundle: {run_dir}")
