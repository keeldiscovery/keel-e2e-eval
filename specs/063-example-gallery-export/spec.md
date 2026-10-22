# Spec 063 -- The example gallery export: six back-test briefs, renamed, into the sample snapshot

The founder, 2026-10-22: *"when you click on example, I want all these use cases to be like four boxes with this use case
name. And when they click on it, they see this brief … Now we cannot use the same company name, but we can exactly use
the same problem statement, just name the company to something else."* Today `make sample` (specs 060/061) exports ONE
run (S-006, 05-paidly) into keel-web's `public/sample/`. This spec exports the six back-test ideas' briefs, from
`make backtest` runs on the fixed chain, each renamed, into `public/sample/<slug>/` with an index. keel-web spec 100
draws the gallery. **Scope: keel-e2e-eval only (`evals/sample_export.py`, a rename map, the Makefile); nothing in
keel-cloud or keel-web changes here; no mark moves; MARKS_VERSION stays. Build lean: `make unit` once, one `make
gallery` run on existing back-test run directories (no paid run in this spec).**

## Rules

- **FR-1 `make gallery RUNS=<dir>[,<dir>…]`.** Takes one or more back-test run directories (the newest `runs/*backtest-<id>`
  for each of the six ids when `RUNS` is omitted) and writes, for each, the 060 file set into
  `<keel_web>/public/sample/<slug>/` (names kept as 061, tokens and emails withheld as 060), plus one
  `public/sample/index.json`: `[{slug, name, oneLine, problem, decision, howSure, pilot, price, b2b, entry, run, cloud, axes}]`
  (`problem` the renamed problem statement in one sentence; `axes` the seven gallery words -- who has it, who pays, rhythm,
  cost mode, price shape, first step, kind -- read from the entry and the run, in plain words, for keel-web 101's matcher) in the
  gallery's order (B2B and B2C alternating, the founder's call later). The single-run `make sample` and `public/sample/*.json`
  at the root stay as they are until keel-web 100 switches the home page over, after which the root files are removed by
  the operator.
- **FR-2 The rename map.** `instructions/gallery_names.toml` maps each entry id to `{slug, name, replaces: [..]}`:
  `08-fresco → daylog "Daylog" replaces ["Fresco"]`, `09-karsa → dollarsafe "Dollarsafe" ["Karsa"]`, `10-palus → idlewell
  "Idlewell" ["Palus Finance", "Palus"]`, `11-issen → talkleap "Talkleap" ["Issen"]`, `12-transload → dockmeasure
  "Dockmeasure" ["Transload"]`, `13-aircaps → captionglass "Captionglass" ["AirCaps"]` (the founder may overrule any name;
  the file is the one place). The export replaces every whole-word occurrence of a `replaces` string in every exported
  text field (project name, idea name, statements, the reveal, questions, insights, people's follow-up words) with
  `name`, case-preserved for the first letter, and nothing else: problem statements, solutions, people and answers stay
  word for word. A survivors grep refuses the export if any `replaces` string remains.
- **FR-3 Provenance, kept out of the public files (amended 2026-10-22: the founder's rule is that the real company
  names never appear; `public/sample/` is served to everyone).** `<slug>/manifest.json` and `index.json` carry only the
  keel-cloud and keel-web SHAs of the run and `exportedAt` -- no entry id, no run directory name, no `renamed.from`, no
  source path. The link from slug to entry and run is written once, outside `OUT`, to `<keel_e2e_eval>/runs/gallery/
  provenance-<exportedAt>.json` (`[{slug, entry, run, cloud, web, renamed: {from, to}}]`), ignored by git as every run
  file is. The survivors grep then covers EVERY byte under `OUT` with no exclusions, case-insensitive, and refuses on
  one hit.
- **FR-3a The interview, playable (founder, 2026-10-22: "create the actual interview question so that founders can play
  with it … this is what I am going to get if I buy this product").** Each `<slug>/` also carries `interview.json`:
  for every link of the run (the primary, the decider's on B2B), the served interview exactly as the stranger's page
  received it -- `kind`, `occasion`, `idea`, `gate` (question, the chips, `condition` when served), `parts[]` with each
  item's `dimension`, `kicker`, `question`, `control`, `options[]` labels, `escape`, `valueBox` / `plan` / `whatYouGet`
  where served, `storyPrompt`, the reveal and the follow-up stems that run's people were asked -- renamed by the same
  map, tokens and ids withheld, in one stable shape keel-web 100 renders without a server. Text only: no interviewer clips, faces or recordings are
  exported (the AI-interviewer version of an example is a later spec on the founder's word). The index gains
  `interview: {links: [{role, items}]}` counts per slug.
- **FR-4 Tests.** Unit tests: the rename over a fixture with the six names in mixed positions (a survivor refuses);
  the index shape; the file set per slug (interview.json included, its shape pinned on one run); nothing about the golden S-006 export moves (060/061's tests unchanged).

## Acceptance

1. `make unit` green with the new tests.
2. `make gallery` over the six newest back-test run directories on this machine writes six slugs and `index.json`; hand
   back the index, the survivors grep (0 hits for the six old names), and `ls public/sample/<slug>` for one slug. **Do
   not commit anything in keel-web** (the operator commits the snapshot with keel-web 100, from runs on the fixed chain).
3. No mark or version moved.
