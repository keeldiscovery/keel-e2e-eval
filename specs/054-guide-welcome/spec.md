# Spec 054 -- The guide's welcome, as the eval sees it

keel-cloud 106 (**contract 20**: `ProjectSummary.guide {welcomeSeen, openersSeen[]}` and `POST
/v2/projects/{id}/guide-seen {what: "WELCOME" | "OPENER", stage?}` -> 204, idempotent, revision-neutral) and keel-web
080 (the welcome sheet at the first open of a project whose `welcomeSeen` is false). Design of record: keel-cloud-docs
`canon/designs/onboarding-videos-design-2026-10-17.md` §3, §5 (D29: the files are keel-web's own `public/guide/`),
§7.1 (the twelve cues), §8 D24 (once per project, Skip the only control), §8.3. **The welcome only**: the openers
(D25) and the explainers (D26 / D27) are later specs; the mark family leaves them room. Selectors, the seam and the
asset names are 080's, the wire 106's; where either settles a detail it is marked *as 106 / 080 define*.

## Rules

- **FR-1 The page object.** `harness/vectors_screens.py` gains `GuideWelcome(page, recorder)` beside `Corridor`, acting
  and reading, asserting nothing (the module's rule). Selectors (`[data-testid=…]`, as 080 defines): `guide-welcome`
  (the sheet), `guide-face` (the `<video>`), `guide-caption`, `guide-snippet[data-cue]`, `guide-skip`, `guide-replay`.
  Methods: `present(timeout_s)` / `absent(after=…)` (absence read only after the page has drawn the project's first
  screen and received the summary that carries `guide`; never a bare sleep); `face()` (`paused`, `muted`, `autoplay`,
  `readyState`, `currentTime` twice 600 ms apart, `error` code, the captions track's `src` and `mode`); `caption()`;
  `cue()` (the snippet's `data-cue`, or None); `controls()` (every button and link inside the sheet, with its words);
  `skip_in_view()` (Skip's box inside the viewport, and `elementFromPoint` at its centre is Skip); `skip()` and
  `escape()` (each returns the `guide-seen` requests the press caused, method, body and status); `replay()` (*Play
  again*: `guide-replay` if visible, else the help menu's trigger *as 080 defines*, then `guide-replay`; returns the
  requests caused); and, local only, `seek(seconds)` / `cues_fired()` over `window.__keelGuide`.
- **FR-2 The welcome on every corpus journey** (S-005 / S-006 / S-007 / S-014), a new leg `leg_welcome(j)` right after
  `leg_project`, both profiles:
  - (a) at the first open (where *Start* lands, `/p/{id}`): `guide-welcome` present; the summary the page received
    says `welcomeSeen: false`; `guide-face` playing by judgement call 1 and muted; captions on (`guide-caption`
    visible with words, and the `<video>` carries a captions track whose `src` ends `welcome.vtt`);
  - (b) Skip, read before any cue has fired: visible, enabled, in view without scrolling at **1280×720** (the harness's
    window: no context passes a viewport, so Playwright's default) and at **390×844** (`set_viewport_size` while the
    sheet shows, then back), and the sheet's **only** control (D24: no other button, link or label);
  - (c) Skip pressed (S-006 / S-007 / S-014; Escape on S-005, FR-3): the sheet gone within 1 s; exactly one `POST
    …/guide-seen` with body `{what: "WELCOME"}` (no `stage`), answered 204; the project's `revision` (`/overview`) the
    same before and after; the same POST once more on the wire -> 204, revision unchanged (106's idempotence);
  - (d) the next open (`goto /p/{id}`): no sheet; the project's `ProjectSummary` on the wire (the `/v2/projects` row,
    or the read 106 names) says `guide.welcomeSeen: true`, `openersSeen` `[]`; and the next founder write -- the
    context step's *Save* -- answers **200** on its first press (no 409 CONCURRENCY; DRIFT #80's second press unused);
  - (e) the sheet never returns: `Corridor.frame()` gains `welcome` (the sheet's count), held 0 on every corridor
    frame the journey reads after (d).
- **FR-3 The walk, once per matrix: S-005, local profile only** (`run(…, welcome_walk=True)` from
  `evals/test_s005_countly.py`), through the seam, before (c):
  - (a) the cues served at `{web_base}/guide/welcome.cues.json` are twelve (§7.1), ids unique, `at` strictly rising;
  - (b) `seek(at + 0.05)` for each in order: `guide-snippet[data-cue]` reads that cue's id after each seek, and
    `cuesFired` after each is the one before plus that id (monotonic, no repeat, never shrinking);
  - (c) Escape skips: as FR-2 (c), the POST included;
  - (d) after (d) of FR-2: *Play again* shows the sheet (video near 0, Skip in view), Skip closes it, and **no**
    `guide-seen` request goes out; *Play again* once more, `seek` past the last cue to the video's end: the sheet
    closes by itself and posts nothing; the summary still says `welcomeSeen: true`, the revision unchanged.
- **FR-4 The guide marks**, a journey ruler of their own (`evals/guide_marks.py`, the shape of
  `evals/interviewer_marks.py`: `MARKS` rows of mark / record key / rule, `score`, `scorecard`, `owed`):
  **`GUIDE_MARKS_VERSION = 1`**; `MARKS_VERSION` untouched (no corpus or model output moves). Record keys `welcome`
  (FR-2), `walk` and `replay` (FR-3); `openers` and `explainers` reserved for the later specs (G6 on). Marks:
  - **G1 once per project** (`welcome`): the sheet at the first open with `welcomeSeen: false`; absent at the next
    open and on every later frame; one WELCOME POST from the page in the journey;
  - **G2 skippable from the first frame** (`welcome`): Skip visible, enabled, in view at both sizes and the only
    control, before any cue; the press closes the sheet within 1 s;
  - **G3 seen is remembered on the wire** (`welcome`): 204 on `{what: "WELCOME"}`, 204 again on the repeat;
    `welcomeSeen: true` after; revision unchanged; the next founder write 200;
  - **G4 replay posts nothing** (`replay`): both replays open the sheet and close it with zero `guide-seen` requests;
  - **G5 the cues fire in order** (`walk`): FR-3 (a) and (b).
  G4 and G5 are measured on S-005 local only. On every other journey and on the remote profile their subjects are not
  in the record, so they are **unmeasured -- reported, never passed** (interviewer_marks' rule, its line 11), and the
  bundle's step says why: *keel-web reads `window.__keelGuide` only in its test build and staging serves the production
  build* (the `REMOTE_TYPES` precedent). The journey writes `guide.json` and `guide-marks.json` and fails on any owed
  mark unmet. Each mark has a seeded fault in `tests/test_guide_marks.py`.
- **FR-5 The remote profile.** FR-2 runs whole (it needs no seam); FR-3 does not (a `kind="note"` step names it).
  `leg_welcome` adds at most **5 s** to a journey: Skip at once, timed from the sheet seen to the next open's absence
  read, the seconds in the step's record, asserted on both profiles (FR-3's walk excluded).
- **FR-6 Every other journey passes the sheet by.** A sheet over the first screen would take the clicks of S-001,
  S-003, S-004, S-012 and `evals/tools/curated_proof_run.py`. `harness/browser.py` `MarketStep.start(welcome="pass")`
  (and `evals/preludes.create_project`, which forwards it) waits up to 5 s for `guide-welcome` and, if it comes,
  presses Skip in one `kind="note"` step; absence there is not a failure. The corpus journeys pass
  `welcome="hold"` (a `Journey.hold_welcome` field `run()` sets), so `leg_welcome` judges it. **S-012's file is not
  touched**: its `leg_project` keeps the default and passes the sheet by; its live cell is not run for this spec.
- **FR-7 Out of scope.** The openers' banner, the explainer pill and band, the welcome's tappable snippets (§7), the
  video's words or HeyGen (no transcript is checked against the audio), reduced motion, and the end-of-video post on a
  first showing (FR-3 ends only a replay). No product fix: anything the page shows that the design or 106 / 080 does
  not say is a **DRIFT entry numbered from #95** (after 052's #94; if 053 has spent #95 by the merge, the next free
  one, with the house's numbering note) in `runs/DRIFT.md`, the run bundle named.

## Acceptance

1. `make unit` green (**2,541 passed / 53 skipped** on master `03b31c2`; the new count measured and the delta
   explained in tasks.md): each of G1-G5 with a seeded fault (a second sheet at the next open; a second WELCOME POST;
   Skip below the fold at 390×844; a second control on the sheet; a 409 on the next write; a revision moved by the
   POST; a POST during a replay; cue ids out of order; `cuesFired` shrinking; eleven cues), the unmeasured rule (no
   `walk` / `replay` -> G4 / G5 unmeasured, never met), and `MarketStep.start`'s pass-by on a page with and without
   the sheet.
2. `make eval K="s005 or s006 or s007 or s014"` green on a fresh stack against keel-cloud 106 + keel-web 080: guide
   marks G1-G3 met on all four, G4 and G5 met on S-005; `leg_welcome`'s seconds per journey in tasks.md.
3. Remote journeys green on staging after 106 + 080 are deployed: G1-G3 met, G4 / G5 unmeasured with the step's why,
   each journey's welcome seconds under 5.
4. DRIFT entries from #95 for anything the page shows that the design does not say (expected candidates: words on
   the sheet beyond the caption; Skip's word; where *Play again* lives).

## Judgement calls (decided; document in tasks.md)

1. **"Playing" on a muted autoplay video** is `paused === false` and `muted === true` at the first read. `currentTime`
   rising between two reads 600 ms apart and `readyState >= 2` are recorded and required only where the browser
   decodes the file: the harness launches Playwright's bundled Chromium (`evals/conftest.py:211`), which may not
   decode an H.264 `mp4`; a `MediaError` 4 there is a note in the bundle, not a failure and not a DRIFT (the
   browser's limit, not the page's). The cue walk runs on the seam's clock, so it holds either way.
2. **Play again** is pressed by its test id: `guide-replay` if visible; otherwise the help menu's trigger *as 080
   defines* opens it first. The harness never hunts by words; if neither is found, that is a DRIFT entry.
3. **S-012 is not touched** (FR-6): the live cell spends a host's model, and the welcome owes it nothing it does
   not already owe S-005.
4. **The next open is a `goto` in the same page**, not a cleared storage or a second device: keel-web may keep the
   sign-in in storage, and the wire's `welcomeSeen: true` is the proof that the flag is the cloud's.
5. **S-005 dismisses with Escape** and the other three with Skip, so both doors are pressed once per matrix on
   local; the remote S-005 presses Skip.
