# Spec 161 -- The four questions, walked: the founder's seven beats, the board's three rows, the pain scene, the gate's words, a No that goes on, Frequency's five rows, every why, the ways; the orb, the face and the Copilot card compared

The founder, 2026-11-23 (`keel-cloud-docs/canon/designs/four-questions-design-2026-11-23.md`, the design of record;
§3 D12: *"ensure that the voice interview, the AI avatar and Copilot all are in sync"*). keel-cloud 268 (seven beats,
`otherTasks`, the pain scene, the letter C as *si*, contract 85), 269 (the four questions, the No path, `fixed_five`,
Importance over the role's tasks, Current solution gone, the beliefs written at the board's yes, `verdictLine`,
contract 86), 270 (follow-ups on every rung against, `Overview.ways`, contract 87), keel-web 257 (the founder) and 258
(the stranger, the founder's page). Spec 160's walks read the old questions; this spec moves every mirror and adds the
three-surfaces check. Nothing paid (FakeSpeech, the fake avatar, the fake transcriber, the fake readers).

## Rules

- **FR-1 The founder's beats.** `harness/story_screens.py`: `said_turns` reads seven beats (1 who; 2 what and when;
  3 the way and every limitation in one breath; 4 the cost; 5 all or some; 6 the when where beat 2 named no moment;
  7 two or three other tasks) and refuses any other order; `fake_readings` scripts (every study's `story` fixture)
  gain beats 3, 4 and 7 with their `heard` words and the slots read (`steps`, `act`, `limits`, `cost`, `otherTasks`),
  one script keeping beat 3's limitations-only answer so the one `ask` (*And how do they do it today?*) is walked;
  `long_beat_3` tells the way as well as the limitations; `heard_cost` stays (a cost heard early is on the board
  before beat 4, and beat 4 is still asked). The walk (`evals/three_views.py`, the founder's legs) answers seven
  beats by the fake transcriber, nothing pressed, and reads the board's rows: who, job, when, today, falls short,
  costs, other tasks (`UnderstoodCard`), each lit as named; a correction on the tasks row by voice redraws it.
- **FR-2 The verdict and the corridor.** After the film's yes the walk hears the verdict line (`story-verdict`,
  the served `verdictLine` word for word) and answers nothing (silence goes on); then the window page, then the
  ready page: **no belief page is drawn** on a spoken PROBLEM project (`vectors_screens.calibrates` learns `spoken`;
  the PROBLEM walk is skipped on a story project and the review table's three rows are read as written:
  *6 or 7 in 10*, the Frequency bin, the Importance list with the own row first then the other tasks). The typed path
  (the corpus studies walked by typing) still walks the belief pages, with Current solution gone from
  `REVIEWED_LISTS` and from the count of screens (`SCOPE_STEPS` unchanged).
- **FR-3 The pain scene.** `story_screens` reads seven scenes from `story/drawn` and the link's `story`: the
  seventh with `pain: true`, its line the board's cost, a picture (library id or `drawn-...`), `costLine` equal to its
  line, eight clips; the film on the link (`interviewer_screens`, 160 FR-4's checks) ends on the pain scene before
  `ai-film-begin` and its step is held longer than a scene's (the fake clock, two holds).
- **FR-4 The gate's words.** On a film link the gate's question is exactly *Did this happen to you?* (no window
  phrase) on the orb, the face and the Copilot card; the No label the served one. `interviewer_screens`' gate reads
  and `classifier_guard`'s gate cases follow.
- **FR-5 A No goes on.** The No-sayer's walk (one per study, orb and face): the No said, the Prevalence follow-up on
  the spot (*How do you go about it, and what keeps this from happening to you?*, heading *What keeps it from
  happening to them*), then Importance, the pilot ask, the thanks; the response's shape (the gate's No, no story, no
  Frequency, the Importance pick, one follow-up) read on the wire; the person counted in Prevalence's denominator
  and in Importance's picks on the founder's page. 160's refused-mic and chip-only walks unchanged. A money or
  solution link's No still leaves (`exitText`).
- **FR-6 Frequency's five rows.** `classifier_guard.FREQUENCY_CONTROLS` becomes `("fixed_five",)`; `vectors_script`:
  `frequency_fits` is retired -- Frequency is always asked (no window to fit); the corpus's `problem.frequency` on
  each entry becomes a founder bin (`p_0_20` .. `p_80_100`, the share of yes-sayers on *Every time* / *Most times*)
  and each person's pick one of the five codes (corpus revision bumped, `tests/test_corpus_r11_shape.py` and its
  successors follow); the stranger answers by letter and by words on the orb (*B*, *most times*, *si* for C); the
  classifier cases for Frequency (`harness/classifier_cases.py`) are on the five codes; the held / against reading of
  each pick for the ladder (`working_rung.py`): A and B support, C, D and E against.
- **FR-7 Every why.** Each study's strangers include: one yes-sayer on *About half the time* who picked the own row
  (Frequency's follow-up alone), one on *Every time* who did not pick the own row (Importance's alone), one on *Now
  and then* who did not pick it (two follow-ups, Frequency's first), one on *Never* after a yes (the second stem *You
  said it happened to you. Tell me about that time.*), and the No-sayer of FR-5. The Insights tab's cards are read
  as spec 119's: one card per line with words, the headings of the three blocks, the groups, the quotes with the
  option and the side, the dissent frame on a held line, `capped` where a person was past two, `tookBy` nowhere.
- **FR-8 The ways and the founder's page.** `report_marks` / `three_views`: the Overview's Frequency card as five
  bands with the two "for" bands shaded and the share caption; no Current solution card, row, breakdown line or
  insight anywhere; the ways panel (*How they do it today*, *read from the {n} experiences, not asked*, the groups
  with the founder's way marked) present only once two or more stories are stored, in `GROUPED` state on the fake
  reader, and never on the Insights tab; the brief's Frequency section and the export on bands.
- **FR-9 Three surfaces, one script.** For each study, the orb link, the face link and the Copilot card (the copilot
  legs, `calls_leg.py`, headless) are walked through the same study and the walk records, per step, the question's
  words, the options' labels in order, the follow-up stems and headings, and the gate's words; the check: the three
  records are equal step for step but for the face's own clip routes and the card's digits. Where they differ the leg
  fails by name and says which step and which surface. 160 FR-3's same-walk check on the two speakers stays.
- **FR-10 The letter C.** `classifier_guard` and the orb's spoken-answer cases: *si* and *sí* read as C on a three-or-
  more-row item, unclear on a two-row one; never a confident wrong answer.
- **FR-11 Untouched.** The ledger and charge checks (nothing bought; `STORY_TURN` and `EXPERIENCE_WAYS` priced 0 read
  on the ledger); the solution and money journeys but for the replay's tasks row; `PROFILE=remote` untouched.
- **FR-12 Report and DRIFT.** The report's *The two speakers* section becomes *The three surfaces*: one row per study
  per surface with the state sequence and the one-script verdict; a *The founder's seven beats* section with the
  board's rows and the verdict line heard; every cloud or web finding to `runs/DRIFT.md` in the usual shape. Contract
  87 read on `x-keel-contract`.

## Acceptance

`make unit` with no new red; a local `make e2e-157 PROFILE=eval` against the sibling main checkouts keel-cloud-docs
(270 merged, contract 87) and keel-web (258 merged) with every 161 check held or a DRIFT entry naming the defect; the
founder's legs, the copilot legs and the ledger checks green; nothing paid. The run on merged masters is the
integrator's run of record.
