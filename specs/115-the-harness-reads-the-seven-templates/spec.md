# Spec 115 -- The harness reads keel-cloud 174: the seven template and frame rules

keel-cloud 174 (merged 2026-10-31; its tasks.md lists every pin): commitment's belief names the decider where someone
else decides (`belief_template_decider`); purchase friction's belief *{value} can slow or stop the purchase.*, its escape
`cant_tell`; compatibility's *For most {actor_plural}, {value}.*, a fact condition on the registry's four, the fact said
back *You said only with help or approval: {fact}.*; importance's two-sentence belief with the writer's `stretch`
(server-side; the stranger's anchor *Think of your last {stretch}*; *when {circumstance}* where no stretch is usable);
frequency's unit never dropped (*… did that happen?* with the unit kept), the founder's frame *a typical {actor}*, *Say a
number from 1 to N* above five, the two-word unit said once; price's `offer_name` as typed (W8 cap 8 words); the follow-up
*What would have to happen for that to be true?*

## Rules

- **FR-1 The slice and the mirrors.** `tests/fixtures/registry/slice.yaml` :61, :126, :212, :593, :607 (`cant_tell`), :645
  (`belief_template_decider`); `instructions/corpus.py:26-28`; `instructions/marks.py:152-154`; `evals/scope_journey.py:80`;
  `evals/corpus_scenario.py:2111-2112`; `instructions/spoken.py:80, :139` (`FACT_ANSWERS` = the registry's four), `:245`;
  `instructions/wording.py:213`.
- **FR-2 Frequency.** `harness/vectors_script.py:311-315` (`frequency_served`: on/in by unit, the short unit), `:3132-3142`
  (`frequency_held`'s unit-dropped step goes; *did that happen?* keeps the unit), `:2608` (the fact said back);
  `tests/test_instruction_spoken.py:168`, `tests/test_controls_089.py:113` (*Say a number from 1 to N.*);
  `tests/test_after_131.py:383`.
- **FR-3 The follow-up.** A mirror of the *Only if* line where the harness reads it (none today; add one beside the ladder
  so 174's words are pinned once).
- **FR-4 The gallery fixtures** stay until re-recorded after the screens; a test reads them in their recorded frame.
- **FR-5 Tests.** `tests/test_seven_templates_115.py`; `make unit` ZERO failed (master's counts as 114's tasks.md records
  them).

## Acceptance

`make unit` ZERO failed. Build right after 114, before 109: cycle 4 reads these templates. One builder at a time in this
repo.
