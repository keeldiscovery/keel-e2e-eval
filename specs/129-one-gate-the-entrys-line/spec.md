# Spec 129 -- One gate: the entry's line

Spec 106 FR-3 holds a cycle's score_pct to the gallery's last accepted one (so a worse build never refreshes the
gallery). Spec 127 added the entry's line and kept 106's gate "on the founder's word". On 2026-11-02 the founder set the
rule for every round -- *"if it passes 80 threshold, promote it to staging"* -- and the same morning Code Four's one-entry
record (84.8%) became the gallery's last accepted, so the next fourteen-cycle would be refused at 84.5% though every entry
clears 80. Two gates, one of them stricter than the founder's rule and moved by the shape of a record, not by quality.

## Rules

- **FR-1** `make quality-accept` admits each entry on the entry's line alone (127 FR-1). The cycle-level gate of 106
  FR-3 is retired: the provenance still records the cycle's score_pct and the gallery's history, and `promote` says
  the cycle's score against the last accepted as information (*84.5% against 84.8% last time*), never as a refusal.
- **FR-2** A record of fewer entries than the gallery holds (Code Four alone) never sets a bar for the next; the
  provenance's `accepted.score_pct` is kept for the record, `last_accepted` is informational.
- **FR-3** `quality/CYCLE.md`, `AGENTS.md`, the Makefile comments and the 106/127 tests re-pinned: the tests of the
  cycle gate become tests of the information line. `make unit` green.

## Acceptance

The next accept of a fourteen-cycle at any overall score admits the entries at or above 80 and refuses the rest by name.
