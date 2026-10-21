# Spec 060 -- The sample project: S-006's run exported as a snapshot for the landing page

Design of record: `keel-cloud-docs/canon/designs/landing-page-design.md` §18.8 (the example is a public project from an
eval run), §18.9 row 1 (the founder, 2026-10-21: *"we can label it honestly … Sample project"*), and §18.11 (the
snapshot, added 2026-10-21). **Scope: keel-e2e-eval only; nothing in the product changes.** Builds on S-006 (05-paidly,
the B2B entry with two roles and twenty answers; `evals/test_s006_paidly.py`, `evals/corpus_scenario.py`,
`evals/preludes.answer_everyone`). **Build lean: one `make unit`, one stack run of S-006 with the export on, the
snapshot committed into keel-web.**

## Why a snapshot and not a flag (acting decision, the founder's to overrule in one line)

§18.8 said *rendered live, read-only*. Live would mean a public read route on keel-cloud without a session, a `sample`
flag on `projects`, and a way to get the project into **prod's** database, where the eval's founders cannot sign in
(prod has no OIDC stub). A snapshot of what the founder API served for the finished S-006 project, committed into
keel-web as static JSON and rendered by the product's own components, gives the same page on staging and prod with no
public API, no flag and no copy of a database. A re-run refreshes it. The respondents are scripted either way (row 1).

## Rules

- **FR-1 The export.** A new harness step `export_sample(j, out_dir)` runs at the end of S-006 when
  `KEEL_SAMPLE_EXPORT=<dir>` is set (never otherwise; the eval cell stays as it is). It writes, as the founder session
  received them, one file per read: `overview.json`, `plan.json`, `standings.json`, `roles.json`, `people.json`,
  `readings.json`, and `readings/<batchId>.json` for every batch `readings.json` lists, plus `invitations.json` and
  `invitations/<id>.json`. Paths mirror `FounderReadController` and `VectorsController` under
  `/v2/projects/{id}/…` with the id removed, so keel-web's sample route (spec 090) can map
  `/v2/projects/sample/<path>` → `/sample/<path>.json` one to one.
- **FR-2 Names withheld.** Every person's name in every file is replaced by *Person 1* … *Person n* in a stable
  order (first appearance in `people.json`); emails are removed; the founder's own name and email are removed from
  every file; invitation tokens and links are replaced by `withheld`. A unit test over a fixture asserts no original
  name, email or token survives (grep of the whole output against the entry's people and founder).
- **FR-3 Verdict as the corpus expects.** The export refuses (exit 1, the reason named) unless the finished project's
  decision label is `BUILD_BUT_CHANGE`, every dimension has n ≥ 10, and the pilot count and the price line are present
  in `overview.json`, because the landing's card draws exactly those three (§18.8). The expected values are
  05-paidly's own (`expected.vector_verdicts`: PROBLEM holding up, SOLUTION holding up, COMMERCIAL not holding up).
- **FR-4 Where it lands.** `make sample` runs S-006 on the local stack with the export into
  `../keel-web/public/sample/` (the sibling checkout, as `stack.toml` finds keel-web), and writes
  `public/sample/manifest.json`: `{entry: "05-paidly", corpus: <revision>, exportedAt, cloud: <sha>, files: [...]}`.
  Committing the result is the operator's step, in keel-web, named in the hand-back.
- **FR-5 Nothing else moves.** S-006's marks, steps and the remote cell are unchanged when the variable is unset;
  `MARKS_VERSION` stays 20 (house rule: the harness's versions move only when a mark moves).

## Acceptance

1. `make unit`: the withholding test (FR-2) and a shape test that every file FR-1 names is written for a recorded
   fixture of S-006's reads.
2. One local stack run of `make sample`: `public/sample/` populated, `manifest.json` written, the verdict gate (FR-3)
   passed, S-006's own marks still green in the same run.
3. Hand-back names the snapshot's size, the decision label, pilot count and price line as exported, and the
   keel-web path to commit.
