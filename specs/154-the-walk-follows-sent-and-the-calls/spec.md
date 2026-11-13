# Spec 154 -- The walk and the fakes follow Sent's three tabs and the calls

keel-cloud 245/247/248/249 and keel-web 186/187/188/189. The eval's walk, its fake runtime and its remote journeys
must keep walking Keel's door through the re-engineered Sent page and file one call without a Meet, so the quality
cycles and the staging journeys stay green. Nothing here is paid: every run is on the fakes; the one `instruction-screen`
named below runs on host claude only on the founder's word.

## Rules

- **FR-0 Owed since 245/186 (2026-11-12 afternoon).** `dimensions.md` copy at `CARDS_SHA256`
  4dc14231eebf3decfca7b26f26781a0b816e308007a724fcfad2cba2968f5f76; the walk reads the Check with no reword line and
  the Choose line through `choose-asked`, `choose-asked-as-written`, `choose-asked-writing` (waiting past the 90 s
  ceiling plus one GET); the fake runtime's drafts carry no `asked`/`only_if`; the fake's ASKED stub answers every
  row; the new log line *asked after the read-back* is read where the walk reads logs.
- **FR-1 The lock step picks no face.** The walk's Before step posts `expectedRevision` alone (247 FR-1, 187 FR-7); the
  fake serves no `recordOnSend`; the credits assertion on a lock is 70.
- **FR-2 Sent as three tabs.** Selectors for `sent-tab-name`, `sent-tab-group`, `sent-tab-calls` and their panels; the
  walk makes a Read and tap link through **New link** (the kind row when the project has two kinds); the group journey
  through **New group link**; the walk asserts the search box appears from six rows in whichever tab it fills.
- **FR-3 The interviewer per kind.** The fake serves `interviewer` as a list per kind (247 FR-5); a journey sets up one
  kind from its card (the face step, the 400 line, the progress bar words, READY on the fake renderer), then makes an
  AI link for that kind and asserts the other kind's AI row stays greyed; `try/{roleId}` opens for the set-up kind only.
- **FR-4 A call, without a Meet.** The fake runtime plans a call (`POST calls`), signs the person in without Google
  (the fake Google the eval's founders already use on group links, writing the identity on the CALL invitation), and
  uploads a **fake call record**: two short 16 kHz WAVs (silence with a tone marker per filing) and a `keys.json` of
  six filings with one undo, a STORY, a FOLLOW_UP, an OWN_QUESTIONS and a THEIR_QUESTIONS stretch (249 FR-1's shape),
  kept as fixtures under `fixtures/calls/`. The fake transcriber answers each stretch with a fixed sentence; the fake
  classifier names option 3 for item 1 so `heard` is exercised. The journey asserts: the row's statuses in order, the
  filed answers, the story RECORDED, one follow-up, two notes, `heard` on item 1, the 30 ledger line, the n line's
  `unverified` 0 after sign-in and 1 on a second call without it, Google's name with *You wrote* on the first.
- **FR-5 The card, headless.** A Playwright walk of the copilot route (188) with fake `mediaDevices` (two silent
  tracks, a device list of two microphones): the browser check passes, the mic dropdown remembers, Start -> six filings
  -> stretches -> End -> upload hits the fake's record route with three parts. No Document PiP in headless: the Float
  step is asserted absent or disabled, never failed.
- **FR-6 Digests re-pinned.** The vendored contract digest (69) and the `dimensions.md` digest in the eval's own
  guards; `make check` stays green on a fresh clone.
- **FR-7 The instruction screen, once, on the founder's word.** `make instruction-screen HOST=claude K=<entry>/CONTEXT
  N=3 WHY=instruction:context-interpret.md` after 248 lands, read for new refusal classes on the `belief_first_person`
  field against the October baseline; reported, never a pass by rule.
- **FR-8 Nothing else.** No change to the stacks, `score.py`, the bench of spec 151, or spec 153's prototype.

## Acceptance

1. The walk on the fake runtime at cloud 247+248+249 / web 187+188+189 reaches the brief with one Read and tap link,
   one group link, one AI link on a set-up kind and one call, and the three remote journeys are green on staging.
2. The call journey's assertions in FR-4 all hold; the n line reads 1 unverified on the second call.
3. The card walk in FR-5 uploads three parts; the fake's record route returns 202 and the row flips to ANSWERED on the
   poll.
4. FR-0's guards pass at the pinned digests.
