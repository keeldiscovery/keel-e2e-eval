"""S-011, the relay itself (relay-design.md §12 item 2's third scenario): proves what only the
relay's own mechanics can prove -- turn ordering under interleaving (a founder turn posted while
the agent's bridge is mid-poll), presence honesty through a real agent silence (the banner appears
once the bridge stops polling, and clears again once it resumes), a second bridge's lease refusal
reported plainly while the first bridge is left unaffected, and a payload-carrying playback turn
rendering as an actual `<table>` in the browser.

**No CANON.md ledger row, on purpose** (relay-design.md §12 item 2's own instruction, echoed by
§13.1's "S-011 added to the ledger only when implemented" -- read here as "the relay is plumbing
beneath every already-ledgered journey moment, not a new moment of its own"): this scenario proves
the transport, not a founder journey step, so `tests/test_journey_coverage.py`'s ledger is
untouched by this module and this comment stands in for a ledger citation that does not belong.

**Judgement call -- the presence-silence window.** Production's own `presence-threshold` default
is `PT90S` (design §14); waiting that out live in every `make eval-all` run would be a real cost
for no extra proof. `stack/cloud.py`'s `build_env` overrides it to `PT12S` for this stack only (a
same-binary environment override, the same standing precedent the MCP protocol override already
set) -- this test waits out the *shortened* window, proving the same honesty property (a banner
that agrees with the wire's own `connected` fact) without the 90-second cost. `poll-window` is
shortened alongside it (`PT3S`, same file) for the same reason: production's own default (`PT25S`)
would make the "resume" step's own idle poll take longer to return than the shortened threshold
above, itself starving the very presence it is trying to prove is honest.

**Two harness bugs found and fixed live against this exact scenario (2026-08-31), neither a
product gap.** First: `ChatPane.presence_banner_text()` used to read `.chat-presence` via a plain
`.first.inner_text()` -- Playwright auto-waits for a locator matching zero elements to attach
rather than returning "" immediately, and while genuinely connected (the element legitimately
never renders) that wait blocked long enough, on its own, to starve this test's own poll/post
calls of the chance to run -- which let presence go stale *because of the check*, not despite it.
Fixed with a `.count()` guard first (`harness/browser.py`). Second: the "resume" step's own idle
`AgentRelay.poll()` call parked for the server's full (then-unshortened) `poll-window` before
returning, handing control back to this synchronous test only after the freshness that poll's own
arrival had just caused was already older than the presence-threshold -- the `PT3S` override above
fixes it. Both findings, and the reasoning behind each fix, are the historical record now that
they're resolved; see harness/browser.py's and stack/cloud.py's own docstrings for the full
derivation.
"""

from __future__ import annotations

import threading
import time

from evals.recipes import arrive_and_create, open_founder_session, open_relay
from evals.scenario import Fact, Scenario
from harness.bridge import BridgeReply
from harness.browser import ChatPane
from harness.evidence import finalize_run
from harness.relay import AgentRelay, RelayError
from harness.steps import Recorder

PROJECT_NAME = "Relay Ordering Probe"
PROBLEM_STATEMENT = "Founders lose the thread switching between the terminal and the browser."
INTERLEAVED_TEXT = "And also -- does this thing actually keep up?"
PRESENCE_SILENCE_S = 15.0  # comfortably over the eval stack's own shortened PT12S threshold


class S011Relay(Scenario):
    """Only `project_name`/`problem_statement` are ever consulted (via `arrive_and_create`) -- this
    scenario proves the relay's own mechanics, not a discovery journey, so every other `Scenario`
    hook (frame/roles/assumptions/etc.) is deliberately left unimplemented and never called."""

    name = "S-011 relay"
    slug = "s011-relay"

    def project_name(self) -> str:
        return PROJECT_NAME

    def problem_statement(self) -> str:
        return PROBLEM_STATEMENT

    def facts(self) -> dict[str, Fact]:
        return {
            "interleaved_founder_turn": Fact(
                text=INTERLEAVED_TEXT, kind="statement",
                hops=["chat_turns"],
                absent_hops=["agent_echo", "stage_screen", "invite_screen", "participant_page",
                              "interpret_context", "brief", "recorded", "roles_context"],
            ),
        }


def test_s011_relay(stack, run_dir, browser, founder_credentials):
    recorder = Recorder(run_dir)
    scenario = S011Relay()
    passed = False
    started = time.monotonic()
    driver, founder, founder_context = open_founder_session(stack, founder_credentials, recorder,
                                                              scenario, browser)
    try:
        project_id = arrive_and_create(driver, founder, scenario)
        founder_relay, agent_relay = open_relay(driver, project_id)
        chat = ChatPane(founder.page, recorder, presence_reader=founder_relay.presence)

        # ---------------------------------------------------------- ordering under interleaving
        # The agent's bridge parks a real long-poll; the founder posts a SECOND turn while it is
        # mid-flight. Proves the wake mechanism (design §14's RelayWaitRegistry) and that ordering
        # survives the concurrency: the interleaved turn must read back after the opening's own
        # turns, in seq order, never reordered by which side's clock happened to tick first.
        poll_result: dict = {}

        def do_poll() -> None:
            poll_result["turns"], poll_result["cursor"] = agent_relay.poll(agent_relay.cursor)

        poll_thread = threading.Thread(target=do_poll)
        poll_thread.start()
        time.sleep(0.5)  # let the poll actually park server-side before the interleaved post lands
        founder_relay.post_turn(INTERLEAVED_TEXT)
        poll_thread.join(timeout=35)
        with recorder.step("the interleaved founder turn reads back in post order, never reordered",
                            party="agent", kind="assert") as h:
            turns = poll_result.get("turns", [])
            texts = [t.text for t in turns]
            seqs = [t.seq for t in turns]
            h.record_assert(f"{INTERLEAVED_TEXT!r} present, seqs ascending", {"texts": texts, "seqs": seqs})
            if INTERLEAVED_TEXT not in texts:
                h.fail(f"expected the interleaved turn to be read back by the parked poll, got {texts}")
                raise AssertionError(h.error)
            if seqs != sorted(seqs):
                h.fail(f"turns were not read back in seq order: {seqs}")
                raise AssertionError(h.error)

        agent_relay.post_turns([BridgeReply(text="Yep -- keeping up fine.").to_turn_input()])

        # ------------------------------------------------------ a second bridge's lease refusal
        # Done BEFORE the presence-silence window below, while the first bridge's own lease is
        # still fresh -- a lease that has gone stale (module docstring's shortened threshold) is,
        # correctly, no longer "live", and a second poller would be let in rather than refused.
        second_agent_relay = AgentRelay(driver.base_url, driver.session, project_id, recorder)
        with recorder.step("a second bridge is refused the relay lease plainly", party="agent",
                            kind="assert") as h:
            try:
                second_agent_relay.poll(cursor=0)
                h.fail("expected the second bridge's poll to be refused the lease, but it succeeded")
                raise AssertionError(h.error)
            except RelayError as err:
                h.record_assert("rule=relay-lease, a sentence-shaped remedy",
                                 {"rule": err.rule, "remedy": err.remedy})
                if err.rule != "relay-lease" or not (err.remedy or "").strip():
                    h.fail(f"expected a plain relay-lease refusal, got rule={err.rule!r} remedy={err.remedy!r}")
                    raise AssertionError(h.error)

        with recorder.step("the first bridge's own poll/post cycle is unaffected by the refusal",
                            party="agent", kind="assert") as h:
            founder_relay.post_turn("Still there?")
            turns, agent_relay.cursor = agent_relay.poll(agent_relay.cursor)
            h.record_assert("the first bridge still reads new founder turns", [t.text for t in turns])
            if "Still there?" not in [t.text for t in turns]:
                h.fail(f"expected the first bridge to keep working after the refusal, got {[t.text for t in turns]}")
                raise AssertionError(h.error)
            agent_relay.post_turns([BridgeReply(text="Still here.").to_turn_input()])

        # ------------------------------------------------------------------------------ presence
        founder.open_overview(project_id)
        with recorder.step("presence reads connected (no banner) right after a poll", party="founder",
                            kind="assert") as h:
            presence = founder_relay.presence()
            h.record_assert("connected=True", presence)
            if not presence.get("connected"):
                h.fail(f"expected the relay to report connected right after a poll, got {presence}")
                raise AssertionError(h.error)
            # The pane refetches presence on its own interval, not on every render -- wait for that
            # refetch to actually land rather than assume it already has (live-confirmed: it had
            # not, on the harness's own first attempt at this assertion).
            chat.wait_for_presence(connected=True)
            chat.read()
        with recorder.step("the chat pane shows no presence banner while the bridge is active",
                            party="founder", kind="assert") as h:
            banner = chat.presence_banner_text()
            h.record_assert("empty banner", banner)
            if banner:
                h.fail(f"expected no presence banner while connected, got {banner!r}")
                raise AssertionError(h.error)

        time.sleep(PRESENCE_SILENCE_S)  # the bridge stops polling -- a genuine silence, not a mock
        founder.open_overview(project_id)
        with recorder.step("presence reads disconnected once the bridge falls silent", party="founder",
                            kind="assert") as h:
            presence = founder_relay.presence()
            h.record_assert("connected=False", presence)
            if presence.get("connected"):
                h.fail(f"expected the relay to report disconnected after {PRESENCE_SILENCE_S}s of "
                       f"silence past the shortened threshold, got {presence}")
                raise AssertionError(h.error)
            chat.wait_for_presence(connected=False)
            chat.read()
        with recorder.step("the chat pane shows the disconnected banner honestly", party="founder",
                            kind="assert") as h:
            banner = chat.presence_banner_text()
            h.record_assert("non-empty banner naming how to start the agent", banner)
            if not banner.strip():
                h.fail("expected a disconnected presence banner after the silence, got none")
                raise AssertionError(h.error)

        # The bridge "resumes": one more poll clears the silence, and the banner clears with it.
        agent_relay.poll(agent_relay.cursor)
        founder.open_overview(project_id)
        chat.wait_for_presence(connected=True)
        with recorder.step("the banner clears once the bridge resumes polling", party="founder",
                            kind="assert") as h:
            presence = founder_relay.presence()
            banner = chat.presence_banner_text()
            h.record_assert("connected=True, empty banner", {"presence": presence, "banner": banner})
            if not presence.get("connected") or banner:
                h.fail(f"expected presence to recover after a resumed poll, got presence={presence}, "
                       f"banner={banner!r}")
                raise AssertionError(h.error)

        # --------------------------------------------------- playback-with-payload renders as a table
        founder_relay.post_turn("Who else could weigh in here?")
        turns, agent_relay.cursor = agent_relay.poll(agent_relay.cursor)
        agent_relay.post_turns([BridgeReply.playback(
            "Here's someone who could weigh in.",
            {"roles": [{"label": "Budget Sign-off", "settles": ["the commercial card"]}]},
        ).to_turn_input()])
        with recorder.step("a payload-carrying playback turn renders as a table in the chat pane",
                            party="founder", kind="assert") as h:
            founder.open_overview(project_id)
            chat.wait_for_turn_count(8)
            rows = chat.read()["playback_rows"]
            h.record_assert("a rendered <table> with a header + at least one role row", rows)
            if len(rows) < 2:
                h.fail(f"expected the playback to render as a table, got rows={rows}")
                raise AssertionError(h.error)

        # ---------------------------------------------------- every-door-opens, chat-turn edition
        # `GUI-C1` (policy v5) sweeps every chat-turn link for well-formedness; the live click-
        # through is a scenario assertion no static sweep can stand in for (`GUI-A3`'s own
        # precedent, `FounderBrowser.follow_display_url`), extended here to a link inside an agent
        # turn.
        overview_url = f"{founder.base_url}/{project_id}"
        founder_relay.post_turn("Where do I go to see this?")
        turns, agent_relay.cursor = agent_relay.poll(agent_relay.cursor)
        agent_relay.post_turns([BridgeReply(
            text=f"Right here: {overview_url}").to_turn_input()])
        with recorder.step("the door a chat turn carried actually opens", party="founder",
                            kind="assert") as h:
            chat.wait_for_turn_count(10)
            links = chat.agent_turn_links()
            h.record_assert(f"a link carrying {overview_url}", links)
            if overview_url not in links:
                h.fail(f"expected the chat turn's own link to render as {overview_url!r}, got {links}")
                raise AssertionError(h.error)
        chat.click_agent_turn_link(overview_url, project_id)

        passed = True
    finally:
        founder_context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
