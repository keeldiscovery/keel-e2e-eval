# Spec 106 -- The gallery holds three studies per example, each from its own walk, with seven people

The founder, 2026-10-30: *"when you run cycle 4, we want to rebuild the examples on our homepage … reduce it to three
toggles -- problem, solution and commercial -- so the output of each can be printed there; and instead of twenty, seven
agents answer it."* Today `make gallery` (spec 063, 079 FR-6) keeps **one run per entry** (`--scope-order`), the index row
carries one `scope`, keel-web's four study pills (spec 110 / 121: problem, solution, solution-money, money) filter that
one run by vector, and the exporter refuses a run that did not invite twenty people (*the disclaimer says twenty*,
`evals/gallery.py:615`). A cycle walks three studies per entry (`quality/cycle.toml` scopes PROBLEM, SOLUTION, COMMERCIAL).

## Rules

- **FR-1 Three studies per example.** `evals/gallery.py` exports, for each entry, every walked scope of the chosen cycle:
  `OUT/<slug>/<study>/…` for `problem`, `solution`, `money` (the 060 file set, `interview.json`, `manifest.json` each),
  and the index row carries `studies: {problem, solution, money}` with each study's own `decision`, `howSure`, `pilot`,
  `price`, `answered` and `invited`; the row's top-level fields are the problem study's as today, so an old reader still
  works. `--scope-order` and `one_per_entry` retire; a cycle whose entry lacks one of the three studies is refused by
  name (nothing written for that entry), never a partial example.
- **FR-2 Seven people.** The walk sends **seven** people per study by default (`quality/cycle.toml` `people = 7`; `make
  quality-walk PEOPLE=`): on the FULL link the corpus's first seven eligible people in corpus order (spec 101's
  `study_people` narrowed), on a B2B money study its deciders (seven today). The exporter's check reads the study's own
  `invited` (`gallery.py:517`) and the disclaimer says the number in words (*seven people answered, all simulated*),
  never a fixed *twenty*; `instructions/gallery_names.toml`'s disclaimer text moves. The quality readers score the
  screens, not the count; the brief's lines read whatever n the study has.
- **FR-3 The gate is the gallery's own last score, not 90 (the founder, 2026-10-30: *"we don't have to wait till 90 … the
  only time we should not do it is if the next rating comes below what we already have; that acts as a gate for us not
  to promote that instruction"*).** `make quality-accept` cuts the accepted cycle as the baseline (the cycle machinery's
  baseline, spec 079) and records its score_pct in the gallery's provenance. The next export is refused by name when the
  new cycle's overall score_pct is **below the baseline's**; equal or above passes, whatever the 90% bar says. With no
  baseline yet (today) the first accepted cycle passes. `--scores` also keeps the **flagged-screen** refusal (a screen
  the reader marked out of place or leaking is never published). `--bar <pct>` stays as an optional stricter gate, off
  by default. The cycle's own 90% bar (quality/cycle.toml) is untouched: it measures the product, not the gallery.
- **FR-4 Provenance and privacy as today**: one provenance file outside OUT naming cycle, entry, study and run per slug;
  no entry id or run name under OUT; *Simulated* and *inspiredBy* on every row and manifest.
- **FR-5 Tests.** `tests/test_gallery_106.py`: three studies exported from one cycle's bundles (fixtures), the index row's
  `studies`, the refusal on a missing study, the seven-people walk (`study_people` narrowed, deciders untouched), the
  disclaimer's number, `--bar`. `make unit` ZERO failed.

## Acceptance

`make unit` ZERO failed. Then, on the founder's word (paid): cycle 4 on Keel's door with `people = 7`, `make
quality-accept` (gallery from that cycle's bundles into keel-web's `public/sample/`), keel-web 151 drawing it. Build
after 105; one builder at a time.
