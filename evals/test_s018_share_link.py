"""S-018: the Overview shared by a link (spec 130 FR-1 (a), FR-3; keel-cloud 201, contract 58; keel-web 163).

A fresh owner's money-alone study at its answers (S-016's walk), then: FR-3's pager (six own projects, *Page 1 of 2*),
the link switched on from the Share sheet, a stranger with no sign-in reading the Overview, Insights, Pilot, the stage
page and the brief under `/s/{token}` with the brand row *{Project} (shared by {firstName}) · {market}* and never
Interviews or a write, the link switched off (*This link is no longer shared.*, the bare 404) and rotated (the old token
dead). The leg is `evals/sharing_leg.link`. On staging: `make remote K=s018` (the coordinator's; never the builder's).
"""

from __future__ import annotations

import pytest

from evals import sharing_leg

pytestmark = pytest.mark.remote


def test_s018_share_link(stack, founder_one, browser, run_dir):
    sharing_leg.run_link(stack, founder_one, browser, run_dir)
