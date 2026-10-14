# Plan 042

1. `instructions/corpus.py` at revision 11: `REVISION`, r10 refused by name, r11's K3 / S10 in the L half; the two unit
   fixtures at revision 11 (`check_corpus_r11.py` OK); the r10 test modules renamed and held to r11's facts.
2. The rubric: `spoken.py` (every stem 20, `KNOWN` empty), `validate.py` / `runner.py` (call 86's reclassification
   deleted, `vector_rule_letters`), `brief_facts.py` (`keelBar`, the B2C Ability line, `notAsked` words); `MARKS_VERSION`
   19 with calls 110-115, `marks.toml`'s header, `rescore.py` refusing below 19.
3. `harness/vectors_script.py`: one RESPONDENT_QUESTIONS job (part 1) under the plain name on part 1's key set; the
   aliases deleted; `frequency_fits` true on Paidly at r11; the idea's name -- `idea_name_of`, `idea_view`, `idea_card`,
   `benefit_question`, `IDEA_NAMES` and `FounderInputs.idea_name`.
4. `harness/vectors_screens.py`: S2 types the founder's name when there is one; step 5 returns the lock's receipt.
5. `evals/corpus_scenario.py`: S2 on `IdeaView`'s new shape and the rename step; `leg_lock` on one job (receipt and job
   list), the #81 re-read turned into a failing guard; `leg_calibrate`'s #80 step a failing guard; every interview held
   to the idea's current name; the brief's `keelBar` (cards), `notAsked` and quotes on the wire. S-006's rename and
   Frequency extras.
6. Unit tests; `make unit`.
7. The local stack against keel-cloud-docs `c432c1d` + keel-web `844ea36` (an archive export, since keel-web master moved):
   `make eval K="s005 or s006 or s007"` twice.
8. Docs: `runs/DRIFT.md` (#76, #77, #80, #81 resolved; #78, #79 still open), AGENTS.md, README.md, this folder.
