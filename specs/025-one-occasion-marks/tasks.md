# Tasks: one occasion, one anchor, one rubric

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `025-one-occasion-marks`

`make unit`: **green at every commit on this branch.** Baseline at `04fcb50`, before a line was
written: **1,141 passed** (Discovered D1). This file was drafted ahead of both siblings (keel-cloud
was on `048-lines-then-questions` at `71e6fe7`, phase 1 only); both have since landed, and the order
below is the order the work was actually done in.

**Tests first.** Every phase's own tests are written before the code that turns them green, and
**no test is deleted to make a phase pass**.

**Amended at implementation (Discovered D11).** As drafted, every test sat in Phase 2 and `make
unit` was red across the Phase 2 commit. The rule this repository works to is the gate green before
every commit — which is how keel-cloud's sibling 049 ran too, one phase at a time with `./gradlew
check` green each time. So **each of T010–T019 lands in the commit of the phase it certifies**,
written first within that phase and ticked there.

**And the corpus is why the first commit is wide.** T022 revises keel-cloud's seven files, and from
the moment it does, everything here that read an anchor's `stage` is red — the corpus reader, the
reading context, the match key, the script generator, the fact registry and the proof tool. They
land in one commit, which is the *one commit wide* red window plan §4 predicted, named rather than
papered over.

**Nothing below spends a model call except T030**, which is the founder's to type.

## Phase 1 — read before writing anything

- [X] **T001 — the exporter question, answered before anything else is written.** Design §6A.8:
      *"That answer depends on one fact this pass did not verify … Spec 049's first task is to check
      it; it is one file."* keel-cloud 049's decision A-6 makes it this spec's first task too.

      **Traced `instructions/` end to end at `master` `aa3b584`. The answer: the exporter reads the
      model's RAW answer. It never sees an applied belief.**

      1. `instructions/runner.py:388` — `answer.result = response.get("result")`. The structured
         output the host CLI returned. It is JSON-schema-validated against keel-cloud's exported
         contract (`runner.py:385–389`, `validator_module.validate_response`) and **applied to
         nothing**.
      2. `instructions/run.py:306` — `score_mod.score_assumptions(case, entry, answer.result, …)`.
      3. `instructions/score.py:161–163` — `produced = result.get("assumptions")`, then
         `align_mod.align(goldens, produced, judge)`.
      4. `instructions/align.py:88–96` — `produced_view` reads `belief.get("expectation")`; with no
         expectation it yields `type: None`.
      5. `instructions/align.py:154–155` — `structural_candidate` returns `False` on
         `not golden.get("type") or golden.get("type") != produced.get("type")`; `is_candidate`
         then refuses too, because *"an interval is never judged"* and the judge is never asked.

      **And keel-cloud's validator does not close the gap.** `instructions/validate.py` shells
      `./gradlew -q screenContracts --args="validate <batch> <report>"` and `fold_in` reads only
      `accepted` and `refusal` — a verdict, never a resolved `Assumption`.

      **Consequence, and it is the spec's:** a belief carrying `reads: {stage, line}` and no
      expectation would never be a candidate, never align, and `golden_belief_recall` would fall by
      one line per reference — design §6A.8's *"an alignment-rule change and a real regression, not a
      rubric question"*. **So v8 carries four judgement calls, not three** (spec FR-002, plan §2),
      and `align.resolve_reads` is FR-011.

- [X] T002 keel-cloud `canon/designs/one-occasion-once-design.md` §3, §4, §5, §6, §6A, §7, §8, §9,
      §10 and §12 — the rule, the participant's page, the data model, `Q8`, the cross-stage half,
      the numbers, **what the marks and the corpus need**, the gates, the risks, and the amendment
      that records the founder's approval of both changes and the 048/049 split.
- [X] T003 keel-cloud `specs/048-lines-then-questions/spec.md` and `specs/049-one-occasion-once/spec.md`
      — their stated requirements on this repository, their *Mark implications* tables, and 049's
      decisions A-6, A-8 and A-9. **Finding**: both say in as many words that they edit no file here
      and satisfy none of these requirements.
- [X] T004 keel-cloud `canon/designs/measured-beliefs-design.md` §3.6, §5 and **decision 18** — the
      reason `(stage, anchorId)` exists, so that `score_reading`'s docstring is replaced rather than
      deleted.
- [X] T005 The seven corpus entries, **counted**: anchors, selections, people, written person-anchor
      pairs, golden anchorings, and which anchors would merge. The result is spec *The corpus
      revision, entry by entry*. **Findings**: 23 anchors → 16; 238 written pairs → 160; `ANCHORED`
      199 → 136 and `GUESSED` 39 → 24; 87 selections, unchanged; and **exactly two people in 106**
      whose `A1` and `A2` cannot be concatenated, both in `02-compliancelog`.
- [X] T006 `instructions/` line by line — `corpus.py` (the hash and the freeze rule), `context.py`,
      `prompts.py`, `score.py`, `align.py`, `marks.py`/`marks.toml`, `models.py`, `validate.py`,
      `report.py`, `rescore.py`, `judge.py`, `why.py`, `instruction.py`, `contract.py`.
      **Three findings beyond T001**, each of which became a requirement:
      1. `models.parse` (`models.py:199–202`) raises `ModelsUnavailable` on an unknown class name,
         so **`MODELS=exported` refuses to start** against 048's table the moment it names
         `questions` (FR-012).
      2. **Judgement call 23 is cited in `marks.toml` and missing from `marks.py`'s list** — the
         list is supposed to be append-only and complete (FR-003).
      3. `report.register_blocks` (`report.py:675–691`) reads the produced questionnaire off the
         **assumptions** result per stage; under 048 that is empty and the register goes blank
         (FR-016).
- [X] T007 `harness/corpus_script.py`, `harness/browser.py`'s `ParticipantPage` and `PeoplePage`,
      `evals/test_s012_journey_through_a_host.py`'s participant leg, `evals/tools/curated_proof_run.py`
      and `evals/corpus_facts.py`. **Findings**: the participant leg is already section-agnostic
      (`_answer_whatever_is_asked`, lines 623–688, iterates `participant.anchors()` flat and never
      touches `.sect`); `ParticipantPage.sections()` (`browser.py:3104–3105`) is **dead code**, called
      by nothing; **nothing anywhere reads a minutes line**; `curated_proof_run.py`'s `rank_of`
      (657–658) and `_sectioned_blocks` (762–785) are the one place that hard-assumes one `.sect`
      per stage in stage order; and `tests/test_journey_through_a_host.py:194`'s
      `assert len(stories) == 3` is the one hard count that encodes one anchor per stage.
- [X] T008 `AGENTS.md` and `.specify/memory/constitution.md`. **Finding**: the constitution is an
      **unfilled template** at `aa3b584` — every principle is still `[PRINCIPLE_N_NAME]` — so there
      is nothing to check against and `AGENTS.md` is this repository's governing document. Recorded
      in the spec's *Input* rather than left as a silent gap.
- [X] T009 `specs/021-short-journey/`, `specs/023-staging-on-demand/` and `specs/024-keels-ai-cell/`
      — the shape this repeats: the one sentence, what it does not do, the siblings table, what
      changes stated first, the FR/SC numbering, the plan's decisions, the tasks' phases and the
      paid tasks left unticked at the end.

## Phase 2 — the tests, first and red

- [X] T010 `tests/test_instruction_marks.py` (new): `MARKS_VERSION == 8`; the judgement-call list
      parses to 1–27 with none missing, none struck and none renumbered; every number in
      `marks.toml`'s `[marks]` equals its value at `aa3b584`.
- [X] T011 `tests/test_corpus_script.py`: the corpus shape, against **the real seven files** —
      every anchor carries a non-empty `stages` list and no `stage`; anchor ids and selection ids are
      unique across an entry; every belief's `selection` is on an anchor whose `stages` contain that
      belief's stage; no person names a struck id; the seven entries carry **16** anchors and **160**
      written person-anchor pairs. Keep `assert len(entry.anchors_for("PROBLEM")) == 1` for
      `01-countly` and add the sibling assertion that the same anchor is returned for `SOLUTION`.
- [X] T012 `tests/test_instruction_score.py`: `score_reading` on the bare id — a result whose
      anchorings carry no `stage` scores 1.0 against a merged fixture; one that carries a `stage` is
      neither refused nor read for it; `missing_ids`/`extra_ids` are bare ids.
- [X] T013 `tests/test_instruction_reads.py` (new): `align.resolve_reads` — a `reads`-carrying belief
      aligns identically to the same belief with the expectation longhand, on all eight fields; an
      out-of-range ordinal, a stage that is not earlier, a chain and a both-at-once belief are each
      counted in `unresolved_reads` and left unmatched; `align.FIELDS` is unchanged.
- [X] T014 `tests/test_instruction_context.py`: `anchors_for` writes no `stage`; `earlier_lines`
      carries design §6A.4's eight keys and no more, 1-based within each stage, and is empty for
      `PROBLEM`; `build_questions` carries 048 FR-011's five keys with `measurements` 0-based
      project-wide.
- [ ] T015 `tests/test_instruction_models.py`: a table naming `questions` parses; one naming an
      unknown class still refuses by name; `models_used`/`efforts_used` report four classes; the
      `questions` class resolves to the `light` tier and to **no** effort.
- [ ] T016 `tests/test_instruction_questions.py` (new): `build_cases` on one entry at `n_runs=1`
      emits three assumptions cases, then exactly one `QUESTIONS` case with id
      `<entry>/QUESTIONS/run1`, then the readings, then the brief; `-k questions` selects it; its
      payload carries `questions.md` and keel-cloud's exported `QUESTIONS` contract.
- [ ] T017 `tests/test_instruction_validate.py` (new or extended): a batch case carries
      `earlier_beliefs` in the order `earlier_lines` numbered them; a `QUESTIONS` case kind is
      emitted; a validator that does not know either shape makes the run report the marks unmeasured
      and name the prerequisite.
- [ ] T018 `tests/test_instruction_why.py`: `WHY=marks:8` earns the full run and not a screen;
      `WHY=marks` with no version is refused; the four existing events are unchanged.
- [ ] T019 `tests/test_journey_through_a_host.py`: the story count becomes **2** with the message
      *"she wrote under both of her role's anchors"*; and, against a fixture page, one section title
      per anchor block with none of the three old stage strings, and exactly one *"About N minutes"*
      line with `N >= 10`.

## Phase 3 — the rubric

- [X] T020 `instructions/marks.py`: `MARKS_VERSION = 8`; judgement call **23** transcribed in from
      `marks.toml`'s own words; **24, 25, 26 and 27** appended in plan §2's words verbatim.
      `DEFAULTS` and `judge()` untouched.
- [X] T021 `instructions/marks.toml`: the v8 header — what moved, what did not, and that scores
      across the bump are not comparable. **No number in `[marks]`.**

## Phase 4 — the corpus

- [X] T022 **The revision, as a keel-cloud commit**, against spec *The corpus revision, entry by
      entry*: seven `A1 + A2` merges; `stage` → `stages` on every anchor; merged prompts, merged
      answer texts, merged taps and re-read anchorings; `05-paidly`'s `A2b`/`A2c` untouched; ids not
      renumbered; the two `02-compliancelog` people decided as the table says. **This branch writes
      no corpus file.** `make unit` here is red until that commit lands, and that is the point.
- [X] T023 `instructions/corpus.py`: `Entry.anchors_for` matches the list; `_entry` refuses a scalar
      `stage` by entry and anchor id; note 3 of the docstring rewritten. T011 goes green.

## Phase 5 — the marks that read the corpus

- [X] T024 `instructions/score.py`: `score_reading` on the bare id, its decision-18 paragraph
      replaced by one naming 049 and this spec; `score_assumptions` calls `resolve_reads` before
      `align`; `unresolved_reads` per case and in `totals`. `instructions/context.py`:
      `anchors_for` drops `stage`; `earlier_lines` added. T012, T013 and part of T014 go green.
- [X] T025 `instructions/align.py`: `resolve_reads`, and T001's finding written into the module
      docstring with its five line references so nobody traces it twice. `FIELDS`, `produced_view`,
      `compare` and `align` untouched.

## Phase 6 — the new screen

- [ ] T026 `instructions/contract.py`, `instruction.py`, `models.py`, `context.build_questions`,
      `prompts.build_cases`, `run.py`'s `-k questions` and printed line, and
      `report.register_blocks` regrouped by entry. T014, T015 and T016 go green.

## Phase 7 — the aggregate

- [ ] T027 `instructions/validate.py`: `earlier_beliefs` on every assumptions case; the `QUESTIONS`
      case kind; the named refusal when keel-cloud's validator knows neither. T017 goes green.

## Phase 8 — the journey, the harness and the `WHY`

- [ ] T028 `harness/corpus_script.py` (`role_of_anchor` against the list, the questionnaire off the
      assumptions result and onto a `QUESTIONS` script entry, the anchoring export losing `stage`);
      `harness/browser.py` (`sections()` load-bearing, `preview_minutes()`, the two decision-18
      citations rewritten); `evals/corpus_facts.py`; `evals/tools/curated_proof_run.py`;
      `evals/test_s012_journey_through_a_host.py`'s two shape assertions; and `instructions/why.py`'s
      `marks:` event. T018 and T019 go green.

## Phase 9 — the documents

- [ ] T029 `README.md` and `AGENTS.md`: the v8 gate, the fifth `WHY` event, the new denominator, and
      the note that a v7 bundle **cannot** be re-scored to v8 because the corpus moved. This
      specification, its plan and these tasks updated with whatever the work found.

## Phase 10 — the run, which is the founder's to spend

- [ ] **T030 — the run of record.** After 048 and 049 have both landed, after T022's corpus commit,
      and after `make unit` is green. One run, once.

      ```sh
      cd /Users/athulrajeev/Documents/projects/keel-e2e-eval
      make instruction-eval HOST=claude WHY=marks:8 MODELS=exported
      ```

      **What each part of it is, and why no part of it may be dropped.**

      - `HOST=claude` — the Claude Code CLI, which is what spec 047 certified and what
        `keel-skill-design.md` §5.5's *supported* gate is read on. **CLI only**: no API path, no
        `KEEL_CLAUDE_MODEL`, no second host. A Copilot run is a different measurement and is never
        averaged with this one.
      - `WHY=marks:8` — FR-023's new event. The run spends because the **rubric** moved, and the
        reason goes into the bundle's `manifest.json` so the bundle says why it exists.
      - `MODELS=exported` — keel-cloud's own routing table, written beside the contracts by its
        exporter. It pins `claude-sonnet-5-5` on the `standard` tier for `assumptions` and `brief`,
        Haiku 4.5 on `light` for `reading` and the new `questions`, **and it carries the effort on
        the job's own key**: `medium` on the standard rows, nothing on the light ones. This is spec
        047's certified combination and spec 024's mechanism.
      - **`CLAUDE_CODE_EFFORT_LEVEL` is not exported, by anyone, anywhere near this run.** It is
        process-wide and would reach the judge as well as the subject — which is why
        `instructions/judge.py`'s `JUDGE_UNSET_ENV` strips it, `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT`
        and `CLAUDE_CODE_MAX_EFFORT_REMINDER` by name. **The judge answers at the CLI's own
        default**, and the bundle records the subject's effort in `manifest.json`'s
        `effort.per_class` and in the verdict's `efforts_used`.
      - `N` is left at its default of **3**. A case that passes twice and fails once is an unstable
        instruction, and the spread is what says so.

      **The price, and where each figure comes from.**

      | | |
      |---|---|
      | Time | **~2.5 h** — spec 047's run `20260930T024851Z-instructions`, **measured** |
      | Money | **~$15** — the same run cost **$15.19**, **measured** |
      | Job-runs | **393 → ~414**: 63 assumptions + **21 `QUESTIONS`** + 309 readings + 21 brief |
      | What makes it cheaper | the 63 assumptions jobs stop emitting a ~570-token questionnaire, and the 309 readings each carry a third fewer anchors (238 → 160 written pairs at `N=1`) |
      | What makes it dearer | 21 Haiku `QUESTIONS` calls at ~$0.027 — **~$0.57** (design §8.2 costs seven, at one per entry; this eval runs `N=3`) |
      | Net | **inside the noise, and downward.** Plan on ~2.5 h and ~$15. |

      **What the run has to show to be the run of record** (spec SC-012): all five marks green at
      `MARKS_VERSION` 8 — `anchoring_accuracy` ≥ 0.90, `golden_belief_recall` ≥ 0.80,
      `rule_refusal_rate` ≤ 0.02, `shape_refusals` = 0, `brief_paragraphs` = 1.00 — with
      `anchors_given` at three times 160, `Q8` firing **at most once** across the corpus,
      `unresolved_reads` reported, and `corpus.sha256` identical before and after.

      **And it is the founder's to start.** Design §11.4, answered on 2026-09-30: *"Yes, after both
      specs land — and it is now ~2.5 h and ~$15."*

- [ ] T031 Whatever T030 finds → `README.md` (the run of record, its table and its bundle name),
      `runs/DRIFT.md` (anything that surprised), and this file. **A red mark is a finding, not a
      reason to run again.**

## Discovered

What the code turned out to say that the spec, the plan or this file did not. Each entry names the
task it was found under. Nothing here is a change of mind about the design; it is what the work met.

- **D1 (baseline).** `make unit` at `04fcb50`, before a line was written: **1,141 passed**, 0
  failed, in 2 m 23 s. That is the number every commit on this branch is held to.
- **D2 (T022).** **keel-cloud's own gate needs three environment variables that no document in
  *this* repository names.** `./gradlew check` without them fails 275 of 1,329 tests on
  `DockerClientProviderStrategy` alone — Testcontainers cannot find the daemon. keel-cloud's
  `AGENTS.md` (lines 78–89) has them: `JAVA_HOME`, `DOCKER_HOST=unix://$HOME/.colima/default/docker.sock`
  and `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, with Colima running. With them:
  **1,548 tests, 0 failures**. Recorded because a green-looking corpus commit taken without them
  would have been a corpus nobody had actually checked.
- **D3 (T022, and it is the one number the spec's table did not carry).** The revision moves
  `02-compliancelog`'s **`expected.standings`**, and nothing in spec *The corpus revision* or FR-007
  said so. Daniel Achebe's merged anchoring is re-read as `ANCHORED`, so his answers now count, and
  all six PROBLEM lines go `inside` +1 / `guessed` −1: `P1` 7/2→8/1, `P2` 4/2→5/1, `P3` 8/3→9/2,
  `P4` 5/3→6/2, `P5` 5/3→6/2, `P6` 7/3→8/2. **No verdict, no drift and no median moves**, and the
  other six entries' `expected` blocks are untouched. `check_corpus.py` found it, which is what the
  corpus's own checker is for.
- **D4 (T022).** **Decision 18 was in keel-cloud's code twice, and neither place was on any list.**
  `canon/designs/measured-beliefs/sim/check_corpus.py` keyed every questionnaire item by
  `(stage, id)` through `model.ref`/`model.resolve`, and
  `src/test/java/…/corpus/CorpusFixture.java`'s `AnchorSpec` carried a scalar `StageType`. Both
  moved with the files: the checker keys by the bare id and `Q1` now asks *does the owning anchor's
  occasion serve this belief's stage*, and `CorpusFixture` carries `List<StageType> stages` and
  **refuses a file still writing the scalar**, by file and by anchor — the same refusal
  `instructions/corpus.py` makes here, for the same reason.
- **D5 (T023).** **This repository has two corpus-shaped fixtures of its own**, and the spec named
  neither: `evals/payroll_exceptions.yaml` (S-013's entry) and `tests/test_corpus_script.py`'s
  `CANNED`. Both carried the scalar `stage` and both now carry `stages`. Neither is the golden
  corpus and neither is merged — `payroll`'s `A2` is genuinely another occasion (*"the last time a
  payroll problem got sorted out without anyone being told to"*), so it keeps its own anchor with
  `stages: [SOLUTION]`. Spec 021's deviation 3 is untouched: still no corpus **copy** here.
- **D6 (T020).** **Three tests outside the marks file pinned `MARKS_VERSION == 7`** —
  `test_instruction_brief.py`, `test_instruction_host.py` and `test_instruction_score.py`. Each was
  asserting something else (the BRIEF number, one rubric for every host, the v6 rate) and using the
  version as a proxy for *nothing moved*. Each now asserts its own claim and leaves the version to
  `tests/test_instruction_marks.py`, which is T010 and the one place that should pin it.
- **D7 (T020).** **Judgement call 22 sits between 16 and 17 in `marks.py`'s list**, out of numeric
  order, and has since v6. It is **left exactly where it is**: the list's rule is append-only and
  struck-nowhere, not sorted, and moving a call would be an edit to the history of what a number
  means. T010 parses the numbers and asserts the *set* is 1–27, which is the claim that matters.
- **D8 (T025).** **A chain cannot arise off this eval's own `earlier_lines`**, so FR-011's
  chain clause had to be given a meaning that is testable here. The eval numbers `earlier_lines`
  from the corpus's golden beliefs, every one of which owns its measurement, and a `reads` names a
  *different* stage's list and so can never name another belief in the same answer. The rule
  implemented is design §6A.5 step 4 stated positively — **the referent must own its
  expectation**: a line that itself carries a `reads`, or that carries neither a `measure` nor an
  `options` list, is not a referent and the reference is counted `unresolved`. It is in the module
  because the contract states it and a list this module is *handed* is not a list it wrote.
- **D9 (T024).** `score_assumptions` reads the case's own
  `payload["context"]["earlier_lines"]` — **the list this eval numbered and sent in that very
  prompt** — and not a second walk of the corpus. One place decides the ordinal, which is the same
  discipline `ScreenContextBuilder.earlierLinesOf` keeps on the other side.
- **D10 (T028, found early because it broke).** `evals/tools/curated_proof_run.py`'s `rank_of`
  read `anchor["stage"]` and ranked by `STAGES.index`. A section is an occasion now, so the rank is
  the anchor's **position in the one questionnaire**. Its graceful degradation on a count mismatch
  is untouched.
- **D11 (the phases).** The ordering amendment at the top of this file: T010–T019 land with the
  phases they certify, so `make unit` is green at every commit. See the note above for why.
