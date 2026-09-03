# Implementation Plan: The Eval Set

**Branch**: `003-eval-set` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

**Input**: spec.md + ../eval-set-design.md (design of record) + keel-cloud
`canon/journeys.md` (the assertions' source of truth) + the shipped server (the
choreography's source of truth — S-001 already taught us the server, not the plan, is the
script).

## Summary

Recalibrate the policy (v2), then implement scenarios S-002–S-007 as modules on the existing
Scenario/driver/browser machinery, each with its own fact registry and journey-referenced
assertions, plus `make eval-all` producing a scored index of the night's runs. Run everything
against the live stack; product gaps found are fixed in the owning repo under the user's
standing authorization and the set rerun.

## Technical Context

Unchanged from features 001/002: Python 3.11 venv (pytest, playwright, requests), fixed ports,
stack via make. No new dependencies. Scenario modules only touch `evals/` + small harness
extensions where a scenario needs a capture the harness lacks (e.g. struck-through claim text,
"said, but didn't count" sections, decline button, out-of-date link page).

## Key implementation decisions

1. **Policy v2 mechanics**: CLA-A1/GUI-A2 restrict their protocol-text sweep to `display`;
   POLICY_VERSION=2; unit fixtures updated; S-001 bundle re-scored as the US1 proof;
   eval-scoring-design.md §3 gets a dated amendment paragraph; DRIFT #4 re-adjudicated in
   place (strike nothing — append the re-adjudication).
2. **Shared recipe, not shared state**: a `recipes.py` helper builds "three stages approved,
   pricing ruled out" for S-002/S-003 by running the real loop with scenario-specific
   participants — never by copying a database or reusing a project.
3. **Choreography from the server**: before writing S-002/S-003 assertions, read keel-cloud's
   `NextRecommendation`, `Project.frame` (carries/supersede), invitation/link services, and the
   participant controller for the invalid-link path — the journey names the experience, the
   server names the mechanism.
4. **S-005 all-skipped**: the scenario asserts the end-to-end experience and records the
   mechanism discovered (accepted-empty vs refused-gently) in the run transcript as a note —
   if the experience is not gentle, that is a DRIFT finding.
5. **S-007 scoring**: interactions carry only agent-surface attributes; scoring marks absent
   categories not-applicable (scoring.py extension per design §6.1).
6. **eval-all**: Make target iterating scenarios against one stack session, then writing
   `runs/INDEX-<stamp>.html` (slug, verdict, score, category bars, link to each report).

## Files

```text
evals/policy.py                    # v2
evals/recipes.py                   # NEW shared setup recipes
evals/test_s002_pricing_pivot.py   # NEW  (journeys §1.7–1.9, §2.4)
evals/test_s003_going_ahead.py     # NEW  (§1.10)
evals/test_s004_divided_person.py  # NEW  (§1.7)
evals/test_s005_opinions.py        # NEW  (§1.7, §2.2 skip-all)
evals/test_s006_consent_decline.py # NEW  (§2.1–2.3)
evals/test_s007_hostile_wire.py    # NEW  (protocol negatives)
harness/browser.py                 # captures: strikethrough, said-but-didn't-count, decline,
                                   #   invalid-link page, both-headings person
harness/scoring.py                 # not-applicable categories
harness/evidence.py                # INDEX generation
Makefile                           # eval-all
tests/                             # policy-v2 fixtures, N/A-category math, index rendering
../eval-scoring-design.md          # §3 amendment (policy v2)
runs/DRIFT.md                      # #4 re-adjudication
```

## Delivery

Sonnet subagent implements and runs the set live; judgement calls and discovered mechanisms
reported; product-gap fixes come back to the main session for design + delegation per repo;
verification and commits central.
