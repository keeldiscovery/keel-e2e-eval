# Implementation Plan: the Keel's-AI door

**Branch**: `024-keels-ai-cell` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the code goes

| File | What it is |
|---|---|
| `harness/keel_host.py` | **New.** The fourth `AgentHost`, and the only one that is not a host. It installs nothing, says nothing, starts nothing, and **refuses every host-leg method by raising with a sentence**. What it does carry is the three facts the scenario still needs from a host object: which executor the wire must report (`api`), how this run is authenticated (it is not — the key is keel-cloud's), and a count of the subprocesses it has run, which is always zero and is asserted. |
| `harness/agent_host.py` | `keel` joins `HOSTS`; `HOSTS_WITHOUT_A_CLI` names it; `EXECUTOR_FOR_HOST["keel"] = "api"`; `INSTALLS` gains `none`; `bundle_slug` learns that `none` is the absence of a road and not a third one; `host_type` routes it. |
| `evals/test_s012_journey_through_a_host.py` | The door branch. Four things: sign **up** instead of in, skip leg one whole, assert the door's own six facts, and read the per-job `execution` off the **wire** instead of off a runtime home that does not exist. Every other line is the line that was there. |
| `harness/browser.py` | `Shell.credits_line_text()`, `Shell.agent_line_present()`, `Shell.says_your_ai()`, `Chat.chat_name()` — four reads, no actions. (`Auth.sign_up` landed with the door-words commit that precedes this one.) |
| `matrix/cells.toml` | `[axes].host_without_a_cli = ["keel"]`, and one cell in `weekly`. |
| `matrix/cells.py` | The new axis list, `install = "none"`, and three coverage rules: the hostless host is weekly's alone, exactly one of it, and never in `per_change`. |
| `Makefile` | `make keels-ai` — the founder's one command for this door. |
| `tests/test_keels_ai_cell.py` | **New**, stackless: the axis, the bundle, the refusals, the wire readers, the cell, the make target, the coverage rules. |
| `AGENTS.md`, `README.md` | The third named LLM place gains a door; the README gains the command and what it costs. |

## 2. The decisions, each with the reason it was taken

### The host is called `keel` and the wire is called `api`, and the bundle carries both

`execution.host` is keel-runtime's and now keel-cloud's word for *which thing did the thinking*,
and spec 045 FR-043 makes it `api` — truthfully, because there is no CLI and no host, only an HTTP
client against a provider. But `api` is a terrible thing to read in
`macos-latest-api-py3.13 · s012-journey-api · PASSED`: *api* names a transport, and the fact a
reader of eight weekly rows needs is **which door the founder came in through**. The founder-facing
name for that is Keel's AI.

So the axis value is `keel` — cell id, bundle name, summary row, `KEEL_REMOTE_CELL`, the founder in
the twin's picker — and `EXECUTOR_FOR_HOST["keel"]` is `"api"`, which is what is asserted. They are
two vocabularies about two subjects and the bundle prints them side by side with a sentence saying
so. The alternative, naming the axis `api`, would have made the id honest about a mechanism nobody
asked about and dishonest about the thing the cell exists to measure.

### The Python axis is inert on this cell, and the bundle says so rather than the id

A cell's Python is *the runtime's* — what `python3` resolves to when the host CLI runs the skill's
script. This cell runs no script, so its Python axis measures nothing; the harness's own
interpreter is 3.12 on every cell and is never the axis. The id shape is not changed for it
(`macos-latest-keel-py3.13`): one id rule everywhere is worth more than a second id shape, ids are
founders in the twin's picker, and a reader who wants to know what the 3.13 bought opens the
bundle, where `versions.json` says in one line that nothing on this cell is run by it. The OS is
**not** inert — Playwright's Chromium and the whole founder journey run on it.

### It is `weekly`, and the coverage rules refuse it anywhere else

Every other live cell spends **the founder's own plan** — his Max subscription, his Copilot seat,
his OpenAI key. This one spends **Keel's Anthropic account**, which is the company's money and the
same account real founders' jobs will run on. A `per_change` cell would bill the company on every
merge. `ai-credits-design.md` §6.3's five-participant row is the number: **1,250 credits**, which
is **$12.50 at list** and **$2.44 of actual inference**, per run. Weekly, that is about ten dollars
a month; per merge it would be whatever the week's merges happened to be.

So: one cell, `weekly`, `macos-latest`, `3.13`, `full`. And rather than leave it to memory,
`coverage_problems` gains three rules — a hostless host appears in `weekly` and nowhere else, at
most once, and never in `per_change` — each with that sentence in its message.

### `install = "none"` is a value, and it does not appear in an id

The install axis answers *how did the skill reach the host*. On this door there is no skill and no
host, and answering `plugin` would put a lie in `versions.json` and in the cell's own data. So
`none` joins `INSTALLS` in both readers. But a cell id of `macos-latest-keel-py3.13-none` reads as
a third packaging road, which is the opposite of what it means, so `Cell.id` and `bundle_slug`
name the install only when there **is** one. One rule, stated once in each file: *`none` is the
absence of a road, not another road.*

### The per-job facts come off the wire, because there is no runtime home to read

Every other host proves what answered from **the runtime's own artefacts** — `canary.wait_for_
envelopes` over `<KEEL_HOME>/jobs/*/envelope.json`, written by the process that ran the job — and
that rule (*never the model's prose*) is the whole of S-012's evidence discipline. There is no such
process here, so the equivalent reading is keel-cloud's own `execution` report on the job, which is
written by the executor and not by the founder, not by the model, and not by this harness.

That is not a weaker reading; on this door it is the **only** one, and the absence of the other is
asserted rather than papered over: FR-008 requires `KEEL_HOME` to be empty at the end, which is the
proof that nothing else could have written anything. The scenario keeps its existing shape —
`agent_host.read_heartbeat(keel_home) is None` is the same call it already makes at §1.0 — and adds
the same call at the end.

### A named refusal is raised where it happens, not waited out

`_land_the_card`'s three benign follow-ups exist because a *live model* sometimes answers a claim
box with a question, and a founder would say more. They are the wrong response to
`LLM_UNAVAILABLE: KEEL_AI_DISABLED`, which is not a model being conversational — it is a door with
no key behind it, and every follow-up spends another 30 credits arriving at the same sentence.

So the wire read that already happens when the screen stops changing
(`refusals.why_the_stage_stopped`) is extended by one: if the failure's message names one of spec
045's four reasons, raise **there**, with keel-cloud's own words. The bounded follow-ups still
apply to everything else, unchanged, on every host. This is deliberately a **new refusal reader**
(`harness/refusals.py::named_reason`) rather than a branch inside the scenario, so the four names
live in one place and `make unit` can hold them.

### The founder's words are swept for *your AI*, not asserted sentence by sentence

keel-web spec 024 FR-014 rewrites twenty-seven strings through one function (`perDoor`, replacing
`Your AI`/`your AI` with `Keel`). Pinning twenty-seven sentences here would make this repository a
second copy of keel-web's own `translate.ts` and would go red on a copy-review the founder has not
finished. What is asserted instead is the **property** the substitution exists to produce: on a
founder screen inside a `KEEL` project, the chat's own name reads `Keel`, and the words *your AI*
appear nowhere. Two screens, two sweeps. Marketing pages are not swept — `/plans` and the landing
describe the own-AI road on purpose, and always will.

### Nothing in `matrix.yml` changes, and that is a finding worth writing down

Every host-specific thing the cell job does is already gated on `matrix.cell.host == '<name>'`: the
three npm installs, the four secret lines, the Copilot model pin. A `keel` cell matches none of
them and therefore installs nothing, receives no secret and pins no model — which is exactly right,
because the only key involved lives on the twin and belongs to keel-cloud. The workflow is
untouched. The cell is data.

## 3. What is deliberately not built

- **No local dry run of the journey.** This repository has three profiles (`eval`, `playground`,
  `remote`) and no recorded or replayed mode — no Prism, ever (`AGENTS.md`). The `eval` profile
  boots keel-cloud from the sibling checkout, so a local run would need that checkout on
  `044-ai-credits` **and** spec 045 built, and 045 is an untracked draft with no code. What is
  exercised here is every stackless property; what waits for the twin is named, per assertion, in
  `tasks.md` Phase 6.
- **No `KEEL_JOURNEY_HOST=keel` default anywhere.** The default is still `copilot`, for spec 019's
  reason: every command written down before today must still mean what it meant.
- **No second scenario file, no `HOST=both`, no averaging.**
- **No keel-cloud or keel-web change.** Two of the three things this cell needs are on branches and
  one does not exist; none of that is this repository's to fix. `runs/DRIFT.md` is for what a *run*
  found, and no run has found any of it.

## 4. Risks, and what each one costs

| Risk | Cost | What is done about it |
|---|---|---|
| The twin has no spec 045 (today's state) | one red cell a week | The cell fails at the first job with keel-cloud's own sentence in the verdict — `422 rule: "agent"` at New project today, `LLM_UNAVAILABLE: KEEL_AI_DISABLED` once 045 lands without a key — never a timeout, never a five-minute wait. |
| keel-web's spec 024 is not on the twin | the cell fails at the first screen | `/signup` would 404 into keel-web's router and the door card would not render. It fails inside twenty seconds on a named locator, which is the cheapest possible failure. |
| A `null` `actual_cost_micro_usd` (X6 unmet, which is today's state everywhere) | one red cell | Asserted, on purpose, naming X6. A cell that passed on a null would certify the one thing spec 045 exists to deliver. |
| The founder's copy review moves keel-web's *Keel* wording | a red cell on a green product | Only the property is asserted, never a sentence: the chat's name, and the absence of *your AI*. Both survive a rewording. |
| `1,500 credits available` is a formatted string | a red cell if keel-web reformats | It is pinned because it is the founder's own number in the founder's own words and `creditsAvailable == 1500` is asserted **beside** it on the wire, so a formatting change and a grant change are told apart by which assertion failed. |
| Somebody adds the cell to `per_change` | a bill per merge on the company's own account | Three coverage rules in `matrix/cells.py`, enforced by `make matrix-check` as well as by `make unit`, each carrying the sentence about whose money it is. |
| Two runs of the cell in one day near the daily cap | the second fails `KEEL_AI_DAILY_CAP` | A weekly cell runs once. If it is dispatched by hand twice, the second fails fast with that name in the verdict, which is the correct outcome and is the same FR-010 path. |
