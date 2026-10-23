# Tasks 063

Built on keel-e2e-eval master `83cd548`, against keel-cloud-docs `9bfa977` and keel-web `8841524` (the sibling
checkouts when the build ran; neither was written to), `MARKS_VERSION` 20 (unchanged). No stack, no model, no paid run.

**The back-test entries were not loaded through `instructions.corpus.load`.** They are corpus revision 13 in
keel-cloud-docs (`canon/designs/measured-beliefs/backtest/`), and this eval's loader reads revision 12 until spec 064
is built. Everything the export needs is read from the run directory instead: the idea name, `b2b` and the entry id
from `backtest.json`'s `entry`; the project name, the problem statement, the four context fields, the window, the
decider and the calibration answers from `inputs.json`'s `founder` (what the run's founder typed, from the entry as it
was at run time).

## Amendment of record, 2026-10-23 (built on branch `063-attribution`, over master `d9e50bf`)

The real company name is the example's attribution, everywhere; each example is labelled a simulated study. This
section overrides FR-2's rename and FR-3's survivors grep below wherever they conflict.

- [x] A001 `instructions/gallery_names.toml`: `slug` and `name` are the real ones -- `fresco` Fresco, `karsa` Karsa,
  `palus-finance` Palus Finance, `issen` Issen, `transload` Transload, `aircaps` AirCaps -- with `replaces = []`
  (anything else is refused by name), plus `inspired_by = {name, batch, ycUrl}` and `public_description = {text, url,
  date}` per entry. Slugs may now carry hyphens.
- [x] A002 The rename is gone (`Renamer` removed): every exported file is the run's export, withheld again, unchanged
  (a test checks byte-equal JSON). The interview.json golden is the old one with *Daylog* back to *Fresco*, nothing else
  (checked when it was regenerated, now `tests/fixtures/gallery/expected-interview-fresco.json`).
- [x] A003 Every index row and `<slug>/manifest.json` carry `inspiredBy {name, batch, ycUrl}`, `publicDescription
  {text, url, date}`, `simulated: true`, `disclaimer` (the amendment's fixed sentence, `name` and `batch` filled) and
  `assumptions[]`. The index row's order is `slug, name, inspiredBy, publicDescription, simulated, disclaimer, oneLine,
  problem, assumptions, decision, howSure, pilot, price, b2b, cloud, web, axes, interview`; the manifest is `cloud,
  web, exportedAt, inspiredBy, publicDescription, simulated, disclaimer, assumptions`.
- [x] A004 The attribution check (`attribution_reasons`, replacing the survivors grep) refuses a slug, writing nothing,
  when any of these holds: `inspiredBy` lacks name, batch or ycUrl; ycUrl is not a `https://www.ycombinator.com/companies/` page;
  the name differs from the example's; `publicDescription` lacks text, url or date, the url is not https, or the date is
  not ISO; `simulated` is not true; the disclaimer is missing or not the fixed sentence; there are no assumptions; the
  index row and the manifest disagree; or the run did not invite exactly twenty people (the disclaimer says "the
  twenty participants"). 060's grep (emails, the back-test founder, links) and the interview's no-id check stay.
- [x] A005 Provenance stays private, as built on 2026-10-22: `runs/gallery/provenance-<exportedAt>.json`
  (`renamed: {from: [], to: <name>}` now). In place of the old-name grep, every byte under `OUT` is grepped, any case,
  for each run's entry id and directory name, `-backtest-` and `/Users/`. This runs before writing (over the new output
  and anything already under OUT) and once more after writing.
- [x] A006 Tests: `tests/test_gallery.py` is now 30 tests (the rename and survivors tests replaced by the attribution
  tests: the map, the fixed sentence, the attribution in the index and the manifest, five missing or bad attribution
  cases, missing disclaimer / simulated / assumptions, the twenty people, nothing renamed, the index and manifest shapes,
  no provenance under OUT). Run with the two suites that scan every `evals/*.py`: **104 passed** (30 + 34 + 40). The
  whole `make unit` was not re-run.
- [x] A007 `make gallery` with `RUNS_DIR=` the main checkout's `runs/` into the scratchpad's
  `gallery-snapshot-v2/public/sample`: six slugs (fresco, karsa, palus-finance, issen, transload, aircaps, B2B / B2C
  alternating) and `index.json`. No entry id, run name, `backtest` or `/Users/` in any file. Provenance went to
  `runs/gallery/provenance-2026-10-23T00:11:51Z.json` in this worktree.

### The amendment's judgement calls

1. *(Superseded by 1d42c51, see B001-B005: this is now `statusToday`.)* **`publicDescription.text` was the `one_liner` field of the YC company page, verbatim, from the saved copies of
   2026-10-22** (`scratchpad/backtest/yc/<slug>.html`, saved 09:14 local; date 2026-10-22). The `.sources.md` files record
   each YC company page URL (used for `ycUrl` and `publicDescription.url`) but not its one-liner:
   - 08-fresco's sources file quotes the page's long description ("AI-powered takeoff and estimating for Division 8
     construction").
   - 09-karsa's quotes a paraphrase ("a stablecoin neobank").
   - The other four quote nothing from the company page.

   So the saved page was the source for all six; nothing was fetched.
2. *(Resolved by 1d42c51: `publicDescription` is the launch-era title, today's words are `statusToday`.)* **Three one-liners describe a later product than the one the back-test studied**, because the companies have
   moved on:
   - Fresco: "AI copilot for construction estimators", where the study is the superintendents' scribe.
   - Karsa: "Stablecoin neobank for emerging markets", where the study is the dollar account.
   - Palus Finance: "Your startup's financial advisor", where the study is yield on idle cash.

   Issen ("AI realtime voice companion for language learning"), Transload ("Measure freight with security cameras") and
   AirCaps ("The AI copilot for in-person conversations.") match. Verbatim was the rule, so they are as served; the
   founder may want the launch post's title instead (the sources' `[LYC]` / `YCL` lines, e.g. *Fresco, the scribe for
   construction*).
3. **Names as the coordinator gave them, not as YC spells them**: YC's page writes *ISSEN* and *transload*; the map
   writes Issen and Transload (the disclaimer and `inspiredBy.name` use the map's).
4. **Batches** are as the coordinator listed, and equal the pages' `batch_name` for all six.
5. **`assumptions[]` are the standings' `belief` sentences**, one per asked dimension, stage by stage, de-duplicated:
   13 on B2B, 12 on B2C. They equal plan.json's. Plain strings, as served, including code's derived Ability to pay
   line ("Your price is 24% to 61% of what the problem costs them today: …").
6. **The disclaimer's "twenty participants" is checked against the run** (each run invited twenty) rather than
   trusted.

## Amendments 1d42c51 and a35af52, 2026-10-23 (same branch, cherry-picked)

**1d42c51: launch-era `publicDescription`, plus `statusToday`.** This resolves the amendment's call 2 below (three
one-liners describe a later product). The founder's gap-11 rule is that every example is pinned to the idea as it was
launched.
- [x] B001 `public_description` in the map is now the company's own words for the studied idea: the **Launch YC post's
  title**, verbatim, with the post's URL (the `sources` file's Launch YC line) and the post's date (`created_at`, UTC).
- [x] B002 The sources files only paraphrase those titles. Fresco's reads "Launch YC: Fresco, the scribe for
  construction" against the real "Fresco: The scribe for construction"; Karsa's reads "Karsa, the global dollar
  account" against "Karsa 💸 - The Global Dollar Account"; the other four give only the URL. So each title was read from
  the saved YC company pages of 2026-10-22, whose data carries every launch post's title, tagline, URL and date. For
  Fresco, Transload and AirCaps the saved launch pages under `scratchpad/backtest/launch/` agree word for word. Nothing
  was fetched.
- [x] B003 `status_today` is the current YC one-liner (company page, 2026-10-22), written only where it differs from the
  launch-era words. AirCaps' launch title is "AirCaps - The AI copilot for in-person conversations." and today's
  one-liner is "The AI copilot for in-person conversations.", the same words, so AirCaps has none. Transload's differ
  only as "we measure" against "Measure" and are kept, since the strings are not identical.
- [x] B004 `statusToday` is optional in the attribution check; where present it has `publicDescription`'s shape rules
  (text, an https URL, an ISO date). Index row and manifest order: `…, publicDescription, statusToday, simulated, …`.
- [x] B005 Spellings: the map's names stay Issen and Transload. The launch-era text is verbatim, so it says "ISSEN - …"
  and "transload – …".

**a35af52: `cluster`, `keywords` and the index envelope.**
- [x] B006 Each index row carries `cluster {id, label}`, taken from the map's `cluster`.
  - The source is the diversity research's topic clusters: `scratchpad/backtest/diversity/clusters_k30.json`, K 30,
    seed 11, with the labels as `diversity-page.html` names each cluster `k`.
  - The ids differ from the coordinator's list, so they were read from the file: Fresco 4 *Construction and real
    estate*, Karsa 27 *Payments, banking, lending, stablecoins*, Palus Finance 27 (same), Issen 29 *Education and
    tutoring*, Transload 16 *Supply chain, logistics, freight*, AirCaps 6 *Consumer video, media and creators*.
  - The file's own k-means assignment puts `palus-finance` in 21 (*Trading, markets and financial analytics*) and
    `aircaps` in 13 (*Personal and work assistants*). The map follows the coordinator's labels; the founder may move
    either.
- [x] B007 `keywords[]`, 5 to 12 lower-case words or short phrases.
  - `evals/gallery.keywords` derives them: the actor, the occasion, then the content words of the one-sentence problem
    statement and the four context fields, the most repeated first, with stop words, verbs and the company's own name
    left out.
  - The map's `keywords` list overrides the derivation, and is written for all six. The derived lists still carried
    verbs and other companies' names (Procore, OneDrive), so the six lists were picked by hand from the same words.
    Every phrase occurs verbatim in that run's problem statement, context fields or occasion (checked), and none is a
    company name.
- [x] B008 `index.json` is now `{generatedAt, count, examples: [...]}`, with `generatedAt` the export's `exportedAt`.
  The rows sit in `examples`, in the gallery's order. keel-web 100 reads `examples`.
- [x] B009 The attribution check also requires `cluster` (an integer id and a label) and 5 to 12 keywords, each lower
  case, non-empty and not naming the company. Index row order: `…, axes, cluster, keywords, interview`.
- [x] B010 Tests: `tests/test_gallery.py` is now 40 tests (added: the clusters, the keyword derivation and the map's
  lists, five cluster or keyword refusals, `statusToday` optional, two `statusToday` shape refusals, and the envelope
  and launch-era expectations). Run with the two suites that scan every `evals/*.py`: **114 passed** (40 + 34 + 40).
- [x] B011 `make gallery` was re-run into `scratchpad/gallery-snapshot-v2/public/sample`, with the directory replaced
  whole: six slugs plus `index.json`, and 0 files carrying an entry id, run name, `backtest` or `/Users/`. Provenance:
  `runs/gallery/provenance-2026-10-23T00:18:10Z.json`, also copied to the main checkout's `runs/gallery/` (git-ignored
  there).

## FR-1 `make gallery`

- [x] T001 `make gallery RUNS=<dir>[,<dir>...] OUT=<dir> RUNS_DIR=<dir>` (Makefile, header comment, `.PHONY`) runs
  `python -m evals.gallery`. `OUT` defaults to `<keel_web>/public/sample` (as `make sample` finds it); `RUNS` defaults
  to the newest finished `*-backtest-<entry>` directory under `RUNS_DIR` (default `runs/`) for each entry of the map.
  A bare name in `RUNS` is looked up under `RUNS_DIR`.
- [x] T002 `evals/gallery.py`: `read_run` (refuses a run with no `backtest.json`, `inputs.json` or
  `export/manifest.json`, one that did not pass, or a listed export file missing), `export` (reads every run, prepares
  every slug in memory, checks the whole output and whatever already sits under `OUT`, and only then writes -- a
  refusal writes nothing), `<OUT>/<slug>/` (the slug's directory replaced whole, then written by 060's own
  `sample_export.write`), `<OUT>/index.json`, a last grep of every byte under `OUT`, and the provenance file outside it.
- [x] T003 The index: `[{slug, name, oneLine, problem, decision, howSure, pilot, price, b2b, cloud, web, axes,
  interview}]` (no `entry` or `run` since the FR-3 amendment) in the gallery's order (`gallery_order`: B2B and B2C alternating, B2B first, each side in the map's
  order). `decision`, `howSure`, `pilot`, `price` are 060's `card()` over the renamed standings.
- [x] T004 The seven `axes`, all derived (judgement call 6).
- [x] T005 `make sample` and its root `public/sample/*.json` are unchanged; the gallery never touches a file at the root
  of `OUT` other than `index.json`.

## FR-2 The rename map

- [x] T006 `instructions/gallery_names.toml`: six `[[gallery]]` tables (`entry`, `slug`, `name`, `replaces`, optional
  `axes`), the spec's six names. `load_names` refuses a bad slug, an empty `replaces`, an unknown axis word or a
  repeated entry / slug / name, by name.
- [x] T007 `Renamer`: one pattern over every `replaces` string of every entry (longest first: `Palus Finance` before
  `Palus`), whole word (`(?<!\w)…(?!\w)`), any case, written as the entry's `name` with the matched first letter's
  case. Applied to every string value of every exported file (060 set, interview.json, the index's text); keys and
  non-strings are kept. On the six runs the only lines that change are the ones carrying a name (checked line by line
  during the build: 18-26 lines a slug, zero other differences).
- [x] T008 The survivors grep (`check`): the whole output read back, every slug against all six entries' strings, any
  case, whole word -- plus 060's grep (an email, the back-test founder's name or address, a link) and a check that
  interview.json carries no id key. Any hit refuses the export, nothing written.

## FR-3 Provenance

- [x] T009 (FR-3 as amended 2026-10-22, master `51b9f79`, cherry-picked) `<slug>/manifest.json` is `{cloud, web,
  exportedAt}` and nothing else (060's own manifest, which `write` puts there first, is overwritten); `cloud` and `web`
  are the run's `backtest.json` `stack` SHAs (seven characters, as the run recorded them), and the index repeats them.
  No entry id, run name, `renamed.from` or source path is written under `OUT`.
- [x] T009a The slug -> entry / run link is written once, outside `OUT`, to `runs/gallery/provenance-<exportedAt>.json`
  (`--provenance-dir` / `PROVENANCE_DIR=` override it; one under `OUT` is refused): `[{slug, entry, run, cloud, web,
  renamed: {from, to}}]` in the gallery's order. `runs/` is git-ignored.
- [x] T009b The survivors grep covers every byte under `OUT`, any case, no file or field excluded: once over what is
  about to be written (`check`) and over what is already there (`survivors_under`, skipping only the slug directories
  and `index.json` the export replaces), refusing before anything is written; and once more over the whole of `OUT`
  after writing.

## FR-3a interview.json

- [x] T010 `interview(run)`: one entry per link the run served (`PRIMARY` first, `COMMERCIAL_B2B` after it on B2B),
  built from `backtest.json` `respondents[link].served` (the interview the respondent page fetched), with what only the
  page drew filled from `respondents[link].drawn` (the item kickers, the gate's chip labels, the rows drawn), and the
  follow-up stems from `transcript.jsonl` (every `<person>: the one follow-up -- …` step whose route answered 200 with
  a filled `text`, grouped by the step's `link`, de-duplicated, in order). Renamed; ids, tokens and the AI
  interviewer's spoken forms dropped (`_DROPPED`); no clip, face or recording is read or written.
- [x] T011 `evals/backtest.served_items` keeps, from now on, an item's own `kicker`, `advantagesPrompt`, `scale`,
  `numeric`, `costTotal`, `valueBox`, `whatYouGet` and `plan` (its options as labels) when served (judgement call 3).
- [x] T012 The index's `interview: {links: [{role, label, items}]}` (`items` = the gate plus every part's items, which
  equals the role's `questionCount` in `roles.json`; the follow-up is not counted).

### The shape (for keel-web 100)

```jsonc
// <slug>/interview.json
{
  "links": [
    {
      "role": "PRIMARY" | "COMMERCIAL_B2B",       // the link; the decision-makers' only on B2B
      "label": "Construction superintendents",     // the role's label (plan.json respondentTypes)
      "kind": "FULL" | "COMMERCIAL_LINK",
      "occasion": "day",                           // the noun the story chip completes
      "idea": null | {"what", "how", "belief", "kicker"},          // the decision-maker's link opens with it
      "gate": null | {
        "kicker": "Part 1 of 2 · A recent time · 1 of 4 · the anchor",
        "question": "In the last 5 working days, did you …?",
        "chips": [{"code": "CANT_RECALL", "label": "I can't recall one particular day"}],
        "exitText": "Thanks for telling us. …",
        "condition": { … }                         // only when the wire serves one (none of the six runs does)
      },
      "storyPrompt": null | "Think of the most recent time …",
      "storyHint": null | "When it was, what you did first, how it ended.",
      "parts": [
        {
          "part": 1,
          "title": "…",                            // only when served (none of the six runs carries it)
          "items": [
            {
              "dimension": "problem.frequency",
              "kicker": "Part 1 of 2 · A recent time · 2 of 4",
              "question": "On how many of those 5 working days …?",
              "control": "segmented_0_to_7" | "pick_two" | "single_choice_5" | "single_choice" | "fixed_four"
                         | "fixed_three" | "benefit_with_advantages" | "cost_total" | "price_ladder" | "value_box" | …,
              "hint": null | "Pick one.",           // served, else the line the page drew
              "options": ["…"],                    // labels, in the order shown; [] where the control has none
              "advantages": ["…"],                 // benefit_with_advantages' founder benefits; [] elsewhere
              "escape": null | "I can't recall",   // the item's one way out; null on Commitment
              "shown": ["0", "1", "…"],            // the rows the page drew for the run's watched person
              // only where served:
              "advantagesPrompt": "…", "scale": {"min", "max", …}, "numeric": {…}, "costTotal": {…},
              "valueBox": {"measure", "label", "currency", "currencySymbol", "nothing": {"code", "label"},
                           "chips": [{"code", "label"}]},
              "plan": {"question": "…", "options": ["…"]},
              "whatYouGet": "a, b and c"
            }
          ]
        }
      ],
      "reveal": null | {"afterPart", "kicker", "what", "how", "belief", "bridge", "formats": [{"format", "available", "label"}]},
      "followUp": null | {
        "kicker": "One last thing",
        "note": "In your own words. A sentence or two is plenty.",
        "asked": [{"dimension": "problem.importance", "question": "You picked … What makes those more pressing?"}]
      }
    }
  ]
}
```

Every key above without "only when served" is always present. Text only: no `itemId`, `optionId`, `id`, `token`,
`costItemId`, `advantagesWhen`, `spoken`, `clip` or `clips` anywhere in the file (the test asserts it).

## FR-4 Tests

- [x] T013 `tests/test_gallery.py` (21, then 24 with the FR-3 amendment): the map is the spec's; a malformed map refused by name; the rename over a
  fixture with the six names in mixed positions (start, middle, end, possessive, lowercase, all caps, quoted, nested)
  and the longer-word non-matches kept; the survivors grep in any case; a survivor (a name in a JSON key, where the
  rename never reaches) refuses and writes nothing; 060's withholding still refuses; nothing but the names changes; the
  index shape (keys, order, values, axes, interview counts = `questionCount`); B2B / B2C alternation; the consumer axes
  and the map's override; `one_sentence` / `one_line`; the file set per slug (the run's export files + interview.json +
  manifest.json); the manifest's provenance; interview.json pinned on one run
  (`tests/fixtures/gallery/expected-interview-daylog.json`); no id, token or media in it; a re-run; the default runs;
  an unknown or twice-given entry; the command line; `served_items`' extras; the Makefile.
- [x] T014 The fixture `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/` (200 KB): the run of record for
  08-fresco cut to what the export reads (see the test module's docstring). `test_sample_export.py` (060/061) and its
  fixture are untouched.

## Judgement calls

1. **The run directory, not the corpus loader, is the source** (the brief: the entries are r13, the loader r12 until
   064). The idea name, b2b and id come from `backtest.json`'s `entry`; the problem statement, the context fields, the
   window, the decider and the calibration from `inputs.json`'s `founder`.
2. **The 060 file set is the run's own `export/`** (spec 062 FR-3 wrote it with names kept and emails, the founder and
   tokens withheld), read back file by file from its manifest, withheld again (a no-op on all six runs, verified) and
   renamed -- rather than re-withholding the raw `sample-reads.json`, which carries the tokens. The run's export
   manifest's `corpus` (12) is carried into the slug's manifest.
3. **interview.json comes from `backtest.json`'s `served` + `drawn` + the transcript's follow-up steps**; no run
   directory holds the raw `GET /v2/i/<token>` body. `served` (spec 062 FR-4.2) had dropped the item kicker and spec
   115's `valueBox` / `plan` / `whatYouGet`; the kicker is taken from `drawn` for these six runs, and
   `served_items` now keeps all of them for future runs. None of the six runs was served a value box, a plan or
   what-you-get (their controls are `cost_total` and `price_ladder`, keel-cloud before 115), so those keys are absent
   today and pass through when a later run carries them. The gate has no `condition` on the wire (contract 19's
   `GateItem`); it passes through if one appears. The `shown` rows (what the page drew) are the run's one watched
   person's, so a number control's range and the cost-total toggles can be drawn without a server.
4. **`problem` is one sentence of the founder's problem statement, word for word**: the words before the `; based on
   …` clause (the founder's own evidence -- on 12-transload it names a founder, *Jago*, which the gallery should not
   carry), to the first full stop. All six keep their own words; five were one sentence already, and 12-transload keeps the first of its two.
5. **`oneLine` is the project name's own tag line** (after its dash: *Fresco — the scribe for construction
   superintendents* → *The scribe for construction superintendents*), its first letter raised.
6. **All seven axes are derived; none is written in `gallery_names.toml`** (the map takes an optional `axes` table
   that wins, for the founder's later word). `whoHasIt` = the context's actor; `whoPays` = *themselves* when the
   decider is the same person, else the decider's role as the founder typed it (*contractor*, *founder*, *manager*);
   `rhythm` = the recall window's unit in a word (*every working day*, *daily*, *weekly*, *monthly*, *nightly*);
   `costMode` = Existing sacrifice's mode (*time* for hours, *money* for an amount); `priceShape` = the price's period
   (*monthly*, *yearly*; *one-off* when a price has no period); `firstStep` = Commitment's step; `kind` = *business* /
   *consumer*. They are renamed like every other text (none carries a name today).
7. **The index carries `web` beside `cloud`** (FR-3: "index.json repeats the SHAs" -- plural), and each link's
   `label` beside `role` and `items`.
8. **Resolved by the FR-3 amendment (the coordinator, 2026-10-22, master `51b9f79`): provenance never reaches the
   public files.** As first built, `index.json` and each `<slug>/manifest.json` carried the entry id, the run name and
   `renamed.from`, and the grep excluded exactly those fields -- so the served files named the real company behind each
   example. Now the manifest is `{cloud, web, exportedAt}`, the index has no `entry` / `run`, the link lives only in
   `runs/gallery/provenance-<exportedAt>.json`, and the grep has no exclusions. The manifest no longer carries 060's
   `files` list either ("only" the SHAs and the time); re-runs stay clean because each slug directory is replaced
   whole.
9. **The rename matches in any case**, the first letter's case kept (`FRESCO` would become `Daylog`). The cost is
   that a common-word use of a name (*transload* is also a freight verb) would be renamed too; none of the six runs'
   exports has a lower-case or all-caps occurrence, so nothing of the kind happened. Longer words (`Frescoes`,
   `Transloading`) are not touched and are not survivors.
10. **`renamed.from` (in the provenance file only) is the list of `replaces` strings** (`["Palus Finance", "Palus"]`), `to` the name.
11. **The default runs are the newest *finished* run per entry** (`passed` true and an export manifest), which on this
    machine are exactly the six the brief names. A run is refused, not skipped, when given explicitly and unfinished.
12. **New module `evals/gallery.py`** rather than growing `evals/sample_export.py` (whose docstring and seam are
    S-006's); it reuses 060's `withhold`, `survivors`, `card`, `write` and `_dumps` unchanged.
13. **`stack.toml`'s four `[paths]` lines read `../../…` under `git update-index --skip-worktree`** for `make unit` in
    the worktree, as 061/062 did, and were put back byte for byte (sha256 `f6986f68…`), the flag cleared. `make gallery`
    itself needed no config change: it ran with `OUT=` given.

## Not done / open

- Nothing was written into keel-web; the snapshot went to the scratchpad `OUT` the brief named. Committing it in
  keel-web is the operator's step, with keel-web 100.
- The provenance file is written in the checkout that runs `make gallery` (`runs/gallery/`); from this worktree it
  is in the worktree, and goes when the worktree is pruned unless copied.
- The AI-interviewer version of an example (clips, spoken forms) is a later spec, as FR-3a says.

## Measured (2026-10-22)

**`make gallery`** (first run, before the FR-3 amendment) over the six newest runs (`RUNS_DIR=` the main checkout's `runs/`), into the scratchpad: six slugs
(37-45 files each with interview.json; 2.0 MB in all) and `index.json`, in the order daylog (B2B), dollarsafe (B2C),
idlewell (B2B), talkleap (B2C), dockmeasure (B2B), captionglass (B2C). Survivors: 0 case-sensitive whole-word hits
outside the manifests; a case-insensitive substring grep of everything hits only the provenance fields of call 8.

**`make unit`** (`PY=` the main checkout's venv, from the worktree with call 13's paths): before, on master `83cd548` (the worktree itself, and again a clean `git archive` copy: same counts)
against keel-cloud-docs `9bfa977`: **2,832 passed / 39 failed / 169 skipped** (the 39 are pre-existing and none is
this spec's: `test_vectors_journey` 27, `test_follow_up_ladder` 6, `test_journey_through_a_host` 4,
`test_backtest::test_every_backtest_entry_loads_in_backtest_mode` 1, `test_report_marks` 1 -- keel-cloud-docs moved
to corpus r13 and its registry since 062's 2,986, which spec 064 is for; the main checkout's count was not
re-measured). **After: 2,855 passed / 39 failed / 169 skipped** -- +23: `tests/test_gallery.py`'s 21, and one case each
in `test_page_object_calls_exist` and `test_scenarios_use_the_stack_addresses`, which are parametrised over every
`evals/*.py` and now see `evals/gallery.py`. The 39 failures are the same 39, by name.

**FR-3 amendment (2026-10-22, after the above).** `tests/test_gallery.py` + the two suites that scan every `evals/*.py`
(`test_page_object_calls_exist`, `test_scenarios_use_the_stack_addresses`), not the whole `make unit`: **98 passed**
(24 + 34 + 40). New: the manifest is exactly `{cloud, web, exportedAt}`; the provenance file outside `OUT`; every byte
under `OUT` free of every old name (substring, any case) and of `08-fresco` / `backtest`; an old name already under
`OUT` refuses with nothing written; a provenance directory under `OUT` refuses. `make gallery` re-run into the same
scratchpad `OUT` (old slug directories and index deleted first): six slugs, `grep -rniE
"fresco|karsa|palus|issen|transload|aircaps"` over all of `OUT` = **0 lines**; provenance at
`runs/gallery/provenance-2026-10-22T23:05:37Z.json` in the worktree. No config change was needed for these runs.
