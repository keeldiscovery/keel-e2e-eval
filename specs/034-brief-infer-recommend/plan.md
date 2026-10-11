# Plan — 034

1. `instructions/brief_facts.py`: `facts`, `beliefs`, `stories` from a corpus entry (decision label by the
   §4.2 rule; no `sharpest`, no `priceTable`: the corpus records neither).
2. `context.py`: BRIEF default keys and `build_brief`.
3. `validate.py`: BRIEF batch case carries `facts` and `stories`.
4. `brief.py`: `reading_problems` (the restatement) and five marks; `run.py` diff/json carry the reading.
5. `marks.py` / `marks.toml` / `rescore.py`: version 14, calls 71–73, refusal of v13 bundles.
6. Fixtures `tests/fixtures/brief/{build,not-yet,build-but-change-b2b}.json`; tests: marks, parity with the
   real validator, context, rescore, version.
7. AGENTS.md, README.md, Makefile at v14. DRY=1 against keel-cloud 079 (the checkout at `706015c`).
