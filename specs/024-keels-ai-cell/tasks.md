# Tasks: the Keel's-AI door

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `024-keels-ai-cell`

`make unit`: **1031** before this branch, **1041** after the two commits that precede this feature
(the door-words fix and `keep_twin`), **1092** after phases 1-6, **1105** after
phase 7, **1111** after the reading button, **1119** after phase 8,
**1127** after phase 9. Green.

## Phase 0 — the two things the matrix found first, each its own commit

Neither is this feature; both were in its way, and both are the same class of fault as the one
`tests/test_the_strangers_door.py` was written for.

- [X] T001 **The Google button's word belongs to the door** (`cd3ceff`). keel-web spec 024 FR-004
      renamed the plain `/login` card's control to *Log in with Google*; `evals/conftest.py`'s
      session-scoped stack-boot capture named the old word, matched nothing, and reddened every
      cell before a scenario ran. Three doors, three words, one table
      (`Auth.GOOGLE_BUTTON_FOR_DOOR`), and `Auth` now carries which door it is looking at. The
      `/signup` row is what this feature then signs up through.
- [X] T002 **`keep_twin`** (`cab0585`). A `workflow_dispatch` input that skips `stop-staging`, for
      the founder's manual testing, ANDed onto that job's existing condition so a red cell still
      stops the twin when the flag is false; and `deploy the twin` made honest about a box that is
      already running.

## Phase 1 — read before writing anything

- [X] T003 keel-cloud `canon/designs/ai-credits-design.md` §5 (the 1,500-credit grant, once per
      Google `sub`, at the moment the `founder_account` row is written), §6 (*the door decides the
      AI*; §6.2's one line at the top right; §6.3's cost table), §7 (the one gate, at New project,
      below 540) and §8 (the ledger, and X1: the `HOLD` is written in the same transaction as the
      job insert). **What decided the cell's set**: §6.3's five-participant row — 1,250 credits,
      $12.50 at list, $2.44 of Keel's own inference.
- [X] T004 keel-cloud `specs/044-ai-credits/spec.md`: FR-013/FR-014 (`GoogleSignIn.doorOf` reads
      the pre-login record's stored `return_to`; `/connect` is `OWN`, everything else is `KEEL`),
      FR-017 (+1,500 in the account-insert transaction), FR-028 (the 409, `required: 540`),
      FR-033 (`/v2/me.aiPath`, `creditsAvailable`, **null on OWN and never absent**). **Found**:
      044 is implemented on the branch `044-ai-credits` (`a5474c5`) and **not on `master`**.
- [X] T005 keel-cloud `specs/045-keels-ai-executor/spec.md`: FR-043 (`execution.host: "api"`, and
      the `execution.host` enum gains `api`), FR-023/FR-025/FR-027 (`actual_cost_micro_usd`,
      summed over every call the job made, **0 when it failed before any**), FR-032
      (`LLM_UNAVAILABLE: KEEL_AI_DISABLED`), FR-037 (the $10.00 daily cap), FR-039
      (`EXECUTOR_TIMEOUT` / `KEEL_AI_TIMEOUT`), FR-045/FR-046 (a `KEEL` account is not asked for
      an agent), FR-047 (its `agent` block is still answered, truthfully, as not connected).
      **Found, and it changed two things**: 045 is an **untracked draft** — no code, no commit, no
      branch, and `KEEL_AI_DISABLED` exists nowhere in keel-cloud but its own spec. And
      **Assumption 11**: none of the four named reasons is an `error.code`; they travel in
      `error_message`, which is why `keel_host.named_reason` reads a message and not a code.
- [X] T006 keel-cloud `canon/openapi-v2.yaml` on `044-ai-credits`: `MeResponse.aiPath`
      (`enum: [KEEL, OWN]`), `MeResponse.creditsAvailable` (`[integer, "null"]`, int64, **may be
      negative**), `CreditRefusal`, and `execution` — whose `host` enum is still
      `[claude, copilot, codex]`. **The `api` value does not exist on the contract yet.**
- [X] T007 keel-web `specs/024-front-door/spec.md`: FR-003 (`/signup`, *Sign up with Google*,
      `return_to=/`, and *"this door marks the account KEEL, server side … keel-web sends nothing
      to say so"*), FR-004, FR-011 (`<CreditsLine/>` vs `<AgentLine/>`, `.creditsline`,
      `creditsLine()`'s exact `${amount} credits available` with `toLocaleString("en-US")` and no
      plural), FR-013 (the gate card and the lock are **not rendered** on KEEL), FR-014
      (`AI_SUBJECT_KEEL`, twenty-seven strings through one `perDoor`), FR-016 (`.credits-refusal`),
      FR-020 (an unknown `aiPath` falls to the own-AI road). **Found**: implemented on the branch
      `024-front-door` (`f2627e1`), not on `master`.
- [X] T008 This repository: `harness/agent_host.py` line by line (which of its rules are a *host's*
      and which are the *journey's*), `evals/test_s012_journey_through_a_host.py`'s four arms,
      `matrix/cells.py`'s six coverage rules, `.github/workflows/matrix.yml`'s cell job.
      **Found, and it saved a workflow change**: every host-specific step and secret in the cell
      job is already gated on `matrix.cell.host == '<name>'`, so a `keel` cell matches none of
      them and `matrix.yml` needs no edit at all.

## Phase 2 — the decisions, taken before a line was written

Each is argued in [plan.md](plan.md) §2; this is the list.

- [X] T009 **The door is `keel` and the wire is `api`**, and the bundle carries both with the
      sentence saying why.
- [X] T010 **`weekly` only, one cell, macOS, 3.13, full, and `install = "none"`** — because the
      money is Keel's, not the founder's.
- [X] T011 **`none` is not a road**, so it is a value in `INSTALLS` and is named in no id and no
      bundle.
- [X] T012 **The per-job facts come off the wire**, because there is no runtime home to read, and
      the *absence* of that home's contents is asserted rather than assumed.
- [X] T013 **A named refusal is raised where it happens**, and only that door chunks its wait.
- [X] T014 **The founder's words are swept for *your AI*, not pinned sentence by sentence.**
- [X] T015 **The Python axis is inert on this cell**, and the bundle says so rather than the id.

## Phase 3 — the harness

- [X] T016 `harness/agent_host.py`: `keel` on `HOSTS`; `HOSTS_WITHOUT_A_CLI` and `has_a_cli()`;
      `EXECUTOR_FOR_HOST["keel"] = "api"`; `KEELS_AI_GRANT = 1500`; `INSTALLS` gains `none` and
      `bundle_slug` learns not to name it; `host_type` routes `keel`.
- [X] T017 `harness/keel_host.py`: `KeelHost` (free `readiness`, a `credential_plan` that says
      there is none and whose key it is, a `write_home_config` that writes nothing, and
      `NoHostHere` from every host-leg method), `execution_facts`, `NAMED_REASONS` and
      `named_reason`.
- [X] T018 `harness/browser.py`: `Shell.credits_line_text`, `Shell.credits_line_present`,
      `Shell.agent_line_present`, `Shell.says_your_ai`, `Chat.chat_name` — five reads, no actions.
- [X] T019 `evals/test_s012_journey_through_a_host.py`: `KEELS_AI`, the sign-up branch, the door's
      landing assertions, leg one under `else`, the credits-before/after pair, the words sweep, the
      wire-read cost block, the empty-`KEEL_HOME` proof, the absent way out, and the bundle's own
      one-line fact.
- [X] T020 `Makefile`: `make keels-ai`, with what it costs and whose account it is written above
      the recipe.

## Phase 4 — the cell

- [X] T021 `matrix/cells.py`: `hostless_hosts`, `NO_INSTALL`, the id rule, and three coverage
      rules — weekly's alone, exactly one, never `per_change` (with the message naming whose money
      it is).
- [X] T022 `matrix/cells.toml`: `[axes].host_without_a_cli = ["keel"]` and the ninth weekly cell.
- [X] T023 `.github/workflows/matrix.yml`: **nothing but the header comment's count**, which is
      the finding of T008 stated as a diff.

## Phase 5 — what a stackless test can hold

- [X] T024 `tests/test_keels_ai_cell.py` — **50 tests**: the axis and its typo, the two
      vocabularies, the bundle name, the seven refusals, the free readiness, the empty home, the
      wire readers (including a `null` cost reading as *not reported* and a `True` reading as *not
      an integer*), the four named reasons, eight of the scenario's own assertions by the words
      they are made in, the cell, the coverage rules (a `keel` cell in `per_change` **and** a
      second one in `weekly`, each refused), the workflow needing no gate, and the make target.
- [X] T025 The four existing tests the new value touched, each corrected to say what it always
      meant rather than loosened:
      * `tests/test_journey_through_a_host.py` -- its eleven `parametrize(agent_host.HOSTS)`
        decorators become `agent_host.CLI_HOSTS`. Every one of them is about a **command line**,
        and a door with no argv has none; asking it for one would have been asking the wrong
        question rather than finding a bug. Its two table tests keep their three CLI rows and gain
        the fourth's two names.
      * `tests/test_matrix_cells.py` -- `test_weekly_is_eight_cells_…` still counts **the
        founder's eight**, by the same filter that already excluded the Spec Kit road; the ninth
        gets `test_weekly_carries_the_one_keels_ai_cell` of its own.
      * `tests/test_s012_copilot_host.py` -- its one ordering assertion read the heartbeat step by
        an exact indent, which spec 024's `else:` arm moved. It reads a pattern now: the property
        is the *order*, and a test that also pinned a column said nothing about it.
      Everything else in all four is green **unchanged**, which is the cheapest proof that no
      existing cell was weakened.

## Phase 6 — the documents

- [X] T026 `AGENTS.md`: the third named LLM place is **widened by a door**, and says so — with the
      sentence about whose money it is, because that is the fact that decides which set buys it.
- [X] T027 `README.md`: *…and one of them has a fourth door*, the two commands, what it costs, what
      it asserts, how it fails fast, and that it has never been run.

## Phase 7 — the run, which is the founder's to spend

- [ ] T028 `make keels-ai` against the twin. **Not run, and not runnable today.** It needs three
      things this repository does not own and two of which do not exist yet:
      1. keel-cloud spec 044 deployed (it is on the branch `044-ai-credits`, not `master`);
      2. keel-cloud spec 045 **built** (it is an untracked draft — no code, no commit);
      3. keel-web spec 024 deployed (it is on the branch `024-front-door`, not `master`);
      4. `KEEL_ANTHROPIC_API_KEY` in SSM at `/keel/staging/anthropic-api-key`, created by hand by
         the founder (spec 045 FR-029).
- [ ] T029 Whatever T028 finds → `runs/DRIFT.md`, `README.md`, and this file.

### What was exercised locally, and what waits

| Asserted | Exercised here | Waiting for the twin |
|---|---|---|
| the host axis, the bundle name, `keel` vs `api` | `make unit` | — |
| leg one refuses rather than returning an empty result | `make unit` (seven methods) | — |
| the free readiness, the empty `KEEL_HOME`, the zero subprocesses | `make unit` | the *end-of-run* emptiness, which needs a run |
| `execution_facts` on every shape a job can be in, `named_reason` on all four | `make unit` | a real `execution` block from keel-cloud |
| the cell, its set, its id, and the three rules that keep it off `per_change` | `make unit`, `make matrix-check` | — |
| the scenario's own eight assertions, by the words they are made in | `make unit` (source-level, as `tests/test_journey_through_a_host.py` does) | the assertions themselves |
| the axis resolving at import with `KEEL_JOURNEY_HOST=keel` | `pytest --collect-only` | — |
| `1,500 credits available`, no agent line, `aiPath: "KEEL"` | — | **the twin** |
| the balance dropping on the first `HOLD` | — | **the twin** |
| `execution.host == "api"`, `actual_cost_micro_usd > 0` | — | **the twin, and keel-cloud spec 045** |
| the founder's screens saying *Keel* | — | **the twin, and keel-web spec 024 deployed** |
| failing fast on `KEEL_AI_DISABLED` within a minute | — | **the twin, with the key removed** |

There is no third way to exercise the rest. This repository has three profiles — `eval`,
`playground` and `remote` — and no recorded or replayed mode; `AGENTS.md` says **no Prism, ever**,
and the two local profiles boot keel-cloud from the sibling checkout, which would have to be on
`044-ai-credits` with spec 045 built. It is not.


## Phase 7 - the other three doors were on the wrong one (2026-09-29, its own commit)

Found while writing this spec, and the more urgent half of it: keel-cloud reads the door off the
stored `return_to` of the sign-in that **creates** an account, and S-012 signed in at the plain
`/login` before it installed anything. On the twin every cell registers a brand-new identity
minutes earlier, so every CLI cell was creating a `KEEL` account with a 1,500-credit grant -- and
once keel-cloud spec 045 lands, keel-cloud would answer eight weekly cells' jobs on **Keel's own**
Anthropic key instead of on the CLI each cell had just installed.

- [X] T030 Read keel-cloud's `GoogleSignIn.doorOf` and `SecurityConfig` line by line. **Two
      findings that decided the shape of the fix**: `doorOf` is called **only on the create
      branch**, so a returning founder's door cannot be moved by anything; and
      `GET /v2/device-authorizations` is **`founderSession`-gated** while the two POSTs beside it
      are `permitAll`, so *"is this a code this Keel issued"* cannot be asked before the sign-in
      by anybody -- including keel-web's own code story.
- [X] T031 `harness/browser.py::Auth.sign_in_with_code` -- the one door that answers `OWN`,
      named for what it is rather than spelled out at four call sites.
- [X] T032 `harness/agent_host.py::ai_path_facts`, `AI_PATH_OWN`, `AI_PATH_KEEL` -- one reader
      that tells a **null** balance from an **absent** field (spec 044 assumption 8).
- [X] T033 `evals/preludes.py::own_ai_door` -- one door assertion for S-012, the corpus riders and
      S-013, asserting only where the answer is about this run and saying which of the three cases
      it got otherwise.
- [X] T034 S-012's legs reordered for the three CLI doors and the Spec Kit road (the table is in
      [spec.md](spec.md)): two assertions added, one split so its session-free half runs
      **earlier**, none removed and none loosened. The Keel door is untouched.
- [X] T035 `evals/corpus_scenario.py` and `evals/test_s013_upgrade_in_place.py` -- the runtime
      starts before the sign-in, and the sign-in carries the code. The riders fall back by name,
      with the reason, when the runtime reconnected on a credential its home already held.
- [X] T036 FR-020: keel-cloud's own `execution` report on a CLI cell must name that cell's host
      and never `api`.
- [X] T037 **13 more stackless tests** in `tests/test_keels_ai_cell.py`: the leg order as an
      ordering property on five anchors, the split assertion moving earlier and not later, the
      session-gated read being after the sign-in *and saying why*, the code surviving the login,
      the one shared door reader and its three guards, the null/absent distinction, both riders'
      order, the rider fallback and S-013's refusal of it, the `execution` cross-check, and
      `sign_in_with_code`'s one `return_to`.
- [ ] T038 A run. Still the founder's to spend, and still not runnable until keel-cloud 044 is
      deployed -- but note that this fix is worth deploying **before** spec 045, not after: 044
      alone writes the wrong `ai_path` and grants the credits, and 045 is what starts spending
      them.


## Phase 8 - the framing alone, at different effort settings (the founder, 2026-09-29)

*"I want to test only the framing-and-assumptions part -- the problem framed, broken into lines and
questions -- at different effort settings, not the whole journey, to keep spend down."*

- [X] T039 `harness/browser.py`: the reading button's word belongs to the door too
      (`READ_BUTTON_FOR_DOOR`, `Shell.door()`). Found by matrix run 36636769648 -- the whole journey
      green on Keel's AI through all three stages, then thirty seconds of waiting on the People page
      for *Have your AI read* where keel-web spec 024 FR-014 renders *Have Keel read*. Its own
      commit; the CLI doors' regex is byte for byte unmoved.
- [X] T040 `evals/test_s012_journey_through_a_host.py`: `_read_the_lines` extracted from
      `_walk_stage_live`, so the framing run and the full journey read the lines through **one**
      function (spec 021's rule, one stage along). It hands the card back un-approved.
- [X] T041 `harness/agent_host.py`: `SHORT_REACHES_THE_ASSUMPTIONS`, `short_reaches_the_assumptions`
      and `short_stops_at` -- one place that says what `short` stops after on each door, and one
      sentence the bundle carries about it. The three CLI doors are unchanged.
- [X] T042 `facts.json` gains *what the framing measured*: the job count, the models that answered,
      the µUSD keel-cloud says it paid, and the wait by this harness's own clock -- and says that
      tokens are not on that wire at all rather than filling a number in.
- [X] T043 `harness/keel_host.py::execution_facts` picks up whatever timing the job row carries and
      names its absence; `tokens` is `None` with the reason.
- [X] T044 `matrix/cells.py`: `legs` joins the id (the argument is in [spec.md](spec.md) FR-028),
      and the coverage rule becomes *one full Keel cell, at most one short one beside it*.
- [X] T045 `matrix/cells.toml`: the tenth weekly cell, with the design's own two numbers above it.
- [X] T046 `.github/workflows/matrix.yml`, `matrix/cells.toml`: the header counts. Nothing else in
      the workflow moves -- a `keel` cell still matches no host-gated step.
- [X] T047 **8 more stackless tests**: the per-door `short`, the one sentence each door gives for
      it, the one shared reader and that it does not approve, the effort line, the absent tokens,
      the wire timing, and that nothing here pins an effort. Plus the id and count expectations in
      `tests/test_matrix_cells.py` moved with FR-028 (the Spec Kit cell's id gains `-short`).
- [ ] T048 One dispatched run of `macos-latest-keel-py3.13-short`, then a second with keel-cloud's
      effort changed, and the two `facts.json` lines read side by side. The founder's to spend, and
      the cheapest paid thing in this repository at about $0.37.


## Phase 9 - the execution report was read off the wrong document (matrix run 36643795391)

- [X] T049 Read keel-cloud `canon/openapi-v2.yaml` on `045-keels-ai-executor` and
      `ConnectDtos.JobDetail`. **`InteractionView.job` is `{job_id, turn_number, status, outcome,
      error}` and carries no `execution` at all**; the report is `InferenceJobDetail.execution`
      from `GET /v2/inference-jobs/{jobId}`, whose `host` enum spec 045 widened to
      `[claude, copilot, codex, api]`, and the key is `execution` (a bare record component, no
      `@JsonProperty`) rather than `execution_payload`.
- [X] T050 `harness/keel_host.py`: `JOB_DETAIL_PATH` and `jobs_with_their_execution` -- one reader
      that fetches each job's own detail and carries the interaction's `screen` across.
      `execution_facts`'s docstring now says which document it takes.
- [X] T051 Both cross-checks pointed at it: the Keel door's cost assertion, and the CLI doors'
      FR-020 check -- which had been **asserting nothing at all** because it filtered on a key the
      stub never has.
- [X] T052 **8 more stackless tests**, against the contract's own shapes: the stub verbatim (and
      that reading it answers `None` to everything, which is the bug), the detail verbatim (and
      every field the fetcher gets out of it, including the screen and the three timestamps), the
      fall-back note when a detail does not answer, an interaction with no job yet, the guard that
      no scenario reads a stub again, the CLI check counting what it read, the framing line reading
      the same number, and the contract's own `api` enum value.
- [ ] T053 Re-run `macos-latest-keel-py3.13-short`. The cell got to its last step on run
      36643795391, so this is the run that closes it.
