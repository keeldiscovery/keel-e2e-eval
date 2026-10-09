"""The named skip for the tests that read the corpus in its revision-2 shape (spec 029 T016, Open
item O-1).

`harness/corpus_script.py`, `harness/stranger_stories.py`, `evals/corpus_facts.py` and the scenarios
built on them drive **today's** product -- three framed stages, the review cards, one
questionnaire -- off the r2 corpus's `beliefs`, `questionnaire.anchors`, `expected.buckets` and
`expected.stages`. Revision 3 drops every one of those keys, and rewriting those readers against the
vector product is a sibling spec's (`030-journey-vectors`), not 029's. So once
`instructions.corpus` is the revision-3 loader, every test that asserts the r2 shape skips **by
name**, with that sentence -- never a fixture copy of the old corpus, which would be a second
frozen corpus in all but name (research R14).
"""

from __future__ import annotations

import pytest

from harness.corpus_script import R2_READERS_RETIRED
from instructions import corpus as corpus_reader

RETIRED = getattr(corpus_reader, "REVISION", 2) >= 3

requires_r2 = pytest.mark.skipif(RETIRED, reason=R2_READERS_RETIRED)


def skip_if_retired() -> None:
    if RETIRED:
        pytest.skip(R2_READERS_RETIRED)
