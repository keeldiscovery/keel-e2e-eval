"""Judgement call 41 (the founder's decision 35, 2026-10-08): the structural marks read the
ACCEPTED answer -- after the runtime's rule refusal and one redraw -- and `rule_refusal_rate`
counts every refusal.

Stackless and modelless: a fake host answers from a list, a fake aggregate refuses from a table.
What is guarded is the redraw's payload (keel-cloud 058's `InferenceOrchestrator` repair turn,
mirrored), which answer the scorer reads, how the bundle records both, and how the rate counts.
"""

from __future__ import annotations

import json
import types

import pytest

from instructions import marks as marks_mod
from instructions import prompts as prompts_mod
from instructions import report as report_mod
from instructions import rescore as rescore_mod
from instructions import run as run_mod
from instructions import runner as runner_mod
from instructions import validate as validate_mod
from tests import v9_fixtures as fx


class _ExecutorModule:
    class ExecutorUnavailable(Exception):
        pass

    class ExecutorTimeout(Exception):
        pass

    class ExecutorAuthFailure(Exception):
        pass

    class InvalidResponse(Exception):
        pass

    @staticmethod
    def InferenceRequest(**kw):                       # noqa: N802 - mirrors the real dataclass
        return types.SimpleNamespace(**kw)


class _Validator:
    class InvalidResponse(Exception):
        pass

    @staticmethod
    def validate_response(response, contract):
        return None


class _Host:
    """Answers each call with the next result, and keeps every request it was sent."""

    def __init__(self, *results):
        self.results = list(results)
        self.requests = []
        self.last_envelope = None

    def execute(self, request):
        self.requests.append(request)
        self.last_envelope = {"num_turns": 1, "total_cost_usd": 0.05}
        return {"outcome": "COMPLETED", "result": self.results.pop(0)}


R3 = {"kind": "rule", "rule": "R3", "path": "items[0].options",
      "message": "R3: a set shows every founder label"}
R5_DOMAIN = {"kind": "rule", "rule": "R5", "path": None,
             "message": "R5: the reveal names the mechanism — Fix: describe the problem only"}


class _Aggregate:
    """Refuses any result whose `bad` is set, with `refusal`; accepts the rest. Records calls."""

    def __init__(self, refusal=R3):
        self.refusal = refusal
        self.calls = []

    def __call__(self, case, result, *, redraw=False):
        self.calls.append((case.case_id, redraw))
        case_id = validate_mod.redraw_id(case.case_id) if redraw else case.case_id
        if (result or {}).get("bad"):
            return {"case_id": case_id, "accepted": False, "refusal": dict(self.refusal)}
        return {"case_id": case_id, "accepted": True, "refusal": None}


@pytest.fixture()
def cases(tmp_path):
    return {c.case_id: c for c in prompts_mod.build_cases(
        fx.entry(), fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime, n_runs=1)}


RESPONDENT = "09-fixture/RESPONDENT_PART1/run1"
CONTEXT = "09-fixture/CONTEXT_INTERPRET/run1"


def _ask(case, host, aggregate):
    return runner_mod.ask_with_redraw(_ExecutorModule, _Validator, host, case, aggregate,
                                      render=lambda payload: "REDRAW PROMPT")


def test_a_host_refused_once_is_redrawn_once_with_the_clouds_repair_and_no_previous_answer(cases):
    case = cases[RESPONDENT]
    raw, redrawn = {"bad": True, "items": ["the first draft"]}, {"items": ["the redraw"]}
    host, aggregate = _Host(raw, redrawn), _Aggregate()
    answer = _ask(case, host, aggregate)

    assert len(host.requests) == 2, "one rule refusal, one more host call"
    first, second = host.requests
    assert (first.turn_number, second.turn_number) == (1, 2)
    assert second.interaction_id == first.interaction_id, "the same interaction, the next turn"
    sent = second.request_payload
    # queueAnotherQuestionsTurn: turn one's context plus `repair`, empty history and input,
    # the same instruction and contract. An InvalidResult (a path) is RecoverySection's sentence.
    assert sent["context"] == {**case.payload["context"], "repair": (
        "NOT DERIVED -- your previous answer was accepted as a shape and then could not be "
        "resolved: items[0].options: R3: a set shows every founder label. Answer again with "
        "everything you already had; fix only that; change nothing else.")}
    assert sent["interaction_history"] == [] and sent["input"] == {"content": ""}
    assert sent["instruction"] == case.payload["instruction"]
    assert sent["response_contract"] == case.payload["response_contract"]
    assert list(sent) == list(case.payload), "the payload's keys, in the cloud's order"
    assert "the first draft" not in json.dumps(sent), "the previous answer is never sent back"

    assert aggregate.calls == [(RESPONDENT, False), (RESPONDENT, True)]
    assert answer.result is raw and answer.redraw.result is redrawn
    assert answer.accepted is answer.redraw and answer.scored.result is redrawn
    assert [r["draft"] for r in answer.refusals] == [1] and answer.refusals[0]["rule"] == "R3"
    assert answer.redraw_prompt == "REDRAW PROMPT"


def test_a_host_refused_twice_stays_refused_and_scores_the_raw_answer(cases):
    case = cases[RESPONDENT]
    raw, redrawn = {"bad": True, "n": 1}, {"bad": True, "n": 2}
    host = _Host(raw, redrawn)
    answer = _ask(case, host, _Aggregate())
    assert len(host.requests) == 2, "the second refusal is terminal: no third call"
    assert answer.accepted is None and answer.scored is answer and answer.scored.result is raw
    assert [(r["draft"], r["rule"]) for r in answer.refusals] == [(1, "R3"), (2, "R3")]


def test_a_domain_refusal_is_repaired_in_the_rules_own_words(cases):
    host = _Host({"bad": True}, {"ok": True})
    _ask(cases[RESPONDENT], host, _Aggregate(R5_DOMAIN))
    assert host.requests[1].request_payload["context"]["repair"] == (
        "REFUSED by rule R5 -- the reveal names the mechanism. describe the problem only "
        "Answer again with everything you already had; change only that.")


def test_a_draft_screen_is_repaired_with_turn_ones_history_and_still_no_answer(cases):
    case = cases[CONTEXT]
    x1 = {"kind": "rule", "rule": "X1", "path": "understands", "message": "X1: names a product"}
    host = _Host({"bad": True, "understands": "an app"}, {"understands": "commuters"})
    answer = _ask(case, host, _Aggregate(x1))
    sent = host.requests[1].request_payload
    # refuseOrRepairDraft: "REFUSED by rule " + path + ": " + why, and buildHistory's turn one.
    assert sent["context"]["repair"] == ("REFUSED by rule understands: X1: names a product. "
                                         "Answer again with everything you already had; change "
                                         "only that.")
    assert sent["interaction_history"] == [{"turn_number": 1, "input": case.payload["input"],
                                            "outcome": "COMPLETED", "questions": None}]
    assert "an app" not in json.dumps(sent)
    assert answer.scored.result == {"understands": "commuters"}


def test_shape_refusals_and_interpret_which_the_cloud_never_redraws_get_no_second_call(cases):
    shape = {"kind": "shape", "rule": None, "path": "items", "message": "missing"}
    host = _Host({"bad": True})
    answer = _ask(cases[RESPONDENT], host, _Aggregate(shape))
    assert len(host.requests) == 1 and answer.redraw is None
    assert answer.scored is answer, "a shape refusal stays on the raw answer"

    for case_id in ("09-fixture/INTERPRET/Ann Abbott/run1",):
        host, aggregate = _Host({"bad": True}), _Aggregate()
        answer = _ask(cases[case_id], host, aggregate)
        assert len(host.requests) == 1 and aggregate.calls == [], \
            "judged at the end of the run, as before call 41"
        assert answer.verdicts == []


def test_an_unaskable_aggregate_redraws_nothing(cases):
    host = _Host({"bad": True})
    answer = _ask(cases[RESPONDENT], host, lambda case, result, redraw=False: None)
    assert len(host.requests) == 1 and answer.verdicts == [] and answer.scored is answer


def _broken(result):
    """The gate's clause breaks E1 (a time word) and an item's key is foreign -- the two things a respondent
    answer can get wrong since keel-cloud 088 (call 83)."""
    broken = json.loads(json.dumps(result))
    broken["items"][0]["event"] = "lost your keys last week"
    broken["items"][1]["key"] = "not.a.key"
    return broken


def _gates(entry) -> int:
    """Call 83: the respondent's validity is the gate's clause, one a Part 1 job."""
    return sum(1 for k in entry.plan()[1] if k == "problem.prevalence")


def test_the_scorer_reads_the_accepted_answer_and_the_raw_one_after_a_second_refusal(cases):
    entry = fx.entry()
    good = fx.respondent_result(entry, 1)
    bad = {**_broken(good), "bad": True}

    def scored(*results):
        state = run_mod._RunState()
        answer = _ask(cases[RESPONDENT], _Host(*results), _Aggregate())
        run_mod._score(cases[RESPONDENT], entry, answer.scored, None, state, fx.FakeJudge())
        return state.respondent[0]

    accepted = scored(bad, good)
    raw = scored(bad, {**good, "bad": True})
    assert accepted.validity_hit == accepted.validity_of == _gates(entry) == 1
    assert accepted.coverage_passed
    assert raw.validity_hit < _gates(entry) and not raw.coverage_passed, \
        "refused twice: the raw answer's faults are the score"


def test_the_rate_counts_every_refusal_over_the_first_drafts():
    report = [
        {"case_id": "a", "accepted": True, "refusal": None},
        {"case_id": "b", "accepted": False, "refusal": R3},
        {"case_id": "b#redraw", "accepted": True, "refusal": None},
        {"case_id": "c", "accepted": False, "refusal": R3},
        {"case_id": "c#redraw", "accepted": False, "refusal": R3},
        {"case_id": "d", "accepted": True, "refusal": None},
    ]
    folded = validate_mod.fold_in(report)
    assert folded["refusals_by_rule"] == {"R3": 3}, "b's one, c's two"
    assert folded["shown"] == 4, "the denominator is the four first drafts"
    assert folded["accepted"] == 2, "an accepted redraw is not a second acceptance"
    assert (folded["redraws"], folded["redraws_accepted"], folded["second_refusals"]) == (2, 1, 1)
    judged = marks_mod.judge({"refusals_by_rule": folded["refusals_by_rule"],
                              "refusals_shown": folded["shown"], "refusals_measured": True},
                             marks_mod.DEFAULTS)
    assert judged["refusals"]["value"] == pytest.approx(3 / 4)
    assert judged["refusals"]["count"] == 3 and judged["refusals"]["shown"] == 4


def test_record_verdicts_keeps_both_entries_and_one_raw_to_accepted_row(cases):
    state = run_mod._RunState()
    case = cases[RESPONDENT]
    answer = _ask(case, _Host({"bad": True, "n": 1}, {"n": 2}), _Aggregate())
    state.record_verdicts(case, answer)
    assert state.judged == {RESPONDENT}
    assert [v["case_id"] for v in state.verdict_entries] == [RESPONDENT, RESPONDENT + "#redraw"]
    row = state.redraws[0]
    assert row["accepted"] and row["raw"] == {"bad": True, "n": 1} and row["redrawn"] == {"n": 2}
    assert row["first_refusal"]["rule"] == "R3" and row["second_refusal"] is None


# --------------------------------------------------------------------- the bundle and a re-score

def _bundle(tmp_path, monkeypatch):
    from types import SimpleNamespace
    bundle = tmp_path / "20261008T000000Z-instructions"
    bundle.mkdir()
    fx.write_export(bundle / "contracts")
    (bundle / "scorecard.json").write_text(json.dumps(
        {"marks_version": marks_mod.MARKS_VERSION, "n_runs": 1, "model": {"host": "claude"},
         "totals": {}}))
    (bundle / "manifest.json").write_text(json.dumps({"host": "claude",
                                                      "marks_version": marks_mod.MARKS_VERSION}))
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: SimpleNamespace(keel_cloud=tmp_path / "no-keel-cloud"))
    monkeypatch.setattr(rescore_mod.corpus_mod, "load",
                        lambda keel_cloud: rescore_mod.corpus_mod.Corpus(
                            entries=[rescore_mod.corpus_mod.load_file(fx.ENTRY)],
                            directory=fx.ENTRY.parent))
    return bundle


def test_the_bundle_records_both_drafts_and_a_rescore_reads_the_accepted_one(
        tmp_path, monkeypatch, cases, capsys):
    bundle = _bundle(tmp_path, monkeypatch)
    entry = fx.entry()
    good = fx.respondent_result(entry, 1)
    bad = {**_broken(good), "bad": True}
    case = cases[RESPONDENT]
    answer = _ask(case, _Host(bad, good), _Aggregate())
    report_mod.write_case(bundle, case, answer, {}, host="claude")

    envelope = json.loads((report_mod.case_dir(bundle, case) / "envelope.json").read_text())
    assert envelope["answer"]["raw"]["result"] == bad
    assert envelope["answer"]["accepted"]["result"] == good
    assert envelope["answer"]["scored"] == "accepted"
    assert [r["rule"] for r in envelope["refusals"]] == ["R3"]
    assert envelope["redraw"]["repair"].startswith("NOT DERIVED")
    assert envelope["redraw"]["result"] == good
    assert (report_mod.case_dir(bundle, case) / "prompt-redraw.txt").read_text() == \
        "REDRAW PROMPT"

    assert rescore_mod.main([str(bundle), "--no-judge"]) == 0
    written = json.loads((bundle / f"scorecard-v{marks_mod.MARKS_VERSION}.json").read_text())
    assert written["totals"]["scored_on"] == run_mod.SCORED_ON_ACCEPTED
    assert written["totals"]["respondent_validity"]["hit"] == _gates(entry)
    assert written["redraws"][0]["accepted"] is True
    assert "scored on  accepted" in capsys.readouterr().out


def test_a_bundle_without_the_answer_block_scores_raw_and_says_so(
        tmp_path, monkeypatch, cases, capsys):
    bundle = _bundle(tmp_path, monkeypatch)
    entry = fx.entry()
    case = cases[RESPONDENT]
    directory = report_mod.case_dir(bundle, case)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "envelope.json").write_text(json.dumps({
        "case_id": case.case_id, "outcome": "COMPLETED", "schema_valid": True,
        "result": _broken(fx.respondent_result(entry, 1))}))
    (bundle / "verdict.json").write_text(json.dumps({"marks": {}, "n_runs": 1, "cases": 1,
                                                     "errored": 0}))
    (bundle / "versions.json").write_text("{}")

    assert rescore_mod.main([str(bundle), "--no-judge"]) == 0
    written = json.loads((bundle / f"scorecard-v{marks_mod.MARKS_VERSION}.json").read_text())
    assert written["totals"]["scored_on"] == run_mod.SCORED_ON_RAW
    assert written["totals"]["respondent_validity"]["hit"] < _gates(entry)
    assert "predates judgement call 41" in capsys.readouterr().out
    page = (bundle / f"report-v{marks_mod.MARKS_VERSION}.html").read_text()
    assert "Scored on the raw answer" in page and "predates judgement call 41" in page


# ------------------------------------------- decision 46's BRIEF redraw left with the screen (spec 052)

def test_no_brief_is_redrawn_since_keel_cloud_104():
    """Call 116: keel-cloud 104 deleted the BRIEF screen, so decision 46's redraw of it (and `refused_twice`, which
    scored a brief refused twice as a fault) went with it; the question screens' redraw is unchanged."""
    from instructions import runner as runner_mod                            # noqa: PLC0415
    assert "BRIEF" not in runner_mod.REDRAW_SCREENS and not hasattr(run_mod, "refused_twice")
    assert runner_mod.UNATTENDED_SCREENS == runner_mod.QUESTION_SCREENS


# -------------------------------------- spec 040 (call 87): ASKED is redrawn like the question screens

ASKED = "09-fixture/ASKED_COMPATIBILITY/run1"
K3 = {"kind": "rule", "rule": "K3", "path": "result.items[index=0].asked",
      "message": "K3: 'was the phone to hand' is not said to the stranger; write it in the second person (you, your)"}


def test_asked_is_an_unattended_question_screen():
    assert "ASKED" in runner_mod.QUESTION_SCREENS
    assert "ASKED" in runner_mod.UNATTENDED_SCREENS and "ASKED" in runner_mod.REDRAW_SCREENS


def test_a_refused_asked_job_is_redrawn_once_with_the_derivation_text(cases):
    """keel-cloud 088's `askedLadder`: the first repair is `queueAnotherQuestionsTurn` with
    `RecoverySection.derivationRepairText(path + ": " + why)`, on the class's own tier; its second rung (standard)
    is not modelled."""
    case = cases[ASKED]
    raw = {"bad": True, "items": [{"index": 0, "asked": "was the phone to hand"},
                                  {"index": 1, "asked": "were your keys all on one ring"}]}
    redrawn = fx.asked_result(fx.entry())
    host, aggregate = _Host(raw, redrawn), _Aggregate(K3)
    answer = _ask(case, host, aggregate)
    assert len(host.requests) == 2 and aggregate.calls == [(ASKED, False), (ASKED, True)]
    sent = host.requests[1].request_payload
    assert sent["context"] == {**case.payload["context"], "repair": (
        "NOT DERIVED -- your previous answer was accepted as a shape and then could not be resolved: "
        "result.items[index=0].asked: K3: 'was the phone to hand' is not said to the stranger; write it in the "
        "second person (you, your). Answer again with everything you already had; fix only that; change nothing "
        "else.")}
    assert sent["interaction_history"] == [] and sent["input"] == {"content": ""}
    assert answer.scored.result is redrawn


def test_an_l_refusal_is_redrawn_as_the_rule_the_validator_reports():
    """Spec 042 call 113 (DRIFT #76 closed): keel-cloud's validator reports a founder-lists refusal `kind: rule`, and
    the cloud's orchestrator repairs it, so the eval redraws it once; a shape refusal is never redrawn, whatever its
    message opens with (spec 040's call 86 reading is gone)."""
    import types                                                         # noqa: PLC0415
    from instructions import runner as runner_mod                        # noqa: PLC0415
    case = types.SimpleNamespace(screen="CALIBRATION_QUESTIONS")
    rule = {"accepted": False, "refusal": {"kind": "rule", "rule": "L1", "path": "result.questions[2].list.items",
                                           "message": "L1: problem.importance takes exactly 5 items"}}
    shaped = {"accepted": False, "refusal": {"kind": "shape", "rule": None, "path": "result.questions[2].list.items",
                                             "message": "L1: problem.importance takes exactly 5 items"}}
    assert runner_mod.should_redraw(case, rule)
    assert not runner_mod.should_redraw(case, shaped)
