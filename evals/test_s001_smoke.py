"""S-001, the smoke, rewritten for the measured-beliefs journey (spec 010 FR-008/FR-009, T024).

keel-cloud `canon/journeys.md` walked once, end to end, deterministically, against the real four
applications -- Postgres, keel-cloud, keel-web, and keel-runtime started through
keel-connect-skill's own script. No LLM: keel-runtime answers every inference job from the script
`harness/corpus_script.py` generates from this repo's own corpus-shaped fixture,
`evals/payroll_exceptions.yaml`, handed over as `KEEL_SCRIPT`.

**What the journey is now.** A founder arrives, connects a runtime by device code, names the
project, **says where it will sell**, frames the problem, the solution and the price, reviews each
one as a card of numbered lines with deal-breakers separated from what is worth knowing, **corrects
one line by saying what they meant**, invites people, watches strangers answer *one story and then
picks*, has the agent read them, sees where it stands, opens a card of strips and dots, opens one
dot, opens that person's whole page, and downloads.

**And then leaves** (spec `011-keel-disconnect`, keel-cloud
`canon/designs/keel-disconnect-design.md` §8.4). The smoke starts the runtime through
keel-connect-skill's own script, so it stops it through that skill's own *other* script,
`scripts/keel_disconnect.py` -- `disconnected`, the heartbeat gone, the landing reading *No agent
connected* again (one run, that line proven both ways), and `GET /v2/me` reading
`agent.connected` false **within two seconds**. That bound is the whole point: keel-cloud's
presence threshold is ninety seconds, so a slack bound would pass with no goodbye implemented at
all, and this is the only place in this repository where §4's goodbye is proven end to end.

Journey coverage (`canon/CANON.md`'s ledger, `canon/journeys.md` §3): this is the one module
proving §1.0 (arrival), §1.1 (the idea becomes three claims), §1.2 (review before spend), §1.4
(approve, then invite), §1.5 (waiting), §1.6 (reading what came back), §1.7 (where it stands),
§1.10 (the derived standing, now the download), §2.1 (the stranger's own page), §2.2 (answering;
everything skippable), §2.3 (thanks). §1.3, §1.8, §1.9, §2.4 are WAIVED in `canon/CANON.md` §5.

**The `§` citations are against a journeys.md that has not been amended for measured beliefs
yet** (spec's own Assumptions: keel-cloud owes that amendment, and `tests/test_journey_coverage.py`
is unchanged until its ledger gains the rows). They name the moment, not the model, and every one
of them still happens.
"""

from __future__ import annotations

import json
import re
import time

from evals import payroll_exceptions as fx
from evals.preludes import (answer_everyone, create_project, invite_everyone, stage_from_overview,
                             walk_stage)
from harness.browser import (MARKET_GROUPS, Auth, AnswersModal, Connect, CorrectionChat, Landing,
                              OpenedCard, Overview, People, PrintPage, ReviewCard, SaidBox, Shell)
from harness.connect import start_runtime_via_skill, stop_runtime_via_skill
from harness.corpus_script import inputs_json
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from stack import runtime as stack_runtime

STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: Whose whole page the founder opens from a dot (the answers modal is opened once, for one
#: person -- a fact registered for a hop the run never visits is a check with nothing to check).
MODAL_PERSON = "Dana Okafor"



# The agent line in both vocabularies -- *No agent connected* / *Agent connected* before keel-web
# spec 017, *Your AI isn't connected* / *Your AI is connected* after it (keel-cloud
# canon/designs/your-ai-design.md §3). Read either, so the matrix stays green across the deploys.
def _reads_not_connected(agent_line: str) -> bool:
    lowered = agent_line.lower()
    return "no agent" in lowered or "not connected" in lowered or "isn't connected" in lowered \
        or "isn’t connected" in lowered or "went away" in lowered


def _reads_connected(agent_line: str) -> bool:
    lowered = agent_line.lower()
    return "agent connected" in lowered or "ai is connected" in lowered

def test_s001_smoke(stack, founder_one, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    cloud_base = stack.cloud_base_url
    started = time.monotonic()
    passed = False
    modal_anchor = None
    context = browser.new_context()

    entry = fx.entry()
    founder = fx.founder()
    people_inputs = fx.people()
    script = fx.script()
    script_path = run_dir / "script.json"
    write_generated(run_dir, script=script.to_json(),
                    inputs=inputs_json(entry, founder, people_inputs))

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=15_000).json()

    try:
        page = context.new_page()

        # -------------------------------------------------------------------------------- §1.0
        # The Google round trip, through the stub issuer's own account picker (keel-cloud
        # google-sign-in-design.md §10.4). Setup is no longer a first-run branch: there is no
        # virgin instance to detect, so this scenario opens on L1 for every run.
        Auth(page, recorder, web_base).sign_in(founder_one)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()
        with recorder.step("§1.0: the landing reads no agent connected and is gated",
                            party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            gated = landing.is_gated()
            h.record_assert({"gated": True, "agent_connected": False},
                             {"gated": gated, "agent_connected": arrival["agent_connected"]})
            assert not arrival["agent_connected"], f"expected no agent connected yet, got {agent_line!r}"
            assert _reads_not_connected(agent_line), (
                f"expected 'No agent connected' / 'Your AI isn't connected' on the landing, got {agent_line!r}")

        with recorder.step("§1.0: keel-connect-skill starts the runtime with this run's own script",
                            party="stack", kind="assert") as h:
            # The script travels as `KEEL_SCRIPT` through `harness/connect.py`'s existing
            # `env_extra` (spec judgement call 2). The runtime is still only ever started through
            # keel-connect-skill's own script -- it is one of the four applications under referee,
            # and starting it any other way would leave it un-refereed.
            result = start_runtime_via_skill(stack, recorder,
                                              env_extra={"KEEL_SCRIPT": str(script_path)})
            # spec 012 FR-005: the outcome, and *which Keel it is about*. `environment` is on all
            # seven shapes of the script's contract now, and the runtime derives it from the base
            # URL it resolved -- so this one assertion says the skill reached this profile's own
            # keel-cloud and not the founder's, or the playground's, or none at all.
            expected_environment = f"localhost:{stack.cloud_port}"
            h.record_assert({"outcome": "authorization_started",
                              "environment": expected_environment},
                             {"outcome": result.get("outcome"),
                              "environment": result.get("environment")})
            assert result["outcome"] == "authorization_started", (
                f"expected a freshly-reset runtime home to need device approval, got {result}")
            assert result.get("environment") == expected_environment, (
                f"expected the skill to name this profile's own Keel, got "
                f"{result.get('environment')!r} (contract: `environment` is on all seven shapes)")

        connect = Connect(page, recorder)
        frame = connect.open(result["verification_uri"])
        with recorder.step("§1.0: the verification URI opens the device-decision frame",
                            party="founder", kind="assert") as h:
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()

        landing.visit()
        with recorder.step("§1.0: the landing reads agent connected",
                            party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            h.record_assert("agent connected", agent_line)
            assert _reads_connected(agent_line), (
                f"expected 'Agent connected' / 'Your AI is connected' on the landing, got {agent_line!r}")

        with recorder.step("§1.0 wire: GET /v2/me reads agent.connected within 30s",
                            party="stack", kind="assert") as h:
            deadline = time.monotonic() + 30
            me = _get("/v2/me")
            connected = bool((me.get("agent") or {}).get("connected"))
            while not connected and time.monotonic() < deadline:
                page.wait_for_timeout(1_000)
                me = _get("/v2/me")
                connected = bool((me.get("agent") or {}).get("connected"))
            h.record_assert(True, connected)
            assert connected, f"/v2/me never reported agent.connected: {me}"

        # -------------------------------------------------------- §1.1, the name and the market
        landing.name_project(founder.project_name)
        from harness.browser import MarketStep
        market_step = MarketStep(page, recorder, web_base)
        with recorder.step("§1.1: the market screen offers a list of countries, in three groups, "
                            "with the region optional", party="founder", kind="assert") as h:
            groups = market_step.country_groups()
            codes = market_step.country_codes()
            h.record_assert(list(MARKET_GROUPS), {"groups": groups, "countries": len(codes)})
            assert groups == list(MARKET_GROUPS), f"the country list's groups read {groups}"
            assert founder.market.country in codes, (
                f"{founder.market.country} is not on the list keel-web offers: {codes}")
            assert "optional" in market_step.region_placeholder().lower(), (
                f"the region box does not say it is optional: "
                f"{market_step.region_placeholder()!r}")

        market_step.fill(founder.market.country, founder.market.region)
        with recorder.step("§1.1: the market screen says, in the founder's own words, what the "
                            "people they ask will see", party="founder", kind="assert") as h:
            described = market_step.described_sentence()
            h.record_assert("units, register and currency, in a sentence", described)
            assert described, (
                "the market step showed no derived sentence at all -- `Market.described` is "
                "composed by keel-cloud (spec 030 FR-014) and read off `GET /v2/markets/{country}`")
            lowered = described.lower()
            assert "english" in lowered, described
            assert any(word in lowered for word in ("pound", "pence", "dollar", "cent")), described
        project_id = market_step.start()

        with recorder.step("§1.1 wire: the market persisted, and the server derived the language",
                            party="stack", kind="assert") as h:
            market = (_get(f"/v2/projects/{project_id}/overview") or {}).get("market") or {}
            h.record_assert({"country": founder.market.country, "region": founder.market.region,
                              "language": founder.market.language}, market)
            assert market.get("country") == founder.market.country, market
            assert (market.get("region") or None) == founder.market.region, (
                f"the region was left empty and came back as {market.get('region')!r} -- never "
                "the word 'null'")
            assert market.get("language") == founder.market.language, market

        # ------------------------------------------------------ §1.1/§1.2, the three review cards
        problem_card = walk_stage(page, recorder, _get, project_id, "PROBLEM",
                                  founder.problem, founder.problem, approve=False)
        _assert_review_card(recorder, problem_card, entry, "PROBLEM")

        # ------------------------------------------------------- §1.3-shaped: the correction turn
        correction = fx.CORRECTION
        before_lines = problem_card.lines()
        chat = CorrectionChat(page, recorder)
        with recorder.step("§1.2: the review card offers a way to say what you meant",
                            party="founder", kind="assert") as h:
            # The panel is **asked for** since keel-web `c807634` (a founder change from
            # playground testing, 2026-09-08): a *Change a line* link beside *Redo the whole
            # claim* opens it. The journey moment is unchanged -- a founder who disagrees with a
            # line has somewhere to say so -- so the assertion follows the product to the link,
            # and the founder clicks it before typing.
            offered = chat.is_offered()
            h.record_assert(True, offered)
            assert offered, (
                "there is no way to correct a line on the review card -- neither an open composer "
                "nor a *Change a line* link; a founder who disagrees with a line has nowhere to "
                "say so")
            chat.ask()
            assert chat.is_visible(), "*Change a line* did not open the composer it names"
        answered = chat.send(correction.message)
        problem_card.recapture("PROBLEM", slug="review-after-correction")
        after_lines = problem_card.lines()
        with recorder.step("§1.2: the agent answers in the same card, with that one line redone "
                            "and a before-and-after", party="agent", kind="assert") as h:
            h.record_assert({"agent answered": True, "changes": ">= 1"},
                             {"turns": [t["who"] for t in answered["turns"]],
                              "changes": answered["changes"]})
            assert any(turn["who"] == "agent" for turn in answered["turns"]), (
                f"the correction went unanswered: {answered['turns']}")
            assert answered["changes"], (
                "the agent answered with no before-and-after; the founder cannot see what moved")
        with recorder.step("§1.2: the correction changed the line it named and left the card "
                            "unapproved", party="founder", kind="assert") as h:
            changed = [(b["heading"], b["you_said"], a["you_said"])
                       for b, a in zip(before_lines, after_lines) if b["you_said"] != a["you_said"]]
            h.record_assert({"approved": False}, {"approved": problem_card.is_approved(),
                                                   "changed": changed})
            assert not problem_card.is_approved(), (
                "the card approved itself while answering a correction; that decision was never "
                "offered")

        problem_card.approve()
        with recorder.step("§1.2 wire: PROBLEM is framed and approved after approval",
                            party="stack", kind="assert") as h:
            after = stage_from_overview(_get(f"/v2/projects/{project_id}/overview"), "PROBLEM")
            h.record_assert({"framed": True, "approved": True}, after)
            assert after["framed"] and after["approved"], after
        problem_card.continue_onward()

        for stage in ("SOLUTION", "COMMERCIAL"):
            card = walk_stage(page, recorder, _get, project_id, stage,
                              founder.statement(stage), founder.statement(stage), approve=False)
            _assert_review_card(recorder, card, entry, stage)
            card.approve()
            card.continue_onward()

        # -------------------------------------------------------------------------------- §1.4
        shell = Shell(page, recorder)
        with recorder.step("§1.4: People unlocks once every framed card is approved",
                            party="founder", kind="assert") as h:
            locked = shell.people_locked()
            h.record_assert({"people_locked": False},
                             {"people_locked": locked, "why": shell.people_locked_reason()})
            assert not locked, "expected the side nav's People entry to unlock after the last approval"

        people = People(page, recorder, web_base)
        people.open(project_id)
        with recorder.step("§1.4: People opens on one card per role",
                            party="founder", kind="assert") as h:
            labels = " | ".join(card["label"] for card in people.role_cards())
            h.record_assert(fx.role_labels(), labels)
            for label in fx.role_labels():
                assert label in labels, f"expected the {label!r} role card, got {labels!r}"

        invite_urls = invite_everyone(page, recorder, project_id, entry, people_inputs, web_base)
        people.switch_to_who_tab()
        with recorder.step("§1.4/§1.5: the table lists everyone invited, none opened",
                            party="founder", kind="assert") as h:
            rows = people.table_rows()
            h.record_assert(len(people_inputs), len(rows))
            assert len(rows) == len(people_inputs), f"expected {len(people_inputs)} rows, got {len(rows)}"
            for row in rows:
                assert "not opened" in row["their_answer"].lower(), (
                    f"§1.5: expected {row['person']!r} to read 'Not opened', got {row['their_answer']!r}")

        # ------------------------------------------------- *What this says*, before any reading
        # §1.7 / FR-008: the paragraph is written by the `BRIEF` screen when a reading batch
        # finishes, so before the first reading there is none -- and keel-cloud says so in its own
        # words (`FounderVoice.whatThisSaysNote`) rather than leaving a block that reads as a bug.
        # This is the only moment it can be read: the paragraph is replaced whole and never
        # cleared, so every reading after the first leaves it standing.
        #
        # **Inverted, with the reason above it** (spec 027 D-5). keel-web spec 027 FR-020 took the
        # paragraph off the overview and FR-027 prints it on page 1 of the sheet, which prints **no
        # note at all** -- "a sheet does not explain to itself why a block it left out is missing".
        # So there is no screen left that draws the note, and the assertion could not move. Two of
        # its three findings stand where they stood, on the wire -- no paragraph, and a note
        # composed in keel-cloud's own words -- and the third is inverted: the overview draws no
        # *What this says* block, and the founder-facing sentence for *there is nothing yet* is the
        # download's own disabled state (FR-025 state 3).
        pre_overview = Overview(page, recorder, web_base)
        pre_overview.open(project_id)
        with recorder.step("§1.7: before the first reading the wire carries its own 'not yet' "
                            "line, the overview draws no paragraph, and there is nothing to hand "
                            "over yet", party="founder", kind="assert") as h:
            wire = _get(f"/v2/projects/{project_id}/overview") or {}
            note = wire.get("whatThisSaysNote")
            download = pre_overview.download_state()
            h.record_assert({"whatThisSays": None, "note": note,
                              "a *What this says* block on the overview": False,
                              "download enabled": False},
                             {"whatThisSays": wire.get("whatThisSays"), "note": note,
                              "a *What this says* block on the overview":
                                  pre_overview.carries_what_this_says(),
                              "download": download})
            assert wire.get("whatThisSays") is None, (
                f"a paragraph exists before anything was read: {wire.get('whatThisSays')!r}")
            assert note, (
                "the wire carries neither a paragraph nor a note, so nothing in the system has a "
                "word for the state the founder is in")
            assert not pre_overview.carries_what_this_says(), (
                "the overview still draws a *What this says* block; keel-web spec 027 FR-020 "
                "moved it to page 1 of the sheet and this screen is the deck now")
            assert download["label"].strip(), (
                "the deck's foot offers no download control at all -- not a disabled one either, "
                "which is the state keel-web FR-025 requires here")
            assert not download["enabled"], (
                f"the download is live before a single answer has been read: {download!r}")
            assert download["why"].strip(), (
                "the download is disabled and says nothing about why; a disabled control that "
                "does not say why is a bug the founder has to guess at (design §6.1 decision 5)")

        # ------------------------------------------------------------------------------ §2.1-3
        answer_everyone(browser, recorder, entry, people_inputs, invite_urls)

        # -------------------------------------------------------------------------------- §1.6
        people.open(project_id)
        for person in people_inputs:
            if person.person not in fx.JOURNEY_PEOPLE:
                continue
            first_name = person.person.split()[0]
            people.open_answers_popup(first_name)
            answers = people.answers_popup_text()
            with recorder.step(f"§1.6/§2.2: the founder reads {first_name}'s own words back",
                                party="founder", kind="assert") as h:
                joined = "\n".join(row["text"] for row in answers["qa"])
                missing = [a.text for a in person.written() if a.text not in joined]
                h.record_assert([a.text for a in person.written()], joined)
                assert not missing, f"expected {first_name}'s own words, missing {missing}"
            people.close_answers_popup()

        people.switch_to_who_tab()
        read_result = people.read_all_and_wait(timeout_s=max(120, 12 * len(people_inputs)))
        with recorder.step("§1.6: the toast names what moved", party="founder", kind="assert") as h:
            h.record_assert("non-empty toast", read_result["toast_text"])
            assert read_result["toast_text"].strip(), (
                "expected a non-empty toast after the agent read the new answers")
        people.follow_toast_link()

        # -------------------------------------------------------------------------------- §1.7
        # **The overview is the deck now** (keel-web spec 027 `brief-ship`). The three steps that
        # stood here each read the thing their subject became, and the paragraph's own step moved
        # to §1.10, where the sheet that prints it is opened:
        #
        # | what stood here | what it reads now |
        # |---|---|
        # | *N of T lines have answers*, off `.evidence__title` | the ship's own caption -- the project, the line count, the people asked |
        # | the legend's four counts, off `.legend` | the three panels' `HELD` and `DID NOT HOLD` rows, summed, plus `untested` off the wire (spec 027 D-6) |
        # | three `OverviewCard`s with a status, counts and a deal-breaker tally | three panels, each with a status word and one count line |
        overview = Overview(page, recorder, web_base)
        overview.open(project_id)
        with recorder.step("§1.7: the ship's caption counts every line and everybody asked",
                            party="founder", kind="assert") as h:
            counts = overview.ship_counts()
            h.record_assert((len(entry.beliefs), len(people_inputs)),
                             {"caption": overview.ship_caption(), "lines, asked": counts})
            assert overview.is_deck(), (
                "the overview is not the deck; with every stage approved and an answer read, "
                "`GuidedStep` here means keel-web is drawing the walk over a finished project")
            assert counts is not None, (
                f"no ship caption at all: {overview.ship_caption()!r}. It is what succeeded the "
                f"evidence bar's own project line (keel-web FR-007/FR-020).")
            assert counts[0] == len(entry.beliefs), (
                f"the caption counts {counts[0]} lines; the fixture has {len(entry.beliefs)}")
            assert counts[1] >= 1, f"the caption says nobody was asked: {counts}"

        with recorder.step("§1.7: the panels' own rows account for every line -- held, did not "
                            "hold, and the untested the deck draws nowhere",
                            party="founder", kind="assert") as h:
            # The legend's assertion -- *the four counts sum to every line there is* -- moved
            # rather than dropped. Opening the tails first is what makes the two sides comparable:
            # a part at rest shows at most three lines (keel-web FR-015), so a count over a closed
            # panel is a count of the budget and not of the evidence.
            overview.open_every_tail()
            panels = overview.panels()
            held = sum(len(Overview.lines_of(panel, Overview.PANEL_HELD)) for panel in panels)
            failed = sum(len(Overview.lines_of(panel, Overview.PANEL_DID_NOT_HOLD))
                         for panel in panels)
            standing = _get(f"/v2/projects/{project_id}/standing") or {}
            untested = len(standing.get("untested") or [])
            h.record_assert({"held + did not hold + untested": len(entry.beliefs)},
                             {"held": held, "did not hold": failed,
                              "untested, on the wire": untested,
                              "per panel": [{"stage": q["stage"], "word": q["word"],
                                              "count": q["count"]} for q in panels]})
            assert held + failed + untested == len(entry.beliefs), (
                f"the deck's rows and the wire's untested list account for "
                f"{held + failed + untested} lines, not the {len(entry.beliefs)} there are "
                f"(held {held}, did not hold {failed}, untested {untested})")
            assert held >= 1, (
                f"no line held after the reading, so nothing moved: {[q['count'] for q in panels]}")

        with recorder.step("§1.7: each panel carries its stage, a status word, its count line and "
                            "a deal-breaker tally where the stage has one",
                            party="founder", kind="assert") as h:
            panels = overview.panels()
            h.record_assert(3, len(panels))
            assert len(panels) == 3, [q["stage"] for q in panels]
            for panel in panels:
                assert panel["name"].strip(), f"{panel['stage']} panel does not name its stage"
                assert panel["word"].strip(), f"{panel['stage']} panel has no status word"
                assert "lines holding" in panel["count"], (
                    f"{panel['stage']} panel has no counts: {panel['count']!r}")
            # keel-web omits the deal-breaker clause entirely where a stage has none, rather than
            # printing *0 of 0* -- so the card-era `assert "deal-breaker" in card["must"]`, which
            # every card satisfied, becomes *at least one stage carries it*, which is the shape the
            # fixture guarantees.
            assert any("deal-breaker" in panel["count"] for panel in panels), (
                f"no panel carries a deal-breaker tally: {[q['count'] for q in panels]}")

        # ------------------------------------------------- §1.7, the opened card and one person
        expectation_of = {b.heading: b.type for b in entry.beliefs}
        opened = OpenedCard(page, recorder, web_base)
        # All three, in the walk's own order. The journey says *opens a card*; opening every one
        # is what makes the fact registry honest -- a `founderPhrase` declared to reach
        # `opened_card` and never looked for on its own stage's card is a check with nothing to
        # check, which is how S-002 once scored a fidelity miss for words nobody showed wrongly.
        for stage in ("SOLUTION", "COMMERCIAL"):
            opened.open(project_id, stage, expectations=expectation_of)
        opened.open(project_id, "PROBLEM", expectations=expectation_of)
        strips = opened.strips()
        with recorder.step("§1.7: the opened card's lines are collapsed, with the first open",
                            party="founder", kind="assert") as h:
            open_count = sum(1 for s in strips if s["open"])
            h.record_assert(1, open_count)
            assert strips, "the opened card rendered no strips at all"
            assert open_count == 1, (
                f"{open_count} of {len(strips)} lines rendered open; exactly one should")

        with recorder.step("§1.7: every strip carries its number, its *You said*, a status and "
                            "the question that produced it", party="founder", kind="assert") as h:
            problems = [s["heading"] for s in strips
                        if not (s["number"].strip() and s["you_said"].strip()
                                and s["status"].strip() and s["read_line"].strip())]
            h.record_assert([], problems)
            assert not problems, f"a strip is missing part of its own line: {problems}"

        with recorder.step("§1.7: a deal-breaker is marked as one",
                            party="founder", kind="assert") as h:
            load_bearing = {b.heading for b in entry.beliefs_for("PROBLEM")
                            if b.risk == "LOAD_BEARING"}
            marked = {s["heading"] for s in strips if s["deal_breaker"]}
            h.record_assert(sorted(load_bearing), sorted(marked))
            for heading in load_bearing:
                assert any(heading in seen for seen in marked), (
                    f"{heading!r} is load-bearing and the strip does not mark it a deal-breaker")

        dotted = next((s for s in strips if MODAL_PERSON in s["dots"]), None)
        # The anchor whose strip the modal is opened from -- the modal shows that stage's story,
        # and only that one, so the registry claims only that one.
        modal_anchor = (entry.anchors_for("PROBLEM") or [{}])[0].get("id")
        with recorder.step(f"§1.7: {MODAL_PERSON}'s own answer is a dot on a line",
                            party="founder", kind="assert") as h:
            h.record_assert(f"a dot labelled {MODAL_PERSON}",
                             {s["heading"]: s["dots"] for s in strips})
            assert dotted is not None, (
                f"no strip carries a mark for {MODAL_PERSON}; every anchored person is a dot")

        opened.ensure_open(dotted["heading"])
        opened.click_dot(dotted["heading"], MODAL_PERSON)
        said = SaidBox(page, recorder)
        with recorder.step("§1.7: the popover names the person, what they wrote and how it was "
                            "read", party="founder", kind="assert") as h:
            box = said.read()
            h.record_assert({"name": MODAL_PERSON, "read_as": "present"}, box)
            assert MODAL_PERSON.split()[0] in box["name"], box
            assert box["read_as"].strip(), "the popover does not say how the answer was read"
            assert box["see_all"].strip(), "the popover offers no way to see their full answers"

        said.see_all()
        modal = AnswersModal(page, recorder)
        with recorder.step("§1.7: the modal shows their story and every pick with the question "
                            "that asked it", party="founder", kind="assert") as h:
            body = modal.capture(MODAL_PERSON)
            h.record_assert({"story": "their own words", "picks": ">= 1"}, body)
            assert body["story"].strip(), "the modal shows no story in their own words"
            assert body["picks"], "the modal shows no picks at all"
            for pick in body["picks"]:
                assert pick["picked"].strip(), f"a pick with no answer: {pick}"
        modal.close(via="footer")

        # ------------------------------------------------------------------------------- §1.10
        overview.open(project_id)
        with recorder.step("§1.10: the overview offers Download, and by now it is live",
                            party="founder", kind="assert") as h:
            # The other side of the disabled control asserted before the first reading (keel-web
            # FR-025 states 1 and 3). The label has been *Download as PDF* and is *Download the
            # brief*; the words are recorded and the assertion is the door, not the copy.
            state = overview.download_state()
            h.record_assert({"label": "Download the brief", "enabled": True,
                              "href": f"/p/{project_id}/print"}, state)
            assert "download" in state["label"].lower(), (
                f"no Download door on the deck's foot: {state!r}")
            assert state["enabled"], (
                f"the download is still disabled after a reading: {state!r}")
            assert (state["href"] or "").endswith(f"/p/{project_id}/print"), (
                f"the download points at {state['href']!r}, not at this project's sheet")
        # **The founder's own click, and it opens a second tab now** (keel-web spec 027 FR-025:
        # `target="_blank"`, so the overview is still there behind the sheet). `stub_print()` is
        # called first and installs `window.print = () => {}` on the **context**, because a
        # page-scoped init script is not inherited by the tab the click opens -- and an unstubbed
        # `PrintRoute` raises a native dialog no locator can dismiss. `download()` answers whichever
        # page the sheet landed on, so this works against a deploy that navigates in place too.
        print_page = PrintPage(page, recorder, web_base)
        print_page.stub_print()
        sheet = overview.download()
        if sheet is not page:
            print_page = PrintPage(sheet, recorder, web_base)
        print_page.capture_here()
        # **Still five sheets, and not the same five.** Until spec 027 they were a title page, an
        # overview page and three stages; FR-030 retired the title page and FR-029 added the
        # evidence page, so the order is page 1, problem, solution, commercial, evidence (keel-web
        # SC-008). `title_page()` is re-pointed at page 1 and this assertion stands where it stood.
        with recorder.step("§1.10: the brief is five pages -- page 1, one per stage, and the "
                            "evidence", party="founder", kind="assert") as h:
            sheets = print_page.sheets()
            title = print_page.title_page()
            one = print_page.page_one()
            h.record_assert({"sheets": 5, "name": founder.project_name,
                              "page 1": "kicker, name, hand-off line, 16:9 block"},
                             {"sheets": len(sheets), "title": title,
                              "hand-off line": one["handoff"],
                              "16:9": print_page.block_169()})
            assert len(sheets) == 5, f"expected five sheets, got {len(sheets)}"
            assert founder.project_name in title["name"], title
            assert not print_page.has_founder_chrome(), (
                "the download page rendered the founder's own chrome; it is its own page")
            assert one["handoff"].strip(), (
                "page 1 carries no hand-off line. The twenty-eight words are addressed to whoever "
                "builds this, and FR-022 moved them from under the overview's button to the top "
                "of the thing being handed over.")
            assert print_page.block_169()["present"], (
                "page 1 drew no 16:9 block (FR-026) -- the one thing on the sheet a founder is "
                "meant to lift straight into a deck")

        # §1.7 / FR-008: the paragraph the `BRIEF` pipeline wrote, **verbatim** -- and since
        # keel-web spec 027 FR-027 it is page 1 of this sheet and not the overview, so the step
        # moved here, where the sheet is open, and lost nothing. Three different findings in one
        # step: keel-cloud ran the job and applied what came back, the "not yet" note stood down,
        # and keel-web rendered the server's own words. The check this replaced was *a heading and
        # twenty characters under it*, which the note satisfies by itself -- six green runs had
        # never once seen a paragraph, because no scripted run had ever produced one.
        brief_paragraph = script.screens["BRIEF"][0]["result"]["whatThisSays"]
        with recorder.step("§1.10: *What this says* is the agent's own paragraph, printed verbatim "
                            "on page 1 of the brief", party="founder", kind="assert") as h:
            wire = _get(f"/v2/projects/{project_id}/overview") or {}
            paragraph = print_page.what_this_says_paragraph()
            heading = print_page.what_this_says_heading()
            h.record_assert(brief_paragraph,
                             {"wire": wire.get("whatThisSays"), "page 1": paragraph,
                              "the heading above it": heading})
            assert wire.get("whatThisSays") == brief_paragraph, (
                "the BRIEF job never produced the paragraph -- the wire carries "
                f"{wire.get('whatThisSays')!r} where the script answered {brief_paragraph!r}")
            assert not wire.get("whatThisSaysNote"), (
                "the server still offers its 'not yet' note beside a paragraph that exists: "
                f"{wire.get('whatThisSaysNote')!r}")
            assert heading.strip(), (
                "page 1 prints the paragraph under no heading -- `WHAT_THIS_SAYS_HEADING` is what "
                "tells a reader what the paragraph is")
            assert paragraph == brief_paragraph, (
                f"page 1 prints {paragraph!r}, not the server's own {brief_paragraph!r}")

        with recorder.step("§1.10: the evidence page counts every line and names nobody",
                            party="founder", kind="assert") as h:
            # keel-web FR-029 / SC-009, principle **P8**: this is the page most likely to be
            # forwarded to an agency or an investor, and a table of names is a list that travels.
            # The names the sheet does print, on the stage pages' *In their words* blocks, are what
            # page 5 is swept for -- so the assertion needs no fixture of its own.
            evidence = print_page.evidence_page()
            named = [name for name in print_page.participant_names() if name.strip()]
            cells = " ".join(cell for row in evidence["rows"] for cell in row)
            leaked = sorted({name for name in named if name in cells})
            h.record_assert({"rows": len(entry.beliefs), "names on page 5": [],
                              "columns": list(PrintPage.EVIDENCE_COLUMNS)},
                             {"rows": len(evidence["rows"]), "columns": evidence["columns"],
                              "heading": evidence["heading"], "names on page 5": leaked,
                              "the names the sheet prints, on the stage pages": sorted(set(named))})
            assert evidence["heading"].strip(), "the evidence page carries no heading"
            assert len(evidence["rows"]) == len(entry.beliefs), (
                f"the evidence page draws {len(evidence['rows'])} rows for the "
                f"{len(entry.beliefs)} lines the fixture carries -- every line, or it is not the "
                f"evidence")
            assert not leaked, (
                f"page 5 names {leaked}. Principle P8: this is the page that gets forwarded, and "
                f"keel-web FR-029 puts no participant name on it.")
            assert not evidence["names"], (
                f"page 5 drew an *In their words* block with names in it: {evidence['names']}")

        # `table_columns()` is scoped to the **stage** pages since spec 027: page 5's evidence
        # table is a `table.ptab` too, so the sheet-wide read answered four rows and the fourth's
        # columns are the evidence page's own four (spec 027 D-3). The assertion below is
        # unchanged, and the evidence page's four are asserted in the step above.
        with recorder.step("§1.10: each stage's table names what it measures, what you said and "
                            "the answers", party="founder", kind="assert") as h:
            columns = print_page.table_columns()
            h.record_assert([list(print_page.COLUMNS)] * 3, columns)
            assert columns, "the download rendered no per-stage table"
            assert len(columns) == 3, (
                f"expected the three stage tables, got {len(columns)}: {columns}")
            # keel-web renders these headings upper-case in CSS, and `inner_text()` returns what
            # was rendered -- the words are the assertion, not their casing.
            wanted = [c.casefold() for c in print_page.COLUMNS]
            for row in columns:
                assert [c.casefold() for c in row[:3]] == wanted, row

        with recorder.step("§1.10: a stage starts on a fresh page, by the stylesheet's own rule",
                            party="founder", kind="assert") as h:
            rule = print_page.fresh_page_rule()
            h.record_assert("page", rule)
            assert rule == "page", (
                f"`.page + .page` carries break-before {rule!r}; a stage does not start fresh")

        # ----------------------------------------------------- §1.0, the other way: the door out
        # Spec `011-keel-disconnect` (keel-cloud `canon/designs/keel-disconnect-design.md` §8.4).
        # The smoke started the runtime through keel-connect-skill's own script; it stops it
        # through that skill's own *other* script, and never `python3 -m keel_runtime disconnect`.
        # Four assertions, and the fourth is the only place in this repository where §4's goodbye
        # is proven end to end.
        stopped = stop_runtime_via_skill(stack, recorder)
        gone_at = time.monotonic()
        with recorder.step("§1.0: \"keel disconnect\" answers `disconnected`, with the pid it "
                            "watched leave", party="founder", kind="assert") as h:
            h.record_assert({"outcome": "disconnected", "pid observed": True},
                             {"outcome": stopped.get("outcome"), "pid observed": "pid" in stopped,
                              "via": stopped.get("via")})
            assert stopped["outcome"] == "disconnected", (
                f"a running runtime stops with a proof it went, in the skill's own vocabulary; "
                f"got {stopped}")
            assert "pid" in stopped, (
                f"`disconnected` carries the pid that was signalled and observed gone: {stopped}")
            assert stopped.get("via") == stack_runtime.VIA_SKILL_SCRIPT, (
                f"the tail must go through the founder's own door, not the runtime's: {stopped}")

        with recorder.step("§1.0: the heartbeat that named the runtime is gone from the home",
                            party="stack", kind="assert") as h:
            heartbeat = stack_runtime.heartbeat_path(stack)
            h.record_assert({"runtime.heartbeat.json exists": False},
                             {"runtime.heartbeat.json exists": heartbeat.exists(),
                              "path": str(heartbeat)})
            assert not heartbeat.exists(), (
                f"`disconnected` was answered while {heartbeat} is still on disk -- the outcome "
                f"and the file it is derived from disagree (keel-runtime's D3)")

        with recorder.step("§1.0 wire: GET /v2/me reads agent.connected false within two seconds "
                            "-- the goodbye, and nothing else could do it that fast",
                            party="stack", kind="assert") as h:
            # **Two seconds is the entire assertion.** keel-cloud derives `agent.connected` from
            # `last_seen_at` against `keel.v2.connect.presence-threshold` (`PT90S`), so a
            # thirty-second bound -- which the connect leg above uses, correctly, for the other
            # direction -- would pass with no goodbye implemented at all. Only keel-runtime's last
            # act (design §4, invariant G3: sent *after* the heartbeat is removed) can put a false
            # here inside two seconds of the disconnect answering.
            #
            # Measured from the moment `disconnect` returned, which is why this step comes before
            # the landing check below rather than after it, as the design lists them: reloading a
            # page first would spend the whole budget on a browser navigation and leave the bound
            # proving nothing.
            deadline = gone_at + 2.0
            me = _get("/v2/me")
            connected = bool((me.get("agent") or {}).get("connected"))
            while connected and time.monotonic() < deadline:
                me = _get("/v2/me")
                connected = bool((me.get("agent") or {}).get("connected"))
            elapsed_ms = round((time.monotonic() - gone_at) * 1000)
            h.record_wire({"bound_s": 2.0}, {"elapsed_ms": elapsed_ms, "/v2/me": me})
            h.record_assert({"agent.connected": False, "within_s": 2.0},
                             {"agent.connected": connected, "elapsed_ms": elapsed_ms})
            assert not connected, (
                f"/v2/me still reads agent.connected {elapsed_ms} ms after the runtime said "
                f"goodbye. Either keel-runtime sent no goodbye (design §4) or keel-cloud did not "
                f"end the session (spec 033); this is the staleness window, not the goodbye: {me}")

        landing.visit()
        with recorder.step("§1.0: the landing reads *No agent connected* again -- one run, that "
                            "line proven both ways", party="founder", kind="assert") as h:
            agent_line = Shell(page, recorder).agent_line_text()
            h.record_assert("no agent connected", agent_line)
            assert _reads_not_connected(agent_line), (
                f"expected 'No agent connected' / 'Your AI isn't connected' on the landing after a "
                f"disconnect, got {agent_line!r}")

        stopped_again = stop_runtime_via_skill(stack, recorder)
        with recorder.step("§1.0: saying it twice is `not_running`, not an error",
                            party="founder", kind="assert") as h:
            h.record_assert({"outcome": "not_running"},
                             {"outcome": stopped_again.get("outcome")})
            assert stopped_again["outcome"] == "not_running", (
                f"the door out is idempotent by its own contract (D10); got {stopped_again}")

        with recorder.step("the fixture hashes exactly as it did when the run began",
                            party="stack", kind="assert") as h:
            fx.corpus().verify_unchanged()
            h.record_assert("unchanged", "unchanged")

        passed = True
    finally:
        context.close()
        finalize_run(run_dir, slug="s001-smoke",
                     facts=fx.facts(modal_person=MODAL_PERSON, modal_anchor=modal_anchor),
                     passed=passed, failed_step=recorder.failed_step,
                     duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")


def _assert_review_card(recorder, card, entry, stage: str) -> None:
    """§1.2, one card: the claim, the numbered lines, the deal-breaker rule line, *You said "…"*,
    the chips with the expected pick marked, the *asked indirectly* mark, and *What they'll be
    asked first*."""
    lines = card.lines()
    with recorder.step(f"§1.2: the {stage.lower()} card carries every line, numbered",
                        party="founder", kind="assert") as h:
        expected = [b.heading for b in entry.beliefs_for(stage)]
        got = [line["heading"] for line in lines]
        h.record_assert(expected, got)
        missing = [heading for heading in expected if not any(heading in seen for seen in got)]
        assert not missing, f"the {stage} card is missing lines: {missing}"
        unnumbered = [line["heading"] for line in lines if not line["number"].strip()]
        assert not unnumbered, f"a line has no number: {unnumbered}"

    with recorder.step(f"§1.2: {stage.lower()}'s deal-breakers are separated from what is worth "
                        "knowing, under their own rule lines", party="founder", kind="assert") as h:
        rule_lines = card.rule_lines()
        h.record_assert(["Deal-breakers · …", "Worth knowing · …"], rule_lines)
        beliefs = entry.beliefs_for(stage)
        if any(b.risk == "LOAD_BEARING" for b in beliefs):
            assert any("deal-breaker" in line.lower() for line in rule_lines), rule_lines
        if any(b.risk == "SUPPORTING" for b in beliefs):
            assert any("worth knowing" in line.lower() for line in rule_lines), rule_lines

    with recorder.step(f"§1.2: every {stage.lower()} line quotes the founder's own phrase and "
                        "offers a pick list", party="founder", kind="assert") as h:
        phrases = {b.heading: b.founder_phrase for b in entry.beliefs_for(stage) if b.founder_phrase}
        problems = []
        for line in lines:
            for heading, phrase in phrases.items():
                if heading in line["heading"] and phrase not in line["you_said"]:
                    problems.append({"line": heading, "phrase": phrase, "read": line["you_said"]})
            if not line["chips"]:
                problems.append({"line": line["heading"], "chips": "none"})
        h.record_assert([], problems)
        assert not problems, f"a line does not read as the design says it must: {problems}"

    with recorder.step(f"§1.2: the founder's expected pick is marked on every {stage.lower()} "
                        "CHOICE line", party="founder", kind="assert") as h:
        choices = {b.heading for b in entry.beliefs_for(stage) if b.type == "CHOICE"}
        unmarked = [line["heading"] for line in lines
                    if any(c in line["heading"] for c in choices)
                    and not any(chip["expected"] for chip in line["chips"])]
        h.record_assert([], unmarked)
        assert not unmarked, f"a CHOICE line marks no expected pick: {unmarked}"

    with recorder.step(f"§1.2: every PROXY line on {stage.lower()} is marked *asked indirectly*",
                        party="founder", kind="assert") as h:
        proxies = {b.heading for b in entry.beliefs_for(stage) if b.mark == "PROXY"}
        marked = {line["heading"] for line in lines if line["proxy"]}
        h.record_assert(sorted(proxies), sorted(marked))
        for heading in proxies:
            assert any(heading in seen for seen in marked), (
                f"{heading!r} is asked indirectly and the card does not say so")

    with recorder.step(f"§1.2: the {stage.lower()} card names what the person will be asked first",
                        party="founder", kind="assert") as h:
        asked_first = card.asked_first()
        h.record_assert("one story, then the picks", asked_first)
        assert asked_first, "no *what they'll be asked first* block on this review card"
        assert "story" in asked_first.lower() and "pick" in asked_first.lower(), asked_first
