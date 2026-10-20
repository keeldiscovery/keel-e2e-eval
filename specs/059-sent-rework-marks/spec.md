# Spec 059 -- The Sent rework in the marks: the Interviews sheet, the page pills, the real table

Against keel-cloud 111 (contract 24: `guide.interviewsSeen`, `guide-seen {interviews: true}`) and keel-web 088 (read its
`specs/088-sent-rework/spec.md`, `tasks.md` and the AGENTS.md paragraph for the ids and words as landed). Design of
record: `keel-cloud-docs/canon/designs/onboarding-videos-design-2026-10-17.md` §15 (D42–D49). Builds on 057 (GUIDE_MARKS
G6–G12), 058 (IM28/IM29), 044/051 (the interviewer leg, W1), 047 (the contacts leg). **Build lean: one `make unit` plus one
stack run of the founder guide journey and one of the journey that sends links; the remote cell is the founder's own run.**

## What keel-web 088 changed that the harness reads today

- Sent's *How it works* link is gone (`harness/interviewer_screens.py` `walkthrough_again`, `HOW_IT_WORKS`; the W1
  "replayed" reading in `evals/interviewer_leg.py`). The first-visit walkthrough itself is unchanged.
- Sent's links table is TanStack-rendered: no `tr.ppl__more` / *Show all*; paging of 10 (`links-prev`, `links-next`,
  `links-range` = *1–10 of n*), a search box (`links-search`) with *Download (.csv)* (`links-download`) at its right,
  headings as buttons (`th button[data-sort]`, `aria-sort`). `register()` must walk every page (Next until disabled)
  and return every row; it must not search. Contacts' dataset table (`table.ppl`, *Show all*) is untouched.
- A first-open sheet on Interviews (`guide-interviews`) when `guide.interviewsSeen` is false: every leg that reaches
  Sent must skip it the way the preludes skip the welcome and the report sheet, except where a mark judges it.
- Role cards carry their count in the action row (`role-count`); the line under the buttons is gone (`kinds()`).
- The who-asks band: `persona-hear` (*Hear her · 5 s*), the 087 hello.

## Rules

- **FR-1 Guide marks.** `GUIDE_MARKS` gains: G13 the Interviews sheet plays once on the founder's first open of Sent,
  Skip or its end posts `{interviews: true}` once (204), the wire says `interviewsSeen: true` after, and the next open
  draws none; G14 Sent's pill *How this page works* opens the band in place with two chapters (*1 of 2 · Where to
  start*, *2 of 2 · This page*), and Contacts' pill opens its one clip; G15 Sent's order top to bottom is the kicker
  and total line, the pill, the who-asks band, the role cards, the links, and no *How it works* control exists; G16 the
  links table: typing one row's name in the search narrows the rows to it and clearing restores them, a click on the
  *Made* heading flips `aria-sort`, the range reads *1–10 of n* with Next enabled when n > 10 (and *1–n of n* with Next
  disabled otherwise), and *Download (.csv)* sits in the search row and downloads every row (header + n lines); G17 each
  role card's action row reads *<answered> answered of <sent> sent · aim for <k> more* / *· enough for now* / *nothing
  sent yet · invite about <k>*, and the numbers agree with the register. G12's word guard now covers the three page
  clips (29 in the manifest).
- **FR-2 Interviewer marks.** IM-W1's "replayed" reading is retired (the row says why); IM30 *the band's Hear her*: on
  Sent after recording, `persona-hear` plays the hello inside the band and the still returns (≤ 8 s; the 90 s timeout on
  the remote profile); absent for a retired face.
- **FR-3 Where they run.** G13–G17 in the founder journey that carries G1–G12 where it reaches Sent, and G16's paging
  (n > 10) in the journey that sends a batch of links (it already makes more than ten); IM30 beside IM28/IM29.
- **FR-4 Skips.** `interviews_screens` / `interviewer_screens` open Sent through one helper that skips the sheet when
  drawn and records that it did (`j.guide["interviews"]`), so S-006, S-007, S-014 and every other journey pass it by;
  only the guide journey judges it.
- **FR-5 Marks file.** `GUIDE_MARKS_VERSION` 3, `INTERVIEWER_MARKS_VERSION` 7, `MARKS_VERSION` 21; the rows with their
  design ids; CHANGELOG.

## Acceptance

1. Unit: the evaluators' tables (sheet-once, the order, the range words for n = 4 / 10 / 11 / 14, the count words, the
   csv line count, the sort flip, the retired W1 row).
2. Stack: the guide journey green with G1–G17 and the links journey green with G16's paging and IM28–IM30 on
   chromium, web from the 088 build (master once merged).
3. `make unit` green: 2,795 on master plus the additions, measured.

## Judgement calls (decide, document in tasks.md, do not ask)

1. Whether `register()` pages with Next or raises the page size through the search box (prefer Next; never search).
2. Where the Sent-open helper lives (prefer `interviews_screens`, imported by `interviewer_screens`).
