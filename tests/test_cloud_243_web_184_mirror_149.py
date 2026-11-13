"""Spec 149 -- the harness mirrors keel-cloud 243 (keel-cloud-docs master `c87d1066`) and keel-web 184 (master
`82a746d9`).

- FR-1 the digest and the contract: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte
  at `RespondentReview.CARDS_SHA256` (243: Importance §2, Relative advantage §2, Compatibility §2), the pin chain moved
  from 241's `78bd1167...`; `x-keel-contract` 64 (the walk's `REVIEW_CONTRACT`), the screen contract 25 unchanged.

No stack, no model, no key: the cloud's and the web's files are read where the checkouts are there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
CARDS = "src/main/resources/keel/dimension-cards.md"
#: keel-cloud 243 (merged at keel-cloud-docs `c87d1066`): Importance §2, Relative advantage §2, Compatibility §2 -- a
#: row in place of each row put aside (was `78bd1167...`, 241).
CARDS_SHA256_243 = "94fd69c097176c877571e300312eb2d380788fbcc0a9358fe31d1881b86b6be5"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


def _cards() -> str:
    return " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())


# ------------------------------------------------------------------------------------------- FR-1 the digest

def test_the_reader_digest_is_243s_cards():
    """FR-1: the reader's cards are the cloud's vendored copy byte for byte, at 243's digest (`CARDS_SHA256_141`, the one
    constant the earlier pins read, moved in place); 241's the step before it, its own."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    from tests.test_cloud_238_241_mirror_148 import CARDS_SHA256_241   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    # eval spec 154 moved the copy to keel-cloud 245's (`CARDS_SHA256_141`); 243's is the step before
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_141
    assert sha in (CARDS_SHA256_243, CARDS_SHA256_141)
    assert (KEEL_CLOUD / CARDS).read_bytes() == ours
    assert CARDS_SHA256_241 == "78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307" != CARDS_SHA256_243


def test_importance_suggests_a_row_in_place_of_each_put_aside():
    """FR-1 (243 FR-5): Importance §2 -- Keel adds none but a row in place of one the review puts aside; the rows handed
    numbered from 0; the Check's pattern and the band counting both."""
    text = _cards()
    assert "Keel adds none but a row in place of one the review puts aside** (keel-cloud 243)" in text
    assert "**In place of each row put aside, Keel suggests one** (keel-cloud 243)" in text
    assert "The rows are handed to the review numbered from 0, the own row 0." in text
    assert ("*Keel put three rows aside and suggested three in their place, so every row sits at the moment your "
            "problem names.*") in text


def test_relative_advantage_and_compatibility_suggest_in_place():
    """FR-1 (243 FR-5): Relative advantage §2 and Compatibility §2 -- a benefit / a condition in place of each put aside;
    the record names whose row each entry was."""
    text = _cards()
    assert "**In place of each benefit put aside, Keel suggests one** (keel-cloud 243)" in text
    assert ("*Keel put one benefit aside and suggested one in its place, so what is left is what only your idea would "
            "have given them.*") in text
    assert "**A condition in place of each put aside** (keel-cloud 243)" in text
    assert "The record says whose row each entry was (*yours* or *Keel's draft*)." in text


# ------------------------------------------------------------------------------------------- FR-1 the contract

def test_the_contract_is_64_and_the_screen_contract_25():
    """FR-1 (243 FR-4): `x-keel-contract` 64 names `inPlaceOf`, `typedKeels`, `replacedBy` and `keels`; the walk's
    `REVIEW_CONTRACT` reads 64 or a later one that keeps them (keel-cloud 244 moved it to 65); `ScreenResponseContracts.CONTRACT_VERSION` stays 25 (the per-note `suggest` is optional
    and no screen's)."""
    spec = _cloud("canon/openapi-v2.yaml")
    assert int(re.search(r"x-keel-contract: (\d+)", spec).group(1)) == vs_screens.REVIEW_CONTRACT >= 64
    for name in ("inPlaceOf", "typedKeels", "replacedBy", "keels"):
        assert re.search(rf"\b{name}: \{{ type: (string|boolean), description: \"Spec 243", spec), name
    contracts = _cloud(APPLICATION + "ScreenResponseContracts.java")
    # keel-cloud 245 moved it to 26 (the draft serves no `asked`, each row its `question`; spec 154)
    assert re.search(r"public static final int CONTRACT_VERSION = (25|26);", contracts)
