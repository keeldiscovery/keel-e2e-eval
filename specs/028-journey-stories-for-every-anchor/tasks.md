# Tasks: a real story for every anchor the host wrote

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `028-journey-stories-for-every-anchor`

`make unit`: **green at every commit on this branch.** Baseline at `581dc0b`, before a line was
written: **1,283 passed** (Discovered **D-0**).

**Tests first, within each phase.** Each phase's own tests are written before the code that turns
them green and land in the same commit (spec 025 D11's rule, kept by 026 and 027 and kept here). **No
test is deleted**, and no assertion is removed — each one either stands where it stood or stands
somewhere else with the reason above it.

**Nothing below spends a model call.** The only paid thing this branch produces is the command in
*The next live run*, and it is the founder's to type.

## Phase 1 — read before writing anything

- [X] **T001** the red run: matrix run **36895521843**, bundle
      `20261001T165730Z-s012-journey-claude`, staging keel-cloud **f6aa07d** (048+049+050+051),
      keel-web **cdfa60f**. Transcript seqs **68–70**, **88–110**, **155–176**, **247**, **251**, and
      `scorecard.json`. What held (everything up to the deck) and what did not (`COMMERCIAL`: 0 of 5
      holding, `untested: 5`, `peopleAnswered: 5`).
- [X] **T002** keel-cloud `canon/designs/measured-beliefs/corpus/03-lullaby.yaml` — the revised
      entry: two anchors, two stories per person, every `anchoring`, Leo's blank `A1` with its tap,
      Keiko's `GUESSED` `A3`, and the twelve picks per person.
- [X] **T003** keel-cloud `canon/openapi-v2.yaml` — `BeliefStanding` (`guessed` is *"answers shown to
      the founder that count towards nothing"*), `StageCard.groups`, `Standing`'s four lists,
      `StageSummary.peopleAnswered`.
- [X] **T004** this repository's blast radius: `harness/corpus_script.py` (`PersonInputs`,
      `AnchorAnswer`, `written`, `person_inputs`, `people_to_invite`), `instructions/corpus.py`
      (`Person.anchors`, `anchoring`), `instructions/context.py` (`tap_enum`), `harness/browser.py`
      (`ParticipantPage.tell_story`/`options_for`/`pick`, `Overview.part_of`/`lines_of`/`tail_of`),
      `evals/test_s012_journey_through_a_host.py` (lines 627–647, 931–1010, 1026–1100, 2146–2203).

## Phase 2 — the matcher, the composer and the escape (FR-001 … FR-016)

- [X] **T010** `tests/test_stranger_stories.py` (new): the matcher's arithmetic, its global-best
      order, its floor, its determinism; the *when* and *thing* readers against every person in
      `03-lullaby`; the composer's lead verbs, value clauses, money rule and yes/no drop; the three
      paths; and the red run's own four host prompts end to end.
- [X] **T011** `harness/stranger_stories.py` (new): `content_words`, `occasion_score`,
      `match_occasions`, `scores_against`, `when_in`, `when_in_prose`, `thing_in`, `thing_in_prose`,
      `lead_for`, `value_clause`, `compose`, `AnchorPlan`, `corpus_prompts`, `plan`, `typed`.
- [X] **T012** the module's own tables, each read off the corpus or off keel-cloud and each with the
      source named beside it: `STOPWORDS`, `FLOOR`, `WHEN_PATTERNS`, `KEEP_CAPITAL`, `LEAD_VERBS`,
      `PRESENT_MARKERS`, `NO_ANCHOR_IN_A_VALUE`, `VALUE_CLAUSES`.

## Phase 3 — the stranger types it (FR-007, FR-010, FR-016, FR-017)

- [X] **T020** `tests/test_stranger_stories.py` gains the three source-level cases: the journey
      module names `THE_STRANGER_SAYS` exactly once, never calls `_story_texts` (retired into the
      module), and decides its picks before it tells its story.
- [X] **T021** `_answer_whatever_is_asked` rewritten: per anchor, read every selection's options and
      decide every tick first; `plan()` once per person with those decisions; then `tell_story` with
      the story **or the tap**; then the ticks. `§2.3` records the per-anchor path, the matcher's
      scores and each composed sentence's provenance.
- [X] **T022** `THE_STRANGER_SAYS` kept with its reason rewritten as *the filler that is never
      typed*; `_story_texts` deleted at its definition and its one reading replaced — the module's
      `plan()` is now this repository's single reading of *which words this stranger types*.

## Phase 4 — §1.7 accounts for the tested lines, and the new step names the party (FR-018 … FR-022)

- [X] **T030** `tests/test_journey_untested_stage.py` (new): `_panel_accounts_for_tested_lines` and
      `_stage_anchoring` as pure functions — the red run's own three stages' numbers, a closed panel
      with a tail, an all-untested stage passing the panel check and failing the new one, and the
      stranger-or-product verdict both ways.
- [X] **T031** the §1.7 panel assertion: the `counted["total"] and not (held or failed)` fault
      replaced by the accounting, tails counted at their own number, and the `reported` block gains
      `tested on the wire` and `rows the panel accounts for`.
- [X] **T032** the new step **§1.7a**, between §1.6's toast and `Overview.open`: no approved stage is
      entirely untested when everyone answered, and the message names the stranger or the product
      from `GET /stages/{stage}`'s own `guessed` and `inside`/`outside`.

## Phase 5 — the ledger and the dispatch

- [X] **T040** this file's **Discovered** section, and *The next live run*.
- [X] **T041** `make unit` green; the branch's own count recorded against **D-0**.

## Discovered

- **D-0 — the baseline.** `make unit` at `581dc0b`: **1,283 passed** in 157s. At the end of this
  branch: **1,318 passed** — thirty-five new tests, none deleted, no assertion removed.

- **D-01 — the filler was never the whole of the bug; the *order* was the other half.** The shortfall
  (four anchors, two stories) explains two filler sentences. It does not explain which two: the
  corpus's app-purchase story went under the host's *"opened an app during a night waking"* and the
  host's *"the last baby app you bought"* got the filler, so the one anchor whose occasion the
  corpus **does** carry was the one that got a guess. Even a corpus with a story per anchor would
  have been mis-filed by the old loop. The matcher is the fix for that half and it would have been
  needed anyway.

- **D-02 — the reading toast said it and nothing read the toast.** Seq 247 recorded *"Seven things
  moved on the problem card and four on your solution"* and asserted only that the string is
  non-empty (spec 016 FR-007: the journey asserts no prose). That is the right rule and it means the
  toast can never be the detector. The detector has to be the wire, which is why FR-020 is its own
  step and not a tightening of §1.6.

- **D-03 — `guessed` is the only field on the wire that can tell a lying referee from a broken
  product, and nothing in this repository had ever read it.** `BeliefStanding.guessed` /
  `inside` / `outside` travel on every belief of `GET /stages/{stage}`, which the journey already
  fetches once at line 829 for the questionnaire slices and never again. The new step fetches it a
  second time, after the readings, for the one question the deck cannot answer: *were the answers
  read as occasions at all?*

- **D-04 — a panel's two parts are `holdingUp` + (`notHoldingUp` + `peopleDisagree`), and the run
  proves it.** PROBLEM: `holdingUp 3`, `notHoldingUp 2`, `peopleDisagree 2` → 3 *Held* rows and
  **4** *Did not hold* rows. So *Did not hold* carries the split lines too, which is why FR-018's
  accounting is one sum against one sum and not two paired comparisons. SOLUTION's `untested: 1`
  appears in neither part and must not: a panel has two parts and no third.

- **D-05 — nine of Amira's fifteen picks were *the page's own first option*, and the reason is a
  word.** `_their_pick` matches a corpus value against an option case- and space-insensitively but
  **exactly**: the host offered *a monthly subscription* and the corpus says *monthly subscription*;
  the host offered *I did* and the corpus says *me*. Both are the same answer and neither matches.
  Out of scope here (spec *Out of scope*), recorded because it is the next simplest change to this
  scenario and because the composer makes it harmless rather than invisible: the story is now written
  from whatever `_their_pick` decided, so a fallback pick and the story still agree.

- **D-06 — `lines_of` drops the tail, and the red run happened to have no tails at all.** Every one
  of the three panels in seq 251 reported `"the tails behind them": [null, null]`, so an accounting
  that counted only visible rows would have passed this run and failed the next one with more than
  three lines in a closed part. The tail is parsed and added (plan Decision 8) on the strength of
  keel-web FR-015, not on the strength of this run.

- **D-07 — the escape path has no live coverage on Lullaby and that is correct.** Leo Martins is the
  only person in `03-lullaby` with a blank anchor and a tap, and he is twelfth: `people_to_invite(entry,
  5)` never reaches him. So FR-014 is held by unit test only, and the unit test uses the real corpus
  person rather than a fixture — which is the whole reason the module takes an `Entry` and a name
  instead of a hand-built object.

## The next live run

Nothing on this branch spends anything. These are the inputs for the founder's next live S-012 run,
against a staging twin carrying **keel-cloud f6aa07d or later** and **keel-web cdfa60f or later** —
the exact build run 36895521843 used, because this branch changes only the referee and the point is
to see the same product answer differently.

**By hand, from this checkout:**

```
make eval-live K=s012 HOST=claude LEGS=full ENTRY=03-lullaby PEOPLE=5 PROFILE=remote
```

**As a matrix dispatch** (`.github/workflows/matrix.yml`, the same shape run 36895521843 used):

| input | value |
|---|---|
| `set` | `nightly` |
| `cells` | `macos-latest-claude-py3.13` |
| `legs` | `full` |
| `entry` | `03-lullaby` |
| `people` | `5` |
| staging | keel-cloud **f6aa07d**, keel-web **cdfa60f** |

**What to read in the bundle, in this order**, because these are the steps this branch wrote:

1. ***§2.3: \<name\> sent their answers*** — now carries `what the stranger did with each anchor the
   host wrote`: one row per anchor with its **path** (*their own story* / *composed from their own
   facts* / *the escape, tapped*), the matcher's scores, and for a composed sentence the thing, the
   when and the picks it was written from. Five people, four anchors each, and **no row may read
   `path: the escape, tapped` for an `A1`/`A3` Lullaby person** — if one does, the matcher scored
   below its floor against a prompt nobody expected, and the scores in that row say against what.
2. ***§1.7a: every approved stage was tested by somebody*** — the new step. Green means every stage
   has at least one line the five answers moved. Red names the party: *the stranger's* means the
   composed sentences still read as guesses (`anchored 0`, `guessed > 0`) and the sentences are in
   step 1's rows to look at; *the product's* means answers were anchored and counted and the stage
   still has nothing, which is a keel-cloud finding and the first one this branch could produce.
3. ***§1.7: each panel's count line is the wire's own three numbers, and each panel accounts for every
   tested line*** — its `per stage` block now prints `tested on the wire` beside `rows the panel
   accounts for`. A fault here is keel-web's: a panel that drops a line or invents one.
4. *§1.6: the host read the answer, and the toast names what moved* — unchanged, and worth reading by
   eye: the toast should now name the commercial card as well as the problem and the solution. Nothing
   asserts those words (spec 016 FR-007) and nothing should.

**What a failure in each one means, so the founder need not guess:** 1 is this repository's matcher or
composer, and the row says which path it took and why; 2 is named in its own message and is the one
step on this branch that can blame keel-cloud; 3 is keel-web's panel against `GET /standing`; 4 is
never a failure, only evidence.
