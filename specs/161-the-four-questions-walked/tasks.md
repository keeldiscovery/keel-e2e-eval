# Tasks -- spec 161

Base: `origin/master` `e097af0` (161 amended; 160 merged). Built 2026-11-24 from 11:06 ET by a builder (Claude Opus 5.5)
in the worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-161`, branch `161-the-four-questions-walked`,
beside keel-web 257's builder (`wt/keel-web-257`, nothing committed past `f7d00534` while this was built). The stack
served the sibling main checkouts `stack.toml` resolves: keel-cloud-docs master `bf5a5b7d` (268-270 merged, contract 87)
and keel-web master `f7d00534` (neither 257 nor 258 merged: its one 258 commit is the follow-up route's `recency`
alone). Nothing paid: no model, no key, no pip install (the main checkout's `.venv`), no network but `git fetch` /
`git push` of this branch; the local stack only. Nothing merged or deployed.

- [x] T1 FR-1, FR-2, FR-3 the founder's mirrors: `story_screens.py` (seven beats, the long beats closed by *that's it*, the two-part beat 3, the scripts, seven scenes),
  `three_views.py`'s founder legs (the board's rows, the verdict, the corridor past the belief pages),
  `vectors_screens.py` (`calibrates(spoken)`, `REVIEWED_LISTS`), their unit mirrors.
- [x] T2 FR-4 (the gate's words, the screener before the film, the screener's No), FR-5, FR-6, FR-10 the stranger's mirrors: `interviewer_screens.py`, `interviewer_leg.py`,
  `classifier_guard.py`, `classifier_cases.py`, `vectors_script.py` (Frequency on bins and codes, the corpus
  revision), `working_rung.py`, the corpus fixtures.
- [x] T3 FR-7, FR-8 the follow-up roster per study, the Insights reads, the Overview reads (Frequency, no Current
  solution, the ways), the brief and export reads (`report_marks.py`, `facts.py`).
- [x] T4 FR-9 the three-surfaces record and check (`three_views_strangers.py`, `calls_leg.py`, `evals/copilot`).
- [x] T5 FR-11, FR-12 the report sections, DRIFT entries, `tests/test_four_questions_161.py`; `make unit`; the local
  run; this file's sections.

## Versions
- Contract read: **87** -- `info.x-keel-contract` of the stack's `canon/openapi-v2.yaml` (sha256
  `d3e7424c1c37f8d0d848f565a4c8a57311b8c2ffc6a7d3a4e968b202faac9e25`, keel-cloud 270's T0), read by the run
  (`Run.contract_read`, a check in FR-1a, the report's head) and pinned by
  `tests/test_four_questions_161.py::test_contract_87_is_the_one_the_walk_reads`.
- `InferenceCharge.VERSION` read: 21 (`EXPERIENCE_WAYS` added, `STORY_TURN` still 0; `interview_charge.PRICE_VERSION_270`).
- Registry read: 5 (keel-cloud 269: twelve keys, 3 / 3 / 6, Frequency `fixed_five` / `share_most_or_every`;
  `instructions/registry.is_269` reads 4 and 5).
- Corpus revision: the files stay keel-cloud's -- 23 (golden), 25 (gallery) -> **read through keel-cloud 269**,
  `instructions/corpus.READ_REVISION_161 = "r23+269"` (judgement call 6).

## How each FR is met

| FR | Where | What the walk holds |
|---|---|---|
| FR-1 | `harness/story_screens.py`: `said_turns` (seven beats, 6 only where owed; any other order refused by name), `STORY_QUESTIONS` (268's seven; 263's kept as `STORY_QUESTIONS_263`), `COST_BEAT` / `ALL_OF_THEM_BEAT` / `WHEN_BEAT` / `OTHER_TASKS_BEAT`, `moment_beat` (2 else 6), `steps_read` / `act_read` / `cost_read` / `other_tasks_read` / `tasks_correction`, `heard_cost` kept; `LONG_BEATS` (3, 4, 7), `DONE_WORDS` / `DONE_WORD`, `with_done_word` / `ends_on_a_done_word` / `without_done_word`, `THINK_LINE`, `TWO_PART_QUIET_S`; `long_beat_3` (the way's *Today they* sentence, five limitations, the cost's *In the end* sentence), `limits_only_beat_3` + `way_answer` (code's one `WAY_ASK`), `two_part_beat_3`; `StoryWalk.beat` (long beats said with the done word; `two_parts`; the ask answered), `StoryWalk.tell`; `CARD_ROWS` / `BOARD_ROWS` with `tasks`, `board_rows_verdict`; `StoryWire` (the seven beats on the wire); `evals/three_views.py`: `tell_the_story` -> `tell_on_screen` (keel-web 257) or `tell_on_the_wire` (before it), `story_wire_checks`, `board_checks`, `keep_founder`; `FR1A_TOLD` / `FR1B_TELLING` / `FR1C_TELLING` | four tellings over the founder's legs: the script's words with the tasks row corrected on the board (FR-1a), the long telling with the condition narrowed (FR-1a), beat 3 in two parts across 7 s of quiet (FR-1b's problem), the limitations alone and the way after code's ask (FR-1c's problem); each beat read as 268 reads it (the way and the limitations apart, the cost heard early and beat 4 still asked, beat 6 only where owed, beat 7's tasks), the words sent with no done word; on keel-web 257's screens also the seven questions, no button, the orb's states, the long beats closed by *That's it.* (never the quiet), the two-part quiet (*Take your time.*, nothing sent, the beat open), the board's seven rows lit, the tasks row redrawn |
| FR-2 | `story_screens.VERDICT_CARD` / `VERDICT_ASK` / `VERDICT_LATER` / `VERDICT_LINE`, `StoryWalk.story_yes(verdict=True)` / `hear_verdict`; `three_views.verdict_wire_checks`, `window_then_ready` (was `window_then_prevalence`), `wait_review`, `READY_PATH` / `BELIEF_PATH`; `fr1_d` (no `leg_calibrate` on the problem); `vectors_screens.calibrates(spoken=)`, `written_beliefs`, `calibration_answered`, `REVIEWED_LISTS` (Current solution out, `REVIEWED_LISTS_RETIRED`; `SCOPE_STEPS` unchanged) | the served `verdictLine` word for word (on 257's screens the `story-verdict` card and *Say yes, or ...*, the silence going on); the review table's three rows as written at the yes (`p_60_80`, `p_60_80`, Importance the own row then the tasks), complete; the window, then the ready page, no belief page; FR-1d's plan complete with no belief page walked |
| FR-3 | `story_screens.scenes_verdict` (seven, the seventh alone `pain`, a picture, `costLine` its line, eight clips), `film_holds` / `held_longer` (the watched rows' `story-line` on the page's clock), `ORB_INTERVIEW_WATCH`'s `line`; `three_views.scenes_checks`; `three_views_strangers.wire_checks` (the link's film), `pain_hold_check` | the founder's build and every link's served story on seven scenes; on keel-web 257 the link's film held longer on the pain scene than on the scene before it |
| FR-4 | `harness/three_surfaces.py` (`GATE_WORDS`, `screener_first`), `interviewer_screens.GATE_WORDS` / `FREQUENCY_LABELS` / `FILM_LINK_ORDER(_NO_SCREENER)`; `three_views_strangers.wire_checks` (*Did this happen to you?* on the problem's gate and the solution's anchor), `screener_order_check`, `film_first_checks` (258's order), `gate_clip` (after *Begin* the gate's clip on 258), `roster_on_the_wire` / `roster_on_screen` (the screener's No); `interviewer_leg` docstring (its corpus links serve no film) | the gate's words on the wire on every film link and, per surface, in the three-surfaces check; the screener's No `outsideSegment: true` taken; on 258 the order and the screener's No leaving before the film |
| FR-5 | `three_surfaces.ROSTER` (the No-sayer), `owed_whys`, `response_for`; `three_views_strangers.walk_whys_on_the_wire`, `roster_on_the_wire`, `roster_on_screen` (the orb, and the face's `only_no`), `link_walk(plan=)`; the solution / money No walks unchanged (`exitText`) | the Prevalence why served on the spot after the No (`recency: false`), the response `recency: false`, no story, no Frequency, the Importance pick, one why, 201; on 258 the No-sayer's walk on the orb and the face (the why, Importance, the pilot ask, the thanks); a solution or money link's No still ending it |
| FR-6 | `classifier_guard.FREQUENCY_CONTROLS = ("fixed_five",)` (`RETIRED_FREQUENCY_CONTROLS` read as numbers on a recorded run), `EVAL_ITEMS` / `EVAL_CASES` (ten Frequency cases: *B*, *most times*, *si*, *sí*, ...); `vectors_script`: `frequency_fits` retired (`FREQUENCY_FITS_RETIRED`), `RETIRED_KEYS`, Frequency's founder answer the bin, each pick a code, the PROBLEM slice and part 1's plan on three; `instructions/corpus.py`: `spec269_frequency`, `spec269_founder_bin`, `SPEC_269_MOVES`, `SPEC_269_PROBLEM`, `SPEC_246_MOVES`, `expected_269`, `picks_269`, the loader reading registry 5 through 269; `instructions/registry.py` registry 5; `instructions/compare.py` (diff against the 269 read); `working_rung.frequency_side`; `link_walk` (Frequency said by its row's words, `ONE_PICK` + `fixed_five`) | the corpus read as keel-cloud's fixture reads it (01-countly and 04-linerly NOT_HOLDING_UP on Frequency, 03-lullaby PEOPLE_DISAGREE on Importance; keel-cloud's engine agrees on 101 of 101); the strangers' Frequency on the five codes on the wire |
| FR-7 | `three_surfaces.ROSTER` (About half with the own row, Every time without, Now and then without, Never after a yes, the No-sayer), `THEMES` / `themes_entries`, `insights_faults`; `three_views_strangers.founder_page_on_the_wire`; `report_marks.insight_faults` (`capped` where served, `tookBy` a fault beside it), `ALSO_HEADINGS_270`; `interviewer_fake.RUNG_HEADINGS` / `NO_FOLLOW_UP` / `NAMED` on registry 5 | each person owed exactly their whys, in order, the words the registry's; the Insights cards: the headings, the quotes' option (*No*, a band), `capped` with `asked + capped = against`, `tookBy` nowhere, the dissent frame |
| FR-8 | `three_surfaces.frequency_row` / `frequency_faults` / `current_solution_anywhere` / `ways_faults` / `brief_frequency_faults`, `ways_entry`, `STORIES`; `vectors_script.EXPERIENCE_WAYS_SCREEN` (in the runtime's screen table); `three_views.Run.load_runtime(extra=)`; `instructions/brief_facts.py` (Frequency's card *k of n · say most times or every time*, no Current solution card) | `chart.frequency` (`forCodes`, the share, `n`, the founder's band), no `chart.window`; no Current solution anywhere on the standings or the overview; `Overview.ways` GROUPED over the four stories with the founder's way flagged, nothing of it on Insights; `facts.problem.frequency` on bands |
| FR-9 | `three_surfaces.served_record` / `card_record` / `walked_record` / `strips_record` / `same_script` (`OPTIONAL_STEPS`); `three_views_strangers.keep_surface`, `card_script`, `three_surfaces_check` | per study the orb's link and the face's link as served and the call's script, held equal step for step (the words, the options in order, the whys, the gate); on 258 the walks' records too; where they part, the step and the surface named |
| FR-10 | the canon's `letters` re-copied into `classifier_cases.py` word for word (266's and 268's: *si*, *si, please*, *sí*, two-row *si*); `EVAL_CASES` *si* / *sí* on the five rows | *si* C on three-or-more rows, unclear on two; the guard's bar unchanged (never a confident wrong answer) |
| FR-11 | `interview_charge.PRICE_VERSION_270`, `FREE_READINGS`, `reading_rows`, `free_reading_faults`; `orb_view`'s ledger checks; the solution and money journeys untouched but for the replay's tasks row (`idea_leg`, on 257) | nothing bought; every story-turn and ways row 0 credits; `PROFILE=remote` untouched |
| FR-12 | `three_views_report.surface_rows` / `surfaces_markdown` (*The three surfaces*), `founder_beats_markdown` (*The founder's seven beats*), the head's contract; `e2e_157_three_views` passes them; `runs/DRIFT.md` | the report's two sections; the DRIFT entries below |

## Pending keel-web 257 / 258 (written to the specs, not DRIFT)

The keel-web checkout the stack serves (`f7d00534`) carries neither 257 nor 258, so these checks are written and red by
name in the one run until they merge -- one failed check a story or a link, `stop=False`, *pending keel-web 257* /
*pending keel-web 258*, listing what it stands for (or a note where the leg reads the cloud alone):

- **keel-web 257** (FR-1 a-d, each story): the seven questions on `story-q`; no button on the seven beats; the long beats
  closed by *That's it.* and sent without it; beat 3 in two parts across 7 s (*Take your time.*); the board's seven rows
  lit in turn (the tasks row last); the tasks row redrawn after its correction; the verdict on `story-verdict` with *Say
  yes, or just tell me if you want a different bar.*; the film held longer on the pain scene (the founder's and the
  link's); no belief page after the window page; the replay's tasks row (FR-1b, FR-1c).
- **keel-web 258** (FR-2 problem orb, avatar and copilot; the order on every film link): the screener before the film;
  the screener's No leaving before the film; Frequency's five rows drawn and answered by letter and by words; a No that
  goes on (the why, Importance, the thanks) on the orb, the face and the Copilot card; every why answered in words; the
  walks' three-surfaces records; after *Begin*, the gate's clip first.

## Judgement calls

1. **Before keel-web 257 / 258 the cloud is read on the wire.** The brief asks one run that proves the cloud's reads while
   the web specs are not merged. A founder's story on keel-web `f7d00534` (five beats) cannot walk the cloud's seven, and
   its player cannot draw `fixed_five`; so where the checkout lacks 257 (`story_screens.web_has_257`: `LONG_BEATS` and the
   seventh question in `storyLines.ts`) the story is told on the wire as 257's page sends it (`StoryWire`), and where it
   lacks 258 (`web_has_258`: `fixed_five` in `Control.tsx` and `aiInterviewFlow.ts`) the problem link's four questions are
   answered on the wire (`roster_on_the_wire`). Every screen check is written to the specs and runs once they merge;
   before that, one failed check a leg names what is pending.
2. **The page is taken off the story's route** (`about:blank`) before a wire telling, so keel-web 245's own conversation
   sends nothing meanwhile; the waiting solution or money start (browser storage) is kept and the walk goes on at the
   address keel-web's return trip lands on (`/?start=solution&problem=...`).
3. **The done word the walk says is *That's it.***, at the end of the beat's one utterance (keel-web 257 FR-11: *closing the
   last chunk*); a done word inside the words (beat 4's scripted *Yes, that's it: ...*) is not a close. The words sent are
   compared without it; a long beat closed by the quiet fails.
4. **Beat 3 in two parts**: the first part (the way and two limitations), 7 s of quiet read every 250 ms (`story-state`),
   the second part and the done word; *joined* is the request's words holding both. The 20 s / 60 s *Anything else?* ladder
   is keel-web's unit test (the spec's word).
5. **The tellings over the legs**: FR-1a the script's words (the tasks row corrected by the cloud's own correction,
   `fake-readings.json`'s `corrections` entry that writes `other_tasks`) and the long telling (with *only the ones in
   Europe*, the cloud's own entry since keel-cloud 264); FR-1b's problem the two parts; FR-1c's problem the limitations
   alone.
6. **The corpus revision is a read.** The corpus files are keel-cloud's canon, never written here (spec 010's one place;
   the brief forbids touching the sibling). keel-cloud 269 judgement call 1 reads them through 269 in
   `VectorCorpusFixture` and leaves the revision that records the scale owed; the eval reads them through the same rules
   (`corpus.spec269_frequency`, the founder's bin `p_60_80`, `SPEC_269_MOVES` / `SPEC_269_PROBLEM`, Current solution not
   asked) and names its read `r23+269`. The loader reads registry 5 through 269 (Current solution's records read as not
   asked, a recorded Frequency count never held to the five codes). `SPEC_246_MOVES` is carried as the fixture carries it,
   so keel-cloud's engine agrees on all 101 checks.
7. **The founder's Frequency bin** is `p_60_80` on every entry (code's default at the boxes' yes, D3) -- *a founder bin per
   entry* read as keel-cloud reads it; a left-out Frequency stays left out.
8. **A recorded 0 after a yes is *Never*** (D2, the floor): spec 090's *sent as 1* retires with the count; the five names stay
   in `ZERO_SENT_AS_ONE` for the record and none is replayed.
9. **The roster is the problem study's.** Only the PROBLEM-scope link asks Frequency and Importance; the solution and
   money links' whys are their own and unchanged (their No still ends, `exitText`). The roster's stories differ so the ways
   group (two the founder's way, one another, one none); its whys are answered in words the scripted THEMES groups
   (`three_surfaces.THEMES`: labels sharing words with their answers, never the rung's name).
10. **The ways are GROUPED by scripting the reading.** The founder is on her own AI, so `EXPERIENCE_WAYS` runs on the
    scripted runtime; the walk reloads it after the roster with the THEMES and the ways' answer over the invitation ids it
    just made (`Run.load_runtime(extra=)`), and puts `EXPERIENCE_WAYS` in the runtime's screen table from keel-cloud's
    export.
11. **`capped` is read where served.** A standings record that carries `capped` (contract 87) is held to `asked + capped =
    against` and refused a `tookBy`; a record from before 270 (the eval's fixtures) is read by 104's `tookBy` sum. No one of
    the roster can be past two whys on the problem study (a No skips Frequency), so `capped` reads 0 there.
12. **The three surfaces are compared as served on every run**, the walks' records only where keel-web 258 drew them. The
    screener and the decision-maker's check are compared only where all three carry them (the call's script files the
    screener on the gate passage and has no passage of the check: noted on the verdict, `not_on_every_surface`, never a
    part); the items and the gate must be on all three.
13. **The fake's ladder port (spec 051) is not moved** to the gate's and Frequency's rungs: the S-0xx journeys' typed path
    asks no film and their whys are the cloud's; only its registry mirrors (headings, the no-why list, the named wordings)
    are registry 5's. The junk follow-up of spec 076 moved from Priya Natarajan (whose one rung was Current solution) to
    Aisha Rahman (Commitment), the one 01-countly person still owed exactly one why.
14. **Tests of a retired screen skip by name**: Current solution's Check hold (`test_ladder_rewritten_whole_145`) and a
    spoken record of record written before 269 (`test_money_cards_redrawn_118`); every other moved mirror's test is
    re-pinned to 268-270 with the spec named.

## Runs
| run | result |
|---|---|

## Commits
| Commit | FR | What |
|---|---|---|

## DRIFT written
