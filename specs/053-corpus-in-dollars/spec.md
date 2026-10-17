# Spec 053 -- The corpus in dollars, as the eval sees it

keel-cloud 105 (corpus **revision 12**: the six GB entries become US entries, same digits, `$` / `USD`, a few words
in the US register; the exports re-cut) and keel-web 078 (D20: the country drop-down offers the United States alone).
Design of record: keel-cloud-docs `canon/designs/report-and-follow-up-design-2026-10-17.md` §0 D19 / D20, §13a. The
founder, 2026-10-17: "the currency amount should be dollars, because we are primarily targeting US markets". Lands
**after 052** (line numbers are 052's head `ec8b4c6`; re-find them after the rebase) and merges **with 105**. 105's
invariant holds: no standing, count, median or verdict moves -- one that does is 105's defect; report it, never re-type.

## Rules

- **FR-1 Revision 12.** `instructions/corpus.py`: the docstring (`:1-7`) opens on **Revision 12 only** (keel-cloud
  105: r11's rules, the six GB entries in the US and in dollars, the founder's words; the shape half is
  `check_corpus_r12.py`'s less rule U, FR-4); `:62` `REVISION = 12`; `_REVISION_OF` (`:65-78`) gains `11:
  "MARKS_VERSION 19's and 20's corpus, in pounds (six GB entries, before keel-cloud 105: 'the currency amount should
  be dollars')"`; the refusal (`:549-553`) keeps its code, so it reads *revision is 11; this eval reads revision 12
  only -- revision 11 is MARKS_VERSION 19's and 20's corpus, in pounds (...)*; `:156` `cost_said`'s example *about
  $10 to $30 a month*. `money_text`, `cost_said`, `_SYMBOL`, `MARKET_CURRENCY`, `brief_facts.CURRENCY_SYMBOL`
  unchanged: they read the currency. Tests: `tests/v9_fixtures.py:33-34, 44` `CANON_NOT_R11` -> `CANON_NOT_R12`;
  `tests/test_instruction_corpus_r11.py:148` *reads revision 12 only*, and after `:163` a case `"revision 11"`;
  `tests/test_corpus_r11_shape.py` docstring `:1-15`, `:44-47` and `:416` revision 12, `:384` gains `(11,
  "MARKS_VERSION 19")`, and one new test, **every entry is a US entry in dollars** (105's
  `everyEntryIsAUsEntryInDollars` through `load`: seven `country: US`, `language: en-US`, region OR on 04 and TX on
  07, every `currency` node USD, no `£`, `GBP` or `en-GB` in any file's bytes). File names stay (history).
- **FR-2 The marks.** **`MARKS_VERSION` stays 20**: no mark, metric, field list or judgement call moves (the corpus's
  symbol and words do), and v20 has no run of record, so no r11 bundle waits to be re-scored. `instructions/marks.py`
  gains a **Spec 053** paragraph after 051's (`:42-44`): 105 moved no schema, instruction or golden number; v20 reads
  revision 12 and refuses 11 by name; the seven r12 files by sha256 (canon at the 105 merge, equal to
  `src/test/resources/keel/corpus-r12/`), as v19's paragraph lists r11's (`:60-64`). v20's *The corpus stays revision
  11* (`:36`) is history. **Numbered calls stay as written** -- each records a rule with the figure of its day, and
  the rule (symbol from the currency) is unchanged: call 42 `:485` *£165 per three months*, call 57 `:638, :640`,
  call 64 `:692-694`, call 65 `:700`, and their `instructions/marks.toml` comments `:261` (*£165 per three months*)
  and `:263` (*worth £5 a month or more*). Live prose moves: `instructions/brief_facts.py:209` *$50 a month*.
- **FR-3 The harness and the journeys.**
  - (a) `harness/vectors_script.py`: `COMPOSED` (`:98-112`), `IDEA_NAMES` (`:310`), `FOLLOW_UP_LINES` (`:1263-1296`)
    carry no `£`, digit or renamed phrase (checked; every short / offer name, Repeatline's new two included, is read
    from the corpus) -- unchanged. Market fallbacks `:1119-1120` and `harness/corpus_script.py:686-688` (comments
    `:120-122`) -> `"US"` / `"en-US"`: never reached, but a fallback must be a country 078 offers.
  - (b) `harness/browser.py` `MarketStep`: the region locator stays positional; the note (`:1775-1781`) says why now
    -- every entry is US and 078 offers only the US, so a label match would work today, but position does not hang
    on a placeholder's words. `described_sentence`'s example (`:1825-1827`) is the sentence `GET /v2/markets/US`
    serves (copied off the stack). `MARKET_GROUPS` (`:1769`) and S-001's §1.1 read (`evals/test_s001_smoke.py:171-182`,
    *three groups*) follow 078 (*as 078 defines*).
  - (c) **D20: a journey that chose GB chooses US.** `evals/payroll_exceptions.yaml` (S-001 / 002 / 003): `:36`
    `{country: US, region: null, language: en-US}`; every `£n` -> `$n`, same digits (`:46`, `:136-137`, `:265-288`);
    `:143` `unit: USD`; header `:21-26` rewritten (the dollar now agrees with the market; the ladder is one set of
    numbers in every currency). S-004 (`evals/test_s004_stranger_who_gives_orders.py`): `:467` `market.fill("US",
    ...)`; `:127` B5 *$30 a seat.*, `:147` *in the US*, `:165` *Thirty dollars per site per month* (call 1).
    `evals/test_s010_two_founders.py:404` posts GB on the wire and stays (the cloud still takes GB, 105 FR-6).
  - (d) S-007 (`evals/test_s007_mulchrun.py:1-15`): no longer *the only US market* nor the only region -- the entry
    whose founder left the price out, in Texas. `OTHER_CURRENCIES` (`:23`, `:43-51`) moves to
    `evals/corpus_scenario.py` as a check every corpus journey runs after its report (call 3): no `£`, `€`, `GBP`,
    `EUR` in any text `j.screens` drew, the three views and the binding included; the project's market is the
    entry's (US, en-US, its region). S-007 keeps its TX / `$` / USD asserts.
  - (e) S-014's built project: `evals/preludes.py:410-411` *$150 a month lost (in the founder's $100-$300), the
    $50-$100 band*; `:418` `"currency": "USD"`; `tests/test_report_marks.py:615` `"edgeSaid": "$50 a month"`.
  - (f) S-006's contacts leg (`evals/contacts_leg.py`): the base query's place is the market's (`:345-346`), now US;
    the fake has 59 (30 GB, 29 US, three of each without an email). `:54-55` *Everyone in the US* (*, again*);
    `:371-388` 26 with a work email (29 in the US, 3 with none); `:407` resized 1; `:614-623` *Find 25 more* is the
    one left, 6 credits; `:628` *the 26*; the other country is GB -- `:56` *Practitioners in the UK*, `:651-662`,
    `:693` 27; `:52-53` `LOW_BALANCE` 10 (under a page, 150, and the one name waiting, 12), `:697-699` `required`
    12; *the fake's 53* (`:664`) stays. Counts from `fake.size` on the entry's country wherever the code can read
    them. `tests/test_contacts_marks.py` (a synthetic GB record and the fake's own facts) stays.
  - (g) `evals/interviewer_leg.py:2393, 2455, 2491, 2505`: the participant bodies carry the entry's
    `market["language"]` for the typed `en-GB`. `CURRENCY_WORDS` (`:1126`) reads the currency: unchanged.
  - (h) A unit test on a real entry moves with it: `tests/test_instruction_report.py:62, 107` `"US · en-US"`;
    `tests/test_journey_through_a_host.py:201` `"US"`. Synthetic ones stay (`tests/test_corpus_script.py:43,
    184-185`'s canned entry; `tests/test_instruction_modules_import.py:126`).
- **FR-4 The eval's own fixtures stay GB, on purpose.** `tests/fixtures/corpus/09-fixture.yaml` and
  `10-fixture-b2b.yaml` are the reader's one non-US path (`MARKET_CURRENCY`, `money_text`'s `£`, a GBP price, the B2B
  hourly rate), and the cloud's Market table still serves GB (105 FR-6). Each moves `revision: 11` -> `12` (`:13`;
  `:9`) so `load` takes it; its header (`:1, :10`; `:6`) says: GB deliberately, `expected` unchanged, r12's rule U
  would refuse it. So the reader does **not** mirror rule U; FR-1's new test holds the canon to it.
  `tests/fixtures/compare/09-fixture.*.out.json` (the engine's output on 09) stay; so do the unit tests' synthetic
  `£` (symbol paths, regexes, a recorded capture; Acceptance 4). `tests/fixtures/brief/` went with 052.
- **FR-5 Regeneration, then the zero-spend re-measure.** Before `make unit`, in keel-cloud-docs at the 105 merge (not
  while a stack runs from it): `./gradlew test --tests 'com.keeldiscovery.cloud.corpus.BriefFactsCorpusTest' --tests
  'com.keeldiscovery.cloud.corpus.SpokenGuidelinesCorpusTest'` (`build/brief-facts/*.json`, `build/spoken-corpus.txt`,
  read by `instructions/cloud_corpus.py`; a stale r11 export fails on the symbol) and `./gradlew -q screenContracts
  --args="export build/screen-contracts"` (`dimension-registry.json`, `themes-cases.json`). The committed
  `dimension-registry.json` and `executor-fixtures/THEMES/cases.json` (read by `test_follow_up_ladder.py`,
  `test_feedback_marks.py`, `test_report_marks.py`) are 105's; `build/insights-simulation/` and the executor payloads
  are read nowhere here (checked). Then, in tasks.md: `brief_facts` **101 of 101** (05-paidly *$50 a month or more · 5
  of 8*), `report_overview` **49 of 49**, `compare_correctness` 108 of 108, `spoken_form` 109 of 109, and S-014's
  `healthy_expected` held to the engine (`instructions/compare.py`) **16 of 16** in USD.
- **FR-6 Out of scope.** No new mark, no version bump (marks, interviewer, report, contacts). The pound / euro
  vocabulary stays where it reads a respondent or a currency: `harness/classifier_guard.py:87` (and `en-GB`
  defaults `:509, :520`), `harness/classifier_cases.py`, `instructions/wording.py:115-122`, `overview.py:262`,
  `evals/interviewer_marks.py:68` `PRICE_WORD`, `tests/test_vectors_journey.py:176`. No product fix: a pound on a
  page after 078 is **DRIFT #95** (after 052's #94) in `runs/DRIFT.md`, house shape, the run bundle named.

## Acceptance

1. `make unit` green against 052's branch (**2,531 passed / 56 skipped**), the delta explained in tasks.md (the US
   test, the revision-11 case, canon tests that un-skip once canon and exports are r12).
2. `make eval K="s005 or s006 or s007 or s014"` green on a fresh stack, keel-cloud 105 + keel-web 078: every corpus
   journey US / en-US and FR-3d met; S-006's contacts on the US counts; S-014 16 of 16 and *$50 a month or more · 10
   of 10* on the price tile; durations in tasks.md.
3. Remote journeys green on staging once 105 + 078 are deployed (the smoke's market step included).
4. Grep gates print exactly these (file and count in tasks.md). `grep -rn '£' instructions harness evals tests`:
   `brief_facts.py:42`; `marks.py` calls 42 / 57 / 64 / 65 (7 lines); `marks.toml:261, :263`; `overview.py:262`;
   `text.py:35` (the tested example); `wording.py:119`; `classifier_guard.py:87`; `corpus_scenario.py`
   `OTHER_CURRENCIES`; `interviewer_marks.py:68`; fixtures 09 (5), 10 (6), compare (3 + 3); synthetic or on a fixture:
   `test_follow_up_ladder.py:114`, `test_instruction_brief_facts.py` (17), `_cost_first.py:74`, `_score.py` (3),
   `_spoken.py` (5), `_text.py` (2), `_window_frame.py` (4), `test_interviewer_marks.py:517`, `test_report_marks.py`
   (6), `test_vectors_journey.py:176`; a 2026-09-07 capture, `test_s004_live_choices.py:362-363`. `grep -rn
   'GBP\|en-GB\|"GB"' evals harness`: `classifier_guard.py`, `classifier_cases.py`, `interviewer_leg.py:1126`,
   `test_s010_two_founders.py:404`, `contacts_leg.py`'s other country, `corpus_scenario.py`'s `OTHER_CURRENCIES`.

## Judgement calls (decided; document in tasks.md)

1. **S-004's "£30 a seat" moves** (*$30*, *in the US*, *Thirty dollars*): D20 makes its market US, and the box tests
   an injection, not a currency -- a pound in a US project would be a second, unasserted test.
2. **The two eval fixtures stay GB** (FR-4); whatever walks the drop-down or reads the canon is US.
3. **`OTHER_CURRENCIES` guards every corpus journey** (FR-3d): the pages are already read, and D19 promises no
   founder page shows a pound. An assertion in the journey, not a mark.
4. **`MARKS_VERSION` stays 20; the numbered calls keep their pounds** (FR-2): history records the figure it saw.
5. **S-006's other country is GB** (the fake has no third); `LOW_BALANCE` 10 so both refusals still fire.
