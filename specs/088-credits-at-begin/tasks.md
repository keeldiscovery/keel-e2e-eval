# Tasks 088 -- The harness reads one charge per interview: Begin posts, 30 credits land, readings cost nothing, an inactive link says so

Branch `088-credits-at-begin` (worktree `wt/eval-088`, `.git` a file), off master `a610122` (086 merged). Read only:
keel-cloud-docs -- the live checkout at `ad5f6441` (spec 160, corpus revision 19) and one snapshot exported by `git
archive` into a scratch folder and named in `stack.toml` for the run only (restored after; never committed):
**`68ff142a`** (156's last docs commit: contract 45, `InferenceCharge.VERSION` 12, still corpus revision 18, before
158-160). **`PRICE_VERSION` 11 -> 12.** `REVISION` 18, `MARKS_VERSION` 21, `INTERVIEWER_MARKS_VERSION` 13 and
`RUBRIC_VERSION` 2 unchanged. **No paid call**: no walk, no reader, no adviser call, no model, no `make eval`. Nothing
merged or deployed; every commit pushed to the branch.

**Built before keel-web 131.** FR-1 and FR-2's and FR-3's wire parts are built and gated. What needs keel-web 131 --
the browser's Begin posting the charge (FR-2) and the inactive page's one line (FR-3) -- is written and **behind one
marker**, `harness/interview_charge.WEB_131_BUILT` (`False`; `KEEL_WEB_131=1` turns it on for one run): in a journey
the step is a note *SKIPPED -- keel-web 131 not yet built: ...* that asserts only what holds either way (never two rows
under one key); in `make unit` two tests skip with the reason *keel-web 131 not yet built*. **When 131 merges the
coordinator sets `WEB_131_BUILT = True`** (one line) and runs the journeys below.

| Commit | What |
|---|---|
| `e21670a` | FR-1: price version 12; INTERVIEW 30, INTERPRET and THEMES 0; §6.3's five-participant row re-summed |
| `e81094b` | FR-2: Begin on the wire -- the scripted posts, one INTERVIEW row of -30, none on a second Begin; the screens behind the marker |
| `b2f90f6` | FR-3: the inactive link on the wire; the page behind the marker |
| this commit | this file, `AGENTS.md`'s spec-088 paragraph |

## Unit

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `a610122`, keel-cloud-docs `1602f8b4` snapshot (086's tasks.md) | 3,712 | 0 | 0 | 61 |
| master `a610122`, keel-cloud-docs `68ff142a` snapshot | 3,712 | 0 | 0 | 61 |
| branch at FR-2 (`e81094b`), `68ff142a` snapshot | 3,740 | 0 | 0 | 62 |
| **branch, keel-cloud-docs `68ff142a` snapshot** | **3,746** | **0** | **0** | **63** |
| master `a610122`, live keel-cloud-docs `ad5f6441` | 3,448 | 78 | 40 | 207 |
| branch, live keel-cloud-docs `ad5f6441` | 3,482 | 78 | 40 | 209 |

**The branch is green on `68ff142a`.** +34 passed is exactly `tests/test_credits_at_begin_088.py`'s 34 that run; +2
skipped are its two keel-web 131 tests. Master is green on `68ff142a` too: no unit test read keel-cloud's charge table
before this spec, which is why the old `PRICE_VERSION` went unnoticed on 156's snapshot (the new
`test_the_mirror_is_keel_clouds_charge_table` now reads it).

**On the live checkout** (revision 19) the branch's 78 failed and 40 errors are **exactly master's set**, node for
node. Every error and 72 of the failures are `CorpusError: ... revision is 19; this eval reads revision 18 only`. The
other six are all **spec 089's** (revision 19, the three moved controls, the frames), the same six 086 named:

- `test_backtest.py:76` and `test_corpus_r18.py:135` / `:160` / `:276` -- revision 19 itself;
- `test_follow_up_ladder.py:69` -- 159's Relative advantage scale;
- `test_interviewer_marks.py:918` (was `:915`; FR-1's fixture comment moved it three lines) -- 158's ITEM_MORE clip
  *And one more?*.

## FR-1 -- the prices -- `e21670a`

- [x] T001 `harness/interviewer_fake.py` and `harness/contacts_fake.py`: `PRICE_VERSION` **11 -> 12** (IM1's
  `_pairs`, `evals/interviewer_marks.py:178`, and CM3, `evals/contacts_marks.py:110, 127`, compare every HOLD to it, as
  before).
- [x] T002 `harness/interview_charge.py` (new): the mirror of 156 -- `PRICE_VERSION` 12, `INTERVIEW` /
  `INTERVIEW_CREDITS` 30, `READ_PRICES` `{INTERPRET: 0, THEMES: 0}` (and `READ_PRICES_V11` 10 / 8 for the record),
  `project_credits(people)` and `FIVE_PARTICIPANTS` = **1,355**: §6.3's framing 540, brief 105 and conversation 560 as
  they were, each reading 0 (was 5 x 9) and 30 at each person's Begin.
- [x] T003 The five-participant figure, moved wherever the harness states it (below).
- [x] T004 The interviewer leg's reading deltas re-pinned: the read-on-arrival HOLD and every INTERPRET / THEMES HOLD of
  the leg's ledger is held at **0** (`_read_on_arrival`, the *no other row* step), and the change of face's
  `before - after == 400` says why no reading can move it now.
- [x] T005 `tests/test_credits_at_begin_088.py`: both fakes at 12; the mirror held to keel-cloud's own
  `InferenceCharge.java` (VERSION, INTERVIEW, INTERPRET, THEMES, and the founder-side rows the fakes state) -- skipped
  by name on a keel-cloud before 156; §6.3 at 1,250 (v11) and 1,355 (v12); no harness line states the old total.

**Every figure that moved:**

| File:line (before) | Was | Now | Why |
|---|---|---|---|
| `harness/interviewer_fake.py:38` | `PRICE_VERSION = 11` | `12` | 156's `VERSION` |
| `harness/contacts_fake.py:39` | `PRICE_VERSION = 11` | `12` | same (no contacts price moved) |
| `tests/test_interviewer_marks.py:816` | `(11, 400, 2_000_000, 400)` | `(12, ...)` | same |
| `tests/test_interviewer_marks.py:41` (`_reading`) | HOLD `-35` (an invented figure) | `-READ_PRICES[action]` = 0 | a reading's and the themes' HOLD is written at 0 |
| `evals/test_s012_journey_through_a_host.py:34` (docstring) | *about 1,250 credits, $12.50* | *about 1,355 credits, $13.55* | §6.3 at version 12 |
| `evals/test_s012_journey_through_a_host.py:1189` (the spend step's expectation) | *1,250 credits ($12.50 at list)* | `FIVE_PARTICIPANTS` 1,355 ($13.55), *§6.3's 1,250 with each reading at 0 and 30 at each person's Begin* | same |
| `evals/test_s012_journey_through_a_host.py:1239` (`spend.json`) | *1,250 credits* | 1,355 (version 12) | same |
| `Makefile:275` (the `keels-ai` head) | *about 1,250 credits ... $12.50* | *about 1,355 credits ... $13.55* | same |
| `tests/test_keels_ai_cell.py:441` | `"1,250 credits" in head` | `"1,355 credits"` and `"$13.55"` | the head's pin |
| `tests/test_matrix_cells.py:259` (docstring) | *1,250 ... $12.50* | *1,355 ... $13.55* | same |
| `matrix/cells.toml:177` (comment) | *About 1,250 credits a run -- $12.50* | *About 1,355 ... $13.55* | same |
| `evals/interviewer_leg.py` `_read_on_arrival`, the *no other row* step | (no pin on the HOLD's credits) | every reading / themes HOLD at 0 | INTERPRET 10 -> 0, THEMES 8 -> 0 |

The *about $2.44 of actual inference* beside each figure is left as it was (§6.3's cost column is not this spec's;
156's tasks.md says the speech path's cost is not on the ledger).

**Not moved, with why** (156's pins, read):

- `evals/interviewer_leg.py:178` (now `_Wire.credits`) and `evals/contacts_leg.py:129` -- `creditsAvailable` readers;
  no price in them.
- `evals/contacts_leg.py:422` (`GRANT_CREDITS - 150` after the first page) and `:691` (the stand-in to `LOW_BALANCE`
  10) -- both read before or without any interview; the answered decision-maker's Begin (from keel-web 131) falls
  between them and the second page, whose receipt is read against its own `balance_before`, so nothing moves. The
  contacts leg never opens a link after its balance is lowered to 10, so it never meets the inactive gate.
- `evals/interviewer_leg.py:3186` (`_low_balance`, `LOW_BALANCE` 100) -- above 30: every link stays active there.
- `evals/test_s012_journey_through_a_host.py:992-1027` (the first job's drop, `CONTEXT_INTERPRET` 3) and
  `evals/preludes.py:75-79` (the credits line on an OWN account) -- no price of 156's.
- `harness/vectors_script.py:1631` -- moved under FR-2 (it composes, not posts; below).

## FR-2 -- Begin on the wire -- `e81094b`

- [x] T006 `harness/vectors_script.py`: `BEGIN_PATH` (`/interview/begin`), `RESPONSE_PATH`, and
  `PersonInputs.scripted_posts(token, recall, **extra)` -- the scripted person's posts **in order**: Begin (no body),
  then the one response. `vectors_script` composes the body and posts nothing itself; the posting is the interviewer
  leg's, which now posts in the script's order (judgement call 1).
- [x] T007 **Where the scripted Begin posts** (`evals/interviewer_leg.py`, S-006's full leg, Keel's door stand-in):
  - `_choice_link` -- the Let-them-choose link answered in writing (`format` TEXT): `_begin(..., twice=True)` between
    the link's intro and the response: 204, **one row** under `interview:<invitationId>` of
    `CreditLedgerEntry.interview`'s shape (kind and action `INTERVIEW`, credits -30, `price_credits` 30,
    `price_version` 12, no job, no cost, `reason` `invitation:<id>`, this project), the balance 30 lower; **a second
    Begin** 204 with no row added (none under the key but the one) and the balance unmoved. Then the response.
  - `_recorded_link` -- the AI link answered from the recorded path: `_begin` once, right after the GET and **before
    the first `/interview/answer` window** (the page's Begin precedes every window), then the response.
- [x] T008 The *no other row* sweeps let a Begin's row through (`interview_charge.is_charge`: kind `INTERVIEW` under an
  `interview:` key, -30, this project): the interviewer leg's (and one row a key, recorded as
  `record["interview_charges"]`) and the contacts leg's.
- [x] T009 **The browser half, behind the 131 marker.** `harness/browser.py`'s Begin press is unchanged (its docstring
  says what it posts from 131). `_begun_on_screen` reads the row after each link a stranger begins on the screens on
  Keel's door: the AI link (`_ai_link`, S-005 and S-006), the chip link (`_chip_ends_it`, S-005 and S-006) and the
  contacts leg's decision-maker (S-006). With the marker off the step is a note, *SKIPPED -- keel-web 131 not yet
  built*, asserting at most one row; on, it asserts exactly one of the shape above.
- [x] T010 Tests: the key, `charged_once`'s faults (eleven ways wrong), the sweeps, `scripted_posts`'s order, the two
  scripted links' order (Begin before the response; before the first window), the screens' marker; keel-web posting
  `interview/begin` (skipped: *keel-web 131 not yet built*).

## FR-3 -- the inactive link -- `b2f90f6`

- [x] T011 `evals/interviewer_leg._inactive_link` (S-006's full leg, after the recorded link, before the change of
  face): the balance stood in at **29**; two fresh text links made (`WAITING_PERSONS`) and opened -- each **200
  `{state: INACTIVE, message: "This link is no longer active."}`** exactly, no digit, no *credit*, and no ledger row
  written; the balance raised to **30**: the first link **served** (`state` OPEN, its parts); its Begin (`_begin`)
  drops the balance to **0**, where **the begun link is still served and the never-begun one reads INACTIVE**; the
  balance put back where it stood.
- [x] T012 `_inactive_on_screen`: the page's one line (keel-web 131: the line, no number, no *credits*) -- **behind the
  marker**: a note *SKIPPED -- keel-web 131 not yet built* until then; on, it opens the link in a fresh context, waits
  for the line and holds the page's text to `page_faults`.
- [x] T013 `stack/ledger.stand_in_balance` takes `label` (default `low-balance`, so the contacts and interviewer legs'
  keys are unchanged) and `what` (the reason's words): one balance moves three times in one run under the UNIQUE key
  (`inactive-under`, `inactive-at-one`, `inactive-back`); a label is `[a-z0-9-]+` or refused.
- [x] T014 Tests: the INACTIVE body and the Begin route held to keel-cloud's `InterviewController` and the gate's 30 to
  the INTERVIEW price (skipped by name before 156); what reads inactive, served and a clean page; the leg's order and
  labels; the label guard; keel-web drawing the inactive line (skipped: *keel-web 131 not yet built*).
- [x] T015 The gallery's recorded expectations gain nothing (no example walks an inactive link).

## FR-4 -- decided before

- [x] T016 `quality/decisions.toml`: no entry names keel-cloud 156 (D-2026-10-29-11 names spec 157's recording at
  lock, not 156); nothing to mark.

## FR-5 -- nothing else moves

- [x] T017 The six remote journeys: the remote profile skips both legs' database half by name (as before), so no ledger
  assertion of this spec runs there; nothing beyond the credits line moved (S-012's spend record states the new
  figure, asserts nothing new).
- [x] T018 The quality cycle: the back-test walk records `creditsAvailable` and asserts no balance; its founders sign up
  on Keel's AI with a fresh grant (2,500), and the largest entry has 20 people -- framing, the lock's 400 and 20 x 30
  stay well above 30, so every link is active through a walk.
- [x] T019 The noise check reads no ledger and opens no link. Unchanged.

## Acceptance

- [x] `make unit` on the `68ff142a` snapshot: **0 failed** (3,746 / 63 skipped against master's 3,712 / 61).
- [ ] `make eval K=s006` on the local stack at cloud `68ff142a` or later: FR-2's scripted Begin (one row, none on the
  second) and FR-3's wire -- **left for the coordinator** (the stack is down; starting it, and any journey, is the
  coordinator's). Can run before keel-web 131: the page-side steps record *SKIPPED*.
- [ ] After keel-web 131 merges: `WEB_131_BUILT = True`, then `make eval K=s005` (the AI link and the chip link: one
  Begin, one row each) and `K=s006` (the same, the decision-maker's row, and the inactive page) -- the coordinator's.

## Judgement calls

1. **The scripted Begin posts from the interviewer leg, in `vectors_script`'s order.** The spec says
   `vectors_script.py` "posts the response directly"; it composes the body (`PersonInputs.response`) and posts nothing.
   The direct posts are `evals/interviewer_leg.py`'s two scripted links (`_choice_link`, `_recorded_link`); the order
   lives in `vectors_script.scripted_posts` and those two post by it.
2. **FR-2's assertion on S-006's Let-them-choose link, not S-012.** S-012 runs on the founder's own door locally (an
   own-AI founder writes no row, 156 T011) and on Keel's door only on the remote profile, where the ledger is never
   read. S-006's interviewer leg is the one journey standing a founder on Keel's door locally with the ledger in reach.
3. **FR-3 is "a new short one" inside S-006's full leg**, not S-012's host, for the same reason, and because the leg
   already makes links on the wire and owns the balance stand-ins. The acceptance's `K=s012` becomes `K=s006`.
4. **The drop "again" is the Begin's own** (30 -> 0): below 30 by the charge itself, which is the founder's case (a
   link begun on the last interview's credits), and 156's test of a begun link served while another on the same
   balance is INACTIVE is walked there too (the second waiting link).
5. **The boundary pinned exactly**: inactive at 29, served at 30 (156: *INACTIVE at 29, served at 30*).
6. **One marker for everything 131 owns**, a constant plus `KEEL_WEB_131=1` for one run against a 131 build; with it
   off a journey records the skip and asserts only what holds either way (at most one row under a key), so S-005 and
   S-006 can run today.
7. **The leg's unit tests read source order** (`inspect.getsource`) for the Begin-before-response and the FR-3 walk,
   as 086's tests did for the follow-up walk: the legs need a stack to run.
8. **`INTERVIEWER_MARKS_VERSION` stays 13**: no mark reads the INTERVIEW row (IM1 and IM13 filter on their own
   actions); the Begin assertions are the leg's own steps, recorded in `record["begins"]`, `["begins_on_screen"]`,
   `["inactive"]`.
9. **§6.3's cost column (about $2.44) is not re-stated**: the spec moves the credits ("the rest as it was"), and the
   speech path's cost is on no ledger (156's *what did not hold*).
10. **The `_reading` fixture's HOLD goes to 0**, not left at its invented -35: the fixture is a ledger, and at version 12
    a reading's HOLD is 0.

## What did not hold

- `make eval`: not run (the stack is down; the coordinator's).
- The browser half of FR-2 and the page of FR-3 are not asserted until keel-web 131 merges (the marker).
- The live checkout is not green: revision 19 and keel-cloud 158-160 are spec 089's (the six named above, the rest the
  revision refusal) -- unchanged by this spec.
