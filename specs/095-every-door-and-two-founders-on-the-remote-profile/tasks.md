# Tasks 095 -- S-003 and S-010 on the remote profile: the registered identity, and a landing on the issuer is a refusal

Branch `095-every-door-and-two-founders-on-the-remote-profile` (worktree `wt/keel-e2e-eval-095`, `.git` a file, its own
`make venv`), off master `78497a0` (4,741 passed / 0 failed / 0 errors / 53 skipped, as 116 recorded it). Built by
Claude on 2026-10-31. Read only: keel-cloud-docs `ab5b15ef`, keel-web `7a3105f` (the `wt/` symlinks to the masters).
**No stack, no staging, no model, no eval.** Nothing merged into master; the branch pushed after every commit, never
force-pushed.

| Commit | What |
|---|---|
| `3bc241b` | FR-2: `harness/browser.py` -- the issuer-aware predicate, `SignInRefused`, `Auth.sign_in`'s two waits |
| `5b72490` | FR-1: `evals/test_s003_every_door.py`, `evals/test_s010_two_founders.py` -- the registered identities |
| `83bcf34` | `tests/test_sign_in_on_the_issuer_095.py` (14) |
| the docs commit | this file and `AGENTS.md`'s spec-095 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `78497a0` (as 116 recorded it), keel-cloud-docs `ab5b15ef`, keel-web `7a3105f` | 4,741 | 0 | 0 | 53 |
| **branch at `83bcf34` (the last code; the docs commit adds none), the same siblings** | **4,755** | **0** | **0** | **53** |

+14 tests, all `tests/test_sign_in_on_the_issuer_095.py`. The 53 skipped are master's 53. No failure came from another
spec. (A first run in this worktree, started before the edits and overlapping them, read 7 failures in tests that read
`harness/browser.py`'s source at run time; all 185 tests of those four files pass on the branch and the clean run above
is the record.)

## FR-1 The identity is registered -- `5b72490`

- [x] T001 **S-003** signs in as `remote.identity_to_sign_in_as(stack, f"{cell} · every-door · {day}",
  fallback=founder_one)`, the corpus journeys' own call and label shape, before its one `Auth(...).sign_in`. On the
  eval and playground profiles it is the built-in *Eval Founder* with no I/O, as before.
- [x] T002 **S-010** registers its two founders on remote: `identity_to_sign_in_as(stack, f"{cell} · two-founders A ·
  {day}", fallback=founder_one, name=founder_name(founder_one))` and the same for B with `founder_two`. Two calls, two
  `POST /identities`, two ids (`new_identity_id`'s random tail), two `sub`s. Locally the built-ins (*Eval Founder*,
  *Nour Haddad*), as before.
- [x] T003 **`founder_name(builtin)`** (new, `evals/test_s010_two_founders.py`): *{the built-in's first word} {MMDD}
  {cell}* -- *Eval 1031 ubuntu-...*, *Nour 1031 ubuntu-...*. `register_cell_identity`'s default name (*Eval {MMDD}
  {cell}*) would have given both founders the same name, and S-010 reads names three ways: step 3's *"both sessions
  read the same account"* (`me_b["name"] != me_a["name"]`) would fail outright, and `name.split()[0] in greeting` (steps
  1 and 3) and step 7's `founder_two.name not in asked_by` would hold nothing. With the built-ins' first words the
  assertions are as strong on the twin as locally.

### Every other browser-path caller of the built-ins (listed, not moved -- FR-3)

Each of these signs in as `founder_one` / `founder_two` / `FOUNDER_ONE` as handed, so on the gated twin each would now
**raise `SignInRefused`** (M6's line) at its sign-in step instead of passing it and failing a step later. None is in a
`matrix/cells.toml` set (the static `test_scenarios_use_the_stack_addresses.py` gate holds the ones that are).

| Where | Who | Note |
|---|---|---|
| `evals/test_s001_smoke.py:102` | `founder_one` | S-001 |
| `evals/test_s002_agent_optional.py:180, :206` | `founder_one` | S-002, twice (the second after the runtime goes away) |
| `evals/test_s004_stranger_who_gives_orders.py:420` | `founder_one` | S-004, live, deselected from `make eval` |
| `evals/test_s008_bundled_runtime.py:283` | `founder_one` | S-008 |
| `evals/test_s009_skill_distribution.py:372` | `founder_one` | S-009 |
| `evals/test_s011_bad_token.py:158, :162, :171, :217, :224` | `founder_one` | S-011's refusals and its real sign-in; `:197` replays a code with `&identity={founder_two.id}` by `page.goto`, not through `Auth` |
| `evals/tools/curated_proof_run.py:854` | `FOUNDER_ONE` | the curated proof tool, local by design |
| `harness/browser.py` `Auth.log_in` | `FOUNDER_ONE` (default) | no caller in the repo |
| `evals/conftest.py` `_capture_the_login_screen` | -- | reads `/login` only, signs nobody in |

Not a browser path (the wire): `stack/auth.py` `sign_in_session` / `login_and_keel_session` default to `FOUNDER_ONE`
(callers: `tests/test_remote_profile.py` only). Already registered (unchanged): the corpus journeys
(`corpus_scenario.run`: S-005/6/7/14), `scope_journey` (S-015/16), `open_link_leg` (S-017), S-012, S-013, and the
back-test (`backtest.sign_in`, its own `register_cell_identity`).

## FR-2 A landing on the issuer is a refusal -- `3bc241b`

- [x] T004 **The predicate** (`harness/browser.py`, module level): `issuer_base_of(authorize_url)`,
  `under_issuer(url, issuer_base)` (the base itself, or a path or query under it -- a path prefix, so `<web>/oidcish`
  is not under `<web>/oidc`), `signed_in_at(url, base_url, issuer_base)` = the old *under the web base and no `/login`*
  **and not under the issuer**, and `refused_at_issuer(url, issuer_base, picker_url)` = under the issuer and not the
  picker the click was made on. `page_one_line(page)`: the body's first non-empty line.
- [x] T005 **`Auth.sign_in`** takes `picker_url = page.url` once the picker is up (after the `stub_break` reload, where
  there is one) and `issuer = issuer_base_of(picker_url)`. Both waits (`expect="home"` and `expect="login"`) now end on
  *keel-web's page* or *a refusal at the issuer*; `_raise_if_refused_at_issuer` records `{refused_by_issuer, issuer,
  landed, line}` and a `sign-in-refused-by-the-issuer` screenshot, then raises `SignInRefused(line, url, founder.id)`
  -- an `AssertionError`, so the step records `ok: false` with the issuer's words and the scenario fails there. A
  refusal is raised at once, not waited out for 20 s.
- [x] T006 **`sign_in_with_code`** (and `sign_up`) delegate to `sign_in`, so they carry FR-2 with no code of their own;
  the test drives `sign_in_with_code` through the code door to prove it.
- [x] T007 **The unit test** `tests/test_sign_in_on_the_issuer_095.py` (14): the predicate on M6's 403 URL
  (`<web>/oidc/authorize?...&identity=founder-a`, from a remote `StackConfig`): under the web base, no `/login`, and
  **not** signed in; keel-web's pages still signed in; the picker itself not yet a refusal; the base read off the picker
  equal to `config.oidc_base_url` on the remote and the eval profile; then `Auth.sign_in`, `sign_in_with_code` and
  `sign_in(expect="login")` walked in Chromium against a staging-shaped stand-in (keel-web and the stub on one origin,
  the stub's own `picker_html`, M6's plain-text 403) -- each raises with the 403's line and the transcript's step is
  `ok: false`; the registered cell lands on `<web>/`. FR-1 read statically (S-003 one call with `fallback=founder_one`;
  S-010 two, `founder_one` and `founder_two`, two labels; `founder_name` distinct in the first word and neither inside
  the other). Checked against master's `browser.py` (helpers only, the old `sign_in`): the three Chromium refusal tests
  fail (the `expect="login"` one by its 20 s timeout).

## FR-3 Nothing else moves

- [x] The local profiles (the issuer is its own origin there, so `signed_in_at` reads exactly what it read), the stub
  (`stack/stub_oidc/*` untouched), the seven corpus journeys, every other scenario's code.

## Where the spec and the code differ (the code's patterns followed)

- **"under the issuer's base (`config.oidc_url`)"**: `Auth` is handed a page, a recorder and a web base -- never a
  `StackConfig` -- by eighteen call sites. Rather than thread a config through each (FR-3), the issuer's base is read
  off the URL the stub's picker is served at: keel-cloud sends the browser to the discovery's one
  `authorization_endpoint`, `{issuer}/authorize`, so the picker's URL less `/authorize` **is** `config.oidc_base_url`
  (`oidc_url` on remote, `<web>/oidc` by default; `localhost:<oidc_port>` on the local profiles, where `oidc_url` is
  empty). A test holds the equality for both profile kinds.
- **"raise with the page's one line, never record `ok: true`"**: the step's `ok` is the recorder's (`Recorder.step`
  records `ok: false` and the error on any exception), so raising inside the step is what records it; no `ok` field is
  written by hand.

## What the spec did not foresee

1. **A fresh founder means S-003 and S-010 go cold on the twin.** A registered cell owns no project, so both take the
   prelude (`approved_project_with_one_read`: a project approved through every stage, one invitation, one answer
   read) and connect a runtime as the new founder (`_connect_agent`, `start_runtime_via_skill`). The corpus journeys
   reset the runtime home on `remote` before starting the runtime (`corpus_scenario._connect`, `stack_runtime.reset`;
   S-013 likewise) because a home carrying the previous founder's credential reconnects as that founder's device
   (run 34662465285). **S-003 and S-010 do not**, and FR-3 kept them so; if the coordinator's remote acceptance runs
   after another scenario in the same session and the agent step does not connect for the new founder, that reset is
   the change to make (the same three lines). Not seen here: nothing was run against staging.
2. **S-010's names**: `register_cell_identity`'s default name is the same for every registration of a cell on a day,
   which S-010 cannot use (T003). The spec said "two distinct registered identities"; distinct ids alone would have
   failed step 3.
3. **The other callers now fail loudly** (the table above): on the twin each fails at its sign-in step with M6's line
   instead of a step later with a missing `.hello`. That is FR-2's intent; moving them is not this spec's.
4. **The old success wait could pass before the click on the twin**: the picker's own URL (`<web>/oidc/authorize?...`)
   satisfied *under the web base, no `/login`*, so on remote the wait could return while still on the picker, even for
   a sign-in that would have succeeded. The new wait excludes the issuer's pages, so it waits for keel-web.
5. **The acceptance** (`make eval K=s003 PROFILE=remote`, `K=s010 PROFILE=remote` against staging) is the
   coordinator's. Not run here.
