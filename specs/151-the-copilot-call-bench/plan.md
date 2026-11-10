# Plan 151 -- The copilot call bench

**Branch** `spec-151` | **Worktree** `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-151` | **Spec** `spec.md` beside this
file | **Design of record** the founder's methodology page of 2026-11-10 (artifact LbKL7ArmfrGD3J5bvhdGHH v7).

## Summary

The referee's harness for a copilot that does not exist yet: a questionnaire fixture read from one back-test bundle, a
catalogue of founder habits and respondent behaviours as data, a script writer (Sonnet 5.5) checked offline against the
catalogue's rules, a two-track renderer on the noise check's TTS, three OpenAI stacks behind one event interface, an
offline scorer for the seven numbers (A--G) against bars the founder can change, and one paid command with a free
`DRY=1`. Built in the noise check's shape (`evals/noise/`), reusing `norm_out`, `ok`, `tts`, the beds and the key
refusal wherever they fit. Nothing is called by the builder: every model call goes through an injectable transport,
the tests and `DRY=1` run on fakes with no key.

## Technical context

- Python 3.12 (the repo's `.venv`), `requests` for HTTP as `evals/noise/pipeline.py` does (no SDK in this repo).
- The audio path needs numpy + soundfile (the noise synth's own optional deps, not in `requirements.txt`) and, for
  Stack 2, `websockets`; both are imported lazily and refused by name when absent. The unit tests need neither: the
  timeline arithmetic is pure Python, the websocket client is exercised through a fake transport.
- Storage: run folders under `runs/` (git-ignored); the fixture is committed under `evals/copilot/fixtures/`.

## Layout

```text
evals/copilot/
  __init__.py
  questionnaire.py      FR-1 bundle -> fixture (controls -> noise kinds), load(), noise_item()
  catalogue.py          FR-2 founder + respondent kinds, verdicts, tiers, states, mechanical rules
  plan.py               FR-3 the rounds' coverage plans (R1 exhaustive <= 700, R2 200, R3 120, R4 12), seeded
  writer.py             FR-3 prompt, Sonnet request, parse, validate, rewrite once, drop + count; FakeWriter (DRY)
  render.py             FR-4 two tracks on one timeline via evals.noise.synth.tts, turn clocks, optional noise bed
  clients.py            the paid transports (Anthropic, OpenAI transcribe / audio / realtime) + the key refusal
  stacks/__init__.py    FR-5 registry; Event shape; canned events
  stacks/base.py        the interface, the shared JSON read (event_from), the item block of every prompt
  stacks/turn_by_turn.py    Stack 1
  stacks/running_state.py   Stack 2 (+ the Realtime transcription client, transport injectable)
  stacks/audio_direct.py    Stack 3
  instructions/copilot-match.md   Stack 1's system prompt
  instructions/copilot-state.md   Stack 2's system prompt
  instructions/copilot-audio.md   Stack 3's system prompt (the audio-direct prompt)
  bars.py               FR-6 the founder's bars, one table
  score.py              FR-6 A--G, the certificate line, costs
  report.py             FR-6/7 sheet.json/.md per stack, page/, register row
  bench.py              FR-7 the command (argparse), DRY path
  fixtures/questionnaire-08-fresco.json
tests/test_copilot_bench.py   FR-9
```

## Decisions (judgement calls, recorded in tasks.md too)

1. **Truth form.** The spec's fixed form plus one optional turn key, `kind` (the catalogue kind the turn was written
   for): the confusion matrix by habit kind (A) and the per-behaviour rows (B) need it, and the writer is told to set it.
   Respondent answer turns carry `verdict: null` (they ask nothing); a respondent turn that belongs to no answer
   (a counter-question, a second voice) carries `nothing`; a reply to a follow-up carries `follow_up`.
2. **Controls.** `value_box`, `cost_total` -> `number` (unit from `valueBox.measure`, else the currency; range open);
   `price_ladder`, `single_choice`, `fixed_three`, `fixed_four`, `scale_four`, `duration_bands`,
   `benefit_with_advantages` -> `single`; `pick_two`, `pick_one_then_one` -> `multi` with `pick: 2`; the served gate ->
   `gate` (Yes/No) and its story prompt -> `free`. An unknown control is refused by name, never guessed.
3. **Tiers.** sure / likely / unsure, the AI interviewer's three; the classifier's high / medium / low read onto them
   in that order where a stack answers in the classifier's words.
4. **Rounds' cells.** R1 gates A, B, E, G; R2 and R3 add C and D; R4 adds F. A cell outside the round is *not
   applicable*; a cell inside it with no rows is *not measured* and makes the certificate INCOMPLETE, as the noise check.
5. **SAMPLE stops the run** after `scripts.jsonl` and `sample.md`, before any audio or stack call, so the reviewer reads
   first; `RESUME=` continues from the written scripts.
6. **DRY** writes three scripts with the fake writer (catalogue templates, validated by the same rules), renders
   nothing, runs Stacks 1 and 2 at the text level through fake clients that answer the canned event of each turn, and
   scores those events; exit 0 whatever the certificate.
7. **Prices.** gpt-transcribe $0.0045/min, gpt-live-transcribe $0.017/min, gpt-audio-mini $10 / 1M audio tokens in
   (the page), gpt-4o-mini-tts about $0.015/min (the page), Haiku 5.5 $0.10 / $0.50, Sonnet 5.5 $2 / $10 per million
   tokens (Anthropic's list). gpt-audio-mini's text-token rates are not on the page: counted, priced at 0, named owed.
8. **Not verified against a live vendor.** The Realtime transcription session shape and gpt-audio-mini's chat
   request are written from the vendors' documented shapes and pinned by fakes; the first paid R1 audio run is the
   check (owed).

## Gate

`make unit` green, whole and unpiped; `make copilot-bench ROUND=1 LEVEL=text DRY=1` green with no key; the new files
byte-compile and pass `ruff check` (installed into the worktree venv for the check; the repo carries no lint target).
