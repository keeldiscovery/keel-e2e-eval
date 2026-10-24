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

- [x] T001 `harness/interviewer_fake.py`: `WORTH_MORE` and `price_said_back(question, band)` -- 130 FR-7's
  `FollowUpComposer.priceSaidBack`: *You put it below €3,000.* where the served stem shows a price (the first currency
  figure in it), *You put it at {band}.* where a band was picked, *You put it low.* otherwise, each with *What would
  make it worth more?*. The registry's `follow_up` text and spoken (the `LADDER` copy) are unchanged (130 judgement call
  6), so IM27's pre-rendered FOLLOW_UP clips keep the registry's words.
- [x] T002 `harness/vectors_script.follow_up_question`: Price's follow-up composed whole (`WHOLE_TEXT`), so its text and
  spoken line are one wording on every journey -- the golden seven show no price in the stem, so their text stays
  *You put it at {band}. ...* and their spoken line moves from the registry's *You put it below what we asked. ...* to
  the text; the would-not-pay sentence still comes first (126 FR-6a); the chain's two codes say back the up-front pick.
- [x] T003 `vs.gerund`, `vs.adoption_statement(asked, name)` (130 FR-11, `ItemFrames.adoptionFriction(asked, name)` over
  `SpokenCap.plain`): *{Name} means {step's gerund}. Would you do that, or not?* where the name is known and the frame
  fits 20 words, else the statement as before; `vs.commitment_stem(step, name, card)` (130 FR-10): a step naming *the*
  trial / pilot / walkthrough / demo / session / onboarding or setup call / test run / course / programme that the card
  does not name opens on *{Name} starts with {a thing}.* before the plain stem, or before *Would you {step}, or not?*
  where the opener would pass 20, else the plain stem.
- [x] T004 the gate's event (130 FR-6): `vs.own_subject_event(asked)` (`ownSubjectEvent`, *did a booking call come in on
  your shift* -> *a booking call come in on your shift*, the person's own time kept) and
  `vs.without_negative_clause(circumstance)` (the circumstance cut before *, and not ...*); the brief's line said of
  them, `brief_facts.gate_clause_of_them(gate, window)` (`servedGateClause`'s new branch: a gate whose clause names its
  own subject reads *had {clause}*, *your* as *their*; None where code says a *you* clause in its own past tense, which
  the harness does not mirror).
- [x] T005 Frequency's line in the window's unit (130 FR-2): `brief_facts.frequency_line(clause, window)` and
  `brief_facts.card(clause=...)` read *the middle answer · {unit plural} they {clause}* -- 05-paidly's *months they
  waited ...* on the golden walk (the 068 test pinned *days*); the corpus's reading (no gate) unchanged.
- [x] T006 X12 (130 FR-8): `vs.condition_from(part)` / `vs.drawn_condition(which_people, segment)` -- *not starting
  from zero* -> *are past the beginner stage*, *with no X* -> *have no X*, a size, a tool or bank, a level.
- [x] T007 the reads: on a back-test `backtest.changed_screens` gains `cloud_130` -- the served Adoption and Commitment
  stems beside the mirror's (the plan's tested face and step, the served idea name and reveal), the served gate when it
  asks the job (*did you turn every guest who calls into a booking?*), the brief's Prevalence and Frequency lines beside
  the served gate's (and Frequency's unit), each a finding where they differ, never a stop; the walk's
  served-no-chip finding names the condition X12 would draw. `instructions/spoken.py` S10 reads *Would you* as it reads
  *would you* (an introduced step past 20 words opens its question with a capital). Unit: `tests/test_after_130.py`.
  The 068 pin of Frequency's *days* on Paidly (`test_revision_16_walk`) reads *months*. Unit: **3,158 passed, 53
  skipped, 0 failed**; the grep clean.

## FR-2 -- contract 37

- [x] T010 the Check screen's draft as `GET calibration/{vector}` serves it (`corpus_scenario._keep_draft`): an item's
  optional `replaces` (contract 37, `SavedList.items[].replaces`, a draft's only) is read and recorded
  (`j.changed["replaced"]`: the dimension, the drafted label, the founder's words), and on a back-test named as a
  finding; never asserted, and never looked for on Save (it is dropped there by the cloud). Nothing in this repository
  names the contract version as a number to bump (068 T010's search, repeated: the `CONTRACT_VERSION` lines in
  `instructions/marks.py` / `marks.toml` are history), so none moved. `j.feedback`'s lists (FM1 / FM2's record) are
  left as they were. Unit: `tests/test_after_130.py`; **3,159 passed, 53 skipped, 0 failed**; the grep clean.

## FR-3 -- the lock-time notes

- [x] T020 `backtest.lock_notes(j)`: the project's interactions (`GET /v2/inference-interactions?project_id=`) read
  once at the transcript -- each row's `detail`, `founderNote`, `diagnostic` and its turns' `content` -- for 130's new
  notes by name: `S13` (a saved row over its screen's cap, at the lock), `L21` (a drafted condition in place of the
  founder's own), `M5` (a trade word or a design note in the reveal); each found once, a finding naming the rule, the
  screen and the words; recorded in `backtest.json` (`lock_notes`) and `backtest.md`. X12's note is read beside them
  (FR-1's draw, named). Each note is also a finding (`j.findings`, read before the transcript lists them). Unit: stub
  interactions (`tests/test_after_130.py`); **3,160 passed, 53 skipped, 0 failed**; the grep clean.

## FR-4 -- nothing else moves

- [x] T030 REVISION stays 16 (`instructions/corpus.py`), `MARKS_VERSION` 20 stands, the golden seven's numbers and
  marks unchanged (the unit tests that hold them pass unmoved); no fixture, corpus or registry edit
  (`git diff --stat 14a0c0e` names none). Unit: **3,160 passed, 53 skipped, 0 failed**; the grep clean.

## Judgement calls

1. **What the harness composes, and what it reads beside the wire.** The golden walk holds every served stem to the
   wire (`_hold_the_screens`), never to a composition of its own, except the follow-up (`_hold_the_follow_up`, strict).
   So Price's follow-up is composed (T002) and held as before, while the named Adoption statement, the introduced
   Commitment step, the gate's event and the brief's gate line are mirrored as functions and read beside the wire on a
   back-test as findings (`backtest.cloud_130`), never asserted on a golden walk: the mirrors are narrower than the
   Java (below), and a narrower mirror must not turn S-005 / S-006 / S-007 red on words the cloud has right.
2. **Price's follow-up and the registry.** 130 composes Price's follow-up whole and leaves the registry's `follow_up`
   words alone (its judgement call 6), so the per-person route's text and spoken line are `price_said_back`, while the
   pre-rendered FOLLOW_UP clip a rung carries (IM27, the `LADDER` copy) keeps *You put it below what we asked.* On the
   golden seven no stem shows a price: their text is unchanged (*You put it at {band}. ...*), their spoken line moves
   to the text.
3. **The narrow mirrors.** `gerund` and `adoption_statement` mirror `SpokenCap.gerund` and the 20-word cap, not
   `StrangerGrammar.wouldDo` nor the grammar check (the fallback statement is read off the wire, `None` here);
   `own_subject_event` reads a subject as a determiner and a noun (*a booking call come in ...*), not `subjectLed`'s
   present-verb list; `condition_from` mirrors every branch but the last (a part opening on a present verb), and
   `drawn_condition` tries a negative qualifier first where the cloud asks `FounderWords.dropped` which one the read-back
   lost. Each is unit-tested on 130's own sentences.
4. **The brief's gate line, read off the gate's own frame.** `gate_clause_of_them` tells the gate's two shapes apart by
   the frame code wrote (*did you ...* / *did your ...* for the person's clause, *did {clause}* only for one with its
   own subject), so no verb list is needed; the person's clause in its own past tense (`saidOfThem`) is not mirrored,
   and the golden card keeps the journey's scripted clause (`event_past`) as 068 did.
5. **S10 reads *Would you*.** The introduced step opens its question *Would you {step}, or not?* where the opener would
   pass 20 words; the guard read only a lower-case *would you* and would have skipped the check. No golden record moves
   (the corpus composer knows no card, 130 T018).
6. **The notes on the wire.** An interaction row's `detail` carries the first note of a row applied over a word rule
   (`Noted.note()`), so a second note on the same row (an L21 behind an L2 cut) is not on the wire; repair turns' `content`
   is read too. X12 is read beside the three the spec names, since FR-1's draw is 130's and the finding names it.
7. **`replaces` on the golden walk.** Recorded, never a finding there: the scripted draft is the entry's own list, so a
   replaced row on a golden walk would be the cloud's L21 meeting the corpus, a reading for the parent, not a stop.

## Left open

- **S-005, S-006, S-007 not run here** (the stack is the parent's while the host-door re-runs go on; acceptance 2).
  Expected to move on the 130 build: an owed Price follow-up's spoken line (= its text), Paidly's Frequency card
  (*months they waited ...*), the served Adoption statement named (held to the wire, no harness words); S-005 should
  now pass L16 on Countly's condition (130 FR-1), keel-runtime's scripted executor still having no repair screen.
- keel-web's drawing of a replaced row (struck through, or a note) is keel-web's to build (130's *Owed*); the walk reads
  the wire's `replaces`, not the screen.
- 130's own open items (FR-3, FR-4, T023: one revision 17) move nothing here; REVISION stays 16.
