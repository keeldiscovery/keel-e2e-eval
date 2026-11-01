# Spec 122 -- The reader asks again when its answer cannot be read

The nine-entry run (2026-11-01, `quality/cycles/20261101-d096da9.md`, 27 studies to the end) left 35 screens unread --
Careforce's SOLUTION study read 79% of its screens -- every one on a reader answer the harness could not read: *the
answer's object does not parse: Expecting ',' delimiter* (a doubled quote or a stray `"}` inside one `why`), *Extra
data*, or *r2 must be 0, 1 or 2; got None* (a mark left out). The answers are the model's slips, not the screens', and
the harness drops the screen on the first slip. A defect of the harness, the founder's rule (2026-11-01: *"I authorize
you to fix all the defects"*). Builds on 078, 081, 109.

- **FR-1 One more ask.** In `quality/readers.py`'s screen loop (and the flow and Insights loops), when a reader's
  answer raises `RubricError` -- the object does not parse, a mark is missing or out of range, R6 missing or present on
  the wrong audience -- the reader asks **once more**: the same prompt with a tail, *Your previous reply could not be
  read: {error}. Reply again with the one JSON object and nothing else.*, under the label `{label}-again` (recorded under
  `calls/` as every call is). The second answer is read as the first would have been; a second `RubricError` leaves the
  screen unread with both errors in its `error` (*first: …; again: …*). A CLI error (`said["error"]`) is not asked again:
  it is the CLI's, not the model's. The cost of both calls is counted.
- **FR-2 The record says so.** The score file's `calls` already carry every call; the cycle record's head gains a line
  when any screen was read on the second ask: *N screens read on a second ask* (0 → no line), beside the unread count.
- **FR-3 Tests.** With a fake runner: a first answer with a doubled quote and a clean second → the screen is scored and
  `calls` holds two entries, the second labelled `-again`; two bad answers → unread, `error` names both; a clean first
  answer → one call, as today; a CLI error → one call, unread. `make unit` green (`set -o pipefail`).

## Acceptance

`make unit` ZERO failed. The next quality cycle's unread count falls to the screens the model slips on twice.
