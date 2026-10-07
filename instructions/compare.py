"""`COMPARE`: keel-cloud's deterministic engine, shelled at zero spend (spec 029 FR-018, research
R3, `contracts/screen-shapes.md` §5; `MARKS_VERSION` 9 judgement call 34).

**An engine shim, not an engine.** The eval builds the engine's input from corpus revision 3 and
nothing else, hands it to keel-cloud's own `screenContracts compare <in> <out>` -- the exporter's
and the validator's sibling, same Gradle task, same `cwd`, same refusal discipline as
`contract.export` and `validate.run` -- keeps both files in the bundle, and **diffs** the output
against `expected`. This repository keeps no copy of the compare arithmetic (`runs/DRIFT.md`
#33/#36/#41/#44/#45), for `DRY=1` or for anything: a Python port would be the ruler certifying
itself.

**Marked** (call 34): per dimension, `status` and `drift` together (25 checks); per vector,
`verdict` and `deciding` together (3 checks) -- 28 an entry, 196 on seven. **Reported, never
marked** (call 3): `n`, `inside`, `outside`, `median`, `proportion`, `optionCounts`, `bar` and the
belief sentence -- a finding first.

**An engine that cannot be asked leaves the mark unmeasured, by name** (call 13): a missing
`gradlew`, a non-zero exit or an unreadable output is an `EngineUnavailable` carrying the engine's
own stderr tail and naming keel-cloud 058, and the caller records `measured: false` with that
reason -- never a zero, never a warning.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

#: The keys of `out.json` per dimension that are diffed and reported, never marked.
REPORTED_KEYS = ("n", "inside", "outside", "median", "proportion", "optionCounts", "bar",
                 "belief_sentence")

PREREQUISITE = ("keel-cloud 058's `screenContracts compare <in> <out>` (spec 029 FR-018, "
                "contracts/screen-shapes.md §5)")


class EngineUnavailable(RuntimeError):
    """keel-cloud's engine could not be asked -- the mark is unmeasured, never a score."""


@dataclass
class CompareScore:
    entry_id: str = ""
    checks: int = 0
    agreed: int = 0
    mismatches: list = field(default_factory=list)       # [{key, expected, produced}] -- marked
    reported_diffs: list = field(default_factory=list)   # [{key, field, expected, produced}]
    measured: bool = False
    reason: str | None = None

    @property
    def compare_correctness(self):
        return (self.agreed / self.checks) if (self.measured and self.checks) else None


# --------------------------------------------------------------------------------- the input

def build_input(entry, registry=None) -> dict:
    """screen-shapes §5's `in.json`, **from r3 only**: the founder's 25 calibrations (the answer,
    or `unsure`, and the chosen phrase the belief sentence is made of), the persona, the context
    slots the sentence fills, and every person's gate answer, golden anchoring and picks -- `rough`
    and `chip` preserved as written. Nothing from `expected`: that is what the output is diffed
    against."""
    registry = registry if registry is not None else entry.registry
    calibration = {}
    for key, value in (entry.founder_calibration or {}).items():
        if (value or {}).get("unsure"):
            calibration[key] = {"unsure": True}
        else:
            calibration[key] = {"answer": value.get("answer"),
                                "belief_phrase": value.get("belief_phrase")}
    return {
        "entry": entry.id,
        "market": dict(entry.market or {}),
        "registry_version": getattr(registry, "version", None),
        "context": dict(entry.context or {}),
        "persona": dict(entry.persona or {}),
        "founder_calibration": calibration,
        "answers": [{"person": p.get("person"), "recency": p.get("recency"),
                     "anchoring": p.get("anchoring"), "chip": p.get("chip"),
                     "picks": dict(p.get("picks") or {})}
                    for p in entry.answers],
    }


# --------------------------------------------------------------------------------- the engine

def run(keel_cloud: Path, entry_input: dict, in_path: Path, out_path: Path, *,
        timeout_s: float = 600.0) -> dict:
    """Writes `in.json`, shells the engine once, reads `out.json` back. Both files stay where the
    caller put them -- the bundle's `compare/` directory -- so a reading of the mark can always be
    re-done from the files the engine actually saw and wrote."""
    keel_cloud = Path(keel_cloud)
    in_path, out_path = Path(in_path), Path(out_path)
    in_path.parent.mkdir(parents=True, exist_ok=True)
    in_path.write_text(json.dumps(entry_input, indent=2, ensure_ascii=False), encoding="utf-8")
    gradlew = keel_cloud / "gradlew"
    if not gradlew.is_file():
        raise EngineUnavailable(f"no {gradlew} -- compare_correctness needs {PREREQUISITE}")
    argv = [str(gradlew), "-q", "screenContracts",
            f"--args=compare {in_path.resolve()} {out_path.resolve()}"]
    try:
        done = subprocess.run(argv, cwd=str(keel_cloud), capture_output=True, text=True,
                              timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise EngineUnavailable(f"could not run keel-cloud's engine: {exc}; needs "
                                f"{PREREQUISITE}") from exc
    if done.returncode != 0:
        tail = (done.stderr.strip() or done.stdout.strip())[-2000:]
        raise EngineUnavailable(
            f"keel-cloud's `screenContracts compare` exited {done.returncode} -- "
            f"compare_correctness is UNMEASURED until {PREREQUISITE} is on the checked-out "
            f"branch.\n{tail}")
    try:
        produced = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EngineUnavailable(f"the engine exited 0 but {out_path} is not readable JSON: "
                                f"{exc}") from exc
    if not isinstance(produced, dict):
        raise EngineUnavailable(f"{out_path} is not a JSON object")
    return produced


# ----------------------------------------------------------------------------------- the diff

def _drift(value):
    return None if value in (None, "") else str(value).lower()


def diff(expected: dict, produced: dict, *, entry=None, entry_id: str = "") -> CompareScore:
    """The engine's output against r3's `expected`: 25 + 3 marked checks, the rest reported.

    A dimension is one check: `status` and `drift` both equal (a missing drift on either side is
    `null`). A vector is one check: `verdict` and `deciding` both equal. A dimension or vector the
    engine left out is a mismatch, not a skip.
    """
    score = CompareScore(entry_id=entry_id or getattr(entry, "id", ""), measured=True)
    expected = expected or {}
    produced = produced or {}
    want_standings = expected.get("standings") or {}
    got_standings = produced.get("standings") or {}
    calibration = getattr(entry, "founder_calibration", {}) or {}
    for key, want in want_standings.items():
        got = got_standings.get(key) or {}
        score.checks += 1
        pair_want = (want.get("status"), _drift(want.get("drift")))
        pair_got = (got.get("status"), _drift(got.get("drift")))
        if pair_want == pair_got:
            score.agreed += 1
        else:
            score.mismatches.append({"key": key, "expected": {"status": pair_want[0],
                                                              "drift": pair_want[1]},
                                     "produced": {"status": pair_got[0], "drift": pair_got[1]}})
        for name in REPORTED_KEYS:
            want_value = want.get(name)
            if name == "belief_sentence" and want_value is None:
                want_value = (calibration.get(key) or {}).get("belief_sentence")
            got_value = got.get(name)
            if want_value is None and got_value is None:
                continue
            if want_value != got_value:
                score.reported_diffs.append({"key": key, "field": name,
                                             "expected": want_value, "produced": got_value})
    want_verdicts = expected.get("vector_verdicts") or {}
    got_verdicts = produced.get("vector_verdicts") or {}
    for vector, want in want_verdicts.items():
        got = got_verdicts.get(vector) or {}
        score.checks += 1
        if (want.get("verdict"), want.get("deciding")) == (got.get("verdict"), got.get("deciding")):
            score.agreed += 1
        else:
            score.mismatches.append({"key": vector,
                                     "expected": {"verdict": want.get("verdict"),
                                                  "deciding": want.get("deciding")},
                                     "produced": {"verdict": got.get("verdict"),
                                                  "deciding": got.get("deciding")}})
    return score


def unmeasured(entry_id: str, reason: str) -> CompareScore:
    """The score of an entry whose engine could not be asked: no checks, `measured: false`."""
    return CompareScore(entry_id=entry_id, measured=False, reason=reason)


def compare_entry(keel_cloud: Path, entry, registry, compare_dir: Path) -> CompareScore:
    """One entry, end to end: build, shell, diff -- or an unmeasured score naming why."""
    entry_input = build_input(entry, registry)
    compare_dir = Path(compare_dir)
    try:
        produced = run(keel_cloud, entry_input, compare_dir / f"{entry.id}.in.json",
                       compare_dir / f"{entry.id}.out.json")
    except EngineUnavailable as reason:
        return unmeasured(entry.id, str(reason))
    return diff(entry.expected, produced, entry=entry)
