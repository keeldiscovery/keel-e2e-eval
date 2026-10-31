"""S-015 and S-016: the two short study-scope journeys (spec 071 FR-2 / FR-3; keel-cloud 133, contract 38; keel-web
109 / 110 / 111).

A project is one of four configurations since keel-cloud 133 -- the problem, the solution, the solution and the money,
the money -- chosen on *What do you want to validate?*; the golden seven and the fourteen stay the harness's ALL (FR-1).
These two journeys walk the two the founder named first, each **short** and each on a seed **derived from 01-countly**
(the corpus file read and hashed as on every journey; nothing in it edited):

* **S-015, the problem study** (`problem_entry`): Countly with `scope: PROBLEM` -- the same restaurant managers, the same
  gate, stories and part-1 picks, so the problem's four standings are Countly's own numbers and are held to them
  (`corpus_scenario.hold_standings`). The choose screen's problem card, Context, the problem chat and its four
  calibrations, *Before people see it* (who asks alone: no pilot screen, and no word since keel-web 113), the lock; one link a person; each
  stranger walks the gate, the story and part 1 and meets the thank-you with no pilot box; the Overview reads *Should
  you build it?*, no Pilot tab, no tiles, one card and a one-piece ship; the decision is *Build* / *Not yet* by the
  rule (Countly's problem is split on Current solution: *Not yet*).
* **S-016, money alone, B2B** (`money_entry`): Countly with the owner deciding (judgement call: the restaurant owner,
  as keel-cloud 133's own walk put Countly on a B2B persona) and `scope: COMMERCIAL` -- Context with no recall window,
  the problem chat, the idea card (*Your idea*), who decides, the money calibration, the lock; **only the
  decision-maker's link** is issued, one an owner (Countly's ten who had a delivery in the window, their own money
  picks, each with an Ability-to-pay and a Purchase-friction answer the seed adds); each link opens with the problem
  in one sentence (held to the spoken-form mirror), the idea card, then part 3; the Overview reads *Will they pay?*,
  the Pilot and *What they would pay* tiles, one card, a one-piece ship.

* **S-016, money alone, consumer** (spec 100, `consumer_money_entry`; keel-cloud 166, keel-web 145): Countly on its own
  persona under `scope: COMMERCIAL` -- the person's one FULL link, no gate, the screener (`Interview.condition`) before
  the idea card; Countly's ten answer it inside, one more (`OUTSIDE_PERSON`) outside, who meets the exit and is counted
  apart (`leg_money_screener`, `corpus_scenario.hold_outside_apart`).

All three are scored by `evals/scope_marks.py` (SC1-SC8, `SCOPE_MARKS_VERSION` 3). Every job is answered by keel-runtime's
scripted executor from the seed's own texts (`harness/vectors_script.generate`, which reads the scope); no model runs.
"""

from __future__ import annotations

import dataclasses
import json
import re
import time

from evals import corpus_facts
from evals import corpus_scenario as cs
from evals import scope_marks
from evals.preludes import own_ai_door
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from instructions import contract as contract_mod
from instructions import corpus as corpus_mod
from stack import remote

SCOPED_FROM = "01-countly"

# ------------------------------------------------------------------------------------------ S-015's seed


def problem_entry(entry):
    """01-countly as a problem study: `scope: PROBLEM`, and `expected` the entry's own problem standings and verdict --
    the same people, gate, stories and part-1 picks, so the same numbers (the solution's and the money's are absent:
    keel-cloud 133 FR-7 serves no out-of-scope vector)."""
    if entry.id != SCOPED_FROM:
        raise ValueError(f"the problem study is derived from {SCOPED_FROM}, not {entry.id}")
    expected = entry.expected or {}
    standings = {k: v for k, v in (expected.get("standings") or {}).items() if k.startswith("problem.")}
    verdicts = {k: v for k, v in (expected.get("vector_verdicts") or {}).items() if k == "PROBLEM"}
    return dataclasses.replace(entry, scope="PROBLEM", expected={"standings": standings, "vector_verdicts": verdicts})


# ------------------------------------------------------------------------------------------ S-016's seed

#: The decision-maker's role (keel-cloud 133 judgement call 7: Countly walked B2B, the restaurant owner decides).
OWNER_ROLE = {"id": "owner", "label": "Restaurant owners", "roleType": "BUYER",
              "about": "the owner of an independent restaurant who chooses and pays for its tools"}
OWNER_TITLE = "Restaurant owner"
#: Purchase friction, B2B only -- the founder's list (keel-cloud 087's item list, the tested item picked first).
FRICTION = {"answer": {"items": [{"code": "pos_setup", "label": "Setting it up with the POS provider"},
                                 {"code": "partner_signoff", "label": "A business partner's sign-off"},
                                 {"code": "card_on_file", "label": "Putting a card on file"}],
                       "picked": 0},
            "belief_sentence": "Setting it up with the POS provider slows the purchase most."}
BUYER_BELIEF = "The restaurant owner decides, and nobody else has to agree."
#: The two B2B-only rows of the plan (05-paidly's own shapes).
B2B_QUESTIONS = {
    "commercial.ability_to_pay": {"part": 3, "control": "single_choice",
                                  "codes": ["existing_line", "new_line_signed_off", "taken_from_other_spend", "no_budget"],
                                  "escape": "cant_recall_one"},
    "commercial.purchase_friction": {"part": 3, "control": "fixed_three", "codes": ["yes_long", "yes_quick", "not_needed"],
                                     "escape": "cant_recall"},
}
#: Each owner's two added answers (Ability to pay, Purchase friction), in Countly's order of the ten.
OWNER_PICKS = {
    "Priya Natarajan": ("existing_line", "yes_quick"),
    "Marcus Lindqvist": ("existing_line", "yes_quick"),
    "Hana Yoshida": ("new_line_signed_off", "yes_quick"),
    "Daniel Achebe": ("existing_line", "not_needed"),
    "Sofia Reyes": ("existing_line", "yes_quick"),
    "Tom Okafor": ("no_budget", "yes_long"),
    "Aisha Rahman": ("existing_line", "not_needed"),
    "Ben Carter": ("taken_from_other_spend", "yes_quick"),
    "Lena Fischer": ("existing_line", "not_needed"),
    "Mei Chen": ("new_line_signed_off", "yes_quick"),
}
#: Revision 5's stated assumption, kept: a time-only cost is put in money at a nominal $20 an hour (B2B: an owner's
#: cost is the business's money).
NOMINAL_RATE = 20


def money_entry(entry):
    """01-countly as money alone on a B2B persona: the owner decides (`OWNER_ROLE`), `scope: COMMERCIAL`; the founder's
    money calibration Countly's own plus Purchase friction (`FRICTION`, B2B only) and Buyer and payer's belief in the
    owner's words; the people the ten owners who had a delivery in the window, each on the decision-maker's link with
    Countly's money picks (a time-only cost put at `NOMINAL_RATE`) and two added answers (`OWNER_PICKS`). `expected` is
    empty: the verdict is held by keel-cloud 133 FR-7's rule over the served standings (`scope_marks.sc6`)."""
    if entry.id != SCOPED_FROM:
        raise ValueError(f"money alone is derived from {SCOPED_FROM}, not {entry.id}")
    calibration = dict(entry.founder_calibration)
    calibration["commercial.purchase_friction"] = FRICTION
    calibration["commercial.buyer_payer_alignment"] = dict(calibration["commercial.buyer_payer_alignment"],
                                                           belief_sentence=BUYER_BELIEF)
    questions = dict(entry.respondent_questions)
    questions.update(B2B_QUESTIONS)
    answers = []
    for raw in entry.answers:
        if raw.get("recency") != "yes":
            continue
        picks = {k: v for k, v in (raw.get("picks") or {}).items() if k.startswith("commercial.")}
        cost = picks.get("commercial.existing_sacrifice") or {}
        if cost.get("mode") == "HOURS":
            picks["commercial.existing_sacrifice"] = {"mode": "AMOUNT", "value": cost["value"] * NOMINAL_RATE,
                                                      "currency": cost.get("currency", "USD"), "period": cost["period"]}
        ability, friction = OWNER_PICKS[raw["person"]]
        picks["commercial.ability_to_pay"] = ability
        picks["commercial.purchase_friction"] = friction
        answers.append({"person": raw["person"], "link": vs.LINK_B2B, "recency": None, "story": None, "chip": None,
                        "anchoring": "ANCHORED", "picks": picks, "pilot_opt_in": bool(raw.get("pilot_opt_in"))})
    if len(answers) != len(OWNER_PICKS):
        raise ValueError(f"money alone walks {len(OWNER_PICKS)} owners, built {len(answers)}")
    return dataclasses.replace(entry, scope="COMMERCIAL", roles=list(entry.roles) + [OWNER_ROLE],
                               persona={"decision_maker": {"role": OWNER_ROLE["id"], "title": OWNER_TITLE}},
                               founder_calibration=calibration, respondent_questions=questions, answers=answers,
                               expected={"standings": {}, "vector_verdicts": {}})


# --------------------------------------------------------------------- S-016's consumer seed (spec 100)

#: Spec 100 FR-1: the one person who answers the money link's screener outside -- no corpus person (Countly's ten are
#: inside by the corpus's own account), sent a link with them and walked last, so no money line moves but
#: `outsideSegment`. A name on the link alone: nothing they say reaches a reading.
OUTSIDE_PERSON = "Ilse Brandvold"


def consumer_money_entry(entry):
    """Spec 100 FR-1 (keel-cloud 166, keel-web 145): 01-countly as money alone on its own consumer persona -- the
    restaurant manager decides and pays (`SAME_PERSON`, as the file records), `scope: COMMERCIAL`, so every person is on
    the one FULL link, which serves no gate: `Interview.condition` (*Do you run one or two sites?*, the context's own
    condition, `vs.money_condition`) before the idea card, then the six money questions. The people: Countly's ten who
    had a delivery in the window, inside, each on their own money picks (a gate No has none to give off the gate, spec
    102 FR-2), and `OUTSIDE_PERSON`, who answers the screener NO and meets the exit. The founder's money calibration
    is Countly's own. `expected` is empty: the verdict is held by keel-cloud 133 FR-7's rule (`scope_marks.sc6`)."""
    if entry.id != SCOPED_FROM:
        raise ValueError(f"money alone on the consumer link is derived from {SCOPED_FROM}, not {entry.id}")
    if vs.is_b2b(entry):
        raise ValueError(f"{entry.id} is walked B2B; the consumer money link is the person's own (keel-cloud 166)")
    answers = []
    for raw in entry.answers:
        if raw.get("recency") != "yes" or raw.get("link", vs.LINK_PRIMARY) != vs.LINK_PRIMARY:
            continue
        picks = {k: v for k, v in (raw.get("picks") or {}).items() if k.startswith("commercial.")}
        answers.append(dict(raw, picks=picks, condition="YES"))
    answers.append({"person": OUTSIDE_PERSON, "recency": None, "story": None, "chip": None, "anchoring": None,
                    "picks": {}, "pilot_opt_in": False, "condition": "NO"})
    scoped = dataclasses.replace(entry, scope="COMMERCIAL", answers=answers,
                                 expected={"standings": {}, "vector_verdicts": {}})
    if vs.money_condition(scoped) is None:
        raise ValueError(f"{entry.id}'s context carries no condition the money link can ask (vs.money_condition)")
    return scoped


def money_link_faults(interviews: dict, walked: dict, want: dict | None) -> list:
    """Spec 100 FR-1 (keel-cloud 166 FR-1, keel-web 145 FR-1): on the consumer money link every person's served
    interview is kind FULL with no gate, the reveal at `afterPart` 0 and `condition` as the mirror asks it (`want`,
    `vs.money_condition`), so the link opens `["condition", "reveal"]` (`vs_screens.first_screens`); a person inside
    walks the screener then the reveal and posts their answers alone (spec 102); the person outside walks the screener
    alone, posts `{outsideSegment: true, answers: []}` (201) and meets the exit (*That's it.*), no pilot box."""
    faults: list = []
    for person, iv in interviews.items():
        if iv.get("kind") != "FULL" or iv.get("gate") is not None:
            faults.append({person: "not a FULL link without a gate", "kind": iv.get("kind"), "gate": iv.get("gate")})
        if (iv.get("reveal") or {}).get("afterPart") != 0:
            faults.append({person: "the reveal does not open the link", "reveal": iv.get("reveal")})
        if (iv.get("condition") or None) != want:
            faults.append({person: "condition", "served": iv.get("condition"), "want": want})
        opening = vs_screens.first_screens(iv)
        if opening != (["condition", "reveal"] if want else ["reveal"]):
            faults.append({person: "first screens", "served": opening})
        if person not in walked:
            continue                         # not walked (spec 102 FR-2 / FR-4): already named in its own finding
        w = walked[person] or {}
        drawn = [x.get("screen") for x in w.get("screens") or []]
        body = w.get("body") or {}
        if body.get("outsideSegment") is True:
            if body != {"outsideSegment": True, "answers": []} or w.get("status") != 201:
                faults.append({person: "the outside body", "body": body, "status": w.get("status")})
            if drawn != ["condition"]:
                faults.append({person: "outside: the screener alone", "drawn": drawn})
            if (w.get("done") or "").strip() != cs.EXIT_TITLE or w.get("done_screen") is not False or w.get("pilot_box"):
                faults.append({person: "outside: the exit", "done": w.get("done"), "pilot_box": w.get("pilot_box")})
        else:
            opens = ["condition", "reveal"] if want else ["reveal"]
            if drawn[:len(opens)] != opens:
                faults.append({person: "inside: the screener, then the reveal", "drawn": drawn[:3]})
            if set(body) - {"answers", "followUps", "pilotOptIn"} or "answers" not in body:
                faults.append({person: "inside: the answers alone (spec 102)", "keys": sorted(body)})
    return faults


def leg_money_screener(j: cs.Journey) -> None:
    """Spec 100 FR-1: the consumer money link's screener held over every person walked (`money_link_faults`), the person
    outside among them. Strict on S-016; a back-test's finding."""
    want = vs.money_condition(j.entry)
    faults = money_link_faults(j.interviews, j.walked, want)
    outside = cs.outside_people(j.walked)
    with cs._step(j, f"{j.entry.id} (COMMERCIAL, consumer): the person's link is FULL with no gate and asks the screener "
                     f"'{(want or {}).get('question')}' before the idea; {len(outside)} outside met the exit with "
                     "outsideSegment alone (keel-cloud 166, keel-web 145)", party="participant",
                  kind="assert" if j.strict else "note") as h:
        h.record_assert({"condition": want, "first screens": ["condition", "reveal"] if want else ["reveal"],
                         "outside": {"body": {"outsideSegment": True, "answers": []}, "status": 201,
                                     "screens": ["condition"]}, "faults": []},
                        {"outside": outside, "faults": faults,
                         "served": {p: {k: iv.get(k) for k in ("kind", "gate", "condition")}
                                    for p, iv in j.interviews.items()}})
        if j.strict:
            assert outside == [OUTSIDE_PERSON], outside
            assert not faults, json.dumps(faults, indent=2, default=str)
    if faults and not j.strict:
        j.findings.append({"what": "the money link's screener (spec 100)", "faults": faults})


# ------------------------------------------------------------------------------- the problem in one sentence

_CUT = re.compile(r"\s*(?:[.;:]\s|\s[-–—]\s)")


def problem_sentence(statement: str | None) -> str | None:
    """keel-cloud 133 `ProblemSentence`, mirrored: the problem card's statement cut to its first sentence (a full stop,
    semicolon, colon or spaced dash), its parenthesis and its provenance (*, based on ...*) dropped, then to the last
    clause boundary under 20 words; under six words, none."""
    text = " ".join(str(statement or "").split())
    if not text:
        return None
    text = _CUT.split(text + " ", maxsplit=1)[0].strip().rstrip(".;:")
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.split(r",\s+based on\b", text)[0].strip()
    words = text.split()
    if len(words) > 20:
        cut = " ".join(words[:20])
        text = cut.rsplit(",", 1)[0] if "," in cut else cut
    if len(text.split()) < 6:
        return None
    return text.rstrip(",") + "."


# ----------------------------------------------------------------------------------- money alone's idea card

def leg_idea_card(j: cs.Journey) -> None:
    """Money alone's step 3, *Your idea* (keel-web 109 FR-3, keel-cloud 133 FR-3): the solution's seed chat and its
    card -- no solution calibration -- then the idea card named and saved (Save approves it), and on to who decides."""
    card = j.corridor.seed(j.project_id, "SOLUTION", j.founder.solution_seed)
    m = j.entry.solution_mechanism
    with cs._step(j, "money alone: the mechanism card draws the entry's own trigger, mechanism and output",
                  party="founder") as h:
        want = [m["trigger"], m["mechanism"], m["output"]] if j.strict else []
        missing = [part for part in want if part not in card["text"]]
        h.record_assert(want, card)
        assert not missing, missing
    j.corridor.confirm_seed("SOLUTION", j.scope)
    typed = j.founder.idea_name
    seen = j.corridor.idea_check(typed, next_url=r"/define/persona")
    j.framing["idea"] = [seen]
    with cs._step(j, "money alone: the idea card is *Your idea*, step 3 of 5, its how and belief the mechanism's, the "
                     "name the founder typed, approved on Save, and Save goes on to who decides", party="founder") as h:
        idea = j.get(j.project("/idea")) or {}
        want = vs.idea_view(j.entry)
        name = vs.idea_name_of(typed)
        h.record_assert({"how": want["how"], "belief": want["belief"], "what": name, "approved": True,
                         "kicker": "Step 3 of 5 · Your idea"}, {"screen": seen, "wire": idea})
        assert {k: idea.get(k) for k in ("how", "belief")} == {k: seen["lines"][k] for k in ("how", "belief")}, idea
        if j.strict:
            assert {k: seen["lines"][k] for k in ("how", "belief")} == {k: want[k] for k in ("how", "belief")}, seen
        assert idea.get("what") == name and idea.get("approved") is True, idea
        assert (seen["frame"].get("kicker") or "").lower().startswith("step 3 of 5 · your idea"), seen["frame"]
        j.idea_name = str(idea.get("shortName") or idea.get("what") or "")


def drift_97(j: cs.Journey) -> None:
    """Spec 072 FR-3: runs/DRIFT.md #97 closed (keel-cloud 134 FR-2) -- `ScreenChain` chains a vector's
    CALIBRATION_QUESTIONS only where the scope holds it. Held on the wire: the CALIBRATION_QUESTIONS jobs are the
    script's, one slice a vector in scope (and its redrafts), every one APPLIED, and none for a vector outside it."""
    in_scope = list(vs.scope_vectors(j.entry))
    rows = [r for r in j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
            if r.get("screen") == "CALIBRATION_QUESTIONS"]
    want = {v: sum(1 for w, _ in vs.calibration_jobs(j.entry) if w == v) for v in in_scope}
    have: dict = {}
    for r in rows:
        have[r.get("vector")] = have.get(r.get("vector"), 0) + 1
    title = (f"{j.entry.id} ({j.scope}): CALIBRATION_QUESTIONS for {', '.join(in_scope)} alone -- one slice a vector in "
             "scope and its redrafts, none for another (DRIFT #97 closed by keel-cloud 134)")
    with cs._step(j, title, party="stack") as h:
        h.record_assert({"jobs by vector": want, "status": "APPLIED"},
                        {"jobs": [(r.get("vector"), r.get("status"), r.get("created_at")) for r in rows]})
        outside = sorted({str(v) for v in have if v not in in_scope})
        assert not outside, (f"CALIBRATION_QUESTIONS chained for {outside} outside the scope -- DRIFT #97 came back",
                             rows)
        assert all(want[v] >= 1 for v in in_scope), want                  # one slice a vector in scope, at least
        assert have == want, {"wire": have, "script": want}
        assert all(r.get("status") == "APPLIED" for r in rows), rows
    j.changed["drift_97"] = {"out_of_scope": [], "jobs": len(rows), "by_vector": have}


# --------------------------------------------------------------------------------------- the scoped reading

def record_of(j: cs.Journey, overview: dict) -> dict:
    """What `scope_marks.score` reads, off the journey."""
    chose = j.changed.get("choose") or {}
    kickers = [(key, (s.get("frame") or {}).get("kicker")) for key, seen in j.framing.items()
               for s in seen if isinstance(s, dict) and s.get("frame")]
    idea_screens = {}
    for person, walked in j.walked.items():
        # spec 100: the decision-maker's idea screen, or the reveal that opens the money study's person link
        first = next((s for s in walked.get("screens") or [] if s.get("screen") in ("idea", "reveal")), None)
        if first is not None:
            idea_screens[person] = first
    statement = ((j.get(j.project("/review/PROBLEM")) or {}).get("statement"))
    # spec 107 (keel-cloud 175): the founder's own texts, which the problem's sentence may keep (SC4)
    audience = (j.get(j.project("/idea")) or {}).get("audienceWords") or () if j.scope != "PROBLEM" else ()
    return {"scope": j.scope, "b2b": vs.is_b2b(j.entry), "choose": chose,
            "created": (chose.get("create") or {}).get("sent"),
            "served_scope": (j.get(j.project("/overview")) or {}).get("scope"),
            "kickers": kickers,
            "idea_kicker": ((j.framing.get("idea") or [{}])[0].get("frame") or {}).get("kicker"),
            "counters": j.changed.get("before_counters"),
            "kinds": sorted({iv.get("kind") for iv in j.interviews.values()}),
            "links": len(set(j.tokens.values())), "people": len(j.people),
            "interviews": j.interviews,
            "pilot_boxes": {p: w.get("pilot_box") for p, w in j.walked.items()},
            "done": {p: w.get("done") for p, w in j.walked.items()},
            "idea_screens": idea_screens,
            # spec 100 (SC8): what each link drew, who answered a screener outside, the money link's mirror
            "screens": {p: [s.get("screen") for s in w.get("screens") or []] for p, w in j.walked.items()},
            "outside": cs.outside_people(j.walked),
            "money_condition": vs.money_condition(j.entry),
            "problem_sentence": problem_sentence(statement) if j.scope != "PROBLEM" else None,
            "founder_texts": list(corpus_mod.founder_texts(j.entry, audience)),
            "standings": j.standings, "overview": overview}


def leg_scoped_report(j: cs.Journey) -> dict:
    """The standings once every link is answered -- on the problem study the entry's own numbers -- then the Overview as
    drawn, and SC1-SC8 scored (`scope-marks.json` in the bundle); every mark measured and met. Spec 100: anyone who
    answered a screener outside is held counted apart first (`corpus_scenario.hold_outside_apart`)."""
    cs._await_standings(j)
    cs.hold_outside_apart(j)                 # spec 100: anyone who answered a screener outside, counted apart
    if j.scope == "PROBLEM":
        cs.hold_standings(j)
    with cs._step(j, f"{j.scope}: every in-scope dimension is called on the wire, with n and a status keel-cloud "
                     "names", party="stack") as h:
        dims = [d for v in j.standings.get("vectors") or [] for d in v.get("dimensions") or []]
        h.record_assert({"vectors": list(vs.scope_vectors(j.entry))},
                        {d.get("dimension"): {k: d.get(k) for k in ("status", "drift", "n")} for d in dims})
        assert dims and all(d.get("status") in cs.STATUS_WORD for d in dims), dims
    overview = j.screens["scoped-overview"] = j.answers.scoped_overview(j.project_id)
    record = record_of(j, overview)
    (j.recorder.run_dir / "scope-record.json").write_text(json.dumps(record, indent=2, default=str) + "\n",
                                                          encoding="utf-8")
    card = scope_marks.score(record)
    (j.recorder.run_dir / "scope-marks.json").write_text(json.dumps(card, indent=2, default=str) + "\n",
                                                         encoding="utf-8")
    if not j.strict:
        # spec 071 FR-4: a back-test walked under a scope -- every mark not met is a finding for the judge, never a stop
        j.findings.extend({"what": f"{c['mark']} not met on the {j.scope} study", "faults": c["faults"]}
                          for c in card["checks"] if not c["ok"])
        return card
    with cs._step(j, f"{j.scope}: the study-scope marks SC1-SC8 (SCOPE_MARKS_VERSION {scope_marks.SCOPE_MARKS_VERSION}) "
                     "-- every one measured and met", party="founder") as h:
        h.record_assert({m: True for m in scope_marks.MARKS}, {c["mark"]: c for c in card["checks"]})
        assert card["met"] == card["of"] == len(scope_marks.MARKS), json.dumps(card["checks"], indent=2, default=str)
    return card


def walk(j: cs.Journey, *, lap=None) -> dict:
    """A study of one scope from the context step to the scored Overview (the project already created on the choose
    screen with `j.scope`): the problem chat in every scope; the problem's calibrations where the problem is in scope;
    the solution's seed, idea card and calibrations where the solution is, the idea card alone on money alone; who
    decides and the money's calibrations where the money is; the lock, the links, the interviews, the scoped reading.
    S-015 / S-016 walk it strict; a back-test under `--scope` (spec 071 FR-4) walks it with `strict=False`."""
    lap = lap or (lambda _name: None)
    vectors = vs.scope_vectors(j.entry)
    cs.leg_context(j)
    lap("leg_context")
    cs.leg_interpret_problem(j)
    lap("leg_interpret_problem")
    if "PROBLEM" in vectors:
        cs.leg_calibrate(j, "PROBLEM")
        lap("leg_calibrate PROBLEM")
    if "SOLUTION" in vectors:
        cs.leg_interpret_solution(j)
        cs.leg_calibrate(j, "SOLUTION")
        lap("leg_calibrate SOLUTION")
    elif "COMMERCIAL" in vectors:
        leg_idea_card(j)
        lap("leg_idea_card")
    if "COMMERCIAL" in vectors:
        cs.leg_persona(j)
        cs.leg_calibrate(j, "COMMERCIAL")
        lap("leg_calibrate COMMERCIAL")
    drift_97(j)
    cs.leg_lock(j)
    lap("leg_lock")
    cs.leg_invite(j)
    lap("leg_invite")
    if j.scope == "COMMERCIAL" and vs.is_b2b(j.entry):
        one_kind(j)
    cs.leg_interview(j)
    lap("leg_interview")
    if j.scope == "COMMERCIAL" and not vs.is_b2b(j.entry):
        leg_money_screener(j)                # spec 100: the consumer money link's screener
    card = leg_scoped_report(j)
    lap("leg_scoped_report")
    return card


# ------------------------------------------------------------------------------- keel-cloud 139: one kind

def one_kind(j: cs.Journey) -> None:
    """Spec 075 FR-2 (keel-cloud 139): a B2B money-only study gives a link to the decision-maker alone, so Sent draws one
    kind card -- theirs -- the register's `kinds[]` is that one, and so are the kinds the contacts picker draws (`GET
    contacts/datasets`; on an account on its own AI the read may be refused for credits, and the page then draws no
    tabs at all)."""
    from harness import interviews_screens as iv_screens                # noqa: PLC0415

    sent = iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
    sent.land(j.project_id)
    cards = sent.kinds()
    register = j.get(j.project("/invitations")) or {}
    status, datasets = j.call("GET", j.project("/contacts/datasets"), ok=(200, 422))
    contacts = iv_screens.Contacts(j.page, j.recorder, j.web_base, patience=j.patience)
    drawn = contacts.open(j.project_id)
    with cs._step(j, "S-016 (keel-cloud 139): money alone on a B2B study -- Sent draws one kind card, the "
                     "decision-maker's; the register's kinds and the contacts picker's are that one kind",
                  party="founder") as h:
        kinds = [k.get("respondentType") for k in register.get("kinds") or []]
        picker = [k.get("respondentType") for k in (datasets or {}).get("kinds") or []] if status == 200 else None
        decider = next((k.get("label") for k in register.get("kinds") or [] if k.get("respondentType") == vs.LINK_B2B),
                       None)
        h.record_assert({"cards": [decider], "kinds": [vs.LINK_B2B], "picker": [vs.LINK_B2B] if status == 200 else
                         "refused (own AI)", "tabs": "at most one"},
                        {"cards": cards, "kinds": kinds, "datasets": {"status": status, "body": datasets},
                         "contacts": drawn})
        assert [c.get("label") for c in cards] == [decider], cards
        assert kinds == [vs.LINK_B2B], kinds
        if picker is not None:
            assert picker == [vs.LINK_B2B], picker
        assert len((drawn or {}).get("tabs") or []) <= 1, drawn
    sent.land(j.project_id)


# ------------------------------------------------------------------------------------------------ the run

def run(stack, founder_one, browser, run_dir, *, scope: str, entry_from, slug: str) -> None:
    """One scoped journey, start to the Overview. `scope` is the one the choose screen is answered with; `entry_from`
    derives the seed from 01-countly (`problem_entry`, `money_entry`)."""
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    cell_label = f"{remote.cell_name()} · scope {slug} · {time.strftime('%Y-%m-%d', time.gmtime())}"
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    corpus, entry = vs.entry_for(stack.keel_cloud, SCOPED_FROM)
    entry = entry_from(entry)
    if entry.scope != scope:
        raise ValueError(f"{slug}: the seed's scope is {entry.scope}, the journey's {scope}")
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
        if getattr(stack, "is_remote", False):
            page.set_default_navigation_timeout(90_000)
        j = cs.open_journey(recorder, page, context, browser, stack, entry, founder, people, script=script,
                            registry=exported.registry)
        j.scope = scope
        j.stack, j.founder_identity = stack, founder_one
        user_code = cs._connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path)
        own_ai_door(page, recorder, stack, j.get, through_the_code_story=bool(user_code))
        cs.leg_project(j)
        cs.hold_the_welcome_clip(j)             # spec 073 FR-4: the welcome per scope (keel-web 114)
        walk(j)
        if j.deferred:
            with recorder.step(f"spec 064: {len(j.deferred)} golden reading(s) the build moved", party="stack",
                               kind="assert") as h:
                h.record_assert([], j.deferred)
                raise AssertionError(json.dumps(j.deferred, indent=2, default=str)[:20000])
        with recorder.step("the corpus hashes exactly as it did when the run began", party="stack",
                           kind="assert") as h:
            corpus.verify_unchanged()
            h.record_assert(hashes_before, dict(corpus.hashes))
        passed = True
    finally:
        context.close()
        finalize_run(run_dir, slug=slug, facts=corpus_facts.vectors_facts_for(entry), passed=passed,
                     failed_step=recorder.failed_step, duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")
