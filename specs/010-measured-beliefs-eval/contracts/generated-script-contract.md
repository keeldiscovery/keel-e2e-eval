# Contract: the generated script and the typed inputs

What `harness/corpus_script.py` writes into a run bundle. Two files, both evidence, neither
committed (spec judgement call 1). A reader with the bundle and the corpus can check every value
in either against the entry by eye.

## `runs/<id>/script.json`

A JSON object. The `_`-prefixed keys are metadata — keel-runtime's `ScriptedExecutor` skips them
by rule, so they are safe to carry and they are the whole provenance of the run.

```json
{
  "_source": "keel-cloud canon/designs/measured-beliefs/corpus/01-countly.yaml",
  "_entry_id": "01-countly",
  "_entry_sha256": "<the hash instructions/corpus.py took on the way in>",
  "_generated_by": "harness/corpus_script.py",
  "_generated_at": "2026-09-07T00:00:00Z",

  "PROBLEM_FRAME":  [ {"outcome": "COMPLETED", "result": {"statement": "…"}} ],
  "PROBLEM_ASSUMPTIONS": [ {"outcome": "COMPLETED", "result": { … }} ],
  "…": [],
  "INTERPRET": [ {"outcome": "COMPLETED", "result": { … }} ]
}
```

Rules the file obeys, each one a unit test in `tests/test_corpus_script.py`:

1. **Every value came from the entry.** No literal in the file that the entry does not carry,
   except: the six screen keys, the outcome words, the `_` metadata, and the two required strings
   named in rule 5. (Acceptance scenario 7 is this rule, asserted before a stack is ever booted.)
2. **`INTERPRET` has one entry per person, in `entry.answers` order.** The scripted executor
   consumes them in order, one per process, so the run must read people in that order too.
3. **A blank anchor is absent** from that person's `anchorings`, because it is absent from the
   context, and an `anchorId` the context does not carry is an `ExecutorUnavailable`.
4. **`invitationId` is not written.** The runtime fills it from the job's own context (RT-002).
5. **`questionnaire.introduction` and `normalization_rationale` are always present**, both being
   `required` on the wire. Where the entry gives neither, the generator writes a fixed sentence
   naming the entry — never an empty string, which the schema's `minLength` would refuse.
6. **A screen the entry cannot produce is absent**, not present-and-empty.
7. **`<STAGE>_ASSUMPTIONS.correction` appears only for a scenario that corrects** (S-001), and
   carries the assumptions envelope plus `reply` and `changes[] {heading, before, after}`.
8. **Every `anchorings[]` entry carries `stage` beside `anchorId`**, keyed by the pair and never
   the bare id (keel-cloud measured-beliefs decision 18, `Q7`, DRIFT #37): an anchor id is unique
   only within one stage's own questionnaire and free to repeat on another's, because a link can
   carry occasions from more than one approved stage and every one of them calls its first
   occasion `A1`. The frozen corpus numbers its ids across the whole entry and so never collides
   (rule unchanged for it), but the generator does not assume a future entry, or a live model,
   will do the same — `by_selection` and `role_of_anchor` are scoped to `(stage, id)` for the same
   reason.

## `runs/<id>/inputs.json`

```json
{
  "_entry_id": "01-countly",
  "founder": {
    "project_name": "Countly",
    "market": {"country": "GB", "region": null, "language": "en-GB"},
    "problem": "…", "solution": "…", "commercial": "…",
    "correction": null
  },
  "people": [
    {"person": "…", "role_id": "manager",
     "anchors": [{"anchor_id": "A1", "text": "…", "tap": null}],
     "picks": [{"selection_id": "S4", "values": ["recounted by hand", "adjusted a spreadsheet"],
                "is_escape": false}]}
  ]
}
```

`language` is recorded and **never typed** — `CreateProjectRequest.market` carries only
`{country, region}` and the server derives the rest (vendored fact V7). A scenario asserts the
language on the screen; it does not enter it.

## The four refusals (FR-004)

Each raises `CorpusScriptError` naming the **entry id and the field**, and none is ever softened
to a warning:

| Refusal | Trigger |
|---|---|
| `no selection` | a belief whose `selection` matches no selection on any anchor of its own stage |
| `unknown pick` | a person's pick that is in neither the selection's `options` nor its `escape` |
| `unknown tap` | a tap outside `instructions/context.py`'s `TAP_ENUM` |
| `no anchoring` | a person who wrote text under an anchor the corpus records no `anchoring` for |

## The drift fold

`drift_equal(corpus_value, wire_value)` — the corpus writes `none|below|above|both`, the wire
writes `NONE|BELOW|ABOVE|BOTH`. One function, in this module, so no scenario carries the
convention. `drift_equal(None, "NONE")` is **False**: an absent drift and a `NONE` drift are
different claims, and only the corpus decides which one it made.
