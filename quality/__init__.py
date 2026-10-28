"""The question-quality readers (spec 078): a versioned rubric, two reader prompts, committed scores, a baseline.

`quality/rubric.py` (the ruler, `RUBRIC_VERSION`), `quality/readers.py` (`make read-screens`, paid: the only module
here that calls a model, through the `claude` CLI as `instructions/judge.py` does) and `quality/table.py`
(`make read-table`, free). Nothing here is imported by `make eval`, a scenario, the matrix or a checker.
"""
