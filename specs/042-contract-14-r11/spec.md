# Spec 042 -- contract 14, corpus r11, one job per lock

The keel-e2e-eval half of keel-cloud 090 (*the founder names the idea*, D14) and 091 (*the defects batch*: DRIFT #76,
#77, #80, #81; one RESPONDENT_QUESTIONS job per lock; every stem 20 words; the brief's words; contract 14; corpus
revision 11), merged at keel-cloud-docs master `c432c1d` (= `5ae2de2` + 090 + 091). Its inputs are 091's *Follow-ups:
keel-e2e-eval* and 090's, and keel-cloud's `canon/openapi-v2.yaml` at contract 14. Sibling of keel-web master `844ea36`
(065) in its first commit -- keel-web 066 merged at `d03583d` while it was in flight (judgement call 122) -- and of
keel-web master **`c14d513`** (= `844ea36` + 066 + 067: contract 14 vendored, the overview's two tiles, S2's name
counter, the #78 / #79 / #80-web fixes, page two's *Keel's bar* and quote credits) in its **second commit** (FR-012). **No model is called and no money is spent**; the proof is the unit suite over keel-cloud's own corpus tests
and the local stack.

## What moved

- FR-001 **Contract 14 mirrored where this eval reads the wire.** The eval vendors no copy of `openapi-v2.yaml` and
  pins no `CONTRACT_VERSION` (the screen contracts are read from keel-cloud's exporter, which 091 left at the same
  schemas), so what moves is what the journeys read: `LockReceipt.questions.interactionIds` is exactly one (asserted on
  the receipt keel-web received and on `GET /v2/inference-interactions`), `BriefCard.keelBar` (Importance, Current
  solution) is a field the brief's cards are compared on, `BriefReading.quotes[].link` / `words` are checked on every
  served quote, `BriefNotAsked.why` is held to 091's house style, and the B2C Ability to pay card reads *derived from
  cost and price: ...*. Routing stays v11; `InferenceCharge` stays 7; the lock's hold (35, `LOCK_JOBS` 1) is not
  observable on an own-AI founder and is recorded, not asserted (call 119). `retryQuestionnaire`'s nullable
  `interactionId` is not reached (no journey's questions fail) and nothing here reads it.
- FR-002 **Corpus revision 11** (`instructions/corpus.py`, judgement call 110): `REVISION = 11`, revision 10 refused by
  name as v18's, and `check_corpus_r11.py`'s two new L rules restated -- every `asked` face carries *you* / *your*
  (`K3`), Commitment's step no *you* of its own (`S10`). The fixtures (`tests/fixtures/corpus/09-fixture.yaml`,
  `10-fixture-b2b.yaml`) are revision 11 -- their faces already said *you* and their step none, so nothing in `expected`
  moved -- and `check_corpus_r11.py` prints OK for both. The r10 test modules are renamed for r11
  (`tests/test_corpus_r11_shape.py`, `tests/test_instruction_corpus_r11.py`) and hold r11's facts.
- FR-003 **The spoken marks** (`instructions/spoken.py`): `S1` holds every stem to 20 words (`LONG_FRAMES` and the 25
  allowance gone, call 111); `spoken.KNOWN` is empty (call 112) -- the five r10 items are fixed, so none is a fault and
  none is named apart; the ledger's machinery stays and has nothing to fire on.
- FR-004 **An `L` refusal is a rule** (call 113): `validate._reclassified` (call 86) is deleted from `fold_in` and
  `runner.should_redraw`; `validate.vector_rule_letters` reads `ScreenContractTool.VECTOR_RULE` off keel-cloud's source
  and a unit test holds the `L` there.
- FR-005 **`brief_facts` reads 091's words** (`instructions/brief_facts.py`, call 114): `keelBar` on Importance and
  Current solution (absent elsewhere and on a left-out card) and compared on every card; the B2C Ability to pay line;
  `NOT_ASKED_WHY` in the house style.
- FR-006 **`MARKS_VERSION` 18 -> 19** (calls 110-115): no mark born or retired and no number in `marks.toml` moved, but
  four calls moved under them, and the module's own rule is to bump for a moved call; `rescore.py` refuses every bundle
  below 19, v18 by name (call 115). There is no v19 run of record; the certificate (`WHY=marks:19`) is the founder's
  word only and is neither run nor proposed here.
- FR-007 **One RESPONDENT_QUESTIONS job a lock** (`harness/vectors_script.py`, call 116): `respondent_jobs` is part 1 on
  the primary link on either persona; the script answers that one job under the plain screen name on part 1's key set
  (`context_keys_for`: the export's union less `mechanism` and `offer_name`); `RESPONDENT_ALIASES` and the three other
  entries are deleted, so a part 2 or 3 job, were the cloud ever to start one again, matches nothing and fails.
  `leg_lock` no longer waits for three parts: it reads the receipt keel-web got from `POST lock` (`Corridor.
  word_pilot_and_lock` returns it) and asserts one interaction id, that `GET /v2/inference-interactions` lists exactly
  that RESPONDENT_QUESTIONS job and that it is APPLIED, then READY and the lock's lists as before.
- FR-008 **The idea's name (keel-cloud 090)** on every journey (`evals/corpus_scenario.py::_hold_the_idea_name`): the
  served reveal / decision-maker's idea is *Imagine {name}.*, the served Relative advantage question is *On your last
  {occasion}, would {name} have made things better, or not?*, and the screens draw the same card (the reveal's or the
  idea screen's card, the idea card above the Relative advantage item) -- `{name}` the idea's **current** name, the one
  the wire stored after S2 (`IdeaView.shortName`). S2 is held on the wire's new shape: `IdeaView.what` is the name with
  no *Imagine*, `shortName` equals it. **S-006's founder renames the idea** (call 117): *Invoice payout service* typed
  over the what line (`vs.IDEA_NAMES`, a composed input, D-6), stored as *invoice payout service* (`vs.idea_name_of`,
  keel-cloud's `IdeaLines.nameOf` restated), on `GET /idea` and the plan's idea, every translator's reveal and idea
  card and every decision-maker's opening screen *Imagine invoice payout service.*, and the Relative advantage question
  *On your last invoice, would invoice payout service have made things better, or not?*. S-005 and S-007 keep Keel's
  draft name. keel-web `844ea36`'s S2 has no five-word counter (keel-web 066 adds it); nothing here needs one.
- FR-009 **Frequency on Paidly** (revision 11): the founder's *2 to 3 months out of 3* fits `{3, MONTHS}`, so
  `vs.frequency_fits` is true there, the founder answers the Frequency screen, every translator is asked it, and it holds
  up (n 9) -- spec 041's D-1 shrinks to Mulch Run. S-006 asserts it.
- FR-010 **The brief's page objects**: page one is spec 041's (plus 066's pilot tile, FR-012); page two's *Keel's bar:
  ...* (Importance, Current solution) and the quotes credited by `quotes[].words` were asserted on the wire alone in the
  first commit and are held in the DOM since the second (FR-012, keel-web 067).
- FR-012 **keel-web `c14d513` (066 + 067), the second commit.** `stack.toml` names the real keel-web checkout again
  (the archive export is gone). The board holds 066's two tiles (`_board_tiles`): `.tile` the people asked (its `b`
  `people.invited`, *1 person asked* / *n people asked*), then `.tile--pilot` (*k of n · p%* over the per-link line, or
  *None yet* with no `.tile__line` before anyone finishes -- read once right after the invitations, once after the
  readings), and the people line *n people asked · a answered · r read by your AI*; the spec-041 beliefs tile check is
  gone; the brief header's pilot tile has a line exactly when someone finished. S2 holds 066's counter (*n / 5 words*,
  Save off over five: the rename types one word past five first, reads the counter over and Save off, then the name).
  Page two holds 067's *Keel's bar: {keelBar}* (`p.dimrow__said.dimrow__said--keel`) per block, nowhere else and on no
  stage page, and each `.bquote`'s `cite` / `data-link` to `reading.quotes[i].words` / `.link` -- see DRIFT #82 for why
  the bar is never drawn live. #78 and #79 are closed (neither fired) and their steps are guards (call 125).
- FR-011 **DRIFT** (`runs/DRIFT.md`): #76, #77, #80 (keel-cloud's half) and #81 RESOLVED by keel-cloud 091 with the live
  observation; the #80 / #81 steps are now guards that fail the journey if they fire (call 118). Second commit: #78 and
  #79 RESOLVED by keel-web 066 (neither fired on `c14d513`), their steps guards too (call 125); **#82** new -- page two
  never draws Keel's bar live (keel-web 067 prefers the row's `founderSaid`, which keel-cloud always sends), stepped
  round in a step named for the entry (call 126).

## Results

- `make unit`: **1,857 passed / 53 skipped** (before, the same worktree at `a676ea7` against keel-cloud-docs `c432c1d`: 1,729 passed /
  28 failed / 142 skipped -- the 28 the journey's corpus-reading tests on r11 shapes and the 89 extra skips spec 040's
  `CANON_NOT_R10` guard took when the canon moved to r11; spec 041 recorded 1,846 / 53 against `7b151f9`). The 53 left
  are 039's r2-shape skips.
- At zero spend, against `c432c1d` (keel-cloud's `SpokenGuidelinesCorpusTest` and `BriefFactsCorpusTest` re-run with
  `--rerun`, the engine shelled by the compare tests): `compare_correctness` **108 of 108**, `spoken_form` **109 of
  109** (74 composed items + 35 faces, none apart; it was 104 of 104 with 5 apart), `brief_facts` **94 of 94**.
- **Second commit**: `make unit` **1,857 passed / 53 skipped** (the new holds live inside the journeys, so no unit test was added or lost); `make eval K="s005 or s006 or s007"` **3 passed, twice**, against
  keel-cloud-docs `c432c1d` + keel-web **`c14d513`** (392 s and 368 s; bundles `runs/20261014T1457*` to `runs/20261014T1508*`), and a third time (414 s) after a one-name variable rename in `_board_tiles` the unit suite asked for. No model, no money.
- First commit: `COMPOSE_PROJECT_NAME=keel-e2e-eval make up`, then `make eval K="s005 or s006 or s007"`: **3 passed,
  twice**, against keel-cloud-docs `c432c1d` + keel-web `844ea36` (local stack; 398 s and 393 s; bundles `runs/20261014T1407*` and `runs/20261014T1414*`, gitignored). No model, no money.

## Disagreements between corpus r11 and the wire (reported, the corpus not edited)

- D-1 **Frequency on Mulch Run's window** (spec 041's D-1, shrunk): r11 re-expressed 05-paidly's Frequency in months
  out of 3, which fits its window, so Paidly's is asked and holds up; 07-mulchrun keeps *4 to 6 working days out of 7*
  over `{2, WEEKS}` (keel-cloud 091 judgement call 11 left 02 / 04 / 07), so the founder leaves it out and the journey
  asserts LEFT_OUT (its card *you weren't sure, so it was left out*, its `notAsked` row) where the corpus reads
  HOLDING_UP.
- D-2 to D-5, D-7, D-8: spec 041's, unchanged (positional list codes; the cost totals' recorded quarter; Xavier Dubois's
  `rather_not_say` story chip, still r11's, typed as the one chip CANT_RECALL; the persona's role word; Paidly's and Mulch
  Run's hourly rates; Paidly's two mechanism terms padded to three).
- D-6 **Words r11 does not record** (spec 041's, plus one): the idea's three lines, Prevalence's clause and fifths, each
  list's Answer words, the gate's clause, the BRIEF reading -- and **S-006's founder's own name for the idea**
  (*Invoice payout service*, `vs.IDEA_NAMES`): r11 records Keel's short name only.

## Judgement calls

110-115 are the rubric's (`instructions/marks.py`, marked `**v19**`) and are summarised here; 116 on are this spec's
journey calls (91-109 are spec 041's). Each is the simplest reading that keeps `make unit` and the three journeys green
where the inputs are silent, and each can be reversed alone.

110. **Corpus revision 11 only**, r10 refused by name as v18's; r11's K3 / S10 restated in the reader's L half.
111. **`S1` is 20 words on every stem**; the 25-word allowance (call 79) is gone with keel-cloud 091 FR-E.
112. **`spoken.KNOWN` is empty**: the five r10 items are fixed, every unit is counted; the ledger stays, idle.
113. **An `L` refusal is a rule as reported**; call 86's reclassification is deleted, the letter held on the source.
114. **`brief_facts` compares `keelBar`** with the other card fields and reads 091's B2C Ability line and `notAsked`
     words; Buyer and payer's *of the k against* is the reported insight half.
115. **`rescore.py` refuses every bundle below 19**, v18 by name. *Why 19 and not v18 amended in place:* the module's own
     rule bumps for any moved call, and four moved; v18 had no run of record, so nothing is stranded -- but the
     founder's certificate is now `WHY=marks:19`. Reversing it is the constant, `OLDEST` and the v18 refusal branch.
116. **The script answers one RESPONDENT_QUESTIONS job, on part 1's key set, under the plain screen name.** No alias for
     parts 2 / 3 is kept "just in case": an unexpected job matching nothing fails at the questions, where the receipt
     step already says what was expected.
117. **One journey renames the idea, and it is S-006** (05-paidly): it is the entry where the name reaches both idea
     cards -- the translators' reveal and every decision-maker's opening screen -- as well as the Relative advantage
     question. The name, *Invoice payout service*, is three words with no claim word (L3) and no product word, and is
     lower-cased by 090's sentence-case rule, so the step also proves the name is read the way keel-cloud derives it.
     S-005 and S-007 keep Keel's draft (090 FR-006: the draft's name is the short name byte for byte).
118. **#80 and #81's workarounds became failing guards, not silent deletions.** A 409 after a redraft still gets the page
     object's second press (so the bundle shows what followed) and then fails `leg_calibrate` in a step named *DRIFT #80
     came back*; a FAILED questions state fails `leg_lock` at once (no re-read), naming #81. Neither fired on any journey
     of this spec.
119. **The lock's one job is asserted on what the founder's page received and on the job list, not on credits.** The
     journeys' founder is on their own AI (the scripted runtime), whose lock holds no credits, so `required` 35 and the
     one hold are keel-cloud's (`CreditPolicy`, `CreditPolicyTest`) and S-012's Keel door's to see; here they are
     recorded in this spec and never asserted.
120. **`quotes[].link` / `words` are checked on every served quote, which on a scripted journey is none.** The referee's
     BRIEF reading quotes nobody: a quote carries an `invitationId`, which a script written before any invitation exists
     cannot know. The check is real on S-012 (a host's model may quote) and vacuous here, and the step says so; the
     scripted journeys assert `quotes == []`.
121. **`notAsked` is held on the wire to the eval's reading of the entry** (`expected_not_asked`, D-1's Frequency read
     as left out), in 091's words.
122. **The journeys ran keel-web `844ea36`, the web this spec was given, from a `git archive` export** with an APFS clone
     of the checkout's `node_modules` (package files identical), because keel-web master moved to `d03583d` (066) while
     this spec was in flight; the sibling checkout was not touched. The bundles' `versions.json` records the export's
     path (no `.git`, so no commit is read there); `844ea36` is stated here. One S-005 attempt ran on `d03583d` by
     accident before the export and stopped at the lock on this spec's own key-name slip (`interaction_id`, fixed);
     the calibrations before it passed with neither #78's nor #79's step firing.
123. **`IdeaView.what` is held to be the name with no *Imagine*** (`vs.idea_view`: the draft's name), and
     `IdeaView.shortName` to equal it after Save -- untouched or renamed.
124. **066's tiles are read twice**: once right after the invitations (nobody finished: *None yet*, no line, the people
     tile already the invited count) and once after the readings, both held to `StandingsView.people` / `.pilot`. The
     counter's word count is the drawn line's words split on spaces, as keel-web's `wordCount` reads a name.
125. **#78's and #79's workarounds became failing guards**, as #80's and #81's (call 118): the S2 page object still
     reloads once on empty lines and `leg_calibrate` still collects a lower-case head, and each then fails the journey
     in a step named *DRIFT #n came back*. Neither fired on `c14d513`.
126. **DRIFT #82 is stepped round, not failed**: the wire is held (`keelBar` on exactly Importance and Current solution),
     the bar slot is held to what keel-web's rule draws where the row also carries `founderSaid` (the founder's words),
     and the step is named for the entry. Failing the journey on it would hide every later assertion behind a design
     question (which bar wins) that is neither the eval's nor settled.
127. **The quotes on page two are held to the wire, which on the scripted journeys is none.** The scripted executor
     loads one fixed BRIEF result before any invitation exists (it fills `invitationId` only on INTERPRET), so the
     referee's reading cannot quote anybody (call 120): `.bquote` count, `cite` words and `data-link` are compared to
     `reading.quotes` -- zero and zero here, real on S-012. A keel-runtime change (filling a quote's `invitationId` from
     the BRIEF context's `stories`) would make it real here; not this repository's to make.
128. **The S2 over-five probe** appends words to the founder's name (*Invoice payout service for every single*, six) and
     reads the counter *6 / 5 words*, `calib__wc--over` and Save disabled before typing the name back; only on the
     journey that renames (S-006), so the other two journeys' S2 stays an untouched approval.

## Follow-ups

- **DRIFT #82** (keel-web and keel-cloud, a design call): which bar page two shows on Importance and Current solution.
  When it is settled the #82 step stops firing and page two is held to *Keel's bar: {keelBar}*.
- **Page two's quotes on a scripted journey** need a keel-runtime change (call 127); `notAsked.why` is held on the wire,
  and on page two only through the block rows spec 041 already compares.
- **#80's web half** (066's StaleBanner) is on master but unexercised: no write is refused any more.
- **The instruction eval's RESPONDENT cases for parts 2 and 3** are kept: the screen still takes a part 2 / 3 result
  (for a job in flight at deploy) and the golden payload is part 2's, but the cloud no longer starts those jobs, so
  their cases measure an instruction no lock asks for. Dropping them moves the respondent denominators -- a marks
  decision for the founder before `WHY=marks:19` is spent.
- **S-012 (live)**: a host's model may draft an idea line over five words, which 090's `L5` refuses on S2's untouched
  approval (090 judgement call 7) -- S-012's `leg_interpret_solution` would then need the founder to shorten it.
- **keel-cloud**: 02 / 04 / 07's Frequency units (091 call 11; D-1); the corpus's submission dates (091 call 12).
- **The remote run against the staging twin** (not run here): as spec 041's, against a twin at keel-cloud-docs `c432c1d`
  (or later) and keel-web `844ea36`.
