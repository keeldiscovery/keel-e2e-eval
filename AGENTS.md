# AGENTS.md

keel-e2e-eval: the referee. It stands the whole connect stack up locally and proves the four
applications (keel-cloud, keel-web, keel-runtime, keel-connect-skill) agree — with each other,
and with the journey. It never talks to keel-skill or the retired agent-protocol/relay surfaces
(archived 2026-09-03, `runs/DRIFT.md`'s dated retirement note); no Prism, ever.

**No LLM except in three named places** (amended 2026-09-06, spec 009; amended again
2026-09-10, spec 016; the third **widened**, not multiplied, by spec 019). Naming them is the
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
  **`MARKS_VERSION` 19** (spec `042-contract-14-r11`, 2026-10-14) is the gate as written, and **there is no run
  of record until `WHY=marks:19` is spent -- the certificate is the founder's word only; never run or
  propose it**. keel-cloud 090 / 091 (merged at keel-cloud-docs `c432c1d`: `CONTRACT_VERSION` 14, the lock one
  RESPONDENT_QUESTIONS job of 35, corpus revision 11) moved four calls under unchanged numbers (110-115): the corpus is
  revision 11 (r10 refused by name; DRIFT #77's five words fixed, 05-paidly's Frequency in months out of 3),
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
  a pass), and what is asserted instead is the six things only that door shows -- 1,500 credits
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
  **Keel's-AI** account with a 1,500-credit grant. The legs are in the founder's own order now --
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
names). The scenario set is **thirteen**.

Rules of this repo: it owns no product code and never fixes the product — cross-repo defects go
to `runs/DRIFT.md` with evidence and get fixed in the owning repo. The **thirteen** scenarios are
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
step round keel-web `844ea36`. Green locally twice against `c432c1d` + keel-web `844ea36`. `make unit` after 042:
**1,857 passed / 53 skipped** (was 1,729 / 28 failed / 142 skipped on the same checkouts). **Nothing generated is committed** -- the script, the
keys table and the typed inputs go into the run bundle, and `Corpus.verify_unchanged()` is called at
the end of every run.

throughout; S-002 (`evals/test_s002_agent_optional.py`, spec 006-agent-optional) starts from a
project S-001 already built (in the same stack session) or its own prelude, then stops the
runtime and proves everything a founder owns keeps working with no agent except creating a
project and reading answers — it found the product offering the read action anyway, refused only
on the wire and never explained on the screen (`runs/DRIFT.md` #17). The evidence bundle
(`runs/<id>/`, report.html) is the product of a run; the scoring policy (`evals/policy.py`,
versioned) is the yardstick. `make up / eval K=s001|s002|s003|s005|s006|s007 / down`; quickstarts in
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
