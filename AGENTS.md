# AGENTS.md

keel-e2e-eval: the referee. It stands the whole connect stack up locally and proves the four
applications (keel-cloud, keel-web, keel-runtime, keel-connect-skill) agree — with each other,
and with the journey. It never talks to keel-skill or the retired agent-protocol/relay surfaces
(archived 2026-09-03, `runs/DRIFT.md`'s dated retirement note); no Prism, ever.

**No LLM except in four named places** (amended 2026-09-06, spec 009; amended again
2026-09-10, spec 016; the third **widened**, not multiplied, by spec 019; the fourth argued for by spec 048). Naming them is the
point: everything not named here stays deterministic, and a fourth would have to be argued for and
added to this line rather than quietly written — which is exactly how the third arrived.
- **S-004**, *the stranger who gives orders* (`evals/test_s004_stranger_who_gives_orders.py`,
  spec 008) — opt-in through `make eval-live`, deselected from `make eval`/`make eval-all`.
- **The instruction eval** (`instructions/`, spec 009) — `make instruction-eval`, needing no stack
  at all, a dependency of nothing, and collected by no pytest run. It scores keel-cloud's
  inference-instruction prose against a frozen golden corpus, and its rubric is versioned as
  `instructions.marks.MARKS_VERSION`, separately from `evals/policy.py`'s `POLICY_VERSION`, so the
  two can never be confused.
  **It spends the founder's money and runs only for a named event** (keel-cloud
  `canon/designs/model-routing-design.md` §7.1; `instructions/why.py`): `WHY=instruction:…`,
  `prompt:…` or `contract:…` earns one screen, `WHY=new-model:<host>:<model>` and
  `WHY=marks:<version>` earn the full run, and a code change earns nothing. Never run it on a
  schedule, in CI, or "to be sure".
  **`marks:` is the fifth event** (spec 025 FR-023, 2026-09-30), and it is full-run only. The other
  four name a change to the *subject*; this one names a change to the **ruler**. The standing gate
  reads *green at the current `MARKS_VERSION`*, so a rubric that moved has no run of record at all
  until one is spent, and a screen is one entry and cannot be one. The policy widened by one named
  event, in the open, which is the amendment shape this document asks for — it did not loosen.
  **`MARKS_VERSION` 21** (spec `078-question-quality-readers`, 2026-10-28) is the gate as written, and **there is no
  run of record until `WHY=marks:21` is spent -- the certificate is the founder's word only; never run or propose it**.
  It adds the `read` mark kind beside `no_leak` (calls 121-123): the question-quality readers' means, flagged
  count and `score_pct`, read from the latest committed score file under `quality/scores/` at `RUBRIC_VERSION`,
  reported in every scorecard and *not measured* without one -- never a `judge()` row, never gating; no `[marks]`
  number moved and `rescore.py` still re-scores a v20 bundle. What follows is v20's account, history since 2026-10-28.
  **The question-quality readers** (`quality/`, spec 078) widen this place rather than add a fifth: they are the
  judge's own door (`instructions/judge.py`'s argv, `judge_env`) with `--model claude-opus-5-5 --effort medium`
  (`quality/readers.toml`), a ruler and never a subject, and their scores are this rubric's `read` kind. `make
  read-screens RUN=<bundle>` reads one back-test bundle's served screens as text (the founder-reader handed the
  entry's `.sources.md`, the respondent-reader the person the walk took on each link), one bounded call a screen, every
  prompt and answer recorded under `runs/`, the score file written to `quality/scores/` and committed; it refuses on a
  missing `claude` binary or a failed one-word probe and reads no key. **Paid (the founder's plan), run on his word
  only** -- never in `make eval` / `make unit`, the matrix, a checker or a schedule (`quality/` has no `test_*.py`;
  `make read-table` is free and calls nothing).
  **`MARKS_VERSION` 20** (spec `052-report`, 2026-10-17) was the gate as written, and **there was no run of record
  until `WHY=marks:20` was spent -- never run**. keel-cloud
  104 (keel-cloud-docs `9a033fe`, contract 19's standings side) deleted the BRIEF screen, so `brief_answers` and its
  seven reading marks retire (call 116); `brief_facts` gains the price median and 103's two card lines (call 119);
  `report_overview` is born at zero spend (the Overview keel-cloud's facts draw against the corpus's, call 117); four
  journey marks -- `report_insights`, `report_no_repeat`, `report_pilot`, `report_binding` -- are
  `evals/report_marks.py`'s, never rows of `judge()` (call 120). At zero spend against `9a033fe` (a fresh
  `BriefFactsCorpusTest`): `brief_facts` 101 of 101, `report_overview` 49 of 49. Corpus revision 11 unchanged. **Since
  spec `053-corpus-in-dollars`** (keel-cloud 105, keel-cloud-docs `7e64f20`) v20 reads corpus **revision 12** -- the six
  GB entries in the US and in dollars, the same digits, no number moved; a revision-11 file refused by name -- and the
  zero-spend rows hold there: `compare_correctness` 108 of 108, `spoken_form` 109 of 109, `brief_facts` 101 of 101,
  `report_overview` 49 of 49. What follows is v19's account, history since 2026-10-17 (never run).
  **`MARKS_VERSION` 19** (spec `042-contract-14-r11`, 2026-10-14) was the gate as written, and **there was no run
  of record until `WHY=marks:19` was spent -- never run**. keel-cloud 090 / 091 (merged at keel-cloud-docs `c432c1d`: `CONTRACT_VERSION` 14, the lock one
  RESPONDENT_QUESTIONS job of 35, corpus revision 11) moved four calls under unchanged numbers (110-115): the corpus is
  revision 11 (r10 refused by name; DRIFT #77's five words fixed, 05-paidly's Frequency in months out of 3; keel-cloud 092 /
  093 at `7850360` -- contract 15, charge 8 -- moved no screen schema and no instruction, so v19 stands, spec 043 call 135),
  `spoken_form` holds every stem to 20 with `spoken.KNOWN` empty, an `L` refusal is read as the validator's rule
  (DRIFT #76 closed; call 86's reclassification deleted), and `brief_facts` reads 091's `keelBar` and words. At zero
  spend against `c432c1d`: `compare_correctness` 108 of 108, `spoken_form` 109 of 109, `brief_facts` 94 of 94. What
  follows is v18's account, history since 2026-10-14 (never run).
  **`MARKS_VERSION` 18** (spec `040-marks-v18`, 2026-10-14) was the gate as written, and **there was no run
  of record until `WHY=marks:18` was spent -- never run**. keel-cloud 087 / 088 / 089 (merged at keel-cloud-docs `7b151f9`: registry `VERSION` 4,
  document 20, `CONTRACT_VERSION` 13, routing v11 `asked: light`, charge 7) are the October redesign: all
  thirteen dimensions decide (no weight anywhere), corpus revision 10 (lists, fixed answers, one escape, no
  one-unit window -- DRIFT #74 closed), the model writes the founder lists (`founder-lists.md`), the gate's
  clause and, on an **eighth screen**, the stranger's `asked` faces (`asked.md`), and the brief answers over
  cards. Ten marks: v17's eight with `brief_paragraphs` become `brief_answers`, and two deterministic ones
  measured at zero spend -- `spoken_form` (every composed corpus item held to the spoken-question
  guidelines, read from keel-cloud's own `SpokenGuidelinesCorpusTest` output) and `brief_facts` (keel-cloud's
  `BriefFactsCorpusTest` cards and pilot against this repository's reading). `rescore.py` refuses every
  bundle below 18 (calls 77-90). `DRY=1` against `7b151f9` measures `compare_correctness` 108 of 108,
  `spoken_form` 104 of 104 (five corpus wording items named apart, DRIFT #77) and `brief_facts` 94 of 94.
  What follows is v17's account, history since 2026-10-14 (never run).
  **`MARKS_VERSION` 17** (spec `038-advantage-benefit-first`, 2026-10-12) was the gate as written, and
  **there is no run of record until `WHY=marks:17` is spent; never run or propose it**. keel-cloud 085
  (merged at `b8a4eed`; registry `VERSION` 3, document 18, `CONTRACT_VERSION` stays 10) asks Relative advantage benefit
  first: the founder ticks one to four advantages, the respondent's one item is code's whole (the model's
  `RESPONDENT_QUESTIONS` result carries the key alone, as Price does), the corpus is revision 9 (three drifts moved, no
  status), the BRIEF facts carry `solution.benefit`, and `rescore.py` refuses every bundle below 17 (call 76).
  `DRY=1` against keel-cloud 085 measures `compare_correctness` 108 of 108. What follows is v16's account, history
  since 2026-10-12 (never run).
  **`MARKS_VERSION` 16** (spec `037-reveal-three-lines`, 2026-10-12) was the gate as written, and
  **there is no run of record until `WHY=marks:16` is spent; never run or propose it**. keel-cloud 084
  (merged at `fc12b49`; inference `CONTRACT_VERSION` 10, document 17) writes the reveal as three lines with the
  mechanism: `occasion` on CONTEXT_INTERPRET, `idea_what` / `idea_how` / `idea_belief` on SOLUTION_MECHANISM, no
  `reveal` on RESPONDENT_QUESTIONS (R6 gone). The validator owns the new rules; this repository's part-2 reveal W3
  fault retires; `rescore.py` refuses every bundle below 16 (call 75). `DRY=1` against keel-cloud 084 measures
  `compare_correctness` 108 of 108. What follows is v15's account, history since 2026-10-12 (never run).
  **`MARKS_VERSION` 15** (spec `036-direction-aware-verdicts`, 2026-10-12) was the gate as written, and
  **there is no run of record until `WHY=marks:15` is spent; never run or propose it**. keel-cloud 082
  (direction-aware verdicts; merged at `438807d`; registry `VERSION` 2, contract stays 9) makes a dimension
  with a supporting side one-sided: the corpus is revision 8 (drift `stronger` / `short`, 28 rows moved, people
  and picks not), the BRIEF facts carry `decision.split` / `decision.notTested`, `rescore.py` refuses every
  bundle below 15 (call 74). `DRY=1` against keel-cloud 082 measures `compare_correctness` 108 of 108. What
  follows is v14's account, history since 2026-10-12 (never run).
  **`MARKS_VERSION` 14** (spec `034-brief-infer-recommend`, 2026-10-11) was the gate as written, and
  **there was no run of record until `WHY=marks:14` was spent**. keel-cloud 079
  (the brief infers and recommends; merged at `706015c`; inference `CONTRACT_VERSION` 9, project
  document 16) turned the BRIEF result from one `whatThisSays` paragraph into a structured reading
  over code's `facts` (context `project_name, market, context, facts, beliefs, stories`). The ruler
  follows (calls 71-73): five reading marks (`shape`, `cites`, `numbers`, `quotes`, `bans`) restate
  keel-cloud's `BriefReading.check` and are proved equal to the real `screenContracts validate` by
  `tests/test_instruction_brief_reading.py`; the corpus stays revision 7; `rescore.py` refuses every
  bundle below 14. `DRY=1` against keel-cloud 079 measures `compare_correctness` 108 of 108. What
  follows is v13's account, history since 2026-10-11 (never run).
  **`MARKS_VERSION` 13** (spec `033-buyer-cost-total`, 2026-10-10) was the gate as written, and
  **there was no run of record until `WHY=marks:13` was spent** (v12's was on hold by the founder). keel-cloud 077 (the buyer's cost is one total; branch
  `077-buyer-cost-total` at `dc13341`; inference `CONTRACT_VERSION` 8) removed the kinds of cost:
  the respondent answers Existing sacrifice with one number, an amount or hours, over the founder's
  recall period (`cost_total`). The ruler follows (judgement calls 67-70): Existing sacrifice owes
  the model nothing on either screen, as Price does (the calibration entry is its key and note,
  options are `C2`; the respondent item is its key alone), `W10` and `U1` retired, the registry's
  cost carries no `code_rule`, corpus revision 7 (an r6 file refused by name as v12's; no standing
  or verdict moved), the brief's time-only figure reads the B2C `HOURS` totals, and `rescore.py`
  refuses every bundle below 13. `DRY=1` against keel-cloud 077 measures `compare_correctness` 108
  of 108 and prints every other mark's denominator (calibration 80, respondent 81, `no_leak` 109 an
  N: the buyer's Existing sacrifice is no longer swept). What follows is v12's account, history
  since 2026-10-10 (never run).
  **`MARKS_VERSION` 12** (spec `032-cost-first-price`, 2026-10-10) was the gate as written, and
  **there is no run of record until `WHY=marks:12` is spent -- that run is on hold by the
  founder; never run or propose it**. keel-cloud 074 (cost first; branch `074-cost-first-price`,
  merging 075) moved the subjects' words: the founder estimates what the problem costs (Existing
  sacrifice is a `cost_estimate`, read by `interval_contains_median`), prices it for that same period,
  and Ability to pay is **derived** from the two and never asked (`cost_covers_price`,
  `b2b_link_only`). The ruler follows (judgement calls 59-66): the registry at thirteen in its
  cost-first shape (invariants 3, 5, 6), corpus revision 6 (an r5 file refused by name as v11's),
  Existing sacrifice owing its kinds with units and no text, Price its key, Ability to pay out of the
  calibration job (the denominator is the *answered* set), `W10` holding the part-3 Existing sacrifice
  question to the recall words, the brief's cost and ability figures keel-cloud's own with the B2C
  time-only people reported apart, and `rescore.py` refusing every bundle below 12. `DRY=1` against
  keel-cloud 074 measures `compare_correctness` 108 of 108 and prints every other mark's denominator
  (calibration 80, respondent 81, `no_leak` 116 an N). What follows is v11's account, history since
  2026-10-10 (never run).
  **`MARKS_VERSION` 11** (spec `031-window-frame-and-price`, 2026-10-09) was the gate as written,
  and **there is no run of record until `WHY=marks:11` is spent — that run is on hold by the
  founder; never run or propose it**. keel-cloud 072 (the window frame) and 073 (Price), on the
  stacked branch `073-price`, moved the subjects' words; the ruler follows (judgement calls 50-58):
  the registry at thirteen (4 / 3 / 6, Price back as SHAPES over `month · year · one_off`), corpus
  revision 5 (a founder price per entry, amounts by unit; an r4 file refused as v10's), Prevalence
  and the gate read as an `event` clause held to E1-E3 with C7 / R8 retired, Price code's on both
  sides and never swept, W7 / W9 / U1 structural and W3 / W8 held only to a name the corpus records
  (every r5 entry records both since 073 `ed581f8`), S1 / W1 / W2 / W5 / W6 reported and never marked (`instructions/wording.py`
  mirrors keel-cloud's `WindowFrame` and `Wording`), the brief's two commercial figures keel-cloud's
  own, and `rescore.py` refusing every bundle below 11. `DRY=1` against keel-cloud 073 measures
  `compare_correctness` 104 of 104 and prints every other mark's denominator. What follows is v10's
  account, history since 2026-10-09 (never run).
  **`MARKS_VERSION` 10** (spec `030-marks-v10-deal-breakers`, 2026-10-09) was the gate as written,
  and had no run of record before v11 superseded it. keel-cloud 071 cut the registry
  to twelve dimensions (4 / 3 / 5, nine deal-breakers that can each fail, the `b2b_only` pair) and
  the corpus to revision 4; the ruler follows (judgement calls 46-49): eight invariants, every
  denominator read off the registry and the entry's persona (calibration 10 on B2C, 12 on B2B;
  part 3 of a B2B study is the decision-maker's link only), `no_claim_words` retired with
  `BAR_SET` and `NOT_TESTED_BY_DESIGN` (`brief_paragraphs` is all four), the corpus read from
  keel-cloud's canon and nowhere else (`tests/fixtures/corpus-r3/` deleted), and `rescore.py`
  refusing every v8 and v9 bundle by name. `DRY=1` against keel-cloud 071 measures
  `compare_correctness` 97 of 97 and prints every other mark's denominator. What follows is v9's
  account, history since 2026-10-09.
  **`MARKS_VERSION` 9** (spec `029-marks-v9-vectors`, 2026-10-07) was the gate as written until its
  run of record was spent: eight subjects (three interpretation screens rendered and never scored,
  calibration and respondent questions scored by code against keel-cloud's exported dimension
  registry, one read a gate story, `COMPARE` shelled to keel-cloud's engine at zero spend, one brief
  a project), eight marks (`marks.toml`; `golden_belief_recall` retired with `align.py`), the
  corpus at revision 3, `rescore.py` refusing every v8 bundle by name, and `MODELS=exported`
  refusing until the exported table carries `context`, `calibration` and `respondent`. `WHY=marks:9`
  is the run of record's event; nothing here changed `why.py`. **The v9 run of record was
  `runs/20261008T194906Z-instructions`** (2026-10-08, Claude, Sonnet 5.5 medium + Haiku 4.5, 414
  cases, $19.75; history -- v10 refuses to re-score it), re-scored under judgement call 44 and accepted by the founder as the certificate
  (decision 48); every mark met. `runs/` is gitignored: its `scorecard-v9.json` is sha256
  `1cae4bb5b85bfeb47dedfb54b51ea9d06361f79bfecbee78cd21884445e81dea`.
- **S-012**, *the journey through a host* (`evals/test_s012_journey_through_a_host.py`, specs
  `016-copilot-e2e`, `019-journey-through-a-host` and `021-short-journey`) — the third, and here
  is the argument for it. keel-cloud `canon/designs/keel-skill-design.md` §5.5 makes a host "supported" only when four
  things are true, and **two of them are this repository's**: S-001 green *through that host*, and
  the instruction eval's run of record green on it. The second has been measurable since spec 014.
  The first never has: no scenario here had ever let an agent host load the skill and decide for
  itself to run it, and the acceptance bed that writes `copilot -p "keel connect"` has skipped
  itself in all four of its run records for want of a `COPILOT_GITHUB_TOKEN` the founder does not
  use. A gate with a part nobody can measure is not a gate. So S-012 is live for the same reason
  S-004 is — **the thing under referee is a model's behaviour, and no script can stand in
  for it** — and it is opt-in through `make eval-live`, deselected from `make eval`/`make
  eval-all`, and skipped by name with its reason when no usable host CLI is there. It runs the
  host twice as a *host* (the two `<cli> -p "keel connect"` legs) and then as a *thinker* (the
  journey keel-runtime hands it), and every assertion about the host leg is made against the
  **runtime's own artefacts**, never against what the model said.

  **It is one scenario, not two.** Spec 019 parameterised it by host — `make eval-live K=s012
  HOST=claude|copilot`, default `copilot` — because keel-cloud `canon/designs/e2e-matrix-design.md`
  §5.1 makes the host one of the matrix's three axes and *"the scenario each cell runs is S-001,
  the founder's journey, through the host"*. That widens a named place; it does not add one. A
  second live scenario would still have to be argued for here.

  **And it is one scenario at four doors** (spec 024). Three of them are a founder's own agent
  CLI. The fourth is not a host at all: keel-cloud `canon/designs/ai-credits-design.md` §6 --
  *"The door decides the AI"* -- so a founder who signs up with Google at keel-web's `/signup`
  runs on **Keel's** AI, with no CLI to install, no skill to load, no device to approve and no
  runtime anywhere, and keel-cloud answers every job in process on its own Anthropic account.
  `make keels-ai` / `make eval-live K=s012 HOST=keel` walks the same journey through that door:
  leg one is **skipped** (`harness/keel_host.py` raises from every one of its methods, so a
  future edit that reached for it gets a sentence rather than an empty result that would read as
  a pass), and what is asserted instead is the six things only that door shows -- 2,000 credits
  on the shell line and no agent line, `aiPath: "KEEL"` on the wire, a balance that drops when
  the first framing is held, `execution.host: "api"` with a real `actual_cost_micro_usd` on every
  job, the founder's screens reading *Keel*, and a `KEEL_HOME` still empty when the brief is
  written. It is **the only cell in the matrix that spends the company's money** -- Keel's own
  Anthropic account, about $2.44 of inference a journey -- so it is weekly's alone, once, and
  `matrix/cells.py`'s coverage rules refuse it in `per_change` by name. Widening a named place is
  what the amendment rule permits; a fourteenth scenario would have been a fourth place and would
  have had to be argued for.

  **And every one of those doors is now entered the way a founder enters it** (spec 024, the
  second half). keel-cloud decides which AI an account runs on from the door it was *created*
  through -- the stored `return_to` of that first sign-in -- and `/connect` is the only path that
  answers `OWN`. S-012 signed in at the plain `/login` before it installed anything, so on the
  twin (where every cell registers its own founder minutes earlier) every CLI cell was creating a
  **Keel's-AI** account with a 2,000-credit grant. The legs are in the founder's own order now --
  install, *"keel connect"*, the code, and only then `/login?user_code=...` -- and so are the
  corpus riders' and S-013's. Nothing was removed; two assertions were added.

  **And what it asserts about the cards moved when keel-cloud 048 moved it** (spec
  `026-journey-one-questionnaire`). One questionnaire belongs to the project now, written by one
  `QUESTIONS` call after the last framed stage is approved, so a review card is read before any
  pick list exists. The review step asks for numbered lines and a deal-breaker; *every line offers
  a pick list* is made after the third approval, against the project's own questionnaire and the
  slice each approved card carries, once `Overview.questionsState` reads `READY`. **No assertion
  was dropped** — the comment where the old one stood quotes it and says where it went, which is
  the rule this repository works to whenever a product moves under a scenario.

  **And §1.7 moved with keel-web 027** (spec `027-journey-brief-ship`). The overview is **the
  deck** now -- the keel ship as one band per stage, three panels of *Held* and *Did not hold*,
  and *Download the brief* -- so the evidence bar, the four-count legend, the three stage cards
  and the *What this says* paragraph all left that screen, and `Overview.open` waited thirty
  seconds for a class (`.ocards`) that keel-web still draws **on a different screen**. §1.7 reads
  the deck: three bands coloured by the verdict the wire sent, three panels whose count lines are
  compared against `GET /overview` and `GET /standing` number for number, the worst panel open at
  rest, and the download live exactly when a reading exists. The paragraph is asserted on **page 1
  of the brief**, which the journey now opens and reads whole -- five pages, the 16:9 block, and an
  evidence page that carries every line's counts and **nobody's name**. **No assertion was
  dropped**: three moved with the reason written where they stood, and the one whose subject no
  longer exists anywhere -- keel-cloud's own *not yet* note -- was inverted into the download's
  disabled state, which is what a founder actually reads at that moment.

  **And it is still one scenario at two lengths** (spec 021). `LEGS=short` stops it after the host
  leg and the **first** model job, which is what every qualifying change now buys; `LEGS=full` is
  what the weekly set and, since design §16, every per-change cell buy (the nightly is suspended since 2026-09-13). That is a *stopping point* in one story, not a second
  story: the assertion the short run makes about the confirmation card is literally the same
  function the full run calls, and nothing new is asserted from the model's prose because the run
  is shorter. A `test_s013_short_journey.py` would have been a fourth named place and would have
  had to be argued for; this is not one.

  **And the back-test widens it once more, locally** (spec 062, `make backtest ENTRY=<id>`, 2026-10-22). The founder
  asked to *emulate* real funded founders and read what Keel's AI asks them and their people: so a **back-test entry**
  (keel-cloud `canon/designs/measured-beliefs/backtest/NN-slug.yaml`, the corpus schema with no `expected`, a top-level
  `idea_name`, an optional `sources`; `instructions/corpus.load(..., backtest=True)`, the golden refusals all kept) is
  walked by `corpus_scenario.run(..., backtest=evals.backtest.Backtest)` with `strict=False` -- S-012's mode, nothing
  held to the file -- by *Backtest Founder* (`backtest@keel-backtest.test`, outside keel-cloud's `fake-for`) signed up
  through `/signup`, so every job runs on Keel's AI with the routing file's own models, on the local stack, contacts,
  renders and transcriber fakes. It writes `backtest.md` / `backtest.json` (founder screens, served respondent
  questions per link, the brief as served, the readings beside the file's anchoring, cost and time), one full-page
  screenshot a founder screen and a respondent screen (`screens/`), and 060/061's export ungated (`export/`). **It is
  the fourth paid command** beside `instruction-eval`, `eval-live` and `keels-ai`: Keel's own Anthropic key read into
  that one command's environment (`KEEL_ANTHROPIC_API_KEY`; refused by one sentence without it; never logged or
  written), about $0.50 of inference (and 1,700 of the account's credits, 400 of them the recorded interviewer) for a
  twenty-person entry -- `08-fresco`, 30 jobs on Sonnet 5.5 and Haiku 4.5, 6.5 minutes -- run on the founder's word only and never by a schedule, a cell
  or `make eval` / `make unit` (`evals/run_backtest.py` is no `test_*.py`; `matrix/cells.py` never names it). A
  widening of this place, not a fifth: the subject is the same journey on the same model door.

- **The live classifier check** (`evals/test_classifier_live.py`, spec 048 FR-2) -- the fourth, argued here as the
  rule asks. keel-cloud 099 makes a model (Keel's AI, the light tier) decide what a respondent's spoken answer means,
  and the only way to know whether it gives a confident wrong answer on real items is to ask it: the FakeClassifier
  the stack and every eval founder run is guarded on every journey, but it is not the thing a stranger meets. So the
  check is live for the same reason S-004 and S-012 are -- **the thing under referee is a model's behaviour** -- and it
  is the smallest such place there could be: text only (no audio, no browser, no journey), one `classify` call a case
  on a link the founder names (`KEEL_CLASSIFIER_LINK`), refused before the first call over $0.10, `-m live`, the weekly
  macOS x Claude cell's alone (`matrix/cells.toml`), skipped by name without the link. It is not a scenario: the
  scenario set stays thirteen.

- **The noise-capture certificate** (`make noise-check`, spec 074 FR-3) -- argued here as the rule asks. Since keel-web
  115 every spoken answer is recorded and Keel writes it down (gpt-transcribe) and reads it (Haiku), and the founder's
  bar of 2026-10-26 is a claim about that pair in noise -- *every answer in a quiet room, more than 90% down to 5 dB in
  every room* -- which only the vendors' own models can answer. So the check is paid for the same reason the live
  classifier check is (**the thing under referee is a model's behaviour**) and is as small as it can be: no stack, no
  browser, no journey; the 1,260 kept samples of 2026-10-26 (`KEEL_NOISE_SAMPLES`) sent down the product's two calls
  as `OpenAiTranscriber` and `KeelsAiClassifier` make them (max_tokens 400, keel-cloud 137; the cloud checkout's own
  `classify-answer.md`), read by `Classification.validated()` restated (keel-cloud 136's partial pick included), about
  $2 and twenty minutes, both keys from the shell (`KEEL_OPENAI_API_KEY`, `KEEL_ANTHROPIC_API_KEY`) into the request
  headers alone. `evals/noise/` holds it (moved from keel-cloud `canon/designs/noise-capture-check-2026-10-26/`, which
  keeps its README and results as the record); it writes `runs/<stamp>-noise-check/` and a row on
  `runs/noise-check-register.md`, and the certificate line is PASS, FAIL naming the first failing cell, or INCOMPLETE
  for a partial run (`ONLY=`, `SNRS=`, `LIMIT=`). Never in `make eval` / `make unit`, the matrix or a schedule
  (`evals/noise/` has no `test_*.py`); everything that scores is offline and unit-tested on the canon's stored rows
  (`tests/test_noise_check.py`).

**The canon comes first**: keel-cloud `canon/CANON.md` holds the governing documents,
their precedence, and the ledger this repo's `tests/test_journey_coverage.py` enforces. This
repo deliberately floats at sibling HEADs (a referee pinned to the past can't call the present).

**The runtime is a referee's target, not the referee's tool**: `keel connect` is never launched by
this harness directly (`python3 -m keel_runtime`) — only through `keel-connect-skill`'s own
script (`harness/connect.py`), because that skill is itself one of the four applications under
referee. `make up` ends with the runtime not yet running; S-001 starts it, because starting it is
part of the journey.

**And the runtime that runs is the one that travelled inside the skill** (spec
`012-bundled-runtime`, keel-cloud `canon/designs/keel-skill-design.md` §3.2): the `keel_runtime/`
package `make runtime` puts beside keel-connect-skill's scripts, **not** the `../keel-runtime`
checkout. Nothing here passes `--runtime-path`, and `KEEL_RUNTIME_PATH`, `KEEL_HOME` and
`KEEL_BASE_URL` are scrubbed out of every child this stack launches — a founder is on the skill's
rule 2 and so is the referee. `make up` gates on the package and names
`make -C ../keel-connect-skill runtime` rather than running it: **this repo never writes to a
sibling repository**, and that target refuses on a dirty keel-runtime checkout anyway. `make down`
asks the runtime to `disconnect` (through the skill's own `keel_disconnect.py` when it exists) and
reads the outcome that proves it went; it does not signal a pid. **And S-001 now leaves the same
way a founder does** (spec `011-keel-disconnect`): its tail shells that script and only that
script — never `python3 -m keel_runtime disconnect` — and asserts `GET /v2/me` reads
`agent.connected` false **within two seconds**, which is the one end-to-end proof of
keel-runtime's goodbye in any of the four repositories. `harness.connect.stop_runtime_via_skill`
is that door and has no fallback; `stop_runtime` is `make down`'s and keeps one. The `../keel-runtime` checkout
stays configured for the two places that *read* its source: `harness/canary.py` and
`instructions/prompts.py`.

**And what ships is refereed too** (spec `013-skill-distribution`): **S-009** installs
keel-connect-skill's four `make dist` trees the way their own installers install them — a
plugin's `skills/`, `install.sh --host claude` run for real, a repository's `.github/skills/`, a
Spec Kit extension directory — and asserts the same contract shapes byte for byte out of all
four, which is L1's gate on the far side of an install (A-6). `make acceptance`
(`stack/containers/acceptance/`) takes the same question to Linux: Debian 12 and Debian 11 — the
3.9 floor itself — on `linux/arm64` and `linux/amd64`, against this stack at
`host.docker.internal:18080`. Its **model-driven half** (`claude -p`, `copilot -p`) reads
`ANTHROPIC_API_KEY`/`COPILOT_GITHUB_TOKEN` **from the caller's own shell and nowhere else** (T-5);
with neither set it skips itself by name and the reason goes into the run record. As with
`make dist` and `make runtime`, this repo **gates on the built trees and names the command** —
it never writes to a sibling.

**And there is a fourth service now** (spec `015-stub-oidc-and-two-founders`, keel-cloud
`canon/designs/google-sign-in-design.md` §10.1-§10.3): `stack/stub_oidc/`, a standard-library OIDC
issuer `make up` starts first, on **18090** (eval) / **18091** (playground). keel-cloud's founder
login is becoming Sign in with Google, and §3.6 is the whole test story -- **the issuer is
configuration**. `KEEL_OIDC_ISSUER` defaults to Google and a deployment sets nothing; this stack
names the stub, so the product keeps exactly one login path and the eval walks all of it. The stub
has no password, no bypass header, no test-only route and no second trusted key, and it refuses a
bad PKCE verifier, a reused code, a mismatched `redirect_uri` and an unknown client -- a stub that
accepted anything would prove nothing about keel-cloud's half. Its two identities (**founder A**
*Eval Founder*, **founder B** *Nour Haddad*) live in `stack/oidc.py`, once.

**The second half has landed** (keel-cloud `master` 866a611 carries spec 032). There is no
password anywhere: `harness/browser.py:Auth.sign_in(identity)` clicks the real *Continue with
Google*, clicks the founder's own name on the stub's account picker, and comes back through the
real callback -- and `stack/auth.py`'s one browserless sign-in walks the same three hops on a
`requests.Session`. **Never a transplanted cookie, never a seeded session, and no function
anywhere in this harness that produces a founder session by any other means.** Two scenarios came
with it: **S-010** (two founders on one instance -- every one of another founder's routes a bare
404) and **S-011** (the callback's own refusals, each with the founder-voiced line the design
names). The scenario set is **seventeen** (spec 052 added S-014, the healthy project; spec 071 S-015 and S-016, the
two study-scope journeys; spec 092 S-017, one open link for a group).

**Study scopes** (spec `071-study-scopes`, 2026-10-25; keel-cloud 133, contract 38; keel-web 109 / 110 / 111): a
project is one of four configurations chosen on *What do you want to validate?* -- PROBLEM, SOLUTION,
SOLUTION_COMMERCIAL, COMMERCIAL -- or **ALL**, the harness's own (accepted on the wire, never offered by the web). Every
golden journey and back-test creates its project as ALL: `Landing.name_project` walks the choose screen by picking
nothing and `ScopeChoose` carries the one create request with `scope: ALL` (`ScopeRewrite`, a one-shot route on
`/v2/projects`); `Journey.scope` is held on the overview and the list. `Entry.scope` (ALL; the corpus records none,
REVISION 16) and `harness/vectors_script`'s scope rules (the scope's vectors, the parts each link serves, the gate's
clock, the calibration and part-1 jobs) return today's answers under ALL -- the seven's scripts and the back-test
entries' people, founder inputs and plans are byte-identical to master's. **S-015** (`evals/test_s015_problem_only.py`)
and **S-016** (`evals/test_s016_money_only.py`) walk `evals/scope_journey.py` on seeds derived from 01-countly: the
problem study (Countly's own four problem standings held) and money alone on a B2B persona (the restaurant owner
decides; only the decision-maker's link; the problem in one spoken sentence before the idea card), each scored by
`evals/scope_marks.py` (SC1-SC7, `SCOPE_MARKS_VERSION` 2 since spec 073, a journey ruler; `MARKS_VERSION` stays 20). `make backtest
SCOPE=` / `scripts/backtest-host.sh --scope` walks an entry as a study of that scope (`strict=False`, the marks as
findings) and records it in `backtest.json` and the register row's Door cell; the gallery's index rows carry `scope`.
DRIFT #95 (a scoped study's *Lock and approve* never lights: `PlanView.complete`), #96 (money alone's hidden recall
window sent as 7 nights) and #97 (`ScreenChain` chains out-of-scope calibrations) are **closed** (spec 072; keel-cloud
134 / 135, contract 39; keel-web 112): the plan is held complete over the scope and the lock pressed on the page, money
alone sends, draws and reads back no window, the script carries the scope's calibrations alone, and a lock receipt may
name no job (money alone). Each is a failing guard should it come back.

**The founder's staging review of 2026-10-26** (spec `073-founder-feedback-2026-10-26`; keel-web 113 / 114, keel-cloud
unchanged, contract 39): the context step is one state at a time (`[data-testid=context-step][data-context-state]`) --
every walk holds form -> Save -> the wait in the form's place (the counter, the phase bar, the truth card; no field, no
Save) -> the *Keel understands* card in the wait's place with *Edit* (`Corridor.context_states`, a MutationObserver
installed before Save), and S-005 alone (`run(..., context_edit=True)`) re-opens the confirmed context and presses
*Edit*: the form back, filled with what was confirmed, nothing saved. *A word from you* is hidden: the last step starts
on its first visible screen (the pilot 1 of 2, who asks 2 of 2; the problem study's who asks alone, no counter), the
word's address redirects there, the interviewer leg writes no founder's word, and every text link's last screen is the
thank-you's default words as served (the exit screen owes none). SC2 (`SCOPE_MARKS_VERSION` 2) and IM5
(`INTERVIEWER_MARKS_VERSION` 8: no word stored, every THANKS clip the default thank-you) are re-pinned. The full
Overview draws no panel lead (`rp-plead`); the brief's page one keeps it and `report_binding` counts it as the sheet's
own (`REPORT_MARKS_VERSION` 2). The welcome per scope: `guide_marks.welcome_clip` -- `welcome` under ALL on S-005/006/
007/014, `welcome-problem` on S-015, `welcome-money` on S-016 (read off the welcome passed by), the four new clips
counted with the manifest's 42 (G12 reads them; `GUIDE_MARKS_VERSION` stays 3). The AI player's crop is read by its own
classes and recorded (`record["ai_band"]`), never scored. `MARKS_VERSION` 20 and corpus REVISION 16 unchanged.

**One recorded path, and the noise-capture certificate** (spec `074-recorded-path-and-noise-certificate`; keel-web 115
-- 120, keel-cloud 136 -- 138, contract 40): keel-web 115 retired the browser's recogniser, so the AI walks drive the
recorder. `ivs.SPEECH_SEAM` restates keel-web 115 FR-5's `installFakeSpeech` -- the fake recorder and the always-granted
microphone; `__say(text, final=True)` pulses the level for three ticks and goes quiet, and the next `stop()` hands back
the said words' UTF-8 zero-padded to 20 KiB as `audio/webm`, which keel-cloud 136's `FakeTranscriber` trims and hears
through the real `/interview/answer` (no stand-in on the seam). `__listening()` is the recorder running; `ear()` /
`wait_ear`, the recogniser's counts and the `not-allowed` leg are gone (`recorder()` / `wait_listening`); every spoken
answer is `how` RECORDED and no `classify` is sent; the text box's seam (`text_seam`) drives the same recorder by a
level, its recording the zeros alone (the stack's fake still hears `FAKE_TRANSCRIPT`). S-005's follow-up says the line
into both windows (the pause, then *Save and next*) and presses *End* in that hold: the pilot ask after *End* records
on the kept stream (keel-web 116 FR-2); S-006's makes a sound and leaves the second window silent to its cap. Keel-web
116 FR-1: *Microphone off* is read once the done screen shows it, the release after the thank-you's end (never while it
plays; StrictMode's release at load read for not moving). Re-pinned (`INTERVIEWER_MARKS_VERSION` 9): IM9 (RECORDED,
SPOKEN retired), IM19 (*Recording your answer.* and *Hearing you…*, one recording, one read), IM21 (no recording in a
beat) and IM25 (every follow-up window recorded: the pause, Save, the cap). Keel-web 117: the occasion is read through
the card's *I'll ask about* line's *Change* (Esc puts it back, nothing edited); the scripted card carries no stem, so it
draws no line (117 J-4) and the noun is held on the confirmed view; Edit's form draws no occasion block. Keel-web 119:
Send more's row is picked by its name (the AI row carries *Hear it*). `make noise-check` (above): the certificate.
`MARKS_VERSION` 20 and corpus REVISION 16 unchanged (keel-cloud's corpus is at revision 16).

**Follow-ups at once, the morning's fixes, and One more thing** (spec `075-follow-ups-at-once-and-the-morning-fixes`;
keel-cloud 139 -- 142 and 144, keel-web 122 -- 124 and 126, contracts 41 and 42): up to two follow-ups, each asked right
after the item it hangs on, the end's only for a rung still owed (`interviewer_fake.asks`, `vs.follow_up_plan`); every
route call carries `asked`, the response `followUps[]`, the stored and the stage rows read the list. The text walk
answers every follow-up screen it meets (after an item's *Next* and after *Send my answers*), and since keel-web 126
tells the one asked on the spot after Send from the end's by its rung (the last item's) -- every screen, the AI sheet's
kicker and its where-word say one kicker, *One more thing*, and every FOLLOW_UP clip opens on *One more thing.*
(`fake.ONE_MORE_THING`; *One last thing.* is `RETIRED_LEAD_IN`, re-rendered once by keel-cloud 144 on a recording that
still says it); the answers line under a person is *One more thing · {rung}: "…"*. The money-only walk holds one kind
(139); every Price step reads its cost box in 140's words; the chain cost step reads *Per* / *of* pre-filled and the
rate row (123); Ability to pay's said line is Keel's reading with the counting sentence (141). Contract 42 (keel-cloud
144): S-006's Try it yourself walks on to the story and holds the hello and the story written down through the
founder's own `interviewer/transcribe` (`dry_run_written_down`: on the gate's id, taken, no miss words), and the wire
checks the route beside the follow-up twin (`_dry_run_transcribe`: the story, the follow-up at 120 and the mic test
written down; an unknown id and a link's gate 422 `ITEM_NOT_ON_FORM`, 90 s 422 `SHAPE_MISMATCH`; nothing stored) -- the
stack's fake transcriber serves it unchanged. Keel-web 126 FR-4: the story's speaker holds the permission sheet through
the seam (`text_seam(held=True)`, keel-web's `installHeldMic` restated; `SpeakBox.grant`), reads the box `asking`
(*Allow the microphone…*, *Cancel*, no waveform, no clock, nothing recorded, Continue off) before T2, and holds the
microphone kept through the take and let go on the done screen. Re-pinned (`INTERVIEWER_MARKS_VERSION` 10, then 11):
IM23 (the order, `asked`, `followUps[]`; one kicker), IM24 (a skip not sent, the step after it), IM25 (every follow-up's
windows), IM26 (asking, the microphone kept) and IM27 (*One more thing.*). Keel-web 122's public pages: no check here
reads Plans' numbers or the legal pages' sentences, and the matrix smokes neither `/terms` nor `/privacy`, so nothing
moved. `MARKS_VERSION` 20, corpus REVISION 16 and every other ruler unchanged. **The light gate** (the founder's word,
2026-10-27): `make unit` and S-005 on the local stack; the other five journeys are the thorough pass's. A journey that
fails mid-way leaves the scripted runtime it started connected, its script moved on: `make down` and `make up` before
the next run (spec 075 D-02).

**The quality cycle** (spec `079-quality-cycle`, 2026-10-28; built on 078's readers and 063's gallery). **A session told
*"kick off the instruction set"* reads `quality/CYCLE.md` and nothing else**: the runbook of the six steps -- the
kick-off (`make quality-walk ENTRIES=<ids|default> [SCOPES=] [DOOR=keel|host] WHY="<the founder's words>"`, paid: per
entry and per scope `make backtest`, then `make read-screens` on the new bundle, then `make read-table BASELINE=1
CYCLE=`; the record `quality/cycles/<yyyymmdd>-<cloud7>.md`), the comparison (`quality/TABLE.md`'s head: this cycle, the
baseline, the bar), the adviser (`make quality-advise CYCLE=`, paid, one call per weak row, `quality/readers/adviser.md`,
proposals in `<record>-advice.md`, **never applied** -- a taken one is a keel-cloud spec), the rerun, the acceptance
(`make quality-accept CYCLE=`, free, on his word only: a new `quality/BASELINE.md`, the old one under
`quality/baselines/`, and `make gallery SCORES=quality/scores` from that cycle's bundles -- a bundle the readers did not
pass refused by name -- with the keel-web refresh sentence printed) and the cadence (`make quality-due`, free). Its
settings are `quality/cycle.toml` (entries, scopes, door, the bar, the weak rule, reader and adviser), held equal to
`quality/rubric.py` and `quality/readers.toml`. The adviser is the readers' door again (the judge's argv, a pinned
model, no key), so the LLM places stay four. No target of it is a dependency of anything; none runs from `make eval`,
`make unit`, the matrix, a checker or a schedule. The thirteen bundles of 2026-10-24 are never scored.

**The back-test under a scope** (spec `082-backtest-under-a-scope`, 2026-10-28; after cycle 1 stopped 13 of its 15
walks). A walk under `SCOPE=PROBLEM` or `SOLUTION` sends the entry's PRIMARY people alone (`vectors_script.study_people`:
the B2B people are the money study's, keel-cloud 133, and those projects have no `COMMERCIAL_B2B` kind -- cycle 1's
KeyError); COMMERCIAL and ALL send everyone, and the follow-up lines, the themes screen and `inputs.json` read the list
that comes back. The chain cost step reads *of* (`chain-base`, its helper, the rate on hours) after the period pill, once
`chain-equation` is drawn (keel-web 123 FR-1). The cycle record's head and `TABLE.md`'s say under the score how many
walks reached their end and which stopped (study -- the step), and a keel-cloud or keel-web sha that moved mid-cycle
(each study's own sha recorded; named, never refused). Cycle 1's record is not rewritten; `make read-table
CYCLE=quality/cycles/20261028-88bfce8.md` reads the same facts from its studies and score files. Readers, rubric,
weak rule, adviser, journeys, `MARKS_VERSION` 21 and `REVISION` 17 unchanged.

**The two studio faces in the harness** (spec `083-two-studio-faces-in-the-harness`, 2026-10-28; keel-cloud 143,
contract 44, + keel-web 125). `harness/interviewer_fake` mirrors 143: `FACES` DAPHNE, SASKIA (the enum's constants whose
offered flag is true, in order), `PRESELECTED` DAPHNE; `RETIRED` = `RETIRED_110` (094's JUDY, JIN, ANNA, TITO: no
constant, no hello on keel-web) + `RETIRED_143` (LIVIA, JIA, MARIEKE, CHUKWU: still constants, keel-web keeps their
files), a pick of any 422 FACE_UNKNOWN; `served_hello` is null for a retired face, as 143 FR-4 serves a recording of
one. The interviewer leg's first recording is the face that is not the preselected one (SASKIA) and the change goes to
the preselected one (DAPHNE), every face word read from the fake; `test_the_faces_are_keel_clouds_own` reads keel-cloud's
enum on the offered flag. The marks only read the data: `INTERVIEWER_MARKS_VERSION` holds at 12. The interviewer's
hellos are heard unmuted: on a machine whose audio output stalls, headless Chromium fires `playing` and never advances
(any face; muted or `--disable-audio-output` plays to the end), so IM28 / IM30 fail for the machine, not the product.

**The card's condition is the settled one** (spec `084-card-condition-settled`, 2026-10-28; keel-cloud 148 FR-1,
contract 44 unchanged). The context card's *Only people who:* line reads the condition the confirmed context stores
(`vectors_script.card_condition` = `segment_of(entry)["condition"]`), so on a `DRAWN` row (07-mulchrun) it is code's
*are based in the Dallas-Fort Worth suburbs* although the scripted result (`scripted_segment`) writes none; spec 077's
"none on 07-mulchrun" no longer holds. S-007 red on staging `f48f256` + keel-web `786d4c3` until this.

**Decided before** (spec `087-decided-before`, 2026-10-29; the founder, after deciding every proposal of cycle
`20261028-f48f256`'s advice: *"whatever the agent found and we decided not to go ahead should be recorded, so that
it's kind of snoozed next time"*). `quality/decisions.toml` is the file of record, one `[[decision]]` per decision
(`id`, `cycle`, `proposals`, `row` = scope / audience / dimension / screen, `fix`, `decision` taken | declined | held,
`spec` on taken, `until` spec-merged | never | a cycle id, `why`, and `merged` when the coordinator writes it);
`quality/decisions.py` reads it and `make unit` refuses a file whose entry lacks a field, says another word, or names a
scope, audience or screen the cycle does not score. A weak row whose `row` and `fix` match a decision is **snoozed**
while its `until` holds: listed under *Decided before* in the cycle record and at the end of the advice page, never
sent to the adviser, not counted. The adviser's prompt carries the declined decisions on its row (`{{declined}}`),
and a proposal that names one in `reopens` is refused by row, naming it (as 081 FR-6 refuses a special case). **The
coordinator's duty** (`quality/CYCLE.md` step 3): after a walk-through with the founder, add his decisions before
the next advise; after a merge of a spec a decision names, write `merged = "<sha>"` on it so the row competes again.
`make quality-advise CYCLE=quality/cycles/20261028-f48f256.md DRY=1` listed all 62 weak rows under the decisions of
2026-10-29 and sent nothing; with the eight `merged` marks of 2026-10-29/30 it lists 15 and would send 47 (spec 085). No model, no new LLM place; readers, rubric, weak rule, `REVISION` and the marks
unchanged.

**The read-back in two sentences** (spec `085-read-back-mirror`, 2026-10-29; keel-cloud 149, merged `73426a67`,
contract 44 unchanged). `vectors_script.sentence` mirrors 149's `ReadBack.sentence`: *{Segment}. When {when}, they want
to {what}. We'll ask about the last {window}.* (since spec 103 / keel-cloud 168 the window its own sentence; 149 wrote
*, counting the last {window}.* on the job) -- the segment whole (`qualifiers.segment`, 148's own *whose* / *that* /
*which* kept, said once by `in_core`), a full stop, the circumstance with its first letter raised, and the job on the
people's verb (`qualifiers.they`: *they {job}* where it already opens *want to* / *need to* / *try to* / *have to* /
*must*, *they are trying to* on *trying to*). The harness's draw (`vectors_script.condition_from(part, before)`,
`drawn_condition`) follows 149 FR-3 through `qualifiers`: a list *A, B or C* is one part (`parts`), a participle is its
verb (`bare`), *whose jobs run on ...* draws *have jobs that run on ...* (`thing_of_theirs`), an organisation's
participle or relative clause draws *work at a {head} that {verb}s ...* (`organisations_clause`, 131's frame before it),
so the tool branch draws only where the people are the subject. `leg_context`'s strict compare reads the mirror, so the
journeys moved with it; 17-expanse's *have 100 or more GPUs* is 145's amount branch, which neither 149 nor the harness
draws. `make unit` on a keel-cloud-docs snapshot at `73426a67`; `make eval K=s005` / `K=s007` owed on a stack at 149+.

**Corpus revision 18 and the follow-ups that name the thing** (spec `086-revision-18-and-the-gate`, 2026-10-29; keel-cloud
152, merged `21395ab0`, and 154, `9f78b765`, contract 44 unchanged). The reader reads **revision 18** and refuses 17 by
name: seven belief templates and the Prevalence phrases in the founder's words, the rate cost's belief *The problem
already costs the payer about ...: {loss}.* (`chain.cost_belief`, rule C), no standing moved -- rule D18
(`tests/test_corpus_r18.py`) holds every entry to its `corpus-r17/` / `backtest-r17/` record (the revision; on the golden
seven the eight belief fields; on the eleven rate back-tests the cost's sentence; `expected` whole), D17 and D16 kept as
mirror-against-mirror records. Invariant 4 reads `{value}` once on every template; the harness's Prevalence phrases are
the bin's share; the Importance Check box reads *Of these {n}, ...*. `MARKS_VERSION` 21 stands (no mark scores a belief
sentence) with the seven r18 digests in its header. The follow-up ladder is 154's (`interviewer_fake.LADDER`, `ALSO`,
`FILL_DEFAULTS`): every rung fills `{job}` (`vectors_script.job_gerund`), `{solution_name}` (*it* where none), `{step}`
and `{effort}` as -ing phrases, the spoken line filled from the project (`lock_values`, `follow_up_clip` =
`FollowUpComposer.clip`), Price, would-not-pay, Buyer and payer and Purchase friction naming the idea; IM27 reads the
leg's filled clip words (`INTERVIEWER_MARKS_VERSION` 13). The gate keeps its two chips (keel-cloud 153 as merged): FR-4
was struck, no gate pin moved. `make unit` gated on keel-cloud-docs snapshots at `21395ab0` and `1602f8b4` (153 + 154);
the ladder's registry reads skip by name on a keel-cloud before 154. `make eval K=s005` / `s006` / `s007` owed on a stack
at 154+.

**One charge per interview, at Begin** (spec `088-credits-at-begin`, 2026-10-29; keel-cloud 156, merged `68ff142a`,
contract 45, `InferenceCharge.VERSION` 12). `PRICE_VERSION` is **12** in both fakes; `harness/interview_charge.py`
mirrors 156 -- `INTERVIEW` 30 at Begin, `INTERPRET` and `THEMES` 0, §6.3's five-participant journey **1,355** credits
(was 1,250), the Begin key `interview:<invitationId>`, the INACTIVE body *This link is no longer active.* -- held to
keel-cloud's `InferenceCharge` and `InterviewController` (skipped by name before 156). The scripted person posts
`interview/begin` before the response (`vectors_script.PersonInputs.scripted_posts`): S-006's interviewer leg Begins
the Let-them-choose link twice (one INTERVIEW row of -30, none on the second) and the recorded link before its first
window; the full leg walks the link's gate (`_inactive_link`: INACTIVE at 29 on the wire, served at 30, the begun link
still served at 0 while a never-begun one is INACTIVE), its balance moved by labelled stand-ins
(`stand_in_balance(label=...)`). Every reading and themes HOLD is held at 0, and both legs' *no other row* sweeps let a
Begin's row through. **What keel-web 131 owns waits behind one marker**, `interview_charge.WEB_131_BUILT` (or
`KEEL_WEB_131=1`): the screens' Begin row (S-005 and S-006's AI and chip links, S-006's decision-maker) and the
inactive page are recorded as *SKIPPED -- keel-web 131 not yet built* until it is set. `make unit` gated on a
keel-cloud-docs snapshot at `68ff142a`; `make eval K=s006` owed on a stack at 156+, and `K=s005` / `K=s006` with the
marker on after 131.

**Corpus revision 19 and the three moved controls** (spec `089-revision-19-and-the-controls`, 2026-10-30; keel-cloud 158,
merged `e3d34831`, contract 46; 159, `1cf2ebc3`, contract 47; 160 at `ad5f6441`). The reader reads **revision 19** and
refuses 18 by name: Relative advantage is **one scale**, `scale_four` (*A lot better · A little better · No difference ·
Worse*, *I can't tell* apart), every recorded answer moved by the one rule (`registry.from_three`), the golden row
recording `optionCounts` on the four; rule D19 (`tests/test_corpus_r19.py`) holds every entry to its `corpus-r18/` /
`backtest-r18/` record (D18, D17, D16 kept mirror against mirror). The corpus's Frequency and Importance rows still record
`segmented_0_to_7` / `pick_two`, read as 158's `segmented_1_to_n` / `pick_one_then_one` (`registry.RECORDED_CONTROLS`).
`MARKS_VERSION` 21 stands with the seven r19 digests; **`INTERVIEWER_MARKS_VERSION` 14** (IM20 reads one tap, the item's
*And one more?* clip, then the second). On the wire and the screens: **Frequency counts from 1**, and the five recorded
0s after a yes (04-linerly Bruno Costa, Dmitri Volkov, Gwen Price; 05-paidly Petra Novak, Talia Ben-David) are sent as
*I can't recall* (`vectors_script.ZERO_AS_CANT_RECALL`), each named in `PersonInputs.notes` and the journey's findings --
the corpus untouched, the founder's call held as `D-2026-10-30-01`; **Importance asks one, then one more**
(`vectors_screens.Interview._one_then_one`, `interviewer_leg._Walk.tap_one_then_one`; one pick with `NOTHING_ELSE` a whole
answer; `interviewer_fake.MORE` *And one more?*; the classifier's `ask: second`; S7 never says *; pick two*);
**Relative advantage is one tap** (no `advantageIds`, no benefit ticks, no advantages ask, `yes_no_per_benefit` retired;
the question *... have made it go better for you, or not?*, the plain frame past 20 words; the follow-up rung on
`no_difference` / `worse`; the brief's line *said it would have gone better, K of them a lot*, `brief_facts.benefit_view`).
160's frames: the served Frequency opens with the window (`vectors_script.frequency_served`, `frequency_held`: the unit said
once, then the cut), E4 still measured on the frame before 160 (`frequency_question`, `wording.frequency_measured`). A
keel-cloud `build/brief-facts/` or `build/spoken-corpus.txt` written before 159 is skipped by name. The screen and
AI-link walks are written to keel-web 135's spec, which is not built: `make unit` green against the live keel-cloud-docs
checkout at `ad5f6441` (3,768 / 0 / 63); `make eval K=s005` / `s006` / `s007` owed on a stack at 160+ with web at 135.

**The money screens, the three controls and the founder screens as drawn** (spec `090-the-money-screens-and-the-controls-as-drawn`,
2026-10-30; keel-web 134, 135's build, 130). The cost box asks the mode first and alone (`Corridor._chain_cost`: the
line `chain-cost-line` read, *Per* and the period chips read only after the pick -- `before_mode` held at none by
`corpus_scenario._hold_the_mode_first` -- the line held to `costHowLine`'s shape, `vectors_screens.cost_how_line` /
`cost_line_parts`: *the buyer's organisation* on B2B, else the context's people, *each {occasion}*, never the
circumstance); RATE is *A share they lose*; the price is six named choices, one click on its own id
(`chain_price_choice`; `chain-share-COST_BASE` is gone). The three controls are walked as 135 **builds** them (its
harness list H-1 to H-16): the AI sheet's second ask read from `[data-testid=ai-sheet] [data-testid=second-ask]`
(`Player.second_ask`), IM20's `one` read after the `more` clip, Importance with picks taken before the escape (one pick +
*Nothing else*, never *None of these*; one pick by speech then *Nothing else*), *Pick one.* held over Importance and the
scale, the text page's second ask by its test id, `pick_two` retired from the walks, no `advantages` read off a
contract-47 wire. **The five recorded 0s are sent as the count 1** (`vectors_script.ZERO_SENT_AS_ONE`, the founder's
D-2026-10-30-01), each still named in `PersonInputs.notes` and the findings. Send more's ways are *People I know by
name* / *People I found with Keel*; the persona question and L1's title are matched by their shape (130's
`personaQuestion`, `beforeInterviewerTitle`); *Lock and record {face}*, *Lock and write the questions*, *Offer a pilot?*.
IM2 / the L1 *no price* assertion meet 130 / 132's *uses ... credits* on L1 -- named for the coordinator, not moved.
`make unit` green against keel-cloud-docs `a396fe9f` and keel-web `02b952c`; the journeys owed after the merge.

**The phrase is the people's: the harness mirrors keel-cloud 161 and 163** (spec `093-the-phrase-is-the-peoples-mirror`,
2026-10-30). The scripted Current solution draft writes the act bare (`vectors_script.bare_phrase` / `said_phrase`,
`ItemFrames.bare` / `said`; the saved list and the Check screen's corpus list too; the corpus still records *your way of
...* and is never edited); the rung is *You said {phrase} works for you. What keeps it working?* (`{phrase}` filled at
the lock, default *the way you do it*; `LADDER_SHA` `b009fac8`; the ladder's registry tests, silently skipped on a 161
registry, run again). **`MARKS_VERSION` 22** (calls 124-126): `L1` in 161's words (a drafted *your way of* faults), `L5`
admits one `suggested` on Purchase friction and Compatibility (keel-cloud 121 FR-3), never elsewhere; an Adoption friction
face is framed as `ItemFrames.adoptionFriction` frames it (`spoken.adoption_frame`: *would you ...* said *You'd ...*), so
K2 counts the cloud's words, and K3 reads the framed line (a base-form clause passes, a third-person subject faults).
`OLDEST` stays 20. Re-scored at v22, the founder-lists screen of 2026-10-30 keeps only spec 091's Importance L1s (its
L5 and K3 faults gone); the 2026-10-29 one loses its L5s.

**A drafted list is held to the draft's rule, not the save's** (spec `091-the-draft-list-minimum`, 2026-10-30).
**`MARKS_VERSION` 23** (calls 127-128): `option_validity`'s `L1` counts Importance's draft (`rival_list`) as
`founder-lists.md` asks it -- with the job's `answers` `{}` the problem itself alone (one item), with the founder's Answer
the problem itself and the N difficulties it names (1 + N, at most `saves.max_items`; `score.named_difficulties`);
`saves.min_items` is the save's rule, read only where a saved list is checked (`corpus._check_list`). `OLDEST` stays 20.
Re-scored at v23, the 2026-10-30 founder-lists screen reads 33/33 and the 2026-10-29 one 27/33 (Importance valid on every
run). **`INTERVIEWER_MARKS_VERSION` 15**: IM2 (and the journey's *L1 revisited ... no price*) reads L1's one served
credits sentence (keel-web 130 / 132: *... which uses 400 credits.*) as the screen's own words -- once, at the served
`changePrice`, no currency (`interviewer_marks.price_words_on`). FR-3a: `models.CLASSES` ends on `example_match` (keel-cloud
routing v13, dormant), and a unit test reads the live `model-routing.json`'s classes against `CLASSES`.

**One open link for a group: three strangers sign in with Google** (spec `092-one-open-link-for-a-group`, 2026-10-30;
keel-cloud 162, contract 48; keel-web 136). **S-017** (`evals/test_s017_open_link.py`, the walk `evals/open_link_leg.py`):
01-countly locked on the scripted runtime, the founder stood on Keel's door with a fresh grant (stand-in keyed
`e2e-eval:092:`, reversed in a `finally`) and the interviewer recorded (`POST interviewer/face`, the fake renderer); Send
more's third way (*A group, with one open link*, `Interviews.send_group`) makes one *Let them choose* link; four strangers
registered on the stub issuer (`stack.auth.register_stranger`: `POST /identities`, the `sub` the stub's, addresses under
`strangers.keel-e2e-eval.test` -- never a real person's) meet it. A and B sign in through the browser (`harness/browser.py`
`Arrival`: the card, *Continue with Google*, the stranger's own button on the picker, keel-cloud's participant callback,
their own `/i/{token}`); C on the wire (`stack.auth.sign_in_arrival`: start, the stub's `/authorize` with `identity=`, the
callback, each hop by hand, the `keel_arrival_` cookie kept). A begins with *Answer in writing* (`walk(begin=
"choice-write")`), answers and opts in; B stops after the gate and resumes there on a second sign-in; A's second sign-in
is ALREADY_ANSWERED; Sent's *By group* tab (`study_line`, `tabs`, `groups`, `group_rows` with the email under the name,
`close_group` / `reopen_group`) is held to the wire; a closed link serves D the inactive line; the ledger carries exactly
two INTERVIEW rows; the Pilot view carries A's email. `stack/oidc.py` `cloud_env` sets
`KEEL_GOOGLE_PARTICIPANT_REDIRECT_URI` on the cloud's origin beside the founder's (a stack booted before this needs `make
down && make up`). Local only: the remote profile refuses S-017 by name. FR-4a: Send more's one credits note is keel-web
131's `FORMAT_CREDITS_NOTE` (`interviewer_screens.FORMAT_CREDITS_NOTE`, read by `format-credits` apart from the state line;
S3 holds no greyed word on any row). No mark moves; `MARKS_VERSION` 22 and corpus REVISION 16 unchanged.

**IM2 knows the staging switch** (spec `094-im2-knows-the-staging-switch`, 2026-10-30; keel-web 132 FR-2). Where the
server serves `recordOnSend: true` (staging's `KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL`) the lock card's first child is
one switch, *Record {face} at lock · 400 credits* (`data-testid=record-at-lock`, `role=switch`, on by default).
**`INTERVIEWER_MARKS_VERSION` 16**: IM2 reads its label on L1 as the screen's own words beside 091's credits sentence --
once, its one number the served `changePrice`, no currency (`interviewer_marks.LOCK_SWITCH_LABEL`, `price_words_on`; the
detail names `L1 switch`); a second switch or another number faults; with no switch drawn (the local stack, production) IM2
reads as v15. `Corridor.l1()` reads the switch at the lock (`Corridor.lock_switch`: drawn, label, role, on, disabled;
never pressed), and the interviewer leg's first step `_lock_switch` (both profiles) records `record["lock"]` and asserts
at most one switch, a drawn one on, and no `recordOnSend` in the lock body (`lock_flags`). Held by unit tests from
keel-web's source words and static frames of 132's card; no stack sets the variable. FR-1a (journey s006): IM2 reads S3's
one credits note, keel-web 131's *Each person who answers uses 30 credits, whichever way they answer.*
(`interviewer_marks.FORMAT_CREDITS_NOTE`, its one number `interview_charge.INTERVIEW_CREDITS`), as S3's own words; a
second credits line or any other price word still faults. FR-2a (journey s017): the open-link leg reads keel-web 140
(contract 49) -- the card's row names the served face (`arrival_interviewer(minutes, name)`: *Daphne, Keel's interviewer,
asks the questions · about 10 minutes*; 136's words on `interviewer: null`), the intro's who line is the served email
(`arrival_signed_in(email)`) and *not you?* the served absolute `groupUrl`; no press is needed for the greeting. No other
mark moves.

**Three stops of the walk that were the harness's** (spec `096-three-stops-of-the-walk`, 2026-10-30; keel-web 109 FR-3,
keel-cloud 165). After a refused lock `Corridor.edit_idea_lines` waits for the scope's next screen -- the solution's first
question or, in the money-only study, who decides (`vectors_screens.IDEA_SAVE_LANDS`, `/define/solution/q/\d+$` or
`/define/persona$`) -- and returns which (`landed`, `idea_save_landing`). The chain cost step's rate box is held to the
view **as it was before the screen's own save** (`leg_calibrate` passes its before-walk read's `hourlyRate` through
`_hold_the_chain_screen`; `corpus_scenario.cost_fill_rate_faults`: the amount, Keel's note iff `defaulted`, the order),
and the entry's own rate is a second step after the save (`saved_rate_faults`: the amount the entry's, `defaulted:
false`). `lock_refusal` reads 165's *the idea card's decision-maker's how line* as `howDecider`; `LOCK_EDITS` edits each
named line alone (`how` no longer drags `howDecider`). No mark moves. `make unit` 4,003 / 0 / 53 (master `dafb23d`
3,970 / 0 / 53); the paid walk (`make quality-walk ENTRIES=10-palus,08-fresco SCOPES=SOLUTION,COMMERCIAL`) owed after the
merge, on a cloud at 165+.

**The money study's people** (spec `101-the-money-studys-people`, 2026-10-30; keel-cloud 133 FR-4 / 139 / 166, keel-web
145). The screens before a link's first item are `vectors_screens.first_screens` (keel-web `screensOf`'s head): the
screener wherever `Interview.condition` is served, any kind; the idea card on a COMMERCIAL_LINK; the gate; and on money
alone's person link (kind FULL, no gate) the card served as `reveal` with `afterPart` 0, walked before part 3
(`reveal_opens`, `Interview._items`, recorded as the `reveal` screen with its problem line). Nobody is read on money
alone (`vs.read_owed`: no gate, no story). On a B2B entry money alone sends the decision-makers alone
(`vs.study_people`'s `DECIDERS_ONLY_SCOPES`; keel-cloud 133: the register serves COMMERCIAL_B2B only), so `j.people`,
`inputs.json`, the follow-up lines, the interview leg and SC3 read the deciders; `leg_invite` sends through
`not_on_this_study` / `people_to_send`, one step records the PRIMARY people as not on this study, and a kind the register
does not serve is a named fault, never a KeyError. A B2C money study and every other scope send as before. No mark
moves (SC4 still reads `idea` on a B2C money study's FULL link: findings until a scope-marks spec). `make unit` 4,048 /
0 / 53 (master `705c7a5` 4,003 / 0 / 53); the paid walks (`ENTRIES=08-fresco,13-aircaps,17-expanse SCOPES=COMMERCIAL`,
`ENTRIES=10-palus,21-codyco SCOPES=SOLUTION,COMMERCIAL`, `DOOR=host`) owed after the merge.

**The money link's body on a consumer entry** (spec `102-the-money-links-body-on-a-consumer-entry`, 2026-10-30;
keel-cloud 133 FR-4, keel-web 145). `PersonInputs.gate` (`vs.person_inputs`: `serves_gate`) -- off the gate, money
alone's FULL link, the expected body is `{answers}` as on the decision-maker's link: no `recency`, `story` or
`anchorChip` (the file's stay its record, never sent), `ends_on_chip` false, `walks_rungs` true for every inside person,
`_speak_for` None. `vs.not_walked_off_the_gate`: a file gate No has no money answers (`response` refuses it by name,
`NO_ANSWERS_OFF_THE_GATE`) and a person outside the segment meets no screener until the interview serves `condition`
(keel-cloud 166 / keel-web 145; `OUTSIDE_OFF_THE_GATE`); `_answer_one` names either in one finding and walks neither --
every consumer entry has two to five gate Noes (13-aircaps: 17 of 20 answer, `_await_standings` waits its 60 s). Every
gated body and the B2B body unchanged; no mark moves. `quality/decisions.py` lists `condition` (the walk's screener) among
the respondent screens, the stop `083fc9a`'s score files left on master. `make unit` 4,076 / 0 / 53 (master `374694d`
4,047 / 1 / 53); the paid walk (`ENTRIES=13-aircaps SCOPES=COMMERCIAL DOOR=host`) owed after the merge.

**The window is its own sentence** (spec `103-the-window-sentence-in-the-mirror`, 2026-10-30; keel-cloud 168, merged
`9ba42382`, contract 49 unchanged). `vectors_script.sentence` closes the job with its full stop and says the window as a
third sentence, *... they want to {job}. We'll ask about the last {window}.*; with no window (none stored, or money
alone, spec 135) the two sentences as before, byte for byte. Every pin of the old *, counting the last {window}.* moved
with why (168), and `test_read_back_mirror_085` holds the new joins and the window line to `ReadBack.java`.
`_drift_96_guard`'s non-strict money-alone check now asks for no *we'll ask about* (*counting the last* could no longer
be drawn, so it tested nothing). Not moved: the web's muted *Counting the last {window}.* under the card
(`corpus_scenario.py:679`, `test_drifts_95_97_closed.py:150`) -- keel-web 147 drops it, its pins move with it. A project
confirmed before 168 keeps the old sentence in its stored `understands`; the walk and every journey make fresh projects.
`test_founder_walk_076` re-pinned to keel-cloud 166's reworded `Interview.condition` description (master's other
failure). `make unit` 4,077 / 0 / 53 (master `a2c76e0` 4,074 / 2 / 53 against keel-cloud-docs at 168+); no paid walk owed
by this spec.

**Choose picks the founder's own row, by its label** (spec `104-choose-picks-the-founders-own-row`, 2026-10-30; the
re-walk of 21-codyco, 17-expanse and 08-fresco). The corpus's `pickedIndex` indexes the entry's TYPED items; Keel's list
writer may draft rows of its own ahead of them (21-codyco: *Forward unanswered calls to Codyco* before the founder's *Let
an AI answer guests in the hotel's voice*), so off the golden walk `corpus_scenario._choose_label` finds the typed item's
label on the drafted rows, for every `vs.PICKED` dimension, and a label not drafted stops the walk by name
(`VectorsScriptError`, recorded in its own step) -- never row 0, never the old clamp to the last row. One finding per
picked dimension names the rows Keel added (*Adoption friction: Keel added: '...', '...'*), no fault. The golden walk
(`strict`) is unchanged: the typed label and index, no finding. Not foreseen: Keel does not always keep the founder's
labels word for word -- the same 21-codyco bundle's compatibility draft moved *could* to *can*, so that walk now stops at
compatibility (pinned in `tests/test_choose_by_label_104.py`); 13-aircaps adoption friction and 08-fresco purchase
friction were drafted without the founder's picked label too, on 2026-10-30. `make unit` 4,093 / 1 / 53 (master `92c0b75` 4,076 / 1 / 53; the one failure is
`test_credits_at_begin_088`'s price version, keel-cloud 169's VERSION 13, spec 105 FR-2's); the paid re-walk is the
coordinator's.

**The harness reads the frontier tier, price version 13, and screens back-test and probe entries** (spec
`105-the-harness-reads-the-frontier-tier`, 2026-10-30; keel-cloud 169: routing v14, `InferenceCharge.VERSION` 13).
`instructions/models.py` mirrors `ModelRouting.FALLBACK`: a class on a tier a host has no row for stands one rung down
(`frontier` on `standard`, nothing else), model and effort together (`ModelTable.standing_tier`), so on v14 a codex or
copilot frame job is `gpt-5.6-terra` at `medium` and claude's is `claude-opus-5-5` at `medium`; the file is still read
as the file, and S-012's per-job model check follows through `resolve_screen`. `PRICE_VERSION` is 13 in
`harness/interview_charge.py` and both fakes (no row they mirror moved; no corridor sum is mirrored; the gate would be
300). **A screen needle that names a back-test entry or a probe now screens it beside the golden corpus**
(`instructions/screen_entries.py`): `K=08-fresco/PROBLEM_INTERPRET` reads keel-cloud's
`canon/designs/measured-beliefs/backtest/08-fresco.yaml` (the three interpretation screens; no golden expectations, so
nothing else) and `K=169-banking-gaming` reads `probes/169-banking-gaming.yaml` (its two frame screens), only the named
files, hashed before and after; a kind word (`K=frame`), a screen word (`K=PROBLEM_INTERPRET`) and the full eval build
what they built. A probe case is marked on its first turn: NEEDS_INPUT with one question that names the planted term (as
typed or inflected) and offers two readings (an *or*), else a fault -- a COMPLETED statement or card named for keeping or
rewriting the term; the marks sit in each case's `diff.json` and the scorecard's `probes`, the extras in its
`screen_entries` (back-test apart from probes), and move no marks row. `make unit` 4,143 / 0 / 53 (master
`8221cf8` 4,093 / 1 / 53; the one failure, the price version, cleared); the screens themselves are the coordinator's,
paid, on the founder's word (`specs/105-.../tasks.md` lists the seven commands).

**The harness reads the founder's own words as never jargon** (spec `107-the-harness-reads-the-founders-own-words`,
2026-10-30; keel-cloud 175). `instructions/corpus.py` `founder_texts(entry, audience_words)` mirrors
`VectorCorridor.founderTexts()` (the four typed context fields, the problem seed, the solution seed, the audience words;
never Keel's interpretations) and `typed_in` mirrors `Vocabulary.typedIn` (whole, case aside, a hyphen joins, no
stemming). J1: `vectors_script.expected_j1` leaves out every typed word, so 05-paidly -- whose own seed says *A platform
that ...* -- owes no *platform* note and the golden walk's strict J1 check expects none. M5: `m5_faults(...,
founder_texts=...)` skips a typed word (the parenthesis and design-note rules still read the line alone), `plain_line`
never moves one, and a `LOCK_PLAIN_WORDS` row fires only where no M5 word it carries is typed (16-pairio's name-list
rows carry none and stand); `scope_marks.sentence_faults` (SC4) the same over the record's `founder_texts`.
`test_after_131`'s refusals of founder-typed words are re-pinned on seeds without them (the words Keel's); fewer
`lock_refused` findings on a back-test walk are the point, not a regression. Not foreseen: 105's `8147930` tracked a
`.venv` symlink that replaced the main checkout's venv on its fast-forward; 107 untracks it (`.gitignore` reads `.venv`)
and the main checkout needs `make venv`. `make unit` 4,166 / 0 / 53 (master `a0ddf77` 4,143 / 0 / 53); the
coordinator's `make eval K=s005` is the acceptance.

**A reworded founder row is picked by its nearest label and named as a drift** (spec
`108-a-reworded-row-is-a-finding-not-a-stop`, 2026-10-30; keel-cloud-docs 177 written for the product's half). Off the
golden walk, where no drafted row equals the founder's typed label, `corpus_scenario._choose_label` picks the one row
`nearest_rows` finds in the nearest tier that has any -- the same words once case, punctuation, a possessive, *-s / -ed
/ -ing* and *could / can / would / will* are folded; else a row carrying every content word of the typed label; else one
whose content words are all the typed label's, at least half (13-aircaps's *Pair the glasses to their phone* for *Wear
the glasses, paired to the phone* needs this third tier: the spec's two do not reach it) -- never another typed row, never
one whose negations differ; it writes **DRIFT: Keel reworded the founder's row '{typed}' as '{drafted}' (spec 081)** into
`findings` and walks on. None near, or more than one, is 104's stop by name; where none is, *{Dimension}: Keel left out:
'...'* is written beside 104's *Keel added* (08-fresco's *A trial on one live job*). `runs/DRIFT.md` #101 files the three
cases of the day as keel-cloud's. Strict is unchanged. `make unit` 4,186 / 1 / 53 (master `554bb03` 4,166 / 0 / 53; the one failure is
`test_open_link_092`'s `group-link` pin against keel-web 142, merged during the build -- eval 098's, not built).

**The harness reads a group's url off the section's `data-url`** (spec `098-the-group-url-off-data-url`, 2026-10-30;
keel-web 142). keel-web no longer draws the shortened `group-link` under a group's name on Sent's *By group*; the url
(the whole served `/i/<token>`) stays on the `sent-group` section's root as `data-url`, open or closed. So
`interviews_screens.GROUP_LINK` is gone, `Interviews.groups()` reads `"url"` off `data-url` and keeps no `"link"` key,
and `test_open_link_092`'s GroupSection pins read `data-url=` (master's one failure, cleared), with two tests beside it:
keel-web draws no `group-link` and keeps `data-url` on the root, and a closed section's url is read. Send more's *Link
made* (`GROUP_LINK_MADE`) and every other S-017 read are unchanged. `make unit` 4,186 / 3 / 53 (master `075b9e1` fails
the same three plus the 092 pin against keel-cloud-docs `8c53497f`: keel-cloud 170, price version 14 and *I can't
recall*, merged during the build -- eval 110's, not built); `make eval K=s017` is the coordinator's acceptance.

**The harness reads keel-cloud 170: price version 14, the gate's No, the chips, the cost frame, the screen** (spec
`110-the-harness-reads-the-lock-jobs-frontier-tier`, 2026-10-30; keel-cloud-docs `8c53497f`). `PRICE_VERSION` 14 in the
mirror and both fakes (`RESPONDENT_QUESTIONS` 70, the lock's job on the frontier tier). The gate's No: the attempt's *I
didn't get to* is retired, so `corpus_scenario.gate_no_faults` wants the served want's *I didn't* or the page's own
*No*, and a served retired label is a fault; `interviewer_fake.story_escape` says the two chips as served, in order.
S6 already read the registry: master's two spoken failures were keel-cloud's `build/spoken-corpus.txt` written before
170 (*I don't know* against the registry's *I can't recall*), skipped by name (`fx.skip_a_spoken_record_before_170`)
and proved clean with the one moved line -- the coordinator reruns `SpokenGuidelinesCorpusTest`. `wording.gate()` and
the Frequency frames frame through `subject_led` (`WindowFrame.subjectLed`, *any* / *some* since 170). The stranger's
cost item had no mirror: `harness/loss_line.py` ports `LossLine` and `vectors_script.cost_question` /
`stranger_cost_label` / `value_box_answer_line` / `cost_item` port `CommercialChain`, held to keel-cloud's seventeen
worked cases and the Palus, Expanse and Codyco lines; a served value box's chip words (*None*, *I can't recall*) are a
screen fault and a cost item that parts from the mirror a finding. The screen reader: back-test entries gain
`<id>/RESPONDENT_PART1`, a probe may carry `job_context` (170's `170-judgement-verb`, marked by
`respondent_probe_mark`: COMPLETED, part 1, no verdict word, the object kept), `build_respondent` hands `problem` and
`condition` as `ScreenContextBuilder` does (never before), and an extra is never scored. `make unit` 4,238 / 0 / 56
(master `20ac3e8` 4,186 / 3 / 53); the 170 screens are the coordinator's, paid, on the founder's word.

**The harness's M5 mirror lets the parenthesis, list and design note yield to the seed** (spec
`111-the-harness-mirrors-m5s-other-rules`, 2026-10-30; keel-cloud 176, keel-cloud-docs `2edd98bf`). `instructions/corpus.py`
`m5_faults(..., founder_texts=...)` reads every parenthesis of a line and skips one whose every name (`names_of`: commas,
*or* / *and*) is `typed_in` the founder's texts -- Codyco's *(OPERA Cloud, Sihot, Apaleo)* -- and skips a design note
whose phrase to its clause's end (`to_clause_end`) is typed (Karsa's *no jargon*, Careforce's *without an integration
project*; a lone *use* never); the mirror still carries no list rule. `plain_line` keeps a typed parenthesis, list or
note, and `_row_fires` stands 16-pairio's three list rows down on its own *SAP, Maximo or SharePoint* (its *CMMS* / *ERP*
fire). The reveal said aloud: `instructions/spoken.py` `reveal_aloud` ports `RevealWords.aloud` (a parenthesis of names
*, such as A, B or C,*; past `SPOKEN_NAMES_MAX` = `MAX_OPTIONS` = 5, *A, B and others*), read by the fake's SOLUTION
mirror (`reveal_said`, `idea_passage`, the problem sentence in `solution_opening`), IM4 and the quality readers' reveal
screen; the written card keeps the founder's punctuation. 107's Codyco pin is `["design note"]` only and Pairio's fires
`["CMMS", "ERP"]`; five `test_after_131` walks re-pinned with why. Fewer `lock_refused` findings (Codyco, Pairio,
Careforce) are the spec working. `make unit` 4,255 / 1 / 56 (master `6fd5c7f` 4,238 / 0 / 56); the one failure is
`test_interviewer_screens`' `ai-mic-on` pin against keel-web 143 (`31b7a13`, merged during the build), not this spec's.

**The interviewer marks read the ear's states** (spec `099-the-marks-read-writing-down`, 2026-10-30; keel-web 143,
keel-web `1d83a28`). The AI sheet's heard line carries `data-heard` (`listening | hearing | writing | words | nothing`):
`FLOW_TIMELINE` samples it on every change with the status (`window.__keelHeard()`, `Player.heard_lines()`) and the
stranger's walk keeps it on `hear_out.heard_lines`; `interviewer_marks.heard_windows` cuts it into recorded windows, and
IM19 owes at least one read and, in every one, *Writing down what you said…* (`HEARD_WRITING_DOWN`; `WRITING_DOWN`
stays the status line's *Writing it down…*) between the pause and the words, never *Heard so far: nothing yet* there --
`nothing` only after an empty transcript. IM17: `Player.mic_test` reads *Test your mic*'s wave (`ai-mic-level` holding
`ai-mic-wave`, five bars, no `.aiv__level`) and, with the seam's stop held (`__holdStop` / `__releaseStop`), the
`writing` block (`ai-mic-writing`, `ai-mic-writing-line`, *Say hello* kept, Start disabled) before *Heard: hello*.
`INTERVIEWER_MARKS_VERSION` 16 -> 17. The selector pin accepts a test id built as an expression or a `testId` prop.
`make unit` 4,294 / 0 / 56 (master `cd03a7e` 4,255 / 1 / 56); `make eval K=s005` at keel-web 143 and the paid s012
re-run are the coordinator's and the founder's.

Rules of this repo: it owns no product code and never fixes the product — cross-repo defects go
to `runs/DRIFT.md` with evidence and get fixed in the owning repo. The **seventeen** scenarios are
deterministic (keel-runtime's `--executor scripted`, never an LLM, except S-004 and S-012 above;
the participants' typed answers are fixture or corpus data, never generated) and every assertion
enforcing a journey moment cites it (`§n.m`).

**The corpus has a second job now** (spec 010): keel-cloud's frozen golden set
(`canon/designs/measured-beliefs/corpus/*.yaml`) is not only what the instruction eval scores the
instructions against — it is also **the script three browser scenarios run on**. **Since spec
`039-vectors-journey` (2026-10-13) the corpus journeys are vectors journeys**: S-005 (`01-countly`,
B2C), S-006 (`05-paidly`, B2B) and S-007 (`07-mulchrun`, US, B2B) walk keel-cloud's **vector
corridor** on revision 9 -- context, the problem and the mechanism, three calibrations, the persona,
the lock and its three parts' questions, one link per corpus person (the decision-makers on their
commercial link), the real interview, the readings, the board, the three vector pages and the brief
-- through keel-web's own screens, one function per leg in `evals/corpus_scenario.py`, every job
answered by the scripted executor from the entry's own stored texts (`harness/vectors_script.py`,
which also derives the four RESPONDENT_QUESTIONS key sets the executor matches on from keel-cloud's
own export). Each asserts the entry's `expected.standings` (status, drift, `n`, counts) and
`expected.vector_verdicts` on the wire and on the rendered pages; where revision 9 and the wire
disagree (Frequency's 0-to-7 axis on the entries' own windows, the cost totals' recorded quarter,
Purchase friction's labels) the spec's *Disagreements* say so and the corpus is not edited. They are
the journey coverage that survives classic's deletion; S-012's leg two walks the same legs live
(`strict=False`). `make up` needs keel-web's framework plugin and `KEEL_VECTORS_ENABLED=true`, both
in `stack/` now. `make unit` after 039: **1,705 passed / 53 skipped** (was 1,764 / 75: classic-only
S-012 tests deleted, 33 vectors tests added). **Since spec `040-marks-v18` the canon is revision 10 and
the contract 13; since spec `041-vectors-journey-r10` (2026-10-14) the three journeys walk it** on keel-web 063's
founder screens and 064's stranger's screens: one dimension a screen -- each list dimension's *Answer* (the founder's
words, which `POST calibration/{vector}/draft` redrafts the list from), *Check and save* (the entry's own list, saved
untouched) and *Choose* (the entry's picked item) -- with every screen's *Stage · k of n*, dots and locked nav held; the
idea as the solution's first question (S2, Save approving it); step 5's two screens; the lock holding every saved list;
each person through the decision-maker's idea screen, the gate's one chip, two picks on Importance, the fixed answers,
one escape last and "nothing" typed as 0; the standings on the wire (each `optionCounts` code mapped onto the wire's
positional codes), the board and the three stage pages (one row's per-person list read); and the brief **on the wire**
(the scripted headline and three answers, a card per dimension equal to `instructions/brief_facts.py`'s reading, what
broke, the pilot on the brief and on `StandingsView`) and **keel-web 065's two pages held to that wire** (page one's
answers, cards, pilot tile and bans; page two's blocks and *What broke*; the download's tab; the board's pilot tile).
The script answers contract 13 (`CALIBRATION_QUESTIONS` lists, one
redraft entry per list in corridor order; `RESPONDENT_QUESTIONS` the gate's clause; `ASKED` the corpus's faces; `BRIEF`
headline + three answers citing what broke); the DRIFT #74 wire step is gone. Product defects met on the way are DRIFT
#78-#81, each stepped round in a step named for the entry. Green locally against keel-cloud-docs `7b151f9` + keel-web
`844ea36`. `make unit` after 041: **1,846 passed / 53 skipped** (the 24 call-89 skips gone; was 1,818 / 77). **Since spec
`042-contract-14-r11` (2026-10-14) they walk corpus revision 11 and contract 14** (keel-cloud 090 / 091 at
keel-cloud-docs `c432c1d`): the lock starts ONE RESPONDENT_QUESTIONS job (part 1; parts 2 and 3 are code's), which the
script answers alone and `leg_lock` asserts on the receipt and the job list; every interview's idea card and Relative
advantage question carry the idea's current name, and on S-006 the founder renames the idea on S2 (*Invoice payout
service*); Paidly's Frequency is asked (r11's months out of 3); the brief's `keelBar`, `notAsked` and quotes are held
on the wire. DRIFT #76 / #77 / #80 / #81 are closed by 091 and the #80 / #81 steps are failing guards; #78 / #79 still
stepped round keel-web `844ea36` until 066 closed them. **Since spec 042's second commit the journeys run keel-web
`c14d513` (066 + 067)**: the board's two tiles (people asked, pilot sign-ups or *None yet*) and people line, S2's
*n / 5 words* counter, page two's *Keel's bar* and quote credits held to the wire (DRIFT #82: the bar is never drawn
live, stepped round in a named step), and #78 / #79 closed with failing guards in their place. Green locally twice
against `c432c1d` + keel-web `c14d513` (and twice before that against `844ea36`). `make unit` after 042:
**1,857 passed / 53 skipped** (was 1,729 / 28 failed / 142 skipped on the same checkouts). **Since spec
`043-contacts-journey` (2026-10-15) they run keel-cloud 092 / 093 (keel-cloud-docs `7850360`: contract 15, `InferenceCharge`
8, document 21)** on keel-web `da0b9eb`, whose pages took contract 15's additive register (newest first) unchanged; **S-006
ends with the contacts leg on the wire** (`evals/contacts_leg.py`): the own-AI refusal, then the founder stood on Keel's door
with a fresh grant (a stand-in, `stack/ledger.py` -- **the one module here that writes to the database**: three named rows'
worth, reversed in a `finally`, local profiles only), Keel's base query, a dataset sized free to the fake's 27, a page of 25
for 150, three emails for 36, links in one Text batch, one found person through FOUND -> LINK_MADE -> OPENED -> ANSWERED,
*Make a new link* (the old link 404), a second page and a second dataset that repeat nobody, `FORMAT_NOT_AVAILABLE`, both
422 credit refusals at 20 and the ledger's HOLD / SPEND pairs at `price_version` 8; S-005 asserts `NOT_B2B`. They are scored
by `evals/contacts_marks.py` (CM1-CM14, `CONTACTS_MARKS_VERSION` 1, a journey ruler apart from `MARKS_VERSION`). **Since spec
043's second commit they run keel-cloud-docs `a4f2c95` (DRIFT #83 closed) on keel-web `752a8c4` (068: People became
Interviews)**: every journey's links are made on Sent's *Send more* (W1 held once per account), the contacts leg runs on
068's own screens (`harness/interviews_screens.py`) with every wire assertion kept, and the readings 068 no longer
starts are started on the wire in a step named DRIFT #84.
`make unit` after 043: **1,912 passed / 53 skipped**. **Since spec `044-ai-interviewer-journey` (2026-10-15) they run
keel-cloud 094 + 095 (keel-cloud-docs `a0b3759`: contract 16, `InferenceCharge` 9 -- `price_version` 9 on every HOLD --
document 22, read on arrival) on keel-web `d23895f` (069: the AI interviewer), served `vite --mode test` for the speech
seam.** Step 5 is three screens (L1 *Who asks the questions*; on the own door one line and *Lock and approve*). S-006 ends
with **the interviewer leg** (`evals/interviewer_leg.py`) after the contacts leg: the own-AI refusals, the founder stood
on Keel's door (spec 043's stand-in, keyed `e2e-eval:044:`), Saskia (Chukwu before spec 083, Tito before 058) recorded from Sent's persona line (NOT_RECORDED ->
RECORDING -> READY on keel-cloud's fake renderer), S1 / S2 / S3, W1 replayed, Try it yourself writing nothing, an AI link
answered on the stranger's own stage through `window.__keelSpeech` (`harness/interviewer_screens.py`), a Let-them-choose
link, Daphne for 400 (Livia before 083, Judy before 058), the refusal at 100, the readings on arrival and nothing left unread; S-005 the short form with its AI
link answered. Scored by `evals/interviewer_marks.py` (IM1-IM13, `INTERVIEWER_MARKS_VERSION` 1; IM12 unmeasured, DRIFT
#86). The journeys' readings: on Keel's door nothing is pressed (095); on the own door with the agent connected first the
founder's session asks, as before. `stack/ledger.py` also reads the stored recording (the scripts are on no route). DRIFT
#84 resolved; #85-#89 new. `make unit` after 044: **2,035 passed / 53 skipped**. **Since spec `045-brief-on-return`
(2026-10-16) they run keel-cloud 096 (keel-cloud-docs `7b1e4f6`, document 23)**: no batch writes the brief; after every
answer is read each journey holds no BRIEF, comes back as the founder (`GET overview`) and sees exactly one land
(`_brief_on_return`); IM13 reads `brief:on-return` and fails `brief:after-batch`. **Since spec `046-founder-feedback-2026-10-16`
(2026-10-16) they run keel-cloud 097 (contract 17, keel-cloud-docs `3002978`) and keel-web 070 (`752e873`)**: Importance's
first draft is the own item alone and its Answer names the others (01-countly one, 05-paidly two, the founder typing the
rest on the Check screen -- *yours + n*, the one-more ask, 422 `ONE_MORE_NEEDED`); a first draft leaves a role the
founder has not written to the Answer's redraft (`L6`); the idea arrives unnamed (approve 422 `IDEA_NAME_REQUIRED`) and
every founder types its name on S2; own + 1 / own + 2 on the wire; the own-AI batch 422 `INTERVIEWER_NEEDS_CREDITS`; the
AI flow with no *Next question*; Select all / Clear and no Copy on Contacts. Scored by `evals/feedback_marks.py`
(FM1-FM6, `FEEDBACK_MARKS_VERSION` 1, owed where the record carries the subject) at the end of every journey. DRIFT
#85, #87-#89 resolved, #90 new. `make unit` after 046: **2,074 passed / 57 skipped**. **Since spec `048-answer-path` (2026-10-16) they run keel-cloud 099
(contract 18, keel-cloud-docs `0f582b2`) and keel-web 072**: no *That's my answer*; the AI link's intro tests the mic;
every spoken answer is read by the cloud's classifier (the stack's FakeClassifier -- the eval's seam puts no `classify`
on the page) and held, asked *Is that right?*, or missed; Back once, "no" in a hold once; the classifier guard
(`harness/classifier_guard.py`) sends the canon's 152 spoken-answer cases carried onto the link's own items before it is
answered, and through Try it yourself's founder route; S-006 answers one link from the recorded path on the wire (`how`
RECORDED); IM14-IM18 (`INTERVIEWER_MARKS_VERSION` 2). `MARKS_VERSION` stays 19 and the corpus revision 11 (099 moved no
screen and no corpus item; its `classify-answer.md` is guarded here, not by the instruction eval). **Since spec
`049-hear-them-out` (2026-10-16) they run keel-cloud 100 (keel-cloud-docs `d2f00d4`) and keel-web 073 (`baf934f`)**:
nothing lit while they speak, the utterance read after a quiet gap (the walk encodes no length: 1.5 s at 073, 4.0 s
from 074); the cases copy carries 100's 18 `readaloud` cases (170); one question read aloud, then answered (IM19); a
pick-two by taps and *Save and next* (IM20); the pilot's yes held and on by itself; `INTERVIEWER_MARKS_VERSION` 3,
`MARKS_VERSION` 19 and corpus r11 unchanged; DRIFT #91 (the recorded pilot ask refused on an answered link). **Since spec
`051-follow-up` (2026-10-17) they run keel-cloud 103 (contract 19, the interview side, keel-cloud-docs `4cda99a`) and
keel-web 076 (`c9ce17c`)**: the one follow-up on the first rung against -- the cloud walks and composes
(`POST .../interview/follow-up`), the harness's `LADDER` copy and `first_rung` (`harness/interviewer_fake.py`, held to the
registry export) are the independent check; every text walk meets it where owed; the story's box spoken (T1 -> T4) and
refused (T6) through `text_seam`; the AI links' two windows by way of Back (S-005 pause then Save; S-006 recorded 4 s
then silent to the seam's cap); the FOLLOW_UP clips and their backfill; the consent line with names; IM23-IM27,
`INTERVIEWER_MARKS_VERSION` 5. **Since spec `054-guide-welcome` (2026-10-17) they hold keel-web 080's welcome over
keel-cloud 106 (contract 20, keel-cloud-docs `7c4d9a9`)** right after the project (`leg_welcome`): once per project,
Skip the one control at both sizes, `guide-seen {what: WELCOME}` 204 and idempotent, the revision unmoved; S-005 local
walks the cues and replays it; G1-G5 in `evals/guide_marks.py` (`GUIDE_MARKS_VERSION` 1); every other journey passes it
by (`MarketStep.start(welcome="pass")`). **Since spec `059-sent-rework-marks` (2026-10-20) they hold keel-web 088's
Interviews › Sent over keel-cloud 111 (contract 24, keel-cloud-docs `096cecc`)**: every open of Sent goes through one
helper, `harness/interviews_screens.pass_interviews_sheet` (`Interviews.land`, `Contacts.go_to_send_more`,
`interviewer_screens.Persona.sent`), which skips the first-open sheet (`guide-interviews`, a lazy chunk, 30 s) when it is
drawn and keeps the pass in `j.guide["interviews"]`; only S-005 holds it up and judges it (`land(sheet="hold")`, G13).
`register()` walks the TanStack table page by page with Next (never the search box) and puts it back on page 1; the row
actions are *See answers, {name}* / *New link, {name}*; each role card's count is `role-count`. G13-G17 in
`evals/guide_marks.py` (`GUIDE_MARKS_VERSION` 3): S-005 measures all five (the sheet once, Sent's pill's two chapters in
place and no pill on the consumer Contacts card, the order, the table at 12 links, the counts before and after the
answers); S-006 measures G14's Contacts pill and G16's paging (23 links). IM30 (`INTERVIEWER_MARKS_VERSION` 7): the
who-asks band's *Hear <name> · 5 s* plays her hello in the band, on both legs; W1's replay reading retired with *How it
works*. `MARKS_VERSION` stays 20 (spec 059 judgement call 3). **Since spec `060-sample-snapshot` (2026-10-21) `make sample` runs S-006 with `KEEL_SAMPLE_EXPORT` set** (`evals/sample_export.py`): at its twenty answers, before the contacts leg, the founder's reads of the finished project (overview, plan, standings, roles, people, readings and every batch, invitations and every link) are written as static JSON with a `manifest.json` into keel-web's `public/sample/` (or the directory the variable names), the people's names kept as served (spec `061-sample-names-kept`, 2026-10-22; 060's *Person n* retired), emails and the founder gone, tokens `withheld`; it refuses (exit 1, after S-006's own marks) unless the decision is `BUILD_BUT_CHANGE`, the three verdicts and every dimension's n are the entry's own, and the pilot and the price line are there. Unset, S-006 is unchanged; committing the snapshot is the operator's step, in keel-web. **Nothing generated is committed** -- the script, the
keys table and the typed inputs go into the run bundle, and `Corpus.verify_unchanged()` is called at
the end of every run.

throughout; S-002 (`evals/test_s002_agent_optional.py`, spec 006-agent-optional) starts from a
project S-001 already built (in the same stack session) or its own prelude, then stops the
runtime and proves everything a founder owns keeps working with no agent except creating a
project and reading answers — it found the product offering the read action anyway, refused only
on the wire and never explained on the screen (`runs/DRIFT.md` #17). The evidence bundle
(`runs/<id>/`, report.html) is the product of a run; the scoring policy (`evals/policy.py`,
versioned) is the yardstick. `make up / eval K=s001|s002|s003|s005|s006|s007|s014|s015|s016|s017 / down`; quickstarts in
`specs/*/quickstart.md`.

**Two referee sessions never share the eval profile.** The stack's ports (55432/18080/5173/18090)
and
runtime home are fixed per profile, not per process — a second `make up`/`make eval`/`make down`
against the default (eval) profile while another is mid-run restarts keel-cloud and drops the
database out from under it (live-confirmed: two sessions racing the same checkout, 2026-09-03).
If a stack session is already running S-001 on eval, use the split-stacks playground profile for
your own instead (relay-design.md §12.5) — its own ports, its own Postgres project, and (spec
005) its own runtime home (`runs/.stack/keel-home-playground/`, never the eval profile's
`keel-home/`):

```bash
make up PROFILE=playground
make eval K=s001 PROFILE=playground
make down PROFILE=playground
```

`make eval`/`make eval-all` read `PROFILE` via the `KEEL_EVAL_PROFILE` env var they set for
pytest (`evals/conftest.py`'s `stack_config` fixture); nothing here defaults to guessing which
profile a running stack is on, so a mismatched `PROFILE` just attaches to (or boots) the wrong
one's own three ports.

**There is a third profile, and it starts nothing** (spec `017-remote-profile`).
`PROFILE=remote` names three URLs read from `KEEL_REMOTE_WEB_URL` and its two optional companions
instead of booting anything: `make up PROFILE=remote` asks whether they answer and `make down
PROFILE=remote` is a no-op. It exists for the staging twin the matrix runs against (keel-cloud
`canon/designs/e2e-matrix-design.md`), and the invariant it is written around is that the eval and
playground profiles behave exactly as they did — if you are changing something in `stack/` or
`harness/browser.py`, that is the property to keep. README's *remote profile* section has the
variable table.
