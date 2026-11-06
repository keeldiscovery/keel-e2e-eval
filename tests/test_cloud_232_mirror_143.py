"""Spec 143 -- the harness mirrors keel-cloud spec 232 (keel-cloud-docs master `ac81bf6f`).

- FR-4 the mirrors: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at 232's
  `CARDS_SHA256` (Importance §2 and Current solution §2: the review may change a row, Put back); the Palus anchor (232
  FR-7, `ItemFrames.thinkOf`) -- *last* said once where the occasion opens on it -- in `instructions/wording.think_of`
  and the two ScaleFour anchors the harness builds (`instructions/spoken.at_stake`, `hard_case`).

No stack, no model, no key: the cloud's files are read where the checkout is there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from instructions import spoken as spoken_mod
from instructions import wording as wording_mod
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
#: keel-cloud 232 FR-6: `RespondentReview.CARDS_SHA256` at keel-cloud-docs `ac81bf6f` (was `06fcd867...`, 231).
CARDS_SHA256_232 = "2f4f0bf810dc9a5eb75e5af7986fa1a60ba1937e88af8a1923905e95149618f7"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------- FR-4 the cards

def test_the_reader_digest_is_232s_cards():
    """FR-4: the reader's cards are the cloud's vendored copy byte for byte, at 232's digest."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_232 == CARDS_SHA256_141
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours


def test_the_two_amended_sections_say_the_review_may_change_a_row():
    """FR-4 (232 FR-6): Importance §2 and Current solution §2 say the review may change a row that breaks the card, the
    Check says so in one line, the founder's words behind Put back; *never rewritten* / *Never a rewrite* are cut."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "**The review may change such a rival** (keel-cloud 232)" in text
    assert "*Answering group requests that come by email* -> *Taking group enquiries over the phone*" in text
    assert "**The review may change such a rung** (spec 232)" in text
    assert "(*Never called back*, never *simply lost*)" in text
    assert text.count("behind **Put back**") == 2
    assert "The rows are never rewritten" not in text and "Never a rewrite" not in text


# ------------------------------------------------------------------------------------- FR-4 the Palus anchor

@pytest.mark.parametrize("whose,occasion,want", [
    ("your", "last 3 months", "Think of the last 3 months."),
    ("your", "the last 3 months", "Think of the last 3 months."),
    ("your", "Your last site walk", "Think of the last site walk."),
    ("the", "last 5 working days", "Think of the last 5 working days."),
    ("your", "their last shift", "Think of the last shift."),
    ("your", "last 3 months holding raise cash", "Think of the last 3 months holding raise cash."),
    ("your", "daily log", "Think of your last daily log."),
    ("the", "daily log", "Think of the last daily log."),
    ("your", "last-minute booking", "Think of your last last-minute booking."),     # a word that only begins with last
])
def test_think_of_says_last_once(whose, occasion, want):
    """FR-4 (232 FR-7): `ItemFrames.thinkOf`'s cases (`TheAnchorSaysLastOnceTest.theOpenings`), mirrored."""
    assert wording_mod.think_of(whose, occasion) == want


def test_the_mirror_reads_the_clouds_openings():
    """FR-4: the openings are the cloud's (`ItemFrames.LAST_OPENINGS`), in its order."""
    frames = _cloud(VECTORS + "ItemFrames.java")
    found = re.search(r"LAST_OPENINGS = java\.util\.List\.of\(([^)]*)\)", frames)
    assert found, "ItemFrames.LAST_OPENINGS"
    assert tuple(re.findall(r'"([^"]*)"', found.group(1))) == wording_mod.LAST_OPENINGS
    assert '"Think of the last " + noun.substring(opening.length()).strip() + "."' in frames


def test_the_scale_four_anchors_say_last_once():
    """FR-4 (232 FR-7: ScaleFour's two anchors through `thinkOf`): the at-stake and hard-case anchors the harness builds
    say *last* once on a window occasion, and read as before on *daily log*."""
    assert spoken_mod.at_stake("last 3 months", "hold raise cash") == \
        "Think of the last 3 months when you had to hold raise cash."
    assert spoken_mod.at_stake("daily log", "write up the site notes") == \
        "Think of the last daily log when you had to write up the site notes."
    assert spoken_mod.at_stake("time", "hold raise cash") == "Think of the most recent time you had to hold raise cash."
    four = _cloud(VECTORS + "ScaleFour.java")
    assert four.count('ItemFrames.thinkOf("the", noun).replaceAll("\\\\.$", "")') == 2
