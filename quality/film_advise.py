"""The film adviser (spec 163 FR-6): `make film-advise RUN=<bundle> [DRY=1]` -- PAID (the founder's plan).

One bounded call per weak criterion of the bundle's film table (`quality/film_rubric.weak_criteria`), through the
`claude` CLI exactly as `make quality-advise` calls it (the judge's argv, `[film] adviser_model` / `adviser_effort` from
`quality/cycle.toml`), the prompt `quality/readers/film-adviser.md`: the weak criterion with its anchors, every film's
score, why and instead line on it -- **the entries named by their number alone** (*film 1*, *film 2*: the adviser never
sees an entry's name, so it cannot write a case) -- and the current text of the three places a film rule lives in
keel-cloud: `picture-setting.md`, `PicturePrompts`' fixed rules and `story-draft.md`, read from the keel-cloud checkout
(at the bundle's sha where that commit has them, else the checkout's).

A proposal is **refused** when it names an entry, its idea, a trade word of the entries' context, or reads as a case
(`quality.cycle.special_case`: *if the person is a ...*) -- the persona-aware rule; it is recorded by criterion with the
reason. The adviser proposes; it never applies: `quality/cycles/<record>-film-advice.md`, committed by hand, each
proposal decided by the founder (taken: a keel-cloud spec). `DRY=1` writes the prompts and calls nothing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from quality import cycle as cyc
from quality import film_rubric as fr
from quality import film_table as ft
from quality import readers, rubric

REPO = Path(__file__).resolve().parent.parent
PROMPT_PATH = REPO / "quality" / "readers" / "film-adviser.md"
#: The three places a film rule lives in keel-cloud (FR-6), by the name the adviser answers with.
PLACES = {"picture-setting.md": "src/main/resources/keel/inference-instructions/picture-setting.md",
          "PicturePrompts": "src/main/java/com/keeldiscovery/cloud/application/story/PicturePrompts.java",
          "story-draft.md": "src/main/resources/keel/inference-instructions/story-draft.md"}
MAX_QUOTE = 16000


def current_text(cloud: Path, sha: str | None = None) -> str:
    """The three places' text, each under its name: at `sha` where the commit has the file, else the checkout's."""
    parts = []
    for name, rel in PLACES.items():
        text = None
        if sha:
            done = subprocess.run(["git", "-C", str(cloud), "show", f"{sha}:{rel}"], capture_output=True, text=True,
                                  timeout=30)
            text = done.stdout if done.returncode == 0 else None
        if text is None and (Path(cloud) / rel).is_file():
            text = (Path(cloud) / rel).read_text(encoding="utf-8")
        parts.append(f"### {name} ({rel})\n\n{(text or '(not in this checkout)')[:MAX_QUOTE]}")
    return "\n\n".join(parts)


def criterion_block(weak: dict) -> str:
    kind = weak["kind"]
    rows = fr.criteria(kind)
    row = next(r for r in rows if r["id"] == weak["criterion"])
    return (f"{row['id'].upper()} -- {row['question']}\n  2: {row['2']}\n  1: {row['1']}\n  0: {row['0']}\n"
            f"Weak: mean {weak['mean']:.2f} over {len(weak['entries'])} films, a 0 in {weak['zeros']}.")


def failing_block(weak: dict, files: list[dict]) -> str:
    """Every film's score on the criterion, by number alone (never the entry's name)."""
    lines = []
    for i, f in enumerate(sorted(files, key=lambda x: x["entry"]), 1):
        if weak["kind"] == "founder":
            for b in (f.get("founder") or {}).get("beats") or []:
                lines.append(f"- film {i}, {b['beat']}: {b[weak['criterion']]} -- "
                             f"{b[fr.FOUNDER_WHYS[fr.FOUNDER_CRITERIA.index(weak['criterion'])]]}"
                             + (f" -- instead: {b['instead']}" if b.get("instead") else ""))
            continue
        film = f["film"]
        if film["kind"] != weak["kind"]:
            continue
        c = weak["criterion"]
        lines.append(f"- film {i}: {film['scores'][c]} -- {film['whys'].get(c, '')}"
                     + (f" -- instead: {film['instead'][c]}" if c in film["instead"] else ""))
    return "\n".join(lines)


def anonymise(text: str, files: list[dict]) -> str:
    """Every entry id and idea name out of the text handed to the adviser (`film N` in their place)."""
    for i, f in enumerate(sorted(files, key=lambda x: x["entry"]), 1):
        for name in {f["entry"], *re.findall(r"[A-Za-z][\w-]+", f["entry"].split("-", 1)[-1])}:
            if len(name) > 2:
                text = re.sub(rf"(?i)\b{re.escape(name)}\b", f"film {i}", text)
    return text


def names_a_case(proposal: dict, files: list[dict]) -> str | None:
    """Why a proposal is refused (a rule, never a case), or None: an entry's id or name in it, or `special_case`."""
    text = " ".join(str(proposal.get(k) or "") for k in ("change", "why"))
    for f in files:
        for name in {f["entry"], f["entry"].split("-", 1)[-1]}:
            if len(name) > 2 and re.search(rf"(?i)\b{re.escape(name)}\b", text):
                return f"it names an entry ({name!r}): a rule, never a case (spec 163 FR-6)"
    said = cyc.special_case({"persona_aware": True, "new_text": proposal.get("change") or ""})
    return f"{said} (spec 163 FR-6, the persona-aware rule)" if said else None


def parse_proposal(raw: str) -> dict:
    body = rubric.extract_json(raw)
    where = str(body.get("where") or "").strip()
    if where not in PLACES:
        raise rubric.RubricError(f"where {where!r} is not one of {', '.join(PLACES)}")
    if str(body.get("rung") or "") not in cyc.RUNGS:
        raise rubric.RubricError(f"rung {body.get('rung')!r} is not one of {', '.join(cyc.RUNGS)}")
    if not str(body.get("change") or "").strip():
        raise rubric.RubricError("no change")
    return {"where": where, "change": str(body["change"]).strip(), "why": str(body.get("why") or "").strip(),
            "rung": body["rung"]}


def main(argv=None, *, runner=subprocess.run) -> int:
    parser = argparse.ArgumentParser(prog="quality.film_advise", description=__doc__.split("\n\n")[0])
    parser.add_argument("--run", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scores-dir", default=str(ft.SCORES_DIR))
    parser.add_argument("--cycles-dir", default=str(ft.CYCLES_DIR))
    parser.add_argument("--cloud", default=None)
    args = parser.parse_args(argv)
    try:
        if not args.run:
            raise ft.Refused("make film-advise refuses: no RUN -- name the film-walk bundle (spec 163 FR-6)")
        cfg = ft.load_film_config()
        bundle = ft.bundle_of(args.run)
        files = ft.load_films(bundle, Path(args.scores_dir))
        if not files:
            raise ft.Refused(f"make film-advise refuses: no film score file for {bundle} -- `make read-films` first")
    except ft.Refused as reason:
        print(str(reason), file=sys.stderr)
        return 2
    weak = fr.weak_criteria(files)
    record = Path(args.cycles_dir) / ft.record_name(files).replace("-film.md", "-film-advice.md")
    if not weak:
        print("no weak criterion: nothing to advise, nothing written")
        return 0
    cloud = Path(args.cloud) if args.cloud else cyc.checkouts()[0]
    quoted = current_text(cloud, files[0].get("cloud_sha"))
    template = readers.template("film-adviser", "advise", readers_dir=PROMPT_PATH.parent)
    jobs = []
    for w in weak:
        prompt = readers.fill(template, {"criterion": criterion_block(w),
                                         "failing": anonymise(failing_block(w, files), files), "current": quoted})
        jobs.append((w, prompt))
    out = readers.RUNS_DIR / f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-film-advise-{bundle}"
    out.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        for i, (w, prompt) in enumerate(jobs, 1):
            (out / f"{i:02d}-{w['criterion']}.prompt.txt").write_text(prompt, encoding="utf-8")
        print(f"dry run: {len(jobs)} prompt(s) written to {out}; no call made, nothing written to {record}")
        return 0
    adviser = {"model": cfg["adviser"]["model"], "effort": cfg["adviser"]["effort"],
               "timeout_s": cfg["adviser"]["timeout_s"], "vendor": "anthropic", "door": "claude CLI"}
    door = readers.Reader(adviser, out, runner=runner)
    try:
        door.probe()
    except readers.Refused as reason:
        print(str(reason).replace("make read-screens", "make film-advise"), file=sys.stderr)
        return 2
    lines = [f"# The film adviser -- {bundle}", "",
             f"Proposals, never applied (spec 163 FR-6): one a weak criterion; each decided by the founder. Adviser "
             f"{adviser['model']} {adviser['effort']} (claude CLI).", ""]
    for w, prompt in jobs:
        lines.append(f"## {w['criterion'].upper()} ({w['kind']}) -- mean {w['mean']:.2f}, a 0 in {w['zeros']}")
        lines.append("")
        try:
            proposal, _ = readers.ask_twice(door, f"advise-{w['criterion']}", prompt, parse_proposal)
        except rubric.RubricError as reason:
            lines += [f"Unread: {reason}", ""]
            continue
        refused = names_a_case(proposal, files)
        if refused:
            lines += [f"**Refused**: {refused}.", ""]
            continue
        lines += [f"- **where**: {proposal['where']} ({PLACES[proposal['where']]})", f"- **rung**: {proposal['rung']}",
                  f"- **why**: {proposal['why']}", "", "```", proposal["change"], "```", ""]
    cost = round(sum(c["cost_usd"] for c in door.calls if not c["cached"]), 4)
    lines.append(f"Cost: ${cost} over {sum(1 for c in door.calls if not c['cached'])} calls (the probe included).")
    record.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {record} (${cost}); commit it -- it is never applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
