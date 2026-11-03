"""S-020: the project shared with a co-founder (spec 130 FR-1 (c); keel-cloud 201 FR-4, FR-5; keel-web 163 FR-6).

S-016's money-alone walk with a co-founder named before the lock: they sign in, find it under *Projects shared with
me* and edit a Check row (saved, then put back); the owner locks and the walk reaches the answers; the co-founder sends
a link and it is begun -- their own credits never move, the credits line they read is the owner's (and on Keel's door
the owner's balance falls by the interview); no Share control, 403 on every sharing route. The leg is
`evals/sharing_leg.CoFounder`. On staging: `make remote K=s020` (the coordinator's; never the builder's).
"""

from __future__ import annotations

import pytest

from evals import sharing_leg

pytestmark = pytest.mark.remote


def test_s020_share_co_founder(stack, founder_one, founder_two, browser, run_dir):
    sharing_leg.run_co_founder(stack, founder_one, founder_two, browser, run_dir)
