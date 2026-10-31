"""The rubric this eval judges by, versioned (spec 009 FR-014).

`MARKS_VERSION` is to this eval what `POLICY_VERSION` is to `evals/policy.py`, and deliberately a
separate constant: an instruction-eval rubric change must never look like a scenario-scoring one.
**Bump it for any change to a mark, a metric definition, an alignment rule, the field list, or a
judgement call below** -- scores under different versions describe different rubrics and are not
comparable.

**`MARKS_VERSION` 9** (spec 029, 2026-10-07): the subjects are the eight screens of the vector
redesign, `golden_belief_recall` and `align.py` are retired, four marks are born and every one is
measured by code against the registry keel-cloud exports, and the corpus is read at revision 3.
Calls 28-36 are `specs/029-marks-v9-vectors/contracts/marks-v9.md` §3's, verbatim; calls 1-27 are
byte for byte what `master` `0165017` carried (`tests/fixtures/marks/calls-1-27.at-0165017.txt`).

**`MARKS_VERSION` 10** (spec 030, 2026-10-09): the ruler follows keel-cloud 071's registry to
twelve dimensions (4 / 3 / 5, nine deal-breakers, the `b2b_only` pair) and its corpus to revision 4.
Calls 46-49 below. Every denominator a scorer reports is read off the registry and the entry's
persona, never typed; `no_claim_words` retires with `BAR_SET` and `NOT_TESTED_BY_DESIGN`; the corpus
is read from keel-cloud's canon and nowhere else; and `rescore.py` refuses every v8 and v9 bundle
by name. v10 has no run of record; it is history from v11.

**`MARKS_VERSION` 24** (spec 112, 2026-10-30): `option_validity` reads keel-cloud 171's Adoption friction (call 129):
`K2` measures a face in *To use it, you'd {step}. Would you do that, or not?* (three words more than 123's *You'd*), `L5`
admits one suggested Adoption friction step with its `suggested_why` (a missing why a fault), `L1` counts the founder's
efforts beside it. The reading moved both ways, so the version moves; no number in `[marks]` moved, the corpus stays
**revision 19** (five of its seven golden Adoption friction faces, written to 163's 12 words, are now `K2`s:
`spoken_form` reads 104 of 109 at zero spend), and a v20 to v23 bundle re-scores at v24 (call 130). **There is no v24
run of record until `WHY=marks:24` is spent -- the founder's word only.** v23's paragraph below is history.

**`MARKS_VERSION` 23** (spec 091, 2026-10-30): a drafted list is held to the draft's rule, not the save's (call 127).
`option_validity`'s `L1` counts Importance's draft (`rival_list`) as `founder-lists.md` asks it written: with the job's
`answers` `{}` the problem itself alone (one item), with the founder's Answer the problem itself and the N difficulties
the Answer names (1 + N, at most `saves.max_items`). `saves.min_items` (2 on the registry of record) is the rule at
Save, once the founder has named the others (keel-cloud 087 / 152), and is read only where a saved list is checked
(`corpus._check_list`), never against a draft. The reading moved both ways (a correct one-item draft passes; a rival
Keel adds with no Answer fails), so the version moves; no number in `[marks]` moved, the corpus stays **revision 19**,
and a v20, v21 or v22 bundle re-scores at v23 (call 128). **There is no v23 run of record until `WHY=marks:23` is spent
-- the founder's word only.** v22's paragraph below is history.

**`MARKS_VERSION` 22** (spec 093, 2026-10-30): `option_validity`'s two list rules say keel-cloud's (calls 124-125),
and an Adoption friction face is framed and judged as keel-cloud frames it (call 126: `K2` counts `ItemFrames`' frame,
`K3` reads the framed line).
`L1` is 161's -- a blank phrase is *the phrase today's way is asked by, the act in the people's words ('checking for
errors')*, and a drafted phrase that opens on *your way of* faults (*write the act alone, in the people's words*); `L5`
admits one `suggested` item on Purchase friction **and Compatibility** (keel-cloud 121 FR-3, contract 31), never
elsewhere -- the harness's *Purchase friction only* was a stale restatement. The reading moved both ways (a Lullaby
Compatibility draft with its one suggested condition passes; a draft in Keel's old words fails), so the version
moves; no number in `[marks]` moved, the corpus stays **revision 19**, and a v20 or v21 bundle re-scores at v22 (its
drafts are in the bundle). **There is no v22 run of record until `WHY=marks:22` is spent -- the founder's word only.**
v21's paragraph below is history.

**`MARKS_VERSION` 21** (spec 078, 2026-10-28): the question-quality readers' **`read`** joins the rubric as a mark kind
beside `no_leak` (calls 121-123). It is scored from a **committed score file** (`quality/scores/<entry>/`, written by
`make read-screens` against `quality/RUBRIC.md` at `RUBRIC_VERSION`), never from a run: the scorecard shows, per
entry, the five means, the flagged count, `score_pct` and the reader when a score file at the current rubric version
exists, and *not measured* otherwise (the dry run's rule). It is **reported, never gating**: no row of `judge()` moves,
no number in `[marks]` moves, and an instruction-eval run passes or fails exactly as at v20. The corpus stays
**revision 16**. **There is no v21 run of record until `WHY=marks:21` is spent -- the certificate is the founder's word
only; never run or propose it.** v20's paragraph below is history (v20 never had a run of record).

**`MARKS_VERSION` 20** (spec 052, 2026-10-17): the report replaces the brief. The ruler follows keel-cloud 104
(keel-cloud-docs `9a033fe`; contract 19, the standings side; `InferenceCharge.VERSION` 10, document 25): the BRIEF
screen, `brief.md`, `BriefReading` and `StandingsView.brief` are deleted, and with them **the seven reading marks and
`brief_answers` retire** (`instructions/brief.py`, the `BRIEF` case kind, `tests/test_instruction_brief_reading.py`;
call 116) -- a subject the product no longer has is not marked. `brief_facts` **stays** (the card lines are the one
source, design §3) and gains the project's second number, `priceMedian` -- the highest price-table edge at least half
of `n` chose at or above, `{edgeSaid, chose, n}` or absent -- one more check an entry, and reads 103's two moved card
lines: Compatibility *said {condition}* (no *said yes:*), Purchase friction counting the supporters, *did not need
{step}, or it was quick* (call 119). One deterministic mark is born at zero spend, **`report_overview`**: the Overview
a founder reads -- the verdict and its line, the two tiles, the three panels' pills, lead lines and rows, the foot --
drawn from keel-cloud's facts (`BriefFactsCorpusTest`) against the same Overview drawn from this repository's reading
of the corpus (`instructions/overview.py`; call 117). Four more report marks are born as **journey** marks, measured
on the stack and never rows of `judge()`: `report_insights`, `report_no_repeat` (design D6), `report_pilot` and
`report_binding` (D10), in `evals/report_marks.py` (`REPORT_MARKS_VERSION` 1); the journeys also measure
`report_overview` against the page (call 120). The corpus stays **revision 11**: no screen schema the model writes
moved. `rescore.py` refuses every bundle below 20 (call 118). **There is no v20 run of record until `WHY=marks:20` is
spent -- the certificate is the founder's word only; never run or propose it.** v19's paragraph below is history (v19
never had a run of record).

**Spec 051 (2026-10-17)**: keel-cloud 103 (contract 19, the interview side, keel-cloud-docs `4cda99a`) moved no screen
schema and no instruction -- the follow-up's ladder is registry data and code composes its words -- so v19 stood; the
journey ruler moved instead (`INTERVIEWER_MARKS_VERSION` 5). 052 took the standings side and this version's bump (v20 above).

**Spec 053 (2026-10-17)**: keel-cloud 105 (corpus **revision 12**, keel-cloud-docs `7e64f20`) moved no screen schema,
no instruction and no golden number -- the six GB entries are US entries in dollars, the same digits, `$` and `USD`,
a few words in the US register (*"the currency amount should be dollars, because we are primarily targeting US
markets"*, the founder) -- so v20 stands and reads **revision 12**, refusing a revision-11 file by name as v19's and
v20's, in pounds; v20's *the corpus stays revision 11* above is history, and so is every numbered call's figure in
pounds (calls 42, 57, 64, 65: each records its rule with the figure of its day, and the rule -- the symbol from the
currency -- did not move). v20 has no run of record, so no r11 bundle waits to be re-scored. The seven revision-12
files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `7e64f20`, equal to
`src/test/resources/keel/corpus-r12/`): `01-countly.yaml` `8de12220f62ac40f05cab2d4bfa041a3291b4abb7427ee467e33a605a7651dbc`; `02-compliancelog.yaml` `af94938d25394012fdd32d3ee6ba3a09f844c89755004d5ec01a2bab6bc3aeaa`; `03-lullaby.yaml`
`632afc3450c76af381e91658cbcb58ac275cbca32a9699f7facf80892f07206e`; `04-linerly.yaml` `f962a7890d59a9a84eda03b552221bf440890e2d3e0288266f7131769c3172d3`; `05-paidly.yaml` `152febaa431191157f04deb3ad72b10ff875c4e609ce4a409d330c6d29264f09`; `06-repeatline.yaml` `5922698ce8551de475258fa0e9a8b7ee0944d47727fe1845dad30c5ffb289a28`; `07-mulchrun.yaml`
`f62b28077eca972ccba275ca8c99fc0d821bffaa834c589e91b37bbdd1e55591`. `DRY=1`-measurable at `7e64f20`:
`brief_facts` 101 of 101 (05-paidly *$50 a month or more · 5 of 8*), `report_overview` 49 of 49,
`compare_correctness` 108 of 108, `spoken_form` 109 of 109.

**Spec 057 (2026-10-20)**: keel-web 086 / keel-cloud 109 (contract 22, keel-cloud-docs `7b3cd84`) moved no screen
schema, no instruction and no corpus file -- the teaching videos are clips and flags -- so v20 stands. The seven new
rows are the journey ruler's (`evals/guide_marks.py`, `GUIDE_MARKS_VERSION` 2, its own changelog in that file), each
with its design id (design §15): G6 the report sheet once (D44), G7 the Overview's two pills (D45), G8 two chapters on
a stage band (D43, D46), G9 the money pair by kind (D47), G10 an explainer under every question (D27), G11 the openers
once per stage (D25), G12 no project word in a caption or snippet (D42, D48); a mark whose clips are absent from the
served manifest passes as not applicable.

**Spec 058 (2026-10-20)**: keel-cloud 110 / keel-web 087 (contract 23, keel-cloud-docs `b54c349`) moved no screen
schema, no instruction and no corpus file -- the four interviewers (LIVIA preselected where JUDY was, JIA, MARIEKE,
CHUKWU) are faces and clips -- so v20 stands. The two new rows are the journey ruler's (`evals/interviewer_marks.py`,
`INTERVIEWER_MARKS_VERSION` 6, its own changelog in that file): IM28 *tap to hear* (a tap on an unpicked card picks it
and her hello plays inside the card to its end, 8 s or less, the still returns, the picked face is posted) and IM29 *the
respondent hears her* (*Hear <name>* on the Let-them-choose intro plays her hello, the choice buttons enabled
throughout).

**Spec 059 (2026-10-20)**: keel-web 088 / keel-cloud 111 (contract 24, keel-cloud-docs `096cecc`) moved no screen
schema, no instruction and no corpus file -- Interviews › Sent reworked is a page, a sheet and a flag -- so **v20
stands** (spec 059 judgement call 3: the spec's FR-5 names `MARKS_VERSION` 21, but this file's rule bumps it only for a
change to this rubric, and 057 / 058 kept v20 on the same ground; a bump would leave v20 with no run of record for a
ruler that did not move). The new rows are the journey rulers' (each with its own changelog in its file):
`evals/guide_marks.py` **`GUIDE_MARKS_VERSION` 3** -- G13 the Interviews sheet once (D44), G14 Sent's two-chapter pill in
place and Contacts' one clip (D43, D46), G15 Sent's order with no *How it works* (D43; 088 FR-1), G16 the links table:
search, the *Made* sort, the range and Next, the csv in the search row (088 FR-4), G17 the role counts (088 FR-3); G12
reads the three page clips with the rest (29 in the manifest) -- and `evals/interviewer_marks.py`
**`INTERVIEWER_MARKS_VERSION` 7** -- IM30 *the band's Hear <name>* (on Sent after the recording, `persona-hear` plays
her hello in the who-asks band to its end, the still returns; absent for a retired face); the interviewer leg's W1
replay reading retires with *How it works* (it was a leg step, never a row).

**Revision 19 read through keel-cloud 174 (2026-10-31; eval 115, the harness half)**: no corpus revision, no mark
moved. The engine writes four belief rows in 174's words -- Commitment where someone else decides *In most cases
{decider} would {value} now.*, Importance *{actor_plural} have {list_size} things that are hard {stretch}. {value} is one
of the two they would most like made easier.*, Compatibility *For most {actor_plural}, {value}.*, Purchase friction
*{value} can slow or stop the purchase.* -- and Purchase friction's escape is `cant_tell`; revision 19 keeps the words
and the code before it (the templates quoted below as revision 18's), and the reader reads them through one rule each
(`corpus.spec174_reads`, keel-cloud's `VectorCorpusFixture.spec174Reads`; `corpus.spec174_escape`). **v24 stands**: no
mark scores a belief sentence, and `spoken_form` reads the escape the registry names.

**Revision 19 read through keel-cloud 173 (2026-10-30; eval 113, the harness half)**: no corpus revision, no mark
moved. The engine's Relative advantage belief is *For most, their last {occasion} would have gone better with it:
{value}.* (the first benefit whole; *the last time* with no noun), its drift clause *you said it would have gone better:
{founder} · ...*; revision 19 keeps 152's *For most, it would have given them ... on their last ...* (quoted below as
revision 18's), and a journey compares the wire with it read through one rule (`corpus.spec173_reads`, keel-cloud's
`VectorCorpusFixture.spec173Reads`). **v24 stands**: no mark scores a belief sentence.

**Corpus revision 19 (2026-10-30, keel-cloud 159; eval 089, the harness half)**: Relative advantage is one scale --
the stranger answers *A lot better · A little better · No difference · Worse* (`scale_four`, *I can't tell* apart),
every recorded answer moved by one rule (positive with a benefit ticked a lot better, positive with none a little
better, neutral no difference, negative worse), the row read by `fixed_last_two_against` and recording the engine's
`optionCounts` on the four; no standing, drift, inside, n or verdict moved. The reader reads **revision 19** and refuses a
revision-18 file by name. **v21 stands**: no mark reads the Relative advantage pick's shape or its benefits
(`compare_correctness` reports `optionCounts` beside the counts, never marks them), so the ruler did not move, the record
did. The seven revision-19 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `1cf2ebc3`, unchanged
through `ad5f6441`, equal to `src/test/resources/keel/corpus-r19/`): `01-countly.yaml`
`431a56d23be2de5cf84da10007802aa87daceb75bb0a9b4c57afa0461da273b3`; `02-compliancelog.yaml`
`5d2152bf7b0f5a5def830c79907f5e139761a48d3ff121f1a56eb55d6064e16f`; `03-lullaby.yaml`
`d96220665201746e05d4b4794eea03bb0887e4d6d6dc0aed4a5db6daa50e4c08`; `04-linerly.yaml`
`27a22794db252cd39113498cb48e115a3c1c3200b429ee416bbaa4eb572d434e`; `05-paidly.yaml`
`91a37d92128f927516bfaf09ea64cb3a02d0d5fbde25c9637aee835126693ba5`; `06-repeatline.yaml`
`c971a78f4ea8be5c2ac1eab6d790576bae7a06f9e188bc3af74e7bb0bd0a44f6`; `07-mulchrun.yaml`
`735476c9c828e0ced83695518771499ac298f8dc864c4e1ac2f500418c046e02`.

**Corpus revision 18 (2026-10-29, keel-cloud 152; eval 086, the harness half)**: the belief words move, no standing --
seven templates and the prevalence phrases in the founder's words (Commitment *Most {actor_plural} would {value} now.*,
Current solution *... still falls short.*, Importance *Of these {list_size}, ...*, Prevalence *under 2 in 10 ... at
least 8 in 10*, Compatibility *For most, {value}.*, Relative advantage *For most, it would have {value} on their last
{occasion}.*), so on the golden seven the six rows' belief sentences and Prevalence's and Relative advantage's phrases
are the engine's new words, and on the eleven rate back-test entries the cost's belief names the payer; no standing,
drift, inside, n or verdict moved. The reader reads **revision 18** and refuses a revision-17 file by name. **v21
stands**: no mark scores a belief sentence (`compare_correctness` reports it beside the counts, never marks it) and
`no_leak` reads the founder's `belief_phrase` as data under the same rule, so the ruler did not move, the record did.
The seven revision-18 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `21395ab0`, equal to
`src/test/resources/keel/corpus-r18/`): `01-countly.yaml`
`84e305923f67b9760f4f8b68f793490cfa5327b508f1860e8b45288d8875c499`; `02-compliancelog.yaml`
`3c8d964502cf413eace932a82bf8ea28bec13679957d31627f771010016084a2`; `03-lullaby.yaml`
`8b55d8e43bd6f5642a8019ea92f381f8398bca9610e808a8c2fbfcad9490f0ca`; `04-linerly.yaml`
`6d3dd62fb68f09a0c67bb3319fb3241fdaf7fe88f24bf2d51cccaee7bc830830`; `05-paidly.yaml`
`0d6f8a0a66ca7d2061487ac5046c95da797c4ba8c68f72eaa32ad67ff70e80e4`; `06-repeatline.yaml`
`5658999231d463408f7e4f8ff4abc476914a4e7203c799655e2c9cbfd9fe0a7b`; `07-mulchrun.yaml`
`9da91df12ef3a0f9a4eb8490216ddfe6ccc11c1d2f3b652d1b03fe6310b3d0f4`.

**Corpus revision 17 (2026-10-28, keel-cloud 147; eval 080, the harness half)**: one standings row moves --
02-compliancelog's Buyer and payer reads HOLDING_UP / none / 7 of 9 inside (was PEOPLE_DISAGREE / both / 5 of 9) under
keel-cloud 145 FR-2's direction-aware rule (a role named, *had to agree* and *decided alone* both support) -- and every
other entry, golden and back-test, moves by its revision line alone; no verdict moved (COMMERCIAL stays NOT_HOLDING_UP on
Price). The reader reads **revision 17** and refuses a revision-16 file by name. **v21 stands**: the ruler did not move,
the record did, so v21's *the corpus stays revision 16* above is history; 076's one named disagreement (the engine and
the facts already reading 7 of 9 against revision 16's 5 of 9) is now agreed -- `compare_correctness` 108 of 108,
`brief_facts` 101 of 101, `report_overview` 49 of 49. The seven revision-17 files, by sha256 (keel-cloud canon's own
bytes at keel-cloud-docs `88bfce8d`, equal to `src/test/resources/keel/corpus-r17/`): `01-countly.yaml`
`6f1226f87876511e9fb615fd489ffc7b93d69a43dd2a8675852753ab2daf0778`; `02-compliancelog.yaml`
`76b2cb578a0cceb6a4ad74aec19b208ad4549b82b51e45d4fcbfd2e0690c5dc1`; `03-lullaby.yaml`
`bf7816847d0eb97aa3b6961bafafcde9738a3ec3fe195fcac332509461666a47`; `04-linerly.yaml`
`8034335c64d0b29025d3569418ef8e337a86d9b0c96e3104297b0bcd3506f9ef`; `05-paidly.yaml`
`34ba180bdf49305622e2e78196289982a39193fced4e0953503f159c7e8eac1f`; `06-repeatline.yaml`
`b025587be123137a5071a7ca769e54df40f94024df7c27a9362fb13b8980cc04`; `07-mulchrun.yaml`
`6e10d4f3518587be88db54d0c6085bfda351dfa2bf83439ddc2aa67d1c3ac79e`.

**Corpus revision 16 (2026-10-23, keel-cloud 129; eval 068, the harness half)**: the golden seven move by their revision
line alone (129 FR-12); every back-test founder's Commitment list is the step alone, so the 112 `yes_after_trying`
picks across the 28 back-test entries become `yes_start` (Keel adds no smaller step the founder did not give, 129 FR-9).
Two golden Commitment options are cut to the whole option's nine words (129 FR-15: 03-lullaby's *Yes, I'd allow it to
use the microphone*, 02-compliancelog's *Yes, after a look at it first*) -- served words, no corpus byte, no code, count,
status or decision moved. The reader reads **revision 16** and refuses a revision-15 file by name. **v20 stands**: this
revision bumps nothing. The seven revision-16 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs
`efdd37bf`, equal to `src/test/resources/keel/corpus-r16/`): `01-countly.yaml`
`131907158493f948b7ac0e71ec4a510cfbe8832c15e32793ffcc661481194c84`; `02-compliancelog.yaml`
`37c3fb2ce7081dc15ae7be93afc91d59f1020af94e3bde143734be27e0f54533`; `03-lullaby.yaml`
`68e13ba3ef624b0ee8bb3a229da2a3e3ca47bc65c3cebbd301c625c812fd55f3`; `04-linerly.yaml`
`514306c4de9abfbbf147d4b74023bf1c104b52bcc90bdaddc11123d0f1890a7c`; `05-paidly.yaml`
`55fd2cb155e108799c17148023c115784503d948e77d8ef696bdd7e2b061452d`; `06-repeatline.yaml`
`075537dabde534a04f4f7d4b8969578fb5973cf6e95f394261857d9a3030bcc7`; `07-mulchrun.yaml`
`a9176347d647dd46c9e599803c4c0eb7b1af165afe672a85a7421c41f6d91dab`.

**Corpus revision 15 (2026-10-23, keel-cloud 128; eval 067, the harness half)**: the golden seven move by their revision
line alone (128 FR-11); the back-test entries gain each person's answer to the segment's condition (`condition`, YES or
NO, rule Q -- 11-issen, 18-careforce), 12-transload's two managers' pilot opt-ins, 11-issen's and 13-aircaps's cost picks
as each person's own loss, and six entries' Importance rivals shortened to fit the founder's 25-word box. The reader
reads **revision 15** and refuses a revision-14 file by name. **v20 stands**: this revision bumps nothing. The seven
revision-15 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `423f0983`, equal to
`src/test/resources/keel/corpus-r15/`): `01-countly.yaml`
`9ee028f1902888732e4580a4daa635464ec96b6e2befbf1b44f9de8fa3c0c303`; `02-compliancelog.yaml`
`e2f2d3345e4bd556044a284abc19e405847340c7042207b5742bbdfca20cd174`; `03-lullaby.yaml`
`33387261056a5d50e9916db854e2240fc44686c592ec9e06339fb4c5aeeeede6`; `04-linerly.yaml`
`72f10800bc24d191296c87cd2a3926f4a8268cceab3ee97a059d52acc20763a4`; `05-paidly.yaml`
`05af06ddb9d23b04e024c4ac0d31f333fb87636e61a99f3cc0412874c7b9d812`; `06-repeatline.yaml`
`a646d30e02117a1cf3fd86c565b30d66a4041c3733f5b39c235b327cc0717d84`; `07-mulchrun.yaml`
`af800e2e46981487d116288aadf890285d42a8a440962b8b1b849460620ab1c3`.

**Corpus revision 14 (2026-10-23, keel-cloud 127; eval 065 and the 064 harness after the fixed chain)**: Commitment's
second yes lives in the golden founders' lists where the step costs data or a signature (02, 03, 06 gain
`smaller_step`), and where it costs nothing (01, 05) *trying it* is the step, so their four `yes_after_trying` answers
read `yes_start` (01's headline 6 -> 7 of 8, 05's 3 -> 6 of 8; no status, drift, median or verdict moved). The reader
reads **revision 14** and refuses a revision-13 file by name; the harness's remap of an unserved conditional yes onto
*probably not* is retired for golden entries (a refusal, rule T) and kept for back-test entries on Keel's AI. **v20
stands**: this cut bumps nothing. The seven revision-14 files, by sha256 (keel-cloud canon's own bytes at
keel-cloud-docs `720f67ca`, equal to `src/test/resources/keel/corpus-r14/`): `01-countly.yaml`
`55266145b892c6571419d795b1a4f37cd4228690c0f72c82e17453d3b8989518`; `02-compliancelog.yaml`
`5c9b7d7e7a4718bed17029ca6471e8b5de7dc1630bccf058f6e760e7787a361d`; `03-lullaby.yaml`
`9ed2936f3efe2633bcc9aa92cbd66ce80540806952f7b666f088cc190e11b6ad`; `04-linerly.yaml`
`b58328714db1fffc38c410878a201e0ca405481187a2e24498d0340acc2225c8`; `05-paidly.yaml`
`bd653d968034724b45f58545f2a0e9708c579a824d6767d9709f37f7acd666f1`; `06-repeatline.yaml`
`a20b48e97d92ce972387c93ea9314acf5313682290b470535575c2fe1b3d68b8`; `07-mulchrun.yaml`
`ef57f0904cda60fd70700220b8c4bc59a20a398fca1121725772f44b87a555a4`.

**Spec 064 (2026-10-23)**: keel-cloud 114-124 / keel-web 093-100 (contract 33, screen response contract 23, routing v12,
corpus **revision 13** at keel-cloud-docs `7915eef`; registry decision 24's value box, the six periods and the chain's
three modes taken by `instructions/registry.py`) -- the reader reads **revision 13** and refuses a revision-12 file by
name as v20's, before the chain. The seven golden entries state no chain and moved only by their revision line, so
every standing, count and verdict the corpus pins reads as it did; the commercial chain (rule C, `instructions/chain.py`)
is read on the back-test entries alone. **v20 stands**: this spec bumps nothing (FR-10). It names, for the operator, the
marks whose words or golden numbers moved under the builds -- each in `specs/064-harness-follows-the-fixed-chain/
tasks.md`'s findings, the served beside the expected: `brief_facts` (the Prevalence line is the founder's clause,
keel-cloud 116; Current solution's and Purchase friction's Keel bars, 117 / 118; Adoption friction's and Commitment's
numbers count the plain yes, Purchase friction's the fear held, 118; the pilot counts the gate's Yes alone, 123 FR-4 --
"2 of 12" -> "2 of 10"), `report_overview` (the decision's named change in place of the semicolon list, 122 FR-3),
`report_insights` (a box a dimension with words, any status, its state; the `notAsked` lines, 119 / 095) and
`spoken_form` on keel-cloud's spoken record (the old cost item's escape label). The seven revision-13 files, by sha256
(keel-cloud canon's own bytes at keel-cloud-docs `7915eef`, equal to `src/test/resources/keel/corpus-r13/`):
`01-countly.yaml` `9c50aeca73d47a839c05614645e37840d3c41787408204d7b31781c75613b77e`; `02-compliancelog.yaml`
`52410aeda42507cbcd78329319c8fcd54a0e135be8b3ef7587777cf4c8b364b0`; `03-lullaby.yaml`
`374a5bf1074e6a3ce76628cfb22dd3612d4ab75e5cf56d3b5776c419c88c1287`; `04-linerly.yaml`
`a49c2219024c5ad6bd9087dca6bb48e7692f4e3dad9e95b428efb486ad485813`; `05-paidly.yaml`
`7162278e7f07f59ea7ae4ab4aaebae8abb977d57af1396ff1e1fb45b326cfbb7`; `06-repeatline.yaml`
`fdc7c70c800acdb84011fdf0f65303f7df9fcd7a381c5ec92f327e605663d575`; `07-mulchrun.yaml`
`f12d0abb2dc7b695d1033025c1244408e89d115f8d78617d49df823658c352c6`.

**`MARKS_VERSION` 19** (history since v20, never run; spec 042, 2026-10-14): the defects batch. The ruler follows keel-cloud 090 / 091 (keel-cloud-docs
`c432c1d`; registry `VERSION` 4, document 20, `CONTRACT_VERSION` 14, routing v11, charge 7 -- the lock holds one job of
35). No mark is born or retired and no number in `marks.toml` moved; four judgement calls moved under them, so the
version moves (this module's own rule). The corpus is **revision 11** (call 110; a revision-10 file is refused by name
as v18's): DRIFT #77's five words fixed -- four Compatibility faces say *your*, 06-repeatline's step is *introduce us
to ...* -- and 05-paidly's Frequency in months out of 3, one median moved (5 -> 2), no status or verdict. `spoken_form`
holds **every** stem to 20 words (call 111: keel-cloud 091 FR-E shortened the two frames call 79 allowed 25) with no
item known apart (call 112: `spoken.KNOWN` is empty); an `L` refusal is read as the validator reports it, a rule
(call 113: keel-cloud 091 FR-C added the letter, DRIFT #76 closed, call 86's reading gone); `brief_facts` reads 091's
words -- `keelBar` on Importance and Current solution, the derived B2C Ability to pay line, `notAsked`'s house style
(call 114). The model's screens, contexts and results are unchanged (091 moved no screen schema; 090 freed only the
founder's idea name). `rescore.py` refuses every bundle below 19 (call 115). **There is no v19 run of record until
`WHY=marks:19` is spent -- the certificate is the founder's word only; never run or propose it.** `DRY=1`-measurable at
`c432c1d`: `compare_correctness` 108 of 108, `spoken_form` **109 of 109** (74 composed items + 35 faces, none apart),
`brief_facts` 94 of 94. v18's paragraph below is history (v18 never had a run of record).
The seven revision-11 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `c432c1d`, equal to
`src/test/resources/keel/corpus-r11/`): `01-countly.yaml` `a3d899d134ca8a48cf075fef6d9133444bc3f64e19f8d60b8d3e3137183c5795`; `02-compliancelog.yaml` `a7c8a68cbd641dade0a1a57fbff885ef3308c1a7327b34cafdf6bf648c3161be`; `03-lullaby.yaml`
`efd8df743e712f333e11195ce376f79922f5554705f8ae4ee577a951dc63f35e`; `04-linerly.yaml` `2dfa46d899d8b006fe5c9977ac2a8e814932cbc88a809f4e7e456d8e10b115f3`; `05-paidly.yaml` `3cef7d5eff5ea528d9b571f68b6ace0fe0b0f89a03eef3127150c627d6cf6668`; `06-repeatline.yaml` `02a04d8a5e38c4f6b5871caf8f904988b58fd81e3052e7b6e712b4e02fb6edc1`; `07-mulchrun.yaml`
`47dde5e0565aef1cb3fd18e8efa8269ba83e2edf8b527de96097f16672840200`.

**`MARKS_VERSION` 18** (spec 040, 2026-10-14): the October redesign. The ruler follows keel-cloud 087 / 088 / 089
(keel-cloud-docs `7b151f9`; registry `VERSION` 4, document 20, `CONTRACT_VERSION` 13, routing v11, charge 7) and
`canon/designs/design-2026-10-14.md` §9 row 11. **All thirteen dimensions decide** (D3): no weight, no DEAL_BREAKER,
no SHAPES anywhere -- a registry still carrying them is refused (call 77) and a vector's verdict is the worst of its
dimensions, which `compare_correctness` asks the engine for (108 of 108 on revision 10). The corpus is **revision 10**
(call 78; a revision-9 file is refused by name as v17's): the founder's lists and picked item, fixed answers and one
escape, no guessed flag, no one-unit window (DRIFT #74 closed by D13). The model writes **no question at all**: the
founder lists (`founder-lists.md`, call 85), the gate's clause (call 83) and -- new, the eighth screen -- the
stranger's `asked` faces (`asked.md`, `ASKED`, call 84); its marks are code's restatements of `L1`-`L5`, `E1`-`E4`
and `K1`-`K6`. Two marks are born and measured at zero spend: **`spoken_form`** -- every item of every corpus
questionnaire, as keel-cloud composed it, held to the spoken-question guidelines (calls 79-81) -- and **`brief_facts`**
-- keel-cloud's cards and pilot against this repository's reading of the corpus (call 82); and `brief_paragraphs`
becomes **`brief_answers`** over the brief's new result (headline, three answers, tests, quotes; call 82). The
reported wording counts of call 56 retire with the text they counted. `rescore.py` refuses every bundle below 18
(call 88). **There is no v18 run of record until `WHY=marks:18` is spent**, on the founder's word only (this spec
never runs or proposes it); v17's paragraph below is history (v17 never had one).
The seven revision-10 files, by sha256 (keel-cloud canon's own bytes at keel-cloud-docs `7b151f9`, equal to
`src/test/resources/keel/corpus-r10/`): `01-countly.yaml` `160a967a162bf44d5fe6dfe0c070df340f829615a876255403624f36a8860e8f`; `02-compliancelog.yaml` `a5dc7c4b4c0f04f0f0a86ec2c49aa9b15ee4546bfb2e433dbca1922f650dc470`; `03-lullaby.yaml`
`9d7eaa6746303f7d4a30e7d615a1498e11b345a8d62a6741cbaf540a4d05b3b4`; `04-linerly.yaml` `84776f41508e05ea9186fb2bd29e8283d254a407497296c65253f85d4e60a9bc`; `05-paidly.yaml` `05478dfae22c3ce0f84f094641f430580712ddfc7e73d05be18540ca9ffdf7c0`; `06-repeatline.yaml` `6fc0caa2e5c30a3244f8878cafe9a3da0041bd793397f04e4d25760b18270827`; `07-mulchrun.yaml`
`733ebc7f3dbe25aceeb8fa15db9900ac3b8dae872a9c04a637ced5076cc3a3e7`.

**`MARKS_VERSION` 17** (history since v18, never run; spec 038, 2026-10-12): Relative advantage, benefit first. The ruler follows keel-cloud 085 (merged at
`b8a4eed`; registry `VERSION` 2 -> 3, project document 17 -> 18, `CONTRACT_VERSION` stays 10). The founder ticks one to
four advantages (`multi_choice`, the belief joined with "or"), and the respondent's one item is **code's whole**
(`benefit_with_advantages`: better / no difference / worse, and under better the founder's ticks): the model's
`RESPONDENT_QUESTIONS` result carries `{"key": "solution.relative_advantage"}` alone, like Price, and anything else it
writes there is not read -- so the RA respondent item owes no question, no options and no W3, and is swept by neither
sweep (sweep B is **56** a run at N=1, was 63, with sweep A still **46**: **102** sweeps, was 109). The founder-side RA
question and five options are the model's as before. The golden corpus moves to **revision 9** (a revision-8 file is
refused by name as v15's / v16's; no status, count or vector verdict moved; three drifts did -- 04-linerly and
06-repeatline `short`, 02-compliancelog `both`), so `compare_correctness` expects them; the `BRIEF` facts carry
`solution.benefit {better, noDifference, worse, n}`. Why a bump: a v16 bundle scored a model-written RA item and a
revision-8 corpus, and cannot be compared. `rescore.py` refuses every bundle below 17. Call 76 below. **There is no
v17 run of record until `WHY=marks:17` is spent** (this spec never runs or proposes it); v16's paragraph below is
history (v16 never had one).
The seven revision-9 files, by sha256 (keel-cloud canon's own bytes, equal to `src/test/resources/keel/corpus-r9/`): `01-countly.yaml` `584625b0d3bdeecd6d64be79433386cadbd47095f1bf8ca11c45da225206e976`; `02-compliancelog.yaml` `c1497e4dad42aba8f4dffc750febf20e0688eca396ed2b502f2beb743de85508`; `03-lullaby.yaml` `4f14d564e4ddc0bf2005e041c372271a6c67c3e115985e5698ef2c234b4edcf2`; `04-linerly.yaml` `3e74db8a58652ee8615248c3cf2449a1f6c2264f37a899bafcb3d044b91f0236`; `05-paidly.yaml` `f2ad5e4a853249b1f2692cd21f352d842113be3927bcae0927f7202d64fb7ef8`; `06-repeatline.yaml` `d72785bf41fca14e36bdac0c75785fc9e7930723d76311d39b5c0da00384daf4`; `07-mulchrun.yaml` `7b6c6d453a485065fa8372dadfd33e6135daba985324b41ba5294b13d3e60e43`.

**`MARKS_VERSION` 16** (history since v17, never run; spec 037, 2026-10-12): the reveal is three lines. The ruler follows keel-cloud 084 (merged at
`fc12b49`; inference `CONTRACT_VERSION` 9 -> 10, project document 16 -> 17). `CONTEXT_INTERPRET` also writes
`occasion` (rules X1, X3: at most four words, no product word); `SOLUTION_MECHANISM` also writes `idea_what`,
`idea_how`, `idea_belief` (L1-L4 lengths, no claim word in what / how, belief opens "The people building it believe
it would"; W3: what carries `short_name`); `RESPONDENT_QUESTIONS` carries no `reveal` and R6 is gone. All of that is
keel-cloud's validator's, delegated as ever (`rule_refusal_rate`, `shape_refusals`). The one mark that moves is this
repository's own: the Part 2 reveal W3 fault (call 55) retires, because a result's `reveal` is no longer read.
Corpus revision stays 8 at v16. `rescore.py` refuses every bundle below 16. Call 75 below. **There is no v16 run of record
until `WHY=marks:16` is spent** (this spec never runs or proposes it); v15's paragraph below is history.

**`MARKS_VERSION` 15** (history since v16, never run; spec 036, 2026-10-12): direction-aware verdicts. The ruler follows keel-cloud 082 (merged at
`438807d`; contract stays 9, document 16): a dimension with a supporting side is one-sided, so a person beyond the
founder's band on that side supports the bet. The golden corpus moves to **revision 8** (a revision-7 file is
refused by name as v13's / v14's; 28 `status` / `drift` / verdict rows moved, the people and picks did not), so
`compare_correctness` -- the engine's `status` + `drift` against the corpus's -- now expects `stronger` / `short`
drift (and, on Linerly, a holding PROBLEM and COMMERCIAL). The registry is exported at **version 2** (the
engine refuses version 1). The `BRIEF` facts this eval builds carry `decision.split` and `decision.notTested`
(`instructions/brief_facts.py`, §4.2 as 082 amended it); `BriefReading.check` did not change, so the five
reading marks are unchanged and take the new facts. No other mark moved. `rescore.py` refuses every bundle
below 15. Call 74 below. **There is no v15 run of record until `WHY=marks:15` is spent** (this spec never
runs or proposes it); v14 never had one.
The seven revision-8 files, by sha256 (keel-cloud canon's own bytes, equal to `src/test/resources/keel/corpus-r8/`): `01-countly.yaml` `81fedfde1c591923b0287a2add568bffe6ac08d749319b37c767a2db9193cdf2`; `02-compliancelog.yaml` `0f58ac60e8df4aa330fb8c0bf5208e2e54838be8d5d08b3c0f7483324605eeda`; `03-lullaby.yaml` `b6693e5d349016815dc9e1b8960929b68af7dd81fc72f94e729f74b380773b85`; `04-linerly.yaml` `3be787a195e4910888d6c49ab6171a4c9c6bc737990f34fa5d330d46ed056699`; `05-paidly.yaml` `d4565a0597905c8a6b5633f27478650178109fc7932cb0c530669bf6798ab9ed`; `06-repeatline.yaml` `407ef8d007cf65189a7f667f2dd07490f7ef3b77565291fd73cf99944b628e5e`; `07-mulchrun.yaml` `11c038f3ac986396b3e517ce57b4ff746ac1c86da52e450344e16af88c14797a`.

**`MARKS_VERSION` 14** (history since v15, never run; spec 034, 2026-10-11): the brief infers and recommends. The ruler follows keel-cloud 079
(branch `079-brief-infer-recommend`, merged at `706015c`; inference `CONTRACT_VERSION` 9, project document 16):
the `BRIEF` screen's result is no longer one paragraph (`whatThisSays`, dropped by the 15 -> 16 upcaster, which
adds `briefReading: null`) but a structured reading -- `{headline, tiles, problem: {conclusion, infer},
solution: {conclusion}, commercial: {conclusion}, sharpest?, next: {sentence, tests[]}, quotes[]}`, every
sentence `{text <= 400, cites[] <= 13}` -- over `facts` that code counts. Its context is `project_name,
market, context, facts, beliefs, stories`. The four paragraph marks retire; **five reading marks replace
them** (`shape`, `cites`, `numbers`, `quotes`, `bans`), each a clause-for-clause restatement of
`BriefReading.check` (refusal `B7`) proved equal to the real `screenContracts validate` by
`tests/test_instruction_brief_reading.py`; the aggregate's own verdict is still `rule_refusal_rate`. Corpus
revision stays 7; no other mark moved. `rescore.py` refuses every bundle below 14. Calls 71-73 below.
**There is no v14 run of record until `WHY=marks:14` is spent** (this spec never runs or proposes it); v13's
paragraph below is history (v13 never had one).

**`MARKS_VERSION` 13** (history since v14, never run; spec 033, 2026-10-10): the buyer's cost is one total. The ruler follows keel-cloud
077 (branch `077-buyer-cost-total`, `dc13341`, off `911f08c`; inference `CONTRACT_VERSION` 8): the
respondent answers Existing sacrifice with one number -- an amount or a number of hours -- over the
founder's recall period (registry respondent control `cost_total`, chips *It cost us nothing* / *I can't
recall* / *That's a rough guess*), so there are no kinds of cost anywhere. Existing sacrifice owes the
model **nothing** on either screen, as Price already did: the calibration entry is its key and
`respondent_note` (options are `C2`), the respondent item its key alone (code composes the question);
`W10` and `U1` retire; the registry carries no cost `code_rule`; the corpus is **revision 7** (an r6 file
refused by name; Existing sacrifice picks are `{mode, value, currency, period}`, `{nothing: true, ...}` or
a chip, with no option counts; **no standing or verdict moved vs r6**); the brief's time-only figure is
the B2C `HOURS` totals; `rescore.py` refuses every bundle below 13. Calls 67-70 below. **There is no v13
run of record until `WHY=marks:13` is spent** (v12's is still on hold by the founder, and this spec never
runs or proposes either); v12's paragraph below is history (v12 never had one).

**The corpus v13 judges, recorded 2026-10-10** (spec 033 US2). Revision 7's seven entries in keel-cloud 077's
canon (`dc13341`), by sha256:

    01-countly         90292cbba8d19af9511caa7feeba425ff339989af84674472257df24191404b4
    02-compliancelog   92ef9d968db83259c61d4c430c069708fec14758d520e879a59c38b9e812feae
    03-lullaby         eb950920e4ca6263fd84e3ded3e7066a6b74dc52f1b915e64f2c195681ef6a46
    04-linerly         15e69221f2ce82dfe585197f02c39dc6ba7ccfd44a6ad6d10936e2c180be4a35
    05-paidly          5842ce136b867d6b26ae2da71db02ef4ea570afce684ceb598d41e6042eec93b
    06-repeatline      39796410abcc2b076475e48846a00b4eb6f19f578e8d6e51896d5334ae498219
    07-mulchrun        97300a40a2b559fee1e628e923daabad729978b9dd42ece5d3c0b978010ef599

The v13 denominators, **counted, not estimated** (`DRY=1 MODELS=exported` against 077): calibration the
*answered* set -- 11 keys on 01-04 (B2C) and 12 on 05-07 (B2B), **80** an N (unchanged: Existing sacrifice is
still a question in the job, owing its key); respondent 11 on a B2C entry and 13 on a B2B one (**4 on Mulch
Run**), **81** an N (unchanged); `no_leak` **46** sweep-A and **63** sweep-B items an N -- **109**, seven fewer than
v12's 116, because the buyer's Existing sacrifice, which carried model text, is code's now and is never swept;
`compare_correctness` 12 + 3 or 13 + 3 checks an entry, **108** on seven, 1.00 on the 077 engine.
`anchoring_accuracy` is still 65 reads at N=1; a full run still builds 135 model cases at N=1 (405 at N=3).

**`MARKS_VERSION` 12** (history since v13, never run; spec 032, 2026-10-10): cost first. The ruler follows keel-cloud 074 (branch
`074-cost-first-price`, `5311217`, which merges 075): the founder first estimates what the problem
costs (Existing sacrifice is a `cost_estimate` -- an amount, or hours at the project's rate, over a
period of a day to a year -- read by `interval_contains_median`), then prices it for that same period
(Price fixed to the cost's, five periods), and Ability to pay is **derived** from the two and never
asked (`derived`, read by `cost_covers_price`, `b2b_link_only`: calibrated on every persona, asked on
the decision-maker's link alone). The registry stays **thirteen** (4 / 3 / 6) in its cost-first shape,
the corpus is **revision 6** (an r5 file refused by name), the two money questions are code's so
Existing sacrifice owes its kinds with units and no question text, Price its key, and Ability to pay is
not in the calibration job (the denominator is the *answered* set); `W10` holds the part-3 Existing
sacrifice question to the recall words; the brief's cost and ability figures are keel-cloud's own,
B2C people who gave only time are reported apart; `rescore.py` refuses every bundle below 12. Calls
59-66 below. **There is no v12 run of record until `WHY=marks:12` is spent, and it is on hold by the
founder**; v11's paragraph below is history (v11 never had one).

**The corpus v12 judged, recorded 2026-10-10** (spec 032 US2; history). Revision 6's seven entries in
keel-cloud 074's canon (`5311217`: r6 after the 075 merge and founder decisions 1 and 2), by sha256:

    01-countly         0d28f78f8624f923cd186ad05a3a94752d78dff82f06e6db10d1c0aedbfc7c2c
    02-compliancelog   e830469c45539344d8456ec709c2688d76238956c9856ce4dc73cce827ce0324
    03-lullaby         1845d53847dc0058385b03d09280ca304eea9c03770c1221595d61fbe14333ce
    04-linerly         f3cc8630ddeb38320644c250eb79dbc5dd3e81020a8b8402db8ef20276d4c05e
    05-paidly          49240210c39c0eb9c67c6f82b6ab372423a2da92166181b3f0f6edbc74793dcc
    06-repeatline      601a68b69097cc10c2475f8d7eb23c28f66eeaa691c9b24065acb3f4c2858185
    07-mulchrun        6e8d796ec582e48f0aa586a6387a26fde3e58fd8b2619eb9fe075986216effcc

The v12 denominators (history), **counted, not estimated** (`DRY=1 MODELS=exported` against 074): calibration
the *answered* set -- 11 keys on 01-04 (B2C) and 12 on 05-07 (B2B), **80** an N; respondent 11 on a
B2C entry (4 / 3 / 4 on `PRIMARY`) and 13 on a B2B one (4 / 3 on `PRIMARY`, 6 on `COMMERCIAL_B2B`;
**4 on Mulch Run**, whose founder left Price out and so Ability to pay), **81** an N; `no_leak` **46**
sweep-A and **70** sweep-B items an N (never Price, never Frequency over a framed window, never the
founder's Existing sacrifice -- 116); `compare_correctness` 12 + 3 or 13 + 3 checks an entry,
**108** on seven. `anchoring_accuracy` is still 65 reads at N=1; a full run still builds 135 model
cases at N=1 (405 at N=3).

**`MARKS_VERSION` 11** (history since v12, never run; spec 031, 2026-10-09): the subjects' words moved and the ruler follows
keel-cloud 072 + 073 (branch `073-price`, `0925484`). The registry is **thirteen** (4 / 3 / 6, Price
back as SHAPES), the corpus **revision 5**; Prevalence and the gate are read as an `event` clause
held to E1-E3 and C7 / R8 retire; Price is code's on both sides; W7, W9 and U1 (and W3 / W8, where
the corpus records the names) are structural; the wording rules the subject only instructs (S1, W1,
W2, W5, W6) are reported per question and never marked; the brief's two commercial figures are
keel-cloud's own; `rescore.py` refuses every bundle below 11. Calls 50-58 below. **There is no v11
run of record until `WHY=marks:11` is spent, and it is on hold by the founder**; v10's paragraph
below is history (v10 never had one).

**The corpus v11 judged, recorded 2026-10-09** (spec 031 US2; history). Revision 5's seven entries in
keel-cloud 073's canon (`78e1118`: r5 with the two golden names of `ed581f8`, additive), by sha256:

    01-countly         d354a69e63755a42226fd7e72d58b39f07b0913df0839c3582288460dbccecd7
    02-compliancelog   448a44fa4920a7688a8dd6c6c2dd69278bb316c81617756aeabe38e791cd6a24
    03-lullaby         54c127906709dee251bd11a8dbf3589e75450424a75c15a5b6d4ef0ad9740e22
    04-linerly         effd50dd0d1e7716308a3efc9492e99684b1e3f711aaf88666300bfadca9a9f7
    05-paidly          e7c39b4b255b02b7c2263a9388df6ea7fe01ebb24d018ff531ec4d77f6441ba0
    06-repeatline      70b889dadc1bb7164b9497dccea0e461e1ef8d99563a2862433bf6961d4242a1
    07-mulchrun        0a06b4ee3712663031f6f3b73adc1623bcf247f9a6de9a9c346a233183d453c3

The v11 denominators, **counted, not estimated**: calibration 11 keys on 01-04 (B2C) and 13 on
05-07 (B2B), 83 an N; respondent 11 on a B2C entry (4 / 3 / 4 on `PRIMARY`) and 13 on a B2B one (4
/ 3 on `PRIMARY`, 6 on `COMMERCIAL_B2B`; 5 on Mulch Run, whose founder left Price out), 82 an N;
`no_leak` 46 sweep-A and 71 sweep-B items an N (never Price, never Frequency over a framed window --
Countly's *last month* and Repeatline's *last shift* keep theirs); `compare_correctness` 11 + 3 or
13 + 3 checks an entry, **104** on seven. `anchoring_accuracy` is still 65 reads at N=1; a full run
still builds 135 model cases at N=1 (405 at N=3).

**The corpus v10 judged, recorded 2026-10-09** (spec 030 US2; history). Revision 4's seven entries in
keel-cloud 071's canon (`f38ac42`), by sha256:

    01-countly         81d5d00665fab6b284f5238f2c2d8512226105d7566e88ad2c1f47a73ba7f391
    02-compliancelog   0585d989e1f4b890bd4648826921dc36a58d3efaf5dbc6a144df66d4a0487e1a
    03-lullaby         fe1f3babc2af3c487f4edc9fa1fa2b84ae0875c596e3e8b17f0d0df3d40d1573
    04-linerly         c781766e3080c495586dacaceb02e388775fe8700956c85a86e957347fb5800a
    05-paidly          0a98e4db5e4640399bcd87559593dc91595c5e80cde094e3ae52276defbf6f6a
    06-repeatline      0754e19cb43e1a463acb081dc4dec96caab0bb1831c2b89a883d0b30071233a2
    07-mulchrun        86deab848963eee58255e8c09abf4579f964ecd27ea6bad276eaae46e4d94e4f

The v10 denominators, **counted, not estimated**: calibration 10 keys on 01-04 (B2C) and 12 on
05-07 (B2B), 76 an N; respondent 10 on a B2C entry (4 / 3 / 3 on `PRIMARY`) and 12 on a B2B one (4
/ 3 on `PRIMARY`, 5 on `COMMERCIAL_B2B`), 76 an N; `compare_correctness` 10 + 3 or 12 + 3 checks an
entry, **97** on seven. `anchoring_accuracy` is still 65 reads at N=1 (106 people less 13 gate-No,
6 chipped stories and 22 decision-makers). A full run builds **135 model cases at N=1** (405 at
N=3): three interpretation screens, three calibration jobs and three respondent jobs an entry
(part 3 of a B2B study is the decision-maker's link, never a fourth job), 65 reads and seven briefs.

**The corpus v9 judged, recorded 2026-10-07** (spec 029 US4.2, plan O-4; history). Revision 3's
seven entries, by sha256 -- the recorded revision under `tests/fixtures/corpus-r3/` (deleted at v10,
call 49), moved verbatim into keel-cloud's canon:

    01-countly         e8b72c47d57085133032d267682f720eecb603b4aab921f2b5a85ccc96815320
    02-compliancelog   5b8d01a9048dc7263f6e8de82da2221f91ffc413b2229dba5e452d59821fda27
    03-lullaby         229f794d6374c315dd6c8edac4d21051d411888f63005b84e72cb28ccab50ed8
    04-linerly         0aa0b13f4f649de942a54baff934e4e6a464098f0e40f4cc2d82b41cf4498fc9
    05-paidly          00f0d030e32457a00c35e9118865591168c9dd4caa661992303b4ed4251b3716
    06-repeatline      991bd046984a64675e07c59ed5dc57f905a63ee87100c1e241dd49006ff43f61
    07-mulchrun        a4e76486a16c07a0f2be1d54d2d2b8f17a0417292e3999dbc81d5b4a2cd7e682

Amended 2026-10-08: Lullaby's `mechanism_terms` drops `cot` (call 39), and every entry's model-written
sets gain `founder_calibration[d].labels`, the labels production sends as `founder_options`.
Amended 2026-10-08 again, synced to keel-cloud 058 `5fc7220`'s canon byte for byte: 13 belief
sentences are the engine's again (`problem.prevalence` in 01/02/04/05/06/07, `problem.importance`
in all seven), every entry records `context.recall_window: {count, unit}` (founder decision 42),
and Lullaby's circumstance reads *the baby cries in the night* (the GRAMMAR decision).

The corpus-wide `anchoring_accuracy` denominator, **counted, not estimated**: 106 people, less 13 who
answer No at the gate, 6 whose story carries a chip and 22 decision-makers on a B2B link (who are
never read) -- **65 reads at N=1, 195 at N=3**. A full run builds 138 model cases at N=1 (414 at N=3)
and 7 `COMPARE` rows; `compare_correctness` is 196 checks.

Judgement calls, append-only across every version, struck nowhere, because the rubric's history is
part of what a number means:

1.  **v1**: exact-match is over matched pairs only, so recall and exactness are not
    double-counted.
2.  **v1**: `measure.kind`/`measure.unit` are `n/a` for a Choice pair and excluded from the rate
    rather than counted as agreeing.
3.  **v1**: extra beliefs are counted and not marked. Over-generation is a finding first.
4.  **v1**: band equality is exact, because the phrase table is a fixture, not a judgement.
5.  **v1**: `GUESSED` precision and recall are mandatory beside accuracy, never optional.
6.  **v1**: a shape refusal, a schema-invalid answer and a rule refusal are three different lines.
7.  **v1**: the spread is reported; nothing is averaged before it is reported.
8.  **v1**: `founderPhrase` is a scored exact-match field, and absent-on-both-sides agrees, because
    a `CHOICE` has no phrase and requiring one would penalise every Choice belief.
9.  **v1**: a `NEEDS_INPUT` from an assumption screen whose statement was present is a failed case
    counted in the recall denominator, per design decision 14 -- not excluded, and not softened.
10. **v1**: the register is rendered and never scored. A metric here would look like evidence and
    be similarity to one hand-written example; the design requires a person, so the run records
    what the person said.
11. **v2** *(the founder's decision, 2026-09-06, after the baseline)*: **option lists are matched
    by meaning, not by words.** The corpus's option words are one reasonable phrasing of an answer
    space; `Q2` requires a belief's list to equal *its own selection's* list and never the
    corpus's. So a Choice pair with no structural overlap goes to the judge, which decides whether
    two lists describe the same answer space, and `expected` becomes a judged semantic match
    rather than a string comparison. The baseline's SOLUTION recall of 0/23 was what forced the
    question: the produced beliefs were about the same things in different words.
12. **v2**: `measure.per` is an eighth scored field. `Measure` is a three-field record and its own
    Javadoc says all three decide equality for `V2`, so a belief whose `per` differs expects a
    different number and an answer against it places nowhere. Nine of the baseline's fifteen
    matched interval pairs disagreed on `per` while scoring a clean sheet on every field that
    existed.
13. **v2**: an **unmeasured** mark is not a met mark. `refusals` read `0 / met` in the baseline
    because nothing had been shown to the aggregate yet; a mark with no measurement behind it now
    fails, as the other two already did for a `None`.
14. **v2**: the **judged fraction is reported on every run**, per case and overall, so a reader
    can discount a score by exactly the amount a model decided. Judgement call 11 buys recall at
    the cost of determinism, and this is the price tag.
15. **v4** *(spec 009 follow-on, 2026-09-07)*: **a new subject is a rubric change.** The `BRIEF`
    screen joins the reading and the assumptions, and a fourth mark joins the three:
    `brief_paragraphs`, the fraction of BRIEF cases that met **all four** of `instructions/brief.py`'s
    per-case marks (shape, coverage, register, source_material). Adding a subject changes what a
    passing run means even where every existing number is untouched, so scores before and after
    this bump are not comparable and the constant says so. (There is no v3 judgement call: v3
    bumped for keel-cloud's `(stage, anchorId)` pair, recorded in `score.score_reading` itself.)
16. **v4**: `brief_paragraphs` is **all four marks or nothing**, per case. A paragraph that is the
    right shape and names no verdict has not half-worked; it is a paragraph a founder would read
    and be misled by, and averaging the four marks together would hide exactly that.
22. **v6** *(the founder, 2026-09-12)*: **the rule-refusal mark is a rate, and shape refusals
    keep their zero.** A rule refusal is the product correcting the model (one extra call, nothing
    a founder sees), and an absolute zero made one invented unit in 1,179 case-runs a failed host.
    `rule_refusal_rate` is refusals over the answers the aggregate actually judged -- 63 on a full
    N=3 run -- so 0.02 reads "at most one correction across the corpus". `shape_refusals` stays
    an absolute zero: an envelope the runtime had to repair is a different failure. Applied to
    every host equally, and every earlier bundle can be re-scored under it without spending.
17. **v4**: **the paragraph is rendered as well as marked.** `brief.md`'s contract is one free-text
    field, so almost everything about a good paragraph is wording -- design §3.8's *cannot be
    checked by code*. The four marks cover only what `brief.md` states as a rule; the paragraph
    itself goes on `register.html` beside its entry's standings, unscored, for the same person who
    reads the anchors (judgement call 10, one subject wider). A mark this narrow can be wrong
    about a paragraph that is right, and the run has to leave the evidence for that.
18. **v4**: **the ordinary-English field names are exempt from `source_material`**, exactly as
    `evals/policy.py`'s judgement calls 1, 5 and 10 exempt theirs. `inside`, `outside`, `guessed`,
    `escaped`, `claims`, `beliefs`, `statement`, `heading`, `risk`, `verdict` and `drift` are
    words `brief.md` itself tells the model to write -- *"how many people landed **inside** the
    founder's own band"* is the instruction's own sentence -- so sweeping them would flag the
    paragraph the instruction asks for. What is swept is the shape a field name has and prose does
    not (`instructions/brief.py`'s `CONTEXT_FIELD_NAMES`).
19. **v4, and stated before the run rather than after it**: the BRIEF context this eval sends is
    production's in every field but one -- `median_reads`, which keel-cloud renders with
    `Measure.say` (rounding minutes to the nearest five above ten, climbing to the largest unit a
    person would use, putting the market's symbol on money). This repo does not own that
    arithmetic and will not keep a copy of it (`runs/DRIFT.md` #33/#36/#41/#44/#45, five times the
    same lesson), so the middle answer goes over in the corpus's own unit: `0.75 hours`, where
    production would say `45 minutes`.

    **`brief.md` names that exact string as a wrong way to say a number** -- *"you quote it
    exactly: 45 minutes, not forty-five minutes, not 0.75 hours"* -- so on the one corpus entry
    whose deciding line has a median (`01-countly`'s `P3`), a model is caught between the rule and
    the example. Whichever it does is worth recording, and the `coverage` mark scores it against
    the **rule**: quote what you were handed. A miss there is this eval's own limit, named here,
    and never a keel-cloud finding. What would close it is a context keel-cloud exports rather than
    one this repo assembles; that is a spec, not a rerun.
20. **v5** *(the first BRIEF run, `runs/20260908T004022Z-instructions`, $1.20 over seven real
    calls, and no rerun)*: **the design's verdict phrase is observed and never marked.** v4's
    `coverage` required each claim's verdict to be named in `FounderVoice`'s own words -- *holding
    up*, *not holding up*, *people disagree*, *still asking*. The run came back **0 of 7**, and
    reading the paragraphs showed the mark was wrong, not the instruction: `brief.md`'s own next
    sentence is *"Write them into ordinary sentences -- 'the problem is real', 'nobody pays
    anything like that today'"*, and that is exactly what came back (*"The problem is real"*,
    *"Your solution splits twice"*, *"On price the ground is firm"*). A code check on the words
    scores the paragraph the instruction asks for as a failure, which is judgement call 10's rule
    arriving from the other direction. So `verdict_phrasing` records per stage whether the phrase
    appears, `register.html` renders it beside the paragraph, and a person decides.
21. **v5**: **a split is counted from both sides.** v4's *no invented `N of M`* allowed only
    `inside` of `inside + outside`. `brief.md`'s third thing a paragraph says is *who the split is
    between*, named by the answers people gave -- *"six of nine had a member of staff take the
    delivery in; three took it in themselves"* -- so `outside` of the same total is a count the
    standings contain too. `02-compliancelog` was marked down for *6 of 10 rebuilt the draft they
    were handed*, which is its own line's `outside` read out exactly as asked.

    Both fixes were made **from that run's own bundle and re-scored without spending again**
    (`python -m instructions.rescore`), which is what a versioned rubric and a kept bundle are
    for. The v4 scorecard stays in the bundle beside the v5 one; neither overwrites the other.
23. **v7** *(the founder, 2026-09-13)*: **the `shape` fault's length edge follows the contract**,
    which moved `whatThisSays` from 1 200 to 2 000 characters (keel-cloud
    `ScreenResponseContracts.WHAT_THIS_SAYS_MAX`, `runs/DRIFT.md` #68). The four marks and
    `brief_paragraphs`'s number are unchanged; a paragraph is judged against the edge production
    actually enforces. **Transcribed here at v8 from `marks.toml`, which has cited it since v7 while
    this list did not carry it** (spec 025 FR-003). It is a transcription and not a new call: no
    number and no rule moves with it, and the list is now what it says it is -- append-only and
    complete.
24. **v8** *(the founder, 2026-09-30; `one-occasion-once-design.md` §8.2)*: **the match key is the
    bare `anchorId` again, because the questionnaire is the project's.** v3 made it
    `(stage, anchorId)` when a stage owned its questionnaire and three of them each numbered from
    `A1`. One questionnaire per project makes `Q7` project-wide, so the pair carries no information
    the id does not, and a `stage` on an anchoring names nothing -- a merged occasion serves more
    than one stage's beliefs.
25. **v8** *(design §8.2)*: **a corpus anchor's `stage` becomes `stages`, a list, and is a label
    rather than a key.** `Entry.anchors_for(stage)` returns the anchors whose `stages` contain it,
    and one anchor may be returned for two stages. Scores before and after are not comparable and
    the constant says so.
26. **v8** *(design §6A.8)*: **a belief that reads another belief's measurement is aligned and
    counted as an ordinary belief.** Two lines reading one control are two lines in the recall
    denominator; the control they share is one, and `anchoring_accuracy` counts person-anchor pairs
    rather than controls, so it does not see the change.
27. **v8, and it is the correction 26 was written conditional on** *(design §6A.8: "That answer
    depends on one fact this pass did not verify ... Spec 049's first task is to check it")*: **the
    expectation is copied here, not by the server, because this eval scores the model's raw
    answer.** `runner.py` stores `response["result"]` and applies it to nothing; `score.py` hands
    `result["assumptions"]` straight to `align.align`; `produced_view` reads `belief["expectation"]`
    and a belief carrying only `reads` has none, so `structural_candidate` refuses it on `type`
    before a judge is ever asked. keel-cloud's validator is shelled for a verdict and never hands an
    applied `Assumption` back. So `align.resolve_reads` copies the referent's whole expectation out
    of the `earlier_lines` **this eval itself numbered and sent**, before alignment, and a reference
    that cannot be resolved is counted as `unresolved_reads` and left to fail to match. 26 holds
    *because of* this call, not in spite of it: with it, `align.FIELDS` does not change and the
    recall denominator does not change.
28. **v9**: **New subjects are a rubric change.** The five new screens of §1 replace `*_ASSUMPTIONS`
    and `QUESTIONS`; `INTERPRET` keeps its constant and is narrowed to the gate story (one judgement
    a respondent); the three interpretation screens are rendered and never scored — their leaks are
    rule refusals (`X1` / `P1` / `M1`) feeding `rule_refusal_rate` only (call 10). Scores before and
    after are not comparable.
29. **v9**: **`golden_belief_recall` is retired, and `align.py` with it.** A calibration answer is a
    typed pick against the registry; the model writes the question, the engine writes the belief.
    There is no structure to align, no option list to overlap, no tie to break. The golden is the
    registry slice, not text.
30. **v9**: **`dimension_coverage` is absolute.** One question per dimension, both screens;
    denominators per §2.1. A plan the eval built by code from `founder_calibration` is what the
    respondent screen is handed, exactly as production's `EVIDENCE_PLAN` would.
31. **v9**: **`option_validity` is code, and 1.00 is honest only because the registry fixes the
    codes.** The mark checks the mapping, not the invention.
32. **v9**: **`no_leak`'s list is derived from the corpus's golden mechanism, never from the live
    `SOLUTION_MECHANISM` output** (the ruler must not move with the subject); ties are inflection
    collisions with the problem's own words and go to the judge; every other hit is a fault.
33. **v9**: **One anchoring judgement per respondent.** Gate-No respondents are outside every
    denominator; **amended 2026-10-07 (decision 10):** a chipped story is set `GUESSED` by code with
    no call and is OUTSIDE the denominator too — only un-chipped stories are read. Number unchanged.
34. **v9**: **`compare_correctness` spends nothing and is measured on `DRY=1`.** Status + drift
    marked; counts reported; an export without the engine leaves it unmeasured, which fails (call
    13). This repo keeps no copy of the arithmetic (DRIFT #33/#36/#41/#44/#45).
35. **v9**: **`brief_paragraphs` gains `no_claim_words`**, scoped to the sentence naming a `BAR_SET`
    or `NOT_TESTED_BY_DESIGN` dimension; the deciding line is the worst deal-breaker; all five or
    nothing.
36. **v9**: **`rule_refusal_rate` keeps 0.02 while its denominator triples**; the new reading is
    recorded in `marks.toml` and is the founder's decision 1, not a quiet tightening.
37. **v9, amended before any run of record** *(the founder's decision 32, 2026-10-08; screen
    `runs/20261008T001657Z-instructions`)*: **a belief phrase may equal its label.** C4 in
    `option_validity` no longer faults a phrase that is its label after `normalise` -- keel-cloud
    062 accepts it, and a mark that refuses what the product accepts measures the eval, not the
    instruction. C4 still faults an empty phrase, one over 120 characters, and one carrying a
    not-sure word. `MARKS_VERSION` stays 9: no v9 run of record had been spent.
38. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T013837Z-instructions`)*: **code appends, never the model** -- *Something else*,
    every respondent-only code the registry names and every band, scale-axis and gate option -- so
    a fixed-code control or the ladder owes exactly one label per remaining plan code, a set every
    founder label (normalised) plus 2-3 distractors, Importance 4-6 difficulties, and a band,
    numeric or gate control `options` null. `MARKS_VERSION` stays 9.
39. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; same bundle)*:
    **`no_leak`'s vocabulary is stemmed from the golden mechanism's `mechanism`, `output`,
    `not_assumed` and `mechanism_terms` only**, never `trigger` (it describes the problem moment)
    or `actor`, less the problem's own stems as before. `MARKS_VERSION` stays 9.
40. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T024419Z-instructions`)*: **sweep B reads the stem, not the options.** The
    founder's label, `belief_phrase` or number for dimension *d* is swept in respondent item *d*'s
    question and the part's reveal only: a fixed-code control shows every rung, the founder's among
    them (Lullaby's *A few taps* on Adoption friction), and a set shows the founder's labels
    verbatim by R2, so a founder label in an option is the rule, not a leak. `MARKS_VERSION`
    stays 9.
41. **v9, amended before any run of record** *(the founder's decision 35, 2026-10-08)*: **the
    structural marks read the accepted answer.** `option_validity`, `dimension_coverage` and
    `no_leak` on the two question screens are scored on the answer after the runtime's rule
    refusal and ONE redraw -- what a founder sees -- because a rule refusal is the product
    correcting the model, one extra call (call 22). The runner redraws as keel-cloud 058's
    orchestrator does, on the five screens it repairs (`CALIBRATION_QUESTIONS`,
    `RESPONDENT_QUESTIONS` -- `repairUnattended`; the three draft vector screens --
    `refuseOrRepairDraft`; never `INTERPRET` or `BRIEF`): turn one's context plus a `repair`
    sentence in the cloud's own words, the same instruction, contract, model and effort, empty
    input, and no previous answer. The raw slip stays measured: `rule_refusal_rate` counts every
    refusal, first draft and redraw, over the first-draft answers (the v6 denominator). A second
    refusal is terminal: the answer stays refused, scores as faults on the raw answer, and counts
    twice. Shape refusals are not redrawn and stay an absolute zero on the raw answer. A v9
    bundle taken before this call has no redraw and is re-scored on the raw answer, saying so.
    `MARKS_VERSION` stays 9.
42. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T115552Z-instructions`)*: **coverage's observed figure for money sets.** A set
    dimension's money median (Existing sacrifice) was handed to `BRIEF` as a bare *165* and the
    check then asked for *165*. It is written in the founder's unit, *£165 per three months* --
    the currency's symbol and the period from the standing, else the one every answer's `cost`
    agrees on, the currency else the market's (the price likewise, as keel-cloud's
    `observedFigure` writes it) -- and a set whose money cannot be written so carries no figure and
    is asked instead for one of its own option counts as `N of M`. The founder's phrase is asked
    for exactly as strictly as brief.md asks: on a bet whose verdict is `NOT_HOLDING_UP` ("The
    four things the paragraph says", 2: `founder_phrase` against `observed`), verbatim -- brief.md
    licenses no paraphrase -- and on no other bet. `MARKS_VERSION` stays 9.
43. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; same bundle)*:
    **a mechanism stem in an option label is a tie.** Sweep A's direct hit inside an OPTION LABEL
    of a PROBLEM calibration question or a Part 1 respondent item (*phone*, *wheel*, *caught* --
    generic nouns of the problem's own world, offered as answers) goes to the judge with the one
    existing question, as an inflection tie does -- a multi-word term too (*signed off*); a hit in
    the question stem stays a fault outright. `MARKS_VERSION` stays 9.
44. **v9, amended before any run of record** *(the orchestrator, 2026-10-08; bundle
    `runs/20261008T115552Z-instructions`)*: **three narrowings of what is the model's.**
    (i) `option_validity`'s not-sure OPTION is one whose whole normalised label is *I'm not sure*,
    *Not sure*, *Don't know*, *I don't know*, *Unsure* or *Prefer not to say* -- never a label
    that contains the words (*Not sure it would fit* is a reason; keel-cloud 058's C3 likewise);
    and a code-appended escape row is told by its label as 058 appends it (*None of these*,
    *Nothing*, *Nothing yet*...), never by a fixed slug -- production slugs the founder's escape
    `none_of_these_<...>`. The same whole-label test finds an escape row the MODEL wrote (a
    fault, code appends it): *Something else*, *None of these*, *Nothing yet*, *Nothing* and the
    registry's escape labels, normalised for case and punctuation -- never a prefix (*Something
    else was cut or given up to cover it* is Ability to pay's scale step, code `barely`; the
    prefix match faulted certificate run 3, `runs/20261008T194906Z-instructions`). **(44a)** `no_leak`'s vocabulary, per question, subtracts every stem of
    the registry's own wording for the dimension being asked -- its `respondent` block (guidance,
    option_rule, chips), its founder `option_rule` and `code_rule` (the fixed escape labels) and
    the registry's `common` block; never its `lullaby` example. *In the order you tried them* is
    registry wording and can never be a leak. **(44b)** Sweep B (the founder's label, phrase or
    number) reads question STEMS only, never the part's reveal: the reveal is governed by R6's
    claim-word rule and legitimately names the mechanism's moment (*at quarter end*).
    `MARKS_VERSION` stays 9.
45. **v9, amended before any run of record** *(the founder's decisions 46 and 47, 2026-10-08;
    bundle `runs/20261008T155720Z-instructions`)*: **what each step can apply.** **(Decision
    47)** `no_leak`'s sweep A on a PROBLEM calibration question uses keel-cloud 058's product-word
    list (`Vocabulary.PRODUCT_WORDS`, whole-word) and the golden mechanism's `mechanism_terms`
    only (single words by stem, less the registry's wording for the dimension, call 44a;
    multi-word terms as phrases), in the question, its options and their belief phrases -- what
    the runtime can refuse at that step -- and a hit is a fault, never judged. Part 1 respondent
    items keep the full derived vocabulary and the judge (calls 32, 39, 43, 44a).
    `judged_fraction` is items judged over items with any hit -- one unit, reported, never marked
    (it read 0.72 as items over word hits). **(Decision 46, call 41 extended)** `BRIEF` is redrawn
    once on a rule refusal, as the cloud now does (`repairUnattended` ->
    `queueAnotherQuestionsTurn`: turn one's context plus `repair`, no history, empty input), and
    the accepted paragraph is scored; a brief refused twice is scored on its raw paragraph as a
    fault, every mark missed -- the founder is shown no paragraph. `MARKS_VERSION` stays 9.

**The v9 run of record, recorded 2026-10-08** (the founder's decision 48; not a judgement call):
`runs/20261008T194906Z-instructions` -- `WHY=marks:9`, host claude, `MODELS=exported`
(claude-sonnet-5-5 at medium, Haiku 4.5), 414 cases, $19.75 -- **re-scored** under call 44's
whole-label escape fix. The run's one fault was a legitimate scale step (Ability to pay's
*Something else was cut or given up to cover it*); the answers are untouched, and the run's own
11 judge answers were all DIFFERENT. Every mark met: `dimension_coverage` 1.00, `option_validity`
1.00, `no_leak` 1.00, `anchoring_accuracy` 0.9949, `compare_correctness` 1.00, refusals 0.0072,
`shape_refusals` 0, `brief_paragraphs` 1.00. The founder accepted the re-score as the certificate.
`runs/` is gitignored, so the bundle lives on this machine only; its `scorecard-v9.json` is
sha256 `1cae4bb5b85bfeb47dedfb54b51ea9d06361f79bfecbee78cd21884445e81dea`. It is history from
2026-10-09: `MARKS_VERSION` 10 refuses to re-score it (call 49, `rescore.py`).

46. **v10** *(spec 030, 2026-10-09; keel-cloud 071, registry decision 14)*: **the registry is
    twelve, calibrated and asked alike.** Invariants 1, 2, 3 and 8 are rewritten: twelve keys,
    4 / 3 / 5; the nine deal-breakers are Prevalence, Importance and Current-solution satisfaction;
    Compatibility, Relative advantage and Adoption friction; Existing sacrifice, Buyer/payer
    alignment and Commitment; `b2b_only` sits on exactly `commercial.ability_to_pay` and
    `commercial.purchase_friction`, and every entry is asked in its own vector's part (4 / 3 / 5;
    `PRIMARY` asks 3 / 3 / 3 after the gate, `COMMERCIAL_B2B` 5); and every deal-breaker's status
    vocabulary reaches `NOT_HOLDING_UP` (invariant 8). `asked_in_v1` is not read; a registry
    carrying it is refused as unknown-shaped, not ignored. Invariant 6's numeric controls are the
    ones keel-cloud's `RespondentControl.yieldsNumber` names (`segmented_0_to_7`, and
    `number_with_unit` on a recall window longer than 7).
47. **v10**: **the plan is per link and per persona.** `dimension_coverage`'s respondent
    denominator is `plan_keys(part, founder_calibration, link, b2b)` -- on `PRIMARY` the registry
    less the `b2b_only` pair, on `COMMERCIAL_B2B` the commercial part whole -- and part 3 of a B2B
    study is asked on the decision-maker's link only (keel-cloud `EvidencePlan`, decision 26), so a
    B2B entry has three respondent jobs, not four. The calibration denominator is the entry's
    calibrated set, `calibrated(b2b)`: on a B2C entry the two `b2b_only` keys are not calibrated,
    and a `founder_calibration` (or a pick, a plan row or a standing) naming them is a refusal
    naming the key.
48. **v10**: **`no_claim_words` retires** with `BAR_SET` and `NOT_TESTED_BY_DESIGN` (keel-cloud
    071 removed both statuses and the two rows they scored); `brief_paragraphs` is all four or
    nothing. Struck through in `marks.toml`'s comment as `golden_belief_recall` is; call 35 stands
    as history.
49. **v10**: **corpus revision 4, read from keel-cloud's canon only.** The fixture fallback of
    2026-10-07 (`tests/fixtures/corpus-r3/`) is deleted with its directory; `load()` refuses a
    directory holding any file at a revision other than 4, by entry and by key, naming a
    revision-3 file as v9's. `rescore.py` refuses a v8 **or v9** bundle by name: corpus r4 carries
    no standing for thirteen of the dimensions a v9 bundle scored, so a v10 number for it would be
    fiction.
50. **v11** *(spec 031, 2026-10-09; keel-cloud 073, registry decision 15)*: **the registry is
    thirteen.** Invariants 1, 3 and 5 restated: thirteen keys, 4 / 3 / 6; `commercial.price` at
    commercial order 2, SHAPES, not `b2b_only` (asked of whoever pays), founder control
    `price_range` whose `periods` are exactly `month · year · one_off` (`PriceLadder.PERIODS`, a
    fifth-invariant fault otherwise), respondent control `price_ladder`, `ordinal_band`; Existing
    sacrifice asked as `branch_pick_amounts`; Ability to pay's rungs `existing_line ·
    new_line_signed_off · taken_from_other_spend · no_budget`. The nine deal-breakers and the
    `b2b_only` pair do not move; the calibrated set is eleven on B2C and thirteen on B2B, read.
51. **v11**: **corpus revision 5, read from keel-cloud's canon only.** `load()` refuses a directory
    holding any file at a revision other than 5, naming a revision-4 file as v10's. The founder's
    Price is `{low, high, period, currency}` -- a low of 1 to under 10,000, the high not below it, a
    period of the three, the market's currency -- or `unsure` (Mulch Run: LEFT_OUT); its plan row is
    the ladder's five bands around the low plus `would_not_pay` (`PriceLadder.bands`, mirrored as
    `corpus.price_ladder_codes`), and a row that disagrees is a refusal naming both; Existing
    sacrifice's kinds carry money · hours · count and its picks are `{currency, amounts}` on the
    row in the row's units; every fixed-code founder answer is one of the registry's codes.
52. **v11**: **the window is code's.** keel-cloud 072 composes the four windowed questions from
    fixed frames around one model-written clause. `option_validity` reads a Prevalence calibration
    entry's and the gate's **`event`** and holds it to E1-E3 as `WindowFrame.fault` does (no digit,
    number word or time word -- the window unit's words included; one clause of at most 25 words,
    no `?`, no sentence break; not opening with *in*, *how many*, *did you*, *out of*, *do you
    think*); a missing `event` is E2. Frequency over a window of more than one unit owes no
    question text, and a text written anyway is ignored, never a fault (keel-cloud D-7); a
    one-unit window keeps its model-written question. **C7 and R8 retire** from every check, and
    `RecallWindow.said` / `is_named_in` with them. `no_leak` sweeps the `event` clause where it swept
    the question.
53. **v11**: **Price is code's on both sides.** Its calibration entry owes its key (and its
    `respondent_note`) and nothing else: options are a C2 fault, a question is ignored; its
    respondent item owes its key, and nothing a model writes there is read. Both count once in
    `dimension_coverage` and `option_validity`; **neither is ever swept by `no_leak`**, and neither
    is Frequency over a framed window: there is no model text a reader is shown. The sweep
    denominators are read off the registry and the entry's window (the case's `swept`).
54. **v11**: **the money, the hint and the unit are structural** -- each an `option_validity`
    fault on the screen it is found on, mirrored from keel-cloud 073: W9 (`Wording.money`: a
    currency symbol, an ISO 4217 code in capitals, or an amount with a currency word) in any
    model-written question, event, option label or belief phrase; W7 (`Wording.tickAll`: *tick /
    select / choose all|every*, *pick all*, *all that apply(ies)*) in a question; U1 (an Existing
    sacrifice founder option but `none` without `unit` money · hours · count; a respondent
    distractor without its `units[i]`).
55. **v11**: **one name for the idea, one for the offer -- held only to a name the corpus
    records.** W3: every SOLUTION calibration question, every part-2 item and the reveal carry
    `solution_mechanism.short_name` verbatim; W8: every COMMERCIAL calibration question and every
    part-3 / decision-maker item, Existing sacrifice and Price aside, carry
    `interpretations.offer_name` verbatim (`Wording.carries`: case, accents, apostrophes,
    punctuation and a leading article free). The eval never takes a name from a live screen's
    answer (marks-v9 §1), and **revision 5 records neither**, so on r5 both are held to none --
    as keel-cloud holds a card confirmed before 072 -- the job is handed `null`, the validator the
    same mechanism and offer (never its Lullaby fixture's names), and the dry run prints *held to no
    name*. A name a later revision records is read with no code change. **Amended 2026-10-09,
    before any run of record** (keel-cloud 073 `ed581f8`, additive within revision 5): every r5
    entry now records both names (Lullaby's *a suggested reason for crying* / *something that helps
    at night*), so W3 and W8 hold to them on all seven; the job is handed them -- on the SOLUTION
    card, the respondents' mechanism, the COMMERCIAL persona map and, since the export names it,
    `offer_name` on every part-3 job -- and so is the validator.
56. **v11**: **the wording rules are reported, never marked.** `window-frame-design.md` §3.6-§3.8
    make S1, S2, W1, W2, W4, W5 and W6 instruction rules the eval counts and the applier never
    refuses; a mark the product does not enforce would be the ruler inventing a rule. Per question
    and item with model text, `score.py` counts its words and W1 (more than 20, or 25 with a scene
    sentence first), W2 (*do you think / believe*, founder side), W6 (second person, founder
    side), S1 (one sentence over 20 words with a clause in front of the question) and W5 (options
    over 8 words) into `totals.wording`; the report renders them and `judge()` reads none. S2 and
    W4 need a name or a jargon list the corpus does not carry: the register page's to read.
57. **v11**: **the brief's commercial figures are keel-cloud's.** Existing sacrifice's `observed`
    is `Figures.cost`'s shape with no hourly rate (the corpus records none, so hours are never
    priced): *a median £22 over three months*, the hours median apart (*; 11 hours*); Price's is
    `Figures.price`'s, *{inside} of {n} said it would be worth {floor} {period} or more*. Call 42's
    *£… per three months* is superseded for both. `brief_paragraphs` stays four per-case marks: B6
    (*will pay / will buy*) is the aggregate's rule, counted by `rule_refusal_rate` and -- refused
    twice -- scored as a fault on every mark (call 41).
58. **v11**: **`rescore.py` refuses every bundle below 11** by name: a v10 bundle answered without
    Price, without units and with the window in the model's own words, so a v11 number for it
    would be fiction. The only v11 number is a v11 run (`WHY=marks:11`, on hold by the founder).
59. **v12**: **the registry is thirteen, cost first.** Invariants 3, 5 and 6 restated (keel-cloud 074's
    `DimensionRegistry`, mirrored): `b2b_only` on **Purchase friction alone**; `b2b_link_only`
    (respondent side) on **exactly Ability to pay**; a `price_range` entry's periods are the five of
    `Period.wires` (`day · week · month · quarter · year`, fixed to the cost's); a `cost` entry names
    those five and the modes `AMOUNT · HOURS`; an entry is `derived` on both sides or neither, read by
    `cost_covers_price` and derived from registry keys; `branch_pick_amounts` yields a number, so
    Existing sacrifice is drawn as an `interval` (invariant 6). Three sets are read, never typed:
    *calibrated* (every entry less Purchase friction off B2B: 12 / 13), *answered* (calibrated less the
    derived one: 11 / 12 -- what the calibration job writes and its denominators) and *asked* (per link:
    `PRIMARY` less `b2b_only` and `b2b_link_only` ones, 3 / 3 / 4 after the gate; `COMMERCIAL_B2B` the
    commercial six). (keel-cloud 074, registry decision 16.)
60. **v12**: **corpus revision 6, read from keel-cloud's canon only.** `load()` refuses a directory
    holding any file at a revision other than 6, naming an r5 file as v11's. The founder's cost is
    `{mode, low, high, rate?, period, currency}` -- `AMOUNT`, or `HOURS` with a rate above 0 on a B2B
    entry only; low above 0, high not below it; one of the five periods; the market's currency -- or
    `unsure`, with the engine's belief sentence; Price's period is the cost's while both are stated;
    Ability to pay is recomputed (`price low / cost high` to `price high / cost low`, whole percent;
    `some_from_spend` when the range crosses 100%, else by the high end: under 50 `small_share`, up to
    100 `mostly_from_spend`, over `new_money`) and a file that disagrees is refused naming both;
    `unsure` exactly when the cost or the price is; every Existing sacrifice pick records its recall
    `period` (`week · month · quarter`); a B2B entry records `hourly_rate`, which the engine's input
    carries; a decision-maker on the `COMMERCIAL_B2B` link has no story and no chip and is ANCHORED by
    rule (keel-cloud 075).
61. **v12**: **the code-framed questions owe no model text.** keel-cloud composes Existing
    sacrifice's question and Price's and renders both inputs. On the calibration side Existing
    sacrifice owes its **options**: 4 to 6 kinds of cost, each with its `unit` money · hours · count
    (U1, the fixed *none* aside), a not-sure label refused (C3), **no belief phrase required or
    read**; any question text the model wrote is not read -- never a fault, never swept, never held to
    W7 / W9 / W8 (labels and phrases still carry W9). Price owes its key (call 53). Ability to pay is
    derived and **not in the job**: a result that includes it is a coverage fault (outside the slice),
    and the job's denominators are the answered set.
62. **v12**: **`W10`.** The part-3 Existing sacrifice question -- on either link -- carries the recall
    words of the founder's cost period verbatim (`Wording.carries`): a day or a week -> *last week*;
    a month -> *last month*; a quarter, a year or no cost estimate -> *the last three months*, because
    the amounts are normalised from them. The registry's respondent guidance names them through a
    `{cost_period}` placeholder the job is handed filled (respondent items only, as keel-cloud fills
    them; the calibration job's copy of the same guidance keeps the placeholder). A fault of
    `option_validity` on that item; measured by code, so it is in the denominator already counted.
63. **v12**: **the commercial slice is read as cost first.** The respondent plan is derived from the
    registry (`b2b_link_only` keeps Ability to pay off `PRIMARY`; a left-out derived answer drops its
    row on the B2B link too, as Mulch Run's does). Existing sacrifice's respondent control yields a
    number yet still owes **options** (the founder's labels plus 2-3 distractors, each with
    `units[i]`) -- never the null options of the scale, the number and the gate; Ability to pay's four
    rungs are the respondent's fixed codes, one label each. Sweep B reads a cost estimate's low and high
    (`RespondentQuestionsRules.numbers`).
64. **v12**: **the cost figures are keel-cloud's.** Existing sacrifice's `observed` is `Figures.cost`'s
    shape per the founder's period: *a median £35 a month*, and on B2C the people who gave only time
    apart (*; 4 lose only time: median 3.7 hours a month, valued getting them back at £20 to £50 a
    month, about £5.45 to £13.64 an hour*); the corpus records the total median only, so a B2B figure
    is the total alone, without keel-cloud's money-and-hours split (a deviation: a shorter figure is
    quoted inside the longer). Ability to pay's is `Figures.ability`, *{inside} of {n} already spend
    {price low} {period} or more*; Price's is call 57's in the founder's period. Call 57's *over three
    months* stands only where the cost was left out.
65. **v12**: **the time-only are reported, not marked.** A B2C respondent who gave only time (hours or
    a count, no money, no *Nothing*, no *Something else*) is not counted as £0: the corpus's standing
    records `time_only` and `time_only_hours`, `compare_correctness` marks `status` and `drift` as
    before, and the new fields are reported and diffed where the engine states them. Their Ability to
    pay reads from their Price band -- the engine's, never a copy here.
66. **v12**: **`rescore.py` refuses every bundle below 12** by name: a v11 bundle was answered with a
    founder Existing sacrifice tick list, a Price over `month · year · one_off`, Ability to pay as a
    model-written question and the recall period unnamed in the amounts question, so a v12 number
    for it would be fiction. The only v12 number is a v12 run (`WHY=marks:12`, on hold by the founder).
67. **v13**: **Existing sacrifice is code's whole on both screens.** keel-cloud 077 removes the kinds of cost
    (inference contract 8: the calibration option's `unit` and the respondent item's `units` are gone). The
    calibration job's Existing sacrifice entry is `key` + `respondent_note` -- options are refused with `C2`,
    as Price's are, and a question written anyway is not read; the respondent job's item is the `key`
    alone (`cost_total` is code-written, `registry.CODE_WRITTEN_RESPONDENT_CONTROLS`), so nothing a model
    writes there is read and the buyer's question -- not the model's -- is what `no_leak` never sweeps.
    **`W10` retires** (code writes the question in the recall words; `wording.recall_fault` is deleted,
    `recall_words` stays: the registry's `{cost_period}` is still filled with it) and **`U1` retires** (no
    unit to hold). The job's denominators are unchanged: Existing sacrifice is still one answered
    dimension and one asked item; only the sweeps lose it (call 63's `units[i]` rule goes with it).
68. **v13**: **corpus revision 7, read from keel-cloud's canon only.** `load()` refuses a directory holding
    any file at a revision other than 7, naming an r6 file as v12's. Existing sacrifice has no kinds: its plan
    row is `control: cost_total` with no `codes` and no `units`; the founder entry carries no `labels` or
    `units`; every pick is `{mode: AMOUNT | HOURS, value >= 0, currency, period}`, `{nothing: true, currency,
    period}` or `{chip}` (the r6 amounts collapsed by keel-cloud's 14 -> 15 upcaster: money summed; else
    hours summed; else *Nothing*; else *can't recall*) with the recall `period` of r6 kept; its standing
    records no `optionCounts`. Every other r6 check stands (the cost estimate, Price on the cost's period,
    Ability to pay recomputed, `hourly_rate`). No standing or verdict moved against r6, so
    `compare_correctness` is 108 of 108 on the 077 engine with the engine's input carrying the new picks.
69. **v13**: **the registry reader at `cost_total`.** Invariant 6's number-yielding respondent controls are
    `segmented_0_to_7`, `number_with_unit` and `cost_total` (`branch_pick_amounts` is gone and is refused: it
    is not number-yielding, and a cost whose respondent control is anything else fails invariant 5 "one
    total"); invariant 5 adds that a `cost` shape carries no `code_rule` (there are no kinds). The
    registry's `something_else` rule no longer names an amounts pick.
70. **v13**: **`rescore.py` refuses every bundle below 13** by name: a v12 bundle answered an Existing
    sacrifice of kinds with a unit each, a respondent tick list with `units[i]` and a part-3 question held to
    the recall words (W10) -- what corpus revision 7 and keel-cloud 077 read as one code-written total -- so
    a v13 number for it would be fiction. The only v13 number is a v13 run (`WHY=marks:13`). The brief's
    time-only figure (call 65, unchanged in kind) now reads the B2C `HOURS` totals: the median hours per
    the founder's period, valued by the median person's Price band.
71. **v14**: **the BRIEF result is a reading, not a paragraph.** keel-cloud 079 replaces
    `{"whatThisSays": string}` with the structured reading above; code's `BriefFacts` (decision, the
    three vectors' words, the money's symbol, the counted problem / solution / commercial lines, `targets`,
    `keys`, an optional `sharpest` split) is the model's input beside `beliefs` and `stories`, and a
    sentence is only ever *over* those facts. This eval builds `facts` from the corpus's own standings in
    the same shape (`instructions/brief_facts.py`): no `sharpest` and no `priceTable`, since the corpus
    records neither a cross-tab nor the ladder's rows -- `brief.md` makes both optional and the marks hold
    the result to exactly the facts it was handed.
72. **v14**: **five marks, each keel-cloud's `B7` clause restated.** `shape` (sentence objects, 400 / 13 /
    3 / 2 / 160, `sharpest` only with a split), `cites` (in `facts.keys`, scoped per section, one a sentence,
    two for `problem.infer`, test keys in `facts.targets`), `numbers` (every digit run in the facts' JSON,
    the market's currency symbol only, no digit or number word in a test), `quotes` (verbatim from that
    invitation's story), `bans` (`will pay` / `will buy`, `proves` / `proven` / `validated` / `will save` /
    `it works`, web addresses, participants' names -- the last checked here, the validator being handed
    none). `brief_paragraphs` is all five or nothing. `coverage`, `register`, `source_material` and the
    observed `verdict_phrasing` retire with the paragraph they read; the reading is rendered on
    `register.html` beside its facts.
73. **v14**: **`rescore.py` refuses every bundle below 14** by name: a v13 bundle answered the BRIEF screen
    with a `whatThisSays` paragraph over the vectors' standings, which contract 9 does not accept, so a v14
    number for it would be fiction. The only v14 number is a v14 run (`WHY=marks:14`).
74. **v15**: **corpus revision 8, read from keel-cloud's canon only; direction-aware verdicts.** `load()` refuses
    a directory holding any file at a revision other than 8, naming an r7 file as v13's / v14's. A standing's
    `drift` may be `stronger` (holding, at least half the supports beyond the founder) or `short` (not
    holding), beside `both` / `none`; `above` / `below` stay on Compatibility. A vector verdict may be
    `NOT_TESTED` (every deal-breaker left out; never a dimension status). `compare_correctness` is unchanged
    in kind -- the engine's output against the corpus -- and moves because both did. The BRIEF facts add
    `decision.split` (NOT_YET with the PROBLEM vector at PEOPLE_DISAGREE: a split, not a no) and
    `decision.notTested` (the vectors at NOT_TESTED, which make the label KEEP_INTERVIEWING unless the problem is
    not holding). `rescore.py` refuses every bundle below 15: a v14 number was scored against revision 7's
    expectations and would be fiction at 8. The only v15 number is a v15 run (`WHY=marks:15`).
75. **v16**: **the reveal is three lines, written with the mechanism.** The three screens' results moved (keel-cloud 084,
    contract 10): `occasion` on `CONTEXT_INTERPRET`, `idea_what` / `idea_how` / `idea_belief` on `SOLUTION_MECHANISM`,
    no `reveal` on `RESPONDENT_QUESTIONS`. The validator owns X3, L1-L4 and W3 for the lines; this repository adds
    no copy of them. The part-2 reveal W3 fault retires with the reveal (call 55's other half, the question stems'
    W3, stays). `rescore.py` refuses every bundle below 16. The only v16 number is a v16 run (`WHY=marks:16`).
76. **v17**: **Relative advantage is asked benefit first, and the respondent's item is code's.** keel-cloud 085 (registry 3,
    document 18, `CONTRACT_VERSION` 10 unchanged): the founder ticks one to four advantages, so the corpus's founder
    answer is a list (rule B, shape half in `corpus._check_benefit_first`; the counts are the engine's), and a person's
    pick is `{answer: positive | neutral | negative, advantages: [...]}`. The respondent RA item joins Price and
    Existing sacrifice in `registry.CODE_WRITTEN_RESPONDENT_CONTROLS` (`benefit_with_advantages`): the model's item is its
    key alone, nothing it writes is read, W3 / W7 / W9 and both sweeps skip it -- on the respondent side only (the
    founder question and options stay the model's, so `score.model_text` / `is_swept` read the control when
    `founder=False`). A registry that reads `benefit_first` on any other control, or whose founder control is not
    `multi_choice`, fails invariant 5. The corpus is revision 9; a revision-8 file is refused by name. The BRIEF facts
    add `solution.benefit`, counted off the picks the engine counts (anchored, no chip) and held to the standing's
    `n`. `rescore.py` refuses every bundle below 17. The only v17 number is a v17 run (`WHY=marks:17`).

77. **v18**: **registry 4: all thirteen decide** (keel-cloud 087 FR-001 / FR-002, D3). The registry is read with no
    `weight`; a registry carrying `weight`, `respondent.chips` / `codes` / `asked_in_v1`, `common.chips` /
    `something_else` or `answers.status_vocabulary` is refused as unknown-shaped (invariant 0), never read. The eight
    invariants are 087's: 1 keys; 2 one escape at most, only Importance's counts against, none on the gate or
    Commitment; 3 b2b; 4 `{value}` once in every template but the benefit list's; 5 codes (controls and rules
    087's, Prevalence's fifths, a list's `saves`, fixed answers unique with their supports, cost / price / derived /
    benefit); 6 interval iff numeric; 7 one gate; 8 every fixed answer set at most five answers of at most nine
    words. `DEAL_BREAKERS`, `deal_breakers()`, `FIXED_RESPONDENT_CODES`, `RESPONDENT_ESCAPES`,
    `CODE_WRITTEN_RESPONDENT_CONTROLS` and `names_the_offer` are deleted: every respondent word is code's.
78. **v18**: **corpus revision 10, read from keel-cloud's canon only** (087 *Corpus revision 10*). `load()` refuses
    any other revision by name (revision 9 is v17's). What is checked is `check_corpus_r10.py`'s shape half -- S, W
    (a window of at least two units, never one -- D13, so `RecallWindow` refuses a count below 2 and has no
    `CYCLES` / `SHIFTS`, and DRIFT #74 is closed by construction; an `occasion` of one to four words), L (each list
    against the registry's `saves`: count, words, `picked`, `phrase`, `asked`, the fixed `Nobody else`), R (each row's
    control, codes and one escape the registry's), A (a pick a code of its row, Importance two, an escape exactly its
    row's, no guessed flag) -- and r9's P / K / D / U / O; the recount is the engine's (`compare_correctness`).
    `expected` drifts are `both | none | stronger | short` (`above` / `below` went with `choice_majority`); a
    vector's `deciding` is any of its dimensions, `null` exactly when `NOT_TESTED`.
79. **v18**: **`spoken_form`, a deterministic mark** (the spoken guidelines §8; design §9 row 11). keel-cloud composes
    every respondent item and its spoken block by code and its `SpokenGuidelinesCorpusTest` writes them
    (`build/spoken-corpus.txt`); `instructions/cloud_corpus.py` runs that test (and 089's) once and
    `instructions/spoken.py` holds the record to §2-§5: `S1` stem at most 20 words, **25 on Existing sacrifice and
    Relative advantage** (keel-cloud 088 call 12: their unchanged frames carry an unbounded slot; held at 25 until
    the founder decides), `S2` anchor + stem the question and one anchor a part, `S3` at most five options (Price
    six), `S4` options at most nine words, `S5` parallel and exclusive, `S6` the §5 escape said last, `S7` / `S8` the §3
    count and options lines, `S9` the §4 transform by dimension, `S10` Commitment's step said once; and every corpus
    `asked` face `K2`-`K6`. One unit an item, one a face; 1.00 is every unit clean. The record is tested once; the
    renderer is keel-cloud's and is never copied here.
80. **v18**: **the three-word option floor binds the founder's words only** -- Importance's five and Current
    solution's five. The registry's fixed answers (*Yes*, *No*, *Yes, easily*) and Price's bands are the record
    (keel-cloud 088 call 14).
81. **v18**: **five corpus wording items are known, named and out of the denominator** (`spoken.KNOWN`): 06-repeatline's
    Commitment step *introduce you to the practice's IT supplier* (`S10`) and four Compatibility faces with no *you*
    (`K3`) -- 01-countly's (keel-cloud 088 saw it), 02-compliancelog's, 03-lullaby's and 07-mulchrun's. They are the
    next corpus revision's items (spec 040 follow-ups); a known item no longer found is a fault, so the ledger shrinks
    with the corpus.
82. **v18**: **the brief is answered, and its facts are compared** (keel-cloud 089 FR-001-FR-007). `brief_paragraphs`
    retires with `tiles`, `conclusion`, `infer`, `sharpest` and `next.sentence`; **`brief_answers`** is a case
    meeting seven marks, each a clause of `BriefReading.check` restated -- `shape`, `length` (the headline and each
    answer at most 2 sentences and 45 words), `cites`, `broke` (an answer whose stage broke cites what broke),
    `numbers`, `quotes`, `bans` -- proved equal to the real validator by `tests/test_instruction_brief_reading.py`.
    **`brief_facts`** is `DRY=1`-measurable: one check a card (`key`, `name`, `number`, `line`, `status`, the verdict
    half of `statusWords`) and one the pilot, keel-cloud's (`BriefFactsCorpusTest`, `build/brief-facts/<entry>.json`)
    against `instructions/brief_facts.py`'s reading of the corpus; the insight half of `statusWords` (spec 082's
    words), the decision, the vector words, `broke` and `notAsked` are reported, never marked. 94 checks on the
    seven entries.
83. **v18**: **the respondent job writes the gate's clause and nothing else** (keel-cloud 088 FR-002). Coverage is
    one `{key}` a planned item (R1); validity is the gate alone -- `event`, E1-E3 and E4 (framed, the gate and the
    Frequency question at most 20 words each); `no_leak` is sweeps A and B over that one clause on Part 1 of the
    primary link. Anything else a model writes on an item is not read and is never a fault. With no model question
    text anywhere, W3 / W7 / W8 (held by the validator as guards) and call 56's reported wording counts
    (`wording.reported`, `long_options`) retire from this repository.
84. **v18**: **eight screens: `ASKED` is a subject** (contract 12-13; routing v11 `asked: light`; `InferenceCharge` 7 is
    keel-cloud's and no mark reads it). One case a saved Compatibility and a saved Adoption friction list an entry
    (`<entry>/ASKED_COMPATIBILITY`, `<entry>/ASKED_ADOPTION_FRICTION`), handed the corpus's labels by index;
    coverage is K1 (every index once, no other), validity K2-K6 (`spoken.face_faults`, the same function the corpus
    faces are marked by), and the aggregate's K refusals are rules. A `BRIEF` case is handed keel-cloud's own facts
    for the entry (`cloud_corpus`) and, where a run has none (the unit fixtures), this repository's reading
    (`brief_facts.facts_for`); its meta says which.
85. **v18**: **the founder-lists job, marked by code** (`founder-lists.md`, keel-cloud 087 FR-012). Coverage is C1 (the
    vector's answered slice in order); validity is Prevalence's `event` (E1-E3) and five fifths (C2-C4), Frequency /
    Price / Existing sacrifice their key and note alone (C2), and every list dimension's draft held to `L1`-`L5`
    against the registry's `saves` -- **and a drafted `asked` face to `K2`-`K6`**, stricter than the aggregate's L4
    (words and no `?`), because a face the founder keeps is never re-phrased and reaches a stranger as drafted
    (keel-cloud 088 FR-003's vouching). `no_leak` sweeps A over the PROBLEM job's written words: Prevalence's clause
    and fifths, Importance's five, Current solution's phrase and outcomes.
86. **v18**: **an `L` refusal is a rule.** keel-cloud's `ScreenContractTool.VECTOR_RULE` lacks the letter, so a
    founder-lists refusal arrives `kind: shape`; `validate.fold_in` reads a shape refusal whose reason opens `L<n>: `
    as rule `L<n>` (keel-cloud follow-up: add `L` to the pattern).
87. **v18**: **`ASKED` is redrawn like the question screens** (call 41): keel-cloud 088's ladder queues its first repair
    on the class's own tier with the derivation text, which `runner.redraw_payload` mirrors; its second rung (one turn
    on `standard`) is not modelled -- the eval measures the instruction at the tier the table names.
88. **v18**: **`rescore.py` refuses every bundle below 18** by name: a v17 bundle answered model-written option sets, a
    respondent questionnaire and a BRIEF reading with tiles, against corpus revision 9 and the nine deal-breakers.
    The only v18 number is a v18 run (`WHY=marks:18`).
89. **v18**: **the journey's corpus-reading unit tests skip by name at revision 10.** `harness/vectors_script.py`'s
    results and typed inputs still write revision 9's shapes; re-pointing them (with the legs and the page objects)
    is the later journey spec's, once keel-web specs 7, 8 and 10 land. The keys table reads the eight-screen export
    and the one-unit branches are deleted.
90. **v18**: **`BRIEF` is a screen the validator takes, read off the call that judges it.** keel-cloud 086 deleted
    `ScreenContractTool`'s last `InferenceScreen.BRIEF` reference (a BRIEF case is any case neither a vector screen
    nor `INTERPRET`, judged by `BriefReading.check(...)`), so `validate.shapes_taken` read BRIEF as not taken and a real
    run would have left its refusal rate unmeasured. The call `BriefReading.check(` is now a marker beside the
    constant (`validate._CALL_MARKERS`); prose still never counts.

Calls 91-109 are spec 041's (the journey on corpus revision 10): they read no mark and live in
`specs/041-vectors-journey-r10/spec.md`, as spec 042's journey calls (116 on) live in its own.

110. **v19**: **corpus revision 11, read from keel-cloud's canon only** (keel-cloud 091 FR-G). `load()` refuses any other
    revision by name (revision 10 is v18's). What is checked is `check_corpus_r11.py`'s shape half: revision 10's S, W,
    L, R, A (call 78) and r11's two rules in L -- every `asked` face carries *you* / *your* (`K3`) and Commitment's step
    carries no *you* of its own (`S10`, since code says *would you {step}*). The unit fixtures are revision 11 (their
    faces already said *you* and their step none; nothing in `expected` moved) and `check_corpus_r11.py` prints OK for
    both. One standing moved on the corpus (05-paidly's Frequency median, 5 -> 2: months out of 3, not invoices out of
    7); no status, drift, count or verdict, so `compare_correctness` stays 108 of 108.
111. **v19**: **`S1` holds every stem to 20 words.** keel-cloud 091 FR-E shortened Relative advantage's frame (*On your
    last {occasion}, would {name} have made things better, or not?*) and made Existing sacrifice's step down until it
    fits, and its `SpokenGuidelinesCorpusTest` holds every item to 20; the 25-word allowance of call 79 and
    `spoken.LONG_FRAMES` are gone.
112. **v19**: **no corpus item is known apart.** Revision 11 rewrote the five items call 81 named (DRIFT #77, closed), so
    `spoken.KNOWN` is empty and `spoken_form` counts every composed item and every face -- 109 units on the seven
    entries. The ledger's machinery is kept (a known item no longer found would still be a fault); it has nothing to
    fire on.
113. **v19**: **an `L` refusal is a rule, as the validator reports it.** keel-cloud 091 FR-C added `L` to
    `ScreenContractTool.VECTOR_RULE` (DRIFT #76, closed), so `validate.fold_in` and `runner.should_redraw` read the
    report's `kind` as it is; call 86's reading of a shaped `L<n>` as a rule (`validate._reclassified`) is deleted, and
    `validate.vector_rule_letters` reads the pattern off the validator's source so a unit test holds the letter there.
114. **v19**: **`brief_facts` reads keel-cloud 091's words.** A card carries `keelBar` where Keel sets the bar --
    Importance *holds if at least 2 in 3 put it in their two*, Current solution *holds if at least 2 in 3 say today's
    way falls short (answers 3 to 5)*, absent on every other card and on a left-out one -- and it is one of the fields
    a card's check compares; on a B2C entry Ability to pay's line is *derived from cost and price: already lose your
    price or more*; `notAsked.why` is one house style (*it is derived from what they lose today and your price, so it
    was not asked*; *a person, not a business, buys it, so it was not asked*), reported. Buyer and payer's *of the k
    against, m said ...* is the insight half of `statusWords`, reported, never marked (call 82). Still 94 checks.
115. **v19**: **`rescore.py` refuses every bundle below 19** by name: a v18 bundle was scored against corpus revision 10,
    with the two frames held at 25 words and five corpus items named apart. The only v19 number is a v19 run
    (`WHY=marks:19`).
116. **v20**: **the reading marks retire, deleted, not skipped.** keel-cloud 104 deleted the BRIEF screen, so
    `instructions/brief.py` (`shape`, `cites`, `numbers`, `quotes`, `bans`, the headline's and the answers' marks and
    `brief_answers`), the `BRIEF` case kind and its context (`context.build_brief`, `brief_facts.beliefs_for` /
    `stories_for` / `targets_for`), decision 46's BRIEF redraw (`run.refused_twice`) and the register's paragraphs
    are gone; `brief_answers` is no longer a key of `marks.toml`, so a verdict cannot carry a value for it. The `brief`
    job class stays in the routing table (THEMES routes through it) and is tolerated as dormant: this eval sends no
    THEMES case (its fake is the stack's; `harness/interviewer_fake.themes`).
117. **v20**: **`report_overview` is the Overview, read twice.** `instructions/overview.py` draws, from one
    `BriefFacts`, what keel-web 077's Overview says: the verdict's words and its line (*{How sure}. {reason}* then
    *Every dimension holds.* or each failing dimension's *{name} is {status}*; on KEEP_INTERVIEWING *{n} people have
    answered.* and *A card needs 5 to say anything and 10 to be sure.*), the pilot tile (*k of n signed up* over
    *p% · per link*, or *None yet*), the price tile (*{edgeSaid} or more* over *half or more said so · {chose} of {n}
    decision-makers*, or *Not asked yet*), per stage the pill, the lead lines and every row (name, status word,
    *number line* or *nobody has answered this yet*), and the foot. One check a hero, a tile, a panel and the foot:
    keel-cloud's facts for the entry against this repository's reading (`brief_facts.facts_for`). `DRY=1`-measurable;
    a cloud that cannot be asked leaves it unmeasured, never zero. On a journey the same drawing, from the wire's
    `StandingsView`, is held to the page (`evals/report_marks.py`).
118. **v20**: **`rescore.py` refuses every bundle below 20** by name: a v19 bundle answered the BRIEF screen and was
    held to its reading marks. The only v20 number is a v20 run (`WHY=marks:20`).
119. **v20**: **`brief_facts` reads keel-cloud 103 / 104's numbers.** Compatibility's line is *could ...* for a *They
    could ...* condition, kept for *could ...*, else *said {condition}* (*said yes:* is gone); Purchase friction's
    number counts `yes_quick` + `not_needed` and its line is *did not need {step}, or it was quick*, so it falls when
    the bet fails like every other card; and `priceMedian` is one more check an entry, `{edgeSaid, chose, n}` from the
    entry's price picks over the founder's ladder (the highest edge with `chose * 2 >= n`; the corpus records the
    picks, so the table is recounted from them -- the one count here besides the pilot's), absent when nobody counted
    answered Price or no edge reaches half.
120. **v20**: **four report marks are the journey's, not the instruction eval's.** `report_insights`,
    `report_no_repeat`, `report_pilot` and `report_binding` read a page, which a model-screen run never has, so a row
    in `judge()` would fail every instruction-eval run by construction (call 13: unmeasured is not met). They are
    scored by `evals/report_marks.py` over a journey's record, owed whenever the record carries their subject, and
    fail the journey; `report_overview` is scored there too, page against wire. `report_binding` compares **tokens**
    (words of four letters or more, lower-cased, and every number), not sentences: CSS case and line breaks differ
    between a view and its sheet (spec 052 call 2).
121. **v21**: **`read` is a mark kind, reported and never gating.** Spec 078 FR-7: the two readers' scores (the
    founder-reader and the respondent-reader, Opus 5.5 at medium through the `claude` CLI, `quality/readers.py`) are
    read by `read_rows()` from the latest committed score file of each entry at the current `RUBRIC_VERSION` -- the
    five means, the flagged count, `score_pct`, `flagged_pct`, the reader -- into the scorecard's `read` block. A
    score file judges a back-test bundle's served words, walked on one cloud sha; an instruction-eval run judges the
    instructions on the golden corpus. They are not the same subject, so `read` is shown beside the marks and never
    joins `ROWS` or `passed`: a run without a score file is *not measured* there, and is not failed by it.
122. **v21**: **the readers' ruler is versioned apart.** `quality/rubric.py`'s `RUBRIC_VERSION` (1) moves with a
    criterion, an anchor, the booleans, the weak rule or `score_pct`, and `MARKS_VERSION` does not follow it: `read`
    shows only a file at the current `RUBRIC_VERSION` and names any other as *not measured: rubric version n*. Scores
    of two rubric versions are never averaged (spec 078 FR-1).
123. **v21**: **`rescore.py` still re-scores a v20 bundle.** v21 moves no row a bundle is scored on -- `read` is read
    from `quality/scores/`, never from the bundle -- so `OLDEST` stays 20 and a v20 scorecard re-scored at v21 is the
    same numbers with the `read` block beside them. Every bundle below 20 is refused as before.
124. **v22**: **`L1` and `L5` say keel-cloud's rules** (spec 093 FR-3). `L1` in keel-cloud 161's words: a blank
    Current solution phrase is *the phrase today's way is asked by, the act in the people's words ('checking for
    errors')*, and a drafted one that opens on *your way of* (any case, any spacing; `ItemFrames.bare`) is a fault --
    *write the act alone, in the people's words* -- as keel-cloud's applier refuses it once and then notes it. `L5`
    admits at most one `suggested` item on Purchase friction (a step Keel adds) and on Compatibility (the condition most
    likely to be missing, keel-cloud 121 FR-3, the founder's *"Agree."* of 2026-10-22), never on any other dimension --
    Adoption friction included (keel-cloud 161 FR-3). keel-cloud's `suggested_why` note is not restated (it is a note,
    never a fault the harness counts). Both read the draft alone, so a bundle's own `cases/**/envelope.json` is enough.
    **Amended by spec 112 FR-2 (keel-cloud 171 FR-2, 2026-10-30)**: `L5` admits one `suggested` item on Adoption
    friction too -- a one-time step the actor takes, last -- and there its missing `suggested_why` **is** a fault (171's
    breach: *the suggested step carries suggested_why -- what in the Answer or the idea calls for it, in one
    sentence*; Compatibility's stays the note above); `L1` on Adoption friction counts the founder's efforts, the one
    suggested step outside the 1 to 4 (*... besides the one suggested step*). At v24 (call 129).
125. **v22**: **`rescore.py` re-scores a v20 or v21 bundle at v22.** The rules above read the produced draft the bundle
    already holds, so `OLDEST` stays 20: a v21 scorecard re-scored at v22 moves only where a draft carried a suggested
    Compatibility condition (now met) or a phrase in Keel's old words (now an `L1`). Every bundle below 20 is refused as
    before.
126. **v22**: **an Adoption friction face is framed as keel-cloud frames it, and `K3` reads the framed line** (spec 093
    FR-4, FR-5; keel-cloud 163). `spoken.framed` is `ItemFrames.adoptionFriction` as `AskedRules.framed` reads it: a
    clause the model opens on *would you* is said *You'd ...* (its *would you* one word), a leading clause after it
    while the whole fits 20, *you had to* as *you would have to*, then *Would you do that, or not?* -- so `K2` counts
    the words the stranger hears (the harness counted the model's *would you* and the frame's: one word more than the
    cloud, 163's *What did not hold*). `K3` on Adoption friction reads the clause as framed: the frame's *Would you*
    addresses the person, so a base-form clause (*open the app before picking the baby up*) is said to the stranger;
    one whose subject is someone or something else (*the cry ...*, *the room ...*, `THIRD_PERSON_OPENERS`) still
    faults. Compatibility's `K3` is unchanged (the clause carries *you / your*). 163's 12-word clause rule is the
    registry's option rule and is not restated. A v20 or v21 bundle re-scores at v22 (call 125). **Amended by spec 112
    FR-1 (keel-cloud 171 FR-4b, 2026-10-30)**: the frame `spoken.framed` reads is now `ItemFrames.adoptionFrame` --
    *To use it, you'd {step}. Would you do that, or not?* around the **whole** step (`spoken.step`: a leading *would
    you* / *you'd* / *you would* / *you had to* / *have to* / *need to* dropped, a past or a participle in base form, a
    leading clause moved to the end in the present, a clause's own *to ..., you'd* purpose dropped), no give-way; 123's
    *You'd ...* and *you had to* -> *you would have to* are retired. `K3` reads the step after the frame's *you'd*.
    171's clause is at most 10 words (the option rule's, `spoken.ADOPTION_CLAUSE_MAX_WORDS`, not restated as a fault):
    an 11-word clause is 21 framed, a `K2`. At v24 (call 129).
127. **v23**: **a drafted list is held to the draft's rule, not the save's** (spec 091 FR-1). `L1` on Importance's
    draft (`rival_list`) reads the job's `answers` slot: `{}` (the seed-time job, every screen this eval runs) is the
    problem itself alone -- exactly one item; the founder's Answer for it is the problem itself and the difficulties the
    Answer names, Keel adding none (*an answer naming one difficulty yields two items*) -- exactly 1 + N, at most
    `saves.max_items`; an Answer naming none (*Nothing else*) leaves the own item. N is read off the Answer's parts
    (`score.named_difficulties`: a line, a bullet, a `;` or a `,` apart, a serial list's last *and* / *or*; a lone *and*
    is one difficulty, grammar only, no trade words). `saves.min_items` is the save's rule and is applied where a saved
    list is checked (`corpus._check_list`: the corpus's recorded lists), never to a draft. Every other list dimension's
    draft keeps the registry's bounds. keel-cloud's applier (spec 097 F9) bounds the redraft 1 to `max_items`; the
    harness holds the founder-lists rule's exact count, so a draft that writes fewer than its Answer names, or adds to
    it, is faulted -- by the draft's rule, named.
128. **v23**: **`rescore.py` re-scores a v20, v21 or v22 bundle at v23.** Call 127 reads the produced draft and the job's
    `answers` the bundle already holds (the case's sent context, else the seed-time job's `{}`), so `OLDEST` stays 20: a
    v22 scorecard re-scored at v23 moves only where Importance's draft count moved (a one-item seed-time draft is now
    valid; a draft that added rivals with no Answer is now an `L1`). Every bundle below 20 is refused as before.
129. **v24**: **an Adoption friction face and draft are read as keel-cloud 171 writes them** (spec 112 FR-1, FR-2).
    `K2` frames a face as `ItemFrames.adoptionFrame` does -- *To use it, you'd {step}. Would you do that, or not?*
    around the whole step in base form (`spoken.step`, call 126's amendment) -- so a clause of 11 words is 21 framed
    and a fault (171's option rule: at most 10); `K3` reads the step after the frame's *you'd*. `L5` admits one
    `suggested` item on Adoption friction (a one-time step the actor takes, last) and faults one without
    `suggested_why`; `L1` counts Adoption friction's items less that one (call 124's amendment). The corpus did not
    move: five golden faces (01, 02, 03, 04, 06) are 11 or 12 words and now `K2`s -- the cloud never refuses a stored
    row, so these are the corpus's age, a revision owed by keel-cloud, never softened here.
130. **v24**: **`rescore.py` re-scores a v20 to v23 bundle at v24.** Call 129 reads the faces and the drafts' flags the
    bundle already holds, so `OLDEST` stays 20: a v23 scorecard re-scored at v24 moves only where an Adoption friction
    face is 11 words or more (now a `K2`) or a draft marked an Adoption friction step (now valid with its why, an `L5`
    without). Every bundle below 20 is refused as before.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

MARKS_VERSION = 24

DEFAULT_MARKS_PATH = Path(__file__).parent / "marks.toml"

#: The ten marks of `marks.toml` at v20 (calls 79, 82, 116, 117): v19's ten without `brief_answers` (retired with the
#: BRIEF screen) and with `report_overview` (the Overview, at zero spend). `golden_belief_recall` (call 29),
#: `brief_paragraphs` (call 82) and `brief_answers` (call 116) are retired: **not** keys, so a verdict cannot carry a
#: value for any of them. The four journey report marks are `evals/report_marks.py`'s (call 120), never keys here.
DEFAULTS = {
    "dimension_coverage": 1.00,
    "option_validity": 1.00,
    "no_leak": 1.00,
    "anchoring_accuracy": 0.90,
    "compare_correctness": 1.00,
    "rule_refusal_rate": 0.02,
    "shape_refusals": 0,
    "spoken_form": 1.00,
    "brief_facts": 1.00,
    "report_overview": 1.00,
}

#: The rows `judge()` returns, in the order the report shows them.
ROWS = ("dimension_coverage", "option_validity", "no_leak", "anchoring_accuracy",
        "compare_correctness", "refusals", "shape_refusals", "spoken_form",
        "brief_facts", "report_overview")


#: Spec 078 FR-7 (call 121): where the `read` mark kind is read from -- committed score files, never a run.
READ_SCORES_DIR = Path(__file__).resolve().parent.parent / "quality" / "scores"


def read_rows(entry_ids, scores_dir: Path | str | None = None) -> dict:
    """The `read` block of a scorecard (calls 121, 122): per entry, the latest committed score file at the current
    `RUBRIC_VERSION` -- `{measured: True, file, scope, means, flagged, screens, score_pct, flagged_pct, reader}` -- or
    `{measured: False, why}`. Reported beside the marks; never a row of `judge()`."""
    import json

    from quality import rubric as rubric_mod

    root = Path(scores_dir) if scores_dir else READ_SCORES_DIR
    out = {}
    for entry_id in sorted(set(entry_ids)):
        files = []
        for path in sorted((root / entry_id).glob("*.json")) if (root / entry_id).is_dir() else []:
            try:
                files.append((path, json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, ValueError):
                continue
        current = [(p, f) for p, f in files if f.get("rubric_version") == rubric_mod.RUBRIC_VERSION
                   and not f.get("partial")]
        if not current:
            other = sorted({f.get("rubric_version") for _, f in files}, key=str)
            out[entry_id] = {"measured": False,
                             "why": (f"not measured: rubric version {other}, not {rubric_mod.RUBRIC_VERSION}" if other
                                     else "not measured: no score file for this entry")}
            continue
        path, latest = max(current, key=lambda pf: (pf[1].get("scored_at") or "", pf[0].name))
        overall = (latest.get("summary") or {}).get("overall") or {}
        out[entry_id] = {"measured": True, "file": path.name, "scope": latest.get("scope") or "ALL",
                         "rubric_version": rubric_mod.RUBRIC_VERSION, "means": overall.get("means"),
                         "flagged": overall.get("flagged"), "screens": overall.get("screens"),
                         "score_pct": overall.get("score_pct"), "flagged_pct": overall.get("flagged_pct"),
                         "insights_pct": overall.get("insights_pct"),
                         "reader": latest.get("reader")}
    return out


def load(path: Path | str | None = None) -> dict:
    path = Path(path) if path else DEFAULT_MARKS_PATH
    if not path.is_file():
        raise FileNotFoundError(f"no marks file at {path}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    marks = dict(DEFAULTS)
    marks.update(raw.get("marks") or {})
    return marks


def _at_least(value, mark) -> bool:
    return value is not None and value >= mark


def judge(totals: dict, marks: dict) -> dict:
    """Each of the ten marks against its number. A run passes only if all ten are met.

    Every row is `{value, mark, measured, met}`, and **an unmeasured mark is not a met mark**
    (judgement call 13): a `None` fails, a refusal count nobody asked for fails, a compare the
    engine never ran fails. `refusals` carries its rate beside the count (call 22, call 36).
    """
    def row(name, value, measured, met, **extra):
        measured = bool(measured) and value is not None
        return {"value": value, "mark": marks[name if name != "refusals" else
                                              "rule_refusal_rate"],
                "measured": measured, "met": bool(measured and met), **extra}

    coverage = totals.get("dimension_coverage")
    validity = totals.get("option_validity")
    leak = totals.get("no_leak")
    accuracy = totals.get("anchoring_accuracy")
    compare = totals.get("compare_correctness")
    spoken = totals.get("spoken_form")
    facts = totals.get("brief_facts")
    overview = totals.get("report_overview")
    measured = bool(totals.get("refusals_measured"))
    refusals = sum((totals.get("refusals_by_rule") or {}).values())
    # v6 (call 22), v9 (call 36): a rate over the answers the aggregate judged -- `refusals_shown`,
    # accepted plus refused -- never over case-runs that were never shown to it.
    shown = int(totals.get("refusals_shown") or 0)
    rate = (refusals / shown) if (measured and shown) else None
    shape = totals.get("shape_refusals")

    results = {
        "dimension_coverage": row("dimension_coverage", coverage, coverage is not None,
                                  _at_least(coverage, marks["dimension_coverage"])),
        "option_validity": row("option_validity", validity, validity is not None,
                               _at_least(validity, marks["option_validity"])),
        "no_leak": row("no_leak", leak, leak is not None, _at_least(leak, marks["no_leak"])),
        "anchoring_accuracy": row("anchoring_accuracy", accuracy, accuracy is not None,
                                  _at_least(accuracy, marks["anchoring_accuracy"])),
        "compare_correctness": row("compare_correctness", compare,
                                   totals.get("compare_measured"),
                                   _at_least(compare, marks["compare_correctness"])),
        "refusals": row("refusals", rate, measured and shown,
                        rate is not None and rate <= marks["rule_refusal_rate"],
                        count=refusals if measured else None,
                        shown=shown if measured else None),
        "shape_refusals": row("shape_refusals", shape if measured else None, measured,
                              shape is not None and shape <= marks["shape_refusals"]),
        "spoken_form": row("spoken_form", spoken, totals.get("spoken_measured"),
                           _at_least(spoken, marks["spoken_form"])),
        "brief_facts": row("brief_facts", facts, totals.get("brief_facts_measured"),
                           _at_least(facts, marks["brief_facts"])),
        "report_overview": row("report_overview", overview, totals.get("report_overview_measured"),
                               _at_least(overview, marks["report_overview"])),
    }
    results["passed"] = all(results[name]["met"] for name in ROWS)
    return results
