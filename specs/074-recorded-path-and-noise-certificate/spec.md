# Spec 074 -- The harness follows keel-web 115 (one recorded path), and the noise-capture certificate

The founder's decision of 2026-10-26: every spoken answer takes the recorded path (keel-web spec 115 retires the
browser's recogniser; keel-cloud spec 136 reads the partial pick and lets `FakeTranscriber` hear text bytes), and
Keel certifies what the founder set on 2026-10-26 after the acoustic runs on three browser pairs (iPhone Safari,
Mac Safari, Mac Chrome; 24 of 24 quiet and 22 of 24 in the café at 5 dB on every pair): **every spoken answer is
captured right in a quiet room, and more than 90% are in a loud place down to 5 dB**, in every room; the café at 0 dB
being the stress case: reported, never gated. The measurement exists -- keel-cloud
`canon/designs/noise-capture-check-2026-10-26/` (`dataset.py`, `synth.py`, `pipeline.py`, `report.py`, 1,260
samples, the page) -- and ran by hand with keys in the shell. This spec makes it a paid eval command with the bar
in it, and moves the AI walks onto the recorder. REVISION 17; marks change only where named.

## Rules

- **FR-1 The AI walks drive the recorder.** `harness/interviewer_screens.py` restates keel-web 115 FR-5's fake:
  `installFakeSpeech` is the fake recorder plus the always-granted mic; **`__say(text, final=True)`** pulses the
  level above the threshold for a few ticks then falls silent, and the next `stop()` hands back the UTF-8 bytes of
  `text` followed by zero bytes up to 20 KiB, base64, as `audio/webm` (past the answer route's silence threshold,
  keel-cloud spec 099); the cloud's fake transcriber (136 FR-2) trims the padding and hears the words, so the walk's
  words reach the classifier through the real `/interview/answer` route as the page sends it. `__listening()` is *the recorder runs on this window*;
  `ear()`, the recogniser counts and the `not-allowed` leg go; `__recordStarts` / `__levels` / `__micReleased` stay
  and still prove nothing listened in a beat or after the thanks. The mic test is still driven by
  `__say("hello", True)`. `INTRO_TRANSCRIBED` takes keel-web 115's new line. Every journey that speaks (the three
  remote journeys, the corpus walks, S-012's full legs) green on the local stack and on staging after keel-web 115
  and keel-cloud 136 are deployed.
- **FR-2 Marks follow the screens.** Where a mark counted the recorder's banner, the recogniser's restart or the
  probe (IM5, the answer-path marks of specs 048–050, the speak-or-type marks of 051/052: say which), it is
  re-pinned to the recorded path; no mark is dropped silently, and the pins' *why* names this spec. Keel-web 116
  moves the microphone's release to the end of the thank-you clip (and keeps the stream through a pilot ask that
  follows *End*): the leg's *Microphone off* fact (075 FR-4, `ai-mic-off`) is read once the done screen shows it, and
  the pilot ask after *End* is asserted to record (`__recordStarts` grows) rather than to have let go.
- **FR-3 `make noise-check`: the certificate.** A paid command, never in `make eval`, `make unit`, the matrix or
  a schedule, run on the founder's word (`KEEL_OPENAI_API_KEY` and `KEEL_ANTHROPIC_API_KEY` from the shell, never
  logged, echoed or written). `evals/noise/` carries the check moved from the canon folder (`dataset.py`, `synth.py`,
  `pipeline.py`, `report.py`, `page_template.html` -- the canon keeps its README and results as the record of
  2026-10-26, with a pointer here): the 1,260 samples are read from `KEEL_NOISE_SAMPLES` (default
  `~/Documents/projects/keel-noise-check-2026-10-26/audio`, the kept set) and synthesized there when absent; Keel's
  path is called exactly as the product calls it -- gpt-transcribe with the item's hints and prompt, then
  `claude-haiku-4-5-20251001` at temperature 0 and **`max_tokens` 400** (keel-cloud spec 137: the product's cap, raised from
  160 after a cut reply lost an answer in the acoustic runs) on the cloud checkout's own
  `src/main/resources/keel/inference-instructions/classify-answer.md` (`stack.toml`'s `keel_cloud`), with
  `Classification.validated()`'s rules restated in `norm_out` **including 136 FR-1** (a pick-N item reads the picks
  named, whatever the model flags). It writes `runs/<stamp>-noise-check/`: `results.jsonl` (one row a sample),
  `summary.json`, `noise-check.md` (the tables of the canon page's *rooms* and *controls*, the misses with their
  transcripts) and the **certificate line** (the founder's bar, 2026-10-26): **quiet: closed answers right 100%**;
  **every bed at 20, 10 and 5 dB: closed answers right > 90%**; confident-wrong ≤ 2% and stories' meaning kept ≥ 90%
  in each of those cells -- **PASS** or **FAIL** with the first failing cell named; the café at 0 dB (and every 0 dB cell) reported in the same tables, outside the bar. A row in the gallery's
  register as the back-tests have (`make gallery`). `--only <substr>`, `--snrs` and `--limit` as `pipeline.py` has
  them, for a cheap partial run; the whole run is about $2 and twenty minutes.
- **FR-4 Nothing else moves.** The six journeys' scripts, the founder's and the respondent's screens, the corpus,
  the judge, the other paid commands.

## Acceptance

Unit: `tests/test_noise_check.py` scores the canon's `results/stt-none.jsonl` rows through the new `norm_out` and
the certificate rule without a call (the pick-two rows now right; the bar PASS on the rows with 136's read, FAIL
when the read is switched off, the failing cell named `clean` -- the quiet room's one partial-pick miss breaks the
100%); the harness's `__say` restatement proven against
keel-web's fixture text (the existing fixture-parity test, extended). `make unit` green. The six remote journeys green
on staging once keel-cloud 136 + keel-web 115 are deployed there. One `make noise-check` on the founder's word, its
certificate PASS, the run folder and the register row kept.
