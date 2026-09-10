"""S-006: `05-paidly`, the widest questionnaire (spec 010 US2, T030).

Five anchors across three stages, **two roles asked their own anchor sets and not each other's**,
twenty people, the corpus's only `SHARE` belief outside mulchrun, its one drift of `both` on
`P1` -- and `S6`, which has **exactly five** anchored people.

`S6` is the sharpest test in the corpus. `Project.FLOOR` is five: one fewer and the line is
`UNTESTED` whatever anyone said. So a screen that reads *Not asked yet* on `S6` is not a rounding
error, it is the floor being applied one person too early, and a screen that reads a real verdict
is the floor being applied exactly right. Nothing else in the corpus sits on that edge.
"""

from __future__ import annotations

from evals import corpus_scenario
from evals.corpus_scenario import STATUS_WORD

ENTRY_ID = "05-paidly"
FLOOR = 5


def _paidly_extras(ctx) -> None:
    recorder, entry = ctx["recorder"], ctx["entry"]
    standings = ctx["standings"]

    with recorder.step("T030: two roles, each asked their own anchors and not the other's",
                        party="participant", kind="assert") as h:
        roles = {p.role_id for p in ctx["people"]}
        by_role = {role: sorted({a.anchor_id for p in ctx["people"] if p.role_id == role
                                  for a in p.anchors}) for role in roles}
        h.record_assert("two disjoint anchor sets", by_role)
        assert len(roles) == 2, f"expected two roles, got {sorted(roles)}"
        sets = list(by_role.values())
        assert not (set(sets[0]) & set(sets[1])), (
            f"the two roles share an anchor, which the entry does not: {by_role}")

    with recorder.step("T030: twenty people answered", party="participant", kind="assert") as h:
        h.record_assert(20, len(ctx["people"]))
        assert len(ctx["people"]) == 20, f"expected twenty people, got {len(ctx['people'])}"

    with recorder.step(f"T030: S6 sits exactly on FLOOR = {FLOOR} and reads a real verdict",
                        party="stack", kind="assert") as h:
        stage_card = ctx["get"](f"/v2/projects/{ctx['project_id']}/stages/SOLUTION")
        beliefs = corpus_scenario.belief_by_heading(stage_card)
        standing = (beliefs.get(ctx["heading_of"]["S6"]) or {}).get("standing") or {}
        spoke = int(standing.get("inside") or 0) + int(standing.get("outside") or 0)
        h.record_assert({"spoke": FLOOR, "verdict": standings["S6"]["verdict"]},
                         {"spoke": spoke, "verdict": standing.get("verdict")})
        assert spoke == FLOOR, (
            f"S6 has {spoke} people who described an occasion; the entry puts it exactly on the "
            f"floor of {FLOOR}, and a different count means the run, not the aggregate, is wrong")
        assert standing.get("verdict") == standings["S6"]["verdict"], (
            f"S6 reads {standing.get('verdict')}; the entry says {standings['S6']['verdict']} -- "
            "the floor is *met*, not missed, and UNTESTED here would be it applied one person "
            "too early")

    with recorder.step("T030: P1's drift is `both`, and a `both` shows no direction",
                        party="founder", kind="assert") as h:
        want = corpus_scenario.status_text(standings["P1"]["verdict"], standings["P1"]["drift"],
                                            None)
        h.record_assert(want, standings["P1"]["drift"])
        assert standings["P1"]["drift"] == "both"
        assert want == STATUS_WORD[standings["P1"]["verdict"]], (
            "a drift of `both` points nowhere, so the status word carries no direction "
            f"(would have read {want!r})")


def test_s006_paidly(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s006-paidly", extra=_paidly_extras)
