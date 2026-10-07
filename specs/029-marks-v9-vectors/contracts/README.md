# contracts/ — what this feature reads and what it asks of its siblings

Copies, not symlinks, taken on 2026-10-07 from
`keel-cloud-docs/canon/drafts/vector-redesign-2026-10-06/` (keel-cloud at `3e91cfc`, this branch at
`a673a67`). A copy here is **design-time reference for the plan, the tasks and the fixtures**; at run
time the eval reads keel-cloud's export and nothing in this directory.

| File | Source (sha256) | What it is here |
|---|---|---|
| `marks-v9.toml` | `marks-v9.draft.toml` (`b7002e36…0b209`) | **Verbatim.** Becomes `instructions/marks.toml` in Phase 2 of tasks.md, byte for byte (FR-002). Its header already says there is no `ANCHOR_READ` constant; `INTERPRET` is the name (A-1). |
| `marks-v9.md` | `marks-v9.draft.md` (`b8d62303…f7464b`) | **Verbatim.** The rubric: §2 the marks, §3 judgement calls 28–36 (the exact words `marks.py` appends), §4 the r3 schema, §5 the Lullaby excerpt, §6 the file-by-file changes, §7 the WHY events, §8 the closed decisions. |
| `dimension-registry.yaml` | `dimension-registry.v1.draft.yaml` (`66ceafb7…93368`) | **Verbatim.** The golden for `option_validity`; the shape every registry fixture under `tests/` copies a slice of. In production the eval reads the JSON keel-cloud 058 exports as `dimension-registry.json`. |
| `screen-shapes.md` | written here from `instruction-table.v1.draft.md` §B/§C (`e77a2b19…3778`), `openapi-v2-vectors.draft.yaml` (`40ca1001…850c3`), `phase0-reconciliation.md` §B (`35b6226d…74fbfb`) | The eight case kinds: context keys, response shapes the validator sees, rule ids per template, the batch shape, the compare engine's two files, the `-k` grammar. |
| `models-screen.json` | this feature | The `MODELS=<file>` pin a screen uses until keel-cloud's export carries the three new classes (FR-023, A-9): the ceiling, nothing else. |

Not copied, read: `phase0-reconciliation.md` §B (all 24 decisions; 5, 8, 9, 14, 15, 16, 17 bite
here), `HANDOFF.md` §4 (the Waits), `registry-schema.draft.md` (`4e3bf248…e19da`; the seven
invariants, restated in data-model.md §1), the frozen corpus `README.md` and `03-lullaby.yaml`
(`bc08e80d…9093e`, revision 2, read only).
