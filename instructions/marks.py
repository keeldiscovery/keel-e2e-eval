"""The rubric this eval judges by, versioned (spec 009 FR-014).

`MARKS_VERSION` is to this eval what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a
separate constant: an instruction-eval rubric change must never look like a scenario-scoring one.
**Bump it for any change to a mark, a metric definition, an alignment rule, the field list, or a
judgement call below** -- scores under different versions describe different rubrics and are not
comparable.

**`MARKS_VERSION` 9** (spec 029, 2026-10-07): the subjects are the eight screens of the vector
redesign, `golden_belief_recall` and `align.py` are retired, four marks are born and every one is
measured by code against the registry keel-cloud exports, and the corpus is read at revision 3.
Calls 28-36 are `specs/029-marks-v9-vectors/contracts/marks-v9.md` §3's, verbatim; calls 1-27 are
byte for byte what `master` `0165017` carried (`tests/fixtures/marks/calls-1-27.at-0165017.txt`).

**The corpus v9 judges, recorded 2026-10-07** (spec 029 US4.2, plan O-4). Revision 3's seven
entries, by sha256 -- the recorded revision under `tests/fixtures/corpus-r3/`, to be moved verbatim
into keel-cloud's canon, so a run reads these bytes either way:

    01-countly         6ed04bd84b464e8c48bbb1dff3922e71bcb3fc9f45b9f542ac933e85f67aa426
    02-compliancelog   177c787d5323d457b952b9ec2a3583b11c59f536982bf961288486291298c82a
    03-lullaby         347e44bce512e64b949aaa8a27cd8b6ba23e9024e9646b43b2bbf0215a9506bc
    04-linerly         3a557919fd01a974cf7d8f4e2226eaedaafb74498e95f1c32c4749bd71d052a2
    05-paidly          cbe618439d14f7725c22c0a8685e6e16a521a30bdd6708207b5a0b073040e12c
    06-repeatline      b0ecb45ee5d824e455e397ae52ecbd55420689b42b78b5ad9aa2e3715c244a75
    07-mulchrun        409b88d88aac05954609f322e1d349c18600cf02dedafa86d8106094c8ac38a0

Amended 2026-10-08: Lullaby's `mechanism_terms` drops `cot` (call 39), and every entry's model-written
sets gain `founder_calibration[d].labels`, the labels production sends as `founder_options`.

The corpus-wide `anchoring_accuracy` denominator, **counted, not estimated**: 106 people, less 13 who
answer No at the gate, 6 whose story carries a chip and 22 decision-makers on a B2B link (who are
never read) -- **65 reads at N=1, 195 at N=3**. A full run builds 138 model cases at N=1 (414 at N=3)
and 7 `COMPARE` rows; `compare_correctness` is 196 checks.

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
23. **v7** *(the founder, 2026-09-13)*: **the `shape` fault's length edge follows the contract**,
    which moved `whatThisSays` from 1 200 to 2 000 characters (keel-cloud
    `ScreenResponseContracts.WHAT_THIS_SAYS_MAX`, `runs/DRIFT.md` #68). The four marks and
    `brief_paragraphs`'s number are unchanged; a paragraph is judged against the edge production
    actually enforces. **Transcribed here at v8 from `marks.toml`, which has cited it since v7 while
    this list did not carry it** (spec 025 FR-003). It is a transcription and not a new call: no
    number and no rule moves with it, and the list is now what it says it is -- append-only and
    complete.
24. **v8** *(the founder, 2026-09-30; `one-occasion-once-design.md` §8.2)*: **the match key is the
    bare `anchorId` again, because the questionnaire is the project's.** v3 made it
    `(stage, anchorId)` when a stage owned its questionnaire and three of them each numbered from
    `A1`. One questionnaire per project makes `Q7` project-wide, so the pair carries no information
    the id does not, and a `stage` on an anchoring names nothing -- a merged occasion serves more
    than one stage's beliefs.
25. **v8** *(design §8.2)*: **a corpus anchor's `stage` becomes `stages`, a list, and is a label
    rather than a key.** `Entry.anchors_for(stage)` returns the anchors whose `stages` contain it,
    and one anchor may be returned for two stages. Scores before and after are not comparable and
    the constant says so.
26. **v8** *(design §6A.8)*: **a belief that reads another belief's measurement is aligned and
    counted as an ordinary belief.** Two lines reading one control are two lines in the recall
    denominator; the control they share is one, and `anchoring_accuracy` counts person-anchor pairs
    rather than controls, so it does not see the change.
27. **v8, and it is the correction 26 was written conditional on** *(design §6A.8: "That answer
    depends on one fact this pass did not verify ... Spec 049's first task is to check it")*: **the
    expectation is copied here, not by the server, because this eval scores the model's raw
    answer.** `runner.py` stores `response["result"]` and applies it to nothing; `score.py` hands
    `result["assumptions"]` straight to `align.align`; `produced_view` reads `belief["expectation"]`
    and a belief carrying only `reads` has none, so `structural_candidate` refuses it on `type`
    before a judge is ever asked. keel-cloud's validator is shelled for a verdict and never hands an
    applied `Assumption` back. So `align.resolve_reads` copies the referent's whole expectation out
    of the `earlier_lines` **this eval itself numbered and sent**, before alignment, and a reference
    that cannot be resolved is counted as `unresolved_reads` and left to fail to match. 26 holds
    *because of* this call, not in spite of it: with it, `align.FIELDS` does not change and the
    recall denominator does not change.
28. **v9**: **New subjects are a rubric change.** The five new screens of §1 replace `*_ASSUMPTIONS`
    and `QUESTIONS`; `INTERPRET` keeps its constant and is narrowed to the gate story (one judgement
    a respondent); the three interpretation screens are rendered and never scored — their leaks are
    rule refusals (`X1` / `P1` / `M1`) feeding `rule_refusal_rate` only (call 10). Scores before and
    after are not comparable.
29. **v9**: **`golden_belief_recall` is retired, and `align.py` with it.** A calibration answer is a
    typed pick against the registry; the model writes the question, the engine writes the belief.
    There is no structure to align, no option list to overlap, no tie to break. The golden is the
    registry slice, not text.
30. **v9**: **`dimension_coverage` is absolute.** One question per dimension, both screens;
    denominators per §2.1. A plan the eval built by code from `founder_calibration` is what the
    respondent screen is handed, exactly as production's `EVIDENCE_PLAN` would.
31. **v9**: **`option_validity` is code, and 1.00 is honest only because the registry fixes the
    codes.** The mark checks the mapping, not the invention.
32. **v9**: **`no_leak`'s list is derived from the corpus's golden mechanism, never from the live
    `SOLUTION_MECHANISM` output** (the ruler must not move with the subject); ties are inflection
    collisions with the problem's own words and go to the judge; every other hit is a fault.
33. **v9**: **One anchoring judgement per respondent.** Gate-No respondents are outside every
    denominator; **amended 2026-10-07 (decision 10):** a chipped story is set `GUESSED` by code with
    no call and is OUTSIDE the denominator too — only un-chipped stories are read. Number unchanged.
34. **v9**: **`compare_correctness` spends nothing and is measured on `DRY=1`.** Status + drift
    marked; counts reported; an export without the engine leaves it unmeasured, which fails (call
    13). This repo keeps no copy of the arithmetic (DRIFT #33/#36/#41/#44/#45).
35. **v9**: **`brief_paragraphs` gains `no_claim_words`**, scoped to the sentence naming a `BAR_SET`
    or `NOT_TESTED_BY_DESIGN` dimension; the deciding line is the worst deal-breaker; all five or
    nothing.
36. **v9**: **`rule_refusal_rate` keeps 0.02 while its denominator triples**; the new reading is
    recorded in `marks.toml` and is the founder's decision 1, not a quiet tightening.
37. **v9, amended before any run of record** *(the founder's decision 32, 2026-10-08; screen
    `runs/20261008T001657Z-instructions`)*: **a belief phrase may equal its label.** C4 in
    `option_validity` no longer faults a phrase that is its label after `normalise` -- keel-cloud
    062 accepts it, and a mark that refuses what the product accepts measures the eval, not the
    instruction. C4 still faults an empty phrase, one over 120 characters, and one carrying a
    not-sure word. `MARKS_VERSION` stays 9: no v9 run of record had been spent.
38. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T013837Z-instructions`)*: **code appends, never the model** -- *Something else*,
    every respondent-only code the registry names and every band, scale-axis and gate option -- so
    a fixed-code control or the ladder owes exactly one label per remaining plan code, a set every
    founder label (normalised) plus 2-3 distractors, Importance 4-6 difficulties, and a band,
    numeric or gate control `options` null. `MARKS_VERSION` stays 9.
39. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; same bundle)*:
    **`no_leak`'s vocabulary is stemmed from the golden mechanism's `mechanism`, `output`,
    `not_assumed` and `mechanism_terms` only**, never `trigger` (it describes the problem moment)
    or `actor`, less the problem's own stems as before. `MARKS_VERSION` stays 9.
40. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T024419Z-instructions`)*: **sweep B reads the stem, not the options.** The
    founder's label, `belief_phrase` or number for dimension *d* is swept in respondent item *d*'s
    question and the part's reveal only: a fixed-code control shows every rung, the founder's among
    them (Lullaby's *A few taps* on Adoption friction), and a set shows the founder's labels
    verbatim by R2, so a founder label in an option is the rule, not a leak. `MARKS_VERSION`
    stays 9.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

MARKS_VERSION = 9

DEFAULT_MARKS_PATH = Path(__file__).parent / "marks.toml"

#: The eight marks of `marks.toml` at v9, with its numbers. `golden_belief_recall` is retired (call
#: 29) and is **not** a key: a v9 verdict cannot carry a value for it.
DEFAULTS = {
    "dimension_coverage": 1.00,
    "option_validity": 1.00,
    "no_leak": 1.00,
    "anchoring_accuracy": 0.90,
    "compare_correctness": 1.00,
    "rule_refusal_rate": 0.02,
    "shape_refusals": 0,
    "brief_paragraphs": 1.00,
}

#: The rows `judge()` returns, in the order the report shows them.
ROWS = ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
        "compare_correctness", "refusals", "shape_refusals", "brief_paragraphs")


def load(path: Path | str | None = None) -> dict:
    path = Path(path) if path else DEFAULT_MARKS_PATH
    if not path.is_file():
        raise FileNotFoundError(f"no marks file at {path}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    marks = dict(DEFAULTS)
    marks.update(raw.get("marks") or {})
    return marks


def _at_least(value, mark) -> bool:
    return value is not None and value >= mark


def judge(totals: dict, marks: dict) -> dict:
    """Each of the eight marks against its number. A run passes only if all eight are met.

    Every row is `{value, mark, measured, met}`, and **an unmeasured mark is not a met mark**
    (judgement call 13): a `None` fails, a refusal count nobody asked for fails, a compare the
    engine never ran fails. `refusals` carries its rate beside the count (call 22, call 36).
    """
    def row(name, value, measured, met, **extra):
        measured = bool(measured) and value is not None
        return {"value": value, "mark": marks[name if name != "refusals" else
                                              "rule_refusal_rate"],
                "measured": measured, "met": bool(measured and met), **extra}

    coverage = totals.get("dimension_coverage")
    validity = totals.get("option_validity")
    leak = totals.get("no_leak")
    accuracy = totals.get("anchoring_accuracy")
    compare = totals.get("compare_correctness")
    brief = totals.get("brief_paragraphs")
    measured = bool(totals.get("refusals_measured"))
    refusals = sum((totals.get("refusals_by_rule") or {}).values())
    # v6 (call 22), v9 (call 36): a rate over the answers the aggregate judged -- `refusals_shown`,
    # accepted plus refused -- never over case-runs that were never shown to it.
    shown = int(totals.get("refusals_shown") or 0)
    rate = (refusals / shown) if (measured and shown) else None
    shape = totals.get("shape_refusals")

    results = {
        "dimension_coverage": row("dimension_coverage", coverage, coverage is not None,
                                  _at_least(coverage, marks["dimension_coverage"])),
        "option_validity": row("option_validity", validity, validity is not None,
                               _at_least(validity, marks["option_validity"])),
        "no_leak": row("no_leak", leak, leak is not None, _at_least(leak, marks["no_leak"])),
        "anchoring_accuracy": row("anchoring_accuracy", accuracy, accuracy is not None,
                                  _at_least(accuracy, marks["anchoring_accuracy"])),
        "compare_correctness": row("compare_correctness", compare,
                                   totals.get("compare_measured"),
                                   _at_least(compare, marks["compare_correctness"])),
        "refusals": row("refusals", rate, measured and shown,
                        rate is not None and rate <= marks["rule_refusal_rate"],
                        count=refusals if measured else None,
                        shown=shown if measured else None),
        "shape_refusals": row("shape_refusals", shape if measured else None, measured,
                              shape is not None and shape <= marks["shape_refusals"]),
        "brief_paragraphs": row("brief_paragraphs", brief, totals.get("brief_measured"),
                                _at_least(brief, marks["brief_paragraphs"])),
    }
    results["passed"] = all(results[name]["met"] for name in ROWS)
    return results
