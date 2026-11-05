# Tasks 140 -- The reader sees the whole screen

Branch `spec-140`, worktree `/Users/athulrajeev/Documents/projects/wt/eval-140` (`.git` a file), off master `a619c72`.
Nothing paid; no stack, no model, no key, no walk; the unit suite only. Against keel-web `58068741` (= `ec99fa93` plus
spec 178's spec file alone: no source moved since the brief's sha) and keel-cloud-docs `21376dd0`; neither checkout
edited. Not merged; master untouched. No rubric, reader instruction or `RUBRIC_VERSION` moved; `quality/readers/
dimensions.md`, the corpus and `quality/decisions.toml` untouched.

| Commit | What |
|---|---|
| `9f2ecda` | plan.md |
| `e3da636` | FR-1, FR-2: `READ_JS` (`choices`, the Commitment block whole), the bundle carries them, the reader is told them |
| `9a1f8d8` | FR-3, FR-4b: the Save's wait and its note; `sent_how`, the draft's two fields |
| `4b2c2e9` | FR-4: the health gate's one restart; the Vite count in the head |
| `aabce03` | FR-5: `tests/test_reader_sees_the_whole_screen_140.py`, `tests/fixtures/spec140/` |
| `2e41997` | a study's data keeps `vite_timeouts` only where a log was read (079 / 087 records to the byte); the 409 press tested |

- [x] T001 FR-1 the Choose screen's suggestion. `evals/backtest.READ_JS`: `choices` -- every `[role=radio]` /
  `[role=checkbox]` option as `{label, suggested, why}`: `suggested` is `data-suggested="true"`, `why` the
  `.calib__suggest-why` of the element the radio's `aria-describedby` names with `-why-` in its id (Buyer and payer's
  belief id may stand beside it and is never read as the why); recorded only where one option is suggested
  (`choices: null` elsewhere). `backtest.founder_screens` carries `choices`, `suggested` (139's Check rows) and
  `commitment` into the bundle (none was carried before: the reader never saw 139's suggested rows either).
  `quality/readers.suggestion_said(label, why)` -- *{label} -- Keel's suggestion: {why}* -- is the one function for the
  *Options:* line (`_suggested_options`) and the *Rows:* line (`_suggested_rows`), and the compact line of such a screen
  ends *; Options: {that line}* (or *; Rows:*). A screen with no suggestion reads to the byte as before.
- [x] T002 FR-2 the Commitment check. `READ_JS` `commitment` gains `step` (`{label, value}`, the one-step block's own
  `label.listcheck__field`), `smaller` (`{label, before, value, after}`: *Or a smaller step first*, *Yes, after*, the box,
  *first*) or `null`, and `smaller_add` (the *+ Add a smaller step first* button where drawn); `answers` and `note` as
  137 read them. `AFTER_EDIT_FIELDS` gains `suggested` and `commitment`. `readers._commitment_lines`: *Your step, as
  strangers hear it: ...*, *Or a smaller step first: Yes, after ... first* or *Or a smaller step first: no smaller step
  (the screen offers + Add a smaller step first)*, *What strangers can answer:* and the chips in order, *Keel's note
  beside the step: ...* where served; the counters stay under *Under the list (Keel's guidance, not a row)*. The words
  are held to keel-web's `translate.ts` by test (`LIST_KEEL_SUGGESTION`, `LIST_STEP_LABEL`, `LIST_SMALLER_STEP_*`,
  `COMMITMENT_ANSWERS_TITLE`).
- [x] T003 FR-3 the Save wait. `harness/vectors_screens.Corridor._press_primary`: the wait for the next address runs to
  `SAVE_BUDGET_S * patience` (60 s scripted, 660 s on a back-test -- the seed's), polled every `SAVE_POLL_MS` (2 s);
  DRIFT #80's 409 second press is kept (made once the refusal is seen, 4 s after); once the address moved, the `/v2/`
  writes the press started settle (at most `SAVE_SETTLE_S`, 10 s). Past `SLOW_SAVE_S` (10 s) a transcript note --
  *founder's Save took N s to move the page (past 10 s: a slow writer, waited up to 660 s) -- {url}* -- and
  `Corridor.slow_saves`. No fixed 10 s left in the method (pinned).
- [x] T004 FR-4 the web health. `stack/processes.wait_or_restart(url, timeout_s, restart=, say=, ok_statuses=, label=)`:
  the gate; on a 500 or a timeout it says so (*keel-web: the health gate failed (...) -- restarting it once and waiting
  again (60s, spec 140)*, printed as `[up] (eval) ...` into the walk's backtest log), restarts once, gates again, and
  raises `HealthGateTimeout` *... (after one restart, spec 140)*. `stack/web.up` uses it after the spawn, and a web of
  this profile's own pid that is up but not answering 200 is stopped and spawned once (said) before the gate; a port
  held by anything else still raises `PortTaken`. `quality/cycle.py`: `WEB_LOG` (`runs/.stack/web.log`),
  `VITE_TIMEOUT` (*transport invoke timed out*), `log_size` before each back-test and `vite_timeouts(log, since)` after it
  (`Study.vite_timeouts`; the whole file where it started over), `vite_total` into the head (`vite_timeouts`) and the
  line under the typos line: *- Vite "transport invoke timed out": 58 lines in runs/.stack/web.log during the walks
  (spec 140)* -- said only where a walk saw one, so a record without is 126's to the byte.
- [x] T004b FR-4b the Current solution draft's two fields. `vectors_screens.sent_how` (the draft body's `how`, `""` kept,
  None where the write carried none); `list_answer` keeps `seen["sent_how"]` only where sent. `evals/corpus_scenario.
  answer_boxes_faults`: where `sent_how` is present, *the draft's two fields* `{answer, how}` against the two boxes as
  typed (each trimmed, the second `""` when empty); where absent, *the draft's one Answer* against `join_answer(what,
  how)` as before (the API path, a web before 177). The bundle's answer record says *sent as answer* / *sent as how*
  where 177 sent them.
- [x] T005 FR-5 tests: `tests/test_reader_sees_the_whole_screen_140.py` (38): keel-web's words and markup pinned; a Choose
  page per shape (suggested with a why, a why beside a belief id, none); the Check row through the same function; the
  Commitment page with and without a smaller step, with the note; the six recorded screens re-read (below); a page
  whose Save moves after 15 s (waited, noted, `slow_saves`), a fast Save (no note), a Save past a 3 s budget (still
  stops), a 409 pressed again once (DRIFT #80 kept); a health endpoint that 500s once (one restart, passes), stays 500 (raises after one restart), answers 200 (no
  restart); `web.up`'s two restart paths; the Vite count per walk (`walk_one`) and in the head's line; FR-4b's four
  cases. Fixture: `tests/fixtures/spec140/recorded_screens.json` -- the six screens as the bundles recorded them
  (`keel read back` dropped) and, under `drawn`, what each screenshot draws that the bundle does not carry.
- [x] T006 the gate (below).

## FR-5 -- the five screens (and the Commitment check), re-read with the new capture

The bundles keep no DOM: each screen is drawn again as keel-web `ec99fa93` draws it, from the bundle's own words
(kicker, intro, title, options, the *Keel will test* box) and what its screenshot shows (the suggestion and its why, the
step boxes, the chips -- transcribed into the fixture), read by the new `READ_JS` in chromium, laid over the recorded
screen and handed to `readers.founder_screens`. Text only; no model. What the founder-reader now gets that cycle 14's
did not:

1. **08-fresco · choose-solution.compatibility** (`20261105T025958Z`, screen 13) -- *Options:*
   `- Could talk into their phone over the noise on site -- Keel's suggestion: Site noise may drown out speech, so this
   is the condition most likely to be missing for some of them.`; the compact line ends with the same.
2. **10-palus · choose-solution.compatibility** (`20261105T033230Z`, screen 13) -- `- could link the company's bank
   account to an outside service -- Keel's suggestion: Linking a bank account to an outside service needs data access
   and often someone's approval, so some finance leads would be unable to do it.` (the third of three).
3. **13-aircaps · choose-solution.compatibility** (`20261105T040639Z`, screen 13) -- `- Had their phone online -- Keel's
   suggestion: A phone with no connection in a noisy or busy place is the most likely gap, and it would stop the
   captions entirely.`
4. **21-codyco · choose-solution.compatibility** (`20261105T102029Z`, screen 13) -- **no change**: the screenshot draws
   no suggestion (two plain radios, *Could forward unanswered calls to another number* / *Ran OPERA Cloud, Sihot or
   Apaleo as their PMS*). The R7 1 there read the screen right; it was not a capture gap.
5. **13-aircaps · choose-solution.adoption_friction** (`20261105T040639Z`, screen 18) -- **no change**: the screenshot
   draws no suggestion (*Wear the caption glasses in conversations* / *Charge the glasses every day*). As 4.
6. **13-aircaps · check-commercial.commitment** (`20261105T041653Z`, screen 18; FR-2's) -- new lines: `Your step, as
   strangers hear it: order the caption glasses with free returns`, `Or a smaller step first: Yes, after try a pair of
   caption glasses first`, `What strangers can answer:` `- Yes, I'd order the caption glasses with free returns`,
   `- Probably yes`, `- Probably not`, `- No`; the counters (*7 / 9 words.*, *6 / 9 words.*) stay as guidance.

## The gate

`set -o pipefail; make unit 2>&1 | tail -1` on `2e41997` against keel-web `58068741` and keel-cloud-docs `21376dd0`,
2026-11-05 11:08 ET: **9 failed, 5541 passed, 81 skipped in 422.80s (0:07:02)**. The nine are master's own, the same
nine on `a619c72` against the same siblings (10:52 ET: **9 failed, 5503 passed, 81 skipped in 302.65s**) -- keel-cloud-docs
moved past 216 (the cards' digest, the corpus' spoken-form records), none touching a file of this spec:
`test_cloud_198_mirror_130::test_commitments_soft_yes_is_on_every_list`,
`test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed`,
`test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`,
`test_cloud_216_mirror_139::test_the_cards_are_the_vendored_copy_at_216s_digest`,
`test_corpus_r19::test_the_backtest_record_holds_every_served_item_to_the_spoken_form`,
`test_instruction_spoken::test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart`,
`test_instruction_spoken::test_the_record_follows_registry_revision_13s_five_changes`,
`test_lock_frontier_110::test_a_record_written_after_170_keeps_every_rule`,
`test_money_cards_redrawn_118::test_the_record_of_record_keeps_every_spoken_rule`.
The branch adds 38 passing (5503 + 38 = 5541) and breaks none; spec 140's own file: 38 passed.

## Judgement calls (each with the spec line it bends)

1. **The compact line carries the suggestion** (FR-1, *in both the founder-reader's full text and the compact one*):
   `quality/readers/founder.md` describes `{{earlier}}` as *kicker and question only*; the instruction is untouched
   (FR-6), and only a screen that drew a suggestion gains the tail *; Options: {label} -- Keel's suggestion: {why}*.
   Every other compact line is 078's to the byte.
2. **`choices` is recorded only where a suggestion is drawn** (FR-1, *for every option*): within it every option is
   there with `suggested` and `why`; a screen with none records `choices: null`, so respondent shots and older-shape
   screens carry nothing new.
3. **The Commitment chips do not make the screen an options screen** (FR-2): `Screen.has_options` is unchanged, so the
   rubric's scope on that screen is cycle 14's and cycle 15 compares with it (FR-6).
4. **The reader's labels are the spec's words, held to keel-web's constants** (FR-2): the drawn `.listcheck__k` is read
   by `textContent` and recorded, but the reader text uses `readers.COMMITMENT_*` (pinned to `translate.ts`), since the
   page upper-cases them in CSS.
5. **The re-read redraws, it does not replay** (FR-5, *re-read from their recorded bundles with the new capture*): a
   bundle has the PNG and the read, never the DOM; the screens are drawn from the bundle's words plus the screenshot's
   transcribed parts, then captured and read. Two of the five drew no suggestion (4, 5 above): the spec's list said
   they did; the screenshots say not.
6. **"The network settles" is the press's own writes draining** (FR-3): Playwright's `networkidle` resolves once per
   document and means nothing after a SPA's push; the press tracks the `/v2/` writes it started and waits them out
   (at most 10 s) after the address moved. The 409 second press now goes once the refusal is seen (+4 s), not after a
   10 s wait.
7. **The slow Save is its own transcript note** (FR-3, *the step's note*): `_press_primary` holds no handle to the
   step it runs inside, so the note is a separate `ok` record beside it (*founder's Save took 17 s ...*), and
   `Corridor.slow_saves` keeps the numbers.
8. **web.up restarts its own unhealthy web too** (FR-4): beside the gate after a spawn, a web of this profile's pid
   that answers non-200 is restarted once (said) rather than refused as a taken port; a foreign owner still raises
   `PortTaken`. One restart per `up` either way.
9. **The Vite count is per walk, the back-test step only** (FR-4, *seen during a walk*): bytes `web.log` gained between
   the start and end of each `make backtest`, summed over the cycle; the read step is not counted. The head line is
   said only when a walk saw one (as the typos line), so records without are byte-equal.
10. **The two fields are compared apart** (FR-4b, *reads `answer` + `how`*): `{answer, how}` against the boxes as typed
    (each trimmed, `""` when the second is empty) -- stricter than comparing the joined texts, and it names the field
    that moved (*the draft's two fields*).

## Left open

- 139's other reads (`own_row`, `leave_out_line`, `nobody_else`) are in `READ_JS` but not carried into the bundle or told
  to the reader; nor is `scale_lines`' phrase box (`label.listcheck__field`, *LIST_PHRASE_LABEL*). Not in 140's FRs.
- The Vite hang's cause is still unknown; FR-4 retries the gate, not a page that never draws mid-walk (21-codyco
  COMMERCIAL's seed).
- keel-cloud-docs moved to `21376dd0` (219-227 merged): the cards' digest and the spoken-form records moved, so nine
  tests are red on master `a619c72` and on this branch alike (listed under the gate); the reader digest follows the cards
  in its own task (spec 140 *Out of scope*).
- Commits carry the brief's `Claude Fable 5.1` trailer; the builder was Claude Opus 5.5.
