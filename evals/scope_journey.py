"""S-015: the short study-scope journey of the problem study (spec 071 FR-2; keel-cloud 133, contract 38; keel-web
109 / 110 / 111).

A project is one of four configurations since keel-cloud 133 -- the problem, the solution, the solution and the money,
the money -- chosen on *What do you want to validate?*; the golden seven and the fourteen stay the harness's ALL (FR-1).
These journeys walk the configurations the founder named first, each **short** and each on a seed **derived from
01-countly** (the corpus file read and hashed as on every journey; nothing in it edited):

* **S-015, the problem study** (`problem_entry`): Countly with `scope: PROBLEM` -- the same restaurant managers, the same
  gate, stories and part-1 picks, so the problem's four standings are Countly's own numbers and are held to them
  (`corpus_scenario.hold_standings`). The choose screen's problem card, Context, the problem chat and its four
  calibrations, *Before people see it* (the word and who asks: no pilot screen), the lock; one link a person; each
  stranger walks the gate, the story and part 1 and meets the thank-you with no pilot box; the Overview reads *Should
  you build it?*, no Pilot tab, no tiles, one card and a one-piece ship; the decision is *Build* / *Not yet* by the
  rule (Countly's problem is split on Current solution: *Not yet*).

It is scored by `evals/scope_marks.py` (SC1-SC7, `SCOPE_MARKS_VERSION` 1). Every job is answered by keel-runtime's
scripted executor from the seed's own texts (`harness/vectors_script.generate`, which reads the scope); no model runs.
"""

from __future__ import annotations

import dataclasses
import json
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
            "problem_sentence": None,
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
    derives the seed from 01-countly (`problem_entry`)."""
    if scope != "PROBLEM":
        raise ValueError(f"{slug}: the scoped journey walks the problem study (scope PROBLEM), not {scope}")
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
        cs.leg_calibrate(j, "PROBLEM")
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
