# Spec 127 -- The gallery admits an entry on its mean (the acceptance gate loosened)

The founder, 2026-11-01 evening, on `make quality-accept`'s gate: *"I'm thinking we can loosen it up. If it's above 84%,
we can accept it."* Asked whether every study or the entry: *"Let it be the entry mean rather than a single project."*
Today (spec 106 FR-3) a study with one flagged screen is refused by name and an entry lacking a study is set aside, so no
cycle has refreshed the homepage examples (the gallery still dates from 2026-10-24). Builds on 126.

- **FR-1 The entry's line.** `quality/cycle.toml` `[gallery]` gains `entry_mean_pct = 84.0` (committed, with its why).
  In `make quality-accept` (and `make gallery --scores`), an entry is an example when it has all three studies in the
  cycle and the **mean of their three `score_pct`** (each study's latest score file at the current `RUBRIC_VERSION`,
  matched by bundle as today) is **at or above the line**. A flagged screen no longer refuses a study; a study with no
  score file still does (the readers did not see it). An entry below the line is refused by name with its mean and the
  line (*10-palus 82.2 < 84.0*), and keeps whatever the gallery holds for it (an older example stays; a slug with none
  stays absent).
- **FR-2 The flagged screens travel.** The gallery's provenance records, per accepted entry, each study's `score_pct`,
  the entry's mean, and the flagged screens by `{study, screen, criterion}` so they are still seen; the acceptance's
  summary line says *N entries accepted on a mean of at least 84.0, M refused (names and means)*.
- **FR-3 The cycle-level gate stands.** The cycle's overall `score_pct` is still held to the gallery's last accepted one
  (spec 106 FR-3's "never below what we already have"); the baseline cut is unchanged. The line is the gallery's alone;
  `[bar]` (90%) and the weak rule are untouched.
- **FR-4** `make unit` green (`set -o pipefail`); tests for the line (at, above, below; a flagged screen admitted; a
  missing score file refused; the provenance's new keys; the summary line).

## Acceptance

`make unit` ZERO failed. `make quality-accept CYCLE=quality/cycles/20261102-7021fd5.md` admits every entry of cycle 7
whose mean is at or above 84.0 and names the rest; keel-web's `public/sample` is refreshed for those and committed there.


## Amendment 2026-11-02 -- the line is 80

The founder, 2026-11-02 morning, after cycle 8 (the fourteen on keel-cloud `1ce203f`, every entry between 80.8 and 86.4): *"let's keep the mean as 80 instead of 84, because ... the new one is better than what we have ... if it passes 80 threshold, promote it to staging."* `[gallery] entry_mean_pct = 80.0`; FR-1's rule is otherwise unchanged; the tests that pin the committed line are re-pinned (`test_gallery_127.py`); the tests that exercise the mechanism at an explicit `line=84.0` keep that fixture value. The round rule from here: walk, advise, defects fixed, improvements shown, entries at or above the line accepted, staging deployed; production on the founder's word.
