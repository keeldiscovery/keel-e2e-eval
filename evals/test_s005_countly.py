"""S-005: `01-countly`, the mockup entry, driven through the real screens (spec 010 US2, T027-T029).

The approved mockup of 2026-09-07 says *"every number on the overview is Countly's, from the
frozen corpus"*, so this scenario asserts the mockup of record **literally**: eighteen beliefs
across three stages, twelve people, and *18 of 18 lines have answers · 9 holding up · 3 not
holding up · 6 people disagree · 0 not tested*.

It earns its place three more times over. It is the only entry with `CONTRADICTED` beliefs and the
only one whose PROBLEM stage sinks; it carries `RATE` and `TIME_SINCE`, two of the seven measure
kinds nothing else here reaches; and it holds the corpus's **only shared multi-select selection**
(`P4a` and `P4b`, both reading `S4`), which is the only exercise of design rule `Q4` anywhere --
and the only thing that proves a shared pick list does not make two lines share a verdict.
"""

from __future__ import annotations

from evals import corpus_scenario
from evals.corpus_scenario import STATUS_WORD
from harness.browser import Overview

ENTRY_ID = "01-countly"

# The mockup's own overview line, asserted literally (T027). Every number is derived from the
# entry's `expected.standings` by `corpus_scenario.expected_legend`, so this is a second, human
# statement of the same arithmetic -- if the two ever disagree, one of them was typed wrong, and
# that is exactly what a mockup of record is for.
#
# **The four counts are no longer side by side on any screen** (keel-web spec 027 FR-020 retired
# the legend with the evidence bar), so the same four numbers are stated three ways below and the
# step asserts each one against the party that can still answer for it. Not a number was dropped.
MOCKUP_LEGEND = {"holding up": 9, "not holding up": 3, "people disagree": 6, "not asked yet": 0}

#: The retired bar's own pair, *18 of 18 lines have answers*. Kept as the record of what the
#: superseded `measured-mock.html` `overview` frame pinned (keel-web D-12 deleted that baseline),
#: and no longer read off a screen.
MOCKUP_LINES = (18, 18)

#: The ship's caption, frame 2 of keel-web `specs/027-brief-ship/mockups/brief-ship-mock.html`:
#: *Countly · 18 lines · 12 asked*. The eighteen is `MOCKUP_LINES`' own total; the twelve is the
#: entry's own people, which is why the step reads it off `ctx["people"]` rather than typing it
#: twice.
MOCKUP_SHIP_LINES = 18

#: The same four counts as **the deck** draws them: `HELD` is `holdingUp`, `DID NOT HOLD` is
#: `notHoldingUp` and `peopleDisagree` together (bad news first, the wire's own two lists in
#: order), and `untested` is drawn nowhere at all -- which is why the third of these is asserted
#: against `GET /standing` and says so (spec 027 D-6).
MOCKUP_PANEL_ROWS = {"held": 9, "did_not_hold": 9, "untested": 0}


def _countly_extras(ctx) -> None:
    recorder, entry, overview = ctx["recorder"], ctx["entry"], ctx["overview"]

    with recorder.step("T027: the deck reads the mockup of record, number for number",
                        party="founder", kind="assert") as h:
        # Every tail opened first: a part at rest shows at most three lines (keel-web FR-015), so a
        # count taken over a closed panel is a count of the budget and not of the evidence.
        overview.open_every_tail()
        panels = overview.panels()
        held = sum(len(Overview.lines_of(panel, Overview.PANEL_HELD)) for panel in panels)
        failed = sum(len(Overview.lines_of(panel, Overview.PANEL_DID_NOT_HOLD))
                     for panel in panels)
        ship = overview.ship_counts()
        standing = ctx["get"](f"/v2/projects/{ctx['project_id']}/standing") or {}
        untested = len(standing.get("untested") or [])
        asked = len(ctx["people"])
        h.record_assert({"ship": (MOCKUP_SHIP_LINES, asked), **MOCKUP_PANEL_ROWS},
                         {"ship": ship, "held": held, "did_not_hold": failed,
                          "untested, on the wire": untested,
                          "the caption": overview.ship_caption(),
                          "per panel": [{"stage": q["stage"], "word": q["word"],
                                          "count": q["count"]} for q in panels]})
        assert ship == (MOCKUP_SHIP_LINES, asked), (
            f"the ship's caption reads {ship}; frame 2 says *Countly · {MOCKUP_SHIP_LINES} lines · "
            f"{asked} asked*")
        assert held == MOCKUP_PANEL_ROWS["held"], (
            f"the panels show {held} lines that held; the mockup says "
            f"{MOCKUP_PANEL_ROWS['held']}")
        assert failed == MOCKUP_PANEL_ROWS["did_not_hold"], (
            f"the panels show {failed} lines that did not hold; the mockup says "
            f"{MOCKUP_PANEL_ROWS['did_not_hold']} -- its 3 *not holding up* and 6 *people "
            f"disagree* together, which is the one part keel-web draws them in")
        # **The one count the deck draws nowhere**, asserted against the party that can still
        # answer for it. A line nobody could answer appears in no part, and `panel__count`'s
        # *N of M lines holding* carries it only inside its denominator.
        assert untested == MOCKUP_PANEL_ROWS["untested"], (
            f"`GET /standing` carries {untested} untested lines; the mockup says "
            f"{MOCKUP_PANEL_ROWS['untested']}")

    with recorder.step("T027: the mockup's four counts and the deck's three rows are the same four "
                        "numbers, stated twice", party="stack", kind="assert") as h:
        # The two human statements above, tied together, so neither can be edited alone -- the same
        # job `MOCKUP_LEGEND` vs `expected_legend(entry)` does one step down.
        derived = {"held": MOCKUP_LEGEND["holding up"],
                   "did_not_hold": MOCKUP_LEGEND["not holding up"]
                   + MOCKUP_LEGEND["people disagree"],
                   "untested": MOCKUP_LEGEND["not asked yet"]}
        h.record_assert(MOCKUP_PANEL_ROWS, derived)
        assert derived == MOCKUP_PANEL_ROWS, (
            f"the mockup's legend rolls up to {derived} and the deck's own rows are typed as "
            f"{MOCKUP_PANEL_ROWS} -- one of the two was typed wrong")
        assert sum(MOCKUP_LEGEND.values()) == MOCKUP_SHIP_LINES == MOCKUP_LINES[1], (
            f"the four counts sum to {sum(MOCKUP_LEGEND.values())}, the caption is typed as "
            f"{MOCKUP_SHIP_LINES} lines and the retired bar's own total was {MOCKUP_LINES[1]}")

    with recorder.step("T027: the corpus's own standings roll up to the mockup's own counts",
                        party="stack", kind="assert") as h:
        derived = corpus_scenario.expected_legend(entry)
        h.record_assert(MOCKUP_LEGEND, derived)
        assert derived == MOCKUP_LEGEND, (
            f"the entry's standings roll up to {derived}, the mockup of record says "
            f"{MOCKUP_LEGEND} -- one of the two was typed wrong")

    # T029 / acceptance 3a. `P4a` and `P4b` both name selection `S4`; the questionnaire asks it
    # **once**, and each line still carries its own standing from its own expected pick. A shared
    # selection never makes two lines share a verdict, and this is the only place in the whole
    # corpus that can prove it.
    with recorder.step("T029: the shared selection S4 is asked once and settles two lines "
                        "separately", party="stack", kind="assert") as h:
        stage_card = ctx["get"](f"/v2/projects/{ctx['project_id']}/stages/PROBLEM")
        beliefs = corpus_scenario.belief_by_heading(stage_card)
        p4a = beliefs.get(ctx["heading_of"]["P4a"]) or {}
        p4b = beliefs.get(ctx["heading_of"]["P4b"]) or {}
        h.record_assert({"same selection": True, "same verdict": False},
                         {"selectionId": [p4a.get("selectionId"), p4b.get("selectionId")],
                          "verdict": [(p4a.get("standing") or {}).get("verdict"),
                                       (p4b.get("standing") or {}).get("verdict")]})
        assert p4a.get("selectionId") and p4a.get("selectionId") == p4b.get("selectionId"), (
            "P4a and P4b must name one selection: "
            f"{p4a.get('selectionId')!r} vs {p4b.get('selectionId')!r}")
        want_a = ctx["standings"]["P4a"]["verdict"]
        want_b = ctx["standings"]["P4b"]["verdict"]
        assert (p4a.get("standing") or {}).get("verdict") == want_a
        assert (p4b.get("standing") or {}).get("verdict") == want_b
        assert want_a != want_b, (
            "the corpus itself expects these two to differ; if they ever agree the test has "
            "stopped proving anything")


def test_s005_countly(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s005-countly", extra=_countly_extras)
