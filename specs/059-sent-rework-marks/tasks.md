# Tasks 059

Built against keel-cloud-docs master `096cecc` (111, contract 24: `guide.interviewsSeen`, `guide-seen {interviews:
true}`) and keel-web master `3fec926` (088, merged), whose `specs/088-sent-rework/tasks.md` *Selectors* are the ids
read here: `guide-interviews`, `guide-pill-page` (`button.guide-pill`), `guide-band`, `guide-chapter`, `persona-line`
(`.ivband`, `data-hearing`), `persona-hear`, `role-count`, `links`, `links-search`, `links-download`, `links-prev`,
`links-next`, `links-range`, `th button[data-sort]` with `aria-sort` on the `th`, `tr[data-invitation]`.

- [x] T001 FR-4 the Sent-open helper (`harness/interviews_screens.pass_interviews_sheet`): a sheet up is skipped; one
  due (the clip present in the served manifest, the contract-24 `interviewsSeen` false, the page on Sent) is waited for
  up to 30 s (088's lazy chunk) and skipped in one `note` step; nothing due, no wait. It keeps each pass in
  `guide["interviews"]` -- `passed` on a journey that does not judge it, `later` on the guide journey's judged record.
  Called by `Interviews.land` (`sheet="pass"` by default, `"hold"` for S-005's first open), `Contacts.go_to_send_more`
  and `interviewer_screens.Persona.sent` (both page objects take the journey's `guide`).
- [x] T002 the harness readers for 088: `register()` walks every page with Next until it is disabled and goes back to
  page 1 (no search; the empty register is `[]`); the action column (no `data-label`) is not a cell; the *Kind · from*
  folded into the footer is put back on each row; `_row(person)` pages to a row for `make_new_link` (*New link,
  {name}*) and `status_cell_offers`; `MAKE_A_NEW_LINK` reads *New link*; `kinds()` reads `role-count` and counts any
  line left under the buttons; `order()`, `links()`, `search()`, `sort()`, `download()`, `go_next()` for G15 / G16.
  `Persona.walkthrough_again` is gone (`how_it_works()` counts the controls of that name); `Persona.hear_band` taps
  `persona-hear` (`HEAR_JS` tags an event inside the band `band`).
- [x] T003 FR-1 / FR-5 `evals/guide_marks.py` **`GUIDE_MARKS_VERSION` 3**: G13 `interviews`, G14 `page_pills`, G15
  `sent_order`, G16 `links`, G17 `role_counts`, with `DESIGN_IDS`; G12 holds that every present clip was read
  (`captions.present`, the three page clips among the 29). `guide_record` drops a pass-only `interviews` (kept as
  `interviews_passed`) and notes every 059 mark a journey carries none of (`SENT_ELSEWHERE_WHY`).
- [x] T004 FR-2 `evals/interviewer_marks.py` **`INTERVIEWER_MARKS_VERSION` 7**: IM30 `the_band_hears_her`
  (`hear_band`); the leg's W1 step holds *How it works* absent and says why (`W1_REPLAY_RETIRED`); IM30 owed on the
  short form and the full leg.
- [x] T005 FR-3 where they run: S-005 (`teaching=True`, the founder journey) -- G13 at `leg_invite`'s first open of
  Sent, G15 / G17 at `leg_invite` and again after the first recording (the band drawn), G16 at `leg_invite` (12 links,
  paged), G14's Sent half at `leg_invite` and its consumer-card half in `leg_contacts_not_b2b`; S-006 -- G14's datasets
  pill in the contacts leg's C1, G16 after the batch (T1); IM30 after the first recording's READY on both.
- [x] T006 FR-5 `instructions/marks.py` gains the Spec 059 paragraph (the changelog); AGENTS.md's paragraph.
- [x] T007 Acceptance 1: `tests/test_guide_sent_marks.py` (103: the sheet-once faults, the page-pill faults, the
  order faults, the range table for n = 4 / 10 / 11 / 14 and its faults, the csv line count, the sort flip, the count
  words, G12's page clips, the pass-by record, 088's ids and words against keel-web's files -- skip before 088);
  `tests/test_interviewer_marks.py` (IM30's 19 faults alone and seeded, the retired face, W1 retired);
  `tests/test_guide_marks.py` / `test_guide_teaching_marks.py` read v3 and the five new marks.
- [x] T008 Acceptance 2 / 3: the stack and `make unit` (below).

## Judgement calls

1. **`register()` pages with Next** (the spec's preference): from page 1, Next until disabled, then Previous back to
   page 1 so the next reader finds the page as the founder left it. It never types into the search box -- the search is
   G16's subject, not the register's.
2. **The Sent-open helper lives in `interviews_screens`** (the spec's preference) and is imported by
   `interviewer_screens` (a module import; `vectors_screens` is imported inside the helper, since it imports
   `interviewer_screens` itself).
3. **`MARKS_VERSION` stays 20**, against FR-5's *21*: `instructions/marks.py`'s rule bumps it only for a change to the
   instruction eval's own rubric, and 088 / 111 moved no screen schema, instruction or corpus file -- 057 and 058 kept
   v20 on the same ground. A bump would leave v20 without a run of record for a ruler that did not move (and the
   certificate is the founder's word only). The two journey rulers moved instead (guide v3, interviewer v7).
4. **G16's range for ten or fewer links**: keel-web 088 draws no pager at all there (its call 8), so *1–n of n* with
   Next disabled is met by the pager's absence (or by a pager that says exactly that).
5. **G16's search term** is the first row in view whose name no other link's who / format / status contains, so the
   narrowing is to exactly one row; *Made* is clicked twice (descending -> ascending -> descending) so the table is left
   as the founder found it.
6. **G14's two halves run where their pages are**: Sent's two chapters on S-005; Contacts' pill is on the datasets view
   only (088 call 11), which a consumer study never reaches -- S-005 holds that its consumer card draws no pill, and
   S-006 (the contacts leg's C1) opens the one clip. A half whose clips are absent passes as not applicable.
7. **G15's band is owed where the account is not on its own AI** (088: no who-asks band on the own door), so S-005's
   first reading (own AI, after the links) has none and its second (Keel's door, after the first recording) has it;
   at least one reading with the band is owed where any is (the remote profile skips the interviewer leg, so none is).
8. **G13's "the next open draws none"** is a plain `goto` read after the overview, as G6's; every later open of Sent
   through the helper is kept in `later` and none may draw the sheet.
9. **IM30's "absent for a retired face"** is a unit-table branch: no journey can record a retired face (keel-cloud 110
   refuses it `FACE_UNKNOWN`), so on the stack the face is Chukwu; a record whose face is retired is met only by no
   button and no hello.
10. **IM30 is read right after the first recording is READY** (before S-006's S2 / S3 reads), on the same Sent the
    popup recorded from; on S-005 the guide journey reads Sent's order and counts again there, with the band drawn.

## Measured (2026-10-20)

**Stack** (`COMPOSE_PROJECT_NAME=keel-e2e-eval-059`, cloud 18082 / web 5183 / oidc 18092, postgres 55432; keel-cloud-docs
`096cecc`, keel-web master `3fec926`; **stack.toml's ports pointed at 18082 / 5183 / 18092 for the run and put back,
not committed**), chromium:

- `make eval K=s005` **1 passed in 296 s** on the first run (`runs/20261021T005129Z-s005-countly`). Guide marks v3
  **17 of 17**, none unmeasured, none not applicable. G13: the sheet at the first open over `interviewsSeen: false`,
  `page-interviews-first`, one `{interviews: true}` 204, `interviewsSeen: true` after, none at the next open nor at
  the three later opens; G14: *Chapter 1 of 2 · Where to start* on `page-interviews-first`, the seam, *Chapter 2 of 2
  · This page* on `page-sent`, in the pill's place, the pill back; the consumer Contacts card with no pill; G15: kicker
  97, total 122, pill 152, (band 186,) cards 190/272, links 323/405, no *How it works*; G16: 12 links, *1–10 of 12*,
  Next to *11–12 of 12*, *Sam Whitfield* searched to one row and cleared back, *Made* descending -> ascending ->
  descending, 13 csv lines; G17: *0 answered of 12 sent · aim for 5 more*, then *12 answered of 12 sent · enough for
  now*; G12 29 clips. Interviewer marks v7 23 of 23 (the short form; IM28 and IM30 met: Chukwu's hello in the band,
  sound on, 5.75 s played, the still back at once).
- `make eval K=s006` **1 passed in 295 s** on the first run (`runs/20261021T005646Z-s006-paidly`). Guide marks v3
  **5 of 5** (G1-G3, G14, G16; the others unmeasured with the why): the sheet passed by once (one `{interviews:
  true}` 204), the datasets pill *How this page works · 2 min* opened `page-contacts` with no chip and closed; 23 links,
  *1–10 of 23*, Next to *11–20 of 23*, *Elena Vasquez* searched and cleared, the sort flip, 24 csv lines. Interviewer
  marks v7 **29 of 29** (IM12 unmeasured as before, DRIFT #86): IM28, IM29 and IM30 met (the band's hello 5.54 s).

**`make unit`**: **2,938 passed / 53 skipped** against master's 2,795 / 53 (+143: 103 in `test_guide_sent_marks.py`,
40 in `test_interviewer_marks.py` -- IM30's 19 faults alone and 19 seeded, the retired face, W1 retired).
