"""S-005, S-006 and S-007's whole body: the corpus journeys, as **vectors** journeys (spec 039; spec 041:
corpus revision 10, contract 13, keel-web 063's founder screens and 064's stranger's screens; spec 042: corpus
revision 11, contract 14 -- one RESPONDENT_QUESTIONS job a lock, the founder's name for the idea).

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
                      solution's first question**: S2, the three lines checked (one entry's founder
                      names the idea there, keel-cloud 090), Save approving them.
6. `leg_persona`   -- who decides; on a B2B entry the decision-maker's respondent type.
7. `leg_lock`      -- step 5's two screens, *Lock and write the questions*; ONE RESPONDENT_QUESTIONS job
                      (keel-cloud 091: part 1; parts 2 and 3 code's); READY; the lock stores every saved
                      list and its picked index (D7).
8. `leg_invite`    -- one link per corpus person: the primary link, or on a B2B entry the
                      decision-maker's commercial link.
9. `leg_interview` -- each person in their own browser context, no founder session, through keel-web
                      064's screens: the decision-maker's idea screen first, the gate (its one chip), every
                      item as served (one escape, last), two picks on Importance, the fixed answers,
                      "nothing" typed as 0; the idea card and the Relative advantage question on the
                      idea's current name (keel-cloud 090); the founder reads after each person.
10. `leg_standings` -- `GET standings` against the entry's `expected.standings` and `expected.vector_verdicts`
                      (codes mapped onto the wire's), and the same on the board (its pilot tile among them)
                      and the three stage pages, one row's per-person list among them.
11. `leg_brief`    -- the brief on the wire: the scripted headline and three answers, a card per dimension
                      equal to the eval's own reading of the entry (`instructions/brief_facts.py`, which
                      spec 040's DRY proved equal to keel-cloud's), what broke, the pilot -- and keel-web
                      065's two pages held to that wire: page one (the decision, headline, answers, every
                      card's words, the pilot tile), page two (one block a card, *What broke* on the broke
                      block alone) and the download's tab.

After them each scenario's `extra` runs: S-006's ends with **the contacts leg** (spec 043, keel-cloud 093,
`evals/contacts_leg.py`) on the wire, and S-005's with the B2C `NOT_B2B` refusal.

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
from evals import feedback_marks
from evals.preludes import create_project, own_ai_door
from harness import vectors_script as vs
from harness import interviews_screens as iv_screens
from harness import vectors_screens as vs_screens
from harness.browser import Auth, Connect, Landing
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
    #: The idea's name every later question uses, as the wire stored it after S2 (`IdeaView.shortName`, keel-cloud 090).
    idea_name: str = ""
    #: The lock's receipt (`LockReceipt`), as keel-web received it from `POST lock`.
    receipt: dict = field(default_factory=dict)
    #: The stack and the identity the founder signed in as (spec 043: the contacts leg reads the ledger and stands the
    #: founder on Keel's door, `stack/ledger.py`). None on S-012, which never runs that leg.
    stack: Any = None
    founder_identity: Any = None
    #: Spec 046: the record `evals/feedback_marks.py` scores at the end of the journey (FM1-FM6).
    feedback: dict = field(default_factory=dict)

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
    with _step(j, "the mechanism card offers no *Someone else would use it* (keel-web 070 F8): who decides is asked "
                  "once, on the persona step", party="founder") as h:
        offered = [words for words in vs_screens.SOMEONE_ELSE_USES if words in card["text"]]
        h.record_assert([], offered)
        assert not offered, offered
    j.corridor.confirm_seed("SOLUTION")
    view = _wait_calibration(j, "SOLUTION")
    typed = j.founder.idea_name
    _idea_unnamed(j, typed)
    seen = j.corridor.idea_check(typed)
    j.framing["idea"] = [seen]
    if seen["reloaded"]:
        # runs/DRIFT.md #78, closed by keel-web 066 (IdeaCheck refills from the served idea): spec 041 reloaded the page
        # once. The page object still reloads (so the bundle shows what followed), and the journey fails here.
        with _step(j, f"{j.entry.id}: DRIFT #78 came back -- S2 drew three empty lines and needed a reload "
                      "(closed by keel-web 066)", party="founder") as h:
            h.record_assert({"reloaded": False}, {"reloaded": True, "lines after the reload": seen["lines"]})
            raise AssertionError("DRIFT #78 came back: S2's lines were empty until the page was reloaded")
    with _step(j, "S2: What it is carries keel-web 066's live counter, n / 5 words, and Save is off over five "
                  "(keel-cloud 090 L5, D14)", party="founder") as h:
        counter = seen.get("counter") or {}
        drawn_words = len(seen["lines"]["what"].split())
        over = counter.get("over") or {}
        want = {"drawn": {"text": f"{drawn_words} / 5 words", "over": False, "save_enabled": drawn_words > 0},
                "over": {"typed": over.get("typed"), "text": f"{len(str(over.get('typed')).split())} / 5 words",
                         "over": True, "save_enabled": False},
                "named": {"text": f"{len(typed.split())} / 5 words", "over": False, "save_enabled": True}}
        h.record_assert(want, counter)
        assert counter == want, json.dumps({"screen": counter, "want": want}, indent=2)
        assert len(str(counter["over"]["typed"]).split()) == 6, counter
    with _step(j, "S2: the idea's how and belief are the mechanism's, the what line the name the founder typed "
                  "(keel-cloud 097 F7), under Solution · 1 of n, and Save approved them on the wire",
               party="founder") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_view(j.entry)
        total = len(view.get("questions") or []) + STAGE_OFFSET["SOLUTION"]
        name = vs.idea_name_of(typed)
        h.record_assert({**({k: want[k] for k in ("how", "belief")} if j.strict else {}), "typed": typed, "name": name,
                         "approved": True, "progress": f"Solution · 1 of {total}"},
                        {"screen": seen, "wire": idea})
        assert all((idea.get(k) or "").strip() for k in ("what", "how", "belief")), idea
        assert {k: idea.get(k) for k in ("how", "belief")} == {k: seen["lines"][k] for k in ("how", "belief")}, (
            idea, seen["lines"])
        assert not (idea.get("what") or "").lower().startswith("imagine"), idea
        assert idea.get("what") == name, (idea.get("what"), name)
        assert idea.get("approved") is True, idea
        assert idea.get("shortName") == idea.get("what"), idea
        _hold_frame(seen["frame"], "SOLUTION", 1, total)
        if j.strict:
            assert {k: seen["lines"][k] for k in ("how", "belief")} == {k: want[k] for k in ("how", "belief")}, (
                seen["lines"], want)
            assert idea.get("shortName") == vs.idea_name(j.entry), (idea, vs.idea_name(j.entry))
        j.idea_name = str(idea.get("shortName") or "")
        named = j.feedback.setdefault("idea", {})
        named.update({"stored": idea.get("what"), "approved": idea.get("approved"), "typed_name": name})
        if not NAME_ON_THE_WIRE:
            named["screen"] = seen["unnamed"]
    if not NAME_ON_THE_WIRE:
        with _step(j, "S2 demands the name (keel-web 070 F7): the what box empty with its placeholder *Name it in up "
                      "to five words*, 0 / 5 words and Save off, until the founder typed one", party="founder") as h:
            want = {"value": "", "placeholder": feedback_marks.NAME_PLACEHOLDER, "save_enabled": False}
            h.record_assert(want, seen["unnamed"])
            assert seen["unnamed"] == want, seen["unnamed"]
    if typed != m["short_name"]:
        with _step(j, f"{j.entry.id}: the founder named the idea {typed!r} on S2, not the mechanism card's "
                      f"{m['short_name']!r} (keel-cloud 090, D14)", party="founder") as h:
            plan = j.get(j.project("/plan")) or {}
            h.record_assert({"shortName": vs.idea_name_of(typed), "plan.idea.what": vs.idea_name_of(typed)},
                            {"idea": idea, "plan.idea": plan.get("idea")})
            assert j.idea_name == vs.idea_name_of(typed) != m["short_name"], (j.idea_name, m["short_name"])
            assert len(typed.split()) <= 5, typed
            assert ((plan.get("idea") or {}).get("what")) == j.idea_name, plan.get("idea")


#: Spec 046 T004: True names the idea on the wire (`PUT idea`) before S2, so the screen opens on the name and its Save
#: approves it -- the stand-in until keel-web 070's S2 (the wire phase). False, since 070: S2 opens empty and the
#: journey types the name there.
NAME_ON_THE_WIRE = False


def _idea_unnamed(j: Journey, typed: str) -> None:
    """keel-cloud 097 F7 (spec 046 FM4): Keel no longer drafts the idea's name. The mechanism card landed with `what`
    null (no r11 seed carries a product name -- `vs.seed_idea_name`), and the server refuses an unnamed idea: approve
    is 422 IDEA_NAME_REQUIRED (097 call 16), and so is `PUT idea` with an empty name; neither writes. The journey then
    names it -- on the wire, `PUT idea` with the name it types (`NAME_ON_THE_WIRE`), until S2 types it."""
    seed_name = vs.seed_idea_name(j.founder.solution_seed)
    with _step(j, "the idea arrives unnamed (keel-cloud 097 F7): what is null, approve and an empty name are refused "
                  "422 IDEA_NAME_REQUIRED, and nothing is written", party="founder", kind="assert") as h:
        idea = j.get(j.project("/idea")) or {}
        revision = j.revision()
        approve, approve_body = j.call("POST", j.project("/idea/approve"), {"expectedRevision": revision},
                                       ok=(200, 422))
        empty, empty_body = j.call("PUT", j.project("/idea"), {
            "expectedRevision": revision, "what": "", "how": idea.get("how"), "belief": idea.get("belief")},
            ok=(200, 422))
        after = j.get(j.project("/idea")) or {}
        refusals = {"approve": {"status": approve, "code": _refusal(approve_body)},
                    "empty": {"status": empty, "code": _refusal(empty_body)}}
        j.feedback["idea"] = {"seed_name": seed_name, "served": idea.get("what"), "refusals": refusals,
                              "typed": typed, "named_on": "wire" if NAME_ON_THE_WIRE else "screen"}
        h.record_assert({"seed name": None, "what": None, "approve": [422, feedback_marks.IDEA_NAME_REQUIRED],
                         "empty": [422, feedback_marks.IDEA_NAME_REQUIRED], "revision": revision},
                        {"seed name": seed_name, "idea": idea, "refusals": refusals, "after": after,
                         "bodies": [approve_body, empty_body]})
        assert seed_name is None, seed_name
        assert idea.get("what") is None and idea.get("approved") is False, idea
        for refusal in refusals.values():
            assert (refusal["status"], refusal["code"]) == (422, feedback_marks.IDEA_NAME_REQUIRED), refusals
        assert after.get("revision") == revision and after.get("approved") is False, after
    if not NAME_ON_THE_WIRE:
        return
    with _step(j, f"the journey names the idea {vs.short_name(j.entry)!r} on the wire (PUT idea, spec 046 T004 until "
                  "keel-web 070's page objects) -- not approved until S2's Save", party="founder", kind="protocol") as h:
        body = {"expectedRevision": j.revision(), "what": vs.short_name(j.entry), "how": idea.get("how"),
                "belief": idea.get("belief")}
        _, named = j.call("PUT", j.project("/idea"), body)
        j.page.reload(wait_until="load")
        h.record_wire(body, named)
        assert named.get("what") == vs.idea_name_of(vs.short_name(j.entry)) and named.get("approved") is False, named


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
        _keep_draft(j, question, "first", None)
        if answer.unsure:
            j.framing[key] = [j.corridor.list_answer(question, None)]
            continue
        seen = [j.corridor.list_answer(question, answer.text)]
        drafted = _wait_calibration(j, vector)
        question = next((q for q in drafted.get("questions") or [] if q.get("dimension") == key), question)
        _keep_draft(j, question, "answer", answer.text)
        typed = vs.importance_typed(j.entry) if (key == "problem.importance" and j.strict) else []
        if typed:
            seen.append(j.corridor.list_check(question, add=typed, one_more=len(vs.importance_named(j.entry)) == 1))
            _hold_importance_check(j, seen[-1], typed)
        else:
            seen.append(j.corridor.list_check(question))
        if key in vs.PICKED:
            label, _ = _choose_label(j, question, answer)
            seen.append(j.corridor.list_choose(question, label))
        j.framing[key] = seen
    refused = j.corridor.conflicts[conflicts:]
    if refused:
        # runs/DRIFT.md #80, closed by keel-cloud 091 FR-A (`GET calibration/{vector}` reads the interaction first and
        # the project second, so a READY is always over the drafted project): spec 041 pressed again after the poll.
        # Spec 042 keeps the page object's second press only so the bundle shows what followed, and fails here.
        with _step(j, f"{j.entry.id}: DRIFT #80 came back -- {len(refused)} {vector.lower()} write(s) refused 409 "
                      "after a redraft (closed by keel-cloud 091)", party="founder") as h:
            h.record_assert({"refused": 0}, refused)
            raise AssertionError(f"DRIFT #80 came back: {json.dumps(refused)}")

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
            box = (choose or check).get("test_after") or (choose or check)["test"] \
                if (choose or key in KEEL_SET) else None
            if box is None or box["belief"] == sentence:
                continue
            if key == "commercial.buyer_payer_alignment" and _capital(box["belief"]) == sentence:
                lower_case.append({"dimension": key, "keel will test": box["belief"], "server": sentence})
                continue
            mismatches.append({"dimension": key, "keel will test": box["belief"], "corpus": sentence})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)
    if lower_case:
        # runs/DRIFT.md #79, closed by keel-web 066 (fillBelief capitalises): spec 041 held the preview equal but for
        # its first letter. Spec 042 fails the journey if the lower-case head is ever drawn again.
        with _step(j, f"{j.entry.id}: DRIFT #79 came back -- the Choose screen's Buyer-and-payer belief opens "
                      "lower-case (closed by keel-web 066)", party="founder") as h:
            h.record_assert({"server": [r["server"] for r in lower_case]},
                            {"screen": [r["keel will test"] for r in lower_case]})
            raise AssertionError(f"DRIFT #79 came back: {json.dumps(lower_case)}")

    if vector == "COMMERCIAL" and j.founder.hourly_rate is not None:
        _hourly_rate(j)
    if vector == "PROBLEM" and not answers["problem.importance"].unsure:
        _importance_needs_three(j)
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


def _hold_importance_check(j: Journey, seen: dict, typed: list[str]) -> None:
    """keel-web 070 F9 on Importance's Check screen: the counter reads *yours + n* for what the Answer named; with one
    named the screen asks for one more in the founder's words, Save is refused 422 ONE_MORE_NEEDED and opens a line;
    with two the ask is absent and Save on. The founder types the rest of their own list, and the counter reads
    *yours + 4*. The *Keel will test* box's sentence counts the list as it stands: *out of two* / *three*, then *five*
    (keel-web 070 fills `{list_size}`)."""
    named = len(vs.importance_named(j.entry))
    x = seen["importance"]
    one = named == 1
    with _step(j, f"Importance's Check screen with {named} other{'s' if named != 1 else ''} (keel-web 070 F9): "
                  f"*yours + {named}*" + (", the ask for one more, Save refused 422 ONE_MORE_NEEDED and a line opened"
                                          if one else ", no ask, Save on") +
               f"; the founder types {len(typed)} more and it reads *yours + {named + len(typed)}*",
               party="founder") as h:
        size = ["zero", "one", "two", "three", "four", "five"]
        want = {"counter": f"yours + {named}", "ask": ONE_MORE_ASK if one else "",
                "save_enabled": True, "added": typed, "counter_after": f"yours + {named + len(typed)}",
                "ask_after": "", "test": f"out of {size[1 + named]}.",
                "test_after": f"out of {size[1 + named + len(typed)]}."}
        if one:
            want["refused"] = {"status": 422, "code": feedback_marks.ONE_MORE_NEEDED}
        have = {k: x.get(k) for k in want if k not in ("refused", "test", "test_after")}
        have["test"] = next((f"out of {w}." for w in size if (seen["test"]["belief"] or "").endswith(f"out of {w}.")),
                            seen["test"]["belief"])
        have["test_after"] = next((f"out of {w}." for w in size
                                   if ((seen.get("test_after") or {}).get("belief") or "").endswith(f"out of {w}.")),
                                  (seen.get("test_after") or {}).get("belief"))
        if one:
            refused = x.get("refused") or {}
            have["refused"] = {"status": refused.get("status"), "code": _refusal(refused.get("body"))}
        h.record_assert(want, {**have, "after the refusal": x.get("after_refusal")})
        assert have == want, json.dumps({"screen": have, "want": want}, indent=2)
        j.feedback["importance_typed"] = list(typed)


#: keel-web 070 `listOneMore(1)`: the Check screen's ask below three in all.
ONE_MORE_ASK = "Name one more difficulty, in your own words. People pick two of these, so the list needs three."


def _keep_draft(j: Journey, question: dict, draft: str, answer: str | None) -> None:
    """Spec 046 (FM1, FM2): a list Keel drafted, as the wire served it on `GET calibration/{vector}` -- the slice's
    first draft, or the redraft from the founder's Answer -- with the Answer it was drafted from."""
    listed = question.get("draft") or {}
    key = question.get("dimension")
    fixed = vs.NOBODY_ELSE[0] if key == "commercial.buyer_payer_alignment" else None
    items = [{"label": i.get("label"), "asked": i.get("asked"), **({"fixed": True} if fixed and i.get("code") == fixed
                                                                    else {})}
             for i in listed.get("items") or []]
    j.feedback.setdefault("lists", []).append({"dimension": key, "draft": draft, "items": items,
                                               "phrase": listed.get("phrase"), "answer": answer})


def _importance_needs_three(j: Journey) -> None:
    """keel-cloud 097 F9 on the wire (spec 046 FR-003): strangers pick two, so Importance is saved with the own item
    and at least two others. The founder's saved list cut to the own item and one other is refused **422
    ONE_MORE_NEEDED** ("name one more difficulty") and writes nothing; cut to the own item and two it is saved (200)
    and its belief reads "out of three"; the founder's own list is then saved again and reads "out of five". The page
    is reloaded after, as `_hourly_rate` does, so its next write is at the new revision."""
    key = "problem.importance"
    saved = vs.saved_list(j.entry, key)
    labels = [{"label": i["label"]} for i in saved["items"]]

    def put(items: list[dict], ok: tuple) -> tuple[int, Any]:
        body = {"expectedRevision": j.revision(),
                "answers": [{"dimension": key, "list": {"items": items, "pickedIndex": None}}]}
        return j.call("PUT", j.project("/calibration/PROBLEM"), body, ok=ok)

    def belief(rows: Any) -> str:
        return next((r.get("belief") or "" for r in (rows or {}).get("rows") or [] if r.get("dimension") == key), "")

    with _step(j, "Importance needs three on the wire (keel-cloud 097 F9): the own item and one other is refused 422 "
                  "ONE_MORE_NEEDED and writes nothing; the own item and two others saves (200, \"out of three\"); "
                  "the founder's own list saves again (\"out of five\")", party="founder", kind="protocol") as h:
        before = j.revision()
        one, one_body = put(labels[:2], (422,))
        after_one = j.revision()
        two, two_body = put(labels[:3], (200,))
        back, back_body = put(labels, (200,))
        j.page.reload(wait_until="load")
        probe = {"own+1": {"status": one, "code": _refusal(one_body),
                           "remedy": (one_body or {}).get("remedy") if isinstance(one_body, dict) else None,
                           "revision moved": after_one != before},
                 "own+2": {"status": two, "belief": belief(two_body)},
                 "own+4": {"status": back, "belief": belief(back_body)}}
        j.feedback.setdefault("importance_probe", probe)
        h.record_wire({"own+1": labels[:2], "own+2": labels[:3], "own+4": labels}, probe)
        assert (one, _refusal(one_body)) == (422, feedback_marks.ONE_MORE_NEEDED), one_body
        assert probe["own+1"]["remedy"] == "name one more difficulty", one_body
        assert not probe["own+1"]["revision moved"], probe
        assert probe["own+2"]["belief"].endswith("out of three."), probe
        want = (j.entry.founder_calibration.get(key) or {}).get("belief_sentence")
        assert not j.strict or probe["own+4"]["belief"] == want, (probe, want)


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
    drawn nowhere on Check (it is Choose's first radio); Importance is drawn as Keel redrafted it, the own item and what
    the Answer named (the founder types the rest there, keel-web 070 F9)."""
    saved = vs.founder_list(entry, key)
    labels = [i["label"] for i in saved["items"] if i.get("code") != vs.NOBODY_ELSE[0]]
    if key == "problem.importance":
        labels = labels[:1 + len(vs.importance_named(entry))]
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
    """Step 5's three screens since keel-web 069 (*A word from you* 1 of 3, *The pilot* 2 of 3, L1 *Who asks the
    questions* 3 of 3 -- on the own door one line and *Lock and approve*; the idea moved to S2), then the lock:
    **one** RESPONDENT_QUESTIONS job (keel-cloud 091, contract 14: part 1 on the
    primary link, the gate's clause; parts 2 and 3 -- on B2B part 3 the decision-maker's link's -- composed by code in
    the lock's own commit), READY before anyone is invited, and the lock storing every saved list with its picked
    index (design §6, D7)."""
    drawn = j.corridor.word_pilot_and_lock()
    j.receipt = drawn.get("receipt") or {}
    j.screens["L1"] = drawn.get("l1") or {}
    with _step(j, "step 5 is three screens since keel-web 069 -- 1 of 3, 2 of 3 and L1 *Who asks the questions* 3 "
                  "of 3, which on an account on its own AI is one line and *Lock and approve*, no carousel; the "
                  "lock's receipt carries no interviewer (contract 16)", party="founder") as h:
        l1 = drawn.get("l1") or {}
        h.record_assert({"counters": ["1 of 3", "2 of 3", "3 of 3"], "title": vs_screens.L1_TITLE,
                         "sub": vs_screens.BEFORE_INTERVIEWER_OWN, "carousel": False,
                         "button": vs_screens.BEFORE_LOCK_APPROVE, "receipt.interviewer": None},
                        {**l1, "counters": drawn["counters"], "receipt": j.receipt})
        assert drawn["counters"] == ["1 of 3", "2 of 3", "3 of 3"], drawn
        assert l1.get("title") == vs_screens.L1_TITLE and l1.get("carousel") is False, l1
        assert l1.get("sub") == vs_screens.BEFORE_INTERVIEWER_OWN, l1
        assert l1.get("button") == vs_screens.BEFORE_LOCK_APPROVE, l1
        assert "interviewer" not in j.receipt, j.receipt
    deadline = time.monotonic() + 120 * j.patience
    state = None
    while time.monotonic() < deadline:
        state = (j.get(j.project("/overview")) or {}).get("questionsState")
        if state in ("READY", "FAILED"):
            break
        time.sleep(0.5)
    if state == "FAILED":
        # runs/DRIFT.md #81, closed by keel-cloud 091 FR-B (FAILED is believed over a fresh project): spec 041 read
        # again once before believing a FAILED. Spec 042 keeps no re-read -- a FAILED now fails the journey, and the
        # step says #81 may have come back if the job itself landed.
        interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
        landed = [i.get("status") for i in interactions if i.get("screen") == "RESPONDENT_QUESTIONS"]
        with _step(j, f"{j.entry.id}: the overview read the questions FAILED -- DRIFT #81 is closed by keel-cloud "
                      "091, so this is a failure, not a race to step round", party="stack") as h:
            h.record_assert({"questionsState": "READY"}, {"questionsState": state, "jobs": landed})
            raise AssertionError(f"questionsState FAILED after the lock (RESPONDENT_QUESTIONS jobs: {landed}); "
                                 "DRIFT #81 came back if every job is APPLIED")
    with _step(j, "the lock started ONE RESPONDENT_QUESTIONS job -- part 1, the gate's clause -- and no other "
                  "(keel-cloud 091, contract 14: LockReceipt.questions.interactionIds is exactly 1)") as h:
        ids = list(((j.receipt.get("questions") or {}).get("interactionIds")) or [])
        interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
        respondent = [i for i in interactions if i.get("screen") == "RESPONDENT_QUESTIONS"]
        h.record_assert({"interactionIds": 1, "RESPONDENT_QUESTIONS jobs": 1, "status": "APPLIED"},
                        {"receipt": j.receipt, "jobs": [{k: i.get(k) for k in ("interaction_id", "status", "job")}
                                                         for i in respondent]})
        assert len(ids) == 1, j.receipt
        assert [i.get("interaction_id") for i in respondent] == ids, (ids, respondent)
        assert respondent[0].get("status") == "APPLIED", respondent[0]
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
    """One link per corpus person, in corpus order, through keel-web 068's Interviews section (spec 043's second
    commit; the People page and its two popups are gone): Sent, W1 the walkthrough the first time this account
    arrives, then each kind's *Send the questions* / *Send more* -- Text, *Someone I know*, the person's name, *Make
    their link* -- for the specialist and, on a B2B entry, the decision-maker (one `POST invitations/batch` for both,
    068 call 11). The register is then held to the wire: newest link first, one row a person, Text, not opened."""
    register = j.get(j.project("/invitations")) or {}
    labels = {k.get("respondentType"): k.get("label") for k in register.get("kinds") or []}
    persona = j.get(j.project("/persona")) or {}
    primary = next(t for t in persona.get("respondentTypes") or [] if not t.get("commercialLink"))
    sent = iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience)
    me_before = j.get("/v2/me") or {}
    walked = sent.land(j.project_id)
    with _step(j, "Interviews (keel-web 068 FR-002 / FR-003): the side nav's group with its three sub-rows, Sent "
                  "current; the walkthrough played exactly when the account had never seen it, and Got it stamped it",
               party="founder") as h:
        nav = sent.nav()
        me_after = j.get("/v2/me") or {}
        h.record_assert({"row": iv_screens.NAV_INTERVIEWS, "subs": iv_screens.SUBPAGES, "current": ["Sent"],
                         "walkthrough": me_before.get("walkthroughSeenAt") is None},
                        {"nav": nav, "walkthrough": walked, "seen before": me_before.get("walkthroughSeenAt"),
                         "seen after": me_after.get("walkthroughSeenAt")})
        assert nav["row"] == iv_screens.NAV_INTERVIEWS and (nav["href"] or "").endswith(
            f"/p/{j.project_id}/interviews/sent"), nav
        assert nav["subs"] == iv_screens.SUBPAGES and nav["current"] == ["Sent"], nav
        assert (walked is not None) == (me_before.get("walkthroughSeenAt") is None), (walked, me_before)
        if walked is not None:
            assert walked["title"] == iv_screens.WALKTHROUGH_TITLE and walked["patch"]["status"] == 200, walked
        assert me_after.get("walkthroughSeenAt"), me_after
    for person in j.people:
        kind = vs.LINK_B2B if person.link == vs.LINK_B2B else vs.LINK_PRIMARY
        about = None if kind == vs.LINK_B2B else f"{primary.get('label')}, asked about one real time."
        made = sent.send_someone(j.project_id, labels[kind], person.person, about)
        link = ((made["batch"] or {}).get("links") or [{}])[0]
        with _step(j, f"{person.person}: one link on the {kind} kind, handed back once and drawn as it came",
                   party="founder") as h:
            h.record_assert({"status": 201, "format": "TEXT", "drawn": link.get("url"), "personName": person.person},
                            {"status": made["status"], "format": (made["batch"] or {}).get("format"),
                             "drawn": made["url"], "link": link, "formats": made["formats"]})
            assert made["status"] == 201 and (made["batch"] or {}).get("format") == "TEXT", made
            assert made["url"] == link.get("url") and link.get("personName") == person.person, made
            # keel-web 069: *Text only*; on their own AI the other two greyed *needs Keel's credits*
            assert made["formats"].get(iv_screens.TEXT_ONLY, {}).get("checked") is True, made["formats"]
            assert all(f["disabled"] and f["word"] == iv_screens.FORMAT_NEEDS_CREDITS
                       for name, f in made["formats"].items() if name != iv_screens.TEXT_ONLY), made["formats"]
        j.links[person.person] = made["url"]
        j.tokens[person.person] = made["url"].rstrip("/").rsplit("/", 1)[-1]
    with _step(j, "every corpus person has a link of their own; the Sent register draws one row a person, newest "
                  "link first, as the wire lists them", party="founder") as h:
        wire = (j.get(j.project("/invitations")) or {}).get("invitations") or []
        drawn = sent.register()
        h.record_assert({"links": len(j.people), "order": [p.person for p in j.people][::-1]},
                        {"links": len(set(j.tokens.values())), "wire": [r.get("personName") for r in wire],
                         "drawn": drawn})
        assert len(set(j.tokens.values())) == len(j.people), j.tokens
        assert [r.get("personName") for r in wire] == [p.person for p in j.people][::-1], wire
        assert [r.get("Who") for r in drawn] == [r.get("personName") for r in wire], drawn
        assert {r.get("Format") for r in drawn} == {"Text"}, drawn
        assert all((r.get("Status") or "").startswith(iv_screens.REGISTER_STATUS["SENT"]) for r in drawn), drawn
    # keel-web 066 (D15): before anyone finishes, the board's pilot tile reads *None yet* with no per-link line.
    j.standings = j.get(j.project("/standings")) or {}
    _board_tiles(j, j.answers.board(j.project_id), "before anyone answered")


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
    _brief_on_return(j)


def _briefs(j: Journey) -> list[dict]:
    interactions = j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
    return [i for i in interactions if i.get("screen") == "BRIEF"]


def _brief_on_return(j: Journey, *, timeout_s: float = 60) -> None:
    """keel-cloud 096 (spec 045): no batch writes the brief any more -- it is written when the founder comes back. After
    every answer is read the project holds **no** BRIEF; the founder's own read of the project (`GET overview` on their
    session, which on their own AI is the session the agent is bound to) starts **one**, and the brief lands."""
    with _step(j, "the brief waits for the founder (keel-cloud 096): every answer read and no BRIEF yet; the founder "
                  "opens the project (GET overview) and exactly one BRIEF is started and lands", party="founder") as h:
        before = _briefs(j)
        overview = j.get(j.project("/overview")) or {}
        deadline = time.monotonic() + timeout_s * j.patience
        after = _briefs(j)
        landed = lambda rows: any(b.get("status") == "APPLIED" or (b.get("status") in TERMINAL_BAD  # noqa: E731
                                                                    and b.get("status") != "STATE_CONFLICT")
                                  for b in rows)
        while time.monotonic() < deadline and not landed(after):
            time.sleep(1)
            after = _briefs(j)
        h.record_assert({"BRIEF before the return": 0, "BRIEF after it": "one APPLIED (a lost race's retries, up to "
                                                                          "three in all, STATE_CONFLICT)"},
                        {"before": [(b.get("status"), b.get("interaction_id")) for b in before],
                         "after": [(b.get("status"), b.get("interaction_id")) for b in after],
                         "awaitingInterpretation": overview.get("awaitingInterpretation")})
        assert before == [], before
        statuses = sorted(b.get("status") for b in after)
        assert 1 <= len(after) <= 3 and statuses.count("APPLIED") == 1, after
        assert set(statuses) <= {"APPLIED", "STATE_CONFLICT"}, after        # 095: a lost race is retried


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
            assert walked.get("status") in (200, 201), walked.get("status")
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
    _hold_the_idea_name(j, person, interview, walked)


#: The dimension whose stem carries the idea's name (keel-cloud 085 / 091 `BenefitFirst.question`).
RA_KEY = "solution.relative_advantage"


def _hold_the_idea_name(j: Journey, person, interview: dict, walked: dict) -> None:
    """keel-cloud 090 (D14) on every journey: the idea card strangers read is *Imagine {name}.* and the Relative
    advantage question *On your last {occasion}, would {name} have made things better, or not?*, both composed by code
    around the idea's **current** name -- the one the wire stored after S2 (`IdeaView.shortName`): Keel's short name
    where the founder saved the draft untouched, the founder's own where they renamed it. Held on the wire (the served
    reveal / idea and the item's question) and on the screens (the reveal's or idea screen's card, and the idea card
    above the Relative advantage item)."""
    name = j.idea_name
    card = vs.idea_card(name)
    served = [("reveal", interview.get("reveal")), ("idea", interview.get("idea"))]
    items = {i.get("dimension"): i for p in interview.get("parts") or [] for i in p.get("items") or []}
    advantage = items.get(RA_KEY)
    if not any(lines for _, lines in served) and advantage is None:
        return                                       # a gate No: nothing about the idea was served
    with _step(j, f"{person.person}: the idea card and the Relative advantage question name the idea "
                  f"{name!r}, its current name (keel-cloud 090)", party="participant") as h:
        faults = []
        occasion = interview.get("occasion") or ""
        want_question = vs.benefit_question(occasion, name)
        for kind, lines in served:
            if lines and lines.get("what") != card:
                faults.append({kind: lines.get("what"), "want": card})
        if advantage is not None and advantage.get("question") != want_question:
            faults.append({"question": advantage.get("question"), "want": want_question})
        if j.strict and occasion != vs.occasion(j.entry):
            faults.append({"occasion": occasion, "corpus": vs.occasion(j.entry)})
        for drawn in walked["screens"]:
            if drawn.get("screen") in ("reveal", "idea") and card not in (drawn.get("card") or ""):
                faults.append({"screen": drawn.get("screen"), "card": drawn.get("card"), "want": card})
            if drawn.get("screen") == "item" and drawn.get("dimension") == RA_KEY and drawn.get("idea_card") != card:
                faults.append({"screen": "item", "idea card": drawn.get("idea_card"), "want": card})
        h.record_assert({"card": card, "question": want_question, "faults": []},
                        {"served": dict(served), "question": (advantage or {}).get("question"), "faults": faults})
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
    """The person's answer is read when this person wrote a story the reader is shown; nobody else's answer queues a
    reading (a gate no, a chip, the decision-maker's link).

    **Since keel-cloud 095 (DRIFT #84 resolved for Keel's door)** a Keel's-door project reads every answer on arrival:
    the journey presses nothing, waits for the newest batch -- the arrival's, which it did not start -- and any after
    it to be DONE, and a `POST readings` of its own is refused 409 (`READING_IN_PROGRESS` while it runs,
    `NOTHING_TO_READ` once all is read). **On the founder's own AI with the agent connected before the answers**
    nothing reads on arrival (095 judgement call 14: the own door reads at its next connect or on the founder's own
    `POST readings`), so the founder's session asks for the reading on the wire -- the call People's button made --
    exactly as before (spec 044 call 151)."""
    readable = any(p.person == person.person for p in vs.readable_people(j.entry))
    if not readable:
        return
    door = (j.get("/v2/me") or {}).get("aiPath")
    if door == "KEEL":
        _read_on_arrival(j, person)
        return
    with _step(j, f"{person.person}'s answer: on their own AI with the agent connected nothing reads on arrival "
                  "(keel-cloud 095 call 14), so the founder's session asks for the reading on the wire",
               party="founder", kind="note") as h:
        deadline = time.monotonic() + 45 * j.patience
        while True:
            status, started = j.call("POST", j.project("/readings"), {}, ok=(201, 409))
            if status == 201:
                break
            if time.monotonic() > deadline:
                raise AssertionError(f"{person.person}'s answer never reached a reading: {started}")
            time.sleep(1)
        h.record_wire({"POST": "readings"}, started)
        batch = _batches_done(j, person)
    with _step(j, f"{person.person}'s answer is read, and nothing failed") as h:
        h.record_assert({"status": "DONE", "failed": []}, batch)
        assert batch.get("status") == "DONE", batch
        assert not batch.get("failed"), batch


def _batches_done(j: Journey, person, *, before: set | None = None) -> dict:
    """The newest reading batch, once it -- and any started after it -- is no longer running."""
    deadline = time.monotonic() + 90 * j.patience
    while True:
        batches = j.get(j.project("/readings")) or []
        batch = batches[0] if isinstance(batches, list) and batches else {}
        fresh = batch.get("batchId") not in (before or set())
        if fresh and batch.get("status") not in (None, "RUNNING", "PENDING"):
            return batch
        if time.monotonic() > deadline:
            raise AssertionError(f"{person.person}'s reading never finished: {batch}")
        time.sleep(1)


def _read_on_arrival(j: Journey, person) -> None:
    """keel-cloud 095 FR-A, on Keel's door: the answer is read on its own; the founder presses nothing."""
    with _step(j, f"{person.person}'s answer is read on arrival (keel-cloud 095): the founder presses nothing, the "
                  "newest batch -- one the journey did not start -- and any after it end DONE, and a POST readings "
                  "of the founder's is refused 409 READING_IN_PROGRESS or NOTHING_TO_READ", party="stack") as h:
        batch = _batches_done(j, person)
        status, refused = j.call("POST", j.project("/readings"), {}, ok=(409,))
        h.record_assert({"status": "DONE", "failed": [], "POST readings": [409, "READING_IN_PROGRESS",
                                                                           "NOTHING_TO_READ"]},
                        {"batch": batch, "POST readings": [status, _refusal(refused)]})
        assert batch.get("status") == "DONE" and not batch.get("failed"), batch
        assert _refusal(refused) in ("READING_IN_PROGRESS", "NOTHING_TO_READ"), refused


def _refusal(body) -> str | None:
    """A reading's refusal names itself in `rule` (keel-cloud `ReadingRefusal`), a vector refusal in `code`."""
    body = body if isinstance(body, dict) else {}
    return body.get("code") or body.get("rule")


# ----------------------------------------------------------------------------- leg 7: standings

def expected_status(entry, key: str) -> str:
    """The entry's own status for `key`, but `LEFT_OUT` where this journey had to leave Frequency
    out (spec 039 / 041 / 042 D-1: the corpus's Frequency is on an "out of N" its own window cannot carry -- since
    revision 11 on Mulch Run alone)."""
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
        h.record_assert({"pills": want, "bands": 3, "download": True},
                        {"pills": got, "bands": len(board["bands"]), "download": board["download"],
                         "tiles": board["tile_cards"], "overall": board["overall"]})
        assert set(got) == set(VECTORS), got
        for vector, word in want.items():
            assert word in got[vector], (vector, got[vector], word)
        assert len(board["bands"]) == 3, board["bands"]
        assert board["download"], "the download is not live after every answer was read"
        headlines = [v.get("headline") for v in verdicts.values()]
        assert board["overall"] in headlines, (board["overall"], headlines)
    _board_tiles(j, board, "after every answer was read")


def people_label(n: int) -> str:
    """keel-web `statLabelPeople` (066, D15): *person asked* under a 1, *people asked* otherwise."""
    return "person asked" if n == 1 else "people asked"


def people_line(counts: dict) -> str:
    """keel-web `evidenceBarPeopleLine` (066): *1 person asked · 0 answered · 0 read by your AI*."""
    n = int(counts.get("invited") or 0)
    return f"{n} {'person' if n == 1 else 'people'} asked · {counts.get('answered')} answered · " \
           f"{counts.get('read')} read by your AI"


def _board_tiles(j: Journey, board: dict, when: str) -> None:
    """keel-web 066 (D15): the overview's two tiles -- the people asked (`.tile`, its number `people.invited`, *1 person
    asked* / *n people asked*), then the pilot sign-ups (`.tile--pilot`: *k of n · p%* over the per-link line, or
    *None yet* and no line before anyone finishes) -- and the people line under them, all the wire's own."""
    with _step(j, f"the board's two tiles, {when}: the people asked, then the pilot sign-ups, and the people line "
                  "(keel-web 066, D15)", party="founder") as h:
        counts = j.standings.get("people") or {}
        pilot = j.standings.get("pilot") or {}
        big, line = pilot_words(pilot)
        nobody = int(pilot.get("finished") or 0) == 0
        want = {"cards": [{"pilot": False, "big": str(counts.get("invited")),
                           "label": people_label(int(counts.get("invited") or 0)), "has_line": False},
                          {"pilot": True, "big": big, "label": "pilot sign-ups", "has_line": not nobody,
                           "line": line}],
                "people_line": people_line(counts)}
        cards = board["tile_cards"]
        have = {"cards": [{"pilot": "tile--pilot" in c["class"], "big": c["big"], "label": c["label"],
                           "has_line": c["has_line"], **({"line": c["line"]} if "tile--pilot" in c["class"] else {})}
                          for c in cards],
                "people_line": board["people_line"]}
        h.record_assert(want, have)
        assert have == want, json.dumps({"screen": have, "wire": want}, indent=2)


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
        assert page["keel_bars"] == 0, "a stage page draws Keel's bar (keel-web 067: page two alone)"
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
        with _step(j, "each stage's notAsked is the entry's, in keel-cloud 091's one house style (FR-F3)") as h:
            want_not = {v: expected_not_asked(j, v) for v in VECTORS}
            have_not = {v: [{k: n.get(k) for k in ("key", "name", "why")}
                            for n in (facts.get(v.lower()) or {}).get("notAsked") or []] for v in VECTORS}
            h.record_assert(want_not, have_not)
            assert have_not == want_not, json.dumps({"wire": have_not, "corpus": want_not}, indent=2)
        with _step(j, "the pilot: the entry's sign-ups over everyone who answered, per link -- on the brief "
                      "and on the overview's read") as h:
            want_pilot = brief_facts_mod.pilot_for(j.entry)
            h.record_assert(want_pilot, {"brief": facts.get("pilot"), "standings": standings.get("pilot")})
            assert facts.get("pilot") == want_pilot, (facts.get("pilot"), want_pilot)
            assert standings.get("pilot") == want_pilot, (standings.get("pilot"), want_pilot)
    with _step(j, "every served quote is credited to its link in the header's words (keel-cloud 091 FR-F2: "
                  "BriefReading.quotes[].link / words)" + (" -- the referee's reading quotes nobody" if j.strict
                                                            else "")) as h:
        quotes = list(reading.get("quotes") or [])
        faults = [q for q in quotes if q.get("link") not in brief_facts_mod.LINK_WORDS
                  or q.get("words") != brief_facts_mod.LINK_WORDS[q.get("link")]]
        h.record_assert({"faults": [], **({"quotes": []} if j.strict else {})}, {"quotes": quotes, "faults": faults})
        assert not faults, faults
        if j.strict:
            assert quotes == [], quotes
    _brief_pages(j, brief, standings)


def expected_not_asked(j: Journey, vector: str) -> list[dict]:
    """`BriefFacts.<stage>.notAsked` as `instructions/brief_facts.py` reads the entry (keel-cloud 089 FR-002, 091
    FR-F3's house style), with the dimension this journey had to leave out read as left out (D-1)."""
    out = []
    b2b = j.entry.b2b()
    for d in j.registry.slice(vector):
        if d.b2b_only and not b2b:
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.NOT_ASKED_WHY[d.key]})
        elif expected_status(j.entry, d.key) == "LEFT_OUT":
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.LEFT_OUT_LINE})
        elif d.b2b_link_only and not b2b:
            out.append({"key": d.key, "name": d.name, "why": brief_facts_mod.NOT_ASKED_WHY[d.key]})
    return out


#: Words keel-web 065 took off page one (FR-002; D3): none of them may come back.
PAGE_ONE_BANS = ("deal-breaker", "where they differ", "inferred from")


def pilot_words(pilot: dict) -> tuple[str, str]:
    """keel-web `pilotNumber` and `pilotLinkLine`: *2 of 12 · 17%* over *2 of 12 people who have it*; before anyone
    finishes *None yet* and no line (keel-web 066, D15)."""
    if int(pilot.get("finished") or 0) == 0:
        return "None yet", ""
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
        assert pilot_tile.get("has_line") is (int((facts.get("pilot") or {}).get("finished") or 0) > 0), pilot_tile
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
    rows = {d.get("dimension"): d for v in standings.get("vectors") or [] for d in v.get("dimensions") or []}
    have_bars = {b["key"]: b["keel_bar"] for stage in breakdown["stages"].values() for b in stage["blocks"]}
    have_said = {b["key"]: b["said"] for stage in breakdown["stages"].values() for b in stage["blocks"]}
    # runs/DRIFT.md #82 (resolved by keel-web da0b9eb, 2026-10-14): Keel's bar wins wherever the wire serves `keelBar`,
    # even though keel-cloud also sends `founderSaid` on those rows. The slot is held to *Keel's bar: {keelBar}* on
    # every such card; a block that draws the founder's words there instead is the defect come back (a guard).
    want_bars = {c["key"]: [f"Keel's bar: {c['keelBar']}"] if c.get("keelBar") else [] for c in cards}
    shadowed = {c["key"]: rows[c["key"]].get("founderSaid") for c in cards
                if c.get("keelBar") and (rows.get(c["key"]) or {}).get("founderSaid")}
    came_back = {k: have_said.get(k) for k, v in shadowed.items()
                 if have_said.get(k) == [v] and not have_bars.get(k)}
    if came_back:
        with _step(j, f"{j.entry.id}: DRIFT #82 came back -- page two drew the founder's words, not Keel's bar, on "
                      f"{', '.join(sorted(came_back))}", party="founder", kind="protocol") as h:
            h.record_wire({k: {"keelBar": next(c["keelBar"] for c in cards if c["key"] == k), "founderSaid": v}
                           for k, v in shadowed.items() if k in came_back}, {"bar slot drawn": came_back})
            raise AssertionError(f"DRIFT #82 came back: {sorted(came_back)}")
    with _step(j, "the brief, page two: Keel's bar where the wire sets it and nowhere else, and every quote credited "
                  "by its served words and link (keel-web 067 + da0b9eb, keel-cloud 091 FR-F1 / F2)", party="founder") as h:
        want_quotes = [{"link": q.get("link"), "words": q.get("words")} for q in reading.get("quotes") or []]
        have_quotes = breakdown["stages"]["problem"]["quotes"]
        others = [q for stage in ("solution", "commercial") for q in breakdown["stages"][stage]["quotes"]]
        h.record_assert({"bars": want_bars, "quotes": want_quotes},
                        {"bars": have_bars, "quotes": have_quotes, "elsewhere": others,
                         "bars drawn": breakdown["keel_bars"], "founderSaid beside keelBar": shadowed})
        assert have_bars == want_bars, json.dumps({"page": have_bars, "wire": want_bars}, indent=2)
        assert breakdown["keel_bars"] == sum(1 for v in want_bars.values() if v), breakdown["keel_bars"]
        assert have_quotes == want_quotes and not others, (have_quotes, want_quotes, others)
        if j.strict:
            keyed = {c["key"] for c in cards if c.get("keelBar")}
            assert keyed == {"problem.importance", "problem.current_solution_satisfaction"}, keyed
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

# --------------------------------------------------------------------------- the feedback marks

def feedback_record(j: Journey) -> dict:
    """Spec 046: the record `evals/feedback_marks.py` scores -- the lists Keel drafted (FM1) with the role words keel-cloud
    exported (`common.role_words`) and the founder's own words, Importance's drafts and saved list (FM2), and what the
    legs kept for FM3-FM6 (the base query, the idea, the AI flow, the typed fields)."""
    record = {k: v for k, v in j.feedback.items() if k not in ("lists", "importance_probe", "importance_typed")}
    lists = list(j.feedback.get("lists") or [])
    if lists:
        common = getattr(j.registry, "common", None) or {}
        record["lists"] = lists
        record["role_words"] = list(common.get("role_words") or [])
        record["founder_text"] = {
            "context": dict(j.founder.context_fields),
            "problem_seed": j.founder.problem_seed, "solution_seed": j.founder.solution_seed,
            "persona_roles": [j.founder.context_fields.get("actor")] + (
                [j.founder.decider["role"]] if j.founder.decider.get("role") else [])}
    key = "problem.importance"
    drafts = {x["draft"]: x for x in lists if x.get("dimension") == key}
    answer = next((a for v in VECTORS for a in j.founder.calibration[v] if a.dimension == key), None)
    if "first" in drafts and answer is not None and not answer.unsure:
        stored = (j.get(j.project("/plan")) or {}).get("lists") or {}
        named = [part.strip() for part in (answer.text or "").split(";") if part.strip()]
        record["importance"] = {
            "own": vs.founder_list(j.entry, key)["items"][0]["label"],
            "named": named,
            "first_draft": [i["label"] for i in drafts["first"]["items"]],
            "redraft": [i["label"] for i in (drafts.get("answer") or {}).get("items") or []],
            "saved": [i.get("label") for i in (stored.get(key) or {}).get("items") or []],
            "typed": list(j.feedback.get("importance_typed") or []),
            "probe": j.feedback.get("importance_probe")}
    return record


def score_feedback(j: Journey) -> dict:
    """The feedback marks over the journey's record, written into the bundle (`feedback.json`, `feedback-marks.json`);
    the journey fails on any owed mark unmet -- owed being every mark whose subject the record carries."""
    from pathlib import Path                                  # noqa: PLC0415
    record = feedback_record(j)
    card = feedback_marks.scorecard(record)
    run_dir = Path(j.recorder.run_dir)
    (run_dir / "feedback.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "feedback-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n", encoding="utf-8")
    require = feedback_marks.owed(record)
    with _step(j, f"feedback marks v{feedback_marks.FEEDBACK_MARKS_VERSION} (spec 046): {card['met']} of "
                  f"{card['measured']} met ({', '.join(require) or 'none'} owed; "
                  f"{', '.join(card['unmeasured']) or 'none'} unmeasured)", party="stack") as h:
        owed = {c["mark"]: c for c in card["checks"] if c["mark"] in require}
        h.record_assert({m: True for m in require}, {m: {"ok": c["ok"], "detail": c["detail"]}
                                                     for m, c in owed.items()})
        unmet = [m for m, c in owed.items() if not (c["measured"] and c["ok"])]
        assert not unmet, {m: owed[m] for m in unmet}
    return card


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
        journey.stack, journey.founder_identity = stack, founder_one
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
        score_feedback(journey)

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
