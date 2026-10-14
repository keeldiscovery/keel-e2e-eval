"""S-005, S-006 and S-007's whole body: the corpus journeys, as **vectors** journeys (spec 039; spec 041:
corpus revision 10, contract 13, keel-web 063's founder screens and 064's stranger's screens).

**The entry id is the only thing that differs between the three scenario modules** (spec 010
FR-015, kept): if `01-countly` needed one special case here, `05-paidly` would need two.

What the scenario does, in the founder's own order, one function per leg so a later spec can change
one leg and leave the others alone:

1. `leg_project`   -- the project on the entry's own market.
2. `leg_context`   -- the four context fields and the entry's own recall window (D13: at least two);
                      CONTEXT_INTERPRET; *Yes, that's it*.
3. `leg_interpret_problem` -- the problem seed and PROBLEM_INTERPRET's card.
4. `leg_calibrate` -- one stage at a time, one dimension a screen (keel-web 063): Prevalence, Frequency,
                      the cost and the price on one screen each; every list dimension's *Answer* (the
                      founder's words, which Keel drafts the list from), *Check and save* and, where it
                      picks, *Choose*; each screen's counter, dots and locked nav; the stored lists and the
                      review on the wire.
5. `leg_interpret_solution` -- the solution seed, SOLUTION_MECHANISM's card, and **the idea as the
                      solution's first question**: S2, the three lines checked, Save approving them.
6. `leg_persona`   -- who decides; on a B2B entry the decision-maker's respondent type.
7. `leg_lock`      -- step 5's two screens, *Lock and write the questions*; three RESPONDENT_QUESTIONS
                      jobs; READY; the lock stores every saved list and its picked index (D7).
8. `leg_invite`    -- one link per corpus person: the primary link, or on a B2B entry the
                      decision-maker's commercial link.
9. `leg_interview` -- each person in their own browser context, no founder session, through keel-web
                      064's screens: the decision-maker's idea screen first, the gate (its one chip), every
                      item as served (one escape, last), two picks on Importance, the fixed answers,
                      "nothing" typed as 0; the founder reads after each person.
10. `leg_standings` -- `GET standings` against the entry's `expected.standings` and `expected.vector_verdicts`
                      (codes mapped onto the wire's), and the same on the board (its pilot tile among them)
                      and the three stage pages, one row's per-person list among them.
11. `leg_brief`    -- the brief on the wire: the scripted headline and three answers, a card per dimension
                      equal to the eval's own reading of the entry (`instructions/brief_facts.py`, which
                      spec 040's DRY proved equal to keel-cloud's), what broke, the pilot -- and keel-web
                      065's two pages held to that wire: page one (the decision, headline, answers, every
                      card's words, the pilot tile), page two (one block a card, *What broke* on the broke
                      block alone) and the download's tab.

Every inference job is answered by keel-runtime's **scripted** executor from the entry's own stored
texts (`harness/vectors_script.py`); no model runs anywhere in this file (`evals/policy.py`).

It lives in `evals/` and not in `harness/` because it asserts. `harness/` is machinery.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from evals import corpus_facts
from evals.preludes import create_project, own_ai_door
from harness import vectors_script as vs
from harness import vectors_screens as vs_screens
from harness.browser import Auth, Connect, Landing, People
from harness.connect import start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from instructions import brief_facts as brief_facts_mod
from instructions import contract as contract_mod
from stack import remote
from stack import runtime as stack_runtime

VECTORS = vs.VECTORS

#: keel-web's own words for a status (`translate.ts` `standingStatus`), named once here so the
#: three scenarios cannot drift apart on what *not holding up* is spelled like.
STATUS_WORD = {
    "HOLDING_UP": "Holding up",
    "NOT_HOLDING_UP": "Not holding up",
    "PEOPLE_DISAGREE": "People disagree",
    "TOO_FEW_TO_CALL": "Too few to call",
    "NOT_ASKED_YET": "Not asked yet",
    "LEFT_OUT": "Left out",
    "NOT_TESTED": "Not tested",
}

#: keel-web `VECTOR_WORD`, the counter's first word (*Problem · 3 of 4*).
STAGE_WORD = {"PROBLEM": "Problem", "SOLUTION": "Solution", "COMMERCIAL": "Commercial"}
#: keel-web 063 FR-003: the idea counts as Solution's first question and who decides as Commercial's.
STAGE_OFFSET = {"PROBLEM": 0, "SOLUTION": 1, "COMMERCIAL": 1}
#: keel-web `KEEL_TEST_PENDING`: the *Keel will test* box on a Choose screen before the pick.
KEEL_TEST_PENDING = "Pick one and the test appears here."
#: Where Keel sets the bar (design D4), the Check screen shows the belief (keel-web 063 FR-005).
KEEL_SET = {"problem.importance", "problem.current_solution_satisfaction", "solution.relative_advantage",
            "commercial.commitment"}

#: The settled and the refused ends of an interaction (keel-cloud `InteractionStatus`).
TERMINAL_BAD = {"RESULT_INVALID", "DOMAIN_REFUSED", "STATE_CONFLICT", "JOB_FAILED", "APPLY_ERROR",
                "ABANDONED"}

#: The count keys `expected.standings` may carry and the wire's own place for each
#: (`DimensionStanding.interval` / `.choice`, `n` on the row).
INTERVAL_KEYS = ("inside", "below", "above")

#: The controls whose served options the item screen draws as rows (keel-web 064 FR-003).
ROW_CONTROLS = {"single_choice", "single_choice_5", "price_ladder", "fixed_four", "fixed_three", "pick_two"}


# ------------------------------------------------------------------------------------ the journey

@dataclass
class Journey:
    """What every leg reads and writes: the recorder, the founder's page and its wire, the entry and
    its typed inputs, and what earlier legs learned (the project id, each person's token)."""
    recorder: Recorder
    page: Any
    context: Any
    web_base: str
    cloud_base: str
    entry: Any
    founder: vs.FounderInputs
    people: list
    script: vs.GeneratedScript | None = None
    browser: Any = None
    #: keel-cloud's exported registry (the run's own `export/`), which the brief's cards are read over.
    registry: Any = None
    project_id: str = ""
    tokens: dict = field(default_factory=dict)       # person -> token
    links: dict = field(default_factory=dict)        # person -> the link the founder sends
    corridor: Any = None
    answers: Any = None
    interviews: dict = field(default_factory=dict)   # person -> the interview the wire served
    walked: dict = field(default_factory=dict)       # person -> what their screens drew
    screens: dict = field(default_factory=dict)      # what the answer pages drew, by page
    framing: dict = field(default_factory=dict)      # dimension -> what its founder screens drew
    #: True on the three scripted corpus journeys: every model answer is the corpus's, so every
    #: screen and every standing is held to the entry. False on S-012, where a host's model writes
    #: the corridor: the same legs run, the same screens are held to the same wire, and nothing is
    #: held to the corpus's own words or counts (spec 016 FR-007's rule, kept).
    strict: bool = True
    #: How many times longer a wait on a model may take: 1 on the scripted journeys, more on S-012.
    patience: float = 1.0
    standings: dict = field(default_factory=dict)    # the last GET standings

    # --------------------------------------------------------------------------- the wire

    def call(self, method: str, path: str, body: dict | None = None, *,
             ok: tuple = (200, 201, 202, 204)) -> tuple[int, Any]:
        url = f"{self.cloud_base}{path}"
        kwargs: dict = {"timeout": 20_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = self.context.request.fetch(url, method=method, **kwargs)
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001 - an empty 204 or a non-JSON error page
            payload = response.text()
        if response.status not in ok:
            raise AssertionError(f"{method} {path} answered {response.status}: {payload}")
        return response.status, payload

    def get(self, path: str) -> Any:
        return self.call("GET", path)[1]

    def project(self, suffix: str) -> str:
        return f"/v2/projects/{self.project_id}{suffix}"

    def revision(self) -> int:
        """The project's current revision, off the overview read every corridor write is held to."""
        return int((self.get(self.project("/overview")) or {}).get("revision") or 0)

    def wait_interaction(self, interaction_id: str, want: set, *, timeout_s: float = 90) -> dict:
        deadline = time.monotonic() + timeout_s
        last: dict = {}
        while time.monotonic() < deadline:
            last = self.get(f"/v2/inference-interactions/{interaction_id}") or {}
            status = last.get("status")
            if status in want:
                return last
            if status in TERMINAL_BAD:
                raise AssertionError(
                    f"interaction {interaction_id} ({last.get('screen')}) ended {status}: "
                    f"{last.get('diagnostic') or last.get('refusal')}")
            time.sleep(0.5)
        raise AssertionError(f"interaction {interaction_id} never reached {sorted(want)}: {last}")


def open_journey(recorder: Recorder, page, context, browser, stack, entry, founder, people, *,
                 script: vs.GeneratedScript | None = None, strict: bool = True,
                 patience: float = 1.0, registry=None) -> Journey:
    """One journey on one founder page: the legs below read and write it. S-005/6/7 open it strict
    on their scripted runtime; S-012 opens it with `strict=False` on a host's live model."""
    return Journey(recorder=recorder, page=page, context=context, web_base=stack.web_base_url,
                   cloud_base=stack.cloud_base_url, entry=entry, founder=founder, people=people,
                   script=script, browser=browser, strict=strict, patience=patience, registry=registry,
                   corridor=vs_screens.Corridor(page, recorder, stack.web_base_url, patience=patience),
                   answers=vs_screens.Answers(page, recorder, stack.web_base_url))


def _step(j: Journey, name: str, *, party: str = "stack", kind: str = "assert"):
    return j.recorder.step(name, party=party, kind=kind)


# ------------------------------------------------------------------------------- leg 1: context

def leg_project(j: Journey) -> None:
    """The project, on the landing's own name and market steps, on the entry's market."""
    founder = j.founder
    j.project_id = create_project(j.page, j.recorder, j.web_base, _market_inputs(founder))
    with _step(j, f"{j.entry.id}: the market is the one the entry names") as h:
        market = (j.get(j.project("/overview")) or {}).get("market") or {}
        h.record_assert({"country": founder.country, "region": founder.region,
                         "language": founder.language}, market)
        assert market.get("country") == founder.country, market
        assert (market.get("region") or None) == founder.region, market
        assert market.get("language") == founder.language, market


def leg_context(j: Journey) -> None:
    """The context step: the four fields and the entry's own recall window, one CONTEXT_INTERPRET
    job, and *Yes, that's it*. Asserted on the card and on the wire: the sentence Keel understood
    (the entry's own `context.understood` on a scripted journey), and the four fields and the window
    the founder typed -- a window of at least two units (D13)."""
    founder = j.founder
    drawn = j.corridor.context(j.project_id, founder.context_fields, founder.window.as_wire())
    with _step(j, "the card says what Keel understood, in the entry's own sentence, over the "
                  "entry's own window", party="founder") as h:
        want = j.entry.context["understood"] if j.strict else "a sentence"
        window_line = j.corridor.context_window_line()
        h.record_assert({"understands": want, "window": vs.window_words(founder.window)},
                        {"understands": drawn, "window": window_line})
        assert drawn.strip(), "the context card drew no sentence"
        if j.strict:
            assert drawn == want, drawn
        assert vs.window_words(founder.window) in window_line, window_line
    j.corridor.confirm_context()
    with _step(j, "the context is confirmed on the wire: the four fields, the sentence, the window "
                  "of at least two (D13)") as h:
        view = j.get(j.project("/context")) or {}
        fields = view.get("fields") or {}
        h.record_assert({**founder.context_fields, "recallWindow": founder.window.as_wire(),
                         "understands": drawn}, view)
        assert view.get("state") == "CONFIRMED", view
        assert view.get("understands") == drawn, (view.get("understands"), drawn)
        assert fields.get("recallWindow") == founder.window.as_wire(), fields
        assert int((fields.get("recallWindow") or {}).get("count") or 0) >= 2, fields
        for key, value in founder.context_fields.items():
            assert fields.get(key) == value, (key, fields)


def _market_inputs(founder: vs.FounderInputs):
    """`evals/preludes.create_project` reads a classic `FounderInputs`; this is the slice of one
    it touches -- the name and the market -- and nothing else."""
    from types import SimpleNamespace
    return SimpleNamespace(project_name=founder.project_name,
                           market=SimpleNamespace(country=founder.country, region=founder.region,
                                                  language=founder.language))


# ----------------------------------------------------------------------------- leg 2: interpret

def leg_interpret_problem(j: Journey) -> None:
    """The problem seed typed into the chat (the entry's own problem statement), PROBLEM_INTERPRET's
    card, and *Yes, that's the problem* -- which chains the PROBLEM calibration questions."""
    card = j.corridor.seed(j.project_id, "PROBLEM", j.founder.problem_seed)
    want = vs.problem_result(j.entry)
    with _step(j, "the problem card is the entry's own interpretation", party="founder") as h:
        h.record_assert(want["statement"] if j.strict else "a statement", card["claim"])
        assert card["claim"].strip(), card
        if j.strict:
            assert card["claim"] == want["statement"], card
    j.corridor.confirm_seed("PROBLEM")
    with _step(j, "the confirmed statement and the offer's name are the entry's, on the wire") as h:
        review = j.get(j.project("/review/PROBLEM")) or {}
        h.record_assert({"statement": card["claim"]}, {"statement": review.get("statement")})
        assert review.get("statement") == card["claim"], review.get("statement")


def leg_interpret_solution(j: Journey) -> None:
    """The solution seed, SOLUTION_MECHANISM's card and *Looks right* (which chains the SOLUTION
    calibration), and then **the idea as the solution's first question** (keel-web 063 S2): the three lines
    the mechanism drafted, read on the Check screen under *Solution · 1 of n*, saved untouched -- Save is the
    approval the lock and every invitation wait on."""
    card = j.corridor.seed(j.project_id, "SOLUTION", j.founder.solution_seed)
    m = j.entry.solution_mechanism
    with _step(j, "the mechanism card draws the entry's own actor, trigger, mechanism and output",
               party="founder") as h:
        want = [m["trigger"], m["mechanism"], m["output"]] if j.strict else []
        missing = [part for part in want if part not in card["text"]]
        h.record_assert(want, card)
        assert card["text"].strip(), card
        assert not missing, missing
    j.corridor.confirm_seed("SOLUTION")
    view = _wait_calibration(j, "SOLUTION")
    seen = j.corridor.idea_check()
    j.framing["idea"] = [seen]
    if seen["reloaded"]:
        # runs/DRIFT.md #78: S2 opened straight from the mechanism card draws the plan's cached idea -- three
        # empty lines from before the card -- and holds them, so Save stays off. The page is reloaded, the way
        # a founder who comes back to it has it.
        with _step(j, f"{j.entry.id}: DRIFT #78 -- S2 drew three empty lines from the stale plan; reloaded once",
                   party="founder", kind="protocol") as h:
            h.record_wire({"reloaded": True}, {"lines after the reload": seen["lines"]})
    with _step(j, "S2: the idea's three lines are the mechanism's, under Solution · 1 of n, and Save "
                  "approved them on the wire", party="founder") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_lines(j.entry)
        total = len(view.get("questions") or []) + STAGE_OFFSET["SOLUTION"]
        h.record_assert({**(want if j.strict else {}), "approved": True,
                         "progress": f"Solution · 1 of {total}"},
                        {"screen": seen, "wire": idea})
        assert all((idea.get(k) or "").strip() for k in ("what", "how", "belief")), idea
        assert {k: idea.get(k) for k in ("what", "how", "belief")} == seen["lines"], (idea, seen["lines"])
        assert idea.get("approved") is True, idea
        assert (idea.get("shortName") or "") in (idea.get("what") or ""), idea
        _hold_frame(seen["frame"], "SOLUTION", 1, total)
        if j.strict:
            assert {k: idea.get(k) for k in want} == want, idea
            assert idea.get("shortName") == m["short_name"], idea


# ----------------------------------------------------------------------------- leg 3: calibrate

def _hold_frame(frame: dict, vector: str, position: int, total: int) -> None:
    """keel-web 063 FR-003 / FR-009: *Stage · k of n*, n dots with the k-th the hollow one (a question's
    Answer, Check and Choose share it), and the side nav locked with no link in it."""
    assert frame["progress"] == f"{STAGE_WORD[vector]} · {position} of {total}", frame
    assert frame["dots"] == total and frame["now"] == position, frame
    assert frame["done"] == position - 1, frame
    assert frame["nav_locked"] and frame["nav_links"] == 0, frame


def _choose_label(j: Journey, question: dict, answer: vs.CalibrationAnswer) -> tuple[str, int]:
    """The one item Choose picks: the entry's own (its `pickedIndex`), read off the drafted list the
    screen shows -- on a live journey the model's list, its item at the entry's index or the last."""
    rows = (question.get("draft") or {}).get("items") or []
    listed = answer.listed or {}
    index = listed.get("pickedIndex") or 0
    if j.strict:
        return listed["items"][index]["label"], index
    held = min(index, max(0, len(rows) - 1))
    return (rows[held].get("label") if rows else listed["items"][index]["label"]), held


def leg_calibrate(j: Journey, vector: str) -> None:
    """One stage, on its screens, one dimension a screen (keel-web 063): CALIBRATION_QUESTIONS READY; each
    single question answered the way the entry answers it; each list dimension's Answer typed (the
    founder's words, `POST calibration/{vector}/draft`), its Check screen waited out while Keel drafts the
    list and saved untouched, and where it picks its Choose screen picking the entry's own item. Asserted
    on the screens -- every screen's *Stage · k of n*, dots and locked nav; each drafted list the entry's own
    words; the *Keel will test* box (none pre-picked on Choose) the entry's belief sentence; the stage's last
    primary naming the next stage -- and on the wire: the slice, every answer stored (a list's items with
    code's positional codes, its `asked` faces, its picked index, its phrase), the review complete with the
    entry's belief sentences and LEFT_OUT exactly where the founder was unsure."""
    view = _wait_calibration(j, vector)
    with _step(j, f"{vector.lower()}: the calibration offers exactly the registry's slice, in order",
               party="founder") as h:
        keys = [q.get("dimension") for q in view.get("questions") or []]
        want = vs.founder_keys(j.entry, vector)
        h.record_assert(want, keys)
        assert keys == want, keys
    j.corridor.wait_questions()
    answers = {a.dimension: a for a in j.founder.calibration[vector]}
    total = len(view.get("questions") or []) + STAGE_OFFSET[vector]
    questions = view.get("questions") or []
    conflicts = len(j.corridor.conflicts)
    for question in questions:
        key = question["dimension"]
        answer = answers[key]
        if not vs.is_list(key):
            j.framing[key] = [j.corridor.single(question, answer.as_wire())]
            continue
        if answer.unsure:
            j.framing[key] = [j.corridor.list_answer(question, None)]
            continue
        seen = [j.corridor.list_answer(question, answer.text)]
        drafted = _wait_calibration(j, vector)
        question = next((q for q in drafted.get("questions") or [] if q.get("dimension") == key), question)
        seen.append(j.corridor.list_check(question))
        if key in vs.PICKED:
            label, _ = _choose_label(j, question, answer)
            seen.append(j.corridor.list_choose(question, label))
        j.framing[key] = seen
    refused = j.corridor.conflicts[conflicts:]
    if refused:
        # runs/DRIFT.md #80: a Save or Continue posted at a revision the server had already moved past (the
        # list's redraft landing) is answered 409 CONCURRENCY and the screen says nothing; pressed again once the
        # page's poll held the new revision, as a founder would.
        with _step(j, f"{j.entry.id}: DRIFT #80 -- {len(refused)} {vector.lower()} write(s) refused 409 with "
                      "nothing on the screen; pressed again", party="founder", kind="protocol") as h:
            h.record_wire({"pressed again": len(refused)}, refused)

    with _step(j, f"{vector.lower()}: every screen reads {STAGE_WORD[vector]} · k of {total} with its dots, "
                  "the side nav locked, and the stage's last primary names the next stage",
               party="founder") as h:
        frames = {k: [s["frame"] for s in j.framing[k]] for k in keys}
        h.record_assert({"total": total, "exit": vs_screens.STAGE_EXIT[vector]}, frames)
        for position, key in enumerate(keys, start=1 + STAGE_OFFSET[vector]):
            for frame in frames[key]:
                _hold_frame(frame, vector, position, total)
        last = j.framing[keys[-1]][-1]
        if not answers[keys[-1]].unsure:
            assert last["primary"] == vs_screens.STAGE_EXIT[vector], last["primary"]

    with _step(j, f"{vector.lower()}: each drafted list is the entry's own on its Check screen, Choose "
                  "opens with nothing picked, and the Keel-will-test box reads the entry's belief",
               party="founder") as h:
        mismatches = []
        lower_case = []
        for key in keys:
            seen = j.framing[key]
            if not vs.is_list(key) or answers[key].unsure:
                continue
            check = next(s for s in seen if s["screen"] == "check")
            choose = next((s for s in seen if s["screen"] == "choose"), None)
            if choose is not None:
                if choose["picked_before"] or choose["test_before"]["belief"] != KEEL_TEST_PENDING:
                    mismatches.append({"dimension": key, "choose": "something was pre-picked", "seen": choose})
            if not j.strict:
                continue
            drawn = _drawn_list(key, check)
            want = _corpus_list(j.entry, key)
            if drawn != want:
                mismatches.append({"dimension": key, "screen": drawn, "corpus": want})
            sentence = (j.entry.founder_calibration.get(key) or {}).get("belief_sentence")
            box = (choose or check)["test"] if (choose or key in KEEL_SET) else None
            if box is None or box["belief"] == sentence:
                continue
            if key == "commercial.buyer_payer_alignment" and _capital(box["belief"]) == sentence:
                lower_case.append({"dimension": key, "keel will test": box["belief"], "server": sentence})
                continue
            mismatches.append({"dimension": key, "keel will test": box["belief"], "corpus": sentence})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)
    if lower_case:
        # runs/DRIFT.md #79: keel-web's preview of Buyer and payer's belief lower-cases the decider at the head
        # of the sentence ("the restaurant manager decides, ..."); the server's sentence -- the corpus's -- opens
        # with a capital. Held equal but for that one letter.
        with _step(j, f"{j.entry.id}: DRIFT #79 -- the Choose screen's Buyer-and-payer belief opens lower-case; "
                      "held to the server's sentence but for its first letter", party="founder",
                   kind="protocol") as h:
            h.record_wire({"server": [r["server"] for r in lower_case]},
                          {"screen": [r["keel will test"] for r in lower_case]})

    if vector == "COMMERCIAL" and j.founder.hourly_rate is not None:
        _hourly_rate(j)
    stored = _wait_calibration(j, vector)
    with _step(j, f"{vector.lower()}: every list is stored as the founder saved it -- code's positional codes, "
                  "the stranger's faces, the picked index, the phrase", party="stack") as h:
        mismatches = []
        for q in stored.get("questions") or []:
            key = q.get("dimension")
            if not vs.is_list(key) or answers[key].unsure:
                continue
            got = (q.get("answer") or {}).get("list") or {}
            items = [{k: i.get(k) for k in ("code", "label", "asked") if i.get(k) is not None}
                     for i in got.get("items") or []]
            have = {"items": items, "pickedIndex": got.get("pickedIndex"), "phrase": got.get("phrase")}
            if j.strict:
                want = vs.saved_list(j.entry, key)
                if have != want:
                    mismatches.append({"dimension": key, "wire": have, "corpus": want})
            elif [i.get("code") for i in items] != [vs.wire_code(key, n) for n in range(len(items))]:
                mismatches.append({"dimension": key, "wire": have, "want": "code's positional codes"})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)

    review = j.get(j.project(f"/review/{vector}")) or {}
    with _step(j, f"{vector.lower()}: the review is complete and reads the entry's belief sentences, "
                  "LEFT_OUT where the founder was unsure", party="stack") as h:
        rows = {r.get("dimension"): r for r in review.get("rows") or []}
        mismatches = []
        for key in vs.founder_keys(j.entry, vector) + (
                ["commercial.ability_to_pay"] if vector == "COMMERCIAL" else []):
            founder = j.entry.founder_calibration.get(key) or {}
            row = rows.get(key) or {}
            if founder.get("unsure") or (key == "problem.frequency" and not vs.frequency_fits(j.entry)):
                if not (row.get("leftOut") or row.get("unsure")):
                    mismatches.append({"dimension": key, "want": "left out", "row": row})
                continue
            if j.strict and row.get("belief") != founder.get("belief_sentence"):
                mismatches.append({"dimension": key, "wire": row.get("belief"),
                                   "corpus": founder.get("belief_sentence")})
        h.record_assert({"complete": True, "mismatches": []},
                        {"complete": review.get("complete"), "mismatches": mismatches,
                         "rows": review.get("rows")})
        assert review.get("complete") is True, review
        assert not mismatches, json.dumps(mismatches, indent=2)


def _capital(text: str) -> str:
    return text[:1].upper() + text[1:]


def _drawn_list(key: str, check: dict) -> dict:
    """What a Check screen drew, in the corpus's shape: the editable labels in order, Importance's locked
    own item first, Current solution's phrase, Commitment's step."""
    rows = check["rows"]
    labels = [r["text"] for r in rows if not r["locked"]]
    if key == "problem.importance":
        own = [r["text"] for r in rows if r["locked"] and r["tag"] == "yours"]
        labels = own + labels
    if key == "commercial.commitment":
        labels = [check["field"]] if check["field"] is not None else labels
    out = {"items": labels}
    if key == "problem.current_solution_satisfaction":
        out["phrase"] = check["field"]
    return out


def _corpus_list(entry, key: str) -> dict:
    """The entry's own list as a Check screen draws it: Buyer and payer's "Nobody else" is code's and
    drawn nowhere on Check (it is Choose's first radio)."""
    saved = vs.founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != vs.NOBODY_ELSE[0]]
    out = {"items": labels}
    if key == "problem.current_solution_satisfaction":
        out["phrase"] = saved.get("phrase")
    return out


def _hourly_rate(j: Journey) -> None:
    """A B2B entry records the hourly rate its brief prices hours at. keel-web draws the rate only
    under an HOURS cost estimate, and every corpus estimate is an AMOUNT, so where keel-cloud's
    market default is not the entry's the rate is set on the wire -- and the step says which it was."""
    view = j.get(j.project("/calibration/COMMERCIAL")) or {}
    rate = (view.get("hourlyRate") or {}).get("amount")
    with _step(j, "the hourly rate is the entry's own", party="stack", kind="protocol") as h:
        if rate is not None and float(rate) == float(j.founder.hourly_rate):
            h.record_wire({"hourlyRate": j.founder.hourly_rate}, {"default": rate, "set": False})
            return
        body = {"expectedRevision": view.get("revision"), "hourlyRate": j.founder.hourly_rate}
        _, saved = j.call("PUT", j.project("/calibration/COMMERCIAL"), body)
        # The write moved the project's revision under the page the founder is on (step 5), which would post
        # its lock at the revision it read: the page is reloaded, the way a founder coming back has it.
        j.page.reload(wait_until="load")
        h.record_wire(body, {"default": rate, "set": True, "saved": saved, "reloaded": j.page.url})


def _wait_calibration(j: Journey, vector: str, *, timeout_s: float = 90) -> dict:
    deadline = time.monotonic() + timeout_s * j.patience
    view: dict = {}
    while time.monotonic() < deadline:
        view = j.get(j.project(f"/calibration/{vector}")) or {}
        if view.get("state") == "READY":
            return view
        if view.get("state") == "FAILED":
            why = j.get(f"/v2/inference-interactions/{view.get('interactionId')}") or {}
            raise AssertionError(f"{vector}'s calibration questions FAILED: "
                                 f"{why.get('status')}: {why.get('diagnostic') or why.get('refusal')}")
        time.sleep(0.5)
    raise AssertionError(f"{vector}'s calibration questions never became READY: {view}")


def leg_persona(j: Journey) -> None:
    """Who decides to pay, on the persona step: the same person on a B2C entry, the entry's
    decision-maker role on a B2B one -- which is what gives a B2B study its second respondent type
    and its commercial link."""
    j.corridor.persona(j.founder.decider)
    with _step(j, "the persona yields one respondent type, or two on a B2B entry") as h:
        view = j.get(j.project("/persona")) or {}
        types = view.get("respondentTypes") or []
        want = 2 if vs.is_b2b(j.entry) else 1
        h.record_assert(want, types)
        assert len(types) == want, types
        if vs.is_b2b(j.entry):
            assert sum(1 for t in types if t.get("commercialLink")) == 1, types
            assert (view.get("decider") or {}).get("role") == j.founder.decider["role"], view


# ---------------------------------------------------------------------------------- leg 4: lock

def leg_lock(j: Journey) -> None:
    """Step 5's two screens (*A word from you* 1 of 2, *The pilot* 2 of 2; the idea moved to S2), then
    *Lock and write the questions*: three RESPONDENT_QUESTIONS jobs (part 3 the decision-maker's link's on a
    B2B entry), READY before anyone is invited, and the lock storing every saved list with its picked
    index (design §6, D7)."""
    drawn = j.corridor.word_pilot_and_lock()
    with _step(j, "step 5 is two screens, 1 of 2 and 2 of 2", party="founder") as h:
        h.record_assert(["1 of 2", "2 of 2"], drawn["counters"])
        assert drawn["counters"] == ["1 of 2", "2 of 2"], drawn
    deadline = time.monotonic() + 120 * j.patience
    state = None
    seen_failed = False
    while time.monotonic() < deadline:
        state = (j.get(j.project("/overview")) or {}).get("questionsState")
        if state == "FAILED" and not seen_failed:
            # runs/DRIFT.md #81: the state is read off the project and then off the open interactions, two reads
            # apart; a part applied between them reads FAILED for that one read. Read again before believing it.
            seen_failed = True
            time.sleep(2)
            continue
        if state in ("READY", "FAILED"):
            break
        time.sleep(0.5)
    if seen_failed and state == "READY":
        with _step(j, f"{j.entry.id}: DRIFT #81 -- the overview read the questions FAILED while the parts were "
                      "landing; READY on the next read", party="stack", kind="protocol") as h:
            h.record_wire({"questionsState": "FAILED"}, {"questionsState": state})
    with _step(j, "the study is version 1, the three parts' questions are written, READY, and the lock "
                  "holds every saved list and its picked index (D7)") as h:
        plan = j.get(j.project("/plan")) or {}
        lists = plan.get("lists") or {}
        want = {key: vs.saved_list(j.entry, key) for v in VECTORS for key in vs.founder_keys(j.entry, v)
                if vs.is_list(key) and not j.entry.unsure(key)}
        have = {key: {"items": [{k: i.get(k) for k in ("code", "label", "asked") if i.get(k) is not None}
                                for i in (lists.get(key) or {}).get("items") or []],
                      "pickedIndex": (lists.get(key) or {}).get("pickedIndex"),
                      "phrase": (lists.get(key) or {}).get("phrase")} for key in want}
        h.record_assert({"locked": True, "version": 1, "questionsState": "READY",
                         "lists": want if j.strict else sorted(want)},
                        {"locked": plan.get("locked"), "version": plan.get("version"),
                         "questionsState": state, "lists": lists})
        assert plan.get("locked") is True and plan.get("version") == 1, plan
        assert state == "READY", (state, plan.get("questions"))
        assert set(want) <= set(lists), (sorted(want), sorted(lists))
        if j.strict:
            assert have == want, json.dumps({"lock": have, "corpus": want}, indent=2)


# -------------------------------------------------------------------------------- leg 5: invite

def leg_invite(j: Journey) -> None:
    """One link per corpus person, in corpus order, through the People page's popups: the
    specialist's *Send the questions*, or on a B2B entry the decision-maker's commercial link for
    every person on `COMMERCIAL_B2B`."""
    persona = j.get(j.project("/persona")) or {}
    primary = next(t for t in persona.get("respondentTypes") or [] if not t.get("commercialLink"))
    decider = next((t for t in persona.get("respondentTypes") or [] if t.get("commercialLink")), None)
    links = vs_screens.PeopleLinks(j.page, j.recorder, j.web_base, patience=j.patience)
    for person in j.people:
        if person.link == vs.LINK_B2B:
            url = links.commercial_link(j.project_id, decider["label"], person.person)
        else:
            url = links.specialist_link(j.project_id, primary["label"], person.person,
                                        f"{primary.get('label')}, asked about one real time.")
        j.links[person.person] = url
        j.tokens[person.person] = url.rstrip("/").rsplit("/", 1)[-1]
    with _step(j, "every corpus person has a link of their own, and the wire has one invitation "
                  "per link", party="founder") as h:
        people = j.get(j.project("/people")) or {}
        h.record_assert(len(j.people), {"links": len(set(j.tokens.values())), "people": people})
        assert len(set(j.tokens.values())) == len(j.people), j.tokens


# ----------------------------------------------------------------------------- leg 6: interview

def leg_interview(j: Journey) -> None:
    """Each person on their own link, in their own browser context with no founder session, through
    keel-web 064's screens: the decision-maker's idea screen first, the gate and its one chip, every item
    as served -- its kicker, its stem, its options, its ONE escape drawn last (none on Commitment) --
    Importance's two picks, the fixed answers, "nothing" typed as 0. The screens are held to the wire on
    every journey; the body the page POSTs is held to the corpus person's own answers, by item and by
    option id. The founder has their AI read after each person, so the scripted readings land on the
    corpus's own people in order."""
    for person in j.people:
        _answer_one(j, person, j.tokens[person.person])
        _read(j, person)


def _answer_one(j: Journey, person, token: str) -> None:
    stranger = j.browser.new_context()
    try:
        interview = stranger.request.get(f"{j.cloud_base}/v2/i/{token}/interview",
                                         timeout=20_000).json()
        j.interviews[person.person] = interview
        items = {i.get("dimension"): i for part in interview.get("parts") or []
                 for i in part.get("items") or []}
        kind = "COMMERCIAL_LINK" if person.link == vs.LINK_B2B else "FULL"
        with _step(j, f"{person.person}: the {kind} interview carries every item this person "
                      "answers, and every option they pick", party="participant") as h:
            missing = [p.dimension for p in person.picks if p.dimension not in items]
            unoffered = []
            for pick in person.picks:
                item = items.get(pick.dimension) or {}
                offered = {o.get("optionId") for o in item.get("options") or []}
                offered |= {a.get("id") for a in item.get("advantages") or []}
                unoffered += [(pick.dimension, code) for code in pick.codes + pick.advantages
                              if vs.option_id(token, pick.dimension, code) not in offered]
                escape = (item.get("escape") or {}).get("code")
                if pick.chip and pick.chip != escape:
                    unoffered.append((pick.dimension, pick.chip))
            h.record_assert({"kind": kind, "missing": [], "unoffered": []},
                            {"kind": interview.get("kind"), "missing": missing,
                             "unoffered": unoffered, "items": sorted(items)})
            assert interview.get("kind") == kind, interview.get("kind")
            assert not missing, missing
            if j.strict:
                assert not unoffered, unoffered
        recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
        expected = person.response(token, recall)
        if unoffered:
            expected = _on_the_offered_options(expected, items)
        by_item = {a["itemId"]: a for a in expected.get("answers") or []}
        page = stranger.new_page()
        screens = vs_screens.Interview(page, j.recorder)
        screens.open(j.links[person.person])
        walked = screens.walk(person, interview, by_item)
        j.walked[person.person] = walked
        _hold_the_screens(j, person, interview, walked)
        with _step(j, f"{person.person}: the page sent exactly this person's answers",
                   party="participant") as h:
            sent = walked["body"] or {}
            h.record_assert(expected, sent)
            assert _normal_body(sent) == _normal_body(expected), (sent, expected)
            h.capture_text("participant_page", "\n\n".join(walked["seen"]))
        if person.pilot_opt_in:
            screens.opt_in_to_pilot(interview)
    finally:
        stranger.close()


def _hold_the_screens(j: Journey, person, interview: dict, walked: dict) -> None:
    """keel-web 064, held to the wire on every journey: the decision-maker's link opens with the idea's
    three lines under the served kicker (D9); the gate's story chip is *I can't recall one particular
    {occasion}* alone; every item draws its served kicker and stem, its served options as rows, *Pick two.*
    on Importance, and its ONE escape -- the served label, after the control and before the buttons, none
    on Commitment."""
    with _step(j, f"{person.person}: every screen draws what the wire served -- the kicker, the stem, the "
                  "options, one escape last", party="participant") as h:
        faults = []
        screens = walked["screens"]
        idea = interview.get("idea")
        if interview.get("kind") == "COMMERCIAL_LINK" and idea:
            first = screens[0] if screens else {}
            if first.get("screen") != "idea" or first.get("kicker") != idea.get("kicker") \
                    or (idea.get("what") or "") not in (first.get("card") or ""):
                faults.append({"idea screen": first, "served": idea})
        gate = next((s for s in screens if s.get("screen") == "gate"), None)
        if gate is not None and person.recency:
            want = [vs_screens.gate_chip_word(interview.get("occasion"))]
            if gate["chips"] != want:
                faults.append({"gate chips": gate["chips"], "want": want})
        by_dimension = {i.get("dimension"): i for p in interview.get("parts") or [] for i in p.get("items") or []}
        for drawn in (s for s in screens if s.get("screen") == "item"):
            item = by_dimension.get(drawn["dimension"]) or {}
            escape = item.get("escape")
            want = {"kicker": item.get("kicker"), "chips": [escape["label"]] if escape else []}
            if item.get("control") in ROW_CONTROLS:
                want["rows"] = [o.get("label") for o in item.get("options") or []]
            if item.get("control") == "pick_two":
                want["hint"] = vs_screens.IV_PICK_TWO
            if not item.get("priceAnchor"):
                want["question"] = item.get("question")
            have = {k: drawn.get(k) for k in want}
            if have != want:
                faults.append({"dimension": drawn["dimension"], "screen": have, "wire": want})
            order = drawn.get("order") or []
            control = next((n for n, c in enumerate(order) if "iv-control" in str(c)), None)
            chips = next((n for n, c in enumerate(order) if "iv-chips" in str(c)), None)
            buttons = next((n for n, c in enumerate(order) if "iv-actions" in str(c)), None)
            if escape and not (control is not None and chips is not None and buttons is not None
                               and control < chips < buttons):
                faults.append({"dimension": drawn["dimension"], "escape not last": order})
            if drawn["dimension"] == "commercial.commitment" and escape is not None:
                faults.append({"dimension": drawn["dimension"], "escape": escape, "want": None})
        h.record_assert([], faults)
        assert not faults, json.dumps(faults, indent=2)


def _on_the_offered_options(body: dict, items: dict) -> dict:
    """A live journey's answer on the options the model's lists made: an option id the item does not
    offer (a benefit the model's list has no place for) becomes the item's first options, as many as the
    person picked. Never reached on a scripted journey."""
    by_id = {i.get("itemId"): i for i in items.values()}
    answers = []
    for answer in body.get("answers") or []:
        item = by_id.get(answer.get("itemId")) or {}
        offered = [o.get("optionId") for o in item.get("options") or []]
        picked = answer.get("optionIds")
        if picked and not all(p in offered for p in picked):
            answer = {**answer, "optionIds": offered[:len(picked)]}
        advantages = [a.get("id") for a in item.get("advantages") or []]
        ticked = answer.get("advantageIds")
        if ticked and not all(a in advantages for a in ticked):
            answer = {**answer, "advantageIds": advantages[:len(ticked)]}
        answers.append(answer)
    return {**body, "answers": answers}


def _normal_body(body: dict) -> dict:
    """A response body with its order taken out -- answers by item, ids as sets -- and keel-web's
    one deprecated constant (`pilotOptIn: false`) dropped, so two bodies compare on what they say."""
    out = {k: v for k, v in body.items() if k not in ("answers", "pilotOptIn")}
    answers = {}
    for answer in body.get("answers") or []:
        a = dict(answer)
        for key in ("optionIds", "advantageIds"):
            if key in a:
                a[key] = sorted(a[key])
        if "costTotal" in a and a["costTotal"].get("value") is not None:
            a["costTotal"] = {**a["costTotal"], "value": round(float(a["costTotal"]["value"]), 4)}
        answers[a.pop("itemId")] = a
    out["answers"] = answers
    return out


def _read(j: Journey, person) -> None:
    """The founder has their AI read the new answer, on the People page, when this person wrote a
    story the reader is shown; nobody else's answer queues a reading (a gate no, a chip, the
    decision-maker's link)."""
    readable = any(p.person == person.person for p in vs.readable_people(j.entry))
    if not readable:
        return
    people = People(j.page, j.recorder, j.web_base)
    deadline = time.monotonic() + 45 * j.patience
    while True:
        people.open(j.project_id)
        state = people.read_action_state()
        if state.get("enabled"):
            break
        if time.monotonic() > deadline:
            raise AssertionError(f"{person.person}'s answer never reached the read action: {state}")
        j.page.wait_for_timeout(1_000)
    people.read_all_and_wait(timeout_s=90 * j.patience)
    with _step(j, f"{person.person}'s answer is read, and nothing failed") as h:
        batches = j.get(j.project("/readings")) or []
        batch = batches[0] if isinstance(batches, list) and batches else {}
        h.record_assert({"status": "DONE", "failed": []}, batch)
        assert batch.get("status") == "DONE", batch
        assert not batch.get("failed"), batch


# ----------------------------------------------------------------------------- leg 7: standings

def expected_status(entry, key: str) -> str:
    """The entry's own status for `key`, but `LEFT_OUT` where this journey had to leave Frequency
    out (spec 039 / 041 D-1: the corpus's Frequency is on an "out of N" its own window cannot carry)."""
    if key == "problem.frequency" and not vs.frequency_fits(entry):
        return "LEFT_OUT"
    return str(((entry.expected.get("standings") or {}).get(key) or {}).get("status") or "").upper()


def _option_counts(raw: str) -> dict[str, int]:
    out = {}
    for part in str(raw).split(","):
        code, _, count = part.strip().partition("=")
        if code:
            out[code.strip()] = int(count)
    return out


def leg_standings(j: Journey) -> None:
    """`GET standings` against the entry, dimension by dimension -- status, drift, n and every count
    the entry records, each `optionCounts` code on the wire's own code -- and every vector's verdict and
    deciding dimension; then the board and the three stage pages, one row's per-person list among them."""
    j.standings = j.get(j.project("/standings")) or {}
    dims = {d.get("dimension"): d for v in j.standings.get("vectors") or []
            for d in v.get("dimensions") or []}
    expected = j.entry.expected.get("standings") or {}
    if not j.strict:
        with _step(j, "every vector stands, with a status from keel-cloud's own words on every "
                      "dimension (a live journey: nothing is held to the corpus)") as h:
            statuses = {k: d.get("status") for k, d in dims.items()}
            verdicts = {v.get("vector"): v.get("verdict") for v in j.standings.get("vectors") or []}
            h.record_assert({"vectors": list(VECTORS), "statuses": sorted(STATUS_WORD)},
                            {"verdicts": verdicts, "statuses": statuses})
            assert set(verdicts) == set(VECTORS), verdicts
            assert all(s in STATUS_WORD for s in list(statuses.values()) + list(verdicts.values())), (
                statuses, verdicts)
        _board(j)
        for vector in VECTORS:
            _vector_page(j, vector)
        return
    with _step(j, "every dimension stands where the entry says it does: status, drift and counts") as h:
        mismatches = []
        for key, want in expected.items():
            got = dims.get(key) or {}
            row: dict = {"dimension": key}
            status = expected_status(j.entry, key)
            if (got.get("status") or "") != status:
                row["status"] = {"wire": got.get("status"), "corpus": status}
            overridden = status != str(want.get("status") or "").upper()
            want_drift = "NONE" if overridden else str(want.get("drift") or "none").upper()
            if (got.get("drift") or "NONE") != want_drift:
                row["drift"] = {"wire": got.get("drift"), "corpus": want_drift}
            if not overridden and status != "LEFT_OUT":
                if "n" in want and int(got.get("n") or 0) != int(want["n"]):
                    row["n"] = {"wire": got.get("n"), "corpus": want["n"]}
                interval = got.get("interval") or {}
                for count in INTERVAL_KEYS:
                    if count in want and interval and int(interval.get(count) or 0) != int(want[count]):
                        row[count] = {"wire": interval.get(count), "corpus": want[count]}
                if "optionCounts" in want:
                    wire_counts = {o.get("code"): int(o.get("count") or 0)
                                   for o in (got.get("choice") or {}).get("optionCounts") or []}
                    for code, count in _option_counts(want["optionCounts"]).items():
                        wire_code = vs.on_the_wire(j.entry, key, code)
                        if wire_counts.get(wire_code, 0) != count:
                            row.setdefault("optionCounts", {})[code] = {
                                "wire": wire_counts.get(wire_code), "wire code": wire_code, "corpus": count}
            if len(row) > 1:
                mismatches.append(row)
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)

    with _step(j, "every vector's verdict is the worst of its dimensions, the deciding one's, as the "
                  "entry says (D3: all thirteen decide)") as h:
        verdicts = {v.get("vector"): v for v in j.standings.get("vectors") or []}
        mismatches = []
        for vector, want in (j.entry.expected.get("vector_verdicts") or {}).items():
            got = verdicts.get(vector) or {}
            deciding = (dims.get(want.get("deciding")) or {}).get("status")
            if got.get("verdict") != want.get("verdict") or deciding != want.get("verdict"):
                mismatches.append({"vector": vector, "wire": got.get("verdict"),
                                   "deciding on the wire": deciding, "corpus": want})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)

    _board(j)
    for vector in VECTORS:
        _vector_page(j, vector)


def _board(j: Journey) -> None:
    """The board, as the founder opens it: one panel per vector, worst first, each pill the
    vector's verdict in keel-web's word; the headline the worst vector's own; the belief count the
    entry's calibrated set; the download live, since answers have been read."""
    board = j.screens["board"] = j.answers.board(j.project_id)
    verdicts = {v.get("vector"): v for v in j.standings.get("vectors") or []}
    with _step(j, "the board: three panels, each the wire's vector verdict in keel-web's word, and "
                  "the download live",
               party="founder") as h:
        want = {v: STATUS_WORD[verdicts[v]["verdict"]] for v in VECTORS}
        got = {p["stage"]: p["pill"] for p in board["panels"]}
        # The tile counts beliefs: every dimension the founder did not leave out.
        beliefs = sum(1 for v in j.standings.get("vectors") or [] for d in v.get("dimensions") or []
                      if d.get("status") != "LEFT_OUT")
        h.record_assert({"pills": want, "bands": 3, "download": True, "beliefs": str(beliefs)},
                        {"pills": got, "bands": len(board["bands"]), "download": board["download"],
                         "tiles": board["tiles"], "overall": board["overall"]})
        assert set(got) == set(VECTORS), got
        for vector, word in want.items():
            assert word in got[vector], (vector, got[vector], word)
        assert len(board["bands"]) == 3, board["bands"]
        assert board["download"], "the download is not live after every answer was read"
        assert board["tiles"] and board["tiles"][0] == str(beliefs), (board["tiles"], beliefs)
        headlines = [v.get("headline") for v in verdicts.values()]
        assert board["overall"] in headlines, (board["overall"], headlines)
    with _step(j, "the board's third tile: pilot sign-ups, k of n · p% over the per-link line, the wire's own "
                  "(keel-web 065, design §7.5)", party="founder") as h:
        big, line = pilot_words(j.standings.get("pilot") or {})
        want = {"present": True, "big": big, "label": "pilot sign-ups", "line": line}
        h.record_assert(want, board["pilot"])
        assert board["pilot"] == want, (board["pilot"], want)


def _vector_page(j: Journey, vector: str) -> None:
    """One stage page: a row per dimension, each status the wire's in keel-web's word (amber where
    left out), the vector's headline the wire's own, on a B2B commercial page the banner naming the
    decision-maker -- and the deciding row opened, its per-person list the wire's people, each read as the
    wire reads them (design §7.1: the people list shows `readAs`)."""
    standing = next(v for v in j.standings.get("vectors") or [] if v.get("vector") == vector)
    rows = standing.get("dimensions") or []
    deciding = (standing.get("deciding") or {}).get("dimension") if isinstance(standing.get("deciding"), dict) \
        else standing.get("deciding")
    if deciding not in {d.get("dimension") for d in rows}:
        deciding = vs.stage_cite(j.entry, vector) if j.strict else None
    opened = next((d for d in rows if d.get("dimension") == deciding and d.get("people")), None) or \
        next((d for d in rows if d.get("people")), None)
    page = j.screens[vector] = j.answers.vector_page(j.project_id, vector,
                                                     open_row=(opened or {}).get("dimension"))
    with _step(j, f"the {vector.lower()} page: every dimension reads the wire's status in keel-web's "
                  "word, and one row's people are the wire's, each as it was read",
               party="founder") as h:
        mismatches = []
        for d in rows:
            key = d.get("dimension")
            row = page["rows"].get(key) or {}
            word = STATUS_WORD[d.get("status")]
            if not row.get("status", "").startswith(word):
                mismatches.append({"dimension": key, "screen": row.get("status"), "want": word})
            if d.get("status") == "LEFT_OUT" and not row.get("amber"):
                mismatches.append({"dimension": key, "screen": "not amber", "want": "amber"})
        people = [{"name": p.get("personName"), "readAs": p.get("readAs")} for p in (opened or {}).get("people") or []]
        h.record_assert({"headline": standing.get("headline"), "mismatches": [], "people": people},
                        {"headline": page["headline"], "mismatches": mismatches,
                         "rows": page["rows"], "people": page["people"], "opened": page["open_row"]})
        assert page["headline"] == standing.get("headline"), (page["headline"], standing.get("headline"))
        assert len(page["rows"]) == len(rows), page["rows"]
        assert not mismatches, json.dumps(mismatches, indent=2)
        assert page["people"] == people, (page["people"], people)
        if opened is not None:
            assert people, opened
        if vector == "COMMERCIAL" and vs.is_b2b(j.entry):
            role = j.founder.decider["role"].lower()
            assert role in page["decider_banner"].lower(), page["decider_banner"]


# --------------------------------------------------------------------------------- leg 8: brief

def expected_cards(j: Journey) -> list[dict]:
    """The entry's cards (keel-cloud 089 FR-001) as `instructions/brief_facts.py` reads them -- the reading
    spec 040's DRY compare proved equal to keel-cloud's own `BriefFactsCorpusTest` -- with the one
    dimension this journey had to leave out read as left out (D-1)."""
    standings = (j.entry.expected or {}).get("standings") or {}
    cards = []
    for dimension in j.registry.calibrated(j.entry.b2b()):
        standing = standings.get(dimension.key) or {}
        if expected_status(j.entry, dimension.key) == "LEFT_OUT":
            standing = {"status": "LEFT_OUT"}
        cards.append(brief_facts_mod.card(j.entry, dimension, standing))
    return cards


def _card(card: dict) -> dict:
    return {k: card.get(k) for k in brief_facts_mod.CARD_FIELDS} | {
        "statusWords": str(card.get("statusWords") or "").split(" · ", 1)[0]}


def leg_brief(j: Journey, *, timeout_s: float = 60) -> None:
    """The brief over the same standings, **on the wire** (`GET standings`, keel-cloud 089): on the scripted
    journeys the headline and the three stage answers are the referee's own and keel-cloud kept them
    (`fallbackUsed` false); every dimension's card is the entry's own (number, line, status); each stage's
    `broke` is the entry's deciding dimension where the stage broke; the pilot -- on the brief and on the
    overview's read -- is the entry's sign-ups over everyone who answered. On a live journey it is whatever
    the model wrote or code's fallback, a headline and three answers either way. keel-web 065's two pages and the
    download's tab are then held to that wire (`_brief_pages`)."""
    deadline = time.monotonic() + timeout_s * j.patience
    brief: dict = {}
    standings: dict = {}
    while time.monotonic() < deadline:
        standings = j.get(j.project("/standings")) or {}
        brief = standings.get("brief") or {}
        if brief.get("fallbackUsed") is False:
            break
        time.sleep(1)
    reading = brief.get("reading") or {}
    facts = brief.get("facts") or {}
    answers = {v.lower(): ((reading.get(v.lower()) or {}).get("answer") or {}) for v in VECTORS}
    headline = (reading.get("headline") or {}).get("text")
    with _step(j, "the brief reads a headline and one answer a stage" + (
            ", the scripted ones, not code's fallback" if j.strict else "")) as h:
        want = vs.brief_result(j.entry) if j.strict else None
        h.record_assert({"fallbackUsed": False, "reading": want} if j.strict else "a headline and three answers",
                        {"fallbackUsed": brief.get("fallbackUsed"), "reading": reading})
        assert headline and all((a.get("text") or "").strip() for a in answers.values()), reading
        assert set(reading) >= {"headline", "problem", "solution", "commercial", "next", "quotes"}, sorted(reading)
        if j.strict:
            assert brief.get("fallbackUsed") is False, brief.get("fallbackUsed")
            assert headline == want["headline"]["text"], headline
            for stage in ("problem", "solution", "commercial"):
                assert answers[stage] == want[stage]["answer"], (stage, answers[stage])
    if j.strict and j.registry is not None:
        with _step(j, "the brief's cards are the entry's own, one a dimension: number, line, status") as h:
            want_cards = [_card(c) for c in expected_cards(j)]
            have_cards = [_card(c) for c in facts.get("cards") or []]
            h.record_assert(want_cards, facts.get("cards"))
            assert have_cards == want_cards, json.dumps({"wire": have_cards, "corpus": want_cards}, indent=2)
        with _step(j, "each stage broke where the entry's verdict is a called failure, on its deciding "
                      "dimension") as h:
            want_broke = {v: vs.broke_key(j.entry, v) for v in VECTORS}
            have_broke = {v: ((facts.get(v.lower()) or {}).get("broke") or {}).get("key") for v in VECTORS}
            h.record_assert(want_broke, have_broke)
            assert have_broke == want_broke, (have_broke, want_broke)
        with _step(j, "the pilot: the entry's sign-ups over everyone who answered, per link -- on the brief "
                      "and on the overview's read") as h:
            want_pilot = brief_facts_mod.pilot_for(j.entry)
            h.record_assert(want_pilot, {"brief": facts.get("pilot"), "standings": standings.get("pilot")})
            assert facts.get("pilot") == want_pilot, (facts.get("pilot"), want_pilot)
            assert standings.get("pilot") == want_pilot, (standings.get("pilot"), want_pilot)
    _brief_pages(j, brief, standings)


#: Words keel-web 065 took off page one (FR-002; D3): none of them may come back.
PAGE_ONE_BANS = ("deal-breaker", "where they differ", "inferred from")


def pilot_words(pilot: dict) -> tuple[str, str]:
    """keel-web `pilotNumber` and `pilotLinkLine`: *2 of 12 · 17%* over *2 of 12 people who have it*."""
    big = f"{pilot.get('optedIn')} of {pilot.get('finished')} · {pilot.get('percent')}%"
    line = " · ".join(f"{p.get('optedIn')} of {p.get('finished')} {p.get('words')}" for p in pilot.get("perLink") or [])
    return big, line


def _card_words(card: dict) -> dict:
    return {"key": card.get("key"), "name": card.get("name"), "number": card.get("number") or None,
            "line": card.get("line"), "statusWords": card.get("statusWords")}


def _brief_pages(j: Journey, brief: dict, standings: dict) -> None:
    """keel-web 065's two pages over the brief `leg_brief` read off the wire, held to it on every journey: page
    one draws the served decision, headline and answers, each stage's served cards (every word, in order, each
    linking to its block), the pilot tile's *k of n · p%* and per-link line from both `facts.pilot` and
    `StandingsView.pilot`, the next tests, and none of the words 065 took off it; page two draws one block per
    card with the card's own words, *What broke* on the broke dimension's block alone; the download's tab draws
    page one again."""
    reading = brief.get("reading") or {}
    facts = brief.get("facts") or {}
    cards = facts.get("cards") or []
    page = j.screens["brief"] = j.answers.brief(j.project_id)
    with _step(j, "the brief, page one: the served decision, headline and answers, every card's words in order, "
                  "the pilot tile, the next tests, and nothing 065 took off it", party="founder") as h:
        decision = str((facts.get("decision") or {}).get("label") or "").lower()
        big, line = pilot_words(facts.get("pilot") or {})
        want = {"decision": decision, "headline": (reading.get("headline") or {}).get("text"),
                "stages": {stage: {"answer": ((reading.get(stage) or {}).get("answer") or {}).get("text"),
                                   "cards": [_card_words(c) for c in cards if str(c.get("key")).startswith(stage + ".")]}
                           for stage in ("problem", "solution", "commercial")},
                "pilot": {"big": big, "line": line},
                "next": [{"text": t.get("text"), "chip": t.get("key")} for t in (reading.get("next") or {}).get("tests") or []],
                "bans": []}
        tiles = page["tiles"]
        pilot_tile = tiles[-1] if tiles else {}
        have = {"decision": page["decision"], "headline": page["headline"],
                "stages": {stage: {"answer": drawn["answer"],
                                   "cards": [{k: c[k] for k in ("key", "name", "number", "line", "statusWords")}
                                             for c in drawn["cards"]]}
                           for stage, drawn in page["stages"].items()},
                "pilot": {"big": pilot_tile.get("big"), "line": pilot_tile.get("line")},
                "next": page["next"],
                "bans": [w for w in PAGE_ONE_BANS if w in page["text"].lower()]}
        h.record_assert(want, {**have, "tiles": tiles, "footer": page["footer"]})
        assert have == want, json.dumps({"page": have, "wire": want}, indent=2)
        assert len(tiles) == 4 and pilot_tile.get("pilot") and [t["pilot"] for t in tiles[:3]] == [False] * 3, tiles
        assert pilot_words(standings.get("pilot") or {}) == (big, line), (standings.get("pilot"), facts.get("pilot"))
        for drawn in page["stages"].values():
            for card in drawn["cards"]:
                assert str(card["href"] or "").endswith(f"/brief/breakdown#{card['key']}"), card
        assert page["footer"], "page one draws no footer"
    breakdown = j.screens["breakdown"] = j.answers.breakdown(j.project_id)
    with _step(j, "the brief, page two: one block per card with the card's own words, What broke on the broke "
                  "dimension's block alone, and the way back", party="founder") as h:
        want_blocks, have_blocks = {}, {}
        for stage in ("problem", "solution", "commercial"):
            mine = [c for c in cards if str(c.get("key")).startswith(stage + ".")]
            broke = ((facts.get(stage) or {}).get("broke") or {}).get("key")
            want_blocks[stage] = [{"key": c["key"], "name": c["name"], "statusWords": c["statusWords"],
                                   "card": " ".join(x for x in (c.get("number"), c.get("line")) if x),
                                   "broke": c["key"] == broke} for c in mine]
            have_blocks[stage] = [{"key": b["key"], "name": b["name"], "statusWords": b["statusWords"],
                                   "card": b["card"], "broke": b["broke"] is not None}
                                  for b in breakdown["stages"][stage]["blocks"]]
        h.record_assert(want_blocks, {"blocks": breakdown["stages"], "back": breakdown["back"]})
        assert have_blocks == want_blocks, json.dumps({"page": have_blocks, "wire": want_blocks}, indent=2)
        assert breakdown["back"] >= 1, "page two draws no way back to the brief"
    printed = j.screens["printed"] = j.answers.brief(j.project_id, printed=True)
    with _step(j, "the download's tab draws page one again: the same decision, headline and answers",
               party="founder") as h:
        same = {k: page[k] for k in ("decision", "headline")} | {
            "answers": {s_: d["answer"] for s_, d in page["stages"].items()}}
        got = {k: printed[k] for k in ("decision", "headline")} | {
            "answers": {s_: d["answer"] for s_, d in printed["stages"].items()}}
        h.record_assert(same, got)
        assert got == same, (got, same)


# ------------------------------------------------------------------------------------- the whole

def run(stack, founder_one, browser, run_dir, *, entry_id: str, slug: str,
        extra: Callable[[Journey], None] | None = None) -> None:
    """The whole scenario. `entry_id` is the only argument that differs between S-005, S-006 and
    S-007. `extra` is the one seam: the thing only *its* entry can say, handed the `Journey`."""
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    cell_label = (f"{remote.cell_name()} · corpus {slug} · "
                  f"{time.strftime('%Y-%m-%d', time.gmtime())}")
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    try:
        corpus, entry = vs.entry_for(stack.keel_cloud, entry_id)
    except (vs.VectorsScriptError, vs.corpus_reader.CorpusError) as refusal:
        import pytest                                       # noqa: PLC0415
        pytest.fail(f"{entry_id}: {refusal}", pytrace=False)
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    hashes_before = dict(corpus.hashes)
    script = vs.generate(entry)
    founder = vs.founder_inputs(entry)
    people = vs.person_inputs(entry)
    write_generated(run_dir, script=script.to_json(), inputs=vs.inputs_json(entry, founder, people))
    try:
        exported = contract_mod.export(stack.keel_cloud, run_dir / "export")
        keys_path = run_dir / "context-keys.json"
        keys_path.write_text(json.dumps(vs.context_keys_for(exported.context_keys), indent=2) + "\n",
                             encoding="utf-8")
        page = context.new_page()
        journey = open_journey(recorder, page, context, browser, stack, entry, founder, people,
                               script=script, registry=exported.registry)
        user_code = _connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path)
        own_ai_door(page, recorder, stack, journey.get, through_the_code_story=bool(user_code))

        leg_project(journey)
        leg_context(journey)
        leg_interpret_problem(journey)
        leg_calibrate(journey, "PROBLEM")
        leg_interpret_solution(journey)
        leg_calibrate(journey, "SOLUTION")
        leg_persona(journey)
        leg_calibrate(journey, "COMMERCIAL")
        leg_lock(journey)
        leg_invite(journey)
        leg_interview(journey)
        leg_standings(journey)
        leg_brief(journey)
        if extra is not None:
            extra(journey)

        with recorder.step("the corpus hashes exactly as it did when the run began",
                           party="stack", kind="assert") as h:
            corpus.verify_unchanged()
            h.record_assert(hashes_before, dict(corpus.hashes))
        passed = True
    finally:
        context.close()
        finalize_run(run_dir, slug=slug, facts=corpus_facts.vectors_facts_for(entry),
                     passed=passed, failed_step=recorder.failed_step,
                     duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")


def _connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path) -> str | None:
    """The runtime on this entry's script, then the founder signed in through the door the runtime's
    code opens (unchanged from the classic journeys: the runtime starts BEFORE the founder signs
    in, because keel-cloud decides the account's AI from the door it was created through)."""
    auth = Auth(page, recorder, web_base)
    if stack_runtime.status(stack).get("running"):
        stop_runtime(stack, recorder)
    if stack.is_remote:
        with recorder.step("the runtime home is put back the way `make up` leaves it",
                           party="stack", kind="protocol") as h:
            stack_runtime.reset(stack)
            h.record_wire({"home": str(stack_runtime.home_dir(stack))},
                          {"after": stack_runtime.status(stack)})
    result = start_runtime_via_skill(stack, recorder, env_extra={
        "KEEL_SCRIPT": str(run_dir / "script.json"),
        "KEEL_CONTEXT_KEYS": str(keys_path)})
    user_code = result.get("user_code")
    if result.get("outcome") == "authorization_started" and user_code:
        auth.sign_in_with_code(founder_one, user_code)
        connect = Connect(page, recorder)
        connect.open(result["verification_uri"])
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()
    else:
        # **No code, so no code story.** The runtime reconnected on a credential the home already
        # held, which is what a local profile does; `ai_path` is immutable, so this sign-in cannot
        # move it either way, and the ordinary door is what a returning founder uses.
        with recorder.step("no device code: the runtime reconnected on the credential its "
                           "home already held, so this founder signs in as a returning one",
                           party="stack", kind="note") as h:
            h.record_wire({"outcome": result.get("outcome")},
                          {"user_code": user_code,
                           "why it does not decide a door": (
                               "keel-cloud reads the door only on the branch that CREATES "
                               "the account (keel-cloud spec 044 FR-014); a returning "
                               "founder keeps whatever their row already says")})
        auth.sign_in(founder_one)
    Landing(page, recorder, web_base).visit()
    return user_code
