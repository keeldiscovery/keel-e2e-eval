# Plan 052

Read first: the design (§3 the card lines, §4 the three views and the binding, §7 the themes job, §11 eval),
keel-cloud 104's spec (`StandingsView` 19, the themes fake, what it deleted), keel-web 077's tasks.md (selectors,
routes), spec 051 here (the ladder copy, the people's `follow_up` lines, the themes prediction's input),
`instructions/brief_facts.py`, `instructions/brief.py` (to delete), `evals/corpus_scenario.py` (`leg_brief`,
`_brief_pages`, `_board`, `_board_tiles`), `harness/vectors_screens.py` `Answers`, `instructions/marks.py`.

| Piece | Place | Modelled on |
|---|---|---|
| delete the reading marks | `instructions/brief.py`, `instructions/marks.py`, `evals/corpus_scenario.py`, `instructions/rescore.py`, `tests/test_instruction_brief_reading.py` | spec 034's retirement of `brief_paragraphs` (marks history 102) |
| `priceMedian`, the two card-line moves | `instructions/brief_facts.py` | `brief_facts.card`, `pilot` |
| themes fake | `harness/interviewer_fake.py` `themes` | `LADDER` (051) |
| `Answers.board` (rewritten), `.insights`, `.pilot`, `.brief(printed=True)` (rewritten); `.breakdown` deleted | `harness/vectors_screens.py` | today's `board` / `brief` |
| `report_overview`, `report_insights`, `report_no_repeat`, `report_pilot`, `report_binding` | `instructions/marks.py` (rows + history), `evals/corpus_scenario.py` (`_report` leg replacing `leg_brief`) | `brief_facts` (deterministic, `DRY=1`) |
| S-014 green | `evals/test_s014_green.py`, `evals/preludes.py` | `test_s005_countly.py` |
| the too-few state | `evals/corpus_scenario.py` `_board_tiles` | 044's *None yet* read |
| the stage page's follow-up line | `harness/vectors_screens.py` `vector_page` | the `dimpeople` list |

Order: 1 delete + `brief_facts` additions + unit tests; 2 the readers against 077 on the stack; 3 the five marks
with seeded faults; 4 S-014 and the too-few state; 5 S-005/6/7 re-pointed; 6 `make unit`, `make eval`, tasks.md,
MARKS_VERSION 20's paragraph; remote journeys when staging has 104 + 077.

Notes: every expected word comes from the wire or the registry export, never typed into the eval; the two empty
states and the eight rung headings are copied once into `interviewer_fake.py` beside the ladder, held to 077's
strings by a source check as 050 did for the framing lines. `report_no_repeat` is a regex over text, cheap and
blunt on purpose: a false positive is a DRIFT to read, not a tolerance to widen.
