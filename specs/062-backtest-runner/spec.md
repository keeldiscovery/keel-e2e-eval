# Spec 062 -- The back-test runner: a real founder's idea walked on Keel's AI, recorded, never held to a corpus

The founder, 2026-10-22: *"find 5 to 6 projects which got initial funding … emulate the founder, how they've entered the
data. See the quality of the questions that generates for the founder. See the quality of the questions that comes to the
person being interviewed … See if there is any gap … Also, the insights, are our insights classification good?"* and
*"run against my local Anthropic one, but still uses the same models that we would use … I still want to capture the
UI."* Six YC companies were shortlisted (scratchpad `backtest/shortlist.md`): Fresco, Palus Finance, Transload (B2B),
Karsa, Issen, AirCaps (B2C). Each becomes a **back-test entry**: a corpus-shaped file with no golden expectations,
written from public material. This spec is the runner. **Scope: keel-e2e-eval only; nothing in keel-cloud or keel-web
changes; no mark moves; MARKS_VERSION stays.** Builds on S-006/S-005 (`evals/corpus_scenario.py`, `strict=False` as
S-012 uses it), 060/061 (`evals/sample_export.py`), `instructions/corpus.py` (the loader), `stack/` (the local eval
profile, which passes the caller's environment to keel-cloud). **Build lean: `make unit` once, one real run.**

## Rules

- **FR-1 Back-test entries.** A directory beside the golden corpus, `<keel_cloud>/canon/designs/measured-beliefs/backtest/`,
  holds `NN-slug.yaml` files in the corpus schema (revision 12) with these differences, and only these:
  `expected` is absent (or empty); a top-level `idea_name: <string>` carries what `IDEA_NAMES` carries for a golden
  entry; a top-level `sources: <path>` may name the sibling `NN-slug.sources.md` (ignored by the loader). The loader
  gains `load(keel_cloud, *, directory=None, backtest=False)`: with `backtest=True` it reads that directory, accepts the
  two keys, treats a missing `expected` as `{}`, and still refuses every shape error it refuses today (registry keys,
  controls, escapes, market/currency, the gate rules), so an author gets the same sentences a golden author gets.
  `vs.entry_for(keel_cloud, entry_id, backtest=True)` resolves an id from that directory, and `vs.IDEA_NAMES` lookups
  fall back to the entry's `idea_name`. A back-test entry is never read by `make eval`, `make unit`'s corpus tests, the
  matrix or the checker; one new unit test loads every file in the directory in back-test mode and fails on a refusal
  (so a broken entry is caught before a paid run).
- **FR-2 The founder on Keel's AI, locally.** `make backtest ENTRY=<id>` runs on the local eval profile (`make up` first
  as today, or the target brings the stack up and down itself -- builder's call, recorded). It refuses with one
  sentence unless `KEEL_ANTHROPIC_API_KEY` is set in the caller's shell (the stack passes the environment through;
  the key is never logged, echoed or written). The founder signs in as a stub identity whose email is
  **outside** keel-cloud's `fake-for` list (`keel-e2e-eval.test`), so every job runs on Keel's real AI with the
  routing file's own models: add one identity to the local stub (or register one at run time if the local stub
  can), email `backtest@keel-backtest.test`, name *Backtest Founder*. Everything else stays as the local stack has it:
  contacts fake, interviewer renders fake, transcriber fake, so nothing but model calls leaves the machine and no
  video is ever rendered.
- **FR-3 The walk.** The journey is `corpus_scenario.run` on the entry with `strict=False` (S-012's mode: the model's
  words are never held to the file; standings are recorded, not asserted; an answer that names an option the served
  list lacks lands on the served list as `_on_the_offered_options` does today). Which legs run follows the entry's
  shape as it does for S-005/6/7 (one link, or two on a `decision_maker.role`). The twenty (or however many) people
  answer from the file on the text link. At the last answer the 060/061 export runs into `runs/<run>/export/`
  with names kept and **no verdict gate** (060 FR-3 is golden-only; here the verdict is the finding). The harness's
  per-step screenshots are kept as today; in addition one full-page screenshot is taken of **every founder screen
  as it is about to be answered** (name, market, the four context fields, every calibration screen, the persona
  screen, every interpret/review screen, the send screen) and of **every served respondent screen** on one person
  per link, named `founder-NN-<slug>.png` / `respondent-<link>-NN-<slug>.png`, so the founder can look at what a
  founder would have seen.
- **FR-4 The transcript.** At the end the runner writes `runs/<run>/backtest.md` and `backtest.json` from the
  recorder's captures and the wire:
  1. **Founder screens, in order**: kicker, question, hint, the options as rendered (every label), the founder's
     answer from the file, what Keel read back (the *Keel understands* card, the belief sentence, the frame), and the
     screenshot's file name.
  2. **Respondent questions, per link**: every served item in order -- wording as served, control, every option
     label, the escape -- taken from the interview the respondent page fetched, plus the screenshot names.
  3. **The brief**: the decision and its label, every card's words, the insights with each one's cited evidence
     (the respondent's own words under each insight), the pilot count and price line, as served.
  4. **Readings**: per person, the model's anchoring judgement beside the file's own (`anchoring:`), as a measurement.
  5. **Cost and time**: every job's `execution.actual_cost_micro_usd` summed (and by class), model names as
     `model_used`, wall time per leg.
  The `.md` is for reading, the `.json` for a judge. Nothing in either is asserted.
- **FR-5 Nothing else moves.** `make eval`, `make unit`, the matrix, the marks and the versions are unchanged;
  `matrix/cells.py` never names the back-test (it spends money). `make backtest` is documented in the Makefile header
  and in AGENTS.md's live-cells paragraph as the fourth paid command, with its cost from the real run.

## Acceptance

1. `make unit` green, including the new back-test-directory test (which passes trivially when the directory is empty
   and refuses a broken entry; include a fixture of a broken one under `tests/fixtures/backtest/`).
2. One real run: if `backtest/` already holds an authored entry when you reach this step, run that; otherwise copy
   `05-paidly.yaml` to `backtest/00-smoke-paidly.yaml` with `expected` removed and `idea_name: Invoice payout service`
   added, run `make backtest ENTRY=00-smoke-paidly`, and delete the smoke file afterwards (leave the directory, with a
   `README.md` of five lines saying what it is). Hand back: the run directory, the counts of founder and respondent
   screenshots, the first twenty lines of `backtest.md`, the summed cost and the models used, wall time, and the
   export's decision label.
3. No mark or version moved.
