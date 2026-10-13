# Spec 039 -- the corpus journeys are vectors journeys

Sibling of keel-cloud master `b8a4eed` (085 merged; registry 3, corpus r9) and keel-web master `e54cb1c` (061 merged).
Classic (the STAGES flow: framing, review cards, classic picks, SUPPORTED / CONTRADICTED / MIXED) is about to be deleted
from both, with no migration. S-005, S-006 and S-007 -- the corpus journeys -- walked classic and had refused by name since
spec 029 (`corpus_script._refuse_r3`). They now walk the **vector corridor** on the golden corpus revision 9, so they are
the journey coverage that survives the deletion. No MARKS_VERSION, POLICY_VERSION or run of record moves.

## What the journeys do

- FR-001 One function per leg in `evals/corpus_scenario.py`, in the corridor's order: `leg_project`, `leg_context`,
  `leg_interpret_problem`, `leg_calibrate(PROBLEM)`, `leg_interpret_solution`, `leg_calibrate(SOLUTION)`, `leg_persona`,
  `leg_calibrate(COMMERCIAL)`, `leg_lock` (idea approved, lock, three parts' questions READY), `leg_invite`,
  `leg_interview`, `leg_standings`, `leg_brief`. A later spec changes one leg and leaves the others alone. The entry id is
  still the only thing that differs between the three modules (spec 010 FR-015).
- FR-002 Every inference job is answered by keel-runtime's **scripted** executor from the entry's own stored texts
  (`harness/vectors_script.py`): CONTEXT_INTERPRET (`context`), PROBLEM_INTERPRET (`interpretations`),
  SOLUTION_MECHANISM (`solution_mechanism`), CALIBRATION_QUESTIONS (three entries, P/S/C, the corridor's order),
  RESPONDENT_QUESTIONS (one per part and link), INTERPRET (each readable person's golden `anchoring`, in corpus order --
  the founder reads after each person) and BRIEF (a referee-worded reading, checked by keel-cloud). No model runs;
  `evals/policy.py`'s named LLM places are unchanged.
- FR-003 The executor matches screens by exact context key set, and keel-cloud's export writes one **union** for
  RESPONDENT_QUESTIONS where the cloud sends four sets (part 1; part 2 + `mechanism`; part 3 + both; the decision-maker's
  part 3 + `offer_name`). `vectors_script.context_keys_for` derives four aliases from the export, drops the classic
  screens, and refuses an export that no longer carries both keys. The run exports keel-cloud's contracts into the bundle
  (`export/`, `context-keys.json`) and hands the runtime `KEEL_SCRIPT` and `KEEL_CONTEXT_KEYS`.
- FR-004 Screens and wire, as before. The founder's corridor, the People page's two popups, the respondent's interview and
  the three answer pages are driven through keel-web's real screens (`harness/vectors_screens.py`; selectors from keel-web's
  `translate.ts` and its own e2e specs); each leg is then asserted on the wire beside the screen. Wire-only, and said where
  it happens: Frequency's answer on a one-unit window (DRIFT #74), the hourly rate when keel-cloud's default is not the
  entry's (keel-web draws a rate only under an HOURS estimate), the interview read once per person to map a corpus code to
  its option id (`InterviewIdCodec`) and label, and the brief's `fallbackUsed`.
- FR-005 Asserted against the entry (strict): the market; the context card's sentence and window; the problem card; the
  mechanism card and the idea's three lines; the registry slice per vector; each calibration screen's belief line and the
  review's rows where the entry's answer is one phrase; LEFT_OUT where the founder was unsure; the lock (version 1, READY);
  one link per person; each interview's kind and items and **the body the page POSTed equal to the person's own answers**;
  every `expected.standings` row -- status, drift, `n`, the interval counts, every `optionCounts` code -- and every
  `expected.vector_verdicts` verdict, with its deciding dimension's own status; the board's pills, bands, belief tile and
  download; each vector page's rows, amber where left out, its headline and (B2B) the decider banner; the printed brief's
  headline, decision and four sections; the corpus unchanged.
- FR-006 Extras with a vectors meaning, kept. S-005 (B2C): one respondent type, every part on one link; Existing sacrifice
  one under the floor of 5 and *Too few to call*; no Frequency asked on a one-unit window. S-006 (B2B): twelve translators
  on the full link (parts 1-2), eight decision-makers on the commercial link (part 3, no gate), the commercial vector counted
  over the eight; `floor: 5` on every dimension and every paidly dimension above it with a real status; twenty asked and
  answered. S-007 (US): the market US / TX / en-US; every amount in dollars and no pound or euro on any page the founder
  reads; *No price yet* leaves Price and Ability to pay out and the commercial vector is still called.
- FR-007 S-012 (live, never run here): leg two walks the same legs opened with `strict=False` and a patience scaled to the
  questions wait -- every screen held to the wire, nothing held to the corpus's words or counts (spec 016 FR-007); a pick
  whose code the model did not write falls back to the item's first options. `LEGS=short` stops after the context card
  (the Keel door after the problem's card and its calibration questions written, through the same functions). Leg one,
  the Keel door's six facts, the accounting and the way out are untouched. The founder and the people come through
  `vectors_script` (`people_to_invite`: the first PEOPLE readable people, and on B2B the first PEOPLE decision-makers).

## Disagreements between corpus r9 and the wire (reported, the corpus not edited)

- D-1 **Frequency.** r9 keeps every Frequency on a 0-to-7 axis in its own units ("days out of 7", "invoices out of 7",
  "working days out of 7"); keel-cloud counts it in the window's unit on 0..count. On the three entries' own windows
  (1 month, 3 months, 2 weeks) neither the founder's range nor the picks fit, so the founder leaves Frequency out and the
  journeys assert LEFT_OUT, not r9's HOLDING_UP. (The corpus README already calls the axis *known, not corrected*.)
- D-2 **Countly's one-unit window** asks no Frequency anywhere (keel-cloud 078), yet `GET standings` 500s until it carries
  an answer -- DRIFT #74. The journey sends `unsure` on the wire.
- D-3 **Cost totals' period.** r9 records every Existing sacrifice pick `period: quarter`; keel-cloud asks over the
  founder's own period (a month on all three) and stores what is typed as that. The journey re-expresses each amount by
  keel-cloud's `Period` days (x 30.4375 / 91.3125), so the engine's normalised cost is r9's. Typed as recorded, Countly's
  Existing sacrifice read 0 inside / 4 above (r9: 4 / 0) and Ability to pay's drift STRONGER (r9: none).
- D-4 **Purchase friction.** r9 records three founder labels that do not slug to its codes ("The agency owner's approval"
  vs `owner_approval`) where the calibration needs four to six, and no respondent distractors where a set needs two. The
  journey writes labels that slug to r9's codes, a fourth (`contract_terms`), and two distractors; `optionCounts` is
  compared on r9's own codes (the distractors count 0).
- D-5 **Words r9 does not record**, composed by the referee and listed in `vectors_script.COMPOSED`: CONTEXT_INTERPRET's
  required `occasion` ("time"); SOLUTION_MECHANISM's required `idea_what` / `idea_how` / `idea_belief`; Paidly's two
  `mechanism_terms` padded to keel-cloud's three; every calibration question and Prevalence clause; every registry-fixed
  scale's labels and belief phrases (r9 records only the chosen code and its phrase); every respondent question and the
  gate's clause; Importance's difficulty labels (each the slug-inverse of its code); the BRIEF reading.
- D-6 **Extras with no r9 subject.** Paidly has no dimension at exactly five anchored people (the least is eight), so
  revision 2's `S6`-on-the-floor assertion has nothing to hold; the floor survives as FR-006 says. r9 asks no physical
  unit, so Mulch Run's miles / feet / cubic yards and Countly's mockup legend went with revision 2's beliefs.
- D-7 **Belief sentences.** A multi-tick answer's sentence is joined by keel-cloud from per-option phrases r9 does not
  record, so only one-phrase answers are held to r9's `belief_sentence`; on the ladder keel-cloud names the highest rung
  (held on the review) while keel-web's live belief line joins every ticked rung (not held -- the server's sentence wins).

- D-8 **The hourly rate.** The B2B entries record `hourly_rate` 20 GBP (Paidly) and 25 USD (Mulch Run); keel-cloud's
  market-and-role default is 60 GBP and 150 USD. No screen sets a rate under an AMOUNT estimate, so the journey sets the
  entry's on the wire (`_hourly_rate`) and records the default it replaced.

## Harness changes the run needed

- `stack/vite.eval.config.ts` loads keel-web's own `reactRouter()` plugin (keel-web 023 moved to React Router framework
  mode; with the plain React plugin vite answered 404 on `/` and `make up` could not boot keel-web `e54cb1c`).
- `stack/cloud.py` sets `KEEL_VECTORS_ENABLED=true` (the staging twin's own flag; without it every corridor route 404s).
- S-002 reads its payroll fixture when it runs rather than at import (the classic reader's refusal at collection had
  interrupted every scenario's collection, so `make eval K=s005` could not run). S-004 keeps the classic `STAGES` and
  stage-card reader it was borrowing from `corpus_scenario`.
- DRIFT #75: keel-web's commercial-link popup posts the last overview poll's revision; the People page is reloaded before
  each commercial link.

## Deleted (classic-only, no caller after this)

- `evals/corpus_scenario.py`'s classic body (status words, drift clauses, legend arithmetic, review-card, deck, opened-card,
  wire and download assertions) and S-005/6/7's classic extras (the mockup legend, T027-T031).
- S-012's classic leg-two helpers (`_wait_for_turn` ... `_answer_whatever_is_asked`, the deck arithmetic, `_their_pick`),
  `OLD_STAGE_SECTION_TITLES`, `VERDICT_PEOPLE_FLOOR`, `STAGES`, `FOLLOW_UPS`, `NAMED_REASON_POLL_S`.
- `harness/stranger_stories.py` (S-012's classic interview was its only caller) and `tests/test_stranger_stories.py`.
- `tests/test_journey_untested_stage.py`; 23 tests of `tests/test_journey_one_questionnaire.py`; 4 of
  `tests/test_overview_board_markup.py`; 3 of `tests/test_participant_sections_are_occasions.py`; the r2-gated and
  classic S-012 tests of `tests/test_journey_through_a_host.py` and `tests/test_keels_ai_cell.py` (replaced by vectors ones).
- Kept, because a classic scenario still calls them until classic goes: `harness/corpus_script.py`, `evals/preludes.py`,
  `evals/payroll_exceptions*`, `corpus_facts.facts_for`, the classic page objects in `harness/browser.py`.

## Success

- SC `make unit` green. `make eval K="s005 or s006 or s007"` green against a local stack on keel-cloud-docs `b8a4eed` and
  keel-web `e54cb1c`. S-012 not run (live). No model, no money.
