# Tasks 060

Built against keel-cloud-docs master `dcfffab` (spec 112 + landing design §18.11) and keel-web master `6f89a95` (090 /
091 specs), corpus revision 12, `MARKS_VERSION` 20.

- [x] T001 FR-1 `evals/sample_export.py`: `capture` takes the seven reads (`overview`, `plan`, `standings`, `roles`,
  `people`, `readings`, `invitations`), one `readings/<batchId>` for every batch `readings` lists and one
  `invitations/<id>` for every row the register lists, through the founder session's own `Journey.get`, keyed by the
  path under `/v2/projects/{id}/` with the id removed. The reads as received go into the run bundle only
  (`sample-reads.json`, gitignored).
- [x] T002 FR-2 `withhold`: every person's name (people.json's order first, then anyone else in file order, then the
  entry's own people) becomes *Person k*, whole words only, longest name first; every `email` key goes, and so does
  any address left in a text; a string that is the founder's name or email is dropped and either one inside a text is
  cut out; `url` / `link` / `href` carrying a `/i/<token>` link, any `token` key, and every token the journey made read
  `withheld`. `survivors` is the grep over the whole output. The export refuses if anything survives.
- [x] T003 FR-3 `gate` (below, judgement call 1): the decision label `BUILD_BUT_CHANGE`; PROBLEM / SOLUTION / COMMERCIAL
  equal to `expected.vector_verdicts`; every asked dimension's n at least the entry's own `expected.standings` n, and
  every dimension the entry expects asked; the pilot count (`optedIn` / `finished`) and the price line
  (`priceMedian.edgeSaid`) present. A refusal writes nothing and names every reason.
- [x] T004 FR-4 `write` + `manifest.json` `{entry, corpus, exportedAt, cloud, files}` (`cloud` the keel-cloud checkout's
  `git rev-parse HEAD`; `files` in the order written). Files a previous manifest listed are removed first, so a re-run
  leaves no batch of the last run behind; the directory and anything the manifest did not list stay. `make sample`
  runs `-k s006` with `KEEL_SAMPLE_EXPORT` defaulting to `<keel_web>/public/sample` as `stack.toml` resolves it
  (`../../keel-web/public/sample` from a worktree, `../keel-web/public/sample` from the main checkout).
- [x] T005 S-006's one seam (`evals/test_s006_paidly.py`): `sample_export.pending(run_dir)` is `None` unless the
  variable is set; `_paidly_extras` takes the export before the contacts leg; `test_s006_paidly` settles it after
  `corpus_scenario.run` returns.
- [x] T006 FR-5: no mark, step or version moved; with the variable unset S-006 records no step of the export.
  `MARKS_VERSION` stays 20. AGENTS.md's paragraph.
- [x] T007 Acceptance 1: `tests/test_sample_export.py` (24) over `tests/fixtures/sample/s006-reads.json`, the reads this
  spec's stack run recorded (one link and one address seeded by the test, since these routes carry neither today).
- [x] T008 Acceptance 2 (below).

## Judgement calls

1. **FR-3's *n ≥ 10 everywhere* cannot hold on 05-paidly, so the gate holds every dimension to the entry's own n.**
   The entry's `expected.standings` are 12 (Prevalence), 9 (the other three problem dimensions and all three solution
   ones) and 8 (all six commercial ones, the eight decision-makers); measured on the wire the same, so twelve of
   thirteen dimensions are under ten and the decision reads *Smallest group: 8 decision-makers* (`howSure` MEDIUM).
   FR-3's own last sentence says the expected values are 05-paidly's own, and with ten the export could never pass for
   the one entry the spec names. So each asked dimension must carry at least the corpus's n (no fewer people than the
   corpus says), the verdicts must be the corpus's, and the spec's ten is kept as `SPEC_MIN_N`, measured and reported by
   name in the gate's step and in `sample.json` (`under 10`), never gating. The founder's to overrule in one line: gating
   at ten means the entry needs at least ten decision-makers and ten translators past the gate, a corpus change.
2. **The card's three figures are on `standings.json`, not `overview.json`.** keel-cloud's `GET overview`
   (`FounderDtos.Overview`) carries revision, name, state, market, guide and counts, and no decision, pilot or price. The
   report's Overview view reads `GET standings`: `facts.decision.label`, `pilot` (`optedIn`, `finished`, `percent`) and
   `priceMedian` (`edgeSaid`, `chose`, `n`). The gate reads them there; keel-web's landing card (091) must read
   `standings.json` for them. No file was added to carry them elsewhere.
3. **The export is taken at the twenty answers, before the contacts leg, and settled after the journey.** §18.11
   names *two roles, twenty answers*, and the corpus's verdicts and counts are the twenty-person project's. The contacts
   leg and the interviewer leg after it add three answered links (one found decision-maker, two AI-interviewer links),
   a found person's email and the stand-in Keel's-door ledger, so the snapshot taken at the very end would be neither
   the corpus's nor twenty. A refusal is held and fails the test only after `corpus_scenario.run` returns, so S-006's
   own marks are all measured in the same run whatever the export says (FR-5) and `make sample` still exits 1.
4. **Withheld means removed for an email and the founder, `withheld` for a token or link.** FR-2's words: an `email`
   key is dropped rather than blanked, so `"email"` never appears in the output.
5. **The worktree stack's ports.** `stack.toml` here names the eval profile's 18080 / 5173 / 18090; for the one run its
   three `[ports]` lines were pointed at 18082 / 5183 / 18092 (`COMPOSE_PROJECT_NAME=keel-e2e-eval-060`, postgres 55432)
   and put back byte for byte after `make down`, as spec 059 did. It is skip-worktree and nothing of it is committed.

## Measured (2026-10-21)

**Stack** (keel-cloud-docs `dcfffab`, keel-web `6f89a95` under vite, chromium):
`make sample KEEL_SAMPLE_EXPORT=<scratchpad>/sample-snapshot` **1 passed in 326 s** on the first run
(`runs/20261021T114556Z-s006-paidly`). S-006's own marks green in the same run: guide v3 5 of 5, interviewer v7 29 of
29 (IM12 unmeasured, DRIFT #86), contacts 13 of 13, report 5 of 5, feedback 5 of 5; the corpus hashed unchanged.
The export: 37 files and `manifest.json`, **187,624 bytes** -- the seven reads, 10 reading batches, 20 invitations;
20 people withheld, the 2 `email` keys (both null on these links) removed, no token on any of these routes, nothing surviving the grep (first and last
names checked apart too, none). Card as exported: decision **BUILD_BUT_CHANGE** (MEDIUM, smallest group 8), pilot
**2 of 20, 10%** (2 of 12 people who have it, 0 of 8 decision-makers), price **$50 a month** (5 of 8). Manifest:
entry `05-paidly`, corpus 12, cloud `dcfffab863b2f042ae3c6a4bd5c091227043d726`.

**`make unit`**: **2,964 passed / 53 skipped** (master's tracked suite on the same checkouts 2,940 / 53, two more than
059 measured against older siblings; +24 in `tests/test_sample_export.py`).

**For the operator**: the snapshot to commit lands in keel-web `public/sample/` (`make sample` from this repository's
main checkout); this run wrote it to the session scratchpad and nothing into keel-web.
