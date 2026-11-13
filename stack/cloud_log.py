"""Spec 154 FR-0: keel-cloud's log lines, read where the stack keeps them (`runs/.stack/cloud.log`, `stack/cloud.py`'s
`log_path`) -- the lines keel-cloud 245 / 247 / 248 / 250 write with ids only, so a journey on the local profile can say
the walk met them: *asked after the read-back: project=… dimension=… read_back=… asked=… rows=…*, *interviewer set up:
project=… role=… face=… credits=…*, *interviewer ready: project=… role=… clips=…*, *project bought: founder=… project=…
credits=1000*, *interviewer bought: founder=… project=… credits=1500*, *credits refused: founder=… needed=… balance=…*,
*call planned: project=… call=… role=…*, *call signed in: project=… call=…*, *call started: project=… call=…*,
*first-person written: project=…* / *first-person owed: project=… not written reason=…*. On the remote profile there is
no log to read and every reader answers `None`, by name -- a note, never a stop. Nothing here asserts.
"""

from __future__ import annotations

import re
from pathlib import Path

from stack.config import REPO_ROOT, StackConfig

#: The lines, by a short name, as keel-cloud writes them (ids only; never a name or an address).
LINES = {
    "asked_after_read_back": "asked after the read-back: ",
    "interviewer_set_up": "interviewer set up: ",
    "interviewer_ready": "interviewer ready: ",
    "project_bought": "project bought: ",
    "interviewer_bought": "interviewer bought: ",
    "credits_refused": "credits refused: ",
    "call_planned": "call planned: ",
    "call_signed_in": "call signed in: ",
    "call_started": "call started: ",
    "call_ended": "call ended: ",
    "call_digested": "call digested: ",
    "call_counted": "call counted: ",
    "first_person_written": "first-person written: ",
    "first_person_owed": "first-person owed: ",
}

_FIELD = re.compile(r"(\w+)=(\"[^\"]*\"|\S+)")


def path_of(config: StackConfig | None) -> Path | None:
    """keel-cloud's log on a local profile (`stack/cloud.py` writes `runs/.stack/<name>.log`, the name the profile's
    process name), or None on the remote profile."""
    if config is None or getattr(config, "is_remote", False):
        return None
    from stack.cloud import _process_name                          # noqa: PLC0415 - the one place the name is spelled
    return REPO_ROOT / "runs" / ".stack" / f"{_process_name(config)}.log"


def fields_of(line: str) -> dict:
    """`key=value` pairs after the line's colon, a quoted value unquoted."""
    tail = line.split(": ", 1)[1] if ": " in line else line
    return {k: v.strip('"') for k, v in _FIELD.findall(tail)}


def lines(config: StackConfig | None, name: str, *, project_id: str | None = None,
          since_offset: int = 0) -> list[dict] | None:
    """Every line of `name` (a key of `LINES`) in the log, newest last, each `{line, **fields}` -- `project_id`'s alone
    where given; from byte `since_offset` on (`offset()` before the step, so a journey reads only what it caused). None
    where there is no log to read (the remote profile, or a log not written yet)."""
    path = path_of(config)
    if path is None or not path.is_file():
        return None
    prefix = LINES[name]
    out = []
    with path.open("rb") as f:
        f.seek(since_offset)
        for raw in f:
            text = raw.decode("utf-8", errors="replace").rstrip("\n")
            if prefix not in text:
                continue
            row = {"line": text[text.index(prefix):], **fields_of(text[text.index(prefix):])}
            if project_id is None or row.get("project") == project_id:
                out.append(row)
    return out


def offset(config: StackConfig | None) -> int:
    """The log's size now -- handed back to `lines(since_offset=...)` so a step reads only what it caused."""
    path = path_of(config)
    return path.stat().st_size if path is not None and path.is_file() else 0
