"""The rubric this eval judges by, versioned (spec 009 FR-014).

`MARKS_VERSION` is to this eval what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a
separate constant: an instruction-eval rubric change must never look like a scenario-scoring one.
**Bump it for any change to a mark, a metric definition, an alignment rule, the field list, or a
judgement call below** -- scores under different versions describe different rubrics and are not
comparable.

Judgement calls, append-only across every version, struck nowhere, because the rubric's history is
part of what a number means:

1.  **v1**: exact-match is over matched pairs only, so recall and exactness are not
    double-counted.
2.  **v1**: `measure.kind`/`measure.unit` are `n/a` for a Choice pair and excluded from the rate
    rather than counted as agreeing.
3.  **v1**: extra beliefs are counted and not marked. Over-generation is a finding first.
4.  **v1**: band equality is exact, because the phrase table is a fixture, not a judgement.
5.  **v1**: `GUESSED` precision and recall are mandatory beside accuracy, never optional.
6.  **v1**: a shape refusal, a schema-invalid answer and a rule refusal are three different lines.
7.  **v1**: the spread is reported; nothing is averaged before it is reported.
8.  **v1**: `founderPhrase` is a scored exact-match field, and absent-on-both-sides agrees, because
    a `CHOICE` has no phrase and requiring one would penalise every Choice belief.
9.  **v1**: a `NEEDS_INPUT` from an assumption screen whose statement was present is a failed case
    counted in the recall denominator, per design decision 14 -- not excluded, and not softened.
10. **v1**: the register is rendered and never scored. A metric here would look like evidence and
    be similarity to one hand-written example; the design requires a person, so the run records
    what the person said.
11. **v2** *(the founder's decision, 2026-09-06, after the baseline)*: **option lists are matched
    by meaning, not by words.** The corpus's option words are one reasonable phrasing of an answer
    space; `Q2` requires a belief's list to equal *its own selection's* list and never the
    corpus's. So a Choice pair with no structural overlap goes to the judge, which decides whether
    two lists describe the same answer space, and `expected` becomes a judged semantic match
    rather than a string comparison. The baseline's SOLUTION recall of 0/23 was what forced the
    question: the produced beliefs were about the same things in different words.
12. **v2**: `measure.per` is an eighth scored field. `Measure` is a three-field record and its own
    Javadoc says all three decide equality for `V2`, so a belief whose `per` differs expects a
    different number and an answer against it places nowhere. Nine of the baseline's fifteen
    matched interval pairs disagreed on `per` while scoring a clean sheet on every field that
    existed.
13. **v2**: an **unmeasured** mark is not a met mark. `refusals` read `0 / met` in the baseline
    because nothing had been shown to the aggregate yet; a mark with no measurement behind it now
    fails, as the other two already did for a `None`.
14. **v2**: the **judged fraction is reported on every run**, per case and overall, so a reader
    can discount a score by exactly the amount a model decided. Judgement call 11 buys recall at
    the cost of determinism, and this is the price tag.
15. **v4** *(spec 009 follow-on, 2026-09-07)*: **a new subject is a rubric change.** The `BRIEF`
    screen joins the reading and the assumptions, and a fourth mark joins the three:
    `brief_paragraphs`, the fraction of BRIEF cases that met **all four** of `instructions/brief.py`'s
    per-case marks (shape, coverage, register, source_material). Adding a subject changes what a
    passing run means even where every existing number is untouched, so scores before and after
    this bump are not comparable and the constant says so. (There is no v3 judgement call: v3
    bumped for keel-cloud's `(stage, anchorId)` pair, recorded in `score.score_reading` itself.)
16. **v4**: `brief_paragraphs` is **all four marks or nothing**, per case. A paragraph that is the
    right shape and names no verdict has not half-worked; it is a paragraph a founder would read
    and be misled by, and averaging the four marks together would hide exactly that.
22. **v6** *(the founder, 2026-09-12)*: **the rule-refusal mark is a rate, and shape refusals
    keep their zero.** A rule refusal is the product correcting the model (one extra call, nothing
    a founder sees), and an absolute zero made one invented unit in 1,179 case-runs a failed host.
    `rule_refusal_rate` is refusals over the answers the aggregate actually judged -- 63 on a full
    N=3 run -- so 0.02 reads "at most one correction across the corpus". `shape_refusals` stays
    an absolute zero: an envelope the runtime had to repair is a different failure. Applied to
    every host equally, and every earlier bundle can be re-scored under it without spending.
17. **v4**: **the paragraph is rendered as well as marked.** `brief.md`'s contract is one free-text
    field, so almost everything about a good paragraph is wording -- design §3.8's *cannot be
    checked by code*. The four marks cover only what `brief.md` states as a rule; the paragraph
    itself goes on `register.html` beside its entry's standings, unscored, for the same person who
    reads the anchors (judgement call 10, one subject wider). A mark this narrow can be wrong
    about a paragraph that is right, and the run has to leave the evidence for that.
18. **v4**: **the ordinary-English field names are exempt from `source_material`**, exactly as
    `evals/policy.py`'s judgement calls 1, 5 and 10 exempt theirs. `inside`, `outside`, `guessed`,
    `escaped`, `claims`, `beliefs`, `statement`, `heading`, `risk`, `verdict` and `drift` are
    words `brief.md` itself tells the model to write -- *"how many people landed **inside** the
    founder's own band"* is the instruction's own sentence -- so sweeping them would flag the
    paragraph the instruction asks for. What is swept is the shape a field name has and prose does
    not (`instructions/brief.py`'s `CONTEXT_FIELD_NAMES`).
19. **v4, and stated before the run rather than after it**: the BRIEF context this eval sends is
    production's in every field but one -- `median_reads`, which keel-cloud renders with
    `Measure.say` (rounding minutes to the nearest five above ten, climbing to the largest unit a
    person would use, putting the market's symbol on money). This repo does not own that
    arithmetic and will not keep a copy of it (`runs/DRIFT.md` #33/#36/#41/#44/#45, five times the
    same lesson), so the middle answer goes over in the corpus's own unit: `0.75 hours`, where
    production would say `45 minutes`.

    **`brief.md` names that exact string as a wrong way to say a number** -- *"you quote it
    exactly: 45 minutes, not forty-five minutes, not 0.75 hours"* -- so on the one corpus entry
    whose deciding line has a median (`01-countly`'s `P3`), a model is caught between the rule and
    the example. Whichever it does is worth recording, and the `coverage` mark scores it against
    the **rule**: quote what you were handed. A miss there is this eval's own limit, named here,
    and never a keel-cloud finding. What would close it is a context keel-cloud exports rather than
    one this repo assembles; that is a spec, not a rerun.
20. **v5** *(the first BRIEF run, `runs/20260908T004022Z-instructions`, $1.20 over seven real
    calls, and no rerun)*: **the design's verdict phrase is observed and never marked.** v4's
    `coverage` required each claim's verdict to be named in `FounderVoice`'s own words -- *holding
    up*, *not holding up*, *people disagree*, *still asking*. The run came back **0 of 7**, and
    reading the paragraphs showed the mark was wrong, not the instruction: `brief.md`'s own next
    sentence is *"Write them into ordinary sentences -- 'the problem is real', 'nobody pays
    anything like that today'"*, and that is exactly what came back (*"The problem is real"*,
    *"Your solution splits twice"*, *"On price the ground is firm"*). A code check on the words
    scores the paragraph the instruction asks for as a failure, which is judgement call 10's rule
    arriving from the other direction. So `verdict_phrasing` records per stage whether the phrase
    appears, `register.html` renders it beside the paragraph, and a person decides.
21. **v5**: **a split is counted from both sides.** v4's *no invented `N of M`* allowed only
    `inside` of `inside + outside`. `brief.md`'s third thing a paragraph says is *who the split is
    between*, named by the answers people gave -- *"six of nine had a member of staff take the
    delivery in; three took it in themselves"* -- so `outside` of the same total is a count the
    standings contain too. `02-compliancelog` was marked down for *6 of 10 rebuilt the draft they
    were handed*, which is its own line's `outside` read out exactly as asked.

    Both fixes were made **from that run's own bundle and re-scored without spending again**
    (`python -m instructions.rescore`), which is what a versioned rubric and a kept bundle are
    for. The v4 scorecard stays in the bundle beside the v5 one; neither overwrites the other.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

MARKS_VERSION = 6

DEFAULT_MARKS_PATH = Path(__file__).parent / "marks.toml"

DEFAULTS = {
    "anchoring_accuracy": 0.90,
    "golden_belief_recall": 0.80,
    "rule_refusal_rate": 0.02,
    "shape_refusals": 0,
    "brief_paragraphs": 1.00,
}


def load(path: Path | str | None = None) -> dict:
    path = Path(path) if path else DEFAULT_MARKS_PATH
    if not path.is_file():
        raise FileNotFoundError(f"no marks file at {path}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    marks = dict(DEFAULTS)
    marks.update(raw.get("marks") or {})
    return marks


def judge(totals: dict, marks: dict) -> dict:
    """Each mark against its number. A run passes only if all three are met.

    **An unmeasured mark is not a met mark** (judgement call 13). A `None` fails, and so does a
    refusal count that was never taken: the baseline of 2026-09-06 reported `refusals: 0, met:
    true` while nothing had been shown to the aggregate at all, which is the one way this rubric
    could flatter a run. `refusals_measured` says whether anybody asked.
    """
    accuracy = totals.get("anchoring_accuracy")
    recall = totals.get("golden_belief_recall")
    brief = totals.get("brief_paragraphs")
    brief_measured = bool(totals.get("brief_measured"))
    measured = bool(totals.get("refusals_measured"))
    refusals = sum((totals.get("refusals_by_rule") or {}).values())
    # v6 (judgement call 22): the rule-refusal mark is a rate over the answers the aggregate
    # judged -- `refusals_shown`, accepted plus refused -- never over case-runs that were never
    # shown to it. A run that shows the aggregate nothing has no rate and is unmeasured.
    shown = int(totals.get("refusals_shown") or 0)
    rate = (refusals / shown) if (measured and shown) else None
    shape = totals.get("shape_refusals")
    results = {
        "anchoring_accuracy": {
            "value": accuracy, "mark": marks["anchoring_accuracy"],
            "met": accuracy is not None and accuracy >= marks["anchoring_accuracy"]},
        "golden_belief_recall": {
            "value": recall, "mark": marks["golden_belief_recall"],
            "met": recall is not None and recall >= marks["golden_belief_recall"]},
        "refusals": {
            "value": refusals if measured else None, "measured": measured,
            "rate": rate, "shown": shown if measured else None,
            "mark": marks["rule_refusal_rate"],
            "met": measured and rate is not None and rate <= marks["rule_refusal_rate"]},
        "shape_refusals": {
            "value": shape if measured else None, "measured": measured,
            "mark": marks["shape_refusals"],
            "met": measured and shape is not None and shape <= marks["shape_refusals"]},
        # v4 (judgement calls 15-17): every BRIEF paragraph meeting all four of its own marks.
        # Unmeasured is not met here either -- a run filtered to one subject reports the other
        # subjects' marks as unmeasured and fails, which is the same rule `refusals` has had
        # since v2 and the reason a filtered run's verdict is never read as a pass.
        "brief_paragraphs": {
            "value": brief, "measured": brief_measured,
            "mark": marks["brief_paragraphs"],
            "met": brief_measured and brief is not None
                    and brief >= marks["brief_paragraphs"]},
    }
    results["passed"] = all(r["met"] for r in results.values() if isinstance(r, dict))
    return results
