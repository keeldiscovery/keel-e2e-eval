"""S-019: the Overview shared with a named viewer (spec 130 FR-1 (b), FR-3; keel-cloud 201; keel-web 163).

A fresh owner's money-alone study at its answers (S-016's walk), then: the owner's own address and a non-email refused
on the sheet, a viewer named; the viewer signs in, finds it under *Overviews shared with me*, the search narrowing the
count by the owner's name, the project's and a name nobody has; opens it read-only (no Share, Interviews greyed, names
out; Interviews, a write and the sharing routes refused); the owner removes them and the row is gone. The leg is
`evals/sharing_leg.viewer`. On staging: `make remote K=s019` (the coordinator's; never the builder's).
"""

from __future__ import annotations

import pytest

from evals import sharing_leg

pytestmark = pytest.mark.remote


def test_s019_share_viewer(stack, founder_one, founder_two, browser, run_dir):
    sharing_leg.run_viewer(stack, founder_one, founder_two, browser, run_dir)
