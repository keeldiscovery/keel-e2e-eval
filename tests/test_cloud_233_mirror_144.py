"""Spec 144 -- the walk waits for the review and shoots the Check after the band (keel-cloud 233 at keel-cloud-docs
master `9e4b7fda`, keel-web 180).

- FR-4 the mirrors: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at 233's
  `CARDS_SHA256` (Compatibility §2: the review may change a condition, a settled row put aside); the contract pin 62 ->
  63 (`AnsweredRows.review`, `ReviewDto`; Compatibility's list saved without `pickedIndex`; `SavedListDto` as 232 left
  it).

No stack, no model, no key: the cloud's files are read where the checkout is there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from quality import cards
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
FOUNDER = "src/main/java/com/keeldiscovery/cloud/protocol/founder/"
#: keel-cloud 233 FR-5: `RespondentReview.CARDS_SHA256` at keel-cloud-docs `9e4b7fda` (was `2f4f0bf8...`, 232).
CARDS_SHA256_233 = "98b7379b8fe68d9ef3c393045804b7837ae759c28e061ed8c812bbb2500b1c7b"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------- FR-4 the cards

def test_the_reader_digest_is_233s_cards():
    """FR-4: the reader's cards are the cloud's vendored copy byte for byte, at 233's digest (the one constant the
    earlier pins read, `CARDS_SHA256_141`, moved with it)."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_233 == CARDS_SHA256_141
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours


def test_compatibility_says_the_review_may_change_a_condition():
    """FR-4 (233 FR-5): Compatibility §2 -- the review may change a condition that breaks the card, the permission
    example, the founder's words behind Put back, a settled row put aside (the note stands with the review off)."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "**The review may change a condition that breaks this card** (keel-cloud 233, the review switch on)" in text
    assert ("*could forward unanswered calls to another number* -> *was allowed to have unanswered calls forwarded to "
            "another number*") in text
    assert "**A settled row is put aside, not noted:**" in text
    assert text.count("behind **Put back**") == 4, "Importance, Current solution (232); Compatibility twice (233)"
    assert "**The settled note:**" not in text


# ------------------------------------------------------------------------------------------ FR-4 contract 63

def test_the_contract_is_63():
    """FR-4 (233 FR-6): `x-keel-contract` 63 -- the walk's hold reads it (`REVIEW_CONTRACT`)."""
    spec = _cloud("canon/openapi-v2.yaml")
    assert int(re.search(r"x-keel-contract: (\d+)", spec).group(1)) == vs_screens.REVIEW_CONTRACT == 63


def test_the_save_answer_names_its_review():
    """FR-4 (233 FR-1): `PUT calibration/{vector}` answers `AnsweredRows(revision, rows, review)`, `review` a
    `ReviewDto(interactionId)` absent where none started; the openapi says so on the answer."""
    dtos = _cloud(FOUNDER + "VectorDtos.java")
    assert "record AnsweredRows(long revision, List<BeliefRowDto> rows, ReviewDto review)" in dtos
    assert "record ReviewDto(String interactionId)" in dtos
    spec = _cloud("canon/openapi-v2.yaml")
    review = spec.split("                  review:\n", 1)[1].split('"409"', 1)[0]
    assert "required: [interactionId]" in review and "interactionId: { type: string, format: uuid }" in review
    assert vs_screens.review_of_answer({"revision": 12, "rows": [],
                                        "review": {"interactionId": "6f0c6c0e-46b2-4c39-9c39-7d3c1c3c0a11"}}) == \
        "6f0c6c0e-46b2-4c39-9c39-7d3c1c3c0a11"
    assert vs_screens.review_of_answer({"revision": 12, "rows": []}) is None
    assert vs_screens.review_of_answer(None) is None and vs_screens.review_of_answer("x") is None


def test_compatibilitys_list_saves_without_a_pick_and_savedlist_is_232s():
    """FR-4 (233 FR-2): Compatibility's Check saves the list with no `pickedIndex` (the pick pending; Choose posts it on
    the rows as served; a pick on a put-aside row 422); `SavedListDto` is 232's record, unchanged (the pin of
    `test_cloud_219_228_mirror_141` reads the same signature)."""
    spec = _cloud("canon/openapi-v2.yaml")
    picked = next(line for line in spec.splitlines() if line.strip().startswith("pickedIndex:"))
    assert "Spec 233 (FR-2, contract 63): except Compatibility's -- the Check's Save carries none" in picked
    assert "A pick naming a row the review put aside" in picked and "422 VALUE_OUT_OF_SHAPE" in picked
    dtos = _cloud(FOUNDER + "VectorDtos.java")
    assert ("record SavedListDto(List<SavedItemDto> items, Integer pickedIndex, String phrase, Integer line,\n"
            "            DurationDto duration, Integer lineAfter, List<PutAsideDto> putAside, ChangedDto changed)") in dtos
    assert vs_screens.REVIEWED_LISTS == ("problem.importance", "problem.current_solution_satisfaction",
                                         "solution.compatibility")
