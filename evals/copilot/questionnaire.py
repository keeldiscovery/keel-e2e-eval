"""Spec 151 FR-1: the questionnaire fixture -- one back-test bundle's served respondent questions, in served order.

`extract(bundle)` reads `backtest.json` -> `respondents[*].served` (spec 062 FR-4.2, `evals.backtest.served_items`):
each link's gate (and its story prompt), then `parts[*].items[*]` -- `dimension`, `question`, `control`, `options`,
`escape`, `spoken{anchor, stem, countLine, optionsLine, escapeLine, under, over}`, `valueBox` -- with the link's idea
(`what`, `how`). Every item gets a stable `id` (`q1`, `q2`, ... in served order across the links, links in the bundle's
order) and the noise dataset's `kind` (`gate`, `single`, `multi` with `pick`, `number`, `free`), so the noise check's
`norm_out` and `ok` read an answer to it unchanged.

The bench is persona-agnostic: every command takes `QUESTIONNAIRE=<fixture>`; the committed fixture is the first
instance, not a special case. Nothing here names a trade or a study.

  python -m evals.copilot.questionnaire --bundle runs/<stamp>-backtest-<entry> --out evals/copilot/fixtures/q.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
DEFAULT_FIXTURE = FIXTURES / "questionnaire-08-fresco.json"
FIXTURE_VERSION = 1

#: Served control -> the noise dataset's kind (and `pick` for a multi). An unknown control is refused by name.
CONTROL_KIND = {
    "value_box": ("number", None),
    "cost_total": ("number", None),
    "price_ladder": ("single", None),
    "single_choice": ("single", None),
    "fixed_three": ("single", None),
    "fixed_four": ("single", None),
    "scale_four": ("single", None),
    "duration_bands": ("single", None),
    "benefit_with_advantages": ("single", None),
    "pick_two": ("multi", 2),
    "pick_one_then_one": ("multi", 2),
}
#: The served value box has no range; the number read is open-ended (`norm_out` needs one).
OPEN_RANGE = [0, 1_000_000_000]
GATE_OPTIONS = ["Yes", "No"]
SPOKEN_KEYS = ("anchor", "stem", "countLine", "optionsLine", "escapeLine", "under", "over", "transform")


class UnknownControl(ValueError):
    pass


def _spoken(raw: dict | None, question: str) -> dict:
    raw = raw or {}
    out = {k: raw[k] for k in SPOKEN_KEYS if raw.get(k) not in (None, "")}
    out.setdefault("stem", question)
    return out


def _item(n: int, link: str, raw: dict) -> dict:
    control = raw.get("control")
    if control not in CONTROL_KIND:
        raise UnknownControl(f"questionnaire refuses: control {control!r} ({raw.get('dimension')}) has no kind -- "
                             f"add it to CONTROL_KIND")
    kind, pick = CONTROL_KIND[control]
    item = {"id": f"q{n}", "link": link, "dimension": raw.get("dimension"), "control": control, "kind": kind,
            "question": raw.get("question"), "options": list(raw.get("options") or []),
            "escape": raw.get("escape"), "spoken": _spoken(raw.get("spoken"), raw.get("question"))}
    if pick:
        item["pick"] = pick
    if kind == "number":
        box = raw.get("valueBox") or {}
        item["unit"] = box.get("measure") or box.get("currency") or ("currency" if control == "cost_total" else None)
        item["range"] = list(OPEN_RANGE)
        if (box.get("nothing") or {}).get("label"):
            item["nothing"] = box["nothing"]["label"]
    if raw.get("askedAfter"):
        item["asked_after"] = [a.get("question") for a in raw["askedAfter"].get("answers") or []]
    return item


def extract(bundle: dict, *, source: str | None = None) -> dict:
    """The fixture from a loaded `backtest.json`."""
    links, items = {}, []
    for link, resp in (bundle.get("respondents") or {}).items():
        served = (resp or {}).get("served") or {}
        idea = served.get("idea") or {}
        links[link] = {"kind": served.get("kind"), "occasion": served.get("occasion"),
                       "idea": {"what": idea.get("what"), "how": idea.get("how")}}
        gate = served.get("gate")
        if gate:
            q = gate.get("question")
            items.append({"id": f"q{len(items) + 1}", "link": link, "dimension": gate.get("dimension"),
                          "control": "gate", "kind": "gate", "question": q, "options": list(GATE_OPTIONS),
                          "escape": None, "spoken": _spoken(gate.get("spoken"), q)})
            if gate.get("storyPrompt"):
                sp = gate["storyPrompt"]
                items.append({"id": f"q{len(items) + 1}", "link": link, "dimension": gate.get("dimension"),
                              "control": "story", "kind": "free", "question": sp, "options": [], "escape": None,
                              "spoken": {"stem": sp}})
        for part in served.get("parts") or []:
            for raw in part.get("items") or []:
                items.append(_item(len(items) + 1, link, raw))
    if not items:
        raise SystemExit("questionnaire refuses: the bundle serves no respondent item")
    return {"version": FIXTURE_VERSION, "source": source, "run": (bundle.get("run") or {}).get("id")
            if isinstance(bundle.get("run"), dict) else bundle.get("run"),
            "scope": bundle.get("scope"), "links": links, "items": items}


def load(path: str | Path | None = None) -> dict:
    path = Path(path) if path else DEFAULT_FIXTURE
    q = json.loads(path.read_text(encoding="utf-8"))
    if not q.get("items"):
        raise SystemExit(f"questionnaire refuses: {path} carries no items")
    q["path"] = str(path)
    return q


def by_id(q: dict) -> dict:
    return {it["id"]: it for it in q["items"]}


def noise_item(item: dict) -> dict:
    """The item in `evals.noise.dataset.ITEMS`' shape, so `evals.noise.pipeline.norm_out` reads it unchanged."""
    out = {"kind": item["kind"], "options": list(item.get("options") or []), "escape": item.get("escape"),
           "question": item.get("question"), "control": item.get("control")}
    if item.get("pick"):
        out["pick"] = item["pick"]
    if item["kind"] == "number":
        out["range"] = list(item.get("range") or OPEN_RANGE)
    return out


def labels(item: dict) -> list[str]:
    """Every label the founder or the respondent could say verbatim: the options and the escape."""
    return list(item.get("options") or []) + ([item["escape"]] if item.get("escape") else [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evals.copilot.questionnaire", description=__doc__.split("\n\n")[0])
    ap.add_argument("--bundle", required=True, help="a runs/<stamp>-backtest-<entry> folder or its backtest.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    path = Path(a.bundle)
    if path.is_dir():
        path = path / "backtest.json"
    fixture = extract(json.loads(path.read_text(encoding="utf-8")), source=path.parent.name)
    Path(a.out).write_text(json.dumps(fixture, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"questionnaire: {len(fixture['items'])} items from {len(fixture['links'])} link(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
