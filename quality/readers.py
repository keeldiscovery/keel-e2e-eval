"""The two readers (spec 078 FR-2 - FR-4): `make read-screens RUN=<bundle> [DRY=1] [LIMIT=n] [ONLY=text]`.

A back-test bundle's `backtest.json` (spec 062 FR-4) is read as text -- every founder screen in order, and every
served respondent screen of each link -- and each screen is scored by one reader in **one call**: the founder-reader
(handed the entry's `.sources.md` whole) reads the founder screens, the respondent-reader (handed the person the walk
took on that link, their line from the sources, their role and the study's context fields) reads each link's screens.
**Spec 081 (rubric version 2)**: both prompts open with the persona block, before any screen -- the founder-reader's
the sources and the project's what / where / when (`founder_persona`), the respondent-reader's the person on the link
and the same context (`persona`) -- recorded once in the score file's header (`persona`); every respondent screen
carries how the AI interviewer says it (`said_aloud`: the served spoken form, else the guidelines' §3 template filled
from the screen) and is scored on R6 against keel-cloud's `spoken-questions-guidelines.md` §2, §3 and §5, pasted by the
runner (`spoken_guidelines`: at the bundle's cloud sha where that commit has it, else the checkout's; the header's
`spoken_guidelines` names which). The earlier screens of the same walk go in as one compact list, kicker and question
only (the coordinator's decision 3); the screen being scored goes in full. After every screen, each reader answers the three whole-flow questions once
(the founder once, the respondent once per link). The readers never drive the UI and never see a screenshot.

**Spec 109 (rubric version 3)**: the bundle's `after_screens` -- what the walk shot after everyone had answered: the
study's stage page, each dimension card opened with its chart, the Insights screen -- are founder screens of the kinds
`stage`, `dimension` and `insights-screen` (`after_screens`), each read in one call on §B (`quality/RUBRIC.md`'s
`prompt-b` part; `quality/readers/founder.md`'s `after` and `after-insights` prompts) with the beliefs the founder checked
on the way in (`checked_beliefs`), and folded into the founder's `score_pct`. A bundle walked before spec 109 has none:
its score file says so (`after_note`) and is not penalised.

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
`DRY=1` prints the persona blocks and the guidelines once, then every prompt with them named in place (the prompt
files it writes into the run folder carry them whole), calls nothing and writes no score.

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
from instructions.spoken import reveal_aloud
from quality import rubric

REPO = Path(__file__).resolve().parent.parent
QUALITY = REPO / "quality"
READERS_DIR = QUALITY / "readers"
READERS_TOML = QUALITY / "readers.toml"
SCORES_DIR = QUALITY / "scores"
RUNS_DIR = REPO / "runs"

PROBE_PROMPT = "Reply with the one word: ready"

#: Spec 081 FR-4: the spoken-question guidelines R6 is read against, in keel-cloud (one source), and the sections pasted.
GUIDELINES_REL = "canon/designs/spoken-questions-guidelines.md"
GUIDELINE_SECTIONS = ("2", "3", "5")

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
    said: str = ""
    #: Spec 109: a screen read after everyone answered (§B), numbered on its own from 1.
    after: bool = False

    def meta(self) -> dict:
        return {"n": self.n, "screen": self.screen, "audience": self.audience, "link": self.link,
                "dimension": self.dimension, "kind": self.kind}

    def label(self) -> str:
        if self.after:
            return f"{self.audience}-after-{self.n:02d}-{self.screen}"
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


# ------------------------------------------------------------------------- after the answers (§B, spec 109)

_STAGE_WORD = {"PROBLEM": "problem", "SOLUTION": "solution", "COMMERCIAL": "money"}


def _stage_words(stage: str | None) -> str:
    return f"the {_STAGE_WORD.get(str(stage or '').upper(), str(stage or '').lower())} stage page" if stage else \
        "the stage page"


def _after_body(s: dict, total: int) -> tuple[list[str], str]:
    """One §B screen as the founder-reader is handed it (FR-2): what each part of the screen is, then its words as drawn
    -- and the compact line the later screens see."""
    kind, n = s.get("kind"), int(s.get("n") or 0)
    head = f"Screen {n} of {total} read after everyone answered"
    if kind == "stage":
        page = s.get("page") or {}
        body = [f"{head}: {_stage_words(s.get('stage'))} ({s.get('url') or 's/' + str(s.get('stage'))}).",
                f"Kicker: {page.get('kicker') or ''}", f"Title: {page.get('title') or ''}",
                f"The verdict line under the title: {page.get('headline') or ''}"]
        if page.get("statement"):
            body.append(f"Keel's statement under it: {page['statement']}")
        if page.get("foot"):
            body.append(f"The count line: {page['foot']}")
        if page.get("decider"):
            body.append(f"The banner: {page['decider']}")
        rows = page.get("rows") or []
        if rows:
            body.append("One card per dimension, as listed (its number and name, your belief, the status word with its "
                        "line; a card that does not open is marked):")
            body += ["  - " + " -- ".join(x for x in (f"{r.get('n') or ''} {r.get('name') or ''}".strip(), r.get("belief"),
                                                      r.get("status")) if x)
                     + ("" if r.get("opens", True) else " (does not open)") for r in rows]
        if page.get("measures"):
            body.append(f"What it measures: {page['measures']}")
        compact = f"{n}. [{_stage_words(s.get('stage'))}] {page.get('headline') or page.get('title') or ''}"
    elif kind == "dimension":
        card = s.get("chart") or {}
        body = [f"{head}: the {card.get('title') or s.get('dimension')} card on {_stage_words(s.get('stage'))}, "
                "opened, its chart drawn.",
                f"The card's title: {card.get('title') or ''}",
                f"Your belief, as the card says it: {card.get('belief') or ''}",
                f"The verdict (the status word, its line and the count under it): {card.get('verdict') or ''}"]
        for label, key in (("Asked", "asked"), ("The bar line", "bar"), ("The chart's caption", "caption"),
                           ("The chart's legend", "legend")):
            if card.get(key):
                body.append(f"{label}: {card[key]}")
        if card.get("drawing"):
            body.append(f"The chart ({card.get('chart') or 'drawn'}), its words: {card['drawing']}")
        people = card.get("people") or []
        if people:
            body.append("Everyone who answered (name -- how Keel read the answer):")
            body += [f"  - {p.get('name') or ''} -- {p.get('read') or ''}" for p in people]
        compact = f"{n}. [the {card.get('title') or s.get('dimension')} card] {card.get('verdict') or ''}"
    else:
        ins = s.get("insights") or {}
        body = [f"{head}: the Insights screen ({s.get('url') or '#insights'}), every fold opened."]
        boxes = ins.get("boxes") or []
        if boxes:
            body.append("One box per line, as drawn (its name and status word, the question asked, the groups with "
                        "their counts):")
            for b in boxes:
                groups = ", ".join(f"{t.get('label')} ({t.get('count')})" for t in b.get("themes") or [])
                body.append(f"  - {b.get('head') or b.get('dimension')} -- {b.get('concern') or ''}"
                            + (f" -- groups: {groups}" if groups else "")
                            + (f" -- {b.get('quotes')} quote(s)" if b.get("quotes") is not None else ""))
        if ins.get("empty"):
            body.append(f"The screen says: {ins['empty']}")
        for line in ins.get("not_asked") or []:
            body.append(f"Under the boxes: {line}")
        compact = f"{n}. [the Insights screen] {len(boxes)} box(es)"
    if s.get("text"):
        body.append("The screen's words, as drawn, in order:\n" + str(s["text"]).strip())
    return body, compact


def after_screens(bundle: dict) -> list[Screen]:
    """Spec 109: the bundle's `after_screens` -- the stage page, each dimension card opened with its chart, the Insights
    screen, as the walk shot them after everyone had answered -- as founder screens of their own kinds, in order."""
    shots = [s for s in bundle.get("after_screens") or [] if rubric.is_after(s.get("kind"))]
    out = []
    for i, s in enumerate(shots, 1):
        s = {**s, "n": int(s.get("n") or i)}
        body, compact = _after_body(s, len(shots))
        out.append(Screen(n=s["n"], screen=s.get("screen") or s["kind"], audience="founder", link=None,
                          dimension=s.get("dimension"), kind=s["kind"], has_options=False, full="\n".join(body),
                          compact=compact, after=True))
    return out


def checked_beliefs(bundle: dict) -> str:
    """Spec 109 FR-2 (B3): the beliefs the founder checked on the way in -- every `check-` screen's belief line (as the
    screen drew it, else the wire's), Keel will test and the bar, as the flow recorded them."""
    lines = []
    for s in bundle.get("founder_screens") or []:
        name = str(s.get("screen") or "")
        if not name.startswith("check-"):
            continue
        back = s.get("keel read back") if isinstance(s.get("keel read back"), dict) else {}
        belief = back.get("belief line on screen") or back.get("belief")
        if not belief:
            continue
        line = f"- {name.removeprefix('check-')} ({(s.get('kicker') or '').strip()}): {belief}"
        if back.get("keel will test"):
            line += f"; Keel will test: {back['keel will test']}"
        if back.get("bar"):
            line += f"; your bar: {_said(back['bar']).strip()}"
        lines.append(line)
    return "\n".join(lines) or "(the flow recorded no check screen with a belief line)"


def _served_items(served: dict) -> dict:
    return {item.get("dimension"): item for part in (served.get("parts") or []) for item in (part.get("items") or [])}


def _spoken(spoken: dict | None) -> str | None:
    """The served spoken form (keel-cloud's `spoken` block), as one line, or None where the bundle records none."""
    if not spoken or not spoken.get("stem"):
        return None
    words = [spoken.get(k) for k in ("anchor", "stem", "countLine", "optionsLine", "escapeLine")]
    return " ".join(str(w).strip() for w in words if w)


def _escape_label(escape) -> str | None:
    if not escape:
        return None
    if isinstance(escape, dict):
        return escape.get("label") or None
    return str(escape).strip() or None


def spoken_template(stem: str | None, options: list | None = None, escape: str | None = None, *,
                    pick_two: bool = False) -> str:
    """The guidelines' §3 template filled from a screen: the stem; *I'll read N options[; pick two].*; the options
    *a; b; or c.*; *Or say {escape}.* -- what the AI interviewer reads when the bundle records no spoken form."""
    words = [str(stem or "").strip()]
    options = [str(o).strip() for o in options or [] if str(o).strip()]
    if options:
        words.append(f"I'll read {len(options)} options{'; pick two' if pick_two else ''}.")
        words.append("; ".join(options[:-1]) + f"; or {options[-1]}." if len(options) > 1 else f"{options[0]}.")
    if escape:
        words.append(f"Or say {escape}.")
    return " ".join(w for w in words if w)


def said_line(served_spoken: dict | None, composed: str) -> tuple[str, str]:
    """(the words, the body line) of how the AI interviewer says a screen (spec 081 FR-4): the served spoken form
    where the bundle records one, else the §3 template the runner filled."""
    served = _spoken(served_spoken)
    if served:
        return served, f"Said aloud by the AI interviewer (the served spoken form): {served}"
    return composed, ("Said aloud by the AI interviewer (the guidelines' §3 template filled from this screen; the "
                      f"bundle records no spoken form for it): {composed}")


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

        def add(screen, kind, dimension, has_options, body, kicker, question, said):
            n = len(out) + 1
            out.append(Screen(n=n, screen=screen, audience="respondent", link=link, dimension=dimension, kind=kind,
                              has_options=has_options,
                              full=f"Screen {n} on this link ({screen}).\n" + "\n".join(body),
                              compact=_compact(n, kicker, question, screen), said=said))

        for d in record.get("drawn") or []:
            what = d.get("screen")
            if what == "gate":
                chip = d.get("chip") or {}
                if chip.get("question"):
                    said, line = said_line(None, spoken_template(chip["question"], chip.get("options")))
                    add("screener", "screener", None, True,
                        [f"Kicker: {d.get('kicker') or ''}", f"Question: {chip['question']}",
                         *_lines("Options", chip.get("options")), line], d.get("kicker"), chip["question"], said)
                body = [f"Kicker: {d.get('kicker') or ''}", f"Question: {d.get('question') or ''}",
                        *_lines("Options", d.get("options")), *_lines("Chips (the escape)", d.get("chips"))]
                if gate.get("storyPrompt"):
                    body.append(f"On a yes, the next screen asks for the story: {gate['storyPrompt']}"
                                + (f" ({gate['storyHint']})" if gate.get("storyHint") else ""))
                said, line = said_line(gate.get("spoken"), spoken_template(
                    d.get("question"), d.get("options"), (d.get("chips") or [None])[0]))
                body.append(line)
                add("gate", "gate", gate.get("dimension"), True, body, d.get("kicker"), d.get("question"), said)
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
                escape = _escape_label(item.get("escape")) or (d.get("chips") or [None])[0]
                if plan and item.get("question") and item["question"] != plan.get("question"):
                    composed = (spoken_template(item["question"], item.get("options") and
                                                [o.get("label") if isinstance(o, dict) else o for o in item["options"]]
                                                or d.get("rows"), escape)
                                + " Then: " + spoken_template(plan.get("question"), plan.get("rows")))
                else:
                    composed = spoken_template(question, d.get("rows"), escape, pick_two=d.get("control") == "pick_two")
                said, line = said_line(item.get("spoken"), composed)
                body.append(line)
                add(f"item-{dim}", "item", dim,
                    bool(d.get("rows") or d.get("chips") or d.get("value_box_label") or plan),
                    body, d.get("kicker"), question, said)
            elif what in ("reveal", "idea"):
                body = [f"Kicker: {d.get('kicker') or ''}", f"A card to read:\n{d.get('card') or ''}"]
                if d.get("question"):
                    body.append(f"Question: {d['question']}")
                # spec 111 (keel-cloud 176): the card said as the AI interviewer says the reveal -- a parenthesis
                # of names *such as ...*, a list past five *and others* -- the card above it as typed
                card = "\n".join(reveal_aloud(x) for x in str(d.get("card") or "").splitlines())
                said, line = said_line(None, " ".join(" ".join(str(x or "").split())
                                                      for x in (card, d.get("question")) if x))
                body.append(line)
                add(what, what, None, False, body, d.get("kicker"), d.get("question") or "(the idea card)", said)
            elif what == "follow_up":
                body = [f"Kicker: {d.get('kicker') or ''}", f"Question: {d.get('question') or ''}",
                        f"Note under it: {d.get('note') or ''}", "A box to type in."]
                said, line = said_line(None, spoken_template(d.get("question")))
                body.append(line)
                add("follow_up", "follow_up", None, False, body, d.get("kicker"), d.get("question"), said)
            else:
                body = [f"{k}: {_said(v)}" for k, v in d.items() if k not in ("order",) and v not in (None, "", [])]
                said, line = said_line(d.get("spoken") if isinstance(d.get("spoken"), dict) else None,
                                       spoken_template(d.get("question"), d.get("rows"), (d.get("chips") or [None])[0]))
                body.append(line)
                add(what or "screen", what or "screen", d.get("dimension"), bool(d.get("rows") or d.get("chips")),
                    body, d.get("kicker"), d.get("question"), said)
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


def context_lines(data: dict) -> list[str]:
    """Spec 081 FR-3: the project's what / where / when as the entry's context fields say it -- actor, actor_plural,
    job, circumstance, segment, the window, and the market's country (and region where the entry names one)."""
    ctx = data.get("context") or {}
    window = ctx.get("recall_window") or {}
    market = data.get("market") or {}
    lines = []
    for key in ("actor", "actor_plural", "job", "circumstance", "segment"):
        if ctx.get(key):
            lines.append(f"  {key}: {ctx[key]}")
    if window:
        lines.append(f"  window: the last {window.get('count')} {str(window.get('unit', '')).lower()}")
    if market.get("country"):
        lines.append(f"  where: {market['country']}" + (f", {market['region']}" if market.get("region") else ""))
    return lines


def founder_persona(entry: dict) -> str:
    """Spec 081 FR-3: the founder-reader's persona block -- the entry's sources whole (the YC material) and the
    project's what / where / when as the context fields say it."""
    return "\n".join(["Your own public material (you are the founder it describes):", "", entry["sources"].strip(), "",
                      "The study you typed into Keel, as its context fields say it (your trade's words are plain to "
                      "you; judge from inside your trade, your place and your time):", *context_lines(entry["yaml"])])


def persona(entry: dict, bundle: dict, link: str) -> str:
    """The respondent-reader's persona block for one link (FR-2; spec 081 FR-3): the person the walk took on that link
    (the first the entry names for it), their line from the sources, their role, and the project's what / where /
    when as the context fields say it."""
    data = entry["yaml"]
    record = (bundle.get("respondents") or {}).get(link) or {}
    person = record.get("person") or _first_person(data, link) or "a person in this role"
    role = _role(data.get("roles") or [], link)
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
    lines.append("The project's what, where and when, in the founder's own words for your situation (given so you know "
                 "your trade, your place and your time; they are not words you would necessarily use):")
    lines += context_lines(data)
    return "\n".join(lines)


# ------------------------------------------------------------------------------------- the spoken guidelines

def guideline_sections(text: str, numbers=GUIDELINE_SECTIONS) -> str:
    """The guidelines' numbered `## n.` sections, each whole to the next `## ` heading, in order -- or `Refused`."""
    out = []
    for number in numbers:
        match = re.search(rf"^## {re.escape(number)}\.[^\n]*$", text, re.M)
        if not match:
            raise Refused(f"the spoken-question guidelines carry no section {number} ({GUIDELINES_REL})")
        rest = text[match.end():]
        stop = re.search(r"^## ", rest, re.M)
        out.append((match.group(0) + rest[:stop.start() if stop else len(rest)]).strip())
    return "\n\n".join(out)


def spoken_guidelines(bundle: dict, cloud: Path | None = None) -> dict:
    """Spec 081 FR-4: §2, §3 and §5 of keel-cloud's spoken-question guidelines, one source -- read with `git show` at
    the bundle's cloud sha where that commit carries the file, else from the checkout. `{text, source, sha256}`."""
    if cloud is None:
        try:
            from stack.config import load_config
            cloud = Path(load_config(validate=False).keel_cloud)
        except Exception:                                # noqa: BLE001 - no sibling: refused below
            cloud = None
    if cloud is None:
        raise Refused(f"make read-screens refuses: no keel-cloud checkout to read {GUIDELINES_REL} from (R6, spec 081)")
    sha = str((bundle.get("stack") or {}).get("keel-cloud") or "").strip()
    text, source = None, None
    if sha:
        done = subprocess.run(["git", "-C", str(cloud), "show", f"{sha}:{GUIDELINES_REL}"], capture_output=True,
                              text=True, timeout=30)
        if done.returncode == 0 and done.stdout.strip():
            text, source = done.stdout, f"keel-cloud {sha} (the bundle's)"
    if text is None:
        path = Path(cloud) / GUIDELINES_REL
        if not path.is_file():
            raise Refused(f"make read-screens refuses: no {GUIDELINES_REL} in {cloud} (R6, spec 081)")
        text = path.read_text(encoding="utf-8")
        source = f"the keel-cloud checkout ({cloud}; the bundle's sha {sha or 'unnamed'} does not carry it)"
    part = guideline_sections(text)
    return {"text": part, "source": source, "sections": list(GUIDELINE_SECTIONS),
            "sha256": hashlib.sha256(part.encode("utf-8")).hexdigest()}


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
         readers_dir: Path | None = None, guidelines: dict | None = None) -> dict:
    """Every prompt of a run, built before any call: `{screens: [(Screen, prompt)], flows: [(audience, link, prompt)],
    insights: [(line, prompt)], persona: {founder, respondent: {link: block}}, spoken_guidelines: {...}}`. A partial
    run (`only` / `limit`) asks no whole-flow question and reads no grouping: a part of a walk is not a flow.
    `guidelines` is `spoken_guidelines(bundle)`'s answer (read here when not given)."""
    rubric_part, rubric_r6 = rubric.prompt_rubric(), rubric.prompt_spoken()
    guidelines = guidelines if guidelines is not None else spoken_guidelines(bundle)
    founder_t, respondent_t = template("founder", "screen", readers_dir), template("respondent", "screen", readers_dir)
    jobs, flows = [], []
    founder = founder_screens(bundle)
    after = after_screens(bundle)                                   # spec 109: §B, after everyone answered
    founder_block = founder_persona(entry)
    links = respondent_screens(bundle)
    blocks = {link: persona(entry, bundle, link) for link in links}
    for screen in _select(founder + after, only, limit):
        if screen.after:
            earlier = "\n".join(s.compact for s in after if s.n < screen.n) or \
                "(none: this is the first screen read after the answers)"
            part = "after-insights" if screen.kind == "insights-screen" else "after"
            jobs.append((screen, fill(template("founder", part, readers_dir),
                                      {"persona": founder_block, "rubric_b": rubric.prompt_after(),
                                       "beliefs": checked_beliefs(bundle), "earlier": earlier,
                                       "screen": screen.full})))
            continue
        earlier = "\n".join(s.compact for s in founder if s.n < screen.n) or "(none: this is the first screen)"
        jobs.append((screen, fill(founder_t, {"persona": founder_block, "rubric": rubric_part,
                                              "earlier": earlier, "screen": screen.full})))
    chosen = [(link, s) for link, screens in links.items() for s in _select(screens, only, None)]
    chosen = chosen[:limit] if limit else chosen
    for link, screen in chosen:
        screens = links[link]
        earlier = "\n".join(s.compact for s in screens if s.n < screen.n) or "(none: this is the first screen)"
        jobs.append((screen, fill(respondent_t, {"persona": blocks[link], "rubric": rubric_part,
                                                 "rubric_r6": rubric_r6, "spoken_rules": guidelines["text"],
                                                 "earlier": earlier, "screen": screen.full})))
    if not (only or limit):
        flows.append(("founder", None, fill(template("founder", "flow", readers_dir),
                                            {"persona": founder_block,
                                             "earlier": "\n".join(s.compact for s in founder)})))
        for link, screens in links.items():
            if screens:
                flows.append(("respondent", link, fill(template("respondent", "flow", readers_dir),
                                                       {"persona": blocks[link],
                                                        "earlier": "\n".join(s.compact for s in screens)})))
    insights = []
    if not (only or limit):
        insights_t, rubric_g = template("respondent", "insights", readers_dir), rubric.prompt_insights()
        for line in insight_lines(bundle):
            block = blocks.get(line["link"]) or persona(entry, bundle, line["link"])
            insights.append((line, fill(insights_t, {"persona": block, "line": render_line(line),
                                                     "rubric_g": rubric_g})))
    return {"screens": jobs, "flows": flows, "insights": insights, "after": len(after),
            "persona": {"founder": founder_block, "respondent": blocks},
            "spoken_guidelines": {k: guidelines[k] for k in ("source", "sections", "sha256")},
            "_guidelines_text": guidelines["text"]}


def named_in_place(prompt: str, work: dict) -> str:
    """A prompt as the dry run prints it (spec 081 acceptance): the persona blocks and the guidelines, printed once
    above, named in place -- the prompt files keep them whole."""
    blocks = [("the founder's persona block, printed above", work["persona"]["founder"])]
    blocks += [(f"the {link} persona block, printed above", b) for link, b in work["persona"]["respondent"].items()]
    blocks.append(("the spoken-question guidelines §2, §3 and §5, printed above", work.get("_guidelines_text") or ""))
    for name, text in sorted(blocks, key=lambda nb: -len(nb[1])):
        if text:
            prompt = prompt.replace(text, f"[{name}]")
    return prompt


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
        work = plan(bundle, entry, only=args.only, limit=args.limit, guidelines=spoken_guidelines(bundle))
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
        print("=" * 100)
        print("THE PERSONA BLOCKS (spec 081 FR-3: each opens every prompt of its reader; the score file's header "
              "records them once)")
        print("=" * 100)
        print("--- founder-reader ---")
        print(work["persona"]["founder"])
        for link, block in work["persona"]["respondent"].items():
            print(f"--- respondent-reader, link {link} ---")
            print(block)
        print("=" * 100)
        print(f"THE SPOKEN-QUESTION GUIDELINES R6 is read against (§2, §3, §5; {work['spoken_guidelines']['source']}; "
              "pasted whole into every respondent prompt)")
        print("=" * 100)
        print(work["_guidelines_text"])
        for i, (label, prompt) in enumerate(jobs, 1):
            print("=" * 100)
            print(f"[{i}/{len(jobs)}] {label}")
            print("=" * 100)
            print(named_in_place(prompt, work))
            (prompts / f"{i:03d}-{label}.prompt.txt").write_text(prompt, encoding="utf-8")
        print(f"dry run: {len(jobs)} prompts for {entry['id']}, scope {bundle_scope(bundle)} "
              f"({len(work['screens'])} screens, {work['after']} of them after the answers, "
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
            answer = (rubric.parse_after(said["answer"], kind=screen.kind) if screen.after else
                      rubric.parse_answer(said["answer"], has_options=screen.has_options, audience=screen.audience))
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
        "persona": work["persona"],
        "spoken_guidelines": work["spoken_guidelines"],
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
        # spec 109: a bundle walked before the answers leg shot nothing after the answers -- said, not penalised
        "after_note": (None if work["after"] else "no screen after the answers in the bundle (walked before spec 109, "
                       "or the leg shot none)"),
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
          f"spoken_pct {overall.get('spoken_pct')}, "
          f"flagged {overall['flagged']}, ${record['cost_usd']} in {record['seconds']} s"
          + (" (partial: not a score of record)" if partial else ""))
    print(f"score file: {path}")
    print(f"calls recorded under: {out / 'calls'}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
