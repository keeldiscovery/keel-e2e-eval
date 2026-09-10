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

ENTRY_ID = "01-countly"

# The mockup's own overview line, asserted literally (T027). Every number is derived from the
# entry's `expected.standings` by `corpus_scenario.expected_legend`, so this is a second, human
# statement of the same arithmetic -- if the two ever disagree, one of them was typed wrong, and
# that is exactly what a mockup of record is for.
MOCKUP_LEGEND = {"holding up": 9, "not holding up": 3, "people disagree": 6, "not tested": 0}
MOCKUP_LINES = (18, 18)


def _countly_extras(ctx) -> None:
    recorder, entry, overview = ctx["recorder"], ctx["entry"], ctx["overview"]

    with recorder.step("T027: the overview reads the mockup of record, number for number",
                        party="founder", kind="assert") as h:
        legend, lines = overview.legend(), overview.lines_with_answers()
        h.record_assert({"lines": MOCKUP_LINES, "legend": MOCKUP_LEGEND},
                         {"lines": lines, "legend": legend})
        assert lines == MOCKUP_LINES, f"the bar reads {lines}; the mockup says {MOCKUP_LINES}"
        assert legend == MOCKUP_LEGEND, f"the legend reads {legend}; the mockup says {MOCKUP_LEGEND}"

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
