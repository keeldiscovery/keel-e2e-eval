"""Does the matrix turning red (or green again) need to say anything, and what (spec
`021-short-journey`; keel-cloud `canon/designs/e2e-matrix-design.md` §6.4).

**The founder asked to be told.** §6.4 named three places a verdict is recorded -- the run bundle,
the identity's label, the workflow summary -- and every one of them is somewhere a founder has to
*go and look*. A red matrix on a Sunday night is a red matrix nobody sees until Monday. So the
`summary` job opens **one** issue, titled `Matrix is red`, labelled `matrix`, and keeps using it:
a second red run comments on it rather than opening a second issue, and the first all-green run
comments *green again* and closes it.

**One issue, never a thread of them.** An issue per red run would be a mailbox; an issue that stays
open across a week of red runs, gathering one table a run, is a log. That is the whole of this
module's judgement, and it is here rather than inline in the workflow for one reason: a decision
inside a `run:` block is a decision neither `make unit` nor `actionlint` can check, and this one
has four branches and two edge cases.

**It decides; it never acts.** Nothing here opens, comments on or closes anything, and nothing
here reaches the network. The workflow's step reads the plan off stdout and does the I/O with
`gh`, holding the one token that may write issues -- so the untested half is four `gh issue` calls
with no branches of their own.

    python -m matrix.notify --red true --issue 41 --table-file table.md --run-url ... --body-out b.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

#: The one issue's title. Matched exactly when the workflow looks for an open one, so a founder
#: who renames the issue gets a new one rather than silence -- which is the safer of the two.
TITLE = "Matrix is red"

#: The label it carries, so `gh issue list --label matrix` finds it and nothing else does.
LABEL = "matrix"

#: The four things the workflow may be told to do.
ACTIONS = ("open", "comment", "close", "none")


@dataclass(frozen=True)
class Plan:
    """What the workflow should do, and the body it should do it with."""

    action: str
    title: str
    label: str
    issue: int | None
    body: str
    why: str


def _truthy(raw: object) -> bool:
    return str(raw).strip().lower() in ("1", "true", "yes", "y", "on")


def decide(*, red: bool, issue: int | None, ran_any: bool, table: str = "",
           run_url: str = "", set_name: str = "", why: str = "") -> Plan:
    """The whole decision.

    - **Red, no open issue** -> `open` one with this run's table.
    - **Red, an open issue** -> `comment` this run's table onto it. Still red, still one issue.
    - **Green, an open issue** -> `comment` *green again* and `close` it (one action, `close`,
      because the workflow does both and a plan with two verbs would need a loop).
    - **Green, no open issue** -> `none`. The ordinary morning, and it says nothing at all.

    `ran_any` is the edge case that matters: a run where **no cell produced a row** is not green.
    The cells were skipped (a failed deploy, a cancelled run, a matrix nobody enabled) and
    reporting that as *green again* would close an issue on the strength of a run that measured
    nothing. It is `none`, whatever the issue's state.
    """
    head = f"### Matrix `{set_name}`" if set_name else "### Matrix"
    tail = (f"\n\n[The run]({run_url})" if run_url else "") + (f" — {why}" if why else "")
    if not ran_any:
        return Plan(action="none", title=TITLE, label=LABEL, issue=issue, body="",
                    why="no cell produced a row, so this run measured nothing -- a run that "
                        "measured nothing is never green")
    if red:
        body = f"{head} is **red**.{tail}\n\n{table}".rstrip() + "\n"
        if issue is None:
            return Plan(action="open", title=TITLE, label=LABEL, issue=None, body=body,
                        why="the matrix is red and no issue is open for it")
        return Plan(action="comment", title=TITLE, label=LABEL, issue=issue, body=body,
                    why=f"the matrix is still red; #{issue} is already open for it")
    if issue is None:
        return Plan(action="none", title=TITLE, label=LABEL, issue=None, body="",
                    why="every cell passed and nothing was open -- the ordinary morning")
    body = (f"{head} is **green again** — every cell passed.{tail}\n\n{table}").rstrip() + "\n"
    return Plan(action="close", title=TITLE, label=LABEL, issue=issue, body=body,
                why=f"every cell passed, so #{issue} is answered and closed")


def _issue_number(raw: str | None) -> int | None:
    """The open issue's number, or `None`. The workflow hands this straight off `gh --jq`, which
    prints an empty line when it found nothing, so a blank, a dash and a zero all mean *none*."""
    text = (raw or "").strip().lstrip("#")
    if not text or not text.isdigit():
        return None
    return int(text) or None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m matrix.notify",
        description="Decide whether a matrix run should open, comment on or close the `Matrix is "
                    "red` issue (spec 021-short-journey).")
    parser.add_argument("--red", default="false", help="did any cell fail")
    parser.add_argument("--ran-any", default="true", help="did any cell produce a row")
    parser.add_argument("--issue", default="", help="the open issue's number, or empty")
    parser.add_argument("--table-file", type=Path, default=None,
                        help="the run's summary table, as markdown")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--set", dest="set_name", default="")
    parser.add_argument("--why", default="")
    parser.add_argument("--body-out", type=Path, default=None,
                        help="write the body here rather than through the shell, so a table full "
                             "of backticks and pipes never becomes an argument")
    args = parser.parse_args(argv)

    table = ""
    if args.table_file and args.table_file.is_file():
        table = args.table_file.read_text(encoding="utf-8").strip()
    plan = decide(red=_truthy(args.red), issue=_issue_number(args.issue),
                  ran_any=_truthy(args.ran_any), table=table, run_url=args.run_url,
                  set_name=args.set_name, why=args.why)
    if args.body_out is not None:
        args.body_out.write_text(plan.body, encoding="utf-8")
    print(json.dumps(asdict(plan), separators=(",", ":")))
    return 0


if __name__ == "__main__":  # pragma: no cover - the workflow's own entry point
    raise SystemExit(main(sys.argv[1:]))
