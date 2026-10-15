# Spec 043 -- contract 15 and the contacts journey

The keel-e2e-eval half of keel-cloud 092 (*contact and avatar ports*: `ContactSource`, the `FakeContactSource` the stack
runs by default) and 093 (*Contacts, datasets and the Sent register*: contract 15, `InferenceCharge` 8, document 21),
merged at keel-cloud-docs master **`7850360`**. Its input is 093's *Follow-ups: keel-e2e-eval* -- *"mirror contract 15
and `InferenceCharge` VERSION 8 (`price_version` on every HOLD is 8). A journey through Contacts and batch links on a B2B
entry with the stack's default fake source ... marks: no phone requested, nothing emailed, every CONTACT_PAGE /
CONTACT_EMAIL pair in the ledger, the 422 refusals at a low balance, and a relinked token's old link 404. Nothing new in
the stack's compose or env."* -- and keel-cloud's `canon/openapi-v2.yaml` at contract 15. Sibling of keel-web master
`da0b9eb` (still contract 14; keel-web 068, the Interviews section, is being built in parallel). **No model is called
and no money is spent.**

## What moved

- FR-001 **Contract 15 and charge v8, where this eval reads them.** The eval vendors no copy of `openapi-v2.yaml`, pins
  no `CONTRACT_VERSION` and, before this spec, read no `price_version` and no charge row anywhere (judgement call 138),
  so what moves is what the journeys now read. The register's additive fields (`respondentType`, `format`, `source`,
  `linkMadeAt`, `foundPersonId`, `datasetName`, `answeredAt`, `kinds[]`) and its newest-first order broke no page object:
  keel-web `da0b9eb` draws the People page, the board and the brief on contract 15's wire unchanged, and S-005 / 006 /
  007 ran green on it before any line here moved (the first run below). Routing stays v11; the instruction eval's ruler
  stays `MARKS_VERSION` 19 (call 135).
- FR-002 **The contacts leg** (`evals/contacts_leg.py::leg_contacts`), last on **S-006** (`05-paidly`, B2B), after the
  brief, **on the wire** -- the founder's own session on keel-cloud's routes, the stranger's link on the participant
  routes, keel-cloud's fake restated by `harness/contacts_fake.py`. In order:
  1. on their own AI the founder's Contacts are refused **422 `CONTACTS_NEED_CREDITS`** (D9);
  2. **stand-in** (call 129): the founder on Keel's door with a fresh grant -- `/v2/me` reads `aiPath` KEEL and
     `creditsAvailable` **1,500**;
  3. `GET contacts/datasets`: one tab per kind of people (`PRIMARY`, `COMMERCIAL_B2B`), prices **150 / 12 / 25**, the
     decision-makers' base query (titles `[agency]`, levels MANAGER + DIRECTOR, the market's country GB, no industry,
     11-50 / 51-200 / 201-500) sized free to the fake's own count (**0**: the fake's people are payroll's);
  4. a dataset from Keel's base query (`basedOn` BASE, unsized), sized free to the fake's count; the founder removes
     every chip but the market (call 132) -- *Everyone in the UK* -- and sizes it: **27 with a work email** (30 in the
     UK, 3 with none), the balance and the ledger untouched;
  5. *Show 25*: **25 names, 150 credits**, the fake's own first 25 in fixture order, no email on any row; the receipt,
     `/v2/me` and the ledger at **1,350**; sized again, **2** left;
  6. *Save 3 picked*: **36 credits** (12 each), each saved person carries the fake's own address and status, `FOUND`;
  7. the AI interviewer is refused **422 `FORMAT_NOT_AVAILABLE`** (*"... is not available yet"*) on the batch and on the
     single commercial link, and no invitation is made (call 134);
  8. links for the three in **one batch, as Text**: each handed back once with the saved email, a `.csv` of
     `name,email,email_status,link`, every found person `LINK_MADE`;
  9. the first person opens their link (a `COMMERCIAL_LINK` interview, part 3 alone; the beacon 204) and answers it
     with the corpus decision-maker Kate Alder's picks (call 133): their status reads **FOUND -> LINK_MADE -> OPENED ->
     ANSWERED**;
  10. the Sent register, **newest link first**: the three new rows on top, the answered row `TEXT` / `DATASET` /
      *Everyone in the UK* / `linkMadeAt` / `foundPersonId` / `answeredAt` / `COMMERCIAL_B2B`; the decision-makers' kind
      row **11 links made, 9 answered** (the corpus's 8 and the found one);
  11. *Make a new link* on the second row: the **old link answers 404**, the new one opens, the invitation is the same;
      the register's *Link made* moves; an answered link is refused **422 `ALREADY_ANSWERED`** (DRIFT #83 is stepped
      round here, call 136);
  12. *Find 25 more*: the **2** left, **12 credits** (6 a name), no id from the first page;
  13. a second dataset on the same search sizes to **0** (every one of the 27 was fetched on this project) and its empty
      page charges **nothing** and writes no ledger row;
  14. a practitioners' dataset in the US: **26** with a work email;
  15. **stand-in** (call 130): the balance lowered to **20**; then a page of names is refused **422
      `INSUFFICIENT_CREDITS_FOR_NAMES`** (`required` 150, `available` 20, *"A page of 25 names is 150 credits. You have
      20."*) and the two waiting names' emails **422 `INSUFFICIENT_CREDITS_FOR_EMAILS`** (`required` 24, `available` 20,
      *"Their verified emails are 24 credits, 12 each. You have 20."*), and nothing is fetched, revealed, stored or
      charged (the ledger, the dataset's people and page, and the US size unchanged);
  16. the ledger since Keel's door: the stand-in grant, **three HOLD / SPEND pairs** (`CONTACT_PAGE` 150, `CONTACT_EMAIL`
      36, `CONTACT_PAGE` 12; each HOLD `price_version` **8**, no job, this project; each SPEND 0 with `price_credits` n
      and the Starter-rate cost -- **750,000 / 180,000 / 60,000 µUSD**), the stand-in low balance, **and no other row**;
  17. nothing is emailed: Compose runs `postgres` / `postgres-playground` only, keel-cloud starts with no mail variable,
      its `application.yml` and build carry no mail configuration or starter, the register's rows carry no email field;
      and keel-cloud's code cannot ask for a phone (the port's methods, `FoundContact`'s fields, the adapter's
      `contact_types: ["email"]`; call 137);
  18. **stand-in reversed** (call 131), in a `finally`: `aiPath` OWN and `creditsAvailable` null, as S-007 and the next
      run on the same database expect.
  On the remote profile (the staging twin, no database) step 1 runs and the rest is skipped by name.
- FR-003 **`NOT_B2B` on S-005** (`leg_contacts_not_b2b`, `01-countly`): `GET` and `POST contacts/datasets` both answer
  **422 `NOT_B2B`** -- before the door's gate, so an own-AI founder meets it too (093 call 8's order).
- FR-004 **The contacts marks** (`evals/contacts_marks.py`, `CONTACTS_MARKS_VERSION` 1): fourteen deterministic marks,
  zero spend, over the record the leg writes into the bundle (`contacts.json`; the scorecard `contacts-marks.json`) --
  CM1 sizing free and the fake's count, CM2 every purchase a HOLD / SPEND pair, CM3 every HOLD at `price_version` 8, CM4
  the balance follows each receipt and `/v2/me`, CM5 nobody fetched twice and each page the fake's own, CM6 excluded on
  sizing, CM7 emails only and never a phone, CM8 nothing emailed, CM9 the status follows the link and the register's row,
  CM10 a new link retires the old, CM11 the two credit refusals, CM12 `FORMAT_NOT_AVAILABLE`, CM13
  `CONTACTS_NEED_CREDITS`, CM14 `NOT_B2B`. S-006 owes CM1-CM13, S-005 CM14; a mark the record cannot feed is unmeasured,
  never passed. `tests/test_contacts_marks.py` meets all of them on a good record and fails each on a seeded fault (35
  faults), restates the fake against keel-cloud's fixture, and holds the stand-ins' shape.
- FR-005 **The stand-ins** (`stack/ledger.py`): the only module in this repository that touches the database -- plain
  `SELECT`s for the ledger and the account, and three named writes, each row carrying `reason` *e2e-eval spec 043: ...*
  and a key under `e2e-eval:043:`; values only ever as `psql -v` variables (a unit test walks every SQL argument); the
  remote profile refused by name.
- FR-006 **DRIFT** (`runs/DRIFT.md`): **#83** new (RESOLVED in the second commit, FR-010) -- the found person's row reads the new link's time after *Make a new
  link*, where 093 call 16 says it keeps the first link's; stepped round in a step named for the entry (call 136).

## Second commit -- keel-web 068's Interviews section and keel-cloud's #83 fix

Siblings: keel-cloud-docs **`a4f2c95`** (= `7850360` + the DRIFT #83 fix: `FoundPersonRow.linkMadeAt` keeps the first
link's time; contract unchanged) and keel-web **`752a8c4`** (= `da0b9eb` + 068: People becomes Interviews -- Sent,
Contacts, Keel-managed; People's page, its send popup, the commercial-link popup and the reading batch deleted).

- FR-007 **Page objects** (`harness/interviews_screens.py`, labels copied from keel-web `translate.ts` at `752a8c4`, the
  selectors 068's spec names for this repository): `Interviews` -- W1 (*Got it* and its `PATCH /v2/me`), the side nav's
  group (`.side-nav__group a.side-nav__item`, `.side-nav__item--sub`), the register (`table.ppl--sent`, cells by
  `data-label`, *Show all*), the kind rows (`.role .btn.primary`), *Send more* for someone the founder knows and for a
  dataset's people (step 1's `[role=radio]`, step 2's who / dataset / `.pickrow`, step 3's `.linkbox` or `.pop
  table.ppl--tight` and the downloaded .csv) and *Make a new link* in the status cell; `Contacts` -- the NOT_B2B card,
  the own-AI line, the tabs, *Start from it*, C2's chips (`.prow`, `.qchip__x`), the name, *Size it* / *Size it again*,
  *Show the first 25*, the page of names and *Save n picked*, C3, *Find 25 more*, *Go to Sent → Send more* and the *Not
  enough credits* popup (`dialog.credits-refusal`). Each write returns the response keel-web received. No selector of
  068's was unusable.
- FR-008 **Every journey's links go through Sent** (`corpus_scenario.leg_invite`): W1 the first time the account
  arrives (held to `walkthroughSeenAt`: played exactly when it was null, stamped after), the nav group (*Interviews*,
  *Sent · Contacts · Keel-managed*, Sent current), then per corpus person the kind's *Send the questions* / *Send more*
  -- Text (the other two greyed *Not available yet*), *Someone I know*, the name, *Make their link* -- for the
  specialist and the decision-maker alike (one `POST invitations/batch`, 068 call 11); the register held to the wire
  (one row a person, newest first, Text, *Not opened*). The lock lands on `/interviews/sent`.
- FR-009 **The contacts leg on keel-web's screens** (`evals/contacts_leg.py`): the own-AI line and the NOT_B2B card;
  C1's tabs and base row; *Start from it* (the chips are the base query's), *Size it* (create BASE, size 0); the chips
  removed down to *Where*, the name typed, *Size it* again (27, *About 27 people with a work email match*); *Show the
  first 25* (the 25 drawn are the receipt's); *Save 3 picked and get their emails · 36 credits*; C3 (*Saved · no link
  yet*, the emails); *Go to Sent → Send more* (Text checked, the other two greyed, *People from a dataset* with *Everyone
  in the UK* chosen, *Make 3 links*, the table, the downloaded .csv equal to the batch's); the found person answers on
  the stranger's own screens (`vectors_screens.Interview`, the page's POST equal to the corpus decision-maker's picks);
  Sent's register (the answered row *Text*, *… dataset*, *Answered*, no *Make a new link*); *Make a new link* on Sent
  (the drawn link is the served one); C3's *Find 25 more*; the second dataset made on C2 the same way (sized 0, *Show the
  first 25* off); and the two refusals pressed on screen, each in the *Not enough credits* popup with keel-cloud's
  sentence and one *Close*. Every wire assertion of the first commit stands, and every body keel-web received for a
  contacts or register route joins CM7's sweep.
- FR-010 **DRIFT**: **#83 RESOLVED** by keel-cloud-docs `a4f2c95` -- the step round it is replaced by the straight
  assertion (`_link_times`: the found person's time unchanged, the register's moved) and CM10 holds it too (call 145);
  **#84** new -- no screen starts a reading since 068 deleted the reading batch, while keel-cloud reads a story only on
  `POST readings` and the board counts *read by your AI*; stepped round in a step named for the entry (call 140).

## Results

- `make unit`: **1,910 passed / 53 skipped** (before, the same worktree at `c120f5c` against keel-cloud-docs `7850360`:
  **1,857 passed / 53 skipped** -- contract 15 broke no unit test; the new ones are `tests/test_contacts_marks.py`'s 49
  and the page-object and stack-address guards' four parametrised rows for the two new `evals/` modules).
- `COMPOSE_PROJECT_NAME=keel-e2e-eval make up`, then `make eval K="s005 or s006 or s007"` against keel-cloud-docs
  `7850360` + keel-web `da0b9eb`:
  - before any line here moved: **3 passed** (441 s; bundles `runs/20261015T0357*` to `runs/20261015T0402*`) -- contract
    15 and the newest-first register broke no page object;
  - with the contacts leg, final code: **3 passed, twice** (391 s and 388 s; bundles `runs/20261015T0417*` to
    `runs/20261015T0421*` and `runs/20261015T0423*` to `runs/20261015T0427*`), the contacts marks **13 of 13** on S-006
    and **1 of 1** on S-005 each time, DRIFT #83's step firing on every S-006, the founder's account back on `OWN`
    after each; and once before that (439 s, `runs/20261015T0407*` to `runs/20261015T0412*`) on the leg before calls
    134's single-link refusal and 137's source read were added.
  No model, no money; nothing generated committed.

- **Second commit**, against keel-cloud-docs `a4f2c95` + keel-web `752a8c4` (`make down`, then `make up` on a fresh
  database): `make unit` **1,912 passed / 53 skipped** (the first commit's 1,910 plus CM10's two new seeded faults); `make eval K="s005 or s006 or s007"` **3 passed, twice** (383 s and 353 s; bundles
  `runs/20261015T0610*` to `runs/20261015T0614*` and `runs/20261015T0616*` to `runs/20261015T0620*`). The contacts marks 13 of 13 on S-006 and
  1 of 1 on S-005 each time; W1 played once (the first journey on the fresh database) and never again; the #84 step on
  every reading.

## Disagreements and gaps (reported, nothing edited)

- D-1 **No route reaches a locked B2B project on Keel's door on this stack** (calls 129-131): the stand-in is the eval's,
  named, reversed, local only. On the staging twin the leg would need a Keel's-AI founder whose corridor Keel's own
  Anthropic account walks -- money, so it is not run here.
- D-2 **The fake is a payroll study's people and 05-paidly is translators and agencies** (call 132): Keel's base query
  for Paidly's decision-makers finds nobody in it, which is the fake's honest answer; the 27 are the UK's with a work
  email once the founder removes the chips.
- D-3 **The fake's call counters are not served** (call 137): `FakeContactSource.rowsFetched` / `emailsRevealed` live in
  keel-cloud's process; the ledger's units (6 a name, 12 an email) are the eval's view of them.

## Judgement calls

129 on are this spec's (110-128 are spec 042's). Each is the simplest reading that keeps `make unit` and the three
journeys green where the inputs are silent, and each can be reversed alone.

129. **The founder is stood on Keel's door with a fresh grant by the eval, on the project the scripted runtime built.**
     Contacts are refused to an own-AI account (D9) and open only on a locked B2B project; on a stack with no Keel's-AI
     key a Keel's-AI founder's jobs fail and refund, so no corridor reaches the lock, and keel-cloud has no route
     between the doors. One write sets `ai_path` KEEL and one `GRANT` row tops the balance up to exactly 1,500 (the
     product's grant), after the own-AI refusal is asserted on the same founder. *Why not a second founder*: founder B
     is S-010's, whose list must stay empty, and an ownership move would be two writes into the project's own row and
     document. Reversing it is deleting the leg's door and running it on the staging twin's Keel's door.
130. **The low balance is one `PURCHASE` row of the difference to 20**, as keel-cloud's own `ContactsJourneyTest.balance`
     writes it: the fake's 53 people cannot spend a 1,500 grant below 546. 20 is under a page (150) and under the two
     waiting names (24), so both refusals are seen at one balance.
131. **The stand-in is reversed in a `finally`**: one closing row to zero and `ai_path` OWN, asserted on `/v2/me`
     (`aiPath` OWN, `creditsAvailable` null), because S-007 runs on the same founder minutes later and `own_ai_door`
     fails a founder on the wrong door; a second run on an un-dropped database starts from zero again.
132. **Keel's base query is held to the fake's count (0 on Paidly), then the founder removes every chip but the market.**
     C2a's chips are the founder's to remove; the place kept is the base query's own (GB), so the 27 are the fake's UK
     people with a work email, as 093's follow-up names them. The base query's derivation is held only where it is
     code's table (levels, place, sizes); its titles are the role words because the fake suggests none.
133. **The found person answers with the first corpus decision-maker's picks** (Kate Alder, `vs.person_inputs`), on the
     found link's own option ids -- composed, never generated -- and the leg runs **last**, so the one extra answer
     moves no standing S-006 holds.
134. **`FORMAT_NOT_AVAILABLE` is asserted for AI_INTERVIEWER on the batch and the single commercial link**; CHOICE and
     `POST invitations` are keel-cloud's `ContactsJourneyTest`'s.
135. **The contacts marks are a journey ruler with their own version, and `MARKS_VERSION` stays 19.** The instruction
     eval's marks measure keel-cloud's inference prose; 092 / 093 add no model turn, move no screen schema (contract 15
     is additive, 093 call 26) and no instruction, so no call of that rubric moved. `CONTACTS_MARKS_VERSION` 1 bumps
     when a contacts mark is born, retired or reads differently.
136. **DRIFT #83 is stepped round, not failed**: the register's *Link made* moving, the old link's 404 and the new one
     opening are held; the found person's row is held to the relink's time while the step fires and to the first link's
     time the moment it does not. Which time C3 shows is a design call, not the eval's.
137. **"No phone was ever requested" is held without the fake's counters**, which keel-cloud never serves: no key
     naming a phone in any contacts response (pages, saves, datasets, the batch, the register), every reveal's SPEND at
     the email-only Starter rate (60,000 µUSD an address -- two source credits; a phone is five), and keel-cloud's own
     code read as text (the port has no phone method, `FoundContact` no phone field, every `contact_types` the adapter
     sends is `["email"]`).
138. **Charge v8 is pinned where the eval first reads a charge** -- the contacts leg's ledger (`price_version` 8 on every
     HOLD it wrote, `CONTACT_PAGE` 150 / `CONTACT_EMAIL` 12 and their costs in `harness/contacts_fake.py`); the
     journeys' own-AI founder writes no ledger row, so nothing older pinned v7 to move.

139. **Four things stay on the wire because no screen can say them** (second commit): the AI interviewer's refusal
     (keel-web greys both other formats and never sends them; the greyed radios are held), a relink of an answered link
     (Sent offers *See … answers* instead; held), a dataset in another country (C2's places narrow within the market's
     country, #50), and the empty page of a search sized 0 (C2 turns *Show the first 25* off; held).
140. **DRIFT #84 is stepped round, not failed**: the founder's own session calls `POST readings` -- the call People's
     button made -- in a step named for the entry, so the board's *read by your AI* and the brief read what they read
     before; failing every journey on a design call between two repositories would hide everything after it.
141. **W1 is held to the account, not to the journey**: it plays exactly when `walkthroughSeenAt` was null before Sent
     first opened (the first journey on a fresh database), *Got it* answers 200 and stamps it; later journeys on the
     same founder assert it does not play.
142. **One Send more popup per corpus person** (Done, then the kind's button again) rather than *Invite another*, so
     every link is made from a popup opened on the register's current revision -- the shape of DRIFT #75's stale
     revision, avoided rather than met; the decision-makers go through the same popup (068 call 11).
143. **The page of names is read once it shows the receipt's names**: right after *Find 25 more* the names view drew
     the previous page's 22 for a moment before its re-read; the page object waits (up to ten seconds) for the drawn
     names to equal the fetch's `page`, and the leg asserts they do. It converged on every run, so it is not a DRIFT.
144. **After a chip changes, C2 offers *Size it*, not *Size it again*** (068's `dirty` forgets the size); the page object
     presses whichever is drawn.
145. **Call 136 reversed**: DRIFT #83 closed, so the found person's row is held to the first link's time and the
     register to the new one's, straight, in the leg and in CM10.
146. **`stack.toml` is not 043's**: its absolute sibling paths are this worktree's machine-local setup, so it was
     reverted before the commit (the run used it; the tracked file keeps the repository's relative paths).

147. **The pilot tick waits for its 204** (third commit, 2026-10-15, staging): the first remote run of the three
    journeys against keel-cloud a4f2c95 + keel-web 752a8c4 failed S-006 on the #84 reading -- `INTERPRET` captured
    revision 56 and the project was at 57 by the time it applied (*This project changed while your AI was
    thinking*). The staging rows showed the 57 was the stranger's pilot opt-in, recorded at 06:37:34.52 after the
    answers at 06:37:34.xx; `opt_in_to_pilot` returned on `expect_request` (the request leaving the browser), so
    the founder's `POST readings` and the pilot's `POST .../pilot` reached the box together. Locally the tick
    always landed first (three passes). It now waits on `expect_response` and asserts the 204. A product note for
    keel-cloud: a reading that loses this race is reported as failed and never retried by anything, which with
    #84 (no screen starts a reading) means nobody would start it again.

## Follow-ups

- ~~keel-web 068's page objects~~ -- done in the second commit (`harness/interviews_screens.py`).
- **DRIFT #84** (keel-web and keel-cloud, a design call): which screen starts a reading, or whether keel-cloud reads a
  story on its own.
- **Keel-managed (K1)** has no page object: nothing in the journeys sends a managed request.
- **S-001 / S-002 / S-003 / S-004** still drive People's deleted page; they were already classic-only and are not in
  the set this spec runs.
- **The staging twin**: the leg's Keel's-door half on a real Keel's-AI founder costs a corridor of inference; not run.
- **keel-cloud**: a served view of the fake's counters (or a ledger read) would let the eval drop call 137's indirect
  holds; the AI interviewer (spec 094) will add a hold to CM2 / CM3's subject.
