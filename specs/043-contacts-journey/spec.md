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
- FR-006 **DRIFT** (`runs/DRIFT.md`): **#83** new -- the found person's row reads the new link's time after *Make a new
  link*, where 093 call 16 says it keeps the first link's; stepped round in a step named for the entry (call 136).

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

## Follow-ups

- **keel-web 068 (the Interviews section) -- `contacts_leg.WEB_068_FOLLOW_UP`**: page objects for the Contacts tabs (one
  per kind, the base query's chips and free size), the dataset page (*Show 25* / *Find 25 more*, the picks, *Save and
  get their emails*, the statuses), the *Send more* popup (a kind, Text only, AI interviewer and *Let them choose* shown
  not available, the batch's links and `.csv`) and the Sent register (newest first, format / source / dataset / *Link
  made*, *Make a new link*), each held to the wire this leg already holds -- the leg's steps stay and gain a screen
  each. Waiting for 068's selectors.
- **DRIFT #83** (keel-cloud, a design call on C3).
- **The staging twin**: the leg's Keel's-door half on a real Keel's-AI founder costs a corridor of inference; not run.
- **keel-cloud**: a served view of the fake's counters (or a ledger read) would let the eval drop call 137's indirect
  holds; the AI interviewer (spec 094) will add a hold to CM2 / CM3's subject.
