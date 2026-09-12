"""S-005, S-006 and S-007's whole body (spec 010 FR-011..FR-015, T026).

**The entry id is the only thing that differs between the three scenario modules.** That is
FR-015, and it is the test of whether the generator was done right rather than a hope: if
`01-countly` needed one special case here, `05-paidly` would need two.

What the scenario does, in the founder's own order: builds a project on the entry's own market,
frames its three statements, reads each review card and checks the pick lists it offers against
the entry's `expected.buckets` **before approving anything**, invites one person per corpus
person, opens each of their links in an isolated context and types their story and their picks,
has the agent read them, and then asserts the entry's whole `expected` section -- `stages`,
`standings`, and the counts they roll up into -- **on the rendered overview, on the opened cards,
on the download page, and again on the wire beside them** (FR-014). A screen that agrees with a
wrong aggregate and a screen that disagrees with a right one are different findings, and a bundle
that only carried one of the two could not tell them apart.

It lives in `evals/` and not in `harness/` because it asserts. `harness/` is machinery.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from evals import corpus_facts
from evals.preludes import answer_everyone, create_project, invite_everyone, walk_stage
from harness import corpus_script
from harness.browser import Auth, Connect, Landing, OpenedCard, Overview, PrintPage, People, ReviewCard, Shell
from harness.connect import start_runtime_via_skill, stop_runtime
from stack import remote
from stack import runtime as stack_runtime
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder

STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# keel-web's own words for a verdict (`translate.ts`'s `measuredStatus`) and for a drift
# (`driftClause`). Named here, once, so three scenarios cannot drift apart on what "not holding
# up" is spelled like -- and so a copy change in keel-web is one edit here, not three.
STATUS_WORD = {
    "SUPPORTED": "Holding up",
    "CONTRADICTED": "Not holding up",
    "MIXED": "People disagree",
    "UNTESTED": "Not asked yet",
}
DRIFT_CLAUSE = {
    ("BELOW", False): "smaller than you think",
    ("ABOVE", False): "bigger than you think",
    # A rate is measured as the gap between the last two incidents, so a longer gap is *less
    # often* -- the direction reverses (design §6.4, `translate.ts`'s own `driftClause`).
    ("BELOW", True): "more often than you think",
    ("ABOVE", True): "less often than you think",
}
LEGEND_OF_VERDICT = {
    "SUPPORTED": "holding up",
    "CONTRADICTED": "not holding up",
    "MIXED": "people disagree",
    "UNTESTED": "not asked yet",
}


def status_text(verdict: str, drift: str | None, measure_kind: str | None) -> str:
    """What a status word must read, in full, for this verdict and this drift."""
    word = STATUS_WORD.get((verdict or "").upper(), "")
    clause = DRIFT_CLAUSE.get(((drift or "").upper(), (measure_kind or "").upper() == "RATE"))
    return f"{word} · {clause}" if clause else word


def belief_by_heading(stage_card: dict) -> dict[str, dict]:
    """Every belief on one `GET /v2/projects/{id}/stages/{stage}` read, by its own heading."""
    out: dict[str, dict] = {}
    for group in stage_card.get("groups") or []:
        for belief in (group.get("loadBearing") or []) + (group.get("supporting") or []):
            out[belief.get("heading") or belief.get("statement", "")] = belief
    return out


def expected_legend(entry) -> dict[str, int]:
    """The four counts the overview's legend must show, derived from the entry's own
    `expected.standings` and nothing else."""
    counts = {word: 0 for word in LEGEND_OF_VERDICT.values()}
    for standing in (entry.expected.get("standings") or {}).values():
        counts[LEGEND_OF_VERDICT[(standing.get("verdict") or "UNTESTED").upper()]] += 1
    return counts


def run(stack, founder_one, browser, run_dir, *, entry_id: str, slug: str,
        extra=None) -> None:
    """The whole scenario. `entry_id` is the only argument that differs between S-005, S-006 and
    S-007 (FR-015).

    `extra` is the one seam: a callable the scenario module passes to say the thing only *its*
    entry can say -- countly's mockup numbers, paidly's floor met exactly, mulchrun's dollars and
    miles. It is handed the whole context and asserts in the scenario's own recorder. Everything a
    second entry would also need belongs above it, not in it.
    """
    recorder = Recorder(run_dir)
    # Spec 017: the stack's own addresses -- `http://localhost:<port>` on the eval and playground
    # profiles, the twin's URLs on `remote` -- and the founder this run signs in as: the built-in
    # Eval Founder locally, a founder registered for this cell against the twin's gated chooser.
    # (The nightly of 2026-09-12, run 34660286884, found both hard-wired to localhost: S-005/6/7
    # rode the macOS x Claude cell for the first time and every one of them failed at sign-in with
    # `ERR_CONNECTION_REFUSED at http://localhost:443/login`.)
    web_base = stack.web_base_url
    cloud_base = stack.cloud_base_url
    cell_label = (f"{remote.cell_name()} · corpus {slug} · "
                  f"{time.strftime('%Y-%m-%d', time.gmtime())}")
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    started = time.monotonic()
    passed = False
    context = browser.new_context()

    corpus, entry = corpus_script.entry_for(stack.keel_cloud, entry_id)
    hashes_before = dict(corpus.hashes)
    script = corpus_script.generate(entry)
    founder = corpus_script.founder_inputs(entry)
    people_inputs = corpus_script.person_inputs(entry)
    script_path = run_dir / "script.json"
    write_generated(run_dir, script=script.to_json(),
                    inputs=corpus_script.inputs_json(entry, founder, people_inputs))

    standings = entry.expected.get("standings") or {}
    buckets = entry.expected.get("buckets") or {}
    stages_expected = entry.expected.get("stages") or {}
    by_id = {b.id: b for b in entry.beliefs}
    heading_of = {b.id: b.heading for b in entry.beliefs}
    measure_of = {b.id: (b.measure or {}).get("kind") for b in entry.beliefs}
    expectation_of = {b.heading: b.type for b in entry.beliefs}

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=15_000).json()

    try:
        page = context.new_page()
        Auth(page, recorder, web_base).sign_in(founder_one)

        # ------------------------------------------------------------------------ the runtime
        # The script travels as `KEEL_SCRIPT` through `harness/connect.py`'s existing `env_extra`
        # (spec judgement call 2): the env var touches one repo and leaves keel-connect-skill's
        # stable output contract alone. The runtime is still only ever started through that
        # skill's own script -- it is one of the four applications under referee.
        #
        # A runtime another scenario left running is holding *that* scenario's script, and the
        # connect skill reports `already_connected` rather than restarting it -- so it is stopped
        # first, the same way `make down` stops one. Each corpus scenario answers from its own
        # entry or it is not measuring that entry at all.
        if stack_runtime.status(stack).get("running"):
            stop_runtime(stack, recorder)
        if stack.is_remote:
            # On the twin this scenario signed in as a founder registered minutes ago, and the
            # profile's runtime home still holds the credential the PREVIOUS scenario's founder
            # approved: left alone, `keel connect` reconnects as that founder's device, this
            # founder's screens read "no AI connected", and the project-name field stays disabled
            # (the nightly of 2026-09-12, run 34662465285: S-005 green, then S-006 and S-007 red
            # at "founder names the project" with `<input disabled>`). A fresh home makes the
            # device this founder's, through the same approval S-005 already walks. Locally every
            # scenario is the one Eval Founder, and the saved credential is right as it is.
            with recorder.step("the runtime home is put back the way `make up` leaves it: this "
                                "founder's device, not the previous scenario's",
                                party="stack", kind="protocol") as h:
                stack_runtime.reset(stack)
                h.record_wire({"home": str(stack_runtime.home_dir(stack))},
                               {"after": stack_runtime.status(stack)})
        result = start_runtime_via_skill(stack, recorder,
                                          env_extra={"KEEL_SCRIPT": str(script_path)})
        landing = Landing(page, recorder, web_base)
        if result.get("outcome") == "authorization_started":
            connect = Connect(page, recorder)
            connect.open(result["verification_uri"])
            connect.approve()
            connect.wait_for_connected(timeout_s=30)
            connect.go_to_projects()
        landing.visit()

        # ------------------------------------------------------------------------- the market
        project_id = create_project(page, recorder, web_base, founder)
        with recorder.step(f"§1.1: {entry_id}'s market is the one the entry names",
                            party="stack", kind="assert") as h:
            market = (_get(f"/v2/projects/{project_id}/overview") or {}).get("market") or {}
            h.record_assert({"country": founder.market.country, "region": founder.market.region,
                              "language": founder.market.language}, market)
            assert market.get("country") == founder.market.country, (
                f"the market did not persist: expected {founder.market.country}, got {market}")
            assert (market.get("region") or None) == founder.market.region, (
                f"the region did not persist: expected {founder.market.region!r}, got {market}")
            assert market.get("language") == founder.market.language, (
                f"the server derived a different language: expected {founder.market.language}, "
                f"got {market}")

        # -------------------------------------------------------------- the three review cards
        for stage in STAGES:
            # `approve=False`: the review card is what this asserts, and an approved card is a
            # different screen entirely (strips, not lines). Read first, approve second.
            card = walk_stage(page, recorder, _get, project_id, stage, founder.statement(stage),
                              founder.statement(stage), approve=False)
            _assert_review_card(recorder, card, entry, stage, buckets)
            card.approve()
            card.continue_onward()

        # -------------------------------------------------------------- the people, and the read
        urls = invite_everyone(page, recorder, project_id, entry, people_inputs, web_base)

        # ------------------------------------------------- *What this says*, before any reading
        _assert_no_paragraph_yet(recorder, page, web_base, _get, project_id)

        # Read after each person, so the reading jobs arrive in the entry's own order and the
        # corpus's own anchorings land on the corpus's own people (`answer_everyone`'s note).
        typed = answer_everyone(browser, recorder, entry, people_inputs, urls,
                                 read_each=(page, project_id, web_base))
        with recorder.step("every person answered their own role's anchors and nobody else's",
                            party="participant", kind="assert") as h:
            strays = [row for row in typed if row["skipped"]]
            h.record_assert([], strays)
            assert not strays, (
                "a person was offered, or refused, something their role's anchor set does not "
                f"match: {strays}")

        # ------------------------------------------------------------------------- the overview
        overview = Overview(page, recorder, web_base)
        overview.open(project_id)
        _assert_overview(recorder, overview, entry, standings)
        _assert_what_this_says(recorder, overview, _get, project_id, script)
        if extra is not None:
            extra({"recorder": recorder, "page": page, "entry": entry, "overview": overview,
                   "project_id": project_id, "get": _get, "web_base": web_base,
                   "people": people_inputs, "founder": founder, "standings": standings,
                   "heading_of": heading_of, "browser": browser})

        # --------------------------------------------------------------------- the opened cards
        wire_standings: dict[str, dict] = {}
        for stage in STAGES:
            stage_card = _get(f"/v2/projects/{project_id}/stages/{stage}")
            wire_standings.update(belief_by_heading(stage_card))
            drifts = {heading_of[bid]: (standings.get(bid) or {}).get("drift", "").upper()
                      for bid in standings if by_id[bid].stage == stage}
            opened = OpenedCard(page, recorder, web_base)
            opened.open(project_id, stage, expectations=expectation_of, drifts=drifts)
            _assert_stage_card(recorder, opened, entry, stage, standings, stages_expected,
                               heading_of, measure_of, by_id)

        _assert_wire(recorder, entry, standings, heading_of, wire_standings)

        # ---------------------------------------------------------------------- the download
        print_page = PrintPage(page, recorder, web_base)
        print_page.open(project_id)
        _assert_download(recorder, print_page, entry, standings, heading_of)

        # ------------------------------------------------------- the corpus has not moved (FR-005)
        with recorder.step("the corpus hashes exactly as it did when the run began",
                            party="stack", kind="assert") as h:
            corpus.verify_unchanged()
            after = {path: corpus_script.corpus_reader._sha256(  # noqa: SLF001 - one reader (R6)
                __import__("pathlib").Path(path)) for path in hashes_before}
            h.record_assert(hashes_before, after)
            assert after == hashes_before, (
                "a corpus file moved while the run was in flight; this run has measured nothing")
        passed = True
    finally:
        context.close()
        finalize_run(run_dir, slug=slug,
                     facts=corpus_facts.facts_for(entry, modal_person=None),
                     passed=passed, failed_step=recorder.failed_step,
                     duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")


# ------------------------------------------------------------------------------------ assertions

def _assert_review_card(recorder, card, entry, stage, buckets) -> None:
    lines = card.lines()
    with recorder.step(f"§1.2: the {stage.lower()} review card carries every line the entry has",
                        party="founder", kind="assert") as h:
        expected_headings = [b.heading for b in entry.beliefs_for(stage)]
        got = [line["heading"] for line in lines]
        h.record_assert(expected_headings, got)
        missing = [heading for heading in expected_headings
                   if not any(heading in seen for seen in got)]
        assert not missing, f"the {stage} card is missing lines the entry carries: {missing}"

    with recorder.step(f"§1.2: every PROXY line on {stage.lower()} is marked *asked indirectly*",
                        party="founder", kind="assert") as h:
        proxies = {b.heading for b in entry.beliefs_for(stage) if b.mark == "PROXY"}
        marked = {line["heading"] for line in lines if line["proxy"]}
        h.record_assert(sorted(proxies), sorted(marked))
        for heading in proxies:
            assert any(heading in seen for seen in marked), (
                f"{heading!r} is a PROXY belief and the card does not mark it asked indirectly")

    with recorder.step(f"§1.2: {stage.lower()}'s deal-breakers are separated under their own rule "
                        "line", party="founder", kind="assert") as h:
        rule_lines = card.rule_lines()
        h.record_assert("a Deal-breakers rule line", rule_lines)
        if any(b.risk == "LOAD_BEARING" for b in entry.beliefs_for(stage)):
            assert any("deal-breaker" in line.lower() for line in rule_lines), (
                f"{stage} has load-bearing lines and no deal-breaker rule line: {rule_lines}")

    with recorder.step(f"§1.2: the {stage.lower()} card names what the person will be asked first",
                        party="founder", kind="assert") as h:
        asked_first = card.asked_first()
        h.record_assert("one story, then the picks", asked_first)
        assert asked_first, "no *what they'll be asked first* block on this review card"
        assert "story" in asked_first.lower(), asked_first
        assert "pick" in asked_first.lower(), asked_first

    # FR-013: the offered list equals the entry's own `expected.buckets`, in order.
    for belief in entry.beliefs_for(stage):
        wanted = buckets.get(belief.selection)
        if not wanted:
            continue
        with recorder.step(
                f"FR-013: line {belief.id} offers the entry's own pick list, in order",
                party="founder", kind="assert") as h:
            got = card.chip_labels(belief.heading)
            h.record_assert(list(wanted), got)
            assert got == list(wanted), (
                f"{belief.id} ({belief.selection}) offers {got}, the entry says {list(wanted)}")

    with recorder.step(f"§1.2: the founder's own phrase is quoted on every {stage.lower()} line",
                        party="founder", kind="assert") as h:
        phrases = {b.heading: b.founder_phrase for b in entry.beliefs_for(stage)
                   if b.founder_phrase}
        missing = []
        for line in lines:
            for heading, phrase in phrases.items():
                if heading in line["heading"] and phrase not in line["you_said"]:
                    missing.append({"line": heading, "phrase": phrase, "read": line["you_said"]})
        h.record_assert([], missing)
        assert not missing, f"a line does not quote the founder's own words: {missing}"


def _assert_overview(recorder, overview, entry, standings) -> None:
    with recorder.step("§1.7: the bar says how many lines have answers",
                        party="founder", kind="assert") as h:
        counts = overview.lines_with_answers()
        h.record_assert((len(standings), len(standings)), counts)
        assert counts is not None, f"no lines-have-answers bar: {overview.evidence_line()!r}"
        assert counts[1] == len(standings), (
            f"the bar counts {counts[1]} lines; the entry has {len(standings)}")
        # The bar's left-hand number is keel-cloud's own `haveEvidence`, and how it counts a line
        # nobody could answer (`05-paidly`'s `S6`, whose anchor most translators tap *hasn't
        # happened* on) is the aggregate's to decide, not this repo's to assert a formula for.
        # What is asserted here is that the bar counts every line and that the reading moved
        # something; the **per-belief standings below are the real check**, and they are exact.
        # Where an entry's own mockup fixes the number -- `01-countly`'s *18 of 18* -- its own
        # scenario module asserts it literally.
        assert counts[0] >= 1, f"no line has answers after the reading: {counts}"

    with recorder.step("§1.7: the legend's four counts are the entry's own, by verdict",
                        party="founder", kind="assert") as h:
        want = expected_legend(entry)
        got = overview.legend()
        h.record_assert(want, got)
        assert got == want, f"the legend reads {got}; the entry's standings say {want}"

    with recorder.step("§1.7: every stage card carries a status, its counts and its deal-breaker "
                        "tally", party="founder", kind="assert") as h:
        cards = overview.stage_cards()
        h.record_assert(3, len(cards))
        assert len(cards) == 3, f"expected three stage cards, got {[c['bet'] for c in cards]}"
        for card in cards:
            assert card["status"].strip(), f"{card['bet']} has no status word"
            assert card["counts"].strip(), f"{card['bet']} has no counts"
            assert "deal-breaker" in card["must"].lower(), (
                f"{card['bet']} has no deal-breaker tally: {card['must']!r}")


def _assert_no_paragraph_yet(recorder, page, web_base, get, project_id) -> None:
    """FR-008 / keel-cloud spec 030 FR-006: before anything has been read there is no paragraph,
    and the wire says so **in its own words** rather than leaving a block that reads as a bug.

    Read here, one moment before the first person's answer is read, because it is the only moment
    it can be read: `Project.whatThisSays` is written once and replaced whole, and every reading
    after the first one leaves it standing.
    """
    overview = Overview(page, recorder, web_base)
    overview.open(project_id)
    with recorder.step("§1.7: before the first reading, *What this says* carries the server's own "
                        "'not yet' line and no paragraph", party="founder", kind="assert") as h:
        wire = get(f"/v2/projects/{project_id}/overview") or {}
        note = wire.get("whatThisSaysNote")
        shown = overview.what_this_says_paragraph()
        heading = overview.what_this_says()
        h.record_assert({"whatThisSays": None, "note": note},
                         {"whatThisSays": wire.get("whatThisSays"), "on the screen": shown})
        assert wire.get("whatThisSays") is None, (
            "a paragraph exists before anything was read: " f"{wire.get('whatThisSays')!r}")
        assert note, (
            "the wire carries neither a paragraph nor a note, so the overview shows the founder "
            "nothing at all where the paragraph will be")
        assert "what this says" in heading.lower(), (
            f"no *What this says* heading on the overview at all: {heading!r}")
        assert shown == note, (
            f"the overview shows {shown!r} where the server's own note reads {note!r}")


def _assert_what_this_says(recorder, overview, get, project_id, script) -> None:
    """FR-008: the overview renders the paragraph the `BRIEF` pipeline wrote, **verbatim**.

    Three claims in one step, and they are different findings: that keel-cloud ran the job and
    applied what came back (the wire carries the scripted paragraph), that the "not yet" note has
    stood down (`whatThisSaysNote` is gone), and that keel-web rendered the server's words rather
    than words of its own (the screen equals the wire, character for character).

    Before this existed the check was *a heading and more than twenty characters under it*, which
    `whatThisSaysNote` satisfies on its own -- so six green runs at 5.0/5 had never once seen a
    paragraph, and 51 `BRIEF` jobs had failed unremarked behind
    `ReadingBatchService.sayWhatThisSays`'s own `catch`.
    """
    scripted = script.screens["BRIEF"][0]["result"]["whatThisSays"]
    with recorder.step("§1.7: *What this says* is the agent's own paragraph, rendered verbatim "
                        "from the wire", party="founder", kind="assert") as h:
        wire = get(f"/v2/projects/{project_id}/overview") or {}
        paragraph = overview.what_this_says_paragraph()
        h.record_assert(scripted, {"wire": wire.get("whatThisSays"), "screen": paragraph})
        assert wire.get("whatThisSays") == scripted, (
            "the BRIEF job never produced the overview's paragraph -- the wire carries "
            f"{wire.get('whatThisSays')!r} where the script answered {scripted!r}")
        assert not wire.get("whatThisSaysNote"), (
            "the server still offers its 'not yet' note beside a paragraph that exists: "
            f"{wire.get('whatThisSaysNote')!r}")
        assert paragraph == scripted, (
            f"the overview renders {paragraph!r}, not the server's own {scripted!r}")


def _assert_stage_card(recorder, opened, entry, stage, standings, stages_expected,
                       heading_of, measure_of, by_id) -> None:
    with recorder.step(f"§1.7: the {stage.lower()} card's own status is the entry's stage verdict",
                        party="founder", kind="assert") as h:
        want = stages_expected.get(stage)
        got = opened.status_word()
        h.record_assert(STATUS_WORD.get(want, want), got)
        assert STATUS_WORD.get(want, "") in got, (
            f"the {stage} card reads {got!r}; the entry says {want}")

    strips = {s["heading"]: s for s in opened.strips()}
    for belief_id, expected in standings.items():
        belief = by_id[belief_id]
        if belief.stage != stage:
            continue
        heading = heading_of[belief_id]
        strip = next((s for h2, s in strips.items() if heading in h2), None)
        with recorder.step(f"§1.7: line {belief_id} reads the standing the entry says it should",
                            party="founder", kind="assert") as h:
            want = status_text(expected.get("verdict"), expected.get("drift"),
                               measure_of.get(belief_id))
            h.record_assert(want, strip["status"] if strip else None)
            assert strip is not None, f"no strip on the {stage} card for {heading!r}"
            assert want in strip["status"], (
                f"{belief_id} reads {strip['status']!r}; the entry says {want!r}")

        with recorder.step(f"§1.7: line {belief_id}'s median is on the strip where the entry "
                            "records one", party="founder", kind="assert") as h:
            # **An absent `median` is not a claim that there is none.** The corpus's own checker
            # (`canon/designs/measured-beliefs/sim/check_corpus.py`) compares only the keys an
            # entry actually writes, and most lines record no median at all -- `01-countly` writes
            # one on three of eighteen. This spec's research R10 read the absence as an assertion
            # ("where `expected.standings[b]` gives no `median`, the screen must show none") and
            # that reading is wrong against the golden set it is reading: it fails `P1` for
            # showing a median that nine anchored people plainly have.
            #
            # R10's real point survives and is asserted where it bites: `NEVER` is positive
            # infinity, so a set containing one has no median at all. None of the three chosen
            # entries has an anchored `never` pick (`03-lullaby` and `04-linerly` do, and neither
            # is in this set), so there is no line here whose median must be absent -- and saying
            # so out loud is better than a check that passes because nothing exercises it.
            wants_median = "median" in expected
            h.record_assert({"entry records a median": wants_median},
                             {"strip shows a tick": strip["median"]})
            if wants_median:
                assert strip["median"], (
                    f"{belief_id}: the entry records a median of {expected['median']} and the "
                    "strip shows no tick at all")

        with recorder.step(f"§1.7: line {belief_id} names the question that produced it",
                            party="founder", kind="assert") as h:
            h.record_assert("Asked: “…” or *Same pick list as line N*", strip["read_line"])
            assert strip["read_line"].strip(), (
                f"{belief_id} carries no *Asked:* line and no *same pick list* note")


def _assert_wire(recorder, entry, standings, heading_of, wire) -> None:
    """FR-014: the same standings read off the wire beside the screen, so a screen agreeing with a
    wrong aggregate and a screen disagreeing with a right one are distinguishable in the bundle.
    The per-belief shape is `BeliefStanding` -- never spec 023's `Standing`, which is the founder
    brief and a different thing entirely."""
    with recorder.step("FR-014 wire: every BeliefStanding equals the entry's own",
                        party="stack", kind="assert") as h:
        mismatches = []
        for belief_id, expected in standings.items():
            got = (wire.get(heading_of[belief_id]) or {}).get("standing") or {}
            row = {"belief": belief_id}
            if (got.get("verdict") or "").upper() != (expected.get("verdict") or "").upper():
                row["verdict"] = {"wire": got.get("verdict"), "corpus": expected.get("verdict")}
            if not corpus_script.drift_equal(expected.get("drift"), got.get("drift")):
                row["drift"] = {"wire": got.get("drift"), "corpus": expected.get("drift")}
            for key in ("inside", "outside", "guessed", "escaped"):
                if key in expected and int(got.get(key) or 0) != int(expected[key]):
                    row[key] = {"wire": got.get(key), "corpus": expected[key]}
            if "median" in expected:
                wire_median = got.get("median")
                if wire_median is None or abs(float(wire_median) - float(expected["median"])) > 1e-6:
                    row["median"] = {"wire": wire_median, "corpus": expected["median"]}
            # An absent `median` is a key the entry did not record, not a claim of absence --
            # the corpus's own checker compares only the keys that are there (see the strip
            # assertion above for the whole reasoning).
            if len(row) > 1:
                mismatches.append(row)
        h.record_assert([], mismatches)
        assert not mismatches, (
            f"the aggregate disagrees with the frozen corpus: {json.dumps(mismatches, indent=2)}")

    with recorder.step("FR-034: `expected.placements`, asserted when the entry carries one",
                        party="stack", kind="assert") as h:
        placements = entry.expected.get("placements")
        h.record_assert("asserted when present", bool(placements))
        if placements:
            for belief_id, want in placements.items():
                testimony = (wire.get(heading_of[belief_id]) or {}).get("testimony") or []
                got = [row.get("placement") for row in testimony]
                assert got == list(want), f"{belief_id}: placements {got}, entry says {want}"


def _assert_download(recorder, print_page, entry, standings, heading_of) -> None:
    with recorder.step("§1.10: the download renders a title page, an overview page and one page "
                        "per stage", party="founder", kind="assert") as h:
        sheets = print_page.sheets()
        h.record_assert(5, len(sheets))
        assert len(sheets) == 5, f"expected five sheets, got {len(sheets)}"
        assert not print_page.has_founder_chrome(), (
            "the download page rendered the founder's own chrome; it is its own page")

    with recorder.step("§1.10: each stage's table names what it measures, what you said and the "
                        "answers", party="founder", kind="assert") as h:
        columns = print_page.table_columns()
        h.record_assert([list(print_page.COLUMNS)] * 3, columns)
        assert columns, "the download page rendered no per-stage table at all"
        wanted = [c.casefold() for c in print_page.COLUMNS]
        for row in columns:
            assert [c.casefold() for c in row[:3]] == wanted, row

    with recorder.step("§1.10: a stage starts on a fresh page, by the stylesheet's own rule",
                        party="founder", kind="assert") as h:
        rule = print_page.fresh_page_rule()
        h.record_assert("page", rule)
        assert rule == "page", (
            f"`.page + .page` carries break-before {rule!r}; a stage does not start fresh")

    with recorder.step("§1.10: the download quotes people in their own words",
                        party="founder", kind="assert") as h:
        quotes = print_page.quotes()
        h.record_assert(">= 1 quote", len(quotes))
        assert quotes, "no *In their words* quotes on any stage sheet"
