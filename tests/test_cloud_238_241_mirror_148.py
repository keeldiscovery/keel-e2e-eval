"""Spec 148 -- the harness mirrors round A: keel-cloud 238 to 241 (keel-cloud-docs master `155eaca9`) and keel-web 183
(master `36d069ed`).

- FR-1 the digest: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at
  `RespondentReview.CARDS_SHA256` (238: Prevalence §2; 239: Existing sacrifice §2, §6; 241: Ability to pay §2, §5, §6),
  the pin chain moved through 238's and 239's digests.

No stack, no model, no key: the cloud's and the web's files are read where the checkouts are there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
PROJECT = "src/main/java/com/keeldiscovery/cloud/domain/project/"
CARDS = "src/main/resources/keel/dimension-cards.md"
#: keel-cloud 238 (`5222bd06`, merged): Prevalence §2, one bullet (was `42fa94dd...`, 237).
CARDS_SHA256_238 = "d764f34fd23127c001ac61f1cfddbedc1adf7ce9ec520144765161cfceaa81d2"
#: keel-cloud 239 (`1260f4fe`; 240 moved no card): Existing sacrifice §2, §6.
CARDS_SHA256_239 = "94f9edc648dd57e76df30d788e7fff86f8cf5fc1ef7f785e36d71574eaf809a7"
#: keel-cloud 241 (`155eaca9`, the round's final sha): Ability to pay §2, §5, §6.
CARDS_SHA256_241 = "78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no {rel} at {KEEL_WEB}")
    return path.read_text(encoding="utf-8")


def _cards() -> str:
    return " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())


# ------------------------------------------------------------------------------------------- FR-1 the digest

def test_the_reader_digest_is_241s_cards():
    """FR-1: the reader's cards are the cloud's vendored copy byte for byte, at 241's digest (`CARDS_SHA256_141`, the one
    constant the earlier pins read, moved in place); 238's and 239's the steps between, each its own."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    from tests.test_cloud_236_237_mirror_147 import CARDS_SHA256_237   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_241 == CARDS_SHA256_141
    assert (KEEL_CLOUD / CARDS).read_bytes() == ours
    assert len({CARDS_SHA256_237, CARDS_SHA256_238, CARDS_SHA256_239, CARDS_SHA256_241}) == 4


def test_prevalence_reads_the_act_that_hurts_against_the_segment():
    """FR-1 (238 FR-6): Prevalence §2's new bullet -- E7 against the segment, the hurt's kind and a new word; E9 names its
    No by a word of the hurt; E8's two verdicts and its blame."""
    text = _cards()
    assert "**The act that hurts, read against the segment (keel-cloud 238).**" in text
    assert "*less than it could* and *more than it should* as verdicts" in text
    assert "*let*, *allowed* or *failed to* at the head as blame" in text
    assert "(*had the call ring out*), never as their choice (*let the call ring out*)" in text


def test_existing_sacrifice_names_the_thing_they_see_go():
    """FR-1 (239 FR-6): Existing sacrifice §2 -- the base the line's, the unit kept, no neutral verb; §6 the pitfall."""
    text = _cards()
    assert "Never *lose*, *lost*, *miss*, *go without* or *fell through*" in text
    assert "*unanswered*: *did not get answered*; *lost track of*: *did you not keep track of*" in text
    assert "the typed *per {unit}* kept in the question and the label on the decision-maker's link, said once" in text
    assert "on a money-only study by its part-3 job; two repair turns" in text
    assert "never *go without* or *fell through* where the writer can say it" not in text


def test_ability_to_pay_labels_fit_every_organisation_on_the_card():
    """FR-1 (241 FR-2): Ability to pay §2, §5, §6 -- the two labels as served; no unit of one kind of organisation."""
    text = _cards()
    assert "`charged_to_users` *Charged back to whoever uses it*" in text
    assert "`outside_funding` *New money from outside, such as a grant*" in text
    assert "**Each source holds in any organisation** (keel-cloud 241)" in text
    assert "`charged_to_users` *Charged to the teams" not in text and "· A grant or outside funding ·" not in text
    assert "*A grant or outside funding* blurred with a grant already in an existing line" in text
