"""S-017: one open link for a group -- three strangers sign in with Google (spec 092; keel-cloud 162, contract 48;
keel-web 136).

01-countly's founder locks the study on the scripted runtime, stands on Keel's door with a fresh grant and records the
interviewer (the fake renderer), makes one *Let them choose* link for a group from Send more, and four strangers
registered on the local stub issuer meet it: A signs in through the browser, begins, answers and opts in to the pilot;
B signs in, begins and stops after the gate; C signs in on the wire and never begins; A again is served ALREADY_ANSWERED
and B again resumes where they stopped; Sent's By group tab draws the group and its three rows with their emails; the
link closed serves D the inactive line and reopened serves the card; the ledger carries exactly two INTERVIEW rows; the
Pilot view carries A's email. The whole walk is `evals/open_link_leg.py`'s. Deterministic (the scripted executor and the
stack's fakes), never live, and local only: the remote profile refuses it by name.
"""

from __future__ import annotations

import pytest

from evals import open_link_leg


def test_s017_open_link(stack, founder_one, browser, run_dir):
    refused = open_link_leg.refusal(stack)
    if refused:
        pytest.skip(refused)
    open_link_leg.run(stack, founder_one, browser, run_dir)
