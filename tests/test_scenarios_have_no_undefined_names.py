"""No scenario reaches a paid run with a name that does not exist (spec `016-copilot-e2e`).

**The harness fault this exists to stop happening twice.** An edit to S-012 renamed a constant and
left one reference behind. Every stackless test still passed -- they import the module and read its
constants, and none of them *executes* the scenario body -- and `make unit` was green at 615. The
`NameError` surfaced where it costs the most: three minutes into a live run, after `make down`,
`make up`, a browser, a sign-in and a session fixture.

It cost nothing that time, because it failed before the first `copilot -p`. It could as easily have
been a name used after the last one, and then it would have thrown away a whole journey's premium
requests and a stack session for a typo.

This is `tests/test_page_object_calls_exist.py`'s idea applied to plain names rather than
attributes: a scenario is *read* here, statically, so the one thing a stackless suite structurally
cannot see -- a body that never runs until money is being spent -- is seen anyway.
"""

from __future__ import annotations

import builtins
import symtable
from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parent.parent / "evals"


def _scenario_files() -> list[Path]:
    return sorted(EVALS.glob("test_s*.py"))


def _undefined_in(table: symtable.SymbolTable, module_names: set[str],
                   trail: tuple[str, ...] = ()) -> list[str]:
    """Every name a nested scope reads as a global that no module-level binding and no builtin
    provides.

    `symtable` is the compiler's own answer to "what does this scope bind and what does it read",
    so this asks Python rather than re-implementing scoping. A name read as a global inside a
    function is only resolvable at module level; if it is not there, the call is a `NameError`
    waiting for the branch that reaches it.
    """
    found: list[str] = []
    for symbol in table.get_symbols():
        if not symbol.is_global() or symbol.is_assigned():
            continue
        name = symbol.get_name()
        if name in module_names or hasattr(builtins, name):
            continue
        found.append(f"{'.'.join(trail) or '<module>'}: {name}")
    for child in table.get_children():
        found += _undefined_in(child, module_names, trail + (child.get_name(),))
    return found


@pytest.mark.parametrize("path", _scenario_files(), ids=lambda p: p.name)
def test_no_scenario_reads_a_name_that_is_never_defined(path: Path):
    top = symtable.symtable(path.read_text(), str(path), "exec")
    module_names = {s.get_name() for s in top.get_symbols()}
    missing = _undefined_in(top, module_names)
    assert not missing, (
        f"{path.name} reads names nothing defines -- a NameError waiting for the branch that "
        f"reaches it, and in a live scenario that branch costs money:\n  " + "\n  ".join(missing))


def test_the_guard_catches_the_fault_that_produced_it(tmp_path: Path):
    """A seeded-loss fixture, in the manner of the scoring suite's: the guard is only worth having
    if it fails on the exact shape it was written for -- a constant renamed at the top and left
    behind in the body."""
    bad = tmp_path / "test_s999_seeded.py"
    bad.write_text("RUNTIME_MODEL = 'x'\n\n\ndef test_it():\n    return HOST_MODEL\n")
    top = symtable.symtable(bad.read_text(), str(bad), "exec")
    missing = _undefined_in(top, {s.get_name() for s in top.get_symbols()})
    assert any("HOST_MODEL" in m for m in missing), missing
