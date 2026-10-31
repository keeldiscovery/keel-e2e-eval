"""Decided before (spec 087): the founder's decisions on what the quality cycle found, and the snooze they put on a
weak row he has already decided.

`quality/decisions.toml` is the file of record, one `[[decision]]` per decision (FR-1). This module reads it, refuses a
file that is not that shape (`load`, run by `make unit` on the file of record and by `make quality-walk` / `make
quality-advise` before anything else), and answers three questions the cycle asks of it:

- **is this weak row snoozed?** (FR-2, `split`) -- a decision matches a row when its `row` matches (scope, audience,
  dimension, screen = the row's kind; `*` any, a list a set, dimension `-` a row with none) AND its `fix` matches the
  row's fix location (`fix_matches`); it snoozes while its `until` holds (`active`): `never` always, a cycle id through
  that cycle, `spec-merged` until `merged = "<sha>"` is written on the entry.
- **what has the founder said no to on this row?** (FR-3, `declined_for`) -- the active declined decisions whose `row`
  matches the row, whatever their `fix`: their `why` goes into the adviser's prompt in full.
- **how is a snoozed row listed?** (FR-2 / FR-4, `line`) -- one line: the row, then each decision's id, its word, its
  spec on `taken`, how long it holds, and its `why`.

No model, no network: a file read and string matching.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from quality import rubric

QUALITY = Path(__file__).resolve().parent
DECISIONS_PATH = QUALITY / "decisions.toml"

#: FR-1: the fields every entry carries; `spec` is required on `taken` only, `merged` written by the coordinator.
FIELDS = ("id", "cycle", "proposals", "row", "fix", "decision", "until", "why")
OPTIONAL = ("spec", "merged")
WORDS = ("taken", "declined", "held")
UNTIL = ("spec-merged", "never")
ROW_KEYS = ("scope", "audience", "dimension", "screen")
ANY = "*"
NO_DIMENSION = "-"

#: The screens the cycle scores, by the row's `kind` (quality/table.py groups a row by it): the founder flow's screen
#: kinds as the readers name them (a founder screen `q-<dimension>` is kind `q`; the rest are their own name), and the
#: stranger's -- plus `insights`, the §G reading of a follow-up line. `make unit` holds this list to every kind the
#: committed score files carry and to quality/table.py's founder files. `context-window` is keel-web 141's 2 of 2, the
#: recall window's own page (spec 097 FR-3), the page's own words (`table.fix_location`'s *no model*). The last three
#: are spec 109's, read after everyone has answered (`rubric.AFTER_KINDS`): the study's stage page, each dimension card
#: opened with its chart, and the Insights screen -- `table.AFTER_FIX` names where each is fixed.
FOUNDER_SCREENS = ("persona", "persona-who-answers", "name", "market", "context", "context-window", "context-card",
                   "problem-seed", "problem-card", "idea", "solution-seed", "solution-card",
                   "failed-solution-calibration", "q", "answer", "check", "choose", "ready-interviewer", "ready-pilot",
                   "send-format", "send-who", "stage", "dimension", "insights-screen")
#: `condition` is the link's own screener as the walk records it (`vectors_screens.Interview._condition`, spec 076 FR-4 /
#: spec 101 FR-1: the decision-maker's, keel-web 127 FR-2), read as its own screen by the readers' catch-all -- the
#: committed money-study score files of 2026-10-30 (`083fc9a`) carry it; `screener` is the gate's own chip question.
RESPONDENT_SCREENS = ("screener", "condition", "gate", "item", "reveal", "idea", "follow_up", "insights")
SCREENS = tuple(dict.fromkeys(FOUNDER_SCREENS + RESPONDENT_SCREENS))

CYCLE_ID = re.compile(r"^\d{8}-[0-9a-f]{7,}(-\d+)?$")
DIMENSION = re.compile(r"^(problem|solution|commercial)\.[a-z_]+$")
SHA = re.compile(r"^[0-9a-f]{7,40}$")

#: The one fix location the cycle names by its category, not its file: every registry row lives in this file
#: (keel-cloud `src/main/resources/keel/dimension-registry.json`), and quality/table.py names such a row's fix
#: `registry row` (the founder guidance, the respondent wording, the follow-up ladder).
REGISTRY_FILE = "dimension-registry.json"
REGISTRY_CATEGORY = "registry row"


class DecisionsError(ValueError):
    """The decisions file is not the shape spec 087 FR-1 reads."""


def _scopes() -> tuple[str, ...]:
    from quality.cycle import SCOPES                                    # noqa: PLC0415 -- cycle imports this module
    return SCOPES


# ------------------------------------------------------------------------------------------------ FR-1 the record

def _strings(value, what: str) -> list[str] | None:
    """A field that is a string, a list of strings, or `*` (None: any)."""
    if value == ANY:
        return None
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list) and value and all(isinstance(v, str) and v.strip() for v in value):
        if ANY in value:
            raise DecisionsError(f"{what} lists `*` beside other values -- `*` stands alone")
        return [v.strip() for v in value]
    raise DecisionsError(f"{what} is {value!r} -- a string, a list of strings, or `*`")


def validate(entry: dict, n: int) -> dict:
    """One `[[decision]]`, checked (FR-1), with `_row` (key -> set or None) and `_fix` (list or None) added."""
    if not isinstance(entry, dict):
        raise DecisionsError(f"entry {n} is not a table")
    name = f"entry {n} ({entry.get('id', 'no id')})"
    missing = [f for f in FIELDS if f not in entry]
    if missing:
        raise DecisionsError(f"{name} lacks {', '.join(missing)}")
    unknown = sorted(set(entry) - set(FIELDS) - set(OPTIONAL))
    if unknown:
        raise DecisionsError(f"{name} carries {', '.join(unknown)}, which no decision has (the fields: "
                             f"{', '.join(FIELDS + OPTIONAL)})")
    if not isinstance(entry["id"], str) or not entry["id"].strip():
        raise DecisionsError(f"{name}: id must be a non-empty string")
    if not isinstance(entry["cycle"], str) or not CYCLE_ID.match(entry["cycle"]):
        raise DecisionsError(f"{name}: cycle {entry['cycle']!r} is not a cycle id (<yyyymmdd>-<cloud7>)")
    if not isinstance(entry["proposals"], list) or not all(isinstance(p, int) and p > 0 for p in entry["proposals"]):
        raise DecisionsError(f"{name}: proposals must be a list of advice numbers")
    if entry["decision"] not in WORDS:
        raise DecisionsError(f"{name}: decision {entry['decision']!r} is not one of {', '.join(WORDS)}")
    until = entry["until"]
    if not isinstance(until, str) or not (until in UNTIL or CYCLE_ID.match(until)):
        raise DecisionsError(f"{name}: until {until!r} is not one of {', '.join(UNTIL)} or a cycle id")
    if not isinstance(entry["why"], str) or not entry["why"].strip():
        raise DecisionsError(f"{name}: why must be the founder's reason, a non-empty string")
    if entry["decision"] == "taken" and "spec" not in entry:
        raise DecisionsError(f"{name}: a taken decision names the spec(s) it became (`spec`)")
    if "spec" in entry:
        _strings(entry["spec"], f"{name}: spec")
    if "merged" in entry:
        if until != "spec-merged":
            raise DecisionsError(f"{name}: merged ends a spec-merged snooze only; this one's until is {until!r}")
        if not isinstance(entry["merged"], str) or not SHA.match(entry["merged"]):
            raise DecisionsError(f"{name}: merged {entry['merged']!r} is not a sha")
    row = entry["row"]
    if not isinstance(row, dict) or set(row) != set(ROW_KEYS):
        raise DecisionsError(f"{name}: row must carry exactly {', '.join(ROW_KEYS)}; it carries "
                             f"{', '.join(sorted(row)) if isinstance(row, dict) else row!r}")
    parsed = {key: _strings(row[key], f"{name}: row.{key}") for key in ROW_KEYS}
    known = {"scope": _scopes(), "audience": rubric.AUDIENCES, "screen": SCREENS}
    for key, allowed in known.items():
        bad = [v for v in parsed[key] or [] if v not in allowed]
        if bad:
            raise DecisionsError(f"{name}: row.{key} names {', '.join(bad)}, which the cycle does not score (it scores "
                                 f"{', '.join(allowed)})")
    bad = [v for v in parsed["dimension"] or [] if v != NO_DIMENSION and not DIMENSION.match(v)]
    if bad:
        raise DecisionsError(f"{name}: row.dimension names {', '.join(bad)} -- a dimension key "
                             "(<scope>.<name>), `-` for a row with none, or `*`")
    fix = _strings(entry["fix"], f"{name}: fix")
    return {**entry, "_row": {k: (None if v is None else set(v)) for k, v in parsed.items()}, "_fix": fix}


def load(path: str | Path | None = None) -> list[dict]:
    """The decisions file, every entry checked (FR-1); no file is no decision."""
    path = Path(path or DECISIONS_PATH)
    if not path.is_file():
        return []
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except tomllib.TOMLDecodeError as reason:
        raise DecisionsError(f"{path.name} is not TOML: {reason}") from reason
    extra = sorted(set(raw) - {"decision"})
    if extra:
        raise DecisionsError(f"{path.name} carries {', '.join(extra)}; it holds `[[decision]]` entries only")
    entries = raw.get("decision") or []
    if not isinstance(entries, list):
        raise DecisionsError(f"{path.name}: `decision` must be an array of tables (`[[decision]]`)")
    out = [validate(e, i) for i, e in enumerate(entries, 1)]
    ids = [d["id"] for d in out]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        raise DecisionsError(f"{path.name}: the id {', '.join(twice)} is used twice")
    return out


# ------------------------------------------------------------------------------------------------ FR-2 the match

def _norm(text: str) -> str:
    return " ".join(str(text).lower().split())


def row_matches(decision: dict, row: dict) -> bool:
    """The decision's `row` against a weak row (`scope`, `audience`, `dimension`, `kind`): `*` any, a list a set, a
    dimension of `-` only a row with none."""
    for key, field in (("scope", "scope"), ("audience", "audience"), ("dimension", "dimension"), ("screen", "kind")):
        allowed = decision["_row"][key]
        if allowed is not None and (row.get(field) or NO_DIMENSION) not in allowed:
            return False
    return True


def fix_matches(decision: dict, fix: dict) -> bool:
    """The decision's `fix` against the row's fix location (`category`, `place`, as quality/table.py names it): `*`
    any; else one of its values is the category, or names the file or phrase the place names (whole, case and spacing
    aside), or is `dimension-registry.json` on a `registry row`. A free label for a product ask names no fix location
    the cycle writes, so it never snoozes a row -- it is listed and, when declined, read by the adviser (FR-3)."""
    values = decision["_fix"]
    if values is None:
        return True
    category, place = _norm(fix.get("category") or ""), _norm(fix.get("place") or "")
    for value in values:
        v = _norm(value)
        if v == category or (v == REGISTRY_FILE and category == REGISTRY_CATEGORY):
            return True
        if v and re.search(rf"(?<![\w.-]){re.escape(v)}(?![\w-])", place):
            return True
    return False


def active(decision: dict, cycle_id: str | None) -> bool:
    """Whether the decision's `until` still holds on this cycle: `never` always; `spec-merged` until the entry says
    `merged`; a cycle id through that cycle (records sort by name: the date, then the build)."""
    until = decision["until"]
    if until == "never":
        return True
    if until == "spec-merged":
        return not decision.get("merged")
    return cycle_id is None or cycle_id <= until


def matching(row: dict, decisions: list[dict], cycle_id: str | None) -> list[dict]:
    return [d for d in decisions if active(d, cycle_id) and row_matches(d, row) and fix_matches(d, row["fix"])]


def summary(decision: dict) -> dict:
    """What a record and an advice page keep of a decision: id, word, why, specs, until."""
    out = {"id": decision["id"], "decision": decision["decision"], "until": decision["until"],
           "why": decision["why"].strip()}
    if decision["decision"] == "taken":
        spec = decision.get("spec")
        out["spec"] = [spec] if isinstance(spec, str) else list(spec or [])
    return out


def split(rows: list[dict], decisions: list[dict], cycle_id: str | None, key) -> tuple[list[dict], list[dict]]:
    """(the rows still to advise, the snoozed ones) -- a snoozed one as `{row, weak_on, decisions}`, `key(row)` its
    name."""
    open_rows, snoozed = [], []
    for row in rows:
        found = matching(row, decisions, cycle_id)
        if found:
            snoozed.append({"row": key(row), "weak_on": list(row.get("weak_on") or []),
                            "decisions": [summary(d) for d in found]})
        else:
            open_rows.append(row)
    return open_rows, snoozed


def _until_words(d: dict) -> str:
    if d["until"] == "never":
        return "for good"
    if d["until"] == "spec-merged":
        return "until its spec is merged"
    return f"through cycle {d['until']}"


def line(snoozed: dict) -> str:
    """One line of *Decided before*: the row, then each decision that snoozes it."""
    said = []
    for d in snoozed["decisions"]:
        spec = f" ({'; '.join(d['spec'])})" if d.get("spec") else ""
        said.append(f"**{d['id']}** {d['decision']}{spec}, {_until_words(d)}: {d['why']}")
    return f"- {snoozed['row']} -- " + " / ".join(said)


# ------------------------------------------------------------------------------------------------ FR-3 the adviser

def declined_for(row: dict, decisions: list[dict], cycle_id: str | None) -> list[dict]:
    """The active declined decisions whose `row` matches this row (a `*` row matches every one), whatever their fix."""
    return [d for d in decisions if d["decision"] == "declined" and active(d, cycle_id) and row_matches(d, row)]


def _row_words(d: dict) -> str:
    def one(key):
        v = d["_row"][key]
        return "any" if v is None else ", ".join(sorted(v))
    return f"scope {one('scope')}; audience {one('audience')}; dimension {one('dimension')}; screen {one('screen')}"


def prompt_lines(declined: list[dict]) -> str:
    """The adviser's `{{declined}}`: each declined decision, its row, what was proposed, and the founder's why."""
    if not declined:
        return "(The founder has declined nothing on this row.)"
    return "\n".join(f"- {d['id']} -- on {_row_words(d)}; what was proposed: {'; '.join(d['_fix'] or ['anything'])}. "
                     f"The founder: {d['why'].strip()}" for d in declined)
