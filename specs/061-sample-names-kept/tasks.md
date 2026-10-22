# Tasks 061

Built against keel-cloud-docs master `bdda576`, keel-web master `b52835c` (092's spec commit on `de15ae8`; no code
since), corpus revision 12, `MARKS_VERSION` 20. Amends spec 060 (`specs/060-sample-snapshot/`).

- [x] T001 FR-1 `evals/sample_export.py`: `PERSON_WORD`, `people_order`, `_people_rows` and `Withheld.names` gone;
  `withhold` no longer takes `people` and touches no person's name. Emails (keys and addresses in a text), the
  founder's name and email, and tokens / links (`withheld`) are withheld exactly as 060 wrote it.
- [x] T002 FR-2 `survivors` checks emails, the founder and tokens and no longer takes `people`; the new `names_kept`
  measures which of the entry's people the output carries, recorded on the FR-2 step (`names kept: 20 of 20`) and as
  `people` in `sample.json`, never gating (judgement call 3).
- [x] T003 FR-3 `tests/test_sample_export.py` edited one for one (24 before, 24 after): the withholding test asserts
  each of the spec's twenty names (written out as `TWENTY`, and equal to the entry's own people) IS in the whole
  output and no `Person <n>`, founder word, token, email or `/i/<token>` link is; the numbering test now holds
  people.json's names to the order served; the one-number test holds a person to one name in every file and the
  pilot's people to the twenty; the whole-words test holds names untouched with the founder still cut out; the
  survivors test finds emails, tokens and the founder and never a name. The fixture is unchanged.
- [x] T004 FR-4 the docstring and 060's spec.md FR-2 each carry one *superseded by 061, 2026-10-22* line; 060's
  tasks.md is not rewritten.
- [x] T005 Acceptance 1 and 3: `make unit` (below); no mark, step of S-006 with the variable unset, or version moved.
- [x] T006 Acceptance 2: `make sample` on the local stack into keel-web's `public/sample/` (below), then `make down`.

## Judgement calls

1. **060's directory is `specs/060-sample-snapshot/`**, not the `060-sample-project` the brief named; the notes went
   there.
2. **The export's FR-2 step is reworded** (`sample (FR-2, spec 061): the people's names kept as served; ...`): the
   060 wording said *names become Person 1 ... Person n*, which would now be false. That step exists only when
   `KEEL_SAMPLE_EXPORT` is set, so S-006's steps with the variable unset are unchanged (060 FR-5).
3. **Names kept is measured, not gated.** FR-2 asks a unit test to assert the twenty names are present; it does not
   add a refusal, and FR-3 says the gate is unchanged. So the export records `names kept: n of 20` and does not refuse
   on it.
4. **`Makefile`'s `sample` comment and `AGENTS.md`'s 060 paragraph** said *names withheld* / *Person 1 ... Person n*;
   each got a minimal amendment naming 061 so neither reads false. No target line changed (`test_make_sample_and_make_eval`
   reads the target, not the comment).
5. **The worktree's `stack.toml`** names `../keel-cloud-docs` etc., which from `wt/eval-061` resolves to nothing; for
   this build its four `[paths]` lines read `../../…` (the same checkouts the main checkout names) under
   `git update-index --skip-worktree`, and were put back byte for byte, flag cleared, after `make down`. Ports and the
   compose project are the defaults (`eval-061_default` network, container `keel-eval-postgres`).
6. **The Python is the main checkout's `.venv`**, passed as `make … PY=<main>/.venv/bin/python`; no venv was created
   in the worktree and nothing was installed.
7. **One `make unit` failure is not 061's**: `tests/test_guide_teaching_marks.py::test_every_present_clip_in_keel_webs_manifest_is_one_the_marks_know`
   fails identically before and after this change, on keel-web master's two landing clips (`landing-intro`,
   `sample-question`, keel-web 091) that the test's allow-list does not name. Out of 061's scope (FR-3: nothing else
   moves); recorded as a DRIFT below, not fixed here.

## DRIFT

- **keel-web 091's landing clips vs. the guide teaching marks' clip test.** keel-web `public/` manifest carries
  `landing-intro` and `sample-question`; `test_every_present_clip_in_keel_webs_manifest_is_one_the_marks_know` allows
  only the teaching clips plus `welcome` and `interviewer-sample`. Adding the two names to the allow-list moves no mark
  (they are not teaching clips), but it is a separate change for its own spec or the operator's word.

## Measured (2026-10-22)

**`make unit`** (`PY=` the main checkout's venv): **2,963 passed / 53 skipped / 1 failed** before the change and
**2,963 / 53 / 1** after (24 in `tests/test_sample_export.py` both times, edited one for one; the one failure is
judgement call 7's, the same test both times). 060's 2,964 / 53 was measured against keel-web `6f89a95`, before 091's
clips.

**Stack** (keel-cloud-docs `bdda576`, keel-web `b52835c` under vite, chromium): `make sample` **1 passed in 320 s**
(`runs/20261022T131325Z-s006-paidly`), into `/Users/athulrajeev/Documents/projects/keel-web/public/sample/`. S-006's
own marks green in the same run: guide v3 5 met, interviewer v7 29 met (IM12 unmeasured, DRIFT #86), contacts v2 13
met, report v1 5 met, feedback v1 5 met; verdict passed. The export: 37 files and `manifest.json`, **188,126 bytes**;
names kept **20 of 20**, survivors `{}`. Manifest: entry `05-paidly`, corpus 12, exportedAt `2026-10-22T13:15:43Z`,
cloud `bdda57637f9e4bfb19da7516e47294e2ddc7a243`. Card as exported: decision **BUILD_BUT_CHANGE** (MEDIUM, smallest
group 8), pilot **2 of 20, 10%**, price **$50 a month** (5 of 8). `grep -c "Nadia Petrova" public/sample/people.json`
**1**; `grep -c "Person 1\"" public/sample/people.json` **0**; no `Person <n>`, `@`, or founder word in any file.

**For the operator**: keel-web `public/sample/` is left as the export wrote it, uncommitted: 7 modified, 30 deleted
(060's batch and invitation ids) and 30 untracked (this run's) -- commit it with keel-web spec 092.

## Follow-up (operator, 2026-10-22)

- The DRIFT above closed on master: `tests/test_guide_teaching_marks.py` now admits keel-web 090's two landing clips (`landing-intro`, `sample-question`), which no mark reads. `make unit` back to 0 failed.
