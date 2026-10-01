# Implementation Plan: one occasion, one anchor, one rubric

**Branch**: `025-one-occasion-marks` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the code goes

| File | What it is |
|---|---|
| `instructions/marks.py` | `MARKS_VERSION = 8`. Judgement call 23 transcribed back in from `marks.toml`; 24, 25, 26 and 27 appended in §2's words verbatim. `DEFAULTS` and `judge()` untouched. |
| `instructions/marks.toml` | A v8 header above `[marks]`: what moved, what did not, and that scores across the bump are not comparable. Not one number in the table. |
| `instructions/corpus.py` | `Entry.anchors_for` matches a list. `_entry` refuses an anchor carrying the scalar `stage`, by entry and anchor id. Module docstring note 3 rewritten: the corpus questionnaire is the project's *and now so is the aggregate's*, and `stages` is a label. |
| `instructions/context.py` | `anchors_for` loses the `stage` key and the decision-18 comment above it. New `earlier_lines(entry, stage)` — design §6A.4's eight keys off the earlier stages' golden beliefs, 1-based within each stage. New `build_questions(entry, keys)` — 048 FR-011's five keys, `measurements` 0-based project-wide. |
| `instructions/align.py` | New `resolve_reads(produced, earlier_lines) -> (beliefs, unresolved)`. Module docstring gains T001's finding with its five line references. `FIELDS`, `produced_view`, `compare` and `align` untouched. |
| `instructions/score.py` | `score_reading` on the bare id, docstring replaced. `score_assumptions` calls `resolve_reads` first and carries `unresolved_reads`; `totals` sums it. |
| `instructions/contract.py` | `SCREEN_QUESTIONS = "QUESTIONS"`. |
| `instructions/instruction.py` | `STEMS["QUESTIONS"] = "questions"`. |
| `instructions/models.py` | `CLASSES` gains `"questions"`; `KIND_TO_CLASS["QUESTIONS"]`, `SCREEN_TO_CLASS["QUESTIONS"]`; the hard-coded `("assumptions", "reading", "brief")` in `models_used` and `efforts_used` becomes four. |
| `instructions/prompts.py` | The `QUESTIONS` case, between the assumptions loop and the readings loop. `Case.existing_roles` stays empty for it; it has no stage. |
| `instructions/validate.py` | `build_batch` gains `earlier_beliefs` per assumptions case and a `QUESTIONS` case kind; `fold_in` unchanged. `ContractUnavailable` is what a validator that does not know either shape raises. |
| `instructions/report.py` | `register_blocks` keyed by entry, not entry × stage; the produced questionnaire read off the `QUESTIONS` result. The anchoring block's denominator label. |
| `instructions/run.py` | The `QUESTIONS` answer into `produced_sets` and the register; `-k questions`; `unresolved_reads` in the printed line and the scorecard. |
| `instructions/why.py` | `SCREEN_EVENTS` and `FULL_EVENTS` gain `"marks"`; `parse` takes `marks:<version>`; `POLICY` gains its line. |
| `harness/corpus_script.py` | `role_of_anchor` against the `stages` list; `_questionnaire_anchors` moves off the assumptions result onto a `QUESTIONS` script entry; the anchoring export drops `stage`; `MAX_ITEMS` unchanged (16 anchors over seven entries, at most 4 on one project — the cap is not near). |
| `harness/browser.py` | `ParticipantPage.sections()` documented as load-bearing; `PeoplePage.preview_minutes()`; two decision-18 citations rewritten. |
| `evals/corpus_facts.py` | Fact ids lose the stage. |
| `evals/tools/curated_proof_run.py` | `rank_of` and `_sectioned_blocks`' rationale. |
| `evals/test_s012_journey_through_a_host.py` | The two shape assertions of FR-021, in the participant leg and at the send popup. |
| `tests/` | `test_instruction_score.py`, `test_instruction_align.py`, `test_instruction_context.py`, `test_instruction_models.py`, `test_instruction_prompts.py`, `test_corpus_script.py`, `test_journey_through_a_host.py` edited; `test_instruction_questions.py` and `test_instruction_reads.py` new. |
| `README.md`, `AGENTS.md` | The v8 gate, the fifth `WHY`, the new denominator, and the run when it is spent. |

## 2. The decisions worth writing down

### The four v8 judgement calls, verbatim

These are the words to append to `instructions/marks.py`, numbered **24, 25, 26, 27**, after
judgement call 23 has been transcribed back in from `marks.toml` (FR-003). The first three are
design §8.2's and §6A.8's, quoted; the fourth is this spec's, and it exists because T001 answered
the question §6A.8 could not.

> 24. **v8** *(the founder, 2026-09-30; design §8.2)*: **the match key is the bare `anchorId`
>     again, because the questionnaire is the project's.** v3 made it `(stage, anchorId)` when a
>     stage owned its questionnaire and three of them each numbered from `A1`. One questionnaire per
>     project makes `Q7` project-wide, so the pair carries no information the id does not, and a
>     `stage` on an anchoring names nothing — a merged occasion serves more than one stage's
>     beliefs.
>
> 25. **v8** *(design §8.2)*: **a corpus anchor's `stage` becomes `stages`, a list, and is a label
>     rather than a key.** `Entry.anchors_for(stage)` returns the anchors whose `stages` contain it,
>     and one anchor may be returned for two stages. Scores before and after are not comparable and
>     the constant says so.
>
> 26. **v8** *(design §6A.8)*: **a belief that reads another belief's measurement is aligned and
>     counted as an ordinary belief.** Two lines reading one control are two lines in the recall
>     denominator; the control they share is one, and `anchoring_accuracy` counts person-anchor
>     pairs rather than controls, so it does not see the change.
>
> 27. **v8, and it is the correction 26 was written conditional on** *(design §6A.8: "That answer
>     depends on one fact this pass did not verify … Spec 049's first task is to check it")*: **the
>     expectation is copied here, not by the server, because this eval scores the model's raw
>     answer.** `runner.py` stores `response["result"]` and applies it to nothing; `score.py` hands
>     `result["assumptions"]` straight to `align.align`; `produced_view` reads `belief["expectation"]`
>     and a belief carrying only `reads` has none, so `structural_candidate` refuses it on `type`
>     before a judge is ever asked. keel-cloud's validator is shelled for a verdict and never hands
>     an applied `Assumption` back. So `align.resolve_reads` copies the referent's whole expectation
>     out of the `earlier_lines` **this eval itself numbered and sent**, before alignment, and a
>     reference that cannot be resolved is counted as `unresolved_reads` and left to fail to match.
>     26 holds *because of* this call, not in spite of it: with it, `align.FIELDS` does not change
>     and the recall denominator does not change.

### The corpus revision is a keel-cloud commit, and this is how the two repositories stay honest

The corpus is keel-cloud's; this repository reads it and hashes it. So the revision lands there, and
the only thing that stops the two drifting is that **this repository's tests read the real files**.
`tests/test_corpus_script.py` already does exactly that (spec 010 R6, *one reader, one hash*), and
the new shape tests join it. The alternative — a fixture copy here to test against — would be a
second frozen set, which is the single thing freezing exists to prevent (spec 021 deviation 3).

The consequence is that **`make unit` on this branch is red until keel-cloud's revision lands**, and
that is correct: a test that passes against a corpus that has not been revised is a test that would
pass against the wrong corpus. The tasks order the work so the red is short and named.

### The hash consequence, in three parts

`Corpus.verify_unchanged()` SHA-256s all seven files on the way in and again at the end of a run
(`run.py:195` and `run.py:320–321`), and writes `corpus.sha256` into the bundle both times. Nothing
about that mechanism changes. What changes is what the digests are:

1. **Every bundle on disk was taken against the old digests.** `README.md`'s runs of record — spec
   047's `20260930T024851Z-instructions` above all — measured a 23-anchor corpus. The v8 bundle
   measures a 16-anchor one, and the two `corpus.sha256` files are the proof that they are different
   measurements. No number crosses the line.
2. **`python -m instructions.rescore` stops being an escape hatch.** It re-reads the corpus
   (`rescore.py:59`) and re-derives goldens from it (`rescore.py:67`), so re-scoring a v7 bundle
   after the revision would align answers given to one questionnaire against a different one. v4 → v5
   and v5 → v6 were pure rubric changes and were re-scored for free; **this one cannot be**, and
   that is the second independent reason the run must be spent. `rescore.py` is not changed — it is
   simply not used across this bump, and the README says so.
3. **The freeze is not weakened.** The corpus is still frozen; this is a **revision**, which design
   §8.2 distinguishes from an edit: *"a deliberate corpus revision across all seven entries, not an
   edit"*. `verify_unchanged` still fails a run outright if a file moves **while a run is in
   flight**, which is the thing it was built to catch and which this change does not touch.

### Why the alignment change lives in `align.py` and not in a new "applier"

`resolve_reads` is `ScreenResultApplier`'s step 2 of design §6A.5, and the temptation is to give it
a module named for that — an `instructions/applied.py` that mimics the server. That would be a copy
of keel-cloud's behaviour in this repository, and `runs/DRIFT.md` records the same lesson five times
(#33, #36, #41, #44, #45): this repo does not keep a copy of the cloud's arithmetic.

What saves it is that **this is not the server's resolution at all.** The server resolves
`{stage, line}` against beliefs on a live aggregate. This eval resolves it against `earlier_lines`
— a list **this repository built, numbered and sent in the context of that very case**. It is the
eval reading its own homework, which is exactly what an aligner does, and it belongs beside
`produced_view` because it is the last thing that happens to a produced belief before it is one.

### The `QUESTIONS` case is not scored, and that is a decision and not an omission

Three things could have scored it and none should.

- **A recall-shaped mark over the corpus's anchors.** It would be similarity to one hand-written
  questionnaire — judgement call 10's whole argument, arriving on a fourth subject. The corpus's
  anchors are one reasonable way to ask; `Q2` binds a selection's options to *its own* belief and
  never to the corpus's, and `align.py`'s judgement call 11 exists because of exactly that.
- **An `occasion` uniqueness metric.** `Q8` already refuses that, in the aggregate, by rule, and
  `validate.py`'s rule is that the aggregate is asked rather than restated.
- **A minutes-arithmetic check.** `minutes` is `FormComposer`'s, it is not on the wire the eval
  reads, and design §4 records that it is not rendered to a participant at all.

So `QUESTIONS` is measured by `rule_refusal_rate` (where `Q8`, `Q5`, `Q6` and `Q7` are now
reachable), by `shape_refusals` (a new answer shape on a new screen), and by `register.html`, which
renders every produced anchor prompt and option list unscored for a person to read. That is the same
shape the BRIEF subject's `verdict_phrasing` took at v5 (judgement call 20) after a code check on
words scored the instruction's own answer as a failure.

### The `WHY` policy gains a word rather than losing one

`why.py`'s four events — `instruction:`, `prompt:`, `contract:`, `new-model:` — describe changes to
the *subject*. This run's subject is unchanged: the same `claude-sonnet-5-5` at the same `medium`,
the same instructions as 048 and 049 leave them. What moved is the **ruler**. There is no honest
event name among the four, and the two dishonest options were both considered:

- **`WHY=new-model:claude:claude-sonnet-5-5`** — it would work today and it would be a lie on the
  bundle's manifest, which exists precisely so that every run on disk says why it exists.
- **`WHY=contract:marks.toml`** — `contract:` earns a **screen**, not a full run, so it would have
  to be argued past the door it was built to be.

So `marks:<version>` is added, as a full-run event, and the policy text says why: a rubric that moved
has no green run until one is spent, and `make instruction-eval`'s standing gate reads *green at the
current `MARKS_VERSION`*. It widens the founder's rule by one named event, in the open, which is the
amendment shape `AGENTS.md` asks for.

### Two merges in `02-compliancelog`, decided rather than averaged

Design §10 risk 5 and 049's risk 4 both name the corpus revision as *a judgement call seven times
over*. In practice six of the seven are one line each — `that same delivery`, `that same wake-up`,
`the tyre that punctured`, `that same invoice`, `that same job site`, and `06-repeatline`'s `S2`
already asking about `A2`'s own request. The seventh, `02-compliancelog`, has two people whose two
answers cannot be concatenated, and spec *The corpus revision* records what each becomes and why.
The rule applied is stated once and applied twice:

> **The merged anchor's tap and anchoring are re-read from the merged answer, against the standard
> the corpus has always used — did this person recount a particular past occasion? A tap is a
> statement about the occasion and outranks words written about something else; an anchoring is not
> derived by precedence from the two halves.**

Deriving it by precedence was the tempting alternative and it is refused for one reason: it would
make the corpus's own word about a person a function of arithmetic. The corpus is the reviewer.

## 2A. What the plan had to add once the work started

Three files this plan's table did not name, each for a reason it could not have known:

- **`evals/payroll_exceptions.yaml` and `tests/test_corpus_script.py`'s `CANNED`** — this repository
  has two corpus-*shaped* fixtures of its own, and both carried the scalar `stage`. Neither is the
  golden corpus and neither is merged; they simply follow the shape. Spec 021's deviation 3 is
  untouched: still no corpus **copy** here.
- **keel-cloud's `sim/check_corpus.py` and `CorpusFixture.java`** — decision 18 was in keel-cloud's
  code twice and on nobody's list. Both moved with the corpus, in the corpus commit.
- **`harness/corpus_script.py`'s `occasion_for`** — the `QUESTIONS` contract wants an occasion of
  two to five words and the corpus carries none, so it is composed from the anchor's own id, the way
  `introduction_for` and `what_this_says_for` already are under rule 5.

And one decision the plan could not take until the code was read: **`resolve_reads`' chain rule is
stated positively — the referent must own its expectation** — because a chain cannot arise off this
eval's own `earlier_lines` at all. See `tasks.md` Discovered **D8**.

## 3. What is deliberately not built

- **No `make` target of its own.** `make instruction-eval` with the new `WHY`.
- **No corpus fixture in this repository.**
- **No repair turn, no retry.**
- **No re-score across the bump.**
- **No new mark, no new subject in the marks table.**
- **No edit to keel-cloud's design, instructions or contracts.** Everything this spec needs from
  them is stated as a prerequisite and fails by name when it is missing.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| The corpus revision bakes a wrong answer into the thing that judges every future run (design §10 risk 5) | every run afterwards | The per-entry table quotes the file's own words for each merge, and the two contested people are decided in the open with the rule that decided them. The merges are reviewable in one table rather than across seven diffs. |
| `MODELS=exported` refuses to start against 048's table | the run does not begin | FR-012, and a test that parses a table carrying a `questions` class. Found by reading `models.parse`, not by a failed run. |
| keel-cloud's validator does not take a `QUESTIONS` batch case | `Q8` unmeasured, and the mark it is tested on is the one nobody can read | FR-019: the run says so by name and reports the mark unmeasured, which fails. Never softened. The prerequisite is stated to 048 rather than worked around. |
| The validator refuses every referencing belief because the batch carries nothing to resolve against | `shape_refusals` — an absolute zero — goes non-zero and the run fails for the eval's own fault | FR-018, and the batch fixture test. This is the one failure that would look like a keel-cloud finding and be this repository's. |
| Haiku cannot hold one questionnaire across three stages' beliefs (design §10 risk 1) | a rule refusal, or a second anchor for one occasion | Not this spec's to fix. 048's own screen answers it first, at $3 and fifteen minutes, before the run is spent; if it cannot, `QUESTIONS` routes to Sonnet in the table and this eval reads the table. |
| Sonnet does not reach for a reference at all (049 risk 2) | the run measures no `reads` and judgement call 27 is untested by the thing that was supposed to test it | `unresolved_reads` and the count of resolved references are both reported, so a zero is visible rather than silent. 049's own screen is what answers it cheaply. |
| The run of record goes red on one mark | ~2.5 h and ~$15 | It is the measurement. A red run is a finding about the instructions or the corpus, and `runs/DRIFT.md` is where it goes. Nothing is re-run to get a better number. |
| `make unit` is red between this branch landing and keel-cloud's revision landing | a red window | Named in §2, ordered in the tasks so the window is one commit wide, and never closed by a fixture copy. |
