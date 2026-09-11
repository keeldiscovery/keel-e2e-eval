"""`.github/workflows/matrix.yml`, held to what spec 021 added to it.

Three things, and the first two are the founder's decisions of 2026-09-11:

1. **The receiver honours `[skip e2e]` on its own push**, the way the four senders already did.
   Until today the same four words were obeyed on a merge to keel-cloud and ignored on a merge to
   this repository, which is the kind of asymmetry nobody notices until it costs thirty-nine
   premium requests. The matcher itself is **run**, under bash, against the messages a founder
   actually writes -- extracted from the workflow, so a matcher that changed shape fails here.
2. **A cell exports `KEEL_JOURNEY_LEGS` from its own field**, so the set decides how far a cell
   goes and the job only reads.
3. **The `summary` job may write issues, and no other job may.** A job-level `permissions:` block
   replaces the workflow's rather than adding to it, which is exactly the sort of thing worth one
   assertion.

Nothing here runs a workflow, reaches GitHub, or needs a runner. `actionlint` checks the YAML's
grammar; this checks what it says.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO / ".github" / "workflows" / "matrix.yml"
TEXT = WORKFLOW_PATH.read_text(encoding="utf-8")
# `on:` is YAML 1.1's boolean true, so the parsed key is `True`. Read as text where that matters.
DOC = yaml.safe_load(TEXT)
JOBS = DOC["jobs"]


def step_named(job: str, needle: str) -> dict:
    for step in JOBS[job]["steps"]:
        if needle in (step.get("name") or "") or needle == step.get("id"):
            return step
    raise AssertionError(f"no step matching {needle!r} in job {job!r}")


# ------------------------------------------------------------------- [skip e2e], on this repo too

def test_the_gate_reads_the_head_commit_message_through_the_environment():
    """Never `${{ github.event.head_commit.message }}` inside a `run:` block: a commit message is
    a stranger's text and an expression is substituted before bash ever sees the script."""
    gate = step_named("select", "gate")
    assert gate["env"]["HEAD_COMMIT_MESSAGE"] == "${{ github.event.head_commit.message }}"
    assert "${{ github.event.head_commit" not in gate["run"], (
        "the message must reach the script as a variable, not as an interpolation")


def test_the_gate_only_reads_it_on_a_push():
    """A schedule, a hand dispatch and a repository_dispatch have no head commit of their own, and
    a stale one from another event would skip a run the founder asked for."""
    run = step_named("select", "gate")["run"]
    assert '[ "$EVENT" = "push" ]' in run
    assert step_named("select", "gate")["env"]["EVENT"] == "${{ github.event_name }}"


SKIP_CONDITION = next(line.strip() for line in TEXT.splitlines() if "grep -qF" in line)


@pytest.mark.parametrize("message,skipped", [
    ("matrix: the short journey [skip e2e]", True),
    ("[skip e2e] docs only", True),
    ("Merge branch 'short-journey'\n\nmatrix: four cells [skip e2e]\n", True),
    ("matrix: the short journey", False),
    ("skip e2e", False),                      # the brackets are the marker, not the words
    ("[skip ci]", False),                     # a different marker, for a different workflow
    ("[SKIP E2E]", False),                    # -F and case-sensitive, as the senders have it
    ("", False),
])
def test_the_matcher_the_workflow_actually_carries(message, skipped):
    """The real condition line, run under the real shell. A matcher that grew a regex, lost its
    `-F`, or started matching `skip ci` fails this without anyone having to remember to look."""
    script = (f'set -euo pipefail\nEVENT=push\n{SKIP_CONDITION}\n'
              '  echo SKIPPED\nelse\n  echo RAN\nfi\n')
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                         env={"HEAD_COMMIT_MESSAGE": message, "PATH": "/usr/bin:/bin:/usr/local/bin"})
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == ("SKIPPED" if skipped else "RAN")


def test_the_matcher_is_literal_and_not_a_pattern():
    assert "grep -qF '[skip e2e]'" in SKIP_CONDITION, (
        "-F, because `[skip e2e]` is a character class to any other grep")


def test_a_skipped_push_still_says_so_in_the_summary():
    """The founder who typed the words gets one line confirming they were read, not silence that
    looks the same as a workflow that never started."""
    run = step_named("select", "gate")["run"]
    assert "[skip e2e]" in run and "GITHUB_STEP_SUMMARY" in run
    assert run.count("enabled=false") == 2, (
        "two ways to be off -- the twin is not on, and the founder said not to -- and each says "
        "which")


# ----------------------------------------------------------------------- the legs reach the cell

def test_a_cell_exports_its_own_legs():
    assert JOBS["cell"]["env"]["KEEL_JOURNEY_LEGS"] == "${{ matrix.cell.legs }}"
    assert JOBS["cell"]["env"]["KEEL_JOURNEY_HOST"] == "${{ matrix.cell.host }}"


def test_the_cell_job_never_decides_how_far_it_goes():
    """`matrix/cells.toml` decides, `python -m matrix` hands it over, the job reads it. A `legs`
    computed in a workflow expression is a decision no unit test could reach."""
    assert "KEEL_JOURNEY_LEGS: short" not in TEXT
    assert re.search(r"KEEL_JOURNEY_LEGS:.*\|\|", TEXT) is None


# --------------------------------------------------------------- the corpus a cell now has to read

def test_a_cell_checks_out_the_corpus_and_nothing_else_of_keel_cloud():
    step = step_named("cell", "golden corpus")
    assert step["with"]["repository"] == "keeldiscovery/keel-cloud"
    assert step["with"]["sparse-checkout"] == "canon/designs/measured-beliefs/corpus"
    assert step["with"]["path"] == "siblings/keel-cloud"
    assert step["if"] == "steps.siblings-token.outputs.have == 'true'"


def test_stack_toml_is_pointed_at_the_corpus_checkout():
    run = step_named("cell", "Bundle the runtime")["run"]
    assert "keel_cloud = \\\"siblings/keel-cloud\\\"" in run or 'keel_cloud = "siblings/keel-cloud"' in run


def test_a_cell_without_the_token_warns_rather_than_pretending():
    run = step_named("cell", "siblings-token")["run"]
    assert "::warning::" in run
    assert "fail by name" in run, (
        "never a quiet fallback to another founder -- a bundle that measured someone it does not "
        "name is worse than one that measured nobody")


# ------------------------------------------------------------------------------- the issue, scoped

def test_only_the_summary_and_wake_jobs_may_write_an_issue():
    """The summary writes the issue; the wake job (the Claude that reads a red matrix, founder's
    rule of 2026-09-11) comments on it and may open a pull request. Nothing else may."""
    assert JOBS["summary"]["permissions"] == {"contents": "read", "issues": "write"}
    assert JOBS["wake"]["permissions"]["issues"] == "write"
    assert JOBS["wake"]["permissions"]["pull-requests"] == "write"
    for name, job in JOBS.items():
        if name in ("summary", "wake"):
            continue
        assert "issues" not in (job.get("permissions") or {}), name
    assert DOC[True] is not None  # `on:` parsed; the workflow-level permissions stay read-only
    assert DOC["permissions"]["contents"] == "read"
    assert "issues" not in DOC["permissions"]


def test_the_summary_job_asks_the_tested_module_what_to_do():
    run = step_named("summary", "Tell the founder")["run"]
    assert "python -m matrix.notify" in run
    verbs = sorted({line.split("gh issue", 1)[1].split()[0]
                    for line in run.splitlines() if "gh issue" in line})
    assert verbs == ["close", "comment", "create", "list"], (
        "list, create, comment, close -- and no fifth verb (the close branch comments first, so "
        "an issue is never closed without saying why)")
    assert "--body-file issue-body.md" in run, (
        "a table full of backticks and pipes goes through a file, never through an argument")


def test_the_issue_is_found_by_title_and_the_label_is_created_before_it_is_used():
    """Two ways this step could fail on a repository that has never been red: `gh issue list
    --label matrix` errors when the label does not exist, and `gh issue create --label matrix`
    refuses one that does not exist. Neither may be how the founder finds out the matrix broke."""
    run = step_named("summary", "Tell the founder")["run"]
    assert "gh issue list --state open" in run and "--label matrix" not in run.split("case")[0]
    assert 'select(.title == "Matrix is red")' in run
    assert "gh label create matrix" in run and "|| true" in run


def test_the_summary_job_has_a_checkout_and_a_python_to_run_it_with():
    """It had neither before spec 021: it only downloaded artifacts and printed a table."""
    uses = [s.get("uses", "") for s in JOBS["summary"]["steps"]]
    assert any(u.startswith("actions/checkout@") for u in uses)
    assert any(u.startswith("actions/setup-python@") for u in uses)


def test_a_cell_job_that_crashed_outright_still_counts_as_red():
    """A cell that failed before pytest wrote no row, so the table cannot see it -- and a matrix
    where every cell crashed is the reddest one there is."""
    run = step_named("summary", "Tell the founder")["run"]
    assert "CELLS_RESULT" in run and "failure)   red=true; ran_any=true" in run
    # ...and a CANCELLED run is neither: it measured nothing (the false alarm of 2026-09-11).
    assert "cancelled) red=false; ran_any=false" in run


def test_the_wake_job_runs_only_on_a_red_matrix_and_never_closes_the_issue():
    job = JOBS["wake"]
    assert "needs.cell.result == 'failure'" in job["if"]
    assert "needs.select.outputs.enabled == 'true'" in job["if"]
    prompt = next(st for st in job["steps"] if "anthropics/claude-code-action" in str(st.get("uses")))
    assert "matrix/RED.md" in prompt["with"]["prompt"]
    assert "KEEL_RUNTIME_CI_CLAUDE" in prompt["with"]["claude_code_oauth_token"]


def test_a_hand_dispatch_has_its_own_concurrency_lane():
    group = DOC["concurrency"]["group"]
    assert "github.run_id" in group and "workflow_dispatch" in group


def test_the_issue_is_information_and_never_a_trigger():
    """Invariant M8 and decision 12, restated where the new job could have broken them."""
    run = step_named("summary", "Tell the founder")["run"]
    for forbidden in ("deploy.sh", "aws ", "workflow_dispatch", "gh workflow run"):
        assert forbidden not in run, forbidden
