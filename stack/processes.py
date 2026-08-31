"""Process lifecycle for the two spawned pieces (gradle, vite): start in their own process group,
record the pgid so `make down` can reliably kill the whole tree, and poll-based health gates
(research.md §3-4).
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import time
from pathlib import Path

import requests

from stack.config import REPO_ROOT

PID_DIR = REPO_ROOT / "runs" / ".stack"


class HealthGateTimeout(RuntimeError):
    """A spawned process never answered its health check within budget."""


class PortTaken(RuntimeError):
    """A fixed port this stack needs is already owned by something else."""


def _pid_file(name: str) -> Path:
    return PID_DIR / f"{name}.pid"


def spawn(name: str, cmd: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> int:
    """Starts `cmd` in its own session/process group, recording the pgid in runs/.stack/<name>.pid.

    Returns the pgid (== pid, since start_new_session makes the child both session leader and
    process-group leader). The caller's stdout/stderr are redirected to `log_path` so a failed
    boot leaves something to read.
    """
    PID_DIR.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "ab")
    process = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _pid_file(name).write_text(str(process.pid))
    return process.pid


def is_running(name: str) -> bool:
    pid_file = _pid_file(name)
    if not pid_file.exists():
        return False
    try:
        pgid = int(pid_file.read_text().strip())
    except ValueError:
        return False
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def killpg_by_name(name: str, *, wait_s: float = 8.0) -> None:
    """Idempotent: no-op if the pidfile is absent or the group is already gone."""
    pid_file = _pid_file(name)
    if not pid_file.exists():
        return
    try:
        pgid = int(pid_file.read_text().strip())
    except ValueError:
        pid_file.unlink(missing_ok=True)
        return
    _killpg(pgid, wait_s=wait_s)
    pid_file.unlink(missing_ok=True)


def _killpg(pgid: int, *, wait_s: float) -> None:
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        return
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        except PermissionError:
            # The pgid no longer names a process we can signal at all -- most likely SIGTERM
            # already reaped it and the OS has since recycled the pid for something we don't
            # own. Either way, there is nothing further this process can do about it: treat it
            # as gone rather than looping until `wait_s` expires and then trying (and failing
            # the same way) to SIGKILL it.
            return
        time.sleep(0.2)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def teardown_all_processes(profile: str = "eval") -> None:
    """Kills every recorded process group for `profile` -- safe to call on a half-up stack.

    Split-stacks (relay-design.md §12.5): `cloud`/`web`'s pid-file stems are profile-suffixed
    for the playground profile (`cloud-playground`/`web-playground`, see stack/cloud.py and
    stack/web.py) precisely so an eval `make down` globbing this same `PID_DIR` cannot also kill
    a playground stack's own JVM/vite processes -- each profile only ever tears down its own two
    names, never the other profile's.
    """
    if not PID_DIR.exists():
        return
    names = ("cloud", "web") if profile == "eval" else ("cloud-playground", "web-playground")
    for name in names:
        killpg_by_name(name)


# ------------------------------------------------------------------------------- health gates

def port_owner_hint(port: int) -> str:
    """Best-effort description of whatever already holds a port, for a fail-fast message."""
    try:
        out = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [line for line in out.stdout.splitlines() if line and not line.startswith("COMMAND")]
        if lines:
            return lines[0]
    except (OSError, subprocess.SubprocessError):
        pass
    return "an unknown process"


def is_port_open(port: int, host: str = "localhost") -> bool:
    """Dual-stack aware: on this machine, vite (Node) binds "localhost" to IPv6 (::1) only, while
    a hardcoded AF_INET socket only ever tries 127.0.0.1 and reports the port as free when it is
    not -- exactly the gap that made the attach-or-boot fixture re-boot an already-up stack and
    then fail on "port already in use". `socket.create_connection` resolves "localhost" through
    `getaddrinfo` and tries every address family it returns, the same way `requests` (and a real
    browser) do.
    """
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def require_port_free(port: int, label: str) -> None:
    if is_port_open(port):
        raise PortTaken(
            f"port {port} ({label}) is already in use by {port_owner_hint(port)} -- "
            f"keel-e2e-eval's ports are fixed (55432/18080/5173) and must be free before "
            f"`make up` boots this stack."
        )


def wait_for_http(url: str, timeout_s: float, *, method: str = "GET",
                   ok_statuses: set[int] | None = None) -> None:
    """Polls `url` until it answers with anything but connection-refused (research.md §4): a
    stack still cold-starting refuses the connection outright; once it answers at all -- even a
    404 or 500 -- the process is up and serving HTTP, which is all a boot gate needs to know.

    If `ok_statuses` is given, the gate additionally requires the status to be one of them.
    """
    deadline = time.monotonic() + timeout_s
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = requests.request(method, url, timeout=3)
            if ok_statuses is None or response.status_code in ok_statuses:
                return
            last_error = RuntimeError(f"got HTTP {response.status_code} from {url}")
        except requests.exceptions.RequestException as exc:
            last_error = exc
        time.sleep(1)
    raise HealthGateTimeout(
        f"{url} never answered within {timeout_s:.0f}s -- last error: {last_error}"
    )
