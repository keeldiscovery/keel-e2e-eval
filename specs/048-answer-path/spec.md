# Spec 048 -- The answer path, as the eval sees it

keel-cloud 099 and keel-web 072 (design keel-cloud `canon/designs/answer-path-2026-10-16.md`; evidence
`canon/designs/spoken-classifier-check-2026-10-16/`). **Contract 17 -> 18.** The AI interviewer no longer has
"That's my answer": the cloud's classifier decides, the page holds a confident read for two seconds, asks "Is that
right?" on a medium one, and falls into the didn't-catch path on an unclear one. The intro gains Test your mic.
Two new participant routes (`classify`, `answer`); `clips.isThatRight`; `AnswerHow` gains RECORDED.

## Rules

- **FR-1 Contract 18** wherever 17 is pinned (`harness/`, `stack/`, README, AGENTS, the corpus marks).
- **FR-2 The stack stays free and offline.** keel-cloud's defaults (`transcriber: fake`, no OpenAI key, no Anthropic
  key for the classifier -> `FakeClassifier`) are what the stack runs; no vendor is called; the live cell never runs
  the audio set. The weekly live cell (`keel-e2e-eval` matrix's live column) gains **one** text-only check: the
  classifier cases below against the real route on staging for the founder's identity, budget under $0.10.
- **FR-3 The classifier guard.** `canon/designs/spoken-classifier-check-2026-10-16/cases.py` (152 cases) copied to
  `harness/classifier_cases.py` (one source: the eval owns the copy from now on, the canon keeps the record). A unit
  test drives `POST /v2/i/{token}/interview/classify` on the stack (fake classifier) with each case and asserts: a
  plain-answer case returns that answer with `confidence` high or medium; an ambiguity case returns `unclear` or
  medium; **never** a confident wrong answer. The confirmation cases run with `previous`.
- **FR-4 The speech seam gains classify.** `harness/interviewer_screens.py` `Player` learns `hold()` (wait for the
  held status and let it elapse), `veto()` ("no" in the hold), `yes()` (the Yes chip or "yes" said), `back()` (Back or
  "go back"), `mic_test(heard="hello")` on the intro; `say()` ends the utterance the way the page now ends it (a
  final then `onend`), no `answer()` tap. The fake recogniser in `browser.py` is unchanged; `window.__keelSpeech.classify`
  (web judgement call 1) is scripted where a journey needs a scripted tier, else the route is left real (the fake).
- **FR-5 Journeys** (`evals/interviewer_leg.py` and the AI-link scenario): the AI link opens on the intro -> Test your
  mic -> "Heard: hello" -> Start -> opening + problem passages -> gate "yes" (held, no tap, next by itself) -> story
  spoken -> an option question answered with the option's own words (held) -> one answered "payroll" (medium ->
  "Is that right?" -> "the first one") -> one answered "the first one, wait, actually the third" (held on 3) -> Back
  from the next question, change it by tap, forward again -> a number "about three" -> an amount "two hundred dollars"
  -> the pilot ask "yes" -> Finish -> the response carries `how` SPOKEN/TAPPED per answer, `heard` per answer, and the
  changed answer; `ai-answer` never in the DOM; the status words in order (`__keelPhases`).
- **FR-6 Try it yourself** (the founder's dry run) runs the same path with the no-op writer; the walkthrough's frame
  with the hold is screenshotted for the marks.
- **FR-7 Marks.** The interviewer marks (`evals/interviewer_marks.py`) add: hold observed (status `AI_HELD` then next
  without a tap), confirm observed, back observed, mic test observed, RECORDED accepted by the response schema.
- **FR-8 Vectors.** `harness/vectors_screens.py` / `vectors_script.py` that pressed `ai-answer` stop doing so.

## Acceptance

1. `make unit` green; the classifier guard passes on the stack's fake (no confident wrong answers; corrections right).
2. `make eval K="<the AI link scenario>"` green on the stack; remote journeys green on staging once cloud 099 and
   web 072 are deployed there.
3. The live cell's classifier check wired into the matrix, skipped unless the live column runs.

## Judgement calls (decide, document in tasks.md, do not ask)

1. Whether the journey scripts tiers through the seam or trusts the fake's own tiering (prefer the fake: it is what
   staging runs for eval founders).
2. The marks' names and the corpus revision bump.
