# Quickstart: running the measured-beliefs eval set

Validation guide, not implementation. Shapes are in `data-model.md`, exact lists in `contracts/`.

## Prerequisites

Four checkouts, siblings, as `stack.toml` names them, at or after:

| Repo | Branch | Needed for |
|---|---|---|
| keel-cloud | `028-measured-beliefs-aggregate` (`03ebe60`+) | the aggregate, the founder wire, the frozen corpus |
| keel-web | `013-measured-beliefs-screens` (`c887aac`+) | the screens; **nine wire gaps are still open — see below** |
| keel-runtime | `scripted-executor-measured` | RT-001–RT-006; **nothing here runs without it** |
| keel-connect-skill | any | how the runtime is started, always |

Plus Docker, a JDK (keel-cloud's exporter is a Gradle task), and — for S-004 only — a logged-in
`claude`.

```sh
make venv          # once
make up            # the eval profile: 55432 / 18080 / 5173, runtime not yet running
```

## The five-minute check, before anything long

The generator needs no stack and no browser. Run it first; a run that fails here fails in eight
minutes instead of eighty:

```sh
make unit                                   # includes the generator's four refusals and policy 8
python -m harness.corpus_script 01-countly  # prints the script it would write, to stdout
```

Read the printed `PROBLEM_ASSUMPTIONS` entry against
`keel-cloud/canon/designs/measured-beliefs/corpus/01-countly.yaml`. Eight beliefs, one anchor,
seven selections, every `expectation` verbatim, every `askedOf` resolved to a role label under
`role.new` or `role.reuse`. If that reads true, the rest is plumbing.

## One scenario at a time

```sh
make eval K=s001    # the smoke: the whole journey, one correction turn, no LLM
make eval K=s005    # 01-countly  — the mockup entry; every number on the overview is Countly's
make eval K=s006    # 05-paidly   — the widest questionnaire; S6 sits exactly on FLOOR = 5
make eval K=s007    # 07-mulchrun — the only US market; dollars, miles, American English
make eval K=s003    # every door, now with the market screen, the popover, the modal, the print page
make eval-all       # all of the above in one stack session, plus runs/INDEX-<stamp>.html
```

`K` is pytest's own `-k`, so no Makefile change was needed to dispatch the three new ones.

The live one is separate, opt-in, and costs real money on the founder's own account:

```sh
make up   PROFILE=playground
make eval K=s005 PROFILE=playground      # S-004 attacks a project S-005 built
make eval-live K=s004 PROFILE=playground
make down PROFILE=playground
```

Two referee sessions never share a profile (`AGENTS.md`). If the eval profile is busy, use
playground for the whole sequence, not for part of it.

## Reading a bundle

```
runs/<id>/
  script.json      the runtime script this run generated from the corpus  (new)
  inputs.json      what the founder and each person typed                 (new)
  transcript.jsonl every interaction, every captured hop
  versions.json    the four siblings' commits, so a red run names what moved
  scorecard.json   every check, weighted, by category
  verdict.json     the run's own answer
  screenshots/
  report.html      self-contained; open it and read left to right
```

`make report RUN=runs/<id>` re-scores an old bundle under policy 8 without rewriting a single
captured byte.

## Expect red, on purpose

This set asserts the design, not the build (spec judgement call 7). On a first run against the
siblings above, these are **findings, not bugs in the harness**, and each is owed a `runs/DRIFT.md`
entry from #30:

**Updated 2026-09-07, after the first runs.** Every one of keel-web's nine wire gaps closed while
this was being built (it re-vendored keel-cloud's wire and regenerated its types), and so did
keel-cloud's stage drift. The table below is what it turned into: one row survived, none in the
shape it was predicted, and one genuinely new finding took their place.

| Expected red | What actually happened | Owner |
|---|---|---|
| the market is not persisted | **closed** — keel-web sends `{name, market}`, and `GET /v2/markets/{country}` gives the step its own sentence | — |
| the correction turn errors | **closed** — `useCorrectionTurn` asks, the card answers in place and stays unapproved | — |
| no chips on any review card | **closed** — `Belief.selectionId` renders, and `expected.buckets` is read off the screen | — |
| no dots on any strip | **closed** — every anchored person is a circle with their own `aria-label` | — |
| *What this says* / *What it measures* blank | **closed** — both render | — |
| stage drift missing its direction | **closed** — `Project.driftOfStage` and `StageSummary.drift` shipped; the assertion judgement call 7 wrote expecting red is green | — |
| the context table missed on `market` | **only if keel-runtime is not on `scripted-executor-measured`** — still true, still the only diagnosis needed | keel-runtime |
| **a blank respondent counts nowhere** | **new, and blocking**: the corpus counts a person who wrote no words as hollow; the product reads them not at all. `runs/DRIFT.md` #30 — S-006 and S-007 are red on it, by design | keel-cloud |

The last one is different in kind from the others: it fails at the *first inference job*, before
any assertion runs, with `ExecutorUnavailable` naming the keys. If a run dies there, the runtime
is on the wrong branch — no other diagnosis is needed.

## The one thing that must never go green quietly

Every corpus scenario calls `Corpus.verify_unchanged()` at the end (FR-005). If a corpus file
moved while the run was in flight, the run **fails**, with `instructions/corpus.py`'s own message,
and it has measured nothing. The corpus is the reviewer, not the subject.
