# Tasks -- spec 092, one open link for a group: the journey, with three strangers signing in with Google

Built 2026-10-30 on branch `092-one-open-link-for-a-group` (worktree `wt/eval-092`), off master `fb7a7f7`; master
`c839572` (the spec's FR-4a) merged in at `a34e4e7`. Pushed after every commit; nothing merged or deployed; no paid or
vendor call (the scripted executor, the stack's fake renderer, transcriber and classifier, the local stub issuer). Read
against keel-cloud-docs master (162 built, contract 48; 164's contract 49 merged meanwhile at `fcec4533`) and keel-web
master `e4f204e` (136 built; 140 a spec only). The spec file is not edited.

| Commit | What |
|---|---|
| `1753854` | FR-1 strangers on the stub issuer |
| `5e984cb` | FR-3 the register read |
| `a34e4e7` | merge of `origin/master` (`c839572`, FR-4a added to the spec) |
| `408294e` | FR-4a Send more's credits note is keel-web 131's |
| `515b035` | FR-2 the journey (S-017) |
| this commit | these tasks and AGENTS.md's spec-092 paragraph |

## FR-1 -- strangers on the stub issuer

- [x] T001 **The env change**: `stack/oidc.py:107` `cloud_env` gains its fifth variable,
  `KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI = {cloud_base_url}/v2/i/auth/google/callback` (`participant_redirect_uri`, :130),
  beside the founder's `KEEL_GOOGLE_REDIRECT_URI`, as 162's tasks.md recommends: the issuer sends the stranger straight to
  keel-cloud, whose 302 lands them on keel-web's `/i/{token}`. (keel-web's dev proxy, `stack/vite.eval.config.ts`,
  forwards every `/v2` to the cloud, so the card's relative `signInUrl` -- `/v2/i/{token}/auth/google/start` on keel-web's
  origin -- reaches keel-cloud too.) `tests/test_stub_oidc.py` `test_the_five_variables_...` (was *four*) re-pinned.
- [x] T002 `stack/auth.py`: `STRANGER_EMAIL_DOMAIN` (:168, `strangers.keel-e2e-eval.test`, RFC 2606's `.test`),
  `ARRIVAL_COOKIE_PREFIX` (:172), `StubStranger` (:176: id, sub, email, name, `given_name` = the name's first word, the
  stub's `given_name` claim), `register_stranger` (:197: `POST {issuer}/identities`, 201 or a RuntimeError naming the
  answer; the `sub` is the stub's `cell-<id>`), `token_of` (:213), `ArrivalSignIn` (:220: refused, landed, token,
  auth_error, cookie, hops), `arrival_cookie` (:236), **`sign_in_arrival(config, group_url, stranger, *, session=None)`**
  (:241): `GET /v2/i/{groupToken}/auth/google/start` (a non-302 is `refused`, e.g. 410) -> the stub's `/authorize` with
  `identity=<id>` appended to the URL keel-cloud produced -> `GET /v2/i/auth/google/callback` -> the 302's Location, the
  arrival's own `/i/{token}` (or `?auth_error=`); every redirect followed by hand, the `keel_arrival_<group>` cookie kept by
  the session (the same session again = the same browser).
- [x] T003 `harness/browser.py` **`Arrival`** (:812) and its pins (:753-:810: `ARRIVAL_CARD`, `ARRIVAL_HEADING`,
  `ARRIVAL_INTERVIEWER`, `ARRIVAL_PLACES`, `ARRIVAL_GOOGLE`, `ARRIVAL_CONSENT`, `ARRIVAL_AUTH_ERROR`, `LINK_INACTIVE`,
  `ARRIVAL_GREETING` / `_WHO` / `_NOT_YOU`, `AI_INTRO`, `CHOICE_WRITE`, `ANSWERED_LINE`; 136's words `arrival_places`,
  `arrival_interviewer`, `arrival_heading` (J-11's rule), `arrival_hello`, `arrival_signed_in`, `ARRIVAL_CONSENT_WORDS`):
  `open` (:831, the card or the inactive line), `read` (:842), **`sign_in`** (:867: `arrival-google` pressed, the
  picker's heading, `chooser_button_selector(stranger.id)` as `Auth.sign_in` does, the landing on another token or
  `auth_error`), `intro` (:894: `data-intro`, greeting, who, *not you?*'s href, the choice's buttons, or the answered /
  inactive line), `write_my_answers` (:917, `choice-write`), `answered` (:923). Never a cookie set by hand.
- [x] T004 `tests/test_open_link_092.py`: registration and the wire sign-in against the **real stub on a socket and a
  stand-in of keel-cloud 162's two participant routes** (`_Cloud`: state `<groupToken>.<random>`, PKCE, nonce, the
  participant redirect URI, no `hd`; the code redeemed at the participant URI; the arrival by `sub`; the cookie keeps the
  token, another session a new one; 410 on a closed group); the env; the browser sign-in's shape.

## FR-3 -- the register read

- [x] T005 `harness/interviews_screens.py` pins (:140-:200): `WHO_GROUP` / `WHO_GROUP_LINE`, `SEND_WHO_IDS`, `SEND_GROUP`,
  `SEND_GROUP_NAME` (`#send-group-name`), `SEND_GROUP_CAP` and `SEND_GROUP_CAP_LINE`, `GROUP_LINK_MADE`,
  `SEND_GROUP_NAME_LABEL` / `_EXAMPLE`, `GROUP_NAME_MAX` 60, `GROUP_CAP` 20, `SEND_GROUP_HINT`, `SENT_STUDY_LINE`,
  `SENT_TABS_LABEL`, `SENT_TAB`, `SENT_GROUP`, `GROUP_NAME`, `GROUP_COUNT`, `GROUP_LINK`, `GROUP_CLOSE`, `GROUP_REOPEN`,
  `GROUP_EMPTY`, `ROW_EMAIL`, `KIND_FROM_GROUP`; `send_make_group`, `send_group_ready`, `sent_study_line`,
  `sent_tab_by_name` / `_by_group`, `group_answered`, `group_link_label`.
- [x] T006 `Interviews.send_group(project_id, kind_label, name, fmt)` (:670): Sent landed (or its first-open sheet passed),
  the kind's primary, step 1's format, the three ways read in order, `send-who-GROUP`, the panel (label, maxlength,
  placeholder, cap line), the button disabled before the name, the name, *Make the link · {word}*, the `POST .../groups`
  awaited and keel-web's one silent retry on a stale revision followed, `group-link-made`, the ready heading, the hint,
  *Copy link*, *Done*.
- [x] T007 `study_line` (:741), `tabs` (:746), `open_tab` (:758), `group_rows` (:771: the same `td[data-label]` cells,
  *Who* the `td b` name alone, the email (`row-email`) read apart and checked to follow the name, *Kind · from* folded from
  the footer, the invitation id, the action's words), `groups` (:796: id, `data-closed`, the name's DOM text as typed --
  CSS uppercases it, so `text_content` never `inner_text` -- the counter, the short link and its `title` url, *Copy
  link*'s accessible name, *Close link* / *Reopen*, the empty line, the rows), `close_group` (:840) / `reopen_group`
  (:845) (the POST awaited, `data-closed` waited for, the section read after).
- [x] T008 Tests: 136's words read off keel-web's `translate.ts`; every test id the harness reads found in the component
  that draws it (SendMorePopup, SentPage, GroupSection, LinksTable, GroupArrivalCard, IntroScreen, AiIntro,
  ParticipantRoute); the By group tab, the arrival card and the intro after the sign-in read off static frames of 136's DOM
  in chromium.

## FR-2 -- the journey

**S-017, a new journey** (`evals/test_s017_open_link.py`; the walk `evals/open_link_leg.py`), not a leg of S-005 -- see
judgement call 1. `make eval K=s017` (not `s015`: see call 2). Steps and asserts, in order (`open_link_leg.py`):

1. `corridor_to_lock` (:193): 01-countly, ALL, on the scripted runtime -- `cs.leg_project`, `leg_context`,
   `leg_interpret_problem`, `leg_calibrate` x3, `leg_interpret_solution`, `leg_persona`, `leg_lock` (their own asserts).
2. `keels_door` (:207): stand-in to Keel's door, `aiPath` KEEL and `creditsAvailable` 2,000. `record_the_interviewer`
   (:227): `POST interviewer/face {face: DAPHNE}`, READY within 90 s.
3. The four strangers registered; each `sub` = `cell-<id>`.
4. `make_the_link` (:245): the three ways in order (names and test ids), the panel, *Make the link · Let them choose*
   (disabled before the name), the POST's `roleId` (the primary kind's), `name`, `format` CHOICE and an integer
   `expectedRevision`, 201, the url drawn = the 201's, the ready heading, *Copy link*, the hint.
5. `stranger_a` (:346): the card (`read_the_card`, :277: the served `GROUP_ARRIVAL` with `placesLeft` 20 and `signInUrl`
   `/v2/i/{token}/auth/google/start`; the drawn h1 = `arrival_heading(founderName, title)`, the interviewer's row,
   *20 of 20 places left*, the `<a>` to `signInUrl`, the sentence, no Begin); the browser sign-in lands on a token other
   than the group's; `read_the_intro` (:310): A's link FULL, `personName` the given name, formats TEXT + AI_INTERVIEWER
   (contract 49's `arrival.email` held to A's when served), the CHOICE intro with *Hi Maya. {heading}*, *Signed in with
   Google as Maya · not you?* to `/i/{group token}`, both buttons; the walk begun by `choice-write`, answered as Priya
   Natarajan (Countly's first opted-in manager with a story); exactly one INTERVIEW row of -30 under A's key; the
   response 200/201 with `format` TEXT; the pilot box drawn and ticked (`pilotOptIn` stored true).
6. `stranger_b` (:385): the card at 19 places, sign-in, intro; *Answer in writing* (Begin 204, one row); the gate answered
   as Marcus Lindqvist; the page on part 1's first question (`problem.frequency`); the page closed.
7. `stranger_c` (:416): the wire sign-in -- hops 302 x3, a token of C's own, the `keel_arrival_` cookie; C's link served
   FULL with C's given name; nothing begun.
8. `a_again` (:439): the card at 18 places; the second browser sign-in returns A's token; the page's line = the served
   ALREADY_ANSWERED message.
9. `b_again` (:457): the same token, the intro, *Answer in writing* (204), the page back on the question B left (no gate
   drawn), still one row for B.
10. `the_register` (:484): the tabs (*By name · 0*, *By group · 1* selected), the study line (`{answered} answered ·
    {planned} planned` from the wire's kinds, `· {counted}` after it), the wire's GroupRow (2 begun, 1 answered, cap 20,
    open, CHOICE, the url), one section (name as typed, *1 of 20 answered*, the url, *Copy link · {name}*, *Close link*),
    three GROUP rows with the three stub emails; A ANSWERED, B OPENED, C SENT or OPENED; `register_faults` (:124): each
    drawn row the wire's -- name, email under it, *Group · opened the link*, the status word, *See answers* on A alone.
11. `close_and_reopen` (:531): *Close link* 204, the section `data-closed` true with *Reopen* and *· closed {day}*, the
    wire's `closedAt`; D's page the inactive line, GET interview the INACTIVE body, D's wire start 410; *Reopen* 204,
    `closedAt` null, D's page the card again at 18 places.
12. `the_ledger` (:565): `ledger_faults` (:108) -- exactly the INTERVIEW rows `interview:<A>` and `interview:<B>` of -30 on
    this project.
13. `restore` (:218, and again in the `finally` if a step failed first); `the_pilot` (:578): `pilotPeople` = [A, GROUP,
    A's email]; the Pilot view one person, A's invitation, A's email.

- [x] T009 `harness/vectors_screens.py` `Interview.walk(..., begin=None)` (:2243, :2292): the test id of the control that
  starts the written interview in *Begin*'s place -- `choice-write` on a Let-them-choose link. Unsaid, every walk presses
  *Begin* as before.
- [x] T010 `tests/test_scenario_set.py`: the set is seventeen; S-017 deterministic and refused on the remote profile.
  AGENTS.md's two *sixteen*s read *seventeen*; its `make eval K=` list gains `s017`.
- [x] T011 `tests/test_open_link_092.py`: the refusal, the per-run ids, who A and B answer as (and Countly gives two),
  `ledger_faults`, `register_faults`, no real address in the walk, `walk(begin=)`.

## FR-4 -- no mark moves

- [x] T012 Nothing in `evals/*_marks.py`, `MARKS_VERSION` (22), corpus REVISION (16) or the gallery moved. The quality walk
  and the gallery reach neither `send_group` nor the groups route (a test holds it). The readers score Send more's
  screens as drawn, the third way included; `contacts_leg`'s Who read is keyed by `aria-checked` and holds with three.

## FR-4a -- Send more's credits note is keel-web 131's (added to the spec mid-build, master `c839572`)

- [x] T013 `harness/interviewer_screens.py` `FORMAT_CREDITS_NOTE` (:99, *Each person who answers uses 30 credits,
  whichever way they answer.*, keel-web `translate.ts` `FORMAT_CREDITS_NOTE`) and `FORMAT_CREDITS` (:100,
  `format-credits`). **What moved, and why**: s006 of 2026-10-30 (`runs/20261030T121939Z-s006-paidly`) read
  `formats["hint"]` -- the dialog's **first** `.hint` -- and since keel-web 131 the first hint under the rows is the
  credits note, drawn before the state line. `SEND_FORMAT_RECORDED` itself (:94) did not move: its words are keel-web's
  unchanged (`translate.ts` `SEND_FORMAT_RECORDED`) and still drawn, under the note. So `Persona.formats_now` (:669) reads
  the note by its test id (`credits`), the state line as the first other `.hint` (`hint`), and keeps every hint
  (`hints`); `evals/interviewer_leg.py` S3 (:604-:610) holds `credits == FORMAT_CREDITS_NOTE`, `hint ==
  SEND_FORMAT_RECORDED`, and every row's `word` None (no *needs Keel's credits* on Keel's door; that word stays the
  own-AI one, and `corpus_scenario`'s own-door read of it is untouched). `tests/test_interviewer_screens.py` pins the
  note to keel-web and the reader and the assertion by source.

## FR-5 -- nothing else moves

- [x] T014 The named and dataset legs, the credits mirror (088), the controls (089/090): untouched. The shared changes are
  additive -- `walk`'s optional `begin`, `cloud_env`'s fifth variable, new page-object methods and classes.

## Gate

| | passed | failed | skipped |
|---|---|---|---|
| master (the brief's record, keel-cloud `a41b6226`, keel-web `e4f204e`) | 3,855 | 0 | 53 |
| this branch, `make unit`, 2026-10-30 (keel-cloud-docs `fcec4533`, keel-web `e4f204e`) | **3,898** | **0** | 53 |

+43: `tests/test_open_link_092.py` 35, `test_scenario_set` +1, `test_interviewer_screens` +2, the rest the merged
master's own. **The journey on the playground stack** (`make up PROFILE=playground`, `make eval K=s017 PROFILE=playground`,
`make down PROFILE=playground`): **1 passed in 111 s**, 140 steps ok, none failed (bundle
`runs/20261030T124113Z-s017-open-link` in this worktree). What it found, besides green: C, signed in on the wire alone, is
OPENED on the register (keel-cloud marks the arrival opened at sign-in; the journey allows SENT or OPENED); the ledger since
the door: the recording's HOLD -400 / SPEND 0, the grant, A's and B's INTERVIEW -30, A's reading's INTERPRET HOLD 0 and
REFUND 0 (Keel's keyless door); the served `Interview.arrival` (contract 49) already carries the stranger's email and the
group url. The first three playground runs failed on the harness's own reads, each fixed before the green one: W1 played
over Sent's own address, the Interviews sheet over the kind cards, and a served item's words are `question`, not `text`.
The remote profile refuses S-017 (`pytest.skip` with the reason).

## Judgement calls

1. **A new journey, not a leg of S-005.** S-005 already carries the interviewer's short leg and Countly's ten people; a
   group leg there would mix the register's rows and the ledger's INTERVIEW rows with the corpus's own. S-017 walks
   Countly's corridor to the lock alone (~80 s on the scripted runtime) and nothing of the corpus's people.
2. **Numbered S-017, not S-015**: `evals/test_s015_problem_only.py` holds S-015 (spec 071); `make eval K=s015` would run
   both. The coordinator's command is `make eval K=s017`.
3. **The founder on Keel's door by the stand-in** (spec 043's, keyed `e2e-eval:092:`) after the lock, and the interviewer
   recorded by `POST interviewer/face` on the wire: a lock on Keel's door never reaches READY on a stack with no Keel's-AI
   key, CHOICE needs a served recording, and an own-AI founder writes no INTERVIEW row.
4. **A answers in the browser, through the written interview** (`walk(begin="choice-write")`): *Answer in writing* is
   keel-web 131's Begin on a Let-them-choose link; A answers as Countly's first opted-in manager with a story (Priya
   Natarajan), B's gate as the next (Marcus Lindqvist); the corpus's answers, not a fourth set.
5. **"Continues where they were" is the kept draft**: keel-web keeps an interview's answers by token in the browser, so
   B's second sign-in in the same browser context must land on the same token (keel-cloud's cookie) and *Answer in
   writing* opens on the question B left, past the gate. Held on the page and by one row for B.
6. **C signs in on the wire** (FR-1's wire path); A and B through the browser (FR-1's browser path, and FR-2's
   greeting, resume and ALREADY_ANSWERED need the browser).
7. **D is the closed link's stranger**: the page's inactive line, the wire's INACTIVE body and start's 410; after
   *Reopen* D's page is the card again (18 places: A and B hold two). D never signs in.
8. **The Pilot view is read after the door is restored**, as `interviewer_leg._read_what_is_left` reads after its own
   restore; the standings and pilot list do not depend on the door.
9. **The register's statuses**: A ANSWERED and B OPENED are asserted; C is SENT or OPENED (the run found OPENED). Every
   drawn word is held to the wire's status.
10. **The remote profile refuses by `pytest.skip`** with the sentence, not a failure: a remote run of the whole set stays
    readable, and the refusal is named in the report.
11. **The stub's `sub` is derived, never supplied** (`cell-<id>`; the stub refuses a supplied one), and `given_name` is the
    stub's (the name's first word): the spec's "(sub, email, name, given_name)" are registered as id, name and email.
12. **The branch merges master rather than rebasing** (the coordinator asked for a rebase): the branch was pushed and the
    rule is no force-push; the merge loses nothing and a later merge to master is clean.
13. **The stack must be booted from this code** for the fifth variable to reach keel-cloud; a stack booted before it
    leaves keel-cloud on its default participant callback (`{KEEL_V2_FOUNDER_BASE_URL}/v2/i/auth/google/callback`,
    through keel-web's proxy), which this branch did not run against. `make down && make up` before `make eval K=s017`.

## What did not hold

- Nothing of the spec. FR-4a's text names `harness/interviews_screens.py` for `SEND_FORMAT_RECORDED`; it lives in
  `harness/interviewer_screens.py`, and its words did not move -- the read did (T013).
