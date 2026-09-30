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
    assert JOBS["cell"]["env"]["KEEL_JOURNEY_INSTALL"] == "${{ matrix.cell.install }}"


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

def test_only_the_summary_job_may_write_an_issue():
    """The summary writes the issue and nothing else may. (An automatic Claude that read the issue
    existed for one afternoon, 2026-09-11; the founder chose a session that reads it on request.)"""
    assert JOBS["summary"]["permissions"] == {"contents": "read", "issues": "write"}
    assert "wake" not in JOBS
    for name, job in JOBS.items():
        if name == "summary":
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


def test_a_hand_dispatch_has_its_own_concurrency_lane():
    group = DOC["concurrency"]["group"]
    assert "github.run_id" in group and "workflow_dispatch" in group


def test_the_issue_is_information_and_never_a_trigger():
    """Invariant M8 and decision 12, restated where the new job could have broken them."""
    run = step_named("summary", "Tell the founder")["run"]
    for forbidden in ("deploy.sh", "aws ", "workflow_dispatch", "gh workflow run"):
        assert forbidden not in run, forbidden


# ------------------------------------------------- the twin follows keel-cloud, whoever pushed first

def test_the_deploy_step_skips_only_when_the_twin_already_runs_the_tag():
    """2026-09-12: the step used to read "the tag is in ECR" as "the twin runs it". The night
    production was deployed first (the same image tag, invariant M1) the keel-cloud dispatch left
    the twin six commits behind and every cell green on the wrong build. The skip must be decided
    by /keel/staging/deployed-tag -- what deploy.sh writes last -- and a tag that is in ECR but
    not on the twin must be a loud red, because an immutable repository means this job cannot
    push it again and only the Mac can move the twin."""
    run = step_named("deploy-staging", "deploy.sh --target staging")["run"]
    assert "/keel/staging/deployed-tag" in run
    assert '[ "$running" = "$TAG" ]' in run, "the skip compares the tag the twin runs, not ECR"
    assert "the twin is already on it" not in run, "an ECR hit is not evidence the twin runs it"
    ecr_branch = run.split("elif aws ecr describe-images", 1)[1].split("else", 1)[0]
    assert "exit 1" in ecr_branch, "in ECR but not on the twin: fail, do not test the wrong build"
    assert "deploy.sh --target staging $TAG" in ecr_branch, "and say which command moves it"


# ------------------------------------------------------------ design §16: one Saturday cron, and the wipe

def test_there_is_exactly_one_cron_and_it_is_saturday_0400():
    """Design §16 (the founder, 2026-09-13): *"on Saturday when I wake up I should be able to see
    4x2 = 8 scenarios completed."* One cron, the weekly; the nightly's is gone (§15)."""
    on = DOC[True] if True in DOC else DOC["on"]
    crons = [entry["cron"] for entry in on["schedule"]]
    assert crons == ["0 4 * * 6"]
    assert "schedule)" in TEXT and "set_name=weekly" in TEXT, "every schedule is the weekly"


def test_every_deploy_wipes_the_twin_with_keel_clouds_own_reset_script():
    """Design §16: *"every time you deploy I want you to clean up the staging DB so that when I
    log in I just see that scenario alone."* The wipe is keel-cloud's reset.sh -- the one script
    that deletes anything on staging and refuses prod outright -- run inside the deploy job after
    the deploy step and before the gate the cells wait on, on the tag the job settled on."""
    steps = JOBS["deploy-staging"]["steps"]
    names = [(s.get("id"), s.get("name") or "") for s in steps]
    deploy_at = next(i for i, (sid, _) in enumerate(names) if sid == "deploy")
    wipe_at = next(i for i, (sid, _) in enumerate(names) if sid == "wipe")
    gate_at = next(i for i, (_, name) in enumerate(names) if name.startswith("The gate"))
    assert deploy_at < wipe_at < gate_at
    wipe = steps[wipe_at]
    assert "./deploy/bin/reset.sh --target staging \"$TAG\"" in wipe["run"]
    assert wipe["working-directory"] == "keel-cloud"
    assert wipe["env"]["TAG"] == "${{ steps.tag.outputs.tag }}"
    # The same two repository variables deploy.sh needs, because the CI role has no ec2:Describe*.
    assert wipe["env"]["KEEL_INSTANCE_ID"] == "${{ vars.KEEL_INSTANCE_ID }}"
    assert wipe["env"]["KEEL_ELASTIC_IP"] == "${{ vars.KEEL_ELASTIC_IP }}"
    # A hand dispatch may keep the twin's data; a push or the schedule always wipes -- except a
    # push to keel-web alone (design §16.1): the page is deployed, the twin's data stays.
    assert wipe["if"] == "inputs.wipe != false && needs.select.outputs.page_only != 'true'"
    on = DOC[True] if True in DOC else DOC["on"]
    assert on["workflow_dispatch"]["inputs"]["wipe"]["default"] is True


def test_the_wipe_never_names_production():
    run = step_named("deploy-staging", "reset.sh --target staging")["run"]
    assert "prod" not in run


def test_a_keel_web_push_deploys_the_twin_and_neither_wipes_nor_runs_a_cell():
    """Design §16.1 (the founder, 2026-09-13): *"a push to keel-web only deploys the twin so you can
    see the page."* The select job answers no cells and page_only=true for keel-web's dispatch; the
    wipe step reads that output; keel-cloud/runtime/skill dispatches are unchanged."""
    pick = next(s for s in JOBS["select"]["steps"] if s.get("id") == "pick")
    assert 'PAYLOAD_REPO" = keeldiscovery/keel-web' in pick["run"]
    assert "page_only=true" in pick["run"] and "cells='[]'" in pick["run"]
    assert JOBS["select"]["outputs"]["page_only"] == "${{ steps.pick.outputs.page_only }}"
    assert "PAYLOAD_REPO" in pick["env"]


# ------------------------------------------- the founder keeps the twin up (2026-09-29/30)

def test_the_dispatch_can_ask_to_stop_the_twin():
    """The founder, 2026-09-29/30: "keep the staging up for now until I say; let's use it for all
    manual testing." The default flipped on 2026-09-30, and the input flipped with it: one
    `workflow_dispatch` input, `stop_twin`, default false, so a dispatch that says nothing about it
    leaves the twin running."""
    on = DOC[True] if True in DOC else DOC["on"]
    inputs = on["workflow_dispatch"]["inputs"]
    assert "keep_twin" not in inputs, (
        "keep_twin is removed outright, not kept as a deprecated alias -- no caller outside this "
        "workflow ever set it (the four senders POST repository_dispatch, which carries no "
        "workflow_dispatch inputs at all), so there is nothing an ignored alias would protect")
    stop = inputs["stop_twin"]
    assert stop["type"] == "boolean"
    assert stop["default"] is False
    assert stop["description"] == (
        "stop the twin after the cells; the founder keeps it running for manual testing until he "
        "says otherwise")


def test_stop_twin_true_is_the_only_thing_that_runs_the_stop():
    """The two properties worth an assertion each, both inverted from before 2026-09-30 but
    otherwise unchanged:

    1. `stop_twin == true` is **ANDed onto** `stop-staging`'s existing `if`, so a cancelled run and
       a cells-only dispatch still behave exactly as spec 023 built them (deploy-gated, always());
       and
    2. nothing in that condition reads the cells' result, so a FAILED cell does not stop the twin
       either -- only the founder's own flag does.
    """
    condition = JOBS["stop-staging"]["if"]
    assert condition == ("always() && needs.select.outputs.deploy == 'true' "
                         "&& inputs.stop_twin == true")
    assert "needs.cell.result" not in condition, (
        "a red cell must not stop the twin on its own; only the founder's own flag may take it down")
    assert JOBS["stop-staging"]["needs"] == ["select", "deploy-staging", "cell"]


def test_a_push_leaves_the_twin_up():
    """`stop_twin` is a dispatch input and nothing else. On a push (or a schedule or a
    repository_dispatch) `inputs.stop_twin` is null, `null == true` is false, and `stop-staging`
    does not run -- the twin stays up for every unattended run, which is the founder's standing
    instruction holding by default now rather than by exception."""
    on = DOC[True] if True in DOC else DOC["on"]
    for event in ("push", "schedule", "repository_dispatch"):
        assert event in on
        assert not isinstance(on[event], dict) or "inputs" not in on[event]


def test_a_dispatch_with_no_stop_twin_also_leaves_the_twin_up():
    """`stop_twin`'s own default is false, so a hand dispatch that says nothing about it -- exactly
    like a push -- leaves `inputs.stop_twin` false and `stop-staging` does not run."""
    on = DOC[True] if True in DOC else DOC["on"]
    assert on["workflow_dispatch"]["inputs"]["stop_twin"]["default"] is False


def test_a_red_cell_does_not_stop_the_twin():
    """A FAILED cell is exactly the case spec 023 built `stop-staging` to still fire for -- and
    exactly the case the founder's standing instruction must not be overridden by. Neither
    `needs.cell.result` nor any other read of the cells' outcome appears in the condition, so a red
    cell is indistinguishable from a green one here: only `inputs.stop_twin == true` stops the
    twin."""
    condition = JOBS["stop-staging"]["if"]
    assert "cell.result" not in condition
    assert "outputs.red" not in condition
    assert condition.count("inputs.stop_twin") == 1


def test_the_summary_says_when_the_twin_is_left_running():
    """`stop-staging` is skipped whenever the twin is left up -- since 2026-09-30, every run that
    does not say `stop_twin: true` -- so the sentence that explains it cannot live inside that job.
    It lives where the founder reads the table."""
    step = step_named("summary", "Say so when the twin was left running")
    assert step["if"] == ("always() && needs.select.outputs.deploy == 'true' "
                          "&& inputs.stop_twin != true")
    assert "The twin was left running (the founder's standing instruction, 2026-09-29)" in step["run"]
    assert "$KEEL_REMOTE_WEB_URL" in step["run"], (
        "the note is worth nothing without the address the founder asked for the box in order to "
        "open")


def test_the_start_tolerates_a_twin_that_is_already_running_and_one_still_stopping():
    """Since the default flipped on 2026-09-30, an already-running twin is the ordinary case.
    `start-instances` on a
    `running` instance is a no-op that answers 200, so the step is correct without asking; the one
    state it cannot start from is `stopping`, which a previous run's own `stop-staging` leaves
    behind for a minute -- so a refused call is retried rather than fatal."""
    run = step_named("deploy-staging", "Start the twin")["run"]
    assert "for attempt in $(seq 1 6); do" in run
    assert "the box is most likely still stopping" in run
    assert "would not accept a start in one minute" in run


def test_the_wait_asserts_no_transition_so_a_box_that_was_already_up_passes_at_once():
    """"Is it up" is answered by asking the box to do something. Nothing in the loop compares a
    before-state with an after-state, so a twin that has been running for a week passes on its
    first attempt instead of waiting for a boot that already happened."""
    run = step_named("deploy-staging", "Wait for the twin")["run"]
    assert "PreviousState" not in run and "pending" not in run
    assert "aws ssm send-command" in run and "get-command-invocation" in run
