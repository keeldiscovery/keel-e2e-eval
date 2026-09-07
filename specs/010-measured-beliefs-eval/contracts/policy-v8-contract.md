# Contract: scoring policy version 8

`evals/policy.py`. `POLICY_VERSION` **7 → 8**, in the same commit as everything below. A run's
score is comparable only to another run's under the same policy; `make report RUN=…` re-scores an
old bundle under 8 without ever rewriting its `transcript.jsonl` or `screenshots/` (FR-031).

## Hops (FR-026)

```python
HOP_IDS = ["stage_screen", "review_card", "invite_screen", "participant_page",
           "overview", "opened_card", "answers_modal", "download"]
```
`brief` **retires** with keel-web's `BriefRoute.tsx`. `HOP_INTERACTION_TYPES` maps each to
`("ui_visit",)` except `participant_page`, which stays `("participant_visit", "ui_visit")` — the
stranger's own render and the founder's read-back are both legitimate places to judge an answer's
fidelity, exactly as in policy 7.

`WAIVERS` loses its one entry: `("assumption", "brief")` waived a Brief that no longer exists.
Nothing replaces it — a review card quotes the founder's own phrase verbatim, so there is nothing
to excuse.

## Clarity tokens (FR-027)

Added to `CLARITY_TOKENS`, all of them raw wire vocabulary a founder screen must never show:

| Family | Tokens |
|---|---|
| placements | `INSIDE` `BELOW` `ABOVE` `OUTSIDE` |
| anchorings | `ANCHORED` `GUESSED` |
| taps | `HASNT_HAPPENED` `CANT_RECALL` `RATHER_NOT_SAY` |
| measure kinds | `COUNT` `DURATION` `MONEY` `SHARE` `TIME_SINCE` `PHYSICAL` `RATE` |
| expectation types | `INTERVAL` `CHOICE` |
| marks | `DIRECT` `PROXY` |
| selection controls | `OPTIONS` `BUCKETS` |
| role types | `PRACTITIONER` `BUYER` `CONSUMER` `MANAGER` |

`GATEKEEPER` joins them for completeness of the `roleType` enum. Any token that turns out to
collide with the product's own correct ALL-CAPS copy is exempted **explicitly and by name** in
`_ENGLISH_COLLISION_EXEMPTIONS`, joining the five already there — never by softening the sweep.
`RATE` and `SHARE` are the two predicted; neither is exempted pre-emptively, and the first red run
decides with the excerpt quoted in the exemption's own comment.

## Retired strings (FR-028)

Added to `RETIRED_STRINGS`: `"counted for"`, `"counted against"`, `"said, but didn't count"` —
the evidence drill-down's own vocabulary, which went away with the claim/stance model. A literal
survival means a retired screen variant leaked back in, not a coincidence. None collides with
ordinary English in the way judgement calls 1 and 5 had to exempt for.

## Two new checks (FR-029)

| Check | Attribute | Weight | Question | Passes when | Skips when |
|---|---|---|---|---|---|
| **ORI-U4** | ORIENTATION | 1 | *Does a review card say, in the founder's own words, what the person will be asked first?* | the captured `review_card` text carries a *what they'll be asked first* block naming one story and then the picks | the interaction is not a review card |
| **GUI-U4** | GUIDANCE | 1 | *Does a status word carry a direction exactly when it should?* | a drifted `INTERVAL` belief's status carries a direction, **and** a `CHOICE` belief's status carries none (design §6.1) | no belief on the captured screen has a status word |

`GUI-U4` is deliberately two-sided. A keel-web that invents a direction for a Choice fails it just
as a keel-web that omits one for a drifted Interval does; the spec's own edge case says so.

## `absent_hops` honoured (FR-030)

`harness/rubric.py`'s `_fid_checks` gains a second loop. For each `hop` in `fact.absent_hops` it
emits `FID-<factId>-<hop>-absent`, attribute FIDELITY, at the same `fid_weight`:

- the hop was captured and the fact is **not** in it → **pass**;
- the hop was captured and the fact **is** in it → **fail**, quoting the excerpt;
- the hop was never captured → **fail**, with the same *hop was never captured* detail an absent
  positive hop already produces. Absence cannot be proved from a screen nobody looked at.

Matching uses `policy.fact_reaches_hop` unchanged, so *found* means the same thing in both
directions and normalization cannot make an absence check stricter than its positive twin.

## What does not change

`CATEGORY_WEIGHTS`, `DEFAULT_WEIGHT`, `FID_ANSWER_PARTICIPANT_PAGE_WEIGHT`,
`COMPLETION_GATE_SCORE`, `normalize`, `fact_reaches_hop`, `UUID_RE`, `GENDERED_PRONOUNS`, and
every check from ORI-U1 to GUI-U3. Policy 8 is additive plus two retirements (`brief`, its
waiver); it reweights nothing.
