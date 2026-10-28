"""The two readers (spec 078 FR-2 - FR-4): `make read-screens RUN=<bundle> [DRY=1] [LIMIT=n] [ONLY=text]`.

A back-test bundle's `backtest.json` (spec 062 FR-4) is read as text -- every founder screen in order, and every
served respondent screen of each link -- and each screen is scored by one reader in **one call**: the founder-reader
(handed the entry's `.sources.md` whole) reads the founder screens, the respondent-reader (handed the person the walk
took on that link, their line from the sources, their role and the study's context fields) reads each link's screens.
The earlier screens of the same walk go in as one compact list, kicker and question only (the coordinator's decision
3); the screen being scored goes in full. After every screen, each reader answers the three whole-flow questions once
(the founder once, the respondent once per link). The readers never drive the UI and never see a screenshot.

**The door is the `claude` CLI, exactly as `instructions/judge.py` calls it** (`_ARGV`, `judge_env`), plus `--model`
and `--effort` from `quality/readers.toml` (the coordinator's decision 1). No key is read, named or passed. A run
refuses before its first screen when the binary is missing or `claude -p` cannot answer a one-word probe. The calls are
bounded (one screen a call, `--max-turns 1`, no tools), cached within a run (the same prompt is never paid twice), and
**every prompt and every answer is recorded** under the run folder (`runs/<stamp>-read-<entry>/calls/`, ignored as
every run is). They are this repository's own calls: never the executor, no nonce fence, no response contract.

A full run writes
`quality/scores/<entry>/<yyyymmdd>-<scope>-r<RUBRIC_VERSION>-<cloud-sha7>-v<routing>-<reader-model>.json` (FR-4; the
scope is the bundle's, spec 071 FR-4: one corpus entry is three studies) and prints its path; **that file is
committed**. A partial run (`LIMIT=` / `ONLY=`, the smoke) writes its
`score.json` into the run folder alone -- a part of a walk is not a score of record and never reaches the table.
`DRY=1` prints every prompt, writes them into the run folder, calls nothing and writes no score.

Never in `make eval`, `make unit`, the matrix, a checker or a schedule; paid (the founder's plan), run on his word.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from instructions.judge import _ARGV as JUDGE_ARGV, judge_env
from quality import rubric

REPO = Path(__file__).resolve().parent.parent
QUALITY = REPO / "quality"
READERS_DIR = QUALITY / "readers"
READERS_TOML = QUALITY / "readers.toml"
SCORES_DIR = QUALITY / "scores"
RUNS_DIR = REPO / "runs"

PROBE_PROMPT = "Reply with the one word: ready"

_FOUNDER_KIND = re.compile(r"^(q|answer|check|choose)-(.+)$")
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


class Refused(RuntimeError):
    """A reason to stop before the first screen -- printed as one sentence, exit 2."""


# ------------------------------------------------------------------------------------------- the config

def load_reader_config(path: Path | None = None) -> dict:
    path = Path(path) if path else READERS_TOML
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    reader = dict(raw.get("reader") or {})
    for key in ("model", "effort", "vendor"):
        if not reader.get(key):
            raise Refused(f"quality/readers.toml has no reader.{key} (spec 078 FR-2)")
    reader.setdefault("door", "claude CLI")
    reader.setdefault("timeout_s", 240)
    return reader


def reader_argv(reader: dict) -> list[str]:
    """`instructions/judge.py`'s argv, plus the pinned model and effort -- nothing else."""
    return [*JUDGE_ARGV, "--model", str(reader["model"]), "--effort", str(reader["effort"])]


# ------------------------------------------------------------------------------------------- templates

def template(audience: str, part: str, readers_dir: Path | None = None) -> str:
    """The `screen` or `flow` prompt of one reader file: the text between its two markers."""
    path = Path(readers_dir or READERS_DIR) / f"{audience}.md"
    text = path.read_text(encoding="utf-8")
    begin, end = f"<!-- {part}:begin -->", f"<!-- {part}:end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise Refused(f"{path.name} must carry one `{part}:begin` and one `{part}:end` marker")
    return text.split(begin, 1)[1].split(end, 1)[0].strip() + "\n"


def fill(text: str, values: dict) -> str:
    """Every `{{name}}` filled in one pass (a value that itself carries braces is never re-filled)."""
    def one(match):
        name = match.group(1)
        if name not in values:
            raise Refused(f"the reader prompt names {{{{{name}}}}}, which the runner does not fill")
        return str(values[name])
    return _PLACEHOLDER.sub(one, text)


# -------------------------------------------------------------------------------------------- the bundle

def load_bundle(run: str | Path) -> tuple[Path, dict]:
    if not run:
        raise Refused("make read-screens refuses: no RUN -- name a back-test bundle, `make read-screens "
                      "RUN=runs/<stamp>-backtest-<entry>`")
    run_dir = Path(run).expanduser()
    if not run_dir.is_absolute() and not run_dir.exists():
        run_dir = RUNS_DIR / run_dir
    path = run_dir / "backtest.json"
    if not path.is_file():
        raise Refused(f"make read-screens refuses: {run_dir} has no backtest.json -- only a back-test bundle "
                      "(spec 062 FR-4) is read")
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if not (bundle.get("entry") or {}).get("id"):
        raise Refused(f"make read-screens refuses: {path} names no entry")
    if not bundle.get("founder_screens"):
        raise Refused(f"make read-screens refuses: {path} carries no founder screen (a walk that stopped early)")
    return run_dir, bundle


def entries_dir() -> Path | None:
    try:
        from instructions import corpus as corpus_mod
        from stack.config import load_config
        return corpus_mod.backtest_dir(load_config(validate=False).keel_cloud)
    except Exception:                                    # noqa: BLE001 - a missing sibling falls back to the bundle
        return None


def load_entry(bundle: dict, directory: Path | None = None) -> dict:
    """The entry yaml and its `.sources.md`, from the sibling keel-cloud checkout (else the path the bundle names),
    with whether the yaml read is byte for byte the one the bundle was walked on."""
    entry = bundle["entry"]
    candidates = []
    if directory:
        candidates.append(Path(directory) / f"{entry['id']}.yaml")
    if entry.get("path"):
        candidates.append(Path(entry["path"]))
    yaml_path = next((p for p in candidates if p.is_file()), None)
    if yaml_path is None:
        raise Refused(f"make read-screens refuses: no entry yaml for {entry['id']} (looked at "
                      f"{[str(p) for p in candidates]})")
    raw = yaml_path.read_bytes()
    data = yaml.safe_load(raw) or {}
    sources_path = yaml_path.parent / (data.get("sources") or f"{entry['id']}.sources.md")
    if not sources_path.is_file():
        raise Refused(f"make read-screens refuses: no sources file at {sources_path}")
    sha = hashlib.sha256(raw).hexdigest()
    return {"id": entry["id"], "yaml": data, "yaml_path": str(yaml_path), "sha256": sha,
            "matches_bundle": sha == entry.get("sha256"),
            "sources": sources_path.read_text(encoding="utf-8"), "sources_path": str(sources_path)}


def routing_version(run_dir: Path) -> str:
    """The product's routing table version the bundle was walked on: keel-cloud's `model-routing.json` at the
    cloud commit `versions.json` names, read with `git show` (read only). `NA` when it cannot be read."""
    try:
        versions = json.loads((run_dir / "versions.json").read_text(encoding="utf-8"))
        cloud = versions["keel-cloud"]
        done = subprocess.run(["git", "-C", cloud["path"], "show",
                               f"{cloud['commit']}:src/main/resources/keel/model-routing.json"],
                              capture_output=True, text=True, timeout=30)
        return str(json.loads(done.stdout)["version"]) if done.returncode == 0 else "NA"
    except Exception:                                    # noqa: BLE001
        return "NA"


# -------------------------------------------------------------------------------------------- the screens

@dataclass
class Screen:
    n: int
    screen: str
    audience: str
    link: str | None
    dimension: str | None
    kind: str
    has_options: bool
    full: str
    compact: str

    def meta(self) -> dict:
        return {"n": self.n, "screen": self.screen, "audience": self.audience, "link": self.link,
                "dimension": self.dimension, "kind": self.kind}

    def label(self) -> str:
        return f"{self.audience}-{self.link + '-' if self.link else ''}{self.n:02d}-{self.screen}"


def _lines(title: str, items) -> list[str]:
    items = [str(i) for i in (items or []) if str(i).strip()]
    return [f"{title}:"] + [f"  - {i}" for i in items] if items else []


def _said(value) -> str:
    if isinstance(value, dict):
        return "\n".join(f"  {k}: {_said(v).strip()}" for k, v in value.items() if v not in (None, "", [], {}))
    if isinstance(value, list):
        return "; ".join(_said(v).strip() for v in value)
    return str(value)


def _compact(n: int, kicker: str, question: str, fallback: str) -> str:
    said = (question or "").strip() or f"({fallback})"
    return f"{n}. [{(kicker or '').strip()}] {said}"


def founder_screens(bundle: dict) -> list[Screen]:
    screens = bundle.get("founder_screens") or []
    out = []
    for s in screens:
        name = s.get("screen") or f"screen-{s.get('n')}"
        match = _FOUNDER_KIND.match(name)
        kind, dimension = (match.group(1), match.group(2)) if match else (name, None)
        body = [f"Screen {s.get('n')} of {len(screens)} of the founder flow ({name}).",
                f"Kicker: {s.get('kicker') or ''}"]
        if s.get("question"):
            body.append(f"Question: {s['question']}")
        if s.get("hint"):
            body.append(f"Hint: {s['hint']}")
        body += _lines("Options", s.get("options"))
        body += _lines("Rows", s.get("rows"))
        body += _lines("Chips (the escape)", s.get("chips"))
        if s.get("keel read back"):
            body.append("What Keel wrote on this screen:\n" + _said(s["keel read back"]))
        if s.get("answer") not in (None, "", {}, []):
            body.append("What was typed or picked here (your own answer, from your material): "
                        + json.dumps(s["answer"], ensure_ascii=False))
        out.append(Screen(n=int(s.get("n") or len(out) + 1), screen=name, audience="founder", link=None,
                          dimension=dimension, kind=kind,
                          has_options=bool(s.get("options") or s.get("rows") or s.get("chips")),
                          full="\n".join(body),
                          compact=_compact(int(s.get("n") or len(out) + 1), s.get("kicker"), s.get("question")
                                           or s.get("hint"), name)))
    return out


def _served_items(served: dict) -> dict:
    return {item.get("dimension"): item for part in (served.get("parts") or []) for item in (part.get("items") or [])}


def _spoken(spoken: dict | None) -> str | None:
    if not spoken or not spoken.get("stem"):
        return None
    words = [spoken.get(k) for k in ("anchor", "stem", "countLine", "optionsLine", "escapeLine")]
    return "Said aloud on the AI interviewer link: " + " ".join(w for w in words if w)


def respondent_screens(bundle: dict) -> dict[str, list[Screen]]:
    """Each link's served screens, as drawn on the page (`respondents[link].drawn`), in order. The screener question
    the gate carries is its own screen (it is served before the gate); the price's up-front ladder and its plan are one
    screen, as the item is one dimension."""
    links = {}
    for link, record in (bundle.get("respondents") or {}).items():
        served = record.get("served") or {}
        items = _served_items(served)
        gate = served.get("gate") or {}
        out: list[Screen] = []

        def add(screen, kind, dimension, has_options, body, kicker, question):
            n = len(out) + 1
            out.append(Screen(n=n, screen=screen, audience="respondent", link=link, dimension=dimension, kind=kind,
                              has_options=has_options,
                              full=f"Screen {n} on this link ({screen}).\n" + "\n".join(body),
                              compact=_compact(n, kicker, question, screen)))

        for d in record.get("drawn") or []:
            what = d.get("screen")
            if what == "gate":
                chip = d.get("chip") or {}
                if chip.get("question"):
                    add("screener", "screener", None, True,
                        [f"Kicker: {d.get('kicker') or ''}", f"Question: {chip['question']}",
                         *_lines("Options", chip.get("options"))], d.get("kicker"), chip["question"])
                body = [f"Kicker: {d.get('kicker') or ''}", f"Question: {d.get('question') or ''}",
                        *_lines("Options", d.get("options")), *_lines("Chips (the escape)", d.get("chips"))]
                if gate.get("storyPrompt"):
                    body.append(f"On a yes, the next screen asks for the story: {gate['storyPrompt']}"
                                + (f" ({gate['storyHint']})" if gate.get("storyHint") else ""))
                if _spoken(gate.get("spoken")):
                    body.append(_spoken(gate.get("spoken")))
                add("gate", "gate", gate.get("dimension"), True, body, d.get("kicker"), d.get("question"))
            elif what == "item":
                dim = d.get("dimension")
                item = items.get(dim) or {}
                body = [f"Kicker: {d.get('kicker') or ''}"]
                if d.get("idea_card"):
                    body.append(f"Above the question, the idea card: {d['idea_card']}")
                plan = d.get("plan") or {}
                if plan and item.get("question") and item["question"] != plan.get("question"):
                    body += [f"Question: {item['question']}", *_lines("Options", item.get("options")),
                             f"Then, on the next screen: {plan.get('question')}", *_lines("Options", plan.get("rows"))]
                    question = item["question"]
                else:
                    body += [f"Question: {d.get('question') or ''}", *_lines("Options", d.get("rows"))]
                    question = d.get("question")
                if d.get("hint"):
                    body.append(f"Hint: {d['hint']}")
                if d.get("value_box_label"):
                    body.append(f"A box to type a number in, labelled: {d['value_box_label']}")
                if d.get("what_you_get"):
                    body.append(f"What you get: {d['what_you_get']}")
                body += _lines("Chips (the escape)", d.get("chips"))
                if _spoken(item.get("spoken")):
                    body.append(_spoken(item.get("spoken")))
                add(f"item-{dim}", "item", dim,
                    bool(d.get("rows") or d.get("chips") or d.get("value_box_label") or plan),
                    body, d.get("kicker"), question)
            elif what in ("reveal", "idea"):
                body = [f"Kicker: {d.get('kicker') or ''}", f"A card to read:\n{d.get('card') or ''}"]
                if d.get("question"):
                    body.append(f"Question: {d['question']}")
                add(what, what, None, False, body, d.get("kicker"), d.get("question") or "(the idea card)")
            elif what == "follow_up":
                body = [f"Kicker: {d.get('kicker') or ''}", f"Question: {d.get('question') or ''}",
                        f"Note under it: {d.get('note') or ''}", "A box to type in."]
                add("follow_up", "follow_up", None, False, body, d.get("kicker"), d.get("question"))
            else:
                body = [f"{k}: {_said(v)}" for k, v in d.items() if k not in ("order",) and v not in (None, "", [])]
                add(what or "screen", what or "screen", d.get("dimension"), bool(d.get("rows") or d.get("chips")),
                    body, d.get("kicker"), d.get("question"))
        links[link] = out
    return links


# ------------------------------------------------------------------------------------------- the persona

def _role(roles: list, link: str) -> dict:
    want = "BUYER" if link.startswith("COMMERCIAL") else "PRACTITIONER"
    return next((r for r in roles if r.get("roleType") == want), roles[0] if roles else {})


def _first_person(entry_yaml: dict, link: str) -> str | None:
    for answer in entry_yaml.get("answers") or []:
        on = answer.get("link") or "PRIMARY"
        if on == link or (link == "PRIMARY" and on not in ("COMMERCIAL_B2B",)):
            return answer.get("person")
    return None


def sources_line(sources: str, person: str | None) -> str:
    """The person's bullet in the sources file (the line naming them and its indented continuation), or ''."""
    if not person:
        return ""
    lines = sources.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"^\s*-\s+\**{re.escape(person)}\**\s*[:(,]", line):
            said = [line.strip().lstrip("-").strip()]
            for more in lines[i + 1:]:
                if more.startswith("  ") and not more.strip().startswith("-"):
                    said.append(more.strip())
                else:
                    break
            return " ".join(said)
    # No bullet of their own (a list written inline, `Revenue directors (...): Stefanie Wagner (6%), ...`): the
    # paragraph that names them, whole when short, else the words around the name.
    for paragraph in re.split(r"\n\s*\n", sources):
        if person in paragraph:
            flat = " ".join(paragraph.split())
            if len(flat) <= 600:
                return flat
            at = flat.index(person)
            return "..." + flat[max(0, at - 200):at + 300] + "..."
    return ""


def persona(entry: dict, bundle: dict, link: str) -> str:
    """The respondent-reader's hand-off for one link (FR-2): the person the walk took on that link (the first the
    entry names for it), their line from the sources, their role, and the study's context fields."""
    data = entry["yaml"]
    record = (bundle.get("respondents") or {}).get(link) or {}
    person = record.get("person") or _first_person(data, link) or "a person in this role"
    role = _role(data.get("roles") or [], link)
    ctx = data.get("context") or {}
    window = ctx.get("recall_window") or {}
    lines = [f"Your name is {person}."]
    line = sources_line(entry["sources"], person)
    if line:
        lines.append(f"About you: {line}")
    if role:
        lines.append(f"Your role: {role.get('label', '')} -- {role.get('about', '')}.")
    if link.startswith("COMMERCIAL"):
        title = ((data.get("persona") or {}).get("decision_maker") or {}).get("title")
        if title:
            lines.append(f"Your title: {title}. You decide on, and pay for, tools like the one in this study.")
    lines.append("The founder's own words for the situation this study is about (given so you know your situation; "
                 "they are not words you would necessarily use):")
    for key in ("actor", "actor_plural", "job", "circumstance", "segment"):
        if ctx.get(key):
            lines.append(f"  {key}: {ctx[key]}")
    if window:
        lines.append(f"  window: the last {window.get('count')} {str(window.get('unit', '')).lower()}")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------- the calls

@dataclass
class Reader:
    """One bounded, recorded, cached door to the `claude` CLI -- the judge's door with a model and an effort."""

    config: dict
    run_dir: Path
    runner: object = subprocess.run
    calls: list = field(default_factory=list)
    _cache: dict = field(default_factory=dict)

    def available(self) -> bool:
        return shutil.which("claude") is not None

    def ask(self, label: str, prompt: str) -> dict:
        """One call: `{answer, cost_usd, seconds, error, cached}`; recorded under `calls/` with its prompt."""
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if key in self._cache:
            return {**self._cache[key], "cached": True}
        started = time.monotonic()
        body, error = {}, None
        try:
            done = self.runner(reader_argv(self.config), input=prompt, capture_output=True, text=True,
                               timeout=float(self.config.get("timeout_s", 240)), env=judge_env(),
                               cwd=str(self.run_dir))
            lines = (done.stdout or "").strip().splitlines()
            body = json.loads(lines[-1]) if lines else {}
            if body.get("is_error") or not lines:
                error = f"the CLI answered an error: {str(body.get('result') or done.stderr or '')[:300]}"
        except Exception as exc:                          # noqa: BLE001 - a failed call leaves the screen unread
            error = f"{type(exc).__name__}: {exc}"
        result = {"answer": None if error else str(body.get("result") or ""),
                  "cost_usd": float(body.get("total_cost_usd") or 0.0),
                  "seconds": round(time.monotonic() - started, 1), "error": error, "cached": False,
                  "model_usage": sorted((body.get("modelUsage") or {}).keys())}
        index = len(self.calls) + 1
        calls_dir = self.run_dir / "calls"
        calls_dir.mkdir(parents=True, exist_ok=True)
        (calls_dir / f"{index:03d}-{label}.prompt.txt").write_text(prompt, encoding="utf-8")
        (calls_dir / f"{index:03d}-{label}.answer.json").write_text(
            json.dumps({**result, "raw": body}, indent=2, ensure_ascii=False), encoding="utf-8")
        self.calls.append({"label": label, **result})
        self._cache[key] = result
        return result

    def probe(self) -> None:
        if not self.available():
            raise Refused("make read-screens refuses: the `claude` binary is not on PATH -- the readers run through "
                          "the claude CLI as instructions/judge.py does (spec 078, the coordinator's decision 1)")
        said = self.ask("probe", PROBE_PROMPT)
        if said["error"] or not (said["answer"] or "").strip():
            raise Refused("make read-screens refuses: `claude -p` could not answer a one-word probe "
                          f"({said['error'] or 'an empty answer'}) -- log the CLI in, then run again")


# ------------------------------------------------------------------------------------------------ the run

def _select(screens: list[Screen], only: str | None, limit: int | None) -> list[Screen]:
    if only:
        needle = only.lower()
        screens = [s for s in screens if needle in s.screen.lower() or needle in (s.dimension or "").lower()]
    return screens[:limit] if limit else screens


# --------------------------------------------------------------------------------- the Insights grouping (§G)

def _answers_on(insight: dict) -> list[dict]:
    """Every answer on a follow-up line: its `quotes` (each person's words), else the groups' and the raw quotes."""
    if insight.get("quotes"):
        return [{"name": q.get("name"), "text": q.get("text")} for q in insight["quotes"]]
    grouped = [q for t in insight.get("themes") or [] for q in t.get("evidence") or []]
    return [{"name": q.get("name"), "text": q.get("text")} for q in grouped + list(insight.get("rawQuotes") or [])]


def insight_lines(bundle: dict) -> list[dict]:
    """The follow-up lines whose grouping the respondent-reader reads (§G): every Insights line of the bundle's
    report (`brief.insights`, the groups with their names and answers) with two answers or more, settled
    (`themes_settled`: not still grouping), each on the link its dimension was asked on -- a commercial dimension on
    the decision-maker's link where the bundle has one, else the first link."""
    links = list((bundle.get("respondents") or {}).keys())
    settled = bundle.get("themes_settled") or {}
    still = set(settled.get("grouping") or [])
    out = []
    for insight in (bundle.get("brief") or {}).get("insights") or []:
        answers = _answers_on(insight)
        if len(answers) < 2 or insight.get("dimension") in still:
            continue
        dim = insight.get("dimension") or ""
        commercial = [l for l in links if l.startswith("COMMERCIAL")]
        link = commercial[0] if dim.startswith("commercial.") and commercial else (links[0] if links else "PRIMARY")
        out.append({"dimension": dim, "name": insight.get("name") or dim, "line": insight.get("rungHeading") or dim,
                    "link": link, "answers": answers, "themes": insight.get("themes") or [],
                    "raw": insight.get("rawQuotes") or []})
    return out


def render_line(line: dict) -> str:
    body = [f"Follow-up line: {line['name']} ({line['dimension']})", f"The question asked: {line['line']}",
            "Every answer on it:"]
    body += [f"  - {a.get('name')}: \"{a.get('text')}\"" for a in line["answers"]]
    body.append("How Keel grouped them for the founder:")
    for theme in line["themes"]:
        label = theme.get("label")
        title = "(each on its own, in no group)" if label == "ON_THEIR_OWN" else f"Group \"{label}\""
        body.append(f"  {title} -- {theme.get('count')} answer(s):")
        body += [f"    - {q.get('name')}: \"{q.get('text')}\"" for q in theme.get("evidence") or []]
    if line["raw"]:
        body.append("  Shown as they were, not grouped:")
        body += [f"    - {q.get('name')}: \"{q.get('text')}\"" for q in line["raw"]]
    return "\n".join(body)


def plan(bundle: dict, entry: dict, *, only: str | None = None, limit: int | None = None,
         readers_dir: Path | None = None) -> dict:
    """Every prompt of a run, built before any call: `{screens: [(Screen, prompt)], flows: [(audience, link, prompt)],
    insights: [(line, prompt)]}`. A partial run (`only` / `limit`) asks no whole-flow question and reads no grouping:
    a part of a walk is not a flow."""
    rubric_part = rubric.prompt_rubric()
    founder_t, respondent_t = template("founder", "screen", readers_dir), template("respondent", "screen", readers_dir)
    jobs, flows = [], []
    founder = founder_screens(bundle)
    for screen in _select(founder, only, limit):
        earlier = "\n".join(s.compact for s in founder if s.n < screen.n) or "(none: this is the first screen)"
        jobs.append((screen, fill(founder_t, {"sources": entry["sources"].strip(), "rubric": rubric_part,
                                              "earlier": earlier, "screen": screen.full})))
    links = respondent_screens(bundle)
    chosen = [(link, s) for link, screens in links.items() for s in _select(screens, only, None)]
    chosen = chosen[:limit] if limit else chosen
    for link, screen in chosen:
        screens = links[link]
        earlier = "\n".join(s.compact for s in screens if s.n < screen.n) or "(none: this is the first screen)"
        jobs.append((screen, fill(respondent_t, {"persona": persona(entry, bundle, link), "rubric": rubric_part,
                                                 "earlier": earlier, "screen": screen.full})))
    if not (only or limit):
        flows.append(("founder", None, fill(template("founder", "flow", readers_dir),
                                            {"sources": entry["sources"].strip(),
                                             "earlier": "\n".join(s.compact for s in founder)})))
        for link, screens in links.items():
            if screens:
                flows.append(("respondent", link, fill(template("respondent", "flow", readers_dir),
                                                       {"persona": persona(entry, bundle, link),
                                                        "earlier": "\n".join(s.compact for s in screens)})))
    insights = []
    if not (only or limit):
        insights_t, rubric_g = template("respondent", "insights", readers_dir), rubric.prompt_insights()
        for line in insight_lines(bundle):
            insights.append((line, fill(insights_t, {"persona": persona(entry, bundle, line["link"]),
                                                     "line": render_line(line), "rubric_g": rubric_g})))
    return {"screens": jobs, "flows": flows, "insights": insights}


#: Spec 071 FR-4: a bundle walked before scopes, or with none named, is the whole study.
DEFAULT_SCOPE = "ALL"


def bundle_scope(bundle: dict) -> str:
    """The study's scope the bundle was walked under (`backtest.json`'s `scope`, spec 071 FR-4): one corpus entry is
    three studies, so a score is always of an (entry, scope) -- ALL when the bundle says none."""
    return str(bundle.get("scope") or DEFAULT_SCOPE)


def score_name(bundle: dict, routing: str, reader: dict, day: str) -> str:
    """`<yyyymmdd>-<scope>-r<RUBRIC_VERSION>-<cloud-sha7>-v<routing>-<reader-model>.json` (FR-4, amended)."""
    sha = str((bundle.get("stack") or {}).get("keel-cloud") or "nosha")[:7]
    return f"{day}-{bundle_scope(bundle)}-r{rubric.RUBRIC_VERSION}-{sha}-v{routing}-{reader['model']}.json"


def run(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="quality.readers", description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="the first n screens per audience (a partial run)")
    parser.add_argument("--only", default=None, help="screens whose name or dimension carries this text (partial)")
    parser.add_argument("--out", default=None, help="the run folder (default runs/<stamp>-read-<entry>)")
    parser.add_argument("--scores-dir", default=str(SCORES_DIR))
    args = parser.parse_args(argv)
    try:
        run_dir, bundle = load_bundle(args.run)
        entry = load_entry(bundle, entries_dir())
        reader_cfg = load_reader_config()
        work = plan(bundle, entry, only=args.only, limit=args.limit)
    except (Refused, rubric.RubricError) as reason:
        print(str(reason), file=sys.stderr)
        return 2
    partial = bool(args.only or args.limit)
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out) if args.out else RUNS_DIR / f"{stamp}-read-{entry['id']}{'-dry' if args.dry_run else ''}"
    out.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        prompts = out / "prompts"
        prompts.mkdir(exist_ok=True)
        jobs = [(s.label(), p) for s, p in work["screens"]] + \
               [(f"flow-{a}-{link or 'founder'}", p) for a, link, p in work["flows"]] + \
               [(f"insights-{line['link']}-{line['dimension']}", p) for line, p in work["insights"]]
        for i, (label, prompt) in enumerate(jobs, 1):
            print("=" * 100)
            print(f"[{i}/{len(jobs)}] {label}")
            print("=" * 100)
            print(prompt)
            (prompts / f"{i:03d}-{label}.prompt.txt").write_text(prompt, encoding="utf-8")
        print(f"dry run: {len(jobs)} prompts for {entry['id']}, scope {bundle_scope(bundle)} "
              f"({len(work['screens'])} screens, "
              f"{len(work['flows'])} whole-flow, {len(work['insights'])} insight lines) written to {prompts}; no call made, no score written")
        return 0

    reader = Reader(reader_cfg, out)
    started = time.monotonic()
    try:
        reader.probe()
    except Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    scores, unread = [], []
    for screen, prompt in work["screens"]:
        said = reader.ask(screen.label(), prompt)
        try:
            if said["error"]:
                raise rubric.RubricError(said["error"])
            answer = rubric.parse_answer(said["answer"], has_options=screen.has_options)
            scores.append(rubric.screen_score(screen.meta(), answer))
            print(f"  {screen.label():<64} scored")
        except rubric.RubricError as reason:
            unread.append({**screen.meta(), "error": str(reason)})
            print(f"  {screen.label():<64} unread: {reason}")
    flow = {"founder": None, "respondent": {}}
    for audience, link, prompt in work["flows"]:
        said = reader.ask(f"flow-{audience}-{link or 'founder'}", prompt)
        try:
            answer = rubric.parse_flow(said["answer"]) if not said["error"] else {"error": said["error"]}
        except rubric.RubricError as reason:
            answer = {"error": str(reason)}
        if audience == "founder":
            flow["founder"] = answer
        else:
            flow["respondent"][link] = answer
    readings = []
    for line, prompt in work["insights"]:
        said = reader.ask(f"insights-{line['link']}-{line['dimension']}", prompt)
        try:
            if said["error"]:
                raise rubric.RubricError(said["error"])
            readings.append({"line": line["line"], "dimension": line["dimension"], "link": line["link"],
                             **rubric.parse_insight(said["answer"])})
            print(f"  insights {line['link']} {line['dimension']:<48} scored")
        except rubric.RubricError as reason:
            unread.append({"insights": line["dimension"], "link": line["link"], "error": str(reason)})
            print(f"  insights {line['link']} {line['dimension']:<48} unread: {reason}")
    probe_cost = reader.calls[0]["cost_usd"] if reader.calls else 0.0
    record = {
        "entry": entry["id"],
        "scope": bundle_scope(bundle),
        "bundle": bundle.get("run") or run_dir.name,
        "cloud_sha": (bundle.get("stack") or {}).get("keel-cloud"),
        "web_sha": (bundle.get("stack") or {}).get("keel-web"),
        "routing_version": routing_version(run_dir),
        "rubric_version": rubric.RUBRIC_VERSION,
        "reader": {k: reader_cfg[k] for k in ("model", "effort", "vendor", "door")},
        "cost_usd": round(sum(c["cost_usd"] for c in reader.calls if not c["cached"]), 4),
        "probe_cost_usd": round(probe_cost, 4),
        "seconds": round(time.monotonic() - started, 1),
        "scored_at": now.isoformat(timespec="seconds"),
        "calls": sum(1 for c in reader.calls if not c["cached"]),
        "partial": partial,
        "selection": {"only": args.only, "limit": args.limit} if partial else None,
        "entry_yaml": {"sha256": entry["sha256"], "matches_bundle": entry["matches_bundle"]},
        "read_fraction": (round((len(scores) + len(readings)) / (len(scores) + len(readings) + len(unread)), 3)
                          if (scores or readings or unread) else None),
        "unread": unread,
        "summary": rubric.summaries(scores, readings),
        "insights": readings,
        "insights_note": (None if work["insights"] else "partial run: no grouping read" if partial
                          else "no grouping to read (no follow-up line with two answers)"),
        "flow": flow,
        "screens": scores,
    }
    if partial:
        path = out / "score.json"
    else:
        target = Path(args.scores_dir) / entry["id"]
        target.mkdir(parents=True, exist_ok=True)
        path = target / score_name(bundle, record["routing_version"], reader_cfg, now.strftime("%Y%m%d"))
        bump = 2
        while path.exists():
            path = path.with_name(re.sub(r"(-\d+)?\.json$", f"-{bump}.json", path.name))
            bump += 1
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "score-path.txt").write_text(str(path) + "\n", encoding="utf-8")
    overall = record["summary"]["overall"]
    print(f"{entry['id']} ({bundle_scope(bundle)}): {len(scores)} screens scored, {len(unread)} unread, score_pct {overall['score_pct']}, "
          f"flagged {overall['flagged']}, ${record['cost_usd']} in {record['seconds']} s"
          + (" (partial: not a score of record)" if partial else ""))
    print(f"score file: {path}")
    print(f"calls recorded under: {out / 'calls'}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
