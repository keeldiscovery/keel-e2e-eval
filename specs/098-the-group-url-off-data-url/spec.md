# Spec 098 -- The harness reads the group's URL off the section's `data-url`

keel-web 142 (the founder, 2026-10-30) stops drawing the shortened link (`data-testid="group-link"`) under a group's
name on the Sent tab; the URL stays on the section's root as `data-url`. `harness/interviews_screens.py` reads the
section's URL off `GROUP_LINK`'s title today (`:162`, the S-017 leg's `section["url"]`, `evals/open_link_leg.py:532`).

## Rules

- **FR-1** `interviews_screens` reads the URL off `[data-group]`'s `data-url`; `GROUP_LINK` is retired and no
  assertion expects a shortened link in the section; the Send-more popup's *Link made* read (`GROUP_LINK_MADE`) is
  unchanged.
- **FR-2** Nothing else moves: the open-link leg's arrival, sign-in, answered and inactive reads; the marks.

## Acceptance

`make unit` green with ZERO failed; `make eval K=s017` green on the playground stack at keel-web 142. Build on the
founder's word of 2026-10-30, after 142 merges and after 097.
