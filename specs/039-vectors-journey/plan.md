# Plan 039

1. `harness/vectors_script.py`: entry (r9, through `instructions/corpus.py`) -> the script (seven screens, four
   RESPONDENT_QUESTIONS aliases), the derived context-keys table, the founder's inputs, each person's answers by dimension
   and code, the `InterviewIdCodec` mirror, the cost re-expression by `Period` days, `people_to_invite` for S-012.
2. `harness/vectors_screens.py`: page objects for the corridor, the People popups, the interview and the answer pages.
3. `evals/corpus_scenario.py`: one function per leg, `open_journey`, strict and live modes; S-005/6/7 with their vectors
   extras.
4. Wire first, then screens: the whole journey on the wire against the local stack until the standings matched r9 (finding
   D-1 to D-4 and DRIFT #74), then each leg moved onto keel-web's screens with the wire kept as the assertion.
5. S-012 leg two onto the same legs (`strict=False`); its dry tests and the keel-door tests rewritten; classic-only helpers
   and tests deleted.
6. Stack: keel-web's framework plugin in the eval vite config, `KEEL_VECTORS_ENABLED`; S-002's lazy fixture; S-004's own
   `STAGES`.
7. Gates: `make unit`; `make eval K="s005 or s006 or s007"` on keel-cloud-docs `b8a4eed` + keel-web `e54cb1c` (the
   worktree's `stack.toml` pointed there locally and not committed; `COMPOSE_PROJECT_NAME=keel-e2e-eval` so the worktree
   reuses the main checkout's Postgres container).
