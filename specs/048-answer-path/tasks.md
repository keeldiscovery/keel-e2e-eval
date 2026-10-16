# Tasks 048

- [x] T001 Contract 18 pins; `harness/classifier_cases.py` from the canon's `cases.py`
- [x] T002 Classifier guard unit test against the stack's `classify` route (FR-3)
- [x] T003 `Player`: `hold`, `veto`, `yes`, `back`, `mic_test`; `say` ends the utterance; no `answer` (FR-4)
- [x] T004 Journeys (FR-5, FR-6) + marks (FR-7) + vectors (FR-8)
- [x] T005 Live cell: the text-only classifier check (FR-2)
- [x] T006 `make unit`, `make eval` on the stack green; judgement calls written here -- remote journeys on staging wait
  for cloud 099 + web 072 to be deployed there

## Measured (2026-10-16, keel-cloud-docs `0f582b2` + keel-web `d49f013`, stack fakes only, a fresh stack)

- `make unit`: **2,298 passed / 53 skipped** (was 2,078 / 53 before spec 048; the 072 source checks now run).
- `make eval K="s005 or s006 or s007"`: **3 passed** (582 s). S-005 interviewer marks v2 **12 of 12** owed (IM14-IM17
  among them); S-006 **17 of 17** (IM14-IM18; IM12 unmeasured as before, DRIFT #86). Classifier guard on the links:
  S-005 116 asked / 103 right / 13 safe / **0 wrong**; S-006 80 / 71 / 9 / **0** on the stranger's route and the same on
  Try it yourself's founder route; the three corrections right on both.
- Not yet: the remote journeys on staging (cloud 099 / web 072 not deployed there); the live classifier check (needs
  `KEEL_CLASSIFIER_LINK`).

## Where things are

| Piece | Place |
|---|---|
| the 152 cases, copied whole | `harness/classifier_cases.py` (canon `spoken-classifier-check-2026-10-16/cases.py` at keel-cloud-docs `0f582b2`, a header above it) |
| the guard (served items, transposition, judge, run) | `harness/classifier_guard.py`; stackless tests `tests/test_classifier_guard.py` |
| the guard on the stack | `evals/interviewer_leg.py::_classifier_guard` (the stranger's route, before the AI link is answered) and `::_dry_run_guard` (Try it yourself's founder route) |
| the Player | `harness/interviewer_screens.py` (`mic_test`, `hold`, `veto`, `confirming`, `yes`, `back`, `save`, `finish`, `wait_ear`, `statuses`) |
| the walk | `evals/interviewer_leg.py::_Walk`, `::_answer_ai_on_screen`, `::_dry_run_on_screen`, `::_recorded_link` |
| the marks | `evals/interviewer_marks.py` IM14-IM18, `INTERVIEWER_MARKS_VERSION` 2 |
| the live check | `evals/test_classifier_live.py`; `matrix/cells.toml` (`classifier` live, on the weekly macOS x Claude 3.13 cell); `.github/workflows/matrix.yml` (`KEEL_CLASSIFIER_LINK`) |
| the stack | `stack/cloud.py`: `KEEL_INTERVIEWER_TRANSCRIBER=fake`, `KEEL_OPENAI_API_KEY=""`, `KEEL_INTERVIEWER_FAKE_TRANSCRIPT=yes` |

## Judgement calls decided

1. **The journey trusts the fake's own tiering** (the spec's call 1, as preferred). The eval's `SPEECH_SEAM` restates
   keel-web 072's fixture -- a final result followed by the recogniser's end, a granted microphone -- but puts **no
   `classify`** on `window.__keelSpeech`, so the page calls the real route and the stack's keel-cloud answers with its
   `FakeClassifier` (what staging runs for eval founders). Tiers are reached by what is said: a correction ("the second
   one, wait, actually the first") and one word two labels carry are unsure by the fake's own rules.
2. **A correction lands on "Is that right?", not on a hold.** FR-5 reads "the first one, wait, actually the third (held
   on 3)", but keel-cloud 099's judgement call 8 makes a correction word turn a high first answer medium (design §2's
   Uncertain tier). The journey follows the cloud: the corrected pick is lit, *Is that right?* is asked, "yes" takes it
   straight on. IM15 is owed through it, so "Is that right?" is measured on every link whatever its labels.
3. **The "payroll" move is opportunistic.** The stack's links carry corpus labels, not the payroll fixture's; the walk
   says one word of the person's option that another option also carries (the fake reads it medium, runner-up the other)
   where one exists, then names the option by its place ("the third one"). Where no such word exists it is not
   attempted; the correction already measures the tier.
4. **Every move ends on the corpus person's own answer.** The response is still held to `sent == want`; the Back move
   says another option first (held, gone on), then Back from the next question and the person's option tapped -- the
   response carries the changed answer, `how` TAPPED. Numbers are said "about n" after one miss ("31"); a whole cost
   total is said in the served currency's word ("300 dollars"), a fractional one typed with *Save and next*.
5. **The classifier guard carries the cases onto the link's own items** (FR-3 could not be met literally: the route
   builds the question from the item the link serves, and no stack link serves the check's payroll items). A whole
   label becomes the served label at its place; each other label word becomes a served-label word in the **same set
   of places**; punctuation is kept (the fake reads "no," and "not X,"); turn words (yes, right, actually, all, last...)
   are never moved; a case whose words cannot be carried, or whose carried words would say a served label whole by
   accident ("no" against a served "No"), is **not asked** and named with its reason. The four correction cases are
   label-independent and are asked wherever the shape fits. Measured on the stack (keel-cloud-docs `0f582b2`): Paidly's
   link 83 asked, 73 right, 10 safe, **0 wrong**; Countly's 119 / 105 / 14 / **0**; three corrections right on both
   ("three days, no wait, five" needs a served number in days 0..30, which neither link has).
6. **The guard runs in the AI-link leg, not in `make unit`.** `make unit` stays stackless (AGENTS.md); its half of the
   guard is `tests/test_classifier_guard.py` (the copy equal to the canon, every case asked of its own item unchanged,
   the transposition's rules, the judge, the fake's reasons parsed from keel-cloud's source). The stack half runs on
   every S-005 / S-006 before the AI link is answered (the stranger's route) and on Try it yourself (the founder's
   route, plus an item not on the form -> 422 ITEM_NOT_ON_FORM).
7. **The live check takes a named link.** Every matrix founder is `@keel-e2e-eval.test`, inside `fake-for`, so their
   links answer with the fake; a link the real model answers needs a READY recording on a founder outside `fake-for`,
   which a cell could only make by paying the renderer. So `KEEL_CLASSIFIER_LINK` (a secret) names an unanswered link
   the founder makes once on his own staging project; `classify` stores nothing, so it serves every week -- until a
   reset of the twin wipes it (then the check skips by name until a new one is set). It is not a scenario (the set stays
   thirteen) but it is the **fourth named LLM place** in AGENTS.md, argued there. A run whose every reason is one the
   fake writes (`FAKE_REASONS`, held to keel-cloud's source) fails as "measured the fake", and one of nothing but
   `timeout` / `vendor` as "Keel's AI never answered". Budget: 152 x $0.0006 = $0.09, refused over $0.10.
8. **RECORDED is measured on the wire.** The browser path cannot produce it (the seam has a recogniser); S-006 makes one
   more AI link on the wire and answers it from the recorded path: a 12 KiB-minus-one-byte webm is silence (`heard` "",
   reason silence, never transcribed), a 16 KiB one is written down by the stack's fake transcriber (pinned to "yes")
   and read Yes, and a response whose answers say `how` RECORDED is stored ANSWERED (IM18). It is read on arrival like
   every other answer.
9. **Marks**: `INTERVIEWER_MARKS_VERSION` 1 -> 2. IM14 *held then on* (the held status, nothing pressed in the hold, the
   next question by itself, a "no" in a hold reopens, `ai-answer` never drawn), IM15 *asked Is that right?*, IM16 *went
   back*, IM17 *mic tested* (Start disabled before, *Heard: hello* and Start enabled after), IM18 *RECORDED accepted*;
   IM3 owes one IS_THAT_RIGHT a role beside DIDNT_CATCH; IM8 reads the answer path's reads (classify / answer /
   transcribe) as no write; IM9 takes RECORDED with its words. S-005's short form owes IM14-IM17. **The corpus revision
   stays 11 and `MARKS_VERSION` 19**: 099 moved no screen schema and no corpus item; its `classify-answer.md` is not a
   screen the instruction eval scores -- this repository's guard and live check are its measure.
10. **Contract 18 is pinned in prose**, where 17 was: no harness module carried the OpenAPI contract's number as a
    constant (the instruction eval's `CONTRACT_VERSION` 14 is the inference contract and did not move).
11. **FR-8 (vectors) needed no change**: `harness/vectors_screens.py` / `vectors_script.py` never pressed `ai-answer`;
    the AI interviewer is driven from `harness/interviewer_screens.py` alone, and a unit test now holds that no Player
    or leg code presses `ai-answer` or `ai-next`.
12. **Found on the way** (fixed here, not product drift): the contacts leg still asserted 1,350 credits after the first
    page (1,500 - 150) though spec 047 moved the grant to 2,000 -- S-006 failed there against `0f582b2`; and
    `tests/test_interviewer_marks.py` read keel-cloud's `ClipKind` without 099's IS_THAT_RIGHT.
13. **The walk reads where the tier lands** (after keel-web 072 merged). The page also asks "Is that right?" for one
    word two labels hold ("Yes" inside "Yes, if it was clearly worth it"; "No" inside "No, I decided on my own") even
    where the fake was sure, and a read meant to be unsure can come back sure. So every spoken answer waits for the held
    status, the unsure one, or the next question: unsure where a hold was meant -> answered ("yes" if the lit one is
    meant, else its place) and kept as an "Is that right?" turn; sure where unsure was meant -> held on the one meant,
    or "no" in the hold and the one meant by its place, and the move tried again on a later question. The Back move says
    the clearest other option (no label inside another) and is tried before the shared-word move, so a short form like
    Paidly's still goes back once; Back and the veto are never tried on benefit_with_advantages (072 call 7: Back lands
    on the main ask and asks the advantages again). The veto is said as an interim (072 hears it in an interim and keeps
    the recogniser, call 5), so the option said next is the new answer, and the same pick said again may be taken
    straight on. IM14-IM18 are owed on S-006 whatever the record carries.
14. **A stray overview read on Keel's keyless door** (found running S-006): the recorded link first took its revision
    from `GET overview`, which on Keel's door starts the stale brief (096 FR-D), fails it keyless, and leaves that
    staleness "tried" -- no brief on the founder's return later. It reads `GET persona`'s revision instead.
15. **Seen once, not reproduced**: on one S-005 run the stranger's page came back to a fresh intro (Test your mic not
    done) right after the story was said; the next three S-005 runs did not. Not filed as drift. A failed S-006 that
    has already sent its AI response leaves answers unread, and S-007's connect then reads them on S-007's script
    (standings off by one person) -- a fresh stack after a failed S-006, as before.
