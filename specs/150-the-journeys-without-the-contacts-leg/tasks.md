# Tasks 150 -- The journeys without the contacts leg

Branch `150-journeys-without-the-contacts-leg`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-150` (`.git`
a file, asserted first), cut at master `bdaaebb`. Built by a builder (Claude Opus 5.5) on 2026-11-09 ET. Read only:
keel-web master **`4e78debb`** and later (185 merged: `specs/185-interviews-is-sent-alone/tasks.md` *What keel-e2e-eval 150
is owed*, `e712e7e5` FR-4 the guide, `78d70c54` FR-3 Send more, `f11fd64f` FR-2 the pages, `be9ed1cd` FR-1 the nav and the
redirects; the checkout's head moved under the build to `309a54a6`, spec 182 only -- no file 150 reads moved), read in
`src/lib/translate.ts` (`INTERVIEWS_SUBPAGES`, `SEND_WHO`, `SENT_KICKER`), `src/components/SideNav.tsx`,
`src/components/interviews/SendMorePopup.tsx`, `src/routes/AppRoutes.tsx`, `public/guide/*.cues.json` and `manifest.json`;
keel-cloud-docs master **`c87d1066`** (244's spec committed, nothing of it built: `ContactsController` and the contact
sources still there). Nothing paid: no stack, no model, no key, no walk, no journey, no cycle -- the unit suite only. Not
merged; master untouched; every commit pushed as it landed. The corpus, `quality/decisions.toml`, the readers and
`MARKS_VERSION` (24) untouched.

| Commit | What |
|---|---|
| `b363c65` | FR-1 the leg goes: the three modules and their test file removed, the page objects cut, S-006's links on Sent |
| `d3b5a02` | FR-2 the marks: contacts marks retired, guide marks v4, feedback marks v2 |
| `55c72a7` | FR-3 the redirects: S-005's `leg_old_addresses`, held offline and pinned to keel-web's routes |
| `c64ee75` | FR-3 follow-up: FR-1's endpoint scan reads the cloud's routes alone (it caught FR-3's page addresses) |
| `0d7089f` | FR-4 the record: README, AGENTS.md, `backtest.py` |
| `efe79a4` | FR-5 the stand-ins' guards kept (they lived in the removed test file) |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1 the leg goes** (`b363c65`). Removed: `evals/contacts_leg.py` (789 lines), `evals/contacts_marks.py` (309),
  `harness/contacts_fake.py` (134), `tests/test_contacts_marks.py` (282, 12 tests). `harness/interviews_screens.py`
  (1,065 -> 836 lines): the `Contacts` page object, `send_from_dataset`, `WHO_DATASET`, `CONTACTS_CLIP`,
  `FORMAT_NOT_AVAILABLE` and every Contacts / dataset / several-links string (`START_FROM_IT`, `DATASET_OPEN`, `SIZE_IT*`,
  `SHOW_FIRST`, `FIND_MORE`, `SAVE_PICKED`, `COPY_AS_NEW`, `NAMES_*`, `GO_TO_SEND_MORE`, `CHIP_*`, `CONTACTS_B2C_TITLE`,
  `CONTACTS_NEED_CREDITS_LINE`, `FOUND_STATUS`, `SEND_LINKS_TITLE`, `SEND_LINKS_DOWNLOAD`) gone; `arrived()` waits on
  `.wtstrip, .sent__kinds, .ccard__title, .intro[role=note]` (no `.contacts__tabs`, `.dsopen__title`, `.dseditor`);
  `SEND_WHO_IDS = ("send-who-OWN", "send-who-GROUP")`; `SUBPAGES = ["Sent"]`; `nav()` reads the one row
  (`NAV_ROW = .side-nav a.side-nav__item[href$="/interviews/sent"]`, current when `aria-current="page"`, any sub-row still
  drawn read into `subs`); `kicker()` reads `p.corridor__kicker` (`SENT_KICKER` *Interviews*); `REDIRECTED` and
  `redirected()` (FR-3). `.ivsub` was never read by the harness, so nothing went for it. `evals/corpus_scenario.py`:
  `leg_invite`'s nav step holds the one row current, no sub-rows and the kicker (*Interviews*, keel-web 185 FR-1);
  **`leg_sent_more`** (S-006's extra where the contacts leg stood -- judgement call 1); the module docstring and the
  Journey's `stack` note. `evals/open_link_leg.py`: `ways` = OWN, GROUP (the step's words *the two ways*).
  `evals/scope_journey.one_kind` (S-016) holds the cards and the register's kinds alone (the contacts picker's `GET
  contacts/datasets` and Contacts' tabs went -- judgement call 3). `evals/test_s005_countly.py` /
  `evals/test_s006_paidly.py`: no contacts leg. Docstrings that named the leg (`interviewer_leg`, `interviewer_marks`,
  `scope_marks`, `stack/ledger.py`, `harness/interview_charge.py`) say it is past. Tests moved in place:
  `test_credits_at_begin_088` / `test_frontier_tier_105` / `test_haiku_5_5_121` (the price-version pins hold the
  interviewer's fake alone; `CONTACT_PAGE` / `CONTACT_EMAIL` no fake's), `test_sample_export` (the export before
  `leg_sent_more`), `test_screens_as_drawn_090` (the way by name; no `WHO_DATASET`), `test_guide_sent_marks` (the helper's
  callers: no `Contacts.go_to_send_more`). New: `tests/test_journeys_without_contacts_150.py` (15).
  **`harness/contacts_fake.py` did not stay**: no journey seeds people through the cloud's contacts endpoints any more --
  its only callers were the contacts leg and its marks, and a pin scans `evals/`, `harness/`, `stack/` for any
  `/contacts/datasets|suggest|plan` or `/managed-requests` route (none). The eval founders' fake-source routing keel-cloud
  244 FR-3 removes is needed by nothing here.
- [x] **FR-2 the marks** (`d3b5a02`). `CONTACTS_MARKS_VERSION` (2) retired with its file -- never a row of
  `MARKS_VERSION` (043 call 135), so **v24 stands**; `instructions/marks.py` records it in a *Spec 150* paragraph.
  `evals/guide_marks.py` **v3 -> v4**: `WELCOME_CUES` thirteen (`phone-interview` then `interviewer-clip`), the at-list in
  the test without 51.84; new mirrors `SCOPED_WELCOME_CUES` (8 / 9 / 8 / 9), `INTERVIEWS_FIRST_CUES` (five: `pi-ask`,
  `pi-yes`, `pi-format`, `pi-answers`, `pi-close`), `LANDING_INTRO_CUES` (seven, no `li-contacts`), each pinned to keel-web's
  own `public/guide/*.cues.json` (judgement call 5); `PAGE_CLIPS` = Sent's two chapters; `CONTACTS_CLIP`,
  `_contacts_pill_faults` and `corpus_scenario.contacts_pill` gone; G14 reads Sent's pill alone (a record's `contacts`
  reading is not read; a record before 150 with only that reading is *not applicable* -- judgement call 6);
  `SENT_ELSEWHERE_WHY` and the module text say G16's paging runs on S-006 (`leg_sent_more`). `evals/feedback_marks.py`
  **v1 -> v2**: FM3 (Keel's base query carries no industry) retired -- its one subject was the contacts leg's read of
  Contacts' tabs (judgement call 2). The interviewer, scope and report marks cited no contacts card in a rule, only
  `contacts_marks` as a shape in their docstrings; those now say it is retired. `report_marks.SOURCE_WORDS` holds
  (185: *Contacts dataset* / *Keel-managed* are still served on old rows).
- [x] **FR-3 the redirects** (`55c72a7`, `c64ee75`). `corpus_scenario.leg_old_addresses`, S-005's extra where its
  NOT_B2B refusal stood: `/interviews/contacts?view=names`, `/interviews/contacts/old-dataset?send=COMMERCIAL_B2B&dataset=old`,
  `/interviews/managed?from=nav`, `/interviews/keel-managed?from=nav`, each landing on exactly
  `{web}/p/{id}/interviews/sent` (the query dropped, no hash) with Sent drawn, 088's sheet passed by after each (G13's
  *later* opens). The harness has **no route-pin pattern and no journey dry mode**, so the one test file
  (`tests/test_old_addresses_redirect_150.py`, 5) runs the journey step itself against a page double that redirects as
  the router does, fails by name on one that keeps the query or never redirects, pins S-005 calling it, and pins
  `REDIRECTED` to keel-web's `AppRoutes.tsx` (each a `Navigate to={`/p/${projectId}/interviews/sent`} replace`, no
  `search` carried). The live redirect is walked only when S-005 next runs (the coordinator's, on a stack).
- [x] **FR-4 the record** (`0d7089f`). `backtest.py` and `quality/cycle.py` counted no contacts step (the back-test walks
  no extra; no lap, END_LEGS entry or cycle field named one) -- so the change is `backtest.py`'s docstring (no Contacts
  fake named) and nothing else moves. README's *The contacts leg* section and AGENTS.md's contacts-marks paragraph say it
  is past since 150, the history kept.
- [x] **FR-5 tests** (`efe79a4`, and the gate below). The two stand-in guards that lived in the removed
  `test_contacts_marks.py` (the ledger never reached on the remote profile; no value spliced into its SQL) kept in
  `tests/test_ledger_stand_ins.py` (5): the stand-ins stay for the interviewer (`e2e-eval:044:`) and open-link
  (`e2e-eval:092:`) legs. **The `DRY=1` runs were not run: there is no journey dry mode.** `DRY=1` in this Makefile is
  the readers', the walk's, the adviser's and the instruction eval's (prompts printed, nothing called); `make eval K=s005`
  / `K=s006` boots a local stack (Postgres, keel-cloud, keel-web, the runtime) and walks it -- not paid, but a stack run,
  which this brief rules out. What a dry path would show is exercised offline: FR-1's and FR-3's tests run `nav()`,
  `kicker()`, `redirected()` and `leg_old_addresses` against doubles.

## Gate

`make unit` (the worktree's `.venv` a symlink to the main checkout's venv, ignored by git) against keel-cloud-docs
`c87d1066`, keel-web `309a54a6` (185 merged):

- Before (`bdaaebb`): **1 failed, 5828 passed, 81 skipped in 336.65s** -- `test_guide_marks::test_the_twelve_cues_are_keel_webs_own`
  (keel-web 185 dropped the welcome's `contacts` cue).
- After FR-4 (`0d7089f`): **5791 passed, 81 skipped in 318.90s, 0 failed**.
- At the head (`efe79a4`, the last code; this commit adds tasks.md only): **5796 passed, 81 skipped in 319.62s
  (0:05:19), 0 failed**, 2026-11-09 21:52 ET.
- Tests: **5829 -> 5796 (-33)**. Removed: `test_contacts_marks.py`'s 12 functions (58 runs, by difference), G14's five
  Contacts faults and its two off-view cases (`test_guide_sent_marks`), FM3's absent-subject case (`test_feedback_marks`'
  parametrisation over the marks). Added: `test_journeys_without_contacts_150` 15, `test_old_addresses_redirect_150` 5,
  `test_ledger_stand_ins` 5 (moved, not new), `test_guide_marks` 7 runs (the cue counts, the scoped welcomes x4, the sheet
  and the tour, `page-contacts` served nowhere), `test_guide_sent_marks` 1 (G14 reads no Contacts half). Moved in place,
  none weakened but for what left: the version pins (guide 3 -> 4, feedback 1 -> 2), the cue at-list, the price-version
  pins, FM3's test (now *retired*).

**Counts**: files removed 4 (1,514 lines), added 3 test files; 31 files changed through FR-4 (+768 / -2,032).
**Cues** (keel-web 185 FR-4): the welcome 14 -> **13**; the scoped welcomes (problem / solution / solution+money / money)
9 / 10 / 9 / 10 -> **8 / 9 / 8 / 9** (185's commit message lists them in another order, 10/9/9/10 -> 9/8/8/9; the files
read 8/9/8/9 in `WELCOME_CLIPS`' order); `page-interviews-first` 7 -> **5** (`pi-no`, `pi-managed` gone); `landing-intro`
8 -> **7** (`li-contacts` gone); the manifest 42 -> **41**; the page clips 3 -> **2**. **Versions**: `GUIDE_MARKS_VERSION`
3 -> **4**, `FEEDBACK_MARKS_VERSION` 1 -> **2**, `CONTACTS_MARKS_VERSION` 2 -> retired, `MARKS_VERSION` **24** unchanged.

## Judgement calls

1. **S-006 keeps what the contacts leg held that Sent still offers** (`leg_sent_more`). The leg was the only journey that
   pressed *New link* on a row not answered (keel-cloud 093 D7: old link 404, new 200, the same invitation, *Link made*
   moved; an answered row refused ALREADY_ANSWERED) and the only one that read the links table past ten (G16's paging).
   185 keeps both on Sent, so FR-1's *send by Send more* is built as one more decision-maker by name (`SENT_MORE_DECIDER`,
   no corpus person, never answered -- no standing moves, as the leg's one answer moved none), *New link* on that row,
   the refusal on the wire, then `links_reading` at 21 links. It runs where the leg ran: after the sample export, before
   the outside decider and the interviewer leg.
2. **FM3 retired, not left unmeasured.** Its subject (Keel's base query) was read only off Contacts' tabs; with the page
   gone and keel-cloud 244 retiring `/contacts/suggest`, an FM3 that can never be measured is a dead row, so the feedback
   ruler moves to v2 (FM1, FM2, FM4-FM6 hold).
3. **S-016's `one_kind` drops the picker's half** (`GET contacts/datasets` and Contacts' tabs): the page is gone and the
   route is 244's to remove; Sent's one card and the register's one kind hold the rule.
4. **Guide marks move to v4** though the brief does not name the bump: the file's rule bumps on a mark retired or read
   differently (G14's half retired, G5's cue list, G12's page clips). `MARKS_VERSION` does not move (no screen schema,
   instruction or corpus file moved -- 059's ground).
5. **The scoped, sheet and tour cue lists are new mirrors.** The harness held only the whole study's welcome cues; 185's
   counts for the other four are pinned as constants against keel-web's own `.cues.json` (skipped by name on a web before
   185) so a dropped cue that returns is seen. No mark walks them.
6. **G14 on a record before 150**: a `page_pills` with only Contacts' reading (S-006's old records) reads *not applicable*
   rather than met or failed; a Contacts reading beside Sent's is ignored.
7. **The nav's `current`** is read as `[the row's words]` when the row carries `aria-current="page"`, so the journey holds
   `current == ["Interviews"]`; any `side-nav__item--sub` still drawn is read into `subs` and fails the step.
8. **The stand-ins stay** (`stack/ledger.py`, default key `e2e-eval:043:`): the interviewer and open-link legs still
   write them; only the docstring says the contacts leg is past. Their two guards moved to their own test file.
9. **Commit trailers** name the model that built them (*Claude Opus 5.5*, the session's attribution), not the brief's
   *Claude Fable 5.1* -- 147's, 148's and 149's precedent.
10. **FR-3's follow-up commit**: FR-1's endpoint scan first matched `interviews/contacts`, the *page* address FR-3 opens on
    purpose; it now reads the cloud's routes alone.

## Left for keel-cloud 244 (the wire half of contacts)

Nothing in this repo calls a contacts route any more (pinned), so 244 can remove `ContactsController`
(`/v2/projects/{id}/contacts/datasets*`, `/contacts/suggest`, `/contacts/plan`, `/managed-requests`), the contact-source
port and its three adapters, their config, the dataset and managed-request tables, and **the eval founders' fake-source
routing** -- no eval journey needs it. What the harness still reads that 244 keeps (FR-3): the sign-up `source` enum on old
rows (`report_marks.SOURCE_WORDS`: *Contacts dataset*, *Keel-managed*). After 244: `x-keel-contract` moves (a path
removed) -- the harness pins no contract number for a contacts path; `InferenceCharge`'s `CONTACT_PAGE` / `CONTACT_EMAIL`
rows may go -- no test here reads them since this spec.

## Open

1. **The live walks**: S-005 (the nav's one row and the kicker, the four old addresses) and S-006 (`leg_sent_more`, G16 at
   21 links) are held offline only; the next `make eval K=s005` / `K=s006` (or `make remote`) on a stack with keel-web 185
   walks them -- the coordinator's call.
2. 185's *Open* stands (the recorded clips still say *Contacts* / *Keel-managed*; the site copy) -- the founder's, not
   the harness's: G12's word guard does not read those words.
