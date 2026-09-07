# Contract: the vendored wire facts

Every field in another repository that this feature's assertions depend on, **copied here with the
commit it was read at**, so a scenario that goes red can be told apart from a sibling that moved.
A fact in this file is not an assumption: it was read out of the named file at the named commit.

Re-vendoring is a task, not a habit — `tasks.md`'s Polish phase carries one per row. A row whose
sibling has moved is a `runs/DRIFT.md` entry, not an edit that quietly follows.

---

## Part A — keel-cloud `028-measured-beliefs-aggregate` @ `03ebe60` (2026-09-07)

### V0 — the context keys, as its own exporter writes them

`./gradlew -q screenContracts --args="export <dir>"` → `context-keys.json`. Thirteen key sets:
ten screens and three corrections. Reproduced in full in `research.md` R1. The three facts that
matter to this repo and to keel-runtime:

- **`market` is on every framing, assumptions and reframe screen.** It is `null` when the project
  has no market, and **present-and-null, never omitted** — which is what makes an exact key-set
  match the right rule.
- **`founder_name` is a fourth key on all three `*_ASSUMPTIONS` screens**, always last, the first
  word of the founder's name, `null` when absent. *Not in this spec's RT-001 table.*
- **`BRIEF` is `{project_name, market, claims}`.** `deal_breakers` no longer exists as a context
  key. *This spec's RT-001 still names it; the export wins.*

### V1 — the correction turn on an assumptions draft

```
POST /v2/inference-interactions/{id}/corrections            -> 201
  request   InferenceInteractionDtos.CorrectionRequest { message: string }
  response  InteractionView (the same shape the other interaction endpoints return)
  domain    InferenceOrchestrator.correct(...) ; InferenceInteraction.correctionQueued(...)
            AWAITING_CONFIRMATION -> PENDING
  contract  ScreenResponseContracts.correctionContract(screen)
            = the assumptions schema + reply (required, <= 1200 chars)
                                     + changes[] {heading, before, after} (required, <= 8)
            allowed_outcomes: ["COMPLETED"]
```

*Used by*: FR-008's one correction turn, FR-020's box **B6**, S-004's attack **A8**.
*Where*: `src/main/java/com/keeldiscovery/cloud/protocol/connect/InferenceInteractionController.java`.

### V2 — `Belief.selectionId`

`FounderDtos.Belief.selectionId : String`, and `FounderDtos.FormSelection.selectionId`. Domain:
`Assumption.selectionId()`. *Used by*: the review card's chips, the opened card's *Asked: "…"*
line, and *Same pick list as line N* — which is how FR-013's `expected.buckets` is read off a
screen at all, and how acceptance scenario 3a's shared `S4` is proved to be **one** selection.

### V3 — per-person observations on testimony

```
FounderDtos.TestimonyRow(personName, quote, counted, whyNot, placement, anchoring,
                         ObservationRow observation, readAs)
FounderDtos.ObservationRow(type, low, high, highExclusive, unit, per, picks[])
```

*Used by*: every dot on every strip, the `SaidBox`'s *Read as …*, and FR-012's per-belief
`inside`/`outside`/`guessed` counts read off the screen rather than only the wire.

### V4 — the assumptions result's `role`, and the missing `askedOf`

The exported `*_ASSUMPTIONS` schema requires `heading, statement, risk, mark, expectation,
selection, role`. **There is no `askedOf` field.** `role` is `{new: {label, roleType, about,
market?}}` or `{reuse: <label>}`; `roleType ∈ {CONSUMER, PRACTITIONER, MANAGER, BUYER,
GATEKEEPER}`. `founderPhrase` is optional and always emitted by the generator.
`assumptions` and `questionnaire.anchors` are each **`maxItems: 8`**.

*Used by*: `harness/corpus_script.py` (FR-002), which resolves the corpus's `askedOf` **role id**
through `Entry.role(id)` to a label. This is the single most likely place for a generator to be
quietly wrong, which is why it is written down.

### V5 — `Overview.whatThisSays`

`FounderDtos.Overview(..., MarketRow market, String whatThisSays, String whatThisSaysNote)`;
stored as `Project.whatThisSays`. *Used by*: FR-008 and acceptance scenario 5, and the print
page's overview sheet.

### V6 — `StageCard.whatItMeasures` and `rationaleLines`

```
FounderDtos.StageCard(revision, type, framed, approved, claim, previousClaim,
                      rationale, rationaleLines[], whatItMeasures,
                      QuestionnaireRow questionnaire, Group[] groups)
```
`rationaleLines` are the `not represented as a belief:` lines with the prefix stripped
(`FounderVoice.rationaleLines`); storage is `Stage.normalizationRationale`.
*Used by*: the opened card's *What it measures*, and the review card's *Not asked, on purpose*.

### V7 — `CreateProjectRequest.market`

```
FounderDtos.CreateProjectRequest(String name, MarketRequest market)
FounderDtos.MarketRequest(String country, String region)      // NO language
```
The language is derived server-side (`Market.languageFor`), and the emitted `Market` is
`{country, region, language}`. *Used by*: `MarketStep`, and every one of `07-mulchrun`'s
US-market assertions. **The request carries no `language`, so no scenario types one.**

### V8 — the two result contracts

- `INTERPRET`: `allowed_outcomes: ["COMPLETED"]` (no `NEEDS_INPUT` at all);
  `result` requires `invitationId` and `anchorings[] {anchorId, anchoring ∈ {ANCHORED, GUESSED}}`,
  `maxItems: 8`; optional `unprompted[]`, `flags[]`.
- `*_ASSUMPTIONS`: `allowed_outcomes: ["NEEDS_INPUT", "COMPLETED"]`; `result` requires
  `assumptions`, `questionnaire {introduction, anchors}`, `normalization_rationale`;
  `NEEDS_INPUT` carries `questions[]`, `maxItems: 3`, **and is legitimate only when the statement
  is missing** (decision 14).
- The `INTERPRET` context is `{invitation_id, anchors[]}` where an anchor is
  `{anchor_id, prompt, text, tap}` — **snake_case `anchor_id` on the way in, camelCase `anchorId`
  on the way out.** Blank answers are not written at all.

---

## Part B — keel-web `013-measured-beliefs-screens` @ `c887aac` (2026-09-07)

### W0 — the routes

```
/                       landing; the name step and the market step are inline frames of it
/p/:projectId           overview (or the walk's chat frame, mid-walk)
/p/:projectId/s/:stage  review card while unframed; opened card once framed
/p/:projectId/people    people/invite   (/invite and /invitations resolve here too)
/p/:projectId/print     the download page — OUTSIDE the project shell, no side nav
/i/:token               the participant page — uncredentialed, credentials: "omit"
/login /setup /connect
```
There is **no `/p/:id/brief`** and no `BriefRoute.tsx`. The `brief` hop retires with it.

### W1 — the one `data-testid` in the repository

`line[data-testid="median-tick"]` in `src/components/strip/Strip.tsx`. Everything else is a role,
an `aria-label`, a heading or a class. The full handle inventory is the plan's page-object table.

### W2 — the nine open wire gaps

Each marked `// wire gap N` in keel-web's own source; each is this feature's DRIFT material, and
**none of them is a reason to soften an assertion**:

| # | keel-cloud field it wants | keel-web stub | Blocks |
|---|---|---|---|
| 1 | `Questionnaire.introduction` | a hand-composed stand-in sentence | FR-008's participant introduction |
| 3 | `Belief.selectionId` (V2) | `selectionFor()` returns `undefined` | **FR-013 entirely**, and 3a's shared selection |
| 4 | `TestimonyRow.observation` (V3) | `marks = []` | every dot, and FR-012's screen-side counts |
| 5a | `Overview.whatThisSays` (V5) | `undefined` | FR-008, acceptance 5 |
| 5b | `StageCard.whatItMeasures` (V6) | `undefined` | acceptance 6 |
| 6 | `CreateProjectRequest.market` (V7) | sends `{name}` only | **all of S-007**, and every market assertion |
| 8 | `StageCard.rationaleLines` (V6) | `[]` | the review card's *Not asked, on purpose* |
| 9 | the correction endpoint (V1) | `postCorrectionTurn()` throws | **FR-008's correction turn**, box B6, attack A8 |
| 10 | a person's `kind` beyond the role label | bare role label | the popover's kind line |

keel-web's types are generated from a vendored `openapi-v2.yaml` taken at keel-cloud `1a24a6a`,
which predates the founder wire. Every gap above closes on **one** keel-web act: re-vendor and
regenerate. That is keel-web's to do, and this repo's to report.

---

## Part C — keel-runtime `timeout-configurable` @ `89b1396`

- `keel_runtime/config.py` already resolves **`KEEL_SCRIPT`** (`ENV_SCRIPT`), flag > env >
  `$KEEL_HOME/config.json`. **RT-005 is already met**; the task is to verify, not to write.
- `keel_runtime/testing/scripted_executor.py`'s `_FIXED_KEY_SCREENS` misses every row (no
  `market`, no `founder_name`), `_resolve_interpret_result` still resolves `perAnswer[].assumptionId`
  through a context `assumptions[]` that no longer exists, and the bundled
  `scripts/payroll-exceptions.json` is written entirely in `claimType`/`stance`/`perAnswer`/
  `evidence`. RT-001 to RT-004 and RT-006 are real work, in that repo.
- `tests/fixtures/response_contracts.json` in keel-runtime is a **hand-copied** snapshot of the
  ten contracts and is stale in the same way. It should be regenerated from the exporter in the
  same pass, or the tests will keep asserting the retired shapes.
