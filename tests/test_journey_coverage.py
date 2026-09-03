"""The canon's ledger, enforced (CANON.md §4): every journey moment is either proven by named
scenarios whose files cite it, or carries an explicit waiver. A moment that is neither fails
here — visible debt only, never silent debt.

Reads keel-cloud's CANON.md via the configured sibling path (the referee floats at HEAD by
design, CANON.md §2), so a ledger edit and a scenario edit are checked against each other on
every stackless run.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from stack.config import load_config

CANON = Path(load_config().keel_cloud) / "canon" / "CANON.md"

ROW = re.compile(r"^\|\s*(§\d+\.\d+)\s*\|.*\|\s*([^|]+?)\s*\|$")
SCENARIO_ID = re.compile(r"S-(\d{3})")


def _ledger() -> list[tuple[str, str]]:
    rows = []
    for line in CANON.read_text().splitlines():
        m = ROW.match(line)
        if m and not m.group(2).startswith("Proven"):
            rows.append((m.group(1), m.group(2)))
    return rows


def _scenario_file(number: str) -> Path:
    matches = sorted(Path("evals").glob(f"test_s{number}_*.py"))
    assert len(matches) == 1, f"expected exactly one evals/test_s{number}_*.py, found {matches}"
    return matches[0]


def test_the_ledger_parses_and_covers_both_journeys() -> None:
    rows = _ledger()
    moments = [m for m, _ in rows]
    assert len(rows) >= 15, f"ledger unexpectedly small: {moments}"
    assert "§1.4" in moments and "§2.4" in moments


@pytest.mark.parametrize("moment,proven", _ledger(), ids=lambda v: v if isinstance(v, str) and v.startswith("§") else "")
def test_every_moment_is_proven_or_visibly_waived(moment: str, proven: str) -> None:
    if proven.upper().startswith("WAIVED"):
        waivers = CANON.read_text().split("## 5. Waivers", 1)[1]
        assert f"**{moment}**" in waivers, (
            f"{moment} is marked waived in the ledger but has no entry in CANON.md §5 — "
            "a waiver without a reason is silent debt")
        return
    numbers = SCENARIO_ID.findall(proven)
    assert numbers, f"{moment} names no scenarios and no waiver: {proven!r}"
    for number in numbers:
        scenario = _scenario_file(number)
        assert moment in scenario.read_text(), (
            f"{scenario} is listed as proving {moment} but never cites it — add the §-citation "
            "next to the assertion that enforces the moment, or fix the ledger")
