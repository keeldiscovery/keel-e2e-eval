"""Spec 105 (keel-cloud 169, routing v14, `InferenceCharge.VERSION` 13): the harness reads the frontier tier.

FR-1, the fallback mirror: a class on a tier a host has no row for stands one rung down -- `frontier` on `standard`
and nothing else -- model and effort together, as keel-cloud's `ModelRouting.FALLBACK` / `standingTier` resolve it;
the S-012 per-job model check reads `resolve_screen`, so it follows. The table is read as the file."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from instructions import models as models_mod
from instructions import prompts as prompts_mod

REPO = Path(__file__).resolve().parent.parent

#: routing v14's shape (keel-cloud 169), synthetic: `frame` on `frontier`, pinned on `claude` alone.
V14 = {
    "version": 14,
    "hosts": {
        "codex": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "copilot": {"light": "gpt-5.6-luna", "standard": "gpt-5.6-terra"},
        "claude": {"light": "claude-haiku-4-5-20251001", "standard": "claude-sonnet-5-5",
                   "frontier": "claude-opus-5-5"},
    },
    "efforts": {"codex": {"standard": "medium"}, "copilot": {"standard": "medium"},
                "claude": {"standard": "medium", "frontier": "medium"}},
    "_tiers": ["light", "standard", "frontier"],
    "classes": {"frame": "frontier", "reading": "light", "brief": "standard", "context": "light",
                "calibration": "standard", "respondent": "standard", "asked": "light", "example_match": "light"},
}


def _frame_case(screen="PROBLEM_INTERPRET"):
    return prompts_mod.Case(case_id=f"e/{screen}/run1", kind="FRAME", entry_id="e", screen=screen,
                            subject="PROBLEM", run_index=1,
                            payload=prompts_mod.payload_for("I", {"k": None}, {"allowed_outcomes": ["COMPLETED"]}))


# --------------------------------------------------------------------------------------- FR-1: the fallback

def test_the_mirror_is_keel_clouds_fallback():
    assert models_mod.FALLBACK == {"frontier": "standard"}


def test_claude_runs_the_frame_screens_on_its_frontier_row():
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier("claude", "frame") == "frontier"
    for screen in ("PROBLEM_INTERPRET", "SOLUTION_MECHANISM"):
        assert table.resolve_screen("claude", screen) == "claude-opus-5-5"
        assert table.resolve_effort_screen("claude", screen) == "medium"


@pytest.mark.parametrize("host", ["codex", "copilot"])
def test_a_host_with_no_frontier_row_stands_on_its_standard_row_model_and_effort_together(host):
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier(host, "frame") == "standard"
    for screen in ("PROBLEM_INTERPRET", "SOLUTION_MECHANISM"):
        assert table.resolve_screen(host, screen) == "gpt-5.6-terra"
        assert table.resolve_effort_screen(host, screen) == "medium"
    assert table.models_used(host)["frame"] == "gpt-5.6-terra"
    assert table.efforts_used(host)["frame"] == "medium"
    # the file is read as the file: no frontier row is invented
    assert "frontier" not in table.hosts[host] and table.tier_for("frame") == "frontier"


def test_stamp_puts_the_fallen_back_model_and_effort_on_a_frame_case():
    table = models_mod.parse(V14, source="v14")
    case = _frame_case("SOLUTION_MECHANISM")
    models_mod.stamp([case], table, "copilot")
    assert case.payload[models_mod.MODEL_KEY] == {"copilot": "gpt-5.6-terra"}
    assert case.payload[models_mod.EFFORT_KEY] == {"copilot": "medium"}
    models_mod.stamp([case], table, "claude")
    assert case.payload[models_mod.MODEL_KEY] == {"claude": "claude-opus-5-5"}
    assert case.payload[models_mod.EFFORT_KEY] == {"claude": "medium"}


def test_only_frontier_falls_and_only_one_rung():
    """keel-cloud `ModelRoutingTest.onlyFrontierFallsBackAndOnlyOneRung`: a standard class on a host with no standard
    row is no pin (a standard job is never sent to a light model), and a frontier class on a host with a light row
    only is no pin too."""
    document = json.loads(json.dumps(V14))
    document["hosts"]["codex"] = {"light": "gpt-5.6-luna"}
    document["efforts"]["codex"] = {}
    table = models_mod.parse(document, source="light-only")
    assert table.standing_tier("codex", "calibration") is None
    assert table.resolve("codex", "calibration") is None
    assert table.resolve("codex", "frame") is None
    assert table.resolve_effort("codex", "frame") is None
    assert table.resolve("codex", "reading") == "gpt-5.6-luna"


def test_the_effort_is_read_where_the_model_stands():
    """A host that pins a frontier MODEL with no frontier effort runs it at the CLI's default effort -- never the
    standard row's effort beside the frontier model (the effort falls only with the model)."""
    document = json.loads(json.dumps(V14))
    document["efforts"]["claude"] = {"standard": "medium"}
    table = models_mod.parse(document, source="no-frontier-effort")
    assert table.resolve("claude", "frame") == "claude-opus-5-5"
    assert table.resolve_effort("claude", "frame") is None


def test_a_host_with_no_row_at_all_is_still_no_pin():
    table = models_mod.parse(V14, source="v14")
    assert table.standing_tier("gemini", "frame") is None
    assert table.resolve("gemini", "frame") is None and table.resolve_effort("gemini", "frame") is None


def test_keel_clouds_live_table_resolves_the_frame_screens_per_host():
    from stack.config import load_config                                    # noqa: PLC0415
    path = load_config(validate=False).keel_cloud / models_mod.CLOUD_RESOURCE
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {path.parent}")
    table = models_mod.load(path)
    if table.tier_for("frame") != "frontier":
        pytest.skip(f"keel-cloud's routing v{table.version} predates spec 169 (frame is not on frontier)")
    assert table.resolve_screen("claude", "PROBLEM_INTERPRET") == "claude-opus-5-5"
    for host in ("codex", "copilot"):
        assert table.resolve_screen(host, "SOLUTION_MECHANISM") == table.hosts[host]["standard"]
        assert table.resolve_effort_screen(host, "SOLUTION_MECHANISM") == table.efforts[host]["standard"]


def test_s012s_per_job_check_reads_the_resolver_that_falls_back():
    source = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text(encoding="utf-8")
    assert "routing_table.resolve_screen(HOST, screen)" in source
    assert "standing_tier" in inspect.getsource(models_mod.ModelTable.resolve)


# ------------------------------------------------------------------------------------ FR-2: the price version

def test_price_version_13_is_pinned_in_the_mirror_and_both_fakes():
    from harness import contacts_fake, interviewer_fake                     # noqa: PLC0415
    from harness import interview_charge as charge                          # noqa: PLC0415
    assert charge.PRICE_VERSION == interviewer_fake.PRICE_VERSION == contacts_fake.PRICE_VERSION == 13
    # §6.3's classic five-participant figure moved no row at 13
    assert charge.FIVE_PARTICIPANTS == charge.project_credits(5, version=12) == 1_355


@pytest.mark.parametrize("rel", ["harness/interview_charge.py", "harness/interviewer_fake.py",
                                 "harness/contacts_fake.py", "evals/test_s012_journey_through_a_host.py"])
def test_the_prose_beside_each_pin_names_13(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert "13" in text and "169" in text, rel


# ------------------------------------------------------------- FR-3: the screen reads back-test and probe entries

import types                                                                 # noqa: E402

import yaml                                                                  # noqa: E402

from instructions import corpus as corpus_mod                                # noqa: E402
from instructions import run as run_mod                                      # noqa: E402
from instructions import screen_entries as screen_mod                        # noqa: E402
from tests import v9_fixtures as fx                                          # noqa: E402

#: keel-cloud 169's probe, restated as a fixture (the live file is read below, skipped by name where absent).
PROBE = {
    "id": "169-banking-gaming",
    "title": "Card fraud blocks at a retail bank",
    "market": {"country": "GB", "region": None, "language": "en-GB"},
    "context": {"actor": "payments operations analyst",
                "actor_plural": "payments operations analysts at retail banks",
                "job": "keep customers able to pay when their debit card is blocked for fraud",
                "circumstance": "a customer's debit card is blocked for suspected fraud",
                "segment": "retail banks in the UK that issue their own debit cards",
                "recall_window": {"count": 3, "unit": "MONTHS"}},
    "statements": {"problem": "Customers cannot pay until the new card comes, and customers churn after the first "
                              "loot box of fees that follows.",
                   "solution": "The app respawns the card in the customer's phone wallet with a new number."},
    "interpretations": {"problem": "Payments operations analysts see customers left unable to pay.",
                        "offer_name": "a quicker way back to paying"},
    "probes": [
        {"screen": "PROBLEM_INTERPRET", "seed": "statements.problem", "planted": "loot box",
         "gaming_sense": "a paid box of random items in a video game", "banking_sense": "a bundle of fees",
         "first_turn": {"outcome": "NEEDS_INPUT", "questions": 1, "names_the_term": True, "readings": 2}},
        {"screen": "SOLUTION_MECHANISM", "seed": "statements.solution", "planted": "respawns",
         "gaming_sense": "a player brought back to life", "banking_sense": "a replacement card issued at once",
         "first_turn": {"outcome": "NEEDS_INPUT", "questions": 1, "names_the_term": True, "readings": 2}},
    ],
}


def _checkout(tmp_path, *, probe=PROBE, broken=False):
    """A keel-cloud checkout with one back-test entry (the golden fixture, as a back-test entry) and the probe."""
    root = tmp_path / "keel-cloud"
    backtest = corpus_mod.backtest_dir(root)
    probes = screen_mod.probes_dir(root)
    backtest.mkdir(parents=True)
    probes.mkdir(parents=True)
    raw = fx.raw_entry()
    raw["id"] = "08-fixture-bt"
    raw.pop("expected", None)
    raw["idea_name"] = "The fixture idea"
    (backtest / "08-fixture-bt.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    (probes / f"{probe['id']}.yaml").write_text(yaml.safe_dump(probe, sort_keys=False), encoding="utf-8")
    if broken:
        (backtest / "30-broken.yaml").write_text("id: 30-broken\nrevision: 1\n", encoding="utf-8")
        (probes / "31-broken.yaml").write_text("id: 31-broken\n", encoding="utf-8")
    return root


def _args(needle, n_runs=1):
    return types.SimpleNamespace(filter=needle, n_runs=n_runs, host="claude")


@pytest.mark.parametrize("needle, wanted", [(None, False), ("", False), ("frame", False), ("Context", False),
                                            ("01-countly", True), ("08-fresco/PROBLEM_INTERPRET", True),
                                            ("169-banking-gaming", True)])
def test_only_a_screen_needle_reads_the_extras(needle, wanted):
    assert screen_mod.wanted(needle) is wanted


def test_the_full_eval_and_a_kind_word_read_nothing_beside_the_corpus(tmp_path):
    root = _checkout(tmp_path, broken=True)
    for needle in (None, "frame", "calibration"):
        assert not screen_mod.load(root, needle), needle


def test_a_golden_screen_never_reads_an_unrelated_extra_file(tmp_path):
    root = _checkout(tmp_path, broken=True)
    assert not screen_mod.load(root, "01-countly"), "the broken files are not named, so never read"
    with pytest.raises(corpus_mod.CorpusError):
        screen_mod.load(root, "30-broken")


def test_the_needle_names_a_backtest_entry_and_builds_its_three_interpretation_screens(tmp_path):
    root = _checkout(tmp_path)
    extras = screen_mod.load(root, "08-fixture-bt")
    assert [e.id for e in extras.backtest] == ["08-fixture-bt"] and extras.probes == []
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                   needle="08-fixture-bt", n_runs=2)
    assert [c.case_id for c in cases] == [f"08-fixture-bt/{s}/run{n}" for s in screen_mod.BACKTEST_SCREENS
                                          for n in (1, 2)]
    assert {c.kind for c in cases} == {"CONTEXT", "FRAME"}
    assert all(c.meta == {"source": "backtest"} and screen_mod.is_extra(c) for c in cases)
    problem = next(c for c in cases if c.screen == "PROBLEM_INTERPRET")
    assert problem.payload["input"]["content"] == str(fx.raw_entry()["statements"]["problem"])
    only = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                  needle="08-fixture-bt/PROBLEM_INTERPRET", n_runs=3)
    assert [c.case_id for c in only] == [f"08-fixture-bt/PROBLEM_INTERPRET/run{n}" for n in (1, 2, 3)]


def test_the_needle_names_the_probe_and_builds_its_two_frame_screens(tmp_path):
    root = _checkout(tmp_path)
    extras = screen_mod.load(root, "169-banking-gaming")
    assert extras.backtest == [] and [p.id for p in extras.probes] == ["169-banking-gaming"]
    cases = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                   needle="169-banking-gaming", n_runs=1)
    assert [c.case_id for c in cases] == ["169-banking-gaming/PROBLEM_INTERPRET/run1",
                                          "169-banking-gaming/SOLUTION_MECHANISM/run1"]
    problem, solution = cases
    assert problem.kind == solution.kind == "FRAME"
    assert "loot box" in problem.payload["input"]["content"]
    assert "respawns" in solution.payload["input"]["content"]
    assert solution.payload["context"]["problem_statement"] == PROBE["interpretations"]["problem"]
    assert problem.meta["source"] == "probe" and problem.meta["probe"]["planted"] == "loot box"
    assert screen_mod.plant_of(solution).planted == "respawns"


def test_all_cases_puts_the_extras_after_the_golden_cases_and_only_where_named(tmp_path):
    root = _checkout(tmp_path)
    golden = corpus_mod.Corpus(entries=[fx.entry()], directory=fx.ENTRY.parent)
    exported, instructions = fx.exported(tmp_path), fx.instructions()

    def cases(needle):
        extras = screen_mod.load(root, needle, golden_ids=[e.id for e in golden.entries])
        return run_mod._all_cases(golden, exported, instructions, fx.FakeRuntime, _args(needle), extras=extras)

    probe = cases("169-banking-gaming")
    assert [c.case_id for c in probe] == ["169-banking-gaming/PROBLEM_INTERPRET/run1",
                                          "169-banking-gaming/SOLUTION_MECHANISM/run1"]
    assert run_mod._golden(probe) == []
    golden_only = cases("09-fixture")
    assert golden_only and not any(screen_mod.is_extra(c) for c in golden_only)
    assert [c for c in cases("frame") if screen_mod.is_extra(c)] == []
    assert len(cases("PROBLEM_INTERPRET")) == 1, "a screen word names no extra entry: the golden case alone"


def test_an_extra_id_that_is_a_golden_one_refuses_by_name(tmp_path):
    root = _checkout(tmp_path, probe={**PROBE, "id": "09-fixture"})
    with pytest.raises(corpus_mod.CorpusError, match="09-fixture is both"):
        screen_mod.load(root, "09-fixture", golden_ids=["09-fixture"])


def test_a_probe_whose_planted_term_is_not_in_its_seed_refuses(tmp_path):
    probe = json.loads(json.dumps(PROBE))
    probe["probes"][0]["planted"] = "battle pass"
    root = _checkout(tmp_path, probe=probe)
    with pytest.raises(corpus_mod.CorpusError, match="'battle pass' is not in statements.problem"):
        screen_mod.load(root, "169-banking-gaming")


def test_a_probe_on_a_screen_that_is_not_a_frame_screen_refuses(tmp_path):
    probe = json.loads(json.dumps(PROBE))
    probe["probes"][0]["screen"] = "CALIBRATION_QUESTIONS"
    root = _checkout(tmp_path, probe=probe)
    with pytest.raises(corpus_mod.CorpusError, match="probes a screen 'CALIBRATION_QUESTIONS'"):
        screen_mod.load(root, "169-banking-gaming")


def test_the_screen_records_name_the_probe_apart_from_the_entries(tmp_path):
    root = _checkout(tmp_path)
    record = screen_mod.load(root, "-").record()                    # "-" names both 08-fixture-bt and the probe
    assert [e["id"] for e in record["backtest"]] == ["08-fixture-bt"]
    assert [p["id"] for p in record["probes"]] == ["169-banking-gaming"]
    assert [x["planted"] for x in record["probes"][0]["plants"]] == ["loot box", "respawns"]


def test_an_extra_file_changed_in_flight_fails_the_run(tmp_path):
    root = _checkout(tmp_path)
    extras = screen_mod.load(root, "169-banking-gaming")
    extras.verify_unchanged()
    path = screen_mod.probes_dir(root) / "169-banking-gaming.yaml"
    path.write_text(path.read_text() + "# edited\n")
    with pytest.raises(corpus_mod.CorpusError, match="changed while the run was in flight"):
        extras.verify_unchanged()


def test_keel_clouds_backtest_entries_and_probe_are_named_by_the_coordinators_needles():
    from stack.config import load_config                                    # noqa: PLC0415
    keel_cloud = load_config(validate=False).keel_cloud
    if not (screen_mod.probes_dir(keel_cloud) / "169-banking-gaming.yaml").is_file():
        pytest.skip("keel-cloud predates spec 169 (no probes/169-banking-gaming.yaml)")
    for needle, entry_id in (("08-fresco/PROBLEM_INTERPRET", "08-fresco"),
                             ("10-palus/SOLUTION_MECHANISM", "10-palus"),
                             ("13-aircaps/PROBLEM_INTERPRET", "13-aircaps")):
        extras = screen_mod.load(keel_cloud, needle)
        assert [e.id for e in extras.backtest] == [entry_id] and extras.probes == [], needle
    extras = screen_mod.load(keel_cloud, "169-banking-gaming")
    assert extras.backtest == [] and [p.id for p in extras.probes] == ["169-banking-gaming"]
    plants = {p.screen: p.planted for p in extras.probes[0].plants}
    assert plants == {"PROBLEM_INTERPRET": "loot box", "SOLUTION_MECHANISM": "respawns"}


# ---------------------------------------------------------------------------------------------- the probe mark

LOOT = screen_mod.Plant(**PROBE["probes"][0])
RESPAWN = screen_mod.Plant(**PROBE["probes"][1])


def _ask(text):
    return [{"id": "q1", "question": text, "input_type": "text", "required": True}]


@pytest.mark.parametrize("term, text, named", [
    ("loot box", "Did you mean a loot box as in games, or a bundle of fees?", True),
    ("loot box", "By loot boxes, do you mean ...", True),
    ("loot box", "Did you mean a loot-box?", True),
    ("loot box", "Did you mean a box of loot?", False),
    ("respawns", "When you say the app respawns the card...", True),
    ("respawns", "Did you mean respawn as in a game, or issue a new card?", True),
    ("respawns", "Did you mean the card is reissued?", False),
])
def test_the_term_is_named_as_typed_or_inflected(term, text, named):
    assert bool(screen_mod.term_pattern(term).search(text)) is named


def test_one_question_naming_the_term_with_two_readings_holds():
    mark = screen_mod.probe_mark("169-banking-gaming", LOOT, outcome="NEEDS_INPUT",
                                 questions=_ask("Did you mean a loot box as in a video game, or a bundle of fees "
                                                "charged together?"), result=None)
    assert mark["held"] and mark["faults"] == []
    assert mark["probe"] == "169-banking-gaming" and mark["planted"] == "loot box"
    assert "loot box" in mark["question"]


@pytest.mark.parametrize("questions, fault", [
    (_ask("What fees follow the block?"), "does not name the planted term 'loot box'"),
    (_ask("What do you mean by a loot box?"), "offers no two readings"),
    (_ask("Did you mean a loot box, or fees?") + _ask("And who pays?"), "2 questions, not 1"),
])
def test_a_needs_input_that_misses_the_term_the_readings_or_the_count_is_a_fault(questions, fault):
    mark = screen_mod.probe_mark("169-banking-gaming", LOOT, outcome="NEEDS_INPUT", questions=questions,
                                 result=None)
    assert not mark["held"] and any(fault in f for f in mark["faults"]), mark["faults"]


def test_a_card_that_keeps_the_term_is_a_fault():
    card = {"actor": "the app", "trigger": "a block", "mechanism": "respawns the card in the phone wallet",
            "output": "they can pay"}
    mark = screen_mod.probe_mark("169-banking-gaming", RESPAWN, outcome="COMPLETED", questions=None, result=card)
    assert not mark["held"]
    assert mark["faults"] == ["the first turn is a COMPLETED card that keeps the planted term 'respawns' without "
                              "asking"]


def test_a_statement_that_rewrites_the_term_silently_is_a_fault():
    mark = screen_mod.probe_mark("169-banking-gaming", LOOT, outcome="COMPLETED", questions=None,
                                 result={"statement": "Customers leave over the fees that follow."})
    assert mark["faults"] == ["the first turn is a COMPLETED statement that rewrites the planted term 'loot box' "
                              "without asking"]


def test_the_run_scores_a_probe_case_off_its_first_turn_and_keeps_it_apart(tmp_path):
    root = _checkout(tmp_path)
    extras = screen_mod.load(root, "169-banking-gaming")
    case = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                  needle="169-banking-gaming/PROBLEM", n_runs=1)[0]
    state = run_mod._RunState()
    asked = types.SimpleNamespace(outcome="NEEDS_INPUT", result=None, schema_valid=True, schema_error=None,
                                  error=None, questions=_ask("Did you mean a loot box from games, or a bundle "
                                                             "of fees?"))
    diff = run_mod._score(case, None, asked, None, state, judge=None)
    run_mod._score_probe(case, asked, diff, state)
    assert diff["source"] == "probe" and diff["probe"]["held"] and diff["failed"] is None
    assert "probe held" in diff["line"]
    assert [m["case_id"] for m in state.probes] == ["169-banking-gaming/PROBLEM_INTERPRET/run1"]
    completed = types.SimpleNamespace(outcome="COMPLETED", result={"statement": "the first loot box of fees"},
                                      schema_valid=True, schema_error=None, error=None, questions=None)
    diff = run_mod._score(case, None, completed, None, state, judge=None)
    run_mod._score_probe(case, completed, diff, state)
    assert diff["failed"].startswith("probe: the first turn is a COMPLETED statement that keeps")
    assert len(state.probes) == 2


def test_a_backtest_case_is_named_in_its_diff_and_carries_no_probe(tmp_path):
    root = _checkout(tmp_path)
    extras = screen_mod.load(root, "08-fixture-bt/SOLUTION")
    case = screen_mod.build_cases(extras, fx.exported(tmp_path), fx.instructions(), fx.FakeRuntime,
                                  needle="08-fixture-bt/SOLUTION", n_runs=1)[0]
    state = run_mod._RunState()
    answer = types.SimpleNamespace(outcome="COMPLETED", result={"actor": "x"}, schema_valid=True,
                                   schema_error=None, error=None, questions=None)
    diff = run_mod._score(case, None, answer, None, state, judge=None)
    assert run_mod._score_probe(case, answer, diff, state) is None
    assert diff["source"] == "backtest" and "probe" not in diff and state.probes == []


def test_a_dry_screen_of_the_probe_builds_its_two_cases_and_records_it_apart(tmp_path, monkeypatch, capsys):
    """`make instruction-screen DRY=1 K=169-banking-gaming` end to end on fixtures: before spec 105 it said *no case
    matches*; now it builds the probe's two frame cases, prints them, and the scorecard names the probe apart."""
    from tests.test_instruction_dry_run import _checkout as dry_checkout   # noqa: PLC0415
    checkout = dry_checkout(tmp_path)
    probes = screen_mod.probes_dir(checkout)
    probes.mkdir(parents=True)
    (probes / "169-banking-gaming.yaml").write_text(yaml.safe_dump(PROBE, sort_keys=False), encoding="utf-8")
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    monkeypatch.setattr(run_mod.report_mod, "start_bundle", lambda *a, **k: bundle)
    monkeypatch.setattr(run_mod.contract_mod, "export", lambda keel_cloud, into: fx.exported(tmp_path / "x"))
    monkeypatch.setattr(run_mod, "_instructions_for", lambda config: fx.instructions())
    corpus = corpus_mod.Corpus(entries=[corpus_mod.load_file(fx.ENTRY)], directory=fx.ENTRY.parent)
    args = types.SimpleNamespace(baseline=False, host="claude", filter="169-banking-gaming", n_runs=3,
                                 marks=None, models=None, no_judge=False)
    code = run_mod._dry_run(types.SimpleNamespace(keel_cloud=checkout), corpus, fx.FakeRuntime,
                            {"cli": "claude"}, args)
    out = capsys.readouterr().out
    assert code == 0, out
    assert "back-test entries none · probes 169-banking-gaming" in out
    assert "169-banking-gaming/PROBLEM_INTERPRET/run1" in out and "6 cases" in out
    scorecard = json.loads((bundle / "scorecard.json").read_text())
    assert scorecard["screen_entries"]["backtest"] == []
    assert [p["id"] for p in scorecard["screen_entries"]["probes"]] == ["169-banking-gaming"]
