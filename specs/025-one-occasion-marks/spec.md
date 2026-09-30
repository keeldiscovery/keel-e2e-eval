# Feature Specification: one occasion, one anchor, one rubric — `MARKS_VERSION` 8, the revised corpus, and the run of record that certifies both

**Feature Branch**: `025-one-occasion-marks`

**Created**: 2026-09-30

**Status**: **Implemented, 2026-09-30, except the run of record — which has not been spent and is
the founder's to type.** Phases 1–9 are landed on this branch, `make unit` is green at every commit,
and keel-cloud's half landed first: `048-lines-then-questions` and `049-one-occasion-once` are both
in, and the corpus revision this spec decides is keel-cloud commit `4652739` on
`049-one-occasion-once` (`check_corpus.py` green on all seven entries, `./gradlew check` 1,548 tests
0 failures). **Nothing here has spent anything**; T030 is the only paid task and it is unticked.

**Three amendments the work made to this document, each recorded in `tasks.md`'s Discovered ledger
rather than edited into the text above as though it had always said so:**

1. **The corpus revision moves `02-compliancelog`'s `expected.standings`** (D3). FR-007 and the
   per-entry table do not say so, and they should: Daniel Achebe's merged anchoring is re-read as
   `ANCHORED`, so his answers count, and all six PROBLEM lines go `inside` +1 / `guessed` −1. No
   verdict, no drift and no median moves, and no other entry's `expected` block moves at all.
2. **keel-cloud's validator takes the `QUESTIONS` shape and does not take `earlier_beliefs`** (D12).
   US6's risk is live, FR-019 is what answers it, and the prerequisite is written out for keel-cloud
   in `validate.py` and in T030. It is the one thing open at the end of this spec.
3. **Phase 2's tests land with the phases they certify** (D11), so `make unit` is green at every
   commit — the rule this repository works to, and the way keel-cloud's sibling 049 ran.

**The design's own numbering calls this spec `025-one-questionnaire`.** It is branched
`025-one-occasion-marks` because what this repository owns is not the questionnaire — keel-cloud
048 owns that — but the **marks**: the rubric version, the alignment rules, the corpus the rubric
reads, and the run that certifies them. The design's §9.2 item 4 is this spec.

**Input**: the designs and specs of record, read in full —

- keel-cloud [`canon/designs/one-occasion-once-design.md`](../../../keel-cloud/canon/designs/one-occasion-once-design.md)
  — **§3** (the rule, and why option (c) is the only place the rule and the evidence are in one
  room), **§4** (what the participant sees; the section titles; *`minutes` is not rendered on the
  participant page at all*), **§5** (the data model; §5.2's `interpret.md` drift), **§6** (`occasion`
  and `Q8`), **§6A in full** (the second approved change: §6A.1 the finding, §6A.4 `earlier_lines`,
  §6A.5 `reads`, §6A.6 one control, §6A.7 one answer against two lines, **§6A.8 `Q2` and the marks,
  and the one fact it does not verify**), **§7.1–§7.3** (the numbers; the corpus's 23 anchors, 106
  people and 358 person-anchor pairs), **§8** (*what the marks and the corpus need* — §8.1 how
  anchoring accuracy is scored today, §8.2 exactly what changes and the three v8 judgement calls,
  §8.3 what the marks do *not* need), **§9** (§9.1 what certifies what, §9.2 the five specs),
  **§10** (the risks), **§12** (the amendment recording the founder's approval of both changes and
  the 048/049 split).
- keel-cloud [`specs/048-lines-then-questions/spec.md`](../../../keel-cloud/specs/048-lines-then-questions/spec.md)
  — its *Mark implications* table, FR-009 to FR-021 (the `QUESTIONS` screen, its context, its
  schema, its four derivations), and its statement that **it edits no file in this repository**.
- keel-cloud [`specs/049-one-occasion-once/spec.md`](../../../keel-cloud/specs/049-one-occasion-once/spec.md)
  — its *Mark implications* table, its decision **A-6** (*the exporter question is answered first,
  not last*), **A-8** (the corpus keeps a `stages` list as a label) and **A-9** (this repository is
  stated as a requirement and never satisfied there), and its risks 1 and 4.
- keel-cloud [`canon/designs/measured-beliefs-design.md`](../../../keel-cloud/canon/designs/measured-beliefs-design.md)
  — §3.6, §5 (`Q1`, `Q2`, `Q4`, `Q7`), §8, and **decision 18**, which the two keel-cloud specs
  supersede and which is the whole reason `MARKS_VERSION` 3 exists.
- keel-cloud `canon/designs/measured-beliefs/corpus/*.yaml` — the seven frozen entries, **counted
  here**, anchor by anchor and person by person. The counts are in *The corpus revision, entry by
  entry* below and every one of them was taken from the files, not from a document.
- this repository, read at `master` `aa3b584`: `instructions/` (`run.py`, `runner.py`, `prompts.py`,
  `context.py`, `contract.py`, `corpus.py`, `instruction.py`, `models.py`, `judge.py`, `marks.py`,
  `marks.toml`, `score.py`, `align.py`, `validate.py`, `report.py`, `rescore.py`, `why.py`);
  `harness/corpus_script.py` and `harness/browser.py`; `evals/test_s012_journey_through_a_host.py`
  and `evals/tools/curated_proof_run.py`; `evals/corpus_facts.py`; `Makefile`; `AGENTS.md`; and
  `specs/021-short-journey/`, `specs/023-staging-on-demand/` and `specs/024-keels-ai-cell/` as the
  shape this repeats.
- `.specify/memory/constitution.md` — **an unfilled template** at `aa3b584`, every principle still
  `[PRINCIPLE_N_NAME]`. It is recorded here because a specification that claims to have been checked
  against a constitution should say when there is nothing to check against. `AGENTS.md` is this
  repository's governing document and is what this spec is written to.

## The one sentence

**`MARKS_VERSION` goes 7 → 8 with four judgement calls, not three: the corpus's anchors carry a
`stages` list instead of one `stage` and seven of them merge so that one occasion is anchored once,
`score_reading`'s match key collapses from `(stage, anchorId)` to the bare anchor id and its
denominator falls from 238 written person-anchor pairs to 160, `Entry.anchors_for` matches a list,
the instruction eval gains the `QUESTIONS` screen — one Haiku call per corpus entry, after that
entry's three assumptions cases — while the three `*_ASSUMPTIONS` screens stop being scored for a
questionnaire they no longer write, and — because **T001 found that this repository's exporter reads
the model's raw answer and never the applied belief** — a produced belief carrying `reads` is
resolved against the `earlier_lines` this eval itself built before it is aligned, which is the
fourth judgement call the design's §6A.8 said would be needed if the answer came back raw.**

## What this spec does not do

- **It does not change a mark's number.** `anchoring_accuracy` stays 0.90, `golden_belief_recall`
  0.80, `rule_refusal_rate` 0.02, `shape_refusals` 0, `brief_paragraphs` 1.00.
  `model-routing-design.md` §7 step 3: *"The marks are not touched. A candidate that misses a mark
  is not the table's problem; the prompt or the model changes, never the number."*
- **It does not add a mark, and it does not score the `QUESTIONS` answer.** The new screen is
  measured by the aggregate (`rule_refusal_rate`, where `Q8` is now reachable) and rendered on
  `register.html` unscored, for the same person who already reads the anchors. A `questionnaire`
  mark would be similarity to one hand-written example — judgement call 10, arriving on a new
  subject.
- **It does not write, edit or commit a corpus file.** The corpus is keel-cloud's
  (`canon/designs/measured-beliefs/corpus/`), read-only here, hashed on the way in, and spec 021's
  deviation 3 stands: *"No corpus copy in this repository."* This spec **decides** the revision,
  entry by entry, with the reasoning and the counts; the seven files are edited on keel-cloud's own
  branch against the table below.
- **It does not touch keel-cloud's instructions, contracts or aggregate.** 048 and 049 own every
  one of those, and this spec's tests fail loudly and by name against a sibling that has not landed
  them rather than working around it.
- **It does not change `evals/policy.py` or `POLICY_VERSION`.** Two rubrics, two constants, and
  `AGENTS.md`'s rule that they can never be confused.
- **It does not re-score an old bundle to v8.** `python -m instructions.rescore` re-reads the corpus
  (`rescore.py:59`), so a v7 bundle re-scored after the revision would align the old answers against
  a corpus that no longer describes the questions they were asked. v4 → v5 was a pure rubric change
  and could be re-scored for free; v7 → v8 cannot, and that is precisely why a run is spent.
- **It does not spend anything but the one run at the end**, and that run is the founder's to type.

## What the siblings are, read at these commits

| Sibling | What this feature depends on | Where it is today |
|---|---|---|
| keel-cloud | `048-lines-then-questions` in full (the `QUESTIONS` screen, its context and schema, the project questionnaire, `Q8`, the routing table's new `questions` class, `CONTRACT_VERSION` 1, `SCHEMA_VERSION` 8) and `049-one-occasion-once` in full (`earlier_lines`, the belief's `reads`, `Q2` as one measurement, the `stage` off `AnchorRef`/`SelectionRef`/`AnchorAnswer`/`Pick`/the reading, `CONTRACT_VERSION` 2, `SCHEMA_VERSION` 9). And the corpus. | **Neither has landed.** `keel-cloud` is on `048-lines-then-questions` at `71e6fe7` — phase 1, the baseline and the ledger. |
| keel-web | `026-one-occasion-once` — sections titled by occasion, the founder preview's minutes line, `AnswersPopup` dropping `stage`. | Not started; keel-web's live numbering is at `025`. |
| keel-runtime | **nothing.** The contract is model-neutral and no schema keyword changes shape (design §9.2 item 5). | — |
| keel-connect-skill | nothing. | — |
| this repository | spec 009's `instructions/` in full; spec 010's `harness/corpus_script.py`; spec 021's `KEEL_JOURNEY_ENTRY` and the corpus founder; spec 022's `instructions/models.py`; spec 047's certified combination, read through spec 024's `MODELS=exported` and judge isolation. | `master` `aa3b584`. |

**So nothing in this spec can be run green until 048 and 049 land**, and that is a statement about
the siblings and not about this spec. Everything provable without them — the corpus shape tests, the
match-key change, the `reads` resolution, the register's regrouping, the journey's section
assertions — is held by `make unit` against fixtures, and the one thing that cannot be is the run of
record, which is T-last and the founder's.

## What changes, stated first

| File | What it is |
|---|---|
| `instructions/marks.py` | `MARKS_VERSION` 7 → **8**. Judgement call **23** transcribed back in from `marks.toml` (it is cited there and missing from the list — see FR-003). Judgement calls **24, 25, 26 and 27** appended, struck nowhere. |
| `instructions/marks.toml` | A header paragraph for v8: what moved, and that scores before and after are not comparable. **No number in the `[marks]` table moves.** |
| `instructions/corpus.py` | `Entry.anchors_for(stage)` matches a **list**: the anchors whose `stages` contain it, so one anchor may be returned for two stages. Note 3 of the module docstring rewritten. A file still carrying the old scalar `stage` is a **refusal to start**, naming the entry and the anchor. |
| `instructions/context.py` | `anchors_for(entry, person)` drops the `stage` key from every INTERPRET context entry. New `earlier_lines(entry, stage)` — the eight keys of design §6A.4, from the earlier stages' golden beliefs. New `build_questions(entry, keys)` — the `measurements[]` of 048 FR-011. |
| `instructions/score.py` | `score_reading` keys on the bare `anchorId`; its docstring's decision-18 paragraph is replaced, not deleted. `score_assumptions` resolves `reads` before it aligns, and reports `unresolved_reads`. |
| `instructions/align.py` | New `resolve_reads(produced, earlier_lines)`. `FIELDS` is **unchanged** — the eight fields still decide a pair; what changes is that a referencing belief now has them. |
| `instructions/contract.py` | `SCREEN_QUESTIONS = "QUESTIONS"`. |
| `instructions/instruction.py` | `STEMS` gains `"QUESTIONS": "questions"`. |
| `instructions/models.py` | `CLASSES` gains `"questions"`; `KIND_TO_CLASS` and `SCREEN_TO_CLASS` gain their rows; `models_used`/`efforts_used` report four classes. **Without this, `MODELS=exported` refuses to start against 048's table** (FR-012). |
| `instructions/prompts.py` | `build_cases` emits one `QUESTIONS` case per entry, **after** the three assumptions cases and before the readings — because that is the order production runs them in and the case id is what `-k` filters on. |
| `instructions/validate.py` | The batch carries the earlier stages' approved beliefs (so the validator can resolve a `reads`) and a `QUESTIONS` case kind (so `Q8`, `Q5` and `Q6` are reachable). `_STAGE_SCREEN` gains nothing; `QUESTIONS` has no stage. |
| `instructions/report.py` | `register_blocks` groups the produced questionnaire **by entry**, not by entry × stage, and puts the entry's whole revised anchor list beside it. The scorecard's anchoring block reports the new denominator. |
| `instructions/run.py` | The `QUESTIONS` case's answer into the batch and the register; `-k questions`; the printed line. |
| `instructions/why.py` | A fifth event: `WHY=marks:<version>` earns **the full run**, because a rubric that moved has no green run until one is spent and the policy has had no word for it. |
| `harness/corpus_script.py` | `role_of_anchor` matches a belief's stage against the anchor's `stages` **list**; the scripted `*_ASSUMPTIONS` results stop carrying `questionnaire`; a `QUESTIONS` script entry is emitted once per entry; the anchoring export drops `stage`. |
| `harness/browser.py` | `ParticipantPage.sections()` — dead since it was written — becomes load-bearing. `PeoplePage.go_to_preview` gains `preview_minutes()`. `answer_as`'s decision-18 scoping comment is rewritten to the project-wide id space. |
| `evals/corpus_facts.py` | Fact ids stop carrying a stage: `anchor.{id}` and `said.{slug}.{anchorId}`. |
| `evals/tools/curated_proof_run.py` | `rank_of` stops reading `anchor["stage"]`; `_sectioned_blocks`' "one `.sect` per stage, in stage order" rationale is replaced by one section per occasion, in questionnaire order. |
| `evals/test_s012_journey_through_a_host.py` | Two new assertions, both shape: the founder's preview carries **one** minutes line, and the participant page draws **one section per anchor block** and none of the three old stage titles. |
| `tests/` | The new and rewritten stackless tests of FR-020. |
| `README.md`, `AGENTS.md` | The v8 gate, the new `WHY` event, the new denominator, and the run of record when it is spent. |

**And one file this repository does not own**: keel-cloud's seven corpus YAMLs, revised against the
table below.

## The corpus revision, entry by entry

**Every number here was counted from the files**, and the merge in every entry is `A1 + A2` — the
problem stage's occasion and the solution stage's, which in all seven entries are the same past
event seen from two angles. `05-paidly`'s `A2b` and `A2c` are genuinely other occasions and **stay**.

| Entry | anchors **before** | anchors **after** | what merges, and the evidence in the file | people | written person-anchor pairs, **before → after** |
|---|---:|---:|---|---:|---:|
| `01-countly` | 3 | **2** | `A2`: *"Think of **that same delivery** arriving."* The merge is written out in prose. | 12 | 33 → **22** |
| `02-compliancelog` | 3 | **2** | `A2` (*"the last time you had to get completion figures out of a system"*) is the system the `A1` report was built from — every person's two answers name the same tool and the same report (*"Exported three CSVs from Cornerstone…"* / *"Cornerstone. The report it gives you counts a course as done if it was ever started…"*). And `A1`'s own `S3` already asks *"How was it put together?"* | 12 | 34 → **22** |
| `03-lullaby` | 3 | **2** | `A2`: *"Think of **that same wake-up**…"* — design §7.2's own example, and the entry the live form is modelled on. | 12 | 34 → **23** |
| `04-linerly` | 3 | **2** | `A2`: *"Think of **the tyre that punctured**"* — the `A1` puncture, named. | 12 | 34 → **23** |
| `05-paidly` | 5 | **4** | `A2`: *"Think of **that same invoice**. How did you send it?"* `A2b` (*the last time a service offered to pay an invoice early*) and `A2c` (*the last platform or payment fee the agency paid*) are different events on different days and are **not** merged. | 20 | 45 → **34** |
| `06-repeatline` | 3 | **2** | `A1`'s own `S2` asks *"How long did the last one take?"* and `A2` is *"the last repeat-prescription request you handled"* — `S2`'s "last one". Two of `A2`'s three selections (*"Does the practice have an online form…"*, *"What kind of phone system…"*) are standing facts and not about an occasion at all. | 19 | 29 → **18** |
| `07-mulchrun` | 3 | **2** | `A2`: *"Think of **that same job site**."* | 19 | 29 → **18** |
| **Total** | **23** | **16** | seven merges, one per entry | **106** | **238 → 160** |

**Three derived numbers, and each one is a reason the constant bumps.**

1. **Design §7.3's ceiling falls from 358 to 252.** `12×2 + 12×2 + 12×2 + 12×2 + 20×4 + 19×2 + 19×2`
   — person-anchor pairs before blanks.
2. **`anchoring_accuracy`'s real denominator falls from 238 to 160** at `N=1` (`given`, the pairs a
   person actually wrote under), and threefold at the `N=3` of a full run.
3. **The golden anchorings go `ANCHORED` 199 / `GUESSED` 39 to `ANCHORED` 136 / `GUESSED` 24.**
   `guessed_recall` and `guessed_precision` are measured over a third fewer judgements than before
   and are not comparable across the bump.

**Selection counts do not move.** 87 selections across the seven entries before and after: a merge
moves a selection from one anchor to another, it never deletes one. The *control* collapse of design
§6A is production's — a later stage reading an earlier line's measurement — and **the frozen corpus
contains no restated measurement to collapse**, because its beliefs were authored by hand against
one questionnaire in the first place. That is the corpus being right all along, exactly as design
§3.4 item 3 says.

**Anchor ids are not renumbered.** The merged anchor keeps `A1`; `A2` is struck; `A3` stays `A3` and
`05-paidly`'s `A2b`/`A2c` keep theirs. A gap in the numbering is harmless once the match key is the
bare id, and renumbering would make every per-anchor row in every bundle on disk unreadable against
the new corpus for no gain.

**The two merges that are not clean, and what each one is decided as.** Both are in
`02-compliancelog`, and they are the only two people in 106 whose `A1` and `A2` cannot simply be
concatenated.

- **Georgia Papadopoulos** — `A1` is blank with a tap of *hasn't happened*; `A2` carries words
  (*"We don't really pull figures. Managers keep their own sheets and I trust them."*) and a golden
  `GUESSED`. **The tap wins.** Her merged anchor carries the tap and no words, and her `A2` sentence
  goes. The reason is not a preference: production's `hasWords()` is `tap == null &&
  !text.isBlank()` (design §4), so an anchor that is both tapped and written is a shape production
  would never read — and under one occasion the thing she said had never happened *is* the occasion.
  This is the one place the revision loses a written pair; it is why the total is 160 and not 161.
- **Daniel Achebe** — `A1` is `GUESSED` (*"It varies with what audit wants. Could be a day, could be
  three."*); `A2` is `ANCHORED` (*"Cornerstone, last month, for a client audit. Their report was
  wrong by about thirty people"*). **The merged anchoring is re-read from the merged text, and it is
  `ANCHORED`**: the merged answer names a particular report on a particular day, which is the
  standard the corpus has always judged by. The hedge about duration survives in the words and no
  longer has an anchoring of its own — which is the honest cost of the merge and is recorded here
  rather than hidden. A precedence rule (*"`GUESSED` wins"*) was considered and rejected: it would
  make the corpus's own word a function of arithmetic rather than of the sentence, and a corpus that
  reasons by rule about what a person said has stopped being a corpus.

## User scenarios

### User Story 1 — The exporter is asked first what it reads (Priority: P1, and it is T001)

**As** the owner of this rubric, **I want** to know before a word of it is written whether the eval
scores the *applied* belief or the model's *raw answer*, **so that** v8 is the right size.

**Why P1**: design §6A.8 says its own third judgement call *"depends on one fact this pass did not
verify"*, and keel-cloud 049's decision **A-6** makes it that spec's first task and this one's.

**Independent Test**: trace `Answer.result` from `runner.py` to `align.produced_view` and say which
it is.

**The answer, traced at `aa3b584`: it reads the model's raw answer.**

1. `instructions/runner.py:388` — `answer.result = response.get("result")`. That is the structured
   output the host CLI handed back, JSON-schema-validated against keel-cloud's exported contract
   (`validator_module.validate_response`, lines 385–389) and **applied to nothing**.
2. `instructions/run.py:306` — `score_mod.score_assumptions(case, entry, answer.result, …)`.
3. `instructions/score.py:161–163` — `produced = result.get("assumptions")` … `align_mod.align(goldens, produced, judge)`.
4. `instructions/align.py:88–96` — `produced_view` reads `belief.get("expectation")` and yields
   `type: None` when there is none.
5. `align.py:154–155` — `structural_candidate` returns `False` on `not golden.get("type") or
   golden.get("type") != produced.get("type")`, and `is_candidate` then refuses it too, because an
   interval is arithmetic and a judge is never asked.

**And keel-cloud's validator never hands the applied belief back.** `instructions/validate.py` does
shell `./gradlew -q screenContracts --args="validate …"` — but `fold_in` reads only
`accepted`/`refusal`, so what comes back is a verdict, never a resolved `Assumption`.

**So a belief carrying `reads: {stage, line}` and no expectation would never be a candidate, never
align, and recall would fall by one line per reference** — which design §6A.8 calls *"an
alignment-rule change and a real regression, not a rubric question"*. **The alignment change is in
this spec**, as FR-007 and judgement call 27.

**Acceptance**: the finding above is written into `align.py`'s module docstring and into judgement
call 27, with the five line references, so that nobody has to trace it a second time.

---

### User Story 2 — One occasion is one anchor, and the corpus says so (Priority: P1)

**As** the reviewer this eval is, **I want** a corpus anchor to carry the *stages its occasion
serves* rather than the *stage that owns its questionnaire*, **so that** the golden set describes
the product 048 and 049 build.

**Why P1**: `corpus.py`'s own note 3 has said since it was written that *"a corpus questionnaire is
the whole project's"*. What made that only half true was `stage` being a key.

**Independent Test**: `Entry.anchors_for("PROBLEM")` and `Entry.anchors_for("SOLUTION")` on
`03-lullaby` both return `A1`, and `Entry.anchor("A2")` returns `None`.

**Acceptance**:

1. Every corpus anchor carries `stages: [...]`, a non-empty list of `STAGES` members, and **no**
   `stage` key. A file carrying the scalar is a refusal to start.
2. `Entry.anchors_for(stage)` returns the anchors whose `stages` contain it; one anchor may be
   returned for two stages, and the two lists share an object.
3. Anchor ids are unique across the entry's whole questionnaire, and so are selection ids —
   `Q7`, project-wide, asserted against the real seven files.
4. Every belief's `selection` resolves to a selection on **some** anchor of the entry, and that
   anchor's `stages` contain the belief's own stage.
5. Every person's `anchors` block names only ids the questionnaire carries, and no person names
   `A2` on any of the seven entries.

---

### User Story 3 — The match key is the bare id, and the denominator says the score is new (Priority: P1)

**As** a reader of a scorecard, **I want** `anchoring_accuracy` scored on the id the project's one
questionnaire actually uses, **so that** a merged occasion serving two stages is one judgement and
not two that cannot both be made.

**Why P1**: `score_reading`'s docstring today says *"Matched by `(stage, anchorId)`, never the bare
id"* and cites decision 18. 049 supersedes decision 18; the docstring cannot simply be deleted,
because the reason it existed is the reason the bump is needed.

**Independent Test**: a reading result whose anchorings carry no `stage` at all scores a full
`anchoring_accuracy` against a merged fixture entry.

**Acceptance**:

1. `score_reading` builds `given` and `produced` keyed on the bare `anchorId`; an anchoring with no
   `stage`, or with one, is neither rejected nor read for it.
2. `context.anchors_for` writes `{anchor_id, prompt, text, tap}` and no `stage`, which is what
   `interpret.md` has said its context is all along (design §5.2's drift).
3. `missing_ids` and `extra_ids` are bare ids and the set arithmetic is over bare ids.
4. The scorecard records `anchors_given` **160** at `N=1` over the revised corpus, and the verdict
   says the score is not comparable with any v7 score.

---

### User Story 4 — The eval gains the screen that writes the questionnaire (Priority: P1)

**As** the owner of `rule_refusal_rate`, **I want** one `QUESTIONS` case per corpus entry, **so
that** `Q8` — a rule that is new, reachable and the one thing standing between the product and two
anchors for one night — is measured rather than assumed.

**Why P1**: design §9.1 says of both screens *"Read `rule_refusal_rate` first (`Q8` is new and
reachable)"*. A mark whose new rule no case can reach is judgement call 13's *unmeasured mark*.

**Independent Test**: `build_cases` on one entry at `n_runs=1` emits three assumptions cases, then
one `QUESTIONS` case, then the readings, then the brief — in that order, with case id
`<entry>/QUESTIONS/run1`.

**Acceptance**:

1. One `QUESTIONS` case per entry per run index, built **after** the entry's three assumptions cases
   because that is the order production runs them in (048 FR-022: the job fires on the approval that
   makes every framed stage approved).
2. Its context is 048 FR-011's — `{project_name, market, founder_name, stage_statements,
   measurements[]}` — built from the entry's own beliefs, indexed 0-based **project-wide across all
   three stages**, each entry carrying its stage.
3. Its instruction is `questions.md`, read through `instruction.read` from keel-cloud's own resource
   directory, `.strip()`ed and not templated.
4. Its contract is keel-cloud's exported `QUESTIONS` contract, read through `contract.export`, never
   restated here.
5. It routes to the `questions` class, which keel-cloud's table puts on the `light` tier — Haiku 4.5
   — and carries **no** `effort` key, for the reason a reading carries none.
6. The three `*_ASSUMPTIONS` cases are unchanged in every way except that their result no longer
   carries a `questionnaire`, and **nothing scores them for one**.
7. `-k questions` selects the new cases, beside `-k reading` and `-k brief`.
8. The `QUESTIONS` answer is **not scored**. It goes to the aggregate (User Story 5) and to
   `register.html` (FR-016).

---

### User Story 5 — A referencing belief is resolved before it is aligned (Priority: P1)

**As** the owner of `golden_belief_recall`, **I want** a produced belief that carries
`reads: {stage, line}` to be given the referent's expectation before alignment, **so that** 049's
*one number, asked once* does not read as a model that forgot to write a band.

**Why P1**: User Story 1's finding. Without it, every reference is an unaligned belief and recall
falls by one line per reference on an instruction change that was supposed to move it by nothing.

**Independent Test**: a produced set with one `reads`-carrying belief aligns to the same goldens,
with the same eight fields, as the same set with the expectation written out longhand.

**Acceptance**:

1. `align.resolve_reads(produced, earlier_lines)` copies the referent's whole `expectation` — the
   `Measure`, the `Bound`s, or the `options` and `expected` — onto the referencing belief, and
   nothing else. `risk`, `mark`, `founderPhrase`, `heading` and `statement` stay the belief's own.
   It is `ScreenResultApplier`'s step 2 of design §6A.5, done here because nothing does it here.
2. It resolves against **the `earlier_lines` this eval built and sent**, not against the model's
   earlier answers: the ordinal is into the list the context numbered, and this eval numbered it from
   the corpus's own golden beliefs of the earlier approved stages. Deterministic, no model, no
   server.
3. A `reads` that names a line out of range, a stage that is not an earlier one, or a belief that
   itself reads another is **not resolved** — it is counted as `unresolved_reads`, reported per case
   and in the totals, and the belief goes to the aligner as it arrived, where it will not match. That
   is production's derivation failure, scored the only way an eval with no repair turn can score it.
4. A belief that carries **both** `reads` and an expectation keeps its own and is counted in
   `unresolved_reads` as a shape the contract refuses (design §6A.5: *"Both, or neither, is a shape
   refusal"*).
5. `align.FIELDS` does not change and `compare()` does not change. What changes is that a
   referencing belief arrives at them whole.

---

### User Story 6 — The aggregate is shown the new answers, so its refusals are real (Priority: P2)

**As** the owner of `shape_refusals` — an absolute zero — **I want** the validation batch to carry
what the applier needs, **so that** a referencing belief is not refused by keel-cloud for a fault
this eval created.

**Why P2**: it cannot break until 049 lands, and then it breaks the whole run at once.
`validate.build_batch` sends `case_id`, `screen`, `market`, `roles`, `statement` and `result` — and
**not** the earlier stages' beliefs. Under 049, `ScreenResultApplier` resolves a `reads` against
those beliefs; with nothing to resolve against it refuses every one as a derivation failure, and
`shape_refusals` — marked at zero — goes to the number of references the corpus provoked.

**Independent Test**: a batch built from a `COMMERCIAL` case whose result carries one `reads` names
the earlier stages' beliefs in the same order the case's own `earlier_lines` numbered them.

**Acceptance**:

1. A batch case carries `earlier_beliefs` — the approved earlier stages' beliefs, per stage, in the
   order `context.earlier_lines` numbered them — so a `{stage, line}` resolves in the validator
   exactly as it resolved in `align.resolve_reads`.
2. A batch gains a `QUESTIONS` case kind whose result the validator applies through
   `writeQuestionnaire`, so `Q5`, `Q6`, `Q7` and `Q8` are reachable and counted by rule id in
   `refusals_by_rule`.
3. If keel-cloud's `screenContracts validate` does not take either shape, the run **says so by
   name** and reports the affected marks as unmeasured. An unmeasured mark is not a met mark
   (judgement call 13), and a green run that never showed the aggregate a questionnaire is the one
   way this rubric could flatter itself.

---

### User Story 7 — The journey reads a page whose sections are occasions (Priority: P2)

**As** the referee of the whole product, **I want** S-012 to notice that the participant page now
has one section per occasion and that the founder's preview names the minutes once, **so that** the
change a founder actually feels is measured by something.

**Why P2**: the participant leg is already section-agnostic — `_answer_whatever_is_asked`
(`evals/test_s012_journey_through_a_host.py:623–688`) calls `participant.anchors()` and iterates the
flat list, never touching `.sect` — so nothing is broken today. What is missing is that nothing
asserts the change either, and two places elsewhere assume a section is a stage.

**Independent Test**: against a two-section fixture page, `ParticipantPage.sections()` returns two
titles and neither is one of the three stage strings.

**Acceptance**:

1. `ParticipantPage.sections()` — defined at `harness/browser.py:3104–3105`, selector `.sect`, and
   **called by nothing in the repository today** — becomes load-bearing: S-012 asserts that the
   number of section titles equals the number of anchor blocks `anchors()` returns, and that none of
   *About your work*, *About a possible tool* or *About buying software* is among them.
2. `PeoplePage.go_to_preview()` already returns the preview text; a new `preview_minutes()` reads
   the *"About N minutes"* figure out of it, and S-012 asserts the preview carries **exactly one**
   such line and that `N >= 10`. Nothing asserts an exact N: the anchors and selections on a live
   page are the model's own, and spec 016 FR-007 stands.
3. `go_to_preview`'s docstring stops promising *"the sections by stage"*.
4. `evals/tools/curated_proof_run.py`'s `rank_of` (lines 657–658) stops reading `anchor["stage"]`,
   and `_sectioned_blocks`' rationale (*"a page with three sections in stage order is the ordinary
   case"*, lines 762–785) is replaced by one section per occasion in questionnaire order. Its
   existing graceful degradation on a count mismatch stays.
5. `tests/test_journey_through_a_host.py:194` — `assert len(stories) == 3, "she wrote under all
   three of her role's anchors"` — becomes **2**, and its message becomes *"she wrote under both of
   her role's anchors"*. Amira Saleh wrote under `A1`, `A2` and `A3`; `A1` and `A2` are now one.
6. `tests/test_corpus_script.py:352` — `assert len(entry.anchors_for("PROBLEM")) == 1` — **still
   passes unchanged**, because `01-countly`'s merged `A1` carries `PROBLEM` in its `stages`. It is
   kept, and a sibling assertion is added that the same anchor is also returned for `SOLUTION`.
7. `evals/corpus_facts.py:174/191` stop keying fact ids on a stage: `anchor.{id}` and
   `said.{slug}.{anchorId}`. `harness/browser.py`'s `answer_as` (3330–3334) and `_selection_block`
   (3199–3205) keep their scoping — two anchors on `05-paidly` still ask the identical question, and
   scoping to the anchor is still what tells them apart — but the decision-18 citations are
   rewritten to the project-wide id space.

---

### User Story 8 — The run of record is spent, once, and it certifies everything above (Priority: P1)

**As** the founder, **I want** one run that proves the revised corpus, the new match key, the new
screen, the resolved references and the new constant are green together, **so that** `make
instruction-eval`'s standing gate means something again.

**Why P1**: `README.md`'s own gate reads *"the instruction eval's run of record **green at the
current `MARKS_VERSION`**"*, and `MARKS_VERSION` 8 has no green run until one is spent. Design
§8.2: all three of *a mark's number*, *a metric definition* and *an alignment rule* move here, so
`assumptions-step-design.md` §9.1's *ship on the screen, re-price on the run* does not apply.

**Independent Test**: none. This is the paid one, and it is the founder's to type.

**Acceptance**: FR-024 and SC-012.

## Requirements

**The rubric**

- **FR-001** `instructions/marks.py`'s `MARKS_VERSION` MUST be **8**.
- **FR-002** The four v8 judgement calls MUST be appended to `marks.py`'s list, struck nowhere, in
  the words the plan sets out verbatim (plan §2, *The four v8 judgement calls*).
- **FR-003** Judgement call **23** — cited by `marks.toml` as v7's and absent from `marks.py`'s
  list at `aa3b584` — MUST be transcribed into the list from `marks.toml`'s own words before 24 is
  appended, so that the list is what it says it is: append-only and complete. **It is a
  transcription, not a new call**: no number and no rule moves.
- **FR-004** No number in `marks.toml`'s `[marks]` table may move. `marks.toml` MUST gain a v8
  header stating what moved and that scores before and after are not comparable.
- **FR-005** Every artefact a run writes — `verdict.json`, `scorecard.json`, `manifest.json` and
  `register.html` — MUST carry `8`, and `rescore.py` MUST keep writing beside rather than over.

**The corpus**

- **FR-006** `Entry.anchors_for(stage)` MUST return the anchors whose `stages` **contain** `stage`,
  and `corpus.load` MUST refuse an entry whose anchor carries the scalar `stage`, naming the entry,
  the anchor and this specification.
- **FR-007** The revision MUST be exactly the table above: seven `A1 + A2` merges, `05-paidly`'s
  `A2b` and `A2c` untouched, ids not renumbered, selections not moved between entries, and the two
  `02-compliancelog` people decided as stated. **23 anchors → 16; 238 written pairs → 160.**
- **FR-008** The revision MUST be landed as a keel-cloud commit. **This repository MUST NOT carry a
  corpus file**, and `tests/` MUST assert the shape (`stages` a list, ids unique project-wide, every
  belief's selection reachable, no person naming a struck id) against the real files rather than a
  copy.

**The marks that read the corpus**

- **FR-009** `score_reading` MUST key on the bare `anchorId`, MUST NOT read a `stage` off a produced
  anchoring, and MUST NOT refuse one that carries one. Its decision-18 paragraph MUST be replaced by
  one naming 049 and this spec, not deleted.
- **FR-010** `context.anchors_for` MUST write `{anchor_id, prompt, text, tap}` and no `stage`.
- **FR-011** `align.resolve_reads` MUST exist, MUST be called by `score_assumptions` before
  `align.align`, MUST copy the referent's whole expectation and nothing else, MUST refuse a chain,
  an out-of-range ordinal and a both-at-once belief, and MUST report `unresolved_reads` per case and
  in `totals`. `align.FIELDS` MUST NOT change.

**The new screen**

- **FR-012** `models.CLASSES` MUST gain `"questions"`, and `KIND_TO_CLASS`/`SCREEN_TO_CLASS` their
  rows. **Without this the eval cannot start at all against 048's table**: `models.parse` raises
  `ModelsUnavailable` on an unknown class name (`models.py:199–202`), and 048 FR-009 adds
  `JobClass.QUESTIONS` to the table keel-cloud exports. `models_used` and `efforts_used` MUST report
  four classes, so the verdict says which model wrote the questionnaires.
- **FR-013** `instruction.STEMS` MUST gain `"QUESTIONS": "questions"` and `contract` MUST gain
  `SCREEN_QUESTIONS`.
- **FR-014** `context.build_questions` MUST build 048 FR-011's context and no more, with
  `measurements` indexed 0-based project-wide across the three stages.
- **FR-015** `prompts.build_cases` MUST emit one `QUESTIONS` case per entry per run index, after the
  three assumptions cases, with case id `<entry>/QUESTIONS/run<N>`, selectable by `-k questions`.
- **FR-016** `report.register_blocks` MUST group the produced questionnaire **by entry** and put the
  entry's whole revised anchor list beside it. The register MUST NOT gain a score, a tick or a cross
  (judgement call 10).
- **FR-017** The `QUESTIONS` answer MUST NOT feed `anchoring_accuracy`, `golden_belief_recall` or
  `brief_paragraphs`, and MUST NOT add a mark.

**The aggregate**

- **FR-018** `validate.build_batch` MUST carry the earlier stages' approved beliefs per case, in the
  order `context.earlier_lines` numbered them, and MUST emit a `QUESTIONS` case kind.
- **FR-019** A validator that does not take either shape MUST make the run report the affected marks
  **unmeasured** and name the prerequisite. It MUST NOT be softened to a warning and MUST NOT be
  scored as a refusal.

**The journey and the harness**

- **FR-020** `harness/corpus_script.py` MUST match a belief's stage against the anchor's `stages`
  list in `role_of_anchor`, MUST stop putting a `questionnaire` on the scripted `*_ASSUMPTIONS`
  results, MUST emit one `QUESTIONS` script entry per entry, and MUST drop `stage` from the
  anchoring export. A script that drifts from the corpus is still never committed.
- **FR-021** S-012 MUST assert, as shape and never as prose: one section title per anchor block,
  none of them one of the three old stage strings; and exactly one *"About N minutes"* line in the
  founder's preview, with `N >= 10`. No exact anchor count, no exact minutes, no verdict word (spec
  016 FR-007).
- **FR-022** `evals/corpus_facts.py`, `evals/tools/curated_proof_run.py` and `harness/browser.py`
  MUST stop deriving a page position or a fact id from an anchor's stage.

**The run**

- **FR-023** `why.py` MUST gain `WHY=marks:<version>` as a **full-run** event, with the policy text
  saying why: a rubric that moved has no green run until one is spent, and neither `instruction:`,
  `prompt:`, `contract:` nor `new-model:` describes this run. The existing four events MUST NOT
  change.
- **FR-024** The run of record MUST be taken at the combination spec 047 certified —
  `claude-sonnet-5-5` at effort `medium`, through `MODELS=exported` so the effort travels on the
  job's own key — on the CLI only, with the judge at the CLI's own default (`judge.py`'s
  `JUDGE_UNSET_ENV` strips `CLAUDE_CODE_EFFORT_LEVEL`, `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` and
  `CLAUDE_CODE_MAX_EFFORT_REMINDER`, and nothing in this change may export them). The exact command
  and its price are in tasks **T030**.

## What is deliberately not built

- **No corpus in this repository, and no second reader of it.** Spec 021 deviation 3, unchanged.
- **No `Q9`, no rule re-implemented here.** `validate.py`'s whole argument is that the only honest
  way to ask what the aggregate refuses is to hand it to the aggregate.
- **No mark for the questionnaire**, and no `occasion` similarity metric. Two anchors with two
  spellings of one occasion are what `register.html` and the founder's review pass are for — design
  §6 says so plainly.
- **No repair turn.** Production gives a derivation failure one; this eval has never had one and is
  not gaining one. An unresolvable `reads` is counted and reported, never retried.
- **No re-score of a v7 bundle to v8.** The corpus moved; see *What this spec does not do*.
- **No second run.** One run of record covers 048 and 049 together, after both have landed, and it
  is spent once.
- **No schedule, no CI, no "to be sure".** `AGENTS.md`'s rule for the instruction eval stands
  whole, and FR-023 widens the `WHY` policy by one named event rather than loosening it.
- **No change to `evals/policy.py`.**

## Success criteria

- **SC-001** `MARKS_VERSION` is 8, with 27 judgement calls, numbered 1–27 with none missing and none
  struck.
- **SC-002** The seven corpus entries carry 16 anchors, every one with a non-empty `stages` list and
  no `stage`, and `make unit` proves it against the real files.
- **SC-003** `Entry.anchors_for("PROBLEM")` and `Entry.anchors_for("SOLUTION")` return the same
  merged anchor on all seven entries.
- **SC-004** A reading result whose anchorings carry no `stage` scores `anchoring_accuracy` 1.0
  against a merged fixture; one with a `stage` scores the same.
- **SC-005** A produced set with one `reads`-carrying belief aligns identically to the same set with
  the expectation written longhand, on all eight fields.
- **SC-006** `-k questions` on one entry at `N=1` builds exactly one case, after the three
  assumptions cases, on the `light` tier and with no `effort` key.
- **SC-007** `MODELS=exported` starts against a table carrying a `questions` class, and refuses by
  name against a table carrying an unknown one.
- **SC-008** `register.html` renders one produced questionnaire per entry beside the entry's whole
  revised anchor list, and carries no score.
- **SC-009** `make unit` is green, and the S-012 section and minutes assertions pass against
  fixtures.
- **SC-010** `WHY=marks:8` earns the full run; `WHY=marks:8` on a screen is refused with the policy;
  no `WHY` still refuses at the door.
- **SC-011** Every bundle carries `corpus.sha256` before and after, and the after digests match the
  before ones — `Corpus.verify_unchanged()` is untouched and still fails a run outright.
- **SC-012** **The run of record is green on all five marks at `MARKS_VERSION` 8**, at
  `claude-sonnet-5-5` / effort `medium`, in about 2.5 hours for about $15; its `anchors_given` is
  three times 160; its `refusals_by_rule` shows `Q8` at most once across the corpus; its
  `shape_refusals` is 0; and its `unresolved_reads` is reported. The bundle, the verdict and the
  number go into `README.md` and, if anything surprised, into `runs/DRIFT.md`.
