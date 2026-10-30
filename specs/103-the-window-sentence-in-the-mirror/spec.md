# Spec 103 -- The harness reads the window as its own sentence

keel-cloud 168 (merged 2026-10-30, cloud master `9ba42382`): `ReadBack` no longer appends *", counting the last
{window}."* to the context read-back; the sentence ends at the job and a third sentence follows: *"…they want to
{job}. We'll ask about the last {window}."* With no window (none stored, or money alone under keel-cloud 135) the two
sentences stand as before, byte for byte. `RecallWindow.words()` already returns *"the last 5 working days"*. Nothing
on the wire or in the corpus moved; the web's muted line *Counting the last {window}.* under the card is unchanged
until keel-web 147 drops it (a separate spec; its pins move with it, not here).

## Rules

- **FR-1 The mirror.** `harness/vectors_script.py` (`read_back`, ~:473): `out + "." + (f" We'll ask about the last
  {window_words(window)}." if window else "")`; the docstring (~:460-466) describes the new shape.
- **FR-2 The pins, re-pinned with why** (168's tasks.md lists them): `tests/test_read_back_mirror_085.py` (:29, :63,
  :71, :82, :199), `tests/test_drawn_screener_seams_077.py` (:66-67, :103, :106), `tests/test_vectors_journey.py`
  (:626-630 07-mulchrun, :633 01-countly), `tests/test_drifts_95_97_closed.py:154` and `tests/test_study_scopes.py:167`
  (`.endswith(". We'll ask about the last 4 weeks.")`).
- **FR-3 The money-alone check.** `evals/corpus_scenario.py:339`: `"counting the last" not in drawn.lower()` would pass
  without testing anything; it becomes `"we'll ask about" not in drawn.lower()`; the prose at :385 and `AGENTS.md:505`
  say the new shape.
- **FR-4 Not here.** `evals/corpus_scenario.py:677` (*Counting the last {window}.*, the web's muted line) and
  `tests/test_drifts_95_97_closed.py:134` move with keel-web 147. History stays: old specs, `runs/DRIFT.md`, `quality/`
  scores, the gallery fixtures.
- **FR-5 Fresh projects.** A project confirmed before 168 keeps the old sentence in its stored `understands`; the
  quality walk and every journey make fresh projects, so nothing is owed, and tasks.md says so.

## Acceptance

`make unit` ZERO failed (master's counts as 102's tasks.md records them, 4,076 passed / 53 skipped). The paid walk is the
coordinator's, on the founder's word. Build now; one builder at a time.
