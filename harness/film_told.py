"""Spec 171: the judge reads the told card -- the Insights tab's *On your problem* view (keel-web 273's `told-card`,
keel-cloud 281's `BriefFacts.problem.told`) graded against what the stub strangers told.

The founder, 2026-11-25 ~12:55 ET: *"update the judge to evaluate for the problem, not only evaluate the insights -- in
the Insights, the new tab."* Three parts, all machinery (the scores are the rubric's, `quality/FILM-RUBRIC.md` *The told
card*):

* **The ground truth** (FR-1, `write_truth`): for every stub stranger who told a story on the film's link (the walk's
  `strangers.walks`, the screens bundle's `plans`), one told-reader call (`quality/readers/told-reader.md` `truth`, the
  film reader's model through its door) marks -- from the story's text alone, independent of Keel's reading -- which of
  the founder's limitations (the problem film's `story.json` `limits[]`, by index) the story describes happening,
  whether the way and the pain are the founder's, and whether it is a real occasion or a guess. Code adds the card the
  truth makes (`truth_card`: the tellers, each of the founder's rows' count and band). Written as `told_truth.json`
  beside `film.json`.
* **The capture** (FR-2, `capture`, on the stack after the answers): the wire (`standings.facts.problem.told`, each
  teller's `GET invitations/{id}` `experience` and `anchoring`, the story's board), the page as drawn (Insights ->
  *On your problem* (`insights-view-problem`) -> *What they told you* (`told-card`): its words, its marked parts and a
  screenshot) and three people's popups (Sent -> *What they said* (`row-open`) -> Insights (`popup-tab-insights`)):
  the first with a hit, the first with a new row, the first guess, where they exist (`sample`).
* **The comparison and the score** (FR-2 / FR-3 / FR-4, `compare`, `score`): per sampled person the ticks, the way and
  the pain against the truth; per row of the founder's the count and the band against the truth's; the verdict
  recomputed. T1 (the ticks), T2 (the counts) are code's over that; T3 (theirs are real) is code's over the
  told-reader's placing of each amber row in the stories; T4 (legible) is the told-reader's. `told_pct` beside
  `founder_pct`, never in `film_pct`. A card absent on a problem project scores nothing (`absent`) and is a DRIFT
  capture note; a T1 / T2 at 0 is a DRIFT finding naming the person or the row, both readings side by side
  (`quality.film_table.findings`).

Nothing here composes a respondent's question (FR-6): the stories are the corpus's people's recorded words, said by the
stub on the walk; the card's words are keel-cloud's and keel-web's.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Callable

from quality import film_rubric as fr

SPEC = "171"
#: FR-1: the truth file, beside the problem film's `film.json`.
TRUTH_FILE = "told_truth.json"
#: The version of the told card's four criteria (T1-T4, `quality/FILM-RUBRIC.md`), recorded in `told` (judgement call
#: 1: `FILM_RUBRIC_VERSION` stays 1 -- F, S, R and `film_pct` are untouched).
TOLD_VERSION = fr.TOLD_VERSION
T_CRITERIA = fr.T_CRITERIA

# ---- keel-web 273's test ids (its spec FR-2 / FR-3; read-only) and its words
VIEW_PROBLEM_ID = "insights-view-problem"
VIEW_ANSWERS_ID = "insights-view-answers"
TOLD_CARD_ID = "told-card"
ROW_OPEN_ID = "row-open"
POPUP_TAB_INSIGHTS_ID = "popup-tab-insights"
STORY_FOLD_ID = "insights-story-fold"
CARD_TITLE = "What they told you"
#: The three blocks in the founder's order (keel-web 273 FR-3; keel-cloud 281: way, limits, pain).
BLOCK_HEADINGS = ("How they do it today", "Where it falls short", "What it costs them")
BAND_WORDS = {"MOST": "reinforced by most", "SOME": "mentioned by some", "NONE": "not mentioned"}
TAG_WORDS = {"MOSTLY_KNOWN": "Mostly what you knew", "HALF_NEW": "Half new", "MOSTLY_NEW": "Mostly new"}
FOOT_LINE = "Counted from what people told, not from a question"
THEIRS_HEAD = "Theirs, not on your board"

# ---- the truth's words
MATCHES = ("same", "differs", "none")
OCCASIONS = ("real", "guess")
#: FR-2: the three people whose popups are read, in order.
SAMPLE_WHYS = ("the first with a hit", "the first with a new row", "the first guess")

#: The DRIFT capture note of an absent card (FR-3), and what owes it.
ABSENT_WHAT = "(capture): no told card"
ABSENT_OWED = ("keel-cloud 281 (`BriefFacts.problem.told` on a PROBLEM project once a story is told) / keel-web 273 "
               "FR-3 (the Insights tab's *On your problem* view, `told-card`)")


class ToldError(fr.FilmRubricError):
    """A told-reader answer, or a truth file, is not what this spec reads (a `RubricError`: asked once more with the
    fault named, as every reader is)."""


# ------------------------------------------------------------------------------------------------ the board

def board_of(story: dict | None) -> dict:
    """The founder's board as the film was built from it (the problem film's served story): the way (`act`, else the
    steps joined), the limitations in order (`limits[]`, the index keel-cloud 281's `limitsHit` points into), the
    pain (`cost`)."""
    story = story or {}
    steps = [s for s in story.get("steps") or [] if s]
    way = story.get("act") or ("; then ".join(steps) if steps else None)
    return {"way": way, "steps": steps, "limits": [x for x in story.get("limits") or [] if x],
            "pain": story.get("cost")}


def board_text(board: dict) -> str:
    lines = [f"  how they do it today: {board.get('way') or '(not said)'}", "  the limitations, numbered:"]
    lines += [f"    {i}. {x}" for i, x in enumerate(board.get("limits") or [], 1)] or ["    (none)"]
    lines.append(f"  what it costs them: {board.get('pain') or '(not said)'}")
    return "\n".join(lines)


def limit_name(board: dict, k: int) -> str:
    limits = board.get("limits") or []
    return f"limitation {k + 1} ({limits[k]})" if 0 <= k < len(limits) else f"limitation {k + 1}"


# ------------------------------------------------------------------------------------------------ the stories

def _plan_story(plans: list[dict], person: str) -> str | None:
    for p in plans or []:
        if p.get("person") == person and p.get("gate") and p.get("screener", "yes") == "yes" \
                and p.get("story_how", "said") == "said" and p.get("story"):
            return str(p["story"])
    return None


def stories_of(film: dict, bundle: dict | None = None) -> list[dict]:
    """FR-1: every stub stranger who told a story on the film's link, in walk order: `{person, invitation, story}` --
    the story the walk said (`walks[].story`, spec 171), else the person's plan in the screens bundle (`plans[].story`,
    a walk before 171) where the response carried a story. A chip tapped, a gate No or no words: no story."""
    strangers = film.get("strangers") or {}
    plans = (bundle or {}).get("plans") or []
    out = []
    for w in strangers.get("walks") or []:
        response = w.get("response") or {}
        if response and response.get("story") is False:
            continue
        text = w.get("story") or _plan_story(plans, w.get("person"))
        if text and not str(text).startswith("tap:"):
            out.append({"person": w.get("person"), "invitation": w.get("invitation"), "story": str(text)})
    return out


def bundle_of_film(film: dict) -> dict:
    """The screens bundle the film leg wrote (`backtest.json` in `screens_bundle`), or `{}`."""
    folder = film.get("screens_bundle")
    try:
        return json.loads((Path(folder) / "backtest.json").read_text(encoding="utf-8")) if folder else {}
    except (OSError, json.JSONDecodeError):
        return {}


# ------------------------------------------------------------------------------------------------ the truth (FR-1)

def truth_prompt(template: str, board: dict, story: str) -> str:
    from quality import readers                                                     # noqa: PLC0415
    return readers.fill(template, {"board": board_text(board), "story": story})


def parse_truth(raw: str, *, limits: int) -> dict:
    """One truth answer as `{limits: [k...] (0-based, ascending), own, way, way_said, pain, pain_said, occasion, why}`
    -- or `ToldError` (a limitation number the board does not have, a word outside its set, no why)."""
    from quality import rubric                                                      # noqa: PLC0415
    try:
        body = rubric.extract_json(raw)
    except rubric.RubricError as reason:
        raise ToldError(str(reason)) from None
    said = body.get("limits")
    if not isinstance(said, list) or not all(isinstance(n, int) and not isinstance(n, bool) for n in said):
        raise ToldError(f"limits must be a list of the board's limitation numbers; got {said!r}")
    odd = [n for n in said if not 1 <= n <= limits]
    if odd:
        raise ToldError(f"limits {odd} -- the board has limitations 1 to {limits}")
    out = {"limits": sorted({n - 1 for n in said})}
    own = body.get("own") or []
    if not isinstance(own, list):
        raise ToldError("own must be a list")
    out["own"] = [str(x).strip() for x in own if str(x).strip()][:2]
    for key, allowed in (("way", MATCHES), ("pain", MATCHES), ("occasion", OCCASIONS)):
        value = str(body.get(key) or "").strip().lower()
        if value not in allowed:
            raise ToldError(f"{key} must be one of {', '.join(allowed)}; got {body.get(key)!r}")
        out[key] = value
    out["way_said"] = str(body.get("way_said") or "").strip()
    out["pain_said"] = str(body.get("pain_said") or "").strip()
    out["why"] = str(body.get("why") or "").strip()
    if not out["why"]:
        raise ToldError("no why on the occasion's call")
    return out


def band(count: int | None, tellers: int) -> str:
    """keel-cloud 281's band: MOST where more than half of the tellers, SOME where at least one, NONE where nobody."""
    count = int(count or 0)
    if tellers and 2 * count > tellers:
        return "MOST"
    return "SOME" if count >= 1 else "NONE"


def verdict_of(yours: int, theirs: int) -> str | None:
    """keel-cloud 281's verdict from the share of the mentions that are theirs: under a third MOSTLY_KNOWN, a third to
    two thirds HALF_NEW, over two thirds MOSTLY_NEW; None while nobody mentioned anything."""
    total = yours + theirs
    if not total:
        return None
    share = theirs / total
    return "MOSTLY_KNOWN" if share < 1 / 3 else ("MOSTLY_NEW" if share > 2 / 3 else "HALF_NEW")


def truth_card(stories: list[dict], limits: int) -> dict:
    """The card the truth makes, as keel-cloud 281 counts it (FR-2): over the stories the truth reads as a real
    occasion (`tellers`; a guess counted in `guessed` and in no row), the founder's way, each limitation and the pain
    -- each a count and its band."""
    real = [s for s in stories if s.get("occasion") == "real"]
    n = len(real)

    def row(count):
        return {"count": count, "band": band(count, n)}
    return {"tellers": n, "guessed": sum(1 for s in stories if s.get("occasion") == "guess"),
            "way": row(sum(1 for s in real if s.get("way") == "same")),
            "limits": [{"k": k, **row(sum(1 for s in real if k in (s.get("limits") or [])))} for k in range(limits)],
            "pain": row(sum(1 for s in real if s.get("pain") == "same")),
            "theirs_said": sum(len(s.get("own") or []) + (s.get("way") == "differs") + (s.get("pain") == "differs")
                               for s in real)}


def write_truth(folder: Path, film: dict, story: dict, *, ask: Callable[[str, str], dict] | None,
                template: str, bundle: dict | None = None, reader: dict | None = None,
                dry_out: Path | None = None) -> dict | None:
    """FR-1: `told_truth.json` beside `film.json` -- one told-reader call a story (`ask(label, prompt)` -> the parsed
    answer, `quality.readers.ask_twice`'s shape), each story's reading, the card the truth makes. `dry_out` writes the
    prompts there and calls nothing (returns None). A story the reader could not read is kept in `unread`, counted
    nowhere."""
    board = board_of(story)
    told = stories_of(film, bundle if bundle is not None else bundle_of_film(film))
    if dry_out is not None:
        for i, s in enumerate(told, 1):
            (Path(dry_out) / f"told-truth-{i:02d}.prompt.txt").write_text(truth_prompt(template, board, s["story"]),
                                                                         encoding="utf-8")
        return None
    rows, unread = [], []
    for i, s in enumerate(told, 1):
        try:
            said = ask(f"told-truth-{i:02d}", truth_prompt(template, board, s["story"]))
        except Exception as reason:                                                 # noqa: BLE001 - kept, named
            unread.append({"n": i, "person": s["person"], "error": str(reason)[:300]})
            continue
        rows.append({"n": i, **s, **said})
    truth = {"spec": SPEC, "entry": (film.get("entry") or {}).get("id"), "project_id": film.get("project_id"),
             "written_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "reader": reader or {},
             "board": board, "stories": rows, "unread": unread, "card": truth_card(rows, len(board["limits"]))}
    (Path(folder) / TRUTH_FILE).write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return truth


def load_truth(folder: Path) -> dict | None:
    try:
        return json.loads((Path(folder) / TRUTH_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ------------------------------------------------------------------------------------------------ the capture (FR-2)

def sample(people: list[dict]) -> list[dict]:
    """FR-2: the three people whose popups are read -- the first with a hit (`limitsHit`), the first with a new row
    (`ownLimits`), the first guess (`guessed`, or `anchoring` GUESSED), each a different person, where they exist; none
    of them existing, the first person whose story was read. `[{person, invitation, why}]`."""
    picked: list[dict] = []
    tests = (lambda e, p: bool(e.get("limitsHit")), lambda e, p: bool(e.get("ownLimits")),
             lambda e, p: bool(e.get("guessed")) or p.get("anchoring") == "GUESSED")
    for why, test in zip(SAMPLE_WHYS, tests):
        for p in people:
            if p.get("invitation") in {x["invitation"] for x in picked}:
                continue
            if test(p.get("experience") or {}, p):
                picked.append({"person": p.get("person"), "invitation": p.get("invitation"), "why": why})
                break
    if not picked:
        first = next((p for p in people if p.get("experience") is not None), people[0] if people else None)
        if first:
            picked.append({"person": first.get("person"), "invitation": first.get("invitation"),
                           "why": "the first story read (none with a hit, a new row or a guess)"})
    return picked


#: Every marked part of an element (its `data-*` attributes) with its words, and its whole words -- keel-web 273's
#: inner markup is not pinned by its spec, so the card and the popup are read whole and by their data attributes.
READ_JS = """(el) => { if (!el) return null; const items = [];
  el.querySelectorAll('*').forEach((n) => { const a = {};
    for (const at of n.attributes) { if (at.name.startsWith('data-') || at.name === 'aria-selected') a[at.name] = at.value; }
    if (Object.keys(a).length) items.push({attrs: a, text: (n.innerText || '').trim().slice(0, 300)}); });
  return {text: (el.innerText || '').trim(), items: items.slice(0, 240)}; }"""


def _shot(locator, path: Path) -> str | None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        locator.screenshot(path=str(path))
        return str(path)
    except Exception:                                                               # noqa: BLE001 - the words still read
        return None


def card_on_screen(run, project_id: str, run_dir: Path) -> dict:
    """FR-2: the Insights tab's *On your problem* view as drawn -- the switch pressed, the told card's words, its marked
    parts and its screenshot (`<run_dir>/told/told-card.png`); `{"drawn": False, ...}` naming what was not there."""
    from harness import vectors_screens as vs_screens                               # noqa: PLC0415
    page = run.page
    out: dict[str, Any] = {"drawn": False, "switch": False}
    try:
        vs_screens.Answers(page, run.recorder, run.web)._report(project_id, "insights")
        switch = page.get_by_test_id(VIEW_PROBLEM_ID).first
        try:
            switch.wait_for(state="visible", timeout=15_000)
        except Exception:                                                           # noqa: BLE001 - named below
            out["error"] = f"no `{VIEW_PROBLEM_ID}` switch on the Insights tab (keel-web before 273)"
            return out
        out["switch"] = True
        switch.click()
        card = page.get_by_test_id(TOLD_CARD_ID).first
        card.wait_for(state="visible", timeout=15_000)
        out.update(drawn=True, **(card.evaluate(READ_JS) or {}))
        out["shot"] = _shot(card, Path(run_dir) / "told" / "told-card.png")
    except Exception as missed:                                                     # noqa: BLE001 - the read named
        out["error"] = str(missed)[:300]
    return out


def popup_on_screen(run, project_id: str, invitation: str, n: int, run_dir: Path) -> dict:
    """FR-2: one person's popup on Sent -- *What they said* (`row-open`) on their row, the Insights tab
    (`popup-tab-insights`), its words, its marked parts and its screenshot; closed after."""
    from harness import interviews_screens as ivs                                   # noqa: PLC0415
    page = run.page
    out: dict[str, Any] = {"drawn": False}
    try:
        page.goto(f"{run.web}/p/{project_id}/interviews/sent", wait_until="load")
        ivs.pass_interviews_sheet(page, run.recorder, run.web)
        row = page.locator(f"tr[data-invitation='{invitation}']").first
        row.wait_for(state="visible", timeout=20_000)
        row.get_by_test_id(ROW_OPEN_ID).first.click()
        tab = page.get_by_test_id(POPUP_TAB_INSIGHTS_ID).first
        tab.wait_for(state="visible", timeout=15_000)
        tab.click()
        dialog = page.locator("[role='dialog']").last
        dialog.wait_for(state="visible", timeout=10_000)
        out.update(drawn=True, **(dialog.evaluate(READ_JS) or {}))
        out["shot"] = _shot(dialog, Path(run_dir) / "told" / f"popup-{n}.png")
        page.keyboard.press("Escape")
    except Exception as missed:                                                     # noqa: BLE001 - the read named
        out["error"] = str(missed)[:300]
    return out


def wire_people(get: Callable[[str], Any], project_id: str, walks: list[dict]) -> list[dict]:
    """Each person who answered on the film's link, from `GET invitations/{id}`: their `experience` (keel-cloud 281's
    boxes, None where none) and `anchoring`."""
    out = []
    for w in walks or []:
        if not w.get("invitation"):
            continue
        detail = get(f"/v2/projects/{project_id}/invitations/{w['invitation']}") or {}
        interview = detail.get("interview") or {}
        out.append({"person": w.get("person"), "invitation": w["invitation"], "experience": detail.get("experience"),
                    "anchoring": interview.get("anchoring"), "has_story": bool(interview.get("story")),
                    "experience_served": "experience" in detail})
    return out


def capture(run, project_id: str, standings: dict, walks: list[dict], run_dir: Path) -> dict:
    """FR-2 on the stack, after the answers (`film_strangers.founder_page_after` on a PROBLEM project): the wire, the
    card as drawn, three people's popups. Each read kept, never a stop."""
    story = run.get(f"/v2/projects/{project_id}/story") or {}
    told = ((standings.get("facts") or {}).get("problem") or {}).get("told")
    people = wire_people(run.get, project_id, walks)
    out: dict[str, Any] = {"spec": SPEC, "wire": {"told": told, "board": board_of(story), "people": people}}
    out["card"] = card_on_screen(run, project_id, run_dir) if told else {"drawn": False, "skipped": "no told served"}
    out["sampled"] = []
    for n, pick in enumerate(sample(people) if told else [], 1):
        out["sampled"].append({**pick, "drawn": popup_on_screen(run, project_id, pick["invitation"], n, run_dir)})
    return out


# ------------------------------------------------------------------------------------------------ absent (FR-3)

def absent(captured: dict | None, truth: dict | None) -> dict | None:
    """FR-3: why the card scores nothing, or None. `drift` True where the card should have been there (a story was
    told on a PROBLEM project): no `told` served (a keel-cloud before 281), or served and not drawn (a keel-web before
    273). No story told: nothing to judge, no DRIFT."""
    stories = (truth or {}).get("stories") or []
    if captured is None:
        return {"why": "the walk captured no told card (a walk before spec 171)", "drift": False}
    if captured.get("error") and not captured.get("wire"):
        return {"why": f"the capture stopped: {captured['error']}", "drift": False}
    told = (captured.get("wire") or {}).get("told")
    if not told and not stories:
        return {"why": "no story told on the film's link: no card to judge", "drift": False}
    if not told:
        return {"why": "no `told` on the brief's facts (keel-cloud before 281)", "drift": True}
    if not (captured.get("card") or {}).get("drawn"):
        return {"why": "the told card was not drawn: " + str((captured.get("card") or {}).get("error")
                                                             or "no `told-card`"), "drift": True}
    if truth is None:
        return {"why": "no told_truth.json (the truth unread)", "drift": False}
    return None


# ------------------------------------------------------------------------------------------------ the comparison

def _by_invitation(rows: list[dict]) -> dict:
    return {r.get("invitation"): r for r in rows if r.get("invitation")}


def compare_people(captured: dict, truth: dict) -> list[dict]:
    """FR-2, per sampled person: Keel's reading (the served `experience` the popup is drawn from) beside the truth's --
    the ticks (`extra`: ticked, not in the truth; `missed`: in the truth, not ticked), the way and the pain."""
    wire = _by_invitation((captured.get("wire") or {}).get("people") or [])
    said = _by_invitation(truth.get("stories") or [])
    out = []
    for pick in captured.get("sampled") or []:
        inv = pick.get("invitation")
        keel = (wire.get(inv) or {}).get("experience") or {}
        true = said.get(inv)
        row = {"person": pick.get("person"), "invitation": inv, "why": pick.get("why"),
               "keel": {"limits": sorted(keel.get("limitsHit") or []), "way": keel.get("wayMatch") or "none",
                        "pain": keel.get("painMatch") or "none", "own": list(keel.get("ownLimits") or []),
                        "guessed": bool(keel.get("guessed"))},
               "popup_drawn": bool((pick.get("drawn") or {}).get("drawn"))}
        if true is None:
            row.update(truth=None, extra=row["keel"]["limits"], missed=[], off=len(row["keel"]["limits"]),
                       note="the truth holds no story for this person")
        else:
            t = set(true.get("limits") or [])
            k = set(row["keel"]["limits"])
            row["truth"] = {"limits": sorted(t), "way": true.get("way"), "pain": true.get("pain"),
                            "own": list(true.get("own") or []), "occasion": true.get("occasion")}
            row.update(extra=sorted(k - t), missed=sorted(t - k), off=len(k ^ t),
                       way_holds=row["keel"]["way"] == true.get("way"),
                       pain_holds=row["keel"]["pain"] == true.get("pain"))
        out.append(row)
    return out


def _within_one(served_band: str, truth_count: int, tellers: int) -> bool:
    return served_band in {band(c, tellers) for c in (truth_count - 1, truth_count, truth_count + 1) if c >= 0}


def compare_rows(captured: dict, truth: dict) -> list[dict]:
    """FR-2, per row of the founder's (the way, each limitation, the pain): the served count and band beside the
    truth's (`truth_card`); a row holds where its count is within one person of the truth's and its band is the band a
    count within one person of the truth's gives."""
    told = (captured.get("wire") or {}).get("told") or {}
    card = truth.get("card") or {}
    tellers = int(card.get("tellers") or 0)
    board = truth.get("board") or {}
    served_limits = {r.get("k"): r for r in (told.get("limits") or {}).get("yours") or []}
    rows = [("the way", (told.get("way") or {}).get("yours"), card.get("way"))]
    rows += [(limit_name(board, t["k"]), served_limits.get(t["k"]), t) for t in card.get("limits") or []]
    rows.append(("the pain", (told.get("pain") or {}).get("yours"), card.get("pain")))
    out = []
    for name, served, true in rows:
        true = true or {"count": 0, "band": "NONE"}
        if not served:
            out.append({"row": name, "keel": None, "truth": true, "holds": False, "note": "not served"})
            continue
        holds = abs(int(served.get("count") or 0) - int(true["count"])) <= 1 \
            and _within_one(str(served.get("band")), int(true["count"]), tellers)
        out.append({"row": name, "keel": {"count": served.get("count"), "band": served.get("band")}, "truth": true,
                    "holds": holds})
    return out


def theirs_rows(captured: dict) -> list[dict]:
    """The amber rows as served, numbered in the card's order (the way's, the limitations', the pain's)."""
    told = (captured.get("wire") or {}).get("told") or {}
    out = []
    for block in ("way", "limits", "pain"):
        for r in (told.get(block) or {}).get("theirs") or []:
            out.append({"row": len(out) + 1, "block": block, "label": r.get("label"), "count": r.get("count"),
                        "words": list(r.get("words") or [])})
    return out


def compare_verdict(captured: dict, truth: dict, placed: list[dict] | None = None) -> dict:
    """FR-2: the verdict served beside the one the truth gives -- the founder's rows' mentions from the truth, theirs
    the amber rows the told-reader placed in two or more stories (each weighed by its stories)."""
    told = (captured.get("wire") or {}).get("told") or {}
    card = truth.get("card") or {}
    yours = int((card.get("way") or {}).get("count") or 0) + int((card.get("pain") or {}).get("count") or 0) \
        + sum(int(r.get("count") or 0) for r in card.get("limits") or [])
    theirs = sum(len(p.get("stories") or []) for p in placed or [] if len(p.get("stories") or []) >= 2
                 and not p.get("founders"))
    want = verdict_of(yours, theirs)
    return {"keel": told.get("verdict"), "truth": want, "holds": told.get("verdict") == want,
            "tellers": {"keel": told.get("tellers"), "truth": card.get("tellers")},
            "guessed": {"keel": told.get("guessed"), "truth": card.get("guessed")}}


# ------------------------------------------------------------------------------------------------ T1 - T3 (code's)

def _mark_by_off(off: int) -> int:
    return 2 if off == 0 else (1 if off == 1 else 0)


def t1(people: list[dict], board: dict) -> tuple[int, str, str | None]:
    """T1 the ticks are right: every limitation ticked across the sampled people is in the truth and none missed -- 2
    all right, 1 one off, 0 more."""
    off = sum(p["off"] for p in people)
    wrong = [p for p in people if p["off"]]
    if not people:
        return 2, "No person's popup was sampled: no tick to be wrong.", None
    if not wrong:
        return 2, f"All {len(people)} sampled people's ticks match what their stories describe.", None
    first = wrong[0]
    parts = ([f"ticked {', '.join(limit_name(board, k) for k in first['extra'])} the story does not describe"]
             if first["extra"] else []) + ([f"missed {', '.join(limit_name(board, k) for k in first['missed'])}"]
                                           if first["missed"] else [])
    why = (f"{off} tick{'s' if off != 1 else ''} off across {len(wrong)} of {len(people)} sampled people; "
           f"{first['person']}: {' and '.join(parts)}.")
    instead = "; ".join(f"{p['person']}: tick {', '.join(str(k + 1) for k in (p.get('truth') or {}).get('limits') or [])
                                                 or 'none'} of the founder's limitations" for p in wrong)
    return _mark_by_off(off), why, instead


def t2(rows: list[dict], tellers: int) -> tuple[int, str, str | None]:
    """T2 the counts add up: each of the founder's rows' count and band within one person of the truth's -- 2, 1 one
    row off, 0 more."""
    off = [r for r in rows if not r["holds"]]
    if not off:
        return 2, f"Every one of the founder's {len(rows)} rows matches the truth's count within one of {tellers}.", None
    first = off[0]
    keel = first.get("keel") or {}
    why = (f"{len(off)} of {len(rows)} rows off; {first['row']}: Keel {keel.get('count', 'nothing')} "
           f"({keel.get('band', 'not served')}), the stories {first['truth']['count']} of {tellers} "
           f"({first['truth']['band']}).")
    instead = "; ".join(f"{r['row']}: {r['truth']['count']} of {tellers}, {BAND_WORDS[r['truth']['band']]}" for r in off)
    return _mark_by_off(len(off)), why, instead


def t3(theirs: list[dict], placed: list[dict], board: dict) -> tuple[int, str, str | None]:
    """T3 theirs are real: every amber row said by two or more stories of the truth and not one of the founder's
    reworded -- 2, 1 one row wrong, 0 more. `placed` is the told-reader's `theirs` (`{row, stories, founders}`)."""
    by = {p.get("row"): p for p in placed or []}
    wrong = []
    for r in theirs:
        p = by.get(r["row"]) or {}
        stories = sorted(set(p.get("stories") or []))
        if p.get("founders"):
            wrong.append((r, f"is the founder's {p['founders']} reworded"))
        elif len(stories) < 2:
            wrong.append((r, f"is said by {len(stories)} stor{'y' if len(stories) == 1 else 'ies'}, not two or more"))
    if not theirs:
        return 2, "No amber row served: nothing claimed as theirs.", None
    if not wrong:
        return 2, f"All {len(theirs)} amber rows are said by two or more stories and none is the founder's.", None
    r, what = wrong[0]
    why = f"{len(wrong)} of {len(theirs)} amber rows wrong; *{r['label']}* {what}."
    instead = "; ".join(f"*{r['label']}*: " + ("fold it into the founder's row" if (by.get(r["row"]) or {}).get(
        "founders") else "leave it off until two stories say it") for r, _ in wrong)
    return _mark_by_off(len(wrong)), why, instead


def drawn_notes(captured: dict) -> list[str]:
    """What code finds on the card's drawn words before the told-reader reads them (T4's evidence): the title, the
    three blocks in the founder's order, the served tag and band words, the foot line."""
    card = captured.get("card") or {}
    text = " ".join(str(card.get("text") or "").split())
    told = (captured.get("wire") or {}).get("told") or {}
    notes = []
    if CARD_TITLE not in text:
        notes.append(f"the title *{CARD_TITLE}* is not drawn")
    at = [text.find(h) for h in BLOCK_HEADINGS]
    if any(i < 0 for i in at):
        notes.append("a block heading is not drawn: " + ", ".join(h for h, i in zip(BLOCK_HEADINGS, at) if i < 0))
    elif at != sorted(at):
        notes.append("the three blocks are not in the founder's order (way, limitations, pain)")
    tag = TAG_WORDS.get(told.get("verdict") or "")
    if tag and tag not in text:
        notes.append(f"the tag *{tag}* (verdict {told.get('verdict')}) is not drawn")
    served = {r.get("band") for r in [(told.get("way") or {}).get("yours") or {}, (told.get("pain") or {}).get("yours")
                                      or {}, *((told.get("limits") or {}).get("yours") or [])] if r}
    for b in sorted(x for x in served if x in BAND_WORDS):
        if BAND_WORDS[b] not in text:
            notes.append(f"the band word *{BAND_WORDS[b]}* ({b}) is not drawn")
    if FOOT_LINE not in text:
        notes.append(f"the foot line *{FOOT_LINE}* is not drawn")
    return notes


# ------------------------------------------------------------------------------------------------ the card call (T3, T4)

def served_text(captured: dict, board: dict) -> str:
    told = (captured.get("wire") or {}).get("told") or {}
    lines = [f"  verdict: {told.get('verdict')} ({TAG_WORDS.get(told.get('verdict') or '', 'no tag')}); "
             f"{told.get('tellers')} told a time, {told.get('guessed')} read as a guess"]
    way = (told.get("way") or {}).get("yours") or {}
    lines.append(f"  1 How they do it today -- yours: {way.get('label')} -- {way.get('count')} ({way.get('band')}); "
                 f"not said {(told.get('way') or {}).get('notSaid')}")
    lines.append("  2 Where it falls short -- yours:")
    for r in (told.get("limits") or {}).get("yours") or []:
        lines.append(f"    {limit_name(board, int(r.get('k') or 0))} -- {r.get('count')} ({r.get('band')})")
    pain = (told.get("pain") or {}).get("yours") or {}
    lines.append(f"  3 What it costs them -- yours: {pain.get('label')} -- {pain.get('count')} ({pain.get('band')}); "
                 f"not said {(told.get('pain') or {}).get('notSaid')}")
    rows = theirs_rows(captured)
    lines.append(f"  {THEIRS_HEAD} (amber), numbered:" if rows else f"  {THEIRS_HEAD}: none served")
    lines += [f"    {r['row']}. [{r['block']}] {r['label']} -- {r['count']} people: " + " / ".join(r["words"])
              for r in rows]
    return "\n".join(lines)


def truth_text(truth: dict) -> str:
    rows = []
    for s in truth.get("stories") or []:
        rows.append(f"  story {s['n']} ({s.get('person')}), {s.get('occasion')}: \"{s.get('story')}\"\n"
                    f"    limitations described: {', '.join(str(k + 1) for k in s.get('limits') or []) or 'none'}; "
                    f"own: {'; '.join(s.get('own') or []) or 'none'}; way {s.get('way')}"
                    + (f" ({s['way_said']})" if s.get("way_said") else "") + f"; pain {s.get('pain')}"
                    + (f" ({s['pain_said']})" if s.get("pain_said") else ""))
    return "\n".join(rows) or "  (no story)"


def drawn_text(captured: dict) -> str:
    card = captured.get("card") or {}
    parts = ["The card (`told-card`), as drawn:", "  " + " / ".join(str(card.get("text") or "(no words)").splitlines())]
    for i, pick in enumerate(captured.get("sampled") or [], 1):
        drawn = pick.get("drawn") or {}
        parts.append(f"Popup {i} -- {pick.get('person')} ({pick.get('why')}), its Insights tab:")
        parts.append("  " + (" / ".join(str(drawn.get("text") or "").splitlines()) if drawn.get("drawn")
                             else f"(not drawn: {drawn.get('error')})"))
    return "\n".join(parts)


def card_images(captured: dict) -> list[dict]:
    out = []
    card = captured.get("card") or {}
    if card.get("shot"):
        out.append({"label": "Screenshot -- the told card (*On your problem*), as drawn", "path": card["shot"]})
    for i, pick in enumerate(captured.get("sampled") or [], 1):
        shot = (pick.get("drawn") or {}).get("shot")
        if shot:
            out.append({"label": f"Screenshot -- popup {i}, {pick.get('person')}'s Insights tab", "path": shot})
    return [i for i in out if Path(i["path"]).is_file()]


def card_request(captured: dict, truth: dict, *, persona: str, template: Callable[[str], str], rubric: str,
                 cfg: dict) -> dict:
    """The one Messages API request for the card (T3's placing, T4): the text, the screenshots, the text after --
    `{body, text, images}` as `quality.film_reader.build_request` returns."""
    import base64                                                                   # noqa: PLC0415

    from quality import readers                                                     # noqa: PLC0415
    board = truth.get("board") or {}
    notes = drawn_notes(captured)
    values = {"persona": persona, "board": board_text(board), "truth": truth_text(truth),
              "served": served_text(captured, board), "drawn": drawn_text(captured),
              "notes": "\n".join(f"- {n}" for n in notes) or "- nothing", "rubric": rubric}
    before = readers.fill(template("card-before-images"), values)
    after = readers.fill(template("card-after-images"), values)
    content, named = [{"type": "text", "text": before}], [before]
    for image in card_images(captured):
        data = Path(image["path"]).read_bytes()
        content += [{"type": "text", "text": image["label"]},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                 "data": base64.b64encode(data).decode("ascii")}}]
        named.append(f"{image['label']}\n[image: {image['path']}, {len(data)} bytes]")
    content.append({"type": "text", "text": after})
    named.append(after)
    body = {"model": cfg["model"], "max_tokens": int(cfg.get("max_tokens", 16000)),
            "output_config": {"effort": cfg["effort"]}, "thinking": {"type": "adaptive"}, "fallbacks": "default",
            "messages": [{"role": "user", "content": content}]}
    return {"body": body, "text": "\n\n".join(named), "images": sum(1 for c in content if c["type"] == "image"),
            "notes": notes}


def text_request(prompt: str, cfg: dict) -> dict:
    """A text-only request through the film reader's door (the truth's calls)."""
    body = {"model": cfg["model"], "max_tokens": int(cfg.get("max_tokens", 16000)),
            "output_config": {"effort": cfg["effort"]}, "thinking": {"type": "adaptive"}, "fallbacks": "default",
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]}
    return {"body": body, "text": prompt}


def parse_card_answer(raw: str, *, rows: int) -> dict:
    """The card call's answer: `theirs` (every amber row placed: `{row, stories, founders}`), `t4` 0-2, `why4`, and
    `instead4` where T4 is under 2 -- or `ToldError`."""
    from quality import rubric                                                      # noqa: PLC0415
    try:
        body = rubric.extract_json(raw)
        t4_mark = rubric._mark(body.get("t4"), "t4", nullable=False)
    except rubric.RubricError as reason:
        raise ToldError(str(reason)) from None
    placed = []
    for p in body.get("theirs") or []:
        if not isinstance(p, dict) or not isinstance(p.get("row"), int):
            raise ToldError(f"a theirs entry without its row number: {p!r}")
        stories = [n for n in p.get("stories") or [] if isinstance(n, int) and not isinstance(n, bool)]
        founders = p.get("founders")
        placed.append({"row": p["row"], "stories": sorted(set(stories)),
                       "founders": str(founders).strip() if founders not in (None, "", "null", "none") else None})
    unplaced = sorted(set(range(1, rows + 1)) - {p["row"] for p in placed})
    if unplaced:
        raise ToldError(f"amber rows {unplaced} not placed: every amber row is placed in the stories")
    why = str(body.get("why4") or "").strip()
    if not why:
        raise ToldError("t4 has no why")
    instead = str(body.get("instead4") or "").strip()
    if t4_mark < 2 and not instead:
        raise ToldError("t4 is under 2 and has no instead line")
    return {"theirs": placed, "t4": t4_mark, "why4": why, "instead4": instead if t4_mark < 2 else ""}


# ------------------------------------------------------------------------------------------------ the score (FR-3)

def absent_block(why: dict) -> dict:
    """FR-3: the card absent -- nothing scored (`told_pct` None), the reason, the DRIFT note where it is owed."""
    return {"version": TOLD_VERSION, "absent": why["why"], "drift": bool(why.get("drift")), "scores": None,
            "whys": None, "instead": None, "told_pct": None, "flagged": False}


def score(captured: dict | None, truth: dict | None, card_answer: dict | None) -> dict:
    """FR-3: the `told` block of the problem film's score file -- T1-T4 (T1-T3 code's over the comparison, T3 over the
    told-reader's placing, T4 the told-reader's), one why each, `instead` under 2, `told_pct` (the sum over 2 x 4 x
    100), `flagged` on a 0; the people, the rows, the amber rows and the verdict compared, kept for the table and DRIFT.
    An absent card is `absent_block`."""
    gone = absent(captured, truth)
    if gone:
        return absent_block(gone)
    if card_answer is None:
        return absent_block({"why": "the told-reader's card call was not read", "drift": False})
    board = truth.get("board") or {}
    people = compare_people(captured, truth)
    rows = compare_rows(captured, truth)
    theirs = theirs_rows(captured)
    tellers = int((truth.get("card") or {}).get("tellers") or 0)
    marks = {}
    marks["t1"] = t1(people, board)
    marks["t2"] = t2(rows, tellers)
    marks["t3"] = t3(theirs, card_answer.get("theirs") or [], board)
    marks["t4"] = (card_answer["t4"], card_answer["why4"], card_answer.get("instead4") or None)
    scores = {c: marks[c][0] for c in T_CRITERIA}
    return {"version": TOLD_VERSION, "absent": None, "drift": False, "scores": scores,
            "whys": {c: marks[c][1] for c in T_CRITERIA},
            "instead": {c: marks[c][2] for c in T_CRITERIA if scores[c] < 2 and marks[c][2]},
            "told_pct": fr.told_pct(scores), "flagged": any(v == 0 for v in scores.values()),
            "people": people, "rows": rows, "theirs": placed_rows(theirs, card_answer.get("theirs") or []),
            "verdict": compare_verdict(captured, truth, card_answer.get("theirs")),
            "notes": drawn_notes(captured), "tellers": tellers}


def placed_rows(theirs: list[dict], placed: list[dict]) -> list[dict]:
    """Each amber row as served with the told-reader's placing beside it (`stories`, `founders`)."""
    by = {p.get("row"): p for p in placed}
    return [{**r, "stories": (by.get(r["row"]) or {}).get("stories") or [],
             "founders": (by.get(r["row"]) or {}).get("founders")} for r in theirs]


def drift_items(told: dict | None) -> list[dict]:
    """FR-4: the DRIFT findings a `told` block owes -- a T1 at 0, one a person whose ticks are off; a T2 at 0, one a
    row off -- each naming the person or the row with the truth and Keel's reading side by side; FR-3: an absent card
    owed by the product, one capture note."""
    told = told or {}
    if told.get("absent"):
        return [{"criterion": "capture", "what": ABSENT_WHAT, "owed": ABSENT_OWED, "detail": told["absent"]}] \
            if told.get("drift") else []
    out = []
    scores = told.get("scores") or {}
    if scores.get("t1") == 0:
        for p in told.get("people") or []:
            if p.get("off"):
                truth = (p.get("truth") or {}).get("limits")
                out.append({"criterion": "T1", "what": f"the ticks are wrong on {p['person']}'s popup",
                            "owed": "keel-cloud 281 FR-1 (EXPERIENCE_READ's `limits_hit`)",
                            "detail": f"{p['person']}: the truth -- the story describes limitations "
                                      f"{_numbers(truth)}; Keel's reading -- ticked {_numbers(p['keel']['limits'])} "
                                      f"(extra {_numbers(p.get('extra'))}, missed {_numbers(p.get('missed'))})"})
    if scores.get("t2") == 0:
        for r in told.get("rows") or []:
            if not r.get("holds"):
                keel = r.get("keel") or {}
                out.append({"criterion": "T2", "what": f"the count of {r['row']} does not add up",
                            "owed": "keel-cloud 281 FR-3 (`BriefFacts.problem.told`'s counts and bands)",
                            "detail": f"{r['row']}: the truth -- {r['truth']['count']} of {told.get('tellers')} "
                                      f"({r['truth']['band']}); Keel's reading -- {keel.get('count', 'not served')} "
                                      f"({keel.get('band', 'not served')})"})
    return out


def _numbers(ks) -> str:
    ks = list(ks or [])
    return ", ".join(str(int(k) + 1) for k in ks) if ks else "none"
