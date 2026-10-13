"""S-005, S-006 and S-007's whole body: the corpus journeys, as **vectors** journeys (spec 039).

**The entry id is the only thing that differs between the three scenario modules** (spec 010
FR-015, kept): if `01-countly` needed one special case here, `05-paidly` would need two.

What the scenario does, in the founder's own order, one function per leg so a later spec can change
one leg and leave the others alone:

1. `leg_context`   -- the project on the entry's own market; the four context fields and the entry's
                      own recall window; CONTEXT_INTERPRET; *Yes, that's it*.
2. `leg_interpret` -- the problem seed and PROBLEM_INTERPRET's card; later the solution seed,
                      SOLUTION_MECHANISM's card and the idea's three lines approved.
3. `leg_calibrate` -- one vector at a time: CALIBRATION_QUESTIONS, the founder's corpus answer per
                      dimension, the review; the persona (who decides) between solution and
                      commercial.
4. `leg_lock`      -- *Lock and write the questions*; three RESPONDENT_QUESTIONS jobs; READY.
5. `leg_invite`    -- one link per corpus person: the primary link, or on a B2B entry the
                      decision-maker's commercial link.
6. `leg_interview` -- each person in their own browser context, no founder session: the gate, the
                      story or chip, one closed answer per item, by code; the founder reads after
                      each person so the scripted readings land on the corpus's own people.
7. `leg_standings` -- `GET standings` against the entry's `expected.standings` and
                      `expected.vector_verdicts`, and the same on the rendered board and vector pages.
8. `leg_brief`     -- the brief: the scripted reading on the wire and on the printed page.

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

#: The settled and the refused ends of an interaction (keel-cloud `InteractionStatus`).
TERMINAL_BAD = {"RESULT_INVALID", "DOMAIN_REFUSED", "STATE_CONFLICT", "JOB_FAILED", "APPLY_ERROR",
                "ABANDONED"}

#: The count keys `expected.standings` may carry and the wire's own place for each
#: (`DimensionStanding.interval` / `.choice`, `n` on the row).
INTERVAL_KEYS = ("inside", "below", "above")


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
    project_id: str = ""
    tokens: dict = field(default_factory=dict)       # person -> token
    links: dict = field(default_factory=dict)        # person -> the link the founder sends
    corridor: Any = None
    answers: Any = None
    interviews: dict = field(default_factory=dict)   # person -> the interview the wire served
    screens: dict = field(default_factory=dict)      # what the answer pages drew, by page
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
                 patience: float = 1.0) -> Journey:
    """One journey on one founder page: the legs below read and write it. S-005/6/7 open it strict
    on their scripted runtime; S-012 opens it with `strict=False` on a host's live model."""
    return Journey(recorder=recorder, page=page, context=context, web_base=stack.web_base_url,
                   cloud_base=stack.cloud_base_url, entry=entry, founder=founder, people=people,
                   script=script, browser=browser, strict=strict, patience=patience,
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
    the founder typed."""
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
    with _step(j, "the context is confirmed on the wire: the four fields, the sentence, the window") as h:
        view = j.get(j.project("/context")) or {}
        fields = view.get("fields") or {}
        h.record_assert({**founder.context_fields, "recallWindow": founder.window.as_wire(),
                         "understands": drawn}, view)
        assert view.get("state") == "CONFIRMED", view
        assert view.get("understands") == drawn, (view.get("understands"), drawn)
        assert fields.get("recallWindow") == founder.window.as_wire(), fields
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
    """The solution seed, SOLUTION_MECHANISM's card and *Looks right*, which chains the SOLUTION
    calibration questions. The idea's three lines are approved on step 5 (`leg_lock`)."""
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
    with _step(j, "the idea's three lines are the ones the mechanism drafted, on the wire") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_lines(j.entry)
        h.record_assert(want if j.strict else "three lines carrying the short name", idea)
        assert all((idea.get(k) or "").strip() for k in ("what", "how", "belief")), idea
        assert (idea.get("shortName") or "") in (idea.get("what") or ""), idea
        if j.strict:
            assert {k: idea.get(k) for k in want} == want, idea
            assert idea.get("shortName") == m["short_name"], idea


# ----------------------------------------------------------------------------- leg 3: calibrate

def leg_calibrate(j: Journey, vector: str) -> None:
    """One vector, on its screens: CALIBRATION_QUESTIONS READY, one screen per dimension answered the
    way the entry answers it, the review read and confirmed. Asserted on the screens -- each belief
    line as the founder sees it before *Continue*, and the review's rows -- and on the wire: the
    slice, every answer stored, `complete`, LEFT_OUT exactly where the founder was unsure."""
    view = _wait_calibration(j, vector)
    with _step(j, f"{vector.lower()}: the calibration offers exactly the registry's slice, in order",
               party="founder") as h:
        keys = [q.get("dimension") for q in view.get("questions") or []]
        want = vs.founder_keys(j.entry, vector)
        h.record_assert(want, keys)
        assert keys == want, keys
    j.corridor.wait_questions()
    answers = {a.dimension: _offered_codes(j, a.as_wire(), view) for a in j.founder.calibration[vector]}
    beliefs = {}
    for question in view.get("questions") or []:
        seen = j.corridor.answer(question, answers[question["dimension"]])
        beliefs[question["dimension"]] = seen["belief"]
    with _step(j, f"{vector.lower()}: each screen's belief line is the entry's own sentence, where "
                  "the entry's answer is one phrase", party="founder") as h:
        mismatches = []
        for key, drawn in beliefs.items():
            founder = j.entry.founder_calibration.get(key) or {}
            # The screen composes its belief line live, joining every ticked phrase; keel-cloud's
            # sentence wins on disagreement (`answerCalibration`), and on the ladder it names the
            # highest rung alone. So a multi-tick answer is held to the server's sentence on the
            # review, and to nothing here.
            answer = founder.get("answer")
            if not j.strict or answers[key].get("unsure") or not _single_phrase(j.entry, key) or (
                    isinstance(answer, list) and len(answer) > 1):
                continue
            if drawn != founder.get("belief_sentence"):
                mismatches.append({"dimension": key, "screen": drawn,
                                   "corpus": founder.get("belief_sentence")})
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)
    drawn = j.corridor.review(j.project_id, vector)
    extra = {k: v for k, v in answers.items() if k not in beliefs}
    if extra:
        # runs/DRIFT.md #74: the one answer no screen asks for -- Frequency on a one-unit window.
        with _step(j, f"{vector.lower()}: DRIFT #74 -- the answer no screen asks ({', '.join(extra)}) "
                      "goes on the wire, so the standings can be read at all",
                   party="stack", kind="protocol") as h:
            body = {"expectedRevision": (j.get(j.project(f"/calibration/{vector}")) or {}).get("revision"),
                    "answers": list(extra.values())}
            _, saved = j.call("PUT", j.project(f"/calibration/{vector}"), body)
            h.record_wire(body, saved)
    if vector == "COMMERCIAL" and j.founder.hourly_rate is not None:
        _hourly_rate(j)
    review = j.get(j.project(f"/review/{vector}")) or {}
    with _step(j, f"{vector.lower()}: the review is complete and reads the entry's beliefs, on the "
                  "screen and on the wire", party="founder") as h:
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
            sentence = founder.get("belief_sentence")
            if j.strict and _single_phrase(j.entry, key):
                if row.get("belief") != sentence:
                    mismatches.append({"dimension": key, "wire": row.get("belief"), "corpus": sentence})
                if sentence and sentence not in drawn["text"]:
                    mismatches.append({"dimension": key, "screen": "absent", "corpus": sentence})
        h.record_assert({"complete": True, "mismatches": []},
                        {"complete": review.get("complete"), "mismatches": mismatches,
                         "rows": review.get("rows"), "foot": drawn["foot"]})
        assert review.get("complete") is True, review
        assert not mismatches, json.dumps(mismatches, indent=2)
    j.corridor.confirm_review(vector)


def _offered_codes(j: Journey, answer: dict, view: dict) -> dict:
    """The founder's answer on the codes this calibration offers. On the scripted journeys every
    corpus code is offered and that is asserted; on a live one a model-written set (Purchase
    friction) slugs its own codes, so the founder ticks the same number of options from the top."""
    codes = answer.get("codes")
    if not codes:
        return answer
    question = next((q for q in view.get("questions") or [] if q.get("dimension") == answer["dimension"]), {})
    offered = [o.get("normalized") for o in question.get("options") or []]
    if all(code in offered for code in codes):
        return answer
    assert not j.strict, f"{answer['dimension']}: the corpus codes {codes} are not offered: {offered}"
    return {**answer, "codes": offered[:len(codes)]}


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
        h.record_wire(body, {"default": rate, "set": True, "saved": saved})


def _single_phrase(entry, key: str) -> bool:
    """Whether the corpus's `belief_sentence` is one keel-cloud must reproduce from this journey's
    labels: one chosen code, the ladder's highest rung, a cost, a price or the derived ratio. A set
    ticked twice is joined by keel-cloud from per-option phrases the corpus does not record (spec
    039 D-4)."""
    founder = entry.founder_calibration.get(key) or {}
    answer = founder.get("answer")
    if key == "commercial.commitment":
        return True
    if isinstance(answer, list):
        return len(answer) == 1
    return answer is not None


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
    """Step 5: the idea in three lines approved (*This describes my idea correctly*, `POST
    idea/approve` -- the gate lock and every invitation wait on), then *Lock and write the
    questions*: three RESPONDENT_QUESTIONS jobs (part 3 the decision-maker's link's on a B2B entry),
    READY before anyone is invited."""
    drawn = j.corridor.approve_idea_and_lock()
    with _step(j, "the idea preview shows the three lines, and the wire says they were approved") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_lines(j.entry)
        h.record_assert({**want, "approved": True}, {"preview": drawn["idea_preview"], "wire": idea})
        assert idea.get("approved") is True, idea
        assert want["what"] in drawn["idea_preview"], drawn
    deadline = time.monotonic() + 120 * j.patience
    state = None
    while time.monotonic() < deadline:
        state = (j.get(j.project("/overview")) or {}).get("questionsState")
        if state in ("READY", "FAILED"):
            break
        time.sleep(0.5)
    with _step(j, "the study is version 1, and the three parts' questions are written, READY") as h:
        plan = j.get(j.project("/plan")) or {}
        h.record_assert({"locked": True, "version": 1, "questionsState": "READY"},
                        {"locked": plan.get("locked"), "version": plan.get("version"),
                         "questionsState": state, "plan.questions": plan.get("questions")})
        assert plan.get("locked") is True and plan.get("version") == 1, plan
        assert state == "READY", (state, plan.get("questions"))


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
    the real interview screens: the gate, the story or chip, one closed answer per item. The body the
    page POSTs is asserted against the corpus person's own answers, by item and by option id. The
    founder has their AI read after each person, so the scripted readings land on the corpus's own
    people in order."""
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
        with _step(j, f"{person.person}: the page sent exactly this person's answers",
                   party="participant") as h:
            sent = walked["body"] or {}
            h.record_assert(expected, sent)
            assert _normal_body(sent) == _normal_body(expected), (sent, expected)
            h.capture_text("participant_page", "\n\n".join(walked["seen"]))
        if person.pilot_opt_in and person.recency is not False:
            screens.opt_in_to_pilot(interview)
    finally:
        stranger.close()


def _on_the_offered_options(body: dict, items: dict) -> dict:
    """A live journey's answer on the options the model actually wrote: an option id the item does
    not offer (a model-slugged Importance difficulty, a Purchase friction blocker) becomes the item's
    first options, as many as the person picked. Never reached on a scripted journey."""
    by_id = {i.get("itemId"): i for i in items.values()}
    answers = []
    for answer in body.get("answers") or []:
        item = by_id.get(answer.get("itemId")) or {}
        offered = [o.get("optionId") for o in item.get("options") or [] if not o.get("somethingElse")]
        picked = answer.get("optionIds")
        if picked and not all(p in offered for p in picked):
            answer = {k: v for k, v in answer.items() if k != "somethingElse"}
            answer["optionIds"] = offered[:len(picked)]
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
    out (spec 039 D-1: the corpus's Frequency is on a 0-to-7 axis its own window cannot carry)."""
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
    the entry records -- and every vector's verdict and deciding dimension."""
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
                        if wire_counts.get(code, 0) != count:
                            row.setdefault("optionCounts", {})[code] = {
                                "wire": wire_counts.get(code), "corpus": count}
            if len(row) > 1:
                mismatches.append(row)
        h.record_assert([], mismatches)
        assert not mismatches, json.dumps(mismatches, indent=2)

    with _step(j, "every vector's verdict is its deciding deal-breaker's, as the entry says") as h:
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


def _vector_page(j: Journey, vector: str) -> None:
    """One vector page: a row per dimension, each status the entry's in keel-web's word (amber where
    left out), the vector's headline the wire's own, and on a B2B commercial page the banner naming
    the decision-maker."""
    page = j.screens[vector] = j.answers.vector_page(j.project_id, vector)
    standing = next(v for v in j.standings.get("vectors") or [] if v.get("vector") == vector)
    with _step(j, f"the {vector.lower()} page: every dimension reads the wire's status in keel-web's "
                  "word",
               party="founder") as h:
        mismatches = []
        for d in standing.get("dimensions") or []:
            key = d.get("dimension")
            row = page["rows"].get(key) or {}
            word = STATUS_WORD[d.get("status")]
            if not row.get("status", "").startswith(word):
                mismatches.append({"dimension": key, "screen": row.get("status"), "want": word})
            if d.get("status") == "LEFT_OUT" and not row.get("amber"):
                mismatches.append({"dimension": key, "screen": "not amber", "want": "amber"})
        h.record_assert({"headline": standing.get("headline"), "mismatches": []},
                        {"headline": page["headline"], "mismatches": mismatches,
                         "rows": page["rows"]})
        assert page["headline"] == standing.get("headline"), (page["headline"], standing.get("headline"))
        assert len(page["rows"]) == len(standing.get("dimensions") or []), page["rows"]
        assert not mismatches, json.dumps(mismatches, indent=2)
        if vector == "COMMERCIAL" and vs.is_b2b(j.entry):
            role = j.founder.decider["role"].lower()
            assert role in page["decider_banner"].lower(), page["decider_banner"]


# --------------------------------------------------------------------------------- leg 8: brief

def leg_brief(j: Journey, *, timeout_s: float = 60) -> None:
    """The brief over the same standings, on the wire and on the page the founder hands over. On the
    scripted journeys the reading is the referee's own and keel-cloud kept it (`fallbackUsed`
    false); on a live one it is whatever the model wrote or code's fallback, and either way the
    printed page draws the wire's headline and the wire's decision."""
    deadline = time.monotonic() + timeout_s * j.patience
    brief: dict = {}
    while time.monotonic() < deadline:
        brief = (j.get(j.project("/standings")) or {}).get("brief") or {}
        if brief.get("fallbackUsed") is False:
            break
        time.sleep(1)
    headline = ((brief.get("reading") or {}).get("headline") or {}).get("text")
    if j.strict:
        with _step(j, "the brief carries the scripted reading, not code's fallback") as h:
            want = vs.brief_result(j.entry)["headline"]["text"]
            h.record_assert({"fallbackUsed": False, "headline": want},
                            {"fallbackUsed": brief.get("fallbackUsed"), "headline": headline})
            assert brief.get("fallbackUsed") is False, brief.get("fallbackUsed")
            assert headline == want, headline
    printed = j.screens["brief"] = j.answers.brief(j.project_id)
    with _step(j, "the printed brief: the wire's headline, the wire's decision, four sections",
               party="founder") as h:
        facts = brief.get("facts") or {}
        decision = str((facts.get("decision") or {}).get("label") or "").lower()
        sections = ["brief-problem", "brief-solution", "brief-commercial", "brief-next"]
        h.record_assert({"headline": headline, "decision": decision, "sections": sections},
                        {"headline": printed["headline"], "decision": printed["decision"],
                         "sections": printed["sections"], "tiles": printed["tiles"],
                         "fallbackUsed": brief.get("fallbackUsed")})
        assert headline and printed["headline"] == headline, (printed["headline"], headline)
        assert printed["decision"] == decision, (printed["decision"], decision)
        assert printed["sections"] == sections, printed["sections"]


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
                               script=script)
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
