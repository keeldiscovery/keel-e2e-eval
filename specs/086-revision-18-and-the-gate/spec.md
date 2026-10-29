# Spec 086 -- The harness reads corpus revision 18, the gate without chips, and the follow-ups that name the thing

Three keel-cloud merges of 2026-10-29 move what the harness pins:

- **152** (cloud master `21395ab0`) cut **corpus revision 18**: seven belief templates and the prevalence phrases moved
  (Commitment *Most {actor_plural} would {value} now.*; Current solution *For most {actor_plural}, {value} still falls
  short.*; Importance *Of these {list_size}, {value} is one of the two that {actor_plural} would most like made easier
  when {circumstance}.*; Prevalence *under 2 in 10 ... at least 8 in 10*; Compatibility *For most, {value}.*; Relative
  advantage *For most, it would have {value} on their last {occasion}.*; the drift templates with them; the rate cost's
  belief *The problem already costs the payer about ...: {loss}.*); every golden belief sentence on those rows moved,
  no standing, drift, inside, n or verdict moved; mirrors `corpus-r18/` and `backtest-r17/`; `check_corpus_r18.py` OK
  on 35. This is spec 080's shape (revision 17) one number on.
- **153** (building) takes the two chips off the gate (*I can't recall one particular ...*, *I'd rather not say*): the
  gate serves an empty chips list; the story screens keep theirs.
- **154** (queued) rewrites every follow-up rung to name the thing (`{job}`, `{solution_name}` filled on every
  dimension).

## Rules

- **FR-1 `REVISION = 18`** in `instructions/corpus.py`, the revision-17 note kept and an 18 note (152, the seven
  templates); a file at 17 refused by name.
- **FR-2 Rule D18**, the eval's own diff (`tests/test_corpus_r18.py`, 080's D17 one on): every entry read beside its
  revision-17 record (keel-cloud's `corpus-r17/` and `backtest-r17/`), every leaf difference one of 152's edits -- the
  revision line and header everywhere; on the golden seven the belief sentences and phrases of the moved rows; on the
  eleven back-test entries with a rate cost, that one sentence -- and never a standing. The cloud's checker prints OK on
  35. Rule Q holds.
- **FR-3 The pins.** Every pin that quotes a moved sentence or phrase moves with why: the corpus-overview and
  brief-facts compares, the zero-spend compare, the marks header's seven r18 digests (`MARKS_VERSION` as the ruler
  decides: it did not move unless a mark reads a sentence), `tests/fixtures/corpus/*-r18` if 080 made r17 fixtures,
  the journeys that read a belief line on a founder screen (S-005/006/007/014/015/016 where they do), and the
  quality readers' anchors where a rubric anchor quotes a template (`quality/RUBRIC.md`, `RUBRIC_VERSION` only if an
  anchor moved).
- **FR-4 The gate without chips (153).** `harness/vectors_screens.py`'s `GATE_RATHER_NOT_SAY` and the journeys that press
  a chip on the gate (`person.anchor_chip` on the gate: `browser.py` CANT_RECALL / RATHER_NOT_SAY) press it on the story
  screen instead, where the chips stay; a journey that expects a chip on the gate is re-pinned to expect none, with
  why. The gate's two answers are asserted as the whole of it.
- **FR-5 The follow-ups (154).** Every journey that reads a follow-up heading or text (`{their_picks}` / `{founder_item}`
  / `{their_answer}` / `{condition}` / `{benefit}` / `{band}` lines) is re-pinned to 154's rungs with `{job}` and
  `{solution_name}` filled from the entry; the spoken line too where the AI link is walked.
- **FR-6 Decided before.** `quality/decisions.toml`: D-2026-10-29-05 gains `merged = "21395ab0"`; D-19 gains the 153 and
  154 shas when they merge (the coordinator writes them; this spec's tests read the file's shape only).

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them); `tests/test_corpus_r18.py`
on the cloud checkout at 152's merge or later; then, on the local stack at the cloud sha that carries 153 and 154 and
web master, `make eval K=s005`, `K=s006`, `K=s007` green. Build in two steps if 154 has not merged when this is built:
FR-1 to FR-4 and FR-6 first, FR-5 when 154 lands; tasks.md says which. Build on the founder's word (the decisions of
2026-10-29).
