"""Spec 126 -- the founder types like a person: the typist, where he types, and the leak check."""
from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import backtest as bt
from harness import typist as tp
from harness import vectors_script as vs
from instructions import spelling
from quality import cycle, rubric, table
from stack.config import load_config

REPO = Path(__file__).resolve().parent.parent
FX = Path(__file__).parent / "fixtures"
#: 21-codyco's PROBLEM walk of cycle 6 (`runs/20261101T111212Z-backtest-21-codyco`), its served parts kept as recorded.
WALK = FX / "typist" / "backtest-21-codyco-PROBLEM.json"
CYCLE_FX = FX / "quality" / "cycle"
SCORE = CYCLE_FX / "scores" / "08-fresco" / "20261101-SOLUTION-r3-abcdef1-v13-claude-opus-5-5.json"
RECORD = REPO / "quality" / "cycles" / "20261101-d096da9.md"
KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)

LONG = ("Hotel groups miss about five percent of their reservation calls even with a central reservations office, "
        "after hours, during peak hours and on holidays; every call that rings out is a booking that goes elsewhere.")


def _walk() -> dict:
    return json.loads(WALK.read_text(encoding="utf-8"))


def _typed_of(bundle: dict) -> list[dict]:
    """The typos the typist types on the recorded walk's own fields (as `type_founder` would, the idea name kept)."""
    screens = {s["screen"]: s for s in bundle["founder_screens"]}
    ctx, out = screens["context"]["answer"], []
    for name, text in [*((k, ctx[k]) for k in tp.CONTEXT_FIELDS), ("problem_seed", screens["problem-seed"]["answer"])]:
        _, found = tp.typos(text, f"21-codyco:{name}", keep={"codyco"})
        out += [{"field": name, "meant": t.meant, "typed": t.typed, "kind": t.kind} for t in found]
    return out


def _untyped(typed: str, found) -> str:
    out, at = [], 0
    for t in found:
        m = re.compile(rf"(?<![^\W\d_]){re.escape(t.typed)}(?![^\W\d_])").search(typed, at)
        out += [typed[at:m.start()], t.meant]
        at = m.end()
    return "".join(out) + typed[at:]


# ------------------------------------------------------------------------------------------------ FR-1 the typist

def test_the_typist_is_deterministic_from_its_seed():
    assert tp.typos(LONG, "21-codyco:problem_seed") == tp.typos(LONG, "21-codyco:problem_seed")
    assert tp.typos(LONG, "21-codyco:problem_seed") != tp.typos(LONG, "08-fresco:problem_seed")
    assert tp.typos(LONG, "21-codyco:problem_seed") != tp.typos(LONG, "21-codyco:segment")


@pytest.mark.parametrize("word, kind, typed", [
    ("receive", "ie/ei", "recieve"), ("believe", "ie/ei", "beleive"), ("without", "dropped", "withot"),
    ("errors", "dropped", "erros"), ("running", "doubled", "runnning"), ("every", "transposed", "evrey")])
def test_the_kinds_people_make(word, kind, typed):
    assert (kind, typed) in tp.edits(word)
    assert all(t[0] == word[0] and spelling.distance(word, t) == 1 for _, t in tp.edits(word))
    assert all(spelling.same_word(word, t) for _, t in tp.edits(word))


def test_the_ie_ei_swap_is_the_only_typo_of_a_word_that_has_one():
    assert {k for k, _ in tp.edits("receive")} == {"ie/ei"}


@pytest.mark.parametrize("words, owed", [(1, 0), (3, 0), (4, 1), (12, 1), (17, 1), (18, 2), (24, 2), (30, 3)])
def test_about_one_typo_every_twelve_words_and_one_from_four(words, owed):
    assert tp.owed(" ".join(["payroll"] * words)) == owed


def test_the_rules_names_numbers_units_short_words_and_the_first_letter():
    text = ("Codyco answers every missed booking within 30 seconds for 5,000 dollars a month; the hotel's agents "
            "forward calls, and Opera Cloud stores bookings as payments arrive minutes later.")
    keep = {"bookings", "booking"}
    typed, found = tp.typos(text, "99-x:problem_seed", keep=keep)
    assert found and len(found) == tp.owed(text)
    for t in found:
        assert re.fullmatch(r"[a-z]{5,}", t.meant), t
        assert t.meant not in keep and t.meant not in tp.UNITS, t
        assert t.typed[0] == t.meant[0] and spelling.distance(t.meant, t.typed) == 1, t
    assert {"Codyco", "Opera", "Cloud", "30", "5,000", "hotel's", "dollars", "seconds", "minutes"} <= set(
        re.findall(r"[\w',]+", typed))
    assert _untyped(typed, found) == text, "punctuation and spacing kept; one edit a word"


def test_a_typo_never_lands_on_a_word_of_the_entrys_material():
    plain = tp.typos(LONG, "21-codyco:problem_seed")[1]
    avoid = {t.typed for t in plain}
    for t in tp.typos(LONG, "21-codyco:problem_seed", avoid=avoid)[1]:
        assert t.typed not in avoid


def test_a_field_with_nothing_to_type_wrong_carries_none():
    assert tp.typos("they have rupees left over", "09-karsa:circumstance") == ("they have rupees left over", [])
    assert tp.typos("reservation agent", "21-codyco:actor")[1] == []          # two words: none owed


@pytest.mark.skipif(not (KEEL_CLOUD / "canon/designs/measured-beliefs/backtest").is_dir(),
                    reason="no keel-cloud back-test directory beside this checkout")
def test_every_back_test_entry_is_typed_by_the_rules():
    corpus = vs.load(KEEL_CLOUD, backtest=True)
    assert corpus.entries
    for entry in corpus.entries:
        founder = vs.founder_inputs(entry)
        keep = tp.kept_words(entry)
        typed, found = tp.type_founder(entry, founder)
        assert typed == tp.type_founder(entry, founder)[0], entry.id
        for name, text in tp.field_texts(founder).items():
            mine = [t for t in found if t["field"] == name]
            candidates = [w for w in re.findall(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*", text) if tp.typeable(w, keep=keep)]
            if tp.word_count(text) >= tp.AT_LEAST_ONE_FROM and candidates:
                assert mine, (entry.id, name, text)
            assert len(mine) <= tp.owed(text), (entry.id, name)
            for t in mine:
                assert t["meant"] not in keep and t["typed"][0] == t["meant"][0], (entry.id, t)
                assert spelling.same_word(t["meant"], t["typed"]), (entry.id, t)
            assert _untyped(tp.field_texts(typed)[name], [tp.Typo(t["meant"], t["typed"], t["kind"])
                                                          for t in mine]) == text, (entry.id, name)
        names = tp._words_of(founder.idea_name)
        assert not {t["meant"] for t in found} & names, entry.id


# ------------------------------------------------------------------------------------------------ FR-2 where he types

def test_the_founder_types_his_four_fields_and_two_seeds_and_nothing_else():
    entry = SimpleNamespace(id="21-codyco", idea_name="Codyco", interpretations={"offer_name": "an agent for calls"},
                            solution_mechanism={"short_name": "Codyco"}, path=None)
    founder = vs.FounderInputs(
        project_name="Codyco missed calls", country="DE", region=None, language="de-DE",
        context_fields={"actor": "reservation agent", "job": "turn every guest who calls into a booking",
                        "circumstance": "booking calls come in on every shift and not every one gets answered",
                        "segment": "reservation agents at hotel groups that run a central reservations office"},
        window=vs.Window(7, "DAYS"), problem_seed=LONG, solution_seed=LONG.replace("Hotel groups", "Hotels"),
        decider={"kind": "SAME_PERSON"}, calibration={"PROBLEM": []}, hourly_rate=None, idea_name="Codyco")
    typed, found = tp.type_founder(entry, founder)
    assert {t["field"] for t in found} == {"job", "circumstance", "segment", "problem_seed", "solution_seed"}
    assert all(set(t) == {"field", "meant", "typed", "kind"} for t in found)
    for same in ("project_name", "country", "region", "language", "window", "decider", "calibration", "hourly_rate",
                 "idea_name"):
        assert getattr(typed, same) == getattr(founder, same), same
    assert typed.context_fields["actor"] == "reservation agent"
    assert typed.problem_seed != founder.problem_seed and typed.solution_seed != founder.solution_seed
    assert not any(t["meant"] in {"agent", "calls", "codyco"} for t in found), "the offer name's words stand"


def test_the_dry_line_marks_each_typo_typed_then_meant():
    found = [tp.Typo("without", "withot", "dropped"), tp.Typo("errors", "erros", "dropped")]
    assert tp.marked("payroll withot erros, withot fail", found) == "payroll withot[without] erros[errors], withot fail"
    assert tp.marked("payroll withot withot", [tp.Typo("without", "withot", "dropped")] * 2) == \
        "payroll withot[without] withot[without]"


def test_the_back_test_types_with_typos_only_when_told():
    assert bt.typos({}) is False and bt.typos({bt.TYPOS_VAR: "0"}) is False and bt.typos({bt.TYPOS_VAR: "off"}) is False
    assert bt.typos({bt.TYPOS_VAR: "1"}) is True and bt.typos({bt.TYPOS_VAR: "on"}) is True
    assert "TYPOS='sometimes'" in bt.door_refusal({bt.TYPOS_VAR: "sometimes"})
    assert bt.Backtest(run_dir=Path("."), stack=None).typos is False
    source = (REPO / "evals" / "corpus_scenario.py").read_text(encoding="utf-8")
    assert source.count("typist.type_founder(") == 1 and 'getattr(backtest, "typos", False) is True' in source
    for golden in ("scope_journey.py", "open_link_leg.py", "backtest.py", "test_s012_journey_through_a_host.py"):
        text = (REPO / "evals" / golden).read_text(encoding="utf-8")
        assert "import typist" not in text and "typist." not in text.replace("harness/typist.py", ""), golden


def test_the_walk_passes_typos_to_every_back_test_unless_told_not_to(tmp_path):
    on = [s["argv"][4:] for s in cycle.plan_steps(["21-codyco"], ["PROBLEM"], "keel", tmp_path, 7, True)
          if s["what"] == "backtest"]
    assert on == [["backtest", "ENTRY=21-codyco", "SCOPE=PROBLEM", "DOOR=keel", "PEOPLE=7", "TYPOS=1"]]
    off = [s["argv"][4:] for s in cycle.plan_steps(["21-codyco"], ["PROBLEM"], "keel", tmp_path, 7)
           if s["what"] == "backtest"]
    assert off == [["backtest", "ENTRY=21-codyco", "SCOPE=PROBLEM", "DOOR=keel", "PEOPLE=7"]]
    make = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "$(if $(filter 0 off,$(TYPOS)),--typos off,)" in make
    assert "$(if $(TYPOS),KEEL_BACKTEST_TYPOS=$(TYPOS) ,)" in make


def _dry(monkeypatch, tmp_path, capsys, *extra):
    from tests.test_quality_cycle_079 import git_checkout                       # noqa: PLC0415
    web = git_checkout(tmp_path / "web", {"package.json": "{}\n"})
    cloud = git_checkout(tmp_path / "cloud", {"canon/designs/measured-beliefs/backtest/21-codyco.yaml": "id\n"})
    monkeypatch.setattr(cycle, "checkouts", lambda: (cloud, web))
    code = cycle.walk(["--entries", "21-codyco", "--scopes", "PROBLEM", "--why", "dry", "--dry-run",
                       "--cycles-dir", str(tmp_path / "cycles"), *extra], runner=None, env={}, which=lambda n: None)
    return code, capsys.readouterr().out


def test_the_dry_walk_says_the_typed_fields_or_that_typos_are_off(monkeypatch, tmp_path, capsys):
    code, out = _dry(monkeypatch, tmp_path, capsys)
    assert code == 0 and "PEOPLE=7 TYPOS=1" in out and "typos: on (spec 126" in out
    assert "21-codyco: the typed fields could not be read" in out              # a stub yaml: said, never refused
    code, out = _dry(monkeypatch, tmp_path / "off", capsys, "--typos", "off")
    assert code == 0 and "TYPOS=1" not in out and "typos: off (TYPOS=0)" in out


@pytest.mark.skipif(not (KEEL_CLOUD / "canon/designs/measured-beliefs/backtest/21-codyco.yaml").is_file(),
                    reason="no keel-cloud 21-codyco beside this checkout")
def test_the_dry_lines_of_21_codyco_mark_its_typos():
    _, entry = vs.entry_for(KEEL_CLOUD, "21-codyco", backtest=True)
    lines = tp.dry_lines(entry, vs.founder_inputs(entry))
    assert [line.split(" (", 1)[0].strip() for line in lines] == list(tp.FIELDS)
    assert re.search(r"problem_seed \(\d+ typos\): .*\b[a-z]+\[[a-z]+\]", lines[4])
    assert lines[0].startswith("    actor (0 typos): ")


# ------------------------------------------------------------------------------------------------ FR-3 the leaks

def test_the_recorded_walk_typed_as_a_person_leaks_nothing():
    bundle = _walk()
    typed = _typed_of(bundle)
    assert typed and tp.walked(bundle, typed) == typed
    assert tp.leaks(bundle, typed) == []


def test_what_the_founder_typed_is_never_a_leak():
    bundle, typed = _walk(), _typed_of(_walk())
    screens = {s["screen"]: s for s in bundle["founder_screens"]}
    screens["problem-seed"]["answer"] = f"{screens['problem-seed']['answer']} {typed[-1]['typed']}"
    assert tp.leaks(bundle, typed) == []


def test_a_typed_form_in_a_served_question_is_a_leak_named_in_the_founders_words():
    bundle, typed = _walk(), _typed_of(_walk())
    leak = next(t for t in typed if t["field"] == "problem_seed")
    item = next(d for d in bundle["respondents"]["PRIMARY"]["drawn"] if d.get("screen") == "item")
    item["question"] = f"In the last week, how many calls {leak['typed'].upper()} out?"
    found = tp.leaks(bundle, typed)
    assert found == [{"screen": f"respondent PRIMARY item {item['dimension']}", "field": "problem_seed",
                      "meant": leak["meant"], "typed": leak["typed"],
                      "text": f"In the last week, how many calls {leak['typed'].upper()} out?"}]
    assert tp.leak_line(found[0]) == (f"typo leak: \"{leak['typed']}\" (meant \"{leak['meant']}\") reached the "
                                      f"PROBLEM question \"In the last week, how many calls {leak['typed'].upper()} "
                                      "out?\"")


def test_a_leak_is_a_whole_word_and_a_corrected_word_is_none():
    bundle = _walk()
    typed = [{"field": "problem_seed", "meant": "without", "typed": "withot", "kind": "dropped"}]
    bundle["brief"]["contextUnderstands"] = "They run payroll without errors; withotx is no word of the founder's."
    assert tp.leaks(bundle, typed) == []
    bundle["after_screens"][0]["text"] = "How do you run payroll withot errors?"
    found = tp.leaks(bundle, typed)
    assert [f["screen"] for f in found] == [f"after {bundle['after_screens'][0]['screen']}"]


def test_a_problem_study_never_types_the_solution_seed():
    typed = [{"field": "solution_seed", "meant": "payment", "typed": "pyment", "kind": "dropped"},
             {"field": "segment", "meant": "agents", "typed": "agenst", "kind": "transposed"}]
    assert tp.walked(_walk(), typed) == typed[1:]


def test_the_gallery_reads_the_words_the_founder_meant():
    founder = {"problem_seed": "payroll withot erros", "context_fields": {"job": "pay evrey worker"}, "project_name": "x"}
    typed = [{"field": "problem_seed", "meant": "without", "typed": "withot", "kind": "dropped"},
             {"field": "problem_seed", "meant": "errors", "typed": "erros", "kind": "dropped"},
             {"field": "job", "meant": "every", "typed": "evrey", "kind": "transposed"}]
    assert tp.as_meant(founder, typed) == {"problem_seed": "payroll without errors",
                                           "context_fields": {"job": "pay every worker"}, "project_name": "x"}
    assert tp.as_meant(founder, None) == founder


# --------------------------------------------------------------------------------- FR-3 the score file and the record

def _walk_one(tmp_path, record: dict):
    tmp_path.mkdir(parents=True, exist_ok=True)
    score = tmp_path / "score.json"
    shutil.copy(SCORE, score)
    runs = tmp_path / "runs"

    def fake(argv, stdout=None, stderr=None):
        if argv[4] == "backtest":
            run = runs / "20261101T110000Z-backtest-21-codyco"
            run.mkdir(parents=True)
            (run / bt.RECORD).write_text(json.dumps({"run": run.name, "passed": True, "scope": "SOLUTION",
                                                     **record}))
            stdout.write(f"run bundle: {run}\n")
        if argv[4] == "read-screens":
            out = Path(argv[6].split("=", 1)[1])
            out.mkdir(parents=True)
            (out / "score-path.txt").write_text(f"{score}\n")
        return SimpleNamespace(returncode=0)

    steps = [s for s in cycle.plan_steps(["21-codyco"], ["SOLUTION"], "host", tmp_path / "work", typos=True)
             if s["study"]]
    study = cycle.walk_one("21-codyco", "SOLUTION", steps, door="host", runner=fake, runs_dir=runs)
    return study, score


def test_the_score_file_carries_the_typos_and_the_leaks_only_when_typos_were_typed(tmp_path):
    bundle = _walk()
    typed = _typed_of(bundle)
    leak = typed[0]
    bundle["respondents"]["PRIMARY"]["served"]["idea"] = {"line": f"An idea for {leak['typed']} people."}
    study, score = _walk_one(tmp_path, {k: bundle[k] for k in ("founder_screens", "respondents", "brief")}
                             | {"typos": typed})
    obj = json.loads(score.read_text(encoding="utf-8"))
    assert study.score_file and obj["typos"] == typed
    assert [x["screen"] for x in obj["typo_leaks"]] == ["respondent PRIMARY idea"]
    rubric.validate_file(obj)

    study, score = _walk_one(tmp_path / "none", {"founder_screens": bundle["founder_screens"]})
    assert score.read_bytes() == SCORE.read_bytes(), "a walk with no typo leaves the score file as the readers wrote it"


def test_the_head_and_the_record_say_the_typos_only_when_there_were_any():
    data = cycle.load_record(RECORD)
    before = cycle.render_record(data)
    assert "typos" not in before and "Typo leaks" not in before
    data["head"].update(typos=12, typo_fields=5, typo_leaks=1)
    data["typo_leaks"] = {"21-codyco · PROBLEM": {"typos": 12, "fields": 5, "leaks": [
        {"screen": "respondent PRIMARY item problem.prevalence", "field": "problem_seed", "meant": "rings",
         "typed": "rigns", "text": "In the last week, how many calls rigns out?"}]},
        "08-fresco · PROBLEM": {"typos": 9, "fields": 5, "leaks": []}}
    text = cycle.render_record(data)
    assert "  - typos: 12 typed on 5 fields; 1 leaked (spec 126)" in text
    assert "- **21-codyco · PROBLEM**: 12 typos typed on 5 fields; 1 leaked" in text
    assert ('  - typo leak: "rigns" (meant "rings") reached the PROBLEM question "In the last week, how many calls '
            'rigns out?"') in text
    assert "- **08-fresco · PROBLEM**: 9 typos typed on 5 fields; none leaked" in text


def test_head_of_counts_the_typos_over_the_latest_files():
    files = [json.loads(SCORE.read_text(encoding="utf-8"))]
    head = cycle._head_of(copy.deepcopy(files))
    assert "typos" not in head
    files[0].update(typos=[{"field": "job", "meant": "every", "typed": "evrey", "kind": "transposed"},
                           {"field": "problem_seed", "meant": "rings", "typed": "rigns", "kind": "transposed"},
                           {"field": "problem_seed", "meant": "about", "typed": "aboutt", "kind": "doubled"}],
                    typo_leaks=[{"screen": "brief", "field": "job", "meant": "every", "typed": "evrey", "text": "x"}])
    head = cycle._head_of(files)
    assert (head["typos"], head["typo_fields"], head["typo_leaks"]) == (3, 2, 1)
    key = table.study(files[0])
    assert key in table.latest_per_entry(files)
