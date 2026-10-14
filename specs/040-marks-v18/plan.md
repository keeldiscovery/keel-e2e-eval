# Plan 040

1. `instructions/registry.py` at registry 4 (invariants 0-8 of 087, the lists' `saves`, one escape, fixed answers;
   `RecallWindow` from two units), `tests/fixtures/registry/slice.yaml` regenerated from the 087 export, the broken
   fixtures re-cut (`2-escape`, `2-escape-against`, `5-saves`, `8-options` new; `2-deal-breakers`, `8-can-fail` gone).
2. `instructions/corpus.py` at revision 10 (r9 refused by name; S / W / L / R / A shape half), the two fixture entries
   rebuilt at r10 and pinned to the engine (`screenContracts compare`) and to `check_corpus_r10.py`; the compare
   fixtures regenerated.
3. The eighth screen: `contract.MODEL_SCREENS`, `instruction.STEMS` (`founder-lists`, `asked`), `models` (`asked`),
   `validate` (the ASKED case, the `L` reclassification), `runner` (ASKED redrawn), `context.build_asked`,
   `prompts.build_cases` (ASKED cases, BRIEF facts).
4. Contexts at contract 13 (`context.py`: `answers`, `saves`, `escape`, no `founder_options`, no `weight`; the BRIEF
   context from facts); `score.py` rewritten for the lists, the gate's clause and the faces.
5. The deterministic marks: `cloud_corpus.py` (keel-cloud's two corpus tests, read back), `spoken.py` (`S1`-`S10`,
   `K2`-`K6`, the known ledger), `brief_facts.py` (the eval's reading and the compare); `run.py` measures them on dry
   and real runs, `rescore.py` reads them from the bundle.
6. `brief.py` at contract 13 (seven marks), `marks.py` / `marks.toml` v18 (calls 77-90), `rescore.py` OLDEST 18,
   `report.py` ten rows.
7. The harness: `vectors_script.context_keys_for` reads eight screens, the one-unit branches deleted, S-005's step
   inverted; the journey's corpus-reading unit tests skip by name (call 89).
8. Tests rewritten per module (three forks of the work, one file set each), `make unit`; `DRY=1` against `7b151f9`.
9. Docs: AGENTS.md, README.md, the Makefile's run list, `runs/DRIFT.md` (#74 closed, #76, #77).
