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
from evals.preludes import (answer_everyone, create_project, invite_everyone,
                            own_ai_door, walk_stage)
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
    """The four counts by verdict, derived from the entry's own `expected.standings` and nothing
    else.

    **Kept exactly as it was, and it is no longer a legend.** keel-web spec 027 FR-020 took the
    four-word legend off the overview with the evidence bar, so nothing on a founder screen draws
    these four side by side any more. The arithmetic is unchanged and is still the entry's own, and
    `expected_panel_rows` below is how the deck is compared against it.
    """
    counts = {word: 0 for word in LEGEND_OF_VERDICT.values()}
    for standing in (entry.expected.get("standings") or {}).values():
        counts[LEGEND_OF_VERDICT[(standing.get("verdict") or "UNTESTED").upper()]] += 1
    return counts


def expected_panel_rows(entry) -> dict[str, int]:
    """The same four counts, arranged the way **the deck** draws them (keel-web spec 027 FR-011,
    FR-012).

    A panel has two parts and only two: `HELD`, which is `Standing.holdingUp`, and `DID NOT HOLD`,
    which is `notHoldingUp` **and** `peopleDisagree` together — bad news first, which is the wire's
    own two lists in order. So three of the four counts survive onto the screen, two of them added
    together.

    **`untested` is the fourth and the deck draws it nowhere**: a line nobody could answer appears
    in no part, and `panel__count`'s *N of M lines holding* carries it only inside its denominator.
    It is returned here so a caller asserts it against the wire rather than quietly dropping it
    (tasks.md **D-6**).
    """
    want = expected_legend(entry)
    return {"held": want["holding up"],
            "did_not_hold": want["not holding up"] + want["people disagree"],
            "untested": want["not asked yet"],
            "total": sum(want.values())}


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
        auth = Auth(page, recorder, web_base)

        # ------------------------------------------------------------------------ the runtime
        # **The runtime starts BEFORE the founder signs in, and that ordering is the product's,
        # not a convenience** (spec `024-keels-ai-cell`; keel-cloud spec 044 FR-014,
        # `GoogleSignIn.doorOf`). keel-cloud decides which AI an account runs on from the door it
        # was **created** through -- read back off the pre-login record's own stored `return_to`
        # -- and `/connect` is the only path that answers `OWN`. A bare `/` answers `KEEL`, grants
        # 1,500 credits, and once keel-cloud spec 045 lands hands that founder's jobs to Keel's
        # own Anthropic key. On the twin every one of these scenarios registers a brand-new
        # identity minutes before it signs in, so every one of them was creating an account on the
        # wrong door. It starts the runtime first now, takes the code the runtime printed, and
        # signs in at `/login?user_code=...` the way a first-time founder does.
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
        user_code = result.get("user_code")
        if result.get("outcome") == "authorization_started" and user_code:
            # The first-time flow, in the founder's own order: the code the runtime just printed
            # goes to `/login?user_code=...`, and the `return_to` that travels with it is
            # `/connect?user_code=...` -- the one path `GoogleSignIn.doorOf` reads as OWN.
            auth.sign_in_with_code(founder_one, user_code)
            connect = Connect(page, recorder)
            connect.open(result["verification_uri"])
            connect.approve()
            connect.wait_for_connected(timeout_s=30)
            connect.go_to_projects()
        else:
            # **No code, so no code story.** The runtime reconnected on a credential the home
            # already held (`connected` / `already_connected`), which is what a local profile
            # does: `make up` leaves a home behind and every scenario there is the one built-in
            # Eval Founder, whose account was created by whichever run first signed in. There is
            # nothing to carry and nothing to decide -- `ai_path` is immutable, so this sign-in
            # cannot move it either way -- and the ordinary door is what a returning founder uses.
            with recorder.step("no device code: the runtime reconnected on the credential its "
                                "home already held, so this founder signs in as a returning one",
                                party="stack", kind="note") as h:
                h.record_wire({"outcome": result.get("outcome")},
                               {"user_code": user_code,
                                "why it does not decide a door": (
                                    "keel-cloud reads the door only on the branch that CREATES "
                                    "the account (keel-cloud spec 044 FR-014); a returning "
                                    "founder keeps whatever their row already says")})
            auth.sign_in(founder_one)
        landing.visit()
        own_ai_door(page, recorder, stack, _get,
                    through_the_code_story=bool(user_code))

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

        # ------------------------------------------------------------------- the overview, the deck
        # **`_assert_what_this_says` is no longer called here, and this is the whole of why**:
        # keel-web spec 027 FR-020 took the paragraph off this screen and FR-027 prints it on page
        # 1 of the sheet. The step is unchanged and still asserts the same three findings; it is
        # called below, once the sheet is open, and is handed the `PrintPage` instead of the
        # `Overview`. The `print_page` is built here rather than there so an entry's own `extra`
        # can reach the sheet too -- `05-paidly` and `07-mulchrun` both sweep a founder screen, and
        # one of the screens they sweep is page 1 now.
        overview = Overview(page, recorder, web_base)
        overview.open(project_id)
        _assert_overview(recorder, overview, entry, standings, _get, project_id)
        print_page = PrintPage(page, recorder, web_base)
        if extra is not None:
            extra({"recorder": recorder, "page": page, "entry": entry, "overview": overview,
                   "print_page": print_page,
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
        print_page.open(project_id)
        _assert_download(recorder, print_page, entry, standings, heading_of)
        _assert_what_this_says(recorder, print_page, _get, project_id, script)

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


def _assert_overview(recorder, overview, entry, standings, get, project_id) -> None:
    """**The deck** (keel-web spec 027 `brief-ship`; keel-cloud `canon/designs/brief-page-design.md`
    §3). Three steps, and they are the three that stood here before, each reading the thing its
    subject became:

    | what stood here | what it reads now |
    |---|---|
    | *N of T lines have answers*, off `.evidence__title` | the ship's own caption — the project, the line count and the people asked |
    | the legend's four counts, off `.legend .up`/`.down`/`.split`/`.none` | the three panels' `HELD` and `DID NOT HOLD` rows, summed — and `untested` against the wire, because the deck draws it nowhere (**D-6**) |
    | three `OverviewCard`s, each with a status, its counts and its deal-breaker tally | three panels, each with a status word, a count line and its stage's name |

    Every tail is opened first (`open_every_tail`), because a part at rest shows at most three
    lines and a count taken over a closed panel would be a count of the budget rather than of the
    evidence. A budget moves a number; it never deletes one.
    """
    with recorder.step("§1.7: the ship's caption counts every line and everybody asked",
                        party="founder", kind="assert") as h:
        counts = overview.ship_counts()
        h.record_assert({"lines": len(standings)},
                         {"caption": overview.ship_caption(), "lines, asked": counts,
                          "the figure in one line": overview.ship_label()})
        assert overview.is_deck(), (
            "the overview is not the deck; every stage is approved and every answer is read, so "
            "`GuidedStep` here means keel-web is drawing the walk over a finished project")
        assert counts is not None, (
            f"no ship caption at all: {overview.ship_caption()!r}. It is what succeeded the "
            f"evidence bar's own project line (keel-web FR-007/FR-020).")
        assert counts[0] == len(standings), (
            f"the caption counts {counts[0]} lines; the entry has {len(standings)}")
        assert counts[1] >= 1, f"the caption says nobody was asked: {overview.ship_caption()!r}"

    with recorder.step("§1.7: the three panels' own rows are the entry's four counts, and the one "
                        "the deck never draws is asserted against the wire",
                        party="founder", kind="assert") as h:
        # **The legend's assertion, moved rather than dropped.** Opening the tails first is what
        # makes the two sides comparable: `HELD` and `DID NOT HOLD` each show three lines at rest.
        overview.open_every_tail()
        panels = overview.panels()
        held = sum(len(Overview.lines_of(panel, Overview.PANEL_HELD)) for panel in panels)
        failed = sum(len(Overview.lines_of(panel, Overview.PANEL_DID_NOT_HOLD))
                     for panel in panels)
        want = expected_panel_rows(entry)
        wire = get(f"/v2/projects/{project_id}/standing") or {}
        untested = len(wire.get("untested") or [])
        h.record_assert({"HELD rows": want["held"], "DID NOT HOLD rows": want["did_not_hold"],
                          "untested, on the wire": want["untested"]},
                         {"HELD rows": held, "DID NOT HOLD rows": failed,
                          "untested, on the wire": untested,
                          "the four counts by verdict, from the entry": expected_legend(entry),
                          "per panel": [{"stage": q["stage"], "word": q["word"],
                                          "count": q["count"]} for q in panels]})
        assert held == want["held"], (
            f"the panels show {held} lines that held; the entry's standings say {want['held']}")
        assert failed == want["did_not_hold"], (
            f"the panels show {failed} lines that did not hold; the entry's standings say "
            f"{want['did_not_hold']} -- `notHoldingUp` and `peopleDisagree` together, which is "
            f"the one part keel-web draws them in")
        assert untested == want["untested"], (
            f"`GET /standing` carries {untested} untested lines; the entry's standings say "
            f"{want['untested']}. This one is read off the wire and not off the screen because "
            f"the deck draws it nowhere -- a line nobody could answer is in no part, and the "
            f"count line carries it only inside its denominator (D-6).")

    with recorder.step("§1.7: every panel carries its stage, a status word and its own count line",
                        party="founder", kind="assert") as h:
        panels = overview.panels()
        bands = overview.bands()
        h.record_assert({"panels": 3, "bands": 3},
                         {"bands": bands, "panels": panels})
        assert len(panels) == 3, f"expected three panels, got {[q['stage'] for q in panels]}"
        assert len(bands) == 3, f"expected three bands, got {[b['stage'] for b in bands]}"
        assert {b["stage"] for b in bands} == {q["stage"] for q in panels} == set(STAGES), (
            f"the bands name {[b['stage'] for b in bands]} and the panels "
            f"{[q['stage'] for q in panels]}; there are three stages and one of each per stage")
        for panel in panels:
            assert panel["name"].strip(), f"{panel['stage']} panel does not name its stage"
            assert panel["word"].strip(), f"{panel['stage']} panel has no status word"
            assert "lines holding" in panel["count"], (
                f"{panel['stage']} panel has no *N of M lines holding* clause: "
                f"{panel['count']!r}")
            assert "answered" in panel["count"], (
                f"{panel['stage']} panel's count line does not say how many people answered: "
                f"{panel['count']!r}")
        for band in bands:
            assert band["wash"], f"{band['stage']} band carries no verdict class: {band!r}"
            assert band["label"].strip(), (
                f"{band['stage']} band has no accessible name, so its colour is the only carrier "
                f"of its verdict (keel-web FR-003)")
        # The deal-breaker tally the three cards each carried. keel-web omits the clause entirely
        # where a stage has no deal-breaker, rather than printing *0 of 0* -- so this asserts that
        # at least one stage carries it, which is the shape the corpus guarantees.
        assert any("deal-breaker" in panel["count"] for panel in panels), (
            f"no panel carries a deal-breaker tally at all: "
            f"{[q['count'] for q in panels]}")


def _assert_no_paragraph_yet(recorder, page, web_base, get, project_id) -> None:
    """**Inverted, with the reason above it** (keel-web spec 027 FR-020/FR-027; tasks.md **D-5**).

    What this asserted: before anything has been read there is no paragraph, and the wire says so
    **in its own words** (`FounderVoice.whatThisSaysNote`) rather than leaving a block that reads
    as a bug — and the overview shows that note, character for character.

    **There is no screen left that draws the note.** The paragraph moved to page 1 of the sheet,
    and `PrintRoute` prints no note at all: keel-web's own comment is that *"a sheet does not
    explain to itself why a block it left out is missing"*. So two of the three findings stand
    where they stood, on the wire — no paragraph, and a note composed in keel-cloud's own words —
    and the third is inverted: the overview must draw **no** *What this says* block, and the
    founder-facing sentence for *there is nothing yet* is the download's own disabled state,
    *Nothing to hand over yet*, with *The brief fills as your AI reads answers.* beside it
    (FR-025 state 3).

    Which is a better reading of the same moment: the note was a sentence about a paragraph the
    founder had not asked for, and the disabled control is a sentence about the thing they came to
    do.

    Still read here, one moment before the first answer is read, because it is still the only
    moment it can be read: `Project.whatThisSays` is written once and replaced whole, and every
    reading after the first leaves it standing.
    """
    overview = Overview(page, recorder, web_base)
    overview.open(project_id)
    with recorder.step("§1.7: before the first reading the wire carries its own 'not yet' line, "
                        "the overview draws no paragraph, and there is nothing to hand over yet",
                        party="founder", kind="assert") as h:
        wire = get(f"/v2/projects/{project_id}/overview") or {}
        note = wire.get("whatThisSaysNote")
        download = overview.download_state()
        h.record_assert({"whatThisSays": None, "note": note,
                          "a *What this says* block on the overview": False,
                          "download enabled": False},
                         {"whatThisSays": wire.get("whatThisSays"), "note": note,
                          "a *What this says* block on the overview":
                              overview.carries_what_this_says(),
                          "download": download})
        assert wire.get("whatThisSays") is None, (
            "a paragraph exists before anything was read: " f"{wire.get('whatThisSays')!r}")
        assert note, (
            "the wire carries neither a paragraph nor a note, so nothing in the system has a word "
            "for the state the founder is in")
        assert not overview.carries_what_this_says(), (
            "the overview still draws a *What this says* block; keel-web spec 027 FR-020 moved it "
            "to page 1 of the sheet and this screen is the deck now")
        assert download["label"].strip(), (
            "the deck's foot offers no download control at all -- not a disabled one either, "
            "which is the state keel-web FR-025 requires here")
        assert not download["enabled"], (
            f"the download is live before a single answer has been read: {download!r}")
        assert download["why"].strip(), (
            "the download is disabled and says nothing about why; a disabled control that does "
            "not say why is a bug the founder has to guess at (design §6.1 decision 5)")


def _assert_what_this_says(recorder, print_page, get, project_id, script) -> None:
    """FR-008, **on the page that draws it now**: the sheet's page 1 renders the paragraph the
    `BRIEF` pipeline wrote, **verbatim** (keel-web spec 027 FR-027).

    Three claims in one step, and they are different findings — unchanged from when this step read
    the overview. That keel-cloud ran the job and applied what came back (the wire carries the
    scripted paragraph), that the "not yet" note has stood down (`whatThisSaysNote` is gone), and
    that keel-web rendered the server's words rather than words of its own (the screen equals the
    wire, character for character).

    Before this existed the check was *a heading and more than twenty characters under it*, which
    `whatThisSaysNote` satisfies on its own — so six green runs at 5.0/5 had never once seen a
    paragraph, and 51 `BRIEF` jobs had failed unremarked behind
    `ReadingBatchService.sayWhatThisSays`'s own `catch`. That is why the equality is byte-for-byte,
    and it is why the reader is scoped to **page 1's own `p.pclaim`**: pages 2-4 each draw one too,
    carrying `StageSummary.claim`, and a sheet-wide read would have compared a stage's claim against
    the paragraph and passed or failed on the wrong sentence (tasks.md **D-2**).
    """
    scripted = script.screens["BRIEF"][0]["result"]["whatThisSays"]
    with recorder.step("§1.10: *What this says* is the agent's own paragraph, printed verbatim on "
                        "page 1 of the brief", party="founder", kind="assert") as h:
        wire = get(f"/v2/projects/{project_id}/overview") or {}
        paragraph = print_page.what_this_says_paragraph()
        heading = print_page.what_this_says_heading()
        h.record_assert(scripted, {"wire": wire.get("whatThisSays"), "page 1": paragraph,
                                    "the heading above it": heading})
        assert wire.get("whatThisSays") == scripted, (
            "the BRIEF job never produced the paragraph -- the wire carries "
            f"{wire.get('whatThisSays')!r} where the script answered {scripted!r}")
        assert not wire.get("whatThisSaysNote"), (
            "the server still offers its 'not yet' note beside a paragraph that exists: "
            f"{wire.get('whatThisSaysNote')!r}")
        assert heading.strip(), (
            "page 1 prints the paragraph under no heading -- `WHAT_THIS_SAYS_HEADING` is what "
            "tells a reader what the paragraph is")
        assert paragraph == scripted, (
            f"page 1 prints {paragraph!r}, not the server's own {scripted!r}")


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
    # **Still five sheets, and not the same five.** Until keel-web spec 027 they were a title page,
    # an overview page and three stages; FR-030 retired the title page ("a five-page document does
    # not need a cover made of metadata") and FR-029 added the evidence page, so the order is now
    # page 1, problem, solution, commercial, evidence (keel-web SC-008). The count assertion is
    # unchanged and the composition is asserted beside it, because a count alone never proved the
    # sheet had not changed -- which is exactly how this step went on passing over a rewrite.
    with recorder.step("§1.10: the brief is five pages -- page 1, one per stage, and the evidence",
                        party="founder", kind="assert") as h:
        sheets = print_page.sheets()
        one = print_page.page_one()
        h.record_assert({"sheets": 5, "page 1": "kicker, name, hand-off line, 16:9 block"},
                         {"sheets": len(sheets), "page 1": one,
                          "16:9": print_page.block_169()})
        assert len(sheets) == 5, f"expected five sheets, got {len(sheets)}"
        assert not print_page.has_founder_chrome(), (
            "the download page rendered the founder's own chrome; it is its own page")
        assert one["name"].strip(), (
            "page 1 is headed by nothing; `.ptitle` is retired and page 1 carries the name now "
            "(keel-web FR-030)")
        assert one["handoff"].strip(), (
            "page 1 carries no hand-off line. The twenty-eight words are addressed to whoever "
            "builds this, and FR-022 moved them from under the overview's button to the top of "
            "the thing being handed over.")
        assert print_page.block_169()["present"], (
            "page 1 drew no 16:9 block (FR-026) -- the one thing on the sheet a founder is meant "
            "to lift straight into a deck")

    with recorder.step("§1.10: the evidence page counts every line and names nobody",
                        party="founder", kind="assert") as h:
        # keel-web FR-029 / SC-009, and the principle is **P8** -- a stranger's words held on their
        # terms. This is the page most likely to be forwarded to an agency or an investor, and a
        # table of names is a list that travels. The names the sheet does print, on the stage
        # pages' *In their words* blocks, are what this step sweeps page 5 for -- so the assertion
        # needs no fixture of its own and cannot go stale against one.
        evidence = print_page.evidence_page()
        named = [name for name in print_page.participant_names() if name.strip()]
        cells = " ".join(cell for row in evidence["rows"] for cell in row)
        leaked = sorted({name for name in named if name in cells})
        h.record_assert({"rows": len(standings), "names on page 5": [],
                          "columns": list(PrintPage.EVIDENCE_COLUMNS)},
                         {"rows": len(evidence["rows"]), "columns": evidence["columns"],
                          "heading": evidence["heading"],
                          "names on page 5": leaked,
                          "the names the sheet prints, on the stage pages": sorted(set(named))})
        assert evidence["heading"].strip(), "the evidence page carries no heading"
        assert len(evidence["rows"]) == len(standings), (
            f"the evidence page draws {len(evidence['rows'])} rows for the {len(standings)} lines "
            f"the entry carries -- every line, or it is not the evidence")
        assert not leaked, (
            f"page 5 names {leaked}. Principle P8: this is the page that gets forwarded, and "
            f"keel-web FR-029 puts no participant name on it.")
        assert not evidence["names"], (
            f"page 5 drew an *In their words* block with names in it: {evidence['names']}")

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
