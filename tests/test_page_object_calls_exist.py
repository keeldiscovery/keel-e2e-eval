"""Every page-object attribute a scenario names must exist on the class it names it on.

`runs/DRIFT.md` #33's second half. `evals/test_s002_agent_optional.py` asked an `OpenedCard` for
`belief_headings()` -- a real method, on `StageCard`, the *review* card, which draws its beliefs as
a `.belief .b-heading` list where an opened card draws strip rows. Python found that out at the
only moment it could: three minutes into a stack run, `AttributeError`, on the first
`make eval-all` since spec 010 rewrote the screens (`runs/20260907T164650Z-s002-agent-optional`).
Nothing else in this repo would have caught it -- the scenarios are the only callers, the stack is
the only way to run them, and a typo'd accessor is indistinguishable from a red run until you read
the traceback.

This is a **static** check, so it costs no stack and no browser: walk each scenario's AST, note
every local bound to a `harness.browser` page object (`card = OpenedCard(...)`), and assert every
attribute reached through that local exists on the class. It is deliberately conservative -- a
name it cannot resolve to exactly one class is skipped rather than guessed at -- so it can fail
only on a real missing attribute, never on a clever binding it did not follow.

It does not check arity, types or that the selector inside still matches keel-web. Those belong to
a run. This checks the one thing a run finds out too late and too expensively.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from harness import browser as browser_module

_EVALS = pathlib.Path(__file__).resolve().parent.parent / "evals"

# Every page object the scenarios construct by name, by that name.
_PAGE_OBJECTS = {
    name: obj
    for name, obj in vars(browser_module).items()
    if inspect.isclass(obj) and obj.__module__ == browser_module.__name__
    and not name.startswith("_")
}


def _scenario_files() -> list[pathlib.Path]:
    return sorted(p for p in _EVALS.glob("*.py") if p.name != "__init__.py")


def _bindings(tree: ast.AST) -> dict[str, set[str]]:
    """`name -> {class names it was ever bound to}`, for direct `name = ClassName(...)` only."""
    bound: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if not isinstance(func, ast.Name) or func.id not in _PAGE_OBJECTS:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                bound.setdefault(target.id, set()).add(func.id)
    return bound


def test_every_page_object_class_was_found():
    """A guard on the guard: if `harness.browser` is ever restructured so this finds no classes,
    the check below would pass vacuously and say nothing."""
    assert {"OpenedCard", "StageCard", "ParticipantPage", "People"} <= set(_PAGE_OBJECTS), (
        f"the page objects moved out of harness.browser: found {sorted(_PAGE_OBJECTS)}")


@pytest.mark.parametrize("path", _scenario_files(), ids=lambda p: p.name)
def test_no_scenario_calls_a_page_object_attribute_that_does_not_exist(path):
    tree = ast.parse(path.read_text(), filename=str(path))
    bound = _bindings(tree)

    missing = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or not isinstance(node.value, ast.Name):
            continue
        classes = bound.get(node.value.id)
        # Only a name bound to exactly one page object is judged: anything reassigned across two
        # classes, or bound somewhere this walk does not follow, is not this test's business.
        if not classes or len(classes) != 1:
            continue
        class_name = next(iter(classes))
        if not hasattr(_PAGE_OBJECTS[class_name], node.attr):
            missing.append(f"{path.name}:{node.lineno}: "
                            f"{node.value.id}.{node.attr} -- {class_name} has no {node.attr!r}")

    assert not missing, "page-object attributes that do not exist:\n  " + "\n  ".join(missing)
