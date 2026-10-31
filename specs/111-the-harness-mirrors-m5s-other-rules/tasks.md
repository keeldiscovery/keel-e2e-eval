# Tasks 111 -- The harness mirrors keel-cloud 176: M5's parenthesis, list and design-note rules yield to the seed

Branch `111-the-harness-mirrors-m5s-other-rules` (worktree `wt/keel-e2e-eval-111`, its own `make venv`), off master
`6fd5c7f` (110's docs). Built by Claude on 2026-10-30. Read only: keel-cloud-docs at `2edd98bf` (176 merged; its
tasks.md's *The keel-e2e-eval pins that must move*, the checklist below; `RevealWords.java`, `PassageComposer.java`,
`FoundersOwnNamesTest` / `support/FoundersNames`). **No stack, no browser beyond the unit tests' local Chromium, no
model, no paid call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `b07aa0c` | FR-1 / FR-2 / FR-4: the M5 mirror, `plain_line`, `_row_fires`; 107's and 131's re-pins; `answer_refused_lock`'s note |
| `ff78383` | FR-3: `spoken.reveal_aloud`; the fake's SOLUTION mirror, IM4, the quality readers' reveal screen |
| `1373647` | FR-5: `tests/test_m5_other_rules_111.py` |
| the docs commit | this file and `AGENTS.md`'s spec-111 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `6fd5c7f` (110's tasks.md), keel-cloud-docs `2edd98bf` | 4,238 | 0 | 56 |
| branch at `ff78383`'s tree (the code, before the new tests), keel-cloud-docs `2edd98bf`, keel-web `1d83a28` | 4,237 | 1 | 56 |
| **branch at `1373647` (the last code; the docs commit adds none), the same siblings** | **4,255** | **1** | **56** |

+18 passed are `tests/test_m5_other_rules_111.py`'s; none removed. **The one failure is not this spec's**:
`tests/test_interviewer_screens.py::test_the_mic_and_beat_selectors_are_in_keel_web[ai-mic-on]` reads keel-web's
`*.tsx` for the literal `data-testid="ai-mic-on"`, and keel-web master's spec 143 (`31b7a13`, *the heard line never says
nothing yet after a sound*, merged during this build) now writes it as an expression in `MicWave.tsx`
(`data-testid={writing ? "ai-mic-writing" : (testId ?? "ai-mic-on")}`). keel-web 143's eval pin, named and left (another
builder owns keel-web; this spec touches no screen read). No new failure from keel-cloud.

## The checklist (keel-cloud 176's *eval pins that must move*)

- [x] T001 **The parenthesis** (FR-1, `instructions/corpus.py`): `names_of` mirrors `RevealWords.names` (commas, *or* /
  *and*, an Oxford comma), `typed_whole` mirrors `typedWhole` (every name `typed_in`, none is never the founder's),
  `founders_parenthesis` / `keels_parenthesis`: the rule reads **every** parenthesis of the line, skips one whose every
  name is typed, and the first one left is the line's one fault (176 T001 and its *did not foresee* 4).
- [x] T002 **The design note** (FR-1): `to_clause_end` mirrors `toClauseEnd` (`[,;:.!?()]`, else the line's end);
  `keels_note` skips a `DESIGN_NOTE` match whose phrase to its clause's end is `typed_in` -- Karsa's *no jargon*, never a
  lone *use* because a seed says *use*. `m5_faults` takes both; its docstring's *read the line alone (175 T003)* is gone.
- [x] T003 **`plain_line`** (FR-1): a parenthesis whose names are typed is not dropped, a bare list whose names are typed
  is not cut, a typed design note is not swapped for the first benefit (`keels_note` on the line as it stands).
- [x] T004 **`LOCK_PLAIN_WORDS`** (FR-1): the comment at the old `:1776-1779` (*the list of names ... stays M5's*) is
  rewritten; `_row_fires` also stands a row down when a list of names it carries is typed whole, so 16-pairio's three
  list rows fire only on a list Keel brought in; its *CMMS* / *ERP* rows stand.
- [x] T005 **107's re-pins, with why** (FR-2): `test_the_spoken_form_rules_still_read_the_line_alone` renamed
  `..._read_the_founders_texts_too`: with Codyco's texts the faults are **`["design note"]` only** (`need no change`;
  its clause *need no change to the front desk* is not in Codyco's seed -- so not *none*), and without the texts all
  three still fire. `test_lock_plain_words_rows_fire_only_on_keels_words`: 16-pairio's `fires` is `["CMMS", "ERP"]`.
  `test_plain_line_leaves_the_founders_words_and_moves_keels`: Codyco's typed parenthesis is now no edit (`None`); a
  parenthesis with Keel's *Mews* is still dropped.
- [x] T006 **`answer_refused_lock`** (FR-4, `evals/corpus_scenario.py`): the docstring says the edit never moves a
  typed name, list or note, and that fewer `lock_refused` findings on 21-codyco / 16-pairio are the spec working.
- [x] T007 **The spoken reveal** (FR-3): `instructions/spoken.py` `reveal_aloud` ports `RevealWords.aloud` line for line
  (`SPOKEN_NAMES_MAX = MAX_OPTIONS` = 5, `_spoken_list`); `corpus.NAME` / `LIST_OF_NAMES` port the cloud's `NAME` and
  `NAMES_IN_A_LIST` (`\p{L}\p{N}` as `[^\W_]`) for it. Used where the harness composes the reveal aloud:
  `harness/interviewer_fake.py` `reveal_said` (`PassageComposer.aloud`), `idea_passage` (`PassageComposer.idea`) and
  `solution_opening` (the problem sentence before *Now the idea.*, which `_framing_words` asserts the SOLUTION clip
  starts with); `evals/interviewer_marks.py` IM4 measures the claim and the benefit against the how / belief as said;
  `quality/readers.py`'s reveal / idea screen composes its *said* line through it (the card above it as typed).
- [x] T008 **Tests** (FR-5): `tests/test_m5_other_rules_111.py` (18): `names_of`, `to_clause_end`; Codyco's
  parenthesis as typed (no fault; the rule still fires without the texts), one Keel name (*Mews*: the fault, named
  whole), the rule reading past the founder's parenthesis; Pairio's list as typed (no edit, its list rows stand down),
  Keel's list (*SAP, Oracle or Fiix*: cut to one name) and the rows back on a Pairio seed without the names; the design
  note typed vs Keel's (Karsa word for word from `FoundersOwnNamesTest`, the lone *use*, Careforce, Codyco); FR-4's cards
  as typed drawing no fault and a *CMMS* refusal answered with the list kept; the spoken cap read off keel-cloud's
  source; *such as*, one name set off, a lower-case parenthesis as typed; *and others* past five, five whole; the
  SOLUTION mirror; IM4 on six names (the how as typed would have failed coverage); the readers' screen; the ported
  pieces held to `RevealWords.java` / `PassageComposer.java`.

## Where the spec and the code differ (the code's patterns followed)

- **`m5_faults` still carries no list rule.** FR-1 names the parenthesis and design-note rules; the mirror never carried
  132's list rule (176's *did not foresee* 6) and the edit (`plain_line`) is where the list is mirrored, so FR-5's
  *Pairio's list as typed (no fault)* is held as *no edit and no list row fires* -- what a back-test walk would do.
  Adding the rule to `m5_faults` would also move `test_after_131`'s golden guard, which the spec did not ask for.
- **`test_after_131.py` moved too**, not in 176's list (it said only `:87-96` need not move, which holds): five tests
  walked Codyco's typed parenthesis or Careforce's typed note as Keel's. Each is re-pinned with why and no assertion
  removed -- `test_codyco_the_pms_and_its_names_go_in_one_edit` walks a seed with the three names cut too (the one edit
  as before) and adds the PMS-only seed keeping the parenthesis; `test_a_design_note_belief_is_the_entrys_first_benefit`
  walks Careforce without *without an integration project* (its seed types it; 176's Karsa pattern) and asserts the
  typed note is no edit; the two stubbed Codyco walks read the card with the founder's texts, as the lock does;
  `test_a_second_refusal_of_the_same_line_stops_with_the_words_named` walks a Codyco seed without *PMS* (on its own seed
  nothing is Keel's and the walk stopped before any edit, a different stop).
- **The edit's list pattern is the eval's own** (`NAMES_IN_A_LIST`, simpler than the cloud's); `aloud` needs the cloud's
  `NAME` (its `matches(NAME)` and the list it cuts past five), ported beside it as `NAME` / `LIST_OF_NAMES`. The edit's
  list check is every name typed (the audience words are in `founder_texts`); the cloud's *counted* names (less the
  idea's own name) are not mirrored there, as they were not before.

## Not foreseen by the spec

1. **Careforce's seed types its design note** (*... the way the staff would, without an integration project: ...*), so
   under 176 its belief draws no M5 fault and a back-test walk meets no refusal for it: one more `lock_refused` finding
   gone (FR-4 names Codyco and Pairio only). Voltair (*recharge on cheap charging pads*), Issen (*adapts to the
   learner's level*) and Transload (*with no change to the dock workflow*) do not type their notes' phrases and are
   unmoved.
2. **The problem sentence is said through `aloud` too** (176 T007): the SOLUTION clip's opening is the problem sentence
   *aloud*, so `fake.solution_opening` and the interviewer leg's framing check (`_framing_words`) follow it.
3. **IM4 would have gone red on a list past five** (the clip leaves the rest unsaid): its claim and benefit are now read
   as said.
4. **keel-web moved during the build** (143, `31b7a13`): the one unit failure above, not this spec's.
5. **For the coordinator** (brings the stack up): a back-test walk of 21-codyco / 16-pairio / 18-careforce shows the
   fewer `lock_refused` findings; none was run here.
