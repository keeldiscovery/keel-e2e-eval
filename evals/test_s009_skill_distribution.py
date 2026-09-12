"""S-009, four trees, one skill (spec `013-skill-distribution`).

The design of record is keel-cloud `canon/designs/keel-skill-design.md`: one source, **four
packaging trees, one build** (§8.1), and acceptance row **A-6** — *"a copied skill still works
after an installer moved it"*. §10.1 calls this layer **L2** and names the assertion it must
make: the four trees answer the **same shapes**, byte for byte, from wherever an installer put
them.

That is the whole of this scenario, and it is a different question from S-008's. S-008 asks
whether the runtime that runs is the one that travelled *inside the skill this repo has beside
it*. S-009 asks whether that is still true after `make dist` copied the skill four ways and an
installer moved one of them somewhere else — a plugin cache, a personal skills directory, a
team's `.github/`, a Spec Kit extension directory. Every one of those is a **copy**, and four
hand-maintained copies is the failure the design exists to prevent.

**What each tree is, and where it lands** (§8.1's table):

| Tree | Installed here as | The installer |
|---|---|---|
| `dist/plugin` | `<project>/.claude/skills/keel-connect` | what `claude plugin install keel@keel` unpacks: the plugin's own `skills/` directory |
| `dist/bare` | `<home>/.claude/skills/keel-connect` | **`install.sh --host claude`**, run for real |
| `dist/copilot-repo` | `<repo>/.github/skills/keel-connect` | `git pull` — a team commits the directory |
| `dist/speckit` | `<project>/.specify/extensions/keel/` | `specify extension add keel`, whose `extension.yml` is checked **structurally** here |

**Why the manifests are read but not obeyed.** Installing the plugin through `claude plugin
install` or the extension through `specify extension add` would need those two host CLIs, a
marketplace and a network — that is §10.2's containerised bed (`make acceptance`), not this
scenario. What this scenario can do without either CLI, and does, is put the bytes exactly where
each installer puts them and then run the skill from there; and read each manifest structurally,
so a tree whose manifest points at a file the install does not contain is red here rather than in
a founder's terminal.

**No `KEEL_RUNTIME_PATH`, no `--runtime-path`, no checkout** (T-1). Each installed tree is asked
to resolve its own runtime with rule 1 of the resolution order made impossible; the address comes
from `KEEL_BASE_URL` alone, exactly as a founder's does, and the only thing this scenario pins is
`--home` — because a referee may not write a credential into the founder's own `~/.keel/`
(spec 012's clarification, and the reason `stack/runtime.py` keeps setting a home at all).

Journey coverage: none of its own. §1.0's arrival is S-001's and S-008's; this scenario proves a
fact about **the four applications' packaging**, which is a question about what ships rather than
a moment in a founder's journey. `canon/CANON.md`'s ledger is not amended by it.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

from harness.browser import Auth, Connect
from harness.evidence import finalize_run
from harness.steps import Recorder
from stack import runtime as stack_runtime

#: The three things `make dist` copies into every tree, identically and byte for byte (D1, D2).
#: L1 asserts it in keel-connect-skill on every commit, against the *built* trees; S-009 asserts
#: it again on the far side of four different installers, which is the only place the claim can
#: actually fail.
SKILL_PAYLOAD = ("SKILL.md", "scripts", "keel_runtime")

#: The keys of `authorization_started` that name *this call* rather than *this skill* — a code, a
#: URL carrying that code, the pid of the process just launched, and the log it is writing. Two
#: trees answering with different values here is correct; two trees answering with a different
#: **set of keys** is the failure this scenario exists to catch.
PER_CALL_KEYS = ("user_code", "verification_uri", "pid", "log_file")

#: `already_connected`'s one moving part: the heartbeat's timestamp advances between calls. Every
#: other byte of that shape must be identical across all four trees, because all four are reading
#: one runtime through one contract.
PER_CALL_KEYS_ALREADY = ("last_heartbeat_at",)

WAIT_SECONDS = 25


def _run_script(script: Path, *, base_url: str, home: Path, args: tuple = ()) -> dict:
    """One line of JSON out of one of the four installed trees' own scripts.

    The environment is `stack.runtime.scrubbed_env` plus `KEEL_BASE_URL` — so `KEEL_RUNTIME_PATH`
    and `KEEL_HOME` are gone (T-1) and the address is named the way a founder names it, on the
    environment rather than on a flag. Nothing here passes `--runtime-path` or `--base-url`: an
    installed skill has to find its own runtime and its own Keel or it has not been installed.
    """
    env = stack_runtime.scrubbed_env({"KEEL_BASE_URL": base_url})
    completed = subprocess.run(
        [sys.executable, str(script), "--home", str(home), *args],
        capture_output=True, text=True, timeout=WAIT_SECONDS + 60, env=env)
    stdout = completed.stdout.strip()
    assert stdout, (
        f"{script} printed nothing on stdout (rc={completed.returncode}, "
        f"stderr={completed.stderr!r})")
    lines = stdout.splitlines()
    assert len(lines) == 1, (
        f"the contract is exactly one line of JSON on stdout, always; {script} printed "
        f"{len(lines)}: {lines!r}")
    body = json.loads(lines[0])
    body["_exit_code"] = completed.returncode
    return body


def _shape(body: dict) -> list:
    """The key set of a contract answer, with this harness's own bookkeeping key removed."""
    return sorted(k for k in body if k != "_exit_code")


def _install_plugin(dist: Path, workspace: Path) -> Path:
    """`claude plugin install keel@keel` unpacks the plugin and reads `skills/` inside it; the
    skill therefore arrives at a path shaped like a project's own `.claude/skills/`."""
    project = workspace / "plugin-project"
    dest = project / ".claude" / "skills" / "keel-connect"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dist / "plugin" / "skills" / "keel-connect", dest)
    return dest


def _install_bare(dist: Path, workspace: Path) -> Path:
    """The only tree with a real installer, so it is **run** rather than imitated: `install.sh
    --host claude` with a `HOME` of its own. Its own contract (§8.3, X-6) is that it copies one
    directory and edits nothing outside the destination; this scenario takes it at its word and
    then runs the skill out of where it says it put it."""
    home = workspace / "bare-home"
    home.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    completed = subprocess.run(
        [str(dist / "bare" / "install.sh"), "--host", "claude"],
        capture_output=True, text=True, timeout=120, env=env, cwd=str(workspace))
    assert completed.returncode == 0, (
        f"install.sh --host claude failed: rc={completed.returncode} "
        f"stdout={completed.stdout!r} stderr={completed.stderr!r}")
    return home / ".claude" / "skills" / "keel-connect"


def _install_copilot_repo(dist: Path, workspace: Path) -> Path:
    """The packaging with no installer at all: a team commits the directory and everyone has it
    on the next `git pull`. Installing it is copying it into a repository, which is what this
    does."""
    repo = workspace / "a-teams-repository"
    dest = repo / ".github" / "skills" / "keel-connect"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dist / "copilot-repo" / ".github" / "skills" / "keel-connect", dest)
    return dest


def _install_speckit(dist: Path, workspace: Path) -> Path:
    """`specify extension add keel` lands the extension at `.specify/extensions/keel/`, and the
    skill is the tree's own root (§8.4: `extension.yml` sits beside `SKILL.md`, `scripts/` and
    `keel_runtime/`)."""
    project = workspace / "speckit-project"
    dest = project / ".specify" / "extensions" / "keel"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dist / "speckit", dest)
    return dest


#: Name → (installer, the relative path the *installed* tree sits at, for the record).
INSTALLERS = (
    ("plugin", _install_plugin),
    ("bare", _install_bare),
    ("copilot-repo", _install_copilot_repo),
    ("speckit", _install_speckit),
)


def _tree_digest(root: Path) -> dict:
    """A path → sha256 map of the three things every tree carries, so "byte-identical" is a
    comparison rather than an adjective."""
    import hashlib

    digest = {}
    for item in SKILL_PAYLOAD:
        target = root / item
        if target.is_file():
            digest[item] = hashlib.sha256(target.read_bytes()).hexdigest()
        elif target.is_dir():
            for path in sorted(target.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    digest[str(path.relative_to(root))] = \
                        hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def test_s009_skill_distribution(stack, founder_one, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    expected_environment = f"localhost:{stack.cloud_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    workspace = Path(tempfile.mkdtemp(prefix="s009-"))
    homes = workspace / "homes"
    homes.mkdir(parents=True, exist_ok=True)
    installed: dict = {}
    started_bodies: dict = {}
    dist = stack.skill_dist_path

    try:
        # ------------------------------------------------ 0. the trees, gated and never built here
        with recorder.step("the four packaging trees exist, built by the repository that owns them",
                            party="stack", kind="assert") as h:
            present = {name: (dist / name).is_dir()
                       for name in ("plugin", "bare", "copilot-repo", "speckit")}
            version = (stack.keel_connect_skill / "VERSION").read_text().strip() \
                if (stack.keel_connect_skill / "VERSION").is_file() else None
            h.record_assert({name: True for name in present},
                             {**present, "VERSION": version,
                              "RUNTIME_VERSION": stack_runtime.bundled_runtime_version(stack)})
            missing = [name for name, ok in present.items() if not ok]
            assert not missing, (
                f"no built packaging trees at {dist} (missing {missing}). S-009 installs what "
                f"`make dist` wrote, never a working tree -- and this repo never writes to a "
                f"sibling, so build them there:\n"
                f"    make -C {stack.keel_connect_skill} dist")

        # ------------------------------------------------------- 1. four installers, four places
        for name, installer in INSTALLERS:
            with recorder.step(f"the {name} tree is installed the way its own installer installs it",
                                party="stack", kind="protocol") as h:
                root = installer(dist, workspace)
                installed[name] = root
                h.record_wire({"tree": name, "source": str(dist / name)},
                               {"installed at": str(root),
                                "carries": sorted(p.name for p in root.iterdir())})
                for item in SKILL_PAYLOAD:
                    assert (root / item).exists(), (
                        f"the installed {name} tree has no {item} at {root} -- an install that "
                        f"drops part of the skill is the failure A-6 is about")

        # ------------------------------- 2. the same bytes, on the far side of four installers
        with recorder.step("all four installed trees carry byte-identical skill, scripts and "
                            "runtime (D1, D2)", party="stack", kind="assert") as h:
            digests = {name: _tree_digest(root) for name, root in installed.items()}
            reference = digests["plugin"]
            differences = {name: sorted(set(reference.items()) ^ set(d.items()))
                           for name, d in digests.items() if d != reference}
            h.record_assert({"trees differing from the plugin tree": {}},
                             {"trees differing from the plugin tree":
                                  {k: len(v) for k, v in differences.items()},
                              "files compared": len(reference)})
            assert reference, "the plugin tree carried no files to compare"
            assert not differences, (
                f"`make dist` copies and never transforms (§8.1), so four installs of one build "
                f"must be four copies of one skill; these differ: {differences}")

        # --------------------------------------------- 3. the two manifests, read structurally
        with recorder.step("the plugin manifest parses, carries the version, and declares no "
                            "behaviour (D6, D7)", party="stack", kind="assert") as h:
            manifest = json.loads(
                (dist / "plugin" / ".claude-plugin" / "plugin.json").read_text())
            forbidden = [k for k in ("hooks", "mcpServers", "dependencies", "userConfig", "skills")
                         if k in manifest]
            h.record_assert({"version": version, "keys that would make it behave differently": []},
                             {"version": manifest.get("version"),
                              "keys that would make it behave differently": forbidden})
            assert manifest.get("version") == version, (
                f"one version, everywhere (D7): VERSION is {version!r}, plugin.json says "
                f"{manifest.get('version')!r}")
            assert not forbidden, (
                f"D6: a plugin must not behave differently from a bare drop of the same skill; "
                f"plugin.json declares {forbidden}")

        with recorder.step("the Spec Kit manifest parses, carries the version, and every path it "
                            "names resolves in the installed tree", party="stack", kind="assert") as h:
            extension = yaml.safe_load((installed["speckit"] / "extension.yml").read_text())
            declared = [entry["file"] for entry in extension["provides"]["commands"]]
            declared += [entry["file"] for entry in extension["provides"].get("scripts", [])]
            unresolved = [f for f in declared if not (installed["speckit"] / f).is_file()]
            h.record_assert({"version": version, "paths that do not resolve": []},
                             {"version": extension["extension"]["version"],
                              "declared": declared, "paths that do not resolve": unresolved})
            assert extension["schema_version"] == "1.0", extension
            assert extension["extension"]["version"] == version, (
                f"D7 again: extension.yml says {extension['extension']['version']!r}")
            assert not unresolved, (
                f"a manifest that names a file the install does not contain is a founder's "
                f"error message, not ours: {unresolved}")

        # ------------------------------ 4. every tree answers `authorization_started`, one shape
        for name, root in installed.items():
            home = homes / name
            home.mkdir(parents=True, exist_ok=True)
            with recorder.step(f"the {name} install resolves its own runtime and asks for a device "
                                "approval", party="stack", kind="assert") as h:
                body = _run_script(root / "scripts" / "keel_connect_check.py",
                                    base_url=stack.cloud_base_url, home=home,
                                    args=("--executor", "scripted", "--credential-backend", "file",
                                          "--no-browser", "--wait-seconds", str(WAIT_SECONDS)))
                started_bodies[name] = body
                h.record_wire({"tree": name, "home": str(home),
                                "KEEL_RUNTIME_PATH": None}, body)
                h.record_assert({"outcome": "authorization_started",
                                  "environment": expected_environment, "exit": 0},
                                 {"outcome": body.get("outcome"),
                                  "environment": body.get("environment"),
                                  "exit": body["_exit_code"]})
                assert body["outcome"] == "authorization_started", (
                    f"the {name} install answered {body} -- with no KEEL_RUNTIME_PATH and no "
                    f"checkout anywhere, a runtime can only have come from inside the tree")
                assert body["environment"] == expected_environment, body
                assert body["_exit_code"] == 0, body
                for key in PER_CALL_KEYS:
                    assert key in body, f"the authorization_started shape carries {key!r}: {body}"

        with recorder.step("all four answered the same `authorization_started` shape, key for key",
                            party="stack", kind="assert") as h:
            shapes = {name: _shape(body) for name, body in started_bodies.items()}
            environments = {name: body["environment"] for name, body in started_bodies.items()}
            h.record_assert({"one shape": shapes["plugin"], "one environment": expected_environment},
                             {"shapes": shapes, "environments": environments})
            assert len(set(map(tuple, shapes.values()))) == 1, (
                f"L1's assertion, on the far side of an install: one contract, four trees, one "
                f"key set. Got {shapes}")
            assert len(set(environments.values())) == 1, environments
            # And the values that *should* differ, do -- otherwise "identical" would be proving
            # nothing but that four trees answered the same cached line.
            codes = {body["user_code"] for body in started_bodies.values()}
            assert len(codes) == len(started_bodies), (
                f"four separate device authorizations must carry four separate codes; got {codes}")

        # -------------- 5. every tree carries the door out too -- and what it says before approval
        for name, root in installed.items():
            with recorder.step(f"the {name} install carries the door out as well as the door in",
                                party="stack", kind="assert") as h:
                body = _run_script(root / "scripts" / "keel_disconnect.py",
                                    base_url=stack.cloud_base_url, home=homes / name)
                h.record_wire({"tree": name,
                                "the pid `authorization_started` handed back":
                                    started_bodies[name].get("pid")}, body)
                # **`disconnected`, and this line is the evidence that closed `runs/DRIFT.md`
                # #51.** Every one of these homes has a live `keel connect` in it -- this scenario
                # was handed its pid four steps ago -- and none of them has been approved. Until
                # keel-runtime `bfc0ad6` the heartbeat was written when the runtime *connected*,
                # so before approval there was nothing on disk for the door out to find, and D1's
                # one-answer rule made that `not_running`: a founder could say "keel connect",
                # walk away from the browser, say "keel disconnect", be told nothing was running,
                # and still have a process polling. This assertion stood at `not_running` and said
                # so, so that the day the runtime's lifecycle moved it would be a *failing* line
                # rather than a silent one -- which is exactly how it was found, on
                # `runs/20260909T071411Z-s009-skill-distribution`.
                #
                # `bfc0ad6` writes the heartbeat in `state="awaiting_approval"` the instant
                # `connect` has a pid and a home. The door out now finds that runtime, signals it,
                # and proves it went: the runtime's `stopped`, which this skill renders
                # `disconnected`, carrying the pid it stopped and the signal it sent. No new
                # outcome name was needed and no contract was loosened -- keel-cloud `c317fc3`
                # amended `status-cli-output.md` to say `connected` may be false while a *present*
                # heartbeat awaits approval, and added no key. The teardown below stays as a net.
                h.record_assert({"outcome": "disconnected (the pre-approval heartbeat, DRIFT #51)"},
                                 {"outcome": body.get("outcome"),
                                  "pid": body.get("pid"),
                                  "signal": body.get("signal"),
                                  "environment": body.get("environment")})
                assert body["outcome"] == "disconnected", (
                    f"the {name} install's door out answered {body}. Since keel-runtime `bfc0ad6` "
                    f"a runtime awaiting device approval has already written its heartbeat, so "
                    f"the door out finds it and stops it; `not_running` here would mean that "
                    f"pre-approval heartbeat has regressed and `runs/DRIFT.md` #51 has reopened")
                assert body.get("pid") == started_bodies[name].get("pid"), (
                    f"and it is *this* runtime that was stopped: the door out reports pid "
                    f"{body.get('pid')}, `authorization_started` handed back "
                    f"{started_bodies[name].get('pid')}")

        # ------------------------ 6. one runtime, four readers: `already_connected`, byte for byte
        page = context.new_page()
        Auth(page, recorder, web_base).sign_in(founder_one)
        shared_home = homes / "shared"
        shared_home.mkdir(parents=True, exist_ok=True)
        first = _run_script(installed["plugin"] / "scripts" / "keel_connect_check.py",
                             base_url=stack.cloud_base_url, home=shared_home,
                             args=("--executor", "scripted", "--credential-backend", "file",
                                   "--no-browser", "--wait-seconds", str(WAIT_SECONDS)))
        with recorder.step("§1.0: an installed skill's device approval opens keel-web's own "
                            "/connect screen", party="founder", kind="assert") as h:
            h.record_wire(None, first)
            assert first["outcome"] == "authorization_started", first
            connect = Connect(page, recorder)
            frame = connect.open(first["verification_uri"])
            h.record_assert("B", frame)
            assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
        connect.approve()
        connect.wait_for_connected(timeout_s=30)

        with recorder.step("the runtime the installed skill started is the one that connected",
                            party="stack", kind="assert") as h:
            deadline = time.monotonic() + 30
            heartbeat = shared_home / stack_runtime.HEARTBEAT_FILENAME
            while not heartbeat.is_file() and time.monotonic() < deadline:
                page.wait_for_timeout(500)
            h.record_assert({"heartbeat written": True}, {"heartbeat written": heartbeat.is_file()})
            assert heartbeat.is_file(), (
                f"the approved runtime never wrote a heartbeat to {shared_home}")

        already: dict = {}
        for name, root in installed.items():
            with recorder.step(f"the {name} install reads the running runtime instead of starting "
                                "a second one", party="stack", kind="assert") as h:
                body = _run_script(root / "scripts" / "keel_connect_check.py",
                                    base_url=stack.cloud_base_url, home=shared_home,
                                    args=("--executor", "scripted", "--credential-backend", "file",
                                          "--no-browser", "--wait-seconds", str(WAIT_SECONDS)))
                already[name] = body
                h.record_wire({"tree": name}, body)
                h.record_assert({"outcome": "already_connected",
                                  "environment": expected_environment},
                                 {"outcome": body.get("outcome"),
                                  "environment": body.get("environment")})
                assert body["outcome"] == "already_connected", (
                    f"`status` is checked first, always, so a running runtime is never restarted "
                    f"-- the {name} install said {body}")
                assert body["environment"] == expected_environment, body
                assert "base_url" not in body, (
                    f"this shape lost `base_url` and gained `environment` (§7); got {body}")

        with recorder.step("four installs, one runtime, one answer -- byte for byte but the "
                            "heartbeat's own clock", party="stack", kind="assert") as h:
            def _comparable(body: dict) -> dict:
                return {k: v for k, v in body.items()
                        if k != "_exit_code" and k not in PER_CALL_KEYS_ALREADY}

            comparable = {name: _comparable(body) for name, body in already.items()}
            reference = comparable["plugin"]
            differing = {name: body for name, body in comparable.items() if body != reference}
            h.record_assert({"one answer": reference, "trees differing": {}},
                             {"answers": comparable, "trees differing": sorted(differing)})
            assert not differing, (
                f"four installs of one build, reading one runtime through one contract, must "
                f"answer the same bytes; these did not: {differing}")
            assert reference.get("agent_session_id"), reference

        with recorder.step("and the shared runtime is put away through an installed tree's own "
                            "door", party="stack", kind="assert") as h:
            body = _run_script(installed["copilot-repo"] / "scripts" / "keel_disconnect.py",
                                base_url=stack.cloud_base_url, home=shared_home)
            h.record_wire(None, body)
            h.record_assert({"outcome": "disconnected"}, {"outcome": body.get("outcome")})
            assert body["outcome"] == "disconnected", (
                f"a runtime one tree started must be stoppable from another -- one skill, four "
                f"copies: {body}")

        passed = True
    finally:
        # **Nothing detached may outlive this scenario.** Two passes, because there are two kinds
        # of runtime here and only one of them has a door.
        #
        # First the door: every home is asked to close through an installed tree's own
        # `keel_disconnect.py`, which is what a founder would do and what stops a *connected*
        # runtime with a proof it went.
        for name, root in installed.items():
            for home in (homes / name, homes / "shared"):
                script = root / "scripts" / "keel_disconnect.py"
                if script.is_file() and home.is_dir():
                    try:
                        _run_script(script, base_url=stack.cloud_base_url, home=home)
                    except Exception:  # noqa: BLE001 -- teardown never masks a real failure
                        pass
        # Then the pids -- now a **net**, not the cleanup it used to be. While `runs/DRIFT.md` #51
        # was open this loop was the only thing that stopped the four unapproved runtimes, because
        # the door out could not see them; since keel-runtime `bfc0ad6` step 5 stops them itself
        # and by the time this runs there is normally nothing left to signal. It stays because a
        # run that fails *before* step 5 -- during the installs, or the four connects -- still has
        # processes polling a device code nobody will ever approve, and a referee that left four
        # of those behind on every red run would be leaving a mess of its own making.
        for name, body in started_bodies.items():
            pid = body.get("pid")
            if not pid:
                continue
            try:
                os.kill(int(pid), signal.SIGTERM)
            except (OSError, ValueError, TypeError):
                pass
        context.close()
        shutil.rmtree(workspace, ignore_errors=True)
        finalize_run(run_dir, slug="s009-skill-distribution", facts={}, passed=passed,
                     failed_step=recorder.failed_step, duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")
