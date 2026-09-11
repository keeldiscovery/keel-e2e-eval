# Implementation Plan: the matrix workflow

**Branch**: `matrix-workflow` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md)

## 1. Where the code goes

| File | What it is |
|---|---|
| `matrix/cells.toml` | **New.** The three axes, the two scenario lists (`default`, `live`), and the three named sets cell by cell. The header carries the Python-axis reconciliation so a reader meets it before the data. |
| `matrix/cells.py` | **New.** `Cell`, `Matrix`, `load`, `coverage_problems`, `validate`, `render`, `main`. Stdlib only — `tomllib`, `argparse`, `json`, `itertools`, `dataclasses`. No `requests`, no `stack`, no `harness`: this module must run on a bare runner before anything is installed. |
| `matrix/__init__.py` | Re-exports the surface once, so a caller writes `from matrix import load`. |
| `matrix/__main__.py` | `python -m matrix`. |
| `.github/workflows/matrix.yml` | **New.** Four jobs: `select`, `deploy-staging`, `cell` (the matrix itself), `summary`. |
| `Makefile` | `matrix-check`, and `-k "$(K)"` quoted in `eval`, `eval-live` and `instruction-eval`. |
| `tests/test_matrix_cells.py` | **New**, 49 stackless tests. |
| `tests/test_scenario_set.py` | One line. It pins the Makefile's `-k` verbatim and therefore had to move with it — which is the pin working, not the pin being in the way. |
| `README.md` | the section *The matrix*, between the gated registry stub and the instruction eval. |

And one file in each of four sibling repositories, each on its own branch, each merged `--no-ff`:
`keel-cloud`, `keel-runtime`, `keel-web`, `keel-connect-skill` → `.github/workflows/dispatch-matrix.yml`.

## 2. The decisions worth writing down

**The cells are a TOML file and not a matrix expression in YAML.** A `strategy.matrix` written in
the workflow cannot be read by `make`, cannot be unit-tested, and cannot be validated before a
runner starts. Put in a file with one reader, the same six lines of Python enforce §5.2 on the
founder's Mac and on the runner, and the coverage rules become tests. The workflow's `select` job
is then three lines of shell and a `fromJSON`.

**`select` runs on every event, gated or not.** It costs one free Linux job and it is the only
place a bad `cells.toml` can be caught before a role is assumed. It also owns the one-line skip
summary, so "the matrix is off" is said once, in the job whose name is *select the cells*, rather
than by four jobs each skipping silently.

**The gate is a repository variable, not a branch or a comment.** `KEEL_STAGING_ENABLED != 'true'`
is checked in `select`'s output and every expensive job `needs` it. keel-cloud's own
`deploy-image.yml` already works this way (`vars.AWS_DEPLOY_ROLE_ARN != ''`), so this is the
repository family's existing idiom rather than a new one.

**Two Pythons per cell job, and the order matters.** `actions/setup-python` is run twice: 3.12
first, captured as `steps.harness-python.outputs.python-path`, then the cell's version — last wins
on `PATH`, so `python3` is the cell's, which is what the skill's script and the bundled runtime are
run by. The harness's venv is built from the captured path explicitly, never from `python3`, which
is also why `make venv`'s own `python3 -m venv` is never reached: `.venv/bin/python` already exists
by the time `make eval-live` asks for it.

**Windows has no `make`.** keel-runtime's `acceptance.yml` says so in a comment and this repository
now needs it to be true in code: the run step calls `make eval-live` when `make` is on `PATH` and
spells out the same pytest invocation when it is not. The Makefile stays the primary form — it is
what the founder types — and the fallback is one line beside it rather than a second source of
truth. (The Windows venv's interpreter lives at `.venv/Scripts/python.exe`; `$VENV_PY` is resolved
once, from `$RUNNER_OS`, and exported.)

**`-k` had to be quoted.** A cell that runs the corpus needs `-k "s005 or s006 or s007"`, and the
Makefile's `$(if $(K),-k $(K),)` splits that into four arguments. Quoting it is invisible to every
existing single-token call and is the smallest change that lets a cell carry more than one
scenario.

**The deploy job runs keel-cloud's own script, not a copy of it.** Eight steps, a rollback point,
an A5 guard on the web bundle, `write_deployed_tag` at the end — all of that belongs to
`deploy.sh` and reproducing any of it here would be a second deploy path to keep in step. The job's
whole contribution is: check out the right commit, hand the script an identity and two values it
cannot look up, and ask the twin afterwards whether it is up.

**`deploy.sh` wants a named AWS profile.** `common.sh` is `KEEL_PROFILE="${AWS_PROFILE:-keel}"` and
every call passes `--profile`, because it was written for a Mac; botocore drops the environment
credential provider the moment a profile is named. So the assumed session is written into a
`default` profile with `aws configure set` (which prints nothing) and `AWS_PROFILE=default` is
exported. The alternative — teaching `deploy.sh` to omit `--profile` — is a change to production's
deploy path for the benefit of staging's CI, which is exactly backwards.

**The keel-oidc tag is content-addressed.** `sha1(tree(stack/stub_oidc) + tree(stack/containers/oidc))`,
first twelve characters. It changes when the stub changes and not when a README does, which turns
§6.3's *"when the stub changed **or** the tag is absent"* into one question against ECR, and keeps
the immutable repository from ever being asked to overwrite a tag.

**The bundles are found by a diff, not a glob.** `runs/` is gitignored (only `DRIFT.md` is
tracked), so a fresh checkout starts empty and `path: runs/` would very nearly do. The collect step
diffs against a listing taken before the run anyway, because that is what makes the *row* right: a
cell that carries four scenarios writes four bundles, and the table names the ones this run wrote.
The new bundles are copied to `_cell/runs/` and each summary row is read from that bundle's own
`verdict.json` — the same file `make report` reads.

**UTF-8, named rather than assumed.** Both inline Python blocks open every file with
`encoding="utf-8"`. A failed step is called `§1.2 SOLUTION` and a row carries an em dash; Windows
defaults to cp1252, and a `UnicodeEncodeError` in the last step of a cell would take that cell's
whole bundle with it.

## 3. What was deliberately not touched

`evals/`, `harness/`, `stack/` — not a line. The remote profile (spec 017), the gated stub
(spec 018) and the journey through a host (spec 019) are what the cells use, and this feature's
whole job is to run them on eighteen machines rather than to change them. The only edit outside the
new files is the Makefile's `-k` quoting and the new `matrix-check` target.

## 4. Verification, and its ceiling

- `make unit`: **765 → 814**, green. The 49 new tests are stackless, offline and hold the **real**
  `cells.toml` to the design's coverage rules.
- `make matrix-check`, `make matrix-check SET=nightly`, `make matrix-check SET=weekly CELLS=…`: all
  three print what they should.
- `actionlint` 1.7.12 with `shellcheck` 0.11: clean on all five workflow files.
- The two inline Python blocks in `matrix.yml` were extracted, compiled, and **run against a
  fixture** — a fake `runs/` with one new bundle and one old one — so the collect step and the
  summary table are known to produce the rows and the Markdown they claim.

**The ceiling, stated plainly.** No job in these five files has ever run on GitHub. There is no
staging twin to deploy to, no `keel-ci-deploy` role to assume, no dispatch token to POST with. What
is proved is that the files parse, that the shell in them is clean, that the data behind them is
the design's, and that the two scripts inside them work. What is not proved is anything about AWS,
about a runner's toolchain, or about a cell — and §13 step 5 exists precisely to prove those one
cell at a time, with the founder watching.
