# Spec 120 -- The referee reads the Insights view's second-stem group and the served count line

The matrix's s012 (2026-11-01, keel-cloud `e65afec` and `bc17235`, keel-web `2a202d8` and `f02595c`) failed at the
report after four answers: the wire served Commitment one grouped quote, and the page drew no group. The page was right:
keel-web 155 FR-9 (keel-cloud 184 FR-8) draws a quote that answered the line's second stem (`heading` ==
`alsoHeading`) under its own heading (`[data-testid=insights-also]`, `.rp-concern--also`), never in `ol.rp-themes`,
and a group whose quotes all answered it is not drawn; 155 FR-7 draws the served `countLine` in place of the composed
*Only k of the n* footer. The referee's mirror (spec 118 FR-4) read neither. A harness defect, the coordinator's
(2026-11-01, the founder's overnight rule).

- **FR-1** `vectors_screens` captures a box's `also` group (heading, quotes) beside its `themes`.
- **FR-2** `report_marks.expected_box` takes the second stem's quotes out of the groups (a group left empty is not
  expected; a group's count is its remaining quotes when any were taken out), expects them under `also`, and expects
  the served `countLine` when there is one, else the composed footer. The comparison holds the drawn `also` group to it.
- **FR-3** Tests on a Commitment box with one second-stem quote and on a first-stem one. `make unit` ZERO failed.
