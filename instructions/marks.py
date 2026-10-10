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

**`MARKS_VERSION` 10** (spec 030, 2026-10-09): the ruler follows keel-cloud 071's registry to
twelve dimensions (4 / 3 / 5, nine deal-breakers, the `b2b_only` pair) and its corpus to revision 4.
Calls 46-49 below. Every denominator a scorer reports is read off the registry and the entry's
persona, never typed; `no_claim_words` retires with `BAR_SET` and `NOT_TESTED_BY_DESIGN`; the corpus
is read from keel-cloud's canon and nowhere else; and `rescore.py` refuses every v8 and v9 bundle
by name. v10 has no run of record; it is history from v11.

**`MARKS_VERSION` 11** (spec 031, 2026-10-09): the subjects' words moved and the ruler follows
keel-cloud 072 + 073 (branch `073-price`, `0925484`). The registry is **thirteen** (4 / 3 / 6, Price
back as SHAPES), the corpus **revision 5**; Prevalence and the gate are read as an `event` clause
held to E1-E3 and C7 / R8 retire; Price is code's on both sides; W7, W9 and U1 (and W3 / W8, where
the corpus records the names) are structural; the wording rules the subject only instructs (S1, W1,
W2, W5, W6) are reported per question and never marked; the brief's two commercial figures are
keel-cloud's own; `rescore.py` refuses every bundle below 11. Calls 50-58 below. **There is no v11
run of record until `WHY=marks:11` is spent, and it is on hold by the founder**; v10's paragraph
below is history (v10 never had one).

**The corpus v11 judges, recorded 2026-10-09** (spec 031 US2). Revision 5's seven entries in
keel-cloud 073's canon (`78e1118`: r5 with the two golden names of `ed581f8`, additive), by sha256:

    01-countly         d354a69e63755a42226fd7e72d58b39f07b0913df0839c3582288460dbccecd7
    02-compliancelog   448a44fa4920a7688a8dd6c6c2dd69278bb316c81617756aeabe38e791cd6a24
    03-lullaby         54c127906709dee251bd11a8dbf3589e75450424a75c15a5b6d4ef0ad9740e22
    04-linerly         effd50dd0d1e7716308a3efc9492e99684b1e3f711aaf88666300bfadca9a9f7
    05-paidly          e7c39b4b255b02b7c2263a9388df6ea7fe01ebb24d018ff531ec4d77f6441ba0
    06-repeatline      70b889dadc1bb7164b9497dccea0e461e1ef8d99563a2862433bf6961d4242a1
    07-mulchrun        0a06b4ee3712663031f6f3b73adc1623bcf247f9a6de9a9c346a233183d453c3

The v11 denominators, **counted, not estimated**: calibration 11 keys on 01-04 (B2C) and 13 on
05-07 (B2B), 83 an N; respondent 11 on a B2C entry (4 / 3 / 4 on `PRIMARY`) and 13 on a B2B one (4
/ 3 on `PRIMARY`, 6 on `COMMERCIAL_B2B`; 5 on Mulch Run, whose founder left Price out), 82 an N;
`no_leak` 46 sweep-A and 71 sweep-B items an N (never Price, never Frequency over a framed window --
Countly's *last month* and Repeatline's *last shift* keep theirs); `compare_correctness` 11 + 3 or
13 + 3 checks an entry, **104** on seven. `anchoring_accuracy` is still 65 reads at N=1; a full run
still builds 135 model cases at N=1 (405 at N=3).

**The corpus v10 judged, recorded 2026-10-09** (spec 030 US2; history). Revision 4's seven entries in
keel-cloud 071's canon (`f38ac42`), by sha256:

    01-countly         81d5d00665fab6b284f5238f2c2d8512226105d7566e88ad2c1f47a73ba7f391
    02-compliancelog   0585d989e1f4b890bd4648826921dc36a58d3efaf5dbc6a144df66d4a0487e1a
    03-lullaby         fe1f3babc2af3c487f4edc9fa1fa2b84ae0875c596e3e8b17f0d0df3d40d1573
    04-linerly         c781766e3080c495586dacaceb02e388775fe8700956c85a86e957347fb5800a
    05-paidly          0a98e4db5e4640399bcd87559593dc91595c5e80cde094e3ae52276defbf6f6a
    06-repeatline      0754e19cb43e1a463acb081dc4dec96caab0bb1831c2b89a883d0b30071233a2
    07-mulchrun        86deab848963eee58255e8c09abf4579f964ecd27ea6bad276eaae46e4d94e4f

The v10 denominators, **counted, not estimated**: calibration 10 keys on 01-04 (B2C) and 12 on
05-07 (B2B), 76 an N; respondent 10 on a B2C entry (4 / 3 / 3 on `PRIMARY`) and 12 on a B2B one (4
/ 3 on `PRIMARY`, 5 on `COMMERCIAL_B2B`), 76 an N; `compare_correctness` 10 + 3 or 12 + 3 checks an
entry, **97** on seven. `anchoring_accuracy` is still 65 reads at N=1 (106 people less 13 gate-No,
6 chipped stories and 22 decision-makers). A full run builds **135 model cases at N=1** (405 at
N=3): three interpretation screens, three calibration jobs and three respondent jobs an entry
(part 3 of a B2B study is the decision-maker's link, never a fourth job), 65 reads and seven briefs.

**The corpus v9 judged, recorded 2026-10-07** (spec 029 US4.2, plan O-4; history). Revision 3's
seven entries, by sha256 -- the recorded revision under `tests/fixtures/corpus-r3/` (deleted at v10,
call 49), moved verbatim into keel-cloud's canon:

    01-countly         e8b72c47d57085133032d267682f720eecb603b4aab921f2b5a85ccc96815320
    02-compliancelog   5b8d01a9048dc7263f6e8de82da2221f91ffc413b2229dba5e452d59821fda27
    03-lullaby         229f794d6374c315dd6c8edac4d21051d411888f63005b84e72cb28ccab50ed8
    04-linerly         0aa0b13f4f649de942a54baff934e4e6a464098f0e40f4cc2d82b41cf4498fc9
    05-paidly          00f0d030e32457a00c35e9118865591168c9dd4caa661992303b4ed4251b3716
    06-repeatline      991bd046984a64675e07c59ed5dc57f905a63ee87100c1e241dd49006ff43f61
    07-mulchrun        a4e76486a16c07a0f2be1d54d2d2b8f17a0417292e3999dbc81d5b4a2cd7e682

Amended 2026-10-08: Lullaby's `mechanism_terms` drops `cot` (call 39), and every entry's model-written
sets gain `founder_calibration[d].labels`, the labels production sends as `founder_options`.
Amended 2026-10-08 again, synced to keel-cloud 058 `5fc7220`'s canon byte for byte: 13 belief
sentences are the engine's again (`problem.prevalence` in 01/02/04/05/06/07, `problem.importance`
in all seven), every entry records `context.recall_window: {count, unit}` (founder decision 42),
and Lullaby's circumstance reads *the baby cries in the night* (the GRAMMAR decision).

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
41. **v9, amended before any run of record** *(the founder's decision 35, 2026-10-08)*: **the
    structural marks read the accepted answer.** `option_validity`, `dimension_coverage` and
    `no_leak` on the two question screens are scored on the answer after the runtime's rule
    refusal and ONE redraw -- what a founder sees -- because a rule refusal is the product
    correcting the model, one extra call (call 22). The runner redraws as keel-cloud 058's
    orchestrator does, on the five screens it repairs (`CALIBRATION_QUESTIONS`,
    `RESPONDENT_QUESTIONS` -- `repairUnattended`; the three draft vector screens --
    `refuseOrRepairDraft`; never `INTERPRET` or `BRIEF`): turn one's context plus a `repair`
    sentence in the cloud's own words, the same instruction, contract, model and effort, empty
    input, and no previous answer. The raw slip stays measured: `rule_refusal_rate` counts every
    refusal, first draft and redraw, over the first-draft answers (the v6 denominator). A second
    refusal is terminal: the answer stays refused, scores as faults on the raw answer, and counts
    twice. Shape refusals are not redrawn and stay an absolute zero on the raw answer. A v9
    bundle taken before this call has no redraw and is re-scored on the raw answer, saying so.
    `MARKS_VERSION` stays 9.
42. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T115552Z-instructions`)*: **coverage's observed figure for money sets.** A set
    dimension's money median (Existing sacrifice) was handed to `BRIEF` as a bare *165* and the
    check then asked for *165*. It is written in the founder's unit, *£165 per three months* --
    the currency's symbol and the period from the standing, else the one every answer's `cost`
    agrees on, the currency else the market's (the price likewise, as keel-cloud's
    `observedFigure` writes it) -- and a set whose money cannot be written so carries no figure and
    is asked instead for one of its own option counts as `N of M`. The founder's phrase is asked
    for exactly as strictly as brief.md asks: on a bet whose verdict is `NOT_HOLDING_UP` ("The
    four things the paragraph says", 2: `founder_phrase` against `observed`), verbatim -- brief.md
    licenses no paraphrase -- and on no other bet. `MARKS_VERSION` stays 9.
43. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; same bundle)*:
    **a mechanism stem in an option label is a tie.** Sweep A's direct hit inside an OPTION LABEL
    of a PROBLEM calibration question or a Part 1 respondent item (*phone*, *wheel*, *caught* --
    generic nouns of the problem's own world, offered as answers) goes to the judge with the one
    existing question, as an inflection tie does -- a multi-word term too (*signed off*); a hit in
    the question stem stays a fault outright. `MARKS_VERSION` stays 9.
44. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T115552Z-instructions`)*: **three narrowings of what is the model's.**
    (i) `option_validity`'s not-sure OPTION is one whose whole normalised label is *I'm not sure*,
    *Not sure*, *Don't know*, *I don't know*, *Unsure* or *Prefer not to say* -- never a label
    that contains the words (*Not sure it would fit* is a reason; keel-cloud 058's C3 likewise);
    and a code-appended escape row is told by its label as 058 appends it (*None of these*,
    *Nothing*, *Nothing yet*...), never by a fixed slug -- production slugs the founder's escape
    `none_of_these_<...>`. The same whole-label test finds an escape row the MODEL wrote (a
    fault, code appends it): *Something else*, *None of these*, *Nothing yet*, *Nothing* and the
    registry's escape labels, normalised for case and punctuation -- never a prefix (*Something
    else was cut or given up to cover it* is Ability to pay's scale step, code `barely`; the
    prefix match faulted certificate run 3, `runs/20261008T194906Z-instructions`). **(44a)** `no_leak`'s vocabulary, per question, subtracts every stem of
    the registry's own wording for the dimension being asked -- its `respondent` block (guidance,
    option_rule, chips), its founder `option_rule` and `code_rule` (the fixed escape labels) and
    the registry's `common` block; never its `lullaby` example. *In the order you tried them* is
    registry wording and can never be a leak. **(44b)** Sweep B (the founder's label, phrase or
    number) reads question STEMS only, never the part's reveal: the reveal is governed by R6's
    claim-word rule and legitimately names the mechanism's moment (*at quarter end*).
    `MARKS_VERSION` stays 9.
45. **v9, amended before any run of record** *(the founder's decisions 46 and 47, 2026-10-08;
    bundle `runs/20261008T155720Z-instructions`)*: **what each step can apply.** **(Decision
    47)** `no_leak`'s sweep A on a PROBLEM calibration question uses keel-cloud 058's product-word
    list (`Vocabulary.PRODUCT_WORDS`, whole-word) and the golden mechanism's `mechanism_terms`
    only (single words by stem, less the registry's wording for the dimension, call 44a;
    multi-word terms as phrases), in the question, its options and their belief phrases -- what
    the runtime can refuse at that step -- and a hit is a fault, never judged. Part 1 respondent
    items keep the full derived vocabulary and the judge (calls 32, 39, 43, 44a).
    `judged_fraction` is items judged over items with any hit -- one unit, reported, never marked
    (it read 0.72 as items over word hits). **(Decision 46, call 41 extended)** `BRIEF` is redrawn
    once on a rule refusal, as the cloud now does (`repairUnattended` ->
    `queueAnotherQuestionsTurn`: turn one's context plus `repair`, no history, empty input), and
    the accepted paragraph is scored; a brief refused twice is scored on its raw paragraph as a
    fault, every mark missed -- the founder is shown no paragraph. `MARKS_VERSION` stays 9.

**The v9 run of record, recorded 2026-10-08** (the founder's decision 48; not a judgement call):
`runs/20261008T194906Z-instructions` -- `WHY=marks:9`, host claude, `MODELS=exported`
(claude-sonnet-5-5 at medium, Haiku 4.5), 414 cases, $19.75 -- **re-scored** under call 44's
whole-label escape fix. The run's one fault was a legitimate scale step (Ability to pay's
*Something else was cut or given up to cover it*); the answers are untouched, and the run's own
11 judge answers were all DIFFERENT. Every mark met: `dimension_coverage` 1.00, `option_validity`
1.00, `no_leak` 1.00, `anchoring_accuracy` 0.9949, `compare_correctness` 1.00, refusals 0.0072,
`shape_refusals` 0, `brief_paragraphs` 1.00. The founder accepted the re-score as the certificate.
`runs/` is gitignored, so the bundle lives on this machine only; its `scorecard-v9.json` is
sha256 `1cae4bb5b85bfeb47dedfb54b51ea9d06361f79bfecbee78cd21884445e81dea`. It is history from
2026-10-09: `MARKS_VERSION` 10 refuses to re-score it (call 49, `rescore.py`).

46. **v10** *(spec 030, 2026-10-09; keel-cloud 071, registry decision 14)*: **the registry is
    twelve, calibrated and asked alike.** Invariants 1, 2, 3 and 8 are rewritten: twelve keys,
    4 / 3 / 5; the nine deal-breakers are Prevalence, Importance and Current-solution satisfaction;
    Compatibility, Relative advantage and Adoption friction; Existing sacrifice, Buyer/payer
    alignment and Commitment; `b2b_only` sits on exactly `commercial.ability_to_pay` and
    `commercial.purchase_friction`, and every entry is asked in its own vector's part (4 / 3 / 5;
    `PRIMARY` asks 3 / 3 / 3 after the gate, `COMMERCIAL_B2B` 5); and every deal-breaker's status
    vocabulary reaches `NOT_HOLDING_UP` (invariant 8). `asked_in_v1` is not read; a registry
    carrying it is refused as unknown-shaped, not ignored. Invariant 6's numeric controls are the
    ones keel-cloud's `RespondentControl.yieldsNumber` names (`segmented_0_to_7`, and
    `number_with_unit` on a recall window longer than 7).
47. **v10**: **the plan is per link and per persona.** `dimension_coverage`'s respondent
    denominator is `plan_keys(part, founder_calibration, link, b2b)` -- on `PRIMARY` the registry
    less the `b2b_only` pair, on `COMMERCIAL_B2B` the commercial part whole -- and part 3 of a B2B
    study is asked on the decision-maker's link only (keel-cloud `EvidencePlan`, decision 26), so a
    B2B entry has three respondent jobs, not four. The calibration denominator is the entry's
    calibrated set, `calibrated(b2b)`: on a B2C entry the two `b2b_only` keys are not calibrated,
    and a `founder_calibration` (or a pick, a plan row or a standing) naming them is a refusal
    naming the key.
48. **v10**: **`no_claim_words` retires** with `BAR_SET` and `NOT_TESTED_BY_DESIGN` (keel-cloud
    071 removed both statuses and the two rows they scored); `brief_paragraphs` is all four or
    nothing. Struck through in `marks.toml`'s comment as `golden_belief_recall` is; call 35 stands
    as history.
49. **v10**: **corpus revision 4, read from keel-cloud's canon only.** The fixture fallback of
    2026-10-07 (`tests/fixtures/corpus-r3/`) is deleted with its directory; `load()` refuses a
    directory holding any file at a revision other than 4, by entry and by key, naming a
    revision-3 file as v9's. `rescore.py` refuses a v8 **or v9** bundle by name: corpus r4 carries
    no standing for thirteen of the dimensions a v9 bundle scored, so a v10 number for it would be
    fiction.
50. **v11** *(spec 031, 2026-10-09; keel-cloud 073, registry decision 15)*: **the registry is
    thirteen.** Invariants 1, 3 and 5 restated: thirteen keys, 4 / 3 / 6; `commercial.price` at
    commercial order 2, SHAPES, not `b2b_only` (asked of whoever pays), founder control
    `price_range` whose `periods` are exactly `month · year · one_off` (`PriceLadder.PERIODS`, a
    fifth-invariant fault otherwise), respondent control `price_ladder`, `ordinal_band`; Existing
    sacrifice asked as `branch_pick_amounts`; Ability to pay's rungs `existing_line ·
    new_line_signed_off · taken_from_other_spend · no_budget`. The nine deal-breakers and the
    `b2b_only` pair do not move; the calibrated set is eleven on B2C and thirteen on B2B, read.
51. **v11**: **corpus revision 5, read from keel-cloud's canon only.** `load()` refuses a directory
    holding any file at a revision other than 5, naming a revision-4 file as v10's. The founder's
    Price is `{low, high, period, currency}` -- a low of 1 to under 10,000, the high not below it, a
    period of the three, the market's currency -- or `unsure` (Mulch Run: LEFT_OUT); its plan row is
    the ladder's five bands around the low plus `would_not_pay` (`PriceLadder.bands`, mirrored as
    `corpus.price_ladder_codes`), and a row that disagrees is a refusal naming both; Existing
    sacrifice's kinds carry money · hours · count and its picks are `{currency, amounts}` on the
    row in the row's units; every fixed-code founder answer is one of the registry's codes.
52. **v11**: **the window is code's.** keel-cloud 072 composes the four windowed questions from
    fixed frames around one model-written clause. `option_validity` reads a Prevalence calibration
    entry's and the gate's **`event`** and holds it to E1-E3 as `WindowFrame.fault` does (no digit,
    number word or time word -- the window unit's words included; one clause of at most 25 words,
    no `?`, no sentence break; not opening with *in*, *how many*, *did you*, *out of*, *do you
    think*); a missing `event` is E2. Frequency over a window of more than one unit owes no
    question text, and a text written anyway is ignored, never a fault (keel-cloud D-7); a
    one-unit window keeps its model-written question. **C7 and R8 retire** from every check, and
    `RecallWindow.said` / `is_named_in` with them. `no_leak` sweeps the `event` clause where it swept
    the question.
53. **v11**: **Price is code's on both sides.** Its calibration entry owes its key (and its
    `respondent_note`) and nothing else: options are a C2 fault, a question is ignored; its
    respondent item owes its key, and nothing a model writes there is read. Both count once in
    `dimension_coverage` and `option_validity`; **neither is ever swept by `no_leak`**, and neither
    is Frequency over a framed window: there is no model text a reader is shown. The sweep
    denominators are read off the registry and the entry's window (the case's `swept`).
54. **v11**: **the money, the hint and the unit are structural** -- each an `option_validity`
    fault on the screen it is found on, mirrored from keel-cloud 073: W9 (`Wording.money`: a
    currency symbol, an ISO 4217 code in capitals, or an amount with a currency word) in any
    model-written question, event, option label or belief phrase; W7 (`Wording.tickAll`: *tick /
    select / choose all|every*, *pick all*, *all that apply(ies)*) in a question; U1 (an Existing
    sacrifice founder option but `none` without `unit` money · hours · count; a respondent
    distractor without its `units[i]`).
55. **v11**: **one name for the idea, one for the offer -- held only to a name the corpus
    records.** W3: every SOLUTION calibration question, every part-2 item and the reveal carry
    `solution_mechanism.short_name` verbatim; W8: every COMMERCIAL calibration question and every
    part-3 / decision-maker item, Existing sacrifice and Price aside, carry
    `interpretations.offer_name` verbatim (`Wording.carries`: case, accents, apostrophes,
    punctuation and a leading article free). The eval never takes a name from a live screen's
    answer (marks-v9 §1), and **revision 5 records neither**, so on r5 both are held to none --
    as keel-cloud holds a card confirmed before 072 -- the job is handed `null`, the validator the
    same mechanism and offer (never its Lullaby fixture's names), and the dry run prints *held to no
    name*. A name a later revision records is read with no code change. **Amended 2026-10-09,
    before any run of record** (keel-cloud 073 `ed581f8`, additive within revision 5): every r5
    entry now records both names (Lullaby's *a suggested reason for crying* / *something that helps
    at night*), so W3 and W8 hold to them on all seven; the job is handed them -- on the SOLUTION
    card, the respondents' mechanism, the COMMERCIAL persona map and, since the export names it,
    `offer_name` on every part-3 job -- and so is the validator.
56. **v11**: **the wording rules are reported, never marked.** `window-frame-design.md` §3.6-§3.8
    make S1, S2, W1, W2, W4, W5 and W6 instruction rules the eval counts and the applier never
    refuses; a mark the product does not enforce would be the ruler inventing a rule. Per question
    and item with model text, `score.py` counts its words and W1 (more than 20, or 25 with a scene
    sentence first), W2 (*do you think / believe*, founder side), W6 (second person, founder
    side), S1 (one sentence over 20 words with a clause in front of the question) and W5 (options
    over 8 words) into `totals.wording`; the report renders them and `judge()` reads none. S2 and
    W4 need a name or a jargon list the corpus does not carry: the register page's to read.
57. **v11**: **the brief's commercial figures are keel-cloud's.** Existing sacrifice's `observed`
    is `Figures.cost`'s shape with no hourly rate (the corpus records none, so hours are never
    priced): *a median £22 over three months*, the hours median apart (*; 11 hours*); Price's is
    `Figures.price`'s, *{inside} of {n} said it would be worth {floor} {period} or more*. Call 42's
    *£… per three months* is superseded for both. `brief_paragraphs` stays four per-case marks: B6
    (*will pay / will buy*) is the aggregate's rule, counted by `rule_refusal_rate` and -- refused
    twice -- scored as a fault on every mark (call 41).
58. **v11**: **`rescore.py` refuses every bundle below 11** by name: a v10 bundle answered without
    Price, without units and with the window in the model's own words, so a v11 number for it
    would be fiction. The only v11 number is a v11 run (`WHY=marks:11`, on hold by the founder).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

MARKS_VERSION = 11

DEFAULT_MARKS_PATH = Path(__file__).parent / "marks.toml"

#: The eight marks of `marks.toml` at v11 (v9's eight, unchanged in number), with its numbers. The
#: wording counts of call 56 are reported and are never a key here.
#: `golden_belief_recall` is retired (call 29) and is **not** a key: a verdict cannot carry a value
#: for it. `no_claim_words` (call 48) was never a mark of its own -- one of `brief_paragraphs`' per-case
#: marks -- so its retirement moves no row here.
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
