# 034 — The brief infers and recommends (marks v14)

Sibling of keel-cloud 079 (`079-brief-infer-recommend`, merged at `706015c`; inference
`CONTRACT_VERSION` 8 → 9, project `SCHEMA_VERSION` 15 → 16). Lean: DRY only, no live model call, no
push or merge, no run of record.

## What moved in keel-cloud
- `brief.md` rewritten (14,894 bytes; byte-identical to the canon draft). This repo keeps no copy of an
  instruction: the exporter and `build_prompt` read it from the sibling, so the "mirror" is the checkout.
- BRIEF context: `project_name, market, context, facts, beliefs, stories`.
- BRIEF result: `{headline, tiles:{problem,solution,commercial}, problem:{conclusion,infer},
  solution:{conclusion}, commercial:{conclusion}, sharpest?, next:{sentence, tests:[{key,text}] <= 3},
  quotes:[{invitationId,text <= 160}] <= 2}`; every sentence `{text <= 400, cites[] <= 13}`.
- Upcaster 15 → 16 drops `whatThisSays`, adds `briefReading: null`. Corpus revision stays r7.
- Checks (`BriefReading.check`, refusal `B7`, run by `screenContracts validate` on a BRIEF case
  `{facts, stories, result}`).

## Requirements
- FR-001 `MARKS_VERSION` 13 → 14; judgement calls 71–73; `rescore.py` refuses every bundle below 14.
- FR-002 The BRIEF case's context is `project_name, market, context, facts, beliefs, stories`, `facts`
  built from the corpus's standings in keel-cloud's shape (`instructions/brief_facts.py`).
- FR-003 `validate.build_batch` sends a BRIEF case as `{facts, stories, result}`.
- FR-004 Five reading marks replace the four paragraph marks (`shape`, `cites`, `numbers`, `quotes`,
  `bans`), each a clause-for-clause restatement of `BriefReading.check`, proved equal to the real
  validator by `tests/test_instruction_brief_reading.py`. Participant names are checked here only.
- FR-005 Fixtures for the three brief scenarios (BUILD, NOT_YET, BUILD_BUT_CHANGE B2B) from the golden
  shape under `tests/fixtures/brief/`.
- FR-006 `make unit` green, nothing skipped by this spec; `DRY=1` compare 108 of 108.

## Out of scope
- No v14 run of record (`WHY=marks:14`).
- The scripted journey (`harness/corpus_script.py` BRIEF answer and the live `evals/` that read
  `Project.whatThisSays` on the wire) is a live-stack mirror of keel-cloud 079's wire, not a mark; it
  needs a stack to prove and is left for a spec that can run one.
