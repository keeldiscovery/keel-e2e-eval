"""Stackless: spec `013-skill-distribution`. Four packaging trees, one skill; two container beds,
two architectures, two Pythons; and one secret rule that must never soften.

Design of record: keel-cloud `canon/designs/keel-skill-design.md` §8.1 (one source, four trees,
one build), §10.1 (L2 is S-009), §10.2 (B1, the CLI stage) and §10.4 (B3, the floor stage), with
acceptance row **A-6**.

Most of these read this repository's own source. That is the only way to hold a property that
would otherwise be observable exclusively during a twenty-minute container build on a machine with
two secrets in its shell: *"no secret is baked into an image"*, *"the ambient `KEEL_BASE_URL` is
not read"* and *"`--bare` is never passed"* are properties of the files, and a property nobody can
check without spending money is a property that quietly stops holding.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from stack.config import REPO_ROOT, load_config

BED = REPO_ROOT / "stack" / "containers" / "acceptance"
DOCKERFILE = BED / "Dockerfile"
FLOOR = BED / "Dockerfile.floor"
RUNNER = BED / "run-acceptance.sh"
MAKEFILE = (REPO_ROOT / "Makefile").read_text()
S009 = REPO_ROOT / "evals" / "test_s009_skill_distribution.py"
DRIFT = (REPO_ROOT / "runs" / "DRIFT.md").read_text()


def _code(path: Path) -> str:
    """The file with its comment lines removed. Several of the rules below are about what a
    command *does*, and every one of them is also explained in a comment right above the command
    -- a grep that could not tell a citation from an invocation would forbid writing the reason
    down (spec 012 settled this same point for `--runtime-path`)."""
    return "\n".join(l for l in path.read_text().splitlines()
                      if not l.strip().startswith("#"))


# ------------------------------------------------------------------ the bed exists, as named

def test_the_three_files_the_design_names_are_the_three_files_that_exist():
    """§13 step 10: `stack/containers/acceptance/{Dockerfile,Dockerfile.floor,
    run-acceptance.sh}`."""
    assert DOCKERFILE.is_file()
    assert FLOOR.is_file()
    assert RUNNER.is_file()
    assert RUNNER.stat().st_mode & 0o111, "run-acceptance.sh must be executable"


def test_make_acceptance_exists_and_drives_the_script():
    assert re.search(r"^acceptance: venv$", MAKEFILE, re.M), "`make acceptance` is the entry point"
    assert "stack/containers/acceptance/run-acceptance.sh" in MAKEFILE
    assert re.search(r"^\.PHONY:.*\bacceptance\b", MAKEFILE, re.M)


def test_both_architectures_are_the_default_and_neither_is_hard_coded_away():
    body = RUNNER.read_text()
    assert "linux/arm64 linux/amd64" in body, (
        "§10.2: one image, run twice -- arm64 native and amd64 emulated")
    assert "--platform" in body


# ---------------------------------------------------------------- the CLI stage (B1), §10.2

def test_the_cli_stage_is_debian_12_with_node_22_and_both_host_clis():
    body = DOCKERFILE.read_text()
    assert "FROM debian:12-slim" in body, "§10.2 names the image; Debian 12 is Python 3.11"
    assert "NODE_VERSION=22" in body, "Node 22 is the floor Copilot CLI's own install page declares"
    assert "@anthropic-ai/claude-code" in body
    assert "@github/copilot" in body


def test_one_source_tree_reaches_both_hosts_skill_directories_by_copy():
    """D1, enforced by a `COPY` (T-3): two destinations, one context path, so "these are the same
    bytes" is a fact about the build rather than a promise in a comment."""
    body = DOCKERFILE.read_text()
    assert "COPY keel-connect /root/.claude/skills/keel-connect" in body
    assert "COPY keel-connect /root/.copilot/skills/keel-connect" in body


def test_the_cli_stage_prints_both_cli_versions_into_the_image():
    """T-6: a run that cannot name which host CLI it measured has measured nothing repeatable."""
    body = DOCKERFILE.read_text()
    assert "/opt/claude-version.txt" in body
    assert "/opt/copilot-version.txt" in body


# ------------------------------------------------------------- the floor stage (B3), §10.4

def test_the_floor_stage_is_debian_11_and_carries_nothing_else():
    body = _code(FLOOR)
    assert "FROM debian:11-slim" in body, "Debian 11 *is* the 3.9 floor, on a real distribution"
    assert "node" not in body.lower(), (
        "§10.4: *nothing else* -- no Node, no host CLI. A skill that needed either would have "
        "stopped being dependency-free Python that travels inside a skill")
    assert "@anthropic-ai" not in body and "@github/copilot" not in body


def test_the_floor_stage_says_why_it_reaches_for_the_archive():
    """`runs/DRIFT.md` #49: Debian 11 has left support, its security suite's Release file expired
    on 2026-09-07 and its packages are already 404. The accommodation is in the file with the
    measurement that produced it, never a bare flag."""
    body = FLOOR.read_text()
    assert "archive.debian.org" in body
    assert "Check-Valid-Until" in body
    assert "#49" in body, "an accommodation with no finding behind it is a workaround"


# ------------------------------------------------- both stages, and the two builder workarounds

def test_both_stages_put_every_copy_ahead_of_every_run():
    """`runs/DRIFT.md` #50: with the legacy builder and `--platform`, a `COPY` whose destination
    is a `RUN`-produced intermediate is rejected outright. Asserted structurally, because the
    failure it prevents only appears on the *second* architecture and reads as a Docker bug."""
    for path in (DOCKERFILE, FLOOR):
        lines = [l.strip() for l in path.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        first_run = next((i for i, l in enumerate(lines) if l.startswith("RUN ")), len(lines))
        late_copies = [l for l in lines[first_run:] if l.startswith("COPY ")]
        assert not late_copies, (
            f"{path.name}: these COPYs come after the first RUN and will fail the cross-"
            f"architecture build: {late_copies}")


def test_the_platform_is_in_the_layer_cache_key():
    """#50 again, the other half: the legacy builder's cache is not keyed by platform, so one
    architecture's green would be the other architecture's image."""
    for path in (DOCKERFILE, FLOOR):
        assert "ARG BUILD_PLATFORM" in path.read_text(), path.name
    assert "--build-arg \"BUILD_PLATFORM=$platform\"" in RUNNER.read_text()


# --------------------------------------------------------------- the secret rule (T-5), intact

def test_no_secret_is_baked_into_either_image():
    """T-5, asserted as an absence: the two names may appear in a comment, and must never appear
    in an `ENV` or an `ARG`."""
    for path in (DOCKERFILE, FLOOR):
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "ANTHROPIC_API_KEY" not in stripped, f"{path.name}: {line}"
            assert "COPILOT_GITHUB_TOKEN" not in stripped, f"{path.name}: {line}"
            assert "credentials.json" not in stripped, f"{path.name}: {line}"


def test_the_secrets_arrive_by_name_from_the_callers_shell_and_nowhere_else():
    body = _code(RUNNER)
    assert '-e "$secret"' in body, (
        "`docker run -e NAME` passes the value through by name; anything that read a file would "
        "be the fallback T-5 forbids")
    assert ".credentials.json" in RUNNER.read_text(), (
        "the skipped-half message names the file it is deliberately not reading")


def test_the_model_driven_half_is_skipped_by_name_with_a_reason_and_recorded():
    body = RUNNER.read_text()
    assert 'SKIPPED ($secret is not set in this shell)' in body
    assert 'result\\":\\"skipped' in body, (
        "the reason reaches the run record, not only the log")
    assert "model-driven.json" in body


def test_claude_is_never_invoked_with_bare_and_never_with_skip_permissions():
    """§10.2's named trap (T-2): `--bare` skips skill auto-discovery, so the run would come back a
    polite paragraph about not knowing what Keel is and it would look like a description defect.
    And `--dangerously-skip-permissions` is refused as root, which in this image the process is."""
    body = _code(RUNNER)
    assert "--permission-mode dontAsk" in body
    assert "--dangerously-skip-permissions" not in body
    assert re.search(r"claude -p[^\n]*--bare", body) is None


# ------------------------------------------------------- the ambient environment, still a lie

def test_the_bed_does_not_read_the_ambient_keel_base_url():
    """`runs/DRIFT.md` #48 and #52: this repository is worked on from shells that export
    `KEEL_BASE_URL=http://localhost:18081`. Inside a container `localhost` is the container, so an
    inherited value would point the whole bed at nothing and the failure would read as the
    skill's."""
    body = RUNNER.read_text()
    assert 'KEEL_BASE_URL="${ACCEPTANCE_BASE_URL:-http://host.docker.internal:18080}"' in body
    assert "${KEEL_BASE_URL:-" not in body, (
        "the ambient value must not be the default; `ACCEPTANCE_BASE_URL` is the override")


def test_the_bed_names_the_command_that_builds_the_trees_and_does_not_run_it():
    """The same rule as `make up`'s bundled-runtime gate: this repo owns no product code and never
    writes to a sibling repository."""
    body = _code(RUNNER)
    assert "make -C" in body and "dist" in body
    assert "$(make -C" not in body and "`make -C" not in body, (
        "the gate names the command; it does not shell it")


# ---------------------------------------------------------------------- S-009 itself, and dist

def test_the_dist_path_is_the_sibling_repos_own_built_trees():
    config = load_config(REPO_ROOT / "absent.toml", validate=False)
    assert config.skill_dist_path == config.keel_connect_skill / "dist"
    assert replace(config, profile="playground").skill_dist_path == config.skill_dist_path, (
        "which packaging trees exist is a fact about the sibling, not about a profile")


def test_s009_exists_is_not_live_and_installs_all_four_trees():
    body = S009.read_text()
    assert "pytestmark = pytest.mark.live" not in body, (
        "the two named LLM exceptions do not change in number or in name (AGENTS.md)")
    for tree in ("plugin", "bare", "copilot-repo", "speckit"):
        assert f'"{tree}"' in body, tree
    assert "install.sh" in body, "the one tree with a real installer is installed by running it"
    assert ".claude/skills" in body.replace('"', "") or '.claude' in body
    assert ".github" in body and ".specify" in body


def test_s009_hands_no_tree_a_checkout():
    body = S009.read_text()
    assert '"--runtime-path"' not in body
    assert "scrubbed_env" in body, (
        "T-1: with no KEEL_RUNTIME_PATH anywhere, a runtime that answers can only be the one "
        "that travelled inside the installed tree")


def test_s009_asserts_one_shape_across_the_four_trees():
    """L1's assertion, on the far side of an install (§10.1)."""
    body = S009.read_text()
    assert "_shape(body)" in body
    assert "one contract, four trees, one" in body
    assert "PER_CALL_KEYS" in body, (
        "the keys that name *this call* rather than *this skill* are listed, so 'identical' is a "
        "claim about the shape and not an accident of caching")


def test_s009_records_the_pre_approval_gap_rather_than_asserting_it_away():
    """`runs/DRIFT.md` #51: before approval there is a live runtime and no heartbeat, so the door
    out answers `not_running`. S-009 asserts what it observed and cites the entry."""
    body = S009.read_text()
    assert 'body["outcome"] == "not_running"' in body
    assert "#51" in body
    assert "SIGTERM" in body, (
        "and it cleans up the processes it started, by the pid the contract handed it -- a "
        "referee that leaked four of them a run would be worse than the gap it found")


def test_the_four_findings_are_in_the_ledger():
    for number in (49, 50, 51, 52):
        assert re.search(r"^## %d\. " % number, DRIFT, re.M), (
            f"spec 013's finding #{number} is not in runs/DRIFT.md")
