# Spec 057 -- Guide marks G6–G12: the teaching videos

Design of record: `keel-cloud-docs/canon/designs/onboarding-videos-design-2026-10-17.md` §15 (D42–D49). Against
keel-web 086 and keel-cloud 109 (contract 22). Builds on 054/055 (GUIDE_MARKS G1–G5, the remote profile, the caption
re-read). **Build lean: one gate run; the remote cell is exercised by the founder's own run, not by this spec's CI.**

## Rules

- **FR-1 Marks.** `GUIDE_MARKS` gains: G6 the report sheet plays once on the report's first open and `guide.reportSeen`
  turns true (and does not play again); G7 the Overview shows *How to read this*, and *When a line fails* only once a
  line is NOT_HOLDING_UP or PEOPLE_DISAGREE, `fresh` until watched; G8 the stage band plays two chapters and the chip
  reads 1 of 2 then 2 of 2; G9 the money chapters are the consumer pair on a consumer project and the business pair
  on a business one; G10 an explainer pill is under every calibration question and its band disables Continue while
  open; G11 the openers play once per stage and `openersSeen` fills in Vector order; G12 no caption of any guide clip
  and no snippet text contains a project word (`night|baby|cry|parent|payroll|chocolate|lullaby`), read from
  `public/guide/*.vtt` served by the web.
- **FR-2 Where they run.** G6–G11 in the founder journey that already covers G1–G5 (on the stack and on the remote
  profile with the 90 s navigation timeout); G12 as a unit-style check against the served vtt files.
- **FR-3 Marks file.** `marks` v20 (or the next): the seven rows with their design ids; CHANGELOG.

## Acceptance

1. Unit: the mark evaluators' tables (sheet-once, two-pill rule, chapter chip, pair choice, word guard).
2. Stack: the founder journey green with G1–G12 on chromium.
3. `make check` green: 2,620 on master plus the additions, measured.

## Judgement calls (decide, document in tasks.md, do not ask)

1. Whether G12 reads the vtt files through the web's served URL or the keel-web checkout (prefer served).
