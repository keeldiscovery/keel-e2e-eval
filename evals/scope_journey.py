"""S-015 and S-016: the two short study-scope journeys (spec 071 FR-2 / FR-3; keel-cloud 133, contract 38; keel-web
109 / 110 / 111).

A project is one of four configurations since keel-cloud 133 -- the problem, the solution, the solution and the money,
the money -- chosen on *What do you want to validate?*; the golden seven and the fourteen stay the harness's ALL (FR-1).
These two journeys walk the two the founder named first, each **short** and each on a seed **derived from 01-countly**
(the corpus file read and hashed as on every journey; nothing in it edited):

* **S-015, the problem study** (`problem_entry`): Countly with `scope: PROBLEM` -- the same restaurant managers, the same
  gate, stories and part-1 picks, so the problem's four standings are Countly's own numbers and are held to them
  (`corpus_scenario.hold_standings`). The choose screen's problem card, Context, the problem chat and its four
  calibrations, *Before people see it* (the word and who asks: no pilot screen), the lock; one link a person; each
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

Both are scored by `evals/scope_marks.py` (SC1-SC7, `SCOPE_MARKS_VERSION` 1). Every job is answered by keel-runtime's
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
from harness import vectors_script as vs
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from instructions import contract as contract_mod
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
        want = [m["trigger"], m["mechanism"], m["output"]]
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
        assert {k: seen["lines"][k] for k in ("how", "belief")} == {k: want[k] for k in ("how", "belief")}, seen
        assert idea.get("what") == name and idea.get("approved") is True, idea
        assert (seen["frame"].get("kicker") or "").lower().startswith("step 3 of 5 · your idea"), seen["frame"]
        j.idea_name = str(idea.get("shortName") or idea.get("what") or "")


def drift_97(j: cs.Journey) -> None:
    """runs/DRIFT.md #97: keel-cloud `ScreenChain` chains CALIBRATION_QUESTIONS on the problem card's and the mechanism
    card's confirmation whatever the scope, so money alone writes a problem slice and a solution slice nobody walks (a
    model job each, and credits on Keel's door). Held on the wire as found: one CALIBRATION_QUESTIONS job per
    `vs.calibration_jobs` entry, the out-of-scope ones among them; none on the problem study (the guard for S-015)."""
    out = vs.chained_out_of_scope(j.entry)
    rows = [r for r in j.get(f"/v2/inference-interactions?project_id={j.project_id}") or []
            if r.get("screen") == "CALIBRATION_QUESTIONS"]
    title = (f"{j.entry.id} ({j.scope}): DRIFT #97 -- keel-cloud chained {len(out)} CALIBRATION_QUESTIONS job(s) for "
             f"{', '.join(out)} though the scope calibrates {', '.join(vs.scope_vectors(j.entry))} alone"
             if out else f"{j.entry.id} ({j.scope}): no CALIBRATION_QUESTIONS job outside the scope (DRIFT #97's guard)")
    with cs._step(j, title, party="stack") as h:
        h.record_assert({"jobs": len(vs.calibration_jobs(j.entry)), "out of scope": list(out)},
                        {"jobs": [(r.get("status"), r.get("created_at")) for r in rows]})
        assert len(rows) == len(vs.calibration_jobs(j.entry)), rows
        assert all(r.get("status") == "APPLIED" for r in rows), rows
    j.changed["drift_97"] = {"out_of_scope": list(out), "jobs": len(rows)}


# --------------------------------------------------------------------------------------- the scoped reading

def record_of(j: cs.Journey, overview: dict) -> dict:
    """What `scope_marks.score` reads, off the journey."""
    chose = j.changed.get("choose") or {}
    kickers = [(key, (s.get("frame") or {}).get("kicker")) for key, seen in j.framing.items()
               for s in seen if isinstance(s, dict) and s.get("frame")]
    idea_screens = {}
    for person, walked in j.walked.items():
        first = next((s for s in walked.get("screens") or [] if s.get("screen") == "idea"), None)
        if first is not None:
            idea_screens[person] = first
    statement = ((j.get(j.project("/review/PROBLEM")) or {}).get("statement"))
    return {"scope": j.scope, "b2b": vs.is_b2b(j.entry), "choose": chose,
            "created": (chose.get("create") or {}).get("sent"),
            "served_scope": (j.get(j.project("/overview")) or {}).get("scope"),
            "kickers": kickers,
            "idea_kicker": ((j.framing.get("idea") or [{}])[0].get("frame") or {}).get("kicker"),
            "counters": j.screens.get("before_counters"),
            "kinds": sorted({iv.get("kind") for iv in j.interviews.values()}),
            "links": len(set(j.tokens.values())), "people": len(j.people),
            "interviews": j.interviews,
            "pilot_boxes": {p: w.get("pilot_box") for p, w in j.walked.items()},
            "done": {p: w.get("done") for p, w in j.walked.items()},
            "idea_screens": idea_screens,
            "problem_sentence": problem_sentence(statement) if j.scope != "PROBLEM" else None,
            "standings": j.standings, "overview": overview}


def leg_scoped_report(j: cs.Journey) -> dict:
    """The standings once every link is answered -- on the problem study the entry's own numbers -- then the Overview as
    drawn, and SC1-SC7 scored (`scope-marks.json` in the bundle); every mark measured and met."""
    cs._await_standings(j)
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
    with cs._step(j, f"{j.scope}: the study-scope marks SC1-SC7 (SCOPE_MARKS_VERSION {scope_marks.SCOPE_MARKS_VERSION}) "
                     "-- every one measured and met", party="founder") as h:
        h.record_assert({m: True for m in scope_marks.MARKS}, {c["mark"]: c for c in card["checks"]})
        assert card["met"] == card["of"] == len(scope_marks.MARKS), json.dumps(card["checks"], indent=2, default=str)
    return card


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
        cs.leg_context(j)
        cs.leg_interpret_problem(j)
        if scope == "PROBLEM":
            cs.leg_calibrate(j, "PROBLEM")
        else:
            leg_idea_card(j)
            cs.leg_persona(j)
            cs.leg_calibrate(j, "COMMERCIAL")
        drift_97(j)
        cs.leg_lock(j)
        cs.leg_invite(j)
        cs.leg_interview(j)
        leg_scoped_report(j)
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
