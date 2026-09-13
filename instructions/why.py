"""The reason a run is paid for -- the founder's spend rule, enforced at the door.

keel-cloud `canon/designs/model-routing-design.md` §7.1 (the founder, 2026-09-13: *"we cannot
afford to run the instructions every time"*): the instruction eval runs by hand only, and only
for one of three events. A screen (`-k`, one entry) is allowed for an instruction, prompt or
contract change and for shopping a new model; the full run is allowed for a new model only, since
it is the certificate a table row lands on. A code change in the runtime or the cloud that touches
none of those earns nothing -- the nightly journey covers it. `--dry-run` needs no reason: it
spends nothing.

The reason is written into the run's `manifest.json`, so every bundle on disk says why it exists.
"""
from __future__ import annotations

SCREEN_EVENTS = ("instruction", "prompt", "contract", "new-model")
FULL_EVENTS = ("new-model",)

POLICY = (
    "the instruction eval runs by hand, for one of three events, never on a schedule\n"
    "(keel-cloud canon/designs/model-routing-design.md §7.1, the founder, 2026-09-13):\n"
    "  WHY=instruction:<file>   an inference-instruction file changed     -> a screen\n"
    "  WHY=prompt:<file>        a prompt section in keel-runtime changed  -> a screen\n"
    "  WHY=contract:<file>      a response contract changed               -> a screen\n"
    "  WHY=new-model:<host>:<model>  a table row changes                   -> the full run (or a screen first)\n"
    "a runtime or cloud change that touches none of these earns no run: the nightly journey covers it.\n"
    "DRY=1 needs no reason."
)


class NoReason(SystemExit):
    """Raised with exit status 2 and the policy on stderr."""


def check(why: str | None, *, screen: bool, dry_run: bool) -> dict | None:
    """Returns the manifest's `why` record, or raises `NoReason`."""
    if dry_run:
        return None if not why else parse(why)
    if not why:
        raise NoReason(f"instruction eval: no WHY given -- refusing to spend.\n{POLICY}")
    record = parse(why)
    allowed = SCREEN_EVENTS if screen else FULL_EVENTS
    if record["event"] not in allowed:
        kind = "a screen" if screen else "the full run"
        raise NoReason(f"instruction eval: WHY={why!r} does not earn {kind}.\n{POLICY}")
    return record


def parse(why: str) -> dict:
    event, sep, rest = why.partition(":")
    if not sep or not rest.strip():
        raise NoReason(f"instruction eval: WHY={why!r} names no subject.\n{POLICY}")
    if event not in SCREEN_EVENTS:
        raise NoReason(f"instruction eval: WHY={why!r} is not one of the three events.\n{POLICY}")
    if event == "new-model":
        host, sep2, model = rest.partition(":")
        if not sep2 or not model.strip():
            raise NoReason(f"instruction eval: WHY=new-model needs <host>:<model>.\n{POLICY}")
        return {"event": event, "host": host, "model": model}
    return {"event": event, "subject": rest}
