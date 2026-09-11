"""The matrix, as data plus the one reader of it (spec 020-matrix-workflow; keel-cloud
`canon/designs/e2e-matrix-design.md` §5).

`cells.toml` is the file; `cells.py` reads it. `python -m matrix` and `make matrix-check` are the
same command, and `.github/workflows/matrix.yml`'s `select` job runs it with `--json`.
"""

from matrix.cells import (  # noqa: F401 - the package's whole surface, re-exported once
    CELLS_TOML,
    SET_NAMES,
    Cell,
    CellsError,
    Matrix,
    coverage_problems,
    load,
    render,
    validate,
)
