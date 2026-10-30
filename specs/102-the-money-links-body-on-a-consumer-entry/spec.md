# Spec 102 -- On a consumer entry's money study the person's body is answers alone

The re-walk of 2026-10-30 (`quality/cycles/20261030-35dfb74.md`) stopped once: 13-aircaps · COMMERCIAL at Harriet Coleman,
*the page sent exactly this person's answers*. The page sent `{answers, followUps, pilotOptIn}`; the harness expected
`{recency: true, story, answers}` -- the gate's shape. Money alone serves no gate (keel-cloud 133 FR-4, spec 101 FR-1:
the FULL link opens with the idea card, then part 3), so nobody is asked *Yes, I recall* and nobody types a story; the
page's body is right and the expectation is wrong. The four money studies that passed are B2B entries, whose
decision-makers' link (`LINK_B2B`) already sends `{answers}` alone (`PersonInputs.response`,
`harness/vectors_script.py:1741`); 13-aircaps is the walked set's one consumer entry, where every one of the 20 people is
on the FULL link (spec 101 FR-2, `study_people`) and every one of them carries the gate's shape in the expected body.
Twelve of the 28 back-test entries are consumer entries; every one of their money studies stops the same way today.

## Rules

- **FR-1 The body.** `PersonInputs.response` (`harness/vectors_script.py`) is handed whether the study serves the gate
  (`serves_gate(entry)`, threaded from `person_inputs` or passed by the caller in `evals/corpus_scenario.py` -- the
  builder picks, tasks.md says which). Where the gate is not served and the link is not `LINK_B2B`: an inside person's
  body is `{"answers": answers}` -- no `recency`, no `story`, no `anchorChip` (the file's story and chip are the gate's,
  which this study never asks; `read_owed` already says no reading is owed). The B2B body and every gated study's body
  are unchanged, pinned by the existing tests.
- **FR-2 No gate, no No.** Where the gate is not served, the walk's gate-No path (`evals/corpus_scenario.py:2900`,
  `if person.link != LINK_B2B and not person.recency`) and its chip-ends-at-the-gate path (`ends_on_chip`) are not taken;
  `walks_rungs` is true for every inside person on the link (the follow-ups are asked as on the B2B link). A file person
  with `recency: false` on a gateless study has no answers to give and is refused by name (`VectorsScriptError`) -- the
  corpus has none today, and the refusal says what a revision would have to record.
- **FR-3 No story, no seam.** `_speak_for` returns None where the gate is not served (no story box exists to speak
  into); `_hold_the_box` is not run; the STORY_SPOKEN table is untouched.
- **FR-4 Outside the segment.** An outside person on a gateless study cannot be screened until keel-cloud 166 /
  keel-web 145 land (spec 100 owns the walk then); until then such a person is not walked and is named in one finding
  (`<name>: outside the segment; the money link asks no screener yet (keel-cloud 166 / keel-web 145, spec 100)`), never
  passed over in silence. The five walked entries have none; 11-issen has one.
- **FR-5 Tests.** `tests/test_money_links_body_102.py`: the body on FULL without the gate (answers alone, story and chip
  dropped), on FULL with the gate (as today), on `LINK_B2B` (as today); 13-aircaps under COMMERCIAL yields 20 bodies with
  no `recency` key; `_speak_for` None off the gate; the `recency: false` refusal; FR-4's finding. Nothing else moves:
  `make unit` green with ZERO failed (master's counts as spec 101's tasks.md records them, 4,048 passed / 53 skipped,
  plus the new tests).

## Acceptance

`make unit` ZERO failed. The paid check -- `make quality-walk ENTRIES=13-aircaps SCOPES=COMMERCIAL DOOR=host WHY=…` --
is the coordinator's to run on the founder's word, never the builder's (it spends Keel's AI). Build now (the founder,
2026-10-30: *let the walk complete.. then lets proceed with the fix*); one builder at a time.
