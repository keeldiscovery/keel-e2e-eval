# Spec 130 -- Sharing: the journeys

keel-cloud 201 and keel-web 163 (the founder, 2026-11-02; mock https://claude.ai/artifact/DyHX6TG5GBCcUcy1ArpBQy v14).
Contract 58 mirrored.

## Rules

- **FR-1 Three remote journeys on the twin**, each from a fresh owner account with one project at the answers stage:
  (a) the owner switches the link on, copies it, a stranger (no sign-in) opens the Overview, Insights, Pilot, a stage
  page and the brief, cannot open Interviews or any write, the brand row reads *{Project} (shared by {firstName}) ·
  {market}*; the owner switches the link off and the stranger gets 404; (b) the owner names a viewer; the viewer
  signs in, finds the project under *Overviews shared with me*, searches by the owner's name, opens it read-only; the
  owner removes them and the row is gone; (c) the owner names a co-founder; the co-founder signs in, finds it under
  *Projects shared with me*, edits a Check row and sends a link, and the owner's credits balance falls while the
  co-founder's does not; the co-founder has no Share control and 403 on the sharing routes.
- **FR-2 The contract mirror**: `sharing`, the sharing routes, the public route, `sharedProjects` / `sharedOverviews`
  with `sharedBy`, document version 36.
- **FR-3 The pager and the tabs** in the journeys: six own projects page as *Page 1 of 2*; the search narrows the count.
- **FR-4** `make unit` green; the journeys green against staging.
