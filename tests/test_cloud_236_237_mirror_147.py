"""Spec 147 -- the harness mirrors keel-cloud 236 and 237 (keel-cloud-docs master `76620269`) and keel-web 181 (master
`b8682c4f`).

- FR-1 the mirrors: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at
  `RespondentReview.CARDS_SHA256` (236: Compatibility §2; 237: Relative advantage §2, §5, §6); the Compatibility Answer
  hint's pin reads keel-web 181's example; `spoken.advantage_stem` / `vectors_script.benefit_frame_of` know 237's tail
  (*have helped you {job} better, or not?*, frame `"237"`; the at-stake anchor keeps *done that better*, frame `"198"`).

No stack, no model, no key: the cloud's and the web's files are read where the checkouts are there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import spoken as spoken_mod
from quality import cards
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
VECTORS = "src/main/java/com/keeldiscovery/cloud/domain/vectors/"
#: keel-cloud 236 (`f8c350c8`): Compatibility §2 (was `3041f69c...`, 235).
CARDS_SHA256_236 = "204eef55f448f8a5da2bb7f13b039a5636ca6f14cfa80108d40ab8cf83df353f"
#: keel-cloud 237 (`76620269`, the sha this spec names): Relative advantage §2, §5 and §6.
CARDS_SHA256_237 = "42fa94dd18d99c3800e507c2225d4e5244d8654425f3287447389ce56c15c0e1"

#: keel-cloud 237's fixtures (`BenefitsFixtures`, `TheBenefitsReadBackTest.theJobInTheTail`).
CLUSTER_JOB = "get each job to run to the end without wasting the cluster"
SIZER_WHAT = "software on every node that predicts each job's resource needs"
CLUSTER_HARD_CASE = "the last job that was killed for too little memory or time"
TABLE_HARD_CASE = "the last conversation you lost at a table with hearing people"


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


# ------------------------------------------------------------------------------------------- FR-1 the cards

def test_the_reader_digest_is_237s_cards():
    """FR-1: the reader's cards are the cloud's vendored copy byte for byte, at 237's digest (`CARDS_SHA256_141`, the one
    constant the earlier pins read, moved in place) -- or a later round's (eval spec 148 moved the copy to keel-cloud
    238 to 241's, `CARDS_SHA256_141`)."""
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == sha == CARDS_SHA256_141
    assert sha in (CARDS_SHA256_237, CARDS_SHA256_141)
    assert CARDS_SHA256_236 != CARDS_SHA256_237
    assert (KEEL_CLOUD / "src/main/resources/keel/dimension-cards.md").read_bytes() == ours


def test_compatibility_reads_every_row_and_moves_the_suggestion():
    """FR-1 (236 FR-6): Compatibility §2 -- every row read, Keel's included; a rewrite faces the settled test; two rows
    about one thing are one; the suggestion moves when put aside; the permission stem is the passive."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "(keel-cloud 233, 236, the review switch on)" in text
    assert "**every row is read, Keel's included** (its drafted rows and its suggestion, as the founder's)" in text
    assert "**A rewrite faces the settled test too:**" in text
    assert "**Two rows about one thing are one, by meaning:**" in text
    assert "**The suggestion moves when put aside:**" in text
    assert "Choose offers it as Keel's suggestion" in text
    assert "**the permission stem is the passive whichever way the row is written**" in text
    assert "*Think of your last booking call. Could unanswered calls have been forwarded to another number?*" in text
    assert "Keel's suggested row and Keel's own rows are never changed" not in text


def test_relative_advantage_reads_the_benefits_back_and_names_the_job():
    """FR-1 (237 FR-4): Relative advantage §2 -- the review may put a benefit aside and rewrite the hard case; the
    question names the job (the at-stake anchor keeps *done that better*); §5's stranger line as code serves it; §6's
    pitfalls of cycles 15 to 17."""
    text = " ".join(cards.CARDS_PATH.read_text(encoding="utf-8").split())
    assert "**The review may put a benefit aside** (keel-cloud 237, the review switch on)" in text
    assert "**The review may rewrite the hard case** (keel-cloud 237, the review switch on)" in text
    assert "*Think of {hard_case}. Would {Name}, {what it is}, have helped you {job} better, or not?*" in text
    assert "keeps *have done that better for you, or not?*, its *that* the job it names" in text
    assert ("*Keel put one benefit aside so what is left is what only your idea would have given them.*") in text
    assert "*Keel changed the moment the question asks about so it is the one that went wrong.*" in text
    assert ("Would Lullaby, a phone app, have helped you work out what the baby needs better, or not?") in text
    assert "*done that better* pointing at nothing once the hard case came first (cycles 15 to 17)" in text


# ------------------------------------------------------------------------------------------- FR-1 the hint

def test_the_compatibility_hint_is_181s():
    """FR-1 (keel-web 181 FR-1): the Answer hint's example is true for some of them, not all -- the walk's pin is the
    page's sentence (`ANSWER_HINT_OF["solution.compatibility"]`, the registry's caps); the 168 example is a fault."""
    from evals import corpus_scenario as cs                          # noqa: PLC0415
    source = _web("src/lib/translate.ts")
    assert ('each reading on from "Most ${said.people ?? "of them"} ...", e.g. "could talk over the noise on site" (true '
            'for some of them, not all).`') in source
    assert "have their phone with them at that moment" not in source.split("ANSWER_HINT_OF", 1)[1].split(
        "export const compatibilityHint", 1)[0]
    for people in ("construction superintendents", "of them"):
        hint = vs_screens.COMPATIBILITY_ANSWER_HINT_WANT.format(people=people)
        assert vs_screens.COMPATIBILITY_ANSWER_HINT.match(hint)["people"] == people
        assert hint.endswith('e.g. "could talk over the noise on site" (true for some of them, not all).')
        assert cs.said_faults({"screen": "answer", "hint": hint}, "solution.compatibility", b2b=False) == []
    old = vs_screens.COMPATIBILITY_ANSWER_HINT_168.format(people="of them")
    assert [f["what"] for f in cs.said_faults({"screen": "answer", "hint": old}, "solution.compatibility",
                                              b2b=False)] == ["the Answer hint"]


# ------------------------------------------------------------------------------------------- FR-1 the tail

def test_the_tails_words_are_scale_fours():
    """FR-1 (237 FR-3): `HELPED`, `HELPED_END`, `DONE_BETTER` and the trailing clause the job is cut by, read off
    `ScaleFour.java`."""
    scale = _cloud(VECTORS + "ScaleFour.java")
    assert f'HELPED = "{spoken_mod.HELPED}";' in scale
    assert f'HELPED_END = "{spoken_mod.HELPED_END}";' in scale
    assert f'DONE_BETTER = "{spoken_mod.DONE_BETTER}";' in scale
    assert '"(?i)^(.+?)\\\\s+(?:until|without|so that|before|after|while|because|in order to)\\\\s+.+$"' in scale
    assert "String helped = atStake ? null : helpedTail(job);" in scale


@pytest.mark.parametrize("args, want", [
    # the spec's own example: the hard case first, the job in the tail
    (("conversation", "AirCaps", "captioning glasses", "follow the conversation", None, TABLE_HARD_CASE),
     "Think of the last conversation you lost at a table with hearing people. Would AirCaps, captioning glasses, have "
     "helped you follow the conversation better, or not?"),
    # the ladder with the job: the head of the what
    (("job", "Sizer", SIZER_WHAT, CLUSTER_JOB, None, CLUSTER_HARD_CASE),
     "Think of the last job that was killed for too little memory or time. Would Sizer, software on every node, have "
     "helped you get each job to run to the end better, or not?"),
    # a ten-word job: *it*, never the bare name beside a what
    (("daily log", "Notes", "an AI scribe that turns your site-walk videos into notes",
      "keep an accurate record of the day's work on site", None,
      "the last daily log when you lost site notes before writing it"),
     "Think of the last daily log when you lost site notes before writing it. Would it have helped you keep an accurate "
     "record of the day's work on site better, or not?"),
    # no rung fits with the job: once more with the old tail
    (("daily log", "Notes", "a voice log",
      "keep an accurate and complete record of every single thing the crew did on the site that day", None,
      "the last daily log when you lost site notes before writing it"),
     "Think of the last daily log when you lost site notes before writing it. Would Notes, a voice log, have done that "
     "better for you, or not?"),
    # no job: the old tail
    (("conversation", "Loop", "captioning glasses", None, None, TABLE_HARD_CASE),
     "Think of the last conversation you lost at a table with hearing people. Would Loop, captioning glasses, have done "
     "that better for you, or not?"),
    # the card's good example
    (("night", "Lullaby", "a phone app that listens to crying", "work out what the baby needs", None,
      "the last night your baby would not settle"),
     "Think of the last night your baby would not settle. Would Lullaby, a phone app, have helped you work out what the "
     "baby needs better, or not?"),
])
def test_the_job_in_the_tail_as_keel_cloud_serves_it(args, want):
    """FR-1 (237 FR-3, `TheBenefitsReadBackTest.theJobInTheTail`): the mirror composes keel-cloud's items word for
    word; each reads its frame."""
    occasion, name, what, job, stem, hard = args
    assert spoken_mod.advantage_stem(occasion, name, what, job, stem, hard) == want
    assert vs.benefit_frame_of(want) == ("237" if " have helped you " in want else "198")


def test_the_at_stake_anchor_keeps_done_that_better():
    """FR-1 (237 FR-3): with no hard case and no stem, the at-stake anchor names the job itself -- its tail stays
    *have done that better for you, or not?* (frame `"198"`)."""
    asked = spoken_mod.advantage_stem("job", "Sizer", SIZER_WHAT, CLUSTER_JOB, None, None)
    assert asked.startswith("Think of the most recent time you had to get each job to run to the end. ")
    assert asked.endswith(spoken_mod.DONE_BETTER) and vs.benefit_frame_of(asked) == "198"
    anchor, at_stake = spoken_mod.advantage_anchor("job", CLUSTER_JOB)
    assert at_stake and asked.startswith(anchor)
    assert spoken_mod.advantage_anchor("job", CLUSTER_JOB, None, CLUSTER_HARD_CASE)[1] is False


def test_the_helped_tail():
    """FR-1 (237 FR-3, `ScaleFour.helpedTail`): the job in the second person, its trailing clause cut."""
    assert spoken_mod.helped_tail(CLUSTER_JOB) == "have helped you get each job to run to the end better, or not?"
    assert spoken_mod.helped_tail("keep track of their own notes") == \
        "have helped you keep track of your own notes better, or not?"
    assert spoken_mod.helped_tail(None) is None and spoken_mod.helped_tail("  ") is None


def test_the_frames_read():
    """FR-1: `benefit_frame_of` -- 237's tail, 198's, and the older three as before; `benefit_split` the anchor apart."""
    helped = ("Think of the last job that ran out of memory. Would Expanse, software on every node, have helped you get "
              "each job to run to the end better, or not?")
    assert vs.benefit_frame_of(helped) == "237"
    assert vs.BENEFIT_HELPED.match(vs.benefit_split(helped)[1])["job"] == "get each job to run to the end"
    assert vs.benefit_split(helped)[0] == "Think of the last job that ran out of memory."
    assert vs.benefit_frame_of("Would it have helped you keep an accurate record of the day's work on site better, or "
                               "not?") == "237"
    assert vs.benefit_frame_of("Would Palus have made your last cash decision go better for you, or not?") == "173"
    assert vs.benefit_frame_of("On your last day, would Fresco have made it go better for you, or not?") == "159"
    assert vs.benefit_frame_of("On your last day, would Fresco have made things better, or not?") == "085"
    assert vs.benefit_frame_of("Would you buy it?") is None
