#!/usr/bin/env bash
# B1 and B3, driven: build the two acceptance images for both architectures, and run what can be
# run tonight against the eval stack on the host.
#
# keel-cloud `canon/designs/keel-skill-design.md` §10.2 (B1) and §10.4 (B3, the floor stage).
# Invoked by `make acceptance`; runnable on its own with the same environment.
#
#   PLATFORMS="linux/arm64 linux/amd64"    which architectures (default: both)
#   ACCEPTANCE_BASE_URL=http://host.docker.internal:18080
#                                          the Keel *inside the container*; the host's eval stack.
#                                          Deliberately **not** `KEEL_BASE_URL`: see below.
#   SKILL_DIST=<...>/keel-connect-skill/dist/bare
#                                          the build context: the tree `make dist` wrote
#   SKIP_BUILD=1                           reuse images already tagged (a rerun of the checks)
#
# ---------------------------------------------------------------------------------------------
# **Two halves, and only one of them can run without a secret.**
#
# The *stackless half* is the skill's own script, inside the container, against the eval stack on
# the host: no model, no host CLI, no money. It always runs, on every image and every
# architecture, and it is what proves the thing B1 exists to prove -- that a copied skill still
# works after an installer moved it, on a machine with no checkout anywhere.
#
# The *model-driven half* is `claude -p "keel connect"` and `copilot -p "keel connect"`, and it
# needs `ANTHROPIC_API_KEY` / `COPILOT_GITHUB_TOKEN` from the caller's own shell. **No secret is
# ever baked into an image, read out of a file, or looked for anywhere but the environment**
# (T-5). When one is unset, that host's half is **skipped with its reason named** and the reason
# is written into the run record -- never quietly passed, and never worked around.
#
# The design writes this as *"`make acceptance` refuses to start when either is unset rather than
# falling back to a file"*. This script keeps the second clause exactly and softens the first, on
# purpose: refusing to start would make the stackless half -- the half that needs nothing and
# proves the most -- unrunnable on any machine without both secrets, which is every machine this
# repository has ever been run on. Refusing *the half that needs the secret*, by name, is the same
# discipline applied one level down. A run whose record says `SKIPPED (ANTHROPIC_API_KEY is not
# set)` is not a green run of B1; the record says so in those words.
# ---------------------------------------------------------------------------------------------

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PLATFORMS="${PLATFORMS:-linux/arm64 linux/amd64}"
# **The ambient `KEEL_BASE_URL` is deliberately not read** (`runs/DRIFT.md` #48, and #52). This
# repository is worked on from shells that export it -- the founder's own keel-connect-playground
# environment exports `KEEL_BASE_URL=http://localhost:18081`, and it was set in the shell that ran
# this bed's own first pass. Inside a container `localhost` is the container, so an inherited
# value would have pointed the whole bed at nothing and the failure would have read as the skill's.
# The override is `ACCEPTANCE_BASE_URL`, which nobody's shell exports by accident.
KEEL_BASE_URL="${ACCEPTANCE_BASE_URL:-http://host.docker.internal:18080}"
SKILL_DIST="${SKILL_DIST:-$REPO_ROOT/../keel-connect-skill/dist/bare}"
SKIP_BUILD="${SKIP_BUILD:-0}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$REPO_ROOT/runs/${STAMP}-acceptance"
mkdir -p "$RUN_DIR"
LOG="$RUN_DIR/acceptance.log"
RESULTS="$RUN_DIR/results"
mkdir -p "$RESULTS"

say() { printf '%s\n' "$*" | tee -a "$LOG"; }

say "[acceptance] run bundle: $RUN_DIR"
say "[acceptance] platforms:  $PLATFORMS"
say "[acceptance] base URL:   $KEEL_BASE_URL  (inside the container)"
say "[acceptance] skill tree: $SKILL_DIST"

# ---------------------------------------------------------------------------- gates, named early

if ! command -v docker >/dev/null 2>&1; then
  say "[acceptance] FAILED: no docker on PATH. Both beds are containers."
  exit 1
fi

# **This repo never writes to a sibling repository** (AGENTS.md), so the four `dist/` trees are
# gated on and the command that builds them is named, exactly as `make up` gates on the bundled
# runtime rather than running `make runtime` (spec 012's own clarification).
if [ ! -f "$SKILL_DIST/keel-connect/SKILL.md" ] || \
   [ ! -f "$SKILL_DIST/keel-connect/keel_runtime/__main__.py" ]; then
  say "[acceptance] FAILED: no built skill at $SKILL_DIST."
  say "             The bed installs what \`make dist\` wrote, never a working tree. Build it in"
  say "             the repository that owns it:"
  say "                 make -C $(dirname "$(dirname "$SKILL_DIST")") dist"
  exit 1
fi

HOST_BASE_URL="$(printf '%s' "$KEEL_BASE_URL" | sed 's|host\.docker\.internal|localhost|')"
if ! curl -fsS --max-time 5 "$HOST_BASE_URL/v2/health" >/dev/null 2>&1 && \
   ! curl -fsS --max-time 5 "$HOST_BASE_URL/actuator/health" >/dev/null 2>&1 && \
   ! curl -sS --max-time 5 -o /dev/null "$HOST_BASE_URL/v2/me"; then
  say "[acceptance] FAILED: nothing answering at $HOST_BASE_URL -- run \`make up\` first."
  say "             The container reaches that same stack at $KEEL_BASE_URL."
  exit 1
fi

RUNTIME_VERSION="$(cat "$(dirname "$(dirname "$SKILL_DIST")")/RUNTIME_VERSION" 2>/dev/null || echo unknown)"
SKILL_VERSION="$(cat "$(dirname "$(dirname "$SKILL_DIST")")/VERSION" 2>/dev/null || echo unknown)"
say "[acceptance] skill VERSION $SKILL_VERSION, bundled RUNTIME_VERSION $RUNTIME_VERSION"

# ------------------------------------------------------------------------------------ the builds

build_one() {  # $1 dockerfile  $2 platform  $3 tag
  local dockerfile="$1" platform="$2" tag="$3"
  if [ "$SKIP_BUILD" = "1" ]; then
    say "[build] $tag -- SKIP_BUILD=1, reusing whatever is tagged"
    return 0
  fi
  say "[build] $tag  ($platform, $(basename "$dockerfile"))"
  # `--build-arg BUILD_PLATFORM` is not decoration: without buildx the legacy builder's cache is
  # not keyed by platform, and the second architecture silently reuses the first's layers until a
  # COPY fails. See either Dockerfile's own comment (`runs/DRIFT.md` #50).
  if docker build --platform "$platform" --build-arg "BUILD_PLATFORM=$platform" \
       -f "$dockerfile" -t "$tag" "$SKILL_DIST" >>"$LOG" 2>&1; then
    say "[build] $tag  ok"
  else
    say "[build] $tag  FAILED -- see $LOG"
    return 1
  fi
}

DF_CLI="$REPO_ROOT/stack/containers/acceptance/Dockerfile"
DF_FLOOR="$REPO_ROOT/stack/containers/acceptance/Dockerfile.floor"

BUILD_FAILURES=0
for platform in $PLATFORMS; do
  arch="${platform#linux/}"
  build_one "$DF_CLI"   "$platform" "keel-acceptance:$arch"       || BUILD_FAILURES=$((BUILD_FAILURES+1))
  build_one "$DF_FLOOR" "$platform" "keel-acceptance-floor:$arch" || BUILD_FAILURES=$((BUILD_FAILURES+1))
done

# ------------------------------------------------------- the stackless half, in every container
#
# One probe, written in Python because Python is the one thing both images are guaranteed to have
# -- that is the whole claim the skill makes. It is kept to 3.9 syntax for the floor stage, which
# *is* Python 3.9: a probe that could not run there would be the failure it was written to detect.
#
# It prints exactly one line of JSON, which is the same discipline the contract it is testing
# holds itself to.

read -r -d '' PROBE <<'PYEOF' || true
import json, os, platform, subprocess, sys, tempfile

SKILL = "/opt/keel-connect"
out = {
    "python": "%d.%d.%d" % sys.version_info[:3],
    "machine": platform.machine(),
    "os_release": "",
    "skill_present": os.path.isfile(os.path.join(SKILL, "SKILL.md")),
    "bundled_runtime_present": os.path.isfile(
        os.path.join(SKILL, "keel_runtime", "__main__.py")),
    "ambient": {},
    "status": None,
    "connect": None,
    "home": {},
    "errors": [],
}
try:
    with open("/etc/os-release") as fh:
        for line in fh:
            if line.startswith("PRETTY_NAME="):
                out["os_release"] = line.split("=", 1)[1].strip().strip('"')
except (IOError, OSError):
    pass

# T-1, in the place it matters most: an image that named a checkout or a home would be measuring
# a path no founder is ever on.
for name in ("KEEL_RUNTIME_PATH", "KEEL_HOME", "KEEL_BASE_URL"):
    out["ambient"][name] = os.environ.get(name)


def one_json_line(argv, env=None, timeout=90):
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, universal_newlines=True)
    stdout, stderr = proc.communicate()
    lines = [l for l in stdout.strip().splitlines() if l.strip()]
    body = {"_exit_code": proc.returncode, "_lines": len(lines)}
    if not lines:
        body["_stderr"] = stderr[-800:]
        return body
    try:
        parsed = json.loads(lines[-1])
    except ValueError:
        body["_stdout"] = stdout[-800:]
        body["_stderr"] = stderr[-800:]
        return body
    parsed["_exit_code"] = proc.returncode
    parsed["_lines"] = len(lines)
    return parsed


# 1. the runtime that travelled answers `status`, with the four keys spec 004 added.
probe_home = tempfile.mkdtemp(prefix="keel-probe-")
env = dict(os.environ)
env["PYTHONPATH"] = SKILL + os.pathsep + env.get("PYTHONPATH", "")
env["PYTHONSAFEPATH"] = "1"
out["status"] = one_json_line(
    [sys.executable, "-m", "keel_runtime", "status", "--home", probe_home], env=env)

# 2. the skill's own script, with **no** --base-url: the address comes from KEEL_BASE_URL alone,
#    which is the founder's own path, and the home therefore follows it (design §6.3).
out["connect"] = one_json_line(
    [sys.executable, os.path.join(SKILL, "scripts", "keel_connect_check.py"),
     "--executor", "scripted", "--credential-backend", "file",
     "--no-browser", "--wait-seconds", "25"])

# 3. the derived home is `~/.keel/<host-slug>/`, and there is nothing loose at `~/.keel` itself.
keel_root = os.path.join(os.path.expanduser("~"), ".keel")
if os.path.isdir(keel_root):
    entries = sorted(os.listdir(keel_root))
    out["home"]["keel_root_entries"] = entries
    out["home"]["derived_dirs"] = [e for e in entries
                                   if os.path.isdir(os.path.join(keel_root, e))]
    out["home"]["loose_files"] = [e for e in entries
                                  if os.path.isfile(os.path.join(keel_root, e))]
    for d in out["home"]["derived_dirs"]:
        out["home"][d] = sorted(os.listdir(os.path.join(keel_root, d)))
else:
    out["home"]["keel_root_entries"] = None

# 4. and the door out, so nothing detached is left polling a stack that is about to go away.
out["disconnect"] = one_json_line(
    [sys.executable, os.path.join(SKILL, "scripts", "keel_disconnect.py")])

sys.stdout.write(json.dumps(out) + "\n")
PYEOF

STACKLESS_FAILURES=0
STACKLESS_RUN=0

probe_one() {  # $1 tag  $2 platform  $3 label
  local tag="$1" platform="$2" label="$3"
  local dest="$RESULTS/$label.json"
  say "[probe] $label  ($tag, $platform)"
  if ! printf '%s' "$PROBE" | docker run --rm -i \
        --platform "$platform" \
        --add-host host.docker.internal:host-gateway \
        -e KEEL_BASE_URL="$KEEL_BASE_URL" \
        "$tag" python3 - > "$dest" 2>>"$LOG"; then
    say "[probe] $label  FAILED to run -- see $LOG"
    STACKLESS_FAILURES=$((STACKLESS_FAILURES+1))
    return 0
  fi
  STACKLESS_RUN=$((STACKLESS_RUN+1))
  # The assertions live here, in one place, so a reader sees what a green probe means.
  if ! python3 - "$dest" "$KEEL_BASE_URL" <<'ASSERTEOF' | tee -a "$LOG"; then
import json, sys

path, base_url = sys.argv[1], sys.argv[2]
body = json.load(open(path))
expected_env = base_url.split("//", 1)[-1]
problems = []

if not body.get("bundled_runtime_present"):
    problems.append("the skill in the image carries no keel_runtime/")
for name in ("KEEL_RUNTIME_PATH", "KEEL_HOME"):
    if body["ambient"].get(name) is not None:
        problems.append("T-1: %s is set in the container (%r)" % (name, body["ambient"][name]))
if body["ambient"].get("KEEL_BASE_URL") != base_url:
    problems.append("KEEL_BASE_URL did not reach the container")

status = body.get("status") or {}
if status.get("running") is not False:
    problems.append("`keel status` on a fresh home must read running: false; got %r" % status)
for key in ("home", "base_url", "environment", "executor", "executor_on_path"):
    if key not in status:
        problems.append("`keel status` is missing %r" % key)

connect = body.get("connect") or {}
if connect.get("outcome") != "authorization_started":
    problems.append("expected authorization_started, got %r" % (connect.get("outcome"),))
for key in ("user_code", "verification_uri", "pid", "log_file", "environment"):
    if key not in connect:
        problems.append("the authorization_started shape is missing %r" % key)
if connect.get("environment") != expected_env:
    problems.append("environment reads %r, expected %r" % (connect.get("environment"), expected_env))
if connect.get("_lines") != 1:
    problems.append("the contract is exactly one line of JSON; got %r" % (connect.get("_lines"),))
if connect.get("_exit_code") != 0:
    problems.append("only internal_error exits non-zero; got %r" % (connect.get("_exit_code"),))

home = body.get("home") or {}
slug = expected_env.replace(":", "-")
dirs = home.get("derived_dirs") or []
if dirs != [slug]:
    problems.append("the home must follow the address: ~/.keel/%s/ alone, found %r" % (slug, dirs))
if home.get("loose_files"):
    problems.append("nothing belongs at ~/.keel itself; found %r" % (home["loose_files"],))

disconnect = body.get("disconnect") or {}
if disconnect.get("outcome") not in ("disconnected", "not_running", "stale_pid_cleared"):
    problems.append("the door out answered %r" % (disconnect.get("outcome"),))

print("        python %s on %s (%s)" % (body.get("python"), body.get("machine"),
                                         body.get("os_release")))
print("        connect: %s  environment: %s  home: ~/.keel/%s/"
      % (connect.get("outcome"), connect.get("environment"), slug))
print("        disconnect: %s" % (disconnect.get("outcome"),))
if problems:
    for p in problems:
        print("        FAILED: %s" % p)
    sys.exit(1)
print("        PASSED")
ASSERTEOF
    STACKLESS_FAILURES=$((STACKLESS_FAILURES+1))
  fi
}

for platform in $PLATFORMS; do
  arch="${platform#linux/}"
  probe_one "keel-acceptance:$arch"       "$platform" "cli-$arch"
  probe_one "keel-acceptance-floor:$arch" "$platform" "floor-$arch"
done

# ----------------------------------------------------------------- the model-driven half, or why not

MODEL_RECORDS="$RESULTS/model-driven.json"
model_json='{'
model_run=0

model_half() {  # $1 host  $2 secret name  $3 tag  $4 platform
  local host="$1" secret="$2" tag="$3" platform="$4"
  local value="${!secret:-}"
  local label="$host-${platform#linux/}"
  if [ -z "$value" ]; then
    local reason="SKIPPED ($secret is not set in this shell)"
    say "[model]  $label  $reason"
    say "         The design's B1 drives \`$host -p \"keel connect\"\` and asserts the reply relays"
    say "         the user code and verification URI **verbatim**, never the raw JSON. That needs a"
    say "         credential this run does not have and must not go looking for (T-5): no file, no"
    say "         keychain, no ~/.claude/.credentials.json. Set $secret in your own shell and"
    say "         re-run \`make acceptance\` to measure it."
    model_json="$model_json\"$label\":{\"result\":\"skipped\",\"reason\":\"$secret is not set in the caller's shell; no secret is read from anywhere else (T-5)\"},"
    return 0
  fi
  say "[model]  $label  running"
  model_run=$((model_run+1))
  local outfile="$RESULTS/model-$label.txt"
  local cmd
  if [ "$host" = "claude" ]; then
    # --bare must NOT be used: it skips skill auto-discovery and would make the skill invisible
    # (T-2). --permission-mode dontAsk, not --dangerously-skip-permissions, which is refused as
    # root -- which in this image the process is.
    cmd='claude -p "keel connect" --output-format json --allowedTools "Skill,Bash(python3:*)" --permission-mode dontAsk'
  else
    cmd='copilot -p "keel connect" --allow-tool "shell(python3:*)" --no-ask-user -s'
  fi
  if docker run --rm \
       --platform "$platform" \
       --add-host host.docker.internal:host-gateway \
       -e KEEL_BASE_URL="$KEEL_BASE_URL" \
       -e "$secret" \
       "$tag" sh -lc "$cmd" > "$outfile" 2>>"$LOG"; then
    if grep -qE '[A-Z0-9]{4}-[A-Z0-9]{4}' "$outfile" && grep -q 'device' "$outfile"; then
      say "[model]  $label  PASSED (a user code and a verification URI, relayed)"
      model_json="$model_json\"$label\":{\"result\":\"passed\"},"
    else
      say "[model]  $label  FAILED (no user code / verification URI in the reply)"
      model_json="$model_json\"$label\":{\"result\":\"failed\",\"reason\":\"the reply carried no user code or verification URI\"},"
    fi
  else
    say "[model]  $label  FAILED (the host CLI exited non-zero -- see $LOG)"
    model_json="$model_json\"$label\":{\"result\":\"failed\",\"reason\":\"the host CLI exited non-zero\"},"
  fi
}

FIRST_PLATFORM="$(printf '%s' "$PLATFORMS" | awk '{print $1}')"
model_half claude  ANTHROPIC_API_KEY     "keel-acceptance:${FIRST_PLATFORM#linux/}" "$FIRST_PLATFORM"
model_half copilot COPILOT_GITHUB_TOKEN  "keel-acceptance:${FIRST_PLATFORM#linux/}" "$FIRST_PLATFORM"
model_json="${model_json%,}}"
printf '%s\n' "$model_json" > "$MODEL_RECORDS"

# --------------------------------------------------------------------------------- the record

python3 - "$RUN_DIR" "$KEEL_BASE_URL" "$PLATFORMS" "$SKILL_VERSION" "$RUNTIME_VERSION" \
         "$BUILD_FAILURES" "$STACKLESS_RUN" "$STACKLESS_FAILURES" <<'RECORDEOF'
import glob, json, os, sys

run_dir, base_url, platforms, skill_v, runtime_v, builds, ran, failed = sys.argv[1:9]
results = {}
for path in sorted(glob.glob(os.path.join(run_dir, "results", "*.json"))):
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        results[name] = json.load(open(path))
    except ValueError:
        results[name] = {"unparseable": True}

record = {
    "bed": "B1 (CLI stage, Debian 12) + B3 (floor stage, Debian 11)",
    "design": "keel-cloud canon/designs/keel-skill-design.md §10.2, §10.4",
    "platforms": platforms.split(),
    "base_url_in_container": base_url,
    "skill_version": skill_v,
    "bundled_runtime_version": runtime_v,
    "build_failures": int(builds),
    "stackless": {"ran": int(ran), "failed": int(failed)},
    "halves": {
        "stackless": "ran" if int(ran) else "did not run",
        "model_driven": "see results/model-driven.json",
    },
    "results": results,
}
with open(os.path.join(run_dir, "acceptance.json"), "w") as fh:
    json.dump(record, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("[acceptance] record: %s" % os.path.join(run_dir, "acceptance.json"))
RECORDEOF

say "[acceptance] builds failed: $BUILD_FAILURES   stackless probes: $STACKLESS_RUN run, $STACKLESS_FAILURES failed"
if [ "$model_run" = "0" ]; then
  say "[acceptance] the model-driven half did not run: no ANTHROPIC_API_KEY and no COPILOT_GITHUB_TOKEN"
  say "             in this shell. Recorded as skipped, with the reason, in results/model-driven.json."
fi

if [ "$BUILD_FAILURES" != "0" ] || [ "$STACKLESS_FAILURES" != "0" ] || [ "$STACKLESS_RUN" = "0" ]; then
  say "[acceptance] FAILED"
  exit 1
fi
say "[acceptance] PASSED (stackless half)"
