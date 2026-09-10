"""S-012 -- Copilot, host and thinker (spec `016-copilot-e2e`).

**Live**, opt-in through `make eval-live K=s012`, never part of `make eval`/`make eval-all`, and it
spends the founder's own premium requests.

Two legs, one runtime, and the runtime is what joins them.

**Leg one, the host.** keel-connect-skill's plugin is installed into a **fresh `COPILOT_HOME`**
from the real public marketplace with Copilot's own two commands, `copilot skill list` is asked
whether it can see `keel-connect` as a plugin skill, and then the founder's three words --
*"keel connect"* -- are said to `copilot -p`. Everything after that is asserted against the
**runtime's own artefacts**, never Copilot's prose: the heartbeat file in state
`awaiting_approval`, the launch log's `KEEL_USER_CODE=` and `KEEL_VERIFICATION_URI=` lines, and the
eval cloud's own answer to `GET /v2/device-authorizations?user_code=`. A host that said *"Keel is
connected!"* and started nothing would pass a grep of its reply and fails every one of these.

**Leg two, the thinker.** That same runtime is on the **Copilot executor**, because the skill read
`SKILL.md`'s one Copilot line and passed `--host copilot` -- nothing in this scenario passes
`--executor`, and `status.executor` is asserted before the first job. Then the founder's journey
from S-001's own legs, with Copilot answering every screen: three stages framed, reviewed and
approved as-is, one person invited and answered, the reading read, *What this says* written, the
overview and one card opened.

**Every card assertion is a shape or an absence** (spec 008's judgement call 8, and spec 016
FR-007). A live model's sentence is not stable and a test that pinned one would be measuring the
weather; what is asserted is that the card exists, carries numbered lines, separates at least one
deal-breaker, and was not refused.

**Not scored.** No attribute of `evals/policy.py` applies to a scenario about which host loaded a
skill and which model answered a job -- the same reason S-008 and S-009 are not scored. The
evidence is the transcript, the two Copilot transcripts beside it, and the per-job envelopes.

The referee owns no product code: a fault here is a `runs/DRIFT.md` entry, never a workaround.
"""

from __future__ import annotations

import json
import os
import time

import pytest

from evals import payroll_exceptions as fx
from evals.preludes import create_project
from harness import canary as canary_mod
from harness import copilot_host, refusals
from harness.browser import (Auth, Chat, Connect, Landing, OpenedCard, Overview, ParticipantPage,
                              People, ReviewCard, Shell)
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from stack import runtime as stack_runtime

pytestmark = pytest.mark.live

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

#: **The host's model is a different question, and gets the founder's own answer.** Leg one asks
#: what happens when the founder types "keel connect" into *their* Copilot, so it pins what their
#: Copilot would have chosen anyway -- CLI 1.0.83 on the upgraded plan logs *"Using default model:
#: claude-sonnet-5"*. Pinning it keeps the run reproducible without making it unrepresentative;
#: putting the runtime's slug here instead would have measured a founder nobody is. The two pins
#: disagree because #59 made them disagree, and the bundle records both and why.
HOST_MODEL = "claude-sonnet-5"

#: The founder's own three, in the order the guided walk takes them.
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: What the runtime's `status` must say before leg two spends anything (FR-006).
EXPECTED_EXECUTOR = "copilot"

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


def _walk_stage_live(page, recorder, get_json, project_id, stage, opening, *, timeout_s=300.0):
    """One stage of the guided walk, against a **live** model.

    Deliberately not `evals/preludes.py::walk_stage`. That one asserts the confirmation card's
    claim **verbatim** against the generated script, which is exactly right for a scripted executor
    and meaningless against a model that writes its own sentence; and its 90-second waits are a
    scripted runtime's, not a live one's. Copying it here rather than growing a `live=` branch on
    it is the choice spec 016's plan states: `walk_stage` is six deterministic scenarios' contract
    with the corpus, and a conditional in it would make all six read like this one.
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

    with recorder.step(f"§1.1: {stage} comes back as a confirmation card Copilot wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"a card": "with a non-empty claim", "stops": []},
                         {"card": card, "what stopped it, in keel-cloud's own words": stops})
        assert card is not None, (
            f"Copilot never landed a confirmation card on {stage} after {len(FOLLOW_UPS)} "
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


#: One benign sentence per anchor, and the same one every time. Its *content* is asserted nowhere:
#: what leg two needs from the stranger is that a real answer reached keel-cloud and produced a
#: reading, not that any particular words did.
THE_STRANGER_SAYS = ("Last month it took me about two hours the day before the pay run, and one "
                     "person was nearly paid the wrong amount because a timesheet came in late.")


def _invite_one_live(page, recorder, project_id: str, web_base: str, person_name: str) -> str:
    """Invite one person to **whichever role the screen actually offers**.

    Deliberately not `evals/preludes.py::invite_everyone`, which reads its role labels out of the
    corpus entry (`{role["id"]: role["label"] for role in entry.roles}`). That is right for a
    scripted run, where the script *is* the corpus, and wrong here: on a live run the roles are
    **Copilot's**, invented from the founder's own three statements, and the fixture's *"A payroll
    manager"* is a label nothing on this page ever had. This repository has made that exact mistake
    once already, in S-010 -- *"asked a warm project for a fixture's role"* -- and the fix was the
    same one: read the label off the screen.
    """
    people = People(page, recorder, web_base)
    people.open(project_id)
    if page.locator(".role").count() == 0:
        people.switch_to_kinds_tab()
    cards = people.role_cards()
    with recorder.step("§1.4: the roles on the People page are the ones Copilot wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"role cards": ">= 1, each with a label"}, cards)
        assert cards, "Copilot's approved cards produced no role to ask anybody"
        assert cards[0]["label"].strip(), f"a role card has no label: {cards[0]!r}"
    label = cards[0]["label"]
    people.open_send_popup(label)
    people.fill_who(person_name, about=f"{label}, asked about one real occasion.")
    people.go_to_preview()
    url = people.generate_link(person_name.split()[0])
    people.close_popup()
    return url


def _answer_whatever_is_asked(browser, recorder, url: str, person_name: str) -> dict:
    """The stranger answers **the questions the page actually asks**, in their own browser context.

    `ParticipantPage.answer_as(person, entry)` resolves a corpus person's answers against the
    corpus's own anchor and selection prompts. On a live project there is no corpus: the anchors
    are the ones Copilot wrote, and every one of that method's `offers(prompt)` checks would fail
    silently into `skipped`, submitting an empty page. So this reads the rendered page instead --
    the same move S-004 makes with `_page_choice`, for the same reason: *what is offered is the
    page's to say.*

    A story in every anchor, and the first offered option in every selection under it. Nothing
    about which option is asserted anywhere; what leg two needs is a real answer on the wire.
    """
    context = browser.new_context()
    try:
        page = context.new_page()
        participant = ParticipantPage(page, recorder)
        participant.open(url)
        drawn = participant.anchors()
        with recorder.step("§2.1: the stranger's page carries the questions Copilot wrote",
                            party="participant", kind="assert") as h:
            h.record_assert({"anchors": ">= 1"}, drawn)
            assert drawn, f"the invitation link rendered no questions at all: {url}"
        answered, picked = [], []
        for anchor in drawn:
            prompt = anchor.get("prompt") or ""
            if not prompt:
                continue
            participant.tell_story(prompt, THE_STRANGER_SAYS)
            answered.append(prompt[:60])
            for selection in anchor.get("selections") or []:
                options = participant.options_for(selection, anchor_prompt=prompt)
                if not options:
                    continue
                participant.pick(selection, [options[0]], anchor_prompt=prompt)
                picked.append(f"{selection[:40]} -> {options[0]}")
        participant.submit()
        with recorder.step(f"§2.3: {person_name} sent their answers",
                            party="participant", kind="assert") as h:
            h.record_assert({"anchors answered": len(drawn)},
                             {"answered": answered, "picked": picked})
            assert answered, "the stranger typed nothing anywhere"
        return {"answered": answered, "picked": picked}
    finally:
        context.close()


def _web_base_of(page) -> str:
    from urllib.parse import urlsplit
    parts = urlsplit(page.url)
    return f"{parts.scheme}://{parts.netloc}"


# --------------------------------------------------------------------------------- the scenario

def test_s012_copilot_host_and_thinker_live(stack, founder_one, browser, run_dir):
    ready = copilot_host.readiness()
    if not ready["ok"]:
        pytest.skip(ready["reason"])

    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    cloud_base = f"http://localhost:{stack.cloud_port}"
    started = _now()
    passed = False
    context = browser.new_context()

    founder = fx.founder()
    # **The fixture supplies the founder's three statements and a person's name, and nothing
    # else.** Its beliefs, roles, anchors and typed answers are a *script's* data; on a live run
    # Copilot writes all four, so anything read from the fixture past this point would be a
    # question nobody asked.
    person_name = fx.people()[0].person
    write_generated(run_dir, inputs={"project": founder.project_name,
                                     "market": founder.market.country,
                                     "statements": {stage: founder.statement(stage)
                                                     for stage in STAGES},
                                     "person": person_name,
                                     "the stranger's story": THE_STRANGER_SAYS})

    keel_home = run_dir / "keel-home"
    copilot_home_dir = run_dir / "copilot-home"
    artifacts = run_dir / "copilot"
    model = os.environ.get("KEEL_COPILOT_MODEL") or RUNTIME_MODEL
    host_model = os.environ.get("KEEL_S012_HOST_MODEL") or HOST_MODEL
    # C-5 again: an unpinned run measures the router, not a model. It is still allowed -- spec 005
    # shipped exactly that -- but the bundle must never imply a pin that was refused. Both probes
    # are free (`-p ""` is refused before inference), so this costs nothing to be sure of.
    if not copilot_host.model_accepted(model):
        with recorder.step("C-5: `--model` refuses the runtime's slug on this account, so that "
                            "half of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": model, "whose": "the runtime's"}, {"pinned": None})
        model = None
    if not copilot_host.model_accepted(host_model):
        with recorder.step("C-5: `--model` refuses the host's slug on this account, so that half "
                            "of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": host_model, "whose": "the host's"}, {"pinned": None})
        host_model = None

    host = copilot_host.CopilotHost(home=copilot_home_dir, keel_home=keel_home,
                                    base_url=cloud_base, artifacts=artifacts,
                                    model=host_model, runtime_model=model)
    host.write_home_config()

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
                              "heartbeat": copilot_host.read_heartbeat(keel_home),
                              "KEEL_HOME": str(keel_home),
                              "COPILOT_HOME": str(copilot_home_dir)})
            assert not arrival["agent_connected"], (
                f"expected no agent connected yet, got {agent_line!r}")
            assert copilot_host.read_heartbeat(keel_home) is None, (
                "this run's KEEL_HOME already carries a heartbeat before Copilot has said a word")

        # =========================================================== LEG ONE: Copilot as the host
        with recorder.step("leg one: how this Copilot is authenticated, and which model it pins",
                            party="stack", kind="note") as h:
            h.record_wire({"COPILOT_HOME": str(copilot_home_dir)},
                           {"credential": copilot_host.credential_plan(),
                            "cli": ready["version"],
                            "pinned_model (the host's own --model)": host_model,
                            "pinned_model (the runtime's KEEL_COPILOT_MODEL)": model,
                            "why they differ": ("runs/DRIFT.md #59 -- the plan's default model "
                                                "answers correctly and keel-runtime cannot read "
                                                "it, so the host keeps the founder's own default "
                                                "and the runtime pins one it can read"),
                            "KEEL_RUNTIME_PATH in the child": "scrubbed (T-1)"})

        with recorder.step("leg one: the plugin is installed from the real marketplace with "
                            "Copilot's own two commands", party="stack", kind="assert") as h:
            added = host.add_marketplace()
            installed = host.install_plugin()
            h.record_wire({"marketplace": copilot_host.MARKETPLACE_SOURCE,
                            "plugin": copilot_host.PLUGIN_SPEC},
                           {"add": added, "install": installed,
                            "list": host.plugin_list()})
            assert added["exit_code"] == 0, (
                f"`copilot plugin marketplace add {copilot_host.MARKETPLACE_SOURCE}` failed: "
                f"{added['stderr'] or added['stdout']}")
            assert installed["exit_code"] == 0, (
                f"`copilot plugin install {copilot_host.PLUGIN_SPEC}` failed: "
                f"{installed['stderr'] or installed['stdout']}")

        with recorder.step("leg one: `copilot skill list` sees keel-connect, as a plugin skill",
                            party="stack", kind="assert") as h:
            listing = host.skill_list()
            hit = copilot_host.find_skill(listing["skills"])
            from_plugin = copilot_host.describes_a_plugin(hit)
            h.record_assert({"skill": copilot_host.SKILL_NAME, "source": "a plugin"},
                             {"found": hit, "from a plugin": from_plugin,
                              "raw": listing["raw"][:4000]})
            assert hit is not None, (
                f"`copilot skill list --json` does not name {copilot_host.SKILL_NAME!r} after the "
                f"plugin installed cleanly: {listing['raw'][:1000]!r}")
            assert from_plugin, (
                f"{copilot_host.SKILL_NAME!r} is visible but not as a plugin skill: {hit!r}")

        with recorder.step('leg one: the founder says "keel connect" to Copilot, once',
                            party="founder", kind="protocol") as h:
            first = copilot_host.say(host, THE_FOUNDER_SAYS, slug="connect-1")
            h.record_wire({"argv": first.argv, "cwd": str(artifacts)},
                           {"exit_code": first.exit_code, "model": first.model,
                            "premium_requests": first.premium_requests,
                            "tools": first.tools_used,
                            "reply": first.reply_text[:4000],
                            "stderr": first.stderr[:2000],
                            "transcript": str(first.transcript_path)})

        with recorder.step("leg one: a runtime is really there -- the heartbeat says "
                            "`awaiting_approval`", party="stack", kind="assert") as h:
            heartbeat = copilot_host.read_heartbeat(keel_home)
            h.record_assert({"state": copilot_host.STATE_AWAITING_APPROVAL,
                              "pid": "a live one", "agent_session_id": None},
                             heartbeat)
            assert heartbeat is not None, (
                "Copilot answered but no runtime heartbeat exists under this run's KEEL_HOME "
                f"({keel_home}) -- so nothing was started, whatever the reply said. Copilot said: "
                f"{first.reply_text[:400]!r}")
            assert heartbeat.get("state") == copilot_host.STATE_AWAITING_APPROVAL, (
                f"expected a runtime waiting for device approval, the heartbeat reads "
                f"{heartbeat.get('state')!r}")
            assert heartbeat.get("pid"), f"the heartbeat names no pid: {heartbeat!r}"

        with recorder.step("leg one: the launch log carries the code and the device page URL",
                            party="stack", kind="assert") as h:
            log_text = copilot_host.read_launch_log(keel_home)
            user_code = copilot_host.user_code_in(log_text)
            verification_uri = copilot_host.verification_uri_in(log_text)
            h.record_assert({"KEEL_USER_CODE=": "XXXX-XXXX",
                              "KEEL_VERIFICATION_URI=": f"{web_base}/connect"},
                             {"user_code": user_code, "verification_uri": verification_uri,
                              "log": log_text[:2000]})
            assert copilot_host.looks_like_a_user_code(user_code), (
                f"no `KEEL_USER_CODE=` line of the right shape in {keel_home}/"
                f"{copilot_host.LAUNCH_LOG_FILENAME}: {log_text[:500]!r}")
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
                f"the eval cloud does not know the code Copilot relayed ({user_code!r}): "
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
            second = copilot_host.say(host, THE_FOUNDER_SAYS, slug="connect-2")
            h.record_wire({"argv": second.argv},
                           {"exit_code": second.exit_code, "model": second.model,
                            "premium_requests": second.premium_requests,
                            "tools": second.tools_used,
                            "reply": second.reply_text[:4000],
                            "transcript": str(second.transcript_path)})

        with recorder.step("leg one: the runtime's own `status` says connected -- and Copilot's "
                            "reply says so too (loosely, and never on its own)",
                            party="stack", kind="assert") as h:
            status = _status()
            said_connected = copilot_host.mentions_connected(second.reply_text)
            h.record_assert({"running": True, "connected": True, "reply mentions connected": True},
                             {"status": status, "reply mentions connected": said_connected,
                              "reply": second.reply_text[:1000]})
            assert status.get("running"), f"the runtime is not running after approval: {status}"
            assert status.get("connected"), (
                f"the runtime never completed device approval: {status}")
            assert said_connected, (
                "the runtime is connected but Copilot's second reply never says so, so the skill's "
                f"`already_connected` was not relayed: {second.reply_text[:400]!r}")

        # =========================================================== LEG TWO: Copilot as the thinker
        with recorder.step("leg two: the runtime is on the Copilot executor, because the skill "
                            "passed `--host copilot` and nothing here passed `--executor`",
                            party="stack", kind="assert") as h:
            # **Read off the runtime's own startup line, not off `keel status`** (`runs/DRIFT.md`
            # #58). keel-cloud's contract defines `status.executor` as *"which executor this home
            # **would** run a job with ... resolved the same way `connect` resolves it"* -- the
            # caller's resolution, not the live process's. Asked from this harness (a Claude Code
            # session, so `CLAUDECODE=1` is in the environment `resolve_executor` reads) it
            # answers `claude` about a runtime whose own log says `KEEL_EXECUTOR=copilot`. That
            # is the first thing this scenario found and it is recorded, not adapted around: the
            # `status` reading goes into the bundle beside the one that knows.
            launched = copilot_host.launch_executor_in(
                copilot_host.read_launch_log(keel_home))
            status = _status()
            h.record_assert({"KEEL_EXECUTOR": EXPECTED_EXECUTOR, "source": "flag"},
                             {"the runtime's own startup line": launched,
                              "keel status (DRIFT #58: the caller's resolution, not this "
                              "runtime's)": {"executor": status.get("executor"),
                                             "executor_on_path": status.get("executor_on_path")},
                              "environment": status.get("environment")})
            assert launched is not None, (
                f"the runtime left no `KEEL_EXECUTOR=` line in {keel_home}/"
                f"{copilot_host.LAUNCH_LOG_FILENAME}, so which executor it chose is unknowable")
            assert launched["executor"] == EXPECTED_EXECUTOR, (
                f"the runtime is on {launched['executor']!r}, not {EXPECTED_EXECUTOR!r} -- the "
                f"skill's `--host copilot` line did not reach the runtime (SKILL.md, the D5 "
                f"exception)")
            assert launched.get("source") == "flag", (
                f"the runtime chose {EXPECTED_EXECUTOR!r} by {launched.get('source')!r} rather "
                f"than by an explicit term -- the skill is meant to *tell* it, so a run that "
                f"guessed right off an environment marker has not proven the skill's line works")
            assert status.get("environment") == f"localhost:{stack.cloud_port}", (
                f"the runtime names {status.get('environment')!r}, not this stack's Keel")

        with recorder.step("C-5: the pin the skill's own launch carried, exercised for the first "
                            "time", party="stack", kind="assert") as h:
            h.record_assert({"model": model}, {"the runtime's own startup line": launched})
            if model:
                assert launched.get("model") == model, (
                    f"the runtime launched with model {launched.get('model')!r} where this run "
                    f"pinned {model!r}: `KEEL_COPILOT_MODEL` did not reach the executor")

        project_id = create_project(page, recorder, web_base, founder)
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
        _answer_whatever_is_asked(browser, recorder, url, person_name)

        people.open(project_id)
        people.switch_to_who_tab()
        read_result = people.read_all_and_wait(timeout_s=420)
        with recorder.step("§1.6: Copilot read the answer, and the toast names what moved",
                            party="founder", kind="assert") as h:
            h.record_assert("a non-empty toast", read_result["toast_text"])
            assert read_result["toast_text"].strip(), (
                "the reading produced no toast, so nothing was read")

        overview = Overview(page, recorder, web_base)
        with recorder.step("§1.7: *What this says* -- the paragraph Copilot wrote, unasked",
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
                "no *What this says* paragraph after the reading -- the BRIEF job Copilot was "
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
            assert not refused, f"Copilot's work was refused: {refused}"
            assert not bad_jobs, f"a job did not complete: {bad_jobs}"
            assert not unsettled, f"an interaction never settled: {unsettled}"

        with recorder.step("what it cost: premium requests, from Copilot's own numbers and never "
                            "a dollar figure (C-7)", party="stack", kind="note") as h:
            rows = canary_mod.wait_for_envelopes(keel_home, timeout_s=180)
            job_premium = []
            for row in rows:
                envelope = row["envelope"] or {}
                job_premium.append({"job_id": row["job_id"],
                                     "premium_requests": envelope.get("premium_requests"),
                                     "num_turns": envelope.get("num_turns"),
                                     "is_error": envelope.get("is_error"),
                                     "executor": envelope.get("executor"),
                                     "model": envelope.get("model")})
            thinking = sum(float(r["premium_requests"] or 0) for r in job_premium)
            hosting = sum(float(run.premium_requests or 0) for run in (first, second))
            caps = canary_mod.cap_sources(stack.keel_runtime, keel_home)
            spend = {"host legs (copilot -p)": hosting,
                     "thinking (keel-runtime jobs)": thinking,
                     "total premium requests": hosting + thinking,
                     "jobs": len(rows),
                     "total_cost_usd": None,
                     "pinned_model (runtime)": model,
                     "pinned_model (host)": host_model,
                     "reported model (host)": second.model,
                     "cap sources": caps}
            h.record_wire({"per job": job_premium}, spend)
            (run_dir / "spend.json").write_text(json.dumps(
                {**spend, "per job": job_premium}, indent=2) + "\n")
            errored = [r for r in job_premium if r["is_error"]]
            assert not errored, f"a keel-runtime job envelope reports an error: {errored}"
            # The second, independent proof that **Copilot did the thinking**: every envelope the
            # runtime wrote names its own executor, and these were written per job by the process
            # that ran them. The startup line says which executor was chosen; this says which one
            # answered.
            wrong_host = [r for r in job_premium if r["executor"] != EXPECTED_EXECUTOR]
            assert job_premium, "the runtime wrote no job envelopes at all"
            assert not wrong_host, (
                f"a job was answered by an executor that is not {EXPECTED_EXECUTOR!r}: "
                f"{wrong_host}")
        print(f"\nS-012 premium requests: {hosting} hosting + {thinking} thinking = "
              f"{hosting + thinking} over {len(rows)} jobs; model {model or 'unpinned'}")

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
        finalize_run(run_dir, slug="s012-copilot-host-and-thinker", facts={}, passed=passed,
                     failed_step=recorder.failed_step, duration_s=_now() - started)
        print(f"\nrun bundle: {run_dir}")
