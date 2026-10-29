"""Spec 088 (keel-cloud 156, contract 45, `InferenceCharge.VERSION` 12): one charge per interview, at Begin.

FR-1, the prices: both fakes at price version 12, the harness's mirror (`harness/interview_charge.py`) held to keel-cloud's
own charge table (skipped by name on a keel-cloud before 156), and §6.3's five-participant figure re-summed wherever the
harness states it."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from harness import contacts_fake
from harness import interview_charge as charge
from harness import interviewer_fake
from stack.config import load_config

CONFIG = load_config(validate=False)
REPO = Path(__file__).resolve().parent.parent
CHARGE_JAVA = "src/main/java/com/keeldiscovery/cloud/domain/connect/InferenceCharge.java"


def _cloud(rel: str) -> str:
    path = CONFIG.keel_cloud / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    return path.read_text(encoding="utf-8")


def _charge_table() -> tuple[int, dict[str, int]]:
    """keel-cloud's `InferenceCharge`: its VERSION and every row's `priceCredits` (the first argument)."""
    text = _cloud(CHARGE_JAVA)
    rows = {m.group(1): int(m.group(2).replace("_", ""))
            for m in re.finditer(r"^\s{4}([A-Z_]+)\s*\(\s*([\d_]+)\s*,", text, re.M)}
    if charge.INTERVIEW not in rows:
        pytest.skip("keel-cloud predates spec 156 (no INTERVIEW row in InferenceCharge)")
    version = re.search(r"public static final int VERSION = (\d+);", text)
    assert version, "InferenceCharge declares no VERSION"
    return int(version.group(1)), rows


# --------------------------------------------------------------------------------------------- FR-1: the prices

def test_both_fakes_carry_price_version_12():
    assert interviewer_fake.PRICE_VERSION == contacts_fake.PRICE_VERSION == charge.PRICE_VERSION == 12


def test_the_mirror_is_keel_clouds_charge_table():
    version, rows = _charge_table()
    assert version == charge.PRICE_VERSION
    assert rows[charge.INTERVIEW] == charge.INTERVIEW_CREDITS == 30
    assert {k: rows[k] for k in charge.READ_PRICES} == charge.READ_PRICES == {"INTERPRET": 0, "THEMES": 0}
    # the founder-side rows 156 left alone, as the two fakes state them
    assert rows["INTERVIEWER_RECORDING"] == rows["INTERVIEWER_CHANGE"] == interviewer_fake.CREDITS
    assert rows["CONTACT_PAGE"] == contacts_fake.PAGE_CREDITS and rows["CONTACT_EMAIL"] == contacts_fake.EMAIL_CREDITS


def test_section_6_3s_five_participants_re_summed():
    assert charge.project_credits(5, version=11) == 1_250             # §6.3's table as written
    assert charge.FIVE_PARTICIPANTS == charge.project_credits(5) == 540 + 105 + 560 + 5 * 30 == 1_355
    assert charge.project_credits(20) == 540 + 105 + 560 + 20 * 30


@pytest.mark.parametrize("rel", ["Makefile", "matrix/cells.toml", "tests/test_matrix_cells.py",
                                 "evals/test_s012_journey_through_a_host.py"])
def test_no_harness_line_states_the_old_five_participant_total(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert "1,250 credits a" not in text and "is 1,250 credits" not in text and "about 1,250" not in text, rel
    assert "$12.50" not in text, rel


@pytest.mark.parametrize("rel", ["Makefile", "matrix/cells.toml", "tests/test_matrix_cells.py"])
def test_the_new_total_is_stated(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert f"{charge.FIVE_PARTICIPANTS:,} credits" in text and "$13.55" in text, rel
