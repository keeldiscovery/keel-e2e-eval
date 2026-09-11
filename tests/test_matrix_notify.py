"""The `Matrix is red` issue: what the workflow is told to do, and why (spec `021-short-journey`).

**The founder asked to be told when the matrix goes red.** The design's §6.4 records a verdict in
three places, and every one of them is somewhere a founder has to go and look. The fourth is one
issue: opened when a cell fails, commented on rather than duplicated while it stays red, and
closed with *green again* by the first run where everything passed.

These are the branches the workflow's own `run:` block cannot be held to. What is left there is
four `gh issue` calls with no branches of their own -- the most that can be checked without a
runner and a repository -- so the decision lives in `matrix/notify.py` and is checked here,
offline, stdlib only, before it can open an issue nobody wanted.
"""

from __future__ import annotations

import json

import pytest

from matrix import notify as n

TABLE = "| cell | scenario | verdict |\n|---|---|---|\n| `macos-latest-claude-py3.13` | s012 | **FAILED** |"


# ------------------------------------------------------------------------------- the four branches

def test_red_with_nothing_open_opens_one():
    plan = n.decide(red=True, issue=None, ran_any=True, table=TABLE)
    assert plan.action == "open"
    assert plan.title == "Matrix is red" and plan.label == "matrix"
    assert TABLE in plan.body
    assert "no issue is open" in plan.why


def test_red_with_one_already_open_comments_rather_than_opening_a_second():
    """An issue per red run is a mailbox; one issue gathering a table a run is a log."""
    plan = n.decide(red=True, issue=41, ran_any=True, table=TABLE)
    assert plan.action == "comment" and plan.issue == 41
    assert TABLE in plan.body
    assert "still red" in plan.why


def test_green_with_one_open_says_green_again_and_closes_it():
    plan = n.decide(red=False, issue=41, ran_any=True, table=TABLE)
    assert plan.action == "close" and plan.issue == 41
    assert "green again" in plan.body
    assert "every cell passed" in plan.body


def test_green_with_nothing_open_says_nothing_at_all():
    """The ordinary morning. A workflow that commented on every green run would be a workflow the
    founder muted, and then the red ones would go unread too."""
    plan = n.decide(red=False, issue=None, ran_any=True, table=TABLE)
    assert plan.action == "none" and plan.body == ""
    assert "ordinary morning" in plan.why


# ------------------------------------------------------------------------------- the two edge cases

@pytest.mark.parametrize("red,issue", [(False, 41), (False, None), (True, 41), (True, None)])
def test_a_run_that_measured_nothing_is_never_green_and_never_red(red, issue):
    """Cells skipped by a failed deploy, or a cancelled run, produce no rows. Closing the issue on
    the strength of that would be closing it on a run that measured nothing -- and opening one
    would be reporting a deploy failure as a red matrix."""
    plan = n.decide(red=red, issue=issue, ran_any=False, table=TABLE)
    assert plan.action == "none"
    assert "measured nothing" in plan.why


def test_every_action_is_one_the_workflow_knows_how_to_do():
    for red in (True, False):
        for issue in (None, 7):
            for ran in (True, False):
                assert n.decide(red=red, issue=issue, ran_any=ran).action in n.ACTIONS


# --------------------------------------------------------------------------- the body it hands over

def test_the_body_names_the_set_and_links_the_run():
    plan = n.decide(red=True, issue=None, ran_any=True, table=TABLE, set_name="per_change",
                    run_url="https://github.com/keeldiscovery/keel-e2e-eval/actions/runs/1",
                    why="push to master")
    assert "`per_change`" in plan.body
    assert "/actions/runs/1" in plan.body
    assert "push to master" in plan.body


def test_the_body_survives_an_empty_table():
    """A cell that failed before pytest wrote no row, so the table can be nothing at all; the
    issue still has to be openable."""
    plan = n.decide(red=True, issue=None, ran_any=True, table="")
    assert plan.action == "open" and plan.body.strip()


# --------------------------------------------------------------- what the workflow actually reads

@pytest.mark.parametrize("raw,expected", [("", None), ("   ", None), ("0", None), ("-", None),
                                          ("41", 41), ("#41", 41), (" 41\n", 41), (None, None)])
def test_an_issue_number_off_gh_jq_is_read_loosely(raw, expected):
    """`gh issue list --jq '... // empty'` prints an empty line when it found nothing, and a
    founder pasting one into a rerun types `#41`."""
    assert n._issue_number(raw) == expected


@pytest.mark.parametrize("raw", ["true", "TRUE", "1", "yes", "on"])
def test_the_shells_idea_of_true_is_this_modules_idea_of_true(raw):
    assert n._truthy(raw) is True


@pytest.mark.parametrize("raw", ["false", "", "0", "no", "maybe", None])
def test_anything_else_is_false(raw):
    assert n._truthy(raw) is False


def test_the_cli_prints_the_plan_as_json_and_writes_the_body_to_a_file(tmp_path, capsys):
    """The body goes through a file and never through an argument: a summary table is full of
    backticks, pipes and em dashes, and a shell is the wrong place to carry those."""
    table = tmp_path / "table.md"
    table.write_text(TABLE, encoding="utf-8")
    body = tmp_path / "body.md"
    assert n.main(["--red", "true", "--ran-any", "true", "--issue", "", "--set", "nightly",
                   "--table-file", str(table), "--body-out", str(body)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["action"] == "open"
    assert plan["title"] == "Matrix is red"
    assert TABLE in body.read_text(encoding="utf-8")


def test_the_cli_survives_a_table_file_that_was_never_written(tmp_path, capsys):
    assert n.main(["--red", "false", "--issue", "9", "--ran-any", "true",
                   "--table-file", str(tmp_path / "missing.md")]) == 0
    assert json.loads(capsys.readouterr().out)["action"] == "close"
