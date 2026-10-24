# Tasks 069 -- The harness after keel-cloud 130 (contract 37)

Branch `069-after-130` off master `14a0c0e` (worktree `wt/eval-069`). The cloud half is keel-cloud-docs master
`48502f95` (spec 130, contract 37 in `canon/openapi-v2.yaml`, corpus still r16, no registry change), read only: its
`specs/130-after-the-129-re-runs/tasks.md` (the served words and judgement calls, and *Owed: keel-e2e-eval*), and the Java
the harness mirrors -- `FollowUpComposer.priceSaidBack`, `ItemFrames.adoptionFriction(asked, name)` /
`commitment(step, name, card)`, `SpokenCap.plain` / `gerund`, `RespondentQuestionsRules.heldEvent` / `ownSubjectEvent` /
`withoutNegativeClause`, `ScreenResultApplier.conditionFrom` / `drawnCondition` (X12), `BriefFacts.servedGateClause` /
`frequencyLine`. One commit per section below, in this order, each gated on `.venv/bin/python -m pytest tests -q` and a
case-insensitive grep of its output for `failed` / `error`. No `make backtest`, no live model, no stack: the golden
journeys (S-005, S-006, S-007) and the host-door re-runs are the parent's (one stack on this machine, in use).

Unit suite on `14a0c0e` before any change: **3,149 passed, 53 skipped, 0 failed, 0 errors** (199 s); the grep clean.

## FR-1 -- the follow-up mirror follows 130

- [ ] T001 `harness/interviewer_fake.py`: `WORTH_MORE` and `price_said_back(question, band)` -- 130 FR-7's
  `FollowUpComposer.priceSaidBack`: *You put it below €3,000.* where the served stem shows a price (the first currency
  figure in it), *You put it at {band}.* where a band was picked, *You put it low.* otherwise, each with *What would
  make it worth more?*. The registry's `follow_up` text and spoken (the `LADDER` copy) are unchanged (130 judgement call
  6), so IM27's pre-rendered FOLLOW_UP clips keep the registry's words.
- [ ] T002 `harness/vectors_script.follow_up_question`: Price's follow-up composed whole (`WHOLE_TEXT`), so its text and
  spoken line are one wording on every journey -- the golden seven show no price in the stem, so their text stays
  *You put it at {band}. ...* and their spoken line moves from the registry's *You put it below what we asked. ...* to
  the text; the would-not-pay sentence still comes first (126 FR-6a); the chain's two codes say back the up-front pick.
- [ ] T003 `vs.gerund`, `vs.adoption_statement(asked, name)` (130 FR-11, `ItemFrames.adoptionFriction(asked, name)` over
  `SpokenCap.plain`): *{Name} means {step's gerund}. Would you do that, or not?* where the name is known and the frame
  fits 20 words, else the statement as before; `vs.commitment_stem(step, name, card)` (130 FR-10): a step naming *the*
  trial / pilot / walkthrough / demo / session / onboarding or setup call / test run / course / programme that the card
  does not name opens on *{Name} starts with {a thing}.* before the plain stem, or before *Would you {step}, or not?*
  where the opener would pass 20, else the plain stem.
- [ ] T004 the gate's event (130 FR-6): `vs.own_subject_event(asked)` (`ownSubjectEvent`, *did a booking call come in on
  your shift* -> *a booking call come in on your shift*, the person's own time kept) and
  `vs.without_negative_clause(circumstance)` (the circumstance cut before *, and not ...*); the brief's line said of
  them, `brief_facts.gate_clause_of_them(gate, window)` (`servedGateClause`'s new branch: a gate whose clause names its
  own subject reads *had {clause}*, *your* as *their*; None where code says a *you* clause in its own past tense, which
  the harness does not mirror).
- [ ] T005 Frequency's line in the window's unit (130 FR-2): `brief_facts.frequency_line(clause, window)` and
  `brief_facts.card(clause=...)` read *the middle answer · {unit plural} they {clause}* -- 05-paidly's *months they
  waited ...* on the golden walk (the 068 test pinned *days*); the corpus's reading (no gate) unchanged.
- [ ] T006 X12 (130 FR-8): `vs.condition_from(part)` / `vs.drawn_condition(which_people, segment)` -- *not starting
  from zero* -> *are past the beginner stage*, *with no X* -> *have no X*, a size, a tool or bank, a level.
- [ ] T007 the reads: on a back-test `backtest.changed_screens` gains `cloud_130` -- the served Adoption and Commitment
  stems beside the mirror's (the plan's tested face and step, the served idea name and reveal), the served gate when it
  asks the job (*did you turn every guest who calls into a booking?*), the brief's Prevalence and Frequency lines beside
  the served gate's (and Frequency's unit), each a finding where they differ, never a stop; the walk's
  served-no-chip finding names the condition X12 would draw. `instructions/spoken.py` S10 reads *Would you* as it reads
  *would you* (an introduced step past 20 words opens its question with a capital). Unit: `tests/test_after_130.py`.

## FR-2 -- contract 37

- [ ] T010 the Check screen's draft as `GET calibration/{vector}` serves it (`corpus_scenario._keep_draft`): an item's
  optional `replaces` (contract 37, `SavedList.items[].replaces`, a draft's only) is read and recorded
  (`j.changed["replaced"]`: the dimension, the drafted label, the founder's words), and on a back-test named as a
  finding; never asserted, and never looked for on Save (it is dropped there by the cloud). Nothing in this repository
  names the contract version as a number to bump (068 T010's search, repeated: the `CONTRACT_VERSION` lines in
  `instructions/marks.py` / `marks.toml` are history), so none moved.

## FR-3 -- the lock-time notes

- [ ] T020 `backtest.lock_notes(j)`: the project's interactions (`GET /v2/inference-interactions?project_id=`) read
  once at the transcript -- each row's `detail`, `founderNote`, `diagnostic` and its turns' `content` -- for 130's new
  notes by name: `S13` (a saved row over its screen's cap, at the lock), `L21` (a drafted condition in place of the
  founder's own), `M5` (a trade word or a design note in the reveal); each found once, a finding naming the rule, the
  screen and the words; recorded in `backtest.json` (`lock_notes`) and `backtest.md`. X12's note is read beside them
  (FR-1's draw, named). Unit: stub interactions.

## FR-4 -- nothing else moves

- [ ] T030 REVISION stays 16 (`instructions/corpus.py`), `MARKS_VERSION` 20 stands, the golden seven's numbers and
  marks unchanged (the unit tests that hold them pass unmoved); no fixture, corpus or registry edit.

## Judgement calls

## Left open
