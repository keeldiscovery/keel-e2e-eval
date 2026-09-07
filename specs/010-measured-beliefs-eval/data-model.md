# Phase 1 — Data model: the eval set, rewritten for measured beliefs

Five things this feature owns the shape of. Nothing here is a wire type; the wire's own shapes are
vendored in `contracts/vendored-wire-facts.md` and read from keel-cloud's exporter at run time.

---

## 1. `GeneratedScript` — the runtime script, keyed by screen

Produced by `harness/corpus_script.generate(entry)`, written to `runs/<id>/script.json`, handed to
keel-runtime as `KEEL_SCRIPT`. Its file format is `contracts/generated-script-contract.md`; its
in-memory shape:

```python
@dataclass(frozen=True)
class GeneratedScript:
    entry_id: str                    # "01-countly" — the only thing that differs per scenario
    entry_sha256: str                # from instructions.corpus, so the bundle names what it ran
    screens: dict[str, list[dict]]   # screen -> entries, consumed in order, last repeats
```

`screens` carries exactly the keys the run will ask for, and no others:

| Screen key | Entries | Built from |
|---|---|---|
| `PROBLEM_FRAME` | 1 `COMPLETED` `{statement}` | `entry.statements["problem"]` |
| `SOLUTION_FRAME` | 1 | `entry.statements["solution"]` |
| `COMMERCIAL_FRAME` | 1 | `entry.statements["commercial"]` |
| `PROBLEM_ASSUMPTIONS` | 1 `COMPLETED` | `entry.beliefs_for("PROBLEM")` + `entry.anchors_for("PROBLEM")` |
| `SOLUTION_ASSUMPTIONS` | 1 | the same for `SOLUTION` |
| `COMMERCIAL_ASSUMPTIONS` | 1 | the same for `COMMERCIAL` |
| `<STAGE>_ASSUMPTIONS.correction` | 0 or 1 | only for the one stage a scenario corrects (S-001 only) |
| `INTERPRET` | one per person, **in `entry.answers` order** | that person's own anchorings |

Screens the entry cannot produce are **absent, not empty**: a `ScriptedExecutor` that has no entry
for a screen refuses by name, which is a better failure than answering the wrong shape.

### An `*_ASSUMPTIONS` entry

Per `contracts/assumptions-result-contract.md` and the exported schema (R8):

```json
{"outcome": "COMPLETED",
 "result": {
   "assumptions": [
     {"heading": "…", "statement": "…", "founderPhrase": "…",
      "risk": "LOAD_BEARING|SUPPORTING", "mark": "DIRECT|PROXY",
      "expectation": { … verbatim from the belief … },
      "selection": "S3",
      "role": {"new": {"label": "…", "roleType": "…", "about": "…"}}   // or {"reuse": "…"}
     }],
   "questionnaire": {"introduction": "…", "anchors": [ … this stage's anchors, verbatim … ]},
   "normalization_rationale": "…"
 }}
```

- `askedOf` → `role`. The corpus's `askedOf` is a **role id**; `Entry.role(id)` gives the label.
  The first belief in the whole entry that names a role emits `role.new` with that role's
  `label`, `roleType` and `about`; every later belief naming the same role emits `role.reuse`.
- `expectation` is copied **verbatim**, both branches (`INTERVAL` with `measure/lower/upper`,
  `CHOICE` with `options/expected`). Nothing is recomputed; the corpus is the golden truth.
- `group` does not go on the wire. Two beliefs sharing a `selection` (countly `P4a`/`P4b`, both
  `S4`, both `group: G1`) simply both name `S4`, which is how rule `Q4` is exercised at all.
- `introduction` and `normalization_rationale` are the entry's own where it has them and a
  fixed, entry-named sentence where it does not, so the field is never absent (both are `required`).

### An `INTERPRET` entry

```json
{"outcome": "COMPLETED",
 "result": {"anchorings": [{"anchorId": "A1", "anchoring": "ANCHORED"}],
            "unprompted": [], "flags": []}}
```

`invitationId` is **not written by the generator** — keel-runtime fills it from the job's own
context (RT-002), because only the running stack knows the real invitation id.
**A blank anchor is omitted**: `Person.written()` skips it, `ScreenContextBuilder.anchorsWritten`
skips it, and the script must skip it too, or the executor refuses an `anchorId` the context does
not carry.

---

## 2. `FounderInputs` — what the founder types

```python
@dataclass(frozen=True)
class Market:
    country: str            # ISO alpha-2, e.g. "GB", "US"
    region: str | None      # "TX", or None — left empty on the screen, never "null"
    language: str           # "en-GB" / "en-US" — asserted, never typed (the server derives it)

@dataclass(frozen=True)
class Correction:
    stage: str              # "PROBLEM" | "SOLUTION" | "COMMERCIAL"
    belief_id: str          # the one line the correction names
    message: str            # what the founder types into the chat
    expected_change: str    # what must differ afterwards, in the founder's own words

@dataclass(frozen=True)
class FounderInputs:
    project_name: str       # entry.title
    market: Market
    problem: str
    solution: str
    commercial: str
    correction: Correction | None   # S-001 only; the corpus entries do not correct
```

---

## 3. `PersonInputs` — what one stranger types

```python
@dataclass(frozen=True)
class AnchorAnswer:
    anchor_id: str
    text: str | None        # None where the corpus left it blank
    tap: str | None         # the ENUM name, via instructions.context.tap_enum

@dataclass(frozen=True)
class Pick:
    selection_id: str
    values: list[str]       # one for a single-select or bucket; many for a multi-select
    is_escape: bool         # the value came from the selection's `escape` list, not `options`

@dataclass(frozen=True)
class PersonInputs:
    person: str             # the corpus's own person name
    role_id: str            # which role's anchors they are asked
    anchors: list[AnchorAnswer]
    picks: list[Pick]
```

A person is only ever offered the anchors their role is asked. Being offered another role's anchor
is a **refusal**, not a shrug (spec edge case) — the scenario fails, naming person, role and anchor.

---

## 4. The hop map — what a screen contributes to scoring

Policy 8's `HOP_IDS`, with the page object that captures each and the interaction type it arrives
on. This table is the whole of what `harness/rubric.py` needs to know about the new screens.

| Hop | Captured by | Interaction type | Notes |
|---|---|---|---|
| `stage_screen` | `Landing`, `MarketStep` | `ui_visit` | keeps its old name; it is the founder's own naming/market surface |
| `review_card` | `ReviewCard`, `CorrectionChat` | `ui_visit` | the unapproved draft, before and after the correction |
| `invite_screen` | `People` | `ui_visit` | unchanged |
| `participant_page` | `ParticipantPage`, and `People`'s answers popup | `participant_visit`, `ui_visit` | reachable from either party, as in policy 7 |
| `overview` | `Overview` | `ui_visit` | |
| `opened_card` | `OpenedCard`, `SaidBox` | `ui_visit` | |
| `answers_modal` | `AnswersModal` | `ui_visit` | the founder's read-back of a person's whole page |
| `download` | `PrintPage` | `ui_visit` | |
| ~~`brief`~~ | — | — | **retired** with `BriefRoute.tsx` |

---

## 5. The fact registry, derived

`evals/corpus_facts.facts_for(entry)` returns `dict[str, Fact]` using the existing
`evals/facts.Fact` unchanged — `text`, `kind`, `hops`, `absent_hops`. Fact ids are stable and
readable so a scorecard names something a person recognises:

```
name                                   -> the entry's title
statement.PROBLEM|SOLUTION|COMMERCIAL   -> that stage's statement
phrase.<beliefId>                       -> that belief's founderPhrase
band.<beliefId>                         -> an INTERVAL's band as the founder's chip reads it
expected.<beliefId>                     -> a CHOICE's expectation.expected
role.<roleId>                           -> that role's label
anchor.<anchorId>                       -> that anchor's prompt
said.<person>.<anchorId>                -> that person's own words
```

`phrase.*`, `band.*` and `expected.*` each carry `absent_hops=["participant_page"]`. That is
design rule `Q5` and the mockup's *"the people you ask never see them"*, and it is the first time
`Fact.absent_hops` — which has existed unused since spec 005 — is scored.

**`absent_hops` semantics** (new in `harness/rubric.py`, FR-030): for each declared absent hop,
the check `FID-<factId>-<hop>-absent` passes when the hop was captured and the fact is **not**
found in it, and fails when it is found. A hop that was never captured at all is the same failure
`hops` already produces — a fact cannot be proved absent from a screen nobody looked at.
