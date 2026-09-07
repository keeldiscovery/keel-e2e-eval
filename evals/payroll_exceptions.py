"""The smoke's fixture, loaded (spec 010 FR-007/FR-010, T023).

Everything this module used to carry as Python literals -- statements, role labels, belief
headings, three participants' typed answers, three hand-written headlines and their counts -- is
now **data**, in `evals/payroll_exceptions.yaml`, in keel-cloud's own frozen-corpus shape, read by
`harness/corpus_script.py` through `instructions/corpus.py`. One generator, one shape, two
sources: this repo's own fixture, which it may edit, and keel-cloud's corpus, which it may not
(spec judgement call 3).

What went away with the old model, and is not replaced: `PROBLEM_HEADLINE` and its
`COUNTS_NOTE` siblings. They were a hand-copy of what keel-cloud's `Standing` would say about a
claim/stance aggregate that no longer exists -- `Stance`, `ClaimType`, `Question` and `Answer` are
gone from that repo entirely. A headline is now derived from a `BeliefStanding` the aggregate
computes from picks, and the smoke reads it off the screen rather than asserting a literal it
mirrored by hand.

`facts()` still exists and is still the one function `evals/test_s001_smoke.py` calls -- it just
delegates to `evals/corpus_facts.facts_for`, which builds the same registry from any entry
(FR-011). The one thing it adds is `absent_hops`: the founder's band and their expected pick,
declared **absent** from the participant's page, scored for the first time (FR-030).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from evals import corpus_facts
from evals.facts import Fact
from harness import corpus_script

FIXTURE_PATH = Path(__file__).resolve().parent / "payroll_exceptions.yaml"

#: The one line the smoke's founder corrects at a review card (FR-008's correction turn). It names
#: **one** line and a different size, so the agent's answer is checkable: the card comes back with
#: that line redone, a before-and-after, and still unapproved.
CORRECTION = corpus_script.Correction(
    stage="PROBLEM",
    belief_id="P1",
    message=("Line 1 isn't what I meant -- it's one to four hours, not one to two. "
             "Redo that line and leave the rest alone."),
    expected_change="Sorting out the last payroll exception took the manager one to four hours.",
)

# The three the journey's own assertions name, kept so `canon/journeys.md` still reads true. They
# are the first person of each role in the fixture, and they are named here rather than indexed so
# a reordering of the YAML cannot silently change who the smoke reads back.
JOURNEY_PEOPLE = ("Dana Okafor", "Wei Zhang", "Marcus Webb")


@lru_cache(maxsize=1)
def _loaded():
    return corpus_script.entry_from_file(FIXTURE_PATH)


def corpus():
    """The one-entry `Corpus`, so a scenario can call `verify_unchanged()` on the fixture exactly
    as the corpus scenarios do on the frozen set (FR-005). This repo may edit the file -- but not
    while a run is in flight, which is the only thing the check is claiming."""
    return _loaded()[0]


def entry():
    return _loaded()[1]


def script():
    return corpus_script.generate(entry(), correction=CORRECTION)


def founder():
    return corpus_script.founder_inputs(entry(), correction=CORRECTION)


def people():
    return corpus_script.person_inputs(entry())


def role_labels() -> list[str]:
    return [role["label"] for role in entry().roles or []]


def facts(*, modal_person: str | None = None,
          modal_anchor: str | None = None) -> dict[str, Fact]:
    """The Fact registry `harness/rubric.py`'s FID-* checks trace, restated for the
    measured-beliefs hops (FR-010): the project name, each stage's claim, each belief's
    `founderPhrase`, each role label, each anchor and selection prompt, and each person's own
    story -- plus, in `absent_hops`, the founder's band and expected pick declared absent from
    `participant_page`."""
    return corpus_facts.facts_for(entry(), modal_person=modal_person,
                                   modal_anchor=modal_anchor)
