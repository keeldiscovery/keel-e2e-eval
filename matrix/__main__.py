"""`python -m matrix` -- what `make matrix-check` runs on the founder's Mac and what the matrix
workflow's `select` job runs on a runner, byte for byte the same code (spec 020)."""

from matrix.cells import main

raise SystemExit(main())
