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
  `prompt:…` or `contract:…` earns one screen, `WHY=new-model:<host>:<model>` earns the full run,
  and a code change earns nothing. Never run it on a schedule, in CI, or "to be sure".
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

  **And it is still one scenario at two lengths** (spec 021). `LEGS=short` stops it after the host
  leg and the **first** model job, which is what every qualifying change now buys; `LEGS=full` is
  what the nightly and weekly sets buy. That is a *stopping point* in one story, not a second
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
instructions against — it is also **the script three browser scenarios run on**. S-005
(`01-countly`), S-006 (`05-paidly`) and S-007 (`07-mulchrun`) generate a keel-runtime script from
an entry (`harness/corpus_script.py`, reading through `instructions/corpus.py` so there is one
reader and one hash), drive it through the real screens, and assert that entry's own `expected`
section where a founder reads it and on the wire beside it. Spec 009 asks *did the prose reach
these beliefs*; these ask *does the product reach these standings*. **Nothing generated is
committed** — the script and the typed inputs go into the run bundle, so a run can never be green
against a script that drifted from a corpus that moved, and `Corpus.verify_unchanged()` is called
at the end of every one.

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
