# Tasks 053

- [x] T001 FR-1 revision 12: `instructions/corpus.py` docstring opens on **Revision 12 only** (keel-cloud 105, the
  founder's words, the shape half is `check_corpus_r12.py` less r12's new rule U), `REVISION = 12`, `_REVISION_OF[11]`
  *MARKS_VERSION 19's and 20's corpus, in pounds (six GB entries, before keel-cloud 105: 'the currency amount should be
  dollars')*, the refusal unchanged in code, `cost_said`'s example *about $10 to $30 a month*; `money_text`, `cost_said`,
  `_SYMBOL`, `MARKET_CURRENCY`, `brief_facts.CURRENCY_SYMBOL` untouched
- [x] T002 FR-1 tests: `tests/v9_fixtures.py` `CANON_NOT_R11` -> `CANON_NOT_R12` (and the docstring of `canon_entry`);
  `tests/test_instruction_corpus_r11.py` *reads revision 12 only* and a `"revision 11"` case; `tests/test_corpus_r11_shape.py`
  docstring, `test_the_seven_entries_are_all_at_revision_twelve`, the exported-registry read at 12, `(11, "MARKS_VERSION
  19")` in the older-file refusals, and the new **`test_every_entry_is_a_us_entry_in_dollars`** (through `load`: seven
  `country: US`, `language: en-US`, region `OR` on 04-linerly and `TX` on 07-mulchrun and none elsewhere, every
  `currency` node anywhere in the data `USD`, no pound sign, `GBP` or `en-GB` in any file's bytes). File names keep r11
- [x] T003 FR-2 the marks: `MARKS_VERSION` stays 20; `instructions/marks.py` gains the **Spec 053** paragraph after 051's
  (105 moved no schema, instruction or golden number; v20 reads r12 and refuses r11 by name; the numbered calls keep
  their pounds; the seven r12 sha256s at `7e64f20`, equal to `src/test/resources/keel/corpus-r12/`; the zero-spend rows);
  `tests/test_instruction_marks.py`'s digest test reads the r12 digests (and checks both hash paragraphs are there);
  `instructions/brief_facts.py` `edge_said`'s example *$50 a month*. Calls 42 / 57 / 64 / 65 and `marks.toml:261, :263`
  untouched (history)
- [x] T004 FR-3a: `COMPOSED`, `IDEA_NAMES`, `FOLLOW_UP_LINES` checked -- no `£`, no digit, no renamed phrase -- unchanged;
  the market fallbacks in `harness/vectors_script.founder_inputs` and `harness/corpus_script` -> `"US"` / `"en-US"` (never
  reached), `corpus_script.Market`'s comments
- [x] T005 FR-3b `harness/browser.py`: `MARKET_GROUPS = ("North America",)` as keel-web 078 defines it (078 FR-1: one
  group, one option, the drop-down kept); the `MarketStep` note says why the region locator stays positional now that a
  label match would work; `described_sentence`'s example is `/v2/markets/US`'s sentence (*So the questions will be in
  American English, in dollars and cents, miles, feet and working days.*, as keel-cloud's
  `FounderMarketControllerContractTest` pins it -- copied from the cloud's contract test, not off a stack: none ran this
  pass); S-001's §1.1 step reads *the groups keel-web 078 defines (the United States alone)*
- [x] T006 FR-3c D20: `evals/payroll_exceptions.yaml` `{country: US, region: null, language: en-US}`, 26 `£n` -> `$n`
  (same digits), `unit: USD`, header point 3 rewritten (the dollar agrees with the market; one ladder in every currency);
  S-004 `market.fill("US", ...)`, B5 *$30 a seat.*, *in the US*, *Thirty dollars per site per month*; S-010's wire GB kept
- [x] T007 FR-3d: `evals/corpus_scenario.OTHER_CURRENCIES` and `leg_one_currency` (run after `leg_report`, before the
  extra, on S-005 / 006 / 007 / 014): the project's market is the entry's own (country, region, language off
  `GET overview` against `entry.market`), and `currency_leaks(j.screens)` is empty with the four report views
  (`board`, `insights`, `pilot`, `printed`) among the pages that drew text. S-007's docstring re-said (the price left
  out, in Texas; no longer the only US market nor the only region) and its own sweep removed; it keeps TX / `$` / USD and
  *every page drew text*. Unit test `test_every_corpus_journey_sweeps_for_another_currency_and_holds_the_entrys_market`
- [x] T008 FR-3e S-014 in USD: `evals/preludes.py` the template's comment (*$150 a month lost (in the founder's
  $100-$300), the $50-$100 band*) and the decision-maker's cost total `"currency": "USD"`; `tests/test_report_marks.py`
  `"edgeSaid": "$50 a month"`
- [x] T009 FR-3f the contacts leg on the US (below, *The contacts leg, verified*)
- [x] T010 FR-3g `evals/interviewer_leg.py`: the four participant bodies (answer, transcribe x3) carry
  `j.entry.market["language"]`; `CURRENCY_WORDS` unchanged
- [x] T011 FR-3h: `tests/test_instruction_report.py` `"US · en-US"` (x2), `tests/test_journey_through_a_host.py` `"US"`;
  synthetic ones kept (`test_corpus_script.py`'s canned entry, `test_instruction_modules_import.py`, `test_contacts_marks.py`,
  and `test_feedback_marks.good()`'s hand-written *freelance translators in the UK* record)
- [x] T012 FR-4: `tests/fixtures/corpus/09-fixture.yaml` and `10-fixture-b2b.yaml` at `revision: 12`, GB kept on purpose,
  each header saying so (the reader's one non-US path; `expected` unchanged; r12's rule U would refuse it, the reader does
  not mirror it, the canon test does). `tests/fixtures/compare/09-fixture.*.out.json` unchanged
- [x] T013 FR-5 the zero-spend re-measure against the regenerated exports (below, *Measured*)
- [x] T014 Acceptance 1 `make unit`; Acceptance 4 the two grep gates (below); this file; AGENTS.md / README.md one line each
  (v20 reads revision 12, the four zero-spend rows at `7e64f20`)
- [ ] T015 **owed to the journey pass** (after keel-web 078 is merged): acceptance 2 -- `make eval K="s005 or s006 or s007
  or s014"` on a fresh stack, keel-cloud 105 + keel-web 078 (every corpus journey US / en-US and `leg_one_currency` met;
  S-006's contacts on the US counts; S-014 16 of 16 and *$50 a month or more · 10 of 10* on the price tile; durations
  here). Also owed to that pass: the S-001 / S-004 page reads on 078's drop-down (`MARKET_GROUPS`, the US option, the
  region box), and DRIFT #95 only if a page shows a pound (not written; nothing has been seen)
- [ ] T016 **owed**: acceptance 3 -- remote journeys on staging once 105 + 078 are deployed (the smoke's market step
  included)

## Measured (2026-10-17, no stack)

- **`make unit` before** (master `fe87278`'s code in this worktree, against keel-cloud-docs `7e64f20` at r12): **35 failed
  / 2,405 passed / 150 skipped** -- every red the r11 reader refusing the r12 canon by name (*revision is 12; this eval
  reads revision 11 only*), every canon test that reads through `canon_entry` skipping. Master's own number on its own
  canon (r11) is the coordinator's **2,535 passed / 55 skipped**.
- **`make unit` after**: **2,594 collected = 2,541 passed / 53 skipped, 0 failed**. Against master's 2,535 / 55: **+4
  new** (`test_every_entry_is_a_us_entry_in_dollars`, the `"revision 11"` refusal case, the `(11, "MARKS_VERSION 19")`
  older-file case, the currency-guard unit test) and **+2 un-skipped** (below, D-01: `brief_facts`' and
  `report_overview`'s DRY canon tests, which skipped on every 104+ export). The 53 skips left are the r2-shape journey
  readers (`test_corpus_script.py`, `test_s004_live_choices.py`, `test_policy_v8.py`), unchanged.
- **The zero-spend rows**, against keel-cloud-docs `7e64f20` (spec 105 merged). The exports were already regenerated
  there (`build/brief-facts/*.json`, `build/spoken-corpus.txt`, `build/screen-contracts/`, 2026-10-17 15:53 local) and
  were only read; nothing was run in that checkout. The engine rows (compare, S-014) were asked of keel-cloud's own
  `screenContracts compare` in a **scratch copy** (`git archive 7e64f20`, its canon corpus `diff -r`-equal to the master
  checkout's), bound to the committed `src/main/resources/keel/dimension-registry.json`:

  | Row | r12 at `7e64f20` | Read from |
  |---|---|---|
  | `brief_facts` | **101 of 101** (14 + 14 + 14 + 14 + 15 + 15 + 15; reported only *statusWords (insight)*); 05-paidly *$50 a month or more · 5 of 8* | `build/brief-facts/` (`cloud_mod.read`, `brief_facts.compare`) |
  | `report_overview` | **49 of 49** (7 parts on 7 entries) | the same, `overview.compare` |
  | `compare_correctness` | **108 of 108** (15 x 4 B2C, 16 x 3 B2B) | the engine, scratch copy |
  | `spoken_form` | **109 of 109** (74 composed items + 35 faces, none known apart) | `build/spoken-corpus.txt` (`test_instruction_spoken.py`) |
  | S-014 `healthy_expected` | **16 of 16**, nothing reported; the cost total `USD`, the engine's line *$150 a month · 10 of 10 inside what you said*; no `£` / `GBP` in any of the eight `out.json` | the engine, scratch copy |

  The price medians, cloud and eval alike: Countly *$20 a month · 7 of 8*, ComplianceLog *$100 a month · 6 of 9*,
  Lullaby *$5 a month · 5 of 8*, Linerly *$20 a year · 7 of 8*, Paidly *$50 a month · 5 of 8*, Repeatline *$100 a month ·
  7 of 7*, Mulch Run none (Price left out); the healthy project *$50 a month · 10 of 10* (`test_report_marks.py`). Every
  standing, count and verdict as at r11 but the symbol (105's invariant held; nothing re-typed).

## The contacts leg, verified

Read off keel-cloud's `src/main/resources/keel/contacts/fake-contacts.json` at `7e64f20` through `harness/contacts_fake.py`
(`people`, `size`, `page`) and keel-cloud's `BaseQuery` (`marketFor`: the role's market, else the project's; `placeOf`: a
region the place list knows, else the country -- Paidly's region is null, so `{COUNTRY: US}`):

| Fact | GB (before) | US (now) |
|---|---|---|
| the fake's people | 30 (3 with no work email) | **29 (3 with none)**; 59 in all, 53 with an email |
| *Everyone in the {market}* sized with a work email | 27 | **26** |
| re-sized after the first page of 25 | 2 | **1** |
| *Find 25 more* | 2 names, 12 credits | **1 name (Brenda Lewis), 6 credits** |
| the second dataset on the same search | 0 | **0** |
| the other country | US, *Practitioners in the US*, 26 | **GB, *Practitioners in the UK*, 27** |
| the email refusal's `required` (names waiting x 12) | 24 | **12** |
| `LOW_BALANCE` (under a page, 150, and under the names waiting) | 20 | **10** |

The counts are read from `fake.size` on the entry's country wherever the leg can (`with_email`, `left_after_page`,
`elsewhere_size`), each step's title and assert from them; the fixture's own facts are pinned once (29 in the US, 26 with
an email, 27 in GB) so a moved fixture fails by name rather than silently re-sizing the journey. *The fake's 53* stays.
`tests/test_contacts_marks.py` (a synthetic GB record and the fake's own facts) is unchanged.

## Grep gates (Acceptance 4)

`grep -rn '£' instructions harness evals tests` -- **76 lines, every one in the spec's list**:

```
instructions/brief_facts.py:42                       (1)
instructions/marks.py:499, 652, 654, 706, 707, 708, 714   calls 42 / 57 / 64 / 65 (7)
instructions/marks.toml:261, 263                     (2)
instructions/overview.py:262                         (1)
instructions/text.py:35                              (1, the tested example)
instructions/wording.py:119                          (1)
harness/classifier_guard.py:87                       (1)
evals/corpus_scenario.py:1726                        OTHER_CURRENCIES (1)
evals/interviewer_marks.py:68                        PRICE_WORD (1)
tests/fixtures/corpus/09-fixture.yaml                (5)
tests/fixtures/corpus/10-fixture-b2b.yaml            (6)
tests/fixtures/compare/09-fixture.agree.out.json     (3)
tests/fixtures/compare/09-fixture.disagree.out.json  (3)
tests/test_follow_up_ladder.py:114                   (1)
tests/test_instruction_brief_facts.py                (17)
tests/test_instruction_cost_first.py:74              (1)
tests/test_instruction_score.py                      (3)
tests/test_instruction_spoken.py                     (5)
tests/test_instruction_text.py:25, 26                (2)
tests/test_instruction_window_frame.py               (4)
tests/test_interviewer_marks.py:517                  (1)
tests/test_report_marks.py                           (6)
tests/test_vectors_journey.py:176                    (1)
tests/test_s004_live_choices.py:362, 363             (2, the 2026-09-07 capture)
```

The two new tests that must name the sign (`test_every_entry_is_a_us_entry_in_dollars`'s tokens, the guard's tuple check)
write it `"\N{POUND SIGN}"`, so the gate stays the spec's list exactly.

`grep -rn 'GBP\|en-GB\|"GB"' evals harness`:

```
evals/corpus_scenario.py:1726       OTHER_CURRENCIES
evals/test_s010_two_founders.py:404 the wire's GB (105 FR-6)
evals/contacts_leg.py:60            ELSEWHERE_COUNTRY = "GB" (the other country)
evals/interviewer_leg.py:1128       CURRENCY_WORDS
harness/classifier_cases.py:104, 110
harness/classifier_guard.py:509, 520 (the en-GB defaults)
```

## Judgement calls (decided by the spec, confirmed by the coordinator)

1. **S-004's "£30 a seat" moves** to *$30 a seat*, *in the US*, *Thirty dollars per site per month*, with a US market:
   D20 makes its market US, and the box tests an injection, not a currency. The other UK words in its follow-ups
   (*rota*, *fortnight*) were left: nothing asserts them and the spec names only the three.
2. **The two eval fixtures stay GB** (FR-4): the reader's one non-US path; whatever walks the drop-down or reads the
   canon is US. The reader does not mirror rule U; the canon-only unit test enforces it.
3. **`OTHER_CURRENCIES` guards every corpus journey** (`leg_one_currency`, after the report): an assertion in the
   journey, not a mark. The guard also holds the project's market to `entry.market` (not to `founder_inputs`, whose
   fallback could otherwise agree with itself).
4. **`MARKS_VERSION` stays 20; the numbered calls keep their pounds**; the marks history (v19's r11 digests, v20's *The
   corpus stays revision 11*) is history.
5. **S-006's other country is GB**, *Practitioners in the UK*, 27; `LOW_BALANCE` 10 so both refusals still fire.
6. **Participant language = the entry's `market["language"]`** on the interviewer leg's four bodies.
7. **Test file names keep "r11"** (history); the test *function* names that say a revision say 12
   (`..._at_revision_twelve`, `..._r12_digests_...`, `..._of_corpus_r12`).

## Discovered

- **D-01 (052's, fixed here):** `tests/test_instruction_brief_facts.cloud_facts_at_104` skipped when *any* entry's
  `commercial` lacked `priceMedian` -- but keel-cloud's `BriefFacts` is `@JsonInclude(NON_NULL)`, so 07-mulchrun (Price
  left out, median null) writes no key on every 104+ export, and the two DRY canon tests (`brief_facts` 101 / 101,
  `report_overview` 49 / 49) skipped in every `make unit` since 052 (052 measured them on a scratch copy instead). The
  skip now asks whether *no* entry carries the key (a pre-104 export); both run and pass at `7e64f20`.
- **D-02:** the `make unit` *before* on this worktree was red (35) only because the sibling canon is already r12 while
  master reads r11 -- 105 and 053 refuse each other by name, as the plan's merge-order risk says. Merge 105 and 053 together.
- **D-03:** `described_sentence`'s example is copied from keel-cloud's contract test, not off a stack (no stack this pass);
  the journey pass can confirm it against `GET /v2/markets/US`.
- **D-04:** keel-web's master already carries 078's spec commit (`c0d38e9`, spec and plan only); `src/lib/markets.ts` there
  still lists thirty-one countries in three groups. `MARKET_GROUPS` follows 078's FR-1 as written (one group, *North
  America*); S-001's read proves it when 078 is built and on the stack.
- **D-05:** `test_feedback_marks.good()` is a hand-written record "as S-006's journey writes one (05-paidly's words)" whose
  segment still says *in the UK*; synthetic, nothing compares it to the entry, kept (FR-3h's rule).

## Where things are

| Piece | Place |
|---|---|
| the revision, its refusal | `instructions/corpus.py` (`REVISION`, `_REVISION_OF`, the docstring) |
| the canon's US rule | `tests/test_corpus_r11_shape.py` `test_every_entry_is_a_us_entry_in_dollars` |
| the Spec 053 paragraph, r12 sha256s | `instructions/marks.py` (after 051's) |
| the currency guard | `evals/corpus_scenario.py` `OTHER_CURRENCIES`, `currency_leaks`, `leg_one_currency` |
| the contacts leg's US counts | `evals/contacts_leg.py` (`LOW_BALANCE`, `DATASET_NAME`, `ELSEWHERE_*`, `_the_work`) |
| the drop-down | `harness/browser.py` `MARKET_GROUPS`, `MarketStep` |
| the smoke's fixture in dollars | `evals/payroll_exceptions.yaml` |
