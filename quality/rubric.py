"""The question-quality rubric, versioned (spec 078 FR-1).

`RUBRIC_VERSION` is to the readers what `instructions.marks.MARKS_VERSION` is to the instruction eval, and a separate
constant: the readers' ruler moving must never look like the instruction eval's moving. **Bump it for any change to a
criterion, an anchor, the two booleans, the weak rule or `score_pct`**, and say what changed and why under *Versions*
in `quality/RUBRIC.md`. Scores of two rubric versions are never averaged (`aggregate` refuses a mix).

`quality/RUBRIC.md` is the one source of the criteria: `prompt_rubric()` pastes the text between its `prompt` markers
into both readers' prompts, `prompt_spoken()` the text between its `prompt-r6` markers into the respondent-reader's
alone, and `criteria()` reads both tables back so a test holds the six rows and their anchors.

**Version 2** (spec 081, the founder 2026-10-28): R2 is judged from inside the persona (*plain to this person*: the
trade's own words are plain to them, a word of another trade is not), and **R6, said aloud**, is scored on every
respondent screen against keel-cloud's `spoken-questions-guidelines.md` §2, §3 and §5 (one wording serves the phone and
the AI interviewer, so no respondent screen is exempt); the founder-reader has no R6. A score file at version 1 is
refused by name (`RETIRED`).

**One score** (FR-4) is one JSON object a screen: `screen`, `audience`, `link`, `dimension`, `kind`, `n`, `r1`..`r6`,
`why1`..`why6`, `out_of_place`, `looks_stupid`, `instead`. The reader gives the scores, the whys and the instead line;
code derives the two booleans (`out_of_place` = R1 is 0, `looks_stupid` = R2, R4 or R6 is 0), so they can never
disagree with the scores. R4 is `None` only on a screen that shows nothing to pick (`has_options` false); R6 is a
score on every respondent screen and `None` on every founder screen -- a respondent answer without it and a founder
answer with it are refused.

**§G, the Insights grouping** (the founder, 2026-10-28): after a link's screens the respondent-reader reads each
follow-up line's grouping once -- G1 (every answer in a group a person in this job would recognise, plain names) and
G2 (junk kept out) -- recorded as `insights: [{line, dimension, link, g1, g2, whys}]` and folded into the
respondent's and the overall `score_pct`, with `insights_pct` beside.

**Version 3** (spec 109, the founder 2026-10-30: *"after everyone has answered, go back to the problem screen and the
insight screen ... and ask: does it make sense?"*): **§B, after the answers** -- the founder-reader scores the study's
stage page and each dimension card on B1-B5 and the Insights screen on B1, B3, B4, B5 and B6 (`B_OF_KIND`; kinds
`AFTER_KINDS`). A §B screen's score carries `b1`..`b6` and `why_b1`..`why_b6` and no R (`AFTER_SCORE_KEYS`); code
derives `out_of_place` = B1 is 0 and `looks_stupid` = B2 or B5 is 0. A version-2 file is set aside by the table and the
cycle, never refused (cycles 1-3 stay of record) and never compared with a version-3 one.

**The score as one number** (the coordinator's decision 2): `score_pct` = the sum of every r1..r6 and b1..b6 given over
2 x their count x 100 (a `None` R4, R6, B2 or B6 is in neither); `spoken_pct` = the same over R6 alone, beside it (spec
081 FR-4); `after_pct` the same over B alone (spec 109); `flagged_pct` = the screens with any 0 over the screens x 100.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RUBRIC_VERSION = 3

#: The rubric versions a score file is refused at, by name (spec 081 FR-1) -- never set aside, never read.
RETIRED = {1: "before spec 081: R2 judged against the general public, no R6 said aloud, no persona block"}

QUALITY_DIR = Path(__file__).resolve().parent
RUBRIC_PATH = QUALITY_DIR / "RUBRIC.md"

#: The six criteria in score order; R1-R5 both readers', R6 the respondent-reader's alone (spec 081 FR-4).
CRITERIA = ("r1", "r2", "r3", "r4", "r5", "r6")
WHYS = ("why1", "why2", "why3", "why4", "why5", "why6")
SHARED = CRITERIA[:5]
SPOKEN = "r6"
AUDIENCES = ("founder", "respondent")

#: §B (spec 109): the founder-reader's six criteria on the screens after the answers -- the stage page, each dimension
#: card opened with its chart, the Insights screen -- and which of them each kind is scored on (the Insights screen draws
#: no chart, so no B2; B6, teaches me something I did not type, is its alone).
B_CRITERIA = ("b1", "b2", "b3", "b4", "b5", "b6")
B_WHYS = ("why_b1", "why_b2", "why_b3", "why_b4", "why_b5", "why_b6")
AFTER_KINDS = ("stage", "dimension", "insights-screen")
B_OF_KIND = {"stage": B_CRITERIA[:5], "dimension": B_CRITERIA[:5],
             "insights-screen": ("b1", "b3", "b4", "b5", "b6")}
#: Every criterion a screen can carry, R then B, and each one's why key.
ALL_CRITERIA = (*CRITERIA, *B_CRITERIA)
WHY_OF = {**dict(zip(CRITERIA, WHYS)), **dict(zip(B_CRITERIA, B_WHYS))}

#: §G (the founder, 2026-10-28): the respondent-reader's two criteria on the Insights grouping of a follow-up line.
G_CRITERIA = ("g1", "g2")
INSIGHT_KEYS = ("line", "dimension", "link", "g1", "g2", "whys")

#: The founder's bar (2026-10-28): the overall score_pct over the latest file of every entry.
BAR_PCT = 90.0
#: The weak rule (design §4): a 0 on one criterion in this many entries, or a mean under WEAK_MEAN.
WEAK_ZERO_ENTRIES = 2
WEAK_MEAN = 1.5

#: The keys of one screen's score, in the order a score file writes them.
SCORE_KEYS = ("n", "screen", "audience", "link", "dimension", "kind", *CRITERIA, *WHYS,
              "out_of_place", "looks_stupid", "instead")
#: Spec 109: the keys of one §B screen's score -- the B criteria in place of the R.
AFTER_SCORE_KEYS = ("n", "screen", "audience", "link", "dimension", "kind", *B_CRITERIA, *B_WHYS,
                    "out_of_place", "looks_stupid", "instead")


def is_after(kind: str | None) -> bool:
    """Whether a screen kind is one of §B's, read after the answers (spec 109)."""
    return kind in AFTER_KINDS

_BEGIN = "<!-- prompt:begin -->"
_END = "<!-- prompt:end -->"
_R6_BEGIN = "<!-- prompt-r6:begin -->"
_R6_END = "<!-- prompt-r6:end -->"
_B_BEGIN = "<!-- prompt-b:begin -->"
_B_END = "<!-- prompt-b:end -->"


class RubricError(ValueError):
    """The rubric file, a reader's answer or a score file is not what this version reads."""


class RubricMismatch(RubricError):
    """Two rubric versions were asked to be averaged or compared: refused (FR-1)."""


# ------------------------------------------------------------------------------------------------ the file

def rubric_text(path: Path | None = None) -> str:
    path = Path(path) if path else RUBRIC_PATH
    if not path.is_file():
        raise RubricError(f"no rubric file at {path}")
    return path.read_text(encoding="utf-8")


def file_version(text: str | None = None) -> int:
    """The version RUBRIC.md says it is -- held equal to `RUBRIC_VERSION` by a unit test."""
    match = re.search(r"\*\*RUBRIC_VERSION (\d+)\*\*", text if text is not None else rubric_text())
    if not match:
        raise RubricError("RUBRIC.md does not say its RUBRIC_VERSION")
    return int(match.group(1))


def prompt_rubric(text: str | None = None) -> str:
    """The part of RUBRIC.md both readers are sent: everything between the two `prompt` markers."""
    text = text if text is not None else rubric_text()
    if text.count(_BEGIN) != 1 or text.count(_END) != 1 or text.index(_BEGIN) > text.index(_END):
        raise RubricError("RUBRIC.md must carry one `prompt:begin` marker and one `prompt:end` marker after it")
    return text.split(_BEGIN, 1)[1].split(_END, 1)[0].strip()


def prompt_spoken(text: str | None = None) -> str:
    """R6, the part only the respondent-reader is sent (spec 081 FR-4): everything between the `prompt-r6` markers."""
    text = text if text is not None else rubric_text()
    if text.count(_R6_BEGIN) != 1 or text.count(_R6_END) != 1 or text.index(_R6_BEGIN) > text.index(_R6_END):
        raise RubricError("RUBRIC.md must carry one `prompt-r6:begin` marker and one `prompt-r6:end` marker after it")
    return text.split(_R6_BEGIN, 1)[1].split(_R6_END, 1)[0].strip()


def prompt_insights(text: str | None = None) -> str:
    """§G, the part the respondent-reader is sent with each follow-up line's grouping."""
    text = text if text is not None else rubric_text()
    begin, end = "<!-- prompt-g:begin -->", "<!-- prompt-g:end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise RubricError("RUBRIC.md must carry one `prompt-g:begin` marker and one `prompt-g:end` marker")
    return text.split(begin, 1)[1].split(end, 1)[0].strip()


def prompt_after(text: str | None = None) -> str:
    """§B, the part the founder-reader is sent with every screen after the answers (spec 109): everything between the
    `prompt-b` markers."""
    text = text if text is not None else rubric_text()
    if text.count(_B_BEGIN) != 1 or text.count(_B_END) != 1 or text.index(_B_BEGIN) > text.index(_B_END):
        raise RubricError("RUBRIC.md must carry one `prompt-b:begin` marker and one `prompt-b:end` marker after it")
    return text.split(_B_BEGIN, 1)[1].split(_B_END, 1)[0].strip()


def b_criteria(text: str | None = None) -> list[dict]:
    """§B's six criteria with their anchors, in order (spec 109)."""
    rows = []
    for line in prompt_after(text).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(r"B[1-6]", cells[0]):
            name = re.match(r"\*\*(.+?)\*\*", cells[1])
            rows.append({"id": cells[0].lower(), "name": name.group(1).rstrip(".") if name else cells[1],
                         "question": cells[1], "2": cells[2], "1": cells[3], "0": cells[4]})
    if [r["id"] for r in rows] != list(B_CRITERIA):
        raise RubricError(f"RUBRIC.md's §B must carry B1..B6 in order; found {[r['id'] for r in rows]}")
    return rows


def g_criteria(text: str | None = None) -> list[dict]:
    """§G's two criteria with their anchors."""
    rows = []
    for line in prompt_insights(text).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(r"G[12]", cells[0]):
            rows.append({"id": cells[0].lower(), "question": cells[1], "2": cells[2], "1": cells[3], "0": cells[4]})
    if [r["id"] for r in rows] != list(G_CRITERIA):
        raise RubricError(f"RUBRIC.md's §G must carry G1, G2 in order; found {[r['id'] for r in rows]}")
    return rows


def criteria(text: str | None = None) -> list[dict]:
    """The six criteria with their anchors: R1-R5 off the table in the prompt part of RUBRIC.md, R6 off the table in
    its `prompt-r6` part."""
    rows = []
    for line in (prompt_rubric(text) + "\n" + prompt_spoken(text)).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(r"R[1-6]", cells[0]):
            name = re.match(r"\*\*(.+?)\*\*", cells[1])
            rows.append({"id": cells[0].lower(), "name": name.group(1).rstrip(".") if name else cells[1],
                         "question": cells[1], "2": cells[2], "1": cells[3], "0": cells[4]})
    if [r["id"] for r in rows] != list(CRITERIA):
        raise RubricError(f"RUBRIC.md's tables must carry R1..R5, then R6 in its own part; found "
                          f"{[r['id'] for r in rows]}")
    return rows


# --------------------------------------------------------------------------------------- a reader's answer

def extract_json(raw: str) -> dict:
    """The one JSON object in a reader's reply: the whole reply, else the outermost `{...}` in it (a reader that
    wraps its object in a fence or a sentence is read, not refused -- the readers carry no response contract)."""
    if raw is None:
        raise RubricError("no answer")
    text = raw.strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise RubricError(f"no JSON object in the answer: {text[:120]!r}") from None
        try:
            value = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise RubricError(f"the answer's object does not parse: {exc}") from None
    if not isinstance(value, dict):
        raise RubricError("the answer is not one JSON object")
    return value


def _mark(value, name: str, *, nullable: bool):
    if value is None and nullable:
        return None
    if isinstance(value, bool) or value not in (0, 1, 2):
        raise RubricError(f"{name} must be 0, 1 or 2{' or null' if nullable else ''}; got {value!r}")
    return int(value)


def parse_answer(raw: str, *, has_options: bool, audience: str) -> dict:
    """A reader's reply as the scores, the whys and the instead line -- or `RubricError`. The respondent-reader's
    carries R6 on every screen; the founder-reader's never does (spec 081 FR-4): either way round is refused."""
    if audience not in AUDIENCES:
        raise RubricError(f"audience {audience!r}")
    body = extract_json(raw)
    out = {}
    for crit, why in zip(SHARED, WHYS):
        nullable = crit == "r4" and not has_options
        out[crit] = _mark(body.get(crit), crit, nullable=nullable)
        out[why] = str(body.get(why) or "").strip()
    if audience == "respondent":
        if body.get(SPOKEN) is None:
            raise RubricError("r6 is missing: the respondent-reader scores R6, said aloud, on every respondent screen "
                              "(spec 081 FR-4)")
        out[SPOKEN] = _mark(body.get(SPOKEN), SPOKEN, nullable=False)
        out["why6"] = str(body.get("why6") or "").strip()
    else:
        if body.get(SPOKEN) is not None:
            raise RubricError("r6 on a founder screen: the founder-reader has no R6 (spec 081 FR-4)")
        out[SPOKEN], out["why6"] = None, ""
    out["instead"] = str(body.get("instead") or "").strip()
    return out


def parse_after(raw: str, *, kind: str) -> dict:
    """The founder-reader's reply on one §B screen (spec 109): the criteria its kind is scored on (`B_OF_KIND`), their
    whys and the instead line -- or `RubricError`. A score on a criterion the kind is not scored on (B2 on the
    Insights screen, B6 on the stage page or a card) is refused, as an R6 on a founder screen is."""
    if not is_after(kind):
        raise RubricError(f"kind {kind!r} is not read after the answers (spec 109: {', '.join(AFTER_KINDS)})")
    body = extract_json(raw)
    out = {}
    for crit, why in zip(B_CRITERIA, B_WHYS):
        if crit in B_OF_KIND[kind]:
            out[crit] = _mark(body.get(crit), crit, nullable=False)
            out[why] = str(body.get(why) or "").strip()
        elif body.get(crit) is not None:
            raise RubricError(f"{crit} on a {kind} screen: it is scored on {', '.join(B_OF_KIND[kind])} alone "
                              "(spec 109 FR-2)")
        else:
            out[crit], out[why] = None, ""
    out["instead"] = str(body.get("instead") or "").strip()
    return out


def parse_insight(raw: str) -> dict:
    """A reader's reply on one follow-up line's grouping (§G): `{g1, g2, whys: {g1, g2}}` -- or `RubricError`."""
    body = extract_json(raw)
    return {"g1": _mark(body.get("g1"), "g1", nullable=False), "g2": _mark(body.get("g2"), "g2", nullable=False),
            "whys": {"g1": str(body.get("why_g1") or "").strip(), "g2": str(body.get("why_g2") or "").strip()}}


def parse_flow(raw: str) -> dict:
    body = extract_json(raw)
    return {"order": _mark(body.get("order"), "order", nullable=False),
            "order_why": str(body.get("order_why") or "").strip(),
            "asked_twice": str(body.get("asked_twice") or "").strip(),
            "missing": str(body.get("missing") or "").strip()}


def screen_score(meta: dict, answer: dict) -> dict:
    """One screen's score object: the screen's identity, the reader's answer, the two booleans code derives. A §B
    screen (spec 109) carries the B criteria in place of the R: `out_of_place` = B1 is 0, `looks_stupid` = B2 or B5 is
    0."""
    score = {key: meta.get(key) for key in ("n", "screen", "audience", "link", "dimension", "kind")}
    if is_after(meta.get("kind")):
        for key in (*B_CRITERIA, *B_WHYS):
            score[key] = answer.get(key)
        score["out_of_place"] = score["b1"] == 0
        score["looks_stupid"] = score["b2"] == 0 or score["b5"] == 0
        score["instead"] = answer.get("instead", "")
        return {key: score[key] for key in AFTER_SCORE_KEYS}
    for key in (*CRITERIA, *WHYS):
        score[key] = answer.get(key)
    score["out_of_place"] = score["r1"] == 0
    score["looks_stupid"] = score["r2"] == 0 or score["r4"] == 0 or score.get(SPOKEN) == 0
    score["instead"] = answer.get("instead", "")
    return {key: score[key] for key in SCORE_KEYS}


def flagged(score: dict) -> bool:
    return any(score.get(c) == 0 for c in ALL_CRITERIA)


# --------------------------------------------------------------------------------------------- summaries

def summary(scores: list[dict], insights: list[dict] | None = None) -> dict:
    """The twelve means (R1-R6, then §B's B1-B6, spec 109), the zeros per criterion, `score_pct`, `spoken_pct` (R6 alone,
    spec 081 FR-4; `None` where no respondent screen is given), `after_pct` (B alone; `None` where no §B screen is given)
    and `flagged_pct` over the given screen scores -- and, when insight readings are given (§G), their two means and
    `insights_pct`, **folded into `score_pct`** by the same 2 x count arithmetic."""
    means, zeros, total, count = {}, {}, 0, 0
    for crit in ALL_CRITERIA:
        given = [s[crit] for s in scores if s.get(crit) is not None]
        means[crit] = round(sum(given) / len(given), 3) if given else None
        zeros[crit] = sum(1 for v in given if v == 0)
        total += sum(given)
        count += len(given)
    spoken = [s[SPOKEN] for s in scores if s.get(SPOKEN) is not None]
    after = [s[c] for s in scores for c in B_CRITERIA if s.get(c) is not None]
    screens = len(scores)
    flags = sum(1 for s in scores if flagged(s))
    out = {"screens": screens, "means": means, "zeros": zeros,
           "flagged": flags, "flagged_pct": round(100.0 * flags / screens, 1) if screens else None,
           "out_of_place": sum(1 for s in scores if s.get("out_of_place")),
           "looks_stupid": sum(1 for s in scores if s.get("looks_stupid")),
           "spoken_pct": round(100.0 * sum(spoken) / (2 * len(spoken)), 1) if spoken else None,
           "after_pct": round(100.0 * sum(after) / (2 * len(after)), 1) if after else None}
    if insights is not None:
        g_total, g_count, g_means, g_zeros = 0, 0, {}, {}
        for crit in G_CRITERIA:
            given = [i[crit] for i in insights if i.get(crit) is not None]
            g_means[crit] = round(sum(given) / len(given), 3) if given else None
            g_zeros[crit] = sum(1 for v in given if v == 0)
            g_total += sum(given)
            g_count += len(given)
        out.update({"insight_lines": len(insights), "insight_means": g_means, "insight_zeros": g_zeros,
                    "insights_pct": round(100.0 * g_total / (2 * g_count), 1) if g_count else None})
        total, count = total + g_total, count + g_count
    out["score_pct"] = round(100.0 * total / (2 * count), 1) if count else None
    return out


def summaries(scores: list[dict], insights: list[dict] | None = None) -> dict:
    """`summary` per audience and overall -- the block every score file carries. The insight readings (§G) are the
    respondent-reader's, so they fold into the respondent's and the overall `score_pct`, never the founder's; the §B
    screens (spec 109) are founder screens, so theirs fold into the founder's and the overall."""
    insights = list(insights or [])
    return {"founder": summary([s for s in scores if s.get("audience") == "founder"]),
            "respondent": summary([s for s in scores if s.get("audience") == "respondent"], insights),
            "overall": summary(scores, insights)}


def aggregate(files: list[dict]) -> list[dict]:
    """Every screen score of several score files -- refused when they are not all at one rubric version (FR-1)."""
    versions = {f.get("rubric_version") for f in files}
    if len(versions) > 1:
        raise RubricMismatch(f"score files at rubric versions {sorted(versions, key=str)} are never averaged "
                             "(spec 078 FR-1)")
    return [s for f in files for s in f.get("screens", [])]


def aggregate_insights(files: list[dict]) -> list[dict]:
    """Every insight reading (§G) of several score files -- refused across rubric versions, as `aggregate`."""
    aggregate(files)
    return [i for f in files for i in f.get("insights") or []]


# ------------------------------------------------------------------------------------------- a score file

HEADER_KEYS = ("entry", "scope", "bundle", "cloud_sha", "web_sha", "routing_version", "rubric_version", "reader",
               "cost_usd", "seconds", "scored_at")
#: Spec 081 FR-3 / FR-4: the version-2 header records, once, the persona block each reader was handed
#: (`{founder, respondent: {link: block}}`) and where the spoken-question guidelines R6 was read against came from.
HEADER_KEYS_V2 = ("persona", "spoken_guidelines")


def validate_file(obj: dict, *, name: str | None = None) -> dict:
    """A score file's shape, or `RubricError` naming what is missing -- the round-trip the table reads. A file at a
    retired version (`RETIRED`) is refused by name; a file at another version (not this one, not retired) is checked
    for its header alone and left for the caller to set aside, never read as this version's."""
    missing = [k for k in (*HEADER_KEYS, "screens", "summary", "flow") if k not in obj]
    if missing:
        raise RubricError(f"a score file without {missing}")
    if not isinstance(obj["rubric_version"], int):
        raise RubricError("rubric_version must be an integer")
    if obj["rubric_version"] in RETIRED:
        raise RubricError(f"{name or 'a score file'} is at rubric version {obj['rubric_version']}, "
                          f"{RETIRED[obj['rubric_version']]} -- refused; the rubric is at {RUBRIC_VERSION} and two "
                          "versions are never mixed (spec 081 FR-1): read the bundle again")
    if obj["rubric_version"] != RUBRIC_VERSION:
        return obj
    absent = [k for k in HEADER_KEYS_V2 if k not in obj]
    if absent:
        raise RubricError(f"a version-{RUBRIC_VERSION} score file without {absent} (spec 081 FR-3 / FR-4)")
    for score in obj["screens"]:
        if is_after(score.get("kind")):
            _validate_after(score)
            continue
        absent = [k for k in SCORE_KEYS if k not in score]
        if absent:
            raise RubricError(f"screen {score.get('screen')!r} has no {absent}")
        if score["audience"] not in AUDIENCES:
            raise RubricError(f"screen {score['screen']!r}: audience {score['audience']!r}")
        for crit in SHARED:
            _mark(score[crit], crit, nullable=crit == "r4")
        if score["audience"] == "respondent":
            if score[SPOKEN] is None:
                raise RubricError(f"respondent screen {score['screen']!r} has no R6 (spec 081 FR-4)")
            _mark(score[SPOKEN], SPOKEN, nullable=False)
        elif score[SPOKEN] is not None:
            raise RubricError(f"founder screen {score['screen']!r} carries an R6: the founder-reader has none "
                              "(spec 081 FR-4)")
    for reading in obj.get("insights") or []:
        absent = [k for k in INSIGHT_KEYS if k not in reading]
        if absent:
            raise RubricError(f"insight line {reading.get('line')!r} has no {absent}")
        for crit in G_CRITERIA:
            _mark(reading[crit], crit, nullable=False)
    return obj


def _validate_after(score: dict) -> None:
    """One §B screen of a version-3 file (spec 109): the founder's, its kind's B criteria each 0-2 and no other."""
    absent = [k for k in AFTER_SCORE_KEYS if k not in score]
    if absent:
        raise RubricError(f"§B screen {score.get('screen')!r} has no {absent} (spec 109)")
    if score["audience"] != "founder":
        raise RubricError(f"§B screen {score['screen']!r}: audience {score['audience']!r} -- the founder-reader reads "
                          "the screens after the answers (spec 109)")
    for crit in B_CRITERIA:
        if crit in B_OF_KIND[score["kind"]]:
            _mark(score[crit], crit, nullable=False)
        elif score[crit] is not None:
            raise RubricError(f"§B screen {score['screen']!r} ({score['kind']}) carries {crit}, which it is not scored "
                              "on (spec 109 FR-2)")


def load_file(path: Path) -> dict:
    return validate_file(json.loads(Path(path).read_text(encoding="utf-8")), name=Path(path).name)
