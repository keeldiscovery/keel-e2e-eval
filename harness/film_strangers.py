"""Spec 165: the strangers on the film's link -- the film's own project locked, its link sent to the entry's seven
people, each walking the four questions on the film link, and the founder's page read after them; then one bundle
`make read-screens` reads (the strangers' screens, §A and R6; the founder's page after the answers, §B).

Spec 163 told the problem by voice on one project and ran the back-test on a second, typed one (its judgement call 1),
so the question score graded the typed path and the page score a page the film never fed. Here the film's project is
the study the people answer (the founder, 2026-11-24: *"the quality of the questions shown to the respondent ... the
film ... post that the interview, the dashboard and the insights"* -- all of one study):

* **The lock** (`lock_project`, FR-1): the window stored (`PUT context/window`, the entry's recall window), the
  PROBLEM calibration answered at the boxes' yes (keel-cloud 269 FR-6: no belief page), the credits read (a short
  balance topped to the grant by the stand-in `three_views.fr1_d` uses), the ready page's lock pressed, the questions
  READY. Any step that does not hold raises `LockFailed` naming the step -- the walk never goes on unlocked.
* **The seven** (`people_plans`, FR-1): the corpus's people the PROBLEM scope sends, the first `people` of them
  (`quality/cycle.toml`, seven; `vectors_script.study_people`), each person's recorded answers mapped onto the four
  questions as spec 161 FR-6 maps them (`vectors_script.person_inputs` through `instructions/corpus.picks_269`): the
  screener by `in_segment`, the gate by `recency`, the person's own story (a recorded chip tapped where the page draws
  one), Frequency's five by the person's code, Importance's pick by the person's first code (`own` the own row,
  `rival_<k>` the k-th row that is not), every why answered in the person's own recorded words where the file has
  them (else spec 161's line for the rung). Each walks the film link on the orb (`three_views_strangers.walk_link`:
  the opening, the screener, the film, *Did this happen to you?*, the experience, Frequency, Importance, the whys,
  the pilot ask, the thanks).
* **The founder's page after them** (FR-2): the themes let settle, then the back-test's answers leg
  (`backtest.answers_leg`: the stage page, each card opened with its chart, the Insights screen and its folds -- §B's
  screens) and spec 164's reads of the page as drawn (`three_views_strangers.founder_page_on_screen`: the ways panel,
  Frequency's card, the Insights boxes, the brief's breakdown), the brief's lines from the standings (§G).
* **The bundle** (`screens_bundle`, FR-2): `backtest.json` in the leg's evidence folder, `kind: "film"` -- the one
  project, no founder screens (the founder's beats are read by `make read-films`' founder-reader, 163 FR-1), the
  watched person's drawn screens on the link (`respondents`, one person a link as every back-test reads it), every
  walk's summary, the screens after the answers, the brief. `make read-screens RUN=<that folder>` reads it.

Machinery, not judgement: nothing here composes a question; the words are keel-cloud's and keel-web's.
"""

from __future__ import annotations

import dataclasses
import time
from pathlib import Path
from typing import Any, Callable

#: The PROBLEM study's link kind (the person's own link).
LINK = "PRIMARY"
#: The scope the film's project is created with (keel-cloud 133).
SCOPE = "PROBLEM"
#: Spec 166: the solution's project (keel-cloud 271: a SOLUTION project made on the problem's, `parentProjectId`).
SOLUTION_SCOPE = "SOLUTION"
#: Spec 166 FR-3: the solution's bundle kind (`make read-screens` reads it as the film's, `quality/readers.FILM_KINDS`).
SOLUTION_KIND = "film-solution"
#: The window stored where the entry records none (`three_views.STORY_WINDOW`'s shape).
DEFAULT_WINDOW = {"count": 7, "unit": "NIGHTS"}
#: How long the lock's waits stand (seconds).
CALIBRATION_WAIT_S = 60
QUESTIONS_WAIT_S = 120
SETTLE_WAIT_S = 120
#: Importance's codes in the corpus read through keel-cloud 269 (`instructions/corpus.py`): the own row, the others.
OWN_CODE = "own"
RIVAL_PREFIX = "rival_"


class LockFailed(AssertionError):
    """The film's project did not lock: the step that did not hold, named (FR-4)."""

    def __init__(self, step: str, detail: Any = None):
        self.step = step
        self.detail = detail
        super().__init__(lock_refusal(step, detail))


def lock_refusal(step: str, detail: Any = None) -> str:
    """The one sentence the leg fails with when the lock does not hold: the step named, then what it answered."""
    said = f" -- {str(detail)[:400]}" if detail not in (None, "", {}, []) else ""
    return (f"spec 165 refuses: the film's project did not lock at {step}{said}; no link is sent on an unlocked "
            "project and no stranger walks")


# ------------------------------------------------------------------------------------------------ the people

def recall_window(entry_yaml: dict | None) -> dict:
    """The window the film's project is stored with: the entry's `context.recall_window` (`{count, unit}`), else the
    default (the fake script's)."""
    window = ((entry_yaml or {}).get("context") or {}).get("recall_window") or {}
    if isinstance(window, dict) and window.get("count") and window.get("unit"):
        return {"count": int(window["count"]), "unit": str(window["unit"])}
    return dict(DEFAULT_WINDOW)


def _codes(person, dimension: str) -> list[str]:
    for pick in getattr(person, "picks", None) or []:
        if getattr(pick, "dimension", None) == dimension:
            return [str(c) for c in (getattr(pick, "codes", None) or [])]
    return []


def people_plans(people: list) -> list[dict]:
    """FR-1: one plan a person (`vectors_script.PersonInputs`, the study's own-link people in corpus order), the
    corpus's answers mapped onto the four questions: `screener` (`no` where the person is outside the segment), `gate`
    (the recorded *yes*), `story` (their words), `story_how` (`chip-tap` where they recorded a chip), `frequency` (one of
    the five codes), `importance` (their codes, first first), `own` (their first pick is the own row), `why` (their own
    recorded follow-up words, or None for spec 161's line). The decision-makers' link is not this study's."""
    out = []
    for p in people:
        if getattr(p, "link", LINK) != LINK:
            continue
        frequency = _codes(p, "problem.frequency")
        importance = _codes(p, "problem.importance")
        out.append({
            "person": p.person,
            "screener": "yes" if getattr(p, "in_segment", True) else "no",
            "gate": bool(p.recency),
            "story": (p.story or None) if p.recency else None,
            "story_how": "chip-tap" if (p.recency and getattr(p, "anchor_chip", None)) else "said",
            "chip": getattr(p, "anchor_chip", None),
            "frequency": frequency[0] if (p.recency and frequency) else None,
            "importance": importance,
            "own": bool(importance) and importance[0] == OWN_CODE,
            "why": getattr(p, "follow_up", None) or None,
        })
    return out


def _bare(text) -> str:
    import re                                                                       # noqa: PLC0415
    return " ".join(re.findall(r"[a-z0-9']+", str(text or "").lower().replace("’", "'")))


def importance_pick(item: dict, code: str | None, *, own_label: str | None, other_tasks) -> str | None:
    """The label a person's Importance code picks among the served rows: `own` the own row (`three_surfaces.own_option`),
    `rival_<k>` the k-th served row that is not the own row (clamped to the last), anything else the first such row."""
    from harness import three_surfaces as ts                                        # noqa: PLC0415
    labels = [o.get("label") for o in item.get("options") or [] if o.get("label")]
    if not labels:
        return None
    mine = ts.own_option(item, other_tasks=other_tasks, own_label=own_label)
    mine_label = (mine or {}).get("label")
    if code == OWN_CODE and mine_label:
        return mine_label
    rest = [x for x in labels if _bare(x) != _bare(mine_label)] or labels
    k = 1
    if code and code.startswith(RIVAL_PREFIX):
        try:
            k = max(1, int(code[len(RIVAL_PREFIX):]))
        except ValueError:
            k = 1
    return rest[min(k, len(rest)) - 1]


def walk_plan(plan: dict, interview: dict, *, own_label: str | None, other_tasks) -> dict:
    """The plan `three_views_strangers.link_walk` walks (spec 161's keys, plus `pick` and `why`)."""
    from harness import three_surfaces as ts                                        # noqa: PLC0415
    item = ts.item_of(interview, ts.IMPORTANCE)
    first = plan["importance"][0] if plan.get("importance") else None
    return {"who": plan["person"], "screener": plan["screener"], "gate": plan["gate"],
            "story": plan.get("story"), "frequency": plan.get("frequency"), "own": plan.get("own"),
            "own_label": own_label, "other_tasks": list(other_tasks or []),
            "pick": importance_pick(item, first, own_label=own_label, other_tasks=other_tasks) if item else None,
            "why": plan.get("why")}


# ------------------------------------------------------------------------------------------------ spec 166: the solution

def solution_plans(people: list) -> list[dict]:
    """Spec 166 FR-3: one plan a person of the SOLUTION study (`vectors_script.person_inputs` under SOLUTION, the first
    `people` own-link people in corpus order), their recorded answers read on the link spec 162 walks: the screener by
    `in_segment`, the check *Did this happen to you?* by `recency` (a No leaves before the plate), the three yes-or-no
    questions by the person's recorded pick read through keel-cloud 272 (`corpus.spec272_solution`: what the old
    registry counted for is yes, against is no); a pick the link cannot carry (a chip -- `yes_no` has no escape -- or
    none recorded) is answered *No* and named (`remapped`, spec 064 FR-7's rule); every why in the person's own recorded
    words where the file has them (else spec 162's line for the rung)."""
    from harness import solution_surfaces as sol                                    # noqa: PLC0415
    from instructions import corpus as corpus_reader                                # noqa: PLC0415
    out = []
    for p in people:
        if getattr(p, "link", LINK) != LINK:
            continue
        picks, remapped = {}, []
        answers = bool(p.recency) and getattr(p, "in_segment", True)       # sent away before the three: nothing owed
        for key in sol.SOLUTION_DIMENSIONS:
            codes = _codes(p, key)
            read = corpus_reader.spec272_solution(codes[0]) if codes else None
            if read in sol.YES_NO_CODES:
                picks[key] = read
            else:
                picks[key] = "no"
                if answers:
                    remapped.append({"dimension": key, "recorded": codes[0] if codes else None, "sent": "no"})
        out.append({"person": p.person, "screener": "yes" if getattr(p, "in_segment", True) else "no",
                    "gate": bool(p.recency), "picks": picks, "why": getattr(p, "follow_up", None) or None,
                    **({"remapped": remapped} if remapped else {})})
    return out


def solution_walk_plan(plan: dict) -> dict:
    """The plan `three_views_strangers.link_walk` walks on a solution link (spec 162's `picks`, plus `why`)."""
    return {"who": plan["person"], "screener": plan["screener"], "gate": plan["gate"],
            "picks": dict(plan.get("picks") or {}), "why": plan.get("why")}


def owed_whys(plan: dict) -> list[str]:
    """The whys a person of the solution study is owed (keel-cloud 272 FR-2): every No in the order asked, at most two
    -- none where the screener or the check sent them away."""
    from harness import solution_surfaces as sol                                    # noqa: PLC0415
    if plan.get("screener") == "no" or not plan.get("gate"):
        return []
    return sol.owed(plan.get("picks") or {})[0]


def walk_solution_people(run: "FilmRun", project_id: str, plans: list[dict], *, out: dict) -> list[dict]:
    """Spec 166 FR-3: one TEXT link a person on the solution's project, each walked on the solution link (the opening,
    the screener, the problem's film, the check, the plate, the solution's film, the three questions, the whys, the
    pilot ask) with their plan; every walk kept, a walk that stops recorded and the next walked."""
    from evals import three_views_strangers as tvs                                   # noqa: PLC0415
    links = tvs.make_links(run, project_id, [p["person"] for p in plans])
    out.update(links=links)
    summaries = []
    for i, (plan, link) in enumerate(zip(plans, links), 1):
        interview, walked, error = {}, None, None
        try:
            interview, _ = tvs.read_served(run, link["url"])
            walked = tvs.walk_link(run, link["url"], interview, shot=f"film-166-person-{i}",
                                   plan=solution_walk_plan(plan))
        except Exception as stopped:  # noqa: BLE001 - one person's stop is recorded; the others still walk
            error = f"{type(stopped).__name__}: {str(stopped)[:600]}"
        out.setdefault("walked", {})[plan["person"]] = walked
        out.setdefault("interviews", {})[plan["person"]] = interview
        summary = walk_summary(plan, link, walked, error=error)
        summary["plan"] = {k: plan.get(k) for k in ("screener", "gate", "picks", "remapped")}
        summary["owed"] = owed_whys(plan)
        summaries.append(summary)
    return summaries


def solution_watched(plans: list[dict]) -> str | None:
    """The one person whose screens the respondent-reader reads on the solution link: the first inside the segment who
    passed the check and is owed a why (the most screens drawn), else the first who passed, else the first."""
    inside = [p for p in plans if p["screener"] == "yes" and p["gate"]]
    owed = [p for p in inside if owed_whys(p)]
    pick = (owed or inside or plans or [None])[0]
    return pick["person"] if pick else None


# ------------------------------------------------------------------------------------------------ the lock

def calibration_ready(view: Any, scope: str = SCOPE) -> bool:
    """The scope's calibration with nothing owed: READY -- or on a spoken SOLUTION project (keel-cloud 271 FR-8: the
    three beliefs written at the board's yes) its three questions answered (spec 162's `solution_calibration_answered`)."""
    if not isinstance(view, dict):
        return False
    if view.get("state") == "READY":
        return True
    return scope == SOLUTION_SCOPE and view.get("total") == 3 and int(view.get("answered") or 0) >= 3


def lock_project(call: Callable[[str, str, dict | None], tuple[int, Any]], project_id: str, *, window: dict | None,
                 press: Callable[[], tuple[int, Any]], need: int, top_up: Callable[[], Any] | None = None,
                 sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic,
                 calibration_wait_s: float = CALIBRATION_WAIT_S, questions_wait_s: float = QUESTIONS_WAIT_S,
                 scope: str = SCOPE) -> dict:
    """FR-1: the film's project locked, step by step; `LockFailed` names the first step that does not hold.

    1 the window (`PUT context/window` 200); 2 the PROBLEM calibration READY (answered at the boxes' yes); 3 the
    credits (`GET /v2/me` `creditsAvailable` >= `need`, else `top_up` once and read again; only read where `need`
    is 0 -- the free walk's lock is bought by a stand-in inside `press`); 4 the lock (`press`: the
    ready page's button, 200 or 201); 5 the questions READY (`GET overview` `questionsState`; FAILED retried once on
    `POST questionnaire/retry`)."""
    base = f"/v2/projects/{project_id}"
    record: dict = {"project_id": project_id, "scope": scope, "window": dict(window) if window else None}
    if window:
        status, body = call("PUT", f"{base}/context/window", {"recallWindow": dict(window)})
        record["window_status"] = status
        if status != 200:
            raise LockFailed("the window (PUT context/window)", {"status": status, "body": body})
    deadline = clock() + calibration_wait_s
    state, view = None, None
    while True:
        status, view = call("GET", f"{base}/calibration/{scope}", None)
        state = (view or {}).get("state") if isinstance(view, dict) else None
        if calibration_ready(view, scope) or state == "FAILED" or clock() >= deadline:
            break
        sleep(1)
    record["calibration"] = state
    if not calibration_ready(view, scope):
        raise LockFailed(f"the {scope} calibration (GET calibration/{scope})",
                         {"state": state, **({k: view.get(k) for k in ("total", "answered")}
                                             if isinstance(view, dict) else {})})
    status, me = call("GET", "/v2/me", None)
    credits = (me or {}).get("creditsAvailable") if isinstance(me, dict) else None
    record["credits_before"] = credits
    if need > 0 and (not isinstance(credits, (int, float)) or credits < need):
        if top_up is None:
            raise LockFailed("the credits (GET /v2/me)", {"creditsAvailable": credits, "need": need})
        record["topped_up"] = top_up()
        status, me = call("GET", "/v2/me", None)
        credits = (me or {}).get("creditsAvailable") if isinstance(me, dict) else None
        record["credits_topped"] = credits
        if not isinstance(credits, (int, float)) or credits < need:
            raise LockFailed("the credits (GET /v2/me, after the top-up)", {"creditsAvailable": credits, "need": need})
    status, body = press()
    record["lock_status"] = status
    if status not in (200, 201):
        raise LockFailed("the lock (the ready page's button, POST lock)", {"status": status, "body": body})
    deadline = clock() + questions_wait_s
    retried = False
    while True:
        status, overview = call("GET", f"{base}/overview", None)
        state = (overview or {}).get("questionsState") if isinstance(overview, dict) else None
        if state == "READY":
            break
        if state == "FAILED" and not retried:
            retried = True
            call("POST", f"{base}/questionnaire/retry", None)
        elif clock() >= deadline:
            break
        sleep(1)
    record["questions"] = state
    record["questions_retried"] = retried
    if state != "READY":
        raise LockFailed("the questions (GET overview questionsState)", {"questionsState": state})
    return record


# ------------------------------------------------------------------------------------------------ the walked record

def drawn_of(rows: list[dict] | None) -> list[dict]:
    """One link's walk (`link_walk`'s rows) as `backtest.json`'s `drawn` screens the respondent-reader is handed
    (`quality/readers.respondent_screens`): the screener, the gate, the experience, each item by its dimension, each
    why, the pilot ask -- in the order drawn. The film is the film reader's (`make read-films`) and is not a question
    screen here."""
    out = []
    for r in rows or []:
        if r.get("screen") != "question":
            continue
        base = {"kicker": r.get("where"), "question": r.get("question")}
        if r.get("follow_up"):
            out.append({"screen": "follow_up", **base, "note": None, "dimension": r["follow_up"].get("dimension")})
        elif r.get("key") == "screener":
            out.append({"screen": "screener", **base, "rows": r.get("options") or []})
        elif r.get("key") == "gate":
            out.append({"screen": "gate", **base, "options": r.get("options") or [], "chips": r.get("chips") or []})
        elif r.get("story") or r.get("step") == "story":
            out.append({"screen": "story", **base, "chips": r.get("chips") or []})
        elif r.get("key"):
            out.append({"screen": "item", "dimension": r["key"], **base, "rows": r.get("options") or [],
                        "chips": r.get("chips") or [], "control": r.get("control")})
        else:
            out.append({"screen": "pilot" if r.get("step") == "pilot" else (r.get("step") or "screen"), **base,
                        "rows": r.get("options") or [], "chips": r.get("chips") or []})
    return out


def response_shape(walked: dict | None) -> dict:
    """What the person's last response sent, by shape (no words): its status, `recency`, a story or a chip, how many
    answers, the whys by dimension, `outsideSegment`."""
    responses = (walked or {}).get("responses") or []
    last = responses[-1] if responses else {}
    body = last.get("sent") or {}
    return {"status": last.get("status"), "recency": body.get("recency"), "story": bool(body.get("story")),
            "anchorChip": body.get("anchorChip"), "answers": len(body.get("answers") or []),
            "followUps": [f.get("dimension") for f in body.get("followUps") or []],
            "outsideSegment": body.get("outsideSegment")}


def walk_summary(plan: dict, link: dict, walked: dict | None, *, error: str | None = None) -> dict:
    """One person's walk, kept in the bundle: who, the link, what they were to say, the steps drawn, the whys asked,
    the response's shape, whether the thanks was reached."""
    rows = (walked or {}).get("rows") or []
    films = [r for r in rows if r.get("screen") == "film"]
    return {"person": plan["person"], "invitation": link.get("invitationId"), "url": link.get("url"),
            "plan": {k: plan.get(k) for k in ("screener", "gate", "story_how", "chip", "frequency", "importance", "own")},
            "steps": [r.get("key") or (f"why:{r['follow_up'].get('dimension')}" if r.get("follow_up") else None)
                      or r.get("step") or r.get("where") for r in rows if r.get("screen") == "question"],
            "said": [(r.get("key") or r.get("step"), r.get("said")) for r in rows if r.get("screen") == "question"],
            "film": [{k: f.get(k) for k in ("kind", "first", "stuck")} for f in films],
            "whys": [r["follow_up"].get("dimension") for r in rows if r.get("follow_up")],
            "response": response_shape(walked), "done": bool((walked or {}).get("done")),
            **({"chip_remapped": remapped} if (remapped := chip_remapped(plan, rows)) else {}),
            **({"error": error} if error else {})}


def chip_remapped(plan: dict, rows: list[dict]) -> dict | None:
    """A recorded story chip the film link does not draw, re-expressed as the chip it does (spec 064 FR-7's rule: a
    finding, never a silent drop): `{recorded, tapped}`, or None where the person tapped no chip."""
    tapped = next((r.get("said") for r in rows if r.get("story") and str(r.get("said") or "").startswith("tap:")),
                  None)
    if not plan.get("chip") or not tapped:
        return None
    return {"recorded": plan["chip"], "tapped": tapped.removeprefix("tap:").strip()}


def watched(plans: list[dict]) -> str | None:
    """The one person a link whose screens the respondent-reader reads, as `backtest.watched_people` picks them: the
    first inside the segment who passed the gate with a story said and no chip, else the first."""
    for p in plans:
        if p["screener"] == "yes" and p["gate"] and p.get("story") and not p.get("chip"):
            return p["person"]
    return plans[0]["person"] if plans else None


def respondents_record(person: str | None, interview: dict | None, walked: dict | None,
                       shots: list[str] | None = None) -> dict:
    """`backtest.json`'s `respondents`: the watched person's link -- who, the interview as served
    (`backtest.served_items`), the screens drawn (`drawn_of`)."""
    if not person or not walked:
        return {}
    from evals import backtest                                                       # noqa: PLC0415
    served = backtest.served_items(interview or {})
    served["followUps"] = [{k: f.get(k) for k in ("dimension", "text", "spoken") if f.get(k)}
                           for f in (interview or {}).get("followUps") or [] if isinstance(f, dict)]
    drawn = drawn_of(walked.get("rows"))
    gate = (interview or {}).get("gate") or {}
    spoken = (gate.get("condition") or (interview or {}).get("condition") or {}).get("spoken")
    for d in drawn:
        if d["screen"] == "screener" and isinstance(spoken, dict):
            d["spoken"] = spoken                    # the screener's served spoken form, for R6
    return {LINK: {"person": person, "served": served, "drawn": drawn, "screens": list(shots or [])}}


def screens_bundle(*, entry: dict, project_id: str, door: str, stack: dict, people: int, lock: dict,
                   plans: list[dict], walks: list[dict], respondents: dict, after_screens: list[dict],
                   answers_leg: dict | None, brief: dict | None, themes_settled: dict | None,
                   founder_page: dict | None, run: str, typos: list | None = None, scope: str = SCOPE,
                   parent: str | None = None) -> dict:
    """FR-2: the one bundle `make read-screens` reads on the film's project (`backtest.json`, `kind: "film"`); spec 166
    FR-3: on the solution's project `kind: "film-solution"`, `scope` SOLUTION, the problem's project named (`parent`)."""
    solution = scope == SOLUTION_SCOPE
    return {"kind": SOLUTION_KIND if solution else "film", "spec": "166" if solution else "165", "run": run,
            "entry": {k: entry.get(k) for k in ("id", "title", "path", "sha256")},
            **({"problem_project_id": parent} if parent else {}),
            "scope": scope, "project_id": project_id, "door": door, "people": people,
            "stack": dict(stack), "founder": {"project": project_id},
            "lock": lock, "plans": plans, "walks": walks,
            "founder_screens": [],
            "founder_screens_note": "the founder's beats are the film's (163 FR-1: `make read-films`' founder-reader); "
                                    "no founder screen is read here",
            "respondents": respondents, "after_screens": after_screens, "answers_leg": answers_leg,
            "brief": brief, "themes_settled": themes_settled, "founder_page": founder_page,
            **({"typos": list(typos)} if typos else {})}


# ------------------------------------------------------------------------------------------------ the scripted runtime

def said_by_rung(walked: dict) -> dict[str, list[str]]:
    """Every why each walk answered, by rung (`{dimension: [text said, ...]}`), in the order walked -- what the
    founder's own runtime is handed to group (`THEMES`) on the free walk."""
    out: dict[str, list[str]] = {}
    for walk in (walked or {}).values():
        for r in (walk or {}).get("rows") or []:
            if r.get("follow_up") and isinstance(r.get("said"), str) and r["said"].strip():
                out.setdefault(str(r["follow_up"].get("dimension")), []).append(r["said"])
    return out


def _label(text: str) -> str:
    """A theme's label from its first answer's own words (keel-cloud 119 T11: a label shares words with its answers;
    T5: never the rung's name): its first five words, the punctuation dropped."""
    words = _bare(text).split()[:5]
    return " ".join(words).capitalize() if words else "What they said"


def themes_script(said: dict[str, list[str]]) -> list[dict]:
    """The scripted runtime's `THEMES` entries for the free walk (spec 012's shape, the texts resolved to the job's own
    answer ids by the runtime): one theme a rung holding every text said on it, labelled from its first. Machinery for
    the fakes, never a reading of the people."""
    out = []
    for dimension, texts in said.items():
        kept = list(dict.fromkeys(t for t in texts if t))
        if kept:
            out.append({"dimension": dimension, "outcome": "COMPLETED",
                        "result": {"themes": [{"label": _label(kept[0]), "answers": kept}]}})
    return out


def ways_script(stories: list[tuple[str, str]], founder_act: str | None) -> dict:
    """The scripted runtime's `EXPERIENCE_WAYS` answer for the free walk: every story told under the founder's way
    (the act the film shows, word for word), or on their own where the story names none."""
    from harness import three_surfaces as ts                                        # noqa: PLC0415
    ids = [i for i, text in stories if i and text]
    label = founder_act if founder_act else ts.ON_THEIR_OWN
    return {"outcome": "COMPLETED", "result": {"ways": [{"label": label, "answerIds": ids}] if ids else []}}


def stories_told(walks: list[dict], walked: dict) -> list[tuple[str, str]]:
    """`(invitationId, the story said)` for every person who told one on the film link."""
    out = []
    for w in walks:
        rows = ((walked or {}).get(w["person"]) or {}).get("rows") or []
        text = next((r.get("said") for r in rows if r.get("story") and isinstance(r.get("said"), str)
                     and not r["said"].startswith("tap:")), None)
        if text and w.get("invitation"):
            out.append((w["invitation"], text))
    return out


# ------------------------------------------------------------------------------------------------ the founder's words

def typed_beats(beats: list[tuple[int, str]], entry, *, seed: str) -> tuple[list[tuple[int, str]], list[dict]]:
    """`TYPOS=1` on the founder's words (spec 126's typist, as today): each beat the founder tells typed through
    `harness/typist.typos` (seeded `<entry>:beat-<n>`, the entry's names kept, its own words avoided); every typo
    recorded `{field, meant, typed, kind}`."""
    from harness import typist                                                       # noqa: PLC0415
    keep, avoid = typist.kept_words(entry), typist.avoided_words(entry)
    out, record = [], []
    for n, words in beats:
        typed, slips = typist.typos(words, f"{seed}:beat-{n}", keep=keep, avoid=avoid)
        out.append((n, typed))
        record += [{"field": f"beat-{n}", **(s._asdict() if hasattr(s, "_asdict") else dict(s))} for s in slips]
    return out, record


# ------------------------------------------------------------------------------------------------ on the stack

@dataclasses.dataclass
class FilmRun:
    """What `three_views_strangers`' walk helpers read off a run (`browser`, `recorder`, `cloud`, `web`, `page`,
    `get` / `call`, `findings`, `stamp`): the film leg's founder context, nothing of e2e-157's runtime."""
    stack: Any
    browser: Any
    recorder: Any
    context: Any
    page: Any
    stamp: str
    findings: list = dataclasses.field(default_factory=list)

    @property
    def cloud(self) -> str:
        return self.stack.cloud_base_url.rstrip("/")

    @property
    def web(self) -> str:
        return self.stack.web_base_url.rstrip("/")

    def call(self, method: str, path: str, body: dict | None = None) -> tuple[int, Any]:
        import json                                                                  # noqa: PLC0415
        kwargs: dict = {"timeout": 60_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = self.context.request.fetch(f"{self.cloud}{path}", method=method, **kwargs)
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001 - an empty body
            payload = response.text()
        return response.status, payload

    def get(self, path: str) -> Any:
        status, body = self.call("GET", path)
        return body if status < 400 else None


def press_on_the_ready_page(run: FilmRun, project_id: str) -> Callable[[], tuple[int, Any]]:
    """The ready page opened, a guide sheet over it passed by (keel-web 080 / 086: its Skip -- the sheet's scrim takes
    every click while it is up; walk 3 met it), and its one primary pressed (`three_views.press_lock`)."""
    def press() -> tuple[int, Any]:
        from evals import three_views as tv                                         # noqa: PLC0415
        from harness import story_screens as ss                                     # noqa: PLC0415
        from harness import vectors_screens as vs_screens                           # noqa: PLC0415
        run.page.goto(f"{run.web}/p/{project_id}/define/ready/interviewer", wait_until="load")
        try:
            vs_screens.pass_teaching_sheet(run.page, run.recorder, run.web, "opener")
        except Exception:  # noqa: BLE001 - absence is never a failure; the scrim is looked for below
            pass
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if ss._skip_sheet(run.page) is None and not run.page.locator(".gw-scrim").count():
                break
            # Trial of 2026-11-24 (09-karsa): the guide's scrim stayed up past the 6 s and took the lock's click -- its
            # own Skip / Close / Got it is pressed where drawn, else Escape, then the scrim is looked for again.
            pressed = False
            for name in ("Skip", "Skip the tour", "Close", "Got it", "Later", "Not now"):
                button = run.page.get_by_role("button", name=name)
                if button.count():
                    try:
                        button.first.click(timeout=2_000)
                        pressed = True
                        break
                    except Exception:  # noqa: BLE001 - the next name, then Escape
                        pass
            if not pressed:
                run.page.keyboard.press("Escape")
            run.page.wait_for_timeout(500)
        # Spec 166's local walk (keel-web 1ca065b3): a guide sheet can mount after the loop above found none, and its
        # scrim then takes the lock's click for the click's whole timeout -- the page is let stand clear of any sheet
        # for two seconds first (each one met passed by its Skip, or Escape), and a click a scrim took is tried again
        clear_for_s(run.page, 2.0)
        for attempt in range(3):
            try:
                return tv.press_lock(run)
            except Exception as taken:  # noqa: BLE001 - a scrim over the button: passed by, then pressed again
                if "intercepts pointer events" not in str(taken) or attempt == 2:
                    raise
                clear_for_s(run.page, 2.0)
        return tv.press_lock(run)
    return press


def clear_for_s(page, seconds: float, *, timeout_s: float = 45) -> bool:
    """The page held clear of any guide sheet for `seconds` running -- a sheet that mounts meanwhile passed by (its Skip,
    else Escape) and the count started again. True once clear; False at the time out."""
    from harness import story_screens as ss                                     # noqa: PLC0415
    deadline = time.monotonic() + timeout_s
    clear_since = time.monotonic()
    while time.monotonic() < deadline:
        up = False
        try:
            up = bool(page.locator(".gw-scrim").count())
        except Exception:  # noqa: BLE001 - a navigation in flight
            up = True
        if up:
            if ss._skip_sheet(page) is None:
                page.keyboard.press("Escape")
            clear_since = time.monotonic()
        elif time.monotonic() - clear_since >= seconds:
            return True
        page.wait_for_timeout(250)
    return False


def walk_people(run: FilmRun, project_id: str, plans: list[dict], *, out: dict) -> list[dict]:
    """FR-1: one TEXT link a person (`invitations/batch`, the orb), each walked on the film link with their plan; every
    walk kept (`out["walked"][person]`, `out["interviews"][person]`), a walk that stops recorded and the next walked."""
    from evals import three_views_strangers as tvs                                   # noqa: PLC0415
    own, tasks, _ = tvs.owner_row_and_tasks(run, project_id)
    links = tvs.make_links(run, project_id, [p["person"] for p in plans])
    out.update(own=own, tasks=tasks, links=links)
    summaries = []
    for i, (plan, link) in enumerate(zip(plans, links), 1):
        interview, walked, error = {}, None, None
        try:
            interview, _ = tvs.read_served(run, link["url"])
            how = walk_plan(plan, interview, own_label=own, other_tasks=tasks)
            walked = tvs.walk_link(run, link["url"], interview, shot=f"film-165-person-{i}", plan=how,
                                   story=plan["story_how"])
        except Exception as stopped:  # noqa: BLE001 - one person's stop is recorded; the others still walk
            error = f"{type(stopped).__name__}: {str(stopped)[:600]}"
        out.setdefault("walked", {})[plan["person"]] = walked
        out.setdefault("interviews", {})[plan["person"]] = interview
        summaries.append(walk_summary(plan, link, walked, error=error))
    return summaries


def settle(run: FilmRun, project_id: str, *, timeout_s: float = SETTLE_WAIT_S) -> dict:
    """The founder's page read once the answers have settled: no Insights line still GROUPING (keel-cloud 119) and the
    ways not GROUPING (keel-cloud 270), or the time out -- what it saw, recorded either way."""
    deadline = time.monotonic() + timeout_s
    waited = 0.0
    while True:
        overview = run.get(f"/v2/projects/{project_id}/overview") or {}
        standings = run.get(f"/v2/projects/{project_id}/standings") or {}
        grouping = [i.get("dimension") for i in standings.get("insights") or [] if i.get("state") == "GROUPING"]
        ways = (overview.get("ways") or {}).get("state")
        if (not grouping and ways != "GROUPING") or time.monotonic() > deadline:
            return {"grouping": grouping, "ways": ways, "waited_s": round(waited, 1), "standings": standings}
        time.sleep(2)
        waited += 2


def founder_page_after(run: FilmRun, project_id: str, run_dir: Path,
                       before_settle: Callable[[], Any] | None = None, *, scope: str = SCOPE,
                       picks: list[dict] | None = None) -> dict:
    """FR-2: the founder's page after the seven answers -- the back-test's answers leg (§B's screens: the stage page,
    every card opened, the Insights screen and its folds) and spec 164's reads of the page as drawn (the ways panel,
    Frequency's card, the Insights boxes, the brief's breakdown), each a check kept, never a stop."""
    import types                                                                     # noqa: PLC0415

    from evals import backtest                                                       # noqa: PLC0415
    from evals import three_views as tv                                              # noqa: PLC0415
    from evals import three_views_strangers as tvs                                   # noqa: PLC0415
    if before_settle is not None:
        before_settle()                       # the free walk: the founder's runtime handed the groupings first
    settled = settle(run, project_id)
    standings = settled.pop("standings")
    cam = backtest.Camera(run_dir=run_dir, page=run.page, watched={})
    j = types.SimpleNamespace(page=run.page, web_base=run.web, project_id=project_id, recorder=run.recorder)
    try:
        done = backtest.answers_leg(j, cam, stages=[scope])
    except Exception as missed:  # noqa: BLE001 - the leg is evidence; recorded
        done = {"errors": [{"at": "the answers leg", "error": repr(missed)[:300]}]}
    leg = tv.Leg("FR-2 the founder's page", "the founder's page after the seven answers (spec 165)")
    overview = run.get(f"/v2/projects/{project_id}/overview") or {}
    try:
        if scope == SOLUTION_SCOPE:
            solution_page_checks(run, leg, project_id, standings, picks or [])
        else:
            tvs.founder_page_on_screen(run, leg, project_id, overview, standings)
    except Exception as missed:  # noqa: BLE001 - recorded
        leg.notes.append(f"the page's reads stopped: {str(missed)[:300]}")
    return {"after_screens": backtest.after_screens(cam), "answers_leg": done,
            "brief": backtest.brief(standings), "themes_settled": settled,
            "founder_page": {"checks": [{"name": c.name, "ok": c.ok, "screen": c.screen} for c in leg.checks],
                             "notes": leg.notes, "ways": overview.get("ways")}}


def solution_page_checks(run, leg, project_id: str, standings: dict, picks: list[dict]) -> None:
    """Spec 166 FR-3 (spec 162 FR-8's reads, kept as checks): the solution's Overview cards as share bars counted from
    the people's picks, the So lines evidence only, the Insights cards as spec 119's, the brief's solution rows; on a
    keel-web with 260 the stage page's three cards as drawn."""
    from evals import three_views_strangers as tvs                                   # noqa: PLC0415
    from harness import solution_surfaces as sol                                    # noqa: PLC0415
    from harness import story_screens as ss                                         # noqa: PLC0415
    leg.check(run, "the three Overview cards are share bars (keel-cloud 272 FR-6), counted from the people's picks",
              not sol.share_faults(standings, picks), screen="the Overview", view="founder (wire)",
              detail={"faults": sol.share_faults(standings, picks)}, stop=False)
    leg.check(run, "the So lines are evidence only (no *should*, *next*, *try*)", not sol.so_line_faults(standings),
              screen="the Overview · the So lines", view="founder (wire)",
              detail={"faults": sol.so_line_faults(standings)}, stop=False)
    leg.check(run, "the Insights cards as spec 119's on the solution's three", not sol.insights_faults(standings),
              screen="Insights", view="founder (wire)", detail={"faults": sol.insights_faults(standings)}, stop=False)
    leg.check(run, "the brief's solution rows on `{yes, n, share, founderBand}`",
              not sol.brief_faults(standings.get("facts") or {}, picks), screen="the brief's facts",
              view="founder (wire)", detail={"faults": sol.brief_faults(standings.get("facts") or {}, picks)},
              stop=False)
    if ss.web_has_260(run.stack.keel_web):
        tvs.solution_page_on_screen(run, leg, project_id, standings)
