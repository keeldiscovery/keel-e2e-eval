"""The film rubric, versioned (spec 163 FR-1).

`FILM_RUBRIC_VERSION` is to the film reader what `quality.rubric.RUBRIC_VERSION` is to the question-quality readers, and
a separate constant: the film's ruler moving never looks like the questions' moving. **Bump it for any change to a
criterion, an anchor, the weak rule or `film_pct`**, and say what changed and why under *Versions* in
`quality/FILM-RUBRIC.md`. Film scores of two versions are never averaged (`aggregate` refuses a mix).

`quality/FILM-RUBRIC.md` is the one source of the criteria: `prompt_problem()` pastes the text between its
`film-problem` markers into the film reader's prompt for a problem film, `prompt_solution()` the `film-solution` part for
a solution film, `prompt_founder()` the `film-founder` part into the founder-reader's prompt for the founder's beats;
`criteria(kind)` reads each table back so a test holds the rows and their anchors.

**One film score** is one JSON object a film (`film_score`): `kind` (`problem` | `solution`), the criteria (`f1`..`f8` or
`s1`..`s9`, each 0-2), `whys` (one sentence a criterion), `missing` (a list), `instead` (one line per criterion under 2),
`film_pct` (code's, never the reader's), `flagged` (a 0 anywhere). **The founder's beats** are a list of rows (`beat`,
`said`, `r1` `r2` `r3` `r5`, their whys, `instead`) and `founder_pct` beside -- never folded into `film_pct`. **The told
card** (spec 171) is the problem film's `told` block: `t1`..`t4` (0-2), their whys, `instead`, `told_pct`, `flagged`,
`version` (`TOLD_VERSION`) -- or `absent` (the reason) with nothing scored; never folded into `film_pct`.

A **score file** (`quality/scores/<bundle>-film-<entry>.json`) is the header (`FILE_KEYS`: the entry, the bundle, the
shas, the version, the reader block, the founder-reader block, the cost and the seconds), the film's score under
`film`, the founder's beats under `founder` (`None` where the founder-reader was not run), and `frames` (the frames and
pictures the reader was handed, by path).
"""

from __future__ import annotations

import re
from pathlib import Path

from quality import rubric

FILM_RUBRIC_VERSION = 1

QUALITY_DIR = Path(__file__).resolve().parent
FILM_RUBRIC_PATH = QUALITY_DIR / "FILM-RUBRIC.md"

#: The problem film's eight criteria (FR-1), the solution film's nine, in score order.
F_CRITERIA = ("f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8")
S_CRITERIA = ("s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9")
KINDS = {"problem": F_CRITERIA, "solution": S_CRITERIA}
_MARKERS = {"problem": "film-problem", "solution": "film-solution", "founder": "film-founder", "told": "film-told"}
#: Spec 171: the told card's four criteria (the Insights tab's *On your problem* view against the strangers' stories),
#: recorded under `told` in the problem film's score file with their own version (`TOLD_VERSION`) -- never in film_pct.
T_CRITERIA = ("t1", "t2", "t3", "t4")
TOLD_VERSION = 1
#: The founder's beats: four of the question-quality rubric's criteria (FR-1, *the founder's questions*).
FOUNDER_CRITERIA = ("r1", "r2", "r3", "r5")
FOUNDER_WHYS = ("why1", "why2", "why3", "why5")

#: The weak rule -- the question-quality rubric's, held equal to it (a unit test reads both).
FILM_WEAK = {"zero_entries": rubric.WEAK_ZERO_ENTRIES, "mean_under": rubric.WEAK_MEAN}

#: The keys of one film's score, in the order a score file writes them.
FILM_SCORE_KEYS = ("kind", "scores", "whys", "missing", "instead", "film_pct", "flagged")
FOUNDER_BEAT_KEYS = ("beat", "said", *FOUNDER_CRITERIA, *FOUNDER_WHYS, "instead")
#: A score file's header (spec 163 FR-3).
FILE_KEYS = ("entry", "bundle", "cloud_sha", "web_sha", "film_rubric_version", "reader", "founder_reader",
             "cost_usd", "seconds", "scored_at", "film", "founder", "frames")


class FilmRubricError(rubric.RubricError):
    """The film rubric file, a reader's answer or a film score file is not what this version reads."""


class FilmRubricMismatch(FilmRubricError):
    """Two film rubric versions were asked to be averaged or compared: refused."""


# ------------------------------------------------------------------------------------------------ the file

def rubric_text(path: Path | None = None) -> str:
    path = Path(path) if path else FILM_RUBRIC_PATH
    if not path.is_file():
        raise FilmRubricError(f"no film rubric file at {path}")
    return path.read_text(encoding="utf-8")


def file_version(text: str | None = None) -> int:
    """The version FILM-RUBRIC.md says it is -- held equal to `FILM_RUBRIC_VERSION` by a unit test."""
    match = re.search(r"\*\*FILM_RUBRIC_VERSION (\d+)\*\*", text if text is not None else rubric_text())
    if not match:
        raise FilmRubricError("FILM-RUBRIC.md does not say its FILM_RUBRIC_VERSION")
    return int(match.group(1))


def _part(name: str, text: str | None = None) -> str:
    text = text if text is not None else rubric_text()
    begin, end = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
    if text.count(begin) != 1 or text.count(end) != 1 or text.index(begin) > text.index(end):
        raise FilmRubricError(f"FILM-RUBRIC.md must carry one `{name}:begin` marker and one `{name}:end` marker after it")
    return text.split(begin, 1)[1].split(end, 1)[0].strip()


def prompt_problem(text: str | None = None) -> str:
    """The problem film's part the film reader is sent: everything between the `film-problem` markers."""
    return _part(_MARKERS["problem"], text)


def prompt_solution(text: str | None = None) -> str:
    """The solution film's part (the other way around): everything between the `film-solution` markers."""
    return _part(_MARKERS["solution"], text)


def prompt_founder(text: str | None = None) -> str:
    """The founder's beats' part the founder-reader is sent: everything between the `film-founder` markers."""
    return _part(_MARKERS["founder"], text)


def prompt_told(text: str | None = None) -> str:
    """Spec 171: the told card's part the told-reader's card call is sent: everything between the `film-told` markers."""
    return _part(_MARKERS["told"], text)


def prompt_of(kind: str, text: str | None = None) -> str:
    if kind not in KINDS:
        raise FilmRubricError(f"film kind {kind!r} -- one of {', '.join(KINDS)}")
    return _part(_MARKERS[kind], text)


def criteria(kind: str, text: str | None = None) -> list[dict]:
    """A table's criteria with their anchors, in order: `problem` (F1-F8), `solution` (S1-S9) or `founder` (R1, R2, R3,
    R5)."""
    want = FOUNDER_CRITERIA if kind == "founder" else (T_CRITERIA if kind == "told" else KINDS.get(kind))
    if want is None:
        raise FilmRubricError(f"criteria kind {kind!r}")
    pattern = {"founder": r"R[1235]", "told": r"T[1-4]", "problem": r"F[1-8]"}.get(kind, r"S[1-9]")
    rows = []
    for line in _part(_MARKERS[kind], text).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(pattern, cells[0]):
            name = re.match(r"\*\*(.+?)\*\*", cells[1])
            rows.append({"id": cells[0].lower(), "name": name.group(1).rstrip(".") if name else cells[1],
                         "question": cells[1], "2": cells[2], "1": cells[3], "0": cells[4]})
    if tuple(r["id"] for r in rows) != tuple(want):
        raise FilmRubricError(f"FILM-RUBRIC.md's {kind} table must carry {', '.join(c.upper() for c in want)} in order; "
                              f"found {[r['id'] for r in rows]}")
    return rows


# --------------------------------------------------------------------------------------- a reader's answer

def _mark(value, name: str, *, nullable: bool):
    """`quality.rubric`'s 0-1-2 check, raised as this rubric's error."""
    try:
        return rubric._mark(value, name, nullable=nullable)
    except FilmRubricError:
        raise
    except rubric.RubricError as reason:
        raise FilmRubricError(str(reason)) from None


def _pct(values: list[int]) -> float | None:
    return round(100.0 * sum(values) / (2 * len(values)), 1) if values else None


def parse_film_answer(raw: str, *, kind: str = "problem") -> dict:
    """The film reader's reply as one film score (`FILM_SCORE_KEYS`) -- or `FilmRubricError`. Every criterion of the
    kind is scored 0-2 (none may be null: a picture that is not there is a 0 on what it had to show); `film_pct` and
    `flagged` are code's, whatever the reader said of them; an `instead` line is required for every criterion under 2
    and dropped for one at 2."""
    names = KINDS.get(kind)
    if names is None:
        raise FilmRubricError(f"film kind {kind!r} -- one of {', '.join(KINDS)}")
    try:
        body = rubric.extract_json(raw)
    except FilmRubricError:
        raise
    except rubric.RubricError as reason:
        raise FilmRubricError(str(reason)) from None
    given = body.get("scores") if isinstance(body.get("scores"), dict) else body
    whys_in = body.get("whys") if isinstance(body.get("whys"), dict) else {}
    instead_in = body.get("instead") if isinstance(body.get("instead"), dict) else {}
    scores, whys, instead = {}, {}, {}
    for crit in names:
        scores[crit] = _mark(given.get(crit), crit, nullable=False)
        whys[crit] = str(whys_in.get(crit) or body.get(f"why_{crit}") or "").strip()
        if not whys[crit]:
            raise FilmRubricError(f"{crit} has no why: every criterion is scored with one sentence of why")
        if scores[crit] < 2:
            line = str(instead_in.get(crit) or "").strip()
            if not line:
                raise FilmRubricError(f"{crit} is scored {scores[crit]} and has no instead line: one line per "
                                      "criterion under 2 (spec 163 FR-3)")
            instead[crit] = line
    extra = sorted(k for k in given if re.fullmatch(r"[fs]\d", str(k)) and k not in names)
    if extra:
        raise FilmRubricError(f"{extra} on a {kind} film: it is scored on {', '.join(names)} alone")
    missing = body.get("missing") or []
    if not isinstance(missing, list):
        raise FilmRubricError("missing must be a list (the limitations or boxes not shown)")
    return film_score(kind, scores, whys, [str(m).strip() for m in missing if str(m).strip()], instead)


def film_score(kind: str, scores: dict, whys: dict, missing: list, instead: dict) -> dict:
    values = [scores[c] for c in KINDS[kind]]
    return {"kind": kind, "scores": dict(scores), "whys": dict(whys), "missing": list(missing),
            "instead": dict(instead), "film_pct": _pct(values), "flagged": any(v == 0 for v in values)}


def parse_founder_beat(raw: str, *, beat: str, said: str) -> dict:
    """The founder-reader's reply on one of Keel's spoken lines to the founder: R1, R2, R3, R5 (0-2, each with a why)
    and the instead line -- or `FilmRubricError`. R4, R6 and R7 are not scored on a beat and refused when given."""
    try:
        body = rubric.extract_json(raw)
    except FilmRubricError:
        raise
    except rubric.RubricError as reason:
        raise FilmRubricError(str(reason)) from None
    row = {"beat": beat, "said": said}
    for crit, why in zip(FOUNDER_CRITERIA, FOUNDER_WHYS):
        row[crit] = _mark(body.get(crit), crit, nullable=False)
        row[why] = str(body.get(why) or "").strip()
    stray = [c for c in ("r4", "r6", "r7") if body.get(c) is not None]
    if stray:
        raise FilmRubricError(f"{stray} on a founder's beat: it is scored on R1, R2, R3 and R5 alone (spec 163 FR-1)")
    row["instead"] = str(body.get("instead") or "").strip()
    return {k: row[k] for k in FOUNDER_BEAT_KEYS}


def founder_summary(beats: list[dict]) -> dict:
    """`founder_pct` over the beats' R1, R2, R3, R5, the means and the zeros per criterion."""
    means, zeros, values = {}, {}, []
    for crit in FOUNDER_CRITERIA:
        given = [b[crit] for b in beats if b.get(crit) is not None]
        means[crit] = round(sum(given) / len(given), 3) if given else None
        zeros[crit] = sum(1 for v in given if v == 0)
        values += given
    return {"beats": len(beats), "means": means, "zeros": zeros, "founder_pct": _pct(values)}


# ------------------------------------------------------------------------------------------- the score file

def validate_file(obj: dict, *, name: str | None = None) -> dict:
    """A film score file's shape, or `FilmRubricError` naming what is missing. A file at another version is checked for
    its header alone and left for the caller to set aside, never read as this version's."""
    label = name or "a film score file"
    missing = [k for k in FILE_KEYS if k not in obj]
    if missing:
        raise FilmRubricError(f"{label} has no {missing}")
    if not isinstance(obj["film_rubric_version"], int):
        raise FilmRubricError(f"{label}: film_rubric_version must be an integer")
    if obj["film_rubric_version"] != FILM_RUBRIC_VERSION:
        return obj
    film = obj["film"] or {}
    absent = [k for k in FILM_SCORE_KEYS if k not in film]
    if absent:
        raise FilmRubricError(f"{label}: the film's score has no {absent}")
    names = KINDS.get(film["kind"])
    if names is None:
        raise FilmRubricError(f"{label}: film kind {film['kind']!r}")
    for crit in names:
        _mark((film["scores"] or {}).get(crit), crit, nullable=False)
    if film["film_pct"] != _pct([film["scores"][c] for c in names]):
        raise FilmRubricError(f"{label}: film_pct {film['film_pct']} is not the mean of its criteria")
    if film["flagged"] != any(film["scores"][c] == 0 for c in names):
        raise FilmRubricError(f"{label}: flagged disagrees with its scores")
    validate_told(obj.get("told"), label)
    founder = obj["founder"]
    if founder is not None:
        for row in founder.get("beats") or []:
            absent = [k for k in FOUNDER_BEAT_KEYS if k not in row]
            if absent:
                raise FilmRubricError(f"{label}: founder beat {row.get('beat')!r} has no {absent}")
            for crit in FOUNDER_CRITERIA:
                _mark(row[crit], crit, nullable=False)
    return obj


def told_pct(scores: dict) -> float | None:
    """Spec 171: the sum of T1-T4 over 2 x 4 x 100 -- None unless all four are scored."""
    values = [scores.get(c) for c in T_CRITERIA]
    return _pct(values) if all(isinstance(v, int) for v in values) else None


def validate_told(told: dict | None, label: str = "a film score file") -> None:
    """Spec 171: a score file's `told` block (absent on a file before it): an absent card scores nothing; else T1-T4
    each 0-2, each with a why, `told_pct` their mean, `flagged` on a 0."""
    if told is None:
        return
    if told.get("absent"):
        if told.get("scores") or told.get("told_pct") is not None:
            raise FilmRubricError(f"{label}: an absent told card scores nothing")
        return
    scores = told.get("scores") or {}
    for crit in T_CRITERIA:
        _mark(scores.get(crit), crit, nullable=False)
        if not str((told.get("whys") or {}).get(crit) or "").strip():
            raise FilmRubricError(f"{label}: told {crit} has no why")
    if told.get("told_pct") != told_pct(scores):
        raise FilmRubricError(f"{label}: told_pct {told.get('told_pct')} is not the mean of T1-T4")
    if bool(told.get("flagged")) != any(scores[c] == 0 for c in T_CRITERIA):
        raise FilmRubricError(f"{label}: told's flagged disagrees with its scores")


def aggregate(files: list[dict]) -> list[dict]:
    """Every film score of several score files -- refused when they are not all at one film rubric version."""
    versions = {f.get("film_rubric_version") for f in files}
    if len(versions) > 1:
        raise FilmRubricMismatch(f"film score files at film rubric versions {sorted(versions, key=str)} are never "
                                 "averaged or tabled together (spec 163 FR-1)")
    return [f["film"] for f in files]


def weak_criteria(files: list[dict]) -> list[dict]:
    """The weak rule over the latest film score of each entry: a criterion with a 0 in `zero_entries` entries or more,
    or a mean under `mean_under` -- one row a weak criterion (its kind, its zeros, its mean, the entries)."""
    aggregate(files)
    rows = []
    for kind, names in KINDS.items():
        of_kind = [f for f in files if (f.get("film") or {}).get("kind") == kind]
        for crit in names:
            given = [(f["entry"], f["film"]["scores"][crit]) for f in of_kind]
            if not given:
                continue
            zeros = [e for e, v in given if v == 0]
            mean = round(sum(v for _, v in given) / len(given), 3)
            if len(zeros) >= FILM_WEAK["zero_entries"] or mean < FILM_WEAK["mean_under"]:
                rows.append({"kind": kind, "criterion": crit, "mean": mean, "zeros": len(zeros),
                             "zero_entries": zeros, "entries": [e for e, _ in given]})
    # spec 171: the told card's T1-T4 over the entries whose problem film carries them scored
    told_files = [f for f in files if ((f.get("told") or {}).get("scores"))]
    for crit in T_CRITERIA:
        given = [(f["entry"], f["told"]["scores"][crit]) for f in told_files]
        if not given:
            continue
        zeros = [e for e, v in given if v == 0]
        mean = round(sum(v for _, v in given) / len(given), 3)
        if len(zeros) >= FILM_WEAK["zero_entries"] or mean < FILM_WEAK["mean_under"]:
            rows.append({"kind": "told", "criterion": crit, "mean": mean, "zeros": len(zeros),
                         "zero_entries": zeros, "entries": [e for e, _ in given]})
    for crit in FOUNDER_CRITERIA:
        given = []
        for f in files:
            beats = (f.get("founder") or {}).get("beats") or []
            if beats:
                given.append((f["entry"], [b[crit] for b in beats]))
        if not given:
            continue
        zeros = [e for e, vs in given if 0 in vs]
        flat = [v for _, vs in given for v in vs]
        mean = round(sum(flat) / len(flat), 3)
        if len(zeros) >= FILM_WEAK["zero_entries"] or mean < FILM_WEAK["mean_under"]:
            rows.append({"kind": "founder", "criterion": crit, "mean": mean, "zeros": len(zeros),
                         "zero_entries": zeros, "entries": [e for e, _ in given]})
    return rows


def passes(film: dict, bar_pct: float) -> bool:
    """FR-4: an entry passes at `film_pct` >= the bar with no 0."""
    return film.get("film_pct") is not None and film["film_pct"] >= bar_pct and not film.get("flagged")
