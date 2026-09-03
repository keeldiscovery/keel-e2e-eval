"""The Fact registry (data-model.md's "Fact registry"), surviving the retirement of
`evals/scenario.py`'s `Scenario` payload-builder abstraction (spec 005-connect-stack FR-006):
a founder- or participant-entered text a scenario cares about tracing hop-by-hop through the
screens it should render on verbatim, checked by `harness/rubric.py`'s FID-* checks.

`evals/payroll_exceptions.py` is the one module that builds these now -- a plain function
returning `dict[str, Fact]`, not a method on a base class every scenario used to subclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fact:
    text: str
    kind: str  # statement | role | assumption | about_line | answer | interpretation
    hops: list[str] = field(default_factory=list)
    absent_hops: list[str] = field(default_factory=list)
