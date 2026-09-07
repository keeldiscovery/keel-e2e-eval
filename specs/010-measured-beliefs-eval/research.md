# Phase 0 — Research: the eval set, rewritten for measured beliefs

Everything below was resolved by reading a sibling at a named commit, not by choosing. Where a
choice was made it says *Decision / Rationale / Alternatives*, in the house shape.

---

## R1 — What are keel-cloud's context keys, actually?

**Read**: keel-cloud `03ebe60`, `src/main/java/com/keeldiscovery/cloud/application/ScreenContextBuilder.java`,
via its own exporter (`./gradlew -q screenContracts --args="export <dir>"`) rather than by eye.

```
PROBLEM_FRAME            project_name, market
PROBLEM_ASSUMPTIONS      problem_statement, existing_roles, market, founder_name
SOLUTION_FRAME           project_name, problem_statement, existing_roles, market
SOLUTION_ASSUMPTIONS     solution_statement, problem_statement, existing_roles, market, founder_name
COMMERCIAL_FRAME         project_name, problem_statement, solution_statement, existing_roles, market
COMMERCIAL_ASSUMPTIONS   commercial_statement, problem_statement, solution_statement, existing_roles, market, founder_name
SOLUTION_REFRAME         current_statement, problem_statement, assumptions, contradicted_evidence, market
COMMERCIAL_REFRAME       current_statement, problem_statement, solution_statement, assumptions, contradicted_evidence, market
INTERPRET                invitation_id, anchors
BRIEF                    project_name, market, claims
PROBLEM_ASSUMPTIONS.correction     … + current_draft, founder_message
SOLUTION_ASSUMPTIONS.correction    … + current_draft, founder_message
COMMERCIAL_ASSUMPTIONS.correction  … + current_draft, founder_message
```

**Two things the spec's RT-001 could not have known**, because both landed in keel-cloud spec 030
after this spec was written:

1. **`founder_name`** is a fourth key on all three assumption screens (last, always written, `null`
   when absent). RT-001's table as written in the spec omits it and would therefore *still* miss.
2. **`BRIEF` is `{project_name, market, claims}`** — `deal_breakers` is gone. RT-001's
   `"deal_breakers present → BRIEF"` rule is stale in the spec text itself.
3. **Three `<SCREEN>.correction` key sets exist**, and the smoke walks a correction turn (FR-008).
   A scripted executor that cannot infer them cannot answer the correction job at all.

**Decision**: RT-001 is implemented from the **export**, not from the spec's prose table, and the
divergence is written into `contracts/vendored-wire-facts.md` and into keel-runtime's own
addendum. The spec's table is a snapshot; the export is the contract. This is precisely why the
spec said the table *SHOULD* be derived from the export rather than copied.

**Alternatives**: implementing the spec's literal table was rejected — it reproduces the same
staleness this whole RT section exists to end, one commit later.

---

## R2 — Is `deal_breakers` really gone, and does anything else in this repo depend on it?

Yes and no. `BRIEF`'s context is `{project_name, market, claims}`, where each claim carries
`{stage, statement, approved, verdict, drift, beliefs[]}` and each belief carries
`{heading, statement, risk, mark, founder_phrase, verdict, drift, median_reads, inside, outside,
below, above, guessed, escaped}`. Nothing in `evals/` reads `deal_breakers` from a context; the
*word* "deal-breaker" is founder copy on the screens (`span.db`, `span.must`, `p.rule-line`) and
that is what the scenarios assert. No change beyond the runtime's inference table.

---

## R3 — Did keel-cloud's spec 030 founder wire land, or is it still in flight?

**All eight items exist in `src/` at `03ebe60`.** They were expected to arrive during this
planning and did. Each is vendored with its exact name and shape in
`contracts/vendored-wire-facts.md` §V1–§V8: the correction endpoint
`POST /v2/inference-interactions/{id}/corrections`, `FounderDtos.Belief.selectionId`,
`FounderDtos.TestimonyRow.observation` (an `ObservationRow`), `Overview.whatThisSays`,
`StageCard.whatItMeasures`, `CreateProjectRequest.market` (a `MarketRequest{country, region}` —
**no `language`**, which the server derives), `StageCard.rationaleLines`, and the `founder_name`
context key.

**Consequence for this plan**: the per-gap tasks are *not* "wait for keel-cloud". They are
"the fact is vendored here with its commit; the assertion is written against it; the task closes
when the **screen** renders it" — because the gaps moved downstream (R4).

---

## R4 — Where are the gaps now?

**keel-web** `013-measured-beliefs-screens` at `c887aac`. Its types are generated from a
**vendored** `specs/013-measured-beliefs-screens/contracts/openapi-v2.yaml` taken at keel-cloud
`1a24a6a` — three commits before the founder wire landed. So nine features are built and stubbed
in place, each marked `// wire gap N` in the source:

| Gap | Stub | What a run sees today |
|---|---|---|
| 1 | `ParticipantRoute.tsx` composes a stand-in introduction | the intro is keel-web's sentence, not `Questionnaire.introduction` |
| 3 | `StageRoute.tsx` `selectionFor()` returns `undefined` | **no chips on any review card**, no *Asked: "…"* line |
| 4 | `StageRoute.tsx` `marks = []` | **no dots on any strip** — band only |
| 5a | `OverviewRoute.tsx` `whatThisSays = undefined` | the heading renders, the paragraph never does |
| 5b | `StageRoute.tsx` `whatItMeasures = undefined` | the *What it measures* block is empty |
| 6 | `CreateProjectStep.tsx` sends `{name}` only | **the market is collected and never persisted** |
| 8 | `StageRoute.tsx` `rationaleLines = []` | *Not asked, on purpose* never renders |
| 9 | `api/interactions.ts` `postCorrectionTurn()` throws | **the correction turn errors every time** |
| 10 | person `kind` is the bare role label | the popover's kind line is thin |

**Decision**: one task per gap, in the Polish phase's *vendored facts* section, each naming the
keel-cloud field, this repo's assertion, and the DRIFT number it produces. None of the nine
softens an assertion. Gaps 6 and 9 are load-bearing for S-001 and S-005–S-007 (a market that is
never persisted makes `07-mulchrun`'s whole US-market scenario unmeasurable, and a correction turn
that throws stops FR-008's walk), so those two are the first DRIFT entries and are called out in
the quickstart as *expect red here*.

**Alternatives**: pinning this repo to a keel-web that has re-vendored was rejected on
`AGENTS.md`'s own rule — *this repo deliberately floats at sibling HEADs*.

---

## R5 — How does a scenario get its script to the runtime?

Settled in the spec (`KEEL_SCRIPT`). Confirmed on the ground: `harness/connect.py` already merges
an `env_extra` dict into the child's environment (spec 008 FR-001), keel-connect-skill's script
launches `keel connect` with the environment it inherits, and **keel-runtime already resolves
`KEEL_SCRIPT`** — `keel_runtime/config.py`'s `ENV_SCRIPT`, flag > env > `config.json`, and its
README already documents it. RT-005 is therefore *already met* at keel-runtime `89b1396`; the
runtime work is RT-001 to RT-004 and RT-006. Recorded so the task is a verification, not a rewrite.

---

## R6 — One reader for the corpus, or two?

**Decision**: one — `instructions/corpus.py`, imported by `harness/corpus_script.py`.

**Rationale**: it already opens the files read-only, hashes each on the way in, offers
`verify_unchanged()`, and knows the three places the corpus and the wire disagree (the tap table,
`founderPhrase`, an anchor's `stage`). A second reader would be a second hash and a second chance
to be wrong about which of those three applies.

**Alternatives**: a `harness/corpus.py` of its own was rejected; SC-008 requires this feature to
write nothing in `instructions/`, and importing is not writing.

---

## R7 — keel-web's DOM: what is actually stable?

`data-testid` appears **once** in the whole of keel-web `src/` — `median-tick`, on the strip's
median line. Everything else, including keel-web's own Playwright suite, is driven by
`getByRole` / `aria-label` / `getByText` / stable classes (`.card`, `.strip`, `.opt`, `.page`,
`.ppl`).

Two traps found and handled in the page objects rather than in the scenarios:

- **The region input's `aria-label` is its placeholder, and the placeholder depends on the
  country** (`regionPlaceholder(...)` — "State or region, if it matters — California, Texas…" for
  US). `MarketStep` finds it **positionally**, as the text input following the country select.
  `07-mulchrun` is the only entry that types into it and it is a US market, which is exactly the
  case a label-matched locator would have found and then silently mismatched for GB.
- **A strip line's caret is a `<span>`, not a button.** The click target is the whole
  `div.strip`, and its handler ignores clicks that land on `svg`, `.said` or a `button`. D5's
  opener judge exercises the row, not the caret glyph, and records that.

**Decision**: no request to keel-web for testids. It is not this repo's to change (`AGENTS.md`),
and asking for one would make the referee's convenience a product requirement.

---

## R8 — What does the wire's assumptions result actually require?

From the export's `PROBLEM_ASSUMPTIONS.json` (identical in shape for the other two):

- `result` requires `assumptions`, `questionnaire`, `normalization_rationale`.
- each assumption requires `heading, statement, risk, mark, expectation, selection, role` — and
  **`role` is `{new: {label, roleType, about, market?}}` or `{reuse: <label>}`**. There is no
  `askedOf` on the wire; the corpus's `askedOf` is a role **id**, and the generator resolves it
  through `Entry.role(id)` to a label. `founderPhrase` is optional on the schema and always
  emitted by the generator, since scoring it is half of why spec 029 put it there.
- `questionnaire` requires `introduction` and `anchors`; each anchor requires `id, prompt,
  selections` and may carry `taps`; each selection requires `id, prompt, control, escape` and may
  carry `options`, `multiSelect`, `other`.
- **`assumptions` and `anchors` are both `maxItems: 8`.** `01-countly`'s PROBLEM stage is exactly
  8 beliefs and 1 anchor — at the cap, not over it. A unit test asserts the cap per stage per
  chosen entry, so an entry that grew would fail in `make unit` rather than mid-run.
- `NEEDS_INPUT` is legal on the assumption screens (`questions`, `maxItems: 3`) and **illegal on
  `INTERPRET`**, whose `allowed_outcomes` is `["COMPLETED"]` alone.

The `INTERPRET` result requires `invitationId` and `anchorings` (each `{anchorId, anchoring}`,
`anchoring ∈ {ANCHORED, GUESSED}`, `maxItems: 8`), with optional `unprompted` and `flags`.

---

## R9 — The print page prints itself

`PrintRoute.tsx` calls `window.print()` on mount once data loads. keel-web's own e2e suite stubs
it. **Decision**: `PrintPage.open()` installs `page.add_init_script("window.print = () => {}")`
before navigating. It is a harness mechanic and is recorded in the bundle as one, not asserted:
FR-019 and the spec's *Out of scope* both say the PDF itself is not this feature's business.

The *fresh page per stage* assertion (FR-008, SC-003) is read off the **stylesheet's own rule** —
the computed `break-before`/`page-break-before` of each `div.page` — never off a pixel offset.

---

## R10 — Reconciling drift vocabulary, and the missing median

Two small deterministic rules, both in the generator's module so no scenario carries a convention:

- `drift_equal("both", "BOTH") → True`. The corpus writes lowercase; the wire's enum is upper.
- **Where `expected.standings[b]` gives no `median`, the screen must show none.** `NEVER` is
  positive infinity, so a set containing one can have no median at all, and an invented midpoint is
  a red run. The assertion is the *absence* of `line[data-testid="median-tick"]` — the one place in
  this whole plan where the single testid keel-web has is exactly the right handle.

---

## R11 — Nine boxes, and where the missing three are

keel-web spec 013's own screens carry **six** free-text inputs: the project name, the region, the
correction composer, the participant's story box, *say roughly*, and *other, say what*. Spec 013
decision 6 is explicit that the founder never types into a band or an option list, so there are no
"claim boxes" on the review or opened cards.

The spec's nine is still right. The three claim boxes are the **walk's chat composer** (`GuidedStep`,
frames C1–C8), which spec 013 leaves untouched and which is where the founder types the problem,
the solution and the commercial claim. It is one input element used at three moments, and S-004
attacks it at all three — a different screen state each time, which is what FR-020 means by
"box". Written into the plan's box table so the count is auditable rather than folklore.

---

## R12 — Does anything need a Makefile change?

Barely. `make eval K=s005` already works: `K` becomes pytest's `-k`, so any new
`evals/test_s005_*.py` is dispatched with no Makefile edit at all. What FR-016 actually needs is
that the three are collected by `make eval`/`make eval-all` (they are, by living in `evals/`) and
that none is marked `live` (they are not). **Decision**: FR-016 closes with a test, not an edit —
`tests/` asserts the seven scenario modules exist, that exactly one carries the `live` marker, and
that `harness/eval_all.py`'s invocation still deselects it.
